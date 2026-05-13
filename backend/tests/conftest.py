from collections.abc import Iterator

import pytest

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.main import app


@pytest.fixture(autouse=True)
def isolate_tests_from_local_live_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Keep unit/API tests deterministic even when local .env contains live keys."""
    for key in (
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_SECRET",
        "GEMINI_API_KEY",
        "GOOGLE_OAUTH_CLIENT_ID",
        "GOOGLE_OAUTH_CLIENT_SECRET",
    ):
        monkeypatch.setenv(key, "")
    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()
    get_supabase_client.cache_clear()
