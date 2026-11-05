# Cline Skills

A collection of [Cline](https://cline.bot) skills, adapted from Anthropic's
[anthropics/skills](https://github.com/anthropics/skills), from
[pbakaus/impeccable](https://github.com/pbakaus/impeccable),
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills),
[iart-ai/manim-skills](https://github.com/iart-ai/manim-skills) and
[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), plus two project-specific
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
| `design-taste-frontend` | Anti-slop company sites at the figma.com and x.ai bar: one section per screen, equal edges, real photographs and product UI, shader effects only on tech, gaming and software pages, checked by its own headless-browser checker | adapted from Leonxlnx/taste-skill 2.5.0 |
| `frontend-design` | Visual design guidance so a UI does not look templated | adapted from anthropics/skills |
| `docx` | Create, read and edit Word documents | adapted from anthropics/skills |
| `xlsx` | Create, read, edit and clean spreadsheets | adapted from anthropics/skills |
| `pptx` | Create, read and edit presentations | adapted from anthropics/skills |
| `pdf` | Read, extract, merge, split, fill and create PDFs | adapted from anthropics/skills |
| `manim` | Math and physics animations in Python with Manim CE: animated equations, plotted functions, geometric proofs, 3D scenes, rendered to MP4/GIF | adapted from iart-ai/manim-skills |
| `mcp-builder` | Build MCP servers in Python or Node | adapted from anthropics/skills |
| `git-workflow-and-versioning` | Branching, atomic commits, commit messages, PRs, semantic versioning and changelogs | adapted from addyosmani/agent-skills |
| `documentation-and-adrs` | Architecture decision records and the documentation that keeps a codebase understandable | adapted from addyosmani/agent-skills |
| `code-review-and-quality` | Multi-axis code review before merging: correctness, design, errors, tests, security | adapted from addyosmani/agent-skills |

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
- For `design-taste-frontend`: Node 22+ and Chrome, Edge or Chromium. The skill ships every
  script it needs (no npm packages, headless Chrome driven over `127.0.0.1`); ffmpeg is
  optional. Run `node design-taste-frontend\scripts\check_env.mjs` first - it prints what is
  missing and the build waits for your yes before anything is installed.
- For `manim`: Manim CE (`python -m pip install manim`), `ffmpeg` and `ffprobe` on PATH,
  and MiKTeX (only for `Tex`/`MathTex`). Run `manim\scripts\manim-env-check.ps1` to see
  what is missing before blaming the scene code.

## Typography rules baked into the skills

Text that a person reads uses the en dash `–` with spaces, never the em dash `—`, never
`-` as a sentence dash, no `≻`, `→`, `•`, `…`, no curly quotes. Math symbols
(`≤`, `≥`, `±`, `×`, `≈`, `√`, `σ`, `χ²`, `α`) stay, because the course needs them.

## Keeping up with upstream

Thirteen of the fourteen skills are forks; only `otchet` is native to this repository.
Their `SKILL.md` is **generated**, so an upstream update is re-applied mechanically
instead of merged by hand.

| Strategy | Meaning | Skills |
|---|---|---|
| `adapt` | `SKILL.md` is rebuilt from upstream plus `tools/notes/<skill>.md`; other files are never overwritten or deleted | pdf, docx, pptx, xlsx, frontend-design, design-taste-frontend, mcp-builder, git-workflow-and-versioning, documentation-and-adrs, code-review-and-quality |
| `manual` | `SKILL.md` is hand-written; sync only reports that upstream moved, you merge yourself | skill-creator, impeccable, manim |
| `own` | this repository is the source of truth; sync skips it | otchet |

**Schedule.** GitHub Actions runs `tools/sync_upstream.py check` every day at
06:00 UTC (13:00 Vietnam, 09:00 Moscow). When an upstream commit changed, the job runs
`apply --all`, `quick_validate.py` and opens **one** pull request on the
`sync/upstream` branch. The branch is reused, so a week of updates still means one PR
to review. Nothing merges automatically.

**Token cost.** `check` and `apply` are plain Python: no model tokens. Tokens are spent
only when a human or an agent reads the diff, which happens once per pull request, not
once per cron run.

Local use:

```powershell
$env:GH_TOKEN = # a GitHub token with public read access
python tools\sync_upstream.py check              # 0 = up to date, 1 = something changed
python tools\sync_upstream.py apply pdf --diff   # regenerate one skill and show the diff
python tools\sync_upstream.py status             # last synced commit per skill
```

Adding a skill from another repository:

```powershell
python tools\sync_upstream.py add my-skill --repo owner/repo --path skills/my-skill
# write tools/notes/my-skill.md, set description (with Vietnamese triggers) and license
python tools\sync_upstream.py apply my-skill
```

Rules: never edit a generated `SKILL.md` by hand. Change `tools/notes/<skill>.md` or
`tools/adapt_config.json` and regenerate. `apply` preserves `LICENSE*`, `CLINE-*.md` and
`references/cline-adaptation.md`; everything else in an `adapt` skill comes from upstream.

Bản Việt: 10 skill `adapt` tự cập nhật từ upstream mỗi ngày và gộp vào một PR trên nhánh
`sync/upstream`; `skill-creator`, `impeccable` và `manim` sửa tay nên chỉ được báo; `otchet`
là nguồn gốc nên bỏ qua. Bước check/apply không tốn token.

## Metadata hygiene

Files handed to a person must not advertise the tool, library or model that produced
them. Every skill that writes a deliverable ships `scripts/strip_metadata.py` (identical
copy, also kept once in `tools/strip_metadata.py`):

```powershell
python scripts\strip_metadata.py report.docx report.pdf clip.mp4   # clean in place
python scripts\strip_metadata.py --check report.docx report.pdf    # report, exit 1 if dirty
python scripts\strip_metadata.py --author "Ivan Ivanov" --title "Otchet" report.docx
```

What it removes:

| Format | Fingerprints left by the library | After cleaning |
|---|---|---|
| `.docx` `.xlsx` `.pptx` | `creator: python-docx`, `description: generated by python-docx`, `lastModifiedBy: Steve Canny`, `creator: openpyxl`, `Application: Microsoft Excel Compatible / Openpyxl 3.1.5`, fake 2013 template dates, `docProps/custom.xml`, packaged thumbnail | neutral `core.xml` (title, optional author, real created/modified), producer fields removed from `app.xml`, no custom part, no thumbnail |
| `.pdf` | `Producer: ReportLab PDF Library`, `Creator: anonymous`, `Title: untitled`, `Subject: unspecified`, XMP stream | only `/CreationDate` and `/ModDate`, no XMP |
| `.png` `.jpg` | EXIF, XMP, text chunks (`Software`, `Author`) | pixels re-encoded, ICC profile kept |
| `.mp4` `.mov` | `encoder=Lavf62.13.101`, `comment: Rendered with Manim Community v0.22.1` | remuxed with `-map_metadata -1` and bitexact flags |

Rules: clean **before** delivering, never after a human edited the file; run `--check`
in the same breath as the deliverable check; if an author is required, pass the real
name (`--author`) or leave the field empty, never a tool or model name.

The same rule covers source files and the commit trail: no "generated with ..." or
"made by ..." lines in a document, a code comment or a commit trailer, and no
`Co-Authored-By` trailer naming an assistant. Attribution to the upstream project a
skill is derived from (licence header, README credit) stays, because the MIT licence
requires it - that names the project, not the generator.

Bản Việt: mọi file giao cho người khác không được để lại dấu vết công cụ trong
metadata. Chạy `python scripts\strip_metadata.py <file>` trước khi giao và xác nhận
bằng `--check`; tên tác giả chỉ ghi bằng tên thật qua `--author`, không ghi tên tool
hay tên AI.

## Licensing

Every skill keeps the license of its origin: `otchet` and `skill-creator` are this
project's own work, `impeccable` is Apache 2.0 (see `impeccable/LICENSE`),
`design-taste-frontend` is MIT, Copyright (c) 2026 Leonxlnx (see
`design-taste-frontend/LICENSE`), and the Anthropic-derived skills carry their
`LICENSE.txt` with the upstream terms.

Bản Việt: repo gom 14 skill cho Cline. Cài bằng cách copy thư mục vào
`C:\Users\<user>\.cline\skills`, khởi động lại Cline, gọi `/tên-skill` hoặc mô tả
việc cần làm bằng tiếng Việt.
