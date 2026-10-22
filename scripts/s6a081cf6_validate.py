#!/usr/bin/env python3
import json, re, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, "data/6a081cf6_high_band.json")))
errs = []
from collections import Counter
c = Counter()
for r in d["picks"]:
    if not (r["prob_pct"] > 70 and -250 <= r["us"] <= 10000): errs.append(f"band {r['fixture_id']}")
    if r["word_count"] < 30: errs.append(f"words {r['fixture_id']}")
    if not r["sources"]: errs.append(f"no source {r['fixture_id']}")
    w = re.findall(r"[a-z0-9']+", r["prediction"].lower())
    for i in range(len(w)-5): c[" ".join(w[i:i+6])] += 1
dups = [k for k, v in c.items() if v > 1]
if dups: errs.append(f"duplicate 6-grams: {dups[:3]}")
for f in ["index.html", "picks.html", "flagged.html", "methodology.html"]:
    t = open(os.path.join(ROOT, "6a081cf6", f)).read()
    for href in re.findall(r'href="([^"]+)"', t):
        if href.startswith("http"): continue
        if not os.path.exists(os.path.normpath(os.path.join(ROOT, "6a081cf6", href))): errs.append(f"broken {f}:{href}")
print("ERRORS" if errs else "PASS", errs if errs else f"— {d['count']} strict-band picks, all >70%, >=30 words, sourced, links OK")
sys.exit(1 if errs else 0)
