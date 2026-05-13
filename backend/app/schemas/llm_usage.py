from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class LLMUsageLogCreateRequest(BaseModel):
    feature: str = Field(min_length=1)
    input_text: str = Field(min_length=1)
    output_text: str | None = None
    model: str | None = None
    purpose: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMUsageLogResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    feature: str
    input_text: str
    output_text: str | None = None
    model: str | None = None
    purpose: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LLMUsageLogListResponse(BaseModel):
    logs: list[LLMUsageLogResponse] = Field(default_factory=list)
