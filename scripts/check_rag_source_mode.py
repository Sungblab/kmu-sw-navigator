from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


CHECK_PATHS = (
    Path("data/raw"),
    Path("data/wiki"),
    Path("supabase/seed.sql"),
)

BANNED_TERMS = (
    "데모용",
    "demo",
    "mock",
    "목업",
)


@dataclass(frozen=True)
class Match:
    path: Path
    line_number: int
    term: str
    line: str


def find_rag_source_violations(repo_root: Path) -> list[Match]:
    matches: list[Match] = []
    for target in CHECK_PATHS:
        path = repo_root / target
        files = path.rglob("*") if path.is_dir() else (path,)
        for file_path in files:
            if not file_path.is_file() or file_path.suffix.lower() not in {".md", ".sql"}:
                continue
            relative_path = file_path.relative_to(repo_root)
            text = file_path.read_text(encoding="utf-8")
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
    matches = find_rag_source_violations(repo_root)
    if matches:
        print("RAG source mode 체크 실패:")
        for match in matches:
            print(_format_match(match))
        return 1

    print("RAG source mode 체크 완료: data/seed에 샘플 전용 출처 표현 없음")
    return 0


def _format_match(match: Match) -> str:
    line = match.line.encode("cp949", errors="backslashreplace").decode("cp949")
    return f"- {match.path}:{match.line_number} contains {match.term!r}: {line}"


if __name__ == "__main__":
    raise SystemExit(main())
