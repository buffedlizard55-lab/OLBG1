#!/usr/bin/env python3
"""Session efe12010 — originated pricing engine.

Everything here is our own line, derived only from the officially sourced inputs in
``sefe12010_data``.  No price is copied from a bookmaker, and no input is invented:
if a required official number is missing the market is emitted as an explicit
"unpriced / unverified" exception rather than filled in.

Confidence policy (restated on the published methodology page)
--------------------------------------------------------------
* Eligible price band : fair American price in [-250, +10000]
                        <=> 0.009901 <= p <= 0.714286
* High-A              : p >= 0.70 and inside the band
* High-B              : 0.62 <= p < 0.70 and inside the band
* Medium              : 0.50 <= p < 0.62, or p > 0.714286 (price-capped out of the band)
* Low                 : everything else, or any fixture without two officially
                        sourced ratings
"""
from __future__ import annotations

import math
from typing import Iterable

BAND_MIN_AMERICAN = -250
BAND_MAX_AMERICAN = 10000
BAND_P_MAX = 100.0 / (100.0 + 250.0 / 1.0) if False else 250.0 / 350.0  # 0.7142857
BAND_P_MIN = 100.0 / (100.0 + 10000.0)                                   # 0.0099010
HIGH_A_FLOOR = 0.70
HIGH_B_FLOOR = 0.62

MARGIN_TWO_WAY = 0.045
MARGIN_THREE_WAY = 0.060
MARGIN_OUTRIGHT = 0.080


# --------------------------------------------------------------------------- odds
def american(dec: float) -> int:
    if dec >= 2.0:
        return int(round((dec - 1.0) * 100.0))
    return -int(round(100.0 / (dec - 1.0)))


def fmt_american(dec: float) -> str:
    a = american(dec)
    return f"+{a}" if a > 0 else str(a)


def in_band(p: float) -> bool:
    return BAND_P_MIN <= p <= BAND_P_MAX


def confidence_for(p: float, rated: bool) -> str:
    if not rated:
        return "low"
    if in_band(p) and p >= HIGH_A_FLOOR:
        return "high"
    if in_band(p) and p >= HIGH_B_FLOOR:
        return "high"
    if p >= 0.50:
        return "medium"
    return "low"


def tier_for(p: float, rated: bool) -> str:
    if not rated:
        return "Unrated"
    if in_band(p) and p >= HIGH_A_FLOOR:
        return "High-A"
    if in_band(p) and p >= HIGH_B_FLOOR:
        return "High-B"
    if p > BAND_P_MAX:
        return "Medium (price-capped)"
    if p >= 0.50:
        return "Medium"
    return "Low"


def market(key: str, label: str, probs: list[tuple[str, float]], margin: float,
           note: str = "", normalise: bool = True) -> dict:
    """Build a priced market.

    ``normalise=False`` is used for multiple-selection markets (podium, points
    finish) where several selections can win at once and the column therefore
    does not and must not sum to 1.
    """
    total = sum(p for _, p in probs) if normalise else 1.0
    outcomes = []
    for selection, p in probs:
        p = p / total
        p = min(max(p, 1e-6), 1 - 1e-6)
        fair = 1.0 / p
        quoted = 1.0 / (p * (1.0 + margin))
        outcomes.append({
            "selection": selection,
            "probability": round(p, 6),
            "fair_odds": round(fair, 4),
            "fair_american": fmt_american(fair),
            "odds": round(quoted, 4),
            "american": fmt_american(quoted),
            "in_band": in_band(p),
        })
    return {
        "key": key,
        "label": label,
        "margin_pct": round(margin * 100.0, 2),
        "book_pct": round((1.0 + margin) * 100.0, 2),
        "exclusive": normalise,
        "note": note,
        "outcomes": outcomes,
    }


# ------------------------------------------------------------------- distributions
def log5(a: float, b: float) -> float:
    """Probability that a rating-`a` side beats a rating-`b` side."""
    num = a - a * b
    den = a + b - 2.0 * a * b
    return num / den if den else 0.5


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def poisson_over(line: float, lam: float, cap: int = 40) -> float:
    """P(total > line) for a Poisson total with mean `lam`; line is a half-number."""
    floor = int(math.floor(line))
    cdf = sum(poisson_pmf(k, lam) for k in range(0, floor + 1))
    return max(min(1.0 - cdf, 1 - 1e-6), 1e-6)


def skellam_cover(mu_a: float, mu_b: float, handicap: float, cap: int = 18) -> float:
    """P(A - B > handicap) for independent Poisson goal counts."""
    total = 0.0
    for a in range(cap + 1):
        pa = poisson_pmf(a, mu_a)
        if pa < 1e-12:
            continue
        for b in range(cap + 1):
            if a - b > handicap:
                total += pa * poisson_pmf(b, mu_b)
    return max(min(total, 1 - 1e-6), 1e-6)


def first_to(target: int, q: float) -> float:
    """P(win a race to `target` frames) when each frame is won with probability q."""
    total = 0.0
    for lost in range(0, target):
        total += math.comb(target - 1 + lost, lost) * (q ** target) * ((1 - q) ** lost)
    return max(min(total, 1 - 1e-6), 1e-6)


def set_prob_from_match(p_match: float) -> float:
    """Invert best-of-three match probability to a per-set probability."""
    lo, hi = 1e-4, 1 - 1e-4
    for _ in range(80):
        mid = (lo + hi) / 2.0
        val = mid * mid * (1.0 + 2.0 * (1.0 - mid))
        if val < p_match:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def harville_top_n(probs: dict[str, float], n: int) -> dict[str, float]:
    """Probability of a top-`n` finish from win probabilities (Harville, sampling w/o
    replacement).  Monte-Carlo-free closed enumeration for small fields."""
    names = list(probs)
    out = {name: 0.0 for name in names}

    def recurse(remaining: dict[str, float], depth: int, prob: float, chosen: list[str]) -> None:
        if depth == n:
            for name in chosen:
                out[name] += prob
            return
        total = sum(remaining.values())
        if total <= 0:
            return
        for name, weight in list(remaining.items()):
            nxt = dict(remaining)
            del nxt[name]
            recurse(nxt, depth + 1, prob * weight / total, chosen + [name])

    recurse(dict(probs), 0, 1.0, [])
    return out


# ------------------------------------------------------------------------- helpers
def headline_selection(markets: Iterable[dict]) -> tuple[dict, dict] | tuple[None, None]:
    """The selection the desk actually publishes for a fixture.

    Rule: use the straight winner-market favourite whenever it is inside the
    published price band and already clears the High floor.  Only when the
    favourite is too short to quote (shorter than -250) or too weak to be a High
    does the desk fall back to the strongest in-band derivative, so a sensible
    match-winner is never displaced by a lopsided side market.
    """
    wm, wo = winner_favourite(markets)
    if wo is not None and wo["in_band"] and wo["probability"] >= HIGH_B_FLOOR:
        return wm, wo
    bm, bo = best_band_outcome(markets)
    if bo is None:
        return wm, wo
    if wo is not None and wo["in_band"] and wo["probability"] >= bo["probability"]:
        return wm, wo
    return bm, bo


def best_band_outcome(markets: Iterable[dict]) -> tuple[dict, dict] | tuple[None, None]:
    """Highest-probability outcome that sits inside the published price band."""
    best_m, best_o = None, None
    for m in markets:
        for o in m["outcomes"]:
            if not o["in_band"]:
                continue
            if best_o is None or o["probability"] > best_o["probability"]:
                best_m, best_o = m, o
    return best_m, best_o


def winner_favourite(markets: Iterable[dict]) -> tuple[dict, dict] | tuple[None, None]:
    for m in markets:
        if m["key"] == "winner":
            best = max(m["outcomes"], key=lambda o: o["probability"])
            return m, best
    return None, None
