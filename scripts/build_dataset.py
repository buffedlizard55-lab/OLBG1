#!/usr/bin/env python3
"""
build_dataset.py - Reproducible governing-body compiler for all 17 in-scope OLBG sports.

Emits:
  - data/sources.json
  - data/coverage.json
  - data/fixtures.json
  - datasets/flagged_for_review.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from dataset_rows_a import get_rows_a
from dataset_rows_b import get_rows_b

DATE_ANCHOR = "2026-10-21"


def build_sources() -> dict:
    return {
        "retrieved": DATE_ANCHOR,
        "principle": (
            "Every match, venue, UTC start time, ranking, and record is verified directly "
            "against the official governing-body or tournament organiser feed. Where an "
            "official feed omits a field (such as a broadcast-TBD start time or opening-week "
            "table), the field is left explicitly null/blank and flagged rather than inferred."
        ),
        "sources": [
            {"id": "olbg", "sport": "all", "name": "OLBG Sports Betting Tips Sitemaps & Sport Hubs",
             "url": "https://www.olbg.com/sitemap-betting-tips.xml", "role": "Upstream taxonomy, event IDs, tip consensus, defect audit"},
            {"id": "nhl", "sport": "ice-hockey", "name": "NHL Official Web API (Schedule & Standings)",
             "url": "https://api-web.nhle.com/v1/schedule/2026-10-21", "role": "Fixtures, venues, UTC times, W-L-OT, points %, goal diff"},
            {"id": "nba", "sport": "basketball", "name": "NBA Official Schedule & Standings",
             "url": "https://www.nba.com/games?date=2026-10-21", "role": "2026-27 opening-week slate, arenas, prior-season baseline"},
            {"id": "euroleague", "sport": "basketball", "name": "EuroLeague & BKT EuroCup Official Feeds",
             "url": "https://www.euroleaguebasketball.net/en/euroleague/game-center/", "role": "Round 7 EuroLeague & Round 4 EuroCup fixtures and W-L standings"},
            {"id": "mlb", "sport": "baseball", "name": "MLB StatsAPI Official Postseason Schedule & Standings",
             "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-21&endDate=2026-10-28", "role": "2026 World Series Games 1-4, home/road & postseason records"},
            {"id": "atp", "sport": "tennis", "name": "ATP Tour Official Rankings & Draws (Vienna / Basel)",
             "url": "https://www.atptour.com/en/scores/current", "role": "ATP 500 draws, head-to-head match history, official PIF ATP rankings"},
            {"id": "wta", "sport": "tennis", "name": "WTA Tour Official Rankings & Draws (Ningbo / Guangzhou / Tokyo)",
             "url": "https://www.wtatennis.com/tournaments", "role": "WTA 500 & WTA 250 draws, official PIF WTA rankings"},
            {"id": "wst", "sport": "snooker", "name": "World Snooker Tour Official Rankings & BetVictor NI Open",
             "url": "https://www.wst.tv/rankings/", "role": "Official two-year world rankings (resolving tournament-seed confusion) & R2 draw"},
            {"id": "pdc", "sport": "darts", "name": "Professional Darts Corporation Machineseeker European Championship",
             "url": "https://www.pdc.tv/tournament/machineseeker-european-championship-1", "role": "All 16 Round 1 ties, European Tour seeds 1-32, Westfalenhalle sessions"},
            {"id": "icc-nzc", "sport": "cricket", "name": "ICC Official Rankings, New Zealand Cricket & Cricket Australia",
             "url": "https://scoring.nzc.nz/fixtures", "role": "Men's & Women's T20Is, ODI Tri-Series, NZ A v India A, Ford Trophy Round 1"},
            {"id": "top14-urc", "sport": "rugby-union", "name": "LNR Top 14, United Rugby Championship & Premiership Rugby",
             "url": "https://top14.lnr.fr/calendrier-et-resultats", "role": "Top 14 J7, URC R4, plus 5 cross-checked Gallagher Premiership fixtures"},
            {"id": "rlwc26", "sport": "rugby-league", "name": "NRL / 2026 Rugby League World Cup Official Draw & IRL Rankings",
             "url": "https://www.nrl.com/draw/?competition=175&round=2&season=2026", "role": "Men's & Women's RLWC26 Round 2 fixtures, venues, R1 scores"},
            {"id": "ehf", "sport": "handball", "name": "European Handball Federation EHF Champions League Men",
             "url": "https://ehfcl.eurohandball.com/men/2026-27/standings/", "role": "All 12 Round 5 group fixtures, group tables, goal difference, H2H scores"},
            {"id": "volley", "sport": "volleyball", "name": "PlusLiga Poland & Lega Pallavolo Serie A SuperLega",
             "url": "https://www.plusliga.pl/games.html", "role": "PlusLiga & Italian SuperLega regular-season fixtures, arenas, UTC times"},
            {"id": "aflw", "sport": "aussie-rules", "name": "Australian Football League Official 2026 NAB AFLW Ladder & Fixture",
             "url": "https://www.afl.com.au/aflw", "role": "All 9 Round 11 AFLW fixtures, Round 10 ladder points & W-L-D records"},
            {"id": "lolesports", "sport": "esports", "name": "Riot Games LoL Esports Worlds 2026 Official Schedule",
             "url": "https://lolesports.com/en-US/", "role": "2026 World Championship Swiss Round 1 draw & venue"},
            {"id": "gaa", "sport": "gaelic-football", "name": "Munster GAA, Cork GAA & Galway GAA Official Championships",
             "url": "https://munster.gaa.ie/fixtures/munster-gaa-fixtures/", "role": "4 County Senior Football Finals (proving OLBG Nov 1 date bug on ID 3536)"},
            {"id": "f1", "sport": "motor-racing", "name": "FIA Formula 1 Official 2026 United States Grand Prix",
             "url": "https://www.formula1.com/en/racing/2026/united-states", "role": "COTA Austin race timetable & 20:00 UTC lights out"},
            {"id": "golf-tours", "sport": "golf", "name": "PGA TOUR, DP World Tour & LPGA Official Schedules",
             "url": "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528", "role": "4 active stroke-play tour events (event-only multi-runner cards)"},
            {"id": "gbgb", "sport": "greyhounds", "name": "Greyhound Board of Great Britain Official Race Calendar",
             "url": "https://www.gbgb.org.uk/", "role": "UK licensed track cards proving OLBG 5h BST-to-EDT clock bug"},
        ],
    }


def build_coverage(fixtures: list[dict]) -> dict:
    by_sport = Counter(f["sport"] for f in fixtures)
    ver_by_sport = Counter(f["sport"] for f in fixtures if f["status"] == "verified")

    included_meta = [
        ("tennis", "Tennis", "https://www.olbg.com/betting-tips/Tennis/3", "priced",
         "ATP 500 Vienna & Basel plus WTA 500 Ningbo & WTA 250 Guangzhou/Tokyo verified with official ATP/WTA rankings."),
        ("basketball", "Basketball", "https://www.olbg.com/betting-tips/Basketball/4", "priced",
         "11 NBA opening-week games plus 4 EuroLeague Round 7 and 2 EuroCup Round 4 ties (including OLBG's misfiled EuroCup game 535918)."),
        ("golf", "Golf", "https://www.olbg.com/betting-tips/Golf/5", "event-only",
         "4 official tour events (PGA Bermuda, DPWT Genesis, LPGA BMW Ladies, Champions Stifel) logged as multi-runner field cards; two-ball pairings publish after round completion."),
        ("cricket", "Cricket", "https://www.olbg.com/betting-tips/Cricket/7", "priced",
         "NZ v India T20Is, Australia W v NZ W 3rd T20I, Afghanistan v Bangladesh ODI, NZ A v India A, and 3 Ford Trophy Round 1 games."),
        ("snooker", "Snooker", "https://www.olbg.com/betting-tips/Snooker/8", "priced",
         "11 BetVictor Northern Ireland Open last-32 matches priced strictly from official WST two-year world rankings (resolving tournament-seed numbering discrepancies)."),
        ("rugby-union", "Rugby Union", "https://www.olbg.com/betting-tips/Rugby_Union/9", "priced",
         "3 Top 14 Journée 7 matches, 4 URC Round 4 matches, and 5 cross-checked Gallagher Premiership Round 4 fixtures."),
        ("rugby-league", "Rugby League", "https://www.olbg.com/betting-tips/Rugby_League/10", "priced",
         "All 7 Men's & Women's 2026 Rugby League World Cup Round 2 fixtures (closing OLBG's complete RLWC26 live blind spot)."),
        ("baseball", "Baseball", "https://www.olbg.com/betting-tips/Baseball/12", "priced",
         "2026 MLB World Series Games 1-4 between Tampa Bay Rays and Milwaukee Brewers with park-adjusted home/road splits."),
        ("ice-hockey", "Ice Hockey", "https://www.olbg.com/betting-tips/Ice_Hockey/13", "priced",
         "6 NHL regular-season games verified directly from the official NHL web API."),
        ("motor-racing", "Motor Racing", "https://www.olbg.com/betting-tips/Motor_Racing/14", "event-only",
         "Formula 1 United States Grand Prix at COTA (20-car field race at 20:00 UTC; not a two-sided fixture)."),
        ("darts", "Darts", "https://www.olbg.com/betting-tips/Darts/15", "priced",
         "Complete 16-match Round 1 draw of the PDC Machineseeker European Championship in Dortmund."),
        ("handball", "Handball", "https://www.olbg.com/betting-tips/Handball/20", "priced",
         "All 12 Round 5 ties in the 2026/27 EHF Champions League Men group stage (flagging OLBG's stale 'Skanderborg Handbold' name on ID 12045)."),
        ("volleyball", "Volleyball", "https://www.olbg.com/betting-tips/Volleyball/21", "priced",
         "5 Polish PlusLiga matches plus 3 Italian SuperLega Credem Banca Round 2 fixtures."),
        ("aussie-rules", "Aussie Rules", "https://www.olbg.com/betting-tips/Aussie_Rules/22", "priced",
         "All 9 Round 11 matches of the 2026 NAB AFLW season with official Round 10 ladder inputs (closing OLBG's empty hub blind spot)."),
        ("esports", "eSports", "https://www.olbg.com/betting-tips/eSports/23", "priced",
         "LoL Esports 2026 World Championship Swiss Stage Round 1 matchup (closing OLBG's empty eSports hub blind spot)."),
        ("gaelic-football", "Gaelic Football", "https://www.olbg.com/betting-tips/Gaelic_Football/25", "priced",
         "4 County Senior Football Finals (Galway, Cork, Waterford, Kerry), explicitly flagged for borderline football-code scope review and OLBG's wrong Nov 1 date on ID 3536."),
        ("greyhounds", "Greyhounds", "https://www.olbg.com/betting-tips/Greyhounds/28", "event-only",
         "3 UK GBGB stadium cards (Kinsley, Monmore, Nottingham) kept event-only and documenting OLBG's 5-hour BST-to-EDT clock bug."),
    ]

    included = []
    for slug, name, url, status, note in included_meta:
        included.append({
            "sport": slug,
            "name": name,
            "olbg_url": url,
            "status": status,
            "fixtures": by_sport[slug],
            "verified": ver_by_sport[slug],
            "note": note,
        })

    excluded = [
        {"name": "Football / Soccer", "olbg_url": "https://www.olbg.com/betting-tips/Football/1", "reason": "Excluded per project specification ('football' / 'soccer')"},
        {"name": "Horse Racing", "olbg_url": "https://www.olbg.com/betting-tips/Horse_Racing/2", "reason": "Excluded per project specification ('horse racing')"},
        {"name": "American Football", "olbg_url": "https://www.olbg.com/betting-tips/American_Football/11", "reason": "Excluded per project specification ('american football')"},
        {"name": "Boxing", "olbg_url": "https://www.olbg.com/betting-tips/Boxing/16", "reason": "Excluded per project specification ('boxing')"},
        {"name": "UFC / MMA", "olbg_url": "https://www.olbg.com/betting-tips/UFC-MMA/17", "reason": "Excluded per project specification ('ufc', 'mma')"},
        {"name": "Entertainment / Specials", "olbg_url": "https://www.olbg.com/betting-tips/Entertainment/18", "reason": "Excluded per project specification ('specials'; ID 18 redirect to Entertainment)"},
        {"name": "Hurling", "olbg_url": "https://www.olbg.com/betting-tips/Hurling/26", "reason": "Excluded per project specification ('hurling'; active un-indexed OLBG ID 26)"},
        {"name": "Cycling", "olbg_url": "https://www.olbg.com/betting-tips", "reason": "Excluded per project specification ('cycling'; no active OLBG sport hub)"},
    ]

    return {
        "retrieved": DATE_ANCHOR,
        "olbg_sports_active": 24,
        "included_count": len(included),
        "excluded_count": len(excluded),
        "included": included,
        "excluded": excluded,
    }


def build_flagged_registry(fixtures: list[dict]) -> dict:
    upstream_bugs = [
        {
            "id": "BUG-OLBG-CLOCK-EDT",
            "category": "Upstream OLBG Defect",
            "severity": "high",
            "affected": "Greyhounds (ID 28), EuroLeague/NBA (ID 4), Snooker (ID 8), Tennis (ID 3), Handball (ID 20), Motor Racing (ID 14)",
            "summary": "OLBG server renders UTC-4 (US Eastern Daylight Time) strings across UK/European events without timezone labels.",
            "evidence": "Event 689388 is titled '11:14 Kinsley' (11:14 BST = 10:14 UTC) yet displays 'Today 06:14' right beside the title; event 534889 ('SAC Kings @ LA Clippers', 02:30 UTC Oct 22) displays 'Today 22:30' next to 'SAC Kings (2:30am)'.",
            "official_url": "https://www.olbg.com/betting-tips/Greyhounds/28",
            "resolution": "Every fixture in data/fixtures.json stores canonical ISO-8601 UTC verified against official governing-body feeds.",
        },
        {
            "id": "BUG-OLBG-3536-DATE",
            "category": "Upstream OLBG Defect",
            "severity": "high",
            "affected": "Gaelic Football — Rathgormack v The Nire (event_id=3536)",
            "summary": "OLBG schedules the Waterford Senior Football Final a full week late on '01 Nov 10:30'.",
            "evidence": "Official Munster GAA championship fixtures schedule Rathgormack v The Nire for Sunday 25 Oct 2026 at 14:30 GMT/UTC at Fraher Field, Dungarvan.",
            "official_url": "https://munster.gaa.ie/fixtures/munster-gaa-fixtures/",
            "resolution": "Corrected to 2026-10-25T14:30:00Z in data/fixtures.json and flagged on row gaa-waterford-3536.",
        },
        {
            "id": "BUG-OLBG-535918-EUROCUP",
            "category": "Upstream OLBG Defect",
            "severity": "medium",
            "affected": "Basketball — Hapoel Bank Yahav Jerusalem v Rigas Zelli (event_id=535918)",
            "summary": "OLBG lists BKT EuroCup/BCL club tie under 'EuroLeague' tournament header.",
            "evidence": "Official EuroLeague Basketball feeds confirm neither Hapoel Jerusalem nor Rigas Zelli is a 2026-27 EuroLeague club; the fixture belongs to European secondary competition.",
            "official_url": "https://www.euroleaguebasketball.net/en/eurocup/game-center/",
            "resolution": "Reclassified accurately under BKT EuroCup with a tailored 168.5-point European total line.",
        },
        {
            "id": "BUG-OLBG-534888-MARKET",
            "category": "Upstream OLBG Defect",
            "severity": "medium",
            "affected": "Basketball — Golden State Warriors @ Los Angeles Lakers (event_id=534888)",
            "summary": "OLBG hub summary card promotes 'Under 234.5' despite zero tips on that market on the event page.",
            "evidence": "Direct inspection of event_id=534888 confirms the consensus is 7/12 (58%) on LA Lakers Moneyline.",
            "official_url": "https://www.olbg.com/betting-tips/Basketball/NBA/NBA_Regular_Season/GS_Warriors_LA_Lakers/4?event_id=534888",
            "resolution": "Recorded true Moneyline consensus and flagged upstream cache desynchronisation.",
        },
        {
            "id": "BUG-OLBG-12045-NAME",
            "category": "Upstream OLBG Defect",
            "severity": "low",
            "affected": "Handball — CS Dinamo Bucuresti v SAH Aarhus (event_id=12045)",
            "summary": "OLBG displays deprecated Danish club name 'Skanderborg Handbold' instead of official EHF name 'SAH Aarhus'.",
            "evidence": "Official EHF 2026/27 Champions League group tables and Round 5 schedule list 'SAH - Skanderborg Aarhus / SAH Aarhus'.",
            "official_url": "https://ehfcl.eurohandball.com/men/2026-27/standings/",
            "resolution": "Recorded official EHF club name 'SAH Aarhus' and documented alias.",
        },
        {
            "id": "BUG-OLBG-EW-DIVZERO",
            "category": "Upstream OLBG Defect",
            "severity": "medium",
            "affected": "Golf (ID 5), Horse Racing (ID 2), Greyhounds (ID 28)",
            "summary": "Each-way tip consensus counter displays '0/0 EW tips ()' due to unpopulated denominator.",
            "evidence": "Observed live on PGA/DPWT tournament rows on /betting-tips/Golf/5.",
            "official_url": "https://www.olbg.com/betting-tips/Golf/5",
            "resolution": "Documented in reverse-engineering report; we originate independent clean probabilities.",
        },
        {
            "id": "BLINDSPOT-OLBG-ZERO-TIPS",
            "category": "Upstream OLBG Blind Spot",
            "severity": "medium",
            "affected": "Rugby League (ID 10), Aussie Rules (ID 22), eSports (ID 23)",
            "summary": "OLBG shows zero live match tips across 17 active top-flight fixtures (7 RLWC26 Round 2, 9 NAB AFLW Round 11, 1 LoL Worlds Swiss).",
            "evidence": "Verified live on nrl.com, afl.com.au, and lolesports.com on 2026-10-21.",
            "official_url": "https://www.nrl.com/draw/?competition=175&round=2&season=2026",
            "resolution": "All 17 missing fixtures captured directly from official governing bodies and fully priced.",
        },
        {
            "id": "AUDIT-SNOOKER-SEED-VS-RANK",
            "category": "Cross-Session Repo Audit",
            "severity": "medium",
            "affected": "Snooker — BetVictor Northern Ireland Open Last 32",
            "summary": "Parallel sessions mixed Belfast event seeding numbers (#1 Trump, #2 Wilson, #12 Pang, #14 Bingham, #23 Zhang) with official WST two-year world rankings (#6 Higgins, #8 Williams, #19 Bingham, #21 Zhang, #29 Pang).",
            "evidence": "Reconciled line by line against https://www.wst.tv/rankings/.",
            "official_url": "https://www.wst.tv/rankings/",
            "resolution": "Standardised strictly on official WST two-year world rankings across all 11 Snooker rows and barred bounded rank-60 estimates from High confidence.",
        },
        {
            "id": "SCOPE-GAELIC-FOOTBALL",
            "category": "Borderline Scope Flag",
            "severity": "low",
            "affected": "Gaelic Football (OLBG Sport ID 25 — 4 County Finals)",
            "summary": "Prompt excludes 'football', 'soccer', and 'american football'. Session aa4e9dbf excluded Gaelic Football; sessions 4f44f7d9, c5e985f4, and ebfbd966 included it.",
            "evidence": "OLBG maintains distinct sport IDs for Football/Soccer (ID 1), American Football (ID 11), Aussie Rules (ID 22), and Gaelic Football (ID 25).",
            "official_url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
            "resolution": "Included all 4 official GAA County Finals with explicit borderline-scope tags so nothing is silently omitted.",
        },
    ]

    row_flags = []
    for f in fixtures:
        if f.get("flags") or f.get("status") != "verified" or f.get("start_utc") is None:
            row_flags.append({
                "match_id": f["id"],
                "sport": f["sport"],
                "competition": f["competition"],
                "match": f"{f['home']} vs {f['away']}" if f.get("away") else f["home"],
                "status": f["status"],
                "missing_utc": f.get("start_utc") is None,
                "unrated_sides": 2 - len(f.get("inputs", {})),
                "flags": f.get("flags", []),
                "official_url": f["sources"][0]["url"],
            })

    return {
        "generated": DATE_ANCHOR,
        "summary": {
            "upstream_and_audit_findings": len(upstream_bugs),
            "flagged_fixture_rows": len(row_flags),
            "cross_checked_rows": sum(1 for f in fixtures if f["status"] != "verified"),
            "missing_utc_rows": sum(1 for f in fixtures if f.get("start_utc") is None),
        },
        "findings": upstream_bugs,
        "rows": row_flags,
    }


def main() -> None:
    rows = get_rows_a() + get_rows_b()
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "Duplicate match IDs in dataset"

    sources_doc = build_sources()
    coverage_doc = build_coverage(rows)
    fixtures_doc = {
        "retrieved": DATE_ANCHOR,
        "window": "2026-10-21 to 2026-10-28",
        "count": len(rows),
        "h2h_count": sum(1 for r in rows if r.get("away")),
        "event_only_count": sum(1 for r in rows if not r.get("away")),
        "matches": rows,
        "fixtures": rows,
    }
    flagged_doc = build_flagged_registry(rows)

    (ROOT / "data" / "sources.json").write_text(json.dumps(sources_doc, indent=2) + "\n")
    (ROOT / "data" / "coverage.json").write_text(json.dumps(coverage_doc, indent=2) + "\n")
    (ROOT / "data" / "fixtures.json").write_text(json.dumps(fixtures_doc, indent=2) + "\n")
    (ROOT / "datasets").mkdir(exist_ok=True)
    (ROOT / "datasets" / "flagged_for_review.json").write_text(json.dumps(flagged_doc, indent=2) + "\n")

    print(
        f"Built dataset: {len(rows)} rows across {len(coverage_doc['included'])} in-scope sports "
        f"({fixtures_doc['h2h_count']} H2H + {fixtures_doc['event_only_count']} multi-runner events)."
    )


if __name__ == "__main__":
    main()
