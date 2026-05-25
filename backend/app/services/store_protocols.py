from datetime import datetime
from typing import Protocol

from app.schemas.assignment import (
    AssignmentCreateRequest,
    AssignmentResponse,
    AssignmentUpdateRequest,
)
from app.schemas.chat import ChatMessageRecord, ChatRequest, ChatResponse, ChatSessionSummary
from app.schemas.llm_usage import LLMUsageLogCreateRequest, LLMUsageLogResponse
from app.schemas.memory import MemoryEventResponse, MemoryResponse
from app.schemas.profile import ProfileResponse, ProfileUpsertRequest


class ProfileStore(Protocol):
    def get_profile(self, user_id: str) -> ProfileResponse | None: ...

    def upsert_profile(self, user_id: str, request: ProfileUpsertRequest) -> ProfileResponse: ...


class MemoryStore(Protocol):
    def save_memory(self, user_id: str, memory: MemoryResponse) -> MemoryResponse: ...

    def get_memory(self, user_id: str, memory_id: str) -> MemoryResponse: ...

    def add_event(self, user_id: str, event: MemoryEventResponse) -> MemoryEventResponse: ...

    def list_active_memories(self, user_id: str) -> list[MemoryResponse]: ...

    def list_events(self, user_id: str) -> list[MemoryEventResponse]: ...


class ChatStore(Protocol):
    def save_exchange(
        self,
        user_id: str,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse: ...

    def list_sessions(self, user_id: str, *, limit: int = 20) -> list[ChatSessionSummary]: ...

    def list_messages(self, user_id: str, session_id: str) -> list[ChatMessageRecord]: ...

    def delete_session(self, user_id: str, session_id: str) -> None: ...


class AssignmentStore(Protocol):
    def create_assignment(
        self,
        user_id: str,
        request: AssignmentCreateRequest,
    ) -> AssignmentResponse: ...

    def list_assignments(self, user_id: str) -> list[AssignmentResponse]: ...

    def update_assignment(
        self,
        user_id: str,
        assignment_id: str,
        request: AssignmentUpdateRequest,
    ) -> AssignmentResponse: ...

    def get_assignment(self, user_id: str, assignment_id: str) -> AssignmentResponse: ...

    def mark_calendar_exported(
        self,
        user_id: str,
        assignment_id: str,
        *,
        calendar_event_id: str,
        synced_at: datetime,
    ) -> AssignmentResponse: ...

    def delete_assignment(self, user_id: str, assignment_id: str) -> None: ...


class LLMUsageLogStore(Protocol):
    def create_log(
        self,
        user_id: str,
        request: LLMUsageLogCreateRequest,
    ) -> LLMUsageLogResponse: ...

    def list_logs(self, user_id: str, *, limit: int = 50) -> list[LLMUsageLogResponse]: ...
