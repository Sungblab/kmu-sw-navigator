from dataclasses import dataclass
from typing import Any

from app.services.retrieval_service import (
    LocalDocumentRetriever,
    SupabaseTextRetriever,
    SupabaseVectorRetriever,
)


@dataclass
class FakeResult:
    data: Any


class FakeRpcQuery:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.data = data

    def execute(self) -> FakeResult:
        return FakeResult(self.data)


class FakeSupabaseRpcClient:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.data = data
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def rpc(self, name: str, params: dict[str, Any]) -> FakeRpcQuery:
        self.calls.append((name, params))
        return FakeRpcQuery(self.data)


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str]] = []

    def embed_texts(
        self,
        texts: list[str],
        *,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        self.calls.append((texts, task_type))
        return [[0.1, 0.2, 0.3] for _ in texts]


def test_local_retriever_prioritizes_wiki_page_on_tie() -> None:
    retriever = LocalDocumentRetriever(
        [
            {
                "source_type": "raw_document",
                "title": "트랙 원문",
                "source": "팀 정리",
                "category": "track",
                "heading_path": "트랙",
                "content": "AI 트랙은 Python을 먼저 본다.",
                "metadata": {"slug": "raw-track"},
            },
            {
                "source_type": "wiki_page",
                "title": "트랙 위키",
                "source": "Mini LLM Wiki",
                "category": "track",
                "heading_path": "트랙",
                "content": "AI 트랙은 Python을 먼저 본다.",
                "metadata": {"slug": "wiki-track"},
            },
        ]
    )

    results = retriever.search("AI 트랙")

    assert results[0].source_type == "wiki_page"
    assert results[0].to_evidence()["metadata"]["slug"] == "wiki-track"


def test_local_retriever_returns_empty_for_unmatched_query() -> None:
    retriever = LocalDocumentRetriever(
        [
            {
                "source_type": "wiki_page",
                "title": "트랙 위키",
                "source": "Mini LLM Wiki",
                "category": "track",
                "heading_path": "트랙",
                "content": "AI 트랙은 Python을 먼저 본다.",
                "metadata": {},
            }
        ]
    )

    assert retriever.search("완전히다른질문") == []


def test_supabase_text_retriever_maps_rpc_rows_to_evidence() -> None:
    client = FakeSupabaseRpcClient(
        [
            {
                "id": "chunk-1",
                "source_type": "wiki_page",
                "source_id": None,
                "title": "신입생 안내",
                "source": "Mini LLM Wiki",
                "category": "freshman",
                "heading_path": "신입생 안내 > 수강신청",
                "content": "수강신청 전에는 시간표 충돌 여부를 확인한다.",
                "rank": 0.75,
            }
        ]
    )
    retriever = SupabaseTextRetriever(client)

    results = retriever.search("수강신청", limit=3)

    assert client.calls == [
        (
            "search_document_chunks_text",
            {"search_query": "수강신청", "match_count": 3, "filter_source_type": None},
        )
    ]
    assert results[0].source_type == "wiki_page"
    assert results[0].score == 0.75
    assert results[0].to_evidence()["metadata"]["id"] == "chunk-1"


def test_supabase_vector_retriever_embeds_query_and_maps_similarity() -> None:
    client = FakeSupabaseRpcClient(
        [
            {
                "id": "chunk-2",
                "source_type": "wiki_page",
                "source_id": None,
                "title": "트랙 안내",
                "source": "Mini LLM Wiki",
                "category": "track",
                "heading_path": "트랙 안내",
                "content": "AI 트랙은 Python을 먼저 본다.",
                "similarity": 0.91,
            }
        ]
    )
    embedding_service = FakeEmbeddingService()
    retriever = SupabaseVectorRetriever(client, embedding_service)

    results = retriever.search("AI 트랙", limit=2)

    assert embedding_service.calls == [(["AI 트랙"], "RETRIEVAL_QUERY")]
    assert client.calls == [
        (
            "match_document_chunks",
            {
                "query_embedding": [0.1, 0.2, 0.3],
                "match_count": 2,
                "match_threshold": 0.0,
                "filter_source_type": None,
            },
        )
    ]
    assert results[0].score == 0.91
    assert results[0].metadata["id"] == "chunk-2"
