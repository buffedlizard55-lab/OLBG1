#!/usr/bin/env python3
"""TC3026353 — zero-vig multi-market line origination engine (session c3026353-olbg1).

Pure mathematics only. No network. Every price this module emits is a MODEL
ESTIMATE (our own originated line), never a sourced fact and never a bookmaker
quote. Fair decimal = 1/p (no margin). American display derived consistently.

Confidence gate (the brief's conjunction):
  High   = p > 0.70 AND fair American inside [-250, +10000] AND official evidence
           (evidence checked by the desk scripts, not here)
  Medium = 0.55 <= p <= 0.70, OR p > 0.70 whose fair price sits SHORTER than
           -250 (chalk cap, disclosed) — never High on probability alone
  Low    = p < 0.55

The arithmetic consequence is published honestly: p>0.70 forces a fair price of
-233.33 or shorter, so an in-window High sits in the narrow [-250, -233.33] band.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

FLOOR_AMERICAN = -250.0
CEIL_AMERICAN = 10000.0
P_HIGH = 0.70
P_MEDIUM = 0.55


def clamp(p: float, lo: float = 1e-4, hi: float = 1 - 1e-4) -> float:
    return max(lo, min(hi, p))


def dec_to_american(dec: float) -> float:
    if dec <= 1.0:
        return float("inf")
    if dec >= 2.0:
        return (dec - 1.0) * 100.0
    return -100.0 / (dec - 1.0)


def american_to_dec(american: float) -> float:
    if american >= 0:
        return 1.0 + american / 100.0
    return 1.0 + 100.0 / abs(american)


def american_to_p(american: float) -> float:
    """Raw (vigged) implied probability of a US price."""
    return 1.0 / american_to_dec(american)


def p_to_american(p: float) -> float:
    p = clamp(p)
    return dec_to_american(1.0 / p)


def zero_vig_pair(p_a: float, p_b: float) -> Tuple[float, float]:
    s = p_a + p_b
    if s <= 0:
        return 0.5, 0.5
    return p_a / s, p_b / s


def devig_two_way(a: float, b: float) -> Tuple[float, float]:
    """Devig a two-way market from US (or decimal-detected) prices."""
    pa, pb = american_to_p(a), american_to_p(b)
    return zero_vig_pair(pa, pb)


def tier(p: float, american: float, evidence: bool) -> str:
    in_window = (FLOOR_AMERICAN - 1e-6 <= american <= CEIL_AMERICAN + 1e-6)
    if p > P_HIGH and in_window and evidence:
        return "High"
    if p > P_HIGH and american < FLOOR_AMERICAN - 1e-6:
        return "Medium (chalk cap)" if evidence else "Low (evidence gap)"
    if p > P_HIGH:
        return "Medium (evidence gap)"
    if p >= P_MEDIUM:
        return "Medium" if evidence else "Medium (evidence gap)"
    return "Low" if evidence else "Low (evidence gap)"


# ---------------------------------------------------------------------------
# Sport-specific expectation engines. Each returns a probability that side A
# (first-listed participant) wins the match. Inputs come from the desk data
# file and are documented per fixture; nothing here reaches the network.
# ---------------------------------------------------------------------------

def _elo(p_a: float, p_b: float, ha: float = 0.0) -> float:
    """Logistic from two strength scores on the desk's declared 0-10-ish scale.

    Scale s = 1.0: one strength point is one e-fold. The data file documents the
    per-fixture rubric (league leader ~1.7-2.0, mid-table ~1.0-1.4, struggling or
    qualifier ~0.6-1.0). `ha` is an optional venue term when the first-listed
    side is at home; 0.0 for neutral or host-unknown rows.
    """
    d = (p_a + ha) - p_b
    return clamp(1.0 / (1.0 + math.exp(-d)))


def _log5(pa: float, pb: float) -> float:
    """Bill James log5 for two win-percentages."""
    pa, pb = clamp(pa, 0.02, 0.98), clamp(pb, 0.02, 0.98)
    num = pa * (1 - pb)
    den = num + pb * (1 - pa)
    return clamp(num / den)


def _best_of_n(pa_frame: float, n: int) -> float:
    """P(A wins a best-of-n contest) from per-frame edge."""
    need = n // 2 + 1
    pa_frame = clamp(pa_frame, 0.02, 0.98)
    pb_frame = 1 - pa_frame
    total = 0.0
    for k in range(need):
        total += math.comb(need - 1 + k, k) * (pa_frame ** need) * (pb_frame ** k)
    return clamp(total)


def _gaussian_margin(mu: float, sigma: float) -> float:
    """P(margin > 0) for margin ~ N(mu, sigma)."""
    return clamp(0.5 * (1.0 + math.erf(mu / (sigma * math.sqrt(2.0)))))


def _poisson_total(lam_a: float, lam_b: float, line: float) -> Tuple[float, float]:
    """P(total goals/runs/points > line) and <= line for independent Poissons."""
    lam = lam_a + lam_b
    over = 0.0
    k = 0
    while True:
        p = math.exp(-lam) * (lam ** k) / math.factorial(k)
        if k > line:
            over += p
        if p < 1e-10 and k > lam + 40:
            break
        k += 1
        if k > 200:
            break
    return clamp(over), clamp(1 - over)


def winner_two_way(inputs: Dict) -> Tuple[float, float]:
    """Dispatch by engine tag in the fixture inputs dict."""
    kind = inputs.get("kind", "elo")
    if kind == "log5":
        return _log5(inputs["a"], inputs["b"]), _log5(inputs["b"], inputs["a"])
    if kind == "elo":
        return _elo(inputs["a"], inputs["b"], inputs.get("home", 0.0)), 0.0
    if kind == "best_of_n":
        pa = _best_of_n(inputs["frame_a"], int(inputs["n"]))
        return pa, 1 - pa
    if kind == "gauss":
        mu, sigma = inputs["mu"], inputs.get("sigma", 12.0)
        pa = _gaussian_margin(mu, sigma)
        return pa, 1 - pa
    if kind == "poisson":
        lam_a, lam_b = inputs["lam_a"], inputs["lam_b"]
        # win prob from Skellam difference
        mu = lam_a - lam_b
        sigma = math.sqrt(lam_a + lam_b)
        pa = _gaussian_margin(mu, max(sigma, 0.5))
        return pa, 1 - pa
    if kind == "field":
        # tournament field: list of (name, strength) — output normalised probs
        raise ValueError("use field_win_probs for field markets")
    raise ValueError(f"unknown engine kind {kind!r}")


def field_win_probs(entries: List[Tuple[str, float]]) -> Dict[str, float]:
    """Normalise declared weights for outright/field markets.

    Entries are (name, weight) with weights summing to any positive total;
    probabilities are w_i / sum(w). Weights are model priors (e.g. from verified
    season win counts or live leaderboard positions) — never copied prices.
    """
    if not entries:
        return {}
    z = sum(w for _, w in entries)
    if z <= 0:
        n = len(entries)
        return {name: 1.0 / n for name, _ in entries}
    return {name: clamp(w / z, 1e-4, 1 - 1e-4) for name, w in entries}


def spread_pair(p_a: float, mu_margin: float, line: float, sigma: float) -> Tuple[float, float]:
    """Two-way handicap: A covers -line, B covers +line (pushes excluded)."""
    p_cov_a = _gaussian_margin(mu_margin - line, sigma)
    return p_cov_a, 1 - p_cov_a


def totals_pair(lam_a: float, lam_b: float, line: float) -> Tuple[float, float]:
    return _poisson_total(lam_a, lam_b, line)


def describe(p_a: float, name_a: str, name_b: str) -> Dict[str, float]:
    american_a = p_to_american(p_a)
    american_b = p_to_american(1 - p_a)
    return {
        "p_a": round(p_a, 4),
        "p_b": round(1 - p_a, 4),
        "dec_a": round(1 / p_a, 3),
        "dec_b": round(1 / (1 - p_a), 3),
        "american_a": round(american_a, 0),
        "american_b": round(american_b, 0),
        "pick": name_a if p_a >= 0.5 else name_b,
        "pick_p": round(max(p_a, 1 - p_a), 4),
        "pick_american": round(american_a if p_a >= 0.5 else american_b, 0),
    }
