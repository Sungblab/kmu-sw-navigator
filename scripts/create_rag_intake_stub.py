from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
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
TEXT_READY_EXTENSIONS = {".md", ".markdown", ".txt"}


@dataclass(frozen=True)
class IntakeStubInput:
    source_file: Path
    title: str
    category: str
    source_name: str
    collected_at: str
    audience: str = "확인 필요"
    grade: str = "확인 필요"


def build_intake_stub(data: IntakeStubInput) -> str:
    if data.category not in VALID_CATEGORIES:
        raise ValueError(f"unsupported RAG category: {data.category}")

    transcript_status = (
        "텍스트 원본"
        if data.source_file.suffix.lower() in TEXT_READY_EXTENSIONS
        else "OCR 또는 수동 전사 필요"
    )
    return "\n".join(
        [
            f"# {data.title} 접수",
            "",
            f"- 자료 제목: {data.title}",
            f"- 원본 파일명 또는 URL: {data.source_file.name}",
            f"- 공식 출처명: {data.source_name}",
            f"- 수집일: {data.collected_at}",
            f"- 담당자가 확인한 날짜: {data.collected_at}",
            f"- 적용 대상: {data.audience}",
            f"- 대상 학년: {data.grade}",
            f"- RAG category: {data.category}",
            f"- 전사 상태: {transcript_status}",
            "",
            "## 정형화할 핵심 필드",
            "",
            "- 핵심 사실: 확인 필요",
            "- 학생에게 추천할 상황: 확인 필요",
            "- 근거 문장 또는 표 위치: 확인 필요",
            "",
            "## 전사/요약 내용",
            "",
            "원본 PDF/사진/캡처라면 여기부터 사람이 확인한 텍스트만 옮긴다.",
            "",
        ]
    )


def default_output_path(source_file: Path, output_dir: Path) -> Path:
    stem = re.sub(r"[^A-Za-z0-9가-힣._-]+", "-", source_file.stem).strip("-")
    return output_dir / f"{stem or 'source'}-intake.md"


def write_intake_stub(data: IntakeStubInput, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_intake_stub(data), encoding="utf-8")
    return output_path


def normalize_argv(argv: list[str]) -> list[str]:
    if argv and argv[0] == "--":
        return argv[1:]
    return argv


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a data/inbox intake metadata stub for a PDF, photo, capture, or text file."
    )
    parser.add_argument("--file", type=Path, required=True, help="Original source file path or name")
    parser.add_argument("--title", required=True)
    parser.add_argument("--category", required=True, choices=sorted(VALID_CATEGORIES))
    parser.add_argument("--source", required=True, help="Official source name or document owner")
    parser.add_argument("--collected-at", default=date.today().isoformat())
    parser.add_argument("--audience", default="확인 필요")
    parser.add_argument("--grade", default="확인 필요")
    parser.add_argument("--output-dir", type=Path, default=Path("data/inbox"))
    args = parser.parse_args(normalize_argv(sys.argv[1:]))

    source_file = args.file
    output_path = default_output_path(source_file, args.output_dir)
    written = write_intake_stub(
        IntakeStubInput(
            source_file=source_file,
            title=args.title,
            category=args.category,
            source_name=args.source,
            collected_at=args.collected_at,
            audience=args.audience,
            grade=args.grade,
        ),
        output_path,
    )
    print(f"RAG intake stub written: {written}")
    print("Next: fill 핵심 필드/전사 내용, then run pnpm rag:intake-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
