from __future__ import annotations

import pytest

from app.scripts.supabase_smoke import resolve_smoke_user_id


def test_resolve_smoke_user_id_prefers_cli_value() -> None:
    user_id = "11111111-1111-4111-8111-111111111111"

    assert resolve_smoke_user_id(user_id, "22222222-2222-4222-8222-222222222222") == user_id


def test_resolve_smoke_user_id_accepts_env_value() -> None:
    user_id = "22222222-2222-4222-8222-222222222222"

    assert resolve_smoke_user_id(None, user_id) == user_id


def test_resolve_smoke_user_id_rejects_non_uuid() -> None:
    with pytest.raises(ValueError, match="auth.users UUID"):
        resolve_smoke_user_id("smoke-not-a-uuid")


def test_resolve_smoke_user_id_returns_none_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_SMOKE_USER_ID", raising=False)

    assert resolve_smoke_user_id(None, None) is None
