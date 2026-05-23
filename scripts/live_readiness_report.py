from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any
from urllib import request
from urllib.error import URLError

try:
    from scripts.build_supabase_sql_bundle import build_sql_bundle, validate_sql_bundle
except ModuleNotFoundError:
    from build_supabase_sql_bundle import build_sql_bundle, validate_sql_bundle


def add_backend_to_path(repo_root: Path) -> None:
    backend_path = str(repo_root / "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)


def build_readiness_report(
    *,
    env_missing_core: bool,
    bundle_errors: list[str],
    schema_ready: bool | None,
    missing_schema_items: list[str],
    api_ready: bool | None,
    include_seed: bool,
    api_base: str,
) -> tuple[list[str], int]:
    lines = ["Live readiness report", ""]
    exit_code = 0

    if env_missing_core:
        lines.append("- Core env: blocker")
        lines.append("  action: run pnpm env:check and fill only the missing variable names.")
        exit_code = max(exit_code, 2)
    else:
        lines.append("- Core env: ready")

    if bundle_errors:
        lines.append("- SQL bundle: blocker")
        for error in bundle_errors:
            lines.append(f"  - {error}")
        exit_code = max(exit_code, 2)
    else:
        seed_label = "schema+seed" if include_seed else "schema-only"
        lines.append(f"- SQL bundle: ready ({seed_label})")

    if schema_ready is None:
        lines.append("- Supabase schema: skipped")
        lines.append("  reason: core Supabase env is missing.")
    elif schema_ready:
        lines.append("- Supabase schema: ready")
    else:
        lines.append("- Supabase schema: blocker")
        for item in missing_schema_items:
            lines.append(f"  - {item}")
        exit_code = max(exit_code, 1)

    if schema_ready is not True or api_ready is None:
        lines.append("- API health: skipped")
        lines.append("  reason: Supabase schema or core env is not ready.")
    elif api_ready:
        lines.append(f"- API health: ready ({api_base}/health)")
    else:
        lines.append(f"- API health: blocker ({api_base}/health)")
        lines.append("  action: start FastAPI on the same port before live smoke.")
        exit_code = max(exit_code, 1)

    lines.extend(
        [
            "",
            "Next actions:",
        ]
    )
    if bundle_errors:
        lines.append("1. Fix supabase/schema.sql or supabase/seed.sql until bundle validation passes.")
    elif schema_ready is False:
        bundle_command = "pnpm supabase:sql-bundle -- --include-seed" if include_seed else "pnpm supabase:sql-bundle"
        lines.append(f"1. {bundle_command}")
        lines.append("2. Open supabase/live-schema-bundle.sql and paste it into the Supabase SQL Editor.")
        lines.append("3. Run the SQL in project abbwnqwvvtxrizutswws.")
        lines.append(f"4. pnpm live:smoke-run --api-base {api_base}")
    elif api_ready is False:
        lines.append("1. cd backend")
        lines.append("2. uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8001")
        lines.append(f"3. pnpm live:smoke-run --api-base {api_base}")
    elif schema_ready:
        lines.append(f"1. pnpm live:smoke-run --api-base {api_base}")
    else:
        lines.append("1. pnpm env:check")

    return lines, exit_code


def collect_missing_schema_items(schema_items: list[Any]) -> list[str]:
    return [
        f"{item.kind}: {item.name}"
        for item in schema_items
        if not item.ready
    ]


def check_api_health(api_base: str) -> bool:
    try:
        response = request.urlopen(f"{api_base.rstrip('/')}/health", timeout=2)
    except (OSError, URLError):
        return False
    return getattr(response, "status", 200) == 200


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print live SaaS readiness without exposing secret values."
    )
    parser.add_argument("--repo-root", default=str(Path.cwd()))
    parser.add_argument("--api-base", default="http://127.0.0.1:8001")
    parser.add_argument(
        "--include-seed",
        action="store_true",
        help="Validate the schema+seed SQL bundle expected for first live apply.",
    )
    normalized_argv = sys.argv[1:] if argv is None else argv
    normalized_argv = [arg for arg in normalized_argv if arg != "--"]
    return parser.parse_args(normalized_argv)


def main() -> int:
    args = parse_args()

    repo_root = Path(args.repo_root).resolve()
    add_backend_to_path(repo_root)

    from app.core.config import get_settings
    from app.db.supabase_client import get_supabase_client
    from app.scripts.check_env import build_report
    from app.scripts.supabase_schema_check import check_supabase_schema

    env_lines, env_missing_core = build_report(repo_root)
    bundle = build_sql_bundle(repo_root, include_seed=args.include_seed)
    bundle_errors = validate_sql_bundle(bundle, include_seed=args.include_seed)

    schema_ready: bool | None = None
    missing_schema_items: list[str] = []
    api_ready: bool | None = None
    settings = get_settings()
    if settings.has_supabase_backend and not env_missing_core:
        schema_items = check_supabase_schema(get_supabase_client())
        missing_schema_items = collect_missing_schema_items(schema_items)
        schema_ready = not missing_schema_items
        if schema_ready:
            api_ready = check_api_health(args.api_base)

    lines, exit_code = build_readiness_report(
        env_missing_core=env_missing_core,
        bundle_errors=bundle_errors,
        schema_ready=schema_ready,
        missing_schema_items=missing_schema_items,
        api_ready=api_ready,
        include_seed=args.include_seed,
        api_base=args.api_base,
    )

    print("\n".join(lines))
    print("")
    print("Environment detail")
    print("\n".join(env_lines))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
