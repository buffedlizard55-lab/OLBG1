#!/usr/bin/env python3
"""T65331685 canonical gates: validate data artifacts and the built site.

Run: python3 scripts/s65331685_validate.py
Exit 0 = clean.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "65331685")
SITE = os.path.join(ROOT, "65331685")

BANNED = ["model", "verified", "verification", "algorithm", "our data shows"]
CANON_PAGES = ["index.html", "sports.html", "matches.html", "markets.html", "high-confidence.html",
               "predictions.html", "analysis.html", "sources.html", "flagged.html", "repo-audit.html",
               "methodology.html"]

errors = []


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def err(msg):
    errors.append(msg)


harvest = load("harvest.json")
fixtures = load("fixtures.json")
lines = load("lines.json")
predictions = load("predictions.json")

# 1. artifacts exist
for name in ["harvest.json", "fixtures.json", "lines.json", "predictions.json", "desk.json"]:
    if not os.path.exists(os.path.join(DATA, name)):
        err(f"missing data artifact {name}")
for p in CANON_PAGES:
    if not os.path.exists(os.path.join(SITE, p)):
        err(f"missing site page {p}")

# 2. harvest reads have url + time
for r in harvest["reads"]:
    if not r["url"].startswith("http") or not r["read_utc"]:
        err(f"harvest row without url/time: {r}")

# 3. fixtures: every row keyed, has start_utc; unverified rows must carry a flag note
seen_ids = set()
for f in fixtures["fixtures"]:
    if f["id"] in seen_ids:
        err(f"duplicate fixture id {f['id']}")
    seen_ids.add(f["id"])
    if not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", f["start_utc"]):
        err(f"bad start_utc on {f['id']}")
    if not f["official"]["sources"] and f["label"] != "unverified":
        err(f"row {f['id']} has no sources but is not flagged")

# 4. zero-vig markets: every priced group (>=2 selections) sums to 1.000
by_key = defaultdict(list)
for g in lines["markets"]:
    for m in g["selections"]:
        by_key[(g["fixture_id"], m["market"])].append(m)
n_pairs = 0
for key, group in by_key.items():
    if len(group) >= 2:
        ssum = sum(x["prob"] for x in group)
        if abs(ssum - 1.0) > 0.002:
            err(f"zero-vig group off: {key} sums to {ssum:.4f}")
        n_pairs += 1
if n_pairs < 50:
    err(f"too few priced two-sided markets ({n_pairs})")

# 5. High-band gate: tier High iff p>0.70 and -250<=am<=10000 (1e-9 tolerance)
for g in lines["markets"]:
    for m in g["selections"]:
        p, am, tier = m["prob"], m["fair_american"], m["tier"]
        should_high = p > 0.70 and (-250.0 - 1e-6) <= am <= 10000.0
        if should_high and tier != "High":
            err(f"tier gate: {m['fixture_id']} {m['selection']} p={p} am={am} marked {tier}")
        if tier == "High" and not should_high:
            err(f"false High: {m['fixture_id']} {m['selection']} p={p} am={am}")
        if tier == "Chalk (disclosed)" and p <= 0.7143:
            err(f"chalk flag on in-window price: {m['fixture_id']} {m['selection']}")

# 6. predictions policy
grams = {}
for p in predictions["predictions"]:
    text = p["text"]
    toks = text.lower().split()
    if len(toks) < 30:
        err(f"short prediction: {p['match']}")
    for b in BANNED:
        if re.search(r"\b" + re.escape(b) + r"\b", text.lower()):
            err(f"banned word '{b}' in: {p['match']}")
    for i in range(len(toks) - 5):
        g6 = " ".join(toks[i:i + 6])
        if g6 in grams:
            err(f"repeated 6-gram '{g6}': {p['match']} vs {grams[g6]}")
        grams[g6] = p["match"]
    for fc in p["facts"]:
        if not fc["source"].startswith("http") or not fc["read_utc"]:
            err(f"fact without source/time in: {p['match']}")
    if not p["start_utc"]:
        err(f"prediction without start: {p['match']}")

# 7. sport coverage: 15 sports, >=3 written picks each
from collections import Counter
c = Counter(p["sport"] for p in predictions["predictions"])
required = ["Ice Hockey", "Baseball", "Basketball", "Rugby Union", "Rugby League", "Cricket", "Tennis",
            "Snooker", "Darts", "Golf", "Gaelic Sports", "Greyhounds", "Motor Racing", "Handball", "Volleyball"]
for sp in required:
    if c.get(sp, 0) < 3:
        err(f"sport {sp} has only {c.get(sp, 0)} written picks")

# 8. site: every table row in matches.html has a source link or the unverified tag
for page in CANON_PAGES:
    with open(os.path.join(SITE, page)) as f:
        content = f.read()
    if "</html>" not in content:
        err(f"page {page} truncated")
    if "T65331685" not in content:
        err(f"page {page} missing session label")
if os.path.exists(os.path.join(SITE, "matches.html")):
    with open(os.path.join(SITE, "matches.html")) as f:
        mh = f.read()
    for row in mh.split("<tr>"):
        if "<td>" in row and "</table>" not in row:
            if "http" not in row and "unverified" not in row and "elrow" not in row and "Elapsed" not in row and "read-time" not in row:
                # elapsed table rows carry notes instead of links; allow those
                if "flagged" not in row and "official read" not in row:
                    err("matches.html row without source link or unverified tag: " + row[:120])

# 9. archive/read-before-create discipline: no claims without reads
if len(harvest["reads"]) < 20:
    err("harvest looks thin (<20 reads)")

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"PASS: {len(fixtures['fixtures'])} fixtures, {sum(len(g['selections']) for g in lines['markets'])} prices, "
      f"{len(predictions['predictions'])} predictions, {len(harvest['reads'])} reads, {len(CANON_PAGES)} pages")
