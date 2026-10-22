#!/usr/bin/env python3
"""Stage the public static site only; never include Git, credentials, test tooling or dependencies."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / ".output/site"
EXTENSIONS = {".html", ".css", ".js", ".json", ".csv", ".md", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".txt", ".pdf", ".gz"}
EXCLUDED = {".git", ".github", ".cache", ".output", ".venv", "node_modules", "__pycache__", "scripts", "tests", ".arena", ".local", ".npm", "coverage", "dist", "build"}


def package():
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    copied = []
    for base, directories, files in os.walk(ROOT):
        directories[:] = sorted(d for d in directories if d not in EXCLUDED and not d.startswith("."))
        for name in sorted(files):
            source = Path(base) / name
            if source.is_symlink() or (source.suffix.lower() not in EXTENSIONS and name != ".nojekyll"):
                continue
            relative = source.relative_to(ROOT)
            target = DEST / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            copied.append({"path": relative.as_posix(), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    (DEST / ".nojekyll").touch()
    (DEST / "deployment-manifest.json").write_text(json.dumps({"scope": "Public static site; no Git, credentials or dependency files", "files": copied}, indent=2) + "\n")
    print(f"Staged {len(copied)} public files in .output/site")
    return copied


if __name__ == "__main__":
    package()
