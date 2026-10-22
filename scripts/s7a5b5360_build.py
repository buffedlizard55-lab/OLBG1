"""Session 7a5b5360-olbg1 — T41 model, picks and site builder.

Run:  python3 scripts/s7a5b5360_build.py
Writes data/7a5b5360/*.json, data/7a5b5360/matches.csv and the 7a5b5360/ dashboard tree.
No third-party dependencies.
"""
import csv
import html
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from s7a5b5360_data import (  # noqa: E402
    COVERAGE, EXCLUDED, FIELD, F1_EVENT, FIXTURES, IN_SCOPE, RETRIEVED_UTC, SOURCES, WINDOW,
)

OUT = os.path.join(ROOT, "data", "7a5b5360")
SITE = os.path.join(ROOT, "7a5b5360")

# ---------------------------------------------------------------- model assumptions (published)
ASSUMPTIONS = {
    "moneyline_shrink": {
        "Baseball": {"k": 0.50, "home": 0.16,
                     "why": "k shrinks the difference between two clubs' season log-odds; 0.50 reflects that a "
                            "best-of-series meeting between a .636 and a .605 club is close. Home edge 0.16 in "
                            "logit units is the long-run MLB home-field figure (~54%)."},
        "Ice Hockey": {"k": 0.55, "home": 0.20,
                       "why": "Points-percentage log-odds shrunk by 0.55 (an 11-game sample is noisy) plus a 0.20 "
                              "home term (~55% home win rate in the NHL)."},
        "Snooker": {"k": 2.40, "home": 0.0,
                    "why": "Strength is a 0-100 blend of frames won in this event (50%) and a rank score "
                           "(37-position)/36 where the player is inside the published top 36 (50%). The 2.40 "
                           "coefficient maps a 0.20 strength gap onto roughly a 61% best-of-7 win chance."},
        "Rugby Union": {"k": 0.0, "home": 0.12,
                        "why": "No league table was readable, so the strength term is switched off entirely and "
                               "only a 0.12 home term is applied. Confidence is capped at Low."},
    },
    "totals": {
        "Ice Hockey": {"mean": 6.0, "sd": 2.0, "line": 5.5, "unit": "goals"},
        "Baseball": {"mean": 8.6, "sd": 4.2, "line": 8.5, "unit": "runs"},
        "Rugby Union": {"mean": 45.0, "sd": 13.0, "line": 45.5, "unit": "points"},
        "Snooker": {"line": 5.5, "unit": "frames", "why": "Exact best-of-7 distribution, no approximation."},
    },
    "handicap": {
        "Ice Hockey": {"line": 1.5, "sd": 2.3, "mu_scale": 1.60, "unit": "goals"},
        "Baseball": {"line": 1.5, "sd": 4.0, "mu_scale": 1.10, "unit": "runs"},
        "Rugby Union": {"line": 7.5, "sd": 14.0, "mu_scale": 6.0, "unit": "points"},
        "Snooker": {"line": 1.5, "unit": "frames", "why": "Exact best-of-7 distribution."},
    },
    "field": {"exponent": 1.5, "offset": 10.0,
              "why": "Outright weight = (points + 10)^1.5. The offset keeps zero-point drivers priced as longshots "
                     "rather than at infinite odds; the exponent prices a 340-point leader at roughly 22% in a "
                     "23-driver field."},
    "overround": {"two_way": 0.045, "three_way": 0.060, "field": 0.075},
    "tiers": {"high": 0.70, "medium": 0.55},
    "band": {"min_decimal": 1.40, "max_decimal": 101.00,
             "note": "Brief: focus on selections priced between -250 (1.40) and +10000 (101.0)."},
}


def logistic(x):
    return 1.0 / (1.0 + math.exp(-x))


def logit(p):
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1 - p))


def phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def dec(p):
    return round(1.0 / p, 2) if p > 0 else None


def american(d):
    if d is None or d <= 1.0:
        return ""
    a = (d - 1.0) * 100.0 if d >= 2.0 else -100.0 / (d - 1.0)
    return f"+{a:.0f}" if a > 0 else f"{a:.0f}"


def pct(p):
    return f"{100.0*p:.1f}%"


# ---------------------------------------------------------------------------- snooker exact math
def wst_score_dist(q):
    """P(final frame score) for the player with per-frame probability q, first to 4."""
    d = {}
    for k in range(4):  # win 4-k
        d[f"4-{k}"] = math.comb(3 + k, k) * q ** 4 * (1 - q) ** k
    for k in range(4):  # lose 0-4 .. 3-4
        d[f"{k}-4"] = math.comb(3 + k, k) * (1 - q) ** 4 * q ** k
    return d


def q_for_match(p):
    lo, hi = 0.01, 0.99
    for _ in range(200):
        mid = (lo + hi) / 2
        if wst_score_dist(mid)["4-0"] + wst_score_dist(mid)["4-1"] + wst_score_dist(mid)["4-2"] + wst_score_dist(mid)["4-3"] < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------------------------- strength
def strength(fx, side):
    inp = fx["inputs"][side]
    return inp.get("rating")


def match_probabilities(fx):
    """Return dict of p(home win), p(away win), p(draw) plus a method label."""
    if fx.get("kind") == "field":
        return None
    sport = fx["sport"]
    conf = ASSUMPTIONS["moneyline_shrink"].get(sport, {"k": 0.0, "home": 0.0})
    sh, sa = strength(fx, "home"), strength(fx, "away")
    if sport == "Snooker":
        # blend frames-won% with rank score
        def sn_str(side):
            r = fx["inputs"][side].get("rating")
            rk = fx["inputs"][side].get("rank")
            rank_score = ((37 - rk) / 36.0) if rk else 0.0
            return 0.5 * (r / 100.0) + 0.5 * rank_score
        h, a = sn_str("home"), sn_str("away")
        ph = logistic(conf["k"] * (h - a))
        return {"home": ph, "away": 1 - ph, "draw": 0.0, "method": "form+rank blend"}
    if sh is None or sa is None:
        ph = logistic(conf["home"])
        out = {"home": ph, "away": 1 - ph, "draw": 0.0, "method": "neutral baseline (one or both inputs blank)"}
        if sport == "Rugby Union":
            draw = 0.03
            out = {"home": (1 - draw) * ph, "away": (1 - draw) * (1 - ph), "draw": draw,
                   "method": "neutral baseline (no official league table readable)"}
        return out
    ph = logistic(conf["k"] * (logit(sh / 100.0) - logit(sa / 100.0)) + conf["home"])
    out = {"home": ph, "away": 1 - ph, "draw": 0.0, "method": "sourced rating difference"}
    if sport == "Rugby Union":
        draw = 0.03
        out = {"home": (1 - draw) * ph, "away": (1 - draw) * (1 - ph), "draw": draw}
    return out


# ------------------------------------------------------------------------------------ markets
def build_markets(fx):
    """Return list of dicts: id, market, selection, prob, fair_dec, book_dec, american."""
    ms = []
    if fx.get("kind") == "field":
        total = sum((d["points"] + 10.0) ** 1.5 for d in FIELD)
        v = ASSUMPTIONS["overround"]["field"]
        for d in FIELD:
            p = (d["points"] + 10.0) ** 1.5 / total
            ms.append(dict(sel=d["name"], market="Race winner (outright)",
                           detail=f"{d['team']} · {d['points']} pts",
                           prob=p, fair=dec(p), book=round(1 / (p * (1 + v)), 2), american=american(dec(p))))
        return ms

    mp = match_probabilities(fx)
    sport = fx["sport"]
    two = ASSUMPTIONS["overround"]["two_way"]
    three = ASSUMPTIONS["overround"]["three_way"]

    def add(market, sel, detail, p, v):
        ms.append(dict(sel=sel, market=market, detail=detail, prob=p, fair=dec(p),
                       book=round(1 / (p * (1 + v)), 2) if p > 0 else None, american=american(dec(p))))

    add("Match winner", fx["home"], fx["inputs"]["home"]["value"], mp["home"], three if mp["draw"] else two)
    add("Match winner", fx["away"], fx["inputs"]["away"]["value"], mp["away"], three if mp["draw"] else two)
    if mp["draw"]:
        add("Match winner", "Draw", "Rugby draw (model draw allowance 3.0%)", mp["draw"], three)

    if sport == "Snooker":
        q = q_for_match(mp["home"])
        dist = wst_score_dist(q)
        home_margin = sum(p for s, p in dist.items() if s.startswith("4-") and int(s.split("-")[1]) <= 2)
        away_margin = sum(p for s, p in dist.items() if s.endswith("-4") and int(s.split("-")[0]) <= 2)
        over = dist["4-2"] + dist["4-3"] + dist["3-4"] + dist["2-4"]
        add("Frame handicap (1.5)", f"{fx['home']} -1.5", "home wins by two frames or more (4-0, 4-1 or 4-2)", home_margin, two)
        add("Frame handicap (1.5)", f"{fx['away']} +1.5", "away loses by one frame or fewer, or wins", 1 - home_margin, two)
        add("Frame handicap (1.5)", f"{fx['away']} -1.5", "away wins by two frames or more (4-0, 4-1 or 4-2)", away_margin, two)
        add("Frame handicap (1.5)", f"{fx['home']} +1.5", "home loses by one frame or fewer, or wins", 1 - away_margin, two)
        add("Total frames", "Over 5.5", "the match reaches a deciding frame or a 4-2/2-4 finish", over, two)
        add("Total frames", "Under 5.5", "4-1, 1-4, 4-0 or 0-4", 1 - over, two)
        return ms

    if sport == "Rugby Union":
        # No sourced points baseline exists (no official table could be read), so a handicap line or a
        # total would be an invented number. Only the two-way winner and the draw are originated.
        return ms

    hc = ASSUMPTIONS["handicap"].get(sport)
    tot = ASSUMPTIONS["totals"].get(sport)
    if hc:
        mu = hc["mu_scale"] * (2 * mp["home"] - 1)
        line = hc["line"]
        p_home_minus = 1 - phi((line - mu) / hc["sd"])          # home wins by more than the line
        p_away_minus = phi((-line - mu) / hc["sd"])             # away wins by more than the line
        label = f"Handicap ({line:g} {hc['unit']})"
        add(label, f"{fx['home']} -{line:g}", f"home wins by {line:g}+ {hc['unit']}", p_home_minus, two)
        add(label, f"{fx['away']} +{line:g}", f"away loses by fewer than {line:g} {hc['unit']}, or wins", 1 - p_home_minus, two)
        add(label, f"{fx['away']} -{line:g}", f"away wins by {line:g}+ {hc['unit']}", p_away_minus, two)
        add(label, f"{fx['home']} +{line:g}", f"home loses by fewer than {line:g} {hc['unit']}, or wins", 1 - p_away_minus, two)
    if tot:
        p_over = 1 - phi((tot["line"] - tot["mean"]) / tot["sd"])
        add(f"Total ({tot['line']:g} {tot['unit']})", f"Over {tot['line']:g}", f"combined {tot['unit']} above {tot['line']:g}", p_over, two)
        add(f"Total ({tot['line']:g} {tot['unit']})", f"Under {tot['line']:g}", f"combined {tot['unit']} below {tot['line']:g}", 1 - p_over, two)
    return ms


def tier_of(p, fx):
    t = ASSUMPTIONS["tiers"]
    if fx["sport"] == "Rugby Union":
        return "low"
    if p >= t["high"]:
        return "high"
    if p >= t["medium"]:
        return "medium"
    return "low"


def band_ok(fair):
    b = ASSUMPTIONS["band"]
    return fair is not None and b["min_decimal"] <= fair <= b["max_decimal"]


# ----------------------------------------------------------------------------------- generate
def generate():
    """Headline pick = the match-winner market (the brief's "pick a match winner").
    A second column carries the highest-probability selection anywhere on the board."""
    fixtures, markets, picks = [], [], []
    for fx in FIXTURES:
        ms = build_markets(fx)
        markets.append({"id": fx["id"], "markets": ms})
        winners = [m for m in ms if m["market"].startswith("Match winner") or m["market"].startswith("Race winner")]
        if fx.get("kind") == "field":
            win = max(winners, key=lambda m: m["prob"])
        else:
            win = max([w for w in winners if w["sel"] != "Draw"], key=lambda m: m["prob"])
        best = max(ms, key=lambda m: m["prob"])
        picks.append({
            "match_id": fx["id"], "sport": fx["sport"], "competition": fx["competition"],
            "start_utc": fx["start_utc"], "start_published": fx["start_published"],
            "home": fx["home"], "away": fx["away"], "venue": fx.get("venue", ""),
            "market": win["market"], "selection": win["sel"], "detail": win["detail"],
            "prob": round(win["prob"], 4), "fair_decimal": win["fair"], "american": win["american"],
            "book_decimal": win["book"], "confidence": tier_of(win["prob"], fx),
            "in_brief_band": band_ok(win["fair"]),
            "best_market": best["market"], "best_selection": best["sel"],
            "best_prob": round(best["prob"], 4), "best_fair_decimal": best["fair"],
            "best_american": best["american"], "best_confidence": tier_of(best["prob"], fx),
            "best_in_brief_band": band_ok(best["fair"]),
            "sources": fx["sources"],
        })
        fixtures.append(fx)

    high_prob = []
    for m in markets:
        for sel in m["markets"]:
            if sel["prob"] >= ASSUMPTIONS["tiers"]["high"]:
                high_prob.append({"match_id": m["id"], "market": sel["market"], "selection": sel["sel"],
                                  "detail": sel["detail"], "prob": round(sel["prob"], 4),
                                  "fair_decimal": sel["fair"], "american": sel["american"],
                                  "book_decimal": sel["book"],
                                  "in_brief_band": band_ok(sel["fair"])})
    high_prob.sort(key=lambda r: -r["prob"])
    return fixtures, markets, picks, high_prob


def main():
    fixtures, markets, picks, high_prob = generate()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SITE, exist_ok=True)

    from s7a5b5360_content import PREDICTIONS, FLAGS, METHOD_TEXT, REPO_REVIEW

    by_id = {f["id"]: f for f in fixtures}
    preds = []
    for key, text in PREDICTIONS.items():
        mid, _, sel = key.partition("::")
        pk = next((p for p in picks if p["match_id"] == mid), None)
        ms = next((m for m in markets if m["id"] == mid), None)
        if not pk or not ms:
            raise SystemExit("prediction references unknown fixture: " + mid)
        selection = next((s for s in ms["markets"] if s["sel"] == sel), None)
        if selection is None:
            raise SystemExit(f"prediction references unknown selection: {mid} :: {sel}")
        preds.append({
            "match_id": mid, "sport": by_id[mid]["sport"], "home": by_id[mid]["home"],
            "away": by_id[mid]["away"], "competition": by_id[mid]["competition"],
            "start_utc": by_id[mid]["start_utc"], "start_published": by_id[mid]["start_published"],
            "market": selection["market"], "selection": selection["sel"],
            "probability": round(selection["prob"], 4), "fair_decimal": selection["fair"],
            "american": selection["american"], "confidence": tier_of(selection["prob"], by_id[mid]),
            "words": len(text.split()), "text": text, "sources": by_id[mid]["sources"],
        })

    counts = {"fixtures": len(fixtures), "markets": sum(len(m["markets"]) for m in markets),
              "picks": len(picks), "predictions": len(preds), "high_probability_selections": len(high_prob)}
    for t in ("high", "medium", "low"):
        counts["picks_" + t] = sum(1 for p in picks if p["confidence"] == t)

    bundle = {
        "session": "7a5b5360-olbg1", "task": "T41", "retrieved_utc": RETRIEVED_UTC, "window": WINDOW,
        "assumptions": ASSUMPTIONS, "counts": counts,
    }
    def dump(name, obj):
        with open(os.path.join(OUT, name), "w") as fh:
            json.dump(obj, fh, indent=1, sort_keys=False)
            fh.write("\n")

    dump("bundle.json", bundle)
    dump("sources.json", SOURCES)
    dump("coverage.json", {"excluded": EXCLUDED, "in_scope": IN_SCOPE, "coverage": COVERAGE})
    dump("fixtures.json", {"meta": bundle, "fixtures": fixtures})
    dump("markets.json", {"meta": bundle, "boards": markets})
    dump("picks.json", {"meta": bundle, "picks": picks})
    dump("predictions.json", {"meta": bundle, "items": preds})
    dump("high_probability.json", {"meta": bundle, "selections": high_prob})
    dump("flags.json", {"meta": bundle, "flags": FLAGS, "repo_review": REPO_REVIEW})

    with open(os.path.join(OUT, "matches.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["match_id", "sport", "competition", "stage", "start_utc", "start_published",
                    "home", "away", "venue", "home_input", "away_input", "pick_market", "pick_selection",
                    "pick_probability", "pick_fair_decimal", "pick_american", "confidence",
                    "in_brief_band", "source_urls"])
        for fx, pk in zip(fixtures, picks):
            w.writerow([fx["id"], fx["sport"], fx["competition"], fx["stage"], fx["start_utc"],
                        fx["start_published"], fx["home"], fx["away"], fx.get("venue", ""),
                        fx["inputs"].get("home", {}).get("value", ""),
                        fx["inputs"].get("away", {}).get("value", ""),
                        pk["market"], pk["selection"], pk["prob"], pk["fair_decimal"],
                        pk["american"], pk["confidence"], pk["in_brief_band"],
                        " | ".join(SOURCES[s]["url"] for s in fx["sources"])])

    from s7a5b5360_site import build_site
    pages = build_site(bundle, fixtures, markets, picks, preds, high_prob, SOURCES,
                       COVERAGE, FLAGS, METHOD_TEXT, REPO_REVIEW, ASSUMPTIONS, FIELD, F1_EVENT,
                       EXCLUDED, IN_SCOPE)
    print("counts:", json.dumps(counts))
    print("pages:", pages)


if __name__ == "__main__":
    main()
