# Antigravity AI Kit — CheatSheet

> **Version**: v3.10.1 | **Quick Reference** for all capabilities
> **Session**: Start with `/status`, end with session-end checklist

---

## 🚀 Session Lifecycle

### Start a Session

1. Run `/status` to load context
2. Review sprint state from `docs/ROADMAP.md`
3. Verify Git state and dependencies
4. Confirm direction with user

### End a Session

1. Update `docs/ROADMAP.md` with completed/in-progress items
2. Sync `docs/CHANGELOG.md` with shipped work
3. Update `.agent/session-context.md` with handoff notes
4. Update `.agent/session-state.json`
5. Commit all tracking files
6. Push (triggers LOCAL-CI-GATE)

---

## 📋 Commands (37)

### Core Workflow

| Command | Description |
|:--------|:------------|
| `/plan` | Create implementation plan |
| `/implement` | Execute the approved plan |
| `/verify` | Run all quality gates |
| `/status` | Check project status |

### Development

| Command | Description |
|:--------|:------------|
| `/build` | Build a new feature from scratch |
| `/fix` | Fix linting, type, or build errors |
| `/debug` | Systematic debugging process |
| `/refactor` | Improve code quality |
| `/cook` | Full scratch-to-done workflow |

### Documentation & Git

| Command | Description |
|:--------|:------------|
| `/doc` | Generate documentation |
| `/adr` | Create Architecture Decision Record |
| `/changelog` | Generate changelog from commits |
| `/git` | Git operations with best practices |
| `/pr` | Create production-grade pull requests |

### PR Toolkit

| Command | Description |
|:--------|:------------|
| `/pr-review` | Review a PR with senior engineering expertise |
| `/pr-fix` | Fix PR issues based on review comments |
| `/pr-merge` | Merge PR safely with dependency validation |
| `/pr-split` | Split oversized PRs into focused sub-PRs |
| `/pr-status` | Triage PRs with CI, staleness, and merge readiness |
| `/pr-describe` | Auto-generate PR title, summary, and labels |

### Exploration & Research

| Command | Description |
|:--------|:------------|
| `/scout` | Explore and understand codebase |
| `/research` | Research technologies or solutions |
| `/ask` | Ask questions about code |

### Quality & Security

| Command | Description |
|:--------|:------------|
| `/code-review` | Run code review |
| `/tdd` | Test-driven development workflow |
| `/security-scan` | Security audit and vulnerability scan |
| `/perf` | Performance analysis and optimization |

### Integration & Deployment

| Command | Description |
|:--------|:------------|
| `/integrate` | Third-party service integration |
| `/db` | Database schema and migrations |
| `/deploy` | Deploy to target environment |
| `/design` | UI/UX design specifications |

### Context Management

| Command | Description |
|:--------|:------------|
| `/learn` | Extract patterns from session |
| `/checkpoint` | Save progress checkpoint |
| `/compact` | Compress context for memory |
| `/eval` | Evaluate metrics |
| `/setup` | Configure project with kit |
| `/help` | Show available commands |

---

## 🤖 Agents (20)

### Core Development

| Agent | Purpose |
|:------|:--------|
| 📋 Planner | Feature planning, risk assessment |
| 🏛️ Architect | System design, ADR creation |
| 🔍 Code Reviewer | Quality + security review |
| 🧪 TDD Guide | Test-first enforcement |
| 🔧 Build Error Resolver | Rapid build fixes |
| 🎨 Frontend Specialist | React, Next.js, UI architecture |
| ⚙️ Backend Specialist | Node.js, Python, API design |

### Quality & Security

| Agent | Purpose |
|:------|:--------|
| 🔐 Security Reviewer | Vulnerability analysis |
| 🎭 E2E Runner | End-to-end testing |
| ⚡ Performance Optimizer | Core Web Vitals optimization |

### Infrastructure

| Agent | Purpose |
|:------|:--------|
| 📱 Mobile Developer | React Native/Expo development |
| 🗄️ Database Architect | Schema design, queries |
| 🚀 DevOps Engineer | CI/CD, deployment |
| 🛡️ Reliability Engineer | SRE, production readiness |

### Maintenance & Discovery

| Agent | Purpose |
|:------|:--------|
| 🧹 Refactor Cleaner | Dead code cleanup |
| 📚 Doc Updater | Documentation sync |
| 🧠 Knowledge Agent | RAG retrieval |
| 🔭 Explorer Agent | Codebase discovery |
| 📊 Sprint Orchestrator | Sprint planning & velocity |

### PR & Code Review

| Agent | Purpose |
|:------|:--------|
| 👀 PR Reviewer | PR review, branch strategy, code quality |

---

## 🧩 Skills (34)

### Operational (7)

| Skill | Purpose |
|:------|:--------|
| verification-loop | Continuous quality gates |
| continuous-learning | Pattern extraction (PAAL) |
| strategic-compact | Context window management |
| eval-harness | Performance evaluation |
| context-budget | LLM token budget management |
| plan-validation | Plan quality gate with scoring |
| production-readiness | Preflight audit and readiness checks |

### Orchestration (4)

| Skill | Purpose |
|:------|:--------|
| intelligent-routing | Automatic agent selection |
| parallel-agents | Multi-agent orchestration |
| behavioral-modes | Adaptive AI operation modes |
| mcp-integration | MCP server integration |

### Domain — Architecture & Design (6)

| Skill | Purpose |
|:------|:--------|
| architecture | System design patterns |
| api-patterns | RESTful API design |
| database-design | Schema optimization |
| frontend-patterns | React/component patterns |
| nodejs-patterns | Backend patterns |
| i18n-localization | Internationalization |

### Domain — Code Quality (4)

| Skill | Purpose |
|:------|:--------|
| clean-code | Code quality principles |
| typescript-expert | Advanced TypeScript |
| testing-patterns | TDD, unit, integration |
| debugging-strategies | Systematic debugging |

### Domain — Operations (4)

| Skill | Purpose |
|:------|:--------|
| docker-patterns | Containerization |
| git-workflow | Branching, commits |
| security-practices | OWASP, vulnerability prevention |
| pr-toolkit | PR lifecycle, review, merge, split |

### Development (9)

| Skill | Purpose |
|:------|:--------|
| app-builder | Full-stack scaffolding |
| mobile-design | Mobile UI/UX patterns |
| webapp-testing | E2E and Playwright testing |
| deployment-procedures | CI/CD and rollback strategies |
| performance-profiling | Core Web Vitals optimization |
| brainstorming | Socratic discovery protocol |
| plan-writing | Structured task breakdown |
| shell-conventions | PowerShell/Bash conventions |
| ui-ux-pro-max | Premium UI/UX design system |

---

## 🔄 Workflows (21)

| Workflow | Command | Phase |
|:---------|:--------|:------|
| brainstorm | `/brainstorm` | Discover |
| quality-gate | `/quality-gate` | Discover |
| plan | `/plan` | Plan |
| create | `/create` | Build |
| enhance | `/enhance` | Build |
| preview | `/preview` | Build |
| ui-ux-pro-max | `/ui-ux-pro-max` | Build |
| pr-fix | `/pr-fix` | Build |
| pr-split | `/pr-split` | Build |
| test | `/test` | Verify |
| review | `/review` | Verify |
| preflight | `/preflight` | Verify |
| pr-review | `/pr-review` | Verify |
| pr | `/pr` | Ship |
| pr-merge | `/pr-merge` | Ship |
| deploy | `/deploy` | Ship |
| debug | `/debug` | Reactive |
| orchestrate | `/orchestrate` | Reactive |
| retrospective | `/retrospective` | Evaluate |
| status | `/status` | Cross-cutting |
| upgrade | `/upgrade` | Maintenance |

---

## ✅ Checklists (4)

| Checklist | When to Use |
|:----------|:------------|
| `session-start.md` | Beginning of every work session |
| `session-end.md` | Before ending any work session |
| `pre-commit.md` | Before every commit |
| `task-complete.md` | After completing any task |

---

## ⚖️ Governance Rules (9)

| Rule File | Scope |
|:----------|:------|
| `coding-style.md` | TypeScript + Python conventions |
| `security.md` | Secrets, auth, data protection, AI safety |
| `testing.md` | TDD, pytest, Jest/Vitest patterns |
| `git-workflow.md` | Commits, branches, push policy |
| `documentation.md` | Doc hierarchy, SSOT, preservation |
| `sprint-tracking.md` | ROADMAP.md as SSOT, session protocols |
| `quality-gate.md` | Pre-task validation and quality standards |
| `architecture.md` | System design patterns and ADR governance |
| `agent-upgrade-policy.md` | Framework upgrade preservation rules |

---

## 🎯 Common Scenarios

### 1. Starting a New Feature

```
/status → /plan → /create → /test → /review → /pr → /deploy
```

### 2. Fixing a Bug

```
/status → /debug → /fix → /test → /review
```

### 3. UI/UX Design Work

```
/brainstorm → /quality-gate → /ui-ux-pro-max → /preview → /review
```

### 4. Code Quality Improvement

```
/status → /review → /refactor → /test → /verify
```

### 5. Sprint Planning

```
/status → /plan → /brainstorm → update ROADMAP.md
```

### 6. PR Lifecycle

```
/pr → /pr-review → /pr-fix → /pr-merge
```

---

## 📁 Directory Structure

```
.agent/
├── rules.md                 # Core governance & identity
├── session-state.json       # Machine-readable state
├── session-context.md       # Human-readable session context
├── CheatSheet.md            # This file
├── manifest.json            # Capability registry
│
├── agents/                  # 20 specialized agents
├── commands/                # 37 slash commands
├── skills/                  # 34 capability extensions
├── workflows/               # 21 slash command workflows
├── hooks/                   # Event-driven automation
├── rules/                   # 9 modular governance rules
├── contexts/                # Mode switching (brainstorm, debug, etc.)
├── checklists/              # Session & pre-commit verification
├── templates/               # Feature, ADR, bug-report templates
├── decisions/               # Architecture Decision Records
└── engine/                  # Runtime engine configs
```
