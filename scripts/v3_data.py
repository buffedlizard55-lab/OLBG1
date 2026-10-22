#!/usr/bin/env python3
"""
v3_data.py - curated snapshot for 2026-10-22.

status:
  "verified" - an official page was fetched on 2026-10-22 by this session and the participants,
               competition, venue (where published) and start were read from it.
  "carried"  - the row survives from the repository's earlier official-source dataset with its
               official link intact, but this session did not re-read the source. Never graded
               above Medium.

No value below is inferred. Where an official page does not publish a field, it is blank and a
flag records it. Ratings are the desk's own transparent conversion of the official record named
in `home_input` / `away_input`; they are not copied from any tipster.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_OLD = json.loads((ROOT / "data" / "fixtures.json").read_text(encoding="utf-8"))["matches"]
BY_ID = {m["id"]: m for m in _OLD}

DEFAULT_RATING = 58.0  # desk prior for a side with no captured official rating (always flagged)

S = {
    "nhl_sched": "https://www.nhl.com/schedule/2026-10-22",
    "nhl_stand": "https://www.nhl.com/standings/2026-10-22/wildcard",
    "nba_sched": "https://www.nba.com/schedule?date=10%2F22%2F2026",
    "nba_stand": "https://www.nba.com/standings?GroupBy=conf&Season=2026-27",
    "el_games": "https://www.euroleaguebasketball.net/en/euroleague/game-center/",
    "el_stand": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
    "mlb_sched": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29",
    "mlb_stand": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026",
    "pdc_sched": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
    "pdc_draw": "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed",
    "wst_mc": "https://www.wst.tv/match-centre/67133698-e8a4-4b37-9266-452a97df8584",
    "wst_rank": "https://www.wst.tv/rankings/",
    "wta_op": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
    "wta_rank": "https://www.wtatennis.com/rankings/singles",
    "atp_op": "https://www.protennislive.com/posting/2026/9410/op.pdf",
    "atp_rank": "https://www.atptour.com/en/rankings/singles",
    "nzc": "https://scoring.nzc.nz/fixtures",
    "icc": "https://www.icc-cricket.com/rankings",
    "urc": "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/",
    "top14": "https://top14.lnr.fr/calendrier-et-resultats",
    "prem": "https://www.premrugby.com/fixtures-results",
    "nrl_m": "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/",
    "nrl_w": "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-womens-round-2/",
    "rlwc": "https://www.nrl.com/RLWC2026/",
    "ehf": "https://ehfcl.eurohandball.com/men/2026-27/standings/",
    "plusliga": "https://www.plusliga.pl/games.html",
    "legavolley": "https://www.legavolley.it/",
    "aflw": "https://www.afl.com.au/aflw/news/1523395/full-fixture-no-re-match-for-former-melbourne-coach-mick-stinear-at-geelong-west-coast-eagles-get-a-break-by-avoiding-north-melbourne",
    "aflw_ladder": "https://www.afl.com.au/aflw/ladder",
    "gaa_munster": "https://munster.gaa.ie/fixtures/club-championships-2026/",
    "gaa_galway": "https://www.galwaygaa.ie/results/",
    "gaa_cork": "https://gaacork.ie/fixtures-results/",
    "pga": "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528",
    "dpwt": "https://www.europeantour.com/dpworld-tour/schedule/2026/",
    "lpga": "https://www.lpga.com/tournaments",
    "pgat_ch": "https://www.pgatour.com/pgatour-champions/schedule",
    "f1": "https://www.formula1.com/en/racing/2026/united-states",
    "lol": "https://lolesports.com/en-US/tournament/115660540725177488",
    "gbgb": "https://www.gbgb.org.uk/",
}


def src(name: str, url: str) -> dict:
    return {"name": name, "url": url}


def fx(**kw) -> dict:
    base = dict(
        stage="", venue="", neutral=False, flags=[], time_note="", date_local=None,
        home_input=None, away_input=None, event_only=False, total_line=None,
        total_sigma=None, hfa=0.0, sigma=14.0, model="normal",
        series=None,   # for binomial leg models: dict(legs=, per_leg_sigma=)
    )
    base.update(kw)
    return base


def inp(label, value, rating=None):
    return {"label": label, "value": value, "rating": rating}


# ---------------------------------------------------------------- NHL
# Official: nhl.com/schedule/2026-10-22 (12 games) and /2026-10-23 (2 games).
# Official: nhl.com/standings/2026-10-22/wildcard, "current as of Oct 21, 9:21 PM EDT".
NHL_T = {
    # team: (GP, W, L, OT, PTS, P%, DIFF, STRK)
    "Boston Bruins": (10, 7, 2, 1, 15, .750, +14, "OT1"),
    "Nashville Predators": (8, 3, 2, 3, 9, .563, -1, "W1"),
    "Toronto Maple Leafs": (11, 5, 4, 2, 12, .545, +3, "W2"),
    "New York Rangers": (11, 7, 3, 1, 15, .682, +9, "W1"),
    "Ottawa Senators": (9, 6, 3, 0, 12, .667, +1, "L1"),
    "San Jose Sharks": (10, 5, 4, 1, 11, .550, -8, "W1"),
    "New Jersey Devils": (9, 5, 4, 0, 10, .556, -1, "W1"),
    "Anaheim Ducks": (9, 4, 5, 0, 8, .444, -3, "L4"),
    "Pittsburgh Penguins": (10, 3, 6, 1, 7, .350, -5, "L4"),
    "Florida Panthers": (9, 5, 2, 2, 12, .667, +5, "W3"),
    "New York Islanders": (9, 5, 3, 1, 11, .611, +7, "W2"),
    "Los Angeles Kings": (7, 1, 4, 2, 4, .286, -10, "W1"),
    "St. Louis Blues": (9, 4, 4, 1, 9, .500, 0, "W1"),
    "Vegas Golden Knights": (11, 8, 3, 0, 16, .727, +14, "L1"),
    "Dallas Stars": (9, 5, 3, 1, 11, .611, +8, "W3"),
    "Winnipeg Jets": (9, 4, 3, 2, 10, .556, -2, "L2"),
    "Calgary Flames": (8, 2, 6, 0, 4, .250, -20, "W1"),
    "Minnesota Wild": (10, 6, 2, 2, 14, .700, +6, "OT1"),
    "Edmonton Oilers": (9, 7, 1, 1, 15, .833, +14, "W2"),
    "Carolina Hurricanes": (11, 8, 2, 1, 17, .773, +15, "W1"),
    "Seattle Kraken": (10, 6, 3, 1, 13, .650, +5, "W1"),
    "Utah Mammoth": (10, 7, 3, 0, 14, .700, +7, "W1"),
    "Vancouver Canucks": (11, 2, 8, 1, 5, .227, -18, "L2"),
    "Detroit Red Wings": (9, 3, 3, 3, 9, .500, -5, "OT1"),
    "Chicago Blackhawks": (9, 3, 6, 0, 6, .333, -15, "L1"),
    "Montreal Canadiens": (9, 4, 3, 2, 10, .556, -4, "OT1"),
    "Tampa Bay Lightning": (9, 7, 2, 0, 14, .778, +8, "W3"),
    "Colorado Avalanche": (10, 5, 4, 1, 11, .550, +10, "L2"),
}

NHL_GAMES = [
    ("nhl-2026020154", "2026-10-22T23:00:00Z", "Boston Bruins", "Nashville Predators", "19:00 EDT"),
    ("nhl-2026020155", "2026-10-22T23:00:00Z", "Toronto Maple Leafs", "New York Rangers", "19:00 EDT"),
    ("nhl-2026020156", "2026-10-22T23:00:00Z", "Ottawa Senators", "San Jose Sharks", "19:00 EDT"),
    ("nhl-2026020157", "2026-10-22T23:00:00Z", "New Jersey Devils", "Anaheim Ducks", "19:00 EDT"),
    ("nhl-2026020158", "2026-10-22T23:00:00Z", "Pittsburgh Penguins", "Florida Panthers", "19:00 EDT"),
    ("nhl-2026020159", "2026-10-22T23:30:00Z", "New York Islanders", "Los Angeles Kings", "19:30 EDT"),
    ("nhl-2026020160", "2026-10-23T00:00:00Z", "St. Louis Blues", "Vegas Golden Knights", "20:00 EDT"),
    ("nhl-2026020161", "2026-10-23T00:00:00Z", "Dallas Stars", "Winnipeg Jets", "20:00 EDT"),
    ("nhl-2026020162", "2026-10-23T01:00:00Z", "Calgary Flames", "Minnesota Wild", "21:00 EDT"),
    ("nhl-2026020163", "2026-10-23T01:00:00Z", "Edmonton Oilers", "Carolina Hurricanes", "21:00 EDT"),
    ("nhl-2026020164", "2026-10-23T02:00:00Z", "Seattle Kraken", "Utah Mammoth", "22:00 EDT"),
    ("nhl-2026020165", "2026-10-23T02:00:00Z", "Vancouver Canucks", "Detroit Red Wings", "22:00 EDT"),
    ("nhl-2026020166", "2026-10-24T00:00:00Z", "Chicago Blackhawks", "Montreal Canadiens", "20:00 EDT"),
    ("nhl-2026020167", "2026-10-24T01:00:00Z", "Colorado Avalanche", "Tampa Bay Lightning", "21:00 EDT"),
]

NHL_FIXTURES = []
for fid, utc, home, away, local in NHL_GAMES:
    h, a = NHL_T[home], NHL_T[away]
    NHL_FIXTURES.append(fx(
        id=fid, sport="ice-hockey", sport_name="Ice Hockey", competition="NHL", stage="Regular season",
        start_utc=utc, home=home, away=away, status="verified", verified_at="2026-10-22T02:30Z",
        sources=[src("NHL official schedule, 22-23 October 2026", S["nhl_sched"]),
                 src("NHL official standings (current as of Oct 21, 9:21 PM EDT)", S["nhl_stand"])],
        home_input=inp("Points percentage (official standings)",
                       f"{h[4]} pts in {h[0]} GP, {h[5]:.3f} P%, {h[6]:+d} GD, {h[7]}", h[5] * 100),
        away_input=inp("Points percentage (official standings)",
                       f"{a[4]} pts in {a[0]} GP, {a[5]:.3f} P%, {a[6]:+d} GD, {a[7]}", a[5] * 100),
        flags=[],
        time_note=f"{local} (ET) converted to UTC",
        hfa=2.5, sigma=2.0, total_line=6.5, total_sigma=1.9, slope=0.038,
    ))

# ---------------------------------------------------------------- NBA
# Official: nba.com/schedule?date=10/22/2026 and nba.com/standings (2026-27).
NBA_T = {
    "Detroit Pistons": (1, 1, 0), "Philadelphia 76ers": (1, 1, 0), "New York Knicks": (1, 0, 1),
    "Boston Celtics": (1, 0, 1), "Atlanta Hawks": (0, 0, 0), "Brooklyn Nets": (0, 0, 0),
    "Charlotte Hornets": (0, 0, 0), "Chicago Bulls": (0, 0, 0), "Cleveland Cavaliers": (0, 0, 0),
    "Indiana Pacers": (0, 0, 0), "Miami Heat": (0, 0, 0), "Milwaukee Bucks": (0, 0, 0),
    "Orlando Magic": (0, 0, 0), "Toronto Raptors": (0, 0, 0), "Washington Wizards": (0, 0, 0),
    "Oklahoma City Thunder": (1, 1, 0), "San Antonio Spurs": (1, 0, 1), "Golden State Warriors": (0, 0, 0),
    "Dallas Mavericks": (0, 0, 0), "Denver Nuggets": (0, 0, 0), "Houston Rockets": (0, 0, 0),
    "Los Angeles Lakers": (0, 0, 0), "LA Clippers": (0, 0, 0), "Memphis Grizzlies": (0, 0, 0),
    "Minnesota Timberwolves": (0, 0, 0), "New Orleans Pelicans": (0, 0, 0), "Phoenix Suns": (0, 0, 0),
    "Portland Trail Blazers": (0, 0, 0), "Sacramento Kings": (0, 0, 0), "Utah Jazz": (0, 0, 0),
}

NBA_GAMES = [
    ("nba-0022600006", "2026-10-22T23:00:00Z", "Philadelphia 76ers", "Cleveland Cavaliers", "Xfinity Mobile Arena, Philadelphia", "19:00 ET"),
    ("nba-0022600007", "2026-10-23T01:30:00Z", "Oklahoma City Thunder", "Denver Nuggets", "Paycom Center, Oklahoma City", "21:30 ET"),
    ("nba-1023-chi-mil", "2026-10-23T20:00:00Z", "Milwaukee Bucks", "Chicago Bulls", "Fiserv Forum, Milwaukee", "16:00 ET"),
    ("nba-1023-nyk-bos", "2026-10-23T23:00:00Z", "Boston Celtics", "New York Knicks", "TD Garden, Boston", "19:00 ET"),
    ("nba-1023-atl-cha", "2026-10-23T23:00:00Z", "Charlotte Hornets", "Atlanta Hawks", "Spectrum Center, Charlotte", "19:00 ET"),
    ("nba-1023-dal-ind", "2026-10-23T23:00:00Z", "Indiana Pacers", "Dallas Mavericks", "Gainbridge Fieldhouse, Indianapolis", "19:00 ET"),
    ("nba-1023-min-orl", "2026-10-23T23:00:00Z", "Orlando Magic", "Minnesota Timberwolves", "Kia Center, Orlando", "19:00 ET"),
    ("nba-1023-tor-was", "2026-10-23T23:00:00Z", "Washington Wizards", "Toronto Raptors", "Capital One Arena, Washington", "19:00 ET"),
    ("nba-1023-det-mia", "2026-10-24T00:00:00Z", "Miami Heat", "Detroit Pistons", "Kaseya Center, Miami", "20:00 ET"),
    ("nba-1023-hou-sas", "2026-10-24T01:30:00Z", "San Antonio Spurs", "Houston Rockets", "Moody Center, Austin", "21:30 ET"),
    ("nba-1023-nop-uta", "2026-10-24T01:30:00Z", "Utah Jazz", "New Orleans Pelicans", "Delta Center, Salt Lake City", "21:30 ET"),
    ("nba-1023-mem-gsw", "2026-10-24T02:00:00Z", "Golden State Warriors", "Memphis Grizzlies", "Chase Center, San Francisco", "22:00 ET"),
    ("nba-1023-lac-lal", "2026-10-24T02:00:00Z", "Los Angeles Lakers", "LA Clippers", "Crypto.com Arena, Los Angeles", "22:00 ET"),
    ("nba-1023-por-sac", "2026-10-24T02:00:00Z", "Sacramento Kings", "Portland Trail Blazers", "Golden 1 Center, Sacramento", "22:00 ET"),
]

NBA_FIXTURES = []
for fid, utc, home, away, venue, local in NBA_GAMES:
    def rec(t):
        gp, w, l = NBA_T[t]
        if gp == 0:
            return inp("2026-27 record (official standings)", "0-0, no games played", 50.0)
        return inp("2026-27 record (official standings)", f"{w}-{l}, {w/gp:.3f} win%", 50.0 + (w - l) * 7.0)
    NBA_FIXTURES.append(fx(
        id=fid, sport="basketball", sport_name="Basketball", competition="NBA", stage="Regular season",
        start_utc=utc, home=home, away=away, venue=venue, status="verified",
        verified_at="2026-10-22T02:35Z",
        sources=[src("NBA official schedule, 22-23 October 2026", S["nba_sched"]),
                 src("NBA official 2026-27 standings", S["nba_stand"])],
        home_input=rec(home), away_input=rec(away),
        flags=[],
        time_note=f"{local} converted to UTC",
        hfa=2.5, sigma=15.0, total_line=228.5, total_sigma=19.0, slope=0.50,
    ))

# ---------------------------------------------------------------- EuroLeague
# Official: euroleaguebasketball.net standings (rank, GP, W, L, PF, PA) and game center.
EL_T = {
    "Panathinaikos AKTOR Athens": (1, 6, 5, 1, 528, 438),
    "Fenerbahce Tarfin Istanbul": (2, 6, 5, 1, 501, 447),
    "Olympiacos Piraeus": (3, 6, 5, 1, 564, 524),
    "Hapoel IBI Tel Aviv": (4, 7, 5, 2, 630, 601),
    "Valencia Basket": (5, 6, 4, 2, 583, 537),
    "Crvena Zvezda Meridianbet Belgrade": (6, 6, 4, 2, 485, 457),
    "Dubai Basketball": (7, 6, 4, 2, 490, 493),
    "Virtus Bologna": (8, 7, 4, 3, 606, 608),
    "Real Madrid": (9, 6, 3, 3, 554, 531),
    "FC Barcelona": (10, 6, 3, 3, 534, 525),
    "Besiktas Istanbul": (11, 6, 3, 3, 554, 555),
    "Partizan Mozzart Bet Belgrade": (12, 6, 3, 3, 466, 471),
    "Anadolu Efes Istanbul": (13, 6, 2, 4, 492, 510),
    "Zalgiris Kaunas": (14, 6, 2, 4, 490, 517),
    "FC Bayern Munich": (15, 6, 2, 4, 521, 552),
    "Maccabi Rapyd Tel Aviv": (16, 6, 2, 4, 509, 540),
    "LDLC ASVEL Villeurbanne": (17, 6, 2, 4, 527, 572),
    "Paris Basketball": (18, 6, 1, 5, 504, 545),
    "Armani Olimpia Milan": (19, 6, 1, 5, 504, 559),
    "Kosner Baskonia Vitoria-Gasteiz": (20, 6, 1, 5, 504, 564),
}

EL_GAMES = [
    ("el-bes-efs-1022", "2026-10-22T17:30:00Z", "Besiktas Istanbul", "Anadolu Efes Istanbul", "Turkcell Basketball Development Center, Istanbul", "19:30 CEST"),
    ("el-dub-bay-1022", "2026-10-22T18:00:00Z", "Dubai Basketball", "FC Bayern Munich", "SAP Garden, Munich", "20:00 CEST"),
    ("el-mta-rmb-1022", "2026-10-22T18:05:00Z", "Maccabi Rapyd Tel Aviv", "Real Madrid", "Aleksandar Nikolic Hall, Belgrade", "20:05 CEST"),
    ("el-pao-bas-1022", "2026-10-22T18:15:00Z", "Panathinaikos AKTOR Athens", "Kosner Baskonia Vitoria-Gasteiz", "Telekom Center Athens", "20:15 CEST"),
    ("el-mil-bar-1022", "2026-10-22T18:30:00Z", "Armani Olimpia Milan", "FC Barcelona", "Unipol Forum, Milan", "20:30 CEST"),
    ("el-par-czv-1022", "2026-10-22T18:45:00Z", "Partizan Mozzart Bet Belgrade", "Crvena Zvezda Meridianbet Belgrade", "Belgrade Arena", "20:45 CEST"),
    ("el-zal-asv-1023", "2026-10-23T17:00:00Z", "Zalgiris Kaunas", "LDLC ASVEL Villeurbanne", "Zalgirio Arena, Kaunas", "20:00 EEST"),
    ("el-oly-fen-1023", "2026-10-23T18:15:00Z", "Olympiacos Piraeus", "Fenerbahce Tarfin Istanbul", "Sunel Arena, Piraeus", "21:15 EEST"),
    ("el-par-val-1023", "2026-10-23T18:45:00Z", "Paris Basketball", "Valencia Basket", "Adidas Arena, Paris", "20:45 CEST"),
]

EL_FIXTURES = []
for fid, utc, home, away, venue, local in EL_GAMES:
    def elrec(t):
        rank, gp, w, l, pf, pa = EL_T[t]
        rating = 50.0 + (w / gp - 0.5) * 45.0 + ((pf - pa) / gp) * 0.25
        return inp("EuroLeague record and points differential (official table)",
                   f"No. {rank}, {w}-{l} in {gp}, {pf-pa:+d} pts diff", rating)
    EL_FIXTURES.append(fx(
        id=fid, sport="basketball", sport_name="Basketball", competition="EuroLeague", stage="Round 7",
        start_utc=utc, home=home, away=away, venue=venue, status="verified",
        verified_at="2026-10-22T02:40Z",
        sources=[src("EuroLeague official Game Center, Round 7", S["el_games"]),
                 src("EuroLeague official 2026-27 regular-season standings", S["el_stand"])],
        home_input=elrec(home), away_input=elrec(away), time_note=local + " converted to UTC",
        hfa=2.0, sigma=10.5, total_line=163.5, total_sigma=18.0, slope=0.18,
    ))

# ---------------------------------------------------------------- MLB
MLB_GAMES = [
    ("mlb-849805", "2026-10-24T00:00:00Z", "Milwaukee Brewers", "Tampa Bay Rays", "American Family Field, Milwaukee", "World Series Game 1"),
    ("mlb-849802", "2026-10-25T00:00:00Z", "Milwaukee Brewers", "Tampa Bay Rays", "American Family Field, Milwaukee", "World Series Game 2"),
    ("mlb-849804", "2026-10-27T00:00:00Z", "Tampa Bay Rays", "Milwaukee Brewers", "Tropicana Field, St. Petersburg", "World Series Game 3"),
    ("mlb-849803", "2026-10-28T00:00:00Z", "Tampa Bay Rays", "Milwaukee Brewers", "Tropicana Field, St. Petersburg", "World Series Game 4"),
]
MLB_FIXTURES = []
for fid, utc, home, away, venue, stage in MLB_GAMES:
    old = BY_ID[fid]
    MLB_FIXTURES.append(fx(
        id=fid, sport="baseball", sport_name="Baseball", competition="MLB", stage=stage,
        start_utc=utc, home=home, away=away, venue=venue, status="verified",
        verified_at="2026-10-22T02:45Z",
        sources=[src("MLB official postseason schedule (StatsAPI)", S["mlb_sched"]),
                 src("MLB official 2026 regular-season standings (home/road splits)", S["mlb_stand"])],
        home_input=(old.get("inputs") or {}).get("home"), away_input=(old.get("inputs") or {}).get("away"),
        flags=["Starting pitchers are not published on the schedule feed at capture time; no pitcher adjustment is applied."]
        + (["Games 3 and 4 keep the series dates from the official schedule; the first-pitch clock for those two games was not captured, so the 00:00Z marker is the published date boundary, not a confirmed start time."]
           if fid in ("mlb-849804", "mlb-849803") else []),
        hfa=0.0, sigma=3.0, total_line=8.5, total_sigma=2.4,
    ))

# ---------------------------------------------------------------- Darts (PDC)
PDC_GAMES = [
    ("pdc-ec-01", "2026-10-22T17:00:00Z", "Luke Woodhouse", 9, "Dirk van Duijvenbode", 24),
    ("pdc-ec-02", "2026-10-22T17:00:00Z", "Danny Noppert", 5, "Stephen Bunting", 28),
    ("pdc-ec-03", "2026-10-22T17:00:00Z", "Niels Zonneveld", 4, "Cameron Menzies", 29),
    ("pdc-ec-04", "2026-10-22T17:00:00Z", "Gerwyn Price", 13, "Rob Cross", 20),
    ("pdc-ec-05", "2026-10-22T17:00:00Z", "James Wade", 16, "Damon Heta", 17),
    ("pdc-ec-06", "2026-10-22T17:00:00Z", "Luke Humphries", 12, "Ryan Searle", 21),
    ("pdc-ec-07", "2026-10-22T17:00:00Z", "Gian van Veen", 8, "Andrew Gilding", 25),
    ("pdc-ec-08", "2026-10-22T17:00:00Z", "Ross Smith", 1, "Karel Sedlacek", 32),
    ("pdc-ec-09", "2026-10-23T17:00:00Z", "Ryan Joyce", 15, "Jermaine Wattimena", 18),
    ("pdc-ec-10", "2026-10-23T17:00:00Z", "Krzysztof Ratajski", 3, "Dave Chisnall", 30),
    ("pdc-ec-11", "2026-10-23T17:00:00Z", "Nathan Aspinall", 6, "Cristo Reyes", 27),
    ("pdc-ec-12", "2026-10-23T17:00:00Z", "Jonny Clayton", 7, "Niko Springer", 26),
    ("pdc-ec-13", "2026-10-23T17:00:00Z", "Luke Littler", 11, "William O'Connor", 22),
    ("pdc-ec-14", "2026-10-23T17:00:00Z", "Wessel Nijman", 2, "Martin Schindler", 31),
    ("pdc-ec-15", "2026-10-23T17:00:00Z", "Kevin Doets", 14, "Michael van Gerwen", 19),
    ("pdc-ec-16", "2026-10-23T17:00:00Z", "Josh Rock", 10, "Chris Dobey", 23),
]
PDC_FIXTURES = []
for fid, utc, home, hs, away, as_ in PDC_GAMES:
    PDC_FIXTURES.append(fx(
        id=fid, sport="darts", sport_name="Darts", competition="PDC Machineseeker European Championship",
        stage="Round 1, best of 11 legs", start_utc=utc, home=home, away=away,
        venue="Westfalenhalle, Dortmund", status="verified", verified_at="2026-10-22T02:50Z",
        sources=[src("PDC official schedule of play", S["pdc_sched"]),
                 src("PDC official field and draw (seed order)", S["pdc_draw"])],
        home_input=inp("PDC European Tour seed", f"Seed {hs} of 32", 100.0 - 1.0 * hs),
        away_input=inp("PDC European Tour seed", f"Seed {as_} of 32", 100.0 - 1.0 * as_),
        flags=[],
        time_note="Session start 17:00 UTC; per-match walk-on not published",
        model="binomial", series={"legs": 11, "per_leg": 0.16}, hfa=0.0,
    ))

# ---------------------------------------------------------------- Snooker (WST)
SNOOKER_GAMES = [
    ("snk-r3-wilson-pang", "2026-10-22T07:00:00Z", "Kyren Wilson", 9, "Pang Junxu", None, "08:00"),
    ("snk-r3-selt-craigie", "2026-10-22T07:00:00Z", "Matthew Selt", None, "Sam Craigie", None, "08:00"),
    ("snk-r3-slessor-walden", "2026-10-22T08:00:00Z", "Elliot Slessor", None, "Ricky Walden", None, "09:00"),
    ("snk-r3-mcgill-baranowski", "2026-10-22T08:00:00Z", "Anthony McGill", None, "Mateusz Baranowski", None, "09:00"),
    ("snk-r3-williams-odonnell", "2026-10-22T13:00:00Z", "Mark Williams", 8, "Martin O'Donnell", None, "14:00"),
    ("snk-r3-gilbert-cheung", "2026-10-22T13:00:00Z", "David Gilbert", None, "Cheung Ka Wai", None, "14:00"),
    ("snk-r3-brown-donaldson", "2026-10-22T14:00:00Z", "Jordan Brown", None, "Scott Donaldson", None, "15:00"),
    ("snk-r3-jones-wells", "2026-10-22T14:00:00Z", "Jak Jones", None, "Daniel Wells", None, "15:00"),
]
SNOOKER_FIXTURES = []
for fid, utc, home, hr, away, ar, local in SNOOKER_GAMES:
    def snk(rank):
        if rank:
            return inp("WST world ranking (top-11 snapshot)", f"No. {rank}", 100.0 - 2.0 * rank)
        return inp("WST world ranking", "not captured outside the top 11", None)
    SNOOKER_FIXTURES.append(fx(
        id=fid, sport="snooker", sport_name="Snooker", competition="BetVictor Northern Ireland Open",
        stage="Round 3, best of 7 frames", start_utc=utc, home=home, away=away,
        venue="Waterfront Hall, Belfast", status="verified", verified_at="2026-10-22T02:55Z",
        sources=[src("WST official match centre / Thursday order of play", S["wst_mc"]),
                 src("WST official world rankings", S["wst_rank"])],
        home_input=snk(hr), away_input=snk(ar),
        flags=[],
        time_note=f"WST session clock {local} (local UK time, BST); converted to UTC by subtracting one hour",
        model="binomial", series={"legs": 7, "per_leg": 0.20}, hfa=0.0,
    ))

# ---------------------------------------------------------------- Tennis
TENNIS_GAMES = [
    ("ten-atp-atmane-bellucci", "2026-10-22T06:30:00Z", "Terence Atmane", None, "Mattia Bellucci", None,
     "Almaty Open", "Almaty Arena", "11:30 local (UTC+5)", "atp"),
    ("ten-atp-machac-khachanov", "2026-10-22T08:00:00Z", "Tomas Machac", None, "Karen Khachanov", 5,
     "Almaty Open", "Almaty Arena", "Not before 13:00 local (UTC+5)", "atp"),
    ("ten-atp-medvedev-shimabukuro", None, "Daniil Medvedev", 1, "Sho Shimabukuro", None,
     "Almaty Open", "Almaty Arena", "Followed by; no clock time published", "atp"),
    ("ten-atp-bublik-marozsan", "2026-10-22T14:30:00Z", "Alexander Bublik", 3, "Fabian Marozsan", None,
     "Almaty Open", "Almaty Arena", "Not before 19:30 local (UTC+5)", "atp"),
    ("ten-wta-jovic-paolini", "2026-10-22T05:00:00Z", "Iva Jovic", 4, "Jasmine Paolini", None,
     "BNB Ningbo Open", "Yinzhou Tennis Center, Ningbo", "13:00 local (UTC+8)", "wta"),
    ("ten-wta-kawa-bencic", None, "Katarzyna Kawa", None, "Belinda Bencic", 5,
     "BNB Ningbo Open", "Yinzhou Tennis Center, Ningbo", "Followed by; no clock time published", "wta"),
    ("ten-wta-eala-shnaider", None, "Alexandra Eala", None, "Diana Shnaider", 6,
     "BNB Ningbo Open", "Yinzhou Tennis Center, Ningbo", "Followed by; no clock time published", "wta"),
    ("ten-wta-rybakina-kudermetova", "2026-10-22T11:00:00Z", "Elena Rybakina", 1, "Polina Kudermetova", None,
     "BNB Ningbo Open", "Yinzhou Tennis Center, Ningbo", "Not before 19:00 local (UTC+8)", "wta"),
]
TENNIS_FIXTURES = []
for fid, utc, home, hs, away, as_, comp, venue, note, tour in TENNIS_GAMES:
    def tseed(s):
        if s:
            return inp("Tournament seed (official draw)", f"Seed {s}", 100.0 - 2.5 * s)
        return inp("Official ranking", "not captured for this snapshot", None)
    TENNIS_FIXTURES.append(fx(
        id=fid, sport="tennis", sport_name="Tennis", competition=comp, stage="Round of 16",
        start_utc=utc, date_local="2026-10-22", home=home, away=away, venue=venue, status="verified",
        verified_at="2026-10-22T03:00Z",
        sources=[src("ATP official order of play, Thursday 22 October" if tour == "atp"
                     else "WTA official order of play, Thursday 22 October",
                     S["atp_op"] if tour == "atp" else S["wta_op"]),
                 src("PIF ATP rankings" if tour == "atp" else "PIF WTA rankings",
                     S["atp_rank"] if tour == "atp" else S["wta_rank"])],
        home_input=tseed(hs), away_input=tseed(as_),
        flags=[],
        time_note=note, model="binomial", series={"legs": 3, "per_leg": 0.22}, hfa=0.0,
    ))

# ---------------------------------------------------------------- AFLW
AFLW_GAMES = [
    ("aflw-r11-07", "2026-10-23T08:45:00Z", "Port Adelaide", "Collingwood", "Alberton Oval, Adelaide", "7.15pm ACDT"),
    ("aflw-r11-09", "2026-10-24T02:05:00Z", "St Kilda", "Brisbane Lions", "RSEA Park, Melbourne", "1.05pm AEDT"),
    ("aflw-r11-02", "2026-10-24T04:05:00Z", "Geelong Cats", "Fremantle", "GMHBA Stadium, Geelong", "3.05pm AEDT"),
    ("aflw-r11-06", "2026-10-24T06:05:00Z", "Gold Coast SUNS", "Richmond", "People First Stadium, Gold Coast", "5.05pm AEDT"),
    ("aflw-r11-03", "2026-10-24T08:15:00Z", "Western Bulldogs", "Melbourne", "Mission Whitten Oval, Melbourne", "7.15pm AEDT"),
    ("aflw-r11-08", "2026-10-25T01:35:00Z", "Sydney Swans", "West Coast Eagles", "Henson Park, Sydney", "12.35pm AEDT"),
    ("aflw-r11-01", "2026-10-25T02:05:00Z", "North Melbourne", "Adelaide Crows", "North Hobart Oval, Hobart", "1.05pm AEDT"),
    ("aflw-r11-05", "2026-10-25T04:05:00Z", "Hawthorn", "Essendon", "Kennedy Community Centre, Dingley", "3.05pm AEDT"),
    ("aflw-r11-04", "2026-10-25T06:05:00Z", "Carlton", "GWS GIANTS", "Ikon Park, Melbourne", "5.05pm AEDT"),
]
AFLW_FIXTURES = []
for fid, utc, home, away, venue, local in AFLW_GAMES:
    old = BY_ID[fid]
    flags = []
    if fid == "aflw-r11-07":
        flags.append("Start corrected this snapshot: the official fixture is 7.15pm ACDT (UTC+10:30) = 08:45Z, not the 08:15Z previously stored for a 7.15pm AEST reading.")
    AFLW_FIXTURES.append(fx(
        id=fid, sport="aussie-rules", sport_name="Aussie Rules", competition="AFLW", stage="Round 11",
        start_utc=utc, home=home, away=away, venue=venue, status="verified",
        verified_at="2026-10-22T03:05Z",
        sources=[src("AFL official 2026 NAB AFLW fixture release (Round 11)", S["aflw"]),
                 src("AFL official 2026 NAB AFLW ladder", S["aflw_ladder"])],
        home_input=(old.get("inputs") or {}).get("home"), away_input=(old.get("inputs") or {}).get("away"),
        flags=flags, time_note=local + " converted to UTC",
        hfa=2.0, sigma=17.0, total_line=75.5, total_sigma=14.0, slope=0.55,
    ))

# ---------------------------------------------------------------- Rugby League (RLWC)
RL_GAMES = [
    ("rl-wc26w-sam-wal", "2026-10-23T06:45:00Z", "Samoa Women", "Wales Women", "CommBank Stadium, Sydney", "Friday 5.45pm AEDT"),
    ("rl-wc26-tga-lbn", "2026-10-23T09:05:00Z", "Tonga", "Lebanon", "CommBank Stadium, Sydney", "Friday 8.05pm AEDT"),
    ("rl-wc26-png-sam", "2026-10-24T04:25:00Z", "Papua New Guinea", "Samoa", "Santos National Football Stadium, Port Moresby", "Saturday 3.25pm AEDT"),
    ("rl-wc26-eng-fra", "2026-10-24T06:35:00Z", "England", "France", "HBF Park, Perth", "Saturday 5.35pm AEDT"),
    ("rl-wc26w-aus-eng", None, "Australia Jillaroos", "England Women", "HBF Park, Perth", "Saturday 24 October; kick-off time not published"),
    ("rl-wc26-nzl-cok", "2026-10-25T05:05:00Z", "New Zealand", "Cook Islands", "One NZ Stadium, Christchurch", "Sunday 4.05pm AEDT"),
    ("rl-wc26-aus-fij", "2026-10-25T09:05:00Z", "Australia", "Fiji", "Suncorp Stadium, Brisbane", "Sunday 8.05pm AEDT"),
]
RL_FIXTURES = []
for fid, utc, home, away, venue, local in RL_GAMES:
    old = BY_ID[fid]
    flags = []
    if fid == "rl-wc26w-aus-eng":
        flags.append("England's Jasmin Strange was ruled out of the tournament with a knee injury at training on 21 October (NRL official team lists).")
        flags.append("The NRL Round 2 women's team-list article gives the date and venue but not a kick-off clock, so the start is deliberately left blank.")
    if fid == "rl-wc26w-sam-wal":
        flags.append("Kick-off is confirmed by the NRL women's Round 2 fixture; late team-mail changes were not re-checked for this match.")
    RL_FIXTURES.append(fx(
        id=fid, sport="rugby-league", sport_name="Rugby League", competition="Rugby League World Cup 2026",
        stage="Round 2", start_utc=utc, date_local=("2026-10-24" if utc is None else None),
        home=home, away=away, venue=venue, status="verified",
        verified_at="2026-10-22T03:10Z",
        sources=[src("NRL official Round 2 women's team lists" if "w-" in fid else "NRL official Round 2 men's team lists",
                     S["nrl_w"] if "w-" in fid else S["nrl_m"]),
                 src("NRL official Rugby League World Cup 2026 hub", S["rlwc"])],
        home_input=(old.get("inputs") or {}).get("home"), away_input=(old.get("inputs") or {}).get("away"),
        flags=flags, time_note=local + " converted to UTC",
        hfa=2.0, sigma=16.0, total_line=42.5, total_sigma=10.0,
    ))

# ---------------------------------------------------------------- Handball (EHF)
EHF_GAMES = [
    ("hand-ehf-12049", "2026-10-22T16:45:00Z", "MT Melsungen", "Orlen Wisla Plock", "Rothenbach-Halle, Kassel", "18:45 CEST"),
    ("hand-ehf-12051", "2026-10-22T16:45:00Z", "OTP Bank - PICK Szeged", "GOG", "Pick Arena, Szeged", "18:45 CEST"),
    ("hand-ehf-12054", "2026-10-22T18:45:00Z", "Sporting CP", "IFK Kristianstad", "Pavilhao Joao Rocha, Lisbon", "20:45 CEST"),
    ("hand-ehf-12046", "2026-10-22T18:45:00Z", "Barça", "Montpellier Handball", "Palau Blaugrana, Barcelona", "20:45 CEST"),
    ("hand-ehf-12048", "2026-10-22T18:45:00Z", "Kolstad Håndball", "SC Magdeburg", "Trondheim Spektrum", "20:45 CEST"),
]
EHF_FIXTURES = []
for fid, utc, home, away, venue, local in EHF_GAMES:
    old = BY_ID.get(fid) or {}
    oi = old.get("inputs") or {}
    hi = oi.get("home") or inp("EHF Champions League table", "not captured", None)
    ai = oi.get("away") or inp("EHF Champions League table", "not captured", None)
    EHF_FIXTURES.append(fx(
        id=fid, sport="handball", sport_name="Handball", competition="EHF Champions League Men",
        stage="Round 5", start_utc=utc, home=home, away=away, venue=venue, status="verified",
        verified_at="2026-10-22T03:15Z",
        sources=[src("EHF Champions League Men official standings and calendar", S["ehf"])],
        home_input=hi, away_input=ai,
        flags=[],
        time_note=local + " converted to UTC", hfa=1.5, sigma=7.0, total_line=61.5, total_sigma=7.5, slope=0.15,
    ))

# ---------------------------------------------------------------- Cricket (NZC)
CRICKET_GAMES = [
    ("cric-nza-inda-fc1", "2026-10-23", "New Zealand A", "India A", "Bert Sutcliffe Oval, Lincoln University", "1st four-day match", "NZC lists Fri 23 Oct, 6.00pm local"),
    ("cric-nz-ind-t20-2", "2026-10-24", "New Zealand", "India", "Hagley Oval, Christchurch", "2nd T20I", "NZC lists Sat 24 Oct; clock time not converted"),
    ("cric-nz-ind-t20-3", "2026-10-27", "New Zealand", "India", "Hnry Stadium, Wellington", "3rd T20I", "NZC lists Tue 27 Oct; clock time not converted"),
    ("cric-ford-auck-cant", "2026-10-27", "Auckland Aces", "Canterbury", "Kennards Hire Community Oval, Auckland", "Ford Trophy Round 1", "NZC lists Tue 27 Oct, 5.30pm local"),
]
CRICKET_FIXTURES = []
for fid, date_local, home, away, venue, stage, note in CRICKET_GAMES:
    old = BY_ID.get(fid) or {"inputs": {}}
    CRICKET_FIXTURES.append(fx(
        id=fid, sport="cricket", sport_name="Cricket",
        competition="Ford Trophy" if "ford" in fid else "International",
        stage=stage, start_utc=None, date_local=date_local, home=home, away=away, venue=venue,
        status="verified", verified_at="2026-10-22T03:20Z",
        sources=[src("New Zealand Cricket official fixtures and results", S["nzc"]),
                 src("ICC official team rankings (used for the international rating)", S["icc"]),
                 ],
        home_input=(old.get("inputs") or {}).get("home"), away_input=(old.get("inputs") or {}).get("away"),
        flags=["NZC's fixture list shows a local clock without a timezone label; UTC start is left blank rather than guessed."],
        time_note=note, hfa=2.0, sigma=22.0, total_line=170.5, total_sigma=24.0,
    ))

# ---------------------------------------------------------------- Rugby Union (carried)
RU_GAMES = [
    ("ru-urc-609577", "2026-10-23T18:45:00Z", "Connacht", "Zebre Parma", "Dexcom Stadium, Galway", "19:45 IRE & UK"),
    ("ru-urc-609576", "2026-10-24T11:45:00Z", "Vodacom Bulls", "Ulster", "Loftus Versfeld, Pretoria", "12:45 IRE & UK / 13:45 SA"),
    ("ru-urc-609580", "2026-10-24T14:00:00Z", "DHL Stormers", "Scarlets", "DHL Stadium, Cape Town", "15:00 IRE & UK / 16:00 SA"),
    ("ru-urc-609578", "2026-10-24T17:00:00Z", "Leinster", "Munster", "Dublin (venue TBC on the URC fixture list)", "18:00 IRE & UK"),
    ("ru-top14-609567", "2026-10-24T14:35:00Z", "Stade Toulousain", "USA Perpignan", "Stade Ernest-Wallon, Toulouse", "16:35 CEST"),
    ("ru-top14-609564", "2026-10-24T14:35:00Z", "Aviron Bayonnais", "LOU Rugby", "Stade Jean-Dauger, Bayonne", "16:35 CEST"),
    ("ru-top14-609554", "2026-10-25T20:05:00Z", "Stade Rochelais", "Union Bordeaux-Bègles", "Stade Marcel-Deflandre, La Rochelle", "21:05 CET"),
    ("ru-gloucester-bath", "2026-10-23T18:45:00Z", "Gloucester", "Bath", "Kingsholm, Gloucester", "19:45 BST"),
    ("ru-newcastle-sale", "2026-10-23T18:45:00Z", "Newcastle Red Bulls", "Sale Sharks", "Kingston Park, Newcastle", "19:45 BST"),
    ("ru-leicester-northampton", "2026-10-24T14:05:00Z", "Leicester Tigers", "Northampton Saints", "Mattioli Woods Welford Road, Leicester", "15:05 BST"),
    ("ru-bristol-exeter", "2026-10-24T14:05:00Z", "Bristol Bears", "Exeter Chiefs", "Ashton Gate, Bristol", "15:05 BST"),
    ("ru-harlequins-saracens", "2026-10-25T15:00:00Z", "Harlequins", "Saracens", "Twickenham Stoop, London", "15:00 GMT"),
]
RU_FIXTURES = []
for fid, utc, home, away, venue, local in RU_GAMES:
    old = BY_ID[fid]
    if fid.startswith("ru-urc"):
        comp, sources = "United Rugby Championship", [src("URC official 2026/27 fixtures in full", S["urc"])]
    elif fid.startswith("ru-top14"):
        comp, sources = "French Top 14", [src("LNR official Top 14 calendar", S["top14"])]
    else:
        comp, sources = "Gallagher Premiership", [src("Premiership Rugby official fixtures", S["prem"])]
    RU_FIXTURES.append(fx(
        id=fid, sport="rugby-union", sport_name="Rugby Union", competition=comp,
        stage="Round 4" if not fid.startswith("ru-top14") else "Journée 7",
        start_utc=utc, home=home, away=away, venue=venue, status="carried",
        verified_at="2026-10-21",
        sources=sources, home_input=(old.get("inputs") or {}).get("home"),
        away_input=(old.get("inputs") or {}).get("away"),
        flags=["Carried from the previous snapshot with its official link intact but not re-read on 22 October; no official rating captured, so this row is capped at Low confidence."],
        time_note=local + " converted to UTC", hfa=2.5, sigma=11.0, total_line=48.5, total_sigma=9.0,
    ))

# ---------------------------------------------------------------- Volleyball (carried)
VOLLEY_GAMES = ["vol-plus-36963", "vol-plus-36964", "vol-plus-36965",
                "vol-lega-perugia", "vol-lega-trentino", "vol-lega-lube"]
VOLLEY_FIXTURES = []
for fid in VOLLEY_GAMES:
    old = BY_ID[fid]
    VOLLEY_FIXTURES.append(fx(
        id=fid, sport="volleyball", sport_name="Volleyball",
        competition="PlusLiga" if "plus" in fid else "SuperLega Credem Banca",
        stage=old.get("stage", "Regular season"), start_utc=old["start_utc"],
        home=old["home"], away=old["away"], venue=old["venue"], status="carried",
        verified_at="2026-10-21",
        sources=[src("PlusLiga official fixtures" if "plus" in fid else "Lega Volley official fixtures",
                     S["plusliga"] if "plus" in fid else S["legavolley"])],
        home_input=(old.get("inputs") or {}).get("home"), away_input=(old.get("inputs") or {}).get("away"),
        flags=["Carried with its official link but not re-read on 22 October; no official table captured, so the row is capped at Low confidence.",
               "plusliga.pl now redirects the public schedule to the TAURON Liga (women's) site, so the men's fixture cannot be re-certified from that URL."]
        if "plus" in fid else ["Carried with its official link but not re-read on 22 October; no official table captured, so the row is capped at Low confidence."],
        hfa=1.5, sigma=9.0, total_line=175.5, total_sigma=18.0,
    ))

# ---------------------------------------------------------------- Gaelic football (carried)
GAA_GAMES = ["gaa-galway-3532", "gaa-cork-3530", "gaa-waterford-3536", "gaa-kerry-sfc"]
GAA_FIXTURES = []
for fid in GAA_GAMES:
    old = BY_ID[fid]
    GAA_FIXTURES.append(fx(
        id=fid, sport="gaelic-football", sport_name="Gaelic Football",
        competition=old["competition"], stage="County final", start_utc=old["start_utc"],
        home=old["home"], away=old["away"], venue=old["venue"], status="carried",
        verified_at="2026-10-21",
        sources=[src("Provincial / county board official fixtures", s["url"]) for s in old["sources"][:2]],
        home_input=(old.get("inputs") or {}).get("home"), away_input=(old.get("inputs") or {}).get("away"),
        flags=["No official club rating is published at this level, so the row uses a neutral baseline and is graded Low.",
               "The Munster club championship page lists no fixture of this kind before 1 November; the county-final date is carried from the earlier snapshot."],
        hfa=1.0, sigma=6.0, total_line=31.5, total_sigma=6.5,
    ))

# ---------------------------------------------------------------- Event-only cards
EVENT_FIXTURES = [
    fx(id="golf-bermuda-2026", sport="golf", sport_name="Golf",
       competition="PGA TOUR Butterfield Bermuda Championship", stage="72-hole stroke play",
       date_local="2026-10-22", home="Butterfield Bermuda Championship", away="",
       venue="Port Royal Golf Course, Southampton, Bermuda", status="carried", verified_at="2026-10-21",
       sources=[src("PGA TOUR official tournament page", S["pga"])], event_only=True,
       flags=["No head-to-head market is priced: the official entry list was not captured, so there is no verified field-strength input and no selection is made."]),
    fx(id="golf-genesis-2026", sport="golf", sport_name="Golf",
       competition="DP World Tour Genesis Championship", stage="72-hole stroke play",
       date_local="2026-10-22", home="Genesis Championship", away="",
       venue="Woo Jeong Hills Country Club, Republic of Korea", status="carried", verified_at="2026-10-21",
       sources=[src("DP World Tour official 2026 schedule", S["dpwt"])], event_only=True,
       flags=["No head-to-head market is priced: entry list not captured."]),
    fx(id="golf-bmw-ladies-2026", sport="golf", sport_name="Golf",
       competition="LPGA BMW Ladies Championship", stage="72-hole stroke play",
       date_local="2026-10-22", home="BMW Ladies Championship", away="",
       venue="Pine Beach Golf Links, Haenam, Republic of Korea", status="carried", verified_at="2026-10-21",
       sources=[src("LPGA official tournament schedule", S["lpga"])], event_only=True,
       flags=["No head-to-head market is priced: entry list not captured."]),
    fx(id="golf-stifel-2026", sport="golf", sport_name="Golf",
       competition="PGA TOUR Champions Stifel Charity Classic", stage="54-hole stroke play",
       date_local="2026-10-22", home="Stifel Charity Classic", away="",
       venue="Norwood Hills Country Club, St. Louis", status="carried", verified_at="2026-10-21",
       sources=[src("PGA TOUR Champions official schedule", S["pgat_ch"])], event_only=True,
       flags=["No head-to-head market is priced: entry list not captured."]),
    fx(id="f1-usgp-2026", sport="motor-racing", sport_name="Motor Racing",
       competition="Formula 1 MSC Cruises United States Grand Prix", stage="Grand Prix, 56 laps",
       start_utc="2026-10-25T21:00:00Z", home="United States Grand Prix", away="",
       venue="Circuit of The Americas, Austin", status="verified", verified_at="2026-10-22T03:25Z",
       sources=[src("Formula 1 official United States Grand Prix schedule", S["f1"])], event_only=True,
       flags=["Race starts 16:00 track time (CDT) = 21:00 UTC. No race-winner market is priced because the official entry list was not captured."],
       time_note="16:00 track time (CDT, UTC-5)"),
    fx(id="lol-worlds26-swiss", sport="esports", sport_name="eSports",
       competition="League of Legends World Championship 2026", stage="Swiss stage",
       date_local="2026-10-22", home="Worlds 2026 Swiss Stage", away="",
       venue="United States (per-match venue not captured)", status="carried", verified_at="2026-10-21",
       sources=[src("Riot Games LoL Esports official Worlds 2026 hub", S["lol"])], event_only=True,
       flags=["The official tournament page did not render a specific fixture at capture time, so no head-to-head is listed and no pick is made."]),
    fx(id="gbgb-meetings-1022", sport="greyhounds", sport_name="Greyhounds",
       competition="GBGB licensed race meetings", stage="Race meetings",
       date_local="2026-10-22", home="GBGB licensed meetings", away="",
       venue="GBGB licensed tracks (meeting list not captured)", status="carried", verified_at="2026-10-21",
       sources=[src("Greyhound Board of Great Britain official site", S["gbgb"])], event_only=True,
       flags=["gbgb.org.uk returned HTTP 500 at capture time; no race card, trap draw or price can be verified, so no selection is made."]),
]

# Per-sport conversion of a 0-100 rating point into a scoring margin, and the deepest
# handicap line the desk is willing to quote. These are modelling choices, not facts.
SPORT_SLOPE = {
    "ice-hockey": 0.038, "basketball": 0.18, "baseball": 0.035, "aussie-rules": 0.55,
    "rugby-league": 0.50, "rugby-union": 0.35, "handball": 0.15, "cricket": 0.40,
    "volleyball": 0.25, "gaelic-football": 0.25,
}
SPORT_HC = {
    "ice-hockey": 3.5, "basketball": 16.5, "baseball": 2.5, "aussie-rules": 40.5,
    "rugby-league": 30.5, "rugby-union": 20.5, "handball": 12.5, "cricket": 40.5,
    "volleyball": 9.5, "gaelic-football": 12.5,
}

ALL = (NHL_FIXTURES + NBA_FIXTURES + EL_FIXTURES + MLB_FIXTURES + PDC_FIXTURES
       + SNOOKER_FIXTURES + TENNIS_FIXTURES + AFLW_FIXTURES + RL_FIXTURES + EHF_FIXTURES
       + CRICKET_FIXTURES + RU_FIXTURES + VOLLEY_FIXTURES + GAA_FIXTURES + EVENT_FIXTURES)

for _f in ALL:
    _f.setdefault("slope", SPORT_SLOPE.get(_f["sport"], 0.05))
    _f.setdefault("hc_max", SPORT_HC.get(_f["sport"], 6.5))
    _f["slope"] = _f.get("slope") or SPORT_SLOPE.get(_f["sport"], 0.05)
    _f["hc_max"] = _f.get("hc_max") or SPORT_HC.get(_f["sport"], 6.5)

VERIFICATION = [
    ("NHL", "https://www.nhl.com/schedule/2026-10-22", "2026-10-22T02:30Z",
     "12 games on 22 October and 2 on 23 October, with ET start times; all 32 clubs' GP/W/L/OT/PTS/P%/DIFF from the wildcard table current as of 21 Oct 9:21 PM EDT."),
    ("NBA", "https://www.nba.com/schedule?date=10%2F22%2F2026", "2026-10-22T02:35Z",
     "2 games on 22 October and 12 on 23 October with ET tip times and arenas; 2026-27 standings (only DET, PHI and OKC at 1-0, SAS/NYK/BOS at 0-1)."),
    ("EuroLeague", "https://www.euroleaguebasketball.net/en/euroleague/standings/", "2026-10-22T02:40Z",
     "Full 20-club table with GP/W/L/PF/PA and rank, plus the Round 7 game centre with all nine fixtures and arenas."),
    ("MLB", "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29", "2026-10-22T02:45Z",
     "Only the World Series remains: Games 1-4 with venues and dates; regular-season home/road splits for TB and MIL."),
    ("PDC", "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/", "2026-10-22T02:50Z",
     "All 16 first-round ties in draw order, 19:00 CEST session start, best-of-11 format and the 1-32 seed bracket."),
    ("WST", "https://www.wst.tv/match-centre/67133698-e8a4-4b37-9266-452a97df8584", "2026-10-22T02:55Z",
     "Eight Round 3 matches on 22 October with session clocks, and the completed Round 2 result Pang 4-3 Davies (14-69, 33-103(112), 112-0, 56-61, 73-35, 56-31, 81-60)."),
    ("ATP Almaty", "https://www.protennislive.com/posting/2026/9410/op.pdf", "2026-10-22T03:00Z",
     "Four Round of 16 singles matches with seeds and local start times."),
    ("WTA Ningbo", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf", "2026-10-22T03:00Z",
     "Four Round of 16 singles matches with seeds and local start times, released 21 October 22:13."),
    ("NZC", "https://scoring.nzc.nz/fixtures", "2026-10-22T03:20Z",
     "NZ v India T20I series dates/venues, Australia Women v NZ Women 3rd T20I, NZ A v India A, Ford Trophy Round 1."),
    ("RLWC", "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/", "2026-10-22T03:10Z",
     "Five men's Round 2 matches and the women's Round 2 schedule with venues and AEDT kick-offs; late mail including J Strange out of the tournament."),
    ("EHF", "https://ehfcl.eurohandball.com/men/2026-27/standings/", "2026-10-22T03:15Z",
     "Five Round 5 matches on 22 October with 18:45/20:45 CEST throw-offs and venues."),
    ("AFLW", "https://www.afl.com.au/aflw/news/1523395/full-fixture-no-re-match-for-former-melbourne-coach-mick-stinear-at-geelong-west-coast-eagles-get-a-break-by-avoiding-north-melbourne", "2026-10-22T03:05Z",
     "All nine Round 11 matches with venues and local times; Port Adelaide v Collingwood is 7.15pm ACDT."),
    ("Formula 1", "https://www.formula1.com/en/racing/2026/united-states", "2026-10-22T03:25Z",
     "Grand Prix start 16:00 track time on Sunday 25 October; 56 laps over 5.513 km."),
]
