from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_SCHEMA_MARKERS = (
    "-- section: schema.sql",
    "create table if not exists profiles",
    "create table if not exists document_chunks",
    "create table if not exists google_oauth_tokens",
    "create or replace function search_document_chunks_text",
    "create or replace function match_document_chunks",
)
REQUIRED_SEED_MARKERS = (
    "-- section: seed.sql",
    "insert into raw_documents",
    "insert into document_chunks",
    "on conflict (source_type, title, heading_path, chunk_index, content_hash) do nothing",
)
SECRET_MARKERS = (
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_SMOKE_PASSWORD",
    "GEMINI_API_KEY",
    "GOOGLE_OAUTH_CLIENT_SECRET",
    "VITE_SUPABASE_PUBLISHABLE_KEY",
    "VITE_SUPABASE_ANON_KEY",
)


def build_sql_bundle(repo_root: Path, *, include_seed: bool) -> str:
    schema_sql = (repo_root / "supabase" / "schema.sql").read_text(encoding="utf-8").strip()
    sections = [
        "-- kmu-sw-navigator Supabase schema bundle",
        "-- Apply this in the Supabase Dashboard SQL Editor.",
        "-- This file contains no secrets.",
        "",
        "-- section: schema.sql",
        schema_sql,
    ]
    if include_seed:
        seed_sql = (repo_root / "supabase" / "seed.sql").read_text(encoding="utf-8").strip()
        sections.extend(
            [
                "",
                "-- section: seed.sql",
                "-- Optional initial RAG seed rows. document_chunks is idempotent by content_hash.",
                seed_sql,
            ]
        )
    return "\n".join(sections).rstrip() + "\n"


def validate_sql_bundle(bundle: str, *, include_seed: bool) -> list[str]:
    errors: list[str] = []
    for marker in REQUIRED_SCHEMA_MARKERS:
        if marker not in bundle:
            errors.append(f"missing required SQL marker: {marker}")
    if include_seed:
        for marker in REQUIRED_SEED_MARKERS:
            if marker not in bundle:
                errors.append(f"missing required SQL marker: {marker}")
    for marker in SECRET_MARKERS:
        if marker in bundle:
            errors.append(f"secret marker must not be present: {marker}")
    return errors


def write_sql_bundle(repo_root: Path, output_path: Path, *, include_seed: bool) -> Path:
    bundle = build_sql_bundle(repo_root, include_seed=include_seed)
    errors = validate_sql_bundle(bundle, include_seed=include_seed)
    if errors:
        raise ValueError("Supabase SQL bundle validation failed:\n" + "\n".join(errors))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(bundle, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a SQL Editor bundle for Supabase schema application."
    )
    parser.add_argument(
        "--output",
        default="supabase/live-schema-bundle.sql",
        help="Output SQL file path relative to the repo root.",
    )
    parser.add_argument(
        "--include-seed",
        action="store_true",
        help="Append supabase/seed.sql after schema.sql.",
    )
    argv = sys.argv[1:]
    if argv[:1] == ["--"]:
        argv = argv[1:]
    args = parser.parse_args(argv)

    repo_root = Path.cwd()
    output_path = repo_root / args.output
    try:
        write_sql_bundle(repo_root, output_path, include_seed=args.include_seed)
    except ValueError as exc:
        print(exc)
        return 1
    print(f"Supabase SQL bundle written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
