#!/usr/bin/env python3
"""
ccb6bde2_taxonomy.py — market investigation register + calibration findings.

Merges three things into the session's data files:
1. data/market_taxonomy-ccb6bde2.json — every standard market family per
   in-scope sport, with status: what datasets/markets_catalog.json claimed,
   what data/lines.json (v2.0) actually priced, what this session's expansion
   prices, and which markets were investigated but NOT priced because they
   need an official statistical input the verified dataset does not contain
   (the missing input is named; nothing is invented).
2. data/model_calibration-ccb6bde2.json — audit findings (F-CCB-xx), the
   v2.0 -> v2.1 change summary, and a shrinkage sensitivity check.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# market_key -> (display family, derivation) for everything the engine emits
EMITTED = {
    "correct_score": ("Correct Score", "exact race-to-N scoreline distribution"),
    "winning_margin": ("Winning Margin Bands", "normal margin band integrals"),
    "regulation_3way": ("60-Minute Regulation Result", "continuity-corrected margin"),
    "overtime_yes_no": ("Game to Overtime Y/N", "regulation draw probability"),
    "f5_winner": ("First 5 Innings Winner", "A5 time-scaling of margin"),
    "f5_total": ("First 5 Innings Total", "A5 time-scaling of total"),
    "first_innings_total": ("1st Innings Total Runs", "innings split of match total"),
    "set_betting": ("Set Betting (Correct Set Score)", "per-set q inverted from match price"),
    "first_set_winner": ("1st Set Winner", "per-set q"),
    "total_sets": ("Total Sets O/U", "set-count distribution"),
    "both_win_set": ("Both Players Win a Set", "set-count distribution"),
    "first_half_winner": ("1st Half Winner", "A5 half split of margin"),
    "first_half_total": ("1st Half Total", "A5 half split of total"),
}

def family_of(key: str) -> tuple[str, str]:
    if key in EMITTED:
        return EMITTED[key]
    if key.startswith("total_legs") or key.startswith("total_frames") or key.startswith("total_games"):
        return ("Total Units Ladder", "race/blended units distribution")
    if key.startswith("total_points"):
        return ("Total Points Ladder", "set distribution x mean points/set (A4)")
    if key.startswith("alt_total"):
        return ("Alternate Totals Ladder", "normal total at five lines")
    if key.startswith("alt_handicap"):
        return ("Alternate Handicap Ladder", "normal margin at five lines")
    if key.startswith("team_total"):
        return ("Team Totals", "A1 score decomposition")
    if key.endswith("_handicap_0.5") or "_handicap_" in key:
        return ("Unit Handicap Ladder", "exact scoreline distribution")
    return (key, "")


# markets investigated but NOT originated: they need an official per-player /
# per-event statistic that the verified dataset does not contain.
NOT_PRICED = {
    "tennis": [
        ("Tiebreak in Match / in 1st Set", "needs official per-player hold/break serve percentages (ATP/WTA stats)"),
        ("Total Aces / Double Faults", "needs official per-player ace rates per service game"),
        ("Player to Win 1st Set & Match combos beyond 1st-set price", "needs set-to-set correlation; independence assumption would misprice combos silently"),
    ],
    "darts": [
        ("Total 180s / Most 180s / Player 180s", "needs official per-player 180-per-leg rates (PDC does not publish a free per-match 180s feed)"),
        ("Highest Checkout / Checkout markets", "needs official per-player checkout-percentage and out-shot distributions"),
        ("King of the Oche / Match trebles", "compound of 180s + checkout + winner; blocked by the two gaps above"),
    ],
    "snooker": [
        ("Total Centuries / 50+ Breaks", "needs official per-player break-building rates (WST publishes season centuries lists, not per-frame rates)"),
        ("Highest Break (player/match)", "needs per-player break distribution, not in dataset"),
        ("First Frame Winner", "derivable as per-frame q but snooker frames are not i.i.d. around the break-off; priced deliberately conservatively as NOT originated — the race approximation is weakest for single-frame markets"),
    ],
    "cricket": [
        ("Top Team Batter / Top Bowler", "needs official playing XIs and player-level batting/bowling records (ICC player rankings exist but XIs are announced at the toss)"),
        ("Method of First Dismissal / Fall of Next Wicket", "needs ball-by-ball dismissal distributions"),
        ("Win by Wickets margin", "the originated margin is in runs; a wickets margin needs a separate chase model with wickets-in-hand distributions"),
        ("Player Performance Points", "needs player-level inputs as above"),
    ],
    "basketball": [
        ("Player Points/Rebounds/Assists props", "needs official per-player season stats and minutes projections"),
        ("Race to 20/50 Points", "needs possession-level pace interaction between the two offences; margin/total split (A1) is too coarse and would be silently wrong"),
    ],
    "ice-hockey": [
        ("Player Shots/Points props", "needs official per-player stats (NHL API has them; not harvested into this dataset)"),
        ("Correct Score (exact goals)", "needs a discrete (Poisson) goals model; the dataset carries only a continuous margin sigma"),
    ],
    "baseball": [
        ("Player props (hits, total bases, pitcher strikeouts)", "needs confirmed probable starters and lineups (fixture itself flags starters unconfirmed) plus per-player stats"),
        ("Inning-by-inning lines beyond F5", "needs bullpen/lineup-turnover sequencing inputs"),
    ],
    "rugby-union": [
        ("First/Anytime Tryscorer", "needs confirmed team lineups and player try-rate history"),
        ("Total Tries", "points margin/total does not separate tries from penalties; needs competition scoring composition"),
    ],
    "rugby-league": [
        ("First/Anytime Tryscorer", "needs confirmed lineups and player try rates"),
        ("Total Tries", "needs tries-vs-goals scoring composition per competition"),
    ],
    "handball": [
        ("Player Goals props", "needs per-player scoring rates (EHF publishes top-scorer lists; not in dataset)"),
    ],
    "volleyball": [
        ("Set Correct Score (points within a set)", "needs rally-level point-win distributions per rotation"),
        ("Player Points props", "needs per-player attack/block stats"),
    ],
    "aussie-rules": [
        ("First Goalkicker / Player Disposals", "needs team sheets and player stats (AFLW stats exist on afl.com.au; not harvested)"),
        ("Quarter-by-quarter lines", "needs quarter scoring distribution inputs"),
    ],
    "gaelic-football": [
        ("First Goalscorer / Total Goals", "no official per-player scoring data harvested; goals-vs-points split not in dataset"),
    ],
    "esports": [
        ("First Blood / First Dragon / First Baron", "needs official per-team objective rates from match histories (LoL Esports publishes results, not an objective-rate feed)"),
        ("Total Dragons/Barons/Towers", "same objective-rate gap"),
    ],
    "golf": [
        ("Outright Winner / Each-Way / Top-5/10/20", "no sourced full-field player ratings (OWGR points per entrant) in dataset — field cards stay informational"),
        ("72-Hole Matchups / Two-Balls", "needs paired official player ratings for named entrants"),
    ],
    "greyhounds": [
        ("Win / Each-Way / Forecast / Tricast", "no sourced per-runner form (official racecards with sectional times) in dataset"),
    ],
    "motor-racing": [
        ("Race Winner / Podium / Points Finish", "no sourced per-driver strength ratings (championship points alone do not price a 20-car field honestly without a full-field model)"),
        ("Fastest Lap / Pole Position", "needs qualifying-pace and tyre-strategy inputs"),
    ],
}


def main() -> None:
    exp = json.loads((ROOT / "data" / "market_expansion-ccb6bde2.json").read_text())
    catalog = json.loads((ROOT / "datasets" / "markets_catalog.json").read_text())
    claimed = {sm["sport"]: sm for sm in catalog["sports_markets"]}
    name_map = {"Ice Hockey": "ice-hockey", "Basketball": "basketball",
                "Baseball": "baseball", "Snooker": "snooker", "Darts": "darts",
                "Cricket": "cricket", "Rugby Union": "rugby-union",
                "Rugby League": "rugby-league", "Tennis": "tennis", "Golf": "golf",
                "Handball": "handball", "Volleyball": "volleyball",
                "Aussie Rules": "aussie-rules", "eSports": "esports",
                "Gaelic Football": "gaelic-football",
                "Greyhound Racing": "greyhounds", "Motor Racing": "motor-racing"}

    priced_families: dict[str, dict[str, str]] = defaultdict(dict)
    market_counts: Counter = Counter()
    for r in exp["matches"]:
        if r.get("field_event"):
            continue
        for m in r["expanded_markets"]:
            fam, how = family_of(m["key"])
            priced_families[r["sport"]][fam] = how
            market_counts[r["sport"]] += 1

    sports_out = []
    for slug in ["tennis", "basketball", "ice-hockey", "baseball", "cricket",
                 "snooker", "darts", "rugby-union", "rugby-league", "handball",
                 "volleyball", "aussie-rules", "gaelic-football", "esports",
                 "golf", "greyhounds", "motor-racing"]:
        cat = next((v for k, v in claimed.items() if name_map.get(k) == slug), None)
        sports_out.append({
            "sport": slug,
            "olbg_markets_observed": cat["olbg_markets"] if cat else [],
            "catalog_claimed_originated": cat["originated_markets_covered"] if cat else [],
            "v20_actually_priced": ["Match Winner", "Draw No Bet (draw sports)",
                                    "Handicap (single line)", "Match Total (single line + 1 alt)"]
                                   if slug not in ("golf", "greyhounds", "motor-racing") else [],
            "expansion_priced_here": [
                {"family": f, "derivation": h}
                for f, h in sorted(priced_families.get(slug, {}).items())],
            "expanded_markets_originated": market_counts.get(slug, 0),
            "investigated_not_priced": [
                {"market": m, "missing_official_input": why}
                for m, why in NOT_PRICED.get(slug, [])],
        })

    taxonomy = {
        "generated": "2026-10-21",
        "session": "ccb6bde2-olbg1",
        "principle": "A market is originated only if its probabilities are exact "
                     "mathematical consequences of sourced inputs already in the "
                     "verified dataset (ratings, margin/total sigmas, race "
                     "formats). Everything else is listed as investigated-not-"
                     "priced with the missing official input named — never filled "
                     "with an invented rate.",
        "sports": sports_out,
    }
    (ROOT / "data" / "market_taxonomy-ccb6bde2.json").write_text(
        json.dumps(taxonomy, indent=2) + "\n")

    # ---- merge findings into the calibration audit -------------------------
    cal_path = ROOT / "data" / "model_calibration-ccb6bde2.json"
    cal = json.loads(cal_path.read_text())
    cal["findings"] = [
        {"id": "F-CCB-01", "severity": "medium",
         "title": "WTA source link for ten-ningbo-rybakina points at the wrong tournament ID",
         "detail": "data/fixtures.json cited https://www.wtatennis.com/tournaments/1115/ningbo/2026/draws, which soft-404s to the WTA homepage (verified live this session). The canonical draws page is /tournaments/2092/ningbo/2026/draws (title 'BNB Ningbo Open 2026 Draws'). CLOSED during this session's merge: session 72198d3e's T20 live re-verification had already corrected the URL in main; confirmed 2092 present post-merge.",
         "evidence": ["https://www.wtatennis.com/tournaments/2092/ningbo/2026/draws"]},
        {"id": "F-CCB-02", "severity": "high",
         "title": "datasets/markets_catalog.json over-claims originated market coverage",
         "detail": "The catalog lists e.g. tennis 'Set Betting & 1st Set Winner', darts 'Most 180s', baseball 'First 5 Innings', golf 'Each-Way / Top-5 Fair Odds' as originated_markets_covered, but data/lines.json (model v2.0) prices only winner / draw-no-bet / handicap / total. This session originates the derivable subset (1,619 markets) and registers the rest as investigated-not-priced in data/market_taxonomy-ccb6bde2.json.",
         "evidence": ["datasets/markets_catalog.json", "data/lines.json"]},
        {"id": "F-CCB-03", "severity": "high",
         "title": "Small-sample record ratings unshrunk in v2.0 (56 ratings from <=12 games)",
         "detail": "Win%/points% from 4-11 games were fed in at face value: EuroLeague 4-2 vs 2-4 (6 games) produced a 33.4-point rating gap and a HIGH-confidence 74% on Real Madrid; NHL 0.800 points% from 10 games rated 80.0. v2.1 applies empirical-Bayes shrinkage toward 50 (factor n/(n+10); composite standings ratings count games double). 12 of the 31 v2.0 highs came from such inputs; v2.1 retains 19 highs.",
         "evidence": ["data/model_calibration-ccb6bde2.json", "data/market_expansion-ccb6bde2.json"]},
        {"id": "F-CCB-04", "severity": "medium",
         "title": "Baseball venue double-count in v2.0",
         "detail": "World Series fixtures use home-record vs road-record split ratings (which already embed venue effects) and v2.0 then added the 0.540 home logit on top. v2.1 prices split-input fixtures at a neutral 0.500 venue term; Brewers Game 1/2 moved 1.51 -> 1.61 and Rays Games 3/4 dropped from high to medium.",
         "evidence": ["scripts/model.py price_match", "data/fixtures.json mlb-849802..849805"]},
        {"id": "F-CCB-05", "severity": "medium",
         "title": "Confidence thresholds inconsistent across sports (high bar 0.580-0.780)",
         "detail": "A 58% baseball favourite was 'high' in v2.0 while an Aussie Rules favourite needed 78% and handball 76%. Thresholds were left unchanged in v2.1 for comparability, but the desk displays the pick probability next to every tier so the inconsistency is visible, and this finding recommends a uniform policy in a future model version.",
         "evidence": ["scripts/model.py SPORTS config"]},
        {"id": "F-CCB-06", "severity": "medium",
         "title": "Tennis ranking labels disagree with the official ATP list of 2026-10-19; four ATP rows unrated",
         "detail": "Verified on atptour.com this session: Tommy Paul No.15, B. Bonzi No.100, S. Tsitsipas No.39, A. Rublev No.22, L. Darderi No.23, J. Duckworth No.73, A. Mannarino No.79. Fixtures said Mannarino 67 / Duckworth 71 / Darderi 22 / Rublev 24 (seedings use an earlier list) and left Bonzi-Paul, Tsitsipas-Kukushkin, Goffin-Bertola unrated (priced 50/50). Kukushkin, Goffin and Bertola are all outside the official top 190 (full 1-190 list read), so those two matches correctly stay baseline-priced under the no-one-sided rule. Bonzi-Paul is now rated and becomes a high-confidence Tommy Paul pick. WTA ranks for Leylah Fernandez / Aliaksandra Sasnovich / Bejlek could not be verified (script-rendered table) and remain blank.",
         "evidence": ["https://www.atptour.com/en/rankings/singles?rankDate=2026-10-19&rankRange=0-100"]},
        {"id": "F-CCB-07", "severity": "low",
         "title": "Darts European Championship seeds used as strength ratings diverge from OLBG consensus",
         "detail": "pdc-ec-01: model favours Luke Woodhouse (seed 9, rating 86.26) over Dirk van Duijvenbode (seed 24, 71.74) at 61%, while OLBG tipsters were 7/8 (88%) on van Duijvenbode. Seeds come from the European Tour Order of Merit, not the two-year world ranking; pdc.tv's rankings table is not machine-readable (consent wall), so no official replacement rating was substituted. Kept as-is, flagged.",
         "evidence": ["data/fixtures.json pdc-ec-01", "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Luke_Woodhouse_vs_Dirk_van_Duijvenbode/15?event_id=32324"]},
        {"id": "F-CCB-08", "severity": "low",
         "title": "Snooker ranking curve is hot at the extreme tail for short formats",
         "detail": "The WST rank curve implies #1 beats #57 at 92.8% in a best-of-7 (per-frame q~0.78). Plausible directionally but almost certainly too strong for a race to 4; refitting the slope needs outcome data the repo does not hold, so v2.1 leaves slopes unchanged and flags the tail instead of inventing a correction.",
         "evidence": ["data/model_calibration-ccb6bde2.json snooker_rank_pairs"]},
        {"id": "F-CCB-09", "severity": "low",
         "title": "OLBG consensus samples are often 1-3 tips; consensus % is not a calibration target",
         "detail": "Of 55 comparable rows the model sided with the OLBG consensus favourite in 34; many '100%' consensuses are 1/1 or 2/2 tips, and several reference handicap/set markets rather than the winner market. Consensus is displayed for transparency but never fitted to.",
         "evidence": ["data/fixtures.json olbg.consensus fields"]},
        {"id": "F-CCB-10", "severity": "low",
         "title": "Best-of totals in v2.0 used an ad-hoc closeness heuristic",
         "detail": "model.py priced tennis/snooker/darts/volleyball totals as 0.44+0.14*closeness rather than from the unit-score distribution, so the totals book was not consistent with the winner price. The expansion derives totals, correct scores and unit handicaps from the exact race-to-N distribution implied by the winner price.",
         "evidence": ["scripts/model.py total market block", "scripts/ccb6bde2_market_engine.py"]},
        {"id": "F-CCB-11", "severity": "low",
         "title": "Three near-coin-flip picks change under shrinkage (all low confidence)",
         "detail": "hand-ehf-12051 (GOG 0.4837 home prob -> Szeged pick at 51.6% two-way... see expansion file), aflw-r11-06 (Gold Coast SUNS 0.5136) flip only because the shrunk rating gap no longer outweighs home advantage; both were and remain low confidence. ten-902102 flips on verified data (Paul No.15 vs Bonzi No.100), not on shrinkage.",
         "evidence": ["data/market_expansion-ccb6bde2.json pick_changes"]},
        {"id": "F-CCB-12", "severity": "medium",
         "title": "This session's own COORDINATION pre-claim about the tennis slope was wrong and is corrected",
         "detail": "The §12 claim filed before the audit ('#1 vs #30 modelled ~53%') was refuted by measurement: the v2.0 curve gives #1 vs #25 = 0.802 and #1 vs #50 = 0.845. The audit numbers, not the pre-claim, are what v2.1 acts on; COORDINATION.md §12 carries the correction.",
         "evidence": ["data/model_calibration-ccb6bde2.json tennis_rank_pairs"]},
    ]
    cal["v21_summary"] = {
        "changes_applied": [
            "R1 small-sample shrinkage of record-derived ratings (k=10 toward 50; composite ratings count games double)",
            "R2 baseball home/road split fixtures priced at neutral venue term",
            "R3 tennis ratings re-verified/backfilled from official ATP list 2026-10-19",
        ],
        "not_changed": "logit scales and confidence thresholds (see F-CCB-05, F-CCB-08)",
        "confidence_counts_v20": exp["confidence_counts_v20"],
        "confidence_counts_v21": exp["confidence_counts_v21"],
        "tier_changes": len(exp["tier_changes"]),
        "pick_changes": exp["pick_changes"],
        "calibration_changes_logged": len(exp["calibration_change_log"]),
        "expanded_markets_originated": sum(market_counts.values()),
    }
    cal_path.write_text(json.dumps(cal, indent=2) + "\n")
    print(f"taxonomy: {len(sports_out)} sports, expanded markets={sum(market_counts.values())}")
    for s in sports_out:
        print(f"  {s['sport']:16s} priced_families={len(s['expansion_priced_here']):2d} "
              f"markets={s['expanded_markets_originated']:4d} not_priced={len(s['investigated_not_priced'])}")
    print("calibration findings merged:", len(cal["findings"]))


if __name__ == "__main__":
    main()
