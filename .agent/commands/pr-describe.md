---
description: Auto-generate PR title, summary, and labels from diff analysis
---

# /pr-describe Command

Automatically generate a conventional-commit title, structured summary, change categorization, and suggested labels by analyzing the PR diff.

## Usage

```
/pr-describe                        # Describe current branch diff
/pr-describe #<number>              # Describe existing PR
/pr-describe <url>                  # Describe PR at GitHub URL
/pr-describe #<number> --update     # Update existing PR description in-place
/pr-describe --format brief         # Short summary only
```

## Examples

```
/pr-describe                        # Generate description for current branch
/pr-describe #42                    # Generate description for PR #42
/pr-describe #42 --update           # Overwrite PR #42's description
/pr-describe --format brief         # One-paragraph summary
```

## What It Does

1. Analyzes the full diff (commits, file changes, additions/deletions)
2. Detects the primary change type (feat, fix, refactor, chore, etc.)
3. Generates conventional-commit title from branch name and diff content
4. Creates structured body (Summary, Changes by Category, Test Plan)
5. Suggests labels based on file types and change patterns
6. Optionally updates the PR description on GitHub

## Output

```markdown
## Generated PR Description

**Title**: feat(auth): add OAuth2 provider support

**Summary**:
Adds Google and GitHub OAuth2 providers with PKCE flow,
token refresh, and session management.

**Changes**:
- Feature: 4 files (OAuth provider, token service, session middleware, config)
- Tests: 3 files (unit + integration for OAuth flow)
- Config: 1 file (environment variables for provider credentials)

**Labels**: `feature`, `auth`, `needs-review`

**Test Plan**:
- [ ] OAuth login flow with Google provider
- [ ] Token refresh after expiry
- [ ] Session persistence across browser restart
```

## Related

- `/pr` — Create a pull request (uses /pr-describe internally)
- `/pr-review` — Review a pull request
- `/pr-status` — Check PR merge readiness
