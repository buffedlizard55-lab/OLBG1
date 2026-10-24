"""Experimental price origination for the 9e041d28 desk.

Every function here is deterministic and documented so that a reader can redo the
arithmetic. No function invents an input: if a required number is missing the
caller must pass ``None`` and the market is withheld instead of being filled in.

Methods
-------
log5          Bill James' two-team estimator. For a match between A and B we use
              the venue-split rates (home team's home win rate, away team's away
              win rate) rather than overall rates, so the venue effect is inside
              the input rather than an invented constant.
Poisson       Independent run/goal counts; ties are broken by the caller's
              documented rule (baseball: renormalise on "no tie"; hockey: a tie
              after 60 minutes is renormalised as a 50/50 overtime/shootout).
Skellam       Difference of two independent Poisson counts, used for handicaps.
Prices        Zero-vig fair decimal = 1/p, American derived from that decimal.
              No margin, no staking advice, no claim that a bookmaker offers it.
"""
from __future__ import annotations

import math
from typing import Iterable

MAX_GOALS = 25


def log5(rate_a: float, rate_b: float) -> float:
    """Probability that A beats B from two win rates."""
    if rate_a is None or rate_b is None:
        raise ValueError("log5 requires both rates")
    num = rate_a * (1 - rate_b)
    den = num + rate_b * (1 - rate_a)
    if den == 0:
        raise ValueError("degenerate log5 inputs")
    return num / den


def decimal_from_prob(p: float) -> float:
    return 1.0 / p


def american_from_prob(p: float) -> int:
    if p <= 0 or p >= 1:
        raise ValueError("probability must be strictly between 0 and 1")
    if p >= 0.5:
        return int(round(-100 * p / (1 - p)))
    return int(round(100 * (1 - p) / p))


def prob_from_american(a: int) -> float:
    if a < 0:
        return (-a) / (-a + 100)
    return 100 / (a + 100)


def in_price_band(p: float, low: int = -250, high: int = 10000) -> bool:
    a = american_from_prob(p)
    return low <= a <= high


def poisson_pmf(lam: float, k: int) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def poisson_grid(lam_home: float, lam_away: float) -> list[list[float]]:
    grid = []
    for h in range(MAX_GOALS + 1):
        row = [poisson_pmf(lam_home, h) * poisson_pmf(lam_away, a) for a in range(MAX_GOALS + 1)]
        grid.append(row)
    total = sum(sum(r) for r in grid)
    return [[c / total for c in r] for r in grid]


def two_way_from_grid(grid: list[list[float]], keep) -> float:
    """Renormalise a score grid onto a two-way market.

    ``keep(home, away)`` returns True for outcomes that settle the first named
    side. The complement is everything else, so the pair always sums to one.
    """
    hit = 0.0
    for h, row in enumerate(grid):
        for a, p in enumerate(row):
            if keep(h, a):
                hit += p
    return hit


def moneyline_two_way(rate_home: float, rate_away: float) -> tuple[float, float]:
    p = log5(rate_home, rate_away)
    return p, 1 - p


def total_lines(lam_home: float, lam_away: float, candidates: Iterable[float]) -> list[dict]:
    grid = poisson_grid(lam_home, lam_away)
    out = []
    for line in candidates:
        over = 0.0
        for h, row in enumerate(grid):
            for a, p in enumerate(row):
                if h + a > line:
                    over += p
        out.append({"line": line, "over": over, "under": 1 - over})
    return out


def best_total(lam_home: float, lam_away: float, candidates: Iterable[float]) -> dict:
    return min(total_lines(lam_home, lam_away, candidates),
               key=lambda x: abs(x["over"] - 0.5))


def handicap(grid: list[list[float]], line: float) -> tuple[float, float]:
    """Home covers ``line`` (a negative number gives the home side a start)."""
    cover = two_way_from_grid(grid, lambda h, a: h - a + line > 0)
    return cover, 1 - cover


def expected_runs(attack_rate: float, defence_rate: float) -> float:
    """Mean of the attack's scoring rate and the opponent's conceding rate."""
    if attack_rate is None or defence_rate is None:
        raise ValueError("expected_runs requires both rates")
    return (attack_rate + defence_rate) / 2.0


def shrink(wins: int, losses: int, prior: float = 0.5, weight: float = 2.0) -> float:
    """Beta-ish shrinkage: (wins + prior*weight) / (games + weight)."""
    games = wins + losses
    return (wins + prior * weight) / (games + weight)


def confidence_label(p: float, complete: bool) -> str:
    """Confidence is evidence-first, not probability-only.

    High needs a complete official input set and a fair probability of at least
    62%. Medium is 55-62% with complete inputs. Anything else, or any incomplete
    input, is Low. This is deliberately stricter than "the favourite is short".
    """
    if not complete:
        return "low"
    if p >= 0.62:
        return "high"
    if p >= 0.55:
        return "medium"
    return "low"
