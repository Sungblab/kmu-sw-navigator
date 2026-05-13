from __future__ import annotations

import argparse
from datetime import datetime
from os import getenv
from uuid import UUID

import httpx

from app.core.config import Settings, get_settings
from app.db.supabase_client import get_supabase_client
from app.schemas.assignment import AssignmentCreateRequest
from app.services.calendar_service import export_assignment_to_calendar
from app.services.google_oauth_token_service import GoogleOAuthTokenStore
from app.services.store_protocols import AssignmentStore
from app.services.supabase_stores import SupabaseAssignmentStore, SupabaseGoogleOAuthTokenStore


def resolve_calendar_smoke_user_id(
    cli_user_id: str | None,
    env_user_id: str | None = None,
) -> str | None:
    raw_user_id = (cli_user_id or env_user_id or getenv("SUPABASE_SMOKE_USER_ID") or "").strip()
    if not raw_user_id:
        return None
    try:
        UUID(raw_user_id)
    except ValueError as exc:
        raise ValueError("Calendar smoke user id must be an auth.users UUID.") from exc
    return raw_user_id


def build_smoke_assignment_request() -> AssignmentCreateRequest:
    return AssignmentCreateRequest(
        title="Google Calendar smoke 과제",
        course="캡스톤",
        due_at=datetime(2026, 6, 10, 23, 59),
        memo="calendar smoke",
    )


def run_calendar_export_smoke(
    *,
    user_id: str,
    assignment_store: AssignmentStore,
    token_store: GoogleOAuthTokenStore,
    settings: Settings,
    client: httpx.Client,
) -> dict[str, object]:
    if token_store.get_token(user_id) is None:
        raise RuntimeError("Google Calendar token is missing for this user.")

    assignment = assignment_store.create_assignment(user_id, build_smoke_assignment_request())
    exported = export_assignment_to_calendar(
        user_id,
        assignment.id,
        store=assignment_store,
        token_store=token_store,
        settings=settings,
        client=client,
    )
    return {
        "assignment_title": assignment.title,
        "calendar_event_id": exported.calendar_event_id,
        "already_exported": exported.already_exported,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test Google Calendar events.insert through the assignment export path."
    )
    parser.add_argument(
        "--user-id",
        default=None,
        help=(
            "Existing Supabase Auth user UUID with a stored Google Calendar token. "
            "Can also be provided through SUPABASE_SMOKE_USER_ID."
        ),
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.has_supabase_backend:
        print(
            "Calendar export smoke skipped: SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY are required."
        )
        return 2
    if not settings.google_oauth_client_secret:
        print("Calendar export smoke skipped: GOOGLE_OAUTH_CLIENT_SECRET is required.")
        return 2

    try:
        user_id = resolve_calendar_smoke_user_id(args.user_id)
    except ValueError as exc:
        print(f"Calendar export smoke skipped: {exc}")
        return 2
    if user_id is None:
        print(
            "Calendar export smoke skipped: provide an existing Supabase Auth user UUID "
            "with --user-id or SUPABASE_SMOKE_USER_ID."
        )
        return 2

    client = get_supabase_client()
    try:
        result = run_calendar_export_smoke(
            user_id=user_id,
            assignment_store=SupabaseAssignmentStore(client),
            token_store=SupabaseGoogleOAuthTokenStore(client),
            settings=settings,
            client=httpx.Client(timeout=10),
        )
    except (RuntimeError, httpx.HTTPError) as exc:
        print(f"Calendar export smoke failed: {exc}")
        return 1

    print("Calendar export smoke completed")
    print(f"user_id={user_id}")
    print(f"assignment_title={result['assignment_title']}")
    print(f"calendar_event_id={result['calendar_event_id']}")
    print(f"already_exported={result['already_exported']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
