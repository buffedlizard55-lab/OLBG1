"""Gate for the 9dc28d1e desk.

Eight checks. Any failure exits non-zero.

1  counts in desk.json match the rows actually present
2  every price is internally consistent (decimal, American, probability)
3  the tier rule is applied exactly as documented, and every High has a prediction
4  predictions are unique prose of at least thirty words with no shared eight-gram
5  every verified fixture cites a source that exists in the register
6  every page links only to files that exist, with relative paths
7  the seventeen in-scope categories all have a page; excluded categories appear nowhere
8  the observation window, timestamps and gate constants are the documented ones
"""

from __future__ import annotations

import json
import re
import sys
from itertools import combinations
from pathlib import Path

import s9dc28d1e_inputs as I
import s9dc28d1e_model as M

ROOT = Path(__file__).resolve().parent.parent
SID = "9dc28d1e"
SITE = ROOT / SID
DESK = ROOT / "data" / SID / "desk.json"

errors: list[str] = []
warnings: list[str] = []


def check(condition, message):
    if not condition:
        errors.append(message)


def main():
    if not DESK.exists():
        print("9DC28D1E VALIDATION FAILED: data/9dc28d1e/desk.json missing; run the builder first")
        return 1

    desk = json.loads(DESK.read_text())
    outcomes = desk["outcomes"]
    fixtures = desk["fixtures"]
    predictions = desk["predictions"]
    counts = desk["counts"]

    # 1 -- counts ---------------------------------------------------------
    check(counts["fixtures"] == len(fixtures), f"fixture count {counts['fixtures']} != {len(fixtures)}")
    check(counts["markets"] == len(desk["markets"]), "market count mismatch")
    check(counts["outcomes"] == len(outcomes), "outcome count mismatch")
    check(counts["priced_matches"] == sum(1 for f in fixtures if f["status"].startswith("verified")),
          "priced match count mismatch")
    check(counts["high"] == sum(1 for o in outcomes if o["tier"] == "HIGH"), "High count mismatch")
    check(counts["medium"] == sum(1 for o in outcomes if o["tier"] == "MEDIUM"), "Medium count mismatch")
    check(counts["low"] == sum(1 for o in outcomes if o["tier"] == "LOW"), "Low count mismatch")
    check(counts["predictions"] == len(predictions), "prediction count mismatch")
    check(counts["findings"] == len(desk["findings"]), "finding count mismatch")
    check(counts["sports"] == 17, "sport count must be 17")

    # 2 -- prices ---------------------------------------------------------
    for o in outcomes:
        p = o["probability"]
        if not 0.0 < p < 1.0:
            errors.append(f"probability out of range: {o['id']} {p}")
            continue
        if abs(o["fair_decimal"] * p - 1.0) > 2e-3:
            errors.append(f"decimal does not match probability: {o['id']} {o['fair_decimal']} x {p}")
        expected = M.american_from_probability(p)
        if abs(expected - o["american"]) > 0.02:
            errors.append(f"American price does not match probability: {o['id']} {o['american']} vs {expected}")

    # 3 -- tier rule ------------------------------------------------------
    predicted = {(p["fixture_id"], p["selection"]) for p in predictions}
    for o in outcomes:
        p, am = o["probability"], o["american"]
        qualifies = p > M.HIGH_PROB_FLOOR and M.in_price_window(am)
        if o["tier"] == "HIGH":
            check(qualifies, f"High row fails the gate: {o['id']}")
            check((o["fixture_id"], o["selection"]) in predicted, f"High without a prediction: {o['id']}")
        else:
            check(not (qualifies and (o["fixture_id"], o["selection"]) in predicted),
                  f"predicted selection is not tiered High: {o['id']}")
        if o["tier"] == "MEDIUM" and not o["reason"]:
            # a Medium inside the band must say why it was not promoted
            if qualifies:
                errors.append(f"in-band Medium without a reason: {o['id']}")
        check(o["sensitivity_low"] <= p <= o["sensitivity_high"],
              f"sensitivity range does not contain the point estimate: {o['id']}")

    # 4 -- prose ----------------------------------------------------------
    grams = {}
    for p in predictions:
        words = p["body"].split()
        if len(words) < 30:
            errors.append(f"prediction under thirty words: {p['headline']} ({len(words)})")
        if len(set(words)) < len(words) * 0.5:
            warnings.append(f"prediction looks repetitive: {p['headline']}")
        lowered = re.findall(r"[a-z']+", p["body"].lower())
        for i in range(len(lowered) - 7):
            grams.setdefault(" ".join(lowered[i:i + 8]), []).append(p["headline"])
    for gram, owners in grams.items():
        if len(set(owners)) > 1:
            errors.append(f"shared eight-gram across predictions: '{gram}'")
    if len({p["headline"] for p in predictions}) != len(predictions):
        errors.append("duplicate prediction headlines")

    # 5 -- sources --------------------------------------------------------
    for f in fixtures:
        if f["status"].startswith("verified"):
            check(f["source_ids"], f"verified fixture without source ids: {f['id']}")
            for sid in f["source_ids"]:
                check(sid in desk["sources"], f"unknown source id {sid} on {f['id']}")
    for p in predictions:
        for _k, _v, src in p["facts"]:
            check(src in desk["sources"], f"prediction fact cites unknown source {src}")

    # 6 -- links ----------------------------------------------------------
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        errors.append("no pages built")
    href_re = re.compile(r'(?:href|src)="([^"]+)"')
    for path in pages:
        text = path.read_text()
        if 'href="/' in text or 'src="/' in text:
            errors.append(f"root-absolute link in {path.relative_to(ROOT)}")
        for target in href_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#")[0].split("?")[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"broken link in {path.relative_to(ROOT)} -> {target}")
    check((SITE / "index.html").exists(), "dashboard missing")
    check((SITE / "assets" / "style.css").exists(), "stylesheet missing")

    # 7 -- categories -----------------------------------------------------
    for slug, name, _rid in I.SPORTS:
        check((SITE / "sports" / f"{slug}.html").exists(), f"missing sport page: {slug}")
    excluded_names = {name for name, _rid in I.EXCLUDED_SPORTS}
    for f in fixtures:
        check(f["sport"] not in excluded_names, f"excluded category present: {f['sport']} ({f['id']})")
    dash = (SITE / "index.html").read_text()
    for name in sorted(excluded_names):
        check(f'>{name}</a></h4>' not in dash, f"excluded category carded on the dashboard: {name}")

    # 8 -- metadata -------------------------------------------------------
    check(desk["window"]["start"] == "2026-10-22T12:11:00Z", "window start changed")
    check(desk["window"]["end"] == "2026-10-25T12:11:00Z", "window end changed")
    check(desk["gate"] == {"probability_floor": 0.70, "short_edge": -250, "long_edge": 10000},
          "gate constants changed")
    check(desk["generated_at"].startswith("2026-10-22T"), "generated-at stamp is not the session date")
    for sid, src in desk["sources"].items():
        check(src["url"].startswith("https://"), f"source {sid} is not https")
        check(src["observed_at"].startswith("2026-10-22T"), f"source {sid} has no session timestamp")

    # report --------------------------------------------------------------
    if warnings:
        for w in warnings:
            print(f"warning: {w}")
    if errors:
        print(f"9DC28D1E VALIDATION FAILED: {len(errors)} error(s)")
        for e in errors[:40]:
            print(f"  - {e}")
        return 1
    print(
        "9DC28D1E VALIDATION PASSED: "
        f"priced={counts['priced_matches']} outcomes={counts['outcomes']} high={counts['high']} "
        f"predictions={counts['predictions']} pages={len(pages)} errors=0 warnings={len(warnings)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
