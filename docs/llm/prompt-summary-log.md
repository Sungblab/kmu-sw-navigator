# 프롬프트 요약 기록

전체 프롬프트를 그대로 저장하지 않고, 중요한 요청과 결정만 요약합니다.

## 2026-05-13

| 순서 | 요청 요약 | 결정 |
| --- | --- | --- |
| 1 | 기존 PRD Markdown을 읽고 구현 방향 구상 | 국민대 소프트웨어융합대학 신입생 RAG AI 도우미 방향 확인 |
| 2 | 실제 완성형 웹앱으로 만들고 과제 조건을 반영 | React + FastAPI + Supabase + Gemini 구조 유지 |
| 3 | 팀은 6명이고 김성빈이 PM | 초기에는 김성빈만 역할 확정, 이후 차성민은 개발, 이가은/정재훈은 데이터 수집/정리, 비타/최승범은 발표자료로 분담 |
| 4 | 기술 스택과 OpenCairn 문서 구조 조사 | docs index, roadmap, feature registry, dev guide, Superpowers spec/plan 구조 도입 |
| 5 | repo와 문서 세팅 후 GitHub public 공개 | README, CONTRIBUTING, AGENTS, docs, LLM 기록 구조를 첫 커밋에 포함 |
| 6 | pnpm 구조와 Docker 필요 여부 검토 | pnpm workspace + uv backend로 정리하고, Docker는 Supabase 로컬 재현 시 선택 사항으로 문서화 |
| 7 | Karpathy LLM Wiki 아이디어와 로컬 OpenCairn/UnivMind 구현 참고 | Mini LLM Wiki를 앱 핵심 RAG 효율화 계층으로 도입 |
| 8 | 프론트와 백엔드 개발 순서 질문 | 기능 하나씩 API 계약, 얇은 백엔드, 프론트 연결, 실제 로직, 검증 순서로 vertical slice를 만들기로 결정 |
| 9 | 개발 현황을 따라가는 Codex 스킬 필요 | `kmu-freshman-ai-next-step` 스킬을 만들어 문서와 실제 구현을 대조한 뒤 다음 구현 단위를 추천하도록 설정 |
| 10 | Codex 세팅, AGENTS.md, 스킬, 하네스 구조를 LLM 사용 보고서에 정리해야 함 | `docs/llm/codex-workflow.md`에 LLM 개발 하네스 섹션을 추가하고 보고서에서 설명할 근거로 사용 |
| 11 | 신입생 전용이 아니라 소프트웨어융합대학 전체 학년과 진로/취업/창업 고민까지 다루고 싶음 | 제품 범위를 개인화 SW 내비게이터로 확장하고 레포 이름 변경은 구현 안정화 후 검토 |
| 12 | 필수 정보는 최소로 받고 나머지는 대화형으로 파악하고 메모리에 저장하고 싶음 | 필수 프로필은 소속, 학년, 입학년도/교과과정 3개로 제한하고 관심사/고민은 대화형 메모리로 저장 |
| 13 | 최신 진로 정보는 Google grounding이 필요하고, 학교 자료는 사전 구축 지식으로 넣고 싶음 | raw Markdown/JSON, Mini LLM Wiki, embedding RAG, Google Search grounding을 지식 소스로 분리 |
| 14 | Claude처럼 답변 중간에 1, 2, 직접 입력 선택지를 주는 UX가 좋음 | Conversational Choice Pattern을 설계에 포함하고 선택 결과를 memory/intention 구조로 저장 |
| 15 | 자연어 과제 입력과 Google Calendar 내보내기를 MVP에 포함하고 싶음 | eCampus 직접 크롤링은 제외하고 자연어/복붙 일정 추출, D-day, Google Calendar export를 MVP 범위로 확정 |

## 2026-05-16

| 순서 | 요청 요약 | 결정 |
| --- | --- | --- |
| 1 | 교수님이 에이전트를 써서 코딩하는 과정을 중요하게 본다고 하며 문서 보강 요청 | `docs/llm/agent-coding-evidence.md`를 추가해 Codex/Superpowers/Gemini Code Assist/Gemini API 역할, 하네스, 직접 검토 기준, 과제 조건 연결을 설명하기로 결정 |
| 2 | 교수님이 LLM이 만들어준 코드를 그대로 쓰면 안 된다고 했고 Python 파일에 주석을 자세히 적었다고 공유 | 주석만으로 설명하지 않고 `python-core-logic`, `agent-coding-evidence`, `submission:check`에 직접 검토/수정/테스트 증거를 추가하기로 결정 |
| 3 | 답변을 끝내기 전에 문서 업데이트 필요 여부를 항상 생각하는 제약을 원함 | `AGENTS.md`에 문서 갱신 판단 게이트를 추가하되, 필요 없으면 불필요한 문서 수정은 생략하도록 정리 |
