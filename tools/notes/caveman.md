## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\caveman\`; in the source repo: `E:\Private\Projects\Cline-Skills\caveman\`.
- **There is no `/caveman` command in Cline.** The skill is switched on by the user saying one of the trigger phrases, and switched off by "stop caveman" / "normal mode" in any language. Loading this file to answer a status question is not activation.
- **No host hooks here.** Where the text asks you to relay `Caveman mode: <mode>` from a hook, print the mode you actually followed plus `(not tracked by this host)`, for example `Caveman mode: caveman (not tracked by this host)`.
- **Aliases:** `/caveman ultra` and `/caveman wenyan` point at the `ultracave` and `megacave` skills, which are not installed in this collection. Say so and stay in this skill instead of improvising.
- **Rules of this repository still win on content, not on style:** a security warning, an irreversible action (`Remove-Item -Recurse`, `git push --force`, history rewrite), or a question you ask the user is written in full sentences first, then the terse style resumes. Terse is never a reason to drop a `not`, a `never`, a path, a number or an error string.
- **Language:** compress the style, never the language. Vietnamese stays Vietnamese, Russian stays Russian; technical terms, paths, commands and errors stay verbatim.
- **Tools:** `read_files`, `editor`, `run_commands` (PowerShell), `search_codebase` - the usual names, unchanged by the voice.
