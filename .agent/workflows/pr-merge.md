---
description: Safe PR merge with dependency validation, CI verification, post-merge checks, and branch cleanup.
version: 1.0.0
sdlc-phase: ship
skills: [pr-toolkit, verification-loop]
commit-types: [feat, fix, refactor, perf, chore, docs, test]
---

# /pr-merge — Safe Pull Request Merge Workflow

> **Trigger**: `/pr-merge <url>` · `/pr-merge <owner/repo>#<number>` · `/pr-merge #<number>`
> **Lifecycle**: Ship — after review approval, final step before deployment

> [!CAUTION]
> Merging a PR modifies the target branch and is difficult to reverse without force-push. Ensure all checks pass, reviews are approved, and dependencies are merged before proceeding. This workflow enforces pre-merge and post-merge validation.

> [!TIP]
> This workflow leverages the **pr-toolkit** skill for dependency validation and merge strategy selection. Read `.agent/skills/pr-toolkit/SKILL.md` for dependency management details.

---

## Scope Filter

| Commit Type | Merge Mode | Gates |
| :--- | :--- | :--- |
| `feat`, `fix`, `refactor`, `perf` | Full (all steps) | All checks required |
| `chore`, `docs`, `test` | Lightweight | Skip Step 4 (post-merge verification) |

---

## Critical Rules

0. **NO ARTIFACT FILES** — NEVER save API responses, diffs, or intermediate data as files in the project directory. Process ALL data in memory via shell pipes, variables, or direct tool output
1. **NEVER** merge a PR with failing CI checks — no exceptions
2. **NEVER** merge a PR without at least 1 approval (unless solo project)
3. **NEVER** merge a PR with unresolved blocking dependencies (`Depends-On:` PRs still open)
4. **ALWAYS** verify the merge target matches the detected branch strategy
5. **ALWAYS** run post-merge validation to catch integration issues immediately
6. **PREFER** squash merge for feature branches, merge commit for release/dev→main

---

## Argument Parsing

| Command | Action |
| :--- | :--- |
| `/pr-merge #<number>` | Merge PR in current repo |
| `/pr-merge <url>` | Merge PR at GitHub URL |
| `/pr-merge #<number> --squash` | Force squash merge |
| `/pr-merge #<number> --merge-commit` | Force merge commit |
| `/pr-merge #<number> --rebase` | Force rebase merge |
| `/pr-merge #<number> --dry-run` | Validate merge readiness without merging |

---

## Steps

Execute IN ORDER. Stop at first failure.

### Step 1: Parse PR Reference and Validate State

// turbo

```bash
gh pr view <number> --repo <owner/repo> \
  --json state,mergeable,mergeStateStatus,title,baseRefName,headRefName,reviewDecision,statusCheckRollup
```

Validate:
- PR is OPEN (not closed or already merged)
- PR is mergeable (no conflicts)
- `mergeStateStatus` is not `BLOCKED`

If validation fails → **STOP** with specific error message.

### Step 2: Verify Merge Prerequisites

// turbo

**2a. Review Approval**:
```bash
gh pr view <number> --repo <owner/repo> --json reviewDecision --jq '.reviewDecision'
```
- If `APPROVED` → proceed
- If `REVIEW_REQUIRED` or `CHANGES_REQUESTED` → **STOP**: "PR requires review approval"

**2b. CI Status**:
```bash
gh pr checks <number> --repo <owner/repo>
```
- All required checks must pass
- If any check failed → **STOP**: "CI check `{name}` failed — fix before merge"
- If checks pending → **WAIT** or **STOP**: "CI checks still running"

**2c. Dependency Validation** (per pr-toolkit dependency management):
```bash
# Extract Depends-On from PR body
gh pr view <number> --repo <owner/repo> --json body --jq '.body' | grep -i 'Depends-On'
```
- For each dependency, verify status is `MERGED`
- If any dependency is OPEN → **STOP**: "Blocking dependency #{dep} is not yet merged"
- If no dependencies → proceed

**2d. Branch Strategy Validation**:
- Verify the merge target matches detected branch strategy
- GitFlow: feature→dev (not main), dev→main (sprint merge), hotfix→main
- If target mismatch → **WARN** (non-blocking for merge, but flag it)

### Step 3: Execute Merge

**3a. Select Merge Strategy**:

| Scenario | Default Strategy | Rationale |
| :--- | :--- | :--- |
| Feature → dev/develop | Squash merge | Clean history, single commit per feature |
| dev → main (release) | Merge commit | Preserve branch history for audit |
| hotfix → main | Squash merge | Fast, clean hotfix |
| User specified `--squash/--merge-commit/--rebase` | User's choice | Explicit override |

**3b. Execute**:
```bash
gh pr merge <number> --repo <owner/repo> \
  --{squash|merge|rebase} \
  --delete-branch \
  --subject "<merge commit title>"
```

- If merge fails (race condition, conflict) → **STOP** with error
- `--delete-branch` auto-cleans the merged branch

### Step 4: Post-Merge Validation

// turbo

**4a. Verify merge was recorded**:
```bash
gh pr view <number> --repo <owner/repo> --json state,mergedAt --jq '{state,mergedAt}'
```

**4b. Check target branch CI** (if available):
```bash
# Check if CI triggered on the target branch after merge
gh run list --repo <owner/repo> --branch <target> --limit 1
```

**4c. Update dependent PRs** (if any PRs depend on this one):
```bash
# Search for PRs that have "Depends-On: #<number>" in their body
gh pr list --repo <owner/repo> --state open --json number,body \
  --jq '[.[] | select(.body | test("Depends-On.*#'<number>'"))] | .[].number'
```
- For each dependent PR, post a comment: "Dependency #{number} has been merged. This PR may now be ready to merge."

### Step 5: Report Results

// turbo

Report merge status and any post-merge actions needed.

---

## Output Template

### Merge Successful

```markdown
## PR Merged Successfully: #{number}

| Field | Value |
| :--- | :--- |
| PR | #{number} — {title} |
| Merged into | {base branch} |
| Strategy | {squash / merge commit / rebase} |
| Branch | {head branch} — deleted |
| Merged at | {timestamp} |

### Post-Merge Status
| Check | Status |
| :--- | :--- |
| CI on target branch | {running / passed / N/A} |
| Dependent PRs notified | {count} PRs |
| Branch cleanup | Deleted |

**Next**: `/deploy` when ready · or continue with dependent PRs
```

### Merge Blocked

```markdown
## PR Merge Blocked: #{number}

| Blocker | Status |
| :--- | :--- |
| {blocker description} | {detail} |

### Resolution
1. {fix steps}
2. Re-run: `/pr-merge #<number>`
```

---

## Governance

**PROHIBITED:**
- Merging PRs with failing CI checks
- Merging PRs without review approval
- Merging PRs with unresolved blocking dependencies
- Force-merging past branch protection rules
- Merging without verifying branch strategy compliance
- Using `// turbo` on the merge execution step (Step 3)

**REQUIRED:**
- All CI checks passing
- At least 1 review approval
- All `Depends-On` dependencies merged
- Branch strategy validation
- Post-merge CI verification (for non-chore PRs)
- Auto-delete merged branch
- Notify dependent PRs after merge

---

## Completion Criteria

- [ ] PR state validated (open, mergeable, not blocked)
- [ ] Review approval confirmed
- [ ] All CI checks passing
- [ ] Dependencies validated (all merged)
- [ ] Branch strategy compliance verified
- [ ] Merge executed with appropriate strategy
- [ ] Merged branch deleted
- [ ] Post-merge CI status checked
- [ ] Dependent PRs notified

---

## Related Resources

- **Skill**: `.agent/skills/pr-toolkit/SKILL.md` — dependency management, merge strategy selection
- **Previous**: `/pr-review` (review approved) · `/pr-fix` (findings addressed)
- **Next**: `/deploy` (deployment after merge)
- **Related**: `/pr` (PR creation) · `/pr-status` (check merge readiness)
