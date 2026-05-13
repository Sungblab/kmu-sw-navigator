from __future__ import annotations

import json
from datetime import datetime

import httpx
import pytest

from app.core.config import Settings
from app.scripts.calendar_export_smoke import (
    build_smoke_assignment_request,
    resolve_calendar_smoke_user_id,
    run_calendar_export_smoke,
)
from app.services.assignment_service import InMemoryAssignmentStore
from app.services.google_oauth_token_service import InMemoryGoogleOAuthTokenStore


def test_resolve_calendar_smoke_user_id_accepts_uuid() -> None:
    user_id = "11111111-1111-4111-8111-111111111111"

    assert resolve_calendar_smoke_user_id(user_id, None) == user_id


def test_resolve_calendar_smoke_user_id_rejects_non_uuid() -> None:
    with pytest.raises(ValueError, match="auth.users UUID"):
        resolve_calendar_smoke_user_id("demo-user", None)


def test_build_smoke_assignment_request() -> None:
    request = build_smoke_assignment_request()

    assert request.title == "Google Calendar smoke 과제"
    assert request.course == "캡스톤"
    assert request.due_at == datetime(2026, 6, 10, 23, 59)


def test_run_calendar_export_smoke_requires_existing_google_token() -> None:
    with pytest.raises(RuntimeError, match="Google Calendar token"):
        run_calendar_export_smoke(
            user_id="11111111-1111-4111-8111-111111111111",
            assignment_store=InMemoryAssignmentStore(),
            token_store=InMemoryGoogleOAuthTokenStore(),
            settings=Settings(google_oauth_client_secret="client-secret"),
            client=httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(500))),
        )


def test_run_calendar_export_smoke_posts_google_event() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.url == "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        assert request.headers["Authorization"] == "Bearer access-token"
        assert json.loads(request.content)["summary"] == "캡스톤 · Google Calendar smoke 과제"
        return httpx.Response(200, json={"id": "google-smoke-event"})

    user_id = "11111111-1111-4111-8111-111111111111"
    assignment_store = InMemoryAssignmentStore()
    token_store = InMemoryGoogleOAuthTokenStore()
    settings = Settings(google_oauth_client_secret="client-secret")
    token_store.save_plain_token_for_test(user_id, "access-token", settings)

    result = run_calendar_export_smoke(
        user_id=user_id,
        assignment_store=assignment_store,
        token_store=token_store,
        settings=settings,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert len(requests) == 1
    assert result == {
        "assignment_title": "Google Calendar smoke 과제",
        "calendar_event_id": "google-smoke-event",
        "already_exported": False,
    }
