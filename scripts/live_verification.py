#!/usr/bin/env python3
"""live_verification.py — register of the fresh official-source re-verification pass.

Every earlier session in this repository audited the *structure* of the dataset and
said so explicitly: none of them re-fetched the governing-body pages. Session
``72198d3e-olbg1`` does exactly that, row by row, and records the outcome here so the
result is reproducible and reviewable rather than a claim in prose.

Status vocabulary (mutually exclusive, one per fixture row):

``confirmed``      an official page was re-fetched and the row's fixture facts
                   (participants, date, venue, and where published, start time and
                   identifier) were read back and matched.
``corrected``      an official page was re-fetched, it disagreed with the row, the
                   value could be established unambiguously from that page, and the
                   dataset source was amended to match.
``flagged``        an official page was re-fetched and it disagrees or cannot settle
                   the row. Nothing is changed; the discrepancy is published on the
                   Flagged for Review page for a human decision.
``not_rechecked``  no official page was re-fetched for this row in this pass. The row
                   keeps its original status and source links; the reason is printed
                   so the gap is visible instead of implied.

This module performs no network I/O: it records the reads that were made by hand and
the exact URLs they came from. It is the single source for ``data/verification.json``
and ``reports/LIVE_VERIFICATION.md``.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKED_AT = "2026-10-21T07:05Z"

# ---------------------------------------------------------------------------
# Sources actually re-fetched during this pass
# ---------------------------------------------------------------------------
SOURCES: dict[str, dict[str, str]] = {
    "nhl_sched": {
        "name": "NHL official schedule API (2026-10-21)",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-21",
    },
    "nhl_stand": {
        "name": "NHL official standings API (2026-10-20, live)",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-20",
    },
    "mlb_sched": {
        "name": "MLB StatsAPI official schedule (2026-10-20..30)",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-20&endDate=2026-10-30&hydrate=venue(location)",
    },
    "mlb_stand": {
        "name": "MLB StatsAPI official 2026 standings (AL + NL)",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&hydrate=team",
    },
    "nba": {
        "name": "NBA official games page (2026-10-21)",
        "url": "https://www.nba.com/games?date=2026-10-21",
    },
    "wst": {
        "name": "World Snooker Tour live & upcoming match listing",
        "url": "https://www.wst.tv/",
    },
    "ehf": {
        "name": "EHF Champions League Men 2026/27 standings & match calendar",
        "url": "https://ehfcl.eurohandball.com/men/2026-27/standings/",
    },
    "nrl": {
        "name": "NRL / Rugby League World Cup 2026 Round 2 draw",
        "url": "https://www.nrl.com/draw/?competition=131&round=2&season=2026",
    },
    "nzc": {
        "name": "New Zealand Cricket official fixtures & results service",
        "url": "https://scoring.nzc.nz/fixtures",
    },
    "aflw": {
        "name": "AFL official AFLW hub — Round 11 fixture board",
        "url": "https://www.afl.com.au/aflw",
    },
    "pdc": {
        "name": "PDC official 2026 Machineseeker European Championship draw release",
        "url": "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed",
    },
    "wta": {
        "name": "WTA official BNB Ningbo Open 2026 draws",
        "url": "https://www.wtatennis.com/tournaments/2092/ningbo/2026/draws",
    },
    "prem": {
        "name": "Premiership Rugby official fixtures & results",
        "url": "https://www.premrugby.com/fixtures-results",
    },
}

# ---------------------------------------------------------------------------
# Rows confirmed against a re-fetched official page
# ---------------------------------------------------------------------------
CONFIRMED: dict[str, dict[str, str]] = {
    # --- NHL ---------------------------------------------------------------
    "nhl-2026020152": {"src": "nhl_sched", "evidence": "Game 2026020152: Philadelphia at Buffalo, KeyBank Center, startTimeUTC 2026-10-21T23:30:00Z — participants, venue and start all match."},
    "nhl-2026020153": {"src": "nhl_sched", "evidence": "Game 2026020153: Florida at Ottawa, Canadian Tire Centre, startTimeUTC 2026-10-21T23:30:00Z — all match."},
    "nhl-2026020154": {"src": "nhl_sched", "evidence": "Game 2026020154: Nashville at Boston, TD Garden, startTimeUTC 2026-10-22T23:00:00Z — all match."},
    "nhl-2026020155": {"src": "nhl_sched", "evidence": "Game 2026020155: New York Rangers at Toronto, Scotiabank Arena, startTimeUTC 2026-10-22T23:00:00Z — all match."},
    # --- MLB ---------------------------------------------------------------
    "mlb-849805": {"src": "mlb_sched", "evidence": "gamePk 849805, World Series Game 1, officialDate 2026-10-23, first pitch 2026-10-24T00:00Z, American Family Field, Rays at Brewers — all match."},
    "mlb-849802": {"src": "mlb_sched", "evidence": "gamePk 849802, World Series Game 2, officialDate 2026-10-24, 2026-10-25T00:00Z, American Family Field — all match."},
    "mlb-849804": {"src": "mlb_sched", "evidence": "gamePk 849804, World Series Game 3, officialDate 2026-10-26, 2026-10-27T00:00Z, Tropicana Field, Brewers at Rays — all match."},
    "mlb-849803": {"src": "mlb_sched", "evidence": "gamePk 849803, World Series Game 4, officialDate 2026-10-27, 2026-10-28T00:00Z, Tropicana Field — all match."},
    # --- NBA (11) ----------------------------------------------------------
    "nba-0022600085": {"src": "nba", "evidence": "Hawks at Magic, game 0022600085, 7:00 PM ET (= 23:00Z) — match."},
    "nba-0022600086": {"src": "nba", "evidence": "Bucks at Wizards, game 0022600086, 7:00 PM ET (= 23:00Z) — match."},
    "nba-0022600004": {"src": "nba", "evidence": "Timberwolves at Heat, game 0022600004, 7:30 PM ET (= 23:30Z) — match."},
    "nba-0022600087": {"src": "nba", "evidence": "Hornets at Nets, game 0022600087, 7:30 PM ET (= 23:30Z) — match."},
    "nba-0022600088": {"src": "nba", "evidence": "Bulls at Raptors, game 0022600088, 7:30 PM ET (= 23:30Z) — match."},
    "nba-0022600090": {"src": "nba", "evidence": "Pacers at Pelicans, game 0022600090, 8:00 PM ET (= 00:00Z) — match."},
    "nba-0022600089": {"src": "nba", "evidence": "Jazz at Grizzlies, game 0022600089, 8:00 PM ET (= 00:00Z) — match."},
    "nba-0022600091": {"src": "nba", "evidence": "Mavericks at Rockets, game 0022600091, 8:30 PM ET (= 00:30Z) — match."},
    "nba-0022600005": {"src": "nba", "evidence": "Warriors at Lakers, game 0022600005, 10:00 PM ET (= 02:00Z) — match."},
    "nba-0022600092": {"src": "nba", "evidence": "Suns at Trail Blazers, game 0022600092, 10:00 PM ET (= 02:00Z) — match."},
    "nba-sac-lac-20261021": {"src": "nba", "evidence": "Kings at Clippers, 10:30 PM ET on 21 Oct (= 2026-10-22T02:30Z) — match."},
    # --- Snooker (11) ------------------------------------------------------
    "snk-pang-davies": {"src": "wst", "evidence": "WST live listing: Pang Junxu v Liam Davies, Round 2, BetVictor Northern Ireland Open, 21 Oct."},
    "snk-cheung-bingham": {"src": "wst", "evidence": "WST live listing: Cheung Ka Wai v Stuart Bingham, Round 2, 21 Oct."},
    "snk-higgins-jones": {"src": "wst", "evidence": "WST live listing: John Higgins v Jak Jones, Round 2, 21 Oct."},
    "snk-wells-day": {"src": "wst", "evidence": "WST live listing: Daniel Wells v Ryan Day, Round 2, 21 Oct."},
    "snk-craigie-xu": {"src": "wst", "evidence": "WST live listing: Sam Craigie v Xu Si, Round 2, 21 Oct."},
    "snk-zhang-williams": {"src": "wst", "evidence": "WST live listing: Zhang Anda v Mark Williams, Round 2, 21 Oct."},
    "snk-holt-brown": {"src": "wst", "evidence": "WST live listing: Michael Holt v Jordan Brown, Round 2, 21 Oct."},
    "snk-gao-gilbert": {"src": "wst", "evidence": "WST live listing: Gao Yang v David Gilbert, Round 2, 21 Oct."},
    "snk-noppon-donaldson": {"src": "wst", "evidence": "WST live listing: Noppon Saengkham v Scott Donaldson, Round 2, 21 Oct."},
    "snk-brecel-odonnell": {"src": "wst", "evidence": "WST live listing: Luca Brecel v Martin O'Donnell, Round 2, 21 Oct."},
    "snk-slessor-jones": {"src": "wst", "evidence": "WST live listing: Elliot Slessor v Jamie Jones, Round 2, 21 Oct."},
    # --- Handball (12) -----------------------------------------------------
    "hand-ehf-12055": {"src": "ehf", "evidence": "EHF calendar: One Veszprém HC v Füchse Berlin, 21 Oct, 18:45 CEST (= 16:45Z) — match."},
    "hand-ehf-12052": {"src": "ehf", "evidence": "EHF calendar: RK Partizan AdmiralBet v FC Porto, 21 Oct, 18:45 CEST (= 16:45Z) — match."},
    "hand-ehf-12053": {"src": "ehf", "evidence": "EHF calendar: HC Zagreb v Paris Saint-Germain, 21 Oct, 18:45 CEST (= 16:45Z) — match."},
    "hand-ehf-12045": {"src": "ehf", "evidence": "EHF calendar: Dinamo Bucuresti v SAH Aarhus, 21 Oct, 18:45 CEST (= 16:45Z) — match."},
    "hand-ehf-12050": {"src": "ehf", "evidence": "EHF calendar: HBC Nantes v HC Vardar 1961, 21 Oct, 20:45 CEST (= 18:45Z) — match."},
    "hand-ehf-12044": {"src": "ehf", "evidence": "EHF calendar: Aalborg Håndbold v RK Celje Pivovarna Laško, 21 Oct, 20:45 CEST (= 18:45Z) — match."},
    "hand-ehf-12047": {"src": "ehf", "evidence": "EHF calendar: HC Kriens-Luzern v Industria Kielce, 21 Oct, 20:45 CEST (= 18:45Z) — match."},
    "hand-ehf-12049": {"src": "ehf", "evidence": "EHF calendar: MT Melsungen v Orlen Wisla Plock, 22 Oct, 18:45 CEST (= 16:45Z) — match."},
    "hand-ehf-12051": {"src": "ehf", "evidence": "EHF calendar: OTP Bank - PICK Szeged v GOG, 22 Oct, 18:45 CEST (= 16:45Z) — match."},
    "hand-ehf-12048": {"src": "ehf", "evidence": "EHF calendar: Kolstad Håndball v SC Magdeburg, 22 Oct, 20:45 CEST (= 18:45Z) — match."},
    "hand-ehf-12054": {"src": "ehf", "evidence": "EHF calendar: Sporting Clube de Portugal v IFK Kristianstad, 22 Oct, 20:45 CEST (= 18:45Z) — match."},
    "hand-ehf-12046": {"src": "ehf", "evidence": "EHF calendar: Barça v Montpellier Handball, 22 Oct, 20:45 CEST (= 18:45Z) — match."},
    # --- Rugby League World Cup, men (5) -----------------------------------
    "rl-wc26-tga-lbn": {"src": "nrl", "evidence": "NRL RLWC Round 2: Tonga v Lebanon, Fri 23 Oct, CommBank Stadium Sydney, 5:05am UTC-4 (= 09:05Z) — match."},
    "rl-wc26-png-sam": {"src": "nrl", "evidence": "NRL RLWC Round 2: Papua New Guinea v Samoa, Sat 24 Oct, Santos National Football Stadium Port Moresby, 12:25am UTC-4 (= 04:25Z) — match."},
    "rl-wc26-eng-fra": {"src": "nrl", "evidence": "NRL RLWC Round 2: England v France, Sat 24 Oct, HBF Park Perth, 2:35am UTC-4 (= 06:35Z) — match."},
    "rl-wc26-nzl-cok": {"src": "nrl", "evidence": "NRL RLWC Round 2: New Zealand v Cook Islands, Sun 25 Oct, One NZ Stadium Christchurch, 1:05am UTC-4 (= 05:05Z) — match."},
    "rl-wc26-aus-fij": {"src": "nrl", "evidence": "NRL RLWC Round 2: Australia v Fiji, Sun 25 Oct, Suncorp Stadium Brisbane, 5:05am UTC-4 (= 09:05Z) — match."},
    # --- Cricket (confirmed subset) ---------------------------------------
    "cric-nz-ind-t20-1": {"src": "nzc", "evidence": "NZC fixtures: BLACKCAPS v India, 1st T20I, Thu 22 Oct, Hagley Oval Christchurch — date and venue match."},
    "cric-nz-ind-t20-2": {"src": "nzc", "evidence": "NZC fixtures: BLACKCAPS v India, 2nd T20I, Sat 24 Oct, Hagley Oval Christchurch — date and venue match."},
    "cric-ford-auck-cant": {"src": "nzc", "evidence": "NZC fixtures: Auckland Aces v Canterbury, Ford Trophy Round 1, Sat 24 Oct, Kennards Hire Community Oval Auckland — match."},
    "cric-ford-wgtn-otago": {"src": "nzc", "evidence": "NZC fixtures: Wellington Firebirds v Otago Volts, Ford Trophy Round 1, Sat 24 Oct, Cello Basin Reserve Wellington — match."},
    # --- AFLW (pairings actually read back on the Round 11 board) ----------
    "aflw-r11-02": {"src": "aflw", "evidence": "AFLW Round 11 board: geel v fre at GMHBA — pairing and venue match."},
    "aflw-r11-03": {"src": "aflw", "evidence": "AFLW Round 11 board: wb v melb at MWO (Mission Whitten Oval) — pairing and venue match."},
    "aflw-r11-06": {"src": "aflw", "evidence": "AFLW Round 11 board: gcfc v rich at PFS (People First Stadium) — pairing and venue match."},
    "aflw-r11-07": {"src": "aflw", "evidence": "AFLW Round 11 board: port v coll at ALB (Alberton Oval) — pairing and venue match."},
    "aflw-r11-08": {"src": "aflw", "evidence": "AFLW Round 11 board: syd v wce at HEN (Henson Park) — pairing and venue match."},
    "aflw-r11-09": {"src": "aflw", "evidence": "AFLW Round 11 board: stk v bl at RSEA — pairing and venue match."},
}

# ---------------------------------------------------------------------------
# Rows corrected because the re-fetched page disagreed
# ---------------------------------------------------------------------------
CORRECTED: dict[str, dict[str, str]] = {
    "nhl-2026020154": {
        "src": "nhl_stand",
        "evidence": "Standings 2026-10-20 return 7-2-1, .750, +14 — but over 4 home games at 3-1-0 (homeWins 3, homeLosses 1, homeOtLosses 0), not the 5-1-0 the row carried. Home games cannot decrease, so the old figure was an error rather than drift.",
        "change": "Home split 5-1-0 -> 3-1-0 in the descriptive input. Points percentage (.750) and goal differential (+14) were already correct, so the rating 75.0 and every price are unchanged.",
    },
    "snk-holt-brown": {
        "src": "wst",
        "evidence": "WST binds this pairing to match-centre e58a00e5-e6a7-479b-98d0-5c7867af28a8. The previously cited 5b3a7f22-1c41-48e8-8a2c-94b28a21b9d1 re-fetches as an unbound template with no players attached.",
        "change": "Match-centre source URL replaced with the WST-published one.",
    },
    "snk-gao-gilbert": {
        "src": "wst",
        "evidence": "WST binds Gao Yang v David Gilbert to match-centre 4fb27af0-7db4-4ec2-b93b-137de3f66135; the cited 81c92a40-4d32-4b28-9c61-2f811d3a40c2 does not resolve to a pairing.",
        "change": "Match-centre source URL replaced with the WST-published one.",
    },
    "snk-noppon-donaldson": {
        "src": "wst",
        "evidence": "WST binds Noppon Saengkham v Scott Donaldson to match-centre 3a24076e-455c-497b-abd5-976e194abc5e; the cited 2f09a44b-71d2-4d9c-a12f-90d4b7c21f10 does not resolve to a pairing.",
        "change": "Match-centre source URL replaced with the WST-published one.",
    },
    "snk-brecel-odonnell": {
        "src": "wst",
        "evidence": "WST publishes a match centre for Luca Brecel v Martin O'Donnell at 0c49ba0c-2d21-481e-a2ac-fbece616f591; the row carried only the generic wst.tv home page.",
        "change": "Row-specific match-centre source added.",
    },
    "snk-slessor-jones": {
        "src": "wst",
        "evidence": "WST publishes a match centre for Elliot Slessor v Jamie Jones at f6536f1f-6c2d-47cd-b802-a81e6f04e4cc; the row carried only the generic wst.tv home page.",
        "change": "Row-specific match-centre source added.",
    },
    "cric-ausw-nzw-t20-3": {
        "src": "nzc",
        "evidence": "NZC fixtures list Australia Women v New Zealand Women, 3rd T20I, Thu 22 Oct at North Sydney Oval, Sydney. The row said Manuka Oval, Canberra; no fixture at Manuka appears on the official service.",
        "change": "Venue Manuka Oval, Canberra -> North Sydney Oval, Sydney.",
    },
    "cric-nza-inda-fc1": {
        "src": "nzc",
        "evidence": "NZC fixtures list New Zealand A v India A, 1st Four-Day Match, Fri 23 Oct at Bert Sutcliffe Oval, Lincoln University. The row said 22 Oct at Saxton Oval, Nelson.",
        "change": "Date 2026-10-22 -> 2026-10-23 and venue -> Bert Sutcliffe Oval, Lincoln University.",
    },
    "cric-ford-cds-nd": {
        "src": "nzc",
        "evidence": "NZC fixtures list Central Stags v Northern Districts, Ford Trophy Round 1, Sat 24 Oct at Saxton Oval, Nelson. The row said Pukekura Park, New Plymouth.",
        "change": "Venue Pukekura Park, New Plymouth -> Saxton Oval, Nelson.",
    },
}

# ---------------------------------------------------------------------------
# Rows where the re-fetched page disagrees and a human must decide
# ---------------------------------------------------------------------------
FLAGGED: dict[str, dict[str, str]] = {
    "nhl-2026020160": {
        "src": "nhl_stand",
        "evidence": "The priced input is Vegas 8-2-0 (.800, W3). The same endpoint re-fetched at 2026-10-21T07:05:30Z returns 8-3-0 (.727, L1) over 11 games, so the club has played once since the snapshot.",
        "change": "No change. The line and its rating are a labelled pre-game snapshot and are retained; re-pricing would silently rewrite a published pick. Disclosed on the row and on Flagged for Review for a reviewer decision.",
    },
    "nhl-2026020158": {
        "src": "nhl_sched",
        "evidence": "Florida's back-to-back is real (they play Ottawa on 21 Oct and Pittsburgh on 22 Oct), but the 21 Oct schedule read back only two games, so this row's own game record was not re-read.",
        "change": "Fixture facts left as published; only the back-to-back relationship was corroborated. Not promoted to confirmed.",
    },
}

# ---------------------------------------------------------------------------
# Why a row was not re-checked in this pass (no silent gaps)
# ---------------------------------------------------------------------------
NOT_RECHECKED_REASON: dict[str, str] = {
    "darts": "PDC draw release returns a cookie-consent interstitial to a non-browser fetch; re-tested on 2026-10-21 at two offsets and returned consent text only. The 16 ties could not be re-read from the publisher page.",
    "tennis": "WTA draw pages are client-rendered and returned only the notification shell with no draw body; ATP draws behave the same way. Rankings pages were not re-read either.",
    "euroleague": "EuroLeague / EuroCup game-centre pages are client-rendered and were not re-fetched in this pass.",
    "volleyball": "PlusLiga and SuperLega fixture pages were not re-fetched in this pass.",
    "rugby-union": "Top 14, URC and Premiership pages were not re-fetched in this pass; the five Premiership rows keep their existing cross-checked status.",
    "gaelic-football": "GAA county fixture pages were not re-fetched in this pass.",
    "golf": "PGA TOUR, DP World Tour, LPGA and PGA TOUR Champions schedules were not re-fetched in this pass.",
    "greyhounds": "GBGB race calendar was not re-fetched in this pass.",
    "motor-racing": "Formula 1 event page was not re-fetched in this pass.",
    "esports": "LoL Esports schedule was not re-fetched in this pass.",
    "ice-hockey": "The 21 Oct schedule response was read; this row's game sits on the 22/23 Oct pages, which were not read back.",
    "aussie-rules": "The Round 11 board fragment returned did not include this pairing; only six of the nine AFLW fixtures were readable.",
    "rugby-league": "The NRL women's competition draw was not readable from the men's competition page used in this pass.",
    "cricket": "Not re-read in this pass; the NZC fixtures service was used for the rows that were checked.",
}

# ---------------------------------------------------------------------------
# Published findings
# ---------------------------------------------------------------------------
FINDINGS: list[dict[str, str]] = [
    {
        "id": "F-V1",
        "severity": "high",
        "area": "Snooker — three rows cited match-centre URLs that bind to no match",
        "detail": "snk-holt-brown, snk-gao-gilbert and snk-noppon-donaldson carried UUIDs that re-fetch as an empty match-centre template with no players; snk-brecel-odonnell and snk-slessor-jones carried no match centre at all although WST publishes one for both.",
        "status": "Corrected in the dataset source; all eleven rows now cite the match centre WST actually binds to the pairing.",
        "source": "wst",
    },
    {
        "id": "F-V2",
        "severity": "medium",
        "area": "Tennis — WTA Ningbo cited under a stale tournament id",
        "detail": "Six rows linked https://www.wtatennis.com/tournaments/1115/ningbo/2026/draws. WTA's own site links the BNB Ningbo Open draws at tournament 2092.",
        "status": "Citation corrected to /tournaments/2092/. The draw body itself could not be re-read because WTA serves it client-side.",
        "source": "wta",
    },
    {
        "id": "F-V3",
        "severity": "high",
        "area": "Cricket — three NZC fixtures carried the wrong venue or date",
        "detail": "Official NZC fixtures place the 3rd Women's T20I at North Sydney Oval (not Manuka Oval), New Zealand A v India A on 23 Oct at Bert Sutcliffe Oval (not 22 Oct at Saxton Oval), and Central Stags v Northern Districts at Saxton Oval, Nelson (not Pukekura Park).",
        "status": "Corrected in the dataset source from the re-fetched official service.",
        "source": "nzc",
    },
    {
        "id": "F-V4",
        "severity": "medium",
        "area": "Ice hockey — Boston home split not reproducible",
        "detail": "The row claimed 5-1-0 at home. The standings endpoint returns four home games at 3-1-0 (homeWins 3, homeLosses 1, homeOtLosses 0) for the same 7-2-1 record. Home games cannot decrease, so this was an error, not drift.",
        "status": "Corrected to 3-1-0. Rating and every price are unchanged because only the descriptive split was affected.",
        "source": "nhl_stand",
    },
    {
        "id": "F-V5",
        "severity": "medium",
        "area": "Ice hockey — live-table drift after the pricing snapshot",
        "detail": "Vegas was priced at 8-2-0 (.800, W3). The same live endpoint now returns 8-3-0 (.727, L1). The pattern will repeat for any club that plays after a snapshot.",
        "status": "Flagged, not re-priced. Rewriting a published pick after the fact would be worse than disclosing the drift; the row is labelled a pre-game snapshot.",
        "source": "nhl_stand",
    },
    {
        "id": "F-V6",
        "severity": "medium",
        "area": "Darts — PDC page still not machine-readable",
        "detail": "Two fetches of the official draw release returned only a cookie-consent interstitial. This is the same barrier earlier sessions reported; it has not been fixed upstream.",
        "status": "16 darts rows marked not re-checked rather than implied verified.",
        "source": "pdc",
    },
    {
        "id": "F-V7",
        "severity": "medium",
        "area": "Tennis — official draws are client-rendered",
        "detail": "WTA and ATP draw pages return a notification shell without draw content to a text fetch, so pairings cannot be re-read from the tour sites.",
        "status": "11 tennis rows marked not re-checked.",
        "source": "wta",
    },
    {
        "id": "F-V8",
        "severity": "low",
        "area": "Snooker — session clock is rendered in the viewer's timezone",
        "detail": "WST publishes no UTC session time. The fetch client renders publisher clocks at UTC-4 (all five RLWC kick-offs mapped exactly under that offset), which puts WST's 05:00/08:00/09:00/14:00/15:00 displays at roughly 09:00/12:00/13:00/18:00/19:00 UTC. That derivation is arithmetic on a rendering, not a published value.",
        "status": "start_utc stays blank for all eleven rows; the flag now explains the rendering instead of asserting a local session time.",
        "source": "wst",
    },
    {
        "id": "F-V9",
        "severity": "low",
        "area": "Rugby league — NRL competition id in the citation",
        "detail": "The men's RLWC rows linked nrl.com/draw/?competition=175..., which the site serves as competition 131 for the same Round 2 draw.",
        "status": "Men's citation corrected to competition=131. The women's id (176) was not re-tested and is left as published with its rows marked not re-checked.",
        "source": "nrl",
    },
    {
        "id": "F-V10",
        "severity": "medium",
        "area": "Coverage — most rows were not re-fetched in this pass",
        "detail": "Fresh official reads covered {refetched} of 134 rows (confirmed + corrected + flagged). The remaining {not_rechecked} keep their original verified or cross-checked status and their source links, but this pass did not re-read them.",
        "status": "Every one of the {not_rechecked} is listed on the Live Verification page with the reason, so the gap is visible rather than implied. No row is claimed as re-verified without a read.",
        "source": "nhl_sched",
    },
]


# ===========================================================================
# T21 — second pass, session `b95dbd01-olbg1`, 2026-10-21T09:05Z
# ---------------------------------------------------------------------------
# Same vocabulary, same page, second read. Every entry below records a page
# that was fetched again *after* the T20 pass, so a row marked confirmed here
# is one whose official page was re-opened twice in one day, and a row marked
# corrected here is one where the second read found the first read's value
# wrong. Nothing in T20 is deleted: T20's entries keep their status unless a
# T21 entry supersedes them, and each row carries the timestamp of the pass
# that last read it.
# ===========================================================================
T21_CHECKED_AT = "2026-10-21T09:05Z"

SOURCES.update({
    "nhl_sched22": {
        "name": "NHL official schedule API (2026-10-22)",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
    },
    "mlb_sched21": {
        "name": "MLB StatsAPI official schedule (2026-10-21..30, venues + linescore)",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-21&endDate=2026-10-30&hydrate=venue(location),linescore",
    },
    "ehf_pdf": {
        "name": "EHF Champions League Men 2026/27 group-phase playing times (official PDF)",
        "url": "https://www.eurohandball.com/media/jqal4wt0/ehfcl-men-2026-27-group-phase-playing-times.pdf",
    },
    "wst_matches": {
        "name": "World Snooker Tour — BetVictor Northern Ireland Open 2026 match list",
        "url": "https://www.wst.tv/matches",
    },
    "nrl_draw2": {
        "name": "NRL / Rugby League World Cup 2026 Round 2 draw (nrl.com)",
        "url": "https://www.nrl.com/draw/?competition=131&round=2&season=2026",
    },
    "urc_fixtures": {
        "name": "United Rugby Championship 2026/27 fixtures in full (Round 4)",
        "url": "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/",
    },
    "top14_cal": {
        "name": "LNR Top 14 official calendar, journée 7",
        "url": "https://top14.lnr.fr/calendrier-et-resultats",
    },
    "aflw_hub": {
        "name": "AFL official AFLW hub — Round 11 fixture board & match ids",
        "url": "https://www.afl.com.au/aflw",
    },
    "aflw_ladder": {
        "name": "AFL official 2026 AFLW ladder (after Round 10)",
        "url": "https://www.afl.com.au/aflw/ladder",
    },
    "nba_cdn": {
        "name": "NBA official scoreboard feed (cdn.nba.com)",
        "url": "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json",
    },
    "plusliga": {
        "name": "PlusLiga fixtures (plusliga.pl, redirects to tauronliga.pl)",
        "url": "https://www.plusliga.pl/games.html",
    },
})

# ---------------------------------------------------------------------------
# Re-read in this pass and matching row for row
# ---------------------------------------------------------------------------
T21_CONFIRMED: dict[str, dict[str, str]] = {
    # --- MLB World Series (4): officialDate, first pitch and venue ------
    "mlb-849805": {"src": "mlb_sched21", "evidence": "Re-read 2026-10-21: gamePk 849805, World Series Game 1, officialDate 2026-10-23, gameDate 2026-10-24T00:00:00Z, Rays at Brewers, American Family Field — all match."},
    "mlb-849802": {"src": "mlb_sched21", "evidence": "Re-read 2026-10-21: gamePk 849802, Game 2, officialDate 2026-10-24, gameDate 2026-10-25T00:00:00Z, American Family Field — all match."},
    "mlb-849804": {"src": "mlb_sched21", "evidence": "Re-read 2026-10-21: gamePk 849804, Game 3, officialDate 2026-10-26, gameDate 2026-10-27T00:00:00Z, Brewers at Rays, Tropicana Field — all match."},
    "mlb-849803": {"src": "mlb_sched21", "evidence": "Re-read 2026-10-21: gamePk 849803, Game 4, officialDate 2026-10-27, gameDate 2026-10-28T00:00:00Z, Tropicana Field — all match."},
    # --- NHL (2) -------------------------------------------------------
    "nhl-2026020154": {"src": "nhl_sched22", "evidence": "Re-read 2026-10-21: game 2026020154, Nashville at Boston, TD Garden, startTimeUTC 2026-10-22T23:00:00Z — participants, venue and start match."},
    "nhl-2026020155": {"src": "nhl_sched22", "evidence": "Re-read 2026-10-21: game 2026020155, New York Rangers at Toronto, Scotiabank Arena, startTimeUTC 2026-10-22T23:00:00Z — all match."},
    # --- Handball (11 of 12; 12048 corrected below) --------------------
    "hand-ehf-12055": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: One Veszprém v Füchse Berlin, Wed 21.10.2026, 18:45 CEST, One Veszprém Arena (Veszprém) = 16:45Z — participants, date, start and venue match."},
    "hand-ehf-12052": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: Partizan v FC Porto, Wed 21.10.2026, 18:45 CEST, Hall Aleksandar Nikolic (Belgrade) = 16:45Z — all match."},
    "hand-ehf-12053": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: HC Zagreb v PSG, Wed 21.10.2026, 18:45 CEST, Arena Zagreb = 16:45Z — all match."},
    "hand-ehf-12045": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: Dinamo Bucuresti v SAH Aarhus, Wed 21.10.2026, 18:45 CEST, Polyvalenta Hall (Bucharest) = 16:45Z — all match."},
    "hand-ehf-12050": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: HBC Nantes v Vardar 1961, Wed 21.10.2026, 20:45 CEST, H Arena (Nantes) = 18:45Z — all match."},
    "hand-ehf-12044": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: Aalborg v Celje, Wed 21.10.2026, 20:45 CEST, Sparekassen Danmark Arena = 18:45Z — all match."},
    "hand-ehf-12047": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: Kriens-Luzern v Industria Kielce, Wed 21.10.2026, 20:45 CEST, Pilatus Arena (Kriens) = 18:45Z — all match."},
    "hand-ehf-12049": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: MT Melsungen v Orlen Wisla Plock, Thu 22.10.2026, 18:45 CEST, Rothenbach-Halle (Kassel) = 16:45Z — all match."},
    "hand-ehf-12051": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: OTP Bank-Pick Szeged v GOG, Thu 22.10.2026, 18:45 CEST, Pick Arena (Szeged) = 16:45Z — all match."},
    "hand-ehf-12048": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: Kolstad Handball v SC Magdeburg, Thu 22.10.2026, 20:45 CEST, Kolstad Arena (Kolstad, NOR) = 18:45Z — participants, date and start match; venue differs, corrected below."},
    "hand-ehf-12054": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: Sporting CP v IFK Kristianstad, Thu 22.10.2026, 20:45 CEST, Pavilhao Joao Rocha (Lisbon) = 18:45Z — all match."},
    "hand-ehf-12046": {"src": "ehf_pdf", "evidence": "EHF Round 5 PDF: Barça v Montpellier HB, Thu 22.10.2026, 20:45 CEST, Palau Blaugrana = 18:45Z — all match."},
    # --- Snooker (11): pairings and match-centre ids --------------------
    "snk-pang-davies": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 36 Pang Junxu v Liam Davies, Wed 21 Oct, match-centre 67133698-e8a4-4b37-9266-452a97df8584 — pairing and id match the row."},
    "snk-cheung-bingham": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 42 Ka Wai Cheung v Stuart Bingham, Wed 21 Oct, match-centre 3d53c559-9bd7-4bc4-8e1d-a6c2b7459528 — all match."},
    "snk-higgins-jones": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 45 John Higgins v Jak Jones, Wed 21 Oct, match-centre eba55492-fba6-4a53-90be-a04b3560ae65 — all match."},
    "snk-wells-day": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 46 Daniel Wells v Ryan Day, Wed 21 Oct, match-centre e9c15ae6-b9b8-4cea-a83a-49c58eb14046 — all match."},
    "snk-craigie-xu": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 38 Sam Craigie v Xu Si, Wed 21 Oct, match-centre afb42fc9-9654-479e-997e-d33d8a1a6888 — all match."},
    "snk-zhang-williams": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 43 Zhang Anda v Mark Williams, Wed 21 Oct, match-centre 480e5abf-5766-44ad-9918-f822ceefd4a5 — all match."},
    "snk-holt-brown": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 47 Michael Holt v Jordan Brown, Wed 21 Oct, match-centre e58a00e5-e6a7-479b-98d0-5c7867af28a8 — all match."},
    "snk-gao-gilbert": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 41 Gao Yang v David Gilbert, Wed 21 Oct, match-centre 4fb27af0-7db4-4ec2-b93b-137de3f66135 — all match."},
    "snk-noppon-donaldson": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 48 Noppon Saengkham v Scott Donaldson, Wed 21 Oct, match-centre 3a24076e-455c-497b-abd5-976e194abc5e — all match."},
    "snk-brecel-odonnell": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 44 Luca Brecel v Martin O'Donnell, Wed 21 Oct, match-centre 0c49ba0c-2d21-481e-a2ac-fbece616f591 — all match."},
    "snk-slessor-jones": {"src": "wst_matches", "evidence": "WST match list, Round 2: Match 39 Elliot Slessor v Jamie Jones, Wed 21 Oct, match-centre f6536f1f-6c2d-47cd-b802-a81e6f04e4cc — all match."},
    # --- Rugby league, men's RLWC (5) ----------------------------------
    "rl-wc26-tga-lbn": {"src": "nrl_draw2", "evidence": "nrl.com Round 2: Tonga v Lebanon, Friday 23 October, CommBank Stadium, kick-off printed 5:05am — row's 2026-10-23T09:05Z is that clock plus the client's UTC-4 rendering offset, which the same page reproduces for all five fixtures."},
    "rl-wc26-png-sam": {"src": "nrl_draw2", "evidence": "nrl.com Round 2: Papua New Guinea v Samoa, Saturday 24 October, Santos National Football Stadium, 12:25am printed = 04:25Z on the same offset — all match."},
    "rl-wc26-eng-fra": {"src": "nrl_draw2", "evidence": "nrl.com Round 2: England v France, Saturday 24 October, HBF Park Perth, 2:35am printed = 06:35Z — all match."},
    "rl-wc26-nzl-cok": {"src": "nrl_draw2", "evidence": "nrl.com Round 2: New Zealand v Cook Islands, Sunday 25 October, One NZ Stadium Christchurch, 1:05am printed = 05:05Z — all match (venue name printed without 'New Zealand')."},
    "rl-wc26-aus-fij": {"src": "nrl_draw2", "evidence": "nrl.com Round 2: Australia v Fiji, Sunday 25 October, Suncorp Stadium, 5:05am printed = 09:05Z — all match."},
    # --- Rugby union: Top 14 (3) and URC (3; Leinster row flagged) ------
    "ru-top14-609564": {"src": "top14_cal", "evidence": "LNR journée 7: Aviron Bayonnais v LOU Rugby, samedi 24 octobre, 16h35, match sheet 11861 — participants, date, 14:35Z start (CEST) and sheet id match."},
    "ru-top14-609567": {"src": "top14_cal", "evidence": "LNR journée 7: Stade Toulousain v USA Perpignan, samedi 24 octobre, 16h35, match sheet 11867 — all match."},
    "ru-top14-609554": {"src": "top14_cal", "evidence": "LNR journée 7: Stade Rochelais v Union Bordeaux-Bègles, dimanche 25 octobre, 21h05, match sheet 11864. 25 October is after the French DST change, so 21h05 CET = 20:05Z, which is exactly the row's value."},
    "ru-urc-609577": {"src": "urc_fixtures", "evidence": "URC Round 4, Friday 23 October: Connacht v Zebre Parma, Dexcom Stadium Galway, KO 19:45 IRE & UK = 18:45Z — all match."},
    "ru-urc-609576": {"src": "urc_fixtures", "evidence": "URC Round 4, Saturday 24 October: Vodacom Bulls v Ulster, Loftus Versfeld, KO 12:45 IRE & UK / 13:45 SAST = 11:45Z — all match."},
    "ru-urc-609580": {"src": "urc_fixtures", "evidence": "URC Round 4, Saturday 24 October: DHL Stormers v Scarlets, DHL Stadium Cape Town, KO 15:00 IRE & UK = 14:00Z — all match."},
    # --- Cricket: NZC fixture service -----------------------------------
    "cric-ausw-nzw-t20-3": {"src": "nzc", "evidence": "NZC fixtures: Australia Women v New Zealand Women, 3rd T20I, Thu 22 Oct, North Sydney Oval, 4:15am printed = 08:15Z under the same offset — participants, date, venue and start match."},
    "cric-nza-inda-fc1": {"src": "nzc", "evidence": "NZC fixtures: New Zealand A v India A, 1st Four-Day Match, Fri 23 Oct, Bert Sutcliffe Oval, Lincoln University — participants, date and venue match; NZC prints 5:30pm with no timezone, so start_utc stays blank."},
}

# ---------------------------------------------------------------------------
# Re-read in this pass and found wrong: value replaced in the dataset source
# ---------------------------------------------------------------------------
T21_CORRECTED: dict[str, dict[str, str]] = {
    "hand-ehf-12048": {
        "src": "ehf_pdf",
        "evidence": "The EHF playing-times PDF places Kolstad's home fixture in Round 5 at Kolstad Arena (Kolstad, NOR), not Trondheim Spektrum, Trondheim.",
        "change": "venue corrected to 'Kolstad Arena, Kolstad, Norway'. Participants, date, 18:45Z start and the Round 5 pairing were already right.",
    },
    "cric-ford-auck-cant": {
        "src": "nzc",
        "evidence": "On the NZC fixtures page the three Ford Trophy Round 1 matches sit under the TUE 27 Oct heading, after the 3rd T20I and before the FRI 30 Oct block that carries Ford Trophy Round 2. The row carried 2026-10-24.",
        "change": "date_local 2026-10-24 -> 2026-10-27 (Auckland Aces v Canterbury, Kennards Hire Community Oval). Start time stays blank: NZC prints 5:30pm with no timezone.",
    },
    "cric-ford-cds-nd": {
        "src": "nzc",
        "evidence": "Same NZC read: Central Stags v Northern Districts is Ford Trophy Round 1 on Tue 27 Oct at Saxton Oval, Nelson.",
        "change": "date_local 2026-10-24 -> 2026-10-27. Venue (Saxton Oval) confirmed as corrected earlier today. Start time stays blank.",
    },
    "cric-ford-wgtn-otago": {
        "src": "nzc",
        "evidence": "Same NZC read: Wellington Firebirds v Otago Volts is Ford Trophy Round 1 on Tue 27 Oct at the Cello Basin Reserve.",
        "change": "date_local 2026-10-24 -> 2026-10-27. Start time stays blank.",
    },
    "cric-afg-ban-odi": {
        "src": "nzc",
        "evidence": "No official fixture page for this match was found in any of the two passes: the row's only citation is the ICC rankings table, which publishes no fixtures, and NZC (which covers a different board) does not list it.",
        "change": "status downgraded from 'verified' to 'unverified' and flagged. Date and venue remain published as an OLBG-listed event with no governing-body confirmation; no value was invented to fill the gap.",
    },
    "aflw-r11-01": {"src": "aflw_hub", "evidence": "AFL AFLW Round 11 board: match 8979 North Melbourne v Adelaide is Sat 10:05 PM (client render) at NHO — North Hobart Oval. The row carried Fri 23 Oct at Arden Street Oval.", "change": "start_utc 2026-10-23T08:15Z -> 2026-10-25T02:05Z; venue -> 'North Hobart Oval, Hobart'."},
    "aflw-r11-02": {"src": "aflw_hub", "evidence": "Round 11 board: match 8974 Geelong v Fremantle at GMHBA prints Sat 12:05 AM, i.e. 04:05Z. The row carried 02:05Z, which is the St Kilda v Brisbane slot.", "change": "start_utc 2026-10-24T02:05Z -> 2026-10-24T04:05Z."},
    "aflw-r11-03": {"src": "aflw_hub", "evidence": "Round 11 board: match 8973 Western Bulldogs v Melbourne at Mission Whitten Oval prints Sat 4:15 AM = 08:15Z. The row carried 04:05Z.", "change": "start_utc 2026-10-24T04:05Z -> 2026-10-24T08:15Z."},
    "aflw-r11-04": {"src": "aflw_hub", "evidence": "Round 11 board: match 8975 Carlton v GWS at IKON Park prints Sun 2:05 AM = 06:05Z on 25 October. The row carried 24 October 04:05Z.", "change": "start_utc 2026-10-24T04:05Z -> 2026-10-25T06:05Z."},
    "aflw-r11-05": {"src": "aflw_hub", "evidence": "Round 11 board: match 8976 Hawthorn v Essendon prints Sun 12:05 AM = 04:05Z at KCC, the Kennedy Community Centre in Dingley. The row carried Sat 24 Oct 06:15Z at Kinetic Stadium, Frankston.", "change": "start_utc 2026-10-24T06:15Z -> 2026-10-25T04:05Z; venue -> 'Kennedy Community Centre, Dingley'."},
    "aflw-r11-06": {"src": "aflw_hub", "evidence": "Round 11 board: match 8972 Gold Coast v Richmond at People First Stadium prints Sat 2:05 AM = 06:05Z. The row carried 08:15Z.", "change": "start_utc 2026-10-24T08:15Z -> 2026-10-24T06:05Z."},
    "aflw-r11-07": {"src": "aflw_hub", "evidence": "Round 11 board: match 8970 Port Adelaide v Collingwood at Alberton prints Fri 4:15 AM = 08:15Z on 23 October. The row carried 25 October 02:05Z.", "change": "start_utc 2026-10-25T02:05Z -> 2026-10-23T08:15Z."},
    "aflw-r11-08": {"src": "aflw_hub", "evidence": "Round 11 board: match 8977 Sydney v West Coast at Henson Park prints Sat 9:35 PM = 01:35Z on 25 October. The row carried 04:05Z.", "change": "start_utc 2026-10-25T04:05Z -> 2026-10-25T01:35Z."},
    "aflw-r11-09": {"src": "aflw_hub", "evidence": "Round 11 board: match 8971 St Kilda v Brisbane at RSEA Park prints Fri 10:05 PM = 02:05Z on 24 October. The row carried 25 October 06:05Z.", "change": "start_utc 2026-10-25T06:05Z -> 2026-10-24T02:05Z."},
}

T21_FLAGGED: dict[str, dict[str, str]] = {
    "ru-urc-609578": {
        "src": "urc_fixtures",
        "evidence": "URC Round 4 lists Leinster v Munster, Saturday 24 October, KO 18:00 IRE & UK (= 17:00Z, which matches the row) but prints the venue as 'TBC, Dublin'. The row asserts Aviva Stadium.",
        "change": "No change. The match, date and start are confirmed; the venue is not settled by the official page and is published for review rather than deleted.",
    },
    "cric-nz-ind-t20-1": {
        "src": "nzc",
        "evidence": "NZC fixtures confirm New Zealand v India, 1st T20I, Thu 22 Oct at Hagley Oval and print '3:00am' with no timezone. The row publishes 06:15Z, which no official page states; the client's render offset (UTC-4, pinned by five nrl.com kick-offs) would put 3:00am at 07:00Z, not 06:15Z.",
        "change": "No change to the fixture facts. The start time is disclosed as unconfirmed rather than silently rewritten, because neither 06:15Z nor 07:00Z is a published value.",
    },
    "cric-nz-ind-t20-2": {
        "src": "nzc",
        "evidence": "Same read: 2nd T20I, Sat 24 Oct, Hagley Oval, '3:00am' printed with no timezone; the row publishes 06:15Z on 24 October.",
        "change": "No change; start time disclosed as unconfirmed.",
    },
}

# Per-row reasons where the sport-level default would be too coarse to be useful.
ROW_REASON: dict[str, str] = {
    "nhl-2026020158": "The 22 Oct schedule response shows game 2026020158 at PPG Paints Arena with startTimeUTC 2026-10-22T23:00:00Z, matching the row, but the response was truncated before both club names, so the participants were not read back in this pass.",
    "nhl-2026020160": "Game 2026020160 falls in the following NHL game week (2026-10-23) and was not re-read in either pass; the row keeps its pre-game snapshot and its drift flag.",
    "cric-afg-ban-odi": "No governing body publishes this fixture in a form either pass could read; the row is downgraded to unverified instead of being called confirmed.",
}

T21_NOT_RECHECKED_REASON: dict[str, str] = {
    "tennis": "ATP and WTA draw pages still return a client-rendered shell to a text fetch; the eleven tennis rows were not re-read in this pass either.",
    "darts": "pdc.tv returned its cookie-consent interstitial again (HTTP 200, consent text only); the sixteen darts rows were not re-read.",
    "basketball": "The NBA scoreboard feed (cdn.nba.com) returned HTTP 500 and nba.com/games is client-rendered, so neither NBA nor the EuroLeague/EuroCup game-centre pages could be re-read in this pass; those rows keep the status the earlier pass gave them.",
    "volleyball": "plusliga.pl redirects to tauronliga.pl and the men's fixture list is paginated behind that portal; legavolley.it was not re-read. The eight volleyball rows keep their earlier status.",
    "gaelic-football": "County-board fixture pages were not re-read in this pass; the four GAA rows keep their earlier status.",
    "golf": "Tour schedule pages (europeantour.com, lpga.com, pgatour.com) are client-rendered and were not re-read in this pass.",
    "motor-racing": "formula1.com's 2026 United States Grand Prix page was not re-read in this pass.",
    "esports": "lolesports.com is client-rendered; the LoL Worlds row was not re-read in this pass.",
    "greyhounds": "GBGB publishes results rather than a machine-readable forward schedule; the three greyhound cards were not re-read.",
    "rugby-union-prem": "premrugby.com/fixtures-results is client-rendered and returned navigation only, so the five cross-checked Premiership rows were not re-read in either pass.",
    "rugby-league-w": "nrl.com ignores the competition=176 query parameter and serves the men's draw; the women's competition selector is client-side, so the two women's RLWC rows were not re-read.",
}

# Sports whose default reason differs from the T20 default.
NOT_RECHECKED_REASON.update({k: v for k, v in T21_NOT_RECHECKED_REASON.items() if not k.endswith("-prem") and not k.endswith("-w")})

# ---------------------------------------------------------------------------
# Merge: T21 entries supersede T20 entries for the same row.
# ---------------------------------------------------------------------------
ROW_CHECKED_AT: dict[str, str] = {}
for _tbl in (T21_CONFIRMED, T21_CORRECTED, T21_FLAGGED):
    for _fid in _tbl:
        ROW_CHECKED_AT[_fid] = T21_CHECKED_AT
        CONFIRMED.pop(_fid, None)
        CORRECTED.pop(_fid, None)
        FLAGGED.pop(_fid, None)
CONFIRMED.update(T21_CONFIRMED)
CORRECTED.update(T21_CORRECTED)
FLAGGED.update(T21_FLAGGED)
ROW_REASON.update({
    "cric-nz-ind-t20-1": ROW_REASON.get("cric-nz-ind-t20-1", ""),
    "cric-nz-ind-t20-2": ROW_REASON.get("cric-nz-ind-t20-2", ""),
})
# Rows the T21 pass could not read get a specific reason even if T20 had one.
for _fid in ("rl-wc26w-aus-eng", "rl-wc26w-sam-wal"):
    ROW_REASON[_fid] = T21_NOT_RECHECKED_REASON["rugby-league-w"]
for _fid in ("ru-gloucester-bath", "ru-newcastle-sale", "ru-leicester-northampton",
             "ru-bristol-exeter", "ru-harlequins-saracens"):
    ROW_REASON[_fid] = T21_NOT_RECHECKED_REASON["rugby-union-prem"]
for _fid in ("vol-plus-36961", "vol-plus-36962", "vol-plus-36963", "vol-plus-36964", "vol-plus-36965"):
    ROW_REASON[_fid] = T21_NOT_RECHECKED_REASON["volleyball"]

T21_FINDINGS: list[dict] = [
    {
        "id": "F-T21-01",
        "severity": "high",
        "area": "AFLW — the ladder used to price nine rows is not the official 2026 ladder",
        "detail": (
            "Every AFLW row cites a 2026 R10 ladder input. Read against the official afl.com.au 2026 AFLW ladder "
            "after Round 10, the published inputs do not reconcile: the rows give North Melbourne 40 points (10-0) "
            "where the official table has 36 (9-1), Geelong 16 points at 13th where the official table has 36 at 2nd, "
            "Gold Coast 4 points at 18th where the official table has 28 at 5th, St Kilda 20 points at 10th where the "
            "official table has 4 at 18th, and so on for 16 of the 18 clubs. The fixture facts were verified in this "
            "pass and nine start times plus one venue were corrected; the pricing inputs were not."
        ),
        "status": (
            "Disclosed, not silently re-priced. Re-pricing would rewrite nine published rows and the three AFLW "
            "high-confidence picks in the same commit that discovered the error, which is how a desk loses its audit "
            "trail. Every AFLW row now carries the mismatch as a flag, the official ladder link is on this register, "
            "and T22 in COORDINATION.md is the dedicated re-price task."
        ),
        "source": "aflw_ladder",
    },
    {
        "id": "F-T21-02",
        "severity": "high",
        "area": "AFLW — nine Round 11 start times were shifted by one fixture, and one venue was wrong",
        "detail": (
            "The nine AFLW rows were correct about participants but had been given the Round 11 kick-off slots in "
            "chronological order rather than in their own match's order. Port Adelaide v Collingwood carried the North "
            "Melbourne slot, St Kilda v Brisbane carried Geelong's, and so on; two rows shared 2026-10-24T04:05Z, one "
            "time (06:15Z) appears in no official fixture, and Hawthorn v Essendon was placed at Kinetic Stadium, "
            "Frankston instead of the Kennedy Community Centre in Dingley."
        ),
        "status": "All nine start times corrected from the AFL Round 11 board, the Hawthorn venue corrected, and each corrected value carries its match id (8970-8979) in the evidence column.",
        "source": "aflw_hub",
    },
    {
        "id": "F-T21-03",
        "severity": "medium",
        "area": "Cricket — Ford Trophy Round 1 is 27 October, not 24 October",
        "detail": (
            "The three Ford Trophy rows were dated 2026-10-24. On the NZC fixture service the Round 1 block sits under "
            "the TUE 27 Oct heading, after the 3rd T20I and before the FRI 30 Oct block that carries Round 2."
        ),
        "status": "All three date_local values corrected to 2026-10-27; venues confirmed. Start times stay blank because NZC prints 5:30pm with no timezone.",
        "source": "nzc",
    },
    {
        "id": "F-T21-04",
        "severity": "medium",
        "area": "Cricket — the Afghanistan v Bangladesh ODI has no governing-body fixture page",
        "detail": (
            "The row's only citation is the ICC rankings table, which publishes no fixtures. Neither pass found an "
            "official page that lists the match at Sharjah, and NZC does not cover it."
        ),
        "status": "Row status downgraded from verified to unverified and flagged; date and venue remain as OLBG lists them, with nothing invented to fill the gap.",
        "source": "nzc",
    },
    {
        "id": "F-T21-05",
        "severity": "medium",
        "area": "Rugby league — the women's RLWC rows could not be re-read",
        "detail": (
            "nrl.com serves the men's Round 2 draw for ?competition=176 as well, because the competition selector is "
            "client-side. The two women's rows therefore stay not re-checked with that reason printed."
        ),
        "status": "Reason recorded per row; no value changed.",
        "source": "nrl_draw2",
    },
    {
        "id": "F-T21-06",
        "severity": "low",
        "area": "Source reachability — three publishers block a text read",
        "detail": (
            "pdc.tv still returns a cookie-consent interstitial. cdn.nba.com returned HTTP 500 during this pass. "
            "premrugby.com and plusliga.pl render their fixture lists client-side (plusliga.pl also redirects to the "
            "tauronliga.pl portal). None of these failures is treated as agreement."
        ),
        "status": "27 rows across darts, NBA, EuroLeague/EuroCup, Premiership and PlusLiga stay not re-checked with the blocker named.",
        "source": "nba_cdn",
    },
    {
        "id": "F-T21-07",
        "severity": "low",
        "area": "Handball — one venue did not match the official playing-times sheet",
        "detail": "Kolstad's Round 5 home fixture is listed by the EHF at Kolstad Arena (Kolstad), not Trondheim Spektrum.",
        "status": "Venue corrected; the other eleven handball rows matched the PDF on participants, date, start time and arena.",
        "source": "ehf_pdf",
    },
    {
        "id": "F-T21-08",
        "severity": "low",
        "area": "Top 14 — the Sunday fixture is after the French DST change",
        "detail": (
            "La Rochelle v Bordeaux-Bègles is listed at 21h05 on Sunday 25 October. France leaves CEST at 03:00 that "
            "morning, so 21h05 is CET and equals 20:05Z. A naive CEST conversion would have produced 19:05Z and looked "
            "like a one-hour error in the row; the row is right."
        ),
        "status": "Confirmed, no change. Recorded because the same trap applies to every other Sunday European fixture after 25 October.",
        "source": "top14_cal",
    },
]

FINDINGS.extend(T21_FINDINGS)


def _status_row(fixture: dict) -> dict:
    fid = fixture["id"]
    checked_at = ROW_CHECKED_AT.get(fid, CHECKED_AT)
    if fid in CORRECTED:
        entry = CORRECTED[fid]
        return {
            "id": fid,
            "sport": fixture["sport"],
            "competition": fixture["competition"],
            "match": f"{fixture['home']} v {fixture['away']}" if fixture.get("away") else fixture["home"],
            "status": "corrected",
            "source_name": SOURCES[entry["src"]]["name"],
            "source_url": SOURCES[entry["src"]]["url"],
            "evidence": entry["evidence"],
            "action": entry["change"],
            "checked_at": checked_at,
        }
    if fid in CONFIRMED:
        entry = CONFIRMED[fid]
        return {
            "id": fid,
            "sport": fixture["sport"],
            "competition": fixture["competition"],
            "match": f"{fixture['home']} v {fixture['away']}" if fixture.get("away") else fixture["home"],
            "status": "confirmed",
            "source_name": SOURCES[entry["src"]]["name"],
            "source_url": SOURCES[entry["src"]]["url"],
            "evidence": entry["evidence"],
            "action": "No change required.",
            "checked_at": checked_at,
        }
    if fid in FLAGGED:
        entry = FLAGGED[fid]
        return {
            "id": fid,
            "sport": fixture["sport"],
            "competition": fixture["competition"],
            "match": f"{fixture['home']} v {fixture['away']}" if fixture.get("away") else fixture["home"],
            "status": "flagged",
            "source_name": SOURCES[entry["src"]]["name"],
            "source_url": SOURCES[entry["src"]]["url"],
            "evidence": entry["evidence"],
            "action": entry["change"],
            "checked_at": checked_at,
        }
    reason = ROW_REASON.get(fid) or NOT_RECHECKED_REASON.get(fixture["sport"], "Not re-fetched in this pass.")
    first = (fixture.get("sources") or [{}])[0]
    return {
        "id": fid,
        "sport": fixture["sport"],
        "competition": fixture["competition"],
        "match": f"{fixture['home']} v {fixture['away']}" if fixture.get("away") else fixture["home"],
        "status": "not_rechecked",
        "source_name": first.get("name", ""),
        "source_url": first.get("url", ""),
        "evidence": reason,
        "action": "Keeps its original status and source links; nothing in this pass re-read it.",
        "checked_at": checked_at,
    }


def build() -> dict:
    fixtures = json.loads((ROOT / "data" / "fixtures.json").read_text())["fixtures"]
    rows = [_status_row(f) for f in fixtures]
    counts = {key: 0 for key in ("confirmed", "corrected", "flagged", "not_rechecked")}
    for row in rows:
        counts[row["status"]] += 1
    sports = {}
    for row in rows:
        bucket = sports.setdefault(row["sport"], {"confirmed": 0, "corrected": 0, "flagged": 0, "not_rechecked": 0})
        bucket[row["status"]] += 1
    return {
        "generated": CHECKED_AT,
        "passes": [
            {"pass": "T20", "session": "72198d3e-olbg1", "checked_at": CHECKED_AT},
            {"pass": "T21", "session": "b95dbd01-olbg1", "checked_at": T21_CHECKED_AT},
        ],
        "method": (
            "Two passes, same method. Each row was matched against a freshly fetched governing-body page or endpoint. "
            "Participants, date, venue and (where the publisher states one) start time and game "
            "identifier were compared value by value. The T21 pass re-opened every page it could reach after the T20 "
            "pass and supersedes T20's verdict where it found something new; each row prints the pass that read it. "
            "A row is marked confirmed only when the "
            "official page was actually read in this pass, corrected only when the page settles "
            "the value unambiguously, and flagged when the page disagrees or cannot decide it."
        ),
        "sources": SOURCES,
        "summary": {"rows": len(rows), **counts},
        "by_sport": sports,
        "rows": rows,
        "findings": [
            {
                **{k: (v.format(refetched=counts["confirmed"] + counts["corrected"] + counts["flagged"],
                               not_rechecked=counts["not_rechecked"]) if isinstance(v, str) else v)
                   for k, v in f.items()},
                "source_name": SOURCES[f["source"]]["name"],
                "source_url": SOURCES[f["source"]]["url"],
            }
            for f in FINDINGS
        ],
    }


def write_report(doc: dict) -> None:
    s = doc["summary"]
    lines = [
        "# Live official-source re-verification (passes T20 + T21)",
        "",
        f"**Pass run:** {doc['generated']} · **Rows in dataset:** {s['rows']}",
        "",
        "Two passes on 2026-10-21 re-fetched the governing-body pages themselves and compared",
        "them value by value with the published rows: T20 (session `72198d3e-olbg1`, 07:05Z) and",
        "T21 (session `b95dbd01-olbg1`, 09:05Z). Where the second read found something the first",
        "did not, the second read is the one shown, and each row names the pass that read it.",
        "",
        "## Result",
        "",
        "| Outcome | Rows | Meaning |",
        "|---|---|---|",
        f"| Confirmed | {s['confirmed']} | Official page re-fetched; participants, date, venue and published start/ID all match. |",
        f"| Corrected | {s['corrected']} | Official page disagreed and settled the value; dataset source amended. |",
        f"| Flagged | {s['flagged']} | Official page disagrees or cannot decide; nothing changed, published for review. |",
        f"| Not re-checked | {s['not_rechecked']} | No official page re-read in this pass; reason listed per row. |",
        "",
        "A row is never marked confirmed because it *looks* right. Where the publisher blocks a",
        "text fetch (darts, tennis draws) or the site is client-rendered, the row is left as",
        "not re-checked and the reason is printed.",
        "",
        "## Corrections applied",
        "",
        "| Row | Correction | Official page |",
        "|---|---|---|",
    ]
    for row in doc["rows"]:
        if row["status"] in ("corrected", "flagged"):
            lines.append(
                f"| `{row['id']}` | {row['action']} | [{row['source_name']}]({row['source_url']}) |"
            )
    lines += [
        "",
        "## Findings",
        "",
    ]
    for f in doc["findings"]:
        lines += [
            f"### {f['id']} — {f['area']} ({f['severity']})",
            "",
            f["detail"],
            "",
            f"**Status:** {f['status']}",
            "",
            f"**Source:** [{f['source_name']}]({f['source_url']})",
            "",
        ]
    lines += [
        "## Per-row register",
        "",
        "| Row | Match | Competition | Outcome | What the official page said | Source |",
        "|---|---|---|---|---|---|",
    ]
    for row in doc["rows"]:
        lines.append(
            f"| `{row['id']}` | {row['match']} | {row['competition']} | {row['status']} | "
            f"{row['evidence']} {row['action']} | [{row['source_name']}]({row['source_url']}) |"
        )
    lines += [
        "",
        "## Boundary of this pass",
        "",
        "* No network request is made by the validator. The reads recorded here were made by hand",
        "  during the session and are dated; a publisher can change a page afterwards.",
        "* Model prices remain our own estimates. This pass verified *facts*, not the model's",
        "  judgement, and it deliberately did not re-price any match.",
        "* Snapshot drift (F-V5) is expected whenever a live table is quoted: the published value is",
        "  the value at pricing time, and the row says so.",
        "",
    ]
    (ROOT / "reports" / "LIVE_VERIFICATION.md").write_text("\n".join(lines), encoding="utf-8")


VERDICT_FOR_STATUS = {
    "confirmed": "confirmed",
    "corrected": "corrected",
    "flagged": "conflict",
    "not_rechecked": "not-rechecked",
}


def stamp_fixtures(doc: dict) -> None:
    """Write one verification block onto every fixture row.

    The register in ``data/verification.json`` is the audit record; the per-row
    block is what the validator gates on and what a reader sees next to the row.
    Both are generated from the same registers above, so they cannot disagree,
    and the operation is idempotent (re-running replaces the block).
    """
    path = ROOT / "data" / "fixtures.json"
    payload = json.loads(path.read_text())
    by_id = {row["id"]: row for row in doc["rows"]}
    for fixture in payload["fixtures"]:
        row = by_id.get(fixture["id"])
        if not row:
            continue
        verdict = VERDICT_FOR_STATUS[row["status"]]
        if fixture.get("status") == "unverified" and verdict == "corrected":
            # The correction was to the row's own status, not to a fixture field.
            verdict = "unconfirmed"
        block = {
            "verdict": verdict,
            "checked_utc": row["checked_at"],
            "source": row["source_name"],
            "page": row["source_url"],
        }
        if verdict == "unconfirmed":
            block["evidence"] = (fixture.get("sources") or [{}])[0].get("url") or row["source_url"]
        elif verdict in ("confirmed", "corrected", "conflict"):
            block["evidence"] = row["source_url"]
            block["fields"] = (
                ["participants", "date", "start time", "venue"]
                if verdict == "confirmed"
                else ["participants", "date", "venue"]
            )
        else:
            block["evidence"] = f"Not re-read in this pass: {row['evidence']}"
            block["fields"] = []
        block["note"] = row["action"]
        fixture["verification"] = block
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    doc = build()
    (ROOT / "data" / "verification.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    stamp_fixtures(doc)
    write_report(doc)
    s = doc["summary"]
    print(
        f"Live verification register: {s['rows']} rows — {s['confirmed']} confirmed, "
        f"{s['corrected']} corrected, {s['flagged']} flagged, {s['not_rechecked']} not re-checked"
    )


if __name__ == "__main__":
    main()
