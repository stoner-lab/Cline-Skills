# -*- coding: utf-8 -*-
"""Keep the Cline skills in sync with their upstream repositories.

    python tools/sync_upstream.py check [--json]        # what changed upstream
    python tools/sync_upstream.py apply --all           # regenerate the automatic skills
    python tools/sync_upstream.py apply pdf --diff      # one skill, show the diff
    python tools/sync_upstream.py apply pdf --dry-run   # show what would change
    python tools/sync_upstream.py status                # per-skill state table
    python tools/sync_upstream.py add my-skill --repo owner/repo --path skills/my-skill

Strategies (tools/adapt_config.json -> strategy):
    adapt   SKILL.md is generated from upstream + tools/notes/<name>.md; safe to overwrite
    manual  SKILL.md is hand-written; sync only reports that upstream moved
    own     this repository is the source (otchet); skipped

Needs a GitHub token in GH_TOKEN or GITHUB_TOKEN for the API path; without one it
falls back to `git ls-remote` and raw.githubusercontent.com, which works for every
public upstream and keeps a scheduled local run token-free.
Exit codes: check -> 0 nothing to do, 1 upstream changed, 2 error.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import difflib
import io
import json
import os
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adapt_skill  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "tools" / "adapt_config.json"
STATE = ROOT / "upstream.json"

# Cache of blobless clones used when the GitHub API is unavailable (no token, 403).
_CLONES: dict[tuple[str, str], Path] = {}


def token() -> str:
    """GitHub token, optional: public repositories work without one."""
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""


def git_remote_head(repo: str, ref: str) -> str:
    """HEAD of ``ref`` in a public repo without a token: `git ls-remote`."""
    import subprocess

    if len(ref) == 40 and all(c in "0123456789abcdef" for c in ref.lower()):
        return ref
    url = f"https://github.com/{repo}.git"
    want = f"refs/heads/{ref}"
    try:
        res = subprocess.run(["git", "ls-remote", url, want],
                             capture_output=True, text=True, timeout=120)
    except Exception as exc:                       # noqa: BLE001
        sys.exit(f"ERROR: cannot reach {url}: {exc}")
    for line in (res.stdout or "").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == want:
            return parts[0]
    sys.exit(f"ERROR: {repo} has no branch {ref!r} (checked with git ls-remote; "
             "set GH_TOKEN if the repository is private)")


def api(url: str, raw: bool = False, attempt: int = 0):
    headers = {
        "User-Agent": "cline-skill-sync",
        "Accept": "application/vnd.github+json",
    }
    tok = token()
    if tok:
        headers["Authorization"] = "token " + tok
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read() if raw else json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (429, 500, 502, 503, 504) and attempt < 3:
            import time
            time.sleep(2 ** attempt)
            return api(url, raw, attempt + 1)
        sys.exit(f"ERROR: GitHub API {e.code} for {url}")
    except Exception:
        if attempt < 3:
            import time
            time.sleep(2 ** attempt)
            return api(url, raw, attempt + 1)
        raise


class Api:
    def __init__(self) -> None:
        self._heads: dict[tuple[str, str], str] = {}

    def head(self, repo: str, ref: str) -> str:
        key = (repo, ref)
        if key not in self._heads:
            try:
                self._heads[key] = api(f"https://api.github.com/repos/{repo}/commits/{ref}")["sha"]
            except (SystemExit, Exception):        # no token, rate limit, 404
                self._heads[key] = git_remote_head(repo, ref)
        return self._heads[key]

    def file_text(self, repo: str, ref: str, path: str, name: str = "SKILL.md") -> str:
        full = f"{path.rstrip('/')}/{name}".lstrip("./")
        url = f"https://api.github.com/repos/{repo}/contents/{urllib.parse.quote(full)}?ref={ref}"
        try:
            data = api(url)
        except (SystemExit, Exception):            # fall back to the raw file
            raw = f"https://raw.githubusercontent.com/{repo}/{ref}/{urllib.parse.quote(full)}"
            try:
                req = urllib.request.Request(raw, headers={"User-Agent": "cline-skill-sync"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    return r.read().decode("utf-8")
            except Exception as exc:               # noqa: BLE001
                sys.exit(f"ERROR: cannot read {repo}:{full}: {exc}")
        if isinstance(data, list):
            sys.exit(f"ERROR: {repo}:{full} is a directory, not a file")
        return base64.b64decode(data["content"]).decode("utf-8")

    def listing(self, repo: str, ref: str, path: str) -> list[str]:
        """Names of the files at the top of the skill folder; best effort only."""
        url = f"https://api.github.com/repos/{repo}/contents/{urllib.parse.quote(path.strip('/'))}?ref={ref}"
        try:
            data = api(url)
        except SystemExit:
            # No token / rate limit: fall back to a shallow blobless clone, otherwise
            # the "files missing locally" warning silently never fires.
            return self._listing_from_git(repo, ref, path)
        return [item["name"] for item in data] if isinstance(data, list) else []

    def _listing_from_git(self, repo: str, ref: str, path: str) -> list[str]:
        import subprocess
        import tempfile

        key = (repo, ref)
        if key not in _CLONES:
            root = Path(tempfile.gettempdir()) / ("cline-sync-" + repo.replace("/", "_"))
            _CLONES[key] = root
            if not (root / ".git").exists():
                subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout",
                                "--depth", "1", f"https://github.com/{repo}.git", str(root)],
                               capture_output=True, text=True, timeout=300)
            else:
                subprocess.run(["git", "-C", str(root), "fetch", "--depth", "1", "origin", ref],
                               capture_output=True, text=True, timeout=300)
        root = _CLONES[key]
        res = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "--name-only",
                              f"origin/{ref}", "--", path.strip("/")],
                             capture_output=True, text=True, timeout=300)
        prefix = path.strip("/") + "/"
        names = []
        for line in (res.stdout or "").splitlines():
            if line.startswith(prefix):
                rest = line[len(prefix):]
                if rest and "/" not in rest:
                    names.append(rest)
        return names


def load_json(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_stale(checked_at: str, days: int = 90) -> bool:
    try:
        return (dt.date.today() - dt.date.fromisoformat(checked_at)).days > days
    except Exception:
        return True


def diff_stat(old: str, new: str) -> int:
    return sum(1 for line in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0)
               if line[:1] in "+-" and not line.startswith(("+++", "---")))


def run_validator(skill_dir: Path) -> str:
    validator = ROOT / "skill-creator" / "scripts" / "quick_validate.py"
    if not validator.exists():
        return ""
    import subprocess
    res = subprocess.run([sys.executable, str(validator), str(skill_dir)],
                         capture_output=True, text=True, encoding="utf-8")
    return (res.stdout or res.stderr).strip()


def cmd_check(args) -> int:
    cfg_all = load_json(CONFIG, {})
    state = load_json(STATE, {"skills": {}}).get("skills", {})
    client, changed, stale, rows = Api(), [], [], []
    for name, cfg in cfg_all.items():
        strategy = cfg.get("strategy", "adapt")
        if strategy == "own":
            rows.append((name, "own", "-", "-"))
            continue
        head = client.head(cfg["repo"], cfg.get("ref", "main"))
        old = state.get(name, {}).get("sha")
        status = "up to date" if old == head else ("CHANGED" if old else "new")
        if status != "up to date":
            changed.append(name)
        if old and is_stale(state[name].get("checked_at", "")):
            stale.append(name)
            status += " (STALE)"
        if strategy == "manual":
            status += " [manual]"
        rows.append((name, status, (old or "-")[:7], head[:7]))
    width = max(len(r[0]) for r in rows)
    if args.json:
        print(json.dumps([{"name": n, "status": s, "old": o, "new": h} for n, s, o, h in rows], indent=2))
    else:
        for name, status, old, head in rows:
            print(f"{name:<{width}}  {status:<24} {old:>7} -> {head:>7}")
        if stale:
            print("\nSTALE (not checked for 90+ days): " + ", ".join(stale))
    return 0 if not changed else 1


def cmd_apply(args) -> int:
    cfg_all = load_json(CONFIG, {})
    state = load_json(STATE, {"skills": {}})
    state.setdefault("skills", {})
    names = list(args.names or [])
    unknown = [n for n in names if n not in cfg_all]
    if unknown:
        sys.exit("ERROR: not in adapt_config.json: " + ", ".join(unknown))
    if args.all or not names:
        names = [n for n, c in cfg_all.items() if c.get("strategy", "adapt") != "own"]
    client = Api()
    for name in names:
        cfg = cfg_all[name]
        strategy = cfg.get("strategy", "adapt")
        ref = cfg.get("ref", "main")
        head = client.head(cfg["repo"], ref)
        if strategy == "own":
            print(f"{name:<28} own repository, skipped")
            continue
        if strategy == "manual":
            old = state["skills"].get(name, {}).get("sha")
            note = "SKILL.md is hand-written; review upstream yourself" if old != head else "up to date"
            print(f"{name:<28} {note}")
            if not args.dry_run:
                state["skills"][name] = {"repo": cfg["repo"], "ref": ref, "path": cfg["path"],
                                         "sha": head, "checked_at": dt.date.today().isoformat()}
            continue

        upstream_md = client.file_text(cfg["repo"], ref, cfg["path"])
        new_text = adapt_skill.build_skill(upstream_md, cfg, name)
        target = ROOT / name / "SKILL.md"
        old_text = target.read_text(encoding="utf-8") if target.exists() else ""
        delta = diff_stat(old_text, new_text)
        warnings = adapt_skill.check_structure(new_text)
        extra = client.listing(cfg["repo"], ref, cfg["path"])
        missing = [f for f in extra if f != "SKILL.md" and not (ROOT / name / f).exists()]
        if args.dry_run:
            print(f"{name:<28} would change {delta} lines" + (f" (+{len(missing)} upstream files missing)" if missing else ""))
            continue
        changed = new_text != old_text
        if changed:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(new_text, encoding="utf-8")
        validation = run_validator(ROOT / name) if changed else ""
        state["skills"][name] = {"repo": cfg["repo"], "ref": ref, "path": cfg["path"],
                                 "sha": head, "checked_at": dt.date.today().isoformat()}
        print(f"{name:<28} {'updated' if changed else 'unchanged':<10} lines: {delta:<4}"
              + (f" validator: {validation}" if validation else ""))
        for w in warnings:
            print(f"{'':<28} WARNING: {w}")
        if missing:
            print(f"{'':<28} WARNING: upstream has files not copied here: {', '.join(missing)}")
        if args.diff and changed:
            sys.stdout.writelines(difflib.unified_diff(old_text.splitlines(True), new_text.splitlines(True),
                                                       fromfile=f"{name}/SKILL.md (old)",
                                                       tofile=f"{name}/SKILL.md (new)"))
    if not args.dry_run:
        save_state(state)
    return 0


def cmd_status(args) -> int:
    state = load_json(STATE, {"skills": {}}).get("skills", {})
    for name, info in sorted(state.items()):
        try:
            age = f"{(dt.date.today() - dt.date.fromisoformat(info['checked_at'])).days}d ago"
        except Exception:
            age = "never"
        print(f"{name:<28} {info['repo']:<26} {info['sha'][:10]}  checked {info['checked_at']} ({age})")
    return 0


def cmd_add(args) -> int:
    cfg_all = load_json(CONFIG, {})
    if args.name in cfg_all:
        sys.exit(f"ERROR: {args.name} already in adapt_config.json")
    cfg_all[args.name] = {
        "repo": args.repo, "ref": args.ref, "path": args.path, "strategy": "adapt",
        "description": args.description or f"TODO: describe {args.name} and add Vietnamese trigger phrases",
        "license": "see LICENSE",
    }
    CONFIG.write_text(json.dumps(cfg_all, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"added {args.name}. next: write tools/notes/{args.name}.md, set description/license,"
          f" then run:  python tools/sync_upstream.py apply {args.name}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync Cline skills with their upstream repositories")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pc = sub.add_parser("check")
    pc.add_argument("--json", action="store_true")
    pc.set_defaults(func=cmd_check)
    pa = sub.add_parser("apply")
    pa.add_argument("names", nargs="*")
    pa.add_argument("--all", action="store_true")
    pa.add_argument("--diff", action="store_true")
    pa.add_argument("--dry-run", action="store_true")
    pa.set_defaults(func=cmd_apply)
    ps = sub.add_parser("status")
    ps.set_defaults(func=cmd_status)
    padd = sub.add_parser("add")
    padd.add_argument("name")
    padd.add_argument("--repo", required=True)
    padd.add_argument("--path", required=True)
    padd.add_argument("--ref", default="main")
    padd.add_argument("--description")
    padd.set_defaults(func=cmd_add)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
