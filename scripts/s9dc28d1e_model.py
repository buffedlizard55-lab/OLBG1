"""Session 9dc28d1e — zero-margin multi-market line origination.

Deliberately simple, auditable and explicit about its assumptions. Nothing here is fitted to any
market price: no bookmaker prices were read, so the output is a model estimate, not a quote.

Method summary
--------------
NHL (goals)
  * League goals-per-team-per-game is computed from the 32-club official summary.
  * Each club's attack and defence are shrunk toward the league mean with weight
    k = GP / (GP + SHRINK). SHRINK = 12 games, chosen because every club has played 7-12 games;
    leaning on a nine-game goal rate without shrinkage would be over-confident.
  * Expected goals for A: off_A + (def_B - league_mean) + home_edge (away side subtracts it).
  * Regulation goals are modelled as independent Poisson variables.
  * Moneyline (settles including OT/SO): P(A) = P(A leads after 60) + 0.5 * P(tied after 60).
    The coin-flip split of overtime is an ASSUMPTION, not a measured quantity.
  * Puck line (settles including OT/SO): a regulation tie becomes a one-goal win for the side that
    takes overtime, so P(A -1.5) = P(A by 2+ after 60) and P(A +1.5) = P(A not lose by 2+).
  * Totals settle on the full game including OT and are modelled as a Poisson total.

EuroLeague (points)
  * League points-per-team-per-game from the 20-club official standings.
  * Attack/defence shrunk with SHRINK = 8 games over six or seven played.
  * Expected points use the same additive structure; home edge is 1.5 points.
  * Margin ~ Normal(mean margin, 12.0) and total ~ Normal(mean total, 15.5). Those dispersions are
    documented assumptions taken from the shape of professional basketball scoring, not fitted here.
  * Handicaps and totals settle on the full game including overtime.

MLB (runs)
  * Moneyline only. The official projection used here returns two clubs' records, not a league run
    environment, so run-line and total origination is withheld rather than guessed.
  * P(A) uses the log5 form on the two official winning percentages.

Price convention
  * fair_decimal = 1/p and american is derived from p. There is no margin, no clipping and no
    rounding inside the calculations; only the display strings are rounded.
"""

from math import exp, erf, factorial, sqrt

from s9dc28d1e_data import EL_TEAMS, MLB_RECORDS, NHL_TEAMS

NHL_SHRINK = 12.0
EL_SHRINK = 8.0
NHL_HOME_EDGE = 0.10      # goals
EL_HOME_EDGE = 1.5        # points
EL_SIGMA_MARGIN = 12.0
EL_SIGMA_TOTAL = 15.5


# ------------------------------------------------------------------ helpers
def _mean(values):
    return sum(values) / len(values)


def nhl_league_mean():
    gp = sum(v[0] for v in NHL_TEAMS.values())
    gf = sum(v[4] for v in NHL_TEAMS.values())
    return gf / gp


def el_league_mean():
    gp = sum(v[0] for v in EL_TEAMS.values())
    pf = sum(v[3] for v in EL_TEAMS.values())
    return pf / gp


def nhl_ratings(name):
    gp, w, l, otl, gf, ga = NHL_TEAMS[name]
    m = nhl_league_mean()
    k = gp / (gp + NHL_SHRINK)
    return m + k * (gf / gp - m), m + k * (ga / gp - m)


def el_ratings(name):
    gp, w, l, pf, pa = EL_TEAMS[name]
    m = el_league_mean()
    k = gp / (gp + EL_SHRINK)
    return m + k * (pf / gp - m), m + k * (pa / gp - m)


def normal_cdf(z):
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))


def poisson_pmf(k, mu):
    return exp(-mu) * mu ** k / factorial(k)


# ------------------------------------------------------------------ NHL
def nhl_expected_goals(away, home):
    oa, da = nhl_ratings(away)
    oh, dh = nhl_ratings(home)
    m = nhl_league_mean()
    mu_away = oa + (dh - m) - NHL_HOME_EDGE
    mu_home = oh + (da - m) + NHL_HOME_EDGE
    return mu_away, mu_home


def nhl_distribution(away, home, max_goals=12):
    mu_a, mu_h = nhl_expected_goals(away, home)
    grid = [(i, j, poisson_pmf(i, mu_a) * poisson_pmf(j, mu_h))
            for i in range(max_goals + 1) for j in range(max_goals + 1)]
    total = sum(p for _, _, p in grid)
    return mu_a, mu_h, [(i, j, p / total) for i, j, p in grid]


def nhl_moneyline(away, home):
    _, _, grid = nhl_distribution(away, home)
    home_win = sum(p for i, j, p in grid if j > i)
    tie = sum(p for i, j, p in grid if i == j)
    return tie / 2 + home_win


def nhl_puck_line(away, home, side, line):
    """side in {'away','home'}; line is the handicap applied to that side (e.g. -1.5, +1.5)."""
    _, _, grid = nhl_distribution(away, home)
    tie_mass = 0.0
    cover = 0.0
    for i, j, p in grid:
        if i == j:
            tie_mass += p
            continue
        margin = (j - i) if side == 'home' else (i - j)
        if margin + line > 0:
            cover += p
    # overtime converts a regulation tie into a one-goal win for one of the two sides
    if line + 1 > 0:
        cover += tie_mass / 2
    return cover


def nhl_total_distribution(away, home, max_goals=16):
    mu_a, mu_h = nhl_expected_goals(away, home)
    mu = mu_a + mu_h
    return [poisson_pmf(k, mu) for k in range(max_goals + 1)]


def nhl_total_over(away, home, line):
    dist = nhl_total_distribution(away, home)
    # line is always a half line, so there is no push
    threshold = int(line) + 1  # over 5.5 needs 6+
    return sum(dist[threshold:])


# ------------------------------------------------------------------ EuroLeague
def el_expected_points(home, away):
    oh, dh = el_ratings(home)
    oa, da = el_ratings(away)
    m = el_league_mean()
    mu_home = oh + (da - m) + EL_HOME_EDGE
    mu_away = oa + (dh - m) - EL_HOME_EDGE
    return mu_home, mu_away


def el_moneyline(home, away):
    mu_h, mu_a = el_expected_points(home, away)
    return normal_cdf((mu_h - mu_a) / EL_SIGMA_MARGIN)


def el_handicap(home, away, side, line):
    mu_h, mu_a = el_expected_points(home, away)
    margin = (mu_h - mu_a) if side == 'home' else (mu_a - mu_h)
    return normal_cdf((margin + line) / EL_SIGMA_MARGIN)


def el_total_over(home, away, line):
    mu_h, mu_a = el_expected_points(home, away)
    mu = mu_h + mu_a
    # continuity: a total of exactly `line` is impossible with half lines
    return 1.0 - normal_cdf((line - mu) / EL_SIGMA_TOTAL)


# ------------------------------------------------------------------ MLB
def mlb_moneyline(away, home):
    a = MLB_RECORDS[away]
    h = MLB_RECORDS[home]
    pa = a['w'] / a['gp']
    ph = h['w'] / h['gp']
    # log5: probability that A beats B given each side's rate against the league average
    return (pa - pa * ph) / (pa + ph - 2 * pa * ph)


# ------------------------------------------------------------------ pricing
def american_from_probability(p):
    if p <= 0 or p >= 1:
        raise ValueError('probability outside (0,1)')
    if p >= 0.5:
        return -100.0 * p / (1.0 - p)
    return 100.0 * (1.0 - p) / p


def fair_decimal(p):
    return 1.0 / p


BAND_LOW = -250.0
BAND_HIGH = 10000.0


def in_band(p):
    am = american_from_probability(p)
    return BAND_LOW <= am <= BAND_HIGH


def tier(p):
    """The brief's rule, applied literally and conjunctively.

    High requires BOTH (a) a model probability strictly greater than 0.70 and (b) the selected
    line's fair American price inside [-250, +10000]. Because >70% implies American < -233.33,
    the conjunction can only be satisfied for probabilities in (0.7000, 0.7143].
    Markets that clear 70% but price shorter than -250 are returned as 'outside_window' and are
    never relabelled High.
    """
    if p > 0.70 and in_band(p):
        return 'high'
    if p > 0.70 and not in_band(p):
        return 'outside_window'
    if 0.60 <= p <= 0.70:
        return 'medium'
    return 'low'
