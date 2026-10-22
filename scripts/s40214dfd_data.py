"""Assemble the 40214dfd desk data from the official-source harvest files.

Writes data/40214dfd/desk.json plus two CSV exports. Every priced row traces to a harvest field
and therefore to an official URL. Anything that could not be confirmed stays null and is listed
in desk['flagged'] or desk['gaps'].
"""
import csv
import json
import re
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s40214dfd_model as M
from s40214dfd_prose import NEAR_MISS_NOTES, PREDICTIONS

ROOT = Path(__file__).resolve().parent.parent
HARVEST = ROOT / "data" / "40214dfd" / "harvest"
OUT = ROOT / "data" / "40214dfd"
AS_OF = "2026-10-22T12:45:00Z"

SOURCES = [
    {
        "source_id": "nhl-scores-20261022",
        "publisher": "NHL.com (National Hockey League)",
        "official": True,
        "url": "https://www.nhl.com/scores/2026-10-22",
        "supporting": [
            "https://www.nhl.com/standings/2026-10-21/wildcard",
            "https://api-web.nhle.com/v1/schedule/2026-10-22",
            "https://api-web.nhle.com/v1/standings/2026-10-21",
        ],
        "observed_from": "2026-10-22T12:12:00Z",
        "observed_to": "2026-10-22T12:19:00Z",
        "read": "All 12 scheduled games, records as W-L-OTL, the moneyline displayed by NHL.com's odds partner, team scoring leaders, and the 21 October standings table.",
        "not_read": "Starting goaltenders for tonight, injury reports, line combinations, and any sportsbook price fetched directly from a book.",
    },
    {
        "source_id": "mlb-postseason",
        "publisher": "MLB.com (Major League Baseball)",
        "official": True,
        "url": "https://www.mlb.com/postseason",
        "supporting": ["https://www.mlb.com/standings/"],
        "observed_from": "2026-10-22T12:20:00Z",
        "observed_to": "2026-10-22T12:29:00Z",
        "read": "World Series games 1-5 with gamePk, date, first pitch clock and home club; final regular-season W-L, runs scored and runs allowed per club.",
        "not_read": "Probable starting pitchers, bullpen availability, ballpark identity, weather, and postseason roster composition.",
    },
    {
        "source_id": "euroleague-r7",
        "publisher": "EuroLeague Basketball",
        "official": True,
        "url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
        "supporting": [
            "https://www.euroleaguebasketball.net/en/euroleague/game-center/",
            "https://www.euroleaguebasketball.net/en/euroleague/standings/",
        ],
        "observed_from": "2026-10-22T12:24:00Z",
        "observed_to": "2026-10-22T12:31:00Z",
        "read": "Round 7 fixtures for 22-23 October with CEST tip-off clocks, each club's win-loss record, and the scoring / scoring-defence averages quoted in the official preview.",
        "not_read": "Full standings table with points for and against for every club, injury reports beyond the preview text, and any bookmaker price.",
    },
    {
        "source_id": "wst-nio-2026",
        "publisher": "World Snooker Tour",
        "official": True,
        "url": "https://www.wst.tv/",
        "supporting": ["https://www.wst.tv/matches/"],
        "observed_from": "2026-10-22T12:36:00Z",
        "observed_to": "2026-10-22T12:41:00Z",
        "read": "Round 3 pairings at the BetVictor Northern Ireland Open 2026 and the clock values as displayed.",
        "not_read": "Any timezone label (the page prints none), the official ranking table, season match records, or frame-level scoring form.",
    },
    {
        "source_id": "gaa-fixtures",
        "publisher": "GAA.ie (Gaelic Athletic Association)",
        "official": True,
        "url": "https://www.gaa.ie/fixtures-results",
        "supporting": ["https://www.gaa.ie/fixtures-results/tables"],
        "observed_from": "2026-10-22T12:43:00Z",
        "observed_to": "2026-10-22T12:44:00Z",
        "read": "The October fixture list: one entry, the Shinty-Hurling International between Ireland and Scotland on Saturday 24 October.",
        "not_read": "County or club championship fixtures, which are not published on this national page.",
    },
]

# Sports the brief puts in scope, with what this session could and could not verify.
COVERAGE = [
    ("Ice hockey", "priced", "12", "Full 22 October NHL slate: records, goals for/against and team leaders from NHL.com.", "nhl-scores-20261022"),
    ("Baseball", "priced", "5", "World Series games 1-5 from the official bracket, with final regular-season run aggregates.", "mlb-postseason"),
    ("Basketball", "priced", "9", "EuroLeague Round 7 fixtures for 22-23 October with records and preview scoring averages.", "euroleague-r7"),
    ("Snooker", "listed, unpriced", "8", "WST Round 3 pairings retrieved, but the page prints no timezone and no ranking or form table, so no line is originated.", "wst-nio-2026"),
    ("Gaelic football", "no in-scope fixture", "0", "The only fixture on the official GAA page in the window is shinty-hurling, an excluded category.", "gaa-fixtures"),
    ("Tennis", "not verified", "0", "Two official routes tried on 22 October. atptour.com/en/scores/current returns live-score cards only. The daily-schedule route (atptour.com/en/scores/current/stockholm/429/daily-schedule) redirected to the 2025 archive results page - completed 2025 matches - so it is not treated as fixture evidence. No ranking table was reachable, so no tennis line is originated.", None),
    ("Darts", "not verified", "0", "pdc.tv returns a JavaScript-rendered draw, and the 2026 European Championship page (pdc.tv/tournament/2026-european-championship) returned a cookie-consent wall with no fixture, round, pairing or result markup at all. With no darts data in the response, nothing is listed and nothing is priced.", None),
    ("Australian rules", "not verified", "0", "afl.com.au/aflw/fixture and /ladder render their fixture and ladder widgets in JavaScript; the retrieved responses contained no rows, so no AFLW fact is asserted.", None),
    ("Rugby union", "not verified", "0", "unitedrugby.com/fixtures returned a 404 page and no alternative official fixture page was read.", None),
    ("Rugby league", "not verified", "0", "No official fixture page was read in this session.", None),
    ("Cricket", "not verified", "0", "icc-cricket.com/matches returned a 404 page and no alternative official fixture page was read.", None),
    ("Handball", "not verified", "0", "No official EHF fixture page was read in this session.", None),
    ("Volleyball", "not verified", "0", "No official Volleyball World fixture page was read in this session.", None),
    ("Golf", "not verified", "0", "Outright tournament markets are multi-runner; no official field or tee-time page was read.", None),
    ("Motor racing", "not verified", "0", "Multi-runner race markets; no official entry list was read.", None),
    ("eSports", "not verified", "0", "No official tournament fixture page was read in this session.", None),
    ("Greyhounds", "not verified", "0", "Race cards are published close to race time; no official GBGB card was read.", None),
]

EXCLUDED = [
    "Soccer / football", "American football", "Boxing", "UFC / MMA", "Hurling",
    "Horse racing", "Cycling", "Specials",
]


def okey(fixture_id, market_name, selection, line):
    return f"{fixture_id}|{market_name}|{selection}|{line}"


def pred_key(pred):
    return okey(pred["fixture_id"], pred["market"], pred["match"]["selection"], pred["match"]["line"])


CROSS_ROW = re.compile(
    r'<td[^>]*>\s*<strong>([^<]{2,60})</strong>\s*</td>\s*<td[^>]*>\s*(\d{1,3})%\s*</td>\s*'
    r'<td[^>]*>\s*([\d.]+)\s*</td>\s*<td[^>]*>\s*([+-]?\d+)\s*</td>\s*<td[^>]*>.*?badge\s+(\w+)',
    re.S)


def scan_cross_desk():
    """Row-by-row read of the merged 53674ac8 desk: every row labelled High, with its stated probability."""
    base = ROOT / "53674ac8"
    rows = []
    if not base.exists():
        return rows
    for path in sorted(base.rglob("*.html")):
        for sel, pct, dec, am, tier in CROSS_ROW.findall(path.read_text()):
            if tier.lower() != "high":
                continue
            rows.append({"page": path.relative_to(ROOT).as_posix(), "selection": sel,
                         "probability_pct": int(pct), "decimal": dec, "american": int(am)})
    return rows


def load(name):
    return json.loads((HARVEST / name).read_text())


def rec_from_wlo(text):
    w, l, ot = (int(x) for x in text.split("-"))
    return {"wins": w, "losses": l, "otl": ot, "games": w + l + ot,
            "record": text}


def market(kind, label, settlement, selections, extra=None):
    m = {
        "market": kind,
        "label": label,
        "settlement": settlement,
        "status": "originated fair price (experimental); no bookmaker quote captured",
        "outcomes": [dict(selection=s, **M.price_block(p)) for s, p in selections],
    }
    if extra:
        m.update(extra)
    return m


def build_nhl():
    raw = load("nhl_2026-10-22.json")
    table = {r["team"]: r for r in raw["standings_rows_verified"]}
    rows, gaps = [], []
    for g in raw["games"]:
        home, away = g["home"], g["away"]
        H, A = table[home], table[away]
        hr, ar = rec_from_wlo(g["home_record"]), rec_from_wlo(g["away_record"])
        p_home = M.winner_probability(hr, ar)
        markets = [
            market("winner", "Match winner", "Full game including overtime and shootout",
                   [(home, p_home), (away, 1 - p_home)]),
        ]
        goal_inputs = all(H.get(k) for k in ("gf", "ga")) and all(A.get(k) for k in ("gf", "ga"))
        if goal_inputs:
            la, lb = M.rate_pair(H["gf"], H["ga"], H["gp"], A["gf"], A["ga"], A["gp"])
            grid = M.difference_grid(la, lb, 18)
            for line in (0.5, 1.5, 2.5):
                markets.append(market(
                    "handicap", f"Puck line {home} -{line}",
                    "Full game including overtime and shootout; half-point line so no push",
                    [(home, M.prob_margin_at_least(grid, line)),
                     (away, 1 - M.prob_margin_at_least(grid, line))],
                    {"line": -line, "subject": home}))
            for line in (4.5, 5.5, 6.5, 7.5, 8.5):
                over = M.prob_total_over(grid, line)
                markets.append(market(
                    "total", f"Total goals {line}",
                    "Full game goals including overtime and shootout; half-point line so no push",
                    [(f"Over {line}", over), (f"Under {line}", 1 - over)],
                    {"line": line}))
            pa = M.poisson_pmf(la, 18)
            pb = M.poisson_pmf(lb, 18)
            for team, vec in ((home, pa), (away, pb)):
                for line in (2.5, 3.5, 4.5):
                    over = math.fsum(m for s, m in enumerate(vec) if s > line)
                    markets.append(market(
                        "team_total", f"{team} team total {line}",
                        "Goals scored by the named team over the full game including overtime and shootout",
                        [(f"{team} Over {line}", over), (f"{team} Under {line}", 1 - over)],
                        {"line": line, "subject": team}))
        else:
            gaps.append({
                "fixture_id": g["id"],
                "missing": "goals for and goals against",
                "missing_sides": [t for t, r in ((home, H), (away, A)) if not r.get("gf")],
                "effect": "Winner market is originated; puck line, total and team total are withheld.",
                "source_id": "nhl-scores-20261022",
            })
        rows.append({
            "id": g["id"], "sport": "Ice hockey", "sport_key": "ice-hockey",
            "competition": "NHL", "home": home, "away": away,
            "start_utc": g["start_utc"], "start_basis": g["start_time_basis"],
            "venue": g["venue"],
            "home_record": g["home_record"], "away_record": g["away_record"],
            "home_inputs": {"wins": H["w"], "losses": H["l"], "otl": H["otl"], "games": H["gp"],
                            "goals_for": H.get("gf"), "goals_against": H.get("ga"),
                            "last10": H.get("l10"), "streak": H.get("streak")},
            "away_inputs": {"wins": A["w"], "losses": A["l"], "otl": A["otl"], "games": A["gp"],
                            "goals_for": A.get("gf"), "goals_against": A.get("ga"),
                            "last10": A.get("l10"), "streak": A.get("streak")},
            "displayed_market_reference": {
                "home_american": g["displayed_home_ml"], "away_american": g["displayed_away_ml"],
                "note": "Moneyline shown on NHL.com's scores module (its odds partner). Recorded as a market reference, not fetched from a sportsbook.",
            },
            "source_ids": ["nhl-scores-20261022"],
            "source_urls": [raw["url"], "https://www.nhl.com/standings/2026-10-21/wildcard"],
            "model_inputs_complete": True,
            "goal_inputs_complete": bool(goal_inputs),
            "settlement_verified": True,
            "markets": markets,
        })
    return rows, gaps, raw


def build_mlb():
    raw = load("mlb_worldseries.json")
    t = raw["team_rates"]
    rows = []
    for g in raw["games"]:
        home, away = g["home"], g["away"]
        H, A = t[home], t[away]
        p_home = M.winner_probability({"wins": H["wins"], "games": 162},
                                      {"wins": A["wins"], "games": 162})
        la, lb = M.rate_pair(H["runs_scored"], H["runs_allowed"], 162,
                             A["runs_scored"], A["runs_allowed"], 162)
        grid = M.difference_grid(la, lb, 25)
        markets = [market("winner", "Match winner",
                          "Full game including extra innings; nine innings or more",
                          [(home, p_home), (away, 1 - p_home)])]
        for line in (0.5, 1.5, 2.5):
            markets.append(market(
                "handicap", f"Run line {home} -{line}",
                "Full game including extra innings; half-point line so no push",
                [(home, M.prob_margin_at_least(grid, line)),
                 (away, 1 - M.prob_margin_at_least(grid, line))],
                {"line": -line, "subject": home}))
        for line in (6.5, 7.5, 8.5, 9.5, 10.5):
            over = M.prob_total_over(grid, line)
            markets.append(market("total", f"Total runs {line}",
                                  "Combined runs over the full game including extra innings",
                                  [(f"Over {line}", over), (f"Under {line}", 1 - over)],
                                  {"line": line}))
        pa, pb = M.poisson_pmf(la, 25), M.poisson_pmf(lb, 25)
        for team, vec in ((home, pa), (away, pb)):
            for line in (3.5, 4.5, 5.5):
                over = math.fsum(m for s, m in enumerate(vec) if s > line)
                markets.append(market("team_total", f"{team} team total {line}",
                                      "Runs scored by the named team over the full game including extra innings",
                                      [(f"{team} Over {line}", over), (f"{team} Under {line}", 1 - over)],
                                      {"line": line, "subject": team}))
        rows.append({
            "id": g["id"], "sport": "Baseball", "sport_key": "baseball",
            "competition": "MLB World Series", "home": home, "away": away,
            "start_utc": g["start_utc"], "start_basis": g["start_time_basis"],
            "venue": g["venue"], "series_game": g["series_game"], "status": g["status"],
            "home_record": f"{H['wins']}-{H['losses']}", "away_record": f"{A['wins']}-{A['losses']}",
            "home_inputs": {"wins": H["wins"], "losses": H["losses"], "games": 162,
                            "runs_scored": H["runs_scored"], "runs_allowed": H["runs_allowed"],
                            "last10": H["l10"], "streak": H["streak"]},
            "away_inputs": {"wins": A["wins"], "losses": A["losses"], "games": 162,
                            "runs_scored": A["runs_scored"], "runs_allowed": A["runs_allowed"],
                            "last10": A["l10"], "streak": A["streak"]},
            "displayed_market_reference": None,
            "source_ids": ["mlb-postseason"],
            "source_urls": [raw["url"], "https://www.mlb.com/standings/"],
            "model_inputs_complete": True,
            "goal_inputs_complete": True,
            "settlement_verified": True,
            "markets": markets,
        })
    return rows, raw


def build_euroleague():
    raw = load("euroleague_round7.json")
    rows = []
    for g in raw["games"]:
        home, away = g["home"], g["away"]
        hw, hl = (int(x) for x in g["home_record"].split("-"))
        aw, al = (int(x) for x in g["away_record"].split("-"))
        p_home = M.winner_probability({"wins": hw, "games": hw + hl},
                                      {"wins": aw, "games": aw + al})
        mu = M.normal_margin(p_home, 12.0)
        markets = [market("winner", "Match winner",
                          "Full game including overtime; EuroLeague games cannot end level",
                          [(home, p_home), (away, 1 - p_home)])]
        for line in (0.5, 2.5, 4.5, 6.5, 8.5, 10.5, 12.5):
            p = M.prob_margin_at_least_normal(mu, 12.0, line)
            markets.append(market(
                "handicap", f"Handicap {home} -{line}",
                "Full game including overtime; half-point line so no push",
                [(home, p), (away, 1 - p)],
                {"line": -line, "subject": home, "model_parameter": "normal spread sigma=12.0 points (assumed)"}))
        rows.append({
            "id": g["id"], "sport": "Basketball", "sport_key": "basketball",
            "competition": "EuroLeague", "home": home, "away": away,
            "start_utc": g["tip_utc"], "start_basis": "converted_from_declared_CEST_UTC+2",
            "venue": None,
            "home_record": g["home_record"], "away_record": g["away_record"],
            "home_inputs": {"wins": hw, "losses": hl, "games": hw + hl},
            "away_inputs": {"wins": aw, "losses": al, "games": aw + al},
            "displayed_market_reference": None,
            "source_ids": ["euroleague-r7"],
            "source_urls": [raw["url"]],
            "model_inputs_complete": True,
            "settlement_verified": True,
            "uses_assumed_parameter": True,
            "preview_facts": g["facts"],
            "markets": markets,
        })
    return rows, raw


def build_snooker():
    raw = load("snooker_ni_open.json")
    rows = []
    for m in raw["matches"]:
        rows.append({
            "id": m["id"], "sport": "Snooker", "sport_key": "snooker",
            "competition": m["event"], "home": m["player_b"], "away": m["player_a"],
            "start_utc": None, "start_basis": "displayed_clock_without_timezone",
            "venue": None, "round": m["round"], "state": m["state"],
            "home_record": None, "away_record": None,
            "home_inputs": None, "away_inputs": None,
            "displayed_market_reference": None,
            "source_ids": ["wst-nio-2026"], "source_urls": [raw["url"], "https://www.wst.tv/matches/"],
            "model_inputs_complete": False, "goal_inputs_complete": False,
            "settlement_verified": False,
            "markets": [],
            "withheld": "No ranking table, season record or frame-level form was retrieved, and the "
                        "start time carries no timezone. No line is originated and no tier is assigned.",
        })
    return rows, raw


def pick_for(fixture, prediction_keys):
    """The desk's headline selection for a fixture, plus the separate match-winner view.

    Headline order: an in-window selection that carries a written prediction (High) first,
    otherwise the highest-probability winner selection with its own tier.
    """
    winner = fixture["markets"][0]
    top_winner = max(winner["outcomes"], key=lambda o: o["probability"])
    other = [o for o in winner["outcomes"] if o is not top_winner][0]
    w_tier, w_reasons = M.confidence_for(
        top_winner["probability"],
        inputs_complete=fixture["model_inputs_complete"],
        has_prediction=False,
        manufactured_by_assumption=fixture.get("uses_assumed_parameter", False),
        settlement_verified=fixture["settlement_verified"],
    )
    winner_view = {
        "market": "winner",
        "selection": top_winner["selection"],
        "opponent": other["selection"],
        "probability": top_winner["probability"],
        "american": top_winner["american"],
        "confidence": w_tier,
        "reasons": w_reasons,
    }

    headline = None
    for mk in fixture["markets"][1:]:
        for o in mk["outcomes"]:
            if not o["fair_price_in_brief_band"] or o["probability"] <= 0.70:
                continue
            key = okey(fixture["id"], mk["market"], o["selection"], mk.get("line"))
            if key in prediction_keys:
                headline = {
                    "fixture_id": fixture["id"],
                    "market": mk["market"],
                    "market_label": mk["label"],
                    "selection": o["selection"],
                    "line": mk.get("line"),
                    "probability": o["probability"],
                    "american": o["american"],
                    "fair_decimal": o["fair_decimal"],
                    "confidence": "high",
                    "reasons": ["model probability above 70% and fair price inside the brief window; "
                                "both sides' inputs verified; written prediction attached"],
                    "key": key,
                }
    if headline is None:
        headline = {
            "fixture_id": fixture["id"],
            "market": "winner",
            "market_label": "Match winner",
            "selection": top_winner["selection"],
            "line": None,
            "probability": top_winner["probability"],
            "american": top_winner["american"],
            "fair_decimal": top_winner["fair_decimal"],
            "confidence": w_tier,
            "reasons": w_reasons,
            "key": None,
        }
    return {"fixture_id": fixture["id"], "headline": headline, "winner_view": winner_view}


def main():
    nhl, nhl_gaps, nhl_raw = build_nhl()
    mlb, mlb_raw = build_mlb()
    el, el_raw = build_euroleague()
    snk, snk_raw = build_snooker()

    priced = nhl + mlb + el
    prediction_keys = {pred_key(p): p for p in PREDICTIONS}
    used = set()
    for fixture in priced:
        for mk in fixture["markets"]:
            for o in mk["outcomes"]:
                key = okey(fixture["id"], mk["market"], o["selection"], mk.get("line"))
                pred = prediction_keys.get(key)
                if pred:
                    used.add(key)
                    if abs(pred["probability"] - o["probability"]) > 5e-4:
                        raise SystemExit(f"prediction probability mismatch for {key}")
                    if pred["american"] != o["american"]:
                        raise SystemExit(f"prediction price mismatch for {key}: "
                                         f"{pred['american']} vs {o['american']}")
                    tier, reasons = M.confidence_for(
                        o["probability"],
                        inputs_complete=fixture["model_inputs_complete"],
                        has_prediction=True,
                        manufactured_by_assumption=fixture.get("uses_assumed_parameter", False),
                        settlement_verified=fixture["settlement_verified"],
                    )
                    o["confidence"] = tier
                    o["confidence_reasons"] = reasons
                    o["prediction_id"] = key
    for fixture in priced:
        for mk in fixture["markets"]:
            for o in mk["outcomes"]:
                if o.get("confidence"):
                    continue
                key = okey(fixture["id"], mk["market"], o["selection"], mk.get("line"))
                tier, reasons = M.confidence_for(
                    o["probability"],
                    inputs_complete=fixture["model_inputs_complete"],
                    has_prediction=key in prediction_keys,
                    manufactured_by_assumption=bool(mk.get("model_parameter")),
                    settlement_verified=fixture["settlement_verified"],
                )
                o["confidence"] = tier
                o["confidence_reasons"] = reasons

    missing = set(prediction_keys) - used
    if missing:
        raise SystemExit(f"predictions not matched to a market: {sorted(missing)}")

    picks = [pick_for(f, prediction_keys) for f in priced]
    highs = []
    for fixture in priced:
        for mk in fixture["markets"]:
            for o in mk["outcomes"]:
                if o.get("confidence") == "high":
                    highs.append({
                        "fixture_id": fixture["id"], "fixture": f"{fixture['away']} @ {fixture['home']}",
                        "sport": fixture["sport"], "competition": fixture["competition"],
                        "start_utc": fixture["start_utc"],
                        "market": mk["market"], "market_label": mk["label"],
                        "selection": o["selection"], "line": mk.get("line"),
                        "probability": o["probability"], "american": o["american"],
                        "fair_decimal": o["fair_decimal"],
                        "prediction_id": o["prediction_id"],
                        "source_url": fixture["source_urls"][0],
                    })

    near = []
    for fixture in priced:
        win_rows = [o for o in fixture["markets"][0]["outcomes"] if o["probability"] > 0.7143]
        if win_rows:
            o = max(win_rows, key=lambda x: x["probability"])
            near.append({
                "fixture_id": fixture["id"],
                "fixture": f"{fixture['away']} @ {fixture['home']}",
                "market": "winner",
                "selection": o["selection"],
                "line": None,
                "probability": o["probability"],
                "american": o["american"],
                "closest": True,
                "source_url": fixture["source_urls"][0],
            })
            continue
        best = None
        for mk in fixture["markets"][1:]:
            for o in mk["outcomes"]:
                if not (0.7143 < o["probability"] <= 0.78):
                    continue
                if best is None or o["probability"] < best["probability"]:
                    best = {
                        "fixture_id": fixture["id"],
                        "fixture": f"{fixture['away']} @ {fixture['home']}",
                        "market": mk["market"],
                        "selection": o["selection"],
                        "line": mk.get("line"),
                        "probability": o["probability"],
                        "american": o["american"],
                        "closest": False,
                        "source_url": fixture["source_urls"][0],
                    }
        if best:
            near.append(best)
    near.sort(key=lambda r: r["probability"])

    seen = set()
    deduped = []
    for r in sorted(near, key=lambda r: r["probability"]):
        sig = (r["selection"], r["american"], r["market"])
        if sig in seen:
            continue
        seen.add(sig)
        deduped.append(r)
    near = deduped

    markets_count = sum(len(f["markets"]) for f in priced)
    outcomes_count = sum(len(m["outcomes"]) for f in priced for m in f["markets"])

    cross = scan_cross_desk()
    cross_below = [r for r in cross if r["probability_pct"] <= 70]

    flagged = [
        {"id": "F-402-01", "severity": "high",
         "title": "The brief's two High rules only intersect between 70.00% and 71.43%",
         "detail": ("-250 is decimal 1.40, i.e. 71.4286%. A fair price for any probability above that "
                    "is shorter than -250, so no selection with a genuine chance above 71.43% can sit "
                    "inside the brief's window. This desk publishes High only inside the true "
                    "intersection and lists every near miss at -251 or shorter on this page. It does "
                    "not relabel a -311 favourite as a High pick."),
         "source": "arithmetic from the brief, illustrated by the near-miss table below"},
        {"id": "F-402-02", "severity": "medium",
         "title": "High lines are authored alternate lines, not the model's single strongest view",
         "detail": ("Each High selection sits on an alternate total, team total or puck line that the "
                    "desk generated in half-point steps around the model expectation. The probability "
                    "is a model output for that rung; the rung was chosen because it satisfies both "
                    "brief conditions. The moneyline view for the same fixture is published separately "
                    "and keeps its own, usually lower, tier."),
         "source": "methodology and the per-fixture winner picks"},
        {"id": "F-402-03", "severity": "medium",
         "title": "Basketball handicaps rest on an assumed spread, so they cannot be High",
         "detail": ("EuroLeague margins are modelled as Normal with sigma = 12.0 points. That parameter "
                    "is assumed, not measured in this session, so every basketball handicap outcome is "
                    "capped below High even when its probability lands inside the window."),
         "source": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/"},
        {"id": "F-402-04", "severity": "medium",
         "title": "Snooker clocks carry no timezone, so eight matches stay unpriced",
         "detail": ("WST prints match clocks in the viewer's local time without an offset. Two 08:00 "
                    "matches were already marked live. Without a timezone and without an official "
                    "ranking table in this session, no snooker line is originated and no match is "
                    "claimed as a pre-match selection."),
         "source": "https://www.wst.tv/"},
        {"id": "F-402-05", "severity": "low",
         "title": "Two NHL fixtures are missing goal inputs, so only the winner market exists",
         "detail": ("Los Angeles (1-4-2) and Calgary had no goals-for / goals-against row in the retrieved "
                    "standings chunk. Their games are published with a winner market only; puck line, "
                    "total and team total are withheld rather than estimated."),
         "source": "https://www.nhl.com/standings/2026-10-21/wildcard"},
        {"id": "F-402-06", "severity": "low",
         "title": "Baseball lines ignore the postseason context that actually decides the games",
         "detail": ("The run model uses final regular-season team aggregates. Starting pitchers, bullpen "
                    "availability, park and rest are not captured, so all five World Series rows stay "
                    "Low and their totals and run lines are research lines only."),
         "source": "https://www.mlb.com/standings/"},
        {"id": "F-402-08", "severity": "high",
         "title": "Cross-desk: all 12 High labels on the merged 53674ac8 desk sit at or below 70%",
         "detail": (f"The desk merged in PR #111 publishes {len(cross)} rows labelled High. Read row by row "
                    f"from its own HTML, {len(cross_below)} of them state a model probability of 63-70%, "
                    "none above 70%. Under the brief's rule a High pick must be above 70%, so these labels "
                    "overstate confidence even where the price is inside the window. The values are "
                    "reproduced on this page exactly as that desk prints them; this session has not edited "
                    "another session's claims and flags them for its owner or the integrator."),
         "source": "53674ac8/lines.html and 53674ac8/sports/*.html (PR #111)"},
        {"id": "F-402-09", "severity": "medium",
         "title": "Cross-desk: those predictions are template text with the name swapped",
         "detail": ("Two of the 53674ac8 snooker predictions are identical sentences apart from the player "
                    "name and price: both read 'brings professional experience and a strong recent record at "
                    "ranking events ... at the Waterfront Hall in Belfast. Their safety play and "
                    "break-building consistency give them a clear edge ...'. That is the repetitive, robotic "
                    "pattern the brief asks to avoid, and it makes no verifiable claim about either player."),
         "source": "53674ac8/sports/snooker.html"},
        {"id": "F-402-10", "severity": "low", "resolved": True,
         "title": "Resolved by another session: 98 site-absolute links had blocked the canonical gate",
         "detail": ("Every nav and footer link in 53674ac8 was written as href=\"/53674ac8/...\", which the "
                    "legacy structural gate rejects ('link escapes repository root') and which resolves to "
                    "the domain root instead of /OLBG1/ on the project Pages site. This session prepared a "
                    "page-level repair, then found on rebasing that session ee3c3e8f-olbg1 had already fixed "
                    "the same 98 links and their generator (scripts/s53674ac8_build_site.py, BASE = \"./\") in "
                    "commit f132b6e. That fix survives regeneration and is strictly better, so this session "
                    "DROPPED its duplicate page edits (the 13 files are byte-identical to main here, git diff "
                    "HEAD -- 53674ac8 is empty) and credits ee3c3e8f-olbg1 / PR #112 with the repair. Re-verified "
                    "on this branch: zero remaining matches for the absolute form, scripts/validate.py 0 errors."),
         "source": "53674ac8/*.html, scripts/s53674ac8_build_site.py, COORDINATION.md section 51.5"},
        {"id": "F-402-07", "severity": "medium",
         "title": "Eleven in-scope sports have no verified fixture in this session",
         "detail": ("Tennis, darts, Australian rules, both rugby codes, cricket, handball, volleyball, "
                    "golf, motor racing, eSports and greyhounds are listed on the Coverage page with the "
                    "official URL that was attempted and the specific reason no row was published. No "
                    "fixture, price or prediction is invented to fill them."),
         "source": "coverage.html"},
    ]

    desk = {
        "schema": "desk402-v1",
        "session": "40214dfd-olbg1",
        "desk_name": "40214dfd · 22 October in-window desk",
        "as_of": AS_OF,
        "model_version": M.MODEL_VERSION,
        "assumptions": M.ASSUMPTIONS,
        "window": {"from_utc": "2026-10-22T00:00:00Z", "to_utc": "2026-10-29T00:00:00Z",
                   "note": "Fixtures on or after the read time and inside seven days."},
        "sources": SOURCES,
        "coverage": [{"sport": s, "status": st, "rows": int(n), "detail": d,
                      "source_id": sid,
                      "source_url": next((x["url"] for x in SOURCES if x["source_id"] == sid), None)}
                     for s, st, n, d, sid in COVERAGE],
        "excluded": EXCLUDED,
        "fixtures": priced + snk,
        "priced_fixture_count": len(priced),
        "unpriced_fixture_count": len(snk),
        "picks": picks,
        "high_picks": sorted(highs, key=lambda r: r["start_utc"] or ""),
        "near_misses": near,
        "over_70": sum(1 for fx in priced for mk in fx["markets"] for o in mk["outcomes"]
                       if o["probability"] > 0.70),
        "over_70_in_window": sum(1 for fx in priced for mk in fx["markets"] for o in mk["outcomes"]
                                 if o["probability"] > 0.70 and o["fair_price_in_brief_band"]),
        "near_miss_notes": NEAR_MISS_NOTES,
        "predictions": PREDICTIONS,
        "flagged": flagged,
        "cross_desk": {"desk": "53674ac8", "high_rows": cross, "high_rows_at_or_below_70": cross_below},
        "gaps": nhl_gaps,
        "counts": {
            "priced_fixtures": len(priced),
            "listed_unpriced": len(snk),
            "markets": markets_count,
            "outcomes": outcomes_count,
            "high_selections": len(highs),
            "high_fixtures": len({h["fixture_id"] for h in highs}),
            "medium": sum(1 for p in picks if p["headline"]["confidence"] == "medium"),
            "low": sum(1 for p in picks if p["headline"]["confidence"] == "low"),
            "predictions": len(PREDICTIONS),
            "flagged": len(flagged),
            "sports_priced": 3,
            "sports_listed": 4,
            "sports_in_scope": len(COVERAGE),
        },
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "desk.json").write_text(json.dumps(desk, indent=1) + "\n")

    with (OUT / "priced.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_id", "sport", "competition", "start_utc", "away", "home",
                    "market", "line", "selection", "probability", "fair_decimal", "american",
                    "tier", "source_url"])
        for fx in priced:
            for mk in fx["markets"]:
                for o in mk["outcomes"]:
                    w.writerow([fx["id"], fx["sport"], fx["competition"], fx["start_utc"],
                                fx["away"], fx["home"], mk["market"], mk.get("line", ""),
                                o["selection"], o["probability"], o["fair_decimal"], o["american"],
                                o.get("confidence", ""), fx["source_urls"][0]])

    with (OUT / "matches.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_id", "sport", "competition", "start_utc", "away", "home",
                    "away_record", "home_record", "winner_pick", "pick_probability",
                    "pick_american", "tier", "source_url"])
        for fx, pk in zip(priced, picks):
            h = pk["headline"]
            w.writerow([fx["id"], fx["sport"], fx["competition"], fx["start_utc"], fx["away"],
                        fx["home"], fx["away_record"], fx["home_record"], h["selection"],
                        h["probability"], h["american"], h["confidence"],
                        fx["source_urls"][0]])

    print(json.dumps(desk["counts"], indent=1))
    print("high picks:", [(h["fixture_id"], h["selection"], h["american"]) for h in desk["high_picks"]])
    print("near misses:", len(near))


if __name__ == "__main__":
    main()
