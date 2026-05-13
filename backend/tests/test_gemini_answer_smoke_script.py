from __future__ import annotations

from app.schemas.chat import ChatRequest
from app.scripts.gemini_answer_smoke import (
    build_answer_smoke_request,
    build_answer_smoke_retrieval_results,
    resolve_answer_smoke_config,
    run_answer_smoke,
)


class FakeAnswerGenerator:
    def generate_answer(self, request, *, intent, memories, retrieval_results):
        assert request.message == "AI 트랙은 1학년 때 뭐부터 준비하면 좋아?"
        assert intent == "academic_advisor"
        assert retrieval_results[0].title == "AI 트랙 안내"
        return "Python과 자료구조를 먼저 준비하세요."


def test_resolve_answer_smoke_config_uses_env_defaults() -> None:
    config = resolve_answer_smoke_config(
        api_key=None,
        model=None,
        env={"GEMINI_API_KEY": "key", "GEMINI_MAIN_MODEL": "main-model"},
    )

    assert config is not None
    assert config.api_key == "key"
    assert config.model == "main-model"


def test_resolve_answer_smoke_config_returns_none_without_key() -> None:
    assert resolve_answer_smoke_config(api_key=None, model=None, env={}) is None


def test_build_answer_smoke_request() -> None:
    assert build_answer_smoke_request() == ChatRequest(
        message="AI 트랙은 1학년 때 뭐부터 준비하면 좋아?"
    )


def test_build_answer_smoke_retrieval_results() -> None:
    results = build_answer_smoke_retrieval_results()

    assert len(results) == 1
    assert results[0].title == "AI 트랙 안내"
    assert "Python" in results[0].content


def test_run_answer_smoke_generates_non_empty_answer() -> None:
    result = run_answer_smoke(FakeAnswerGenerator())

    assert result == {
        "intent": "academic_advisor",
        "answer_length": len("Python과 자료구조를 먼저 준비하세요."),
        "answer_preview": "Python과 자료구조를 먼저 준비하세요.",
        "internal_source_count": 1,
    }
