# Google Calendar OAuth Connect Plan

> **For agentic workers:** 이 plan은 Google Calendar consent URL을 백엔드에서 생성하고 설정 화면에 연결 상태를 표시한 구현 기록이다.

**Goal:** 앱 로그인과 Google Calendar consent를 분리하고, Calendar 권한 env가 있을 때 연결 시작 URL 생성, callback code exchange, server-only token 저장까지 처리한다.

## Implemented Scope

- `backend/app/core/config.py`에 Google OAuth env를 추가했다.
- `backend/app/services/google_calendar_oauth_service.py`를 추가했다.
- `GET /api/integrations/google-calendar/status`를 추가했다.
- `GET /api/integrations/google-calendar/connect`를 추가했다.
- `GET /api/integrations/google-calendar/callback`을 추가했다.
- OAuth `state`는 raw user id를 노출하지 않고 HMAC digest로 만든다.
- callback에서 `state`를 검증해 user id를 복원하고 Google token endpoint로 authorization code를 교환한다.
- access/refresh token은 프론트에 반환하지 않고 in-memory/Supabase token store에 보호 문자열로 저장한다.
- access token이 만료되었으면 refresh token으로 Google token endpoint를 다시 호출해 새 access token을 저장한다.
- frontend settings page가 Calendar 설정 상태를 보여주고, configured 상태에서 consent URL로 이동한다.
- `.env.example`, `backend/.env.example`, `docs/contributing/dev-guide.md`에 Google OAuth env를 추가했다.

## Core Logic Notes

- Google Calendar event 생성은 Google Calendar API의 event insert 흐름을 사용하므로 OAuth scope는 `https://www.googleapis.com/auth/calendar.events`를 기본값으로 둔다.
- 프론트는 client secret을 알지 않는다. 백엔드가 consent URL을 만들고 프론트는 redirect만 수행한다.
- env가 없으면 API는 오류를 던지지 않고 `configured=false`를 반환해 로컬 발표/테스트 환경을 유지한다.
- Google 공식 OAuth 문서 기준으로 authorization code는 `https://oauth2.googleapis.com/token` endpoint에 POST해 access/refresh token으로 교환한다.
- 배포 env에서는 Supabase `google_oauth_tokens` table을, 로컬 env에서는 in-memory token store를 쓴다.
- refresh 시 기존 refresh token은 유지하고 새 access token, scope, expires_at만 갱신한다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_google_calendar_oauth_service.py tests\api\test_google_calendar_integration_api.py -q
uv run python -m pytest tests\services\test_google_oauth_token_service.py tests\services\test_calendar_service.py tests\services\test_supabase_stores.py -q
cd ..
pnpm lint:backend
pnpm build:frontend
```

결과:

- focused OAuth service/API tests: 7 passed
- focused token refresh/Calendar/Supabase store tests: 통과
- `pnpm lint:backend`: All checks passed
- `pnpm build:frontend`: Vite production build 통과

## Remaining Work

- Calendar export service가 저장된 token을 사용해 실제 Google `events.insert`를 호출하게 연결한다.
- Google env 설정 뒤 live OAuth smoke를 수행하고, 저장된 token으로 `pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>`를 실행한다.
