from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


RUNTIME_ROOTS = (
    Path("frontend/src"),
    Path("backend/app"),
)

BANNED_TERMS = (
    "demo-user",
    "x-user-id",
    "mock",
    "목업",
    "데모",
)


@dataclass(frozen=True)
class Match:
    path: Path
    line_number: int
    term: str
    line: str


def find_runtime_product_mode_violations(repo_root: Path) -> list[Match]:
    matches: list[Match] = []
    for root in RUNTIME_ROOTS:
        for path in (repo_root / root).rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py", ".ts", ".tsx", ".css"}:
                continue
            relative_path = path.relative_to(repo_root)
            text = path.read_text(encoding="utf-8")
            for index, line in enumerate(text.splitlines(), start=1):
                normalized = line.lower()
                for term in BANNED_TERMS:
                    if term in normalized:
                        matches.append(
                            Match(
                                path=relative_path,
                                line_number=index,
                                term=term,
                                line=line.strip(),
                            )
                        )
    return matches


def main() -> int:
    repo_root = Path.cwd()
    matches = find_runtime_product_mode_violations(repo_root)
    if matches:
        print("런타임 product mode 체크 실패:")
        for match in matches:
            print(f"- {match.path}:{match.line_number} contains {match.term!r}: {match.line}")
        return 1

    print("런타임 product mode 체크 완료: 우회 인증/샘플 전용 fallback 표현 없음")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
