import json
from datetime import UTC, datetime

import httpx

from app.core.config import Settings
from app.schemas.assignment import AssignmentCreateRequest
from app.services.assignment_service import InMemoryAssignmentStore
from app.services.calendar_service import export_assignment_to_calendar
from app.services.google_oauth_token_service import InMemoryGoogleOAuthTokenStore


def test_export_assignment_builds_google_event_payload_and_marks_assignment() -> None:
    store = InMemoryAssignmentStore()
    assignment = store.create_assignment(
        "user-1",
        AssignmentCreateRequest(
            title="기말 프로젝트",
            course="문제해결코딩",
            due_at=datetime(2026, 6, 10, 23, 59),
            memo="팀 repo 제출",
        ),
    )

    exported = export_assignment_to_calendar("user-1", assignment.id, store=store)
    updated = store.get_assignment("user-1", assignment.id)

    assert exported.calendar_event_id == f"kmu-{assignment.id}"
    assert exported.already_exported is False
    assert exported.google_event["summary"] == "문제해결코딩 · 기말 프로젝트"
    assert exported.google_event["start"]["dateTime"] == "2026-06-10T23:29:00"
    assert exported.google_event["end"]["dateTime"] == "2026-06-10T23:59:00"
    assert updated.calendar_event_id == exported.calendar_event_id


def test_export_assignment_is_idempotent_when_calendar_event_exists() -> None:
    store = InMemoryAssignmentStore()
    assignment = store.create_assignment(
        "user-1",
        AssignmentCreateRequest(
            title="자료구조 과제",
            due_at=datetime(2026, 5, 22, 23, 59),
        ),
    )

    first = export_assignment_to_calendar("user-1", assignment.id, store=store)
    second = export_assignment_to_calendar("user-1", assignment.id, store=store)

    assert second.already_exported is True
    assert second.calendar_event_id == first.calendar_event_id


def test_export_assignment_posts_event_to_google_when_token_exists() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        assert request.headers["Authorization"] == "Bearer access-token"
        assert request.headers["Content-Type"] == "application/json"
        assert json.loads(request.content)["summary"] == "자료구조 과제"
        return httpx.Response(200, json={"id": "google-event-1"})

    assignment_store = InMemoryAssignmentStore()
    token_store = InMemoryGoogleOAuthTokenStore()
    settings = Settings(google_oauth_client_secret="client-secret")
    assignment = assignment_store.create_assignment(
        "user-1",
        AssignmentCreateRequest(
            title="자료구조 과제",
            due_at=datetime(2026, 5, 22, 23, 59),
        ),
    )
    token_store.save_plain_token_for_test("user-1", "access-token", settings)

    exported = export_assignment_to_calendar(
        "user-1",
        assignment.id,
        store=assignment_store,
        token_store=token_store,
        settings=settings,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert exported.calendar_event_id == "google-event-1"
    stored = assignment_store.get_assignment("user-1", assignment.id)
    assert stored.calendar_event_id == "google-event-1"


def test_export_assignment_refreshes_expired_token_before_google_insert() -> None:
    seen_authorizations: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url == "https://oauth2.googleapis.com/token":
            return httpx.Response(
                200,
                json={
                    "access_token": "new-access-token",
                    "expires_in": 1800,
                    "token_type": "Bearer",
                },
            )
        seen_authorizations.append(request.headers["Authorization"])
        return httpx.Response(200, json={"id": "google-event-2"})

    assignment_store = InMemoryAssignmentStore()
    token_store = InMemoryGoogleOAuthTokenStore()
    settings = Settings(
        google_oauth_client_id="client-id",
        google_oauth_client_secret="client-secret",
    )
    assignment = assignment_store.create_assignment(
        "user-1",
        AssignmentCreateRequest(
            title="운영체제 과제",
            due_at=datetime(2026, 5, 22, 23, 59),
        ),
    )
    token_store.save_plain_token_for_test(
        "user-1",
        "old-access-token",
        settings,
        refresh_token="refresh-token",
        expires_at=datetime(2026, 5, 14, 11, 0, tzinfo=UTC),
    )

    exported = export_assignment_to_calendar(
        "user-1",
        assignment.id,
        store=assignment_store,
        token_store=token_store,
        settings=settings,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        now=datetime(2026, 5, 14, 12, 0, tzinfo=UTC),
    )

    assert exported.calendar_event_id == "google-event-2"
    assert seen_authorizations == ["Bearer new-access-token"]
