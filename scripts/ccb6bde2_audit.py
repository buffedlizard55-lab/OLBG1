#!/usr/bin/env python3
"""ccb6bde2_audit.py — line-by-line audit of the existing root-desk dataset + model.

Read-only: inspects data/fixtures.json, data/lines.json, data/predictions.json and
scripts/model.py configuration. Writes data/model_calibration-ccb6bde2.json.
Nothing here modifies prior sessions' files.
"""
import json, math, sys, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import model as M

fxdoc = json.loads((ROOT / "data" / "fixtures.json").read_text())
fx = fxdoc["fixtures"]
lindoc = json.loads((ROOT / "data" / "lines.json").read_text())
lines = {l["id"]: l for l in lindoc["lines"]}
preds = json.loads((ROOT / "data" / "predictions.json").read_text())["items"]

print("fixtures:", len(fx), "lines:", len(lines), "predictions:", len(preds))
print("by sport:", dict(collections.Counter(f["sport"] for f in fx)))
print("by status:", dict(collections.Counter(f["status"] for f in fx)))
print("fixture keys:", sorted(set().union(*[set(f.keys()) for f in fx])))

# --- input label survey -------------------------------------------------
labs = collections.Counter()
for f in fx:
    for side in ("home", "away"):
        inp = (f.get("inputs") or {}).get(side) or {}
        labs[(f["sport"], inp.get("label", "NONE"), "rating" in inp, bool(inp.get("bounded")))] += 1
for k, v in sorted(labs.items()):
    print(v, k)

# --- integrity checks ----------------------------------------------------
issues = []
ids = [f["id"] for f in fx]
if len(set(ids)) != len(ids):
    issues.append("DUPLICATE fixture ids")
for f in fx:
    if not f.get("sources") or not f["sources"][0].get("url"):
        issues.append(f"{f['id']}: missing official source link (brief: every row must carry one)")
    if f.get("away") and f["id"] not in lines:
        issues.append(f"{f['id']}: H2H fixture has no priced line")
    if not f.get("away") and f["id"] in lines:
        issues.append(f"{f['id']}: field event unexpectedly has a line")
    if not f.get("start_utc"):
        pass  # counted below — allowed but must be blank+flagged, checked via status
missing_utc = [f["id"] for f in fx if not f.get("start_utc")]
print("missing start_utc:", len(missing_utc), missing_utc[:40])

for lid, l in lines.items():
    s = l["home_probability"] + l["draw_probability"] + l["away_probability"]
    if abs(s - 1.0) > 0.0015:
        issues.append(f"{lid}: winner probs sum to {s}")
    for m in l["markets"]:
        ps = sum(o["probability"] for o in m["outcomes"])
        if abs(ps - 1.0) > 1e-4:
            issues.append(f"{lid} market {m['key']}: probs sum {ps}")
        for o in m["outcomes"]:
            if o["odds"] <= 1.0:
                issues.append(f"{lid} {m['key']}: odds {o['odds']} <= 1")
    if l["confidence"] == "high" and not l.get("both_measured"):
        issues.append(f"{lid}: HIGH confidence without both sides measured")

seen_text = set()
for p in preds:
    w = len(p["text"].split())
    if w < 30:
        issues.append(f"prediction {p['match_id']}: only {w} words")
    if p["text"] in seen_text:
        issues.append(f"prediction {p['match_id']}: duplicate text")
    seen_text.add(p["text"])
    ln = lines.get(p["match_id"])
    if ln and p["selection"] != ln["pick"]:
        issues.append(f"prediction {p['match_id']}: selection {p['selection']!r} != line pick {ln['pick']!r}")
print("INTEGRITY ISSUES:", len(issues))
for i in issues:
    print(" -", i)

# --- calibration curves --------------------------------------------------
def sigm(x): return 1 / (1 + math.exp(-x))
def logit(p): return math.log(p / (1 - p))

calib = {}
# tennis: rank pairs
pairs = [(1, 5), (1, 25), (1, 50), (1, 100), (5, 25), (5, 50), (10, 25), (10, 50), (20, 50), (30, 80), (50, 100)]
calib["tennis_rank_pairs"] = [
    {"rank_a": a, "rank_b": b, "rating_a": M.tennis_rank_rating(a), "rating_b": M.tennis_rank_rating(b),
     "p_favourite": round(sigm((M.tennis_rank_rating(a) - M.tennis_rank_rating(b)) / M.SPORTS["tennis"]["scale"]), 3)}
    for a, b in pairs]
spairs = [(1, 8), (1, 16), (1, 32), (1, 57), (5, 16), (5, 32), (10, 30), (20, 40), (25, 57)]
calib["snooker_rank_pairs"] = [
    {"rank_a": a, "rank_b": b, "rating_a": M.snooker_rating(a), "rating_b": M.snooker_rating(b),
     "p_favourite": round(sigm((M.snooker_rating(a) - M.snooker_rating(b)) / M.SPORTS["snooker"]["scale"]), 3)}
    for a, b in spairs]
# team sports: generic rating gaps
gaps = [5, 10, 15, 20, 30, 40]
calib["rating_gap_curves"] = {}
for slug, cfg in M.SPORTS.items():
    calib["rating_gap_curves"][slug] = {
        "scale": cfg["scale"], "p_base": cfg["p_base"], "high_threshold": cfg["high"], "med_threshold": cfg["med"],
        "p_home_by_gap": {g: round(sigm(logit(cfg["p_base"]) + g / cfg["scale"]), 3) for g in gaps}}
# confidence threshold spread
calib["confidence_threshold_range"] = {
    "high_min": min(c["high"] for c in M.SPORTS.values()),
    "high_max": max(c["high"] for c in M.SPORTS.values()),
    "by_sport": {k: {"high": v["high"], "med": v["med"]} for k, v in M.SPORTS.items()}}

# actual distribution of favourite probabilities among both-measured verified rows
dist = collections.Counter()
for l in lines.values():
    p = max(l["home_probability"], l["away_probability"])
    dist[(l["sport"], l["confidence"])] += 1
calib["confidence_counts_by_sport"] = {f"{k[0]}/{k[1]}": v for k, v in sorted(dist.items())}

# market families present
fam = collections.Counter()
for l in lines.values():
    for m in l["markets"]:
        fam[(l["sport"], m["key"])] += 1
calib["market_families_by_sport"] = {f"{k[0]}/{k[1]}": v for k, v in sorted(fam.items())}

# sample of extreme favourites and closest matches (sanity eyeball)
ranked = sorted(lines.values(), key=lambda l: -max(l["home_probability"], l["away_probability"]))
calib["strongest_favourites"] = [
    {"id": l["id"], "sport": l["sport"], "pick": l["pick"],
     "p": max(l["home_probability"], l["away_probability"]), "confidence": l["confidence"],
     "rating_home": l["rating_home"], "rating_away": l["rating_away"]} for l in ranked[:15]]
calib["integrity_issues"] = issues
calib["missing_start_utc"] = missing_utc

out = ROOT / "data" / "model_calibration-ccb6bde2.json"
out.write_text(json.dumps({"audited": "2026-10-21", "session": "ccb6bde2-olbg1",
                           "model_under_audit": lindoc["model"], **calib}, indent=2) + "\n")
print("wrote", out)
for r in calib["tennis_rank_pairs"]: print("tennis", r)
for r in calib["snooker_rank_pairs"]: print("snooker", r)
print("high threshold range:", calib["confidence_threshold_range"]["high_min"], "->", calib["confidence_threshold_range"]["high_max"])
print("strongest favourites:")
for s in calib["strongest_favourites"]: print("  ", s)
