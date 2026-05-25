from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.chat import ChatMessageRecord, ChatRequest, ChatResponse, ChatSessionSummary

RESPONSE_METADATA_KEY = "__response"


class InMemoryChatStore:
    def __init__(self) -> None:
        self.sessions: dict[str, dict[str, str]] = {}
        self.messages: list[dict[str, object]] = []

    def save_exchange(
        self,
        user_id: str,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse:
        session_id = request.session_id or response.session_id or str(uuid4())
        now = datetime.now(UTC).isoformat()
        title = _chat_session_title(request.message, response.intent)
        self.sessions.setdefault(
            session_id,
            {
                "id": session_id,
                "user_id": user_id,
                "title": title,
                "intent": response.intent,
                "created_at": now,
                "updated_at": now,
                "last_message_preview": response.answer[:120],
            },
        )
        self.sessions[session_id].update(
            {
                "intent": response.intent,
                "updated_at": now,
                "last_message_preview": response.answer[:120],
            }
        )
        response_with_session = response.model_copy(update={"session_id": session_id})
        self.messages.extend(
            [
                {
                    "id": str(uuid4()),
                    "session_id": session_id,
                    "user_id": user_id,
                    "role": "user",
                    "content": request.message,
                    "evidence": {},
                    "memory_updates": [],
                },
                {
                    "id": str(uuid4()),
                    "session_id": session_id,
                    "user_id": user_id,
                    "role": "assistant",
                    "content": response.answer,
                    "evidence": _chat_message_evidence(response),
                    "memory_updates": [
                        memory.model_dump() for memory in response.memory_updates
                    ],
                },
            ]
        )
        return response_with_session

    def list_sessions(self, user_id: str, *, limit: int = 20) -> list[ChatSessionSummary]:
        sessions = [
            session
            for session in self.sessions.values()
            if session["user_id"] == user_id
        ]
        sessions = sorted(sessions, key=lambda session: session.get("updated_at", ""), reverse=True)
        return [
            ChatSessionSummary(
                id=session["id"],
                title=session.get("title"),
                intent=session.get("intent"),
                last_message_preview=session.get("last_message_preview"),
                updated_at=session.get("updated_at"),
                created_at=session.get("created_at"),
            )
            for session in sessions[:limit]
        ]

    def list_messages(self, user_id: str, session_id: str) -> list[ChatMessageRecord]:
        return [
            ChatMessageRecord(
                id=str(message["id"]),
                session_id=str(message["session_id"]),
                role=message["role"],
                content=str(message["content"]),
                evidence=dict(message.get("evidence") or {}),
                memory_updates=list(message.get("memory_updates") or []),
            )
            for message in self.messages
            if message["user_id"] == user_id and message["session_id"] == session_id
        ]

    def delete_session(self, user_id: str, session_id: str) -> None:
        session = self.sessions.get(session_id)
        if not session or session.get("user_id") != user_id:
            return
        self.sessions.pop(session_id, None)
        self.messages = [
            message
            for message in self.messages
            if not (
                message.get("user_id") == user_id
                and message.get("session_id") == session_id
            )
        ]


def _chat_message_evidence(response: ChatResponse) -> dict[str, object]:
    evidence: dict[str, object] = response.evidence.model_dump()
    evidence[RESPONSE_METADATA_KEY] = {
        "intent": response.intent,
        "model": response.model,
        "actions": [action.model_dump() for action in response.actions],
        "choices": [choice.model_dump() for choice in response.choices],
        "needs_verification": response.needs_verification,
    }
    return evidence


def _chat_session_title(message: str, intent: str) -> str:
    normalized = message.strip()
    rules = [
        ("schedule_assistant", "일정 정리"),
        ("career_advisor", "진로 준비 상담"),
        ("startup_project_mentor", "프로젝트 상담"),
        ("academic_advisor", "수강·로드맵 상담"),
    ]
    for target_intent, title in rules:
        if intent == target_intent:
            return title
    if "트랙" in normalized or "과목" in normalized:
        return "트랙·과목 상담"
    if "백엔드" in normalized or "AI" in normalized.upper():
        return "AI·백엔드 상담"
    return "새 상담"
