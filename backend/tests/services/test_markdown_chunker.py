from app.services.markdown_chunker import chunk_markdown


def test_chunk_markdown_preserves_heading_path_and_hash() -> None:
    text = """# 신입생 안내

## 수강신청

수강신청 전에는 졸업 요건, 전공 기초, 시간표 충돌 여부를 확인합니다.

## 학교 시스템

학교 포털, eCampus, 학사 공지를 매주 확인합니다.
"""

    chunks = chunk_markdown(text, max_chars=200)

    assert [chunk.chunk_index for chunk in chunks] == [0, 1]
    assert chunks[0].heading_path == "신입생 안내 > 수강신청"
    assert "졸업 요건" in chunks[0].content
    assert len(chunks[0].content_hash) == 64
    assert chunks[0].source_start < chunks[0].source_end
    assert chunks[0].token_count > 0


def test_chunk_markdown_splits_long_paragraph_under_same_heading() -> None:
    long_text = "가" * 130

    chunks = chunk_markdown(f"# 로드맵\n\n{long_text}", max_chars=50)

    assert len(chunks) == 3
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert {chunk.heading_path for chunk in chunks} == {"로드맵"}
    assert "".join(chunk.content for chunk in chunks) == long_text

