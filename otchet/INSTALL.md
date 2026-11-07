# Installation and portability

## Requirements

- Cline extension in VS Code
- An AI API configured in Cline (OpenAI, Anthropic, OpenRouter, Google, etc.)
- Python 3.10+
- `python-docx`
- Optional: `pypdfium2` for PDF page checks
- Optional: Microsoft Word on Windows for PDF export

```powershell
python -m pip install python-docx pypdfium2
```

## Option 1: global Cline skill

The skill is the `otchet` folder inside the Cline-Skills repository. Clone only that
folder and copy it to the global skill directory:

```powershell
git clone --depth 1 --filter=blob:none --sparse https://github.com/stoner-lab/Cline-Skills.git "$env:TEMP\cline-skills"
git -C "$env:TEMP\cline-skills" sparse-checkout set otchet
Copy-Item -LiteralPath "$env:TEMP\cline-skills\otchet" -Destination "$HOME\.cline\skills\otchet" -Recurse
```

Cline also scans `%USERPROFILE%\.agents\skills`, so either global location works:

```powershell
Copy-Item -LiteralPath "$env:TEMP\cline-skills\otchet" -Destination "$HOME\.agents\skills\otchet" -Recurse
```

If you downloaded a ZIP instead, extract it and copy the `otchet` folder to the same place.

## Option 2: workspace skill

Copy the same folder into the project:

```text
<project>\.cline\skills\otchet
<project>\.agents\skills\otchet
```

Cline scans both workspace locations.

## Relative paths

- `scripts/docx_helpers.py` resolves templates as
  `<otchet>/assets/templates/` using `Path(__file__)`.
- Override the template folder when needed:

```powershell
$env:OTCHET_TEMPLATES = "D:\my-templates"
```

- Override the skill folder for imports:

```powershell
$env:OTCHET_SKILL_DIR = "D:\skills\otchet"
```

## Quick test

From the `otchet` folder:

```powershell
python -c "import sys; sys.path.insert(0, 'scripts'); from docx_helpers import title_template_path; print(title_template_path(), title_template_path().exists())"
python scripts/validate_docx.py path\to\report.docx --pdf path\to\report.pdf
```

## GitHub notes

- `assets/templates/title_page_leti.docx` is a clean generated reference with no
  personal data. Replace it if your institution has a different title page.
- Do not commit real reports containing student names.
- `.gitattributes` marks DOCX/DOC/PDF as binary.
- `.gitignore` excludes generated reports, PDFs and `__pycache__`.
