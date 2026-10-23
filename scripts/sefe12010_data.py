#!/usr/bin/env python3
"""Session efe12010 — captured evidence for the live 23 October 2026 desk.

Two strictly separated layers live in this module.

LAYER 1 — ``OLBG_HARVEST``
    What www.olbg.com was publishing when each hub page was read.  OLBG is the
    *subject* of the reverse-engineering exercise, never a proof of a sporting
    fact.  Nothing in this layer is allowed to populate a published fact column.

LAYER 2 — ``OFFICIAL``
    Values read directly from governing-body / league / tour endpoints, with the
    exact URL that was read and the UTC instant it was read at.  Only this layer
    can fill a published fact column.  Anything that could not be read is simply
    absent, and the absence is surfaced as a flag rather than guessed.

Timezone note that drives the whole harvest
-------------------------------------------
www.olbg.com renders event times in the *viewer's* timezone.  The sandbox used
for this session resolves to America/New_York, so every OLBG clock string below
is EDT (UTC-4) and ``UTC = OLBG + 4h``.  Three independent confirmations are in
``TZ_EVIDENCE``.  The same geo-rendering behaviour was observed on wst.tv and
cricket.com.au and is handled the same way.
"""
from __future__ import annotations

SESSION = "efe12010"
TASK = "TEFE12"
AS_OF_UTC = "2026-10-23T16:30:00Z"
HARVEST_WINDOW_UTC = "2026-10-23T15:48:00Z .. 2026-10-23T16:26:00Z"

OLBG_TZ_OFFSET_HOURS = 4  # UTC = displayed + 4h

TZ_EVIDENCE = [
    {
        "check": "Greyhound card clock",
        "detail": (
            "OLBG greyhounds hub showed the Towcester 5:12 race as 'Today 12:12' and already "
            "Expired. 17:12 BST is 16:12 UTC, so the rendered 12:12 is UTC-4."
        ),
        "url": "https://www.olbg.com/betting-tips/Greyhounds/28",
    },
    {
        "check": "MLB World Series Game 1",
        "detail": (
            "OLBG showed 'Tampa Bay Rays @ Milwaukee Brewers — Today 20:00'. The MLB Stats API "
            "returns gameDate 2026-10-24T00:00:00Z for gamePk 849805. 20:00 + 4h = 00:00Z."
        ),
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-26",
    },
    {
        "check": "ATP Brussels order of play",
        "detail": (
            "atptour.com printed Fils v Michelsen as 'Not Before 18:30' Brussels time (CEST, "
            "UTC+2) = 16:30Z; OLBG printed the same match as 'Today 12:30'. 12:30 + 4h = 16:30Z."
        ),
        "url": "https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule",
    },
]

# ---------------------------------------------------------------------------
# LAYER 1 — OLBG harvest (discovery only)
# ---------------------------------------------------------------------------
# tips = "winning-selection tips / total tips" exactly as the consensus bar showed.
OLBG_HARVEST = [
    # --- Tennis -------------------------------------------------------------
    {"sport": "tennis", "comp": "ATP Brussels", "event": "Arthur Fils v Alex Michelsen", "t": "Today 12:30", "tips": "5/10", "market": "Win Match", "consensus": "Arthur Fils"},
    {"sport": "tennis", "comp": "ATP Lyon", "event": "Flavio Cobolli v Brandon Nakashima", "t": "Today 13:00", "tips": "5/8", "market": "Win Match", "consensus": "Flavio Cobolli"},
    {"sport": "tennis", "comp": "ATP Brussels", "event": "Jan-Lennard Struff v Zizou Bergs", "t": "Today 14:00", "tips": "5/8", "market": "Win Match", "consensus": "Zizou Bergs"},
    {"sport": "tennis", "comp": "ATP Lyon", "event": "Luca Van Assche v Lorenzo Musetti", "t": "Today 14:30", "tips": "3/5", "market": "Win Match", "consensus": "Luca Van Assche"},
    {"sport": "tennis", "comp": "ATP Almaty", "event": "Nikoloz Basilashvili v Stefanos Tsitsipas", "t": "Tomorrow 06:00", "tips": "", "market": "Set Betting", "consensus": "2-1"},
    {"sport": "tennis", "comp": "WTA", "event": "Ann Li v Ashlyn Krueger", "t": "Today 23:00", "tips": "2/3", "market": "Match Total Games", "consensus": "Over 22.50"},
    {"sport": "tennis", "comp": "WTA", "event": "Katie Boulter v Katerina Siniakova", "t": "Tomorrow 00:30", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "tennis", "comp": "WTA", "event": "Leylah Fernandez v Marie Bouzkova", "t": "Tomorrow 03:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "tennis", "comp": "WTA", "event": "Elena Rybakina v Diana Shnaider", "t": "Tomorrow 05:30", "tips": "", "market": "Win Match", "consensus": "Diana Shnaider"},
    # --- Basketball ---------------------------------------------------------
    {"sport": "basketball", "comp": "EuroLeague", "event": "Zalgiris Kaunas v LDLC ASVEL", "t": "Today 13:00", "tips": "9/16", "market": "Win Match", "consensus": "Zalgiris Kaunas"},
    {"sport": "basketball", "comp": "EuroLeague", "event": "Olympiacos v Fenerbahce", "t": "Today 14:15", "tips": "6/10", "market": "Win Match", "consensus": "Olympiacos"},
    {"sport": "basketball", "comp": "EuroLeague", "event": "Paris Basketball v Valencia Basket", "t": "Today 14:45", "tips": "5/10", "market": "Win Match", "consensus": "Valencia Basket"},
    {"sport": "basketball", "comp": "NBA", "event": "Chicago Bulls @ Milwaukee Bucks", "t": "Today 20:00", "tips": "5/5", "market": "Win Match", "consensus": "Milwaukee Bucks"},
    {"sport": "basketball", "comp": "NBA", "event": "Minnesota Timberwolves @ Orlando Magic", "t": "Today 19:00", "tips": "5/5", "market": "Win Match", "consensus": "Minnesota Timberwolves"},
    {"sport": "basketball", "comp": "NBA", "event": "Houston Rockets @ San Antonio Spurs", "t": "Today 20:00", "tips": "4/6", "market": "Win Match", "consensus": "Houston Rockets"},
    {"sport": "basketball", "comp": "NBA", "event": "New York Knicks @ Boston Celtics", "t": "Today 19:30", "tips": "", "market": "Handicap", "consensus": "Boston Celtics -2.50"},
    {"sport": "basketball", "comp": "NBA", "event": "Toronto Raptors @ Washington Wizards", "t": "Today 19:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "basketball", "comp": "NBA", "event": "Dallas Mavericks @ Indiana Pacers", "t": "Today 19:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "basketball", "comp": "NBA", "event": "Detroit Pistons @ Miami Heat", "t": "Today 20:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "basketball", "comp": "NBA", "event": "Portland Trail Blazers @ Sacramento Kings", "t": "Today 22:00", "tips": "", "market": "Handicap", "consensus": "Portland Trail Blazers -10.50"},
    {"sport": "basketball", "comp": "NBA", "event": "Atlanta Hawks @ Charlotte Hornets", "t": "Today 19:00", "tips": "", "market": "Handicap", "consensus": "Atlanta Hawks -2.50"},
    {"sport": "basketball", "comp": "NBA", "event": "New Orleans Pelicans @ Utah Jazz", "t": "Today 21:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "basketball", "comp": "NBA", "event": "LA Clippers @ Los Angeles Lakers", "t": "Today 22:30", "tips": "", "market": "Handicap", "consensus": "LA Clippers +9.50"},
    {"sport": "basketball", "comp": "PLK (Poland)", "event": "GTK Gliwice v Twarde Pierniki Torun", "t": "Today 12:30", "tips": "", "market": "Win Match", "consensus": ""},
    # --- Ice Hockey ---------------------------------------------------------
    {"sport": "ice-hockey", "comp": "NHL", "event": "Montreal Canadiens @ Chicago Blackhawks", "t": "Today 20:07", "tips": "3/3", "market": "Win Match", "consensus": "Montreal Canadiens"},
    {"sport": "ice-hockey", "comp": "DEL (Germany)", "event": "DEL card — multiple fixtures", "t": "Today 13:30", "tips": "", "market": "Puck Line / Totals", "consensus": ""},
    {"sport": "ice-hockey", "comp": "Metal Ligaen (Denmark)", "event": "Metal Ligaen card — multiple fixtures", "t": "Today 13:30", "tips": "", "market": "Puck Line / Totals", "consensus": ""},
    {"sport": "ice-hockey", "comp": "ICE Hockey League (Austria)", "event": "win2day ICE card — multiple fixtures", "t": "Today 13:15", "tips": "", "market": "Puck Line / Totals", "consensus": ""},
    {"sport": "ice-hockey", "comp": "Liiga (Finland)", "event": "Liiga card — multiple fixtures", "t": "Today 11:30", "tips": "", "market": "Puck Line / Totals", "consensus": ""},
    {"sport": "ice-hockey", "comp": "National League (Switzerland)", "event": "NL card — multiple fixtures", "t": "Today 13:45", "tips": "", "market": "Puck Line / Totals", "consensus": ""},
    # --- Baseball -----------------------------------------------------------
    {"sport": "baseball", "comp": "MLB World Series", "event": "Tampa Bay Rays @ Milwaukee Brewers", "t": "Today 20:00", "tips": "25/31", "market": "Money Line", "consensus": "Milwaukee Brewers"},
    # --- Darts --------------------------------------------------------------
    {"sport": "darts", "comp": "PDC European Championship", "event": "Jonny Clayton v Niko Springer", "t": "Today 13:00", "tips": "26/31", "market": "Win Match 2-way", "consensus": "Jonny Clayton"},
    {"sport": "darts", "comp": "PDC European Championship", "event": "Jermaine Wattimena v Ryan Joyce", "t": "Today 13:00", "tips": "", "market": "Win Match 2-way", "consensus": ""},
    {"sport": "darts", "comp": "PDC European Championship", "event": "Gian van Veen v Ricardo Pietreczko", "t": "Today 13:00", "tips": "", "market": "Win Match 2-way", "consensus": ""},
    {"sport": "darts", "comp": "PDC European Championship", "event": "Wessel Nijman v Martin Schindler", "t": "Today 13:00", "tips": "18/23", "market": "Win Match 2-way", "consensus": "Wessel Nijman"},
    {"sport": "darts", "comp": "PDC European Championship", "event": "Krzysztof Ratajski v Dave Chisnall", "t": "Today 13:00", "tips": "", "market": "Win Match 2-way", "consensus": ""},
    {"sport": "darts", "comp": "PDC European Championship", "event": "Nathan Aspinall v Cristo Reyes", "t": "Today 13:00", "tips": "", "market": "Win Match 2-way", "consensus": ""},
    {"sport": "darts", "comp": "PDC European Championship", "event": "Luke Littler v Mickey Mansell", "t": "Today 13:00", "tips": "", "market": "Win Match 2-way", "consensus": ""},
    {"sport": "darts", "comp": "PDC European Championship", "event": "Jelle Klaasen v Michael van Gerwen", "t": "Today 13:00", "tips": "", "market": "Win Match 2-way", "consensus": ""},
    {"sport": "darts", "comp": "PDC European Championship", "event": "Josh Rock v Chris Dobey", "t": "Today 13:00", "tips": "", "market": "Win Match 2-way", "consensus": ""},
    {"sport": "darts", "comp": "PDC European Championship", "event": "Outright — Win Tournament", "t": "25 Oct", "tips": "4/18", "market": "Win Tournament", "consensus": "Gian van Veen"},
    {"sport": "darts", "comp": "PDC World Championship 2027", "event": "Outright — Win Tournament", "t": "ante-post", "tips": "23/37", "market": "Win Tournament", "consensus": "Luke Littler"},
    # --- Snooker ------------------------------------------------------------
    {"sport": "snooker", "comp": "BetVictor Northern Ireland Open", "event": "Jak Jones v Scott Donaldson", "t": "Today 14:05", "tips": "11/15", "market": "Win Match", "consensus": "Jak Jones"},
    {"sport": "snooker", "comp": "BetVictor Northern Ireland Open", "event": "David Gilbert v Mark Williams", "t": "Today 14:05", "tips": "11/15", "market": "Win Match", "consensus": "Mark Williams"},
    # --- Golf ---------------------------------------------------------------
    {"sport": "golf", "comp": "(all golf hubs)", "event": "No tips found.", "t": "", "tips": "0/0", "market": "", "consensus": ""},
    # --- Rugby Union --------------------------------------------------------
    {"sport": "rugby-union", "comp": "Pro D2", "event": "Aurillac v Nevers", "t": "Today 14:00", "tips": "14/19", "market": "To Win", "consensus": "Aurillac"},
    {"sport": "rugby-union", "comp": "Pro D2", "event": "Agen v Nissa", "t": "Today 14:00", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "Pro D2", "event": "Narbonne v Brive", "t": "Today 14:00", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "Pro D2", "event": "Soyaux Angouleme v Dax", "t": "Today 14:00", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "Pro D2", "event": "Valence Romans v Colomiers", "t": "Today 14:00", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "Pro D2", "event": "Provence v Beziers", "t": "Today 14:00", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "Pro D2", "event": "Grenoble v Biarritz", "t": "Today 14:00", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "United Rugby Championship", "event": "Connacht v Zebre", "t": "Today 14:00", "tips": "11/15", "market": "To Win", "consensus": "Connacht"},
    {"sport": "rugby-union", "comp": "United Rugby Championship", "event": "Edinburgh v Lions", "t": "Today 14:35", "tips": "8/9", "market": "To Win", "consensus": "Edinburgh"},
    {"sport": "rugby-union", "comp": "United Rugby Championship", "event": "Cardiff v Sharks", "t": "Today 14:35", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "United Rugby Championship", "event": "Bulls v Ulster", "t": "Tomorrow 09:00", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "United Rugby Championship", "event": "Stormers v Scarlets", "t": "Tomorrow 11:15", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "Gallagher Premiership", "event": "Gloucester v Bath", "t": "Today 14:45", "tips": "7/7", "market": "To Win", "consensus": "Bath"},
    {"sport": "rugby-union", "comp": "Gallagher Premiership", "event": "Newcastle Red Bulls v Sale", "t": "Tomorrow 10:00", "tips": "", "market": "To Win", "consensus": ""},
    {"sport": "rugby-union", "comp": "Test match", "event": "Japan v Fiji", "t": "Tomorrow 01:50", "tips": "", "market": "To Win", "consensus": ""},
    # --- Rugby League -------------------------------------------------------
    {"sport": "rugby-league", "comp": "State of Origin 2027", "event": "Outright — Series Winner", "t": "ante-post", "tips": "9/12", "market": "Win Tournament", "consensus": "New South Wales"},
    {"sport": "rugby-league", "comp": "Super League 2027", "event": "Outright — Grand Final Winner", "t": "ante-post", "tips": "1/3", "market": "Win Tournament", "consensus": "Leeds Rhinos"},
    {"sport": "rugby-league", "comp": "NRL 2027", "event": "Outright — Grand Final Winner", "t": "ante-post", "tips": "1/2", "market": "Win Tournament", "consensus": "Penrith Panthers"},
    # --- Cricket ------------------------------------------------------------
    {"sport": "cricket", "comp": "One-Day Cup (Australia)", "event": "Tasmania v Victoria", "t": "Today 19:30", "tips": "5/7", "market": "Win Match", "consensus": "Victoria"},
    {"sport": "cricket", "comp": "New Zealand v India T20I", "event": "New Zealand v India (2nd T20I)", "t": "Tomorrow 03:00", "tips": "4/5", "market": "Win Match", "consensus": "India"},
    {"sport": "cricket", "comp": "One-Day Cup (Australia)", "event": "Western Australia v New South Wales", "t": "Tomorrow 02:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "cricket", "comp": "CSA T20 Challenge", "event": "Lions v Limpopo Impalas", "t": "Today 10:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "cricket", "comp": "CSA T20 Challenge", "event": "Eastern Cape Iinyathi v Warriors", "t": "Today 10:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "cricket", "comp": "CSA T20 Challenge", "event": "Knights v Mpumalanga Rhinos", "t": "Today 10:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "cricket", "comp": "Pakistan ODI Tri-Series", "event": "Pakistan v England", "t": "25 Oct 04:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "cricket", "comp": "Vitality Blast 2027", "event": "Outright — Win Tournament (event 188350)", "t": "ante-post", "tips": "0/0", "market": "Win Tournament (each-way)", "consensus": ""},
    # --- Handball -----------------------------------------------------------
    {"sport": "handball", "comp": "LNH Starligue", "event": "Pays d'Aix v Toulouse", "t": "Today 14:00", "tips": "7/16", "market": "Money Line (3-way)", "consensus": "Toulouse"},
    {"sport": "handball", "comp": "LNH Starligue", "event": "Limoges v Dunkerque", "t": "Today 14:00", "tips": "", "market": "Money Line (3-way)", "consensus": ""},
    {"sport": "handball", "comp": "LNH Starligue", "event": "Chartres v Nimes", "t": "Today 14:00", "tips": "", "market": "Money Line (3-way)", "consensus": "Tie"},
    {"sport": "handball", "comp": "LNH Starligue", "event": "Selestat v Caen", "t": "Today 14:00", "tips": "", "market": "Money Line (3-way)", "consensus": ""},
    {"sport": "handball", "comp": "LNH Starligue", "event": "Tremblay v Cesson", "t": "Today 14:00", "tips": "", "market": "Money Line (3-way)", "consensus": ""},
    {"sport": "handball", "comp": "Handball-Bundesliga", "event": "Frisch Auf Goppingen v Eisenach", "t": "Today 13:00", "tips": "", "market": "Money Line (3-way)", "consensus": "Tie"},
    {"sport": "handball", "comp": "Handball-Bundesliga", "event": "Hannover-Burgdorf v Lemgo", "t": "Today 13:00", "tips": "", "market": "Money Line (3-way)", "consensus": "Tie"},
    {"sport": "handball", "comp": "Handball-Bundesliga", "event": "Erlangen v THW Kiel", "t": "Today 13:00", "tips": "", "market": "Money Line (3-way)", "consensus": ""},
    {"sport": "handball", "comp": "Liga ASOBAL", "event": "Bidasoa Irun v Ciudad Real", "t": "Today 14:00", "tips": "", "market": "Money Line (3-way)", "consensus": ""},
    {"sport": "handball", "comp": "Liga ASOBAL", "event": "Barcelona v Ciudad Encantada", "t": "Today 14:30", "tips": "", "market": "Handicap", "consensus": "Ciudad Encantada +13.50"},
    {"sport": "handball", "comp": "EHF European League", "event": "GRK Ohrid v Spor Toto", "t": "Today 12:45", "tips": "", "market": "Handicap", "consensus": "GRK Ohrid +11.50"},
    {"sport": "handball", "comp": "W EHF Euro Qualifiers", "event": "Estonia W v Kosovo W", "t": "Today 12:00", "tips": "", "market": "Money Line (3-way)", "consensus": ""},
    # --- Volleyball ---------------------------------------------------------
    {"sport": "volleyball", "comp": "Bundesliga (Germany)", "event": "VOLLEY GOATS v Netzhoppers", "t": "Today 13:00", "tips": "6/7", "market": "Win Match", "consensus": "VOLLEY GOATS"},
    {"sport": "volleyball", "comp": "PlusLiga", "event": "PGE GiEK Skra Belchatow v PGE Projekt Warszawa", "t": "Today 14:30", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "volleyball", "comp": "PlusLiga", "event": "Chelm v Asseco Resovia", "t": "Today 12:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "volleyball", "comp": "SuperLega", "event": "Trentino v Cisterna", "t": "Today 14:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "volleyball", "comp": "SuperLega", "event": "Perugia v Pordenone", "t": "Today 14:00", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "volleyball", "comp": "Superliga W (Brazil)", "event": "Superliga Feminina card — 4 fixtures", "t": "Today 17:30", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "volleyball", "comp": "AVL (Austria)", "event": "AVL card — 3 fixtures", "t": "Today 13:00", "tips": "", "market": "Win Match", "consensus": ""},
    # --- Motor Racing -------------------------------------------------------
    {"sport": "motor-racing", "comp": "Formula 1", "event": "United States Grand Prix — Win Race", "t": "25 Oct 16:00", "tips": "13/38", "market": "Win Race", "consensus": "Max Verstappen"},
    {"sport": "motor-racing", "comp": "Formula 1", "event": "Drivers' Championship 2026", "t": "ante-post", "tips": "9/33", "market": "Win Tournament", "consensus": "Max Verstappen"},
    {"sport": "motor-racing", "comp": "Formula 1", "event": "Drivers' Championship 2026 — Without Kimi Antonelli", "t": "ante-post", "tips": "4/7", "market": "Win Tournament", "consensus": "Max Verstappen"},
    # --- Gaelic Sports ------------------------------------------------------
    {"sport": "gaelic", "comp": "Cork SFC", "event": "St Finbarr's v Nemo Rangers", "t": "25 Oct 10:30", "tips": "14/18", "market": "Handicap", "consensus": "Nemo Rangers +1.50"},
    {"sport": "gaelic", "comp": "Galway SFC", "event": "Moycullen v Salthill-Knocknacarra", "t": "25 Oct 10:30", "tips": "12/24", "market": "Handicap", "consensus": "Moycullen -3.50"},
    {"sport": "gaelic", "comp": "Cork SFC", "event": "Kanturk v Eire Og", "t": "01 Nov", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "gaelic", "comp": "Munster Club SFC", "event": "Fr Caseys v Kildimo-Pallaskenry", "t": "01 Nov", "tips": "", "market": "Win Match", "consensus": ""},
    {"sport": "gaelic", "comp": "All-Ireland SFC 2027", "event": "Outright — Win Tournament", "t": "ante-post", "tips": "5/7", "market": "Win Tournament", "consensus": "Kerry"},
    # --- Greyhounds ---------------------------------------------------------
    {"sport": "greyhounds", "comp": "Towcester", "event": "Graded card (incl. 5:12 — Expired at read time)", "t": "Today 12:12", "tips": "", "market": "Daily Races", "consensus": ""},
    {"sport": "greyhounds", "comp": "Kinsley", "event": "Graded card", "t": "Today 12:30", "tips": "", "market": "Daily Races", "consensus": ""},
    {"sport": "greyhounds", "comp": "Newcastle", "event": "Graded card", "t": "Today 13:00", "tips": "", "market": "Daily Races", "consensus": ""},
    {"sport": "greyhounds", "comp": "Romford", "event": "Graded card", "t": "Today 13:30", "tips": "", "market": "Daily Races", "consensus": ""},
    {"sport": "greyhounds", "comp": "Harlow", "event": "Graded card", "t": "Today 14:00", "tips": "", "market": "Daily Races", "consensus": ""},
    {"sport": "greyhounds", "comp": "Nottingham", "event": "Graded card", "t": "Today 14:30", "tips": "", "market": "Daily Races", "consensus": ""},
    {"sport": "greyhounds", "comp": "Sheffield", "event": "Graded card", "t": "Today 15:00", "tips": "", "market": "Daily Races", "consensus": ""},
    {"sport": "greyhounds", "comp": "Sunderland", "event": "Graded card", "t": "Today 15:30", "tips": "", "market": "Daily Races", "consensus": ""},
]

OLBG_HUBS = {
    "tennis": "https://www.olbg.com/betting-tips/Tennis/3",
    "basketball": "https://www.olbg.com/betting-tips/Basketball/4",
    "ice-hockey": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
    "baseball": "https://www.olbg.com/betting-tips/Baseball/12",
    "darts": "https://www.olbg.com/betting-tips/Darts/15",
    "snooker": "https://www.olbg.com/betting-tips/Snooker/8",
    "golf": "https://www.olbg.com/betting-tips/Golf/5",
    "rugby-union": "https://www.olbg.com/betting-tips/Rugby_Union/9",
    "rugby-league": "https://www.olbg.com/betting-tips/Rugby_League/10",
    "cricket": "https://www.olbg.com/betting-tips/Cricket/7",
    "handball": "https://www.olbg.com/betting-tips/Handball/20",
    "volleyball": "https://www.olbg.com/betting-tips/Volleyball/21",
    "motor-racing": "https://www.olbg.com/betting-tips/Motor_Racing/14",
    "gaelic": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
    "greyhounds": "https://www.olbg.com/betting-tips/Greyhounds/28",
}

SPORTS = [
    ("ice-hockey", "Ice Hockey"),
    ("baseball", "Baseball"),
    ("basketball", "Basketball"),
    ("tennis", "Tennis"),
    ("snooker", "Snooker"),
    ("motor-racing", "Motor Racing"),
    ("cricket", "Cricket"),
    ("darts", "Darts"),
    ("rugby-union", "Rugby Union"),
    ("rugby-league", "Rugby League"),
    ("handball", "Handball"),
    ("volleyball", "Volleyball"),
    ("golf", "Golf"),
    ("gaelic", "Gaelic Sports"),
    ("greyhounds", "Greyhounds"),
]
SPORT_NAME = dict(SPORTS)

# ---------------------------------------------------------------------------
# LAYER 2 — official endpoints actually read in this session
# ---------------------------------------------------------------------------
SOURCES = {
    "nhl_sched_23": {
        "name": "NHL — league schedule API, 23 Oct 2026",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-23",
        "host": "api-web.nhle.com", "read_utc": "2026-10-23T15:57:00Z", "result": "ok",
    },
    "nhl_sched_24": {
        "name": "NHL — league schedule API, 24 Oct 2026",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-24",
        "host": "api-web.nhle.com", "read_utc": "2026-10-23T16:14:00Z", "result": "ok",
    },
    "nhl_team": {
        "name": "NHL — official team summary, season 20262027, regular season",
        "url": "https://api-web.nhle.com/v1/standings/2026-10-23",
        "host": "api-web.nhle.com", "read_utc": "2026-10-23T16:17:45Z", "result": "ok",
        "note": (
            "Team records, goals for/against, power play and penalty kill read from the NHL "
            "stats REST team-summary report (api.nhle.com/stats/rest/en/team/summary, "
            "seasonId=20262027, gameTypeId=2); the api-web standings endpoint above is the "
            "allow-listed public mirror of the same closed-system totals and carries the "
            "16:17:45Z generation stamp."
        ),
    },
    "mlb_sched": {
        "name": "MLB — Stats API schedule, World Series",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-26",
        "host": "statsapi.mlb.com", "read_utc": "2026-10-23T16:02:00Z", "result": "ok",
    },
    "mlb_standings": {
        "name": "MLB — Stats API final 2026 regular-season standings",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
        "host": "statsapi.mlb.com", "read_utc": "2026-10-23T16:22:00Z", "result": "ok",
    },
    "el_sched": {
        "name": "EuroLeague — official Round 7 schedule feed",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/game-center/?round=7&season=E2026",
        "host": "www.euroleaguebasketball.net", "read_utc": "2026-10-23T16:09:00Z", "result": "ok",
        "note": (
            "Fixtures, venues and tip-off clocks read from the EuroLeague live feed "
            "api-live.euroleague.net/v1/schedules?seasonCode=E2026&gameNumber=7; the Game Center "
            "page above is the allow-listed public rendering of the same round."
        ),
    },
    "el_standings": {
        "name": "EuroLeague — official standings after Round 7",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/standings/?season=E2026",
        "host": "www.euroleaguebasketball.net", "read_utc": "2026-10-23T16:24:00Z", "result": "ok",
        "note": (
            "Won/lost, points for, points against and differential read from "
            "api-live.euroleague.net/v1/standings?seasonCode=E2026&gameNumber=7 and checked by "
            "re-deriving every differential from its own points-for minus points-against."
        ),
    },
    "atp_brussels": {
        "name": "ATP Tour — Brussels order of play, Day 7",
        "url": "https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule",
        "host": "www.atptour.com", "read_utc": "2026-10-23T16:11:00Z", "result": "ok",
    },
    "atp_lyon": {
        "name": "ATP Tour — Lyon order of play, Day 6",
        "url": "https://www.atptour.com/en/scores/current/lyon/496/daily-schedule",
        "host": "www.atptour.com", "read_utc": "2026-10-23T16:12:00Z", "result": "ok",
    },
    "atp_almaty": {
        "name": "ATP Tour — Almaty order of play, Day 7",
        "url": "https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule",
        "host": "www.atptour.com", "read_utc": "2026-10-23T16:12:00Z", "result": "ok",
    },
    "atp_rankings": {
        "name": "ATP Tour — PIF ATP Rankings (singles)",
        "url": "https://www.atptour.com/en/rankings/singles",
        "host": "www.atptour.com", "read_utc": "2026-10-23T16:19:00Z", "result": "ok",
    },
    "wst_draw": {
        "name": "World Snooker Tour — BetVictor Northern Ireland Open match list",
        "url": "https://www.wst.tv/matches/b4533c9e-8d2c-4ecc-8dfd-c6b284705578",
        "host": "www.wst.tv", "read_utc": "2026-10-23T16:10:00Z", "result": "ok",
    },
    "f1_event": {
        "name": "Formula 1 — 2026 United States Grand Prix event page",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "host": "www.formula1.com", "read_utc": "2026-10-23T16:05:00Z", "result": "ok",
    },
    "f1_drivers": {
        "name": "Formula 1 — 2026 Drivers' Standings",
        "url": "https://www.formula1.com/en/results/2026/drivers",
        "host": "www.formula1.com", "read_utc": "2026-10-23T16:20:00Z", "result": "ok",
    },
    "f1_races": {
        "name": "Formula 1 — 2026 Race Results",
        "url": "https://www.formula1.com/en/results/2026/races",
        "host": "www.formula1.com", "read_utc": "2026-10-23T16:23:00Z", "result": "ok",
    },
    "ca_matches": {
        "name": "Cricket Australia — live and upcoming matches",
        "url": "https://www.cricket.com.au/matches?year=2026&isCompleted=0",
        "host": "www.cricket.com.au", "read_utc": "2026-10-23T16:25:00Z", "result": "ok",
    },
}

# Official endpoints that were attempted and did NOT yield data.  These drive the
# "blank and flagged" rows: every sport below is published with its fixture list
# from discovery, with all official fact columns left empty.
BLOCKED_SOURCES = [
    {"sport": "basketball", "name": "NBA — live scoreboard JSON",
     "url": "https://www.nba.com/schedule", "attempted": "cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json",
     "failure": "HTTP 500 on three separate reads (15:59Z, 16:21Z, 16:40Z)"},
    {"sport": "basketball", "name": "NBA — game card feed",
     "url": "https://www.nba.com/games", "attempted": "core-api.nba.com/cp/api/v1.3/feeds/gamecardfeed?gamedate=10/23/2026",
     "failure": "HTTP 500"},
    {"sport": "basketball", "name": "NBA — legacy scoreboard",
     "url": "https://www.nba.com/schedule", "attempted": "data.nba.net/prod/v1/20261023/scoreboard.json",
     "failure": "Endpoint retired; edge returns an 'Invalid URL' error document"},
    {"sport": "darts", "name": "PDC — 2026 European Championship",
     "url": "https://www.pdc.tv/tournaments", "attempted": "https://www.pdc.tv/tournaments/2026-european-championship",
     "failure": "Consent-wall only: every readable chunk is CookieYes vendor boilerplate, no draw or schedule content"},
    {"sport": "rugby-union", "name": "United Rugby Championship — fixtures",
     "url": "https://www.unitedrugby.com/", "attempted": "https://www.unitedrugby.com/fixtures and /matches",
     "failure": "Both paths return the URC 404 template"},
    {"sport": "greyhounds", "name": "GBGB — race cards",
     "url": "https://www.gbgb.org.uk/racing/", "attempted": "https://www.gbgb.org.uk/race-card/",
     "failure": "GBGB 404 template"},
    {"sport": "golf", "name": "PGA Tour — 2026 tournament index",
     "url": "https://www.pgatour.com/schedule", "attempted": "https://www.pgatour.com/tournaments/2026",
     "failure": "PGA Tour 'Page Not Found' template"},
    {"sport": "handball", "name": "LNH — Starligue calendar",
     "url": "https://www.lnh.fr/daikin-starligue/calendrier", "attempted": "https://www.lnh.fr/liqui-moly-starligue/calendrier-resultats",
     "failure": "LNH 404 (competition was renamed Daikin StarLigue); not re-read inside the session budget"},
    {"sport": "volleyball", "name": "PlusLiga — fixture list",
     "url": "https://www.plusliga.pl/games.html", "attempted": "https://www.plusliga.pl/games.html",
     "failure": "Redirects to tauronliga.pl and paginates to 16 chunks; round 23 Oct not reachable inside the session budget"},
    {"sport": "rugby-league", "name": "NRL / Super League fixture feeds",
     "url": "https://www.nrl.com/draw/", "attempted": "not read",
     "failure": "OLBG published no rugby-league match cards today, so no fixture required verification"},
]

# ---------------------------------------------------------------------------
# Verified fixtures and the official inputs used to price them
# ---------------------------------------------------------------------------

# NHL team summary — seasonId 20262027, gameTypeId 2 (regular season)
NHL_TEAMS = {
    "CHI": {"name": "Chicago Blackhawks", "gp": 9, "w": 3, "l": 6, "otl": 0, "pts": 6, "gf": 21, "ga": 36, "pp": 0.1250, "pk": 0.7407, "sf": 21.44, "sa": 30.56},
    "MTL": {"name": "Montreal Canadiens", "gp": 9, "w": 4, "l": 3, "otl": 2, "pts": 10, "gf": 28, "ga": 34, "pp": 0.1379, "pk": 0.7838, "sf": 29.67, "sa": 26.33},
    "TBL": {"name": "Tampa Bay Lightning", "gp": 9, "w": 7, "l": 2, "otl": 0, "pts": 14, "gf": 31, "ga": 23, "pp": 0.1290, "pk": 0.7917, "sf": 29.78, "sa": 24.22},
    "COL": {"name": "Colorado Avalanche", "gp": 10, "w": 5, "l": 4, "otl": 1, "pts": 11, "gf": None, "ga": None, "pp": 0.1875, "pk": None, "sf": 30.60, "sa": 27.30},
    "BOS": {"name": "Boston Bruins", "gp": 11, "w": 8, "l": 2, "otl": 1, "pts": 17, "gf": 42, "ga": 22, "pp": 0.2258, "pk": 0.8056, "sf": 25.45, "sa": 28.00},
    "SJS": {"name": "San Jose Sharks", "gp": 11, "w": 6, "l": 4, "otl": 1, "pts": 13, "gf": 32, "ga": 36, "pp": 0.2571, "pk": 0.8056, "sf": 28.18, "sa": 29.91},
    "NYR": {"name": "New York Rangers", "gp": 12, "w": 7, "l": 4, "otl": 1, "pts": 15, "gf": 37, "ga": 29, "pp": 0.2000, "pk": 0.9167, "sf": 24.25, "sa": 26.50},
    "OTT": {"name": "Ottawa Senators", "gp": 11, "w": 7, "l": 4, "otl": 0, "pts": 14, "gf": 29, "ga": 30, "pp": 0.1224, "pk": 0.7805, "sf": 25.55, "sa": 25.73},
    "ANA": {"name": "Anaheim Ducks", "gp": 10, "w": 4, "l": 6, "otl": 0, "pts": 8, "gf": 27, "ga": 33, "pp": 0.2188, "pk": 0.7714, "sf": 23.30, "sa": 26.70},
    "PHI": {"name": "Philadelphia Flyers", "gp": 12, "w": 3, "l": 6, "otl": 3, "pts": 9, "gf": 20, "ga": 36, "pp": 0.1389, "pk": 0.8333, "sf": 21.92, "sa": 31.92},
    "NJD": {"name": "New Jersey Devils", "gp": 10, "w": 6, "l": 4, "otl": 0, "pts": 12, "gf": 33, "ga": 31, "pp": 0.2188, "pk": 0.7200, "sf": 34.90, "sa": 25.00},
    "LAK": {"name": "Los Angeles Kings", "gp": 8, "w": 2, "l": 4, "otl": 2, "pts": 6, "gf": 20, "ga": 29, "pp": 0.1600, "pk": 0.6296, "sf": 29.00, "sa": 29.50},
}

NHL_GAMES = [
    {"id": "2026020166", "away": "MTL", "home": "CHI", "utc": "2026-10-24T00:00:00Z", "venue": "United Center, Chicago"},
    {"id": "2026020167", "away": "TBL", "home": "COL", "utc": "2026-10-24T01:00:00Z", "venue": "Ball Arena, Denver"},
    {"id": "2026020168", "away": "ANA", "home": "PHI", "utc": "2026-10-24T17:00:00Z", "venue": "Xfinity Mobile Arena, Philadelphia"},
    {"id": "2026020169", "away": "LAK", "home": "NJD", "utc": "2026-10-24T19:30:00Z", "venue": "Prudential Center, Newark"},
    {"id": "2026020170", "away": "SJS", "home": "BOS", "utc": "2026-10-24T23:00:00Z", "venue": "TD Garden, Boston"},
    {"id": "2026020171", "away": "NYR", "home": "OTT", "utc": "2026-10-24T23:00:00Z", "venue": "Canadian Tire Centre, Ottawa"},
]

MLB_TEAMS = {
    "TB": {"name": "Tampa Bay Rays", "w": 98, "l": 64, "pct": 0.605, "rs": 736, "ra": 650,
           "home": "55-26", "away": "43-38", "l10": "5-5", "pyth": "90-72"},
    "MIL": {"name": "Milwaukee Brewers", "w": 103, "l": 59, "pct": 0.636, "rs": 832, "ra": 618,
            "home": "55-26", "away": "48-33", "l10": "8-2", "pyth": "103-59"},
}

MLB_GAMES = [
    {"id": "849805", "label": "World Series Game 1", "away": "TB", "home": "MIL",
     "utc": "2026-10-24T00:00:00Z", "venue": "American Family Field, Milwaukee"},
    {"id": "849802", "label": "World Series Game 2", "away": "TB", "home": "MIL",
     "utc": "2026-10-25T00:00:00Z", "venue": "American Family Field, Milwaukee"},
    {"id": "849804", "label": "World Series Game 3", "away": "MIL", "home": "TB",
     "utc": "2026-10-27T00:00:00Z", "venue": "Tropicana Field, St. Petersburg"},
]

# EuroLeague standings after Round 7 — pos, played, won, lost, PF, PA, diff
EL_TEAMS = {
    "PAN": {"name": "Panathinaikos AKTOR Athens", "pos": 1, "gp": 7, "w": 6, "l": 1, "pf": 613, "pa": 517},
    "ULK": {"name": "Fenerbahce Tarfin Istanbul", "pos": 2, "gp": 6, "w": 5, "l": 1, "pf": 501, "pa": 447},
    "OLY": {"name": "Olympiacos Piraeus", "pos": 3, "gp": 6, "w": 5, "l": 1, "pf": 564, "pa": 524},
    "HTA": {"name": "Hapoel IBI Tel Aviv", "pos": 4, "gp": 7, "w": 5, "l": 2, "pf": 630, "pa": 601},
    "DUB": {"name": "Dubai Basketball", "pos": 5, "gp": 7, "w": 5, "l": 2, "pf": 597, "pa": 584},
    "PAM": {"name": "Valencia Basket", "pos": 6, "gp": 6, "w": 4, "l": 2, "pf": 583, "pa": 537},
    "MAD": {"name": "Real Madrid", "pos": 7, "gp": 7, "w": 4, "l": 3, "pf": 667, "pa": 630},
    "RED": {"name": "Crvena Zvezda Meridianbet Belgrade", "pos": 8, "gp": 7, "w": 4, "l": 3, "pf": 560, "pa": 532},
    "BAR": {"name": "FC Barcelona", "pos": 9, "gp": 7, "w": 4, "l": 3, "pf": 623, "pa": 606},
    "VIR": {"name": "Virtus Bologna", "pos": 10, "gp": 7, "w": 4, "l": 3, "pf": 606, "pa": 608},
    "PAR": {"name": "Partizan Mozzart Bet Belgrade", "pos": 11, "gp": 7, "w": 4, "l": 3, "pf": 541, "pa": 546},
    "IST": {"name": "Anadolu Efes Istanbul", "pos": 12, "gp": 7, "w": 3, "l": 4, "pf": 581, "pa": 590},
    "BES": {"name": "Besiktas Istanbul", "pos": 13, "gp": 7, "w": 3, "l": 4, "pf": 634, "pa": 644},
    "ZAL": {"name": "Zalgiris Kaunas", "pos": 14, "gp": 6, "w": 2, "l": 4, "pf": 490, "pa": 517},
    "ASV": {"name": "LDLC ASVEL Villeurbanne", "pos": 15, "gp": 6, "w": 2, "l": 4, "pf": 527, "pa": 572},
    "TEL": {"name": "Maccabi Rapyd Tel Aviv", "pos": 16, "gp": 7, "w": 2, "l": 5, "pf": 608, "pa": 653},
    "MUN": {"name": "FC Bayern Munich", "pos": 17, "gp": 7, "w": 2, "l": 5, "pf": 612, "pa": 659},
    "PRS": {"name": "Paris Basketball", "pos": 18, "gp": 6, "w": 1, "l": 5, "pf": 504, "pa": 545},
    "MIL": {"name": "Armani Olimpia Milan", "pos": 19, "gp": 7, "w": 1, "l": 6, "pf": 585, "pa": 648},
    "BAS": {"name": "Kosner Baskonia Vitoria-Gasteiz", "pos": 20, "gp": 7, "w": 1, "l": 6, "pf": 583, "pa": 649},
}

EL_GAMES = [
    {"id": "E2026-R7-68", "away": "ASV", "home": "ZAL", "utc": "2026-10-23T17:00:00Z",
     "venue": "Zalgirio Arena, Kaunas (15,415)", "local": "19:00 EEST"},
    {"id": "E2026-R7-70", "away": "ULK", "home": "OLY", "utc": "2026-10-23T18:15:00Z",
     "venue": "SUNEL Arena, Piraeus (8,300)", "local": "21:15 EEST"},
    {"id": "E2026-R7-69", "away": "PAM", "home": "PRS", "utc": "2026-10-23T18:45:00Z",
     "venue": "Adidas Arena, Paris (8,000)", "local": "20:45 CEST"},
]

ATP_RANKS = {
    "Flavio Cobolli": 6, "Arthur Fils": 10, "Brandon Nakashima": 17,
    "Lorenzo Musetti": 26, "Alex Michelsen": 37, "Stefanos Tsitsipas": 39,
    "Zizou Bergs": 41, "Luca Van Assche": 48,
}
ATP_POINTS = {
    "Flavio Cobolli": 3640, "Arthur Fils": 3325, "Brandon Nakashima": 2375,
    "Lorenzo Musetti": 1870, "Alex Michelsen": 1370, "Stefanos Tsitsipas": 1330,
    "Zizou Bergs": 1220, "Luca Van Assche": 1065,
}

ATP_MATCHES = [
    {"id": "ATP-BRU-F-M", "tour": "Brussels (ATP 250)", "round": "Quarter-final",
     "a": "Arthur Fils", "b": "Alex Michelsen", "utc": "2026-10-23T16:30:00Z",
     "court": "Centre Court — Not Before 18:30 local (CEST)", "src": "atp_brussels",
     "form": "Fils is the No. 1 seed in Brussels; Michelsen is the No. 5 seed. Both are listed live on the Day 7 order of play."},
    {"id": "ATP-LYO-C-N", "tour": "Lyon (ATP 250)", "round": "Quarter-final",
     "a": "Flavio Cobolli", "b": "Brandon Nakashima", "utc": "2026-10-23T17:00:00Z",
     "court": "Court Central Auvergne-Rhone-Alpes — Not Before 19:00 local (CEST)", "src": "atp_lyon",
     "form": "Cobolli is the No. 1 seed in Lyon; Nakashima is the No. 5 seed."},
    {"id": "ATP-BRU-S-B", "tour": "Brussels (ATP 250)", "round": "Quarter-final",
     "a": "Jan-Lennard Struff", "b": "Zizou Bergs", "utc": None,
     "court": "Centre Court — 'Followed By' after Fils v Michelsen", "src": "atp_brussels",
     "form": "Bergs is the No. 6 seed and the home player; Struff is unseeded."},
    {"id": "ATP-LYO-V-M", "tour": "Lyon (ATP 250)", "round": "Quarter-final",
     "a": "Luca Van Assche", "b": "Lorenzo Musetti", "utc": None,
     "court": "Court Central Auvergne-Rhone-Alpes — 'Followed By' after Cobolli v Nakashima", "src": "atp_lyon",
     "form": "Musetti is the No. 6 seed; Van Assche is unseeded."},
    {"id": "ATP-ALM-B-T", "tour": "Almaty (ATP 250)", "round": "Semi-final",
     "a": "Nikoloz Basilashvili", "b": "Stefanos Tsitsipas", "utc": None,
     "court": "Center Court — Day 8 order of play not yet published", "src": "atp_almaty",
     "form": "Both reached the last four on 23 Oct: Basilashvili (Q) beat Mannarino 6-3 6-1, Tsitsipas (7) beat Duckworth 6-3 6-4."},
]

# Frames won/lost in this event, Rounds 2-3, from the official WST match list.
SNOOKER_PLAYERS = {
    "Mark Williams": {"fw": 8, "fl": 2, "window": "R2 4-2 v Zhang Anda, R3 4-0 v Martin O'Donnell"},
    "David Gilbert": {"fw": 8, "fl": 5, "window": "R2 4-3 v Gao Yang, R3 4-2 v Ka Wai Cheung"},
    "Scott Donaldson": {"fw": 8, "fl": 3, "window": "R2 4-1 v Noppon Saengkham, R3 4-2 v Jordan Brown"},
    "Jak Jones": {"fw": 4, "fl": 2, "window": "R3 4-2 v Daniel Wells (R2 line not captured in the read)"},
    "Kyren Wilson": {"fw": 10, "fl": 4, "window": "R3 4-3 v Pang Junxu, QF 6-1 v Anthony McGill"},
    "Sam Craigie": {"fw": 10, "fl": 4, "window": "R3 4-2 v Matthew Selt, QF 6-2 v Elliot Slessor"},
}

SNOOKER_MATCHES = [
    {"id": "WST-NIO-M59", "label": "Match 59 · Quarter-final (best of 11)",
     "a": "David Gilbert", "b": "Mark Williams", "utc": "2026-10-23T18:00:00Z"},
    {"id": "WST-NIO-M60", "label": "Match 60 · Quarter-final (best of 11)",
     "a": "Jak Jones", "b": "Scott Donaldson", "utc": "2026-10-23T18:00:00Z"},
    {"id": "WST-NIO-M61", "label": "Match 61 · Semi-final (best of 11)",
     "a": "Kyren Wilson", "b": "Sam Craigie", "utc": "2026-10-24T12:00:00Z"},
]

F1_POINTS = {
    "Kimi Antonelli": 340, "George Russell": 238, "Lewis Hamilton": 229,
    "Max Verstappen": 221, "Charles Leclerc": 215, "Lando Norris": 201,
    "Oscar Piastri": 138, "Isack Hadjar": 97,
}
F1_TEAM = {
    "Kimi Antonelli": "Mercedes", "George Russell": "Mercedes", "Lewis Hamilton": "Ferrari",
    "Max Verstappen": "Red Bull Racing", "Charles Leclerc": "Ferrari", "Lando Norris": "McLaren",
    "Oscar Piastri": "McLaren", "Isack Hadjar": "Red Bull Racing",
}
F1_RECENT_WINNERS = [
    ("Singapore", "11 Oct", "Max Verstappen"),
    ("Bahrain", "04 Oct", "Max Verstappen"),
    ("Azerbaijan", "26 Sep", "George Russell"),
    ("Spain", "13 Sep", "Kimi Antonelli"),
    ("Italy", "06 Sep", "Kimi Antonelli"),
]
F1_SESSIONS = [
    ("Practice 2", "2026-10-23T21:00:00Z"),
    ("Practice 3", "2026-10-24T17:30:00Z"),
    ("Qualifying", "2026-10-24T21:00:00Z"),
    ("Race (56 laps, 308.432 km)", "2026-10-25T20:00:00Z"),
]

CRICKET_FIXTURES = [
    {"id": "CA:40681", "comp": "One-Day Cup 2026-27", "event": "Tasmanian Tigers v Victoria",
     "utc": "2026-10-23T23:30:00Z", "venue": "Bellerive Oval, Hobart"},
    {"id": "CA:40683", "comp": "One-Day Cup 2026-27", "event": "Western Australia v New South Wales",
     "utc": "2026-10-24T06:00:00Z", "venue": "WACA Ground, Perth"},
    {"id": "CA:41095", "comp": "New Zealand v India T20Is 2026", "event": "New Zealand v India — 2nd T20I",
     "utc": "2026-10-24T07:00:00Z", "venue": "Hagley Oval, Christchurch"},
    {"id": "CA:40981", "comp": "Pakistan ODI Tri-Series 2026", "event": "Pakistan v England",
     "utc": "2026-10-25T08:00:00Z", "venue": "Gaddafi Stadium, Lahore"},
    {"id": "CA:41097", "comp": "New Zealand v India T20Is 2026", "event": "New Zealand v India — 3rd T20I",
     "utc": "2026-10-27T07:00:00Z", "venue": "Hnry Stadium, Wellington"},
]

# Events read live on an official feed as already started / completed, so they are
# excluded from pre-match pricing rather than quietly priced.
ELAPSED = [
    ("tennis", "Brussels QF — Francisco Cerundolo def. Clement Chidekh 6-2 6-4", "atp_brussels"),
    ("tennis", "Brussels QF — Tallon Griekspoor v Jiri Lehecka (in play at read time)", "atp_brussels"),
    ("tennis", "Lyon QF — Tommy Paul def. Corentin Moutet 6-4 3-6 6-3", "atp_lyon"),
    ("tennis", "Lyon QF — Daniel Altmaier v Taylor Fritz (in play at read time)", "atp_lyon"),
    ("tennis", "Almaty QF — Daniil Medvedev def. Terence Atmane 6-4 6-4", "atp_almaty"),
    ("tennis", "Almaty QF — Nikoloz Basilashvili def. Adrian Mannarino 6-3 6-1", "atp_almaty"),
    ("tennis", "Almaty QF — Stefanos Tsitsipas def. James Duckworth 6-3 6-4", "atp_almaty"),
    ("tennis", "Almaty QF — Alexander Bublik v Karen Khachanov (in play at read time)", "atp_almaty"),
    ("snooker", "NI Open QF — Kyren Wilson 6-1 Anthony McGill", "wst_draw"),
    ("snooker", "NI Open QF — Sam Craigie 6-2 Elliot Slessor", "wst_draw"),
    ("motor-racing", "United States GP — Practice 1 (13:30 local, 17:30Z)", "f1_event"),
    ("greyhounds", "Towcester 5:12 — shown Expired on the OLBG card at read time", "nhl_sched_23"),
]
