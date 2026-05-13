# Google Calendar Export Foundation Plan

> **For agentic workers:** 이 plan은 저장된 assignment를 Google Calendar event payload로 변환하고, 앱 내부에 export 상태를 기록하는 구현 기록이다.

**Goal:** 저장된 과제/일정을 Google Calendar로 내보낼 수 있는 API와 UI 흐름을 만든다. 저장된 Google OAuth token이 있으면 `events.insert`를 호출하고, token이 없으면 앱 내부 export 상태 저장으로 fallback한다. live 연동은 키와 consent 설정 뒤 별도 smoke로 검증한다.

## Implemented Scope

- `backend/app/services/calendar_service.py`를 추가했다.
- `POST /api/assignments/{assignment_id}/export-calendar`를 추가했다.
- `AssignmentResponse`에 `calendar_event_id`, `calendar_synced_at`을 추가했다.
- `AssignmentStore` protocol에 `get_assignment`, `mark_calendar_exported`를 추가했다.
- in-memory/Supabase assignment store가 Calendar export 상태를 저장한다.
- 저장된 Google OAuth token이 있으면 Google Calendar API `events.insert` endpoint로 event payload를 POST한다.
- Google API 응답의 실제 event id를 `calendar_event_id`로 저장한다.
- frontend schedule card에 Calendar 내보내기 버튼을 추가했다.

## Core Logic Notes

- Google Calendar API의 event 생성은 `start`, `end`가 필요하므로 과제 마감 시각을 기준으로 30분짜리 마감 알림 event payload를 만든다.
- summary는 과목이 있으면 `과목 · 제목`, 없으면 제목만 사용한다.
- description에는 앱에서 내보낸 일정이라는 설명과 원문 memo를 포함한다.
- 이미 `calendar_event_id`와 `calendar_synced_at`이 있으면 새 event id를 만들지 않고 `already_exported=true`를 반환해 중복 내보내기를 막는다.
- token이 없으면 `kmu-{assignment_id}` synthetic id로 앱 내부 export 상태만 저장한다.
- token이 있으면 보호 저장된 access token을 server-side에서만 복원해 `Authorization: Bearer` header로 Google API를 호출한다.
- token이 만료되었으면 refresh token으로 새 access token을 발급받은 뒤 `events.insert`를 호출한다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_calendar_service.py tests\api\test_assignments_api.py tests\services\test_supabase_stores.py -q
cd ..
pnpm lint:backend
pnpm build:frontend
```

결과:

- focused calendar/API/Supabase tests: 통과
- `pnpm lint:backend`: All checks passed
- `pnpm build:frontend`: Vite production build 통과

## Remaining Work

- Supabase/Google env 설정과 저장된 Google OAuth token 준비 뒤 `pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>` live export smoke를 실행한다.
