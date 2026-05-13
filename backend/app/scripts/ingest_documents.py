from __future__ import annotations

import argparse
from pathlib import Path

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.schemas.llm_usage import LLMUsageLogCreateRequest
from app.services.document_ingest import build_document_chunk_payloads, load_ingest_documents
from app.services.embedding_service import GeminiEmbeddingService, attach_embeddings_to_payloads
from app.services.supabase_stores import SupabaseLLMUsageLogStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest raw/wiki markdown into document_chunks.")
    parser.add_argument("--raw-dir", type=Path, default=Path("../data/raw"))
    parser.add_argument("--wiki-dir", type=Path, default=Path("../data/wiki"))
    parser.add_argument("--max-chars", type=int, default=1200)
    parser.add_argument("--with-embeddings", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--llm-log-user-id",
        default=None,
        help="Optional Supabase auth user id used to record embedding ingest in llm_usage_logs.",
    )
    args = parser.parse_args()

    settings = get_settings()
    documents = load_ingest_documents(args.raw_dir, args.wiki_dir)
    payloads = build_document_chunk_payloads(documents, max_chars=args.max_chars)

    if args.with_embeddings:
        if not settings.gemini_api_key:
            print("Document ingest skipped: GEMINI_API_KEY is required for embeddings.")
            return 2
        embedding_service = GeminiEmbeddingService(
            api_key=settings.gemini_api_key,
            model=settings.gemini_embedding_model,
            output_dimensionality=settings.gemini_embedding_dim,
        )
        payloads = attach_embeddings_to_payloads(payloads, embedding_service)

    source_counts = _count_by_source_type(payloads)
    embedded_count = sum(1 for payload in payloads if payload.get("embedding") is not None)

    print(
        "Document ingest prepared: "
        f"documents={len(documents)}, chunks={len(payloads)}, "
        f"wiki_chunks={source_counts.get('wiki_page', 0)}, "
        f"raw_chunks={source_counts.get('raw_document', 0)}, "
        f"embedded_chunks={embedded_count}"
    )

    if args.llm_log_user_id and args.with_embeddings and settings.has_supabase_backend:
        SupabaseLLMUsageLogStore(get_supabase_client()).create_log(
            args.llm_log_user_id,
            build_embedding_ingest_log_request(
                raw_dir=str(args.raw_dir),
                wiki_dir=str(args.wiki_dir),
                document_count=len(documents),
                chunk_count=len(payloads),
                embedded_count=embedded_count,
                model=settings.gemini_embedding_model,
                output_dimensionality=settings.gemini_embedding_dim,
                dry_run=args.dry_run,
            ),
        )

    if args.dry_run:
        return 0

    if not settings.has_supabase_backend:
        print(
            "Document ingest skipped: SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY are required."
        )
        return 2

    client = get_supabase_client()
    if payloads:
        # 1차 ingest는 embedding 없이 text search 근거를 먼저 채운다.
        # embedding 재생성 slice에서 같은 content_hash 기준으로 vector를 업데이트한다.
        client.table("document_chunks").insert(payloads).execute()

    print(f"Document ingest inserted: chunks={len(payloads)}")
    return 0


def _count_by_source_type(payloads: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for payload in payloads:
        source_type = str(payload["source_type"])
        counts[source_type] = counts.get(source_type, 0) + 1
    return counts


def build_embedding_ingest_log_request(
    *,
    raw_dir: str,
    wiki_dir: str,
    document_count: int,
    chunk_count: int,
    embedded_count: int,
    model: str,
    output_dimensionality: int,
    dry_run: bool,
) -> LLMUsageLogCreateRequest:
    return LLMUsageLogCreateRequest(
        feature="embedding_ingest",
        input_text=f"{raw_dir} | {wiki_dir}",
        output_text=(
            f"documents={document_count}, chunks={chunk_count}, "
            f"embedded_chunks={embedded_count}"
        ),
        model=model,
        purpose="문서 chunk embedding 생성",
        metadata={
            "document_count": document_count,
            "chunk_count": chunk_count,
            "embedded_count": embedded_count,
            "output_dimensionality": output_dimensionality,
            "dry_run": dry_run,
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
