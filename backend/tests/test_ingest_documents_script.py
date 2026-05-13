from __future__ import annotations

from app.scripts.ingest_documents import build_embedding_ingest_log_request


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
