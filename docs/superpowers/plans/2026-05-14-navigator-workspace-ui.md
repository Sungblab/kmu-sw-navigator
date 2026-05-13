# Navigator Workspace UI Implementation Plan

> **For agentic workers:** 이 plan은 Claude/NotebookLM식 workspace UI shell을 실제 React 화면에 반영한 기록이다.

**Goal:** 기존 홈/기록 탭 기반 화면을 제거하고, 왼쪽 navigation, 중앙 workspace, 오른쪽 context panel을 가진 3-column 앱 shell로 교체한다.

**Design Direction:** 사용자가 승인한 방향은 warm monochrome, Claude/NotebookLM style, Pretendard 기반, 초록색 accent 제거다. 첫 화면은 landing/dashboard가 아니라 바로 상담 workspace여야 한다.

## Implemented Scope

- `frontend/src/App.tsx`를 3-column workspace shell로 교체했다.
- 왼쪽 sidebar에 브랜드, 새 상담, workspace navigation, recent chats, LLM 기록, 설정 진입점을 추가했다.
- 중앙 영역에 `AI 상담`, `학업 로드맵`, `진로/취업`, `프로젝트`, `일정`, `LLM 기록`, `설정` 페이지 전환 구조를 추가했다.
- 기본 화면은 chat workspace로 두고, `/api/chat` contract와 연결된 메시지 전송 흐름을 유지했다.
- 오른쪽 context panel에 프로필, 메모리, 답변 근거, 일정, 추천 액션을 배치했다.
- `frontend/src/styles.css`에 Pretendard import와 light/warm monochrome base style을 적용했다.
- 더 이상 사용하지 않는 `HomePage.tsx`, `RecordsPage.tsx`를 제거했다.
- 모바일 상단에 메뉴 버튼을 추가하고, `lg` 미만 화면에서 workspace navigation/recent chats/LLM 기록/설정을 여는 drawer를 추가했다.
- drawer 선택 시 페이지 전환 후 자동으로 닫히며, 데스크톱 3-column sidebar는 그대로 유지한다.
- 모바일 상단에 context 버튼을 추가하고, 프로필/메모리/답변 근거/일정/추천 액션을 오른쪽 drawer로 확인할 수 있게 했다.
- 데스크톱 오른쪽 context panel과 모바일 context drawer는 같은 `ContextPanelContent`를 사용한다.

## Verification

```powershell
pnpm build:frontend
rg -n "emerald|green|teal|sky|slate|bg-emerald|text-emerald" frontend\src
Invoke-WebRequest -Uri http://127.0.0.1:5173 -UseBasicParsing
```

결과:

- `pnpm build:frontend` 통과
- `frontend/src`에서 초록/청록/하늘색 계열 Tailwind class 검색 결과 없음
- frontend dev server `http://127.0.0.1:5173` 응답 200 확인
- Playwright CLI package version 확인은 성공했지만, 임시 Node runtime에서 `require('playwright')`가 잡히지 않아 자동 클릭 smoke는 실행하지 못했다. 모바일 drawer는 브라우저에서 메뉴 버튼 클릭으로 추가 수동 확인한다.
- mobile context drawer 추가 후 `pnpm build:frontend` 통과

## Remaining Work

- 페이지별 placeholder를 실제 API 기능과 연결해야 한다.
- 다음 backend slice에서 Supabase persistence adapter와 실제 RAG/Gemini 연결을 진행한다.
