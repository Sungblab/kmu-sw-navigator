from __future__ import annotations

from app.schemas.chat import ChatRequest
from app.scripts.gemini_grounding_smoke import (
    build_grounding_smoke_request,
    resolve_grounding_smoke_config,
    run_grounding_smoke,
)
from app.services.answer_generation_service import GroundedAnswer


class FakeGroundingGenerator:
    def generate_grounded_answer(self, request, *, intent, memories, retrieval_results):
        assert request.message == "AI 백엔드 취업 트렌드 알려줘"
        assert intent == "career_advisor"
        assert memories == []
        assert retrieval_results == []
        return GroundedAnswer(
            text="최신 AI 백엔드 채용은 LLM 서비스 경험을 많이 봅니다.",
            web_sources=[
                {
                    "title": "AI jobs",
                    "uri": "https://example.com/jobs",
                    "domain": "example.com",
                }
            ],
        )


def test_resolve_grounding_smoke_config_uses_env_defaults() -> None:
    config = resolve_grounding_smoke_config(
        api_key=None,
        model=None,
        env={"GEMINI_API_KEY": "key", "GEMINI_MAIN_MODEL": "main-model"},
    )

    assert config is not None
    assert config.api_key == "key"
    assert config.model == "main-model"


def test_resolve_grounding_smoke_config_returns_none_without_key() -> None:
    assert resolve_grounding_smoke_config(api_key=None, model=None, env={}) is None


def test_build_grounding_smoke_request() -> None:
    assert build_grounding_smoke_request() == ChatRequest(
        message="AI 백엔드 취업 트렌드 알려줘"
    )


def test_run_grounding_smoke_returns_web_sources() -> None:
    result = run_grounding_smoke(FakeGroundingGenerator())

    assert result == {
        "intent": "career_advisor",
        "answer_length": len("최신 AI 백엔드 채용은 LLM 서비스 경험을 많이 봅니다."),
        "answer_preview": "최신 AI 백엔드 채용은 LLM 서비스 경험을 많이 봅니다.",
        "web_source_count": 1,
        "first_web_source": "https://example.com/jobs",
    }
