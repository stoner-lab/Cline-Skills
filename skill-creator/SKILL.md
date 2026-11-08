---
name: skill-creator
description: "Tạo, sửa, kiểm thử và đóng gói skill: viết SKILL.md, viết test prompt, sửa skill không chịu kích hoạt. Dùng khi người dùng nói: 'tạo skill', 'viết skill', 'sửa skill', 'skill không hoạt động', 'skill không tự kích hoạt', 'làm skill cho việc này', 'đóng gói skill'. Không dấu cũng khớp: 'tao skill', 'viet skill', 'sua skill', 'skill khong hoat dong', 'skill khong tu kich hoat', 'lam skill cho viec nay', 'dong goi skill'. Dùng cả khi người dùng nói «làm cái này thành skill» hoặc nhắc tới SKILL.md, .cline/skills. Kết hợp: injection-scan nếu skill mới sẽ đọc nội dung từ ngoài vào."
---

# Skill Creator (Cline edition)

A skill for creating new Cline skills and iteratively improving them. This is an
adaptation of Anthropic's `skill-creator` (github.com/anthropics/skills) to the
Cline runtime: same method, different mechanics. What changed and why is listed in
`references/cline-adaptation.md`; the untouched original text is kept in
`references/upstream-SKILL.md`.

The loop:

1. Decide what the skill should do and roughly how.
2. Write a draft `SKILL.md`.
3. Design 2–3 realistic test prompts.
4. Run them with the skill loaded, plus a baseline without it.
5. Let the user review outputs and give feedback.
6. Rewrite the skill from that feedback (and from anything obviously broken).
7. Repeat until the user is satisfied.
8. Validate, then hand over the folder.

Your job is to find out where the user stands in this loop and move them forward.
If they say "I want a skill for X", narrow it down, draft it, write test prompts,
run them, collect feedback. If a draft already exists, jump straight to testing.
If they say "I don't need evals, just help me write it", respect that – the loop is
a tool, not a ritual.

## 0. Start here: how skills work in Cline

Read this before writing anything, because the mechanics differ from Claude.

**Where skills live**

- Global: `C:\Users\duy\.cline\skills\<skill-name>\SKILL.md` (verified working).
- Workspace-level: some Cline builds also read `<workspace>\.cline\skills\<skill-name>\`.
  If unsure, create the global one – it always works.
- A skill is just a folder: `SKILL.md` plus optional `scripts/`, `references/`,
  `assets/`. No build step, no manifest.

**Frontmatter**

- Required: `name` (kebab-case, ≤ 64 chars, no leading/trailing hyphen) and
  `description` (≤ 1024 chars, no `<` `>` characters).
- Optional and tolerated: `license`, `compatibility`, `metadata`, `allowed-tools`.
- Exactly one YAML block at the very top, delimited by `---` lines. A typo there
  makes the skill silently invisible, so validate it (§10).

**Discovery and invocation**

- Cline reads the skills list when a session starts. After creating or editing a
  skill, tell the user to **start a new task or restart VS Code** so the new
  `SKILL.md` is picked up. This is the most common "it doesn't work" cause.
- The user can invoke a skill explicitly with `/skill-name`.
- You invoke it through the `skills` tool with `skill: "skill-name"`. That call is
  a blocking step: call the tool, then follow what it returned.

**Tool mapping – upstream name → your tool**

| In upstream Anthropic skills | In Cline |
|---|---|
| `view`, `read_file` | `read_files` |
| `create_file`, `str_replace` | `editor` |
| `bash_tool` | `run_commands` (PowerShell on Windows) |
| `grep`, `glob` | `search_codebase`, `run_commands` |
| web fetch | `fetch_web_content` |
| `Task`, subagents | not available – run steps inline, one at a time |

**What is missing here**

- No subagents, so no parallel "with skill vs baseline" runs. Run test prompts
  yourself, sequentially, and keep outputs in separate folders (§5, Mode A).
- No `claude -p` CLI, so `scripts/run_eval.py` and `scripts/improve_description.py`
  (they shell out to Claude Code) usually cannot run. Optimize the description
  manually (§9) unless the user really has the `claude` CLI installed.
- No `present_files` tool: report file paths instead.

**Windows / PowerShell**

- Use `python`, not `python3`. Quote paths. The console code page mangles Cyrillic,
  so write logs to a UTF-8 file (`python ... > log.txt` or `Tee-Object`) instead of
  trusting what the terminal shows.
- `mkdir -p`, `cp -r`, `kill` are not PowerShell: use `New-Item -ItemType Directory`,
  `Copy-Item -Recurse`, `Stop-Process`.

**Vietnamese and other non-ASCII content**

- Read and write every text file explicitly as UTF-8: `open(p, encoding="utf-8")`,
  `Path.read_text(encoding="utf-8")`, `json.dump(..., ensure_ascii=False)`. The
  Windows default (ANSI code page) silently corrupts Vietnamese diacritics.
- Set `$env:PYTHONIOENCODING='utf-8'` (or `chcp 65001`) when a script prints user
  text, and still prefer verifying content in a UTF-8 file via `read_files` – the
  terminal rendering is not evidence.
- A skill `name` stays kebab-case ASCII (`bao-cao-pr`); the `description` and the
  body may be Vietnamese, Russian, or mixed. Frontmatter must be saved as UTF-8
  without BOM.
- `scripts/scaffold_evals.py` transliterates Vietnamese prompts into folder slugs
  (`Làm báo cáo ... → lam-bao-cao-...`) so paths stay portable; normalise strings with
  `unicodedata.normalize("NFC", s)` before comparing them.

## 1. Capture intent

Start from what the user actually has, not from a blank page:

- If the conversation already contains the workflow ("turn this into a skill"),
  mine it first: which tools were used, in what order, which corrections the user
  made, what the input and output looked like. Then ask only about the gaps.
- If they bring a task description, ask for one real example of input and one of
  the expected output. A skill without a concrete example tends to be vague.
- Ask what "done" looks like: what must be in the output, what must never appear,
  which format (`.docx`, `.xlsx`, table, code, plain text).

## 2. Interview and research

Ask about the things that break skills later:

- Edge cases: empty input, missing columns, one row only, values out of range.
- Input/output formats and filenames, units, decimal separator, language.
- Dependencies: external services, API keys, fonts, templates, local paths.
- Who runs it: the user only, or anyone on the machine.
- Error behaviour: stop and ask, or make a documented assumption?

Do the research yourself before asking: check the workspace for templates, read a
sample of the data, look at similar skills already installed in
`C:\Users\duy\.cline\skills\`. Come to the user with a draft, not with homework.

## 3. Write the SKILL.md

### 3.1 Anatomy

```
skill-name/
├── SKILL.md          (required: frontmatter + instructions)
├── scripts/          (optional: deterministic helpers the model can just run)
├── references/       (optional: docs read only when needed)
└── assets/           (optional: templates, fonts, sample files used in output)
```

### 3.2 Progressive disclosure

Three levels, and they matter more in Cline than in Claude because context is
shared with the whole coding session:

1. **Metadata** – `name` + `description`, always in context (~100 words).
2. **Body** – `SKILL.md`, loaded when the skill triggers. Keep it under ~500 lines.
3. **Bundled files** – read or executed on demand, unlimited size.

Practical consequences:

- If the body grows past ~500 lines, split it: move details into `references/` and
  leave a pointer plus the "when to read this" condition.
- Reference files longer than ~300 lines get a table of contents at the top.
- Scripts are better than prose when a step is deterministic: "run
  `python scripts/build_report.py`" beats ten lines of instructions the model may
  improvise around.
- A skill that supports several variants (OS, format, tool) should keep one
  `references/<variant>.md` per variant, so only the relevant one is read.

### 3.3 Frontmatter: the description is the whole game

`description` decides whether the skill is ever used. Rules:

- Say **what** it does and **when** to use it, both in the description, not in the body.
- Be a little pushy: Cline, like Claude, tends to *under*-trigger skills. Name the
  concrete phrases, file names, and tasks that should pull the skill in.
- Keep it under 1024 characters, no angle brackets, one paragraph.

Weak:

```
description: Helps with reports.
```

Strong:

```
description: Build Russian-language ПР/lab reports end to end (title page from the
LETI template, Times New Roman 14, tables and figures with captions, DOCX + PDF).
Use it whenever the user mentions ПР, отчёт, лабораторная, реферат, курсовая, a
report template, or asks to format/rewrite/check a Russian academic report, even if
they do not say the word "skill".
```

### 3.4 Body writing rules

- Imperative mood ("Read the file", "Ask the user"), not "you should probably".
- Explain **why** a rule exists, once. A model that understands the reason applies
  it in cases the author never imagined; a model following `MUST` blindly breaks at
  the first edge case.
- Reserve all-caps `ALWAYS` / `NEVER` for the two or three rules that genuinely must
  not bend. If everything is shouting, nothing is.
- Generalize: write for millions of future prompts, not for the two examples you
  are testing. Overfitted rules ("if the file is named Q4.xlsx, then...") age badly.
- Include concrete examples of input → output, and templates for outputs whose shape
  matters (report structure, commit format, JSON schema).
- Duplicate the critical bit rather than rely on the model scrolling: if a rule
  appears in the body and again in a checklist, that is fine.
- No secrets, no credentials, no absolute paths specific to your machine unless the
  skill is explicitly local-only.

### 3.5 Safety

Skills must not contain malware, exploit code, credential harvesting, or anything
that would surprise the user given the description. Decline requests to build
skills for unauthorized access, data exfiltration, or deception. Role-play and
simulation skills are fine.

## 4. Test prompts

Write 2–3 prompts a real user would type – messy, concrete, with a file name or a
constraint – not abstract requests like "format data". Show them to the user and
ask whether they match reality before running anything.

Save them to `evals/evals.json` inside the skill folder:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "name": "short-descriptive-name",
      "prompt": "User's task prompt",
      "expected_output": "What a good result looks like",
      "files": []
    }
  ]
}
```

Assertions come later (§6); prompts first. Full schema: `references/schemas.md`.
You can scaffold the whole directory tree with:

```
python scripts/scaffold_evals.py <skill-folder> --iteration 1
```

## 5. Run the tests

Put results in `<skill-name>-workspace/` **next to** the skill folder, organised by
iteration: `iteration-1/<eval-name>/with_skill/outputs/`,
`iteration-1/<eval-name>/without_skill/outputs/`.

### Mode A – inline (default, no API keys, works everywhere)

For each eval, one at a time:

1. Read the current `SKILL.md` and follow it literally, as if it were a fresh task.
2. Save every produced file into `.../with_skill/outputs/`.
3. Then run the same prompt **without** the skill (see below for what the baseline
   means) and save into `.../without_skill/outputs/`.
4. Write `eval_metadata.json` next to the two folders: prompt, assertions list
   (may be empty at first), and a one-line note of what you observed.

Baseline depends on the situation:

- New skill: the baseline is no skill at all – solve the task with your normal tools.
- Existing skill being improved: snapshot the old version first
  (`Copy-Item -Recurse <skill> <workspace>\skill-snapshot`), then run the baseline
  from the snapshot. That shows whether the edit helped.

Honest caveat: in Mode A you wrote the skill and you run it, so the comparison is
weaker than independent runs. Say so to the user; the human review step compensates.
Token and time metrics are not available – do not invent them, just skip that table.

### Mode B – scripted (only if the user has the Claude Code CLI or their own harness)

- `scripts/run_eval.py`, `scripts/improve_description.py` call `claude -p` under the
  hood and need the Claude Code CLI plus a `.claude/` project root. If
  `claude` is not on PATH they will fail; check with `Get-Command claude` before
  promising anything.
- `scripts/aggregate_benchmark.py` and `eval-viewer/generate_review.py` are plain
  Python and work fine on Windows:

```
python scripts/aggregate_benchmark.py <workspace>\iteration-1 --skill-name my-skill
python eval-viewer/generate_review.py <workspace>\iteration-1 --skill-name my-skill --benchmark <workspace>\iteration-1\benchmark.json --static review.html
```

`--static` writes a self-contained HTML file the user can open by double-click;
without it the script starts a local server and opens a browser tab.

## 6. Grade the outputs

Grade against explicit assertions, not vibes. For each eval write assertions like
"the .docx has a title page with the department name", "the table has 12 rows",
"no first-person pronouns", "the PDF exists and has 3 pages".

Two ways to check them, in order of preference:

1. **Programmatic** – write a tiny script (or reuse `scripts/quick_validate.py`,
   `python-docx`, `pypdf`) and let it print pass/fail per assertion. Reusable across
   iterations and immune to your own optimism.
2. **Inline review** – read the output and judge, using `agents/grader.md` as the
   checklist. There are no subagents here, so this is you reading the file, not a
   separate agent.

Write results to `grading.json` in each run folder, with exactly these field names
in `expectations`: `text`, `passed`, `evidence`. The viewer depends on them.

## 7. Improve the skill

After the user has looked at outputs:

- **Generalise, do not overfit.** The two test prompts are a training set you will
  throw away. If a fix only works for them, it is noise.
- **Keep it lean.** Delete rules that never changed an output. Re-read the
  transcript: where did the skill make you waste steps?
- **Explain the why.** If the user's feedback is terse ("too long", "wrong format"),
  find the underlying reason and write that into the skill instead of adding a
  patch sentence.
- **Move repeated work into `scripts/`.** If every run wrote the same helper, ship it
  once in the skill and tell the skill to call it.
- **Re-check the description** if the problem was "it never triggered" – that is a
  metadata problem, not a body problem (§9).

## 8. Iterate

1. Apply the changes.
2. Re-run all evals into `iteration-<N+1>/`, baseline included.
3. Show the user the new outputs (folder paths, plus the static HTML viewer if
   Mode B is in play).
4. Read the feedback, improve again.

Stop when the user is happy, when the feedback is empty, or when changes stop
producing differences. Blind A/B comparison (`agents/comparator.md`) needs
independent agents; in Cline do it by shuffling outputs yourself and asking the
user which they prefer without telling them which version it is.

## 9. Optimize the description (manual, Cline-friendly)

Offer this once the skill body is stable – a perfect body with a bad description is
dead weight.

1. **Write 20 trigger queries**: ~10 that should fire the skill, ~10 that should not.
   Make them realistic: file paths, mixed case, typos, casual phrasing, near-miss
   tasks that belong to a different skill. Clear-cut examples ("read this PDF") are
   useless because almost nothing triggers on them.
2. **Review with the user** – which ones are unrealistic, which cases are missing.
3. **Score by reading only `name` + `description`**: for each query decide
   "triggers / does not trigger". Do this before looking at the body, otherwise you
   are grading your knowledge instead of the metadata.
4. **Rewrite** the description where it failed (missing trigger words, too narrow,
   too generic), score again, keep the best version.
5. **Apply** the winner to the frontmatter and show the user before/after with scores.

If the `claude` CLI is installed, `scripts/improve_description.py` automates part of
this; otherwise the manual loop above is the supported path. Never claim a numeric
improvement you did not measure.

## 10. Validate and hand over

- `python scripts/quick_validate.py <skill-folder>` must print `Skill is valid!`.
  It checks the frontmatter: required keys, kebab-case name, description length,
  forbidden characters, allowed extra keys.
- Read the final `SKILL.md` once yourself, top to bottom. Frontmatter typos and
  duplicated headings are invisible to the validator but break the skill.
- Tell the user to **restart Cline / open a new task**, then try `/skill-name`
  once, and a normal request that should trigger it.
- Sharing with someone else: copy the whole folder into their
  `C:\Users\<user>\.cline\skills\`. A `.skill` archive (a zip) can be produced with
  `python -m scripts.package_skill <skill-folder> <output-dir>` from the
  skill-creator directory, but Cline itself only needs the unpacked folder.
- Updating an existing skill: keep the directory name and the `name` field
  unchanged (renaming silently breaks `/<name>` and any other skill that refers to
  it). Edit a copy first if the installed skill is read-only.

## 11. Reference files

- `references/schemas.md` – JSON shapes for `evals.json`, `eval_metadata.json`,
  `grading.json`, `benchmark.json`, `feedback.json`. Read it before hand-writing
  any of them.
- `references/cline-adaptation.md` – exactly what was changed from the Anthropic
  original and why.
- `references/upstream-SKILL.md` – the original Claude-oriented text, kept for
  comparison (contains the subagent and `claude -p` workflows).
- `agents/grader.md` – how to grade assertions. In Cline, use it as your own
  checklist, not as a subagent prompt.
- `agents/comparator.md` – blind A/B comparison protocol.
- `agents/analyzer.md` – what to look for in benchmark data (non-discriminating
  assertions, flaky evals, time/token tradeoffs).
- `scripts/quick_validate.py` – frontmatter validator (needs PyYAML; falls back to a
  minimal parser if PyYAML is missing).
- `scripts/scaffold_evals.py` – creates `evals/evals.json` and the
  `<skill>-workspace/iteration-N/<eval>/` tree from prompts.
- `scripts/aggregate_benchmark.py` – turns `grading.json` files into
  `benchmark.json` / `benchmark.md`.
- `scripts/package_skill.py` – packs a skill folder into a `.skill` zip.
- `scripts/run_eval.py`, `scripts/improve_description.py` – Claude Code CLI only
  (`claude -p`); they will refuse to run when the CLI is absent.
- `eval-viewer/generate_review.py` – builds the HTML review page (use `--static`
  for a file you can just double-click).

## 12. Pitfalls in Cline, in order of frequency

1. **Skill created but not listed** – Cline read the skills at session start.
   Restart or open a new task.
2. **YAML broken** – a colon or quote inside an unquoted `description`, or two
   frontmatter blocks. Wrap the value in quotes when in doubt.
3. **Never triggers** – description too abstract or too narrow. Fix the metadata,
   not the body.
4. **Triggers too often** – description claims a whole domain. Narrow it and add an
   explicit boundary ("do not use for X, use skill Y instead").
5. **Body too long** – move detail into `references/`; the body should be the map,
   not the territory.
6. **Script paths** – quote paths with spaces; Cyrillic paths work but keep them
   quoted. Prefer relative paths inside the skill folder.
7. **Bash-isms** – `cp -r`, `nohup`, `$!` do not exist in PowerShell.
8. **Fake metrics** – without subagents there are no reliable token/time numbers.
   Report what you measured, skip the rest.
9. **Mojibake in Vietnamese or Cyrillic text** – a file was written with the ANSI
   code page. Rewrite it with `encoding="utf-8"`, set `PYTHONIOENCODING`, and verify
   by opening the file with `read_files`, never by looking at the console.

Repeating the core loop once more: understand the task → draft `SKILL.md` → test
prompts → run with and without the skill → human review → improve → repeat →
validate → hand over.
