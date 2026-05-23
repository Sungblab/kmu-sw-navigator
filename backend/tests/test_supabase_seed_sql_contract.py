from __future__ import annotations

from pathlib import Path

SEED_SQL = Path(__file__).resolve().parents[2] / "supabase" / "seed.sql"


def test_seed_document_chunks_use_unique_conflict_key() -> None:
    sql = SEED_SQL.read_text(encoding="utf-8")

    assert "insert into document_chunks" in sql
    assert "content_hash" in sql
    assert (
        "on conflict (source_type, title, heading_path, chunk_index, content_hash) do nothing"
        in sql
    )


def test_seed_sql_has_no_demo_source_labels() -> None:
    sql = SEED_SQL.read_text(encoding="utf-8").casefold()

    assert "데모용" not in sql
    assert "demo" not in sql
    assert "mock" not in sql
