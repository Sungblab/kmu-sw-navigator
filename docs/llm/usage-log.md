# LLM 활용 기록

이 문서는 제출용 LLM 활용 기록입니다. 앱에서 Gemini API를 사용한 로그는 DB의 `llm_usage_logs`에 저장하고, 개발 과정에서 사용한 LLM 기록은 이 문서에 남깁니다.

## 기록 형식

| 날짜 | 작성자 | 도구 | 목적 | 결과 | 직접 검토/수정 |
| --- | --- | --- | --- | --- | --- |
| 2026-05-13 | 김성빈 | Codex | PRD 검토와 MVP 방향 확정 | 완성형 웹앱 + LLM 협업 기록 강화 방향 확정 | 김성빈이 주제와 팀 운영 방향을 확정 |
| 2026-05-13 | 김성빈 | Codex | OpenCairn 문서 구조 조사 | docs index, roadmap, feature registry, dev guide, Superpowers spec/plan 구조를 본 프로젝트에 맞게 축소 | 과제 repo에는 private docs가 아니라 제출 증거로 docs/superpowers를 포함하기로 결정 |
| 2026-05-13 | 김성빈 | Codex | repo 초기 문서와 공개 GitHub 세팅 준비 | README, CONTRIBUTING, AGENTS, docs 구조, LLM 기록 템플릿 작성 | 김성빈이 PM/개발 리드 역할과 팀원 역할 미정을 반영 |
| 2026-05-13 | 김성빈 | Codex | 패키지 구조와 GitHub 운영 방식 정리 | pnpm workspace, uv backend, Docker 선택 사항, PR/Issue 템플릿, verify workflow 구성 | 수업 MVP에서는 Supabase Cloud를 기본으로 쓰고 Docker를 필수 요구사항에서 제외하기로 결정 |

## 앱 기능별 Gemini API 기록 예정 항목

| 기능 | 모델 | 목적 |
| --- | --- | --- |
| RAG 챗봇 | `gemini-3-flash-preview` | 검색된 자료를 바탕으로 신입생 질문에 답변 |
| 일정 파싱 | `gemini-3.1-flash-lite` | 자연어 일정에서 제목, 과목, 마감일 JSON 추출 |
| 질문 분류 | `gemini-3.1-flash-lite` | 질문 유형 분류와 간단 요약 |
| 임베딩 | `gemini-embedding-2` | 문서 chunk와 사용자 질문 embedding 생성 |
