# 보고서 목차

보고서는 6-10페이지 분량을 목표로 합니다.

1. 프로젝트 개요
   - 프로젝트명
   - 개발 배경
   - 대상 사용자
   - 문제 정의
   - 로그인 사용자별 데이터가 저장되는 SaaS형 웹앱을 목표로 한 이유
   - 신입생 전용에서 소프트웨어융합대학 전체 학년으로 확장한 이유

2. 개발 목적
   - 신입생 정보 탐색 문제 해결
   - 도메인 특화 RAG 챗봇 구현
   - 개인화 메모리 기반 학업/진로/프로젝트 상담
   - Supabase Auth/Postgres 기반 사용자별 데이터 저장
   - 추천과 앱 내부 일정 관리 제공

3. 기술 스택
   - React + Vite + TypeScript
   - FastAPI + Python
   - Supabase Auth/Postgres/pgvector
   - Gemini API
   - Google Search grounding
   - Google Calendar API는 선택 확장 기능

4. 주요 기능
   - 개인화 AI 상담
   - 학교/학과 자료 기반 RAG
   - 진로/취업/창업 grounding
   - 트랙/활동/프로젝트 추천
   - 자연어 일정 관리, D-day, 완료/삭제
   - LLM 활용 기록

5. 시스템 구조
   - 전체 아키텍처
   - API 흐름
   - DB 구조
   - 프로필/메모리/메모리 이벤트 구조
   - 내부 RAG와 Google grounding 라우팅

6. 코드 구조와 주요 코드 설명
   - 사용자 입력 처리
   - 메모리 저장 정책과 민감도 판단
   - 인증 dependency와 user_id 결정
   - 저장소 protocol과 Supabase/in-memory fallback
   - 추천 조건문
   - 문서 검색 함수
   - Gemini 호출 함수
   - D-day 계산 함수
   - Calendar 내보내기를 선택 확장 기능으로 분리한 이유
   - 환경 점검과 live smoke 분리
   - 로그 저장 함수

7. 실행 결과
   - 온보딩/홈 화면
   - Supabase 로그인과 사용자별 profile 저장
   - 개인화 챗봇 답변
   - 근거 보기: 개인화 근거, 내부 자료, 최신 웹 근거
   - 추천 결과
   - 일정 등록, D-day, 완료/삭제
   - LLM 활용 기록 화면

8. LLM 활용 방식
   - Gemini API 사용 위치
   - Codex/Superpowers 개발 보조 방식
   - 에이전트 기반 코딩 활용 증거: `docs/llm/agent-coding-evidence.md`
   - AGENTS.md 기반 repo 규칙과 문서 읽기 순서
   - Codex 전용 스킬과 개발 현황 추적 스킬
   - spec/plan/verification으로 구성한 LLM 개발 하네스
   - Codex, Gemini Code Assist, Gemini API의 역할 구분
   - 직접 검토, 수정, 테스트한 내용
   - LLM 생성 코드를 그대로 제출하지 않기 위해 수행한 리팩토링과 설명 문서화

9. 한계와 개선 방향
   - 자료 범위 한계
   - 전체 학과 확장
   - Supabase/Gemini/Google live smoke 결과와 남은 외부 설정
   - Google Calendar OAuth 연동은 후속 선택 확장
   - RAG 품질 개선

## 보고서에 넣을 실행 근거

| 항목 | 근거 |
| --- | --- |
| Python 백엔드 테스트 | `pnpm test:backend` |
| 제출 증거 스크립트 테스트 | `python -m pytest tests` |
| Python lint | `pnpm lint:backend` |
| 프론트엔드 빌드 | `pnpm build:frontend` |
| 문서 구조 검증 | `pnpm docs:check` |
| 제출 조건 증거 검증 | `pnpm submission:check` |
| 환경 변수 점검 | `pnpm env:check` |
| Live smoke 준비 점검 | `pnpm live:smoke-plan -- --user-id <supabase-auth-user-uuid> --email <email> --password <password>` |
| Supabase live 검증 | 키와 Auth user 준비 후 `pnpm env:check:strict`, `pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>`, `pnpm supabase:login-smoke -- --email <email> --password <password>`, `pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>` |
| Google Calendar live 검증 | 선택 확장 기능. 이번 제출 필수 검증에서는 제외 |
| Gemini live 검증 | 키 설정 후 `pnpm gemini:smoke`, `pnpm gemini:answer-smoke`, `pnpm gemini:grounding-smoke`, `pnpm rag:ingest:embeddings` |

## 보고서 문장 초안

```txt
본 프로젝트는 LLM을 개발 보조 도구로 활용했지만, 핵심 Python 로직은 함수 단위로 분리하고 테스트를 작성해 직접 검증했다. 추천 기능은 LLM 임의 생성이 아니라 리스트/딕셔너리 기반 후보와 조건문 점수 계산으로 구현했으며, RAG와 Gemini는 답변의 근거와 자연어 생성을 보조하는 역할로 분리했다.
```

```txt
최종 목표는 Supabase Auth와 Postgres에 사용자별 프로필, 메모리, 채팅, 일정, LLM 활용 기록을 저장하는 SaaS형 학업 내비게이터다. 로컬 fallback은 외부 서비스 장애에 대비한 안전장치로 설명하고, 제출 전에는 가능한 live smoke 결과를 별도로 제시한다.
```

```txt
교수님이 중요하게 본 에이전트 기반 코딩 과정은 별도 문서와 로그로 남겼다. Codex는 PRD 분석, spec/plan 작성, 코드 수정, 검증 명령 실행, 실패 원인 분석에 사용했고, Gemini Code Assist는 리뷰 의견을 받는 데 사용했다. 단, 최종 코드는 사람이 직접 읽고 수정했으며 `pnpm verify:local`, backend tests, frontend build, docs check 같은 명령으로 동작을 확인했다.
```
