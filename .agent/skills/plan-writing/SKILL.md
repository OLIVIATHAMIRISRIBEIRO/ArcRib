---
name: plan-writing
description: Structured task planning with clear breakdowns, dependencies, and verification criteria.
version: 1.0.0
allowed-tools: Read, Glob, Grep
---

# Plan Writing

> Small tasks, clear outcomes, verifiable results.

---

## Overview

Framework for breaking down work into clear, actionable tasks with verification criteria.

---

## Task Breakdown Principles

### 1. Small, Focused Tasks

- Each task: 2-5 minutes
- One clear outcome per task
- Independently verifiable

### 2. Clear Verification

- How do you know it's done?
- What can you check/test?
- What's the expected output?

### 3. Logical Ordering

- Dependencies identified
- Parallel work where possible
- Critical path highlighted
- **Verification is always LAST**

---

## Planning Principles

> 🔴 **NO fixed templates. Each plan's CONTENT is UNIQUE to the task.**
> ✅ **Every plan MUST satisfy the quality schema in `plan-schema.md`.**
> Dynamic content within a consistent structure = the standard.

### Principle 1: Right-Size to Task Tier

Plan length MUST match task complexity:

| Task Tier | Max Sections | Max Tasks | Guideline |
| --------- | ------------ | --------- | --------- |
| **Trivial** (1-2 files) | Tier 1 only (7 sections) | 5-8 tasks | ~1 page — concise, no specialist synthesis |
| **Medium** (3-10 files) | Tier 1 + Tier 2 (15 sections) | 8-15 tasks | 2-3 pages — includes specialist input |
| **Large** (10+ files) | Tier 1 + Tier 2 + domains (15+ sections) | 15-25 tasks | 3-5 pages — full multi-agent synthesis |

| ❌ Wrong | ✅ Right |
| -------- | -------- |
| 50 tasks with sub-sub-tasks | Right-sized task count per tier |
| Every micro-step listed | Only actionable items |
| Verbose descriptions | One-line per task |
| Large task crammed into 1 page | Large task gets full Tier 2 coverage |
| Trivial task with 15 sections | Trivial task uses Tier 1 only |

> **Rule:** Trivial tasks stay concise (~1 page). Medium/Large tasks expand to cover all required tier sections. Never sacrifice completeness for brevity on complex tasks.

---

### Principle 2: Be SPECIFIC, Not Generic

| ❌ Wrong             | ✅ Right                                                 |
| -------------------- | -------------------------------------------------------- |
| "Set up project"     | "Run `npx create-next-app`"                              |
| "Add authentication" | "Install next-auth, create `/api/auth/[...nextauth].ts`" |
| "Style the UI"       | "Add Tailwind classes to `Header.tsx`"                   |

---

### Principle 3: Dynamic Content Based on Context

**For NEW PROJECT:**

- What tech stack?
- What's the MVP?
- What's the file structure?

**For FEATURE ADDITION:**

- Which files are affected?
- What dependencies needed?
- How to verify it works?

**For BUG FIX:**

- What's the root cause?
- What file/line to change?
- How to test the fix?

---

### Principle 4: Verification is Simple

| ❌ Wrong                     | ✅ Right                                     |
| ---------------------------- | -------------------------------------------- |
| "Verify the component works" | "Run `npm run dev`, click button, see toast" |
| "Test the API"               | "curl localhost:3000/api/users returns 200"  |
| "Check styles"               | "Open browser, verify dark mode works"       |

---

### Principle 5: Cross-Cutting Concerns Are Mandatory

Every plan MUST explicitly address:

1. **Security**: Reference `.agent/rules/security.md` — what security implications exist?
2. **Testing**: Reference `.agent/rules/testing.md` — what test types are needed? Coverage targets?
3. **Documentation**: Reference `.agent/rules/documentation.md` — which docs need updating?

If a concern is genuinely not applicable, state `N/A — [one-line justification]`.

**NEVER silently omit these sections.** Silent omission is a plan defect.

---

### Principle 6: Schema Compliance

Every plan MUST satisfy the quality schema defined in `plan-schema.md`:

- **Tier 1** sections are ALWAYS required. Omitting any Tier 1 section is a plan defect.
- **Tier 2** sections are required for Medium and Large tasks (3+ files or 1+ hours).
- Before presenting a plan, validate it against the schema checklist.
- Plans scoring below 70% of their tier maximum must be revised before presentation.

See also: `domain-enhancers.md` for domain-specific plan sections.

---

## Plan Structure (Minimal)

```markdown
# [Task Name]

## Goal

One sentence: What are we building/fixing?

## Tasks

- [ ] Task 1: [Action] → Verify: [Check]
- [ ] Task 2: [Action] → Verify: [Check]
- [ ] Task 3: [Action] → Verify: [Check]

## Done When

- [ ] [Main success criteria]

## Notes

[Any important considerations]
```

> **That's it.** No phases, no sub-sections unless truly needed.

---

## Best Practices

1. **Start with goal** — What are we building/fixing?
2. **Max 10 tasks** — If more, break into multiple plans
3. **Each task verifiable** — Clear "done" criteria
4. **Project-specific** — No copy-paste templates
5. **Update as you go** — Mark `[x]` when complete

---

## When to Use

- New project from scratch
- Adding a feature
- Fixing a bug (if complex)
- Refactoring multiple files
