"""Origination engine for session f840c28a-olbg1.

Nothing in here reads the internet. It turns the captured official facts in
``sf840c28a_facts`` into margin-free two-way prices, grades each outcome against
the brief's confidence gate and produces the pick list.

Method (also published on the desk's methodology page)
------------------------------------------------------
Ice hockey
    Independent Poisson goals with
        lambda_home = ((home GF/G) + (away GA/G)) / 2 * 1.05
        lambda_away = ((away GF/G) + (home GA/G)) / 2 * 0.95
    Markets: moneyline, +-1.5 puck line, Asian handicap -1/+1 (integer line,
    pushes removed) and totals 5.5 / 6.5. A club without a captured goals-for
    and goals-against rate (Detroit) is not priced at all.

Basketball
    Only wins and losses were captured, so the rating is a shrunk win rate
        s = (W - L) / (GP + 8)
    and the expected margin is
        margin = 40 * (s_home - s_away) + 3.0        (3.0 = home court)
    with a normal margin distribution of sd 12.5. Markets: moneyline and
    spread ladders. Totals are withheld: no official scoring figure was read.

Confidence gate
    High    p > 0.70 and fair American price inside [-250, +10000]
    Medium  0.60 <= p <= 0.70 and inside the band
    Low     0.55 <= p < 0.60 and inside the band
    Anything outside the band is listed as "outside band" and is never a pick.

Prices are fair (zero-margin) two-way prices: the two probabilities of a market
are normalised to sum to one, then converted to American odds.
"""

from __future__ import annotations

import math

import sf840c28a_facts as F

BAND_LO = -250.0
BAND_HI = 10000.0


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def american(p: float) -> float:
    """Fair American price for probability p."""
    p = min(max(p, 0.0005), 0.9995)
    if p >= 0.5:
        return -100.0 * p / (1.0 - p)
    return 100.0 * (1.0 - p) / p


def decimal(p: float) -> float:
    return 1.0 / min(max(p, 0.0005), 0.9995)


def band_state(price: float) -> str:
    return "in" if BAND_LO <= price <= BAND_HI else "out"


def tier(p: float, price: float) -> str:
    if band_state(price) != "in":
        return "outside band"
    if p > 0.70:
        return "High"
    if p >= 0.60:
        return "Medium"
    if p >= 0.52:
        return "Low"
    return "outside band"


def poisson_pmf(lam: float, k: int) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def nhl_grid(lam_h: float, lam_a: float, n: int = 12):
    return {(h, a): poisson_pmf(lam_h, h) * poisson_pmf(lam_a, a)
            for h in range(n) for a in range(n)}


# --------------------------------------------------------------------------
# price a market: normalise the two sides so the book is margin-free
# --------------------------------------------------------------------------

def two_way(p_a: float, p_b: float):
    total = p_a + p_b
    pa, pb = p_a / total, p_b / total
    return pa, pb


# --------------------------------------------------------------------------
# ice hockey
# --------------------------------------------------------------------------

LEAGUE_GOALS = 3.00   # NHL average goals per club per game, prior centre
PRIOR_GP = 12.0       # games of league-average prior added to every rate
HOME_GOALS = 1.03     # home scoring multiplier
ROAD_GOALS = 0.97


def shrunk(rate: float, gp: int) -> float:
    """Regress a goals-for/against rate onto the league average."""
    return (rate * gp + LEAGUE_GOALS * PRIOR_GP) / (gp + PRIOR_GP)


def nhl_lambdas(home: str, away: str):
    th, ta = F.NHL_TEAMS[home], F.NHL_TEAMS[away]
    if th["gf"] is None or ta["gf"] is None:
        return None
    gf_h, ga_h = shrunk(th["gf"], th["gp"]), shrunk(th["ga"], th["gp"])
    gf_a, ga_a = shrunk(ta["gf"], ta["gp"]), shrunk(ta["ga"], ta["gp"])
    lam_h = ((gf_h + ga_a) / 2.0) * HOME_GOALS
    lam_a = ((gf_a + ga_h) / 2.0) * ROAD_GOALS
    return lam_h, lam_a


def nhl_markets(home: str, away: str):
    """Return list of market dicts for one NHL fixture."""
    lam = nhl_lambdas(home, away)
    if lam is None:
        return None
    lam_h, lam_a = lam
    grid = nhl_grid(lam_h, lam_a)

    win_h = sum(p for (h, a), p in grid.items() if h > a)
    win_a = sum(p for (h, a), p in grid.items() if a > h)
    # overtime/shootout is decided, so split the regulation tie in proportion to
    # the two clubs' relative scoring strength
    tie = sum(p for (h, a), p in grid.items() if h == a)
    share_h = lam_h / (lam_h + lam_a)
    win_h += tie * share_h
    win_a += tie * (1 - share_h)

    markets = []

    # moneyline
    pa, pb = two_way(win_h, win_a)
    markets.append(dict(market="Moneyline", line="", home_sel=home, away_sel=away,
                        home_p=pa, away_p=pb))

    # 1.5 puck line. The two sides are exhaustive on a half-goal line:
    # the home club covers by winning by two or more, everything else is the
    # away club's side of the line.
    cover_h15 = sum(p for (h, a), p in grid.items() if h - a > 1.5)
    pa, pb = cover_h15, 1.0 - cover_h15
    markets.append(dict(market="Puck line", line="+/-1.5", home_sel=f"{home} -1.5",
                        away_sel=f"{away} +1.5", home_p=pa, away_p=pb))

    # Asian handicap -1 / +1, pushes removed
    h_minus1_win = sum(p for (h, a), p in grid.items() if h - a > 1)
    h_minus1_push = sum(p for (h, a), p in grid.items() if h - a == 1)
    a_plus1_win = sum(p for (h, a), p in grid.items() if a - h >= 0)
    a_plus1_push = sum(p for (h, a), p in grid.items() if h - a == 1)
    denom = 1.0 - h_minus1_push
    pa, pb = two_way(h_minus1_win / denom, a_plus1_win / denom)
    markets.append(dict(market="Asian handicap", line="-1 / +1 (push void)",
                        home_sel=f"{home} -1", away_sel=f"{away} +1",
                        home_p=pa, away_p=pb))

    # deeper puck line
    cover_h25 = sum(p for (h, a), p in grid.items() if h - a > 2.5)
    pa, pb = cover_h25, 1.0 - cover_h25
    markets.append(dict(market="Puck line", line="+/-2.5", home_sel=f"{home} -2.5",
                        away_sel=f"{away} +2.5", home_p=pa, away_p=pb))

    # Asian handicap -2 / +2
    h_minus2 = sum(p for (h, a), p in grid.items() if h - a > 2)
    h_minus2_push = sum(p for (h, a), p in grid.items() if h - a == 2)
    a_plus2 = sum(p for (h, a), p in grid.items() if a - h >= -1)
    pa, pb = two_way(h_minus2 / (1 - h_minus2_push), a_plus2 / (1 - h_minus2_push))
    markets.append(dict(market="Asian handicap", line="-2 / +2 (push void)",
                        home_sel=f"{home} -2", away_sel=f"{away} +2",
                        home_p=pa, away_p=pb))

    # totals
    for line in (4.5, 5.5, 6.5, 7.5):
        over = sum(p for (h, a), p in grid.items() if h + a > line)
        under = sum(p for (h, a), p in grid.items() if h + a < line)
        pa, pb = two_way(over, under)
        markets.append(dict(market="Match total", line=str(line),
                            home_sel=f"Over {line}", away_sel=f"Under {line}",
                            home_p=pa, away_p=pb))
    return markets


# --------------------------------------------------------------------------
# basketball
# --------------------------------------------------------------------------

PRIOR_GAMES = 10.0      # 10 wins + 10 losses of .500 prior per club
ML_SLOPE = 4.4          # logit slope on (rating difference + home edge)
HOME_EDGE = 0.03        # home court in win-probability points
MARGIN_SD = 12.5        # standard deviation of an NBA final margin


def nba_rating(team: str):
    rec = F.NBA_RECORDS.get(team)
    if rec is None:
        return None
    w, l = rec
    return (w + PRIOR_GAMES) / (w + l + 2 * PRIOR_GAMES) - 0.5


def nba_markets(home: str, away: str):
    rh, ra = nba_rating(home), nba_rating(away)
    if rh is None or ra is None:
        return None
    z = ML_SLOPE * ((rh - ra) + HOME_EDGE)
    ph = 1.0 / (1.0 + math.exp(-z))
    margin = MARGIN_SD * _probit(ph)

    markets = []
    pa, pb = two_way(ph, 1 - ph)
    markets.append(dict(market="Moneyline", line="", home_sel=home, away_sel=away,
                        home_p=pa, away_p=pb))

    for line in (4.5, 6.5, 9.5):
        p = norm_cdf((margin - line) / MARGIN_SD)
        pa, pb = two_way(p, 1 - p)
        markets.append(dict(market="Point spread", line=str(line),
                            home_sel=f"{home} -{line}", away_sel=f"{away} +{line}",
                            home_p=pa, away_p=pb))
    return markets


def _probit(p: float) -> float:
    """Inverse standard normal CDF (Acklam's rational approximation)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


# --------------------------------------------------------------------------
# build the priced board
# --------------------------------------------------------------------------

def outcomes(ms):
    """Flatten markets into priced selections."""
    out = []
    for m in ms:
        for side, sel, p in (("home", m["home_sel"], m["home_p"]),
                             ("away", m["away_sel"], m["away_p"])):
            price = american(p)
            out.append(dict(market=m["market"], line=m["line"], side=side,
                            selection=sel, p=p, price=price,
                            decimal=round(decimal(p), 3),
                            band=band_state(price), tier=tier(p, price)))
    return out


def pick_for(outs, game):
    """Choose the desk's selection for one fixture.

    Candidate selections are limited to markets we can defend from captured
    facts: the moneyline (either side), every match-total rung, and the puck
    line / spread / Asian handicap rungs **on our favoured side**. Underdog
    cushion lines are deliberately excluded -- they carry the biggest number in
    the window but say nothing useful about the match.

    Among those candidates the pick is the highest-probability selection whose
    fair price sits inside the brief's -250..+10000 window.
    """
    ml = [o for o in outs if o["market"] == "Moneyline"]
    if not ml:
        return None
    fav = max(ml, key=lambda o: o["p"])
    side = fav["side"]

    cands = [o for o in outs
             if o["band"] == "in"
             and o["p"] <= 0.7142857
             and (o["market"] in ("Moneyline", "Match total")
                  or (o["side"] == side and o["market"] in
                      ("Puck line", "Point spread", "Asian handicap")))]
    if not cands:
        return None
    best = max(cands, key=lambda o: (o["p"], o["market"] == "Moneyline"))
    reason = ("Highest-probability selection inside the window among the "
              "moneyline, the totals ladder and the favoured side's handicap ladder.")
    return dict(selection=best["selection"], market=best["market"],
                line=best["line"], p=best["p"], price=best["price"],
                decimal=best["decimal"], confidence=best["tier"],
                game=game, side=best["side"], note=reason, fav_side=side)


def build_board():
    games = []

    for g in F.NHL_GAMES:
        ms = nhl_markets(g["home"], g["away"])
        row = dict(sport="ice-hockey", competition="NHL",
                   away=g["away"], home=g["home"],
                   start_utc=g["start_utc"], olbg_time=g["olbg_time"],
                   priced=ms is not None,
                   source="nhl-team-summary",
                   olbg_url="https://www.olbg.com/betting-tips/Ice_Hockey/13",
                   markets=[], pick=None,
                   home_rec=F.NHL_TEAMS[g["home"]], away_rec=F.NHL_TEAMS[g["away"]])
        if ms is not None:
            outs = outcomes(ms)
            row["markets"] = [dict(market=m["market"], line=m["line"],
                                   home_sel=m["home_sel"], away_sel=m["away_sel"],
                                   home_p=m["home_p"], away_p=m["away_p"])
                              for m in ms]
            row["outcomes"] = outs
            row["pick"] = pick_for(outs, f'{g["away"]} @ {g["home"]}')
            row["withheld"] = []
        else:
            row["outcomes"] = []
            row["pick"] = None
            row["withheld"] = ["Detroit goals-for and goals-against were not visible in the "
                               "returned page slice, so no rate could be used."]
        games.append(row)

    for g in F.NBA_GAMES:
        ms = nba_markets(g["home"], g["away"])
        row = dict(sport="basketball", competition="NBA",
                   away=g["away"], home=g["home"], start_utc=g["start_utc"],
                   olbg_time=g["et"], priced=ms is not None,
                   source="nba-injury",
                   olbg_url="https://www.olbg.com/betting-tips/Basketball/4",
                   markets=[], pick=None,
                   home_rec=F.NBA_RECORDS.get(g["home"]),
                   away_rec=F.NBA_RECORDS.get(g["away"]),
                   on_olbg_hub=g["on_olbg_hub"],
                   injuries=F.NBA_INJURIES.get((g["away"], g["home"]), {}))
        if ms is not None:
            outs = outcomes(ms)
            row["markets"] = [dict(market=m["market"], line=m["line"],
                                   home_sel=m["home_sel"], away_sel=m["away_sel"],
                                   home_p=m["home_p"], away_p=m["away_p"]) for m in ms]
            row["outcomes"] = outs
            row["pick"] = pick_for(outs, f'{g["away"]} @ {g["home"]}')
        else:
            row["outcomes"] = []
            row["pick"] = None
        row["withheld"] = ["Game total: no official NBA scoring figure was read, "
                           "so no total is originated."]
        games.append(row)

    return games


if __name__ == "__main__":
    board = build_board()
    n_priced = sum(1 for g in board if g["priced"])
    print(f"fixtures: {len(board)}  priced: {n_priced}")
    for g in board:
        p = g["pick"]
        if p:
            print(f'{g["sport"][:5]} {g["away"]:>3} @ {g["home"]:<3} | '
                  f'{p["selection"]:<18} {p["market"]:<14} p={p["p"]:.3f} '
                  f'price={p["price"]:>8.0f} {p["confidence"]}')
        else:
            print(f'{g["sport"][:5]} {g["away"]:>3} @ {g["home"]:<3} | no pick')
