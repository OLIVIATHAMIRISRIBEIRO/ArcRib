---
description: Production readiness assessment with weighted scoring across 10 audit domains.
version: 1.0.0
sdlc-phase: verify
skills: [production-readiness, verification-loop, security-practices]
commit-types: [feat, fix, refactor, perf]
---

# /preflight — Production Readiness Assessment

> **Trigger**: `/preflight [domain|flag]`
> **Lifecycle**: Verify — after `/review`, before `/pr`

> [!CAUTION]
> Production readiness gate. All critical domains must pass before proceeding
> to `/pr` → `/deploy`. A failing preflight blocks the shipping pipeline.

> [!TIP]
> This workflow leverages the **production-readiness**, **verification-loop**, and
> **security-practices** skills. Read `.agent/skills/production-readiness/SKILL.md`
> for domain specifications and scoring criteria.

---

## Critical Rules

1. **Evidence-backed scoring** — every domain score must cite observable proof (file, command output, observation, or N/A justification)
2. **Never bypass blockers** — blocker rule violations override total score (see skill for precedence)
3. **Human approval required** — Go/No-Go recommendation requires explicit user decision
4. **Non-destructive** — checks do not modify source code; verification commands (test suites, linters, builds) may run but must not alter project state
5. **Skill-mediated delegation** — domain checks reference existing skills, never duplicate their logic
6. **Fail-safe defaults** — unverifiable checks score 0, not assumed pass

---

## Argument Parsing

| Command | Action |
| :--- | :--- |
| `/preflight` | Full scan — all 10 domains (D1-D10), standard scorecard |
| `/preflight [domain]` | Single domain focus (e.g., `/preflight security`, `/preflight tasks`) |
| `/preflight --quick` | Quick scan — D4 (Code) + D5 (Security) + D6 (Config) + D9 (CI/CD) |
| `/preflight --full` | Deep scan — all D1-D10 + market benchmark comparison |
| `/preflight --rescan` | Re-scan — all D1-D10 with delta comparison against previous scorecard |

### Domain Name Aliases

| Domain | Aliases |
| :--- | :--- |
| D1: Task Completeness | `tasks`, `roadmap`, `scope` |
| D2: User Journey Validation | `journeys`, `ux`, `flows` |
| D3: Implementation Correctness | `implementation`, `correctness`, `tests` |
| D4: Code Quality | `code`, `quality`, `lint` |
| D5: Security & Privacy | `security`, `sec`, `privacy` |
| D6: Configuration Readiness | `config`, `configuration`, `env` |
| D7: Performance Baseline | `performance`, `perf`, `speed` |
| D8: Documentation | `docs`, `documentation` |
| D9: Infrastructure & CI/CD | `infra`, `ci`, `cicd`, `pipeline` |
| D10: Observability & Monitoring | `observability`, `monitoring`, `logs` |

---

## Steps

// turbo
1. **Project Detection & Inventory**
   - Detect project type (web, mobile, API, library, monorepo)
   - Identify tech stack (language, framework, build tool)
   - Locate key files: ROADMAP.md, package.json/pubspec.yaml, CI config, .env files
   - Identify the target deployment platform
   - Determine which domains are applicable (not all domains apply to every project type)
   - Load the `production-readiness` skill for domain definitions

// turbo
2. **Domain Scanning**
   - For each applicable domain (D1-D10):
     - Load the primary skill referenced in the domain definition
     - Execute each sub-check per the rubric in the `production-readiness` skill
     - Record evidence for each sub-check (file path, command output, observation)
     - Calculate domain score based on sub-check results
     - Classify findings by severity:
       - 🔴 **Critical**: Blocks production, must fix
       - 🟠 **High**: Significant risk, should fix before ship
       - 🟡 **Medium**: Improvement recommended, can ship with plan
       - 🟢 **Low**: Minor suggestion, no blocking impact
   - For `--quick` mode: execute only D4, D5, D6, D9
   - For single domain: execute only the specified domain

// turbo
3. **Scoring & Classification**
   - Calculate per-domain scores from sub-check results
   - Apply Blocker Rule Precedence (see `production-readiness` skill):
     1. Check: Any domain = 0? → 🔴 Not Ready
     2. Check: D5 < 50%? → 🔴 Not Ready
     3. Check: D4 < 50%? → 🟡 minimum
   - Calculate total score (sum of all domain scores)
   - Determine Go/No-Go status from thresholds:
     - ≥ 85: 🟢 Production Ready
     - 70-84: 🟡 Conditionally Ready
     - < 70: 🔴 Not Ready
   - For `--rescan`: generate delta comparison table
   - For `--full`: add market benchmark comparison section

4. **Go/No-Go Recommendation**
   - Present the Production Readiness Scorecard to the user
   - Highlight critical/high findings with remediation guidance
   - Recommend next actions based on verdict
   - **Wait for explicit user decision** — never auto-proceed

---

## Output Template

```markdown
# 🚀 Production Readiness Scorecard

> Project: [project name] · Date: [date] · Mode: [default|quick|full|rescan]

## Overall Verdict

| Score | Status | Decision |
| :--- | :--- | :--- |
| [XX/100] | [🟢/🟡/🔴] [Status] | [Recommendation] |

## Domain Scores

| Domain | Score | Status | Key Finding |
| :--- | :--- | :--- | :--- |
| D1: Task Completeness | X/8 | [emoji] | [summary] |
| D2: User Journeys | X/10 | [emoji] | [summary] |
| D3: Implementation | X/10 | [emoji] | [summary] |
| D4: Code Quality | X/15 | [emoji] | [summary] |
| D5: Security & Privacy | X/18 | [emoji] | [summary] |
| D6: Configuration | X/8 | [emoji] | [summary] |
| D7: Performance | X/8 | [emoji] | [summary] |
| D8: Documentation | X/5 | [emoji] | [summary] |
| D9: Infrastructure | X/10 | [emoji] | [summary] |
| D10: Observability | X/8 | [emoji] | [summary] |

## Blocker Check

| Rule | Condition | Result |
| :--- | :--- | :--- |
| Zero Domain | Any domain = 0 | [PASS/FAIL] |
| Security Floor | D5 ≥ 50% | [PASS/FAIL] |
| Quality Floor | D4 ≥ 50% | [PASS/FAIL] |

## Findings

### 🔴 Critical
- [finding with evidence and remediation]

### 🟠 High
- [finding with evidence and remediation]

### 🟡 Medium
- [finding with evidence and remediation]

## Recommended Next Actions

1. [action based on verdict]
2. [action based on top findings]

---

Verdict: [🟢/🟡/🔴] [score]/100 — [status text]
Run `/preflight --rescan` after fixes to verify improvement.
```

---

## Governance

**PROHIBITED:**
- Auto-deploying based on a passing score — human decision always required
- Skipping blocker rule evaluation
- Fabricating evidence for sub-check scores
- Modifying project files during analysis
- Proceeding to `/pr` without presenting the scorecard

**REQUIRED:**
- Evidence citation for every scored sub-check
- Blocker rule evaluation before total score
- Human approval for Go/No-Go decision
- Skill reference for each domain scan
- Finding classification by severity (🔴/🟠/🟡/🟢)

---

## Completion Criteria

- [ ] Project type and tech stack detected
- [ ] Applicable domains identified
- [ ] All applicable domain sub-checks executed with evidence
- [ ] Blocker rules evaluated
- [ ] Per-domain scores calculated
- [ ] Total score and Go/No-Go status determined
- [ ] Findings classified by severity
- [ ] Scorecard presented to user
- [ ] User has made explicit Go/No-Go decision
- [ ] After approval: proceed to `/pr` for PR creation

---

## Scope Filter

| Commit Type | Preflight Required? | Rationale |
| :--- | :--- | :--- |
| `feat()` | ✅ Required | New features need readiness validation |
| `fix()` | ⚠️ Optional | Critical fixes may need quick deploy path |
| `refactor()` | ✅ Required | Structural changes need validation |
| `perf()` | ✅ Required | Performance changes need baseline verification |
| `docs()` | ❌ Skip | No production impact |
| `chore()` | ❌ Skip | No production impact |
| `test()` | ❌ Skip | No production impact |
| Pre-launch | ✅ Required | Major releases always require preflight |

---

## Related Resources

- **Previous**: `/review` (code quality gates must pass before preflight)
- **Next**: `/pr` (create pull request after readiness verified)
- **Skills**: `.agent/skills/production-readiness/SKILL.md` · `.agent/skills/verification-loop/SKILL.md` · `.agent/skills/security-practices/SKILL.md`
- **Related**: `/deploy` (deployment after PR merged) · `/retrospective` (sprint-level audit)
