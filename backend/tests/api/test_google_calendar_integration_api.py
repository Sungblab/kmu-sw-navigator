import httpx
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_current_user_id,
    get_google_oauth_http_client,
    get_google_oauth_token_store,
)
from app.core.config import get_settings
from app.main import app
from app.services.google_calendar_oauth_service import build_google_calendar_connect_response
from app.services.google_oauth_token_service import InMemoryGoogleOAuthTokenStore


def test_google_calendar_status_api_reports_unconfigured(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_OAUTH_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_OAUTH_CLIENT_SECRET", raising=False)
    get_settings.cache_clear()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    client = TestClient(app)

    response = client.get("/api/integrations/google-calendar/status")

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert response.status_code == 200
    assert response.json()["configured"] is False
    assert response.json()["connected"] is False


def test_google_calendar_connect_api_returns_authorization_url(monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "client-id")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv(
        "GOOGLE_OAUTH_REDIRECT_URI",
        "http://127.0.0.1:8000/api/integrations/google-calendar/callback",
    )
    get_settings.cache_clear()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    client = TestClient(app)

    response = client.get("/api/integrations/google-calendar/connect")

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert response.status_code == 200
    assert response.json()["configured"] is True
    assert "accounts.google.com" in response.json()["authorization_url"]


def test_google_calendar_callback_exchanges_code_and_stores_token(monkeypatch) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "access_token": "access-token",
                "refresh_token": "refresh-token",
                "expires_in": 3600,
                "scope": "https://www.googleapis.com/auth/calendar.events",
                "token_type": "Bearer",
            },
        )

    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "client-id")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("GOOGLE_OAUTH_REDIRECT_URI", "http://127.0.0.1/callback")
    get_settings.cache_clear()
    settings = get_settings()
    connect = build_google_calendar_connect_response("user-1", settings)
    assert connect.authorization_url is not None
    state = connect.authorization_url.split("state=", 1)[1]
    store = InMemoryGoogleOAuthTokenStore()
    app.dependency_overrides[get_google_oauth_token_store] = lambda: store
    app.dependency_overrides[get_google_oauth_http_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(handler)
    )
    client = TestClient(app)

    response = client.get(
        "/api/integrations/google-calendar/callback",
        params={"code": "auth-code", "state": state},
    )
    status_response = client.get(
        "/api/integrations/google-calendar/status",
        headers={"X-User-Id": "user-1"},
    )

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert response.status_code == 200
    assert response.json()["connected"] is True
    assert status_response.json()["connected"] is True
    assert store.reveal_access_token("user-1", settings) == "access-token"
