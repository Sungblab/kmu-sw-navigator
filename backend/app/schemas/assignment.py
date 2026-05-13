from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

AssignmentStatus = Literal["todo", "done"]


class AssignmentParseRequest(BaseModel):
    text: str = Field(min_length=1)
    reference_date: date | None = None


class AssignmentCreateRequest(BaseModel):
    title: str
    due_at: datetime
    course: str | None = None
    memo: str | None = None


class AssignmentUpdateRequest(BaseModel):
    status: AssignmentStatus | None = None


class AssignmentResponse(BaseModel):
    id: str
    title: str
    course: str | None = None
    due_at: datetime
    memo: str | None = None
    status: AssignmentStatus = "todo"
    calendar_event_id: str | None = None
    calendar_synced_at: datetime | None = None
    d_day: int
    d_day_label: str


class AssignmentPreviewResponse(BaseModel):
    title: str
    course: str | None = None
    due_at: datetime
    memo: str | None = None
    d_day: int
    d_day_label: str
    confidence: float
    missing_fields: list[str] = Field(default_factory=list)
    parser: str = "python_rules"


class AssignmentListResponse(BaseModel):
    assignments: list[AssignmentResponse] = Field(default_factory=list)
