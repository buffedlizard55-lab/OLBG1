#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T60 / session 1a421e41-olbg1 -- independent validator for the desk and the
published site. Re-derives every gate from the raw inputs rather than trusting
the builder. Exits non-zero on any error.

  python3 scripts/s1a421e41_validate.py
"""

import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "1a421e41")
SITE = os.path.join(ROOT, "1a421e41")

ERRORS = []
WARNINGS = []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def phi(x):
    import math
    return 0.5 * (1.0 + math.erf(x / (2.0 ** 0.5)))


def american(p):
    if p is None or p <= 0 or p >= 1:
        return None
    if p >= 0.5:
        return int(round(-100.0 * p / (1.0 - p)))
    return int(round(100.0 * (1.0 - p) / p))


def main():
    desk = json.load(open(os.path.join(DATA, "desk.json")))
    H = load("h", os.path.join(DATA, "olbg_harvest_raw.py"))
    E = load("e", os.path.join(DATA, "official_evidence.py"))
    rows = desk["rows"]
    meta = desk["meta"]

    # ---------------------------------------------------------- scope
    scope_keys = {s["key"] for s in desk["scope"]["in_scope"]}
    if len(scope_keys) != 17:
        err("scope: expected 17 in-scope sports, found %d" % len(scope_keys))
    excluded_ids = {x["olbg_id"] for x in desk["scope"]["excluded"]}
    if not {1, 2, 11, 16, 17, 18, 26} <= excluded_ids:
        err("scope: excluded OLBG ids incomplete: %s" % sorted(excluded_ids))
    for r in rows:
        if r["olbg_id"] in excluded_ids:
            err("scope: row %s sits on excluded OLBG id %s" % (r["row_id"], r["olbg_id"]))
        if r["sport"] not in scope_keys:
            err("scope: row %s has out-of-scope sport %s" % (r["row_id"], r["sport"]))

    # ---------------------------------------------------------- counts
    n_olbg = len([r for r in rows if r["origin"] == "olbg"])
    n_add = len([r for r in rows if r["origin"] == "official_addition"])
    harvested = sum(len(v) for v in H.HARVEST.values())
    if n_olbg != harvested:
        err("counts: %d OLBG rows in desk vs %d harvested" % (n_olbg, harvested))
    if meta["rows_total"] != len(rows):
        err("counts: meta.rows_total %d != %d rows" % (meta["rows_total"], len(rows)))
    if meta["rows_from_olbg"] != n_olbg or meta["rows_official_additions"] != n_add:
        err("counts: meta origin split does not match rows")
    if len({r["row_id"] for r in rows}) != len(rows):
        err("counts: duplicate row_id")

    # ---------------------------------------------------------- sources
    for r in rows:
        srcs = r["sources"]["official"] + r["sources"]["olbg"]
        if not srcs:
            err("sources: row %s has no source link at all" % r["row_id"])
        if not r["sources"]["official"]:
            if not any(f["code"].startswith(("UNVERIFIED", "RATING-UNVERIFIED", "NOT-LISTED")) for f in r["flags"]):
                err("sources: row %s has no official source and is not flagged unverified" % r["row_id"])
            if r["rating"]["klass"] != "C":
                err("sources: row %s has no official source but is graded Class %s" % (r["row_id"], r["rating"]["klass"]))
        for s in r["sources"]["official"]:
            if not s["url"].startswith("https://"):
                err("sources: row %s official source is not an https URL: %r" % (r["row_id"], s["url"]))
            host = s["url"].split("/")[2]
            if any(b in host for b in ("wikipedia.org", "basketball-reference", "realgm", "eurobasket.com",
                                       "flashscore", "sofascore", "bet365", "oddschecker", "sportsmole",
                                       "express.co.uk", "mirror.co.uk", "skysports.com", "bbc.co.uk")):
                err("sources: row %s cites a non-official host as official: %s" % (r["row_id"], host))

    # ---------------------------------------------------------- price maths
    for r in rows:
        for m in r["markets"]:
            exp = american(m["p"])
            if m["american"] != exp:
                err("prices: %s %s american %s != recomputed %s" % (r["row_id"], m["label"], m["american"], exp))
            if m["decimal"] is not None and abs(m["decimal"] - 1.0 / m["p"]) > 5e-4:
                err("prices: %s %s decimal %s != 1/p %s" % (r["row_id"], m["label"], m["decimal"], 1.0 / m["p"]))
            if abs(m["p"] - 0.94) < 1e-9 or abs(m["p"] - 0.06) < 1e-9:
                err("ladder: %s %s sits on a clipped probability %s; the ladder should stop before saturating"
                    % (r["row_id"], m["label"], m["p"]))
            if m["market"] == "Handicap" and m["line"] is not None:
                neg = "-" in m["label"].split(" ")[-2] if len(m["label"].split(" ")) > 2 else False
                if neg != (m["line"] < 0):
                    err("ladder: %s %s label sign disagrees with stored line %s" % (r["row_id"], m["label"], m["line"]))
            if m["market"] in ("Handicap", "Match Total"):
                line = m["line"]
                if line is None or abs((abs(line) * 2) % 2 - 1) > 1e-9:
                    err("grid: %s %s line %s is not on a strict half-point grid (a push is possible)"
                        % (r["row_id"], m["label"], line))
            if m["ge_70"] != (m["p"] >= 0.70):
                err("gate: %s %s ge_70 flag disagrees with p" % (r["row_id"], m["label"]))
            win = m["american"] is not None and -250 <= m["american"] <= 10000
            if m["in_window"] != win:
                err("gate: %s %s in_window flag disagrees with american %s" % (r["row_id"], m["label"], m["american"]))

    # ---------------------------------------------------------- totals discipline
    for r in rows:
        has_total = any(m["market"] == "Match Total" for m in r["markets"])
        flagged = any(f["code"] == "TOTAL-NOT-ORIGINATED" for f in r["flags"])
        if has_total and flagged:
            err("totals: %s originates a total AND is flagged TOTAL-NOT-ORIGINATED" % r["row_id"])
        if has_total and not r["rating"]["total_originatable"]:
            err("totals: %s originates a total without an official anchor" % r["row_id"])
        if r["rating"]["klass"] == "C":
            if any(m["market"] != "Match Winner" for m in r["markets"]):
                err("totals: Class C row %s carries a non-moneyline market" % r["row_id"])
            if r["winner_pick"]["confidence"] == "High":
                err("tier: Class C row %s graded High" % r["row_id"])
            if not any(f["code"] == "SPREAD-NOT-ORIGINATED" for f in r["flags"]) and \
               r["sport"] not in ("golf", "motor_racing", "greyhounds", "gaelic_football", "cricket", "esports", "rugby_league", "aussie_rules"):
                warn("spread: Class C row %s has sigma but no SPREAD-NOT-ORIGINATED flag" % r["row_id"])
        if r["rating"].get("hard_cap") == "Medium" and r["winner_pick"]["confidence"] == "High":
            err("tier: hard-capped row %s graded High" % r["row_id"])

    # ---------------------------------------------------------- High gate
    high_rows = [r for r in rows if r["high_selection"]]
    if len(high_rows) != meta["high_selections"]:
        err("high: meta.high_selections %d != %d rows with a high_selection" % (meta["high_selections"], len(high_rows)))
    if len(desk["high_picks"]) != len(high_rows):
        err("high: high_picks board %d != %d" % (len(desk["high_picks"]), len(high_rows)))
    for r in high_rows:
        h = r["high_selection"]
        if h["p"] < 0.70:
            err("high: %s p %.4f < 0.70" % (r["row_id"], h["p"]))
        if not (-250 <= h["american"] <= 10000):
            err("high: %s american %d outside -250..+10000" % (r["row_id"], h["american"]))
        if r["rating"]["klass"] != "A":
            err("high: %s is Class %s, not Class A" % (r["row_id"], r["rating"]["klass"]))
        if not r["rating"]["form_ok"]:
            err("high: %s lacks official current-form evidence" % r["row_id"])
        if not r["sources"]["official"]:
            err("high: %s has no official source link" % r["row_id"])
        # tightest-rung rule: nothing qualifying may sit closer to our centre
        for m in r["markets"]:
            if m["ge_70"] and m["in_window"] and round(m["offset"], 6) < round(h["offset"], 6) - 1e-9:
                err("high: %s chose offset %.3f but %s is tighter at %.3f"
                    % (r["row_id"], h["offset"], m["label"], m["offset"]))
        if not r["prediction"]:
            err("high: %s has no prediction" % r["row_id"])

    # ---------------------------------------------------------- rejected ledger
    for r in rows:
        if len(r["rejected_highs"]) > r.get("rejected_high_count", 0):
            err("rejected: %s lists more rejections than its recorded count" % r["row_id"])
        if len(r["rejected_highs"]) > 3:
            err("rejected: %s prints %d ledger rows; the summary should stay readable"
                % (r["row_id"], len(r["rejected_highs"])))
        kinds = [j.get("kind") for j in r["rejected_highs"]]
        if len(set(kinds)) != len(kinds):
            err("rejected: %s repeats a ledger kind: %s" % (r["row_id"], kinds))
        for j in r["rejected_highs"]:
            if j["p"] < 0.70:
                err("rejected: %s %s p %.4f < 0.70 but is in the rejected-High ledger" % (r["row_id"], j["label"], j["p"]))
            if j["american"] is not None and -250 <= j["american"] <= 10000:
                err("rejected: %s %s american %d IS inside the window but was rejected" % (r["row_id"], j["label"], j["american"]))

    # ---------------------------------------------------------- predictions
    preds = [r["prediction"] for r in rows if r["prediction"]]
    if len(preds) != len(high_rows):
        err("predictions: %d predictions for %d High picks" % (len(preds), len(high_rows)))
    texts = [p["text"] for p in preds]
    if len(set(texts)) != len(texts):
        err("predictions: duplicate prediction text")
    for p in preds:
        wc = len(p["text"].split())
        if wc < 30:
            err("predictions: %s is %d words (<30)" % (p["for_selection"], wc))
        if p["word_count"] != wc:
            err("predictions: stored word_count %d != actual %d" % (p["word_count"], wc))
        if not p["official_sources"]:
            err("predictions: %s carries no official source link" % p["for_selection"])
    # non-repetition: no 6-word run shared between two different predictions
    def runs(t, n=6):
        w = t.lower().split()
        return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
    for i in range(len(texts)):
        ri = runs(texts[i])
        for j in range(i + 1, len(texts)):
            shared = ri & runs(texts[j])
            if shared:
                err("predictions: %d and %d share a 6-word run: %s" % (i, j, sorted(shared)[0]))

    # ---------------------------------------------------------- re-verify official arithmetic
    st = E.EUROLEAGUE_STANDINGS
    srows = st["rows"]
    for r in srows:
        if r[7] - r[8] != r[9]:
            err("standings: %s PTS+ - PTS- != +/-" % r[1])
        if r[4] + r[5] != r[3]:
            err("standings: %s W + L != GP" % r[1])
        hw, hl = (int(x) for x in r[10].split("-"))
        aw, al = (int(x) for x in r[11].split("-"))
        if hw + aw != r[4] or hl + al != r[5]:
            err("standings: %s H + A != overall W-L" % r[1])
    tot = st["totals"]
    if sum(r[7] for r in srows) != tot["sum_pts_for"]:
        err("standings: sum(PTS+) does not match recorded total")
    if sum(r[7] for r in srows) != sum(r[8] for r in srows):
        err("standings: sum(PTS+) != sum(PTS-); table is not a closed system")
    if sum(r[4] for r in srows) != sum(r[5] for r in srows):
        err("standings: sum(W) != sum(L)")
    hw = sum(int(r[10].split("-")[0]) for r in srows)
    aw = sum(int(r[11].split("-")[0]) for r in srows)
    if hw != tot["home_wins"] or aw != tot["away_wins"] or hw + aw != tot["games"]:
        err("standings: home/away win split does not reconcile with games played")
    for c in E.EUROLEAGUE_OFFICIAL_CONFLICTS:
        if not any(f["id"] == c["id"] for f in desk["findings"]):
            err("findings: official conflict %s not published" % c["id"])
    for row in E.EUROLEAGUE_CLOCK_RECONCILIATION["rows"]:
        if row[7] != -6:
            err("clock: %s delta %s != -6h" % (row[1], row[7]))
    if len(E.EUROLEAGUE_CLOCK_RECONCILIATION["rows"]) != 8:
        err("clock: expected 8 reconciled EuroLeague fixtures")

    # ---------------------------------------------------------- findings register
    ids = [f["id"] for f in desk["findings"]]
    if len(set(ids)) != len(ids):
        err("findings: duplicate finding id")
    for f in desk["findings"]:
        for k in ("id", "title", "detail", "status"):
            if not f.get(k):
                err("findings: %s missing %s" % (f.get("id"), k))
        if not f.get("sources") and f.get("status") != "confirmed-model-property":
            warn("findings: %s has no source link" % f["id"])

    # ---------------------------------------------------------- site
    pages = []
    for base, _dirs, files in os.walk(SITE):
        for fn in files:
            if fn.endswith(".html"):
                pages.append(os.path.join(base, fn))
    if pages:
        html = {os.path.relpath(p, ROOT): open(p, encoding="utf-8").read() for p in pages}
        broken = 0
        for rel, txt in html.items():
            d = os.path.dirname(os.path.join(ROOT, rel))
            import re
            for href in re.findall(r'href="([^"#]+\.html)"', txt):
                if href.startswith("http"):
                    continue
                if not os.path.exists(os.path.normpath(os.path.join(d, href))):
                    broken += 1
                    err("site: %s links to missing %s" % (rel, href))
        if "1a421e41/index.html" not in html:
            err("site: landing page 1a421e41/index.html missing")
        print("site pages: %d, broken relative links: %d" % (len(pages), broken))
    else:
        warn("site: no pages built yet under 1a421e41/")

    print("rows %d | markets %d | high %d | predictions %d | findings %d" % (
        len(rows), sum(r["market_counts"]["total"] for r in rows), len(high_rows),
        len(preds), len(desk["findings"])))
    for w in WARNINGS:
        print("WARN  %s" % w)
    for e in ERRORS:
        print("ERROR %s" % e)
    print("%s: %d error(s), %d warning(s)" % ("FAIL" if ERRORS else "PASS", len(ERRORS), len(WARNINGS)))
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
