from __future__ import annotations

from pathlib import Path

from scripts.check_submission_evidence import CHECKS, check_evidence


def test_submission_evidence_checks_current_repo() -> None:
    assert check_evidence(Path.cwd()) == []
    assert {check.requirement for check in CHECKS} == {
        "사용자 입력",
        "조건문",
        "반복문",
        "함수",
        "리스트/딕셔너리",
        "의미 있는 출력",
        "실행 가능한 Python 코드",
        "LLM 활용 기록",
    }
