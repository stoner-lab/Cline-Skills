# Cline adaptation of `impeccable`

Source: https://github.com/pbakaus/impeccable (`skill/` + built `.claude/skills/impeccable`),
version 4.8.0, Apache 2.0. Installed at `C:\Users\duy\.cline\skills\impeccable`.

## What was copied

- `SKILL.md`, `reference/**` (41 playbooks incl. `degraded/`), `scripts/**`
  (launchers, `command-metadata.json`, `data/font-index.json`), `VERSION`.
- Not copied: `.claude/agents/*` (subagent prompts), plugin manifests, CLI/extension
  sources — Cline has no subagents and does not need the extension.

## Changes

1. **Frontmatter** reduced to keys Cline accepts: `name`, `description`, `license`,
   `compatibility`, `metadata{version, upstream, adaptation}`. The Claude-only fields
   (`user-invocable`, `argument-hint`, top-level `version`) were removed; the version
   now lives in `metadata.version` and is still read by the engine.
2. **Description** kept the upstream trigger list and added Vietnamese and Russian
   phrasing (`làm đẹp giao diện`, `sửa UI`, `thiết kế lại trang`, `review giao diện`,
   `улучшить интерфейс`, `сделать красиво`) so the skill fires for non-English users.
3. **Paths**: every `.claude/skills/impeccable` reference in `SKILL.md` and
   `reference/*.md` (17 files, 72 places) now points at
   `C:\Users\duy\.cline\skills\impeccable`, and the Windows launcher is spelled out.
4. **New section "Cline runtime notes"** in `SKILL.md`: invocation as
   `/impeccable <command> [target]`, tool mapping, launcher fallback, no subagents
   (use `reference/degraded/*.md`), no hooks (run the detector manually), no live
   browser channel (use Playwright MCP or user screenshots), answer in the user's
   language, UTF-8 everywhere, no unverified visual claims.

## Verified on this machine

```
impeccable.cmd --version   -> 4.8.0
impeccable.cmd help        -> command table
impeccable.cmd context     -> PRODUCT_INIT_REQUIRED / MANUAL_DETECTOR_REQUIRED directives
impeccable.cmd detect --json index.html -> []  (exit 0)
```

`context` itself tells the model to run the detector manually when no hook is
active, which is exactly the Cline situation — no extra wiring needed.

## Known limits

- `live` and the interactive `generate` mode rely on the browser extension; in
  Cline they are unavailable. Use Playwright MCP screenshots instead.
- The design-detector hook never fires automatically; run `detect` after finishing
  UI edits.
- Fonts/tokens assets stay local; no network needed after the engine is cached.
