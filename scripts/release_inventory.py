#!/usr/bin/env python3
"""Whole-repository line inventory and risk/source review register, not factual certification."""
from __future__ import annotations

import csv
import hashlib
import gzip
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = {"reports/release_file_inventory.csv", "reports/release_line_findings.csv", "reports/release_line_findings.csv.gz"}
URL = re.compile(r"https?://[^\s<>\"'`\\)\]]+")
RISK = re.compile(r"\b(?:verified|confirmed|high.confidence|calibrated|all markets|complete coverage|70%|no hallucinations)\b", re.I)


def inventory():
    raw = subprocess.check_output(["git", "ls-files", "-c", "-o", "--exclude-standard", "-z"], cwd=ROOT)
    paths = sorted(set(p.decode() for p in raw.split(b"\0") if p))
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    line_count = file_count = findings = 0
    with (reports / "release_file_inventory.csv").open("w", newline="") as files, (reports / "release_line_findings.csv").open("w", newline="") as lines:
        fw, lw = csv.writer(files), csv.writer(lines)
        fw.writerow(["path", "sha256", "bytes", "utf8_lines", "scope", "review_status", "manual_review_url"])
        lw.writerow(["path", "line", "kind", "excerpt", "urls_in_line", "manual_review_url", "verification_limit"])
        for relative in paths:
            path = ROOT / relative
            if relative in OUTPUTS or not path.is_file():
                continue  # generated self-referential audit CSVs cannot hash themselves
            content = path.read_bytes()
            try:
                text = content.decode("utf-8")
                split = text.splitlines()
                count = len(split)
            except UnicodeDecodeError:
                split, count = [], ""
            canonical = (relative.startswith(("data/release/", "scripts/release_", "tests/release/", ".github/workflows/"))
                         or relative in {"assets/release.css", "assets/release.js", "README.md"}
                         or ("/" not in relative and relative.endswith(".html")) or relative.startswith("sports/"))
            scope = "canonical release" if canonical else "historical/reference; not recertified"
            review = "automated fingerprint/line inventory; NOT manual factual verification"
            link = "https://github.com/buffedlizard55-lab/OLBG1/blob/arena/6ad5a3a8-olbg1/" + quote(relative)
            fw.writerow([relative, hashlib.sha256(content).hexdigest(), len(content), count, scope, review, link])
            file_count += 1
            if isinstance(count, int):
                line_count += count
            for number, line in enumerate(split, 1):
                urls = URL.findall(line)
                risk = bool(RISK.search(line))
                if not urls and not risk:
                    continue
                kind = "source URL + claim term" if urls and risk else "source URL" if urls else "claim term for review"
                # Do not pretend each matching line is either true or false.
                lw.writerow([relative, number, kind, line.strip()[:240], " ; ".join(dict.fromkeys(urls)),
                             link + "#L" + str(number), "offline inspection aid; external contents and historical claims not recertified"])
                findings += 1
    plain = reports / "release_line_findings.csv"
    (reports / "release_line_findings.csv.gz").write_bytes(gzip.compress(plain.read_bytes(), mtime=0))
    plain.unlink()
    print(f"Line inventory: {file_count} files; {line_count} UTF-8 lines; {findings} source/claim locations. No blanket factual certification.")
    return {"files": file_count, "lines": line_count, "locations": findings}


if __name__ == "__main__":
    inventory()
