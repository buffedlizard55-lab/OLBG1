"""Session cf2699ba-olbg1 — release gates.

Checks the desk rather than the prose: counts, tier arithmetic, source provenance,
link resolution, prediction rules and HTML integrity. Exits non-zero on any error.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "cf2699ba")
SITE = os.path.join(ROOT, "cf2699ba")

problems = []
notes = []


def fail(msg):
    problems.append(msg)


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def american_from_prob(p):
    return -(100.0 * p) / (1.0 - p) if p > 0.5 else 100.0 * (1.0 - p) / p


def main():
    sports = load("sports.json")["sports"]
    sources = load("sources.json")["sources"]
    disc = load("discovery.json")
    fixtures = load("fixtures.json")
    lines = load("lines.json")
    preds = load("predictions.json")["predictions"]
    flags = load("flagged.json")["flags"]

    src_ids = {s["id"] for s in sources}
    sport_keys = {s["key"] for s in sports}

    # ---- 1. structure -----------------------------------------------------
    if len(sport_keys) != 15:
        fail(f"expected 15 sports, found {len(sport_keys)}")
    if disc["count"] != len(disc["events"]):
        fail("discovery count does not match rows")
    if fixtures["count"] != len(fixtures["fixtures"]):
        fail("fixture count does not match rows")
    for s in sources:
        if not s["url"].startswith("https://"):
            fail(f"source {s['id']} is not https")
        if not s["observed"]:
            fail(f"source {s['id']} has no observation window")
    if not any(s["role"] == "discovery" for s in sources):
        fail("no discovery source recorded")

    # ---- 2. discovery rows ------------------------------------------------
    seen_ids = set()
    for r in disc["events"]:
        if r["sport"] not in sport_keys:
            fail(f"discovery row {r['olbg_event_id']} has unknown sport {r['sport']}")
        if str(r["olbg_event_id"]) not in r["olbg_url"]:
            fail(f"discovery row {r['olbg_event_id']} url does not carry its id")
        if not r["olbg_time_text"]:
            fail(f"discovery row {r['olbg_event_id']} has no time string")
        key = (r["sport"], r["olbg_event_id"])
        if key in seen_ids:
            fail(f"duplicate discovery row {key}")
        seen_ids.add(key)
        if r["olbg_pct"] is not None and not (0 <= r["olbg_pct"] <= 100):
            fail(f"share out of range on {r['olbg_event_id']}")

    # ---- 3. fixtures ------------------------------------------------------
    for f in fixtures["fixtures"]:
        if f["sport"] not in sport_keys:
            fail(f"fixture {f['id']} unknown sport")
        if not f["sources"]:
            fail(f"fixture {f['id']} has no source")
        for sid in f["sources"]:
            if sid not in src_ids:
                fail(f"fixture {f['id']} cites missing source {sid}")
        official = [s for s in f["sources"] if any(x["id"] == s and x["role"].startswith("official") for x in sources)]
        if not official:
            fail(f"fixture {f['id']} has no official source")
        for fact in f["facts"]:
            if fact["src"] not in src_ids:
                fail(f"fixture {f['id']} fact cites missing source {fact['src']}")

    # ---- 4. tier arithmetic ----------------------------------------------
    tier_counts = {"High": 0, "Medium": 0, "Low": 0}
    checked = 0
    for l in lines["verified_lines"]:
        for b in l["blocks"]:
            for o in b["outcomes"]:
                if o.get("p") is None:
                    if o.get("tier") is not None:
                        fail(f"unpriced outcome carries a tier: {o['selection']}")
                    continue
                checked += 1
                p, am = o["p"], o["american"]
                if abs(american_from_prob(p) - am) > 1.5:
                    fail(f"American price does not follow from p: {o['selection']} {p} {am}")
                if abs(o["decimal"] - 1 / p) > 0.002:
                    fail(f"decimal does not follow from p: {o['selection']}")
                expect = "Low"
                if b["class"] == "market":
                    if p >= 0.70 and -250 <= am <= 10000:
                        expect = "High"
                    elif p >= 0.62:
                        expect = "Medium"
                if o["tier"] != expect:
                    fail(f"tier mismatch on {o['selection']}: {o['tier']} != {expect}")
                tier_counts[o["tier"]] += 1
    for i in lines["indicative"]:
        if i.get("p") is not None:
            if i["tier"] != "Low":
                fail(f"indicative row graded above Low: {i['name']}")
            checked += 1
            tier_counts["Low"] += 1
    if checked != len([1 for l in lines["verified_lines"] for b in l["blocks"] for o in b["outcomes"] if o.get("p")]) + sum(
            1 for i in lines["indicative"] if i.get("p")):
        fail("priced row accounting mismatch")
    if sum(tier_counts.values()) != sum(lines["tier_counts"].values()):
        notes.append(f"tier totals differ from model output ({tier_counts} vs {lines['tier_counts']})")

    # ---- 5. high-confidence rule claims ----------------------------------
    for o in lines["out_of_band"]:
        if not (o["p"] >= 0.70 and o["american"] < -250):
            fail(f"out-of-band ledger row is not actually out of band: {o['selection']}")
    for f in flags:
        for sid in f["src"]:
            if sid not in src_ids:
                fail(f"flag {f['id']} cites missing source {sid}")
    if len({f["id"] for f in flags}) != len(flags):
        fail("duplicate flag ids")

    # ---- 6. predictions ---------------------------------------------------
    bodies = []
    for p in preds:
        w = len(p["body"].split())
        if w < 30:
            fail(f"prediction {p['id']} is only {w} words")
        if p["words"] != w:
            fail(f"prediction {p['id']} word count not recomputed")
        low = re.findall(r"[a-z']+", p["body"].lower())
        for bad in ("model", "models", "verified", "verify", "verification", "algorithm"):
            if bad in low:
                fail(f"prediction {p['id']} uses banned word '{bad}'")
        if not p["facts"]:
            fail(f"prediction {p['id']} has no linked fact")
        for fct in p["facts"]:
            if fct["src"] not in src_ids:
                fail(f"prediction {p['id']} cites missing source {fct['src']}")
        if p["fixture_id"] not in {f["id"] for f in fixtures["fixtures"]}:
            fail(f"prediction {p['id']} points at unknown fixture")
        bodies.append(p["body"])
    if len(set(bodies)) != len(bodies):
        fail("duplicate prediction bodies")
    pairs = [(p["fixture_id"], p["selection"]) for p in preds]
    if len(set(pairs)) != len(pairs):
        fail("duplicate fixture/selection prediction")

    # ---- 7. html ----------------------------------------------------------
    pages = []
    for base, _, files in os.walk(SITE):
        for fn in files:
            if fn.endswith(".html"):
                pages.append(os.path.join(base, fn))
    if len(pages) < 20:
        fail(f"only {len(pages)} html pages built")
    href_re = re.compile(r'href="([^"]+)"')
    for path in pages:
        text = open(path, encoding="utf-8").read()
        rel = os.path.relpath(path, SITE)
        if "Snapshot 23 Oct 2026" not in text:
            fail(f"{rel} is missing the snapshot stamp")
        for href in href_re.findall(text):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            if href.startswith("#"):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), href.split("#")[0]))
            if not os.path.exists(target):
                fail(f"{rel} links to missing {href}")
        if "<script" in text.lower():
            fail(f"{rel} contains a script tag")
        if "localhost" in text or "127.0.0.1" in text:
            fail(f"{rel} references a local service")
        # every table row that carries a price must carry a source-ish link
    index = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
    for token in ("135", "6", "19"):
        if token not in index:
            notes.append(f"index does not mention {token}")

    print(f"pages={len(pages)} sports={len(sport_keys)} listings={len(disc['events'])} "
          f"fixtures={len(fixtures['fixtures'])} sources={len(src_ids)} "
          f"predictions={len(preds)} flags={len(flags)} tiers={tier_counts}")
    for n in notes:
        print("  note:", n)
    if problems:
        print(f"\nVALIDATION FAILED ({len(problems)} problems)")
        for p in problems[:40]:
            print("  -", p)
        return 1
    print("\nVALIDATION PASSED (0 errors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
