---
description: Fix pull request issues based on review comments from all reviewers (humans and bots). Fetch findings, prioritize by severity, implement fixes with before/after evidence, verify, push, and post detailed resolution summary attributing each fix to the original reviewer.
version: 1.1.0
sdlc-phase: build
skills: [pr-toolkit, verification-loop]
commit-types: [fix]
---

# /pr-fix — Pull Request Fix Workflow

> **Trigger**: `/pr-fix <url>` · `/pr-fix <owner/repo>#<number>` · `/pr-fix #<number>`
> **Lifecycle**: Build — remediation phase after review findings, before re-review

> [!CAUTION]
> This workflow modifies code and pushes to the PR branch. Ensure you have write access to the branch and that no other contributors are actively pushing to it. Coordinate with the PR author if you are not the author.

> [!TIP]
> This workflow leverages the **pr-toolkit** skill for fix prioritization and the **verification-loop** skill for post-fix validation. Read `.agent/skills/pr-toolkit/SKILL.md` for the fix prioritization framework.

---

## Scope Filter

| Commit Type | Behavior | Rationale |
| :--- | :--- | :--- |
| `fix()` | Full workflow (all steps) | Fix commits from review findings |

> This workflow always produces `fix` commits. The scope filter applies to the PR's original commit type for context only.

---

## Critical Rules

0. **NO ARTIFACT FILES** — NEVER save API responses, diffs, review bodies, fix plans, or intermediate data as files in the project directory. Process ALL data in memory via shell pipes, variables, or direct tool output. Files like `pr-17.json`, `pr-17.diff`, `pr-17-fix-comment.md`, `pr-17-comments.json` MUST NOT be created. If a command output is too large, use `head`/`tail` to truncate — do NOT redirect to a file
1. **ALWAYS** fetch and read ALL review comments (from humans AND bots) before implementing any fix — understand the full picture first
2. **ALWAYS** prioritize fixes: CRITICAL → HIGH → MEDIUM → LOW (never skip severity levels)
3. **ALWAYS** run `/review` pipeline after all fixes before pushing — never push broken code
4. **NEVER** modify code unrelated to review findings — stay scoped to the review
5. **NEVER** dismiss or resolve review comments without implementing the fix or providing justification
6. **ATOMIC** commits — one fix per commit with descriptive message referencing the finding. Exception: closely related documentation fixes in the same file may be grouped
7. **EVIDENCE MANDATE** — every fix MUST include `file:line` references, before/after code, and attribution to the original reviewer
8. **REVIEWER ATTRIBUTION** — every fix in the summary MUST attribute the finding to the reviewer who flagged it (e.g., "@gemini-code-assist", "@username")

---

## Argument Parsing

| Command | Action |
| :--- | :--- |
| `/pr-fix <url>` | Fix PR at the given GitHub URL |
| `/pr-fix <owner/repo>#<number>` | Fix PR by owner/repo and number |
| `/pr-fix #<number>` | Fix PR in current repo by number |
| `/pr-fix #<number> --critical-only` | Fix only CRITICAL findings |
| `/pr-fix #<number> --dry-run` | Show fix plan without implementing |

---

## Steps

Execute IN ORDER. Stop at first failure.

### Step 1: Parse PR Reference and Validate

// turbo

Parse the PR reference (same as `/pr-review` Step 1):

```bash
# Get repo if not specified
gh repo view --json nameWithOwner --jq .nameWithOwner

# Validate PR exists and is open
gh pr view <number> --repo <owner/repo> --json state,title,headRefName --jq '{state,title,headRefName}'
```

- If PR is closed/merged → **STOP**: "Cannot fix a closed/merged PR"
- If PR is open → proceed

### Step 2: Fetch ALL Review Comments (Humans + Bots)

Retrieve all review comments from ALL sources — human reviewers, bot reviewers (Gemini Code Assist, CodeRabbit, Copilot, SonarCloud), and general comments:

```bash
# Fetch PR review verdicts (REQUEST_CHANGES, COMMENT, APPROVE)
gh api repos/<owner>/<repo>/pulls/<number>/reviews

# Fetch inline review comments (file-specific findings from humans and bots)
gh api repos/<owner>/<repo>/pulls/<number>/comments

# Fetch issue-level comments (general PR conversation, bot summaries)
gh api repos/<owner>/<repo>/issues/<number>/comments

# Get PR diff for context
gh pr diff <number> --repo <owner/repo>
```

Extract and categorize each comment:

| Field | Description | Example |
| :--- | :--- | :--- |
| **Reviewer** | Who posted the comment (username or bot name) | `@gemini-code-assist`, `@emredursun` |
| **Type** | Inline (file-specific) or general (PR-level) | `inline` at `skills/README.md:28` |
| **Finding** | What the reviewer flagged | "Operational Skills count should be 7, not 6" |
| **Severity** | Mapped from reviewer's labels or inferred | `MEDIUM` |
| **Suggested fix** | If the reviewer provided a code suggestion | `## Operational Skills (7)` |
| **Status** | Open, resolved, or outdated | `open` |

**Bot-specific parsing:**
- **Gemini Code Assist**: Look for `Medium Priority` / `High Priority` labels and `Suggested change` blocks
- **CodeRabbit**: Look for severity badges and inline suggestions
- **SonarCloud**: Look for quality gate status and inline issues
- **Human reviewers**: Parse REQUEST_CHANGES body for severity indicators (must fix, should fix, nit)

Skip already-resolved comments (marked as resolved or outdated by GitHub).

### Step 3: Categorize and Prioritize Fixes

Apply the pr-toolkit fix prioritization framework:

| Priority | Category | Examples |
| :--- | :--- | :--- |
| P0 | CRITICAL | Security vulnerabilities, data loss, crashes |
| P1 | HIGH | Broken functionality, failed tests, code quality blockers |
| P2 | MEDIUM | Documentation inconsistencies, naming, count mismatches |
| P3 | LOW/NIT | Suggestions, preferences, nice-to-haves |

Generate a fix plan with reviewer attribution:

```markdown
## Fix Plan for PR #{number} — {title}

| # | Priority | Reviewer | File:Line | Finding | Planned Fix |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | P2 | @gemini-code-assist | `skills/README.md:28` | Operational Skills count wrong (5→6, should be 7) | Update heading to `## Operational Skills (7)` |
| 2 | P2 | @gemini-code-assist | `skills/README.md:96` | pr-toolkit categorized as Development, should be Operations | Move to Domain > Operations section |
| ... | ... | ... | ... | ... | ... |

**Total**: {p0} P0, {p1} P1, {p2} P2, {p3} P3
**Source**: {n} from humans, {n} from bots
```

If `--dry-run` flag → display fix plan and **STOP**
If `--critical-only` flag → filter to P0 only

### Step 4: Checkout PR Branch

```bash
# Fetch the PR branch
git fetch origin pull/<number>/head:<branch-name>
# Or if you have push access:
git fetch origin <head-branch>
git checkout <head-branch>

# Ensure branch is up to date
git pull origin <head-branch>
```

- If checkout fails → **STOP**: "Cannot checkout PR branch — check access permissions"
- If branch has conflicts with base → resolve conflicts first per `/pr` conflict resolution protocol

### Step 5: Implement Fixes

Implement fixes in priority order (P0 → P1 → P2 → P3):

For each fix:

1. **Read** the affected file and understand the context
2. **Record before state** — capture the exact code/content before the fix (with line number)
3. **Implement** the fix addressing the reviewer's specific concern
4. **Record after state** — capture the exact code/content after the fix
5. **Verify** the fix resolves the issue (run affected tests if applicable)
6. **Commit** with descriptive message referencing the finding and reviewer:

```bash
git add <fixed-files>
git commit -m "fix(review): <description of fix>

Addresses @<reviewer>'s finding at <file>:<line>:
<summary of reviewer's finding>"
```

**Fix Guidelines:**
- Address the reviewer's exact concern — do not over-fix or refactor adjacent code
- If a finding requires a larger change than expected, document the scope and confirm with user
- If a finding is incorrect or not applicable, prepare a justification comment instead of a code change
- For bot suggestions with `Suggested change` blocks, apply the exact suggestion when valid
- When applying a fix, verify it doesn't introduce a new inconsistency elsewhere (cross-file consistency check)

**Grouping Exception:**
- Closely related fixes in the same file from the same reviewer MAY be grouped into a single commit if they are logically inseparable (e.g., updating a count heading AND moving an item in the same table). Document the grouping reason in the commit message.

### Step 6: Run Verification

After all fixes are implemented, run the full verification pipeline:

```bash
# Delegate to /review pipeline
# Gates: lint → type-check → tests → security → build
```

Record the result of each gate:

| Gate | Status | Details |
| :--- | :--- | :--- |
| Lint | Pass/Fail | {output summary} |
| Type Check | Pass/Fail | {output summary} |
| Tests | Pass/Fail | {n}/{n} passing |
| Security | Pass/Fail | {output summary} |
| Build | Pass/Fail | {output summary} |

- If any gate fails → fix the failure, re-run verification (max 3 retry cycles)
- If all gates pass → proceed to push
- If verification cannot pass after 3 cycles → **STOP** and report partial progress

### Step 7: Push Fixes

```bash
git push origin <head-branch>
```

- If push rejected → pull latest, resolve conflicts, re-verify, retry push
- If push succeeds → proceed to comment

### Step 8: Post Resolution Summary

Post a detailed summary comment on the PR documenting all fixes with before/after evidence and reviewer attribution:

```bash
gh pr comment <number> --repo <owner/repo> --body "## Review Fixes Applied — PR #{number}

### Fixes Summary

| # | Priority | Reviewer | File:Line | Finding | Fix Applied | Commit |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | P2 | @gemini-code-assist | \`skills/README.md:28\` | Operational Skills count incorrect (6→7) | Updated heading to \`## Operational Skills (7)\` | [\`abc1234\`](link) |
| 2 | P2 | @gemini-code-assist | \`skills/README.md:96\` | pr-toolkit categorization inconsistency | Moved pr-toolkit from Development to Domain > Operations | [\`abc1234\`](link) |

### Before / After

**Fix 1** — \`skills/README.md:28\` (@gemini-code-assist)
\`\`\`diff
- ## Operational Skills (6)
+ ## Operational Skills (7)
\`\`\`

**Fix 2** — \`skills/README.md:96\` (@gemini-code-assist)
\`\`\`diff
  ## Development Skills (10)
- | [pr-toolkit](pr-toolkit/SKILL.md) | PR lifecycle domain knowledge |
+ ## Development Skills (9)

  ### Operations
+ | [pr-toolkit](pr-toolkit/SKILL.md) | PR lifecycle domain knowledge |
\`\`\`

### Verification

| Gate | Status |
| :--- | :--- |
| Lint | :white_check_mark: Pass |
| Type Check | :white_check_mark: Pass |
| Tests | :white_check_mark: Pass ({n}/{n}) |
| Security | :white_check_mark: Pass |
| Build | :white_check_mark: Pass |

### Disposition

| Category | Count | Status |
| :--- | :--- | :--- |
| P0 (Critical) | {n} | {All fixed / N/A} |
| P1 (High) | {n} | {All fixed / N/A} |
| P2 (Medium) | {n} | {All fixed} |
| P3 (Low/NIT) | {n} | {Fixed / Deferred with justification} |

**Total**: {n} fixes applied across {n} commits
**Ready for re-review** :arrows_counterclockwise:"
```

Re-request review from the original reviewer(s):

```bash
# Re-request from human reviewers who requested changes
gh pr edit <number> --repo <owner/repo> --add-reviewer <reviewer>
```

For bot reviewers (Gemini, CodeRabbit), they will automatically re-analyze on the new push — no manual re-request needed.

---

## Output Template

### Fixes Applied Successfully

```markdown
## PR Fix Complete: #{number} — {title}

| Field | Value |
| :--- | :--- |
| PR | #{number} — {title} |
| Branch | {head-branch} |
| Fixes Applied | {count} ({n} from humans, {n} from bots) |
| Commits | {commit count} |
| Verification | All {n} gates passed |

### Fix Summary

| # | Priority | Reviewer | File:Line | Fix Applied | Commit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | {P0-P3} | @{reviewer} | `{file}:{line}` | {description} | `{sha}` |

### Verification Results

| Gate | Status | Details |
| :--- | :--- | :--- |
| Lint | {status} | {detail} |
| Type Check | {status} | {detail} |
| Tests | {status} | {n}/{n} passing |
| Security | {status} | {detail} |
| Build | {status} | {detail} |

### Disposition

| Priority | Count | Status |
| :--- | :--- | :--- |
| P0 (Critical) | {n} | {status} |
| P1 (High) | {n} | {status} |
| P2 (Medium) | {n} | {status} |
| P3 (Low) | {n} | {status} |

**Next**: Wait for re-review from @{reviewer}. Bot reviewers will re-analyze automatically on push.
```

### Fix Failed

```markdown
## PR Fix Failed at Step {N}

### Error
{error description}

### Resolution
1. {fix steps}
2. Re-run: `/pr-fix <reference>`

### Partial Progress
| # | Fix | Status | Commit |
| :--- | :--- | :--- | :--- |
| 1 | {fix description} | Applied | `{sha}` |
| 2 | {fix description} | Failed — {reason} | — |
```

---

## Governance

**PROHIBITED:**
- Modifying code unrelated to review findings
- Pushing without running full verification pipeline
- Dismissing review comments without justification
- Force-pushing over the PR branch (use regular push only)
- Skipping CRITICAL or HIGH findings (unless `--critical-only` is used)
- Resolving review threads without implementing the fix
- Posting fix summaries without `file:line` references — every fix must cite its location
- Posting fix summaries without reviewer attribution — every fix must credit the reviewer who flagged it
- Using generic titles like "Review Fixes Applied" without PR context
- Omitting before/after code diffs in the resolution comment

**REQUIRED:**
- Read ALL review comments (humans AND bots) before implementing any fix
- Priority-ordered fixing (P0 → P1 → P2 → P3)
- Atomic commits — one fix per commit with review reference (grouping exception documented)
- Full `/review` pipeline pass before push with per-gate status recorded
- Detailed summary comment with: reviewer attribution, file:line, before/after diffs, verification results
- Re-request review from original human reviewers
- Content-specific comment title: "Review Fixes Applied — PR #{number}" (not generic)

---

## Completion Criteria

- [ ] PR reference parsed and validated (open PR)
- [ ] All review comments fetched from ALL sources (human reviews, bot inline comments, general comments)
- [ ] Each comment attributed to its reviewer (human or bot name)
- [ ] Fix plan generated with priority ordering and reviewer attribution
- [ ] PR branch checked out and up to date
- [ ] All applicable fixes implemented (by priority level)
- [ ] Before/after state recorded for each fix
- [ ] Each fix committed with descriptive message referencing reviewer and file:line
- [ ] Full verification pipeline passed with per-gate status
- [ ] Detailed summary comment posted on PR (with attribution, file:line, before/after diffs, gate results)
- [ ] Re-review requested from original human reviewer(s)

---

## Related Resources

- **Skill**: `.agent/skills/pr-toolkit/SKILL.md` — fix prioritization framework, commit conventions
- **Previous**: `/pr-review` (review findings that drive fixes)
- **Next**: Re-review cycle → `/pr-review` or manual reviewer re-check
- **Related**: `/review` (local verification pipeline) · `/pr` (PR creation)
- **Rule**: `.agent/rules/git-workflow.md` — commit conventions
