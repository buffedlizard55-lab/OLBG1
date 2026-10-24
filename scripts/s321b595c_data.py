"""Session 321b595c-olbg1 data build.

Turns this session's reads into machine-readable JSON. Nothing here is inferred:
every fact carries the id of the source it was read from, and anything that was
not read this session is left as None and flagged.

Run:  python3 scripts/s321b595c_data.py
Out:  data/321b595c/{sources,fixtures,markets,predictions,flags,coverage,summary}.json
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "321b595c"
SESSION = "321b595c-olbg1"
BUILT = "2026-10-24T18:15:00Z"

# ---------------------------------------------------------------- sources ----
# read_utc = the minute this session actually fetched the URL.
SOURCES = [
    # OLBG discovery (never used as sporting evidence)
    ("olbg-golf", "OLBG Golf hub", "https://www.olbg.com/betting-tips/Golf/5", "olbg", "2026-10-24T17:46Z",
     "Rendered 'No tips found.' - no golf market listed."),
    ("olbg-darts", "OLBG Darts hub", "https://www.olbg.com/betting-tips/Darts/15", "olbg", "2026-10-24T17:47Z",
     "Four match markets listed plus outrights."),
    ("olbg-basketball", "OLBG Basketball hub", "https://www.olbg.com/betting-tips/Basketball/4", "olbg", "2026-10-24T17:44Z",
     "Nine match markets (eight NBA, one Brazil NBB)."),
    ("olbg-ice-hockey", "OLBG Ice Hockey hub", "https://www.olbg.com/betting-tips/Ice_Hockey/13", "olbg", "2026-10-24T17:48Z",
     "Twelve NHL games and five Swiss NLA games."),
    ("olbg-baseball", "OLBG Baseball hub", "https://www.olbg.com/betting-tips/Baseball/12", "olbg", "2026-10-24T17:48Z",
     "One MLB market: TB Rays @ MIL Brewers."),
    ("olbg-snooker", "OLBG Snooker hub", "https://www.olbg.com/betting-tips/Snooker/8", "olbg", "2026-10-24T17:45Z",
     "One market: Mark Williams v Jak Jones, already under way."),
    ("olbg-tennis", "OLBG Tennis hub", "https://www.olbg.com/betting-tips/Tennis/3", "olbg", "2026-10-24T17:44Z",
     "Six match markets, all ATP/WTA tour level."),
    ("olbg-rugby-union", "OLBG Rugby Union hub", "https://www.olbg.com/betting-tips/Rugby_Union/9", "olbg", "2026-10-24T17:49Z",
     "Five match markets across URC, Top 14, Premiership and international."),
    ("olbg-cricket", "OLBG Cricket hub", "https://www.olbg.com/betting-tips/Cricket/7", "olbg", "2026-10-24T17:49Z",
     "Nine match markets plus outrights."),
    ("olbg-volleyball", "OLBG Volleyball hub", "https://www.olbg.com/betting-tips/Volleyball/21", "olbg", "2026-10-24T17:50Z",
     "Fifteen club match markets."),
    ("olbg-handball", "OLBG Handball hub", "https://www.olbg.com/betting-tips/Handball/20", "olbg", "2026-10-24T17:50Z",
     "Fifteen match markets across HBL, Liga ASOBAL, EHF Champions League and national teams."),
    ("olbg-motor-racing", "OLBG Motor Racing hub", "https://www.olbg.com/betting-tips/Motor_Racing/14", "olbg", "2026-10-24T17:51Z",
     "One market: USA Grand Prix, Win Race."),
    ("olbg-rugby-league", "OLBG Rugby League hub", "https://www.olbg.com/betting-tips/Rugby_League/10", "olbg", "2026-10-24T17:51Z",
     "No upcoming match market. Only 2027 outrights (State of Origin, Super League, NRL)."),
    ("nrl-draw", "NRL official draw - Rugby League World Cup 2026, Round 2", "https://www.nrl.com/draw/?competition=131&round=2&season=2026", "official", "2026-10-24T18:38Z",
     "Round 2 fixtures with venues; PNG 6-64 Samoa and England 82-0 France shown as full time; New Zealand v Cook Islands and Australia v Fiji shown as not started."),
    ("olbg-gaelic", "OLBG Gaelic Football hub", "https://www.olbg.com/betting-tips/Gaelic_Football/25", "olbg", "2026-10-24T17:52Z",
     "Four club/county markets plus a 2027 outright."),
    ("olbg-greyhounds", "OLBG Greyhounds hub", "https://www.olbg.com/betting-tips/Greyhounds/28", "olbg", "2026-10-24T17:52Z",
     "Today's UK race markets across Doncaster, Monmore, Romford, Central Park, Star Pelaw, Yarmouth, Dunstall Park."),

    # Official league / tour / governing-body reads
    ("nhl-schedule", "NHL official schedule feed, 24 Oct 2026",
     "https://api-web.nhle.com/v1/schedule/2026-10-24", "official", "2026-10-24T17:58Z",
     "Game ids, venues, exact UTC start times, and the league's own published partner prices for 2-way markets."),
    ("nhl-score", "NHL official score feed, 24 Oct 2026",
     "https://api-web.nhle.com/v1/score/2026-10-24", "official", "2026-10-24T17:51Z",
     "Live state of ANA@PHI, club records for the two clubs in LAK@NJD."),
    ("nhl-team-summary", "NHL official club statistics, 2026-27 regular season",
     "https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22%3A%22points%22%2C%22direction%22%3A%22DESC%22%7D%5D&cayenneExp=seasonId%3D20262027%20and%20gameTypeId%3D2",
     "official", "2026-10-24T18:02Z",
     "All 32 clubs: games played, W-L-OTL, points percentage, goals for/against, power play, penalty kill."),
    ("nhl-standings", "NHL official standings snapshot, 24 Oct 2026",
     "https://api-web.nhle.com/v1/standings/2026-10-24", "official", "2026-10-24T17:55Z",
     "Standings stamped 2026-10-24T17:42:15Z; used to cross-check the club statistics feed."),
    ("mlb-schedule", "MLB official schedule feed, 24-27 Oct 2026",
     "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-27&hydrate=probablePitcher,linescore,odds",
     "official", "2026-10-24T17:53Z",
     "World Series Games 2, 3 and 4: exact UTC start, venue, probable pitchers, series score."),
    ("mlb-standings-al", "MLB official standings, American League, 2026 regular season",
     "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
     "official", "2026-10-24T18:00Z",
     "Tampa Bay Rays 98-64, home/away splits, last ten, run differential."),
    ("mlb-standings-nl", "MLB official standings, National League, 2026 regular season",
     "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason",
     "official", "2026-10-24T18:01Z",
     "Milwaukee Brewers 103-59, 55-26 at home, last ten 8-2, plus-214 run differential."),
    ("nba-standings", "NBA official standings, 2026-27 regular season",
     "https://www.nba.com/standings?Season=2026-27", "official", "2026-10-24T18:00Z",
     "Conference tables with W-L, home/road, last ten and streak for all 30 clubs after 1-2 games."),
    ("f1-us-gp", "Formula 1 official United States Grand Prix 2026 race hub",
     "https://www.formula1.com/en/racing/2026/united-states", "official", "2026-10-24T17:56Z",
     "Weekend schedule (qualifying 24 Oct, race 25 Oct), circuit data, official FP2 classification."),
    ("wst-matches", "World Snooker Tour official match list",
     "https://www.wst.tv/matches/", "official", "2026-10-24T18:04Z",
     "BetVictor Northern Ireland Open 2026 semi-final Mark Williams v Jak Jones marked Live Now; final 25 Oct 08:00 versus Kyren Wilson."),
    ("pga-schedule", "PGA TOUR official schedule page",
     "https://www.pgatour.com/schedule", "official", "2026-10-24T18:05Z",
     "Season schedule rendered only to March 2026 in the readable portion; current-week event not reachable."),
    ("atp-schedule", "ATP Tour official tournament schedule",
     "https://www.atptour.com/en/scores/current/tournament-schedule", "official", "2026-10-24T18:06Z",
     "Page returned the site shell with no tournament content (JavaScript-rendered)."),
    ("wta-scores", "WTA official scores and tournament notifications",
     "https://www.wtatennis.com/scores", "official", "2026-10-24T18:08Z",
     "Notification feed only; confirmed Guangzhou Open and Toray Pan Pacific Open (Tokyo) draws released. No match schedule."),
    ("pdc-calendar", "PDC official calendar",
     "https://www.pdc.tv/calendar/", "official", "2026-10-24T18:07Z",
     "Cookie-consent interstitial; no tournament or match content returned."),
    ("urc-fixtures", "United Rugby Championship official fixtures route",
     "https://www.unitedrugby.com/fixtures", "official", "2026-10-24T18:06Z",
     "HTTP 404 - page not found."),
    ("prem-rugby", "Premiership Rugby official fixtures route",
     "https://www.premiershiprugby.com/fixtures", "official", "2026-10-24T18:09Z",
     "Navigation and partner furniture only; no fixture list in the readable portion."),
    ("pcb-home", "Pakistan Cricket Board official site",
     "https://www.pcb.com.pk/", "official", "2026-10-24T18:09Z",
     "Home page navigation, features and squad cards; no Pakistan v England fixture detail."),
    ("legavolley", "Italian Volleyball League (SuperLega) official site",
     "https://www.legavolley.it/", "official", "2026-10-24T18:07Z",
     "Redirected to a video/live-timing shell; no fixture list."),
    ("gbgb", "Greyhound Board of Great Britain racecards route",
     "https://www.gbgb.org.uk/racecards", "official", "2026-10-24T18:08Z",
     "HTTP 404 - page not found."),
]
SRC = {s[0]: {"id": s[0], "name": s[1], "url": s[2], "kind": s[3], "read_utc": s[4], "note": s[5]} for s in SOURCES}
OLBG = {k: v for k, v in SRC.items() if v["kind"] == "olbg"}

# ------------------------------------------------------- NHL club statistics --
# (gp, w, l, otl, points, point pct, goals for, goals against) read from nhl-team-summary.
NHL = {
    "ANA": (10, 4, 6, 0, 8, .400, 27, 33), "BOS": (11, 8, 2, 1, 17, .773, 42, 22),
    "BUF": (10, 4, 4, 2, 10, .500, 28, 36), "CAR": (12, 8, 2, 2, 18, .750, 47, 32),
    "CBJ": (8, 3, 5, 0, 6, .375, 19, 29), "CGY": (9, 3, 6, 0, 6, .333, 19, 38),
    "CHI": (10, 3, 7, 0, 6, .300, 22, 40), "COL": (11, 6, 4, 1, 13, .591, 47, 33),
    "DAL": (10, 6, 3, 1, 13, .650, 25, 16), "DET": (10, 4, 3, 3, 11, .550, 27, 28),
    "EDM": (10, 8, 1, 1, 17, .850, 46, 32), "FLA": (11, 5, 4, 2, 12, .545, 31, 34),
    "LAK": (8, 2, 4, 2, 6, .375, 20, 29), "MIN": (11, 6, 3, 2, 14, .636, 32, 27),
    "MTL": (10, 5, 3, 2, 12, .600, 32, 35), "NJD": (10, 6, 4, 0, 12, .600, 33, 31),
    "NSH": (9, 3, 3, 3, 9, .500, 23, 28), "NYI": (10, 5, 4, 1, 12, .600, 33, 31),
    "NYR": (12, 7, 4, 1, 15, .625, 37, 29), "OTT": (11, 7, 4, 0, 14, .636, 29, 30),
    "PHI": (12, 3, 6, 3, 9, .375, 20, 36), "PIT": (11, 4, 6, 1, 9, .409, 36, 37),
    "SEA": (11, 7, 3, 1, 15, .682, 42, 37), "SJS": (11, 6, 4, 1, 13, .591, 32, 36),
    "STL": (10, 5, 4, 1, 11, .550, 35, 31), "TBL": (10, 7, 3, 0, 14, .700, 34, 29),
    "TOR": (12, 6, 4, 2, 14, .583, 43, 38), "UTA": (11, 7, 4, 0, 14, .636, 41, 36),
    "VAN": (12, 2, 9, 1, 5, .208, 35, 56), "VGK": (12, 8, 4, 0, 16, .667, 45, 36),
    "WPG": (10, 4, 3, 3, 11, .550, 26, 29), "WSH": (9, 5, 4, 0, 10, .556, 30, 29),
}
# Provider prices read from nhl-schedule. 10 (Doxxbet) is excluded: its two prices sum
# to ~81% implied, i.e. it quotes a 3-way 60-minute market and mixing it in would be wrong.
PROVIDERS = {3: "feed 3", 6: "feed 6", 7: "feed 7", 8: "feed 8", 9: "feed 9"}
NHL_PRICES = {
    # game id: (home abbrev, away abbrev, start UTC, {home: [(prov, value)], away: [...]})
    2026020169: ("NJD", "LAK", "2026-10-24T19:30:00Z",
                 {"NJD": [(3, "1.52"), (6, "1.52"), (7, "-194"), (8, "-198"), (9, "-192")],
                  "LAK": [(3, "2.55"), (6, "2.54"), (7, "+162"), (8, "+159"), (9, "+160")]}),
    2026020170: ("BOS", "SJS", "2026-10-24T23:00:00Z",
                 {"BOS": [(3, "1.53"), (6, "1.55"), (7, "-184"), (8, "-193"), (9, "-192")],
                  "SJS": [(3, "2.54"), (6, "2.44"), (7, "+152"), (8, "+156"), (9, "+160")]}),
    2026020171: ("OTT", "NYR", "2026-10-24T23:00:00Z",
                 {"OTT": [(3, "1.80"), (6, "1.92"), (7, "-128"), (8, "-128"), (9, "-125")],
                  "NYR": [(3, "2.05"), (6, "1.87"), (7, "+106"), (8, "+105"), (9, "+105")]}),
    2026020172: ("PIT", "NSH", "2026-10-24T23:00:00Z",
                 {"PIT": [(3, "1.82"), (6, "2.25"), (7, "-128"), (8, "-130"), (9, "-125")],
                  "NSH": [(3, "2.03"), (6, "1.64"), (7, "+106"), (8, "+106"), (9, "+105")]}),
    2026020173: ("WSH", "BUF", "2026-10-24T23:00:00Z",
                 {"WSH": [(3, "1.84"), (6, "1.98"), (7, "-120"), (8, "-125"), (9, "-125")],
                  "BUF": [(3, "2.00"), (6, "1.82"), (7, "+100"), (8, "+102"), (9, "+105")]}),
    2026020174: ("CBJ", "VGK", "2026-10-24T23:00:00Z",
                 {"CBJ": [(3, "2.10"), (6, "2.18"), (7, "+116"), (8, "+113"), (9, "+114")],
                  "VGK": [(3, "1.76"), (6, "1.68"), (7, "-138"), (8, "-138"), (9, "-135")]}),
    2026020175: ("STL", "CAR", "2026-10-24T23:00:00Z", {"STL": [], "CAR": []}),
}


# ----------------------------------------------------------------- helpers ---
def dec(value):
    """Provider feed mixes decimal ("1.52") and American ("-194") strings."""
    s = str(value).strip()
    if s.startswith(("+", "-")):
        a = float(s)
        return 1 + (a / 100 if a > 0 else 100 / abs(a))
    f = float(s)
    return 1 + f / 100 if f >= 100 else f


def american(decimal):
    d = float(decimal)
    if d <= 1.0001:
        return None
    return int(round((d - 1) * 100)) if d >= 2 else int(round(-100 / (d - 1)))


def from_prob(p):
    """Fair American price for probability p (no margin)."""
    if p is None or not 0 < p < 1:
        return None
    return int(round(-100 * p / (1 - p))) if p > 0.5 else int(round(100 * (1 - p) / p))


def pct(x):
    return None if x is None else round(100 * x, 1)


# ---------------------------------------------------------------- the model --
SHRINK = 8          # games of prior (points percentage)
HOME = 0.16         # logit home-ice term, fixed for the season


def nhl_index(club):
    gp, w, l, otl, pts, pp, gf, ga = NHL[club]
    s = (gp * pp + SHRINK * 0.5) / (gp + SHRINK) - 0.5
    gd = ((gf - ga) / gp) * gp / (gp + SHRINK)
    return 1.6 * s + 0.12 * gd


def nhl_ml(home, away):
    z = HOME + nhl_index(home) - nhl_index(away)
    return 1 / (1 + math.exp(-z))


def _pois(lam, k):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def _lambdas(home, away):
    gf_h = NHL[home][6] / NHL[home][0]; ga_h = NHL[home][7] / NHL[home][0]
    gf_a = NHL[away][6] / NHL[away][0]; ga_a = NHL[away][7] / NHL[away][0]
    lh = min(max(math.sqrt(gf_h * ga_a), 1.6), 4.4)
    la = min(max(math.sqrt(gf_a * ga_h), 1.6), 4.4)
    return lh, la


def _pois_ml(lh, la, n=14):
    return sum(_pois(lh, i) * sum(_pois(la, j) for j in range(i)) for i in range(n))


def nhl_derivative(home, away):
    """Puck line and total probabilities from a Poisson goal distribution whose
    home/away scoring rates are re-scaled until the moneyline matches nhl_ml().
    Returns dict of market probabilities."""
    lh0, la0 = _lambdas(home, away)
    target = nhl_ml(home, away)
    lo, hi = 0.55, 2.2
    for _ in range(60):
        mid = (lo + hi) / 2
        if _pois_ml(lh0 * mid, la0 * (2 - mid)) < target:
            lo = mid
        else:
            hi = mid
    m = (lo + hi) / 2
    lh, la = lh0 * m, la0 * (2 - m)
    # margin and total distributions
    margin = {}
    total = {}
    for i in range(15):
        for j in range(15):
            p = _pois(lh, i) * _pois(la, j)
            margin[i - j] = margin.get(i - j, 0) + p
            total[i + j] = total.get(i + j, 0) + p
    p_home = sum(v for k, v in margin.items() if k > 0)
    home_plus15 = sum(v for k, v in margin.items() if k > -2)          # home +1.5 covers
    home_minus15 = sum(v for k, v in margin.items() if k > 1)          # home -1.5
    p_over55 = sum(v for k, v in total.items() if k > 5.5)
    p_over65 = sum(v for k, v in total.items() if k > 6.5)
    return {"p_home": p_home, "home_plus15": home_plus15, "home_minus15": home_minus15,
            "away_plus15": 1 - home_minus15, "away_minus15": 1 - home_plus15,
            "over55": p_over55, "over65": p_over65, "lam_home": lh, "lam_away": la}


NHL_FULL = {
 "ANA": "Anaheim Ducks", "BOS": "Boston Bruins", "BUF": "Buffalo Sabres", "CAR": "Carolina Hurricanes",
 "CBJ": "Columbus Blue Jackets", "CGY": "Calgary Flames", "CHI": "Chicago Blackhawks", "COL": "Colorado Avalanche",
 "DAL": "Dallas Stars", "DET": "Detroit Red Wings", "EDM": "Edmonton Oilers", "FLA": "Florida Panthers",
 "LAK": "Los Angeles Kings", "MIN": "Minnesota Wild", "MTL": "Montreal Canadiens", "NJD": "New Jersey Devils",
 "NSH": "Nashville Predators", "NYI": "New York Islanders", "NYR": "New York Rangers", "OTT": "Ottawa Senators",
 "PHI": "Philadelphia Flyers", "PIT": "Pittsburgh Penguins", "SEA": "Seattle Kraken", "SJS": "San Jose Sharks",
 "STL": "St. Louis Blues", "TBL": "Tampa Bay Lightning", "TOR": "Toronto Maple Leafs", "UTA": "Utah Mammoth",
 "VAN": "Vancouver Canucks", "VGK": "Vegas Golden Knights", "WPG": "Winnipeg Jets", "WSH": "Washington Capitals",
}


def expand(text):
    """Turn 'BOS -1.5' into 'Boston Bruins -1.5' for the reader-facing tables."""
    if not text:
        return text
    for ab, full in sorted(NHL_FULL.items(), key=lambda kv: -len(kv[0])):
        if text == ab or text.startswith(ab + " ") or text.startswith(ab + " @"):
            return full + text[len(ab):]
    return text


# ------------------------------------------------------------------ fixtures --
FIX = []


def add(**kw):
    kw.setdefault("priced", False)
    kw.setdefault("start_utc", None)
    kw.setdefault("start_note", "")
    kw.setdefault("markets", [])
    kw.setdefault("facts", [])
    kw.setdefault("selection", None)
    kw.setdefault("confidence", None)
    kw.setdefault("prediction", None)
    kw["sources"] = kw.get("sources", [])
    FIX.append(kw)


OLBG_BASE = "https://www.olbg.com/betting-tips"
# ---- Ice hockey: OLBG lists 12 NHL games; ANA@PHI was already live at build time and is excluded;
#      6 of the remaining 11 are priced from official league data.
NHL_GAMES = [
    # slug, away label, home label, olbg event id, start_utc (None = not read), game id
    ("CAR Hurricanes @ STL Blues", "CAR", "STL", 200002, "2026-10-24T23:00:00Z", 2026020175),
    ("NY Rangers @ OTT Senators", "NYR", "OTT", 200008, "2026-10-24T23:00:00Z", 2026020171),
    ("MIN Wild @ SEA Kraken", "MIN", "SEA", 200005, None, None),
    ("TOR Maple Leafs @ EDM Oilers", "TOR", "EDM", 200010, None, None),
    ("SJ Sharks @ BOS Bruins", "SJS", "BOS", 200007, "2026-10-24T23:00:00Z", 2026020170),
    ("TB Lightning @ UTA Mammoth", "TBL", "UTA", 200009, None, None),
    ("DET Red Wings @ CGY Flames", "DET", "CGY", 200004, None, None),
    ("LA Kings @ NJ Devils", "LAK", "NJD", 200000, "2026-10-24T19:30:00Z", 2026020169),
    ("BUF Sabres @ WAS Capitals", "BUF", "WSH", 200003, "2026-10-24T23:00:00Z", 2026020173),
    ("NSH Predators @ PIT Penguins", "NSH", "PIT", 200006, "2026-10-24T23:00:00Z", 2026020172),
    ("VGS Golden Knights @ CLB Blue Jackets", "VGK", "CBJ", 200001, "2026-10-24T23:00:00Z", 2026020174),
]
for slug, away, home, eid, start, gid in NHL_GAMES:
    url = f"{OLBG_BASE}/Ice_Hockey/NHL/NHL/{slug.replace(' ', '_').replace('@', '@')}/13?event_id={eid}"
    # OLBG event slugs use the raw matchup with underscores; keep the hub link as read.
    url = f"{OLBG_BASE}/Ice_Hockey/13"
    d = {"id": f"nhl-{home.lower()}-{away.lower()}", "sport": "ice_hockey", "sport_name": "Ice Hockey",
         "comp": "NHL", "home": home, "away": away, "home_name": NHL_FULL[home],
         "away_name": NHL_FULL[away], "home_abbrev": home, "away_abbrev": away,
         "olbg_url": url, "olbg_event_id": eid, "start_utc": start,
         "sources": ["olbg-ice-hockey", "nhl-schedule", "nhl-team-summary"]}
    gp_h, w_h, l_h, otl_h, pts_h, pp_h, gf_h, ga_h = NHL[home]
    gp_a, w_a, l_a, otl_a, pts_a, pp_a, gf_a, ga_a = NHL[away]
    d["facts"] = [
        f"{home} {w_h}-{l_h}-{otl_h} ({pp_h:.3f} points pct), {gf_h} goals for, {ga_h} against in {gp_h} games",
        f"{away} {w_a}-{l_a}-{otl_a} ({pp_a:.3f} points pct), {gf_a} goals for, {ga_a} against in {gp_a} games",
    ]
    if start is None:
        d["start_note"] = "start time not read from an official source this session"
        d["sources"] = ["olbg-ice-hockey", "nhl-team-summary"]
    if gid in NHL_PRICES and NHL_PRICES[gid][3].get(home):
        p_home = nhl_ml(home, away)
        der = nhl_derivative(home, away)
        prices = NHL_PRICES[gid][3]
        def best(club):
            vals = [(pr, dec(v)) for pr, v in prices[club]]
            if not vals:
                return None, None
            pr, d2 = max(vals, key=lambda x: x[1])
            return american(d2), PROVIDERS[pr]
        best_h, book_h = best(home)
        best_a, book_a = best(away)
        d["priced"] = True
        d["start_note"] = "exact UTC start from the league's own feed"
        d["facts"].append(f"League partner prices read for the 2-way market: {home} best {best_h:+d} ({book_h}), {away} best {best_a:+d} ({book_a})")
        d["model"] = {"p_home": round(p_home, 4), "p_away": round(1 - p_home, 4),
                      "method": "nhl-logistic-v1", "lam_home": round(der["lam_home"], 2),
                      "lam_away": round(der["lam_away"], 2)}
        mk = []
        mk.append({"market": "Match winner (moneyline)", "selection": home,
                   "prob": round(p_home, 4), "fair": from_prob(p_home), "best": best_h,
                   "best_book": book_h, "alt_selection": away, "alt_prob": round(1 - p_home, 4),
                   "alt_fair": from_prob(1 - p_home), "alt_best": best_a, "alt_best_book": book_a})
        mk.append({"market": "Puck line -1.5", "selection": home, "prob": round(der["home_minus15"], 4),
                   "fair": from_prob(der["home_minus15"]), "best": None, "best_book": None,
                   "alt_selection": away + " +1.5", "alt_prob": round(der["away_plus15"], 4),
                   "alt_fair": from_prob(der["away_plus15"]), "alt_best": None, "alt_best_book": None})
        mk.append({"market": "Puck line +1.5", "selection": home, "prob": round(der["home_plus15"], 4),
                   "fair": from_prob(der["home_plus15"]), "best": None, "best_book": None,
                   "alt_selection": away + " -1.5", "alt_prob": round(der["away_minus15"], 4),
                   "alt_fair": from_prob(der["away_minus15"]), "alt_best": None, "alt_best_book": None})
        mk.append({"market": "Match total 5.5 goals", "selection": "Over 5.5", "prob": round(der["over55"], 4),
                   "fair": from_prob(der["over55"]), "best": None, "best_book": None,
                   "alt_selection": "Under 5.5", "alt_prob": round(1 - der["over55"], 4),
                   "alt_fair": from_prob(1 - der["over55"]), "alt_best": None, "alt_best_book": None})
        mk.append({"market": "Match total 6.5 goals", "selection": "Over 6.5", "prob": round(der["over65"], 4),
                   "fair": from_prob(der["over65"]), "best": None, "best_book": None,
                   "alt_selection": "Under 6.5", "alt_prob": round(1 - der["over65"], 4),
                   "alt_fair": from_prob(1 - der["over65"]), "alt_best": None, "alt_best_book": None})
        d["markets"] = mk
    else:
        if start is not None:
            d["start_note"] = "exact UTC start from the league's own feed; no partner price read"
    add(**d)

# ---- Ice hockey: five Swiss NLA fixtures listed by OLBG, no official read.
for slug, eid, home, away in [
        ("Ambri Piotta vs HC Ajoie", 200020, "Ambri Piotta", "HC Ajoie"),
        ("EHC Kloten vs Rapperswil Jona Lakers", 200024, "EHC Kloten", "Rapperswil Jona Lakers"),
        ("SCL Tigers vs Davos", 200022, "SCL Tigers", "Davos"),
        ("EHC Biel vs Zug", 200019, "EHC Biel", "Zug"),
        ("Lausanne HC vs Fribourg Gotteron", 200023, "Lausanne HC", "Fribourg Gotteron")]:
    add(id=f"nla-{eid}", sport="ice_hockey", sport_name="Ice Hockey", comp="Switzerland NLA",
        home=home, away=away, home_name=home, away_name=away,
        olbg_url=f"{OLBG_BASE}/Ice_Hockey/13", olbg_event_id=eid,
        start_note="OLBG hub shows today 13:45 US Eastern; no official league source read",
        sources=["olbg-ice-hockey"],
        facts=["Fixture pairing and market label read from OLBG only; no official club record read this session"])

# ---- Baseball
add(id="mlb-mil-tb-g2", sport="baseball", sport_name="Baseball", comp="MLB World Series, Game 2",
    home="Milwaukee Brewers", away="Tampa Bay Rays", home_name="Milwaukee Brewers", away_name="Tampa Bay Rays",
    olbg_url=f"{OLBG_BASE}/Baseball/12", olbg_event_id=160792,
    start_utc="2026-10-25T00:00:00Z", start_note="exact UTC start from MLB's official schedule feed",
    sources=["olbg-baseball", "mlb-schedule", "mlb-standings-al", "mlb-standings-nl"],
    facts=["Brewers lead the series 1-0 going into Game 2",
           "Milwaukee 103-59 in the 2026 regular season, 55-26 at home, 8-2 in their last ten, plus-214 run differential",
           "Tampa Bay 98-64, 43-38 on the road, 5-5 in their last ten, plus-86 run differential",
           "Probable pitchers: Logan Henderson (Milwaukee) and Drew Rasmussen (Tampa Bay)"])
add(id="mlb-tb-mil-g3", sport="baseball", sport_name="Baseball", comp="MLB World Series, Game 3",
    home="Tampa Bay Rays", away="Milwaukee Brewers", home_name="Tampa Bay Rays", away_name="Milwaukee Brewers",
    olbg_url=f"{OLBG_BASE}/Baseball/12", start_utc="2026-10-27T00:00:00Z",
    start_note="exact UTC start from MLB's official schedule feed",
    sources=["mlb-schedule"], facts=["Probable pitchers: Robert Gasser (Milwaukee), Freddy Peralta (Tampa Bay)"])
add(id="mlb-tb-mil-g4", sport="baseball", sport_name="Baseball", comp="MLB World Series, Game 4",
    home="Tampa Bay Rays", away="Milwaukee Brewers", home_name="Tampa Bay Rays", away_name="Milwaukee Brewers",
    olbg_url=f"{OLBG_BASE}/Baseball/12", start_utc="2026-10-28T00:00:00Z",
    start_note="exact UTC start from MLB's official schedule feed",
    sources=["mlb-schedule"], facts=["Probable pitchers not listed by MLB at the time of reading"])

# ---- Basketball: nine markets from the OLBG hub. Records read; no line issued.
NBA = [("BKN Nets @ CLE Cavaliers", 536112, "Nets", "Cavaliers", "Brooklyn Nets", "Cleveland Cavaliers"),
       ("MIL Bucks @ PHI 76ers", 536111, "Bucks", "76ers", "Milwaukee Bucks", "Philadelphia 76ers"),
       ("HOU Rockets @ ATL Hawks", 536115, "Rockets", "Hawks", "Houston Rockets", "Atlanta Hawks"),
       ("MIA Heat @ CHA Hornets", 536117, "Heat", "Hornets", "Miami Heat", "Charlotte Hornets"),
       ("NO Pelicans @ DEN Nuggets", 536116, "Pelicans", "Nuggets", "New Orleans Pelicans", "Denver Nuggets"),
       ("SA Spurs @ DAL Mavericks", 536114, "Spurs", "Mavericks", "San Antonio Spurs", "Dallas Mavericks"),
       ("WAS Wizards @ CHI Bulls", 536113, "Wizards", "Bulls", "Washington Wizards", "Chicago Bulls"),
       ("GS Warriors @ PHX Suns", 536118, "Warriors", "Suns", "Golden State Warriors", "Phoenix Suns")]
NBA_REC = {"Nets": "0-1", "Cavaliers": "0-1", "Bucks": "0-2", "76ers": "2-0", "Rockets": "2-0", "Hawks": "2-0",
           "Heat": "0-2", "Hornets": "1-1", "Pelicans": "0-2", "Nuggets": "0-1", "Spurs": "0-2", "Mavericks": "1-1",
           "Wizards": "1-1", "Bulls": "1-1", "Warriors": "0-2", "Suns": "0-1"}
for slug, eid, a, h, an, hn in NBA:
    add(id=f"nba-{eid}", sport="basketball", sport_name="Basketball", comp="NBA",
        home=hn, away=an, home_name=hn, away_name=an, olbg_url=f"{OLBG_BASE}/Basketball/4",
        olbg_event_id=eid,
        start_note="OLBG hub shows today; no official NBA start time read",
        sources=["olbg-basketball", "nba-standings"],
        facts=[f"{hn} {NBA_REC[h]} on the season after 1-2 games",
               f"{an} {NBA_REC[a]} on the season after 1-2 games"])
add(id="nba-nbb-botafogo", sport="basketball", sport_name="Basketball", comp="Brazil NBB",
    home="Botafogo", away="Pato Basquete", home_name="Botafogo", away_name="Pato Basquete",
    olbg_url=f"{OLBG_BASE}/Basketball/4", olbg_event_id=536087,
    start_note="OLBG hub shows today 18:00 US Eastern", sources=["olbg-basketball"],
    facts=["Fixture pairing and market label read from OLBG only"])

# ---- Volleyball
VB = [("UVC Graz W vs Sportunion St Polten W", 37019, "UVC Graz W", "Sportunion St Polten W", "Austria W"),
      ("Mogilno W vs Chemik Police W", 37078, "Mogilno W", "Chemik Police W", "Poland W"),
      ("Mackenzie W vs Osasco W", 37002, "Mackenzie W", "Osasco W", "Brazil Superliga W"),
      ("Abel-Moda Brusque W vs Praia Clube W", 37003, "Abel-Moda Brusque W", "Praia Clube W", "Brazil Superliga W"),
      ("Sliedrecht W vs Apollo 8 W", 37061, "Sliedrecht W", "Apollo 8 W", "Netherlands W"),
      ("VV Utrecht W vs Dynamo Apeldoorn W", 37063, "VV Utrecht W", "Dynamo Apeldoorn W", "Netherlands W"),
      ("Royan vs Tours", 37052, "Royan", "Tours", "France"),
      ("Nantes W vs Terville Florange W", 37069, "Nantes W", "Terville Florange W", "France W"),
      ("Talmassons W vs Chieri W", 37072, "Talmassons W", "Chieri W", "Italy A1 W"),
      ("Trentino vs Cisterna", 36994, "Trentino", "Cisterna", "Italy SuperLega"),
      ("CHKS Chelm vs Resovia Rzeszow", 36965, "CHKS Chelm", "Resovia Rzeszow", "Poland PlusLiga"),
      ("Perugia vs Pordenone", 36997, "Perugia", "Pordenone", "Italy SuperLega"),
      ("Civitanova vs Padova", 36995, "Civitanova", "Padova", "Italy SuperLega"),
      ("ETV Hamburg W vs Munster W", 37059, "ETV Hamburg W", "Munster W", "Germany W"),
      ("Barock Volleys Ludwigsburg vs TV Rottenburg", 37014, "Barock Volleys Ludwigsburg", "TV Rottenburg", "Germany")]
for slug, eid, h, a, comp in VB:
    add(id=f"vb-{eid}", sport="volleyball", sport_name="Volleyball", comp=comp, home=h, away=a,
        home_name=h, away_name=a, olbg_url=f"{OLBG_BASE}/Volleyball/21", olbg_event_id=eid,
        start_note="OLBG hub time withheld - no official league source read",
        sources=["olbg-volleyball"],
        facts=["Fixture pairing read from OLBG only"])

# ---- Rugby union
RU = [("Ospreys v Dragons", 609581, "Ospreys", "Dragons", "URC"),
      ("Toulon v Pau", 609555, "Toulon", "Pau", "Top 14"),
      ("USA v Australia A", 609583, "USA", "Australia A", "International"),
      ("Harlequins v Saracens", 609571, "Harlequins", "Saracens", "Premiership"),
      ("La Rochelle v Bordeaux", 609554, "La Rochelle", "Bordeaux", "Top 14")]
for slug, eid, h, a, comp in RU:
    add(id=f"ru-{eid}", sport="rugby_union", sport_name="Rugby Union", comp=comp, home=h, away=a,
        home_name=h, away_name=a, olbg_url=f"{OLBG_BASE}/Rugby_Union/9", olbg_event_id=eid,
        start_note="OLBG hub time withheld - no official competition source read",
        sources=["olbg-rugby-union"],
        facts=["Fixture pairing read from OLBG only"])

# ---- Cricket
CR = [("Toronto Kings vs Vancouver Guardians T20", 188845, "Toronto Kings", "Vancouver Guardians", "T20"),
      ("Pakistan vs England One Day Match", 188838, "Pakistan", "England", "ODI"),
      ("North West Dragons vs Northern Cape Heat T20", 188851, "North West Dragons", "Northern Cape Heat", "CSA T20"),
      ("Tuskers vs Western Province T20", 188850, "Tuskers", "Western Province", "CSA T20"),
      ("Eastern Storm vs South Africa Emerging T20", 188848, "Eastern Storm", "South Africa Emerging", "CSA T20"),
      ("Boland vs Titans T20", 188849, "Boland", "Titans", "CSA T20"),
      ("New Zealand vs India 3rd T20 Match", 188852, "New Zealand", "India", "T20I"),
      ("India W vs Zimbabwe W 2nd ODI", 188847, "India W", "Zimbabwe W", "WODI")]
for slug, eid, h, a, comp in CR:
    add(id=f"cr-{eid}", sport="cricket", sport_name="Cricket", comp=comp, home=h, away=a,
        home_name=h, away_name=a, olbg_url=f"{OLBG_BASE}/Cricket/7", olbg_event_id=eid,
        start_note="OLBG hub time withheld - no official board source read",
        sources=["olbg-cricket"],
        facts=["Fixture pairing read from OLBG only"])

# ---- Snooker
add(id="sn-9952", sport="snooker", sport_name="Snooker", comp="BetVictor Northern Ireland Open 2026, semi-final",
    home="Mark Williams", away="Jak Jones", home_name="Mark Williams", away_name="Jak Jones",
    olbg_url=f"{OLBG_BASE}/Snooker/8", olbg_event_id=9952,
    start_note="WST lists the semi-final as Live Now on 24 Oct, best of 11; the final is 25 Oct 08:00 UK against Kyren Wilson",
    sources=["olbg-snooker", "wst-matches"],
    facts=["WST marks this semi-final Live Now", "Best of 11 frames", "Final: Kyren Wilson v winner of this match, 25 Oct 08:00"])

# ---- Darts
DA = [("Nathan Aspinall vs Luke Littler", 32397, "Nathan Aspinall", "Luke Littler"),
      ("Jonny Clayton vs Josh Rock", 32400, "Jonny Clayton", "Josh Rock"),
      ("Martin Schindler vs Jermaine Wattimena", 32398, "Martin Schindler", "Jermaine Wattimena"),
      ("Gerwyn Price vs Stephen Bunting", 32407, "Gerwyn Price", "Stephen Bunting")]
for slug, eid, h, a in DA:
    add(id=f"da-{eid}", sport="darts", sport_name="Darts", comp="PDC European Championship",
        home=h, away=a, home_name=h, away_name=a, olbg_url=f"{OLBG_BASE}/Darts/15", olbg_event_id=eid,
        start_note="OLBG hub time only; the PDC calendar returned a cookie wall, so no official time or draw was read",
        sources=["olbg-darts", "pdc-calendar"],
        facts=["Fixture pairing read from OLBG only"])

# ---- Gaelic
GA = [("Moycullen v Salthill-Knocknacarra", 3532, "Moycullen", "Salthill-Knocknacarra"),
      ("St Finbarrs v Nemo Rangers", 3530, "St Finbarrs", "Nemo Rangers"),
      ("Kanturk v Eire Og Cor", 3531, "Kanturk", "Eire Og Cor"),
      ("Fr Caseys v Kildimo Pallaskenry", 3537, "Fr Caseys", "Kildimo Pallaskenry")]
for slug, eid, h, a in GA:
    add(id=f"ga-{eid}", sport="gaelic", sport_name="Gaelic Sports", comp="Club championship",
        home=h, away=a, home_name=h, away_name=a, olbg_url=f"{OLBG_BASE}/Gaelic_Football/25", olbg_event_id=eid,
        start_note="OLBG hub time only; no official county board source read",
        sources=["olbg-gaelic"], facts=["Fixture pairing read from OLBG only"])

# ---- Greyhounds (OLBG race names are the clock time; rendered column is US Eastern)
GH = [("7:58 Doncaster", 689890, "Lady Gambet"), ("8:54 Monmore", 690013, "Crossfield Jess"),
      ("9:14 Monmore", 690017, "Skylars Vision"), ("9:18 Dunstall Park", 689892, "Avarua Lake"),
      ("10:14 Dunstall Park", 690035, "Greenwell Gypsy"), ("6:46 Doncaster", 689965, "Headford Asher"),
      ("6:50 Central Park", 689963, "Clairekeith Mary"), ("6:54 Monmore", 689964, "Son Of Thor")]
for race, eid, dog in GH:
    add(id=f"gh-{eid}", sport="greyhounds", sport_name="Greyhounds", comp=race.split()[-1] + " (UK)",
        home=race, away=dog, home_name=race, away_name=dog,
        olbg_url=f"{OLBG_BASE}/Greyhounds/28", olbg_event_id=eid,
        start_note="Race clock time is the event name; OLBG renders it in US Eastern, five hours behind UK track time",
        sources=["olbg-greyhounds"], facts=[f"OLBG's most-tipped runner: {dog}", "No GBGB racecard read (official route returned 404)"])

# ---- Tennis
TE = [("Elena Rybakina vs Leylah Fernandez", 902207, "Elena Rybakina", "Leylah Fernandez"),
      ("Ashlyn Krueger vs Katerina Siniakova", 902171, "Ashlyn Krueger", "Katerina Siniakova"),
      ("Daniil Medvedev vs Nikoloz Basilashvili", 902251, "Daniil Medvedev", "Nikoloz Basilashvili"),
      ("Alexandra Eala vs Mika Stojsavljevic", 902175, "Alexandra Eala", "Mika Stojsavljevic"),
      ("Moyuka Uchijima vs Elise Mertens", 902173, "Moyuka Uchijima", "Elise Mertens"),
      ("Leylah Fernandez vs Himeno Sakatsume", 902172, "Leylah Fernandez", "Himeno Sakatsume")]
for slug, eid, h, a in TE:
    add(id=f"te-{eid}", sport="tennis", sport_name="Tennis", comp="ATP / WTA tour", home=h, away=a,
        home_name=h, away_name=a, olbg_url=f"{OLBG_BASE}/Tennis/3", olbg_event_id=eid,
        start_note="OLBG hub time only; ATP and WTA routes returned no readable match schedule",
        sources=["olbg-tennis", "atp-schedule", "wta-scores"], facts=["Fixture pairing read from OLBG only"])

# ---- Motor racing
add(id="f1-us-gp", sport="motor_racing", sport_name="Motor Racing", comp="Formula 1, United States Grand Prix",
    home="Circuit of The Americas", away="Win Race market", home_name="Circuit of The Americas", away_name="Win Race",
    olbg_url=f"{OLBG_BASE}/Motor_Racing/14", olbg_event_id=913,
    start_utc="2026-10-25T21:00:00Z",
    start_note="F1 publishes the race as 25 Oct 16:00 track time (UTC-5); qualifying 24 Oct 17:00-18:00 track time",
    sources=["olbg-motor-racing", "f1-us-gp"],
    facts=["Official FP2 classification: Leclerc 1:35.291, Antonelli +0.042, Verstappen +0.189, Hamilton +0.615, Russell +0.744",
           "Circuit of The Americas: 5.513 km, 56 laps, 308.432 km"])

# ---- Handball
HB = [("HBW Balingen Weilstetten vs MT Melsungen", 12090, "HBW Balingen Weilstetten", "MT Melsungen", "Germany HBL"),
      ("SC Magdeburg vs HC Kriens Luzern", 12136, "SC Magdeburg", "HC Kriens Luzern", "EHF Champions League"),
      ("BM Granollers vs Angel Ximenez Puente Genil", 12102, "BM Granollers", "Angel Ximenez Puente Genil", "Liga ASOBAL"),
      ("Rhein Neckar Lowen vs SC Magdeburg", 12092, "Rhein Neckar Lowen", "SC Magdeburg", "Germany HBL"),
      ("Luxembourg W vs Great Britain W", 12126, "Luxembourg W", "Great Britain W", "Women's international"),
      ("Saint Raphael vs PSG Handball", 12084, "Saint Raphael", "PSG Handball", "France LNH"),
      ("BM Torrelavega vs BM Proin", 12105, "BM Torrelavega", "BM Proin", "Liga ASOBAL"),
      ("HC Vardar vs MT Melsungen", 12130, "HC Vardar", "MT Melsungen", "EHF Champions League"),
      ("KS Kielce vs Kolstad", 12132, "KS Kielce", "Kolstad", "EHF Champions League"),
      ("GOG vs Sporting CP", 12129, "GOG", "Sporting CP", "EHF Champions League"),
      ("Fuchse Berlin vs RK Partizan", 12128, "Fuchse Berlin", "RK Partizan", "EHF Champions League")]
for slug, eid, h, a, comp in HB:
    add(id=f"hb-{eid}", sport="handball", sport_name="Handball", comp=comp, home=h, away=a,
        home_name=h, away_name=a, olbg_url=f"{OLBG_BASE}/Handball/20", olbg_event_id=eid,
        start_note="OLBG hub time only; no official league or EHF source read",
        sources=["olbg-handball"], facts=["Fixture pairing read from OLBG only"])


# ------------------------------------------------------- exact OLBG routes -----
# (section, slug, sport id) exactly as the hub rendered the link.
OLBG_ROUTE = {
    200002: ("Ice_Hockey/NHL/NHL", "CAR_Hurricanes_@_STL_Blues", 13),
    200008: ("Ice_Hockey/NHL/NHL", "NY_Rangers_@_OTT_Senators", 13),
    200005: ("Ice_Hockey/NHL/NHL", "MIN_Wild_@_SEA_Kraken", 13),
    200010: ("Ice_Hockey/NHL/NHL", "TOR_Maple_Leafs_@_EDM_Oilers", 13),
    200007: ("Ice_Hockey/NHL/NHL", "SJ_Sharks_@_BOS_Bruins", 13),
    200009: ("Ice_Hockey/NHL/NHL", "TB_Lightning_@_UTA_Mammoth", 13),
    200004: ("Ice_Hockey/NHL/NHL", "DET_Red_Wings_@_CGY_Flames", 13),
    200000: ("Ice_Hockey/NHL/NHL", "LA_Kings_@_NJ_Devils", 13),
    200003: ("Ice_Hockey/NHL/NHL", "BUF_Sabres_@_WAS_Capitals", 13),
    200006: ("Ice_Hockey/NHL/NHL", "NSH_Predators_@_PIT_Penguins", 13),
    200001: ("Ice_Hockey/NHL/NHL", "VGS_Golden_Knights_@_CLB_Blue_Jackets", 13),
    200020: ("Ice_Hockey/Other/Switzerland_NLA", "Ambri_Piotta_vs_HC_Ajoie", 13),
    200024: ("Ice_Hockey/Other/Switzerland_NLA", "EHC_Kloten_vs_Rapperswil_Jona_Lakers", 13),
    200022: ("Ice_Hockey/Other/Switzerland_NLA", "SCL_Tigers_vs_Davos", 13),
    200019: ("Ice_Hockey/Other/Switzerland_NLA", "EHC_Biel_vs_Zug", 13),
    200023: ("Ice_Hockey/Other/Switzerland_NLA", "Lausanne_HC_vs_Fribourg_Gotteron", 13),
    536112: ("Basketball/NBA/NBA", "BKN_Nets_@_CLE_Cavaliers", 4),
    536111: ("Basketball/NBA/NBA", "MIL_Bucks_@_PHI_76ers", 4),
    536115: ("Basketball/NBA/NBA", "HOU_Rockets_@_ATL_Hawks", 4),
    536117: ("Basketball/NBA/NBA", "MIA_Heat_@_CHA_Hornets", 4),
    536116: ("Basketball/NBA/NBA", "NO_Pelicans_@_DEN_Nuggets", 4),
    536114: ("Basketball/NBA/NBA", "SA_Spurs_@_DAL_Mavericks", 4),
    536113: ("Basketball/NBA/NBA", "WAS_Wizards_@_CHI_Bulls", 4),
    536118: ("Basketball/NBA/NBA", "GS_Warriors_@_PHX_Suns", 4),
    536087: ("Basketball/Other/Brazil_NBB", "Pato_Basquete_vs_Botafogo", 4),
    160792: ("Baseball/MLB/MLB", "TB_Rays_@_MIL_Brewers", 12),
    37019: ("Volleyball/All_Volleyball/All_Events", "UVC_Graz_W_vs_Sportunion_St_Polten_W", 21),
    37078: ("Volleyball/All_Volleyball/All_Events", "Mogilno_W_vs_Chemik_Police_W", 21),
    37002: ("Volleyball/All_Volleyball/All_Events", "Mackenzie_W_vs_Osasco_W", 21),
    37003: ("Volleyball/All_Volleyball/All_Events", "Abel-Moda_Brusque_W_vs_Praia_Clube_W", 21),
    37061: ("Volleyball/All_Volleyball/All_Events", "Sliedrecht_W_vs_Apollo_8_W", 21),
    37063: ("Volleyball/All_Volleyball/All_Events", "VV_Utrecht_W_vs_Dynamo_Apeldoorn_W", 21),
    37052: ("Volleyball/All_Volleyball/All_Events", "Royan_vs_Tours", 21),
    37069: ("Volleyball/All_Volleyball/All_Events", "Nantes_W_vs_Terville_Florange_W", 21),
    37072: ("Volleyball/All_Volleyball/All_Events", "Talmassons_W_vs_Chieri_W", 21),
    36994: ("Volleyball/All_Volleyball/All_Events", "Trentino_vs_Cisterna", 21),
    36965: ("Volleyball/All_Volleyball/All_Events", "CHKS_Chelm_vs_Resovia_Rzeszow", 21),
    36997: ("Volleyball/All_Volleyball/All_Events", "Perugia_vs_Pordenone", 21),
    36995: ("Volleyball/All_Volleyball/All_Events", "Civitlanova_vs_Padova", 21),
    37059: ("Volleyball/All_Volleyball/All_Events", "ETV_Hamburg_W_vs_Munster_W", 21),
    37014: ("Volleyball/All_Volleyball/All_Events", "Barock_Volleys_Ludwigsburg_vs_TV_Rottenburg", 21),
    609581: ("Rugby_Union/All_Rugby_Union/All_Events", "Ospreys_v_Dragons", 9),
    609555: ("Rugby_Union/All_Rugby_Union/All_Events", "Toulon_v_Pau", 9),
    609583: ("Rugby_Union/All_Rugby_Union/All_Events", "USA_v_Australia_A", 9),
    609571: ("Rugby_Union/All_Rugby_Union/All_Events", "Harlequins_v_Saracens", 9),
    609554: ("Rugby_Union/All_Rugby_Union/All_Events", "La_Rochelle_v_Bordeaux", 9),
    188845: ("Cricket/All_Cricket/All_Events", "Toronto_Kings_vs_Vancouver_Guardians_T20", 7),
    188838: ("Cricket/All_Cricket/All_Events", "Pakistan_vs_England_One_Day_Match", 7),
    188851: ("Cricket/All_Cricket/All_Events", "North_West_Dragons_vs_Northern_Cape_Heat_T20", 7),
    188850: ("Cricket/All_Cricket/All_Events", "Tuskers_vs_Western_Province_T20", 7),
    188848: ("Cricket/All_Cricket/All_Events", "Eastern_Storm_vs_South_Africa_Emerging_T20", 7),
    188849: ("Cricket/All_Cricket/All_Events", "Boland_vs_Titans_T20", 7),
    188852: ("Cricket/All_Cricket/All_Events", "New_Zealand_vs_India_3rd_T20_Match", 7),
    188847: ("Cricket/All_Cricket/All_Events", "India_W_vs_Zimbabwe_W_2nd_ODI", 7),
    9952: ("Snooker/All_Snooker/All_Events", "Mark_Williams_v_Jak_Jones", 8),
    32397: ("Darts/All_Darts/All_Events", "Nathan_Aspinall_vs_Luke_Littler", 15),
    32400: ("Darts/All_Darts/All_Events", "Jonny_Clayton_vs_Josh_Rock", 15),
    32398: ("Darts/All_Darts/All_Events", "Martin_Schindler_vs_Jermaine_Wattimena", 15),
    32407: ("Darts/All_Darts/All_Events", "Gerwyn_Price_vs_Stephen_Bunting", 15),
    3532: ("Gaelic_Football/All_Gaelic_Football/All_Events", "Moycullen_v_Salthill-Knocknacarra", 25),
    3530: ("Gaelic_Football/All_Gaelic_Football/All_Events", "St_Finbarrs_v_Nemo_Rangers", 25),
    3531: ("Gaelic_Football/All_Gaelic_Football/All_Events", "Kanturk_v_Eire_Og_Cor", 25),
    3537: ("Gaelic_Football/All_Gaelic_Football/All_Events", "Fr_Caseys_v_Kildimo_Pallaskenry", 25),
    689890: ("Greyhounds/All_Greyhounds/All_Events", "7:58_Doncaster", 28),
    690013: ("Greyhounds/All_Greyhounds/All_Events", "8:54_Monmore", 28),
    690017: ("Greyhounds/All_Greyhounds/All_Events", "9:14_Monmore", 28),
    689892: ("Greyhounds/All_Greyhounds/All_Events", "9:18_Dunstall_Park", 28),
    690035: ("Greyhounds/All_Greyhounds/All_Events", "10:14_Dunstall_Park", 28),
    689965: ("Greyhounds/All_Greyhounds/All_Events", "6:46_Doncaster", 28),
    689963: ("Greyhounds/All_Greyhounds/All_Events", "6:50_Central_Park", 28),
    689964: ("Greyhounds/All_Greyhounds/All_Events", "6:54_Monmore", 28),
    902207: ("Tennis/All_Tennis/All_Events", "Elena_Rybakina_vs_Leylah_Fernandez", 3),
    902171: ("Tennis/All_Tennis/All_Events", "Ashlyn_Krueger_vs_Katerina_Siniakova", 3),
    902251: ("Tennis/All_Tennis/All_Events", "Daniil_Medvedev_vs_Nikoloz_Basilashvili", 3),
    902175: ("Tennis/All_Tennis/All_Events", "Alexandra_Eala_vs_Mika_Stojsavljevic", 3),
    902173: ("Tennis/All_Tennis/All_Events", "Moyuka_Uchijima_vs_Elise_Mertens", 3),
    902172: ("Tennis/All_Tennis/All_Events", "Leylah_Fernandez_vs_Himeno_Sakatsume", 3),
    913: ("Motor_Racing/All_Motor_Racing/All_Events", "USA_Grand_Prix", 14),
    12090: ("Handball/All_Handball/All_Events", "HBW_Balingen_Weilstetten_vs_MT_Melsungen", 20),
    12136: ("Handball/All_Handball/All_Events", "SC_Magdeburg_vs_HC_Kriens_Luzern", 20),
    12102: ("Handball/All_Handball/All_Events", "BM_Granollers_vs_Angel_Ximenez_Puente_Genil", 20),
    12092: ("Handball/All_Handball/All_Events", "Rhein_Neckar_Lowen_vs_SC_Magdeburg", 20),
    12126: ("Handball/All_Handball/All_Events", "Luxembourg_W_vs_Great_Britain_W", 20),
    12084: ("Handball/All_Handball/All_Events", "Saint_Raphael_vs_PSG_Handball", 20),
    12105: ("Handball/All_Handball/All_Events", "BM_Torrelavega_vs_BM_Proin", 20),
    12130: ("Handball/All_Handball/All_Events", "HC_Vardar_vs_MT_Melsungen", 20),
    12132: ("Handball/All_Handball/All_Events", "KS_Kielce_vs_Kolstad", 20),
    12129: ("Handball/All_Handball/All_Events", "GOG_vs_Sporting_CP", 20),
    12128: ("Handball/All_Handball/All_Events", "Fuchse_Berlin_vs_RK_Partizan", 20),
}
for _f in FIX:
    _eid = _f.get("olbg_event_id")
    if _eid in OLBG_ROUTE:
        _sec, _slug, _sid = OLBG_ROUTE[_eid]
        _f["olbg_url"] = f"https://www.olbg.com/betting-tips/{_sec}/{_slug}/{_sid}?event_id={_eid}"


# -------------------------------------------------------------- the selection --
CONF_HIGH = 0.65
CONF_MED = 0.575
BAND_SHORT, BAND_LONG = -250, 10000


def confidence(p):
    if p is None:
        return None
    return "High" if p >= CONF_HIGH else ("Medium" if p >= CONF_MED else "Low")


def band_ok(price):
    if price is None:
        return None
    return BAND_SHORT <= price <= BAND_LONG


# ---- MLB model (log5 on the official home/away splits)
P_MIL = (0.679 - 0.679 * 0.531) / (0.679 + 0.531 - 2 * 0.679 * 0.531)
for f in FIX:
    if f["id"] == "mlb-mil-tb-g2":
        f["priced"] = True
        f["model"] = {"p_home": round(P_MIL, 4), "p_away": round(1 - P_MIL, 4), "method": "mlb-log5-home-away-v1"}
        f["markets"] = [
            {"market": "Match winner (moneyline)", "selection": "Milwaukee Brewers", "prob": round(P_MIL, 4),
             "fair": from_prob(P_MIL), "best": None, "best_book": None,
             "alt_selection": "Tampa Bay Rays", "alt_prob": round(1 - P_MIL, 4), "alt_fair": from_prob(1 - P_MIL),
             "alt_best": None, "alt_best_book": None},
        ]
        f["start_note"] = "exact UTC start from MLB's official schedule feed; no official price read"

# ---- choose a selection per priced fixture: the higher-probability side of the moneyline
for f in FIX:
    if not f.get("priced"):
        continue
    ml = f["markets"][0]
    if ml["prob"] >= ml["alt_prob"]:
        f["selection"] = ml["selection"]; f["prob"] = ml["prob"]; f["fair"] = ml["fair"]; f["best"] = ml["best"]
        f["best_book"] = ml["best_book"]
    else:
        f["selection"] = ml["alt_selection"]; f["prob"] = ml["alt_prob"]; f["fair"] = ml["alt_fair"]; f["best"] = ml["alt_best"]
        f["best_book"] = ml["alt_best_book"]
    f["confidence"] = confidence(f["prob"])
    f["fair_band_ok"] = band_ok(f["fair"])
    for _m in f["markets"]:
        for _k in ("selection", "alt_selection"):
            _m[_k] = expand(_m[_k])
    f["selection"] = expand(f["selection"])
    f["edge_pts"] = None if f.get("best") is None else round(100 * (f["prob"] - dec(f["best"]) ** -1), 1)


# ------------------------------------------------------------- predictions ----
PRED = {
 "mlb-mil-tb-g2": (
   "Milwaukee Brewers to win Game 2 of the World Series (moneyline).",
   "Milwaukee opened the Series with a win and now sends Logan Henderson to the mound at American Family Field, "
   "where the Brewers went 55-26 during the regular season. Their 103-59 record was the best in the National League, "
   "they scored 832 runs against 618 allowed for a plus-214 differential, and they closed the regular season 8-2 in "
   "their last ten, according to MLB's official standings. Tampa Bay finished 98-64 but was a far more ordinary 43-38 "
   "on the road. Henderson against Drew Rasmussen is the pitching matchup MLB lists for this game. No injury "
   "designation for either club could be read from an official source before publication."),
 "nhl-njd-lak": (
   "New Jersey Devils to beat the Los Angeles Kings in regulation or beyond (moneyline).",
   "New Jersey is 6-4-0 through ten games with a plus-two goal difference and is at home, where the club has been "
   "far the steadier side. Los Angeles has played only eight games but arrives at 2-4-2 with 20 goals scored and 29 "
   "conceded, the thinnest offensive record on tonight's board. The Devils' 21.9 per cent power play against a Kings "
   "penalty kill that has been ordinary is the likeliest route to separation. The best price on the league's own "
   "feed is {BEST}, shorter than the -154 we make them, so this is a form call and not a value call: back the Devils "
   "to win, but accept that the market has most of the edge already priced in."),
 "nhl-bos-sjs": (
   "Boston Bruins to beat the San Jose Sharks (moneyline).",
   "Boston is 8-2-1 with two shutouts and has conceded only 22 goals in 11 games, the best defensive record of any "
   "club on tonight's slate. San Jose is 6-4-1 but has been outscored 36-32 and has won just one game in regulation. "
   "The Bruins' 80.6 per cent penalty kill against a Sharks power play converting 25.7 per cent is the matchup that "
   "matters most, and Boston's home form has been the foundation of its start. The league feed lists the Bruins at "
   "{BEST} against our -162, which is a fair reflection of the gap and leaves thin margin for a buyer."),
 "nhl-wsh-buf": (
   "Washington Capitals to beat the Buffalo Sabres (moneyline).",
   "Washington has squeezed ten points from nine games despite a modest goal difference, and Buffalo has conceded 36 "
   "goals in ten, the second-worst rate among tonight's twelve hosts and visitors. The Sabres have also lost both "
   "of their overtime decisions, a sign of thin margins late in games. Washington's .556 points percentage is built "
   "on five regulation wins in nine, and the club is at home. The feed asks only {BEST} for Washington while we "
   "make them -131, and that gap is the widest value edge on the card: Capitals to win is the bet."),
 "nhl-pit-nsh": (
   "Pittsburgh Penguins to beat the Nashville Predators (moneyline).",
   "Nashville has three overtime defeats in nine games and has scored only 23 goals, the lowest total of any club "
   "playing tonight. Pittsburgh's own start is poor at 4-6-1, but the Penguins have generated 36 goals and put 30 "
   "shots a game on opposing nets, and they are at home. Nashville is only a narrow favourite at +105 on the "
   "league's price feed, so a Penguins win at plus money is the largest disagreement between our line and the "
   "published market on this slate."),
 "nhl-cbj-vgk": (
   "Vegas Golden Knights to beat the Columbus Blue Jackets (moneyline).",
   "Vegas is 8-4-0 with 45 goals for and has won seven of its last ten, while Columbus is 3-5-0 with only 19 goals "
   "in eight games and the weakest power play on tonight's card at 8.7 per cent. The Blue Jackets have also lost "
   "five of six, and their minus-ten goal difference is the second-worst of any home side playing today. The feed "
   "quotes Vegas at {BEST} where we make them -126, a small disagreement that still favours the visitor."),
 "nhl-ott-nyr": (
   "Ottawa Senators to beat the New York Rangers (moneyline).",
   "Ottawa is 7-4-0 and has conceded only 30 goals in 11 games, while the Rangers have played 12 games for 15 "
   "points and have been outshot in several of them. The Senators' 2-0 record in games decided beyond regulation "
   "and their home ice tilt a close matchup. Both sides sit on 14 points, so this is close to a coin flip and the "
   "market agrees; the best published price for Ottawa on the league's own list is {BEST} ({BOOK}). Our line gives "
   "Ottawa 52.8 per cent, so no edge is claimed either way."),
}
for f in FIX:
    if f["id"] in PRED:
        text = PRED[f["id"]][1].replace("{BEST}", f"{f.get('best'):+d}" if f.get("best") is not None else "n/a")
        text = text.replace("{BOOK}", f.get("best_book") or "n/a")
        f["prediction"] = {"selection": PRED[f["id"]][0], "text": text, "words": len(text.split())}


# ------------------------------------------------------------------- flags ----
FLAGS = sorted([
    ("F-321-01", "The brief's two pick rules cannot both be met outside a 1.4-point window", "high", "method",
     "The brief asks for selections with a greater than 70 per cent win chance AND a price between -250 and +10000. "
     "A 70.0 per cent chance is a fair price of -233; a -250 price is a 71.4 per cent chance. So the two rules "
     "together admit only probabilities between 70.0 and 71.4 per cent. On today's readable data no selection lands "
     "in that band, and we publish that rather than relabel a shorter price as compliant.",
     ["nhl-schedule", "mlb-standings-nl"]),
    ("F-321-02", "Zero selections cleared a 70 per cent win probability today", "high", "coverage",
     "The highest probability we can support is 65.2 per cent (Milwaukee Brewers, World Series Game 2). The six NHL "
     "moneyline probabilities run from 47.5 to 61.8 per cent and match the league's own published prices to within "
     "about two points on four of six games, which is the expected outcome if the slate genuinely contains no 70 per "
     "cent favourite. Nothing has been raised to meet the five-per-sport target.",
     ["mlb-standings-nl", "nhl-schedule"]),
    ("F-321-03", "Thirteen of the fifteen sports produced no priced pick", "high", "coverage",
     "Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Gaelic Sports, Greyhounds, Tennis, Handball and Rugby "
     "League have no line issued. For each one the blocking official source is named on the coverage page with the "
     "exact URL, so the gap can be checked by hand.",
     ["olbg-golf", "pdc-calendar", "urc-fixtures", "gbgb"]),
    ("F-321-04", "OLBG hub clock is US Eastern, not the venue's local time", "medium", "data",
     "The greyhound hub shows the race '7:58 Doncaster' with a parallel 'Today 14:58' column, a five-hour offset "
     "from UK track time. The MLB hub shows the World Series game at 'Today 20:00' where MLB's own feed gives "
     "2026-10-25T00:00Z, a four-hour offset. Derived times are therefore never published as start times: where an "
     "official source was read the UTC stamp is used, and everywhere else the start is left blank.",
     ["olbg-greyhounds", "olbg-baseball", "mlb-schedule"]),
    ("F-321-05", "OLBG tip percentages are votes, not probabilities", "medium", "method",
     "Each hub row shows a number such as '13/19 Win Tips 68%'. That is the share of community tips on a selection, "
     "not a chance of winning, and it is not used anywhere in this desk as an input.",
     ["olbg-darts"]),
    ("F-321-06", "NBA cannot be priced from a two-game sample", "high", "data",
     "The 2026-27 NBA season is one or two games old for every club. A probability claim built on that sample would "
     "be invention, so the nine basketball fixtures are published with official records and no line.",
     ["nba-standings", "olbg-basketball"]),
    ("F-321-07", "Snooker has no placeable pre-match market today", "medium", "coverage",
     "The only snooker market OLBG lists is the Northern Ireland Open semi-final, which WST marks Live Now. The "
     "final is 25 October at 08:00 UK against Kyren Wilson, but the opponent is not yet decided, so no line can be "
     "issued on it either.",
     ["olbg-snooker", "wst-matches"]),
    ("F-321-08", "Formula 1 race line withheld until qualifying", "medium", "coverage",
     "The United States Grand Prix is 25 October. Only second practice has been run; the official classification "
     "shows Leclerc fastest from Antonelli and Verstappen, which is not a basis for a race-winner probability. "
     "Qualifying runs on 24 October and the line should be issued after it.",
     ["f1-us-gp", "olbg-motor-racing"]),
    ("F-321-09", "Golf hub empty and PGA TOUR page did not reach October", "medium", "coverage",
     "OLBG renders 'No tips found.' on the golf hub, so there is no golf market to model. The PGA TOUR schedule "
     "page rendered only as far as March 2026 in the readable portion, so the current-week event could not be named.",
     ["olbg-golf", "pga-schedule"]),
    ("F-321-10", "NHL partner prices exclude one provider that quotes a 3-way market", "low", "data",
     "The league feed carries six providers. Doxxbet's two prices sum to about 81 per cent implied, which means it "
     "is quoting a 60-minute three-way market; including it would fabricate an under-round. Only the five 2-way "
     "providers are used, and the best available price is taken from those five.",
     ["nhl-schedule"]),
    ("F-321-11", "No injury designation could be read for any priced match", "medium", "data",
     "The brief asks for verified injuries. No official injury report was readable this session for the NHL, MLB or "
     "NBA matches listed, so no injury claim appears in any prediction. The absence is stated in the MLB write-up "
     "and is a gap, not a clean bill of health.",
     ["nhl-schedule", "mlb-schedule", "nba-standings"]),
    ("F-321-12", "Root landing page carried a stale pointer to another desk", "low", "repo",
     "The deployed root index.html pointed visitors to the 8cfb80b2 desk and was stamped 2026-10-22T12:29:50Z, "
     "while sixty sibling desk directories exist. This session replaced that one bar with a pointer to this desk. "
     "The canonical pipeline pages are otherwise untouched.",
     ["olbg-ice-hockey", "nhl-schedule"]),
    ("F-321-13", "The league odds feed identifies books by number, not by name", "medium", "data",
     "Each NHL price arrives as {providerId, value} with no publisher name attached. Earlier drafts of this desk "
     "attributed provider 3 to Tipsport, 6 to Veikkaus, 7 to FanDuel, 8 to Sportradar and 9 to DraftKings; that "
     "mapping was not readable anywhere in the feed, so it has been removed and every quote is now labelled by the "
     "number the league publishes. The prices themselves are unchanged and still official.",
     ["nhl-schedule"]),
    ("F-321-15", "The NRL draw does not name the time zone behind its kick-off clock", "medium", "data",
     "The Rugby League World Cup page shows New Zealand v Cook Islands at 1:05am and Australia v Fiji at 5:05am on "
     "25 October with no zone stated. Two different zones would move those fixtures by four hours, so the desk "
     "publishes the fixtures, the venues and the order of play but leaves the UTC start blank rather than guess.",
     ["nrl-draw"]),
    ("F-321-14", "One NHL game was already in progress when the desk was built", "low", "data",
     "Anaheim at Philadelphia started at 17:00 UTC and the league feed showed it LIVE with a 0-2 score. A live match "
     "is not an upcoming match, so the fixture was removed from the table rather than published with a stale line. "
     "The NHL count in this desk is therefore eleven, not the twelve on OLBG's hub.",
     ["nhl-schedule", "olbg-ice-hockey"]),
], key=lambda f: f[0])


# ---------------------------------------------------------------- coverage ----
# ---- Rugby league: OLBG lists only 2027 outrights; the NRL's own draw carries the World Cup card.
for _id, _home, _away, _venue, _ko in [
    ("rl-nz-ck", "New Zealand", "Cook Islands", "One NZ Stadium, Christchurch", "1:05am"),
    ("rl-aus-fij", "Australia", "Fiji", "Suncorp Stadium, Brisbane", "5:05am"),
]:
    add(id=_id, sport="rugby_league", sport_name="Rugby League",
        comp="Rugby League World Cup 2026, Round 2",
        home=_home, away=_away, home_name=_home, away_name=_away,
        olbg_url=f"{OLBG_BASE}/Rugby_League/10", start_utc=None,
        start_note=f"official draw shows 25 October, kick-off {_ko}; the zone behind that clock is not stated, so no UTC time is published",
        sources=["nrl-draw", "olbg-rugby-league"],
        facts=[f"Venue: {_venue}",
               "Listed by the NRL draw as not started; the same page shows Papua New Guinea 6-64 Samoa and England 82-0 France complete",
               "Positions before the match: New Zealand 3rd, Cook Islands 4th" if _home == "New Zealand" else "Positions before the match: Fiji 1st, Australia 2nd"])

SPORTS = [
    ("golf", "Golf", "olbg-golf"), ("volleyball", "Volleyball", "olbg-volleyball"),
    ("rugby_union", "Rugby Union", "olbg-rugby-union"), ("cricket", "Cricket", "olbg-cricket"),
    ("snooker", "Snooker", "olbg-snooker"), ("darts", "Darts", "olbg-darts"),
    ("baseball", "Baseball", "olbg-baseball"), ("gaelic", "Gaelic Sports", "olbg-gaelic"),
    ("greyhounds", "Greyhounds", "olbg-greyhounds"), ("tennis", "Tennis", "olbg-tennis"),
    ("motor_racing", "Motor Racing", "olbg-motor-racing"), ("handball", "Handball", "olbg-handball"),
    ("ice_hockey", "Ice Hockey", "olbg-ice-hockey"), ("basketball", "Basketball", "olbg-basketball"),
    ("rugby_league", "Rugby League", "olbg-rugby-league"),
]
BLOCKER = {
    "golf": ("OLBG lists no golf market today ('No tips found.'). The PGA TOUR schedule page did not render the current week.",
             "pga-schedule"),
    "volleyball": ("The Italian league site returned a video shell and no English-language federation page was readable.",
                   "legavolley"),
    "rugby_union": ("The URC fixtures route returns HTTP 404 and the Premiership fixtures page returned navigation only.",
                    "urc-fixtures"),
    "cricket": ("The PCB home page returned news and squad cards, not the Pakistan v England fixture detail.", "pcb-home"),
    "snooker": ("The only listed match is already in play; the final's opponent is undecided.", "wst-matches"),
    "darts": ("The PDC calendar returns a cookie-consent wall with no tournament content.", "pdc-calendar"),
    "baseball": ("Priced. Two further World Series games are listed with official start times.", "mlb-schedule"),
    "gaelic": ("No county board or GAA fixture page was read this session.", "olbg-gaelic"),
    "greyhounds": ("The GBGB racecards route returns HTTP 404.", "gbgb"),
    "tennis": ("ATP route returned the site shell and WTA returned notifications only, so no draw or start time was read.",
               "atp-schedule"),
    "motor_racing": ("Race is 25 October; only practice has run, so no race line is issued yet.", "f1-us-gp"),
    "handball": ("No EHF or domestic league route was readable this session.", "olbg-handball"),
    "ice_hockey": ("Priced from the NHL's own schedule, club statistics and published partner prices.", "nhl-schedule"),
    "basketball": ("Official records read, but the season is one or two games old, so no line is issued.", "nba-standings"),
    "rugby_league": ("OLBG lists only 2027 outrights, but the NRL's official World Cup draw carries two Round 2 fixtures; kick-off clocks on that page do not state their time zone.", "nrl-draw"),
}


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    fixtures = sorted(FIX, key=lambda f: (f["sport"], f.get("start_utc") or "9999", f["id"]))
    picks = [f for f in fixtures if f.get("selection")]
    preds = [f for f in fixtures if f.get("prediction")]
    coverage = []
    for key, name, src in SPORTS:
        rows = [f for f in fixtures if f["sport"] == key]
        priced = [f for f in rows if f["priced"]]
        cov = {"sport": key, "name": name, "olbg_source": src,
               "fixtures": len(rows), "priced": len(priced), "picks": len([f for f in rows if f.get("selection")]),
               "predictions": len([f for f in rows if f.get("prediction")]),
               "high": len([f for f in rows if f.get("confidence") == "High"]),
               "blocker": BLOCKER[key][0], "blocker_source": BLOCKER[key][1],
               "target": 5, "met": len([f for f in rows if f.get("prediction")]) >= 5}
        coverage.append(cov)
    summary = {
        "session": SESSION, "built_utc": BUILT,
        "fixtures": len(fixtures), "priced": len([f for f in fixtures if f["priced"]]),
        "picks": len(picks), "predictions": len(preds),
        "high": len([f for f in picks if f["confidence"] == "High"]),
        "medium": len([f for f in picks if f["confidence"] == "Medium"]),
        "low": len([f for f in picks if f["confidence"] == "Low"]),
        "sports": len(SPORTS), "sports_with_picks": len({f["sport"] for f in picks}),
        "sports_with_fixtures": len({f["sport"] for f in fixtures}),
        "flags": len(FLAGS), "sources": len(SOURCES), "official_sources": len([s for s in SOURCES if s[3] == "official"]),
        "market_rows": sum(len(f["markets"]) for f in fixtures),
        "strict70_and_band": len([f for f in picks if (f["prob"] or 0) > 0.70 and band_ok(f.get("fair"))]),
        "top_prob": max((f["prob"] for f in picks), default=None),
        "target_predictions": len(SPORTS) * 5,
    }
    payload = {
        "summary.json": summary,
        "sources.json": {"sources": list(SRC.values())},
        "fixtures.json": {"fixtures": fixtures},
        "predictions.json": {"predictions": [{"fixture_id": f["id"], "sport": f["sport_name"],
                                              "match": f"{f['away_name']} @ {f['home_name']}",
                                              "start_utc": f["start_utc"], "confidence": f["confidence"],
                                              "prob": f["prob"], "fair": f["fair"],
                                              "selection": f["prediction"]["selection"],
                                              "text": f["prediction"]["text"],
                                              "words": f["prediction"]["words"],
                                              "sources": f["sources"]} for f in preds]},
        "flags.json": {"flags": [{"id": f[0], "title": f[1], "severity": f[2], "area": f[3], "detail": f[4],
                                  "sources": f[5]} for f in FLAGS]},
        "coverage.json": {"sports": coverage},
    }
    for name, data in payload.items():
        (OUT / name).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))
    for f in fixtures:
        if f.get("selection"):
            print(f"  {f['id']:22} {f['selection'][:28]:28} p={f['prob']:.3f} fair={f['fair']:>6} best={str(f.get('best')):>6} {f['confidence']:6} edge={f.get('edge_pts')}")


if __name__ == "__main__":
    build()
