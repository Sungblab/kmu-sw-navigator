# KMU Freshman AI Assistant

국민대학교 소프트웨어융합대학 신입생을 위한 **RAG 기반 AI 학교생활 도우미**입니다. 학교와 학부 자료를 검색한 뒤 Gemini가 근거 기반 답변을 생성하고, 관심 분야 기반 트랙/활동 추천, 자연어 일정 등록, D-day 관리, LLM 활용 기록을 제공합니다.

## 프로젝트 정보

| 항목 | 내용 |
| --- | --- |
| 프로젝트명 | KMU Freshman AI Assistant, 북악 새내기 AI |
| 주제 | 국민대 소프트웨어융합대학 신입생 RAG AI 도우미 |
| PM / 개발 리드 | 김성빈 |
| 팀원 | 정재훈, 이가은, 차성민, 최승범, 비타 |
| 제출 마감 | 2026년 6월 11일 |
| 과제 조건 | Python 사용, 사용자 입력, 조건문, 반복문, 함수, 리스트/딕셔너리, 의미 있는 출력, 실행 가능한 코드, LLM 활용 기록 |

## 핵심 기능

- **RAG 챗봇**: 국민대/소프트웨어학부 자료를 검색하고 출처와 함께 답변합니다.
- **트랙/활동 추천**: 관심 분야, 목표, 코딩 경험, 학습 성향을 바탕으로 추천 결과를 제공합니다.
- **일정 관리**: 자연어로 입력한 과제/일정을 구조화하고 D-day를 계산합니다.
- **LLM 활용 기록**: Gemini API 사용 기록과 Codex 기반 개발 워크플로우를 문서로 남깁니다.
- **발표/보고서 지원**: 데모 시나리오, 보고서 목차, 코드 설명 포인트를 repo 안에서 관리합니다.

## 기술 스택

| 영역 | 선택 |
| --- | --- |
| Frontend | React, Vite, TypeScript, Tailwind CSS, shadcn/ui, lucide-react |
| Backend | Python 3.12, FastAPI, Pydantic, Uvicorn |
| Database/Auth | Supabase Auth, Supabase Postgres |
| Vector Search | Supabase pgvector, `vector(768)` |
| LLM | Gemini API, `google-genai` |
| Package/Dev | uv, pnpm workspace |
| 문서/협업 | Superpowers 방식의 spec, plan, execution log, LLM usage log |

## 문서 먼저 읽기

이 repo는 문서를 작업 라우터로 사용합니다.

1. [docs/README.md](docs/README.md): 전체 문서 인덱스
2. [docs/product/prd-dev-plan.md](docs/product/prd-dev-plan.md): 초기 PRD와 개발 계획
3. [docs/contributing/dev-guide.md](docs/contributing/dev-guide.md): 로컬 개발 환경
4. [docs/contributing/feature-registry.md](docs/contributing/feature-registry.md): 기능 소유 영역
5. [docs/llm/codex-workflow.md](docs/llm/codex-workflow.md): Codex/Superpowers 활용 방식
6. [CONTRIBUTING.md](CONTRIBUTING.md): 팀원 기여 방법

## 빠른 시작

### 1. 필수 도구

- Python 3.12+
- uv
- Node.js 20.19+
- pnpm 10+
- Supabase 프로젝트
- Gemini API Key

Docker는 기본 개발 흐름에 필요하지 않습니다. Supabase를 로컬 컨테이너로 완전히 재현하고 싶을 때만 선택적으로 사용합니다. 수업 제출용 MVP는 Supabase Cloud와 `supabase/schema.sql` 실행만으로 진행합니다.

### 2. 환경 변수

```powershell
Copy-Item .env.example .env
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

`.env`와 각 앱의 `.env`에 Supabase와 Gemini 값을 채웁니다. 비밀값은 커밋하지 않습니다.

### 3. 백엔드 실행

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

백엔드 헬스체크:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 4. 프론트엔드 실행

```powershell
pnpm install
pnpm dev:frontend
```

프론트엔드는 기본적으로 `http://localhost:5173`에서 실행됩니다.

### 5. 문서 체크

```powershell
pnpm docs:check
```

이 명령은 제출과 협업에 필요한 핵심 문서가 존재하는지 검사합니다.

## 개발 원칙

- 기능을 만들기 전 `docs/superpowers/specs/`에 설계를 남깁니다.
- 구현 전에 `docs/superpowers/plans/`에 실행 계획을 남깁니다.
- LLM을 사용하면 `docs/llm/usage-log.md`에 목적과 결과를 기록합니다.
- 새 기능은 `feature/<short-name>` 브랜치에서 작업합니다.
- PR에는 실행한 검증 명령을 반드시 적습니다.
- 발표에서 설명할 수 없는 코드는 제출하지 않습니다.

## GitHub 운영

- 기본 브랜치: `main`
- 공개 repo로 운영합니다.
- 이슈로 작업 단위를 만들고, 브랜치와 PR을 연결합니다.
- 팀원이 구현한 기능은 PR 리뷰 후 병합합니다.
- 김성빈은 PM/개발 리드로 설계, 통합, 검증, 발표 흐름을 관리합니다.

## 과제 조건 매핑

| 조건 | 충족 방식 |
| --- | --- |
| Python 사용 | FastAPI 백엔드, RAG, Gemini 호출, 일정 계산 |
| 사용자 입력 | 질문, 추천 조건, 자연어 일정 입력 |
| 조건문 | 트랙/활동 추천 규칙 |
| 반복문 | 문서 chunk 처리, 일정 목록, 로그 목록 |
| 함수 | RAG 검색, 임베딩 생성, 추천, D-day 계산 |
| 리스트/딕셔너리 | 추천 규칙, 문서 목록, sources, logs |
| 의미 있는 출력 | 근거 기반 답변, 추천 결과, D-day, LLM 기록 |
| 실행 가능한 코드 | 프론트엔드와 백엔드 로컬 실행 |
| LLM 활용 기록 | `docs/llm/usage-log.md`, `docs/llm/codex-workflow.md` |

## 라이선스

MIT License를 사용합니다. 자세한 내용은 [LICENSE](LICENSE)를 확인하세요.
