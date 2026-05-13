# LLM Usage Log API Plan

> **For agentic workers:** 이 plan은 앱 내부 LLM 사용 기록을 `llm_usage_logs` 저장소와 화면에 연결한 구현 기록이다.

**Goal:** Gemini 기반 답변 생성처럼 앱 내부에서 LLM을 사용하는 경로를 사용자별 로그로 남기고, `LLM 기록` 화면과 API에서 확인할 수 있게 한다.

## Implemented Scope

- `backend/app/schemas/llm_usage.py`를 추가했다.
- `backend/app/services/llm_usage_log_service.py`에 in-memory log store를 추가했다.
- `backend/app/services/store_protocols.py`에 `LLMUsageLogStore` protocol을 추가했다.
- `backend/app/services/supabase_stores.py`에 `SupabaseLLMUsageLogStore`를 추가했다.
- `supabase/schema.sql`의 `llm_usage_logs`에 `metadata` jsonb column을 추가했다.
- `backend/app/api/llm_logs.py`에 `GET /api/llm-logs`를 추가했다.
- `/api/chat`에서 Gemini answer generator를 사용한 경우 `rag_chat` LLM usage log를 저장한다.
- `/api/chat`에서 Google grounding generator가 성공한 경우 `google_grounding` LLM usage log를 저장한다.
- `/api/assignments/preview`에서 Gemini 일정 parser가 성공한 경우 `schedule_parser` LLM usage log를 저장한다.
- `ingest_documents` CLI에 `--llm-log-user-id`를 추가해 embedding ingest 실행 요약을 `embedding_ingest` 로그로 남길 수 있게 했다.
- frontend `LLM 활용 기록` 화면이 `/api/llm-logs`를 조회해 앱 내부 LLM 기록을 표시한다.

## Core Logic Notes

- 로그 owner는 request body가 아니라 인증 dependency의 `user_id`로 정한다.
- in-memory fallback은 외부 DB 없이 발표 데모와 테스트를 재현하기 위한 경로다.
- Supabase adapter는 `user_id`로 조회 범위를 제한한다.
- 현재 자동 기록은 채팅 답변 생성, Google grounding, Gemini 일정 parser 경로에 연결했다.
- embedding ingest는 Supabase user id가 명시된 경우에만 기록한다. CLI 경로에서는 익명 실행이 가능하므로 임의 user id를 만들지 않는다.
- 개발 과정에서 Codex/ChatGPT/Gemini를 쓴 기록은 계속 `docs/llm/usage-log.md`에 남긴다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_llm_usage_log_service.py tests\api\test_llm_usage_logs_api.py -q
cd ..
pnpm test:backend
pnpm lint:backend
pnpm build:frontend
pnpm docs:check
```

결과:

- focused LLM usage log/assignment/ingest tests: 11 passed
- `pnpm test:backend`: 87 passed
- `pnpm lint:backend`: All checks passed
- `pnpm build:frontend`: Vite production build 통과

## Remaining Work

- Supabase live DB에서 `pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>`로 `llm_usage_logs` insert/list smoke를 수행한다.
