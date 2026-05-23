from __future__ import annotations

from pathlib import Path

from scripts.build_supabase_sql_bundle import build_sql_bundle, main, write_sql_bundle


def test_build_sql_bundle_includes_schema_without_seed_by_default() -> None:
    bundle = build_sql_bundle(Path.cwd(), include_seed=False)

    assert "-- section: schema.sql" in bundle
    assert "create table if not exists profiles" in bundle
    assert "-- section: seed.sql" not in bundle
    assert "SUPABASE_SERVICE_ROLE_KEY" not in bundle


def test_build_sql_bundle_can_append_seed() -> None:
    bundle = build_sql_bundle(Path.cwd(), include_seed=True)

    assert "-- section: schema.sql" in bundle
    assert "-- section: seed.sql" in bundle
    assert "insert into raw_documents" in bundle
    assert "on conflict (source_type, title, heading_path, chunk_index, content_hash) do nothing" in bundle


def test_write_sql_bundle_creates_output_file(tmp_path: Path) -> None:
    output = tmp_path / "live-schema-bundle.sql"

    written = write_sql_bundle(Path.cwd(), output, include_seed=False)

    assert written == output
    assert output.read_text(encoding="utf-8").startswith(
        "-- kmu-sw-navigator Supabase schema bundle"
    )


def test_cli_accepts_pnpm_separator(monkeypatch, tmp_path: Path) -> None:
    output = tmp_path / "bundle.sql"
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_supabase_sql_bundle.py",
            "--",
            "--output",
            str(output),
            "--include-seed",
        ],
    )

    assert main() == 0
    assert "-- section: seed.sql" in output.read_text(encoding="utf-8")
