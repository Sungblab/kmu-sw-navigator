from __future__ import annotations

import argparse
import secrets
import string
from datetime import UTC, datetime
from pathlib import Path

import httpx

from app.core.config import get_settings
from app.scripts.smoke_env import default_repo_root, upsert_env_values


def generate_password(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits + "!_-"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(char.islower() for char in password)
            and any(char.isupper() for char in password)
            and any(char.isdigit() for char in password)
        ):
            return password


def default_smoke_email() -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"codex-smoke+{timestamp}@example.com"


def create_supabase_auth_user(
    client: httpx.Client,
    *,
    supabase_url: str,
    service_role_key: str,
    email: str,
    password: str,
) -> str:
    response = client.post(
        f"{supabase_url.rstrip('/')}/auth/v1/admin/users",
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
        },
        json={
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"source": "kmu-sw-navigator live smoke"},
        },
    )
    response.raise_for_status()
    user_id = response.json().get("id")
    if not isinstance(user_id, str) or not user_id:
        raise RuntimeError("Supabase admin create user response did not include id.")
    return user_id


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a Supabase Auth user for local live smoke tests."
    )
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument(
        "--write-root-env",
        action="store_true",
        help="Write SUPABASE_SMOKE_USER_ID/EMAIL/PASSWORD to ignored root .env.",
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    settings = get_settings()
    if not settings.has_supabase_backend:
        print(
            "Supabase smoke user skipped: SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY are required."
        )
        return 2

    email = (args.email or default_smoke_email()).strip()
    password = args.password or generate_password()

    try:
        with httpx.Client(timeout=args.timeout) as client:
            user_id = create_supabase_auth_user(
                client,
                supabase_url=settings.supabase_url,
                service_role_key=settings.supabase_service_role_key,
                email=email,
                password=password,
            )
    except httpx.HTTPStatusError as exc:
        print(f"Supabase smoke user failed: {exc.response.status_code} {exc.response.text[:300]}")
        return 1
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"Supabase smoke user failed: {exc}")
        return 1

    wrote_env = False
    if args.write_root_env:
        repo_root = Path(args.repo_root).resolve() if args.repo_root else default_repo_root()
        upsert_env_values(
            repo_root / ".env",
            {
                "SUPABASE_SMOKE_USER_ID": user_id,
                "SUPABASE_SMOKE_EMAIL": email,
                "SUPABASE_SMOKE_PASSWORD": password,
            },
        )
        wrote_env = True

    print("Supabase smoke user created")
    print(f"user_id={user_id}")
    print(f"email={email}")
    print(f"password_saved_to_root_env={wrote_env}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
