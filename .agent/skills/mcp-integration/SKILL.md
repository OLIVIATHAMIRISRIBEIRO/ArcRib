---
name: mcp-integration
description: Model Context Protocol (MCP) integration patterns for extending AI capabilities with external tools and data sources.
version: 1.0.0
triggers: [mcp, tool, server, protocol, integration, external]
---

# MCP Integration Skill

> **Purpose**: Guide the integration and effective use of Model Context Protocol (MCP) servers to extend AI agent capabilities with external tools, data sources, and services.

---

## Overview

The Model Context Protocol (MCP) is an open standard that connects AI systems with external tools and data sources through a unified interface. MCP servers act as capability providers — each server exposes a set of tools that the AI can invoke to perform actions beyond its native abilities.

This skill ensures that MCP integrations follow Trust-Grade principles: secure, reliable, and properly governed.

---

## Core Concepts

### MCP Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│    AI Agent      │────▶│   MCP Client     │────▶│   MCP Server    │
│  (LLM + Kit)    │◀────│  (IDE/Runtime)   │◀────│  (Tool Provider)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                                                    ┌────┴────┐
                                                    │ External │
                                                    │ Service  │
                                                    └─────────┘
```

### Key Components

| Component | Role | Example |
|:----------|:-----|:--------|
| **MCP Server** | Exposes tools via protocol | GitHub MCP, GitKraken MCP, Database MCP |
| **MCP Client** | Connects AI to servers | VS Code extension, Cursor, IDE runtime |
| **Tools** | Individual capabilities | `create_issue`, `git_commit`, `run_query` |
| **Resources** | Data endpoints | File contents, database schemas, API docs |
| **Prompts** | Reusable templates | Code review template, deployment checklist |

---

## Integration Patterns

### Pattern 1: Git Operations via MCP

**When to use**: Git operations that benefit from structured API access rather than raw CLI commands.

**Available servers**: GitKraken MCP, GitHub MCP

```
Preferred for:
- Creating branches, commits, PRs (structured data)
- Reading git status, blame, diff (parsed output)
- Managing issues and reviews (API access)

Still use CLI for:
- Complex git operations (rebase, cherry-pick)
- Local-only operations (stash, worktree)
- Performance-critical batch operations
```

### Pattern 2: Issue and Project Management

**When to use**: Creating, updating, and querying issues across platforms.

```
GitHub MCP Server provides:
- issue_write (create/update issues)
- issue_read (get details, comments, labels)
- search_issues (query with GitHub syntax)
- list_issues (paginated browsing)

Best practices:
- Use search_* for targeted queries with criteria
- Use list_* for broad retrieval with pagination
- Batch reads in groups of 5-10 items
```

### Pattern 3: Code Search and Analysis

**When to use**: Finding code patterns across repositories.

```
GitHub MCP provides:
- search_code (cross-repo code search)
- get_file_contents (read specific files)
- get_commit (commit details with diff)

Usage guidance:
- Use search_code for finding symbols, functions, patterns
- Use get_file_contents for reading specific known files
- Combine with local grep_search for current workspace
```

### Pattern 4: Pull Request Workflow

**When to use**: Full PR lifecycle management.

```
Workflow:
1. create_branch → Create feature branch
2. push_files → Push code changes
3. create_pull_request → Open PR
4. request_copilot_review → Automated review
5. pull_request_read(get_status) → Check CI status
6. merge_pull_request → Merge when ready

Trust-Grade rules:
- Always create PR (never push directly to main)
- Always request review before merge
- Always check CI status before merge
```

---

## Security Guidelines

### Authentication

- MCP servers use token-based authentication
- Tokens are managed by the IDE/runtime, never by the AI agent
- Never log, display, or store authentication tokens
- Verify server identity before sending sensitive operations

### Permission Model

| Operation Type | Risk Level | Verification Required |
|:---------------|:-----------|:---------------------|
| Read (list, get, search) | Low | None |
| Create (new issue, branch, file) | Medium | Confirm with user |
| Modify (update, edit) | Medium | Confirm with user |
| Delete (remove file, close issue) | High | Explicit user approval |
| Deploy (merge, publish) | Critical | Double confirmation |

### Data Handling

- Never pass secrets through MCP tool parameters
- Sanitize user data before including in tool calls
- Respect repository visibility (public vs private)
- Log operations for audit trail (session-context.md)

---

## Server Selection Guide

| Task | Recommended Server | Why |
|:-----|:-------------------|:----|
| Git operations (commit, branch, status) | GitKraken MCP | Richer git-specific tools |
| GitHub issues and PRs | GitHub MCP | Native GitHub API access |
| Code review and analysis | GitHub MCP | PR review tools |
| Repository management | GitHub MCP | Repo CRUD operations |
| Complex git workflows | GitKraken MCP | Worktree, stash, blame |

---

## Error Handling

### Common MCP Errors

| Error | Cause | Resolution |
|:------|:------|:-----------|
| `ENEEDAUTH` | Token expired/missing | Re-authenticate via IDE settings |
| `403 Forbidden` | Insufficient permissions | Check token scopes |
| `404 Not Found` | Resource doesn't exist | Verify owner/repo/branch names |
| `422 Unprocessable` | Invalid parameters | Check required fields and formats |
| `Rate Limited` | Too many requests | Implement exponential backoff |

### Fallback Strategy

When an MCP server is unavailable:
1. Log the failure in session context
2. Fall back to CLI equivalent if available
3. Notify user of degraded capability
4. Continue with remaining available tools

---

## Integration with Antigravity AI Kit

### Loading Rules Integration

MCP capabilities are registered in `engine/loading-rules.json` under domain rules:

```json
{
  "domain": "git-operations",
  "keywords": ["git", "commit", "branch", "pr", "merge"],
  "loadAgents": ["devops-engineer"],
  "loadSkills": ["git-workflow", "mcp-integration"],
  "mcpServers": ["GitKraken", "github-mcp-server"]
}
```

### Session Context Tracking

Log MCP operations in session context for continuity:

```markdown
## MCP Operations This Session
- Created branch `feature/auth` via GitKraken MCP
- Opened PR #42 via GitHub MCP
- Requested Copilot review via GitHub MCP
```

### Workflow State Integration

MCP operations map to workflow phases:

| Phase | MCP Operations |
|:------|:--------------|
| EXPLORE | `search_code`, `get_file_contents`, `list_issues` |
| PLAN | `issue_write` (create tracking issue) |
| IMPLEMENT | `create_branch`, `push_files` |
| VERIFY | `pull_request_read(get_status)` |
| REVIEW | `request_copilot_review`, `pull_request_review_write` |
| DEPLOY | `merge_pull_request` |
