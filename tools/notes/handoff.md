# Handoff

## Cline runtime notes (read first)

- **Where to write:** `%TEMP%` (`$env:TEMP`) on Windows, as the skill says - not the workspace. Name it `handoff-<topic>-<YYYYMMDD-HHMMSS>.md`.
- **"Suggested skills" section:** name Cline skills, not Claude ones. The next agent calls the `skills` tool with the skill name (for example `otchet`, `injection-scan`, `archify`, `diagnosing-bugs`). If a skill upstream would call does not exist here, say which one is missing and what it would have done.
- **Reference, do not duplicate:** link specs, plans, ADRs, issues, commits and diffs by path or URL instead of copying their content.
- **Redaction:** no tokens, cookies, passwords or personal data. The repository rule `Rules/security.md` applies here too.
- **Tools:** `read_files` to collect the material, `editor` to write the document, `run_commands` (PowerShell) when a command's output must be quoted.
- **Language:** write the handoff in the user's language; keep paths, commands and identifiers unchanged.
