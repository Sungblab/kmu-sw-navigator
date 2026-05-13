# RAG Document Ingest Plan

> **For agentic workers:** 이 plan은 raw/wiki Markdown을 `document_chunks` payload로 변환하는 RAG ingest 기반 구현 기록이다.

**Goal:** Mini LLM Wiki와 raw markdown을 heading-aware chunk로 나누고, Supabase `document_chunks`에 넣을 수 있는 payload를 만든다.

## Implemented Scope

- `backend/app/services/document_ingest.py`를 추가했다.
- `data/raw/*.md`를 `raw_document` source로 읽는다.
- `data/wiki/*.md` 중 `_index.md`, `log.md`를 제외한 파일을 `wiki_page` source로 읽는다.
- `chunk_markdown()`을 재사용해 `heading_path`, `content_hash`, `token_count`, 원문 위치 metadata를 보존한다.
- `backend/app/scripts/ingest_documents.py`를 추가했다.
- `pnpm rag:ingest:dry`와 `pnpm rag:ingest` 명령을 추가했다.
- 현재 1차 ingest는 embedding 없이 text search/RAG 근거 chunk를 먼저 채운다.

## Core Logic Notes

- `source_type`을 `wiki_page`와 `raw_document`로 분리해 검색 단계에서 wiki 우선, raw 보강 정책을 적용할 수 있게 했다.
- `heading_path`는 답변 근거가 어느 문단에서 왔는지 설명하기 위한 필드다.
- `content_hash`는 후속 embedding 재생성 slice에서 같은 내용인지 판단하는 기준으로 쓴다.
- `metadata`에는 파일 slug, path, source offset, token count를 넣어 발표와 디버깅에서 추적 가능하게 했다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_document_ingest.py -q
cd ..
pnpm rag:ingest:dry
pnpm lint:backend
```

결과:

- `tests\services\test_document_ingest.py`: 2 passed
- `pnpm rag:ingest:dry`: documents=8, chunks=36, wiki_chunks=24, raw_chunks=12
- `pnpm lint:backend`: All checks passed

## Remaining Work

- Gemini embedding service를 추가해 `document_chunks.embedding`을 채운다.
- Supabase env 설정 뒤 `pnpm rag:ingest`로 live insert smoke를 수행한다.
- `/api/chat`이 text/vector retrieval 결과를 실제 evidence에 넣게 한다.
