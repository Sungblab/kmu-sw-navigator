from app.schemas.chat import ChatAction, ChatEvidence, ChatRequest, ChatResponse, ChoiceOption
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
    intent = detect_intent(request.message)
    personalization = [memory.natural_text for memory in memories]
    retrieval_results = retrieval_results or []
    evidence = ChatEvidence(
        personalization=personalization,
        internal_sources=[result.to_evidence() for result in retrieval_results],
    )
    actions: list[ChatAction] = []
    choices = _base_choices()
    needs_verification: list[str] = []

    if intent == "academic_advisor":
        if not evidence.internal_sources:
            evidence.notes.append("내부 자료에서 직접 일치하는 근거를 찾지 못했습니다.")
        answer = (
            "수강신청과 학업 질문은 먼저 적용 교과과정, 현재 학년, 관심 트랙을 "
            "확인해서 좁히는 것이 좋습니다. Mini LLM Wiki와 원문 chunk를 우선 검색해 "
            "근거가 있는 항목부터 보여줍니다."
        )
        actions.append(
            ChatAction(type="open_tab", label="학업 탭 열기", payload={"tab": "academic"})
        )
    elif intent == "career_advisor":
        answer = (
            "진로 상담은 관심 분야와 현재 경험을 기준으로 첫 포트폴리오 방향을 "
            "잡는 흐름이 좋습니다. 저장된 관심 메모리가 있으면 그 내용을 우선 "
            "근거로 사용합니다."
        )
        actions.append(
            ChatAction(type="open_tab", label="진로 탭 열기", payload={"tab": "career"})
        )
        # 최신성이 필요한 정보는 아직 grounding 전이므로 검증 필요 항목으로 분리한다.
        needs_verification.append(
            "최신 채용/공모전 정보는 Google grounding 연결 후 확인해야 합니다."
        )
    elif intent == "startup_project_mentor":
        answer = (
            "프로젝트나 창업 아이디어는 문제 정의, 사용자, 작은 출시 범위를 먼저 "
            "정하면 실행하기 쉽습니다. 지금은 아이디어를 기록하고 다음 질문으로 "
            "구체화하는 계약 단계입니다."
        )
        actions.append(
            ChatAction(type="open_tab", label="프로젝트 탭 열기", payload={"tab": "project"})
        )
    elif intent == "schedule_assistant":
        answer = (
            "일정 문장으로 보입니다. 다음 단계에서는 제목, 과목, 마감일을 추출해 "
            "저장 전 미리보기로 보여주면 됩니다."
        )
        choices = [
            ChoiceOption(
                id="create_schedule",
                label="일정 미리보기 만들기",
                message="방금 문장을 일정으로 추출해줘.",
            ),
            ChoiceOption(
                id="show_upcoming",
                label="다가오는 일정 보기",
                message="다가오는 과제와 시험을 보여줘.",
            ),
        ]
        actions.append(
            ChatAction(type="open_tab", label="일정 탭 열기", payload={"tab": "schedule"})
        )
    else:
        answer = (
            "먼저 학업, 진로, 프로젝트, 일정 중 어떤 방향의 도움이 필요한지 고르면 "
            "다음 질문을 더 정확히 이어갈 수 있습니다."
        )

    if answer_generator is not None:
        answer = answer_generator.generate_answer(
            request,
            intent=intent,
            memories=memories,
            retrieval_results=retrieval_results,
        )

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
        except Exception:
            evidence.notes.append("Google grounding 호출에 실패해 기본 답변을 사용했습니다.")

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        intent=intent,
        actions=actions,
        evidence=evidence,
        choices=choices,
        memory_updates=[],
        needs_verification=needs_verification,
    )


def detect_intent(message: str) -> str:
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


def _base_choices() -> list[ChoiceOption]:
    return [
        ChoiceOption(
            id="academic",
            label="학업 상담",
            message="수강신청과 전공 로드맵을 먼저 보고 싶어.",
        ),
        ChoiceOption(
            id="career",
            label="진로 상담",
            message="내 관심 분야에 맞는 진로 준비를 알려줘.",
        ),
        ChoiceOption(
            id="schedule",
            label="일정 관리",
            message="과제와 시험 일정을 정리하고 싶어.",
        ),
    ]
