# Supabase Vector Retrieval Adapter Plan

> **For agentic workers:** 이 plan은 질문 embedding을 만들어 `match_document_chunks` RPC로 검색하는 vector retrieval adapter 구현 기록이다.

**Goal:** Supabase와 Gemini env가 모두 있으면 `/api/chat`에서 질문을 embedding하고 `match_document_chunks` vector RPC를 사용한다. env가 부족하면 Supabase text RPC 또는 local fallback을 유지한다.

## Implemented Scope

- `backend/app/services/retrieval_service.py`에 `SupabaseVectorRetriever`를 추가했다.
- 질문은 `RETRIEVAL_QUERY` task type으로 embedding한다.
- `match_document_chunks` RPC에 `query_embedding`, `match_count`, `match_threshold`, `filter_source_type`을 전달한다.
- RPC의 `similarity` 값을 `RetrievalResult.score`로 매핑한다.
- `backend/app/api/dependencies.py`가 env 상태에 따라 retriever를 선택한다.
  - Supabase + Gemini key 있음: `SupabaseVectorRetriever`
  - Supabase만 있음: `SupabaseTextRetriever`
  - Supabase 없음: `LocalDocumentRetriever`
- fake embedding service와 fake RPC client 테스트를 추가했다.

## Core Logic Notes

- vector retrieval은 실제 의미 검색 경로다.
- text retrieval은 Gemini key가 없거나 embedding ingest가 준비되지 않은 상황의 DB fallback이다.
- local retrieval은 Supabase env가 없는 발표/테스트 fallback이다.
- 세 경로 모두 `RetrievalResult`를 반환하므로 frontend evidence와 chat contract는 바뀌지 않는다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_retrieval_service.py tests\api\test_chat_contract_api.py -q
cd ..
pnpm lint:backend
```

결과:

- focused retrieval/chat tests: 8 passed
- `pnpm lint:backend`: All checks passed

## Remaining Work

- 실제 Supabase `document_chunks.embedding` 데이터와 Gemini key로 live vector RPC smoke를 수행한다.
- retrieved evidence를 Gemini answer generation prompt에 넣는다.
- Google grounding은 career/startup 최신 정보 intent에만 별도 연결한다.
