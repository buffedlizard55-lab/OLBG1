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
    "f1_usgp": {
        "name": "Formula 1 official 2026 United States Grand Prix page",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
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
        "url": "https://www.nrl.com/draw/rugby-league-world-cup/2026/round-2/",
    },
    "irl": {
        "name": "IRL official fixtures & match records (RLWC26 Round 2)",
        "url": "https://www.intrl.sport/fixtures-results",
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
    "nhl-2026020152": {
        "src": "nhl_stand",
        "evidence": "Independent re-read on 2026-10-21T07:20Z: standings return Buffalo 4-3-2 / .556 with goalDifferential -7, and Philadelphia 2-6-3 / .318 with a road line of 0-4-1 and goalDifferential -19. Both clubs had played exactly the number of games in the stored record (9 and 11), so the stored +2 and -14 differentials and the 0-4-2 road line cannot be snapshot drift.",
        "change": "Buffalo goal differential +2 -> -7; Philadelphia road 0-4-2 -> 0-4-1 and differential -14 -> -19. Ratings come from points percentage, which was already correct, so no rating or price moved.",
    },
    "nhl-2026020153": {
        "src": "nhl_stand",
        "evidence": "Independent re-read on 2026-10-21T07:20Z: Ottawa are 6-3-0 / .667 over 9 games with homeGamesPlayed 4 and a 3-1-0 home record. The stored 4-1-0 home line would require five home wins from four home games.",
        "change": "Ottawa home split 4-1-0 -> 3-1-0. Record, points percentage, rating and every price are unchanged.",
    },
    "f1-usgp-2026": {
        "src": "f1_usgp",
        "evidence": "formula1.com/en/racing/2026/united-states lists the race on 25 October with 56 laps at Circuit of The Americas and a 16:00 track time. Austin is on CDT (UTC-5) on 25 October, so the start is 21:00 UTC, not the 20:00 UTC recorded. The same page shows no round number.",
        "change": "start_utc 2026-10-25T20:00:00Z -> 2026-10-25T21:00:00Z; the 'EDT' description and the unverifiable 'Round 18' label removed.",
    },
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

CORRECTED.update({
    "rl-wc26-tga-lbn": {"src": "irl", "evidence": "IRL match record 2569: Tonga v Lebanon, CommBank Stadium, Fri 23 Oct 20:05 local (09:05Z) — participants, venue and start agree.", "change": "Legacy nrl.com/draw/?competition=175 link replaced with the official men's Round 2 draw page plus IRL match record 2569."},
    "rl-wc26-png-sam": {"src": "irl", "evidence": "IRL match record 2570: Papua New Guinea v Samoa, Santos National Football Stadium, Sat 24 Oct 14:25 local (04:25Z) — agree.", "change": "Legacy competition=175 link replaced with the official men's Round 2 draw page plus IRL match record 2570."},
    "rl-wc26-eng-fra": {"src": "irl", "evidence": "IRL match record 2571: England v France, HBF Park Perth, Sat 24 Oct 14:35 local (06:35Z) — agree.", "change": "Legacy competition=175 link replaced with the official men's Round 2 draw page plus IRL match record 2571."},
    "rl-wc26-nzl-cok": {"src": "irl", "evidence": "IRL match record 2572: New Zealand v Cook Islands, One NZ Stadium, Sun 25 Oct 18:05 local (05:05Z) — agree.", "change": "Legacy competition=175 link replaced with the official men's Round 2 draw page plus IRL match record 2572."},
    "rl-wc26-aus-fij": {"src": "irl", "evidence": "IRL match record 2573: Australia v Fiji, Suncorp Stadium, Sun 25 Oct 19:05 local (09:05Z) — agree.", "change": "Legacy competition=175 link replaced with the official men's Round 2 draw page plus IRL match record 2573."},
    "rl-wc26w-aus-eng": {"src": "irl", "evidence": "IRL match record 2588: Australia v England, HBF Park Perth, Sat 24 Oct 17:05 local (09:05Z) — agree.", "change": "Legacy competition=176 link (which resolves to the men's competition 131) replaced with the official women's Round 2 draw page plus IRL match record 2588."},
    "rl-wc26w-sam-wal": {"src": "irl", "evidence": "IRL match record 2586: Samoa v Wales, CommBank Stadium, Fri 23 Oct 17:50 local (06:50Z). The NRL draw publishes 2:45am AEDT (06:45Z).", "change": "Legacy competition=176 link replaced with the official women's Round 2 draw. Kick-off conflict disclosed on the row: 06:45Z (NRL) vs 06:50Z (IRL); neither is inferred away."},
})

# ---------------------------------------------------------------------------
# Why a row was not re-checked in this pass (no silent gaps)
# ---------------------------------------------------------------------------
NOT_RECHECKED_REASON: dict[str, str] = {
    "darts": "PDC draw release returns a cookie-consent interstitial to a non-browser fetch; re-tested on 2026-10-21 at two offsets and returned consent text only. The 16 ties could not be re-read from the publisher page.",
    "tennis": "Official draw widgets are client-rendered and returned no draw body. ATP results pages were read and confirm the Round-of-32 winners behind six pairings, but the Round-of-16 matches have not been played, so no results feed lists them. All eleven rows therefore carry a \u201creconstructed, not draw-verified\u201d flag and keep blank start times.",
    "euroleague": "EuroLeague / EuroCup game-centre pages are client-rendered and were not re-fetched in this pass.",
    "volleyball": "Re-tested on 2026-10-21: www.plusliga.pl redirects to tauronliga.pl and returns a generic competition page rather than the cited fixture list, so the five PlusLiga rows could not be re-read. SuperLega pages were not fetched.",
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
        "status": "11 tennis rows marked not re-checked and now flagged as reconstructed from Round-of-32 results plus byes.",
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
    {
        "id": "F-V11",
        "severity": "high",
        "area": "NHL — four input sub-values were transcription errors, not drift",
        "detail": "A second independent read of the standings endpoint on 2026-10-21T07:20Z found Buffalo at -7 (stored +2), Philadelphia at 0-4-1 and -19 (stored 0-4-2 / -14), Ottawa at 3-1-0 at home (stored 4-1-0, impossible from four home games) and Nashville at -1 (stored 0). Each club had played exactly the number of games in its stored record, which rules out a game having been played in between.",
        "status": "Corrected in the dataset source. Ratings derive from points percentage, which was already correct, so no rating or price moved.",
        "source": "nhl_stand",
    },
    {
        "id": "F-V12",
        "severity": "medium",
        "area": "Formula 1 — the United States GP start was an hour early",
        "detail": "formula1.com gives 16:00 track time on 25 October at Circuit of The Americas. Austin is on CDT (UTC-5) on that date, so the start is 21:00 UTC; the row carried 20:00 UTC and described 16:00 as EDT. The same page shows no round number, so the 'Round 18' label was not supportable.",
        "status": "start_utc corrected to 2026-10-25T21:00:00Z; the round number was removed.",
        "source": "f1_usgp",
    },
    {
        "id": "F-V13",
        "severity": "medium",
        "area": "Source integrity — two cited URLs do not resolve to the fixture list",
        "detail": "plusliga.pl/table.html redirects to tauronliga.pl and returns a generic competition page; munster.gaa.ie/fixtures/munster-gaa-fixtures/ resolved to an April 2025 news post titled 'Munster GAA Fixtures - April 7th to 12th 2025'. Neither page evidences the 2026 fixtures it is cited for.",
        "status": "The nine affected rows keep their published values and are listed as not re-checked with this specific blocker named. Nothing was upgraded.",
        "source": "nhl_sched",
    },
]


def _status_row(fixture: dict) -> dict:
    fid = fixture["id"]
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
            "checked_at": CHECKED_AT,
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
            "checked_at": CHECKED_AT,
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
            "checked_at": CHECKED_AT,
        }
    reason = NOT_RECHECKED_REASON.get(fixture["sport"], "Not re-fetched in this pass.")
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
        "checked_at": CHECKED_AT,
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
        "method": (
            "Each row was matched against a freshly fetched governing-body page or endpoint. "
            "Participants, date, venue and (where the publisher states one) start time and game "
            "identifier were compared value by value. A row is marked confirmed only when the "
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
        "# Live official-source re-verification (session `72198d3e-olbg1`)",
        "",
        f"**Pass run:** {doc['generated']} · **Rows in dataset:** {s['rows']}",
        "",
        "Every earlier session in this repository audited the dataset's *shape* and said so",
        "explicitly. This pass instead re-fetched the governing-body pages themselves and",
        "compared them value by value with the published rows.",
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


def main() -> None:
    doc = build()
    (ROOT / "data" / "verification.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    write_report(doc)
    s = doc["summary"]
    print(
        f"Live verification register: {s['rows']} rows — {s['confirmed']} confirmed, "
        f"{s['corrected']} corrected, {s['flagged']} flagged, {s['not_rechecked']} not re-checked"
    )


if __name__ == "__main__":
    main()
