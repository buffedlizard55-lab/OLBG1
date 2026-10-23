#!/usr/bin/env python3
"""Independent selected-excerpt import, 23 Oct 2026. NOT a live scraper.

All projections below were transcribed from actual fetch_page results during the
recorded window. They replace (never re-date) the withdrawn copied first draft.
Excerpts are selected tool-rendered text, NOT original HTTP response bodies.
No prior desk's fixtures, statistics, prices or prose are imported by this code.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION = "455acb16"
OBSERVED_AFTER = "2026-10-23T21:34:10Z"
OBSERVED_BEFORE = "2026-10-23T21:44:36Z"
# These are source-observation bounds, not a claim of per-request timestamps.
SPORTS = [
    ("golf", "Golf", 5, "Golf", "pga-schedule"),
    ("volleyball", "Volleyball", 21, "Volleyball", "lega-calendar"),
    ("rugby-union", "Rugby Union", 9, "Rugby_Union", "urc-calendar"),
    ("cricket", "Cricket", 7, "Cricket", "nzc-fixtures"),
    ("snooker", "Snooker", 8, "Snooker", "wst-matches"),
    ("darts", "Darts", 15, "Darts", "pdc-hub"),
    ("baseball", "Baseball", 12, "Baseball", "mlb-schedule"),
    ("gaelic-sports", "Gaelic Sports", 25, "Gaelic_Football", "munster-calendar"),
    ("greyhounds", "Greyhounds", 28, "Greyhounds", "gbgb-calendar"),
    ("tennis", "Tennis", 3, "Tennis", "atp-almaty"),
    ("motor-racing", "Motor Racing", 14, "Motor_Racing", "f1-hub"),
    ("handball", "Handball", 20, "Handball", "lnh-calendar"),
    ("ice-hockey", "Ice Hockey", 13, "Ice_Hockey", "nhl-schedule"),
    ("basketball", "Basketball", 4, "Basketball", "nba-news"),
    ("rugby-league", "Rugby League", 10, "Rugby_League", "nrl-men"),
]
SPORT_ORDER = [r[0] for r in SPORTS]
SPORT_NAMES = {r[0]: r[1] for r in SPORTS}
OLBG_HUBS = {r[0]: f"https://www.olbg.com/betting-tips/{r[3]}/{r[2]}" for r in SPORTS}
# The current brief says Gaelic Sports, not only Gaelic Football. A fresh read
# of /Hurling/26 explicitly says OLBG's Gaelic Sports competitions cover both
# Football and Hurling. They share ONE category here; their scoring rules must
# never be pooled. Hybrid shinty/camogie entries are not imported as hurling.
EXCLUDED_IDS = [1, 2, 11, 16, 17, 18, 22, 23]
OFFICIAL_HOSTS = {
    "api-web.nhle.com", "www.nhl.com", "statsapi.mlb.com", "www.nba.com", "cdn.nba.com",
    "www.atptour.com", "wtafiles.wtatennis.com", "www.wst.tv", "www.pdc.tv",
    "www.unitedrugby.com", "scoring.nzc.nz", "www.lnh.fr", "munster.gaa.ie",
    "www.legavolley.it", "www.plusliga.pl", "www.tauronliga.pl", "www.pgatour.com", "www.gbgb.org.uk",
    "www.formula1.com", "www.nrl.com", "www.euroleaguebasketball.net",
}

MLB_SCHEDULE = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-30&fields=dates,date,games,gamePk,gameType,season,gameDate,status,detailedState,startTimeTBD,teams,away,home,team,id,name,venue,seriesGameNumber,description,ifNecessary"
MLB_STATS = "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason&fields=records,standingsType,teamRecords,team,id,name,season,gamesPlayed,wins,losses,runsScored,runsAllowed,lastUpdated"


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def observation(sid, publisher, url, chunks, excerpt, *, projection=None, resolved_url=None, role="official", note=""):
    value = {
        "id": sid, "publisher": publisher, "role": role, "url": url,
        "resolved_url": resolved_url or url, "channel": "fetch_page",
        "observed_after": OBSERVED_AFTER, "observed_before": OBSERVED_BEFORE,
        "chunks_read": chunks, "retention": "Selected excerpt and field projection from tool-rendered Markdown; not original HTTP bytes.",
        "http_status": None, "excerpt": excerpt, "projection": projection or {}, "note": note,
    }
    value["content_sha256"] = digest({"excerpt": value["excerpt"], "projection": value["projection"]})
    return value


def fact_row(fid, sport, competition, a, b, date, *, start=None, venue=None, status=None,
             clock=None, event=None, season=None, a_id=None, b_id=None, kind="match", conditional=None, note=""):
    return {
        "id": fid, "sport": sport, "kind": kind, "competition": competition,
        "event": event, "participant_a": a, "participant_b": b,
        "participant_a_id": a_id, "participant_b_id": b_id,
        "source_date": date, "published_clock": clock, "start_utc": start,
        "venue": venue, "official_status": status, "season": season,
        "if_necessary": conditional, "source_note": note,
    }


def selected_observations():
    """Fixed manual transcription. Calling this cannot renew a source's lifetime."""
    obs = []
    nhl_games = [
        # IDs, venue, season, FUT and exact UTC were all present in chunks 0–3.
        (2026020166, "2026-10-24T00:00:00Z", 8, "Montréal Canadiens", 16, "Chicago Blackhawks", "United Center"),
        (2026020167, "2026-10-24T01:00:00Z", 14, "Tampa Bay Lightning", 21, "Colorado Avalanche", "Ball Arena"),
        (2026020168, "2026-10-24T17:00:00Z", 24, "Anaheim Ducks", 4, "Philadelphia Flyers", "Xfinity Mobile Arena"),
        (2026020169, "2026-10-24T19:30:00Z", 26, "Los Angeles Kings", 1, "New Jersey Devils", "Prudential Center"),
        (2026020170, "2026-10-24T23:00:00Z", 28, "San Jose Sharks", 6, "Boston Bruins", "TD Garden"),
        (2026020171, "2026-10-24T23:00:00Z", 3, "New York Rangers", 9, "Ottawa Senators", "Canadian Tire Centre"),
        (2026020172, "2026-10-24T23:00:00Z", 18, "Nashville Predators", 5, "Pittsburgh Penguins", "PPG Paints Arena"),
        (2026020173, "2026-10-24T23:00:00Z", 7, "Buffalo Sabres", 15, "Washington Capitals", "Capital One Arena"),
        (2026020174, "2026-10-24T23:00:00Z", 54, "Vegas Golden Knights", 29, "Columbus Blue Jackets", "Nationwide Arena"),
        (2026020175, "2026-10-24T23:00:00Z", 12, "Carolina Hurricanes", 19, "St. Louis Blues", "Enterprise Center"),
        (2026020176, "2026-10-24T23:00:00Z", 10, "Toronto Maple Leafs", 22, "Edmonton Oilers", "Rogers Place"),
        (2026020177, "2026-10-25T01:00:00Z", 14, "Tampa Bay Lightning", 68, "Utah Mammoth", "Delta Center"),
        (2026020178, "2026-10-25T02:00:00Z", 17, "Detroit Red Wings", 20, "Calgary Flames", "Scotiabank Saddledome"),
        (2026020179, "2026-10-25T02:00:00Z", 30, "Minnesota Wild", 55, "Seattle Kraken", "Climate Pledge Arena"),
    ]
    fixtures = [fact_row(f"nhl-{gid}", "ice-hockey", "NHL", a, b,
                "2026-10-23" if gid <= 2026020167 else "2026-10-24", start=t, venue=v,
                status="FUT", season=20262027, a_id=ai, b_id=bi) for gid, t, ai, a, bi, b, v in nhl_games]
    obs.append(observation("nhl-schedule", "NHL", "https://api-web.nhle.com/v1/schedule/2026-10-23", [0,1,2,3],
        '"date":"2026-10-23","dayAbbrev":"FRI","numberOfGames":2; "date":"2026-10-24","dayAbbrev":"SAT","numberOfGames":12; "id":2026020166,"season":20262027; "startTimeUTC":"2026-10-24T00:00:00Z"; "gameState":"FUT","gameScheduleState":"OK"',
        projection={"fixtures": fixtures}, note="Only league dates 23 and 24 October projected. The remaining returned week was not fully read; no zero-fixture or full-week claim."))

    # Table projection: GP, W, L, OT, PTS, GF, GA. No points-percentage proxy.
    records = [
        (6,"Boston Bruins",11,8,2,1,17,42,22,"7-2-1","W1"),
        (14,"Tampa Bay Lightning",9,7,2,0,14,31,23,"7-2-0","W3"),
        (9,"Ottawa Senators",11,7,4,0,14,31,30,"6-4-0","L1"),
        (12,"Carolina Hurricanes",12,8,2,2,18,47,33,"8-1-1","OT1"),
        (3,"New York Rangers",12,7,4,1,15,37,29,"6-3-1","L1"),
        (10,"Toronto Maple Leafs",12,6,4,2,14,43,39,"5-3-2","W3"),
        (1,"New Jersey Devils",10,6,4,0,12,33,31,"6-4-0","W2"),
        (8,"Montréal Canadiens",9,4,3,2,10,30,34,"4-3-2","OT1"),
        (7,"Buffalo Sabres",10,4,4,2,10,28,37,"4-4-2","L1"),
        (5,"Pittsburgh Penguins",11,4,6,1,9,37,38,"3-6-1","W1"),
        (4,"Philadelphia Flyers",12,3,6,3,9,20,37,"3-5-2","W3"),
        (29,"Columbus Blue Jackets",8,3,5,0,6,20,29,"3-5-0","L2"),
        (15,"Washington Capitals",9,5,4,0,10,30,29,"5-4-0","L1"),
        (68,"Utah Mammoth",11,7,4,0,14,41,36,"6-4-0","L1"),
        (30,"Minnesota Wild",11,6,3,2,14,32,27,"5-3-2","L1"),
        (22,"Edmonton Oilers",10,8,1,1,17,47,32,"8-1-1","W3"),
        (54,"Vegas Golden Knights",12,8,4,0,16,46,36,"7-3-0","L2"),
        (55,"Seattle Kraken",11,7,3,1,15,44,37,"6-3-1","W2"),
        (28,"San Jose Sharks",11,6,4,1,13,33,37,"5-4-1","W2"),
        (21,"Colorado Avalanche",10,5,4,1,11,41,31,"5-4-1","L2"),
        (19,"St. Louis Blues",10,5,4,1,11,35,31,"5-4-1","W2"),
        (18,"Nashville Predators",9,3,3,3,9,23,30,"3-3-3","L1"),
        (24,"Anaheim Ducks",10,4,6,0,8,27,33,"4-6-0","L5"),
        (26,"Los Angeles Kings",8,2,4,2,6,20,29,"2-4-2","W2"),
        (20,"Calgary Flames",9,3,6,0,6,19,38,"3-6-0","W2"),
        (17,"Detroit Red Wings",10,4,3,3,11,28,30,"4-3-3","W1"),
        (16,"Chicago Blackhawks",9,3,6,0,6,21,36,"3-6-0","L1"),
    ]
    stats = [{"id": f"nhl-stat-{tid}", "competition": "NHL", "season": 20262027, "team_id": tid,
              "team": name, "games_played": gp, "wins": w, "losses": l, "ot_losses": ot,
              "points": pts, "goals_for": gf, "goals_against": ga, "last_ten": l10, "streak": streak,
              "as_of": "2026-10-23", "period": "2026-27 regular season to date"}
             for tid,name,gp,w,l,ot,pts,gf,ga,l10,streak in records]
    obs.append(observation("nhl-standings", "NHL", "https://www.nhl.com/standings/2026-10-23/wildcard", [0,1],
        "GP - Games Played; W - Wins (worth two points); L - Losses (worth zero points); OT - OT/Shootout losses (worth one point).\nBoston Bruins | 11 | 8 | 2 | 1 | 17 | .773 | 7 | 8 | 42 | 22\nChicago Blackhawks | 9 | 3 | 6 | 0 | 6 | .333 | 2 | 3 | 21 | 36\nStandings update after each game ends and are current as of Oct 23, 5:31 PM EDT",
        projection={"statistics": stats}, note="27 rows needed by the selected schedule, transcribed from the official table; team IDs joined to the same exact identities in the NHL schedule."))
    obs.append(observation("nhl-suzuki", "NHL", "https://www.nhl.com/news/montreal-canadiens-nick-suzuki-injury-status-update-october-22-2026", [0],
        "Nick Suzuki will be out 2-4 weeks for the Montreal Canadiens because of an upper-body injury, ending his ironman streak.",
        projection={"injury": {"player": "Nick Suzuki", "team_id": 8, "report_date": "2026-10-22", "body_area": "upper-body", "expected_absence": "2-4 weeks"}},
        note="A dated report, not a complete or constantly polled lineup. No numeric injury adjustment is invented."))
    obs.append(observation("nhl-scoreboard", "NHL", "https://www.nhl.com/scores/2026-10-24", [0],
        "Saturday, October 24\n7:00 PM EDT\nSharks 6-4-1\nBruins 8-2-1\nDavid Pastrnak BOS • #88 • RW\n6 Goals\n10 Assists",
        projection={"player_context": {"David Pastrnak": {"team_id": 6, "goals": 6, "assists": 10}}},
        note="Only the first chunk of the score page read; not a full scoreboard import."))

    mlb_fixtures=[]
    for gid, num, date, t, away, home, venue, cond, state in [
        (849805,1,"2026-10-23","2026-10-24T00:00:00Z",139,158,"American Family Field","N","Pre-Game"),
        (849802,2,"2026-10-24","2026-10-25T00:00:00Z",139,158,"American Family Field","N","Scheduled"),
        (849804,3,"2026-10-26","2026-10-27T00:00:00Z",158,139,"Tropicana Field","N","Scheduled"),
        (849803,4,"2026-10-27","2026-10-28T00:00:00Z",158,139,"Tropicana Field","N","Scheduled"),
        (849799,5,"2026-10-28","2026-10-29T00:00:00Z",158,139,"Tropicana Field","Y","Scheduled"),
        (849801,6,"2026-10-30","2026-10-31T00:00:00Z",139,158,"American Family Field","Y","Scheduled"),
    ]:
        names={139:"Tampa Bay Rays",158:"Milwaukee Brewers"}
        mlb_fixtures.append(fact_row(f"mlb-{gid}","baseball","MLB",names[away],names[home],date,
              start=t,venue=venue,status=state,season="2026",a_id=away,b_id=home,conditional=cond,event=f"World Series Game {num}"))
    obs.append(observation("mlb-schedule","MLB",MLB_SCHEDULE,[0],
        '"gamePk":849805,"gameType":"W","season":"2026","gameDate":"2026-10-24T00:00:00Z","status":{"detailedState":"Pre-Game","startTimeTBD":false}; "description":"World Series Game 5","seriesGameNumber":5,"ifNecessary":"Y"',
        projection={"fixtures":mlb_fixtures},note="Game 6 lies outside the exact rolling seven-day window and is conditional. Neither conditional game is priced."))
    mlb_stats=[
        {"id":"mlb-stat-139","competition":"MLB","season":"2026","team_id":139,"team":"Tampa Bay Rays","games_played":162,"wins":98,"losses":64,"runs_scored":736,"runs_allowed":650,"period":"2026 regular season only","as_of":"2026 regular season","provider_last_updated":"2026-10-23T20:52:56Z"},
        {"id":"mlb-stat-158","competition":"MLB","season":"2026","team_id":158,"team":"Milwaukee Brewers","games_played":162,"wins":103,"losses":59,"runs_scored":832,"runs_allowed":618,"period":"2026 regular season only","as_of":"2026 regular season","provider_last_updated":"2026-10-06T00:15:51Z"},
    ]
    obs.append(observation("mlb-standings","MLB",MLB_STATS,[0,2],
        '"team":{"id":139,"name":"Rays"},"season":"2026","gamesPlayed":162; "runsAllowed":650,"runsScored":736,"wins":98,"losses":64\n"team":{"id":158,"name":"Brewers"},"season":"2026","gamesPlayed":162,"lastUpdated":"2026-10-06T00:15:51Z"; "runsAllowed":618,"runsScored":832,"wins":103,"losses":59',
        projection={"statistics":mlb_stats},note="Selected team records in chunks 0 and 2, not every team. Original provider update timestamps preserved. Completed regular-season aggregates are not postseason form. Projection correction: an earlier common-schema OTL zero was not an official MLB field and has been removed; the NHL-only category is not applicable to MLB. This does not change the observation bounds or run-rate calculations."))

    def calendar(sid,publisher,url,chunks,excerpt,rows,note="",resolved_url=None):
        obs.append(observation(sid,publisher,url,chunks,excerpt,projection={"fixtures":rows},note=note,resolved_url=resolved_url))
    calendar("atp-almaty","ATP", "https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule",[0],
        "Sat, 24 October, 2026 (Day 8)\nCenter Court Starts At 12:00\nL. Miedler / N. Oberleitner (1) Vs (3) N. Balaji / E. King\nNot Before 15:00\nN. Basilashvili (Q) Vs (7) S. Tsitsipas\nNot Before 18:00\nD. Medvedev (1) Vs (3) A. Bublik", [
            fact_row("atp-almaty-doubles","tennis","ATP Almaty","L. Miedler / N. Oberleitner","N. Balaji / E. King","2026-10-24",clock="Starts at 12:00",venue="Center Court",event="Doubles semi-final"),
            fact_row("atp-almaty-sf1","tennis","ATP Almaty","N. Basilashvili","S. Tsitsipas","2026-10-24",clock="Not before 15:00",venue="Center Court",event="Singles semi-final"),
            fact_row("atp-almaty-sf2","tennis","ATP Almaty","D. Medvedev","A. Bublik","2026-10-24",clock="Not before 18:00",venue="Center Court",event="Singles semi-final"),
        ], "Use Local Time Zone switch present. No explicit timezone in excerpt; Not Before is a bound, never an exact start.")
    calendar("atp-brussels","ATP","https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule",[0],
        "Sat, 24 October, 2026 (Day 8)\nCentre Court Starts At 13:30\nN. Barrientos / D. Pel Vs (4) S. Doumbia / B. Stevens\nNot Before 16:00\nF. Cerundolo (3) Vs T. Griekspoor\nNot Before 18:30\nA. Fils (1) Vs J. Struff",[
            fact_row("atp-brussels-doubles","tennis","ATP Brussels","N. Barrientos / D. Pel","S. Doumbia / B. Stevens","2026-10-24",clock="Starts at 13:30",venue="Centre Court",event="Doubles semi-final"),
            fact_row("atp-brussels-sf1","tennis","ATP Brussels","F. Cerundolo","T. Griekspoor","2026-10-24",clock="Not before 16:00",venue="Centre Court",event="Singles semi-final"),
            fact_row("atp-brussels-sf2","tennis","ATP Brussels","A. Fils","J. Struff","2026-10-24",clock="Not before 18:30",venue="Centre Court",event="Singles semi-final"),
        ], "Source abbreviations preserved; no inferred rankings, current form, exact UTC or current pre-match status.")
    calendar("wta-ningbo-op","WTA","https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",[0],
        "ORDER OF PLAY - SATURDAY, 24 OCTOBER 2026\nStarting at 1:00 PM\nDesirae KRAWCZYK USA Fanny STOLLAR HUN VS Ulrikke EIKERI NOR Quinn GLEASON USA\nNot before 3:00 PM\nSF Laylah FERNANDEZ CAN VS Marie BOUZKOVA CZE\nNot before 5:30 PM\n[1] Elena RYBAKINA KAZ VS [6] Diana SHNAIDER",[
            fact_row("wta-ningbo-doubles","tennis","BNB Ningbo Open","Desirae Krawczyk / Fanny Stollar","Ulrikke Eikeri / Quinn Gleason","2026-10-24",clock="Starting at 1:00 PM",venue="CENTER COURT",event="Doubles"),
            fact_row("wta-ningbo-sf1","tennis","BNB Ningbo Open","Laylah FERNANDEZ","Marie BOUZKOVA","2026-10-24",clock="Not before 3:00 PM",venue="CENTER COURT",event="Semi-final"),
            fact_row("wta-ningbo-sf2","tennis","BNB Ningbo Open","Elena RYBAKINA","Diana SHNAIDER","2026-10-24",clock="Not before 5:30 PM",venue="CENTER COURT",event="Semi-final"),
        ], "Official sheet spells Laylah; preserved as published, not an identity correction from memory. No exact UTC. The previous Kostyuk pairing is not imported.")
    obs.append(observation("wta-ningbo-draw","WTA","https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf",[0],
        "M. Kostyuk Right Wrist Injury\nRELEASED\n23 Oct 2026 10:00 PM",
        projection={"availability_note":"M. Kostyuk Right Wrist Injury"},note="Supports a withdrawal/availability review. Order of play is used for upcoming pairings; bracket alone is not reconstructed into future opponents."))
    calendar("wta-osaka-op","WTA","https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf",[0],
        "ORDER OF PLAY - SATURDAY, 24 OCTOBER 2026\nStarting at 12:00 PM\nSF\n[1] Ann LI USA VS Ashlyn KRUEGER USA\nNot before 1:30 PM\nSF\n[8] Katie BOULTER GBR VS Katerina SINIAKOVA CZE\nPossible Court Change\nF\n[1] Storm HUNTER AUS Janice TJEN INA VS Jesika MALECKOVA CZE Miriam SKOCH CZE",[
            fact_row("wta-osaka-sf1","tennis","Kinoshita Group Japan Open","Ann LI","Ashlyn KRUEGER","2026-10-24",clock="Starting at 12:00 PM",venue="CENTER",event="Semi-final"),
            fact_row("wta-osaka-sf2","tennis","Kinoshita Group Japan Open","Katie BOULTER","Katerina SINIAKOVA","2026-10-24",clock="Not before 1:30 PM",venue="CENTER",event="Semi-final"),
            fact_row("wta-osaka-doubles","tennis","Kinoshita Group Japan Open","Storm HUNTER / Janice TJEN","Jesika MALECKOVA / Miriam SKOCH","2026-10-24",clock="Possible Court Change; follows preceding listing",event="Doubles final"),
        ], "No exact UTC is stated. Li–Boulter from the withdrawn draft is contradicted by this order of play.")
    obs.append(observation("atp-lyon-check","ATP","https://www.atptour.com/en/scores/current/lyon/496/daily-schedule",[0],
        "Fri, 23 October, 2026 (Day 6)\nT. Paul (4) Defeats C. Moutet\n64 36 63\nT. Fritz (2) Defeats D. Altmaier\n765 62\nF. Cobolli (1) Defeats (5) B. Nakashima\n46 64 64",
        note="Read contains Friday results, not Saturday pairings. No Lyon semi-final opponents inferred."))

    pdc_pairs=[("Cameron Menzies","Gerwyn Price","07:15"),("Stephen Bunting","Kim Huybrechts","08:15"),
        ("Ross Smith","Damon Heta","09:15"),("Gian van Veen","Luke Woodhouse","10:15"),
        ("Krzysztof Ratajski","Kevin Doets","13:15"),("Martin Schindler","Jermaine Wattimena","14:15"),
        ("Nathan Aspinall","Luke Littler","15:15"),("Jonny Clayton","Josh Rock","16:15")]
    calendar("pdc-hub","PDC","https://www.pdc.tv/tournament-hub/10870",[0,5,6,7],
        "Last 16\nSat 24 Oct\n07:15 Cameron Menzies - Gerwyn Price -\n08:15 Stephen Bunting - Kim Huybrechts -\n09:15 Ross Smith - Damon Heta -\n10:15 Gian van Veen - Luke Woodhouse -\n13:15 Krzysztof Ratajski - Kevin Doets -\n14:15 Martin Schindler - Jermaine Wattimena -\n15:15 Nathan Aspinall - Luke Littler -\n16:15 Jonny Clayton - Josh Rock -",
        [fact_row(f"pdc-r16-{i}","darts","PDC European Championship",a,b,"2026-10-24",clock=t,event="Last 16") for i,(a,b,t) in enumerate(pdc_pairs,1)],
        "Sporting text in chunk 6 follows the consent notice. Times have no timezone label. Rankings, leg-winning rates and market availability were not established.")
    calendar("wst-matches","World Snooker Tour","https://www.wst.tv/matches/",[0,2,3],
        "Scheduled\nSemi Finals\n08:00\nSat 24 Oct\nMatch 61\nKyren Wilson\nSam Craigie\n14:00\nSat 24 Oct\nMatch 62\nWinner of match 59\nWinner of match 60\nScheduled\nFinal\n08:00\nSun 25 Oct\nMatch 63\nWinner of match 61\nWinner of match 62",[
            fact_row("wst-61","snooker","BetVictor Northern Ireland Open 2026","Kyren Wilson","Sam Craigie","2026-10-24",clock="08:00",status="Scheduled",event="Semi-final, match 61"),
            fact_row("wst-62","snooker","BetVictor Northern Ireland Open 2026",None,None,"2026-10-24",clock="14:00",status="Scheduled",event="Semi-final, match 62",note="Winner of match 59 v winner of match 60; participants not inferred."),
            fact_row("wst-63","snooker","BetVictor Northern Ireland Open 2026",None,None,"2026-10-25",clock="08:00",status="Scheduled",event="Final, match 63",note="Winner of match 61 v winner of match 62; participants not inferred."),
        ], "Clock timezone absent. Earlier quarter-final results/liveness are not pre-match opportunities.")
    urc_rows=[]
    for i,(a,b,t,v) in enumerate([
        ("Vodacom Bulls","Ulster","12:45 IRE & UK / 13:45 ITA & SA","Loftus Versfeld, Pretoria"),
        ("DHL Stormers","Scarlets","15:00 IRE & UK / 16:00 ITA & SA","DHL Stadium, Cape Town"),
        ("Benetton","Glasgow Warriors","15:00 IRE & UK / 16:00 ITA & SA","Stadio Monigo, Treviso"),
        ("Leinster","Munster","18:00 IRE & UK / 19:00 ITA & SA",None),
        ("Ospreys","Dragons","19:45 IRE & UK / 20:45 ITA & SA","St. Helen’s, Swansea"),
    ],1):
        urc_rows.append(fact_row(f"urc-r4-{i}","rugby-union","United Rugby Championship",a,b,"2026-10-24",clock=t,venue=v,event="Round 4"))
    calendar("urc-calendar","United Rugby Championship","https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/",[0],
        "ROUND 4\nSATURDAY, OCTOBER 24\nVodacom Bulls v Ulster\nLoftus Versfeld, Pretoria, KO 12.45 IRE & UK / 13.45 ITA & SA\nDHL Stormers v Scarlets\nDHL Stadium, Cape Town, KO 15.00 IRE & UK / 16.00 ITA & SA\nBenetton v Glasgow Warriors\nStadio Monigo, Treviso, KO 15.00 IRE & UK / 16.00 ITA & SA\nLeinster v Munster\nTBC, Dublin, KO 18.00 IRE & UK / 19.00 ITA & SA\nOspreys v Dragons\nSt. Helen’s, Swansea, KO 19.45 IRE & UK / 20.45 ITA & SA",urc_rows,
        "Season fixture publication, not a current status feed. Venue TBC remains null for Leinster–Munster. Exact UTC left blank rather than treating the long-range calendar as a fresh status check.")
    nzc_data=[
        ("nzc-t20-2","BLACKCAPS","India","2026-10-24","3:00am","Hagley Oval, Christchurch","2nd T20I"),
        ("nzc-t20-3","BLACKCAPS","India","2026-10-27","3:00am","Hnry Stadium, Wellington","3rd T20I"),
        ("nzc-ft-1","Auckland Aces","Canterbury","2026-10-27","5:30pm","Kennards Hire Community Oval, Auckland","Ford Trophy Round 1"),
        ("nzc-ft-2","Central Stags","Northern Districts","2026-10-27","5:30pm","Saxton Oval, Nelson","Ford Trophy Round 1"),
        ("nzc-ft-3","Wellington Firebirds","Otago Volts","2026-10-27","5:30pm","Cello Basin Reserve, Wellington","Ford Trophy Round 1"),
    ]
    calendar("nzc-fixtures","New Zealand Cricket","https://scoring.nzc.nz/fixtures",[0],
        "SAT24 Oct\nBLACKCAPS\nIndia\n3:00am\nHagley Oval, Christchurch\nIndia in New Zealand - 2nd T20I\nTUE27 Oct\nBLACKCAPS\nIndia\n3:00am\nHnry Stadium, Wellington\nAuckland Aces / Canterbury / 5:30pm / Kennards Hire Community Oval, Auckland\nCentral Stags / Northern Districts / 5:30pm / Saxton Oval, Nelson\nWellington Firebirds / Otago Volts / 5:30pm / Cello Basin Reserve, Wellington",
        [fact_row(fid,"cricket","NZC",a,b,d,clock=t,venue=v,event=e) for fid,a,b,d,t,v,e in nzc_data],
        "The display timezone is not labelled. These are source-calendar dates and clocks, NOT converted UTC. Multi-day A-team match already listed Friday is not offered as a fresh upcoming match. Other dates/competitions remain incomplete.")
    calendar("lnh-calendar","Ligue Nationale de Handball","https://www.lnh.fr/liquimoly-starligue/calendrier",[0,1],
        "Daikin StarLigue - J08\nsam. 24 oct. 19h00\nNantes vs Chambéry\ndim. 25 oct. 16h00\nSaint-Raphaël vs Paris\ndim. 25 oct. 17h00\nMontpellier vs Saran",[
            fact_row("lnh-j8-nantes","handball","Daikin StarLigue","Nantes","Chambéry","2026-10-24",clock="19h00",event="J08"),
            fact_row("lnh-j8-paris","handball","Daikin StarLigue","Saint-Raphaël","Paris","2026-10-25",clock="16h00",event="J08"),
            fact_row("lnh-j8-montpellier","handball","Daikin StarLigue","Montpellier","Saran","2026-10-25",clock="17h00",event="J08"),
        ], "Venue and timezone not confirmed in the selected match rows. Friday score-bearing rows are excluded from pre-match research.",resolved_url="https://www.lnh.fr/daikin-starligue/calendrier")
    calendar("munster-calendar","Munster GAA","https://munster.gaa.ie/fixtures/events-calendar/",[0,1],
        "2026 Kerry County Senior Football Championship Final – Dr. Crokes v Kenmare Shamrocks\nStarts:Sun, Oct 25, 2026 @ 2:00pm\nFitzgerald Stadium\n2026 Waterford Senior Football Championship Final – Rathgormack v The Nire\nStarts:Sun, Oct 25, 2026 @ 2:30pm\nCappoquin Logistics Fraher Field, Dungarvan\n2026 Cork Premier Senior Football Championship Final – St Finbarrs v Nemo Rangers\nStarts:Sun, Oct 25, 2026 @ 4:00pm\nSuperValu Páirc Uí Chaoimh\n2026 Limerick Senior Hurling Championship Final – Na Piarsaigh v Kilmallock\nStarts:Sun, Oct 25, 2026 @ 3:45pm\nTUS Gaelic Grounds",[
            fact_row("gaa-kerry-final","gaelic-sports","Kerry Senior Football Championship","Dr. Crokes","Kenmare Shamrocks","2026-10-25",clock="2:00pm",venue="Fitzgerald Stadium",event="Final"),
            fact_row("gaa-waterford-final","gaelic-sports","Waterford Senior Football Championship","Rathgormack","The Nire","2026-10-25",clock="2:30pm",venue="Cappoquin Logistics Fraher Field, Dungarvan",event="Final"),
            fact_row("gaa-cork-final","gaelic-sports","Cork Premier Senior Football Championship","St Finbarrs","Nemo Rangers","2026-10-25",clock="4:00pm",venue="SuperValu Páirc Uí Chaoimh",event="Final"),
            fact_row("gaa-limerick-hurling","gaelic-sports","Limerick Senior Hurling Championship","Na Piarsaigh","Kilmallock","2026-10-25",clock="3:45pm",venue="TUS Gaelic Grounds, Limerick",event="Final"),
        ], "Football and hurling kept in one Gaelic Sports category but different competitions. Hybrid camogie/shinty entries excluded. No club strength or form is invented. Clock timezone absent.")
    lega_matches=[
        (7,"Sir Susa Scai Perugia","Tinet Prata di Pordenone","2026-10-25","18:00","Pala Barton Energy, Perugia"),
        (8,"Itas Trentino","Cisterna Volley","2026-10-25","17:00","BTS Arena, Trento"),
        (9,"Gas Sales Bluenergy Piacenza","Valsa Group Modena","2026-10-25","18:00","PalaBancaSport, Piacenza"),
        (10,"Cucine Lube Civitanova","Pallavolo Padova","2026-10-25","18:00","Eurosuole Forum, Civitanova Marche"),
        (11,"Allianz Milano","Acqua Sant'Anna Cuneo","2026-10-25","19:00","Allianz Cloud (Palalido), Milano"),
        (12,"Vero Volley Monza","Rana Verona","2026-10-25","18:00","OpiquadArena, Monza"),
        (61,"Sir Susa Scai Perugia","Pallavolo Padova","2026-10-28","20:30","Pala Barton Energy, Perugia"),
    ]
    calendar("lega-calendar","Lega Pallavolo Serie A","https://www.legavolley.it/calendario/?idCampionato=999",[0,1,2,3,4,5],
        "Regular Season SuperLega Credem Banca\n2ª Giornata Andata - Domenica 25 Ottobre 2026 Ore 18:00\n7 | Domenica 25/10/2026 Ore 18:00 | Sir Susa Scai Perugia | 0-0 | Tinet Prata di Pordenone\n8 | Domenica 25/10/2026 Ore 17:00 | Itas Trentino | 0-0 | Cisterna Volley\n9 | Domenica 25/10/2026 Ore 18:00 | Gas Sales Bluenergy Piacenza | 0-0 | Valsa Group Modena\n10 | Domenica 25/10/2026 Ore 18:00 | Cucine Lube Civitanova | 0-0 | Pallavolo Padova\n11 | Domenica 25/10/2026 Ore 19:00 | Allianz Milano | 0-0 | Acqua Sant'Anna Cuneo\n12 | Domenica 25/10/2026 Ore 18:00 | Vero Volley Monza | 0-0 | Rana Verona\n61 | Mercoledí 28/10/2026 Ore 20:30 | Sir Susa Scai Perugia | 0-0 | Pallavolo Padova",
        [fact_row(f"lega-{i}","volleyball","SuperLega Credem Banca",a,b,d,clock=t,venue=v,event="Regular season") for i,a,b,d,t,v in lega_matches],
        "Calendar 0-0 placeholders are not results or proof of current pre-match state. No exact timezone published in selected table; statistics not sufficient for pricing.")
    obs.append(observation("plusliga-redirect","Polish volleyball league","https://www.plusliga.pl/games.html",[0],
        "Mecze - Sezon 2026/2027 - TAURON Liga\nPGE GiEK SKRA Bełchatów\nAsseco Resovia Rzeszów",
        resolved_url="https://www.tauronliga.pl/games.html",note="Redirect and competition-identity irregularity. No Polish fixtures or statistics imported from this conflicting response."))
    calendar("pga-schedule","PGA TOUR","https://www.pgatour.com/schedule",[0,4,5],
        "OCT 22 - 25\nButterfield Bermuda Championship\nPort Royal Golf Course\nSouthampton • Bermuda\nOCT 29 - NOV 1\nVidantaWorld Mexico Open\nVidanta Vallarta\nVallarta • Mexico",[
            fact_row("pga-bermuda","golf","PGA TOUR",None,None,"2026-10-22",venue="Port Royal Golf Course, Southampton, Bermuda",event="Butterfield Bermuda Championship · 22–25 Oct",kind="field-event",status="R2 Complete"),
            fact_row("pga-mexico","golf","PGA TOUR",None,None,"2026-10-29",venue="Vidanta Vallarta, Vallarta, Mexico",event="VidantaWorld Mexico Open · 29 Oct–1 Nov",kind="field-event"),
        ], "Current tournament and next event calendar only; no artificial H2H between two golfers. R2 Complete comes from the leaderboard widget in chunk 5. Full field, withdrawals, tee times and matchup availability unconfirmed.")
    calendar("gbgb-calendar","Greyhound Board of Great Britain","https://www.gbgb.org.uk/racing/open-races/2025-category-one-schedule/",[0],
        "2026 Category One Schedule\nFri 23 Oct | Romford | Premier Greyhound Racing Champion Stakes | | 575m Flat\nSat 24 Oct | Dunstall Park | Arena Racng Company Scurry Gold Cup | | 270m Flat\nSat 24 Oct | Dunstall Park | Premier Greyhound Racing Oaks | | 480m Flat",[
            fact_row("gbgb-champion-stakes","greyhounds","GBGB Category One",None,None,"2026-10-23",venue="Romford",event="Premier Greyhound Racing Champion Stakes · 575m",kind="field-event"),
            fact_row("gbgb-scurry","greyhounds","GBGB Category One",None,None,"2026-10-24",venue="Dunstall Park",event="Scurry Gold Cup · 270m",kind="field-event"),
            fact_row("gbgb-oaks","greyhounds","GBGB Category One",None,None,"2026-10-24",venue="Dunstall Park",event="Premier Greyhound Racing Oaks · 480m",kind="field-event"),
        ], "Page URL retains 2025 but heading is 2026. Only final-event calendar, not individual racecards, runners, traps, or scratchings. Friday race may already be elapsed; not declared upcoming.")
    obs.append(observation("gbgb-races-check","Greyhound Board of Great Britain","https://www.gbgb.org.uk/racing/open-races/",[0],
        "Open Races\n2026 Category One Schedule\nFilter the results by entering the dates or types of races you want to see.",note="Interactive filters rendered, not individual racecards. Not evidence of zero races."))
    calendar("f1-hub","Formula 1","https://www.formula1.com/en/racing/2026/united-states",[0],
        "FORMULA 1 MSC CRUISES UNITED STATES GRAND PRIX 2026\nMY TIME17:30 TRACK TIME16:30\n24Oct Qualifying17:00 - 18:00\n25Oct Race16:00\nCircuit Length5.513km\nNumber of Laps56\nRace Distance308.432km",[
            fact_row("f1-usgp-quali","motor-racing","Formula 1",None,None,"2026-10-24",clock="Qualifying 17:00–18:00 (display mode unconfirmed)",event="United States Grand Prix qualifying",kind="field-event"),
            fact_row("f1-usgp-race","motor-racing","Formula 1",None,None,"2026-10-25",clock="Race 16:00 (display mode unconfirmed)",event="United States Grand Prix",kind="field-event"),
        ], "My time / Track time mode is ambiguous in extraction. No UTC, complete field or finishing probabilities inferred. Two sessions of one GP are not counted as two of five independent matches for a quota.")
    men=[("png-samoa","Papua New Guinea","Samoa","2026-10-24","12:25am","Santos National Football Stadium, Port Moresby"),
         ("eng-france","England","France","2026-10-24","2:35am","HBF Park, Perth"),
         ("nz-cook","New Zealand","Cook Islands","2026-10-25","1:05am","One NZ Stadium, Christchurch"),
         ("aus-fiji","Australia","Fiji","2026-10-25","5:05am","Suncorp Stadium, Brisbane")]
    calendar("nrl-men","NRL","https://www.nrl.com/draw/?competition=131&round=2&season=2026",[0],
        "Rugby League World Cup\nRound 2\nTonga vs Lebanon\nFriday 23rd October\nFull Time\n36 points / 0 points\nPapua New Guinea vs Samoa / Saturday 24th October / Kick off:12:25am\nEngland vs France / Saturday 24th October / Kick off:2:35am\nNew Zealand vs Cook Islands / Sunday 25th October / Kick off:1:05am\nAustralia vs Fiji / Sunday 25th October / Kick off:5:05am",
        [fact_row("rl-"+fid,"rugby-league","Rugby League World Cup",a,b,d,clock=t,venue=v,event="Men's Round 2") for fid,a,b,d,t,v in men],
        "Position values on this page are not international strength ratings. Display timezone absent. No 0-point placeholders treated as played results; Tonga–Lebanon full-time excluded.")
    women=[("fiji-png","Fiji","Papua New Guinea","2026-10-23","10:15pm","Santos National Football Stadium, Port Moresby"),
           ("aus-eng","Australia","England","2026-10-24","5:05am","HBF Park, Perth"),
           ("nz-france","New Zealand","France","2026-10-24","11:00pm","One NZ Stadium, Christchurch")]
    calendar("nrl-women","NRL","https://www.nrl.com/draw/womens-rugby-league-world-cup/2026/round-2/",[0],
        "Women's Rugby League World Cup\nRound 2\nSamoa vs Wales / Friday 23rd October / Full Time / 76 points / 0 points\nFiji vs Papua New Guinea / Friday 23rd October / Kick off:10:15pm\nAustralia vs England / Saturday 24th October / Kick off:5:05am\nNew Zealand vs France / Saturday 24th October / Kick off:11:00pm",
        [fact_row("rlw-"+fid,"rugby-league","Women's Rugby League World Cup",a,b,d,clock=t,venue=v,event="Women's Round 2") for fid,a,b,d,t,v in women],
        "Unlabelled timezone retained as published; no conversion or claim that Friday's listing remains upcoming.",resolved_url="https://www.nrl.com/draw/womens-rugby-league-world-cup/2026/round-2/?competition=157&round=2&season=2026")
    calendar("nba-news","NBA","https://www.nba.com/news/starting-5-october-23-2026",[0],
        "October 23, 2026 11:26 AM\nThe season’s first Prime doubleheader headlines Friday’s 12-game slate, as the Knicks visit the Celtics (7 ET) before a Texas showdown in Austin between the Rockets and Spurs (9:30 ET).\nWizards host the Raptors on League Pass (7 ET).",[
            fact_row("nba-0022600008","basketball","NBA","New York Knicks","Boston Celtics","2026-10-23",clock="7 ET",event="Friday slate"),
            fact_row("nba-0022600009","basketball","NBA","Houston Rockets","San Antonio Spurs","2026-10-23",clock="9:30 ET",event="Friday slate"),
            fact_row("nba-0022600097","basketball","NBA","Toronto Raptors","Washington Wizards","2026-10-23",clock="7 ET",event="Friday slate"),
        ], "Only three schedule pairings from the newsletter; not all 12. Exact UTC and current status left blank until a structured schedule is available. No record or score default from early season.")
    obs.append(observation("nba-games-check","NBA","https://www.nba.com/games?date=2026-10-23",[0],
        "Sorry, something went wrong. Please refresh the page.",note="Calendar says 12 games but cards failed to render. No invented pairings."))
    fail=observation("nba-json-check","NBA","https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json",[0],
        "",note="fetch_page returned Failed to fetch page (HTTP 500). No schedule facts accepted from this attempt.")
    fail["result"]="failed"
    obs.append(fail)
    obs.append(observation("euroleague-results","Euroleague Basketball","https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",[0,1],
        "Friday, October 23, 2026\nZalgiris Kaunas 105-85 LDLC ASVEL Villeurbanne\nOlympiacos Piraeus 61-64 Fenerbahce Tarfin Istanbul\nParis Basketball 93-104 Valencia Basket",
        note="Completed games only in the read. Do not publish the earlier desk's speculative Saturday Round 7 pairings as supported upcoming games."))
    # OLBG is an official source for its own routes/market definitions only, not sporting truth.
    for slug,name,sport_id,route,_ in SPORTS:
        empty = "No tournaments tips found." if slug in ("motor-racing","rugby-league") else "No tips found."
        obs.append(observation("olbg-"+slug,"OLBG",OLBG_HUBS[slug],[0],empty,
            role="discovery",note="Live cards unavailable in the retrieval output. This is an extraction gap, not evidence of no events or closed tips. Exact current submission eligibility remains unverified."))
    obs.append(observation("olbg-hurling","OLBG","https://www.olbg.com/betting-tips/Hurling/26",[0],
        "No tips found.\nGaelic Football and Hurling have been part of OLBG's tipping line-up since early 2019, and there are now two monthly Gaelic Sports tipster competitions to get involved in — both covering Football and Hurling tips:",
        role="discovery",note="Explicit basis for including football and hurling inside the single requested Gaelic Sports category. Live event cards remain unavailable."))
    for sid,url in [("olbg-nhl","https://www.olbg.com/betting-tips/Ice_Hockey/NHL/13"),("olbg-mlb","https://www.olbg.com/betting-tips/Baseball/MLB/12")]:
        obs.append(observation(sid,"OLBG",url,[0],"No tips found.",role="discovery",note="Competition subroute also rendered no live cards; no event IDs enumerated or inferred."))
    obs.append(observation("olbg-robots","OLBG","https://www.olbg.com/robots.txt",[0],
        "User-agent: *\nDisallow: /api/\nDisallow: /storage/app/json_data/*\nUser-agent: Python-urllib\nDisallow: /",role="discovery",note="No restricted API/storage route, agent impersonation or location spoofing used."))
    return obs


def assemble_inputs():
    observations=selected_observations()
    fixtures=[]; statistics=[]
    for src in observations:
        for i,facts in enumerate(src["projection"].get("fixtures", [])):
            fixture=copy.deepcopy(facts)
            fixture["source_ids"]=[src["id"]]
            # A list prevents generic legacy row scanners from mistaking a map of
            # evidence references (id/sport/start_utc refs) for another fixture.
            fixture["field_evidence"]=[{"field":k,"source_id":src["id"],"pointer":f"/projection/fixtures/{i}/{k}"}
                for k,v in facts.items() if v is not None]
            fixture["observed_after"]=src["observed_after"]
            fixture["observed_before"]=src["observed_before"]
            fixture["olbg_event_url"]=None
            fixture["olbg_eligibility"]=None
            fixture["market_quote"]=None
            fixtures.append(fixture)
        for i,record in enumerate(src["projection"].get("statistics", [])):
            record=copy.deepcopy(record)
            record.update(source_id=src["id"],pointer=f"/projection/statistics/{i}",
                observed_after=src["observed_after"],observed_before=src["observed_before"])
            statistics.append(record)
    return observations,fixtures,statistics

if __name__ == "__main__":
    o,f,s=assemble_inputs()
    print(f"Fixed selected import: {len(o)} observations / {len(f)} listings / {len(s)} statistical records. No live refresh claimed.")
