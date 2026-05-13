# Local RAG Retrieval Chat Plan

> **For agentic workers:** 이 plan은 `/api/chat`이 placeholder가 아니라 local raw/wiki chunk 검색 결과를 evidence로 반환하게 만든 기록이다.

**Goal:** Supabase vector/RPC 연결 전에도 `data/wiki`, `data/raw` Markdown chunk를 검색해 chat response의 `evidence.internal_sources`에 실제 근거를 넣는다.

## Implemented Scope

- `backend/app/services/retrieval_service.py`를 추가했다.
- `LocalDocumentRetriever`가 ingest payload를 받아 query term 기반으로 chunk를 scoring한다.
- 같은 점수면 `wiki_page`를 `raw_document`보다 우선한다.
- `RetrievalResult.to_evidence()`로 chat schema에 들어갈 evidence dict를 만든다.
- `backend/app/api/dependencies.py`에 local retriever dependency를 추가했다.
- `backend/app/api/chat.py`가 질문마다 retriever를 호출해 `build_chat_response()`에 전달한다.
- `backend/app/services/chat_contract_service.py`의 academic placeholder source를 실제 retrieval 결과로 교체했다.

## Core Logic Notes

- 현재 retriever는 DB 없이 동작하는 fallback이다. Supabase vector search가 준비되면 같은 `RetrievalResult` 형태로 adapter를 교체한다.
- source score가 같으면 Mini Wiki를 우선한다. 이는 원문을 바로 답변에 쓰기보다 신입생용으로 정리된 wiki를 먼저 본다는 제품 정책이다.
- 검색어는 한글/영문/숫자 토큰으로 단순 추출한다. 복잡한 의미 검색은 embedding/vector slice에서 맡는다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_retrieval_service.py tests\api\test_chat_contract_api.py -q
cd ..
pnpm lint:backend
```

결과:

- focused retrieval/chat tests: 6 passed
- `pnpm lint:backend`: All checks passed

## Remaining Work

- Supabase `search_document_chunks_text` RPC adapter를 추가한다.
- Supabase `match_document_chunks` vector adapter를 추가한다.
- Gemini 답변 생성 단계에서 retrieved evidence를 context로 사용한다.
