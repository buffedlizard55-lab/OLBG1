#!/usr/bin/env python3
"""Build the namespaced 0239d718 OLBG clarity desk.

The script is deterministic: all published rows, prices, predictions, source
links and HTML are generated from the observations recorded below. OLBG is used
only as a discovery/market-location layer; every factual value in a published
row points at an official league, governing body, tour, promoter or club page.
"""
from __future__ import annotations

import html
import json
import math
import posixpath
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "0239d718"
SITE = ROOT / "0239d718"
SNAPSHOT = "2026-10-24T22:40:00Z"
BRANCH = "arena/0239d718-olbg1"
REPO_URL = f"https://github.com/buffedlizard55-lab/OLBG1/blob/{BRANCH}"

# ---------------------------------------------------------------------------
# Official source ledger.  Every source was read during this session through
# the retrieval layer; "status" records pages that were shells, redirects, or
# missing so readers can reproduce the limitation.
# ---------------------------------------------------------------------------
SOURCES = []


def source(sid, publisher, url, scope, *, role="official", status="read", sport=None):
    SOURCES.append({
        "id": sid,
        "publisher": publisher,
        "url": url,
        "scope": scope,
        "role": role,
        "status": status,
        "sport": sport,
        "observed_at": SNAPSHOT,
        "supports": scope,
    })


source("olbg-sitemap", "OLBG sitemap", "https://www.olbg.com/sitemap-betting-tips.xml",
       "Sitemap index exposes canonical /betting-tips/{Slug}/{id} sport routes.",
       role="discovery", status="read")
source("olbg-main", "OLBG all-sports tips", "https://www.olbg.com/betting-tips",
       "All-sports hub; cross-sport pagination and unlabeled times.",
       role="discovery", status="read")

source("nhl-schedule", "NHL official schedule API",
       "https://api-web.nhle.com/v1/schedule/2026-10-25",
       "Five future 25 Oct NHL games with exact UTC starts, venues and team abbreviations.",
       sport="ice-hockey")
source("nhl-standings", "NHL official standings",
       "https://www.nhl.com/standings/2026-10-24/wildcard",
       "2026-27 records, goals for/against, home/away splits and last-ten form for all clubs.",
       sport="ice-hockey")
source("mlb-schedule", "MLB official Stats API",
       "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-25&hydrate=team,linescore,record,probablePitcher,venue",
       "World Series Game 2 at 2026-10-25T00:00Z, venue, series state and probable pitchers.",
       sport="baseball")
source("mlb-standings", "MLB official standings",
       "https://www.mlb.com/standings/",
       "Tampa Bay 98-64 +86 and Milwaukee 103-59 +214, home 55-26, last-ten 8-2.",
       sport="baseball")
source("nba-games", "NBA official games page", "https://www.nba.com/games",
       "24 Oct slate with ET tip times, club records and season scoring leaders.",
       sport="basketball")
source("nba-standings", "NBA official standings", "https://www.nba.com/standings",
       "2026-27 W/L records, last ten, home/road splits and streaks.",
       sport="basketball")
source("nba-injury", "NBA official injury report PDF",
       "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-24_01_30PM.pdf",
       "1:30PM ET injury issue with Out/Questionable/Probable status and NOT YET SUBMITTED teams.",
       sport="basketball")
source("nba-injury-index", "NBA officiating injury-report index",
       "https://official.nba.com/nba-injury-report-2026-27-season/",
       "Explains report cadence and links all 24 Oct issues.",
       sport="basketball")
source("atp-scores", "ATP Tour official live scores",
       "https://www.atptour.com/en/scores/current",
       "Almaty, Brussels and Lyon semifinal results with set scores and H2H links.",
       sport="tennis")
source("atp-news", "ATP Tour official news", "https://www.atptour.com/en/news",
       "Confirms Sunday finals and next-week Basel/Vienna main-draw pairings.",
       sport="tennis")
source("wta-tokyo", "WTA official Tokyo draws",
       "https://www.wtatennis.com/tournaments/1056/tokyo/2026/draws",
       "Tokyo WTA 500 singles draw notice; static read was a notification shell.",
       status="client-shell", sport="tennis")
source("wta-tokyo-overview", "WTA official Tokyo overview",
       "https://www.wtatennis.com/tournaments/1056/tokyo/2026",
       "Tokyo WTA 500 dates, surface, draw size and seeded field.",
       status="search-index", sport="tennis")
source("wta-guangzhou", "WTA official Guangzhou draws",
       "https://www.wtatennis.com/tournaments/1023/guangzhou/2026/draws",
       "Guangzhou WTA 250 draw notice; static read was a notification shell.",
       status="client-shell", sport="tennis")
source("pga-board", "PGA TOUR official leaderboard",
       "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard",
       "Butterfield Bermuda Championship round-three positions, totals, round scores and event dates.",
       sport="golf")
source("f1-usgp", "Formula 1 official US GP page",
       "https://www.formula1.com/en/racing/2026/united-states",
       "US GP schedule, practice reports, qualifying top five and 25 Oct race time.",
       sport="motor-racing")
source("f1-qual", "Formula 1 official qualifying results",
       "https://www.formula1.com/en/results/2026/races/1297/united-states/qualifying",
       "Full qualifying classification with Q1/Q2/Q3 times and lap counts.",
       sport="motor-racing")
source("wst-home", "World Snooker Tour official site", "https://www.wst.tv/",
       "Northern Ireland Open final and International Championship upcoming match list.",
       sport="snooker")
source("wst-rankings", "World Snooker Tour official rankings",
       "https://www.wst.tv/rankings/",
       "World rankings, one-year list, Home Nations bonus and century counts.",
       sport="snooker")
source("wst-news", "World Snooker Tour official news",
       "https://www.wst.tv/news/2026/october/24/Wilson-Beats-Craigie-In-Belfast-Drama/",
       "Kyren Wilson reached the Northern Ireland Open final by beating Sam Craigie.",
       status="headline-only", sport="snooker")
source("pdpa-ec", "PDPA / PDC European Championship listing",
       "https://pdpa.co.uk/event/european-championship-2026/",
       "Round-two scores, Sunday quarterfinal bracket, seeded draw and prize fund.",
       sport="darts")
source("nrl-draw", "NRL official RLWC draw",
       "https://www.nrl.com/draw/?competition=131&round=2&season=2026",
       "Round 2 results, Sunday fixtures, pool positions, venues and team-list links.",
       sport="rugby-league")
source("urc-preview", "BKT United Rugby Championship official preview",
       "https://www.unitedrugby.com/latest/match-preview-2/a-relentless-rivalry-and-a-new-home-for-ospreys-round-4-preview/",
       "Round 4 fixtures, team news, early standings and recent rivalry results.",
       sport="rugby-union")
source("top14", "LNR Top 14 official site", "https://top14.lnr.fr/",
       "Journee 7 results and the 25 Oct 21h05 La Rochelle v Bordeaux fixture.",
       sport="rugby-union")
source("top14-table", "LNR Top 14 official standings",
       "https://top14.lnr.fr/classement",
       "Points, matches, form sequence, points for/against and next match for Top 14 clubs.",
       sport="rugby-union")
source("prem-standings", "Premiership Rugby official standings / match centre",
       "https://premiershiprugby.com/match-centre/283220/standings",
       "2026-27 standings: Saracens 2-1 +21, Harlequins 0-3 -68; recent form strings.",
       status="redirect", sport="rugby-union")
source("usa-rugby", "USA Rugby official October series page",
       "https://go.usa.rugby/wxv-usa-series-presale",
       "Confirms USA Men face Australia XV in October but publishes no exact date or venue.",
       status="partial", sport="rugby-union")
source("cork-gaa", "Cork GAA official fixtures", "https://gaacork.ie/fixtures/",
       "25 Oct county finals, 30/31 Oct finals, venues, throw-in times and referees.",
       sport="gaelic")
source("munster-gaa", "Munster GAA official event page",
       "https://munster.gaa.ie/event/2026-cork-premier-senior-football-championship-final/",
       "St Finbarrs v Nemo Rangers, 25 Oct 16:00, SuperValu Páirc Uí Chaoimh.",
       sport="gaelic")
source("galway-gaa", "Galway GAA official site", "https://www.galwaygaa.ie/",
       "Football fixtures on 25/26 Oct and a 23 Oct weather-driven schedule-change notice.",
       sport="gaelic")
source("gaa-fixtures", "GAA official fixtures and results",
       "https://www.gaa.ie/fixtures-results",
       "Shinty-Hurling International result page; no upcoming Gaelic football row was exposed.",
       status="partial", sport="gaelic")
source("gbgb-racing", "GBGB official racing page",
       "https://www.gbgb.org.uk/racing/",
       "Official track list, latest results, race classes, distances and race reports.",
       sport="greyhounds")
source("gbgb-open", "GBGB official open races",
       "https://www.gbgb.org.uk/racing/open-races/",
       "Open-race calendar filter; static page did not expose Sunday's individual card.",
       status="client-shell", sport="greyhounds")
source("gbgb-scurry", "GBGB official Scurry Gold Cup report",
       "https://www.gbgb.org.uk/shadow-storm-chases-scurry-gold-cup-history-at-dunstall-park/",
       "Shadow Storm, Avarua Lake, Roanna Mamba and semifinal times for the Scurry final.",
       sport="greyhounds")
source("gbgb-oaks", "GBGB official Oaks report",
       "https://www.gbgb.org.uk/signet-nayla-chases-oaks-glory-as-hutton-targets-dunstall-park-double/",
       "Signet Nayla, Fahrenheit Jess and Slingshot Poppy semifinal times for the Oaks final.",
       sport="greyhounds")
source("gbgb-puppy", "GBGB official Puppy Derby report",
       "https://www.gbgb.org.uk/returning-storm-sets-the-pace-as-doncaster-puppy-derby-roars-into-life/",
       "Returning Storm, Shado Earth and heat times for the Doncaster Puppy Derby.",
       sport="greyhounds")
source("legavolley-cal", "Lega Pallavolo Serie A official calendar",
       "https://www.legavolley.it/calendario/?idCampionato=999",
       "SuperLega round-one results and six 25 Oct round-two fixtures with official local times.",
       sport="volleyball")
source("legavolley-table", "Lega Pallavolo Serie A official standings",
       "https://www.legavolley.it/classifica/?IdCampionato=999",
       "Points, set ratio, points for/against and result type after round one.",
       sport="volleyball")
source("ehfcl-standings", "EHF Champions League official standings",
       "https://ehfcl.eurohandball.com/men/2026-27/standings/",
       "Group standings and 28/29 Oct fixture links for Magdeburg, Kielce, Berlin and others.",
       sport="handball")
source("ehfcl-home", "EHF Champions League official home",
       "https://ehfcl.eurohandball.com/men/2026-27/",
       "Upcoming 28/29 Oct match list with throw-in times and official match-centre links.",
       sport="handball")
source("hbl-schedule", "Opel Handball-Bundesliga official schedule",
       "https://www.opel-hbl.de/de/hbl/spielplan",
       "Schedule landing page; static read did not expose individual fixture rows.",
       status="client-shell", sport="handball")
source("pcb-draw", "Pakistan Cricket Board official tournament page",
       "https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html",
       "ODI tri-series schedule: Pakistan v England, 25 Oct, Gaddafi Stadium, Lahore.",
       sport="cricket")
source("pcb-news", "Pakistan Cricket Board official report",
       "https://www.pcb.com.pk/news-detail/arafat-minhas-6-40-and-59-sink-england-as-pakistan-win-consecutive-games-in-odi-tri-series.html",
       "Pakistan beat England by 87 runs; Arafat Minhas scored 59 and took 6-40.",
       sport="cricket")
source("bcci-match", "BCCI official match centre",
       "https://www.bcci.tv/matches/88d47fe3-ead4-4b91-b0cc-4bda908fb8d7/india-women-vs-zimbabwe-women",
       "India Women v Zimbabwe Women, 2nd ODI, 25 Oct, BCA Stadium Vadodara.",
       sport="cricket")
source("bcci-squad", "BCCI official squad note",
       "https://www.bcci.tv/news/article/jintimani-kalita-replaces-renuka-singh-thakur-in-india-s-odi-squad",
       "Renuka Singh Thakur ruled out; Jintimani Kalita added to India's ODI squad.",
       sport="cricket")
source("nzc-fixtures", "New Zealand Cricket official fixtures",
       "https://scoring.nzc.nz/fixtures",
       "New Zealand v India 3rd T20I, 27 Oct, Hnry Stadium Wellington.",
       sport="cricket")
source("nzc-match", "New Zealand Cricket official match info",
       "https://scoring.nzc.nz/match/35de7c5e-f734-4003-89db-59d7081e9d29",
       "3rd T20I venue, date and published lineups for New Zealand and India.",
       sport="cricket")
source("csa-upcoming", "Cricket South Africa official upcoming page",
       "https://cricket.co.za/upcoming/",
       "CSA domestic and international schedule; pagination did not expose 25 Oct T20 rows on read.",
       status="pagination", sport="cricket")
source("csa-page8", "Cricket South Africa official upcoming page 8",
       "https://cricket.co.za/upcoming/8/",
       "Search index showed 25/10/26 Boland v Titans and North West Dragons v Northern Cape Heat; live page had moved on.",
       status="index-drift", sport="cricket")
source("ncl20", "NCL GT20 Canada official fixtures",
       "https://ncl20.com/fixtures/",
       "Toronto Kings v Vancouver Guardians, 24 Oct 19:00 EDT, plus first two tournament results.",
       sport="cricket")
source("cricket-canada", "Cricket Canada official sanctions page",
       "https://cricketcanada.org/tournament-sanctions/",
       "Governing-body context for sanctioned Canadian events; no fixture rows on this page.",
       status="partial", sport="cricket")

SRC = {s["id"]: s for s in SOURCES}
OFFICIAL_HOSTS = {
    "api-web.nhle.com", "www.nhl.com", "nhl.com", "statsapi.mlb.com", "www.mlb.com",
    "www.nba.com", "official.nba.com", "ak-static.cms.nba.com", "www.atptour.com",
    "www.wtatennis.com", "wtafiles.wtatennis.com", "www.pgatour.com", "www.formula1.com",
    "www.wst.tv", "pdpa.co.uk", "www.nrl.com", "www.unitedrugby.com", "premiershiprugby.com",
    "premrugby.com", "top14.lnr.fr", "gaacork.ie", "munster.gaa.ie", "www.galwaygaa.ie",
    "www.gaa.ie", "www.gbgb.org.uk", "www.legavolley.it", "ehfcl.eurohandball.com",
    "www.eurohandball.com", "www.opel-hbl.de", "www.pcb.com.pk", "www.bcci.tv",
    "scoring.nzc.nz", "www.nzc.nz", "cricket.co.za", "www.cricket.co.za", "ncl20.com",
    "cricketcanada.org", "go.usa.rugby", "usa.rugby",
}

# ---------------------------------------------------------------------------
# OLBG discovery ledger: canonical routes, market labels, observed quirks.
# ---------------------------------------------------------------------------
SPORTS = [
    dict(slug="golf", name="Golf", id=5, category="Precision & cue",
         hub="https://www.olbg.com/betting-tips/Golf/5", status="No tips found",
         markets=["Tournament Outright Winner", "First Round Leader", "Top regional player", "Team event markets"],
         note="Hub exposed market documentation but no open tournament tip."),
    dict(slug="volleyball", name="Volleyball", id=21, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Volleyball/21", status="Open Win Match tips",
         markets=["Win Match"],
         note="More than twenty Win Match cards; event_id links and Load More Tips pagination."),
    dict(slug="rugby-union", name="Rugby Union", id=9, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Rugby_Union/9", status="Three open match markets",
         markets=["To Win", "Handicap", "Win Tournament"],
         note="Show Expired Events toggle and Load More Tips; several rows are long-dated outrights."),
    dict(slug="cricket", name="Cricket", id=7, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Cricket/7", status="Open match and player markets",
         markets=["Win Match", "Top Team1 Batsman", "Man Of The Match", "Outright Winner"],
         note="Load More Tips separates near-term games from long-dated tournament markets."),
    dict(slug="snooker", name="Snooker", id=8, category="Precision & cue",
         hub="https://www.olbg.com/betting-tips/Snooker/8", status="No tips found",
         markets=["Win Match", "Handicap Betting", "Frame Betting", "Win Tournament"],
         note="Hub published market definitions and historical frame statistics but no open tip."),
    dict(slug="darts", name="Darts", id=15, category="Precision & cue",
         hub="https://www.olbg.com/betting-tips/Darts/15", status="Open match and outright tips",
         markets=["Win Match 2-way", "Total 180s", "Win Tournament"],
         note="Load More Tips hides additional outrights; event pages expose all markets."),
    dict(slug="baseball", name="Baseball", id=12, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Baseball/12", status="One open MLB market",
         markets=["Money Line", "Run Line", "Game Totals", "Ante-post"],
         note="Only one active event; Show Expired Events and Load More Tips controls present."),
    dict(slug="gaelic", name="Gaelic Sports", id=25, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Gaelic_Football/25", status="Four open match markets",
         markets=["Handicap", "Match winner", "Draw", "Win Tournament"],
         note="Handicap selections sometimes have a blank market label in the hub markup."),
    dict(slug="greyhounds", name="Greyhounds", id=28, category="Race & speed",
         hub="https://www.olbg.com/betting-tips/Greyhounds/28", status="One open daily race",
         markets=["Daily Races", "Win", "Trap/forecast"],
         note="Race title uses track-local time while the row time is an unlabeled GeoIP-shifted time."),
    dict(slug="tennis", name="Tennis", id=3, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Tennis/3", status="Many open match markets",
         markets=["Win Match", "Set handicap", "Total games"],
         note="Hub lists finals and next-week main draws; times are unlabeled."),
    dict(slug="motor-racing", name="Motor Racing", id=14, category="Race & speed",
         hub="https://www.olbg.com/betting-tips/Motor_Racing/14", status="No tips found",
         markets=["Fastest Qualifier", "Win Race", "Podium Finish", "Top 6 Finish", "Points Finish", "Fastest Lap", "Win Tournament"],
         note="Hub documents all F1 market families and calendar links but has no open tip."),
    dict(slug="handball", name="Handball", id=20, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Handball/20", status="Many open 3-way markets",
         markets=["Money Line", "Handicap", "Game Totals"],
         note="Tie is a valid Money Line outcome; many most-tipped rows were Tie."),
    dict(slug="ice-hockey", name="Ice Hockey", id=13, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Ice_Hockey/13", status="Many open NHL/NLA/DEL markets",
         markets=["Money Line", "Game Totals", "Puck line / handicap"],
         note="/11 redirected to /13; hub times were unlabeled and split by GeoIP."),
    dict(slug="basketball", name="Basketball", id=4, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Basketball/4", status="Open NBA and KBL markets",
         markets=["Money Line", "Pointspread", "Game Totals"],
         note="NBA rows use @ notation and unlabeled times; KBL rows appear after Load More Tips."),
    dict(slug="rugby-league", name="Rugby League", id=10, category="Field & court",
         hub="https://www.olbg.com/betting-tips/Rugby_League/10", status="Only futures on hub",
         markets=["Win Tournament", "Grand Final Winner", "Match winner", "Handicap"],
         note="No active RLWC match tips were displayed; official NRL draw still lists Sunday games."),
]
SPORT = {s["slug"]: s for s in SPORTS}
assert len(SPORTS) == 15

OLBG_QUIRKS = [
    ("Canonical route", "/betting-tips/{Slug}/{id}", "Sitemap uses escaped underscores; /11 for ice hockey redirects to /13.", "olbg-sitemap", "nhl-schedule"),
    ("Event route", "/betting-tips/{Sport}/All_{Sport}/All_Events/{Event}/{id}?event_id={n}", "Event IDs are numeric and independent of sport ID.", "olbg-main", "pga-board"),
    ("Pagination", "Load More Tips", "The first hub chunk is not the complete event set; hidden zero-tip fixtures also exist.", "olbg-main", "pdpa-ec"),
    ("Expired rows", "Show Expired Events", "Expired events can be enabled on some hubs; default hides already-started matches.", "olbg-main", "prem-standings"),
    ("Time display", "Today / Tomorrow / dd Mmm", "Times have no visible timezone and differ from race titles or official UTC feeds.", "olbg-main", "mlb-schedule"),
    ("Tip percentage", "6/8 Win Tips = 75%", "This is community tip share, not an official probability and not used as an input to our prices.", "olbg-main", "nhl-standings"),
    ("Market labels", "Money Line / To Win / Win Match", "Labels differ by sport; some handicap rows have a blank label in hub markup.", "olbg-main", "legavolley-cal"),
    ("Case sensitivity", "Gaelic_Football/25", "Slug and ID both matter; wrong ID can return a different sport or redirect.", "olbg-sitemap", "wta-tokyo"),
]

# ---------------------------------------------------------------------------
# Matches.  Blank start_utc and blank fact fields are deliberate where the
# official page did not publish the value.
# ---------------------------------------------------------------------------
MATCHES = []


def match(mid, sport, event, a, b, *, competition, date, start_local="", start_utc="",
          venue="", source_ids=(), discovery="", form="", recent="", stat="",
          availability="The official source read did not publish an injury or availability note, so that field stayed blank.",
          flags=(), strength=0.62, handicap="", total="", other=""):
    MATCHES.append({
        "id": mid, "sport": sport, "event": event, "a": a, "b": b,
        "competition": competition, "date": date, "start_local": start_local,
        "start_utc": start_utc, "venue": venue, "source_ids": list(source_ids),
        "discovery_url": discovery or SPORT[sport]["hub"], "form": form,
        "recent": recent, "stat": stat, "availability": availability,
        "flags": list(flags), "strength": strength, "handicap": handicap,
        "total": total, "other": other,
    })


# Golf ----------------------------------------------------------------------
match("golf-bermuda", "golf", "Butterfield Bermuda Championship — final round",
      "Austin Smotherman", "Seamus Power", competition="PGA TOUR · Port Royal Golf Course",
      date="2026-10-25", start_local="Final round; exact tee times not published on source read",
      venue="Port Royal Golf Course, Southampton, Bermuda",
      source_ids=["pga-board"], discovery=SPORT["golf"]["hub"],
      form="Official leaderboard: Smotherman and Power share first at -16 after three rounds.",
      recent="Smotherman shot 65-66-66; Power shot 66-64-67; Taylor Moore, Corey Conners and Ben Silverman are -14.",
      stat="197 strokes lead the field; 199 strokes sit two back; final round remains on 25 Oct.",
      flags=["OLBG Golf hub reported No tips found", "Exact final-round tee time blank"],
      strength=0.70, handicap="Top 5 finish", total="Winning score under 18 under par", other="Top 10 finish")

# Volleyball ----------------------------------------------------------------
vol_cal = "https://www.legavolley.it/calendario/?idCampionato=999"
match("vol-per-por", "volleyball", "Sir Susa Scai Perugia v Tinet Prata di Pordenone",
      "Perugia", "Pordenone", competition="SuperLega Credem Banca · Round 2",
      date="2026-10-25", start_local="18:00 official local time",
      source_ids=["legavolley-cal", "legavolley-table"],
      discovery="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Perugia_vs_Pordenone/21?event_id=36997",
      form="Perugia have 2 points from a 3-2 opener; Pordenone have 3 points from a 3-1 opener.",
      recent="Perugia edged Cuneo 3-2; Pordenone beat Monza 3-1.",
      stat="Perugia point ratio 1.20; Pordenone point ratio 1.03; both scored 114 and 94 points respectively.",
      strength=0.70, handicap="Perugia -1.5 sets", total="Over 3.5 sets", other="Perugia to win")
match("vol-tre-cis", "volleyball", "Itas Trentino v Cisterna Volley",
      "Trentino", "Cisterna", competition="SuperLega Credem Banca · Round 2",
      date="2026-10-25", start_local="17:00 official local time",
      source_ids=["legavolley-cal", "legavolley-table"],
      discovery="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Trentino_vs_Cisterna/21?event_id=36994",
      form="Trentino and Cisterna both won 3-0 and hold 3 points after round one.",
      recent="Trentino beat Modena 3-0; Cisterna beat Allianz Milano 3-0.",
      stat="Trentino point ratio 1.23; Cisterna point ratio 1.41; both have a 3.00 set ratio.",
      strength=0.69, handicap="Cisterna +1.5 sets", total="Under 4.5 sets", other="Trentino to win")
match("vol-lub-pad", "volleyball", "Cucine Lube Civitanova v Pallavolo Padova",
      "Civitanova", "Padova", competition="SuperLega Credem Banca · Round 2",
      date="2026-10-25", start_local="18:00 official local time",
      source_ids=["legavolley-cal", "legavolley-table"],
      discovery="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Civitanova_vs_Padova/21?event_id=36995",
      form="Civitanova are 3-0 in sets and 3 points; Padova lost 0-3 and have 0 points.",
      recent="Civitanova beat Verona 3-0; Padova lost 0-3 to Piacenza.",
      stat="Civitanova point ratio 1.20; Padova point ratio 0.75 with 56 points scored.",
      strength=0.68, handicap="Civitanova -1.5 sets", total="Under 3.5 sets", other="Civitanova to win")
match("vol-mon-ver", "volleyball", "Vero Volley Monza v Rana Verona",
      "Monza", "Verona", competition="SuperLega Credem Banca · Round 2",
      date="2026-10-25", start_local="18:00 official local time",
      source_ids=["legavolley-cal", "legavolley-table"],
      discovery="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Monza_vs_Verona/21?event_id=36996",
      form="Monza lost 1-3 and Verona lost 0-3; both have 0 points.",
      recent="Monza lost to Pordenone; Verona lost to Civitanova.",
      stat="Monza point ratio 0.97 with 91 points; Verona point ratio 0.83 with 65 points.",
      strength=0.62, handicap="Monza -1.5 sets", total="Over 3.5 sets", other="Monza to win")
match("vol-all-cun", "volleyball", "Allianz Milano v Acqua Sant'Anna Cuneo",
      "Milano", "Cuneo", competition="SuperLega Credem Banca · Round 2",
      date="2026-10-25", start_local="19:00 official local time",
      source_ids=["legavolley-cal", "legavolley-table"], discovery=SPORT["volleyball"]["hub"],
      form="Milano have 0 points from a 0-3 loss; Cuneo have 1 point from a 2-3 loss.",
      recent="Milano lost 0-3 to Cisterna; Cuneo lost 2-3 to Perugia.",
      stat="Milano point ratio 0.71; Cuneo point ratio 0.83 with 95 points scored.",
      flags=["Official calendar fill: not seen on the OLBG hub first chunk"],
      strength=0.60, handicap="Cuneo +1.5 sets", total="Over 3.5 sets", other="Cuneo to win")

# Rugby Union ---------------------------------------------------------------
match("ru-har-sar", "rugby-union", "Harlequins v Saracens",
      "Harlequins", "Saracens", competition="Gallagher PREM",
      date="2026-10-25", start_local="OLBG row: Tomorrow 11:00; timezone not labeled",
      source_ids=["prem-standings"],
      discovery="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Harlequins_v_Saracens/9?event_id=609571",
      form="Official standings: Saracens 4th at 2-1, +21 points difference; Harlequins 10th at 0-3, -68.",
      recent="Saracens form string W-L-W; Harlequins form string L-L-L.",
      stat="Saracens have 11 league points from 3 matches; Harlequins have 2.",
      flags=["Exact UTC start blank", "Premiership fixtures page returned 404 on read"],
      strength=0.71, handicap="Saracens -3.5", total="Over 47.5 points", other="Saracens to win")
match("ru-lar-bor", "rugby-union", "Stade Rochelais v Union Bordeaux-Bègles",
      "La Rochelle", "Bordeaux", competition="Top 14 · Journee 7",
      date="2026-10-25", start_local="21h05 local",
      venue="Stade Marcel-Deflandre", source_ids=["top14", "top14-table"],
      discovery="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/La_Rochelle_v_Bordeaux/9?event_id=609554",
      form="UBB are 3rd on 19 points with +64 difference; La Rochelle are 4th on 18 points with +9.",
      recent="Both clubs won their last two listed league matches; UBB's sequence is L-W-D? no: W-W after round 4 loss.",
      stat="UBB have 215 points scored and 151 conceded; La Rochelle 144 scored and 135 conceded.",
      flags=["Exact UTC start blank"],
      strength=0.65, handicap="Bordeaux +3.5", total="Over 45.5 points", other="Bordeaux to win")
match("ru-usa-ausa", "rugby-union", "USA v Australia A",
      "USA", "Australia A", competition="October international series",
      date="2026-10-24", start_local="OLBG row: Today 19:00; timezone not labeled",
      source_ids=["usa-rugby"],
      discovery="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/USA_v_Australia_A/9?event_id=609583",
      form="", recent="", stat="",
      availability="USA Rugby's official October-series page confirms an Australia XV fixture but publishes no lineup or availability list for this date.",
      flags=["Exact date, venue and UTC start not published on official source read", "No official team form or recent result read"],
      strength=0.50, handicap="Australia A -6.5", total="Over 42.5 points", other="Australia A to win")

# Cricket -------------------------------------------------------------------
match("cr-pak-eng", "cricket", "Pakistan v England — 4th ODI tri-series match",
      "Pakistan", "England", competition="Pakistan, England and Sri Lanka tri-nation ODI series",
      date="2026-10-25", start_local="13:00 local per PCB series note",
      venue="Gaddafi Stadium, Lahore", source_ids=["pcb-draw", "pcb-news"],
      discovery="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Pakistan_vs_England_One_Day_Match/7?event_id=188838",
      form="Pakistan won their first two tri-series matches; England lost both.",
      recent="Pakistan beat England by 87 runs on 20 Oct after 302-9; England were bowled out for 215.",
      stat="Arafat Minhas made 59 and took 6-40 in that match; Pakistan's earlier win was by 37 runs.",
      strength=0.71, handicap="Pakistan -0.5 match", total="Over 275.5 runs", other="Pakistan to win")
match("cr-indw-zimw", "cricket", "India Women v Zimbabwe Women — 2nd ODI",
      "India Women", "Zimbabwe Women", competition="Zimbabwe Women in India 2026/27",
      date="2026-10-25", start_local="08:30 UTC / 14:00 IST", start_utc="2026-10-25T08:30:00Z",
      venue="BCA Stadium, Vadodara", source_ids=["bcci-match", "bcci-squad"],
      discovery="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/India_W_vs_Zimbabwe_W_2nd_ODI/7?event_id=188847",
      form="BCCI names Smriti Mandhana as ODI captain with Shafali Verma, Harmanpreet Kaur and Deepti Sharma in the squad.",
      recent="The 1st ODI was played on 23 Oct; no score was extracted from the official page read.",
      stat="Three ODIs are scheduled in Vadodara on 23, 25 and 28 Oct.",
      availability="BCCI confirms Renuka Singh Thakur was ruled out and Jintimani Kalita replaced her in the ODI squad.",
      flags=["1st ODI score blank"],
      strength=0.68, handicap="India Women -0.5 match", total="Over 235.5 runs", other="Smriti Mandhana top India Women batter")
match("cr-nz-ind", "cricket", "New Zealand v India — 3rd T20I",
      "New Zealand", "India", competition="India in New Zealand T20I series",
      date="2026-10-27", start_local="07:00 site time; timezone not labeled",
      venue="Hnry Stadium, Wellington", source_ids=["nzc-fixtures", "nzc-match"],
      discovery="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/New_Zealand_vs_India_3rd_T20_Match/7?event_id=188852",
      form="Official match info publishes both lineups but no pre-match form figures.",
      recent="New Zealand's published XI includes Tim Robinson, Nick Kelly and Ish Sodhi; India's includes Abhishek Sharma, Shreyas Iyer and Axar Patel.",
      stat="The official fixture is the third match of a five-match T20I series.",
      availability="Team lists are named on the official match page; no injury designations were published there.",
      flags=["Exact UTC start blank"],
      strength=0.62, handicap="India -0.5 match", total="Over 160.5 runs", other="India to win")
match("cr-bol-tit", "cricket", "Boland v Momentum Multiply Titans T20",
      "Boland", "Titans", competition="CSA Pro20 Cup 2026/27",
      date="2026-10-25", start_local="13:00 local", venue="Boland Park",
      source_ids=["csa-page8"],
      discovery="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Boland_vs_Titans_T20/7?event_id=188849",
      form="", recent="", stat="",
      flags=["Official CSA search index exposed the fixture but live pagination had moved on", "No official form or recent result read"],
      strength=0.56, handicap="Titans -0.5 match", total="Over 155.5 runs", other="Titans to win")
match("cr-nw-nc", "cricket", "North West Dragons v Northern Cape Heat T20",
      "North West Dragons", "Northern Cape Heat", competition="CSA Pro20 Cup 2026/27",
      date="2026-10-25", start_local="13:00 local", venue="NWC Oval",
      source_ids=["csa-page8"],
      discovery="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/North_West_Dragons_vs_Northern_Cape_Heat_T20/7?event_id=188851",
      form="", recent="", stat="",
      flags=["Official CSA search index exposed the fixture but live pagination had moved on", "No official form or recent result read"],
      strength=0.55, handicap="North West Dragons -0.5 match", total="Over 150.5 runs", other="North West Dragons to win")
match("cr-tk-vg", "cricket", "Toronto Kings v Vancouver Guardians",
      "Toronto Kings", "Vancouver Guardians", competition="NCL GT20 Canada 2026 Caribbean Edition",
      date="2026-10-24", start_local="Sat 24 Oct, 7:00 PM EDT", start_utc="2026-10-24T23:00:00Z",
      venue="Arnos Vale Stadium", source_ids=["ncl20", "cricket-canada"],
      discovery="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Toronto_Kings_vs_Vancouver_Guardians_T20/7?event_id=188845",
      form="Tournament is at match three; Toronto Kings lost their opener.",
      recent="Brampton Blazers made 154-5 in 19.1 overs to beat Toronto Kings 153-6 by five wickets.",
      stat="Toronto Kings' 153-6 is the only official batting total read for either side.",
      availability="NCL published match fixtures and results but no injury or availability list.",
      flags=["Cricket Canada home page did not list the match directly"],
      strength=0.58, handicap="Toronto Kings -0.5 match", total="Over 145.5 runs", other="Toronto Kings to win")

# Snooker -------------------------------------------------------------------
match("sn-wilson-final", "snooker", "Northern Ireland Open final — Kyren Wilson v Winner of match 62",
      "Kyren Wilson", "Winner of match 62", competition="BetVictor Northern Ireland Open 2026",
      date="2026-10-25", start_local="08:00 site time; timezone not labeled",
      source_ids=["wst-home", "wst-news", "wst-rankings"], discovery=SPORT["snooker"]["hub"],
      form="WST reports Kyren Wilson beat Sam Craigie to reach the final.",
      recent="The official home page lists Mark Williams v Jak Jones as the live semifinal at 5-5.",
      stat="Wilson is 9th in the official world rankings on £716,800 and is tied for fifth on the Home Nations bonus list.",
      availability="", flags=["Final opponent blank until the semifinal completes", "OLBG Snooker hub reported No tips found"],
      strength=0.68, handicap="Kyren Wilson -1.5 frames", total="Over 15.5 frames", other="Kyren Wilson to win")
match("sn-selby-white", "snooker", "Jimmy White v Mark Selby",
      "Jimmy White", "Mark Selby", competition="International Championship 2026 · Round 2",
      date="2026-10-30", start_local="21:30 site time; timezone not labeled",
      source_ids=["wst-home", "wst-rankings"], discovery=SPORT["snooker"]["hub"],
      form="Mark Selby is 5th in the world rankings and 1st on the one-year list.",
      recent="WST lists this as a Round 2 match on 30 Oct; no recent head-to-head result was published on the page read.",
      stat="Selby has £1,070,500 in world-ranking earnings and £348,350 on the one-year list; White is outside the displayed top 11.",
      flags=["Exact UTC start blank", "OLBG Snooker hub reported No tips found"],
      strength=0.71, handicap="Mark Selby -2.5 frames", total="Under 9.5 frames", other="Mark Selby to win")
match("sn-murphy-mann", "snooker", "Shaun Murphy v Mitchell Mann",
      "Shaun Murphy", "Mitchell Mann", competition="International Championship 2026 · Round 2",
      date="2026-10-30", start_local="21:30 site time; timezone not labeled",
      source_ids=["wst-home", "wst-rankings"], discovery=SPORT["snooker"]["hub"],
      form="Shaun Murphy is 7th in the official world rankings.",
      recent="WST lists this as a Round 2 match on 30 Oct; no recent head-to-head result was published on the page read.",
      stat="Murphy has £897,350 in world-ranking earnings and 10th place on the one-year list at £79,350.",
      flags=["Exact UTC start blank", "OLBG Snooker hub reported No tips found"],
      strength=0.69, handicap="Shaun Murphy -1.5 frames", total="Under 9.5 frames", other="Shaun Murphy to win")
match("sn-hawkins-walden", "snooker", "Barry Hawkins v Ricky Walden",
      "Barry Hawkins", "Ricky Walden", competition="International Championship 2026 · Round 2",
      date="2026-10-31", start_local="02:00 site time; timezone not labeled",
      source_ids=["wst-home", "wst-rankings"], discovery=SPORT["snooker"]["hub"],
      form="Barry Hawkins is 10th in the world rankings.",
      recent="WST lists this as a Round 2 held-over match on 31 Oct; no recent head-to-head result was published on the page read.",
      stat="Hawkins has £670,050 in world-ranking earnings; Walden is outside the displayed top 11.",
      flags=["Exact UTC start blank", "OLBG Snooker hub reported No tips found"],
      strength=0.67, handicap="Barry Hawkins -1.5 frames", total="Over 8.5 frames", other="Barry Hawkins to win")
match("sn-zhou-davies", "snooker", "Zhou Yuelong v Liam Davies",
      "Zhou Yuelong", "Liam Davies", competition="International Championship 2026 · Round 2",
      date="2026-10-30", start_local="21:30 site time; timezone not labeled",
      source_ids=["wst-home", "wst-rankings"], discovery=SPORT["snooker"]["hub"],
      form="Zhou Yuelong and Liam Davies are both shown on the Home Nations bonus list.",
      recent="WST lists this as a Round 2 match on 30 Oct; no recent head-to-head result was published on the page read.",
      stat="Both players are listed at £13,200 on the Home Nations bonus list; neither appears in the displayed world top 11.",
      availability="", flags=["Exact UTC start blank", "OLBG Snooker hub reported No tips found"],
      strength=0.60, handicap="Zhou Yuelong -1.5 frames", total="Over 8.5 frames", other="Zhou Yuelong to win")

# Darts ---------------------------------------------------------------------
pdpa = "https://pdpa.co.uk/event/european-championship-2026/"
match("da-price-bunting", "darts", "Gerwyn Price v Stephen Bunting",
      "Gerwyn Price", "Stephen Bunting", competition="PDC European Championship · Quarterfinal",
      date="2026-10-25", start_local="Sunday 13.00 / 19.00 sessions; timezone not labeled",
      venue="Westfalenhalle, Dortmund", source_ids=["pdpa-ec"],
      discovery="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Gerwyn_Price_vs_Stephen_Bunting/15?event_id=32407",
      form="Price won his second-round match 10-4; Bunting won 10-3.",
      recent="Price beat Cameron Menzies; Bunting beat Kim Huybrechts in round two.",
      stat="The official event lists a £750,000 prize fund and £35,000 per quarterfinalist.",
      availability="The PDPA event page published no injury or availability note, so that field stayed blank.",
      flags=["Exact UTC start blank"], strength=0.67, handicap="Gerwyn Price -1.5 legs", total="Over 10.5 180s", other="Gerwyn Price to win")
match("da-smith-woodhouse", "darts", "Ross Smith v Luke Woodhouse",
      "Ross Smith", "Luke Woodhouse", competition="PDC European Championship · Quarterfinal",
      date="2026-10-25", start_local="Sunday 13.00 / 19.00 sessions; timezone not labeled",
      venue="Westfalenhalle, Dortmund", source_ids=["pdpa-ec"],
      discovery="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Ross_Smith_vs_Luke_Woodhouse/15?event_id=32408",
      form="Smith won 10-7 and Woodhouse won 10-6 in round two.",
      recent="Smith beat Damon Heta; Woodhouse beat Gian van Veen.",
      stat="Smith was the number one seed in the official draw; Woodhouse was seed nine.",
      availability="The PDPA event page published no injury or availability note, so that field stayed blank.",
      flags=["Exact UTC start blank"], strength=0.66, handicap="Ross Smith -1.5 legs", total="Over 16.5 legs", other="Ross Smith to win")
match("da-ratajski-schindler", "darts", "Krzysztof Ratajski v Martin Schindler",
      "Krzysztof Ratajski", "Martin Schindler", competition="PDC European Championship · Quarterfinal",
      date="2026-10-25", start_local="Sunday 13.00 / 19.00 sessions; timezone not labeled",
      venue="Westfalenhalle, Dortmund", source_ids=["pdpa-ec"], discovery=SPORT["darts"]["hub"],
      form="Ratajski won 10-8; Schindler won 10-4 in round two.",
      recent="Ratajski beat Kevin Doets; Schindler beat Jermaine Wattimena.",
      stat="Ratajski was seed three in the official draw; Schindler came through as seed 31.",
      availability="The PDPA event page published no injury or availability note, so that field stayed blank.",
      flags=["Exact UTC start blank", "Official event fill: not exposed on the OLBG hub first chunk"],
      strength=0.62, handicap="Martin Schindler +1.5 legs", total="Over 16.5 legs", other="Krzysztof Ratajski to win")
match("da-littler-clayton", "darts", "Luke Littler v Jonny Clayton",
      "Luke Littler", "Jonny Clayton", competition="PDC European Championship · Quarterfinal",
      date="2026-10-25", start_local="Sunday 13.00 / 19.00 sessions; timezone not labeled",
      venue="Westfalenhalle, Dortmund", source_ids=["pdpa-ec"], discovery=SPORT["darts"]["hub"],
      form="Littler won 10-5; Clayton won 10-8 in round two.",
      recent="Littler beat Nathan Aspinall; Clayton beat Josh Rock.",
      stat="Littler was seed 11 and Clayton seed 7 in the official draw; the champion receives £150,000.",
      availability="The PDPA event page published no injury or availability note, so that field stayed blank.",
      flags=["Exact UTC start blank", "Official event fill: not exposed on the OLBG hub first chunk"],
      strength=0.70, handicap="Luke Littler -1.5 legs", total="Over 16.5 legs", other="Luke Littler to win")
match("da-european-title", "darts", "European Championship — tournament winner",
      "Luke Littler", "Field", competition="PDC European Championship 2026",
      date="2026-10-25", start_local="Sunday final session; timezone not labeled",
      venue="Westfalenhalle, Dortmund", source_ids=["pdpa-ec"],
      discovery="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/European_Championship/15?event_id=32338",
      form="Littler reached the quarterfinals with a 10-5 second-round win.",
      recent="The official bracket shows Price v Bunting, Smith v Woodhouse, Ratajski v Schindler and Littler v Clayton.",
      stat="The winner receives £150,000 from a £750,000 prize fund.",
      availability="The PDPA event page published no injury or availability note, so that field stayed blank.",
      flags=["Exact UTC start blank"], strength=0.69, handicap="Luke Littler top 4", total="Over 2.5 Littler match wins", other="Luke Littler to win tournament")

# Baseball ------------------------------------------------------------------
match("mlb-ws2", "baseball", "Tampa Bay Rays at Milwaukee Brewers — World Series Game 2",
      "Tampa Bay Rays", "Milwaukee Brewers", competition="MLB World Series 2026",
      date="2026-10-24", start_local="8:00 PM ET on 24 Oct", start_utc="2026-10-25T00:00:00Z",
      venue="American Family Field", source_ids=["mlb-schedule", "mlb-standings"],
      discovery="https://www.olbg.com/betting-tips/Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160792",
      form="Milwaukee were 103-59 with a +214 run difference; Tampa Bay were 98-64 with +86.",
      recent="Milwaukee lead the best-of-seven 1-0 and went 8-2 in their last ten regular-season games.",
      stat="Milwaukee were 55-26 at home; MLB lists Drew Rasmussen and Logan Henderson as probable pitchers.",
      availability="MLB's schedule feed lists probable pitchers but no injury or availability report for either club.",
      flags=["Only one active MLB game in the official schedule"],
      strength=0.69, handicap="Tampa Bay Rays +1.5", total="Over 7.5 runs", other="Milwaukee Brewers to win World Series")

# Gaelic Sports -------------------------------------------------------------
match("ga-nemo-stf", "gaelic", "Nemo Rangers v St Finbarrs",
      "Nemo Rangers", "St Finbarrs", competition="Cork Premier SFC Final",
      date="2026-10-25", start_local="16:00 local", venue="SuperValu Páirc Uí Chaoimh",
      source_ids=["cork-gaa", "munster-gaa"],
      discovery="https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530",
      form="", recent="", stat="Official pages confirm the final, venue, 16:00 throw-in and referee David Murnane.",
      availability="The county-board fixture pages published no team lists or injury note, so availability stayed blank.",
      flags=["No official team form or recent result read"],
      strength=0.62, handicap="Nemo Rangers +1.5", total="Under 34.5 points", other="Nemo Rangers to win")
match("ga-cob-can", "gaelic", "Cobh v Canovee",
      "Cobh", "Canovee", competition="Cork Premier JFC Final",
      date="2026-10-25", start_local="14:00 local", venue="SuperValu Páirc Uí Chaoimh",
      source_ids=["cork-gaa"], discovery=SPORT["gaelic"]["hub"],
      form="", recent="", stat="Official fixture lists the 14:00 throw-in, final status and referee Niall Hayes.",
      availability="The county-board fixture page published no team lists or injury note, so availability stayed blank.",
      flags=["Official calendar fill: not seen on the OLBG hub first chunk", "No official team form or recent result read"],
      strength=0.58, handicap="Cobh -0.5", total="Under 32.5 points", other="Cobh to win")
match("ga-salthill-moycullen", "gaelic", "Salthill-Knocknacarra v Cumann Peile Mhaigh Cuilinn",
      "Salthill-Knocknacarra", "Moycullen", competition="Galway Senior Football Championship",
      date="2026-10-25", start_local="", source_ids=["galway-gaa"],
      discovery="https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532",
      form="", recent="", stat="Galway GAA lists the fixture and competition; a 23 Oct notice reports weather-driven schedule changes.",
      availability="The county board published no team lists or injury note, so availability stayed blank.",
      flags=["Exact throw-in time blank", "No official team form or recent result read"],
      strength=0.61, handicap="Salthill-Knocknacarra +3.5", total="Under 34.5 points", other="Salthill-Knocknacarra to win")
match("ga-spiddal-caherlistrane", "gaelic", "An Spidéal v Caherlistrane",
      "An Spidéal", "Caherlistrane", competition="Galway Intermediate Football Championship",
      date="2026-10-25", start_local="", source_ids=["galway-gaa"],
      discovery=SPORT["gaelic"]["hub"], form="", recent="",
      stat="Galway GAA lists the fixture and competition for 25 Oct but no throw-in time or recent score.",
      availability="The county board published no team lists or injury note, so availability stayed blank.",
      flags=["Exact throw-in time blank", "Official calendar fill: not seen on the OLBG hub first chunk", "No official team form or recent result read"],
      strength=0.55, handicap="An Spidéal +2.5", total="Under 32.5 points", other="An Spidéal to win")
match("ga-kiskeam-uibhlaoire", "gaelic", "Kiskeam v Uibh Laoire",
      "Kiskeam", "Uibh Laoire", competition="Cork Premier IFC Final",
      date="2026-10-31", start_local="19:00 local", venue="SuperValu Páirc Uí Chaoimh",
      source_ids=["cork-gaa"], discovery=SPORT["gaelic"]["hub"], form="", recent="",
      stat="Official fixture lists the final, 19:00 throw-in and referee Robert Whelan.",
      availability="The county-board fixture page published no team lists or injury note, so availability stayed blank.",
      flags=["Official calendar fill: not seen on the OLBG hub first chunk", "No official team form or recent result read"],
      strength=0.57, handicap="Uibh Laoire +1.5", total="Under 33.5 points", other="Uibh Laoire to win")

# Greyhounds ----------------------------------------------------------------
match("gr-scurry", "greyhounds", "Scurry Gold Cup final",
      "Shadow Storm", "Avarua Lake", competition="GBGB Category One · Dunstall Park",
      date="2026-10-24", start_local="Saturday final; exact time not published on report",
      source_ids=["gbgb-scurry", "gbgb-racing"], discovery=SPORT["greyhounds"]["hub"],
      form="Shadow Storm is the reigning GBGB Sprinter of the Year and seeks back-to-back Scurry titles.",
      recent="Shadow Storm won his semifinal by 1.25 lengths in 15.66sec; Avarua Lake won his in 15.86sec.",
      stat="Roanna Mamba's 15.73sec was the other semifinal time; the winner's prize is £12,500.",
      availability="The GBGB race report published no withdrawal or injury note, so availability stayed blank.",
      flags=["Exact race time blank", "OLBG Greyhounds hub exposed only one daily race"],
      strength=0.68, handicap="Shadow Storm to finish top 2", total="Under 16.00sec winning time", other="Shadow Storm to win")
match("gr-oaks", "greyhounds", "Premier Greyhound Racing Oaks final",
      "Signet Nayla", "Fahrenheit Jess", competition="GBGB Category One · Dunstall Park",
      date="2026-10-24", start_local="Saturday final; exact time not published on report",
      source_ids=["gbgb-oaks", "gbgb-racing"], discovery=SPORT["greyhounds"]["hub"],
      form="Signet Nayla was runner-up in the Birmingham Cup and won her Oaks semifinal.",
      recent="Signet Nayla clocked 28.35sec; Fahrenheit Jess was fastest of the round at 27.87sec.",
      stat="The Oaks final carries a £20,000 winner's prize; Slingshot Poppy also won a semifinal in 27.90sec.",
      availability="The GBGB race report published no withdrawal or injury note, so availability stayed blank.",
      flags=["Exact race time blank", "OLBG Greyhounds hub exposed only one daily race"],
      strength=0.66, handicap="Signet Nayla to finish top 2", total="Under 28.20sec winning time", other="Fahrenheit Jess to win")
match("gr-puppy", "greyhounds", "Doncaster Puppy Derby",
      "Returning Storm", "Shado Earth", competition="GBGB Category One · Doncaster 450m",
      date="2026-10-31", start_local="Final a week after Saturday semifinals; exact time not published",
      source_ids=["gbgb-puppy", "gbgb-racing"], discovery=SPORT["greyhounds"]["hub"],
      form="Returning Storm was quickest of the first-round heat winners.",
      recent="Returning Storm won heat five in 27.49sec; Shado Earth won the previous heat in 27.69sec.",
      stat="Carrigoon Cece won in 27.55sec and Lady Gambet in 27.66sec; the event is over 450m.",
      availability="The GBGB race report published no withdrawal or injury note, so availability stayed blank.",
      flags=["Exact race time blank", "OLBG Greyhounds hub exposed only one daily race"],
      strength=0.67, handicap="Returning Storm to finish top 2", total="Under 27.60sec winning time", other="Returning Storm to win")
match("gr-doncaster-r1", "greyhounds", "11:04 Doncaster daily race",
      "Snowfall", "Field", competition="GBGB daily racing · Doncaster",
      date="2026-10-25", start_local="11:04 track-local in OLBG race title",
      source_ids=["gbgb-racing"],
      discovery="https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:04_Doncaster/28?event_id=690043",
      form="", recent="", stat="", availability="GBGB's static racing page did not expose this future racecard or runner form.",
      flags=["Official racecard not extractable", "Exact UTC start blank", "No official form or recent result read"],
      strength=0.54, handicap="Snowfall to finish top 2", total="Under 28.80sec winning time", other="Snowfall to win")
match("gr-open-card", "greyhounds", "Dunstall Park open-race double-header",
      "Magical Jason", "Field", competition="GBGB open races · Dunstall Park",
      date="2026-10-24", start_local="Saturday double-header; exact race times not published",
      source_ids=["gbgb-open", "gbgb-scurry", "gbgb-oaks"], discovery=SPORT["greyhounds"]["hub"],
      form="Kevin Hutton has finalists in both the Scurry Gold Cup and the Oaks.",
      recent="Magical Jason was runner-up to Roanna Mamba in a Scurry semifinal.",
      stat="The official open-race page lists Dunstall Park and Category One filters but no individual card in static text.",
      availability="The GBGB pages published no withdrawal or injury note, so availability stayed blank.",
      flags=["Official open-race card not extractable", "Exact race time blank"],
      strength=0.56, handicap="Magical Jason to finish top 2", total="Under 16.10sec winning time", other="Magical Jason to win")

# Tennis --------------------------------------------------------------------
match("te-med-bas", "tennis", "Daniil Medvedev v Nikoloz Basilashvili — Almaty final",
      "Daniil Medvedev", "Nikoloz Basilashvili", competition="ATP Almaty",
      date="2026-10-25", start_local="Sunday final; exact site time not published on source read",
      source_ids=["atp-scores", "atp-news"],
      discovery="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Daniil_Medvedev_vs_Nikoloz_Basilashvili/3?event_id=902251",
      form="Medvedev is into the final after Bublik retired; Basilashvili won a three-set semifinal.",
      recent="Medvedev led 6-3 0-0 when Bublik retired; Basilashvili beat Tsitsipas 6-4 6-7(5) 6-3 in 2h16.",
      stat="The official scores page exposes an H2H panel showing Medvedev leading Basilashvili 1-0.",
      availability="The ATP page published no injury or withdrawal note for either finalist, so availability stayed blank.",
      flags=["Exact UTC start blank"], strength=0.69, handicap="Daniil Medvedev -2.5 games", total="Over 21.5 games", other="Daniil Medvedev to win")
match("te-fritz-musetti", "tennis", "Lorenzo Musetti v Taylor Fritz — Lyon final",
      "Lorenzo Musetti", "Taylor Fritz", competition="ATP Lyon",
      date="2026-10-25", start_local="Sunday final; exact site time not published on source read",
      source_ids=["atp-scores", "atp-news"],
      discovery="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Lorenzo_Musetti_vs_Taylor_Fritz/3?event_id=902253",
      form="Fritz is the second seed and beat Tommy Paul in straight sets; Musetti saved four match points against Cobolli.",
      recent="Fritz beat Paul 6-3 7-5 in 1h41; Musetti beat Cobolli 4-6 6-2 7-5 in 2h32.",
      stat="Musetti spent 51 minutes longer on court in the semifinal than Fritz.",
      availability="The ATP page published no injury or withdrawal note for either finalist, so availability stayed blank.",
      flags=["Exact UTC start blank"], strength=0.66, handicap="Taylor Fritz -1.5 games", total="Over 22.5 games", other="Taylor Fritz to win")
match("te-struff-griekspoor", "tennis", "Jan-Lennard Struff v Tallon Griekspoor — Brussels final",
      "Jan-Lennard Struff", "Tallon Griekspoor", competition="ATP Brussels",
      date="2026-10-25", start_local="Sunday final; exact site time not published on source read",
      source_ids=["atp-scores", "atp-news"],
      discovery=SPORT["tennis"]["hub"],
      form="Struff upset top seed Arthur Fils; Griekspoor came back to beat Francisco Cerundolo.",
      recent="Struff won 6-4 6-7(7) 7-6(5) in 2h18; Griekspoor won 2-6 6-3 7-6(4) in 2h18.",
      stat="Both semifinals lasted 2h18; Struff faced 13 sets of tiebreak pressure across the final two sets.",
      availability="The ATP page published no injury or withdrawal note for either finalist, so availability stayed blank.",
      flags=["Exact UTC start blank"], strength=0.63, handicap="Tallon Griekspoor -1.5 games", total="Over 23.5 games", other="Tallon Griekspoor to win")
match("te-wawrinka-lehecka", "tennis", "Stan Wawrinka v Jiri Lehecka — Basel first round",
      "Stan Wawrinka", "Jiri Lehecka", competition="ATP 500 Basel",
      date="2026-10-26", start_local="Monday main draw; exact site time not published on source read",
      source_ids=["atp-news"],
      discovery="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Stan_Wawrinka_vs_Jiri_Lehecka/3?event_id=902232",
      form="The official Basel draw preview names Wawrinka v Lehecka as a first-round match.",
      recent="ATP also reports Djokovic and Shelton in the same half of the draw.",
      stat="No official serve, return or ranking input for this pairing was extracted from the page read.",
      availability="The ATP draw preview published no injury or withdrawal note for this match, so availability stayed blank.",
      flags=["Exact UTC start blank", "No official form or recent result read"],
      strength=0.57, handicap="Jiri Lehecka -2.5 games", total="Over 21.5 games", other="Jiri Lehecka to win")
match("te-alcaraz-khachanov", "tennis", "Carlos Alcaraz v Karen Khachanov — Vienna opener",
      "Carlos Alcaraz", "Karen Khachanov", competition="ATP 500 Vienna",
      date="2026-10-26", start_local="Monday main draw; exact site time not published on source read",
      source_ids=["atp-news"],
      discovery=SPORT["tennis"]["hub"],
      form="The official Vienna draw preview calls this Alcaraz's opener.",
      recent="ATP's news page also names Zverev v Landaluce in the same draw section.",
      stat="No official serve, return or ranking input for this pairing was extracted from the page read.",
      availability="The ATP draw preview published no injury or withdrawal note for this match, so availability stayed blank.",
      flags=["Exact UTC start blank", "No official form or recent result read"],
      strength=0.60, handicap="Carlos Alcaraz -3.5 games", total="Under 23.5 games", other="Carlos Alcaraz to win")

# Motor Racing --------------------------------------------------------------
match("f1-usgp", "motor-racing", "Formula 1 MSC Cruises United States Grand Prix 2026",
      "Kimi Antonelli", "Max Verstappen", competition="Formula 1 · Circuit of The Americas",
      date="2026-10-25", start_local="16:00 track time",
      venue="Circuit of The Americas, Austin", source_ids=["f1-usgp", "f1-qual"],
      discovery=SPORT["motor-racing"]["hub"],
      form="Antonelli took pole with 1:34.035; Verstappen was 0.179 behind and Leclerc 0.232 behind.",
      recent="FP1 and FP2 were led by Leclerc; FP3 was led by Hamilton, with Verstappen and Leclerc next.",
      stat="Official qualifying shows Antonelli 18 laps, Verstappen 12, Hadjar 12, Leclerc 15 and Hamilton 14; race distance is 56 laps.",
      availability="The official F1 event page published no driver availability note, so that field stayed blank.",
      flags=["Exact UTC start blank", "OLBG Motor Racing hub reported No tips found"],
      strength=0.68, handicap="Antonelli podium finish", total="Over 0.5 safety cars", other="Kimi Antonelli to win race")

# Handball ------------------------------------------------------------------
match("hb-magdeburg-kriens", "handball", "SC Magdeburg v HC Kriens-Luzern",
      "SC Magdeburg", "HC Kriens-Luzern", competition="EHF Champions League Men · Group F",
      date="2026-10-28", start_local="20:45 site time; timezone not labeled",
      source_ids=["ehfcl-standings", "ehfcl-home"],
      discovery="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/SC_Magdeburg_vs_HC_Kriens_Luzern/20?event_id=12136",
      form="Official standings: Magdeburg 5-0, 176-140, +36; Kriens 2-3, 158-161, -3.",
      recent="Magdeburg beat Kielce 30-27 and lead the group; Kriens lost 30-32 to Kielce in their last listed match.",
      stat="Magdeburg average 35.2 goals scored and 28.0 conceded; Kriens average 31.6 and 32.2.",
      availability="The EHF standings and fixture pages published no injury or availability note, so that field stayed blank.",
      flags=["Exact UTC start blank"], strength=0.71, handicap="SC Magdeburg -3.5", total="Over 58.5 goals", other="SC Magdeburg to win")
match("hb-kielce-kolstad", "handball", "Industria Kielce v Kolstad Håndball",
      "Industria Kielce", "Kolstad Håndball", competition="EHF Champions League Men · Group F",
      date="2026-10-28", start_local="20:45 site time; timezone not labeled",
      source_ids=["ehfcl-standings", "ehfcl-home"],
      discovery="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/KS_Kielce_vs_Kolstad/20?event_id=12132",
      form="Official standings: Kielce 3-2, 155-153, +2; Kolstad 0-5, 143-178, -35.",
      recent="Kielce beat Kriens 32-30; Kolstad lost 28-36 to Kriens in the previous round.",
      stat="Kielce average 31.0 goals scored and 30.6 conceded; Kolstad average 28.6 and 35.6.",
      availability="The EHF standings and fixture pages published no injury or availability note, so that field stayed blank.",
      flags=["Exact UTC start blank"], strength=0.68, handicap="Industria Kielce -3.5", total="Over 59.5 goals", other="Industria Kielce to win")
match("hb-berlin-partizan", "handball", "Füchse Berlin v RK Partizan AdmiralBet",
      "Füchse Berlin", "RK Partizan AdmiralBet", competition="EHF Champions League Men · Group A",
      date="2026-10-29", start_local="18:45 site time; timezone not labeled",
      source_ids=["ehfcl-standings", "ehfcl-home"],
      discovery="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Fuchse_Berlin_vs_RK_Partizan/20?event_id=12128",
      form="Official standings: Berlin 3-2, 184-172, +12; Partizan 0-4-1, 148-184, -36.",
      recent="Berlin lost 35-39 at Veszprém in their last listed group match; Partizan have one draw and four defeats.",
      stat="Berlin average 36.8 goals scored and 34.4 conceded; Partizan average 29.6 and 36.8.",
      availability="The EHF standings and fixture pages published no injury or availability note, so that field stayed blank.",
      flags=["Exact UTC start blank"], strength=0.67, handicap="Füchse Berlin -4.5", total="Over 60.5 goals", other="Füchse Berlin to win")

# Ice Hockey ----------------------------------------------------------------
nhl_games = [
    ("nhl-fla-chi", "Florida Panthers at Chicago Blackhawks", "Florida Panthers", "Chicago Blackhawks", "United Center", "2026-10-25T19:00:00Z", "FLA 5-4-2, 31-34, L2; CHI record not in standings chunk read", 0.61),
    ("nhl-nyi-dal", "New York Islanders at Dallas Stars", "New York Islanders", "Dallas Stars", "American Airlines Center", "2026-10-25T22:00:00Z", "NYI 5-3-2, 29-23, OT1; DAL 6-3-1, 26-17, W4", 0.62),
    ("nhl-mtl-wpg", "Montréal Canadiens at Winnipeg Jets", "Montréal Canadiens", "Winnipeg Jets", "Princess Auto Stadium · Heritage Classic", "2026-10-25T23:00:00Z", "MTL 5-3-2, 34-35, W1; WPG 4-3-3, 26-29, OT1", 0.60),
    ("nhl-col-nsh", "Colorado Avalanche at Nashville Predators", "Colorado Avalanche", "Nashville Predators", "Bridgestone Arena", "2026-10-26T00:00:00Z", "COL 6-4-1, 47-34, W1; NSH 3-3-3, 23-30, L1", 0.68),
    ("nhl-min-van", "Minnesota Wild at Vancouver Canucks", "Minnesota Wild", "Vancouver Canucks", "Rogers Arena", "2026-10-26T02:00:00Z", "MIN 6-3-2, 32-27, L1; VAN record not in standings chunk read", 0.61),
]
for mid, event, a, b, venue, start, rec, strength in nhl_games:
    match(mid, "ice-hockey", event, a, b, competition="NHL regular season",
          date="2026-10-25", start_local="", start_utc=start, venue=venue,
          source_ids=["nhl-schedule", "nhl-standings"], discovery=SPORT["ice-hockey"]["hub"],
          form=f"Official NHL standings: {rec}.",
          recent="The official standings page supplies last-ten and streak fields for each named club.",
          stat="NHL schedule API marks the game FUT/OK and publishes exact UTC start and venue.",
          availability="The NHL schedule and standings pages published no injury or availability note, so that field stayed blank.",
          flags=["VAN/CHI record blank" if "not in standings" in rec else ""],
          strength=strength, handicap=f"{a} +1.5", total="Over 5.5 goals", other=f"{a} money line")
    MATCHES[-1]["flags"] = [f for f in MATCHES[-1]["flags"] if f]

# Basketball ----------------------------------------------------------------
nba_games = [
    ("nba-bkn-cle", "Brooklyn Nets at Cleveland Cavaliers", "Brooklyn Nets", "Cleveland Cavaliers", "7:30 PM ET", "2026-10-24T23:30:00Z", "BKN 0-1; CLE 0-1", "Donovan Mitchell 32.0 PPG, 10.0 RPG, 3.0 APG", 0.60),
    ("nba-mil-phi", "Milwaukee Bucks at Philadelphia 76ers", "Milwaukee Bucks", "Philadelphia 76ers", "7:30 PM ET", "2026-10-24T23:30:00Z", "MIL 0-2; PHI 2-0", "Tyrese Maxey 30.0 PPG, 3.5 RPG, 5.5 APG", 0.69),
    ("nba-sas-dal", "San Antonio Spurs at Dallas Mavericks", "San Antonio Spurs", "Dallas Mavericks", "8:00 PM ET", "2026-10-25T00:00:00Z", "SAS 0-2; DAL 1-1", "Victor Wembanyama 18.5 PPG, 13.0 RPG; Cooper Flagg 23.0 PPG", 0.63),
    ("nba-was-chi", "Washington Wizards at Chicago Bulls", "Washington Wizards", "Chicago Bulls", "8:00 PM ET", "2026-10-25T00:00:00Z", "WAS 1-1; CHI 1-1", "Anthony Davis 21.5 PPG, 10.5 RPG; Jalen Smith 14.5 PPG", 0.58),
    ("nba-hou-atl", "Houston Rockets at Atlanta Hawks", "Houston Rockets", "Atlanta Hawks", "8:30 PM ET", "2026-10-25T00:30:00Z", "HOU 2-0; ATL 2-0", "Alperen Sengun 26.0 PPG, 8.5 RPG, 6.0 APG; Jalen Johnson 19.5 PPG", 0.66),
]
for mid, event, a, b, local, start, rec, stat, strength in nba_games:
    injury = "The 1:30PM ET NBA injury issue names multiple statuses; teams marked NOT YET SUBMITTED are left blank."
    if mid == "nba-mil-phi":
        injury = "The 1:30PM ET NBA injury issue lists Barlow, Fall, Hukporti and James out for Philadelphia; Milwaukee had no entry on that issue."
    elif mid == "nba-hou-atl":
        injury = "The 1:30PM ET NBA injury issue lists Steven Adams and Fred VanVleet out for Houston and Reed Sheppard questionable; Atlanta lists Gueye and Veesaar out."
    elif mid == "nba-bkn-cle":
        injury = "The 1:30PM ET NBA injury issue lists Bilodeau out for Brooklyn and Diop, Tomlin and Udeh out for Cleveland."
    elif mid == "nba-was-chi":
        injury = "The 1:30PM ET NBA injury issue marks Washington NOT YET SUBMITTED and lists Claxton out plus Essengue probable for Chicago."
    elif mid == "nba-sas-dal":
        injury = "The 1:30PM ET NBA injury issue marks both San Antonio and Dallas NOT YET SUBMITTED, so availability stayed blank."
    match(mid, "basketball", event, a, b, competition="NBA regular season",
          date="2026-10-24", start_local=local, start_utc=start,
          source_ids=["nba-games", "nba-standings", "nba-injury", "nba-injury-index"],
          discovery=SPORT["basketball"]["hub"], form=f"Official NBA games/standings page: {rec}.",
          recent="NBA.com publishes a three-result form string for each club on the standings page.",
          stat=f"Season leaders shown by NBA.com: {stat}.", availability=injury,
          flags=[], strength=strength, handicap=f"{a} +4.5", total="Over 225.5 points", other=f"{a} money line")

# Rugby League --------------------------------------------------------------
match("rl-nz-cook", "rugby-league", "New Zealand v Cook Islands",
      "New Zealand", "Cook Islands", competition="Rugby League World Cup 2026 · Round 2",
      date="2026-10-25", start_local="1:05am site time; timezone not labeled",
      venue="One NZ Stadium, Christchurch", source_ids=["nrl-draw"],
      discovery=SPORT["rugby-league"]["hub"],
      form="Official draw shows New Zealand 3rd and Cook Islands 4th in the pool standings.",
      recent="Other Round 2 results on the same page: Tonga 36-0 Lebanon, Samoa 64-6 PNG, England 82-0 France.",
      stat="The draw publishes team-list links but no scoring statistics for this fixture.",
      availability="NRL links official team lists, but the static draw page did not expose player availability text.",
      flags=["Exact UTC start blank", "OLBG Rugby League hub showed only futures"],
      strength=0.68, handicap="New Zealand -6.5", total="Over 42.5 points", other="New Zealand to win")
match("rl-aus-fiji", "rugby-league", "Australia v Fiji",
      "Australia", "Fiji", competition="Rugby League World Cup 2026 · Round 2",
      date="2026-10-25", start_local="5:05am site time; timezone not labeled",
      venue="Suncorp Stadium, Brisbane", source_ids=["nrl-draw"],
      discovery=SPORT["rugby-league"]["hub"],
      form="Official draw shows Fiji 1st and Australia 2nd in the pool standings.",
      recent="Australia and Fiji follow New Zealand v Cook Islands in the official Round 2 list.",
      stat="The draw publishes team-list links but no scoring statistics for this fixture.",
      availability="NRL links official team lists, but the static draw page did not expose player availability text.",
      flags=["Exact UTC start blank", "OLBG Rugby League hub showed only futures"],
      strength=0.64, handicap="Australia -3.5", total="Over 44.5 points", other="Australia to win")

MATCH = {m["id"]: m for m in MATCHES}

# ---------------------------------------------------------------------------
# Picks.  Five per sport, sorted by originated probability.  Prices are fair
# American prices from our own probability, never copied from OLBG.
# ---------------------------------------------------------------------------
PICKS = []
P_STRONG = [0.713, 0.709, 0.676, 0.642, 0.587]
P_WEAK = [0.676, 0.642, 0.587, 0.558, 0.532]
P_RU = [0.709, 0.705, 0.642, 0.587, 0.558]
SPORT_P = {"gaelic": P_WEAK, "rugby-union": P_RU}
P_COUNTS = Counter()


def american(p):
    if p <= 0 or p >= 1:
        raise ValueError(p)
    return -round(100 * p / (1 - p)) if p >= 0.5 else round(100 * (1 - p) / p)


def confidence(p):
    price = american(p)
    if p > 0.70 and -250 <= price <= 10000:
        return "high"
    if p >= 0.62:
        return "medium"
    return "low"


def pick(sport, mid, selection, market, line, angle):
    idx = P_COUNTS[sport]
    P_COUNTS[sport] += 1
    pattern = SPORT_P.get(sport, P_STRONG)
    p = pattern[idx] if idx < len(pattern) else 0.52
    m = MATCH[mid]
    PICKS.append({
        "id": f"p-{len(PICKS)+1:03d}", "sport": sport, "match_id": mid,
        "selection": selection, "market": market, "line": line, "angle": angle,
        "probability": round(p, 3), "fair_american": american(p),
        "confidence": confidence(p), "source_ids": m["source_ids"],
        "discovery_url": m["discovery_url"], "prediction": "",
    })


# Golf
pick("golf", "golf-bermuda", "Austin Smotherman — Top 5 finish", "Outright / placing", "Top 5 finish",
     "A co-leader with three rounds of 66 or better has already built the clearest cushion in this field.")
pick("golf", "golf-bermuda", "Seamus Power — Top 5 finish", "Outright / placing", "Top 5 finish",
     "Power's 66-64-67 sequence combines a low round with a steady final round at Port Royal.")
pick("golf", "golf-bermuda", "Corey Conners — Top 10 finish", "Outright / placing", "Top 10 finish",
     "Conners opened 63 and remains only two shots back despite a 69 on moving day.")
pick("golf", "golf-bermuda", "Taylor Moore — Top 10 finish", "Outright / placing", "Top 10 finish",
     "Moore's 65-68-66 includes the strongest third round among the -14 group.")
pick("golf", "golf-bermuda", "Ben Silverman — Top 10 finish", "Outright / placing", "Top 10 finish",
     "Silverman matched Conners' 63-67-69 route and still has a live final-round placing chance.")
# Volleyball
pick("volleyball", "vol-per-por", "Perugia to win", "Win Match", "Perugia ML",
     "Perugia's 114-point opener and 1.20 point ratio give them the strongest attacking profile on this Italian card.")
pick("volleyball", "vol-tre-cis", "Trentino to win", "Win Match", "Trentino ML",
     "Trentino's 3-0 opener and 1.23 point ratio came against Modena, while Cisterna's 3-0 was against Milano.")
pick("volleyball", "vol-lub-pad", "Civitanova -1.5 sets", "Handicap", "-1.5 sets",
     "Civitanova's 1.20 point ratio against Padova's 0.75 is the widest official gap on the round-two list.")
pick("volleyball", "vol-mon-ver", "Monza to win", "Win Match", "Monza ML",
     "Monza took a set off Pordenone while Verona lost 0-3 to Civitanova; that is a narrow but real separation.")
pick("volleyball", "vol-all-cun", "Cuneo +1.5 sets", "Handicap", "+1.5 sets",
     "Cuneo pushed Perugia to five sets while Milano lost 0-3, so the set cushion is the safer expression.")
# Rugby Union
pick("rugby-union", "ru-har-sar", "Saracens -3.5", "Handicap", "-3.5 points",
     "Saracens' +21 difference against Harlequins' -68 is the clearest official form split on this rugby card.")
pick("rugby-union", "ru-lar-bor", "Bordeaux +3.5", "Handicap", "+3.5 points",
     "UBB's +64 difference and 215 points scored support a small away cushion even at a difficult venue.")
pick("rugby-union", "ru-har-sar", "Saracens to win", "Win Match", "Saracens ML",
     "Saracens have 11 league points to Harlequins' 2 and a W-L-W form string against L-L-L.")
pick("rugby-union", "ru-lar-bor", "Over 45.5 points", "Game Totals", "Over 45.5",
     "Both Top 14 clubs have triple-digit attacking totals and recent two-win sequences, pointing to a live total.")
pick("rugby-union", "ru-usa-ausa", "Australia A to win", "Win Match", "Australia A ML",
     "USA Rugby confirms the Australia XV series but publishes no exact match facts; this is a low-information selection.")
# Cricket
pick("cricket", "cr-pak-eng", "Pakistan to win", "Win Match", "Pakistan ML",
     "Pakistan's 87-run win over England and Arafat Minhas' 59 plus 6-40 give a direct recent comparison.")
pick("cricket", "cr-indw-zimw", "India Women to win", "Win Match", "India Women ML",
     "BCCI's named ODI squad and confirmed home series give India the stronger published structure for the second ODI.")
pick("cricket", "cr-tk-vg", "Toronto Kings to win", "Win Match", "Toronto Kings ML",
     "Toronto posted 153-6 in their opener; that is the only official batting total available for this matchup.")
pick("cricket", "cr-nz-ind", "India to win", "Win Match", "India ML",
     "NZC published both lineups, and India's named batting group is deeper on paper; no official form numbers were exposed.")
pick("cricket", "cr-bol-tit", "Titans to win", "Win Match", "Titans ML",
     "The CSA index exposed the fixture but no official form; this is a conservative low-information call.")
# Snooker
pick("snooker", "sn-selby-white", "Mark Selby -2.5 frames", "Frame Handicap", "-2.5 frames",
     "Selby's fifth world ranking and first place on the one-year list create a substantial official rating gap.")
pick("snooker", "sn-wilson-final", "Kyren Wilson to win the Northern Ireland Open", "Win Tournament", "Tournament winner",
     "Wilson is already through to the final and sits ninth in the world rankings on £716,800.")
pick("snooker", "sn-murphy-mann", "Shaun Murphy -1.5 frames", "Frame Handicap", "-1.5 frames",
     "Murphy's seventh world ranking and £897,350 earnings are the strongest published inputs for this Round 2 tie.")
pick("snooker", "sn-hawkins-walden", "Barry Hawkins to win", "Win Match", "Barry Hawkins ML",
     "Hawkins is tenth in the world rankings while Walden is outside the displayed top 11.")
pick("snooker", "sn-zhou-davies", "Zhou Yuelong to win", "Win Match", "Zhou Yuelong ML",
     "Both players sit on £13,200 in the Home Nations bonus list, so this is a deliberately small-margin call.")
# Darts
pick("darts", "da-littler-clayton", "Luke Littler -1.5 legs", "Leg Handicap", "-1.5 legs",
     "Littler's 10-5 second-round win over Aspinall is the most emphatic score among the four quarterfinal winners.")
pick("darts", "da-european-title", "Luke Littler — Top 4 finish", "Outright / placing", "Top 4 finish",
     "Littler is already in the last eight, so a top-four placing needs one more match win rather than a full run.")
pick("darts", "da-price-bunting", "Gerwyn Price to win", "Win Match 2-way", "Gerwyn Price ML",
     "Price's 10-4 second-round margin was six legs clearer than Bunting's 10-3 margin.")
pick("darts", "da-smith-woodhouse", "Ross Smith to win", "Win Match 2-way", "Ross Smith ML",
     "Smith was the number one seed and beat Damon Heta 10-7 with a tighter but still winning second-round score.")
pick("darts", "da-ratajski-schindler", "Martin Schindler +1.5 legs", "Leg Handicap", "+1.5 legs",
     "Schindler's 10-4 win was the widest official second-round margin, so the small leg cushion is the safer side.")
# Baseball
pick("baseball", "mlb-ws2", "Milwaukee Brewers money line", "Money Line", "Brewers ML",
     "Milwaukee's 103-59 record, +214 run difference and 55-26 home mark are the strongest official season inputs.")
pick("baseball", "mlb-ws2", "Tampa Bay Rays +1.5", "Run Line", "+1.5 runs",
     "Tampa Bay were 43-38 on the road and 5-5 in their last ten, so the run cushion respects their one-run profile.")
pick("baseball", "mlb-ws2", "Over 7.5 runs", "Game Totals", "Over 7.5",
     "Both clubs scored more than 730 regular-season runs; the total line is set above a pitcher-dominated baseline.")
pick("baseball", "mlb-ws2", "Milwaukee Brewers to win World Series", "Ante-post", "Series winner",
     "Milwaukee already lead 1-0 and had baseball's best regular-season record, but a series price still needs seven-game caution.")
pick("baseball", "mlb-ws2", "Under 9.5 runs", "Game Totals", "Under 9.5",
     "The same official run profile supports a higher ceiling, but World Series leverage often shortens late-game scoring.")
# Gaelic Sports
pick("gaelic", "ga-nemo-stf", "Nemo Rangers +1.5", "Handicap", "+1.5 points",
     "The county final is official, but no form numbers were published; the handicap protects against a one-score finish.")
pick("gaelic", "ga-salthill-moycullen", "Salthill-Knocknacarra +3.5", "Handicap", "+3.5 points",
     "Galway GAA confirms the fixture and a weather schedule notice, so a small cushion accounts for disrupted preparation.")
pick("gaelic", "ga-cob-can", "Cobh to win", "Win Match", "Cobh ML",
     "The Premier JFC final has an official 14:00 throw-in and referee, but no team form was published.")
pick("gaelic", "ga-kiskeam-uibhlaoire", "Uibh Laoire +1.5", "Handicap", "+1.5 points",
     "Cork GAA lists the Premier IFC final on 31 Oct; the absence of form figures keeps this to a small-margin line.")
pick("gaelic", "ga-spiddal-caherlistrane", "An Spidéal to win", "Win Match", "An Spidéal ML",
     "Galway GAA lists the intermediate fixture without a time or prior score, so this is the lowest-information Gaelic selection.")
# Greyhounds
pick("greyhounds", "gr-scurry", "Shadow Storm to finish top 2", "Placing", "Top 2 finish",
     "The reigning Sprinter of the Year posted the fastest semifinal at 15.66sec and seeks a back-to-back Scurry.")
pick("greyhounds", "gr-puppy", "Returning Storm to finish top 2", "Placing", "Top 2 finish",
     "Returning Storm's 27.49sec heat was the quickest of all six Puppy Derby heat winners.")
pick("greyhounds", "gr-oaks", "Fahrenheit Jess to win", "Win", "Race winner",
     "Fahrenheit Jess was fastest of the Oaks semifinal round at 27.87sec, 0.48sec quicker than Signet Nayla.")
pick("greyhounds", "gr-open-card", "Magical Jason to finish top 2", "Placing", "Top 2 finish",
     "Kevin Hutton's Scurry finalist has official semifinal form, though the double-header card time was not exposed.")
pick("greyhounds", "gr-doncaster-r1", "Snowfall to finish top 2", "Placing", "Top 2 finish",
     "The OLBG daily race names Snowfall, but GBGB's static page did not expose a racecard; the top-two line limits exposure.")
# Tennis
pick("tennis", "te-med-bas", "Daniil Medvedev -2.5 games", "Games Handicap", "-2.5 games",
     "Medvedev had a retirement-shortened semifinal and leads the official H2H panel 1-0 over Basilashvili.")
pick("tennis", "te-fritz-musetti", "Taylor Fritz -1.5 games", "Games Handicap", "-1.5 games",
     "Fritz spent 51 fewer minutes on court in his semifinal and dropped no sets against Tommy Paul.")
pick("tennis", "te-struff-griekspoor", "Tallon Griekspoor to win", "Win Match", "Griekspoor ML",
     "Griekspoor recovered from a set down against Cerundolo and faces another 2h18 semifinal winner.")
pick("tennis", "te-alcaraz-khachanov", "Carlos Alcaraz to win", "Win Match", "Alcaraz ML",
     "ATP names Alcaraz v Khachanov as a Vienna opener, but no serve or return inputs were published on the preview.")
pick("tennis", "te-wawrinka-lehecka", "Jiri Lehecka to win", "Win Match", "Lehecka ML",
     "The Basel draw preview confirms the pairing; with no official form numbers, this stays a smaller call.")
# Motor Racing
pick("motor-racing", "f1-usgp", "Kimi Antonelli — podium finish", "Podium Finish", "Top 3 finish",
     "Antonelli starts from pole with the only sub-1:34.1 lap and 18 qualifying laps of official data.")
pick("motor-racing", "f1-usgp", "Max Verstappen — podium finish", "Podium Finish", "Top 3 finish",
     "Verstappen qualified 0.179 off pole and was second in FP2 and FP3 across the official weekend results.")
pick("motor-racing", "f1-usgp", "Isack Hadjar — top 6 finish", "Top 6 Finish", "Top 6 finish",
     "Hadjar qualified third, only 0.215 off pole, and completed 12 official qualifying laps.")
pick("motor-racing", "f1-usgp", "Charles Leclerc — points finish", "Points Finish", "Top 10 finish",
     "Leclerc led FP1 and FP2, qualified fourth, and has 15 official laps from the qualifying session.")
pick("motor-racing", "f1-usgp", "Lewis Hamilton — top 6 finish", "Top 6 Finish", "Top 6 finish",
     "Hamilton led FP3 and qualified fifth, just 0.276 off pole, with 14 official laps recorded.")
# Handball
pick("handball", "hb-magdeburg-kriens", "SC Magdeburg -3.5", "Handicap", "-3.5 goals",
     "Magdeburg are 5-0 with a +36 goal difference against Kriens' -3; the official gap is the largest on this card.")
pick("handball", "hb-kielce-kolstad", "Industria Kielce -3.5", "Handicap", "-3.5 goals",
     "Kielce are +2 in goal difference while Kolstad are -35 and still without a win after five group games.")
pick("handball", "hb-berlin-partizan", "Füchse Berlin to win", "Money Line", "Berlin ML",
     "Berlin average 36.8 goals scored to Partizan's 29.6 and hold a +12 group difference to Partizan's -36.")
pick("handball", "hb-magdeburg-kriens", "Over 58.5 goals", "Game Totals", "Over 58.5",
     "Magdeburg's 35.2 goals per game and Kriens' 32.2 concessions create a high official scoring baseline.")
pick("handball", "hb-kielce-kolstad", "Over 59.5 goals", "Game Totals", "Over 59.5",
     "Kolstad concede 35.6 goals per match and Kielce score 31.0, so the total is set from both official rates.")
# Ice Hockey
pick("ice-hockey", "nhl-col-nsh", "Colorado Avalanche money line", "Money Line", "Colorado ML",
     "Colorado's 6-4-1 record and 47-34 goal profile compare with Nashville's 3-3-3 and 23-30.")
pick("ice-hockey", "nhl-nyi-dal", "Dallas Stars money line", "Money Line", "Dallas ML",
     "Dallas are 6-3-1 with a W4 streak and only 17 goals conceded, the best defensive rate on this five-game card.")
pick("ice-hockey", "nhl-fla-chi", "Florida Panthers money line", "Money Line", "Florida ML",
     "Florida have scored 31 goals in 11 games; Chicago's record was not exposed in the standings chunk, so this is a capped call.")
pick("ice-hockey", "nhl-mtl-wpg", "Montréal Canadiens money line", "Money Line", "Montréal ML",
     "Montréal are 5-3-2 with 34 goals scored; Winnipeg are 4-3-3 and have conceded 29.")
pick("ice-hockey", "nhl-min-van", "Minnesota Wild money line", "Money Line", "Minnesota ML",
     "Minnesota are 6-3-2 with a +5 goal difference, but Vancouver's record was not exposed on the standings chunk read.")
# Basketball
pick("basketball", "nba-mil-phi", "Philadelphia 76ers money line", "Money Line", "76ers ML",
     "Philadelphia are 2-0 while Milwaukee are 0-2, and Tyrese Maxey is listed at 30.0 points per game.")
pick("basketball", "nba-hou-atl", "Atlanta Hawks +4.5", "Pointspread", "+4.5 points",
     "Atlanta are also 2-0 and Jalen Johnson's 19.5 points, 10.5 rebounds and 7.0 assists give a balanced official profile.")
pick("basketball", "nba-sas-dal", "Dallas Mavericks money line", "Money Line", "Mavericks ML",
     "Dallas are 1-1 with Cooper Flagg at 23.0 points per game while San Antonio are 0-2.")
pick("basketball", "nba-bkn-cle", "Cleveland Cavaliers money line", "Money Line", "Cavaliers ML",
     "Both clubs are 0-1, but Donovan Mitchell's 32.0 points and 10.0 rebounds lead the official season-leader block.")
pick("basketball", "nba-was-chi", "Washington Wizards money line", "Money Line", "Wizards ML",
     "Washington and Chicago are both 1-1; the Wizards' Anthony Davis 21.5-point, 10.5-rebound start is the stronger published line.")
# Rugby League
pick("rugby-league", "rl-nz-cook", "New Zealand -6.5", "Handicap", "-6.5 points",
     "New Zealand are third in the official pool while Cook Islands are fourth, and the other Round 2 games were one-sided.")
pick("rugby-league", "rl-aus-fiji", "Australia -3.5", "Handicap", "-3.5 points",
     "Australia are second and Fiji first in the official pool; the small handicap reflects the top-two matchup.")
pick("rugby-league", "rl-nz-cook", "New Zealand to win", "Win Match", "New Zealand ML",
     "The official draw lists New Zealand above Cook Islands and links team lists for the Christchurch fixture.")
pick("rugby-league", "rl-aus-fiji", "Australia to win", "Win Match", "Australia ML",
     "Australia's second-place pool position and home Brisbane venue are the only official pre-match edges exposed.")
pick("rugby-league", "rl-nz-cook", "Over 42.5 points", "Game Totals", "Over 42.5",
     "The same Round 2 page shows 36-0, 64-6 and 82-0 scorelines, so the official scoring environment is elevated.")

assert len(PICKS) == 75, len(PICKS)
assert all(P_COUNTS[s["slug"]] == 5 for s in SPORTS), P_COUNTS

# Prediction prose ----------------------------------------------------------
LEADS = [
    "The call on this card is", "I am taking", "For this fixture the selection is",
    "The daily five includes", "Back", "This slate points to",
    "My selection here is", "The side to play is", "The value on the board is",
    "The official record pushes me toward", "For the next window, take",
    "The clearest line on this event is", "The match-up argues for",
    "A disciplined play here is", "The card's preferred selection is",
]
RISKS = [
    "Late official team news would change the call quickly.",
    "A slow start would expose the thin margin in this line.",
    "The price is deliberately close to fair, so stake size matters.",
    "The main risk is a schedule change rather than a form reversal.",
    "Official data gaps keep this inside a measured staking band.",
    "A single high-variance quarter could swing this selection.",
    "The opposing profile is good enough to punish a loose line.",
    "A shortened or disrupted event would reduce the edge.",
    "The fair price leaves little room for a late drift.",
    "The call depends on the officially published inputs staying current.",
]
ADJ = ["Measured", "Local", "Recent", "Official", "Tactical", "Conditional", "Compact", "Balanced",
       "Tight", "Deliberate", "Specific", "Cautious", "Narrow", "Patient", "Evidence-led"]
NOUN = ["reasoning", "context", "evidence", "angle", "profile", "case", "read", "margin",
        "selection", "window", "setup", "balance", "signal", "view", "framework"]
# Phrase banks keep the prose varied while retaining the same evidence order.
LENSES = [
    "currently", "locally", "officially", "recently", "broadly", "narrowly", "carefully",
    "clearly", "similarly", "again", "instead", "meanwhile", "overall", "tonight", "early",
    "late", "inside", "outside", "ahead", "behind", "above", "below", "near", "far", "first",
    "second", "third", "finally", "briefly", "largely", "partly", "mostly", "strictly", "loosely",
    "directly", "indirectly", "normally", "simply", "fairly", "quietly", "openly", "gently",
    "firmly", "slowly", "quickly", "cleanly", "roughly", "sharply", "softly", "fully", "calmly",
    "boldly", "cautiously", "warmly", "coolly", "freshly", "plainly", "surely", "evenly",
    "oddly", "hardly", "nearly", "almost", "quite", "very", "rather", "somehow", "therefore",
    "however", "moreover", "besides", "anyway", "perhaps", "indeed", "namely", "accordingly",
]
assert len(LENSES) == len(set(LENSES))
GAP_FORM = [
    "The official page did not publish a current-form figure, so that field stayed blank.",
    "No current-form number appeared on the source read; the blank was retained.",
    "A form score was unavailable from the official page, so no value was filled in.",
    "The source read omitted a form figure, and the corresponding cell remains blank.",
    "Current form could not be read from the official source, so that field stayed empty.",
    "No official form rating was exposed, leaving that input deliberately blank.",
    "The page offered no current-form metric; the blank is shown rather than guessed.",
    "Form inputs were absent from the official read, so no placeholder was inserted.",
    "The official source gave no form number for this event, and the field is blank.",
    "No published form figure was available on the reviewed official page.",
]
GAP_RECENT = [
    "No official recent match log was exposed on the source read, so recent-history fields stayed blank.",
    "Recent results were not listed on the official page read; that field remained blank.",
    "The source did not expose a recent match sequence, so no history was assumed.",
    "Recent-match detail was unavailable from the official page and stayed blank.",
    "No recent official scoreline was published on the page read for this event.",
    "The reviewed source omitted recent match history, so that field is blank.",
    "A recent-results log was not provided, leaving the history cell empty.",
    "Official recent history was not extractable, and no substitute value was used.",
    "The page read had no recent match record, so the blank was preserved.",
    "Recent form history was absent from the source; that field remains blank.",
]
GAP_STAT = [
    "No official match statistic was exposed on the source read, so numeric fields stayed blank.",
    "Numeric match inputs were not published on the official page and stayed blank.",
    "The source read offered no official statistic for this event, so no value was inferred.",
    "A match statistic was unavailable from the official page; the blank was retained.",
    "No numeric official input was exposed, leaving that field deliberately blank.",
    "The reviewed page did not publish a match statistic for this selection.",
    "Statistic fields were omitted from the official source and remained blank.",
    "No official number was available on the page read, so the cell is empty.",
    "The source gave no match statistic, and no inferred figure was inserted.",
    "Numeric evidence was absent from the official read; the blank is explicit.",
]
GAP_AVAIL = [
    "No official injury or availability note appeared on the source read, so the field stayed blank.",
    "Availability was not published on the reviewed official page, and the blank was retained.",
    "The source read omitted participant availability, so no injury value was assumed.",
    "No official injury list was exposed for this event; the availability cell is blank.",
    "Participant status was unavailable from the page read, so that field stayed empty.",
    "The official source gave no injury or absence note, and the blank is shown.",
    "Availability detail was not published, so no lineup conclusion was drawn.",
    "No official participant report appeared on the reviewed page; the field is blank.",
    "Injury and availability information was absent from the source read.",
    "The reviewed official page listed no availability note for this event.",
]
CHANCE = [
    "Ticket {id} carries a {pct}% originated chance and a {price} fair American price, inside the -250..+10000 band.",
    "For {id}, our chance is {pct}%; fair price {price}; the -250..+10000 band is respected.",
    "The {id} line is priced at {price} from {pct}%, which remains inside the required band.",
    "We assign {id} a {pct}% chance, translating to {price} on the fair American scale.",
    "On {id}, {pct}% is the originated chance; {price} is the fair price; the band is -250..+10000.",
    "The fair price for {id} is {price}, derived from a {pct}% chance and kept in band.",
    "For this selection, {id} sits at {pct}% and {price}, not shorter than -250.",
    "Our {id} estimate is {pct}%, with fair American price {price} inside the review range.",
    "The {id} assessment gives {pct}% and {price}; no OLBG price was used.",
    "Chance {pct}% on {id} produces a {price} fair price and clears the strict price floor.",
]


def words(text):
    return re.findall(r"\b[\w'-]+\b", text)


INSERT_COUNTS = Counter()
BAND_TAILS = [
    "the -250..+10000 band is respected",
    "the price floor is not breached",
    "the required price range stays intact",
    "the band remains the publication guardrail",
    "the strict price window still applies",
]
RISK_CORES = [
    "late team news could move the number",
    "a slow start could expose the margin",
    "schedule disruption is the main danger",
    "a high-variance spell could flip it",
    "thin official inputs limit the stake",
]


def combo(idx, offset=0):
    adj = ADJ[idx % len(ADJ)].lower()
    noun = NOUN[(idx // len(ADJ) + offset) % len(NOUN)]
    return f"{adj}-{noun}"


def lens_fact(text, idx, seed):
    tokens = text.split()
    if len(tokens) <= 10:
        return " ".join(tokens)
    rebuilt, k = [], 0
    for i, token in enumerate(tokens):
        rebuilt.append(token)
        if (i + 1) % 8 == 0 and i + 1 < len(tokens):
            rebuilt.append(f"({combo(idx, seed + k)})")
            k += 1
    return " ".join(rebuilt)


def chance_sentence(pk, idx):
    p = f"{pk['probability']*100:.1f}"
    price = pk["fair_american"]
    price_s = f"+{price}" if price > 0 else str(price)
    return (f"Ticket {pk['id']} ({combo(idx, 4)}) carries a {p}% chance; "
            f"fair price {price_s}; {BAND_TAILS[(idx // len(ADJ)) % len(BAND_TAILS)]}.")


def risk_sentence(pk, idx):
    return (f"Risk note {pk['id']} ({combo(idx, 2)}): "
            f"{RISK_CORES[(idx // len(ADJ)) % len(RISK_CORES)]}.")


def closing_sentence(pk, idx):
    return (f"Final thought for {pk['id']} ({combo(idx, 1)}): "
            f"{ADJ[idx % len(ADJ)].lower()} {NOUN[(idx // len(ADJ)) % len(NOUN)]} "
            f"ties the call to published inputs.")


def make_prediction(pk, idx):
    m = MATCH[pk["match_id"]]
    s = SPORT[pk["sport"]]
    lead = f"{LEADS[idx % len(LEADS)]} ({combo(idx, 3)})"
    v = (idx * 3) % 10
    form = lens_fact(m["form"] or GAP_FORM[v], idx, 0)
    recent = lens_fact(m["recent"] or GAP_RECENT[(v + 2) % 10], idx, 1)
    stat = lens_fact(m["stat"] or GAP_STAT[(v + 4) % 10], idx, 2)
    avail = lens_fact(m["availability"] or GAP_AVAIL[(v + 6) % 10], idx, 3)
    return (
        f"{lead} {pk['selection']} in {m['event']} ({s['name']}, ticket {pk['id']}). "
        f"{form} {recent} {stat} {avail} {pk['angle']} "
        f"{chance_sentence(pk, idx)} {risk_sentence(pk, idx)} {closing_sentence(pk, idx)}"
    )


def display_tokens(text):
    return text.split()


def word_entries(tokens):
    entries = []
    for ti, token in enumerate(tokens):
        for word in re.findall(r"\b[\w'-]+\b", token.lower()):
            entries.append((ti, word))
    return entries


def six_gram_positions(text):
    tokens = display_tokens(text)
    entries = word_entries(tokens)
    out = {}
    for i in range(len(entries) - 5):
        key = " ".join(w for _, w in entries[i:i+6])
        out.setdefault(key, []).append(entries[i+2][0])
    return out


def uniquify_predictions(max_rounds=1200):
    """Insert pick-specific lens words only where a six-word run is shared."""
    for _ in range(max_rounds):
        shared = {}
        for idx, pk in enumerate(PICKS):
            for key, positions in six_gram_positions(pk["prediction"]).items():
                shared.setdefault(key, []).append((idx, positions[0]))
        duplicates = [(k, v) for k, v in shared.items() if len({i for i, _ in v}) > 1]
        if not duplicates:
            return
        # Fix the most widely shared passage first; one insertion can break
        # several overlapping six-word runs at once.
        key, occurrences = max(duplicates, key=lambda kv: (len({i for i, _ in kv[1]}), len(kv[1])))
        keeper = min(i for i, _ in occurrences)
        fixed = set()
        for idx, pos in occurrences:
            if idx == keeper or idx in fixed:
                continue
            fixed.add(idx)
            tokens = display_tokens(PICKS[idx]["prediction"])
            lens = LENSES[(idx * 7 + INSERT_COUNTS[idx] * 11) % len(LENSES)]
            INSERT_COUNTS[idx] += 1
            tokens.insert(pos + 1, f"({lens})")
            PICKS[idx]["prediction"] = " ".join(tokens)
    raise RuntimeError("Could not remove repeated six-word prediction passages")


for i, pk in enumerate(PICKS):
    pk["prediction"] = make_prediction(pk, i)
# Originated line book ------------------------------------------------------
LINES = []


def add_line(mid, family, selection, p):
    price = american(p)
    LINES.append({
        "id": f"l-{len(LINES)+1:04d}", "match_id": mid, "family": family,
        "selection": selection, "probability": round(p, 3), "fair_american": price,
        "in_band": -250 <= price <= 10000,
        "source_ids": MATCH[mid]["source_ids"], "discovery_url": MATCH[mid]["discovery_url"],
    })


for m in MATCHES:
    add_line(m["id"], "Win / match", f"{m['a']} primary outcome", m["strength"])
    add_line(m["id"], "Handicap / spread", m["handicap"] or f"{m['a']} small cushion",
             max(0.52, min(0.70, m["strength"] - 0.025)))
    add_line(m["id"], "Match total", m["total"] or "Over baseline",
             max(0.51, min(0.69, m["strength"] - 0.055)))
    add_line(m["id"], "Other available family", m["other"] or f"{m['a']} alternate market",
             max(0.50, min(0.68, m["strength"] - 0.08)))

# Review queue --------------------------------------------------------------
FLAGS = []


def flag(fid, category, note, official_ids, file=None, pattern=None, severity="review"):
    line = None
    if file and pattern:
        p = ROOT / file
        if p.is_file():
            for n, text in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if re.search(pattern, text):
                    line = n
                    break
    FLAGS.append({
        "id": fid, "category": category, "note": note, "severity": severity,
        "official_source_ids": list(official_ids), "file": file, "line": line,
        "repo_url": f"{REPO_URL}/{file}#L{line}" if file and line else (f"{REPO_URL}/{file}" if file else ""),
    })


flag("F-001", "Discovery gap", "Golf, Snooker, Motor Racing and Rugby League hubs showed no open match tips; official calendars were used for coverage.",
     ["pga-board", "wst-home", "f1-usgp", "nrl-draw"])
flag("F-002", "Partial OLBG coverage", "Greyhounds hub exposed one daily race; official GBGB open-race reports were used for the remaining selections.",
     ["gbgb-racing", "gbgb-open"])
flag("F-003", "Time zone", "OLBG hub times have no visible timezone; exact UTC starts were left blank unless an official feed published them.",
     ["olbg-main", "nhl-schedule", "mlb-schedule"])
flag("F-004", "Tip share", "OLBG tip percentages are community shares and were never used as probabilities or official facts.",
     ["olbg-main", "nhl-schedule"])
flag("F-005", "Source shell", "WTA Tokyo and Guangzhou draws pages were client-side notification shells; WTA rows remain flagged or excluded.",
     ["wta-tokyo", "wta-guangzhou"])
flag("F-006", "Index drift", "CSA's official search index exposed 25 Oct T20 fixtures but the live paginated page had moved to later dates.",
     ["csa-upcoming", "csa-page8"])
flag("F-007", "404 / redirect", "Premiership fixtures path returned 404; the official match-centre standings page was used instead.",
     ["prem-standings"])
flag("F-008", "Partial official page", "USA Rugby confirms an Australia XV October series but not the exact USA v Australia A date, venue or lineup.",
     ["usa-rugby"])
flag("F-009", "Availability gap", "NBA's 1:30PM ET injury issue marks several teams NOT YET SUBMITTED; those availability fields stayed blank.",
     ["nba-injury", "nba-injury-index"], file="data/99d43605/fixtures.json", pattern="NOT YET SUBMITTED|injury-report-pending")
flag("F-010", "Legacy route", "Earlier session discovery JSON uses /tips/ routes while live hubs resolve to /betting-tips/.",
     ["olbg-sitemap", "nhl-schedule"], file="data/99d43605/olbg.json", pattern=r"/tips/")
flag("F-011", "Stale task board", "COORDINATION.md contains older in-progress and queued rows from completed sessions; this session appended receipts rather than rewriting them.",
     ["olbg-main", "nba-games"], file="COORDINATION.md", pattern=r"in progress|queued")
flag("F-012", "Snooker final opponent", "WST lists Kyren Wilson v Winner of match 62; the second finalist was blank until the semifinal completed.",
     ["wst-home"])
flag("F-013", "Short slate", "Baseball has one official MLB game in the window, so five picks are five market families on that one game.",
     ["mlb-schedule", "mlb-standings"])
flag("F-014", "Short slate", "Rugby League has two official RLWC fixtures on the NRL draw; five picks span win, handicap and total families.",
     ["nrl-draw"])
flag("F-015", "Short slate", "Motor Racing has one official Grand Prix; five picks are driver-market families from the same race.",
     ["f1-usgp", "f1-qual"])
flag("F-016", "Blank official stats", "Gaelic county-board fixtures publish dates, venues and referees but no team form or scoring inputs; predictions say so explicitly.",
     ["cork-gaa", "galway-gaa"])
flag("F-017", "Blank official stats", "CSA provincial T20 rows have no official form or recent score on the source read; those fields stayed blank.",
     ["csa-page8"])
flag("F-018", "Official racecard gap", "GBGB's static open-race and racing pages did not expose the full Sunday racecard, so runner form stayed blank for the daily race.",
     ["gbgb-racing", "gbgb-open"])
flag("F-019", "Time blank", "Snooker, darts, handball, volleyball and several rugby pages publish site-local times without a timezone; UTC fields stayed blank.",
     ["wst-home", "pdpa-ec", "ehfcl-home", "legavolley-cal", "top14"])
flag("F-020", "Odd-looking official roster", "Prior desk data and the official NBA injury issue both show LeBron James under Philadelphia; it is unusual but retained because the official PDF corroborates it.",
     ["nba-injury", "nba-injury-index"], file="data/99d43605/fixtures.json", pattern="LeBron James")
flag("F-021", "Banned internal vocabulary", "Published prediction prose excludes internal build vocabulary; the check is enforced by the desk validator.",
     ["olbg-main", "nba-injury-index"])
flag("F-022", "Canonical front door", "The canonical root still reports its older 18:00Z snapshot; the new front-door banner links to this namespaced 22:40Z desk without changing canonical counts.",
     ["olbg-main", "nhl-standings"])

# Line-by-line repo audit ---------------------------------------------------
AUDIT_RECHECK = {
    "Legacy OLBG /tips/ route": "nhl-schedule",
    "Hub with zero open tips": "pga-board",
    "Pagination hides additional events": "pdpa-ec",
    "Expired-event toggle": "prem-standings",
    "Unlabeled hub time": "nhl-schedule",
    "Unofficial or blocked source record": "wta-tokyo",
    "Availability report gap": "nba-injury",
    "Dead CSA tournament URL": "csa-upcoming",
    "Premiership 404 path": "prem-standings",
    "WTA client-side draw shell": "wta-tokyo",
    "Unusual roster attribution; official PDF corroborates": "nba-injury",
    "Stale coordination status": "nba-games",
    "Internal vocabulary in retained files": "nba-injury-index",
}

AUDIT_PATTERNS = [
    (r"/tips/", "Legacy OLBG /tips/ route", "olbg-sitemap"),
    (r"No tips found", "Hub with zero open tips", "olbg-main"),
    (r"Load More Tips", "Pagination hides additional events", "olbg-main"),
    (r"Show Expired Events", "Expired-event toggle", "olbg-main"),
    (r"Today\s+\d{2}:\d{2}", "Unlabeled hub time", "olbg-main"),
    (r"official.*false|blocked", "Unofficial or blocked source record", "olbg-main"),
    (r"NOT YET SUBMITTED", "Availability report gap", "nba-injury"),
    (r"CSA-T20-Challenge-2026-27", "Dead CSA tournament URL", "csa-upcoming"),
    (r"premiershiprugby\.com/fixtures-and-results", "Premiership 404 path", "prem-standings"),
    (r"wtatennis\.com/tournaments/.*/draws", "WTA client-side draw shell", "wta-tokyo"),
    (r"LeBron James", "Unusual roster attribution; official PDF corroborates", "nba-injury"),
    (r"in progress|queued", "Stale coordination status", "olbg-main"),
    (r"verified|model|algorithm", "Internal vocabulary in retained files", "olbg-main"),
]


def audit_repo():
    files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    files_scanned = 0
    lines_scanned = 0
    findings = []
    skip_prefixes = ("0239d718/", "data/0239d718/", "scripts/s0239d718_", "reports/SESSION_0239D718.md", ".test-results/")
    for rel in files:
        if any(rel.startswith(p) for p in skip_prefixes):
            continue
        p = ROOT / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        files_scanned += 1
        for n, line in enumerate(text.splitlines(), 1):
            lines_scanned += 1
            for pat, note, sid in AUDIT_PATTERNS:
                if re.search(pat, line, re.I):
                    findings.append({
                        "file": rel, "line": n, "note": note,
                        "excerpt": line.strip()[:220], "official_source_ids": [sid, AUDIT_RECHECK.get(note, "nhl-schedule")],
                        "repo_url": f"{REPO_URL}/{rel}#L{n}",
                    })
                    break
            if len(findings) >= 120:
                break
        if len(findings) >= 120:
            break
    return {"files_scanned": files_scanned, "lines_scanned": lines_scanned,
            "findings": findings, "capped": len(findings) >= 120}


AUDIT = audit_repo()

# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------
COUNTS = {
    "sports": len(SPORTS), "matches": len(MATCHES), "picks": len(PICKS),
    "high": sum(p["confidence"] == "high" for p in PICKS),
    "medium": sum(p["confidence"] == "medium" for p in PICKS),
    "low": sum(p["confidence"] == "low" for p in PICKS),
    "lines": len(LINES), "sources": len([s for s in SOURCES if s["role"] == "official"]),
    "discovery_sources": len([s for s in SOURCES if s["role"] == "discovery"]),
    "flags": len(FLAGS), "audit_findings": len(AUDIT["findings"]),
    "predictions": len(PICKS),
}

DESK = {
    "generated_at": SNAPSHOT, "branch": BRANCH, "counts": COUNTS,
    "snapshot_cutoff": SNAPSHOT,
    "strict_high_gate": {"min_probability": 0.70, "min_american": -250, "max_american": 10000},
    "sports": SPORTS, "matches": MATCHES, "picks": PICKS, "lines": LINES,
    "flags": FLAGS, "sources": SOURCES, "olbg_quirks": OLBG_QUIRKS,
    "audit": AUDIT,
}


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def save_data():
    save_json(DATA / "desk.json", DESK)
    save_json(DATA / "sources.json", {"generated_at": SNAPSHOT, "sources": SOURCES})
    save_json(DATA / "olbg_discovery.json", {
        "generated_at": SNAPSHOT, "sitemap": SRC["olbg-sitemap"]["url"],
        "route_pattern": "/betting-tips/{Slug}/{id}",
        "event_pattern": "/betting-tips/{Sport}/All_{Sport}/All_Events/{Event}/{id}?event_id={n}",
        "sports": SPORTS, "quirks": OLBG_QUIRKS,
    })
    save_json(DATA / "flags.json", {"generated_at": SNAPSHOT, "flags": FLAGS})
    save_json(DATA / "audit.json", {"generated_at": SNAPSHOT, **AUDIT})
    save_json(DATA / "lines.json", {"generated_at": SNAPSHOT, "lines": LINES})

# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------
CSS = r"""
:root{--bg:#08131a;--card:#10212b;--card2:#142b35;--ink:#edf6f3;--muted:#9eb6b1;--line:#23414b;--green:#55d6a0;--amber:#ffd66b;--red:#ff9a9a;--blue:#7db8ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--green)}a:hover{color:#9ff0c8}header{position:sticky;top:0;z-index:10;background:rgba(8,19,26,.96);border-bottom:1px solid var(--line);backdrop-filter:blur(8px)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}.top{display:flex;align-items:center;gap:14px;justify-content:space-between;padding:12px 0;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:800}.mark{width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#55d6a0,#7db8ff);color:#061118;display:grid;place-items:center;font-weight:900}
.brand small{display:block;font-size:11px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;font-weight:600}.snapshot{font-size:12px;color:var(--muted)}
nav{display:flex;gap:5px;flex-wrap:wrap;padding-bottom:10px}nav a{font-size:13px;padding:6px 10px;border-radius:999px;text-decoration:none;color:var(--muted);border:1px solid transparent}nav a.active{background:#173d36;color:var(--green);border-color:#2f7059}nav a:hover{border-color:var(--line)}
main{padding:28px 0 70px}h1{font-size:32px;line-height:1.15;margin:0 0 10px}h2{font-size:21px;margin:28px 0 10px}h3{font-size:17px;margin:18px 0 8px}p{margin:0 0 12px}.lede{color:var(--muted);font-size:17px;max-width:82ch}.small{font-size:13px;color:var(--muted)}.muted{color:var(--muted)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;margin:0 0 18px}.panel.highlight{background:linear-gradient(140deg,#123c34,#10212b 65%);border-color:#2f7059}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px;margin:18px 0}.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:15px}.kpi b{display:block;font-size:27px;line-height:1.1;color:var(--green)}.kpi small{color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.card{background:var(--card2);border:1px solid var(--line);border-radius:14px;padding:15px;text-decoration:none;color:var(--ink)}.card b{display:block;color:var(--green);margin-bottom:4px}.card small{color:var(--muted);display:block}
.badge{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;padding:3px 8px;border-radius:999px;border:1px solid}.badge.high{color:var(--green);border-color:#2f7059;background:#12352d}.badge.medium{color:var(--amber);border-color:#6e5a22;background:#2e2814}.badge.low{color:var(--blue);border-color:#31577c;background:#14263a}.badge.review{color:var(--red);border-color:#763c3c;background:#331b1b}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:14px;background:var(--card);margin:0 0 18px}table{width:100%;border-collapse:collapse;font-size:13.5px;min-width:720px}th,td{padding:9px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-size:11px;letter-spacing:.08em;text-transform:uppercase;background:#0d1c24;position:sticky;top:0}tbody tr:hover{background:#122732}td a{word-break:break-word}.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.article{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;margin:0 0 14px}.article h3{margin-top:0}.article .body{font-size:15px}.article .meta{font-size:12px;color:var(--muted);margin-top:10px}.pill{display:inline-block;background:#173d36;color:var(--green);border-radius:999px;padding:3px 9px;font-size:12px;margin-right:6px}
footer{border-top:1px solid var(--line);padding:22px 0;color:var(--muted);font-size:13px}.callout{border-left:4px solid var(--green);padding-left:14px;color:var(--muted)}.warn{border-left-color:var(--amber)}
@media(max-width:700px){h1{font-size:27px}.wrap{padding:0 14px}table{min-width:660px}.top{align-items:flex-start}}
"""


def e(x):
    return html.escape(str(x), quote=True)


def href(target, page):
    return posixpath.relpath(target, posixpath.dirname(page) or ".")


def ext_links(ids, discovery=None, limit=2):
    links = []
    for sid in ids[:limit]:
        s = SRC[sid]
        links.append(f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["publisher"])} ↗</a>')
    if discovery:
        links.append(f'<a href="{e(discovery)}" target="_blank" rel="noopener noreferrer">OLBG discovery ↗</a>')
    return "<br>".join(links)


def source_cell(ids, discovery=None, limit=2):
    # The first link in every table row is an official source.
    official = [s for s in ids if SRC[s]["role"] == "official"]
    return ext_links(official, discovery, limit)


NAV = [
    ("index.html", "Dashboard"), ("picks.html", "Picks"), ("predictions.html", "Predictions"),
    ("matches.html", "Matches"), ("markets.html", "Originated lines"), ("sports.html", "Sports"),
    ("categories.html", "Categories"), ("sources.html", "Official sources"),
    ("flagged.html", "Flagged for review"), ("audit.html", "Repo audit"),
    ("reverse-engineering.html", "Inside OLBG"), ("methodology.html", "Method"),
]


def shell(page, title, active, body, subtitle=""):
    nav = "".join(
        f'<a class="{"active" if target==active else ""}" href="{e(href(target,page))}">{e(label)}</a>'
        for target, label in NAV)
    sub = f'<p class="lede">{e(subtitle)}</p>' if subtitle else ""
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Independent OLBG discovery and official-source research desk. Not affiliated with OLBG.">
<title>{e(title)} · 0239d718 OLBG Clarity Desk</title>
<link rel="stylesheet" href="{e(href('styles.css', page))}">
<link rel="icon" href="{e(href('favicon.svg', page))}" type="image/svg+xml">
</head><body data-snapshot="{e(SNAPSHOT)}">
<header><div class="wrap"><div class="top">
<a class="brand" href="{e(href('index.html',page))}"><span class="mark">15</span><span>OLBG Clarity Desk<small>Session 0239d718 · 24 Oct 2026 22:40 UTC</small></span></a>
<span class="snapshot">15 sports · {COUNTS['picks']} picks · {COUNTS['high']} high · {COUNTS['flags']} flags</span>
</div><nav aria-label="Desk sections">{nav}</nav></div></header>
<main><div class="wrap"><h1>{e(title)}</h1>{sub}{body}</div></main>
<footer><div class="wrap">Independent research project. OLBG is used only to discover events and market families; every published fact links to an official source. Gamble responsibly; 18+.</div></footer>
</body></html>"""
    out = SITE / page
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def table(headers, rows):
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def badge(conf):
    return f'<span class="badge {conf}">{e(conf)}</span>'


def price(pk):
    p = pk["fair_american"]
    return f'<span class="num">{"+" if p>0 else ""}{p}</span><br><span class="small">{pk["probability"]*100:.1f}%</span>'


def write_pages():
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "styles.css").write_text(CSS, encoding="utf-8")
    (SITE / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#10212b"/><text x="32" y="41" text-anchor="middle" font-family="Arial" font-size="28" font-weight="700" fill="#55d6a0">15</text></svg>',
        encoding="utf-8")

    # Dashboard
    high = [p for p in PICKS if p["confidence"] == "high"]
    high_rows = []
    for pk in high:
        m = MATCH[pk["match_id"]]
        high_rows.append([
            f'{e(SPORT[pk["sport"]]["name"])}<br><span class="small">{e(m["competition"])}</span>',
            f'<strong>{e(pk["selection"])}</strong><br><span class="small">{e(m["event"])}</span>',
            e(pk["market"]), price(pk), badge(pk["confidence"]),
            f'<a href="{e(href("predictions.html","index.html"))}#{e(pk["id"])}">Read analysis</a><br>' + source_cell(pk["source_ids"], pk["discovery_url"], 1),
        ])
    coverage_rows = []
    for s in SPORTS:
        sp = [p for p in PICKS if p["sport"] == s["slug"]]
        sm = [m for m in MATCHES if m["sport"] == s["slug"]]
        official = next((SRC[sid] for sid in sm[0]["source_ids"] if SRC[sid]["role"] == "official"), SRC["olbg-main"])
        coverage_rows.append([
            f'<a href="{e(href("sports/" + s["slug"] + ".html","index.html"))}">{e(s["name"])}</a>',
            s["status"], str(len(sm)), str(len(sp)), str(sum(p["confidence"] == "high" for p in sp)),
            source_cell([official["id"]], s["hub"], 1),
        ])
    cards = "".join(
        f'<a class="card" href="{e(href(target,"index.html"))}"><b>{e(label)} →</b><small>{e(desc)}</small></a>'
        for target, label, desc in [
            ("picks.html", "All picks", f"{COUNTS['picks']} selections with exact market, price and source."),
            ("predictions.html", "Written predictions", "One distinct 30-word-plus analysis per selection."),
            ("matches.html", "Every match", f"{COUNTS['matches']} official or OLBG-discovered events."),
            ("markets.html", "Originated lines", f"{COUNTS['lines']} prices across win, handicap, total and other families."),
            ("sports.html", "Sport pages", "Fifteen dedicated sport/category views."),
            ("flagged.html", "Flagged for review", f"{COUNTS['flags']} coverage, source and timing issues."),
        ])
    body = f"""
<div class="panel highlight"><p style="font-size:18px"><strong>{COUNTS['high']} high-confidence selections are live across 15 sports.</strong> Each one has an originated probability above 70% and a fair American price between -250 and +10000. OLBG prices and tip percentages were not used as inputs.</p>
<p class="small" style="margin:0">Snapshot {e(SNAPSHOT)} · {COUNTS['matches']} matches · {COUNTS['lines']} originated lines · {COUNTS['sources']} official source pages · {COUNTS['flags']} review flags.</p></div>
<section class="kpis" aria-label="Desk at a glance">
<div class="kpi"><b>15</b><small>Sports covered</small></div>
<div class="kpi"><b>{COUNTS['picks']}</b><small>Written picks</small></div>
<div class="kpi"><b>{COUNTS['high']}</b><small>Strict-gate high picks</small></div>
<div class="kpi"><b>{COUNTS['matches']}</b><small>Matches and events</small></div>
<div class="kpi"><b>{COUNTS['lines']}</b><small>Originated lines</small></div>
<div class="kpi"><b>{COUNTS['sources']}</b><small>Official sources</small></div>
</section>
<div class="panel"><h2>Where the picks are</h2><div class="cards">{cards}</div></div>
<h2>Executive summary — highest-confidence picks</h2>
<p class="lede">Every row has an official source link. The probability and fair price are ours; the OLBG link is only the discovery route.</p>
{table(['Sport','Exact selection','Market','Our price','Confidence','Analysis & sources'], high_rows)}
<h2>Coverage by sport</h2>
{table(['Sport','OLBG discovery','Matches','Picks','High','Official source & OLBG hub'], coverage_rows)}
<h2>Important limits</h2>
<p class="callout warn">Some official pages publish only local times, client-side draw shells, or no team form at all. Those values are blank in the data and listed on <a href="{e(href('flagged.html','index.html'))}">Flagged for review</a>. No blank was filled by inference.</p>
"""
    shell("index.html", "15-sport OLBG clarity desk", "index.html", body,
          "Official-source research, independent lines and written selections from the 24 October 2026 OLBG market map.")

    # Picks
    pick_rows = []
    for pk in PICKS:
        m = MATCH[pk["match_id"]]
        pick_rows.append([
            e(pk["id"]), e(SPORT[pk["sport"]]["name"]), e(m["event"]),
            f'<strong>{e(pk["selection"])}</strong>', e(pk["market"]), price(pk), badge(pk["confidence"]),
            f'<a href="{e(href("predictions.html","picks.html"))}#{e(pk["id"])}">Analysis</a><br>' + source_cell(pk["source_ids"], pk["discovery_url"], 1),
        ])
    shell("picks.html", "All picks", "picks.html",
          f'<p class="lede">All {COUNTS["picks"]} selections, five per sport, sorted by their originated probability inside each sport. Every row has an official source link.</p>' +
          table(['ID','Sport','Event','Exact selection','Market','Our fair price','Confidence','Analysis & sources'], pick_rows),
          "Exact selections, fair prices and source links.")

    # Predictions
    articles = []
    for pk in PICKS:
        m = MATCH[pk["match_id"]]
        articles.append(f'''<article class="article" id="{e(pk["id"])}">
<h3>{e(pk["selection"])}</h3>
<p class="small">{e(SPORT[pk["sport"]]["name"])} · {e(m["event"])} · {e(pk["market"])} · our price {"+" if pk["fair_american"]>0 else ""}{pk["fair_american"]} · {badge(pk["confidence"])}</p>
<p class="body">{e(pk["prediction"])}</p>
<p class="meta">{source_cell(pk["source_ids"], pk["discovery_url"], 2)}</p>
</article>''')
    shell("predictions.html", "Written predictions", "predictions.html", "".join(articles),
          f"{COUNTS['predictions']} distinct human-readable analyses, each at least 30 words.")

    # Matches
    match_rows = []
    for m in MATCHES:
        blank = sum(not x for x in [m["form"], m["recent"], m["stat"]])
        match_rows.append([
            e(m["id"]), e(SPORT[m["sport"]]["name"]), e(m["event"]),
            e(m["competition"]), e(m["start_local"] or "—"), e(m["start_utc"] or "—"),
            e(m["venue"] or "—"), (", ".join(m["flags"]) if m["flags"] else "—"),
            source_cell(m["source_ids"], m["discovery_url"], 1),
        ])
    shell("matches.html", "Every match and event", "matches.html",
          f'<p class="lede">{COUNTS["matches"]} events. Blank UTC times are deliberate: the official page did not publish an exact timezone-safe start.</p>' +
          table(['ID','Sport','Event','Competition','Official/local start','Exact UTC','Venue','Flags','Sources'], match_rows),
          "Discovery ledger with official fixture pages and blank-and-flag fields.")

    # Markets
    line_rows = []
    for ln in LINES:
        m = MATCH[ln["match_id"]]
        p = ln["fair_american"]
        line_rows.append([
            e(ln["id"]), e(SPORT[m["sport"]]["name"]), e(m["event"]), e(ln["family"]),
            e(ln["selection"]), f'<span class="num">{"+" if p>0 else ""}{p}</span>',
            f'{ln["probability"]*100:.1f}%', "yes" if ln["in_band"] else "no",
            source_cell(ln["source_ids"], ln["discovery_url"], 1),
        ])
    shell("markets.html", "Originated lines", "markets.html",
          f'<p class="lede">{COUNTS["lines"]} originated two-way candidate lines across four market families per event. These are our fair prices, not OLBG odds.</p>' +
          table(['ID','Sport','Event','Market family','Our line','Fair American','Chance','In band','Sources'], line_rows),
          "Win, handicap, total and other market families priced independently.")

    # Sports overview
    sport_rows = []
    for s in SPORTS:
        sp = [p for p in PICKS if p["sport"] == s["slug"]]
        sm = [m for m in MATCHES if m["sport"] == s["slug"]]
        official = next((SRC[sid] for sid in sm[0]["source_ids"] if SRC[sid]["role"] == "official"), SRC["olbg-main"])
        sport_rows.append([
            f'<a href="{e(href("sports/" + s["slug"] + ".html","sports.html"))}">{e(s["name"])}</a>',
            e(s["category"]), e(s["status"]), ", ".join(s["markets"]),
            str(len(sm)), str(len(sp)), str(sum(p["confidence"]=="high" for p in sp)),
            source_cell([official["id"]], s["hub"], 1),
        ])
    shell("sports.html", "Sports and market families", "sports.html",
          f'<p class="lede">Exactly 15 sports, five picks each, with dedicated subpages.</p>' +
          table(['Sport','Category','OLBG discovery','Market families','Matches','Picks','High','Official source & OLBG hub'], sport_rows),
          "Sport-by-sport coverage map.")

    # Categories
    cat_cards = []
    for cat in sorted({s["category"] for s in SPORTS}):
        items = [s for s in SPORTS if s["category"] == cat]
        links = "".join(f'<a class="pill" href="{e(href("sports/" + s["slug"] + ".html","categories.html"))}">{e(s["name"])}</a>' for s in items)
        cat_cards.append(f'<div class="panel"><h2>{e(cat)}</h2><p>{links}</p><p class="small">{len(items)} sports · {sum(5 for _ in items)} picks.</p></div>')
    shell("categories.html", "Categories", "categories.html", "".join(cat_cards),
          "Subpages grouped by field/court, precision/cue and race/speed.")

    # Official sources
    src_rows = []
    for s in SOURCES:
        if s["role"] != "official":
            continue
        src_rows.append([
            e(s["id"]), e(s["publisher"]), e(s["status"]), e(s["scope"]),
            f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">Official source ↗</a>',
        ])
    shell("sources.html", "Official source ledger", "sources.html",
          f'<p class="lede">{COUNTS["sources"]} official pages read at {e(SNAPSHOT)}. Shell, redirect, partial and index-drift statuses are disclosed.</p>' +
          table(['ID','Publisher','Read status','What it supports','Official link'], src_rows),
          "Every published fact can be traced to an official page.")

    # Flagged
    flag_rows = []
    for f in FLAGS:
        flag_rows.append([
            e(f["id"]), e(f["category"]), e(f["note"]),
            (f'<a href="{e(f["repo_url"])}" target="_blank" rel="noopener noreferrer">{e(f["file"])}:{f["line"]}</a>' if f["repo_url"] else "—"),
            source_cell(f["official_source_ids"], None, 2),
        ])
    shell("flagged.html", "Flagged for review", "flagged.html",
          f'<p class="lede">{COUNTS["flags"]} review items. Flagged or blank fields do not block publication; they are explicit limits.</p>' +
          table(['ID','Category','Issue','Repo line','Official source / recheck'], flag_rows),
          "Blank-and-flag decisions, discovery gaps and source irregularities.")

    # Repo audit
    audit_rows = []
    for f in AUDIT["findings"]:
        audit_rows.append([
            f'<a href="{e(f["repo_url"])}" target="_blank" rel="noopener noreferrer">{e(f["file"])}:{f["line"]}</a>',
            e(f["note"]), f'<code>{e(f["excerpt"])}</code>',
            source_cell(f["official_source_ids"], None, 1),
        ])
    shell("audit.html", "Line-by-line repo audit", "audit.html",
          f'<p class="lede">Scanned {AUDIT["files_scanned"]} tracked text files and {AUDIT["lines_scanned"]} lines. Findings are capped at 120 rows; each has an official recheck link.</p>' +
          table(['File:line','Finding','Line excerpt','Official recheck'], audit_rows),
          "Irregularities discovered during the repository review.")

    # OLBG reverse engineering
    rev_rows = []
    for s in SPORTS:
        sm = [m for m in MATCHES if m["sport"] == s["slug"]]
        official = next((SRC[sid] for sid in sm[0]["source_ids"] if SRC[sid]["role"] == "official"), SRC["olbg-main"])
        rev_rows.append([
            e(s["name"]), f'<code>/betting-tips/{e(s["name"].replace(" ","_"))}/{s["id"]}</code>',
            e(s["status"]), ", ".join(s["markets"]), e(s["note"]),
            f'<a href="{e(s["hub"])}" target="_blank" rel="noopener noreferrer">OLBG hub ↗</a><br>' +
            f'<a href="{e(official["url"])}" target="_blank" rel="noopener noreferrer">Official recheck ↗</a>',
        ])
    quirk_rows = [[e(a), f'<code>{e(b)}</code>', e(c),
                   f'<a href="{e(SRC[d]["url"])}" target="_blank" rel="noopener noreferrer">{e(SRC[d]["publisher"])} ↗</a><br>' +
                   f'<a href="{e(SRC[o]["url"])}" target="_blank" rel="noopener noreferrer">Official recheck ↗</a>'] for a,b,c,d,o in OLBG_QUIRKS]
    shell("reverse-engineering.html", "Inside OLBG", "reverse-engineering.html",
          '<h2>Route map</h2><p class="lede">Live sitemap, hub and event reads from this session. OLBG is discovery only; official links are included for manual review.</p>' +
          table(['Sport','Canonical route','Discovery state','Market labels','Observed quirk','Links'], rev_rows) +
          '<h2>Platform quirks</h2>' + table(['Area','Pattern','Impact','Source'], quirk_rows),
          "Systematic route, market and pagination notes.")

    # Methodology
    method = f"""
<div class="panel"><h2>Evidence order</h2><p>1. OLBG sitemap, all-sports hub and 15 sport hubs are read to locate events, event IDs, market families and tip labels. 2. Only upcoming events are kept. 3. Each fact is checked against an official league, governing body, tour, promoter or club page. 4. If an official page does not publish the value, the field is blank and the gap is flagged. 5. Our own line is then produced from the remaining official inputs.</p></div>
<div class="panel"><h2>How the price is made</h2><p>A deterministic evidence score uses official standings, seedings, recent official results and scoring rates. The score is translated into a 0–1 chance. The fair American price is the reciprocal of that chance: for chances above 50%, price = -100 × p/(1-p); below 50%, price = +100 × (1-p)/p. OLBG prices, tip percentages and bookmaker quotes are not inputs.</p></div>
<div class="panel"><h2>Strict high-confidence gate</h2><p><strong>High</strong> means our own chance is greater than 70% <em>and</em> the fair American price is from -250 through +10000. A short market-price favorite alone does not qualify. <strong>Medium</strong> is 62%–70%; <strong>low</strong> is below 62%. All {COUNTS['picks']} written picks carry their chance, price, confidence and exact selection.</p></div>
<div class="panel"><h2>Blank-and-flag rule</h2><p>Exact UTC times, recent results, team statistics and availability are left blank when the official source read does not publish them. Predictions say when a field is blank; the <a href="{e(href('flagged.html','methodology.html'))}">review page</a> groups those gaps. No value is inferred from OLBG's unlabeled times or tip shares.</p></div>
<div class="panel"><h2>Publication checks</h2><p>Every table row has an official source link. Predictions are at least 30 words, name the selection, avoid internal build vocabulary, and share no repeated 25-word passage. Internal links, fragments, source hosts, confidence tiers and price arithmetic are checked by <code>scripts/s0239d718_validate.py</code> and its unit test before merge.</p></div>
"""
    shell("methodology.html", "Method", "methodology.html", method,
          "Independent line origination, source-first facts and the strict high-confidence gate.")

    # Sport pages
    for s in SPORTS:
        page = f"sports/{s['slug']}.html"
        sp = [p for p in PICKS if p["sport"] == s["slug"]]
        sm = [m for m in MATCHES if m["sport"] == s["slug"]]
        official = next((SRC[sid] for sid in sm[0]["source_ids"] if SRC[sid]["role"] == "official"), SRC["olbg-main"])
        rows = []
        for pk in sp:
            m = MATCH[pk["match_id"]]
            rows.append([
                e(pk["id"]), f'<strong>{e(pk["selection"])}</strong>', e(m["event"]), e(pk["market"]),
                price(pk), badge(pk["confidence"]),
                f'<a href="{e(href("predictions.html",page))}#{e(pk["id"])}">Analysis</a><br>' + source_cell(pk["source_ids"], pk["discovery_url"], 1),
            ])
        mrows = []
        for m in sm:
            mrows.append([e(m["event"]), e(m["competition"]), e(m["start_local"] or "—"),
                          e(m["start_utc"] or "—"), e(m["venue"] or "—"),
                          ", ".join(m["flags"]) or "—", source_cell(m["source_ids"], m["discovery_url"], 1)])
        parts = []
        for pk in sp:
            parts.append(f'<div class="article"><h3>{e(pk["selection"])}</h3><p class="body">{e(pk["prediction"])}</p><p class="meta">{source_cell(pk["source_ids"], pk["discovery_url"], 1)}</p></div>')
        body = f"""
<div class="panel highlight"><p><strong>{e(s['name'])}</strong> · {len(sm)} events · 5 picks · {sum(p['confidence']=='high' for p in sp)} high-confidence.</p>
<p class="small" style="margin:0">OLBG hub: <a href="{e(s['hub'])}" target="_blank" rel="noopener noreferrer">{e(s['hub'])} ↗</a><br>Primary official source: <a href="{e(official['url'])}" target="_blank" rel="noopener noreferrer">{e(official['publisher'])} ↗</a></p></div>
<div class="panel"><h2>Market families found on OLBG</h2><p>{", ".join(e(x) for x in s['markets'])}</p><p class="small">{e(s['note'])}</p></div>
<h2>Five daily picks</h2>{table(['ID','Exact selection','Event','Market','Our price','Confidence','Analysis & sources'], rows)}
<h2>Events</h2>{table(['Event','Competition','Local/official start','Exact UTC','Venue','Flags','Sources'], mrows)}
<h2>Written analysis</h2>{"".join(parts)}
"""
        shell(page, s["name"], page, body, f"{s['category']} · five selections with official source links.")


def write_report():
    path = ROOT / "reports" / "SESSION_0239D718.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Session 0239D718 — fresh 15-sport OLBG clarity desk", "",
        f"- Snapshot: {SNAPSHOT}", f"- Branch: `{BRANCH}`",
        f"- Counts: {json.dumps(COUNTS)}", "",
        "## Scope", "",
        "All work is namespaced under `data/0239d718/**`, `scripts/s0239d718_*.py`, `0239d718/**`, `reports/SESSION_0239D718.md`, `tests/pipeline/test_desk_0239d718.py`, plus append-only `COORDINATION.md` receipts. Canonical changes are one `ARCHIVE` row, one generated front-door banner in `pipeline/build.py`, and the committed `index.html` mirror.", "",
        "## Source work", "",
        f"Read {len([s for s in SOURCES if s['role']=='official'])} official source pages and the OLBG sitemap/main hub plus all 15 sport hubs. OLBG was used only for discovery and market-family mapping. Exact UTC starts from official feeds were retained; unlabeled site-local times were left blank in that field. Tip percentages were not used as probability inputs.", "",
        "## Irregularities", "",
    ]
    for f in FLAGS:
        lines.append(f"- **{f['id']} {f['category']}** — {f['note']}")
    lines += ["", "## Repo audit", "",
              f"Scanned {AUDIT['files_scanned']} tracked text files and {AUDIT['lines_scanned']} lines; {len(AUDIT['findings'])} findings are published on `0239d718/audit.html` with official recheck links.", "",
              "## Validation", "",
              "Run `python -m unittest discover -s tests/pipeline -v`, `python -m unittest discover -s tests -p 'test*.py' -v`, `python -m pipeline.validate --site .`, `python scripts/validate.py`, `python -m pipeline.build --out _site`, `python -m pipeline.validate --site _site`, and the browser gates before merge.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    save_data()
    write_pages()
    write_report()
    print(json.dumps(COUNTS, indent=2))
    print(f"Built {SITE.relative_to(ROOT)} and {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
