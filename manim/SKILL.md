---
name: manim
description: "Build math/physics/CS animations with Manim Community Edition in Python – Scenes and Mobjects, timed animations, LaTeX/MathTex equation morphs, graphs and ValueTracker updaters, 3D scenes and moving camera – then render to MP4/GIF from the CLI with a render-a-frame-first verify loop. Trigger when the user asks to make a math animation, animate an equation or formula, morph one formula into another, plot or animate a graph/function, trace a dot along a curve, animate a geometric proof, build a 3Blue1Brown-style explainer, or visualize a math/physics/CS concept as a video. Also trigger on Vietnamese \"làm video minh họa toán\", \"animate công thức\", \"vẽ đồ thị động\", \"dựng cảnh 3D\", \"xuất MP4/GIF từ Python\" and Russian «анимация формулы», «анимировать график», «ролик в стиле 3Blue1Brown», «визуализировать теорему». Not for UI motion, Remotion/social video, or CSV business charts."
license: MIT
compatibility: "Cline on Windows (verified here with Manim CE 0.22.1, Python 3.14, ffmpeg 7.x, MiKTeX 26.5). All shell steps use run_commands/PowerShell; stills are inspected with read_files. The upstream bash helpers are ported to PowerShell in scripts/."
metadata:
  version: "0.2.0"
  upstream: "https://github.com/iart-ai/manim-skills"
  adaptation: "Cline/Windows port: bash to PowerShell, python -m manim, media-path discovery, UTF-8 and CJK/Cyrillic font pitfalls, output probing"
---

# Manim (Programmatic Math Animation)

Manim (Mathematical Animation Engine, Community Edition) renders explanatory math/physics/CS videos from Python – the engine behind 3Blue1Brown-style motion. Every scene is declarative: you build vector objects, play timed animations over them, and render a deterministic MP4/GIF from the CLI. Best-in-class for moving equations, transforming formulas, animated graphs, and geometric intuition.

## Cline runtime notes (read first)

- **Skill folder:** `C:\Users\duy\.cline\skills\manim`. Invoke explicitly with `/manim`, or the `skills` tool (`skill: "manim"`). Never write scenes inside the skill folder – it is read as documentation only.
- **Tools:** shell -> `run_commands` (PowerShell 7), read -> `read_files`, write/edit -> `editor`, search -> `search_codebase`. Any `bash`, `Read`, `Write`, `grep` in the upstream text means that Cline equivalent.
- **Call Manim as `python -m manim`.** The `manim.exe` shim lives in `C:\Users\duy\AppData\Roaming\Python\Python314\Scripts` and is not on PATH; `python -m manim` always works on this machine.
- **One folder per clip** inside the user's project, e.g. `<project>\anim\<clip>\scene.py`. Manim writes `media/` next to the script, so the folder stays self-contained and re-renderable.
- **Quote every path.** Workspace paths here contain spaces and Cyrillic (`...\Cognitio\3\3.1\СтатАн`). Use `Push-Location` / `Pop-Location`, `-LiteralPath`, and double quotes around arguments.
- **Capture command output through a file.** Terminal echo through shell integration is unreliable here:
  `python -m manim -ql -s scene.py MyScene *> out.txt; Get-Content out.txt -Tail 20`
- **Write source files as UTF-8.** `editor` does it; with PowerShell use `Set-Content -LiteralPath x.py -Encoding utf8`. Cyrillic/Vietnamese labels mojibake otherwise.
- **Inspect stills with `read_files`** on the PNG path – it renders images to you. Do not judge a frame from the log text alone.
- **Answer the user in Vietnamese** (their standing preference); keep Manim API names and code in English.
- There are no subagents or hooks: run the verify loop inline, yourself.

## Setup & render (verified on this machine)

```powershell
python -m manim --version        # Manim Community v0.22.1
python -m manim -pql scene.py SquareToCircle   # render one Scene, low quality, preview
```

If it is missing: `python -m pip install manim` (needs Python 3.9+, ffmpeg, and a LaTeX distribution for `Tex`/`MathTex`; MiKTeX and ffmpeg are already installed here). `python -m pip install "manim[gui]"` only if the user wants the interactive GUI.

Render flags that matter:
- `-q l|m|h|k` – quality: low (fast iteration) -> 4K. `-ql` while building, `-qh` to ship.
- `-p` – play when done; `-o name` – output filename; `--format=gif` – render a GIF.
- `-s` – **save the last frame as a PNG** (no video encode – the verification lever, see below).
- `-n a,b` – render only animation index range `a..b` (stop early to inspect a moment).
- `-r 1920,1080` – frame size; `--fps 60` – frame rate.

**Output paths (Windows, Manim 0.22):**

| What | Where |
|---|---|
| Video | `media\videos\<script>\<480p15\|720p30\|1080p60\|2160p60>\<Scene>.mp4` |
| Still (`-s`) | `media\images\<script>\<Scene>_ManimCE_v0.22.1.png` – **version suffix**, never hardcode it |
| Still with `-o name` | `media\images\<script>\name.png` – no suffix; `-o` also renames the MP4 |
| LaTeX cache | `media\Tex\` – safe to delete to force re-typeset |

**`-s` without `-o` overwrites itself.** The default still name comes from the Scene, so a second verification run replaces the PNG and the earlier frame is gone. Always pass `-o f-start` / `-o f-mid` / `-o f-end` when you need more than one still (verified here: `-s ... -o mid` -> `mid.png`).

Find the newest artifact instead of guessing:

```powershell
Get-ChildItem -LiteralPath .\media -Recurse -File -Include *.mp4, *.png |
    Sort-Object LastWriteTime | Select-Object -Last 1 FullName, Length
```

## The three building blocks

Everything is **Scenes** (orchestration) acting on **Mobjects** (objects) via **Animations** (timed change).

```python
from manim import *


class SquareToCircle(Scene):
    def construct(self):                 # ALL animation code lives in construct()
        sq = Square().set_fill(BLUE, opacity=0.5)
        self.play(Create(sq))            # animate it drawing on
        self.play(sq.animate.rotate(PI / 4))
        self.play(Transform(sq, Circle().set_fill(PINK, opacity=0.5)))
        self.wait(0.5)                   # hold
```

**Mobjects** – vector objects (`Circle`, `Square`, `Rectangle`, `Line`, `Dot`, `Polygon`, `Axes`, `Text`, `MathTex`).
- Position: `.shift(UP*2)` (relative), `.move_to(ORIGIN)` (absolute), `.next_to(other, RIGHT, buff=0.5)`, `.align_to(other, LEFT)`. Directions are constants: `UP DOWN LEFT RIGHT ORIGIN UL UR DL DR`.
- Style: `.set_fill(color, opacity)`, `.set_stroke(color, width)`, `.set_color(YELLOW)`. Colors: `BLUE RED GREEN YELLOW WHITE` + `BLUE_E`, etc.
- `self.add(m)` shows instantly (no animation); `self.remove(m)`. Later-added objects render on top.

**Animations** – interpolate a mobject's state over `run_time` seconds (default 1s).
- Construction: `Create`, `Write` (for text/Tex), `DrawBorderThenFill`, `FadeIn`, `FadeOut`, `GrowFromCenter`.
- Change: `Transform(a, b)` (morph a into b, keep a), `ReplacementTransform(a, b)` (swap a for b), `Rotate`, `Indicate`, `Circumscribe`, `Wiggle`.
- **`.animate` syntax** – animate any method call: `self.play(sq.animate.shift(UP).set_fill(RED))`. Chains apply together.
- Play several at once: `self.play(Create(a), FadeIn(b), run_time=2)`.

**Timing & easing** – `run_time=` sets duration; `rate_func=` sets the easing curve (`smooth` is the default – ease-in-out; also `linear`, `rush_into`, `rush_from`, `there_and_back`, `ease_out_bounce`). Stagger a group with `LaggedStart(*anims, lag_ratio=0.2)`. Slow *starts* read worse than slow ends; reserve `linear` for loops.

## Math, text & equations

`Text`/`MarkupText` (Pango, no LaTeX) for labels; `Tex`/`MathTex` (LaTeX, raw strings) for typeset math. Animate equations with `Write` and morph between them with `TransformMatchingTex`. Full recipes – substring coloring, `{{ }}` isolation, term-by-term transforms, LaTeX preamble – in `references/math-and-text.md`.

## Graphs, plotting & updaters

`Axes` + `ax.plot(lambda x: ...)` for functions; `ax.c2p(x, y)` maps math coords -> screen. Drive live values with `ValueTracker` + `always_redraw`/`add_updater` so dependent mobjects recompute every frame (a dot riding a curve, a counter, a moving tangent). See `references/graphs-and-updaters.md`.

## 3D & moving camera

`ThreeDScene` + `set_camera_orientation(phi=, theta=)`, `ThreeDAxes`, `Surface`, `begin_ambient_camera_rotation()`; `MovingCameraScene` + `self.camera.frame.animate...` for 2D camera pushes/follows. See `references/3d-and-camera.md`.

## Deliver & verify (rendered frame -> MP4)

Manim is deterministic – the same scene renders the same frames – so verify by rendering **frames** (PNG, no video encode) before committing to the full video. Use this whenever the output is a math clip MP4/GIF.

**Output contract:**
- One `.py` with one `Scene` (or `ThreeDScene`) subclass per clip; all motion inside `construct()`. Deliverable = the re-runnable script plus the rendered `media\videos\...\<Scene>.mp4`.
- Raw strings (`r"..."`) for every `Tex`/`MathTex`; LaTeX installed.
- Report the absolute path of the MP4 and its real spec (probe it, do not assume).

**`-s` ignores `-n`.** Verified on Manim 0.22.1: `-s -n 0,1`, `-s -n 0,3` and `-s` alone produced byte-identical PNGs – `-s` always saves the *last* frame of the whole scene, so the upstream "stop after animation N" trick does not work here. To see a mid moment, render a cheap `-ql` preview and let ffmpeg pull frames at chosen timestamps: `scripts\grab-frames.ps1` does exactly that.

**Verify loop – render frames -> inspect -> encode video:**

```powershell
Push-Location .\anim\pythagoras          # the clip folder with scene.py
# 1. End frame as a PNG (no video encode – fastest single check)
python -m manim -ql -s scene.py Proof -o f-end
# 2. Real start/mid/end stills: renders a cheap -ql preview, then ffmpeg grabs frames
& "C:\Users\duy\.cline\skills\manim\scripts\grab-frames.ps1" scene.py Proof
#    -> f-5.png  f-50.png  f-95.png   (timeline percentages; -Percent 0,40,100 to tune)
# 3. Tile them into one image, then open that sheet with read_files
& "C:\Users\duy\.cline\skills\manim\scripts\contact-sheet.ps1" sheet.png .\f-5.png .\f-50.png .\f-95.png
# 4. Only once the frames look right, encode the video
python -m manim -qh scene.py Proof                       # MP4, 1080p60
python -m manim -qm scene.py Proof --format=gif          # GIF demo
Pop-Location
```

**Bundled helpers** (PowerShell, run with `&`):

```powershell
$manim = "C:\Users\duy\.cline\skills\manim"
& "$manim\scripts\manim-env-check.ps1"                          # python / manim / ffmpeg / latex / dvisvgm
& "$manim\scripts\grab-frames.ps1" scene.py Proof                # -ql preview -> f-5 / f-50 / f-95 PNGs
& "$manim\scripts\contact-sheet.ps1" sheet.png f-5.png f-50.png f-95.png
& "$manim\scripts\probe-mp4.ps1" .\media\videos\scene\1080p60\Proof.mp4 1920x1080 60
```

Tiling start | mid | end into one `sheet.png` beats flipping between three files – read the sheet with `read_files`, then judge fidelity.

**Before you finish:**
1. `grab-frames.ps1` runs clean at 5% / 50% / 95% – no LaTeX errors, no missing-glyph boxes, no traceback.
2. Equations/labels are mathematically correct and fully inside the frame (nothing clipped at edges).
3. No overlap between mobjects at the inspected frames; `next_to`/`arrange` used instead of hand-guessed coords.
4. Timing reads well – `run_time`/`rate_func` intentional, `self.wait()` holds on key states, groups staggered not simultaneous.
5. Full MP4 encodes, `probe-mp4.ps1` reports the expected resolution/fps/duration, and the file plays.

## Quick reference

| Need | Use |
|---|---|
| New animation | `class S(Scene): def construct(self): ...` |
| Show instantly / animate on | `self.add(m)` / `self.play(Create(m))` |
| Animate a method | `self.play(m.animate.shift(UP))` |
| Morph / replace | `Transform(a,b)` / `ReplacementTransform(a,b)` |
| Typeset math | `MathTex(r"e^{i\pi}+1=0")`, animate with `Write` |
| Morph equations | `TransformMatchingTex(eq1, eq2)` |
| Plot a function | `ax=Axes(...); ax.plot(lambda x: x**2)` |
| Live/linked value | `ValueTracker` + `always_redraw(...)` |
| Position relative | `m.next_to(other, RIGHT, buff=0.3)` |
| Duration / easing | `self.play(a, run_time=2, rate_func=smooth)` |
| Stagger a group | `LaggedStart(*anims, lag_ratio=0.2)` |
| Render / inspect / gif | `python -m manim -qh f.py S` / `-ql -s -n a,b` / `--format=gif` |

## Gotchas

- **LaTeX is required** for `Tex`/`MathTex` (not for `Text`). A missing-glyph box or compile error = LaTeX not installed or a bad TeX string. Always use raw strings `r"..."`.
- **MiKTeX may stall on a missing package.** If the run freezes at `tex_file_writing.py` before the first frame, MiKTeX is waiting on an install prompt that `run_commands` cannot answer. Fix outside the render: `miktex packages install <package>` (or set auto-install to "yes" in the MiKTeX console), then re-run. Same symptom after a fresh `\usepackage{...}` in a `TexTemplate` preamble.
- **LaTeX cache hides bad edits** only rarely, but a corrupted cache does break renders: delete `media\Tex\` to force a re-typeset.
- `Transform(a, b)` mutates `a` to look like `b` (and `b` is not added); `ReplacementTransform(a, b)` leaves `b` on screen – pick based on which object you keep referencing after.
- `.animate` interpolates start->end states, so it can take odd paths for rotations/some transforms; use a dedicated animation (`Rotate`) when the path matters.
- Updaters added with `add_updater` keep running – `mob.clear_updaters()` (or `remove_updater`) when done, or later animations fight the updater.
- Don't hand-guess coordinates; compose with `next_to`, `arrange`, `VGroup(...).arrange(DOWN)`, and `ax.c2p()` so layout survives edits.
- `construct()` runs once to *script* the timeline; there is no realtime loop – never use wall-clock time or randomness without a seed.
- **PowerShell, not bash:** `cp -r`, `rm -rf`, `nohup`, `$!`, `&&` are not commands here. Use `Copy-Item`, `Remove-Item -Recurse -Force`, `;`. Prefer the absolute `ffmpeg`/`ffprobe` on PATH.
- **Cyrillic/Vietnamese labels:** `Text("Теорема Пифагора")` usually falls back to a Pango font that has the glyphs, but verify in the still. If boxes appear, pin a font that exists on this machine: `Text(..., font="Segoe UI")` or `font="DejaVu Sans"`. `MathTex` cannot typeset Cyrillic unless you load a Cyrillic-capable TeX font – use `Text` for prose.
- **Do not `-p` (preview) in automation** – it opens a player and blocks. Omit `-p` in `run_commands`.
- Long renders: `-ql` for iteration, and `-n a,b` to re-render one stretch instead of the whole scene.

## Reference files

- `references/math-and-text.md` – Text vs MarkupText vs Tex vs MathTex, raw strings, substring coloring (`set_color_by_tex`, `substrings_to_isolate`, `{{ }}`), `TransformMatchingTex` term morphs, and LaTeX preamble/packages.
- `references/graphs-and-updaters.md` – `Axes`/`NumberPlane`, `plot`, `get_area`, `c2p`/`p2c`, `ValueTracker`, `always_redraw`, `add_updater`, a dot tracing a curve, animated counters, tangent/secant.
- `references/3d-and-camera.md` – `ThreeDScene`, `set_camera_orientation`, `ThreeDAxes`, `Surface`/parametric, ambient rotation, `MovingCameraScene` pushes/follows.
- `references/cline-windows.md` – this adaptation in detail: verified toolchain versions, paths, PowerShell recipes, per-failure troubleshooting table.

Adapted from [iart-ai/manim-skills](https://github.com/iart-ai/manim-skills) (MIT). Upstream `contact-sheet.sh` / `probe-mp4.sh` are ported to PowerShell in `scripts\`; the marketing footers of the upstream files were dropped.


