from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.memory import MemoryResponse

ChatIntent = Literal[
    "academic_advisor",
    "career_advisor",
    "startup_project_mentor",
    "schedule_assistant",
    "general",
]
ChatMode = Literal["auto", "academic", "career", "schedule"]
ChatModelTier = Literal["balanced", "fast"]


class ChatAttachment(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    mime_type: str = Field(default="application/octet-stream", max_length=120)
    size: int = Field(ge=0, le=2_000_000)
    text_content: str | None = Field(default=None, max_length=12_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = None
    mode: ChatMode = "auto"
    model_tier: ChatModelTier = "balanced"
    attachments: list[ChatAttachment] = Field(default_factory=list, max_length=3)


class ChatAction(BaseModel):
    type: str
    label: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ChatEvidence(BaseModel):
    personalization: list[str] = Field(default_factory=list)
    internal_sources: list[dict[str, Any]] = Field(default_factory=list)
    web_sources: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ChoiceOption(BaseModel):
    id: str
    label: str
    message: str


class ChatResponse(BaseModel):
    session_id: str | None = None
    answer: str
    intent: ChatIntent
    model: str | None = None
    actions: list[ChatAction] = Field(default_factory=list)
    evidence: ChatEvidence = Field(default_factory=ChatEvidence)
    choices: list[ChoiceOption] = Field(default_factory=list)
    memory_updates: list[MemoryResponse] = Field(default_factory=list)
    needs_verification: list[str] = Field(default_factory=list)


class ChatSessionSummary(BaseModel):
    id: str
    title: str | None = None
    intent: str | None = None
    last_message_preview: str | None = None
    updated_at: str | None = None
    created_at: str | None = None


class ChatMessageRecord(BaseModel):
    id: str
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    memory_updates: list[dict[str, Any]] = Field(default_factory=list)


class ChatSessionsResponse(BaseModel):
    sessions: list[ChatSessionSummary] = Field(default_factory=list)


class ChatMessagesResponse(BaseModel):
    messages: list[ChatMessageRecord] = Field(default_factory=list)
