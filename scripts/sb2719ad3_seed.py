#!/usr/bin/env python3
"""Persist the TB2719 evidence register; observations only, no price calculations."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "b2719ad3"
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

sources: dict[str, dict] = {}
events: list[dict] = []


def source(key: str, publisher: str, url: str, supports: str) -> None:
    sources[key] = {
        "publisher": publisher,
        "url": url,
        "supports": supports,
        "accessed_at": NOW,
        "access": "Fetched or located through the research tool; shell egress was not relied upon.",
    }


def event(
    event_id: str,
    sport: str,
    competition: str,
    home: str,
    away: str,
    start_utc: str | None,
    start_display: str,
    official: str,
    evidence: list[str],
    *,
    venue: str = "",
    pricing: dict | None = None,
    notes: list[str] | None = None,
    availability: str = "",
    flags: list[str] | None = None,
    high_prediction: str = "",
    not_before: bool = False,
) -> None:
    row = {
        "id": event_id,
        "sport": sport,
        "competition": competition,
        "home": home,
        "away": away,
        "start_utc": start_utc,
        "start_display": start_display,
        "not_before": not_before,
        "venue": venue,
        "official_source": official,
        "evidence_sources": evidence,
        "pricing": pricing,
        "notes": notes or [],
        "availability": availability,
        "flags": flags or [],
        "high_prediction": high_prediction,
    }
    if not pricing and not row["flags"]:
        raise ValueError(f"Unpriced row requires a review reason: {event_id}")
    events.append(row)


def record(gp: int, wins: int, gf: float | None = None, ga: float | None = None, **extra) -> dict:
    return {"gp": gp, "wins": wins, "gf": gf, "ga": ga, **extra}


# Discovery and official evidence. OLBG is used for inventory/market location only,
# never as an input to an originated probability.
source("OLBG_ROBOTS", "OLBG", "https://www.olbg.com/robots.txt", "Discovery access rules")
source("OLBG_SITEMAP", "OLBG", "https://www.olbg.com/sitemap.xml", "Canonical hub discovery")
source("NHL_SCHEDULE", "NHL", "https://api-web.nhle.com/v1/schedule/2026-10-24", "Twelve game IDs, UTC starts and scheduled states")
source("NHL_STANDINGS", "NHL", "https://api-web.nhle.com/v1/standings/2026-10-24", "Records and goals at 2026-10-24T17:06:30Z")
source("NHL_LINEUPS", "NHL", "https://www.nhl.com/news/nhl-lineup-projections-2026-27-season", "Projected lineups, starters, scratches and injuries for 24 October")
source("NHL_ONTAP", "NHL", "https://www.nhl.com/news/nhl-on-tap-devils-host-kings-seek-huge-boost-after-trading-for-hellebuyck", "24 October schedule and current form notes")
source("NHL_EDM", "Edmonton Oilers / NHL", "https://www.nhl.com/oilers/news/pre-game-report-oilers-vs-maple-leafs", "Edmonton form, Jarry start, Ekholm and Levi availability")
source("NHL_TOR", "Toronto Maple Leafs / NHL", "https://www.nhl.com/mapleleafs/news/game-day-oilers-oct-24-2026", "Toronto-Edmonton records and recent head-to-head history")
source("NHL_TOR_RECAP", "Toronto Maple Leafs / NHL", "https://www.nhl.com/mapleleafs/news/recap-leafs-vs-rangers-oct-22-2026", "Toronto 5-4 win and three-game streak")
source("NHL_STATUS", "NHL", "https://www.nhl.com/news/nhl-status-report-news-and-notes-october-23-2026", "Toronto week-to-week injuries and Tavares travel status")
source("NHL_TOR_EDM_LINEUPS", "NHL", "https://www.nhl.com/news/toronto-maple-leafs-edmonton-oilers-game-preview-october-24-2026", "Toronto at Edmonton projected lineups and injury lists")
source("NHL_SEA_FORM", "Seattle Kraken / NHL", "https://www.nhl.com/kraken/news/postgame-instant-analysis-utah-mammoth-seattle-kraken-102226", "Seattle seven wins, 15 points and 42 goals through eleven games")
source("NHL_SEA_PREVIEW", "Seattle Kraken / NHL", "https://www.nhl.com/kraken/news/minnesota-wild-vs-seattle-kraken-game-preview-projected-lines-102426", "Minnesota at Seattle records and current form")
source("NBA_INJURIES", "NBA", "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-24_01_00PM.pdf", "24 October fixtures, ET starts and 13:00 ET availability report")
source("NBA_STATS", "NBA", "https://www.nba.com/stats/teams/traditional?Season=2026-27", "2026-27 team records, points and plus/minus; one- or two-game samples")
source("LEGA_ROUND1", "Lega Volley", "https://www.legavolley.it/2026/1a-giornata-and-18-10-2026-regular-season-superlega-stagione-2026-risultati-classifica/", "All six opening results, set records and 25 October fixtures")
source("LNR_TOULON", "LNR / Top 14", "https://top14.lnr.fr/club/toulon", "Toulon 2-0-4, 130:130 and Pau fixture")
source("LNR_PAU", "LNR / Top 14", "https://top14.lnr.fr/club/pau", "Pau 5-0-1, 239:181 and 24 October 21:00 fixture")
source("LNR_ROCHELLE", "LNR / Top 14", "https://top14.lnr.fr/club/la-rochelle", "La Rochelle 4-0-2, 144:135 and Bordeaux fixture")
source("LNR_BORDEAUX", "LNR / Top 14", "https://top14.lnr.fr/club/bordeaux-begles", "Bordeaux 4-0-2, 215:151 and 25 October 21:05 fixture")
source("URC_FIXTURE", "United Rugby Championship", "https://www.unitedrugby.com/latest/news/adjustments-to-2026-27-bkt-united-rugby-championship-fixture-broadcast-for-rounds-2-4-6-15/", "Ospreys-Dragons moved to 19:00 UK")
source("URC_TEAMS", "United Rugby Championship", "https://www.unitedrugby.com/latest/news/round-4-team-announcements/", "Ospreys and Dragons named lineups")
source("URC_TABLE", "United Rugby Championship", "https://stats.unitedrugby.com/match-centre/table/", "Ospreys 1-0-2, 81:107; Dragons 1-1-1, 88:83")
source("PCB_RESULTS", "Pakistan Cricket Board", "https://www.pcb.com.pk/news-detail/sri-lanka-seal-second-highest-chase-in-odi-history-as-brook-s-record-double-ton-goes-in-vain.html", "Tri-series results and 25 October 13:00 PKT start")
source("PCB_PAK_ENG", "Pakistan Cricket Board", "https://www.pcb.com.pk/news-detail/arafat-minhas-6-40-and-59-sink-england-as-pakistan-win-consecutive-games-in-odi-tri-series.html", "Pakistan 302/9 beat England 215 by 87 runs; Arafat Minhas 59 and 6-40")
source("BCCI_SECOND", "BCCI", "https://www.bcci.tv/matches/88d47fe3-ead4-4b91-b0cc-4bda908fb8d7/india-women-vs-zimbabwe-women", "Second ODI at 2026-10-25T08:30:00Z")
source("BCCI_FIRST", "BCCI", "https://www.bcci.tv/matches/023cf7d3-6571-4932-997b-cac801ed0b4a/india-women-vs-zimbabwe-women", "First ODI: Zimbabwe 197; India 200/1 in 27.1 overs, nine-wicket win")
source("BCCI_AVAILABILITY", "BCCI", "https://www.bcci.tv/news/article/jintimani-kalita-replaces-renuka-singh-thakur-in-indias-odi-squad", "Jintimani Kalita replaces Renuka Singh Thakur in India ODI squad")
source("WST_MATCH", "World Snooker Tour", "https://www.wst.tv/match-centre/e6719e69-c712-476e-8081-8e30790868f5", "Williams-Jones listed without a score; localized clock differs from indexed view")
source("WST_WILLIAMS", "World Snooker Tour", "https://www.wst.tv/players/6aaddcbb-345c-474a-9069-e7757e155729", "Williams 14 wins in 20 matches this season")
source("WST_JONES", "World Snooker Tour", "https://www.wst.tv/players/036bc430-6c51-4d63-a366-a6ca218f7f39", "Jones 19 wins in 27 matches this season")
source("WST_WILLIAMS_QF", "World Snooker Tour", "https://www.wst.tv/news/2026/october/23/Vintage-Williams-Beats-Gilbert-With-Ton-Trio", "Williams recovered from 4-2 down to beat Gilbert 6-4 with three straight centuries")
source("MLB_SCHEDULE", "MLB", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&teamId=158", "World Series Game 2 ID 849802 at 2026-10-25T00:00:00Z")
source("MLB_STANDINGS", "MLB", "https://www.mlb.com/standings/2026", "Milwaukee 103-59, 832:618; Tampa Bay 98-64, 736:650 and venue splits")
source("MLB_GAME2", "MLB", "https://www.mlb.com/news/rays-brewers-world-series-game-2-starting-lineups-and-pitching-matchup", "Rasmussen-Henderson pitching matchup and current starter records")
source("MLB_GAME1", "MLB", "https://www.mlb.com/gameday/849805/final/box", "Milwaukee won Game 1, 3-2")
source("WTA_NINGBO_OP", "WTA", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf", "Sunday final not before 17:00 Ningbo time")
source("WTA_NINGBO_REPORT", "WTA", "https://www.wtatennis.com/news/4598225/rybakina-survives-shnaider-test-sets-up-ningbo-final-with-fernandez", "Rybakina and Fernandez semifinal results and 3-2 head-to-head")
source("WTA_NINGBO_PREVIEW", "WTA", "https://www.wtatennis.com/news/4598107/elena-rybakina-vs-leylah-fernandez-everything-to-know-about-the-ningbo-final", "Current form; contains a contradictory Saturday date that is flagged")
source("WTA_RYBAKINA", "WTA", "https://www.wtatennis.com/players/324166/elena-rybakina", "Rybakina No. 1 and 49-14 profile record")
source("WTA_FERNANDEZ", "WTA", "https://www.wtatennis.com/players/326735/leylah-fernandez", "Fernandez No. 30 and 24-25 profile record")
source("WTA_OSAKA_OP", "WTA", "https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf", "Krueger-Siniakova Sunday final at 13:30 Osaka time")

source("ATP_ALMATY_SCHEDULE", "ATP Tour", "https://www.atptour.com/en/news/almaty-atp-250-2026-history-draw-schedule", "Sunday singles final not before 15:00 Almaty time")
source("ATP_ALMATY_REPORT", "ATP Tour", "https://www.atptour.com/en/news/medvedev-bublik-almaty-2026-saturday", "Medvedev-Basilashvili final, current form and 1-0 head-to-head")
source("ATP_MEDVEDEV", "ATP Tour", "https://www.atptour.com/en/players/daniil-medvedev/mm58/overview", "Medvedev profile 45-18")
source("ATP_BASILASHVILI", "ATP Tour", "https://www.atptour.com/en/players/nikoloz-basilashvili/bg23/overview", "Basilashvili profile 7-10")
source("F1_USA", "Formula 1", "https://www.formula1.com/en/racing/2026/united-states", "United States GP at 2026-10-25T20:00:00Z and practice-two results")
source("EHF_STANDINGS", "European Handball Federation", "https://ehfcl.eurohandball.com/men/2026-27/standings/", "Magdeburg 5-0-0, 176:140; Kriens-Luzern 2-0-3, 158:161")
source("EHF_MAGDEBURG", "European Handball Federation", "https://www.eurohandball.com/en/club/zKttAiKCyYIIy_T_l4gBLQ/sc-magdeburg/", "Magdeburg-Kriens on 28 October at 20:45 in Magdeburg")
source("LNH_HOME", "Ligue Nationale de Handball", "https://www.lnh.fr/daikin-starligue/accueil", "Saint-Raphaël-Paris on 25 October at 16:00; Paris 14 points from seven")
source("GALWAY_CHANGE", "Galway GAA", "https://www.galwaygaa.ie/changes-weekend-football-fixture-schedule/", "Weather-revised senior and intermediate finals on Sunday")
source("GBGB_SCURRY", "Greyhound Board of Great Britain", "https://www.gbgb.org.uk/shadow-storm-chases-scurry-gold-cup-history-at-dunstall-park/", "Scurry Gold Cup final and semifinal evidence; complete official runner card not captured")
source("GBGB_OAKS", "Greyhound Board of Great Britain", "https://www.gbgb.org.uk/signet-nayla-chases-oaks-glory-as-hutton-targets-dunstall-park-double/", "Oaks final and semifinal evidence; complete official runner card not captured")
source("PDC_DAY3", "Professional Darts Corporation", "https://www.pdc.tv/tournaments/machineseeker-european-championship", "Official tournament/session evidence; proposed Price-Bunting pairing not confirmed")

SPORTS = [
    ("golf", "Golf", ["https://www.olbg.com/tips/Golf/6"], "No tips were displayed; event and outright pages are the pick locations when offered."),
    ("volleyball", "Volleyball", ["https://www.olbg.com/tips/Volleyball/21"], "Hub cards expose the leading selection; event pages are the location for match, set handicap and total-set markets."),
    ("rugby-union", "Rugby Union", ["https://www.olbg.com/tips/Rugby_Union/9"], "Hub cards expose the leading selection; event pages contain winner, handicap and total-point discussion."),
    ("cricket", "Cricket", ["https://www.olbg.com/tips/Cricket/7"], "Match selections sit beneath fixtures; event pages contain additional match and player-market comments where offered."),
    ("snooker", "Snooker", ["https://www.olbg.com/tips/Snooker/8"], "The hub shows the leading match selection; event pages carry frame and handicap discussion where offered."),
    ("darts", "Darts", ["https://www.olbg.com/tips/Darts/15"], "The hub shows match selections; event pages carry leg and handicap discussion where offered."),
    ("baseball", "Baseball", ["https://www.olbg.com/tips/Baseball/12"], "The hub shows the moneyline selection; event pages are the run-line and total-runs discussion locations."),
    ("gaelic-sports", "Gaelic Sports", ["https://www.olbg.com/tips/Gaelic_Football/25", "https://www.olbg.com/tips/Hurling/26"], "Football and Hurling have separate OLBG routes but one requested desk; fixture cards link to match comments."),
    ("greyhounds", "Greyhounds", ["https://www.olbg.com/tips/Greyhounds/28"], "Race cards and runner-level comments are the pick locations; a complete official runner card is required before pricing."),
    ("tennis", "Tennis", ["https://www.olbg.com/tips/Tennis/3"], "The hub shows match-winner selections; event pages contain set and game-market discussion where offered."),
    ("motor-racing", "Motor Racing", ["https://www.olbg.com/tips/Motor_Racing/14"], "Outright selections sit on the hub and event pages; this desk does not treat practice order as a race-price input."),
    ("handball", "Handball", ["https://www.olbg.com/tips/Handball/20"], "Fixture cards link to winner, handicap and total-goal discussion where offered."),
    ("ice-hockey", "Ice Hockey", ["https://www.olbg.com/tips/Ice_Hockey/13"], "The underscore route is canonical; hub cards lead to moneyline, puck-line and total-goal discussion."),
    ("basketball", "Basketball", ["https://www.olbg.com/tips/Basketball/4"], "The hub shows leading selections; event pages contain moneyline, spread and total-point discussion."),
    ("rugby-league", "Rugby League", ["https://www.olbg.com/tips/Rugby_League/10"], "Only 2027 outrights were captured; no upcoming match-winner inventory was available."),
]

# NHL: total games played includes overtime losses; this matches the league's winPctg basis.
nhl_games = [
    ("2026020168", "Philadelphia Flyers", "Anaheim Ducks", "PHI", "ANA", "2026-10-24T17:00:00Z", record(12, 3, 20, 37), record(10, 4, 27, 33)),
    ("2026020169", "New Jersey Devils", "Los Angeles Kings", "NJD", "LAK", "2026-10-24T19:30:00Z", record(10, 6, 33, 31), record(8, 2, 20, 29)),
    ("2026020170", "Boston Bruins", "San Jose Sharks", "BOS", "SJS", "2026-10-24T23:00:00Z", record(11, 8, 42, 22), record(11, 6, 33, 37)),
    ("2026020171", "Ottawa Senators", "New York Rangers", "OTT", "NYR", "2026-10-24T23:00:00Z", record(11, 7, 31, 30), record(12, 7, 37, 29)),
    ("2026020172", "Pittsburgh Penguins", "Nashville Predators", "PIT", "NSH", "2026-10-24T23:00:00Z", record(11, 4, 37, 38), record(9, 3, 23, 30)),
    ("2026020173", "Washington Capitals", "Buffalo Sabres", "WSH", "BUF", "2026-10-24T23:00:00Z", record(9, 5, 30, 29), record(10, 4, 28, 37)),
    ("2026020174", "Columbus Blue Jackets", "Vegas Golden Knights", "CBJ", "VGK", "2026-10-24T23:00:00Z", record(8, 3, 20, 29), record(12, 8, 46, 36)),
    ("2026020175", "St. Louis Blues", "Carolina Hurricanes", "STL", "CAR", "2026-10-24T23:00:00Z", record(10, 5, 35, 31), record(12, 8, 47, 33)),
    ("2026020176", "Edmonton Oilers", "Toronto Maple Leafs", "EDM", "TOR", "2026-10-24T23:00:00Z", record(10, 8, 47, 32), record(12, 6, 43, 39)),
    ("2026020177", "Utah Mammoth", "Tampa Bay Lightning", "UTA", "TBL", "2026-10-25T01:00:00Z", record(11, 7, 41, 36), record(10, 7, 34, 29)),
    ("2026020178", "Calgary Flames", "Detroit Red Wings", "CGY", "DET", "2026-10-25T02:00:00Z", record(9, 3, 19, 38), record(10, 4, 28, 30)),
    ("2026020179", "Seattle Kraken", "Minnesota Wild", "SEA", "MIN", "2026-10-25T02:00:00Z", record(11, 7, 42, None), record(11, 6, 32, 27)),
]
nhl_record_labels = {
    "ANA": "4-6-0", "PHI": "3-6-3", "LAK": "2-4-2", "NJD": "6-4-0",
    "SJS": "6-4-1", "BOS": "8-2-1", "NYR": "7-4-1", "OTT": "7-4-0",
    "NSH": "3-3-3", "PIT": "4-6-1", "BUF": "4-4-2", "WSH": "5-4-0",
    "VGK": "8-4-0", "CBJ": "3-5-0", "CAR": "8-2-2", "STL": "5-4-1",
    "TOR": "6-4-2", "EDM": "8-1-1", "TBL": "7-3-0", "UTA": "7-4-0",
    "DET": "4-3-3", "CGY": "3-6-0", "MIN": "6-3-2", "SEA": "7-3-1",
}
for gid, home, away, hc, ac, start, hr, ar in nhl_games:
    eid = f"nhl-{gid}"
    notes = [f"Official W-L-OTL records: {hc} {nhl_record_labels[hc]} and {ac} {nhl_record_labels[ac]}. Pricing uses games played and wins on the NHL win-percentage basis."]
    flags = []
    prediction = ""
    availability = "Official projected lineups and injury lists are linked for this fixture."
    evidence = ["NHL_SCHEDULE", "NHL_STANDINGS", "NHL_LINEUPS"]
    official = "NHL_SCHEDULE"
    if hr["ga"] is None or ar["ga"] is None:
        flags.append("Seattle goals against was not present in the captured standings fragment; total and handicap screens remain blank.")
        evidence += ["NHL_SEA_FORM", "NHL_SEA_PREVIEW"]
    if gid == "2026020169":
        notes += ["New Jersey is 4-1-0 in its last five; Los Angeles has two straight wins after an 0-4-2 start.", "New Jersey home scoring is 26:17; Los Angeles road scoring is 17:19."]
        availability = "New Jersey lists no injuries. Los Angeles lists Kevin Fiala and Alex Turcotte injured; Quinton Byfield is questionable. Jake Allen is projected for New Jersey."
        prediction = "New Jersey Devils to win is the selection. The Devils are 6-4-0 with 33 goals and have won four of their last five, while Los Angeles is 2-4-2 with 20 goals despite consecutive wins. New Jersey’s 26-17 home scoring record strengthens the case, although Quinton Byfield is questionable for the Kings. Kevin Fiala and Alex Turcotte are injured for Los Angeles; New Jersey lists no injuries, with Jake Allen projected in goal."
        evidence.append("NHL_ONTAP")
    if gid == "2026020176":
        notes += ["Edmonton and Toronto each bring a three-game winning streak; Toronto is 4-1-0 across the last five head-to-head meetings.", "Edmonton has 47 goals in ten games; Toronto has 43 scored and 39 conceded in twelve."]
        availability = "Toronto lists John Tavares, Chris Tanev, Nick Blankenburg and Marshall Rifai out. Edmonton lists Mattias Ekholm and Devon Levi unavailable; Tristan Jarry is projected to start."
        prediction = "Edmonton Oilers to win is the selection. Edmonton is 8-1-1 with 47 goals in ten games and three consecutive wins; Toronto is 6-4-2 with 43 scored and 39 conceded, also on a three-game streak. Toronto’s 4-1-0 record across the last five meetings is the warning. John Tavares, Chris Tanev, Nick Blankenburg and Marshall Rifai are out for the visitors, while Mattias Ekholm and Devon Levi are unavailable for Edmonton and Tristan Jarry is projected to start."
        evidence += ["NHL_ONTAP", "NHL_EDM", "NHL_TOR", "NHL_TOR_RECAP", "NHL_STATUS", "NHL_TOR_EDM_LINEUPS"]
        official = "NHL_TOR_EDM_LINEUPS"
    event(eid, "ice-hockey", "NHL", home, away, start, start.replace("T", " ").replace("Z", " UTC"), official, evidence,
          pricing={"kind": "log5", "home": hr, "away": ar, "handicap": 1.5}, notes=notes,
          availability=availability, flags=flags, high_prediction=prediction)

# NBA injury report supplies the eight captured OLBG fixtures and official ET starts.
nba_games = [
    ("mia-cha", "Charlotte Hornets", "Miami Heat", "2026-10-24T22:00:00Z", record(2, 1, 95.5, 115.5), record(2, 0, 108.5, 129.5), "Miami: Pelle Larsson probable. Charlotte: Kylan Boswell, Kon Knueppel, Coby White and Grant Williams out; Christian Anderson probable."),
    ("bkn-cle", "Cleveland Cavaliers", "Brooklyn Nets", "2026-10-24T23:30:00Z", record(1, 0, 106.0, 114.0), record(1, 0, 103.0, 110.0), "Brooklyn: Tyler Bilodeau out. Cleveland: Khalifa Diop, Nae'Qwan Tomlin and Ernest Udeh Jr. out; Dean Wade questionable."),
    ("mil-phi", "Philadelphia 76ers", "Milwaukee Bucks", "2026-10-24T23:30:00Z", record(2, 2, 110.0, 103.0), record(2, 0, 120.5, 130.0), "Milwaukee had not submitted at 13:00 ET. Philadelphia lists Dominick Barlow, Tacko Fall, Ariel Hukporti and LeBron James out."),
    ("sas-dal", "Dallas Mavericks", "San Antonio Spurs", "2026-10-25T00:00:00Z", record(2, 1, 115.5, 116.5), record(2, 0, 107.0, 115.0), "Both teams were marked NOT YET SUBMITTED in the 13:00 ET report."),
    ("was-chi", "Chicago Bulls", "Washington Wizards", "2026-10-25T00:00:00Z", record(2, 1, 112.0, 130.0), record(2, 1, 115.0, 114.0), "Washington had not submitted. Chicago lists Nic Claxton out and Noa Essengue probable."),
    ("hou-atl", "Atlanta Hawks", "Houston Rockets", "2026-10-25T00:30:00Z", record(2, 2, 130.0, 103.0), record(2, 2, 121.0, 110.0), "Houston: Steven Adams and Fred VanVleet out; Reed Sheppard questionable. Atlanta: Mouhamed Gueye and Henri Veesaar out, with three two-way players questionable."),
    ("nop-den", "Denver Nuggets", "New Orleans Pelicans", "2026-10-25T01:00:00Z", record(1, 0, 84.0, 96.0), record(2, 0, 119.5, 121.5), "New Orleans had not submitted. Denver lists Cameron Johnson, Spencer Jones and Julian Strawther out; Alpha Diallo questionable."),
    ("gsw-phx", "Phoenix Suns", "Golden State Warriors", "2026-10-25T02:00:00Z", record(1, 0, 83.0, 124.0), record(2, 0, 106.5, 119.0), "Golden State had not submitted. Phoenix lists Mark Williams out, Oso Ighodaro doubtful and Luke Kennard questionable."),
]
for slug, home, away, start, hr, ar, availability in nba_games:
    event(f"nba-{slug}-20261024", "basketball", "NBA", home, away, start, start.replace("T", " ").replace("Z", " UTC"),
          "NBA_INJURIES", ["NBA_INJURIES", "NBA_STATS"],
          pricing={"kind": "log5", "home": hr, "away": ar, "handicap": 4.5},
          notes=["NBA scoring samples contain only one or two games per team; prices are exploratory and cannot be High."],
          availability=availability,
          flags=["One- or two-game scoring sample and incomplete submissions in the official 13:00 ET injury report cap confidence at Low."])

# SuperLega: match records drive the winner screen; set records drive derivative screens only.
volley = [
    ("perugia-pordenone", "Sir Susa Scai Perugia", "Pallavolo Pordenone", "2026-10-25T17:00:00Z", record(1, 1, **{"sets_won": 3, "sets_lost": 2}), record(1, 1, **{"sets_won": 3, "sets_lost": 1})),
    ("trentino-cisterna", "Itas Trentino", "Cisterna Volley", "2026-10-25T16:00:00Z", record(1, 1, **{"sets_won": 3, "sets_lost": 0}), record(1, 1, **{"sets_won": 3, "sets_lost": 0})),
    ("piacenza-modena", "Gas Sales Bluenergy Piacenza", "Modena Volley", "2026-10-25T17:00:00Z", record(1, 1, **{"sets_won": 3, "sets_lost": 0}), record(1, 0, **{"sets_won": 0, "sets_lost": 3})),
    ("lube-padova", "Cucine Lube Civitanova", "Sonepar Padova", "2026-10-25T17:00:00Z", record(1, 1, **{"sets_won": 3, "sets_lost": 0}), record(1, 0, **{"sets_won": 0, "sets_lost": 3})),
    ("monza-verona", "Vero Volley Monza", "Rana Verona", "2026-10-25T17:00:00Z", record(1, 0, **{"sets_won": 1, "sets_lost": 3}), record(1, 0, **{"sets_won": 0, "sets_lost": 3})),
    ("milano-cuneo", "Allianz Milano", "Cuneo Volley", "2026-10-25T18:00:00Z", record(1, 0, **{"sets_won": 0, "sets_lost": 3}), record(1, 0, **{"sets_won": 2, "sets_lost": 3})),
]
for slug, home, away, start, hr, ar in volley:
    event(f"volley-{slug}-20261025", "volleyball", "SuperLega", home, away, start, start.replace("T", " ").replace("Z", " UTC"),
          "LEGA_ROUND1", ["LEGA_ROUND1"], pricing={"kind": "volleyball", "home": hr, "away": ar},
          notes=["Every team has played one match. Match records set the winner price; opening set records inform the set handicap and total only."],
          flags=["One-match samples cap every selection at Low; no availability adjustment is applied."])

# Rugby union scoring screens retain a draw outcome.
event("rugby-toulon-pau-20261024", "rugby-union", "Top 14", "RC Toulon", "Section Paloise", "2026-10-24T19:00:00Z", "24 Oct 21:00 Europe/Paris",
      "LNR_PAU", ["LNR_TOULON", "LNR_PAU"], venue="Toulon",
      pricing={"kind": "score3", "home": record(6, 2, 130, 130), "away": record(6, 5, 239, 181), "handicap": 1.5},
      notes=["Toulon is 2-0-4 with 130:130; Pau is 5-0-1 with 239:181 and beat Castres 35-26 in its last match."],
      flags=["Independent scoring approximation; no home, lineup or injury adjustment and no High eligibility."])
event("rugby-ospreys-dragons-20261024", "rugby-union", "United Rugby Championship", "Ospreys", "Dragons RFC", "2026-10-24T18:00:00Z", "24 Oct 19:00 UK",
      "URC_FIXTURE", ["URC_FIXTURE", "URC_TEAMS", "URC_TABLE"], venue="St Helen's, Swansea",
      pricing={"kind": "score3", "home": record(3, 1, 81, 107), "away": record(3, 1, 88, 83), "handicap": 1.5},
      notes=["Ospreys are 1-0-2 with 81:107; Dragons are 1-1-1 with 88:83. Both starting XVs are officially announced."],
      availability="Official Round 4 team announcements supply both starting XVs and replacements.",
      flags=["Three-game samples and an independent scoring approximation cap confidence at Low."])
event("rugby-rochelle-bordeaux-20261025", "rugby-union", "Top 14", "Stade Rochelais", "Union Bordeaux-Bègles", "2026-10-25T20:05:00Z", "25 Oct 21:05 Europe/Paris",
      "LNR_BORDEAUX", ["LNR_ROCHELLE", "LNR_BORDEAUX"], venue="La Rochelle",
      pricing={"kind": "score3", "home": record(6, 4, 144, 135), "away": record(6, 4, 215, 151), "handicap": 1.5},
      notes=["La Rochelle is 4-0-2 with 144:135; Bordeaux is 4-0-2 with 215:151 and won 23-22 at Clermont in its last match."],
      flags=["Independent scoring approximation; no home, lineup or injury adjustment and no High eligibility."])

# Cricket uses only the current, like-for-like series records; derivatives are deliberately blank.
event("cricket-pakistan-england-20261025", "cricket", "ODI tri-series — match 4", "Pakistan", "England", "2026-10-25T08:00:00Z", "25 Oct 13:00 PKT",
      "PCB_RESULTS", ["PCB_RESULTS", "PCB_PAK_ENG"], venue="Gaddafi Stadium, Lahore",
      pricing={"kind": "log5", "home": record(2, 2), "away": record(2, 0)},
      notes=["Pakistan is 2-0 after beating Sri Lanka by 37 runs and England by 87 runs. England is 0-2 after also losing a record chase to Sri Lanka.", "In the previous meeting Pakistan scored 302/9 and England 215; Arafat Minhas contributed 59 and 6-40."],
      flags=["Two-match series samples cap confidence at Low. Tie/no-result, run handicap and total runs are not separately priced."])
event("cricket-india-zimbabwe-women-20261025", "cricket", "Women's ODI series — match 2", "India Women", "Zimbabwe Women", "2026-10-25T08:30:00Z", "25 Oct 08:30 UTC",
      "BCCI_SECOND", ["BCCI_SECOND", "BCCI_FIRST", "BCCI_AVAILABILITY"], venue="BCA Stadium, Vadodara",
      pricing={"kind": "log5", "home": record(1, 1), "away": record(1, 0)},
      notes=["India won the first ODI by nine wickets: Zimbabwe 197 in 49.5 overs, India 200/1 in 27.1. Pratika Rawal made 100 not out and Shafali Verma 64 not out.", "Jintimani Kalita replaces Renuka Singh Thakur, who is building bowling volume at the BCCI Centre of Excellence."],
      availability="BCCI announced Jintimani Kalita as Renuka Singh Thakur’s replacement for this ODI series.",
      flags=["One-match ODI sample caps confidence at Low. Tie/no-result, run handicap and total runs are not separately priced."])

# Snooker remains priced but the unconfirmed clock is blank and prominent.
event("snooker-williams-jones-20261024", "snooker", "Northern Ireland Open — semifinal", "Mark Williams", "Jak Jones", None, "24 Oct; WST indexed/localized clocks differ",
      "WST_MATCH", ["WST_MATCH", "WST_WILLIAMS", "WST_JONES", "WST_WILLIAMS_QF"], venue="Belfast, Northern Ireland",
      pricing={"kind": "log5", "home": record(20, 14), "away": record(27, 19)},
      notes=["Williams has 14 wins in 20 season matches; Jones has 19 in 27. Williams recovered from 4-2 down to beat David Gilbert 6-4 with three consecutive centuries."],
      flags=["UTC start is blank because WST indexed and localized pages show different clocks. Refresh match state before any kickoff-time use.", "Frame handicap and total frames are not priced without an official match-format and frame-distribution input."])

# Baseball: three transparent winner components; starter context is not folded into the formula.
event("baseball-rays-brewers-849802", "baseball", "World Series — Game 2", "Milwaukee Brewers", "Tampa Bay Rays", "2026-10-25T00:00:00Z", "24 Oct 20:00 ET / 2026-10-25T00:00:00Z",
      "MLB_SCHEDULE", ["MLB_SCHEDULE", "MLB_STANDINGS", "MLB_GAME2", "MLB_GAME1"], venue="American Family Field",
      pricing={"kind": "baseball", "home": record(162, 103, 832, 618, home_gp=81, home_wins=55), "away": record(162, 98, 736, 650, away_gp=81, away_wins=43), "handicap": 1.5},
      notes=["Milwaukee leads the Series 1-0 after a 3-2 win. Regular season: Milwaukee 103-59 with 832:618; Tampa Bay 98-64 with 736:650.", "Drew Rasmussen faces Logan Henderson. Tampa Bay is 14-1 in Rasmussen’s 15 starts since the All-Star break; Milwaukee is 21-4 in Henderson’s 25 career starts."],
      availability="Official Game 2 FAQ names Drew Rasmussen and Logan Henderson as starting pitchers.",
      flags=["The winner price averages overall record, Pythagorean and venue-split components equally; starter records are context, not a hidden adjustment."])

# Tennis: two supportable season-record screens and one deliberately unpriced final.
event("tennis-rybakina-fernandez-20261025", "tennis", "WTA Ningbo — final", "Elena Rybakina", "Leylah Fernandez", "2026-10-25T09:00:00Z", "25 Oct not before 17:00 Asia/Shanghai",
      "WTA_NINGBO_OP", ["WTA_NINGBO_OP", "WTA_NINGBO_REPORT", "WTA_NINGBO_PREVIEW", "WTA_RYBAKINA", "WTA_FERNANDEZ"],
      pricing={"kind": "log5", "home": record(63, 49), "away": record(49, 24)},
      notes=["Rybakina is No. 1 with a 49-14 profile record; Fernandez is No. 30 at 24-25. Rybakina leads their head-to-head 3-2 and has won the last two.", "Both won their semifinals 6-3, 7-5. Fernandez is 11-2 since the start of the Asian Swing."],
      flags=["Start is not-before, not guaranteed. A WTA preview says Saturday while the dated official order of play says Sunday; the PDF controls and the contradiction is flagged.", "Set/game handicaps and totals are not priced without comparable current distributions."])
event("tennis-krueger-siniakova-20261025", "tennis", "WTA Osaka — final", "Ashlyn Krueger", "Katerina Siniakova", "2026-10-25T04:30:00Z", "25 Oct 13:30 Asia/Tokyo",
      "WTA_OSAKA_OP", ["WTA_OSAKA_OP"],
      flags=["Comparable current singles W-L records for both finalists were not captured from official evidence; winner, handicap and total remain blank."])
event("tennis-medvedev-basilashvili-20261025", "tennis", "ATP Almaty — final", "Daniil Medvedev", "Nikoloz Basilashvili", "2026-10-25T10:00:00Z", "25 Oct not before 15:00 Asia/Almaty",
      "ATP_ALMATY_SCHEDULE", ["ATP_ALMATY_SCHEDULE", "ATP_ALMATY_REPORT", "ATP_MEDVEDEV", "ATP_BASILASHVILI"],
      pricing={"kind": "log5", "home": record(63, 45), "away": record(17, 7)},
      notes=["Profiles display Medvedev 45-18 and Basilashvili 7-10; current Almaty wins are reported separately rather than silently added to those records.", "Medvedev has a Tour-leading 37 hard-court wins and is 10-1 in Almaty. Basilashvili beat Tsitsipas 6-4, 6-7(5), 6-3; Medvedev leads their head-to-head 1-0."],
      flags=["Start is not-before, not guaranteed. Profile records may lag current-tournament results, so confidence is capped below High.", "Set/game handicaps and totals are not priced without comparable current distributions."])

# Event-level official fixtures with insufficient comparable inputs.
event("motor-usa-gp-20261025", "motor-racing", "Formula 1 — United States Grand Prix", "Circuit of the Americas", "2026 driver field", "2026-10-25T20:00:00Z", "2026-10-25T20:00:00Z",
      "F1_USA", ["F1_USA"], venue="Austin, Texas",
      notes=["Practice two was led by Charles Leclerc from Kimi Antonelli and Max Verstappen; qualifying had not been completed in the captured evidence."],
      flags=["No race-winner price: qualifying and a complete comparable current driver dataset were not captured. Practice order is not substituted for race form."])

event("handball-magdeburg-kriens-20261028", "handball", "EHF Champions League — Group F", "SC Magdeburg", "HC Kriens-Luzern", "2026-10-28T19:45:00Z", "28 Oct 20:45 Europe/Berlin",
      "EHF_MAGDEBURG", ["EHF_MAGDEBURG", "EHF_STANDINGS"], venue="Magdeburg, Germany",
      pricing={"kind": "score3", "home": record(5, 5, 176, 140), "away": record(5, 2, 158, 161), "handicap": 1.5},
      notes=["Magdeburg is 5-0-0 with 176:140; Kriens-Luzern is 2-0-3 with 158:161. Magdeburg won the September away meeting 39-29."],
      flags=["Independent scoring approximation with a draw outcome; no lineup or injury adjustment and no High eligibility."])
event("handball-saint-raphael-paris-20261025", "handball", "Daikin StarLigue — round 8", "Saint-Raphaël", "Paris Saint-Germain", "2026-10-25T15:00:00Z", "25 Oct 16:00 Europe/Paris",
      "LNH_HOME", ["LNH_HOME"],
      notes=["Paris has 14 points from seven matches; Saint-Raphaël has four from six with 176:190 in the captured LNH table."],
      flags=["Paris goals for/against and a complete comparable W-D-L breakdown were not captured; winner, handicap and total remain blank."])

# Gaelic football uses the latest weather notice, not an older fixtures page or OLBG clock.
event("gaelic-moycullen-salthill-20261025", "gaelic-sports", "Galway Senior Football Championship — final", "Maigh Cuilinn / Moycullen", "Salthill-Knocknacarra", "2026-10-25T16:00:00Z", "25 Oct 16:00 Europe/Dublin",
      "GALWAY_CHANGE", ["GALWAY_CHANGE"], venue="Pearse Stadium",
      flags=["Weather moved the senior final to Sunday at 16:00. Comparable current team scoring and availability records were not captured; no price or selection."])
event("gaelic-caherlistrane-spideal-20261025", "gaelic-sports", "Galway Intermediate Football Championship — final", "Caherlistrane", "An Spidéal", "2026-10-25T14:00:00Z", "25 Oct 14:00 Europe/Dublin",
      "GALWAY_CHANGE", ["GALWAY_CHANGE"], venue="Pearse Stadium",
      flags=["The latest weather notice says 14:00; an older fixtures view showed 15:00. The notice controls and the conflict remains visible.", "Comparable current team scoring and availability records were not captured; no price or selection."])

# Greyhound competitions are real, but runner-level fields are not complete enough for selections.
event("greyhounds-scurry-final-20261024", "greyhounds", "Arena Racing Company Scurry Gold Cup — final", "Dunstall Park", "Finalist field", None, "24 Oct; official race time not captured",
      "GBGB_SCURRY", ["GBGB_SCURRY"], venue="Dunstall Park",
      notes=["Official semifinal reports name Shadow Storm, Avarua Lake, Roanna Mamba and other qualifiers."],
      flags=["Complete official final runner card, traps and race time were not captured; no runner selection or price."])
event("greyhounds-oaks-final-20261024", "greyhounds", "Premier Greyhound Racing Oaks — final", "Dunstall Park", "Finalist field", None, "24 Oct; official race time not captured",
      "GBGB_OAKS", ["GBGB_OAKS"], venue="Dunstall Park",
      notes=["Official semifinal reports name Signet Nayla, Fahrenheit Jess and Slingshot Poppy among the qualifiers."],
      flags=["Complete official final runner card, traps and race time were not captured; no runner selection or price."])

REVIEW_LEADS = [
    {"sport": "golf", "item": "No current Golf tips in the captured hub", "reason": "No fixture is invented to fill the requested sport.", "official_source": "OLBG_SITEMAP"},
    {"sport": "darts", "item": "Price–Bunting and other proposed pairings", "reason": "Official session evidence exists, but the pairing was not confirmed; no match row or price.", "official_source": "PDC_DAY3"},
    {"sport": "rugby-league", "item": "2027 outright-only OLBG inventory", "reason": "No upcoming match-winner list was captured; no team or price is inferred from outrights.", "official_source": "OLBG_SITEMAP"},
    {"sport": "rugby-union", "item": "Harlequins–Saracens and other uncorroborated hub leads", "reason": "Searches found historical material rather than a current official fixture; excluded from the match list.", "official_source": "URC_FIXTURE"},
    {"sport": "gaelic-sports", "item": "Dunloy–Portaferry and Shinrone–Kilcormac-Killoughey", "reason": "Official county/Ulster pages did not substantiate the proposed current pairings; excluded rather than guessed.", "official_source": "GALWAY_CHANGE"},
    {"sport": "greyhounds", "item": "Runner-level pricing", "reason": "GBGB event schedules and semifinal stories do not replace a complete official final card.", "official_source": "GBGB_SCURRY"},
]

payload = {
    "desk": "TB2719",
    "date": "2026-10-24",
    "persisted_at": NOW,
    "method_version": "tb2719-v1",
    "scope": [{"slug": slug, "name": name, "olbg_urls": urls, "market_location": location} for slug, name, urls, location in SPORTS],
    "source_registry": sources,
    "events": events,
    "review_leads": REVIEW_LEADS,
    "inventory_note": "OLBG supplied discovery routes and market/pick locations only. Official sources control participants, starts, records and availability. Community support is never treated as probability.",
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "observations.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "sources.json").write_text(json.dumps(sources, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {len(events)} events across {len(SPORTS)} sports with {len(sources)} registered sources at {NOW}")
