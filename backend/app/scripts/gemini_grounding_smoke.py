from __future__ import annotations

import argparse
from dataclasses import dataclass
from os import environ

from app.schemas.chat import ChatRequest
from app.services.answer_generation_service import (
    GeminiGroundingAnswerGenerator,
    GroundingAnswerGenerator,
)
from app.services.chat_contract_service import build_chat_response


@dataclass(frozen=True)
class GeminiGroundingSmokeConfig:
    api_key: str
    model: str


def resolve_grounding_smoke_config(
    *,
    api_key: str | None,
    model: str | None,
    env: dict[str, str] | None = None,
) -> GeminiGroundingSmokeConfig | None:
    values = environ if env is None else env
    resolved_api_key = (api_key or values.get("GEMINI_API_KEY") or "").strip()
    if not resolved_api_key:
        return None
    resolved_model = (model or values.get("GEMINI_MAIN_MODEL") or "gemini-3-flash-preview").strip()
    return GeminiGroundingSmokeConfig(api_key=resolved_api_key, model=resolved_model)


def build_grounding_smoke_request() -> ChatRequest:
    return ChatRequest(message="AI 백엔드 취업 트렌드 알려줘")


def run_grounding_smoke(grounding_generator: GroundingAnswerGenerator) -> dict[str, object]:
    response = build_chat_response(
        build_grounding_smoke_request(),
        memories=[],
        retrieval_results=[],
        grounding_answer_generator=grounding_generator,
    )
    first_source = response.evidence.web_sources[0]["uri"] if response.evidence.web_sources else ""
    return {
        "intent": response.intent,
        "answer_length": len(response.answer),
        "answer_preview": response.answer[:120],
        "web_source_count": len(response.evidence.web_sources),
        "first_web_source": first_source,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test Gemini Google grounding.")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    config = resolve_grounding_smoke_config(api_key=args.api_key, model=args.model)
    if config is None:
        print("Gemini grounding smoke skipped: GEMINI_API_KEY is required.")
        return 2

    try:
        result = run_grounding_smoke(
            GeminiGroundingAnswerGenerator(config.api_key, config.model)
        )
    except Exception as exc:
        print(f"Gemini grounding smoke failed: {exc}")
        return 1

    print("Gemini grounding smoke completed")
    print(f"intent={result['intent']}")
    print(f"answer_length={result['answer_length']}")
    print(f"answer_preview={result['answer_preview']}")
    print(f"web_source_count={result['web_source_count']}")
    print(f"first_web_source={result['first_web_source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
