---
name: plan-validation
description: Quality gate for implementation plans. Validates schema compliance, cross-cutting concerns, and completeness scoring before user presentation.
version: 1.0.0
triggers: [post-plan-creation]
allowed-tools: Read, Grep
---

# Plan Validation

> Quality gate ensuring every implementation plan meets enterprise standards
> before being presented to the user for approval.

---

## Overview

This skill is used by the planner agent as a self-validation checklist after creating a plan but BEFORE presenting it to the user. The planner applies the validation pipeline below to its own output, verifying against the quality schema (`plan-schema.md`), checking cross-cutting concerns, and calculating a completeness score. Plans that fail validation are revised before presentation.

**Invocation**: The planner runs this checklist during `/plan` workflow step 3.5. This is NOT a separate agent — the planner validates its own plan against these criteria.

---

## Validation Pipeline

### Step 1: Task Size Classification

Determine the task size from the plan content:

| Indicator | Classification |
|-----------|---------------|
| Plan references 1-2 files | **Trivial** |
| Plan references 3-10 files | **Medium** |
| Plan references 10+ files | **Large** |
| Estimated effort < 30 minutes | **Trivial** |
| Estimated effort 1-4 hours | **Medium** |
| Estimated effort > 4 hours | **Large** |

Use the HIGHER classification when indicators conflict.

### Step 2: Schema Compliance

Verify all required sections are present and substantively populated:

**Tier 1 Sections (Always Required)**:

| # | Section | Check |
|---|---------|-------|
| 1 | Context & Problem Statement | Present and >= 2 sentences |
| 2 | Goals & Non-Goals | Both goals AND non-goals stated |
| 3 | Implementation Steps | Steps have file paths and verification criteria |
| 4 | Testing Strategy | Test types specified with coverage targets |
| 5 | Security Considerations | Substantive content or explicit "N/A — [reason]" |
| 6 | Risks & Mitigations | At least 1 risk with severity and mitigation |
| 7 | Success Criteria | Measurable, checkable outcomes |

**Tier 2 Sections (Required for Medium/Large)**:

| # | Section | Check |
|---|---------|-------|
| 8 | Architecture Impact | Components and files identified |
| 9 | API / Data Model Changes | Schemas defined (or N/A with reason) |
| 10 | Rollback Strategy | Concrete undo procedure |
| 11 | Observability | Logging/metrics plan |
| 12 | Performance Impact | Assessment provided |
| 13 | Documentation Updates | Specific docs identified |
| 14 | Dependencies | Blockers and dependents listed |
| 15 | Alternatives Considered | At least 1 rejected alternative with reasoning |

### Step 3: Cross-Cutting Verification

These sections MUST be non-empty regardless of task domain:

| Section | Acceptable Content |
|---------|-------------------|
| **Security Considerations** | Specific requirements from `rules/security.md` OR `N/A — [valid justification]` |
| **Testing Strategy** | At least unit test plan with coverage target OR `N/A — [valid justification]` |
| **Documentation Updates** | Specific docs listed OR `N/A — no docs affected` |

**Unacceptable**: Empty section, placeholder text, section completely missing.

### Step 4: Specificity Audit

Verify that implementation steps are actionable, not vague:

| Vague (FAIL) | Specific (PASS) |
|-------------|-----------------|
| "Update the component" | "Add `onSubmit` handler to `src/components/LoginForm.tsx`" |
| "Add tests" | "Create `tests/auth.test.js` with login success/failure cases" |
| "Fix the bug" | "Change line 42 of `lib/parser.js`: replace `==` with `===`" |
| "Style the UI" | "Add Tailwind classes `flex gap-4 p-6` to `Header.tsx`" |

**Rule**: Every implementation step MUST include a file path.

### Step 5: Completeness Scoring

Calculate the score using the rubric from `plan-schema.md`:

**Tier 1 Scoring** (60 points max):

| Section | Points |
|---------|--------|
| Context & Problem Statement | 10 |
| Goals & Non-Goals | 10 |
| Implementation Steps | 10 |
| Testing Strategy | 10 |
| Security Considerations | 10 |
| Risks & Mitigations | 5 |
| Success Criteria | 5 |

**Tier 2 Scoring** (20 additional points):

| Section | Points |
|---------|--------|
| Architecture Impact | 4 |
| API / Data Model Changes | 3 |
| Rollback Strategy | 3 |
| Observability | 2 |
| Performance Impact | 2 |
| Documentation Updates | 2 |
| Dependencies | 2 |
| Alternatives Considered | 2 |

**Score Rules**:
- Section present and substantively populated = full points
- Section present but placeholder/minimal = half points
- Section missing = 0 points
- "N/A" with valid justification = full points

**Domain Enhancement Scoring** (bonus/penalty on top of tier score):
- For each domain in `matchedDomains` from the loading engine:
  - Domain enhancer section present and substantive = **+2 bonus points**
  - Domain matched but enhancer section missing = **-2 penalty points**
  - Domain matched with "N/A — [valid reason]" = no bonus, no penalty
- Maximum domain bonus: +6 points (3 domains × 2 points)
- Domain scoring does not change the pass threshold — it provides additional quality signal

### Step 6: Verdict

| Condition | Verdict | Action |
|-----------|---------|--------|
| Score >= 70% of tier max | **PASS** | Present plan to user with score |
| Score < 70% of tier max | **REVISE** | Identify gaps, revise, re-validate |

**Revision Protocol**:
1. Identify the specific missing or weak sections
2. Provide targeted instructions to the planner for revision
3. Re-run validation after revision
4. Maximum 2 revision cycles — then present with warnings

---

## Output Format

After validation, append to the plan:

```markdown
## Plan Quality Assessment

**Task Size**: [Trivial/Medium/Large]
**Quality Score**: [X]/[max] ([percentage]%) [+N domain bonus / -N domain penalty]
**Verdict**: [PASS/REVISE]

### Validation Results

| Check | Status |
|-------|--------|
| Schema Compliance | [sections present]/[sections required] |
| Cross-Cutting Concerns | [All addressed / Missing: X, Y] |
| Specificity Audit | [All steps have file paths / X steps lack paths] |
| Domain Enhancement | [N domains matched, N enhancer sections present] |
| Rules Consulted | [list of rule files referenced] |
| Matched Domains | [list from loading engine] |
```

---

## Integration

- **Invoked by**: `/plan` workflow (step 3.5, between plan creation and user presentation)
- **Depends on**: `plan-schema.md` for scoring rubric, `domain-enhancers.md` for domain sections
- **Feeds into**: Plan quality score shown to user alongside the plan
- **Learning**: Quality scores are logged to `.agent/contexts/plan-quality-log.md` for adaptive improvement

---

## Principles

1. **Validate, don't block**: The goal is quality improvement, not gatekeeping. After 2 revision cycles, present the plan with warnings rather than blocking indefinitely.
2. **Score transparently**: The user sees the quality score and understands what was checked.
3. **Learn from outcomes**: Post-implementation retrospectives compare predicted vs. actual to calibrate future scoring.
4. **Cross-cutting is non-negotiable**: Security, testing, and documentation sections must ALWAYS be addressed. This is the single most impactful quality gate.
