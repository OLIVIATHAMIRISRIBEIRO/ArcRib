# Plan Retrospective

> Post-implementation review protocol for measuring plan accuracy
> and feeding learnings back into future plan generation.

---

## Overview

After a planned task reaches the VERIFY phase (all implementation complete, tests running), this retrospective compares the original plan against actual implementation to identify accuracy gaps and improve future planning.

---

## When to Run

- **Primary Trigger**: The `plan-complete` hook in `.agent/hooks/hooks.json` fires when workflow state transitions to VERIFY phase
- **Manual Trigger**: User runs `/retrospective` on a completed plan
- **Data Flow**: The hook reads the original plan file (`docs/PLAN-{slug}.md`), compares against `git diff --name-only` from the plan's creation timestamp, then appends results to `.agent/contexts/plan-quality-log.md`
- **Frequency**: After every planned task completes implementation
- **Blocking**: No — this is a learning activity, not a quality gate (severity: medium, onFailure: log)
- **Planner Integration**: The planner reads `plan-quality-log.md` during Requirements Analysis (Step 1) to adjust estimates and predictions for future plans

---

## Retrospective Dimensions

### 1. File Prediction Accuracy

Compare files listed in the plan vs. files actually modified:

| Metric | Measurement |
|--------|-------------|
| **Files Predicted** | Count of unique file paths in the plan |
| **Files Actually Modified** | Count from `git diff --name-only` against plan start |
| **Prediction Accuracy** | Predicted / Actual (percentage) |
| **Surprise Files** | Files modified that were NOT in the plan |
| **Unused Predictions** | Files in the plan that were NOT modified |

### 2. Task Completeness

| Metric | Measurement |
|--------|-------------|
| **Tasks Planned** | Count of implementation steps in original plan |
| **Tasks Completed** | Steps that matched actual work |
| **Surprise Tasks** | Work done that wasn't in the plan |
| **Dropped Tasks** | Planned tasks that turned out unnecessary |
| **Completeness Score** | (Completed - Surprise) / Planned |

### 3. Estimate Accuracy

| Metric | Measurement |
|--------|-------------|
| **Estimated Effort** | Total hours from plan |
| **Actual Effort** | Approximate actual time spent |
| **Drift** | Actual / Estimated (ratio; 1.0 = perfect) |
| **Drift Direction** | Over-estimated / Under-estimated / Accurate |

### 4. Risk Prediction

| Metric | Measurement |
|--------|-------------|
| **Risks Identified** | Count of risks in plan |
| **Risks Materialized** | Planned risks that actually occurred |
| **Surprise Risks** | Unplanned risks that emerged |
| **Risk Prediction Rate** | Materialized / (Materialized + Surprise) |

### 5. Specialist Contribution Value

| Specialist | Contribution Accurate? | Key Insight That Helped |
|-----------|----------------------|------------------------|
| Architect | Yes/No/Partial | [what was most useful] |
| Security-Reviewer | Yes/No/Partial | [what was most useful] |
| TDD-Guide | Yes/No/Partial | [what was most useful] |

---

## Output Format

Append one row to `.agent/contexts/plan-quality-log.md`:

```markdown
| [date] | [plan name] | [quality score] | [files predicted] | [files actual] | [surprise count] | [estimate drift] | [key learning] |
```

### Key Learning Format

Capture the single most important learning in one sentence:

**Good examples**:
- "Auth tasks consistently require middleware changes not predicted in plans"
- "Database migration effort was 2x underestimated due to index rebuilding"
- "Frontend plans should always include accessibility testing as a task"

**Bad examples**:
- "The plan was good" (not actionable)
- "Everything went as expected" (no learning value)

---

## Adaptive Feedback

The planner agent reads `plan-quality-log.md` at the start of each planning session to:

1. **Adjust estimates**: If historical drift is consistently 1.5x, multiply estimates by 1.5
2. **Predict surprise files**: If auth tasks consistently miss middleware, proactively include middleware files
3. **Weight risks**: If certain risk categories historically materialize, elevate their severity
4. **Improve domain sections**: If specific domain enhancer sections are consistently unhelpful, deprioritize them
5. **Value specialists**: If security-reviewer contributions are consistently accurate, weight their input more heavily

---

## Example Retrospective Entry

```
| 2026-03-16 | PLAN-user-auth | 72/80 | 8 | 11 | 3 (middleware, session config, error handler) | 1.4x | Auth plans should include middleware and session store files by default |
```
