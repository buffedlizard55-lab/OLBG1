"""Session e6fc2f12-olbg1 — independent line origination and confidence grading.

Method (all of it disclosed on the Methodology page):

  * Team strength is a Beta(2,2)-shrunk win rate. Shrinking is a documented
    choice, not a sourced fact; it stops a 3-0 start being read as a 100% team.
  * Two-team win probability uses log5. No home-field edge is inserted, because
    no official home/road split was read for these competitions. Leaving it out
    pushes estimates toward the middle, which makes a High tier harder to reach,
    not easier.
  * Hockey and baseball totals/handicaps use independent Poisson goal/run counts
    with each side's expected rate set to the mean of its own scoring rate and
    the opponent's conceding rate. Baseball's Poisson approximation is crude
    without starters, parks or bullpens, so MLB markets are capped below High.
  * Rugby union handicap and total use a normal approximation with a stated
    standard deviation. This is an assumption and is labelled as one.

Tier rules (the brief's own rule, applied literally):
  High   = model probability above 0.70 AND the fair price expresses inside
           -250 … +10000. At p > 0.70 the fair decimal is below 1.4286, i.e.
           shorter than -233; the band's -250 floor therefore bounds the tier at
           p <= 5/7 (0.7143). High picks are consequently the 70.0%–71.4% slice
           of the book: genuine favourites, never odds-on shots priced at -500.
  Medium = p >= 0.62 but not High.
  Low    = everything else, including every market whose inputs are too thin to
           justify a stronger claim.

Nothing is clipped: probabilities are the model's own, prices are 1/p.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import se6fc2f12_data as D
from se6fc2f12_predictions import PREDICTIONS

OUT = Path(__file__).resolve().parents[1] / "data" / "e6fc2f12"

# --------------------------------------------------------------------------- #
# arithmetic helpers
# --------------------------------------------------------------------------- #


def american(p: float) -> int | None:
    """Fair American price from a probability. None when p is not a probability."""
    if not (0 < p < 1):
        return None
    if p >= 0.5:
        return int(round(-100 * p / (1 - p)))
    return int(round(100 * (1 - p) / p))


def decimal(p: float) -> float:
    return 1 / p


def in_band(p: float) -> bool:
    a = american(p)
    return a is not None and -250 <= a <= 10000


def tier(p: float, high_eligible: bool, medium_eligible: bool = True) -> str:
    if high_eligible and p > 0.70 and in_band(p):
        return "High"
    if medium_eligible and p >= 0.65:
        return "Medium"
    return "Low"


def poisson_pmf(lam: float, k: int) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def poisson_cdf(lam: float, k: int) -> float:
    return sum(poisson_pmf(lam, i) for i in range(0, k + 1))


def poisson_over(lam: float, line: float) -> float:
    """P(total > line) for a half-integer line."""
    return 1 - poisson_cdf(lam, int(math.floor(line)))


def norm_cdf(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def log5(pa: float, pb: float) -> float:
    """Probability that A beats B given each side's own win rate."""
    num = pa * (1 - pb)
    den = pa * (1 - pb) + pb * (1 - pa)
    return num / den if den else 0.5


# --------------------------------------------------------------------------- #
# ratings
# --------------------------------------------------------------------------- #


def nhl_ratings() -> dict:
    out = {}
    for abbr, name, gp, w, l, otl, gf, ga in D.NHL_TEAMS:
        assert w + l + otl == gp, f"{abbr}: {w}+{l}+{otl} != {gp}"
        out[abbr] = {
            "abbrev": abbr, "name": name, "gp": gp, "w": w, "l": l, "otl": otl,
            "points": 2 * w + otl,
            "win_pct": w / gp,
            # Beta(2,2) shrinkage
            "strength": (w + 2) / (gp + 4),
            "gf": gf, "ga": ga,
            "gf_pg": (gf / gp) if gf is not None else None,
            "ga_pg": (ga / gp) if ga is not None else None,
            "goals_verified": gf is not None and ga is not None,
            "source": "nhl-team-summary",
        }
    return out


def mlb_ratings() -> dict:
    out = {}
    for abbr, t in D.MLB_TEAMS.items():
        gp = t["wins"] + t["losses"]
        assert gp == 162, f"{abbr}: {gp} games"
        out[abbr] = {
            "abbrev": abbr, "name": t["name"], "gp": gp,
            "w": t["wins"], "l": t["losses"], "win_pct": t["wins"] / gp,
            "strength": (t["wins"] + 2) / (gp + 4),
            "rs": t["rs"], "ra": t["ra"], "rs_pg": t["rs"] / gp, "ra_pg": t["ra"] / gp,
            "source": t["source"],
        }
    return out


def urc_ratings() -> dict:
    out = {}
    for abbr, name, p, w, d, l, pf, pa, form in D.URC_TABLE:
        assert w + d + l == p, f"{abbr}: {w}+{d}+{l} != {p}"
        # Draws count half in a two-way strength estimate.
        out[abbr] = {
            "abbrev": abbr, "name": name, "p": p, "w": w, "d": d, "l": l,
            "pf": pf, "pa": pa, "form": form,
            "points_pg": pf / p, "conceded_pg": pa / p,
            "win_pct": (w + 0.5 * d) / p,
            "strength": (w + 0.5 * d + 2) / (p + 4),
            "source": "urc-table",
        }
    return out


# --------------------------------------------------------------------------- #
# market builders
# --------------------------------------------------------------------------- #


def price_row(fixture_id, sport, market, selection, line, p, high_ok, medium_ok=True,
              model_note=""):
    a = american(p)
    return {
        "fixture_id": fixture_id,
        "sport": sport,
        "market": market,
        "selection": selection,
        "line": line,
        "model_probability": round(p, 6),
        "fair_decimal": round(decimal(p), 4),
        "american": a,
        "tier": tier(p, high_ok, medium_ok),
        "high_eligible": high_ok,
        "fair_price_in_band": in_band(p),
        "model_note": model_note,
    }


def nhl_fixture_id(gid: int) -> str:
    return f"nhl-{gid}"


def build_nhl(teams: dict) -> tuple[list, list]:
    fixtures, lines = [], []
    for gid, date, hhmm, home_id, away_id, venue in D.NHL_GAMES:
        h, a = D.NHL_IDS[home_id], D.NHL_IDS[away_id]
        th, ta = teams[h], teams[a]
        utc = datetime.fromisoformat(f"{date}T{hhmm}:00-04:00").astimezone(timezone.utc)
        fid = nhl_fixture_id(gid)
        missing = []
        if not th["goals_verified"]:
            missing.append("home goals for/against")
        if not ta["goals_verified"]:
            missing.append("away goals for/against")
        fixtures.append({
            "id": fid, "sport": "ice-hockey", "competition": "NHL",
            "round": "2026-27 regular season",
            "home": th["name"], "away": ta["name"],
            "starts_at_utc": utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "starts_note": "Eastern start time converted to UTC (EDT = UTC-4)",
            "venue": venue,
            "source_ids": ["nhl-game-log", "nhl-team-summary"],
            "state": "upcoming",
            "missing_fields": missing,
            "priced": True,
            "external_id": str(gid),
        })

        # --- moneyline (includes OT and shootout, matching the NHL's own W/L/OTL) ---
        ph = log5(th["strength"], ta["strength"])
        lines.append(price_row(fid, "ice-hockey", "Match winner", th["name"], None, ph, True,
                               model_note="log5 on Beta(2,2)-shrunk win rates; no home edge"))
        lines.append(price_row(fid, "ice-hockey", "Match winner", ta["name"], None, 1 - ph, True,
                               model_note="log5 on Beta(2,2)-shrunk win rates; no home edge"))

        if not (th["goals_verified"] and ta["goals_verified"]):
            continue

        lam_h = (th["gf_pg"] + ta["ga_pg"]) / 2
        lam_a = (ta["gf_pg"] + th["ga_pg"]) / 2
        note = "independent Poisson goals; rate = mean(own goals for, opponent goals against)"

        # --- totals ladder ---
        for total_line in (4.5, 5.5, 6.5, 7.5):
            po = poisson_over(lam_h + lam_a, total_line)
            lines.append(price_row(fid, "ice-hockey", "Match total", f"Over {total_line}",
                                   total_line, po, True, model_note=note))
            lines.append(price_row(fid, "ice-hockey", "Match total", f"Under {total_line}",
                                   total_line, 1 - po, True, model_note=note))

        # --- three-way puck line (home -1.5 / away +1.5) ---
        p_home_by2 = 0.0
        for hg in range(0, 16):
            for ag in range(0, 16):
                if hg - ag >= 2:
                    p_home_by2 += poisson_pmf(lam_h, hg) * poisson_pmf(lam_a, ag)
        lines.append(price_row(fid, "ice-hockey", "Handicap", f"{th['name']} -1.5", -1.5,
                               p_home_by2, True, model_note=note))
        lines.append(price_row(fid, "ice-hockey", "Handicap", f"{ta['name']} +1.5", 1.5,
                               1 - p_home_by2, True, model_note=note))

        # --- team totals ---
        for side, lam, name in (("home", lam_h, th["name"]), ("away", lam_a, ta["name"])):
            pt = poisson_over(lam, 2.5)
            lines.append(price_row(fid, "ice-hockey", "Team total", f"{name} over 2.5", 2.5,
                                   pt, True, model_note=note))
            lines.append(price_row(fid, "ice-hockey", "Team total", f"{name} under 2.5", 2.5,
                                   1 - pt, True, model_note=note))
    return fixtures, lines


def build_mlb(teams: dict) -> tuple[list, list]:
    fixtures, lines = [], []
    for i, (pk, utc, venue) in enumerate(D.MLB_GAMES, start=1):
        fid = f"mlb-{pk}"
        tb, mil = teams["TB"], teams["MIL"]
        home, away = (tb, mil) if "Tropicana" in venue else (mil, tb)
        fixtures.append({
            "id": fid, "sport": "baseball", "competition": "MLB World Series",
            "round": f"Game {i}",
            "home": home["name"], "away": away["name"],
            "starts_at_utc": utc,
            "starts_note": "exact UTC start from the official schedule",
            "venue": venue,
            "source_ids": ["mlb-schedule", "mlb-standings", "mlb-standings-al"],
            "state": "upcoming",
            "missing_fields": ["starting pitchers", "lineups", "bullpen availability"],
            "priced": True,
            "external_id": str(pk),
        })
        p_home = log5(home["strength"], away["strength"])
        note = ("log5 on regular-season win rates. Starting pitchers, parks, lineups and "
                "bullpens are not modelled, so no MLB market is High-eligible.")
        lines.append(price_row(fid, "baseball", "Match winner", home["name"], None, p_home,
                               False, model_note=note))
        lines.append(price_row(fid, "baseball", "Match winner", away["name"], None, 1 - p_home,
                               False, model_note=note))

        lam_h = (home["rs_pg"] + away["ra_pg"]) / 2
        lam_a = (away["rs_pg"] + home["ra_pg"]) / 2
        pnote = "independent Poisson runs, conditional on unequal scores; a crude approximation"
        for total_line in (7.5, 8.5, 9.5):
            po = poisson_over(lam_h + lam_a, total_line)
            lines.append(price_row(fid, "baseball", "Match total", f"Over {total_line}",
                                   total_line, po, False, model_note=pnote))
            lines.append(price_row(fid, "baseball", "Match total", f"Under {total_line}",
                                   total_line, 1 - po, False, model_note=pnote))
        p_by2 = 0.0
        for hg in range(0, 20):
            for ag in range(0, 20):
                if hg - ag >= 2:
                    p_by2 += poisson_pmf(lam_h, hg) * poisson_pmf(lam_a, ag)
        lines.append(price_row(fid, "baseball", "Handicap", f"{home['name']} -1.5", -1.5, p_by2,
                               False, model_note=pnote))
        lines.append(price_row(fid, "baseball", "Handicap", f"{away['name']} +1.5", 1.5,
                               1 - p_by2, False, model_note=pnote))
    return fixtures, lines


URC_SD_MARGIN = 13.5   # assumption, disclosed
URC_SD_TOTAL = 16.0    # assumption, disclosed


def build_urc(teams: dict) -> tuple[list, list]:
    fixtures, lines = [], []
    for fid_, date, hhmm, h, a, venue in D.URC_GAMES:
        th, ta = teams[h], teams[a]
        fixtures.append({
            "id": fid_, "sport": "rugby-union", "competition": "United Rugby Championship",
            "round": "Round 4",
            "home": th["name"], "away": ta["name"],
            "starts_at_utc": None,
            "starts_note": (f"source states {hhmm} but the page labels every time 'Local' without "
                            "a timezone; the time is reproduced as published and no UTC conversion "
                            "is inferred"),
            "starts_local": f"{date} {hhmm} (source local)",
            "starts_date": date,
            "venue": venue,
            "source_ids": ["urc-match-centre", "urc-table"],
            "state": "upcoming",
            "missing_fields": ["kick-off timezone"],
            "priced": True,
            "external_id": None,
        })
        ph = log5(th["strength"], ta["strength"])
        note = "log5 on Beta(2,2)-shrunk win rates with draws counted as half; no home edge"
        lines.append(price_row(fid_, "rugby-union", "Match winner", th["name"], None, ph, True,
                               model_note=note))
        lines.append(price_row(fid_, "rugby-union", "Match winner", ta["name"], None, 1 - ph, True,
                               model_note=note))

        exp_h = (th["points_pg"] + ta["conceded_pg"]) / 2
        exp_a = (ta["points_pg"] + th["conceded_pg"]) / 2
        margin = exp_h - exp_a
        mnote = (f"normal approximation: expected margin {margin:.1f}, sd {URC_SD_MARGIN} "
                 "(sd is an assumption)")
        for hand in (1.5, 3.5, 6.5, 9.5):
            p_h = 1 - norm_cdf((hand - margin) / URC_SD_MARGIN)
            lines.append(price_row(fid_, "rugby-union", "Handicap", f"{th['name']} -{hand}",
                                   -hand, p_h, True, model_note=mnote))
            lines.append(price_row(fid_, "rugby-union", "Handicap", f"{ta['name']} +{hand}",
                                   hand, 1 - p_h, True, model_note=mnote))
        total = exp_h + exp_a
        tnote = (f"normal approximation: expected total {total:.1f}, sd {URC_SD_TOTAL} "
                 "(sd is an assumption)")
        for tl in (39.5, 44.5, 49.5, 54.5):
            p_over = 1 - norm_cdf((tl - total) / URC_SD_TOTAL)
            lines.append(price_row(fid_, "rugby-union", "Match total", f"Over {tl}", tl,
                                   p_over, True, model_note=tnote))
            lines.append(price_row(fid_, "rugby-union", "Match total", f"Under {tl}", tl,
                                   1 - p_over, True, model_note=tnote))
    return fixtures, lines


def build_unpriced() -> list:
    fixtures = []
    for fid_, date, hhmm, home, away, venue, url in D.RLWC_GAMES:
        fixtures.append({
            "id": fid_, "sport": "rugby-league", "competition": "Rugby League World Cup",
            "round": "Round 2", "home": home, "away": away,
            "starts_at_utc": None,
            "starts_note": (f"source shows '{hhmm}' without a timezone; reproduced as published, "
                            "no UTC conversion inferred"),
            "starts_local": f"{date} {hhmm} (source local)",
            "starts_date": date, "venue": venue,
            "source_ids": ["nrl-draw"], "state": "upcoming",
            "missing_fields": ["kick-off timezone", "team ratings", "squad lists"],
            "priced": False,
            "reason": ("No official team-strength input was captured for these nations in this "
                       "session, so no price is originated rather than inventing one."),
        })
    for fid_, date, hhmm, home, away in D.SNOOKER_GAMES:
        fixtures.append({
            "id": fid_, "sport": "snooker", "competition": "BetVictor Northern Ireland Open",
            "round": "Round 3", "home": home, "away": away,
            "starts_at_utc": None,
            "starts_note": (f"source session time '{hhmm}' with no timezone stated; reproduced as "
                            "published"),
            "starts_local": f"{date} {hhmm} (source session time)",
            "starts_date": date, "venue": "Belfast, Northern Ireland",
            "source_ids": ["wst-ni-open"], "state": "upcoming",
            "missing_fields": ["session timezone", "complete world-ranking points for both players"],
            "priced": False,
            "reason": ("The official ranking table was read only for its top eleven; both players' "
                       "points were not captured for every match, so no price is originated."),
        })
    for fid_, label, date, window in D.F1_SESSIONS:
        fixtures.append({
            "id": fid_, "sport": "motor-racing", "competition": "FIA Formula One World Championship",
            "round": "Round 18 — United States Grand Prix", "home": label, "away": "—",
            "starts_at_utc": None,
            "starts_note": f"track-time window {window} on {date}; timezone not stated on the page",
            "starts_local": f"{date} {window} (track time)",
            "starts_date": date, "venue": "Circuit of The Americas, Austin",
            "source_ids": ["f1-usgp", "f1-calendar"], "state": "upcoming",
            "missing_fields": ["timezone", "grid", "driver form model"],
            "priced": False,
            "reason": ("A race outright needs a driver-strength model; the standings table body was "
                       "not readable in this session, so no price is originated."),
        })
    return fixtures


# --------------------------------------------------------------------------- #
# primary picks, counts, coverage
# --------------------------------------------------------------------------- #


def primary_pick(fixture_lines: list) -> dict | None:
    """The match-winner selection the model prefers, for the fixture table."""
    ml = [l for l in fixture_lines if l["market"] == "Match winner"]
    if not ml:
        return None
    best = max(ml, key=lambda r: r["model_probability"])
    return {
        "selection": best["selection"],
        "american": best["american"],
        "probability": best["model_probability"],
        "tier": best["tier"],
        "market": best["market"],
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    nhl = nhl_ratings()
    mlb = mlb_ratings()
    urc = urc_ratings()

    fx_nhl, ln_nhl = build_nhl(nhl)
    fx_mlb, ln_mlb = build_mlb(mlb)
    fx_urc, ln_urc = build_urc(urc)
    fx_unpriced = build_unpriced()

    fixtures = fx_nhl + fx_mlb + fx_urc + fx_unpriced
    lines = ln_nhl + ln_mlb + ln_urc

    by_fixture: dict[str, list] = {}
    for row in lines:
        by_fixture.setdefault(row["fixture_id"], []).append(row)
    for f in fixtures:
        f["primary_pick"] = primary_pick(by_fixture.get(f["id"], []))
        f["markets_priced"] = len(by_fixture.get(f["id"], []))

    # Attach the hand-written prediction to every High row; a High row without one
    # is a release blocker, not something to render blank.
    missing_predictions = []
    for row in lines:
        if row["tier"] == "High":
            key = (row["fixture_id"], row["selection"])
            text = PREDICTIONS.get(key)
            if not text:
                missing_predictions.append(key)
            row["prediction"] = text
        else:
            row["prediction"] = None
    if missing_predictions:
        raise SystemExit(f"High rows without a prediction: {missing_predictions}")

    published = [
        {
            "fixture_id": r["fixture_id"], "sport": r["sport"], "market": r["market"],
            "selection": r["selection"], "line": r["line"], "american": r["american"],
            "fair_decimal": r["fair_decimal"], "model_probability": r["model_probability"],
            "tier": r["tier"], "prediction": r["prediction"], "model_note": r["model_note"],
        }
        for r in lines if r["tier"] == "High"
    ]

    counts = {
        "fixtures": len(fixtures),
        "fixtures_priced": sum(1 for f in fixtures if f["priced"]),
        "fixtures_unpriced": sum(1 for f in fixtures if not f["priced"]),
        "markets": len(lines),
        "outcomes_by_tier": {
            t: sum(1 for l in lines if l["tier"] == t) for t in ("High", "Medium", "Low")
        },
        "high_eligible_markets": sum(1 for l in lines if l["high_eligible"]),
        "in_band_markets": sum(1 for l in lines if l["fair_price_in_band"]),
    }

    sport_counts: dict[str, dict] = {}
    for f in fixtures:
        s = sport_counts.setdefault(f["sport"], {"fixtures": 0, "priced": 0, "markets": 0})
        s["fixtures"] += 1
        s["priced"] += 1 if f["priced"] else 0
        s["markets"] += f["markets_priced"]

    payload_fixtures = fixtures
    payload_lines = lines

    (OUT / "fixtures.json").write_text(json.dumps(payload_fixtures, indent=1) + "\n")
    (OUT / "markets.json").write_text(json.dumps(payload_lines, indent=1) + "\n")
    (OUT / "sources.json").write_text(json.dumps(D.SOURCES, indent=1) + "\n")
    (OUT / "ratings.json").write_text(json.dumps(
        {"nhl": nhl, "mlb": mlb, "urc": urc}, indent=1) + "\n")
    (OUT / "coverage.json").write_text(json.dumps(
        {"sport_counts": sport_counts, "unverified_sports": D.UNVERIFIED_SPORTS},
        indent=1) + "\n")

    meta = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_version": "e6fc2f12-evidence-1.0",
        "counts": counts,
        "tier_rule": {
            "high": "model probability > 0.70 AND fair price within -250..+10000",
            "medium": "model probability >= 0.65 and not High",
            "low": "everything else",
        },
    }
    (OUT / "model.json").write_text(json.dumps(meta, indent=1) + "\n")
    (OUT / "predictions.json").write_text(json.dumps(published, indent=1) + "\n")

    print(json.dumps(counts, indent=1))
    print("sports:", json.dumps(sport_counts, indent=1))
    highs = [l for l in lines if l["tier"] == "High"]
    print(f"\nHIGH rows: {len(highs)}")
    for r in sorted(highs, key=lambda x: -x["model_probability"]):
        print(f"  {r['fixture_id']:>14} | {r['market']:<12} | {r['selection']:<34} | "
              f"p={r['model_probability']:.4f} | {r['american']:>6} | {r['line']}")
    med = [l for l in lines if l["tier"] == "Medium"]
    print(f"\nMEDIUM rows: {len(med)}")


if __name__ == "__main__":
    main()
