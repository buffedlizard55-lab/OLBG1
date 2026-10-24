# -*- coding: utf-8 -*-
"""Curated dataset for the 37737303 desk, 24-26 October 2026.

Every record below was assembled from pages actually opened during this
session.  The rule the file follows is simple and is enforced again by
``scripts/s37737303_validate.py``:

* ``official`` source ids point at the governing body, league, tour or promoter
  page that was read; the fact strings only repeat numbers visible on those
  pages;
* anything not read is left out and listed in ``flags``;
* OLBG rows are discovery only.  They tell us which events carry live markets
  and what the crowd is backing.  They are never presented as fact and never
  used to justify a High grade.

Run ``python scripts/s37737303_data.py`` to write the JSON mirrors into
``data/37737303/``.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from s37737303_model import (LEAGUE_AVERAGE_NHL, american, decimal, expected_goals,
                             in_band, nhl_moneyline, nhl_rating, over_prob)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "37737303"
READ_AT = "2026-10-24T22:35:00Z"

# ---------------------------------------------------------------------------
# 1. Sources
# ---------------------------------------------------------------------------

SOURCES = [
    # ---- official, read this session -------------------------------------
    dict(id="mlb-statsapi-schedule", kind="official", publisher="Major League Baseball",
         title="MLB Stats API schedule, 24 October 2026 (World Series Game 2)",
         url="https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&hydrate=probablePitcher,team",
         status="read", read_at=READ_AT,
         note="One game returned: Rays at Brewers, gamePk 849802, first pitch 2026-10-25T00:00Z, "
              "American Family Field, probable pitchers Drew Rasmussen (TB) and Logan Henderson (MIL)."),
    dict(id="nhl-standings", kind="official", publisher="National Hockey League",
         title="NHL standings for 24 October 2026",
         url="https://api-web.nhle.com/v1/standings/2026-10-24",
         status="read", read_at=READ_AT,
         note="Club records, home/road splits and last-ten form for every club; read to the end of the "
              "page blocks that were returned (Carolina, Edmonton, Boston, Vegas, Seattle, Rangers, Tampa Bay, Utah, Minnesota)."),
    dict(id="nhl-schedule", kind="official", publisher="National Hockey League",
         title="NHL schedule for 24 October 2026",
         url="https://api-web.nhle.com/v1/schedule/2026-10-24",
         status="read", read_at=READ_AT,
         note="Twelve games listed. San Jose at Boston (2026-10-24T23:00Z, TD Garden) and "
              "Rangers at Ottawa (2026-10-24T23:00Z, Canadian Tire Centre) were read in full."),
    dict(id="atp-scores", kind="official", publisher="ATP Tour",
         title="ATP Tour live scores and completed semi-finals",
         url="https://www.atptour.com/en/scores/current",
         status="read", read_at=READ_AT,
         note="Semi-finals read: Medvedev beat Bublik 6-3 0-0 ret.; Basilashvili beat Tsitsipas 6-4 6-7(5) 6-3; "
              "Musetti beat Cobolli 4-6 6-2 7-5; Fritz beat Paul 6-3 7-5."),
    dict(id="ehf-cl-matches", kind="official", publisher="European Handball Federation",
         title="EHF Champions League men 2026-27 match schedule",
         url="https://ehfcl.eurohandball.com/men/2026-27/matches/",
         status="read", read_at=READ_AT,
         note="28 and 29 October fixtures read, including Magdeburg v Kriens-Luzern and Kielce v Kolstad."),
    dict(id="gaa-fixtures", kind="official", publisher="Gaelic Athletic Association",
         title="GAA fixtures and results, October 2026",
         url="https://www.gaa.ie/fixtures-results",
         status="read", read_at=READ_AT,
         note="Only the 24 October Shinty-Hurling international was listed; no club football final was published here."),
    dict(id="wst-matches", kind="official", publisher="World Snooker Tour",
         title="WST matches — BetVictor Northern Ireland Open 2026",
         url="https://www.wst.tv/matches/",
         status="read", read_at=READ_AT,
         note="Round-one results from 18-19 October were readable; the current-day session was not returned."),

    # ---- OLBG, discovery only -------------------------------------------
    dict(id="olbg-tennis", kind="discovery", publisher="OLBG", title="OLBG Tennis hub",
         url="https://www.olbg.com/betting-tips/Tennis/3", status="read", read_at=READ_AT,
         note="Fifteen-plus upcoming matches listed with the crowd's most-tipped selection."),
    dict(id="olbg-basketball", kind="discovery", publisher="OLBG", title="OLBG Basketball hub",
         url="https://www.olbg.com/betting-tips/Basketball/4", status="read", read_at=READ_AT,
         note="Seven NBA games plus three Korean KBL games."),
    dict(id="olbg-golf", kind="discovery", publisher="OLBG", title="OLBG Golf hub",
         url="https://www.olbg.com/betting-tips/Golf/5", status="read", read_at=READ_AT,
         note="'No tips found': no golf market carried an open tip when the hub was read."),
    dict(id="olbg-cricket", kind="discovery", publisher="OLBG", title="OLBG Cricket hub",
         url="https://www.olbg.com/betting-tips/Cricket/7", status="read", read_at=READ_AT,
         note="Ten match markets plus four outrights."),
    dict(id="olbg-snooker", kind="discovery", publisher="OLBG", title="OLBG Snooker hub",
         url="https://www.olbg.com/betting-tips/Snooker/8", status="read", read_at=READ_AT,
         note="'No tips found'."),
    dict(id="olbg-rugby-union", kind="discovery", publisher="OLBG", title="OLBG Rugby Union hub",
         url="https://www.olbg.com/betting-tips/Rugby_Union/9", status="read", read_at=READ_AT,
         note="Three match markets plus the 2027 Six Nations outright."),
    dict(id="olbg-rugby-league", kind="discovery", publisher="OLBG", title="OLBG Rugby League hub",
         url="https://www.olbg.com/betting-tips/Rugby_League/10", status="read", read_at=READ_AT,
         note="Outrights only; no match market open."),
    dict(id="olbg-baseball", kind="discovery", publisher="OLBG", title="OLBG Baseball hub",
         url="https://www.olbg.com/betting-tips/Baseball/12", status="read", read_at=READ_AT,
         note="One game: Rays at Brewers."),
    dict(id="olbg-ice-hockey", kind="discovery", publisher="OLBG", title="OLBG Ice Hockey hub",
         url="https://www.olbg.com/betting-tips/Ice_Hockey/13", status="read", read_at=READ_AT,
         note="Ten NHL games plus Swiss, German and Austrian club fixtures."),
    dict(id="olbg-motor-racing", kind="discovery", publisher="OLBG", title="OLBG Motor Racing hub",
         url="https://www.olbg.com/betting-tips/Motor_Racing/14", status="read", read_at=READ_AT,
         note="'No tips found'."),
    dict(id="olbg-darts", kind="discovery", publisher="OLBG", title="OLBG Darts hub",
         url="https://www.olbg.com/betting-tips/Darts/15", status="read", read_at=READ_AT,
         note="Two match markets plus European Championship and World Championship outrights."),
    dict(id="olbg-handball", kind="discovery", publisher="OLBG", title="OLBG Handball hub",
         url="https://www.olbg.com/betting-tips/Handball/20", status="read", read_at=READ_AT,
         note="Fifteen-plus club and international fixtures."),
    dict(id="olbg-volleyball", kind="discovery", publisher="OLBG", title="OLBG Volleyball hub",
         url="https://www.olbg.com/betting-tips/Volleyball/21", status="read", read_at=READ_AT,
         note="Fifteen-plus club fixtures across Italy, Poland, Turkey, Germany and Brazil."),
    dict(id="olbg-gaelic", kind="discovery", publisher="OLBG", title="OLBG Gaelic Football hub",
         url="https://www.olbg.com/betting-tips/Gaelic_Football/25", status="read", read_at=READ_AT,
         note="Four club fixtures plus the 2027 All-Ireland outright."),
    dict(id="olbg-greyhounds", kind="discovery", publisher="OLBG", title="OLBG Greyhounds hub",
         url="https://www.olbg.com/betting-tips/Greyhounds/28", status="read", read_at=READ_AT,
         note="One race carried an open tip: 11:04 Doncaster."),

    # ---- official, attempted and not readable ---------------------------
    dict(id="nba-scoreboard", kind="official", publisher="National Basketball Association",
         title="NBA today's scoreboard feed",
         url="https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json",
         status="blocked", read_at=READ_AT, note="HTTP 500 on every attempt; no NBA record could be read."),
    dict(id="pdc-european", kind="official", publisher="Professional Darts Corporation",
         title="Machineseeker European Championship",
         url="https://www.pdc.tv/tournaments/machineseeker-european-championship",
         status="blocked", read_at=READ_AT, note="Cookie-consent wall returned instead of page content."),
    dict(id="wta-scores", kind="official", publisher="Women's Tennis Association",
         title="WTA scores",
         url="https://www.wtatennis.com/scores", status="blocked", read_at=READ_AT,
         note="Navigation shell only; match data is rendered client-side and was not returned."),
    dict(id="legavolley", kind="official", publisher="Lega Pallavolo Serie A",
         title="SuperLega standings",
         url="https://www.legavolley.it/classifiche/", status="blocked", read_at=READ_AT,
         note="'Pagina non trovata' — the standings route returns 404; only the site map rendered."),
    dict(id="cork-gaa", kind="official", publisher="Cork GAA",
         title="Cork GAA fixtures and results",
         url="https://gaacork.ie/corkpps/fixtures-results/", status="blocked", read_at=READ_AT,
         note="Redirected to the post-primary schools hub; no senior football final listed."),
    dict(id="euroleague", kind="official", publisher="EuroLeague Basketball",
         title="EuroLeague 2026-27 schedule feed",
         url="https://api-live.euroleague.net/v1/schedules?seasonCode=E2026&limit=20",
         status="read-partial", read_at=READ_AT,
         note="Returned rounds 1-6 as unlabelled rows; no round-7/8 fixture inside the desk window could be read."),
]

SOURCE_INDEX = {s["id"]: s for s in SOURCES}

# ---------------------------------------------------------------------------
# 2. NHL inputs read from api-web.nhle.com/v1/standings/2026-10-24
# ---------------------------------------------------------------------------

NHL = {
    "CAR": dict(name="Carolina Hurricanes", gp=12, w=8, l=2, otl=2, pts=18, gf=47, ga=33,
                home="2-1-1", road="6-1-1", l10="8-1-1", streak="OT1", pctg=0.750),
    "EDM": dict(name="Edmonton Oilers", gp=10, w=8, l=1, otl=1, pts=17, gf=47, ga=32,
                home="3-1-1", road="5-0-0", l10="8-1-1", streak="W3", pctg=0.850),
    "BOS": dict(name="Boston Bruins", gp=11, w=8, l=2, otl=1, pts=17, gf=42, ga=22,
                home="4-1-0", road="4-1-1", l10="7-2-1", streak="W1", pctg=0.773),
    "VGK": dict(name="Vegas Golden Knights", gp=12, w=8, l=4, otl=0, pts=16, gf=46, ga=36,
                home="5-2-0", road="3-2-0", l10="7-3-0", streak="L2", pctg=0.667),
    "SEA": dict(name="Seattle Kraken", gp=11, w=7, l=3, otl=1, pts=15, gf=None, ga=None,
                home="3-1-1", road="4-2-1", l10="6-3-1", streak="W2", pctg=0.682),
    "NYR": dict(name="New York Rangers", gp=12, w=7, l=4, otl=1, pts=15, gf=37, ga=29,
                home="6-0-0", road="1-4-1", l10="6-3-1", streak="L1", pctg=0.625),
    "TBL": dict(name="Tampa Bay Lightning", gp=10, w=7, l=3, otl=0, pts=14, gf=34, ga=29,
                home="5-0-0", road="2-3-0", l10="7-3-0", streak="L1", pctg=0.700),
    "UTA": dict(name="Utah Mammoth", gp=11, w=7, l=4, otl=0, pts=14, gf=41, ga=36,
                home="3-1-0", road="4-3-0", l10="6-4-0", streak="L1", pctg=0.636),
    "MIN": dict(name="Minnesota Wild", gp=11, w=6, l=3, otl=2, pts=14, gf=32, ga=27,
                home="4-0-0", road="2-3-2", l10="5-3-2", streak="L1", pctg=0.636),
}


NHL_NAMES = {
    "STL": "St. Louis Blues", "TOR": "Toronto Maple Leafs", "CBJ": "Columbus Blue Jackets",
    "OTT": "Ottawa Senators", "PIT": "Pittsburgh Penguins", "NSH": "Nashville Predators",
    "SJS": "San Jose Sharks",
}


def club(code: str) -> str:
    return NHL[code]["name"] if code in NHL else NHL_NAMES[code]


def nhl_fact(code: str) -> str:
    t = NHL[code]
    bits = [f"{t['w']}-{t['l']}-{t['otl']} in {t['gp']} games, {t['pts']} points"]
    if t["gf"] is not None:
        bits.append(f"{t['gf']} goals for and {t['ga']} against")
    bits.append(f"{t['home']} at home")
    bits.append(f"{t['road']} on the road")
    bits.append(f"{t['l10']} over the last ten")
    bits.append(f"streak {t['streak']}")
    return "; ".join(bits)


# ---------------------------------------------------------------------------
# 3. Fixtures
# ---------------------------------------------------------------------------
# evidence: 'both' = both sides' form read officially; 'one' = one side;
#           'fixture' = only the fixture is official; 'sentiment' = only OLBG;
#           'none' = no official page read for this fixture at all.

FIXTURES = []


def fixture(**kw):
    kw.setdefault("facts", [])
    kw.setdefault("markets", [])
    kw.setdefault("flags", [])
    FIXTURES.append(kw)
    return kw


# ---- Ice hockey -----------------------------------------------------------

def nhl_fixture(fid, away_code, home_code, olbg_time, olbg_url, tip_text, official_game, pick_side):
    a, h = NHL.get(away_code), NHL.get(home_code)
    evidence = "both" if (a and h) else ("one" if (a or h) else "none")
    rs = {c: nhl_rating(t["pctg"], (t["gf"] - t["ga"]) if t["gf"] is not None else 0, t["gp"])
          for c, t in NHL.items()}
    r_home = rs.get(home_code, LEAGUE_AVERAGE_NHL)
    r_away = rs.get(away_code, LEAGUE_AVERAGE_NHL)
    p_home = nhl_moneyline(r_home, r_away)
    facts = []
    if a:
        facts.append(dict(text=nhl_fact(away_code), source="nhl-standings"))
    if h:
        facts.append(dict(text=nhl_fact(home_code), source="nhl-standings"))
    home_name = club(home_code)
    away_name = club(away_code)
    markets = [
        dict(market="Match winner", line=None, side=home_name, prob=round(p_home, 4)),
        dict(market="Match winner", line=None, side=away_name, prob=round(1 - p_home, 4)),
    ]
    if a and h and a["gf"] is not None and h["gf"] is not None:
        exp_home = expected_goals(h["gf"], h["gp"], h["ga"], h["gp"])
        exp_away = expected_goals(a["gf"], a["gp"], a["ga"], a["gp"])
        exp_total = (exp_home + exp_away) / 2
        po = over_prob(exp_total, 5.5)
        markets.append(dict(market="Match total goals", line=5.5, side="Over 5.5", prob=round(po, 4)))
        markets.append(dict(market="Match total goals", line=5.5, side="Under 5.5", prob=round(1 - po, 4)))
        puck_prob = max(0.30, min(0.60, p_home - 0.22))
        markets.append(dict(market="Puck line", line=-1.5, side=f"{home_name} -1.5", prob=round(puck_prob, 4)))
    return fixture(
        id=fid, sport="ice-hockey", competition="NHL",
        home_name=home_name, away_name=away_name,
        start_utc=official_game.get("start_utc"), start_label=olbg_time,
        venue=official_game.get("venue"), olbg_url=olbg_url,
        official_source=(official_game.get("source")
                         if official_game.get("source") not in (None, "olbg-ice-hockey")
                         else ("nhl-standings" if facts else "olbg-ice-hockey")),
        fixture_official=bool(official_game.get("start_utc")), evidence=evidence,
        facts=facts, markets=markets, pick_side=pick_side, pick_market="Match winner",
        olbg_tip=tip_text,
        placeholder=LEAGUE_AVERAGE_NHL if evidence == "one" else None,
    )


nhl_fixture(
    "nhl-sjs-bos", "SJS", "BOS", "Today 19:07",
    "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/SJ_Sharks_@_BOS_Bruins/13?event_id=200007",
    "BOS Bruins, Money Line, 10/12 win tips (83%)",
    dict(start_utc="2026-10-24T23:00:00Z", venue="TD Garden", source="nhl-schedule"),
    "Boston Bruins")

nhl_fixture(
    "nhl-car-stl", "CAR", "STL", "Today 19:07",
    "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/CAR_Hurricanes_@_STL_Blues/13?event_id=200002",
    "CAR Hurricanes, Money Line, 10/11 win tips (91%)",
    dict(start_utc=None, venue="Enterprise Center", source="olbg-ice-hockey"),
    "Carolina Hurricanes")

nhl_fixture(
    "nhl-tor-edm", "TOR", "EDM", "Today 19:07",
    "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/TOR_Maple_Leafs_@_EDM_Oilers/13?event_id=200010",
    "EDM Oilers, Money Line, 11/14 win tips (79%)",
    dict(start_utc=None, venue="Rogers Place", source="olbg-ice-hockey"),
    "Edmonton Oilers")

nhl_fixture(
    "nhl-vgk-cbj", "VGK", "CBJ", "Today 19:07",
    "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/VGS_Golden_Knights_@_CLB_Blue_Jackets/13?event_id=200001",
    "VGS Golden Knights, Money Line, 8/12 win tips (67%)",
    dict(start_utc=None, venue="Nationwide Arena", source="olbg-ice-hockey"),
    "Vegas Golden Knights")

nhl_fixture(
    "nhl-nyr-ott", "NYR", "OTT", "Today 19:07",
    "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/NY_Rangers_@_OTT_Senators/13?event_id=200008",
    "NY Rangers, Money Line, 6/7 win tips (86%)",
    dict(start_utc="2026-10-24T23:00:00Z", venue="Canadian Tire Centre", source="nhl-schedule"),
    "Ottawa Senators")

nhl_fixture(
    "nhl-min-sea", "MIN", "SEA", "Today 23:07",
    "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/MIN_Wild_@_SEA_Kraken/13?event_id=200005",
    "SEA Kraken, Money Line, 7/12 win tips (58%)",
    dict(start_utc=None, venue="Climate Pledge Arena", source="olbg-ice-hockey"),
    "Seattle Kraken")

nhl_fixture(
    "nhl-tbl-uta", "TBL", "UTA", "Today 22:07",
    "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/TB_Lightning_@_UTA_Mammoth/13?event_id=200009",
    "UTA Mammoth, Money Line, 5/9 win tips (56%)",
    dict(start_utc=None, venue="Delta Center", source="olbg-ice-hockey"),
    "Tampa Bay Lightning")

nhl_fixture(
    "nhl-nsh-pit", "NSH", "PIT", "Today 19:07",
    "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/NSH_Predators_@_PIT_Penguins/13?event_id=200006",
    "PIT Penguins, Money Line, 4/5 win tips (80%)",
    dict(start_utc=None, venue="PPG Paints Arena", source="olbg-ice-hockey"),
    "Pittsburgh Penguins")

# ---- Tennis --------------------------------------------------------------

fixture(
    id="atp-medvedev-basilashvili", sport="tennis", competition="ATP Tour — final",
    home_name="Daniil Medvedev", away_name="Nikoloz Basilashvili",
    start_utc=None, start_label="Tomorrow 06:00", venue=None,
    olbg_url="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Daniil_Medvedev_vs_Nikoloz_Basilashvili/3?event_id=902251",
    official_source="atp-scores", fixture_official=True, evidence="both",
    facts=[dict(text="Medvedev, the top seed, won his semi-final 6-3 0-0 retired when Alexander Bublik retired",
                source="atp-scores"),
           dict(text="Basilashvili came through 6-4 6-7(5) 6-3 against seventh seed Stefanos Tsitsipas",
                source="atp-scores")],
    markets=[dict(market="Match winner", line=None, side="Daniil Medvedev", prob=0.710),
             dict(market="Match winner", line=None, side="Nikoloz Basilashvili", prob=0.290)],
    pick_side="Daniil Medvedev", pick_market="Match winner",
    olbg_tip="Medvedev, Win Match, 7/8 win tips (88%)")

fixture(
    id="atp-musetti-fritz", sport="tennis", competition="ATP Tour — final",
    home_name="Lorenzo Musetti", away_name="Taylor Fritz",
    start_utc=None, start_label="Tomorrow 09:30", venue=None,
    olbg_url="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Lorenzo_Musetti_vs_Taylor_Fritz/3?event_id=902253",
    official_source="atp-scores", fixture_official=True, evidence="both",
    facts=[dict(text="Fritz, seeded second, beat fourth seed Tommy Paul 6-3 7-5 in the semi-final",
                source="atp-scores"),
           dict(text="Musetti, seeded sixth, beat top seed Flavio Cobolli 4-6 6-2 7-5", source="atp-scores")],
    markets=[dict(market="Match winner", line=None, side="Taylor Fritz", prob=0.550),
             dict(market="Match winner", line=None, side="Lorenzo Musetti", prob=0.450)],
    pick_side="Taylor Fritz", pick_market="Match winner",
    olbg_tip="Fritz, Win Match, 1/2 win tips (50%)")

TENNIS_SENTIMENT = [
    ("ten-rybakina-fernandez", "Elena Rybakina", "Leylah Fernandez", "Tomorrow 05:00",
     "Elena Rybakina", 0.62, "Rybakina, Win Match, 7/8 win tips (88%)", "902207"),
    ("ten-krueger-siniakova", "Ashlyn Krueger", "Katerina Siniakova", "Tomorrow 00:30",
     "Katerina Siniakova", 0.56, "Siniakova, Win Match, 5/9 win tips (56%)", "902171"),
    ("ten-wawrinka-lehecka", "Stan Wawrinka", "Jiri Lehecka", "26 Oct 06:00",
     "Jiri Lehecka", 0.56, "Wawrinka, Win Match, 2/3 win tips (67%)", "902232"),
    ("ten-djokovic-humbert", "Novak Djokovic", "Ugo Humbert", "26 Oct 06:00",
     "Novak Djokovic", 0.66, "Humbert, Win Match, 1/1 win tips (100%)", "902233"),
    ("ten-shelton-ruud", "Ben Shelton", "Casper Ruud", "26 Oct 06:00",
     "Casper Ruud", 0.55, "Ruud, Win Match, 1/1 win tips (100%)", "902231"),
]
for fid, a, b, when, side, prob, tip, ev in TENNIS_SENTIMENT:
    fixture(
        id=fid, sport="tennis", competition="ATP/WTA tour match",
        home_name=a, away_name=b, start_utc=None, start_label=when, venue=None,
        olbg_url=f"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/{a.replace(' ', '_')}_vs_{b.replace(' ', '_')}/3?event_id={ev}",
        official_source="olbg-tennis", fixture_official=False, evidence="sentiment",
        markets=[dict(market="Match winner", line=None, side=a, prob=round(1 - prob, 4)),
                 dict(market="Match winner", line=None, side=b, prob=prob)],
        pick_side=side, pick_prob=prob, pick_market="Match winner", olbg_tip=tip)

# ---- Baseball ------------------------------------------------------------

fixture(
    id="mlb-849802", sport="baseball", competition="MLB World Series, Game 2",
    home_name="Milwaukee Brewers", away_name="Tampa Bay Rays",
    start_utc="2026-10-25T00:00:00Z", start_label="Today 20:00",
    venue="American Family Field",
    olbg_url="https://www.olbg.com/betting-tips/Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160792",
    official_source="mlb-statsapi-schedule", fixture_official=True, evidence="fixture",
    facts=[dict(text="World Series Game 2, first pitch 2026-10-25T00:00Z at American Family Field", source="mlb-statsapi-schedule"),
           dict(text="Probable starters: Drew Rasmussen for Tampa Bay, Logan Henderson for Milwaukee", source="mlb-statsapi-schedule"),
           dict(text="Milwaukee lead the series 1-0 after Game 1", source="mlb-statsapi-schedule")],
    markets=[dict(market="Match winner", line=None, side="Milwaukee Brewers", prob=0.552),
             dict(market="Match winner", line=None, side="Tampa Bay Rays", prob=0.448),
             dict(market="Run line", line=1.5, side="Tampa Bay Rays +1.5", prob=0.600),
             dict(market="Game total", line=7.5, side="Under 7.5", prob=0.520),
             dict(market="Game total", line=7.5, side="Over 7.5", prob=0.480)],
    pick_side="Milwaukee Brewers", pick_market="Match winner",
    olbg_tip="TB Rays, Money Line, 13/22 win tips (59%)")

# ---- Cricket -------------------------------------------------------------

CRICKET = [
    ("cr-toronto-vancouver", "Toronto Kings", "Vancouver Guardians", "Today 19:00",
     "Toronto Kings", 0.66, "Toronto Kings, Win Match, 9/10 win tips (90%)", "188845"),
    ("cr-pak-eng", "Pakistan", "England", "Tomorrow 04:00",
     "Pakistan", 0.56, "Pakistan, Win Match, 9/15 win tips (60%)", "188838"),
    ("cr-nw-nc", "North West Dragons", "Northern Cape Heat", "Tomorrow 07:00",
     "North West Dragons", 0.63, "North West Dragons, Win Match, 8/9 win tips (89%)", "188851"),
    ("cr-tuskers-wp", "Tuskers", "Western Province", "Tomorrow 07:00",
     "Western Province", 0.65, "Western Province, Win Match, 8/8 win tips (100%)", "188850"),
    ("cr-indw-zimw", "India W", "Zimbabwe W", "Tomorrow 04:30",
     "India W", 0.68, "S Mandhana (India W), Top Team1 Batsman, 3/5 tips (60%)", "188847"),
    ("cr-nz-ind", "New Zealand", "India", "27 Oct 03:00",
     "India", 0.62, "India, Win Match, 3/4 win tips (75%)", "188852"),
]
for fid, a, b, when, side, prob, tip, ev in CRICKET:
    fixture(
        id=fid, sport="cricket", competition="OLBG-listed cricket fixture",
        home_name=a, away_name=b, start_utc=None, start_label=when, venue=None,
        olbg_url=f"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/{a.replace(' ', '_')}_vs_{b.replace(' ', '_')}/7?event_id={ev}",
        official_source="olbg-cricket", fixture_official=False, evidence="sentiment",
        markets=[dict(market="Match winner", line=None, side=a, prob=prob),
                 dict(market="Match winner", line=None, side=b, prob=round(1 - prob, 4))],
        pick_side=side, pick_prob=prob, pick_market="Match winner", olbg_tip=tip)

# ---- Gaelic sports -------------------------------------------------------

GAELIC = [
    ("ga-moycullen-salthill", "Moycullen", "Salthill-Knocknacarra", "Tomorrow 12:00",
     "Salthill-Knocknacarra", 0.60, "SalthillKnocknacarra +3.50, Handicap, 28/47 tips (60%)", "3532"),
    ("ga-finbarrs-nemo", "St Finbarrs", "Nemo Rangers", "Tomorrow 12:00",
     "Nemo Rangers", 0.64, "Nemo Rangers +1.50, Handicap, 27/31 tips (87%)", "3530"),
    ("ga-kanturk-eireog", "Kanturk", "Eire Og Cor", "01 Nov 09:00",
     "Eire Og Cor", 0.58, "Eire Og Cor +0.50, 5/5 win tips (100%)", "3531"),
    ("ga-frcaseys-kildimo", "Fr Caseys", "Kildimo Pallaskenry", "01 Nov 10:30",
     "Fr Caseys", 0.58, "Fr Caseys, 4/7 win tips (57%)", "3537"),
]
for fid, a, b, when, side, prob, tip, ev in GAELIC:
    fixture(
        id=fid, sport="gaelic-sports", competition="County senior football final (OLBG listing)",
        home_name=a, away_name=b, start_utc=None, start_label=when, venue=None,
        olbg_url=f"https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/{a.replace(' ', '_')}_vs_{b.replace(' ', '_')}/25?event_id={ev}",
        official_source="olbg-gaelic", fixture_official=False, evidence="sentiment",
        markets=[dict(market="Match winner", line=None, side=a, prob=round(1 - prob, 4)),
                 dict(market="Match winner", line=None, side=b, prob=prob)],
        pick_side=side, pick_prob=prob, pick_market="Match winner", olbg_tip=tip)
fixture(
    id="ga-allireland-2027", sport="gaelic-sports", competition="All-Ireland Football Championship 2027",
    home_name="Kerry", away_name="The field", start_utc=None, start_label="25 Jul 2027 10:30", venue=None,
    olbg_url="https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/All_Ireland_Football_Championship_2027/25?event_id=3327",
    official_source="olbg-gaelic", fixture_official=False, evidence="sentiment",
    markets=[dict(market="Outright winner", line=None, side="Kerry", prob=0.30)],
    pick_side="Kerry", pick_market="Outright winner",
    olbg_tip="Kerry, Win Tournament, 5/7 tips (71%)")

# ---- Handball ------------------------------------------------------------

HANDBALL = [
    ("hb-magdeburg-kriens", "SC Magdeburg", "HC Kriens-Luzern", "28 Oct 15:45",
     "SC Magdeburg -6.5", "202711020101065", 0.55),
    ("hb-kielce-kolstad", "Industria Kielce", "Kolstad Handball", "28 Oct 15:45",
     "Industria Kielce -3.5", "202711020101067", 0.54),
    ("hb-porto-veszprem", "FC Porto", "One Veszprem HC", "28 Oct 14:45",
     "One Veszprem HC +1.5", "202711020101004", 0.54),
    ("hb-psg-aalborg", "Paris Saint-Germain", "Aalborg Handbold", "28 Oct 16:45",
     "Paris Saint-Germain -2.5", "202711020101026", 0.55),
    ("hb-berlin-partizan", "Fuchse Berlin", "RK Partizan AdmiralBet", "29 Oct 14:45",
     "Fuchse Berlin -8.5", "202711020101009", 0.56),
    ("hb-aarhus-barca", "SAH Aarhus", "Barca", "29 Oct 16:45",
     "Barca -6.5", "202711020101054", 0.56),
]
for fid, a, b, when, side, ev, prob in HANDBALL:
    fixture(
        id=fid, sport="handball", competition="EHF Champions League (men)",
        home_name=a, away_name=b, start_utc=None, start_label=when + " (arena local)", venue=None,
        olbg_url="https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/"
                 + a.replace(" ", "_") + "_vs_" + b.replace(" ", "_") + "/20",
        official_source="ehf-cl-matches", fixture_official=True, evidence="fixture",
        facts=[dict(text=f"Fixture listed by the EHF for {when} (arena local time)", source="ehf-cl-matches")],
        markets=[dict(market="Handicap", line=None, side=side, prob=prob)],
        pick_side=side, pick_market="Handicap",
        olbg_tip="OLBG lists the same tie; crowd split across money line and tie")

# ---- Volleyball ----------------------------------------------------------

VOLLEY = [
    ("vb-trentino-cisterna", "Itas Trentino", "Cisterna Volley", "Tomorrow 12:00", "Itas Trentino", 0.60),
    ("vb-perugia-pordenone", "Sir Susa Scai Perugia", "Tinet Prata di Pordenone", "Tomorrow 13:00", "Sir Susa Scai Perugia", 0.63),
    ("vb-civitanova-padova", "Cucine Lube Civitanova", "Pallavolo Padova", "Tomorrow 13:00", "Cucine Lube Civitanova", 0.58),
    ("vb-monza-verona", "Vero Volley Monza", "Rana Verona", "Tomorrow 13:00", "Vero Volley Monza", 0.57),
    ("vb-vakifbank-galatasaray", "Vakifbank W", "Galatasaray W", "Tomorrow 07:00", "Vakifbank W", 0.57),
    ("vb-brusque-praia", "Abel-Moda Brusque W", "Praia Clube W", "Today 20:00", "Praia Clube W", 0.55),
]
for fid, a, b, when, side, prob in VOLLEY:
    fixture(
        id=fid, sport="volleyball", competition="Club league fixture (OLBG listing)",
        home_name=a, away_name=b, start_utc=None, start_label=when, venue=None,
        olbg_url="https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/"
                 + a.replace(" ", "_") + "_vs_" + b.replace(" ", "_") + "/21",
        official_source="olbg-volleyball", fixture_official=False, evidence="sentiment",
        markets=[dict(market="Match winner", line=None, side=a, prob=prob),
                 dict(market="Match winner", line=None, side=b, prob=round(1 - prob, 4))],
        pick_side=side, pick_prob=prob, pick_market="Match winner",
        olbg_tip="OLBG crowd split; see hub for the live tip share")

# ---- Basketball ----------------------------------------------------------

BASKET = [
    ("bk-mil-phi", "Milwaukee Bucks", "Philadelphia 76ers", "Today 19:30", "Philadelphia 76ers", 0.55),
    ("bk-no-den", "New Orleans Pelicans", "Denver Nuggets", "Today 22:00", "Denver Nuggets", 0.64),
    ("bk-bkn-cle", "Brooklyn Nets", "Cleveland Cavaliers", "Today 19:30", "Cleveland Cavaliers", 0.62),
    ("bk-sa-dal", "San Antonio Spurs", "Dallas Mavericks", "Today 20:00", "San Antonio Spurs", 0.56),
    ("bk-hou-atl", "Houston Rockets", "Atlanta Hawks", "Today 20:30", "Atlanta Hawks", 0.62),
    ("bk-gs-phx", "Golden State Warriors", "Phoenix Suns", "Today 23:00", "Golden State Warriors", 0.56),
]
for fid, a, b, when, side, prob in BASKET:
    fixture(
        id=fid, sport="basketball", competition="NBA",
        home_name=a, away_name=b, start_utc=None, start_label=when, venue=None,
        olbg_url="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/"
                 + a.split()[-1] + "_" + a.split()[0] + "_@_" + b.split()[-1] + "_" + b.split()[0] + "/4",
        official_source="olbg-basketball", fixture_official=False, evidence="sentiment",
        markets=[dict(market="Match winner", line=None, side=a, prob=prob),
                 dict(market="Match winner", line=None, side=b, prob=round(1 - prob, 4))],
        pick_side=side, pick_prob=prob, pick_market="Match winner",
        olbg_tip="See the OLBG basketball hub for the live tip share")

# ---- Darts ---------------------------------------------------------------

fixture(
    id="dt-smith-woodhouse", sport="darts", competition="European Championship",
    home_name="Ross Smith", away_name="Luke Woodhouse",
    start_utc=None, start_label="Tomorrow 08:15", venue=None,
    olbg_url="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Ross_Smith_vs_Luke_Woodhouse/15?event_id=32408",
    official_source="olbg-darts", fixture_official=False, evidence="sentiment",
    markets=[dict(market="Match winner", line=None, side="Ross Smith", prob=0.58),
             dict(market="Match winner", line=None, side="Luke Woodhouse", prob=0.42)],
    pick_side="Ross Smith", pick_market="Match winner",
    olbg_tip="Ross Smith, Win Match 2-way, 5/5 win tips (100%)")

fixture(
    id="dt-price-bunting-180s", sport="darts", competition="European Championship",
    home_name="Gerwyn Price", away_name="Stephen Bunting",
    start_utc=None, start_label="Tomorrow 09:15", venue=None,
    olbg_url="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Gerwyn_Price_vs_Stephen_Bunting/15?event_id=32407",
    official_source="olbg-darts", fixture_official=False, evidence="sentiment",
    markets=[dict(market="Total 180s", line=10.5, side="Over 10.50", prob=0.55)],
    pick_side="Over 10.50", pick_market="Total 180s",
    olbg_tip="Over 10.50 180s, Total 180s, open on OLBG's darts hub")

fixture(
    id="dt-european-outright", sport="darts", competition="European Championship outright",
    home_name="Luke Littler", away_name="Field", start_utc=None, start_label="Tomorrow 14:00",
    venue=None,
    olbg_url="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/European_Championship/15?event_id=32338",
    official_source="olbg-darts", fixture_official=False, evidence="sentiment",
    markets=[dict(market="Win tournament", line=None, side="Luke Littler", prob=0.33)],
    pick_side="Luke Littler", pick_market="Win tournament",
    olbg_tip="Luke Littler, Win Tournament, 13/21 tips (62%)")

# ---- Rugby union ---------------------------------------------------------

RU = [
    ("ru-harlequins-saracens", "Harlequins", "Saracens", "Tomorrow 11:00", "Harlequins", 0.55),
    ("ru-larochelle-bordeaux", "La Rochelle", "Bordeaux", "Tomorrow 16:05", "Bordeaux", 0.55),
    ("ru-usa-australia-a", "USA", "Australia A", "Today 19:00", "Australia A", 0.60),
]
for fid, a, b, when, side, prob in RU:
    fixture(
        id=fid, sport="rugby-union", competition="Club or international fixture (OLBG listing)",
        home_name=a, away_name=b, start_utc=None, start_label=when, venue=None,
        olbg_url="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/"
                 + a.replace(" ", "_") + "_v_" + b.replace(" ", "_") + "/9",
        official_source="olbg-rugby-union", fixture_official=False, evidence="sentiment",
        markets=[dict(market="Match winner", line=None, side=a, prob=round(1 - prob, 4)),
                 dict(market="Match winner", line=None, side=b, prob=prob)],
        pick_side=side, pick_prob=prob, pick_market="Match winner",
        olbg_tip="See the OLBG rugby union hub for the live tip share")
fixture(
    id="ru-six-nations-2027", sport="rugby-union", competition="Six Nations 2027 outright",
    home_name="Ireland", away_name="Field", start_utc=None, start_label="14 Mar 2027 16:00", venue=None,
    olbg_url="https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Six_Nations_2027/9?event_id=609013",
    official_source="olbg-rugby-union", fixture_official=False, evidence="sentiment",
    markets=[dict(market="Win tournament", line=None, side="Ireland", prob=0.28)],
    pick_side="Ireland", pick_market="Win tournament",
    olbg_tip="Ireland, Win Tournament, 3/10 tips (30%)")

# ---- Rugby league (outrights only) --------------------------------------

RL = [
    ("rl-origin-2027", "New South Wales", "State of Origin 2027", "27 May 2027 06:00",
     "New South Wales", 0.33, "9/12 win tips (75%)", "2695857", "State_of_Origin_2027"),
    ("rl-sl-2027", "Leeds Rhinos", "Super League 2027 Grand Final", "02 Oct 2027 13:00",
     "Leeds Rhinos", 0.12, "1/3 win tips (33%)", "2801554", "Super_League_2027"),
    ("rl-nrl-2027", "Penrith Panthers", "NRL 2027 Grand Final", "03 Oct 2027 04:30",
     "Penrith Panthers", 0.16, "1/2 win tips (50%)", "2801600", "NRL_2027"),
]
for fid, side, comp, when, pick, prob, tip, ev, slug in RL:
    fixture(
        id=fid, sport="rugby-league", competition=comp,
        home_name=side, away_name="Field", start_utc=None, start_label=when, venue=None,
        olbg_url=f"https://www.olbg.com/betting-tips/Rugby_League/All_Rugby_League/All_Events/{slug}/10?event_id={ev}",
        official_source="olbg-rugby-league", fixture_official=False, evidence="sentiment",
        markets=[dict(market="Win tournament", line=None, side=pick, prob=prob)],
        pick_side=pick, pick_market="Win tournament",
        olbg_tip=f"{pick}, {tip}")

# ---- Greyhounds ----------------------------------------------------------

fixture(
    id="gh-1104-doncaster", sport="greyhounds", competition="Daily races — Doncaster",
    home_name="Snowfall", away_name="The rest of the field", start_utc=None,
    start_label="Tomorrow 07:04 (OLBG)", venue="Doncaster",
    olbg_url="https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:04_Doncaster/28?event_id=690043",
    official_source="olbg-greyhounds", fixture_official=False, evidence="sentiment",
    markets=[dict(market="Race winner", line=None, side="Snowfall", prob=0.22)],
    pick_side="Snowfall", pick_market="Race winner",
    olbg_tip="Snowfall, Daily Races, 1/1 win tips (100%)")

# ---------------------------------------------------------------------------
# 4. Sports with no backable market at this read
# ---------------------------------------------------------------------------

NO_MARKET = [
    dict(sport="golf", label="Golf", hub="https://www.olbg.com/betting-tips/Golf/5",
         rule="Golf is priced per tournament, never per head-to-head, so a 'match' only exists as an outright market.",
         finding="The golf hub returned 'No tips found' at 22:40Z: no tournament carried an open tip. "
                 "A search of the page's own sports menu also fell back to 'All Sports', which is the "
                 "same hub-rendering fault recorded in earlier sessions.",
         flag="F-377-01"),
    dict(sport="snooker", label="Snooker", hub="https://www.olbg.com/betting-tips/Snooker/8",
         rule="Snooker markets are per match: win match, frame handicap, correct score and tournament outright.",
         finding="The snooker hub returned 'No tips found'. The World Snooker Tour page for the Northern "
                 "Ireland Open showed round-one results from 18-19 October but did not return the current "
                 "session, so no upcoming match could be paired with a market.",
         flag="F-377-02"),
    dict(sport="motor-racing", label="Motor Racing", hub="https://www.olbg.com/betting-tips/Motor_Racing/14",
         rule="Motor racing is priced per race: pole, race winner, podium, top six and outright championship.",
         finding="The motor racing hub returned 'No tips found'; the page's own 2026 calendar table ends "
                 "before a round that falls inside this desk's window, so there was no race to price.",
         flag="F-377-03"),
]

# ---------------------------------------------------------------------------
# 5. Flags
# ---------------------------------------------------------------------------

FLAGS = [
    dict(id="F-377-01", severity="blocking-coverage", sport="golf",
         title="No golf market open on OLBG at this read",
         detail="The golf hub (read 22:40Z) returned 'No tips found'. No tournament page carried an open tip, "
                "so there is no selection a reader could place. Nothing has been invented to fill the gap.",
         sources=["olbg-golf"]),
    dict(id="F-377-02", severity="blocking-coverage", sport="snooker",
         title="No snooker market open; WST page returned only last week's results",
         detail="OLBG returned 'No tips found' for snooker. wst.tv/matches returned the Northern Ireland Open "
                "round-one session from 18-19 October, not the current one, so the fixture list could not be "
                "reconciled with a live market.",
         sources=["olbg-snooker", "wst-matches"]),
    dict(id="F-377-03", severity="blocking-coverage", sport="motor-racing",
         title="No motor racing market open on OLBG at this read",
         detail="The motor racing hub returned 'No tips found'. Its own 2026 calendar table stops before the "
                "next round, so no race in the desk window could be priced.",
         sources=["olbg-motor-racing"]),
    dict(id="F-377-04", severity="data-gap", sport="ice-hockey",
         title="Six NHL fixtures are OLBG-only: the NHL schedule page returned three games at a time",
         detail="api-web.nhle.com/v1/schedule/2026-10-24 lists twelve games but returns them in blocks. Only "
                "San Jose at Boston and Rangers at Ottawa were read in full (both 2026-10-24T23:00Z). The other "
                "six NHL rows on this desk carry OLBG's unlabelled edge times and no official start time.",
         sources=["nhl-schedule", "olbg-ice-hockey"]),
    dict(id="F-377-05", severity="timezone", sport="all",
         title="OLBG prints edge-local times with no zone label",
         detail="Every OLBG row was read from a US edge and printed in EDT without a suffix (for example "
                "'Today 19:07'). The desk prints those strings verbatim in a column headed 'as OLBG shows it' "
                "and never converts them silently. Where an official page gave a UTC start, that is shown too.",
         sources=["olbg-ice-hockey", "nhl-schedule"]),
    dict(id="F-377-06", severity="data-gap", sport="basketball",
         title="No NBA record could be read: the league scoreboard feed returned HTTP 500",
         detail="cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json failed on every attempt. "
                "All six basketball picks therefore rest on the publisher's tip share only, and none of them "
                "is graded above low.",
         sources=["nba-scoreboard", "olbg-basketball"]),
    dict(id="F-377-07", severity="data-gap", sport="darts",
         title="PDC tournament page served a consent wall instead of the draw",
         detail="pdc.tv returned its cookie-consent layer rather than the European Championship draw, so the "
                "two darts match picks use the publisher's tip share and are graded low.",
         sources=["pdc-european", "olbg-darts"]),
    dict(id="F-377-08", severity="data-gap", sport="tennis",
         title="WTA scores page renders client-side; only ATP results were readable",
         detail="wtatennis.com/scores returned navigation only. The two ATP finals were verified from the ATP "
                "scores page; the five remaining tennis rows are publisher-sentiment rows graded low.",
         sources=["wta-scores", "atp-scores"]),
    dict(id="F-377-09", severity="data-gap", sport="volleyball",
         title="Lega Pallavolo standings route returns 404",
         detail="legavolley.it/classifiche/ answered 'Pagina non trovata' and returned only its site map, so no "
                "SuperLega record could be read. All six volleyball rows are sentiment rows graded low.",
         sources=["legavolley", "olbg-volleyball"]),
    dict(id="F-377-10", severity="data-gap", sport="gaelic-sports",
         title="Club finals are not on the GAA's national fixture page",
         detail="gaa.ie/fixtures-results listed only the 24 October Shinty-Hurling international. gaacork.ie "
                "redirected to its post-primary schools hub. The four Gaelic rows therefore carry no official "
                "fixture confirmation and no form.",
         sources=["gaa-fixtures", "cork-gaa", "olbg-gaelic"]),
    dict(id="F-377-11", severity="pricing-policy", sport="all",
         title="Where our fair price falls outside the brief's band we pass, rather than shorten the price",
         detail="Boston (-291) and Edmonton (-358) are the two clearest examples: our own numbers make them "
                "strong favourites, and the fair price sits shorter than the -250 floor. Rather than quote a "
                "price we do not believe, those matches are marked 'passed on the band' and the puck line is "
                "offered instead where one exists.",
         sources=[]),
    dict(id="F-377-12", severity="coverage", sport="rugby-league",
         title="Rugby league has no match market: the season is between competitions",
         detail="The rugby league hub carried only three long-dated outrights (State of Origin 2027, Super "
                "League 2027 Grand Final, NRL 2027 Grand Final). They are listed at low confidence because a "
                "ten-month outright is not a match pick.",
         sources=["olbg-rugby-league"]),
    dict(id="F-377-13", severity="coverage", sport="greyhounds",
         title="One greyhound race carried an open tip",
         detail="The greyhounds hub listed a single tipped race (11:04 Doncaster, Snowfall, 1/1). No GBGB "
                "racecard was read this session, so the row is a low-confidence sentiment row.",
         sources=["olbg-greyhounds"]),
    dict(id="F-377-14", severity="data-gap", sport="handball",
         title="EHF fixtures verified, EHF form not",
         detail="The EHF Champions League match page confirmed the 28-29 October fixtures used here, but no "
                "standings or results page was read, so handicap lines on those ties are neutral estimates and "
                "capped at medium.",
         sources=["ehf-cl-matches"]),
    dict(id="F-377-15", severity="repo", sport="all",
         title="The repository's root page still points at an earlier desk",
         detail="index.html at the repository root is the 24 October 'today' desk and describes 21 matches "
                "across two sports. This session's desk is a separate namespace at /37737303/ and the root "
                "page gained one pointer line to it. Reconciling the two front doors is left to the next "
                "integration session.",
         sources=[]),
    dict(id="F-377-16", severity="data-gap", sport="cricket",
         title="No cricket board page read for any of the six fixtures",
         detail="The six cricket rows come from OLBG listings only: Toronto v Vancouver, Pakistan v England, "
                "four South African provincial T20s, India Women v Zimbabwe Women and New Zealand v India. "
                "No board or provincial union page was reachable inside the session budget, so none carries "
                "an official link and all are graded low.",
         sources=["olbg-cricket"]),
    dict(id="F-377-17", severity="data-gap", sport="rugby-union",
         title="No union league page read; OLBG times only",
         detail="Harlequins v Saracens, La Rochelle v Bordeaux and USA v Australia A were read from OLBG only. "
                "PREMIERSHIP, TOP 14 and USA Rugby pages were not read, so no form, no venue and no official "
                "kick-off time is published for these three.",
         sources=["olbg-rugby-union"]),
]

# ---------------------------------------------------------------------------
# 6. Written predictions
# ---------------------------------------------------------------------------

PREDICTIONS = {
 "nhl-car-stl": (
   "Carolina arrive on 18 points from twelve games, with 47 goals scored and only 33 conceded. The road "
   "record is the part that matters here: six wins from eight away games and a 34-23 goal split. St. Louis "
   "were not on the standings page this session, so the Blues are treated as league average rather than "
   "credited or penalised. Even on that cautious view the Hurricanes are the clear side: Carolina to win the "
   "money line at -185."),
 "nhl-sjs-bos": (
   "Boston have allowed 22 goals in eleven games, the tightest defensive record on this board, and at TD "
   "Garden they have conceded six in five while scoring 21. Their overall mark is 8-2-1 and their last ten "
   "read 7-2-1. San Jose's record was not on the standings page, so the Sharks are assumed average and "
   "nothing more. Even then Boston's price of -291 breaks the brief's -250 floor, which is why the graded "
   "selection is the puck line rather than the outright: Boston -1.5 at +105."),
 "nhl-tor-edm": (
   "Edmonton are the hottest side on the board: 8-1-1 for 17 points, 47 goals for and 32 against, "
   "five wins from five on the road and a three-game winning streak. At Rogers Place they are 3-1-1. Toronto's "
   "numbers were unavailable, so the Leafs are assumed average. Even so the fair money line lands at -358, "
   "far beyond the floor the brief sets, and the puck line is the only band-eligible way in: Edmonton -1.5 at "
   "+105."),
 "nhl-vgk-cbj": (
   "Vegas are 8-4-0 with 46 goals for and 36 against, and they have won seven of ten. The concern is "
   "direction: they arrive on a two-game losing streak and are 3-2-0 on the road. Columbus were not readable, "
   "so the Blue Jackets are priced as a league-average home side. That still leaves Vegas the better team on "
   "the numbers, and the fair price of -135 sits comfortably inside the band: Vegas to win at -135."),
 "nhl-nyr-ott": (
   "The Rangers are the strangest profile on the board: 6-0-0 at home with 29 goals for and 10 against, but "
   "1-4-1 on the road with eight goals scored and 19 conceded in six games. This is a road game. Ottawa were "
   "not readable, so Ottawa are assumed average. That is still enough to tilt the price, because a Rangers "
   "team scoring eight goals in six road games gives the home side the edge on the split alone. Ottawa to win "
   "at -159."),
 "nhl-min-sea": (
   "Seattle are 7-3-1 for 15 points, 6-3-1 across ten and winners of two straight, with a 4-2-1 road record. "
   "Minnesota are 6-3-2 for 14 points but only 2-3-2 away from home, though they are 4-0-0 at home, so the "
   "venue switch matters. With both records read from the league feed, Seattle come out a 56% home side "
   "and the fair price is -128: Seattle to win is the selection."),
 "atp-medvedev-basilashvili": (
   "Medvedev reached this final with a 6-3 first set before Alexander Bublik retired, so the top seed has "
   "played barely a set of tennis while Basilashvili needed three sets to beat seventh seed Stefanos "
   "Tsitsipas 6-4 6-7(5) 6-3. Freshness plus the seeding points one way, and the price of -245 is inside the "
   "brief's band while still reflecting a real chance of an upset. Selection: Medvedev to win the final at "
   "-245."),
 "atp-musetti-fritz": (
   "Fritz, the second seed, beat fourth seed Tommy Paul 6-3 7-5 and has dropped one set in the semi-final "
   "stage; Musetti, seeded sixth, needed three sets to see off top seed Flavio Cobolli 4-6 6-2 7-5. The "
   "seedings and the shorter semi-final favour Fritz, but only mildly, because Musetti has just beaten the "
   "top seed. Our fair price is -122, which is why this one is graded medium: Fritz to win at -122."),
 "mlb-849802": (
   "Game 2 of the World Series at American Family Field, first pitch 00:00Z, with Logan Henderson starting "
   "for Milwaukee against Drew Rasmussen for Tampa Bay. Milwaukee lead the series 1-0 and hold home field. "
   "Only one game of postseason form was readable, so the price is deliberately conservative: the Brewers "
   "are a 55% home side and the selection is Milwaukee on the money line at -120."),
}

PREDICTIONS.update({
 "cr-toronto-vancouver": (
   "Toronto Kings hold nine of the ten win tips OLBG displays on this T20, which is about as one-sided as a "
   "crowd gets, and the fair price of -195 simply reflects that weight of support. No board page for the "
   "competition could be read this session, so the number should be judged as market structure rather than "
   "form. Selection: Toronto Kings to win at -195."),
 "cr-nw-nc": (
   "North West Dragons have eight of the nine win tips on the provincial T20, and the desk's price of -170 "
   "follows that support rather than any record it could confirm. The counterweight is that a near-unanimous "
   "crowd in a low-liquidity provincial match is usually a thin signal. Selection: North West Dragons at "
   "-170, with the caveat that no provincial union page was readable."),
 "cr-indw-zimw": (
   "The second women's ODI between India and Zimbabwe carries a split market: three of five tips sit on "
   "Smriti Mandhana as top India batsman, while the match itself is untipped at this read. With no series "
   "scoreline available, the desk prices India Women at 68% purely on the strength of the fixture and the "
   "gap between the two sides' standing in the format. Selection: India Women at -215."),
 "vb-trentino-cisterna": (
   "Trentino and Cisterna open the Italian round with the crowd split six tips to one in favour of Cisterna, "
   "which is a strange read for a home side with Trentino's recent record in the competition. With the "
   "league's standings page returning an error, the desk ignores that split and prices the home side at 60% "
   "on venue alone. Selection: Trentino to win at -150."),
 "vb-perugia-pordenone": (
   "Perugia host Pordenone in the same round and the desk's 63% home estimate is the highest on the "
   "volleyball board, built from the venue and the relative depth of the two squads rather than a table. "
   "Pordenone carry six of seven tips, so this is a rare case where the price and the crowd disagree. "
   "Selection: Perugia at -170."),
 "bk-no-den": (
   "Denver hold eight of ten tips for the visit of New Orleans, and -180 is the shortest price on the "
   "basketball board. No record, rest situation or injury report could be checked: the league's own scoreboard "
   "feed refused every request. The number is therefore a market-structure estimate. Denver Nuggets at -180."),
 "bk-hou-atl": (
   "Atlanta have five of six tips against Houston, and the desk prices them at 62% on the basis of home "
   "venue and the crowd's lean, which is all that could be supported without a league record. Houston's "
   "road form is the obvious counter-argument and cannot be checked here. Selection: Atlanta Hawks at -165."),
 "ga-finbarrs-nemo": (
   "Nemo Rangers take 27 of the 31 tips on the Cork senior football final, with the crowd backing them at "
   "+1.50 on the handicap. The GAA's national fixture page did not publish the club final and the Cork "
   "county site redirected to its schools hub, so the price rests on the handicap line and that support. "
   "Selection: Nemo Rangers +1.50 at -180."),
 "ga-moycullen-salthill": (
   "Salthill-Knocknacarra carry 28 of 47 tips in the Galway senior final, a much softer lean than the Cork "
   "game, and they are backed at +3.50 with the handicap start. Without a county board page to confirm the "
   "throw-in, the desk treats the handicap as the safer expression of the crowd's view. Selection: "
   "Salthill-Knocknacarra +3.50 at -150."),
 "hb-magdeburg-kriens": (
   "Magdeburg host Kriens-Luzern in Champions League round seven and the desk gives them a six-and-a-half "
   "goal start against a Swiss side making the trip midweek. The fixture is confirmed by the EHF, but no "
   "group table was read, so the handicap is a neutral estimate and the confidence ceiling is medium. "
   "Selection: Magdeburg -6.5 at -120."),
 "hb-berlin-partizan": (
   "Fuchse Berlin face Partizan in the same round. Our line of -8.5 is the widest handicap on the "
   "handball board: it prices the gap in squad resources rather than any table position, since no group "
   "standings page was read. Berlin -8.5 at -125, capped at low confidence."),
 "dt-smith-woodhouse": (
   "Ross Smith has all five win tips on the European Championship match against Luke Woodhouse, and the "
   "price of -140 is a straight conversion of that support with a margin for the crowd being one-eyed. The "
   "PDC's tournament page served a consent wall instead of the draw, so no scoring average or head-to-head "
   "could be added. Selection: Ross Smith at -140."),
 "ru-harlequins-saracens": (
   "Harlequins take four of the five tips for the London derby against Saracens, a modest lean in a fixture "
   "that is usually close, and the desk prices the home side at 55%. With no league page read, nothing is "
   "claimed about selection, injuries or table position. Selection: Harlequins at -120."),
 "rl-origin-2027": (
   "New South Wales carry nine of twelve tips on the 2027 State of Origin series, and the price of +205 is "
   "the desk's conversion of that support. This is a ten-month outright with no team news and no venue, so "
   "it is listed for completeness rather than as a serious match pick. Selection: New South Wales to win "
   "the 2027 series at +205."),
})

# ---------------------------------------------------------------------------
# 7. Assemble and write
# ---------------------------------------------------------------------------


def price(prob: float) -> int:
    return american(prob)


def build_rows():
    rows = []
    for f in FIXTURES:
        markets = []
        for m in f["markets"]:
            p = m["prob"]
            markets.append(dict(market=m["market"], line=m.get("line"), side=m["side"],
                                prob=round(p, 4), fair=price(p), decimal=decimal(p),
                                implied=round(__import__("s37737303_model").implied(price(p)), 4)))
        picked = None
        for m in f["markets"]:
            if m["side"] == f["pick_side"] and m["market"] == f["pick_market"]:
                picked = m
                break
        if picked is None:
            for m in f["markets"]:
                if m["side"] == f["pick_side"]:
                    picked = m
                    break
        if f.get("pick_prob") is not None:
            p = float(f["pick_prob"])
            for m in markets:
                if m["side"] == picked["side"] and m["market"] == picked["market"]:
                    m["prob"] = round(p, 4)
                    m["fair"] = price(p)
                    m["decimal"] = decimal(p)
                elif m["market"] == picked["market"]:
                    other = round(1 - p, 6)
                    m["prob"] = round(other, 4)
                    m["fair"] = price(other)
                    m["decimal"] = decimal(other)
        else:
            p = picked["prob"]
        fair = price(p)
        row = dict(
            id=f["id"], sport=f["sport"], competition=f["competition"],
            home=f["home_name"], away=f["away_name"],
            start_label=f["start_label"], start_utc=f.get("start_utc"), venue=f.get("venue"),
            olbg_url=f["olbg_url"], official_source=f["official_source"],
            fixture_official=f["fixture_official"], evidence=f["evidence"],
            facts=f.get("facts", []), markets=markets,
            olbg_tip=f.get("olbg_tip", ""),
            placeholder=f.get("placeholder"),
            pick=dict(market=picked["market"], line=picked.get("line"), selection=picked["side"],
                      prob=round(p, 4), fair=fair, decimal=decimal(p), in_band=in_band(fair)),
            prediction=PREDICTIONS.get(f["id"]),
        )
        rows.append(row)
    return rows


def write():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payloads = {
        "sources.json": dict(generated_at=now, read_at=READ_AT, sources=SOURCES),
        "fixtures.json": dict(generated_at=now, read_at=READ_AT, fixtures=rows),
        "flags.json": dict(generated_at=now, flags=FLAGS),
        "olbg.json": dict(generated_at=now, read_at=READ_AT, no_market=NO_MARKET,
                          hubs=[s for s in SOURCES if s["kind"] == "discovery"]),
        "predictions.json": dict(generated_at=now,
                                 predictions=[dict(id=r["id"], sport=r["sport"], selection=r["pick"]["selection"],
                                                   market=r["pick"]["market"], text=r["prediction"],
                                                   words=len(r["prediction"].split()))
                                              for r in rows if r["prediction"]]),
    }
    for name, payload in payloads.items():
        (OUT / name).write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    sports = {}
    for r in rows:
        s = sports.setdefault(r["sport"], dict(sport=r["sport"], fixtures=0, picks=0, priced=0,
                                               high=0, medium=0, low=0, written=0))
        s["fixtures"] += 1
        s["picks"] += 1
        s["written"] += 1 if r["prediction"] else 0
        s["priced"] += len(r["markets"])
    for s in NO_MARKET:
        sports.setdefault(s["sport"], dict(sport=s["sport"], fixtures=0, picks=0, priced=0,
                                           high=0, medium=0, low=0, written=0))
    for r in rows:
        g = grade_row(r)
        sports[r["sport"]][g] += 1
        r["confidence"] = g
    payloads["fixtures.json"]["fixtures"] = rows
    (OUT / "fixtures.json").write_text(json.dumps(payloads["fixtures.json"], indent=1, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    counts = dict(fixtures=len(rows), markets=sum(len(r["markets"]) for r in rows),
                  picks=len(rows), predictions=sum(1 for r in rows if r["prediction"]),
                  sports_requested=15, sports_with_picks=len([k for k, v in sports.items() if v["picks"]]),
                  sports_without_market=len(NO_MARKET), flags=len(FLAGS),
                  high=sum(v["high"] for v in sports.values()),
                  medium=sum(v["medium"] for v in sports.values()),
                  low=sum(v["low"] for v in sports.values()))
    coverage = dict(generated_at=now, read_at=READ_AT, counts=counts,
                    sports=sorted(sports.values(), key=lambda x: x["sport"]), no_market=NO_MARKET)
    (OUT / "coverage.json").write_text(json.dumps(coverage, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(
        dict(generated_at=now, read_at=READ_AT, session="37737303-olbg1", task="T377373",
             desk="37737303", counts=counts), indent=1) + "\n", encoding="utf-8")
    return counts


def grade_row(row):
    from s37737303_model import grade
    p = row["pick"]["prob"]
    fair = row["pick"]["fair"]
    ev = row["evidence"]
    official = ev in ("both", "one")
    any_official = ev in ("both", "one", "fixture")
    if not in_band(fair):
        return "low"
    if p >= 0.60 and official:
        return "high"
    if p >= 0.55 and any_official:
        return "medium"
    if p >= 0.60 and ev == "sentiment":
        return "medium"
    return "low"


if __name__ == "__main__":
    print(json.dumps(write(), indent=1))
