from pathlib import Path

from app.scripts.supabase_schema_check import REQUIRED_TABLES

SCHEMA_SQL = Path(__file__).resolve().parents[2] / "supabase" / "schema.sql"


def test_text_search_rpc_argument_matches_backend_adapter() -> None:
    sql = SCHEMA_SQL.read_text(encoding="utf-8")

    assert "create or replace function search_document_chunks_text" in sql
    assert "search_query text" in sql
    assert "query_text text" not in sql


def test_schema_sql_contains_all_live_smoke_tables_and_functions() -> None:
    sql = SCHEMA_SQL.read_text(encoding="utf-8")

    for table_name in (
        "profiles",
        "user_memories",
        "memory_events",
        "chat_sessions",
        "chat_messages",
        "assignments",
        "google_oauth_tokens",
        "llm_usage_logs",
        "document_chunks",
    ):
        assert f"create table if not exists {table_name}" in sql

    assert "create or replace function search_document_chunks_text" in sql
    assert "create or replace function match_document_chunks" in sql
    assert "create unique index if not exists document_chunks_unique_chunk_idx" in sql


def test_schema_sql_requests_postgrest_schema_cache_reload() -> None:
    sql = SCHEMA_SQL.read_text(encoding="utf-8").casefold()

    assert "notify pgrst, 'reload schema'" in sql


def test_schema_check_covers_every_schema_table() -> None:
    sql = SCHEMA_SQL.read_text(encoding="utf-8")
    schema_tables = {
        line.removeprefix("create table if not exists ").split(" ", 1)[0]
        for line in sql.splitlines()
        if line.startswith("create table if not exists ")
    }

    assert schema_tables <= set(REQUIRED_TABLES)
