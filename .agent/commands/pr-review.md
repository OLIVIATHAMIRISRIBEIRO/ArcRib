---
description: Review a pull request with Senior Staff Engineer expertise
---

# /pr-review Command

Review any pull request with multi-perspective analysis covering PR hygiene, branch strategy, code quality, security, testing, and architecture.

## Usage

```
/pr-review <url>                    # Review PR at GitHub URL
/pr-review <owner/repo>#<number>    # Review PR by repo and number
/pr-review #<number>                # Review PR in current repo
/pr-review #<number> --local        # Review locally only (don't post)
/pr-review #<number> --focus <area> # Focus on specific perspective
```

## Examples

```
/pr-review https://github.com/org/repo/pull/42
/pr-review deelmarkt/app#10
/pr-review #5
/pr-review #5 --local
/pr-review #5 --focus security
```

## Focus Areas

- `security` — Security-only review
- `quality` — Code quality-only review
- `hygiene` — PR structure and process compliance

## What It Does

1. Fetches PR metadata, diff, and existing reviews
2. Detects branch strategy (GitFlow / Trunk-Based)
3. Applies 6-perspective review framework
4. Generates findings with severity and fix suggestions
5. Posts review to GitHub (REQUEST_CHANGES / APPROVE / COMMENT)

## Related

- `/pr` — Create a pull request
- `/pr-fix` — Fix issues from review comments
- `/pr-merge` — Merge with dependency validation
- `/pr-split` — Split oversized PRs
- `/pr-status` — Check merge readiness
- `/review` — Local code quality gates
