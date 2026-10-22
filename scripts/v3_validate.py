#!/usr/bin/env python3
"""
v3_validate.py - release gates for the 22 October snapshot.

Exit code 0 only when every gate passes. Any failure prints the offending row.
"""
from __future__ import annotations

import json
import os
from html.parser import HTMLParser
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import v3_data as D          # noqa: E402
import v3_model as M         # noqa: E402
from v3_prose import HIGH_PROSE  # noqa: E402

errors: list[str] = []
warnings: list[str] = []


class _Tbl(HTMLParser):
    def __init__(self):
        super().__init__(); self.tables = []; self.done = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "table":
            self.tables.append({"h": 0, "rows": []})
        elif tag == "tr" and self.tables:
            self.tables[-1]["rows"].append(0)
        elif tag == "th" and self.tables:
            self.tables[-1]["h"] += 1
        elif tag == "td" and self.tables:
            self.tables[-1]["rows"][-1] += int(d.get("colspan", 1))

    def handle_endtag(self, tag):
        if tag == "table" and self.tables:
            self.done.append(self.tables.pop())


def check_tables():
    import glob
    bad = []
    for f in sorted(glob.glob(str(ROOT / "v3" / "*.html"))) + [str(ROOT / "index.html")]:
        p = _Tbl()
        p.feed(open(f, encoding="utf-8").read())
        for i, t in enumerate(p.done):
            if not t["h"]:
                continue
            for r in t["rows"]:
                if r not in (t["h"], 0):
                    bad.append(f"{os.path.basename(f)} table{i}: {t['h']} cols, row with {r}")
    return bad


def check(cond, msg):
    if not cond:
        errors.append(msg)


def main() -> int:
    priced = [M.price_fixture(f) for f in D.ALL]
    ids = [p["id"] for p in priced]
    check(len(ids) == len(set(ids)), "duplicate fixture ids")
    check(len(priced) >= 100, f"only {len(priced)} fixtures")

    snap = datetime(2026, 10, 22, tzinfo=timezone.utc)
    for p in priced:
        check(bool(p["home"]), f"{p['id']}: empty home")
        check(bool(p["competition"]), f"{p['id']}: empty competition")
        check(bool(p["sources"]), f"{p['id']}: no source")
        for s in p["sources"]:
            check(isinstance(s.get("url"), str) and s["url"].startswith("http"),
                  f"{p['id']}: bad source url {s.get('url')!r}")
        check(p["status"] in ("verified", "carried"), f"{p['id']}: bad status {p['status']}")
        if p["start_utc"]:
            dt = datetime.strptime(p["start_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            check(dt >= snap, f"{p['id']}: start {p['start_utc']} is not in the future")
        else:
            check(p["date_local"] is not None, f"{p['id']}: neither start_utc nor date_local")
            if p["date_local"]:
                dt = datetime.strptime(p["date_local"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                check(dt >= snap, f"{p['id']}: date {p['date_local']} is stale")
        if not p["event_only"]:
            check(bool(p["markets"]), f"{p['id']}: priced match with no markets")
            check(p["pick"] is not None, f"{p['id']}: no headline pick")
            for mk in p["markets"]:
                check(1.02 <= mk["price"] <= 60, f"{p['id']}: implausible price {mk['price']}")
                check(0 < mk["model_prob"] < 1, f"{p['id']}: bad probability")
            b = p["best_market"]
            if b and b["confidence"] == "High":
                check(b["model_prob"] >= 0.70, f"{p['id']}: High below 70%")
                check(1.40 <= b["price"] <= 101.0, f"{p['id']}: High outside band {b['price']}")
                check(bool(HIGH_PROSE.get(p["id"])), f"{p['id']}: High pick without bespoke prose")
            if p["status"] == "carried":
                check(not (b and b["confidence"] == "High"), f"{p['id']}: carried row graded High")

    highs = [p for p in priced if p["best_market"] and p["best_market"]["confidence"] == "High"]
    check(len(highs) >= 5, f"only {len(highs)} High picks")
    for p in highs:
        words = len(HIGH_PROSE[p["id"]].split())
        check(words >= 30, f"{p['id']}: prose {words} words")
    prose = [HIGH_PROSE[p["id"]] for p in highs]
    grams = set()
    for t in prose:
        toks = re.findall(r"[a-z0-9]+", t.lower())
        seen = set()
        for i in range(len(toks) - 5):
            g = " ".join(toks[i:i + 6])
            check(g not in grams, f"duplicate 6-gram in prose: {g}")
            check(g not in seen, f"repeated 6-gram inside one preview: {g}")
            seen.add(g)
        grams |= seen

    # built artefacts agree with the in-memory model
    fx = json.loads((ROOT / "data/v3/fixtures.json").read_text())
    ln = json.loads((ROOT / "data/v3/lines.json").read_text())
    pr = json.loads((ROOT / "data/v3/predictions.json").read_text())
    cv = json.loads((ROOT / "data/v3/coverage.json").read_text())
    check(fx["count"] == len(priced), "fixtures.json count mismatch")
    check(len(ln["books"]) == sum(1 for p in priced if not p["event_only"]), "lines.json book count")
    check(len(pr["picks"]) == sum(1 for p in priced if not p["event_only"]), "predictions.json count")
    check(sum(1 for x in pr["picks"] if x.get("no_pick_reason")) == pr.get("no_pick_count", -1),
          "predictions.json no_pick_count mismatch")
    check(pr["high_count"] == len(highs), "predictions.json high_count mismatch")
    check(cv["totals"]["fixtures"] == len(priced), "coverage totals mismatch")

    pages = sorted((ROOT / "v3").glob("*.html")) + [ROOT / "index.html"]
    check(len(pages) >= 20, f"only {len(pages)} html pages")
    for pg in pages:
        t = pg.read_text(encoding="utf-8")
        check(len(t) > 2000, f"{pg.name}: suspiciously small")
        check("None" not in t.replace("NoneType", ""), f"{pg.name}: contains a None artefact")
        check("{" not in t.split("<body")[1][:200], f"{pg.name}: unrendered template")
        check(t.count("<table") == t.count("</table>"), f"{pg.name}: unbalanced tables")
        check(t.count("<details") == t.count("</details>"), f"{pg.name}: unbalanced details")
        check("http" in t, f"{pg.name}: no source links")

    print(f"fixtures {len(priced)} | priced {sum(1 for p in priced if not p['event_only'])} | "
          f"markets {sum(len(p['markets']) for p in priced)} | High {len(highs)} | pages {len(pages)}")
    for w in warnings:
        print("WARN " + w)
    for b in check_tables():
        errors.append("ragged table — " + b)

    if errors:
        for e in errors[:40]:
            print("FAIL " + e)
        print(f"{len(errors)} errors")
        return 1
    print("PASS 0 errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
