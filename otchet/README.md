# otchet — Russian academic reports for Cline

A [Cline](https://cline.bot) skill that writes university reports **in Russian** for
any subject: ПР (практическая работа), лабораторная, реферат, курсовая,
отчёт по практике, НИР, МДП.

It reads the assignment, finds the variant, looks at the nearest sample report,
asks only for what is genuinely missing, writes the text in plain Russian, builds
the DOCX, exports the PDF through Microsoft Word, and validates the result before
handing it over.

**Languages:** [English](README.md) | [Русский](README.ru.md) | [Tiếng Việt](README.vi.md)

## What it does well

- **Any subject, any university.** Nothing is hard-coded: subject, chair, teacher,
  variant and structure come from the assignment or from you. LETI is only the
  default title page.
- **Follows the provided textbook to the letter.** Hand it a методичка and say
  nothing else: every requirement is implemented, including the «Рекомендации»
  section. *рекомендуется*, *следует*, *необходимо* are requirements, not advice.
- **Asks for the page count** on coursework and research work (30 / 50 / 70 or a
  custom number) and distributes it across chapters before writing anything.
- **Screenshots are opt-out.** Results, IDE windows, graphs and boards are captured
  and cropped to the useful area, then inserted as `Рис. N` with continuous
  numbering. Code is never a screenshot: it stays text, introduced by a lead-in
  sentence.
- **«Цель работы» cannot be lost.** `save_report(..., require_goal=True)` refuses to
  save a practical report without it, and `validate_docx.py` checks it afterwards.
- **Title page cloned from the бланк**, so it keeps Times New Roman 14 pt instead of
  being rescaled by the body preset.
- **PDF export leaves no Word behind**: `export_pdf_via_word()` reuses an already
  open Word, closes only its own session and waits for it to exit.
- **No VPN, no network services.** Everything runs locally; the model is whatever
  you configured in Cline.

## Requirements

| Requirement | Why |
|---|---|
| Cline (VS Code extension or Desktop) | runs the skill |
| Python 3.10+ (tested on 3.14) | scripts |
| `python-docx`, `lxml` | build the DOCX |
| `pypdf` | strip PDF metadata, check `/Link` annotations |
| `pypdfium2` | render and inspect PDF pages |
| `Pillow` | insert and check illustrations |
| Microsoft Word on Windows | PDF export, real TOC, `Fields.Update()` |
| Times New Roman | present on Windows |

```powershell
python -m pip install python-docx pypdf pypdfium2 lxml pillow
python scripts\check_env.py      # exit 0 means the environment is usable
```

Without Word you still get a DOCX, but no PDF and no real table of contents — the
skill says so before starting.

## Install

The skill lives in the `otchet` folder of the
[Cline-Skills](https://github.com/stoner-lab/Cline-Skills) repository. Copy that
folder into `%USERPROFILE%\.cline\skills\otchet`.

**Option 1 — sparse clone (only this skill):**

```powershell
git clone --depth 1 --filter=blob:none --sparse https://github.com/stoner-lab/Cline-Skills.git "$env:TEMP\cline-skills"
git -C "$env:TEMP\cline-skills" sparse-checkout set otchet
Copy-Item -LiteralPath "$env:TEMP\cline-skills\otchet" -Destination "$env:USERPROFILE\.cline\skills\otchet" -Recurse
```

**Option 2 — full clone, then copy:**

```powershell
git clone https://github.com/stoner-lab/Cline-Skills.git "$env:TEMP\cline-skills"
Copy-Item -LiteralPath "$env:TEMP\cline-skills\otchet" -Destination "$env:USERPROFILE\.cline\skills\otchet" -Recurse
```

**Option 3 — ZIP:** *Code → Download ZIP*, extract, move the `otchet` folder to
`%USERPROFILE%\.cline\skills\otchet`.

Restart Cline or start a new task afterwards so the skill list reloads.
`INSTALL.md` covers the folder overrides (`OTCHET_TEMPLATES`, `OTCHET_SKILL_DIR`)
and how relative paths resolve.

## Usage

```text
/otchet
```

or simply:

```text
Сделай ПР-3 по варианту 11, предмет «Статистический анализ», группа 3310
```

The skill asks for the missing pieces (name, group, teacher, deadline, where to
save) and, unless you say otherwise, writes section by section and waits for your
confirmation. Hand it a методичка and nothing else and it follows the textbook.

## How it works

1. reads the assignment, finds the variant, looks at a sample report;
2. checks numbers, units and decimal separators against the variant;
3. asks for what is missing — including the page count for long reports;
4. proposes an outline with a page budget;
5. writes the sections one at a time;
6. builds the DOCX with `scripts\docx_helpers.py`;
7. exports the PDF through Word;
8. runs `scripts\validate_docx.py` and compares the real page count with the target;
9. prints a compliance table: every textbook requirement → where it is met.

## Scripts

| Script | Role |
|---|---|
| `scripts\docx_helpers.py` | building blocks: title page, sections, tables, figures with captions, code blocks, PDF export |
| `scripts\validate_docx.py` | checks fonts, margins, spacing, captions, TOC, page numbers, title page against the template |
| `scripts\check_env.py` | lists every missing library, font or template with the command that fixes it |
| `scripts\selftest.py` | end-to-end self test on the bundled template |
| `scripts\strip_metadata.py` | removes author metadata from DOCX/PDF before delivery |
| `scripts\capture_window.ps1` | captures one application window to PNG, DPI aware, `-Crop` / `-CropPercent` |
| `scripts\crop_image.ps1` | crops an image by pixels or ratio, `-AutoTrim` strips uniform borders |

## Reference material

`references/format.md` (formatting and ГОСТ rules), `references/report-types.md`
(structure per report type), `references/checklist.md` (pre-delivery checklist),
`references/extraction.md` (reading the assignment and the sample),
`references/templates.md` (title page templates).

## Screenshots

A ПР-3 report built **entirely by the skill**, no manual editing. Names and group
numbers are masked. Images come from the PDF the skill exported.

<p align="center">
  <img src="assets/screenshots/pr3-cover-full.png" width="680" alt="Title page of a ПР-3 report">
</p>

## Honest limits

- It does not invent measurements or results: missing data is reported, not filled.
- Scanned PDFs and photographed pages need your eyes; the skill says what it cannot read.
- Formatting follows the assignment first, then the sample, then the built-in defaults.
- Built for Windows and PowerShell; Word is required for the PDF path.

## License

MIT — see [`LICENSE`](LICENSE). Part of the
[Cline-Skills](https://github.com/stoner-lab/Cline-Skills) collection.

