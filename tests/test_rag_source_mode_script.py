from __future__ import annotations

from pathlib import Path

from scripts.check_rag_source_mode import find_rag_source_violations


def test_rag_source_mode_checks_current_repo() -> None:
    assert find_rag_source_violations(Path.cwd()) == []


def test_rag_source_mode_detects_demo_source(tmp_path: Path) -> None:
    raw_dir = tmp_path / "data" / "raw"
    wiki_dir = tmp_path / "data" / "wiki"
    supabase_dir = tmp_path / "supabase"
    raw_dir.mkdir(parents=True)
    wiki_dir.mkdir(parents=True)
    supabase_dir.mkdir()
    (raw_dir / "bad.md").write_text("source: 데모용 샘플 자료\n", encoding="utf-8")
    (wiki_dir / "ok.md").write_text("source: 팀 정리 초안\n", encoding="utf-8")
    (supabase_dir / "seed.sql").write_text("-- seed\n", encoding="utf-8")

    matches = find_rag_source_violations(tmp_path)

    assert [(match.path.as_posix(), match.term) for match in matches] == [
        ("data/raw/bad.md", "데모용")
    ]
