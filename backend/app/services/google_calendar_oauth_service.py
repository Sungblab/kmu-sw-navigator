import base64
import hashlib
import hmac
import json
from urllib.parse import urlencode

from app.core.config import Settings
from app.schemas.integration import (
    GoogleCalendarConnectResponse,
    GoogleCalendarStatusResponse,
)
from app.services.google_oauth_token_service import GoogleOAuthTokenStore

GOOGLE_OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


def get_google_calendar_status(
    settings: Settings,
    *,
    user_id: str | None = None,
    store: GoogleOAuthTokenStore | None = None,
) -> GoogleCalendarStatusResponse:
    return GoogleCalendarStatusResponse(
        configured=settings.has_google_calendar_oauth,
        connected=bool(user_id and store and store.get_token(user_id)),
        scope=settings.google_calendar_scope,
    )


def build_google_calendar_connect_response(
    user_id: str,
    settings: Settings,
) -> GoogleCalendarConnectResponse:
    if not settings.has_google_calendar_oauth:
        return GoogleCalendarConnectResponse(
            configured=False,
            scope=settings.google_calendar_scope,
            reason="Google OAuth 환경 변수가 설정되지 않았습니다.",
        )

    # Calendar OAuth는 앱 로그인과 별개이므로, 백엔드가 consent URL을 만들고
    # 프론트는 이 URL로 이동만 한다. 토큰 교환은 callback slice에서 처리한다.
    query = urlencode(
        {
            "client_id": settings.google_oauth_client_id,
            "redirect_uri": settings.google_oauth_redirect_uri,
            "response_type": "code",
            "scope": settings.google_calendar_scope,
            "access_type": "offline",
            "prompt": "consent",
            "state": _build_state(user_id, settings.google_oauth_client_secret),
        }
    )
    return GoogleCalendarConnectResponse(
        configured=True,
        authorization_url=f"{GOOGLE_OAUTH_AUTH_URL}?{query}",
        scope=settings.google_calendar_scope,
    )


def _build_state(user_id: str, secret: str) -> str:
    payload = _b64url_encode(json.dumps({"uid": user_id}, separators=(",", ":")).encode())
    signature = _sign_state_payload(payload, secret)
    return f"{payload}.{signature}"


def parse_google_calendar_state(state: str, settings: Settings) -> str:
    payload, signature = state.split(".", 1)
    expected = _sign_state_payload(payload, settings.google_oauth_client_secret)
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid Google Calendar OAuth state")
    decoded = json.loads(_b64url_decode(payload).decode())
    return str(decoded["uid"])


def _sign_state_payload(payload: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    return _b64url_encode(digest)


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode())
