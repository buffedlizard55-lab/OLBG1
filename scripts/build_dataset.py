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
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from dataset_rows_a import get_rows_a
from dataset_rows_b import get_rows_b

DATE_ANCHOR = "2026-10-21"

CONSENSUS_RE = re.compile(r"^\d+/\d+ win tips \(\d+%\)$")
LIVE_SNAPSHOT = ROOT / "data" / "live_snapshot.json"


def apply_live_consensus(rows: list[dict]) -> dict:
    """Overlay the live OLBG tip-consensus capture onto matching dataset rows.

    Only OLBG's own upstream tip counters are replaced; every sporting fact (kick-off
    time, venue, records, ratings) still comes from the governing-body sources recorded
    on the row.  The previous value is retained in ``consensus_prior`` so the change is
    auditable.  Rows whose captured consensus is not in OLBG's own ``x/y win tips (z%)``
    format are left untouched rather than being partially written.
    """
    if not LIVE_SNAPSHOT.exists():
        return {"applied": 0, "skipped": 0}
    snap = json.loads(LIVE_SNAPSHOT.read_text())
    live = {int(ev["event_id"]): ev for ev in snap["events"]}
    applied = skipped = 0
    for row in rows:
        olbg = row.get("olbg") or {}
        ev = live.get(int(olbg.get("event_id") or 0))
        if not ev or not CONSENSUS_RE.match(ev.get("consensus", "")):
            skipped += 1
            continue
        if olbg.get("consensus") != ev["consensus"]:
            olbg["consensus_prior"] = olbg.get("consensus")
            olbg["consensus"] = ev["consensus"]
        if olbg.get("selection") != ev["selection"]:
            olbg["selection_prior"] = olbg.get("selection")
        olbg["selection"] = ev["selection"]
        if ev.get("market"):
            olbg["market"] = ev["market"]
        olbg["captured_utc"] = snap["fetched_utc"]
        applied += 1
    return {"applied": applied, "skipped": skipped, "captured_utc": snap["fetched_utc"]}


def live_refresh_findings() -> list[dict]:
    """Public disclosure of what the live re-capture did and did not confirm."""
    diff_path = ROOT / "data" / "live_diff.json"
    if not diff_path.exists():
        return []
    d = json.loads(diff_path.read_text())
    s = d["summary"]
    flips = [c for c in d["changed"] if c["selection_flipped"]]
    examples = "; ".join(
        f"{c['title']} ({c['was']['selection']} -> {c['now']['selection']})" for c in flips[:4]
    )
    return [
        {
            "id": "F-LIVE-01-DRIFT",
            "category": "Live Recapture",
            "severity": "medium",
            "affected": f"{s['consensus_or_selection_changed']} of {s['matched']} dataset rows matched to a live OLBG card",
            "summary": (
                f"OLBG tip consensus and/or most-tipped selection moved between the committed "
                f"capture and the {d['captured_utc']} recapture."
            ),
            "evidence": (
                f"{s['selection_flipped']} cards changed the selection OLBG highlights, e.g. {examples}, "
                f"and {s['consensus_or_selection_changed'] - s['selection_flipped']} kept the same selection "
                f"with a different tip count/share. Consensus is an upstream opinion counter, not a "
                f"verified sporting fact, so this changes no fixture, price or confidence tier."
            ),
            "official_url": "https://www.olbg.com/betting-tips",
            "resolution": (
                "Every matched row carries the recaptured consensus plus "
                "olbg.captured_utc and the superseded value in olbg.consensus_prior; the full "
                "before/after list is published on the Live Refresh page and in data/live_diff.json."
            ),
        },
        {
            "id": "F-LIVE-02-NO-OFFICIAL",
            "category": "Verification Boundary",
            "severity": "high",
            "affected": f"{s['new_not_in_dataset']} live OLBG cards not present in the verified dataset",
            "summary": (
                "These events are listed because OLBG publishes them, but none of their kick-off times, "
                "participant records or ratings have been confirmed against a governing body in this pass."
            ),
            "evidence": (
                f"The {d['captured_utc']} capture returned {s['live_events_captured']} cards across "
                f"{s['sports_with_live_events']} sports; {s['matched']} join to an existing source-verified row "
                f"by OLBG event_id and {s['new_not_in_dataset']} do not. No price, winner pick or confidence tier "
                "is originated for an unjoined card."
            ),
            "official_url": "https://www.olbg.com/betting-tips",
            "resolution": (
                "Published as upstream-only rows on the Live Refresh page with every sporting field left blank "
                "and marked Unverified; they are excluded from data/fixtures.json, data/lines.json and the "
                "134-event verified count until an official source confirms each one."
            ),
        },
        {
            "id": "F-LIVE-03-TRUNCATION",
            "category": "Upstream OLBG Defect",
            "severity": "medium",
            "affected": f"{s['dataset_rows_absent_from_capture']} dataset rows with an OLBG event_id",
            "summary": (
                "Dataset rows whose OLBG event page exists were not visible on the recaptured hub first screen."
            ),
            "evidence": (
                "OLBG hubs render roughly 20 cards before a 'Load More Tips' control, so absence from the "
                "first screen is not evidence that OLBG has delisted or completed the event. Examples include "
                "basketball 535918/535921/535923 and darts 32331/32336, all still future-dated in the dataset."
            ),
            "official_url": "https://www.olbg.com/betting-tips/Basketball/4",
            "resolution": (
                "Recorded as 'not in capture' rather than deleted or expired; the rows stay in the dataset with "
                "their governing-body kick-off times and are listed with this caveat in data/live_diff.json."
            ),
        },
        {
            "id": "F-LIVE-04-EMPTY-HUBS",
            "category": "Upstream OLBG Coverage",
            "severity": "medium",
            "affected": "Aussie Rules (ID 22), eSports (ID 23), Rugby League (ID 10)",
            "summary": (
                "Two in-scope hubs returned 'No tips found', and the Rugby League hub returned only 2027 outright "
                "markets while the desk still carries 9 AFLW fixtures, 1 LoL Worlds tie and 7 RLWC26 fixtures."
            ),
            "evidence": (
                "Fetched hubs for Aussie_Rules/22 and eSports/23 returned 'No tips found' at the capture time; "
                "Rugby_League/10 listed State of Origin 2027, Super League 2027 and NRL 2027 outrights only. "
                "Absence of OLBG tips does not invalidate the governing-body fixtures, but it does mean OLBG "
                "consensus cannot be refreshed for those sports."
            ),
            "official_url": "https://www.olbg.com/betting-tips/Rugby_League/10",
            "resolution": (
                "Consensus for those three sports is retained from the earlier capture and labelled with its "
                "capture timestamp; the gap is published rather than back-filled."
            ),
        },
        {
            "id": "F-LIVE-06-MLB-CLOCK",
            "category": "Upstream OLBG Defect",
            "severity": "medium",
            "affected": "Baseball - TB Rays @ MIL Brewers (event_id=160789)",
            "summary": (
                "OLBG's baseball hub card shows '24 Oct 01:00' for a game the official MLB StatsAPI schedules "
                "for 2026-10-25T00:00:00Z."
            ),
            "evidence": (
                "Verified against the official MLB StatsAPI schedule for 2026-10-24, which returns gamePk 849802, "
                "'World Series Game 2', Tampa Bay Rays at Milwaukee Brewers, American Family Field, "
                "gameDate 2026-10-25T00:00:00Z. Even reading OLBG's clock as UTC-4, its label maps to "
                "2026-10-24T05:00:00Z - roughly 19 hours before the official first pitch."
            ),
            "official_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24",
            "resolution": (
                "The desk keeps the official MLB time on mlb-849802 and treats the OLBG label as a display defect; "
                "the OLBG link is retained only as the upstream discovery reference."
            ),
        },
        {
            "id": "F-LIVE-05-ZERO-TIPS",
            "category": "Upstream OLBG Defect",
            "severity": "low",
            "affected": "Golf - Hero Womens Indian Open (event_id=101909)",
            "summary": "The each-way outright card still renders an empty tip count / 0% share on the hub.",
            "evidence": (
                "The card shows 'Avani Prashanth' with no tip counter, matching the previously documented 0/0 "
                "division display defect on each-way-only outright markets."
            ),
            "official_url": "https://www.olbg.com/betting-tips/Golf/5",
            "resolution": "Consensus is recorded as unavailable for this card; no share is inferred.",
        },
    ]



def build_sources() -> dict:
    return {
        "retrieved": DATE_ANCHOR,
        "principle": (
            "Every match row carries an official governing-body or tournament-organiser source; "
            "its status remains verified or cross-checked as recorded. Where an "
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
            "resolution": "Every fixture in data/fixtures.json stores a canonical ISO-8601 UTC value linked to a governing-body source; any unconfirmed UTC is left blank and flagged.",
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
            "official_url": "https://www.nrl.com/draw/?competition=131&round=2&season=2026",
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
        {
            "id": "AUDIT-PREDICTION-PROSE-REMEDIATED",
            "category": "Provenance Correction",
            "severity": "medium",
            "affected": "31 High-confidence generated predictions",
            "summary": "An independent post-integration audit found tactical prose that was not represented in the stored source facts arrays.",
            "evidence": "The review page records the historical issue and examples; the generated text is now limited to each fixture's two stored, source-linked input values plus the explicitly labelled model selection.",
            "official_url": "https://api-web.nhle.com/v1/standings/2026-10-20",
            "resolution": "Re-authored all 31 predictions from the versioned official-input fields; unsupported tactical, injury, lineup and performance claims were removed. The source freshness boundary remains separately flagged.",
        },
        {
            "id": "AUDIT-STATUS-SPLIT",
            "category": "Verification Status",
            "severity": "medium",
            "affected": "Primary snapshot: 134 source-linked events",
            "summary": "The fixture data contains 129 Verified rows and 5 Cross-checked Gallagher Premiership rows; public summary wording must preserve that split.",
            "evidence": "Premiership fixture rendering was client-side during the stored verification work, so those five rows were deliberately not promoted to Verified.",
            "official_url": "https://www.premrugby.com/fixtures-results",
            "resolution": "Dashboard, README and audit manifest now use '134 source-linked events (129 Verified; 5 Cross-checked)' instead of flattening all rows to Verified.",
        },
        {
            "id": "AUDIT-SOURCE-FRESHNESS",
            "category": "Review Boundary",
            "severity": "medium",
            "affected": "All primary fixture source links",
            "summary": "The final integration gate validates recorded URL authority, data structure and static output; it does not make live network requests during validation.",
            "evidence": "A valid recorded source link is auditable provenance, not a guarantee that a remote publisher has not later changed its content.",
            "official_url": "https://api-web.nhle.com/v1/schedule/2026-10-21",
            "resolution": "The exact per-row source URLs are published in the Final Integration Audit. Any later discrepancy must remain blank/flagged until a governing-body source is re-opened and compared.",
        },
        {
            "id": "LIVE-F-V1-SNK-LINKS",
            "category": "Live Re-Verification Correction",
            "severity": "high",
            "affected": "Snooker — 5 of 11 Northern Ireland Open Round 2 rows",
            "summary": "Three rows cited WST match-centre UUIDs that bind to no match, and two rows cited only the generic site even though WST publishes a match centre for both ties.",
            "evidence": "Re-fetching 5b3a7f22-1c41-48e8-8a2c-94b28a21b9d1 returns an unbound template with no players. The WST live listing binds Holt-Brown to e58a00e5, Gao-Gilbert to 4fb27af0, Noppon-Donaldson to 3a24076e, Brecel-O'Donnell to 0c49ba0c and Slessor-Jones to f6536f1f.",
            "official_url": "https://www.wst.tv/",
            "resolution": "All eleven rows now cite the match centre WST actually binds to the pairing.",
        },
        {
            "id": "LIVE-F-V2-WTA-ID",
            "category": "Live Re-Verification Correction",
            "severity": "medium",
            "affected": "Tennis — 6 WTA 500 Ningbo Open rows",
            "summary": "The rows cited tournament 1115 for Ningbo; WTA's own site links the BNB Ningbo Open draws at tournament 2092.",
            "evidence": "The wta.com notification panel links https://www.wtatennis.com/tournaments/2092/ningbo/2026/draws for both the singles and doubles draw releases.",
            "official_url": "https://www.wtatennis.com/tournaments/2092/ningbo/2026/draws",
            "resolution": "Citation corrected to 2092. The draw body is client-rendered, so the pairings could not be re-read and those rows are listed as not re-checked.",
        },
        {
            "id": "LIVE-F-V3-CRIC-VENUE",
            "category": "Live Re-Verification Correction",
            "severity": "high",
            "affected": "Cricket — cric-ausw-nzw-t20-3, cric-nza-inda-fc1, cric-ford-cds-nd",
            "summary": "Three NZC fixtures carried a venue or date that the official service does not publish.",
            "evidence": "scoring.nzc.nz/fixtures lists the 3rd Women's T20I at North Sydney Oval, New Zealand A v India A on 23 Oct at Bert Sutcliffe Oval (Lincoln University), and Central Stags v Northern Districts at Saxton Oval, Nelson.",
            "official_url": "https://scoring.nzc.nz/fixtures",
            "resolution": "All three corrected in the dataset source from the re-fetched official service and flagged on their rows.",
        },
        {
            "id": "LIVE-F-V4-BOS-SPLIT",
            "category": "Live Re-Verification Correction",
            "severity": "medium",
            "affected": "Ice hockey — nhl-2026020154 Boston Bruins v Nashville Predators",
            "summary": "The row claimed a 5-1-0 home record; the official standings return four home games at 3-1-0 for the same 7-2-1 record.",
            "evidence": "api-web.nhle.com/v1/standings/2026-10-20: homeGamesPlayed 4, homeWins 3, homeLosses 1, homeOtLosses 0, while overall 7-2-1, pointPctg .750 and goalDifferential +14 already matched the row.",
            "official_url": "https://api-web.nhle.com/v1/standings/2026-10-20",
            "resolution": "Descriptive split corrected to 3-1-0. Because points percentage and goal differential drove the rating, no price moved.",
        },
        {
            "id": "LIVE-F-V5-NHL-DRIFT",
            "category": "Snapshot Drift Disclosure",
            "severity": "medium",
            "affected": "Ice hockey — nhl-2026020160 St. Louis Blues v Vegas Golden Knights",
            "summary": "Vegas was priced at 8-2-0 (.800, W3); the same live endpoint now returns 8-3-0 (.727, L1) over 11 games played.",
            "evidence": "The standings endpoint reports standingsDateTimeUtc 2026-10-21T07:05:30Z, i.e. it is a live table, so any club that plays after a snapshot will drift the same way.",
            "official_url": "https://api-web.nhle.com/v1/standings/2026-10-20",
            "resolution": "Deliberately not re-priced: the published line is a labelled pre-game snapshot and rewriting a pick after the fact would be worse than disclosing it. Row flag records both values.",
        },
        {
            "id": "LIVE-F-V6-PDC-WALL",
            "category": "Source Access Limit",
            "severity": "medium",
            "affected": "Darts — all 16 Machineseeker European Championship rows",
            "summary": "The official PDC draw release still returns only a cookie-consent interstitial to a text fetch.",
            "evidence": "Two fetches on 2026-10-21 (start of document and mid-document) returned Consent Management Platform text with no draw content.",
            "official_url": "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed",
            "resolution": "The 16 darts rows are marked not re-checked on the Live Verification page instead of being implied verified.",
        },
        {
            "id": "LIVE-F-V7-WTA-ATP-JS",
            "category": "Source Access Limit",
            "severity": "medium",
            "affected": "Tennis — all 11 ATP/WTA rows",
            "summary": "WTA and ATP draw pages are client-rendered and return a notification shell without draw content to a text fetch.",
            "evidence": "Re-fetching /tournaments/2092/ningbo/2026/draws returned the site's notification panel only, with no draw body.",
            "official_url": "https://www.wtatennis.com/tournaments/2092/ningbo/2026/draws",
            "resolution": "The tennis rows keep their source links but are published as not re-checked in this pass.",
        },
        {
            "id": "LIVE-F-V8-WST-CLOCK",
            "category": "Rendering Limit",
            "severity": "low",
            "affected": "Snooker — all 11 rows (session start)",
            "summary": "WST publishes no UTC session time and renders the clock in the viewer's timezone, so a scraped clock cannot be a fixture start time.",
            "evidence": "The fetch client renders publisher clocks at UTC-4: all five RLWC kick-offs displayed on nrl.com map exactly to the published UTC values under that offset, and the WST listing showed 05:00/08:00/09:00/14:00/15:00 for a Belfast afternoon and evening card.",
            "official_url": "https://www.wst.tv/",
            "resolution": "start_utc stays blank on all eleven rows. The flag now explains the rendering rather than asserting a local session time.",
        },
        {
            "id": "LIVE-F-V9-NRL-ID",
            "category": "Live Re-Verification Correction",
            "severity": "low",
            "affected": "Rugby league — 5 men's RLWC26 rows and the zero-tips blind-spot finding",
            "summary": "The men's World Cup rows cited nrl.com competition 175; the site serves the same Round 2 draw as competition 131.",
            "evidence": "Requesting ?competition=175&round=2&season=2026 returns the draw page with canonical competition=131 and the full five-match Round 2 list.",
            "official_url": "https://www.nrl.com/draw/?competition=131&round=2&season=2026",
            "resolution": "Men's citation corrected to 131. The women's id 176 was re-tested later on 2026-10-21 and also canonicalises to 131, so the two women's rows are flagged under LIVE-F-V12-NRL-WOMEN-ID.",
        },
        {
            "id": "LIVE-F-V10-COVERAGE",
            "category": "Review Boundary",
            "severity": "medium",
            "affected": "134 primary rows",
            "summary": "Two passes re-fetched official pages for 71 rows (55 confirmed, 10 corrected, 6 flagged). The other 63 were not re-read and are listed individually as not re-checked with the blocker for each sport.",
            "evidence": "Counts come from data/verification.json, which is generated by scripts/live_verification.py and contains one row per fixture.",
            "official_url": "https://api-web.nhle.com/v1/schedule/2026-10-21",
            "resolution": "The gap is published row by row on the Live Verification page; no row is claimed as re-verified without a recorded read.",
        },
        {
            "id": "LIVE-F-V12-NRL-WOMEN-ID",
            "category": "Live Re-Verification Correction",
            "severity": "medium",
            "affected": "Rugby league — 2 women's RLWC26 rows",
            "summary": "The women's World Cup rows cite nrl.com/draw/?competition=176, but that request canonicalises to competition=131 and returns the five men's Round 2 matches.",
            "evidence": "Re-tested on 2026-10-21: the fetched page's canonical URL is ?competition=131&round=2&season=2026 and its body lists Tonga v Lebanon, Papua New Guinea v Samoa, England v France, New Zealand v Cook Islands and Australia v Fiji. No women's fixture appears.",
            "official_url": "https://www.nrl.com/draw/?competition=176&round=2&season=2026",
            "resolution": "Both women's rows are flagged for a human to supply a working women's competition citation. Fixture facts are unchanged rather than guessed.",
        },
        {
            "id": "LIVE-F-V13-PREMIERSHIP-UNREADABLE",
            "category": "Review Boundary",
            "severity": "low",
            "affected": "Rugby union — 5 Gallagher Premiership rows",
            "summary": "A second fetch of the Premiership fixtures page returned page chrome only, with no fixture rows, so the five Premiership rows stay cross-checked rather than verified.",
            "evidence": "premrugby.com/fixtures-results returned navigation, sponsor blocks and footer; the fixture list is rendered client-side.",
            "official_url": "https://www.premrugby.com/fixtures-results",
            "resolution": "Cross-checked status retained and the reason published; no row was promoted on the strength of an unread page.",
        },
        {
            "id": "LIVE-F-V14-URC-VENUE-TBC",
            "category": "Live Re-Verification Correction",
            "severity": "low",
            "affected": "Rugby union — Leinster v Munster (ru-urc-609578)",
            "summary": "The row asserted Aviva Stadium, Dublin; the official URC 2026/27 fixtures release publishes the Round 4 venue as 'TBC, Dublin'.",
            "evidence": "Round 4 entry: 'Leinster v Munster — TBC, Dublin, KO 18.00 IRE & UK / 19.00 ITA & SA'. Participants, date and kick-off match the row; the venue does not.",
            "official_url": "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/",
            "resolution": "Venue replaced with 'Dublin (venue TBC)' in the dataset source and the row carries a flag until the URC confirms a ground.",
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

    live = apply_live_consensus(rows)

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
    flagged_doc["findings"].extend(live_refresh_findings())
    flagged_doc["summary"]["upstream_and_audit_findings"] = len(flagged_doc["findings"])

    (ROOT / "data" / "sources.json").write_text(json.dumps(sources_doc, indent=2) + "\n")
    (ROOT / "data" / "coverage.json").write_text(json.dumps(coverage_doc, indent=2) + "\n")
    (ROOT / "data" / "fixtures.json").write_text(json.dumps(fixtures_doc, indent=2) + "\n")
    (ROOT / "datasets").mkdir(exist_ok=True)
    (ROOT / "datasets" / "flagged_for_review.json").write_text(json.dumps(flagged_doc, indent=2) + "\n")

    print(
        f"Live consensus overlay: {live.get('applied', 0)} rows refreshed from {live.get('captured_utc', '-')}; "
        f"{len(flagged_doc['findings'])} published findings."
    )
    print(
        f"Built dataset: {len(rows)} rows across {len(coverage_doc['included'])} in-scope sports "
        f"({fixtures_doc['h2h_count']} H2H + {fixtures_doc['event_only_count']} multi-runner events)."
    )


if __name__ == "__main__":
    main()
