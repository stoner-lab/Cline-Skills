---
name: handoff
description: "Nén hội thoại hiện tại thành tài liệu bàn giao để phiên sau tiếp tục: đã làm gì, tiếp theo là gì, nên gọi skill nào, đã che secrets. Dùng khi người dùng nói: 'bàn giao công việc', 'viết handoff', 'tóm tắt để phiên sau tiếp', 'chuẩn bị context cho phiên mới'. Không dấu cũng khớp: 'ban giao cong viec', 'viet handoff', 'tom tat de phien sau tiep', 'chuan bi context cho phien moi'. Kết hợp: ghi rõ trong tài liệu những skill mà phiên sau nên gọi."
license: "MIT (c) 2026 Matt Pocock - full text in LICENSE inside this directory"
compatibility: "Cline on Windows: PowerShell shell, read_files/editor/run_commands/search_codebase, no subagents; see the Cline runtime notes inside."
metadata:
  upstream: "https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff"
  adaptation: "Cline runtime notes in SKILL.md"
---
# Handoff

## Cline runtime notes (read first)

- **Where to write:** `%TEMP%` (`$env:TEMP`) on Windows, as the skill says - not the workspace. Name it `handoff-<topic>-<YYYYMMDD-HHMMSS>.md`.
- **"Suggested skills" section:** name Cline skills, not Claude ones. The next agent calls the `skills` tool with the skill name (for example `otchet`, `injection-scan`, `archify`, `diagnosing-bugs`). If a skill upstream would call does not exist here, say which one is missing and what it would have done.
- **Reference, do not duplicate:** link specs, plans, ADRs, issues, commits and diffs by path or URL instead of copying their content.
- **Redaction:** no tokens, cookies, passwords or personal data. The repository rule `Rules/security.md` applies here too.
- **Tools:** `read_files` to collect the material, `editor` to write the document, `run_commands` (PowerShell) when a command's output must be quoted.
- **Language:** write the handoff in the user's language; keep paths, commands and identifiers unchanged.

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows) - not the current workspace.

Include a "suggested skills" section in the document, naming which skills the next agent should call the `skills` tool for (Cline).

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
