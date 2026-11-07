# skill-creator (Cline edition)

Create, edit, improve and evaluate Cline skills (`SKILL.md` folders under `.cline/skills`).

> **Fork note.** Adapted from [anthropics/skills · skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
> for the Cline runtime: tool mapping, no subagents, no `claude -p`, UTF-8 everywhere,
> typography limits, Vietnamese trigger phrases. What changed: `references/cline-adaptation.md`.
> The untouched original: `references/upstream-SKILL.md`. License: Apache 2.0 (`LICENSE.txt`).

## Install

Copy this folder to `C:\Users\<user>\.cline\skills\skill-creator`, then restart Cline (or start a new task)
so the skills list is re-read. Invoke with `/skill-creator`, or just describe the job.

## What it does

- drafts a `SKILL.md` from an interview in the current conversation;
- writes test prompts (`evals/evals.json`) and scaffolds run folders;
- grades outputs against assertions, benchmarks two variants;
- optimizes the `description` so the skill actually triggers;
- validates (`scripts/quick_validate.py`) and packs (`.skill` zip) the result.

## Layout

```
SKILL.md                  workflow and rules
references/               schemas, Cline adaptation notes, upstream copy
agents/                   grader / comparator / analyzer checklists (used inline)
scripts/                  scaffold_evals.py, quick_validate.py, package_skill.py, ...
eval-viewer/              static HTML review page generator
assets/                   review page template
```

## Quick checks

```
python scripts/quick_validate.py .
python scripts/scaffold_evals.py <skill-folder> --iteration 1 --prompts prompts.txt
```

Bản Việt: skill này giúp tạo và cải thiện skill cho Cline; gọi bằng `/skill-creator` hoặc chỉ cần nói
"tạo skill cho việc này".
