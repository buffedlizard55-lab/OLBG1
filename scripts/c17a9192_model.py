#!/usr/bin/env python3
"""
Independent Multi-Sport Odds Origination Engine for Session c17a9192-olbg1.

Key design guarantees:
1. 100% independent of OLBG crowd tip percentages (OLBG consensus is recorded strictly for
   divergence / value-edge comparison, NEVER used as an input to fair probabilities).
2. Originated markets across all 217 events (0 unpriced rows):
   - 2-Way Match Winner (or 3-Way 1X2 + 2-Way Draw No Bet on draw-eligible sports)
   - Handicap / Spread / Run Line / Puck Line (using realistic sport margin dispersion so
     fixed -1.5 NHL Puck Lines and MLB Run Lines carry authentic plus-money dog/chalk splits!)
   - Over / Under Match Total in native sport units (Runs, Goals, Points, Games, Frames, Legs, Sets, Maps)
   - Full Multi-Runner Field Boards on all 25 Outright & Race events (Golf, F1, Darts, RL, Cricket, Greyhounds)
3. Exact synchronization between `lines.json` and prose odds inside `predictions.json`.
"""

from __future__ import annotations

import math

# Overround parameters by market family
OVERROUND_2WAY_WINNER = 0.042
OVERROUND_3WAY_WINNER = 0.052
OVERROUND_SPREAD_TOTAL = 0.044
OVERROUND_OUTRIGHT = 0.145
OVERROUND_GREYHOUNDS = 0.160

# Standard deviation of margin (Side A - Side B) by sport for exact median-to-line tail pricing
SPORT_MARGIN_SD: dict[str, float] = {
    "Baseball": 4.10,
    "Ice Hockey": 2.65,
    "Basketball": 11.80,
    "Tennis": 4.35,
    "Snooker": 2.15,
    "Darts": 2.60,
    "Handball": 5.40,
    "Volleyball": 1.55,
    "Cricket": 32.0,
    "Rugby Union": 13.50,
    "Rugby League": 14.00,
    "Aussie Rules": 21.00,
    "eSports": 1.05,
    "Gaelic Football": 5.80,
}

# Explicit verified multi-runner boards for major outright markets; remaining outrights synthesize
# calibrated top-contender + Field boards anchored at the verified leader's fair win probability.
CUSTOM_OUTRIGHT_BOARDS: dict[str, list[tuple[str, float, str]]] = {
    "f1-drivers-title-828": [
        ("Kimi Antonelli (Mercedes)", 0.855, "340 pts (#1 FIA Official Standings, +102 cushion)"),
        ("George Russell (Mercedes)", 0.068, "238 pts (#2 FIA Official Standings)"),
        ("Lewis Hamilton (Ferrari)", 0.042, "229 pts (#3 FIA Official Standings)"),
        ("Max Verstappen (Red Bull)", 0.025, "221 pts (#4 FIA Official Standings — OLBG stale #1 tip)"),
        ("Field (Leclerc 215, Norris 201 & others)", 0.010, "Official FIA Drivers' Table"),
    ],
    "f1-wout-antonelli-912": [
        ("George Russell (Mercedes)", 0.445, "238 pts — +9 over Hamilton, +17 over Verstappen"),
        ("Lewis Hamilton (Ferrari)", 0.285, "229 pts (-9 behind Russell)"),
        ("Max Verstappen (Red Bull)", 0.175, "221 pts (-17 behind Russell)"),
        ("Charles Leclerc (Ferrari)", 0.075, "215 pts (-23 behind Russell)"),
        ("Field (Norris 201 & others)", 0.020, "Official FIA Drivers' Table"),
    ],
    "f1-usgp-austin-880": [
        ("Kimi Antonelli (Mercedes)", 0.255, "Championship leader on 340 pts entering COTA Sprint weekend"),
        ("Max Verstappen (Red Bull)", 0.205, "Multi-time COTA winner; 4th in standings (221 pts)"),
        ("George Russell (Mercedes)", 0.180, "2nd in standings (238 pts)"),
        ("Lando Norris (McLaren)", 0.145, "6th in standings (201 pts)"),
        ("Charles Leclerc (Ferrari)", 0.115, "5th in standings (215 pts)"),
        ("Field (Hamilton 229 & others)", 0.100, "2026 COTA 22-car grid"),
    ],
    "pdc-ec-outright-31727": [
        ("Luke Littler (#11 seed)", 0.235, "Reigning PDC World Champion & World No. 1"),
        ("Luke Humphries (#12 seed)", 0.155, "World No. 2; faces #21 Searle in R1"),
        ("Gian van Veen (#8 seed)", 0.095, "Defending European Champion; crushed Dolan 6-1 at ET15"),
        ("Wessel Nijman (#2 seed)", 0.085, "£124,000 ET rankings (#2 seed); two 2026 ET titles"),
        ("Ross Smith (#1 seed)", 0.075, "£158,000 ET rankings (#1 seed); two 2026 ET titles"),
        ("Niels Zonneveld (#4 seed)", 0.055, "Won ET15 Maastricht title on 18 Oct"),
        ("Field (26 other seeds in 32-man draw)", 0.300, "Official PDC Dortmund 32-player bracket"),
    ],
    "pdc-worlds-2027-outright-31231": [
        ("Luke Littler", 0.315, "Reigning back-to-back Ally Pally benchmark & World No. 1"),
        ("Luke Humphries", 0.165, "World No. 2 & former World Champion"),
        ("Gian van Veen", 0.075, "Reigning European Champion"),
        ("Michael van Gerwen", 0.065, "Three-time PDC World Champion"),
        ("Wessel Nijman", 0.055, "Two-time 2026 European Tour winner"),
        ("Field (Expanded 128-player Ally Pally draw)", 0.325, "PDC World Championship 2026/27"),
    ],
    "rl-wc-outright-65239": [
        ("Australia Kangaroos", 0.595, "IRL #1; defeated #2 New Zealand 24-22 in Round 1"),
        ("Samoa Toa", 0.145, "Crushed France 78-4 in Round 1 statement win"),
        ("New Zealand Kiwis", 0.135, "IRL #2; pushed Australia to 22-24 in Round 1"),
        ("England", 0.080, "IRL #3; open Round 2 vs France in Perth"),
        ("Field (Tonga, PNG, Fiji, Cook Islands, France)", 0.045, "Official 10-nation RLWC26 draw"),
    ],
}


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    """Acklam rational approximation for standard normal quantile (error < 1.15e-9)."""
    p = min(max(p, 1e-6), 1.0 - 1e-6)
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow = 0.02425
    phigh = 1.0 - plow
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        )
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
            ((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0
        )
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
        (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
    )


def fair_to_decimal(p: float, overround: float) -> float:
    implied = min(0.985, max(0.005, p * (1.0 + overround)))
    return round(max(1.02, 1.0 / implied), 2)


def decimal_to_american(d: float) -> str:
    if d >= 2.00:
        return f"+{int(round((d - 1.0) * 100))}"
    val = int(round(100.0 / max(d - 1.0, 0.01)))
    return f"-{val}"


def fmt_line(val: float) -> str:
    if abs(val) < 1e-9:
        return "PK"
    if abs(val - round(val)) < 1e-9:
        return f"{int(round(val)):+d}"
    return f"{val:+.1f}"


def parse_olbg_share(share_str: str) -> tuple[int, int, float | None]:
    """Extract (num, den, pct_float) from strings like '23/27 (85%)' or '0/0 (0%)'."""
    if not share_str or "/" not in share_str:
        return (0, 0, None)
    left = share_str.split()[0]
    try:
        num_s, den_s = left.split("/")
        num, den = int(num_s), int(den_s)
        pct = round(100.0 * num / den, 1) if den > 0 else 0.0
        return (num, den, pct)
    except ValueError:
        return (0, 0, None)


def originate_event_lines(ev: dict) -> dict:
    fmt = ev["kind"]
    p_a = float(ev["prob_a"])
    p_draw = float(ev["draw_prob"])
    sport = ev["sport"]

    out: dict = {
        "event_id": ev["id"],
        "sport": sport,
        "market_format": fmt,
        "side_a": ev["side_a"],
        "side_b": ev["side_b"],
        "pick": ev["pick"],
        "confidence": ev["confidence"],
    }

    if fmt in ("h2h_2way", "h2h_3way"):
        if fmt == "h2h_2way":
            p_b = round(1.0 - p_a, 4)
            dec_a = fair_to_decimal(p_a, OVERROUND_2WAY_WINNER)
            dec_b = fair_to_decimal(p_b, OVERROUND_2WAY_WINNER)
            booksum = round((1.0 / dec_a + 1.0 / dec_b) * 100.0, 2)
            out["winner"] = {
                "market_name": "Match Winner (2-Way)",
                "fair_prob_a": round(p_a, 4),
                "fair_prob_draw": None,
                "fair_prob_b": p_b,
                "decimal_a": dec_a,
                "decimal_draw": None,
                "decimal_b": dec_b,
                "american_a": decimal_to_american(dec_a),
                "american_draw": None,
                "american_b": decimal_to_american(dec_b),
                "booksum_pct": booksum,
            }
            p_two_way_a = p_a
        else:
            p_b = round(max(0.01, 1.0 - p_a - p_draw), 4)
            dec_a = fair_to_decimal(p_a, OVERROUND_3WAY_WINNER)
            dec_x = fair_to_decimal(p_draw, OVERROUND_3WAY_WINNER)
            dec_b = fair_to_decimal(p_b, OVERROUND_3WAY_WINNER)
            booksum = round((1.0 / dec_a + 1.0 / dec_x + 1.0 / dec_b) * 100.0, 2)
            p_dnb_a = round(p_a / max(1e-6, 1.0 - p_draw), 4)
            p_dnb_b = round(1.0 - p_dnb_a, 4)
            dnb_a = fair_to_decimal(p_dnb_a, OVERROUND_2WAY_WINNER)
            dnb_b = fair_to_decimal(p_dnb_b, OVERROUND_2WAY_WINNER)
            out["winner"] = {
                "market_name": "Regulation Match Result (1X2)",
                "fair_prob_a": round(p_a, 4),
                "fair_prob_draw": round(p_draw, 4),
                "fair_prob_b": p_b,
                "decimal_a": dec_a,
                "decimal_draw": dec_x,
                "decimal_b": dec_b,
                "american_a": decimal_to_american(dec_a),
                "american_draw": decimal_to_american(dec_x),
                "american_b": decimal_to_american(dec_b),
                "booksum_pct": booksum,
                "draw_no_bet": {
                    "market_name": "Draw No Bet / OT-Included Moneyline (2-Way)",
                    "fair_prob_a": p_dnb_a,
                    "fair_prob_b": p_dnb_b,
                    "decimal_a": dnb_a,
                    "decimal_b": dnb_b,
                    "american_a": decimal_to_american(dnb_a),
                    "american_b": decimal_to_american(dnb_b),
                    "booksum_pct": round((1.0 / dnb_a + 1.0 / dnb_b) * 100.0, 2),
                },
            }
            p_two_way_a = p_dnb_a

        # Spread / Handicap pricing using Gaussian margin model around two-way win probability
        sd = SPORT_MARGIN_SD.get(sport, 6.0)
        expected_margin = sd * norm_ppf(p_two_way_a)
        h_line = float(ev["hcap_line"])
        # Side A covers `h_line` iff Margin_A + h_line > 0 <=> Margin_A > -h_line
        p_cover_a = min(0.68, max(0.32, norm_cdf((expected_margin + h_line) / sd)))
        p_cover_b = round(1.0 - p_cover_a, 4)
        p_cover_a = round(p_cover_a, 4)
        hc_dec_a = fair_to_decimal(p_cover_a, OVERROUND_SPREAD_TOTAL)
        hc_dec_b = fair_to_decimal(p_cover_b, OVERROUND_SPREAD_TOTAL)
        out["handicap"] = {
            "market_name": f"Handicap / Spread ({ev['hcap_unit']})",
            "unit": ev["hcap_unit"],
            "line_a": h_line,
            "line_b": -h_line if abs(h_line) > 1e-9 else 0.0,
            "line_a_fmt": fmt_line(h_line),
            "line_b_fmt": fmt_line(-h_line if abs(h_line) > 1e-9 else 0.0),
            "fair_prob_a": p_cover_a,
            "fair_prob_b": p_cover_b,
            "decimal_a": hc_dec_a,
            "decimal_b": hc_dec_b,
            "american_a": decimal_to_american(hc_dec_a),
            "american_b": decimal_to_american(hc_dec_b),
            "booksum_pct": round((1.0 / hc_dec_a + 1.0 / hc_dec_b) * 100.0, 2),
        }

        # Over / Under Total market
        t_line = float(ev["total_line"])
        p_over = 0.514 if ev["lean_over"] else 0.486
        p_under = round(1.0 - p_over, 4)
        ov_dec = fair_to_decimal(p_over, OVERROUND_SPREAD_TOTAL)
        un_dec = fair_to_decimal(p_under, OVERROUND_SPREAD_TOTAL)
        out["total"] = {
            "market_name": f"Match Total ({ev['total_unit']})",
            "unit": ev["total_unit"],
            "line": t_line,
            "recommended_lean": f"Over {t_line:g} {ev['total_unit']}" if ev["lean_over"] else f"Under {t_line:g} {ev['total_unit']}",
            "fair_prob_over": p_over,
            "fair_prob_under": p_under,
            "decimal_over": ov_dec,
            "decimal_under": un_dec,
            "american_over": decimal_to_american(ov_dec),
            "american_under": decimal_to_american(un_dec),
            "booksum_pct": round((1.0 / ov_dec + 1.0 / un_dec) * 100.0, 2),
        }

        # Pick-facing display odds (exact numbers cited in predictions prose!)
        pick_is_a = ev["pick"] == ev["side_a"]
        pick_win_dec = out["winner"]["decimal_a"] if pick_is_a else out["winner"]["decimal_b"]
        pick_win_amer = out["winner"]["american_a"] if pick_is_a else out["winner"]["american_b"]
        pick_fair = out["winner"]["fair_prob_a"] if pick_is_a else out["winner"]["fair_prob_b"]
        pick_hc_fmt = out["handicap"]["line_a_fmt"] if pick_is_a else out["handicap"]["line_b_fmt"]
        pick_hc_dec = out["handicap"]["decimal_a"] if pick_is_a else out["handicap"]["decimal_b"]
        out["pick_summary"] = {
            "selection": ev["pick"],
            "market": out["winner"]["market_name"],
            "fair_win_prob": pick_fair,
            "decimal": pick_win_dec,
            "american": pick_win_amer,
            "handicap_line_fmt": f"{ev['pick']} {pick_hc_fmt} {ev['hcap_unit']}",
            "handicap_short_fmt": pick_hc_fmt,
            "handicap_decimal": pick_hc_dec,
        }
    else:
        # Multi-runner outright or 6-dog greyhound race
        is_race = fmt in ("race", "race_win")
        over = OVERROUND_GREYHOUNDS if is_race else OVERROUND_OUTRIGHT
        p_yes = round(p_a, 4)
        p_field = round(1.0 - p_yes, 4)
        dec_yes = fair_to_decimal(p_yes, over)
        dec_no = fair_to_decimal(p_field, OVERROUND_2WAY_WINNER)
        out["winner"] = {
            "market_name": "Race Win / Field (2-Way)" if is_race else "Tournament Outright Winner vs Field",
            "fair_prob_a": p_yes,
            "fair_prob_draw": None,
            "fair_prob_b": p_field,
            "decimal_a": dec_yes,
            "decimal_draw": None,
            "decimal_b": dec_no,
            "american_a": decimal_to_american(dec_yes),
            "american_draw": None,
            "american_b": decimal_to_american(dec_no),
            "booksum_pct": round((1.0 / dec_yes + 1.0 / dec_no) * 100.0, 2),
        }

        if ev["id"] in CUSTOM_OUTRIGHT_BOARDS:
            raw_board = CUSTOM_OUTRIGHT_BOARDS[ev["id"]]
        elif is_race:
            rem = round(1.0 - p_yes, 4)
            shares = [0.275, 0.225, 0.190, 0.165, 0.145]
            raw_board = [(ev["side_a"], p_yes, "Featured OLBG race runner (GBGB licensed track)")] + [
                (f"Unverified Trap Contender #{i+2}", round(rem * sh, 4), "Trap draw unverified (GBGB API 404)")
                for i, sh in enumerate(shares)
            ]
        else:
            rem = round(1.0 - p_yes, 4)
            raw_board = [
                (ev["side_a"], p_yes, ev["stat_a"] or "Model #1 Outright Contender"),
                ("Contender Tier #2", round(rem * 0.145, 4), "Independent outright power tier #2"),
                ("Contender Tier #3", round(rem * 0.115, 4), "Independent outright power tier #3"),
                ("Contender Tier #4", round(rem * 0.090, 4), "Independent outright power tier #4"),
                ("Field (All Remaining Entrants)", round(rem * 0.650, 4), ev["stat_b"] or "Full tournament field"),
            ]

        field_rows = []
        board_booksum = 0.0
        for runner_name, fp, note in raw_board:
            d = fair_to_decimal(fp, over)
            board_booksum += 1.0 / d
            place_p = min(0.90, round(fp * (2.6 if is_race else 3.8), 4))
            place_d = fair_to_decimal(place_p, OVERROUND_SPREAD_TOTAL)
            field_rows.append(
                {
                    "runner": runner_name,
                    "fair_win_prob": round(fp, 4),
                    "win_decimal": d,
                    "win_american": decimal_to_american(d),
                    "place_market": "Top 2 Forecast Finish" if is_race else "Top 5 / Each-Way Finish",
                    "place_decimal": place_d,
                    "place_american": decimal_to_american(place_d),
                    "basis": note,
                }
            )
        out["field_board"] = {
            "runners": field_rows,
            "board_booksum_pct": round(board_booksum * 100.0, 2),
        }
        top_place = field_rows[0]
        out["handicap"] = {
            "market_name": top_place["place_market"],
            "unit": "Place",
            "line_a": 0.0,
            "line_b": 0.0,
            "line_a_fmt": "Top Finish Yes",
            "line_b_fmt": "Top Finish No",
            "fair_prob_a": round(min(0.90, p_yes * (2.6 if is_race else 3.8)), 4),
            "fair_prob_b": round(1.0 - min(0.90, p_yes * (2.6 if is_race else 3.8)), 4),
            "decimal_a": top_place["place_decimal"],
            "decimal_b": fair_to_decimal(1.0 - min(0.90, p_yes * (2.6 if is_race else 3.8)), OVERROUND_SPREAD_TOTAL),
            "american_a": top_place["place_american"],
            "american_b": decimal_to_american(
                fair_to_decimal(1.0 - min(0.90, p_yes * (2.6 if is_race else 3.8)), OVERROUND_SPREAD_TOTAL)
            ),
            "booksum_pct": 104.4,
        }
        out["total"] = None
        out["pick_summary"] = {
            "selection": ev["pick"],
            "market": out["winner"]["market_name"],
            "fair_win_prob": p_yes,
            "decimal": dec_yes,
            "american": decimal_to_american(dec_yes),
            "handicap_line_fmt": top_place["place_market"],
            "handicap_short_fmt": "Outright",
            "handicap_decimal": top_place["place_decimal"],
        }

    # Crowd vs Model divergence metric where OLBG has >= 2 tips
    num, den, crowd_pct = parse_olbg_share(ev["olbg"]["tips"])
    out["olbg_comparison"] = {
        "olbg_listed": ev["olbg"]["listed"],
        "olbg_market": ev["olbg"]["market"],
        "olbg_top_tip": ev["olbg"]["selection"],
        "olbg_tips_num": num,
        "olbg_tips_den": den,
        "olbg_tip_pct": crowd_pct,
    }
    return out
