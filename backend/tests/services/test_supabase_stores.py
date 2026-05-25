from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.schemas.assignment import AssignmentCreateRequest, AssignmentUpdateRequest
from app.schemas.google_oauth import GoogleOAuthTokenRecord
from app.schemas.llm_usage import LLMUsageLogCreateRequest
from app.schemas.profile import ProfileUpsertRequest
from app.services.memory_service import create_memory_candidate
from app.services.supabase_stores import (
    SupabaseAssignmentStore,
    SupabaseGoogleOAuthTokenStore,
    SupabaseLLMUsageLogStore,
    SupabaseMemoryStore,
    SupabaseProfileStore,
)


@dataclass
class FakeResult:
    data: Any


class FakeSupabaseClient:
    def __init__(self) -> None:
        self.tables: dict[str, list[dict[str, Any]]] = {
            "profiles": [],
            "user_memories": [],
            "memory_events": [],
            "assignments": [],
            "google_oauth_tokens": [],
            "llm_usage_logs": [],
        }

    def table(self, name: str) -> FakeTableQuery:
        return FakeTableQuery(self.tables, name)


class FakeTableQuery:
    def __init__(self, tables: dict[str, list[dict[str, Any]]], table_name: str) -> None:
        self.tables = tables
        self.table_name = table_name
        self.filters: list[tuple[str, Any]] = []
        self.payload: dict[str, Any] | None = None
        self.payloads: list[dict[str, Any]] | None = None
        self.mutation: str | None = None
        self.single_result = False
        self.order_column: str | None = None
        self.limit_count: int | None = None

    def select(self, _columns: str) -> FakeTableQuery:
        return self

    def eq(self, column: str, value: Any) -> FakeTableQuery:
        self.filters.append((column, value))
        return self

    def upsert(self, payload: dict[str, Any]) -> FakeTableQuery:
        self.payload = payload
        self.mutation = "upsert"
        return self

    def insert(self, payload: dict[str, Any]) -> FakeTableQuery:
        self.payload = payload
        self.mutation = "insert"
        return self

    def update(self, payload: dict[str, Any]) -> FakeTableQuery:
        self.payload = payload
        self.mutation = "update"
        return self

    def delete(self) -> FakeTableQuery:
        self.payload = {}
        self.mutation = "delete"
        return self

    def maybe_single(self) -> FakeTableQuery:
        self.single_result = True
        return self

    def order(self, column: str, desc: bool = False) -> FakeTableQuery:
        self.order_column = f"-{column}" if desc else column
        return self

    def limit(self, count: int) -> FakeTableQuery:
        self.limit_count = count
        return self

    def execute(self) -> FakeResult:
        rows = self.tables[self.table_name]
        if self.payload is not None:
            return self._execute_mutation(rows)

        result = [row for row in rows if self._matches(row)]
        if self.order_column:
            reverse = self.order_column.startswith("-")
            column = self.order_column.removeprefix("-")
            result = sorted(result, key=lambda row: row.get(column, ""), reverse=reverse)
        if self.single_result:
            return FakeResult(result[0] if result else None)
        if self.limit_count is not None:
            result = result[: self.limit_count]
        return FakeResult(result)

    def _execute_mutation(self, rows: list[dict[str, Any]]) -> FakeResult:
        assert self.payload is not None
        if isinstance(self.payload, list):
            inserted = []
            for item in self.payload:
                row = dict(item)
                row.setdefault("id", str(uuid4()))
                rows.append(row)
                inserted.append(dict(row))
            return FakeResult(inserted)

        if self.mutation == "update":
            updated = []
            for row in rows:
                if self._matches(row):
                    row.update(self.payload)
                    updated.append(dict(row))
            return FakeResult(updated)

        if self.mutation == "delete":
            deleted = []
            remaining = []
            for row in rows:
                if self._matches(row):
                    deleted.append(dict(row))
                else:
                    remaining.append(row)
            rows[:] = remaining
            return FakeResult(deleted)

        if self.table_name == "memory_events":
            row = dict(self.payload)
            row.setdefault("id", str(uuid4()))
            rows.append(row)
            return FakeResult([dict(row)])

        key = "id"
        existing = next((row for row in rows if row.get(key) == self.payload.get(key)), None)
        if existing:
            existing.update(self.payload)
            return FakeResult([dict(existing)])

        row = dict(self.payload)
        row.setdefault("id", str(uuid4()))
        rows.append(row)
        return FakeResult([row])

    def _matches(self, row: dict[str, Any]) -> bool:
        return all(row.get(column) == value for column, value in self.filters)


def test_supabase_profile_store_gets_missing_and_upserts_profile() -> None:
    client = FakeSupabaseClient()
    store = SupabaseProfileStore(client)

    assert store.get_profile("user-1") is None

    profile = store.upsert_profile(
        "user-1",
        ProfileUpsertRequest(department="software", grade=1, curriculum_year="2025"),
    )

    assert profile.id == "user-1"
    assert client.tables["profiles"][0]["department"] == "software"
    assert store.get_profile("user-1") == profile


def test_supabase_profile_store_treats_none_result_as_missing_profile() -> None:
    class NoneResultQuery:
        def select(self, _columns: str) -> NoneResultQuery:
            return self

        def eq(self, _column: str, _value: str) -> NoneResultQuery:
            return self

        def maybe_single(self) -> NoneResultQuery:
            return self

        def execute(self) -> None:
            return None

    class NoneResultClient:
        def table(self, _name: str) -> NoneResultQuery:
            return NoneResultQuery()

    store = SupabaseProfileStore(NoneResultClient())

    assert store.get_profile("user-1") is None


def test_supabase_memory_store_persists_memory_and_event_payloads() -> None:
    client = FakeSupabaseClient()
    store = SupabaseMemoryStore(client)

    memory = create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="AI랑 백엔드 관심 있어",
        category="interest",
        key="topic",
        value_json={"topics": ["AI", "백엔드"]},
    )

    assert memory.status == "active"
    assert client.tables["user_memories"][0]["user_id"] == "user-1"
    assert client.tables["memory_events"][0]["event_type"] == "created"
    assert store.list_active_memories("user-1") == [memory]


def test_supabase_memory_store_updates_and_archives_by_user_scope() -> None:
    client = FakeSupabaseClient()
    store = SupabaseMemoryStore(client)
    memory = create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="AI랑 백엔드 관심 있어",
        category="interest",
        key="topic",
        value_json={"topics": ["AI"]},
    )

    updated = memory.model_copy(update={"status": "archived"})
    store.save_memory("user-1", updated)

    assert store.get_memory("user-1", memory.id).status == "archived"
    assert store.list_active_memories("user-1") == []


def test_supabase_llm_usage_log_store_persists_and_lists_by_user_scope() -> None:
    client = FakeSupabaseClient()
    store = SupabaseLLMUsageLogStore(client)

    first = store.create_log(
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

    logs = store.list_logs("user-1")

    assert logs == [first]
    assert client.tables["llm_usage_logs"][0]["user_id"] == "user-1"


def test_supabase_assignment_store_persists_updates_and_deletes_by_user_scope() -> None:
    client = FakeSupabaseClient()
    store = SupabaseAssignmentStore(client)

    assignment = store.create_assignment(
        "user-1",
        AssignmentCreateRequest(
            title="자료구조 과제",
            course="자료구조",
            due_at=datetime(2026, 5, 22, 23, 59),
        ),
    )
    other_user_assignment = store.create_assignment(
        "user-2",
        AssignmentCreateRequest(
            title="다른 사용자 일정",
            due_at=datetime(2026, 5, 20, 23, 59),
        ),
    )

    updated = store.update_assignment(
        "user-1",
        assignment.id,
        AssignmentUpdateRequest(status="done"),
    )
    store.delete_assignment("user-2", other_user_assignment.id)

    assert updated.status == "done"
    assert store.list_assignments("user-1") == []
    assert client.tables["assignments"] == [
        {
            "user_id": "user-1",
            "title": "자료구조 과제",
            "course": "자료구조",
            "due_at": datetime(2026, 5, 22, 23, 59),
            "memo": None,
            "id": assignment.id,
            "status": "done",
        }
    ]


def test_supabase_assignment_store_marks_calendar_exported() -> None:
    client = FakeSupabaseClient()
    store = SupabaseAssignmentStore(client)
    assignment = store.create_assignment(
        "user-1",
        AssignmentCreateRequest(
            title="기말 프로젝트",
            due_at=datetime(2026, 6, 10, 23, 59),
        ),
    )

    exported = store.mark_calendar_exported(
        "user-1",
        assignment.id,
        calendar_event_id="kmu-event-1",
        synced_at=datetime(2026, 5, 14, 12, 0),
    )

    assert exported.calendar_event_id == "kmu-event-1"
    assert exported.calendar_synced_at == datetime(2026, 5, 14, 12, 0)


def test_supabase_google_oauth_token_store_upserts_and_gets_token() -> None:
    client = FakeSupabaseClient()
    store = SupabaseGoogleOAuthTokenStore(client)

    saved = store.save_token(
        "user-1",
        GoogleOAuthTokenRecord(
            user_id="user-1",
            access_token="protected-access",
            refresh_token="protected-refresh",
            scope="https://www.googleapis.com/auth/calendar.events",
            expires_at=datetime(2026, 5, 14, 13, 0),
        ),
    )

    assert saved.access_token == "protected-access"
    assert store.get_token("user-1") == saved
    assert client.tables["google_oauth_tokens"][0]["encrypted_access_token"] == "protected-access"
