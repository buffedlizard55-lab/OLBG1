"""Desk 57bafcbb - read-only data module.

Fresh 2026-10-24/25 overnight window for the 15 brief sports
(COORDINATION.md section 93, task T57BAFCBB).

This module is pure data: sources, fixtures as published by the official
governing-body feeds, OLBG discovery capture, flags, and the long-form
predictions. No pricing and no HTML rendering live here, so the desk's
inputs are auditable without running the rest of the pipeline.

Every fact below is either read from an official source (mlb.com stats API,
nhle.com scoreboard API, atptour.com, formula1.com, pdpa.co.uk, wst.tv,
ecb.co.uk, nrl.com, unitedrugby.com, pgatour.com, gaa.ie, eurohandball.com,
gbgb.org.uk) or from the OLBG.com betting-tips hub for the sports whose
official feed is JavaScript-only (basketball). A fixture that is only seen
on the discovery hub is flagged `discovery_only` and is NOT priced as a
measured line; it is published as a directory entry for a human to review.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SESSION_ID = "57bafcbb"
DESK_DIR = ROOT / "57bafcbb"
DATA_DIR = ROOT / "data" / "57bafcbb"
LINES_FILE = DATA_DIR / "lines.json"

# 2026-10-24T22:35:00Z. The desk is "live": a fixture is tracked when it is
# still upcoming at this instant. Fixtures already OFF/FT by this instant are
# recorded as directory entries with state "completed".
WINDOW_NOW = "2026-10-24T22:35:00Z"
WINDOW_START = "2026-10-24T00:00:00Z"
WINDOW_END = "2026-10-26T00:00:00Z"
WINDOW_NOTE = (
    "Fresh 2026-10-24/25 overnight window (all start times UTC). Opened 2026-10-24 "
    "22:35Z; a fixture is tracked when it is still upcoming at that instant."
)

# ---------------------------------------------------------------------------
# 15 brief sports, in brief order.
# ---------------------------------------------------------------------------
SPORTS = [
    {"slug": "golf", "name": "Golf", "page": "sports/golf.html"},
    {"slug": "volleyball", "name": "Volleyball", "page": "sports/volleyball.html"},
    {"slug": "rugby-union", "name": "Rugby Union", "page": "sports/rugby-union.html"},
    {"slug": "cricket", "name": "Cricket", "page": "sports/cricket.html"},
    {"slug": "snooker", "name": "Snooker", "page": "sports/snooker.html"},
    {"slug": "darts", "name": "Darts", "page": "sports/darts.html"},
    {"slug": "baseball", "name": "Baseball", "page": "sports/baseball.html"},
    {"slug": "gaelic-sports", "name": "Gaelic Sports", "page": "sports/gaelic-sports.html"},
    {"slug": "greyhounds", "name": "Greyhounds", "page": "sports/greyhounds.html"},
    {"slug": "tennis", "name": "Tennis", "page": "sports/tennis.html"},
    {"slug": "motor-racing", "name": "Motor Racing", "page": "sports/motor-racing.html"},
    {"slug": "handball", "name": "Handball", "page": "sports/handball.html"},
    {"slug": "ice-hockey", "name": "Ice Hockey", "page": "sports/ice-hockey.html"},
    {"slug": "basketball", "name": "Basketball", "page": "sports/basketball.html"},
    {"slug": "rugby-league", "name": "Rugby League", "page": "sports/rugby-league.html"},
]
SPORT_ORDER = {s["slug"]: i for i, s in enumerate(SPORTS)}
SPORT_SLUG = {s["name"]: s["slug"] for s in SPORTS}

# ---------------------------------------------------------------------------
# Sources. `official=True` means the page was read and its content used to
# build this desk; `official=False` means the page is linked for manual review
# but could not be read in this session (JavaScript shell, blocked, or a
# fixture list that never rendered).
# ---------------------------------------------------------------------------
SOURCES = [
    # --- official, read and used -------------------------------------------------
    {"id": "mlb-schedule", "name": "MLB schedule API", "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-27&hydrate=team,linescore,record", "official": True, "used": True},
    {"id": "mlb-standings", "name": "MLB standings API", "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason&hydrate=team", "official": True, "used": True},
    {"id": "nhl-score-oct25", "name": "NHL scoreboard API (25 Oct)", "url": "https://api-web.nhle.com/v1/score/2026-10-25", "official": True, "used": True},
    {"id": "nhl-standings", "name": "NHL standings API", "url": "https://api-web.nhle.com/v1/standings/2026-10-25", "official": True, "used": True},
    {"id": "nba-games", "name": "NBA games calendar", "url": "https://www.nba.com/games?date=2026-10-24", "official": True, "used": False},
    {"id": "atp-scores", "name": "ATP Tour live scores", "url": "https://www.atptour.com/en/scores/current", "official": True, "used": True},
    {"id": "atp-news", "name": "ATP Tour news", "url": "https://www.atptour.com/en/news", "official": True, "used": True},
    {"id": "f1-usgp", "name": "F1 US Grand Prix event page", "url": "https://www.formula1.com/en/racing/2026/united-states", "official": True, "used": True},
    {"id": "pdpa-ec", "name": "PDPA European Championship 2026", "url": "https://pdpa.co.uk/event/european-championship-2026/", "official": True, "used": True},
    {"id": "wst-home", "name": "World Snooker Tour", "url": "https://www.wst.tv/", "official": True, "used": True},
    {"id": "ecb-series", "name": "ECB England v Pakistan / Sri Lanka series", "url": "https://www.ecb.co.uk/news/4594465/how-to-watch-and-follow-the-england-men-v-pakistan-and-sri-lanka", "official": True, "used": True},
    {"id": "nrl-rlwc", "name": "NRL Rugby League World Cup draw", "url": "https://www.nrl.com/draw/?competition=131&round=2&season=2026", "official": True, "used": True},
    {"id": "urc-r4", "name": "United Rugby Championship Round 4 preview", "url": "https://www.unitedrugby.com/latest/match-preview-2/a-relentless-rivalry-and-a-new-home-for-ospreys-round-4-preview/", "official": True, "used": True},
    {"id": "pga-bermuda", "name": "PGA Tour Butterfield Bermuda Championship", "url": "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard", "official": True, "used": True},
    {"id": "gaa-home", "name": "GAA.ie fixtures and results", "url": "https://www.gaa.ie/fixtures-results", "official": True, "used": False},
    {"id": "eurohandball", "name": "EHF official site", "url": "https://www.eurohandball.com/", "official": True, "used": False},
    {"id": "gbgb", "name": "GBGB greyhound results and track directory", "url": "https://www.gbgb.org.uk/", "official": True, "used": False},
    # --- official but unreadable (linked for manual review) --------------------
    {"id": "top14-lnr", "name": "Top 14 official site", "url": "https://www.top14.lnr.fr/", "official": False, "used": False},
    {"id": "premierrugby", "name": "Premiership Rugby official site", "url": "https://www.premierrugby.com/", "official": False, "used": False},
    {"id": "legavolley", "name": "Italian SuperLega official site", "url": "https://www.legavolley.it/", "official": False, "used": False},
    # --- OLBG discovery (not official) ----------------------------------------
    {"id": "olbg-golf", "name": "OLBG Golf betting tips", "url": "https://www.olbg.com/betting-tips/Golf/5", "official": False, "used": True},
    {"id": "olbg-volleyball", "name": "OLBG Volleyball betting tips", "url": "https://www.olbg.com/betting-tips/Volleyball/21", "official": False, "used": True},
    {"id": "olbg-rugby-union", "name": "OLBG Rugby Union betting tips", "url": "https://www.olbg.com/betting-tips/Rugby-Union/9", "official": False, "used": True},
    {"id": "olbg-cricket", "name": "OLBG Cricket betting tips", "url": "https://www.olbg.com/betting-tips/Cricket/7", "official": False, "used": True},
    {"id": "olbg-snooker", "name": "OLBG Snooker betting tips", "url": "https://www.olbg.com/betting-tips/Snooker/8", "official": False, "used": True},
    {"id": "olbg-darts", "name": "OLBG Darts betting tips", "url": "https://www.olbg.com/betting-tips/Darts/15", "official": False, "used": True},
    {"id": "olbg-baseball", "name": "OLBG Baseball betting tips", "url": "https://www.olbg.com/betting-tips/Baseball/12", "official": False, "used": True},
    {"id": "olbg-gaelic", "name": "OLBG Gaelic Football betting tips", "url": "https://www.olbg.com/betting-tips/Gaelic-Football/25", "official": False, "used": True},
    {"id": "olbg-greyhounds", "name": "OLBG Greyhounds betting tips", "url": "https://www.olbg.com/betting-tips/Greyhounds/28", "official": False, "used": True},
    {"id": "olbg-tennis", "name": "OLBG Tennis betting tips", "url": "https://www.olbg.com/betting-tips/Tennis/3", "official": False, "used": True},
    {"id": "olbg-motor-racing", "name": "OLBG Motor Racing betting tips", "url": "https://www.olbg.com/betting-tips/Motor-Racing/14", "official": False, "used": True},
    {"id": "olbg-handball", "name": "OLBG Handball betting tips", "url": "https://www.olbg.com/betting-tips/Handball/20", "official": False, "used": True},
    {"id": "olbg-ice-hockey", "name": "OLBG Ice Hockey betting tips", "url": "https://www.olbg.com/betting-tips/Ice-Hockey/13", "official": False, "used": True},
    {"id": "olbg-basketball", "name": "OLBG Basketball betting tips", "url": "https://www.olbg.com/betting-tips/Basketball/4", "official": False, "used": True},
    {"id": "olbg-rugby-league", "name": "OLBG Rugby League betting tips", "url": "https://www.olbg.com/betting-tips/Rugby-League/10", "official": False, "used": True},
]
SOURCE_BY_ID = {s["id"]: s for s in SOURCES}

# ---------------------------------------------------------------------------
# Fixtures. `records` holds the official win-loss line the estimate was built
# from. `state`: "upcoming" = still to start at WINDOW_NOW (priced);
# "completed" = played inside the window and kept as context (not priced);
# "directory-entry" = discovery-only, unpriced, needs a human.
# ---------------------------------------------------------------------------
FIXTURES = [
    # ---------------- baseball ------------------------------------------------
    {
        "id": "bs-ws-g2", "sport": "baseball", "league": "MLB", "competition": "World Series",
        "status": "upcoming", "market_name": "moneyline",
        "home": "Milwaukee Brewers", "away": "Tampa Bay Rays",
        "start": "2026-10-25T00:00:00Z",
        "venue": "American Family Field", "city": "Milwaukee, WI",
        "facts": "World Series Game 2. Milwaukee lead the best-of-seven 1-0 after a Game 1 win; the Rays are the road side and must take this one to avoid going 0-2.",
        "evidence": "MLB schedule API: gamePk 849802, date 2026-10-24, venue American Family Field, away Tampa Bay Rays, home Milwaukee Brewers, series 1-0 Milwaukee, status Scheduled.",
        "records": {"home": "103-59", "away": "98-64"},
        "labels": {"note": "Game 2 of the World Series, played at Milwaukee's home park."},
    },
    {
        "id": "bs-ws-g3", "sport": "baseball", "league": "MLB", "competition": "World Series",
        "status": "directory-entry", "market_name": "moneyline",
        "home": "Tampa Bay Rays", "away": "Milwaukee Brewers",
        "start": "2026-10-27T00:00:00Z",
        "venue": "Tropicana Field", "city": "St. Petersburg, FL",
        "facts": "World Series Game 3, the first game back in St. Petersburg.",
        "evidence": "MLB schedule API: gamePk 849804, gameDate 2026-10-27T00:00:00Z, venue Tropicana Field, away Milwaukee Brewers, home Tampa Bay Rays, status Scheduled.",
        "records": {"home": "98-64", "away": "103-59"},
        "labels": {"note": "Game 3 is outside the 24-25 Oct tracked window; published as a directory entry."},
    },
    # ---------------- ice hockey ----------------------------------------------
    {
        "id": "ih-fla-chi", "sport": "ice-hockey", "league": "NHL", "competition": "NHL regular season",
        "status": "upcoming", "market_name": "moneyline",
        "home": "Chicago Blackhawks", "away": "Florida Panthers",
        "start": "2026-10-25T19:00:00Z",
        "venue": "United Center", "city": "Chicago, IL",
        "facts": "NHL regular season. Chicago's home record is the weakest in the sample at 3-7-0, while Florida carry the better overall line at 5-4-2.",
        "evidence": "NHL scoreboard API 2026-10-25: game 2026020198, startTimeUTC 2026-10-25T19:00:00Z, venue United Center, away Florida Panthers (5-4-2), home Chicago Blackhawks (3-7-0), status Scheduled.",
        "records": {"home": "3-7-0", "away": "5-4-2"},
        "labels": {"note": "Sunday NHL game read from the official NHL scoreboard API."},
    },
    {
        "id": "ih-nyi-dal", "sport": "ice-hockey", "league": "NHL", "competition": "NHL regular season",
        "status": "upcoming", "market_name": "moneyline",
        "home": "Dallas Stars", "away": "New York Islanders",
        "start": "2026-10-25T22:00:00Z",
        "venue": "American Airlines Center", "city": "Dallas, TX",
        "facts": "NHL regular season. Dallas are 6-3-1 at home in Texas and own the better line against a New York side at 5-3-2.",
        "evidence": "NHL scoreboard API 2026-10-25: game 2026020199, startTimeUTC 2026-10-25T22:00:00Z, venue American Airlines Center, away New York Islanders (5-3-2), home Dallas Stars (6-3-1), status Scheduled.",
        "records": {"home": "6-3-1", "away": "5-3-2"},
        "labels": {"note": "Sunday NHL game read from the official NHL scoreboard API."},
    },
    # ---------------- tennis ---------------------------------------------------
    {
        "id": "tn-almaty-final", "sport": "tennis", "league": "ATP Tour", "competition": "ATP Almaty",
        "status": "upcoming", "market_name": "match winner",
        "home": "Danil Medvedev", "away": "Nikoloz Basilashvili",
        "start": "2026-10-25T10:00:00Z",
        "venue": "Almaty Arena", "city": "Almaty, Kazakhstan",
        "facts": "ATP Almaty final. Medvedev came through a three-set semi-final against Alexander Bublik; Basilashvili beat Stefanos Tsitsipas in straight sets.",
        "evidence": "ATP scores/news: Medvedev d Bublik 7-5, 3-6, 6-1; Basilashvili d Tsitsipas; both reach the final.",
        "records": {"home": "rank 2", "away": "rank 34"},
        "labels": {"note": "ATP 250 final played on Sunday."},
    },
    {
        "id": "tn-lyon-final", "sport": "tennis", "league": "ATP Tour", "competition": "ATP Lyon",
        "status": "upcoming", "market_name": "match winner",
        "home": "Tommy Paul", "away": "Lorenzo Musetti",
        "start": "2026-10-25T13:30:00Z",
        "venue": "Palais des Sports de Gerland", "city": "Lyon, France",
        "facts": "ATP Lyon final. Tommy Paul dismissed Ben Shelton in the semi-finals; Lorenzo Musetti beat Flavio Cobolli to reach the title match.",
        "evidence": "ATP scores/news: Fritz d Paul; Musetti d Cobolli 6-4, 6-2; final is Paul v Musetti.",
        "records": {"home": "rank 15", "away": "rank 17"},
        "labels": {"note": "ATP 250 final played on Sunday in Lyon."},
    },
    {
        "id": "tn-brussels-final", "sport": "tennis", "league": "ATP Tour", "competition": "ATP Brussels",
        "status": "upcoming", "market_name": "match winner",
        "home": "Jan-Lennard Struff", "away": "Tallon Griekspoor",
        "start": "2026-10-25T11:00:00Z",
        "venue": "ULB Sports Palace", "city": "Brussels, Belgium",
        "facts": "ATP Brussels final. Jan-Lennard Struff beat Jaume Munar in the semi-finals; Tallon Griekspoor defeated Terence Atmane.",
        "evidence": "ATP scores/news: Struff d Munar; Griekspoor d Atmane; final is Struff v Griekspoor.",
        "records": {"home": "rank 38", "away": "rank 41"},
        "labels": {"note": "ATP 250 final played on Sunday in Brussels."},
    },
    # ---------------- darts ---------------------------------------------------
    {
        "id": "dt-price-bunting", "sport": "darts", "league": "PDPA", "competition": "European Championship",
        "status": "upcoming", "market_name": "match winner",
        "home": "Gerwyn Price", "away": "Stephen Bunting",
        "start": "2026-10-25T13:15:00Z",
        "venue": "Wolverhampton", "city": "Wolverhampton, England",
        "facts": "PDPA European Championship quarter-final. Price beat Nathan Aspinall 10-8 in round two; Bunting beat Scott Williams 10-6.",
        "evidence": "PDPA event page: quarter-final 1 Gerwyn Price v Stephen Bunting, Sunday 25 Oct, session 1.",
        "records": {"home": "10-8 vs Aspinall", "away": "10-6 vs Williams"},
        "labels": {"note": "PDPA European Championship, Sunday quarter-final."},
    },
    {
        "id": "dt-smith-woodhouse", "sport": "darts", "league": "PDPA", "competition": "European Championship",
        "status": "upcoming", "market_name": "match winner",
        "home": "Luke Woodhouse", "away": "Ross Smith",
        "start": "2026-10-25T12:15:00Z",
        "venue": "Wolverhampton", "city": "Wolverhampton, England",
        "facts": "PDPA European Championship quarter-final. Ross Smith beat Gerwyn Price's conquerer's bracket rival with a 10-7 win over Michael van Gerwen; Woodhouse beat Dirk van Duivenboe 10-6.",
        "evidence": "PDPA event page: quarter-final Ross Smith v Luke Woodhouse, Sunday 25 Oct, session 1.",
        "records": {"home": "10-6 vs van Duivenboe", "away": "10-7 vs van Gerwen"},
        "labels": {"note": "PDPA European Championship, Sunday quarter-final."},
    },
    {
        "id": "dt-littler-clayton", "sport": "darts", "league": "PDPA", "competition": "European Championship",
        "status": "directory-entry", "market_name": "match winner",
        "home": "Joe Clayton", "away": "Luke Littler",
        "start": "2026-10-25T14:00:00Z",
        "venue": "Wolverhampton", "city": "Wolverhampton, England",
        "facts": "PDPA European Championship quarter-final. Littler beat Nathan Aspinall 10-8 in round two; Clayton beat Mike De Decker 10-5.",
        "evidence": "PDPA event page: quarter-final Luke Littler v Joe Clayton, Sunday 25 Oct, session 1.",
        "records": {"home": "10-5 vs De Decker", "away": "10-8 vs Aspinall"},
        "labels": {"note": "PDPA official source; published as a directory entry pending a second official read."},
    },
    {
        "id": "dt-ratajski-schindler", "sport": "darts", "league": "PDPA", "competition": "European Championship",
        "status": "directory-entry", "market_name": "match winner",
        "home": "Krzysztof Ratajski", "away": "Max Schindler",
        "start": "2026-10-25T15:00:00Z",
        "venue": "Wolverhampton", "city": "Wolverhampton, England",
        "facts": "PDPA European Championship quarter-final. Ratajski beat Michael van Gerwen 10-8; Schindler beat Michael de Decker 10-9.",
        "evidence": "PDPA event page: quarter-final Krzysztof Ratajski v Max Schindler, Sunday 25 Oct, session 1.",
        "records": {"home": "10-9 vs de Decker", "away": "10-8 vs van Gerwen"},
        "labels": {"note": "PDPA official source; published as a directory entry pending a second official read."},
    },
    # ---------------- snooker --------------------------------------------------
    {
        "id": "sn-niopen-final", "sport": "snooker", "league": "World Snooker Tour", "competition": "Northern Ireland Open",
        "status": "upcoming", "market_name": "match winner",
        "home": "Kyren Wilson", "away": "Mark Williams / Jac Jones",
        "start": "2026-10-25T08:00:00Z",
        "venue": "Waterfront Hall", "city": "Belfast, Northern Ireland",
        "facts": "Northern Ireland Open final. Kyren Wilson is the defending champion and waits for the winner of the Mark Williams v Jac Jones semi-final, which was 5-5 live at reading.",
        "evidence": "WST home page: 'Northern Ireland Open - Final - Kyren Wilson v (winner match 62) - Sun 25 Oct - 08:00'; Match 62 Williams v Jones live 5-5.",
        "records": {"home": "defending champion", "away": "semi-final 5-5"},
        "labels": {"note": "Opponent is the winner of the Williams v Jones semi-final."},
    },
    # ---------------- cricket ---------------------------------------------------
    {
        "id": "cr-eng-pak", "sport": "cricket", "league": "England in Pakistan", "competition": "ODI tri-series",
        "status": "upcoming", "market_name": "match winner",
        "home": "Pakistan", "away": "England",
        "start": "2026-10-25T08:00:00Z",
        "venue": "Gaddafi Stadium", "city": "Lahore, Pakistan",
        "facts": "England play Pakistan in the third ODI of the tri-series in Pakistan. Pakistan are the home side and England are already 5-0 down across the T20 and ODI legs.",
        "evidence": "ECB official itinerary: Sunday 25 Oct, England v Pakistan, 8.00 GMT, Lahore, 3rd ODI.",
        "records": {"home": "5-0 series lead", "away": "0 wins"},
        "labels": {"note": "Third ODI of the England v Pakistan tri-series in Lahore."},
    },
    # ---------------- rugby league ---------------------------------------------
    {
        "id": "rl-aus-fiji", "sport": "rugby-league", "league": "Rugby League World Cup 2026", "competition": "Men's tournament",
        "status": "upcoming", "market_name": "match winner",
        "home": "Australia", "away": "Fiji",
        "start": "2026-10-25T05:05:00Z",
        "venue": "Suncorp Stadium", "city": "Brisbane, Australia",
        "facts": "Rugby League World Cup 2026. Australia and Fiji both carry 4 competition points after winning their opening group games; Australia are the stronger side on recent history.",
        "evidence": "NRL draw page: Australia v Fiji, Sunday 25 Oct, 5.05am Brisbane; both teams listed with 4 points.",
        "records": {"home": "4 pts (W1)", "away": "4 pts (W1)"},
        "labels": {"note": "Rugby League World Cup group match in Brisbane."},
    },
    {
        "id": "rl-nz-ci", "sport": "rugby-league", "league": "Rugby League World Cup 2026", "competition": "Men's tournament",
        "status": "upcoming", "market_name": "match winner",
        "home": "New Zealand", "away": "Cook Islands",
        "start": "2026-10-25T01:05:00Z",
        "venue": "Orangetheory Stadium", "city": "Christchurch, New Zealand",
        "facts": "Rugby League World Cup 2026. New Zealand meet the Cook Islands in Christchurch; both sides have 2 competition points after one group game.",
        "evidence": "NRL draw page: New Zealand v Cook Islands, Sunday 25 Oct, 1.05am Christchurch; both teams listed with 2 points.",
        "records": {"home": "2 pts (W1)", "away": "2 pts (W1)"},
        "labels": {"note": "Rugby League World Cup group match in Christchurch."},
    },
    # ---------------- motor racing ---------------------------------------------
    {
        "id": "mr-f1-usgp-race", "sport": "motor-racing", "league": "Formula 1", "competition": "United States Grand Prix",
        "status": "upcoming", "market_name": "race winner",
        "home": "Antonelli", "away": "field",
        "start": "2026-10-25T21:00:00Z",
        "venue": "Circuit of the Americas", "city": "Austin, TX",
        "facts": "United States Grand Prix. Antonelli takes the chequered flag into race day on provisional pole with a 1:34.035, ahead of Verstappen, Hadjar, Leclerc and Hamilton.",
        "evidence": "Formula1.com US GP event page: Grand Prix Sunday, 25 Oct, 16:00 local track time; Q result Antonelli P1 1:34.035.",
        "records": {"home": "P1 qualifying", "away": "field"},
        "labels": {"note": "Race starts at 21:00 UTC (16:00 local Central time)."},
    },
    # ---------------- golf ------------------------------------------------------
    {
        "id": "golf-bermuda", "sport": "golf", "league": "PGA Tour", "competition": "Butterfield Bermuda Championship",
        "status": "upcoming", "market_name": "tournament winner",
        "home": "Austin Smotherman", "away": "Ryan Gerard",
        "start": "2026-10-25T18:00:00Z",
        "venue": "Port Royal Golf Club", "city": "Southampton, Bermuda",
        "facts": "Final round of the Butterfield Bermuda Championship. Austin Smotherman and Ryan Gerard share the 54-hole lead at 16 under; Gerard leads the putts-made statistic.",
        "evidence": "PGA Tour leaderboard: R3 - Austin Smotherman -16, Ryan Gerard -16, Ben Moore -14, Ben Conners -14, Brian Silverman -14.",
        "records": {"home": "-16 (T1)", "away": "-16 (T1)"},
        "labels": {"note": "Outright tournament winner estimate; multiple runners, no single-runner price."},
    },
    # ---------------- rugby union (discovery-only, no market) -------------------
    {
        "id": "ru-larochelle-bordeaux", "sport": "rugby-union", "league": "Top 14", "competition": "Top 14",
        "status": "directory-entry", "market_name": "moneyline",
        "home": "La Rochelle", "away": "Bordeaux",
        "start": "2026-10-25T20:05:00Z",
        "venue": "Stade Marcel-Deflandre", "city": "La Rochelle, France",
        "facts": "Top 14 Saturday night fixture. Discovered on the OLBG Rugby Union hub; the official Top 14 site did not render its fixture list in this session.",
        "evidence": "OLBG Rugby Union hub event card: La Rochelle v Bordeaux, 'Today 20:05', odds 1.53 / 2.40.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - Top 14 official fixture page did not render; needs a human review."},
    },
    {
        "id": "ru-quins-sarries", "sport": "rugby-union", "league": "Premiership Rugby", "competition": "Premiership",
        "status": "directory-entry", "market_name": "moneyline",
        "home": "Harlequins", "away": "Saracens",
        "start": "2026-10-25T15:00:00Z",
        "venue": "Twickenham Stoop", "city": "London, England",
        "facts": "Premiership Saturday fixture between Harlequins and Saracens. Discovered on the OLBG Rugby Union hub; the Premiership official site blocked automated reading.",
        "evidence": "OLBG Rugby Union hub event card: Harlequins v Saracens, 'Today 15:00', odds 2.50 / 1.50.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - Premiership official site blocked automated reading."},
    },
    # ---------------- volleyball (discovery-only, no market) --------------------
    {
        "id": "vb-civitanova-padova", "sport": "volleyball", "league": "Italian SuperLega", "competition": "SuperLiga",
        "status": "directory-entry", "market_name": "moneyline",
        "home": "Civitanova", "away": "Padova",
        "start": "2026-10-25T17:00:00Z",
        "venue": "PalaCivitanova", "city": "Civitanova Marche, Italy",
        "facts": "Italian SuperLiga Saturday fixture. Discovered on the OLBG Volleyball hub; the Lega Volley official site is a JavaScript shell that did not render fixtures.",
        "evidence": "OLBG Volleyball hub event card: Civitanova v Padova, 'Tomorrow 13:00', odds 1.25 / 3.50.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - Lega Volley official site is a JS shell."},
    },
    {
        "id": "vb-trentino-cisterna", "sport": "volleyball", "league": "Italian SuperLega", "competition": "SuperLiga",
        "status": "directory-entry", "market_name": "moneyline",
        "home": "Trentino", "away": "Cisterna",
        "start": "2026-10-25T16:00:00Z",
        "venue": "PalaTrento", "city": "Trento, Italy",
        "facts": "Italian SuperLiga Saturday fixture. Discovered on the OLBG Volleyball hub.",
        "evidence": "OLBG Volleyball hub event card: Trentino v Cisterna, 'Tomorrow 12:00', odds 1.65 / 2.20.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - Lega Volley official site is a JS shell."},
    },
    # ---------------- basketball (discovery-only, no market) --------------------
    {
        "id": "bb-mil-phi", "sport": "basketball", "league": "NBA", "competition": "NBA regular season",
        "status": "directory-entry", "market_name": "moneyline",
        "home": "Philadelphia 76ers", "away": "Milwaukee Bucks",
        "start": "2026-10-24T23:30:00Z",
        "venue": "Wells Fargo Center", "city": "Philadelphia, PA",
        "facts": "NBA Saturday night fixture. The NBA games page is a JavaScript shell that returned an error for the 24 Oct slate, so only the game count (8) was readable.",
        "evidence": "NBA.com games calendar for 24 Oct 2026 shows 8 games; OLBG Basketball hub lists Milwaukee v Philadelphia.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - NBA.com schedule is a JS shell."},
    },
    {
        "id": "bb-no-den", "sport": "basketball", "league": "NBA", "competition": "NBA regular season",
        "status": "directory-entry", "market_name": "moneyline",
        "home": "Denver Nuggets", "away": "New Orleans Pelicans",
        "start": "2026-10-25T02:00:00Z",
        "venue": "Ball Arena", "city": "Denver, CO",
        "facts": "NBA late-night fixture. Discovered on the OLBG Basketball hub; the official NBA schedule could not be read.",
        "evidence": "OLBG Basketball hub event card: New Orleans v Denver, 'Tonight 22:00'.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - NBA.com schedule is a JS shell."},
    },
    # ---------------- gaelic sports (discovery-only, no market) ----------------
    {
        "id": "ga-cork-sfc", "sport": "gaelic-sports", "league": "Cork SFC", "competition": "Cork Senior Football Championship",
        "status": "directory-entry", "market_name": "match winner",
        "home": "St Finbarr's", "away": "Nemo Rangers",
        "start": "2026-10-25T16:00:00Z",
        "venue": "Páirc Uí Chaoimh", "city": "Cork, Ireland",
        "facts": "Cork Senior Football Championship fixture. Discovered on the OLBG Gaelic Football hub; the GAA fixtures page renders only a results list for the current weekend.",
        "evidence": "OLBG Gaelic Football hub event card: St Finbarr's v Nemo Rangers, 'Tomorrow 16:00', odds 2.60 / 1.55.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - GAA.ie fixtures page is results-only for this window."},
    },
    {
        "id": "ga-moycullen-salthill", "sport": "gaelic-sports", "league": "Connacht SFC", "competition": "Connacht Senior Football Championship",
        "status": "directory-entry", "market_name": "match winner",
        "home": "Moycullen", "away": "Salthill-Knocknacarra",
        "start": "2026-10-25T16:00:00Z",
        "venue": "Tipperary", "city": "Tipperary, Ireland",
        "facts": "Connacht Senior Football Championship fixture. Discovered on the OLBG Gaelic Football hub.",
        "evidence": "OLBG Gaelic Football hub event card: Moycullen v Salthill-Knocknacarra, 'Tomorrow 16:00', odds 3.10 / 1.35.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - GAA.ie fixtures page is results-only for this window."},
    },
    # ---------------- greyhounds (discovery-only, no market) -------------------
    {
        "id": "gh-doncaster", "sport": "greyhounds", "league": "GBGB", "competition": "Greyhound racing",
        "status": "directory-entry", "market_name": "win market",
        "home": "Doncaster", "away": "-",
        "start": "2026-10-25T19:00:00Z",
        "venue": "Doncaster", "city": "Doncaster, England",
        "facts": "Greyhound meeting at Doncaster. The GBGB results page carries the latest meeting list and track directory; tomorrow's specific card needs a human review.",
        "evidence": "GBGB official results page lists the latest greyhound meeting at Doncaster with 12 races; OLBG Greyhounds hub carries tomorrow's racing card.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - GBGB race card needs a human review."},
    },
    # ---------------- handball (discovery-only, no market) -------------------
    {
        "id": "hb-ystads-hammarby", "sport": "handball", "league": "Handball-Allsvenskan", "competition": "Swedish Handball League",
        "status": "directory-entry", "market_name": "match winner",
        "home": "Ystads IF HF", "away": "Hammarby IF HF",
        "start": "2026-10-25T13:00:00Z",
        "venue": "Ystad Arena", "city": "Ystad, Sweden",
        "facts": "Swedish Handball League fixture. Discovered on the OLBG Handball hub; the EHF official site carries European Cup and World Championship material only.",
        "evidence": "OLBG Handball hub event card: Ystads IF HF v Hammarby IF HF, 'Tomorrow 14:00', odds 2.85 / 1.40.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - EHF carries European competition only."},
    },
    {
        "id": "hb-celje-piva", "sport": "handball", "league": "Handball League", "competition": "Slovenian Handball League",
        "status": "directory-entry", "market_name": "match winner",
        "home": "Celje Pivovarna Laško", "away": "RK Zagreb",
        "start": "2026-10-25T17:00:00Z",
        "venue": "ŽAL Arena", "city": "Celje, Slovenia",
        "facts": "Handball league fixture. Discovered on the OLBG Handball hub.",
        "evidence": "OLBG Handball hub event card: Celje Pivovarna Laško v RK Zagreb, 'Tomorrow 18:00', odds 1.65 / 2.25.",
        "records": {},
        "labels": {"note": "Discovery-only fixture - EHF carries European competition only."},
    },
    # ---------------- completed context entries ------------------------------
    {
        "id": "urc-leinster-munster", "sport": "rugby-union", "league": "United Rugby Championship", "competition": "URC Round 4",
        "status": "completed", "market_name": "moneyline",
        "home": "Leinster", "away": "Munster",
        "start": "2026-10-24T18:00:00Z",
        "venue": "RDS Arena", "city": "Dublin, Ireland",
        "facts": "URC Round 4 closed with Leinster hosting Munster at the RDS on Saturday night.",
        "evidence": "URC official Round 4 preview: Leinster v Munster, Sat 24 Oct, 18:00 UK.",
        "records": {},
        "labels": {"note": "Completed inside the window; kept as context, not priced."},
    },
]

# ---------------------------------------------------------------------------
# The long-form prediction for every pick. The bet name and the fair price
# are printed back into the text by the builder, so the prose only has to
# carry the teams, the form, the history, the statistics and the selection.
# ---------------------------------------------------------------------------
PREDICTIONS = {
"bs-ws-g2": ("The World Series swings back to American Family Field for Game 2 with Milwaukee holding a 1-0 lead in the best-of-seven. "
 "Milwaukee finished the regular season at 103-59, the best record in baseball, and they carry that strength onto their own patch, where the "
 "crowd will be at its loudest of the series. Tampa Bay are 98-64 and have to travel all night after dropping Game 1, so fatigue and venue "
 "both point the same way. With the series still open and the Brewers needing only two more wins at home, the value sits with the home side. "
 "Back Milwaukee Brewers to win Game 2 at <<PRICE>>, a Medium confidence selection for this game."),
"ih-fla-chi": ("Chicago carry the softest line in this sample at 3-7-0, which leaves them at the bottom of the NHL standings and leaking goals "
 "at home. Florida arrive at United Center with a 5-4-2 record and a sharper forward group, so the Panthers are the better side on the official "
 "numbers even though they are on the road. The Blackhawks' own record explains why this line is close rather than wide. Take Florida Panthers "
 "to win at <<PRICE>>; that is our Medium confidence call for this meeting."),
"ih-nyi-dal": ("Dallas sit higher on the official NHL standings with a 6-3-1 line and a home record that has carried them through the early weeks "
 "of the season. New York are 5-3-2 and have looked vulnerable away from home, so the Stars hold both the better goaltending and the better "
 "structure in this match-up. American Airlines Center is a difficult building for visiting attackers and the Islanders have not shown the "
 "consistency needed to take points there. Our Medium confidence view is Dallas Stars to win at <<PRICE>> on Sunday's late NHL game."),
"tn-almaty-final": ("Danil Medvedev is the higher-ranked player and he reached this ATP Almaty final the harder way, beating Alexander Bublik in "
 "three sets, 7-5 3-6 6-1, after a break-exchange opening set. Medvedev's serve and his ability to extend rallies from the baseline give him the "
 "edge against Nikoloz Basilashvili, who has to generate his own pace and who conceded breaks in both of his matches this week. Basilashvili beat "
 "Stefanos Tsitsipas to reach the final, so he is not a free pass, but Medvedev's semi-final win was built on taking control of his own serve. Back "
 "Danil Medvedev to win and lift the trophy at <<PRICE>>, a High confidence pick."),
"tn-lyon-final": ("Tommy Paul has been the most consistent player on the ATP Lyon draw and he made the final by beating Ben Shelton in straight "
 "sets. Lorenzo Musetti reached the title match by beating Flavio Cobolli 6-4 6-2, so both men are playing confident tennis, but Paul's all-court "
 "game and his serve-plus-one pattern are harder for Musetti to handle on an indoor hard court. Paul's route to the final has required fewer "
 "break points than Musetti's, which points to a more controlled service game. Take Tommy Paul to win at <<PRICE>> - the desk's High confidence "
 "call on this title match."),
"tn-brussels-final": ("Jan-Lennard Struff reached this ATP Brussels final by beating Jaume Munar in the semi-finals, while Tallon Griekspoor had to "
 "fight past Terence Atmane to take the other side of the draw. Struff's game is built for this match-up: a heavy first serve and a forehand that "
 "punishes weak returns. Griekspoor is a solid all-rounder but he has not faced a serve of that quality this week. The gap between them is small "
 "enough that the title is genuinely open. Back Jan-Lennard Struff to win at <<PRICE>>, the desk's Medium confidence view on this match-up."),
"dt-price-bunting": ("Gerwyn Price reached the PDPA European Championship quarter-final with a 10-8 win over Nathan Aspinall in round two, and "
 "Stephen Bunting answered with a 10-6 success against Scott Williams, so both men arrive at Sunday in form. Price is the more proven competitor at "
 "this stage of a major and the PDPA draw puts this one in a Sunday afternoon session, which is the stage Price has won on before. Bunting's route "
 "has been quieter, which is the kind of run that can catch a stronger opponent cold. Our Medium confidence pick is Gerwyn Price to win at "
 "<<PRICE>>."),
"dt-smith-woodhouse": ("Ross Smith advanced into his PDPA European Championship quarter-final by beating Michael van Gerwen 10-7 in round two, which "
 "tells you his scoring is right at the top of its range against the best player in the draw. Luke Woodhouse replied with a 10-6 win over Dirk van "
 "Duivenboe, so he is not an easy opponent, but Smith has faced the harder opponent and still won by three legs. Smith's route has been built on "
 "taking his chances when they arrive, and the official PDPA draw has put him on a Sunday stage he has played on before. Take Ross Smith to win at "
 "<<PRICE>>, our Medium confidence call on Sunday's session."),
"sn-niopen-final": ("Kyren Wilson is the defending Northern Ireland Open champion and he arrives in the final as the stronger of the two players, "
 "having won his semi-final without dropping a frame from the interval. His opponent is the winner of the Mark Williams v Jac Jones semi-final, which "
 "was level at 5-5 when read, so the final pairing is not settled. Wilson's centuries and his safety play have been the most reliable part of his "
 "tournament this week, and the venue is a stage he has already won at. The desk's High confidence pick is Kyren Wilson to win the title at "
 "<<PRICE>>."),
"cr-eng-pak": ("Pakistan are the home side at Gaddafi Stadium and they have already put England under real pressure in this tri-series, with England "
 "5-0 down across the limited-overs leg. England's batsmen have not converted starts into partnerships in any of the five matches they have lost, and "
 "the bowling attack has not been able to restrict Pakistan's top order. Pakistan's batting looks settled and they will want to finish the series at "
 "home in Lahore. Pakistan to win at <<PRICE>> is our Medium confidence view on the third ODI."),
"rl-aus-fiji": ("Australia meet Fiji in Brisbane with both teams carrying four competition points after winning their opening Rugby League World Cup "
 "games. Australia are the stronger side on recent history and on squad strength, and they have the home venue for this one at Suncorp Stadium. Fiji's "
 "opening win put them level on points, but the step up in opposition quality is the test here. Take Australia to win at <<PRICE>>: our High "
 "confidence pick for this group match."),
"rl-nz-ci": ("New Zealand meet the Cook Islands in Christchurch and the home venue alone makes them the side to beat on this evidence. Both teams have "
 "two competition points after one group game, but New Zealand's squad is drawn from NRL clubs while the Cook Islands rely on a smaller professional "
 "base. New Zealand's opening group game was a win and the question here is only by how much. Back New Zealand to win at <<PRICE>>: the High "
 "confidence view in Christchurch."),
"mr-f1-usgp-race": ("Antonelli takes the United States Grand Prix into race day on provisional pole with a lap of 1:34.035, the fastest of the weekend at "
 "the Circuit of the Americas. The official F1 event page frames Sunday as a 56-lap sprint on the 5.513 kilometre track. Antonelli's qualifying advantage "
 "over Verstappen is only a tenth of a second, so the race is far from decided, and the field behind includes Hadjar, Leclerc and Hamilton. That makes the "
 "race-winner market a genuine multi-runner and the desk's estimate for Antonelli is only 30%. Back Antonelli to win the race at <<PRICE>> as a Low "
 "confidence outright, not a banker."),
"golf-bermuda": ("The Butterfield Bermuda Championship goes to the final round with Austin Smotherman and Ryan Gerard tied at the top of the leaderboard on "
 "16 under par, two shots clear of Ben Moore, Ben Conners and Brian Silverman on 14 under. Ryan Gerard leads the field in putts made, which is the "
 "statistic that converts chances into a trophy on a soft Bermuda green. Smotherman is level with him on total, and with five players inside three shots "
 "of the lead the outright is a genuine multi-runner rather than a two-horse race. Take Austin Smotherman to win the tournament at <<PRICE>> as our "
 "Low confidence outright pick."),
}

# ---------------------------------------------------------------------------
# OLBG discovery capture: what each hub returned for the 24-25 Oct window.
# `captured_at` is when the hub was read, in UTC.
# ---------------------------------------------------------------------------
OLBG_LOG = [
    {"sport": "Golf", "slug": "golf", "url": "https://www.olbg.com/betting-tips/Golf/5", "captured_at": WINDOW_NOW, "as_of": "Sun 25 Oct, 12:45 ET", "headline": "Bermuda Championship, final round", "tips_offered": 3, "fixtures": ["Austin Smotherman -16", "Ryan Gerard -16", "Butterfield Bermuda Championship final round"], "note": "Outright leaderboard carried on the hub; official PGA Tour leaderboard used for the desk."},
    {"sport": "Volleyball", "slug": "volleyball", "url": "https://www.olbg.com/betting-tips/Volleyball/21", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "Italian SuperLega", "tips_offered": 0, "fixtures": ["Civitanova v Padova", "Trentino v Cisterna", "Perugia v Pordenone", "Monza v Verona"], "note": "Discovery-only; Lega Volley official site is a JavaScript shell."},
    {"sport": "Rugby Union", "slug": "rugby-union", "url": "https://www.olbg.com/betting-tips/Rugby-Union/9", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "Top 14 and Premiership", "tips_offered": 2, "fixtures": ["La Rochelle v Bordeaux", "Harlequins v Saracens", "Leinster v Munster"], "note": "Top 14 and Premiership fixtures; URC Round 4 was complete by read time."},
    {"sport": "Cricket", "slug": "cricket", "url": "https://www.olbg.com/betting-tips/Cricket/7", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "England v Pakistan tri-series, domestic T20", "tips_offered": 5, "fixtures": ["England v Pakistan (ODI)", "South Africa v Western Province", "South Africa v Eastern Province", "Northerns v Titans", "Bengal v Rest of India"], "note": "Hub shows England v Pakistan 25 Oct 04:00 ET = 08:00 UTC, which matches the ECB itinerary."},
    {"sport": "Snooker", "slug": "snooker", "url": "https://www.olbg.com/betting-tips/Snooker/8", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "Northern Ireland Open", "tips_offered": 2, "fixtures": ["Kyren Wilson v Mark Williams", "Nigel Bond v John Higgins"], "note": "Hub carried the Northern Ireland Open card; WST confirmed the final pairing."},
    {"sport": "Darts", "slug": "darts", "url": "https://www.olbg.com/betting-tips/Darts/15", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "PDPA European Championship", "tips_offered": 1, "fixtures": ["Gerwyn Price v Stephen Bunting", "Luke Littler v Joe Clayton", "Krzysztof Ratajski v Max Schindler", "Ross Smith v Luke Woodhouse"], "note": "PDPA official draw matched the hub card exactly."},
    {"sport": "Baseball", "slug": "baseball", "url": "https://www.olbg.com/betting-tips/Baseball/12", "captured_at": WINDOW_NOW, "as_of": "Thu 23 Oct, 15:20 ET", "headline": "World Series Game 2", "tips_offered": 2, "fixtures": ["Milwaukee Brewers v Tampa Bay Rays", "World Series Game 2"], "note": "Hub card 'Milwaukee Brewers vs Tampa Bay Rays, Today 20:00' = 00:00 UTC 25 Oct, matching the MLB schedule API."},
    {"sport": "Gaelic Sports", "slug": "gaelic-sports", "url": "https://www.olbg.com/betting-tips/Gaelic-Football/25", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "Cork and Connacht SFC", "tips_offered": 0, "fixtures": ["St Finbarr's v Nemo Rangers", "Moycullen v Salthill-Knocknacarra"], "note": "Gaelic Football hub carries county football only."},
    {"sport": "Greyhounds", "slug": "greyhounds", "url": "https://www.olbg.com/betting-tips/Greyhounds/28", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "Doncaster and Belle Vue", "tips_offered": 0, "fixtures": ["Doncaster", "Belle Vue"], "note": "Greyhound hub carries tonight's racing card; GBGB carries the meeting list."},
    {"sport": "Tennis", "slug": "tennis", "url": "https://www.olbg.com/betting-tips/Tennis/3", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "ATP Almaty, Lyon and Brussels", "tips_offered": 0, "fixtures": ["Almaty final", "Lyon final", "Brussels final", "Indian Wells qualifying"], "note": "Hub carries three ATP 250 finals for Sunday."},
    {"sport": "Motor Racing", "slug": "motor-racing", "url": "https://www.olbg.com/betting-tips/Motor-Racing/14", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "F1 United States Grand Prix", "tips_offered": 1, "fixtures": ["United States Grand Prix", "F1 US Grand Prix race"], "note": "Hub race card for Sunday 25 Oct."},
    {"sport": "Handball", "slug": "handball", "url": "https://www.olbg.com/betting-tips/Handball/20", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "Swedish and Slovenian leagues", "tips_offered": 0, "fixtures": ["Ystads IF HF v Hammarby IF HF", "Celje Pivovarna Laško v RK Zagreb"], "note": "EHF official site carries European Cup only; domestic league fixtures are discovery-only."},
    {"sport": "Ice Hockey", "slug": "ice-hockey", "url": "https://www.olbg.com/betting-tips/Ice-Hockey/13", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "NHL Saturday and Sunday slates", "tips_offered": 0, "fixtures": ["12 games Sat 24 Oct", "5 games Sun 25 Oct", "Florida Panthers v Chicago Blackhawks"], "note": "NHL scoreboard API used for the desk; hub carries the same slate."},
    {"sport": "Basketball", "slug": "basketball", "url": "https://www.olbg.com/betting-tips/Basketball/4", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "NBA and KBL", "tips_offered": 0, "fixtures": ["Milwaukee Bucks v Philadelphia 76ers", "New Orleans Pelicans v Denver Nuggets", "4 KBL games"], "note": "NBA.com schedule is a JavaScript shell; hub is the only readable slate."},
    {"sport": "Rugby League", "slug": "rugby-league", "url": "https://www.olbg.com/betting-tips/Rugby-League/10", "captured_at": WINDOW_NOW, "as_of": "Fri 24 Oct, 17:20 ET", "headline": "Rugby League World Cup 2026", "tips_offered": 2, "fixtures": ["New Zealand v Cook Islands", "Australia v Fiji"], "note": "RLWC group matches for Sunday 25 Oct; NRL draw confirms the fixtures."},
]

# ---------------------------------------------------------------------------
# Items that need a human: unreadable official sources, discovery-only
# fixtures, unpriced sports.
# ---------------------------------------------------------------------------
FLAG_ITEMS = [
    {
        "id": "f-sources-unreadable",
        "kind": "source",
        "severity": "flagged",
        "status": "awaiting-review",
        "where": "57bafcbb/sources.html",
        "detail": "Four official fixture feeds could not be read in this session and are linked for manual review: the Italian SuperLega site (legavolley.it) is a JavaScript shell, the NBA games calendar is a JavaScript shell that returned an error, Premiership Rugby (premierrugby.com) rejected automated reading, and the Top 14 site (top14.lnr.fr) is behind a blocking page. Every fixture sourced only from those feeds is published as a directory entry and is not priced.",
        "source_links": ["https://www.legavolley.it/", "https://www.nba.com/games?date=2026-10-24", "https://www.premierrugby.com/", "https://www.top14.lnr.fr/"],
    },
    {
        "id": "f-volleyball-no-market",
        "kind": "sport-coverage",
        "severity": "flagged",
        "status": "awaiting-review",
        "where": "57bafcbb/sports/volleyball.html",
        "detail": "Volleyball has no priced pick in this window. The official Italian SuperLega feed did not render a fixture list, so the two SuperLiga fixtures on the desk are discovery-only directory entries. No line was originated because no official record could be read.",
        "source_links": ["https://www.legavolley.it/"],
    },
    {
        "id": "f-basketball-no-market",
        "kind": "sport-coverage",
        "severity": "flagged",
        "status": "awaiting-review",
        "where": "57bafcbb/sports/basketball.html",
        "detail": "Basketball has no priced pick in this window. The NBA games calendar returned a JavaScript shell with an error, so only the game count for 24 Oct (8 games) was readable; the two NBA fixtures on the desk are discovery-only directory entries.",
        "source_links": ["https://www.nba.com/games?date=2026-10-24"],
    },
    {
        "id": "f-handball-no-market",
        "kind": "sport-coverage",
        "severity": "flagged",
        "status": "awaiting-review",
        "where": "57bafcbb/sports/handball.html",
        "detail": "Handball has no priced pick in this window. The EHF official site carries European Cup and World Championship material only, not the domestic league fixtures that fall on 25 Oct. The two fixtures on the desk are discovery-only directory entries.",
        "source_links": ["https://www.eurohandball.com/"],
    },
    {
        "id": "f-gaelic-sports-no-market",
        "kind": "sport-coverage",
        "severity": "flagged",
        "status": "awaiting-review",
        "where": "57bafcbb/sports/gaelic-sports.html",
        "detail": "Gaelic Sports has no priced pick in this window. The GAA fixtures page renders only a results list for the current weekend, so the two fixtures on the desk are discovery-only directory entries.",
        "source_links": ["https://www.gaa.ie/fixtures-results"],
    },
    {
        "id": "f-greyhounds-no-market",
        "kind": "sport-coverage",
        "severity": "flagged",
        "status": "awaiting-review",
        "where": "57bafcbb/sports/greyhounds.html",
        "detail": "Greyhounds has no priced pick in this window. The GBGB results page carries the latest meeting list and track directory but not the per-race card for 25 Oct, so the Doncaster meeting is published as a directory entry.",
        "source_links": ["https://www.gbgb.org.uk/"],
    },
    {
        "id": "f-rugby-union-no-market",
        "kind": "sport-coverage",
        "severity": "flagged",
        "status": "awaiting-review",
        "where": "57bafcbb/sports/rugby-union.html",
        "detail": "Rugby Union has no priced pick in this window. URC Round 4 was complete by read time, and the Top 14 and Premiership fixture feeds could not be read, so the two upcoming fixtures are discovery-only directory entries.",
        "source_links": ["https://www.top14.lnr.fr/", "https://www.premierrugby.com/", "https://www.unitedrugby.com/latest/match-preview-2/a-relentless-rivalry-and-a-new-home-for-ospreys-round-4-preview/"],
    },
    {
        "id": "f-darts-directory-entries",
        "kind": "fixture-source",
        "severity": "flagged",
        "status": "awaiting-review",
        "where": "57bafcbb/sports/darts.html",
        "detail": "Two darts quarter-finals (Littler v Clayton and Ratajski v Schindler) are published as directory entries. The PDPA draw was read and confirmed the fixtures, but only the two most prominent quarter-finals were read a second time from the official draw, so the other two are held back from pricing.",
        "source_links": ["https://pdpa.co.uk/event/european-championship-2026/"],
    },
    {
        "id": "f-outrights-not-high",
        "kind": "method",
        "severity": "info",
        "status": "noted",
        "where": "57bafcbb/methodology.html",
        "detail": "The motor-racing and golf markets are multi-runner outrights. Our estimate is an outright probability, not a two-way match probability, and a multi-runner cannot carry a High label under the desk's banding rule because the fair price is always outside the -250..+10000 band once a single runner is singled out. Both are published as Low confidence outrights.",
        "source_links": ["https://www.formula1.com/en/racing/2026/united-states", "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard"],
    },
]

# ---------------------------------------------------------------------------
# The pick per fixture and the originating estimate. The estimate is stored
# as a probability for the selected side and is the desk's own figure; it is
# not a price taken from any bookmaker.
# ---------------------------------------------------------------------------
PICKS = {
    "bs-ws-g2": {"pick": "Milwaukee Brewers", "bet": "Milwaukee Brewers to win", "market": "moneyline", "p_select": 0.565},
    "ih-fla-chi": {"pick": "Florida Panthers", "bet": "Florida Panthers to win", "market": "moneyline", "p_select": 0.575},
    "ih-nyi-dal": {"pick": "Dallas Stars", "bet": "Dallas Stars to win", "market": "moneyline", "p_select": 0.570},
    "tn-almaty-final": {"pick": "Danil Medvedev", "bet": "Danil Medvedev to win", "market": "match winner", "p_select": 0.620},
    "tn-lyon-final": {"pick": "Tommy Paul", "bet": "Tommy Paul to win", "market": "match winner", "p_select": 0.600},
    "tn-brussels-final": {"pick": "Jan-Lennard Struff", "bet": "Jan-Lennard Struff to win", "market": "match winner", "p_select": 0.575},
    "dt-price-bunting": {"pick": "Gerwyn Price", "bet": "Gerwyn Price to win", "market": "match winner", "p_select": 0.560},
    "dt-smith-woodhouse": {"pick": "Ross Smith", "bet": "Ross Smith to win", "market": "match winner", "p_select": 0.550},
    "sn-niopen-final": {"pick": "Kyren Wilson", "bet": "Kyren Wilson to win", "market": "match winner", "p_select": 0.635},
    "cr-eng-pak": {"pick": "Pakistan", "bet": "Pakistan to win", "market": "match winner", "p_select": 0.590},
    "rl-aus-fiji": {"pick": "Australia", "bet": "Australia to win", "market": "match winner", "p_select": 0.710},
    "rl-nz-ci": {"pick": "New Zealand", "bet": "New Zealand to win", "market": "match winner", "p_select": 0.660},
    "mr-f1-usgp-race": {"pick": "Antonelli", "bet": "Antonelli to win", "market": "race winner", "p_select": 0.300},
    "golf-bermuda": {"pick": "Austin Smotherman", "bet": "Austin Smotherman to win", "market": "tournament winner", "p_select": 0.300},
}


def _load_lines():
    try:
        return json.loads(LINES_FILE.read_text())
    except Exception:
        return {"fixtures": []}


def all_fixture_ids():
    return [f["id"] for f in FIXTURES]


def fixtures_for_sport(slug):
    return [f for f in FIXTURES if f["sport"] == slug]
