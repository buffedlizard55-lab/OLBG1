"""Turns the recorded official inputs into our own prices and picks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import s1707d752_data as D
import s1707d752_model as M

VENUE_UNCONFIRMED = {"nhl-tor-edm"}


def _nhl_complete(t: dict) -> bool:
    return all(t.get(k) is not None for k in ("gp", "gf", "ga"))


def build() -> dict:
    league = M.league_goals_per_team_game({k: v for k, v in D.NHL_TEAMS.items() if _nhl_complete(v)})
    rows = []
    for f in D.FIXTURES:
        sid = f["id"]
        sport = f["sport"]
        if sport == "Basketball":
            hr, ar = D.NBA_TEAMS[f["home"]], D.NBA_TEAMS[f["away"]]
            r = M.basketball(hr, ar)
            markets = {
                "Money line": {
                    "home": M.price_block(r["p_home"]), "away": M.price_block(r["p_away"]),
                    "label": "Home / away win"},
                "Handicap": {
                    "line": r["spread"],
                    "home": M.price_block(r["cover_home"]), "away": M.price_block(r["cover_away"]),
                    "label": f"Our line: home {r['spread']:+.1f} points"},
                "Match total": {"withheld": "No 2026-27 points data on the official standings page read."},
            }
            summary = {
                "home_rate": r["home_rate"], "away_rate": r["away_rate"],
                "home_line": f"{hr['wins']}-{hr['losses']}", "away_line": f"{ar['wins']}-{ar['losses']}",
                "home_detail": f"home {hr['home']}, road {hr['road']}, L10 {hr['l10']}, {hr['streak']}, conf {hr['conf']}",
                "away_detail": f"home {ar['home']}, road {ar['road']}, L10 {ar['l10']}, {ar['streak']}, conf {ar['conf']}",
            }
        elif sport == "Ice Hockey":
            hr, ar = D.NHL_TEAMS[f["home"]], D.NHL_TEAMS[f["away"]]
            if not (_nhl_complete(hr) and _nhl_complete(ar)):
                rows.append({**f, "priced": False, "markets": {}, "pick": None,
                             "why": f.get("incomplete_reason", "Official inputs incomplete."), "summary": {}})
                continue
            r = M.hockey(hr, ar, league)
            markets = {
                "Money line": {"home": M.price_block(r["p_home"]), "away": M.price_block(r["p_away"]),
                               "label": "Full game, overtime and shootout included"},
                "Handicap (puck line)": {"line": 1.5,
                                         "home": M.price_block(r["puck_home_minus_15"]),
                                         "away": M.price_block(r["puck_away_plus_15"]),
                                         "label": "Home -1.5 / away +1.5"},
                "Match total": {"line": r["total_line"],
                                "over": M.price_block(r["total_over"]), "under": M.price_block(r["total_under"]),
                                "label": f"Over / under {r['total_line']} goals"},
            }
            summary = {
                "home_line": f"{hr['w']}-{hr['l']}-{hr['otl']}, {hr['pts']} pts", "away_line": f"{ar['w']}-{ar['l']}-{ar['otl']}, {ar['pts']} pts",
                "home_detail": (f"{hr['gp']} GP, {hr['gf']} GF / {hr['ga']} GA, "
                                f"{hr['gf']/hr['gp']:.2f} goals for and {hr['ga']/hr['gp']:.2f} against per game, "
                                f"PP {hr['pp']}%, PK {hr['pk']}%, shots {hr['sf']} for / {hr['sa']} against"),
                "away_detail": (f"{ar['gp']} GP, {ar['gf']} GF / {ar['ga']} GA, "
                                f"{ar['gf']/ar['gp']:.2f} goals for and {ar['ga']/ar['gp']:.2f} against per game, "
                                f"PP {ar['pp']}%, PK {ar['pk']}%, shots {ar['sf']} for / {ar['sa']} against"),
                "lambda_home": round(r["lambda_home"], 2), "lambda_away": round(r["lambda_away"], 2),
            }
        else:  # Baseball
            hr, ar = D.MLB_TEAMS[f["home"]], D.MLB_TEAMS[f["away"]]
            r = M.baseball(hr, ar)
            markets = {
                "Money line": {"home": M.price_block(r["p_home"]), "away": M.price_block(r["p_away"]),
                               "label": "Full game, extra innings included"},
                "Handicap (run line)": {"withheld": "Milwaukee's season runs scored and allowed were not in the retained slice."},
                "Match total": {"withheld": "Both teams' run rates are required; only Tampa Bay's were captured."},
            }
            summary = {
                "home_line": f"{hr['wins']}-{hr['losses']}", "away_line": f"{ar['wins']}-{ar['losses']}",
                "home_detail": f"home {hr['home']}, road {hr['road']}, L10 {hr['l10']}, {hr['streak']}; {hr['note']}",
                "away_detail": f"home {ar['home']}, road {ar['road']}, L10 {ar['l10']}, {ar['streak']}; {ar['note']}",
                "pitchers": f["pitchers"],
            }

        # pick = the side with the higher originated probability in the money line
        if r["p_home"] >= r["p_away"]:
            side, p, name, opp = "home", r["p_home"], f["home_name"], f["away_name"]
        else:
            side, p, name, opp = "away", r["p_away"], f["away_name"], f["home_name"]
        price = M.price_block(p)
        if sport == "Basketball":
            sample = min(hr["wins"] + hr["losses"], ar["wins"] + ar["losses"]); floor_key = "basketball"
        elif sport == "Ice Hockey":
            sample = min(hr["gp"], ar["gp"]); floor_key = "hockey"
        else:
            sample = min(hr["wins"] + hr["losses"], ar["wins"] + ar["losses"]); floor_key = "baseball"
        graded = M.grade(p, complete=sid not in VENUE_UNCONFIRMED,
                         band=M.in_brief_band(price["american"]), sample_games=sample,
                         sample_floor=M.HIGH_MIN_GAMES[floor_key])
        rows.append({
            **f, "priced": True, "markets": markets, "summary": summary,
            "pick": {
                "side": side, "name": name, "opponent": opp, "probability": p,
                "decimal": price["decimal"], "american": price["american"],
                "confidence": graded["tier"], "caps": graded["caps"], "sample": sample,
                "band": M.in_brief_band(price["american"]),
                "literal": M.brief_literal_high(p, price["american"]),
                "prose": D.PREDICTIONS.get(sid, ""),
                "anchor": "pick-" + sid,
            },
        })
    return {"rows": rows, "league_goals": league}


if __name__ == "__main__":
    out = build()
    print(f"league goals/team/game: {out['league_goals']:.3f}")
    for r in out["rows"]:
        if not r["priced"]:
            print(f"  -- {r['id']}: unpriced")
            continue
        p = r["pick"]
        print(f"{r['id']:16s} {p['name'][:28]:28s} p={p['probability']:.3f} "
              f"dec={p['decimal']:.3f} am={p['american']:+6d} {p['confidence']:22s} "
              f"band={'Y' if p['band'] else 'N'} literal={'Y' if p['literal'] else 'N'}")
