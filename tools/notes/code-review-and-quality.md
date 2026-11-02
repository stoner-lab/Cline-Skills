## Cline runtime notes (read first)

- **Skill directory:** the folder that holds this `SKILL.md`. Installed: `C:\Users\<user>\.cline\skills\code-review-and-quality\`; in the source repo: `E:\Private\Projects\Cline-Skills\code-review-and-quality\`.
- **Tools:** shell -> `run_commands` (PowerShell), read -> `read_files`, edit -> `editor`, search -> `search_codebase`, browser -> Playwright MCP. Any `Bash`, `Read`, `Write`, `Edit`, `Grep`, `Glob` name below means the Cline equivalent.
- **Shell is Windows PowerShell.** Use `python`, not `python3`; `mkdir -p`, `cp -r`, `rm -rf`, `cat >` do not exist - use `New-Item`, `Copy-Item`, `Remove-Item`, `Set-Content`. Never use `nohup`, `$!`, `&&` or heredocs.
- **No subagents.** Everything runs inline, in one session, one step at a time. Where upstream says to delegate to an agent, do the work yourself and say so.
- **Encoding:** all text files are UTF-8; the console code page mangles Vietnamese and Cyrillic, so write logs to a file and read them with `read_files`.
- **Language:** answer in the user's language (Vietnamese, Russian, English...). Code, commit messages, branch names and file contents follow the repository convention (English here).
- **Destructive git commands** (`reset --hard`, `push --force`, `clean -fd`, `branch -D`) are never run without an explicit instruction from the user in the same turn.

- **Review inline:** read the diff with `run_commands` (`git --no-pager diff`), the surrounding files with `read_files`, cross-references with `search_codebase`, and report findings ordered by severity (blocker, should fix, nit) with file:line.
- **Scope:** review what changed plus its immediate blast radius; do not rewrite unrelated code, and say explicitly when something is out of scope.
