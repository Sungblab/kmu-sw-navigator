from __future__ import annotations

import jwt
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user_id, get_profile_store
from app.core.config import get_settings
from app.main import app
from app.services.profile_service import InMemoryProfileStore


def test_dev_header_auth_works_without_supabase_jwt_secret(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    get_settings.cache_clear()
    store = InMemoryProfileStore()
    app.dependency_overrides[get_profile_store] = lambda: store
    client = TestClient(app)

    response = client.post(
        "/api/profile",
        headers={"X-User-Id": "dev-user-1"},
        json={"department": "software", "grade": 1, "curriculum_year": "2025"},
    )

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert response.status_code == 200
    assert response.json()["id"] == "dev-user-1"


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
        headers={"Authorization": f"Bearer {token}", "X-User-Id": "ignored-user"},
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

    response = client.get("/api/profile", headers={"X-User-Id": "dev-user-1"})

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
