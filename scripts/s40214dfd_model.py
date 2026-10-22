"""Origination model for the 40214dfd desk.

Every input to this module is a value that was read from an official source and stored in
data/40214dfd/harvest/*.json. Nothing here invents a statistic: the only non-observed numbers
are the declared model parameters listed in ASSUMPTIONS, and every output that depends on one
of them is tagged with that parameter so the site can show it.

Prices are fair prices derived as 1/p. They are NOT bookmaker offers. No bookmaker price is
claimed anywhere in this desk.
"""
from decimal import Decimal, ROUND_HALF_UP
import math

MODEL_VERSION = "desk402-v1.0"

ASSUMPTIONS = {
    "record_model": (
        "Beta(2,2) shrinkage of the season win rate, then log5 between the two shrunk rates. "
        "No home-field term is added because no home-split edge is measured here."
    ),
    "nhl_winner": (
        "Binary market: wins include overtime and shootout wins; losses include regulation, "
        "overtime and shootout losses."
    ),
    "nhl_goal_model": (
        "Independent Poisson goals per side. Each side's rate averages its own goals-for per game "
        "and the opponent's goals-against per game. Regulation-goal approximation: overtime and "
        "shootout goals are not separate events in the grid."
    ),
    "mlb_run_model": (
        "Independent Poisson runs per side, conditioned on the game not finishing tied. Rates "
        "average own runs scored per game and opponent runs allowed per game from the final "
        "regular-season table. Postseason personnel, starting pitchers, bullpens, parks and "
        "travel are not modelled."
    ),
    "basketball_handicap": (
        "Margins are modelled as Normal with an ASSUMED standard deviation of 12.0 points; the "
        "mean is set so that the model's win probability is reproduced. 12.0 is an assumption, "
        "not a measured league constant, and basketball handicap rows are capped below High for "
        "that reason."
    ),
    "basketball_totals": (
        "Expected total is the sum of the two sides' expected points, where a side's expectation "
        "averages its own points per game and the opponent's points allowed per game as quoted by "
        "the official preview. Totals are only originated when BOTH averages are published."
    ),
    "handicaps": (
        "Only half-point lines are originated, so every handicap or total settles without a push. "
        "Whole-number lines are deliberately not offered."
    ),
    "high_rule": (
        "The brief asks for selections above a 70% chance whose price is inside -250..+10000. "
        "American -250 is decimal 1.40, i.e. 71.4286%. A fair price above 70% is therefore at most "
        "1.4286 decimal, so the two rules only intersect on 70.0000% < p <= 71.4286%. High is "
        "issued only inside that intersection, with verified inputs on both sides and a written "
        "prediction."
    ),
}


# ---------------------------------------------------------------- price helpers
def decimal_from_prob(p):
    if not (0.0 < p < 1.0):
        raise ValueError("probability must be strictly between 0 and 1")
    return 1.0 / p


def american_from_decimal(d):
    d = Decimal(str(d))
    if d <= 1:
        raise ValueError("decimal odds must exceed 1")
    value = (d - 1) * 100 if d >= 2 else -100 / (d - 1)
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def in_brief_band(p):
    """True when the FAIR price of a probability sits inside the brief's -250..+10000 window."""
    fair = decimal_from_prob(p)
    return 1.40 <= fair <= 101.0


def price_block(p):
    fair = decimal_from_prob(p)
    displayed = round(fair, 4)
    return {
        "probability": round(p, 6),
        "fair_decimal": displayed,
        "american": american_from_decimal(displayed),
        "fair_price_in_brief_band": in_brief_band(p),
        "offer_status": "originated fair price; no bookmaker quote captured",
    }


# ---------------------------------------------------------------- win model
def shrunk_rate(wins, games, alpha=2.0):
    if games <= 0 or wins < 0 or wins > games:
        raise ValueError("invalid record")
    return (wins + alpha) / (games + 2 * alpha)


def log5(p_a, p_b):
    num = p_a * (1 - p_b)
    den = num + p_b * (1 - p_a)
    if den <= 0:
        raise ValueError("degenerate log5")
    return num / den


def winner_probability(team_a, team_b):
    """team records are {'wins': int, 'games': int}."""
    pa = shrunk_rate(team_a["wins"], team_a["games"])
    pb = shrunk_rate(team_b["wins"], team_b["games"])
    return log5(pa, pb)


# ---------------------------------------------------------------- goal / run grid
def poisson_pmf(lam, n_max):
    if not (0 < lam < 25):
        raise ValueError("rate outside the tested domain")
    values = [math.exp(-lam)]
    for n in range(1, n_max + 1):
        values.append(values[-1] * lam / n)
    if sum(values) < 0.999999:
        raise ValueError("truncated tail too heavy; raise n_max")
    return values


def difference_grid(lam_a, lam_b, n_max=20):
    """Joint independent-Poisson score grid on the margin (a - b)."""
    pa = poisson_pmf(lam_a, n_max)
    pb = poisson_pmf(lam_b, n_max)
    margins = {}
    total = 0.0
    totals = {}
    for i, px in enumerate(pa):
        for j, py in enumerate(pb):
            mass = px * py
            total += mass
            margins[i - j] = margins.get(i - j, 0.0) + mass
            totals[i + j] = totals.get(i + j, 0.0) + mass
    return {"margin": margins, "total": totals, "mass": total}


def prob_margin_at_least(grid, line):
    """P(margin > line) for a half-point line, e.g. line=1.5 -> P(margin >= 2)."""
    return math.fsum(m for d, m in grid["margin"].items() if d > line)


def prob_total_over(grid, line):
    return math.fsum(m for t, m in grid["total"].items() if t > line)


def rate_pair(scored_a, allowed_a, games_a, scored_b, allowed_b, games_b):
    lam_a = (scored_a / games_a + allowed_b / games_b) / 2.0
    lam_b = (scored_b / games_b + allowed_a / games_a) / 2.0
    return lam_a, lam_b


# ---------------------------------------------------------------- normal margin model
def _phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _inverse_normal(p, lo=-6.0, hi=6.0, tol=1e-10):
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _phi(mid) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0


def normal_margin(p_win, sigma=12.0):
    """Mean margin that reproduces p_win under an assumed normal spread."""
    return sigma * _inverse_normal(p_win)


def prob_margin_at_least_normal(mu, sigma, line):
    return 1.0 - _phi((line - mu) / sigma)


# ---------------------------------------------------------------- confidence
def confidence_for(p, *, inputs_complete, has_prediction, manufactured_by_assumption=False,
                   settlement_verified=True):
    """Return (tier, [reasons]). Tiers are issued from the brief's own arithmetic.

    High needs the intersection 70.0% < p <= 71.4286%, complete verified inputs on both sides,
    a written prediction, no assumed-only parameter carrying the number, and a verified
    settlement definition.
    """
    reasons = []
    if not settlement_verified:
        reasons.append("settlement definition not verified for this market")
    if not inputs_complete:
        reasons.append("verified inputs are not complete on both sides")
    if manufactured_by_assumption:
        reasons.append("the number depends on an assumed model parameter (normal spread sigma)")
    if not has_prediction:
        reasons.append("no written prediction attached to this selection")
    if not (p > 0.7000):
        reasons.append("model probability is not above 70%")
    if not in_brief_band(p):
        reasons.append("fair price is outside the brief's -250..+10000 window")
    if not reasons:
        return "high", ["model probability above 70% and fair price inside the brief window; "
                        "both sides' inputs verified; written prediction attached"]
    if p >= 0.65 and in_brief_band(p) is False and p > 0.7143:
        return "medium", reasons + ["strong model view but priced shorter than -250"]
    if p >= 0.60:
        return "medium", reasons
    return "low", reasons
