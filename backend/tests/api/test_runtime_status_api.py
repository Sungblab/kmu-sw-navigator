from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user_id
from app.api.runtime import get_runtime_schema_items
from app.core.config import get_settings
from app.main import app


def test_runtime_status_api_returns_non_secret_live_readiness(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-secret")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "google-client-id")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "google-secret")
    get_settings.cache_clear()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_runtime_schema_items] = lambda: []
    client = TestClient(app)

    response = client.get("/api/runtime/status")

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    payload = response.json()
    assert response.status_code == 200
    assert payload["mode"] == "live"
    assert payload["supabase_backend"]["ready"] is True
    assert payload["gemini"]["ready"] is True
    assert payload["google_calendar"]["ready"] is True
    assert "service-role-secret" not in response.text
    assert "gemini-secret" not in response.text


def test_public_runtime_status_does_not_require_auth(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-secret")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")
    get_settings.cache_clear()
    app.dependency_overrides[get_runtime_schema_items] = lambda: []
    client = TestClient(app)

    response = client.get("/api/runtime/public-status")

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    assert response.status_code == 200
    assert response.json()["gemini"]["ready"] is True
    assert "service-role-secret" not in response.text
    assert "gemini-secret" not in response.text
