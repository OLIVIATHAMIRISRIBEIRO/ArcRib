---
name: production-readiness
description: Production readiness audit domains, weighted scoring criteria, and check specifications for the /preflight workflow.
version: 1.0.0
triggers: [pre-deploy, pre-launch, milestone, production-readiness]
allowed-tools: Read, Grep, Bash
---

# Production Readiness

> **Purpose**: Assess project readiness for production deployment across 10 audit domains
> **Invoked by**: `/preflight` workflow
> **Reusable by**: `/retrospective`, `/deploy`

---

## Overview

This skill defines the audit domains, sub-check rubrics, and scoring model used by the `/preflight` workflow to generate a Production Readiness Scorecard. Each domain has weighted scoring with evidence-based pass criteria.

---

## Principles

1. **Evidence over assertion** — every score must be backed by observable proof
2. **Non-destructive** — checks do not modify source code; test suites, linters, and builds may run as verification commands but must not alter project state
3. **Fail-safe defaults** — unverifiable checks score 0 (not assumed pass)
4. **Domain independence** — each domain is scored independently
5. **Blocker precedence** — blocker rules override total score

---

## Domain Definitions

### D1: Task Completeness (8 points)

> Verify all planned work is complete, scope is aligned, and no undocumented features exist.

**Primary Skill**: `plan-writing` · **Check Method**: Read ROADMAP.md, task files

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| ROADMAP.md or task tracker exists and is current | 2 | File exists, contains structured task list |
| All MVP/milestone tasks marked complete | 3 | No `[ ]` items remain in milestone scope |
| No undocumented features | 2 | Every implemented feature has a task entry |
| Scope drift detection | 1 | No features implemented outside planned scope |

---

### D2: User Journey Validation (10 points)

> Verify critical user flows work end-to-end and fail-safe behavior is defined.

**Primary Skill**: `webapp-testing` · **Secondary Skill**: `testing-patterns` · **Check Method**: Walk critical flows, check error handling

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| Critical user flows identified | 2 | At least 3 key flows documented or testable |
| Happy path verified | 3 | Core flows produce expected outcomes |
| Error/edge case handling | 3 | Graceful degradation on failure paths |
| Accessibility baseline | 2 | Basic keyboard navigation, ARIA labels on critical elements |

---

### D3: Implementation Correctness (10 points)

> Verify features function as specified, no dead code, and test suite passes.

**Primary Skill**: `verification-loop` · **Secondary Skill**: `testing-patterns` · **Check Method**: Run test suite, static analysis

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| Test suite passes | 4 | Zero test failures |
| Test coverage adequate | 2 | Coverage ≥ project target (or ≥60% default) |
| No dead code or unused exports | 2 | Static analysis clean |
| Feature correctness audit | 2 | Implemented features match specifications |

---

### D4: Code Quality (15 points)

> Verify code meets quality gates. Delegates to the `/review` workflow.

**Primary Skill**: `verification-loop` · **Secondary Skill**: `clean-code` · **Check Method**: Delegate to `/review`

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| Lint passes | 3 | Zero lint errors |
| Type check passes | 3 | Zero type errors in strict mode |
| Build succeeds | 3 | Production build completes without errors |
| Code style compliance | 3 | Follows project conventions (naming, structure) |
| Dependency health | 3 | No critical/high vulnerabilities in dependencies |

---

### D5: Security & Privacy (18 points)

> Non-negotiable security assessment. Highest weight domain.

**Primary Skill**: `security-practices` · **Check Method**: OWASP check, secrets scan, dependency audit

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| No hardcoded secrets | 4 | Grep for API keys, passwords, tokens — zero matches |
| Dependencies vulnerability scan | 3 | No critical/high CVEs in production deps |
| Authentication/authorization audit | 3 | Auth flows follow security-practices skill standards |
| Input validation on all endpoints | 3 | No unvalidated user input reaches business logic |
| HTTPS/security headers configured | 3 | CSP, HSTS, X-Frame-Options present in production config |
| Privacy compliance check | 2 | PII handling documented, consent mechanisms present |

---

### D6: Configuration Readiness (8 points)

> Verify environment configuration is production-ready.

**Primary Skill**: `deployment-procedures` · **Secondary Skill**: `shell-conventions` · **Check Method**: Env var audit, config validation

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| All required env vars documented | 2 | `.env.example` or equivalent exists with all vars |
| No dev-only values in production config | 2 | No `localhost`, `debug=true`, dev API keys |
| Secrets management strategy defined | 2 | Secrets via env vars or vault, not committed |
| Environment-specific configs separated | 2 | Dev/staging/prod configs isolated |

---

### D7: Performance Baseline (8 points)

> Verify performance meets baseline thresholds.

**Primary Skill**: `performance-profiling` · **Check Method**: Bundle analysis, response time check

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| Bundle size within budget | 2 | Initial JS < 200KB gzipped (web) or reasonable for platform |
| No obvious performance anti-patterns | 2 | No N+1 queries, unbounded loops, memory leaks |
| Core Web Vitals baseline (web) | 2 | LCP < 2.5s, CLS < 0.1 (if applicable) |
| API response times acceptable | 2 | p95 < 500ms for critical endpoints |

---

### D8: Documentation (5 points)

> Verify operational documentation is adequate.

**Primary Skill**: `plan-writing` · **Check Method**: File existence and content check

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| README with setup instructions | 2 | README exists, includes install + run commands |
| API documentation (if applicable) | 1 | Endpoints documented or N/A justified |
| Runbook or incident procedures | 1 | Basic operational guide exists or N/A justified |
| CHANGELOG current | 1 | Recent changes documented |

---

### D9: Infrastructure & CI/CD (10 points)

> Verify deployment pipeline and infrastructure readiness.

**Primary Skill**: `deployment-procedures` · **Secondary Skill**: `docker-patterns` · **Check Method**: CI config analysis, deployment strategy

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| CI pipeline passes | 3 | All CI checks green on target branch |
| Deployment strategy defined | 2 | Deploy method documented (manual, CD, container) |
| Rollback capability exists | 3 | Rollback procedure tested or documented |
| Health check endpoint (if applicable) | 2 | `/health` or equivalent returns service status |

---

### D10: Observability & Monitoring (8 points)

> Verify incident visibility and error tracking readiness.

**Primary Skill**: `deployment-procedures` · **Check Method**: Config analysis, logging audit

| Sub-Check | Points | Pass Criteria |
| :--- | :--- | :--- |
| Error tracking configured | 3 | Error monitoring service connected (Sentry, etc.) or plan documented |
| Structured logging in place | 2 | Application logs are structured (JSON) with severity levels |
| Alerting configured for critical paths | 2 | At least downtime/error-rate alerts defined |
| No PII in logs | 1 | Grep logs config for email/password/token patterns |

---

## Scoring Model

### Domain Weights

| Domain | Weight | Max Score |
| :--- | :--- | :--- |
| D1: Task Completeness | 8% | 8 |
| D2: User Journey Validation | 10% | 10 |
| D3: Implementation Correctness | 10% | 10 |
| D4: Code Quality | 15% | 15 |
| D5: Security & Privacy | 18% | 18 |
| D6: Configuration Readiness | 8% | 8 |
| D7: Performance Baseline | 8% | 8 |
| D8: Documentation | 5% | 5 |
| D9: Infrastructure & CI/CD | 10% | 10 |
| D10: Observability & Monitoring | 8% | 8 |
| **Total** | **100%** | **100** |

---

### Go/No-Go Thresholds

| Score | Status | Action |
| :--- | :--- | :--- |
| ≥ 85/100 | 🟢 **Production Ready** | Proceed to `/pr` → `/deploy` |
| 70-84 | 🟡 **Conditionally Ready** | Fix medium issues, re-run with `--rescan` |
| < 70 | 🔴 **Not Ready** | Fix critical/high issues, re-run with `--rescan` |

---

### Blocker Rule Precedence

Blocker rules **override** the total score. Even if the total score is above threshold, a blocker rule violation forces a lower verdict.

**Evaluation order**: Blockers are checked BEFORE the total score is evaluated.

| Rule | Condition | Override Verdict | Rationale |
| :--- | :--- | :--- | :--- |
| **Zero Domain** | Any domain scores 0/max | 🔴 Not Ready | A completely unchecked domain is a blind spot |
| **Security Floor** | D5 < 50% (< 9/18) | 🔴 Not Ready | Security is non-negotiable for production |
| **Quality Floor** | D4 < 50% (score ≤ 7/15) | 🟡 Caps verdict at Conditionally Ready | Code quality below threshold needs attention |

**Precedence**: Zero Domain > Security Floor > Quality Floor > Total Score

---

### Evidence Requirements

Every sub-check score must be supported by one of:

- **File evidence**: path to file or config that proves compliance
- **Command output**: result of a verification command (lint, test, scan)
- **Observation**: documented observation with specific detail
- **N/A justification**: one-line reason why the check doesn't apply

Unsupported scores default to 0.

---

## Delta Comparison (`--rescan`)

When invoked with `--rescan`, compare against the most recent previous scorecard:

1. Load previous scorecard from conversation artifacts
2. Run full D1-D10 scan with current state
3. Generate delta table:

```markdown
| Domain | Previous | Current | Delta |
| :--- | :--- | :--- | :--- |
| D1: Tasks | 5/8 | 8/8 | +3 ✅ |
| D5: Security | 6/18 | 14/18 | +8 ✅ |
```

4. Highlight regressions (negative delta) with `[!WARNING]`
5. Summary: total improvement, remaining gaps, updated verdict

---

## Integration

- **Primary consumer**: `/preflight` workflow (Verify phase)
- **Reusable by**: `/retrospective` (sprint audit can reference domain definitions)
- **Reusable by**: `/deploy` (deployment pre-flight can reference D5, D6, D9 checks)
- **References**: 8 existing skills via the delegation map in domain definitions
