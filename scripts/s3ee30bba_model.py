#!/usr/bin/env python3
"""Zero-vig multi-market line origination and confidence grading for session 3ee30bba-olbg1.

Models use only live-verified governing-body statistical aggregates read in this session:
- NHL: Empirical-Bayes shrunk bivariate Poisson (k=10 games) + Beta(3,3) Log5 OT/SO tie resolution
- MLB: 2026 regular-season run-rate conditioned non-tie Poisson grid (Games 1–4; Game 5 conditional withheld)
- EuroLeague: Empirical-Bayes shrunk Normal margin/total model (k=6 games; Valencia conflict quarantined)
- EHF Champions League Men: Empirical-Bayes shrunk 60-minute bivariate Poisson grid (k=5 games; 1X2, DNB, Hcap, Totals)

Fair prices carry zero bookmaker margin (fair_decimal = 1 / p).
High confidence requires BOTH model probability > 70% AND originated price inside [-250, +10000].
"""
from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP

from scripts.s3ee30bba_data import (
    EHF_STANDINGS,
    EUROLEAGUE_STANDINGS,
    MLB_STANDINGS,
    NHL_STANDINGS,
)

BAND_MIN_AMERICAN = -250
BAND_MAX_AMERICAN = 10000
BAND_MIN_DECIMAL = 1.4
BAND_MAX_DECIMAL = 101.0
HIGH_PROB_FLOOR = 0.70
MEDIUM_PROB_FLOOR = 0.58


def verify_standings_conservation() -> dict:
    nhl_gp = sum(v[1] for v in NHL_STANDINGS.values())
    nhl_w = sum(v[2] for v in NHL_STANDINGS.values())
    nhl_l = sum(v[3] + v[4] for v in NHL_STANDINGS.values())
    nhl_gf = sum(v[5] for v in NHL_STANDINGS.values())
    nhl_ga = sum(v[6] for v in NHL_STANDINGS.values())
    if not (nhl_gp == 306 and nhl_w == 153 == nhl_l and nhl_gf == 954 == nhl_ga):
        raise ValueError(f"NHL conservation failed: GP={nhl_gp}, W={nhl_w}, L={nhl_l}, GF={nhl_gf}, GA={nhl_ga}")

    el_gp = sum(v[0] for v in EUROLEAGUE_STANDINGS.values())
    el_w = sum(v[1] for v in EUROLEAGUE_STANDINGS.values())
    el_l = sum(v[2] for v in EUROLEAGUE_STANDINGS.values())
    el_pf = sum(v[3] for v in EUROLEAGUE_STANDINGS.values())
    el_pa = sum(v[4] for v in EUROLEAGUE_STANDINGS.values())
    if not (el_gp == 132 and el_w == 66 == el_l and el_pf == 11459 == el_pa):
        raise ValueError(f"EuroLeague conservation failed: GP={el_gp}, W={el_w}, L={el_l}, PF={el_pf}, PA={el_pa}")

    ehf_gp = sum(v[1] for v in EHF_STANDINGS.values())
    ehf_w = sum(v[2] for v in EHF_STANDINGS.values())
    ehf_d = sum(v[3] for v in EHF_STANDINGS.values())
    ehf_l = sum(v[4] for v in EHF_STANDINGS.values())
    ehf_gf = sum(v[5] for v in EHF_STANDINGS.values())
    ehf_ga = sum(v[6] for v in EHF_STANDINGS.values())
    if not (ehf_gp == 120 and ehf_w == 55 == ehf_l and ehf_d == 10 and ehf_gf == 3844 == ehf_ga):
        raise ValueError(f"EHF conservation failed: GP={ehf_gp}, W={ehf_w}, D={ehf_d}, L={ehf_l}, GF={ehf_gf}, GA={ehf_ga}")

    return {
        "nhl": {"clubs": 32, "team_games": nhl_gp, "games": nhl_gp // 2, "wins": nhl_w, "losses_incl_otl": nhl_l, "gf": nhl_gf, "ga": nhl_ga, "mean_goals_per_team": round(nhl_gf / nhl_gp, 6)},
        "euroleague": {"clubs": 20, "team_games": el_gp, "games": el_gp // 2, "wins": el_w, "losses": el_l, "pf": el_pf, "pa": el_pa, "mean_pts_per_team": round(el_pf / el_gp, 6)},
        "ehf_cl": {"clubs": 24, "team_games": ehf_gp, "games": ehf_gp // 2, "wins": ehf_w, "draws": ehf_d, "losses": ehf_l, "gf": ehf_gf, "ga": ehf_ga, "mean_goals_per_team": round(ehf_gf / ehf_gp, 6)},
    }


def american_from_fair_decimal(raw_decimal: float) -> int:
    d = Decimal(str(raw_decimal))
    if not d.is_finite() or d <= Decimal("1"):
        raise ValueError(f"Invalid fair decimal: {raw_decimal}")
    us = (d - Decimal("1")) * Decimal("100") if d >= Decimal("2") else Decimal("-100") / (d - Decimal("1"))
    return int(us.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def make_outcome(selection: str, probability: float) -> dict:
    if not (isinstance(probability, float) and math.isfinite(probability) and 0.0 < probability < 1.0):
        raise ValueError(f"Invalid probability for {selection}: {probability}")
    fair_dec = 1.0 / probability
    dec_disp = str(Decimal(str(fair_dec)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    us = american_from_fair_decimal(fair_dec)
    in_window = (BAND_MIN_DECIMAL <= fair_dec <= BAND_MAX_DECIMAL) and (BAND_MIN_AMERICAN <= us <= BAND_MAX_AMERICAN)
    if probability > HIGH_PROB_FLOOR and in_window:
        conf = "high"
        note = "In-window High (>70% & -250..+10000)"
    elif probability > HIGH_PROB_FLOOR and not in_window:
        conf = "medium"
        note = "Out-of-window chalk (< -250): capped at Medium"
    elif probability >= MEDIUM_PROB_FLOOR and in_window:
        conf = "medium"
        note = "Moderate edge (58%–70% in-window)"
    else:
        conf = "low"
        note = "Low conviction (<58% or > +10000)"
    return {
        "selection": selection,
        "probability": probability,
        "fair_decimal": fair_dec,
        "decimal_display": dec_disp,
        "american": us,
        "american_display": f"{us:+d}",
        "in_window": in_window,
        "above_70_outside_window": bool(probability > HIGH_PROB_FLOOR and not in_window),
        "confidence": conf,
        "tier_note": note,
    }


def pois_pmf(lam: float, max_k: int = 65) -> list[float]:
    vals = [math.exp(-lam)]
    for k in range(1, max_k + 1):
        vals.append(vals[-1] * lam / k)
    s = math.fsum(vals)
    return [v / s for v in vals]


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _market(mid: str, family: str, label: str, settlement: str, model_version: str, outcomes: list[dict]) -> dict:
    mass = math.fsum(o["probability"] for o in outcomes)
    if abs(mass - 1.0) > 1e-9:
        raise ValueError(f"Market {mid} mass={mass} != 1.0")
    best = max(outcomes, key=lambda o: o["probability"])
    return {
        "id": mid,
        "family": family,
        "label": label,
        "settlement": settlement,
        "model_version": model_version,
        "outcomes": outcomes,
        "recommended": best["selection"],
        "confidence": best["confidence"],
    }


def _originate_nhl(row: dict) -> dict:
    mu = 954.0 / 306.0
    a_code, h_code = row["away_code"], row["home_code"]
    a_name, gpa, wa, la, otla, gfa, gaa, _ = NHL_STANDINGS[a_code]
    h_name, gph, wh, lh, otlh, gfh, gah, _ = NHL_STANDINGS[h_code]
    k = 10.0
    aa = ((gfa + k * mu) / (gpa + k)) / mu
    da = ((gaa + k * mu) / (gpa + k)) / mu
    ah = ((gfh + k * mu) / (gph + k)) / mu
    dh = ((gah + k * mu) / (gph + k)) / mu
    lam_a = mu * aa * dh / 1.035
    lam_h = mu * ah * da * 1.035

    va = pois_pmf(lam_a, 25)
    vh = pois_pmf(lam_h, 25)
    pa_ot = (wa + 3.0) / (gpa + 6.0)
    ph_ot = (wh + 3.0) / (gph + 6.0)
    ot_home = (ph_ot * (1.0 - pa_ot)) / (ph_ot * (1.0 - pa_ot) + pa_ot * (1.0 - ph_ot))

    dist: list[tuple[int, int, float]] = []
    for i, px in enumerate(va):
        for j, py in enumerate(vh):
            p = px * py
            if i == j:
                dist.append((i, j + 1, p * ot_home))
                dist.append((i + 1, j, p * (1.0 - ot_home)))
            else:
                dist.append((i, j, p))

    fid = row["id"]
    ver = "nhl-shrunk-poisson-v1"
    p_h_ml = math.fsum(p for x, y, p in dist if y > x)
    p_h_m15 = math.fsum(p for x, y, p in dist if y - x >= 2)
    p_h_p15 = math.fsum(p for x, y, p in dist if y - x >= -1)
    p_o55 = math.fsum(p for x, y, p in dist if x + y > 5.5)
    p_o65 = math.fsum(p for x, y, p in dist if x + y > 6.5)
    p_att25 = math.fsum(p for x, y, p in dist if x > 2.5)
    p_htt25 = math.fsum(p for x, y, p in dist if y > 2.5)

    markets = [
        _market(f"{fid}-ml", "winner", "Match Winner (Incl. OT/SO)", "Full game incl. OT & shootout", ver,
                [make_outcome(f"{h_name} ML", p_h_ml), make_outcome(f"{a_name} ML", 1.0 - p_h_ml)]),
        _market(f"{fid}-pl-home-m15", "handicap", f"Puck Line ({h_code} -1.5 / {a_code} +1.5)", "Full game incl. OT/SO", ver,
                [make_outcome(f"{h_name} -1.5", p_h_m15), make_outcome(f"{a_name} +1.5", 1.0 - p_h_m15)]),
        _market(f"{fid}-pl-home-p15", "handicap", f"Reverse Puck Line ({h_code} +1.5 / {a_code} -1.5)", "Full game incl. OT/SO", ver,
                [make_outcome(f"{h_name} +1.5", p_h_p15), make_outcome(f"{a_name} -1.5", 1.0 - p_h_p15)]),
        _market(f"{fid}-tot-55", "total", "Game Total 5.5 Goals", "Combined goals incl. OT/SO winner", ver,
                [make_outcome("Over 5.5 Goals", p_o55), make_outcome("Under 5.5 Goals", 1.0 - p_o55)]),
        _market(f"{fid}-tot-65", "total", "Game Total 6.5 Goals", "Combined goals incl. OT/SO winner", ver,
                [make_outcome("Over 6.5 Goals", p_o65), make_outcome("Under 6.5 Goals", 1.0 - p_o65)]),
        _market(f"{fid}-tt-away-25", "team-total", f"{a_name} Team Total 2.5", "Away team goals incl. OT/SO", ver,
                [make_outcome(f"{a_name} Over 2.5 Goals", p_att25), make_outcome(f"{a_name} Under 2.5 Goals", 1.0 - p_att25)]),
        _market(f"{fid}-tt-home-25", "team-total", f"{h_name} Team Total 2.5", "Home team goals incl. OT/SO", ver,
                [make_outcome(f"{h_name} Over 2.5 Goals", p_htt25), make_outcome(f"{h_name} Under 2.5 Goals", 1.0 - p_htt25)]),
    ]
    winner_best = max(markets[0]["outcomes"], key=lambda o: o["probability"])
    return {
        "model_version": ver,
        "parameters": {"lambda_away": round(lam_a, 4), "lambda_home": round(lam_h, 4), "ot_home_prob": round(ot_home, 4)},
        "winner_pick": dict(winner_best),
        "markets": markets,
        "withheld_markets": [
            {"family": "period", "reason": "1st-period goal-split distributions not queried from standings endpoint."},
            {"family": "player-prop", "reason": "Confirmed starting goaltenders and line TOI unverified pre-warmup."},
        ],
    }


def _originate_mlb(row: dict) -> dict:
    mu = 4.40
    a_code, h_code = row["away_code"], row["home_code"]
    a_name, gpa, wa, la, rsa, raa = MLB_STANDINGS[a_code]
    h_name, gph, wh, lh, rsh, rah = MLB_STANDINGS[h_code]
    lam_a = ((rsa / gpa) * (rah / gph) / mu) / 1.025
    lam_h = ((rsh / gph) * (raa / gpa) / mu) * 1.025

    va = pois_pmf(lam_a, 30)
    vh = pois_pmf(lam_h, 30)
    pairs = [(x, y, px * py) for x, px in enumerate(va) for y, py in enumerate(vh) if x != y]
    tot = math.fsum(z for _, _, z in pairs)
    dist = [(x, y, z / tot) for x, y, z in pairs]

    fid = row["id"]
    ver = "mlb-shrunk-poisson-v1"
    p_h_ml = math.fsum(p for x, y, p in dist if y > x)
    p_h_m15 = math.fsum(p for x, y, p in dist if y - x >= 2)
    p_h_p15 = math.fsum(p for x, y, p in dist if y - x >= -1)
    p_o75 = math.fsum(p for x, y, p in dist if x + y > 7.5)
    p_o85 = math.fsum(p for x, y, p in dist if x + y > 8.5)
    p_o95 = math.fsum(p for x, y, p in dist if x + y > 9.5)
    p_htt45 = math.fsum(p for x, y, p in dist if y > 4.5)

    markets = [
        _market(f"{fid}-ml", "winner", "Match Winner (Moneyline)", "Full game incl. extra innings", ver,
                [make_outcome(f"{h_name} ML", p_h_ml), make_outcome(f"{a_name} ML", 1.0 - p_h_ml)]),
        _market(f"{fid}-rl-home-m15", "handicap", f"Run Line ({h_code} -1.5 / {a_code} +1.5)", "Full game incl. extra innings", ver,
                [make_outcome(f"{h_name} -1.5", p_h_m15), make_outcome(f"{a_name} +1.5", 1.0 - p_h_m15)]),
        _market(f"{fid}-rl-home-p15", "handicap", f"Reverse Run Line ({h_code} +1.5 / {a_code} -1.5)", "Full game incl. extra innings", ver,
                [make_outcome(f"{h_name} +1.5", p_h_p15), make_outcome(f"{a_name} -1.5", 1.0 - p_h_p15)]),
        _market(f"{fid}-tot-75", "total", "Game Total 7.5 Runs", "Combined runs incl. extra innings", ver,
                [make_outcome("Over 7.5 Runs", p_o75), make_outcome("Under 7.5 Runs", 1.0 - p_o75)]),
        _market(f"{fid}-tot-85", "total", "Game Total 8.5 Runs", "Combined runs incl. extra innings", ver,
                [make_outcome("Over 8.5 Runs", p_o85), make_outcome("Under 8.5 Runs", 1.0 - p_o85)]),
        _market(f"{fid}-tot-95", "total", "Game Total 9.5 Runs", "Combined runs incl. extra innings", ver,
                [make_outcome("Over 9.5 Runs", p_o95), make_outcome("Under 9.5 Runs", 1.0 - p_o95)]),
        _market(f"{fid}-tt-home-45", "team-total", f"{h_name} Team Total 4.5", "Home runs incl. extra innings", ver,
                [make_outcome(f"{h_name} Over 4.5 Runs", p_htt45), make_outcome(f"{h_name} Under 4.5 Runs", 1.0 - p_htt45)]),
    ]
    winner_best = max(markets[0]["outcomes"], key=lambda o: o["probability"])
    return {
        "model_version": ver,
        "parameters": {"lambda_away": round(lam_a, 4), "lambda_home": round(lam_h, 4)},
        "winner_pick": dict(winner_best),
        "markets": markets,
        "withheld_markets": [
            {"family": "period", "reason": "First-5-innings line withheld because individual pitcher inning-split FIP/ERA feeds were not used."},
            {"family": "player-prop", "reason": "Confirmed batting orders and bullpen pitch-count availability unverified."},
        ],
    }


def _originate_euroleague(row: dict) -> dict:
    mu = 11459.0 / 132.0
    h_name, a_name = row["home"], row["away"]
    gph, wh, lh, pfh, pah = EUROLEAGUE_STANDINGS[h_name]
    gpa, wa, la, pfa, paa = EUROLEAGUE_STANDINGS[a_name]
    k = 6.0
    oh = (pfh + k * mu) / (gph + k)
    dh = (pah + k * mu) / (gph + k)
    oa = (pfa + k * mu) / (gpa + k)
    da = (paa + k * mu) / (gpa + k)
    exp_h = (oh + da - mu) + 1.25
    exp_a = (oa + dh - mu) - 1.25
    margin = exp_h - exp_a
    total = exp_h + exp_a
    sigma_m = 11.5
    sigma_t = 15.0

    fid = row["id"]
    ver = "el-shrunk-normal-v1"
    p_h_ml = 1.0 - norm_cdf((0.0 - margin) / sigma_m)
    p_h_m35 = 1.0 - norm_cdf((3.5 - margin) / sigma_m)
    p_h_m65 = 1.0 - norm_cdf((6.5 - margin) / sigma_m)
    p_h_p35 = 1.0 - norm_cdf((-3.5 - margin) / sigma_m)
    c_tot = math.floor(total) + 0.5
    t_low = c_tot - 4.0
    t_mid = c_tot
    p_o_low = 1.0 - norm_cdf((t_low - total) / sigma_t)
    p_o_mid = 1.0 - norm_cdf((t_mid - total) / sigma_t)

    markets = [
        _market(f"{fid}-ml", "winner", "Match Winner (Incl. OT)", "Full game incl. overtime", ver,
                [make_outcome(f"{h_name} ML", p_h_ml), make_outcome(f"{a_name} ML", 1.0 - p_h_ml)]),
        _market(f"{fid}-sp-m35", "handicap", "Point Spread (-3.5 / +3.5)", "Full game incl. overtime", ver,
                [make_outcome(f"{h_name} -3.5", p_h_m35), make_outcome(f"{a_name} +3.5", 1.0 - p_h_m35)]),
        _market(f"{fid}-sp-m65", "handicap", "Alt Point Spread (-6.5 / +6.5)", "Full game incl. overtime", ver,
                [make_outcome(f"{h_name} -6.5", p_h_m65), make_outcome(f"{a_name} +6.5", 1.0 - p_h_m65)]),
        _market(f"{fid}-sp-p35", "handicap", "Reverse Point Spread (+3.5 / -3.5)", "Full game incl. overtime", ver,
                [make_outcome(f"{h_name} +3.5", p_h_p35), make_outcome(f"{a_name} -3.5", 1.0 - p_h_p35)]),
        _market(f"{fid}-tot-low", "total", f"Game Total {t_low:.1f} Points", "Combined points incl. overtime", ver,
                [make_outcome(f"Over {t_low:.1f} Pts", p_o_low), make_outcome(f"Under {t_low:.1f} Pts", 1.0 - p_o_low)]),
        _market(f"{fid}-tot-mid", "total", f"Game Total {t_mid:.1f} Points", "Combined points incl. overtime", ver,
                [make_outcome(f"Over {t_mid:.1f} Pts", p_o_mid), make_outcome(f"Under {t_mid:.1f} Pts", 1.0 - p_o_mid)]),
    ]
    winner_best = max(markets[0]["outcomes"], key=lambda o: o["probability"])
    return {
        "model_version": ver,
        "parameters": {"expected_home_pts": round(exp_h, 2), "expected_away_pts": round(exp_a, 2), "expected_margin": round(margin, 2)},
        "winner_pick": dict(winner_best),
        "markets": markets,
        "withheld_markets": [
            {"family": "period", "reason": "Quarter-by-quarter EuroLeague scoring distributions not modeled from overall standings."},
            {"family": "player-prop", "reason": "Final 12-man matchday registration sheets lock 60 minutes pre-tipoff."},
        ],
    }


def _originate_ehf(row: dict) -> dict:
    mu = 3844.0 / 120.0
    h_name, a_name = row["home"], row["away"]
    _, gph, wh, dh_, lh, gfh, gah, _ = EHF_STANDINGS[h_name]
    _, gpa, wa, da_, la, gfa, gaa, _ = EHF_STANDINGS[a_name]
    k = 5.0
    ah = ((gfh + k * mu) / (gph + k)) / mu
    dfh = ((gah + k * mu) / (gph + k)) / mu
    aa = ((gfa + k * mu) / (gpa + k)) / mu
    dfa = ((gaa + k * mu) / (gpa + k)) / mu
    lam_h = mu * ah * dfa * 1.035
    lam_a = mu * aa * dfh / 1.035

    vh = pois_pmf(lam_h, 60)
    va = pois_pmf(lam_a, 60)
    dist = [(x, y, px * py) for x, px in enumerate(vh) for y, py in enumerate(va)]

    fid = row["id"]
    ver = "ehf-shrunk-poisson-v1"
    p_1 = math.fsum(p for x, y, p in dist if x > y)
    p_x = math.fsum(p for x, y, p in dist if x == y)
    p_2 = math.fsum(p for x, y, p in dist if y > x)
    p_dnb_h = p_1 / (p_1 + p_2)
    p_hm25 = math.fsum(p for x, y, p in dist if x - y >= 3)
    p_hp25 = math.fsum(p for x, y, p in dist if x - y >= -2)
    c_tot = int(math.floor(lam_h + lam_a))
    t_low = float(c_tot) - 1.5
    t_high = float(c_tot) + 1.5
    p_o_low = math.fsum(p for x, y, p in dist if x + y > t_low)
    p_o_high = math.fsum(p for x, y, p in dist if x + y > t_high)

    markets = [
        _market(f"{fid}-1x2", "winner", "Match Result 1X2 (60 Min)", "Regulation 60 minutes (3-way)", ver,
                [make_outcome(f"{h_name} (60m)", p_1), make_outcome("Draw (60m)", p_x), make_outcome(f"{a_name} (60m)", p_2)]),
        _market(f"{fid}-dnb", "winner", "Draw No Bet (2-Way)", "60 minutes; draw refunds stake", ver,
                [make_outcome(f"{h_name} DNB", p_dnb_h), make_outcome(f"{a_name} DNB", 1.0 - p_dnb_h)]),
        _market(f"{fid}-hc-m25", "handicap", "Goal Handicap (-2.5 / +2.5)", "Regulation 60 minutes", ver,
                [make_outcome(f"{h_name} -2.5", p_hm25), make_outcome(f"{a_name} +2.5", 1.0 - p_hm25)]),
        _market(f"{fid}-hc-p25", "handicap", "Reverse Goal Handicap (+2.5 / -2.5)", "Regulation 60 minutes", ver,
                [make_outcome(f"{h_name} +2.5", p_hp25), make_outcome(f"{a_name} -2.5", 1.0 - p_hp25)]),
        _market(f"{fid}-tot-low", "total", f"Match Total {t_low:.1f} Goals", "Regulation 60 minutes combined goals", ver,
                [make_outcome(f"Over {t_low:.1f} Goals", p_o_low), make_outcome(f"Under {t_low:.1f} Goals", 1.0 - p_o_low)]),
        _market(f"{fid}-tot-high", "total", f"Match Total {t_high:.1f} Goals", "Regulation 60 minutes combined goals", ver,
                [make_outcome(f"Over {t_high:.1f} Goals", p_o_high), make_outcome(f"Under {t_high:.1f} Goals", 1.0 - p_o_high)]),
    ]
    winner_best = max(markets[0]["outcomes"], key=lambda o: o["probability"])
    return {
        "model_version": ver,
        "parameters": {"lambda_home": round(lam_h, 4), "lambda_away": round(lam_a, 4), "draw_prob": round(p_x, 4)},
        "winner_pick": dict(winner_best),
        "markets": markets,
        "withheld_markets": [
            {"family": "period", "reason": "1st-half (30-min) scoring splits not published in EHF Group Phase standings."},
            {"family": "player-prop", "reason": "Matchday 16-player EHF technical-meeting rosters not yet confirmed."},
        ],
    }


def originate_all(fixtures: list[dict]) -> dict[str, dict]:
    books: dict[str, dict] = {}
    for row in fixtures:
        mode = row.get("pricing_mode")
        if mode == "nhl":
            books[row["id"]] = _originate_nhl(row)
        elif mode == "mlb":
            books[row["id"]] = _originate_mlb(row)
        elif mode == "euroleague":
            books[row["id"]] = _originate_euroleague(row)
        elif mode == "ehf":
            books[row["id"]] = _originate_ehf(row)
        else:
            books[row["id"]] = {
                "model_version": None,
                "parameters": None,
                "winner_pick": None,
                "markets": [],
                "withheld_markets": [
                    {"family": "all", "reason": row.get("withhold_reason") or "Unverified UTC start or statistical input."}
                ],
            }
    return books
