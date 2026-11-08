---
name: brand
description: "Giọng điệu thương hiệu, nhận diện, messaging framework, quản lý asset và kiểm tra tính nhất quán của thương hiệu. Dùng khi người dùng nói: 'viết brand voice', 'giọng điệu thương hiệu', 'messaging framework', 'kiểm tra brand compliance', 'quản lý asset thương hiệu'. Không dấu cũng khớp: 'viet brand voice', 'giong dieu thuong hieu', 'messaging framework', 'kiem tra brand compliance', 'quan ly asset thuong hieu'. Không dùng cho thiết kế UI cụ thể (dùng ui-styling) hay slide (dùng slides)."
license: "MIT (c) 2024 Next Level Builder - full text in LICENSE inside this directory"
compatibility: "Cline on Windows: PowerShell shell, python 3.14 and node 24 on PATH, read_files/editor/run_commands; scripts run from the skill directory; no subagents; see the Cline runtime notes inside."
metadata:
  upstream: "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/main/.claude/skills/brand"
  adaptation: "Cline runtime notes in SKILL.md"
---
# Brand

## Cline runtime notes (read first)

- **Skill directory:** the folder holding this `SKILL.md`, written `<skill>` below. Installed: `C:\Users\<user>\.cline\skills\brand\`; in the source repo: `E:\Private\Projects\Cline-Skills\brand\`.
- **Scripts run from the skill directory.** The text uses relative paths (`python scripts/...`, `node scripts/...`). `run_commands` starts in the workspace, so prefix the command with a location change: `Set-Location "$env:USERPROFILE\.cline\skills\brand"; node scripts/inject-brand-context.cjs`
- **`python3` does not exist on Windows** - every `python3 ...` in the text runs as `python ...` (3.14 here).
- **Dependencies:** Node 24 cho các file `.cjs`; không có phụ thuộc Python.
- **Tools:** `Read` -> `read_files`; `Write`/`Edit` -> `editor`; shell -> `run_commands` (PowerShell); search -> `search_codebase`. No subagents.
- **Never install packages on your own.** If something is missing, report the exact command and wait for permission.
- **Language:** answer the user in their language (Vietnamese by default); keep tokens, CSS, component names and file paths verbatim.

Brand identity, voice, messaging, asset management, and consistency frameworks.

## When to Use

- Brand voice definition and content tone guidance
- Visual identity standards and style guide development
- Messaging framework creation
- Brand consistency review and audit
- Asset organization, naming, and approval
- Color palette management and typography specs

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project: `scripts/<file>` is this skill's own `scripts/` folder, and `../<skill>/scripts/<file>` is a sibling sub-skill installed alongside it. Build the full path from that directory (Claude Code reports it as the skill's base directory when the skill loads) and keep the working directory at the project root – the scripts read and write project files such as `docs/brand-guidelines.md`, `assets/design-tokens.json` or `src/` relative to it.

## Quick Start

**Inject brand context into prompts:**
```bash
node scripts/inject-brand-context.cjs
node scripts/inject-brand-context.cjs --json
```

**Validate an asset:**
```bash
node scripts/validate-asset.cjs <asset-path>
```

**Extract/compare colors:**
```bash
node scripts/extract-colors.cjs --palette
node scripts/extract-colors.cjs <image-path>
```

## Brand Sync Workflow

```bash
# 1. Edit docs/brand-guidelines.md (or use /brand update)
# 2. Sync to design tokens
node scripts/sync-brand-to-tokens.cjs
# 3. Verify
node scripts/inject-brand-context.cjs --json | head -20
```

The sync stops when it detects existing token files, `:root` custom properties
or Tailwind v4 `@theme` variables in common CSS entry points and their local
CSS imports, or Tailwind theme colors and presets. Review the reported source
before proceeding. If the detected files are the managed
`assets/design-tokens.*` outputs from an earlier sync and replacing them is
intentional, re-run with `--force`.

**Files synced:**
- `docs/brand-guidelines.md` → Source of truth
- `assets/design-tokens.json` → Token definitions
- `assets/design-tokens.css` → CSS variables

## Subcommands

| Subcommand | Description | Reference |
|------------|-------------|-----------|
| `update` | Update brand identity and sync to all design systems | `references/update.md` |

## References

| Topic | File |
|-------|------|
| Voice Framework | `references/voice-framework.md` |
| Visual Identity | `references/visual-identity.md` |
| Messaging | `references/messaging-framework.md` |
| Consistency | `references/consistency-checklist.md` |
| Guidelines Template | `references/brand-guideline-template.md` |
| Asset Organization | `references/asset-organization.md` |
| Color Management | `references/color-palette-management.md` |
| Typography | `references/typography-specifications.md` |
| Logo Usage | `references/logo-usage-rules.md` |
| Approval Checklist | `references/approval-checklist.md` |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/inject-brand-context.cjs` | Extract brand context for prompt injection |
| `scripts/sync-brand-to-tokens.cjs` | Sync brand-guidelines.md → design-tokens.json/css |
| `scripts/validate-asset.cjs` | Validate asset naming, size, format |
| `scripts/extract-colors.cjs` | Extract and compare colors against palette |

## Templates

| Template | Purpose |
|----------|---------|
| `templates/brand-guidelines-starter.md` | Complete starter template for new brands |

## Routing

1. Parse subcommand from `$ARGUMENTS` (first word)
2. Load corresponding `references/{subcommand}.md`
3. Execute with remaining arguments
