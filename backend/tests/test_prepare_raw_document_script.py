from pathlib import Path

import pytest

from app.scripts.prepare_raw_document import prepare_raw_document, slugify


def test_prepare_raw_document_writes_frontmatter(tmp_path: Path) -> None:
    source = tmp_path / "curriculum.txt"
    source.write_text("# AI curriculum\n\n- Python\n- Data structures\n", encoding="utf-8")

    output = prepare_raw_document(
        input_path=source,
        output_dir=tmp_path / "raw",
        title="인공지능학부 교과과정",
        category="curriculum",
        source="사용자 제공 캡처 정리",
        collected_at="2026-05-23",
    )

    assert output.name == "인공지능학부-교과과정.md"
    assert output.read_text(encoding="utf-8").startswith(
        "---\n"
        "title: 인공지능학부 교과과정\n"
        "category: curriculum\n"
        "source: 사용자 제공 캡처 정리\n"
        "collected_at: 2026-05-23\n"
        "---\n\n"
    )
    assert "# AI curriculum" in output.read_text(encoding="utf-8")


def test_prepare_raw_document_replaces_existing_frontmatter(tmp_path: Path) -> None:
    source = tmp_path / "club.md"
    source.write_text(
        "---\ntitle: old\ncategory: general\n---\n\n# 동아리\n\n내용",
        encoding="utf-8",
    )

    output = prepare_raw_document(
        input_path=source,
        output_dir=tmp_path / "raw",
        title="소융대 동아리",
        category="club",
        source="국민대 홈페이지",
        collected_at="2026-05-23",
    )

    text = output.read_text(encoding="utf-8")
    assert text.count("---") == 2
    assert "title: old" not in text
    assert "# 동아리" in text


def test_prepare_raw_document_rejects_binary_sources(tmp_path: Path) -> None:
    source = tmp_path / "capture.png"
    source.write_bytes(b"not-text")

    with pytest.raises(ValueError, match="extract text first"):
        prepare_raw_document(
            input_path=source,
            output_dir=tmp_path / "raw",
            title="캡처",
            category="general",
            source="사용자 제공",
        )


def test_slugify_keeps_korean_terms() -> None:
    assert slugify("AI 트랙 / 2025") == "ai-트랙-2025"
