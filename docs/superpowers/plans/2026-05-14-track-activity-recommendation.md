# Track Activity Recommendation Plan

> **For agentic workers:** 이 plan은 조건문/딕셔너리 기반 트랙/활동 추천 구현 기록이다.

**Goal:** 사용자의 학년, 관심사, 목표, 코딩 경험, 활동 성향을 입력받아 설명 가능한 Python 규칙으로 트랙과 활동 후보를 추천한다.

## Implemented Scope

- `backend/app/schemas/recommendation.py`를 추가했다.
- `backend/app/services/recommendation_service.py`를 추가했다.
- `backend/app/api/recommendations.py`를 추가했다.
- `POST /api/recommend/track`을 추가했다.
- `POST /api/recommend/activity`를 추가했다.
- frontend `진로/취업` 화면에서 추천 실행과 결과 표시를 실제 API에 연결했다.
- 추천 점수는 Python 규칙으로 유지하되, 최상위 추천어와 사용자 입력을 query로 만들어 기존 RAG retriever의 내부 문서 출처를 `evidence.internal_sources`에 붙였다.
- frontend 추천 카드 아래에 내부 근거 chip을 표시한다.
- frontend `진로/취업` 화면은 이미 로드한 프로필/메모리에서 관심사, 목표, 학습 선호, 활동 성향을 간단한 keyword rule로 추출해 추천 API 입력으로 사용한다.
- 메모리가 없을 때는 기존 데모 fallback 입력을 유지한다.
- frontend `진로/취업` 화면에서 트랙 관심사, 활동 관심사, 목표, 코딩 경험, 학습 선호, 활동 방식, 주간 가능 시간을 직접 편집할 수 있다.
- 직접 편집 전에는 프로필/메모리 자동 추출값을 초기값으로 쓰고, 수정 후에는 `자동값으로 되돌리기`로 다시 동기화할 수 있다.

## Core Logic Notes

- 추천 후보는 `TRACK_RULES`, `ACTIVITY_RULES` 딕셔너리 리스트로 관리한다.
- 입력 관심사는 소문자/토큰 단위로 정규화한 뒤 각 후보의 keyword와 비교한다.
- 학년, 코딩 경험, 학습 선호, 활동 성향, 주간 가능 시간을 조건문으로 점수에 반영한다.
- 결과는 점수순으로 정렬하고, 중복되지 않는 다음 행동 목록을 함께 반환한다.
- 추천 결과가 나온 뒤 `get_document_retriever()` 경로로 Mini Wiki/raw/Supabase 검색 근거를 조회한다.
- RAG 근거는 추천 점수를 바꾸지 않고, 사용자가 추천 이유를 확인할 수 있는 출처 설명으로만 사용한다.
- frontend 입력 자동화는 `Memory.natural_text`와 `value_json`을 합쳐 AI/백엔드/창업/운동/알고리즘 같은 keyword를 추출한다.
- 이 자동화는 API 추천 규칙을 바꾸지 않고, 사용자가 저장한 메모리를 추천 요청의 초기값으로 쓰는 얇은 연결층이다.
- frontend 직접 입력값은 comma/newline 단위로 나눠 중복을 제거하고 최대 8개 관심사만 추천 API로 보낸다.
- 빈 입력은 발표 데모가 끊기지 않도록 AI/백엔드, 개발/운동 fallback으로 보정한다.
- 이 로직은 사용자 입력, 조건문, 반복문, 함수, 리스트/딕셔너리, 의미 있는 출력 조건을 직접 보여준다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_recommendation_service.py tests\api\test_recommendations_api.py -q
cd ..
pnpm test:backend
pnpm lint:backend
pnpm docs:check
pnpm build:frontend
```

결과:

- focused recommendation service/API tests: 5 passed
- `pnpm test:backend`: 74 passed
- `pnpm lint:backend`: All checks passed
- `pnpm docs:check`: 필수 문서 19개 확인 완료
- `pnpm build:frontend`: Vite production build 통과
- RAG evidence focused tests: 5 passed
- Profile/memory recommendation input frontend build: 통과
- Editable recommendation input frontend build: 통과 (`pnpm build:frontend`)

## Remaining Work

- Gemini answer generation으로 추천 설명 문장을 더 자연스럽게 만든다.
