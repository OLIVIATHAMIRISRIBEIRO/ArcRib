---
description: Split oversized PRs into focused sub-PRs by concern category
---

# /pr-split Command

Split large (L/XL) pull requests into focused, independently-reviewable sub-PRs organized by concern category with a dependency-ordered merge plan.

## Usage

```
/pr-split                           # Analyze current branch for splitting
/pr-split #<number>                 # Analyze existing PR for splitting
/pr-split --dry-run                 # Show split plan without creating branches
/pr-split --auto                    # Auto-split by file category
```

## Examples

```
/pr-split                           # Split current branch
/pr-split #42                       # Split PR #42
/pr-split --dry-run                 # Preview split plan only
/pr-split #42 --auto                # Auto-split without manual grouping
```

## What It Does

1. Analyzes full diff and classifies PR size (must be L or XL)
2. Categorizes files by concern (feature, tests, config, deps, docs, infra)
3. Proposes split plan with merge ordering and dependencies
4. Waits for user approval of the split plan
5. Creates sub-branches with selective cherry-pick/checkout
6. Verifies each sub-branch independently (build + tests)
7. Creates sub-PRs with structured bodies and dependency declarations
8. Updates original PR with links to all sub-PRs

## Split Categories

| Category | Examples |
| :--- | :--- |
| Feature Code | `src/`, application logic |
| Tests | `tests/`, `*.test.*`, `*.spec.*` |
| Configuration | `.eslintrc`, `tsconfig`, tool configs |
| Dependencies | `package.json`, lock files |
| Documentation | `README`, `docs/`, `CHANGELOG` |
| Infrastructure | `Dockerfile`, CI/CD, deploy configs |

## Related

- `/pr` — Create a pull request (warns on XL size)
- `/pr-review` — Review each sub-PR
- `/pr-merge` — Merge sub-PRs in dependency order
- `/pr-status` — Check status of all sub-PRs
