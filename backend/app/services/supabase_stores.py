from datetime import UTC, datetime
from typing import Any

from app.schemas.assignment import (
    AssignmentCreateRequest,
    AssignmentResponse,
    AssignmentUpdateRequest,
)
from app.schemas.chat import ChatMessageRecord, ChatRequest, ChatResponse, ChatSessionSummary
from app.schemas.google_oauth import GoogleOAuthTokenRecord
from app.schemas.llm_usage import LLMUsageLogCreateRequest, LLMUsageLogResponse
from app.schemas.memory import MemoryEventResponse, MemoryResponse
from app.schemas.profile import ProfileResponse, ProfileUpsertRequest
from app.services.assignment_service import build_assignment_response
from app.services.chat_store import _chat_message_evidence, _chat_session_title


class SupabaseProfileStore:
    def __init__(self, client: Any) -> None:
        self.client = client

    def get_profile(self, user_id: str) -> ProfileResponse | None:
        result = (
            self.client.table("profiles")
            .select("*")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        if result is None or not result.data:
            return None
        return _profile_from_row(result.data)

    def upsert_profile(
        self,
        user_id: str,
        request: ProfileUpsertRequest,
    ) -> ProfileResponse:
        # 프로필 owner는 요청 body가 아니라 인증된 user_id로만 정해 사용자 간 덮어쓰기를 막는다.
        payload = {"id": user_id, **request.model_dump()}
        result = self.client.table("profiles").upsert(payload).execute()
        return _profile_from_row(_single_row(result.data))


class SupabaseMemoryStore:
    def __init__(self, client: Any) -> None:
        self.client = client

    def save_memory(self, user_id: str, memory: MemoryResponse) -> MemoryResponse:
        # user_id는 서버에서 붙이고 response schema에는 노출하지 않는다.
        # 메모리 소유 범위가 request body가 아니라 API boundary에서 정해진다.
        payload = {"user_id": user_id, **memory.model_dump()}
        result = self.client.table("user_memories").upsert(payload).execute()
        return _memory_from_row(_single_row(result.data))

    def get_memory(self, user_id: str, memory_id: str) -> MemoryResponse:
        # 모든 조회는 user_id와 memory_id를 함께 걸어 다른 사용자의 메모리가 섞이지 않게 한다.
        result = (
            self.client.table("user_memories")
            .select("*")
            .eq("user_id", user_id)
            .eq("id", memory_id)
            .maybe_single()
            .execute()
        )
        if not result.data:
            raise KeyError(memory_id)
        return _memory_from_row(result.data)

    def add_event(self, user_id: str, event: MemoryEventResponse) -> MemoryEventResponse:
        payload = {"user_id": user_id, **event.model_dump()}
        result = self.client.table("memory_events").insert(payload).execute()
        return _memory_event_from_row(_single_row(result.data))

    def list_active_memories(self, user_id: str) -> list[MemoryResponse]:
        result = (
            self.client.table("user_memories")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "active")
            .execute()
        )
        return [_memory_from_row(row) for row in result.data]

    def list_events(self, user_id: str) -> list[MemoryEventResponse]:
        result = (
            self.client.table("memory_events")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return [_memory_event_from_row(row) for row in result.data]


class SupabaseChatStore:
    def __init__(self, client: Any) -> None:
        self.client = client

    def save_exchange(
        self,
        user_id: str,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse:
        session_id = request.session_id or response.session_id
        if session_id is None:
            session_id = self._create_session(user_id, request, response)
        else:
            self._touch_session(user_id, session_id, response)

        response_with_session = response.model_copy(update={"session_id": session_id})
        user_message_created_at = datetime.now(UTC).isoformat()
        assistant_message_created_at = datetime.now(UTC).isoformat()
        # user/assistant 메시지를 연속 insert해 대화 재구성 순서를 유지한다.
        self.client.table("chat_messages").insert(
            [
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "role": "user",
                    "content": request.message,
                    "evidence": {},
                    "memory_updates": [],
                    "created_at": user_message_created_at,
                },
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "role": "assistant",
                    "content": response.answer,
                    "evidence": _chat_message_evidence(response),
                    "memory_updates": [
                        memory.model_dump() for memory in response.memory_updates
                    ],
                    "created_at": assistant_message_created_at,
                },
            ]
        ).execute()
        return response_with_session

    def _create_session(
        self,
        user_id: str,
        request: ChatRequest,
        response: ChatResponse,
    ) -> str:
        now = datetime.now(UTC).isoformat()
        result = (
            self.client.table("chat_sessions")
            .insert(
                {
                    "user_id": user_id,
                    "title": _chat_session_title(request.message, response.intent),
                    "intent": response.intent,
                    "updated_at": now,
                }
            )
            .execute()
        )
        return str(_single_row(result.data)["id"])

    def _touch_session(self, user_id: str, session_id: str, response: ChatResponse) -> None:
        self.client.table("chat_sessions").update(
            {
                "intent": response.intent,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ).eq("user_id", user_id).eq("id", session_id).execute()

    def list_sessions(self, user_id: str, *, limit: int = 20) -> list[ChatSessionSummary]:
        result = (
            self.client.table("chat_sessions")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [
            _chat_session_from_row(
                row,
                last_message_preview=self._get_last_message_preview(user_id, str(row["id"])),
            )
            for row in result.data or []
        ]

    def list_messages(self, user_id: str, session_id: str) -> list[ChatMessageRecord]:
        result = (
            self.client.table("chat_messages")
            .select("*")
            .eq("user_id", user_id)
            .eq("session_id", session_id)
            .order("created_at")
            .execute()
        )
        return [_chat_message_from_row(row) for row in result.data or []]

    def delete_session(self, user_id: str, session_id: str) -> None:
        self.client.table("chat_messages").delete().eq("user_id", user_id).eq(
            "session_id", session_id
        ).execute()
        self.client.table("chat_sessions").delete().eq("user_id", user_id).eq(
            "id", session_id
        ).execute()

    def _get_last_message_preview(self, user_id: str, session_id: str) -> str | None:
        result = (
            self.client.table("chat_messages")
            .select("content")
            .eq("user_id", user_id)
            .eq("session_id", session_id)
            .eq("role", "assistant")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        return _message_preview(str(result.data[0].get("content") or ""))


class SupabaseAssignmentStore:
    def __init__(self, client: Any) -> None:
        self.client = client

    def create_assignment(
        self,
        user_id: str,
        request: AssignmentCreateRequest,
    ) -> AssignmentResponse:
        payload = {"user_id": user_id, **request.model_dump()}
        result = self.client.table("assignments").insert(payload).execute()
        return _assignment_from_row(_single_row(result.data))

    def list_assignments(self, user_id: str) -> list[AssignmentResponse]:
        result = (
            self.client.table("assignments")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "todo")
            .order("due_at")
            .execute()
        )
        return [_assignment_from_row(row) for row in result.data or []]

    def get_assignment(self, user_id: str, assignment_id: str) -> AssignmentResponse:
        result = (
            self.client.table("assignments")
            .select("*")
            .eq("user_id", user_id)
            .eq("id", assignment_id)
            .maybe_single()
            .execute()
        )
        if not result.data:
            raise KeyError(assignment_id)
        return _assignment_from_row(result.data)

    def update_assignment(
        self,
        user_id: str,
        assignment_id: str,
        request: AssignmentUpdateRequest,
    ) -> AssignmentResponse:
        payload = request.model_dump(exclude_none=True)
        result = (
            self.client.table("assignments")
            .update(payload)
            .eq("user_id", user_id)
            .eq("id", assignment_id)
            .execute()
        )
        if not result.data:
            raise KeyError(assignment_id)
        return _assignment_from_row(_single_row(result.data))

    def mark_calendar_exported(
        self,
        user_id: str,
        assignment_id: str,
        *,
        calendar_event_id: str,
        synced_at: datetime,
    ) -> AssignmentResponse:
        result = (
            self.client.table("assignments")
            .update(
                {
                    "calendar_event_id": calendar_event_id,
                    "calendar_synced_at": synced_at,
                }
            )
            .eq("user_id", user_id)
            .eq("id", assignment_id)
            .execute()
        )
        if not result.data:
            raise KeyError(assignment_id)
        return _assignment_from_row(_single_row(result.data))

    def delete_assignment(self, user_id: str, assignment_id: str) -> None:
        result = (
            self.client.table("assignments")
            .delete()
            .eq("user_id", user_id)
            .eq("id", assignment_id)
            .execute()
        )
        if result.data == []:
            raise KeyError(assignment_id)


class SupabaseGoogleOAuthTokenStore:
    def __init__(self, client: Any) -> None:
        self.client = client

    def save_token(
        self,
        user_id: str,
        token: GoogleOAuthTokenRecord,
    ) -> GoogleOAuthTokenRecord:
        payload = {
            "user_id": user_id,
            "provider": "google",
            "encrypted_access_token": token.access_token,
            "encrypted_refresh_token": token.refresh_token,
            "scope": token.scope,
            "expires_at": token.expires_at,
        }
        result = self.client.table("google_oauth_tokens").upsert(payload).execute()
        return _google_oauth_token_from_row(_single_row(result.data))

    def get_token(self, user_id: str) -> GoogleOAuthTokenRecord | None:
        result = (
            self.client.table("google_oauth_tokens")
            .select("*")
            .eq("user_id", user_id)
            .eq("provider", "google")
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return _google_oauth_token_from_row(result.data)


class SupabaseLLMUsageLogStore:
    def __init__(self, client: Any) -> None:
        self.client = client

    def create_log(
        self,
        user_id: str,
        request: LLMUsageLogCreateRequest,
    ) -> LLMUsageLogResponse:
        log = LLMUsageLogResponse(user_id=user_id, **request.model_dump())
        payload = log.model_dump(mode="json")
        result = self.client.table("llm_usage_logs").insert(payload).execute()
        return _llm_usage_log_from_row(_single_row(result.data))

    def list_logs(self, user_id: str, *, limit: int = 50) -> list[LLMUsageLogResponse]:
        result = (
            self.client.table("llm_usage_logs")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [_llm_usage_log_from_row(row) for row in result.data or []]


def _profile_from_row(row: dict[str, Any]) -> ProfileResponse:
    return ProfileResponse(
        id=row["id"],
        exists=True,
        department=row.get("department", "unknown"),
        grade=row.get("grade", 1),
        curriculum_year=row.get("curriculum_year", "unknown"),
    )


def _single_row(data: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    # Supabase write responses are list-shaped, while maybe_single reads are dict-shaped.
    # Normalizing here keeps the service layer independent from client response quirks.
    if isinstance(data, list):
        if not data:
            raise RuntimeError("Supabase mutation returned no rows")
        return data[0]
    return data


def _memory_from_row(row: dict[str, Any]) -> MemoryResponse:
    return MemoryResponse(
        id=row["id"],
        category=row["category"],
        key=row["key"],
        value_json=row.get("value_json") or {},
        natural_text=row["natural_text"],
        confidence=float(row.get("confidence", 0.5)),
        sensitivity=row.get("sensitivity", "low"),
        status=row.get("status", "active"),
        embedding_status=row.get("embedding_status", "pending"),
    )


def _memory_event_from_row(row: dict[str, Any]) -> MemoryEventResponse:
    return MemoryEventResponse(
        id=row["id"],
        memory_id=row.get("memory_id"),
        event_type=row["event_type"],
        reason=row.get("reason"),
        snapshot=row.get("snapshot") or {},
    )


def _chat_session_from_row(
    row: dict[str, Any],
    *,
    last_message_preview: str | None = None,
) -> ChatSessionSummary:
    return ChatSessionSummary(
        id=str(row["id"]),
        title=row.get("title"),
        intent=row.get("intent"),
        last_message_preview=last_message_preview,
        updated_at=_datetime_to_string(row.get("updated_at")),
        created_at=_datetime_to_string(row.get("created_at")),
    )


def _chat_message_from_row(row: dict[str, Any]) -> ChatMessageRecord:
    return ChatMessageRecord(
        id=str(row["id"]),
        session_id=str(row["session_id"]),
        role=row["role"],
        content=row["content"],
        evidence=row.get("evidence") or {},
        memory_updates=row.get("memory_updates") or [],
    )


def _assignment_from_row(row: dict[str, Any]) -> AssignmentResponse:
    due_at = row["due_at"]
    if isinstance(due_at, str):
        due_at = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
    return build_assignment_response(
        id=str(row["id"]),
        title=row["title"],
        due_at=due_at,
        course=row.get("course"),
        memo=row.get("memo"),
        status=row.get("status", "todo"),
        calendar_event_id=row.get("calendar_event_id"),
        calendar_synced_at=_parse_datetime(row.get("calendar_synced_at")),
    )


def _google_oauth_token_from_row(row: dict[str, Any]) -> GoogleOAuthTokenRecord:
    return GoogleOAuthTokenRecord(
        user_id=str(row["user_id"]),
        access_token=row["encrypted_access_token"],
        refresh_token=row.get("encrypted_refresh_token"),
        scope=row.get("scope"),
        expires_at=_parse_datetime(row.get("expires_at")),
    )


def _llm_usage_log_from_row(row: dict[str, Any]) -> LLMUsageLogResponse:
    return LLMUsageLogResponse(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        feature=row["feature"],
        input_text=row["input_text"],
        output_text=row.get("output_text"),
        model=row.get("model"),
        purpose=row["purpose"],
        metadata=row.get("metadata") or {},
        created_at=_parse_datetime(row.get("created_at")) or datetime.now(),
    )


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    raise TypeError(f"Unsupported datetime value: {value!r}")


def _datetime_to_string(value: Any) -> str | None:
    parsed = _parse_datetime(value)
    return parsed.isoformat() if parsed is not None else None


def _message_preview(content: str, *, limit: int = 120) -> str:
    normalized = " ".join(content.split())
    return normalized[:limit]
