# Agent Upgrade Policy

> **Priority**: CRITICAL — Inviolable
> **Scope**: All AI Agent interactions related to framework initialization, upgrading, and state mutation.

---

## 1. The Preservation Contract

The Antigravity AI Kit exists organically alongside user code. User customizations must survive framework upgrades.

The following files and directories are **STRICTLY PROTECTED**:

| Protected Item | Type | Reason |
| :--- | :--- | :--- |
| `.agent/session-state.json` | File | Active session metadata |
| `.agent/session-context.md` | File | Session narrative context |
| `.agent/identity.json` | File | User/project identity (may contain PII) |
| `.agent/rules/` | Directory | User-customized governance rules |
| `.agent/checklists/` | Directory | User-customized quality gates |
| `.agent/decisions/` | Directory | Architecture Decision Records |
| `.agent/contexts/` | Directory | Learning data and plan quality logs |

This is the **canonical list**. The `/upgrade` workflow references this list — do not duplicate or abbreviate it elsewhere.

---

## 2. Non-Destructive Upgrades Only

| Command | Purpose | Safety |
| :--- | :--- | :--- |
| `ag-kit update` | Non-destructive AST merger | Safe — preserves protected items |
| `ag-kit update --dry-run` | Preview upgrade changes | Safe — read-only |
| `init --force` | Catastrophic repair | **DESTRUCTIVE** — wipes protected items |

- **Mandated**: Use `ag-kit update` for all routine upgrades
- **Prohibited**: Never use `init --force` for routine upgrades. This is a last-resort catastrophic repair command that wipes protected files

---

## 3. Upgrade Governance

The `/upgrade` workflow follows the standard EWS v1.0 governance model:

- **Human confirmation required** before executing `ag-kit update`
- **Post-upgrade verification** via `ag-kit verify` is mandatory
- **Preservation verification** — all 7 protected items must be confirmed intact after upgrade
- **Rollback available** — `git checkout -- .agent/` restores pre-upgrade state if uncommitted

---

## Related Resources

- **Workflow**: `.agent/workflows/upgrade.md` (`/upgrade`)
- **Skill**: `.agent/skills/verification-loop/SKILL.md`
- **See also**: `.agent/rules/security.md` (secrets in upgrade payloads), `.agent/rules/git-workflow.md` (commit conventions after upgrade)
