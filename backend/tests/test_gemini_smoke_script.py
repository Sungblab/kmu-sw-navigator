from __future__ import annotations

from datetime import date, datetime

from app.scripts.gemini_smoke import (
    GeminiSmokeConfig,
    build_gemini_smoke_texts,
    resolve_gemini_smoke_config,
    run_gemini_smoke,
)
from app.services.assignment_service import ParsedAssignment


class FakeEmbeddingService:
    def embed_texts(
        self,
        texts: list[str],
        *,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        assert task_type == "RETRIEVAL_DOCUMENT"
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeAssignmentParser:
    def parse_assignment(self, text: str, *, reference_date: date) -> ParsedAssignment:
        assert text == "자료구조 과제 다음주 금요일까지 제출"
        assert reference_date == date(2026, 5, 14)
        return ParsedAssignment(
            title="자료구조 과제",
            course="자료구조",
            due_at=datetime(2026, 5, 22, 23, 59),
            confidence=0.91,
        )


def test_resolve_gemini_smoke_config_uses_env_defaults() -> None:
    config = resolve_gemini_smoke_config(
        api_key=None,
        embedding_model=None,
        schedule_model=None,
        embedding_dim=None,
        env={
            "GEMINI_API_KEY": "key",
            "GEMINI_EMBEDDING_MODEL": "embed-model",
            "GEMINI_SCHEDULE_MODEL": "schedule-model",
            "GEMINI_EMBEDDING_DIM": "768",
        },
    )

    assert config == GeminiSmokeConfig(
        api_key="key",
        embedding_model="embed-model",
        schedule_model="schedule-model",
        embedding_dim=768,
    )


def test_resolve_gemini_smoke_config_returns_none_without_key() -> None:
    assert (
        resolve_gemini_smoke_config(
            api_key=None,
            embedding_model=None,
            schedule_model=None,
            embedding_dim=None,
            env={},
        )
        is None
    )


def test_build_gemini_smoke_texts() -> None:
    assert build_gemini_smoke_texts() == ["AI 트랙", "자료구조 과제"]


def test_run_gemini_smoke_checks_embedding_and_schedule_parser() -> None:
    result = run_gemini_smoke(
        embedding_service=FakeEmbeddingService(),
        assignment_parser=FakeAssignmentParser(),
        reference_date=date(2026, 5, 14),
    )

    assert result == {
        "embedding_count": 2,
        "embedding_dim": 3,
        "assignment_title": "자료구조 과제",
        "assignment_due_at": "2026-05-22T23:59:00",
        "assignment_confidence": 0.91,
    }
