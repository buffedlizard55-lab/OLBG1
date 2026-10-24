"""Validator for the 580f43c9 desk.

Run:  python3 scripts/s580f43c9_validate.py
Exit code 0 = every check passed.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s580f43c9_model import american_from_prob, decimal_from_prob, in_band, tier, INPUT_COMPLETE
from s580f43c9_data import SOURCES, MATCHES, PICKS, GAPS, FLAGS, AUDIT

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "580f43c9"
DATA = ROOT / "data" / "580f43c9"

BANNED = ["model", "models", "verified", "verification", "verify", "algorithm"]
checks = 0
fails = []


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def main():
    cards = json.loads((DATA / "picks.json").read_text())
    src_by_id = {s["id"]: s for s in SOURCES}

    # --- data integrity -----------------------------------------------------
    check(len(cards) == len(PICKS), "picks.json out of date with the data module")
    for m in MATCHES:
        check(m["source"] in src_by_id, f"match {m['id']} references unknown source {m['source']}")
        if m["source"] in src_by_id:
            check(src_by_id[m["source"]]["official"] is True,
                  f"match {m['id']} rests on a non-official source")
        check(bool(m["injury_note"]), f"match {m['id']} has no injury note")

    ids = [m["id"] for m in MATCHES]
    check(len(ids) == len(set(ids)), "duplicate match ids")

    # --- every priced row: official evidence + arithmetic -------------------
    prose_bodies = []
    for c in cards:
        src = c["source"]
        check(src["official"] is True, f"{c['match_id']}: priced row without an official source")
        check(src["url"].startswith("https://"), f"{c['match_id']}: source URL not https")
        p = c["prob"]
        check(abs(c["fair_decimal"] - round(decimal_from_prob(p), 3)) < 1e-9,
              f"{c['match_id']}: fair decimal is not 1/p")
        check(c["fair_american"] == american_from_prob(p),
              f"{c['match_id']}: American price inconsistent with the probability")
        check(c["in_band"] == in_band(p), f"{c['match_id']}: band flag inconsistent")
        # selection must be one of the two participants
        parties = c["match"].split(" v ")
        check(c["selection"] in parties, f"{c['match_id']}: selection is not a participant")
        # tier rule, both directions
        expect = tier(p, c["sport"], INPUT_COMPLETE[c["sport"]], c["out_of_band"])
        check(expect == c["confidence"],
              f"{c['match_id']}: tier {c['confidence']} does not follow the gate (expected {expect})")
        if c["confidence"] == "high":
            check(p > 0.70, f"{c['match_id']}: high below 70%")
            check(in_band(p), f"{c['match_id']}: high outside the price band")
        if p > 0.70 and in_band(p) and INPUT_COMPLETE[c["sport"]]:
            check(c["confidence"] == "high",
                  f"{c['match_id']}: qualifies for high but is labelled {c['confidence']}")

        # prose
        words = len(c["prose"].split())
        check(words >= 30, f"{c['match_id']}: prose is only {words} words")
        check(c["selection"].split()[0] in c["prose"] or c["selection"] in c["prose"],
              f"{c['match_id']}: prose never names the selection")
        for bad in BANNED:
            check(bad not in c["prose"].lower(), f"{c['match_id']}: prose contains banned word '{bad}'")
        prose_bodies.append((c["match_id"], c["prose"]))

    # six-gram uniqueness across every write-up
    grams = {}
    for mid, prose in prose_bodies:
        toks = re.findall(r"[a-z0-9']+", prose.lower())
        for i in range(len(toks) - 5):
            gram = " ".join(toks[i:i + 6])
            grams.setdefault(gram, set()).add(mid)
    shared = {g: s for g, s in grams.items() if len(s) > 1}
    check(not shared, f"repeated 6-grams across write-ups: {list(shared)[:5]}")

    # --- gaps and flags ----------------------------------------------------
    for g in GAPS:
        check(g["source"].startswith("https://"), f"gap {g['sport']} has no source link")
        check(len(g["blocked"]) > 40, f"gap {g['sport']} has no usable reason")
    for f in FLAGS:
        check(f["link"].startswith("https://"), f"flag {f['id']} has no link")
    check(len({f["id"] for f in FLAGS}) == len(FLAGS), "duplicate flag ids")
    for a in AUDIT:
        check(a["verdict"] in ("pass", "flag"), f"audit {a['id']} has an unknown verdict")

    # --- site: internal links and fragments --------------------------------
    pages = sorted(SITE.rglob("*.html"))
    check(len(pages) >= 20, f"only {len(pages)} pages built")
    anchor_cache = {}
    for page in pages:
        text = page.read_text()
        refs = re.findall(r'href="([^"]+)"', text)
        check(not re.search(r'href="https?://localhost', text), f"{page.name}: localhost reference")
        for ref in refs:
            if ref.startswith(("http://", "https://", "mailto:")):
                continue
            target, _, frag = ref.partition("#")
            if target == "":
                target_path = page
            else:
                target_path = (page.parent / target).resolve()
            check(target_path.exists(), f"{page.relative_to(SITE)}: broken link {ref}")
            if frag and target_path.exists() and target_path.suffix == ".html":
                if target_path not in anchor_cache:
                    anchor_cache[target_path] = set(
                        re.findall(r'id="([^"]+)"', target_path.read_text()))
                check(frag in anchor_cache[target_path],
                      f"{page.relative_to(SITE)}: missing fragment #{frag} in {target_path.name}")

    # --- clarity requirements on the landing page -------------------------
    index = (SITE / "index.html").read_text()
    check("Executive summary" in index or "executive summary" in index.lower(),
          "landing page does not present an executive summary")
    check(index.count("<table") >= 2, "landing page lacks the picks table")
    for c in cards:
        check(c["selection"] in index, f"landing page never names the pick {c['selection']}")

    print(f"{checks} checks, {len(fails)} failures")
    for f in fails:
        print("  FAIL:", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
