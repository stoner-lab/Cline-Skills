# Grilling

## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\grilling\`; source repo: `E:\Private\Projects\Cline-Skills\grilling\`.
- **Tools:** `Read` -> `read_files`; `Write`/`Edit` -> `editor`; shell -> `run_commands` (PowerShell); search -> `search_codebase`; asking the user -> `ask_question` when a single choice is needed, otherwise numbered questions in the reply.
- **One round = one message.** Ask the whole frontier in a single reply, numbered, each with your recommended answer, then stop and wait. Do not drip one question per message, and never start the next round before the user answers this one.
- **No subagents.** Where the upstream text says to dispatch a sub-agent with a fresh context to find a fact, do that lookup yourself with `read_files`, `search_codebase` or `run_commands`, state the fact you found, and ask only the questions downstream of it. Do not ask the user for anything you can read from disk.
- **Facts are yours, decisions are the user's.** Lookups are yours to do; every decision goes to the user and waits.
- **Language:** ask in the user's language; keep technical terms, file paths and identifiers unchanged.
- **Stop condition:** the frontier is empty. Then list the settled decisions in one block, and act only after the user confirms that you understood each other.
