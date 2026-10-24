#!/usr/bin/env python3
"""Line-by-line repository inventory and release-focused audit for desk 29dd717c."""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "29dd717c" / "repo-audit.json"
CURRENT_PREFIXES = (
    "29dd717c/", "data/29dd717c/", "scripts/s29dd717c_",
    "tests/pipeline/test_desk_29dd717c.py", "pipeline/", ".github/",
)
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz",
    ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".mp4", ".mov", ".avi", ".pyc",
}


def current(path):
    return path.startswith(CURRENT_PREFIXES) or path in {"COORDINATION.md", "index.html"}


def add(findings, path, line, check, excerpt, severity):
    findings.append({"path": path, "line": line, "check": check,
                     "excerpt": excerpt.strip()[:240], "severity": severity})


def main():
    paths = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    findings = []
    text_files = binary_files = lines_read = unreadable = 0
    bytes_read = 0
    for rel in paths:
        path = ROOT / rel
        if not path.is_file():
            add(findings, rel, 0, "Tracked path missing from checkout", "git ls-files entry has no readable file", "blocker" if current(rel) else "historical")
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            binary_files += 1
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            unreadable += 1
            add(findings, rel, 0, "Unreadable tracked file", str(exc), "blocker" if current(rel) else "historical")
            continue
        if b"\x00" in raw[:8192]:
            binary_files += 1
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")
            add(findings, rel, 0, "Non-UTF8 text required replacement decoding", "Manual encoding review advised", "review" if current(rel) else "historical")
        text_files += 1
        bytes_read += len(raw)
        is_current = current(rel)
        for number, line in enumerate(text.splitlines(), 1):
            lines_read += 1
            if re.match(r"^(<{7}|={7}|>{7})(?:\s|$)", line):
                add(findings, rel, number, "Unresolved merge-conflict marker", line,
                    "blocker" if is_current else "historical")
            if not is_current:
                continue
            if re.search(r"https?://(?:localhost|127\.0\.0\.1)(?::|/|\b)", line):
                add(findings, rel, number, "Browser-facing localhost URL", line, "blocker")
            if re.search(r"https?://(?:example\.com|example\.org)(?:/|\b)", line, re.I):
                add(findings, rel, number, "Placeholder external URL", line, "blocker")
            if (rel.startswith(("29dd717c/", "data/29dd717c/", "scripts/s29dd717c_"))
                    and rel not in {"scripts/s29dd717c_repo_audit.py", "data/29dd717c/repo-audit.json", "29dd717c/repository-audit.html"}):
                if re.search(r"href=[\"']#[\"']", line):
                    add(findings, rel, number, "Empty placeholder link", line, "blocker")
                if re.search(r"\b(?:TODO|FIXME)\b", line):
                    add(findings, rel, number, "Unresolved maintenance marker", line, "review")
    result = {
        "audit": "29dd717c repository line scan",
        "snapshot": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "scope": f"All {len(paths)} tracked paths inventoried; every readable tracked text file scanned line by line for conflict markers, with deeper release checks on pipeline, workflow, integration and desk files.",
        "tracked_files": len(paths), "text_files_scanned": text_files,
        "binary_files_skipped": binary_files, "unreadable_files": unreadable,
        "lines_scanned": lines_read, "bytes_read": bytes_read,
        "release_blockers": sum(x["severity"] == "blocker" for x in findings),
        "findings": findings,
        "limitations": [
            "Binary files are inventoried but not decoded or line-scanned.",
            "Historical desks receive structural conflict-marker scanning only; their old sporting facts are not recertified by this audit.",
            "Current-desk HTML local links and fragments are checked separately by the desk unit tests; official external URLs retain their documented read limitations.",
            "COORDINATION.md is scanned as a shared board, but historical TODO wording is not treated as a current release defect.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("tracked_files", "text_files_scanned", "lines_scanned", "release_blockers")} | {"findings": len(findings)}, indent=2))


if __name__ == "__main__":
    main()
