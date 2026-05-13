from __future__ import annotations

import argparse
from dataclasses import dataclass
from os import getenv
from pathlib import Path

from app.scripts.check_env import read_env_file


@dataclass(frozen=True)
class LiveSmokeStep:
    name: str
    command: str
    ready: bool
    missing: list[str]


def build_live_smoke_steps(
    repo_root: Path,
    *,
    user_id: str | None,
    email: str | None,
    password: str | None,
) -> list[LiveSmokeStep]:
    backend_env = read_env_file(repo_root / "backend" / ".env")
    frontend_env = read_env_file(repo_root / "frontend" / ".env")
    root_env = read_env_file(repo_root / ".env")

    smoke_user_id = user_id or root_env.get("SUPABASE_SMOKE_USER_ID") or getenv(
        "SUPABASE_SMOKE_USER_ID"
    )
    smoke_email = email or root_env.get("SUPABASE_SMOKE_EMAIL") or getenv("SUPABASE_SMOKE_EMAIL")
    smoke_password = (
        password or root_env.get("SUPABASE_SMOKE_PASSWORD") or getenv("SUPABASE_SMOKE_PASSWORD")
    )

    return [
        _step(
            "Supabase env strict",
            "pnpm env:check:strict",
            missing_env(
                backend_env,
                "SUPABASE_URL",
                "SUPABASE_SERVICE_ROLE_KEY",
                "SUPABASE_JWT_SECRET",
            )
            + missing_env(frontend_env, "VITE_SUPABASE_URL")
            + missing_any_env(
                frontend_env,
                ("VITE_SUPABASE_PUBLISHABLE_KEY", "VITE_SUPABASE_ANON_KEY"),
            ),
        ),
        _step(
            "Supabase DB smoke",
            "pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>",
            missing_value(smoke_user_id, "--user-id or SUPABASE_SMOKE_USER_ID"),
        ),
        _step(
            "Supabase login/API smoke",
            "pnpm supabase:login-smoke -- --email <email> --password <password>",
            missing_env(frontend_env, "VITE_SUPABASE_URL")
            + missing_any_env(
                frontend_env,
                ("VITE_SUPABASE_PUBLISHABLE_KEY", "VITE_SUPABASE_ANON_KEY"),
            )
            + missing_env(backend_env, "SUPABASE_JWT_SECRET")
            + missing_value(smoke_email, "--email or SUPABASE_SMOKE_EMAIL")
            + missing_value(smoke_password, "--password or SUPABASE_SMOKE_PASSWORD"),
        ),
        _step(
            "Supabase LLM usage smoke",
            "pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>",
            missing_env(backend_env, "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
            + missing_value(smoke_user_id, "--user-id or SUPABASE_SMOKE_USER_ID"),
        ),
        _step(
            "Gemini smoke",
            "pnpm gemini:smoke",
            missing_env(backend_env, "GEMINI_API_KEY"),
        ),
        _step(
            "Gemini answer smoke",
            "pnpm gemini:answer-smoke",
            missing_env(backend_env, "GEMINI_API_KEY"),
        ),
        _step(
            "Gemini grounding smoke",
            "pnpm gemini:grounding-smoke",
            missing_env(backend_env, "GEMINI_API_KEY"),
        ),
        _step(
            "Google Calendar event smoke",
            "pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>",
            missing_env(
                backend_env,
                "SUPABASE_URL",
                "SUPABASE_SERVICE_ROLE_KEY",
                "GOOGLE_OAUTH_CLIENT_SECRET",
            )
            + missing_value(smoke_user_id, "--user-id or SUPABASE_SMOKE_USER_ID")
            + ["stored Google OAuth token for this user"],
        ),
        _step(
            "Embedding ingest",
            "pnpm rag:ingest:embeddings",
            missing_env(backend_env, "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "GEMINI_API_KEY"),
        ),
    ]


def missing_env(values: dict[str, str], *keys: str) -> list[str]:
    return [key for key in keys if not values.get(key)]


def missing_any_env(values: dict[str, str], keys: tuple[str, ...]) -> list[str]:
    return [] if any(values.get(key) for key in keys) else [" or ".join(keys)]


def missing_value(value: str | None, label: str) -> list[str]:
    return [] if value else [label]


def _step(name: str, command: str, missing: list[str]) -> LiveSmokeStep:
    return LiveSmokeStep(name=name, command=command, ready=not missing, missing=missing)


def format_live_smoke_plan(steps: list[LiveSmokeStep]) -> list[str]:
    lines = ["Live smoke plan", ""]
    for index, step in enumerate(steps, 1):
        status = "ready" if step.ready else "blocked"
        lines.append(f"{index}. [{status}] {step.name}")
        lines.append(f"   command: {step.command}")
        if step.missing:
            lines.append(f"   missing: {', '.join(step.missing)}")
        else:
            lines.append("   missing: none")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the live smoke checklist without secrets.")
    parser.add_argument(
        "--repo-root",
        default=str(Path.cwd().parent if Path.cwd().name == "backend" else Path.cwd()),
    )
    parser.add_argument("--user-id", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    steps = build_live_smoke_steps(
        Path(args.repo_root).resolve(),
        user_id=args.user_id,
        email=args.email,
        password=args.password,
    )
    print("\n".join(format_live_smoke_plan(steps)))
    return 0 if all(step.ready for step in steps) else 2


if __name__ == "__main__":
    raise SystemExit(main())
