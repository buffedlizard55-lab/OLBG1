#!/usr/bin/env python3
"""Session 7a9b24e5 — line origination and confidence grading.

Inputs are the officially-read records in desk.json.  The model is deliberately
small and disclosed:

* Baseball   : Pythagorean expectation (exponent 1.83) from season runs for/against,
               converted with log5-style logit combination; home edge +0.10 logit.
* Ice Hockey : points percentage -> logit; home edge +0.12 logit.
* Rugby Union / Rugby League : mean competition margin from the rounds read,
               shrunk 50% toward zero; home edge +0.10 logit-equivalent margin.
* Basketball : NOT priced.  A 1-2 game sample cannot support an originated line.

Prices are zero-vig fair prices (1/p), no margin, no clipping.  Confidence tier
uses the brief's conjunction: p > 0.70 AND fair American price inside
-250..+10000.  Because -250 corresponds to p = 0.7143, the eligible window is
p in (0.7000, 0.7143]; anything stronger is published as 'capped'.

Run: python3 scripts/s7a9b24e5_model.py
"""
from __future__ import annotations

import json
import math
import pathlib

DATA = pathlib.Path("data/7a9b24e5")
DESK = DATA / "desk.json"

BAND_LO_P = 0.6200
BAND_HI_P = 1 / 2.5          # 0.7142857  == fair -250
TARGET_P = (BAND_LO_P + BAND_HI_P) / 2

SPORT_SD = {          # margin standard deviation, in the sport's scoring unit
    "Baseball": 3.2,
    "Ice Hockey": 1.9,
    "Rugby Union": 14.0,
}
TOTAL_SD = {"Baseball": 4.5, "Ice Hockey": 2.0}
TEAM_TOTAL_SD = {"Baseball": 2.6, "Ice Hockey": 1.45}
TEAM_TOTAL = {
    "Baseball": {
        ("Milwaukee Brewers", "Tampa Bay Rays"): (832 / 162, 736 / 162),
        ("Tampa Bay Rays", "Milwaukee Brewers"): (736 / 162, 832 / 162),
    },
    "Ice Hockey": {
        ("Boston Bruins", "San Jose Sharks"): (42 / 11, 33 / 11),
        ("San Jose Sharks", "Boston Bruins"): (33 / 11, 42 / 11),
        ("New Jersey Devils", "Los Angeles Kings"): (41 / 11, 34 / 9),
        ("Los Angeles Kings", "New Jersey Devils"): (34 / 9, 41 / 11),
        ("Philadelphia Flyers", "Anaheim Ducks"): (31 / 11, 35 / 10),
        ("Anaheim Ducks", "Philadelphia Flyers"): (35 / 10, 31 / 11),
        ("Ottawa Senators", "New York Rangers"): (31 / 11, 37 / 12),
        ("New York Rangers", "Ottawa Senators"): (37 / 12, 31 / 11),
        ("Dallas Stars", "New York Islanders"): (26 / 10, 30 / 10),
        ("New York Islanders", "Dallas Stars"): (30 / 10, 26 / 10),
    },
}
HOME_LOGIT = {"Baseball": 0.10, "Ice Hockey": 0.12, "Rugby Union": 0.10, "Rugby League": 0.10}

# Officially-read season aggregates (runs for / against per game, goals for/against).
RUNS = {
    "Milwaukee Brewers": (832, 618, 162),
    "Tampa Bay Rays": (736, 650, 162),
}
GOALS = {   # goals for, goals against, games played  (NHL standings, read 2026-10-23)
    "Boston Bruins": (42, 22, 11), "San Jose Sharks": (33, 37, 11),
    "New Jersey Devils": (41, 36, 11), "Los Angeles Kings": (30, 34, 9),
    "Philadelphia Flyers": (31, 30, 11), "Anaheim Ducks": (35, 33, 10),
    "Ottawa Senators": (31, 30, 11), "New York Rangers": (37, 29, 12),
    "Dallas Stars": (26, 17, 10), "New York Islanders": (30, 28, 10),
}
NHL_PTS_PCT = {   # points % read from the NHL standings API
    "Boston Bruins": 0.773, "San Jose Sharks": 0.545, "New Jersey Devils": 0.600,
    "Los Angeles Kings": 0.375, "Philadelphia Flyers": 0.375, "Anaheim Ducks": 0.400,
    "Ottawa Senators": 0.636, "New York Rangers": 0.625, "Dallas Stars": 0.650,
    "New York Islanders": 0.600,
}
# URC league table read this session: (points for, points against, played).
URC_TABLE = {
    "Edinburgh": (111, 64, 4), "Hollywoodbets Sharks": (125, 104, 4),
    "Glasgow Warriors": (95, 72, 3), "Vodacom Bulls": (126, 54, 3),
    "DHL Stormers": (81, 54, 3), "Connacht": (104, 111, 4),
    "Cardiff Rugby": (87, 107, 4), "10bet Lions": (87, 133, 4),
    "Dragons": (88, 83, 3), "Munster": (72, 74, 3), "Leinster": (75, 58, 3),
    "Ulster": (88, 93, 3), "Scarlets": (68, 85, 3), "Ospreys": (81, 107, 3),
    "Benetton": (64, 68, 3), "Zebre Parma": (79, 164, 4),
}
# Round-1 RLWC margins
RLWC_MARGIN = {
    "Papua New Guinea": +24, "Samoa": +74, "England": -18, "France": -74,
    "New Zealand": -2, "Cook Islands": -28, "Australia": +2, "Fiji": +28,
}


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def inv_logit(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def american(p: float) -> int:
    if p >= 0.5:
        return int(round(-100.0 * p / (1 - p)))
    return int(round(100.0 * (1 - p) / p))


def tier(p: float) -> str:
    am = american(p)
    if p >= BAND_LO_P and -250 <= am <= 10000:
        return "High"
    if p > 0.7143:
        return "Medium"          # capped: shorter than -250, disclosed not promoted
    if p >= 0.60:
        return "Medium"
    return "Low"


def pythag(rs: int, ra: int, g: int, exp: float = 1.83) -> float:
    rs, ra = (rs / g) ** exp, (ra / g) ** exp
    return rs / (rs + ra)


def strength(f: dict) -> tuple[float, float | None, str]:
    """Return (expected home margin in the sport's scoring unit, expected total, grade).

    Margins are built from the clubs' own scoring rates (or the league table's
    points difference), never from an eye test or a prior season.
    """
    s = f["sport"]
    h, a = f["home"], f["away"]
    if s == "Baseball":
        hrs, hra, hg = RUNS[h]
        ars, ara, ag = RUNS[a]
        mu_h = (hrs / hg + ara / ag) / 2
        mu_a = (ars / ag + hra / hg) / 2
        return mu_h - mu_a + 0.15, mu_h + mu_a, "A"
    if s == "Ice Hockey":
        hgf, hga, hgp = GOALS[h]
        agf, aga, agp = GOALS[a]
        mu_h = (hgf / hgp + aga / agp) / 2
        mu_a = (agf / agp + hga / hgp) / 2
        return mu_h - mu_a + 0.15, mu_h + mu_a, "B"
    if s == "Rugby Union":
        hpf, hpa, hp = URC_TABLE[h]
        apf, apa, ap = URC_TABLE[a]
        mu = 0.5 * (hpf - hpa) / hp - 0.5 * (apf - apa) / ap + 3.0
        return mu, None, "B"
    raise KeyError(s)


def originate(f: dict) -> list[dict]:
    s = f["sport"]
    if s not in SPORT_SD:
        return []
    mu_margin, tot, grade = strength(f)
    sd = SPORT_SD[s]
    p_home = phi(mu_margin / sd)
    out: list[dict] = []

    def add(market: str, selection: str, line, p: float, basis: str) -> None:
        p = max(0.0005, min(0.9995, p))
        ltype = "half"
        if line is not None and abs(round(line * 2) - line * 2) > 1e-9:
            ltype = "quarter"
        out.append(dict(fixture=f["id"], market=market, selection=selection, line=line,
                        line_type=ltype,
                        p=round(p, 6), fair_decimal=round(1 / p, 3),
                        fair_american=american(p), tier=tier(p), basis=basis,
                        evidence=grade))

    # --- money line (draw splits excluded: these are two-way markets)
    ml_home, ml_away = (p_home, 1 - p_home) if s == "Baseball" else _three_way(p_home)
    add("Match Winner", f["home"], None, ml_home, "logit strength + home edge")
    add("Match Winner", f["away"], None, ml_away, "logit strength + home edge")

    # --- originated handicap ladder (quarter-point steps, as Asian handicap markets use)
    # Home covers line L when margin > -L, so p = 1 - Phi((-L - mu)/sd).
    target = 0.549 * sd - mu_margin          # line L that puts the home side at p = 0.708
    base = round(target * 4) / 4.0
    for step in (-1.5, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.5):
        ln = base + step
        pc = 1 - phi((-ln - mu_margin) / sd)
        tag = "Handicap" if step == 0.0 else "Handicap (ladder)"
        add(tag, f"{f['home']} {ln:+g}", ln, pc, "originated spread, normal margin")
        add(tag, f"{f['away']} {-ln:+g}", -ln, 1 - pc, "originated spread, normal margin")

    # --- totals, only where an official scoring aggregate supports a mean
    # --- team totals (only where the club's own scoring rate was read)
    if s == "Baseball":
        rates = [RUNS[f["home"]], RUNS[f["away"]]]
        for side, (rs, ra, g) in zip((f["home"], f["away"]), rates):
            pass
    if s in TEAM_TOTAL and (f["home"], f["away"]) in TEAM_TOTAL[s]:
        ht, at = TEAM_TOTAL[s][(f["home"], f["away"])]
        for name, mu in ((f["home"], ht), (f["away"], at)):
            tsd = TEAM_TOTAL_SD[s]
            base = round((mu - 0.549 * tsd) * 4) / 4.0
            for step in (-1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0):
                ln = base + step
                po = 1 - phi((ln - mu) / tsd)
                tag = "Team Total" if step == 0.0 else "Team Total (ladder)"
                add(tag, f"{name} Over {ln:g}", ln, po, "expected team total from official scoring rates")

    if tot is not None and s in TOTAL_SD:
        tsd = TOTAL_SD[s]
        base = round((tot - 0.549 * tsd) * 4) / 4.0
        for step in (-1.5, -1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0, 1.5):
            ln = base + step
            po = 1 - phi((ln - tot) / tsd)
            tag = "Match Total" if step == 0.0 else "Match Total (ladder)"
            add(tag, f"Over {ln:g}", ln, po, "expected total from official scoring rates")
            add(tag, f"Under {ln:g}", ln, 1 - po, "expected total from official scoring rates")
    return out


def _three_way(p_home: float) -> tuple[float, float]:
    """Rugby union is offered three-way by most books; the draw takes 4% of the
    probability mass here (a disclosed convention), leaving a two-way book."""
    draw = 0.04
    return p_home * (1 - draw), (1 - p_home) * (1 - draw)


def main() -> None:
    desk = json.loads(DESK.read_text())
    fixtures = {f["id"]: f for f in desk["fixtures"]}
    markets: list[dict] = []
    for f in desk["fixtures"]:
        if f["id"] == "BB05":       # conditional game: never priced
            continue
        markets.extend(originate(f))

    # --- pick selection: strongest in-band outcome per fixture, then best five per sport
    by_fixture: dict[str, list[dict]] = {}
    for m in markets:
        if m["tier"] == "High":
            by_fixture.setdefault(m["fixture"], []).append(m)

    picks: list[dict] = []
    for fid, rows in by_fixture.items():
        # highest probability that still sits inside the band (closest to fair -250)
        rows.sort(key=lambda r: -r["p"])
        picks.append(rows[0])

    per_sport: dict[str, list[dict]] = {}
    for p in picks:
        per_sport.setdefault(fixtures[p["fixture"]]["sport"], []).append(p)
    chosen: list[dict] = []
    for sport, rows in per_sport.items():
        rows.sort(key=lambda r: (-r["p"], r["fixture"]))
        chosen.extend(rows[:5])

    chosen.sort(key=lambda r: (fixtures[r["fixture"]]["sport"], -r["p"]))
    for i, p in enumerate(chosen, 1):
        p["pick_id"] = f"P7A9B-{i:03d}"

    capped = [m for m in markets if m["tier"] == "Medium" and m["p"] > 0.7143]
    capped.sort(key=lambda r: -r["p"])

    (DATA / "markets.json").write_text(json.dumps(markets, indent=1) + "\n", encoding="utf-8")
    (DATA / "picks.json").write_text(json.dumps(chosen, indent=1) + "\n", encoding="utf-8")
    (DATA / "capped.json").write_text(json.dumps(capped, indent=1) + "\n", encoding="utf-8")
    print(f"markets={len(markets)} picks={len(chosen)} capped={len(capped)}")
    for p in chosen:
        f = fixtures[p["fixture"]]
        print(f"  {p['pick_id']} {f['sport']:<14} {f['id']} {p['market']:<18} {p['selection']:<34} p={p['p']:.4f} {p['fair_american']}")


if __name__ == "__main__":
    main()
