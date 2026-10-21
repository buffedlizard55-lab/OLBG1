#!/usr/bin/env python3
"""
ccb6bde2_market_engine.py — expanded-market derivation engine (session ccb6bde2).

PURPOSE
-------
data/lines.json (model v2.0) prices only 4 market families per match
(winner / draw-no-bet / handicap / total). datasets/markets_catalog.json claims
far wider "originated" coverage (Set Betting, Correct Score, Winning Margin,
First 5 Innings, Most 180s ...) that the delivered lines file does not contain.
This engine closes the derivable part of that gap and itemises the rest.

PRINCIPLE — derivation, not invention
-------------------------------------
Every probability below is a deterministic mathematical consequence of inputs
that already exist in the verified dataset:

* p_home_2way  (two-way win probability from official ratings, model.py logit)
* margin ~ Normal(mu_margin, sigma)          (model.py SPORTS sigma)
* total  ~ Normal(mu_total,  tsigma)         (model.py SPORTS total/tsigma)
* race format  (best-of-N from the fixture's official stage string)

No new per-player statistics are introduced. Markets that cannot be derived
from those inputs without inventing a statistical rate (darts 180s, snooker
centuries, cricket top batter, tennis aces/tiebreaks, goal-scorer props ...)
are NOT priced here; they are listed in data/market_taxonomy-ccb6bde2.json
with status "investigated-not-priced" and the missing official input named.

Documented modelling assumptions used by this engine (all printed on the
Methodology page):
A1  Margin and total are independent normals. Team scores are
    (T+M)/2 and (T-M)/2, each Normal((mu_T +- mu_M)/2, sqrt(sigma_T^2 +
    sigma_M^2)/2).
A2  Race-to-N units (legs/frames/sets) are i.i.d. Bernoulli(q). q is solved
    from the match probability by inverting the negative-binomial race
    formula, so every derived scoreline is exactly consistent with the
    originated match price.
A3  tennis per-set q is obtained the same way (Bo3). Total games uses the
    exact set-count distribution times a documented 9.7 mean games/set with
    the sport's existing total sigma retained for spread.
A4  Volleyball points total = sets distribution times a documented
    44.0 mean points/set (rally scoring to 25/15), existing sigma retained.
A5  Half markets split mu by 1/2 and sigma by sqrt(2) (equal, independent
    halves). Baseball First-5 scales mu by 5/9 and sigma by sqrt(5/9).

All markets conserve probability (sum == 1 within 1e-9) and emit the same odds
triplet as model.py (book 5% overround / fair / American). Half-point lines
only: no pushes, so every market is a clean partition.
"""
from __future__ import annotations

import math

OVERROUND = 1.05


# --------------------------------------------------------------------------- 
# odds helpers (identical conventions to scripts/model.py)
# --------------------------------------------------------------------------- 
def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def to_odds(p: float) -> float:
    p = min(max(p, 0.012), 0.960)
    return round(min(max(1.0 / (p * OVERROUND), 1.02), 85.0), 2)


def to_fair_odds(p: float) -> float:
    p = min(max(p, 0.008), 0.992)
    return round(min(max(1.0 / p, 1.01), 99.0), 2)


def to_american(dec: float) -> str:
    if dec >= 2.0:
        return f"+{int(round((dec - 1.0) * 100))}"
    return f"-{int(round(100.0 / max(dec - 1.0, 0.01)))}"


def outcome(selection: str, p: float) -> dict:
    o = to_odds(p)
    f = to_fair_odds(p)
    return {
        "selection": selection,
        "probability": round(p, 6),
        "odds": o,
        "fair_odds": f,
        "american": to_american(o),
        "fair_american": to_american(f),
        "implied_pct": int(round(p * 100)),
    }


def market(key: str, name: str, line: str, pairs: list[tuple[str, float]],
           basis: str, group: str) -> dict:
    """Build one market from (selection, raw_p) pairs; renormalised to sum 1."""
    ps = [min(max(p, 1e-6), 1.0 - 1e-6) for _, p in pairs]
    s = sum(ps)
    ps = [p / s for p in ps]
    ps[-1] = 1.0 - sum(ps[:-1])
    return {
        "key": key, "name": name, "line": line, "group": group,
        "outcomes": [outcome(sel, p) for (sel, _), p in zip(pairs, ps)],
        "basis": basis,
    }


def _over_under(mu: float, sigma: float, line: float, unit: str,
                key: str, name: str, basis: str, group: str) -> dict:
    p_over = 1.0 - _norm_cdf((line + 0.0 - mu) / sigma)  # line is x.5
    return market(key, name, f"{line:.1f}",
                  [(f"Over {line:.1f} {unit}", p_over),
                   (f"Under {line:.1f} {unit}", 1.0 - p_over)],
                  basis, group)


def _handicap(mu: float, sigma: float, line: float, home: str, away: str,
              key: str, name: str, basis: str, group: str,
              unit: str = "") -> dict:
    """Home gives `line` (positive = home -line). P(home covers) = P(M > line)."""
    p_home_cover = 1.0 - _norm_cdf((line - mu) / sigma)
    hs = f"{home} {-line:+.1f}{unit}"
    as_ = f"{away} {line:+.1f}{unit}"
    return market(key, name, f"{line:.1f}",
                  [(hs, p_home_cover), (as_, 1.0 - p_home_cover)],
                  basis, group)


# --------------------------------------------------------------------------- 
# race-to-N (best-of) machinery
# --------------------------------------------------------------------------- 
def race_win_p(q: float, need: int) -> float:
    """P(win race to `need` units) with per-unit win prob q."""
    opp = 1.0 - q
    return sum(math.comb(need - 1 + k, k) * (q ** need) * (opp ** k)
               for k in range(need))


def solve_unit_p(p_match: float, need: int) -> float:
    """Invert race_win_p by bisection (monotone in q)."""
    lo, hi = 0.001, 0.999
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if race_win_p(mid, need) < p_match:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def race_scorelines(q: float, need: int) -> list[tuple[int, int, float]]:
    """[(winner_units, loser_units, p)] for the q-side winning need-k."""
    opp = 1.0 - q
    return [(need, k, math.comb(need - 1 + k, k) * (q ** need) * (opp ** k))
            for k in range(need)]


def race_markets(home: str, away: str, p_match: float, need: int,
                 unit: str, sport_key: str) -> list[dict]:
    """Correct score, total units ladder, unit handicap for a race format."""
    q = solve_unit_p(p_match, need)
    home_lines = race_scorelines(q, need)
    away_lines = race_scorelines(1.0 - q, need)
    out: list[dict] = []
    base = (f"Per-{unit[:-1]} win probability q={q:.3f} solved from the "
            f"originated match price via the race-to-{need} negative-binomial "
            f"formula (exact consistency with Match Winner)")

    # correct score
    pairs = [(f"{home} {need}-{k}", p) for _, k, p in home_lines]
    pairs += [(f"{away} {need}-{k}", p) for _, k, p in away_lines]
    out.append(market("correct_score", f"Correct Score ({unit.capitalize()})",
                      f"Race to {need}", pairs, base, "Correct Score"))

    # total units distribution
    tot: dict[int, float] = {}
    for _, k, p in home_lines + away_lines:
        tot[need + k] = tot.get(need + k, 0.0) + p
    exp_units = sum(n * p for n, p in tot.items())
    for line in sorted({need + k - 0.5 for k in range(need)}):
        p_over = sum(p for n, p in tot.items() if n > line)
        if 0.02 < p_over < 0.98:
            out.append(market(f"total_{unit}_{line}", f"Total {unit.capitalize()}",
                              f"{line:.1f}",
                              [(f"Over {line:.1f} {unit}", p_over),
                               (f"Under {line:.1f} {unit}", 1.0 - p_over)],
                              base + f"; E[units]={exp_units:.2f}", "Totals"))

    # unit handicap ladder from exact scoreline distribution
    all_scores = [(need, k, p) for _, k, p in home_lines] + \
                 [(k, need, p) for _, k, p in away_lines]
    for hl in (0.5, 1.5, 2.5, 3.5):
        if hl > need:
            continue
        p_home_cover = sum(p for h, a, p in all_scores if (h - a) > hl) \
            if p_match >= 0.5 else sum(p for h, a, p in all_scores if (h - a) > -hl)
        signed = hl if p_match >= 0.5 else -hl
        if 0.02 < p_home_cover < 0.98:
            out.append(market(f"{unit}_handicap_{hl}", f"{unit.capitalize()} Handicap",
                              f"{hl:.1f}",
                              [(f"{home} {-signed:+.1f}", p_home_cover),
                               (f"{away} {signed:+.1f}", 1.0 - p_home_cover)],
                              base, "Handicaps"))
    return out


# --------------------------------------------------------------------------- 
# margin / total (normal) machinery
# --------------------------------------------------------------------------- 
MARGIN_BANDS = {
    "basketball": [(1, 2), (3, 5), (6, 10), (11, 15), (16, 20), (21, 999)],
    "rugby-union": [(1, 7), (8, 14), (15, 21), (22, 28), (29, 999)],
    "rugby-league": [(1, 6), (7, 12), (13, 18), (19, 24), (25, 999)],
    "handball": [(1, 2), (3, 4), (5, 6), (7, 8), (9, 999)],
    "aussie-rules": [(1, 9), (10, 19), (20, 29), (30, 39), (40, 999)],
    "gaelic-football": [(1, 3), (4, 6), (7, 9), (10, 12), (13, 999)],
    "ice-hockey": [(1, 1), (2, 2), (3, 3), (4, 999)],
    "baseball": [(1, 1), (2, 2), (3, 3), (4, 4), (5, 999)],
    "cricket": [(1, 10), (11, 25), (26, 50), (51, 75), (76, 999)],
    "esports": [(1, 5), (6, 10), (11, 15), (16, 999)],
}


def margin_markets(home: str, away: str, mu_m: float, sig_m: float,
                   mu_t: float | None, sig_t: float | None,
                   sport: str, cfg: dict, draws: bool) -> list[dict]:
    out: list[dict] = []
    nbasis = (f"Margin ~ N({mu_m:+.1f}, {sig_m:.1f}) from the originated "
              f"winner probability and the sport's documented sigma")

    # winning-margin bands (6-way style: home bands + draw-if-applicable + away bands)
    bands = MARGIN_BANDS.get(sport)
    if bands:
        pairs: list[tuple[str, float]] = []
        for lo, hi in bands:
            top = 99.0 if hi == 999 else hi + 0.5
            p = _norm_cdf((top - mu_m) / sig_m) - _norm_cdf(((lo - 0.5) - mu_m) / sig_m)
            lab = f"{lo}+" if hi == 999 else (f"{lo}" if lo == hi else f"{lo}-{hi}")
            pairs.append((f"{home} by {lab}", max(p, 1e-6)))
        if draws:
            p_draw = _norm_cdf((0.5 - mu_m) / sig_m) - _norm_cdf((-0.5 - mu_m) / sig_m)
            pairs.append(("Draw", max(p_draw, 1e-6)))
        for lo, hi in reversed(bands):
            bot = -99.0 if hi == 999 else -(hi + 0.5)
            p = _norm_cdf((-(lo - 0.5) - mu_m) / sig_m) - _norm_cdf((bot - mu_m) / sig_m)
            lab = f"{lo}+" if hi == 999 else (f"{lo}" if lo == hi else f"{lo}-{hi}")
            pairs.append((f"{away} by {lab}", max(p, 1e-6)))
        out.append(market("winning_margin", "Winning Margin", "", pairs,
                          nbasis, "Winning Margin"))

    # alternate handicap ladder (centred on the originated line)
    fair_line = math.floor(abs(mu_m) * 2) / 2 + 0.5
    step = _ladder_step(sport, sig_m)
    for off in (-2, -1, 0, 1, 2):
        hl = max(0.5, fair_line + off * step)
        signed = hl if mu_m >= 0 else -hl
        out.append(_handicap(mu_m, sig_m, signed, home, away,
                             f"alt_handicap_{signed}", cfg["handicap_name"] + " (Alt)",
                             nbasis, "Handicaps"))

    # totals ladder + team totals
    if mu_t is not None and sig_t is not None:
        tstep = _ladder_step(sport, sig_t, total=True)
        base_line = math.floor(mu_t) + 0.5 if float(mu_t).is_integer() or True else mu_t
        base_line = round(mu_t) - 0.5 if mu_t == int(mu_t) else math.floor(mu_t) + 0.5
        tbasis = (f"Total ~ N({mu_t:.1f}, {sig_t:.1f}); competition baseline "
                  f"documented in model.py")
        for off in (-2, -1, 0, 1, 2):
            ln = base_line + off * tstep
            out.append(_over_under(mu_t, sig_t, ln, cfg["total_name"].lower(),
                                   f"alt_total_{ln}", "Match Total (Alt)",
                                   tbasis, "Totals"))
        # team totals from A1 decomposition
        sig_team = math.sqrt(sig_t ** 2 + sig_m ** 2) / 2.0
        for team, mu_team, tag in ((home, (mu_t + mu_m) / 2.0, "home"),
                                   (away, (mu_t - mu_m) / 2.0, "away")):
            ln = math.floor(mu_team) + 0.5
            out.append(_over_under(mu_team, sig_team, ln,
                                   cfg["total_name"].lower(),
                                   f"team_total_{tag}", f"{team} Team Total",
                                   "Assumption A1: team score=(Total+/-Margin)/2, "
                                   "independent normals", "Team Totals"))

    # first-half markets (A5) for period sports
    if sport in ("basketball", "rugby-union", "rugby-league", "handball"):
        h_mu, h_sig = mu_m / 2.0, sig_m / math.sqrt(2)
        p_h1 = 1.0 - _norm_cdf((0.0 - h_mu) / h_sig)
        pairs = [(f"{home} (1st Half)", p_h1)]
        if draws:
            pd_ = _norm_cdf((0.5 - h_mu) / h_sig) - _norm_cdf((-0.5 - h_mu) / h_sig)
            pa = _norm_cdf((-0.5 - h_mu) / h_sig)
            ph = 1.0 - _norm_cdf((0.5 - h_mu) / h_sig)
            pairs = [(f"{home} (1st Half)", max(ph, 1e-6)),
                     ("Draw (1st Half)", max(pd_, 1e-6)),
                     (f"{away} (1st Half)", max(pa, 1e-6))]
        else:
            pairs.append((f"{away} (1st Half)", 1.0 - p_h1))
        out.append(market("first_half_winner", "1st Half Winner", "", pairs,
                          "Assumption A5: halves split mu evenly, sigma/sqrt(2)",
                          "Half Markets"))
        if mu_t is not None and sig_t is not None:
            ln = math.floor(mu_t / 2.0) + 0.5
            out.append(_over_under(mu_t / 2.0, sig_t / math.sqrt(2), ln,
                                   cfg["total_name"].lower(),
                                   "first_half_total", "1st Half Total",
                                   "Assumption A5: halves split mu evenly, sigma/sqrt(2)",
                                   "Half Markets"))
    return out


def _ladder_step(sport: str, sigma: float, total: bool = False) -> float:
    if sigma >= 25:
        return 10.0
    if sigma >= 12:
        return 5.0
    if sigma >= 6:
        return 2.0
    if sigma >= 3:
        return 1.0
    return 0.5


# --------------------------------------------------------------------------- 
# sport-specific expansions
# --------------------------------------------------------------------------- 
def hockey_regulation(home: str, away: str, mu_m: float, sig_m: float,
                      p_home_incl_ot: float) -> list[dict]:
    """60-minute 3-way + OT yes/no from the margin distribution."""
    p_draw = _norm_cdf((0.5 - mu_m) / sig_m) - _norm_cdf((-0.5 - mu_m) / sig_m)
    p_home_reg = 1.0 - _norm_cdf((0.5 - mu_m) / sig_m)
    p_away_reg = _norm_cdf((-0.5 - mu_m) / sig_m)
    basis = ("Continuity-corrected normal margin: regulation draw = |margin| < 0.5 "
             "goals; money line (incl. OT/SO) remains the originated v2 market")
    return [
        market("regulation_3way", "60-Minute Result (3-Way)", "Regulation",
               [(f"{home} (Reg)", p_home_reg), ("Draw (Reg)", p_draw),
                (f"{away} (Reg)", p_away_reg)], basis, "Regulation"),
        market("overtime_yes_no", "Game to Overtime", "",
               [("Yes — overtime/shootout", p_draw), ("No — decided in regulation", 1 - p_draw)],
               basis, "Regulation"),
    ]


def baseball_f5(home: str, away: str, mu_m: float, sig_m: float,
                mu_t: float, sig_t: float) -> list[dict]:
    f = 5.0 / 9.0
    mu5, sig5 = mu_m * f, sig_m * math.sqrt(f)
    p_home5 = 1.0 - _norm_cdf((0.5 - mu5) / sig5)
    p_draw5 = _norm_cdf((0.5 - mu5) / sig5) - _norm_cdf((-0.5 - mu5) / sig5)
    p_away5 = _norm_cdf((-0.5 - mu5) / sig5)
    basis = ("Assumption A5: first 5 innings carry 5/9 of run expectation, "
             "sigma scaled by sqrt(5/9)")
    ln = math.floor(mu_t * f) + 0.5
    return [
        market("f5_winner", "First 5 Innings (3-Way)", "F5",
               [(f"{home} (F5)", p_home5), ("Tied (F5)", p_draw5),
                (f"{away} (F5)", p_away5)], basis, "First 5 Innings"),
        _over_under(mu_t * f, sig_t * math.sqrt(f), ln, "runs",
                    "f5_total", "First 5 Innings Total", basis, "First 5 Innings"),
    ]


def cricket_innings(home: str, away: str, mu_t: float, sig_t: float) -> list[dict]:
    """1st-innings total: innings assumed to split match runs evenly (A1-style)."""
    mu_i, sig_i = mu_t / 2.0, sig_t / math.sqrt(2)
    ln = math.floor(mu_i) + 0.5
    return [
        _over_under(mu_i, sig_i, ln, "runs", "first_innings_total",
                    "1st Innings Total Runs",
                    "Assumption: innings totals iid, match total = sum of two "
                    "innings (mu/2, sigma/sqrt(2)); batting side unknown pre-toss",
                    "Innings Markets"),
    ]


def tennis_markets(home: str, away: str, p_match: float,
                   mu_t: float, sig_t: float) -> list[dict]:
    """Set betting + 1st set + total sets + total games (Bo3, assumption A3)."""
    q = solve_unit_p(p_match, 2)  # per-set win prob for the 'home' player
    p20 = q * q
    p21 = 2 * q * q * (1 - q)
    p12 = 2 * q * (1 - q) * (1 - q)
    p02 = (1 - q) * (1 - q)
    basis = (f"Per-set win probability q={q:.3f} inverted from the match price "
             f"(Bo3): P(match)=q^2(3-2q). Sets assumed independent (A3)")
    out = [
        market("set_betting", "Set Betting", "Bo3",
               [(f"{home} 2-0", p20), (f"{home} 2-1", p21),
                (f"{away} 2-1", p12), (f"{away} 2-0", p02)], basis, "Set Markets"),
        market("first_set_winner", "1st Set Winner", "",
               [(home, q), (away, 1 - q)], basis, "Set Markets"),
        market("total_sets", "Total Sets", "2.5",
               [("Over 2.5 sets", p21 + p12), ("Under 2.5 sets", p20 + p02)],
               basis, "Set Markets"),
        market("both_win_set", "Both Players Win a Set", "",
               [("Yes", p21 + p12), ("No", p20 + p02)], basis, "Set Markets"),
    ]
    # total games: expected sets x 9.7 games/set (A3), keep model total as anchor blend
    exp_sets = 2 * (p20 + p02) + 3 * (p21 + p12)
    mu_games = 0.5 * mu_t + 0.5 * (exp_sets * 9.7)
    for ln in (20.5, 21.5, 22.5, 23.5):
        out.append(_over_under(mu_games, sig_t, ln, "games", f"total_games_{ln}",
                               "Total Games",
                               "A3: E[games]=E[sets]x9.7 blended 50/50 with the "
                               "documented competition baseline; sigma as model.py",
                               "Totals"))
    return out


def volleyball_points(home: str, away: str, p_match: float,
                      sig_t: float) -> list[dict]:
    """Total points ladder from the exact set-count distribution (A4)."""
    q = solve_unit_p(p_match, 3)
    dist: dict[int, float] = {}
    for _, k, p in race_scorelines(q, 3) + race_scorelines(1 - q, 3):
        dist[3 + k] = dist.get(3 + k, 0.0) + p
    exp_sets = sum(n * p for n, p in dist.items())
    mu_pts = exp_sets * 44.0
    out = []
    base_line = math.floor(mu_pts) + 0.5
    for off in (-10.0, 0.0, 10.0):
        out.append(_over_under(mu_pts, sig_t, base_line + off, "points",
                               f"total_points_{base_line + off}", "Total Match Points",
                               "A4: exact set distribution (race to 3) x 44.0 mean "
                               "points/set; sigma as model.py", "Totals"))
    return out
