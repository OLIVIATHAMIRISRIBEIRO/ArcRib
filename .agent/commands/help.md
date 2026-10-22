---
description: Comprehensive reference for all Antigravity AI Kit capabilities
---

# /help Command

Your complete guide to the Antigravity AI Kit. Type `/help` for a quick overview, or drill down into specific categories.

## Usage

```
/help                  # Quick overview of all capabilities
/help commands         # All 37 slash commands with descriptions
/help workflows        # All 21 workflows with descriptions
/help agents           # All 20 AI agents with domains
/help skills           # All 34 skill modules
/help rules            # Governance rules
/help checklists       # Quality gate checklists
/help cli              # Terminal CLI commands (ag-kit)
/help <command-name>   # Detail on a specific command (e.g., /help plan)
```

---

## Quick Overview

**Antigravity AI Kit v3.10.1** — Trust-Grade AI Development Framework

| Category | Count | Description |
|:---------|:------|:------------|
| ⌨️ Commands | 37 | Slash commands for every development task |
| 🔄 Workflows | 21 | Multi-step development lifecycles |
| 🤖 Agents | 20 | Specialized AI roles for delegation |
| 🛠️ Skills | 34 | Domain knowledge modules |
| ⚖️ Rules | 9 | Modular governance constraints |
| ✅ Checklists | 4 | Quality gate checklists |
| ⚙️ Runtime | 29 | Engine modules (governance, reputation, self-healing) |

### Getting Started

```
/status           → Check your session and project health
/plan             → Create an implementation plan
/create           → Build a new feature from scratch
/review           → Run quality gates before committing
```

### Recommended Workflow

```
/brainstorm  →  /plan  →  /create  →  /test  →  /review  →  /deploy
```

---

## Commands (37)

### Core Workflow

| Command | Description |
|:--------|:------------|
| `/plan` | Create structured implementation plan with task breakdown |
| `/implement` | Execute an approved plan step by step |
| `/verify` | Run all quality gates (lint, types, tests, security, build) |
| `/status` | Check project health, session state, and capabilities |

### Feature Development

| Command | Description |
|:--------|:------------|
| `/build` | Build a new feature from scratch |
| `/fix` | Fix linting, type, or build errors |
| `/debug` | Systematic debugging with hypothesis tracking |
| `/refactor` | Improve code quality without changing behavior |
| `/cook` | Full scratch-to-done workflow (plan → build → test → review) |
| `/design` | UI/UX design specifications and mockups |

### Testing & Quality

| Command | Description |
|:--------|:------------|
| `/tdd` | Test-driven development — write tests first, then implement |
| `/code-review` | Comprehensive code review with security analysis |
| `/security-scan` | Security audit and vulnerability scan |
| `/perf` | Performance analysis and optimization |
| `/eval` | Evaluate metrics and measure quality |

### Documentation & Git

| Command | Description |
|:--------|:------------|
| `/doc` | Generate or update documentation |
| `/adr` | Create Architecture Decision Record |
| `/changelog` | Generate changelog from commits |
| `/git` | Git operations with best practices |
| `/pr` | Create production-grade pull requests |
| `/pr-review` | Review a pull request with senior engineering expertise |
| `/pr-fix` | Fix PR issues based on review comments |
| `/pr-merge` | Merge PR safely with dependency validation |
| `/pr-split` | Split oversized PRs into focused sub-PRs |
| `/pr-status` | Triage PRs with CI, staleness, and merge readiness |
| `/pr-describe` | Auto-generate PR title, summary, and labels |
| `/checkpoint` | Save progress checkpoint for session continuity |

### Exploration & Research

| Command | Description |
|:--------|:------------|
| `/scout` | Explore and understand an unfamiliar codebase |
| `/research` | Research technologies, libraries, or solutions |
| `/ask` | Ask questions about code, architecture, or patterns |

### Infrastructure & Integration

| Command | Description |
|:--------|:------------|
| `/integrate` | Third-party service integration |
| `/db` | Database schema design and migrations |
| `/deploy` | Deploy to target environment with pre-flight checks |
| `/setup` | Configure a new project with Antigravity AI Kit |

### Context Management

| Command | Description |
|:--------|:------------|
| `/learn` | Extract reusable patterns from current session (PAAL cycle) |
| `/compact` | Compress context window for long sessions |
| `/help` | This reference — show available capabilities |

---

## Workflows (21)

Workflows are multi-step development lifecycles. Use them with the `/` prefix.

| Workflow | Description | Key Steps |
|:---------|:------------|:----------|
| `/brainstorm` | Structured ideation and discovery | Socratic questioning → options → decision |
| `/create` | Build new features from scratch | Scaffold → implement → test → review |
| `/debug` | Systematic debugging | Reproduce → hypothesize → verify → fix |
| `/deploy` | Production deployment | Pre-flight → execute → verify → monitor |
| `/enhance` | Iterative feature improvement | Analyze → plan → implement → validate |
| `/orchestrate` | Multi-agent task coordination | Decompose → delegate → merge → verify |
| `/plan` | Implementation planning | Research → design → breakdown → verify |
| `/pr` | Production-grade PR creation | Branch validation → size guard → review → push → CI |
| `/pr-review` | Multi-perspective PR review | Fetch → analyze → 6-perspective review → post verdict |
| `/pr-fix` | Fix PR based on review comments | Fetch reviews → prioritize → fix → verify → push |
| `/pr-merge` | Safe PR merge | Validate → verify prerequisites → merge → post-merge checks |
| `/pr-split` | Split oversized PRs | Analyze → categorize → split plan → create sub-PRs |
| `/preflight` | Production readiness audit | 10-domain assessment → scoring → verdict |
| `/preview` | Local dev server management | Start → verify → iterate → stop |
| `/quality-gate` | Pre-task validation protocol | Market research → gap analysis → ethics review |
| `/retrospective` | Sprint audit and review | Metrics → findings → action items |
| `/review` | Quality gate pipeline | Lint → types → tests → security → build |
| `/status` | Project state overview | Session → git → health → capabilities |
| `/test` | Systematic test writing | Strategy → write → run → coverage |
| `/ui-ux-pro-max` | Premium UI/UX design | Style → palette → typography → implement |
| `/upgrade` | Non-destructive framework updates | Backup → update → verify → preserve |

---

## Agents (20)

Agents are specialized AI roles. They are automatically activated based on task context, or you can request a specific agent.

| Agent | Domain |
|:------|:-------|
| `architect` | System design, DDD, Hexagonal Architecture |
| `backend-specialist` | Node.js, NestJS, API design |
| `build-error-resolver` | Rapid build/compile error fixes |
| `code-reviewer` | Quality + security code review |
| `database-architect` | Schema design, queries, optimization |
| `devops-engineer` | CI/CD, Docker, deployment pipelines |
| `doc-updater` | Documentation synchronization |
| `e2e-runner` | End-to-end test execution |
| `explorer-agent` | Codebase discovery and mapping |
| `frontend-specialist` | React, Next.js, UI architecture |
| `knowledge-agent` | RAG retrieval and context lookup |
| `mobile-developer` | React Native, Expo mobile development |
| `performance-optimizer` | Core Web Vitals, profiling, optimization |
| `planner` | Task breakdown, Socratic analysis |
| `pr-reviewer` | PR review, branch strategy, code quality |
| `refactor-cleaner` | Dead code cleanup, code improvement |
| `reliability-engineer` | SRE, production readiness, SLA monitoring |
| `security-reviewer` | Vulnerability analysis, OWASP compliance |
| `sprint-orchestrator` | Sprint planning, velocity tracking |
| `tdd-guide` | Test-first development enforcement |

---

## Skills (34)

Skills are domain knowledge modules that agents use. They are loaded automatically based on task context.

| Category | Skills |
|:---------|:-------|
| **Architecture** | `architecture`, `api-patterns`, `clean-code`, `database-design`, `docker-patterns` |
| **Frontend** | `frontend-patterns`, `ui-ux-pro-max`, `mobile-design`, `i18n-localization` |
| **Backend** | `nodejs-patterns`, `typescript-expert`, `security-practices` |
| **Testing** | `testing-patterns`, `webapp-testing`, `eval-harness` |
| **DevOps** | `deployment-procedures`, `git-workflow`, `pr-toolkit`, `shell-conventions` |
| **AI & Orchestration** | `intelligent-routing`, `parallel-agents`, `mcp-integration`, `context-budget`, `behavioral-modes` |
| **Planning** | `brainstorming`, `plan-writing`, `plan-validation`, `strategic-compact`, `continuous-learning` |
| **Performance** | `performance-profiling` |
| **Production** | `production-readiness` |
| **Scaffolding** | `app-builder` |
| **Debugging** | `debugging-strategies` |
| **Verification** | `verification-loop` |

---

## Rules (9)

Rules are modular governance constraints that all agents must follow.

| Rule | Purpose |
|:-----|:--------|
| `coding-style` | Naming conventions, file limits, type safety |
| `git-workflow` | Conventional commits, atomic changes, branch strategy |
| `security` | Secret management, input validation, OWASP |
| `testing` | Test-first, coverage targets, test naming |
| `documentation` | Doc hierarchy, SSOT, preservation |
| `sprint-tracking` | ROADMAP.md as SSOT, session protocols |
| `quality-gate` | Pre-task validation and quality standards |
| `architecture` | System design patterns and ADR governance |
| `agent-upgrade-policy` | Framework upgrade preservation rules |

---

## Checklists (4)

Checklists are quality gates run at specific lifecycle moments.

| Checklist | When | Key Checks |
|:----------|:-----|:-----------|
| `session-start` | Beginning of each session | Read context, verify git, check dependencies |
| `session-end` | End of each session | Update ROADMAP, CHANGELOG, commit tracking files |
| `pre-commit` | Before git commit | Tests pass, lint clean, no secrets, build succeeds |
| `task-complete` | After task completion | Verification, documentation, cleanup |

---

## CLI Commands (ag-kit)

Terminal commands available after installing the kit:

| Command | Description |
|:--------|:------------|
| `ag-kit init` | Install .agent/ into your project |
| `ag-kit status` | Show project health dashboard |
| `ag-kit verify` | Run manifest integrity checks (90 checks) |
| `ag-kit scan` | Enhanced security scanning |
| `ag-kit update` | Update to latest version (diff-based, preserves customizations) |
| `ag-kit heal` | Detect and diagnose CI failures |
| `ag-kit plugin list` | List installed plugins |
| `ag-kit plugin install <path>` | Install a plugin |
| `ag-kit plugin remove <name>` | Remove a plugin |
| `ag-kit market search <query>` | Search marketplace plugins |
| `ag-kit market info <name>` | Get marketplace plugin details |
| `ag-kit market install <name>` | Install from marketplace |

---

## Quick Reference Card

```
Start here:        /status → /plan → /create → /review
Debug issues:      /debug → /fix → /verify
Write tests:       /tdd → /test → /verify
Deploy:            /review → /deploy
Learn more:        /help <topic>
Terminal:          ag-kit verify | ag-kit scan | ag-kit status
```
