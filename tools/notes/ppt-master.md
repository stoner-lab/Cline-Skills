## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\ppt-master\`; in the source repo: `E:\Private\Projects\Cline-Skills\ppt-master\`.
- **Scripts run from the skill directory** (`python scripts/...`). `run_commands` starts in the workspace, so prefix with a location change: `Set-Location "$env:USERPROFILE\.cline\skills\ppt-master"; python scripts/<name>.py ...`
- **Python 3.14 on PATH.** Present: `python-pptx`, `PyMuPDF`, `Pillow`, `numpy`, `reportlab`, `svglib`, `nbconvert`, `requests`, `beautifulsoup4`, `curl_cffi`.
- **Absent, so say so instead of failing late:** `mammoth` (.docx source), `markdownify` + `ebooklib` (.html/.epub source), `google-genai` and `openai` (AI image generation). `pandoc` is NOT installed, so `.doc`, `.odt`, `.rtf`, `.tex`, `.rst`, `.org` sources cannot be converted. PDF, native `.docx` (only after mammoth), `.ipynb` and pasted text do work.
- **Never `pip install` on your own.** Report the exact command, explain which source format or feature it unlocks, and wait for permission.
- **The pipeline is serial with BLOCKING stops.** Those stops map to this repository's rule: present the recommendation, then use `ask_question` (or a numbered question) and wait for an explicit answer. Never decide for the user, never bundle phases, never pre-write content for a later phase.
- **No subagents.** Where the text mentions an Executor role or a separate generator, do it inline in this session; the repository has no subagent runtime for skill work.
- **Read `spec_lock.md` before each page**, as the text demands; it is the guard against drift after context compaction.
- **Output location:** one project folder per deck under `projects/<slug>/` in the working directory, not inside the skill folder.
- **Language:** talk to the user in their language (Vietnamese by default); slide copy follows the language of the brief, technical terms and file paths stay verbatim.
