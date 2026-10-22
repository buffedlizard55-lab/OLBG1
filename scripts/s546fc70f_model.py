"""T546F model: originates match-winner, handicap and total lines from OFFICIAL inputs only.

Inputs (read by hand from official pages on 2026-10-22, see data/546fc70f/*.csv and the source URLs
recorded in each CSV's columns / in the desk sources list):
  * EuroLeague E2026 results + schedule     -> https://api-live.euroleague.net/v1/results?seasonCode=E2026
                                               https://api-live.euroleague.net/v1/schedules?seasonCode=E2026&limit=5
  * NHL standings snapshot 2026-10-22       -> https://api-web.nhle.com/v1/standings/now
  * NHL game list (4 games confirmed)       -> https://api-web.nhle.com/v1/schedule/2026-10-22 ,
                                               https://api-web.nhle.com/v1/score/2026-10-22

Model constants are ASSUMPTIONS, not sourced facts, and are printed in the output:
  EL_SHRINK_K = 6 pseudo-games at league average (EuroLeague)
  NHL_SHRINK_K = 5 pseudo-games at league average (NHL)
  Sigma for EuroLeague margin and total = sample SD of the 66 played games (data-derived).
  No home-court / home-ice term is applied (no official, sourced home-effect value used).
  NHL tied regulation games are split by the Poisson strength ratio (an assumption).
Nothing in this script is a bookmaker price. Fair prices are our own estimates.
"""
import csv, json, math, os, statistics
from math import erf, sqrt, exp, factorial

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "546fc70f")
EL_SHRINK_K = 6
NHL_SHRINK_K = 5
WINDOW_MIN_AMERICAN = -250   # brief: "between -250 and +10000"
WINDOW_MAX_AMERICAN = 10000
P_HIGH = 0.70                 # brief: "greater than 70% chance to win"


def Phi(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


def american(p):
    p = min(max(p, 1e-9), 1 - 1e-9)
    if p >= 0.5:
        return round(-100 * p / (1 - p))
    return round(100 * (1 - p) / p)


def decimal(p):
    return round(1 / p, 4)


def in_window(price):
    return WINDOW_MIN_AMERICAN <= price <= WINDOW_MAX_AMERICAN


def tier(p, price=None):
    """Confidence tier for a MATCH-WINNER pick only.
    High   : p > 0.70 AND American price inside -250..+10000 (strict reading of the brief).
    Medium : 0.60 < p <= 0.70, OR p > 0.70 but priced beyond -250 (flagged as outside window).
    Low    : p <= 0.60.
    """
    if price is None:
        price = american(p)
    if p > P_HIGH and in_window(price):
        return "High"
    if p > 0.60:
        return "Medium"
    return "Low"


def tier_note(p, price):
    if p > P_HIGH and not in_window(price):
        return "p>70% but price beyond -250 window: downgraded to Medium"
    return ""


# ---------------- EuroLeague ----------------
def load_el():
    rows = list(csv.DictReader(open(os.path.join(DATA, "euroleague_e2026_results.csv"), encoding="utf-8")))
    games = [dict(g, home_pts=int(g["home_pts"]), away_pts=int(g["away_pts"])) for g in rows]
    stats = {}
    def add(t, pf, pa):
        s = stats.setdefault(t, {"gp": 0, "pf": 0, "pa": 0, "w": 0, "l": 0})
        s["gp"] += 1; s["pf"] += pf; s["pa"] += pa
        if pf > pa: s["w"] += 1
        else: s["l"] += 1
    for g in games:
        add(g["home"], g["home_pts"], g["away_pts"])
        add(g["away"], g["away_pts"], g["home_pts"])
    margins = [g["home_pts"] - g["away_pts"] for g in games]
    totals = [g["home_pts"] + g["away_pts"] for g in games]
    sd_m = statistics.stdev(margins)
    sd_t = statistics.stdev(totals)
    L = sum(s["pf"] for s in stats.values()) / sum(s["gp"] for s in stats.values())
    for t, s in stats.items():
        K = EL_SHRINK_K
        s["O"] = (s["pf"] + K * L) / (s["gp"] + K)
        s["D"] = (s["pa"] + K * L) / (s["gp"] + K)
        s["M"] = s["O"] - s["D"]
    return stats, L, sd_m, sd_t, len(games)


def lean(p):
    return {"tier": "n/a (not a winner pick)", "in_window_strict": False, "in_window_reading_B": False}


def el_markets(stats, L, sd_m, sd_t, fixtures):
    out = []
    for f in fixtures:
        A, B = f["home"], f["away"]  # home listed first as published by the official schedule
        a, b = stats[A], stats[B]
        E_m = a["M"] - b["M"]               # expected margin for listed home side (no home term)
        p_home = Phi(E_m / sd_m)
        E_A = a["O"] + b["D"] - L
        E_B = b["O"] + a["D"] - L
        E_t = E_A + E_B
        m = {"sport": "EuroLeague basketball", "game_no": f["game_no"], "round": f["round"],
             "date_as_published": f["date_as_published"], "time_as_published": f.get("time_as_published", ""),
             "home": A, "away": B, "fixture_source": "https://api-live.euroleague.net/v1/schedules?seasonCode=E2026&limit=5",
             "home_record": f"{a['w']}-{a['l']}", "away_record": f"{b['w']}-{b['l']}",
             "home_pts_pg": round(a["pf"] / a["gp"], 2), "home_pa_pg": round(a["pa"] / a["gp"], 2),
             "away_pts_pg": round(b["pf"] / b["gp"], 2), "away_pa_pg": round(b["pa"] / b["gp"], 2),
             "expected_margin_home": round(E_m, 2), "expected_total": round(E_t, 2),
             "markets": []}
        # match winner (moneyline, no draw in basketball)
        for side, p in ((A, p_home), (B, 1 - p_home)):
            am = american(p)
            m["markets"].append({"market": "Match winner", "selection": side, "p": round(p, 4),
                                 "american": am, "decimal": decimal(p), "tier": tier(p, am),
                                 "tier_note": tier_note(p, am),
                                 "in_window_strict": p > P_HIGH and in_window(am),
                                 "in_window_reading_B": p > P_HIGH})
        # handicap ladder (listed home side)
        for h in (-5.5, -3.5, -1.5, 1.5, 3.5, 5.5):
            pc = 1 - Phi((-h - E_m) / sd_m)    # P(home margin + h > 0)
            m["markets"].append({"market": f"Handicap {A} {h:+.1f}", "selection": f"{A} {h:+.1f}", "p": round(pc, 4),
                                 "american": american(pc), "decimal": decimal(pc), **lean(pc)})
        # total ladder
        base = math.floor(E_t) + 0.5
        for line in (base - 10, base - 5, base - 2.5, base + 2.5, base + 5, base + 10):
            if line <= 0:
                continue
            po = 1 - Phi((line - E_t) / sd_t)
            for side, p in (("Over", po), ("Under", 1 - po)):
                m["markets"].append({"market": f"Total points {line}", "selection": f"{side} {line}", "p": round(p, 4),
                                     "american": american(p), "decimal": decimal(p), **lean(p)})
        out.append(m)
    return out


# ---------------- NHL ----------------
def load_nhl():
    rows = {r["abbrev"]: r for r in csv.DictReader(open(os.path.join(DATA, "nhl_standings_2026-10-22.csv"), encoding="utf-8"))}
    gf = sum(int(r["gf"]) for r in rows.values()); gp = sum(int(r["gp"]) for r in rows.values())
    g0 = gf / gp
    team = {}
    for k, r in rows.items():
        n = int(r["gp"]); K = NHL_SHRINK_K
        team[k] = {"gp": n, "w": int(r["w"]), "l": int(r["l"]), "otl": int(r["otl"]), "gf": int(r["gf"]), "ga": int(r["ga"]),
                   "att": (int(r["gf"]) + K * g0) / (n + K) / g0, "def": (int(r["ga"]) + K * g0) / (n + K) / g0}
    return team, g0


def pois(lam, kmax=14):
    return [exp(-lam) * lam ** k / factorial(k) for k in range(kmax + 1)]


def nhl_markets(team, g0, fixtures):
    out = []
    for f in fixtures:
        A, B = f["home_abbrev"], f["away_abbrev"]   # NHL: home team is the second listed (@)
        # Sign convention below: "A" = home team in the market rows.
        ta, tb = team[A], team[B]
        lamA = ta["att"] * tb["def"] * g0 / g0 * g0 / g0 * g0  # = att*def*g0 (rates scaled back to goals)
        lamA = ta["att"] * tb["def"] * g0
        lamB = tb["att"] * ta["def"] * g0
        pa, pb = pois(lamA), pois(lamB)
        p_win_reg = sum(pa[i] * pb[j] for i in range(len(pa)) for j in range(len(pb)) if i > j)
        p_tie = sum(pa[i] * pb[i] for i in range(len(pa)))
        p_ot_home = lamA / (lamA + lamB)
        p_home_ml = p_win_reg + p_tie * p_ot_home
        m = {"sport": "NHL ice hockey", "game_no": f["game_id"], "round": "", "date_as_published": "2026-10-22",
             "time_as_published": f["date_utc_start"], "home": A, "away": B,
             "fixture_source": f["official_source"],
             "home_record": f"{ta['w']}-{ta['l']}-{ta['otl']}", "away_record": f"{tb['w']}-{tb['l']}-{tb['otl']}",
             "home_pts_pg": round(lamA, 2), "home_pa_pg": "", "away_pts_pg": round(lamB, 2), "away_pa_pg": "",
             "expected_margin_home": round(lamA - lamB, 2), "expected_total": round(lamA + lamB, 2), "markets": []}
        # reg-margin distribution for puck line
        def p_margin_ge(k):
            return sum(pa[i] * pb[j] for i in range(len(pa)) for j in range(len(pb)) if i - j >= k)
        p_h_minus15 = p_margin_ge(2)                       # home wins by 2+ in regulation
        p_h_plus15 = 1 - sum(pa[i] * pb[j] for i in range(len(pa)) for j in range(len(pb)) if j - i >= 2)
        sel = [(A, p_home_ml), (B, 1 - p_home_ml)]
        for side, p in sel:
            am = american(p)
            m["markets"].append({"market": "Match winner (incl. OT)", "selection": side, "p": round(p, 4),
                                 "american": am, "decimal": decimal(p), "tier": tier(p, am),
                                 "tier_note": tier_note(p, am),
                                 "in_window_strict": p > P_HIGH and in_window(am),
                                 "in_window_reading_B": p > P_HIGH})
        for side, p in ((f"{A} -1.5", p_h_minus15), (f"{B} +1.5", p_h_plus15), (f"{B} -1.5", 1 - p_h_plus15), (f"{A} +1.5", 1 - p_h_minus15)):
            m["markets"].append({"market": "Puck line 1.5", "selection": side, "p": round(p, 4),
                                 "american": american(p), "decimal": decimal(p), **lean(p)})
        lam = lamA + lamB
        tp = pois(lam, 25)
        for line in (5.5, 6.5):
            po = sum(tp[k] for k in range(len(tp)) if k > line)
            for side, p in (("Over", po), ("Under", 1 - po)):
                m["markets"].append({"market": f"Total goals {line}", "selection": f"{side} {line}", "p": round(p, 4),
                                     "american": american(p), "decimal": decimal(p), **lean(p)})
        out.append(m)
    return out


def backtest_el():
    """Walk-forward check of the EuroLeague winner model on the 66 played games.
    For each game in rounds 3+, the team ratings use ONLY games from earlier rounds.
    Reports log loss, Brier score, accuracy and a calibration table versus a naive 50% baseline."""
    rows = list(csv.DictReader(open(os.path.join(DATA, "euroleague_e2026_results.csv"), encoding="utf-8")))
    games = [dict(g, home_pts=int(g["home_pts"]), away_pts=int(g["away_pts"]), round=int(g["round"]), game_no=int(g["game_no"])) for g in rows]
    preds = []
    for g in games:
        if g["round"] < 3:
            continue
        prior = [x for x in games if x["round"] < g["round"]]
        st = {}
        for x in prior:
            for t, pf, pa in ((x["home"], x["home_pts"], x["away_pts"]), (x["away"], x["away_pts"], x["home_pts"])):
                d = st.setdefault(t, {"gp": 0, "pf": 0, "pa": 0})
                d["gp"] += 1; d["pf"] += pf; d["pa"] += pa
        if g["home"] not in st or g["away"] not in st:
            continue
        Lp = sum(d["pf"] for d in st.values()) / sum(d["gp"] for d in st.values())
        def M(t):
            d = st[t]; return (d["pf"] - d["pa"]) / (d["gp"] + EL_SHRINK_K)
        E = M(g["home"]) - M(g["away"])
        sd = statistics.stdev([x["home_pts"] - x["away_pts"] for x in prior])
        ph = Phi(E / sd)
        y = 1 if g["home_pts"] > g["away_pts"] else 0
        preds.append((ph, y, g["round"], g["game_no"]))
    n = len(preds)
    ll = -sum(y * math.log(min(max(p, 1e-9), 1 - 1e-9)) + (1 - y) * math.log(min(max(1 - p, 1e-9), 1 - 1e-9)) for p, y, _, _ in preds) / n
    brier = sum((p - y) ** 2 for p, y, _, _ in preds) / n
    base_ll = -(sum(y for _, y, _, _ in preds) / n * math.log(0.5) + (1 - sum(y for _, y, _, _ in preds) / n) * math.log(0.5))
    acc = sum(1 for p, y, _, _ in preds if (p >= 0.5) == (y == 1)) / n
    buckets = {}
    for p, y, _, _ in preds:
        # bucket by the favourite's probability
        fav = max(p, 1 - p)
        fav_won = (p >= 0.5) == (y == 1)
        b = "50-60%" if fav < 0.6 else ("60-70%" if fav < 0.7 else ">=70%")
        bb = buckets.setdefault(b, {"n": 0, "fav_wins": 0, "mean_fav_p": 0.0})
        bb["n"] += 1; bb["fav_wins"] += int(fav_won); bb["mean_fav_p"] += fav
    for b in buckets.values():
        b["mean_fav_p"] = round(b["mean_fav_p"] / b["n"], 4); b["observed_fav_win_rate"] = round(b["fav_wins"] / b["n"], 4)
        del b["fav_wins"]
    return {"n_predictions": n, "log_loss_model": round(ll, 4), "log_loss_coin_flip_baseline": round(base_ll, 4),
            "brier_model": round(brier, 4), "accuracy_model": round(acc, 4), "calibration_by_favourite_band": buckets,
            "note": "Walk-forward on played games only (rounds 3-7). Small sample; no home term; model has no injury, rest or roster data."}


def main():
    stats, L, sd_m, sd_t, n_games = load_el()
    el_fix = [r for r in csv.DictReader(open(os.path.join(DATA, "euroleague_e2026_upcoming.csv"), encoding="utf-8"))]
    el_fix = [dict(r, home=r["home"], away=r["away"]) for r in el_fix if r["played_flag_official"] == "false"]
    # sanity: every fixture team must have played games in the official results
    for f in el_fix:
        assert f["home"] in stats and f["away"] in stats, (f["home"], f["away"])
    el = el_markets(stats, L, sd_m, sd_t, el_fix)

    team, g0 = load_nhl()
    nhl_fix = list(csv.DictReader(open(os.path.join(DATA, "nhl_fixtures_official_2026-10-22.csv"), encoding="utf-8")))
    nhl = nhl_markets(team, g0, nhl_fix)

    bt = backtest_el()
    out = {"generated_utc": "2026-10-22", "backtest_euroleague": bt, "assumptions": {
              "EL_SHRINK_K": EL_SHRINK_K, "NHL_SHRINK_K": NHL_SHRINK_K,
              "EL_sigma_margin_sample_sd": round(sd_m, 3), "EL_sigma_total_sample_sd": round(sd_t, 3),
              "EL_league_pts_per_team_per_game": round(L, 3), "EL_games_used": n_games,
              "NHL_league_goals_per_team_per_game": round(g0, 3),
              "home_advantage_term": "none (no official value sourced)",
              "high_rule": "p > 0.70 AND American price within -250..+10000 (strict reading) AND official evidence; reading B (p>0.70 only) also recorded"},
           "fixtures": el + nhl}
    json.dump(out, open(os.path.join(DATA, "model_output.json"), "w"), indent=2)
    # flat CSV
    with open(os.path.join(DATA, "lines_all_markets.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sport", "game", "date_as_published", "time_as_published", "home", "away", "market", "selection",
                    "p_model", "american_fair", "decimal_fair", "tier", "in_window_strict", "in_window_reading_B", "fixture_source"])
        for m in out["fixtures"]:
            for k in m["markets"]:
                w.writerow([m["sport"], m["game_no"], m["date_as_published"], m["time_as_published"], m["home"], m["away"],
                            k["market"], k["selection"], k["p"], k["american"], k["decimal"], k["tier"],
                            k["in_window_strict"], k["in_window_reading_B"], m["fixture_source"]])
    # summary
    for m in out["fixtures"]:
        best = max(m["markets"], key=lambda k: k["p"])
        print(m["sport"][:10], m["home"], "v", m["away"], "| E_margin_home", m["expected_margin_home"], "E_total", m["expected_total"],
              "| top:", best["selection"], best["market"], best["p"], best["american"], best["tier"], "strict" if best["in_window_strict"] else "")
    print("backtest", json.dumps(bt))
    print("assumptions", json.dumps(out["assumptions"]))


if __name__ == "__main__":
    main()
