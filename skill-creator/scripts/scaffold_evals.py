#!/usr/bin/env python3
"""Scaffold eval folders for a Cline skill.

No API keys, no subagents, no external services - just directories and JSON.

Usage:
    python scripts/scaffold_evals.py <skill-folder> --iteration 1
    python scripts/scaffold_evals.py <skill-folder> --iteration 1 --prompts prompts.txt

What it does:
  1. Reads <skill-folder>/evals/evals.json. If the file is missing, it is created
     from --prompts (one prompt per line; blank lines and '#' comments ignored),
     or filled with a single placeholder prompt.
  2. Creates <skill-folder>-workspace/iteration-<N>/<eval-slug>/
       with_skill/outputs/      - results produced following SKILL.md
       without_skill/outputs/   - baseline results produced without the skill
       eval_metadata.json       - prompt, assertions (empty), notes
  3. Prints the resulting tree so it can be pasted into the chat.

Rename `without_skill` to `old_skill` when the baseline is a previous version of
the same skill (SKILL.md, section 5, Mode A).
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

PLACEHOLDER_PROMPT = "Replace with a real user request that should trigger this skill."


def slugify(text: str) -> str:
    """URL/dir-safe slug that keeps Vietnamese readable: 'Báo cáo ПР-1' -> 'bao-cao-pr-1'."""
    text = str(text or "").strip().lower()
    text = text.replace("đ", "d").replace("Đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^0-9a-zа-яё_-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    if len(text) > 50 and "-" in text[:50]:
        text = text[:50].rsplit("-", 1)[0]
    return text[:60] or "eval"


def load_prompts(path: Path | None) -> list[str]:
    if path is None:
        return []
    prompts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        prompts.append(line)
    return prompts


def ensure_evals_json(skill_dir: Path, prompts: list[str]) -> dict:
    evals_dir = skill_dir / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    evals_path = evals_dir / "evals.json"

    if evals_path.exists():
        return json.loads(evals_path.read_text(encoding="utf-8"))

    if not prompts:
        prompts = [PLACEHOLDER_PROMPT]

    data = {
        "skill_name": skill_dir.name,
        "evals": [
            {
                "id": i,
                "name": ("eval-%d" % i) if prompt == PLACEHOLDER_PROMPT else slugify(prompt),
                "prompt": prompt,
                "expected_output": "",
                "files": [],
            }
            for i, prompt in enumerate(prompts)
        ],
    }
    evals_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
    print(f"created {evals_path}")
    return data


def scaffold(skill_dir: Path, iteration: int, data: dict) -> Path:
    workspace = skill_dir.parent / f"{skill_dir.name}-workspace" / f"iteration-{iteration}"
    for ev in data.get("evals", []):
        name = slugify(ev.get("name") or f"eval-{ev.get('id', 0)}")
        base = workspace / name
        for variant in ("with_skill", "without_skill"):
            (base / variant / "outputs").mkdir(parents=True, exist_ok=True)
        meta = {
            "eval_id": ev.get("id"),
            "eval_name": name,
            "prompt": ev.get("prompt", ""),
            "expected_output": ev.get("expected_output", ""),
            "files": ev.get("files", []),
            "assertions": ev.get("assertions", []),
            "notes": "",
        }
        (base / "eval_metadata.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {name}")
    return workspace


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold eval folders for a Cline skill")
    ap.add_argument("skill_folder", help="path to the skill folder (contains SKILL.md)")
    ap.add_argument("--iteration", type=int, default=1, help="iteration number (default 1)")
    ap.add_argument("--prompts", help="text file with one prompt per line")
    args = ap.parse_args()

    skill_dir = Path(args.skill_folder).resolve()
    if not (skill_dir / "SKILL.md").exists():
        print(f"ERROR: SKILL.md not found in {skill_dir}")
        return 1

    prompts = load_prompts(Path(args.prompts) if args.prompts else None)
    data = ensure_evals_json(skill_dir, prompts)
    print(f"scaffolding iteration-{args.iteration} for {skill_dir.name}:")
    workspace = scaffold(skill_dir, args.iteration, data)
    print(f"\ndone: {workspace}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
