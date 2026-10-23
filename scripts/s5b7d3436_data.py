#!/usr/bin/env python3
"""Persist session 5b7d3436's fresh discovery and official-source observations.

This module contains observations, not predictions.  Running it rewrites only
this session's isolated JSON inputs.  Prices are derived separately by
s5b7d3436_lines.py.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "5b7d3436"
CAPTURE_AT = "2026-10-23T21:36:17Z"
EVIDENCE_EXPIRES_AT = "2026-10-24T03:36:17Z"
SESSION = "T5B7D"

SPORT_ORDER = [
    "Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts",
    "Baseball", "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing",
    "Handball", "Ice Hockey", "Basketball", "Rugby League",
]
SPORT_SLUGS = {
    "Golf": "golf", "Volleyball": "volleyball", "Rugby Union": "rugby-union",
    "Cricket": "cricket", "Snooker": "snooker", "Darts": "darts",
    "Baseball": "baseball", "Gaelic Sports": "gaelic-sports",
    "Greyhounds": "greyhounds", "Tennis": "tennis",
    "Motor Racing": "motor-racing", "Handball": "handball",
    "Ice Hockey": "ice-hockey", "Basketball": "basketball",
    "Rugby League": "rugby-league",
}
OLBG_ROUTES = {
    "Golf": ("Golf", 5), "Volleyball": ("Volleyball", 21),
    "Rugby Union": ("Rugby_Union", 9), "Cricket": ("Cricket", 7),
    "Snooker": ("Snooker", 8), "Darts": ("Darts", 15),
    "Baseball": ("Baseball", 12), "Gaelic Sports": ("Gaelic_Football", 25),
    "Greyhounds": ("Greyhounds", 28), "Tennis": ("Tennis", 3),
    "Motor Racing": ("Motor_Racing", 14), "Handball": ("Handball", 20),
    "Ice Hockey": ("Ice_Hockey", 13), "Basketball": ("Basketball", 4),
    "Rugby League": ("Rugby_League", 10),
}


def save(name: str, value) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def src(id: str, publisher: str, url: str, takeaway: str, *, official: bool = True,
        method: str = "direct fetch", final_url: str | None = None, status: str = "read") -> dict:
    return {
        "id": id, "publisher": publisher, "url": url, "official": official,
        "method": method, "status": status, "final_url": final_url,
        "registered_at": CAPTURE_AT,
        "timestamp_note": "Registration time after the session read; the retrieval tool did not expose an exact per-URL timestamp.",
        "takeaway": takeaway,
    }


SOURCES = [
    src("olbg-main", "OLBG", "https://www.olbg.com/betting-tips",
        "Main all-sports page displayed ‘No tips found’ and ‘No tournaments tips found’ at capture.", official=False),
    src("olbg-robots", "OLBG", "https://www.olbg.com/robots.txt",
        "Public crawling policy checked; disallowed API, events.php, sports, search and other routes were not used.", official=False),
    src("olbg-sitemap", "OLBG", "https://www.olbg.com/sitemap-betting-tips.xml",
        "Public betting-tip sitemap supplied canonical hub routes; chunk 0 carried 2026-10-23 lastmod values.", official=False),
    src("nhl-schedule-23", "NHL", "https://api-web.nhle.com/v1/schedule/2026-10-23",
        "Official schedule lists Montréal at Chicago at 2026-10-24T00:00:00Z and Tampa Bay at Colorado at 01:00:00Z."),
    src("nhl-schedule-24", "NHL", "https://api-web.nhle.com/v1/schedule/2026-10-24",
        "Official schedule reports 12 games; captured rows include Anaheim–Philadelphia, Los Angeles–New Jersey and San Jose–Boston."),
    src("nhl-standings", "NHL", "https://www.nhl.com/standings/2026-10-23/wildcard",
        "Official table supplied games, records, goals for/against, home/away splits and a 5:31 PM EDT update stamp for all ten priced clubs."),
    src("nhl-suzuki", "NHL", "https://www.nhl.com/news/montreal-canadiens-nick-suzuki-injury-status-update-october-22-2026",
        "Nick Suzuki is out 2–4 weeks with an upper-body injury; NHL reports 12 points in nine games and confirms the Chicago fixture time."),
    src("mlb-schedule", "MLB Stats API", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-28&hydrate=team,probablePitcher,venue",
        "Five World Series listings; Game 1 and Game 2 are Pre-Game/Scheduled at American Family Field with probable pitchers named."),
    src("mlb-al-standings", "MLB Stats API", "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026",
        "Tampa Bay regular-season line: 98–64, 736 runs scored and 650 allowed; standings update 2026-10-23T20:52:56Z."),
    src("mlb-nl-standings", "MLB Stats API", "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason&fields=records,teamRecords,team,name,wins,losses,gamesPlayed,runsScored,runsAllowed,records,splitRecords,wins,losses,type,pct",
        "Milwaukee regular-season line: 103–59, 832 runs scored and 618 allowed; home 55–26 and away 48–33."),
    src("nba-game", "NBA", "https://www.nba.com/game/nyk-vs-bos-0022600008",
        "Knicks at Celtics, Friday 23 October at 7:00 PM ET, TD Garden; official preview records both teams' opening losses and recent head-to-head results."),
    src("nba-standings-2025", "NBA", "https://www.nba.com/standings?Season=2025-26",
        "Official 2025–26 standings: Boston 56–26 (30–11 home), New York 53–29 (22–19 road). Used as historical context only, not as a current-season record."),
    src("nba-injury", "NBA Official", "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_05_15PM.pdf",
        "5:15 PM report: three Knicks two-way players questionable; Boston's Devin Carter out with illness."),
    src("nba-injury-portal", "NBA Official", "https://official.nba.com/nba-injury-report-2026-27-season/",
        "Official portal explains reporting requirements and links continually updated reports; latest captured link was 5:15 PM ET."),
    src("icc-match", "ICC", "https://www.icc-cricket.com/matches/271647/new-zealand-vs-india",
        "Official match centre lists New Zealand v India as an upcoming T20; its displayed ‘Your time’ clock does not establish a UTC start."),
    src("icc-team-news", "ICC", "https://www.icc-cricket.com/news/injury-blow-for-india-ahead-of-second-t20i-with-new-zealand",
        "India lead 1–0 after chasing 226; Ishan Kishan is out with a low-grade right adductor strain and Kumar Kushagra joins as cover. Saturday match at Hagley Oval."),
    src("wta-order", "WTA", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
        "Official Saturday order of play: [1] Elena Rybakina v [6] Diana Shnaider, not before 5:30 PM on Center Court; released 23 October at 4:07 PM."),
    src("wta-draw", "WTA", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf",
        "Official Ningbo main draw and withdrawal notes, released 23 October at 10:00 PM. Seed numbers are not treated as world rankings."),
    src("volleyball-fixtures", "League fixture platform", "https://www.tauronliga.pl/games/nocookies/1.html",
        "Explicitly lists PGE GiEK SKRA Bełchatów v PGE Projekt Warszawa on Saturday 24 October at 18:00, with match ID 1104819.",
        final_url="https://www.tauronliga.pl/games/nocookies/1.html"),
    src("urc-teams", "United Rugby Championship", "https://www.unitedrugby.com/latest/news/round-4-team-announcements/",
        "Leinster v Munster at Aviva Stadium, Saturday 24 October, KO 18:00 IRE & UK / 19:00 ITA & SA; full match squads published."),
    src("pdc-report", "PDC", "https://www.pdc.tv/news/2026/october/22/nine-dart-star-woodhouse-sets-up-van-veen-clash-dortmund/",
        "Official-domain extraction confirms Van Veen v Woodhouse in Saturday's afternoon session; Woodhouse hit a nine-darter in a 6–3 win and Van Veen won 6–4 with a 99.26 average.",
        method="official-domain web search extraction; direct page returned consent text"),
    src("cork-fixtures", "Cork GAA", "https://gaacork.ie/fixtures/",
        "Premier SFC final: Nemo Rangers v St Finbarrs, Sunday 25 October at 16:00, SuperValu Páirc Uí Chaoimh; referee David Murnane."),
    src("f1-schedule", "Formula 1", "https://www.formula1.com/en/latest/article/what-time-is-the-formula-1-2026-united-states-grand-prix-and-how-can-i-watch-it.5jZFEoK96n4tpbRzEJjRoH",
        "United States Grand Prix at Circuit of The Americas on Sunday 25 October at 15:00 local; qualifying is Saturday at 16:00 local."),
    src("kiel-preview", "THW Kiel", "https://thw-handball.de/bundesliga/2026/10/thw-kiel-handball-bundesliga-saison-2026-2027-hc-erlangen-vorbericht-auswaertsspiel/",
        "Club preview dated 22 October lists HC Erlangen v THW Kiel on Saturday at 18:00, PSD Bank Arena; Erlangen remain unbeaten at home."),
    src("pga-tee-times", "PGA TOUR", "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/tee-times",
        "Butterfield Bermuda Championship at Port Royal, 22–25 October; Round 2 was in progress at capture. No future head-to-head pairing was established."),
    src("wst-match", "World Snooker Tour", "https://www.wst.tv/match-centre/1966aeac-c5a8-4bda-97e7-3d80e391d64f",
        "Official match-centre listing shows Kyren Wilson v Sam Craigie in the Northern Ireland Open semi-finals on 24 October; displayed clock conflicts with the indexed official copy."),
    src("gbgb-schedule", "Greyhound Board of Great Britain", "https://www.gbgb.org.uk/racing/open-races/2025-category-one-schedule/",
        "Official Category One schedule lists the 270m Scurry Gold Cup and 480m Oaks at Dunstall Park on Saturday 24 October; runners and race times were blank in the captured table."),
    src("nrl-teams", "NRL", "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/",
        "Official Round 2 team lists: Papua New Guinea v Samoa, Saturday 24 October at 3:25 PM AEDT, Santos National Football Stadium; page updated 23 October at 7:06 PM."),
]

for sport, (route, number) in OLBG_ROUTES.items():
    observation = ("No tournament tips and no match listings rendered" if sport in {"Motor Racing", "Rugby League"}
                   else "No tips found rendered on the public hub")
    SOURCES.append(src(f"olbg-hub-{SPORT_SLUGS[sport]}", "OLBG",
                       f"https://www.olbg.com/betting-tips/{route}/{number}",
                       observation + "; this is discovery state, not official confirmation that no fixtures exist.", official=False))

SUBROUTES = [
    ("Ice Hockey", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/13"),
    ("Basketball", "https://www.olbg.com/betting-tips/Basketball/NBA/4"),
    ("Basketball", "https://www.olbg.com/betting-tips/Basketball/European/Euroleague/4"),
    ("Baseball", "https://www.olbg.com/betting-tips/Baseball/MLB/12"),
    ("Tennis", "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/3"),
]
for index, (sport, url) in enumerate(SUBROUTES, 1):
    SOURCES.append(src(f"olbg-subroute-{index}", "OLBG", url,
                       f"{sport} competition subroute displayed ‘No tips found’.", official=False))

EVENT_SAMPLES = {
    "Basketball": ("534842", "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/NY_Knicks_@_BOS_Celtics/4?event_id=534842"),
    "Ice Hockey": ("199984", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/MTL_Canadiens_@_CHI_Blackhawks/13?event_id=199984"),
    "Baseball": ("160789", "https://www.olbg.com/betting-tips/Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160789"),
    "Cricket": ("188832", "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/New_Zealand_vs_India_2nd_T20_Match/7?event_id=188832"),
    "Tennis": ("902163", "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Elena_Rybakina_vs_Diana_Shnaider/3?event_id=902163"),
    "Volleyball": ("36964", "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/PGE_Skra_Belchatow_vs_Projekt_Warszawa/21?event_id=36964"),
    "Rugby Union": ("609578", "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Leinster_v_Munster/9?event_id=609578"),
    "Darts": ("32385", "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Gian_van_Veen_vs_Luke_Woodhouse/15?event_id=32385"),
    "Gaelic Sports": ("3530", "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530"),
    "Motor Racing": ("913", "https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/USA_Grand_Prix/14?event_id=913"),
    "Handball": ("12091", "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/HC_Erlangen_vs_THW_Kiel/20?event_id=12091"),
}
for sport, (event_id, url) in EVENT_SAMPLES.items():
    SOURCES.append(src(f"olbg-event-{event_id}", "OLBG", url,
                       f"Every displayed selection on sampled {sport} event {event_id} was labeled Expired; no currently available market was established.", official=False))


def nhl_inputs(gp: int, wins: int, losses: int, ot: int, gf: int, ga: int) -> dict:
    return {"games": gp, "wins": wins, "losses": losses, "ot_losses": ot,
            "goals_for": gf, "goals_against": ga}


def mlb_inputs(wins: int, losses: int, rs: int, ra: int) -> dict:
    return {"games": wins + losses, "wins": wins, "losses": losses,
            "runs_scored": rs, "runs_allowed": ra}


def fixture(id: str, sport: str, competition: str, event: str, *, home=None, away=None,
            date=None, start_utc=None, start_local=None, state="upcoming", venue=None,
            sources=(), facts=(), availability=(), inputs=None, flags=(), gaps=(),
            olbg_event=None, utc_basis=None) -> dict:
    return {
        "id": id, "sport": sport, "slug": SPORT_SLUGS[sport], "competition": competition,
        "event": event, "home": home, "away": away, "date": date,
        "start_utc": start_utc, "start_local": start_local, "start_utc_basis": utc_basis,
        "state": state, "venue": venue, "source_ids": list(sources),
        "facts": list(facts), "availability": list(availability), "inputs": inputs,
        "flags": list(flags), "market_gaps": list(gaps),
        "olbg_event_id": olbg_event,
        "olbg_state": "expired" if olbg_event else "no_open_listing",
        "open_olbg_market": False, "registered_at": CAPTURE_AT,
        "evidence_expires_at": EVIDENCE_EXPIRES_AT,
    }


FIXTURES = [
    fixture("GF01", "Golf", "PGA TOUR · Butterfield Bermuda Championship",
            "Butterfield Bermuda Championship · tournament field", date="2026-10-25",
            start_local="Tournament runs 22–25 October; Round 2 was in progress at capture",
            state="in_progress", venue="Port Royal Golf Course, Southampton, Bermuda",
            sources=["pga-tee-times"],
            facts=["The official page showed Round 2 in progress and the 22–25 October tournament window."],
            flags=["No future official head-to-head pairing was established; the tournament row is not a two-player match."],
            gaps=["Outright, head-to-head, round-score and player markets withheld: no supported future pairing or complete current leaderboard was captured."]),

    fixture("VB01", "Volleyball", "Polish league fixture · match 1104819",
            "PGE GiEK SKRA Bełchatów v PGE Projekt Warszawa",
            home="PGE GiEK SKRA Bełchatów", away="PGE Projekt Warszawa", date="2026-10-24",
            start_local="Saturday 24 October, 18:00 (league-displayed local time)",
            sources=["volleyball-fixtures"], olbg_event="36964",
            facts=["The schedule explicitly displays both clubs, Saturday 24 October at 18:00 and match ID 1104819."],
            flags=["A PlusLiga request redirected to tauronliga.pl; the explicit fixture text was retained and the cross-domain routing is flagged.",
                   "The official page did not expose a UTC offset in the captured text; UTC remains blank."],
            gaps=["Winner, set handicap, total sets and exact score withheld: no compatible current team-strength dataset was captured.",
                  "Player props withheld: no official availability and player-statistics package was captured."]),

    fixture("RU01", "Rugby Union", "United Rugby Championship · Round 4",
            "Leinster Rugby v Munster Rugby", home="Leinster Rugby", away="Munster Rugby",
            date="2026-10-24", start_local="Saturday 24 October, KO 18:00 IRE & UK / 19:00 ITA & SA",
            venue="Aviva Stadium, Dublin", sources=["urc-teams"], olbg_event="609578",
            facts=["Dan Sheehan captains Leinster; Joey Carbery and Jamison Gibson-Park are the named half-backs.",
                   "Tadhg Beirne captains Munster; Charlie O’Shea and Craig Casey are the named half-backs."],
            availability=["Official starting teams and replacements are published; no injury conclusion is inferred from selection."],
            flags=["UTC is not printed by the official article; the two official regional clocks are preserved instead of substituting an OLBG clock."],
            gaps=["Winner, points handicap and total points withheld pending a compatible current table/scoring dataset.",
                  "Try-scorer and player markets withheld; squad publication alone does not supply a scoring baseline."]),

    fixture("CR01", "Cricket", "India tour of New Zealand · 2nd T20I",
            "New Zealand v India", home="New Zealand", away="India", date="2026-10-24",
            start_local="Saturday 24 October; ICC match list displays 03:00 ‘Your time’ (timezone unresolved)",
            venue="Hagley Oval, Christchurch", sources=["icc-match", "icc-team-news"], olbg_event="188832",
            facts=["India lead the five-match series 1–0 after chasing 226 with four wickets in hand and two deliveries remaining."],
            availability=["Ishan Kishan is ruled out with a low-grade right adductor strain; Kumar Kushagra has been added as cover."],
            flags=["The ICC page's ‘Your time’ value cannot be converted responsibly without an exposed timezone; UTC remains blank."],
            gaps=["Match winner, innings handicap and match/innings totals withheld: no compatible current team and venue scoring baseline was captured.",
                  "Player props withheld despite team news because no supported player-market baseline was established."]),

    fixture("SN01", "Snooker", "BetVictor Northern Ireland Open · semi-final",
            "Kyren Wilson v Sam Craigie", home="Kyren Wilson", away="Sam Craigie", date="2026-10-24",
            start_local="24 October; direct official fetch displays 08:00 while the official-domain indexed copy displays 12:00",
            sources=["wst-match"],
            facts=["The official match-centre listing identifies a Northern Ireland Open semi-final between Kyren Wilson and Sam Craigie."],
            flags=["Official display times conflict (08:00 direct fetch versus 12:00 indexed copy); UTC and a definitive local start remain blank.",
                   "The fetched parent match page carries unrelated 2023 metadata; that metadata was not assigned to this semi-final."],
            gaps=["Match winner, frame handicap and total frames withheld: no current paired player-statistics package was captured.",
                  "Century and highest-break markets withheld: no supported market baseline was established."]),

    fixture("DA01", "Darts", "Machineseeker European Championship · Round 2",
            "Gian van Veen v Luke Woodhouse", home="Gian van Veen", away="Luke Woodhouse", date="2026-10-24",
            start_local="Saturday afternoon session, 13:00–17:00 CEST; individual match time not stated",
            venue="Westfalenhalle, Dortmund", sources=["pdc-report"], olbg_event="32385",
            facts=["Woodhouse won 6–3 against Dirk van Duijvenbode with a nine-dart leg and an average above 99.",
                   "Van Veen won 6–4 against Andrew Gilding with a 99.26 average."],
            flags=["The source establishes a four-match afternoon session, not an exact individual start; no precise UTC start is assigned.",
                   "The direct page returned consent text; substantive details come from official-domain search extraction and are labeled accordingly."],
            gaps=["Match winner, leg handicap and total legs withheld: two match averages are insufficient for a calibrated best-of-19 probability.",
                  "180s and highest-checkout markets withheld: no compatible current player distribution was captured."]),

    fixture("BB01", "Baseball", "2026 World Series · Game 1",
            "Tampa Bay Rays at Milwaukee Brewers", home="Milwaukee Brewers", away="Tampa Bay Rays",
            date="2026-10-23", start_utc="2026-10-24T00:00:00Z", start_local="Official MLB gameDate in UTC",
            venue="American Family Field", sources=["mlb-schedule", "mlb-al-standings", "mlb-nl-standings"],
            olbg_event="160789", utc_basis="Official MLB gameDate field",
            facts=["MLB status is Pre-Game; probable pitchers are Nick Martinez for Tampa Bay and Jacob Misiorowski for Milwaukee.",
                   "Regular-season totals: Tampa Bay 98–64, 736 runs for/650 against; Milwaukee 103–59, 832 for/618 against."],
            inputs={"kind": "mlb", "home": mlb_inputs(103, 59, 832, 618), "away": mlb_inputs(98, 64, 736, 650)},
            flags=["Probable pitchers are named, but no current pitcher-statistics package was captured; the fair-line calculation uses team totals only."],
            gaps=["First-five innings, pitcher props and player props withheld: probable-pitcher names without compatible current statistics are insufficient."]),

    fixture("BB02", "Baseball", "2026 World Series · Game 2",
            "Tampa Bay Rays at Milwaukee Brewers · Game 2", home="Milwaukee Brewers", away="Tampa Bay Rays",
            date="2026-10-24", start_utc="2026-10-25T00:00:00Z", start_local="Official MLB gameDate in UTC",
            venue="American Family Field", sources=["mlb-schedule", "mlb-al-standings", "mlb-nl-standings"],
            utc_basis="Official MLB gameDate field",
            facts=["MLB status is Scheduled; probable pitchers are Drew Rasmussen for Tampa Bay and Logan Henderson for Milwaukee.",
                   "The same official regular-season team totals are used; no Game 1 result is assumed."],
            inputs={"kind": "mlb", "home": mlb_inputs(103, 59, 832, 618), "away": mlb_inputs(98, 64, 736, 650)},
            flags=["No Game 1 result or current pitcher-statistics package was available at capture; team totals are the only numerical inputs."],
            gaps=["First-five innings, pitcher props and player props withheld pending compatible current pitching statistics and Game 1 availability news."]),

    fixture("GS01", "Gaelic Sports", "Cork Premier Senior Football Championship · final",
            "Nemo Rangers v St Finbarrs", home="Nemo Rangers", away="St Finbarrs", date="2026-10-25",
            start_local="Sunday 25 October, 16:00 (Cork GAA display)",
            venue="SuperValu Páirc Uí Chaoimh", sources=["cork-fixtures"], olbg_event="3530",
            facts=["Cork GAA lists the Premier SFC final and referee David Murnane."],
            flags=["No UTC offset was exposed in the captured official fixture text; UTC remains blank."],
            gaps=["Winner, points handicap and total points withheld: no compatible current club scoring and availability dataset was captured."]),

    fixture("GH01", "Greyhounds", "GBGB Category One · Dunstall Park finals",
            "Scurry Gold Cup (270m) and Premier Greyhound Racing Oaks (480m)", date="2026-10-24",
            start_local="Saturday 24 October; race times not present in the captured GBGB schedule",
            venue="Dunstall Park", sources=["gbgb-schedule"],
            facts=["The official schedule lists both Category One events and their distances; winner and winning-time cells are blank."],
            flags=["No official final runner list, trap draw or race time was captured; this is an event-level row, not a runner matchup."],
            gaps=["Race winner, forecast/tricast and trap-related markets withheld: runners, traps and current sectional form were not established."]),

    fixture("TN01", "Tennis", "WTA Ningbo Open · singles semi-final",
            "Elena Rybakina v Diana Shnaider", home="Elena Rybakina", away="Diana Shnaider", date="2026-10-24",
            start_local="Saturday 24 October, not before 17:30 on Center Court (official order of play)",
            venue="Center Court, Ningbo, China", sources=["wta-order", "wta-draw"], olbg_event="902163",
            facts=["The official order of play identifies [1] Rybakina against [6] Shnaider after the preceding semi-final.",
                   "The draw records withdrawals including Iga Świątek and Marta Kostyuk; no inference is made about either semi-finalist's availability."],
            availability=["Both named semi-finalists remain in the official order of play; no additional health claim is made."],
            flags=["The order of play gives a local ‘not before’ time and warns matches may move; no fixed UTC start is assigned.",
                   "Numbers in the draw's seeded-player table are treated as seeds, not substituted for current world rankings."],
            gaps=["Match winner, game/set handicap and total games withheld: no compatible current ranking and surface-performance package was captured.",
                  "Player aces and other props withheld: no supported player-market baseline was established."]),

    fixture("MR01", "Motor Racing", "Formula 1 · United States Grand Prix",
            "United States Grand Prix · race field", date="2026-10-25",
            start_local="Sunday 25 October, 15:00 local; qualifying Saturday 24 October at 16:00 local",
            venue="Circuit of The Americas, Austin", sources=["f1-schedule"], olbg_event="913",
            facts=["The official preview says Max Verstappen won in Singapore and Kimi Antonelli leads the championship by 102 points entering Austin."],
            flags=["Qualifying had not established a final grid in the captured evidence; local time is preserved without an invented UTC conversion."],
            gaps=["Race winner, podium, head-to-head and qualifying markets withheld: final grid and a compatible current driver-performance package were not captured."]),

    fixture("HB01", "Handball", "Handball-Bundesliga · Round 10",
            "HC Erlangen v THW Kiel", home="HC Erlangen", away="THW Kiel", date="2026-10-24",
            start_local="Saturday 24 October, 18:00 in the 22 October club preview",
            venue="PSD Bank Arena, Nürnberg", sources=["kiel-preview"], olbg_event="12091",
            facts=["Erlangen are unbeaten at home in the preview: 28–28 v Hannover, 29–28 v Bergischer HC and 33–32 v MT Melsungen."],
            flags=["Older official schedule snippets displayed 19:00 while the newer 22 October preview says 18:00; the newer preview is shown and the discrepancy retained.",
                   "UTC remains blank because the captured preview does not print an offset."],
            gaps=["Winner (including draw), goal handicap and total goals withheld: a complete paired current table/scoring dataset was not captured.",
                  "Player props withheld: no official match availability and player-statistics package was captured."]),

    fixture("IH01", "Ice Hockey", "NHL · regular season",
            "Montréal Canadiens at Chicago Blackhawks", home="Chicago Blackhawks", away="Montréal Canadiens",
            date="2026-10-23", start_utc="2026-10-24T00:00:00Z", start_local="Friday 23 October, 8:00 PM ET",
            venue="United Center", sources=["nhl-schedule-23", "nhl-standings", "nhl-suzuki"],
            olbg_event="199984", utc_basis="Official NHL startTimeUTC field",
            facts=["Official standings: Montréal 4–3–2 with 30 GF/34 GA in nine; Chicago 3–6–0 with 21 GF/36 GA in nine."],
            availability=["Nick Suzuki is out 2–4 weeks with an upper-body injury; he had 12 points in nine games."],
            inputs={"kind": "nhl", "home": nhl_inputs(9, 3, 6, 0, 21, 36), "away": nhl_inputs(9, 4, 3, 2, 30, 34)},
            flags=["Starting goalies and complete lineup changes were not captured; fair lines remain experimental and cannot become High picks.",
                   "Suzuki's confirmed absence is disclosed but not assigned an invented numerical adjustment in the team-total calculation."],
            gaps=["Starting-goalie and player props withheld: no compatible current goalie/lineup dataset was captured."]),

    fixture("IH02", "Ice Hockey", "NHL · regular season",
            "Tampa Bay Lightning at Colorado Avalanche", home="Colorado Avalanche", away="Tampa Bay Lightning",
            date="2026-10-23", start_utc="2026-10-24T01:00:00Z", start_local="Official NHL startTimeUTC in UTC",
            venue="Ball Arena", sources=["nhl-schedule-23", "nhl-standings"], utc_basis="Official NHL startTimeUTC field",
            facts=["Official standings: Tampa Bay 7–2–0 with 31 GF/23 GA in nine; Colorado 5–4–1 with 41 GF/31 GA in ten."],
            inputs={"kind": "nhl", "home": nhl_inputs(10, 5, 4, 1, 41, 31), "away": nhl_inputs(9, 7, 2, 0, 31, 23)},
            flags=["Starting goalies and complete availability reports were not captured; fair lines remain experimental."],
            gaps=["Starting-goalie and player props withheld: no compatible current goalie/lineup dataset was captured."]),

    fixture("IH03", "Ice Hockey", "NHL · regular season · 24 October schedule",
            "Anaheim Ducks at Philadelphia Flyers", home="Philadelphia Flyers", away="Anaheim Ducks",
            date="2026-10-24", start_utc="2026-10-24T17:00:00Z", start_local="Official NHL startTimeUTC in UTC",
            sources=["nhl-schedule-24", "nhl-standings"], utc_basis="Official NHL startTimeUTC field",
            facts=["Official standings: Anaheim 4–6–0 with 27 GF/33 GA in ten; Philadelphia 3–6–3 with 20 GF/37 GA in twelve."],
            inputs={"kind": "nhl", "home": nhl_inputs(12, 3, 6, 3, 20, 37), "away": nhl_inputs(10, 4, 6, 0, 27, 33)},
            flags=["Venue, starting goalies and complete availability were not established in the captured evidence; venue is blank and lines remain experimental."],
            gaps=["Starting-goalie and player props withheld: no compatible current goalie/lineup dataset was captured."]),

    fixture("IH04", "Ice Hockey", "NHL · regular season · 24 October schedule",
            "Los Angeles Kings at New Jersey Devils", home="New Jersey Devils", away="Los Angeles Kings",
            date="2026-10-24", start_utc="2026-10-24T19:30:00Z", start_local="Official NHL startTimeUTC in UTC",
            sources=["nhl-schedule-24", "nhl-standings"], utc_basis="Official NHL startTimeUTC field",
            facts=["Official standings: Los Angeles 2–4–2 with 20 GF/29 GA in eight; New Jersey 6–4–0 with 33 GF/31 GA in ten."],
            inputs={"kind": "nhl", "home": nhl_inputs(10, 6, 4, 0, 33, 31), "away": nhl_inputs(8, 2, 4, 2, 20, 29)},
            flags=["Venue, starting goalies and complete availability were not established in the captured evidence; venue is blank and lines remain experimental."],
            gaps=["Starting-goalie and player props withheld: no compatible current goalie/lineup dataset was captured."]),

    fixture("IH05", "Ice Hockey", "NHL · regular season · 24 October schedule",
            "San Jose Sharks at Boston Bruins", home="Boston Bruins", away="San Jose Sharks",
            date="2026-10-24", start_utc="2026-10-24T23:00:00Z", start_local="Official NHL startTimeUTC in UTC",
            sources=["nhl-schedule-24", "nhl-standings"], utc_basis="Official NHL startTimeUTC field",
            facts=["Official standings: San Jose 6–4–1 with 33 GF/37 GA in eleven; Boston 8–2–1 with 42 GF/22 GA in eleven."],
            inputs={"kind": "nhl", "home": nhl_inputs(11, 8, 2, 1, 42, 22), "away": nhl_inputs(11, 6, 4, 1, 33, 37)},
            flags=["Venue, starting goalies and complete availability were not established in the captured evidence; venue is blank and lines remain experimental."],
            gaps=["Starting-goalie and player props withheld: no compatible current goalie/lineup dataset was captured."]),

    fixture("BK01", "Basketball", "NBA · regular season",
            "New York Knicks at Boston Celtics", home="Boston Celtics", away="New York Knicks",
            date="2026-10-23", start_utc="2026-10-23T23:00:00Z", start_local="Friday 23 October, 7:00 PM ET",
            venue="TD Garden, Boston", sources=["nba-game", "nba-standings-2025", "nba-injury"],
            olbg_event="534842", utc_basis="Official ET start converted with America/New_York (EDT, UTC−4 on this date)",
            facts=["Both teams are 0–1 after opening losses: New York lost 106–100 and Boston lost 121–113.",
                   "Historical context only: official 2025–26 standings were Boston 56–26 and New York 53–29."],
            availability=["New York lists Jaden Akins, Kevin McCullar Jr. and Tyler Nickel questionable as two-way players; Boston lists Devin Carter out with illness."],
            flags=["Current rosters changed materially in the official preview, so last-season records are not promoted into a current moneyline price."],
            gaps=["Winner, spread and total points withheld: one current game per team and major roster changes do not provide a supportable paired scoring baseline.",
                  "Player props withheld: the injury report establishes listed statuses but not a current role/minutes baseline."]),

    fixture("RL01", "Rugby League", "2026 Men's Rugby League World Cup · Round 2",
            "Papua New Guinea v Samoa", home="Papua New Guinea", away="Samoa", date="2026-10-24",
            start_utc="2026-10-24T04:25:00Z", start_local="Saturday 24 October, 3:25 PM AEDT",
            venue="Santos National Football Stadium, Port Moresby", sources=["nrl-teams"],
            utc_basis="Official AEDT start converted at UTC+11",
            facts=["The NRL page publishes the fixture, venue and official team lists, with a 23 October 7:06 PM update stamp."],
            availability=["Official team lists are present; no additional injury inference is made from selection."],
            gaps=["Winner, points handicap and total points withheld: no compatible paired current scoring/strength dataset was captured.",
                  "Try-scorer markets withheld: squad lists alone do not establish a scoring distribution."]),
]

GLOBAL_FLAGS = [
    {"id": "G001", "severity": "scope", "title": "Empty hubs are not empty fixture lists",
     "detail": "The main page and 13 hubs rendered ‘No tips found’; Motor Racing and Rugby League rendered no tournament tips/matches. This is capture-time OLBG interface state, not official confirmation of absent or completed fixtures.", "source_ids": ["olbg-main"]},
    {"id": "G002", "severity": "blocking", "title": "Expired OLBG samples cannot release picks",
     "detail": "All 11 sampled event pages showed Expired on every displayed selection. Upcoming official fixtures do not reopen those listings, so no current OLBG market or publishable High pick is claimed.", "source_ids": [f"olbg-event-{v[0]}" for v in EVENT_SAMPLES.values()]},
    {"id": "G003", "severity": "data", "title": "OLBG popularity is not a probability",
     "detail": "Malformed ‘Most Popular Tip’ percentages and detailed tip counts were excluded from every calculation. Community selections are not calibrated probabilities or official availability evidence.", "source_ids": ["olbg-main"]},
    {"id": "G004", "severity": "provenance", "title": "Per-URL retrieval timestamps were not exposed",
     "detail": f"All source records carry registration time {CAPTURE_AT}; this is not represented as the exact network retrieval time or publisher update time. Source-provided update stamps are preserved separately in takeaways.", "source_ids": []},
    {"id": "G005", "severity": "audit", "title": "Historical desk claims were not recycled",
     "detail": "Earlier desk probabilities, fixtures, predictions and claimed pick counts were not accepted as fresh evidence. Historical URLs were used only as leads for new OLBG and official reads.", "source_ids": []},
    {"id": "G006", "severity": "audit", "title": "Canonical root describes an older brief",
     "detail": "The repository root still describes a 22 October, 17-sport release. This isolated desk covers exactly the current 15-sport brief; Australian Rules and eSports are excluded.", "source_ids": []},
    {"id": "G007", "severity": "audit", "title": "Coordination board requires targeted maintenance",
     "detail": "COORDINATION.md contains duplicated numbering and stale status rows. This session used an append-only claim and does not infer ownership from stale ‘in progress’ text.", "source_ids": []},
    {"id": "G008", "severity": "retrieval", "title": "NBA report discovery required the official portal",
     "detail": "A guessed 6:00 PM PDF returned AccessDenied. The official injury-report portal was then read and its actual latest captured link, 5:15 PM, supplied the team statuses.", "source_ids": ["nba-injury-portal", "nba-injury"]},
    {"id": "G009", "severity": "retrieval", "title": "Player endpoints were not substituted for team statistics",
     "detail": "NHL club-stats responses contained player statistics, not team standings. They were excluded; NHL's official standings table supplies every numerical hockey input.", "source_ids": ["nhl-standings"]},
    {"id": "G010", "severity": "retrieval", "title": "PDC consent wall limited direct extraction",
     "detail": "The direct PDC article returned consent text. The official-domain search result supplied the article's fixture, session and recent-result text; that method is labeled rather than presented as a clean direct-page parse.", "source_ids": ["pdc-report"]},
]


def main() -> None:
    assert set(SPORT_ORDER) == set(SPORT_SLUGS) == set(OLBG_ROUTES)
    assert len(SPORT_ORDER) == 15
    assert {f["sport"] for f in FIXTURES} == set(SPORT_ORDER)
    source_ids = {s["id"] for s in SOURCES}
    assert len(source_ids) == len(SOURCES)
    for f in FIXTURES:
        assert set(f["source_ids"]) <= source_ids, f["id"]
        if f["olbg_event_id"]:
            assert f"olbg-event-{f['olbg_event_id']}" in source_ids
    save("sources.json", {"session": SESSION, "registered_at": CAPTURE_AT, "count": len(SOURCES), "sources": SOURCES})
    save("fixtures.json", {"session": SESSION, "registered_at": CAPTURE_AT,
                           "evidence_expires_at": EVIDENCE_EXPIRES_AT,
                           "sports": SPORT_ORDER, "count": len(FIXTURES), "fixtures": FIXTURES})
    discovery = []
    for sport in SPORT_ORDER:
        route, number = OLBG_ROUTES[sport]
        event_id, event_url = EVENT_SAMPLES.get(sport, (None, None))
        discovery.append({
            "sport": sport, "slug": SPORT_SLUGS[sport], "olbg_id": number,
            "hub_url": f"https://www.olbg.com/betting-tips/{route}/{number}",
            "hub_state": "no_tournament_or_matches" if sport in {"Motor Racing", "Rugby League"} else "no_tips_found",
            "event_id": event_id, "event_url": event_url,
            "event_state": "expired" if event_id else "not_sampled",
            "open_market_established": False, "registered_at": CAPTURE_AT,
        })
    save("discovery.json", {"session": SESSION, "registered_at": CAPTURE_AT,
                            "main_url": "https://www.olbg.com/betting-tips",
                            "main_state": "no_tips_found",
                            "subroutes": [{"sport": s, "url": u, "state": "no_tips_found"} for s, u in SUBROUTES],
                            "count": len(discovery), "open_markets": 0, "rows": discovery})
    flags = list(GLOBAL_FLAGS)
    for f in FIXTURES:
        for index, detail in enumerate(f["flags"], 1):
            flags.append({"id": f"{f['id']}-F{index}", "severity": "fixture", "title": f"{f['id']} · {f['event']}",
                          "detail": detail, "source_ids": f["source_ids"], "fixture_id": f["id"]})
        for index, detail in enumerate(f["market_gaps"], 1):
            flags.append({"id": f"{f['id']}-M{index}", "severity": "pricing", "title": f"{f['id']} · markets withheld",
                          "detail": detail, "source_ids": f["source_ids"], "fixture_id": f["id"]})
    save("flagged.json", {"session": SESSION, "registered_at": CAPTURE_AT, "count": len(flags), "flags": flags})
    print(f"Wrote {len(SOURCES)} sources, {len(FIXTURES)} fixtures, {len(discovery)} discovery rows and {len(flags)} flags")


if __name__ == "__main__":
    main()
