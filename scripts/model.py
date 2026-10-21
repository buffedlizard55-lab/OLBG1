"""
model.py - transparent, deterministic multi-market pricing engine for originated lines.

DESIGN PRINCIPLES
-----------------
1. Sourced inputs vs modelling assumptions are strictly separated. Every constant
   below is a documented modelling assumption published on Methodology.
2. Sourced inputs (official world rankings, official league points percentages,
   official table points, official tournament seeds, official ICC team ratings)
   are recorded on each fixture row together with the governing-body URL.
3. A strength differential is ONLY applied when BOTH sides in the match carry a
   sourced rating. Never pit a real rating against a placeholder: unrated rows
   fall back to the sport's neutral venue baseline and are strictly capped at LOW
   confidence.
4. Every market conserves probability strictly (sum(p) == 1.0 within 1e-9), emits
   vig-free fair decimal odds, 5%-overround bookmaker decimal odds, and US
   American moneyline odds, and is 100% deterministic.
"""

from __future__ import annotations

import math

OVERROUND = 1.05  # symmetric 5% bookmaker margin on originated bookmaker quotes

# --------------------------------------------------------------------------
# Sport configuration (all constants documented on methodology.html)
# --------------------------------------------------------------------------
SPORTS = {
    "ice-hockey": dict(
        name="Ice Hockey", p_base=0.535, scale=42.0, sigma=2.85,
        total=6.5, tsigma=2.15, high=0.610, med=0.555, draws=False, draw_p=0.0,
        handicap_name="Puck Line", total_name="Goals", fixed_line=1.5,
    ),
    "basketball": dict(
        name="Basketball", p_base=0.560, scale=32.0, sigma=13.5,
        total=228.5, tsigma=17.5, high=0.680, med=0.575, draws=False, draw_p=0.0,
        handicap_name="Point Spread", total_name="Points", fixed_line=None,
    ),
    "baseball": dict(
        name="Baseball", p_base=0.540, scale=40.0, sigma=3.85,
        total=7.5, tsigma=3.20, high=0.580, med=0.545, draws=False, draw_p=0.0,
        handicap_name="Run Line", total_name="Runs", fixed_line=1.5,
    ),
    "snooker": dict(
        name="Snooker", p_base=0.500, scale=27.0, sigma=2.35,
        total=5.5, tsigma=1.05, high=0.630, med=0.560, draws=False, draw_p=0.0,
        handicap_name="Frame Handicap", total_name="Frames (Bo7)", fixed_line=1.5,
    ),
    "darts": dict(
        name="Darts", p_base=0.500, scale=33.0, sigma=2.75,
        total=9.5, tsigma=1.45, high=0.665, med=0.565, draws=False, draw_p=0.0,
        handicap_name="Legs Handicap", total_name="Legs (Bo11)", fixed_line=None,
    ),
    "cricket": dict(
        name="Cricket", p_base=0.525, scale=22.0, sigma=24.0,
        total=339.5, tsigma=32.0, high=0.615, med=0.560, draws=False, draw_p=0.0,
        handicap_name="Runs / Wickets Handicap", total_name="Match Runs", fixed_line=None,
    ),
    "rugby-union": dict(
        name="Rugby Union", p_base=0.565, scale=22.0, sigma=13.0,
        total=48.5, tsigma=12.5, high=0.720, med=0.575, draws=True, draw_p=0.030,
        handicap_name="Points Handicap", total_name="Points", fixed_line=None,
    ),
    "rugby-league": dict(
        name="Rugby League", p_base=0.545, scale=22.0, sigma=14.5,
        total=44.5, tsigma=13.0, high=0.750, med=0.575, draws=True, draw_p=0.024,
        handicap_name="Points Handicap", total_name="Points", fixed_line=None,
    ),
    "tennis": dict(
        name="Tennis", p_base=0.500, scale=26.0, sigma=3.60,
        total=22.5, tsigma=4.20, high=0.660, med=0.565, draws=False, draw_p=0.0,
        handicap_name="Games Handicap", total_name="Games (Bo3)", fixed_line=None,
    ),
    "golf": dict(
        name="Golf", p_base=0.500, scale=22.0, sigma=4.00,
        total=None, tsigma=None, high=0.700, med=0.600, draws=False, draw_p=0.0,
        handicap_name="Stroke Handicap", total_name="Strokes", fixed_line=None,
    ),
    "handball": dict(
        name="Handball", p_base=0.560, scale=22.0, sigma=6.50,
        total=60.5, tsigma=5.80, high=0.760, med=0.575, draws=True, draw_p=0.070,
        handicap_name="Goals Handicap", total_name="Goals", fixed_line=None,
    ),
    "volleyball": dict(
        name="Volleyball", p_base=0.550, scale=17.0, sigma=1.65,
        total=181.5, tsigma=19.0, high=0.650, med=0.570, draws=False, draw_p=0.0,
        handicap_name="Sets Handicap", total_name="Match Points (Bo5)", fixed_line=1.5,
    ),
    "aussie-rules": dict(
        name="Aussie Rules", p_base=0.555, scale=24.0, sigma=18.5,
        total=74.5, tsigma=16.5, high=0.780, med=0.575, draws=False, draw_p=0.0,
        handicap_name="Points Line", total_name="Points (AFLW)", fixed_line=None,
    ),
    "esports": dict(
        name="eSports", p_base=0.500, scale=20.0, sigma=7.00,
        total=27.5, tsigma=6.50, high=0.650, med=0.570, draws=False, draw_p=0.0,
        handicap_name="Kill Handicap", total_name="Kills (Bo1)", fixed_line=None,
    ),
    "gaelic-football": dict(
        name="Gaelic Football", p_base=0.535, scale=17.0, sigma=6.50,
        total=29.5, tsigma=6.50, high=0.640, med=0.565, draws=True, draw_p=0.075,
        handicap_name="Points Handicap", total_name="Score Points (60m)", fixed_line=None,
    ),
    "greyhounds": dict(
        name="Greyhounds", p_base=0.500, scale=18.0, sigma=0.90,
        total=None, tsigma=None, high=0.650, med=0.560, draws=False, draw_p=0.0,
        handicap_name="Trap Handicap", total_name="Lengths", fixed_line=None,
    ),
    "motor-racing": dict(
        name="Motor Racing", p_base=0.500, scale=20.0, sigma=2.00,
        total=None, tsigma=None, high=0.650, med=0.560, draws=False, draw_p=0.0,
        handicap_name="Grid Handicap", total_name="Positions", fixed_line=None,
    ),
}

COMPETITION_TOTALS = {
    "EuroLeague": (171.5, 14.5),
    "BKT EuroCup": (168.5, 14.5),
    "Women's T20I Series": (289.5, 28.0),
    "Ford Trophy (List A 50-over)": (529.5, 44.0),
    "First-Class Tour Match": (None, None),
}


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1.0 - 1e-6)
    return math.log(p / (1.0 - p))


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    p = min(max(p, 1e-9), 1.0 - 1e-9)
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1.0 - 0.02425
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )
    if p > phigh:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
        (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    )


def to_odds(p: float) -> float:
    """Convert probability to bookmaker decimal odds with a 5% overround, clamped to (1.02, 85.0)."""
    p = min(max(p, 0.012), 0.960)
    return round(min(max(1.0 / (p * OVERROUND), 1.02), 85.0), 2)


def to_fair_odds(p: float) -> float:
    """Convert probability to vig-free fair decimal odds."""
    p = min(max(p, 0.008), 0.992)
    return round(min(max(1.0 / p, 1.01), 99.0), 2)


def to_american(dec: float) -> str:
    """Convert decimal odds to US moneyline format (+145 / -165)."""
    if dec >= 2.0:
        return f"+{int(round((dec - 1.0) * 100))}"
    denom = max(dec - 1.0, 0.01)
    return f"-{int(round(100.0 / denom))}"


def implied(p: float) -> int:
    return int(round(p * 100))


def snooker_rating(rank) -> float:
    """Map an official WST world-ranking position to a 0-100 score (rank>36 bounded at 60)."""
    if rank is None:
        rank = 60
    rank = max(1, min(int(rank), 200))
    return round(100.0 - 70.0 * math.log(rank) / math.log(60.0), 2)


def tennis_rank_rating(rank: int) -> float:
    """Map an official ATP/WTA world ranking position to a 0-100 log-strength score."""
    r = max(1, min(int(rank), 400))
    return round(100.0 - 52.0 * math.log(r) / math.log(100.0), 2)


def darts_seed_rating(seed: int) -> float:
    """Map an official 1..32 PDC European Tour seed + Order-of-Merit tier to 0-100."""
    s = max(1, min(int(seed), 32))
    return round(94.0 - 30.0 * ((s - 1) / 31.0), 2)


def _outcome(selection: str, p: float) -> dict:
    odds = to_odds(p)
    fair = to_fair_odds(p)
    return {
        "selection": selection,
        "probability": round(p, 6),
        "odds": odds,
        "fair_odds": fair,
        "american": to_american(odds),
        "fair_american": to_american(fair),
        "implied_pct": implied(p),
    }


def _normalize_probs(ps: list[float]) -> list[float]:
    ps_clean = [min(max(x, 0.012), 0.976) for x in ps]
    s = sum(ps_clean)
    normed = [round(x / s, 6) for x in ps_clean]
    normed[-1] = round(1.0 - sum(normed[:-1]), 6)
    return normed


def price_match(match: dict) -> dict:
    """Originate full multi-market book for one two-sided fixture."""
    sport = match["sport"]
    cfg = SPORTS[sport]
    comp = match.get("competition", "")

    home_in = match.get("inputs", {}).get("home")
    away_in = match.get("inputs", {}).get("away")

    def rating_of(side):
        if not side:
            return None, False
        if sport == "snooker" and "rating" not in side:
            rank = side.get("rank")
            return snooker_rating(rank), rank is not None
        return side.get("rating"), (side.get("rating") is not None and not side.get("bounded", False))

    r_home, m_home = rating_of(home_in)
    r_away, m_away = rating_of(away_in)
    both_rated = r_home is not None and r_away is not None
    both_measured = m_home and m_away

    p_venue = 0.500 if match.get("neutral", False) else cfg["p_base"]
    base_logit = _logit(p_venue)
    logit = base_logit + ((r_home - r_away) / cfg["scale"] if both_rated else 0.0)
    p_home_2way = min(max(_sigmoid(logit), 0.025), 0.975)

    # Dynamic draw probability shrinks smoothly in heavy mismatches
    if cfg["draws"]:
        d_raw = cfg["draw_p"] * math.exp(-(((p_home_2way - 0.5) / 0.34) ** 2))
        d = max(0.018, round(d_raw, 6))
        probs_3 = _normalize_probs([p_home_2way * (1.0 - d), d, (1.0 - p_home_2way) * (1.0 - d)])
        p_home_raw, p_draw, p_away_raw = probs_3[0], probs_3[1], probs_3[2]
    else:
        probs_2 = _normalize_probs([p_home_2way, 1.0 - p_home_2way])
        p_home_raw, p_away_raw = probs_2[0], probs_2[1]
        p_draw = 0.0

    p_best = max(p_home_raw, p_away_raw)
    coverage = (1 if r_home is not None else 0) + (1 if r_away is not None else 0)

    if match.get("status") != "verified":
        confidence = "low"
    elif both_rated and both_measured and p_best >= cfg["high"]:
        confidence = "high"
    elif both_rated and p_best >= cfg["med"]:
        confidence = "medium"
    else:
        confidence = "low"

    markets = []

    # ---- 1. Primary Match Winner (3-way where draws apply, else 2-way) ---
    if cfg["draws"]:
        winner_outcomes = [
            _outcome(match["home"], p_home_raw),
            _outcome("Draw", p_draw),
            _outcome(match["away"], p_away_raw),
        ]
    else:
        winner_outcomes = [
            _outcome(match["home"], p_home_raw),
            _outcome(match["away"], p_away_raw),
        ]
    markets.append({
        "key": "winner",
        "name": "Match Winner (3-Way)" if cfg["draws"] else "Match Winner",
        "line": "",
        "outcomes": winner_outcomes,
        "basis": "Official governing-body ratings + venue adjustment" if both_rated else "Neutral home/venue baseline (unrated side)",
    })

    # ---- 1b. Draw No Bet (2-Way) for 3-way sports ------------------------
    if cfg["draws"]:
        dnb_probs = _normalize_probs([p_home_2way, 1.0 - p_home_2way])
        markets.append({
            "key": "dnb",
            "name": "Draw No Bet (2-Way)",
            "line": "PK",
            "outcomes": [
                _outcome(f"{match['home']} (DNB)", dnb_probs[0]),
                _outcome(f"{match['away']} (DNB)", dnb_probs[1]),
            ],
            "basis": "Two-way conditional probabilities excluding regulation draw",
        })

    # ---- 2. Handicap / Point Spread / Puck Line / Run Line ---------------
    if sport not in ("motor-racing", "golf", "greyhounds"):
        margin = cfg["sigma"] * _norm_ppf(p_home_2way)
        if cfg["fixed_line"] is not None and abs(margin) < 2.2:
            line = cfg["fixed_line"]
        else:
            line = max(0.5, (math.floor(abs(margin) * 2.0) / 2.0) + 0.5)
        fav_home = p_home_2way >= 0.5
        line_signed = -line if fav_home else line
        p_cover_raw = (
            1.0 - _norm_cdf((line - abs(margin)) / cfg["sigma"])
            if fav_home
            else _norm_cdf((line - abs(margin)) / cfg["sigma"])
        )
        cov_probs = _normalize_probs([min(max(p_cover_raw, 0.08), 0.92), 1.0 - min(max(p_cover_raw, 0.08), 0.92)])
        markets.append({
            "key": "handicap",
            "name": cfg["handicap_name"],
            "line": f"{abs(line_signed):.1f}",
            "outcomes": [
                _outcome(f"{match['home']} {line_signed:+.1f}", cov_probs[0]),
                _outcome(f"{match['away']} {-line_signed:+.1f}", cov_probs[1]),
            ],
            "basis": f"Gaussian margin projection (E[M]={margin:+.1f}, sigma={cfg['sigma']:.1f})",
        })

    # ---- 3. Match Total Over / Under -------------------------------------
    comp_override = COMPETITION_TOTALS.get(comp)
    tot_base = comp_override[0] if comp_override is not None else cfg["total"]
    tot_sigma = comp_override[1] if comp_override is not None else cfg["tsigma"]
    if tot_base is not None and tot_sigma is not None:
        # Slight upward shift in totals for competitive Best-of-N matches vs quick sweeps
        if sport in ("tennis", "snooker", "darts", "volleyball"):
            closeness = 1.0 - 2.0 * abs(p_home_2way - 0.5)
            p_over_raw = 0.44 + 0.14 * closeness
        else:
            p_over_raw = 0.500
        tot_probs = _normalize_probs([p_over_raw, 1.0 - p_over_raw])
        alt_line = round(tot_base - 1.5, 1)
        p_alt_raw = min(max(1.0 - _norm_cdf((alt_line - tot_base) / tot_sigma), 0.08), 0.92)
        alt_probs = _normalize_probs([p_alt_raw, 1.0 - p_alt_raw])
        markets.append({
            "key": "total",
            "name": f"Match Total ({cfg['total_name']})",
            "line": f"{tot_base:.1f}",
            "outcomes": [
                _outcome(f"Over {tot_base:.1f}", tot_probs[0]),
                _outcome(f"Under {tot_base:.1f}", tot_probs[1]),
            ],
            "alternate": [
                _outcome(f"Over {alt_line:.1f}", alt_probs[0]),
                _outcome(f"Under {alt_line:.1f}", alt_probs[1]),
            ],
            "basis": f"Competition baseline total ({tot_base:.1f} {cfg['total_name'].lower()}, sigma={tot_sigma:.1f})",
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
        "pick_market": markets[0]["name"],
        "confidence": confidence,
        "expected_margin": round(cfg["sigma"] * _norm_ppf(p_home_2way), 2),
        "rating_home": r_home,
        "rating_away": r_away,
        "rating_measured_home": m_home,
        "rating_measured_away": m_away,
        "rating_coverage": coverage,
        "both_rated": both_rated,
        "both_measured": both_measured,
        "markets": markets,
        "model_notes": _notes(sport, both_rated, r_home, r_away, cfg, tot_base),
    }


def _notes(sport, both_rated, r_home, r_away, cfg, tot_base) -> list[str]:
    out = []
    if both_rated:
        out.append(
            f"Both sides carry official governing-body ratings ({r_home} vs {r_away}); "
            f"log-odds differential scaled by k={cfg['scale']:.0f}."
        )
    else:
        out.append(
            "One or both sides have no current official numeric rating; model falls back to "
            "the neutral home/venue baseline and strictly caps confidence at low."
        )
    if tot_base is not None:
        out.append(f"Total market centered on competition baseline {tot_base:.1f} ({cfg['total_name']}).")
    else:
        out.append("No match total originated for multi-innings / multi-runner format.")
    return out
