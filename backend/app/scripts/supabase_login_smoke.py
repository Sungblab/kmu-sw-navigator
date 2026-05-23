from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import dataclass
from os import environ

import httpx

from app.scripts.auth_api_smoke import normalize_api_base, run_auth_api_smoke
from app.scripts.check_env import read_env_file
from app.scripts.smoke_env import default_repo_root, read_root_smoke_env


@dataclass(frozen=True)
class SupabaseLoginSmokeConfig:
    supabase_url: str
    anon_key: str
    email: str
    password: str
    api_base: str


def resolve_login_config(
    *,
    supabase_url: str | None,
    anon_key: str | None,
    email: str | None,
    password: str | None,
    api_base: str | None,
    env: Mapping[str, str] = environ,
) -> SupabaseLoginSmokeConfig | None:
    if env is environ:
        repo_root = default_repo_root()
        root_env = read_root_smoke_env(repo_root)
        frontend_env = read_env_file(repo_root / "frontend" / ".env")
    else:
        root_env = {}
        frontend_env = {}
    resolved_supabase_url = (
        supabase_url
        or env.get("VITE_SUPABASE_URL")
        or env.get("SUPABASE_URL")
        or frontend_env.get("VITE_SUPABASE_URL")
        or root_env.get("SUPABASE_URL")
        or ""
    ).strip()
    resolved_anon_key = (
        anon_key
        or env.get("VITE_SUPABASE_PUBLISHABLE_KEY")
        or env.get("VITE_SUPABASE_ANON_KEY")
        or env.get("SUPABASE_ANON_KEY")
        or frontend_env.get("VITE_SUPABASE_PUBLISHABLE_KEY")
        or frontend_env.get("VITE_SUPABASE_ANON_KEY")
        or root_env.get("SUPABASE_ANON_KEY")
        or ""
    ).strip()
    resolved_email = (
        email or env.get("SUPABASE_SMOKE_EMAIL") or root_env.get("SUPABASE_SMOKE_EMAIL") or ""
    ).strip()
    resolved_password = (
        password
        or env.get("SUPABASE_SMOKE_PASSWORD")
        or root_env.get("SUPABASE_SMOKE_PASSWORD")
        or ""
    ).strip()
    resolved_api_base = (
        api_base
        or env.get("API_BASE_URL")
        or root_env.get("API_BASE_URL")
        or "http://127.0.0.1:8000"
    ).strip()

    if not (
        resolved_supabase_url and resolved_anon_key and resolved_email and resolved_password
    ):
        return None

    return SupabaseLoginSmokeConfig(
        supabase_url=resolved_supabase_url.rstrip("/"),
        anon_key=resolved_anon_key,
        email=resolved_email,
        password=resolved_password,
        api_base=normalize_api_base(resolved_api_base),
    )


def build_password_token_url(supabase_url: str) -> str:
    return f"{supabase_url.rstrip('/')}/auth/v1/token?grant_type=password"


def fetch_access_token(client: httpx.Client, config: SupabaseLoginSmokeConfig) -> str:
    # Supabase password grant로 실제 사용자 session token을 받아 backend JWT boundary를 검증한다.
    response = client.post(
        build_password_token_url(config.supabase_url),
        headers={
            "apikey": config.anon_key,
            "Authorization": f"Bearer {config.anon_key}",
        },
        json={"email": config.email, "password": config.password},
    )
    response.raise_for_status()
    access_token = response.json().get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise RuntimeError("Supabase login response did not include access_token.")
    return access_token


def run_login_auth_api_smoke(
    client: httpx.Client,
    config: SupabaseLoginSmokeConfig,
) -> dict[str, object]:
    access_token = fetch_access_token(client, config)
    return run_auth_api_smoke(client, config.api_base, access_token)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Log in through Supabase Auth, then smoke test the local FastAPI "
            "Bearer-token API boundary."
        )
    )
    parser.add_argument("--supabase-url", default=None)
    parser.add_argument("--anon-key", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    config = resolve_login_config(
        supabase_url=args.supabase_url,
        anon_key=args.anon_key,
        email=args.email,
        password=args.password,
        api_base=args.api_base,
    )
    if config is None:
        print(
            "Supabase login smoke skipped: provide Supabase URL, anon key, "
            "SUPABASE_SMOKE_EMAIL, and SUPABASE_SMOKE_PASSWORD."
        )
        return 2

    try:
        with httpx.Client(timeout=args.timeout) as client:
            result = run_login_auth_api_smoke(client, config)
    except httpx.HTTPStatusError as exc:
        print(
            "Supabase login smoke failed: "
            f"{exc.response.status_code} {exc.response.text[:300]}"
        )
        return 1
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"Supabase login smoke failed: {exc}")
        return 1

    print("Supabase login smoke completed")
    print(f"api_base={config.api_base}")
    print(f"profile_exists={result['profile_exists']}")
    print(f"profile_department={result['profile_department']}")
    print(f"profile_grade={result['profile_grade']}")
    print(f"onboarding_memory_status={result['onboarding_memory_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
