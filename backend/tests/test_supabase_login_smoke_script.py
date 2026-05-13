from __future__ import annotations

import httpx
import pytest

from app.scripts.supabase_login_smoke import (
    SupabaseLoginSmokeConfig,
    build_password_token_url,
    fetch_access_token,
    resolve_login_config,
    run_login_auth_api_smoke,
)


def test_resolve_login_config_uses_cli_values() -> None:
    config = resolve_login_config(
        supabase_url="https://project.supabase.co/",
        anon_key="anon",
        email="student@example.com",
        password="password",
        api_base="http://127.0.0.1:8000/",
        env={},
    )

    assert config == SupabaseLoginSmokeConfig(
        supabase_url="https://project.supabase.co",
        anon_key="anon",
        email="student@example.com",
        password="password",
        api_base="http://127.0.0.1:8000",
    )


def test_resolve_login_config_reads_frontend_style_env() -> None:
    config = resolve_login_config(
        supabase_url=None,
        anon_key=None,
        email=None,
        password=None,
        api_base=None,
        env={
            "VITE_SUPABASE_URL": "https://project.supabase.co",
            "VITE_SUPABASE_ANON_KEY": "anon",
            "SUPABASE_SMOKE_EMAIL": "student@example.com",
            "SUPABASE_SMOKE_PASSWORD": "password",
            "API_BASE_URL": "http://api.test",
        },
    )

    assert config is not None
    assert config.supabase_url == "https://project.supabase.co"
    assert config.anon_key == "anon"
    assert config.email == "student@example.com"
    assert config.password == "password"
    assert config.api_base == "http://api.test"


def test_resolve_login_config_reads_publishable_key_alias() -> None:
    config = resolve_login_config(
        supabase_url=None,
        anon_key=None,
        email=None,
        password=None,
        api_base=None,
        env={
            "VITE_SUPABASE_URL": "https://project.supabase.co",
            "VITE_SUPABASE_PUBLISHABLE_KEY": "publishable",
            "SUPABASE_SMOKE_EMAIL": "student@example.com",
            "SUPABASE_SMOKE_PASSWORD": "password",
        },
    )

    assert config is not None
    assert config.anon_key == "publishable"


def test_resolve_login_config_returns_none_when_required_value_is_missing() -> None:
    assert (
        resolve_login_config(
            supabase_url="https://project.supabase.co",
            anon_key="anon",
            email="student@example.com",
            password=None,
            api_base=None,
            env={},
        )
        is None
    )


def test_build_password_token_url() -> None:
    assert (
        build_password_token_url("https://project.supabase.co/")
        == "https://project.supabase.co/auth/v1/token?grant_type=password"
    )


def test_fetch_access_token_posts_password_grant_without_logging_password() -> None:
    seen_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(200, json={"access_token": "access-token"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    config = SupabaseLoginSmokeConfig(
        supabase_url="https://project.supabase.co",
        anon_key="anon",
        email="student@example.com",
        password="password",
        api_base="http://api.test",
    )

    assert fetch_access_token(client, config) == "access-token"
    assert seen_request is not None
    assert seen_request.url.path == "/auth/v1/token"
    assert seen_request.url.query == b"grant_type=password"
    assert seen_request.headers["apikey"] == "anon"
    assert seen_request.headers["Authorization"] == "Bearer anon"
    assert seen_request.read() == b'{"email":"student@example.com","password":"password"}'


def test_fetch_access_token_raises_when_response_has_no_token() -> None:
    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json={})))
    config = SupabaseLoginSmokeConfig(
        supabase_url="https://project.supabase.co",
        anon_key="anon",
        email="student@example.com",
        password="password",
        api_base="http://api.test",
    )

    with pytest.raises(RuntimeError, match="access_token"):
        fetch_access_token(client, config)


def test_run_login_auth_api_smoke_fetches_token_then_calls_profile_api() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.host == "project.supabase.co":
            return httpx.Response(200, json={"access_token": "access-token"})
        return httpx.Response(
            200,
            json={"department": "software", "grade": 1, "curriculum_year": "2025"},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    config = SupabaseLoginSmokeConfig(
        supabase_url="https://project.supabase.co",
        anon_key="anon",
        email="student@example.com",
        password="password",
        api_base="http://api.test",
    )

    result = run_login_auth_api_smoke(client, config)

    assert [request.url.host for request in requests] == [
        "project.supabase.co",
        "api.test",
        "api.test",
    ]
    assert result["profile_exists"] is True
