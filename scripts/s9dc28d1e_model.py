"""Pricing engine for the 9dc28d1e desk.

Three transparent, deliberately simple models. None of them is a calibrated betting
model; each is a zero-margin price generator whose assumptions are published next to
every number it produces.

NHL   Poisson goals, rates shrunk toward the league mean, small home multiplier.
EL    Normal margin and total around shrunk points rates, small home multiplier.
MLB   Pythagorean win rates combined log5, run totals from paired per-game rates.

Every selection is re-priced under a grid of assumptions so the desk can publish a
sensitivity range instead of a single point estimate.
"""

from __future__ import annotations

import math

from s9dc28d1e_inputs import (
    EL_GAMES,
    EL_TEAMS,
    MLB_GAMES,
    MLB_RECORDS,
    NHL_GAMES,
    NHL_TEAMS,
)

# ---------------------------------------------------------------------------
# NHL
# ---------------------------------------------------------------------------

NHL_K = 12.0            # pseudo-games of shrinkage toward the league mean
NHL_HOME = 1.045        # home multiplier on expected goals
NHL_AWAY = 0.955
NHL_BAND_LINES = (1.5, 2.5, 3.5, 4.5)
NHL_TOTAL_LINES = (5.5, 6.5, 7.5)
NHL_PUCK_LINES = (1.5,)


def _poisson_pmf(lam: float, k: int) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def _poisson_cdf(lam: float, k: int) -> float:
    return sum(_poisson_pmf(lam, i) for i in range(0, max(0, k) + 1))


def _poisson_over(lam: float, line: float) -> float:
    """P(X > line) for a half-run/half-goal line."""
    return 1.0 - _poisson_cdf(lam, int(math.floor(line)))


def _diff_distribution(mu_h: float, mu_a: float, span: int = 22):
    """P(home goals - away goals = d) for independent Poissons."""
    return {
        d: sum(_poisson_pmf(mu_h, k) * _poisson_pmf(mu_a, k - d) for k in range(max(0, d), span))
        for d in range(-span, span + 1)
    }


def _shrink(value: float, games: float, mean: float, k: float) -> float:
    weight = games / (games + k)
    return mean + weight * (value - mean)


def nhl_league_mean() -> float:
    total = sum(v[5] for v in NHL_TEAMS.values())
    games = sum(v[0] for v in NHL_TEAMS.values())
    return total / games


def nhl_rates(team: str, k: float = NHL_K) -> tuple[float, float]:
    games, _w, _l, _otl, _pts, gf, ga, *_ = NHL_TEAMS[team]
    avg = nhl_league_mean()
    attack = _shrink(gf / games, games, avg, k)
    defence = _shrink(ga / games, games, avg, k)
    return attack / avg, defence / avg


def nhl_lambdas(home: str, away: str, k: float = NHL_K, home_mult: float = NHL_HOME) -> tuple[float, float]:
    avg = nhl_league_mean()
    off_h, def_h = nhl_rates(home, k)
    off_a, def_a = nhl_rates(away, k)
    mu_h = avg * off_h * def_a * home_mult
    mu_a = avg * off_a * def_h * (2.0 - home_mult)
    return mu_h, mu_a


def nhl_selections(home: str, away: str, k: float = NHL_K, home_mult: float = NHL_HOME):
    """Yield (market_key, market_label, selection_label, probability)."""
    mu_h, mu_a = nhl_lambdas(home, away, k, home_mult)
    diff = _diff_distribution(mu_h, mu_a)
    total = sum(diff.values())

    p_home_reg = sum(p for d, p in diff.items() if d > 0)
    p_tie = diff[0]
    p_home = p_home_reg + 0.5 * p_tie
    yield ("winner", "Match winner (incl. OT/SO)", f"{home} to win", p_home)
    yield ("winner", "Match winner (incl. OT/SO)", f"{away} to win", 1.0 - p_home)

    for line in NHL_PUCK_LINES:
        # settlement is the full game including overtime, so a regulation tie always ends
        # with a one-goal margin and cannot cover -1.5 either way.
        home_minus = sum(p for d, p in diff.items() if d >= line)
        home_plus = 1.0 - sum(p for d, p in diff.items() if d <= -line)
        yield ("handicap", f"Puck line {home} -{line}", f"{home} -{line}", home_minus)
        yield ("handicap", f"Puck line {away} +{line}", f"{away} +{line}", 1.0 - home_minus)
        yield ("handicap", f"Puck line {away} -{line}", f"{away} -{line}", 1.0 - home_plus)
        yield ("handicap", f"Puck line {home} +{line}", f"{home} +{line}", home_plus)

    for line in NHL_TOTAL_LINES:
        over = _poisson_over(mu_h + mu_a, line)
        yield ("total", f"Match total {line}", f"Over {line} goals", over)
        yield ("total", f"Match total {line}", f"Under {line} goals", 1.0 - over)

    for team, mu in ((home, mu_h), (away, mu_a)):
        for line in NHL_BAND_LINES:
            over = _poisson_over(mu, line)
            yield ("team-total", f"{team} total {line}", f"{team} over {line} goals", over)
            yield ("team-total", f"{team} total {line}", f"{team} under {line} goals", 1.0 - over)


# ---------------------------------------------------------------------------
# EuroLeague
# ---------------------------------------------------------------------------

EL_K = 4.0                 # pseudo-games of shrinkage applied to point differential
EL_DIFF_WEIGHT = 0.50      # how much of the rating gap is allowed to show up as margin
EL_HOME_EDGE = 2.5         # points of home advantage added to the margin
EL_MARGIN_SD = 11.0
EL_TOTAL_SD = 15.5
EL_HANDICAP_LINES = (2.5, 4.5, 6.5, 8.5)
EL_TOTAL_LINES = (150.5, 154.5, 158.5, 162.5, 166.5, 170.5)
EL_TEAM_LINES = (70.5, 76.5, 82.5)


def el_rating(team: str, k: float = EL_K) -> float:
    """Shrunk points differential per game. A 6-game sample does not deserve full weight."""
    games, _w, _l, pf, pa = EL_TEAMS[team]
    raw = (pf - pa) / games
    weight = games / (games + k)
    return raw * weight


def el_pace(team: str) -> float:
    games, _w, _l, pf, pa = EL_TEAMS[team]
    return (pf + pa) / games


def el_mus(home: str, away: str, k: float = EL_K, home_edge: float = EL_HOME_EDGE,
           diff_weight: float = EL_DIFF_WEIGHT) -> tuple[float, float]:
    margin = (el_rating(home, k) - el_rating(away, k)) * diff_weight + home_edge
    total = (el_pace(home) + el_pace(away)) / 2.0
    return (total + margin) / 2.0, (total - margin) / 2.0


def _normal_upper(x: float, mu: float, sd: float) -> float:
    return 0.5 * math.erfc((x - mu) / (sd * math.sqrt(2.0)))


def el_selections(home: str, away: str, k: float = EL_K, home_edge: float = EL_HOME_EDGE,
                  margin_sd: float = EL_MARGIN_SD, total_sd: float = EL_TOTAL_SD):
    mu_h, mu_a = el_mus(home, away, k, home_edge)
    margin_mu = mu_h - mu_a
    total_mu = mu_h + mu_a

    p_home = 0.5 * math.erfc((-margin_mu) / (margin_sd * math.sqrt(2.0)))
    yield ("winner", "Match winner", f"{home} to win", p_home)
    yield ("winner", "Match winner", f"{away} to win", 1.0 - p_home)

    for line in EL_HANDICAP_LINES:
        cover_h = _normal_upper(line, margin_mu, margin_sd)
        yield ("handicap", f"Handicap {home} -{line}", f"{home} -{line}", cover_h)
        yield ("handicap", f"Handicap {away} +{line}", f"{away} +{line}", 1.0 - cover_h)

    for line in EL_TOTAL_LINES:
        over = _normal_upper(line, total_mu, total_sd)
        yield ("total", f"Match total {line}", f"Over {line} points", over)
        yield ("total", f"Match total {line}", f"Under {line} points", 1.0 - over)

    for team, mu in ((home, mu_h), (away, mu_a)):
        for line in EL_TEAM_LINES:
            over = _normal_upper(line, mu, margin_sd * 0.85)
            yield ("team-total", f"{team} total {line}", f"{team} over {line} points", over)
            yield ("team-total", f"{team} total {line}", f"{team} under {line} points", 1.0 - over)


# ---------------------------------------------------------------------------
# MLB
# ---------------------------------------------------------------------------

MLB_PYTH = 1.83
MLB_HOME_RUNS = 0.15
MLB_TOTAL_LINES = (7.5, 8.5, 9.5)
MLB_TEAM_LINES = (3.5, 4.5)
MLB_RUNLINE = 1.5


def mlb_pythagorean(team: str) -> float:
    _gp, _w, _l, rs, ra = MLB_RECORDS[team]
    return rs ** MLB_PYTH / (rs ** MLB_PYTH + ra ** MLB_PYTH)


def mlb_moneyline(home: str, away: str, exp: float = MLB_PYTH, home_runs: float = MLB_HOME_RUNS) -> float:
    def pyth(team):
        _gp, _w, _l, rs, ra = MLB_RECORDS[team]
        return rs ** exp / (rs ** exp + ra ** exp)

    ph, pa = pyth(home), pyth(away)
    base = (ph - ph * pa) / (ph + pa - 2 * ph * pa)
    odds = base / (1 - base) * 1.08
    return odds / (1 + odds)


def mlb_mus(home: str, away: str, home_runs: float = MLB_HOME_RUNS) -> tuple[float, float]:
    _g1, _w1, _l1, rs_h, ra_h = MLB_RECORDS[home]
    _g2, _w2, _l2, rs_a, ra_a = MLB_RECORDS[away]
    gp_h = MLB_RECORDS[home][0]
    gp_a = MLB_RECORDS[away][0]
    mu_h = ((rs_h / gp_h) + (ra_a / gp_a)) / 2.0 + home_runs
    mu_a = ((rs_a / gp_a) + (ra_h / gp_h)) / 2.0 - home_runs
    return mu_h, mu_a


def mlb_selections(home: str, away: str, exp: float = MLB_PYTH, home_runs: float = MLB_HOME_RUNS):
    p_home = mlb_moneyline(home, away, exp, home_runs)
    mu_h, mu_a = mlb_mus(home, away, home_runs)
    diff = _diff_distribution(mu_h, mu_a, span=26)
    # a tied nine-inning game is decided in extra innings; split it evenly and renormalise
    p_tie = diff[0]
    scale = 1.0 / (1.0 - p_tie)
    win_h = (sum(p for d, p in diff.items() if d > 0) + 0.5 * p_tie) * scale
    # publish the log5 moneyline as the headline price and use the run model for margins
    yield ("winner", "Match winner (incl. extra innings)", f"{home} to win", p_home)
    yield ("winner", "Match winner (incl. extra innings)", f"{away} to win", 1.0 - p_home)

    home_minus = sum(p for d, p in diff.items() if d > MLB_RUNLINE) * scale
    home_plus = 1.0 - sum(p for d, p in diff.items() if d < -MLB_RUNLINE) * scale
    yield ("handicap", f"Run line {home} -{MLB_RUNLINE}", f"{home} -{MLB_RUNLINE}", home_minus)
    yield ("handicap", f"Run line {away} +{MLB_RUNLINE}", f"{away} +{MLB_RUNLINE}", 1.0 - home_minus)
    yield ("handicap", f"Run line {away} -{MLB_RUNLINE}", f"{away} -{MLB_RUNLINE}", 1.0 - home_plus)
    yield ("handicap", f"Run line {home} +{MLB_RUNLINE}", f"{home} +{MLB_RUNLINE}", home_plus)

    for line in MLB_TOTAL_LINES:
        over = _poisson_over(mu_h + mu_a, line)
        yield ("total", f"Match total {line}", f"Over {line} runs", over)
        yield ("total", f"Match total {line}", f"Under {line} runs", 1.0 - over)

    for team, mu in ((home, mu_h), (away, mu_a)):
        for line in MLB_TEAM_LINES:
            over = _poisson_over(mu, line)
            yield ("team-total", f"{team} total {line}", f"{team} over {line} runs", over)
            yield ("team-total", f"{team} total {line}", f"{team} under {line} runs", 1.0 - over)


# ---------------------------------------------------------------------------
# Prices, gate and tiers
# ---------------------------------------------------------------------------

HIGH_PROB_FLOOR = 0.70
PRICE_SHORT_EDGE = -250
PRICE_LONG_EDGE = 10000


def decimal_from_probability(p: float) -> float:
    return round(1.0 / p, 6)


def american_from_probability(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return float("nan")
    if p > 0.5:
        return round(-100.0 * p / (1.0 - p), 2)
    return round(100.0 * (1.0 - p) / p, 2)


def in_price_window(american: float) -> bool:
    return PRICE_SHORT_EDGE <= american <= PRICE_LONG_EDGE


def qualifies_for_high(p: float, american: float) -> bool:
    return p > HIGH_PROB_FLOOR and in_price_window(american)


def tier_for(p: float, american: float, player_evidence: bool) -> tuple[str, str]:
    """Return (tier, reason). The gate is applied conjunctively and literally."""
    if p > HIGH_PROB_FLOOR and in_price_window(american):
        if player_evidence:
            return "HIGH", ""
        return "MEDIUM", "clears the 70% rule and sits inside the price window, but no verified player-level source was available for the required write-up"
    if p > HIGH_PROB_FLOOR:
        return "MEDIUM", "clears 70% but the fair price is shorter than -250, so it is outside the brief's window"
    if p >= 0.65:
        return "MEDIUM", ""
    return "LOW", ""


# ---------------------------------------------------------------------------
# Sensitivity grid
# ---------------------------------------------------------------------------

def sensitivity(sport: str, home: str, away: str, key: str, label: str) -> tuple[float, float]:
    lows, highs = [], []
    if sport == "ice-hockey":
        for k in (6.0, 12.0, 20.0):
            for hm in (1.0, 1.045, 1.08):
                for kk, _m, ll, _p in nhl_selections(home, away, k, hm):
                    if kk == key and ll == label:
                        lows.append(_p)
                        highs.append(_p)
    elif sport == "basketball":
        for k in (2.0, 4.0, 8.0):
            for hm in (2.0, 2.5, 3.0):
                for sd in (10.0, 11.0, 12.0):
                    for kk, _m, ll, _p in el_selections(home, away, k, hm, sd):
                        if kk == key and ll == label:
                            lows.append(_p)
                            highs.append(_p)
    else:
        for exp in (1.70, 1.83, 2.00):
            for hr in (0.0, 0.15, 0.30):
                for kk, _m, ll, _p in mlb_selections(home, away, exp, hr):
                    if kk == key and ll == label:
                        lows.append(_p)
                        highs.append(_p)
    if not lows:
        return (0.0, 1.0)
    return (round(min(lows), 6), round(max(highs), 6))
