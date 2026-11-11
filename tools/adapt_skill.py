# -*- coding: utf-8 -*-
"""Turn an upstream SKILL.md into a Cline SKILL.md.

Input: the upstream file plus the per-skill entry of tools/adapt_config.json.
Output: frontmatter (Cline keys) + H1 + "Cline runtime notes" + upstream body
with the tool names mapped and the typography normalised.

Everything that is specific to this repository lives in adapt_config.json and
tools/notes/; regenerating from the same inputs must produce the same file.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_COMPAT = ("Cline on Windows: PowerShell shell, run_commands/read_files/editor, "
                  "no subagents; see the Cline runtime notes inside.")

TOOL_MAP = [
    ("view tool", "read_files tool"),
    ("`view`", "`read_files`"),
    ("create_file", "editor"),
    ("str_replace", "editor"),
    ("bash_tool", "run_commands"),
]

TYPO = {"\u2014": "\u2013", "\u2026": "...", "\u2022": "\u2013"}


def load_config(name: str, path: Path | None = None) -> dict:
    cfg_path = path or REPO_ROOT / "tools" / "adapt_config.json"
    data = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    if name not in data:
        raise KeyError(f"{name} is not in adapt_config.json - run: sync_upstream.py add {name} --repo ... --path ...")
    return data[name]


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.index("\n---", 3)
    return text[3:end], text[end + 4:]


def _outside_code(text: str, fn) -> str:
    """Apply fn only to prose: fenced blocks and inline code are left untouched."""
    parts = re.split(r"(```.*?```|`[^`\n]*`)", text, flags=re.S)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            parts[i] = fn(part)
    return "".join(parts)


def normalize(text: str) -> str:
    """No em dash and no ellipsis character anywhere; the bullet glyph only in prose.

    ``\u2022`` and ``\u2026`` sometimes *name* the character inside inline code
    ("never insert ``\u2022`` literally"), so those spans are left alone for the
    bullet; a dash is a dash even in code, so ``\u2014`` is replaced everywhere.
    """
    text = text.replace("\u2014", "\u2013").replace("\u2026", "...")
    return _outside_code(text, lambda s: s.replace("\u2022", "\u2013"))


def _apply(text: str, table) -> str:
    items = table.items() if isinstance(table, dict) else table
    for bad, good in items:
        text = text.replace(bad, good)
    return text


def map_tools(text: str) -> str:
    return _outside_code(text, lambda s: _apply(s, TOOL_MAP))


def build_frontmatter(name: str, cfg: dict) -> str:
    desc = " ".join(str(cfg["description"]).split())
    license_line = cfg.get("license", "see LICENSE")
    compat = cfg.get("compatibility", DEFAULT_COMPAT)
    upstream = f"https://github.com/{cfg['repo']}/tree/{cfg.get('ref', 'main')}/{cfg['path']}".rstrip("/")
    extra = ""
    # Some upstream skills ship their own integrity guard that greps fixed keys inside the
    # frontmatter. They live under metadata: so quick_validate still sees only allowed keys.
    for key, value in (cfg.get("frontmatter_metadata") or {}).items():
        extra += f'  {key}: "{value}"\n'
    return ("---\n"
            f"name: {name}\n"
            f'description: "{desc}"\n'
            f'license: "{license_line}"\n'
            f'compatibility: "{" ".join(str(compat).split())}"\n'
            "metadata:\n"
            f'  upstream: "{upstream}"\n'
            '  adaptation: "Cline runtime notes in SKILL.md"\n'
            f"{extra}"
            "---\n")


def build_body(upstream_body: str, notes: str, cfg: dict) -> str:
    lines = upstream_body.lstrip("\n").split("\n")
    head, rest = (lines[0], lines[1:]) if lines and lines[0].startswith("# ") else ("", lines)
    rest_text = "\n".join(rest)
    for old, new in cfg.get("replacements", []):
        rest_text = rest_text.replace(old, new)
    rest_text = map_tools(rest_text)
    rest_text = normalize(rest_text)
    parts = [p for p in (head, normalize(notes).strip(), rest_text.strip()) if p]
    return "\n\n".join(parts) + "\n"


def build_skill(upstream_text: str, cfg: dict, name: str) -> str:
    _, body = split_frontmatter(upstream_text)
    notes = ""
    if cfg.get("notes"):
        notes_path = REPO_ROOT / cfg["notes"]
        if notes_path.exists():
            notes = notes_path.read_text(encoding="utf-8")
    return build_frontmatter(name, cfg) + build_body(body, notes, cfg)


def check_structure(text: str) -> list[str]:
    """Warnings that need a human: the adaptation assumes this shape."""
    warns = []
    if not text.startswith("---"):
        warns.append("SKILL.md has no frontmatter")
    if not re.search(r"(?m)^# ", text):
        warns.append("no level-1 heading")
    if "## Cline runtime notes" not in text:
        warns.append("Cline runtime notes missing (no notes file?)")
    return warns
