# Google Grounding Plan

> **For agentic workers:** 이 plan은 진로/취업/창업/최신 공지 질문에 Google Search grounding을 붙인 구현 기록이다.

**Goal:** 최신성이 필요한 진로, 취업, 창업, 공모전, 소프트웨어융합대학 최신 공지 질문에서 Gemini Google Search grounding을 사용하고, 답변 근거를 `evidence.web_sources`로 분리 표시한다.

## Implemented Scope

- `backend/app/services/answer_generation_service.py`에 `GroundedAnswer`, `GroundingAnswerGenerator`, `GeminiGroundingAnswerGenerator`를 추가했다.
- `GeminiGroundingAnswerGenerator`는 공식 Gemini API 방식인 `types.Tool(google_search=types.GoogleSearch())`를 사용한다.
- grounding 응답의 `grounding_metadata.grounding_chunks[].web`에서 `title`, `uri`, `domain`을 추출해 `web_sources`로 반환한다.
- `backend/app/services/chat_contract_service.py`가 `career_advisor`, `startup_project_mentor`, `latest_notice_advisor` intent에서 grounding generator를 호출한다.
- `backend/app/api/dependencies.py`와 `backend/app/api/chat.py`에 grounding dependency를 추가했다.
- frontend chat chip과 context panel에서 `evidence.web_sources`를 `웹` 근거로 표시한다.
- 최근 상담 목록은 `latest_notice_advisor`를 `최신 공지`로 표시한다.

## Core Logic Notes

- 학업/학교 기본 자료 질문은 기존 내부 RAG를 우선한다.
- 진로/취업/창업/최신 공지처럼 최신성이 필요한 질문만 Google grounding을 호출한다.
- 소융대/학부 공지 질문은 국민대학교 소프트웨어융합대학 공식 사이트, 학부 공지사항, 공식 SNS를 우선 확인하도록 prompt에 명시한다.
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
- 2026-06-02 최신 공지 확장 focused/API tests: 20 passed
- 2026-06-02 `pnpm gemini:grounding-smoke`: intent=`career_advisor`, web_source_count=3
- 2026-06-02 latest notice 직접 grounding 호출: intent=`latest_notice_advisor`, web_source_count=4

## Remaining Work

- 웹 출처 URL을 UI에서 클릭 가능한 외부 링크로 만드는 polish를 검토한다.
