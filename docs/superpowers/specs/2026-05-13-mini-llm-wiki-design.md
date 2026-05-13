# Mini LLM Wiki Design

Status: approved for implementation
Date: 2026-05-13
Owner: 김성빈

## 목표

국민대 소프트웨어융합대학 신입생 자료를 원문 그대로만 chunking하지 않고, 신입생 질문에 맞게 정리된 Mini LLM Wiki 계층을 만든다.

## 배경

동아리 목록, 로드맵, 트랙 안내, 수강신청 안내는 양이 많고 구조가 다릅니다. 단순 vector 검색만 쓰면 정확한 이름 검색과 넓은 요약 질문 모두에서 품질이 흔들릴 수 있습니다. 따라서 raw source와 답변 사이에 지속적으로 갱신되는 wiki page 계층을 둡니다.

## 범위

이번 단계에서 구현하는 범위:

1. `data/raw/`와 `data/wiki/` 폴더 구조
2. raw markdown을 category별 wiki page로 컴파일하는 Python 코드
3. heading-aware markdown chunking
4. Supabase schema에 raw/wiki/chunk 메타데이터 반영
5. 문서와 LLM 활용 기록 갱신

이번 단계에서 제외하는 범위:

- 실제 Gemini API로 위키 자동 재작성
- PDF/HWP/웹 크롤링 ingest
- 앱 UI에서 위키 페이지 편집
- graph visualization

## 아키텍처

```txt
data/raw/*.md
-> backend/app/services/wiki_compiler.py
-> data/wiki/*.md
-> backend/app/services/markdown_chunker.py
-> Supabase document_chunks
-> RAG chat
```

## 데이터 모델

- `raw_documents`: 원문 자료 메타데이터
- `wiki_pages`: 컴파일된 위키 페이지
- `wiki_logs`: 위키 재생성 기록
- `document_chunks`: raw/wiki 공통 chunk 저장소

`document_chunks.source_type`은 `raw_document` 또는 `wiki_page`입니다. 검색 정책은 `wiki_page`를 우선하고, 근거 보강이 필요하면 `raw_document`를 함께 사용합니다.

## 오류 처리

- raw markdown에 제목이 없으면 파일명을 제목으로 사용합니다.
- frontmatter가 없어도 실행됩니다.
- 빈 문서는 wiki 생성에서 제외합니다.
- 같은 slug가 반복되면 category 단위로 병합합니다.

## 테스트 기준

- raw markdown metadata 파싱
- heading-aware chunking
- category별 wiki page 생성
- `_index.md`와 `log.md` 생성
- CLI dry run 없이 실제 `data/wiki/` 재생성

