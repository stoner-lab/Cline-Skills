## Cline runtime notes (read first)

- **Skill directory:** the folder that holds this `SKILL.md`. Installed: `C:\Users\<user>\.cline\skills\documentation-and-adrs\`; in the source repo: `E:\Private\Projects\Cline-Skills\documentation-and-adrs\`.
- **Tools:** shell -> `run_commands` (PowerShell), read -> `read_files`, edit -> `editor`, search -> `search_codebase`, browser -> Playwright MCP. Any `Bash`, `Read`, `Write`, `Edit`, `Grep`, `Glob` name below means the Cline equivalent.
- **Shell is Windows PowerShell.** Use `python`, not `python3`; `mkdir -p`, `cp -r`, `rm -rf`, `cat >` do not exist - use `New-Item`, `Copy-Item`, `Remove-Item`, `Set-Content`. Never use `nohup`, `$!`, `&&` or heredocs.
- **No subagents.** Everything runs inline, in one session, one step at a time. Where upstream says to delegate to an agent, do the work yourself and say so.
- **Encoding:** all text files are UTF-8; the console code page mangles Vietnamese and Cyrillic, so write logs to a file and read them with `read_files`.
- **Language:** answer in the user's language (Vietnamese, Russian, English...). Code, commit messages, branch names and file contents follow the repository convention (English here).
- **Destructive git commands** (`reset --hard`, `push --force`, `clean -fd`, `branch -D`) are never run without an explicit instruction from the user in the same turn.

- **Where ADRs live:** follow the repository convention (`docs/adr/`, `docs/decisions/`, or `adr/`); if there is none, propose `docs/adr/NNNN-short-title.md` and confirm with the user before creating the folder.
- **Language of documents:** the repository decides (English by default, Russian for course reports); keep one language per document.
