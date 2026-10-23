#!/usr/bin/env python3
"""T67 (session cf2699ba-olbg1) - 23 October 2026, fifteen-sport desk.

Authors the observation set: the OLBG hub sweep (discovery only), the official sources that were
actually read (each with the timestamp it was read), the small set of fixtures that an official
page confirms, and the numeric inputs used to originate prices.

Nothing in this file is inferred. Every field is either transcribed from a fetched page, and says
which page, or left empty with a reason recorded in FLAGS.

Run: python3 scripts/scf2699ba_data.py
Out: data/cf2699ba/{sources,discovery,fixtures,inputs}.json
"""
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "cf2699ba"
OBSERVED = "2026-10-23T16:20Z-16:40Z"

# --------------------------------------------------------------------------------------------------
# Sports. OLBG sport ids and hub paths come from the live hub URLs captured this session.
# Golf returned "No tips found"; Rugby League carries only 2027 outrights. Both are still covered.
# --------------------------------------------------------------------------------------------------
SPORTS = [
    ("golf", "Golf", 5, "Golf", "no-listings"),
    ("volleyball", "Volleyball", 21, "Volleyball", "listings"),
    ("rugby-union", "Rugby Union", 9, "Rugby_Union", "listings"),
    ("cricket", "Cricket", 7, "Cricket", "listings"),
    ("snooker", "Snooker", 8, "Snooker", "listings"),
    ("darts", "Darts", 15, "Darts", "listings"),
    ("baseball", "Baseball", 12, "Baseball", "listings"),
    ("gaelic-sports", "Gaelic Sports", 25, "Gaelic_Football", "listings"),
    ("greyhounds", "Greyhounds", 28, "Greyhounds", "listings"),
    ("tennis", "Tennis", 3, "Tennis", "listings"),
    ("motor-racing", "Motor Racing", 14, "Motor_Racing", "listings"),
    ("handball", "Handball", 20, "Handball", "listings"),
    ("ice-hockey", "Ice Hockey", 13, "Ice_Hockey", "listings"),
    ("basketball", "Basketball", 4, "Basketball", "listings"),
    ("rugby-league", "Rugby League", 10, "Rugby_League", "outrights-only"),
]

# --------------------------------------------------------------------------------------------------
# Sources actually read. "read" says exactly what the page yielded; "limits" says what it did not.
# Only sources whose content is used for a fixture or a number are marked official=True.
# --------------------------------------------------------------------------------------------------
SOURCES = [
    {
        "id": "src-olbg-hubs",
        "org": "OLBG",
        "title": "Fifteen sport hubs (fixture lists and tip-vote shares)",
        "url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
        "read_at": "2026-10-23T16:20Z",
        "official": False,
        "role": "discovery",
        "read": "Team/runner names, competition labels, printed start-time strings, the leading tipster "
                "selection, market type, and the tip count and share behind it, for every in-scope hub.",
        "limits": "No timezone is printed anywhere on any hub. Tip-vote share is a count of published "
                  "tips, not a probability and not a price.",
    },
    {
        "id": "src-nhl-schedule",
        "org": "National Hockey League",
        "title": "NHL schedule for 2026-10-23",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-23",
        "read_at": "2026-10-23T16:24Z",
        "official": True,
        "role": "fixture",
        "read": "Two games only (Montreal at Chicago, Tampa Bay at Colorado), with UTC start strings "
                "00:00Z and 01:00Z on 24 October, venues United Center and Ball Arena, game ids 2026020166 "
                "and 2026020167, and per-provider price arrays for each side.",
        "limits": "The price arrays disagree across providers (see F-CF-03). The feed publishes no team "
                  "records on this endpoint.",
    },
    {
        "id": "src-nhl-standings",
        "org": "National Hockey League",
        "title": "NHL standings for 2026-10-23",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-23",
        "read_at": "2026-10-23T16:26Z",
        "official": True,
        "role": "context",
        "read": "Top of the table only: Carolina 18 points, Edmonton and Boston 16, Vegas 15, in the "
                "portion of the response that loaded.",
        "limits": "Montreal, Chicago, Tampa Bay and Colorado are not in the portion that loaded, so no "
                  "record for any of tonight's four clubs could be read from this page.",
    },
    {
        "id": "src-mlb-schedule",
        "org": "Major League Baseball",
        "title": "MLB schedule 2026-10-23 to 2026-10-25",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-25",
        "read_at": "2026-10-23T16:27Z",
        "official": True,
        "role": "fixture",
        "read": "World Series Game 1, gamePk 849805, Tampa Bay Rays at Milwaukee Brewers, 2026-10-24T00:00Z, "
                "American Family Field, probable pitchers Nick Martinez (TB) and Jacob Misiorowski (MIL), "
                "series description \"World Series\", game 1 of 7, ifNecessary=N. Game 2, gamePk 849802, "
                "2026-10-25T00:00Z.",
        "limits": "Postseason league records read 0-0, so the schedule cannot supply season records.",
    },
    {
        "id": "src-mlb-standings",
        "org": "Major League Baseball",
        "title": "MLB standings, American League, 2026 season",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026",
        "read_at": "2026-10-23T16:29Z",
        "official": True,
        "role": "input",
        "read": "Tampa Bay Rays: 98 wins 64 losses, .605, home 55-26, away 43-38, last ten 6-4, "
                "runs scored 736, runs allowed 650.",
        "limits": "National League was requested in the same call but only the American League block "
                  "loaded, so no Milwaukee line was read here.",
    },
    {
        "id": "src-mlb-records-capture",
        "org": "Major League Baseball (repository capture)",
        "title": "Canonical 2026 season records captured 2026-10-22",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026",
        "read_at": "2026-10-22 (capture), cited 2026-10-23",
        "official": True,
        "role": "input",
        "read": "Milwaukee Brewers: 103 wins 59 losses, runs scored 832, runs allowed 618. Stored in the "
                "repository at data/current/evidence/mlb-records-2026.json with its own source URL.",
        "limits": "Captured the previous day, not re-read in this session. Disclosed on the row and on "
                  "the flag page.",
    },
    {
        "id": "src-urc-r4",
        "org": "United Rugby Championship",
        "title": "Match centre, Round 4, 2026-27",
        "url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "read_at": "2026-10-23T16:31Z",
        "official": True,
        "role": "fixture",
        "read": "Friday 23 October: Cardiff v Hollywoodbets Sharks at Cardiff Arms Park, Connacht v "
                "Zebre Parma at Dexcom Stadium, Edinburgh v Emirates Lions at Hive Stadium, all printed "
                "as 14:45 with the page note that times are local. Also the eight Round 3 results of "
                "9-10 October, used as form: Glasgow 36-19 Connacht, Dragons 31-38 Ospreys, Bulls 57-15 "
                "Lions, Stormers 39-22 Sharks, Zebre 12-29 Edinburgh, Scarlets 27-26 Benetton, "
                "Ulster 26-26 Munster, Leinster 29-5 Cardiff.",
        "limits": "Local time only: no offset printed, so UTC depends on the venue's zone. Club names "
                  "differ between the fixture block and the results block (F-CF-04).",
    },
    {
        "id": "src-f1-usgp",
        "org": "Formula 1",
        "title": "United States Grand Prix 2026",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "read_at": "2026-10-23T16:33Z",
        "official": True,
        "role": "fixture",
        "read": "Circuit of the Americas, 5.513 km, 56 laps, 308.432 km race distance. Sessions: "
                "practice one Friday 13:30-14:30, practice two Friday 17:00-18:00, practice three "
                "Saturday 13:30-14:30, qualifying Saturday 17:00, race Sunday 16:00.",
        "limits": "No offset printed; local Austin time assumed to be the basis but not stated on the "
                  "page, so no UTC value is published.",
    },
    {
        "id": "src-wst-nio",
        "org": "World Snooker Tour",
        "title": "BetVictor Northern Ireland Open match list",
        "url": "https://www.wst.tv/matches",
        "read_at": "2026-10-23T16:35Z",
        "official": True,
        "role": "context",
        "read": "Belfast, 18-26 October. Round 1 results read: Scott Donaldson 4-0 Wu Yize, "
                "David Gilbert 4-1 Oliver Sykes, Mark Williams 4-1 Wu Yize's compatriot unavailable in "
                "the loaded portion, Jak Jones' opening result not in the loaded portion.",
        "limits": "The loaded portion stops at the 18-19 October sessions, so today's last-64 ties are "
                  "not confirmed on the tournament page and no snooker fixture is treated as confirmed.",
    },
]

# --------------------------------------------------------------------------------------------------
# Discovery rows. Transcribed from the hubs. Time strings are reproduced exactly as printed, with no
# conversion anywhere in this project. `share` is tips-for-the-pick over tips-on-the-event.
# Market codes: ML win market, HCP handicap/puck-line/spread, TOT total, SETS set market, OUT outright.
# --------------------------------------------------------------------------------------------------
D = "https://www.olbg.com/betting-tips/"

def row(sport, eid, name, comp, t, pick, market, tips, share, path=None):
    return {
        "sport": sport,
        "olbg_event_id": eid,
        "name": name,
        "competition": comp,
        "olbg_time_text": t,
        "olbg_pick": pick,
        "market": market,
        "olbg_tips": tips,
        "share": share,
        "url": D + (path or "OLBG/0"),
    }

DISCOVERY = [
    # ---------------- Ice Hockey ----------------
    row("ice-hockey", 199984, "Montreal Canadiens @ Chicago Blackhawks", "NHL", "Today 20:07",
        "Montreal Canadiens", "ML", 3, 1.00, "NHL/1330/Montreal_Canadiens_v_Chicago_Blackhawks/199984?event_id=199984"),
    row("ice-hockey", 199946, "Esbjerg Energy vs Herning Blue Fox", "Denmark Metal Ligaen", "Today 13:00",
        "Herning Blue Fox", "ML", 3, 1.00, "Denmark_Metal_Ligaen/1200/Esbjerg_Energy_v_Herning_Blue_Fox/199946?event_id=199946"),
    row("ice-hockey", 199924, "EHC Munchen vs Iserlohn Roosters", "Germany DEL", "Today 13:30",
        "EHC Munchen", "ML", 1, 1.00),
    row("ice-hockey", 199925, "Adler Mannheim vs Lowen Frankfurt", "Germany DEL", "Today 13:30",
        "Adler Mannheim", "ML", 1, 1.00),
    row("ice-hockey", 199926, "Eisbaren Berlin vs Augsburger Panther", "Germany DEL", "Today 13:30",
        "Eisbaren Berlin -1.50", "HCP", 1, 1.00),
    row("ice-hockey", 199927, "Grizzlys Wolfsburg vs ERC Ingolstadt", "Germany DEL", "Today 13:30",
        "ERC Ingolstadt", "ML", 2, 1.00),
    row("ice-hockey", 199928, "Nurnberg Ice Tigers vs Krefeld Pinguine", "Germany DEL", "Today 13:30",
        "Under 5.50", "TOT", 1, 1.00),
    row("ice-hockey", 199930, "Straubing Tigers vs Kolner Haie", "Germany DEL", "Today 13:30",
        "Under 5.50", "TOT", 1, 1.00),
    row("ice-hockey", 199947, "Rodovre Mighty Bulls vs Herlev Eagles", "Denmark Metal Ligaen", "Today 13:30",
        "Herlev Eagles", "ML", 2, 1.00),
    row("ice-hockey", 199955, "Kiekko-Espoo vs HIFK", "Finland SM Liiga", "Today 12:30",
        "Over 5.50", "TOT", 1, 1.00),
    row("ice-hockey", 199965, "Graz 99ers vs Black Wings Linz", "Austria ICE Hockey League", "Today 12:30",
        "Linz +1.50", "HCP", 1, 0.50),
    row("ice-hockey", 199968, "Pioneers Vorarlberg vs HCB Sudtirol", "Austria ICE Hockey League", "Today 13:30",
        "HCB Sudtirol", "ML", 1, 1.00),
    row("ice-hockey", 199969, "HK Olimpija Ljubljana vs Fehervar AV19", "Austria ICE Hockey League", "Today 13:15",
        "Olimpija -1.50", "HCP", 1, 1.00),
    row("ice-hockey", 199908, "Fribourg Gotteron vs EHC Biel", "Switzerland National League", "Today 13:45",
        "Fribourg Gotteron", "ML", 1, 1.00),
    # ---------------- Basketball ----------------
    row("basketball", 535928, "Zalgiris Kaunas vs ASVEL Lyon-Villeurbanne", "EuroLeague", "Today 13:00",
        "Zalgiris Kaunas", "ML", 16, 0.5625),
    row("basketball", 535925, "Olympiacos vs Fenerbahce", "EuroLeague", "Today 14:15",
        "Olympiacos", "ML", 10, 0.60),
    row("basketball", 535926, "Paris Basketball vs Valencia Basket", "EuroLeague", "Today 14:45",
        "Valencia Basket", "ML", 10, 0.50),
    row("basketball", 536041, "Chicago Bulls @ Milwaukee Bucks", "NBA", "Today 16:10",
        "Milwaukee Bucks", "ML", 5, 1.00),
    row("basketball", 536036, "Minnesota Timberwolves @ Orlando Magic", "NBA", "Today 19:10",
        "Minnesota Timberwolves", "ML", 5, 1.00),
    row("basketball", 534841, "Houston Rockets @ San Antonio Spurs", "NBA", "Today 21:40",
        "San Antonio Spurs", "ML", 6, 0.6667),
    row("basketball", 534842, "New York Knicks @ Boston Celtics", "NBA", "Today 19:10",
        "Boston Celtics -2.50", "HCP", 3, 1.00),
    row("basketball", 536034, "Toronto Raptors @ Washington Wizards", "NBA", "Today 19:10",
        "Toronto Raptors", "ML", 4, 0.75),
    row("basketball", 536037, "Dallas Mavericks @ Indiana Pacers", "NBA", "Today 19:10",
        "Indiana Pacers", "ML", 3, 1.00),
    row("basketball", 536038, "Detroit Pistons @ Miami Heat", "NBA", "Today 20:10",
        "Detroit Pistons", "ML", 3, 1.00),
    row("basketball", 536043, "Portland Trail Blazers @ Sacramento Kings", "NBA", "Today 22:10",
        "Portland Trail Blazers -10.50", "HCP", 3, 1.00),
    row("basketball", 536035, "Atlanta Hawks @ Charlotte Hornets", "NBA", "Today 19:10",
        "Atlanta Hawks -2.50", "HCP", 2, 1.00),
    row("basketball", 536040, "New Orleans Pelicans @ Utah Jazz", "NBA", "Today 21:40",
        "Utah Jazz", "ML", 2, 1.00),
    row("basketball", 536031, "GTK Gliwice vs Torun", "Poland PLK", "Today 14:15",
        "Torun", "ML", 3, 0.6667),
    # ---------------- Tennis ----------------
    row("tennis", 902150, "Arthur Fils vs Alex Michelsen", "", "Today 12:30", "Arthur Fils", "ML", 10, 0.50),
    row("tennis", 902155, "Flavio Cobolli vs Brandon Nakashima", "", "Today 13:00", "Flavio Cobolli", "ML", 8, 0.625),
    row("tennis", 902153, "Jan-Lennard Struff vs Zizou Bergs", "", "Today 14:00", "Jan-Lennard Struff", "ML", 8, 0.625),
    row("tennis", 902147, "Luca Van Assche vs Lorenzo Musetti", "", "Today 14:30", "Luca Van Assche", "ML", 5, 0.60),
    row("tennis", 902157, "Ann Li vs Ashlyn Krueger", "", "Today 23:00", "Over 22.50", "TOT", 3, 0.6667),
    row("tennis", 902162, "Katie Boulter vs Katerina Siniakova", "", "Tomorrow 00:30", "Katie Boulter", "ML", 1, 1.00),
    row("tennis", 902160, "Leylah Fernandez vs Marie Bouzkova", "", "Tomorrow 03:00", "Leylah Fernandez", "ML", 1, 1.00),
    row("tennis", 902163, "Elena Rybakina vs Diana Shnaider", "", "Tomorrow 05:30", "Diana Shnaider", "ML", 1, 1.00),
    row("tennis", 902159, "Nikoloz Basilashvili vs Stefanos Tsitsipas", "", "Tomorrow 06:00",
        "Tsitsipas 2-1", "SETS", 1, 1.00),
    # ---------------- Cricket ----------------
    row("cricket", 188839, "Tasmania vs Victoria", "Australia One-Day Cup", "Today 19:30", "Tasmania", "ML", 7, 0.7143),
    row("cricket", 188838, "Pakistan vs England", "ODI series", "25 Oct 04:00", "Pakistan", "ML", 1, 1.00),
    row("cricket", 188832, "New Zealand vs India", "T20 international", "Tomorrow 03:00", "India", "ML", 5, 0.80),
    row("cricket", 188840, "Western Australia vs New South Wales", "Australia One-Day Cup", "Tomorrow 02:00",
        "Western Australia", "ML", 4, 0.75),
    row("cricket", 188841, "Lions vs Limpopo Impalas", "South Africa T20 Challenge", "Tomorrow 07:00",
        "Lions", "ML", 3, 1.00),
    row("cricket", 188842, "Eastern Cape Iinyathi vs Warriors", "South Africa T20 Challenge", "Tomorrow 07:00",
        "Warriors", "ML", 2, 1.00),
    row("cricket", 188843, "Knights vs Mpumalanga Rhinos", "South Africa T20 Challenge", "Tomorrow 12:00",
        "Mpumalanga Rhinos", "ML", 1, 1.00),
    row("cricket", 182606, "ICC Cricket World Cup 2027", "Outright", "21 Nov 2027", "India", "OUT", 1, 1.00),
    row("cricket", 187184, "Womens Big Bash League 2026", "Outright", "05 Dec", "Sydney Thunder Women", "OUT", 1, 1.00),
    row("cricket", 187503, "Big Bash League 2026-27", "Outright", "12 Dec", "Perth Scorchers", "OUT", 1, 1.00),
    row("cricket", 187504, "SA20 2026-27", "Outright", "24 Jan 2027", "MI Cape Town", "OUT", 1, 1.00),
    row("cricket", 188350, "T20 Blast 2027", "Outright", "18 Jul 2027", "Somerset", "OUT", 1, 1.00),
    # ---------------- Snooker ----------------
    row("snooker", 9951, "Jak Jones v Scott Donaldson", "Northern Ireland Open", "Today 14:05",
        "Jak Jones", "ML", 15, 0.7333),
    row("snooker", 9950, "David Gilbert v Mark Williams", "Northern Ireland Open", "Today 14:05",
        "Mark Williams", "ML", 15, 0.7333),
    # ---------------- Darts ----------------
    row("darts", 32335, "Jonny Clayton vs Niko Springer", "European Championship", "Today 14:45",
        "Jonny Clayton", "ML", 31, 0.8387),
    row("darts", 32326, "Wessel Nijman vs Martin Schindler", "European Championship", "Today 15:45",
        "Wessel Nijman", "ML", 23, 0.7826),
    row("darts", 32332, "Ryan Joyce vs Jermaine Wattimena", "European Championship", "Today 13:15",
        "Ryan Joyce", "ML", 25, 0.64),
    row("darts", 32333, "Krzysztof Ratajski vs Dave Chisnall", "European Championship", "Today 13:45",
        "Krzysztof Ratajski", "ML", 26, 0.5769),
    row("darts", 32327, "Nathan Aspinall vs Cristo Reyes", "European Championship", "Today 14:15",
        "Nathan Aspinall", "ML", 22, 0.6364),
    row("darts", 32328, "Luke Littler vs William O'Connor", "European Championship", "Today 15:15",
        "Luke Littler", "ML", 20, 0.70),
    row("darts", 32331, "Kevin Doets vs Michael van Gerwen", "European Championship", "Today 16:15",
        "Michael van Gerwen", "ML", 17, 0.5882),
    row("darts", 32336, "Josh Rock vs Chris Dobey", "European Championship", "Today 16:45",
        "Josh Rock", "ML", 19, 0.5263),
    row("darts", 32384, "Stephen Bunting vs Kim Huybrechts", "European Championship", "Tomorrow 13:15",
        "Kim Huybrechts", "ML", 3, 0.6667),
    row("darts", 32385, "Gian van Veen vs Luke Woodhouse", "European Championship", "Tomorrow 13:15",
        "Luke Woodhouse", "ML", 3, 0.6667),
    row("darts", 32386, "Ross Smith vs Damon Heta", "European Championship", "Tomorrow 13:15",
        "Damon Heta", "ML", 3, 0.6667),
    row("darts", 32383, "Cameron Menzies vs Gerwyn Price", "European Championship", "Tomorrow 13:15",
        "Gerwyn Price", "ML", 2, 0.50),
    row("darts", 32338, "European Championship 2026", "Outright", "25 Oct 14:00", "Luke Littler", "OUT", 3, 0.6667),
    # ---------------- Baseball ----------------
    row("baseball", 160789, "Tampa Bay Rays @ Milwaukee Brewers", "MLB World Series", "Today 20:00",
        "Milwaukee Brewers", "ML", 31, 0.8065, "MLB/1100/Tampa_Bay_Rays_v_Milwaukee_Brewers/160789?event_id=160789"),
    # ---------------- Rugby Union ----------------
    row("rugby-union", 609579, "Edinburgh v Emirates Lions", "United Rugby Championship", "Today 14:45",
        "Edinburgh", "ML", 9, 0.8889),
    row("rugby-union", 609577, "Connacht v Zebre Parma", "United Rugby Championship", "Today 14:45",
        "Connacht", "ML", 15, 0.7333),
    row("rugby-union", 609575, "Cardiff v Hollywoodbets Sharks", "United Rugby Championship", "Today 14:45",
        "Hollywoodbets Sharks", "ML", 7, 0.5714),
    row("rugby-union", 609570, "Gloucester v Bath", "Premiership Rugby", "Today 14:45", "Gloucester", "ML", 7, 1.00),
    row("rugby-union", 609573, "Newcastle Red Bulls v Sale Sharks", "Premiership Rugby", "Today 14:45",
        "Sale Sharks", "ML", 5, 0.60),
    row("rugby-union", 609558, "Agen v Nissa", "France Pro D2", "Today 13:30", "Agen", "ML", 18, 0.6667),
    row("rugby-union", 609560, "Aurillac v Nevers", "France Pro D2", "Today 13:30", "Aurillac", "ML", 19, 0.7368),
    row("rugby-union", 609557, "Narbonne v Brive", "France Pro D2", "Today 13:00", "Brive", "ML", 17, 0.6471),
    row("rugby-union", 609559, "Valence Romans v Colomiers", "France Pro D2", "Today 13:30", "Valence Romans", "ML", 11, 0.5455),
    row("rugby-union", 609562, "Provence v Beziers", "France Pro D2", "Today 15:00", "Provence", "ML", 10, 0.60),
    row("rugby-union", 609561, "Grenoble v Biarritz", "France Pro D2", "Today 15:00", "Grenoble", "ML", 10, 0.60),
    row("rugby-union", 609563, "Soyaux Angouleme v Dax", "France Pro D2", "Today 13:30", "Dax", "ML", 14, 0.50),
    row("rugby-union", 609582, "Japan v Fiji", "Autumn international", "Tomorrow 01:50", "Fiji", "ML", 3, 0.6667),
    row("rugby-union", 609576, "Bulls v Ulster", "United Rugby Championship", "Tomorrow 07:45", "Ulster", "ML", 4, 0.75),
    row("rugby-union", 609580, "Stormers v Scarlets", "United Rugby Championship", "Tomorrow 10:00", "Scarlets", "ML", 1, 1.00),
    # ---------------- Volleyball ----------------
    row("volleyball", 37009, "VOLLEY GOATS Mitteldeutschland vs Netzhoppers KW", "Germany Bundesliga", "Today 13:30",
        "Netzhoppers KW", "ML", 7, 0.8571),
    row("volleyball", 37015, "ATSC Klagenfurt Women vs Linz-Steg Women", "Austria League", "Today 14:00",
        "Linz-Steg Women", "ML", 7, 0.5714),
    row("volleyball", 37025, "Lokomotiv Avia vs Montana", "Bulgaria Superleague", "Today 12:30",
        "Lokomotiv Avia", "ML", 4, 0.75),
    row("volleyball", 37001, "Brasilia Women vs Sesc RJ Flamengo Women", "Brazil Superliga", "Today 17:30",
        "Brasilia Women", "ML", 9, 0.5556),
    row("volleyball", 37022, "Minas Women vs Paulistano-Barueri Women", "Brazil Superliga", "Today 17:30",
        "Minas Women", "ML", 6, 0.6667),
    row("volleyball", 37017, "SG Sokol-Post Women vs TSV Hartberg Women", "Austria League", "Tomorrow 10:30",
        "Sokol-Post 3-1", "SETS", 1, 1.00),
    row("volleyball", 37026, "Sternberk Women vs VK Lvice Praha Women", "Czech Extraliga", "Tomorrow 12:00",
        "Sternberk 3-1", "SETS", 1, 1.00),
    row("volleyball", 37031, "UVC Ried vs VBK Klagenfurt", "Austria League", "Tomorrow 12:00", "UVC Ried", "ML", 1, 1.00),
    row("volleyball", 36964, "PGE Skra Belchatow vs Projekt Warszawa", "Poland PlusLiga", "Tomorrow 12:00",
        "Projekt Warszawa", "ML", 3, 0.6667),
    row("volleyball", 37002, "Mackenzie Women vs Osasco Women", "Brazil Superliga", "Tomorrow 15:00",
        "Mackenzie Women", "ML", 3, 0.6667),
    row("volleyball", 37003, "Abel-Moda Brusque Women vs Praia Clube Women", "Brazil Superliga", "Tomorrow 20:00",
        "Abel-Moda Brusque Women", "ML", 2, 1.00),
    row("volleyball", 36994, "Trentino vs Cisterna", "Italy SuperLega", "25 Oct 12:00", "Cisterna", "ML", 2, 1.00),
    row("volleyball", 36997, "Perugia vs Pordenone", "Italy SuperLega", "25 Oct 13:00", "Pordenone", "ML", 2, 1.00),
    row("volleyball", 36965, "CHKS Chelm vs Resovia Rzeszow", "Poland PlusLiga", "25 Oct 13:00",
        "Resovia Rzeszow", "ML", 3, 0.6667),
    # ---------------- Handball ----------------
    row("handball", 12101, "Bidasoa Irun vs Caserio Ciudad Real", "Spain Liga ASOBAL", "Today 13:00",
        "Bidasoa Irun", "ML", 12, 0.50),
    row("handball", 12088, "Frisch Auf Goppingen vs ThSV Eisenach", "Germany Bundesliga", "Today 13:00",
        "Tie", "ML", 15, 0.40),
    row("handball", 12083, "Pays d'Aix UC vs Toulouse", "France Starligue", "Today 14:00", "Toulouse", "ML", 16, 0.4375),
    row("handball", 12080, "Limoges 87 vs Dunkerque", "France Starligue", "Today 14:00", "Limoges 87", "ML", 15, 0.40),
    row("handball", 12093, "TSV Hannover-Burgdorf vs TBV Lemgo Lippe", "Germany Bundesliga", "Today 14:00",
        "Tie", "ML", 13, 0.4615),
    row("handball", 12079, "Chartres vs USAM Nimes", "France Starligue", "Today 14:00", "Tie", "ML", 10, 0.50),
    row("handball", 12121, "FC Barcelona vs Ciudad Encantada", "Spain Liga ASOBAL", "Today 13:00",
        "Ciudad Encantada +13.50", "HCP", 5, 0.80),
    row("handball", 12085, "Selestat Alsace vs Caen", "France Starligue", "Today 14:30", "Caen", "ML", 8, 0.50),
    row("handball", 12086, "Tremblay vs Cesson Rennes", "France Starligue", "Today 14:30", "Cesson Rennes", "ML", 9, 0.4444),
    row("handball", 12120, "GRK Ohrid vs Spor Toto SK", "EHF European Cup", "Today 12:30",
        "Spor Toto SK +11.50", "HCP", 5, 1.00),
    row("handball", 12110, "Estonia Women vs Kosovo Women", "Women's international", "Today 14:00",
        "Kosovo Women", "ML", 11, 0.4545),
    row("handball", 12076, "Skive FH vs Aalborg Handbold", "Denmark Handboldligaen", "Tomorrow 09:00",
        "Aalborg Handbold", "ML", 6, 0.50),
    row("handball", 12077, "Skjern Handbold vs Ribe Esbjerg HH", "Denmark Handboldligaen", "Tomorrow 10:00",
        "Ribe Esbjerg HH", "ML", 3, 0.6667),
    row("handball", 12107, "Villa de Aranda vs Puerto Sagunto", "Spain Liga ASOBAL", "Tomorrow 13:00",
        "Puerto Sagunto", "ML", 2, 1.00),
    # ---------------- Motor Racing ----------------
    row("motor-racing", 913, "United States Grand Prix 2026", "Formula 1", "25 Oct 16:00",
        "Max Verstappen", "ML", 38, 0.3421),
    row("motor-racing", 828, "Formula 1 Drivers Championship 2026", "Outright", "06 Dec 08:00",
        "Max Verstappen", "OUT", 33, 0.2727),
    row("motor-racing", 912, "F1 Drivers Championship 2026 without Kimi Antonelli", "Outright", "06 Dec 08:00",
        "Max Verstappen", "OUT", 7, 0.5714),
    # ---------------- Gaelic Sports ----------------
    row("gaelic-sports", 3530, "St Finbarrs v Nemo Rangers", "Cork senior football final", "25 Oct 12:00",
        "Nemo Rangers +1.50", "HCP", 18, 0.7778),
    row("gaelic-sports", 3532, "Moycullen v Salthill-Knocknacarra", "Galway senior football final", "25 Oct 12:00",
        "Moycullen -3.50", "HCP", 24, 0.50),
    row("gaelic-sports", 3531, "Kanturk v Eire Og Cor", "Cork intermediate football", "01 Nov 09:00",
        "Kanturk", "ML", 7, 0.5714),
    row("gaelic-sports", 3537, "Fr Caseys v Kildimo Pallaskenry", "Limerick senior football", "01 Nov 10:30",
        "Fr Caseys", "ML", 3, 1.00),
    row("gaelic-sports", 3327, "All-Ireland Senior Football Championship 2027", "Outright", "25 Jul 2027",
        "Kerry", "OUT", 7, 0.7143),
    # ---------------- Greyhounds ----------------
    row("greyhounds", 689803, "17:12 Towcester (A3) - Choices Jean", "Towcester", "Today 12:12",
        "Choices Jean", "ML", 4, 0.50),
    row("greyhounds", 689800, "17:18 Kinsley (A7) - Grumpy Sandstorm", "Kinsley", "Today 17:18",
        "Grumpy Sandstorm", "ML", 2, 1.00, "Greyhounds/28/Kinsley/689800?event_id=689800"),
    row("greyhounds", 689802, "17:31 Towcester (A2) - Mums Image", "Towcester", "Today 17:31",
        "Mums Image", "ML", 2, 1.00),
    row("greyhounds", 689806, "17:24 Newcastle (A4) - Alnwick Tina", "Newcastle", "Today 17:24",
        "Alnwick Tina", "ML", 1, 1.00),
    row("greyhounds", 689804, "17:37 Kinsley (A5) - Grumpy Jacko", "Kinsley", "Today 17:37",
        "Grumpy Jacko", "ML", 1, 1.00),
    row("greyhounds", 689798, "17:43 Newcastle (A3) - Dryland Velvet", "Newcastle", "Today 17:43",
        "Dryland Velvet", "ML", 2, 0.50),
    row("greyhounds", 689805, "17:49 Towcester (A5) - Trapstyle Sneezy", "Towcester", "Today 17:49",
        "Trapstyle Sneezy", "ML", 2, 1.00),
    row("greyhounds", 689801, "17:51 Harlow (A6) - Doreens Poppy", "Harlow", "Today 17:51",
        "Doreens Poppy", "ML", 1, 1.00),
    row("greyhounds", 689807, "17:56 Kinsley (A4) - Kellyseyenoone", "Kinsley", "Today 17:56",
        "Kellyseyenoone", "ML", 1, 1.00),
    row("greyhounds", 689808, "18:02 Newcastle (A2) - Mollys Aoibhe", "Newcastle", "Today 18:02",
        "Mollys Aoibhe", "ML", 1, 1.00),
    row("greyhounds", 689810, "18:08 Nottingham (A3) - Honeygar Flow", "Nottingham", "Today 18:08",
        "Honeygar Flow", "ML", 1, 1.00),
    row("greyhounds", 689811, "18:11 Harlow (A5) - Club Dream", "Harlow", "Today 18:11",
        "Club Dream", "ML", 1, 1.00),
    row("greyhounds", 689816, "18:18 Sheffield (A4) - Jaykay Seven", "Sheffield", "Today 18:18",
        "Jaykay Seven", "ML", 1, 1.00),
    row("greyhounds", 689846, "20:33 Romford (A2) - Ontherun Jamie", "Romford", "Today 20:33",
        "Ontherun Jamie", "ML", 2, 1.00),
    row("greyhounds", 689717, "21:13 Romford (A1) - Grouchos Gregor", "Romford", "Today 21:13",
        "Grouchos Gregor", "ML", 2, 1.00),
    # ---------------- Rugby League ----------------
    row("rugby-league", 2695857, "State of Origin 2027 series", "Outright", "27 May 2027",
        "New South Wales", "OUT", 12, 0.75),
    row("rugby-league", 2801554, "Super League 2027", "Outright", "02 Oct 2027", "Leeds Rhinos", "OUT", 3, 1.00),
    row("rugby-league", 2801600, "NRL 2027", "Outright", "03 Oct 2027", "Penrith Panthers", "OUT", 2, 1.00),
]

# --------------------------------------------------------------------------------------------------
# Fixtures confirmed on an official page today. Only these can carry a Medium or High grade.
# --------------------------------------------------------------------------------------------------
FIXTURES = [
    {
        "id": "fx-nhl-mtl-chi",
        "sport": "ice-hockey",
        "olbg_event_id": 199984,
        "name": "Montreal Canadiens at Chicago Blackhawks",
        "home": "Chicago Blackhawks",
        "away": "Montreal Canadiens",
        "competition": "NHL",
        "start_utc": "2026-10-24T00:00Z",
        "venue": "United Center, Chicago",
        "evidence": "src-nhl-schedule",
        "official_id": "game 2026020166",
        "state": "FUT (pre-game at read time)",
        "notes": "The league lists exactly two games for 23 October; this is one of them.",
    },
    {
        "id": "fx-nhl-tbl-col",
        "sport": "ice-hockey",
        "olbg_event_id": None,
        "name": "Tampa Bay Lightning at Colorado Avalanche",
        "home": "Colorado Avalanche",
        "away": "Tampa Bay Lightning",
        "competition": "NHL",
        "start_utc": "2026-10-24T01:00Z",
        "venue": "Ball Arena, Denver",
        "evidence": "src-nhl-schedule",
        "official_id": "game 2026020167",
        "state": "FUT (pre-game at read time)",
        "notes": "Not on the OLBG hub at capture time: a confirmed fixture with no listing.",
    },
    {
        "id": "fx-mlb-ws-g1",
        "sport": "baseball",
        "olbg_event_id": 160789,
        "name": "Tampa Bay Rays at Milwaukee Brewers",
        "home": "Milwaukee Brewers",
        "away": "Tampa Bay Rays",
        "competition": "World Series, Game 1 of 7",
        "start_utc": "2026-10-24T00:00Z",
        "venue": "American Family Field, Milwaukee",
        "evidence": "src-mlb-schedule",
        "official_id": "gamePk 849805",
        "state": "Scheduled; probable pitchers Nick Martinez (TB), Jacob Misiorowski (MIL)",
        "notes": "ifNecessary=N, so the game is not contingent on another result.",
    },
    {
        "id": "fx-urc-car-sha",
        "sport": "rugby-union",
        "olbg_event_id": 609575,
        "name": "Cardiff v Hollywoodbets Sharks",
        "home": "Cardiff",
        "away": "Sharks",
        "competition": "United Rugby Championship, Round 4",
        "start_utc": None,
        "local_time": "14:45 local, Friday 23 October",
        "venue": "Cardiff Arms Park",
        "evidence": "src-urc-r4",
        "official_id": "Round 4 fixture list",
        "state": "Scheduled",
        "notes": "The URC prints local time only; no UTC conversion is published because the page "
                 "does not state an offset.",
    },
    {
        "id": "fx-urc-con-zeb",
        "sport": "rugby-union",
        "olbg_event_id": 609577,
        "name": "Connacht v Zebre Parma",
        "home": "Connacht",
        "away": "Zebre Parma",
        "competition": "United Rugby Championship, Round 4",
        "start_utc": None,
        "local_time": "14:45 local, Friday 23 October",
        "venue": "Dexcom Stadium, Galway",
        "evidence": "src-urc-r4",
        "official_id": "Round 4 fixture list",
        "state": "Scheduled",
        "notes": "Local time only, as above.",
    },
    {
        "id": "fx-urc-edi-lio",
        "sport": "rugby-union",
        "olbg_event_id": 609579,
        "name": "Edinburgh v Emirates Lions",
        "home": "Edinburgh",
        "away": "Lions",
        "competition": "United Rugby Championship, Round 4",
        "start_utc": None,
        "local_time": "14:45 local, Friday 23 October",
        "venue": "Hive Stadium, Edinburgh",
        "evidence": "src-urc-r4",
        "official_id": "Round 4 fixture list",
        "state": "Scheduled",
        "notes": "Local time only, as above.",
    },
]

# --------------------------------------------------------------------------------------------------
# Numeric inputs, each with the source it came from.
# --------------------------------------------------------------------------------------------------
INPUTS = {
    "nhl_quotes": {
        "fx-nhl-mtl-chi": {
            "source": "src-nhl-schedule",
            "away": {"name": "Montreal Canadiens", "american": [-170, -170, -162]},
            "home": {"name": "Chicago Blackhawks", "american": [138, 142, 134]},
            "excluded": "The same response carries decimal quotes that point the other way "
                        "(Montreal 2.35, Chicago 1.59); excluded and flagged as F-CF-03.",
        },
        "fx-nhl-tbl-col": {
            "source": "src-nhl-schedule",
            "away": {"name": "Tampa Bay Lightning", "american": [105, 106, 105]},
            "home": {"name": "Colorado Avalanche", "american": [-129, -128, -125]},
            "excluded": "Same provider split as the other game; the consistent trio only.",
        },
    },
    "mlb": {
        "fx-mlb-ws-g1": {
            "away": {"name": "Tampa Bay Rays", "w": 98, "l": 64, "rs": 736, "ra": 650,
                     "source": "src-mlb-standings"},
            "home": {"name": "Milwaukee Brewers", "w": 103, "l": 59, "rs": 832, "ra": 618,
                     "source": "src-mlb-records-capture"},
            "games": 162,
        }
    },
    "urc": {
        "source": "src-urc-r4",
        "results": [
            ["Glasgow Warriors", 36, "Connacht", 19, "2026-10-09"],
            ["Dragons", 31, "Ospreys", 38, "2026-10-09"],
            ["Bulls", 57, "Lions", 15, "2026-10-10"],
            ["Stormers", 39, "Sharks", 22, "2026-10-10"],
            ["Zebre Parma", 12, "Edinburgh", 29, "2026-10-10"],
            ["Scarlets", 27, "Benetton", 26, "2026-10-10"],
            ["Ulster", 26, "Munster", 26, "2026-10-10"],
            ["Leinster", 29, "Cardiff", 5, "2026-10-10"],
        ],
    },
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sports = [
        {"key": k, "name": n, "olbg_id": i, "hub": f"https://www.olbg.com/betting-tips/{p}/{i}",
         "coverage": c, "observed": OBSERVED}
        for k, n, i, p, c in SPORTS
    ]
    for k, n, i, p, c in SPORTS:
        pass
    (OUT / "sports.json").write_text(json.dumps(sports, indent=1))
    (OUT / "sources.json").write_text(json.dumps(SOURCES, indent=1))
    (OUT / "discovery.json").write_text(json.dumps(DISCOVERY, indent=1))
    (OUT / "fixtures.json").write_text(json.dumps(FIXTURES, indent=1))
    (OUT / "inputs.json").write_text(json.dumps(INPUTS, indent=1))

    per = {}
    for r in DISCOVERY:
        per[r["sport"]] = per.get(r["sport"], 0) + 1
    print(f"sports={len(sports)} sources={len(SOURCES)} discovery={len(DISCOVERY)} fixtures={len(FIXTURES)}")
    print(" ".join(f"{k}:{v}" for k, v in sorted(per.items())))
    print("missing sports:", [k for k, *_ in SPORTS if k not in per])


if __name__ == "__main__":
    main()
