# Sprint Tracking Protocol

> **Priority**: CRITICAL — Enforced by session checklists
> **SSOT**: `docs/ROADMAP.md` is the **only** place where task status is tracked

---

## Core Principle

> **`docs/ROADMAP.md` is the Single Source of Truth.**
> No task status lives outside this file. No exceptions.
> If it's not in ROADMAP.md, it doesn't exist as a tracked item.

---

## Session Start Protocol

1. **Read** `docs/ROADMAP.md` — load current sprint state
2. **Identify** in-progress `[/]` items from last session
3. **Present** sprint state summary to user before starting work
4. **Validate** against `docs/ARCHITECTURE.md` for structural context
5. **Begin** work only after user confirms direction

---

## Session End Protocol

1. **Update** `docs/ROADMAP.md` with completed `[x]` and in-progress `[/]` items
2. **Sync** `docs/CHANGELOG.md` with shipped work from this session
3. **Update** `.agent/session-context.md` with handoff notes for next session
4. **Update** `.agent/session-state.json` with machine-readable metadata
5. **Verify** no duplicate entries exist (ROADMAP ↔ CHANGELOG ↔ session-context)
6. **Commit** all tracking files together in a single atomic commit

---

## Mid-Session Updates

- **Mark items `[/]`** when starting work on them
- **Mark items `[x]`** immediately when completing them
- **Add sub-items** under parent tasks as they're discovered
- **NEVER** mark items complete without verification

---

## Sprint Lifecycle States

| Marker | Meaning      | When to Use                          |
| :----- | :----------- | :----------------------------------- |
| `[ ]`  | Not started  | Task exists but work hasn't begun    |
| `[/]`  | In progress  | Actively being worked on             |
| `[x]`  | Completed    | Done and verified                    |
| `[-]`  | Cancelled    | Intentionally dropped with reason    |

---

## Sprint Question Protocol

When the user asks about sprint status:

1. **ALWAYS** read `docs/ROADMAP.md` first
2. **PRESENT** the current state from the file
3. **NEVER** answer from memory — the file is the source of truth
4. If file is stale or missing, inform user and offer to create/update it

---

## Reject & Escalate Rules

### REJECT (Agent must refuse)

- Tracking task status in `session-context.md` instead of `ROADMAP.md`
- Creating duplicate task lists in multiple files
- Marking tasks complete without verification
- Updating CHANGELOG without updating ROADMAP

### ESCALATE (Agent must ask user)

- Sprint scope changes (adding/removing major items)
- Changing sprint deadlines
- Deferring critical-path items to next sprint
- Architecture changes that affect sprint estimates

---

## Cultural References

> These organizations exemplify the sprint discipline we enforce:

| Company    | Practice We Adopt                          |
| :--------- | :----------------------------------------- |
| Stripe     | Ship fast, measure everything, iterate     |
| Amazon     | Two-pizza teams, ownership, bias for action |
| Anthropic  | Safety-first, no shortcuts on quality      |
| Linear     | Opinionated tooling, consistent execution  |

---

## Version History

| Version | Date       | Changes                                    |
| :------ | :--------- | :----------------------------------------- |
| 1.0.0   | 2026-03-15 | Initial sprint tracking protocol for kit   |
