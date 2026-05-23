from __future__ import annotations

from pathlib import Path

from app.scripts.live_smoke_plan import (
    LiveSmokeStep,
    build_live_smoke_steps,
    format_live_smoke_plan,
)


def test_build_live_smoke_steps_marks_missing_inputs(tmp_path: Path) -> None:
    (tmp_path / "backend").mkdir()
    (tmp_path / "frontend").mkdir()
    (tmp_path / "backend" / ".env").write_text(
        "\n".join(
            [
                "SUPABASE_URL=https://project.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY=service-role",
                "SUPABASE_JWT_SECRET=jwt-secret",
                "GEMINI_API_KEY=",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "frontend" / ".env").write_text(
        "\n".join(
            [
                "VITE_SUPABASE_URL=https://project.supabase.co",
                "VITE_SUPABASE_ANON_KEY=anon",
            ]
        ),
        encoding="utf-8",
    )

    steps = build_live_smoke_steps(
        tmp_path,
        user_id=None,
        email=None,
        password=None,
    )

    assert steps[0] == LiveSmokeStep(
        name="Supabase env strict",
        command="pnpm env:check:strict",
        ready=True,
        missing=[],
    )
    assert steps[1].name == "Supabase schema check"
    assert steps[1].ready is True
    assert steps[3].ready is False
    assert steps[3].missing == ["--user-id or SUPABASE_SMOKE_USER_ID"]
    assert steps[6].ready is False
    assert "GEMINI_API_KEY" in steps[6].missing


def test_build_live_smoke_steps_accepts_publishable_key_alias(tmp_path: Path) -> None:
    (tmp_path / "backend").mkdir()
    (tmp_path / "frontend").mkdir()
    (tmp_path / "backend" / ".env").write_text(
        "\n".join(
            [
                "SUPABASE_URL=https://project.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY=service-role",
                "SUPABASE_JWT_SECRET=jwt-secret",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "frontend" / ".env").write_text(
        "\n".join(
            [
                "VITE_SUPABASE_URL=https://project.supabase.co",
                "VITE_SUPABASE_PUBLISHABLE_KEY=publishable",
            ]
        ),
        encoding="utf-8",
    )

    steps = build_live_smoke_steps(
        tmp_path,
        user_id=None,
        email="student@example.com",
        password="password",
    )

    assert steps[0].ready is True
    assert "VITE_SUPABASE_ANON_KEY" not in steps[2].missing


def test_format_live_smoke_plan_hides_secret_values(tmp_path: Path) -> None:
    (tmp_path / "backend").mkdir()
    (tmp_path / "frontend").mkdir()
    (tmp_path / "backend" / ".env").write_text(
        "\n".join(
            [
                "SUPABASE_URL=https://project.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY=secret-value",
                "SUPABASE_JWT_SECRET=jwt-secret",
                "GEMINI_API_KEY=gemini-secret",
                "GOOGLE_OAUTH_CLIENT_SECRET=google-secret",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "frontend" / ".env").write_text(
        "VITE_SUPABASE_URL=https://project.supabase.co\nVITE_SUPABASE_ANON_KEY=anon-secret\n",
        encoding="utf-8",
    )

    report = "\n".join(
        format_live_smoke_plan(
            build_live_smoke_steps(
                tmp_path,
                user_id="11111111-1111-4111-8111-111111111111",
                email="student@example.com",
                password="password",
            )
        )
    )

    assert "secret-value" not in report
    assert "gemini-secret" not in report
    assert "google-secret" not in report
    assert "anon-secret" not in report
    assert "[ready] Supabase DB smoke" in report
    assert "pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>" in report
    assert "pnpm supabase:create-smoke-user --write-root-env" in report
