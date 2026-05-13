import pytest

from app.services.document_ingest import IngestDocument, build_document_chunk_payloads
from app.services.embedding_service import (
    DeterministicEmbeddingService,
    attach_embeddings_to_payloads,
    validate_embeddings,
)


def test_deterministic_embedding_service_returns_expected_dimension() -> None:
    service = DeterministicEmbeddingService(output_dimensionality=8)

    embeddings = service.embed_texts(["AI 트랙", "백엔드 프로젝트"])

    assert len(embeddings) == 2
    assert {len(embedding) for embedding in embeddings} == {8}
    assert embeddings[0] == service.embed_texts(["AI 트랙"])[0]


def test_validate_embeddings_rejects_dimension_mismatch() -> None:
    with pytest.raises(ValueError, match="dimension mismatch"):
        validate_embeddings([[0.1, 0.2]], expected_dim=3)


def test_attach_embeddings_to_payloads_preserves_payload_metadata(tmp_path) -> None:
    payloads = build_document_chunk_payloads(
        [
            IngestDocument(
                source_type="wiki_page",
                slug="track",
                title="트랙 안내",
                source="Mini LLM Wiki",
                category="track",
                content="# 트랙 안내\n\nAI 트랙은 Python을 먼저 본다.",
                path=tmp_path / "track.md",
            )
        ],
        max_chars=200,
    )
    service = DeterministicEmbeddingService(output_dimensionality=4)

    enriched = attach_embeddings_to_payloads(payloads, service, batch_size=1)

    assert enriched[0]["title"] == "트랙 안내"
    assert enriched[0]["metadata"] == payloads[0]["metadata"]
    assert enriched[0]["embedding"] is not None
    assert len(enriched[0]["embedding"]) == 4
