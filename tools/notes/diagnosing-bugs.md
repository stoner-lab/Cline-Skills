## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\diagnosing-bugs\`; source repo: `E:\Private\Projects\Cline-Skills\diagnosing-bugs\`.
- **Tools:** `Read` -> `read_files`; `Write`/`Edit` -> `editor`; shell -> `run_commands` (PowerShell 5.1 or pwsh 7); search -> `search_codebase`. Browser automation is only available when a Playwright MCP is configured; if it is not, skip that loop type and say so instead of pretending.
- **Bash vs PowerShell:** translate bash examples - `&&` becomes `;` (`If ($?) { ... }` is safer), `export X=1` becomes `$env:X='1'`, `grep` becomes `Select-String`, `2>&1` merges differently, `Ctrl+C` kills the whole pipeline.
- **`scripts\hitl-loop.template.sh` is a bash script.** Run it through WSL (`wsl bash "<skill>/scripts/hitl-loop.template.sh"`) or Git Bash. If neither exists, drive the human with plain numbered steps in the reply and paste their answer back yourself. Never describe a loop as automated when a human is the loop.
- **Redaction:** the repository rule `Rules/security.md` applies on top of the skill's own. Never put tokens, cookies or personal data into the reply, a log file or a commit message; quote only the lines that carry the signal.
- **No subagents.** Exploration runs inline, one step at a time.
- **Language:** talk to the user in their language; keep commands, code and log output verbatim.
