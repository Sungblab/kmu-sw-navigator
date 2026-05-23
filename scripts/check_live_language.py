from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ACTIVE_DOC_PATHS = (
    Path("README.md"),
    Path("docs/README.md"),
    Path("docs/product"),
    Path("docs/report"),
    Path("docs/architecture"),
    Path("docs/testing"),
    Path("docs/contributing"),
)

BANNED_TERMS = ("demo", "mock", "데모", "목업")


@dataclass(frozen=True)
class Match:
    path: Path
    line_number: int
    term: str
    line: str


def iter_active_docs(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for relative in ACTIVE_DOC_PATHS:
        path = repo_root / relative
        if path.is_file():
            paths.append(path)
        elif path.is_dir():
            paths.extend(sorted(path.rglob("*.md")))
    return paths


def find_live_language_violations(repo_root: Path) -> list[Match]:
    matches: list[Match] = []
    for path in iter_active_docs(repo_root):
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
    matches = find_live_language_violations(repo_root)
    if matches:
        print("활성 문서 live language 체크 실패:")
        for match in matches:
            print(f"- {match.path}:{match.line_number} contains {match.term!r}: {match.line}")
        return 1

    print("활성 문서 live language 체크 완료: 시연/제품 설명이 live 기준으로 정렬됨")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
