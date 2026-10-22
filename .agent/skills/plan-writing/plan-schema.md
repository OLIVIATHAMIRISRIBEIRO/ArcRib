# Plan Quality Schema

> Defines the mandatory structure and scoring rubric for implementation plans.
> Every plan produced by the `/plan` workflow MUST satisfy this schema.

---

## Task Size Classification

Before applying the schema, classify the task:

| Size | Criteria | Required Tiers |
|------|----------|----------------|
| **Trivial** | 1-2 files, <30 minutes estimated effort | Tier 1 only |
| **Medium** | 3-10 files, 1-4 hours estimated effort | Tier 1 + Tier 2 |
| **Large** | 10+ files, multi-day effort | Tier 1 + Tier 2 + architect consultation |

---

## Tier 1 — Always Required

Every plan, regardless of task size, MUST include these sections:

| # | Section | Description | Points |
|---|---------|-------------|--------|
| 1 | **Context & Problem Statement** | Why this change is needed. 2-3 sentences covering the problem, impact, and motivation. | 10 |
| 2 | **Goals & Non-Goals** | What the plan achieves (goals) and what is explicitly out of scope (non-goals). Prevents scope creep. | 10 |
| 3 | **Implementation Steps** | Ordered tasks with exact file paths, specific actions, and verification criteria per step. | 10 |
| 4 | **Testing Strategy** | Test types required (unit, integration, e2e), coverage targets, key test cases. Reference `.agent/rules/testing.md`. | 10 |
| 5 | **Security Considerations** | Applicable security requirements from `.agent/rules/security.md`. If genuinely not applicable, state `N/A — [one-line justification]`. | 10 |
| 6 | **Risks & Mitigations** | At least 1 risk with severity (Low/Medium/High) and concrete mitigation strategy. | 5 |
| 7 | **Success Criteria** | Measurable definition of done. Checkboxes with specific, verifiable outcomes. | 5 |

**Tier 1 Maximum: 60 points**

---

## Tier 2 — Required for Medium & Large Tasks

Plans for tasks affecting 3+ files or requiring 1+ hours MUST also include:

| # | Section | Description | Points |
|---|---------|-------------|--------|
| 8 | **Architecture Impact** | Affected components/modules, integration points, dependency changes. Include component diagram for Large tasks. | 4 |
| 9 | **API / Data Model Changes** | New or modified endpoints, request/response schemas, database schema changes. | 3 |
| 10 | **Rollback Strategy** | How to undo the change if deployment fails or defects are discovered post-release. | 3 |
| 11 | **Observability** | Logging additions, metrics to track, alerting changes, monitoring dashboards affected. | 2 |
| 12 | **Performance Impact** | Bundle size changes, query performance, latency estimates, memory usage. | 2 |
| 13 | **Documentation Updates** | Which docs need changing (ROADMAP, CHANGELOG, README, API docs, ADRs). Reference `.agent/rules/documentation.md`. | 2 |
| 14 | **Dependencies** | What blocks this work (prerequisites). What depends on this work (downstream impact). | 2 |
| 15 | **Alternatives Considered** | At least 1 rejected approach with reasoning for why the chosen approach is superior. | 2 |

**Tier 2 Maximum: 20 points (added to Tier 1)**

---

## Domain Enhancement Scoring

When the loading engine matches specific domains (e.g., frontend, backend, security), the corresponding domain enhancer sections from `domain-enhancers.md` MUST be included. Domain sections are scored as **bonus points** on top of the tier maximum:

| Condition | Scoring Impact |
|-----------|---------------|
| Domain matched and enhancer section present + substantive | +2 bonus points per domain |
| Domain matched but enhancer section missing | -2 penalty per missing domain (deducted from tier score) |
| Domain matched with "N/A — [valid reason]" | No bonus, no penalty |
| No domains matched | No impact |

**Maximum domain bonus**: +6 points (3 domains × 2 points each).

Domain scoring does NOT change the pass threshold — it provides additional quality signal. A plan can PASS without domain bonuses but will be penalized if matched domains are ignored.

---

## Scoring

| Task Size | Max Score | Pass Threshold (70%) |
|-----------|-----------|---------------------|
| Trivial | 60 | 42 |
| Medium | 80 | 56 |
| Large | 100 | 70 |

**Score Calculation**:
- A section earns full points when present and substantively populated
- A section earns zero points when missing or contains only placeholder text
- "N/A" with a valid justification counts as populated (earns full points)

**Verdict**:
- **PASS**: Score >= 70% of tier maximum
- **REVISE**: Score < 70% — identify missing sections and revise (max 2 revision cycles)

---

## Cross-Cutting Mandate

Regardless of task domain, these sections MUST be substantively addressed in every plan:

1. **Security Considerations** (Tier 1, #5) — Reference `.agent/rules/security.md`
2. **Testing Strategy** (Tier 1, #4) — Reference `.agent/rules/testing.md`
3. **Documentation Updates** (Tier 2, #13) — Reference `.agent/rules/documentation.md`

If a cross-cutting section is genuinely not applicable, the plan MUST state:
```
N/A — [specific reason this concern does not apply to this task]
```

**NEVER silently omit a cross-cutting section.** Silent omission is a plan defect.

---

## Alignment Verification

Every plan MUST include an alignment check against operating constraints:

| Check | Question |
|-------|----------|
| Operating Constraints | Does this respect Trust > Optimization? |
| Existing Patterns | Does this follow project conventions? |
| Rules Consulted | Which rule files were reviewed? |
| Coding Style | Does this comply with `.agent/rules/coding-style.md`? |
