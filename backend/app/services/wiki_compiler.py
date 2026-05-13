from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class RawDocument:
    slug: str
    title: str
    category: str
    source: str
    body: str
    path: Path


@dataclass(frozen=True)
class WikiPage:
    slug: str
    title: str
    category: str
    content: str
    source_count: int


@dataclass(frozen=True)
class WikiBuild:
    pages: list[WikiPage]
    index_content: str
    log_content: str
    generated_at: date

    @property
    def pages_by_slug(self) -> dict[str, WikiPage]:
        return {page.slug: page for page in self.pages}


CATEGORY_TITLES = {
    "club": "동아리와 활동",
    "freshman": "신입생 안내",
    "general": "기타 자료",
    "roadmap": "로드맵",
    "system": "학교 시스템",
    "track": "트랙 안내",
}


def parse_raw_document(path: Path) -> RawDocument:
    text = path.read_text(encoding="utf-8")
    metadata, body = _split_frontmatter(text)
    body = body.strip()
    title = metadata.get("title") or _first_h1(body) or _title_from_stem(path.stem)
    category = _slugify(metadata.get("category") or "general")
    source = metadata.get("source") or "팀 정리"
    return RawDocument(
        slug=_slugify(path.stem),
        title=title,
        category=category,
        source=source,
        body=body,
        path=path,
    )


def load_raw_documents(raw_dir: Path) -> list[RawDocument]:
    return [
        parse_raw_document(path)
        for path in sorted(raw_dir.glob("*.md"))
        if path.name.lower() != "readme.md"
    ]


def compile_wiki(raw_documents: list[RawDocument], generated_at: date) -> WikiBuild:
    grouped: dict[str, list[RawDocument]] = {}
    for document in raw_documents:
        if document.body.strip():
            grouped.setdefault(document.category, []).append(document)

    pages = [
        _compile_category_page(category, sorted(documents, key=lambda doc: doc.title), generated_at)
        for category, documents in sorted(grouped.items())
    ]
    index_content = _build_index(pages, generated_at)
    log_content = _build_log(
        raw_count=sum(page.source_count for page in pages),
        pages=pages,
        generated_at=generated_at,
    )
    return WikiBuild(
        pages=pages,
        index_content=index_content,
        log_content=log_content,
        generated_at=generated_at,
    )


def write_wiki(build: WikiBuild, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "_index.md").write_text(build.index_content, encoding="utf-8")
    (output_dir / "log.md").write_text(build.log_content, encoding="utf-8")
    for page in build.pages:
        (output_dir / f"{page.slug}.md").write_text(page.content, encoding="utf-8")


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


def _title_from_stem(stem: str) -> str:
    return stem.replace("-", " ").replace("_", " ").strip() or "Untitled"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z가-힣_-]+", "-", value.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-_")
    return slug or "general"


def _category_title(category: str) -> str:
    return CATEGORY_TITLES.get(category, _title_from_stem(category))


def _compile_category_page(
    category: str, documents: list[RawDocument], generated_at: date
) -> WikiPage:
    title = _category_title(category)
    source_lines = "\n".join(
        f"- {document.title} — {document.source} (`{document.path.name}`)" for document in documents
    )
    body_sections = "\n\n".join(_document_section(document) for document in documents)
    content = f"""---
slug: {category}
type: topic
category: {category}
status: active
sources: {len(documents)}
last_touched: {generated_at.isoformat()}
---

# {title}

## 핵심 요약

이 페이지는 `{category}` category의 원문 {len(documents)}개를
신입생 질문에 답하기 좋게 묶은 Mini LLM Wiki page입니다.

## 원문별 정리

{body_sections}

## 관련 자료

{source_lines}
"""
    return WikiPage(
        slug=category,
        title=title,
        category=category,
        content=content,
        source_count=len(documents),
    )


def _document_section(document: RawDocument) -> str:
    return f"""### {document.title}

출처: {document.source}

{document.body}"""


def _build_index(pages: list[WikiPage], generated_at: date) -> str:
    page_lines = "\n".join(
        f"- [[{page.slug}]] — {page.title} ({page.source_count}개 원문)" for page in pages
    )
    return f"""# kmu-sw-navigator Wiki

생성일: {generated_at.isoformat()}

## 위키 페이지

{page_lines}

## 검색 원칙

- 신입생 질문은 wiki page를 우선 검색합니다.
- 답변 근거가 부족하면 raw document chunk를 함께 검색합니다.
- 출처가 불명확한 내용은 학부 공지 확인 필요로 표시합니다.
"""


def _build_log(raw_count: int, pages: list[WikiPage], generated_at: date) -> str:
    page_summary = ", ".join(page.slug for page in pages) or "none"
    return f"""# Wiki Build Log

- {generated_at.isoformat()}: {raw_count}개 원문으로 {len(pages)}개 wiki page 생성: {page_summary}
"""
