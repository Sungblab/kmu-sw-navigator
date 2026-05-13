from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.markdown_chunker import chunk_markdown
from app.services.wiki_compiler import parse_raw_document


@dataclass(frozen=True)
class IngestDocument:
    source_type: str
    slug: str
    title: str
    source: str
    category: str
    content: str
    path: Path


def load_ingest_documents(raw_dir: Path, wiki_dir: Path) -> list[IngestDocument]:
    documents: list[IngestDocument] = []

    for raw_path in sorted(raw_dir.glob("*.md")):
        if raw_path.name.lower() == "readme.md":
            continue
        raw_document = parse_raw_document(raw_path)
        documents.append(
            IngestDocument(
                source_type="raw_document",
                slug=raw_document.slug,
                title=raw_document.title,
                source=raw_document.source,
                category=raw_document.category,
                content=raw_document.body,
                path=raw_path,
            )
        )

    for wiki_path in sorted(wiki_dir.glob("*.md")):
        if wiki_path.name.lower() in {"_index.md", "log.md"}:
            continue
        metadata, body = _split_frontmatter(wiki_path.read_text(encoding="utf-8"))
        category = metadata.get("category") or wiki_path.stem
        documents.append(
            IngestDocument(
                source_type="wiki_page",
                slug=metadata.get("slug") or wiki_path.stem,
                title=_first_h1(body) or _title_from_slug(wiki_path.stem),
                source="Mini LLM Wiki",
                category=category,
                content=body.strip(),
                path=wiki_path,
            )
        )

    return [document for document in documents if document.content.strip()]


def build_document_chunk_payloads(
    documents: list[IngestDocument],
    max_chars: int = 1200,
) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for document in documents:
        for chunk in chunk_markdown(document.content, max_chars=max_chars):
            # source_type/category metadata를 chunk마다 반복 저장해 RAG 검색 결과만으로도
            # 답변 근거와 "wiki 우선, raw 보강" 정책을 설명할 수 있게 한다.
            payloads.append(
                {
                    "source_type": document.source_type,
                    "source_id": None,
                    "title": document.title,
                    "source": document.source,
                    "category": document.category,
                    "department": "소프트웨어융합대학",
                    "heading_path": chunk.heading_path,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "content_hash": chunk.content_hash,
                    "embedding": None,
                    "metadata": {
                        "slug": document.slug,
                        "path": str(document.path.as_posix()),
                        "source_start": chunk.source_start,
                        "source_end": chunk.source_end,
                        "token_count": chunk.token_count,
                    },
                }
            )
    return payloads


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if end_index is None:
        return {}, text

    metadata: dict[str, str] = {}
    for line in lines[1:end_index]:
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip()
    return metadata, "\n".join(lines[end_index + 1 :])


def _first_h1(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _title_from_slug(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").strip() or "Untitled"
