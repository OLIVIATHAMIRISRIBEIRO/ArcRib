# Session Start Checklist

> **Framework**: Antigravity AI Kit
> **Purpose**: Complete this checklist at the beginning of every work session  
> **Principle**: Full context before new work

---

## 🔄 Context Loading

- [ ] **session-context.md** loaded
  - Last session summary reviewed
  - Open items identified
  - Handoff context verified (not just session-end boilerplate)
- [ ] **session-state.json** loaded
  - Last commit verified
  - Current task identified
  - **Staleness check**: Compare `lastCommit` with `git log --oneline -1` — if diverged, flag to user
- [ ] **rules.md** loaded (if project has one)
  - Project-specific rules acknowledged

---

## 📋 Sprint State Validation

- [ ] **docs/ROADMAP.md** loaded (SSOT for sprint tracking)
  - Current sprint identified
  - In-progress `[/]` items from last session reviewed
  - Completed `[x]` items acknowledged
- [ ] **Sprint state presented** to user before starting work
  - Summary of where we left off
  - Proposed next items to work on
- [ ] **docs/ARCHITECTURE.md** reviewed for structural context
- [ ] **docs/CHANGELOG.md** reviewed for recent shipped work

---

## 📂 Project State

- [ ] **Git status** clean or understood
  ```bash
  git status
  git branch
  ```
- [ ] **Dependencies** up to date
  ```bash
  npm install  # or pnpm install
  ```
- [ ] **Build** passes
  ```bash
  npm run build
  ```

---

## 🎯 Task Context

Based on task type, load relevant context:

**For Feature Work:**

- [ ] Requirements document located
- [ ] Related existing code identified
- [ ] Test strategy understood

**For Bug Fixes:**

- [ ] Bug reproduction steps known
- [ ] Related logs/errors reviewed
- [ ] Affected code paths identified

**For Refactoring:**

- [ ] Scope of changes understood
- [ ] Test coverage verified
- [ ] Rollback plan considered

---

## ⚡ Quick Verification

- [ ] Development server starts
  ```bash
  npm run dev
  ```
- [ ] Tests pass
  ```bash
  npm test
  ```
- [ ] No critical errors in console

---

## ✅ Ready State

After completing this checklist:

1. ✅ Context fully loaded
2. ✅ Environment verified
3. ✅ Ready to begin task

**Proceed with**: `/plan` or `/implement`
