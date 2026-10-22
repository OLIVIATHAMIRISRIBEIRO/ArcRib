---
description: Fix pull request issues based on review comments
---

# /pr-fix Command

Fix PR issues by fetching review comments, prioritizing by severity, implementing fixes, and pushing resolution.

## Usage

```
/pr-fix <url>                      # Fix PR at GitHub URL
/pr-fix <owner/repo>#<number>      # Fix PR by repo and number
/pr-fix #<number>                  # Fix PR in current repo
/pr-fix #<number> --critical-only  # Fix only CRITICAL findings
/pr-fix #<number> --dry-run        # Show fix plan without implementing
```

## Examples

```
/pr-fix https://github.com/org/repo/pull/42
/pr-fix deelmarkt/app#10
/pr-fix #5
/pr-fix #5 --critical-only
/pr-fix #5 --dry-run
```

## What It Does

1. Fetches all review comments and requested changes
2. Categorizes fixes by severity (P0-P3)
3. Checks out the PR branch
4. Implements fixes in priority order
5. Runs `/review` verification pipeline
6. Pushes fixes and posts resolution summary
7. Re-requests review from original reviewer

## Related

- `/pr-review` — Review a pull request
- `/pr` — Create a pull request
- `/pr-merge` — Merge with dependency validation
- `/pr-status` — Check merge readiness
- `/review` — Local code quality gates
