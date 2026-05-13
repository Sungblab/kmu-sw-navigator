from app.core.config import Settings
from app.services.google_calendar_oauth_service import (
    build_google_calendar_connect_response,
    get_google_calendar_status,
    parse_google_calendar_state,
)


def test_google_calendar_status_reports_missing_configuration() -> None:
    status = get_google_calendar_status(Settings())

    assert status.configured is False
    assert status.connected is False
    assert status.scope == "https://www.googleapis.com/auth/calendar.events"


def test_google_calendar_connect_response_builds_authorization_url() -> None:
    settings = Settings(
        google_oauth_client_id="client-id",
        google_oauth_client_secret="client-secret",
        google_oauth_redirect_uri="http://127.0.0.1:8000/api/integrations/google-calendar/callback",
    )

    response = build_google_calendar_connect_response("user-1", settings)

    assert response.configured is True
    assert response.authorization_url is not None
    assert "https://accounts.google.com/o/oauth2/v2/auth" in response.authorization_url
    assert "client_id=client-id" in response.authorization_url
    assert (
        "scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar.events"
        in response.authorization_url
    )
    assert "access_type=offline" in response.authorization_url
    assert "user-1" not in response.authorization_url


def test_google_calendar_state_round_trips_without_raw_user_id() -> None:
    settings = Settings(google_oauth_client_secret="client-secret")
    response = build_google_calendar_connect_response(
        "user-1",
        Settings(
            google_oauth_client_id="client-id",
            google_oauth_client_secret="client-secret",
            google_oauth_redirect_uri="http://127.0.0.1/callback",
        ),
    )
    assert response.authorization_url is not None
    state = response.authorization_url.split("state=", 1)[1]

    assert "user-1" not in state
    assert parse_google_calendar_state(state, settings) == "user-1"
