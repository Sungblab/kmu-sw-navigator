from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

SUPPORTED_TEXT_EXTENSIONS = {".md", ".markdown", ".txt"}
VALID_CATEGORIES = {
    "freshman",
    "track",
    "curriculum",
    "club",
    "roadmap",
    "system",
    "career",
    "startup",
    "general",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z가-힣_-]+", "-", value.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-_")
    return slug or "untitled"


def build_raw_markdown(
    *,
    text: str,
    title: str,
    category: str,
    source: str,
    collected_at: str,
) -> str:
    body = strip_frontmatter(text).strip()
    return f"""---
title: {title}
category: {category}
source: {source}
collected_at: {collected_at}
---

{body}
"""


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    end_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if end_index is None:
        return text
    return "\n".join(lines[end_index + 1 :])


def prepare_raw_document(
    *,
    input_path: Path,
    output_dir: Path,
    title: str,
    category: str,
    source: str,
    collected_at: str | None = None,
    slug: str | None = None,
) -> Path:
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Unsupported category '{category}'. Use one of: {', '.join(sorted(VALID_CATEGORIES))}"
        )
    if input_path.suffix.lower() not in SUPPORTED_TEXT_EXTENSIONS:
        raise ValueError(
            "Only Markdown/text files can be normalized directly. "
            "For PDF or photos, extract text first and save it as .txt or .md."
        )

    text = input_path.read_text(encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slugify(slug or title)}.md"
    output_path.write_text(
        build_raw_markdown(
            text=text,
            title=title,
            category=category,
            source=source,
            collected_at=collected_at or date.today().isoformat(),
        ),
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize a collected KMU source text/markdown file into data/raw frontmatter."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("../data/raw"), type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--category", required=True, choices=sorted(VALID_CATEGORIES))
    parser.add_argument("--source", required=True)
    parser.add_argument("--collected-at")
    parser.add_argument("--slug")
    args = parser.parse_args()

    output_path = prepare_raw_document(
        input_path=args.input,
        output_dir=args.output_dir,
        title=args.title,
        category=args.category,
        source=args.source,
        collected_at=args.collected_at,
        slug=args.slug,
    )
    print(f"Raw document prepared: {output_path}")


if __name__ == "__main__":
    main()
