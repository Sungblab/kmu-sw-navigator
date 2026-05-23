from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from typing import Any

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client

REQUIRED_TABLES = (
    "profiles",
    "raw_documents",
    "wiki_pages",
    "wiki_logs",
    "document_chunks",
    "assignments",
    "chat_sessions",
    "chat_messages",
    "chat_logs",
    "llm_usage_logs",
    "user_memories",
    "memory_events",
    "google_oauth_tokens",
)

REQUIRED_FUNCTION_ARGS: dict[str, dict[str, Any]] = {
    "search_document_chunks_text": {"search_query": "schema smoke", "match_count": 1},
    "match_document_chunks": {
        "query_embedding": [0.0] * 768,
        "match_count": 1,
        "match_threshold": 0.0,
        "filter_source_type": None,
    },
}


@dataclass(frozen=True)
class SchemaCheckItem:
    kind: str
    name: str
    ready: bool
    error: str | None = None


def check_supabase_schema(client: Any) -> list[SchemaCheckItem]:
    items: list[SchemaCheckItem] = []
    for table_name in REQUIRED_TABLES:
        try:
            client.table(table_name).select("*").limit(1).execute()
        except Exception as exc:
            items.append(
                SchemaCheckItem(kind="table", name=table_name, ready=False, error=str(exc)[:180])
            )
        else:
            items.append(SchemaCheckItem(kind="table", name=table_name, ready=True))

    for function_name, args in REQUIRED_FUNCTION_ARGS.items():
        try:
            client.rpc(function_name, args).execute()
        except Exception as exc:
            items.append(
                SchemaCheckItem(
                    kind="function",
                    name=function_name,
                    ready=False,
                    error=str(exc)[:180],
                )
            )
        else:
            items.append(SchemaCheckItem(kind="function", name=function_name, ready=True))
    return items


def check_supabase_schema_with_retries(
    client: Any,
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


def format_schema_report(items: list[SchemaCheckItem]) -> list[str]:
    lines = ["Supabase schema check", ""]
    for item in items:
        status = "ready" if item.ready else "missing"
        lines.append(f"- [{status}] {item.kind}: {item.name}")
        if item.error:
            lines.append(f"  error: {item.error}")
    missing = [item for item in items if not item.ready]
    lines.append("")
    if missing:
        lines.append("Required action: apply supabase/schema.sql in the Supabase SQL Editor.")
    else:
        lines.append("Required action: none")
    return lines


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether the live Supabase project has required tables/functions."
    )
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-delay", type=float, default=2.0)
    normalized_argv = sys.argv[1:] if argv is None else argv
    if normalized_argv[:1] == ["--"]:
        normalized_argv = normalized_argv[1:]
    return parser.parse_args(normalized_argv)


def main() -> int:
    args = parse_args()

    settings = get_settings()
    if not settings.has_supabase_backend:
        print("Supabase schema check skipped: SUPABASE_URL and SERVICE_ROLE key are required.")
        return 2

    items = check_supabase_schema_with_retries(
        get_supabase_client(),
        retries=args.retries,
        delay_seconds=args.retry_delay,
    )
    print("\n".join(format_schema_report(items)))
    return 0 if all(item.ready for item in items) else 1


if __name__ == "__main__":
    raise SystemExit(main())
