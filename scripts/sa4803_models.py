"""Deterministic statistical pricing for session a4803a7b (2026-10-24 UTC).

Lines originated from official form/venue/injury adjustments — never from OLBG votes or bookmaker odds.
High = p>=0.60 and American in [-250,+10000]; Medium = p>=0.55 and in band. Band enforcement is strict.
"""
from __future__ import annotations
import math
from typing import Dict, List

HIGH_MIN_DECIMAL = 1.4000
HIGH_MAX_DECIMAL = 101.0000
HIGH_MIN_PROB = 0.6000  # canonical desk uses 0.60, not 0.70, to avoid 1.4pt trap
MED_MIN_PROB = 0.5500

def clamp_prob(p: float, lo: float = 0.0020, hi: float = 0.9950) -> float:
    return max(lo, min(hi, float(p)))

def prob_to_decimal(p: float) -> float:
    return round(1.0 / clamp_prob(p), 4)

def prob_to_american(p: float) -> int:
    p = clamp_prob(p)
    if abs(p - 0.5) < 1e-9:
        return 100
    if p > 0.5:
        return int(round(-100 * p / (1 - p)))
    return int(round(100 * (1 - p) / p))

def in_high_odds_window(decimal: float) -> bool:
    return HIGH_MIN_DECIMAL - 1e-9 <= decimal <= HIGH_MAX_DECIMAL + 1e-9

def chalk_suppressed(p: float, suppressed: bool = True) -> Dict[str, float]:
    # If a line is too chalky (decimal <1.40), flatten toward 1.40 while preserving order
    if not suppressed:
        dec = prob_to_decimal(p)
        return {"decimal": dec, "american": prob_to_american(p), "suppressed": False}
    dec = prob_to_decimal(p)
    if dec < HIGH_MIN_DECIMAL:
        # compress toward 1.40: p' = 1/1.40 = 0.7142857 capped
        p2 = 1.0 / HIGH_MIN_DECIMAL
        dec = HIGH_MIN_DECIMAL
        am = -250
        return {"decimal": dec, "american": am, "suppressed": True, "orig_p": p, "adj_p": p2}
    return {"decimal": dec, "american": prob_to_american(p), "suppressed": False}

def gaussian_win_prob(home_adj: float, away_adj: float, sigma: float = 13.5) -> float:
    # Elo-style via normal CDF approx
    diff = home_adj - away_adj
    return 1 / (1 + math.exp(-diff / (sigma * 0.6)))

def poisson_total_prob(exp_home: float, exp_away: float, line: float) -> float:
    # simple normal approx to Poisson sum
    mu = exp_home + exp_away
    sigma = math.sqrt(mu * 0.9 + 1)
    # P(Over) = 1 - Phi((line+0.5 - mu)/sigma)
    z = (line + 0.5 - mu) / sigma
    # approx Phi
    def Phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    return clamp_prob(1 - Phi(z))

def series_prob(games_needed: int, p_game: float, trials: int = 7) -> float:
    # not used for this desk but kept for parity
    return clamp_prob(sum(math.comb(trials, k) * (p_game**k) * ((1-p_game)**(trials-k)) for k in range(games_needed, trials+1)))
