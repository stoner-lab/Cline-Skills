# manim – Cline skill

Build math/physics/CS animations with **Manim Community Edition** in Python and render
them to MP4/GIF from the CLI: equations that write on and morph term-by-term, plotted
functions with a dot riding the curve, animated proofs, 3D surfaces with an orbiting
camera – 3Blue1Brown-style explainers, scripted.

This is a Cline/Windows adaptation of [iart-ai/manim-skills](https://github.com/iart-ai/manim-skills)
(MIT). The method (Scenes -> Mobjects -> Animations, render-a-frame-first verification)
is unchanged; the mechanics were ported to this runtime.

## Install

Cline reads skills from `C:\Users\<user>\.cline\skills\<skill-name>\`. This skill ships in the
[Cline-Skills](https://github.com/stoner-lab/Cline-Skills) collection, folder `manim/`.

```powershell
git clone --depth 1 https://github.com/stoner-lab/Cline-Skills.git "$env:TEMP\cline-skills"
Copy-Item -Recurse "$env:TEMP\cline-skills\manim" "$env:USERPROFILE\.cline\skills\manim"
```

Then start a new task (or restart VS Code) so Cline picks up the new `SKILL.md`.
Invoke it with `/manim <what to animate>`, or just ask for a math animation.

## Requirements

| Piece | Why | Check |
|---|---|---|
| Python 3.9+ | runs Manim | `python --version` |
| Manim CE | the engine | `python -m manim --version` |
| ffmpeg / ffprobe | encodes MP4, grabs frames | `ffmpeg -version` |
| LaTeX + dvisvgm | only for `Tex` / `MathTex` | `latex --version` |

```powershell
python -m pip install manim
& "$env:USERPROFILE\.cline\skills\manim\scripts\manim-env-check.ps1"
```

## What it contains

| Path | Purpose |
|---|---|
| `SKILL.md` | the skill itself: runtime notes, building blocks, verify loop, gotchas |
| `references/math-and-text.md` | Text vs MarkupText vs Tex vs MathTex, substring colouring, `TransformMatchingTex` |
| `references/graphs-and-updaters.md` | `Axes`, `plot`, `c2p`, `ValueTracker`, `always_redraw`, tangents |
| `references/3d-and-camera.md` | `ThreeDScene`, `Surface`, ambient rotation, `MovingCameraScene` |
| `references/cline-windows.md` | the adaptation in detail + troubleshooting table |
| `scripts/manim-env-check.ps1` | verifies python / manim / ffmpeg / latex / dvisvgm |
| `scripts/grab-frames.ps1` | renders a `-ql` preview and grabs stills at chosen timeline percentages |
| `scripts/contact-sheet.ps1` | tiles stills side-by-side into one review image |
| `scripts/probe-mp4.ps1` | prints and asserts the encoded MP4's real resolution / codec / fps / duration |

## Verify loop

```powershell
python -m manim -ql -s scene.py Proof -o f-end                 # end frame, no encode
& "$env:USERPROFILE\.cline\skills\manim\scripts\grab-frames.ps1" scene.py Proof
& "$env:USERPROFILE\.cline\skills\manim\scripts\contact-sheet.ps1" sheet.png f-5.png f-50.png f-95.png
python -m manim -qh scene.py Proof                             # ship it
& "$env:USERPROFILE\.cline\skills\manim\scripts\probe-mp4.ps1" .\media\videos\scene\1080p60\Proof.mp4 1920x1080 60
```

## Changes vs upstream

- bash -> PowerShell everywhere; `manim` -> `python -m manim` (the shim is not always on PATH).
- `contact-sheet.sh` / `probe-mp4.sh` ported to PowerShell; `seek-shot.sh` dropped (HTML harness, irrelevant here).
- New `grab-frames.ps1`: upstream's `-s -n a,b` "mid frame" recipe does **not** work – `-s` ignores `-n` and always saves the final frame (verified byte-identical PNGs on Manim 0.22.1).
- New `manim-env-check.ps1`; plus notes on MiKTeX prompts, UTF-8 source files, Cyrillic/Vietnamese fonts, and media path discovery.
- Frontmatter rewritten with Vietnamese/Russian trigger phrases and an explicit "not for UI motion / Remotion / CSV charts" boundary.

## License

MIT – see `LICENSE`. Upstream © iart.ai (`github.com/iart-ai/manim-skills`); this adaptation keeps the same license.
