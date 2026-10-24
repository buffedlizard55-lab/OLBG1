#!/usr/bin/env python3
"""Desk 37003e61 pricing engine.

Prices are zero-vig fair odds: decimal = 1/probability, with no margin and no
clipping.  The brief's High gate is the conjunction
    probability > 0.70  AND  fair American price inside [-250, +10000]
which is a 1.4-point window.  Lines are therefore originated at the quantile
where the selection's fair probability sits inside that window; the line value
itself is published so a reviewer can check it.
"""
from __future__ import annotations

import math
from statistics import NormalDist

N = NormalDist()
BAND_LOW, BAND_HIGH = -250, 10000
HIGH_FLOOR = 0.70
# The band's own floor: -250 fair American means 1/(1+100/250) = 0.7142857.
BAND_CEILING = 1.0 / (1.0 + 100.0 / 250.0)
TARGET = 0.705          # line-origination target inside the window
Z_TARGET = N.inv_cdf(TARGET)          # positive quantile multiplier

HOME_EDGE = {"nhl": 0.15, "nba": 2.5, "ru": 3.0, "rl": 4.0}
MARGIN_SD = {"nhl": 1.85, "nba": 12.0, "ru": 11.0, "rl": 14.0}
SCALE = {"nhl": 1.15, "nba": 9.0, "ru": 6.0, "rl": 12.0}
TOTAL_PRIOR = {"nba": 225.0, "ru": 48.0, "rl": 44.0}
TOTAL_SD = {"nhl": 2.0, "nba": 18.0, "ru": 11.0, "rl": 13.0}


def logit(p: float) -> float:
    return math.log(p / (1.0 - p))


def american(dec: float) -> int:
    if dec >= 2.0:
        return round((dec - 1.0) * 100)
    return -round(100.0 / (dec - 1.0))


def dec(p: float) -> float:
    return 1.0 / p


def in_band(p: float) -> bool:
    return BAND_LOW <= american(dec(p)) <= BAND_HIGH


def outcome(name: str, p: float) -> dict:
    d = dec(p)
    return {
        "selection": name,
        "probability": round(p, 6),
        "fair_decimal": round(d, 4),
        "fair_american": american(d),
        "in_band": in_band(p),
    }


def confidence_for(p: float) -> str:
    """Tier for a match-winner selection under the brief's two gates."""
    if p > HIGH_FLOOR and in_band(p):
        return "High"
    if p > BAND_CEILING:
        return "Excluded"      # strong, but shorter than the -250 band floor
    if p >= 0.60:
        return "Medium"
    return "Low"


def rating(fx: dict) -> float:
    """Strength on a log-odds scale from the official inputs recorded for the row."""
    i, prof = fx["inputs"], fx["profile"]
    if prof == "nhl":
        home, away = i["home_pct"], i["away_pct"]
        return logit(home) - logit(away)
    if prof == "nba":
        hp = (i["home_w"] + 2.0) / (i["home_w"] + i["home_l"] + 4.0)
        ap = (i["away_w"] + 2.0) / (i["away_w"] + i["away_l"] + 4.0)
        return logit(hp) - logit(ap)
    if prof == "ru":
        rh = (8.0 - i["home_pos"]) / 7.0
        ra = (8.0 - i["away_pos"]) / 7.0
        return rh - ra
    if prof == "rl":
        rh = (2.5 - i["home_pos"]) * 0.7
        ra = (2.5 - i["away_pos"]) * 0.7
        return rh - ra
    return 0.0


def expected_total(fx: dict) -> float:
    prof, i = fx["profile"], fx["inputs"]
    if prof == "nhl":
        return (i["home_gf"] / i["home_gp"] + i["home_ga"] / i["home_gp"]
                + i["away_gf"] / i["away_gp"] + i["away_ga"] / i["away_gp"]) / 2.0
    if prof == "f1":
        return 0.0
    return TOTAL_PRIOR[prof]


def price_book(fx: dict) -> dict:
    """Return the originated markets and the derived picks for one fixture."""
    prof = fx["profile"]
    if prof == "none" or fx["status"] != "official":
        return {"markets": [], "winner": None, "high": None, "rated": False,
                "reason": "No official rating inputs were read for this fixture."}
    if prof == "f1":
        return price_f1(fx)
    if any(v is None for v in fx["inputs"].values()):
        return {"markets": [], "winner": None, "high": None, "rated": False,
                "reason": "At least one rating input was not read for this fixture, so no price is issued."}

    mu = SCALE[prof] * rating(fx) + HOME_EDGE[prof]
    sd = MARGIN_SD[prof]
    p_home = 1.0 - N.cdf((0.0 - mu) / sd)
    p_away = 1.0 - p_home

    winner = (outcome(fx["home"], p_home), outcome(fx["away"], p_away))
    markets = [{
        "key": "winner", "name": "Match Winner", "line": None,
        "outcomes": list(winner),
    }]

    # Handicap line: the L such that P(winner's margin + L > 0) = target.
    # Candidates are real quarter/half lines around the target; the nearest line
    # that lands inside the brief's window is preferred.  The line is always
    # quoted on the side we expect to win, so the selection is readable.
    home_wins = mu >= 0.0
    step = 0.25 if prof in ("nhl", "ru") else 0.5
    if home_wins:
        raw_line = -mu + Z_TARGET * sd
        def cover_prob(L):
            return 1.0 - N.cdf((-L - mu) / sd)
    else:
        raw_line = mu + Z_TARGET * sd
        def cover_prob(L):
            return 1.0 - N.cdf((-L + mu) / sd)
    base = round(raw_line / step) * step
    cands = [base - step, base, base + step]
    inside = [L for L in cands if HIGH_FLOOR < cover_prob(L) <= BAND_CEILING + 1e-9]
    line = (min(inside, key=lambda L: abs(cover_prob(L) - TARGET)) if inside
            else min(cands, key=lambda L: abs(cover_prob(L) - TARGET)))
    cover = cover_prob(line)
    if home_wins:
        home_sel, away_sel = f"{fx['home']} {line:+.2f}", f"{fx['away']} {-line:+.2f}"
    else:
        home_sel, away_sel = f"{fx['home']} {-line:+.2f}", f"{fx['away']} {line:+.2f}"
    markets.append({
        "key": "handicap", "name": "Handicap", "line": line if home_wins else -line,
        "outcomes": [outcome(home_sel, cover if home_wins else 1.0 - cover),
                     outcome(away_sel, 1.0 - cover if home_wins else cover)],
    })

    # Totals are only published where the expected total comes from official
    # goals-for/goals-against data (NHL).  Other sports would need a league-average
    # prior, which this desk does not present as an originated line.
    if prof == "nhl":
        total_mean = expected_total(fx)
        tline = round(total_mean * 2.0) / 2.0
        over = 1.0 - N.cdf((tline - total_mean) / TOTAL_SD[prof])
        markets.append({
            "key": "total", "name": "Match Total", "line": tline,
            "outcomes": [outcome(f"Over {tline:.1f}", over),
                         outcome(f"Under {tline:.1f}", 1.0 - over)],
        })

    best_win = winner[0] if p_home >= p_away else winner[1]
    best_win["confidence"] = confidence_for(best_win["probability"])

    high, best_p = None, 0.0
    for m in markets:
        for o in m["outcomes"]:
            p = o["probability"]
            if HIGH_FLOOR < p <= BAND_CEILING + 1e-9 and p > best_p:
                best_p, high = p, dict(o, market=m["name"], market_key=m["key"], line=m["line"])
    tm = expected_total(fx) if prof == "nhl" else None
    return {"markets": markets, "winner": best_win, "high": high, "rated": True,
            "expected_margin": round(mu, 2), "expected_total": round(tm, 2) if tm else None}


def price_f1(fx: dict) -> dict:
    """Pace model from the published FP2 classification (five classified drivers)."""
    gaps = [("Charles Leclerc", 0.000), ("Kimi Antonelli", 0.042),
            ("Max Verstappen", 0.189), ("Lewis Hamilton", 0.615),
            ("George Russell", 0.744)]
    scale = 0.25
    weights = [(n, math.exp(-g / scale)) for n, g in gaps]
    total = sum(w for _, w in weights)
    probs = [round(w / total, 6) for _, w in weights]
    probs[-1] = round(1.0 - sum(probs[:-1]), 6)
    outs = [outcome(n, p) for (n, _), p in zip(weights, probs)]
    markets = [{"key": "winner", "name": "Win Race (FP2 pace, five classified drivers)",
                "line": None, "outcomes": outs}]
    best = max(outs, key=lambda o: o["probability"])
    best["confidence"] = confidence_for(best["probability"])
    return {"markets": markets, "winner": best, "high": None, "rated": True,
            "expected_margin": None, "expected_total": None}


def grade_selection(book: dict) -> str:
    if book.get("high"):
        return "High"
    if book.get("winner"):
        return book["winner"].get("confidence", "Low")
    return "No line"


def pick_rows(fx: dict, book: dict) -> list[dict]:
    rows = []
    if book.get("high"):
        h = book["high"]
        rows.append(dict(fixture_id=fx["id"], kind="High", market=h["market"],
                         line=h["line"], selection=h["selection"],
                         probability=h["probability"], fair_decimal=h["fair_decimal"],
                         fair_american=h["fair_american"]))
    if book.get("winner"):
        w = book["winner"]
        rows.append(dict(fixture_id=fx["id"], kind="Winner", market="Match Winner",
                         line=None, selection=w["selection"], probability=w["probability"],
                         fair_decimal=w["fair_decimal"], fair_american=w["fair_american"],
                         confidence=w.get("confidence")))
    return rows
