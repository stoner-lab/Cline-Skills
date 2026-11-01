# Cline Skills

A collection of [Cline](https://cline.bot) skills, adapted from Anthropic's
[anthropics/skills](https://github.com/anthropics/skills) and from
[pbakaus/impeccable](https://github.com/pbakaus/impeccable), plus two project-specific
skills (`otchet`, `skill-creator`).

Every skill is a folder with a `SKILL.md` (YAML frontmatter plus instructions) and
optional `scripts/`, `references/`, `assets/`. Copy a folder into
`C:\Users\<user>\.cline\skills\` and restart Cline (or start a new task) so the
skills list is reloaded. Invoke with `/skill-name`, or just describe the job: the
`description` of each skill lists Vietnamese, Russian and English trigger phrases.

## Skills

| Skill | What it does | Origin |
|---|---|---|
| `otchet` | Russian academic reports (ПР, лабораторная, реферат, курсовая): LETI title page, Times New Roman 14, captions, DOCX plus PDF, Vietnamese and UTF-8 rules | this repo |
| `skill-creator` | Build, test, benchmark and package new Cline skills | adapted from anthropics/skills |
| `impeccable` | Frontend design direction, audit, critique and rewrite with a full playbook library and a design detector | adapted from pbakaus/impeccable 4.8.0 |
| `frontend-design` | Visual design guidance so a UI does not look templated | adapted from anthropics/skills |
| `docx` | Create, read and edit Word documents | adapted from anthropics/skills |
| `xlsx` | Create, read, edit and clean spreadsheets | adapted from anthropics/skills |
| `pptx` | Create, read and edit presentations | adapted from anthropics/skills |
| `pdf` | Read, extract, merge, split, fill and create PDFs | adapted from anthropics/skills |
| `mcp-builder` | Build MCP servers in Python or Node | adapted from anthropics/skills |

## What "adapted to Cline" means

Anthropic's skills assume the Claude runtime: `view` / `create_file` / `str_replace` /
`bash_tool` tools, subagents, `claude -p`, LibreOffice, `pandoc`, `unzip`, `/mnt/...` paths.
Each adapted skill now opens with a **Cline runtime notes** section that:

- maps every tool name to the Cline equivalent (`read_files`, `editor`, `run_commands`,
  `search_codebase`, Playwright MCP for the browser);
- states the real skill directory and resolves relative paths from it;
- lists what is installed (python-docx, python-pptx, openpyxl, pypdf, pdfplumber,
  reportlab, lxml, pypdfium2, PyYAML) and what is missing (LibreOffice, pandoc,
  poppler, Tesseract);
- replaces Bash-only helpers with PowerShell equivalents and Word COM for PDF export;
- removes the subagent dependency (work runs inline) and keeps UTF-8 everywhere;
- adds Vietnamese, Russian and English trigger phrases to the `description`, because
  Cline picks a skill from the metadata alone.

Details per skill: `references/cline-adaptation.md` in `skill-creator` and
`impeccable`, and the notes section inside every other `SKILL.md`.

## Requirements

- Cline in VS Code (skills live in `~/.cline/skills`).
- Python 3.11+ with: `python-docx`, `python-pptx`, `openpyxl`, `pypdf`, `pdfplumber`,
  `reportlab`, `lxml`, `pypdfium2`, `PyYAML`:
  `pip install python-docx python-pptx openpyxl pypdf pdfplumber reportlab lxml pypdfium2 pyyaml`
- Optional: Node 20+ (`docx` npm package for the docx skill, MCP SDK for mcp-builder),
  Microsoft Word for DOCX to PDF export, Playwright MCP for visual checks.

## Typography rules baked into the skills

Text that a person reads uses the en dash `–` with spaces, never the em dash `—`, never
`-` as a sentence dash, no `≻`, `→`, `•`, `…`, no curly quotes. Math symbols
(`≤`, `≥`, `±`, `×`, `≈`, `√`, `σ`, `χ²`, `α`) stay, because the course needs them.

## Licensing

Every skill keeps the license of its origin: `otchet` and `skill-creator` are this
project's own work, `impeccable` is Apache 2.0 (see `impeccable/LICENSE`), the
Anthropic-derived skills carry their `LICENSE.txt` with the upstream terms.

Bản Việt: repo gom 9 skill cho Cline. Cài bằng cách copy thư mục vào
`C:\Users\<user>\.cline\skills`, khởi động lại Cline, gọi `/tên-skill` hoặc mô tả
việc cần làm bằng tiếng Việt.
