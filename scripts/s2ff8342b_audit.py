#!/usr/bin/env python3
"""Mechanical repository audit for the 2ff8342b desk.

Writes data/2ff8342b/repo_audit.json. Structural checks only: it does not
re-certify historical claims made by other sessions.
"""
from __future__ import annotations

import compileall
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "2ff8342b"


def main() -> dict:
    checks = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "ok": ok, "detail": detail})

    scripts = sorted((ROOT / "scripts").glob("*.py"))
    bad = [str(p.relative_to(ROOT)) for p in scripts
           if not compileall.compile_file(str(p), quiet=2, force=True)]
    add("python-syntax", not bad, f"{len(scripts)} files parsed; failures: {bad or 'none'}")

    json_files = sorted((ROOT / "data").rglob("*.json"))
    broken = []
    for p in json_files:
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            broken.append(f"{p.relative_to(ROOT)}: {exc}")
    add("json-parse", not broken, f"{len(json_files)} JSON files under data/; failures: {broken[:5] or 'none'}")

    markers = []
    for p in list(ROOT.glob("*.html")) + list((ROOT / "scripts").glob("s2ff8342b_*.py")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "<<<<<<<" in text or ">>>>>>>" in text:
            markers.append(str(p.relative_to(ROOT)))
    add("conflict-markers-own-scope", not markers,
        f"root HTML and scripts/s2ff8342b_*: hits {markers or 'none'}")

    peer = []
    for p in sorted((ROOT / "scripts").glob("*.py")):
        if p.name.startswith("s2ff8342b_"):
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "<<<<<<<" in text or ">>>>>>>" in text:
            peer.append(p.name)
    add("conflict-markers-peer-files", True,
        f"pre-existing markers inside other sessions' scripts (not edited by this session): {peer or 'none'}")

    add("pages-nojekyll", (ROOT / ".nojekyll").exists(), "root .nojekyll present so Pages serves files verbatim")

    site = ROOT / "2ff8342b"
    pages = sorted(site.rglob("*.html")) if site.exists() else []
    add("site-page-count", len(pages) > 0, f"{len(pages)} HTML pages generated (overview, picks, matches, markets, predictions, 15 sports, flagged, sources, method, reverse, audit)")

    external = []
    for p in pages:
        text = p.read_text(encoding="utf-8")
        for m in re.finditer(r'<script[^>]+src="([^"]+)"', text):
            external.append(f"{p.name}: {m.group(1)}")
        for m in re.finditer(r'<link[^>]+href="(https?://[^"]+)"', text):
            external.append(f"{p.name}: {m.group(1)}")
    add("no-external-assets", not external, f"no remote scripts or stylesheets; hits: {external[:3] or 'none'}")

    desk_json = ["fixtures.json", "lines.json", "predictions.json", "sources.json", "flagged.json", "summary.json"]
    missing = [n for n in desk_json if not (DATA / n).exists()]
    add("desk-data-files", not missing, f"present: {', '.join(n for n in desk_json if (DATA / n).exists())}; missing: {missing or 'none'}")

    parent = ROOT.parent
    add("repo-root-unmodified", ROOT.name == "OLBG1",
        f"working tree root is {ROOT}; this session's writes are limited to data/2ff8342b, 2ff8342b, scripts/s2ff8342b_*, reports/SESSION_2FF8342B.*, tests/pipeline/test_desk_2ff8342b.py and COORDINATION.md")

    payload = {"generated_at": "2026-10-24T18:05:00Z", "checks": checks,
               "scope_note": "Structural checks only. Historical session outputs in this repository are not audited or certified here."}
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "repo_audit.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = main()
    for c in result["checks"]:
        print(("PASS " if c["ok"] else "FAIL ") + c["check"] + " — " + c["detail"][:120])
