# Gemini Embedding Service Plan

> **For agentic workers:** 이 plan은 RAG chunk에 Gemini embedding을 붙일 수 있게 한 구현 기록이다.

**Goal:** `document_chunks` payload에 768차원 Gemini embedding을 붙일 수 있는 service adapter와 ingest 옵션을 추가한다.

## Implemented Scope

- `backend/app/services/embedding_service.py`를 추가했다.
- `GeminiEmbeddingService`가 `google-genai`의 `models.embed_content()`를 사용해 embedding을 생성한다.
- `DeterministicEmbeddingService`를 추가해 외부 API 없이 테스트에서 embedding shape를 검증한다.
- `validate_embeddings()`로 embedding 차원 mismatch를 즉시 실패 처리한다.
- `attach_embeddings_to_payloads()`가 title, heading_path, content를 묶어 embedding 입력을 만든다.
- `backend/app/scripts/ingest_documents.py`에 `--with-embeddings` 옵션을 추가했다.
- `pnpm rag:ingest:embeddings` 명령을 추가했다.

## Core Logic Notes

- embedding 입력에 title과 heading path를 포함해 짧은 chunk도 검색 맥락을 잃지 않게 했다.
- output dimensionality는 설정값 `GEMINI_EMBEDDING_DIM=768`을 따른다.
- 테스트용 deterministic embedding은 실제 검색 품질용이 아니라 Python 흐름, 차원 검증, payload 연결을 재현하기 위한 fallback이다.
- Gemini API 키가 없으면 embedding ingest는 실패하고, embedding 없는 dry-run/일반 ingest는 계속 사용할 수 있다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_embedding_service.py -q
cd ..
pnpm rag:ingest:dry
pnpm rag:ingest:embeddings
pnpm lint:backend
```

결과:

- `tests\services\test_embedding_service.py`: 3 passed
- `pnpm rag:ingest:dry`: documents=8, chunks=36, wiki_chunks=24, raw_chunks=12, embedded_chunks=0
- `pnpm rag:ingest:embeddings`: 현재 `.env`가 없어 `GEMINI_API_KEY is required for embeddings.` 메시지 후 종료
- `pnpm lint:backend`: All checks passed

## Remaining Work

- 실제 `GEMINI_API_KEY`를 넣고 `pnpm gemini:smoke`와 live embedding ingest를 수행한다.
- Supabase `document_chunks.embedding`에 vector가 들어간 뒤 `match_document_chunks` RPC를 smoke test한다.
- `/api/chat`에서 질문 embedding을 생성하고 vector/text retrieval을 호출한다.
