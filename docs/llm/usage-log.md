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
| 2026-05-13 | 김성빈 | Codex | 모바일 웹앱 중심 목업 보정 | Pretendard 한글 폰트, 하단 탭바, sticky 상단바, safe-area, 48px 터치 타깃을 반영 | 실제 사용자는 휴대폰으로 볼 가능성이 높으므로 데스크톱보다 모바일 사용성을 우선하기로 결정 |
| 2026-05-13 | 김성빈 | Codex | 모바일 네비게이션 재검토 | 하단 고정 탭바를 제거하고 PC/모바일 모두 일반 상단 메뉴바 계열로 통일 | 모바일만 과하게 앱처럼 보이지 않도록 웹앱 전체의 일관성을 우선 |
| 2026-05-13 | 김성빈 | Codex | 챗봇 근거 시각화 목업 작성 | 채팅 답변 옆에 Mini Wiki/source 그래프, 학기별 로드맵, 추천 이유 체인을 배치한 HTML 목업 추가 | RAG 답변의 근거와 추천 판단 흐름을 발표에서 설명하기 쉽게 만들기로 결정 |
| 2026-05-13 | 김성빈 | Codex | 개발 현황 추적용 Codex 스킬 추가 | `~/.codex/skills/kmu-freshman-ai-next-step`에 문서, git 상태, 실제 코드, 검증 기록을 함께 읽고 다음 구현 단위를 추천하는 절차를 정리 | `plans-status.md`만 믿지 않고 실제 구현과 검증 근거를 대조하도록 스킬 목적을 제한 |
| 2026-05-13 | 김성빈 | Codex | LLM 개발 하네스 문서화 | `AGENTS.md`, `docs/README.md`, feature registry, Superpowers spec/plan, Codex 스킬, 검증 명령, 사용 기록이 연결되는 구조를 `docs/llm/codex-workflow.md`에 정리 | 보고서에서 “AI가 만든 코드”가 아니라 “AI를 통제하고 검증한 개발 절차”로 설명하기로 결정 |
| 2026-05-13 | 김성빈 | Codex | 개인화 SW 내비게이터 초기 설계 확정 | 신입생 전용 범위에서 전체 학년 대상의 학업/진로/프로젝트/일정 개인화 AI 내비게이터로 확장하는 umbrella spec 작성 | 필수 프로필은 최소화하고, 관심사/진로 고민은 대화형 선택지와 메모리로 쌓는 방향을 확정 |
| 2026-05-13 | 김성빈 | Codex | 메모리/RAG/grounding/Calendar 설계 정리 | `profiles`, `user_memories`, `memory_events`, 내부 RAG, Google grounding, Google Calendar export, 근거 표시 정책을 문서화 | 파인튜닝 대신 raw 자료, Mini LLM Wiki, embedding RAG, 최신 웹 grounding을 조합하기로 결정 |
| 2026-05-13 | 김성빈 | Codex | repo/product rename 정리 | 로컬 폴더, GitHub repo, package/workspace metadata, README, API title, frontend title, GitHub 설정 문서를 `kmu-sw-navigator` 방향으로 정렬 | 과거 LLM 사용 기록의 초기 스킬명은 당시 이름으로 보존하고 현재 사용자-facing 명칭만 갱신 |

## 앱 기능별 Gemini API 기록 예정 항목

| 기능 | 모델 | 목적 |
| --- | --- | --- |
| RAG 챗봇 | `gemini-3-flash-preview` | 검색된 자료를 바탕으로 신입생 질문에 답변 |
| 일정 파싱 | `gemini-3.1-flash-lite` | 자연어 일정에서 제목, 과목, 마감일 JSON 추출 |
| 질문 분류 | `gemini-3.1-flash-lite` | 질문 유형 분류와 간단 요약 |
| 임베딩 | `gemini-embedding-2` | 문서 chunk와 사용자 질문 embedding 생성 |
| 메모리 추출 | `gemini-3.1-flash-lite` | 대화에서 관심사, 진로 고민, 프로젝트 선호 저장 후보 추출 |
| 최신 웹 grounding | `gemini-3-flash-preview` | 취업/창업/공모전/기술 트렌드처럼 최신성이 필요한 답변 보강 |
