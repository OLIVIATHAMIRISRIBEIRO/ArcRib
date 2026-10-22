---
description: Guide splitting large PRs into focused sub-PRs by concern category with dependency-ordered merge plan.
version: 1.0.0
sdlc-phase: build
skills: [pr-toolkit, git-workflow]
commit-types: [chore]
---

# /pr-split — Pull Request Split Workflow

> **Trigger**: `/pr-split` (current branch) · `/pr-split #<number>` (existing PR)
> **Lifecycle**: Build — remediation for oversized PRs, before `/pr-review`

> [!CAUTION]
> Splitting a PR creates new branches and potentially modifies git history. This workflow uses `git cherry-pick` and selective checkout — it does NOT rewrite existing commits. The original PR/branch is preserved until the user explicitly closes it.

> [!TIP]
> This workflow leverages the **pr-toolkit** skill for split strategy (section 11) and size classification (section 2). PRs classified as L or XL are candidates for splitting.

---

## Critical Rules

0. **NO ARTIFACT FILES** — NEVER save API responses, diffs, or intermediate data as files in the project directory. Process ALL data in memory via shell pipes, variables, or direct tool output
1. **NEVER** delete or force-push the original branch — preserve it as reference
2. **ALWAYS** analyze the full diff before proposing a split plan
3. **ALWAYS** verify each sub-PR independently passes `/review` pipeline
4. **ALWAYS** include dependency ordering in the split plan
5. **PRESERVE** all commits — use cherry-pick or selective checkout, not rebase
6. **ATOMIC** sub-PRs — each must be independently mergeable and testable

---

## Argument Parsing

| Command | Action |
| :--- | :--- |
| `/pr-split` | Analyze current branch for splitting |
| `/pr-split #<number>` | Analyze existing PR for splitting |
| `/pr-split --dry-run` | Show split plan without creating branches |
| `/pr-split --auto` | Auto-split by file category (no manual grouping) |

---

## Steps

Execute IN ORDER. Stop at first failure.

### Step 1: Analyze Current Diff

// turbo

```bash
# If analyzing current branch
git diff --name-only origin/<target>..HEAD
git diff --stat origin/<target>..HEAD

# If analyzing an existing PR
gh pr diff <number> --repo <owner/repo> --name-only
gh pr view <number> --repo <owner/repo> --json additions,deletions,changedFiles
```

Classify the PR size per pr-toolkit size matrix.
- If XS/S/M → **STOP**: "PR is already reviewable ({size} — {files} files, {loc} LOC). Splitting not recommended."
- If L/XL → proceed with split analysis

### Step 2: Categorize Changed Files

// turbo

Group all changed files by concern category (per pr-toolkit split categories):

```markdown
## Split Analysis: {files} files, +{additions}/-{deletions}

### Feature Code ({count} files)
- src/components/Button.tsx
- src/hooks/useAuth.ts

### Tests ({count} files)
- tests/Button.test.tsx
- tests/useAuth.test.ts

### Configuration ({count} files)
- .agent/manifest.json
- .eslintrc.js

### Dependencies ({count} files)
- package.json
- package-lock.json

### Documentation ({count} files)
- README.md
- docs/api.md
```

### Step 3: Propose Split Plan

// turbo

Generate a split plan with merge ordering:

```markdown
## Proposed Split Plan

| # | Sub-PR | Branch Name | Files | Type | Depends On |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Update dependencies | split/{original}-deps | 2 | chore(deps) | — |
| 2 | Update configuration | split/{original}-config | 3 | chore | — |
| 3 | Implement feature | split/{original}-feat | 8 | feat | #1, #2 |
| 4 | Add tests | split/{original}-tests | 4 | test | #3 |
| 5 | Update documentation | split/{original}-docs | 3 | docs | #3 |

**Merge Order**: 1 → 2 → 3 → 4 → 5
```

If `--dry-run` → display plan and **STOP**.

Present plan to user for approval before proceeding.

### Step 4: Create Sub-Branches

For each sub-PR in the approved plan:

```bash
# Create sub-branch from target
git checkout <target>
git pull origin <target>
git checkout -b split/<original>-<category>

# Cherry-pick or selectively checkout files from original branch
git checkout <original-branch> -- <file1> <file2> <file3>
git commit -m "<type>(<scope>): <description>

Split from: <original-branch>
Part N of M in split series"
```

### Step 5: Verify Each Sub-Branch

// turbo

For each sub-branch, run the verification pipeline:

```bash
git checkout split/<original>-<category>

# Run /review pipeline (scope-filtered)
# lint → type-check → tests → security → build
```

- If any sub-branch fails verification → fix issues before proceeding
- Each sub-PR must be independently buildable and testable

### Step 6: Create Sub-PRs

For each verified sub-branch:

```bash
git push origin split/<original>-<category>

gh pr create \
  --base <target> \
  --head split/<original>-<category> \
  --title "<type>(<scope>): <description>" \
  --body "## Summary
Split from #{original-pr} — Part {N} of {M}

## Changes
{categorized change list}

## Dependencies
{Depends-On: #prev if applicable}

## Context
This PR is part of a split series. See #{original-pr} for full context.
Merge order: {1 → 2 → 3 → ...}"
```

### Step 7: Update Original PR

Post a comment on the original PR linking all sub-PRs:

```bash
gh pr comment <original-number> --repo <owner/repo> --body "## PR Split Complete

This PR has been split into {M} focused sub-PRs:

| # | Sub-PR | Status |
| :--- | :--- | :--- |
| 1 | #{sub-pr-1} — {title} | Open |
| 2 | #{sub-pr-2} — {title} | Open |
| ... | ... | ... |

**Merge order**: #1 → #2 → #3 → ...

This PR can be closed after all sub-PRs are merged."
```

---

## Output Template

### Split Complete

```markdown
## PR Split Complete

| Field | Value |
| :--- | :--- |
| Original PR | #{number} — {title} |
| Sub-PRs Created | {count} |
| Total Files | {original files} → {avg per sub-PR} per sub-PR |
| Verification | All sub-PRs pass /review |

### Sub-PRs

| # | PR | Title | Size | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | #{n} | {title} | {size} | Created |

**Next**: Review and merge sub-PRs in order: #1 → #2 → ...
```

---

## Governance

**PROHIBITED:**
- Deleting or force-pushing the original branch
- Creating sub-PRs that cannot independently build/test
- Splitting into sub-PRs that have circular dependencies
- Proceeding without user approval of the split plan
- Using `// turbo` on branch creation or PR creation steps

**REQUIRED:**
- Full diff analysis before proposing split
- User approval of split plan before creating branches
- Each sub-PR independently passes `/review`
- Dependency ordering declared in sub-PR bodies
- Original PR updated with links to all sub-PRs
- Merge order explicitly documented

---

## Completion Criteria

- [ ] Original PR analyzed and size classified (L/XL)
- [ ] Files categorized by concern
- [ ] Split plan generated with merge ordering
- [ ] Split plan approved by user
- [ ] Sub-branches created with selective commits
- [ ] Each sub-branch passes `/review` independently
- [ ] Sub-PRs created with structured bodies and dependency declarations
- [ ] Original PR updated with sub-PR links and merge order

---

## Related Resources

- **Skill**: `.agent/skills/pr-toolkit/SKILL.md` — split categories (section 11), size classification (section 2)
- **Previous**: `/pr` (PR creation triggered XL warning)
- **Next**: `/pr-review` (review each sub-PR) · `/pr-merge` (merge in dependency order)
- **Related**: `/pr-fix` (fix review findings on sub-PRs)
