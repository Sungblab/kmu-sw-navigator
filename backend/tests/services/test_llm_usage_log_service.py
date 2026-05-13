from __future__ import annotations

from app.schemas.llm_usage import LLMUsageLogCreateRequest
from app.services.llm_usage_log_service import InMemoryLLMUsageLogStore


def test_in_memory_llm_usage_log_store_records_and_lists_recent_entries() -> None:
    store = InMemoryLLMUsageLogStore()

    first = store.create_log(
        "user-1",
        LLMUsageLogCreateRequest(
            feature="rag_chat",
            input_text="AI 트랙 알려줘",
            output_text="AI 트랙 답변",
            model="gemini-test",
            purpose="RAG 답변 생성",
        ),
    )
    second = store.create_log(
        "user-1",
        LLMUsageLogCreateRequest(
            feature="schedule_parser",
            input_text="자료구조 과제 내일까지",
            output_text='{"title":"자료구조 과제"}',
            model="gemini-lite",
            purpose="일정 JSON 추출",
        ),
    )
    store.create_log(
        "user-2",
        LLMUsageLogCreateRequest(
            feature="rag_chat",
            input_text="다른 사용자 질문",
            purpose="다른 사용자 로그",
        ),
    )

    logs = store.list_logs("user-1")

    assert [log.id for log in logs] == [second.id, first.id]
    assert logs[0].feature == "schedule_parser"
    assert logs[0].model == "gemini-lite"
    assert all(log.user_id == "user-1" for log in logs)
