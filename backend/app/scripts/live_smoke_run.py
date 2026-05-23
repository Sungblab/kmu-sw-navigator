from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from urllib import request
from urllib.error import URLError

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.scripts.supabase_schema_check import (
    SchemaCheckItem,
    check_supabase_schema,
    format_schema_report,
)


@dataclass(frozen=True)
class SmokeCommand:
    name: str
    args: list[str]
    required: bool = True
    failure_category: str = "code"
    next_action: str = "Inspect the command output above and rerun the focused smoke."


@dataclass(frozen=True)
class SmokeCommandResult:
    name: str
    returncode: int
    failure_category: str = "code"
    next_action: str = "Inspect the command output above and rerun the focused smoke."

    @property
    def passed(self) -> bool:
        return self.returncode == 0


def build_smoke_commands(*, api_base: str, include_google: bool) -> list[SmokeCommand]:
    commands = [
        SmokeCommand(
            "Supabase DB smoke",
            ["-m", "app.scripts.supabase_smoke"],
            failure_category="schema",
            next_action="Run pnpm supabase:schema-check and confirm the smoke user UUID exists.",
        ),
        SmokeCommand(
            "Supabase LLM usage smoke",
            ["-m", "app.scripts.llm_usage_smoke"],
            failure_category="schema",
            next_action="Check llm_usage_logs schema and rerun pnpm supabase:llm-smoke.",
        ),
        SmokeCommand(
            "Supabase login/API smoke",
            ["-m", "app.scripts.supabase_login_smoke", "--api-base", api_base],
            failure_category="auth",
            next_action=(
                "Confirm the FastAPI server is running and the Supabase Auth "
                "email/password are valid."
            ),
        ),
        SmokeCommand(
            "Gemini smoke",
            ["-m", "app.scripts.gemini_smoke"],
            failure_category="env",
            next_action="Check GEMINI_API_KEY and Gemini model availability.",
        ),
        SmokeCommand(
            "Gemini answer smoke",
            ["-m", "app.scripts.gemini_answer_smoke"],
            failure_category="env",
            next_action="Check GEMINI_API_KEY and answer model availability.",
        ),
        SmokeCommand(
            "Gemini grounding smoke",
            ["-m", "app.scripts.gemini_grounding_smoke"],
            failure_category="env",
            next_action="Check GEMINI_API_KEY and Google Search grounding availability.",
        ),
        SmokeCommand(
            "Embedding ingest",
            [
                "-m",
                "app.scripts.ingest_documents",
                "--raw-dir",
                "../data/raw",
                "--wiki-dir",
                "../data/wiki",
                "--with-embeddings",
            ],
            failure_category="schema",
            next_action=(
                "Check document_chunks schema, Gemini embedding config, and rerun "
                "pnpm rag:ingest:embeddings."
            ),
        ),
    ]
    if include_google:
        commands.append(
            SmokeCommand(
                "Google Calendar event smoke",
                ["-m", "app.scripts.calendar_export_smoke"],
                failure_category="auth",
                next_action=(
                    "Connect Google Calendar for the smoke user, then rerun "
                    "pnpm google:calendar-smoke."
                ),
            )
        )
    return commands


def run_smoke_commands(commands: list[SmokeCommand]) -> list[SmokeCommandResult]:
    results: list[SmokeCommandResult] = []
    for command in commands:
        print("")
        print(f"== {command.name} ==")
        completed = subprocess.run([sys.executable, *command.args], check=False)
        results.append(
            SmokeCommandResult(
                name=command.name,
                returncode=completed.returncode,
                failure_category=command.failure_category,
                next_action=command.next_action,
            )
        )
        if command.required and completed.returncode != 0:
            break
    return results


def print_result_summary(results: list[SmokeCommandResult]) -> None:
    print("")
    print("Live smoke run summary")
    for result in results:
        status = "passed" if result.passed else f"failed:{result.returncode}"
        print(f"- [{status}] {result.name}")


def print_failure_guidance(results: list[SmokeCommandResult]) -> None:
    failed = next((result for result in results if not result.passed), None)
    if failed is None:
        return
    print("")
    print(f"Failure classification: {failed.failure_category}")
    print(f"Next action: {failed.next_action}")


def print_schema_blocker_next_actions() -> None:
    print("")
    print("Live smoke run stopped: Supabase schema is not ready.")
    print("")
    print("Next actions:")
    print("1. pnpm supabase:sql-bundle -- --include-seed")
    print("2. Open supabase/live-schema-bundle.sql and paste it into the Supabase SQL Editor.")
    print("3. Run the SQL in project abbwnqwvvtxrizutswws.")
    print("4. Rerun pnpm live:smoke-run --api-base http://127.0.0.1:8001")


def check_schema_with_retries(
    client: object,
    *,
    retries: int = 3,
    delay_seconds: float = 2.0,
) -> list[SchemaCheckItem]:
    attempts = max(retries, 1)
    last_items: list[SchemaCheckItem] = []
    for attempt in range(1, attempts + 1):
        last_items = check_supabase_schema(client)
        if all(item.ready for item in last_items):
            return last_items
        if attempt < attempts:
            print("")
            print(
                "Supabase schema is not visible yet. "
                f"Retrying schema check ({attempt + 1}/{attempts})..."
            )
            time.sleep(delay_seconds)
    return last_items


def check_api_health(api_base: str) -> bool:
    try:
        response = request.urlopen(f"{api_base.rstrip('/')}/health", timeout=2)
    except (OSError, URLError):
        return False
    return getattr(response, "status", 200) == 200


def print_api_health_blocker(api_base: str) -> None:
    print("")
    print(f"FastAPI server is not reachable: {api_base}/health")
    print("")
    print("Next actions:")
    print("1. Start a live-check backend on the same port used by --api-base.")
    print("2. cd backend")
    print("3. uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8001")
    print("4. Rerun pnpm live:smoke-run --api-base http://127.0.0.1:8001")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run live Supabase/Gemini smoke checks in dependency order."
    )
    parser.add_argument("--api-base", default="http://127.0.0.1:8001")
    parser.add_argument(
        "--include-google",
        action="store_true",
        help="Also run Google Calendar event smoke. Requires OAuth token setup.",
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.has_supabase_backend:
        print("Live smoke run skipped: SUPABASE_URL and SERVICE_ROLE key are required.")
        return 2

    schema_items = check_schema_with_retries(get_supabase_client())
    print("\n".join(format_schema_report(schema_items)))
    if not all(item.ready for item in schema_items):
        print_schema_blocker_next_actions()
        return 1

    if not check_api_health(args.api_base):
        print_api_health_blocker(args.api_base)
        return 1

    results = run_smoke_commands(
        build_smoke_commands(api_base=args.api_base, include_google=args.include_google)
    )
    print_result_summary(results)
    print_failure_guidance(results)
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
