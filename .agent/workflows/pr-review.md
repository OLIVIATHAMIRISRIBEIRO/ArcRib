---
description: Review pull requests with Senior Staff Engineer expertise. Multi-perspective analysis covering PR hygiene, branch strategy, code quality, security, testing, and architecture. Engages with existing reviewer comments (bots and humans) and tracks review rounds.
version: 1.1.0
sdlc-phase: verify
skills: [pr-toolkit, verification-loop]
commit-types: []
---

# /pr-review — Pull Request Review Workflow

> **Trigger**: `/pr-review <url>` · `/pr-review <owner/repo>#<number>` · `/pr-review #<number>`
> **Lifecycle**: Verify — peer review before merge, independent of local development

> [!CAUTION]
> This workflow posts reviews to GitHub that are visible to the entire team. Ensure findings are accurate, constructive, and properly prioritized before submitting. Every review reflects engineering standards.

> [!TIP]
> This workflow leverages the **pr-toolkit** skill for review patterns and the **pr-reviewer** agent for multi-perspective analysis. Read `.agent/skills/pr-toolkit/SKILL.md` for review framework details.

---

## Critical Rules

0. **NO ARTIFACT FILES** — NEVER save API responses, diffs, review bodies, or intermediate data as files in the project directory. Process ALL data in memory via shell pipes, variables, or direct tool output. Files like `pr-17.json`, `pr-17.diff`, `pr-17-review.md`, `pr-17-comments.json` MUST NOT be created. If a command output is too large, use `head`/`tail` to truncate — do NOT redirect to a file
1. **ALWAYS** fetch the full PR diff before reviewing — never review from title/description alone
2. **ALWAYS** detect the project's branch strategy before assessing target branch compliance
3. **ALWAYS** include a concrete fix suggestion for every finding — no criticism without remedy
4. **NEVER** post a review with only NITs — if everything is clean, APPROVE explicitly
5. **NEVER** approve a PR with known CRITICAL findings — no social-pressure approvals
6. **EVIDENCE MANDATE** — every finding MUST include a `file:line` reference. Findings without file:line evidence are REJECTED and must not appear in the review output. Generic statements like "code quality is good" are not findings — cite specific locations or omit
7. **EXISTING COMMENT ENGAGEMENT** — analyze ALL existing reviews AND inline comments from all reviewers (including bots like Gemini Code Assist, CodeRabbit, Copilot, SonarCloud, etc.). Reference and respond to their findings — acknowledge valid points, challenge incorrect ones, and avoid duplicating already-flagged issues
8. **REVIEW ROUND AWARENESS** — detect whether this is a first review or a follow-up round. For follow-up rounds, track which previous findings were addressed and which remain open. Reference the prior review explicitly
9. **OUTPUT IDENTITY** — the review title MUST follow the format `PR #{number} Review — {content-specific summary}`. NEVER use agent branding, "Antigravity", or generic titles. The title must reflect the PR's actual content

---

## Argument Parsing

| Command | Action |
| :--- | :--- |
| `/pr-review <url>` | Review PR at the given GitHub URL |
| `/pr-review <owner/repo>#<number>` | Review PR by owner/repo and number |
| `/pr-review #<number>` | Review PR in current repo by number |
| `/pr-review #<number> --post` | Review and post to GitHub (default) |
| `/pr-review #<number> --local` | Review locally only — do not post to GitHub |
| `/pr-review #<number> --focus security` | Focus review on security perspective only |
| `/pr-review #<number> --focus quality` | Focus review on code quality perspective only |

---

## Steps

Execute IN ORDER. Stop at first failure.

### Step 1: Parse PR Reference

// turbo

Parse the user-provided PR reference to extract:

- **Repository**: `owner/repo` (from URL or current repo via `gh repo view --json nameWithOwner`)
- **PR Number**: extracted from URL path or `#N` argument

```bash
# If URL provided, extract owner/repo and number from URL path
# If #N provided, get current repo
gh repo view --json nameWithOwner --jq .nameWithOwner
```

Validate the PR exists and is open:

```bash
gh pr view <number> --repo <owner/repo> --json state,title --jq '.state'
```

- If PR not found → **STOP** with error: "PR not found"
- If PR is closed/merged → **WARN**: "PR is already {state} — review will be informational only"

### Step 2: Fetch PR Data & Existing Reviewer Comments

Retrieve comprehensive PR metadata AND all existing reviewer feedback:

```bash
# PR metadata
gh pr view <number> --repo <owner/repo> \
  --json title,body,state,baseRefName,headRefName,author,files,additions,deletions,changedFiles,commits,labels,url,reviews,reviewRequests

# PR diff
gh pr diff <number> --repo <owner/repo>

# Existing review verdicts (APPROVE, REQUEST_CHANGES, COMMENT)
gh api repos/<owner>/<repo>/pulls/<number>/reviews

# Existing inline review comments (where bots like Gemini, CodeRabbit post findings)
gh api repos/<owner>/<repo>/pulls/<number>/comments

# General PR conversation comments
gh api repos/<owner>/<repo>/issues/<number>/comments

# CI status
gh pr checks <number> --repo <owner/repo>
```

Extract and document:

- Title, author, branch direction (head → base)
- File count, additions, deletions
- Existing reviews and their verdicts
- CI check results
- **All existing inline comments** — organized by reviewer (human vs. bot)
- **All general PR comments** — including bot analysis summaries

### Step 3: Detect Review Round & Analyze Existing Comments

**3a. Review Round Detection**

Determine if this is a first review or a follow-up round:

```bash
# Count existing reviews from this reviewer or similar agents
gh api repos/<owner>/<repo>/pulls/<number>/reviews \
  --jq '[.[] | select(.state != "DISMISSED")] | length'
```

| Condition | Round | Behavior |
| :--- | :--- | :--- |
| Zero prior substantive reviews | **Round 1** | Full review — no prior context to reference |
| 1+ prior reviews exist | **Round N+1** | Track addressed/unaddressed items from prior rounds |

For Round N+1:
- Parse previous review findings into a checklist
- Cross-reference with current diff to identify which findings were addressed
- Open the review with: "Follow-up review (Round {N}). {X} of {Y} previous findings addressed."
- Flag any unaddressed CRITICAL/HIGH findings as **still open**

**3b. Existing Reviewer Comment Analysis**

Analyze ALL existing inline comments and review comments from all reviewers (bots and humans):

For each existing comment:
1. **Identify the reviewer** — human, Gemini Code Assist, CodeRabbit, Copilot, SonarCloud, or other bot
2. **Classify the finding** — CRITICAL / HIGH / MEDIUM / LOW / NIT / suggestion
3. **Assess validity** — is the finding correct? Does it apply to this codebase context?
4. **Determine response** — agree, partially agree, disagree, or note as already-addressed

Build a **Prior Findings Ledger**:

| # | Reviewer | File:Line | Finding | Valid? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | gemini-code-assist | `skills/README.md:28` | Operational Skills count wrong (5→7) | Yes | Open |
| 2 | gemini-code-assist | `skills/README.md:96` | pr-toolkit categorization inconsistency | Yes | Open |
| ... | ... | ... | ... | ... | ... |

**Engagement Rules:**
- **Valid finding, still open** → Reference it: "Agree with @gemini-code-assist — {finding}. Additionally, {your analysis}."
- **Valid finding, already addressed** → Acknowledge: "{finding} from @{reviewer} has been resolved in commit {sha}."
- **Invalid or incorrect finding** → Challenge constructively: "Respectfully disagree with @{reviewer} on {finding} because {reason with evidence}."
- **Duplicate of your own finding** → Skip yours, reference theirs: "As @{reviewer} already flagged, {finding}."
- **Finding you missed** → Acknowledge and amplify: "@{reviewer} correctly identified {finding}. This is {severity} because {impact}."

### Step 4: Analyze PR Hygiene

// turbo

Apply PR Hygiene perspective from pr-toolkit:

**4a. Title Format Validation**
- Check conventional commits format: `type(scope): description`
- Verify type is valid: feat, fix, docs, style, refactor, test, chore, perf, ci
- Verify description is imperative mood, under 72 characters

**4b. Body Completeness**
- Check for required sections: Summary, Changes, Test Plan
- Check for Breaking Changes section (if applicable)
- Check for Related Issues references

**4c. PR Size Classification**
- Classify as XS/S/M/L/XL per pr-toolkit size matrix
- If XL (50+ files or 1500+ LOC) → finding: CRITICAL — recommend splitting
- **Exception**: Automated vendor upgrades (e.g., framework kit upgrades) where large diffs are expected and acceptable. Note the exception explicitly in the finding.

**4d. Scope Coherence**
- Analyze changed file paths for unrelated concerns
- Detect mixed feature + tooling, mixed feature + dependency upgrades
- If scope violation detected → finding: HIGH — recommend focused PRs

### Step 5: Analyze Branch Strategy

// turbo

**5a. Detect Branch Strategy**
- Check for `dev`/`develop` remote branch existence
- Classify as GitFlow or Trunk-Based

**5b. Validate Target Branch**
- Apply target validation rules from pr-toolkit
- GitFlow: `feature/*` → `dev` (not `main`)
- Trunk-Based: any → `main`
- If invalid target → finding: CRITICAL — wrong base branch

**5c. Branch Naming**
- Verify branch follows naming convention: `type/[ticket-]description`
- If non-standard naming → finding: LOW

### Step 6: Multi-Perspective Code Review

Read each changed file in the PR diff. For EVERY finding, you MUST include:
- **File path and line number** (`path/to/file.ext:line`)
- **The actual code** (quote the relevant line or block from the diff)
- **Why it matters** (impact explanation, not just "this is bad")
- **Concrete fix** (exact code change, command, or config adjustment)

Findings without `file:line` evidence are automatically rejected and MUST NOT appear in the output.

**Cross-file consistency**: Check that counts, references, and categorizations are consistent across related files (e.g., if `README.md` says "5 skills" but the directory contains 7, that is a finding).

**6a. Code Quality Review**

For each changed file, check:
- Function size (> 50 lines → HIGH — cite `file:line` of the function declaration)
- File size (> 800 lines → HIGH — cite the file and total line count)
- Nesting depth (> 4 levels → HIGH — cite `file:line` of the deepest nesting)
- Error handling (missing try/catch → MEDIUM — cite `file:line` of unprotected call)
- Debug artifacts (console.log, debugger → MEDIUM — cite `file:line` of each occurrence)
- Naming quality (single-letter vars, generic names → LOW — cite `file:line` and suggest rename)
- Immutability patterns (mutation → MEDIUM — cite `file:line` and show immutable alternative)

**6b. Security Review**

For each changed file, check:
- Hardcoded secrets (API keys, passwords, tokens → CRITICAL — cite `file:line`)
- Input validation (missing validation on user input → HIGH — cite `file:line` of handler)
- Injection risks (string concatenation in queries → CRITICAL — cite `file:line`)
- XSS vectors (unescaped user content in HTML → CRITICAL — cite `file:line`)
- Auth/authz (missing guards on protected resources → HIGH — cite `file:line`)
- Sensitive data exposure (PII in logs → HIGH — cite `file:line`)

**6c. Testing Review**

Check the PR diff for:
- New functions/components without corresponding tests → HIGH (cite `file:line` of untested code)
- Test file changes that reduce coverage → MEDIUM (cite before/after coverage if available)
- Flaky test patterns (timeouts, sleep, race conditions) → MEDIUM (cite `file:line`)
- Missing edge case coverage → LOW (cite `file:line` and describe missing case)

**6d. Architecture Review**

Assess structural changes:
- Pattern consistency with existing codebase → MEDIUM (cite `file:line` and existing pattern location)
- Separation of concerns violations → HIGH (cite `file:line`)
- Circular dependency introduction → HIGH (cite both files involved)
- Over-engineering / premature abstraction → MEDIUM (cite `file:line`)
- API design consistency → MEDIUM (cite `file:line` and existing convention)

### Step 7: Generate Review Report

Compile all findings into the structured review format:

1. **Title**: `PR #{number} Review — {2-5 word content summary}` (e.g., "PR #17 Review — Agent Kit Upgrade v3.9.0")
2. **Review round indicator**: "Round {N}" with prior findings tracker (if Round 2+)
3. **Existing reviewer analysis**: Summary of engagement with Gemini/CodeRabbit/human comments
4. **Group findings by severity** (CRITICAL → HIGH → MEDIUM → LOW → NIT) — NOT by perspective. Severity-first grouping is MANDATORY
5. **What's Good section**: List 3+ specific positive observations about the PR (clean patterns, good test coverage, proper error handling, etc.). Every review MUST include this section. Be specific — cite file paths
6. Calculate verdict per decision table
7. Generate assessment summary with per-perspective status
8. Format inline comments for GitHub posting

### Step 8: Post Review to GitHub

**Skip this step if `--local` flag was used.**

Post the review using the `gh` CLI:

```bash
# Post review with verdict
gh pr review <number> --repo <owner/repo> \
  --{approve|request-changes|comment} \
  --body "<review body>"
```

For inline findings, post as review comments:

```bash
gh api repos/<owner>/<repo>/pulls/<number>/comments \
  --method POST \
  -f body="<finding detail>" \
  -f commit_id="<latest commit sha>" \
  -f path="<file path>" \
  -F line=<line number> \
  -f side="RIGHT"
```

- If posting fails → display review locally as fallback
- If GitHub API rate-limited → wait and retry once, then fallback to local display
- Confirm review was posted successfully

---

## Output Template

### Review Complete

```markdown
## PR #{number} Review — {content-specific summary}

{Round N indicator, if applicable: "Follow-up review (Round N). X of Y previous findings addressed."}

| Field | Value |
| :--- | :--- |
| PR | #{number} — {title} |
| Branch | {head} → {base} |
| Size | {label} ({files} files, +{additions}/-{deletions}) |
| Review Round | {Round 1 / Round N — X of Y prior findings addressed} |
| Verdict | {APPROVE / REQUEST_CHANGES / COMMENT} |

### Existing Reviewer Comments

{Summary of engagement with other reviewers' comments. For each reviewer:}

| Reviewer | Comments | Agreed | Challenged | Already Addressed |
| :--- | :--- | :--- | :--- | :--- |
| @gemini-code-assist | {count} | {count} | {count} | {count} |
| @{human-reviewer} | {count} | {count} | {count} | {count} |

{If no existing comments: "No prior reviewer comments found."}

### Assessment Summary

| Perspective | Status | Findings |
| :--- | :--- | :--- |
| PR Hygiene | {status} | {count} issues |
| Branch Strategy | {status} | {count} issues |
| Code Quality | {status} | {count} issues |
| Security | {status} | {count} issues |
| Testing | {status} | {count} issues |
| Architecture | {status} | {count} issues |

**Findings**: {critical} Critical, {high} High, {medium} Medium, {low} Low

### Must Fix

{N. finding title — file:line reference}
{description with code quote, impact, and concrete fix}

### High

{numbered findings with file:line, each with Fix suggestion}

### Medium

{numbered findings with file:line, each with Fix suggestion}

### Low / NIT

{numbered findings with file:line}

### What's Good

{3+ specific positive observations with file paths. Examples:}
- {Clean error handling pattern in `src/auth/handler.ts` — proper try/catch with user-friendly messages}
- {Test coverage for edge cases in `tests/payment.test.ts` — null input, expired tokens, rate limits all covered}
- {Consistent naming conventions across all new files in `src/services/`}

## Verdict: {REQUEST_CHANGES | APPROVE | COMMENT}

{justification — 1-2 sentences referencing specific findings}

**Review posted**: {Yes — link / No — local only}
```

### Review Failed

```markdown
## PR Review Failed at Step {N}

### Error
{error description}

### Resolution
1. {fix steps}
2. Re-run: `/pr-review <reference>`
```

---

## Governance

**PROHIBITED:**
- Approving PRs with known CRITICAL findings
- Posting reviews without reading the full diff
- Making findings without `file:line` evidence — every finding MUST cite a specific location
- Reviewing without detecting the branch strategy first
- Social-pressure approvals ("LGTM" without analysis)
- Posting duplicate reviews (check existing reviews first)
- Ignoring existing reviewer comments (bots or humans) — every existing comment must be acknowledged
- Using agent branding ("Antigravity", "Tier-1", "Upgrade Protocol") in review titles — use PR-specific content summaries
- Producing generic observations without evidence ("code quality is good", "changes are clean") — cite specific files/lines or omit
- Grouping findings by perspective instead of severity — severity-first ordering is mandatory

**REQUIRED:**
- Full diff analysis before any verdict
- Concrete fix suggestion for every finding
- Severity-prioritized findings (CRITICAL first, then HIGH, then MEDIUM, then LOW/NIT)
- Branch strategy detection before target validation
- Evidence-based findings with `file:line` references for EVERY finding
- Constructive tone — teach, don't criticize
- "What's Good" section with 3+ specific positive observations
- Engagement with all existing reviewer comments (agree, challenge, or acknowledge)
- Review round tracking for follow-up reviews
- Cross-file consistency checking (counts, references, categorizations match across files)
- Content-specific review title that reflects the PR's actual changes

---

## Completion Criteria

- [ ] PR reference parsed and validated
- [ ] Full PR data fetched (metadata, diff, reviews, CI)
- [ ] Existing inline comments and review comments fetched from ALL reviewers
- [ ] Review round detected (Round 1 vs. Round N+1)
- [ ] Existing reviewer comments analyzed and engagement planned (agree/challenge/acknowledge)
- [ ] PR hygiene assessed (title, body, size, scope)
- [ ] Branch strategy detected and target validated
- [ ] Code quality, security, testing, architecture reviewed with file:line evidence
- [ ] Cross-file consistency verified (counts, references, categorizations)
- [ ] Findings compiled by SEVERITY (not perspective) with fix suggestions
- [ ] "What's Good" section populated with 3+ specific positive observations
- [ ] Existing reviewer comments referenced in review body
- [ ] Verdict rendered per decision table
- [ ] Review posted to GitHub (unless `--local`)

---

## Related Resources

- **Skill**: `.agent/skills/pr-toolkit/SKILL.md` — review patterns, severity levels, size classification
- **Agent**: `.agent/agents/pr-reviewer.md` — Senior Staff Engineer review specialist
- **Related**: `/pr` (create PRs) · `/pr-fix` (fix review findings) · `/review` (local quality gates)
- **Rule**: `.agent/rules/git-workflow.md` — branching and commit conventions
