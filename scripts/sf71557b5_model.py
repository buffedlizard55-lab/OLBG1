#!/usr/bin/env python3
"""
sf71557b5_model.py - session f71557b5-olbg1 (task T50) line origination.

Turns data/f71557b5/fixtures.json into originated multi-market prices, a
match-winner call per fixture, a desk selection per fixture, confidence tiers and
the two audit tables the brief asks for (Rejected Highs, no-bet reasons).

Pricing policy, printed in full on the desk methodology page:

* The originated line is the **zero-vig fair price** (1 / model probability). The
  5% book-equivalent is published next to it for comparison but is not the line
  the price window is tested against. See finding F-F7-01: with a book margin the
  brief's ">70%" and ">= -250" rules cannot both hold, because 70% at a 5%
  overround prices at -277.
* High confidence requires: status verified, a sourced rating on BOTH sides,
  model probability >= 0.700, and a fair price inside -250 .. +10000. Because
  -250 is exactly a 71.43% fair price, the admissible High band is
  0.700 <= p <= 0.7143 and the qualifying rung is chosen from a standard
  sport-specific ladder (no model-calibrated alternate lines).
* A fixture whose favourite is shorter than -250 can still produce a High pick on
  a handicap rung, but never on the moneyline.
* Where only one side carries a sourced rating the strength edge is refused: the
  line falls back to a neutral baseline and confidence is capped at Low.
* Totals are priced only where BOTH sides' scoring rates were read on an official
  page (NHL goals for/against per game, MLB runs scored/allowed per game). Every
  other total is investigated-not-priced with the missing input named.

Run:  python3 scripts/sf71557b5_model.py
Writes: data/f71557b5/{lines,predictions,window}.json, data/f71557b5/matches.csv
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
from collections import Counter

import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from sf71557b5_prose import PROSE  # noqa: E402

D = ROOT / "data" / "f71557b5"

MARGIN = 0.05          # 5% overround, used only for the published book-equivalent
BAND_LO_US = -250      # brief's window floor
BAND_HI_US = 10000     # brief's window ceiling
HIGH_P = 0.700
MED_P = 0.55
BET_P = 0.52

# Labelled modelling constants. These are choices, not statistics, and are printed
# as such on the methodology page and in every market's `basis` string.
CONST = {
    "nhl_hfa": 0.25, "nhl_sigma": 1.30, "nhl_ppg_k": 2.0,
    "mlb_hfa": 0.35, "mlb_sigma": 4.30, "mlb_sigma_total": 4.30,
    "nba_hfa": 0.05, "nba_sigma": 12.0,
    "el_k": 22.0, "el_hfa": 3.0, "el_sigma": 13.0,
    "ru_sigma": 12.0, "gaa_sigma": 6.0, "aflw_sigma": 28.0, "aflw_scale": 0.65,
    "hb_h2h_shrink": 0.60, "hb_hfa": 1.5, "hb_sigma": 6.0,
    "neutral_hfa": 1.0, "neutral_sigma": 12.0,
    "darts_seed_k": 0.0035, "darts_oom_k": 0.03, "darts_legs_to_win": 6,
    "snooker_top16": 0.06, "snooker_frames_to_win": 5,
}

# Standard ladder rungs per sport (absolute handicap on the home/listed-first side).
LADDERS = {
    "ice-hockey": [0.0, 0.5, 1.5, 2.5, 3.5],
    "basketball": [0.0] + [x / 2 for x in range(3, 42, 2)],       # 1.5 .. 20.5
    "baseball": [0.0, 1.5, 2.5],
    "rugby-union": [0.0] + [x / 2 for x in range(3, 62, 2)],      # 1.5 .. 30.5
    "rugby-league": [0.0] + [x / 2 for x in range(3, 62, 2)],
    "aussie-rules": [0.0] + [x / 2 for x in range(3, 162, 2)],    # 1.5 .. 80.5
    "gaelic-football": [0.0] + [x / 2 for x in range(3, 32, 2)],  # 1.5 .. 15.5
    "handball": [0.0] + [x / 2 for x in range(3, 32, 2)],
    "darts": [0.0, 0.5, 1.5, 2.5, 3.5, 4.5],
    "snooker": [0.0, 0.5, 1.5, 2.5, 3.5],
    "cricket": [0.0],
}
TOTAL_LADDERS = {
    # Ice hockey is deliberately absent: see flag F-F7-NHL-01. No sourced scoring
    # rate survives reconciliation, so no NHL total is originated.
    "baseball": [x / 2 for x in range(13, 22, 2)],    # 6.5 .. 10.5
}
UNIT = {"ice-hockey": "goals", "basketball": "points", "baseball": "runs",
        "rugby-union": "points", "rugby-league": "points", "aussie-rules": "points",
        "gaelic-football": "points", "handball": "goals", "darts": "legs",
        "snooker": "frames", "cricket": "runs"}


def phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def phi_inv(p: float) -> float:
    p = min(max(p, 1e-9), 1 - 1e-9)
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def us_from_price(price: float) -> int:
    if price >= 2.0:
        return int(round((price - 1) * 100))
    if price <= 1.01:
        return -10000                      # desk display bound; anything shorter is printed as -10000
    return -int(round(100 / (price - 1)))


# Probabilities are clamped to the desk's display bounds so no line is ever printed
# shorter than -10000 or longer than +10000. A clamped outcome is marked and is
# never eligible to be a selection.
P_LO, P_HI = 0.0099, 0.9901


def clamp(p: float) -> float:
    return min(max(p, P_LO), P_HI)


def fair(p: float) -> float:
    return round(1.0 / clamp(p), 2)


def book(p: float) -> float:
    return round(1.0 / (clamp(p) * (1 + MARGIN)), 2)


def in_band(p: float) -> bool:
    if not (0 < p < 1):
        return False
    us = us_from_price(fair(p))
    return BAND_LO_US <= us <= BAND_HI_US


def market(label, outcomes, basis, h=0.0, kind="winner"):
    """outcomes: list of (name, probability). `h` is the rung magnitude, `kind` is
    winner / handicap / total - used so the desk can prefer the tightest line."""
    rows = []
    for name, p in outcomes:
        capped = not (P_LO <= p <= P_HI)
        rows.append({"selection": name, "prob": round(clamp(p), 4), "raw_prob": round(p, 6),
                     "capped": capped, "price": fair(p), "us": us_from_price(fair(p)),
                     "book_price": book(p), "book_us": us_from_price(book(p)),
                     "in_band": (not capped) and in_band(p), "h": h, "kind": kind})
    return {"market": label, "outcomes": rows, "basis": basis, "h": h, "kind": kind}


# --------------------------------------------------------------------------
# First-to-N score distribution (darts legs / snooker frames).
# --------------------------------------------------------------------------
def first_to_dist(p: float, n: int):
    """Return {margin: probability} for the winner plus p_win."""
    q = 1 - p
    dist = {}
    pwin = 0.0
    for x in range(n):                      # winner takes n, loser takes x
        ways = math.comb(n - 1 + x, x)
        dist[n - x] = dist.get(n - x, 0) + ways * (p ** n) * (q ** x)
        pwin += ways * (p ** n) * (q ** x)
    for x in range(n):                      # loser takes n
        ways = math.comb(n - 1 + x, x)
        dist[-(n - x)] = dist.get(-(n - x), 0) + ways * (q ** n) * (p ** x)
    return dist, pwin


def cover(dist, side, h):
    """P(side covers a handicap of h points in its favour)."""
    return sum(v for k, v in dist.items() if (k if side == "home" else -k) > h - 1e-9)


GAA_DETAIL = {
    "gaa-cork-psfc-final": dict(margin_home=0.0, both_sourced=True, detail=(
        "St Finbarrs semi-final +2 (2-12 to 0-16 v Clonakilty); Nemo Rangers semi-final +2 (1-15 to 0-16 v "
        "Carrigaline) and quarter-final +3 (1-20 to 1-17 v Castlehaven); the 2025 final between these two clubs "
        "was won by St Finbarrs 1-14 to 1-13 (+1). Recent averages are St Finbarrs +1.5 and Nemo Rangers +2.5, so "
        "half the difference (-0.5) plus half the verified head-to-head (+0.5) gives a dead-even expected margin.")),
    "gaa-wat-sfc-final": dict(margin_home=0.33, both_sourced=True, detail=(
        "Rathgormack semi-final +2 (1-14 to 0-15 v Gaultier), round 6 +19 (5-15 to 2-5 v Abbeyside-Ballinacourty), "
        "round 5 -4 (1-7 to 1-11 at Abbeyside); The Nire semi-final +7 (0-12 to 0-5 v Abbeyside-Ballinacourty) and "
        "round 6 +3 (2-10 to 0-13 v Gaultier).")),
    "gaa-gal-sfc-final": dict(margin_home=7.15, both_sourced=False, detail=(
        "Only one verified head-to-head exists: Maigh Cuilinn 3-12 to Salthill-Knocknacarra 0-8 in league round 4 "
        "on 10 April 2026 (+13). Salthill-Knocknacarra's championship scores were not read on an official page, so "
        "the margin is 55% of the verified head-to-head and confidence is capped at Medium.")),
    "gaa-cork-safc-final": dict(margin_home=3.5, both_sourced=True, detail=(
        "Eire Og round 3 +15 (0-24 to 0-9 v Kilshannig) and semi-final +3 (2-16 to 1-16 v Cill na Martra); Kanturk "
        "round 3 level (2-8 to 1-11 v Aghabullogue) and semi-final +4 (1-18 to 1-14 v Carbery Rangers).")),
    "gaa-lim-sfc-final": dict(margin_home=5.0, both_sourced=True, detail=(
        "Fr Caseys semi-final +12 (3-12 to 1-06 v Monaleen, 17 October, Sean Finn Park); Kildimo Pallaskenry "
        "semi-final +2 after extra time (2-16 to 0-20 v Mungret St Pauls, 17 October, Clarina).")),
}


# --------------------------------------------------------------------------
# Per-fixture margin models. Each returns (m, sigma, both_sourced, notes).
# m is the expected margin from the perspective of the listed home side.
# --------------------------------------------------------------------------
def margin_for(fx):
    mdl = fx.get("model")
    if not mdl:
        return 0.0, CONST["neutral_sigma"], False, [
            "No sourced rating on either side: neutral baseline at evens, confidence capped at Low and the "
            "fixture published as no-bet (repository rule 4)."], None, None
    kind = mdl["kind"]
    notes = []
    if kind == "nhl":
        d = mdl["home_ppg"] - mdl["away_ppg"]
        m = d * CONST["nhl_ppg_k"] + CONST["nhl_hfa"]
        notes.append(f"Expected goal margin from the official points-per-game gap "
                     f"({mdl['home_ppg']:.3f} v {mdl['away_ppg']:.3f}, i.e. {mdl['home_rec']} on {mdl['home_pts']} "
                     f"points v {mdl['away_rec']} on {mdl['away_pts']}) scaled by the labelled constant "
                     f"{CONST['nhl_ppg_k']} goals per 1.000 of points percentage, plus {CONST['nhl_hfa']} goals of "
                     f"home ice. Spread assumption {CONST['nhl_sigma']} goals. No goals-for/against value is used "
                     f"anywhere (see flag F-F7-NHL-01) and no match total is priced for this sport.")
        return m, CONST["nhl_sigma"], True, notes, None, None
    if kind == "mlb":
        hg, ha = mdl["home_rs_pg"], mdl["home_ra_pg"]
        ag, aa = mdl["away_rs_pg"], mdl["away_ra_pg"]
        m = ((hg - ha) - (ag - aa)) / 2 + CONST["mlb_hfa"]
        notes.append(f"Expected run margin from 162-game runs scored/allowed per game "
                     f"({hg:.2f}-{ha:.2f} home, {ag:.2f}-{aa:.2f} away) plus a {CONST['mlb_hfa']}-run home constant.")
        total = (hg + ha + ag + aa) / 2
        return m, CONST["mlb_sigma"], True, notes, total, CONST["mlb_sigma_total"]
    if kind == "euroleague":
        hp = mdl["home_w"] / (mdl["home_w"] + mdl["home_l"])
        ap = mdl["away_w"] / (mdl["away_w"] + mdl["away_l"])
        neutral = "neutral" in (fx.get("venue") or "")
        hfa = 0.0 if neutral else CONST["el_hfa"]
        m = (hp - ap) * CONST["el_k"] + hfa
        hfa_txt = "no home term (the official preview names a neutral venue)" if neutral else f"{CONST['el_hfa']} points of home court"
        notes.append(f"Expected point margin from Round 7 win percentage ({mdl['home_w']}-{mdl['home_l']} v "
                     f"{mdl['away_w']}-{mdl['away_l']}) scaled by {CONST['el_k']} points per full win percentage, "
                     f"plus {hfa_txt}. Spread assumption {CONST['el_sigma']} points.")
        return m, CONST["el_sigma"], True, notes, None, None
    if kind == "lnr_published":
        p_h = mdl["home_pct"] / (mdl["home_pct"] + mdl["away_pct"])
        m = phi_inv(p_h) * CONST["ru_sigma"]
        notes.append(f"Anchored on the league's own published three-way probabilities "
                     f"({mdl['home_pct']:.2f}% / {mdl['away_pct']:.2f}% / {mdl['draw_pct']:.2f}%), converted to a "
                     f"draw-no-bet win probability of {p_h*100:.2f}% and then to an expected point margin "
                     f"with a {CONST['ru_sigma']}-point spread assumption.")
        return m, CONST["ru_sigma"], True, notes, None, None
    if kind == "handball_h2h":
        m = mdl["h2h_margin"] * CONST["hb_h2h_shrink"] + CONST["hb_hfa"]
        notes.append(f"Expected goal margin from the verified same-competition head-to-head "
                     f"({mdl['h2h_margin']} goals) shrunk by {CONST['hb_h2h_shrink']} for a single observation, "
                     f"plus a {CONST['hb_hfa']}-goal home constant.")
        return m, CONST["hb_sigma"], True, notes, None, None
    if kind == "cricket_margin":
        # margin_runs is the verified gap favouring the AWAY side in both fixtures that carry it.
        m = -mdl["margin_runs"]
        notes.append(f"Expected run margin {m:+.1f} from the home side's perspective, taken directly from the "
                     f"sourced {mdl['margin_runs']}-run gap that favours the away side, with a "
                     f"{mdl['sigma']}-run spread (labelled assumption).")
        return m, mdl["sigma"], True, notes, None, None
    if kind == "aflw":
        raw = (mdl["home_pts"] - mdl["away_pts"]) * 3.0 + (mdl["home_pct"] - mdl["away_pct"]) / 100 * 20
        m = raw * CONST["aflw_scale"]
        notes.append(f"Ladder input ({mdl['home_pts']} pts / {mdl['home_pct']}% v {mdl['away_pts']} pts / "
                     f"{mdl['away_pct']}%) mapped to points at 3 per ladder point plus 20 per 100% of percentage, "
                     f"then scaled by {CONST['aflw_scale']} - the scale calibrated against the two Round 10 margins "
                     f"read on AFL.com.au (51 and 53 points) - with a {CONST['aflw_sigma']}-point spread.")
        return m, CONST["aflw_sigma"], True, notes, None, None
    if kind == "gaa":
        det = GAA_DETAIL.get(fx["id"], {})
        m = det.get("margin_home", 0.0)
        notes.append(f"Expected point margin {m:+.2f} from verified championship scores (a goal counts as three "
                     f"points). {det.get('detail', '')} Spread assumption {CONST['gaa_sigma']} points.")
        return m, CONST["gaa_sigma"], det.get("both_sourced", True), notes, None, None
    if kind == "darts":
        s1, s2 = mdl.get("seed_home"), mdl.get("seed_away")
        o1, o2 = mdl.get("oom_home"), mdl.get("oom_away")
        seed_term = CONST["darts_seed_k"] * (s2 - s1) if (s1 and s2) else 0.0
        oom_term = 0.0
        if o1 and o2:
            oom_term = CONST["darts_oom_k"] * math.tanh((math.log(o1) - math.log(o2)) / 2)
        p_leg = min(max(0.5 + seed_term + oom_term, 0.30), 0.72)
        dist, pwin = first_to_dist(p_leg, CONST["darts_legs_to_win"])
        notes.append(f"Per-leg win probability {p_leg:.3f} from the official seed gap "
                     f"({s1 if s1 else 'not published'} v {s2 if s2 else 'not published'}) and Order of Merit money, "
                     f"then a first-to-{CONST['darts_legs_to_win']} leg distribution. "
                     f"FORMAT ASSUMPTION: the best-of length was not printed on the official pages read, "
                     f"so first-to-{CONST['darts_legs_to_win']} is a labelled modelling choice.")
        return ("dist", dist, pwin), None, (s1 and s2) or (o1 and o2), notes, None, None
    if kind == "snooker":
        edge = CONST["snooker_top16"] * (int(mdl["home_top16"]) - int(mdl["away_top16"]))
        p_frame = min(max(0.5 + edge, 0.30), 0.72)
        dist, pwin = first_to_dist(p_frame, CONST["snooker_frames_to_win"])
        both = mdl["home_top16"] != mdl["away_top16"]
        notes.append(f"Per-frame win probability {p_frame:.3f}"
                     + (f" from verified world top-16 status ({mdl['note'][:90]}...)" if both else
                        " - neither player's top-16 status nor a Round 2 score was read for BOTH sides, so no "
                        "strength edge is applied and confidence is capped at Low (repository rule 4).")
                     + f" FORMAT ASSUMPTION: first-to-{CONST['snooker_frames_to_win']} frames; the best-of length "
                       "for this round was not printed on the official page read.")
        return ("dist", dist, pwin), None, both, notes, None, None
    if kind == "nba_onesided":
        m = CONST["nba_hfa"] * CONST["nba_sigma"]
        notes.append("Only the home club has a verified 2026-27 result; the visitor has not yet played. "
                     "Per repository rule 4 the line is a neutral baseline plus a documented home-court term "
                     f"and confidence is capped at Low.")
        return m, CONST["nba_sigma"], False, notes, None, None
    if kind == "one_sided":
        m = CONST["neutral_hfa"]
        notes.append("Only one club has a verified 2026/27 result on an official EHF page. Per repository rule 4 "
                     "the strength edge is refused: neutral baseline plus a documented home-court term, "
                     "confidence capped at Low.")
        return m, CONST["neutral_sigma"], False, notes, None, None
    return 0.0, CONST["neutral_sigma"], False, ["Unhandled model kind - neutral baseline."], None, None, None, None


def build():
    fx = json.loads((D / "fixtures.json").read_text(encoding="utf-8"))["fixtures"]
    rows, rejected, nobet = [], [], []

    for f in fx:
        home, away = f["home"], (f.get("away") or "")
        sport = f["sport"]
        row = {"id": f["id"], "sport": sport, "competition": f["competition"], "round": f.get("round", ""),
               "home": home, "away": away, "venue": f.get("venue", ""),
               "start_utc": f.get("start_utc", ""), "start_local": f.get("start_local", ""),
               "status": f["status"], "event_only": f.get("event_only", False),
               "sources": f["sources"], "evidence": f.get("evidence", []), "flags": f.get("flags", []),
               "markets": [], "selection": None, "winner_call": None, "rejected_highs": []}

        if f.get("event_only"):
            row["note"] = ("Event card: the official pages read publish the event but no field, entry list, "
                           "qualifying order or drawn pairing, so no outright price is originated. Market "
                           "investigated, not priced.")
            rows.append(row)
            continue

        out = margin_for(f)
        notes = out[3]
        both = out[2]

        if isinstance(out[0], tuple):              # darts / snooker first-to-N distribution
            _, dist, pwin = out[0]
            ladder = LADDERS[sport]
            unit = UNIT[sport]
            wm = market("Match winner", [(home, pwin), (away, 1 - pwin)], notes[-1], h=0.0, kind="winner")
            row["markets"].append(wm)
            for h in ladder:
                if h == 0.0:
                    continue
                ph = cover(dist, "home", h)
                if not (0.05 <= ph <= 0.95):
                    continue
                row["markets"].append(market(
                    f"{unit.capitalize()} handicap ({h})",
                    [(f"{home} -{h}", ph), (f"{away} +{h}", 1 - ph)],
                    f"First-to-{CONST['darts_legs_to_win' if sport == 'darts' else 'snooker_frames_to_win']} "
                    f"{unit} distribution; rung kept only while both sides price between 5% and 95%. {notes[-1]}",
                    h=h, kind="handicap"))
            base_p, base_name = (pwin, home) if pwin >= 0.5 else (1 - pwin, away)
        else:
            m, sigma = out[0], out[1]
            total, sigma_total = out[4], out[5]
            p_home = phi(m / sigma)
            ladder = LADDERS.get(sport, [0.0])
            unit = UNIT.get(sport, "points")
            row["markets"].append(market("Match winner", [(home, p_home), (away, 1 - p_home)], notes[-1],
                                         h=0.0, kind="winner"))
            for h in ladder:
                if h == 0.0:
                    continue
                ph = phi((m - h) / sigma)
                if not (0.05 <= ph <= 0.95):
                    continue
                row["markets"].append(market(
                    f"{unit.capitalize()} handicap ({h})",
                    [(f"{home} -{h}", ph), (f"{away} +{h}", 1 - ph)],
                    f"Same expected margin ({m:+.2f} {unit}, spread {sigma}) shifted by the rung; kept only while "
                    f"both sides price between 5% and 95%. {notes[-1]}",
                    h=h, kind="handicap"))
            if total is not None:
                for t in TOTAL_LADDERS.get(sport, []):
                    po = phi((total - t) / sigma_total)
                    if not (0.05 <= po <= 0.95):
                        continue
                    row["markets"].append(market(
                        f"Match total ({t})",
                        [(f"Over {t}", po), (f"Under {t}", 1 - po)],
                        f"Expected total {total:.2f} {unit} built from both clubs' verified scoring rates, "
                        f"spread {sigma_total} (labelled assumption).",
                        h=0.0, kind="total"))
            else:
                row["flags"] = row["flags"] + [{
                    "code": f"F-F7-TOT-{f['id'][:14]}",
                    "text": f"Match total investigated, not priced: the official pages read for this fixture do not "
                            f"publish both sides' per-match scoring rate (or the match format needed to convert it), "
                            f"so no total baseline is sourced. Left blank rather than filled with a league constant."}]
            base_p, base_name = (p_home, home) if p_home >= 0.5 else (1 - p_home, away)

        # ---- match-winner call (always published, own tier) -----------------
        wc_capped = not (P_LO <= base_p <= P_HI)
        wc_p = round(clamp(base_p), 4)
        row["winner_call"] = {"selection": base_name, "prob": wc_p, "price": fair(base_p),
                              "us": us_from_price(fair(base_p)), "in_band": (not wc_capped) and in_band(base_p),
                              "capped": wc_capped,
                              "confidence": ("High" if (wc_p >= HIGH_P and not wc_capped and in_band(base_p)
                                                        and both and f["status"] == "verified") else
                                             "Medium" if wc_p >= MED_P else "Low"),
                              "cap": None if both else "Low (one-sided or absent sourced ratings - rule 4)"}

        # ---- desk selection: best band-compliant rung -----------------------
        cands = []
        for mk in row["markets"]:
            for o in mk["outcomes"]:
                if o["in_band"] and not o["capped"] and o["prob"] >= BET_P:
                    cands.append((o["prob"], mk["market"], o))
        # High-eligible candidates are ranked by the TIGHTEST line, not the highest
        # probability: a 71% call on a 3.5-point handicap is a real bet, a 71% call on a
        # 66.5-point alternate is an artefact of the ladder. Below the High threshold the
        # strongest in-window probability wins.
        high_cands = [c for c in cands if c[0] >= HIGH_P]
        if high_cands:
            cands = sorted(high_cands, key=lambda x: (x[2]["h"], -x[0]))
        else:
            cands.sort(key=lambda x: -x[0])
        if not cands:
            reason = ("No selection on this fixture is both inside the -250..+10000 window and at or above 52%: "
                      + ("every rung at or above 70% prices shorter than -250, and the in-window rungs sit below 52%."
                         if any(not o["in_band"] and o["prob"] >= HIGH_P for mk in row["markets"] for o in mk["outcomes"])
                         else "the sourced inputs do not separate the two sides enough to reach 52% inside the window."))
            row["selection"] = None
            nobet.append({"id": f["id"], "sport": sport, "match": f"{home} v {away}", "reason": reason})
        else:
            p, mkname, o = cands[0]
            tier = ("High" if (p >= HIGH_P and both and f["status"] == "verified") else
                    "Medium" if p >= MED_P else "Low")
            if not both and tier != "Low":
                tier = "Low"
            row["selection"] = {"market": mkname, "selection": o["selection"], "prob": round(p, 4),
                                "price": o["price"], "us": o["us"], "book_price": o["book_price"],
                                "book_us": o["book_us"], "confidence": tier,
                                "cap": None if both else "Low (one-sided or absent sourced ratings - rule 4)"}
            if tier == "High":
                row["selection"]["prose"] = PROSE.get(f["id"], "")
                row["selection"]["prose_missing"] = f["id"] not in PROSE

        # ---- rejected highs: >=70% but outside the window -------------------
        for mk in row["markets"]:
            for o in mk["outcomes"]:
                if not o["capped"] and o["prob"] >= HIGH_P and not o["in_band"]:
                    row["rejected_highs"].append({"market": mk["market"], "selection": o["selection"],
                                                  "prob": o["prob"], "price": o["price"], "us": o["us"]})
                    rejected.append({"id": f["id"], "sport": sport, "match": f"{home} v {away}",
                                     "market": mk["market"], "selection": o["selection"],
                                     "prob": o["prob"], "price": o["price"], "us": o["us"],
                                     "reason": "model probability at or above 70% but the fair price is shorter "
                                               "than -250, so the brief's window excludes it from High confidence"})
        row["model_notes"] = notes
        rows.append(row)

    tiers = Counter(r["selection"]["confidence"] for r in rows if r["selection"])
    wc_tiers = Counter(r["winner_call"]["confidence"] for r in rows if r["winner_call"])
    doc = {"session": "f71557b5-olbg1", "policy": {
        "line": "zero-vig fair price (book-equivalent at 5% shown alongside)",
        "window": [BAND_LO_US, BAND_HI_US], "high_prob": HIGH_P,
        "admissible_high_band": "0.700 <= p <= 0.7143 at a zero-vig line",
        "constants": CONST, "ladders": {k: v for k, v in LADDERS.items()},
        "total_ladders": TOTAL_LADDERS, "units": UNIT},
        "rows": rows, "counts": {
            "fixtures": len(rows),
            "event_cards": sum(1 for r in rows if r["event_only"]),
            "priced": sum(1 for r in rows if r["markets"]),
            "prices": sum(len(o) for r in rows for m in r["markets"] for o in [m["outcomes"]]),
            "selections": sum(1 for r in rows if r["selection"]),
            "no_bet": len(nobet),
            "high": tiers.get("High", 0), "medium": tiers.get("Medium", 0), "low": tiers.get("Low", 0),
            "winner_high": wc_tiers.get("High", 0), "winner_medium": wc_tiers.get("Medium", 0),
            "winner_low": wc_tiers.get("Low", 0),
            "rejected_highs": len(rejected),
            "sports": len({r["sport"] for r in rows}),
        }}
    (D / "lines.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    (D / "window.json").write_text(json.dumps({"rejected_highs": rejected, "no_bet": nobet},
                                              indent=1, ensure_ascii=False), encoding="utf-8")

    with (D / "matches.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "sport", "competition", "home", "away", "venue", "start_utc", "start_local",
                    "status", "markets", "prices", "selection", "selection_market", "prob", "fair_price",
                    "us", "book_price", "in_window", "confidence", "match_winner_call", "winner_prob",
                    "winner_us", "winner_confidence", "official_sources"])
        for r in rows:
            sel = r["selection"] or {}
            wc = r["winner_call"] or {}
            w.writerow([r["id"], r["sport"], r["competition"], r["home"], r["away"], r["venue"],
                        r["start_utc"], r["start_local"], r["status"], len(r["markets"]),
                        sum(len(m["outcomes"]) for m in r["markets"]),
                        sel.get("selection", ""), sel.get("market", ""), sel.get("prob", ""),
                        sel.get("price", ""), sel.get("us", ""), sel.get("book_price", ""),
                        sel.get("us", "") and BAND_LO_US <= sel["us"] <= BAND_HI_US,
                        sel.get("confidence", ""), wc.get("selection", ""), wc.get("prob", ""),
                        wc.get("us", ""), wc.get("confidence", ""),
                        " | ".join(s["url"] for s in r["sources"])])

    highs = [{"id": r["id"], "sport": r["sport"], "home": r["home"], "away": r["away"],
              "market": r["selection"]["market"], "selection": r["selection"]["selection"],
              "prob": r["selection"]["prob"], "price": r["selection"]["price"],
              "us": r["selection"]["us"], "winner_call": r["winner_call"]["selection"],
              "winner_confidence": r["winner_call"]["confidence"]}
             for r in rows if r["selection"] and r["selection"]["confidence"] == "High"]
    (D / "highs.json").write_text(json.dumps(highs, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"f71557b5 model: {doc['counts']['fixtures']} rows | {doc['counts']['priced']} priced | "
          f"{doc['counts']['prices']} prices | {doc['counts']['selections']} tips "
          f"({doc['counts']['high']} High / {doc['counts']['medium']} Medium / {doc['counts']['low']} Low) | "
          f"{doc['counts']['no_bet']} no-bet | {doc['counts']['rejected_highs']} rejected highs")
    print("HIGH picks:")
    for h in highs:
        print(f"  {h['id']:28s} {h['selection']:42s} {h['prob']:.4f} {h['price']:.2f} ({h['us']:+d})  [{h['market']}]")


if __name__ == "__main__":
    build()
