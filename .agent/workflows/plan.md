---
description: Create implementation plan. Invokes planner agent for structured task breakdown.
version: 2.2.0
sdlc-phase: plan
agents: [planner]
skills: [plan-writing, brainstorming, plan-validation]
commit-types: [docs]
---

# /plan — Implementation Planning

> **Trigger**: `/plan [task description]`
> **Lifecycle**: Plan — first step of SDLC after discovery

> [!IMPORTANT]
> This workflow creates plans, NOT code. No implementation during planning. All plans require user approval before execution begins.

> [!TIP]
> This workflow leverages the **plan-writing** skill. Read `.agent/skills/plan-writing/SKILL.md` for extended guidance.

---

## Critical Rules

1. **No code writing** — this workflow produces plans only
2. **Socratic gate** — ask at least 3 clarifying questions before creating a plan
3. **Dynamic naming** — name plan files based on the task (e.g., `PLAN-auth-fix.md`)
4. **Verification criteria** — every task in the plan must have clear "done" criteria
5. **User approval required** — never proceed to implementation without explicit approval
6. **Small, focused tasks** — break down work into atomic, verifiable steps

---

## Argument Parsing

| Command | Action |
| :----------------------- | :---------------------------------------------- |
| `/plan` | Prompt for task description |
| `/plan [description]` | Create implementation plan for the described task |

---

## Steps

// turbo
1. **Clarify Requirements** (Socratic Gate)
   - Ask at least 3 clarifying questions about purpose, scope, and constraints
   - Confirm acceptance criteria and edge cases
   - Identify relevant existing code and patterns

// turbo
2. **Explore Codebase**
   - Scan project structure and architecture
   - Identify files, modules, and patterns relevant to the task
   - Note dependencies and integration points

3. **Create Plan**
   - The loading engine provides `matchedDomains` and `mandatoryRules` — pass these to the planner agent
   - Consult all mandatory rules (security, testing, coding-style, documentation, git-workflow) using the Rule Extraction Algorithm
   - Classify task size: Trivial (1-2 files), Medium (3-10 files), Large (10+ files)
   - Break down the task into right-sized steps with exact file paths (see plan-writing SKILL.md Principle 1)
   - Assign verification criteria to each step
   - Order tasks logically (dependencies first)
   - Include cross-cutting concerns (security, testing, documentation) — ALWAYS, for ALL task sizes
   - For Medium/Large tasks: invoke specialist synthesis (security-reviewer, tdd-guide, architect) per the Specialist Invocation Protocol
   - Include domain-specific sections based on `matchedDomains` (see `domain-enhancers.md`)
   - Identify which agents are needed for multi-domain tasks
   - Save plan to `docs/PLAN-{task-slug}.md`

// turbo
3.5. **Validate Plan Quality**
   - The planner performs self-validation using the `plan-validation` skill checklist:
     1. Classify task size from file count and effort estimate
     2. Schema compliance: verify all required Tier sections are present and populated
     3. Cross-cutting verification: Security, Testing, Documentation sections are non-empty (or explicit "N/A — [reason]")
     4. Specificity audit: every implementation step includes a file path
     5. Score the plan against the rubric in `plan-schema.md`
     6. Apply domain scoring: +2 bonus per matched domain with enhancer, -2 penalty per missing
   - **Verdict**: Score >= 70% of tier max → PASS (present to user with score)
   - **Revision**: Score < 70% → identify gaps, revise, re-validate (max 2 cycles, then present with warnings)
   - The quality score is displayed alongside the plan for transparency

4. **Present for Approval**
   - Show the plan summary to the user with quality score
   - Wait for explicit approval before any implementation

---

## Naming Convention

| Request | Plan File |
| :----------------------- | :--------------------------- |
| `/plan e-commerce cart` | `PLAN-ecommerce-cart.md` |
| `/plan mobile app` | `PLAN-mobile-app.md` |
| `/plan auth fix` | `PLAN-auth-fix.md` |

---

## Output Template

```markdown
## 📋 Plan: [Task Name]

### Scope

[What this plan covers and what it doesn't]

### Tasks

1. [ ] [Task description] — **Verify**: [done criteria]
2. [ ] [Task description] — **Verify**: [done criteria]
3. [ ] [Task description] — **Verify**: [done criteria]

### Agent Assignments (if multi-domain)

| Task | Agent | Domain |
| :--- | :---- | :----- |
| [task] | [agent] | [domain] |

### Risks & Considerations

- [risk or constraint]

---

✅ Plan saved: `docs/PLAN-{slug}.md`

Approve to start implementation with `/create` or `/enhance`.
```

---

## Governance

**PROHIBITED:**
- Writing implementation code during planning
- Proceeding to implementation without user approval
- Creating vague, unverifiable tasks
- Skipping the Socratic gate
- Skipping failed steps · proceeding without resolution

**REQUIRED:**
- At least 3 clarifying questions before planning
- Mandatory rule consultation before plan creation
- Verification criteria for every task
- Cross-cutting concerns (security, testing, documentation) in every plan
- Plan validation against quality schema before presentation
- User approval before implementation begins
- Plan file saved in `docs/` with dynamic name

---

## Post-Implementation Retrospective

After the planned task is fully implemented and verified (reaches VERIFY phase), the `plan-complete` hook triggers a retrospective:

1. **Trigger**: Workflow state transitions to VERIFY (or user runs `/retrospective` on a completed plan)
2. **Data Source**: Compare `docs/PLAN-{slug}.md` against `git diff --name-only` from plan start
3. **Execution**: Run the plan-retrospective protocol (`.agent/skills/plan-writing/plan-retrospective.md`)
4. **Output**: Append one row to `.agent/contexts/plan-quality-log.md`
5. **Feedback Loop**: Planner reads the quality log at planning time (Step 1, Requirements Analysis) to adjust estimates, predict surprise files, and weight risk categories

This is non-blocking (severity: medium, onFailure: log). If skipped, no impact on current work, but future plan accuracy degrades.

---

## Completion Criteria

- [ ] Clarifying questions asked and answered
- [ ] Codebase explored for relevant context
- [ ] Mandatory rules consulted (security, testing, coding-style, documentation)
- [ ] Plan created with verifiable tasks and exact file paths
- [ ] Cross-cutting concerns addressed (security, testing, documentation)
- [ ] Plan validated against quality schema (score >= 70% of tier max)
- [ ] Domain-specific sections included for all matched domains
- [ ] Plan saved to `docs/PLAN-{slug}.md`
- [ ] User has reviewed and approved the plan
- [ ] After approval: proceed to `/create` or `/enhance` for implementation
- [ ] After implementation: retrospective logged to `plan-quality-log.md` (via plan-complete hook)

---

## Related Resources

- **Previous**: `/brainstorm` (explore options) · `/quality-gate` (validate approach)
- **Next**: `/create` (scaffold new features) · `/enhance` (iterative development)
- **Skill**: `.agent/skills/plan-writing/SKILL.md`
- **Schema**: `.agent/skills/plan-writing/plan-schema.md`
- **Domains**: `.agent/skills/plan-writing/domain-enhancers.md`
- **Validation**: `.agent/skills/plan-validation/SKILL.md`
- **Agent**: `planner` agent (see `.agent/agents/planner.md`)
