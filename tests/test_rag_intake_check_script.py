from __future__ import annotations

from pathlib import Path

from scripts.check_rag_intake import (
    build_prepare_raw_command,
    check_intake_file,
    check_intake_tree,
    format_results,
)


VALID_INTAKE = """# 인공지능학부 교과과정 접수

- 자료 제목: 인공지능학부 교과과정
- 원본 파일명 또는 URL: https://cs.kookmin.ac.kr/ai/major
- 공식 출처명: 국민대학교 소프트웨어융합대학 홈페이지
- 수집일: 2026-05-23
- 담당자가 확인한 날짜: 2026-05-23
- 적용 대상: 인공지능학부
- 대상 학년: 전체
- RAG category: curriculum

## 정형화할 핵심 필드

- 과목명: 프로그래밍
- 학생에게 추천할 상황: AI 전공 1학년이 첫 학기 과목을 물을 때
"""


def test_check_intake_file_accepts_filled_template(tmp_path: Path) -> None:
    intake = tmp_path / "ai-curriculum.md"
    intake.write_text(VALID_INTAKE, encoding="utf-8")

    result = check_intake_file(intake)

    assert result.errors == []
    assert result.warnings == []


def test_check_intake_file_rejects_missing_required_field(tmp_path: Path) -> None:
    intake = tmp_path / "club.md"
    intake.write_text(VALID_INTAKE.replace("공식 출처명: 국민대학교 소프트웨어융합대학 홈페이지", "공식 출처명:"), encoding="utf-8")

    result = check_intake_file(intake)

    assert "missing or empty field: 공식 출처명" in result.errors


def test_check_intake_file_rejects_unknown_category(tmp_path: Path) -> None:
    intake = tmp_path / "career.md"
    intake.write_text(VALID_INTAKE.replace("RAG category: curriculum", "RAG category: unknown"), encoding="utf-8")

    result = check_intake_file(intake)

    assert "unsupported RAG category: unknown" in result.errors


def test_check_intake_file_flags_personal_info_risk(tmp_path: Path) -> None:
    intake = tmp_path / "private.md"
    intake.write_text(VALID_INTAKE + "\n학생 연락처: 010-1234-5678\n", encoding="utf-8")

    result = check_intake_file(intake)

    assert "possible personal phone number" in result.errors


def test_check_intake_tree_skips_templates(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "README.md").write_text("학생 연락처: 010-1234-5678", encoding="utf-8")
    (inbox / "source-intake-template.md").write_text("자료 제목:", encoding="utf-8")

    results = check_intake_tree(inbox)

    assert results == []


def test_build_prepare_raw_command_uses_checked_metadata(tmp_path: Path) -> None:
    intake = tmp_path / "ai curriculum.md"
    intake.write_text(VALID_INTAKE, encoding="utf-8")
    result = check_intake_file(intake)

    command = build_prepare_raw_command(result)

    assert command == (
        'pnpm rag:prepare-raw --input "../data/inbox/ai curriculum.md" '
        '--title "인공지능학부 교과과정" --category curriculum '
        '--source "국민대학교 소프트웨어융합대학 홈페이지" --collected-at 2026-05-23'
    )


def test_format_results_prints_prepare_command_for_ready_file(tmp_path: Path) -> None:
    intake = tmp_path / "club.md"
    intake.write_text(VALID_INTAKE.replace("curriculum", "club"), encoding="utf-8")

    output = "\n".join(format_results([check_intake_file(intake)]))

    assert "prepare:" in output
    assert "pnpm rag:prepare-raw" in output
