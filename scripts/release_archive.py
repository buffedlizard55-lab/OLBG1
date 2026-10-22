#!/usr/bin/env python3
"""One-time, non-destructive archive of superseded root pages and sport pages."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive/pre-release-20261022"
MANIFEST = ROOT / "data/release/archive.json"


def preserve():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    originals = sorted(list(ROOT.glob("*.html")) + list((ROOT / "sports").glob("*.html")))
    archived = {path.relative_to(ROOT).as_posix() for path in originals}
    records = []
    for path in originals:
        relative = path.relative_to(ROOT)
        dest = ARCHIVE / relative
        text = path.read_text()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()

        def rewrite(match):
            attr, quote, href = match.groups()
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
                return match.group(0)
            target = (path.parent / unquote(parsed.path)).resolve()
            try:
                rel = target.relative_to(ROOT).as_posix()
            except ValueError:
                return match.group(0)
            target = ARCHIVE / rel if rel in archived else target
            rewritten = os.path.relpath(target, dest.parent).replace(os.sep, "/")
            return attr + "=" + quote + urlunsplit(("", "", rewritten, parsed.query, parsed.fragment)) + quote

        text = re.sub(r"\b(href|src)\s*=\s*(['\"])(.*?)\2", rewrite, text, flags=re.I)
        back = os.path.relpath(ROOT / "index.html", dest.parent).replace(os.sep, "/")
        banner = ('<aside role="note" style="padding:18px;background:#fff2ce;color:#392b00;border-bottom:3px solid #bb8000;position:relative;z-index:9999">'
                  '<strong>Archived snapshot — not current betting advice.</strong> Prior facts, prices and verification labels are unrecertified. '
                  f'<a style="color:#003c88;text-decoration:underline" href="{back}">Open the evidence-first dashboard</a>.</aside>')
        text = re.sub(r"(<body\b[^>]*>)", lambda m: m.group(1) + banner, text, count=1, flags=re.I)
        text = text.replace("</head>", '<meta name="robots" content="noindex,nofollow"></head>', 1)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
        records.append({"original": relative.as_posix(), "original_sha256": digest,
                        "archive_path": dest.relative_to(ROOT).as_posix(),
                        "changes": "Local links rebased and historical warning inserted; originals otherwise retained."})
    shutil.copy2(ROOT / "README.md", ARCHIVE / "README.md")
    data = {"archive": ARCHIVE.relative_to(ROOT).as_posix(),
            "policy": "Prior root and sports pages archived before canonical replacement. Session namespaces, old datasets and old generators are unchanged.",
            "files": records}
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n")
    return data


if __name__ == "__main__":
    print(f"Preserved {len(preserve()['files'])} superseded primary HTML files")
