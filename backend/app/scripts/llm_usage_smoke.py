from __future__ import annotations

import argparse
from os import getenv
from uuid import UUID

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.schemas.llm_usage import LLMUsageLogCreateRequest
from app.services.store_protocols import LLMUsageLogStore
from app.services.supabase_stores import SupabaseLLMUsageLogStore


def resolve_llm_smoke_user_id(
    cli_user_id: str | None,
    env_user_id: str | None = None,
) -> str | None:
    raw_user_id = (cli_user_id or env_user_id or getenv("SUPABASE_SMOKE_USER_ID") or "").strip()
    if not raw_user_id:
        return None

    try:
        UUID(raw_user_id)
    except ValueError as exc:
        raise ValueError("LLM usage smoke user id must be an auth.users UUID.") from exc
    return raw_user_id


def build_smoke_log_request() -> LLMUsageLogCreateRequest:
    return LLMUsageLogCreateRequest(
        feature="llm_usage_smoke",
        input_text="Supabase LLM usage log smoke",
        output_text="LLM usage log insert/list smoke completed",
        model="smoke-test",
        purpose="Supabase llm_usage_logs insert/list 검증",
        metadata={"source": "llm_usage_smoke"},
    )


def run_llm_usage_smoke(
    store: LLMUsageLogStore,
    *,
    user_id: str,
) -> dict[str, object]:
    # LLM 활용 기록은 제출 증거이므로 insert 직후 같은 user scope로 조회되는지 확인한다.
    created = store.create_log(user_id, build_smoke_log_request())
    listed_logs = store.list_logs(user_id, limit=5)
    return {
        "created_log_id": created.id,
        "created_feature": created.feature,
        "listed_count": len(listed_logs),
        "latest_log_id": listed_logs[0].id if listed_logs else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test Supabase llm_usage_logs insert/list persistence."
    )
    parser.add_argument(
        "--user-id",
        default=None,
        help=(
            "Existing Supabase Auth user UUID to own the smoke row. "
            "Can also be provided through SUPABASE_SMOKE_USER_ID."
        ),
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.has_supabase_backend:
        print(
            "LLM usage smoke skipped: SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY are required."
        )
        return 2

    try:
        user_id = resolve_llm_smoke_user_id(args.user_id)
    except ValueError as exc:
        print(f"LLM usage smoke skipped: {exc}")
        return 2
    if user_id is None:
        print(
            "LLM usage smoke skipped: provide an existing Supabase Auth user UUID "
            "with --user-id or SUPABASE_SMOKE_USER_ID."
        )
        return 2

    store = SupabaseLLMUsageLogStore(get_supabase_client())
    result = run_llm_usage_smoke(store, user_id=user_id)

    print("LLM usage smoke completed")
    print(f"user_id={user_id}")
    print(f"created_log_id={result['created_log_id']}")
    print(f"created_feature={result['created_feature']}")
    print(f"listed_count={result['listed_count']}")
    print(f"latest_log_id={result['latest_log_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
