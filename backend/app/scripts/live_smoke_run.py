from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.scripts.supabase_schema_check import check_supabase_schema, format_schema_report


@dataclass(frozen=True)
class SmokeCommand:
    name: str
    args: list[str]
    required: bool = True


@dataclass(frozen=True)
class SmokeCommandResult:
    name: str
    returncode: int

    @property
    def passed(self) -> bool:
        return self.returncode == 0


def build_smoke_commands(*, api_base: str, include_google: bool) -> list[SmokeCommand]:
    commands = [
        SmokeCommand("Supabase DB smoke", ["-m", "app.scripts.supabase_smoke"]),
        SmokeCommand("Supabase LLM usage smoke", ["-m", "app.scripts.llm_usage_smoke"]),
        SmokeCommand(
            "Supabase login/API smoke",
            ["-m", "app.scripts.supabase_login_smoke", "--api-base", api_base],
        ),
        SmokeCommand("Gemini smoke", ["-m", "app.scripts.gemini_smoke"]),
        SmokeCommand("Gemini answer smoke", ["-m", "app.scripts.gemini_answer_smoke"]),
        SmokeCommand("Gemini grounding smoke", ["-m", "app.scripts.gemini_grounding_smoke"]),
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
        ),
    ]
    if include_google:
        commands.append(
            SmokeCommand("Google Calendar event smoke", ["-m", "app.scripts.calendar_export_smoke"])
        )
    return commands


def run_smoke_commands(commands: list[SmokeCommand]) -> list[SmokeCommandResult]:
    results: list[SmokeCommandResult] = []
    for command in commands:
        print("")
        print(f"== {command.name} ==")
        completed = subprocess.run([sys.executable, *command.args], check=False)
        results.append(SmokeCommandResult(name=command.name, returncode=completed.returncode))
        if command.required and completed.returncode != 0:
            break
    return results


def print_result_summary(results: list[SmokeCommandResult]) -> None:
    print("")
    print("Live smoke run summary")
    for result in results:
        status = "passed" if result.passed else f"failed:{result.returncode}"
        print(f"- [{status}] {result.name}")


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

    schema_items = check_supabase_schema(get_supabase_client())
    print("\n".join(format_schema_report(schema_items)))
    if not all(item.ready for item in schema_items):
        print("")
        print("Live smoke run stopped: Supabase schema is not ready.")
        return 1

    results = run_smoke_commands(
        build_smoke_commands(api_base=args.api_base, include_google=args.include_google)
    )
    print_result_summary(results)
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
