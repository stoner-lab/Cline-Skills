## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\design-system\`; in the source repo: `E:\Private\Projects\Cline-Skills\design-system\`.
- **Scripts run from the skill directory.** The text uses relative paths (`python scripts/...`, `node scripts/...`). `run_commands` starts in the workspace, so prefix the command with a location change: `Set-Location "$env:USERPROFILE\.cline\skills\design-system"; node scripts/generate-tokens.cjs`
- **`python3` does not exist on Windows** - every `python3 ...` in the text runs as `python ...` (3.14 here).
- **Dependencies:** Node 24 cho các file `.cjs`; python chỉ dùng stdlib.
- **Tools:** `Read` -> `read_files`; `Write`/`Edit` -> `editor`; shell -> `run_commands` (PowerShell); search -> `search_codebase`. No subagents.
- **Never install packages on your own.** If something is missing, report the exact command and wait for permission.
- **Language:** answer the user in their language (Vietnamese by default); keep tokens, CSS, component names and file paths verbatim.
