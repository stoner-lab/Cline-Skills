## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\design\`; in the source repo: `E:\Private\Projects\Cline-Skills\design\`.
- **Scripts run from the skill directory.** The text uses relative paths (`python scripts/...`, `node scripts/...`). `run_commands` starts in the workspace, so prefix the command with a location change: `Set-Location "$env:USERPROFILE\.cline\skills\design"; python scripts/logo/search.py "tech startup" --design-brief`
- **`python3` does not exist on Windows** - every `python3 ...` in the text runs as `python ...` (3.14 here).
- **Dependencies:** Pillow có sẵn; `google` (google-genai) KHÔNG có, nên mục logo/generate sẽ lỗi và phải nói rõ.
- **Tools:** `Read` -> `read_files`; `Write`/`Edit` -> `editor`; shell -> `run_commands` (PowerShell); search -> `search_codebase`. No subagents.
- **Never install packages on your own.** If something is missing, report the exact command and wait for permission.
- **Language:** answer the user in their language (Vietnamese by default); keep tokens, CSS, component names and file paths verbatim.
