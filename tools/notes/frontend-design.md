## Cline runtime notes (read first)

- **Skill directory:** the folder that holds this `SKILL.md`. Installed: `C:\Users\<user>\.cline\skills\frontend-design\`; in the source repo: `E:\Private\Projects\Cline-Skills\frontend-design\`. Every relative path below resolves from there.
- **Tools:** `Read` / read_files tool -> `read_files`; `Write` / `editor` -> `editor`; `Edit` / `editor` -> `editor`; `Bash` / `run_commands` -> `run_commands` (PowerShell); search -> `search_codebase`; browser -> the Playwright MCP tools.
- **Shell is Windows PowerShell here.** `python` (not `python3`). Bash-only helpers are missing: `unzip` -> `Expand-Archive`, `zip` -> `Compress-Archive`; `pandoc`, `pdftoppm`, `soffice` and LibreOffice are not installed. Microsoft Word is available through COM (working pattern: `otchet/scripts/docx_helpers.py::export_pdf_via_word`).
- **Python packages installed:** python-docx, python-pptx, openpyxl, pypdf, pdfplumber, reportlab, lxml, pypdfium2, PyYAML. `pandas` is not installed - `pip install pandas` if a recipe needs it.
- **No subagents:** any instruction to spawn an agent or run things in parallel is executed inline, one step at a time.
- **Encoding:** all text files are UTF-8. The console code page mangles Vietnamese and Cyrillic, so write logs to a file and read them with `read_files` instead of trusting the terminal.
- **Language:** answer in the user's language (Vietnamese, Russian, English...); the deliverable stays in the language the task needs.
- **Verify visually** when the output has a layout: render to an image and look at it before claiming it is good.

- **No scripts.** This skill is guidance; the deliverable is code you write or a critique you give. Render the result and look at it before calling it done.


Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliché or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.
