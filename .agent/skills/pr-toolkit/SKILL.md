---
name: pr-toolkit
description: Pull request lifecycle domain knowledge — branch strategy detection, PR size classification, confidence-scored review, git-aware context, PR analytics, dependency management, and split/merge/describe operations.
version: 2.0.0
triggers: [pr, pull-request, review, merge, branch, code-review]
allowed-tools: Read, Grep, Bash
---

# PR Toolkit Skill

> **Purpose**: Provide domain knowledge for the complete PR lifecycle — creation, review, remediation, merge, split, describe, analytics, and dependency management. Used by `/pr`, `/pr-review`, `/pr-fix`, `/pr-merge`, `/pr-split`, `/pr-describe`, and `/pr-status`.

---

## 1. Branch Strategy Detection

Detect the project's branching model before any PR operation. This enables generic behavior across GitFlow, trunk-based, and hybrid strategies.

### Detection Protocol

```bash
# Check for GitFlow indicators
git branch -r | grep -E 'origin/(dev|develop)$'
# Check for release branches
git branch -r | grep -E 'origin/release/'
```

| Indicator | Strategy | Description |
| :--- | :--- | :--- |
| `dev` or `develop` branch exists | GitFlow | Feature branches merge to dev; dev merges to main at release |
| Only `main`/`master` exists | Trunk-Based | Short-lived feature branches merge directly to main |
| `release/*` branches exist | GitFlow (full) | Includes release branch phase before main |

### Target Branch Validation — GitFlow

| Source Branch Pattern | Valid Target | Invalid Target | Action on Invalid |
| :--- | :--- | :--- | :--- |
| `feature/*` | `dev`, `develop` | `main`, `master` | **BLOCK** — redirect to dev |
| `bugfix/*` | `dev`, `develop` | `main`, `master` | **BLOCK** — redirect to dev |
| `hotfix/*` | `main`, `master` | — | Proceed (emergency path) |
| `release/*` | `main`, `master` | — | Proceed (release cut) |
| `dev`, `develop` | `main`, `master` | — | Proceed (sprint merge) |
| `chore/*`, `docs/*` | `dev`, `develop` | `main`, `master` | **BLOCK** — redirect to dev |

### Target Branch Validation — Trunk-Based

| Source Branch Pattern | Valid Target | Action |
| :--- | :--- | :--- |
| Any short-lived branch | `main`, `master` | Proceed |

### Auto-Detection Output

```markdown
**Branch Strategy**: GitFlow detected (origin/dev exists)
**Target Validation**: feature/X → dev ✅ (valid) | feature/X → main ❌ (invalid — redirect to dev)
```

---

## 2. PR Size Classification

Classify PRs to enforce reviewability standards. Based on Google's recommended PR size guidelines.

### Size Matrix

| Label | Files Changed | Lines Changed | Estimated Review Time | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **XS** | 1-5 | < 100 | < 15 min | Fast-track review |
| **S** | 6-15 | 100-300 | 15-30 min | Standard review |
| **M** | 16-30 | 300-700 | 30-60 min | Thorough review |
| **L** | 31-50 | 700-1500 | 1-2 hours | Consider splitting |
| **XL** | 50+ | 1500+ | 2+ hours | **MUST split** — block creation |

### Detection Commands

```bash
# Count changed files
git diff --name-only origin/<target>..HEAD | wc -l
# Count changed lines
git diff --stat origin/<target>..HEAD | tail -1
```

### Scope Coherence Check

A PR is scope-coherent when ALL changed files relate to ONE logical change.

| Violation | Detection Pattern | Severity |
| :--- | :--- | :--- |
| Mixed feature + tooling | Framework/config files alongside source code | HIGH |
| Mixed feature + dependency upgrade | Unrelated `package.json` bumps alongside feature | MEDIUM |
| Mixed feature + documentation restructure | Deleted/moved docs alongside new code | HIGH |
| Multiple unrelated features | Changes span unrelated modules with no shared dependency | CRITICAL |

**Remediation**: Split into focused PRs:

1. Tooling/config changes → separate `chore:` PR
2. Dependency upgrades → separate `chore(deps):` PR
3. Documentation → separate `docs:` PR
4. Feature code → focused `feat:` PR

---

## 3. Title Format Enforcement

### Conventional Commits Title Format

```
type(scope): description
```

### Validation Rules

| Rule | Valid Example | Invalid Example |
| :--- | :--- | :--- |
| Has type prefix | `feat(auth): add login` | `add login feature` |
| Lowercase type | `feat:` | `Feat:`, `FEAT:` |
| Parenthesized scope (recommended) | `feat(auth):` | `feat-auth:` |
| Colon + space after type/scope | `feat: add` | `feat:add` |
| Imperative mood | `add`, `fix`, `update` | `added`, `fixes`, `updating` |
| No period at end | `feat: add login` | `feat: add login.` |
| Under 72 characters | Short description | Exceeds 72 character limit... |

### Branch-to-Title Parser

| Branch Name | Parsed Title |
| :--- | :--- |
| `feature/ABC-123-add-user-auth` | `feat(user): add user auth` |
| `bugfix/ABC-456-fix-login` | `fix(login): fix login` |
| `hotfix/PROD-001-patch-xss` | `fix(security): patch xss` |
| `chore/update-deps` | `chore(deps): update deps` |
| `docs/api-reference` | `docs(api): api reference` |

### Parsing Algorithm

1. Extract branch type prefix: `feature/` → `feat`, `bugfix/` → `fix`, `hotfix/` → `fix`
2. Remove ticket prefix: `ABC-123-` → strip
3. Extract first segment as scope: `add-user-auth` → scope: `user`
4. Remaining segments as description: `add user auth`
5. Compose: `feat(user): add user auth`
6. If parsing fails → fallback to first commit message subject line

---

## 4. Review Patterns

### Multi-Perspective Review Framework

When reviewing a PR, apply these 6 perspectives sequentially:

| # | Perspective | Focus | Key Questions |
| :--- | :--- | :--- | :--- |
| 1 | **PR Hygiene** | Structure | Title format? Body complete? Size acceptable? Scope coherent? |
| 2 | **Branch Strategy** | Process | Correct target branch? Branch naming convention? |
| 3 | **Code Quality** | Standards | Functions < 50 lines? Files < 800 lines? No deep nesting? Error handling? |
| 4 | **Security** | Vulnerabilities | Hardcoded secrets? Input validation? Injection? XSS? Auth checks? |
| 5 | **Testing** | Coverage | New code has tests? Edge cases covered? Coverage maintained? |
| 6 | **Architecture** | Design | Follows existing patterns? SOLID? No over-engineering? Clean dependencies? |

### Review Severity Levels

| Severity | Label | Action Required | Blocks Merge? |
| :--- | :--- | :--- | :--- |
| **CRITICAL** | :red_circle: | Must fix — security, data loss, crash risk | Yes |
| **HIGH** | :orange_circle: | Should fix — broken functionality, quality blocker | Yes (3+) |
| **MEDIUM** | :yellow_circle: | Consider fixing — improvement suggestion | No |
| **LOW** | :blue_circle: | Nice to have — optional improvement | No |
| **NIT** | :white_circle: | Style preference — no action required | No |

### Review Verdict Decision Table

| Condition | Verdict |
| :--- | :--- |
| Zero CRITICAL + zero HIGH | **APPROVE** |
| Zero CRITICAL + minor HIGH (1-2, acknowledged) | **COMMENT** |
| Any CRITICAL OR 3+ HIGH | **REQUEST_CHANGES** |

---

## 5. Fix Prioritization Framework

When implementing fixes from review comments:

### Priority Order

1. **CRITICAL** (security, data loss, crashes) → fix immediately
2. **HIGH** (broken functionality, code quality blockers) → fix before merge
3. **MEDIUM** (style, naming, documentation) → fix if time permits
4. **LOW/NIT** (preferences, suggestions) → optional

### Fix Commit Convention

```bash
# Individual fix commits (during fix process)
fix(review): address hardcoded API key in auth.ts
fix(review): add input validation for user endpoint

# Squash commit (final push)
fix(review): address PR #N review findings
```

### Fix Verification Protocol

After each fix:

1. Run affected tests
2. Verify the reviewer's specific concern is addressed
3. Reference the review comment in commit message

After all fixes:

1. Run full `/review` pipeline (lint, types, tests, security, build)
2. Push with descriptive commit
3. Re-request review from original reviewer
4. Comment on PR summarizing all changes made

---

## 6. PR Body Completeness Checklist

A complete PR body must contain:

| Section | Required | Description |
| :--- | :--- | :--- |
| Summary | Always | 1-3 sentences describing the change and its motivation |
| Changes | Always | Categorized list of what changed |
| Test Plan | Always | How to verify the changes work |
| Breaking Changes | When applicable | What breaks and migration steps |
| Related Issues | When applicable | `Closes #N` or `Related to #N` |
| Screenshots | For UI changes | Before/after visual comparison |
| Checklist | Always | Standard verification items completed |

---

## 7. Repository Health Signals

When creating or reviewing PRs, check for these repo-level indicators and recommend improvements:

| Signal | Check Method | Healthy State | Recommendation if Missing |
| :--- | :--- | :--- | :--- |
| Branch protection | `gh api repos/{owner}/{repo}/branches/{branch}/protection` | Rules configured | Set up branch protection rules |
| PR template | `.github/pull_request_template.md` exists | Template present | Create PR template |
| CODEOWNERS | `CODEOWNERS` or `.github/CODEOWNERS` exists | File present | Define code ownership |
| CI pipeline | `.github/workflows/` contains CI config | Workflows present | Set up CI/CD pipeline |
| Auto-delete branches | `gh api repos/{owner}/{repo} --jq .delete_branch_on_merge` | `true` | Enable auto-delete |
| Default branch | `gh api repos/{owner}/{repo} --jq .default_branch` | Matches strategy | Align with branch strategy |

---

## 8. Confidence Scoring Framework

Every review finding receives a confidence score (0-100) alongside its severity level. Findings below the configurable threshold are suppressed from the review output. Based on Anthropic's Code Review architecture.

### Confidence Scale

| Score Range | Label | Meaning | Action |
| :--- | :--- | :--- | :--- |
| 90-100 | **Certain** | Definitely a real issue — clear evidence in code | Always report |
| 70-89 | **High** | Very likely real — strong indicators present | Report (above default threshold) |
| 50-69 | **Moderate** | Possibly real — some indicators but ambiguous | Suppress by default |
| 25-49 | **Low** | Unlikely — weak signals, may be intentional | Suppress |
| 0-24 | **Noise** | Almost certainly false positive | Never report |

### Threshold Configuration

- **Default threshold**: 70 (report High + Certain findings only)
- **Strict mode** (`--strict`): threshold 50 (include Moderate)
- **Relaxed mode** (`--relaxed`): threshold 90 (only Certain)

### Scoring Heuristics

| Factor | Score Adjustment | Rationale |
| :--- | :--- | :--- |
| Pattern matches known vulnerability (OWASP) | +30 | High-confidence security pattern |
| Issue is in PR-introduced code (not pre-existing) | +20 | Git-aware context confirms newness |
| Issue has file:line evidence | +15 | Specific, verifiable finding |
| Codebase has similar patterns elsewhere | -15 | May be intentional project convention |
| Issue is style/preference only | -20 | Subjective, not objective |
| Test file or generated code | -25 | Lower risk context |

### Output Format with Confidence

```markdown
### CRITICAL (confidence: 95/100)

#### Hardcoded API key in auth service
- **File**: `src/auth/client.ts:42`
- **Confidence**: 95 — matches known secret pattern, introduced in this PR
- **Issue**: API key exposed in source code
- **Fix**: Move to environment variable via `process.env.AUTH_API_KEY`
```

---

## 9. PR Analytics & Metrics

Track PR lifecycle metrics aligned with DORA and industry standards. Used by `/pr-status` for reporting and trend detection.

### Core PR Metrics

| Metric | Definition | How to Measure | Healthy Target |
| :--- | :--- | :--- | :--- |
| **Coding Time** | First commit to PR open | `git log --format=%aI` on first commit vs PR creation time | < 2 days |
| **Pickup Time** | PR creation to first review action | PR `created_at` vs first review `submitted_at` | < 4 hours |
| **Review Time** | First review to merge | First review `submitted_at` vs `merged_at` | < 24 hours |
| **Cycle Time** | First commit to merge (end-to-end) | Sum of coding + pickup + review time | < 3 days |
| **Merge Frequency** | PRs merged per developer per week | Count of merged PRs / active devs / weeks | 3-5 PRs/dev/week |
| **Review Rounds** | Number of review cycles before merge | Count of `REQUEST_CHANGES` events | < 2 rounds |
| **PR Size (median)** | Median lines changed per PR | `additions + deletions` across merged PRs | 100-300 LOC |

### DORA Alignment

| DORA Metric | PR Toolkit Signal | Measurement |
| :--- | :--- | :--- |
| **Deployment Frequency** | Merge frequency | PRs merged to main/production per time period |
| **Lead Time for Changes** | Cycle time | First commit to production deployment |
| **Change Failure Rate** | Revert rate | PRs that required hotfix or revert after merge |
| **Mean Time to Recovery** | Hotfix cycle time | Time from incident to hotfix PR merged |

### Data Collection Commands

```bash
# List merged PRs with dates (last 30 days)
gh pr list --repo <owner/repo> --state merged --limit 50 \
  --json number,title,createdAt,mergedAt,additions,deletions,changedFiles,reviews

# Calculate cycle time for a specific PR
gh pr view <number> --repo <owner/repo> \
  --json createdAt,mergedAt,reviews,commits

# Review turnaround per reviewer
gh api repos/<owner>/<repo>/pulls/<number>/reviews \
  --jq '[.[] | {user: .user.login, submitted: .submitted_at, state: .state}]'
```

### Staleness Detection

| PR Age | Status | Action |
| :--- | :--- | :--- |
| < 3 days | Fresh | Normal flow |
| 3-7 days | Aging | Nudge reviewers |
| 7-14 days | Stale | Escalate to team lead |
| 14+ days | Abandoned | Consider closing with comment |

---

## 10. PR Dependency Management

Manage dependencies between PRs to ensure correct merge ordering. Based on Mergify's `Depends-On` pattern.

### Depends-On Convention

Add dependency declarations in the PR body:

```markdown
## Dependencies

Depends-On: #42
Depends-On: #45
Depends-On: https://github.com/org/other-repo/pull/10
```

### Dependency Rules

| Rule | Description |
| :--- | :--- |
| **Block merge** | A PR with unmerged dependencies cannot be merged |
| **Cross-repo support** | Dependencies can reference PRs in other repositories |
| **Cycle detection** | If PR A depends on PR B and PR B depends on PR A → **BLOCK** both with warning |
| **Transitive** | If A depends on B and B depends on C, then A implicitly depends on C |

### Detection Commands

```bash
# Extract Depends-On from PR body
gh pr view <number> --repo <owner/repo> --json body \
  --jq '.body' | grep -oP 'Depends-On:\s*#?\d+|Depends-On:\s*https://[^\s]+'

# Check dependency PR status
gh pr view <dep-number> --repo <owner/repo> --json state --jq '.state'
```

### Dependency Validation Output

```markdown
## Dependency Check: PR #{number}

| Dependency | Status | Blocking? |
| :--- | :--- | :--- |
| #42 | MERGED | No |
| #45 | OPEN (approved) | Yes — must merge first |
| org/other-repo#10 | OPEN (in review) | Yes — cross-repo dependency |

**Verdict**: 1 blocking dependency — cannot merge until #45 is merged.
```

---

## 11. PR Split Strategy

Guide for splitting large PRs into focused sub-PRs. Used by `/pr-split` workflow.

### Split Categories

| Category | Detection Pattern | Sub-PR Type |
| :--- | :--- | :--- |
| **Feature code** | `src/`, `lib/`, `app/` files | `feat:` PR |
| **Tests** | `tests/`, `__tests__/`, `*.test.*`, `*.spec.*` | `test:` PR |
| **Configuration** | `.agent/`, `.github/`, config files | `chore:` PR |
| **Dependencies** | `package.json`, lock files, `pubspec.yaml` | `chore(deps):` PR |
| **Documentation** | `*.md`, `docs/` | `docs:` PR |
| **Styling** | CSS/SCSS files, theme files | `style:` PR |
| **Infrastructure** | `Dockerfile`, CI/CD workflows, terraform | `ci:` or `chore:` PR |

### Split Protocol

1. **Analyze** the diff to categorize all changed files
2. **Group** files by category (feature, test, config, docs, deps)
3. **Identify** dependencies between groups (tests depend on feature code)
4. **Propose** split plan with merge order
5. **Create** sub-branches from the original branch using `git cherry-pick` or `git checkout -- <files>`
6. **Verify** each sub-PR independently passes `/review` pipeline

### Split Merge Order

```
chore(deps): update dependencies          ← merge first (no dependencies)
chore: update configuration               ← merge second
feat(feature): implement core feature     ← merge third
test(feature): add tests for feature      ← merge fourth (depends on feat)
docs: update documentation                ← merge last
```

---

## 12. PR Auto-Description

Generate PR title, summary, labels, and changelog from commits and diff. Used by `/pr-describe` command.

### Description Generation Algorithm

1. **Title**: Parse from branch name (section 3) or compose from commit messages
2. **Summary**: Aggregate commit messages into 1-3 sentence summary
3. **Changes**: Group commits by type (feat, fix, chore, docs) into categorized list
4. **Labels**: Auto-suggest labels based on file paths and commit types
5. **Related Issues**: Extract from commit messages (`Closes #N`, `Fixes #N`, `Relates to #N`)

### Label Suggestion Rules

| File Pattern | Suggested Label |
| :--- | :--- |
| `src/`, `lib/`, `app/` | `feature` or `bugfix` (from commit type) |
| `tests/`, `*.test.*` | `testing` |
| `docs/`, `*.md` | `documentation` |
| `*.css`, `*.scss`, `*.styled.*` | `styling` |
| `.github/`, `Dockerfile`, CI config | `infrastructure` |
| `package.json`, lock files | `dependencies` |
| Security-related files | `security` |

### Size Label (auto-assigned)

| PR Size | Label |
| :--- | :--- |
| XS (1-5 files, <100 LOC) | `size/XS` |
| S (6-15 files, 100-300 LOC) | `size/S` |
| M (16-30 files, 300-700 LOC) | `size/M` |
| L (31-50 files, 700-1500 LOC) | `size/L` |
| XL (50+ files, 1500+ LOC) | `size/XL` |

---

## 13. Existing Reviewer Comment Engagement

When reviewing or fixing PRs, analyze ALL existing reviews AND inline comments from all reviewers (including bots like Gemini Code Assist, CodeRabbit, Copilot, SonarCloud, etc.). Reference and respond to their findings — acknowledge valid points, challenge incorrect ones, and avoid duplicating already-flagged issues.

### Comment Fetching Protocol

Fetch comments from all three GitHub API endpoints:

```bash
# Review verdicts (APPROVE, REQUEST_CHANGES, COMMENT)
gh api repos/<owner>/<repo>/pulls/<number>/reviews

# Inline review comments (file-specific findings — where bots post)
gh api repos/<owner>/<repo>/pulls/<number>/comments

# General PR conversation (bot summaries, human discussion)
gh api repos/<owner>/<repo>/issues/<number>/comments
```

### Bot Identification

| Bot Name | Comment Pattern | Finding Format |
| :--- | :--- | :--- |
| `gemini-code-assist` | Inline comments with `Medium Priority` / `High Priority` labels, `Suggested change` blocks | Severity label + description + suggested code change |
| `coderabbitai` | Summary review + inline comments with severity badges | Structured review with inline suggestions |
| `github-actions[bot]` | CI check results and status comments | Pass/fail with log links |
| `sonarcloud[bot]` | Quality gate status + inline issues | Coverage, duplications, security hotspots |
| `dependabot[bot]` | Security alerts and version bumps | CVE references with severity |

### Engagement Rules

| Scenario | For `/pr-review` | For `/pr-fix` |
| :--- | :--- | :--- |
| Valid finding, still open | Agree: "As @{reviewer} flagged..." | Include in fix plan with attribution |
| Valid finding, already fixed | Acknowledge: "Resolved in {sha}" | Skip — already handled |
| Invalid/incorrect finding | Challenge with evidence | Skip fix, post justification comment |
| Duplicate of your finding | Reference theirs, skip yours | Fix once, attribute to first finder |
| Finding you missed | Amplify: "@{reviewer} correctly identified..." | Add to fix plan |

### Attribution Format

When posting review comments or fix summaries, always attribute findings:

```markdown
## For /pr-review output:
"Agree with @gemini-code-assist — the Operational Skills count at `skills/README.md:28`
should be 7, not 6. The heading was changed from (5) to (6) but two new skills were added
(plan-validation and production-readiness), making the correct count 7."

## For /pr-fix output:
| # | Priority | Reviewer | File:Line | Finding | Fix Applied | Commit |
| 1 | P2 | @gemini-code-assist | `skills/README.md:28` | Skills count wrong | Updated to (7) | `abc1234` |
```

### Cross-File Consistency Checks

When bot reviewers flag inconsistencies, verify across ALL related files:

| Check Type | Files to Cross-Reference | Example |
| :--- | :--- | :--- |
| Count headings | README.md headings vs actual items | "## Skills (6)" but 7 items listed |
| Categorization | README.md categories vs CheatSheet.md categories | pr-toolkit in "Development" vs "Operations" |
| Version strings | package.json, manifest.json, README badges | Version mismatch across files |
| Feature counts | manifest.json capabilities vs file system | Manifest says 21 workflows but 20 files exist |
