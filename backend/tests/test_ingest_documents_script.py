from __future__ import annotations

from typing import Any

from app.scripts.ingest_documents import build_embedding_ingest_log_request, upsert_document_chunks


class _FakeTable:
    def __init__(self) -> None:
        self.payloads: list[dict[str, object]] | None = None
        self.on_conflict: str | None = None

    def upsert(
        self,
        payloads: list[dict[str, object]],
        *,
        on_conflict: str,
    ) -> _FakeTable:
        self.payloads = payloads
        self.on_conflict = on_conflict
        return self

    def execute(self) -> None:
        return None


class _FakeClient:
    def __init__(self) -> None:
        self.tables: dict[str, _FakeTable] = {}

    def table(self, name: str) -> _FakeTable:
        table = _FakeTable()
        self.tables[name] = table
        return table


def test_build_embedding_ingest_log_request_summarizes_embedding_run() -> None:
    request = build_embedding_ingest_log_request(
        raw_dir="../data/raw",
        wiki_dir="../data/wiki",
        document_count=4,
        chunk_count=12,
        embedded_count=12,
        model="gemini-embedding-2",
        output_dimensionality=768,
        dry_run=True,
    )

    assert request.feature == "embedding_ingest"
    assert request.input_text == "../data/raw | ../data/wiki"
    assert request.model == "gemini-embedding-2"
    assert request.metadata == {
        "document_count": 4,
        "chunk_count": 12,
        "embedded_count": 12,
        "output_dimensionality": 768,
        "dry_run": True,
    }
    assert "embedded_chunks=12" in (request.output_text or "")


def test_upsert_document_chunks_uses_schema_unique_key() -> None:
    client = _FakeClient()
    payloads: list[dict[str, Any]] = [
        {
            "source_type": "wiki_page",
            "title": "트랙 안내",
            "heading_path": "AI",
            "chunk_index": 0,
            "content_hash": "hash",
        }
    ]

    upsert_document_chunks(client, payloads)

    table = client.tables["document_chunks"]
    assert table.payloads == payloads
    assert table.on_conflict == "source_type,title,heading_path,chunk_index,content_hash"
