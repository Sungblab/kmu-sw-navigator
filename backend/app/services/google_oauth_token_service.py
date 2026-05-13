from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Protocol

import httpx

from app.core.config import Settings
from app.schemas.google_oauth import (
    GoogleOAuthConnectionResponse,
    GoogleOAuthTokenRecord,
)

GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"


class GoogleOAuthTokenStore(Protocol):
    def save_token(
        self,
        user_id: str,
        token: GoogleOAuthTokenRecord,
    ) -> GoogleOAuthTokenRecord: ...

    def get_token(self, user_id: str) -> GoogleOAuthTokenRecord | None: ...


class InMemoryGoogleOAuthTokenStore:
    def __init__(self) -> None:
        self.tokens: dict[str, GoogleOAuthTokenRecord] = {}

    def save_token(
        self,
        user_id: str,
        token: GoogleOAuthTokenRecord,
    ) -> GoogleOAuthTokenRecord:
        self.tokens[user_id] = token
        return token

    def get_token(self, user_id: str) -> GoogleOAuthTokenRecord | None:
        return self.tokens.get(user_id)

    def reveal_access_token(self, user_id: str, settings: Settings) -> str:
        token = self.tokens[user_id]
        return _unprotect_token(token.access_token, settings.google_oauth_client_secret)

    def save_plain_token_for_test(
        self,
        user_id: str,
        access_token: str,
        settings: Settings,
        refresh_token: str | None = None,
        expires_at: datetime | None = None,
    ) -> GoogleOAuthTokenRecord:
        token = GoogleOAuthTokenRecord(
            user_id=user_id,
            access_token=_protect_token(access_token, settings.google_oauth_client_secret),
            refresh_token=(
                _protect_token(refresh_token, settings.google_oauth_client_secret)
                if refresh_token
                else None
            ),
            expires_at=expires_at,
        )
        return self.save_token(user_id, token)


def exchange_google_calendar_code(
    user_id: str,
    *,
    code: str,
    settings: Settings,
    store: GoogleOAuthTokenStore,
    client: httpx.Client | None = None,
    now: datetime | None = None,
) -> GoogleOAuthConnectionResponse:
    http_client = client or httpx.Client(timeout=10)
    response = http_client.post(
        GOOGLE_OAUTH_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.google_oauth_client_id,
            "client_secret": settings.google_oauth_client_secret,
            "redirect_uri": settings.google_oauth_redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    response.raise_for_status()
    payload = response.json()
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + timedelta(seconds=int(payload.get("expires_in", 0)))

    # 토큰은 프론트로 반환하지 않고 서버 저장소에만 둔다. 테스트/로컬에서도 평문 저장을
    # 피하기 위해 OAuth client secret으로 서명된 keystream을 만들어 보호 문자열로 저장한다.
    token = GoogleOAuthTokenRecord(
        user_id=user_id,
        access_token=_protect_token(payload["access_token"], settings.google_oauth_client_secret),
        refresh_token=(
            _protect_token(payload["refresh_token"], settings.google_oauth_client_secret)
            if payload.get("refresh_token")
            else None
        ),
        scope=payload.get("scope"),
        expires_at=expires_at,
    )
    saved = store.save_token(user_id, token)
    return GoogleOAuthConnectionResponse(
        connected=True,
        scope=saved.scope,
        expires_at=saved.expires_at,
    )


def reveal_protected_access_token(
    record: GoogleOAuthTokenRecord,
    settings: Settings,
) -> str:
    return _unprotect_token(record.access_token, settings.google_oauth_client_secret)


def reveal_protected_refresh_token(
    record: GoogleOAuthTokenRecord,
    settings: Settings,
) -> str | None:
    if not record.refresh_token:
        return None
    return _unprotect_token(record.refresh_token, settings.google_oauth_client_secret)


def refresh_google_calendar_token(
    user_id: str,
    *,
    settings: Settings,
    store: GoogleOAuthTokenStore,
    client: httpx.Client | None = None,
    now: datetime | None = None,
) -> GoogleOAuthConnectionResponse:
    current = store.get_token(user_id)
    if not current:
        raise ValueError("Google OAuth token is missing")
    refresh_token = reveal_protected_refresh_token(current, settings)
    if not refresh_token:
        raise ValueError("Google OAuth refresh token is missing")

    http_client = client or httpx.Client(timeout=10)
    response = http_client.post(
        GOOGLE_OAUTH_TOKEN_URL,
        data={
            "client_id": settings.google_oauth_client_id,
            "client_secret": settings.google_oauth_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    response.raise_for_status()
    payload = response.json()
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + timedelta(seconds=int(payload.get("expires_in", 0)))
    refreshed = GoogleOAuthTokenRecord(
        user_id=user_id,
        access_token=_protect_token(payload["access_token"], settings.google_oauth_client_secret),
        refresh_token=current.refresh_token,
        scope=payload.get("scope") or current.scope,
        expires_at=expires_at,
    )
    saved = store.save_token(user_id, refreshed)
    return GoogleOAuthConnectionResponse(
        connected=True,
        scope=saved.scope,
        expires_at=saved.expires_at,
    )


def token_needs_refresh(
    record: GoogleOAuthTokenRecord,
    *,
    now: datetime | None = None,
    skew_seconds: int = 60,
) -> bool:
    if not record.expires_at:
        return False
    base = now or datetime.now(UTC)
    return record.expires_at <= base + timedelta(seconds=skew_seconds)


def _protect_token(token: str, secret: str) -> str:
    raw = token.encode()
    key = _token_key(secret, len(raw))
    encrypted = bytes(value ^ key[index] for index, value in enumerate(raw))
    mac = hmac.new(secret.encode(), encrypted, hashlib.sha256).digest()
    return _b64url(encrypted + mac)


def _unprotect_token(protected: str, secret: str) -> str:
    data = _unb64url(protected)
    encrypted, mac = data[:-32], data[-32:]
    expected = hmac.new(secret.encode(), encrypted, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        raise ValueError("Invalid protected token")
    key = _token_key(secret, len(encrypted))
    return bytes(value ^ key[index] for index, value in enumerate(encrypted)).decode()


def _token_key(secret: str, length: int) -> bytes:
    blocks = []
    counter = 0
    while sum(len(block) for block in blocks) < length:
        blocks.append(
            hmac.new(secret.encode(), str(counter).encode(), hashlib.sha256).digest()
        )
        counter += 1
    return b"".join(blocks)[:length]


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _unb64url(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode())
