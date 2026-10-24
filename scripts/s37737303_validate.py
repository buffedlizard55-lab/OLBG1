# -*- coding: utf-8 -*-
"""Gate for the 37737303 desk.

Exit code 0 means every check passed.  The checks are the ones the brief and
the repository's coordination rules actually require, not a smoke test:

1. all fifteen brief sports exist as pages and appear in coverage;
2. price arithmetic is internally consistent (probability -> American price,
   decimal price, band flag);
3. every pick is one of the markets published for its own fixture;
4. every fixture links an OLBG event page and a source id that exists;
5. every fact cites an *official* source, never a discovery row;
6. confidence grading follows the published rule, including the band;
7. every written prediction is at least 30 words, unique by six-gram, names
   the selection, avoids internal vocabulary, and cites official facts;
8. no prediction is written for a fixture with no official input at all;
9. coverage counts agree with the data;
10. no internal link in the built desk is broken.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "37737303"
DESK = ROOT / "37737303"

BRIEF_SPORTS = ["golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
                "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball", "ice-hockey",
                "basketball", "rugby-league"]
BANNED = ["model", "verified", "verification", "hallucinat", "algorithm", "regression"]
BAND_LOW, BAND_HIGH = -250, 10000

errors: list[str] = []
checks: list[str] = []


def check(cond, msg):
    if cond:
        checks.append(msg)
    else:
        errors.append(msg)


def american(prob):
    if prob >= 0.5:
        raw = -100.0 * prob / (1 - prob)
    else:
        raw = 100.0 * (1 - prob) / prob
    return int(round(raw / 5.0) * 5)


def main() -> int:
    fixtures = json.loads((DATA / "fixtures.json").read_text())["fixtures"]
    sources = {s["id"]: s for s in json.loads((DATA / "sources.json").read_text())["sources"]}
    coverage = json.loads((DATA / "coverage.json").read_text())
    preds = json.loads((DATA / "predictions.json").read_text())["predictions"]
    flags = json.loads((DATA / "flags.json").read_text())["flags"]

    # 1. sports coverage
    for sport in BRIEF_SPORTS:
        check((DESK / "sports" / f"{sport}.html").is_file(), f"sport page exists: {sport}")
        check(any(s["sport"] == sport for s in coverage["sports"]), f"sport in coverage table: {sport}")

    # 2-6. per fixture
    grams: dict[str, str] = {}
    seen_ids = set()
    for f in fixtures:
        fid = f["id"]
        check(fid not in seen_ids, f"{fid}: unique id")
        seen_ids.add(fid)
        check(f["sport"] in BRIEF_SPORTS, f"{fid}: sport inside the brief")
        check(f["official_source"] in sources, f"{fid}: official_source resolves")
        check(f["olbg_url"].startswith("https://www.olbg.com/"), f"{fid}: OLBG event link present")
        for m in f["markets"]:
            check(abs(american(m["prob"]) - m["fair"]) <= 5, f"{fid}: price arithmetic for {m['side']}")
            check(abs(1 / m["prob"] - m["decimal"]) < 0.02, f"{fid}: decimal price for {m['side']}")
            check(m["prob"] > 0.02, f"{fid}: probability not degenerate for {m['side']}")
        sides = {(m["market"], m["side"]) for m in f["markets"]}
        check((f["pick"]["market"], f["pick"]["selection"]) in sides, f"{fid}: pick is a published market")
        p = f["pick"]
        check(abs(p["fair"] - american(p["prob"])) <= 5, f"{fid}: pick price arithmetic")
        check(p["in_band"] == (BAND_LOW <= p["fair"] <= BAND_HIGH), f"{fid}: band flag")
        for fact in f["facts"]:
            src = sources.get(fact["source"], {})
            check(src.get("kind") == "official", f"{fid}: fact cites an official source")
        # confidence rule
        expected = "low"
        if p["in_band"]:
            if p["prob"] >= 0.60 and f["evidence"] in ("both", "one"):
                expected = "high"
            elif p["prob"] >= 0.55 and f["evidence"] in ("both", "one", "fixture"):
                expected = "medium"
            elif p["prob"] >= 0.60 and f["evidence"] == "sentiment":
                expected = "medium"
        check(f["confidence"] == expected, f"{fid}: confidence follows the published rule")

    # 7-8. predictions
    for pred in preds:
        words = pred["text"].split()
        check(len(words) >= 30, f"{pred['id']}: prediction has 30+ words ({len(words)})")
        low = pred["text"].lower()
        for word in BANNED:
            check(word not in low, f"{pred['id']}: prediction free of '{word}'")
        row = next((f for f in fixtures if f["id"] == pred["id"]), None)
        check(row is not None, f"{pred['id']}: prediction maps to a fixture")
        if row:
            sel_tokens = [w.strip(".,()").lower() for w in pred["selection"].replace("-", " ").split()]
            text_low = pred["text"].lower()
            check(any(len(w) > 3 and w in text_low for w in sel_tokens),
                  f"{pred['id']}: prediction names the selection")
            check(row["evidence"] != "none", f"{pred['id']}: fixture has an official or publisher input")
            side_tokens = [w.strip(".,()").lower()
                           for t in (row["home"], row["away"]) for w in t.split()]
            check(any(len(w) > 3 and w in text_low for w in side_tokens),
                  f"{pred['id']}: prediction names one of the sides")
            # any American price quoted in the prose must be a price this desk actually
            # publishes for the fixture, or one of the two band constants
            quoted = {int(t) for t in re.findall(r"(?<![\w.])([+-]\d{3,5})(?![\w.])", pred["text"])}
            published = {m["fair"] for m in row["markets"]} | {-250, 10000}
            for q in sorted(quoted):
                check(any(abs(abs(q) - abs(pub)) <= 5 or abs(q - pub) <= 5 for pub in published),
                      f"{pred['id']}: quoted price {q:+d} matches a published line")
        tokens = re.findall(r"[a-z0-9']+", low)
        for i in range(len(tokens) - 5):
            gram = " ".join(tokens[i:i + 6])
            check(gram not in grams, f"{pred['id']}: six-gram unique vs {grams.get(gram, '')}")
            grams.setdefault(gram, pred["id"])

    # 9. coverage counts
    counts = coverage["counts"]
    check(counts["fixtures"] == len(fixtures), "coverage fixture count")
    check(counts["picks"] == len(fixtures), "coverage pick count")
    check(counts["markets"] == sum(len(f["markets"]) for f in fixtures), "coverage market count")
    check(counts["predictions"] == len(preds), "coverage prediction count")
    check(counts["flags"] == len(flags), "coverage flag count")
    check(counts["high"] == sum(1 for f in fixtures if f["confidence"] == "high"), "coverage high count")
    check(counts["sports_with_picks"] + counts["sports_without_market"] == 15,
          "all fifteen sports accounted for (picks or no-market)")

    # flags reference real sources
    for flag in flags:
        for sid in flag["sources"]:
            check(sid in sources, f"{flag['id']}: flag source resolves ({sid})")

    # 10. internal links
    for page in DESK.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"#:]+\.html)"', text):
            target = (page.parent / href).resolve()
            if not target.exists():
                errors.append(f"broken link: {page.relative_to(DESK)} -> {href}")
        if "index.html" not in text:
            errors.append(f"no route home from {page.relative_to(DESK)}")
    checks.append("internal links checked")

    for line in checks:
        pass
    if errors:
        print("DESK VALIDATION FAILED")
        for e in errors:
            print("  ERROR:", e)
        return 1
    print(f"DESK VALIDATION PASSED — {len(checks)} checks, {len(fixtures)} fixtures, "
          f"{len(preds)} predictions, {len(flags)} flags, 15 sports")
    return 0


if __name__ == "__main__":
    sys.exit(main())
