from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.core.config import Settings
from app.schemas.assignment import AssignmentResponse
from app.schemas.calendar import CalendarExportResponse
from app.services.google_oauth_token_service import (
    GoogleOAuthTokenStore,
    refresh_google_calendar_token,
    reveal_protected_access_token,
    token_needs_refresh,
)
from app.services.store_protocols import AssignmentStore

DEFAULT_TIMEZONE = "Asia/Seoul"
GOOGLE_CALENDAR_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"


def export_assignment_to_calendar(
    user_id: str,
    assignment_id: str,
    *,
    store: AssignmentStore,
    token_store: GoogleOAuthTokenStore | None = None,
    settings: Settings | None = None,
    client: httpx.Client | None = None,
    now: datetime | None = None,
) -> CalendarExportResponse:
    assignment = store.get_assignment(user_id, assignment_id)
    google_event = build_google_calendar_event(assignment)

    if assignment.calendar_event_id and assignment.calendar_synced_at:
        return CalendarExportResponse(
            assignment_id=assignment.id,
            calendar_event_id=assignment.calendar_event_id,
            calendar_synced_at=assignment.calendar_synced_at,
            already_exported=True,
            google_event=google_event,
        )

    synced_at = now or datetime.now(UTC)
    calendar_event_id = _create_google_calendar_event(
        user_id,
        google_event,
        token_store=token_store,
        settings=settings,
        client=client,
        now=synced_at,
    ) or f"kmu-{assignment.id}"
    updated = store.mark_calendar_exported(
        user_id,
        assignment_id,
        calendar_event_id=calendar_event_id,
        synced_at=synced_at,
    )
    return CalendarExportResponse(
        assignment_id=updated.id,
        calendar_event_id=calendar_event_id,
        calendar_synced_at=synced_at,
        already_exported=False,
        google_event=google_event,
    )


def _create_google_calendar_event(
    user_id: str,
    google_event: dict[str, Any],
    *,
    token_store: GoogleOAuthTokenStore | None,
    settings: Settings | None,
    client: httpx.Client | None,
    now: datetime,
) -> str | None:
    if not token_store or not settings:
        return None
    token_record = token_store.get_token(user_id)
    if not token_record:
        return None

    http_client = client or httpx.Client(timeout=10)
    if token_needs_refresh(token_record, now=now):
        refresh_google_calendar_token(
            user_id,
            settings=settings,
            store=token_store,
            client=http_client,
            now=now,
        )
        token_record = token_store.get_token(user_id)
        if not token_record:
            return None
    access_token = reveal_protected_access_token(token_record, settings)
    response = http_client.post(
        GOOGLE_CALENDAR_EVENTS_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json=google_event,
    )
    response.raise_for_status()
    return str(response.json()["id"])


def build_google_calendar_event(assignment: AssignmentResponse) -> dict[str, Any]:
    start_at = assignment.due_at - timedelta(minutes=30)
    summary = (
        f"{assignment.course} · {assignment.title}"
        if assignment.course
        else assignment.title
    )
    description_parts = [
        "kmu-sw-navigator에서 내보낸 과제 일정입니다.",
    ]
    if assignment.memo:
        description_parts.append(f"메모: {assignment.memo}")

    # 과제 마감은 한 시점이지만 Google Calendar event는 시작/종료가 필요하다.
    # 마감 직전 준비 시간을 캘린더에서 분리해 볼 수 있도록 30분짜리 event로 변환한다.
    return {
        "summary": summary,
        "description": "\n".join(description_parts),
        "start": {
            "dateTime": start_at.isoformat(),
            "timeZone": DEFAULT_TIMEZONE,
        },
        "end": {
            "dateTime": assignment.due_at.isoformat(),
            "timeZone": DEFAULT_TIMEZONE,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 24 * 60},
                {"method": "popup", "minutes": 60},
            ],
        },
    }
