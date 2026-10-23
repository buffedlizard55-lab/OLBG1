#!/usr/bin/env python3
"""Session 4c4968fc — gate for the desk. Non-zero exit means the desk may not ship."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import s4c4968fc_data as D
import s4c4968fc_model as M

DATA = ROOT / "data" / "4c4968fc"
SITE = ROOT / "4c4968fc"
fails, warns = [], []


def fail(msg):
    fails.append(msg)


def warn(msg):
    warns.append(msg)


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main():
    fixtures = load("fixtures.json")["fixtures"]
    markets = load("markets.json")["markets"]
    picks = load("picks.json")["picks"]
    preds = load("predictions.json")["predictions"]
    flagged = load("flagged.json")["items"]
    manifest = load("site-manifest.json")

    # ---- scope
    sports = [k for k, _n, _h in D.SPORTS]
    if len(sports) != 15:
        fail(f"sport list has {len(sports)} entries, expected 15")
    banned_sports = {"soccer", "football", "boxing", "mma", "ufc", "hurling", "cycling", "horse-racing"}
    if banned_sports & set(sports):
        fail(f"out-of-scope sport in registry: {banned_sports & set(sports)}")
    listed = {f["sport"] for f in fixtures}
    if listed - set(sports):
        fail(f"fixtures outside the registry: {listed - set(sports)}")
    missing = set(sports) - listed
    for s in missing:
        if not any(it["sport"] == s for it in flagged):
            fail(f"sport {s} has no fixtures and no flag")

    # ---- fixtures
    if len(fixtures) < 30:
        warn(f"only {len(fixtures)} fixtures")
    ids = [f["id"] for f in fixtures]
    if len(ids) != len(set(ids)):
        fail("duplicate fixture ids")
    for f in fixtures:
        if not f["sources"]:
            fail(f"{f['id']} has no source")
        for s in f["sources"]:
            if not s["url"].startswith("https://"):
                fail(f"{f['id']} source not https: {s['url']}")
            if s["id"].startswith("olbg"):
                fail(f"{f['id']} cites OLBG as fixture evidence")
        if not f["start_utc"]:
            fail(f"{f['id']} missing start time")
        elif not re.match(r"^2026-10-2[3-9]T\d{2}:\d{2}:\d{2}Z$", f["start_utc"]):
            fail(f"{f['id']} start outside the published window: {f['start_utc']}")
        if not f["facts"]:
            fail(f"{f['id']} carries no sourced facts")

    # ---- markets: complementary pairs, sane probabilities
    by_fx = defaultdict(list)
    for m in markets:
        by_fx[m["fixture"]].append(m)
        if not (0.0 < m["p"] < 1.0):
            fail(f"{m['fixture']} {m['market']} p out of range: {m['p']}")
        if m["tier"] not in ("High", "Medium", "Low"):
            fail(f"{m['fixture']} bad tier {m['tier']}")
        if m["tier"] == "High" and not (m["p"] > 0.70 and M.in_band(m["p"])):
            fail(f"{m['fixture']} {m['market']} High but fails the gate (p={m['p']})")
        if m["tier"] != "High" and m["p"] > 0.70 and M.in_band(m["p"]):
            fail(f"{m['fixture']} {m['market']} qualifies but is not High")
        if m["tier"] == "High" and not (-250 <= m["american"] <= 10000):
            fail(f"{m['fixture']} High price outside band: {m['american']}")
    for fid, ms in by_fx.items():
        groups = defaultdict(list)
        for m in ms:
            groups[m["market"]].append(m)
        for mk, rs in groups.items():
            if mk in ("Match winner", "Head-to-head"):
                tot = sum(r["p"] for r in rs)
                if abs(tot - 1.0) > 1e-6:
                    fail(f"{fid} {mk} books sum to {tot:.6f}")
            elif mk in ("Match total", "Team total", "Total sets", "Total games", "Total points"):
                # ladder: over/under rungs must be complementary in pairs of two
                if len(rs) % 2 != 0:
                    fail(f"{fid} {mk} ladder has odd rung count")
                for i in range(0, len(rs) - 1, 2):
                    if abs(rs[i]["p"] + rs[i + 1]["p"] - 1.0) > 1e-6:
                        fail(f"{fid} {mk} rung not complementary: {rs[i]['p']:.4f}+{rs[i+1]['p']:.4f}")

    # ---- picks
    if len(picks) > 15 * 5:
        fail("more picks than the per-sport cap allows")
    per_sport = Counter(p["sport"] for p in picks)
    for s, c in per_sport.items():
        if c > 5:
            fail(f"{s} has {c} picks, cap is 5")
    seen = set()
    for p in picks:
        if (p["fixture"], p["market"]) in seen:
            fail(f"duplicate pick {p['fixture']} {p['market']}")
        seen.add((p["fixture"], p["market"]))
        if p["tier"] != "High":
            fail(f"pick {p['fixture']} is not High")
        if p["p"] <= 0.70:
            fail(f"pick {p['fixture']} p={p['p']} below 0.70")
        if not (-250 <= p["american"] <= 10000):
            fail(f"pick {p['fixture']} price {p['american']} outside band")
        if p["fixture"] not in ids:
            fail(f"pick references unknown fixture {p['fixture']}")

    # ---- predictions
    pred_keys = {(x["fixture"], x["market"]) for x in preds}
    for p in picks:
        if (p["fixture"], p["market"]) not in pred_keys:
            fail(f"no prediction for pick {p['fixture']} {p['market']}")
    texts = []
    for x in preds:
        words = x["text"].split()
        if len(words) < 30:
            fail(f"{x['fixture']} prediction is {len(words)} words")
        low = x["text"].lower()
        for bad in ("model", "verified", "algorithm", "regression"):
            if re.search(rf"\b{bad}\b", low):
                fail(f"{x['fixture']} prediction uses banned word '{bad}'")
        if x["selection"].lower() not in low and x["selection_line"].lower() not in low:
            fail(f"{x['fixture']} prediction does not state the selection")
        if not x["sources"]:
            fail(f"{x['fixture']} prediction has no source link")
        texts.append(x["text"])
    def grams(t, n=6):
        w = re.findall(r"[a-z]+", t.lower())
        return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if grams(texts[i]) & grams(texts[j]):
                fail(f"predictions {preds[i]['fixture']} and {preds[j]['fixture']} share a six-word phrase")

    # ---- flagged items carry a link
    for it in flagged:
        if not it["source_list"]:
            fail(f"flag {it['id']} has no link for manual review")

    # ---- pages
    for page in manifest["pages"]:
        path = SITE / page
        if not path.exists():
            fail(f"missing page {page}")
            continue
        body = path.read_text(encoding="utf-8")
        if "<html" not in body or "</html>" not in body:
            fail(f"{page} is not a complete document")
        for bad in ("model", "verified"):
            if re.search(rf"\b{bad}\b", body, re.I):
                fail(f"{page} contains the banned word '{bad}'")
        if 'href="index.html"' not in body and page != "index.html":
            pass
        if page.startswith("sports/") and 'href="../index.html"' not in body and 'href="../high-confidence.html"' not in body:
            fail(f"{page} has no path back to the desk")
        if "<table" in body and "https://" not in body:
            fail(f"{page} publishes a table with no outbound source link")
    # every table row on a data page must expose at least one official link
    for page in ("matches.html", "predictions.html", "flagged.html", "sports/ice-hockey.html"):
        body = (SITE / page).read_text(encoding="utf-8")
        rows = re.findall(r"<tr>(?:(?!</tr>).)*</tr>", body, re.S)
        for r in rows:
            if 'class="grp"' in r or "<th" in r:
                continue
            if "https://" not in r:
                fail(f"{page} has a row without an official link")
    if len(manifest["pages"]) < 20:
        fail(f"only {len(manifest['pages'])} pages published")

    # ---- csv exports parse
    for name in ("matches.csv", "markets.csv", "predictions.csv"):
        rows = (DATA / name).read_text(encoding="utf-8").strip().split("\n")
        if len(rows) < 2:
            fail(f"{name} is empty")

    print(f"fixtures={len(fixtures)} markets={len(markets)} picks={len(picks)} "
          f"predictions={len(preds)} pages={len(manifest['pages'])} flags={len(flagged)}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    if fails:
        print(f"\n{len(fails)} failure(s)")
        return 1
    print(f"\nOK — {len(warns)} warning(s), 0 failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
