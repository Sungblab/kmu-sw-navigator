from datetime import UTC, datetime

import httpx

from app.core.config import Settings
from app.services.google_oauth_token_service import (
    InMemoryGoogleOAuthTokenStore,
    exchange_google_calendar_code,
    refresh_google_calendar_token,
)


def test_exchange_google_calendar_code_stores_token_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = request.content.decode()
        assert request.url == "https://oauth2.googleapis.com/token"
        assert "code=auth-code" in body
        assert "grant_type=authorization_code" in body
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

    store = InMemoryGoogleOAuthTokenStore()
    client = httpx.Client(transport=httpx.MockTransport(handler))
    settings = Settings(
        google_oauth_client_id="client-id",
        google_oauth_client_secret="client-secret",
        google_oauth_redirect_uri="http://127.0.0.1/callback",
    )

    saved = exchange_google_calendar_code(
        "user-1",
        code="auth-code",
        settings=settings,
        store=store,
        client=client,
        now=datetime(2026, 5, 14, 12, 0, tzinfo=UTC),
    )

    assert saved.connected is True
    assert saved.expires_at.isoformat() == "2026-05-14T13:00:00+00:00"
    assert store.get_token("user-1").access_token != "access-token"
    assert store.reveal_access_token("user-1", settings) == "access-token"


def test_refresh_google_calendar_token_updates_access_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = request.content.decode()
        assert request.url == "https://oauth2.googleapis.com/token"
        assert "grant_type=refresh_token" in body
        assert "refresh_token=refresh-token" in body
        return httpx.Response(
            200,
            json={
                "access_token": "new-access-token",
                "expires_in": 1800,
                "scope": "https://www.googleapis.com/auth/calendar.events",
                "token_type": "Bearer",
            },
        )

    store = InMemoryGoogleOAuthTokenStore()
    settings = Settings(
        google_oauth_client_id="client-id",
        google_oauth_client_secret="client-secret",
    )
    store.save_plain_token_for_test(
        "user-1",
        "old-access-token",
        settings,
        refresh_token="refresh-token",
        expires_at=datetime(2026, 5, 14, 11, 0, tzinfo=UTC),
    )

    refreshed = refresh_google_calendar_token(
        "user-1",
        settings=settings,
        store=store,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        now=datetime(2026, 5, 14, 12, 0, tzinfo=UTC),
    )

    assert refreshed.connected is True
    assert refreshed.expires_at.isoformat() == "2026-05-14T12:30:00+00:00"
    assert store.reveal_access_token("user-1", settings) == "new-access-token"
