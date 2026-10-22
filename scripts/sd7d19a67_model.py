"""Session d7d19a67-olbg1 (TD7D19, claimed as T65) - own line origination, confidence tiers and desk assembly.

What this script does
---------------------
It turns the officially-read fixtures and statistics in ``scripts/sd7d19a67_data.py`` into
originated betting lines, a match-winner pick with a Low/Medium/High confidence label for every
priced fixture, and the desk artefacts under ``data/d7d19a67/``.

Model versions (all disclosed on the desk; none calibrated out-of-sample)
-------------------------------------------------------------------------
nhl-poisson-v1
    Independent Poisson goal counts per club, rates taken from the official NHL standings read
    this session (``api-web.nhle.com/v1/standings/2026-10-21``):
    ``rate_for = goalFor / gamesPlayed``, ``rate_against = goalAgainst / gamesPlayed``,
    ``lambda_A = (rate_for_A + rate_against_B) / 2``. No home-ice bonus is inserted. Games
    decided after regulation are split between the clubs in proportion to lambda - that split is
    a model assumption, not an official overtime statistic.
mlb-poisson-v1
    The same construction on official 2026 regular-season runs scored / runs allowed per game.
    No pitcher, park, lineup, rest or postseason adjustment, because none was read officially.
el-log5-v1
    log5 on Beta(2,2)-shrunk win rates from the official EuroLeague Round 7 Game Center records.
    Winner market only: the official preview publishes no margin distribution, so handicap and
    total lines are withheld rather than invented.

Confidence policy
-----------------
The brief asks for a match winner and a Low/Medium/High label per match, so the confidence label
attaches to the **winner market**. Derivative markets (3-way regulation, handicap, match total)
are priced and published with probability, fair decimal and fair American prices, but they are
not graded with the match-confidence label - they are published as originated lines.

High   probability >= 0.60 AND originated American price inside -250..+10000 AND fixture plus both
       sides' statistical inputs were read from official pages this session AND a unique
       hand-written prediction of at least 30 words exists AND no official context sentence read
       this session contradicts the lean.
Medium everything else that is in-window with probability >= 0.52, plus in-window/out-of-window
       strong favourites (probability > 0.714285, i.e. a price shorter than -250), plus picks
       capped by a contradicting official sentence.
Low    no evidence-backed lean (probability < 0.52).

Prices are originated fair prices: ``decimal = 1/p`` with no margin and no clipping, American
derived from the unrounded decimal. Nothing on this desk is a bookmaker quote and no edge is
claimed.
"""

import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sd7d19a67_data as D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "d7d19a67")

HIGH_FLOOR = 0.60
MEDIUM_FLOOR = 0.52
WINDOW_SHORT_LIMIT = -250.0
WINDOW_LONG_LIMIT = 10000.0
GATE_A_FLOOR = 0.70
# probability whose fair price is exactly -250
WINDOW_EDGE_PROB = 250.0 / 350.0

# Official context read this session that contradicts the model lean -> cap at Medium.
HIGH_BLOCKED = {
    "el-E2026-63": ("capped at Medium: the official EuroLeague Round 7 Game Center preview for this "
                    "fixture says it should be a close game and records that the two clubs split their "
                    "meetings last season with both games decided by a single possession, which "
                    "contradicts a 70% lean"),
    "el-E2026-62": ("capped at Medium: the official EuroLeague Round 7 Game Center preview records that "
                    "the home team has won each of the last five meetings between these clubs and that "
                    "Real Madrid are 1-4 away from home this season, which contradicts the log5 lean on "
                    "the visiting side"),
}

UNPRICED_REASON = {
    "tennis": ("the official order of play read this session publishes names, seeds and start order "
               "only - no ranking points, form or head-to-head - and no official ranking or "
               "results page was read for these players, so no price is originated"),
    "cricket": ("the official PCB tournament page publishes date, teams and ground only: no start "
                "time, no squad and no form input, so no price is originated"),
    "rugby-league": ("the official IRL fixture list publishes teams, date, clock and venue only - no "
                     "form, ladder or points input for these World Cup fixtures - so no price is "
                     "originated"),
}


def poisson_pmf(lam, n):
    return math.exp(-lam) * lam ** n / math.factorial(n)


def score_matrix(lam_a, lam_b, max_goals=12):
    return [[poisson_pmf(lam_a, i) * poisson_pmf(lam_b, j) for j in range(max_goals + 1)]
            for i in range(max_goals + 1)]


def matrix_parts(m):
    p_a = sum(m[i][j] for i in range(len(m)) for j in range(len(m[0])) if i > j)
    p_b = sum(m[i][j] for i in range(len(m)) for j in range(len(m[0])) if j > i)
    p_tie = max(0.0, 1.0 - p_a - p_b)
    p_a_by2 = sum(m[i][j] for i in range(len(m)) for j in range(len(m[0])) if i - j >= 2)
    return p_a, p_b, p_tie, p_a_by2


def american_from_prob(p):
    """(American, decimal) from an unrounded probability, no margin, no clipping."""
    dec = 1.0 / p
    amer = -round(p / (1.0 - p) * 100.0) if p >= 0.5 else round((1.0 - p) / p * 100.0)
    return amer, dec


def in_window(p):
    amer, _ = american_from_prob(p)
    return bool(WINDOW_SHORT_LIMIT <= amer <= WINDOW_LONG_LIMIT)


def price(sel, p):
    """One priced outcome. ``probability`` is the rounded display value; ``probability_exact`` is the
    unrounded model probability the prices were derived from, so a reviewer can re-derive them."""
    amer, dec = american_from_prob(p)
    return {"selection": sel, "probability": round(p, 4), "probability_exact": p,
            "fair_decimal": round(dec, 4), "fair_american": amer,
            "in_brief_window": bool(WINDOW_SHORT_LIMIT <= amer <= WINDOW_LONG_LIMIT)}


# -------------------------------------------------------------------- models
def poisson_fixture(away, home, gf_a, ga_a, gp_a, gf_h, ga_h, gp_h, label_for, label_total,
                    model, inputs, max_goals=12, total_lines=(), name_a=None, name_h=None):
    lam_a = ((gf_a / gp_a) + (ga_h / gp_h)) / 2.0
    lam_h = ((gf_h / gp_h) + (ga_a / gp_a)) / 2.0
    m = score_matrix(lam_a, lam_h, max_goals=max_goals)
    p_a_reg, p_h_reg, p_tie, p_a_by2 = matrix_parts(m)
    share_a = lam_a / (lam_a + lam_h)
    p_a = p_a_reg + p_tie * share_a
    p_h = 1.0 - p_a
    totals = {line: sum(m[i][j] for i in range(len(m)) for j in range(len(m[0])) if i + j > line)
              for line in total_lines}
    na, nh = name_a or away, name_h or home
    markets = [{
        "market": "Match winner (including %s)" % label_for,
        "family": "winner", "model": model, "inputs": inputs,
        "outcomes": [price("%s (%s)" % (na, away), p_a), price("%s (%s)" % (nh, home), p_h)],
    }]
    if p_tie > 0:
        markets.append({
            "market": "Result after regulation (3-way)",
            "family": "regulation", "model": model, "inputs": inputs,
            "outcomes": [price("%s regulation win" % away, p_a_reg),
                         price("Draw after regulation", p_tie),
                         price("%s regulation win" % home, p_h_reg)],
        })
    markets.append({
        "market": "Handicap %s -1.5 %s" % (away, label_total),
        "family": "handicap", "model": model, "inputs": inputs,
        "outcomes": [price("%s -1.5" % away, p_a_by2), price("%s +1.5" % home, 1.0 - p_a_by2)],
    })
    for line in total_lines:
        markets.append({
            "market": "Match total %.1f %s" % (line, label_total),
            "family": "total", "model": model, "inputs": inputs,
            "outcomes": [price("Over %.1f" % line, totals[line]),
                         price("Under %.1f" % line, 1.0 - totals[line])],
        })
    detail = {"lambda_away": round(lam_a, 4), "lambda_home": round(lam_h, 4),
              "expected_total": round(lam_a + lam_h, 4)}
    winner = p_a >= p_h and (p_a, "%s (%s)" % (na, away)) or (p_h, "%s (%s)" % (nh, home))
    return markets, detail, {"probability": round(winner[0], 4), "probability_exact": winner[0],
                             "selection": winner[1]}


def nhl_fixture(away, home):
    a, h = D.NHL_STANDINGS[away], D.NHL_STANDINGS[home]
    inputs = ("official NHL standings for 2026-10-21: games played, goals for and goals against "
              "for %s and %s" % (away, home))
    return poisson_fixture(away, home, a[4], a[5], a[0], h[4], h[5], h[0],
                           "overtime and shootout", "goals", "nhl-poisson-v1", inputs,
                           total_lines=(5.5, 6.5), name_a=D.NHL_NAMES[away], name_h=D.NHL_NAMES[home])


def mlb_fixture(away, home):
    a, h = D.MLB_TEAMS[away], D.MLB_TEAMS[home]
    inputs = ("official MLB 2026 regular-season runs scored and runs allowed for %s and %s"
              % (away, home))
    return poisson_fixture(away, home, a["rs"], a["ra"], a["w"] + a["l"], h["rs"], h["ra"],
                           h["w"] + h["l"], "extra innings", "runs", "mlb-poisson-v1", inputs,
                           max_goals=14, total_lines=(7.5, 8.5, 9.5),
                           name_a=a["name"], name_h=h["name"])


def el_fixture(away, home):
    a, h = D.EUROLEAGUE_TEAMS[away], D.EUROLEAGUE_TEAMS[home]
    p_a_raw = (a["w"] + 2.0) / (a["w"] + a["l"] + 4.0)
    p_h_raw = (h["w"] + 2.0) / (h["w"] + h["l"] + 4.0)
    p_a = (p_a_raw - p_a_raw * p_h_raw) / (p_a_raw + p_h_raw - 2.0 * p_a_raw * p_h_raw)
    p_h = 1.0 - p_a
    inputs = ("official EuroLeague Round 7 Game Center records: %s %d-%d, %s %d-%d"
              % (a["name"], a["w"], a["l"], h["name"], h["w"], h["l"]))
    markets = [{
        "market": "Match winner", "family": "winner", "model": "el-log5-v1", "inputs": inputs,
        "outcomes": [price("%s (%s)" % (a["name"], away), p_a),
                     price("%s (%s)" % (h["name"], home), p_h)],
    }]
    detail = {"shrunk_winrate_away": round(p_a_raw, 4), "shrunk_winrate_home": round(p_h_raw, 4),
              "log5_probability_away": round(p_a, 4)}
    winner = (p_a, "%s (%s)" % (a["name"], away)) if p_a >= p_h else (p_h, "%s (%s)" % (h["name"], home))
    withheld = [
        {"market": "Handicap", "reason": "the official Round 7 Game Center publishes club records and "
                                         "points-for/points-against ranks but no margin distribution for "
                                         "either club, so a spread would need an invented input"},
        {"market": "Match total", "reason": "official points-per-game figures were read for some clubs "
                                            "only and never for both sides of one fixture, so a total "
                                            "line is withheld rather than estimated"},
    ]
    return markets, detail, {"probability": round(winner[0], 4), "probability_exact": winner[0],
                             "selection": winner[1]}, withheld


# -------------------------------------------------------------------- tiering
def tier_for(fixture_key, p):
    """(tier, gate_a_literal, reason) for a winner pick at originated probability p."""
    amer, _ = american_from_prob(p)
    gate_a = bool(p > GATE_A_FLOOR and WINDOW_SHORT_LIMIT <= amer <= WINDOW_LONG_LIMIT)
    if not (WINDOW_SHORT_LIMIT <= amer <= WINDOW_LONG_LIMIT):
        return ("Medium", gate_a,
                "originated price %+d sits outside the brief's -250..+10000 window, so this pick "
                "cannot be High under the brief's own rule even at probability %.3f" % (amer, p))
    if fixture_key in HIGH_BLOCKED:
        return ("Medium", gate_a, HIGH_BLOCKED[fixture_key])
    if p >= HIGH_FLOOR:
        return ("High", gate_a,
                "in-window originated price %+d, official inputs read for both sides this session, "
                "model probability %.3f at or above the desk's %.2f High floor, no contradicting "
                "official context" % (amer, p, HIGH_FLOOR))
    if p >= MEDIUM_FLOOR:
        return ("Medium", gate_a,
                "in-window originated price %+d but model probability %.3f is below the desk's %.2f "
                "High floor" % (amer, p, HIGH_FLOOR))
    return ("Low", gate_a,
            "model probability %.3f leaves no evidence-backed lean (the two sides are within "
            "%.1f percentage points)" % (p, abs(0.5 - p) * 100.0))


# -------------------------------------------------------------------- assembly
def build_fixtures():
    fixtures = []
    for f in D.FIXTURES:
        row = dict(f)
        row["sport_name"] = D.SPORT_NAMES[f["sport"]]
        row["olbg_hub"] = D.SPORT_OLBG.get(f["sport"])
        row["blank_fields"] = list(f.get("blank_fields") or [])
        row["flags"] = [f["flag"]] if f.get("flag") else []
        row["time_local"] = f.get("time_local")
        row["context"] = list(D.CONTEXT.get(f["key"], []))
        markets, detail, winner, withheld = [], {}, None, []
        priced, reason = True, None
        if f["sport"] == "ice-hockey":
            if not f.get("away") or not f.get("home"):
                priced, reason = False, ("the away club was not inside the official schedule chunks this "
                                         "desk read, so there is no second side to price")
            else:
                markets, detail, winner = nhl_fixture(f["away"], f["home"])
                row["standings"] = {
                    side: dict(zip(("gp", "w", "l", "otl", "gf", "ga", "points"), D.NHL_STANDINGS[c]))
                    for side, c in (("away", f["away"]), ("home", f["home"]))}
                for side in ("away", "home"):
                    row["standings"][side]["name"] = D.NHL_NAMES[f[side]]
                    row["standings"][side]["streak"] = "%s%d" % D.NHL_STREAK[f[side]]
        elif f["sport"] == "baseball":
            markets, detail, winner = mlb_fixture(f["away"], f["home"])
            row["standings"] = {side: dict(D.MLB_TEAMS[f[side]]) for side in ("away", "home")}
        elif f["sport"] == "basketball":
            markets, detail, winner, withheld = el_fixture(f["away"], f["home"])
            row["standings"] = {side: dict(D.EUROLEAGUE_TEAMS[f[side]]) for side in ("away", "home")}
        else:
            priced, reason = False, UNPRICED_REASON.get(f["sport"], "no official statistical input was read for this fixture this session")
        for i, mk in enumerate(markets):
            mk["market_id"] = "%s#m%d" % (f["key"], i + 1)
            mk["stronger_side"] = max(mk["outcomes"], key=lambda o: o["probability"])["selection"]
            mk["stronger_probability"] = max(o["probability"] for o in mk["outcomes"])
            mk["stronger_american"] = max(mk["outcomes"], key=lambda o: o["probability"])["fair_american"]
            mk["line_signature"] = "%s|%s" % (mk["model"], ",".join(
                "%s=%.4f" % (o["selection"], o["probability"]) for o in mk["outcomes"]))
        row["priced"] = priced
        row["unpriced_reason"] = reason
        row["markets"] = markets
        row["withheld_markets"] = withheld
        row["model_detail"] = detail
        if winner:
            tier, gate_a, tier_reason = tier_for(f["key"], winner["probability"])
            amer, dec = american_from_prob(winner["probability"])
            row["winner_pick"] = {
                "selection": winner["selection"], "probability": winner["probability"],
                "probability_exact": winner["probability_exact"],
                "fair_decimal": round(dec, 4), "fair_american": amer,
                "in_brief_window": in_window(winner["probability"]), "tier": tier,
                "gate_a_literal": gate_a, "tier_reason": tier_reason,
                "model": markets[0]["model"], "inputs": markets[0]["inputs"],
            }
        else:
            row["winner_pick"] = None
        fixtures.append(row)
    return fixtures


def mark_duplicates(fixtures):
    """Flag fixtures whose originated winner line is byte-identical to another fixture's."""
    groups = {}
    for f in fixtures:
        if f["winner_pick"]:
            sig = "%s|%s|%.4f" % (f["winner_pick"]["model"], f["winner_pick"]["selection"],
                                  f["winner_pick"]["probability"])
            groups.setdefault(sig, []).append(f["key"])
    dupes = {sig: keys for sig, keys in groups.items() if len(keys) > 1}
    for f in fixtures:
        if not f["winner_pick"]:
            continue
        sig = "%s|%s|%.4f" % (f["winner_pick"]["model"], f["winner_pick"]["selection"],
                              f["winner_pick"]["probability"])
        if sig in dupes:
            f["duplicate_line_keys"] = [k for k in dupes[sig] if k != f["key"]]
            f.setdefault("flags", [])
            if "F-D7D-13" not in f["flags"]:
                f["flags"].append("F-D7D-13")
        else:
            f["duplicate_line_keys"] = []
    return dupes


def summarise(fixtures):
    counts = {"fixtures": len(fixtures), "priced": 0, "unpriced": 0, "markets": 0, "outcomes": 0,
              "high": 0, "medium": 0, "low": 0, "gate_a_winner": 0, "gate_a_any_selection": 0,
              "out_of_window_strong": 0, "duplicate_line_fixtures": 0}
    per_sport = {}
    for f in fixtures:
        s = per_sport.setdefault(f["sport"], {"name": f["sport_name"], "olbg_hub": f.get("olbg_hub"),
                                              "fixtures": 0, "priced": 0, "markets": 0, "high": 0,
                                              "medium": 0, "low": 0, "unpriced_reason": f["unpriced_reason"]})
        s["fixtures"] += 1
        counts["priced" if f["priced"] else "unpriced"] += 1
        if f["priced"]:
            s["priced"] += 1
        if f.get("duplicate_line_keys"):
            counts["duplicate_line_fixtures"] += 1
        for mk in f["markets"]:
            counts["markets"] += 1
            s["markets"] += 1
            counts["outcomes"] += len(mk["outcomes"])
            for o in mk["outcomes"]:
                if o["probability"] > GATE_A_FLOOR and o["in_brief_window"]:
                    counts["gate_a_any_selection"] += 1
                if o["probability"] > WINDOW_EDGE_PROB + 1e-9 and not o["in_brief_window"]:
                    counts["out_of_window_strong"] += 1
        wp = f["winner_pick"]
        if wp:
            counts[wp["tier"].lower()] += 1
            s[wp["tier"].lower()] += 1
            if wp["gate_a_literal"]:
                counts["gate_a_winner"] += 1
    return counts, per_sport


def write_desk(fixtures, counts, per_sport, dupes):
    os.makedirs(OUT_DIR, exist_ok=True)
    import sd7d19a67_predictions as P
    desk = {
        "schema_version": 1,
        "session": D.SESSION,
        "task": D.TASK,
        "generated_at_utc": D.DESK_READ_UTC,
        "window": {"from_utc": D.WINDOW_FROM_UTC, "until_utc": D.WINDOW_UNTIL_UTC,
                   "rule": "fixtures dated 22-29 October 2026 exactly as published by the official "
                           "source named on the row; rows whose official page carried no usable date "
                           "are not published"},
        "confidence_policy": {
            "high_floor_probability": HIGH_FLOOR,
            "medium_floor_probability": MEDIUM_FLOOR,
            "price_window_american": [WINDOW_SHORT_LIMIT, WINDOW_LONG_LIMIT],
            "window_edge_probability": round(WINDOW_EDGE_PROB, 6),
            "gate_a_literal": "probability > 70%% AND originated price inside -250..+10000, which "
                              "arithmetically leaves only -250..-233 (70.0%%..71.4%%)",
            "gate_b_published_high": "originated price inside -250..+10000 AND probability >= %.2f AND "
                                     "fixture and both sides' inputs read from official pages this "
                                     "session AND a unique hand-written prediction of at least 30 words "
                                     "AND no contradicting official context sentence" % HIGH_FLOOR,
            "tier_scope": "the confidence label attaches to the winner market of each fixture; "
                          "derivative markets are published as originated lines without the match "
                          "confidence label",
            "model_versions": ["nhl-poisson-v1", "mlb-poisson-v1", "el-log5-v1"],
            "pricing": "fair price only: decimal = 1/probability, no margin, no clipping, American "
                       "derived from the unrounded decimal",
            "not_claimed": ["bookmaker price", "price availability at any operator", "betting edge",
                            "out-of-sample calibration", "player availability beyond the official "
                            "sentences quoted in the context column"],
            "high_blocked": HIGH_BLOCKED,
        },
        "counts": counts,
        "per_sport": per_sport,
        "duplicate_line_groups": dupes,
        "fixtures": fixtures,
        "sources": D.SOURCES,
        "gaps": D.GAPS,
        "flags": D.FLAGS,
        "context": D.CONTEXT,
        "nhl_standings": {k: dict(list(zip(("gp", "w", "l", "otl", "gf", "ga", "points"), v))
                                  + [("name", D.NHL_NAMES[k]), ("streak", "%s%d" % D.NHL_STREAK[k])])
                          for k, v in D.NHL_STANDINGS.items()},
        "nhl_standings_url": D.NHL_STANDINGS_URL,
        "nhl_results": D.NHL_RESULTS,
        "mlb_teams": D.MLB_TEAMS,
        "euroleague_teams": D.EUROLEAGUE_TEAMS,
    }
    desk = P.attach(desk)
    counts["predictions"] = len(P.PREDICTIONS)
    desk["counts"]["predictions"] = counts["predictions"]
    with open(os.path.join(OUT_DIR, "desk.json"), "w", encoding="utf-8") as fh:
        json.dump(desk, fh, indent=1, ensure_ascii=False, sort_keys=False)
        fh.write("\n")

    with open(os.path.join(OUT_DIR, "fixtures.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_key", "sport", "sport_name", "competition", "away", "home", "date",
                    "time_utc", "time_local", "venue", "status", "priced", "winner_selection",
                    "probability", "fair_decimal", "fair_american", "in_brief_window", "tier",
                    "gate_a_literal", "model", "tier_reason", "unpriced_reason", "official_source",
                    "flags"])
        for f in fixtures:
            wp = f["winner_pick"] or {}
            w.writerow([f["key"], f["sport"], f["sport_name"], f["competition"], f.get("away") or "",
                        f.get("home") or "", f["date"], f.get("time_utc") or "", f.get("time_local") or "",
                        f.get("venue") or "", f.get("status") or "", "yes" if f["priced"] else "no",
                        wp.get("selection", ""), wp.get("probability", ""), wp.get("fair_decimal", ""),
                        wp.get("fair_american", ""),
                        "yes" if wp.get("in_brief_window") else ("no" if wp else ""),
                        wp.get("tier", ""), "yes" if wp.get("gate_a_literal") else ("no" if wp else ""),
                        wp.get("model", ""), wp.get("tier_reason", ""), f["unpriced_reason"] or "",
                        f["official_link"], ";".join(f["flags"])])

    with open(os.path.join(OUT_DIR, "markets.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_key", "sport", "market_id", "market", "family", "model", "outcome",
                    "probability", "fair_decimal", "fair_american", "in_brief_window",
                    "stronger_side", "inputs", "official_source"])
        for f in fixtures:
            for mk in f["markets"]:
                for o in mk["outcomes"]:
                    w.writerow([f["key"], f["sport"], mk["market_id"], mk["market"], mk["family"],
                                mk["model"], o["selection"], o["probability"], o["fair_decimal"],
                                o["fair_american"], "yes" if o["in_brief_window"] else "no",
                                "yes" if o["selection"] == mk["stronger_side"] else "no",
                                mk["inputs"], f["official_link"]])
    return desk


def main():
    fixtures = build_fixtures()
    dupes = mark_duplicates(fixtures)
    counts, per_sport = summarise(fixtures)
    write_desk(fixtures, counts, per_sport, dupes)
    import sd7d19a67_predictions as P
    problems, _ = P.check(json.load(open(os.path.join(OUT_DIR, "desk.json"), encoding="utf-8")))
    if problems:
        raise SystemExit("prediction checks failed:\n  " + "\n  ".join(problems))

    print("fixtures %d priced %d unpriced %d | markets %d outcomes %d"
          % (counts["fixtures"], counts["priced"], counts["unpriced"], counts["markets"],
             counts["outcomes"]))
    print("winner tiers High %d Medium %d Low %d | gateA winner %d gateA any selection %d | "
          "out-of-window strong %d | duplicate-line fixtures %d"
          % (counts["high"], counts["medium"], counts["low"], counts["gate_a_winner"],
             counts["gate_a_any_selection"], counts["out_of_window_strong"],
             counts["duplicate_line_fixtures"]))
    for s, v in sorted(per_sport.items()):
        print("  %-13s fixtures=%2d priced=%2d markets=%2d H=%d M=%d L=%d"
              % (s, v["fixtures"], v["priced"], v["markets"], v["high"], v["medium"], v["low"]))
    print("\nHigh winner picks:")
    for f in fixtures:
        wp = f["winner_pick"]
        if wp and wp["tier"] == "High":
            print("  %-16s %-52s p=%.4f %+d" % (f["key"], wp["selection"], wp["probability"],
                                                wp["fair_american"]))
    print("\nMedium / Low winner picks:")
    for f in fixtures:
        wp = f["winner_pick"]
        if wp and wp["tier"] != "High":
            print("  %-16s %-8s %-46s p=%.4f %+d" % (f["key"], wp["tier"], wp["selection"],
                                                     wp["probability"], wp["fair_american"]))
    print("\nSelections above 70%% and in-window (brief-literal Gate A), any market:")
    for f in fixtures:
        for mk in f["markets"]:
            for o in mk["outcomes"]:
                if o["probability"] > GATE_A_FLOOR and o["in_brief_window"]:
                    print("  %-16s %-34s %-24s p=%.4f %+d" % (f["key"], mk["market"][:34],
                                                              o["selection"][:24], o["probability"],
                                                              o["fair_american"]))
    print("\nDuplicate originated winner-line groups:")
    for sig, keys in dupes.items():
        print("  %-58s %s" % (sig[:58], ",".join(keys)))


if __name__ == "__main__":
    main()
