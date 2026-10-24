#!/usr/bin/env python3
"""Resolve the recurring rebase conflicts for session 37737303 locally.

Only three files ever collide, and all three are append-only lists:
  * COORDINATION.md   -> keep BOTH sides, my section appended at the end and renumbered
  * pipeline/build.py -> keep BOTH ARCHIVE lines
  * index.html        -> keep BOTH <li> entries
Nothing is discarded; this is the additive-union rule from COORDINATION.md §0.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MINE = "37737303"


def conflicts(lines):
    while True:
        idx = [k for k, ln in enumerate(lines) if ln.startswith("<<<<<<<")]
        if not idx:
            return
        i = idx[0]
        sep = next(k for k in range(i + 1, len(lines)) if lines[k].startswith("======="))
        j = next(k for k in range(sep + 1, len(lines)) if lines[k].startswith(">>>>>>>"))
        yield i, sep, j


def resolve_text(path: pathlib.Path) -> bool:
    lines = path.read_text().splitlines()
    if not any(ln.startswith("<<<<<<<") for ln in lines):
        return False
    out = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith("<<<<<<<"):
            out.append(lines[i])
            i += 1
            continue
        sep = next(k for k in range(i + 1, len(lines)) if lines[k].startswith("======="))
        j = next(k for k in range(sep + 1, len(lines)) if lines[k].startswith(">>>>>>>"))
        head, mine = lines[i + 1:sep], lines[sep + 1:j]
        if path.name == "COORDINATION.md":
            out += head + mine          # both kept; renumbering below
        else:
            merged = list(head)
            for ln in mine:
                key = re.sub(r"^\s*", "", ln)[:60]
                if key and not any(key[:40] in h for h in merged):
                    merged.append(ln)
            out += merged
        i = j + 1
    text = "\n".join(out) + "\n"
    if path.name == "COORDINATION.md":
        # my claim must not reuse a section number another session already holds
        nums = [int(m) for m in re.findall(r"^## (\d+)\. Session `(?!37737303)", text, re.M)]
        mine_heads = [m for m in re.findall(r"^## (\d+)\. Session `37737303", text, re.M)]
        if mine_heads:
            want = max(nums + [0]) + 1
            for old in set(mine_heads):
                if int(old) != want:
                    text = text.replace(f"## {old}. Session `{MINE}", f"## {want}. Session `{MINE}")
                    text = text.replace(f"§{old}.x", f"§{want}.x")
    path.write_text(text)
    return True


def main():
    targets = sys.argv[1:] or ["COORDINATION.md", "pipeline/build.py", "index.html"]
    for name in targets:
        p = ROOT / name
        if p.exists() and resolve_text(p):
            print(f"resolved {name}")
        elif p.exists() and any(ln.startswith("<<<<<<<") for ln in p.read_text().splitlines()):
            print(f"UNRESOLVED {name}", file=sys.stderr)
    left = [
        str(p.relative_to(ROOT))
        for p in ROOT.rglob("*")
        if p.is_file() and p.suffix in {".py", ".html", ".md", ".json"}
        and "node_modules" not in p.parts and ".git" not in p.parts
        and any(ln.startswith("<<<<<<<") for ln in p.read_text(errors="ignore").splitlines()[:400])
    ]
    if left:
        print("markers still present: " + ", ".join(left), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
