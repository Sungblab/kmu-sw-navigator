from __future__ import annotations

import httpx

from app.scripts.auth_api_smoke import (
    build_profile_smoke_payload,
    normalize_api_base,
    resolve_access_token,
    run_auth_api_smoke,
)


def test_resolve_access_token_prefers_cli_value() -> None:
    assert resolve_access_token("cli-token", "env-token") == "cli-token"


def test_resolve_access_token_uses_env_value() -> None:
    assert resolve_access_token(None, "env-token") == "env-token"


def test_resolve_access_token_returns_none_when_missing(
    monkeypatch,
) -> None:
    monkeypatch.delenv("SUPABASE_SMOKE_ACCESS_TOKEN", raising=False)

    assert resolve_access_token(None, None) is None


def test_normalize_api_base_removes_trailing_slash() -> None:
    assert normalize_api_base("http://127.0.0.1:8000/") == "http://127.0.0.1:8000"


def test_build_profile_smoke_payload_matches_demo_profile() -> None:
    assert build_profile_smoke_payload() == {
        "department": "software",
        "grade": 1,
        "curriculum_year": "2025",
    }


def test_run_auth_api_smoke_posts_and_reads_profile() -> None:
    seen_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        assert request.headers["Authorization"] == "Bearer access-token"
        if request.method == "POST":
            return httpx.Response(200, json={**build_profile_smoke_payload(), "id": "user-id"})
        return httpx.Response(200, json={**build_profile_smoke_payload(), "id": "user-id"})

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = run_auth_api_smoke(client, "http://api.test/", "access-token")

    assert [request.method for request in seen_requests] == ["POST", "GET"]
    assert [request.url.path for request in seen_requests] == ["/api/profile", "/api/profile"]
    assert result == {
        "profile_department": "software",
        "profile_grade": 1,
        "profile_exists": True,
    }
