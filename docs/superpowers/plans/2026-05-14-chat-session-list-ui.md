# Chat Session List UI Plan

> **For agentic workers:** 이 plan은 저장된 chat session/message를 API로 조회하고 sidebar recent chats에 연결한 구현 기록이다.

**Goal:** `/api/chat`이 만든 session을 다시 조회할 수 있게 하고, 프론트 왼쪽 recent chats를 실제 session 목록으로 교체한다.

## Implemented Scope

- `ChatResponse.session_id`를 응답 contract에 추가했다.
- `ChatSessionSummary`, `ChatMessageRecord`, `ChatSessionsResponse`, `ChatMessagesResponse` schema를 추가했다.
- `ChatStore` protocol에 `list_sessions()`, `list_messages()`를 추가했다.
- `InMemoryChatStore`, `SupabaseChatStore`가 session/message 조회를 지원한다.
- `/api/chat/sessions`, `/api/chat/sessions/{session_id}/messages` endpoint를 추가했다.
- frontend API client에 `getChatSessions()`, `getChatMessages()`를 추가했다.
- sidebar recent chats가 API session 목록을 렌더링한다.
- session을 클릭하면 저장된 메시지를 중앙 chat workspace에 불러온다.
- `새 상담` 버튼은 session id를 reset해 다음 메시지가 새 session으로 저장되게 한다.

## Core Logic Notes

- session list는 사용자별로만 조회한다.
- message list도 `user_id`와 `session_id`를 함께 조건으로 걸어 다른 사용자의 대화가 섞이지 않게 한다.
- API 실패 시 chat list 오류가 현재 상담 입력 흐름을 막지 않도록 프론트에서는 기존 목록을 유지한다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_chat_store.py tests\services\test_supabase_stores.py tests\api\test_chat_contract_api.py -q
cd ..
pnpm build:frontend
pnpm test:backend
```

결과:

- focused chat session tests: 11 passed
- `pnpm build:frontend`: Vite production build 통과
- `pnpm test:backend`: 44 passed

## Remaining Work

- live Supabase env에서 session/message 조회 smoke를 수행한다.
- sidebar에 session 생성 시간/최근 메시지 preview를 추가한다.
- session 삭제/이름 변경은 후속 UX slice에서 결정한다.
