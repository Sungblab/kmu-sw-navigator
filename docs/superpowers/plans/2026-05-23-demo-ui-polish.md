# Demo UI Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the demo UI by rendering assistant markdown with Streamdown and surfacing user action results with Sonner toasts.

**Architecture:** Keep the current Vite React single-app structure. Add presentation-only dependencies in `frontend`, render assistant messages through a small markdown component, and keep backend/API contracts unchanged.

**Tech Stack:** React 19, Vite, Tailwind CSS 4, `streamdown`, `@streamdown/cjk`, `sonner`.

---

### Task 1: Add UI dependencies

**Files:**
- Modify: `frontend/package.json`
- Modify: `pnpm-lock.yaml`

- [x] **Step 1: Install presentation dependencies**

Run:

```powershell
pnpm --dir frontend add streamdown @streamdown/cjk sonner
```

Expected: `frontend/package.json` includes the three dependencies and lockfile updates.

### Task 2: Render assistant markdown and toasts

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`

- [x] **Step 1: Import dependencies**

Add `Streamdown`, CJK plugin wiring if required by the installed package API, and `Toaster`/`toast` from `sonner`.

- [x] **Step 2: Render assistant messages with Streamdown**

Keep user messages as plain text. For assistant messages, render `message.text` through a scoped markdown container so lists, links, code blocks, and tables are readable in the demo.

- [x] **Step 3: Add toast feedback**

Show success toasts after completed actions and error toasts inside existing catch branches. Keep `setError(...)` behavior so errors remain visible in the app surface.

- [x] **Step 4: Add Streamdown/Tailwind source hint**

If required by Tailwind 4 scanning, add a `@source` hint for Streamdown in `frontend/src/styles.css`.

### Task 3: Documentation and verification

**Files:**
- Modify: `docs/contributing/feature-registry.md`
- Modify: `docs/contributing/plans-status.md`
- Modify: `docs/llm/usage-log.md`

- [x] **Step 1: Record the UI polish slice**

Update feature/status/log docs to state that the change improves demo presentation only and does not alter backend contracts.

- [x] **Step 2: Verify**

Run:

```powershell
pnpm build:frontend
pnpm docs:check
git diff --check
```

Expected: all commands exit 0.

Result:

- `pnpm build:frontend`: passed
- `pnpm docs:check`: 필수 문서 20개 확인 완료
- `git diff --check`: passed
