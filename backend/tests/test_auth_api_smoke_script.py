from __future__ import annotations

import httpx

from app.scripts.auth_api_smoke import (
    build_onboarding_memory_smoke_payload,
    build_profile_smoke_payload,
    check_api_contract,
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


def test_build_onboarding_memory_smoke_payload_matches_live_onboarding() -> None:
    payload = build_onboarding_memory_smoke_payload()

    assert payload["category"] == "onboarding"
    assert payload["key"] == "learning_context"
    assert payload["value_json"]["interests"] == ["AI", "백엔드"]
    assert "온보딩 관심사" in payload["natural_text"]


def test_check_api_contract_requires_runtime_public_status() -> None:
    seen_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_paths.append(request.url.path)
        if request.url.path == "/api/runtime/public-status":
            return httpx.Response(200, json={"mode": "live"})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    check_api_contract(client, "http://api.test/")

    assert seen_paths == ["/api/runtime/public-status"]


def test_check_api_contract_fails_for_stale_backend() -> None:
    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(404)))

    try:
        check_api_contract(client, "http://api.test/")
    except RuntimeError as exc:
        assert "/api/runtime/public-status" in str(exc)
        assert "Restart FastAPI" in str(exc)
    else:
        raise AssertionError("Expected stale backend contract failure")


def test_run_auth_api_smoke_posts_profile_memory_and_reads_profile() -> None:
    seen_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        if request.url.path == "/api/runtime/public-status":
            return httpx.Response(200, json={"mode": "live"})
        assert request.headers["Authorization"] == "Bearer access-token"
        if request.method == "POST" and request.url.path == "/api/profile":
            return httpx.Response(200, json={**build_profile_smoke_payload(), "id": "user-id"})
        if request.method == "POST" and request.url.path == "/api/memories":
            return httpx.Response(
                200,
                json={
                    **build_onboarding_memory_smoke_payload(),
                    "id": "memory-id",
                    "confidence": 0.7,
                    "sensitivity": "low",
                    "status": "active",
                    "embedding_status": "pending",
                },
            )
        return httpx.Response(200, json={**build_profile_smoke_payload(), "id": "user-id"})

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = run_auth_api_smoke(client, "http://api.test/", "access-token")

    assert [request.method for request in seen_requests] == ["GET", "POST", "POST", "GET"]
    assert [request.url.path for request in seen_requests] == [
        "/api/runtime/public-status",
        "/api/profile",
        "/api/memories",
        "/api/profile",
    ]
    assert result == {
        "profile_department": "software",
        "profile_grade": 1,
        "profile_exists": True,
        "onboarding_memory_status": "active",
    }
