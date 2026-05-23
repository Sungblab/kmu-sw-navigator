from __future__ import annotations

import argparse
from dataclasses import dataclass
from os import environ

from app.core.config import get_settings
from app.schemas.chat import ChatRequest
from app.services.answer_generation_service import AnswerGenerator, GeminiAnswerGenerator
from app.services.chat_contract_service import build_chat_response
from app.services.retrieval_service import RetrievalResult


@dataclass(frozen=True)
class GeminiAnswerSmokeConfig:
    api_key: str
    model: str


def resolve_answer_smoke_config(
    *,
    api_key: str | None,
    model: str | None,
    env: dict[str, str] | None = None,
) -> GeminiAnswerSmokeConfig | None:
    values = environ if env is None else env
    resolved_api_key = (api_key or values.get("GEMINI_API_KEY") or "").strip()
    if not resolved_api_key:
        return None
    resolved_model = (model or values.get("GEMINI_MAIN_MODEL") or "gemini-3-flash-preview").strip()
    return GeminiAnswerSmokeConfig(api_key=resolved_api_key, model=resolved_model)


def build_answer_smoke_request() -> ChatRequest:
    return ChatRequest(message="AI 트랙은 1학년 때 뭐부터 준비하면 좋아?")


def build_answer_smoke_retrieval_results() -> list[RetrievalResult]:
    return [
        RetrievalResult(
            source_type="wiki_page",
            title="AI 트랙 안내",
            source="Mini LLM Wiki",
            category="track",
            heading_path="AI 트랙",
            content="AI 트랙은 Python, 자료구조, 선형대수 기초를 먼저 준비하면 좋다.",
            score=0.91,
            metadata={"source": "gemini_answer_smoke"},
        )
    ]


def run_answer_smoke(answer_generator: AnswerGenerator) -> dict[str, object]:
    response = build_chat_response(
        build_answer_smoke_request(),
        memories=[],
        retrieval_results=build_answer_smoke_retrieval_results(),
        answer_generator=answer_generator,
    )
    return {
        "intent": response.intent,
        "answer_length": len(response.answer),
        "answer_preview": response.answer[:120],
        "internal_source_count": len(response.evidence.internal_sources),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test Gemini answer generation.")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--model", default=None)
    args = parser.parse_args()
    settings = get_settings()

    config = resolve_answer_smoke_config(
        api_key=args.api_key or settings.gemini_api_key,
        model=args.model or settings.gemini_main_model,
    )
    if config is None:
        print("Gemini answer smoke skipped: GEMINI_API_KEY is required.")
        return 2

    try:
        result = run_answer_smoke(GeminiAnswerGenerator(config.api_key, config.model))
    except Exception as exc:
        print(f"Gemini answer smoke failed: {exc}")
        return 1

    print("Gemini answer smoke completed")
    print(f"intent={result['intent']}")
    print(f"answer_length={result['answer_length']}")
    print(f"answer_preview={result['answer_preview']}")
    print(f"internal_source_count={result['internal_source_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
