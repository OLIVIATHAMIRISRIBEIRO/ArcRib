---
description: Merge a pull request safely with dependency validation and post-merge checks
---

# /pr-merge Command

Safely merge a pull request after validating CI status, review approval, dependency chain, and branch strategy compliance. Includes post-merge verification and dependent PR notification.

## Usage

```
/pr-merge #<number>                 # Merge PR in current repo
/pr-merge <url>                     # Merge PR at GitHub URL
/pr-merge #<number> --squash        # Force squash merge
/pr-merge #<number> --merge-commit  # Force merge commit
/pr-merge #<number> --rebase        # Force rebase merge
/pr-merge #<number> --dry-run       # Validate merge readiness without merging
```

## Examples

```
/pr-merge #42                       # Merge with auto-detected strategy
/pr-merge #42 --squash              # Squash merge
/pr-merge #42 --dry-run             # Check if #42 is ready to merge
/pr-merge https://github.com/org/repo/pull/42
```

## What It Does

1. Validates PR state (open, mergeable, not blocked)
2. Verifies review approval and CI checks passing
3. Validates dependency chain (`Depends-On:` PRs all merged)
4. Checks branch strategy compliance (correct merge target)
5. Selects merge strategy (squash / merge commit / rebase)
6. Executes merge and deletes merged branch
7. Runs post-merge validation (CI on target branch)
8. Notifies dependent PRs that this dependency is resolved

## Related

- `/pr` — Create a pull request
- `/pr-review` — Review a pull request
- `/pr-status` — Check merge readiness
- `/pr-split` — Split oversized PR into sub-PRs
