---
description: Triage pull requests with CI status, staleness detection, and dependency readiness
---

# /pr-status Command

Quick triage view for one or more pull requests — CI status, review state, staleness, dependency readiness, and merge eligibility at a glance.

## Usage

```
/pr-status                          # All open PRs in current repo
/pr-status #<number>                # Single PR status
/pr-status <url>                    # PR at GitHub URL
/pr-status <owner/repo>            # All open PRs in specified repo
/pr-status #<number> --deps         # Show dependency chain status
```

## Examples

```
/pr-status                          # Triage all open PRs
/pr-status #42                      # Status of PR #42
/pr-status https://github.com/org/repo/pull/10
/pr-status deelmarkt/app            # All open PRs in deelmarkt/app
/pr-status #42 --deps               # Dependency chain for PR #42
```

## What It Does

1. Fetches PR metadata (state, reviews, checks, labels)
2. Classifies CI status (passing / failing / pending / none)
3. Detects staleness (days since last update, sync status with target)
4. Validates dependency chain (`Depends-On:` references)
5. Calculates merge readiness score (0-100)
6. Outputs a triage dashboard with actionable next steps

## Output

```
PR #42 — feat(auth): add OAuth2 provider
├─ Status: OPEN
├─ Reviews: 1/1 APPROVED
├─ CI: ✓ All checks passing (3/3)
├─ Staleness: Fresh (updated 2h ago, in sync with main)
├─ Dependencies: #40 MERGED, #41 OPEN (blocking)
├─ Merge Ready: No — dependency #41 not yet merged
└─ Next: Merge #41 first, then this PR is ready
```

## Related

- `/pr` — Create a pull request
- `/pr-review` — Review a pull request
- `/pr-merge` — Merge a pull request safely
- `/pr-describe` — Auto-generate PR description
