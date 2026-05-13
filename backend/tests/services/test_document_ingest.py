from pathlib import Path

from app.services.document_ingest import build_document_chunk_payloads, load_ingest_documents


def test_load_ingest_documents_reads_raw_and_wiki_sources(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    wiki_dir = tmp_path / "wiki"
    raw_dir.mkdir()
    wiki_dir.mkdir()
    (raw_dir / "track.md").write_text(
        """---
title: 트랙 안내
category: track
source: 팀 정리
---

# 트랙 안내

AI 트랙은 Python과 자료구조를 먼저 본다.
""",
        encoding="utf-8",
    )
    (wiki_dir / "track.md").write_text(
        """---
slug: track
category: track
---

# 트랙 위키

신입생 질문에는 위키를 먼저 검색한다.
""",
        encoding="utf-8",
    )
    (wiki_dir / "_index.md").write_text("# index", encoding="utf-8")
    (wiki_dir / "log.md").write_text("# log", encoding="utf-8")

    documents = load_ingest_documents(raw_dir, wiki_dir)

    assert [document.source_type for document in documents] == ["raw_document", "wiki_page"]
    assert documents[0].title == "트랙 안내"
    assert documents[1].title == "트랙 위키"
    assert documents[1].source == "Mini LLM Wiki"


def test_build_document_chunk_payloads_preserves_rag_metadata(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    wiki_dir = tmp_path / "wiki"
    raw_dir.mkdir()
    wiki_dir.mkdir()
    (raw_dir / "freshman.md").write_text(
        """---
title: 신입생 안내
category: freshman
source: 팀 정리
---

# 신입생 안내

## 수강신청

수강신청 전에는 졸업 요건과 시간표 충돌 여부를 확인한다.
""",
        encoding="utf-8",
    )

    payloads = build_document_chunk_payloads(
        load_ingest_documents(raw_dir, wiki_dir),
        max_chars=200,
    )

    assert len(payloads) == 1
    payload = payloads[0]
    assert payload["source_type"] == "raw_document"
    assert payload["title"] == "신입생 안내"
    assert payload["category"] == "freshman"
    assert payload["heading_path"] == "신입생 안내 > 수강신청"
    assert payload["embedding"] is None
    assert payload["metadata"]["slug"] == "freshman"
    assert payload["metadata"]["token_count"] > 0
