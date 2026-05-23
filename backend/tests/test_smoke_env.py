from pathlib import Path

from app.scripts.smoke_env import upsert_env_values


def test_upsert_env_values_updates_existing_and_appends_new(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("API_BASE_URL=http://127.0.0.1:8001\nOLD=value\n", encoding="utf-8")

    upsert_env_values(
        env_path,
        {
            "API_BASE_URL": "http://127.0.0.1:8000",
            "SUPABASE_SMOKE_EMAIL": "student@example.com",
        },
    )

    text = env_path.read_text(encoding="utf-8")
    assert "API_BASE_URL=http://127.0.0.1:8000" in text
    assert "OLD=value" in text
    assert "SUPABASE_SMOKE_EMAIL=student@example.com" in text
