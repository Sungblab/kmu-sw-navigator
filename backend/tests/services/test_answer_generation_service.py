from app.schemas.chat import ChatRequest
from app.schemas.memory import MemoryResponse
from app.services.answer_generation_service import GroundedAnswer, build_answer_prompt
from app.services.chat_contract_service import build_chat_response
from app.services.retrieval_service import RetrievalResult


class FakeAnswerGenerator:
    def __init__(self) -> None:
        self.calls = []

    def generate_answer(self, request, *, intent, memories, retrieval_results):
        self.calls.append(
            {
                "message": request.message,
                "intent": intent,
                "memories": memories,
                "retrieval_results": retrieval_results,
            }
        )
        return "Gemini 스타일 답변입니다."


class FakeGroundingAnswerGenerator:
    def __init__(self) -> None:
        self.calls = []

    def generate_grounded_answer(self, request, *, intent, memories, retrieval_results):
        self.calls.append({"message": request.message, "intent": intent})
        return GroundedAnswer(
            text="최신 채용 정보는 웹 근거 기준으로 정리했습니다.",
            web_sources=[
                {
                    "title": "AI 채용 공고",
                    "uri": "https://example.com/jobs",
                    "domain": "example.com",
                }
            ],
        )


def test_build_answer_prompt_includes_question_memories_and_evidence() -> None:
    memory = MemoryResponse(
        id="memory-1",
        category="interest",
        key="topic",
        value_json={"topics": ["AI"]},
        natural_text="AI에 관심 있음",
        confidence=0.8,
    )
    result = RetrievalResult(
        source_type="wiki_page",
        title="트랙 안내",
        source="Mini LLM Wiki",
        category="track",
        heading_path="트랙 안내",
        content="AI 트랙은 Python과 자료구조를 먼저 본다.",
        score=0.9,
        metadata={"slug": "track"},
    )

    prompt = build_answer_prompt(
        ChatRequest(message="AI 트랙은 뭐부터 준비해?"),
        intent="academic_advisor",
        memories=[memory],
        retrieval_results=[result],
    )

    assert "AI 트랙은 뭐부터 준비해?" in prompt
    assert "AI에 관심 있음" in prompt
    assert "AI 트랙은 Python과 자료구조" in prompt


def test_build_chat_response_uses_answer_generator_when_present() -> None:
    generator = FakeAnswerGenerator()

    response = build_chat_response(
        ChatRequest(message="수강신청 전에 뭘 봐?"),
        memories=[],
        retrieval_results=[],
        answer_generator=generator,
    )

    assert response.answer == "Gemini 스타일 답변입니다."
    assert generator.calls[0]["intent"] == "academic_advisor"


def test_build_chat_response_uses_grounding_for_career_questions() -> None:
    grounding = FakeGroundingAnswerGenerator()

    response = build_chat_response(
        ChatRequest(message="AI 백엔드 취업 트렌드 알려줘"),
        memories=[],
        retrieval_results=[],
        grounding_answer_generator=grounding,
    )

    assert response.intent == "career_advisor"
    assert response.answer == "최신 채용 정보는 웹 근거 기준으로 정리했습니다."
    assert response.evidence.web_sources[0]["title"] == "AI 채용 공고"
    assert response.needs_verification == []
    assert grounding.calls[0]["intent"] == "career_advisor"


def test_build_chat_response_does_not_ground_academic_questions() -> None:
    grounding = FakeGroundingAnswerGenerator()

    response = build_chat_response(
        ChatRequest(message="AI 트랙 과목 알려줘"),
        memories=[],
        retrieval_results=[],
        grounding_answer_generator=grounding,
    )

    assert response.intent == "academic_advisor"
    assert response.evidence.web_sources == []
    assert grounding.calls == []
