# Cline / Windows adaptation notes

What was changed from [iart-ai/manim-skills](https://github.com/iart-ai/manim-skills) (upstream `skills/manim/`, MIT) so the skill actually runs as a Cline skill on this machine, plus the traps that bite here. Read this when a step in `SKILL.md` fails.

## Verified toolchain (this machine, checked at adaptation time)

| Piece | Version / path | Note |
|---|---|---|
| Python | 3.14.4 (`python` on PATH) | `python -m manim` is the reliable entry point |
| Manim CE | 0.22.1 | `manim.exe` lives in `C:\Users\duy\AppData\Roaming\Python\Python314\Scripts`, **not** always on PATH |
| ffmpeg / ffprobe | 7.x, `C:\ffmpeg\...\bin` on PATH | needed for encoding and `probe-mp4.ps1` |
| LaTeX | MiKTeX-pdfTeX 4.27 (MiKTeX 26.5) | `dvisvgm` present; required by `Tex`/`MathTex` |
| dvisvgm | on PATH | converts the dvi to the SVG Manim strokes |
| uv | 0.11.21 | optional; use `uv pip install manim` for an isolated env |
| git | 2.53 | only relevant when re-syncing upstream |

## Changes from upstream

1. **Frontmatter.** Kept `name: manim`; rewrote `description` to include Vietnamese and Russian trigger phrases and an explicit boundary (not UI motion / Remotion / CSV charts). Added `license`, `compatibility`, `metadata` with `upstream` and `version`. Required by the Cline loader: one YAML block, `name` + `description` only.
2. **Added "Cline runtime notes".** Tool mapping (`run_commands`/`read_files`/`editor`/`search_codebase`), skill folder path, invocation, and the "answer in Vietnamese" preference.
3. **All shell is PowerShell.** Upstream `bash` blocks became PowerShell: `Push-Location`/`Pop-Location`, `Get-ChildItem -LiteralPath`, `*>` redirection, `&` call operator. `manim ...` became `python -m manim ...` everywhere.
4. **Scripts ported + one added.** `scripts/contact-sheet.sh` -> `scripts/contact-sheet.ps1`; `scripts/probe-mp4.sh` -> `scripts/probe-mp4.ps1`; new `scripts/grab-frames.ps1` replaces the broken upstream "mid frame" trick; new `scripts/manim-env-check.ps1` verifies the toolchain. `scripts/seek-shot.sh` was dropped – it drives an HTML `?t=N` harness for the web-animation packs, irrelevant to Manim.
5. **Corrected the verify loop.** Upstream says `manim -sql scene.py Scene -n 0,3` (with `-n a,b`) which "stops after animation N". On Manim 0.22.1 `-s` ignores `-n` entirely: `-s -n 0,1`, `-s -n 0,3` and plain `-s` all wrote byte-identical PNGs (MD5-checked). The reliable way to inspect a mid moment is to render a `-ql` preview and let ffmpeg extract frames by timestamp – that is what `grab-frames.ps1` does, and the frames it produces at 5/50/95 % are visibly different for a real scene.
6. **Media paths documented** for Manim 0.22 on Windows, including that stills are named `<Scene>_ManimCE_v0.22.1.png` – the version suffix means you must discover the file, not hardcode it.
7. **Gotchas section extended** with Windows-specific items (MiKTeX prompts, PowerShellisms, Cyrillic/Vietnamese fonts, no `-p` in automation) and the upstream marketing footers were removed.

## Running the helpers

```powershell
$manim = "C:\Users\duy\.cline\skills\manim"
& "$manim\scripts\manim-env-check.ps1"
& "$manim\scripts\grab-frames.ps1" scene.py Proof -Percent 5,50,95 -OutDir frames
& "$manim\scripts\contact-sheet.ps1" sheet.png frames\f-5.png frames\f-50.png frames\f-95.png
& "$manim\scripts\probe-mp4.ps1" .\media\videos\scene\1080p60\Scene.mp4 1920x1080 60
```

Scripts take positional arguments (same order as the bash originals) so they stay copy-pasteable from the docs. Exit codes: `0` ok, `1` assertion failed, `2` missing input/tool.

Relative paths inside the scripts are resolved through the PowerShell provider (`Resolve-Path`, `$PWD.ProviderPath`), not `[System.IO.Path]::GetFullPath` – the latter resolves against the .NET process directory, which does **not** follow `Push-Location` and silently loads the wrong folder.

## Troubleshooting table

| Symptom | Cause | Fix |
|---|---|---|
| `'manim' is not recognized` | shim folder not on PATH | use `python -m manim ...` |
| Render hangs at `tex_file_writing.py` | MiKTeX waiting on a package install | `miktex packages install <pkg>`, or enable auto-install in the MiKTeX console, retry |
| `FileNotFoundError: latex` / blank boxes instead of glyphs | no LaTeX engine or bad TeX string | run `manim-env-check.ps1`; fix raw strings |
| Cyrillic/Vietnamese shows as boxes | no glyphs in the default Pango font | `Text(..., font="Segoe UI")`; use `Text`, not `MathTex`, for prose |
| `mojibake` text in the scene | `.py` written in ANSI code page | rewrite with `Set-Content -Encoding utf8` (or `editor`) |
| `-s` "produced nothing" | looked for a fixed filename | glob `media\images\*\*.png`, newest by `LastWriteTime` |
| two stills are byte-identical | `-s` ignores `-n` | use `grab-frames.ps1` (ffmpeg timestamp grab) instead of `-s -n a,b` |
| stills land in the workspace root instead of the clip folder | a script resolved relative paths with `GetFullPath` | use `Resolve-Path` / `$PWD.ProviderPath`; the bundled scripts already do |
| MP4 exists but plays black / 0 bytes | encode killed early or player opened with `-p` | drop `-p`, re-run, then `probe-mp4.ps1` |
| Command output lost in the terminal | shell integration | redirect to a file: `... *> out.txt; Get-Content out.txt -Tail 30` |
| Path with spaces/Cyrillic breaks | unquoted argument | quote it, use `-LiteralPath` |

## Known limits

- No subagents and no hooks in Cline: the verify loop runs inline, one render at a time.
- No live preview channel: judge frames from saved PNGs via `read_files` (or Playwright MCP if a GIF/HTML preview is needed).
- `manim[gui]` / interactive `--gui` mode is not usable from `run_commands` (it blocks on a window).
