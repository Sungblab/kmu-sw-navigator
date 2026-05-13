from datetime import date
from pathlib import Path

from app.services.wiki_compiler import compile_wiki, parse_raw_document, write_wiki


def write_raw(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_parse_raw_document_reads_frontmatter_and_body(tmp_path: Path) -> None:
    raw_path = tmp_path / "ai-roadmap.md"
    write_raw(
        raw_path,
        """---
title: AI 학습 로드맵
category: roadmap
source: 팀 정리
---

# AI 학습 로드맵

Python, 수학, 자료구조, 머신러닝 순서로 학습합니다.
""",
    )

    document = parse_raw_document(raw_path)

    assert document.slug == "ai-roadmap"
    assert document.title == "AI 학습 로드맵"
    assert document.category == "roadmap"
    assert document.source == "팀 정리"
    assert "머신러닝" in document.body


def test_compile_wiki_groups_documents_into_index_pages(tmp_path: Path) -> None:
    roadmap_path = tmp_path / "ai-roadmap.md"
    club_path = tmp_path / "clubs.md"
    write_raw(
        roadmap_path,
        """---
title: AI 학습 로드맵
category: roadmap
source: 팀 정리
---

# AI 학습 로드맵

Python, 수학, 자료구조, 머신러닝 순서로 학습합니다.
""",
    )
    write_raw(
        club_path,
        """---
title: 동아리 안내
category: club
source: 팀 정리
---

# 동아리 안내

개발 동아리, 알고리즘 스터디, 창업 활동을 탐색합니다.
""",
    )

    build = compile_wiki(
        [parse_raw_document(roadmap_path), parse_raw_document(club_path)],
        generated_at=date(2026, 5, 13),
    )

    assert [page.slug for page in build.pages] == ["club", "roadmap"]
    assert "[[club]]" in build.index_content
    assert "[[roadmap]]" in build.index_content
    assert "AI 학습 로드맵" in build.pages_by_slug["roadmap"].content
    assert "개발 동아리" in build.pages_by_slug["club"].content
    assert "2026-05-13" in build.log_content
    assert "2개 원문" in build.log_content


def test_write_wiki_creates_index_log_and_pages(tmp_path: Path) -> None:
    raw_path = tmp_path / "tracks.md"
    wiki_dir = tmp_path / "wiki"
    write_raw(
        raw_path,
        """---
title: 트랙 안내
category: track
source: 팀 정리
---

# 트랙 안내

AI, 웹, 보안 관심사별 트랙을 정리합니다.
""",
    )
    build = compile_wiki([parse_raw_document(raw_path)], generated_at=date(2026, 5, 13))

    write_wiki(build, wiki_dir)

    assert (wiki_dir / "_index.md").exists()
    assert (wiki_dir / "log.md").exists()
    assert (wiki_dir / "track.md").exists()
    assert "트랙 안내" in (wiki_dir / "track.md").read_text(encoding="utf-8")

