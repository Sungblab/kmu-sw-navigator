# Google Grounding Plan

> **For agentic workers:** 이 plan은 진로/취업/창업 질문에 Google Search grounding을 붙인 구현 기록이다.

**Goal:** 최신성이 필요한 진로, 취업, 창업, 공모전 질문에서 Gemini Google Search grounding을 사용하고, 답변 근거를 `evidence.web_sources`로 분리 표시한다.

## Implemented Scope

- `backend/app/services/answer_generation_service.py`에 `GroundedAnswer`, `GroundingAnswerGenerator`, `GeminiGroundingAnswerGenerator`를 추가했다.
- `GeminiGroundingAnswerGenerator`는 공식 Gemini API 방식인 `types.Tool(google_search=types.GoogleSearch())`를 사용한다.
- grounding 응답의 `grounding_metadata.grounding_chunks[].web`에서 `title`, `uri`, `domain`을 추출해 `web_sources`로 반환한다.
- `backend/app/services/chat_contract_service.py`가 `career_advisor`, `startup_project_mentor` intent에서만 grounding generator를 호출한다.
- `backend/app/api/dependencies.py`와 `backend/app/api/chat.py`에 grounding dependency를 추가했다.
- frontend chat chip과 context panel에서 `evidence.web_sources`를 `웹` 근거로 표시한다.

## Core Logic Notes

- 학업/학교 자료 질문은 기존 내부 RAG를 우선한다.
- 진로/취업/창업처럼 최신성이 필요한 질문만 Google grounding을 호출한다.
- grounding이 성공하면 `needs_verification`을 비우고, 웹 출처를 `evidence.web_sources`에 넣는다.
- grounding 호출이 실패하거나 `GEMINI_API_KEY`가 없으면 기존 deterministic 답변과 검증 필요 메시지를 유지한다.
- Google Search grounding은 Gemini API가 검색 query 생성, 검색 실행, 근거 metadata 생성을 처리한다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_answer_generation_service.py tests\api\test_chat_contract_api.py -q
cd ..
pnpm test:backend
pnpm lint:backend
pnpm build:frontend
```

결과:

- focused grounding service/API tests: 9 passed
- `pnpm test:backend`: 79 passed
- `pnpm lint:backend`: All checks passed
- `pnpm build:frontend`: Vite production build 통과

## Remaining Work

- 실제 `GEMINI_API_KEY`를 넣은 `pnpm gemini:grounding-smoke` live Google grounding smoke를 실행한다.
- 웹 출처 URL을 UI에서 클릭 가능한 외부 링크로 만드는 polish를 검토한다.
