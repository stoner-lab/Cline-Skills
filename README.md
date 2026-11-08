# Cline Skills

A collection of AI agent skills, adapted for **Cline on Windows**, plus a few written
here. Skills come from several platforms:
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills),
[pbakaus/impeccable](https://github.com/pbakaus/impeccable),
[iart-ai/manim-skills](https://github.com/iart-ai/manim-skills),
[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) and
[tt-a1i/archify](https://github.com/tt-a1i/archify), plus a few skills written here.

Every skill is a folder with a `SKILL.md` (YAML frontmatter plus instructions) and optional
`scripts/`, `references/`, `assets/`. Copy a folder into `C:\Users\<user>\.cline\skills\`
and restart Cline, or start a new task, so the skill list reloads. Call a skill by name or
just describe the job: the `description` carries Vietnamese, Russian and English triggers.

**Languages:** [English](README.md) | [Русский](README.ru.md) | [Tiếng Việt](README.vi.md)

## Skills

| Skill | What it does | Origin |
|---|---|---|
| `otchet` | Russian academic reports (ПР, лабораторная, реферат, курсовая): LETI title page, Times New Roman 14, captions, DOCX and PDF rules | this repo |
| `injection-scan` | Offline prompt-injection scanner for untrusted text and documents (docx, pdf, pptx, xlsx, zip), exit codes 0 clean, 1 review or unscanned, 2 block | this repo |
| `archify` | Turn an idea, plan, Mermaid source or codebase into a validated standalone HTML diagram (architecture, workflow, sequence, dataflow, lifecycle, ERD, class, tree, timeline, waterfall) or a one-page explainer | adapted from tt-a1i/archify |
| `docx` | Create, read and edit Word documents, including tables and styles | adapted from upstream (see `LICENSE`) |
| `pdf` | Read, extract text and tables, merge, split, rotate, watermark, fill forms, encrypt, OCR | adapted from upstream (see `LICENSE`) |
| `pptx` | Create, read and edit presentations | adapted from upstream (see `LICENSE`) |
| `xlsx` | Create, read, edit and clean spreadsheets | adapted from upstream (see `LICENSE`) |
| `frontend-design` | Visual design guidance so a UI does not look templated | adapted from upstream (see `LICENSE`) |
| `mcp-builder` | Build MCP servers in Python or Node | adapted from upstream (see `LICENSE`) |
| `skill-creator` | Build, test, benchmark and package new skills | adapted from upstream (see `LICENSE`) |
| `grilling` | Relentless interview that stress-tests a plan or decision as a design tree, one round of questions at a time, each with a recommended answer | adapted from upstream (see `LICENSE`) |
| `grill-me` | One-line alias that starts `grilling` | adapted from upstream (see `LICENSE`) |
| `diagnosing-bugs` | Diagnosis loop for hard bugs and performance regressions: build a failing feedback loop, minimise, hypothesise, instrument, fix, clean up | adapted from upstream (see `LICENSE`) |
| `handoff` | Compact the current conversation into a handoff document for the next session, with secrets redacted | adapted from upstream (see `LICENSE`) |
| `impeccable` | Frontend design direction, audit, critique and rewrite with a playbook library and a design detector | adapted from pbakaus/impeccable |
| `design-taste-frontend` | Company sites at the figma.com and x.ai bar, checked by its own headless-browser checker | adapted from Leonxlnx/taste-skill |
| `manim` | Math and physics animations with Manim CE, rendered to MP4 or GIF | adapted from iart-ai/manim-skills |
| `git-workflow-and-versioning` | Branching, atomic commits, commit messages, pull requests, semantic versioning | adapted from addyosmani/agent-skills |
| `documentation-and-adrs` | Architecture decision records and the documentation that keeps a codebase readable | adapted from addyosmani/agent-skills |
| `code-review-and-quality` | Multi-axis code review before merging: correctness, design, errors, tests, security | adapted from addyosmani/agent-skills |

## What "adapted" means

Each adapted skill opens with a **Cline runtime notes** section: tool names mapped to Cline
(`read_files`, `editor`, `run_commands`, `search_codebase`), the real skill directory and how
relative paths resolve from it, what is installed on this machine, PowerShell instead of Bash,
no subagents, and Vietnamese plus Russian trigger phrases in the `description`.

Adaptation is reproducible, not hand-edited: `upstream.json` pins the upstream commit of every
skill, `tools/adapt_config.json` holds the per-skill description, notes file, replacements and
files to keep, `tools/notes/*.md` holds the Cline notes, and `tools/sync_upstream.py`
(`check`, `apply`, `status`, `add`) regenerates `SKILL.md` from those inputs.

## Requirements

- Cline in VS Code or the Cline Desktop app; skills live in `~/.cline/skills`.
- Node 18 or newer for `archify` and `design-taste-frontend`.
- Python 3.11 or newer with `python-docx`, `python-pptx`, `openpyxl`, `PyMuPDF`, `pypdf`,
  `reportlab`, `lxml` for `docx`, `pptx`, `xlsx`, `pdf`, `otchet` and `injection-scan`.

## License

Repository-level terms are in [`LICENSE`](LICENSE): the files written here are MIT.
Skills taken from other projects keep their own license, and those terms still apply
to this copy.

