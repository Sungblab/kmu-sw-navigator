# LLM 활용 기록

이 문서는 KMU SW Navigator 프로젝트의 제출용 LLM 활용 기록입니다. 일자별 작업 로그가 아니라 **팀원별 사용 도구, 사용 목적, 산출물, 사람이 확인한 내용**을 중심으로 정리합니다. 보고서 PDF에 포함하거나 별도 문서로 제출해도 바로 읽을 수 있도록 작성했습니다.

본 프로젝트에서 LLM은 세 가지 범위로 사용했습니다.

1. 개발 보조: Codex, ChatGPT, Gemini Code Assist를 사용해 주제 정리, 설계, 구현 보조, 오류 분석, 리뷰 관점 점검을 수행했습니다.
2. 데이터 정형화 보조: Gemini와 ChatGPT를 사용해 팀원이 수집한 학생회, 학사, 동아리 자료를 JSON 또는 Markdown 형태로 정리했습니다.
3. 앱 기능: Gemini API를 사용해 RAG 답변 생성, 자연어 일정 파싱, 문서 임베딩, 최신 웹 grounding을 수행했습니다.

## 1. 팀원별 LLM 활용 요약

| 이름 | 역할 | 사용 도구 | 사용 목적 | 산출물 | 사람이 확인한 내용 |
| --- | --- | --- | --- | --- | --- |
| 김성빈 | PM, 개발 통합, 검증 | Codex, ChatGPT, Gemini API, Gemini Code Assist | 프로젝트 주제 구체화, PRD/spec/plan 작성, FastAPI/RAG/Supabase/Gemini 구현 보조, 오류 분석, 코드 리뷰 관점 점검, 보고서 정리 | 개인화 RAG 기반 AI 내비게이터 범위 확정, Python FastAPI 백엔드, React UI, Supabase 저장소, Gemini 기반 답변 생성/일정 파싱 흐름 구현 | 추천 규칙, 일정 D-Day 계산, RAG 근거 선택, 인증/저장소 경계, LLM 로그 저장 흐름을 코드와 테스트로 확인했습니다. |
| 차성민 | 개발 보조, 기능 테스트, 코드 정리 | Codex | 프론트엔드 개발 중 API 호출 fallback과 팀 역할 문서 정리 보조 | git author `2476ae`로 `frontend/src/lib/api.ts`, `package.json`의 dev API fetch fallback 수정과 `docs/collaboration/team-roles.md` 수정 기록 | API fallback 수정이 실제 프론트엔드 API 호출 흐름과 맞는지 확인했고, 팀 역할 문서는 최종 역할 분담과 맞게 유지했습니다. |
| 이가은 | 데이터 수집/정리 | Gemini, ChatGPT | 학생회/학사 관련 자료를 JSON 형태로 정리하는 과정에서 사용 | `data/inbox/council.json` 형태의 접수 단계 자료 작성 | 자료를 최종 지식베이스와 분리해 `data/inbox`에 두고, 추후 출처, 내용, 개인정보 위험을 확인할 대상으로 표시했습니다. |
| 정재훈 | 데이터 수집/정리 | Gemini, ChatGPT | 동아리 자료를 JSON과 Markdown 형태로 정리하는 과정에서 사용 | `data/inbox/clubs_information.json`에 두음, WINK, AIM, KOSS 동아리 정보 정리 | 동아리명, 활동 내용, 지원 대상, 출처 확인 필요 항목을 사람이 확인할 수 있도록 접수 자료로 분리했습니다. |
| 비타 | 발표자료 | 해당 없음 | 발표자료 구성과 시연 흐름 정리 담당 | 발표자료 제작과 발표 화면 구성 | 이번 제출용 LLM 활용 기록에는 별도 LLM 사용 사실을 기재하지 않습니다. |
| 최승범 | 발표자료 | 해당 없음 | 발표자료 구성과 시연 흐름 정리 담당 | 발표자료 제작과 발표 화면 구성 | 이번 제출용 LLM 활용 기록에는 별도 LLM 사용 사실을 기재하지 않습니다. |

## 2. 개발 보조 LLM 사용 방식

김성빈은 Codex와 ChatGPT를 설계와 검증을 돕는 개발 보조 도구로 사용했습니다. 사용 방식은 다음과 같습니다.

| 단계 | LLM 활용 | 사람이 확인한 내용 |
| --- | --- | --- |
| 주제 구체화 | 가계부, 추천 시스템, 챗봇, 웹앱 등 가능한 주제 중 과제 조건을 만족하는 방향을 비교했습니다. | 최종 주제를 국민대학교 소프트웨어융합대학 개인화 RAG 내비게이터로 결정했습니다. |
| 요구사항 정리 | 과제 조건, 사용자 입력, Python 핵심 로직, LLM 활용 기록 요구사항을 문서 구조로 정리했습니다. | 제출물 기준을 `docs/report/`, `docs/architecture/`, `docs/llm/`로 나누고 보고서에 들어갈 항목을 확정했습니다. |
| 설계 문서 작성 | PRD, Superpowers spec, implementation plan의 구조와 문장 정리에 사용했습니다. | MVP 범위, 제외 범위, 실제 구현 가능한 기능을 직접 고르고 문서 표현을 수정했습니다. |
| 구현 보조 | FastAPI route, service, Pydantic schema, 테스트 구조를 잡는 데 사용했습니다. | 프로젝트 구조에 맞게 함수 분리, 타입 정리, 테스트 보강을 수행했습니다. |
| 오류 분석 | 테스트 실패, API payload 오류, Supabase 저장소 문제, 프론트 API 연결 문제를 분석하는 데 사용했습니다. | 실제 로그와 테스트 결과를 보고 원인을 확정한 뒤 코드를 수정했습니다. |
| 코드 리뷰 관점 | Gemini Code Assist와 Codex를 통해 누락 테스트, 보안 위험, 문서 불일치 가능성을 점검했습니다. | 타당한 지적만 반영하고, 비밀값 커밋 방지와 live 검증 상태를 직접 확인했습니다. |
| 보고서 정리 | 코드 설명, LLM 활용 방식, 제출 조건 매핑 문장을 정리하는 데 사용했습니다. | 보고서에는 전체 코드를 붙이지 않고 주요 Python 로직과 파일 경로 중심으로 설명했습니다. |

## 2.1 개발 과정에서의 구체적 활용

개발 과정에서 LLM은 기능을 한 번에 완성하는 용도가 아니라, 작업을 작게 나누고 검증 가능한 형태로 정리하는 데 사용했습니다.

### 3.1 주제와 범위 결정

초기에는 가계부, 학점 계산기, 퀴즈 프로그램, 추천 시스템, 챗봇, 웹앱 등 여러 주제를 비교했습니다. LLM에는 각 주제가 과제 조건을 얼마나 잘 보여줄 수 있는지, Python 로직을 설명하기 쉬운지, 발표 데모로 설득력이 있는지 비교하도록 요청했습니다.

그 결과 단순 계산 프로그램보다 사용자 입력, 조건문, 반복문, 리스트/딕셔너리, API 응답, LLM 활용 기록을 모두 보여줄 수 있는 웹앱이 적합하다고 판단했습니다. 최종적으로 국민대학교 소프트웨어융합대학 학생을 위한 개인화 RAG 기반 AI 내비게이터로 주제를 정했습니다.

사람이 결정한 내용은 다음과 같습니다.

- 신입생 안내를 주요 데모 시나리오로 사용합니다.
- 설계 범위는 소프트웨어융합대학 전체 학년까지 확장 가능하게 둡니다.
- Python 핵심 로직은 FastAPI 백엔드에 둡니다.
- React 프론트엔드는 사용자 입력과 결과 확인 화면으로 사용합니다.
- Supabase, RAG, Gemini API는 실제 서비스처럼 보이게 만드는 보조 구조로 사용합니다.

### 3.2 문서 구조 설계

LLM은 제출 문서와 개발 문서를 분리하는 데 사용했습니다. 처음에는 README 하나에 모든 내용을 넣을 수도 있었지만, 프로젝트가 커지면서 문서를 역할별로 나누었습니다.

| 문서 영역 | LLM 활용 방식 | 사람이 정한 기준 |
| --- | --- | --- |
| `docs/report/` | 최종보고서, 데모 흐름, 제출 체크리스트의 구성을 잡는 데 사용 | 제출 PDF와 발표영상에서 바로 설명 가능한 문서만 남겼습니다. |
| `docs/architecture/` | RAG, Mini LLM Wiki, Python 핵심 로직 설명 구조를 잡는 데 사용 | 발표에서 질문받을 수 있는 판단 기준 위주로 정리했습니다. |
| `docs/llm/` | LLM 사용 목적, 에이전트 활용 방식, 프롬프트 요약을 정리하는 데 사용 | 일자별 나열보다 사람별 역할과 사용 목적 중심으로 정리했습니다. |
| `docs/superpowers/` | 기능별 설계와 실행 계획을 기록하는 구조를 잡는 데 사용 | 구현 전에 범위와 검증 기준을 남기도록 했습니다. |
| `docs/contributing/` | roadmap, feature registry, plans-status 문서 구조를 잡는 데 사용 | 팀원이 어느 파일을 봐야 하는지 빠르게 알 수 있게 했습니다. |

### 3.3 Python 백엔드 구현 보조

Codex는 FastAPI 백엔드의 route, service, schema, test 구조를 정리하는 데 사용했습니다. 구현 과정에서 사람은 파일 구조와 책임 분리를 확인했습니다.

주요 활용 예시는 다음과 같습니다.

| 기능 | LLM 활용 | 사람이 확인한 코드 기준 |
| --- | --- | --- |
| 채팅 API | 사용자 질문을 받고 RAG 검색, 답변 생성, 저장을 연결하는 흐름 정리 | `backend/app/api/chat.py`에서 route가 사용자 입력을 받고 service 계층으로 넘기는지 확인 |
| RAG 검색 | raw/wiki 문서 chunk 검색 방식과 evidence 응답 구조 정리 | `backend/app/services/retrieval_service.py`에서 반복문으로 문서 후보를 순회하고 점수화하는지 확인 |
| 답변 생성 | 검색 근거, 사용자 메모리, intent를 프롬프트로 구성하는 방식 정리 | `backend/app/services/answer_generation_service.py`에서 내부 근거와 웹 근거가 분리되는지 확인 |
| 추천 기능 | 트랙/활동 후보를 리스트와 딕셔너리로 관리하고 점수화하는 구조 정리 | `backend/app/services/recommendation_service.py`에서 조건문과 점수 계산이 설명 가능한지 확인 |
| 일정 기능 | 자연어 일정 parser, D-Day 계산, 일정 저장 payload 구조 정리 | `backend/app/services/assignment_service.py`에서 날짜 계산과 저장 값이 테스트 가능한지 확인 |
| LLM 로그 | Gemini 사용 기록을 저장하고 조회하는 API 구조 정리 | `llm_usage_logs` 저장 흐름과 `GET /api/llm-logs` 응답을 확인 |

### 3.4 오류 분석과 수정

개발 중 오류가 발생했을 때 LLM에는 에러 메시지, 실패한 테스트, 관련 파일을 기준으로 원인 후보를 좁히도록 요청했습니다. 이후 실제 수정 여부는 테스트와 실행 결과로 확인했습니다.

활용한 오류 분석 유형은 다음과 같습니다.

- API 응답 payload가 프론트엔드 타입과 맞지 않는 문제 분석
- Supabase 저장소 adapter에서 JSON 직렬화가 필요한 값 확인
- 일정 저장 API에서 날짜, 시간, D-Day 값이 깨지는 문제 분석
- Gemini API key가 없을 때 fallback 경로가 정상 동작하는지 확인
- live smoke와 local test의 역할을 분리하는 문서 정리
- 프론트엔드 API fallback과 dev server proxy 흐름 점검

오류 분석 후에는 관련 테스트를 실행해 수정 결과를 확인했습니다.

### 3.5 프론트엔드와 데모 흐름 정리

프론트엔드는 React UI 자체가 과제의 핵심 언어는 아니지만, 사용자가 입력하고 결과를 확인하는 화면입니다. LLM은 화면 흐름과 API 연결 구조를 정리하는 데 사용했습니다.

주요 활용 내용은 다음과 같습니다.

- AI 상담, 학업 로드맵, 진로/취업, 프로젝트, 일정, 설정 탭 구성 정리
- 채팅 입력과 assistant 답변 표시 흐름 정리
- RAG 근거 chip, 개인화 메모리, 추천 액션 표시 방식 정리
- 자연어 일정 입력 후 일정 후보 카드 표시 방식 정리
- LLM 활용 기록 화면과 제출 증거 설명 흐름 정리

프론트엔드 구현 결과는 `pnpm build:frontend`로 확인했습니다.

### 3.6 보고서와 발표 준비

보고서 작성에서는 LLM을 문장 정리와 구성 점검에 사용했습니다. 다만 보고서에는 전체 코드를 붙이지 않고, 과제 조건을 보여주는 주요 Python 파일과 로직 중심으로 설명했습니다.

보고서에 반영한 핵심 설명은 다음과 같습니다.

- 프로젝트 주제와 목적
- 주요 기능
- 시스템 구조
- 코드 구조
- 채팅 API, RAG 검색, 추천, 일정 D-Day 계산의 주요 흐름
- LLM 활용 방식
- 실행 결과
- 한계와 개선 방향

발표 준비에서는 데모 순서를 정리하는 데 사용했습니다. 최종 발표자료는 이미 별도 PPT로 만들었기 때문에 repo 안의 outline 문서는 제거했고, 현재는 `docs/product/live-scenario.md`와 `docs/report/final-report.md`를 기준으로 설명합니다.

## 3. 에이전트 개발 하네스

본 프로젝트는 LLM이 작업할 때마다 같은 기준을 따르도록 작업 규칙과 검증 절차를 고정했습니다. 이 구조를 개발 하네스라고 설명할 수 있습니다.

| 구성 | 위치 | 역할 |
| --- | --- | --- |
| repo 규칙 | `AGENTS.md` | 한국어 응답, 문서 읽기 순서, Python 과제 조건, 완료 전 검증 절차를 고정 |
| 문서 라우터 | `docs/README.md` | PRD, roadmap, feature registry, architecture, testing, report 문서로 이동 |
| 기능 레지스트리 | `docs/contributing/feature-registry.md` | 기능별 소유 경로와 중복 작업 방지 기준 |
| 작업 상태 | `docs/contributing/plans-status.md` | 구현 상태, live smoke 결과, 다음 작업 후보 기록 |
| 설계/실행 계획 | `docs/superpowers/specs/`, `docs/superpowers/plans/` | 기능 구현 전 요구사항과 구현 순서 기록 |
| Codex 전용 스킬 | `~/.codex/skills/kmu-sw-navigator-*` | 새 Codex 세션이 repo 규칙, 완료 게이트, 다음 작업 판단 기준을 복원 |
| 검증 명령 | `package.json` scripts | 문서, Python, wiki, RAG ingest, frontend build를 반복 검증 |
| 제출용 기록 | `docs/llm/usage-log.md`, `docs/llm/agent-coding-evidence.md` | LLM 사용 목적, 산출물, 확인 내용을 기록 |

하네스를 둔 이유는 작업마다 기준이 달라지지 않게 하기 위해서입니다. 예를 들어 새 Codex 세션을 시작하더라도 먼저 repo 규칙을 읽고, 관련 문서를 확인하고, 변경 후 검증 명령을 실행하도록 만들었습니다. 이렇게 하면 프로젝트 설명, 코드 구조, 테스트 결과, 제출 문서가 서로 어긋나는 문제를 줄일 수 있습니다.

작업 흐름은 다음 순서로 반복했습니다.

```txt
요구사항 확인
-> AGENTS.md와 docs/README.md로 작업 규칙 복원
-> PRD/roadmap/feature registry로 범위 확인
-> spec 또는 plan 작성
-> 구현
-> 코드 구조, 보안, 과제 조건, 설명 가능성 확인
-> 테스트/빌드/문서 검증 실행
-> 실패하면 원인 분석 후 수정
-> LLM 사용 기록과 관련 문서 갱신
```

하네스가 실제로 적용된 예시는 다음과 같습니다.

| 상황 | 사용한 하네스 요소 | 결과 |
| --- | --- | --- |
| 새 기능 구현 전 | `docs/superpowers/specs/`, `docs/superpowers/plans/` | 기능 범위와 검증 기준을 먼저 정리했습니다. |
| 기능 상태 확인 | `docs/contributing/feature-registry.md`, `docs/contributing/plans-status.md` | 어떤 기능이 완료됐고 어떤 파일이 관련되는지 확인했습니다. |
| 문서와 코드 불일치 점검 | `docs/README.md`, `docs/architecture/`, `docs/report/` | 제출 문서가 실제 구현과 맞는지 점검했습니다. |
| 과제 조건 확인 | `pnpm submission:check` | 사용자 입력, 조건문, 반복문, 함수, 리스트/딕셔너리, 의미 있는 출력, 실행 가능한 Python, LLM 활용 기록 증거를 확인했습니다. |
| 문서 누락 확인 | `pnpm docs:check` | 필수 문서가 repo에 존재하는지 확인했습니다. |
| Python 백엔드 확인 | `pnpm test:backend`, `pnpm lint:backend` | API와 service 로직이 테스트와 lint를 통과하는지 확인했습니다. |
| 프론트엔드 확인 | `pnpm build:frontend` | React 앱이 production build를 통과하는지 확인했습니다. |

## 4. 팀원 데이터 정형화에서의 LLM 사용

이가은과 정재훈은 데이터 수집/정리 과정에서 Gemini와 ChatGPT를 사용했습니다. 이 과정의 목적은 원자료를 앱이 처리하기 쉬운 JSON 또는 Markdown 형태로 정리하는 것이었습니다.

| 팀원 | 사용 도구 | 처리한 자료 | 정리 결과 | 확인 방식 |
| --- | --- | --- | --- | --- |
| 이가은 | Gemini, ChatGPT | 학생회/학사 관련 자료 | `data/inbox/council.json` | 최종 지식베이스와 분리해 접수 자료로 보관하고, 출처/내용/개인정보 위험 확인 대상으로 표시 |
| 정재훈 | Gemini, ChatGPT | 동아리 자료 | `data/inbox/clubs_information.json`, Markdown 자료 | 동아리명, 활동 내용, 지원 대상, 출처 확인 필요 항목을 사람이 확인할 수 있게 분리 |

`data/inbox`를 사용한 이유는 팀원이 정리한 자료를 바로 RAG 검색 근거로 넣지 않고, 먼저 접수 자료로 분리하기 위해서입니다. 이후 실제 반영 단계에서는 출처, category, placeholder, 개인정보 위험을 확인한 뒤 `data/raw`와 `data/wiki`로 옮기는 절차를 사용합니다.

## 5. 앱 기능별 Gemini API 사용

앱 내부 Gemini API 사용 기록은 별도로 `llm_usage_logs` 테이블과 `GET /api/llm-logs` API에서 조회할 수 있게 연결했습니다. 개발 과정의 LLM 활용 기록은 위 팀원별 표와 하네스 설명으로 제출하고, 앱 기능에서의 Gemini 사용은 아래처럼 구분합니다.

| 기능 | 모델 | 목적 | 코드에서 담당한 부분 |
| --- | --- | --- | --- |
| RAG 챗봇 | `gemini-3-flash-preview`, `gemini-3.1-flash-lite` | 검색된 자료, 상담 모드, 사용자 입력을 바탕으로 자연어 답변 생성 | 검색 근거 선택, intent 분류, 사용자 메모리 주입, 응답 schema 관리 |
| 일정 파싱 | `gemini-3.1-flash-lite` | 자연어 일정에서 제목, 과목, 마감일 JSON 추출 | D-Day 계산과 저장 payload 생성 |
| 임베딩 | `gemini-embedding-2` | 문서 chunk와 사용자 질문 embedding 생성 | ingest 대상 문서, source_type, chunk metadata 관리 |
| 최신 웹 grounding | `gemini-3-flash-preview` | 취업/창업/공모전/소융대 공지처럼 최신성이 필요한 답변 보강 | 최신성이 필요한 intent에서만 호출하고, 내부 RAG 근거와 웹 근거를 분리 표시 |

앱 내부 LLM 기록은 개발 과정의 LLM 활용 기록과 구분합니다. 개발 과정의 기록은 이 문서의 팀원별 표와 하네스 설명이고, 앱 내부 기록은 실제 사용자가 채팅하거나 일정 파싱, embedding ingest, grounding을 실행했을 때 남는 서비스 로그입니다.

## 6. 제출 시 설명할 핵심 포인트

교수님에게 설명할 때는 다음 순서로 말하면 됩니다.

1. 우리 팀은 LLM을 개발 보조, 데이터 정형화 보조, 앱 기능 세 가지 범위로 나누어 사용했습니다.
2. 김성빈은 Codex, ChatGPT, Gemini API, Gemini Code Assist를 사용해 설계, 구현 보조, 오류 분석, 검증, 보고서 정리를 했습니다.
3. 차성민은 Codex를 사용해 프론트엔드 API fallback과 팀 역할 문서 정리를 보조했습니다.
4. 이가은과 정재훈은 Gemini와 ChatGPT를 사용해 수집 자료를 JSON/Markdown 형태로 정리했습니다.
5. 앱 내부에서는 Gemini API를 RAG 답변 생성, 일정 파싱, embedding, 최신 웹 grounding에 사용했습니다.
6. 개발 과정은 `AGENTS.md`, `docs/README.md`, feature registry, Superpowers spec/plan, Codex 전용 스킬, 검증 명령으로 관리했습니다.
7. 제출 조건은 `pnpm submission:check`, 문서 존재 여부는 `pnpm docs:check`, 백엔드와 프론트엔드는 테스트/린트/build 명령으로 확인했습니다.
