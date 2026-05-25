from app.schemas.chat import ChatEvidence, ChatRequest, ChatResponse
from app.services.chat_store import InMemoryChatStore
from app.services.supabase_stores import SupabaseChatStore
from tests.services.test_supabase_stores import FakeSupabaseClient


def test_in_memory_chat_store_creates_session_and_message_pair() -> None:
    store = InMemoryChatStore()
    response = ChatResponse(
        answer="수강신청 전에 졸업 요건을 확인하세요.",
        intent="academic_advisor",
        evidence=ChatEvidence(internal_sources=[{"title": "신입생 안내"}]),
    )

    saved = store.save_exchange(
        user_id="user-1",
        request=ChatRequest(message="수강신청 전에 뭐 봐?"),
        response=response,
    )

    assert saved.session_id is not None
    assert store.sessions[saved.session_id]["title"] == "수강·로드맵 상담"
    assert [message["role"] for message in store.messages] == ["user", "assistant"]
    assert store.messages[1]["evidence"]["internal_sources"][0]["title"] == "신입생 안내"
    summary = store.list_sessions("user-1")[0]
    assert summary.id == saved.session_id
    assert summary.last_message_preview == "수강신청 전에 졸업 요건을 확인하세요."
    assert summary.updated_at is not None
    assert [message.role for message in store.list_messages("user-1", saved.session_id)] == [
        "user",
        "assistant",
    ]


def test_supabase_chat_store_creates_session_and_inserts_messages() -> None:
    client = FakeSupabaseClient()
    client.tables["chat_sessions"] = []
    client.tables["chat_messages"] = []
    store = SupabaseChatStore(client)

    saved = store.save_exchange(
        user_id="user-1",
        request=ChatRequest(message="AI 트랙은 뭐부터 봐?"),
        response=ChatResponse(answer="Python부터 보세요.", intent="academic_advisor"),
    )

    assert saved.session_id is not None
    assert client.tables["chat_sessions"][0]["title"] == "수강·로드맵 상담"
    assert [message["role"] for message in client.tables["chat_messages"]] == [
        "user",
        "assistant",
    ]
    summary = store.list_sessions("user-1")[0]
    assert summary.id == saved.session_id
    assert summary.last_message_preview == "Python부터 보세요."
    assert [message.role for message in store.list_messages("user-1", saved.session_id)] == [
        "user",
        "assistant",
    ]


def test_chat_store_deletes_session_and_messages() -> None:
    store = InMemoryChatStore()
    saved = store.save_exchange(
        user_id="user-1",
        request=ChatRequest(message="수강신청 전에 뭐 봐?"),
        response=ChatResponse(answer="졸업요건부터 보세요.", intent="academic_advisor"),
    )

    assert saved.session_id is not None
    store.delete_session("user-1", saved.session_id)

    assert store.list_sessions("user-1") == []
    assert store.list_messages("user-1", saved.session_id) == []


def test_supabase_chat_store_reuses_existing_session() -> None:
    client = FakeSupabaseClient()
    client.tables["chat_sessions"] = [
        {"id": "session-1", "user_id": "user-1", "title": "기존", "intent": "general"}
    ]
    client.tables["chat_messages"] = []
    store = SupabaseChatStore(client)

    saved = store.save_exchange(
        user_id="user-1",
        request=ChatRequest(message="이어 질문", session_id="session-1"),
        response=ChatResponse(answer="이어 답변", intent="career_advisor"),
    )

    assert saved.session_id == "session-1"
    assert client.tables["chat_sessions"][0]["intent"] == "career_advisor"
    assert client.tables["chat_sessions"][0]["updated_at"] is not None
    assert len(client.tables["chat_messages"]) == 2
