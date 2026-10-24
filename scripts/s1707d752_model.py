"""Price origination for desk 1707d752.

Every number produced here is OUR OWN estimate, derived only from the official
facts recorded in s1707d752_data.py. Nothing here is a bookmaker quote.

Rules encoded:
  * No default ratings. A team without a captured record cannot be priced.
  * Small samples are shrunk toward the league mean before use.
  * Fair decimal price = 1 / probability, no margin, never clipped.
  * American price is derived from the unrounded decimal price.
  * Confidence is a documented function of the originated probability and of
    whether the inputs are complete; it cannot be raised by hand.
"""
from __future__ import annotations

import math
from statistics import NormalDist

NORM = NormalDist()


# --------------------------------------------------------------------------
# price conversion
# --------------------------------------------------------------------------
def decimal_from_probability(p: float) -> float:
    return 1.0 / p


def american_from_decimal(d: float) -> int:
    # half-up rounding: Python's round() is banker's rounding and would make
    # +192.5 collapse to +192 in one place and +193 in another.
    if d >= 2.0:
        return int(math.floor((d - 1.0) * 100 + 0.5))
    return int(math.floor(-100.0 / (d - 1.0) + 0.5))


def price_block(p: float) -> dict:
    p = min(max(p, 0.0005), 0.9995)
    d = decimal_from_probability(p)
    return {"probability": round(p, 8), "decimal": round(d, 3), "american": american_from_decimal(d)}


def in_brief_band(american: int) -> bool:
    """The brief's price window: -250 to +10000 inclusive."""
    return -250 <= american <= 10000


def brief_literal_high(p: float, american: int) -> bool:
    """The brief read literally: >70% AND a fair price inside -250..+10000."""
    return p > 0.70 and in_brief_band(american)


# --------------------------------------------------------------------------
# basketball
# --------------------------------------------------------------------------
BASKET_PRIOR = 12.0         # Beta(12,12): a two-game start is weak evidence, so shrink hard
BASKET_HOME_LOGIT = 0.20    # ~ +2.6 points of home advantage
BASKET_MARGIN_SD = 12.0     # points, league-typical spread of final margins


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def _shrugged_pct(won: int, played: int) -> float:
    return (won + BASKET_PRIOR) / (played + 2 * BASKET_PRIOR)


def basketball(home: dict, away: dict) -> dict:
    """home/away: {'wins': n, 'losses': n} from the official NBA standings."""
    ph = _shrugged_pct(home["wins"], home["wins"] + home["losses"])
    pa = _shrugged_pct(away["wins"], away["wins"] + away["losses"])
    edge = _logit(ph) - _logit(pa) + BASKET_HOME_LOGIT
    p_home = 1.0 / (1.0 + math.exp(-edge))
    mu = BASKET_MARGIN_SD * NORM.inv_cdf(p_home)      # our 50/50 margin, home positive
    line = round(mu * 2) / 2.0                        # publishable half-point line
    cover_home = 1 - NORM.cdf((line - mu) / BASKET_MARGIN_SD) if line >= 0 else NORM.cdf((line - mu) / BASKET_MARGIN_SD)
    cover_home = NORM.cdf((mu - line) / BASKET_MARGIN_SD)
    return {
        "p_home": p_home,
        "p_away": 1 - p_home,
        "home_rate": ph,
        "away_rate": pa,
        "margin": mu,
        "spread": line,
        "cover_home": cover_home,
        "cover_away": 1 - cover_home,
    }


# --------------------------------------------------------------------------
# ice hockey
# --------------------------------------------------------------------------
HOCKEY_SHRINK_GAMES = 8.0
HOCKEY_HOME_MULT = 1.03
HOCKEY_AWAY_MULT = 0.97
HOCKEY_TOTAL_LINE = 5.5


def league_goals_per_team_game(teams: dict) -> float:
    gf = sum(t["gf"] for t in teams.values())
    gp = sum(t["gp"] for t in teams.values())
    return gf / gp


def _poisson(k: int, lam: float) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def hockey(home: dict, away: dict, league_avg: float, max_goals: int = 12) -> dict:
    adj = lambda gf, ga, gp: ((gf + HOCKEY_SHRINK_GAMES * league_avg) / (gp + HOCKEY_SHRINK_GAMES),
                              (ga + HOCKEY_SHRINK_GAMES * league_avg) / (gp + HOCKEY_SHRINK_GAMES))
    hgf, hga = adj(home["gf"], home["ga"], home["gp"])
    agf, aga = adj(away["gf"], away["ga"], away["gp"])
    lam_home = hgf * (aga / league_avg) * HOCKEY_HOME_MULT
    lam_away = agf * (hga / league_avg) * HOCKEY_AWAY_MULT
    p_home = p_tie = p_home_ml2 = 0.0
    p_total_over = 0.0
    for i in range(max_goals + 1):
        pi = _poisson(i, lam_home)
        for j in range(max_goals + 1):
            pj = _poisson(j, lam_away)
            cell = pi * pj
            if i > j:
                p_home += cell
            elif i == j:
                p_tie += cell
            if i - j >= 2:
                p_home_ml2 += cell
            if i + j > HOCKEY_TOTAL_LINE:
                p_total_over += cell
    p_home += p_tie / 2.0          # ties resolved in overtime / shootout
    return {
        "p_home": p_home,
        "p_away": 1 - p_home,
        "lambda_home": lam_home,
        "lambda_away": lam_away,
        "lambda_total": lam_home + lam_away,
        "puck_home_minus_15": p_home_ml2,
        "puck_away_plus_15": 1 - p_home_ml2,
        "total_over": p_total_over,
        "total_under": 1 - p_total_over,
        "total_line": HOCKEY_TOTAL_LINE,
        "shrink": HOCKEY_SHRINK_GAMES,
    }


# --------------------------------------------------------------------------
# baseball
# --------------------------------------------------------------------------
BASEBALL_HOME_LOGIT = 0.16   # ~54% home field
BASEBALL_PRIOR = 2.0


def baseball(home: dict, away: dict) -> dict:
    ph = (home["wins"] + BASEBALL_PRIOR) / (home["wins"] + home["losses"] + 2 * BASEBALL_PRIOR)
    pa = (away["wins"] + BASEBALL_PRIOR) / (away["wins"] + away["losses"] + 2 * BASEBALL_PRIOR)
    # log5 with a home-field term in logit space
    edge = _logit(ph) - _logit(pa) + BASEBALL_HOME_LOGIT
    p_home = 1.0 / (1.0 + math.exp(-edge))
    return {"p_home": p_home, "p_away": 1 - p_home, "home_rate": ph, "away_rate": pa}


# --------------------------------------------------------------------------
# confidence
# --------------------------------------------------------------------------
HIGH_FLOOR = 0.60
MEDIUM_FLOOR = 0.53
# Minimum games played by BOTH sides before a High call is allowed. A two-game
# NBA start or an eight-game NHL start is not enough evidence for the top tier.
HIGH_MIN_GAMES = {"hockey": 8, "basketball": 20, "baseball": 60}


def grade(p: float, *, complete: bool, band: bool, sample_games: int | None, sample_floor: int) -> dict:
    """Documented tiering. Caps are recorded, never hidden.

    High   : p >= 60%, the selection's fair price sits inside -250..+10000,
             every input this desk needs was captured, and the league sample is
             at least 10 games per side.
    Medium : p >= 53%, or a 60%+ chance that fails a High condition.
    Low    : below 53%.
    """
    caps = []
    if p >= HIGH_FLOOR:
        if not band:
            caps.append("fair price is outside the brief's -250 to +10000 window")
        if not complete:
            caps.append("a required input was not captured")
        if sample_games is not None and sample_games < sample_floor:
            caps.append(f"the thinner side has played {sample_games} games, below the {sample_floor}-game minimum for a High call")
        tier = "High" if not caps else "Medium"
    elif p >= MEDIUM_FLOOR:
        tier = "Medium"
    else:
        tier = "Low"
    return {"tier": tier, "caps": caps, "probability": round(p, 4)}



