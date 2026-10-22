# Git Workflow Rules

> **Priority**: HIGH — Enforced by hooks

> [!CAUTION]
> **PUSH POLICY**: NEVER push commits during implementation or task work.
> Commits are **local-only** until the user explicitly requests the **session-end protocol**.
> The pre-push hook runs the full LOCAL-CI-GATE (lint, type-check, tests, build) which takes 60-160 seconds.
> Premature pushes waste time and block the agent. Only push once, at session end, after all work is verified.

## Commit Format

```
type(scope): description

[optional body]

[optional footer]
```

### Types

| Type       | Use                |
| :--------- | :----------------- |
| `feat`     | New feature        |
| `fix`      | Bug fix            |
| `docs`     | Documentation      |
| `refactor` | Code restructuring |
| `test`     | Test additions     |
| `chore`    | Maintenance        |

## Branch Naming

- `feature/` — New features
- `fix/` — Bug fixes
- `refactor/` — Code improvements

## Before Commit

- [ ] All tests pass
- [ ] Lint passes
- [ ] Build succeeds
- [ ] No secrets in code

## Pull Requests

- **REQUIRE** code review
- **INCLUDE** test coverage
- **LINK** to issue/ticket
