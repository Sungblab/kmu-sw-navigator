from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

from google import genai
from google.genai import types

from app.schemas.chat import ChatRequest
from app.schemas.memory import MemoryResponse
from app.services.retrieval_service import RetrievalResult

CHAT_MAX_OUTPUT_TOKENS = 4096


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

    def stream_answer(
        self,
        request: ChatRequest,
        *,
        intent: str,
        memories: list[MemoryResponse],
        retrieval_results: list[RetrievalResult],
    ) -> Iterator[str | StreamedAnswerChunk]:
        ...


@dataclass(frozen=True)
class GroundedAnswer:
    text: str
    web_sources: list[dict[str, str]]


@dataclass(frozen=True)
class StreamedAnswerChunk:
    text: str
    response: object | None = None


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
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                max_output_tokens=CHAT_MAX_OUTPUT_TOKENS,
            ),
        )
        answer = (response.text or "").strip()
        if not answer:
            raise RuntimeError("Gemini returned an empty answer")
        if _looks_incomplete_answer(answer, response):
            retry_response = self.client.models.generate_content(
                model=self.model,
                contents=_build_retry_prompt(prompt, answer),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    max_output_tokens=CHAT_MAX_OUTPUT_TOKENS,
                ),
            )
            retry_answer = (retry_response.text or "").strip()
            if retry_answer and not _looks_incomplete_answer(retry_answer, retry_response):
                return retry_answer
        return _repair_markdown(answer)

    def stream_answer(
        self,
        request: ChatRequest,
        *,
        intent: str,
        memories: list[MemoryResponse],
        retrieval_results: list[RetrievalResult],
    ) -> Iterator[str]:
        prompt = build_answer_prompt(
            request,
            intent=intent,
            memories=memories,
            retrieval_results=retrieval_results,
        )
        stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                max_output_tokens=CHAT_MAX_OUTPUT_TOKENS,
            ),
        )
        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield StreamedAnswerChunk(text=text, response=chunk)
            elif _finish_reason(chunk):
                yield StreamedAnswerChunk(text="", response=chunk)


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
                max_output_tokens=CHAT_MAX_OUTPUT_TOKENS,
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
    attachment_lines = [
        _format_attachment(index, attachment)
        for index, attachment in enumerate(request.attachments, 1)
    ]
    if not attachment_lines:
        attachment_lines = ["- 첨부 파일 없음"]

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

사용자 첨부:
{chr(10).join(attachment_lines)}

작성 규칙:
- 내부 근거가 있으면 근거 제목을 자연스럽게 언급한다.
- 내부 근거가 없으면 확인이 필요하다고 말한다.
- 최신 취업/공모전 정보는 아직 웹 grounding 전이므로 확정적으로 말하지 않는다.
- 제목 한 줄만 쓰지 말고, 학생이 바로 실행할 수 있는 3-4개 항목을 포함한다.
- 각 항목은 완성된 문장으로 쓰고, 마크다운 굵게 표시는 반드시 닫는다.
- 전체 답변은 4문장 또는 4개 bullet 이내로 답한다.
"""


def _format_attachment(index: int, attachment: object) -> str:
    name = getattr(attachment, "name", "첨부 파일")
    mime_type = getattr(attachment, "mime_type", "application/octet-stream")
    text_content = (getattr(attachment, "text_content", None) or "").replace("\n", " ").strip()
    if len(text_content) > 1500:
        text_content = f"{text_content[:1500]}..."
    if text_content:
        return f"{index}. {name} ({mime_type}): {text_content}"
    return f"{index}. {name} ({mime_type}): 텍스트 추출 없음"


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


def _build_retry_prompt(original_prompt: str, incomplete_answer: str) -> str:
    return f"""{original_prompt}

이전 응답이 중간에 끊겼거나 마크다운이 닫히지 않아 사용자 화면에서 깨졌다.

이전 응답:
{incomplete_answer}

다시 작성:
- 제목만 쓰지 말고 구체적인 다음 행동 3개를 포함한다.
- 한국어 완성 문장으로 작성한다.
- 마크다운 강조 표시는 열었으면 반드시 닫는다.
- 답변만 출력한다.
"""


def _looks_incomplete_answer(answer: str, response: object | None = None) -> bool:
    return _has_unbalanced_markdown_strong(answer.strip()) or _was_cut_off(response)


def _has_unbalanced_markdown_strong(answer: str) -> bool:
    return answer.count("**") % 2 == 1


def _was_cut_off(response: object | None) -> bool:
    finish_reason = _finish_reason(response).casefold()
    return "max" in finish_reason or "length" in finish_reason


def _finish_reason(response: object | None) -> str:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return ""
    finish_reason = getattr(candidates[0], "finish_reason", "")
    if not finish_reason:
        finish_reason = getattr(candidates[0], "finishReason", "")
    return str(finish_reason or "")


def _repair_markdown(answer: str) -> str:
    if _has_unbalanced_markdown_strong(answer):
        return answer.replace("**", "")
    return answer


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
