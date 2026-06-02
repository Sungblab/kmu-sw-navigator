from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_answer_generator,
    get_chat_store,
    get_current_user_id,
    get_document_retriever,
    get_grounding_answer_generator,
    get_memory_store,
)
from app.main import app
from app.services.answer_generation_service import GroundedAnswer, StreamedAnswerChunk
from app.services.chat_store import InMemoryChatStore
from app.services.memory_service import InMemoryMemoryStore, create_memory_candidate
from app.services.retrieval_service import LocalDocumentRetriever


class FakeGroundingAnswerGenerator:
    def generate_grounded_answer(self, request, *, intent, memories, retrieval_results):
        return GroundedAnswer(
            text="웹 근거로 최신 진로 정보를 정리했습니다.",
            web_sources=[{"title": "채용 트렌드", "uri": "https://example.com/career"}],
        )


class FakeStreamingAnswerGenerator:
    model = "gemini-test-stream"

    def generate_answer(self, request, *, intent, memories, retrieval_results):
        return f"{intent}: fallback"

    def stream_answer(self, request, *, intent, memories, retrieval_results):
        yield f"{request.mode}/"
        yield f"{request.model_tier}/"
        yield request.attachments[0].name if request.attachments else "no-file"


class FakeCutoffCandidate:
    finish_reason = "MAX_TOKENS"


class FakeCutoffResponse:
    candidates = [FakeCutoffCandidate()]


class FakeCutoffStreamingAnswerGenerator:
    model = "gemini-test-stream"

    def generate_answer(self, request, *, intent, memories, retrieval_results):
        return "Python 문법 다음에는 선형대수 기초와 자료구조를 함께 확인하세요."

    def stream_answer(self, request, *, intent, memories, retrieval_results):
        yield StreamedAnswerChunk(
            text="Python 문법과 선형",
            response=FakeCutoffResponse(),
        )


def test_chat_returns_answer_actions_evidence_and_choices() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    client = TestClient(app)

    response = client.post("/api/chat", json={"message": "무엇부터 하면 좋아?"})

    app.dependency_overrides.clear()
    body = response.json()
    assert response.status_code == 200
    assert body["answer"]
    assert isinstance(body["actions"], list)
    assert body["session_id"] is not None
    assert isinstance(body["evidence"], dict)
    assert isinstance(body["choices"], list)


def test_academic_question_includes_internal_sources_evidence_key() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever(
        [
            {
                "source_type": "wiki_page",
                "title": "신입생 안내",
                "source": "Mini LLM Wiki",
                "category": "freshman",
                "heading_path": "신입생 안내 > 수강신청",
                "content": "수강신청 전에는 졸업 요건과 시간표 충돌 여부를 확인한다.",
                "metadata": {"slug": "freshman"},
            }
        ]
    )
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    client = TestClient(app)

    response = client.post("/api/chat", json={"message": "수강신청 전에 뭘 확인해야 해?"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["intent"] == "academic_advisor"
    assert response.json()["evidence"]["internal_sources"]
    assert response.json()["evidence"]["internal_sources"][0]["source_type"] == "wiki_page"


def test_career_question_includes_personalization_evidence_key() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="AI랑 백엔드 관심 있어",
        category="interest",
        key="topic",
        value_json={"topics": ["AI", "백엔드"]},
    )
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_grounding_answer_generator] = (
        lambda: FakeGroundingAnswerGenerator()
    )
    client = TestClient(app)

    response = client.post("/api/chat", json={"message": "취업 준비는 어떻게 시작할까?"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["intent"] == "career_advisor"
    assert response.json()["evidence"]["personalization"] == ["AI랑 백엔드 관심 있어"]
    assert response.json()["evidence"]["web_sources"][0]["title"] == "채용 트렌드"
    assert response.json()["needs_verification"] == []


def test_chat_saves_low_sensitivity_learning_context_from_conversation() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        json={
            "mode": "career",
            "message": (
                "AI랑 백엔드에 관심 있고 목표는 포트폴리오 준비야. "
                "코딩은 초급이고 프로젝트로 배우고 싶어. 주 4시간 가능해."
            ),
        },
    )

    app.dependency_overrides.clear()
    body = response.json()
    saved_memories = store.list_active_memories("user-1")
    assert response.status_code == 200
    assert body["memory_updates"]
    assert body["memory_updates"][0]["category"] == "conversation"
    assert body["memory_updates"][0]["key"] == "learning_context"
    assert body["memory_updates"][0]["value_json"] == {
        "track_interests": ["AI", "백엔드"],
        "activity_interests": ["개발"],
        "goal": "포트폴리오 준비",
        "coding_level": "beginner",
        "preference": "project",
        "activity_style": "unknown",
        "weekly_hours": 4,
    }
    assert saved_memories[0].natural_text.startswith("대화에서 파악한 학습/진로 정보")


def test_assignment_sentence_returns_schedule_intent_without_hardcoded_choices() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    client = TestClient(app)

    response = client.post("/api/chat", json={"message": "자료구조 과제 다음주 금요일까지야"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["intent"] == "schedule_assistant"
    assert response.json()["choices"] == []


def test_assignment_sentence_returns_calendar_add_action() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        json={"message": "자료구조 과제 다음주 금요일까지야"},
    )

    app.dependency_overrides.clear()
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "schedule_assistant"
    assert body["actions"][0]["type"] == "assignment_preview"
    assert body["actions"][0]["label"] == "캘린더에 추가"
    assert body["actions"][0]["payload"]["preview"]["title"] == "자료구조 과제"
    assert body["actions"][0]["payload"]["preview"]["course"] == "자료구조"
    assert body["actions"][0]["payload"]["source_text"] == "자료구조 과제 다음주 금요일까지야"


def test_chat_sessions_and_messages_endpoints_return_saved_exchange() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    client = TestClient(app)

    chat_response = client.post("/api/chat", json={"message": "AI 트랙은 뭐부터 봐?"})
    session_id = chat_response.json()["session_id"]
    sessions_response = client.get("/api/chat/sessions")
    messages_response = client.get(f"/api/chat/sessions/{session_id}/messages")

    app.dependency_overrides.clear()
    assert sessions_response.status_code == 200
    assert sessions_response.json()["sessions"][0]["id"] == session_id
    assert sessions_response.json()["sessions"][0]["last_message_preview"]
    assert messages_response.status_code == 200
    assert [message["role"] for message in messages_response.json()["messages"]] == [
        "user",
        "assistant",
    ]


def test_chat_stream_returns_sse_text_and_done_events() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    client = TestClient(app)

    with client.stream("POST", "/api/chat/stream", json={"message": "AI 트랙 알려줘"}) as response:
        body = response.read().decode("utf-8")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "event: status" in body
    assert "event: text" in body
    assert "event: done" in body
    assert chat_store.list_sessions("user-1")[0].id


def test_chat_stream_uses_request_options_and_streaming_generator() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: FakeStreamingAnswerGenerator()
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    client = TestClient(app)

    with client.stream(
        "POST",
        "/api/chat/stream",
        json={
            "message": "수강 전략 알려줘",
            "mode": "academic",
            "model_tier": "fast",
            "attachments": [
                {
                    "name": "courses.md",
                    "mime_type": "text/markdown",
                    "size": 12,
                    "text_content": "Python 이후 AI",
                }
            ],
        },
    ) as response:
        body = response.read().decode("utf-8")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "academic/" in body
    assert "fast/" in body
    assert "courses.md" in body
    assert "gemini-test-stream" in body


def test_chat_stream_retries_cutoff_answer_before_done_and_save() -> None:
    store = InMemoryMemoryStore()
    chat_store = InMemoryChatStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    app.dependency_overrides[get_chat_store] = lambda: chat_store
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: FakeCutoffStreamingAnswerGenerator()
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    client = TestClient(app)

    with client.stream("POST", "/api/chat/stream", json={"message": "AI 트랙 알려줘"}) as response:
        body = response.read().decode("utf-8")

    saved_messages = chat_store.list_messages("user-1", chat_store.list_sessions("user-1")[0].id)
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "Python 문법 다음에는 선형대수 기초와 자료구조를 함께 확인하세요." in body
    assert (
        saved_messages[1].content
        == "Python 문법 다음에는 선형대수 기초와 자료구조를 함께 확인하세요."
    )
