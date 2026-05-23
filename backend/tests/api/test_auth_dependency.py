from __future__ import annotations

import httpx
import jwt
from fastapi.testclient import TestClient

from app.api import auth as auth_api
from app.api.dependencies import get_current_user_id, get_profile_store
from app.core.config import get_settings
from app.main import app
from app.services.profile_service import InMemoryProfileStore


def test_request_without_supabase_session_is_rejected(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "")
    get_settings.cache_clear()
    app.dependency_overrides[get_profile_store] = lambda: InMemoryProfileStore()
    client = TestClient(app)

    response = client.post(
        "/api/profile",
        json={"department": "software", "grade": 1, "curriculum_year": "2025"},
    )

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert response.status_code == 401


def test_supabase_auth_api_uses_verified_session_user(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role")
    get_settings.cache_clear()

    def fake_get(url: str, *, headers: dict[str, str], timeout: int) -> httpx.Response:
        assert url == "https://example.supabase.co/auth/v1/user"
        assert headers["apikey"] == "service-role"
        assert headers["Authorization"] == "Bearer live-token"
        assert timeout == 10
        return httpx.Response(
            200,
            json={"id": "supabase-user-api"},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(auth_api.httpx, "get", fake_get)
    store = InMemoryProfileStore()
    app.dependency_overrides[get_profile_store] = lambda: store
    client = TestClient(app)

    response = client.post(
        "/api/profile",
        headers={"Authorization": "Bearer live-token"},
        json={"department": "software", "grade": 1, "curriculum_year": "2025"},
    )

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert response.status_code == 200
    assert response.json()["id"] == "supabase-user-api"


def test_supabase_jwt_auth_uses_verified_subject(monkeypatch) -> None:
    secret = "test-supabase-jwt-secret-with-enough-length"
    monkeypatch.setenv("SUPABASE_JWT_SECRET", secret)
    get_settings.cache_clear()
    store = InMemoryProfileStore()
    app.dependency_overrides[get_profile_store] = lambda: store
    token = jwt.encode(
        {"sub": "supabase-user-1", "aud": "authenticated"},
        secret,
        algorithm="HS256",
    )
    client = TestClient(app)

    response = client.post(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"department": "software", "grade": 1, "curriculum_year": "2025"},
    )

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert response.status_code == 200
    assert response.json()["id"] == "supabase-user-1"


def test_supabase_jwt_auth_rejects_missing_bearer_token(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-supabase-jwt-secret-with-enough-length")
    get_settings.cache_clear()
    app.dependency_overrides[get_profile_store] = lambda: InMemoryProfileStore()
    client = TestClient(app)

    response = client.get("/api/profile")

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert response.status_code == 401


def test_auth_dependency_override_still_supports_unit_tests() -> None:
    app.dependency_overrides[get_current_user_id] = lambda: "override-user"
    app.dependency_overrides[get_profile_store] = lambda: InMemoryProfileStore()
    client = TestClient(app)

    response = client.get("/api/profile")

    app.dependency_overrides.clear()
    assert response.status_code == 200
