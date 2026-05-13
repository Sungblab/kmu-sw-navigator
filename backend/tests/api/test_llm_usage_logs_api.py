from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user_id, get_llm_usage_log_store
from app.main import app
from app.schemas.llm_usage import LLMUsageLogCreateRequest
from app.services.llm_usage_log_service import InMemoryLLMUsageLogStore


def test_llm_usage_logs_endpoint_returns_current_user_logs() -> None:
    store = InMemoryLLMUsageLogStore()
    store.create_log(
        "user-1",
        LLMUsageLogCreateRequest(
            feature="rag_chat",
            input_text="AI 트랙 알려줘",
            output_text="답변",
            model="gemini-test",
            purpose="RAG 답변 생성",
        ),
    )
    store.create_log(
        "user-2",
        LLMUsageLogCreateRequest(
            feature="schedule_parser",
            input_text="다른 사용자 입력",
            purpose="다른 사용자 로그",
        ),
    )
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_llm_usage_log_store] = lambda: store
    client = TestClient(app)

    response = client.get("/api/llm-logs")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()["logs"]) == 1
    assert response.json()["logs"][0]["feature"] == "rag_chat"
    assert response.json()["logs"][0]["input_text"] == "AI 트랙 알려줘"


def test_chat_with_answer_generator_records_llm_usage_log() -> None:
    class FakeAnswerGenerator:
        model = "gemini-test"

        def generate_answer(self, request, *, intent, memories, retrieval_results):
            return "Gemini 답변"

    from app.api.dependencies import (
        get_answer_generator,
        get_chat_store,
        get_document_retriever,
        get_grounding_answer_generator,
        get_memory_store,
    )
    from app.services.chat_store import InMemoryChatStore
    from app.services.memory_service import InMemoryMemoryStore
    from app.services.retrieval_service import LocalDocumentRetriever

    log_store = InMemoryLLMUsageLogStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: InMemoryMemoryStore()
    app.dependency_overrides[get_chat_store] = lambda: InMemoryChatStore()
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: FakeAnswerGenerator()
    app.dependency_overrides[get_grounding_answer_generator] = lambda: None
    app.dependency_overrides[get_llm_usage_log_store] = lambda: log_store
    client = TestClient(app)

    response = client.post("/api/chat", json={"message": "AI 트랙 알려줘"})
    logs_response = client.get("/api/llm-logs")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert logs_response.json()["logs"][0]["feature"] == "rag_chat"
    assert logs_response.json()["logs"][0]["input_text"] == "AI 트랙 알려줘"
    assert logs_response.json()["logs"][0]["output_text"] == "Gemini 답변"
    assert logs_response.json()["logs"][0]["model"] == "gemini-test"


def test_chat_with_grounding_generator_records_llm_usage_log() -> None:
    class FakeGroundingAnswerGenerator:
        model = "gemini-grounding-test"

        def generate_grounded_answer(self, request, *, intent, memories, retrieval_results):
            from app.services.answer_generation_service import GroundedAnswer

            return GroundedAnswer(
                text="Grounded 답변",
                web_sources=[{"title": "웹 근거", "uri": "https://example.com"}],
            )

    from app.api.dependencies import (
        get_answer_generator,
        get_chat_store,
        get_document_retriever,
        get_grounding_answer_generator,
        get_memory_store,
    )
    from app.services.chat_store import InMemoryChatStore
    from app.services.memory_service import InMemoryMemoryStore
    from app.services.retrieval_service import LocalDocumentRetriever

    log_store = InMemoryLLMUsageLogStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: InMemoryMemoryStore()
    app.dependency_overrides[get_chat_store] = lambda: InMemoryChatStore()
    app.dependency_overrides[get_document_retriever] = lambda: LocalDocumentRetriever([])
    app.dependency_overrides[get_answer_generator] = lambda: None
    app.dependency_overrides[get_grounding_answer_generator] = (
        lambda: FakeGroundingAnswerGenerator()
    )
    app.dependency_overrides[get_llm_usage_log_store] = lambda: log_store
    client = TestClient(app)

    response = client.post("/api/chat", json={"message": "취업 준비는 어떻게 해?"})
    logs_response = client.get("/api/llm-logs")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert logs_response.json()["logs"][0]["feature"] == "google_grounding"
    assert logs_response.json()["logs"][0]["output_text"] == "Grounded 답변"
    assert logs_response.json()["logs"][0]["model"] == "gemini-grounding-test"


def test_assignment_preview_with_parser_records_llm_usage_log() -> None:
    from datetime import date, datetime

    from app.api.dependencies import get_assignment_parser
    from app.services.assignment_service import ParsedAssignment

    class FakeAssignmentParser:
        model = "gemini-schedule-test"

        def parse_assignment(self, text: str, *, reference_date: date) -> ParsedAssignment:
            return ParsedAssignment(
                title="AI 보고서",
                course="인공지능",
                due_at=datetime(2026, 5, 15, 18, 0),
                confidence=0.91,
            )

    log_store = InMemoryLLMUsageLogStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_assignment_parser] = lambda: FakeAssignmentParser()
    app.dependency_overrides[get_llm_usage_log_store] = lambda: log_store
    client = TestClient(app)

    response = client.post(
        "/api/assignments/preview",
        json={"text": "AI 보고서 내일 18시까지", "reference_date": "2026-05-14"},
    )
    logs_response = client.get("/api/llm-logs")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert logs_response.json()["logs"][0]["feature"] == "schedule_parser"
    assert logs_response.json()["logs"][0]["input_text"] == "AI 보고서 내일 18시까지"
    assert logs_response.json()["logs"][0]["model"] == "gemini-schedule-test"
