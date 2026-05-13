from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from app.services.wiki_compiler import compile_wiki, load_raw_documents, write_wiki


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Mini LLM Wiki markdown files.")
    parser.add_argument("--raw-dir", type=Path, default=Path("../data/raw"))
    parser.add_argument("--wiki-dir", type=Path, default=Path("../data/wiki"))
    parser.add_argument("--generated-at", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()

    documents = load_raw_documents(args.raw_dir)
    build = compile_wiki(documents, generated_at=args.generated_at)
    write_wiki(build, args.wiki_dir)
    print(
        f"Mini LLM Wiki generated: raw_documents={len(documents)}, "
        f"wiki_pages={len(build.pages)}, output={args.wiki_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

