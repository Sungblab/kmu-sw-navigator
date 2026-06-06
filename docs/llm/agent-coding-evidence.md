# 에이전트 기반 코딩 활용 증거

이 문서는 교수님이 “AI 에이전트를 사용해 코딩한 과정”을 평가할 때 바로 확인할 수 있도록, 본 프로젝트에서 Codex, Superpowers, Gemini Code Assist, Gemini API를 어떻게 사용했고 어떤 부분을 사람이 직접 검토했는지 정리한다.

핵심 주장은 다음과 같다.

```txt
AI 에이전트가 코드를 대신 제출한 것이 아니라,
사람이 목표와 기준을 정하고 에이전트에게 설계, 구현, 검증, 리뷰를 반복 수행하게 한 뒤
결과를 직접 읽고 수정하고 테스트했다.
```

## 1. 에이전트 개발 하네스

본 프로젝트는 에이전트가 임의로 코드를 작성하지 않도록 repo 안팎에 작업 규칙을 고정했다.

| 구성 | 위치 | 역할 |
| --- | --- | --- |
| repo 규칙 | `AGENTS.md` | 한국어 응답, 문서 읽기 순서, Python 과제 조건, 완료 전 검증 절차를 고정 |
| 문서 라우터 | `docs/README.md` | PRD, roadmap, feature registry, architecture, testing, report 문서로 이동 |
| 기능 레지스트리 | `docs/contributing/feature-registry.md` | 기능별 소유 경로와 중복 작업 방지 기준 |
| 작업 상태 | `docs/contributing/plans-status.md` | 현재 구현 상태, live smoke 대기 항목, 다음 작업 후보 |
| 설계/실행 계획 | `docs/superpowers/specs/`, `docs/superpowers/plans/` | 기능 구현 전 요구사항과 구현 순서 기록 |
| 전용 Codex 스킬 | `~/.codex/skills/kmu-sw-navigator-*` | 새 Codex 세션이 repo 규칙, 완료 게이트, 다음 작업 판단, 병렬 세션 분할을 복원 |
| 검증 명령 | `package.json` scripts | 문서, Python, wiki, RAG ingest, frontend build를 반복 검증 |
| LLM 사용 기록 | `docs/llm/usage-log.md`, `docs/llm/prompt-summary-log.md` | 에이전트를 어떤 목적으로 사용했고 어떤 결정을 사람이 했는지 기록 |

## 2. 사용한 에이전트와 역할

| 도구 | 사용 위치 | 역할 |
| --- | --- | --- |
| Codex | 개발 세션 | repo 문서 읽기, spec/plan 작성, 코드 수정, 테스트 실행, 실패 원인 분석, 문서 최신화 |
| Superpowers | 개발 워크플로우 | brainstorming, spec, plan, verification, code review 절차 고정 |
| Gemini Code Assist | PR/리뷰 단계 | 코드 리뷰 의견 제공, 잠재 버그와 누락 테스트 지적 |
| Gemini API | 앱 기능 | RAG 답변 생성, Google grounding, 자연어 일정 parser, embedding 생성 |

Codex와 Gemini Code Assist는 개발 보조 에이전트이고, Gemini API는 앱 기능 자체에서 호출하는 LLM이다. 보고서에서는 두 범위를 구분해서 설명한다.

## 3. 에이전트 코딩 반복 흐름

기능 단위 작업은 다음 순서로 진행했다.

```txt
요구사항 확인
-> AGENTS.md와 docs/README.md로 작업 규칙 복원
-> PRD/roadmap/feature registry로 범위 확인
-> spec 또는 plan 작성
-> 테스트 또는 검증 기준 먼저 정리
-> Codex로 구현 구조 정리
-> 사람이 코드 구조, 과제 조건, 보안, 설명 가능성 검토
-> 테스트/빌드/문서 검증 실행
-> 실패하면 원인 분석 후 수정
-> usage log와 plan/status 문서 갱신
```

이 흐름 때문에 코드만 남는 것이 아니라, 설계 문서, 실행 계획, 테스트 결과, 사용 기록이 같이 남는다.

## 4. 사람이 직접 검토한 기준

LLM 활용 결과를 프로젝트 기준에 맞추기 위해 다음 기준으로 직접 검토했다.

- Python 함수가 사용자 입력을 받아 의미 있는 출력을 만드는가
- 조건문, 반복문, 리스트/딕셔너리 사용 지점이 발표에서 설명 가능한가
- 추천/일정/RAG/메모리 정책이 LLM 임의 판단이 아니라 코드의 명시적 규칙으로 남아 있는가
- Supabase service role key, Gemini key, Google token 같은 비밀값이 커밋되지 않는가
- 테스트 없이 “구현 완료”라고 문서에 쓰지 않았는가
- live key가 없어 실행하지 못한 검증은 “대기” 또는 “미수행”으로 분리했는가

## 4.1 그대로 사용하지 않았다는 증거

교수님에게는 “주석이 많다”만으로 설명하기보다, 아래 네 가지를 함께 보여주는 것이 안전하다.

| 증거 | 보여줄 위치 | 의미 |
| --- | --- | --- |
| 판단 주석 | `backend/app/services/*.py` | 추천, 일정, RAG, 메모리 정책의 이유를 사람이 설명 가능하게 남김 |
| 테스트 | `backend/tests/`, `tests/` | 생성된 코드가 실제 요구사항을 만족하는지 실행으로 확인 |
| 설명 문서 | `docs/architecture/python-core-logic.md` | 핵심 Python 로직을 과제 조건과 연결해 사람이 이해한 구조로 정리 |
| 사용 기록 | `docs/llm/usage-log.md` | Codex가 한 일과 사람이 직접 검토/수정/검증한 일을 분리 기록 |

따라서 발표에서는 “LLM을 설계 정리, 구현 보조, 오류 분석에 사용했고, Python 로직을 함수/조건문/반복문/테스트/주석/문서로 설명 가능하게 정리했다”고 설명한다.

## 5. 과제 조건과 연결되는 에이전트 활용

| 과제 조건 | 에이전트 활용 방식 | 사람이 확인한 증거 |
| --- | --- | --- |
| Python 사용 | Codex가 FastAPI service/schema/test 구조 정리를 보조 | `backend/app/`, `backend/tests/`, `pnpm test:backend` |
| 사용자 입력 | 채팅, 추천, 일정, 로그인 입력 경로 구현 보조 | API route와 React 입력 UI 확인 |
| 조건문 | 추천 점수, 일정 parser fallback, memory sensitivity 분기 구현 | `recommendation_service.py`, `assignment_service.py`, tests |
| 반복문 | 문서 chunk, 추천 후보, 근거 목록 순회 구현 | RAG ingest dry-run과 service tests |
| 함수 | 기능별 service 함수 분리 | 발표용 `docs/architecture/python-core-logic.md` |
| 리스트/딕셔너리 | 추천 규칙, evidence, assignments, memory payload 구성 | `TRACK_RULES`, `ACTIVITY_RULES`, response schema |
| 의미 있는 출력 | 답변, 추천, D-day, Calendar export, LLM log 출력 | frontend build와 demo scenario |
| LLM 활용 기록 | Codex/Gemini 사용 목적과 결과 기록 | `docs/llm/usage-log.md`, LLM 기록 화면 |

## 6. 보고서에 넣을 설명 문장

```txt
본 프로젝트는 Codex 같은 코딩 에이전트를 개발 하네스 안에서 동작하는 보조 개발자로 사용했다. AGENTS.md, 문서 라우터, feature registry, Superpowers spec/plan, 전용 Codex 스킬로 작업 범위를 먼저 고정했고, 구현 후에는 테스트와 빌드, 문서 검증을 실행했다. Python 함수 구조, 조건문/반복문, 추천 규칙, RAG 근거 처리, 일정 계산 로직은 직접 읽고 수정해 발표에서 설명 가능한 형태로 정리했다.
```

## 7. 발표에서 보여줄 자료

발표에서는 아래 순서로 화면이나 파일을 보여주면 “에이전트 활용 과정”이 명확하다.

1. `AGENTS.md`: 에이전트에게 준 repo 규칙
2. `docs/README.md`: 문서 라우터
3. `docs/superpowers/specs/`, `docs/superpowers/plans/`: 설계와 실행 계획
4. `docs/llm/usage-log.md`: 실제 LLM 사용 기록
5. `docs/report/submission-checklist.md`: 제출 조건과 검증 명령
6. `pnpm verify:local` 또는 최근 검증 결과

## 8. 주의해서 설명할 점

- “AI가 다 만들었다”가 아니라 “AI에게 일을 나누고, 사람이 기준과 검증을 통제했다”고 설명한다.
- Gemini API를 앱 기능에 쓴 것과 Codex를 개발 보조로 쓴 것을 구분한다.
- live key가 필요한 Supabase/Gemini/Google 검증은 실제 실행 여부를 과장하지 않는다.
- 코드 리뷰 의견은 무조건 반영한 것이 아니라 타당성을 확인한 뒤 반영/미반영 이유를 남긴다.
