## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\ui-ux-pro-max\`; in the source repo: `E:\Private\Projects\Cline-Skills\ui-ux-pro-max\`.
- **Search command:** every `${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/scripts/search.py` in the text below is already rewritten to `$env:USERPROFILE\.cline\skills\ui-ux-pro-max\scripts\search.py`. Run it with `run_commands` (PowerShell):
  `python "$env:USERPROFILE\.cline\skills\ui-ux-pro-max\scripts\search.py" "<query>" --domain ux`
  `python` is 3.14 on this machine; scripts use only the standard library, so nothing to install.
- **Tools:** `Read` -> `read_files`; `Write`/`Edit` -> `editor`; shell -> `run_commands` (PowerShell); search code -> `search_codebase`.
- **Do not create a `bash` habit:** the examples were written for bash. In PowerShell use `;` instead of `&&`, quote the script path, and keep each query on one line.
- **`--persist` writes files:** always pass `--output-dir` pointing at the project root, never at the skill folder. Check whether `design-system\<slug>\MASTER.md` already exists before regenerating.
- **Data files are large:** `data\*.csv|json` is about 2,9 MB of local catalogue. Query it, do not read it whole into context; `references\quick-reference.md` and `references\pro-rules.md` are the only prose files meant to be read.
- **No subagents, no network:** the catalogue is local, so results cannot be fetched from the internet. If a search returns nothing, follow the "0 results" rule in the text and label the fallback as a default.
- **Language:** answer the user in their language (Vietnamese by default); keep design tokens, CSS property names and catalogue terms as they are.
