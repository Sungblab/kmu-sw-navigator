# LLM 활용 기록

이 문서는 제출용 LLM 활용 기록입니다. 앱에서 Gemini API를 사용한 로그는 DB의 `llm_usage_logs`에 저장하고, 개발 과정에서 사용한 LLM 기록은 이 문서에 남깁니다.

## 기록 형식

| 날짜 | 작성자 | 도구 | 목적 | 결과 | 직접 검토/수정 |
| --- | --- | --- | --- | --- | --- |
| 2026-05-13 | 김성빈 | Codex | PRD 검토와 MVP 방향 확정 | 완성형 웹앱 + LLM 협업 기록 강화 방향 확정 | 김성빈이 주제와 팀 운영 방향을 확정 |
| 2026-05-13 | 김성빈 | Codex | OpenCairn 문서 구조 조사 | docs index, roadmap, feature registry, dev guide, Superpowers spec/plan 구조를 본 프로젝트에 맞게 축소 | 과제 repo에는 private docs가 아니라 제출 증거로 docs/superpowers를 포함하기로 결정 |
| 2026-05-13 | 김성빈 | Codex | repo 초기 문서와 공개 GitHub 세팅 준비 | README, CONTRIBUTING, AGENTS, docs 구조, LLM 기록 템플릿 작성 | 김성빈이 PM/개발 리드 역할과 팀원 역할 미정을 반영 |
| 2026-05-13 | 김성빈 | Codex | 패키지 구조와 GitHub 운영 방식 정리 | pnpm workspace, uv backend, Docker 선택 사항, PR/Issue 템플릿, verify workflow 구성 | 수업 MVP에서는 Supabase Cloud를 기본으로 쓰고 Docker를 필수 요구사항에서 제외하기로 결정 |
| 2026-05-13 | 김성빈 | Codex | OpenCairn/UnivMind 구현 참고 후 Mini LLM Wiki 설계/구현 | raw/wiki 자료 구조, heading-aware chunker, wiki compiler, schema 확장, wiki 생성 script 추가 | LangGraph/worker는 과제 범위에서 제외하고 Python script로 축소 구현 |
| 2026-05-13 | 김성빈 | Codex | 코드 리뷰와 주석 기록 방식 정리 | Gemini Code Assist 자동 리뷰, 팀원 리뷰, 리뷰 반영/미반영 이유, 의도 주석을 제출 증거로 남기는 규칙 추가 | 리뷰 코멘트를 맹목적으로 반영하지 않고 직접 판단한 근거를 PR thread와 문서에 남기기로 결정 |
| 2026-05-13 | 김성빈 | Codex | 프로젝트 전용 Codex 스킬 세팅 | `~/.codex/skills/kmu-freshman-ai`에 과제 조건, 문서 라우팅, 검증, Gemini 리뷰 대응 절차를 담은 스킬 작성 | 새 세션에서도 동일한 작업 방식과 기록 기준을 유지하기 위한 로컬 개발 가이드로 사용 |
| 2026-05-13 | 김성빈 | Codex | 로그인/메인 HTML 목업 스타일 결정 | getdesign.md의 Cal.com 뉴트럴 UI를 참고해 랜딩페이지 없이 로그인/메인 앱 화면 목업 작성 | 발표 데모와 실제 React 구현 기준으로 쓰기 위해 튀지 않는 밝은 뉴트럴 스타일을 선택 |

## 앱 기능별 Gemini API 기록 예정 항목

| 기능 | 모델 | 목적 |
| --- | --- | --- |
| RAG 챗봇 | `gemini-3-flash-preview` | 검색된 자료를 바탕으로 신입생 질문에 답변 |
| 일정 파싱 | `gemini-3.1-flash-lite` | 자연어 일정에서 제목, 과목, 마감일 JSON 추출 |
| 질문 분류 | `gemini-3.1-flash-lite` | 질문 유형 분류와 간단 요약 |
| 임베딩 | `gemini-embedding-2` | 문서 chunk와 사용자 질문 embedding 생성 |
