# Quality Gate Rules

> **Priority**: HIGH — Enforced before implementation of new features and refactors
> **Scope**: All workspaces — applies to `feat()` and `refactor()` tasks only

---

## Scope Filter

| Task Type                         | Quality Gate Required? |
| :-------------------------------- | :--------------------- |
| `feat()` — new features           | ✅ Required            |
| `refactor()` — structural changes | ✅ Required            |
| `fix()` — bug fixes               | ❌ Skip                |
| `chore()` — maintenance           | ❌ Skip                |
| `docs()` — documentation          | ❌ Skip                |
| `test()` — test additions         | ❌ Skip                |

---

## Pre-Execution Research Checklist

Before implementing any in-scope task, **ALL** items must be completed. If any item is incomplete, execution is forbidden.

### ☐ 1. Market Research Completed

- Analyze **minimum 5** competitors or market leaders in the feature domain
- Document how each implements the same or similar feature
- Identify user adoption drivers: UX simplicity, accuracy, speed, transparency

### ☐ 2. Outdated Pattern Verification

- Verify the proposed approach does not use deprecated, abandoned, or criticized patterns
- If outdated → propose a modern, evidence-based alternative (mandatory)
- Document which patterns are considered harmful or legacy

### ☐ 3. Baseline Parity Validation

- Confirm the project **meets or exceeds** the current market baseline
- Gaps must be explicitly listed with severity assessment
- No gap left unaddressed without documented justification

### ☐ 4. Enhancement Definition

- Define exactly how the project **improves upon** the market baseline
- Improvement must be intentional and documented
- Consider: transparency, ethical automation, user-centricity, measurable outcomes

### ☐ 5. Ethics & Automation Risk Assessment

- Evaluate: privacy implications, AI bias risks, automation safety, user autonomy
- Mitigation strategies must be documented for each identified risk
- Data protection compliance must be considered for data-touching features

### ☐ 6. Implementation Plan Prepared

- Structured plan ready before execution begins
- Plan includes research summary, key insights, risks, execution steps
- Plan reviewed and approved before implementation may begin

---

## Enhancement Principle

| Scenario                                    | Required Action                  |
| :------------------------------------------ | :------------------------------- |
| Competitors offer a standard                | **Meet or exceed** it            |
| Competitors use unethical automation        | **Reject and improve**           |
| Feature can be more transparent             | **Enhance by default**           |
| Feature can be more user-centric            | **Enhance by default**           |
| Feature can offer measurable outcomes       | **Enhance by default**           |

**Never replicate patterns without improvement.**

---

## Cross-Cutting Deference

Quality gate enforcement defers to specialized rules for domain-specific checks:

- **Security**: See `rules/security.md` for input validation, auth, data protection
- **Testing**: See `rules/testing.md` for coverage requirements, test types
- **Code Quality**: See `rules/coding-style.md` for naming, file limits, immutability
- **Documentation**: See `rules/documentation.md` for doc hierarchy, SSOT

---

## Reject & Escalate Rules

| Condition                                   | Action                                 |
| :------------------------------------------ | :------------------------------------- |
| No market research provided                 | ❌ Reject — enforce research protocol  |
| Clearly outdated or harmful patterns        | ❌ Reject — propose modern alternative |
| Below-market standard solutions             | ❌ Reject — document gap               |
| Ethics, privacy, or automation safety risks | ❌ Reject — document mitigation        |
| Bypassing research ("just implement it")    | ❌ Reject — enforce protocol           |

### Escalation Response

> "This task cannot proceed in its current form, as it does not meet quality and market standards. Below are the identified risks and gaps. A revised, modern alternative is proposed."

---

## Related Resources

- **Workflow**: `.agent/workflows/quality-gate.md` — step-by-step research procedure
- **Skill**: `.agent/skills/brainstorming/SKILL.md` — Socratic questioning patterns
- **Next Step**: After approval, proceed to `/plan` for implementation planning

---

## Version History

| Version | Date       | Changes                                           |
| :------ | :--------- | :------------------------------------------------ |
| 1.0.0   | 2026-03-16 | Initial generic quality gate protocol for kit     |

