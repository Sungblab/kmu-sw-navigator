from __future__ import annotations

import argparse
from os import getenv
from typing import Any

import httpx


def resolve_access_token(cli_token: str | None, env_token: str | None = None) -> str | None:
    token = (cli_token or env_token or getenv("SUPABASE_SMOKE_ACCESS_TOKEN") or "").strip()
    return token or None


def normalize_api_base(api_base: str) -> str:
    return api_base.rstrip("/")


def build_profile_smoke_payload() -> dict[str, Any]:
    return {
        "department": "software",
        "grade": 1,
        "curriculum_year": "2025",
    }


def run_auth_api_smoke(client: httpx.Client, api_base: str, access_token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    # Bearer token smoke는 인증된 user_id로 profile upsert/read가 이어지는지 확인한다.
    write_response = client.post(
        f"{normalize_api_base(api_base)}/api/profile",
        json=build_profile_smoke_payload(),
        headers=headers,
    )
    write_response.raise_for_status()

    read_response = client.get(
        f"{normalize_api_base(api_base)}/api/profile",
        headers=headers,
    )
    read_response.raise_for_status()
    read_payload = read_response.json()

    return {
        "profile_department": read_payload.get("department"),
        "profile_grade": read_payload.get("grade"),
        "profile_exists": read_payload.get("exists") is not False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test a Supabase access token against the local FastAPI API."
    )
    parser.add_argument(
        "--api-base",
        default=getenv("API_BASE_URL", "http://127.0.0.1:8000"),
        help="FastAPI base URL. Defaults to API_BASE_URL or http://127.0.0.1:8000.",
    )
    parser.add_argument(
        "--access-token",
        default=None,
        help=(
            "Supabase Auth access token from a real login session. "
            "Can also be provided through SUPABASE_SMOKE_ACCESS_TOKEN."
        ),
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    access_token = resolve_access_token(args.access_token)
    if access_token is None:
        print(
            "Auth API smoke skipped: provide a Supabase access token with "
            "--access-token or SUPABASE_SMOKE_ACCESS_TOKEN."
        )
        return 2

    try:
        with httpx.Client(timeout=args.timeout) as client:
            result = run_auth_api_smoke(client, args.api_base, access_token)
    except httpx.HTTPStatusError as exc:
        print(
            "Auth API smoke failed: "
            f"{exc.response.status_code} {exc.response.text[:300]}"
        )
        return 1
    except httpx.HTTPError as exc:
        print(f"Auth API smoke failed: {exc}")
        return 1

    print("Auth API smoke completed")
    print(f"api_base={normalize_api_base(args.api_base)}")
    print(f"profile_exists={result['profile_exists']}")
    print(f"profile_department={result['profile_department']}")
    print(f"profile_grade={result['profile_grade']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
