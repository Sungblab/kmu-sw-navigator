from __future__ import annotations

from pathlib import Path

from scripts.copy_supabase_sql_bundle import (
    build_dashboard_sql_editor_url,
    main,
    read_env_values,
    resolve_project_ref,
)


def test_read_env_values_ignores_comments_and_quotes(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        """
# comment
SUPABASE_URL="https://abc123.supabase.co"
EMPTY=
""".strip(),
        encoding="utf-8",
    )

    values = read_env_values(env_path)

    assert values["SUPABASE_URL"] == "https://abc123.supabase.co"
    assert values["EMPTY"] == ""


def test_resolve_project_ref_reads_backend_env(tmp_path: Path) -> None:
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    (backend_dir / ".env").write_text(
        "SUPABASE_URL=https://abbwnqwvvtxrizutswws.supabase.co\n",
        encoding="utf-8",
    )

    assert resolve_project_ref(tmp_path) == "abbwnqwvvtxrizutswws"


def test_build_dashboard_sql_editor_url_uses_project_ref() -> None:
    assert (
        build_dashboard_sql_editor_url("abbwnqwvvtxrizutswws")
        == "https://supabase.com/dashboard/project/abbwnqwvvtxrizutswws/sql/new"
    )


def test_cli_accepts_pnpm_separator_and_copies_bundle(monkeypatch, capsys) -> None:
    copied: dict[str, str] = {}

    def fake_copy(text: str) -> None:
        copied["text"] = text

    monkeypatch.setattr("scripts.copy_supabase_sql_bundle.copy_to_clipboard", fake_copy)
    monkeypatch.setattr(
        "sys.argv",
        [
            "copy_supabase_sql_bundle.py",
            "--",
            "--project-ref",
            "abbwnqwvvtxrizutswws",
            "--api-base",
            "http://127.0.0.1:8001",
        ],
    )

    assert main() == 0

    output = capsys.readouterr().out
    assert "-- section: schema.sql" in copied["text"]
    assert "-- section: seed.sql" in copied["text"]
    assert "Copied Supabase SQL bundle to clipboard" in output
    assert "https://supabase.com/dashboard/project/abbwnqwvvtxrizutswws/sql/new" in output
    assert "pnpm live:smoke-run --api-base http://127.0.0.1:8001" in output
