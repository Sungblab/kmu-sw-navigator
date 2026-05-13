from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvidenceCheck:
    requirement: str
    paths: tuple[str, ...]
    keywords: tuple[str, ...] = ()


CHECKS = (
    EvidenceCheck(
        "사용자 입력",
        (
            "frontend/src/App.tsx",
            "backend/app/api/chat.py",
            "backend/app/api/assignments.py",
            "backend/app/api/recommendations.py",
        ),
    ),
    EvidenceCheck(
        "조건문",
        (
            "backend/app/services/memory_service.py",
            "backend/app/services/chat_contract_service.py",
            "backend/app/services/recommendation_service.py",
            "backend/app/services/assignment_service.py",
        ),
        ("if ",),
    ),
    EvidenceCheck(
        "반복문",
        (
            "backend/app/services/retrieval_service.py",
            "backend/app/services/recommendation_service.py",
            "backend/app/services/document_ingest.py",
        ),
        ("for ",),
    ),
    EvidenceCheck(
        "함수",
        (
            "backend/app/services/chat_contract_service.py",
            "backend/app/services/recommendation_service.py",
            "backend/app/services/assignment_service.py",
            "backend/app/services/calendar_service.py",
        ),
        ("def ",),
    ),
    EvidenceCheck(
        "리스트/딕셔너리",
        (
            "backend/app/services/recommendation_service.py",
            "backend/app/schemas/chat.py",
            "backend/app/schemas/assignment.py",
        ),
        ("list[", "dict[", "TRACK_RULES", "ACTIVITY_RULES"),
    ),
    EvidenceCheck(
        "의미 있는 출력",
        (
            "backend/app/schemas/chat.py",
            "backend/app/schemas/recommendation.py",
            "backend/app/schemas/assignment.py",
            "backend/app/schemas/calendar.py",
        ),
    ),
    EvidenceCheck(
        "실행 가능한 Python 코드",
        ("backend/app/main.py", "backend/tests/test_health.py", "backend/pyproject.toml"),
    ),
    EvidenceCheck(
        "LLM 활용 기록",
        (
            "docs/llm/usage-log.md",
            "backend/app/api/llm_logs.py",
            "backend/app/services/llm_usage_log_service.py",
        ),
    ),
)


def check_evidence(repo_root: Path) -> list[str]:
    failures: list[str] = []
    for check in CHECKS:
        missing_paths = [path for path in check.paths if not (repo_root / path).exists()]
        if missing_paths:
            failures.append(f"{check.requirement}: missing paths: {', '.join(missing_paths)}")
            continue

        if check.keywords and not _any_keyword_exists(repo_root, check.paths, check.keywords):
            failures.append(
                f"{check.requirement}: missing keywords: {', '.join(check.keywords)}"
            )
    return failures


def _any_keyword_exists(repo_root: Path, paths: tuple[str, ...], keywords: tuple[str, ...]) -> bool:
    for path in paths:
        content = (repo_root / path).read_text(encoding="utf-8")
        if any(keyword in content for keyword in keywords):
            return True
    return False


def main() -> int:
    repo_root = Path.cwd()
    failures = check_evidence(repo_root)
    if failures:
        print("제출 증거 체크 실패:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"제출 조건 증거 {len(CHECKS)}개 확인 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
