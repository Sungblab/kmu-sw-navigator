from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client

REQUIRED_TABLES = (
    "profiles",
    "user_memories",
    "memory_events",
    "chat_sessions",
    "chat_messages",
    "assignments",
    "google_oauth_tokens",
    "llm_usage_logs",
    "document_chunks",
)

REQUIRED_FUNCTION_ARGS: dict[str, dict[str, Any]] = {
    "search_document_chunks_text": {"query_text": "schema smoke", "match_count": 1},
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether the live Supabase project has required tables/functions."
    )
    parser.parse_args()

    settings = get_settings()
    if not settings.has_supabase_backend:
        print("Supabase schema check skipped: SUPABASE_URL and SERVICE_ROLE key are required.")
        return 2

    items = check_supabase_schema(get_supabase_client())
    print("\n".join(format_schema_report(items)))
    return 0 if all(item.ready for item in items) else 1


if __name__ == "__main__":
    raise SystemExit(main())
