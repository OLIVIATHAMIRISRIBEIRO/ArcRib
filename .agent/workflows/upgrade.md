---
description: Non-destructive Antigravity AI Kit framework upgrade with preservation verification.
version: 1.0.0
sdlc-phase: maintenance
skills: [verification-loop]
commit-types: [chore]
---

# /upgrade — Framework Upgrade

> **Trigger**: `/upgrade [sub-command]`
> **Lifecycle**: Maintenance — invoked when a new Antigravity AI Kit version is available

> [!CAUTION]
> Framework upgrades modify `.agent/` files on disk. The Preservation Contract
> (defined in `.agent/rules/agent-upgrade-policy.md`) protects user-specific state.
> Always verify integrity after upgrade. Never use `init --force` for routine upgrades.

> [!TIP]
> This workflow references the **agent-upgrade-policy** rule for the canonical list of
> protected files. Read `.agent/rules/agent-upgrade-policy.md` for the full Preservation Contract.

---

## Critical Rules

1. **Non-destructive only** — use `ag-kit update`, never `init --force` for routine upgrades
2. **Preservation Contract** — user-specific state (rules, checklists, sessions, decisions, contexts, identity) must survive upgrades
3. **Verify after upgrade** — always run `ag-kit verify` post-upgrade to confirm manifest integrity
4. **Rollback capability** — uncommitted upgrades can be reverted via `git checkout -- .agent/`
5. **Human confirmation** — the upgrade step requires explicit user approval before execution

---

## Scope Filter

| Change Type | Upgrade Applies? | Rationale |
| :---------- | :--------------- | :-------- |
| New kit version available | Yes | Core use case |
| User wants to refresh `.agent/` | Yes | Non-destructive merge |
| First-time setup | No | Use `npx antigravity-ai-kit init` instead |
| Catastrophic repair | No | Use `init --force` (destructive — last resort) |

---

## Argument Parsing

| Command | Action |
| :----------------------- | :----------------------------------------------- |
| `/upgrade` | Interactive upgrade — detect, preview, apply, verify |
| `/upgrade --dry-run` | Preview changes without applying |
| `/upgrade --verify-only` | Run post-upgrade verification checks only |

---

## Steps

// turbo
1. **Pre-Upgrade Assessment**
   - Check current kit version: read `manifest.json` → `kitVersion`
   - Verify no uncommitted critical work: `git status --porcelain`
   - If dirty working tree → prompt to commit or stash before proceeding
   - Record current state for rollback reference: `git rev-parse HEAD`

// turbo
2. **Preservation Snapshot**
   - Verify all Preservation Contract items exist (see rule for canonical list):
     - `.agent/session-state.json`
     - `.agent/session-context.md`
     - `.agent/identity.json`
     - `.agent/rules/` (user customizations)
     - `.agent/checklists/` (user customizations)
     - `.agent/decisions/` (ADRs)
     - `.agent/contexts/` (learning data)
   - Record file checksums for post-upgrade comparison

3. **Execute Upgrade**
   - Run the non-destructive AST merger:
     ```bash
     ag-kit update
     ```
   - For preview-only mode: `ag-kit update --dry-run`
   - Monitor output for warnings or conflicts

// turbo
4. **Verify Integrity**
   - Run manifest verification:
     ```bash
     ag-kit verify
     ```
   - Confirm capability counts match the new version
   - Verify all Preservation Contract items remain intact (compare checksums from Step 2)
   - If any protected file was modified or deleted → **STOP** and report violation

// turbo
5. **Post-Upgrade Summary**
   - Report version change (old → new)
   - List new capabilities added (agents, skills, workflows, rules)
   - Confirm Preservation Contract compliance
   - Complete the task-complete protocol

---

## Output Template

### Successful Upgrade

```markdown
## Upgrade Complete

| Field | Value |
| :--- | :--- |
| Previous Version | [old version] |
| New Version | [new version] |
| Preservation Contract | All protected files intact |
| Manifest Verify | Passed |

### New Capabilities

| Type | Added | Details |
| :--- | :--- | :--- |
| Agents | [+N] | [names] |
| Skills | [+N] | [names] |
| Workflows | [+N] | [names] |
| Rules | [+N] | [names] |

### Preservation Verification

All 7 protected items verified intact.

**Next**: Run `/status` to confirm project health.
```

### Failed Upgrade

```markdown
## Upgrade Failed

### Error

[Error description from ag-kit update output]

### Rollback

To restore previous state:
```bash
git checkout -- .agent/
```

### Resolution

1. [Fix steps based on error]
2. Re-run: `/upgrade`
```

---

## Governance

**PROHIBITED:**
- Using `init --force` for routine upgrades — this is a destructive wipe
- Deleting or modifying Preservation Contract files during upgrade
- Skipping post-upgrade verification
- Proceeding if `ag-kit verify` fails
- Auto-executing the upgrade step without user confirmation

**REQUIRED:**
- Pre-upgrade working tree check
- Preservation snapshot before upgrade execution
- `ag-kit verify` after every upgrade
- Preservation Contract compliance verification
- Human approval before executing Step 3 (upgrade)
- Rollback instructions available in case of failure

---

## Completion Criteria

- [ ] Current version identified
- [ ] Working tree clean (committed or stashed)
- [ ] Preservation Contract items inventoried
- [ ] Upgrade executed via `ag-kit update` (not `init --force`)
- [ ] `ag-kit verify` passes
- [ ] All Preservation Contract items verified intact
- [ ] Version change and new capabilities reported to user
- [ ] After upgrade: proceed to `/status` for health check

---

## Related Resources

- **Rule**: `.agent/rules/agent-upgrade-policy.md` (Preservation Contract)
- **Next**: `/status` (post-upgrade health check)
- **Skill**: `.agent/skills/verification-loop/SKILL.md`
- **Related**: `/deploy` (deployment after code changes) · `/review` (post-upgrade quality check)
- **CLI**: `ag-kit update`, `ag-kit update --dry-run`, `ag-kit verify`
