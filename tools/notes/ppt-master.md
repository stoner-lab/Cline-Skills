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
