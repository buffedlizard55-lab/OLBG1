#!/usr/bin/env python3
"""TC3026353 desk validator — row-level gates before any merge.

Checks:
  1. every fixture carries at least one official https:// source link
  2. every prediction text >= 30 words, names its selection, and contains
     neither banned word ('model', 'verified' — substring match)
  3. prediction texts share no repeated 5-gram
  4. tier labels match the published gate arithmetic (recomputed)
  5. priced rows: decimal == 1/p and tier arithmetic consistent
  6. summary counts consistent with the row sets
  7. required HTML pages exist and contain no banned words in body text

Usage: python3 scripts/sc3026353_validate.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from sc3026353_model import p_to_american, tier  # noqa: E402

BANNED = ("model", "verified")
SITE = ROOT / "c3026353"
DATA = ROOT / "data" / "c3026353"

REQUIRED_PAGES = [
    "index.html", "matches.html", "markets.html", "high-confidence.html",
    "predictions.html", "analysis.html", "sources.html", "flagged.html",
    "methodology.html", "reverse-engineering.html", "repo-audit.html",
]


def words(text):
    return re.findall(r"[A-Za-z0-9'’\u2010-\u2027-]+", text)


def fivegrams(text):
    w = [x.lower() for x in words(text)]
    return {" ".join(w[i:i + 5]) for i in range(max(0, len(w) - 4))}


def check(loaded=True):
    errors, warnings, stats = [], [], {}
    if not DATA.exists():
        return (["data exports missing — run scripts/sc3026353_build.py first"], [], {})
    preds = json.loads((DATA / "predictions.json").read_text())["rows"]
    markets = json.loads((DATA / "markets.json").read_text())["rows"]
    fixtures = json.loads((DATA / "fixtures.json").read_text())["fixtures"]
    summary = json.loads((DATA / "summary.json").read_text())

    # 1. official link per fixture
    for fx in fixtures:
        urls = []
        for sid in fx.get("sources", []):
            # resolve via sources.json
            pass
    sources = {s["id"]: s for s in json.loads((DATA / "sources.json").read_text())["sources"]}
    for fx in fixtures:
        offs = [sources[sid] for sid in fx.get("sources", []) if sid in sources and sources[sid]["kind"] == "official"]
        if not offs:
            errors.append(f"{fx['id']}: no official source on the row")
        for s in offs:
            if not s["url"].startswith("https://"):
                errors.append(f"{fx['id']}: official source not https ({s['url']})")

    # 2/3. prediction text rules
    grams = {}
    for p in preds:
        t = p["text"]
        w = words(t)
        if len(w) < 30:
            errors.append(f"{p['fixture_id']}: prediction under 30 words ({len(w)})")
        low = t.lower()
        for b in BANNED:
            if b in low:
                errors.append(f"{p['fixture_id']}: banned word {b!r} in prediction text")
        sel_words = [w for w in re.findall(r"[A-Za-z]{5,}", p["selection"].split(" to ")[0])]
        if sel_words and not any(w.lower() in low for w in sel_words):
            errors.append(f"{p['fixture_id']}: selection {p['selection']!r} not named in text")
        for g in fivegrams(t):
            if g in grams and grams[g] != p["fixture_id"]:
                errors.append(f"{p['fixture_id']}: repeated 5-gram {g!r} (also in {grams[g]})")
            grams[g] = p["fixture_id"]

    # 4. tier arithmetic for predictions
    for p in preds:
        fx = next(f for f in fixtures if f["id"] == p["fixture_id"])
        ok = fx.get("grade") in ("direct", "search")
        expected = tier(p["p"], p["american"], ok)
        if p["tier"] != expected:
            errors.append(f"{p['fixture_id']}: tier {p['tier']!r} != recomputed {expected!r}")
        if p["tier"] == "High":
            if not (p["p"] > 0.70 and -250.0000001 <= p["american"] <= 10000):
                errors.append(f"{p['fixture_id']}: High pick outside the p/window gate")
            if not ok:
                errors.append(f"{p['fixture_id']}: High pick without a read official source")

    # 5. market arithmetic
    for r in markets:
        if r["p"] <= 0 or r["p"] >= 1:
            errors.append(f"{r['fixture_id']} {r['market']}: bad p {r['p']}")
            continue
        if abs(r["decimal"] - 1 / r["p"]) > 0.02:
            errors.append(f"{r['fixture_id']} {r['market']} {r['selection']}: decimal {r['decimal']} != 1/p {1/r['p']:.3f}")

    # 6. summary consistency
    if summary["fixtures"] != len(fixtures):
        errors.append(f"summary fixtures {summary['fixtures']} != {len(fixtures)}")
    if summary["predictions"] != len(preds):
        errors.append(f"summary predictions {summary['predictions']} != {len(preds)}")
    if summary["high_picks"] != sum(1 for p in preds if p["tier"] == "High"):
        errors.append("summary high_picks mismatch")
    if summary["priced"] != len(markets):
        errors.append("summary priced mismatch")

    # 7. pages
    for name in REQUIRED_PAGES:
        path = SITE / name
        if not path.exists():
            errors.append(f"missing page {name}")
            continue
        body = path.read_text().lower()
        for b in BANNED:
            if b in body:
                errors.append(f"{name}: banned word {b!r} in published page")
    for s, _lab in json.loads(json.dumps([list(x) for x in __import__("sc3026353_data").SPORTS])):
        if not (SITE / "sports" / f"{s}.html").exists():
            errors.append(f"missing sport page sports/{s}.html")

    stats = {
        "fixtures": len(fixtures), "predictions": len(preds), "markets": len(markets),
        "high": sum(1 for p in preds if p["tier"] == "High"),
        "errors": len(errors), "warnings": len(warnings),
    }
    return errors, warnings, stats


def main():
    errors, warnings, stats = check()
    print(json.dumps(stats, indent=1))
    for w in warnings:
        print("WARN:", w)
    for e in errors[:60]:
        print("ERROR:", e)
    if errors:
        print(f"FAILED with {len(errors)} error(s)")
        sys.exit(1)
    print("DESK VALIDATION PASSED")


if __name__ == "__main__":
    main()
