# Assignment D-day Plan

> **For agentic workers:** 이 plan은 자연어 일정 입력을 preview하고 D-day를 계산하는 구현 기록이다.

**Goal:** 사용자가 "자료구조 과제 다음주 금요일까지" 같은 문장을 입력하면 Python 규칙으로 제목, 과목, 마감일, D-day를 계산하고 일정 탭에서 저장/조회한다.

## Implemented Scope

- `backend/app/schemas/assignment.py`를 추가했다.
- `backend/app/services/assignment_service.py`를 추가했다.
- `backend/app/api/assignments.py`를 추가했다.
- `POST /api/assignments/preview`가 자연어 문장을 일정 preview로 변환한다.
- `POST /api/assignments`, `GET /api/assignments`, `PATCH /api/assignments/{assignment_id}`, `DELETE /api/assignments/{assignment_id}`를 추가했다.
- 저장소는 `AssignmentStore` protocol로 분리했고, 로컬 개발은 in-memory, Supabase env가 있으면 `assignments` table adapter를 사용한다.
- frontend schedule page가 preview, save, list, 완료, 삭제를 실제 API와 연결한다.
- `GEMINI_API_KEY`가 있으면 `GeminiAssignmentParser`가 자연어 일정을 JSON으로 구조화하고, 실패하거나 키가 없으면 기존 Python 규칙 parser로 fallback한다.
- preview 응답에는 `parser` 필드가 포함되어 `gemini` 또는 `python_rules` 경로를 확인할 수 있다.

## Core Logic Notes

- `오늘`, `내일`, `다음주 금요일`, `2026-05-20`, `5월 20일`을 Python 조건문으로 처리한다.
- D-day는 `due_at.date() - today`로 계산한다.
- 날짜나 제목을 찾지 못하면 `missing_fields`와 낮은 confidence를 반환한다.
- 과목명은 `자료구조 과제`, `캡스톤 프로젝트` 같은 패턴에서 추출한다.
- Gemini parser는 제목, 과목, ISO datetime, confidence만 받도록 prompt를 제한한다.
- 외부 LLM 응답은 그대로 저장하지 않고 `ParsedAssignment` dataclass로 변환한 뒤 D-day 계산과 응답 생성은 기존 Python 코드가 맡는다.
- Gemini parser가 예외를 내거나 필수 제목이 비어 있으면 기존 Python 규칙으로 다시 파싱한다.
- 완료/삭제는 `user_id`와 `assignment_id`를 함께 조건으로 걸어 다른 사용자의 일정을 건드리지 않게 했다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_assignment_service.py tests\api\test_assignments_api.py -q
uv run python -m pytest tests\services\test_assignment_service.py tests\services\test_supabase_stores.py tests\api\test_assignments_api.py -q
cd ..
pnpm test:backend
pnpm lint:backend
pnpm docs:check
pnpm build:frontend
```

결과:

- focused assignment/Supabase/API tests: 12 passed
- Gemini parser focused assignment/API tests: 13 passed
- `pnpm test:backend`: 77 passed
- `pnpm lint:backend`: All checks passed
- `pnpm docs:check`: 필수 문서 19개 확인 완료
- `pnpm build:frontend`: Vite production build 통과

## Remaining Work

- Supabase `.env` 설정 뒤 live DB에서 일정 생성/완료/삭제 smoke를 실행한다.
- Calendar export를 추가한다.
- 실제 `GEMINI_API_KEY`를 넣은 `pnpm gemini:smoke` 일정 parser live smoke를 실행한다.
