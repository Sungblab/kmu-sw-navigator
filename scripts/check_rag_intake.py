from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

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
SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt"}
SKIP_FILENAMES = {"README.md", "source-intake-template.md"}
REQUIRED_FIELDS = (
    "자료 제목",
    "원본 파일명 또는 URL",
    "공식 출처명",
    "수집일",
    "적용 대상",
    "대상 학년",
    "RAG category",
)
PERSONAL_INFO_PATTERNS = (
    ("possible personal phone number", re.compile(r"01[016789][-\s]?\d{3,4}[-\s]?\d{4}")),
    ("possible personal email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("possible student id", re.compile(r"\b20\d{6,8}\b")),
)


@dataclass(frozen=True)
class IntakeCheckResult:
    path: Path
    errors: list[str]
    warnings: list[str]

    @property
    def passed(self) -> bool:
        return not self.errors


def extract_field(text: str, label: str) -> str | None:
    pattern = re.compile(
        rf"^[^\S\r\n]*(?:[-*][^\S\r\n]*)?{re.escape(label)}[^\S\r\n]*:[^\S\r\n]*([^\r\n]+)[^\S\r\n]*$",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip().strip("`")
    return value or None


def check_intake_file(path: Path) -> IntakeCheckResult:
    errors: list[str] = []
    warnings: list[str] = []

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        errors.append("unsupported file type: extract PDF/photo text to .txt or .md first")
        return IntakeCheckResult(path=path, errors=errors, warnings=warnings)

    text = path.read_text(encoding="utf-8")
    for field in REQUIRED_FIELDS:
        if not extract_field(text, field):
            errors.append(f"missing or empty field: {field}")

    category = extract_field(text, "RAG category")
    if category and category not in VALID_CATEGORIES:
        errors.append(f"unsupported RAG category: {category}")

    for message, pattern in PERSONAL_INFO_PATTERNS:
        if pattern.search(text):
            errors.append(message)

    if "공식 출처 확인 필요" in text:
        warnings.append("source requires official verification")

    return IntakeCheckResult(path=path, errors=errors, warnings=warnings)


def check_intake_tree(inbox_dir: Path) -> list[IntakeCheckResult]:
    if not inbox_dir.exists():
        return []
    results: list[IntakeCheckResult] = []
    for path in sorted(item for item in inbox_dir.iterdir() if item.is_file()):
        if path.name in SKIP_FILENAMES:
            continue
        results.append(check_intake_file(path))
    return results


def format_results(results: list[IntakeCheckResult]) -> list[str]:
    lines = ["RAG intake check", ""]
    if not results:
        lines.append("No intake source files found.")
        return lines

    for result in results:
        status = "ready" if result.passed else "blocked"
        lines.append(f"- [{status}] {result.path.as_posix()}")
        for error in result.errors:
            lines.append(f"  error: {error}")
        for warning in result.warnings:
            lines.append(f"  warning: {warning}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate data/inbox source intake files before RAG normalization."
    )
    parser.add_argument("--inbox-dir", type=Path, default=Path("data/inbox"))
    args = parser.parse_args()

    results = check_intake_tree(args.inbox_dir)
    print("\n".join(format_results(results)))
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
