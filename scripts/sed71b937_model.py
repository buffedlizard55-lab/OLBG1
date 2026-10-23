#!/usr/bin/env python3
"""TED71 (session ed71b937-olbg1) - own line origination.

Two hard rules drive this file.

1.  **Inputs** (records, points for/against, start times) must have been read
    on an official page this session.  If they were not, the market is
    published as *unpriced* with the reason, never estimated from memory.

2.  **Constants** (shrinkage prior, margin spread, ladder rungs) are model
    parameters.  They are disclosed here and on the methodology page, and
    every number they produce is labelled an estimate.  A constant is not a
    sourced fact and is never presented as one.

The High tier is the brief's literal conjunction:

    model probability >= 0.700  AND  originated fair price inside -250..+10000

Because fair decimal is 1/p, that conjunction collapses to a 1.43-point-wide
probability window, p in [0.700, 0.71429].  See BAND_NOTE - it is published
on the site rather than hidden, because it is the reason the High tier is
small.
"""

from __future__ import annotations

import json
import math
import os

SESSION = "ed71b937-olbg1"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data", "ed71b937")

# --- disclosed model constants -------------------------------------------
SHRINK_ALPHA = 2          # Beta(2,2) prior on a win rate
SHRINK_BETA = 2
EL_MARGIN_SD = 18.0       # EuroLeague game-margin standard deviation, points
EL_TOTAL_LADDER = (-4.5, 0.0, 4.5)
EL_HANDICAP_RUNGS = (0.5, 2.5, 4.5, 6.5, 8.5)
NHL_MARGIN_SD = 1.45      # NHL game-margin standard deviation, goals
NHL_TOTAL_LADDER = (-0.5, 0.0, 0.5)
NHL_HANDICAP_RUNGS = (0.5, 1.5, 2.5)
MLB_MARGIN_SD = 1.30      # MLB game-margin standard deviation, runs
MLB_TOTAL_LADDER = (-0.5, 0.0, 0.5)
MLB_HANDICAP_RUNGS = (0.5, 1.5, 2.5)

BAND_MIN_AMERICAN = -250
BAND_MAX_AMERICAN = 10000
HIGH_PROB_FLOOR = 0.700

BAND_NOTE = (
    "Fair decimal price is 1/p with no margin.  A price of -250 is decimal "
    "1.400, which corresponds to p = 0.71429.  Therefore the brief's "
    "conjunction - probability at least 70% AND price no shorter than -250 - "
    "can only be satisfied inside the 1.43-point window p in [0.700, 0.71429]. "
    "Every selection above 0.71429 is a genuine 70%+ preference but is priced "
    "shorter than -250, so it is disclosed in the out-of-band ledger and is "
    "not promoted to High.  That is arithmetic, not caution."
)


# --- pricing primitives ---------------------------------------------------
def shrink(wins, games):
    """Beta(2,2)-shrunk win rate.  Overtime/shootout losses count as losses."""
    return (wins + SHRINK_ALPHA) / (games + SHRINK_ALPHA + SHRINK_BETA)


def log5(pa, pb):
    """Probability that side A beats side B from two independent win rates."""
    denom = pa + pb - 2.0 * pa * pb
    if denom <= 0:
        return None
    return (pa - pa * pb) / denom


def _norm_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def margin_probs(mu, sd):
    """Continuous margin model: P(margin > line) and P(total side)."""
    return mu, sd


def p_cover(mu, sd, line):
    """P(margin strictly greater than `line`) under N(mu, sd).

    Half-point lines never push, so no tie mass is needed.
    """
    return 1.0 - _norm_cdf((line - mu) / sd)


def decimal_to_american(dec):
    if dec is None:
        return None
    if dec <= 1.0:
        return None
    if dec >= 2.0:
        return int(round((dec - 1.0) * 100))
    return int(round(-100.0 / (dec - 1.0)))


def fair(p):
    """Zero-vig fair decimal and its American rendering."""
    if p is None or p <= 0 or p >= 1:
        return None, None
    dec = 1.0 / p
    return dec, decimal_to_american(dec)


def in_band(american):
    if american is None:
        return False
    return BAND_MIN_AMERICAN <= american <= BAND_MAX_AMERICAN


def band_position(p):
    """Where a probability sits relative to the High conjunction."""
    dec, ame = fair(p)
    if p is None:
        return "unpriced"
    if p >= HIGH_PROB_FLOOR and in_band(ame):
        return "high-in-band"
    if p >= HIGH_PROB_FLOOR and ame is not None and ame < BAND_MIN_AMERICAN:
        return "out-of-band-short"
    if p >= HIGH_PROB_FLOOR and ame is not None and ame > BAND_MAX_AMERICAN:
        return "out-of-band-long"
    if p >= 0.60:
        return "medium"
    return "low"


SELECTIONS = []


def _sel(fixture_id, sport, match, market, selection, p, inputs, model,
         note=None):
    dec, ame = fair(p)
    SELECTIONS.append({
        "fixture_id": fixture_id,
        "sport": sport,
        "match": match,
        "market": market,
        "selection": selection,
        "prob": None if p is None else round(p, 4),
        "fair_decimal": None if dec is None else round(dec, 4),
        "fair_american": ame,
        "tier": band_position(p),
        "inputs": inputs,
        "model": model,
        "note": note,
    })


def unpriced(fixture_id, sport, match, market, reason):
    SELECTIONS.append({
        "fixture_id": fixture_id, "sport": sport, "match": match,
        "market": market, "selection": None, "prob": None,
        "fair_decimal": None, "fair_american": None, "tier": "unpriced",
        "inputs": None, "model": None, "note": reason,
    })


def _wl(record):
    """'7-2-0' -> (7, 9); '4-2' -> (4, 6).  Binary: every non-win is a loss."""
    parts = [int(x) for x in record.split("-")]
    return parts[0], sum(parts)


def price_two_way(fid, sport, match, a_name, b_name, rec_a, rec_b,
                  inputs_src, mu=None, sd=None, cap=None):
    """Winner market from official records, plus a ladder when a margin model
    input exists."""
    wa, ga = _wl(rec_a)
    wb, gb = _wl(rec_b)
    pa_raw, pb_raw = wa / ga, wb / gb
    pa, pb = shrink(wa, ga), shrink(wb, gb)
    p_a = log5(pa, pb)
    p_b = None if p_a is None else 1.0 - p_a
    inputs = {
        "record_a": rec_a, "record_b": rec_b,
        "raw_win_pct_a": round(pa_raw, 4), "raw_win_pct_b": round(pb_raw, 4),
        "shrunk_a": round(pa, 4), "shrunk_b": round(pb, 4),
        "source": inputs_src,
    }
    model = "Beta({},{}) shrinkage + log5, no home-edge term".format(
        SHRINK_ALPHA, SHRINK_BETA)
    if cap:
        model += "; confidence capped to Low ({})".format(cap)
    for name, p in ((a_name, p_a), (b_name, p_b)):
        if p is None:
            continue
        tier = band_position(p)
        if cap and tier in ("high-in-band", "medium"):
            tier = "low"
        dec, ame = fair(p)
        SELECTIONS.append({
            "fixture_id": fid, "sport": sport, "match": match,
            "market": "Match winner", "selection": name,
            "prob": round(p, 4),
            "fair_decimal": None if dec is None else round(dec, 4),
            "fair_american": ame, "tier": tier,
            "inputs": inputs, "model": model, "note": None,
        })
    if mu is not None and sd:
        for rung in (0.5, 1.5, 2.5) if sport == "Ice Hockey" else (2.5, 4.5, 6.5):
            for side, sgn in ((a_name, 1.0), (b_name, -1.0)):
                line = sgn * rung if side == a_name else rung
                # A -rung covers when margin(A) > rung;
                # B +rung covers when margin(A) < -rung... expressed as
                # P(margin_A > rung) and P(margin_A < -rung).
                if side == a_name:
                    p = p_cover(mu, sd, rung)
                    mname = "{} -{} (handicap)".format(a_name, rung)
                else:
                    p = _norm_cdf((-rung - mu) / sd)
                    mname = "{} +{} (handicap)".format(b_name, rung)
                _sel(fid, sport, match, mname, side, p,
                     {"margin_mu": round(mu, 3), "margin_sd": sd},
                     "Normal margin model, disclosed SD constant")


def price_basketball(fid, match, a, b, rec_a, rec_b, pfa, pfpa, pfb, pfpb,
                     src):
    """EuroLeague: winner plus handicap and total ladders from official
    points for/against."""
    wa, ga = _wl(rec_a)
    wb, gb = _wl(rec_b)
    pa, pb = shrink(wa, ga), shrink(wb, gb)
    p_a = log5(pa, pb)
    p_b = 1.0 - p_a
    rating_a = (pfa - pfpa) / ga
    rating_b = (pfb - pfpb) / gb
    mu = rating_a - rating_b
    proj_total = (pfa / ga + pfb / gb + pfpa / ga + pfpb / gb) / 2.0
    inputs = {
        "record_a": rec_a, "record_b": rec_b,
        "points_for_against_a": [pfa, pfpa],
        "points_for_against_b": [pfb, pfpb],
        "rating_a": round(rating_a, 3), "rating_b": round(rating_b, 3),
        "margin_mu": round(mu, 3),
        "projected_total": round(proj_total, 2),
        "source": src,
    }
    for name, p in ((a, p_a), (b, p_b)):
        dec, ame = fair(p)
        SELECTIONS.append({
            "fixture_id": fid, "sport": "Basketball", "match": match,
            "market": "Match winner", "selection": name,
            "prob": round(p, 4), "fair_decimal": round(dec, 4),
            "fair_american": ame, "tier": band_position(p),
            "inputs": inputs,
            "model": "Beta({},{}) shrinkage + log5 on official W-L, no "
                     "home-edge term".format(SHRINK_ALPHA, SHRINK_BETA),
            "note": None,
        })
    for rung in EL_HANDICAP_RUNGS:
        # margin_A = score(A) - score(B).  All four rungs of a two-way
        # handicap book are published, and each label is checked against the
        # inequality it actually settles:
        #   A -h settles when margin_A >  h
        #   A +h settles when margin_A > -h
        #   B -h settles when margin_A < -h
        #   B +h settles when margin_A <  h
        ladder = (
            ("Handicap {} -{}".format(a, rung), a, p_cover(mu, EL_MARGIN_SD, rung)),
            ("Handicap {} +{}".format(a, rung), a, p_cover(mu, EL_MARGIN_SD, -rung)),
            ("Handicap {} -{}".format(b, rung), b,
             _norm_cdf((-rung - mu) / EL_MARGIN_SD)),
            ("Handicap {} +{}".format(b, rung), b,
             _norm_cdf((rung - mu) / EL_MARGIN_SD)),
        )
        for mname, side, p in ladder:
            _sel(fid, "Basketball", match, mname, side, p,
                 {"margin_mu": round(mu, 3), "margin_sd": EL_MARGIN_SD,
                  "rung": rung},
                 "Normal margin model; SD is a disclosed model constant, not "
                 "a sourced fact")
    for off in EL_TOTAL_LADDER:
        line = round((proj_total + off) * 2) / 2.0
        half = 0.5 if abs(line % 1) == 0.5 else 0.0
        # Total ladder needs a total-variance constant that was NOT read from
        # an official source, so the line is published but left unpriced.
        unpriced(fid, "Basketball", match,
                 "Match total {} {} (line {})".format(
                     "over" if off < 0 else "under", abs(off), line),
                 "Projected total {} is derived from official points "
                 "for/against, but no official total-variance input was read "
                 "this session, so no probability is attached.  Published as "
                 "a line, not a priced selection.".format(
                     round(proj_total, 2)))


def run():
    with open(os.path.join(DATA, "fixtures.json"), encoding="utf-8") as fh:
        fx = json.load(fh)

    def find(pred):
        return [r for r in fx["rows"] if r["official"] and pred(r["official"])]

    nhl = find(lambda o: o.get("competition", "").startswith("NHL 2026-27"))
    ws = find(lambda o: "World Series" in o.get("competition", ""))
    el = find(lambda o: "EuroLeague" in o.get("competition", ""))
    assert len(nhl) == 2, len(nhl)
    assert len(ws) == 1, len(ws)
    assert len(el) == 3, len(el)

    # ---- NHL: two games, official records read on nhl.com ----------------
    for r in nhl:
        off = r["official"]
        match = "{} v {}".format(off["away"], off["home"])
        price_two_way(
            r["id"], "Ice Hockey", match, off["away"], off["home"],
            off["record_away"], off["record_home"],
            inputs_src=off["sources"],
        )
        for mkt, reason in (
            ("Puck line (handicap)",
             "No official goals for/against input was read this session for "
             "these two clubs, so the margin model has no sourced input and "
             "the market is left unpriced."),
            ("Game total",
             "No official goals for/against input was read this session, so "
             "no total is originated."),
        ):
            unpriced(r["id"], "Ice Hockey", match, mkt, reason)

    # ---- MLB World Series G1: priced, but postseason-capped to Low -------
    off = ws[0]["official"]
    match = "{} v {}".format(off["away"], off["home"])
    price_two_way(
        ws[0]["id"], "Baseball", match, off["away"], off["home"],
        off["record_away"], off["record_home"],
        inputs_src=off["sources"],
        cap="postseason effects, starting pitchers, ballpark and lineups are "
            "not modelled; the disclosed policy caps any World Series game at "
            "Low regardless of the record-based number",
    )
    for mkt in ("Run line (handicap)", "Game total"):
        unpriced(ws[0]["id"], "Baseball", match, mkt,
                 "Paired official regular-season run rates were not read this "
                 "session, so no Poisson score model is run and the market is "
                 "left unpriced.")

    # ---- EuroLeague round 7: official W-L plus points for/against --------
    for r in el:
        off = r["official"]
        price_basketball(
            r["id"], "{} v {}".format(off["away"], off["home"]),
            off["away"], off["home"],
            off["record_away"], off["record_home"],
            off["pf_pa_away"][0], off["pf_pa_away"][1],
            off["pf_pa_home"][0], off["pf_pa_home"][1],
            off["sources"],
        )

    return SELECTIONS


def summary(sels=None):
    sels = sels if sels is not None else SELECTIONS
    tiers = {}
    for s in sels:
        tiers[s["tier"]] = tiers.get(s["tier"], 0) + 1
    priced = [s for s in sels if s["prob"] is not None]
    return {
        "selections": len(sels),
        "priced": len(priced),
        "unpriced": len(sels) - len(priced),
        "tiers": tiers,
        "high": [s for s in sels if s["tier"] == "high-in-band"],
        "out_of_band_short": [s for s in sels
                              if s["tier"] == "out-of-band-short"],
    }


def build():
    sels = run()
    out = {
        "session": SESSION, "task": "TED71",
        "generated_at": "2026-10-23T16:55:00Z",
        "band": {"min_american": BAND_MIN_AMERICAN,
                 "max_american": BAND_MAX_AMERICAN,
                 "prob_floor": HIGH_PROB_FLOOR,
                 "note": BAND_NOTE},
        "constants": {
            "shrinkage_prior": "Beta({},{})".format(SHRINK_ALPHA, SHRINK_BETA),
            "link": "log5",
            "home_edge": "none applied",
            "el_margin_sd_points": EL_MARGIN_SD,
            "el_handicap_rungs": list(EL_HANDICAP_RUNGS),
            "el_total_ladder_offsets": list(EL_TOTAL_LADDER),
        },
        "selections": sels,
        "counts": {k: v for k, v in summary(sels).items()
                   if k not in ("high", "out_of_band_short")},
    }
    with open(os.path.join(DATA, "lines.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return out


if __name__ == "__main__":
    o = build()
    s = summary(o["selections"])
    print("selections", s["selections"], "priced", s["priced"],
          "unpriced", s["unpriced"])
    print("tiers", json.dumps(s["tiers"]))
    print("HIGH:", json.dumps(s["high"], indent=1))
    print("OUT-OF-BAND-SHORT (>=70% but shorter than -250):")
    for x in s["out_of_band_short"]:
        print("  ", x["match"], "|", x["selection"], x["prob"],
              x["fair_american"])
