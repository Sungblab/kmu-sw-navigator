# 기여 가이드

이 문서는 팀원이 이 프로젝트에 참여하는 방법을 설명합니다. 목표는 “코드만 제출”이 아니라, 설계와 협업 과정까지 설명 가능한 프로젝트를 만드는 것입니다.

## 1. 작업 시작 전

1. `README.md`를 읽습니다.
2. `docs/README.md`에서 관련 문서를 찾습니다.
3. `docs/contributing/feature-registry.md`에서 같은 기능을 누가 건드리는지 확인합니다.
4. GitHub Issue가 있으면 자신의 브랜치를 만듭니다.
5. LLM을 사용할 경우 사용 목적을 `docs/llm/usage-log.md`에 기록합니다.

## 2. 로컬 개발 환경

### 공통 도구

- Python 3.12+
- uv
- Node.js 20.19+
- pnpm 10+
- Git

### 백엔드

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 프론트엔드

```powershell
pnpm install
pnpm dev:frontend
```

### 문서 검사

```powershell
pnpm docs:check
```

## 3. 브랜치 규칙

`main`에 직접 커밋하지 않습니다. 기능별 브랜치를 사용합니다.

```powershell
git checkout -b feature/rag-chat
git checkout -b feature/schedule-dday
git checkout -b docs/llm-usage-log
```

## 4. 커밋 규칙

커밋은 작고 설명 가능하게 나눕니다.

```txt
docs: 프로젝트 문서 인덱스 추가
feat(backend): 일정 D-day 계산 함수 추가
feat(frontend): 챗봇 질문 입력 UI 추가
test(backend): 추천 규칙 테스트 추가
chore: 환경 변수 예시 정리
```

## 5. PR 규칙

PR에는 아래 내용을 포함합니다.

```md
## 변경 요약
- 무엇을 바꿨는지

## 검증
- 실행한 명령
- 수동으로 확인한 화면 또는 API
- 실행하지 못한 검증과 이유

## LLM 활용
- 어떤 LLM을 어떤 목적으로 사용했는지
- 최종 코드를 어떻게 이해하고 수정했는지
```

## 6. LLM 활용 기록 규칙

LLM을 사용한 경우 아래 항목을 기록합니다.

- 날짜
- 작성자
- 사용 도구: Codex, ChatGPT, Claude, Gemini 등
- 사용 목적: 설계, 코드 초안, 오류 해결, 테스트 아이디어, 문서 정리 등
- 반영 결과
- 직접 검토한 내용

예시는 `docs/llm/usage-log.md`를 확인합니다.

## 7. 역할 기록

현재 확정된 역할은 김성빈의 PM/개발 리드 역할입니다. 나머지 팀원의 역할은 실제 분담이 정해질 때 `docs/collaboration/team-roles.md`에 기록합니다.

## 8. 발표 대비 원칙

- 본인이 작성한 코드는 주요 함수 단위로 설명할 수 있어야 합니다.
- API 키나 비밀값은 발표자료에 노출하지 않습니다.
- 데모가 실패할 경우를 대비해 sample data와 스크린샷을 준비합니다.
- 보고서에는 전체 코드를 붙이지 않고 주요 구조와 핵심 코드만 설명합니다.
