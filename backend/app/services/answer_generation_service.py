from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from google import genai
from google.genai import types

from app.schemas.chat import ChatRequest
from app.schemas.memory import MemoryResponse
from app.services.retrieval_service import RetrievalResult


class AnswerGenerator(Protocol):
    def generate_answer(
        self,
        request: ChatRequest,
        *,
        intent: str,
        memories: list[MemoryResponse],
        retrieval_results: list[RetrievalResult],
    ) -> str:
        ...


@dataclass(frozen=True)
class GroundedAnswer:
    text: str
    web_sources: list[dict[str, str]]


class GroundingAnswerGenerator(Protocol):
    def generate_grounded_answer(
        self,
        request: ChatRequest,
        *,
        intent: str,
        memories: list[MemoryResponse],
        retrieval_results: list[RetrievalResult],
    ) -> GroundedAnswer:
        ...


class GeminiAnswerGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_answer(
        self,
        request: ChatRequest,
        *,
        intent: str,
        memories: list[MemoryResponse],
        retrieval_results: list[RetrievalResult],
    ) -> str:
        prompt = build_answer_prompt(
            request,
            intent=intent,
            memories=memories,
            retrieval_results=retrieval_results,
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                systemInstruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                maxOutputTokens=512,
            ),
        )
        answer = (response.text or "").strip()
        if not answer:
            raise RuntimeError("Gemini returned an empty answer")
        return answer


class GeminiGroundingAnswerGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_grounded_answer(
        self,
        request: ChatRequest,
        *,
        intent: str,
        memories: list[MemoryResponse],
        retrieval_results: list[RetrievalResult],
    ) -> GroundedAnswer:
        prompt = build_grounding_prompt(
            request,
            intent=intent,
            memories=memories,
            retrieval_results=retrieval_results,
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=GROUNDING_SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=768,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        answer = (response.text or "").strip()
        if not answer:
            raise RuntimeError("Gemini grounding returned an empty answer")
        return GroundedAnswer(
            text=answer,
            web_sources=_web_sources_from_response(response),
        )


SYSTEM_INSTRUCTION = (
    "너는 국민대학교 소프트웨어융합대학 학생을 돕는 AI 내비게이터다. "
    "제공된 내부 근거와 사용자 메모리를 우선 사용하고, 근거가 부족하면 부족하다고 말한다. "
    "답변은 한국어로 짧고 실행 가능한 다음 행동 중심으로 작성한다."
)

GROUNDING_SYSTEM_INSTRUCTION = (
    "너는 국민대학교 소프트웨어융합대학 학생의 진로/취업/창업 질문을 돕는 AI다. "
    "최신성이 필요한 내용은 Google Search grounding 근거를 우선 사용하고, "
    "내부 자료와 충돌하면 최신 웹 정보와 학교 내부 맥락을 분리해 설명한다. "
    "답변은 한국어로 짧고 실행 가능한 다음 행동 중심으로 작성한다."
)


def build_answer_prompt(
    request: ChatRequest,
    *,
    intent: str,
    memories: list[MemoryResponse],
    retrieval_results: list[RetrievalResult],
) -> str:
    memory_lines = [
        f"- {memory.category}/{memory.key}: {memory.natural_text}" for memory in memories[:5]
    ] or ["- 저장된 개인화 메모리 없음"]
    evidence_lines = [
        _format_evidence(index, result)
        for index, result in enumerate(retrieval_results[:5], 1)
    ]
    if not evidence_lines:
        evidence_lines = ["- 내부 자료 근거 없음"]

    # prompt는 사용자 입력, 분류된 intent, 개인화 메모리, 검색 근거를 분리해
    # LLM이 출처 없는 추측보다 제공된 근거를 우선하도록 만든다.
    return f"""사용자 질문:
{request.message}

분류된 intent:
{intent}

개인화 메모리:
{chr(10).join(memory_lines)}

내부 검색 근거:
{chr(10).join(evidence_lines)}

작성 규칙:
- 내부 근거가 있으면 근거 제목을 자연스럽게 언급한다.
- 내부 근거가 없으면 확인이 필요하다고 말한다.
- 최신 취업/공모전 정보는 아직 웹 grounding 전이므로 확정적으로 말하지 않는다.
- 4문장 이내로 답한다.
"""


def build_grounding_prompt(
    request: ChatRequest,
    *,
    intent: str,
    memories: list[MemoryResponse],
    retrieval_results: list[RetrievalResult],
) -> str:
    base_prompt = build_answer_prompt(
        request,
        intent=intent,
        memories=memories,
        retrieval_results=retrieval_results,
    )
    return f"""{base_prompt}

추가 규칙:
- 채용, 인턴, 공모전, 창업 지원, 기술 트렌드처럼 최신성이 필요한 내용은 웹 검색 근거를 사용한다.
- 출처가 불확실하면 확정적으로 말하지 않는다.
- 학교 내부 자료 근거와 최신 웹 근거를 섞어 말할 때는 어떤 부분이 최신 웹 정보인지 구분한다.
"""


def _format_evidence(index: int, result: RetrievalResult) -> str:
    content = result.content.replace("\n", " ").strip()
    if len(content) > 500:
        content = f"{content[:500]}..."
    return (
        f"{index}. [{result.source_type}] {result.title}"
        f" / {result.heading_path or 'root'} / score={result.score}: {content}"
    )


def _web_sources_from_response(response: object) -> list[dict[str, str]]:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return []
    metadata = getattr(candidates[0], "grounding_metadata", None)
    chunks = getattr(metadata, "grounding_chunks", None) if metadata else None
    sources: list[dict[str, str]] = []
    seen: set[str] = set()
    for chunk in chunks or []:
        web = getattr(chunk, "web", None)
        uri = str(getattr(web, "uri", "") or "")
        if not web or not uri or uri in seen:
            continue
        seen.add(uri)
        sources.append(
            {
                "title": str(getattr(web, "title", "") or "웹 근거"),
                "uri": uri,
                "domain": str(getattr(web, "domain", "") or ""),
            }
        )
    return sources
