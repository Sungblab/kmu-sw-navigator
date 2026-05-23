from __future__ import annotations

import argparse
from uuid import UUID

from app.core.config import get_settings
from app.core.supabase_errors import schema_blocker_message
from app.db.supabase_client import get_supabase_client
from app.schemas.profile import ProfileUpsertRequest
from app.scripts.smoke_env import resolve_smoke_value
from app.services.memory_service import create_memory_candidate
from app.services.supabase_stores import SupabaseMemoryStore, SupabaseProfileStore


def resolve_smoke_user_id(cli_user_id: str | None, env_user_id: str | None = None) -> str | None:
    raw_user_id = (cli_user_id or env_user_id or "").strip()
    if not raw_user_id:
        return None

    try:
        UUID(raw_user_id)
    except ValueError as exc:
        raise ValueError("Supabase smoke user id must be an auth.users UUID.") from exc
    return raw_user_id


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test Supabase profile and memory persistence."
    )
    parser.add_argument(
        "--user-id",
        default=None,
        help=(
            "Existing Supabase Auth user UUID to use for the smoke rows. "
            "Can also be provided through SUPABASE_SMOKE_USER_ID."
        ),
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.has_supabase_backend:
        print(
            "Supabase smoke skipped: SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY are required."
        )
        return 2

    try:
        user_id = resolve_smoke_user_id(args.user_id, resolve_smoke_value("SUPABASE_SMOKE_USER_ID"))
    except ValueError as exc:
        print(f"Supabase smoke skipped: {exc}")
        return 2
    if user_id is None:
        print(
            "Supabase smoke skipped: provide an existing Supabase Auth user UUID "
            "with --user-id or SUPABASE_SMOKE_USER_ID."
        )
        return 2

    client = get_supabase_client()
    profile_store = SupabaseProfileStore(client)
    memory_store = SupabaseMemoryStore(client)

    try:
        profile = profile_store.upsert_profile(
            user_id,
            ProfileUpsertRequest(
                department="software",
                grade=1,
                curriculum_year="2025",
            ),
        )
        saved_profile = profile_store.get_profile(user_id)

        # 실제 DB smoke는 사용자 입력 -> 정책 분류 -> 메모리/event 저장까지 한 번에 확인한다.
        memory = create_memory_candidate(
            store=memory_store,
            user_id=user_id,
            natural_text="AI와 백엔드 프로젝트에 관심 있어",
            category="interest",
            key="smoke_topic",
            value_json={"topics": ["AI", "백엔드"], "source": "supabase_smoke"},
        )
        active_memories = memory_store.list_active_memories(user_id)
        events = memory_store.list_events(user_id)
    except Exception as exc:
        print(schema_blocker_message("Supabase smoke", exc))
        return 1

    print("Supabase smoke completed")
    print(f"user_id={user_id}")
    print(f"profile_exists={saved_profile is not None}")
    print(f"profile_department={profile.department}")
    print(f"memory_status={memory.status}")
    print(f"active_memory_count={len(active_memories)}")
    print(f"event_count={len(events)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
