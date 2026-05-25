from app.schemas.chat import ChatEvidence, ChatRequest, ChatResponse
from app.schemas.memory import MemoryResponse
from app.services.answer_generation_service import AnswerGenerator, GroundingAnswerGenerator
from app.services.retrieval_service import RetrievalResult

ACADEMIC_KEYWORDS = ["수강", "교과", "학업", "과목", "커리큘럼", "트랙", "학점"]
CAREER_KEYWORDS = ["취업", "진로", "인턴", "포트폴리오", "직무", "회사"]
PROJECT_KEYWORDS = ["프로젝트", "창업", "공모전", "해커톤", "아이디어"]
SCHEDULE_KEYWORDS = ["과제", "마감", "시험", "일정", "제출", "다음주"]


def build_chat_response(
    request: ChatRequest,
    memories: list[MemoryResponse],
    retrieval_results: list[RetrievalResult] | None = None,
    answer_generator: AnswerGenerator | None = None,
    grounding_answer_generator: GroundingAnswerGenerator | None = None,
) -> ChatResponse:
    intent = detect_intent(request.message, mode=request.mode)
    personalization = [memory.natural_text for memory in memories]
    retrieval_results = retrieval_results or []
    evidence = ChatEvidence(
        personalization=personalization,
        internal_sources=[result.to_evidence() for result in retrieval_results],
    )
    actions = []
    choices = []
    needs_verification: list[str] = []
    model: str | None = None
    answer = (
        "Gemini 응답 생성기가 연결되지 않아 답변을 만들 수 없습니다. "
        "설정을 확인한 뒤 다시 시도해 주세요."
    )

    if intent == "academic_advisor":
        if not evidence.internal_sources:
            evidence.notes.append("내부 자료에서 직접 일치하는 근거를 찾지 못했습니다.")
    elif intent == "career_advisor":
        # 최신성이 필요한 정보는 아직 grounding 전이므로 검증 필요 항목으로 분리한다.
        needs_verification.append(
            "최신 채용/공모전 정보는 Google grounding 연결 후 확인해야 합니다."
        )

    if answer_generator is not None:
        answer = answer_generator.generate_answer(
            request,
            intent=intent,
            memories=memories,
            retrieval_results=retrieval_results,
        )
        model = getattr(answer_generator, "model", None)

    if grounding_answer_generator is not None and intent in {
        "career_advisor",
        "startup_project_mentor",
    }:
        try:
            grounded_answer = grounding_answer_generator.generate_grounded_answer(
                request,
                intent=intent,
                memories=memories,
                retrieval_results=retrieval_results,
            )
            answer = grounded_answer.text
            evidence.web_sources = grounded_answer.web_sources
            needs_verification = []
            model = getattr(grounding_answer_generator, "model", None)
        except Exception:
            evidence.notes.append("Google grounding 호출에 실패해 기본 답변을 사용했습니다.")

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        intent=intent,
        model=model,
        actions=actions,
        evidence=evidence,
        choices=choices,
        memory_updates=[],
        needs_verification=needs_verification,
    )


def detect_intent(message: str, *, mode: str = "auto") -> str:
    if mode == "academic":
        return "academic_advisor"
    if mode == "career":
        return "career_advisor"
    if mode == "schedule":
        return "schedule_assistant"
    normalized = message.casefold()
    # 일정 문장은 학업/진로 단어와 섞여도 저장 행동이 필요하므로 가장 먼저 분류한다.
    if _contains_any(normalized, SCHEDULE_KEYWORDS):
        return "schedule_assistant"
    if _contains_any(normalized, CAREER_KEYWORDS):
        return "career_advisor"
    if _contains_any(normalized, PROJECT_KEYWORDS):
        return "startup_project_mentor"
    if _contains_any(normalized, ACADEMIC_KEYWORDS):
        return "academic_advisor"
    return "general"


def _contains_any(message: str, keywords: list[str]) -> bool:
    return any(keyword in message for keyword in keywords)
