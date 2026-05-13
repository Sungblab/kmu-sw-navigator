from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class MarkdownChunk:
    chunk_index: int
    heading_path: str
    content: str
    token_count: int
    content_hash: str
    source_start: int
    source_end: int


def chunk_markdown(text: str, max_chars: int = 1200) -> list[MarkdownChunk]:
    """Split markdown by heading-aware character chunks."""
    if max_chars < 20:
        raise ValueError("max_chars must be at least 20")

    heading_stack: list[str] = []
    pending: list[tuple[str, int, int]] = []
    chunks: list[MarkdownChunk] = []
    cursor = 0

    def heading_path() -> str:
        return " > ".join(part for part in heading_stack if part)

    def add_chunk(content: str, start: int, end: int) -> None:
        clean = content.strip()
        if not clean:
            return
        chunks.append(
            MarkdownChunk(
                chunk_index=len(chunks),
                heading_path=heading_path(),
                content=clean,
                token_count=max(1, (len(clean) + 3) // 4),
                content_hash=sha256(clean.encode("utf-8")).hexdigest(),
                source_start=start,
                source_end=end,
            )
        )

    def flush() -> None:
        if not pending:
            return
        content = "\n".join(part for part, _, _ in pending).strip()
        start = pending[0][1]
        end = pending[-1][2]
        pending.clear()
        add_chunk(content, start, end)

    for segment in text.splitlines(keepends=True):
        start = cursor
        end = cursor + len(segment)
        cursor = end
        line = segment.rstrip("\r\n").rstrip()

        if line.startswith("#"):
            marker, _, title = line.partition(" ")
            if marker and set(marker) == {"#"} and 1 <= len(marker) <= 6 and title.strip():
                # heading_path를 metadata로 남겨 RAG 답변의 문단 근거를 설명할 수 있게 한다.
                flush()
                level = len(marker)
                heading_stack[level - 1 :] = [title.strip()]
                continue

        if len(line) > max_chars:
            # 긴 문단은 검색 단위가 너무 커지지 않도록 쪼개되 원문 위치는 유지한다.
            flush()
            for offset in range(0, len(line), max_chars):
                part = line[offset : offset + max_chars]
                add_chunk(part, start + offset, min(start + offset + len(part), end))
            continue

        if not line and not pending:
            continue

        next_text = "\n".join([part for part, _, _ in pending] + [line]).strip()
        if pending and len(next_text) > max_chars:
            # chunk 크기를 제한해 embedding 검색에서 한 결과가 여러 주제를 섞지 않게 한다.
            flush()
        pending.append((line, start, end))

    flush()
    return chunks
