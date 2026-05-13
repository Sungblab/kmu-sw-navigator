from __future__ import annotations

from pathlib import Path

from app.scripts.check_env import build_report, missing_keys, read_env_file


def test_read_env_file_ignores_comments_and_does_not_require_values_to_be_logged(
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "# comment",
                "SUPABASE_URL=https://example.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY='secret-value'",
                "EMPTY_VALUE=",
            ]
        ),
        encoding="utf-8",
    )

    values = read_env_file(env_file)

    assert values["SUPABASE_URL"] == "https://example.supabase.co"
    assert values["SUPABASE_SERVICE_ROLE_KEY"] == "secret-value"
    assert missing_keys(values, ("SUPABASE_URL", "EMPTY_VALUE", "MISSING")) == [
        "EMPTY_VALUE",
        "MISSING",
    ]


def test_build_report_lists_missing_keys_without_secret_values(tmp_path: Path) -> None:
    backend_env = tmp_path / "backend" / ".env"
    frontend_env = tmp_path / "frontend" / ".env"
    backend_env.parent.mkdir()
    frontend_env.parent.mkdir()
    backend_env.write_text(
        "SUPABASE_URL=https://example.supabase.co\nSUPABASE_SERVICE_ROLE_KEY=secret-value\n",
        encoding="utf-8",
    )
    frontend_env.write_text("VITE_SUPABASE_URL=https://example.supabase.co\n", encoding="utf-8")

    lines, has_missing_core = build_report(tmp_path)
    report = "\n".join(lines)

    assert has_missing_core is True
    assert "Backend Supabase Direct: ready" in report
    assert "Frontend Supabase Framework: missing" in report
    assert "VITE_SUPABASE_ANON_KEY" in report
    assert "secret-value" not in report


def test_build_report_accepts_supabase_publishable_key_alias(tmp_path: Path) -> None:
    backend_env = tmp_path / "backend" / ".env"
    frontend_env = tmp_path / "frontend" / ".env"
    backend_env.parent.mkdir()
    frontend_env.parent.mkdir()
    backend_env.write_text(
        "\n".join(
            [
                "SUPABASE_URL=https://example.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY=secret-value",
                "SUPABASE_JWT_SECRET=jwt-secret",
            ]
        ),
        encoding="utf-8",
    )
    frontend_env.write_text(
        "\n".join(
            [
                "VITE_SUPABASE_URL=https://example.supabase.co",
                "VITE_SUPABASE_PUBLISHABLE_KEY=publishable",
            ]
        ),
        encoding="utf-8",
    )

    lines, has_missing_core = build_report(tmp_path)
    report = "\n".join(lines)

    assert has_missing_core is False
    assert "Frontend Supabase Framework: ready" in report
