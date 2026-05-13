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
from app.services.answer_generation_service import GroundedAnswer
from app.services.chat_store import InMemoryChatStore
from app.services.memory_service import InMemoryMemoryStore, create_memory_candidate
from app.services.retrieval_service import LocalDocumentRetriever


class FakeGroundingAnswerGenerator:
    def generate_grounded_answer(self, request, *, intent, memories, retrieval_results):
        return GroundedAnswer(
            text="웹 근거로 최신 진로 정보를 정리했습니다.",
            web_sources=[{"title": "채용 트렌드", "uri": "https://example.com/career"}],
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


def test_assignment_sentence_returns_schedule_choice() -> None:
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
    assert any(choice["id"] == "create_schedule" for choice in response.json()["choices"])


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
    assert messages_response.status_code == 200
    assert [message["role"] for message in messages_response.json()["messages"]] == [
        "user",
        "assistant",
    ]
