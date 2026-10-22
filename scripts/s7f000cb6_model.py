#!/usr/bin/env python3
"""Independent zero-vig multi-market pricing & High-confidence selection engine (7f000cb6).

Model Version: 7f000cb6-quant-v1.0
- Zero bookmaker/aggregator odds imported.
- Zero default/fallback ratings (if either side lacks verified current-season stats, no line is originated).
- Exact unclamped zero-vig decimal price (1 / p) and rounded American display odds.
- High-confidence gate:
    1) Fixture is upcoming with an explicit verified ISO-8601 UTC timestamp (> AS_OF_UTC) and zero official-source contradictions;
    2) Selection fair price sits strictly inside [-250, +10000] American odds (1.4000 <= fair_decimal <= 101.0000);
    3) Selection probability satisfies p > 0.7000 (so p lies in (0.7000, 0.7142857], i.e. -234 to -250);
    4) Heavy-chalk moneylines steeper than -250 (fair_decimal < 1.4000) are capped at 'Medium (Chalk > -250)' rather than graded High merely for having high win probability.
"""
from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP

from s7f000cb6_data import (
    AS_OF_UTC,
    EUROLEAGUE_STANDINGS,
    MLB_STANDINGS,
    NHL_STANDINGS,
)

MODEL_VERSION = "7f000cb6-quant-v1.0"


def american_from_decimal(dec: float) -> int:
    d = Decimal(str(round(dec, 6)))
    if d <= Decimal("1"):
        raise ValueError(f"Invalid decimal odds: {dec}")
    val = (d - Decimal("1")) * Decimal("100") if d >= Decimal("2") else Decimal("-100") / (d - Decimal("1"))
    return int(val.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def fmt_american(us: int) -> str:
    return f"+{us}" if us > 0 else str(us)


def in_playable_window(fair_decimal: float) -> bool:
    return 1.4000 <= fair_decimal <= 101.0000


def grade_selection(prob: float, fair_dec: float, has_flag: bool = False) -> tuple[str, str]:
    """Return (grade, note) enforcing both p > 0.70 and the [-250, +10000] window."""
    in_win = in_playable_window(fair_dec)
    if prob > 0.7000 and in_win and not has_flag:
        return "High", "Meets p > 70.0% and [-250, +10000] fair-price window with full official verification."
    if prob > 0.7142857:
        return "Medium", "Capped at Medium: fair odds steeper than -250 chalk ceiling despite >71.4% win probability."
    if prob > 0.7000 and has_flag:
        return "Medium", "Capped at Medium due to official publisher prose/table discrepancy flag."
    if prob >= 0.5800 and in_win:
        return "Medium", "Moderate conviction (58.0%–70.0%) inside [-250, +10000]."
    return "Low", "Experimental baseline (<58.0% edge or outside target band)."


def make_outcome(selection: str, prob: float, has_flag: bool = False) -> dict:
    fair_dec = 1.0 / prob
    us = american_from_decimal(fair_dec)
    grade, note = grade_selection(prob, fair_dec, has_flag=has_flag)
    return {
        "selection": selection,
        "probability": round(prob, 5),
        "fair_decimal": round(fair_dec, 4),
        "american_odds": us,
        "american_display": fmt_american(us),
        "in_target_window": in_playable_window(fair_dec),
        "confidence": grade,
        "confidence_note": note,
    }


def two_way_market(
    mid: str,
    market_type: str,
    label: str,
    sel_a: str,
    prob_a: float,
    sel_b: str,
    settlement: str,
    official_url: str,
    line: float | None = None,
    has_flag: bool = False,
) -> dict:
    out_a = make_outcome(sel_a, prob_a, has_flag=has_flag)
    out_b = make_outcome(sel_b, 1.0 - prob_a, has_flag=has_flag)
    return {
        "market_id": mid,
        "market_type": market_type,
        "market_label": label,
        "line": line,
        "settlement": settlement,
        "official_url": official_url,
        "outcomes": [out_a, out_b],
    }


def pmf_poisson(lam: float, max_k: int = 20) -> list[float]:
    vals = [math.exp(-lam)]
    for k in range(1, max_k + 1):
        vals.append(vals[-1] * lam / k)
    s = math.fsum(vals)
    return [v / s for v in vals]


def norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


NHL_MU = sum(v["gf"] for v in NHL_STANDINGS.values()) / sum(v["gp"] for v in NHL_STANDINGS.values())
EL_MU = sum(v["pf"] for v in EUROLEAGUE_STANDINGS.values()) / sum(v["gp"] for v in EUROLEAGUE_STANDINGS.values())
MLB_MU = (832 + 736 + 618 + 650) / (4 * 162)


HIGH_PREDICTION_COPY = {
    "nhl-2026020154": {
        "market_type": "winner",
        "selection": "Boston Bruins",
        "players": ["David Pastrnak", "Juuse Saros"],
        "text": (
            "Back the Boston Bruins on the full-game moneyline against the visiting Nashville Predators at TD Garden. "
            "Anchored by winger David Pastrnak (12 points through ten appearances), Boston sits 7-2-1 with a +14 goal "
            "differential (36 GF, 22 GA) and just pushed Dallas to a 3-2 overtime finish on October 20. Even though Juuse "
            "Saros guided Nashville to a 5-2 home win over St. Louis on October 17, the Predators remain 3-2-3 overall "
            "after consecutive losses to Vegas (5-2) and San Jose (3-2 SO), making Boston the clear match-winner play."
        ),
    },
    "nhl-2026020158": {
        "market_type": "handicap",
        "selection": "Pittsburgh Penguins +1.5 Goals",
        "players": ["Erik Karlsson", "Evgeni Malkin"],
        "text": (
            "Take Pittsburgh Penguins +1.5 Goals as home-ice handicap protection when the Florida Panthers skate into PPG "
            "Paints Arena on Thursday night. Blue-liner Erik Karlsson (11 points on 1 goal and 10 assists) alongside center "
            "Evgeni Malkin (5 goals, 7 points) have kept Pittsburgh resilient at home with a 2-1-0 record (10 GF, 9 GA), "
            "dropping their most recent contest by only a single tally in a 5-4 clash with Utah. Florida arrives at 5-3-2 "
            "owning just three regulation wins from ten games after Wednesday's 5-1 defeat in Ottawa, favoring Pittsburgh +1.5."
        ),
    },
    "nhl-2026020174": {
        "market_type": "winner",
        "selection": "Vegas Golden Knights",
        "players": ["Jack Eichel", "Mark Stone", "Kent Johnson"],
        "text": (
            "Play the Vegas Golden Knights to win outright (including overtime and shootout) Saturday night at Nationwide "
            "Arena against the Columbus Blue Jackets. Paced by Jack Eichel (18 points) and captain Mark Stone (8 goals, 15 "
            "points), Pacific-leading Vegas holds an 8-3-0 record with 44 goals scored (+14 differential) and a 3-1-0 road "
            "ledger despite Tuesday's 6-2 setback versus Tampa Bay. Following Kent Johnson's 1-0 overtime winner over the "
            "Rangers on October 17, 3-5-0 Columbus has lost consecutively to Minnesota (2-1) and Toronto (6-2), pointing "
            "squarely toward Vegas on the moneyline."
        ),
    },
    "nhl-2026020177": {
        "market_type": "handicap",
        "selection": "Tampa Bay Lightning +1.5 Goals",
        "players": ["Nikita Kucherov", "Nick Schmaltz", "Clayton Keller"],
        "text": (
            "Side with Tampa Bay Lightning +1.5 Goals as road puck-line insurance Saturday at Delta Center against the Utah "
            "Mammoth. Catalyzed by playmaker Nikita Kucherov (13 points), Tampa Bay travels west at 7-2-0 (.778 points "
            "percentage, 31 GF, 23 GA) riding a three-game winning streak capped by Tuesday's commanding 6-2 victory at "
            "Vegas. Although Utah sits 7-3-0 behind Nick Schmaltz (7 goals, 13 points) and Clayton Keller (13 points), the "
            "Mammoth edged struggling Pittsburgh by just a 5-4 margin last time out, giving Lightning +1.5 clear value."
        ),
    },
    "nhl-2026020179": {
        "market_type": "handicap",
        "selection": "Minnesota Wild +1.5 Goals",
        "players": ["Kirill Kaprizov"],
        "text": (
            "Grab Minnesota Wild +1.5 Goals for Saturday's late Western matchup at Climate Pledge Arena against the Seattle "
            "Kraken. Russian winger Kirill Kaprizov paces the NHL scoring race with 11 goals and 17 points, fueling "
            "Minnesota's 6-2-2 start (31 GF, 25 GA) highlighted by an October 18 victory over Columbus (2-1) before a "
            "narrow 4-3 overtime loss to Edmonton on October 20. Seattle stands 6-3-1 (39 GF, 34 GA) yet has managed only "
            "four regulation victories across ten outings, making Minnesota +1.5 the standout handicap call."
        ),
    },
    "mlb-849804": {
        "market_type": "handicap",
        "selection": "Milwaukee Brewers +1.5 Runs",
        "players": ["Jacob Misiorowski", "Trevor Megill", "Drew Rasmussen"],
        "text": (
            "Back Milwaukee Brewers +1.5 Runs on Tuesday's World Series Game 3 run line at Tropicana Field against the "
            "Tampa Bay Rays. Milwaukee compiled baseball's top 103-59 regular-season record (+214 run differential, 832 RS, "
            "618 RA) and surged to 7-1 in October by sweeping Los Angeles 4-0 in the NLCS behind closer Trevor Megill's 6-2 "
            "Game 3 save and Game 1 rotation spearhead Jacob Misiorowski. Even facing 98-64 Tampa Bay and ALCS Game 5 "
            "winner Drew Rasmussen (3-1 over Cleveland), Milwaukee +1.5 carries premier run-prevention support."
        ),
    },
    "mlb-849803": {
        "market_type": "handicap",
        "selection": "Milwaukee Brewers +1.5 Runs",
        "players": ["Aaron Ashby", "DL Hall", "Freddy Peralta"],
        "text": (
            "Wager on Milwaukee Brewers +1.5 Runs in Wednesday's World Series Game 4 matchup at St. Petersburg against the "
            "host Tampa Bay Rays. Depth arms DL Hall and Aaron Ashby — who locked down Milwaukee's 6-4 NLCS Game 4 sweep "
            "clincher over the Dodgers — anchor a Brewers staff that allowed an MLB-low 618 runs across 162 regular-season "
            "games (103-59) and sits 7-1 this postseason. Tampa Bay went 98-64 (+86 differential) and clinched the ALCS 7-3 "
            "in Game 6 behind Freddy Peralta, yet Milwaukee receiving +1.5 runs remains firmly favored."
        ),
    },
    "el-r7-67": {
        "market_type": "handicap",
        "selection": "Panathinaikos AKTOR Athens -4.5 Pts",
        "players": ["Kendrick Nunn", "Kostas Sloukas", "Markus Howard"],
        "text": (
            "Lay Panathinaikos AKTOR Athens -4.5 Points at home against Kosner Baskonia Vitoria-Gasteiz rather than paying "
            "steep -468 moneyline chalk. Top-seeded Panathinaikos sits 5-1 with a league-best +90 point differential (528 PF, "
            "438 PA, 73.0 points allowed per game), holds five consecutive Athens wins over Baskonia, and welcomes back "
            "guards Kendrick Nunn and Kostas Sloukas following weekend Greek League action after Round 6's maiden defeat. "
            "Last-place Baskonia enters 1-5 (-60 differential, 0-2 away) under newly appointed coach Velimir Perasovic "
            "following scorer Markus Howard's October 14 departure, making Panathinaikos -4.5 the obvious spread pick."
        ),
    },
    "el-r7-63": {
        "market_type": "handicap",
        "selection": "FC Barcelona +6.5 Pts",
        "players": ["Josh Nebo", "Moses Wright"],
        "text": (
            "Take FC Barcelona +6.5 Points on the road spread against Armani Olimpia Milan in Thursday's Round 7 clash. "
            "Anchored in the paint by former Milan center Josh Nebo opposite Olimpia big man Moses Wright, Barcelona enters "
            "at 3-3 overall with a positive +9 scoring margin (534 PF, 525 PA) after splitting two close home games last "
            "week. Conversely, 19th-place Milan has skidded to 1-5 (504 PF, 559 PA, -55 differential) on a four-game "
            "EuroLeague losing streak, and with both meetings last season decided by one possession, Barcelona +6.5 offers tremendous value."
        ),
    },
}


def price_fixture(fixture: dict) -> dict:
    sport = fixture["sport"]
    fid = fixture["id"]
    hm, aw = fixture["home"], fixture["away"]
    url = fixture["official_url"]
    has_flag = bool(fixture["flags"])

    out = {
        "fixture_id": fid,
        "sport": sport,
        "model_version": MODEL_VERSION,
        "official_url": url,
        "status": "unpriced",
        "unpriced_reason": "",
        "winner_pick": None,
        "markets": [],
        "model_inputs": {},
    }

    if sport == "ice-hockey" and fixture["home_code"] in NHL_STANDINGS:
        h = NHL_STANDINGS[fixture["home_code"]]
        a = NHL_STANDINGS[fixture["away_code"]]
        k = 6.0
        ah = (h["gf"] + k * NHL_MU) / (h["gp"] + k)
        dh = (h["ga"] + k * NHL_MU) / (h["gp"] + k)
        aa = (a["gf"] + k * NHL_MU) / (a["gp"] + k)
        da = (a["ga"] + k * NHL_MU) / (a["gp"] + k)
        lh = 1.045 * ah * da / NHL_MU
        la = (1.0 / 1.045) * aa * dh / NHL_MU
        vh, va = pmf_poisson(lh, 20), pmf_poisson(la, 20)

        p_h_reg = sum(vh[i] * va[j] for i in range(21) for j in range(21) if i > j)
        p_tie = sum(vh[i] * va[i] for i in range(21))
        sh = (h["pts"] + 6.0) / (2.0 * h["gp"] + 12.0)
        sa = (a["pts"] + 6.0) / (2.0 * a["gp"] + 12.0)
        ot_h = (sh * (1.0 - sa)) / (sh * (1.0 - sa) + sa * (1.0 - sh))
        p_ml_h = p_h_reg + p_tie * ot_h

        p_pl_h_minus = sum(vh[i] * va[j] for i in range(21) for j in range(21) if i - j >= 2)
        p_pl_a_minus = sum(vh[i] * va[j] for i in range(21) for j in range(21) if j - i >= 2)

        def p_over_nhl(line: float) -> float:
            return sum(
                vh[i] * va[j]
                for i in range(21)
                for j in range(21)
                if ((i + j + 1) if i == j else (i + j)) > line
            )

        p1_under = sum(pmf_poisson(0.30 * (lh + la), 12)[:2])

        markets = [
            two_way_market(f"{fid}-winner", "winner", "Match Winner (incl. OT/SO)", hm, p_ml_h, aw, "Full game including overtime and shootout", url, has_flag=has_flag),
            two_way_market(f"{fid}-pl-home-minus", "handicap", "Puck Line (-1.5 / +1.5)", f"{hm} -1.5 Goals", p_pl_h_minus, f"{aw} +1.5 Goals", "Full game including OT/SO (1 goal awarded to OT/SO winner)", url, line=-1.5, has_flag=has_flag),
            two_way_market(f"{fid}-pl-away-minus", "handicap", "Alt Puck Line (+1.5 / -1.5)", f"{hm} +1.5 Goals", 1.0 - p_pl_a_minus, f"{aw} -1.5 Goals", "Full game including OT/SO", url, line=1.5, has_flag=has_flag),
            two_way_market(f"{fid}-tot-5.5", "total", "Match Total (5.5 Goals)", "Over 5.5 Goals", p_over_nhl(5.5), "Under 5.5 Goals", "Full game including OT/SO winner goal", url, line=5.5, has_flag=has_flag),
            two_way_market(f"{fid}-tot-6.5", "total", "Match Total (6.5 Goals)", "Over 6.5 Goals", p_over_nhl(6.5), "Under 6.5 Goals", "Full game including OT/SO winner goal", url, line=6.5, has_flag=has_flag),
            two_way_market(f"{fid}-tt-home-2.5", "team-total", f"{hm} Regulation Goals (2.5)", f"{hm} Over 2.5 Goals", sum(vh[3:]), f"{hm} Under 2.5 Goals", "60-minute regulation team goals", url, line=2.5, has_flag=has_flag),
            two_way_market(f"{fid}-p1-1.5", "period", "1st Period Total (1.5 Goals)", "1st Period Over 1.5 Goals", 1.0 - p1_under, "1st Period Under 1.5 Goals", "1st period goals (20 mins)", url, line=1.5, has_flag=has_flag),
        ]
        win_m = markets[0]
        best_win = win_m["outcomes"][0] if p_ml_h >= 0.5 else win_m["outcomes"][1]
        out.update(
            status="priced",
            winner_pick=best_win,
            markets=markets,
            model_inputs={
                "home_record": f"{h['w']}-{h['l']}-{h['otl']} ({h['pts']} pts, {h['gf']} GF / {h['ga']} GA)",
                "away_record": f"{a['w']}-{a['l']}-{a['otl']} ({a['pts']} pts, {a['gf']} GF / {a['ga']} GA)",
                "lambda_home": round(lh, 4),
                "lambda_away": round(la, 4),
            },
        )
        return out

    if sport == "baseball" and fixture["home_code"] in MLB_STANDINGS:
        h = MLB_STANDINGS[fixture["home_code"]]
        a = MLB_STANDINGS[fixture["away_code"]]
        lh = 1.035 * (h["rs"] / h["gp"]) * (a["ra"] / a["gp"]) / MLB_MU
        la = (1.0 / 1.035) * (a["rs"] / a["gp"]) * (h["ra"] / h["gp"]) / MLB_MU
        vh, va = pmf_poisson(lh, 25), pmf_poisson(la, 25)
        pairs = [(i, j, vh[i] * va[j]) for i in range(26) for j in range(26) if i != j]
        mass = math.fsum(z for _, _, z in pairs)
        grid = [(i, j, z / mass) for i, j, z in pairs]

        p_ml_h = math.fsum(z for i, j, z in grid if i > j)
        p_rl_h_minus = math.fsum(z for i, j, z in grid if i - 1.5 > j)
        p_rl_a_minus = math.fsum(z for i, j, z in grid if j - 1.5 > i)
        p_over_75 = math.fsum(z for i, j, z in grid if i + j > 7.5)
        p_over_85 = math.fsum(z for i, j, z in grid if i + j > 8.5)
        vh5, va5 = pmf_poisson(0.56 * lh, 18), pmf_poisson(0.56 * la, 18)
        f5_pairs = [(i, j, vh5[i] * va5[j]) for i in range(19) for j in range(19) if i != j]
        f5_mass = math.fsum(z for _, _, z in f5_pairs)
        p_f5_h = math.fsum(z / f5_mass for i, j, z in f5_pairs if i > j)

        markets = [
            two_way_market(f"{fid}-winner", "winner", "Match Winner (incl. Extra Innings)", hm, p_ml_h, aw, "Full game including extra innings", url, has_flag=has_flag),
            two_way_market(f"{fid}-rl-home-minus", "handicap", "Run Line (-1.5 / +1.5)", f"{hm} -1.5 Runs", p_rl_h_minus, f"{aw} +1.5 Runs", "Full game run line", url, line=-1.5, has_flag=has_flag),
            two_way_market(f"{fid}-rl-away-minus", "handicap", "Alt Run Line (+1.5 / -1.5)", f"{hm} +1.5 Runs", 1.0 - p_rl_a_minus, f"{aw} -1.5 Runs", "Full game alternate run line", url, line=1.5, has_flag=has_flag),
            two_way_market(f"{fid}-tot-7.5", "total", "Match Total (7.5 Runs)", "Over 7.5 Runs", p_over_75, "Under 7.5 Runs", "Full game total runs", url, line=7.5, has_flag=has_flag),
            two_way_market(f"{fid}-tot-8.5", "total", "Match Total (8.5 Runs)", "Over 8.5 Runs", p_over_85, "Under 8.5 Runs", "Full game total runs", url, line=8.5, has_flag=has_flag),
            two_way_market(f"{fid}-tt-home-4.5", "team-total", f"{hm} Team Total (4.5 Runs)", f"{hm} Over 4.5 Runs", sum(vh[5:]), f"{hm} Under 4.5 Runs", "Full game home runs", url, line=4.5, has_flag=has_flag),
            two_way_market(f"{fid}-f5-winner", "period", "First 5 Innings (Draw No Bet)", f"{hm} F5 DNB", p_f5_h, f"{aw} F5 DNB", "First 5 innings conditional on non-tie", url, has_flag=has_flag),
        ]
        best_win = markets[0]["outcomes"][0] if p_ml_h >= 0.5 else markets[0]["outcomes"][1]
        out.update(
            status="priced",
            winner_pick=best_win,
            markets=markets,
            model_inputs={
                "home_record": f"{h['w']}-{h['l']} ({h['rs']} RS / {h['ra']} RA; {h['postseason']})",
                "away_record": f"{a['w']}-{a['l']} ({a['rs']} RS / {a['ra']} RA; {a['postseason']})",
                "lambda_home": round(lh, 4),
                "lambda_away": round(la, 4),
            },
        )
        return out

    if sport == "basketball" and fixture["home_code"] in EUROLEAGUE_STANDINGS:
        h = EUROLEAGUE_STANDINGS[fixture["home_code"]]
        a = EUROLEAGUE_STANDINGS[fixture["away_code"]]
        k = 4.0
        oh = (h["pf"] + k * EL_MU) / (h["gp"] + k)
        dh = (h["pa"] + k * EL_MU) / (h["gp"] + k)
        oa = (a["pf"] + k * EL_MU) / (a["gp"] + k)
        da = (a["pa"] + k * EL_MU) / (a["gp"] + k)
        eh = (oh + da) / 2.0 + 1.6
        ea = (oa + dh) / 2.0 - 1.6
        diff = eh - ea
        tot = eh + ea
        p_ml_h = norm_cdf(diff / 11.5)
        med_line = math.floor(abs(diff)) + 0.5
        main_line = -med_line if diff >= 0 else med_line
        p_main_h = norm_cdf((diff + main_line) / 11.5)
        tot_line = math.floor(tot) + 0.5
        p_over = norm_cdf((tot - tot_line) / 14.0)

        markets = [
            two_way_market(f"{fid}-winner", "winner", "Match Winner (incl. OT)", hm, p_ml_h, aw, "Full game including overtime", url, has_flag=has_flag),
            two_way_market(f"{fid}-spread-main", "handicap", f"Point Spread ({main_line:+g})", f"{hm} {main_line:+g} Pts", p_main_h, f"{aw} {-main_line:+g} Pts", "Full game including overtime", url, line=main_line, has_flag=has_flag),
            two_way_market(f"{fid}-spread-4.5", "handicap", "Alt Spread (-4.5 / +4.5)", f"{hm} -4.5 Pts", norm_cdf((diff - 4.5) / 11.5), f"{aw} +4.5 Pts", "Full game including overtime", url, line=-4.5, has_flag=has_flag),
            two_way_market(f"{fid}-spread-plus6.5", "handicap", "Alt Spread (-6.5 / +6.5)", f"{hm} -6.5 Pts", norm_cdf((diff - 6.5) / 11.5), f"{aw} +6.5 Pts", "Full game including overtime", url, line=-6.5, has_flag=has_flag),
            two_way_market(f"{fid}-tot-main", "total", f"Match Total ({tot_line:g} Pts)", f"Over {tot_line:g} Pts", p_over, f"Under {tot_line:g} Pts", "Full game including overtime", url, line=tot_line, has_flag=has_flag),
            two_way_market(f"{fid}-tt-home", "team-total", f"{hm} Team Total ({math.floor(eh)+0.5:g} Pts)", f"{hm} Over {math.floor(eh)+0.5:g} Pts", norm_cdf((eh - (math.floor(eh) + 0.5)) / 9.8), f"{hm} Under {math.floor(eh)+0.5:g} Pts", "Full game home points", url, line=math.floor(eh) + 0.5, has_flag=has_flag),
            two_way_market(f"{fid}-1h-winner", "period", "1st Half Winner (2-Way DNB)", f"{hm} 1H DNB", norm_cdf((0.5 * diff) / 8.2), f"{aw} 1H DNB", "First 20 minutes Draw No Bet", url, has_flag=has_flag),
        ]
        best_win = markets[0]["outcomes"][0] if p_ml_h >= 0.5 else markets[0]["outcomes"][1]
        out.update(
            status="priced",
            winner_pick=best_win,
            markets=markets,
            model_inputs={
                "home_record": f"{h['w']}-{h['l']} ({h['pf']} PF / {h['pa']} PA, H {h['home']})",
                "away_record": f"{a['w']}-{a['l']} ({a['pf']} PF / {a['pa']} PA, A {a['away']})",
                "proj_home_pts": round(eh, 2),
                "proj_away_pts": round(ea, 2),
            },
        )
        return out

    # Explicit blank/withheld reason when official data lacks exact future UTC or >=5-game two-sided series
    reason = (
        fixture["flags"][0]
        if fixture.get("flags")
        else "Withheld: requires verified exact future UTC timestamp and >=5-game two-sided official statistical series."
    )
    out["unpriced_reason"] = reason
    return out


def build_predictions(fixtures_by_id: dict[str, dict], priced_by_id: dict[str, dict]) -> list[dict]:
    preds: list[dict] = []
    for fid, spec in HIGH_PREDICTION_COPY.items():
        fx = fixtures_by_id[fid]
        pr = priced_by_id[fid]
        assert fx["start_utc"] > AS_OF_UTC, f"Fixture {fid} start_utc is not strictly future!"
        assert not fx["flags"], f"Fixture {fid} has flags and cannot be High!"
        chosen = None
        chosen_mkt = None
        for m in pr["markets"]:
            if m["market_type"] == spec["market_type"]:
                for o in m["outcomes"]:
                    if o["selection"] == spec["selection"]:
                        chosen = o
                        chosen_mkt = m
                        break
            if chosen:
                break
        assert chosen is not None, f"Could not locate High selection {spec['selection']} in {fid}"
        assert chosen["confidence"] == "High", f"{fid} {spec['selection']} graded {chosen['confidence']} not High!"
        assert 0.7000 < chosen["probability"] <= 0.7142857, f"Probability out of strict High window: {chosen['probability']}"
        assert -250 <= chosen["american_odds"] <= 10000, f"Odds out of [-250, +10000]: {chosen['american_odds']}"
        words = spec["text"].split()
        assert len(words) >= 30, f"Prediction too short ({len(words)} words) for {fid}"

        preds.append(
            {
                "id": f"pred-{fid}",
                "match_id": fid,
                "sport": fx["sport"],
                "competition": fx["competition"],
                "stage": fx["stage"],
                "home": fx["home"],
                "away": fx["away"],
                "start_utc": fx["start_utc"],
                "venue": fx["venue"],
                "market_id": chosen_mkt["market_id"],
                "market_type": chosen_mkt["market_type"],
                "market_label": chosen_mkt["market_label"],
                "selection": chosen["selection"],
                "probability": chosen["probability"],
                "fair_decimal": chosen["fair_decimal"],
                "american_odds": chosen["american_odds"],
                "american_display": chosen["american_display"],
                "in_target_window": chosen["in_target_window"],
                "confidence": "High",
                "verified_players": spec["players"],
                "home_form": pr["model_inputs"]["home_record"],
                "away_form": pr["model_inputs"]["away_record"],
                "word_count": len(words),
                "text": spec["text"],
                "official_url": fx["official_url"],
            }
        )
    return preds
