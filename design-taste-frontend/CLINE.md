# Cline port of tasteskill

`design-taste-frontend` is the Cline copy of [tasteskill](https://github.com/Leonxlnx/taste-skill)
2.5.0 (`skills/taste-skill/` upstream, MIT, © 2026 Leonxlnx — see `LICENSE`). Everything the skill
ships works unchanged: `assets/`, `library/`, `references/` and every upstream script are upstream
bytes, and the scripts already find Chrome on Windows on their own.

## What differs from upstream

**1. `SKILL.md` is generated, never edited by hand.** `tools/sync_upstream.py apply
design-taste-frontend` rebuilds it from

- the upstream `SKILL.md` (body kept as written), and
- `tools/notes/design-taste-frontend.md` — the `## Cline runtime notes (read first)` block placed
  right after the H1: the absolute `<skill>` path, the tool mapping, `scripts/check_env.mjs`
  before the first page, "ask before installing anything", PowerShell instead of bash, the project
  folder layout, one script at a time, the checkers are never swapped for a browser tool, no
  subagents, the language rule, the report shape.

The frontmatter therefore carries Cline keys the upstream file does not have: `name`,
`description` (968 characters, Vietnamese and Russian triggers included), `license`,
`compatibility`, and `metadata.upstream` / `metadata.adaptation`. `adapt_config.json` adds one
`replacements` pair so the upstream sentence "`<skill>` is this folder" points at the notes
instead of at nothing.

**2. `scripts/check_env.mjs` (new, not upstream).** `node <skill>\scripts\check_env.mjs [--json]` —
Node 22+, a Chrome/Edge/Chromium (same candidate list as the checkers, `CHROME_PATH` first), the
37 kit files, `library/*.json` parsing, and ffmpeg as a warning only. Exit 1 on a missing required
item, with a fix list and the reminder to ask before installing. It changes nothing on disk.

**3. `CLINE.md` and the licence files.** This note, plus `LICENSE` and `CHANGELOG.md` copied
verbatim from upstream so the copy carries its licence and its history.

## What was deliberately left out

`install.sh` (a bash symlink/junction installer for `~/.claude/skills` and `~/.codex/skills`), the
agent plugin manifests (`.claude-plugin/`, `.codex-plugin/`, `.agents/`) and `tests/` — Cline reads
`~\.cline\skills\<name>\SKILL.md` directly, so a plain copied folder is enough. The README's
marketing sections, `examples/` and the screenshot WebPs describe the project, not the build.

## Updating from upstream

```powershell
python tools\sync_upstream.py check                       # upstream moved?
python tools\sync_upstream.py apply design-taste-frontend # regenerates SKILL.md only
```

`apply` never copies the other upstream files, so an update that adds or moves a kit file shows up
as `WARNING: upstream has files not copied here`. Copy them by hand, then run
`node design-taste-frontend\scripts\check_env.mjs` — it is the fastest way to catch a kit file the
port expects and upstream renamed.

After regenerating, refresh the installed copy and restart the task:

```powershell
robocopy E:\Private\Projects\Cline-Skills\design-taste-frontend C:\Users\duy\.cline\skills\design-taste-frontend /MIR /NFL /NDL /NJH /NJS
```

Smoke test before trusting a fresh copy (no browser needed):

```powershell
node <skill>\scripts\start.mjs deal --page software --history .taste-skill\history.json
```
