#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the fec05fb4 desk: data invariants, gate compliance and site integrity."""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "fec05fb4"
DESK = json.loads((ROOT / "data" / "fec05fb4" / "desk.json").read_text())

FAIL: list[str] = []
WARN: list[str] = []
OK = 0


def check(cond: bool, msg: str) -> None:
    global OK
    if cond:
        OK += 1
    else:
        FAIL.append(msg)


# --------------------------------------------------------------------------
# 1. structural JSON checks
# --------------------------------------------------------------------------
def walk(obj, path="desk"):
    if isinstance(obj, float):
        check(math.isfinite(obj), f"non-finite number at {path}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{path}[{i}]")


walk(DESK)
rows = DESK["rows"]
listings = DESK["listing_only"]
counts = DESK["counts"]
cov = DESK["coverage"]
preds = DESK["predictions"]
flags = DESK["flagged"]

check(len(cov) == 17, "coverage must have 17 categories")
check(len(rows) == counts["upcoming"], "counts.upcoming mismatch")
check(len(listings) == counts["listing_only"], "counts.listing_only mismatch")
check(sum(c["upcoming"] for c in cov) == len(rows), "coverage upcoming sum mismatch")
check(sum(c["listings"] for c in cov) == len(listings), "coverage listing sum mismatch")
check(sum(c["high"] for c in cov) == counts["high"], "coverage high sum mismatch")
check(sum(1 for r in rows if r["tier"] == "High") == counts["high"], "high count mismatch")
check(sum(1 for r in rows if r["tier"] == "Medium") == counts["medium"], "medium count mismatch")
check(sum(1 for r in rows if r["tier"] == "Low") == counts["low"], "low count mismatch")
check(sum(1 for r in rows if r["tier"] == "Unpriced") == counts["unpriced"], "unpriced count mismatch")
check(sum(len(r["markets"]) for r in rows) == counts["markets"], "market count mismatch")
check(sum(len(m["outcomes"]) for r in rows for m in r["markets"]) == counts["outcomes"], "outcome count mismatch")
check(len(preds) == counts["predictions"], "prediction count mismatch")
check(len(flags) == counts["flags"], "flag count mismatch")

EXCLUDED = {"football", "soccer", "american-football", "boxing", "ufc", "mma", "hurling",
            "horse-racing", "cycling", "specials"}
for r in rows + listings:
    check(r["sport"] not in EXCLUDED, f"excluded sport present: {r['id']} {r['sport']}")

ids = [r["id"] for r in rows] + [r["id"] for r in listings]
check(len(ids) == len(set(ids)), "duplicate fixture ids across upcoming + listings")

# every priced row has both sides and an official source
for r in rows:
    if r["tier"] in ("High", "Medium", "Low"):
        check(bool(r["winner"]), f"{r['id']}: priced without winner")
        check(bool(r["selection"]), f"{r['id']}: priced without selection")
        check(bool(r["official_sources"]), f"{r['id']}: priced without an official source")
        check(all(s["url"].startswith("https://") for s in r["official_sources"]),
              f"{r['id']}: non-https source")
    else:
        check(r["selection"] is None, f"{r['id']}: unpriced row carries a selection")
    check(bool(r["home"]), f"{r['id']}: missing home")
    if r["start_utc"]:
        check(r["start_utc"] > DESK["as_of"], f"{r['id']}: upcoming row starts before the cut-off")

# listing rows must never be priced and must carry a flag
for r in listings:
    check(r["tier"] == "Unpriced", f"listing {r['id']} is priced")
    check(r["selection"] is None, f"listing {r['id']} has a selection")
    check(bool(r["flags"]), f"listing {r['id']} has no flag")
    if r["start_utc"] is None:
        check("start_utc" in (r["missing_fields"] or []), f"listing {r['id']} blank time not declared")

# --------------------------------------------------------------------------
# 2. market arithmetic
# --------------------------------------------------------------------------
for r in rows:
    for m in r["markets"]:
        check(len(m["outcomes"]) in (2, 3), f"{r['id']}/{m['key']}: outcome count {len(m['outcomes'])}")
        total = sum(o["probability"] for o in m["outcomes"])
        check(abs(total - 1.0) < 1e-6, f"{r['id']}/{m['key']}: probabilities sum to {total}")
        for o in m["outcomes"]:
            p = o["probability"]
            check(0 < p < 1, f"{r['id']}: probability out of range")
            check(abs(o["fair_decimal"] * p - 1.0) < 1e-5,
                  f"{r['id']}: fair decimal {o['fair_decimal']} not 1/p for {o['selection']}")
            am = o["fair_american"]
            check(am is not None, f"{r['id']}: missing fair American price")
            # -250 .. +10000 band is exactly 1.4 decimal .. 101.0 decimal
            check(o["in_band"] == (0.70 < p <= 0.714286 and 1.4 <= 1 / p <= 101.0 + 1e-9),
                  f"{r['id']}: in_band flag disagrees with p for {o['selection']}")

# --------------------------------------------------------------------------
# 3. High gate
# --------------------------------------------------------------------------
highs = [r for r in rows if r["tier"] == "High"]
check(len(highs) >= 1, "no High selections at all")
check(len(highs) == len(preds), "each High must have exactly one prediction")
for r in highs:
    s = r["selection"]
    check(s["in_band"], f"{r['id']}: High outside the 70-71.43 band")
    check(0.70 < s["probability"] <= 0.714286, f"{r['id']}: High probability {s['probability']}")
    check(s["fair_american"] is not None and -250 <= s["fair_american"] <= 10000,
          f"{r['id']}: High fair price outside -250..+10000")
    check(r["evidence_status"] == "fresh", f"{r['id']}: High on carried evidence")
    check(r["tier"] == "High" and r["prediction_id"] == r["id"], f"{r['id']}: prediction wiring")
    check(len(r["official_sources"]) >= 2, f"{r['id']}: High needs at least two official source links")
    check("confirmed" in json.dumps(r).lower(), f"{r['id']}: no availability confirmation recorded")

for r in rows:
    if r["evidence_status"] == "carried":
        check(r["tier"] != "High", f"{r['id']}: carried evidence promoted to High")

# --------------------------------------------------------------------------
# 4. predictions
# --------------------------------------------------------------------------
seen_six = {}
for p in preds:
    words = p["text"].split()
    check(len(words) >= 30, f"{p['fixture_id']}: prediction only {len(words)} words")
    check(len(words) <= 140, f"{p['fixture_id']}: prediction is {len(words)} words")
    check(len(p["facts"]) >= 3, f"{p['fixture_id']}: fewer than three verified facts")
    check(p["selection"] in p["text"], f"{p['fixture_id']}: prediction does not name the selection")
    sel_row = next(r for r in rows if r["id"] == p["fixture_id"])
    check(sel_row["tier"] == "High", f"{p['fixture_id']}: prediction on a non-High row")
    check(f"{p['probability']:.6f}" == f"{sel_row['selection']['probability']:.6f}",
          f"{p['fixture_id']}: predicted probability differs from the row")
    check("Selection:" in p["text"], f"{p['fixture_id']}: no explicit selection sentence")
    check(len({s['url'] for s in p['sources']}) >= 2, f"{p['fixture_id']}: fewer than two source links")
    toks = re.findall(r"[a-z0-9']+", p["text"].lower())
    for i in range(len(toks) - 5):
        g = " ".join(toks[i:i + 6])
        check(g not in seen_six or seen_six[g] == p["fixture_id"],
              f"{p['fixture_id']}: repeats 6-gram '{g}' from {seen_six.get(g)}")
        seen_six.setdefault(g, p["fixture_id"])
    check(p["text"].count("Selection:") == 1, f"{p['fixture_id']}: multiple selection sentences")

# no prediction text repeated
texts = [p["text"] for p in preds]
check(len(texts) == len(set(texts)), "duplicate prediction text")

# --------------------------------------------------------------------------
# 5. flags
# --------------------------------------------------------------------------
fids = [f["id"] for f in flags]
check(len(fids) == len(set(fids)), "duplicate flag ids")
for f in flags:
    check(f["title"] and f["detail"] and f["source"], f"flag {f['id']} incomplete")
    check(f["severity"] in ("high", "medium", "low"), f"flag {f['id']} severity")

# --------------------------------------------------------------------------
# 6. HTML
# --------------------------------------------------------------------------
class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables: list[list] = []          # stack of audit modes
        self.in_thead = [False]
        self.in_tbody = [False]
        self.row_has_link: list[list] = []
        self.ids: Counter = Counter()
        self.h1 = 0
        self.links: list[str] = []
        self.snapshot = None
        self.row_is_detail = False
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.snapshot = a.get("data-snapshot")
        if a.get("id"):
            self.ids[a["id"]] += 1
        if tag == "h1":
            self.h1 += 1
        if tag == "table":
            self.tables.append({"mode": a.get("data-audit", "none"), "link": False, "detail": False})
            self.in_thead.append(False)
            self.in_tbody.append(False)
        elif tag == "thead" and self.in_thead:
            self.in_thead[-1] = True
        elif tag == "tbody" and self.in_tbody:
            self.in_tbody[-1] = True
        elif tag == "tr" and self.tables:
            self.tables[-1]["link"] = False
            self.tables[-1]["detail"] = "detail" in (a.get("class") or "")
        elif tag == "a":
            href = a.get("href", "")
            self.links.append(href)
            if href.startswith("https://") and self.tables:
                self.tables[-1]["link"] = True

    def handle_endtag(self, tag):
        if tag == "table" and self.tables:
            self.tables.pop()
            self.in_thead.pop()
            self.in_tbody.pop()
        elif tag == "thead" and self.in_thead:
            self.in_thead[-1] = False
        elif tag == "tbody" and self.in_tbody:
            self.in_tbody[-1] = False
        elif tag == "tr" and self.tables:
            cur = self.tables[-1]
            if cur["mode"] == "row" and self.in_tbody[-1] and not self.in_thead[-1] and not cur["detail"]:
                self.row_has_link.append([cur["link"], ""])


pages = sorted(SITE.rglob("*.html"))
check(len(pages) == 25, f"expected 25 pages, found {len(pages)}")
for sport in [c["sport"] for c in cov]:
    check((SITE / "sports" / f"{sport}.html").exists(), f"missing sport page {sport}")

for page_file in pages:
    ap = Audit()
    ap.feed(page_file.read_text(encoding="utf-8"))
    rel = page_file.relative_to(SITE)
    check(ap.h1 == 1, f"{rel}: {ap.h1} h1 elements")
    check(ap.snapshot == "2026-10-22T12:45:00Z", f"{rel}: missing/incorrect data-snapshot")
    dups = [k for k, v in ap.ids.items() if v > 1]
    check(not dups, f"{rel}: duplicate ids {dups[:4]}")
    empty = [i for i, (has, _) in enumerate(ap.row_has_link) if not has]
    check(not empty, f"{rel}: {len(empty)} data rows without an https source link")
    for href in ap.links:
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = (page_file.parent / href.split("#")[0]).resolve()
        check(target.exists(), f"{rel}: broken local link {href}")

text_all = "\n".join(p.read_text(encoding="utf-8") for p in pages)
for bad in ("localhost", "127.0.0.1", "http://"):
    check(bad not in text_all, f"site contains {bad}")

# --------------------------------------------------------------------------
# 7. excluded-scope words must not appear as covered categories
# --------------------------------------------------------------------------
for page_file in pages:
    if page_file.name in ("methodology.html", "flagged.html", "index.html"):
        continue
    txt = page_file.read_text(encoding="utf-8").lower()
    for word in ("horse racing", "ufc", "boxing"):
        if word in txt:
            WARN.append(f"{page_file.name} mentions '{word}' (check it is an exclusion note)")

# --------------------------------------------------------------------------
print(f"PASS checks: {OK}")
if WARN:
    print(f"WARNINGS ({len(WARN)}):")
    for w in WARN:
        print("  !", w)
if FAIL:
    print(f"FAILURES ({len(FAIL)}):")
    for f in FAIL[:60]:
        print("  x", f)
    sys.exit(1)
print("fec05fb4 validation: PASS")
print(f"  rows={len(rows)} listings={len(listings)} pages={len(pages)} High={len(highs)} predictions={len(preds)} flags={len(flags)}")
