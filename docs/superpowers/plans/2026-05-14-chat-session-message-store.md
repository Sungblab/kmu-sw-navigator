# Chat Session Message Store Plan

> **For agentic workers:** 이 plan은 `/api/chat` 요청/응답을 session과 message pair로 저장하게 만든 구현 기록이다.

**Goal:** chat 응답에 `session_id`를 포함하고, 사용자 메시지와 assistant 메시지를 `chat_sessions`, `chat_messages` 저장소에 기록한다.

## Implemented Scope

- `ChatResponse.session_id`를 추가했다.
- `backend/app/services/chat_store.py`에 `InMemoryChatStore`를 추가했다.
- `backend/app/services/store_protocols.py`에 `ChatStore` protocol을 추가했다.
- `backend/app/services/supabase_stores.py`에 `SupabaseChatStore`를 추가했다.
- `/api/chat`이 응답 생성 뒤 `chat_store.save_exchange()`를 호출한다.
- session id가 없으면 새 session을 만들고, 있으면 기존 session에 user/assistant message pair를 추가한다.
- Supabase fake client를 list insert, generated id, filtered update에 맞게 보강했다.

## Core Logic Notes

- 첫 질문 앞부분을 session title로 저장해 채팅 목록에서 식별 가능하게 한다.
- user와 assistant message를 항상 한 쌍으로 저장해 대화 순서를 복원할 수 있게 한다.
- assistant message에는 evidence와 memory_updates snapshot을 함께 저장한다.
- 로컬/테스트 환경은 in-memory store, Supabase env가 있으면 Supabase store를 쓴다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_chat_store.py tests\services\test_supabase_stores.py tests\api\test_chat_contract_api.py -q
cd ..
pnpm lint:backend
```

결과:

- focused chat store/API tests: 10 passed
- `pnpm lint:backend`: All checks passed

## Remaining Work

- 채팅 목록 조회 API를 추가한다.
- frontend recent chats를 실제 session 목록으로 교체한다.
- live Supabase env에서 chat session/message insert smoke를 수행한다.
