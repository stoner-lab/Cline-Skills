## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\banner-design\`; in the source repo: `E:\Private\Projects\Cline-Skills\banner-design\`.
- **Scripts run from the skill directory.** The text uses relative paths (`python scripts/...`, `node scripts/...`). `run_commands` starts in the workspace, so prefix the command with a location change: `Set-Location "$env:USERPROFILE\.cline\skills\banner-design"; (không có script)`
- **`python3` does not exist on Windows** - every `python3 ...` in the text runs as `python ...` (3.14 here).
- **Dependencies:** Chỉ đọc `references/`; ảnh sinh cần dịch vụ ngoài nên hỏi trước.
- **Tools:** `Read` -> `read_files`; `Write`/`Edit` -> `editor`; shell -> `run_commands` (PowerShell); search -> `search_codebase`. No subagents.
- **Never install packages on your own.** If something is missing, report the exact command and wait for permission.
- **Language:** answer the user in their language (Vietnamese by default); keep tokens, CSS, component names and file paths verbatim.
