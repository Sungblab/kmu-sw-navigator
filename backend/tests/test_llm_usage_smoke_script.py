from __future__ import annotations

import pytest

from app.schemas.llm_usage import LLMUsageLogCreateRequest
from app.scripts.llm_usage_smoke import (
    build_smoke_log_request,
    resolve_llm_smoke_user_id,
    run_llm_usage_smoke,
)
from app.services.llm_usage_log_service import InMemoryLLMUsageLogStore


def test_resolve_llm_smoke_user_id_prefers_cli_value() -> None:
    user_id = "11111111-1111-4111-8111-111111111111"

    assert resolve_llm_smoke_user_id(user_id, "22222222-2222-4222-8222-222222222222") == user_id


def test_resolve_llm_smoke_user_id_accepts_env_value() -> None:
    user_id = "22222222-2222-4222-8222-222222222222"

    assert resolve_llm_smoke_user_id(None, user_id) == user_id


def test_resolve_llm_smoke_user_id_rejects_non_uuid() -> None:
    with pytest.raises(ValueError, match="auth.users UUID"):
        resolve_llm_smoke_user_id("demo-user")


def test_build_smoke_log_request() -> None:
    request = build_smoke_log_request()

    assert isinstance(request, LLMUsageLogCreateRequest)
    assert request.feature == "llm_usage_smoke"
    assert request.input_text == "Supabase LLM usage log smoke"
    assert request.metadata["source"] == "llm_usage_smoke"


def test_run_llm_usage_smoke_creates_and_lists_current_user_log() -> None:
    store = InMemoryLLMUsageLogStore()
    other = store.create_log(
        "22222222-2222-4222-8222-222222222222",
        LLMUsageLogCreateRequest(
            feature="other",
            input_text="다른 사용자",
            purpose="scope check",
        ),
    )

    result = run_llm_usage_smoke(
        store,
        user_id="11111111-1111-4111-8111-111111111111",
    )

    assert result["created_feature"] == "llm_usage_smoke"
    assert result["listed_count"] == 1
    assert result["latest_log_id"] != other.id
