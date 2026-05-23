from __future__ import annotations

import argparse
import sys
from pathlib import Path


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


def write_sql_bundle(repo_root: Path, output_path: Path, *, include_seed: bool) -> Path:
    bundle = build_sql_bundle(repo_root, include_seed=include_seed)
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
    write_sql_bundle(repo_root, output_path, include_seed=args.include_seed)
    print(f"Supabase SQL bundle written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
