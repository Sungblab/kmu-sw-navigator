from datetime import UTC, date, datetime

import httpx
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_assignment_parser,
    get_assignment_store,
    get_current_user_id,
    get_google_oauth_http_client,
    get_google_oauth_token_store,
)
from app.core.config import get_settings
from app.main import app
from app.services.assignment_service import InMemoryAssignmentStore, ParsedAssignment
from app.services.google_oauth_token_service import InMemoryGoogleOAuthTokenStore


def test_preview_assignment_api_returns_d_day() -> None:
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    client = TestClient(app)

    response = client.post(
        "/api/assignments/preview",
        json={"text": "자료구조 과제 다음주 금요일까지", "reference_date": "2026-05-14"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["d_day_label"] == "D-8"


def test_preview_assignment_api_uses_parser_dependency() -> None:
    class FakeAssignmentParser:
        def parse_assignment(self, text: str, *, reference_date: date) -> ParsedAssignment:
            assert text == "AI 보고서 내일 18시까지"
            return ParsedAssignment(
                title="AI 보고서",
                course="인공지능",
                due_at=datetime(2026, 5, 15, 18, 0),
                confidence=0.91,
            )

    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_assignment_parser] = lambda: FakeAssignmentParser()
    client = TestClient(app)

    response = client.post(
        "/api/assignments/preview",
        json={"text": "AI 보고서 내일 18시까지", "reference_date": "2026-05-14"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["title"] == "AI 보고서"
    assert response.json()["course"] == "인공지능"
    assert response.json()["parser"] == "gemini"


def test_create_and_list_assignments_api() -> None:
    store = InMemoryAssignmentStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_assignment_store] = lambda: store
    client = TestClient(app)

    create_response = client.post(
        "/api/assignments",
        json={
            "title": "자료구조 과제",
            "course": "자료구조",
            "due_at": "2026-05-22T23:59:00",
        },
    )
    list_response = client.get("/api/assignments")

    app.dependency_overrides.clear()
    assert create_response.status_code == 200
    assert create_response.json()["title"] == "자료구조 과제"
    assert list_response.status_code == 200
    assert list_response.json()["assignments"][0]["course"] == "자료구조"


def test_update_and_delete_assignments_api() -> None:
    store = InMemoryAssignmentStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_assignment_store] = lambda: store
    client = TestClient(app)

    create_response = client.post(
        "/api/assignments",
        json={
            "title": "자료구조 과제",
            "course": "자료구조",
            "due_at": "2026-05-22T23:59:00",
        },
    )
    assignment_id = create_response.json()["id"]
    update_response = client.patch(f"/api/assignments/{assignment_id}", json={"status": "done"})
    delete_response = client.delete(f"/api/assignments/{assignment_id}")
    missing_response = client.patch("/api/assignments/missing", json={"status": "done"})

    app.dependency_overrides.clear()
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "done"
    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


def test_export_assignment_to_calendar_api_marks_assignment() -> None:
    store = InMemoryAssignmentStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_assignment_store] = lambda: store
    client = TestClient(app)

    create_response = client.post(
        "/api/assignments",
        json={
            "title": "기말 프로젝트",
            "course": "문제해결코딩",
            "due_at": "2026-06-10T23:59:00",
        },
    )
    assignment_id = create_response.json()["id"]
    export_response = client.post(f"/api/assignments/{assignment_id}/export-calendar")
    second_response = client.post(f"/api/assignments/{assignment_id}/export-calendar")
    missing_response = client.post("/api/assignments/missing/export-calendar")

    app.dependency_overrides.clear()
    assert export_response.status_code == 200
    assert export_response.json()["calendar_event_id"] == f"kmu-{assignment_id}"
    assert export_response.json()["already_exported"] is False
    assert second_response.json()["already_exported"] is True
    assert missing_response.status_code == 404


def test_export_assignment_to_calendar_api_uses_google_token_when_available(monkeypatch) -> None:
    call_urls: list[str] = []

    def handler(_: httpx.Request) -> httpx.Response:
        call_urls.append(str(_.url))
        if str(_.url) == "https://oauth2.googleapis.com/token":
            return httpx.Response(
                200,
                json={
                    "access_token": "new-access-token",
                    "expires_in": 1800,
                    "token_type": "Bearer",
                },
            )
        return httpx.Response(200, json={"id": "google-event-1"})

    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "client-secret")
    get_settings.cache_clear()
    store = InMemoryAssignmentStore()
    token_store = InMemoryGoogleOAuthTokenStore()
    token_store.save_plain_token_for_test(
        "user-1",
        "old-access-token",
        get_settings(),
        refresh_token="refresh-token",
        expires_at=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
    )
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_assignment_store] = lambda: store
    app.dependency_overrides[get_google_oauth_token_store] = lambda: token_store
    app.dependency_overrides[get_google_oauth_http_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(handler)
    )
    client = TestClient(app)

    create_response = client.post(
        "/api/assignments",
        json={
            "title": "자료구조 과제",
            "due_at": "2026-05-22T23:59:00",
        },
    )
    export_response = client.post(
        f"/api/assignments/{create_response.json()['id']}/export-calendar"
    )

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert export_response.status_code == 200
    assert export_response.json()["calendar_event_id"] == "google-event-1"
    assert call_urls == [
        "https://oauth2.googleapis.com/token",
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
    ]
