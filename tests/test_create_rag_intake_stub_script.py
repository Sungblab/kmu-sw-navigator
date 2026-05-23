from __future__ import annotations

from pathlib import Path

import pytest

from scripts.create_rag_intake_stub import (
    IntakeStubInput,
    build_intake_stub,
    default_output_path,
    normalize_argv,
    write_intake_stub,
)


def test_build_intake_stub_marks_photo_as_needing_transcript() -> None:
    stub = build_intake_stub(
        IntakeStubInput(
            source_file=Path("club-poster.png"),
            title="소프트웨어융합대학 동아리 포스터",
            category="club",
            source_name="국민대학교 소프트웨어융합대학",
            collected_at="2026-05-23",
        )
    )

    assert "원본 파일명 또는 URL: club-poster.png" in stub
    assert "RAG category: club" in stub
    assert "전사 상태: OCR 또는 수동 전사 필요" in stub


def test_build_intake_stub_marks_text_as_ready() -> None:
    stub = build_intake_stub(
        IntakeStubInput(
            source_file=Path("curriculum.txt"),
            title="소프트웨어학부 교과과정",
            category="curriculum",
            source_name="국민대학교 소프트웨어융합대학",
            collected_at="2026-05-23",
        )
    )

    assert "전사 상태: 텍스트 원본" in stub


def test_build_intake_stub_rejects_unknown_category() -> None:
    with pytest.raises(ValueError, match="unsupported RAG category"):
        build_intake_stub(
            IntakeStubInput(
                source_file=Path("source.pdf"),
                title="자료",
                category="unknown",
                source_name="국민대학교",
                collected_at="2026-05-23",
            )
        )


def test_default_output_path_sanitizes_filename() -> None:
    assert default_output_path(Path("AI curriculum 2026.pdf"), Path("data/inbox")) == Path(
        "data/inbox/AI-curriculum-2026-intake.md"
    )


def test_write_intake_stub_creates_file(tmp_path: Path) -> None:
    output = tmp_path / "intake.md"

    written = write_intake_stub(
        IntakeStubInput(
            source_file=Path("roadmap.pdf"),
            title="AI 트랙 로드맵",
            category="roadmap",
            source_name="국민대학교 소프트웨어융합대학",
            collected_at="2026-05-23",
        ),
        output,
    )

    assert written == output
    assert "AI 트랙 로드맵 접수" in output.read_text(encoding="utf-8")


def test_normalize_argv_accepts_pnpm_separator() -> None:
    assert normalize_argv(["--", "--file", "source.pdf"]) == ["--file", "source.pdf"]
