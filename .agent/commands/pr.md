---
description: Create production-grade pull requests with branch validation, size guards, and CI verification
---

# /pr Command

Create pull requests with branch strategy validation, size/scope guards, pre-flight checks, and CI verification.

## Usage

```
/pr                    # Create PR targeting default branch
/pr [target]           # Create PR targeting specific branch (e.g., /pr dev)
/pr --draft            # Create PR as draft
/pr --draft [target]   # Create draft PR targeting specific branch
```

## Examples

```
/pr                    # Auto-detects target via branch strategy
/pr dev                # Target dev branch explicitly
/pr --draft            # Create draft PR
/pr main               # Target main (validated against strategy)
```

## What It Does

1. Detects branch strategy (GitFlow / Trunk-Based) and validates target
2. Syncs with target branch and resolves conflicts
3. Checks PR size (XS-XL) and scope coherence
4. Runs pre-flight `/review` pipeline (lint, types, tests, security, build)
5. Generates conventional commit title from branch name
6. Creates PR with structured body (Summary, Changes, Test Plan)
7. Monitors CI pipeline status

## PR Toolkit

| Command | Purpose |
| :--- | :--- |
| `/pr` | Create a pull request |
| `/pr-review #N` | Review an existing PR |
| `/pr-fix #N` | Fix PR based on review comments |
| `/pr-merge #N` | Merge PR safely with validation |
| `/pr-split` | Split oversized PR into sub-PRs |
| `/pr-status` | Triage PRs with merge readiness |
| `/pr-describe` | Auto-generate PR description |

## Related

- `/pr-review` — Review a pull request
- `/pr-fix` — Fix issues from review comments
- `/pr-merge` — Merge with dependency validation
- `/pr-split` — Split oversized PRs
- `/pr-status` — Check merge readiness
- `/pr-describe` — Auto-generate description
- `/review` — Local code quality gates
- `/preflight` — Production readiness check
