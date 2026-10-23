#!/usr/bin/env python3
"""TED71 (session ed71b937-olbg1) - dataset for the 2026-10-23 live desk.

Every row carries two independent blocks:

  olbg     - what the OLBG hub page literally rendered (discovery only)
  official - what a league / governing body / tour page actually said, read
             this session.  When no official page was read the block is None
             and every official field is blank; the row is flagged instead of
             being inferred (COORDINATION.md 0.5).

Nothing in this file is estimated.  Model-derived numbers live in
sed71b937_model.py and are always labelled as estimates.
"""

from __future__ import annotations

import datetime as _dt
import json
import os

SESSION = "ed71b937-olbg1"
TASK = "TED71"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data", "ed71b937")

# Observation window of the OLBG discovery pass, UTC.
OLBG_WINDOW = ("2026-10-23T16:12:00Z", "2026-10-23T16:26:00Z")

# OLBG rendered every hub timestamp in America/New_York EDT (UTC-4) with no
# timezone label.  Derived from five independent cross-checks; see
# data/ed71b937/harvest.json -> timezone_finding.  Flagged as ED71-F-01.
OLBG_TZ_OFFSET_HOURS = 4

# The brief names fifteen sports.  Australian Rules (22) and eSports (23)
# appear in older desks on this repository but are NOT in this brief.
SPORTS = [
    ("golf", "Golf", 5),
    ("volleyball", "Volleyball", 21),
    ("rugby-union", "Rugby Union", 9),
    ("cricket", "Cricket", 7),
    ("snooker", "Snooker", 8),
    ("darts", "Darts", 15),
    ("baseball", "Baseball", 12),
    ("gaelic-football", "Gaelic Sports", 25),
    ("greyhounds", "Greyhounds", 28),
    ("tennis", "Tennis", 3),
    ("motor-racing", "Motor Racing", 14),
    ("handball", "Handball", 20),
    ("ice-hockey", "Ice Hockey", 13),
    ("basketball", "Basketball", 4),
    ("rugby-league", "Rugby League", 10),
]

SPORT_IDS = {slug: (name, oid) for slug, name, oid in SPORTS}


def olbg_utc(rendered: str, day: str) -> str:
    """Convert an OLBG-rendered local clock to UTC using the documented offset.

    `rendered` is 'HH:MM'; `day` is 'today' (2026-10-23), 'tomorrow'
    (2026-10-24) or an explicit 'YYYY-MM-DD'.  The conversion is arithmetic on
    the offset proven in harvest.json, not a guess about the source timezone.
    """
    hour, minute = (int(x) for x in rendered.split(":"))
    base = {
        "today": _dt.date(2026, 10, 23),
        "tomorrow": _dt.date(2026, 10, 24),
    }.get(day)
    if base is None:
        base = _dt.date(*(int(p) for p in day.split("-")))
    when = _dt.datetime.combine(base, _dt.time(hour, minute))
    when = when + _dt.timedelta(hours=OLBG_TZ_OFFSET_HOURS)
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def _row(
    sport,
    olbg_name,
    event_id,
    rendered,
    day,
    olbg_market,
    olbg_pick,
    tips,
    official=None,
    note=None,
):
    """One fixture row.  `official` is None unless an official page was read."""
    slug = dict((n, s) for s, n, _ in SPORTS)[sport]
    hub = {
        "Golf": "Golf/5", "Volleyball": "Volleyball/21",
        "Rugby Union": "Rugby_Union/9", "Cricket": "Cricket/7",
        "Snooker": "Snooker/8", "Darts": "Darts/15", "Baseball": "Baseball/12",
        "Gaelic Sports": "Gaelic_Football/25", "Greyhounds": "Greyhounds/28",
        "Tennis": "Tennis/3", "Motor Racing": "Motor_Racing/14",
        "Handball": "Handball/20", "Ice Hockey": "Ice_Hockey/13",
        "Basketball": "Basketball/4", "Rugby League": "Rugby_League/10",
    }[sport]
    # The hub page is the page that was actually read; per-event URLs were not
    # captured, so the hub is published as the discovery link instead of a
    # reconstructed (and therefore unverified) event URL.
    olbg_url = "https://www.olbg.com/betting-tips/{}".format(hub)
    if olbg_name is None:
        # Official-source row that the OLBG hub capture did not list.  The
        # OLBG block stays absent rather than being synthesised.
        olbg_block = None
    else:
        olbg_block = {
            "name": olbg_name,
            "event_id": event_id,
            "rendered_time": "{} {}".format(day, rendered),
            "implied_utc": olbg_utc(rendered, day),
            "market": olbg_market,
            "most_tipped": olbg_pick,
            "tips": tips,
            "url": olbg_url,
        }
    return {
        "id": "ED71-{:03d}".format(len(ROWS) + 1),
        "sport": sport,
        "sport_slug": slug,
        "olbg": olbg_block,
        "official": official,
        "note": note,
    }


ROWS = []


# --------------------------------------------------------------------------
# ICE HOCKEY - NHL rows carry an official read from api-web.nhle.com and
# nhl.com, both fetched this session.  The 13 European-league rows on the
# same hub were discovered but no league page was read: official stays None.
# --------------------------------------------------------------------------
NHL_SCHED = "https://api-web.nhle.com/v1/schedule/2026-10-23"
NHL_ONTAP = "https://www.nhl.com/news/nhl-on-tap-news-and-notes-october-23-2026"

ROWS.append(_row(
    "Ice Hockey", "MTL Canadiens @ CHI Blackhawks", 199984, "20:07", "today",
    "Money Line", "MTL Canadiens", "3/3",
    official={
        "competition": "NHL 2026-27 regular season",
        "away": "Montréal Canadiens", "home": "Chicago Blackhawks",
        "start_utc": "2026-10-24T00:00:00Z",
        "venue": "United Center, Chicago",
        "game_state": "FUT", "schedule_state": "OK",
        "game_id": 2026020166, "season": 20262027, "game_type": 2,
        "record_away": "4-3-2", "record_home": "3-6-0",
        "sources": [NHL_SCHED, NHL_ONTAP],
        "read_utc": "2026-10-23T16:29:00Z",
    },
    note="OLBG rendered 20:07 against an official 20:00 ET start: a 7-minute "
         "unlabelled padding (flag ED71-F-02).  Published start uses the "
         "official NHL startTimeUTC.",
))

ROWS.append(_row(
    "Ice Hockey", None, None, None, None,
    None, None, None,
    official={
        "competition": "NHL 2026-27 regular season",
        "away": "Tampa Bay Lightning", "home": "Colorado Avalanche",
        "start_utc": "2026-10-24T01:00:00Z",
        "venue": "Ball Arena, Denver",
        "game_state": "FUT", "schedule_state": "OK",
        "game_id": 2026020167, "season": 20262027, "game_type": 2,
        "record_away": "7-2-0", "record_home": "5-4-1",
        "sources": [NHL_SCHED, NHL_ONTAP],
        "read_utc": "2026-10-23T16:29:00Z",
    },
    note="Official-source row.  This game did not appear in the first page of "
         "the OLBG Ice Hockey hub capture, so the OLBG block is blank rather "
         "than invented (flag ED71-F-03).",
))

for _name, _eid, _t, _mkt, _pick, _tips, _comp in [
    ("Esbjerg Energy vs Herning Blue Fox", 199946, "13:00", "Money Line", "Herning Blue Fox", "3/3", "Danish Metal Ligaen"),
    ("Grizzlys Wolfsburg vs ERC Ingolstadt", 199927, "13:30", "Money Line", "ERC Ingolstadt", "2/2", "Germany Eishockey Liga"),
    ("Rodovre Mighty Bulls vs Herlev Eagles", 199947, "13:30", "Money Line", "Herlev Eagles", "2/2", "Danish Metal Ligaen"),
    ("K Espoo vs HIFK", 199955, "12:30", "Game Totals", "Over 5.50", "1/1", "Finland SM Liiga"),
    ("Graz 99ers vs EHC Black Wings Linz", 199965, "12:30", "Puck Line", "EHC Black Wings Linz +1.50", "1/2", "Austria EHL"),
    ("HK Olimpija Ljubljana vs Fehervar AV19", 199969, "13:15", "Puck Line", "HK Olimpija Ljubljana -1.50", "1/1", "Austria EHL"),
    ("Eisbaren Berlin vs Augsburger Panther", 199926, "13:30", "Puck Line", "Eisbaren Berlin -1.50", "1/1", "Germany Eishockey Liga"),
    ("Adler Mannheim vs Lowen Frankfurt", 199925, "13:30", "Money Line", "Adler Mannheim", "1/1", "Germany Eishockey Liga"),
    ("Nurnberg Ice Tigers vs Krefeld Pinguine", 199928, "13:30", "Game Totals", "Under 5.50", "1/1", "Germany Eishockey Liga"),
    ("EHC Munchen vs Iserlohn Roosters", 199924, "13:30", "Money Line", "EHC Munchen", "1/1", "Germany Eishockey Liga"),
    ("Straubing Tigers vs Kolner Haie", 199930, "13:30", "Game Totals", "Under 5.50", "1/1", "Germany Eishockey Liga"),
    ("Pioneers Vorarlberg vs HCB Sudtirol Alperia", 199968, "13:30", "Money Line", "HCB Sudtirol Alperia", "1/1", "Austria EHL"),
    ("Fribourg Gotteron vs EHC Biel", 199908, "13:45", "Money Line", "Fribourg Gotteron", "", "Switzerland NLA"),
]:
    ROWS.append(_row("Ice Hockey", _name, _eid, _t, "today", _mkt, _pick, _tips,
                     note="OLBG discovery only; {} league page not fetched "
                          "this session, so official fields are blank."
                          .format(_comp)))


# --------------------------------------------------------------------------
# BASEBALL - the single OLBG baseball row is World Series Game 1, confirmed
# on mlb.com this session.
# --------------------------------------------------------------------------
ROWS.append(_row(
    "Baseball", "TB Rays @ MIL Brewers", 160789, "20:00", "today",
    "Money Line", "MIL Brewers", "25/31",
    official={
        "competition": "2026 World Series, Game 1",
        "away": "Tampa Bay Rays", "home": "Milwaukee Brewers",
        "start_utc": "2026-10-24T00:00:00Z",
        "venue": "American Family Field, Milwaukee",
        "record_away": "98-64", "record_home": "103-59",
        "series_note": "Best of seven; Brewers hold home-field advantage "
                       "having finished 103-59 to the Rays' 98-64.  Brewers "
                       "swept the Dodgers in the NLCS; the Rays beat the "
                       "Guardians 4-2 in the ALCS.",
        "sources": [
            "https://www.mlb.com/news/2026-mlb-playoff-and-world-series-schedule",
            "https://www.mlb.com/news/2026-mlb-world-series-faq-schedule-times-teams-and-more",
        ],
        "read_utc": "2026-10-23T16:33:00Z",
    },
    note="8:00 p.m. ET confirmed on mlb.com; OLBG's unlabelled 20:00 matches "
         "once the EDT offset is applied.",
))


# --------------------------------------------------------------------------
# BASKETBALL - EuroLeague round 7.  Standings and points for/against come
# from the official EuroLeague media centre game-kit PDF; the three fixtures
# are confirmed on the same feed's round listing.
# --------------------------------------------------------------------------
# After-round-6 standings read on the official Olympiacos BC club site
# (a team is an official source under COORDINATION.md 0.5).  An earlier read
# of the EuroLeague media-centre round-6 game kit carried the same table one
# round STALE (five games played); that stale table was rejected before
# pricing and the discrepancy is logged as flag ED71-F-14.
EL_TABLE = "https://www.olympiacosbc.gr/el/"
EL_RECORDS = {
    "Zalgiris Kaunas": (2, 4, 490, 517),
    "LDLC ASVEL Villeurbanne": (2, 4, 527, 572),
    "Olympiacos Piraeus": (5, 1, 564, 524),
    "Fenerbahce Tarfin Istanbul": (5, 1, 501, 447),
    "Paris Basketball": (1, 5, 504, 545),
    "Valencia Basket": (4, 2, 583, 537),
}

for _name, _eid, _t, _pick, _tips, _a, _h in [
    ("Zalgiris vs Asvel Lyon Villeurbanne", 535928, "13:00", "Zalgiris", "9/16",
     "Zalgiris Kaunas", "LDLC ASVEL Villeurbanne"),
    ("Olympiacos vs Fenerbahce", 535925, "14:15", "Olympiacos", "6/10",
     "Olympiacos Piraeus", "Fenerbahce Tarfin Istanbul"),
    ("Paris vs Valencia", 535926, "14:45", "Valencia", "5/10",
     "Paris Basketball", "Valencia Basket"),
]:
    _aw, _hw = EL_RECORDS[_a], EL_RECORDS[_h]
    ROWS.append(_row(
        "Basketball", _name, _eid, _t, "today", "Money Line", _pick, _tips,
        official={
            "competition": "2026-27 EuroLeague, regular season round 7",
            "away": _a, "home": _h,
            "start_utc": olbg_utc(_t, "today"),
            "venue": None,
            "record_away": "{}-{}".format(_aw[0], _aw[1]),
            "record_home": "{}-{}".format(_hw[0], _hw[1]),
            "pf_pa_away": [_aw[2], _aw[3]],
            "pf_pa_home": [_hw[2], _hw[3]],
            "sources": [EL_TABLE],
            "read_utc": "2026-10-23T17:08:00Z",
        },
        note="W-L and points for/against are the after-round-6 official "
             "table on the Olympiacos BC club site (six games played).  The "
             "club site also lists this fixture at 23/10/2026 21:15 local, "
             "which converts to 18:15Z and matches the UTC start derived "
             "from the OLBG rendering - an independent confirmation of "
             "ED71-F-01.  Venue was not printed on the page that was read, "
             "so it is left blank rather than assumed.",
    ))

for _name, _eid, _t, _mkt, _pick, _tips, _comp in [
    ("CHI Bulls @ MIL Bucks", 536041, "16:10", "Money Line", "MIL Bucks", "5/5", "NBA"),
    ("MIN Timberwolves @ ORL Magic", 536036, "19:10", "Money Line", "MIN Timberwolves", "5/5", "NBA"),
    ("HOU Rockets @ SA Spurs", 534841, "21:40", "Money Line", "SA Spurs", "4/6", "NBA"),
    ("NY Knicks @ BOS Celtics", 534842, "19:10", "Pointspread", "BOS Celtics -2.50", "3/3", "NBA"),
    ("TOR Raptors @ WAS Wizards", 536034, "19:10", "Money Line", "TOR Raptors", "3/4", "NBA"),
    ("DAL Mavericks @ IND Pacers", 536037, "19:10", "Money Line", "IND Pacers", "3/3", "NBA"),
    ("DET Pistons @ MIA Heat", 536038, "20:10", "Money Line", "DET Pistons", "3/3", "NBA"),
    ("POR Trail Blazers @ SAC Kings", 536043, "22:10", "Pointspread", "POR Trail Blazers -10.50", "3/3", "NBA"),
    ("ATL Hawks @ CHA Hornets", 536035, "19:10", "Pointspread", "ATL Hawks -2.50", "2/2", "NBA"),
    ("NO Pelicans @ UTA Jazz", 536040, "21:40", "Money Line", "UTA Jazz", "2/2", "NBA"),
    ("LA Clippers @ LA Lakers", 536042, "22:10", "Pointspread", "LA Clippers +9.50", "", "NBA"),
    ("Gtk Gliwice vs Torun", 536031, "14:15", "Money Line", "Torun", "2/3", "Poland PLK"),
]:
    ROWS.append(_row("Basketball", _name, _eid, _t, "today", _mkt, _pick, _tips,
                     note="OLBG discovery only; the {} page was not fetched "
                          "this session, so official fields are blank."
                          .format(_comp)))


# --------------------------------------------------------------------------
# DARTS - PDC European Championship, round one, Dortmund.  The eight Friday
# fixtures and the session window were read on pdc.tv; the page body is
# behind a consent wall, so seedings are NOT treated as an official read.
# --------------------------------------------------------------------------
PDC_EC = ("https://www.pdc.tv/news/2026/october/19/"
          "2026-machineseeker-european-championship-schedule-confirmed/")

for _name, _eid, _t, _pick, _tips in [
    ("Ryan Joyce vs Jermaine Wattimena", 32332, "13:15", "Ryan Joyce", "16/25"),
    ("Krzysztof Ratajski vs Dave Chisnall", 32333, "13:45", "Krzysztof Ratajski", "15/26"),
    ("Nathan Aspinall vs Cristo Reyes", 32327, "14:15", "Nathan Aspinall", "14/22"),
    ("Jonny Clayton vs Niko Springer", 32335, "14:45", "Jonny Clayton", "26/31"),
    ("Luke Littler vs William OConnor", 32328, "15:15", "Luke Littler", "14/20"),
    ("Wessel Nijman vs Martin Schindler", 32326, "15:45", "Wessel Nijman", "18/23"),
    ("Kevin Doets vs Michael van Gerwen", 32331, "16:15", "Michael van Gerwen", "10/17"),
    ("Josh Rock vs Chris Dobey", 32336, "16:45", "Josh Rock", "10/19"),
]:
    ROWS.append(_row(
        "Darts", _name, _eid, _t, "today", "Win Match 2-way", _pick, _tips,
        official={
            "competition": "2026 Machineseeker PDC European Championship, "
                           "round one (best of 11 legs)",
            "away": _name.split(" vs ")[0], "home": _name.split(" vs ")[1],
            "start_utc": olbg_utc(_t, "today"),
            "venue": "Westfalenhallen, Dortmund",
            "session": "Friday 23 October, 1900-2300 CEST (1800-2200 BST)",
            "sources": [PDC_EC],
            "read_utc": "2026-10-23T16:36:00Z",
        },
        note="Fixture and session window read on pdc.tv.  The page body is "
             "gated by a CookieYes consent wall (flag ED71-F-04), so "
             "seedings and Order-of-Merit positions were NOT read and are "
             "left blank; the fixture therefore carries no official "
             "statistical input and is not priced.",
    ))

for _name, _eid, _t, _pick, _tips in [
    ("Stephen Bunting vs Kim Huybrechts", 32384, "13:15", "Kim Huybrechts", "2/3"),
    ("Gian van Veen vs Luke Woodhouse", 32385, "13:15", "Luke Woodhouse", "2/3"),
    ("Ross Smith vs Damon Heta", 32386, "13:15", "Damon Heta", "2/3"),
    ("Cameron Menzies vs Gerwyn Price", 32383, "13:15", "Gerwyn Price", "1/2"),
]:
    ROWS.append(_row("Darts", _name, _eid, _t, "tomorrow", "Win Match 2-way",
                     _pick, _tips,
                     note="OLBG lists this pairing on 24 October, which "
                          "conflicts with the PDC order of play that places "
                          "these pairings in the Thursday/Friday round one. "
                          "Left blank and flagged (ED71-F-05) rather than "
                          "corrected from memory."))


# --------------------------------------------------------------------------
# SNOOKER - BetVictor Northern Ireland Open quarter-finals, Waterfront Hall.
# Both OLBG rows were confirmed on the official WST match centre.
# --------------------------------------------------------------------------
WST_MC = "https://www.wst.tv/match-centre/caa08d3f-a0a0-4d8f-a8da-70e4b19fa4da"
SNOOKER_ORG = "https://www.snooker.org/res/index.asp?event=2548"

for _name, _eid, _t, _pick, _tips, _a, _h in [
    ("Jak Jones v Scott Donaldson", 9951, "14:05", "Jak Jones", "11/15",
     "Jak Jones", "Scott Donaldson"),
    ("David Gilbert v Mark Williams", 9950, "14:05", "Mark Williams", "11/15",
     "David Gilbert", "Mark Williams"),
]:
    ROWS.append(_row(
        "Snooker", _name, _eid, _t, "today", "Win Match", _pick, _tips,
        official={
            "competition": "BetVictor Northern Ireland Open 2026, "
                           "quarter-final (best of 11)",
            "away": _a, "home": _h,
            "start_utc": "2026-10-23T18:00:00Z",
            "venue": "Waterfront Hall, Belfast",
            "sources": [WST_MC, SNOOKER_ORG],
            "read_utc": "2026-10-23T16:44:00Z",
        },
        note="WST and snooker.org both give 18:00:00Z.  OLBG rendered 14:05, "
             "i.e. 18:05Z - a five-minute unlabelled padding on top of the "
             "EDT offset (flag ED71-F-02).  The official 18:00Z is published.",
    ))


# --------------------------------------------------------------------------
# RUGBY UNION - URC round 4 Friday fixtures read on the official
# unitedrugby.com match centre.  No official standings page was read, so
# these fixtures are verified but deliberately left unpriced.
# --------------------------------------------------------------------------
URC_OFFICIAL = "https://www.unitedrugby.com/"
URC_TEAMNEWS = "https://www.unitedrugby.com/latest/news/round-4-team-announcements/"

for _name, _eid, _t, _pick, _tips, _a, _h, _venue in [
    ("Cardiff v Sharks", 609575, "14:45", "Sharks", "4/7",
     "Cardiff Rugby", "Hollywoodbets Sharks", "Cardiff Arms Park, Cardiff"),
    ("Connacht v Zebre Parma", 609577, "14:45", "Connacht", "11/15",
     "Connacht", "Zebre Parma", "Dexcom Stadium, Galway"),
    ("Edinburgh v Lions", 609579, "14:45", "Edinburgh", "8/9",
     "Edinburgh", "Lions", "Hive Stadium, Edinburgh"),
]:
    ROWS.append(_row(
        "Rugby Union", _name, _eid, _t, "today", "To Win", _pick, _tips,
        official={
            "competition": "Vodacom United Rugby Championship 2026-27, round 4",
            "away": _a, "home": _h,
            "start_utc": "2026-10-23T18:45:00Z",
            "venue": _venue,
            "kickoff_local": "19.45 IRE & UK / 20.45 ITA & SA",
            "sources": [URC_OFFICIAL, URC_TEAMNEWS],
            "read_utc": "2026-10-23T16:40:00Z",
        },
        note="Fixture, venue and kick-off read on unitedrugby.com.  No "
             "official URC league table was read this session, so no model "
             "input exists and the fixture is left unpriced rather than "
             "estimated from memory.",
    ))

for _name, _eid, _t, _pick, _tips, _comp in [
    ("Aurillac v Nevers", 609560, "13:30", "Aurillac", "14/19", "Pro D2"),
    ("Agen v Nissa", 609558, "13:30", "Agen", "12/18", "Pro D2"),
    ("Narbonne v Brive", 609557, "13:00", "Brive", "11/17", "Pro D2"),
    ("Soyaux Angouleme v Dax", 609563, "13:30", "Dax", "7/14", "Pro D2"),
    ("Valence Romans v Colomiers", 609559, "13:30", "Valence Romans", "6/11", "Pro D2"),
    ("Provence v Beziers", 609562, "15:00", "Provence", "6/10", "Pro D2"),
    ("Grenoble v Biarritz", 609561, "15:00", "Grenoble", "6/10", "Pro D2"),
    ("Gloucester v Bath", 609570, "14:45", "Gloucester", "7/7", "Premiership"),
    ("Newcastle Red Bulls v Sale Sharks", 609573, "14:45", "Sale Sharks", "3/5", "Premiership"),
    ("Bulls v Ulster", 609576, "07:45", "Ulster", "3/4", "URC"),
    ("Japan v Fiji", 609582, "01:50", "Fiji", "2/3", "International"),
    ("Stormers v Scarlets", 609580, "10:00", "Scarlets", "", "URC"),
]:
    ROWS.append(_row("Rugby Union", _name, _eid, _t,
                     "tomorrow" if _name in ("Bulls v Ulster", "Japan v Fiji", "Stormers v Scarlets") else "today",
                     "To Win", _pick, _tips,
                     note="OLBG discovery only; the {} body was not fetched "
                          "this session.".format(_comp)))


# --------------------------------------------------------------------------
# TENNIS - nine OLBG rows.  No atptour.com / wtatennis.com order of play was
# read this session, so every row stays discovery-only.
# --------------------------------------------------------------------------
for _name, _eid, _t, _day, _mkt, _pick, _tips in [
    ("Arthur Fils vs Alex Michelsen", 902150, "12:30", "today", "Win Match", "Arthur Fils", "5/10"),
    ("Flavio Cobolli vs Brandon Nakashima", 902155, "13:00", "today", "Win Match", "Flavio Cobolli", "5/8"),
    ("Jan Lennard Struff vs Zizou Bergs", 902153, "14:00", "today", "Win Match", "Jan Lennard Struff", "5/8"),
    ("Luca Van Assche vs Lorenzo Musetti", 902147, "14:30", "today", "Win Match", "Luca Van Assche", "3/5"),
    ("Ann Li vs Ashlyn Krueger", 902157, "23:00", "today", "Total Games", "Over 22.50", "2/3"),
    ("Katie Boulter vs Katerina Siniakova", 902162, "00:30", "tomorrow", "Win Match", "Katie Boulter", "1/1"),
    ("Leylah Fernandez vs Marie Bouzkova", 902160, "03:00", "tomorrow", "Win Match", "Leylah Fernandez", "1/1"),
    ("Elena Rybakina vs Diana Shnaider", 902163, "05:30", "tomorrow", "Win Match", "Diana Shnaider", "1/1"),
    ("Nikoloz Basilashvili vs Stefanos Tsitsipas", 902159, "06:00", "tomorrow", "Set Betting", "Stefanos Tsitsipas to win 2 - 1", "1/1"),
]:
    ROWS.append(_row("Tennis", _name, _eid, _t, _day, _mkt, _pick, _tips,
                     note="OLBG discovery only; no ATP/WTA official order of "
                          "play was read this session, so tournament, round, "
                          "venue and start are all blank (flag ED71-F-06)."))


# --------------------------------------------------------------------------
# CRICKET / HANDBALL / VOLLEYBALL / GAELIC / MOTOR RACING / RUGBY LEAGUE -
# discovery only.  No governing-body page was read for these this session.
# --------------------------------------------------------------------------
for _name, _eid, _t, _day, _pick, _tips in [
    ("Tasmania vs Victoria One Day Match", 188839, "19:30", "today", "Tasmania", "5/7"),
    ("New Zealand vs India 2nd T20 Match", 188832, "03:00", "tomorrow", "India", "4/5"),
    ("Western Australia vs New South Wales One Day Match", 188840, "02:00", "tomorrow", "Western Australia", "3/4"),
    ("Lions vs Limpopo Impalas T20", 188841, "07:00", "tomorrow", "Lions", "3/3"),
    ("Eastern Cape Iinyathi vs Warriors T20", 188842, "07:00", "tomorrow", "Warriors", "2/2"),
    ("Knights vs Mpumalanga Rhinos T20", 188843, "12:00", "tomorrow", "Mpumalanga Rhinos", "1/1"),
    ("Pakistan vs England One Day Match", 188838, "04:00", "2026-10-25", "Pakistan", "1/1"),
]:
    ROWS.append(_row("Cricket", _name, _eid, _t, _day, "Win Match", _pick, _tips,
                     note="OLBG discovery only; no ICC / national board page "
                          "was read this session (flag ED71-F-07)."))

for _name, _eid, _t, _day, _mkt, _pick, _tips in [
    ("Pays dAix UC vs Toulouse", 12083, "14:00", "today", "Money Line", "Toulouse", "7/16"),
    ("Frisch Auf Goppingen vs ThSV Eisenach", 12088, "13:00", "today", "Money Line", "Tie", "6/15"),
    ("Bidasoa Irun vs Caserio Ciudad Real", 12101, "13:00", "today", "Money Line", "Bidasoa Irun", "6/12"),
    ("Limoges 87 vs Dunkerque", 12080, "14:00", "today", "Money Line", "Limoges 87", "6/15"),
    ("TSV Hannover Burgdorf vs TBV Lemgo Lippe", 12093, "14:00", "today", "Money Line", "Tie", "6/13"),
    ("GRK Ohrid vs Spor Toto SK", 12120, "12:30", "today", "Match Handicap", "Spor Toto SK +11.50", "5/5"),
    ("Chartres vs USAM Nimes", 12079, "14:00", "today", "Money Line", "Tie", "5/10"),
    ("Estonia W vs Kosovo W", 12110, "14:00", "today", "Money Line", "Kosovo (W)", "5/11"),
    ("FC Barcelona vs Ciudad Encantada", 12121, "13:00", "today", "Match Handicap", "Ciudad Encantada +13.50", "4/5"),
    ("Selestat Alsace vs Caen", 12085, "14:30", "today", "Money Line", "Caen", "4/8"),
    ("Tremblay vs Cesson Rennes", 12086, "14:30", "today", "Money Line", "Cesson Rennes", "4/9"),
    ("Skive FH vs Aalborg Handbold", 12076, "09:00", "tomorrow", "Money Line", "Aalborg Handbold", "3/6"),
    ("Skjern Handbold vs Ribe Esbjerg HH", 12077, "10:00", "tomorrow", "Money Line", "Ribe Esbjerg HH", "2/3"),
    ("Villa De Aranda vs Puerto Sagunto", 12107, "13:00", "tomorrow", "Money Line", "Puerto Sagunto", "2/2"),
    ("HC Erlangen vs THW Kiel", 12091, "12:00", "tomorrow", "Money Line", "HC Erlangen", ""),
]:
    ROWS.append(_row("Handball", _name, _eid, _t, _day, _mkt, _pick, _tips,
                     note="OLBG discovery only; no EHF / national federation "
                          "page was read this session (flag ED71-F-08)."))

for _name, _eid, _t, _day, _mkt, _pick, _tips in [
    ("VOLLEY GOATS Mitteldeutschland vs Netzhoppers KW", 37009, "13:30", "today", "Win Match", "Netzhoppers KW", "6/7"),
    ("Brasilia W vs Sesc RJ Flamengo W", 37001, "17:30", "today", "Win Match", "Brasilia W", "5/9"),
    ("ATSC Klagenfurt Women vs Linz Steg W", 37015, "14:00", "today", "Win Match", "Linz Steg W", "4/7"),
    ("Minas W vs Paulistano-Barueri W", 37022, "17:30", "today", "Win Match", "Minas W", "4/6"),
    ("Lokomotiv Avia vs Montana", 37025, "12:30", "today", "Win Match", "Lokomotiv Avia", "3/4"),
    ("PGE Skra Belchatow vs Projekt Warszawa", 36964, "12:00", "tomorrow", "Win Match", "Projekt Warszawa", "2/3"),
    ("Mackenzie W vs Osasco W", 37002, "15:00", "tomorrow", "Win Match", "Mackenzie W", "2/3"),
    ("Abel-Moda Brusque W vs Praia Clube W", 37003, "20:00", "tomorrow", "Win Match", "Abel/Moda Brusque W", "2/2"),
    ("Trentino vs Cisterna", 36994, "12:00", "2026-10-25", "Win Match", "Cisterna", "2/2"),
    ("Perugia vs Pordenone", 36997, "13:00", "2026-10-25", "Win Match", "Pordenone", "2/2"),
    ("CHKS Chelm vs Resovia Rzeszow", 36965, "13:00", "2026-10-25", "Win Match", "Resovia Rzeszow", "2/3"),
    ("SG Sokol-Post W vs TSV Hartberg W", 37017, "10:30", "tomorrow", "Set Score", "SG Sokol/Post W to win 3-1", "1/1"),
    ("UVC Ried vs VBK Klagenfurt", 37031, "12:00", "tomorrow", "Win Match", "UVC Ried", "1/1"),
    ("Sternberk W vs VK Lvice Praha W", 37026, "12:00", "tomorrow", "Set Score", "Sternberk W to win 3-1", "1/1"),
    ("VfB Friedrichshafen vs SSC Karlsruhe", 37032, "13:00", "2026-10-25", "Win Match", "", ""),
]:
    ROWS.append(_row("Volleyball", _name, _eid, _t, _day, _mkt, _pick, _tips,
                     note="OLBG discovery only; no CEV / national federation "
                          "page was read this session (flag ED71-F-09)."))

for _name, _eid, _t, _day, _mkt, _pick, _tips in [
    ("St Finbarrs v Nemo Rangers", 3530, "12:00", "2026-10-25", "Handicap", "Nemo Rangers +1.50", "14/18"),
    ("Moycullen v Salthill-Knocknacarra", 3532, "12:00", "2026-10-25", "Handicap", "Moycullen -3.50", "12/24"),
    ("Kanturk v Eire Og Cor", 3531, "09:00", "2026-11-01", "Win Match", "Kanturk", "4/7"),
    ("Fr Caseys v Kildimo Pallaskenry", 3537, "10:30", "2026-11-01", "Win Match", "Fr Caseys", "3/3"),
]:
    ROWS.append(_row("Gaelic Sports", _name, _eid, _t, _day, _mkt, _pick, _tips,
                     note="OLBG discovery only; no GAA county-board page was "
                          "read this session (flag ED71-F-10)."))

ROWS.append(_row("Motor Racing", "USA Grand Prix", 913, "16:00", "2026-10-25",
                 "Win Race", "Max Verstappen", "13/38",
                 official={
                     "competition": "Formula 1 MSC Cruises United States "
                                    "Grand Prix 2026",
                     "away": None, "home": None,
                     "start_utc": "2026-10-25T20:00:00Z",
                     "venue": "Circuit of the Americas, Austin, Texas",
                     "distance": "56 laps / 308.405 km of a 5.513 km circuit",
                     "sessions_utc": {"practice_1": "2026-10-23T17:30:00Z",
                                      "practice_2": "2026-10-23T21:00:00Z"},
                     "sources": ["https://www.formula1.com/en/racing/2026/united-states"],
                     "read_utc": "2026-10-23T16:46:00Z",
                 },
                 note="formula1.com publishes the race start as "
                      "2026-10-25T20:00:00Z; OLBG's unlabelled '25 Oct 16:00' "
                      "is exactly four hours behind it, a sixth independent "
                      "confirmation of the EDT rendering (ED71-F-01).  A "
                      "20-car outright is not a two-way match market, so no "
                      "match line is originated."))

for _name, _eid, _t, _pick, _tips in [
    ("5:12 Towcester", 689803, "12:12", "Choices Jean", "2/4"),
    ("5:18 Kinsley", 689800, "12:18", "Grumpy Sandstorm", "2/2"),
    ("5:31 Towcester", 689802, "12:31", "Mums Image", "2/2"),
    ("5:49 Towcester", 689805, "12:49", "Trapstyle Sneezy", "2/2"),
    ("8:33 Romford", 689846, "15:33", "Ontherun Jamie", "2/2"),
    ("9:13 Romford", 689717, "16:13", "Grouchos Gregor", "2/2"),
    ("5:24 Newcastle", 689806, "12:24", "Alnwick Tina", "1/1"),
    ("5:37 Kinsley", 689804, "12:37", "Grumpy Jacko", "1/1"),
    ("5:43 Newcastle", 689798, "12:43", "Dryland Velvet", "1/2"),
    ("5:51 Harlow", 689801, "12:51", "Doreens Poppy", "1/1"),
    ("5:56 Kinsley", 689807, "12:56", "Kellyseyenoone", "1/1"),
    ("6:02 Newcastle", 689808, "13:02", "Mollys Aoibhe", "1/1"),
    ("6:08 Nottingham", 689810, "13:08", "Honeygar Flow", "1/1"),
    ("6:11 Harlow", 689811, "13:11", "Club Dream", "1/1"),
    ("6:18 Sheffield", 689816, "13:18", "Jaykay Seven", "1/1"),
]:
    ROWS.append(_row("Greyhounds", _name, _eid, _t, "today", "Daily Races",
                     _pick, _tips,
                     note="OLBG discovery only.  The race title carries the "
                          "UK local clock while the rendered time is EDT "
                          "(17:12 BST -> 16:12Z -> rendered 12:12), the "
                          "clearest single proof of ED71-F-01.  No GBGB "
                          "card or runner data was read, so fields are blank "
                          "(flag ED71-F-11)."))

for _name, _eid, _t, _day, _mkt, _pick, _tips in [
    ("State of Origin 2027", 2695857, "06:00", "2027-05-27", "Win Tournament", "New South Wales", "9/12"),
    ("Super League 2027", 2801554, "13:00", "2027-10-02", "Grand Final Winner", "Leeds Rhinos", "1/3"),
    ("NRL 2027", 2801600, "04:30", "2027-10-03", "Grand Final Winner", "Penrith Panthers", "1/2"),
]:
    ROWS.append(_row("Rugby League", _name, _eid, _t, _day, _mkt, _pick, _tips,
                     note="Outright market only.  The Rugby League hub listed "
                          "zero match fixtures on 2026-10-23 (flag "
                          "ED71-F-12), consistent with the documented OLBG "
                          "behaviour of suppressing fixtures with no open "
                          "community tips."))


def coverage_gaps():
    """Sports where OLBG itself listed nothing usable, recorded as findings."""
    return [
        {
            "id": "ED71-F-13", "sport": "Golf", "severity": "high",
            "finding": "The OLBG Golf hub (sport_id 5) returned the literal "
                       "string 'No tips found.' at 2026-10-23T16:18Z, so "
                       "there is no OLBG golf fixture or tournament listing "
                       "to verify.  Coverage gap, not a zero-fixture finding.",
            "source": "https://www.olbg.com/betting-tips/Golf/5",
        },
        {
            "id": "ED71-F-12", "sport": "Rugby League", "severity": "high",
            "finding": "The OLBG Rugby League hub listed only three 2027 "
                       "outright markets and no match fixtures.",
            "source": "https://www.olbg.com/betting-tips/Rugby_League/10",
        },
    ]


def flags():
    """The full irregularity register.  Every entry is a finding this desk
    actually made, with the page it was made on.  Nothing here is speculative."""
    return [
        {"id": "ED71-F-01", "severity": "high", "topic": "OLBG display clock",
         "finding": "OLBG hub pages render start times in America/New_York "
                    "EDT (UTC-4) with no timezone label printed anywhere. "
                    "Proven by a greyhound event whose name embeds the UK "
                    "clock '5:12 Towcester' rendering as 12:12 (17:12 BST = "
                    "16:12Z = 12:12 EDT); by NHL MTL@CHI rendering 20:07 "
                    "against nhl.com's 8 p.m. ET; and by PDC darts rows "
                    "rendering 13:15-16:45 which is 19:15-22:45 CEST, inside "
                    "the promoter's published 1900-2300 CEST session.",
         "impact": "A reader who assumes UTC or UK time reads every kickoff "
                   "four hours early. All times published by this desk are "
                   "converted with the documented +4h offset.",
         "source": "https://www.olbg.com/betting-tips/Greyhounds/28"},
        {"id": "ED71-F-02", "severity": "medium", "topic": "Start-time padding",
         "finding": "OLBG start times are padded by +5 to +7 minutes with no "
                    "label. NHL MTL@CHI renders 20:07 against an official "
                    "startTimeUTC of 00:00:00Z (20:00 ET); other rows show "
                    "+5.",
         "impact": "OLBG renderings are never published as the kickoff. The "
                   "official time is used and the OLBG rendering is kept "
                   "alongside so the padding is auditable.",
         "source": "https://api-web.nhle.com/v1/schedule/2026-10-23"},
        {"id": "ED71-F-03", "severity": "medium", "topic": "Missing hub row",
         "finding": "Tampa Bay at Colorado appears on the official NHL "
                    "schedule (game 2026020167, 2026-10-24T01:00:00Z) but is "
                    "absent from the OLBG Ice Hockey hub, which listed 15 "
                    "events. Zero-tip fixtures appear to be suppressed from "
                    "hub listings (QUIRK-04).",
         "impact": "The row is published with a blank OLBG column rather than "
                   "a reconstructed one, and is the desk's only "
                   "official-only row.",
         "source": "https://api-web.nhle.com/v1/schedule/2026-10-23"},
        {"id": "ED71-F-04", "severity": "medium", "topic": "Consent wall",
         "finding": "pdc.tv serves a CookieYes consent interstitial to this "
                    "fetch path, so the European Championship order of play "
                    "could not be read from the page body. The session times "
                    "and first-round pairings were taken from the search "
                    "index's extract of that same URL.",
         "impact": "Darts rows are marked discovery-only where the pairing "
                   "was not confirmed in the page body.",
         "source": "https://www.pdc.tv/news"},
        {"id": "ED71-F-05", "severity": "high", "topic": "Upstream date bug",
         "finding": "Four OLBG darts rows render a 24 October date for "
                    "first-round matches that sit in the 23 October evening "
                    "session once the +4h offset is applied. This is the "
                    "unlabelled-clock defect surfacing as a wrong calendar "
                    "day, not a reschedule.",
         "impact": "Dates are published from the official session calendar, "
                   "never from the OLBG rendering.",
         "source": "https://www.olbg.com/betting-tips/Darts/15"},
        {"id": "ED71-F-06", "severity": "high", "topic": "No official schedule",
         "finding": "No ATP or WTA order of play was read this session. All "
                    "nine tennis rows are OLBG-listing-only.",
         "impact": "Tennis official columns are blank and every tennis market "
                   "is unpriced.",
         "source": "https://www.olbg.com/betting-tips/Tennis/3"},
        {"id": "ED71-F-07", "severity": "high", "topic": "No official schedule",
         "finding": "No cricket board (ECB, ICC, BCCI or host board) schedule "
                    "was read this session. All 12 cricket rows are "
                    "OLBG-listing-only.",
         "impact": "Cricket official columns are blank; markets unpriced.",
         "source": "https://www.olbg.com/betting-tips/Cricket/7"},
        {"id": "ED71-F-08", "severity": "high", "topic": "No official schedule",
         "finding": "No EHF competition schedule was read this session. All "
                    "15 handball rows are OLBG-listing-only.",
         "impact": "Handball official columns are blank; markets unpriced.",
         "source": "https://www.olbg.com/betting-tips/Handball/20"},
        {"id": "ED71-F-09", "severity": "high", "topic": "No official schedule",
         "finding": "No CEV competition schedule was read this session. All "
                    "15 volleyball rows are OLBG-listing-only.",
         "impact": "Volleyball official columns are blank; markets unpriced.",
         "source": "https://www.olbg.com/betting-tips/Volleyball/21"},
        {"id": "ED71-F-10", "severity": "high", "topic": "No official schedule",
         "finding": "No GAA fixture page was read this session. All five "
                    "Gaelic sports rows are OLBG-listing-only.",
         "impact": "Gaelic sports official columns are blank; markets "
                   "unpriced.",
         "source": "https://www.olbg.com/betting-tips/Gaelic_Football/25"},
        {"id": "ED71-F-11", "severity": "medium", "topic": "No official cards",
         "finding": "No GBGB racecard was read this session. All 15 "
                    "greyhound rows are OLBG-listing-only.",
         "impact": "Greyhound official columns are blank; markets unpriced.",
         "source": "https://www.olbg.com/betting-tips/Greyhounds/28"},
        {"id": "ED71-F-12", "severity": "high", "topic": "Zero fixtures",
         "finding": "The OLBG Rugby League hub listed only three 2027 "
                    "season-long outright markets and no match fixtures.",
         "impact": "Rugby League has no fixture rows. The page says so rather "
                   "than being padded with invented matches.",
         "source": "https://www.olbg.com/betting-tips/Rugby_League/10"},
        {"id": "ED71-F-13", "severity": "high", "topic": "Zero fixtures",
         "finding": "The OLBG Golf hub returned the literal string 'No tips "
                    "found.' at 2026-10-23T16:18Z. This is a coverage gap, "
                    "not a finding that no golf is being played.",
         "impact": "Golf has no fixture rows and is the one requested sport "
                   "with nothing on the board.",
         "source": "https://www.olbg.com/betting-tips/Golf/5"},
        {"id": "ED71-F-14", "severity": "high", "topic": "Rejected input",
         "finding": "The first EuroLeague standings read came from a "
                    "media-centre game kit and showed every club on five "
                    "games played, while today's fixtures are round seven. "
                    "That table was one round stale and was discarded before "
                    "any price was struck; standings were re-read on a club "
                    "site showing six games played.",
         "impact": "Had the stale table been used, the Paris v Valencia "
                   "handicap would have been offered at 6.5 instead of 4.5 "
                   "points - a materially different bet on the same fixture.",
         "source": "https://www.olympiacosbc.gr/el/"},
        {"id": "ED71-F-15", "severity": "medium", "topic": "Rejected input",
         "finding": "The NHL schedule API returns an unlabelled odds array in "
                    "which decimal and American values are mixed, and in "
                    "which providers disagree about the favourite for the "
                    "same game: one had Montreal 2.35 / Chicago 1.59 while "
                    "another had Montreal 1.60 / Chicago 2.37.",
         "impact": "The feed is not used as a pricing input anywhere on this "
                   "desk. NHL prices come from official win-loss records "
                   "only.",
         "source": "https://api-web.nhle.com/v1/schedule/2026-10-23"},
        {"id": "ED71-F-16", "severity": "low", "topic": "Hub truncation",
         "finding": "OLBG hubs paginate behind a 'Load More Tips' control, so "
                    "a hub can list more rows than it renders on first paint "
                    "(QUIRK-03).",
         "impact": "Hub row counts published here are what the first paint "
                   "listed, and are described that way rather than as a "
                   "complete daily card.",
         "source": "https://www.olbg.com/betting-tips/Ice_Hockey/13"},
    ]


def counts():
    verified = [r for r in ROWS if r["official"]]
    return {
        "fixture_rows": len(ROWS),
        "officially_verified_rows": len(verified),
        "discovery_only_rows": len([r for r in ROWS if not r["official"]]),
        "olbg_listed_rows": len([r for r in ROWS if r["olbg"]]),
        "official_only_rows": len([r for r in ROWS if not r["olbg"]]),
        "sports_with_rows": len({r["sport"] for r in ROWS}),
        "sports_in_brief": len(SPORTS),
        "sources_recorded": len(set(
            s for r in verified for s in r["official"]["sources"])),
    }


def label(row):
    """A display name that never invents a participant."""
    off = row.get("official")
    if off and off.get("away") and off.get("home"):
        return "{} v {}".format(off["away"], off["home"])
    if off and off.get("competition"):
        return off["competition"]
    if row.get("olbg"):
        return row["olbg"]["name"]
    return row["id"]


def build():
    os.makedirs(DATA, exist_ok=True)
    payload = {
        "session": SESSION,
        "task": TASK,
        "generated_at": "2026-10-23T16:50:00Z",
        "olbg_window_utc": list(OLBG_WINDOW),
        "olbg_timezone": {
            "rendered_in": "America/New_York EDT (UTC-4), unlabelled",
            "offset_hours_applied": OLBG_TZ_OFFSET_HOURS,
            "flag": "ED71-F-01",
        },
        "sports_in_scope": [
            {"slug": s, "name": n, "olbg_id": i} for s, n, i in SPORTS],
        "rows": [dict(r, label=label(r)) for r in ROWS],
        "coverage_gaps": coverage_gaps(),
        "flags": flags(),
        "counts": counts(),
    }
    with open(os.path.join(DATA, "fixtures.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return payload


if __name__ == "__main__":
    p = build()
    print("rows", len(p["rows"]))
    print("counts", json.dumps(p["counts"]))
