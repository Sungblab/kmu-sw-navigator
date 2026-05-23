from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_supabase_sql_bundle import build_sql_bundle, validate_sql_bundle


def read_env_values(path: Path) -> dict[str, str]:
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


def resolve_project_ref(repo_root: Path, explicit_ref: str | None = None) -> str | None:
    if explicit_ref:
        return explicit_ref
    backend_env = read_env_values(repo_root / "backend" / ".env")
    supabase_url = backend_env.get("SUPABASE_URL", "")
    match = re.match(r"https://([a-z0-9-]+)\.supabase\.co/?", supabase_url)
    if match:
        return match.group(1)
    return None


def build_dashboard_sql_editor_url(project_ref: str | None) -> str:
    if not project_ref:
        return "https://supabase.com/dashboard/projects"
    return f"https://supabase.com/dashboard/project/{project_ref}/sql/new"


def copy_to_clipboard(text: str) -> None:
    # Windows 기본 도구만 사용해 추가 패키지 없이 SQL Editor 붙여넣기 흐름을 만든다.
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Set-Clipboard -Value ([Console]::In.ReadToEnd())",
        ],
        input=text,
        text=True,
        check=True,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Supabase SQL bundle and copy it to the clipboard for SQL Editor."
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Copy only supabase/schema.sql without seed rows.",
    )
    parser.add_argument(
        "--project-ref",
        help="Supabase project ref for the Dashboard SQL Editor URL.",
    )
    parser.add_argument(
        "--api-base",
        default="http://127.0.0.1:8001",
        help="FastAPI base URL to show in the follow-up live smoke command.",
    )
    normalized_argv = sys.argv[1:] if argv is None else argv
    if normalized_argv[:1] == ["--"]:
        normalized_argv = normalized_argv[1:]
    return parser.parse_args(normalized_argv)


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    include_seed = not args.schema_only
    bundle = build_sql_bundle(repo_root, include_seed=include_seed)
    errors = validate_sql_bundle(bundle, include_seed=include_seed)
    if errors:
        print("Supabase SQL bundle validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    copy_to_clipboard(bundle)
    dashboard_url = build_dashboard_sql_editor_url(resolve_project_ref(repo_root, args.project_ref))
    seed_label = "schema+seed" if include_seed else "schema only"
    print(f"Copied Supabase SQL bundle to clipboard ({seed_label}, {len(bundle)} characters).")
    print(f"Open SQL Editor: {dashboard_url}")
    print("")
    print("After running the SQL, verify with:")
    print("pnpm supabase:schema-check")
    print(f"pnpm live:smoke-run --api-base {args.api_base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
