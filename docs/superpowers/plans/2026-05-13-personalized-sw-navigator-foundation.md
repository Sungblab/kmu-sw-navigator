# Personalized SW Navigator Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first vertical slice for the personalized SW navigator: profile storage, user memory storage, memory events, and the first chat response contract that can expose personalization evidence.

**Architecture:** Keep this slice backend-first and schema-first. Add Supabase tables/RLS, FastAPI schemas/routes/services, focused backend tests, then connect the frontend after the API contract is stable.

**Tech Stack:** FastAPI, Pydantic, Supabase Postgres/pgvector, Gemini embedding, React + Vite + TypeScript, pnpm, uv, pytest.

---

## Implementation Result

2026-05-13에 `feature/profile-memory-foundation` 브랜치에서 backend-first로 구현했다.

구현된 범위:

- `supabase/schema.sql`에 `profiles`, `chat_sessions`, `chat_messages`, `user_memories`, `memory_events`, `google_oauth_tokens`, assignment Calendar fields, 사용자 소유 테이블 RLS policy를 추가했다.
- `backend/app/schemas/`에 profile, memory, chat contract Pydantic 모델을 추가했다.
- `backend/app/services/memory_service.py`에 deterministic 메모리 민감도 정책, candidate/confirm/reject/archive/update 흐름, 이벤트 기록을 추가했다.
- `backend/app/api/`에 `/api/profile`, `/api/memories`, `/api/chat` 라우터와 테스트용 user dependency를 추가했다.
- `backend/app/services/chat_contract_service.py`에 Gemini/RAG 연결 전 deterministic intent fallback과 evidence/choice 응답 contract를 추가했다.
- `frontend/src/`에 API 타입/client, Home page, Records page, 실제 앱 shell을 추가했다.
- Windows `uv run pytest` console-script canonicalize 문제를 피하기 위해 root scripts를 `uv run python -m ...` 형태로 정리했다.
- 메모리 민감도 정책, 메모리 이벤트 기록, chat intent fallback, Chat contract 근거 슬롯에 발표용 의도 주석을 추가했다.
- `docs/architecture/python-core-logic.md`에 핵심 Python 로직의 판단 이유와 현재 한계를 정리했다.

검증 결과:

```powershell
pnpm docs:check
pnpm test:backend
pnpm lint:backend
pnpm build:frontend
```

결과: `pnpm docs:check`, `pnpm wiki:build`, `pnpm test:backend`, `pnpm lint:backend`, `pnpm build:frontend`가 통과했다. 중간에 `uv run pytest`와 기존 `pnpm test:backend`는 console-script shim 문제로 실패했지만, `uv run python -m pytest`로 root script를 수정한 뒤 `pnpm test:backend`가 Python 3.12.11 환경에서 22개 테스트 통과로 복구됐다.

남은 범위:

- 현재 profile/memory 저장소는 Supabase adapter 전 단계의 in-memory 구현이다.
- `/api/chat`은 실제 RAG/Gemini가 아니라 deterministic contract shell이다.
- 실제 Supabase JWT 검증, embedding 생성, RAG retrieval, Google grounding, 일정 저장/Calendar export는 후속 plan에서 구현한다.

---

## File Structure

Create or modify these files during implementation:

- Modify: `supabase/schema.sql` for `profiles`, `chat_sessions`, `chat_messages`, `user_memories`, `memory_events`, `google_oauth_tokens`, assignment calendar fields, and RLS policies.
- Create: `backend/app/schemas/profile.py` for profile request/response models.
- Create: `backend/app/schemas/memory.py` for memory and memory event models.
- Create: `backend/app/schemas/chat.py` for chat request/response/evidence contracts.
- Create: `backend/app/services/profile_service.py` for profile CRUD.
- Create: `backend/app/services/memory_service.py` for memory candidate persistence, sensitivity policy, and event logging.
- Create: `backend/app/services/chat_contract_service.py` for deterministic MVP chat response assembly before full Gemini/RAG integration.
- Create: `backend/app/api/profile.py`, `backend/app/api/memories.py`, `backend/app/api/chat.py` for route boundaries.
- Modify: `backend/app/main.py` to include API routers.
- Create: `backend/tests/services/test_memory_service.py`.
- Create: `backend/tests/api/test_profile_api.py`.
- Create: `backend/tests/api/test_memory_api.py`.
- Create: `backend/tests/api/test_chat_contract_api.py`.
- Modify: `frontend/src/types/api.ts` after backend response shape is stable.
- Modify: `frontend/src/lib/api.ts` after backend response shape is stable.
- Create: `frontend/src/pages/HomePage.tsx` when starting frontend.
- Create: `frontend/src/pages/RecordsPage.tsx` when starting frontend.
- Modify: `docs/contributing/feature-registry.md`, `docs/contributing/plans-status.md`, and `docs/llm/usage-log.md` when the slice state changes.

## Task 1: Schema Foundation

**Files:**
- Modify: `supabase/schema.sql`

- [ ] **Step 1: Add tables and RLS to `supabase/schema.sql`**

Add tables for profile, chat, memory, memory events, and Google OAuth token storage. Keep token columns encrypted-at-rest by application code; this schema only stores encrypted strings.

Expected table names:

```sql
profiles
chat_sessions
chat_messages
user_memories
memory_events
google_oauth_tokens
```

Expected memory fields:

```sql
category text not null
key text not null
value_json jsonb not null default '{}'::jsonb
natural_text text not null
embedding vector(768)
embedding_status text not null default 'pending'
confidence numeric not null default 0.5
sensitivity text not null default 'low'
status text not null default 'active'
```

- [ ] **Step 2: Add assignment Calendar fields**

Add these columns to the existing assignment table or planned assignment table:

```sql
calendar_event_id text
calendar_synced_at timestamp with time zone
```

- [ ] **Step 3: Add RLS policies**

Every user-owned table must enable RLS and restrict rows by `auth.uid() = user_id`. `profiles.id` should match the Supabase Auth user id.

- [ ] **Step 4: Verify schema text**

Run:

```powershell
pnpm docs:check
```

Expected: required docs still pass. SQL execution against Supabase is done in a later DB-backed smoke.

## Task 2: Backend Schemas

**Files:**
- Create: `backend/app/schemas/profile.py`
- Create: `backend/app/schemas/memory.py`
- Create: `backend/app/schemas/chat.py`

- [ ] **Step 1: Create profile models**

Define Pydantic models for:

```txt
ProfileUpsertRequest
ProfileResponse
```

Fields:

```txt
department: software | ai | unknown | other
grade: 1 | 2 | 3 | 4
curriculum_year: 2023 | 2024 | 2025 | unknown
```

- [ ] **Step 2: Create memory models**

Define Pydantic models for:

```txt
MemoryResponse
MemoryEventResponse
MemoryUpdateRequest
```

Expose `natural_text`, `category`, `key`, `value_json`, `confidence`, `sensitivity`, `status`, and `embedding_status`. Do not expose raw embedding vectors to the frontend.

- [ ] **Step 3: Create chat contract models**

Define Pydantic models for:

```txt
ChatRequest
ChatAction
ChatEvidence
ChatResponse
ChoiceOption
```

`ChatResponse` must include:

```txt
answer: str
actions: list[ChatAction]
evidence: ChatEvidence
choices: list[ChoiceOption]
memory_updates: list[MemoryResponse]
needs_verification: list[str]
```

- [ ] **Step 4: Run backend import check**

Run:

```powershell
pnpm test:backend
```

Expected: existing health/wiki tests still pass or fail only because dependencies are not installed. If dependencies are missing, record the exact reason in `docs/llm/usage-log.md`.

## Task 3: Memory Service

**Files:**
- Create: `backend/app/services/memory_service.py`
- Test: `backend/tests/services/test_memory_service.py`

- [ ] **Step 1: Write tests for sensitivity policy**

Test cases:

```txt
"AI랑 백엔드 관심 있어" -> low sensitivity, auto save allowed
"학점이 낮아서 취업이 걱정돼" -> medium sensitivity, confirmation required
"내 비밀번호는 ..." -> high sensitivity, reject storing
```

- [ ] **Step 2: Implement `classify_memory_sensitivity()`**

Use deterministic Python keyword rules first. Gemini extraction can suggest candidates later, but Python owns the final policy gate.

- [ ] **Step 3: Write tests for memory event decisions**

Test:

```txt
auto_saved creates created event
confirmed_by_user creates confirmed event
rejected creates rejected event and no active memory
```

- [ ] **Step 4: Implement memory candidate persistence**

Implement service functions:

```txt
create_memory_candidate()
confirm_memory()
reject_memory()
archive_memory()
```

Embedding generation can be stubbed behind an interface in this task. If embedding is unavailable, set `embedding_status = pending`.

- [ ] **Step 5: Run focused tests**

Run:

```powershell
cd backend && uv run pytest tests/services/test_memory_service.py -q
```

Expected: memory service tests pass.

## Task 4: Profile and Memory APIs

**Files:**
- Create: `backend/app/api/profile.py`
- Create: `backend/app/api/memories.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/api/test_profile_api.py`
- Test: `backend/tests/api/test_memory_api.py`

- [ ] **Step 1: Add API tests with test user dependency override**

Use FastAPI dependency overrides so API tests do not require a live Supabase auth token.

Test profile endpoints:

```txt
GET /api/profile returns missing profile state
POST /api/profile stores required fields
PATCH /api/profile updates grade/curriculum_year
```

Test memory endpoints:

```txt
GET /api/memories returns active memories only
PATCH /api/memories/{id} updates natural_text/value_json
DELETE /api/memories/{id} archives memory
```

- [ ] **Step 2: Implement profile routes**

Routes:

```txt
GET /api/profile
POST /api/profile
PATCH /api/profile
```

- [ ] **Step 3: Implement memory routes**

Routes:

```txt
GET /api/memories
PATCH /api/memories/{memory_id}
DELETE /api/memories/{memory_id}
```

- [ ] **Step 4: Register routers**

Modify `backend/app/main.py` so routers are mounted under `/api`.

- [ ] **Step 5: Run API tests**

Run:

```powershell
cd backend && uv run pytest tests/api/test_profile_api.py tests/api/test_memory_api.py -q
```

Expected: profile and memory API tests pass.

## Task 5: Chat Contract MVP

**Files:**
- Create: `backend/app/services/chat_contract_service.py`
- Create: `backend/app/api/chat.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/api/test_chat_contract_api.py`

- [ ] **Step 1: Write chat contract tests**

Test:

```txt
POST /api/chat returns answer/actions/evidence/choices
academic question includes internal_sources evidence key
career question includes personalization evidence key
assignment sentence returns schedule choice
```

- [ ] **Step 2: Implement deterministic intent fallback**

Before full Gemini routing, use Python keyword fallback:

```txt
학업 keywords -> academic_advisor
취업/진로 keywords -> career_advisor
프로젝트/창업 keywords -> startup_project_mentor
과제/마감/시험 keywords -> schedule_assistant
```

- [ ] **Step 3: Implement MVP response shape**

Return Korean mentor-tone answers with choice options. Do not claim full RAG or Google grounding is implemented until those services are wired.

- [ ] **Step 4: Run chat tests**

Run:

```powershell
cd backend && uv run pytest tests/api/test_chat_contract_api.py -q
```

Expected: chat contract tests pass.

## Task 6: Frontend Contract Wiring

**Files:**
- Modify: `frontend/src/types/api.ts`
- Modify: `frontend/src/lib/api.ts`
- Create: `frontend/src/pages/HomePage.tsx`
- Create: `frontend/src/pages/RecordsPage.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add TypeScript API types**

Add types matching backend:

```txt
Profile
Memory
MemoryEvent
ChatResponse
ChatEvidence
ChoiceOption
```

- [ ] **Step 2: Add API client functions**

Add functions:

```txt
getProfile()
upsertProfile()
getMemories()
updateMemory()
deleteMemory()
sendChatMessage()
```

- [ ] **Step 3: Build Home page**

Home must show:

```txt
large AI input
profile summary
recent memories
D-day placeholder
recommended choice chips
```

- [ ] **Step 4: Build Records page**

Records must show:

```txt
profile
active memories
edit/delete controls
LLM usage link/placeholder
```

- [ ] **Step 5: Run frontend build**

Run:

```powershell
pnpm build:frontend
```

Expected: Vite build succeeds.

## Task 7: Documentation and Review

**Files:**
- Modify: `docs/contributing/feature-registry.md`
- Modify: `docs/contributing/plans-status.md`
- Modify: `docs/llm/usage-log.md`
- Modify: this plan document with verification results

- [ ] **Step 1: Update feature state**

When profile/memory foundation is implemented and verified, update:

```txt
user-profile-memory: planned -> complete
personalized-sw-navigator-design: active -> complete
```

Only mark complete after backend tests and frontend build pass.

- [ ] **Step 2: Record LLM usage**

Add a row to `docs/llm/usage-log.md` describing how Codex/Gemini helped design or implement the slice and what the human verified.

- [ ] **Step 3: Run required verification**

Run:

```powershell
pnpm docs:check
pnpm test:backend
pnpm lint:backend
pnpm build:frontend
```

Expected: all pass, or exact blockers are recorded.

- [ ] **Step 4: Self-review**

Review for:

```txt
no tokens/secrets committed
no frontend access to Google tokens
no raw embedding vectors exposed
memory sensitivity policy tested
docs match implemented behavior
```

## Future Plans

After this foundation slice:

1. `2026-05-13-rag-grounding-router.md`: Gemini service, embedding service, internal RAG, retrieval router, Google grounding.
2. `2026-05-13-schedule-calendar-export.md`: assignment parser, D-day, Google Calendar export.
3. `2026-05-13-navigator-ui.md`: polished Home/Academic/Career/Project/Schedule/Records tabs.
