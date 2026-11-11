---
name: ppt-master
description: "Quy trình dựng bài trình chiếu từ tài liệu nguồn (PDF, DOCX, URL, Markdown): tạo project → chiến lược → từng trang SVG → xuất PPTX, kèm template, icon và layout dựng sẵn. Dùng khi người dùng nói: 'làm ppt từ tài liệu', 'dựng deck từ báo cáo', 'làm bài trình chiếu từ pdf', 'tạo slide từ word', 'ppt-master', 'chuyển tài liệu thành slide'. Không dấu cũng khớp: 'lam ppt tu tai lieu', 'dung deck tu bao cao', 'lam bai trinh chieu tu pdf', 'tao slide tu word', 'ppt-master', 'chuyen tai lieu thanh slide'. Ưu tiên skill này khi phải dựng deck TỪ tài liệu nguồn; chỉ sửa hoặc tạo file .pptx trực tiếp thì dùng pptx; cần deck HTML có Chart.js thì dùng slides."
license: "MIT"
compatibility: "Cline on Windows: PowerShell shell, python 3.14, node 24; read_files/editor/run_commands; scripts run from the skill directory; no pandoc, no LibreOffice, no subagents; see the Cline runtime notes inside."
metadata:
  upstream: "https://github.com/hugohe3/ppt-master/tree/main/skills/ppt-master"
  adaptation: "Cline runtime notes in SKILL.md"
  copyright: "Copyright (c) 2025-2026 Hugo He"
  license: "MIT"
  official_repository: "https://github.com/hugohe3/ppt-master"
  sponsors: "https://github.com/sponsors/hugohe3"
---
# PPT Master Skill

## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\ppt-master\`; in the source repo: `E:\Private\Projects\Cline-Skills\ppt-master\`.
- **Scripts run from the skill directory** (`python scripts/...`). `run_commands` starts in the workspace, so prefix with a location change: `Set-Location "$env:USERPROFILE\.cline\skills\ppt-master"; python scripts/<name>.py ...`
- **Python 3.14 on PATH.** Present: `python-pptx`, `PyMuPDF`, `Pillow`, `numpy`, `reportlab`, `svglib`, `nbconvert`, `requests`, `beautifulsoup4`, `curl_cffi`, `mammoth`, `markdownify`, `ebooklib`, `google-genai`, `openai`.
- **Pandoc 3.13 is installed** at `%LOCALAPPDATA%\Pandoc\pandoc.exe` and its folder is on the user PATH. A session started before the install may not see it: call the absolute path `"$env:LOCALAPPDATA\Pandoc\pandoc.exe"` in that case. It covers `.doc`, `.odt`, `.rtf`, `.tex`, `.rst`, `.org`, `.typ`.
- **Source formats that work now:** PDF and `.ipynb` natively, `.docx` through mammoth, `.html` through markdownify, `.epub` through ebooklib, pasted text, and everything pandoc handles.
- **AI image generation needs API keys**, not just the packages: `google-genai` reads `GEMINI_API_KEY` / `GOOGLE_API_KEY`, `openai` reads `OPENAI_API_KEY`. Without a key, say the image step is unavailable instead of inventing images.
- **SVG to PNG fallback:** `svglib` + `reportlab` are installed; `cairosvg` is not, so gradients or filters may degrade in the Office-compatible path. Report that limitation when output looks flat.
- **Never `pip install` on your own.** Report the exact command and what it unlocks, then wait for permission.
- **The pipeline is serial with BLOCKING stops.** Those stops map to this repository's rule: present the recommendation, then use `ask_question` (or a numbered question) and wait for an explicit answer. Never decide for the user, never bundle phases, never pre-write content for a later phase.
- **No subagents.** Where the text mentions an Executor role or a separate generator, do it inline in this session; the repository has no subagent runtime for skill work.
- **Read `spec_lock.md` before each page**, as the text demands; it is the guard against drift after context compaction.
- **Output location:** one project folder per deck under `projects/<slug>/` in the working directory, not inside the skill folder.
- **Language:** talk to the user in their language (Vietnamese by default); slide copy follows the language of the brief, technical terms and file paths stay verbatim.

PPT Master is a routed presentation workflow. This entry owns global execution discipline and route selection only; each selected route owns its procedure.

## Mandatory Load Order

**Hard rule – paths before commands**: Retain the host-provided absolute
directory containing this file as `SKILL_DIR`. Per tool call, expand
`${SKILL_DIR}` and replace any `skills/ppt-master/` prefix with it. Never `cd`,
use CWD, or assume a repo checkout. If unavailable, ask; never search or guess.

1. Read this file.
2. Run `python3 "${SKILL_DIR}/scripts/attribution_guard.py"`. Any non-zero result
   stops the Skill immediately; do not inspect, repair, or bypass the integrity
   gate. On Windows, a `python3` that never starts (the WindowsApps stub exits
   9009 with no output) is not a guard result: rerun with `python` first.
3. Read [`workflows/routing.md`](workflows/routing.md) through the concrete
   absolute path `${SKILL_DIR}/workflows/routing.md`.
4. Select exactly one top-level route and its active profile from the routing
   authority.
5. Read only the resulting runtime authority and its explicitly triggered
   supporting documents.

| Selected route / profile | Runtime authority |
|---|---|
| Generate PPTX – Image to PPTX | [`workflows/profiles/image-to-pptx.md`](workflows/profiles/image-to-pptx.md); vision host, always Quick |
| Generate PPTX – Beautify | [`workflows/profiles/beautify-pptx.md`](workflows/profiles/beautify-pptx.md); explicit Quick intent selects Quick, otherwise Default |
| Generate PPTX – ordinary Default | [`workflows/generate-pptx.md`](workflows/generate-pptx.md) |
| Generate PPTX – ordinary explicit Quick | [`workflows/profiles/quick-generate.md`](workflows/profiles/quick-generate.md) |
| Create Template | [`workflows/create-template.md`](workflows/create-template.md) |
| Edit Native PPTX | [`workflows/edit-native-pptx.md`](workflows/edit-native-pptx.md) |

**Hard rule – selected authority only**: Do not load another top-level route's
procedure after routing. Image to PPTX and Beautify are mutually exclusive;
Image to PPTX activates Quick, while Beautify selects from explicit Quick
intent. Never load both runtimes. Supporting documents refine one route; they
never compete with it.

---

## Authored Expression Range

**Reference – not a constraint**: what a generated page can carry. Text – inline
emphasis runs, lead-in, kicker, pull quote, hero number, takeaway line. Geometry
– 187 Office presets, Boolean merge, connectors, freeform, page-field and
outline-carrier composition. Image – full-bleed field, editorial crop, shaped
picture, registered layers, scrim and spotlight, cross-page continuity. Paint –
gradients, channel alpha, native shadow and glow, halftone, faceted form.
Recurrence – one cross-page motif varied by page role. Each form's syntax lives
in the selected runtime authority's construction references.

---

## Vocabulary

One meaning per term across every loaded file. Where a word is used in
more than one sense, the sense is named here and the files say which one.

| Term | Meaning |
|---|---|
| **Reference** (label) | A starting sketch the executing role adjusts or replaces freely, with no upstream repair or stated reason; `(binding)` after a field label removes that freedom |
| **Relationships** | The §IX line naming a page's semantic units and their source-stated `order` / `link` / `parent` / `membership` / `contrast` / `overlap`, or `none` |
| **Topology decision** | The per-page yes/no on whether geometry must carry the page's `Relationships` (`topology=yes` / `topology=no`); unrelated to `pptx_structure.mode` |
| **`pptx_structure.mode`** | `flat` (every object Slide-local) or `structured` (declared Master/Layout/slot metadata); a packaging route, never information structure |
| **Composition** | The §IX `Composition` line: a Reference for a page's macro composition, hierarchy, and focus |
| **Image pattern** | The §VIII column carrying one image-composition suggestion in ordinary words (optionally citing `#P`/`#M` ids) |
| **Layout** | A PowerPoint Layout under a Master, or the Layout template kind; never a page-composition sketch |
| **Device** | An everyday page carrier – card, band, icon-and-label, KPI tile, divider, quote block – recalled in the Executor's device menu |
| **Carrier** | What a page unit sits in: a device, an image, or native geometry; the family names are carrier and field, direction and sequence, grouping and ownership, emphasis and annotation. `data-pptx-carrier` is a structured-slot attribute, not this term. The **carrier receipt** is the checker's per-page inventory of what was actually drawn |
| **Page job** | What one page must do for the reader; the input every carrier, contour, and effect decision is judged against |
| **Page field** | One large surface, outline, aperture, or off-canvas contour that organizes zones instead of a card per unit |
| **Contour / preset / atom** | A contour is a shape's silhouette; a preset is one of the 187 Office `prst` contours drawn through `preset_shape_svg.py`; an atom is one object that compiles to one DrawingML shape |
| **Geometry signature** | The retained line `page job → composition move → contour / edge language` kept per page and compared before the next page |
| **Texture** (of a block) | Whether a §IX block is prose, bullets, keywords, or labels; distinct from visual texture (grain, halftone) |
| **Anchor** | Two senses: a lock anchor (a deck-wide color, type, or spacing value) and the `page_rhythm` tag `anchor` for structural pages |
| **Sheet / slice / plate** | A sheet is one generated image holding several elements on a chroma key; a slice is one element cut from it; a plate is a registered full-canvas layer of several non-overlapping objects |
| **Module line** | The `P<NN> modules: ...` line written before each page naming the triggered modules it uses |
| **Mode** | Named by qualifier: communication `mode` (how the deck argues), reading mode (`consumption_mode`), `generation_mode` (`continuous` / `split`), `pptx_structure.mode`, `replication_mode` (how a template was created) |

## Phase Frame

Every route is one Plan → Do·Check·Act cycle: Plan ends when every authoring
input exists as a file or retained decision; Do authors pages, Check runs the
route's gates, Act repairs at the owning layer (discipline 7), and the cycle
ends at export. Step numbers stay as written.

| Phase | Default | Quick | Edit Native | Create Template |
|---|---|---|---|---|
| **Plan** | Steps 1–5 | §2 | §1–4 | Steps 1–3 |
| **Do·Check·Act** | Steps 6–7 | §3–4 | §5–7 | Steps 4–8 |

## Global Execution Discipline

1. **Serial execution** – Follow the selected authority's steps in order. A completed non-blocking step may continue directly to the next eligible step.
2. **Blocking means stop** – At every `⛔ BLOCKING` gate, wait for explicit user confirmation. Do not decide on the user's behalf.
3. **No cross-phase bundling** – Do not combine work across an unclosed gate. Once the route's final user gate closes, later non-blocking steps may continue automatically.
4. **Gate before entry** – Verify every listed prerequisite before entering a step.
5. **No speculative execution** – Do not prepare later-phase artifacts before their owning step.
6. **Deterministic routing** – Do not add a route-choice question when [`routing.md`](workflows/routing.md) resolves the request. If a route prerequisite is missing, state it and stop that route.
7. **Act at the owning layer** – On failure, repair at the shallowest layer that owns the fault: the page for a page-local issue, the Plan artifact for a roster/spec/resource fault, the owning source artifact for a tool failure; then resume from the route's declared pointer. Do not silently downgrade a required artifact.

## Global Communication Rules

- Match the user's language and source language unless the user explicitly overrides it.
- Localize user-facing option labels and explanations. Render each fixed message template (role-switch banner, completion report) in the user's chat language when it differs from the template's. Keep exact enum IDs or field names when needed for precision.
- Keep `design_spec.md` section headings and field names in the template's original English; content values may use the user's language.
- Before switching roles, read the corresponding role reference and output:

```markdown
## [Role Switch: <Role Name>]
📖 Reading role definition: references/<filename>.md
📋 Current task: <brief description>
```

---

## Repository Compatibility

- This package is a workflow/skill, not a generic application scaffold. Do not create `.worktrees/`, `tests/`, branch workflows, or generic engineering structure by default.
- Keep required workflow, reference, script, and template documentation inside this Skill directory.
- Repository-level documents may point into the package; package runtime files must not depend on repository-level instructions.
- On Windows, if a documented `python3 ...` command is unavailable, rerun the same command with `python`.
- Sponsor information is optional reference material. Read the matching [`SPONSORS.md`](SPONSORS.md) or [`SPONSORS_CN.md`](SPONSORS_CN.md) only when the user explicitly requests a model, AI image model, API/provider, or hosted-service recommendation. Never surface sponsor or model recommendations proactively during normal generation, troubleshooting, or quality review.
