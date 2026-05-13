from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CalendarExportResponse(BaseModel):
    assignment_id: str
    calendar_event_id: str
    calendar_synced_at: datetime
    already_exported: bool = False
    google_event: dict[str, Any] = Field(default_factory=dict)
