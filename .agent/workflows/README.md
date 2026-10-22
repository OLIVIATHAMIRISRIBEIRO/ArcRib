# Antigravity AI Kit — Workflows

> **Purpose**: Process templates for common development tasks
> **Count**: 21 Workflows
> **Standard**: Enterprise Workflow Standard (EWS) v1.0

---

## Overview

Workflows are structured process templates that guide you through complex tasks. Each workflow follows the EWS v1.0 standard with 11 mandatory sections including trigger/lifecycle definition, critical rules, argument parsing, governance alerts, and completion criteria.

Invoke them using slash commands (e.g., `/brainstorm authentication system`).

---

## Available Workflows

| Workflow | Command | Lifecycle | Description |
| :---------------- | :--------------- | :------------ | :----------------------------------------------- |
| **brainstorm** | `/brainstorm` | Discover | Creative ideation and option exploration |
| **quality-gate** | `/quality-gate` | Discover | Pre-task market research, gap analysis, ethics |
| **plan** | `/plan` | Plan | Structured implementation planning |
| **create** | `/create` | Build | Scaffold new features, components, or modules |
| **enhance** | `/enhance` | Build | Iterative feature development on existing code |
| **preview** | `/preview` | Build | Local development server management |
| **ui-ux-pro-max** | `/ui-ux-pro-max` | Build | Premium UI/UX design and implementation |
| **test** | `/test` | Verify | Systematic test writing and execution |
| **review** | `/review` | Verify | Sequential quality gate pipeline |
| **preflight** | `/preflight` | Verify | Production readiness assessment with 10-domain scoring |
| **pr** | `/pr` | Ship | Production-grade PR creation with branch validation and size guards |
| **pr-review** | `/pr-review` | Verify | Multi-perspective PR review with senior engineering expertise |
| **pr-fix** | `/pr-fix` | Build | Fix PR issues based on review comments with verification |
| **pr-merge** | `/pr-merge` | Ship | Safe PR merge with dependency validation and post-merge checks |
| **pr-split** | `/pr-split` | Build | Split oversized PRs into focused sub-PRs by concern category |
| **deploy** | `/deploy` | Ship | Production deployment with pre-flight checks |
| **debug** | `/debug` | Reactive | Systematic problem investigation |
| **orchestrate** | `/orchestrate` | Reactive | Multi-agent coordination for complex tasks |
| **retrospective** | `/retrospective` | Evaluate | Tier-1 quality audit against market standards |
| **status** | `/status` | Cross-cutting | Project status overview and health check |
| **upgrade** | `/upgrade` | Maintenance | Formal protocol for non-destructive framework upgrades |

---

## SDLC Lifecycle Map

```
Discover ──► Plan ──► Build ──► Verify ──► Ship ──► Evaluate
   │           │        │         │         │          │
   ▼           ▼        ▼         ▼         ▼          ▼
/brainstorm  /plan   /create   /test       /pr        /retrospective
/quality-gate        /enhance  /review     /pr-merge
                     /preview  /preflight  /deploy
                     /pr-fix   /pr-review
                     /pr-split
                     /ui-ux-pro-max

    Reactive (any phase)          Cross-cutting (any phase)
    ────────────────────          ────────────────────────
    /debug                        /status
    /orchestrate                  /upgrade
```

---

## EWS v1.0 Standard

Every workflow conforms to the Enterprise Workflow Standard v1.0 with these sections:

| # | Section | Purpose |
| :- | :------------------- | :----------------------------------------------- |
| 1 | Frontmatter | `description` and `version` fields |
| 2 | Trigger / Lifecycle | When and where in SDLC this workflow runs |
| 3 | Governance Alert | Risk-appropriate alert (NOTE/IMPORTANT/CAUTION) |
| 4 | Critical Rules | Non-negotiable behavioral constraints |
| 5 | Argument Parsing | Sub-commands and argument table |
| 6 | Steps | Ordered steps with `// turbo` annotations |
| 7 | Output Template | Structured output format |
| 8 | Governance Footer | PROHIBITED / REQUIRED behavioral contracts |
| 9 | Completion Criteria | Checklist of done criteria |
| 10 | Related Resources | Links to skills, agents, and related workflows |
| 11 | Scope Filter | When applicable: commit-type filtering table |

---

## Turbo Annotation Policy

Steps annotated with `// turbo` can be auto-executed without user confirmation:

- **Allowed**: Read-only steps (analysis, detection, research, diagnostics)
- **Prohibited**: State-mutating steps (server start, deployment, code generation)

---

## Creating Custom Workflows

1. Create `workflows/my-workflow.md`
2. Add frontmatter with `description` and `version` fields
3. Follow the EWS v1.0 template (11 sections)
4. Map to an SDLC lifecycle phase
5. Link to relevant skills and agents in Related Resources
