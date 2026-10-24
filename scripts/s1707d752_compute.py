"""Turns the recorded official inputs into our own prices and picks.

Nothing here reads the network. If an input is missing the row is returned
unpriced with the reason, never filled in.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import s1707d752_data as D
import s1707d752_model as M

# Matches whose home/away assignment could not be confirmed on an official page.
VENUE_UNCONFIRMED = {"nhl-tor-edm"}

# Games already under way when the sources were read. Pricing a live game would
# not be a prediction, so they are held back.
LIVE = set()


def _nhl_ready(t: dict) -> bool:
    return t is not None and all(t.get(k) is not None for k in ("gp", "w", "l", "otl", "gf", "ga"))


def build() -> dict:
    league = M.league_goals_per_team_game(
        {k: v for k, v in D.NHL_TEAMS.items() if _nhl_ready(v)})
    rows = []
    for f in D.FIXTURES:
        sid, sport = f["id"], f["sport"]
        row = {**f, "priced": False, "markets": {}, "pick": None, "summary": {}}

        if sport == "Basketball":
            hr, ar = D.NBA_TEAMS[f["home"]], D.NBA_TEAMS[f["away"]]
            r = M.basketball(hr, ar)
            row["markets"] = {
                "Money line": {"home": M.price_block(r["p_home"]), "away": M.price_block(r["p_away"]),
                               "label": "Two-way, no draw"},
                "Handicap": {"withheld": ("The standings read gives wins and losses, not points scored or "
                                          "conceded, so a points line cannot be originated from it.")},
                "Match total": {"withheld": ("No points-for or points-against figures were published on the "
                                             "page read, so a total would be invented.")},
            }
            row["summary"] = {
                "home_line": f"{hr['wins']}-{hr['losses']}", "away_line": f"{ar['wins']}-{ar['losses']}",
                "home_detail": (f"{hr['wins']}-{hr['losses']} overall, {hr['home']} at home, {hr['road']} on the "
                                f"road, {hr['l10']} last ten, {hr['streak']}, conference {hr['conf']}"),
                "away_detail": (f"{ar['wins']}-{ar['losses']} overall, {ar['home']} at home, {ar['road']} on the "
                                f"road, {ar['l10']} last ten, {ar['streak']}, conference {ar['conf']}"),
                "sample": min(hr["wins"] + hr["losses"], ar["wins"] + ar["losses"]),
                "rate_home": round(r["home_rate"], 3), "rate_away": round(r["away_rate"], 3),
            }
            cand = [(r["p_home"], f["home_name"], "home"), (r["p_away"], f["away_name"], "away")]

        elif sport == "Ice Hockey":
            hr, ar = D.NHL_TEAMS[f["home"]], D.NHL_TEAMS[f["away"]]
            if not (_nhl_ready(hr) and _nhl_ready(ar)):
                row["why"] = f.get("incomplete_reason", "The league team summary did not carry both clubs.")
                rows.append(row)
                continue
            r = M.hockey(hr, ar, league)
            row["markets"] = {
                "Money line": {"home": M.price_block(r["p_home"]), "away": M.price_block(r["p_away"]),
                               "label": "Three-way result folded into a two-way price, overtime and shootout included"},
                "Handicap (puck line)": {"line": 1.5, "home": M.price_block(r["puck_home_minus_15"]),
                                         "away": M.price_block(r["puck_away_plus_15"]),
                                         "label": "Home -1.5 against away +1.5"},
                "Match total": {"line": r["total_line"], "over": M.price_block(r["total_over"]),
                                "under": M.price_block(r["total_under"]),
                                "label": f"Goals, over or under {r['total_line']}"},
            }
            row["summary"] = {
                "home_line": f"{hr['w']}-{hr['l']}-{hr['otl']}, {hr['pts']} pts",
                "away_line": f"{ar['w']}-{ar['l']}-{ar['otl']}, {ar['pts']} pts",
                "home_detail": (f"{hr['gp']} games, {hr['gf']} goals for and {hr['ga']} against "
                                f"({hr['gf']/hr['gp']:.2f}/{hr['ga']/hr['gp']:.2f} per game), power play "
                                f"{hr['pp']}%, penalty kill {hr['pk']}%, {hr['sf']} shots for and {hr['sa']} "
                                f"against per game"),
                "away_detail": (f"{ar['gp']} games, {ar['gf']} goals for and {ar['ga']} against "
                                f"({ar['gf']/ar['gp']:.2f}/{ar['ga']/ar['gp']:.2f} per game), power play "
                                f"{ar['pp']}%, penalty kill {ar['pk']}%, {ar['sf']} shots for and {ar['sa']} "
                                f"against per game"),
                "sample": min(hr["gp"], ar["gp"]),
                "goals_expect_home": round(r["lambda_home"], 2),
                "goals_expect_away": round(r["lambda_away"], 2),
                "league_goals": round(league, 2),
            }
            cand = [(r["p_home"], f["home_name"], "home"), (r["p_away"], f["away_name"], "away")]

        else:  # Baseball
            hr, ar = D.MLB_TEAMS[f["home"]], D.MLB_TEAMS[f["away"]]
            r = M.baseball(hr, ar)
            row["markets"] = {
                "Money line": {"home": M.price_block(r["p_home"]), "away": M.price_block(r["p_away"]),
                               "label": "Full game, extra innings included"},
                "Handicap (run line)": {"withheld": ("Milwaukee's runs scored and allowed were cut off at the read "
                                                     "boundary, so a -1.5 run line cannot be originated.")},
                "Match total": {"withheld": ("Only Tampa Bay's run rates were captured; a two-sided total needs "
                                             "both.")},
            }
            row["summary"] = {
                "home_line": f"{hr['wins']}-{hr['losses']}", "away_line": f"{ar['wins']}-{ar['losses']}",
                "home_detail": (f"{hr['wins']}-{hr['losses']}, {hr['home']} at home, {hr['road']} on the road, "
                                f"{hr['l10']} last ten, {hr['streak']}, {hr['note']}"),
                "away_detail": (f"{ar['wins']}-{ar['losses']}, {hr['home']} home / {ar['road']} road, "
                                f"{ar['l10']} last ten, {ar['streak']}, {ar['note']}"),
                "sample": min(hr["wins"] + hr["losses"], ar["wins"] + ar["losses"]),
                "home_rate": round(r["home_rate"], 3), "away_rate": round(r["away_rate"], 3),
            }
            cand = [(r["p_home"], f["home_name"], "home"), (r["p_away"], f["away_name"], "away")]

        cand.sort(reverse=True)
        p, name, side = cand[0]
        band = M.in_brief_band(M.american_from_decimal(1 / p))
        literal = M.brief_literal_high(p, M.american_from_decimal(1 / p))
        complete = sid not in VENUE_UNCONFIRMED and bool(f.get("utc"))
        tier = M.grade(p, complete=complete, band=band,
                       sample_games=row["summary"]["sample"],
                       sample_floor=M.HIGH_MIN_GAMES[{"Basketball": "basketball",
                                                      "Ice Hockey": "hockey",
                                                      "Baseball": "baseball"}[sport]])
        caps = list(tier["caps"])
        if sid in VENUE_UNCONFIRMED:
            caps.insert(0, "Home and away not confirmed on an official page, so the pick is capped at Medium.")
        if not f.get("utc"):
            caps.append("Start time not confirmed by an official source.")

        row.update({
            "priced": True,
            "side": side,
            "complete": complete,
            "pick": {
                "name": name, "side": side, "sport": sport, "competition": f["competition"],
                "american": M.american_from_decimal(1 / p), "decimal": round(1 / p, 3),
                "probability": round(p, 6), "band": band, "literal": literal,
                "confidence": tier["tier"], "caps": caps,
                "anchor": f"pick-{sid}",
                "prose": D.PREDICTIONS[sid],
            },
        })
        rows.append(row)
    return {"rows": rows, "league_goals": round(league, 3)}


if __name__ == "__main__":
    data = build()
    print(f"league goals/team/game: {data['league_goals']}")
    n = 0
    for r in data["rows"]:
        if r["priced"]:
            p = r["pick"]
            n += 1
            print(f"{r['id']:16} {p['name'][:26]:26} p={p['probability']:.3f} dec={p['decimal']:.3f} "
                  f"am={p['american']:>6} {p['confidence']:6} band={'Y' if p['band'] else 'N'} "
                  f"literal={'Y' if p['literal'] else 'N'} utc={r['utc']}")
        else:
            print(f"{r['id']:16} UNPRICED  {r.get('why','')[:80]}")
    print(f"{n} priced of {len(data['rows'])}")
