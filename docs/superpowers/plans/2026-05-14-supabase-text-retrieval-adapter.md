# Supabase Text Retrieval Adapter Plan

> **For agentic workers:** 이 plan은 local RAG retriever 위에 Supabase `search_document_chunks_text` RPC adapter를 붙인 기록이다.

**Goal:** Supabase env가 있으면 `/api/chat`이 DB의 `document_chunks`를 RPC로 검색하고, env가 없으면 local Markdown retriever를 fallback으로 사용한다.

## Implemented Scope

- `backend/app/services/retrieval_service.py`에 `SupabaseTextRetriever`를 추가했다.
- `SupabaseTextRetriever.search()`가 `search_document_chunks_text` RPC를 호출한다.
- RPC row를 `RetrievalResult`로 변환해 local retriever와 같은 evidence 형태를 유지한다.
- `backend/app/api/dependencies.py`에 `get_document_retriever()`를 추가했다.
- Supabase backend env가 있으면 `SupabaseTextRetriever`, 없으면 `LocalDocumentRetriever`를 반환한다.
- `/api/chat` dependency를 `get_document_retriever()`로 교체했다.
- fake RPC client 테스트를 추가했다.

## Core Logic Notes

- 검색 결과 evidence schema는 local/Supabase 경로가 같다.
- DB RPC의 SQL 정렬에서 `wiki_page`가 `raw_document`보다 우선된다.
- live Supabase가 없을 때도 같은 Markdown 자료로 fallback 검색을 유지해 발표와 테스트가 중단되지 않는다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_retrieval_service.py tests\api\test_chat_contract_api.py -q
cd ..
pnpm lint:backend
```

결과:

- focused retrieval/chat tests: 7 passed
- `pnpm lint:backend`: All checks passed

## Remaining Work

- Supabase env와 `document_chunks` data를 넣은 뒤 live RPC smoke를 수행한다.
- `match_document_chunks` vector retrieval adapter를 추가한다.
- Gemini answer generation에서 retrieval evidence를 context로 사용한다.
