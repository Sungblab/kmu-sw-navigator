from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from os import environ
from typing import Protocol

from app.services.assignment_service import AssignmentParser, GeminiAssignmentParser
from app.services.embedding_service import EmbeddingService, GeminiEmbeddingService


@dataclass(frozen=True)
class GeminiSmokeConfig:
    api_key: str
    embedding_model: str
    schedule_model: str
    embedding_dim: int


class _EmbeddingServiceLike(Protocol):
    def embed_texts(
        self,
        texts: list[str],
        *,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        ...


def resolve_gemini_smoke_config(
    *,
    api_key: str | None,
    embedding_model: str | None,
    schedule_model: str | None,
    embedding_dim: int | None,
    env: dict[str, str] | None = None,
) -> GeminiSmokeConfig | None:
    values = environ if env is None else env
    resolved_api_key = (api_key or values.get("GEMINI_API_KEY") or "").strip()
    if not resolved_api_key:
        return None

    resolved_embedding_model = (
        embedding_model or values.get("GEMINI_EMBEDDING_MODEL") or "gemini-embedding-2"
    ).strip()
    resolved_schedule_model = (
        schedule_model
        or values.get("GEMINI_SCHEDULE_MODEL")
        or values.get("GEMINI_LIGHT_MODEL")
        or "gemini-3.1-flash-lite"
    ).strip()
    resolved_embedding_dim = embedding_dim or int(values.get("GEMINI_EMBEDDING_DIM") or "768")

    return GeminiSmokeConfig(
        api_key=resolved_api_key,
        embedding_model=resolved_embedding_model,
        schedule_model=resolved_schedule_model,
        embedding_dim=resolved_embedding_dim,
    )


def build_gemini_smoke_texts() -> list[str]:
    return ["AI 트랙", "자료구조 과제"]


def run_gemini_smoke(
    *,
    embedding_service: EmbeddingService | _EmbeddingServiceLike,
    assignment_parser: AssignmentParser,
    reference_date: date,
) -> dict[str, object]:
    # Gemini smoke는 embedding 차원과 일정 JSON parser를 함께 확인한다.
    embeddings = embedding_service.embed_texts(build_gemini_smoke_texts())
    parsed = assignment_parser.parse_assignment(
        "자료구조 과제 다음주 금요일까지 제출",
        reference_date=reference_date,
    )

    return {
        "embedding_count": len(embeddings),
        "embedding_dim": len(embeddings[0]) if embeddings else 0,
        "assignment_title": parsed.title,
        "assignment_due_at": parsed.due_at.isoformat(),
        "assignment_confidence": parsed.confidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test Gemini embedding and assignment parsing."
    )
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--embedding-model", default=None)
    parser.add_argument("--schedule-model", default=None)
    parser.add_argument("--embedding-dim", type=int, default=None)
    args = parser.parse_args()

    config = resolve_gemini_smoke_config(
        api_key=args.api_key,
        embedding_model=args.embedding_model,
        schedule_model=args.schedule_model,
        embedding_dim=args.embedding_dim,
    )
    if config is None:
        print("Gemini smoke skipped: GEMINI_API_KEY is required.")
        return 2

    try:
        result = run_gemini_smoke(
            embedding_service=GeminiEmbeddingService(
                config.api_key,
                config.embedding_model,
                config.embedding_dim,
            ),
            assignment_parser=GeminiAssignmentParser(config.api_key, config.schedule_model),
            reference_date=date(2026, 5, 14),
        )
    except Exception as exc:
        print(f"Gemini smoke failed: {exc}")
        return 1

    print("Gemini smoke completed")
    print(f"embedding_count={result['embedding_count']}")
    print(f"embedding_dim={result['embedding_dim']}")
    print(f"assignment_title={result['assignment_title']}")
    print(f"assignment_due_at={result['assignment_due_at']}")
    print(f"assignment_confidence={result['assignment_confidence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
