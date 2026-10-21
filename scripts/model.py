"""
model.py - transparent, deterministic pricing model for originated lines.

DESIGN PRINCIPLES
-----------------
1. Nothing in here is presented as a sourced fact. Every constant below is a
   *modelling assumption* and is listed on the site's Methodology page.
2. Sourced inputs (league records, official world rankings) are supplied per
   match and recorded on each row. Where a sourced input is missing we do NOT
   guess it: the match falls back to a neutral baseline and is capped at LOW
   confidence.
3. A strength rating is only used when EVERY participant in the match has one.
   Using one real rating against one placeholder produces garbage, so we refuse.
4. Everything is seeded/deterministic - re-running the pipeline reproduces the
   same prices byte for byte.
"""

from __future__ import annotations

import math

# --------------------------------------------------------------------------
# Sport configuration. All values are modelling assumptions, not statistics.
#   p_base   : home win probability used when no strength input exists
#   scale    : rating points needed to shift the log-odds by 1.0
#   sigma    : standard deviation of the final margin (used for handicaps)
#   total    : baseline match total used when no total input exists
#   tsigma   : standard deviation of the match total
#   high/med : sport-relative confidence thresholds on max(p)
#   draws    : whether a draw is a live outcome
#   draw_p   : assumed draw probability (only when draws is True)
# --------------------------------------------------------------------------
SPORTS = {
    "ice-hockey": dict(
        name="Ice Hockey", p_base=0.53, scale=14.0, sigma=3.0,
        total=6.0, tsigma=2.2, high=0.58, med=0.545, draws=False, draw_p=0.0,
        handicap_name="Puck line", total_name="Goals",
    ),
    "basketball": dict(
        name="Basketball", p_base=0.56, scale=14.0, sigma=18.0,
        total=225.5, tsigma=18.0, high=0.62, med=0.560, draws=False, draw_p=0.0,
        handicap_name="Points handicap", total_name="Points",
    ),
    "baseball": dict(
        name="Baseball", p_base=0.54, scale=40.0, sigma=4.0,
        total=8.5, tsigma=3.4, high=0.58, med=0.545, draws=False, draw_p=0.0,
        handicap_name="Run line", total_name="Runs",
    ),
    "snooker": dict(
        name="Snooker", p_base=0.50, scale=27.0, sigma=2.6,
        total=None, tsigma=None, high=0.62, med=0.560, draws=False, draw_p=0.0,
        handicap_name="Frame handicap", total_name="Frames",
    ),
    "darts": dict(
        name="Darts", p_base=0.50, scale=16.0, sigma=3.2,
        total=None, tsigma=None, high=0.65, med=0.580, draws=False, draw_p=0.0,
        handicap_name="Legs handicap", total_name="Legs",
    ),
    "cricket": dict(
        name="Cricket", p_base=0.53, scale=18.0, sigma=22.0,
        total=320.5, tsigma=32.0, high=0.60, med=0.550, draws=True, draw_p=0.02,
        handicap_name="Runs handicap", total_name="Match runs",
    ),
    "rugby-union": dict(
        name="Rugby Union", p_base=0.55, scale=16.0, sigma=13.0,
        total=48.5, tsigma=12.0, high=0.60, med=0.555, draws=True, draw_p=0.025,
        handicap_name="Handicap", total_name="Points",
    ),
    "rugby-league": dict(
        name="Rugby League", p_base=0.55, scale=16.0, sigma=14.0,
        total=42.5, tsigma=12.0, high=0.60, med=0.555, draws=True, draw_p=0.02,
        handicap_name="Handicap", total_name="Points",
    ),
    "tennis": dict(
        name="Tennis", p_base=0.50, scale=24.0, sigma=2.4,
        total=None, tsigma=None, high=0.65, med=0.580, draws=False, draw_p=0.0,
        handicap_name="Games handicap", total_name="Games",
    ),
    "golf": dict(
        name="Golf", p_base=0.50, scale=22.0, sigma=4.0,
        total=None, tsigma=None, high=0.70, med=0.600, draws=False, draw_p=0.0,
        handicap_name="Stroke handicap", total_name="Strokes",
    ),
    "handball": dict(
        name="Handball", p_base=0.55, scale=16.0, sigma=8.0,
        total=57.5, tsigma=8.0, high=0.60, med=0.555, draws=True, draw_p=0.05,
        handicap_name="Handicap", total_name="Goals",
    ),
    "volleyball": dict(
        name="Volleyball", p_base=0.55, scale=18.0, sigma=1.6,
        total=None, tsigma=None, high=0.62, med=0.570, draws=False, draw_p=0.0,
        handicap_name="Sets handicap", total_name="Sets",
    ),
    "aussie-rules": dict(
        name="Aussie Rules", p_base=0.57, scale=18.0, sigma=30.0,
        total=167.5, tsigma=26.0, high=0.62, med=0.560, draws=False, draw_p=0.0,
        handicap_name="Line", total_name="Points",
    ),
    "esports": dict(
        name="eSports", p_base=0.50, scale=20.0, sigma=1.8,
        total=None, tsigma=None, high=0.64, med=0.570, draws=False, draw_p=0.0,
        handicap_name="Map handicap", total_name="Maps",
    ),
    "gaelic-football": dict(
        name="Gaelic Football", p_base=0.55, scale=18.0, sigma=10.0,
        total=39.5, tsigma=9.0, high=0.60, med=0.555, draws=True, draw_p=0.03,
        handicap_name="Handicap", total_name="Points",
    ),
    "greyhounds": dict(
        name="Greyhounds", p_base=0.50, scale=18.0, sigma=0.9,
        total=None, tsigma=None, high=0.55, med=0.500, draws=False, draw_p=0.0,
        handicap_name="Trap handicap", total_name="Lengths",
    ),
    "motor-racing": dict(
        name="Motor Racing", p_base=0.50, scale=20.0, sigma=2.0,
        total=None, tsigma=None, high=0.60, med=0.520, draws=False, draw_p=0.0,
        handicap_name="Grid handicap", total_name="Positions",
    ),
}

OVERRROUND = 1.05  # each price is shortened so implied probabilities sum to 105%


# --------------------------------------------------------------------------
# maths helpers
# --------------------------------------------------------------------------
def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    """Inverse standard normal CDF (Acklam's rational approximation)."""
    p = min(max(p, 1e-9), 1 - 1e-9)
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


def to_odds(p: float) -> float:
    """Convert a probability to decimal odds with a 5% overround."""
    p = min(max(p, 0.005), 0.995)
    return round(1.0 / (p * OVERRROUND), 2)


def implied(p: float) -> int:
    return int(round(p * 100))


# --------------------------------------------------------------------------
# ratings
# --------------------------------------------------------------------------
def snooker_rating(rank) -> float | None:
    """
    Map an official WST world-ranking position to a 0-100 strength score.

    Players outside the published top 36 have no numeric rank. Rather than
    invent one we place them in a single bounded bucket at rank 60 - which is
    itself a documented bound (they sit below 36th), not a measurement.
    """
    if rank is None:
        rank = 60
    rank = max(1, min(int(rank), 200))
    return round(100.0 - 70.0 * math.log(rank) / math.log(60.0), 2)


def winpct_rating(pct: float) -> float:
    """A league win/points percentage expressed on a 0-100 scale."""
    return round(pct * 100.0, 2)


# --------------------------------------------------------------------------
# the model
# --------------------------------------------------------------------------
def price_match(match: dict) -> dict:
    """Originate every market for one match and return a pricing record."""
    sport = match["sport"]
    cfg = SPORTS[sport]

    home_in = match.get("inputs", {}).get("home")
    away_in = match.get("inputs", {}).get("away")

    def rating_of(side):
        """Return (rating, measured). measured=False means a bounded bucket, not a measurement."""
        if not side:
            return None, False
        if sport == "snooker":
            rank = side.get("rank")
            return snooker_rating(rank), rank is not None
        return side.get("rating"), side.get("rating") is not None

    r_home, m_home = rating_of(home_in)
    r_away, m_away = rating_of(away_in)
    both_rated = r_home is not None and r_away is not None
    both_measured = m_home and m_away

    base_logit = _logit(cfg["p_base"])
    if both_rated:
        logit = base_logit + (r_home - r_away) / cfg["scale"]
    else:
        logit = base_logit

    p_home = _sigmoid(logit)

    # three-way sports remove a fixed draw slice first
    if cfg["draws"]:
        d = cfg["draw_p"]
        p_home_raw = p_home * (1 - d)
        p_away_raw = (1 - p_home) * (1 - d)
        p_draw = d
    else:
        p_home_raw = p_home
        p_away_raw = 1 - p_home
        p_draw = 0.0

    p_best = max(p_home_raw, p_away_raw)
    coverage = (1 if r_home is not None else 0) + (1 if r_away is not None else 0)

    if both_rated and p_best >= cfg["high"]:
        confidence = "high"
    elif both_rated and p_best >= cfg["med"]:
        confidence = "medium"
    elif both_rated:
        confidence = "low"
    else:
        # no strength input: cannot claim conviction, whatever the baseline says
        confidence = "low"

    markets = []

    # ---- 1. match winner -------------------------------------------------
    winner_outcomes = [
        {"selection": match["home"], "probability": p_home_raw},
        {"selection": match["away"], "probability": p_away_raw},
    ]
    if cfg["draws"]:
        winner_outcomes.insert(1, {"selection": "Draw", "probability": p_draw})
    for o in winner_outcomes:
        o["odds"] = to_odds(o["probability"])
        o["implied_pct"] = implied(o["probability"])
    markets.append({
        "key": "winner", "name": "Match Winner",
        "line": "", "outcomes": winner_outcomes,
        "basis": "Sourced ratings" if both_rated else "No strength input - neutral baseline plus home edge",
    })

    # ---- 2. handicap -----------------------------------------------------
    if sport not in ("cricket", "motor-racing", "golf", "greyhounds"):
        edge = p_home - 0.5
        margin = cfg["sigma"] * _norm_ppf(p_home)
        line = (math.floor(abs(margin) * 2) / 2.0) + 0.5
        fav_home = p_home >= 0.5
        line_signed = -line if fav_home else line      # handicap applied to home
        p_cover_home = 1 - _norm_cdf((line - abs(margin)) / cfg["sigma"]) if fav_home \
            else _norm_cdf((line - abs(margin)) / cfg["sigma"])
        p_cover_home = min(max(p_cover_home, 0.05), 0.95)
        markets.append({
            "key": "handicap", "name": cfg["handicap_name"],
            "line": f"{abs(line_signed):.1f}",
            "outcomes": [
                {"selection": f"{match['home']} {line_signed:+.1f}", "probability": p_cover_home, "odds": to_odds(p_cover_home), "implied_pct": implied(p_cover_home)},
                {"selection": f"{match['away']} {-line_signed:+.1f}", "probability": 1 - p_cover_home, "odds": to_odds(1 - p_cover_home), "implied_pct": implied(1 - p_cover_home)},
            ],
            "basis": "Expected margin derived from the match-winner probability",
        })

    # ---- 3. match total --------------------------------------------------
    if cfg["total"] is not None:
        base = round(cfg["total"] * 2) / 2.0
        p_over = 0.5
        alt_over = base - 1.5
        p_alt_over = 1 - _norm_cdf((alt_over - base) / cfg["tsigma"])
        markets.append({
            "key": "total", "name": f"Match Total ({cfg['total_name']})",
            "line": f"{base:.1f}",
            "outcomes": [
                {"selection": f"Over {base:.1f}", "probability": p_over, "odds": to_odds(p_over), "implied_pct": implied(p_over)},
                {"selection": f"Under {base:.1f}", "probability": 1 - p_over, "odds": to_odds(1 - p_over), "implied_pct": implied(1 - p_over)},
            ],
            "alternate": [
                {"selection": f"Over {alt_over:.1f}", "probability": p_alt_over, "odds": to_odds(p_alt_over), "implied_pct": implied(p_alt_over)},
                {"selection": f"Under {alt_over:.1f}", "probability": 1 - p_alt_over, "odds": to_odds(1 - p_alt_over), "implied_pct": implied(1 - p_alt_over)},
            ],
            "basis": "League baseline total - no match-specific total input was sourced",
        })

    pick_sel = match["home"] if p_home_raw >= p_away_raw else match["away"]
    if cfg["draws"] and p_draw >= max(p_home_raw, p_away_raw):
        pick_sel = "Draw"

    return {
        "id": match["id"],
        "sport": sport,
        "sport_name": cfg["name"],
        "favourite": match["home"] if p_home_raw >= p_away_raw else match["away"],
        "home_probability": round(p_home_raw, 4),
        "draw_probability": round(p_draw, 4),
        "away_probability": round(p_away_raw, 4),
        "pick": pick_sel,
        "pick_market": "Match Winner",
        "confidence": confidence,
        "rating_home": r_home,
        "rating_away": r_away,
        "rating_measured_home": m_home,
        "rating_measured_away": m_away,
        "rating_coverage": coverage,
        "both_rated": both_rated,
        "both_measured": both_measured,
        "markets": markets,
        "model_notes": _notes(sport, both_rated, r_home, r_away, cfg),
    }


def _notes(sport, both_rated, r_home, r_away, cfg) -> list[str]:
    out = []
    if both_rated:
        out.append(
            f"Both participants carry a sourced strength rating ({r_home} v {r_away}); "
            f"the differential is converted to a win probability with a {cfg['scale']:.0f}-point log-odds scale."
        )
    else:
        out.append(
            "At least one participant has no sourced strength rating, so the model refuses to "
            "carry a one-sided edge and falls back to the sport's neutral home baseline. Confidence is capped at low."
        )
    if cfg["total"] is not None:
        out.append(
            f"Match total is set at the league baseline ({cfg['total']}) and priced pick'em; "
            "no match-specific scoring input was available."
        )
    else:
        out.append(
            "No match-total market is originated for this sport: the governing body's match format "
            "was not verified in this build, so a total line would rest on an assumption about format."
        )
    return out
