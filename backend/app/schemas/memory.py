from typing import Any, Literal

from pydantic import BaseModel, Field

MemorySensitivity = Literal["low", "medium", "high"]
MemoryStatus = Literal["candidate", "active", "archived", "rejected"]
EmbeddingStatus = Literal["pending", "ready", "failed"]
MemoryEventType = Literal[
    "created",
    "candidate_created",
    "confirmed",
    "rejected",
    "updated",
    "archived",
]


class MemoryResponse(BaseModel):
    id: str
    category: str
    key: str
    value_json: dict[str, Any] = Field(default_factory=dict)
    natural_text: str
    confidence: float = Field(default=0.5, ge=0, le=1)
    sensitivity: MemorySensitivity = "low"
    status: MemoryStatus = "active"
    embedding_status: EmbeddingStatus = "pending"


class MemoryEventResponse(BaseModel):
    id: str
    memory_id: str | None = None
    event_type: MemoryEventType
    reason: str | None = None
    snapshot: dict[str, Any] = Field(default_factory=dict)


class MemoryUpdateRequest(BaseModel):
    natural_text: str | None = None
    value_json: dict[str, Any] | None = None
    status: MemoryStatus | None = None


class MemoryCreateRequest(BaseModel):
    natural_text: str = Field(min_length=1)
    category: str = Field(min_length=1)
    key: str = Field(min_length=1)
    value_json: dict[str, Any] = Field(default_factory=dict)
