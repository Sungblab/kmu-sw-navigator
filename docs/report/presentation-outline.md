# 발표자료 구성

발표영상은 20-25분을 목표로 합니다.

## 1. 주제 소개

- 국민대 소프트웨어융합대학 개인화 AI 내비게이터
- 학년별 학업/진로/프로젝트/일정 고민
- 왜 도메인 특화 RAG와 개인화 메모리가 필요한가

## 2. 시스템 구조

- React UI
- FastAPI Python backend
- Supabase Auth/Postgres/pgvector
- Gemini API
- Mini LLM Wiki와 RAG 흐름
- 사용자 프로필/메모리와 memory events
- Google Search grounding과 Google Calendar API

## 3. 라이브 기능 시연

1. 메인 workspace: 왼쪽 사이드바, 중앙 상담, 오른쪽 context panel
2. 설정 화면: Supabase 로그인 구조와 Google Calendar 연결 상태
3. 개인화 RAG 상담 질문
4. 개인화 근거, 내부 자료, 최신 웹 근거 확인
5. 진로/활동 추천 입력 직접 수정과 추천 결과 확인
6. 자연어 일정 등록
7. D-day, 완료/삭제, Google Calendar 내보내기
8. 메모리와 LLM 활용 기록 확인

## 4. 코드 설명

- FastAPI route 구조
- 메모리 저장 정책과 민감도 판단
- 추천 규칙 딕셔너리
- 조건문 분기
- chunk 반복 처리
- D-day 계산 함수
- Calendar 내보내기 중복 방지
- Supabase Direct/backend와 Framework/frontend env 분리
- `env:check`와 live smoke 절차
- LLM usage log 저장

## 5. LLM 활용과 협업 방식

- Codex로 PRD 분석, spec 작성, plan 작성, 문서 구조 설계
- Codex 전용 스킬과 `AGENTS.md`로 에이전트 작업 규칙 고정
- `docs/llm/agent-coding-evidence.md`로 에이전트 기반 코딩 과정 설명
- Gemini API로 앱 기능 구현
- Google grounding으로 최신 정보 보강
- LLM 결과는 직접 검토하고, 핵심 로직은 테스트와 주석으로 설명 가능한 코드로 수정
- LLM 사용 목적과 결과는 `docs/llm/usage-log.md`에 기록

## 6. 한계와 개선 방향

- 자료 최신화
- 더 많은 학과 확장
- Google Calendar 양방향 동기화
- eCampus 직접 연동
- RAG 평가 자동화
- 실제 Supabase/Gemini/Google 키를 넣은 live smoke 추가

## 7. 권장 시간 배분

| 구간 | 시간 |
| --- | --- |
| 문제 정의와 주제 소개 | 2-3분 |
| 시스템 구조 | 4분 |
| 앱 라이브 시연 | 9-10분 |
| Python 핵심 로직 설명 | 5분 |
| 에이전트 활용 기록과 직접 검증 | 3분 |
| 한계와 개선 방향 | 2분 |
