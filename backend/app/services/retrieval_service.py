from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.document_ingest import build_document_chunk_payloads, load_ingest_documents
from app.services.embedding_service import EmbeddingService


@dataclass(frozen=True)
class RetrievalResult:
    source_type: str
    title: str
    source: str | None
    category: str | None
    heading_path: str
    content: str
    score: float
    metadata: dict[str, Any]

    def to_evidence(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "title": self.title,
            "source": self.source,
            "category": self.category,
            "heading_path": self.heading_path,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
        }


class LocalDocumentRetriever:
    def __init__(self, payloads: list[dict[str, Any]]) -> None:
        self.payloads = payloads

    @classmethod
    def from_markdown_dirs(cls, raw_dir: Path, wiki_dir: Path) -> LocalDocumentRetriever:
        documents = load_ingest_documents(raw_dir, wiki_dir)
        payloads = build_document_chunk_payloads(documents)
        return cls(payloads)

    def search(self, query: str, *, limit: int = 5) -> list[RetrievalResult]:
        query_terms = _tokenize(query)
        if not query_terms:
            return []

        scored: list[RetrievalResult] = []
        for payload in self.payloads:
            score = _score_payload(payload, query_terms)
            if score <= 0:
                continue
            scored.append(_result_from_payload(payload, score))

        # 같은 점수면 wiki_page를 raw_document보다 먼저 보여줘 Mini Wiki 우선 정책을 유지한다.
        scored.sort(
            key=lambda result: (result.score, result.source_type == "wiki_page"),
            reverse=True,
        )
        return scored[:limit]


class SupabaseTextRetriever:
    def __init__(self, client: Any) -> None:
        self.client = client

    def search(self, query: str, *, limit: int = 5) -> list[RetrievalResult]:
        if not query.strip():
            return []

        # DB document_chunks를 먼저 검색한다.
        # schema SQL에서 wiki_page 우선 정렬을 보장한다.
        result = self.client.rpc(
            "search_document_chunks_text",
            {
                "search_query": query,
                "match_count": limit,
                "filter_source_type": None,
            },
        ).execute()
        return [_result_from_rpc_row(row) for row in result.data or []]


class SupabaseVectorRetriever:
    def __init__(self, client: Any, embedding_service: EmbeddingService) -> None:
        self.client = client
        self.embedding_service = embedding_service

    def search(self, query: str, *, limit: int = 5) -> list[RetrievalResult]:
        if not query.strip():
            return []

        # 질문은 retrieval query task로 embedding해 document chunk vector와 비교한다.
        query_embedding = self.embedding_service.embed_texts(
            [query],
            task_type="RETRIEVAL_QUERY",
        )[0]
        result = self.client.rpc(
            "match_document_chunks",
            {
                "query_embedding": query_embedding,
                "match_count": limit,
                "match_threshold": 0.0,
                "filter_source_type": None,
            },
        ).execute()
        return [_result_from_rpc_row(row) for row in result.data or []]


def _score_payload(payload: dict[str, Any], query_terms: set[str]) -> float:
    searchable = " ".join(
        [
            str(payload.get("title") or ""),
            str(payload.get("category") or ""),
            str(payload.get("heading_path") or ""),
            str(payload.get("content") or ""),
        ]
    ).casefold()
    matched = sum(1 for term in query_terms if term in searchable)
    if matched == 0:
        return 0.0

    source_bonus = 0.25 if payload.get("source_type") == "wiki_page" else 0.0
    heading_bonus = 0.15 if str(payload.get("heading_path") or "") else 0.0
    return matched + source_bonus + heading_bonus


def _result_from_payload(payload: dict[str, Any], score: float) -> RetrievalResult:
    return RetrievalResult(
        source_type=str(payload["source_type"]),
        title=str(payload["title"]),
        source=payload.get("source"),
        category=payload.get("category"),
        heading_path=str(payload.get("heading_path") or ""),
        content=str(payload["content"]),
        score=round(score, 4),
        metadata=dict(payload.get("metadata") or {}),
    )


def _result_from_rpc_row(row: dict[str, Any]) -> RetrievalResult:
    score = row.get("similarity", row.get("rank", 0.0))
    return RetrievalResult(
        source_type=str(row["source_type"]),
        title=str(row["title"]),
        source=row.get("source"),
        category=row.get("category"),
        heading_path=str(row.get("heading_path") or ""),
        content=str(row["content"]),
        score=round(float(score), 4),
        metadata={"id": str(row.get("id")), "source_id": row.get("source_id")},
    )


def _tokenize(query: str) -> set[str]:
    # 한글/영문 키워드를 단순 추출해 DB 없이도 RAG 근거 선택 흐름을 발표에서 설명할 수 있게 한다.
    return {
        token.casefold()
        for token in re.findall(r"[0-9A-Za-z가-힣]+", query)
        if len(token) >= 2
    }
