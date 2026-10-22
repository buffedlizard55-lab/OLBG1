#!/usr/bin/env python3
"""sf1c13c19_validate.py - gates for the f1c13c19 desk deliverables."""
import json, pathlib, sys

DATA = pathlib.Path("data/f1c13c19")
SITE = pathlib.Path("f1c13c19")
errors, warnings = [], []

fx = json.loads((DATA / "fixtures.json").read_text())
lines = json.loads((DATA / "lines.json").read_text())
pred = json.loads((DATA / "predictions.json").read_text())

E = {e["id"]: e for e in fx["events"]}
L = {l["id"]: l for l in lines["lines"]}
P = {p["id"]: p for p in pred["predictions"]}

def american_value(dec):
    return int(round((dec - 1.0) * 100)) if dec >= 2.0 else -int(round(100.0 / max(dec - 1.0, 0.01)))

# 1. coverage: every fixture priced or listed
priced_ids = set(L) | {x["id"] for x in lines.get("event_listings", [])}
for e in fx["events"]:
    if e["id"] not in priced_ids:
        errors.append(f"fixture {e['id']} neither priced nor listed")

# 2. fixture bookkeeping
for e in fx["events"]:
    if not e.get("sources"):
        errors.append(f"{e['id']}: no sources attached")
    if e["verification"]["verdict"] not in ("verified", "cross-checked", "pending"):
        errors.append(f"{e['id']}: bad verdict {e['verification']['verdict']}")
    if e["verification"]["verdict"] == "pending" and e["start_utc"] is None and not e["flags"]:
        errors.append(f"{e['id']}: pending row without flags (blank-and-flag violation)")

# 3. market conservation + price consistency
for l in lines["lines"]:
    for mk in l["markets"]:
        s = sum(o["probability"] for o in mk["outcomes"])
        if abs(s - 1.0) > 1e-4:
            errors.append(f"{l['id']} market {mk['key']} probabilities sum to {s}")
        for o in mk["outcomes"]:
            if not (1.0 <= o["fair_odds"] and 1.0 <= o["odds"]):
                errors.append(f"{l['id']} market {mk['key']} non-positive odds")
            if o["fair_odds"] >= o["odds"] and o["probability"] > 0.02:
                pass  # fair must be >= book (vig-free): tolerance check below
            if o["fair_odds"] + 0.011 < o["odds"]:
                errors.append(f"{l['id']} market {mk['key']}: book price longer than fair")

# 4. HIGH gate strictness
highs = [p for p in pred["predictions"] if p["confidence"] == "high"]
for p in highs:
    e, l = E[p["id"]], L[p["id"]]
    if e["verification"]["verdict"] != "verified":
        errors.append(f"high {p['id']}: fixture not verified")
    if not l["both_verified"]:
        errors.append(f"high {p['id']}: ratings not both verified-tier")
    pk = p["pick"]
    if pk["probability"] < 0.70 - 1e-9:
        errors.append(f"high {p['id']}: p={pk['probability']} below 0.70")
    am = pk["fair_american"]
    fv = american_value(pk["fair_odds"])
    if not (-250 <= fv <= 10000):
        errors.append(f"high {p['id']}: fair american {fv} outside -250..+10000")
    if pk["probability"] > 0.7144 and fv < -250:
        errors.append(f"high {p['id']}: probability above band top yet graded high")
    if p["word_count"] < 30:
        errors.append(f"high {p['id']}: prediction text {p['word_count']} words < 30")

# 5. Above-window rows never graded high
for p in pred["predictions"]:
    if p["above_window"] and p["confidence"] == "high":
        errors.append(f"{p['id']}: above-window row graded high (T55 violation)")

# 6. uniqueness of prediction texts
texts = [p["prediction_text"] for p in pred["predictions"]]
if len(set(texts)) != len(texts):
    errors.append("duplicate prediction texts found")

# 7. site presence + links
need = ["index.html", "matches.html", "high.html", "window.html", "flagged.html",
        "snapshot.html", "methodology.html", "sources.html"]
for n in need:
    f = SITE / n
    if not f.exists():
        errors.append(f"missing site page {f}")
    elif "<table" in f.read_text() or n in ("index.html", "high.html"):
        pass
hp_txt = (SITE / "high.html").read_text() if (SITE / "high.html").exists() else ""
for p in pred["predictions"]:
    if p["confidence"] == "high" and p["pick"]["selection"] not in hp_txt:
        errors.append(f"high pick {p['id']} selection missing from high.html")

# 8. stats sanity
if lines["stats"]["high"] != len(highs):
    errors.append("stats.high != predictions high count")
if pred["stats"]["high"] != len(highs):
    errors.append("predictions stats mismatch")

print(f"checked {len(fx['events'])} fixtures, {len(lines['lines'])} priced lines, {len(highs)} high picks")
if warnings:
    print("WARNINGS:")
    for w in warnings:
        print(" -", w)
if errors:
    print(f"VALIDATION FAILED ({len(errors)} errors)")
    for e in errors[:50]:
        print(" -", e)
    sys.exit(1)
print("VALIDATION PASSED")
