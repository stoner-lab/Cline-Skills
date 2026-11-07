## Cline runtime notes (read first)

- **Skill directory:** the folder that holds this `SKILL.md`. Installed: `C:\Users\<user>\.cline\skills\mcp-builder\`; in the source repo: `E:\Private\Projects\Cline-Skills\mcp-builder\`. Every relative path below resolves from there.
- **Tools:** `Read` / read_files tool -> `read_files`; `Write` / `editor` -> `editor`; `Edit` / `editor` -> `editor`; `Bash` / `run_commands` -> `run_commands` (PowerShell); search -> `search_codebase`; browser -> the Playwright MCP tools.
- **Shell is Windows PowerShell here.** `python` (not `python3`). Bash-only helpers are missing: `unzip` -> `Expand-Archive`, `zip` -> `Compress-Archive`; `pandoc`, `pdftoppm`, `soffice` and LibreOffice are not installed. Microsoft Word is available through COM (working pattern: `otchet/scripts/docx_helpers.py::export_pdf_via_word`).
- **Python packages installed:** python-docx, python-pptx, openpyxl, pypdf, pdfplumber, reportlab, lxml, pypdfium2, PyYAML. `pandas` is not installed - `pip install pandas` if a recipe needs it.
- **No subagents:** any instruction to spawn an agent or run things in parallel is executed inline, one step at a time.
- **Encoding:** all text files are UTF-8. The console code page mangles Vietnamese and Cyrillic, so write logs to a file and read them with `read_files` instead of trusting the terminal.
- **Language:** answer in the user's language (Vietnamese, Russian, English...); the deliverable stays in the language the task needs.
- **Verify visually** when the output has a layout: render to an image and look at it before claiming it is good.

- **Toolchain:** Python 3.14 and Node 24 are installed. `scripts/requirements.txt` lists the MCP SDK packages - install them before running `scripts/connections.py` or `scripts/evaluation.py`.
