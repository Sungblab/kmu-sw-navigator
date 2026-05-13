# Mini LLM Wiki Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** raw markdown 자료를 신입생용 wiki page로 정리하고, RAG 검색을 위해 raw/wiki chunk 메타데이터를 준비한다.

**Architecture:** Python service가 `data/raw/*.md`를 읽고 category별 wiki markdown을 생성한다. OpenCairn의 heading-aware chunking과 UnivMind의 `_index` 중심 wiki 구조를 과제 규모에 맞게 단순화한다.

**Tech Stack:** Python 3.12, FastAPI backend package, Markdown files, Supabase SQL, pytest, ruff.

---

### Task 1: Raw/Wiki Data Layout

**Files:**
- Create: `data/raw/freshman-guide.md`
- Create: `data/raw/kmu-sw-tracks.md`
- Create: `data/raw/kmu-clubs.md`
- Create: `data/raw/kmu-roadmaps.md`
- Create: `data/wiki/.gitkeep`
- Modify: `data/README.md`

- [x] **Step 1: Define layout**

`data/raw/` stores source markdown with optional frontmatter. `data/wiki/` stores generated wiki pages.

### Task 2: Markdown Chunker TDD

**Files:**
- Create: `backend/tests/services/test_markdown_chunker.py`
- Create: `backend/app/services/markdown_chunker.py`

- [x] **Step 1: Write failing tests**

Tests cover heading path, content hash, chunk index, and long paragraph splitting.

- [x] **Step 2: Run tests and verify RED**

Run:

```powershell
cd backend
uv run pytest tests/services/test_markdown_chunker.py -q
```

Expected: import failure because `app.services.markdown_chunker` does not exist.

Result: `ModuleNotFoundError: No module named 'app.services'`

- [x] **Step 3: Implement chunker**

Implement `chunk_markdown(text: str, max_chars: int = 1200) -> list[MarkdownChunk]`.

- [x] **Step 4: Run tests and verify GREEN**

Run:

```powershell
cd backend
uv run pytest tests/services/test_markdown_chunker.py -q
```

Expected: all tests pass.

Result: `2 passed`

### Task 3: Wiki Compiler TDD

**Files:**
- Create: `backend/tests/services/test_wiki_compiler.py`
- Create: `backend/app/services/wiki_compiler.py`
- Create: `backend/app/scripts/build_wiki.py`

- [x] **Step 1: Write failing tests**

Tests cover raw document parsing, category grouping, wiki page frontmatter, index generation, and log generation.

- [x] **Step 2: Run tests and verify RED**

Run:

```powershell
cd backend
uv run pytest tests/services/test_wiki_compiler.py -q
```

Expected: import failure because `app.services.wiki_compiler` does not exist.

Result: `ModuleNotFoundError: No module named 'app.services'`

- [x] **Step 3: Implement compiler and CLI**

Implement:

- `parse_raw_document(path: Path) -> RawDocument`
- `compile_wiki(raw_documents: list[RawDocument], generated_at: date) -> WikiBuild`
- `write_wiki(build: WikiBuild, output_dir: Path) -> None`
- CLI: `python -m app.scripts.build_wiki --raw-dir ../data/raw --wiki-dir ../data/wiki`

- [x] **Step 4: Run tests and verify GREEN**

Run:

```powershell
cd backend
uv run pytest tests/services/test_wiki_compiler.py -q
```

Expected: all tests pass.

Result: `3 passed`

### Task 4: Schema And Docs

**Files:**
- Modify: `supabase/schema.sql`
- Modify: `supabase/seed.sql`
- Modify: `README.md`
- Modify: `docs/architecture/rag-design.md`
- Modify: `docs/contributing/roadmap.md`
- Modify: `docs/contributing/feature-registry.md`
- Modify: `docs/llm/usage-log.md`
- Modify: `docs/llm/prompt-summary-log.md`
- Modify: `scripts/check_docs.py`

- [x] **Step 1: Extend schema**

Add `raw_documents`, `wiki_pages`, `wiki_logs`, and chunk metadata columns.

- [x] **Step 2: Update docs**

Document Mini LLM Wiki as the core RAG efficiency layer.

### Task 5: Verification, Commit, Push

**Files:**
- Modify: `docs/superpowers/plans/2026-05-13-mini-llm-wiki.md`

- [x] **Step 1: Generate wiki pages**

Run:

```powershell
cd backend
uv run python -m app.scripts.build_wiki --raw-dir ..\data\raw --wiki-dir ..\data\wiki
```

Result: `raw_documents=4`, `wiki_pages=4`

- [x] **Step 2: Run full verification**

Run:

```powershell
pnpm docs:check
cd backend
uv run pytest
uv run ruff check .
cd ..
pnpm build:frontend
```

Result:

- `pnpm docs:check`: 필수 문서 19개 확인 완료
- `python -m py_compile ...`: 통과
- `uv run pytest`: 6 passed
- `uv run ruff check .`: All checks passed
- `pnpm build:frontend`: built successfully

- [x] **Step 3: Commit and push to main**

Run:

```powershell
git add .
git commit -m "feat: add mini llm wiki foundation"
git push
```

Result: committed as `feat: add mini llm wiki foundation` and pushed to `origin/main`.
