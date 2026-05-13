# Supabase Persistence Adapter Implementation Plan

> **For agentic workers:** 이 plan은 프로필/메모리 API가 in-memory 저장소만 쓰던 상태에서 Supabase adapter를 붙인 구현 기록이다.

**Goal:** `/api/profile`, `/api/memories`, `/api/chat`에서 사용하는 profile/memory 저장소를 protocol 기반으로 분리하고, Supabase 환경 변수가 있으면 영속 저장소를 사용하게 한다.

**Design Direction:** 과제 발표와 로컬 테스트에서는 외부 키 없이도 실행 가능해야 하므로 in-memory fallback을 유지한다. 실제 배포 환경에서는 `SUPABASE_URL`과 `SUPABASE_SERVICE_ROLE_KEY`가 있을 때 Supabase service-role client를 통해 저장한다.

## Implemented Scope

- `backend/app/services/store_protocols.py`에 `ProfileStore`, `MemoryStore` protocol을 추가했다.
- `backend/app/services/supabase_stores.py`에 `SupabaseProfileStore`, `SupabaseMemoryStore`를 구현했다.
- `backend/app/core/config.py`에 backend 설정과 Supabase 사용 가능 여부 판단을 추가했다.
- `backend/app/db/supabase_client.py`에 Supabase client 생성 함수를 추가했다.
- `backend/app/api/dependencies.py`에서 환경 변수 유무에 따라 Supabase adapter 또는 in-memory fallback을 선택하게 했다.
- profile/memory/chat API dependency 타입을 protocol로 바꿔 저장소 구현체를 교체 가능하게 했다.
- `backend/tests/services/test_supabase_stores.py`에 fake Supabase client 기반 저장, 조회, 수정, archive 테스트를 추가했다.
- Supabase write 응답이 list-shaped로 돌아오는 경우를 `_single_row()`에서 정규화해 live client 응답 형태와 테스트 fake의 차이를 줄였다.
- `backend/app/scripts/supabase_smoke.py`와 `pnpm supabase:smoke`를 추가해 실제 Supabase DB write/read를 확인할 수 있게 했다.
- `backend/app/scripts/check_env.py`와 `pnpm env:check`를 추가해 Supabase Direct/backend 값과 Framework/frontend 값을 비밀값 노출 없이 점검할 수 있게 했다.
- `pnpm env:check:strict`는 core Supabase 값이 누락되면 exit 2로 실패하므로 배포 전 점검에 사용할 수 있다.

## Core Logic Notes

- 프로필과 메모리의 `user_id`는 request body가 아니라 인증 dependency에서 받은 값으로만 붙인다.
- 모든 메모리 조회/수정은 `user_id`와 `memory_id`를 함께 조건으로 걸어 사용자 간 데이터가 섞이지 않게 한다.
- in-memory fallback은 배포 기능이 아니라 로컬 발표, 단위 테스트, 외부 키 없는 검증을 위한 실행 경로다.
- Supabase `insert/upsert` 응답은 단일 dict가 아니라 list로 올 수 있으므로, adapter boundary에서 한 번 정규화한다.
- 실제 Supabase project smoke는 아직 수행하지 않았다. service role key와 schema 적용이 준비되면 `/api/profile`, `/api/memories`를 live DB로 검증한다.
- 현재 앱 구조에서는 Supabase Dashboard의 `Direct` 값 중 `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`를 `backend/.env`에 두고, `Framework` client 값 중 `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`를 `frontend/.env`에 둔다.
- `SUPABASE_SERVICE_ROLE_KEY`는 브라우저 번들에 들어가면 안 되므로 frontend env에는 절대 넣지 않는다.
- live smoke의 `--user-id`는 Supabase Auth에 실제 존재하는 UUID여야 한다. schema가 `profiles.id`, `user_memories.user_id` 등을 `auth.users(id)`에 연결하므로 임의 문자열은 사용하지 않는다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_supabase_stores.py -q
cd ..
pnpm test:backend
pnpm lint:backend
pnpm env:check
pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>
```

결과:

- `tests\services\test_supabase_stores.py`: 3 passed
- `pnpm test:backend`: 81 passed
- `pnpm lint:backend`: All checks passed
- `pnpm docs:check`: 필수 문서 19개 확인 완료
- `tests\test_check_env_script.py`: 2 passed
- `pnpm env:check`: 현재 `.env` 파일이 없어 backend/frontend Supabase, Gemini, Google OAuth 누락 항목을 값 노출 없이 출력
- `pnpm env:check:strict`: core Supabase 값 누락 때문에 exit 2로 실패하는 것을 확인
- `pnpm supabase:smoke`: 현재 `.env`가 없어 `SUPABASE_URL`과 `SUPABASE_SERVICE_ROLE_KEY` 필요 메시지 출력 후 종료. 키와 실제 Auth user UUID 설정 후 live DB smoke로 다시 실행한다.

## Remaining Work

- Supabase 프로젝트에 `supabase/schema.sql`을 적용하고 `.env`를 채운 뒤 live persistence smoke를 수행한다.
- Supabase Auth 실제 가입/로그인 후 Bearer token API 요청을 live smoke로 검증한다.
- `chat_sessions`, `chat_messages`, `assignments`, Google OAuth token 저장소의 live DB smoke를 수행한다.
