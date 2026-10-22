---
name: shell-conventions
description: PowerShell shell conventions for Windows. Avoid bash-isms. Reference before running terminal commands.
triggers: [powershell, terminal, shell, command, run, windows, cli]
---

# Shell Conventions — Windows PowerShell 5.x

> **Environment**: Windows PowerShell 5.x (NOT PowerShell 7/Core)
> **Scope**: All `run_command` tool calls across all workspaces

---

## 🔴 CRITICAL RULES

1. **NEVER use `&&`** — It is NOT a valid operator in PowerShell 5.x
2. **NEVER use `cd dir && command`** — Use the `Cwd` parameter on `run_command` instead
3. **NEVER use `||`** as bash-style OR — Use `if (-not $?) { ... }` instead

---

## Operator Reference

| Operator | Bash                       | PowerShell 5.x          | Notes                             |
| -------- | -------------------------- | ----------------------- | --------------------------------- |
| `&&`     | Sequential (conditional)   | ❌ **NOT SUPPORTED**    | Use `;` or `Cwd` param            |
| `;`      | Sequential (unconditional) | ✅ Sequential execution | Runs next regardless of exit code |
| `\|`     | Pipe stdout                | ✅ Pipe objects         | Different semantics than bash     |
| `\|\|`   | OR (run on failure)        | ❌ **NOT SUPPORTED**    | Use `if (-not $?) { ... }`        |
| `>`      | Redirect stdout            | ✅ Redirect output      | Same behavior                     |
| `2>&1`   | Redirect stderr to stdout  | ✅ Merge streams        | Same behavior                     |

---

## Patterns

### ❌ WRONG: Chaining with &&

```bash
cd src && npm test && npm run build
```

### ✅ RIGHT: Use Cwd parameter

```powershell
# Set Cwd to "src" on run_command, then just run:
npm test
```

### ✅ RIGHT: Sequential with ;

```powershell
git status; git log --oneline -5
```

### ✅ RIGHT: Call operator for executables with spaces/special chars

```powershell
& ".venv\Scripts\ruff.exe" check app/
& ".venv\Scripts\pytest.exe" tests/ -v
```

---

## Common Patterns

| Task                | PowerShell Command                          |
| ------------------- | ------------------------------------------- |
| Run Node.js tests   | `npm test`                                  |
| Run Python tests    | `& ".venv\Scripts\pytest.exe" tests/ -q`    |
| Run linter          | `npm run lint`                              |
| Check git status    | `git status`                                |
| Build project       | `npm run build`                             |
| Install deps        | `npm install`                               |
| List files          | `Get-ChildItem -Recurse`                    |
| Find in files       | `Select-String -Pattern "text" -Path "*.md"`|

---

## Virtual Environment (Python)

```powershell
# Activate (PowerShell)
& ".venv\Scripts\Activate.ps1"

# Run without activation (preferred for tool calls)
& ".venv\Scripts\python.exe" -m pytest tests/ -q
& ".venv\Scripts\python.exe" -m ruff check app/
```

> [!TIP]
> For `run_command` tool calls, prefer calling the executable directly with `&` rather than activating the virtual environment.
