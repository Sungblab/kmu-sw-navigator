# Repo Docs Initialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 공개 GitHub repo로 올릴 수 있는 초기 문서, 개발 가이드, LLM 활용 기록, 최소 실행 skeleton을 만든다.

**Architecture:** root는 README와 기여 문서를 제공하고, `docs/README.md`가 세부 문서 라우터 역할을 한다. 백엔드는 FastAPI skeleton, 프론트엔드는 Vite React skeleton, Supabase는 schema SQL로 시작한다.

**Tech Stack:** Python 3.12, FastAPI, uv, React, Vite, TypeScript, Tailwind CSS, Supabase, Gemini API.

---

### Task 1: Repository Public Surface

**Files:**
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `AGENTS.md`
- Create: `SECURITY.md`
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `.env.example`

- [x] **Step 1: README 작성**

프로젝트 목적, 기술 스택, 빠른 시작, 문서 읽기 순서, 과제 조건 매핑을 한국어로 작성한다.

- [x] **Step 2: 기여 가이드 작성**

팀원이 브랜치, 커밋, PR, LLM 활용 기록, 검증 명령을 이해할 수 있도록 작성한다.

- [x] **Step 3: Agent guide 작성**

Codex와 팀원이 문서 읽기 순서, Superpowers 흐름, 코드 규칙을 따르도록 작성한다.

### Task 2: Docs Router And Collaboration Records

**Files:**
- Create: `docs/README.md`
- Create: `docs/contributing/dev-guide.md`
- Create: `docs/contributing/roadmap.md`
- Create: `docs/contributing/feature-registry.md`
- Create: `docs/contributing/plans-status.md`
- Create: `docs/collaboration/team-roles.md`
- Create: `docs/collaboration/workflow.md`
- Create: `docs/collaboration/meeting-notes.md`

- [x] **Step 1: docs index 작성**

`docs/README.md`가 제품, 개발, 협업, LLM, Superpowers, 테스트, 제출 문서로 라우팅한다.

- [x] **Step 2: 팀 역할 기록**

초기에는 김성빈을 PM으로 기록하고 나머지 팀원은 구체 분담 전으로 두었다. 현재 역할은 차성민 개발, 이가은/정재훈 데이터 수집/정리, 비타/최승범 발표자료로 `docs/collaboration/team-roles.md`에 갱신했다.

### Task 3: LLM Workflow Records

**Files:**
- Create: `docs/llm/codex-workflow.md`
- Create: `docs/llm/usage-log.md`
- Create: `docs/llm/prompt-summary-log.md`
- Create: `docs/superpowers/specs/2026-05-13-kmu-sw-navigator-design.md`
- Create: `docs/superpowers/plans/2026-05-13-repo-docs-initialization.md`

- [x] **Step 1: Codex workflow 문서화**

Brainstorming, spec, plan, implementation, verification, completion record 흐름을 설명한다.

- [x] **Step 2: usage log 초기 기록 작성**

2026-05-13의 PRD 검토, OpenCairn 문서 구조 조사, repo 초기화 준비를 기록한다.

### Task 4: Minimal App Skeleton

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/tests/test_health.py`
- Create: `frontend/package.json`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/styles.css`
- Create: `supabase/schema.sql`
- Create: `supabase/seed.sql`

- [x] **Step 1: FastAPI health endpoint 작성**

`GET /health`가 `{ "status": "ok" }`를 반환한다.

- [x] **Step 2: Vite React skeleton 작성**

한국어 landing shell과 4개 핵심 기능 카드를 표시한다.

- [x] **Step 3: Supabase 초기 schema 작성**

profiles, document_chunks, assignments, chat_logs, llm_usage_logs, match RPC를 만든다.

### Task 5: Verification And First Commit

**Files:**
- Create: `scripts/check_docs.py`

- [x] **Step 1: 문서 체크 스크립트 작성**

필수 문서 파일 존재 여부를 검사한다.

- [x] **Step 2: 검증 실행**

Run:

```powershell
pnpm docs:check
python -m py_compile scripts/check_docs.py backend/app/main.py
pnpm build:frontend
cd backend
uv sync
uv run pytest
uv run ruff check .
```

Result:

- 필수 문서 16개 확인 완료
- Python syntax check 통과
- frontend production build 통과
- backend health test 1개 통과
- ruff check 통과

- [x] **Step 3: 첫 커밋**

Run:

```powershell
git init -b main
git add .
git commit -m "docs: initialize project repository"
```

- [ ] **Step 4: GitHub public repo 생성과 push**

Run:

```powershell
gh repo create Sungblab/kmu-sw-navigator --public --source=. --remote=origin --push
```
