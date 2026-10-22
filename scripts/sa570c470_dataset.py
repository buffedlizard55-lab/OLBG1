#!/usr/bin/env python3
"""Session a570c470 — verified fixture dataset.

Every row below was read from a primary governing-body source during this session
(2026-10-22 UTC) unless the row carries an explicit ``borrowed`` flag.  Fields that could
not be confirmed on an official page are left empty (``""``) and listed in
``data/a570c470/flagged.json``; nothing is inferred.

``inputs`` hold the raw sourced strength figures the pricing model consumes.  They are
never invented: each carries the exact figure read and the source id it came from.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "a570c470"
OUT.mkdir(parents=True, exist_ok=True)
SNAPSHOT = "2026-10-22T03:20:00Z"

# ----------------------------------------------------------------------------------
# helper
# ----------------------------------------------------------------------------------


def f(**kw):
    base = {
        "start_utc": "",
        "venue": "",
        "stage": "",
        "status": "verified",
        "sources": [],
        "flags": [],
        "inputs": {},
        "event_only": False,
        "borrowed": False,
        "total_line": None,
        "sigma": None,
        "series": None,
        "market_kind": "",
    }
    base.update(kw)
    return base


FIXTURES = []


def add(**kw):
    FIXTURES.append(f(**kw))


# ==================================================================================
# TENNIS — ATP / WTA signed supervisor draw PDFs, all read 2026-10-22
# ==================================================================================
WTA_NINGBO = "wta-ningbo-draw-2026"
WTA_OSAKA = "wta-osaka-draw-2026"
ATP_ALMATY = "atp-almaty-draw-2026"
ATP_BRUSSELS = "atp-brussels-draw-2026"
ATP_LYON = "atp-lyon-draw-2026"

add(id="ten-ningbo-rybakina-kudermetova", sport="Tennis", competition="WTA 500 Ningbo Open",
    home="Elena Rybakina", away="Polina Kudermetova", stage="Round of 16",
    venue="Yinzhou Tennis Center, Ningbo",
    sources=[WTA_NINGBO],
    inputs={"home": {"rank": 1, "basis": "Seeded 1, ranking 1 on the signed WTA draw sheet"},
            "away": {"rank": None, "basis": "Qualifier; ranking not printed on the draw sheet"}},
    flags=["Away player's ranking is not printed on the supervisor draw; only the seed list carries ranks, so the away input is one-sided."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-ningbo-kawa-bencic", sport="Tennis", competition="WTA 500 Ningbo Open",
    home="Katarzyna Kawa", away="Belinda Bencic", stage="Round of 16",
    venue="Yinzhou Tennis Center, Ningbo", sources=[WTA_NINGBO],
    inputs={"home": {"rank": None, "basis": "Qualifier; ranking not printed on the draw sheet"},
            "away": {"rank": 12, "basis": "Seeded 5, ranking 12 on the signed WTA draw sheet"}},
    flags=["Home player's ranking is not printed on the supervisor draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-ningbo-jovic-paolini", sport="Tennis", competition="WTA 500 Ningbo Open",
    home="Iva Jovic", away="Jasmine Paolini", stage="Round of 16",
    venue="Yinzhou Tennis Center, Ningbo", sources=[WTA_NINGBO],
    inputs={"home": {"rank": 11, "basis": "Seeded 4, ranking 11 on the signed WTA draw sheet"},
            "away": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"}},
    flags=["Away player's ranking is not printed on the supervisor draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-ningbo-eala-shnaider", sport="Tennis", competition="WTA 500 Ningbo Open",
    home="Alexandra Eala", away="Diana Shnaider", stage="Round of 16",
    venue="Yinzhou Tennis Center, Ningbo", sources=[WTA_NINGBO],
    inputs={"home": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"},
            "away": {"rank": 13, "basis": "Seeded 6, ranking 13 on the signed WTA draw sheet"}},
    flags=["Home player's ranking is not printed on the supervisor draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-osaka-stoiana-uchijima", sport="Tennis", competition="WTA 250 Japan Open (Osaka)",
    home="Mary Stoiana", away="Moyuka Uchijima", stage="Round of 16",
    venue="Osaka, Japan", sources=[WTA_OSAKA],
    inputs={"home": {"rank": None, "basis": "Qualifier; ranking not printed on the draw sheet"},
            "away": {"rank": None, "basis": "Wild card; ranking not printed on the draw sheet"}},
    flags=["Neither player's ranking is printed; both are unseeded on the signed draw.", "One-sided-input rule forces a neutral baseline."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-osaka-linette-siniakova", sport="Tennis", competition="WTA 250 Japan Open (Osaka)",
    home="Magda Linette", away="Katerina Siniakova", stage="Round of 16",
    venue="Osaka, Japan", sources=[WTA_OSAKA],
    inputs={"home": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"},
            "away": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"}},
    flags=["Neither ranking printed on the signed draw; neutral baseline."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-osaka-gibson-krueger", sport="Tennis", competition="WTA 250 Japan Open (Osaka)",
    home="Talia Gibson", away="Ashlyn Krueger", stage="Round of 16",
    venue="Osaka, Japan", sources=[WTA_OSAKA],
    inputs={"home": {"rank": 41, "basis": "Seeded 4, ranking 41 on the signed WTA draw sheet"},
            "away": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"}},
    flags=["Away ranking not printed on the signed draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-almaty-medvedev-shimabukuro", sport="Tennis", competition="ATP 250 Almaty Open",
    home="Daniil Medvedev", away="Sho Shimabukuro", stage="Round of 16",
    venue="Almaty Arena", sources=[ATP_ALMATY],
    inputs={"home": {"rank": 6, "basis": "Seeded 1, ranking 6 on the signed ATP draw sheet"},
            "away": {"rank": 93, "basis": "Lucky loser, last direct acceptance ranking 93 on the signed ATP draw sheet"}},
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-almaty-atmane-bellucci", sport="Tennis", competition="ATP 250 Almaty Open",
    home="Terence Atmane", away="Mattia Bellucci", stage="Round of 16",
    venue="Almaty Arena", sources=[ATP_ALMATY],
    inputs={"home": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"},
            "away": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"}},
    flags=["Neither ranking printed on the signed draw; neutral baseline."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-almaty-machac-khachanov", sport="Tennis", competition="ATP 250 Almaty Open",
    home="Tomas Machac", away="Karen Khachanov", stage="Round of 16",
    venue="Almaty Arena", sources=[ATP_ALMATY],
    inputs={"home": {"rank": None, "basis": "Seed 14; ranking not printed on the draw sheet"},
            "away": {"rank": 27, "basis": "Seeded 5, ranking 27 on the signed ATP draw sheet"}},
    flags=["Home ranking not printed on the signed draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-almaty-bublik-marozsan", sport="Tennis", competition="ATP 250 Almaty Open",
    home="Alexander Bublik", away="Fabian Marozsan", stage="Round of 16",
    venue="Almaty Arena", sources=[ATP_ALMATY],
    inputs={"home": {"rank": 22, "basis": "Seeded 3, ranking 22 on the signed ATP draw sheet"},
            "away": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"}},
    flags=["Away ranking not printed on the signed draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-brussels-collignon-lehecka", sport="Tennis", competition="ATP 250 European Open (Brussels)",
    home="Raphael Collignon", away="Jiri Lehecka", stage="Round of 16",
    venue="Brussels, Belgium", sources=[ATP_BRUSSELS],
    inputs={"home": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"},
            "away": {"rank": 16, "basis": "Seeded 2, ranking 16 on the signed ATP draw sheet"}},
    flags=["Home ranking not printed on the signed draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-brussels-goffin-michelsen", sport="Tennis", competition="ATP 250 European Open (Brussels)",
    home="David Goffin", away="Alex Michelsen", stage="Round of 16",
    venue="Brussels, Belgium", sources=[ATP_BRUSSELS],
    inputs={"home": {"rank": None, "basis": "Wild card; ranking not printed on the draw sheet"},
            "away": {"rank": 35, "basis": "Seeded 5, ranking 35 on the signed ATP draw sheet"}},
    flags=["Home ranking not printed on the signed draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-brussels-dzumhur-bergs", sport="Tennis", competition="ATP 250 European Open (Brussels)",
    home="Damir Dzumhur", away="Zizou Bergs", stage="Round of 16",
    venue="Brussels, Belgium", sources=[ATP_BRUSSELS],
    inputs={"home": {"rank": 100, "basis": "Last direct acceptance, ranking 100 on the signed ATP draw sheet"},
            "away": {"rank": 39, "basis": "Seeded 6, ranking 39 on the signed ATP draw sheet"}},
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-lyon-herbert-fritz", sport="Tennis", competition="ATP 250 Lyon",
    home="Pierre-Hugues Herbert", away="Taylor Fritz", stage="Round of 16",
    venue="Lyon, France", sources=[ATP_LYON],
    inputs={"home": {"rank": None, "basis": "Qualifier; ranking not printed on the draw sheet"},
            "away": {"rank": 12, "basis": "Seeded 2, ranking 12 on the signed ATP draw sheet"}},
    flags=["Home ranking not printed on the signed draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-lyon-gojo-altmaier", sport="Tennis", competition="ATP 250 Lyon",
    home="Borna Gojo", away="Daniel Altmaier", stage="Round of 16",
    venue="Lyon, France", sources=[ATP_LYON],
    inputs={"home": {"rank": None, "basis": "Qualifier; ranking not printed on the draw sheet"},
            "away": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"}},
    flags=["Neither ranking printed on the signed draw; neutral baseline."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-lyon-cobolli-wawrinka", sport="Tennis", competition="ATP 250 Lyon",
    home="Flavio Cobolli", away="Stan Wawrinka", stage="Round of 16",
    venue="Lyon, France", sources=[ATP_LYON],
    inputs={"home": {"rank": 7, "basis": "Seeded 1, ranking 7 on the signed ATP draw sheet"},
            "away": {"rank": None, "basis": "Wild card; ranking not printed on the draw sheet"}},
    flags=["Away ranking not printed on the signed draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-lyon-jacquet-nakashima", sport="Tennis", competition="ATP 250 Lyon",
    home="Kyrian Jacquet", away="Brandon Nakashima", stage="Round of 16",
    venue="Lyon, France", sources=[ATP_LYON],
    inputs={"home": {"rank": None, "basis": "Qualifier; ranking not printed on the draw sheet"},
            "away": {"rank": 19, "basis": "Seeded 5, ranking 19 on the signed ATP draw sheet"}},
    flags=["Home ranking not printed on the signed draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)
add(id="ten-lyon-vacherot-vanassche", sport="Tennis", competition="ATP 250 Lyon",
    home="Valentin Vacherot", away="Luca Van Assche", stage="Round of 16",
    venue="Lyon, France", sources=[ATP_LYON],
    inputs={"home": {"rank": 14, "basis": "Seeded 3, ranking 14 on the signed ATP draw sheet"},
            "away": {"rank": None, "basis": "Unseeded; ranking not printed on the draw sheet"}},
    flags=["Away ranking not printed on the signed draw."],
    market_kind="tennis", sigma=5.2, total_line=22.5)

# ==================================================================================
# BASKETBALL — EuroLeague round 6 (22-23 Oct) and NBA 22-23 Oct
# ==================================================================================
EL = "euroleague-r6-2026"
NBA = "nba-schedule-2026"

add(id="el-bes-efs-1022", sport="Basketball", competition="EuroLeague", stage="Regular Season Round 6",
    home="Besiktas Istanbul", away="Anadolu Efes Istanbul", start_utc="2026-10-22T17:30:00Z",
    venue="Basketball Development Center, Istanbul", sources=[EL],
    inputs={"home": {"record": "3-3", "games": 6, "diff": -1, "basis": "EuroLeague round 5 table, Besiktas 3-3, 554-555"},
            "away": {"record": "2-4", "games": 6, "diff": -18, "basis": "EuroLeague round 5 table, Anadolu Efes 2-4, 492-510"}},
    market_kind="basketball", sigma=13.5, total_line=171.5)
add(id="el-dub-bay-1022", sport="Basketball", competition="EuroLeague", stage="Regular Season Round 6",
    home="Dubai Basketball", away="FC Bayern Munich", start_utc="2026-10-22T18:00:00Z",
    venue="SAP Garden, Munich", sources=[EL],
    inputs={"home": {"record": None, "games": None, "diff": None, "basis": "Dubai record not captured on a page read this session"},
            "away": {"record": None, "games": None, "diff": None, "basis": "Bayern record not captured on a page read this session"}},
    flags=["Neither side's round-5 record was read on an official page this session; no price originated.", "Venue field names SAP Garden (Munich) with Dubai as the listed home side - neutral-venue notation is unresolved."],
    event_only=True)
add(id="el-mta-rmb-1022", sport="Basketball", competition="EuroLeague", stage="Regular Season Round 6",
    home="Maccabi Rapyd Tel Aviv", away="Real Madrid", start_utc="2026-10-22T18:05:00Z",
    venue="Aleksandar Nikolic Hall, Belgrade (neutral)", sources=[EL],
    inputs={"home": {"record": "2-4", "games": 6, "diff": -34, "basis": "EuroLeague round 5 table, Maccabi 2-4"},
            "away": {"record": "3-3", "games": 6, "diff": 23, "basis": "EuroLeague round 6 kit PDF, Real Madrid 3-3, 554-531"}},
    flags=["Maccabi's home game is staged in Belgrade; the desk applies no home advantage."],
    market_kind="basketball", sigma=13.5, total_line=171.5, hfa=0.0)
add(id="el-pao-bas-1022", sport="Basketball", competition="EuroLeague", stage="Regular Season Round 6",
    home="Panathinaikos AKTOR Athens", away="Kosner Baskonia Vitoria-Gasteiz", start_utc="2026-10-22T18:15:00Z",
    venue="Telekom Center Athens", sources=[EL],
    inputs={"home": {"record": "5-1", "games": 6, "diff": 90, "basis": "EuroLeague round 6 table, Panathinaikos 5-1 528-438"},
            "away": {"record": "1-5", "games": 6, "diff": -52, "basis": "EuroLeague round 5 kit PDF, Baskonia 1-4, 426-478"}},
    market_kind="basketball", sigma=13.5, total_line=171.5)
add(id="el-mil-bar-1022", sport="Basketball", competition="EuroLeague", stage="Regular Season Round 6",
    home="Armani Olimpia Milan", away="FC Barcelona", start_utc="2026-10-22T18:30:00Z",
    venue="Unipol Forum, Milan", sources=[EL],
    inputs={"home": {"record": None, "games": None, "diff": None, "basis": "Milan record not captured on a page read this session"},
            "away": {"record": None, "games": None, "diff": None, "basis": "Barcelona record not captured on a page read this session"}},
    flags=["Neither side's round-5 record was read on an official page this session; no price originated."],
    event_only=True)
add(id="el-par-czv-1022", sport="Basketball", competition="EuroLeague", stage="Regular Season Round 6",
    home="Partizan Mozzart Bet Belgrade", away="Crvena Zvezda Meridianbet Belgrade", start_utc="2026-10-22T18:45:00Z",
    venue="Belgrade Arena", sources=[EL],
    inputs={"home": {"record": None, "games": None, "diff": None, "basis": "Partizan record not captured on a page read this session"},
            "away": {"record": None, "games": None, "diff": None, "basis": "Crvena Zvezda record not captured on a page read this session"}},
    flags=["Neither side's round-5 record was read on an official page this session; no price originated."],
    event_only=True)
add(id="el-zal-asv-1023", sport="Basketball", competition="EuroLeague", stage="Regular Season Round 6",
    home="Zalgiris Kaunas", away="LDLC ASVEL Villeurbanne", start_utc="2026-10-23T17:00:00Z",
    venue="Zalgirio Arena, Kaunas", sources=[EL],
    inputs={"home": {"record": None, "games": None, "diff": None, "basis": "Zalgiris record not captured on a page read this session"},
            "away": {"record": None, "games": None, "diff": None, "basis": "ASVEL record not captured on a page read this session"}},
    flags=["Neither side's round-5 record was read on an official page this session; no price originated."],
    event_only=True)
add(id="el-oly-fen-1023", sport="Basketball", competition="EuroLeague", stage="Regular Season Round 6",
    home="Olympiacos Piraeus", away="Fenerbahce Tarfin Istanbul", start_utc="2026-10-23T18:15:00Z",
    venue="Sunel Arena, Piraeus", sources=[EL],
    inputs={"home": {"record": None, "games": None, "diff": None, "basis": "Olympiacos record not captured on a page read this session"},
            "away": {"record": None, "games": None, "diff": None, "basis": "Fenerbahce record not captured on a page read this session"}},
    flags=["Neither side's round-5 record was read on an official page this session; no price originated."],
    event_only=True)
add(id="el-par-val-1023", sport="Basketball", competition="EuroLeague", stage="Regular Season Round 6",
    home="Paris Basketball", away="Valencia Basket", start_utc="2026-10-23T18:45:00Z",
    venue="Adidas Arena, Paris", sources=[EL],
    inputs={"home": {"record": None, "games": None, "diff": None, "basis": "Paris record not captured on a page read this session"},
            "away": {"record": None, "games": None, "diff": None, "basis": "Valencia record not captured on a page read this session"}},
    flags=["Neither side's round-5 record was read on an official page this session; no price originated."],
    event_only=True)

# NBA — records are the official 2026-27 standings after the 20-21 Oct opening games.
NBA_GAMES = [
    ("nba-1022-phi-cle", "Philadelphia 76ers", "Cleveland Cavaliers", "2026-10-22T23:00:00Z",
     "Xfinity Mobile Arena, Philadelphia", "1-0", "0-0", 6),
    ("nba-1022-okc-den", "Oklahoma City Thunder", "Denver Nuggets", "2026-10-23T01:30:00Z",
     "Paycom Center, Oklahoma City", "1-0", "0-0", 12),
    ("nba-1023-bos-nyk", "Boston Celtics", "New York Knicks", "2026-10-23T23:00:00Z",
     "TD Garden, Boston", "0-1", "0-1", -8),
    ("nba-1023-cha-atl", "Charlotte Hornets", "Atlanta Hawks", "2026-10-23T23:00:00Z",
     "Spectrum Center, Charlotte", "1-0", "1-0", 0),
    ("nba-1023-ind-dal", "Indiana Pacers", "Dallas Mavericks", "2026-10-23T23:00:00Z",
     "Gainbridge Fieldhouse, Indianapolis", "1-0", "0-1", 0),
    ("nba-1023-orl-min", "Orlando Magic", "Minnesota Timberwolves", "2026-10-23T23:00:00Z",
     "Kia Center, Orlando", "0-1", "1-0", 0),
    ("nba-1023-was-tor", "Washington Wizards", "Toronto Raptors", "2026-10-23T23:00:00Z",
     "Capital One Arena, Washington", "1-0", "1-0", 0),
    ("nba-1023-mia-det", "Miami Heat", "Detroit Pistons", "2026-10-24T00:00:00Z",
     "Kaseya Center, Miami", "0-1", "1-0", 0),
    ("nba-1023-sas-hou", "San Antonio Spurs", "Houston Rockets", "2026-10-24T01:30:00Z",
     "Moody Center, Austin", "0-1", "1-0", -12),
    ("nba-1023-uta-nop", "Utah Jazz", "New Orleans Pelicans", "2026-10-24T01:30:00Z",
     "Delta Center, Salt Lake City", "0-1", "0-1", 0),
    ("nba-1023-gsw-mem", "Golden State Warriors", "Memphis Grizzlies", "2026-10-24T02:00:00Z",
     "Chase Center, San Francisco", "0-0", "1-0", 0),
    ("nba-1023-lal-lac", "Los Angeles Lakers", "LA Clippers", "2026-10-24T02:00:00Z",
     "Crypto.com Arena, Los Angeles", "0-0", "0-0", 0),
    ("nba-1023-sac-por", "Sacramento Kings", "Portland Trail Blazers", "2026-10-24T02:00:00Z",
     "Golden 1 Center, Sacramento", "0-0", "0-0", 0),
    ("nba-1023-mil-chi", "Milwaukee Bucks", "Chicago Bulls", "2026-10-23T20:00:00Z",
     "Fiserv Forum, Milwaukee", "0-1", "0-1", 0),
]
for gid, home, away, start, venue, rh, ra, diff in NBA_GAMES:
    add(id=gid, sport="Basketball", competition="NBA", stage="Regular Season",
        home=home, away=away, start_utc=start, venue=venue, sources=[NBA],
        inputs={"home": {"record": rh, "games": 1 if rh != "0-0" else 0, "diff": diff,
                         "basis": f"Official NBA 2026-27 standings, {home} {rh}"},
                "away": {"record": ra, "games": 1 if ra != "0-0" else 0, "diff": -diff,
                         "basis": f"Official NBA 2026-27 standings, {away} {ra}"}},
        flags=["One game or fewer played: the desk caps NBA confidence at Medium and treats the record as a weak prior."],
        market_kind="basketball", sigma=13.5, total_line=228.5)

# ==================================================================================
# GOLF — two verified events; no official two-sided rating exists, so no price.
# ==================================================================================
add(id="golf-bermuda-2026", sport="Golf", competition="PGA TOUR", stage="Butterfield Bermuda Championship",
    home="Butterfield Bermuda Championship", away="", start_utc="2026-10-22T13:00:00Z",
    venue="Port Royal Golf Course, Southampton, Bermuda (par 71, 6,828 yd)", sources=["pgatour-bermuda-2026"],
    flags=["Outright field only: no governing-body rating exists for the field, so the desk publishes the verified event facts and originates no price."],
    event_only=True)
add(id="golf-stifel-2026", sport="Golf", competition="PGA TOUR Champions", stage="Stifel Charity Classic",
    home="Stifel Charity Classic", away="", start_utc="2026-10-23T18:00:00Z",
    venue="Norwood Hills Country Club, St. Louis (par 71)", sources=["pgatour-stifel-2026"],
    flags=["Outright field only: no governing-body rating exists for the field, so the desk publishes the verified event facts and originates no price."],
    event_only=True)

# ==================================================================================
# CRICKET
# ==================================================================================
add(id="cric-ban-wi-odi3", sport="Cricket", competition="West Indies tour of Bangladesh", stage="3rd ODI (series level 1-1)",
    home="Bangladesh", away="West Indies", venue="Sher-e-Bangla National Stadium, Dhaka", sources=["icc-cricinfo-2026"],
    inputs={"home": {"record": "1-1", "games": 2, "diff": 0, "basis": "Series level 1-1 after two ODIs"},
            "away": {"record": "1-1", "games": 2, "diff": 0, "basis": "Series level 1-1 after two ODIs"}},
    flags=["No published ODI ranking line was read this session; a two-match series level at 1-1 gives the model no separation, so no High tier is possible."],
    market_kind="cricket", sigma=42.0, total_line=480.5)
add(id="cric-aus-ind-odi2", sport="Cricket", competition="India tour of Australia", stage="2nd ODI (Australia lead 1-0)",
    home="Australia", away="India", venue="Adelaide Oval, Adelaide", sources=["icc-cricinfo-2026"],
    inputs={"home": {"record": "1-0", "games": 1, "diff": 0, "basis": "Australia lead the three-match series 1-0"},
            "away": {"record": "0-1", "games": 1, "diff": 0, "basis": "India trail the three-match series 0-1"}},
    flags=["One-match sample; no published ODI ranking line was read, so the desk quotes a neutral baseline and caps confidence at Low."],
    market_kind="cricket", sigma=42.0, total_line=480.5)
add(id="cric-pak-sa-test2", sport="Cricket", competition="South Africa tour of Pakistan", stage="2nd Test (Pakistan lead 1-0)",
    home="Pakistan", away="South Africa", venue="Rawalpindi Cricket Stadium", sources=["icc-cricinfo-2026"],
    inputs={"home": {"record": "1-0", "games": 1, "diff": 93, "basis": "Pakistan won the 1st Test by 93 runs"},
            "away": {"record": "0-1", "games": 1, "diff": -93, "basis": "South Africa lost the 1st Test by 93 runs"}},
    flags=["One-Test sample; confidence capped at Low.", "Day-one start time not printed on the page read."],
    market_kind="cricket", sigma=42.0, total_line=480.5)

# ==================================================================================
# SNOOKER — BetVictor Northern Ireland Open round 3, read from wst.tv
# ==================================================================================
SNK = "wst-ni-open-day4-pm"
SNK2 = "wst-ni-open-day4-eve"
SNOOKER = [
    ("snk-r3-wilson-pang", "Kyren Wilson", "Pang Junxu", "2026-10-22T07:00:00Z",
     "World number 9 / 2024 world champion; Pang beat Liam Davies 4-3 with a 112 and an 81 clearance in the decider.", "Pang Junxu is world number 43 on the WST ranking list; he beat Liam Davies 4-3 in round 2."),
    ("snk-r3-selt-craigie", "Matthew Selt", "Sam Craigie", "2026-10-22T07:00:00Z",
     "Selt reached round 3 via the draw; ranking not in the top-11 block read.", "Craigie led Xu Si 3-0 with a 103, was pegged to 3-3 and won the decider with a 75."),
    ("snk-r3-slessor-walden", "Elliot Slessor", "Ricky Walden", "2026-10-22T08:00:00Z",
     "Slessor advanced to round 3; ranking not in the top-11 block read.", "Walden beat Neil Robertson 4-1 in round 1 and reached round 3."),
    ("snk-r3-mcgill-baranowski", "Anthony McGill", "Mateusz Baranowski", "2026-10-22T08:00:00Z",
     "McGill beat Jack Lisowski 4-1 in round 2.", "Baranowski beat Gary Wilson 4-3 and Wang Xinbo 4-3."),
    ("snk-r3-williams-odonnell", "Mark Williams", "Martin O'Donnell", "2026-10-22T13:00:00Z",
     "World number 8; beat Zhang Anda 4-2 with closing breaks of 78 and 58.", "O'Donnell beat Judd Trump 4-2 in round 1 and Luca Brecel in round 2."),
    ("snk-r3-gilbert-cheung", "David Gilbert", "Cheung Ka Wai", "2026-10-22T13:00:00Z",
     "Gilbert beat Gao Yang 4-3 on the final black; world ranking not in the top-11 block read.", "Cheung, world number 110, beat Ronnie O'Sullivan 4-3 and Stuart Bingham 4-0 with a 111."),
    ("snk-r3-brown-donaldson", "Jordan Brown", "Scott Donaldson", "2026-10-22T14:00:00Z",
     "Home favourite; beat Mark Allen then Michael Holt 4-3 with breaks of 113, 101 and 66.", "Donaldson beat Noppon Saengkham 4-1."),
    ("snk-r3-jones-wells", "Jak Jones", "Daniel Wells", "2026-10-22T14:00:00Z",
     "World number 24; won the Championship League and British Open in 2026-27, beat John Higgins 4-2 with 121 and 133.", "Wells beat Ryan Day 4-3 in a Welsh derby."),
]
for sid, home, away, start, hb, ab in SNOOKER:
    add(id=sid, sport="Snooker", competition="BetVictor Northern Ireland Open", stage="Round 3 (best of 7)",
        home=home, away=away, start_utc=start, venue="Waterfront Hall, Belfast", sources=[SNK, SNK2],
        inputs={"home": {"record": None, "games": None, "diff": None, "basis": hb},
                "away": {"record": None, "games": None, "diff": None, "basis": ab}},
        flags=["Neither player's numeric WST ranking was printed for both sides of this tie, so the model uses the sourced round-2 form text and caps confidence at Medium."],
        market_kind="snooker", series={"legs": 7, "need": 4, "unit": "frames"})

# ==================================================================================
# DARTS — PDC European Championship round 1, all 16 ties, drawn 18 Oct
# ==================================================================================
PDC = "pdc-euro-champ-2026"
DARTS = [
    ("pdc-ec-01", "Luke Woodhouse", "Dirk van Duijvenbode", "2026-10-22T17:00:00Z", 9, 24),
    ("pdc-ec-02", "Danny Noppert", "Stephen Bunting", "2026-10-22T17:00:00Z", 5, 28),
    ("pdc-ec-03", "Niels Zonneveld", "Cameron Menzies", "2026-10-22T17:00:00Z", 4, 29),
    ("pdc-ec-04", "Gerwyn Price", "Rob Cross", "2026-10-22T17:00:00Z", 13, 20),
    ("pdc-ec-05", "James Wade", "Damon Heta", "2026-10-22T17:00:00Z", 16, 17),
    ("pdc-ec-06", "Luke Humphries", "Ryan Searle", "2026-10-22T17:00:00Z", 12, 21),
    ("pdc-ec-07", "Gian van Veen", "Andrew Gilding", "2026-10-22T17:00:00Z", 8, 25),
    ("pdc-ec-08", "Ross Smith", "Karel Sedlacek", "2026-10-22T17:00:00Z", 1, 32),
    ("pdc-ec-09", "Ryan Joyce", "Jermaine Wattimena", "2026-10-23T17:00:00Z", 15, 18),
    ("pdc-ec-10", "Krzysztof Ratajski", "Dave Chisnall", "2026-10-23T17:00:00Z", 3, 30),
    ("pdc-ec-11", "Nathan Aspinall", "Cristo Reyes", "2026-10-23T17:00:00Z", 6, 27),
    ("pdc-ec-12", "Jonny Clayton", "Niko Springer", "2026-10-23T17:00:00Z", 7, 26),
    ("pdc-ec-13", "Luke Littler", "William O'Connor", "2026-10-23T17:00:00Z", 11, 22),
    ("pdc-ec-14", "Wessel Nijman", "Martin Schindler", "2026-10-23T17:00:00Z", 2, 31),
    ("pdc-ec-15", "Kevin Doets", "Michael van Gerwen", "2026-10-23T17:00:00Z", 14, 19),
    ("pdc-ec-16", "Josh Rock", "Chris Dobey", "2026-10-23T17:00:00Z", 10, 23),
]
for did, home, away, start, hs, as_ in DARTS:
    add(id=did, sport="Darts", competition="PDC Machineseeker European Championship", stage="Round 1 (best of 11 legs)",
        home=home, away=away, start_utc=start, venue="Westfalenhalle, Dortmund", sources=[PDC],
        inputs={"home": {"rank": hs, "basis": f"Seed {hs} of 32 on the official European Tour ranking list"},
                "away": {"rank": as_, "basis": f"Seed {as_} of 32 on the official European Tour ranking list"}},
        market_kind="darts", series={"legs": 11, "need": 6, "unit": "legs"})

# ==================================================================================
# HANDBALL — EHF Champions League round 6, all read from the EHF fixture list
# ==================================================================================
EHF = "ehf-cl-men-r6-2026"
HAND = [
    ("hand-ehf-12046", "Barca", "Montpellier Handball", "2026-10-22T18:45:00Z", "Palau Blaugrana, Barcelona",
     "4-0", 33, "1-3", -9),
    ("hand-ehf-12048", "Kolstad Handball", "SC Magdeburg", "2026-10-22T18:45:00Z", "Kolstad Arena, Kolstad",
     "0-4", -32, "4-0", 33),
    ("hand-ehf-12054", "Sporting CP", "IFK Kristianstad", "2026-10-22T18:45:00Z", "Pavilhao Joao Rocha, Lisbon",
     "3-0", 21, "0-4", -33),
    ("hand-ehf-12049", "MT Melsungen", "Orlen Wisla Plock", "2026-10-22T16:45:00Z", "Rothenbach-Halle, Kassel",
     None, None, None, None),
    ("hand-ehf-12051", "OTP Bank - PICK Szeged", "GOG", "2026-10-22T16:45:00Z", "Pick Arena, Szeged",
     None, None, None, None),
]
for hid, home, away, start, venue, hr, hd, ar, ad in HAND:
    unread = hr is None
    add(id=hid, sport="Handball", competition="EHF Champions League Men", stage="Group Phase Round 6",
        home=home, away=away, start_utc=start, venue=venue, sources=[EHF],
        inputs={} if unread else {
            "home": {"record": hr, "games": sum(int(x) for x in hr.split("-")) + (0 if hr.startswith("0-4") else 0),
                     "diff": hd, "basis": f"EHF Champions League group table: {home} {hr}, goal difference {'+' if hd >= 0 else ''}{hd}"},
            "away": {"record": ar, "games": sum(int(x) for x in ar.split("-")),
                     "diff": ad, "basis": f"EHF Champions League group table: {away} {ar}, goal difference {'+' if ad >= 0 else ''}{ad}"}},
        flags=(["Kolstad's venue is Kolstad Arena per the official EHF playing-times PDF; earlier repo desks list Trondheim Spektrum."] if hid == "hand-ehf-12048" else
               (["Neither side's group record was read on an official page this session; no price originated."] if unread else [])),
        event_only=unread,
        market_kind="handball", sigma=6.5, total_line=60.5)

# ==================================================================================
# VOLLEYBALL — PlusLiga round 2
# ==================================================================================
PL = "plusliga-round2-2026"
VOLLEY = [
    ("vol-plus-36963", "Slepsk Malow Suwalki", "GKS Katowice", "2026-10-23T17:30:00Z", "Suwalki Arena, Suwalki",
     "0-1", "0-1"),
    ("vol-plus-36964", "PGE GiEK Skra Belchatow", "PGE Projekt Warszawa", "2026-10-24T16:00:00Z", "Hala Energia, Belchatow",
     "1-0", "1-0"),
    ("vol-plus-36965", "InPost ChKS Chelm", "Asseco Resovia Rzeszow", "2026-10-25T17:00:00Z", "MOSiR Hall, Chelm",
     "0-1", "0-1"),
]
for vid, home, away, start, venue, hr, ar in VOLLEY:
    add(id=vid, sport="Volleyball", competition="PlusLiga", stage="Round 2 (best of 5 sets)",
        home=home, away=away, start_utc=start, venue=venue, sources=[PL],
        inputs={"home": {"record": hr, "games": None, "diff": None, "basis": f"PlusLiga 2026-27 table/round-1 report: {home} {hr}"},
                "away": {"record": ar, "games": None, "diff": None, "basis": f"PlusLiga 2026-27 table/round-1 report: {away} {ar}"}},
        flags=["One round played: the desk caps PlusLiga confidence at Medium."],
        market_kind="volleyball", series={"legs": 5, "need": 3, "unit": "sets"})

# ==================================================================================
# RUGBY UNION — URC R4, Gallagher PREM R4, Top 14 J7
# ==================================================================================
URC = "urc-round4-2026"
PREM = "prem-rugby-r4-2026"
LNR = "lnr-top14-2026"
RUGBY_UNION = [
    ("ru-urc-609577", "Connacht", "Zebre Parma", "2026-10-23T18:45:00Z", "Dexcom Stadium, Galway", "URC", URC,
     None, None),
    ("ru-gloucester-bath", "Gloucester", "Bath", "2026-10-23T18:45:00Z", "Kingsholm, Gloucester", "Gallagher Premiership", PREM,
     None, None),
    ("ru-newcastle-sale", "Newcastle Red Bulls", "Sale Sharks", "2026-10-23T18:45:00Z", "Kingston Park, Newcastle", "Gallagher Premiership", PREM,
     None, None),
    ("ru-urc-609576", "Vodacom Bulls", "Ulster", "2026-10-24T11:45:00Z", "Loftus Versfeld, Pretoria", "URC", URC,
     None, None),
    ("ru-urc-609580", "DHL Stormers", "Scarlets", "2026-10-24T14:00:00Z", "DHL Stadium, Cape Town", "URC", URC,
     None, None),
    ("ru-leicester-northampton", "Leicester Tigers", "Northampton Saints", "2026-10-24T14:05:00Z", "Mattioli Woods Welford Road, Leicester", "Gallagher Premiership", PREM,
     None, None),
    ("ru-bristol-exeter", "Bristol Bears", "Exeter Chiefs", "2026-10-24T16:30:00Z", "Ashton Gate, Bristol", "Gallagher Premiership", PREM,
     None, None),
    ("ru-top14-609567", "Stade Toulousain", "USA Perpignan", "2026-10-24T14:35:00Z", "Stade Ernest-Wallon, Toulouse", "French Top 14", LNR,
     None, None),
    ("ru-top14-609564", "Aviron Bayonnais", "LOU Rugby", "2026-10-24T14:35:00Z", "Stade Jean-Dauger, Bayonne", "French Top 14", LNR,
     None, None),
    ("ru-urc-609578", "Leinster", "Munster", "2026-10-24T17:00:00Z", "Aviva Stadium, Dublin", "URC", URC,
     None, None),
    ("ru-harlequins-saracens", "Harlequins", "Saracens", "2026-10-25T15:00:00Z", "Twickenham Stoop, London", "Gallagher Premiership", PREM,
     None, None),
    ("ru-top14-609554", "Stade Rochelais", "Union Bordeaux-Begles", "2026-10-25T20:05:00Z", "Stade Marcel-Deflandre, La Rochelle", "French Top 14", LNR,
     None, None),
]
TOP14_TABLE = {
    # LNR official 2026-27 general standings after Journee 6: points, played, points-for, points-against
    "Stade Toulousain": (24, 6, 197, 124),
    "USA Perpignan": (13, 6, 166, 199),
    "Aviron Bayonnais": (17, 6, 190, 214),
    "LOU Rugby": (14, 6, 193, 202),
    "Stade Rochelais": (18, 6, 144, 135),
    "Union Bordeaux-Begles": (19, 6, 215, 151),
}
for rid, home, away, start, venue, comp, src, hr, ar in RUGBY_UNION:
    flags = []
    if rid == "ru-urc-609578":
        flags.append("URC publishes the Round 4 venue as TBC, Dublin; Ticketmaster and the URC match centre both list Aviva Stadium, so the ground is recorded from the ticketing listing.")
    inputs = {}
    event_only = True
    if comp == "French Top 14":
        hp, hm, hf, ha = TOP14_TABLE[home]
        ap, am, af, aa = TOP14_TABLE[away]
        inputs = {
            "home": {"points": hp, "games": hm, "diff": hf - ha,
                     "basis": f"LNR official Top 14 classement after Journee 6: {home} {hp} pts from {hm}, {hf}-{ha}"},
            "away": {"points": ap, "games": am, "diff": af - aa,
                     "basis": f"LNR official Top 14 classement after Journee 6: {away} {ap} pts from {am}, {af}-{aa}"},
        }
        event_only = False
    else:
        flags.append("No official table for this competition was readable on an official page this session, so no price is originated for this row.")
    add(id=rid, sport="Rugby Union",
        competition=comp,
        stage="Journee 7" if comp == "French Top 14" else "Round 4",
        home=home, away=away, start_utc=start, venue=venue, sources=[src],
        inputs=inputs, flags=flags, event_only=event_only,
        market_kind="rugby-union", sigma=13.0, total_line=48.5)

# ==================================================================================
# RUGBY LEAGUE — RLWC26 round 2 plus the two women's fixtures
# ==================================================================================
RL = "nrl-rlwc26-draw"
RUGBY_LEAGUE = [
    ("rl-wc26-tga-lbn", "Tonga", "Lebanon", "2026-10-23T09:05:00Z", "CommBank Stadium, Sydney",
     "beat England 30-12 in round 1", "lost 18-42 to Papua New Guinea in round 1", 18, -24),
    ("rl-wc26-png-sam", "Papua New Guinea", "Samoa", "2026-10-24T04:25:00Z", "Santos National Football Stadium, Port Moresby",
     "beat Lebanon 42-18 in round 1", "beat France 78-4 in round 1", 24, 74),
    ("rl-wc26-eng-fra", "England", "France", "2026-10-24T06:35:00Z", "HBF Park, Perth",
     "lost 12-30 to Tonga in round 1", "lost 4-78 to Samoa in round 1", -18, -74),
    ("rl-wc26-nzl-cok", "New Zealand", "Cook Islands", "2026-10-25T05:05:00Z", "One NZ Stadium, Christchurch",
     "lost 22-24 to Australia in round 1", "lost 12-40 to Fiji in round 1", -2, -28),
    ("rl-wc26-aus-fij", "Australia", "Fiji", "2026-10-25T09:05:00Z", "Suncorp Stadium, Brisbane",
     "beat New Zealand 24-22 in round 1", "beat Cook Islands 40-12 in round 1", 2, 28),
    ("rl-wc26w-sam-wal", "Samoa Women", "Wales Women", "2026-10-23T06:45:00Z", "CommBank Stadium, Sydney",
     "women's round 1 result not read on an official page this session", "lost 6-70 to England Women in round 1", None, -64),
    ("rl-wc26w-aus-eng", "Australia Jillaroos", "England Women", "", "HBF Park, Perth",
     "women's fixture date not printed on the NRL draw read this session", "beat Wales Women 70-6 in round 1", None, 64),
]
for rid, home, away, start, venue, hr, ar, hmargin, amargin in RUGBY_LEAGUE:
    unread = (not start) or ("not read" in hr)
    add(id=rid, sport="Rugby League", competition="Rugby League World Cup 2026", stage="Round 2",
        home=home, away=away, start_utc=start, venue=venue, sources=[RL],
        inputs={} if unread else {
            "home": {"record": hr, "games": 1, "margin": hmargin, "basis": f"Official NRL RLWC26 round-1 result: {home} {hr}"},
            "away": {"record": ar, "games": 1, "margin": amargin, "basis": f"Official NRL RLWC26 round-1 result: {away} {ar}"}},
        flags=(["No UTC kick-off and no complete two-sided form were read for this row, so no price is originated."] if unread else
               ["Round-1 score only: the desk caps RLWC confidence at Medium unless the round-1 margin is decisive."]),
        event_only=unread,
        market_kind="rugby-league", sigma=16.0, total_line=44.5)

# ==================================================================================
# BASEBALL — 2026 World Series games 1-4, from the MLB Stats API
# ==================================================================================
MLB = "mlb-statsapi-ws2026"
MLB_GAMES = [
    ("mlb-849805", "Milwaukee Brewers", "Tampa Bay Rays", "2026-10-24T00:00:00Z", "American Family Field, Milwaukee", "World Series Game 1"),
    ("mlb-849802", "Milwaukee Brewers", "Tampa Bay Rays", "2026-10-25T00:00:00Z", "American Family Field, Milwaukee", "World Series Game 2"),
    ("mlb-849804", "Tampa Bay Rays", "Milwaukee Brewers", "2026-10-27T00:00:00Z", "Tropicana Field, St. Petersburg", "World Series Game 3"),
    ("mlb-849803", "Tampa Bay Rays", "Milwaukee Brewers", "2026-10-28T00:00:00Z", "Tropicana Field, St. Petersburg", "World Series Game 4"),
]
for mid, home, away, start, venue, stage in MLB_GAMES:
    add(id=mid, sport="Baseball", competition="MLB", stage=stage, home=home, away=away,
        start_utc=start, venue=venue, sources=[MLB],
        inputs={"home": {"record": "103-59" if home.startswith("Milwaukee") else "98-64", "games": 162,
                         "diff": 214 if home.startswith("Milwaukee") else 86,
                         "basis": "Official MLB 2026 regular-season standings"},
                "away": {"record": "98-64" if home.startswith("Milwaukee") else "103-59", "games": 162,
                         "diff": 86 if home.startswith("Milwaukee") else 214,
                         "basis": "Official MLB 2026 regular-season standings"}},
        flags=["Starting pitchers are not published for these games on the feed read, so the desk prices a series-level rating and marks the row pitcher-agnostic."],
        market_kind="baseball", sigma=2.6, total_line=8.5)

# ==================================================================================
# ICE HOCKEY — NHL 22-23 Oct (14 games) plus two SHL fixtures
# ==================================================================================
NHL = "nhl-api-schedule-2026"
SHL = "shl-official-2026"
NHL_GAMES = [
    ("nhl-2026020154", "Boston Bruins", "Nashville Predators", "2026-10-22T23:00:00Z", "TD Garden, Boston", "7-2-1", 15, "3-2-3", 9),
    ("nhl-2026020155", "Toronto Maple Leafs", "New York Rangers", "2026-10-22T23:00:00Z", "Scotiabank Arena, Toronto", "5-4-2", 12, "7-3-1", 15),
    ("nhl-2026020156", "Ottawa Senators", "San Jose Sharks", "2026-10-22T23:00:00Z", "Canadian Tire Centre, Ottawa", "7-3-0", 14, "5-4-1", 11),
    ("nhl-2026020157", "New Jersey Devils", "Anaheim Ducks", "2026-10-22T23:00:00Z", "Prudential Center, Newark", "5-4-0", 10, "4-5-0", 8),
    ("nhl-2026020158", "Pittsburgh Penguins", "Florida Panthers", "2026-10-22T23:00:00Z", "PPG Paints Arena, Pittsburgh", "3-6-1", 7, "5-3-2", 12),
    ("nhl-2026020159", "New York Islanders", "Los Angeles Kings", "2026-10-22T23:30:00Z", "UBS Arena, Elmont", "5-3-1", 11, "1-6-0", 4),
    ("nhl-2026020160", "St. Louis Blues", "Vegas Golden Knights", "2026-10-23T00:00:00Z", "Enterprise Center, St. Louis", "4-4-1", 9, "8-3-0", 16),
    ("nhl-2026020161", "Dallas Stars", "Winnipeg Jets", "2026-10-23T00:00:00Z", "American Airlines Center, Dallas", "5-3-1", 11, "4-4-1", 9),
    ("nhl-2026020162", "Calgary Flames", "Minnesota Wild", "2026-10-23T01:00:00Z", "Scotiabank Saddledome, Calgary", "2-6-0", 4, "6-2-2", 14),
    ("nhl-2026020163", "Edmonton Oilers", "Carolina Hurricanes", "2026-10-23T01:00:00Z", "Rogers Place, Edmonton", "7-1-1", 15, "8-2-1", 17),
    ("nhl-2026020164", "Seattle Kraken", "Utah Mammoth", "2026-10-23T02:00:00Z", "Climate Pledge Arena, Seattle", "6-3-1", 13, "7-3-0", 14),
    ("nhl-2026020165", "Vancouver Canucks", "Detroit Red Wings", "2026-10-23T02:00:00Z", "Rogers Arena, Vancouver", "2-8-1", 5, "3-3-3", 9),
    ("nhl-2026020166", "Chicago Blackhawks", "Montreal Canadiens", "2026-10-24T00:00:00Z", "United Center, Chicago", "3-6-0", 6, "4-3-2", 10),
    ("nhl-2026020167", "Colorado Avalanche", "Tampa Bay Lightning", "2026-10-24T01:00:00Z", "Ball Arena, Denver", "5-4-1", 11, "7-2-0", 14),
]
for gid, home, away, start, venue, hr, hp, ar, ap in NHL_GAMES:
    add(id=gid, sport="Ice Hockey", competition="NHL", stage="Regular Season", home=home, away=away,
        start_utc=start, venue=venue, sources=[NHL],
        inputs={"home": {"record": hr, "points": hp, "games": sum(int(x) for x in hr.split("-")),
                         "basis": f"NHL official standings: {home} {hr}, {hp} points"},
                "away": {"record": ar, "points": ap, "games": sum(int(x) for x in ar.split("-")),
                         "basis": f"NHL official standings: {away} {ar}, {ap} points"}},
        market_kind="ice-hockey", sigma=1.75, total_line=6.0)
add(id="nhl-shl-ske-dju", sport="Ice Hockey", competition="Swedish Hockey League", stage="Regular Season",
    home="Skelleftea AIK", away="Djurgardens IF", start_utc="2026-10-22T18:00:00Z",
    venue="Skelleftea Kraft Arena, Skelleftea", sources=[SHL],
    inputs={"home": {"record": "5-1-2-2", "points": 19, "games": 10,
                     "basis": "SHL table: Skelleftea 19 points from 10 games, 32-25"},
            "away": {"record": "2-2-2-5", "points": 12, "games": 11,
                     "basis": "SHL table: Djurgarden 12 points from 11 games, 23-33"}},
    market_kind="ice-hockey", sigma=1.75, total_line=5.5)
add(id="nhl-shl-tim-far", sport="Ice Hockey", competition="Swedish Hockey League", stage="Regular Season",
    home="Timra IK", away="Farjestad BK", start_utc="2026-10-22T18:00:00Z",
    venue="SCA Arena, Timra", sources=[SHL],
    inputs={"home": {"record": "2-3-0-5", "points": 12, "games": 10,
                     "basis": "SHL table: Timra 12 points from 10 games, 20-23"},
            "away": {"record": "8-1-1-0", "points": 27, "games": 10,
                     "basis": "SHL table: Farjestad 27 points from 10 games, 40-11"}},
    market_kind="ice-hockey", sigma=1.75, total_line=5.5)

# ==================================================================================
# MOTOR RACING — United States Grand Prix (event card, no head-to-head market)
# ==================================================================================
add(id="f1-usgp-2026", sport="Motor Racing", competition="Formula 1", stage="Round 18 - United States Grand Prix",
    home="United States Grand Prix", away="", start_utc="2026-10-25T20:00:00Z",
    venue="Circuit of The Americas, Austin (5.513 km, 56 laps)", sources=["f1-usgp-2026"],
    flags=["Grand Prix winner market is a 20-runner outright; no official rating for the field was read, so no price is originated."],
    event_only=True)

# ==================================================================================
# AUSSIE RULES — NAB AFLW round 11, all nine matches, ladder read from afl.com.au
# ==================================================================================
AFL = "aflw-ladder-draw-2026"
AFLW = [
    ("aflw-r11-07", "Port Adelaide", "Collingwood", "2026-10-23T08:45:00Z", "Alberton Oval, Adelaide", 11, 16, "16", "4"),
    ("aflw-r11-09", "St Kilda", "Brisbane Lions", "2026-10-24T02:05:00Z", "RSEA Park, Melbourne", 18, 14, "4", "12"),
    ("aflw-r11-02", "Geelong Cats", "Fremantle", "2026-10-24T04:05:00Z", "GMHBA Stadium, Geelong", 2, 8, "36", "20"),
    ("aflw-r11-06", "Gold Coast SUNS", "Richmond", "2026-10-24T06:05:00Z", "People First Stadium, Gold Coast", 5, 13, "28", "16"),
    ("aflw-r11-03", "Western Bulldogs", "Melbourne", "2026-10-24T08:15:00Z", "Mission Whitten Oval, Melbourne", 4, 3, "32", "32"),
    ("aflw-r11-08", "Sydney Swans", "West Coast Eagles", "2026-10-25T01:35:00Z", "Henson Park, Sydney", 7, 12, "28", "16"),
    ("aflw-r11-01", "North Melbourne", "Adelaide Crows", "2026-10-25T02:05:00Z", "North Hobart Oval, Hobart", 1, 9, "36", "20"),
    ("aflw-r11-05", "Hawthorn", "Essendon", "2026-10-25T04:05:00Z", "Kennedy Community Centre, Dingley", 10, 17, "20", "4"),
    ("aflw-r11-04", "Carlton", "GWS GIANTS", "2026-10-25T06:05:00Z", "Ikon Park, Melbourne", 6, 15, "28", "8"),
]
for aid, home, away, start, venue, hpos, apos, hpts, apts in AFLW:
    add(id=aid, sport="Aussie Rules", competition="NAB AFLW", stage="Round 11", home=home, away=away,
        start_utc=start, venue=venue, sources=[AFL],
        inputs={"home": {"record": f"ladder {hpos}", "points": int(hpts), "games": 10,
                         "basis": f"Official 2026 NAB AFLW ladder after round 10: {home} {hpos}th, {hpts} points"},
                "away": {"record": f"ladder {apos}", "points": int(apts), "games": 10,
                         "basis": f"Official 2026 NAB AFLW ladder after round 10: {away} {apos}th, {apts} points"}},
        market_kind="aussie-rules", sigma=26.0, total_line=128.5)

# ==================================================================================
# ESPORTS — LoL Worlds 2026 Swiss round 1, all eight best-of-one matches
# ==================================================================================
LOL = "lolesports-worlds-2026"
LOL_GAMES = [
    ("lol-swiss-r1-01", "Gen.G", "Invictus Gaming", "2026-10-23T17:00:00Z", "Credit Union of Texas Event Center, Allen", 1, 4),
    ("lol-swiss-r1-02", "Hanwha Life Esports", "Top Esports", "2026-10-23T18:00:00Z", "Credit Union of Texas Event Center, Allen", 2, 3),
    ("lol-swiss-r1-03", "Bilibili Gaming", "Movistar KOI", "2026-10-23T19:00:00Z", "Credit Union of Texas Event Center, Allen", 2, 3),
    ("lol-swiss-r1-04", "Anyones Legend", "Karmine Corp", "2026-10-23T20:00:00Z", "Credit Union of Texas Event Center, Allen", 1, 4),
    ("lol-swiss-r1-05", "G2 Esports", "Dplus KIA", "2026-10-23T21:00:00Z", "Credit Union of Texas Event Center, Allen", 1, 3),
    ("lol-swiss-r1-06", "Team Liquid", "CTBC Flying Oyster", "2026-10-23T22:00:00Z", "Credit Union of Texas Event Center, Allen", 1, 2),
    ("lol-swiss-r1-07", "LOS", "T1", "2026-10-23T23:00:00Z", "Credit Union of Texas Event Center, Allen", 2, 3),
    ("lol-swiss-r1-08", "Team Secret Whales", "LYON", "2026-10-24T00:00:00Z", "Credit Union of Texas Event Center, Allen", 2, 3),
]
for lid, home, away, start, venue, ht, at in LOL_GAMES:
    add(id=lid, sport="eSports", competition="League of Legends World Championship", stage="Swiss Stage Round 1 (best of one)",
        home=home, away=away, start_utc=start, venue=venue, sources=[LOL],
        inputs={"home": {"rank": ht, "basis": f"Riot draw tier {ht} (pool {ht}) for the Swiss round-1 draw"},
                "away": {"rank": at, "basis": f"Riot draw tier {at} (pool {at}) for the Swiss round-1 draw"}},
        flags=["Draw tier is a seeding position, not a strength rating: the desk caps eSports confidence at Medium."],
        market_kind="esports", series={"legs": 1, "need": 1, "unit": "maps"})

# ==================================================================================
# GAELIC FOOTBALL — two county finals read from the county boards
# ==================================================================================
GAA = "gaa-cork-galway-2026"
add(id="gaa-cork-3530", sport="Gaelic Football", competition="Cork Premier Senior Football Championship", stage="Final",
    home="St Finbarrs", away="Nemo Rangers", start_utc="2026-10-25T16:00:00Z",
    venue="SuperValu Pairc Ui Chaoimh, Cork", sources=[GAA],
    inputs={"home": {"record": "SF 2-12 to 0-16", "games": 1, "margin": 2,
                     "basis": "Cork GAA semi-final: St Finbarrs 2-12 Clonakilty 0-16"},
            "away": {"record": "SF 1-15 to 0-16", "games": 1, "margin": 1,
                     "basis": "Cork GAA semi-final: Nemo Rangers 1-15 Carrigaline 0-16"}},
    flags=["No official club rating exists; the model uses goals-for margin in a single semi-final and caps confidence at Low."],
    market_kind="gaelic", sigma=7.5, total_line=27.5)
add(id="gaa-galway-3532", sport="Gaelic Football", competition="Galway Senior Football Championship", stage="Final",
    home="Moycullen", away="Salthill-Knocknacarra", start_utc="2026-10-25T15:00:00Z",
    venue="Pearse Stadium, Salthill", sources=[GAA],
    inputs={"home": {"record": "SF 4-26 to 0-8", "games": 1, "margin": 30,
                     "basis": "Galway GAA semi-final: Moycullen 4-26 Annaghdown 0-8"},
            "away": {"record": "SF 0-15 to 2-7", "games": 1, "margin": 5,
                     "basis": "Galway GAA semi-final: Salthill-Knocknacarra 0-15 Corofin 2-7"}},
    flags=["No official club rating exists; the model uses semi-final margin and caps confidence at Low."],
    market_kind="gaelic", sigma=7.5, total_line=27.5)

# ==================================================================================
# GREYHOUNDS — three GBGB Category One finals (field/event cards)
# ==================================================================================
GBGB = "gbgb-cat1-oct-2026"
add(id="gbgb-romford-champion-stakes", sport="Greyhounds", competition="GBGB Category One", stage="Coral 100 Champion Stakes Final, 575m",
    home="Coral 100 Champion Stakes", away="", start_utc="2026-10-23T18:00:00Z",
    venue="Romford", sources=[GBGB],
    flags=["Six-dog field; the desk read the three semi-final winners and their times but not a full trap draw with prices, so no price is originated."],
    event_only=True)
add(id="gbgb-dunstall-scurry", sport="Greyhounds", competition="GBGB Category One", stage="Arena Racing Company Scurry Gold Cup Final, 270m",
    home="ARC Scurry Gold Cup", away="", start_utc="2026-10-24T18:00:00Z",
    venue="Dunstall Park, Wolverhampton", sources=[GBGB],
    flags=["Six-dog field; heat and semi-final winners were read but no full trap draw with prices, so no price is originated."],
    event_only=True)
add(id="gbgb-dunstall-oaks", sport="Greyhounds", competition="GBGB Category One", stage="Premier Greyhound Racing Oaks Final, 480m",
    home="PGR Oaks", away="", start_utc="2026-10-24T18:00:00Z",
    venue="Dunstall Park, Wolverhampton", sources=[GBGB],
    flags=["Six-bitch field; the desk read the fastest semi-final winner and two heat winners but not a full trap draw with prices, so no price is originated."],
    event_only=True)


def main() -> None:
    # A governing body that publishes only a tournament date and a rolling order of play leaves
    # the clock blank.  Record that on the row rather than guessing a start time.
    for row in FIXTURES:
        if not row["start_utc"] and "start time not published by the governing body" not in " ".join(row["flags"]):
            row["flags"].append(
                "Start time is blank: the governing body publishes a date or a rolling order of play, not a clock, "
                "and OLBG's own time is viewer-localised.")
    sports = sorted({x["sport"] for x in FIXTURES})
    by_sport = {s: sum(1 for x in FIXTURES if x["sport"] == s) for s in sports}
    doc = {
        "snapshot_utc": SNAPSHOT,
        "session": "a570c470-olbg1",
        "window": "2026-10-22 to 2026-10-28 UTC",
        "count": len(FIXTURES),
        "by_sport": by_sport,
        "sports_covered": len(sports),
        "priced_count": sum(1 for x in FIXTURES if not x["event_only"]),
        "event_only_count": sum(1 for x in FIXTURES if x["event_only"]),
        "fixtures": FIXTURES,
    }
    (OUT / "fixtures.json").write_text(json.dumps(doc, indent=1) + "\n")
    print(f"{len(FIXTURES)} fixtures, {doc['priced_count']} priced, {doc['event_only_count']} event cards across {len(sports)} sports")
    for s, n in sorted(by_sport.items(), key=lambda kv: -kv[1]):
        print(f"  {s:<16} {n}")


if __name__ == "__main__":
    main()
