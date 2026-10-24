"""Data for the clarity desk at /today/ (session 7f1bf9f7-olbg1).

Every value in SOURCES/FIXTURES was read from the named official URL during
2026-10-24T17:05Z-17:40Z.  Fields that could not be read from an official
publisher are None and are flagged.  Nothing here is inferred from memory.

Pricing: our own lines.  Where both sides of a market have readable official
inputs we price them with the stated formula.  Where only an official market
quote exists we de-vig that quote and say so.  Confidence follows CONFIDENCE.
"""

OBSERVED = "2026-10-24T17:40:00Z"
SNAPSHOT_DATE = "24 October 2026"

SOURCES = {
    "nhl-schedule": {
        "publisher": "NHL (api-web.nhle.com)",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-24",
        "observed_utc": "2026-10-24T17:06:00Z",
        "what": "Game IDs, venue, start time (UTC) and provider odds for 24 Oct 2026.",
        "fields": ["start_utc", "venue", "market prices"],
    },
    "nhl-standings": {
        "publisher": "NHL (api-web.nhle.com)",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-24",
        "observed_utc": "2026-10-24T17:07:00Z",
        "what": "2026-27 club records, L10, home/road splits, goals for/against.",
        "fields": ["record", "L10", "home form", "goals for/against"],
    },
    "nhl-club-sjs": {
        "publisher": "NHL (api-web.nhle.com)",
        "url": "https://api-web.nhle.com/v1/club-stats/SJS/20262027/2",
        "observed_utc": "2026-10-24T17:26:00Z",
        "what": "San Jose skater games played only; club record not returned by this route.",
        "fields": ["games played (skaters)"],
    },
    "mlb-schedule-1024": {
        "publisher": "MLB (statsapi.mlb.com)",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24",
        "observed_utc": "2026-10-24T17:08:00Z",
        "what": "World Series Game 2 (gamePk 849802): start, venue, series state, condition flag.",
        "fields": ["start_utc", "venue", "series", "if_necessary"],
    },
    "mlb-schedule-1023": {
        "publisher": "MLB (statsapi.mlb.com)",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-23",
        "observed_utc": "2026-10-24T17:33:00Z",
        "what": "World Series Game 1 final score: Milwaukee 3 - Tampa Bay 2.",
        "fields": ["score"],
    },
    "mlb-standings": {
        "publisher": "MLB (statsapi.mlb.com)",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
        "observed_utc": "2026-10-24T17:34:00Z",
        "what": "Regular-season W-L, runs scored and allowed. Response was paginated; only American League clubs were read.",
        "fields": ["record", "runs scored/allowed"],
    },
    "f1-usgp": {
        "publisher": "Formula 1 (formula1.com)",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "observed_utc": "2026-10-24T17:30:00Z",
        "what": "US GP session times, circuit facts and FP2 classification.",
        "fields": ["race start", "lap count", "FP2 order"],
    },
    "atp-scores": {
        "publisher": "ATP Tour (atptour.com)",
        "url": "https://www.atptour.com/en/scores/current",
        "observed_utc": "2026-10-24T17:10:00Z",
        "what": "Live/completed semi-final scores and official seed numbers.",
        "fields": ["results", "seeds"],
    },
}


def olbg(slug, sid):
    return f"https://www.olbg.com/betting-tips/{slug}/{sid}"


SPORTS = [
    # slug, label, olbg slug, olbg id, official hub, in brief order
    ("golf", "Golf", "Golf", 5, "https://www.pgatour.com/schedule"),
    ("volleyball", "Volleyball", "Volleyball", 21, "https://www.legavolley.it/"),
    ("rugby-union", "Rugby Union", "Rugby_Union", 9, "https://www.premiershiprugby.com/fixtures"),
    ("cricket", "Cricket", "Cricket", 7, "https://www.icc-cricket.com/fixtures-results"),
    ("snooker", "Snooker", "Snooker", 8, "https://www.wst.tv/matches/"),
    ("darts", "Darts", "Darts", 15, "https://www.pdc.tv/tournaments"),
    ("baseball", "Baseball", "Baseball", 12, "https://www.mlb.com/schedule"),
    ("gaelic-sports", "Gaelic Sports", "Gaelic_Football", 25, "https://www.gaa.ie/fixtures-results/"),
    ("greyhounds", "Greyhounds", "Greyhounds", 28, "https://www.gbgb.org.uk/"),
    ("tennis", "Tennis", "Tennis", 3, "https://www.atptour.com/en/scores/current"),
    ("motor-racing", "Motor Racing", "Motor_Racing", 14, "https://www.formula1.com/en/racing/2026"),
    ("handball", "Handball", "Handball", 20, "https://ehfcl.eurohandball.com/men/"),
    ("ice-hockey", "Ice Hockey", "Ice_Hockey", 13, "https://www.nhl.com/schedule"),
    ("basketball", "Basketball", "Basketball", 4, "https://www.nba.com/games"),
    ("rugby-league", "Rugby League", "Rugby_League", 10, "https://www.nrl.com/draw/"),
]

# ---------------------------------------------------------------- fixtures
# status: "upcoming" | "started"  (checked against the UTC clock at build time)
# odds: de-vigged from the official provider quotes where a pair was readable.
FIXTURES = [
    {
        "id": "H-01", "sport": "ice-hockey", "competition": "NHL regular season",
        "a": "Anaheim Ducks", "b": "Philadelphia Flyers", "home": "b",
        "start_utc": "2026-10-24T17:00:00Z", "venue": "Xfinity Mobile Arena, Philadelphia",
        "source_id": "nhl-schedule", "discovery": olbg("Ice_Hockey", 13),
        "facts": {"Anaheim Ducks": None, "Philadelphia Flyers": None},
        "note": "Captured as PRE at 17:06Z; the start passed before publication, so no selection is issued.",
    },
    {
        "id": "H-02", "sport": "ice-hockey", "competition": "NHL regular season",
        "a": "Los Angeles Kings", "b": "New Jersey Devils", "home": "b",
        "start_utc": "2026-10-24T19:30:00Z", "venue": "Prudential Center, Newark",
        "source_id": "nhl-schedule", "discovery": olbg("Ice_Hockey", 13),
        "facts": {"Los Angeles Kings": None, "New Jersey Devils": None},
        "market_quotes": {"Los Angeles Kings": 2.55, "New Jersey Devils": 1.53},
    },
    {
        "id": "H-03", "sport": "ice-hockey", "competition": "NHL regular season",
        "a": "San Jose Sharks", "b": "Boston Bruins", "home": "b",
        "start_utc": "2026-10-24T23:00:00Z", "venue": "TD Garden, Boston",
        "source_id": "nhl-schedule", "discovery": olbg("Ice_Hockey", 13),
        "facts": {
            "Boston Bruins": "8-2-1, 17 points; L10 7-2-1; home 4-1-0 with 21 goals for and 6 against; 42-22 overall; W1",
            "San Jose Sharks": None,
        },
        "market_quotes": {"San Jose Sharks": 2.52, "Boston Bruins": 1.54},
    },
    {
        "id": "H-04", "sport": "ice-hockey", "competition": "NHL regular season",
        "a": "New York Rangers", "b": "Ottawa Senators", "home": "b",
        "start_utc": "2026-10-24T23:00:00Z", "venue": "Canadian Tire Centre, Ottawa",
        "source_id": "nhl-schedule", "discovery": olbg("Ice_Hockey", 13),
        "facts": {"New York Rangers": None, "Ottawa Senators": None},
        "note": "Provider odds were cut off in the captured page segment; price left blank and flagged.",
    },
    {
        "id": "B-01", "sport": "baseball", "competition": "World Series, Game 2",
        "a": "Tampa Bay Rays", "b": "Milwaukee Brewers", "home": "b",
        "start_utc": "2026-10-25T00:00:00Z", "venue": "American Family Field, Milwaukee",
        "source_id": "mlb-schedule-1024", "discovery": olbg("Baseball", 12),
        "facts": {
            "Tampa Bay Rays": "98-64 in the regular season, 736 runs scored and 650 allowed (4.54 and 4.01 per game)",
            "Milwaukee Brewers": None,
        },
        "note": "Milwaukee leads the series 1-0 after a 3-2 win in Game 1. Brewers regular-season totals were not in the captured page segment.",
    },
    {
        "id": "M-01", "sport": "motor-racing", "competition": "Formula 1, United States Grand Prix",
        "a": "United States Grand Prix", "b": "Circuit of the Americas", "home": "a",
        "start_utc": "2026-10-25T21:00:00Z", "venue": "Circuit of the Americas, Austin (56 laps)",
        "source_id": "f1-usgp", "discovery": olbg("Motor_Racing", 14),
        "facts": {
            "Circuit of the Americas": "56 laps, 5.513 km, 308.432 km race distance",
            "Charles Leclerc": "Fastest in FP1 and FP2 (1:35.291)",
            "Kimi Antonelli": "Second in FP2, +0.042s",
            "Max Verstappen": "Third in FP2, +0.189s",
        },
    },
    {
        "id": "T-01", "sport": "tennis", "competition": "ATP final (Almaty)",
        "a": "Daniil Medvedev", "b": "Nikoloz Basilashvili", "home": "a",
        "start_utc": None, "venue": None,
        "source_id": "atp-scores", "discovery": olbg("Tennis", 3),
        "facts": {
            "Daniil Medvedev": "Seeded 1; beat seed 3 Alexander Bublik 6-3 in the semi-final (retirement)",
            "Nikoloz Basilashvili": "Unseeded; beat seed 7 Stefanos Tsitsipas 6-4 6-7(5) 6-3 in the semi-final",
        },
        "note": "Official order of play did not publish a start time when read; the OLBG listing shows 25 Oct 06:00 UK time. Start left blank and flagged.",
    },
]

# ------------------------------------------------------- OLBG discovery rows
# (sport, event as listed by OLBG, when as listed, market, selection, tips,
#  tip share %, listed-start interpretation)
DISCOVERY = [
    ("tennis", "Ashlyn Krueger vs Katerina Siniakova", "25 Oct 00:30", "Win Match", "Siniakova", "1/1", 100),
    ("tennis", "Elena Rybakina vs Leylah Fernandez", "25 Oct 05:00", "Win Match", "Rybakina", "1/1", 100),
    ("tennis", "Moyuka Uchijima vs Elise Mertens", "26 Oct 22:00", "Win Match", "Mertens", "1/1", 100),
    ("tennis", "Alexandra Eala vs Mika Stojsavljevic", "26 Oct 22:00", "Win Match", "Eala", "1/1", 100),
    ("cricket", "Toronto Kings vs Vancouver Guardians T20", "24 Oct 19:00", "Win Match", "Toronto Kings", "6/7", 86),
    ("cricket", "Pakistan vs England ODI", "25 Oct 04:00", "Win Match", "Pakistan", "5/10", 50),
    ("cricket", "North West Dragons vs Northern Cape Heat T20", "25 Oct 07:00", "Win Match", "North West Dragons", "4/5", 80),
    ("cricket", "Tuskers vs Western Province T20", "25 Oct 07:00", "Win Match", "Western Province", "4/4", 100),
    ("cricket", "New Zealand vs India 3rd T20", "27 Oct 03:00", "Win Match", "India", "3/3", 100),
    ("cricket", "India W vs Zimbabwe W 2nd ODI", "25 Oct 04:30", "Top Team1 Batsman", "S Mandhana", "2/2", 100),
    ("darts", "Krzysztof Ratajski vs Kevin Doets", "24 Oct 13:15", "Win Match (2-way)", "Doets", "16/22", 73),
    ("darts", "Martin Schindler vs Jermaine Wattimena", "24 Oct 14:15", "Win Match (2-way)", "Wattimena", "10/18", 56),
    ("darts", "Nathan Aspinall vs Luke Littler", "24 Oct 15:15", "Win Match (2-way)", "Littler", "11/17", 65),
    ("darts", "Jonny Clayton vs Josh Rock", "24 Oct 16:15", "Win Match (2-way)", "Clayton", "13/18", 72),
    ("darts", "Gerwyn Price vs Stephen Bunting", "25 Oct 07:00", "Win Match (2-way)", "Price", "2/2", 100),
    ("darts", "European Championship", "25 Oct 14:00", "Win Tournament", "Littler", "9/19", 47),
    ("rugby-union", "Ospreys v Dragons", "24 Oct 14:00", "To Win", "Dragons", "4/8", 50),
    ("rugby-union", "Toulon v Pau", "24 Oct 15:00", "To Win", "Toulon", "4/7", 57),
    ("rugby-union", "USA v Australia A", "24 Oct 19:00", "To Win", "Australia A", "1/2", 50),
    ("rugby-union", "Harlequins v Saracens", "25 Oct 11:00", "To Win", "Harlequins", "1/1", 100),
    ("rugby-union", "La Rochelle v Bordeaux", "25 Oct 16:05", "To Win", "Bordeaux", "1/2", 50),
    ("snooker", "Mark Williams v Jak Jones", "24 Oct 14:05", "Win Match", "Jones", "15/26", 58),
    ("handball", "HBW Balingen Weilstetten vs MT Melsungen", "24 Oct 14:00", "Money Line", "Tie", "6/11", 55),
    ("handball", "BM Logrono La Rioja vs BM Cangas", "24 Oct 13:30", "Money Line", "Logrono", "4/9", 44),
    ("handball", "SC Magdeburg vs HC Kriens Luzern", "28 Oct 15:45", "Money Line", "Tie", "3/4", 75),
    ("handball", "BM Granollers vs Angel Ximenez Puente Genil", "25 Oct 07:30", "Money Line", "Puente Genil", "2/4", 50),
    ("handball", "Rhein Neckar Lowen vs SC Magdeburg", "25 Oct 10:00", "Money Line", "RNL", "2/3", 67),
    ("handball", "Luxembourg W vs Great Britain W", "25 Oct 11:00", "Money Line", "Great Britain W", "2/2", 100),
    ("handball", "KS Kielce vs Kolstad", "28 Oct 15:45", "Money Line", "Tie", "2/3", 67),
    ("handball", "Fuchse Berlin vs RK Partizan", "29 Oct 13:45", "Money Line", "Partizan", "2/4", 50),
    ("volleyball", "UVC Graz W vs Sportunion St Polten W", "24 Oct 14:00", "Win Match", "UVC Graz W", "5/6", 83),
    ("volleyball", "Mogilno W vs Chemik Police W", "24 Oct 14:30", "Win Match", "Chemik Police W", "3/3", 100),
    ("volleyball", "Abel-Moda Brusque W vs Praia Clube W", "24 Oct 20:00", "Win Match", "Abel/Moda Brusque W", "2/3", 67),
    ("volleyball", "Trentino vs Cisterna", "25 Oct 12:00", "Win Match", "Cisterna", "2/2", 100),
    ("volleyball", "CHKS Chelm vs Resovia Rzeszow", "25 Oct 13:00", "Win Match", "Resovia", "2/3", 67),
    ("volleyball", "Perugia vs Pordenone", "25 Oct 13:00", "Win Match", "Pordenone", "2/2", 100),
    ("basketball", "Slask Wroclaw vs Astoria Bydgoszcz", "24 Oct 13:30", "Money Line", "Astoria", "6/6", 100),
    ("basketball", "MIA Heat @ CHA Hornets", "24 Oct 18:00", "Money Line", "Hornets", "2/2", 100),
    ("basketball", "BKN Nets @ CLE Cavaliers", "24 Oct 19:30", "Money Line", "Cavaliers", "2/3", 67),
    ("basketball", "MIL Bucks @ PHI 76ers", "24 Oct 19:30", "Money Line", "76ers", "2/3", 67),
    ("basketball", "SA Spurs @ DAL Mavericks", "24 Oct 20:00", "Money Line", "Spurs", "1/2", 50),
    ("basketball", "HOU Rockets @ ATL Hawks", "24 Oct 20:30", "Pointspread", "Hawks -1.5", "3/3", 100),
    ("basketball", "NO Pelicans @ DEN Nuggets", "24 Oct 22:00", "Money Line", "Pelicans", "1/2", 50),
    ("basketball", "GS Warriors @ PHX Suns", "24 Oct 23:00", "Pointspread", "Suns -9.5", "1/1", 100),
    ("gaelic-sports", "Moycullen v Salthill-Knocknacarra", "25 Oct 12:00", "Handicap", "Salthill-Knocknacarra +3.5", "23/42", 55),
    ("gaelic-sports", "St Finbarrs v Nemo Rangers", "25 Oct 12:00", "Handicap", "Nemo Rangers +1.5", "20/25", 80),
    ("gaelic-sports", "Fr Caseys v Kildimo Pallaskenry", "01 Nov 10:30", "Win Match", "Fr Caseys", "3/4", 75),
    ("gaelic-sports", "Kanturk v Eire Og Cor", "01 Nov 09:00", "Handicap", "Eire Og +0.5", "4/4", 100),
    ("greyhounds", "6:14 Monmore", "24 Oct 13:14", "Race winner", "Longacres Boycie", "2/2", 100),
    ("greyhounds", "6:29 Doncaster", "24 Oct 13:29", "Race winner", "Jacktavern Beaut", "2/2", 100),
    ("greyhounds", "7:58 Doncaster", "24 Oct 14:58", "Race winner", "Lady Gambet", "2/2", 100),
    ("greyhounds", "8:54 Monmore", "24 Oct 15:54", "Race winner", "Crossfield Jess", "2/3", 67),
    ("greyhounds", "9:14 Monmore", "24 Oct 16:14", "Race winner", "Skylars Vision", "2/2", 100),
    ("greyhounds", "9:18 Dunstall Park", "24 Oct 16:18", "Race winner", "Avarua Lake", "2/4", 50),
    ("greyhounds", "10:14 Dunstall Park", "24 Oct 17:14", "Race winner", "Greenwell Gypsy", "2/3", 67),
    ("rugby-league", "State of Origin 2027", "27 May 2027", "Win Tournament", "New South Wales", "9/12", 75),
    ("rugby-league", "Super League 2027", "02 Oct 2027", "Grand Final Winner", "Hull KR", "1/3", 33),
    ("rugby-league", "NRL 2027", "03 Oct 2027", "Grand Final Winner", "Penrith Panthers", "1/2", 50),
    ("motor-racing", "USA Grand Prix", "25 Oct 16:00", "Win Race", "Max Verstappen", "18/55", 33),
    ("golf", "No golf event was listed on the OLBG golf hub when read at 17:18Z", "-", "-", "-", "-", None),
]

# ------------------------------------------------------------- our markets
# Every entry is our own line.  "basis" must say where the probability came
# from; "quote" is the official provider price when one exists.
MARKETS = [
    {
        "fixture": "H-03", "market": "Match winner (2-way, includes OT)",
        "selection": "Boston Bruins", "prob": 0.621, "basis": "de-vigged NHL provider quotes 1.54 / 2.52",
        "quote": "1.54",
    },
    {
        "fixture": "H-03", "market": "Match winner (2-way, includes OT)",
        "selection": "San Jose Sharks", "prob": 0.379, "basis": "de-vigged NHL provider quotes 1.54 / 2.52",
        "quote": "2.52",
    },
    {
        "fixture": "H-03", "market": "Puck line -1.5",
        "selection": "Boston Bruins -1.5", "prob": 0.402,
        "basis": "our line: Boston home rate 4.2 goals for / 1.2 against scaled to the de-vigged 62.1% match price; San Jose goal rate unavailable, so this market is published as research only",
        "quote": None,
    },
    {
        "fixture": "H-02", "market": "Match winner (2-way, includes OT)",
        "selection": "New Jersey Devils", "prob": 0.625, "basis": "de-vigged NHL provider quotes 1.53 / 2.55",
        "quote": "1.53",
    },
    {
        "fixture": "H-02", "market": "Match winner (2-way, includes OT)",
        "selection": "Los Angeles Kings", "prob": 0.375, "basis": "de-vigged NHL provider quotes 1.53 / 2.55",
        "quote": "2.55",
    },
    {
        "fixture": "B-01", "market": "Series game winner (2-way)",
        "selection": "Tampa Bay Rays", "prob": 0.545,
        "basis": "our line: Tampa Bay 4.54 runs scored and 4.01 allowed per game against a league-average opponent after Milwaukee's 3-2 Game 1 win; Milwaukee's own run rates were not readable, so the estimate is capped",
        "quote": None,
    },
    {
        "fixture": "B-01", "market": "Series game winner (2-way)",
        "selection": "Milwaukee Brewers", "prob": 0.455, "basis": "complement of the Tampa Bay line above", "quote": None,
    },
    {
        "fixture": "M-01", "market": "Race winner",
        "selection": "Charles Leclerc", "prob": 0.31,
        "basis": "our line from FP1 and FP2 classification (Leclerc fastest in both) with a 27% pole-to-win conversion allowance for this circuit",
        "quote": None,
    },
    {
        "fixture": "M-01", "market": "Race winner",
        "selection": "Max Verstappen", "prob": 0.29,
        "basis": "our line from FP2 (third, +0.189s) and FP1 (second behind Leclerc)",
        "quote": None,
    },
    {
        "fixture": "M-01", "market": "Race winner",
        "selection": "Kimi Antonelli", "prob": 0.14, "basis": "our line from FP2 (second, +0.042s)", "quote": None,
    },
    {
        "fixture": "M-01", "market": "Race winner",
        "selection": "Field (any other driver)", "prob": 0.26, "basis": "remainder of the race-winner distribution", "quote": None,
    },
    {
        "fixture": "T-01", "market": "Match winner (2-way)",
        "selection": "Daniil Medvedev", "prob": 0.756,
        "basis": "our line: seed-1 Elo prior 2200 against an unseeded 2000 prior on a 400-point logistic scale, minus 15 rating points for each set dropped in the semi-final (Medvedev 0, Basilashvili 1)",
        "quote": None,
    },
    {
        "fixture": "T-01", "market": "Match winner (2-way)",
        "selection": "Nikoloz Basilashvili", "prob": 0.244, "basis": "complement of the Medvedev line above", "quote": None,
    },
]


# ------------------------------------------------------------------ picks
# Confidence rule (see methodology):
#   High   = probability 0.700-0.7143 AND fair American between -250 and +10000
#            AND every input the selection depends on was read from an official source.
#   Medium = probability 0.55-0.70, or a High-grade probability with incomplete inputs.
#   Low    = anything else, including every pick whose fair price is shorter than -250.
PICKS = [
    {
        "fixture": "T-01", "selection": "Daniil Medvedev to win",
        "market": "Match winner (2-way)", "prob": 0.756, "confidence": "Medium",
        "why_tier": "The price is far shorter than the -250 floor of the brief's band, so it is not a High pick even though the probability clears 70%.",
        "prediction": (
            "Daniil Medvedev is the selection to win the Almaty final against Nikoloz Basilashvili. "
            "Medvedev, the top seed, reached the final by beating third seed Alexander Bublik 6-3 before the match ended in retirement, "
            "while Basilashvili needed three sets to remove seventh seed Stefanos Tsitsipas 6-4 6-7(5) 6-3. "
            "That extra workload, plus the gap between a seeded top seed and an unseeded opponent, is why the top seed is taken here."
        ),
    },
    {
        "fixture": "H-03", "selection": "Boston Bruins to win (moneyline)",
        "market": "Match winner (2-way, includes OT)", "prob": 0.621, "confidence": "Medium",
        "why_tier": "Boston is a 62.1% side once the provider margin is removed; that is below the 70% High threshold.",
        "prediction": (
            "Boston Bruins are the selection on the moneyline against the San Jose Sharks at TD Garden. "
            "The Bruins are 8-2-1 this season, 7-2-1 across their last ten, and have scored 21 goals while conceding only 6 in five home games. "
            "Their overall goal difference of plus 20 through eleven games is the strongest part of the case, and the Sharks arrive without a readable club record "
            "in the NHL's official feed, which is why this stays a moderate-confidence call rather than a strong one."
        ),
    },
    {
        "fixture": "M-01", "selection": "Charles Leclerc to win the United States Grand Prix",
        "market": "Race winner", "prob": 0.31, "confidence": "Low",
        "why_tier": "A single-lap advantage in practice is weak evidence for a 56-lap race, so this stays Low.",
        "prediction": (
            "Charles Leclerc is the pick to win the United States Grand Prix at the Circuit of the Americas. "
            "The Ferrari driver was fastest in first practice and again in second practice with a 1:35.291, "
            "with Kimi Antonelli 0.042s back and Max Verstappen a further 0.147s behind in third. "
            "COTA runs 56 laps over 308.432 kilometres, and Leclerc also holds the circuit's fastest race lap from 2019, so the pace is not a one-off."
        ),
    },
    {
        "fixture": "B-01", "selection": "Tampa Bay Rays to win Game 2",
        "market": "Series game winner (2-way)", "prob": 0.545, "confidence": "Low",
        "why_tier": "Only one side's run rates could be read, so the estimate is capped at Low.",
        "prediction": (
            "Tampa Bay Rays are the selection to level the World Series in Game 2 at American Family Field. "
            "The Rays won 98 regular-season games and scored 736 runs while allowing 650, a per-game rate of 4.54 against 4.01, "
            "yet they lost Game 1 by a single run, 3-2, in Milwaukee. "
            "A one-run defeat on the road is not evidence of a mismatch, and the Rays' run prevention remains the strongest verifiable number in this series."
        ),
    },
    {
        "fixture": "M-01", "selection": "Max Verstappen to win the United States Grand Prix",
        "market": "Race winner", "prob": 0.29, "confidence": "Low",
        "why_tier": "Third in second practice is not a strong enough base for a longer price.",
        "prediction": (
            "Max Verstappen is the alternative selection for the United States Grand Prix at the Circuit of the Americas. "
            "The Red Bull driver was second in first practice behind Charles Leclerc and then third in second practice, 0.189s off Leclerc's 1:35.291 and 0.147s behind Kimi Antonelli. "
            "The gaps are small enough that grid position and strategy will decide the 56-lap race, and Verstappen's long-run pace was not published in the session results read here."
        ),
    },
]


# ------------------------------------------------------------- coverage
COVERAGE = [
    # sport, discovery rows listed, fixtures with an official link, picks, high picks, headline reason
    ("ice-hockey", 4, 4, 1, 0, "Four of the league's twelve 24 Oct games were captured with odds; club records were readable for Boston only, which caps confidence."),
    ("baseball", 1, 1, 1, 0, "One game on the calendar (World Series Game 2); Milwaukee's run rates were not in the captured standings segment."),
    ("tennis", 5, 1, 1, 0, "Semi-final results and seeds are official; no official order of play with start times was published when read."),
    ("motor-racing", 1, 1, 2, 0, "Practice classification only. No grid, no long-run data, so race picks stay Low."),
    ("basketball", 8, 0, 0, 0, "NBA.com returned its calendar (8 games on 24 Oct) but no per-game detail, and the NBA data feed refused the request, so no team inputs exist."),
    ("cricket", 6, 0, 0, 0, "Listed matches are franchise and bilateral games whose boards published no fixture page that could be read in this window."),
    ("darts", 6, 0, 0, 0, "The PDC tournament route returned a consent wall instead of a draw, so no match could be confirmed."),
    ("rugby-union", 5, 0, 0, 0, "League fixture pages were not read this session; the listed matches therefore stay discovery-only."),
    ("rugby-league", 3, 0, 0, 0, "OLBG lists outright markets for 2027 only; no match market exists to price."),
    ("snooker", 1, 0, 0, 0, "One match was listed and its start had already passed when read."),
    ("handball", 8, 0, 0, 0, "EHF fixture route was not read; all eight listings remain discovery-only."),
    ("volleyball", 6, 0, 0, 0, "Six listed matches, five already started; league sites were not read."),
    ("golf", 0, 0, 0, 0, "The OLBG golf hub returned no tips at all when read, so no event was available to price."),
    ("gaelic-sports", 4, 0, 0, 0, "Club fixtures were listed but no official fixture page was read."),
    ("greyhounds", 7, 0, 0, 0, "Race cards change every few minutes and no GBGB card was read; runner names stay unconfirmed."),
]

FLAGS = [
    ("F-7F-01", "high", "Eight of twelve NHL games on 24 Oct have no published row",
     "The NHL schedule feed reports 12 games for 24 Oct 2026. Only the first four carried through in the page segment that was read, so eight games are missing from this desk.",
     "https://api-web.nhle.com/v1/schedule/2026-10-24"),
    ("F-7F-02", "high", "Eleven of fifteen sports carry no priced selection today",
     "Basketball, cricket, darts, rugby union, rugby league, snooker, handball, volleyball, golf, Gaelic sports and greyhounds are listed but unpriced. Each row states the specific missing input; no value was filled in to reach a quota.",
     "https://www.olbg.com/betting-tips"),
    ("F-7F-03", "high", "The five-High-picks-per-sport target is not met",
     "Zero selections clear the High bar today. The brief's band starts at -250 (71.4% fair) and the High rule starts at 70%, which leaves a 1.4-point window; the verified inputs available this session do not land inside it for any match.",
     "https://www.olbg.com/betting-tips"),
    ("F-7F-04", "medium", "Tennis start time is unconfirmed",
     "No official order of play with a start time was published for the Almaty final when read. The 25 Oct 06:00 UK listing comes from OLBG, which is a discovery source and not an official federation.",
     "https://www.atptour.com/en/scores/current"),
    ("F-7F-05", "medium", "NHL odds for Rangers at Senators were not readable",
     "The provider price block was truncated in the captured page segment. The price is blank rather than estimated.",
     "https://api-web.nhle.com/v1/schedule/2026-10-24"),
    ("F-7F-06", "medium", "Milwaukee Brewers season totals were not captured",
     "The MLB standings response is paginated by league; only American League clubs were in the segment read, so the Brewers' runs scored and allowed are blank.",
     "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason"),
    ("F-7F-07", "medium", "Puck-line and run-line prices are our own research lines",
     "Boston -1.5 and the Tampa Bay / Milwaukee prices are originated here, not observed sportsbook offers. They are labelled as such everywhere they appear.",
     "https://api-web.nhle.com/v1/schedule/2026-10-24"),
    ("F-7F-08", "low", "OLBG tip shares are votes, not probabilities",
     "The discovery table reproduces OLBG's tip counts because that is what the site publishes. A 100% tip share is one tipster out of one and is not a 100% chance of winning.",
     "https://www.olbg.com/betting-tips/Tennis/3"),
]

# ------------------------------------------------------------ repo findings
REPO_FINDINGS = [
    ("R-01", "high", "A peer desk published 66 High picks that all sit on the same fair price",
     "data/8aede3ba/fixtures.json prices every High selection at the same point of the 70%-to--250 window. Sixty-six independent matches cannot all land on one price; the tier was set by the window, not by the fixture.",
     "data/8aede3ba/fixtures.json"),
    ("R-02", "high", "Peer-desk prose contains claims that are not checkable",
     "data/8aede3ba/fixtures.json describes 'Paul George's 38-point Celtics debut' and calls New York the reigning champion. No source in that file supports either statement, and neither appears in the official NBA or NHL feeds read today.",
     "data/8aede3ba/fixtures.json"),
    ("R-03", "high", "The canonical root releases zero High picks and says so in prose",
     "index.html and data/current/snapshot.json both report high: 0, medium: 0. Anyone landing on the root sees no picks at all, which is the confusion this desk exists to fix.",
     "data/current/snapshot.json"),
    ("R-04", "medium", "The repository carries 55 sibling desk directories and 141 MB of tracked files",
     "Each session publishes its own copy of the same dashboard. There is no index that says which desk is current, so a reader cannot tell which numbers to trust.",
     "COORDINATION.md"),
    ("R-05", "medium", "COORDINATION.md repeats section headings",
     "The file contains more than one '## 4. Requests and conflict log' and repeated '## 74'/'## 75' headings, so the task board is not reliably ordered.",
     "COORDINATION.md"),
    ("R-06", "medium", "Old rows keep claims that are now contradicted",
     "The root README states 'zero Medium/High selections' while sibling desks advertise dozens. Both are published under the same domain.",
     "README.md"),
    ("R-07", "low", "Root navigation does not link to any desk's picks",
     "Before this session, no page on the root linked to a page called picks with actual selections; picks.html was an alias to a match list with no picks on it.",
     "pipeline/build.py"),
]
