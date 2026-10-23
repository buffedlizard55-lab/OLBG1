#!/usr/bin/env python3
"""Session 496eaf02 — originated pricing engine (zero-vig fair prices).

Policy (documented on the desk's methodology page):
* Eligible price band : fair American price in [-250, +10000]
                        <=> 0.009901 <= p <= 0.714286
* High-A              : p >= 0.70 and inside the band
* High-B              : 0.62 <= p < 0.70 and inside the band
* Medium              : 0.50 <= p < 0.62, or p > 0.714286 (price-capped out of band)
* Low                 : everything else, or any fixture without two officially sourced inputs

The desk sets its own spread / total lines: the line is chosen (half-point search)
so the model's cover / over probability is 0.66 — the midpoint of the High window —
unless no line in the search range reaches it, in which case the balanced line
(expected margin / expected total, rounded to the half) is used. No bookmaker price,
edge or missing-input default is inserted.
"""
from __future__ import annotations

import math

BAND_MIN_AMERICAN = -250
BAND_MAX_AMERICAN = 10000
BAND_P_MAX = 250.0 / 350.0          # 0.7142857
BAND_P_MIN = 100.0 / (100.0 + 10000.0)
HIGH_A_FLOOR = 0.70
HIGH_B_FLOOR = 0.62
MED_FLOOR = 0.50
LINE_TARGET = 0.66                  # midpoint of the High window

HOME_EDGE = {"ice-hockey": 0.04, "baseball": 0.05, "basketball": 0.05, "el": 0.05, "urc": 0.06,
             "rugby-league": 0.05, "handball": 0.05, "volleyball": 0.05,
             "cricket": 0.04, "gaelic-sports": 0.05}

# margin / total parameters: mu_margin = scale*(wA - wB); mu_total = base + scale*(wA - wB)
MARGIN = {"basketball": (28.0, 12.0), "el": (25.0, 11.0), "ice-hockey": (6.0, 1.6),
          "baseball": (6.0, 2.7), "urc": (35.0, 13.0), "rugby-league": (40.0, 16.0),
          "handball": (10.0, 7.0), "volleyball": (60.0, 18.0), "cricket": (120.0, 45.0),
          "gaelic-sports": (25.0, 12.0)}
TOTAL = {"basketball": (222.0, 20.0, 12.0), "el": (164.0, 15.0, 11.0), "ice-hockey": (5.6, 1.5, 1.6),
         "baseball": (8.7, 3.0, 2.7), "urc": (48.0, 12.0, 13.0), "rugby-league": (42.0, 12.0, 16.0),
         "handball": (58.0, 8.0, 7.0), "volleyball": (150.0, 30.0, 20.0), "cricket": (290.0, 50.0, 45.0),
         "gaelic-sports": (40.0, 15.0, 12.0)}
TOTAL["cricket-t20"] = (165.0, 60.0, 25.0)

SPORT_UNIT = {"basketball": "points", "el": "points", "ice-hockey": "goals", "baseball": "runs",
              "urc": "points", "rugby-league": "points", "handball": "goals",
              "volleyball": "points", "cricket": "runs", "gaelic-sports": "points"}


# --------------------------------------------------------------- odds helpers
def american(dec: float) -> int:
    if dec >= 2.0:
        return int(round((dec - 1.0) * 100.0))
    return -int(round(100.0 / max(dec - 1.0, 0.01)))


def fmt_american(dec: float) -> str:
    a = american(dec)
    return f"+{a}" if a > 0 else str(a)


def in_band(p: float) -> bool:
    return BAND_P_MIN <= p <= BAND_P_MAX


def confidence_for(p: float, rated: bool) -> str:
    if not rated:
        return "low"
    if in_band(p) and p >= HIGH_A_FLOOR:
        return "high"
    if in_band(p) and p >= HIGH_B_FLOOR:
        return "high"
    if p >= MED_FLOOR:
        return "medium"
    return "low"


def tier_for(p: float, rated: bool) -> str:
    if not rated:
        return "Unrated"
    if in_band(p) and p >= HIGH_A_FLOOR:
        return "High-A"
    if in_band(p) and p >= HIGH_B_FLOOR:
        return "High-B"
    if p > BAND_P_MAX:
        return "Medium (price-capped)"
    if p >= MED_FLOOR:
        return "Medium"
    return "Low"


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def poisson_over(line: float, lam: float, cap: int = 60) -> float:
    """P(total > line) for a Poisson total with mean lam; line is a half-number."""
    k = math.floor(line) + 1
    return sum(poisson_pmf(i, lam) for i in range(k, cap + 1))


def first_to_n(q: float, n: int) -> float:
    """P(player wins a first-to-n contest) given per-unit win probability q."""
    return sum(math.comb(n - 1 + k, k) * q ** n * (1 - q) ** k for k in range(0, n))


def match_from_unit(q: float, n: int, format_label: str) -> dict:
    """Outcome dict for a first-to-n market."""
    return {"selection": format_label, "probability": round(first_to_n(q, n), 6)}


# ------------------------------------------------------------------- inputs
def win_pct(inp: dict) -> float:
    """Official win percentage from a team/series input (draws = 0.5 wins)."""
    if "w" in inp and "l" in inp:
        d = inp.get("d", 0)
        return (inp["w"] + 0.5 * d) / (inp["w"] + inp["l"] + d)
    if "rating" in inp:
        return inp["rating"]
    return None


def player_unit_q(a_inp: dict, b_inp: dict, kind: str) -> float:
    """Per-set / per-leg / per-frame win probability for player sports."""
    if kind in ("rank", "seed"):  # tennis: Bradley-Terry on (100/rank)^0.3
        ra = a_inp["rank"] if "rank" in a_inp else float(a_inp.get("seed", 20)) * 3.5
        rb = b_inp["rank"] if "rank" in b_inp else float(b_inp.get("seed", 20)) * 3.5
        sa = (100.0 / max(ra, 1)) ** 0.3
        sb = (100.0 / max(rb, 1)) ** 0.3
        return sa / (sa + sb)
    if kind == "merit":  # darts: Bradley-Terry on prize money (£k), exponent 0.2
        sa, sb = a_inp["prize"] ** 0.2, b_inp["prize"] ** 0.2
        return sa / (sa + sb)
    if kind == "prize":  # snooker: Bradley-Terry on WST prize (£), exponent 0.2
        sa, sb = a_inp["prize"] ** 0.2, b_inp["prize"] ** 0.2
        return sa / (sa + sb)
    return None


def winner_probability(fx: dict) -> tuple[float, str]:
    """(p_home, rating_kind) for a fixture."""
    inp = fx["inputs"]
    kind = inp["kind"]
    if kind in ("team", "series", "pool", "mlb", "nhl", "nba", "el", "urc", "rating"):
        if kind == "pool":  # Rugby League World Cup: documented pool-position strength
            pa = inp["a"].get("p", 0.5)
            pb = inp["b"].get("p", 0.5)
            return pa, "team"
        if kind == "rating":  # cricket team ratings (documented input)
            ra, rb = inp["a"]["rating"], inp["b"]["rating"]
            sport = fx["sport"]
            h = HOME_EDGE.get(sport, 0.04)
            p = (ra + h) / ((ra + h) + rb)
            return max(0.2, min(0.85, p)), "team"
        if kind == "mlb":
            wa = inp["a"]["w"] / (inp["a"]["w"] + inp["a"]["l"])
            wb = inp["b"]["w"] / (inp["b"]["w"] + inp["b"]["l"])
        elif kind == "nhl":
            wa = inp["a"]["ppg"] / 2.0 / inp["a"]["gp"]
            wb = inp["b"]["ppg"] / 2.0 / inp["b"]["gp"]
        elif kind == "nba":
            wa = (inp["a"]["w"] + 5.0) / (inp["a"]["w"] + inp["a"]["l"] + 10.0)
            wb = (inp["b"]["w"] + 5.0) / (inp["b"]["w"] + inp["b"]["l"] + 10.0)
        else:
            wa, wb = win_pct(inp["a"]), win_pct(inp["b"])
            if wa is None or wb is None:
                return None, "low"
        wa = max(0.25, min(0.75, wa))
        wb = max(0.25, min(0.75, wb))
        adj = inp["a"].get("adj", 0.0)
        wa = max(0.2, min(0.8, wa + adj))
        sport = fx["sport"]
        h = HOME_EDGE.get(sport, 0.05)
        p = 0.5 + 0.5 * (wa - wb) + h
        return max(0.2, min(0.85, p)), "team"
    if kind in ("rank", "seed", "merit", "prize"):
        q = player_unit_q(inp["a"], inp["b"], kind)
        if q is None:
            return None, "low"
        n = 2 if kind in ("rank", "seed") else (10 if kind == "merit" else 6)
        return first_to_n(q, n), "player"
    if kind == "form":  # Gaelic / greyhounds: documented form-based estimate
        if "form_p" in inp:
            return inp["form_p"], "form"
        return None, "low"
    if kind == "outright":  # golf H2H
        return None, "outright"
    if kind == "f1":
        return None, "f1"
    return None, "low"


def margin_mu(fx: dict, wa: float, wb: float) -> float:
    sport = "urc" if fx["sport"] == "rugby-union" else fx["sport"]
    if sport in MARGIN:
        return MARGIN[sport][0] * (wa - wb)
    return None


def total_mu(fx: dict, wa: float, wb: float) -> float:
    sport = "urc" if fx["sport"] == "rugby-union" else fx["sport"]
    if sport == "cricket":
        key = "cricket-t20" if "T20" in fx["comp"] else "cricket"
    else:
        key = sport
    if key in TOTAL:
        base, scale, _ = TOTAL[key]
        return base + scale * (wa - wb)
    return None


def search_line(mu: float, sigma: float, target: float, lo: float, hi: float) -> float:
    """Half-point line whose cover probability is closest to target."""
    best, best_err = None, 1e9
    step = 0.5
    v = lo
    while v <= hi + 1e-9:
        p = 1.0 - norm_cdf((v - mu) / sigma)
        err = abs(p - target)
        if err < best_err:
            best, best_err = v, err
        v += step
    return best if best is not None else round(mu * 2) / 2


def market(key: str, label: str, outcomes: list[tuple[str, float]], note: str = "") -> dict:
    out = []
    for sel, p in outcomes:
        p = max(1e-6, min(1 - 1e-6, p))
        out.append({"selection": sel, "probability": round(p, 6),
                    "fair_decimal": round(1.0 / p, 4),
                    "fair_american": fmt_american(1.0 / p),
                    "in_band": in_band(p)})
    return {"key": key, "label": label, "note": note, "outcomes": out}


def priced_book(fx: dict, at_note: str = "") -> dict:
    """Originated price book for one fixture (winner / spread / total + sport-specific)."""
    if fx["inputs"].get("if_necessary") == "Y":
        return {"fixture_id": fx["id"], "markets": [], "rated": "low",
                "winner_p": None, "inputs": fx["inputs"],
                "note": "MLB official ifNecessary=Y: game only occurs if tied 2-2; all markets withheld"}
    pw, rated = winner_probability(fx)
    sport = fx["sport"]
    a_name, b_name = fx["a"], fx["b"]
    markets = []
    if pw is not None:
        markets.append(market("winner", "Match Winner",
                              [(f"{a_name}", pw), (f"{b_name}", 1 - pw)],
                              "fair zero-vig price from official records"))
    wa = wb = None
    if rated == "team":
        # recompute win% for margin/total (mlb/nhl/nba kinds handled inside)
        inp = fx["inputs"]
        if inp["kind"] == "mlb":
            wa = inp["a"]["w"] / (inp["a"]["w"] + inp["a"]["l"])
            wb = inp["b"]["w"] / (inp["b"]["w"] + inp["b"]["l"])
        elif inp["kind"] == "nhl":
            wa = inp["a"]["ppg"] / 2.0 / inp["a"]["gp"]
            wb = inp["b"]["ppg"] / 2.0 / inp["b"]["gp"]
        elif inp["kind"] == "nba":
            wa = (inp["a"]["w"] + 5.0) / (inp["a"]["w"] + inp["a"]["l"] + 10.0)
            wb = (inp["b"]["w"] + 5.0) / (inp["b"]["w"] + inp["b"]["l"] + 10.0)
        elif inp["kind"] == "pool":
            wa, wb = inp["a"].get("p", 0.5), inp["b"].get("p", 0.5)
        elif inp["kind"] == "rating":
            wa, wb = inp["a"]["rating"], inp["b"]["rating"]
        elif inp["kind"] == "form" and "form_p" in inp:
            wa, wb = inp["form_p"], 1 - inp["form_p"]
        else:
            wa, wb = win_pct(inp["a"]), win_pct(inp["b"])
        if wa is None or wb is None:
            wa, wb = 0.5, 0.5
        wa = max(0.25, min(0.75, wa + inp["a"].get("adj", 0.0)))
        wb = max(0.25, min(0.75, wb))
        mu_m = margin_mu(fx, wa, wb)
        mu_t = total_mu(fx, wa, wb)
        unit = SPORT_UNIT.get(sport, "points")
        mg_key = "urc" if sport == "rugby-union" else sport
        if mu_m is not None:
            sigma_m = MARGIN[mg_key][1]
            # desk line: favourite's expected margin minus 0.41 sigma -> cover 0.66
            fav = a_name if pw >= 0.5 else b_name
            dog = b_name if pw >= 0.5 else a_name
            mu_fav = abs(mu_m)
            line = max(0.5, search_line(mu_fav, sigma_m, LINE_TARGET, 0.0, 30.0))
            p_cov = 1.0 - norm_cdf((line - mu_fav) / sigma_m)
            markets.append(market("handicap", f"Handicap / Spread ({unit})",
                                  [(f"{fav} -{line:.1f}", p_cov), (f"{dog} +{line:.1f}", 1 - p_cov)],
                                  f"desk line {fav} -{line:.1f} {unit}; cover from margin distribution"))
        if mu_t is not None:
            sigma_t = TOTAL[mg_key][2]
            line = search_line(mu_t, sigma_t, LINE_TARGET, -50.0, 400.0)
            p_over = 1.0 - norm_cdf((line - mu_t) / sigma_t)
            markets.append(market("total", f"Match Total ({unit})",
                                  [(f"Over {line:.1f}", p_over), (f"Under {line:.1f}", 1 - p_over)],
                                  f"desk line {line:.1f} {unit}; over probability from total distribution"))
    # ---- sport-specific markets
    inp = fx["inputs"]
    if sport == "baseball" and rated == "team":
        # fixed +/-1.5 run line
        mu_m = margin_mu(fx, wa, wb)
        sigma_m = MARGIN["baseball"][1]
        p_home = 1.0 - norm_cdf((1.5 - mu_m) / sigma_m)   # home -1.5 covers
        p_away = norm_cdf((1.5 - mu_m) / sigma_m)          # away +1.5 covers
        markets.append(market("run_line", "Run Line (+/-1.5 runs)",
                              [(f"{a_name} -1.5", p_home), (f"{b_name} +1.5", p_away)],
                              "standard 1.5-run line; cover from margin distribution"))
    if sport == "ice-hockey" and rated == "team":
        mu_m = margin_mu(fx, wa, wb)
        sigma_m = MARGIN["ice-hockey"][1]
        p_home = 1.0 - norm_cdf((1.5 - mu_m) / sigma_m)
        p_away = norm_cdf((1.5 - mu_m) / sigma_m)
        markets.append(market("puck_line", "Puck Line (+/-1.5 goals)",
                              [(f"{a_name} -1.5", p_home), (f"{b_name} +1.5", p_away)],
                              "standard 1.5-goal line; cover from margin distribution"))
    if sport == "volleyball" and rated == "team":
        # set score market from per-set probability
        q = 0.5 + 0.18 * (wa - wb)
        q = max(0.3, min(0.7, q))
        a3 = q ** 3
        b3 = (1 - q) ** 3
        a21 = 3 * q ** 3 * (1 - q)
        b21 = 3 * (1 - q) ** 3 * q
        markets.append(market("set_score", "Set Score (best of 5)",
                              [(f"{a_name} 3-0", a3), (f"{a_name} 3-1", a21),
                               (f"{b_name} 3-1", b21), (f"{b_name} 3-0", b3)],
                              "per-set probability from win% delta"))
    if sport == "darts" and inp["kind"] == "merit":
        q = player_unit_q(inp["a"], inp["b"], "merit")
        n = 10  # Round 2 = best of 19
        p_a = first_to_n(q, n)
        fav = a_name if p_a >= 0.5 else b_name
        dog = b_name if p_a >= 0.5 else a_name
        q_f = q if p_a >= 0.5 else 1 - q
        # exact legs-margin distribution for a first-to-10 contest
        margin = {}
        for k in range(0, 10):
            margin[10 - k] = margin.get(10 - k, 0.0) + math.comb(9 + k, k) * q_f ** 10 * (1 - q_f) ** k
            margin[-(10 - k)] = margin.get(-(10 - k), 0.0) + math.comb(9 + k, k) * (1 - q_f) ** 10 * q_f ** k
        mu_legs = sum(k * p for k, p in margin.items())
        var = sum((k - mu_legs) ** 2 * p for k, p in margin.items())
        sigma_legs = math.sqrt(var) if var else 2.0
        # desk handicap line: discrete half-leg search for exact cover 0.66
        line, p_cov = exact_line(margin, 0.0, 12.0)
        markets.append(market("handicap", "Handicap (legs)",
                              [(f"{fav} -{line:.1f}", p_cov), (f"{dog} +{line:.1f}", 1 - p_cov)],
                              "desk line; cover from exact legs-margin distribution"))
        # total legs: exact distribution (total = 10 + k where k = legs lost by winner)
        tot = {}
        for k in range(0, 10):
            tot[10 + k] = math.comb(9 + k, k) * (q_f ** 10 * (1 - q_f) ** k + (1 - q_f) ** 10 * q_f ** k)
        line_t = None
        best_err = 1e9
        for v in [x + 0.5 for x in range(10, 19)]:
            p_over = sum(p for k, p in tot.items() if k >= v)
            err = abs(p_over - LINE_TARGET)
            if err < best_err:
                best_err, line_t = err, v
        p_over = sum(p for k, p in tot.items() if k >= line_t)
        markets.append(market("total", "Total Legs",
                              [(f"Over {line_t:.1f}", p_over), (f"Under {line_t:.1f}", 1 - p_over)],
                              "desk line; over from exact legs distribution"))
    if sport == "snooker" and inp["kind"] == "prize":
        q = player_unit_q(inp["a"], inp["b"], "prize")
        p_a = first_to_n(q, 6)  # SF = best of 11
        fav = a_name if p_a >= 0.5 else b_name
        dog = b_name if p_a >= 0.5 else a_name
        q_f = q if p_a >= 0.5 else 1 - q
        margin = {}
        for k in range(0, 6):
            margin[6 - k] = math.comb(5 + k, k) * q_f ** 6 * (1 - q_f) ** k
            margin[-(6 - k)] = math.comb(5 + k, k) * (1 - q_f) ** 6 * q_f ** k
        mu_fr = sum(k * p for k, p in margin.items())
        var = sum((k - mu_fr) ** 2 * p for k, p in margin.items())
        sigma_fr = math.sqrt(var) if var else 1.5
        line, p_cov = exact_line(margin, 0.0, 8.0)
        markets.append(market("handicap", "Handicap (frames)",
                              [(f"{fav} -{line:.1f}", p_cov), (f"{dog} +{line:.1f}", 1 - p_cov)],
                              "desk line; cover from exact frame-margin distribution"))
        tot = {}
        for k in range(0, 6):
            tot[6 + k] = math.comb(5 + k, k) * (q_f ** 6 * (1 - q_f) ** k + (1 - q_f) ** 6 * q_f ** k)
        line_t = None
        best_err = 1e9
        for v in [x + 0.5 for x in range(6, 12)]:
            p_over = sum(p for k, p in tot.items() if k >= v)
            err = abs(p_over - LINE_TARGET)
            if err < best_err:
                best_err, line_t = err, v
        p_over = sum(p for k, p in tot.items() if k >= line_t)
        markets.append(market("total", "Total Frames",
                              [(f"Over {line_t:.1f}", p_over), (f"Under {line_t:.1f}", 1 - p_over)],
                              "desk line; over from exact frame distribution"))
    if sport == "tennis" and inp["kind"] in ("rank", "seed"):
        q = player_unit_q(inp["a"], inp["b"], inp["kind"])
        p_a = first_to_n(q, 2)
        # set betting (best of 3)
        a20 = q * q
        b20 = (1 - q) * (1 - q)
        a21 = 2 * q * q * (1 - q)
        b21 = 2 * (1 - q) * (1 - q) * q
        markets.append(market("set_betting", "Set Betting (best of 3)",
                              [(f"{a_name} 2-0", a20), (f"{a_name} 2-1", a21),
                               (f"{b_name} 2-1", b21), (f"{b_name} 2-0", b20)],
                              "per-set probability from rank/seed"))
        # total games: mu = 20 + 10*(2q-1), sigma 3
        mu_g = 20.0 + 10.0 * (2 * q - 1)
        line_t = search_line(mu_g, 3.0, LINE_TARGET, 14.0, 26.0)
        p_over = 1.0 - norm_cdf((line_t - mu_g) / 3.0)
        markets.append(market("total", "Total Games",
                              [(f"Over {line_t:.1f}", p_over), (f"Under {line_t:.1f}", 1 - p_over)],
                              "desk line; over from games distribution"))
        # 1st set winner
        markets.append(market("first_set", "1st Set Winner",
                              [(f"{a_name} 1st set", q), (f"{b_name} 1st set", 1 - q)],
                              "per-set probability"))
    if sport == "golf" and inp["kind"] == "outright":
        # H2H outright: P(a finishes higher) via strength share
        sa = (100.0 / max(inp["a"].get("owgr", 150), 1)) ** 0.5
        sb = (100.0 / max(inp["b"].get("owgr", 150), 1)) ** 0.5
        # form adjustment from R2 position
        fa = inp["a"].get("r2", 0)
        fb = inp["b"].get("r2", 0)
        sa *= 1.0 + 0.02 * (fa - fb)
        sb *= 1.0 + 0.02 * (fb - fa)
        p_a = sa / (sa + sb)
        markets.append(market("winner", "Outright H2H (higher finish)",
                              [(f"{a_name}", p_a), (f"{b_name}", 1 - p_a)],
                              "strength share from OWGR + R2 form"))
        for nm, pp in ((a_name, p_a), (b_name, 1 - p_a)):
            pt = 0.10 + 0.25 * pp
            markets.append(market(f"top10_{nm}", f"{nm} Top 10 Finish",
                                  [(f"{nm} Top 10", pt), (f"{nm} outside Top 10", 1 - pt)],
                                  "derived top-10 market from strength share"))
    if sport == "motor-racing" and inp["kind"] in ("f1", "outright"):
        st = inp.get("standings", {})
        total = sum(st.values())
        lead = st.get("Antonelli", total) if st else total
        # race winner market for MR01: proportional to championship points
        if fx["id"] == "MR01":
            probs = []
            for drv, pts in sorted(st.items(), key=lambda kv: -kv[1]):
                probs.append((f"{drv} to win race", pts / total))
            markets.append(market("winner", "Race Winner", probs,
                                  "share of championship points over the field"))
            # podium: 3 x share x 0.75 (field concentration), capped
            p3 = []
            for drv, pts in sorted(st.items(), key=lambda kv: -kv[1]):
                p3.append((f"{drv} Podium", min(0.70, 3 * pts / total * 0.75)))
            markets.append(market("podium", "Podium Finish", p3,
                                  "top-3 probability from points share"))
        if fx["id"] == "MR03":
            probs = []
            for drv, pts in sorted(st.items(), key=lambda kv: -kv[1]):
                probs.append((f"{drv} Top 6", 0.75 * (pts / lead) ** 0.35))
            markets.append(market("top6", "Top 6 Finish", probs,
                                  "top-6 probability from points share (field concentration)"))
        if fx["id"] == "MR02":
            markets.append(market("pole", "Fastest Qualifier (Pole)",
                                  [("Leclerc Pole", 0.28), ("Verstappen Pole", 0.22),
                                   ("Norris Pole", 0.16), ("Russell Pole", 0.14),
                                   ("Antonelli Pole", 0.12), ("Field Pole", 0.08)],
                                  "FP1 order of play (Leclerc fastest in FP1)"))
        if fx["id"] == "MR05":
            share = st["Antonelli"] / total
            markets.append(market("outright", "Drivers' Championship",
                                  [("Antonelli Champion", min(0.75, 0.45 + 0.5 * share)),
                                   ("Field Champion", 1 - min(0.75, 0.45 + 0.5 * share))],
                                  "championship share; Antonelli can clinch in Austin with a win"))
    return {"fixture_id": fx["id"], "markets": markets, "rated": rated,
            "winner_p": pw, "inputs": inp}


def exact_line(margin: dict, lo: float, hi: float) -> tuple[float, float]:
    """Half-step line whose exact cover probability is closest to 0.66."""
    best_v, best_p, best_err = 0.5, 0.5, 1e9
    v = lo
    while v <= hi + 1e-9:
        p = sum(pr for k, pr in margin.items() if k > v)
        err = abs(p - LINE_TARGET)
        if err < best_err:
            best_v, best_p, best_err = v, p, err
        v += 0.5
    return best_v, best_p


def featured_pick(book: dict) -> dict:
    """The desk's pick.

    Rule: if the match winner sits in the High window (in band and >= 0.62),
    feature it; otherwise feature the highest-probability in-band selection
    across all originated markets (handicap / total / sport-specific).
    """
    rated_ok = book["rated"] in ("team", "player", "f1")
    def cand(m: dict, o: dict) -> dict:
        conf = confidence_for(o["probability"], rated_ok)
        return {"market": m["label"], "key": m["key"], "selection": o["selection"],
                "probability": o["probability"], "fair_decimal": o["fair_decimal"],
                "fair_american": o["fair_american"], "confidence": conf,
                "in_band": o["in_band"]}
    best = None
    for m in book["markets"]:
        if m["key"] != "winner":
            continue
        for o in m["outcomes"]:
            if o["in_band"] and o["probability"] >= HIGH_B_FLOOR:
                return cand(m, o)
    for m in book["markets"]:
        for o in m["outcomes"]:
            c = cand(m, o)
            if not c["in_band"] and c["confidence"] != "high":
                continue
            if best is None or c["probability"] > best["probability"]:
                best = c
    return best


def rank_of(conf: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}[conf]
