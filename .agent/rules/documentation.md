# Documentation Rules

> **Priority**: HIGH — Enforced in reviews

---

## Document Hierarchy

| File                     | Role                         | Update Frequency    |
| :----------------------- | :--------------------------- | :------------------ |
| `docs/ARCHITECTURE.md`   | System design, tech stack    | On architecture changes |
| `docs/ROADMAP.md`        | Sprint tracking (SSOT)       | Every session start/end |
| `docs/CHANGELOG.md`      | Shipped work log             | Every session end       |
| `.agent/session-context.md` | Session handoff context   | Every session end       |
| `.agent/session-state.json` | Machine-readable metadata | Every session end       |

---

## ROADMAP.md as SSOT

**`docs/ROADMAP.md` is the Single Source of Truth for sprint tracking.**

- **NEVER** track task status in any other file
- **ALWAYS** read ROADMAP.md at session start before doing anything
- **UPDATE** ROADMAP.md at session end with completed/in-progress items
- **PRESENT** sprint state to user after loading

---

## CHANGELOG.md Format

Follow [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [Sprint X] — YYYY-MM-DD

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description
```

---

## Inline Documentation

- **WHY over WHAT**: Comments explain rationale, not mechanics
- **Complex logic**: Every non-obvious algorithm needs a comment explaining WHY it exists
- **API docs**: Public APIs documented with JSDoc/docstrings
- **No stale comments**: If code changes, comments must change too

---

## Preservation Rule

**No valuable content shall be silently deleted.**

- When updating files, apply changes **additively**
- If content must be removed, explicitly document what was removed and why
- Never silently drop sections when rewriting files

---

## Cross-Reference Integrity

**When referencing actions in other files, complete those actions in the same commit.**

- **Reference = Action**: "Move to X.md" means update X.md immediately
- **Completion Check**: Verify all referenced actions are completed
- **No broken links**: All file references must point to existing files
