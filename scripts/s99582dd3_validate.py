#!/usr/bin/env python3
"""Validator gate for the 99582dd3 independent verification desk.

Offline only. Checks:
  * every expected page exists with one <h1> and a <title>,
  * every internal relative link resolves inside the desk,
  * every sporting table row carries at least one external HTTPS link,
  * no HTTP (non-TLS) links and no empty href/src,
  * every rendered High grade truly clears 70% inside -250..+10000,
  * released prediction prose meets the writing gates,
  * the audit re-run is deterministic against the committed data.
"""
from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "99582dd3"
DATA = ROOT / "data" / "99582dd3"
sys.path.insert(0, str(ROOT / "scripts"))
import s99582dd3_audit as audit  # noqa: E402

PAGES = ["index.html", "todays-picks.html", "upcoming-picks.html", "markets.html",
         "predictions.html", "flagged.html", "sources.html", "repo-audit.html",
         "methodology.html"] + [f"sports/{slug}.html" for _, slug in audit.SPORTS]
FORBIDDEN = ("model", "verified")


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._tbody = 0
        self._policy_stack: list[str] = []
        self.row_policies: list[str] = []
        self.h1 = 0
        self.title = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.title += 1
        if tag == "table":
            self._policy_stack.append(d.get("data-row-policy", "source"))
        if tag == "tbody":
            self._tbody += 1
        if tag == "tr" and self._tbody:
            self._row = []
        if tag == "a" and d.get("href") is not None:
            self.links.append(d["href"])
            if self._row is not None:
                self._row.append(d["href"])
        if tag in ("link", "script", "img"):
            t = d.get("href") or d.get("src")
            if t is not None:
                self.links.append(t)

    def handle_endtag(self, tag):
        if tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self.row_policies.append(self._policy_stack[-1] if self._policy_stack else "source")
            self._row = None
        if tag == "tbody" and self._tbody:
            self._tbody -= 1
        if tag == "table" and self._policy_stack:
            self._policy_stack.pop()


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    slate = json.loads((DATA / "slate.json").read_text())
    flags = json.loads((DATA / "flags.json").read_text())
    preds = json.loads((DATA / "predictions_gated.json").read_text())

    # ---- data invariants -------------------------------------------------- #
    if len(slate) != 75:
        errors.append(f"expected 75 audited events, got {len(slate)}")
    sports = {r["sport"] for r in slate}
    if sports != {n for n, _ in audit.SPORTS}:
        errors.append(f"sport set mismatch: {sorted(sports)}")
    for name, _ in audit.SPORTS:
        if sum(1 for r in slate if r["sport"] == name) != 5:
            errors.append(f"{name} does not have exactly five events")
    for r in slate:
        if not r["official_urls"]:
            errors.append(f"{r['id']} has no official URL")
        for u in r["all_source_urls"]:
            p = urlparse(u)
            if p.scheme != "https":
                errors.append(f"{r['id']} non-HTTPS source {u}")
            if p.hostname not in audit.OFFICIAL_HOSTS and p.hostname not in audit.DISCOVERY_HOSTS:
                warnings.append(f"{r['id']} unregistered host {p.hostname}")
        rec = r["recommended"]
        if rec["is_high"]:
            if not (rec["prob"] > audit.HIGH_FLOOR and audit.AM_FLOOR <= rec["american"] <= audit.AM_CEIL):
                errors.append(f"{r['id']} high pick fails window/floor {rec}")
        for m in r["markets"]:
            if (m.get("confidence") or "").lower() == "high":
                if not (m["fair_prob"] > 0.70 and -250 <= m["fair_american"] <= 10000):
                    errors.append(f"{r['id']} market high fails rule: {m['market_label']}")
        if r["prediction"]:
            low = r["prediction"].lower()
            if any(w in low for w in FORBIDDEN):
                errors.append(f"{r['id']} prediction contains internal vocabulary")
            if len(r["prediction"].split()) < 30:
                errors.append(f"{r['id']} prediction under 30 words")

    # ---- pages + links ---------------------------------------------------- #
    for rel in PAGES:
        path = SITE / rel
        if not path.is_file():
            errors.append(f"missing page {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        c = Collector()
        c.feed(text)
        if c.h1 != 1:
            errors.append(f"{rel}: expected exactly one h1, got {c.h1}")
        if c.title != 1:
            errors.append(f"{rel}: expected one title")
        for href in c.links:
            if not href:
                errors.append(f"{rel}: empty href")
                continue
            if href.startswith(("https://", "mailto:", "#")):
                continue
            if href.startswith("http://"):
                errors.append(f"{rel}: non-HTTPS link {href}")
                continue
            clean = href.split("#", 1)[0].split("?", 1)[0]
            target = (path.parent / unquote(clean)).resolve()
            if not str(target).startswith(str(SITE.resolve())):
                errors.append(f"{rel}: link escapes desk {href}")
            elif not target.is_file():
                errors.append(f"{rel}: broken relative link {href}")
        # Sporting-data rows need an external HTTPS source. Audit pages and
        # internal-policy tables may cite desk pages for structural findings.
        audit_page = rel in ("flagged.html", "repo-audit.html", "methodology.html")
        for i, (row_links, policy) in enumerate(zip(c.rows, c.row_policies), 1):
            if policy == "internal":
                continue  # documentation tables (e.g. dataset inventory)
            if not row_links:
                errors.append(f"{rel}: table row {i} has no source link")
            elif policy == "source" and not audit_page \
                    and not any(h.startswith("https://") for h in row_links):
                errors.append(f"{rel}: table row {i} lacks an external HTTPS link")

    # ---- predictions page reflects gating --------------------------------- #
    released = [p for p in preds if not p["withheld"]]
    if len(released) != 75:
        warnings.append(f"{len(released)} released predictions (expected 75)")

    # ---- determinism: re-run into a temp tree ----------------------------- #
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        audit.run("2026-10-23T19:45:00Z", t)
        for name in ("slate.json", "flags.json", "predictions_gated.json", "sources.json"):
            if (t / name).read_text() != (DATA / name).read_text():
                errors.append(f"non-deterministic audit output: {name}")

    print(f"Desk validation: {len(errors)} errors, {len(warnings)} warnings "
          f"({len(PAGES)} pages, {len(slate)} events, {len(flags)} flags)")
    for w in warnings:
        print("WARN:", w)
    for err in errors:
        print("ERROR:", err)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
