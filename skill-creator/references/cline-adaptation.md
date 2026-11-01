# Cline adaptation of Anthropic's `skill-creator`

Source: https://github.com/anthropics/skills/tree/main/skills/skill-creator
Original text kept verbatim in `upstream-SKILL.md`. This file lists every change so
the two can be diffed conceptually.

## Why change anything

The upstream skill assumes the Claude Code / Cowork runtime: subagents for parallel
with-skill and baseline runs, task notifications carrying `total_tokens` and
`duration_ms`, `claude -p` for description optimization, `/tmp` for scratch space,
Unix shell commands, and a `present_files` tool. Cline has none of those. The method
(interview → draft → test → review → improve → repeat) is runtime-independent and was
kept; only the mechanics changed.

## Changes in `SKILL.md`

| Upstream | Adapted for Cline |
|---|---|
| No runtime section | New §0: where skills live, frontmatter limits, discovery/restart, tool mapping, what is missing, Windows notes |
| "spawn two subagents in the same turn" | §5 Mode A: run the prompt inline, then the baseline inline, in separate output folders; caveat that this is weaker than independent agents |
| Task notification with `total_tokens` / `duration_ms` | Removed; §5 says not to invent token/time metrics |
| `nohup ... &`, `VIEWER_PID`, `kill` | `python eval-viewer/generate_review.py ... --static review.html` (self-contained file) |
| Grader/comparator/analyzer subagent prompts | §6/§8: same documents used as inline checklists; blind A/B done by shuffling outputs and asking the user |
| `claude -p` in the main loop | §9: manual description optimization (20 queries, scoring, rewrite), scripted path marked optional |
| `present_files` packaging step | §10: hand over the folder path; `.skill` zip optional |
| "Claude.ai-specific instructions" and "Cowork-Specific Instructions" sections | Removed; replaced by §12 "Pitfalls in Cline" |
| `/tmp/skill-name/` scratch paths | Windows temp or a folder next to the skill |
| `${CLAUDE_PLUGIN_ROOT}`-style paths | Absolute Windows path `C:\Users\duy\.cline\skills\...` and relative paths inside the skill |
| English-only assumptions | §0 "Vietnamese and other non-ASCII content": UTF-8 everywhere, `ensure_ascii=False`, console is not evidence, ASCII kebab-case `name` but any language in `description`/body |

Kept unchanged on purpose: the writing guidance (progressive disclosure, pushy
descriptions, why-over-MUST, generalize-don't-overfit), the `evals.json` structure,
the grading field names (`text`, `passed`, `evidence`), the benchmark and viewer
workflow, the safety section, and the packaging idea.

## Changes in `scripts/`

| File | Change |
|---|---|
| `utils.py` | `read_text()` → `read_text(encoding="utf-8")`; on Windows the default code page cannot read Cyrillic SKILL.md files |
| `quick_validate.py` | same UTF-8 fix; PyYAML made optional with a minimal frontmatter fallback parser |
| `run_eval.py` | `import select` wrapped in try/except (POSIX-only); exits with a clear message when `claude` is not on PATH |
| `improve_description.py` | same `claude` guard + `select` fallback |
| `scaffold_evals.py` | **new**: creates `evals/evals.json` and `<skill>-workspace/iteration-N/<eval>/{with_skill,without_skill}/outputs` plus `eval_metadata.json`; dependency-free replacement for the subagent-driven setup |
| `aggregate_benchmark.py`, `generate_review.py`, `generate_report.py`, `package_skill.py` | unchanged: pure Python, work on Windows |

`agents/*.md`, `references/schemas.md`, `assets/`, `eval-viewer/` are unchanged.

## What Cline users should expect

- Everything up to "write the skill and test it by hand" works with no extra setup.
- Automated benchmarks and trigger evaluation need the Claude Code CLI; without it,
  the skill falls back to inline runs and manual description scoring.
- After creating or editing a skill, restart Cline (or start a new task) so the
  skills list is re-read.
