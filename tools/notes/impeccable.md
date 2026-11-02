## Cline runtime notes (read first)

- **Invocation:** `/impeccable [command] [target]`, e.g. `/impeccable audit src/pages/index.tsx`. With no argument, present the routing menu. References live in `reference/`; read only the one you need.
- **Tools:** shell → `run_commands` (PowerShell), read → `read_files`, edit → `editor`, search → `search_codebase`, browser → the Playwright MCP tools when present. Any `Bash(...)`, `Read`, `Edit`, `Grep` tool name later in this skill means the Cline equivalent.
- **Scripts:** `<skill-dir>` is `C:\Users\duy\.cline\skills\impeccable`. On Windows call `C:\Users\duy\.cline\skills\impeccable\scripts\impeccable.cmd <verb>`; keep the working directory at the user's project. The launcher runs an engine binary that ships beside it or is downloaded once and checksum-verified. If it fails or the machine is offline, take the "Launcher unavailable" path below — the skill still works in degraded mode.
- **No subagents:** where a reference tells you to spawn an agent (`agents/*.md` upstream), read the matching file in `reference/degraded/` (asset-producer, documenter, finish-reviewer, manual-edit-applier) and do the work inline. Say which one you used when you report back.
- **No hooks:** the design detector does not fire after edits. Run it manually when the engine is available (`impeccable.cmd detect <paths>`), otherwise rely on `reference/craft-floor.md` and your own review.
- **No live browser channel:** `live` and the interactive `generate` mode need the Impeccable extension. Use Playwright MCP to render and screenshot pages when available; if not, ask the user for screenshots at the sizes that matter and review those.
- **Language:** answer in the user's language (Vietnamese, Russian, English…), keep design vocabulary in English, write files as UTF-8. Report paths relative to the project.
- **Honesty:** never describe a visual result you have not rendered or seen. "Looks good" without evidence is a failed review.
