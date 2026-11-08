---
name: slides
description: "Làm bài trình chiếu HTML có Chart.js, design token, layout responsive và công thức copywriting theo ngữ cảnh. Dùng khi người dùng nói: 'làm slide html', 'bài thuyết trình html', 'slide có chart', 'deck html', 'làm presentation html'. Không dấu cũng khớp: 'lam slide html', 'bai thuyet trinh html', 'slide co chart', 'deck html', 'lam presentation html'. Khác pptx: `slides` ra file HTML, còn pptx sửa/tạo file .pptx thật. Ra file HTML. Cần file .pptx thật để nộp hoặc sửa thì dùng pptx; cần báo cáo Word thì docx hoặc otchet."
license: "MIT (c) 2024 Next Level Builder - full text in LICENSE inside this directory"
compatibility: "Cline on Windows: PowerShell shell, python 3.14 and node 24 on PATH, read_files/editor/run_commands; scripts run from the skill directory; no subagents; see the Cline runtime notes inside."
metadata:
  upstream: "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/main/.claude/skills/slides"
  adaptation: "Cline runtime notes in SKILL.md"
---
# Slides

## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\slides\`; in the source repo: `E:\Private\Projects\Cline-Skills\slides\`.
- **Scripts run from the skill directory.** The text uses relative paths (`python scripts/...`, `node scripts/...`). `run_commands` starts in the workspace, so prefix the command with a location change: `Set-Location "$env:USERPROFILE\.cline\skills\slides"; (không có script)`
- **`python3` does not exist on Windows** - every `python3 ...` in the text runs as `python ...` (3.14 here).
- **Dependencies:** Chỉ đọc `references/`; Chart.js nhúng qua CDN nên trình chiếu cần mạng.
- **Tools:** `Read` -> `read_files`; `Write`/`Edit` -> `editor`; shell -> `run_commands` (PowerShell); search -> `search_codebase`. No subagents.
- **Never install packages on your own.** If something is missing, report the exact command and wait for permission.
- **Language:** answer the user in their language (Vietnamese by default); keep tokens, CSS, component names and file paths verbatim.

Strategic HTML presentation design with data visualization.

## When to Use

- Marketing presentations and pitch decks
- Data-driven slides with Chart.js
- Strategic slide design with layout patterns
- Copywriting-optimized presentation content

## Subcommands

| Subcommand | Description | Reference |
|------------|-------------|-----------|
| `create` | Create strategic presentation slides | `references/create.md` |

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project: `scripts/<file>` is this skill's own `scripts/` folder, and `../<skill>/scripts/<file>` is a sibling sub-skill installed alongside it. Build the full path from that directory (Claude Code reports it as the skill's base directory when the skill loads) and keep the working directory at the project root – the scripts read and write project files such as `docs/brand-guidelines.md`, `assets/design-tokens.json` or `src/` relative to it.

## References (Knowledge Base)

| Topic | File |
|-------|------|
| Layout Patterns | `references/layout-patterns.md` |
| HTML Template | `references/html-template.md` |
| Copywriting Formulas | `references/copywriting-formulas.md` |
| Slide Strategies | `references/slide-strategies.md` |

## Routing

1. Parse subcommand from `$ARGUMENTS` (first word)
2. Load corresponding `references/{subcommand}.md`
3. Execute with remaining arguments
