from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EnvCheck:
    label: str
    file_path: Path
    required_keys: tuple[str, ...]
    purpose: str
    alternative_key_groups: tuple[tuple[str, ...], ...] = ()


ENV_CHECKS = (
    EnvCheck(
        label="Backend Supabase Direct",
        file_path=Path("backend/.env"),
        required_keys=("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"),
        purpose="FastAPI persistence through the Supabase service-role client",
    ),
    EnvCheck(
        label="Backend Supabase JWT",
        file_path=Path("backend/.env"),
        required_keys=("SUPABASE_JWT_SECRET",),
        purpose="Verify Supabase Auth access tokens",
    ),
    EnvCheck(
        label="Frontend Supabase Framework",
        file_path=Path("frontend/.env"),
        required_keys=("VITE_SUPABASE_URL",),
        alternative_key_groups=(("VITE_SUPABASE_PUBLISHABLE_KEY", "VITE_SUPABASE_ANON_KEY"),),
        purpose="Create Supabase login sessions in React/Vite",
    ),
    EnvCheck(
        label="Gemini",
        file_path=Path("backend/.env"),
        required_keys=("GEMINI_API_KEY",),
        purpose="Live answer generation, schedule parsing, embeddings, and grounding",
    ),
    EnvCheck(
        label="Google Calendar OAuth",
        file_path=Path("backend/.env"),
        required_keys=("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET"),
        purpose="Build Calendar consent URLs and exchange OAuth tokens",
    ),
)


def read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def missing_keys(env_values: dict[str, str], required_keys: tuple[str, ...]) -> list[str]:
    return [key for key in required_keys if not env_values.get(key)]


def missing_alternative_key_groups(
    env_values: dict[str, str],
    alternative_key_groups: tuple[tuple[str, ...], ...],
) -> list[str]:
    return [
        " or ".join(group)
        for group in alternative_key_groups
        if not any(env_values.get(key) for key in group)
    ]


def build_report(repo_root: Path) -> tuple[list[str], bool]:
    env_cache: dict[Path, dict[str, str]] = {}
    lines = ["Environment check", ""]
    has_missing_core = False

    for check in ENV_CHECKS:
        absolute_path = repo_root / check.file_path
        env_values = env_cache.setdefault(absolute_path, read_env_file(absolute_path))
        missing = missing_keys(env_values, check.required_keys) + missing_alternative_key_groups(
            env_values,
            check.alternative_key_groups,
        )
        status = "ready" if not missing else "missing"
        if check.label.startswith(("Backend Supabase", "Frontend Supabase")) and missing:
            has_missing_core = True

        lines.append(f"- {check.label}: {status}")
        lines.append(f"  file: {check.file_path.as_posix()}")
        lines.append(f"  purpose: {check.purpose}")
        if missing:
            lines.append(f"  missing: {', '.join(missing)}")
        else:
            lines.append("  missing: none")

    lines.extend(
        [
            "",
            "Use Supabase Direct values in backend/.env for the FastAPI server.",
            "Use Supabase Framework/client values in frontend/.env for React login.",
            "Never put SUPABASE_SERVICE_ROLE_KEY in frontend/.env.",
        ]
    )
    return lines, has_missing_core


def main() -> int:
    parser = argparse.ArgumentParser(description="Check required local environment variables.")
    parser.add_argument(
        "--repo-root",
        default=str(Path.cwd().parent if Path.cwd().name == "backend" else Path.cwd()),
        help="Repository root path. Defaults to parent when run from backend/.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 2 when core Supabase backend/frontend variables are missing.",
    )
    args = parser.parse_args()

    lines, has_missing_core = build_report(Path(args.repo_root).resolve())
    print("\n".join(lines))
    if args.strict and has_missing_core:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
