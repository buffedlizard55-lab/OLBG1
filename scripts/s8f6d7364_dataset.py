#!/usr/bin/env python3
"""T66 / session 8f6d7364-olbg1 — dataset builder.

Emits data/8f6d7364/{fixtures.json,sources.json,flagged.json,inputs.json}.

Every fixture value below was read from the official page named in its
`sources` list by THIS session through the Arena page-fetch tool during the
windows recorded in sources.json, except rows explicitly marked
`observed_by="canonical-same-day"` (official page captured 2026-10-22
07:17:40-07:30:30Z by the repository's canonical session and recorded in
data/current/evidence/, re-used with that window disclosed), or
`observed_by="pdc-same-day"` (official pdc.tv schedule page captured by the
canonical session at 07:17Z plus this session's indexed reads of the same
official URLs; direct re-fetch blocked by the site's consent wall — attempts
logged in flagged.json).

Rules enforced here (COORDINATION.md §0.5):
  * blank + flag any value not confirmed from an official source;
  * OLBG is discovery only: its time text / top pick / tip counts are stored
    under `olbg` and never promoted to official facts;
  * conversions to UTC are arithmetic from an explicit timezone label
    (CEST/EDT/ET/local-stated-by-page + named venue zone) — never guesses.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "8f6d7364")
GEN = "2026-10-22T21:55:00Z"
HARVEST = json.load(open(os.path.join(OUT, "harvest.json")))

# ---------------------------------------------------------------- sources ---
SOURCES = [
    # id, org, url, observed (UTC window this session unless noted), method, observed_by, role, note
    ("src-olbg-hubs", "OLBG (discovery only, not a source of fact)",
     "https://www.olbg.com/betting-tips/", "2026-10-22T20:50Z/2026-10-22T20:57Z",
     "Arena page-fetch, chunk 0 of each of 17 in-scope hub pages", "this-session", "discovery",
     "Server-rendered top list per hub; 'Load More Tips' XHR pagination beyond capture."),
    ("src-nhl-schedule", "National Hockey League",
     "https://api-web.nhle.com/v1/schedule/2026-10-22", "2026-10-22T20:53Z/2026-10-22T21:00Z",
     "Arena page-fetch, chunks 0-3 (JSON)", "this-session", "official",
     "12 games on 2026-10-22 with startTimeUTC, gameState FUT/OK and embedded official odds arrays."),
    ("src-nhl-standings", "National Hockey League",
     "https://api-web.nhle.com/v1/standings/now", "2026-10-22T20:56Z/2026-10-22T21:04Z",
     "Arena page-fetch, chunks 0-7 (JSON); standingsDateTimeUtc=2026-10-22T20:57:30Z",
     "this-session", "official",
     "All 32 clubs: W-L-OTL, points, L10 and streak fields read verbatim."),
    ("src-mlb-schedule", "Major League Baseball",
     "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-26&hydrate=probablePitcher,team,venue,seriesStatus",
     "2026-10-22T21:02Z/2026-10-22T21:03Z", "Arena page-fetch, chunk 0 (JSON)",
     "this-session", "official",
     "World Series games 849805 (G1), 849802 (G2), 849804 (G3); ifNecessary flags as read."),
    ("src-mlb-records", "Major League Baseball",
     "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
     "2026-10-22T07:17:40Z/2026-10-22T07:30:30Z",
     "canonical same-day capture (data/current/evidence/mlb-records-2026.json)",
     "canonical-same-day", "official",
     "2026 regular-season records: Rays 98-64 (736 RS / 650 RA), Brewers 103-59 (832 RS / 618 RA)."),
    ("src-el-gamecenter", "Euroleague Basketball",
     "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
     "2026-10-22T21:05Z/2026-10-22T21:08Z", "Arena page-fetch, chunks 0-1",
     "this-session", "official",
     "Round 7: Friday fixtures with CEST tip times and both teams' records; Thursday results as form."),
    ("src-nba-games22", "National Basketball Association",
     "https://www.nba.com/games?date=2026-10-22",
     "2026-10-22T07:17:40Z/2026-10-22T07:30:30Z (card details); 2026-10-22T21:30Z (this session's re-read: calendar day count only, matchup cards JS-blocked)",
     "canonical same-day capture (data/current/evidence/nba-games-20261022.json) + this session re-fetch",
     "canonical-same-day", "official",
     "Game ids 0022600006 Cavaliers @ 76ers '7:00 PM ET', 0022600007 Nuggets @ Thunder '9:30 PM ET'; official calendar confirms 2 games on 22 Oct and 12 on 23 Oct."),
    ("src-nba-cal23", "National Basketball Association",
     "https://www.nba.com/games?date=2026-10-23", "2026-10-22T21:31Z/2026-10-22T21:31Z",
     "Arena page-fetch (calendar only; matchup cards JS-blocked)", "this-session", "official",
     "Official calendar confirms 12 games on 2026-10-23; individual matchups/times NOT retrievable."),
    ("src-wta-osaka-op", "Women's Tennis Association",
     "https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf",
     "2026-10-22T21:12Z/2026-10-22T21:13Z", "Arena page-fetch (order-of-play PDF)",
     "this-session", "official",
     "ORDER OF PLAY Friday 23 October 2026, RELEASED 22 Oct 2026 4:20 PM; four quarter-finals with starting/not-before times (tournament local)."),
    ("src-wta-osaka-draw", "Women's Tennis Association",
     "https://wtafiles.wtatennis.com/pdf/draws/2026/405/MDS.pdf",
     "2026-10-22T21:11Z/2026-10-22T21:12Z", "Arena page-fetch (main-draw PDF)",
     "this-session", "official",
     "Main draw with per-seed official ranks, R32/R16 scores, withdrawals/retirements."),
    ("src-wta-ningbo-op", "Women's Tennis Association",
     "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
     "2026-10-22T21:39Z/2026-10-22T21:40Z", "Arena page-fetch (order-of-play PDF)",
     "this-session", "official",
     "ORDER OF PLAY Friday 23 October 2026; four quarter-finals with starting/not-before times (tournament local)."),
    ("src-wta-ningbo-draw", "Women's Tennis Association",
     "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf",
     "2026-10-22T21:24Z/2026-10-22T21:25Z", "Arena page-fetch (main-draw PDF)",
     "this-session", "official",
     "Main draw with per-seed official ranks, R32/R16 scores, 'RELEASED 22 Oct 2026 7:46 PM', retirements."),
    ("src-atp-almaty-sched", "ATP Tour",
     "https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule",
     "2026-10-22T21:17Z/2026-10-22T21:18Z", "Arena page-fetch",
     "this-session", "official",
     "Fri 23 Oct Day 7 order of play, Center Court 'Starts At 11:30' / 'Not Before 13:00' (local, page states Use Local Time Zone)."),
    ("src-atp-almaty-draw", "ATP Tour",
     "https://www.atptour.com/en/scores/current/almaty/9410/draws",
     "2026-10-22T21:16Z/2026-10-22T21:17Z", "Arena page-fetch",
     "this-session", "official",
     "R32 results and seed markers; official print link protennisliv mds.pdf."),
    ("src-atp-brussels-sched", "ATP Tour",
     "https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule",
     "2026-10-22T21:36Z/2026-10-22T21:37Z", "Arena page-fetch",
     "this-session", "official",
     "Fri 23 Oct Centre Court: Starts At 14:00, 'Not Before 16:00' Griekspoor-Lehecka (local)."),
    ("src-atp-lyon-sched", "ATP Tour",
     "https://www.atptour.com/en/scores/current/lyon/496/daily-schedule",
     "2026-10-22T21:37Z/2026-10-22T21:38Z", "Arena page-fetch",
     "this-session", "official",
     "Fri 23 Oct Court Central: Starts At 12:00, 'Not Before 14:00' Moutet-Paul, 'Followed By' Altmaier-Fritz (local)."),
    ("src-atp-current", "ATP Tour",
     "https://www.atptour.com/en/scores/current",
     "2026-10-22T21:38Z/2026-10-22T21:39Z", "Arena page-fetch",
     "this-session", "official",
     "Live R16 results used as form: Medvedev d. Shimabukuro 6-2 6-1; Lehecka d. Collignon 6-4 6-2; Fritz d. Herbert 6-2 7-5; Michelsen d. Goffin 6-3 6-4; Cobolli d. Wawrinka 6-2 6-4."),
    ("src-pdc-ec-schedule", "Professional Darts Corporation",
     "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
     "2026-10-22T07:17:40Z/2026-10-22T07:30:30Z (canonical capture) + 2026-10-22T21:2xZ (this session's indexed reads of the same official URL and pdc.tv/live; 8 direct fetch chunks returned only the consent wall)",
     "canonical same-day capture (data/current/evidence/pdc-extraction.json) + indexed reads; direct fetch blocked",
     "pdc-same-day", "official",
     "Friday 23 Oct 1900-2300 CEST, Round One x8 — all eight OLBG pairs listed verbatim; Thu update: Humphries out, Huybrechts in (pdc.tv, 22 Oct)."),
    ("src-urc-fixtures", "United Rugby Championship",
     "https://stats.unitedrugby.com/match-centre/2026-27/4",
     "2026-10-22T21:08Z/2026-10-22T21:10Z", "Arena page-fetch, chunks 0-1",
     "this-session", "official",
     "Round 4 fixtures; page states 'All times shown are Local'."),
    ("src-urc-table", "United Rugby Championship",
     "https://stats.unitedrugby.com/match-centre/table/2026-27",
     "2026-10-22T21:32Z/2026-10-22T21:33Z", "Arena page-fetch",
     "this-session", "official",
     "Full league table: PTS/PL/W/D/L/PF/PA/FORM for all 16 clubs."),
    ("src-lnr-top14", "Ligue Nationale de Rugby (Top 14)",
     "https://top14.lnr.fr/calendrier-et-resultats",
     "2026-10-22T21:32Z/2026-10-22T21:33Z", "Arena page-fetch",
     "this-session", "official",
     "Round 7 fixtures (Sat 24 / Sun 25 Oct) with club table positions as displayed."),
    ("src-lnr-prod2", "Ligue Nationale de Rugby (Pro D2)",
     "https://prod2.lnr.fr/calendrier-et-resultats",
     "2026-10-22T21:34Z/2026-10-22T21:35Z", "Arena page-fetch",
     "this-session", "official",
     "Round 8 fixtures (Fri 23 Oct) with club table positions as displayed; Thu result Montauban 24-23 Oyonnax."),
    ("src-irl-fixtures", "International Rugby League",
     "https://www.intrl.sport/fixtures-results",
     "2026-10-22T21:09Z/2026-10-22T21:10Z", "Arena page-fetch",
     "this-session", "official",
     "Fixtures 23-31 Oct with venue and time text; page does not state a timezone (flagged)."),
    ("src-irl-rankings", "International Rugby League",
     "https://www.intrl.sport/world-rankings",
     "2026-10-22T21:34Z/2026-10-22T21:35Z", "Arena page-fetch",
     "this-session", "official",
     "Official men's and women's world rankings with published strength percentages."),
    ("src-lnh-starligue-cal", "Ligue Nationale de Handball",
     "https://www.lnh.fr/daikin-starligue/calendrier",
     "2026-10-22T21:39Z/2026-10-22T21:44Z", "Arena page-fetch, chunks 0-1",
     "this-session", "official",
     "Daikin StarLigue J08 fixtures (per-match official 'Infos' links)."),
    ("src-lnh-starligue-table", "Ligue Nationale de Handball",
     "https://www.lnh.fr/daikin-starligue/classement",
     "2026-10-22T21:54Z/2026-10-22T21:56Z", "Arena page-fetch, chunks 0-1",
     "this-session", "official",
     "2026/27 table after 7 rounds: pts/mj/V-D-N and goals for/against for all 16 clubs."),
    ("src-munster-gaa", "Munster GAA",
     "https://munster.gaa.ie/fixtures/events-calendar/",
     "2026-10-22T21:10Z/2026-10-22T21:11Z and 2026-10-22T21:44Z/2026-10-22T21:45Z",
     "Arena page-fetch, chunks 0-1", "this-session", "official",
     "Cork, Kerry and Waterford senior football championship finals with date/time/venue."),
    ("src-aflw-match", "Australian Football League",
     "https://www.afl.com.au/aflw/matches/8970",
     "2026-10-22T21:41Z/2026-10-22T21:42Z", "Arena page-fetch",
     "this-session", "official",
     "Port Adelaide v Collingwood, Round 11, Friday 23 October 2026, 4:15 AM (EDT), Alberton Oval."),
    ("src-wst-ni-open", "World Snooker Tour",
     "https://www.wst.tv/matches/",
     "2026-10-22T21:09Z/2026-10-22T21:12Z", "Arena page-fetch, chunks 0-2",
     "this-session", "official",
     "BetVictor Northern Ireland Open: Round 3 (Thu) results incl. Wilson 4-3 Pang; scheduled quarter-finals Fri 23 Oct; page does not state a timezone (flagged)."),
    ("src-f1-usgp", "Formula 1",
     "https://www.formula1.com/en/racing/2026/united-states",
     "2026-10-22T21:01Z/2026-10-22T21:02Z", "Arena page-fetch",
     "this-session", "official",
     "United States Grand Prix 2026 schedule rows incl. '25Oct Race 16:00' (page MY TIME/TRACK TIME toggle — timezone context ambiguous, flagged)."),
    ("src-pgc-hub", "PGA TOUR Champions",
     "https://www.pgatour.com/pgatour-champions",
     "2026-10-22T21:40Z/2026-10-22T21:41Z", "Arena page-fetch",
     "this-session", "official",
     "Stifel Charity Classic pre-tournament article at Norwood Hills CC, St Louis; Schwab Cup top-10 through SAS Championship (18 Oct): 1 Cink (16 top-10s, 5 wins), 2 Z. Johnson, 3 Alker/McNeill, 5 Goosen."),
    ("src-pga-schedule", "PGA TOUR",
     "https://www.pgatour.com/schedule",
     "2026-10-22T07:17:40Z/2026-10-22T07:30:30Z",
     "canonical same-day capture (data/current/evidence/pga-schedule.json)",
     "canonical-same-day", "official",
     "Butterfield Bermuda Championship, 22-25 October 2026, Port Royal Golf Course."),
    ("src-gbgb", "Greyhound Board of Great Britain",
     "https://www.gbgb.org.uk/racing/",
     "2026-10-22T21:45Z/2026-10-22T21:46Z", "Arena page-fetch",
     "this-session", "official",
     "Official race reports dated Thu 22 Oct 2026 (Scurry Gold Cup, Dunstall Park; Oaks, Dunstall Park; Doncaster Puppy Derby). Structured race cards are JS-rendered and not retrievable."),
    ("src-lol-worlds", "Riot Games (LoL Esports)",
     "https://lolesports.com/en-GB/tournament/115660540725177488/overview",
     "2026-10-22T21:45Z/2026-10-22T21:46Z", "Arena page-fetch",
     "this-session", "official",
     "Worlds 2026 'IN PROGRESS', Oct-Nov, phase format and qualified teams; no match-level fixtures exposed on the overview."),
    ("src-plusliga", "PlusLiga / TAURON Liga portal",
     "https://www.plusliga.pl/games.html",
     "2026-10-22T21:45Z/2026-10-22T21:46Z", "Arena page-fetch (chunk 0 of 16; page serves completed 16-17 Oct matches first)",
     "this-session", "official",
     "Page reachable; future-dated fixtures not reached inside fetched chunks — per-row verification not completed (flagged)."),
    ("src-hbl", "Handball-Bundesliga domain observed",
     "https://www.hbl.de/",
     "2026-10-22T21:45Z/2026-10-22T21:46Z", "Arena page-fetch",
     "this-session", "official",
     "IRREGULARITY: hbl.de redirected to an unrelated steel-company site (europeanstaal.de) — not a handball source this session; German handball rows left unverified."),
    ("src-icc", "International Cricket Council",
     "https://www.icc-cricket.com/fixtures-results",
     "2026-10-22T21:09Z/2026-10-22T21:09Z", "Arena page-fetch (JS shell only, no fixture data)",
     "this-session", "official",
     "Fixture list not retrievable (client-side rendering)."),
    ("src-nzc", "New Zealand Cricket",
     "https://www.nzc.co.nz/fixtures/",
     "2026-10-22T21:48Z/2026-10-22T21:48Z", "Arena page-fetch — transport failure",
     "this-session", "official",
     "Fetch failed; no content read."),
    ("src-csa", "Cricket South Africa",
     "https://www.cricket.co.za/",
     "2026-10-22T21:48Z/2026-10-22T21:49Z", "Arena page-fetch",
     "this-session", "official",
     "Site reachable but live widget displayed a stale 'Tour of England 2025' card; no 2026 fixture retrievable."),
    ("src-premrugby", "PREM Rugby",
     "https://www.premrugby.com/fixtures-results",
     "2026-10-22T21:48Z/2026-10-22T21:49Z", "Arena page-fetch (JS shell: filters only, no fixture rows)",
     "this-session", "official",
     "Fixture rows not retrievable."),
    ("src-wta-rankings", "Women's Tennis Association",
     "https://www.wtatennis.com/",
     "2026-10-22T21:50Z/2026-10-22T21:50Z", "not fetched — draw PDFs used instead",
     "this-session", "official",
     "Official per-seed ranks read from the two draw PDFs instead."),
    ("src-gaagalway", "Galway GAA",
     "https://www.gaagalway.ie/fixtures/",
     "2026-10-22T21:50Z/2026-10-22T21:50Z", "Arena page-fetch — transport failure",
     "this-session", "official",
     "Fetch failed; Moycullen v Salthill-Knocknacarra left unverified."),
    ("src-aflw-ladder", "Australian Football League",
     "https://www.afl.com.au/aflw/ladder",
     "2026-10-22T21:52Z/2026-10-22T21:53Z", "Arena page-fetch (JS: 'Loading', no ladder rows)",
     "this-session", "official",
     "Ladder not retrievable — no AFLW strength input, pricing withheld."),
    ("src-atp-rankings", "ATP Tour",
     "https://www.atptour.com/en/rankings/singles",
     "2026-10-22T21:47Z/2026-10-22T21:49Z", "Arena page-fetch, chunks 0-2 (date-selector only; ranked table deeper and not reached)",
     "this-session", "official",
     "Official seeds from event draw/schedule pages used; player rank table not retrieved (flagged)."),
    ("src-nba-standings", "National Basketball Association",
     "https://www.nba.com/standings",
     "2026-10-22T21:50Z/2026-10-22T21:50Z", "not attempted after nba.com/schedule and /games JS-blocked twice",
     "this-session", "official",
     "No NBA strength input obtained; NBA rows unpriced."),
    ("src-euroleague-standings", "Euroleague Basketball",
     "https://www.euroleaguebasketball.net/en/euroleague/standings/",
     "2026-10-22T21:05Z/2026-10-22T21:05Z", "not fetched — team records read from the official game-center article instead",
     "this-session", "official",
     "Records for the six Friday teams taken from the Round 7 game-center article."),
]
SOURCES_J = [
    {"id": i, "org": o, "url": u, "observed": w, "method": m, "observed_by": by,
     "role": role, "note": n}
    for (i, o, u, w, m, by, role, n) in SOURCES
]

# ------------------------------------------------------------------ flags ---
FLAGS = []

def flag(fid, severity, title, detail, links=None, rows=None):
    FLAGS.append({"id": fid, "severity": severity, "title": title, "detail": detail,
                  "links": links or [], "rows": rows or []})

flag("F-8F6D-01", "high",
     "OLBG hub time text uses inconsistent timezone conventions across sports",
     "Read from OLBG hub pages (20:50-20:57Z) against official times: NHL/MLB/tennis/darts/golf text matches "
     "US Eastern (NHL '19:07' vs official 23:00Z = 19:00 ET nominal, +7 min pad; NBA text matches UK BST with a "
     "+10 min pad: OLBG '00:10' vs official 7:00 PM ET = 00:00 BST); rugby union text equals venue-local times "
     "exactly; EuroLeague text equals BST exactly. Official times (UTC) are authoritative on this desk; OLBG text "
     "is preserved verbatim under `olbg.time_text` only.",
     ["https://api-web.nhle.com/v1/schedule/2026-10-22",
      "https://www.nba.com/games?date=2026-10-22",
      "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/"])
flag("F-8F6D-02", "high",
     "OLBG Rathgormack v The Nire date conflicts with the official Munster GAA calendar",
     "OLBG event 3536 shows '01 Nov 15:30'; the official Munster GAA calendar lists the 2026 Waterford Senior "
     "Football Championship Final Rathgormack v The Nire on Sun, Oct 25, 2026 @ 2:30pm at Cappoquin Logistics "
     "Fraher Field, Dungarvan. Official value published; OLBG text kept as discovery only.",
     ["https://munster.gaa.ie/event/2026-waterford-senior-football-championship-final-rathgormack-v-the-nire/",
      "https://munster.gaa.ie/fixtures/events-calendar/"], ["gf-waterford-final"])
flag("F-8F6D-03", "medium",
     "Direct fetch of the official PDC European Championship schedule page returns only a consent wall",
     "Eight page-fetch attempts (news article, /tournaments, /live) returned cookie-consent content only on "
     "2026-10-22 21:0x-21:1xZ. The same official page's content was read this session through indexed excerpts of "
     "that exact pdc.tv URL and was captured canonically at 07:17Z (data/current/evidence/pdc-extraction.json). "
     "Rows published with observed_by=pdc-same-day and this disclosure.",
     ["https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/"],
     [f"gd-{i}" for i in range(1, 9)])
flag("F-8F6D-04", "medium",
     "nba.com matchup cards are JS-blocked for this fetch method — 23 Oct NBA rows not individually verified",
     "The official nba.com calendar (read 21:31Z) confirms 12 games on 2026-10-23 but the per-game cards did not "
     "render (same failure on 22 Oct, where the canonical session had captured cards at 07:17Z). Rows "
     "gb-chi-mil, gb-nyk-bos and gb-hou-sa keep OLBG-discovered participants with official time/status fields "
     "blank and flagged.",
     ["https://www.nba.com/games?date=2026-10-23"], ["gb-chi-mil", "gb-nyk-bos", "gb-hou-sa"])
flag("F-8F6D-05", "medium",
     "Official sources unreachable or JS-blocked for several discovery rows (blank + flagged, per §0.5)",
     "ICC fixtures page (JS shell), NZC (fetch failure), Cricket South Africa (stale 2025 widget) leave the four "
     "OLBG cricket rows unverified; gaagalway.ie fetch failure leaves Moycullen v Salthill-Knocknacarra unverified; "
     "premrugby.com fixture rows JS-blocked leaves Newcastle v Sale unverified; CBV (Brazil NBB) and the Danish/German/"
     "Spanish handball federations and the Volleyball federation pages outside PlusLiga were not retrievable this "
     "session; the four European club hockey OLBG rows (Danish Metal Ligaen, Austria EHL) have no official league "
     "source fetched this session. All keep discovery content and blank official fields.",
     ["https://www.icc-cricket.com/fixtures-results",
      "https://www.cricket.co.za/",
      "https://www.premrugby.com/fixtures-results"])
flag("F-8F6D-06", "medium",
     "hbl.de no longer serves Handball-Bundesliga content",
     "Fetch of https://www.hbl.de/ on 2026-10-22 21:45Z redirected to an unrelated steel company site "
     "(europeanstaal.de). German handball rows are therefore unverified against a federation source this session.",
     ["https://www.hbl.de/"], ["hb-gop-eis", "hb-han-lem", "hb-erl-kiel"])
flag("F-8F6D-07", "medium",
     "WST match page does not state a timezone for its listed start times",
     "The Northern Ireland Open match list (read 21:09-21:12Z) shows times such as '08:00'/'14:00' Fri 23 Oct with "
     "no timezone. time_text published verbatim; start_utc left blank and flagged (same treatment as the canonical "
     "snapshot's WST rows).",
     ["https://www.wst.tv/matches/"], ["sn-qf-1", "sn-qf-2", "sn-qf-3"])
flag("F-8F6D-08", "medium",
     "IRL fixture page does not state a timezone for its listed start times",
     "Official fixture times (e.g. '20:05' Tonga v Lebanon) are published as venue text; start_utc blank + flagged.",
     ["https://www.intrl.sport/fixtures-results"], ["rl-men-1", "rl-women-1", "rl-int-1"])
flag("F-8F6D-09", "medium",
     "Formula 1 US GP start time timezone context ambiguous on the official page",
     "The race row reads '25Oct Race 16:00' beneath a MY TIME/TRACK TIME toggle whose reference zone depends on the "
     "viewer; the page does not print an explicit timezone next to the row. Official date 25 Oct published; the "
     "start time published as listed with the ambiguity flagged; start_utc blank.",
     ["https://www.formula1.com/en/racing/2026/united-states"], ["mr-us-gp"])
flag("F-8F6D-10", "medium",
     "Stifel Charity Classic official date/time not printed on the fetched official page",
     "The PGA TOUR Champions hub (21:40Z) confirms the event, venue (Norwood Hills Country Club, St. Louis) and "
     "pre-tournament coverage but no date/start row was present in the fetched content; the OLBG '25 Oct 17:45' "
     "text is discovery only. Official date/time blank + flagged.",
     ["https://www.pgatour.com/pgatour-champions"], ["gf-stifel"])
flag("F-8F6D-11", "medium",
     "Greyhounds: no structured official fixtures retrievable and no OLBG listings",
     "The OLBG greyhounds hub returned 'No tips found' (20:56Z) and GBGB's race cards are JS-rendered; only official "
     "news/report headlines (dated Thu 22 Oct 2026) were readable. No per-race rows published; sport marked a "
     "coverage gap.",
     ["https://www.gbgb.org.uk/racing/", "https://www.olbg.com/betting-tips/Greyhounds/28"], [])
flag("F-8F6D-12", "low",
     "OLBG visible hub capture excludes later pages ('Load More Tips' XHR) and some official fixtures",
     "Discovery captured the server-rendered top list per hub. Official rounds contain additional fixtures OLBG's "
     "visible list did not show (URC 3, Top 14 5, rugby league 14, AFLW 1, snooker 3, MLB 2, GAA Kerry 1) — all "
     "published as discovery='official-only' with the OLBG gap noted.",
     ["https://www.olbg.com/betting-tips/"], [])
flag("F-8F6D-13", "medium",
     "No NBA strength input obtainable — tonight's two verified NBA rows are left unpriced",
     "Official NBA standings/records could not be fetched (JS blocks); no records were inferred. Rows carry "
     "officially-verified participants/time and blank prices with reason.",
     ["https://www.nba.com/games?date=2026-10-22"], ["nb-cle-phi", "nb-den-okc"])
flag("F-8F6D-14", "low",
     "Ante-post/outright listings are out of scope for this match desk",
     "OLBG hubs list outrights (F1 drivers' title, PDC World Championship, cricket World Cup/BBL/SA20/T20 Blast, "
     "State of Origin 2027, Super League/NRL 2027, All-Ireland 2027). These are not matches in the 22-29 Oct window "
     "and are recorded in the harvest but excluded from the fixtures list with this reason.",
     ["https://www.olbg.com/betting-tips/Cricket/7"], [])
flag("F-8F6D-15", "low",
     "OLBG tip counts are community votes, not probabilities or odds",
     "OLBG '% Win Tips' figures (e.g. '16/20 Win Tips 80%') are stored under olbg.tips for transparency and never "
     "used as probabilities. OLBG event pages were not opened for bookmaker odds; no bookmaker quote is asserted "
     "anywhere on this desk (the only market quotes shown are the NHL API's officially embedded odds, labelled as such).",
     ["https://www.olbg.com/betting-tips/Baseball/12"], [])
flag("F-8F6D-16", "medium",
     "Near-window and out-of-window model favourites are disclosed, not promoted",
     "The brief's High gate (model p >= 0.70 AND fair price inside -250..+10000) excludes favourites whose fair "
     "price is shorter than -250 (p > 0.7143). Every such selection is listed in the >=70% out-of-window ledger on "
     "the Analysis page instead of being labelled High.",
     [], [])
flag("F-8F6D-17", "low",
     "WTA order-of-play times are tournament-local; UTC derived from the tournament's stated venue zone",
     "Osaka (JST, UTC+9) and Ningbo (UTC+8) OP PDFs state venue and local times but not the zone abbreviation; UTC "
     "values are arithmetic from the stated venue location and flagged 'tz by venue'.",
     ["https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf",
      "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf"], [])
flag("F-8F6D-18", "low",
     "PlusLiga future fixtures not reached inside the fetched page chunks",
     "plusliga.pl/games.html is reachable (chunk 0 of 16 served completed 16-17 Oct results first); the three "
     "OLBG volleyball rows using Polish competitions keep blank official fields until a targeted re-read.",
     ["https://www.plusliga.pl/games.html"], ["vb-sle-gks", "vb-skra-pro", "vb-chk-res"])
flag("F-8F6D-19", "medium",
     "eSports: no match-level fixtures from either source",
     "OLBG eSports hub returned 'No tips found'; the official LoL Esports Worlds overview confirms the tournament is "
     "in progress but exposes no match fixtures to this fetch. No esports rows published; coverage gap recorded.",
     ["https://lolesports.com/en-GB/tournament/115660540725177488/overview",
      "https://www.olbg.com/betting-tips/eSports/23"], [])
flag("F-8F6D-21", "low",
     "World Series Game 3 home team outside fetched payload chunk",
     "The official MLB schedule payload read this session (21:02Z) printed game 849804's away team (Milwaukee) "
     "but the home side fell outside the fetched chunk. Left blank, not inferred.",
     ["https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-26&hydrate=probablePitcher,team,venue,seriesStatus"],
     ["mlb-ws-g3"])
flag("F-8F6D-20", "low",
     "Ante-post note: Luke Humphries withdrew from the PDC European Championship (official, 22 Oct)",
     "Official PDC update: Kim Huybrechts replaces Humphries and faces Ryan Searle on Thursday. Affects the Thursday "
     "tie only; the eight Friday ties published here are unchanged.",
     ["https://www.pdc.tv/news/2026/october/22/humphries-withdraws-from-machineseeker-european-championship"], [])

# ---------------------------------------------------------------- helpers ---
def ev(sport):
    for h in HARVEST["hubs"]:
        if h["sport"] == sport:
            return {e["id"]: e for e in h["events"]}
    return {}

def olbg_of(sport, eid):
    e = ev(sport).get(eid)
    if not e:
        return None
    hub = [h for h in HARVEST["hubs"] if h["sport"] == sport][0]
    return {"event_id": eid, "hub_url": hub["olbg_url"],
            "time_text": e.get("olbg_time_text"), "top_pick": e.get("top_pick"),
            "market": e.get("market"), "tips": e.get("tips"), "tips_pct": e.get("pct")}

FIX = []
def fx(fid, sport, sport_name, competition, a, b, date, start_utc, time_text, venue,
       official_status, round_text, sources, observed, discovery, olbg=None,
       flags_=None, notes=None, blank=None, olbg_missing=False):
    FIX.append({
        "id": fid, "sport": sport, "sport_name": sport_name, "competition": competition,
        "participant_a": a, "participant_b": b, "date": date, "start_utc": start_utc,
        "time_text": time_text, "venue": venue, "official_status": official_status,
        "round": round_text, "sources": sources, "observed": observed,
        "discovery": discovery, "olbg": olbg, "flags": flags_ or [], "notes": notes or [],
        "fields_blank": blank or [], "olbg_capture_gap": olbg_missing,
        "verified": discovery != "discovery-only-unverified",
    })

# ============================================================ ICE HOCKEY ====
# NHL schedule 2026-10-22 (src-nhl-schedule, 20:53-21:00Z): startTimeUTC + odds (official, embedded).
NHL = [
    ("nhl-ns-h", "NSH Predators", "BOS Bruins", "2026-10-22T23:00:00Z", "TD Garden",
     {"NSH": [2.25, 2.12, "+130", "+126", "+127", 3.00], "BOS": [1.67, 1.72, "-155", "-152", "-156", 2.10]}, 199936),
    ("nhl-ny-tor", "NY Rangers", "TOR Maple Leafs", "2026-10-22T23:00:00Z", "Scotiabank Arena",
     {"NYR": [1.89, 1.95, "-110", "-112", "-112", 2.45], "TOR": [1.95, 1.85, "-110", "-110", "-108", 2.45]}, 199937),
    ("nhl-sjs-ott", "SJ Sharks", "OTT Senators", "2026-10-22T23:00:00Z", "Canadian Tire Centre",
     {"SJS": [2.10, 2.15, "+114", "+108", "+111", 2.75], "OTT": [1.76, 1.70, "-135", "-130", "-135", 2.25]}, 199942),
    ("nhl-ana-njd", "ANA Ducks", "NJ Devils", "2026-10-22T23:00:00Z", "Prudential Center",
     {"ANA": [2.71, 2.62, "+180", "+184", "+179", 3.80], "NJD": [1.47, 1.48, "-218", "-225", "-223", 1.77]}, 199932),
    ("nhl-fla-pit", "FLA Panthers", "PIT Penguins", "2026-10-22T23:00:00Z", "PPG Paints Arena",
     {"FLA": [1.96, 1.92, "-105", "-110", "-108", 2.50], "PIT": [1.88, 1.88, "-115", "-110", "-114", 2.45]}, 199934),
    ("nhl-lak-nyi", "LA Kings", "NY Islanders", "2026-10-22T23:30:00Z", "UBS Arena",
     {"LAK": [1.91, 1.92, "-115", "-110", "-112", 2.50], "NYI": [1.93, 1.87, "-105", "-110", "-110", 2.50]}, 199938),
    ("nhl-vgk-stl", "VGS Golden Knights", "STL Blues", "2026-10-23T00:00:00Z", "Enterprise Center",
     {"VGK": [1.78, 2.07, "-130", "-126", "-132", 2.30], "STL": [2.08, 1.76, "+110", "+105", "+108", 2.70]}, 199940),
    ("nhl-wpg-dal", "WPG Jets", "DAL Stars", "2026-10-23T00:00:00Z", "American Airlines Center",
     {"WPG": [2.62, 1.52, "+170", "+158", "+166", 3.60], "DAL": [1.50, 2.54, "-192", "-207", "-205", 1.87]}, 199941),
    ("nhl-min-cgy", "MIN Wild", "CGY Flames", "2026-10-23T01:00:00Z", "Scotiabank Saddledome",
     {"MIN": [1.48, 2.75, "-205", "-215", "-213", 1.80], "CGY": [2.69, 1.45, "+170", "+176", "+171", 3.75]}, 199935),
    ("nhl-car-edm", "CAR Hurricanes", "EDM Oilers", "2026-10-23T01:00:00Z", "Rogers Place",
     {"CAR": [1.83, 2.02, "-118", "-120", "-120", 2.35], "EDM": [2.02, 1.78, "-102", "+100", "-102", 2.60]}, 199931),
    ("nhl-uta-sea", "UTA Mammoth", "SEA Kraken", "2026-10-23T02:00:00Z", "Climate Pledge Arena",
     {"UTA": [1.57, None, "-170", "-178", "-175", None], "SEA": [2.44, 1.55, "+142", "+146", "+142", None]}, 199939),
    ("nhl-det-van", "DET Red Wings", "VAN Canucks", "2026-10-23T02:00:00Z", "Rogers Arena",
     {"DET": [1.61, 1.57, "-170", "-166", "-170", 2.03], "VAN": [2.36, 2.40, "+142", "+138", "+139", 3.15]}, 199933),
]
for fid, a, b, ut, ven, odds, olbg_id in NHL:
    fx(fid, "ice-hockey", "Ice Hockey", "NHL", a, b, ut[:10], ut, None, ven,
       "FUT (gameScheduleState OK)", "Regular season",
       ["src-nhl-schedule", "src-nhl-standings"], "2026-10-22T20:53Z/2026-10-22T21:00Z",
       "olbg", olbg_of("ice-hockey", olbg_id),
       flags_=["F-8F6D-01", "F-8F6D-15"],
       notes=["Official odds arrays recorded verbatim (see inputs.json 'official_odds'). "
              "OLBG time text differs from official nominal start (flag F-8F6D-01)."])
# European club rows from OLBG — no official league source fetched this session.
for eid, name, comp in [(199946, "Esbjerg Energy vs Herning Blue Fox", "Danish Metal Ligaen"),
                        (199969, "HK Olimpija Ljubljana vs Fehervar AV19", "Austria EHL"),
                        (199947, "Rodovre Mighty Bulls vs Herlev Eagles", "Danish Metal Ligaen"),
                        (199968, "Pioneers Vorarlberg vs HCB Sudtirol Alperia", "Austria EHL")]:
    a, b = [x.strip() for x in name.split(" vs ")]
    fx(f"nhl-euro-{eid}", "ice-hockey", "Ice Hockey", comp, a, b, None, None, None, None,
       None, None, [], None, "discovery-only-unverified", olbg_of("ice-hockey", eid),
       flags_=["F-8F6D-05"], blank=["participant verification", "date", "start time", "venue", "status"])

# =============================================================== BASEBALL ===
fx("mlb-ws-g1", "baseball", "Baseball", "MLB World Series", "TB Rays", "MIL Brewers",
   "2026-10-23", "2026-10-24T00:00:00Z", None, "American Family Field", "Scheduled",
   "World Series Game 1 (ifNecessary=N)", ["src-mlb-schedule", "src-mlb-records"],
   "2026-10-22T21:02Z/2026-10-22T21:03Z (schedule); records 2026-10-22T07:17Z",
   "olbg", olbg_of("baseball", 160789),
   flags_=["F-8F6D-15"],
   notes=["Probable pitchers officially listed: TB Nick Martinez, MIL Jacob Misiorowski (src-mlb-schedule)."])
fx("mlb-ws-g2", "baseball", "Baseball", "MLB World Series", "TB Rays", "MIL Brewers",
   "2026-10-24", "2026-10-25T00:00:00Z", None, "American Family Field", "Scheduled",
   "World Series Game 2 (ifNecessary=N)", ["src-mlb-schedule", "src-mlb-records"],
   "2026-10-22T21:02Z/2026-10-22T21:03Z", "official-only", None,
   olbg_missing=True,
   notes=["Probable pitcher TB: Drew Rasmussen (official); MIL pitcher not printed in fetched payload (blank)."])
fx("mlb-ws-g3", "baseball", "Baseball", "MLB World Series", "MIL Brewers", None,
   "2026-10-26", "2026-10-27T00:00:00Z", None, None, None,
   "World Series Game 3", ["src-mlb-schedule", "src-mlb-records"],
   "2026-10-22T21:02Z/2026-10-22T21:03Z", "official-only", None,
   olbg_missing=True, blank=["participant_b (home team not present in fetched payload chunk)", "venue", "status detail", "probable pitchers"],
   flags_=["F-8F6D-21"],
   notes=["Away team (MIL Brewers), date and 00:00Z start read from the official payload; the home side was outside the fetched chunk, so it is left blank rather than inferred."])

# ============================================================= BASKETBALL ===
fx("nb-cle-phi", "basketball", "Basketball", "NBA", "CLE Cavaliers", "PHI 76ers",
   "2026-10-22", "2026-10-22T23:00:00Z", "7:00 PM ET", None, None, None,
   ["src-nba-games22"], "2026-10-22T07:17:40Z/2026-10-22T07:30:30Z (canonical); 2026-10-22T21:30Z calendar re-read",
   "olbg", olbg_of("basketball", 534845),
   flags_=["F-8F6D-01", "F-8F6D-13", "F-8F6D-15"],
   notes=["Official time text '7:00 PM ET' (nba.com game id 0022600006); OLBG text 'Tomorrow 00:10' (BST +10 min, F-8F6D-01)."])
fx("nb-den-okc", "basketball", "Basketball", "NBA", "DEN Nuggets", "OKC Thunder",
   "2026-10-23", "2026-10-23T01:30:00Z", "9:30 PM ET (22 Oct US local)", None, None, None,
   ["src-nba-games22"], "2026-10-22T07:17:40Z/2026-10-22T07:30:30Z (canonical); 2026-10-22T21:30Z calendar re-read",
   "olbg", olbg_of("basketball", 534843),
   flags_=["F-8F6D-01", "F-8F6D-13", "F-8F6D-15"],
   notes=["Official time text '9:30 PM ET' (nba.com game id 0022600007)."])
fx("gb-chi-mil", "basketball", "Basketball", "NBA", "CHI Bulls", "MIL Bucks",
   "2026-10-23", None, None, None, None, None,
   ["src-nba-cal23"], "2026-10-22T21:31Z (calendar: 12 games on 23 Oct; matchups not retrievable)",
   "discovery-only-unverified", olbg_of("basketball", 536041),
   flags_=["F-8F6D-04", "F-8F6D-15"],
   blank=["official participant confirmation", "official time", "status"],
   notes=["Participants from OLBG discovery only; official row-level fields blank."])
fx("gb-nyk-bos", "basketball", "Basketball", "NBA", "NY Knicks", "BOS Celtics",
   "2026-10-23", None, None, None, None, None,
   ["src-nba-cal23"], "2026-10-22T21:31Z (calendar: 12 games on 23 Oct; matchups not retrievable)",
   "discovery-only-unverified", olbg_of("basketball", 534842),
   flags_=["F-8F6D-04", "F-8F6D-15"],
   blank=["official participant confirmation", "official time", "status"])
fx("gb-hou-sa", "basketball", "Basketball", "NBA", "HOU Rockets", "SA Spurs",
   "2026-10-23", None, None, None, None, None,
   ["src-nba-cal23"], "2026-10-22T21:31Z (calendar: 12 games on 23 Oct; matchups not retrievable)",
   "discovery-only-unverified", olbg_of("basketball", 534841),
   flags_=["F-8F6D-04", "F-8F6D-15"],
   blank=["official participant confirmation", "official time", "status"],
   notes=["OLBG text reads '24 Oct 02:40' (BST); the official calendar counts this game under 23 Oct US dates."])
for eid, a, b in [(536019, "Fortaleza BC", "Pinheiros"), (536020, "Uniao Corinthians", "Minas"),
                  (536052, "Brasilia", "Corinthians")]:
    fx(f"nb-nbb-{eid}", "basketball", "Basketball", "Brazil NBB", a, b, None, None, None, None,
       None, None, [], None, "discovery-only-unverified", olbg_of("basketball", eid),
       flags_=["F-8F6D-05"],
       blank=["date", "start time", "status", "participant confirmation"])
EL = [("el-zal-asv", "Zalgiris Kaunas", "LDLC ASVEL Villeurbanne", "19:00 CEST", "2026-10-23T17:00:00Z", 535928,
       "Zalgiris (2-4) v ASVEL (2-4); ASVEL allow a league-high 95.3 ppg through six rounds; Zalgiris backcourt expected healthy (official preview)."),
      ("el-oly-fen", "Olympiacos Piraeus", "Fenerbahce Tarfin Istanbul", "20:15 CEST", "2026-10-23T18:15:00Z", 535925,
       "Olympiacos (5-1, 98.2 ppg) v Fenerbahce (5-1, 74.5 ppg allowed, seeking first road win); Olympiacos won the last three H2Hs (official preview)."),
      ("el-par-val", "Paris Basketball", "Valencia Basket", "20:45 CEST", "2026-10-23T18:45:00Z", 535926,
       "Paris (1-5, three straight losses; Nadir Hifi 20.2 ppg) v Valencia (5-1, league-best 98.3 ppg, first loss last round; TJ Shorts faces former club) (official preview).")]
for fid, a, b, tt, ut, eid, note in EL:
    fx(fid, "basketball", "Basketball", "EuroLeague Round 7", a, b, "2026-10-23", ut, tt, None,
       None, "Round 7", ["src-el-gamecenter"], "2026-10-22T21:05Z/2026-10-22T21:08Z",
       "olbg", olbg_of("basketball", eid), flags_=["F-8F6D-15"], notes=[note])

# ================================================================ TENNIS ===
# (row id, sport-competition, a, b, round, date, start_utc, time_text, tz-note, olbg id, source, notes)
TEN = [
 ("tn-osaka-li-tagger", "WTA Japan Open (Osaka)", "Ann Li", "Lilli Tagger", "Quarterfinal",
  "2026-10-23", "2026-10-23T02:30:00Z", "Starting at 11:30 AM", "JST (venue)", 902135,
  ["src-wta-osaka-op", "src-wta-osaka-draw"],
  ["Draw: [1] Li def. Jones 5-7 6-0 6-3, then Sonmez 6-3 6-1; Tagger def. Zhang 7-5 6-3, Samsonova 6-3 6-3, Valentova 7-5 6-3 (official draw).",
   "Official seed table: Li rank 31 (seed 1). Tagger unseeded (rank not printed on draw)."]),
 ("tn-osaka-gibson-krueger", "WTA Japan Open (Osaka)", "Talia Gibson", "Ashlyn Krueger", "Quarterfinal",
  "2026-10-23", None, "Followed by (after Li-Tagger)", "JST (venue)", 902107,
  ["src-wta-osaka-op", "src-wta-osaka-draw"],
  ["Gibson [4] (official rank 41) def. Dart 7-5 7-6(6), then Kraus 6-2 6-1; Krueger def. Tjen [6] 6-3 6-1 (official draw)."]),
 ("tn-osaka-stoiana-siniakova", "WTA Japan Open (Osaka)", "Mary Stoiana", "Katerina Siniakova", "Quarterfinal",
  "2026-10-23", None, "Followed by", "JST (venue)", 902138,
  ["src-wta-osaka-op", "src-wta-osaka-draw"],
  ["[Q] Stoiana def. Oliynykova [7] 6-2 3-6 6-3 and Uchijima 6-4 6-7(7) 6-3; Siniakova def. Linette 6-4 6-1 with a retirement win in R32 (official draw)."]),
 ("tn-osaka-boulter-ruzic", "WTA Japan Open (Osaka)", "Katie Boulter", "Antonia Ruzic", "Quarterfinal",
  "2026-10-23", None, "Followed by", "JST (venue)", 902134,
  ["src-wta-osaka-op", "src-wta-osaka-draw"],
  ["Boulter [8] (official rank 54) def. Sakatsume 6-3 6-2; Ruzic def. Badosa with a retirement (official draw)."]),
 ("tn-ningbo-bejlek-bouzkova", "WTA Ningbo Open", "Sara Bejlek", "Marie Bouzkova", "Quarterfinal",
  "2026-10-23", "2026-10-23T05:00:00Z", "Not before 1:00 PM", "UTC+8 (venue)", 902117,
  ["src-wta-ningbo-op", "src-wta-ningbo-draw"],
  ["Bejlek def. Shi 7-6(3) 6-4, then Cirstea [8] 4-6 6-3 6-3; Bouzkova def. Rakhimova 6-4 6-4, then Zakharova 7-5 6-2 (official draw)."]),
 ("tn-ningbo-fernandez-alexandrova", "WTA Ningbo Open", "Leylah Fernandez", "Ekaterina Alexandrova", "Quarterfinal",
  "2026-10-23", None, "Followed by", "UTC+8 (venue)", 902118,
  ["src-wta-ningbo-op", "src-wta-ningbo-draw"],
  ["Fernandez def. Mertens [7] 4-6 6-3 7-5, then Sasnovich 7-5 6-7(3) 6-3; Alexandrova def. Guo 6-2 6-3, then Kostyuk [3] 6-4, RET (Kostyuk right wrist) (official draw)."]),
 ("tn-ningbo-jovic-shnaider", "WTA Ningbo Open", "Iva Jovic", "Diana Shnaider", "Quarterfinal",
  "2026-10-23", "2026-10-23T08:00:00Z", "Not before 4:00 PM", "UTC+8 (venue)", 902140,
  ["src-wta-ningbo-op", "src-wta-ningbo-draw"],
  ["Jovic [4] (official rank 11) def. Paolini 6-4 6-3; Shnaider [6] (official rank 13) def. Putintseva 7-5 7-6(4), then Eala 7-5 6-4 (official draw)."]),
 ("tn-ningbo-rybakina-kawa", "WTA Ningbo Open", "Elena Rybakina", "Katarzyna Kawa", "Quarterfinal",
  "2026-10-23", "2026-10-23T11:00:00Z", "Not before 7:00 PM", "UTC+8 (venue)", 902143,
  ["src-wta-ningbo-op", "src-wta-ningbo-draw"],
  ["Rybakina [1] (official rank 1) bye then Kudermetova RET; Kawa [Q] def. Snigur 1-6 6-2 6-4, Bencic [5] 7-5 6-2 (official draw)."]),
 ("tn-almaty-basil-mann", "ATP Almaty Open", "Nikoloz Basilashvili", "Adrian Mannarino", "Quarterfinal",
  "2026-10-23", "2026-10-23T06:30:00Z", "Starts At 11:30", "Almaty local (UTC+5)", 902119,
  ["src-atp-almaty-sched", "src-atp-almaty-draw"],
  ["Center Court starts 11:30 local; [Q] Basilashvili and Mannarino advanced to this quarter-final (official schedule/draw)."]),
 ("tn-almaty-tsitsi-duck", "ATP Almaty Open", "Stefanos Tsitsipas", "James Duckworth", "Quarterfinal",
  "2026-10-23", "2026-10-23T08:00:00Z", "Not Before 13:00", "Almaty local (UTC+5)", 902129,
  ["src-atp-almaty-sched", "src-atp-almaty-draw", "src-atp-current"],
  ["Tsitsipas [7] d. Kovacevic 7-6(9) 3-6 6-3, Kukushkin 6-1 6-2; Duckworth d. Kecmanovic 6-4, Darderi [2] 7-5 7-6(7) (official draw/results)."]),
 ("tn-almaty-medv-atmane", "ATP Almaty Open", "Daniil Medvedev", "Terence Atmane", "Quarterfinal",
  "2026-10-23", None, "Followed By", "Almaty local (UTC+5)", 902145,
  ["src-atp-almaty-sched", "src-atp-current"],
  ["Medvedev [1] d. Shimabukuro 6-2 6-1 (official live results, 21:38Z); Atmane advanced through Hijikata 7-6(5) 6-2 and Bellucci (official draw)."]),
 ("tn-brussels-griek-leheck", "ATP European Open (Brussels)", "Tallon Griekspoor", "Jiri Lehecka", "Quarterfinal",
  "2026-10-23", "2026-10-23T14:00:00Z", "Not Before 16:00", "Brussels local (CEST, UTC+2)", 902144,
  ["src-atp-brussels-sched", "src-atp-current"],
  ["Lehecka [2] d. Collignon 6-4 6-2 (official live results, 21:38Z); Griekspoor reached the quarter-final per the official order of play."]),
 ("tn-lyon-moutet-paul", "ATP Lyon Open", "Corentin Moutet", "Tommy Paul", "Quarterfinal",
  "2026-10-23", "2026-10-23T12:00:00Z", "Not Before 14:00", "Lyon local (CEST, UTC+2)", 902133,
  ["src-atp-lyon-sched"],
  ["Court Central starts 12:00 local; Moutet v [4] Paul listed Not Before 14:00 (official order of play)."]),
 ("tn-lyon-altmaier-fritz", "ATP Lyon Open", "Daniel Altmaier", "Taylor Fritz", "Quarterfinal",
  "2026-10-23", None, "Followed By", "Lyon local (CEST, UTC+2)", 902152,
  ["src-atp-lyon-sched", "src-atp-current"],
  ["Fritz [2] d. Herbert 6-2 7-5 (official live results, 21:38Z); Altmaier-Fritz follows Moutet-Paul (official order of play)."]),
]
for fid, comp, a, b, rnd, date, ut, tt, tzn, eid, srcs, notes in TEN:
    blanks = [] if ut else ["start_utc (time published as order-of-play text; sequence not fixed)"]
    fx(fid, "tennis", "Tennis", comp, a, b, date, ut, tt, None, None, rnd, srcs,
       "2026-10-22T21:11Z/2026-10-22T21:39Z", "olbg", olbg_of("tennis", eid),
       flags_=["F-8F6D-15", "F-8F6D-17"] + (["F-8F6D-17"] if "venue" in tzn else []),
       notes=notes, blank=blanks)

# =============================================================== CRICKET ===
for eid, a, b, comp, tt in [
    (188831, "Afghanistan", "Zimbabwe", "International ODI", "Tomorrow 07:30"),
    (188833, "Dolphins", "Garden Route Badgers", "South Africa domestic T20", "Tomorrow 12:00"),
    (188832, "New Zealand", "India", "International T20 (2nd)", "24 Oct 03:00"),
    (188830, "India W", "Zimbabwe W", "International Women's ODI (1st)", "Tomorrow 04:30")]:
    fx(f"ck-{eid}", "cricket", "Cricket", comp, a, b, None, None, None, None, None, None,
       ["src-icc"], "2026-10-22T21:09Z (ICC page: JS shell, no data)",
       "discovery-only-unverified", olbg_of("cricket", eid), flags_=["F-8F6D-05", "F-8F6D-15"],
       blank=["date", "start time", "participant confirmation", "status"],
       notes=["Also attempted: NZC (fetch failure), Cricket South Africa (stale 2025 widget). Official verification unresolved."])

# =========================================================== RUGBY LEAGUE ===
RL = [
 ("rl-men-1", "Men", "IRL Men's Rugby League World Cup", "Tonga", "Lebanon", "Round 2", "2026-10-23", "20:05", "CommBank Stadium, Sydney", "2569"),
 ("rl-women-1", "Women", "IRL Women's Rugby League World Cup", "Samoa", "Wales", "Round 2", "2026-10-23", "17:50", "CommBank Stadium, Sydney", "2586"),
 ("rl-women-2", "Women", "IRL Women's Rugby League World Cup", "Fiji", "Papua New Guinea", "Round 2", "2026-10-24", "12:15", "Santos National Football Stadium, Port Moresby", "2587"),
 ("rl-int-1", "Men", "Senior International Matches (Men)", "Scotland", "Wales", "Senior International", "2026-10-24", "14:00", "Biggar RFC", "2661"),
 ("rl-int-2", "Men", "European Championship B (Men)", "Netherlands", "Serbia", "ECB", "2026-10-24", "14:00", "FK Zemun Stadium", "2664"),
 ("rl-men-2", "Men", "IRL Men's Rugby League World Cup", "Papua New Guinea", "Samoa", "Round 2", "2026-10-24", "14:25", "Santos National Football Stadium, Port Moresby", "2570"),
 ("rl-men-3", "Men", "IRL Men's Rugby League World Cup", "England", "France", "Round 2", "2026-10-24", "14:35", "HBF Park, Perth", "2571"),
 ("rl-int-3", "Men", "European Championship D (Men)", "Italy", "Czechia", "ECD", "2026-10-24", "15:00", "Stadio Giovanni Invernizzi, Abbiategrasso", "2646"),
 ("rl-women-3", "Women", "IRL Women's Rugby League World Cup", "Australia", "England", "Round 2", "2026-10-24", "17:05", "HBF Park, Perth", "2588"),
 ("rl-int-4", "Women", "Senior International Matches (Women)", "Malta", "Philippines", "Senior International", "2026-10-25", "15:00", "Croom Oval", "2665"),
 ("rl-women-4", "Women", "IRL Women's Rugby League World Cup", "New Zealand", "France", "Round 2", "2026-10-25", "15:50", "One NZ Stadium, Christchurch", "2589"),
 ("rl-men-4", "Men", "IRL Men's Rugby League World Cup", "New Zealand", "Cook Islands", "Round 2", "2026-10-25", "18:05", "One NZ Stadium, Christchurch", "2572"),
 ("rl-men-5", "Men", "IRL Men's Rugby League World Cup", "Australia", "Fiji", "Round 2", "2026-10-25", "19:05", "Suncorp Stadium, Brisbane", "2573"),
]
for fid, div, comp, a, b, rnd, date, tt, ven, mid in RL:
    fx(f"rugby-league-{fid}", "rugby-league", "Rugby League", comp, a, b, date, None, tt, ven,
       None, rnd, ["src-irl-fixtures"], "2026-10-22T21:09Z/2026-10-22T21:10Z",
       "official-only", None, flags_=["F-8F6D-08", "F-8F6D-12"],
       blank=["start_utc (page states no timezone)"],
       notes=[f"Division: {div}. OLBG rugby-league hub showed only 2027 outrights at capture time (F-8F6D-12)."])

# =========================================================== RUGBY UNION ===
URC = [
 ("urc-car-sha", "Cardiff Rugby", "Hollywoodbets Sharks", "2026-10-23", "14:45", "Cardiff Arms Park", "292608", True),
 ("urc-con-zeb", "Connacht Rugby", "Zebre Parma", "2026-10-23", "14:45", "Dexcom Stadium", "292609", False),
 ("urc-edi-lio", "Edinburgh Rugby", "10bet Lions", "2026-10-23", "14:45", "Hive Stadium", "292610", False),
 ("urc-bul-uls", "Vodacom Bulls", "Ulster Rugby", "2026-10-24", "07:45", "Loftus Versfeld", "292611", False),
 ("urc-sto-sca", "DHL Stormers", "Scarlets", "2026-10-24", "10:00", "DHL Stadium", "292612", False),
 ("urc-ben-gla", "Benetton Rugby", "Glasgow Warriors", "2026-10-24", "10:00", "Stadio Monigo", "292613", True),
 ("urc-lei-mun", "Leinster Rugby", "Munster Rugby", "2026-10-24", "13:00", "Aviva Stadium", "292614", False),
 ("urc-osp-dra", "Ospreys", "Dragons RFC", "2026-10-24", "14:00", "St Helen's", "292615", True),
]
LOCAL_TZ = {"2026-10-23": {"Cardiff Arms Park": ("BST", 1), "Dexcom Stadium": ("IST", 1), "Hive Stadium": ("BST", 1)},
            "2026-10-24": {"Loftus Versfeld": ("SAST", 2), "DHL Stadium": ("SAST", 2), "Stadio Monigo": ("CEST", 2),
                           "Aviva Stadium": ("IST", 1), "St Helen's": ("BST", 1)}}
OLBG_URC = {"urc-con-zeb": 609577, "urc-edi-lio": 609579, "urc-bul-uls": 609576,
            "urc-sto-sca": 609580, "urc-lei-mun": 609578}
for fid, a, b, date, tt, ven, mid, miss in UC_LOCAL if False else URC:
    tz, off = LOCAL_TZ[date][ven]
    hh, mm = int(tt[:2]), int(tt[3:])
    start = f"{date}T{hh - off:02d}:{mm:02d}:00Z" if hh - off >= 0 else None
    fx(fid, "rugby-union", "Rugby Union", "United Rugby Championship", a, b, date, start, f"{tt} ({tz}, local)",
       ven, None, "Round 4", ["src-urc-fixtures", "src-urc-table"],
       "2026-10-22T21:08Z/2026-10-22T21:10Z (fixtures); table 21:32Z",
       "official-only" if miss else "olbg", olbg_of("rugby-union", OLBG_URC.get(fid, 0)) if fid in OLBG_URC else None,
       flags_=["F-8F6D-12"] if miss else [], olbg_missing=miss,
       notes=["URC page states 'All times shown are Local'; UTC derived from the venue's stated local zone."])
T14 = [("t14-van-clm", "RC Vannes", "ASM Clermont", "2026-10-24", "14h30", 14, 11, True),
       ("t14-bay-lou", "Aviron Bayonnais", "LOU Rugby", "2026-10-24", "16h35", 5, 8, False),
       ("t14-cas-par", "Castres Olympique", "Stade Français Paris", "2026-10-24", "16h35", 13, 6, True),
       ("t14-rac-mon", "Racing 92", "Montpellier Hérault Rugby", "2026-10-24", "16h35", 12, 7, True),
       ("t14-tou-per", "Stade Toulousain", "USA Perpignan", "2026-10-24", "16h35", 1, 9, False),
       ("t14-tou-pau", "RC Toulon", "Section Paloise", "2026-10-24", "21h00", 10, 2, True),
       ("t14-lar-ubb", "Stade Rochelais", "Union Bordeaux-Bègles", "2026-10-25", "21h05", 4, 3, True)]
T14_OLBG = {"t14-bay-lou": 609564, "t14-tou-per": 609567}
for fid, a, b, date, tt, pa, pb, miss in T14:
    hh, mm = int(tt[:2]), int(tt[3:])
    start = f"{date}T{hh - 2:02d}:{mm:02d}:00Z"
    fx(fid, "rugby-union", "Rugby Union", "Top 14 Round 7", a, b, date, start, f"{tt} (CEST, local)", None,
       None, "J7", ["src-lnr-top14"], "2026-10-22T21:32Z/2026-10-22T21:33Z",
       "official-only" if miss else "olbg", olbg_of("rugby-union", T14_OLBG[fid]) if fid in T14_OLBG else None,
       flags_=["F-8F6D-12"] if miss else [], olbg_missing=miss,
       notes=[f"Official table positions on the fixture page: {a} {pa}e, {b} {pb}e."])
P2 = [("p2-nar-bri", "RC Narbonnais", "CA Brive", "15", 5, False),
      ("p2-agen-nis", "SU Agen", "Nissa Rugby", "10", 13, False),
      ("p2-soy-dax", "Soyaux-Angoulême XV", "US Dax", "8", 7, False),
      ("p2-aur-nev", "Stade Aurillacois", "USON Nevers", "9", 16, False),
      ("p2-val-col", "Valence Romans", "Colomiers Rugby", "11", 12, False),
      ("p2-pro-bez", "Provence Rugby", "AS Béziers Hérault", "2", 14, False),
      ("p2-gre-bia", "FC Grenoble Rugby", "Biarritz Olympique PB", "3", 6, False)]
P2_OLBG = {"p2-nar-bri": 609557, "p2-agen-nis": 609558, "p2-soy-dax": 609563,
           "p2-aur-nev": 609560, "p2-val-col": 609559, "p2-pro-bez": 609562, "p2-gre-bia": 609561}
for fid, a, b, pa, pb, miss in P2:
    tt = "19h00" if fid == "p2-nar-bri" else ("21h00" if fid in ("p2-pro-bez", "p2-gre-bia") else "19h30")
    hh, mm = int(tt[:2]), int(tt[3:])
    start = f"2026-10-23T{hh - 2:02d}:{mm:02d}:00Z"
    fx(fid, "rugby-union", "Rugby Union", "Pro D2 Round 8", a, b, "2026-10-23", start, f"{tt} (CEST, local)",
       None, None, "J8", ["src-lnr-prod2"], "2026-10-22T21:34Z/2026-10-22T21:35Z",
       "official-only" if miss else "olbg", olbg_of("rugby-union", P2_OLBG[fid]),
       flags_=["F-8F6D-12"] if miss else [], olbg_missing=miss,
       notes=[f"Official table positions on the fixture page: {a} {pa}e, {b} {pb}e."])
fx("prem-new-sale", "rugby-union", "Rugby Union", "Gallagher Premiership", "Newcastle Red Bulls",
   "Sale Sharks", None, None, None, None, None, None, ["src-premrugby"],
   "2026-10-22T21:48Z (JS shell, no fixture rows)", "discovery-only-unverified", olbg_of("rugby-union", 609573),
   flags_=["F-8F6D-05"], blank=["date", "start time", "participant confirmation", "status"])

# ================================================================ GOLF ===
fx("gf-stifel", "golf", "Golf", "PGA TOUR Champions", None, None, None, None, None,
   "Norwood Hills Country Club, St. Louis, Missouri", None, "Tournament (outright)",
   ["src-pgc-hub"], "2026-10-22T21:40Z/2026-10-22T21:41Z", "olbg", olbg_of("golf", 101903),
   flags_=["F-8F6D-10", "F-8F6D-15"],
   blank=["official date", "official start time"],
   notes=["Official Schwab Cup top-10 through 18 Oct: 1 Stewart Cink (16 top-10s, 5 wins, 3 runner-up), "
          "2 Zach Johnson, 3 Steven Alker / George McNeill, 5 Retief Goosen (src-pgc-hub).",
          "OLBG '25 Oct 17:45', pick Stewart Cink (3/13 tips) is discovery only."])
fx("gf-bermuda", "golf", "Golf", "PGA TOUR", None, None, "2026-10-22", None, "22-25 October 2026",
   "Port Royal Golf Course, Southampton, Bermuda", None, "Tournament (outright)",
   ["src-pga-schedule"], "2026-10-22T07:17:40Z/2026-10-22T07:30:30Z", "official-only", None,
   flags_=["F-8F6D-12"], olbg_missing=True,
   notes=["Butterfield Bermuda Championship; not visible in the OLBG golf hub capture."])

# ========================================================== MOTOR RACING ===
fx("mr-us-gp", "motor-racing", "Motor Racing", "Formula 1", None, None, "2026-10-25", None,
   "Race 16:00 (as listed on official page)", "Circuit of The Americas", "Scheduled",
   "United States Grand Prix 2026 — race", ["src-f1-usgp"], "2026-10-22T21:01Z/2026-10-22T21:02Z",
   "olbg", olbg_of("motor-racing", 913),
   flags_=["F-8F6D-09", "F-8F6D-15"],
   blank=["start_utc (timezone context ambiguous on official page)"],
   notes=["Official schedule rows read: FP1 23 Oct 13:30-14:30, FP2 17:00-18:00, FP3 24 Oct 13:30-14:30, "
          "Qualifying 17:00-18:00, Race 25 Oct 16:00 (page's MY TIME/TRACK TIME toggle — flagged)."])

# ================================================================ DARTS ===
DARTS = [("gd-1", "Ryan Joyce", "Jermaine Wattimena", 32332, 1),
         ("gd-2", "Krzysztof Ratajski", "Dave Chisnall", 32333, 2),
         ("gd-3", "Nathan Aspinall", "Cristo Reyes", 32327, 3),
         ("gd-4", "Jonny Clayton", "Niko Springer", 32335, 4),
         ("gd-5", "Luke Littler", "William OConnor", 32328, 5),
         ("gd-6", "Wessel Nijman", "Martin Schindler", 32326, 6),
         ("gd-7", "Kevin Doets", "Michael van Gerwen", 32331, 7),
         ("gd-8", "Josh Rock", "Chris Dobey", 32336, 8)]
for fid, a, b, eid, seq in DARTS:
    fx(fid, "darts", "Darts", "PDC Machineseeker European Championship", a, b, "2026-10-23",
       None, "Session 19:00-23:00 CEST (17:00-21:00Z); per-match start not printed", "Westfalenhalle, Dortmund",
       None, f"Round One, tie {seq} of 8 (Friday session order as published)",
       ["src-pdc-ec-schedule"], "2026-10-22T07:17:40Z (canonical) + 2026-10-22T21:1xZ indexed reads",
       "olbg", olbg_of("darts", eid),
       flags_=["F-8F6D-03", "F-8F6D-15"],
       blank=["per-match start time (official page publishes session window only)"],
       notes=["Official context: 32-player field, £750,000, Westfalenhalle, 22-25 Oct; Littler listed as world "
              "number one, Nijman as number two seed (official schedule article)."])

# ============================================================== HANDBALL ===
HB = [("hb-lim-dun", "Limoges 87", "Dunkerque", "2026-10-23", "20h00", 5, 16, False),
      ("hb-aix-tou", "Pays dAix UC", "Toulouse", "2026-10-23", "20h00", 8, 13, False),
      ("hb-cha-nim", "Chartres", "USAM Nimes", "2026-10-23", "20h00", 6, 4, False),
      ("hb-sel-cae", "Selestat Alsace", "Caen", "2026-10-23", "20h30", 9, 12, False),
      ("hb-tre-ces", "Tremblay", "Cesson Rennes", "2026-10-23", "20h30", 7, 15, False),
      ("hb-nan-cha", "Nantes", "Chambery Savoie", "2026-10-24", "19h00", 2, 10, False)]
HB_OLBG = {"hb-lim-dun": 12080, "hb-aix-tou": 12083, "hb-cha-nim": 12079,
           "hb-sel-cae": 12085, "hb-tre-ces": 12086, "hb-nan-cha": 12082}
for fid, a, b, date, tt, pa, pb, miss in HB:
    hh, mm = int(tt[:2]), int(tt[3:])
    start = f"{date}T{hh - 2:02d}:{mm:02d}:00Z"
    fx(fid, "handball", "Handball", "Daikin StarLigue J08", a, b, date, start, f"{tt} (CEST, local)",
       None, None, "Journée 8", ["src-lnh-starligue-cal", "src-lnh-starligue-table"],
       "2026-10-22T21:39Z/2026-10-22T21:56Z", "olbg", olbg_of("handball", HB_OLBG[fid]),
       notes=[f"Official table after 7 rounds: {a} {pa}e, {b} {pb}e (src-lnh-starligue-table)."])
HB_UNVER = [("hb-skive-aal", "Skive FH", "Aalborg Handbold", "Denmark Ligaen", 12076, "Denmark (ligabold.dk not fetched)"),
            ("hb-gop-eis", "Frisch Auf Goppingen", "ThSV Eisenach", "Germany Bundesliga", 12088, "Germany (hbl.de irregularity, F-8F6D-06)"),
            ("hb-han-lem", "TSV Hannover Burgdorf", "TBV Lemgo Lippe", "Germany Bundesliga", 12093, "Germany (hbl.de irregularity, F-8F6D-06)"),
            ("hb-erl-kiel", "HC Erlangen", "THW Kiel", "Germany Bundesliga", 12091, "Germany (hbl.de irregularity, F-8F6D-06)"),
            ("hb-skj-rib", "Skjern Handbold", "Ribe Esbjerg HH", "Denmark Ligaen", 12077, "Denmark (ligabold.dk not fetched)"),
            ("hb-vep-psa", "Villa De Aranda", "Puerto Sagunto", "Spain ASOBAL", 12107, "Spain (asobal.es not fetched)"),
            ("hb-bid-crd", "Bidasoa Irun", "Caserio Ciudad Real", "Spain ASOBAL", 12101, "Spain (asobal.es not fetched)"),
            ("hb-nav-val", "BM Nava", "Atletico Valladolid", "Spain ASOBAL", 12104, "Spain (asobal.es not fetched)"),
            ("hb-est-kos", "Estonia W", "Kosovo W", "International women's", 12110, "Estonia/Kosovo federations not fetched")]
for fid, a, b, comp, eid, why in HB_UNVER:
    fx(fid, "handball", "Handball", comp, a, b, None, None, None, None, None, None, [], None,
       "discovery-only-unverified", olbg_of("handball", eid), flags_=["F-8F6D-05"],
       blank=["date", "start time", "participant confirmation", "status"],
       notes=[f"Official verification unresolved: {why}."])

# ============================================================= VOLLEYBALL ===
VB_UNVER = [("vb-bra-ses", "Brasilia W", "Sesc RJ Flamengo W", "Brazil women", 37001),
            ("vb-sle-gks", "Slepsk Suwalki", "GKS Katowice", "Poland PlusLiga (assumed)", 36963),
            ("vb-pau-min", "Paulistano-Barueri W", "Minas W", "Brazil women", 37000),
            ("vb-skra-pro", "PGE Skra Belchatow", "Projekt Warszawa", "Poland PlusLiga (assumed)", 36964),
            ("vb-mac-osa", "Mackenzie W", "Osasco W", "Brazil women", 37002),
            ("vb-abp-pra", "Abel-Moda Brusque W", "Praia Clube W", "Brazil women", 37003),
            ("vb-tre-cis", "Trentino", "Cisterna", "Italy SuperLega (assumed)", 36994),
            ("vb-per-por", "Perugia", "Pordenone", "Italy SuperLega (assumed)", 36997),
            ("vb-chk-res", "CHKS Chelm", "Resovia Rzeszow", "Poland (assumed)", 36965),
            ("vb-tii-kyk", "Tiikerit", "KyKy", "Finland (assumed)", 37007),
            ("vb-atl-lin", "ATSC Klagenfurt Women", "Linz Steg W", "Austria women (assumed)", 37015),
            ("vb-sok-har", "SG Sokol-Post W", "TSV Hartberg W", "Austria women (assumed)", 37017),
            ("vb-fri-kar", "VfB Friedrichshafen", "SSC Karlsruhe", "Germany Bundesliga (assumed)", 37010),
            ("vb-lun-warn", "SVG Luneburg", "SV Warnemunde", "Germany Bundesliga (assumed)", 37011)]
for fid, a, b, comp, eid in VB_UNVER:
    fl = ["F-8F6D-18"] if fid in ("vb-sle-gks", "vb-skra-pro", "vb-chk-res") else ["F-8F6D-05"]
    fx(fid, "volleyball", "Volleyball", comp, a, b, None, None, None, None, None, None,
       ["src-plusliga"] if "Poland" in comp else [], 
       "2026-10-22T21:45Z (chunk 0 of 16: completed matches only)" if "Poland" in comp else None,
       "discovery-only-unverified", olbg_of("volleyball", eid), flags_=fl,
       blank=["date", "start time", "participant confirmation", "status"],
       notes=["Official federation fixture page not completed this session (see flag)."])

# =========================================================== AUSSIE RULES ===
fx("af-port-col", "aussie-rules", "Aussie Rules", "2026 NAB AFLW Season Round 11", "Port Adelaide",
   "Collingwood", "2026-10-23", None, "Friday 23 October 2026 • 4:15 AM (EDT)", "Alberton Oval, Adelaide (Kaurna)",
   None, "Round 11", ["src-aflw-match"], "2026-10-22T21:41Z/2026-10-22T21:42Z",
   "official-only", None, flags_=["F-8F6D-12"], olbg_missing=True,
   notes=["Official match centre shows a live countdown; ladder input not retrievable (src-aflw-ladder) so the row is unpriced."])

# ========================================================= GAELIC FOOTBALL ===
fx("gf-cork-final", "gaelic-football", "Gaelic Football", "2026 Cork Premier Senior Football Championship Final",
   "St Finbarrs", "Nemo Rangers", "2026-10-25", None, "4:00pm", "SuperValu Páirc Uí Chaoimh",
   None, "Final", ["src-munster-gaa"], "2026-10-22T21:44Z/2026-10-22T21:45Z",
   "olbg", olbg_of("gaelic-football", 3530), flags_=["F-8F6D-15"],
   blank=["start_utc (page states no timezone)"],
   notes=["OLBG text '25 Oct 16:00' agrees with the official 4:00pm listing."])
fx("gf-kerry-final", "gaelic-football", "Gaelic Football", "2026 Kerry County Senior Football Championship Final",
   "Dr. Crokes", "Kenmare Shamrocks", "2026-10-25", None, "2:00pm", "Fitzgerald Stadium Killarney",
   None, "Final", ["src-munster-gaa"], "2026-10-22T21:10Z/2026-10-22T21:11Z",
   "official-only", None, flags_=["F-8F6D-12"], olbg_missing=True,
   blank=["start_utc (page states no timezone)"])
fx("gf-waterford-final", "gaelic-football", "Gaelic Football", "2026 Waterford Senior Football Championship Final",
   "Rathgormack", "The Nire", "2026-10-25", None, "2:30pm",
   "Cappoquin Logistics Fraher Field, Dungarvan", None, "Final",
   ["src-munster-gaa"], "2026-10-22T21:10Z/2026-10-22T21:11Z", "olbg", olbg_of("gaelic-football", 3536),
   flags_=["F-8F6D-02", "F-8F6D-15"], blank=["start_utc (page states no timezone)"],
   notes=["Official date/time published; OLBG '01 Nov 15:30' contradicts it (F-8F6D-02)."])
fx("gf-moy-sal", "gaelic-football", "Gaelic Football", "GAA club (assumed Galway)", "Moycullen",
   "Salthill-Knocknacarra", None, None, None, None, None, None, ["src-gaagalway"],
   "2026-10-22T21:50Z (fetch failure)", "discovery-only-unverified", olbg_of("gaelic-football", 3532),
   flags_=["F-8F6D-05"], blank=["date", "start time", "participant confirmation", "status"])
fx("gf-kant-eog", "gaelic-football", "Gaelic Football", "GAA club (assumed Cork)", "Kanturk", "Eire Og Cor",
   None, None, None, None, None, None, [], None, "discovery-only-unverified",
   olbg_of("gaelic-football", 3531), flags_=["F-8F6D-05"],
   blank=["date", "start time", "participant confirmation", "status"],
   notes=["OLBG text '01 Nov 14:00'; county board source not fetched this session."])
fx("gf-frc-kil", "gaelic-football", "Gaelic Football", "GAA club (assumed Limerick)", "Fr Caseys",
   "Kildimo Pallaskenry", None, None, None, None, None, None, [], None, "discovery-only-unverified",
   olbg_of("gaelic-football", 3537), flags_=["F-8F6D-05"],
   blank=["date", "start time", "participant confirmation", "status"],
   notes=["OLBG text '01 Nov 15:30'; county board source not fetched this session."])

# ============================================================== SNOOKER ===
SN = [("sn-qf-1", "Anthony McGill", "Kyren Wilson", "08:00", "Match 57"),
      ("sn-qf-2", "Sam Craigie", "Elliot Slessor", "08:00", "Match 58"),
      ("sn-qf-3", "David Gilbert", "Mark Williams", "14:00", "Match 59")]
for fid, a, b, tt, mnum in SN:
    fx(fid, "snooker", "Snooker", "BetVictor Northern Ireland Open 2026", a, b, "2026-10-23", None,
       tt, None, None, f"Quarter-finals ({mnum})", ["src-wst-ni-open"],
       "2026-10-22T21:09Z/2026-10-22T21:12Z", "official-only", None,
       flags_=["F-8F6D-07", "F-8F6D-12"], olbg_missing=True,
       blank=["start_utc (page states no timezone)"],
       notes=["A fourth quarter-final is listed as 'Winner of match 55 v Winner of match 56' and is not published "
              "until those ties finish (Jones-Wells and Brown-Donaldson were live at capture)."])

# ------------------------------------------------------------- write out ---
os.makedirs(OUT, exist_ok=True)
json.dump({"generated_at": GEN, "session": "8f6d7364-olbg1", "task": "T66",
           "window_utc": "2026-10-22T21:00Z/2026-10-29T21:00Z",
           "count": len(FIX), "fixtures": FIX},
          open(os.path.join(OUT, "fixtures.json"), "w"), indent=1, ensure_ascii=False)
json.dump({"generated_at": GEN, "count": len(SOURCES_J), "sources": SOURCES_J},
          open(os.path.join(OUT, "sources.json"), "w"), indent=1, ensure_ascii=False)
json.dump({"generated_at": GEN, "count": len(FLAGS), "flags": FLAGS},
          open(os.path.join(OUT, "flagged.json"), "w"), indent=1, ensure_ascii=False)

# ================================================== model inputs (official) ==
inputs = {
    "generated_at": GEN,
    "model_version": "8f6d7364-v1.0",
    "nhl_standings_observed": "2026-10-22T20:56Z/2026-10-22T21:04Z (standingsDateTimeUtc 20:57:30Z)",
    "nhl": {  # team: [W, L, OTL, GP, L10_W, L10_L, L10_OTL, streak] — read verbatim from src-nhl-standings
        "NSH": [3, 4, 1, 8, 4, 2, 2, "W1"], "BOS": [7, 2, 1, 10, 7, 2, 1, "OT1"],
        "NYR": [7, 3, 1, 11, 7, 2, 1, "W1"], "TOR": [5, 4, 2, 11, 5, 3, 2, "W2"],
        "SJS": [5, 4, 1, 10, 5, 4, 1, "W1"], "OTT": [7, 3, 0, 10, 7, 3, 0, "W1"],
        "ANA": [4, 5, 0, 9, 4, 5, 0, "L4"], "NJD": [5, 4, 0, 9, 5, 4, 0, "W1"],
        "FLA": [5, 3, 2, 10, 5, 3, 2, "L1"], "PIT": [3, 6, 1, 10, 3, 6, 1, "L4"],
        "LAK": [1, 5, 1, 7, 1, 5, 1, "W1"], "NYI": [5, 3, 1, 9, 5, 3, 1, "W2"],
        "VGK": [8, 3, 0, 11, 7, 3, 0, "L1"], "STL": [4, 4, 1, 9, 4, 4, 1, "W1"],
        "WPG": [4, 4, 2, 10, 4, 4, 2, "L2"], "DAL": [5, 3, 1, 9, 5, 3, 1, "W3"],
        "MIN": [6, 2, 2, 10, 6, 2, 2, "OT1"], "CGY": [2, 6, 0, 8, 2, 6, 0, "W1"],
        "CAR": [8, 2, 1, 11, 8, 2, 0, "W1"], "EDM": [7, 1, 1, 9, 7, 1, 1, "W2"],
        "UTA": [7, 3, 0, 10, 7, 3, 0, "W1"], "SEA": [6, 3, 1, 10, 6, 3, 1, "W1"],
        "DET": [3, 5, 1, 9, 3, 5, 1, "OT1"], "VAN": [2, 8, 1, 11, 1, 8, 1, "L2"],
    },
    "mlb_records_observed": "2026-10-22T07:17:40Z/2026-10-22T07:30:30Z (canonical same-day, src-mlb-records)",
    "mlb": {"TB": {"w": 98, "l": 64, "rs": 736, "ra": 650, "gp": 162},
            "MIL": {"w": 103, "l": 59, "rs": 832, "ra": 618, "gp": 162}},
    "euroleague_records_observed": "2026-10-22T21:05Z/2026-10-22T21:08Z (src-el-gamecenter)",
    "euroleague": {"Zalgiris Kaunas": [2, 4], "LDLC ASVEL Villeurbanne": [2, 4],
                   "Olympiacos Piraeus": [5, 1], "Fenerbahce Tarfin Istanbul": [5, 1],
                   "Paris Basketball": [1, 5], "Valencia Basket": [5, 1]},
    "urc_table_observed": "2026-10-22T21:32Z/2026-10-22T21:33Z (src-urc-table)",
    "urc": {  # club: [W, D, L, PF, PA, form] — full table verbatim
        "Edinburgh Rugby": [3, 0, 0, 80, 54, "WWW"], "Glasgow Warriors": [2, 1, 0, 95, 72, "WDW"],
        "Vodacom Bulls": [2, 0, 1, 126, 54, "WLW"], "DHL Stormers": [2, 0, 1, 81, 54, "WLW"],
        "Hollywoodbets Sharks": [2, 0, 1, 89, 83, "WWL"], "Cardiff Rugby": [2, 0, 1, 66, 71, "WWL"],
        "10bet Lions": [2, 0, 1, 77, 102, "WWL"], "Dragons RFC": [1, 1, 1, 88, 83, "DWL"],
        "Munster Rugby": [1, 1, 1, 72, 74, "LWD"], "Leinster Rugby": [1, 0, 2, 75, 58, "LLW"],
        "Ulster Rugby": [0, 2, 1, 88, 93, "LDD"], "Scarlets": [1, 0, 2, 68, 85, "LLW"],
        "Ospreys": [1, 0, 2, 81, 107, "LLW"], "Connacht Rugby": [1, 0, 2, 56, 84, "LWL"],
        "Benetton Rugby": [0, 1, 2, 64, 68, "DLL"], "Zebre Parma": [0, 0, 3, 52, 116, "LLL"],
    },
    "top14_positions": {"RC Vannes": 14, "ASM Clermont": 11, "Aviron Bayonnais": 5, "LOU Rugby": 8,
                        "Castres Olympique": 13, "Stade Français Paris": 6, "Racing 92": 12,
                        "Montpellier Hérault Rugby": 7, "Stade Toulousain": 1, "USA Perpignan": 9,
                        "RC Toulon": 10, "Section Paloise": 2, "Stade Rochelais": 4, "Union Bordeaux-Bègles": 3},
    "prod2_positions": {"RC Narbonnais": 15, "CA Brive": 5, "SU Agen": 10, "Nissa Rugby": 13,
                        "Soyaux-Angoulême XV": 8, "US Dax": 7, "Stade Aurillacois": 9, "USON Nevers": 16,
                        "Valence Romans": 11, "Colomiers Rugby": 12, "Provence Rugby": 2,
                        "AS Béziers Hérault": 14, "FC Grenoble Rugby": 3, "Biarritz Olympique PB": 6},
    "lnh_table_observed": "2026-10-22T21:54Z/2026-10-22T21:56Z (src-lnh-starligue-table)",
    "lnh": {"Paris": [7, 0, 0, 239, 190], "Nantes": [6, 1, 0, 244, 203], "Montpellier": [4, 1, 2, 234, 205],
            "Nimes": [5, 2, 0, 228, 228], "Limoges": [4, 3, 0, 234, 214], "Chartres": [3, 3, 1, 204, 224],
            "Tremblay": [3, 3, 1, 231, 227], "Aix": [3, 4, 0, 227, 223], "Selestat": [3, 4, 0, 208, 217],
            "Chambery": [2, 3, 2, 224, 231], "Saran": [3, 4, 0, 202, 216], "Caen": [3, 4, 0, 198, 235],
            "Toulouse": [3, 4, 0, 198, 201], "Saint-Raphael": [2, 5, 0, 207, 225],
            "Cesson Rennes": [1, 6, 0, 209, 227], "Dunkerque": [1, 6, 0, 175, 196]},
    "irl_rankings_observed": "2026-10-22T21:34Z/2026-10-22T21:35Z (src-irl-rankings)",
    "irl_men": {"Australia": 100, "New Zealand": 82, "England": 70, "Samoa": 56, "Tonga": 54,
                "PNG": 47, "Fiji": 34, "Cook Islands": 24, "France": 21, "Wales": 18,
                "Lebanon": 7, "Czech Republic": 6, "Serbia": 20, "Netherlands": 23, "Italy": 11,
                "Scotland": 8, "Jamaica": 9, "Greece": 14, "Malta": 14, "Canada": 13},
    "irl_women": {"Australia": 100, "New Zealand": 64, "England": 40, "France": 25, "Samoa": 22,
                  "PNG": 19, "Canada": 19, "Ireland": 18, "Wales": 17, "Fiji": 13,
                  "Tonga": 12, "USA": 12, "Greece": 11, "Netherlands": 10, "Scotland": 8,
                  "Serbia": 4, "Kenya": 4, "Ghana": 4, "Brazil": 3, "Jamaica": 3, "Italy": 2,
                  "Philippines": 2, "Lebanon": 2, "Uganda": 1, "Malta": 1, "Turkey": 1},
    "tennis_rank_basis": {
        "observed": "WTA draw PDFs (src-wta-osaka-draw, src-wta-ningbo-draw) + ATP event seeds/draws (src-atp-*-draw/sched)",
        "official_ranks": {"Ann Li": 31, "Talia Gibson": 41, "Katie Boulter": 54,
                            "Elena Rybakina": 1, "Iva Jovic": 11, "Diana Shnaider": 13},
        "assumption_unseeded": "unseeded/qualifier in a 32-draw ranked one place below that draw's lowest official seed (documented model assumption, not a fact)",
        "assumption_notes": "Osaka lowest seed rank 54 -> unseeded default 59, qualifier default 69; Ningbo lowest seed rank 16 -> unseeded default 21, qualifier default 31; ATP: seed slot n mapped to that event's seed ladder with unseeded default 21.",
        "atp_seeds": {"Daniil Medvedev": 1, "Stefanos Tsitsipas": 7, "Jiri Lehecka": 2,
                      "Tommy Paul": 4, "Taylor Fritz": 2},
    },
    "official_odds_note": ("Official NHL-embedded odds read verbatim from src-nhl-schedule under 'official_odds' "
                           "in this file; providers are not identified by the API. Decimal providers [3,6,10], "
                           "American providers [7,8,9]. Used only as a market cross-check, never as our price."),
    "official_odds": {fid: odds for fid, _, _, _, _, odds, _ in NHL},
}
json.dump(inputs, open(os.path.join(OUT, "inputs.json"), "w"), indent=1, ensure_ascii=False)
print(f"fixtures={len(FIX)} sources={len(SOURCES_J)} flags={len(FLAGS)}")
by = {}
for f in FIX:
    by[f["discovery"]] = by.get(f["discovery"], 0) + 1
print(by)
sports = {}
for f in FIX:
    sports[f["sport"]] = sports.get(f["sport"], 0) + 1
print(sports)
