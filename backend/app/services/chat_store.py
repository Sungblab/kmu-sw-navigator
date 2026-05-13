from __future__ import annotations

from uuid import uuid4

from app.schemas.chat import ChatMessageRecord, ChatRequest, ChatResponse, ChatSessionSummary


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
        # 첫 질문 일부를 session title로 두면 채팅 목록에서 사람이 식별하기 쉽다.
        self.sessions.setdefault(
            session_id,
            {
                "id": session_id,
                "user_id": user_id,
                "title": request.message[:80],
                "intent": response.intent,
            },
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
                    "evidence": response.evidence.model_dump(),
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
        return [
            ChatSessionSummary(
                id=session["id"],
                title=session.get("title"),
                intent=session.get("intent"),
            )
            for session in sessions[-limit:][::-1]
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
