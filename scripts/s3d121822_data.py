"""Data for the 3d121822 desk (24 October 2026, 17:xx UTC).

Every value here was read during this session from a named source.  Fields
that could not be confirmed are left as None and published as blank plus a
review flag.  Nothing is inferred, interpolated or filled from memory.

Two kinds of source are used and never mixed:
  * OLBG public pages  -> discovery only (which events exist, market labels)
  * governing body / league / tour / club pages -> fact verification

All OLBG clock labels are reproduced exactly as displayed.  OLBG does not
publish a timezone on those cards, so no UTC conversion is attempted.
"""

OBSERVED = "2026-10-24T17:05:00Z"   # start of the live read block
OBSERVED_END = "2026-10-24T17:12:00Z"
DESK = "3d121822-olbg1"

# --------------------------------------------------------------------------
# Source ledger.  id -> (url, publisher, what it was used for, read at)
# --------------------------------------------------------------------------
SOURCES = {
    "olbg-golf": ("https://www.olbg.com/betting-tips/Golf/5", "OLBG", "Golf hub: no tips found", "2026-10-24T17:01:00Z"),
    "olbg-darts": ("https://www.olbg.com/betting-tips/Darts/15", "OLBG", "Darts fixtures and market labels", "2026-10-24T17:02:00Z"),
    "olbg-snooker": ("https://www.olbg.com/betting-tips/Snooker/8", "OLBG", "Snooker fixture and markets", "2026-10-24T17:03:00Z"),
    "olbg-basketball": ("https://www.olbg.com/betting-tips/Basketball/4", "OLBG", "Basketball fixtures and market labels", "2026-10-24T17:04:00Z"),
    "olbg-hockey": ("https://www.olbg.com/betting-tips/Ice_Hockey/13", "OLBG", "Ice hockey fixtures and market labels", "2026-10-24T17:05:00Z"),
    "olbg-baseball": ("https://www.olbg.com/betting-tips/Baseball/12", "OLBG", "Baseball fixture and market labels", "2026-10-24T17:06:00Z"),
    "olbg-tennis": ("https://www.olbg.com/betting-tips/Tennis/3", "OLBG", "Tennis fixtures and markets", "2026-10-24T17:07:00Z"),
    "olbg-rugbyu": ("https://www.olbg.com/betting-tips/Rugby_Union/9", "OLBG", "Rugby union fixtures and markets", "2026-10-24T17:08:00Z"),
    "olbg-cricket": ("https://www.olbg.com/betting-tips/Cricket/7", "OLBG", "Cricket fixtures and markets", "2026-10-24T17:08:30Z"),
    "olbg-handball": ("https://www.olbg.com/betting-tips/Handball/20", "OLBG", "Handball fixtures and markets", "2026-10-24T17:09:00Z"),
    "olbg-volleyball": ("https://www.olbg.com/betting-tips/Volleyball/21", "OLBG", "Volleyball fixtures and markets", "2026-10-24T17:09:30Z"),
    "olbg-gaelic": ("https://www.olbg.com/betting-tips/Gaelic_Football/25", "OLBG", "Gaelic football fixtures", "2026-10-24T17:10:00Z"),
    "olbg-greyhounds": ("https://www.olbg.com/betting-tips/Greyhounds/28", "OLBG", "Greyhound races", "2026-10-24T17:10:30Z"),
    "olbg-motor": ("https://www.olbg.com/betting-tips/Motor_Racing/14", "OLBG", "Motor racing fixture", "2026-10-24T17:11:00Z"),
    "olbg-rugbyl": ("https://www.olbg.com/betting-tips/Rugby_League/10", "OLBG", "Rugby league hub: outrights only", "2026-10-24T17:11:30Z"),
    "nba-standings": ("https://www.nba.com/standings", "NBA", "2026-27 regular-season win-loss records and streaks", "2026-10-24T17:09:00Z"),
    "nhl-score": ("https://api-web.nhle.com/v1/score/2026-10-24", "NHL", "24 Oct schedule, team records, published partner prices, UTC starts", "2026-10-24T17:07:00Z"),
    "nhl-standings": ("https://api-web.nhle.com/v1/standings/2026-10-24", "NHL", "Standings snapshot 17:05:30Z (first clubs read)", "2026-10-24T17:06:00Z"),
    "mlb-schedule": ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24&hydrate=team,linescore", "MLB", "World Series Game 2, start UTC, series state, ifNecessary flag", "2026-10-24T17:06:00Z"),
    "mlb-gameday": ("https://www.mlb.com/gameday/849802", "MLB", "Game 2 route for manual review", "2026-10-24T17:06:00Z"),
}

# --------------------------------------------------------------------------
# Official records used as pricing inputs.
# NBA: (wins, losses, streak, conference record, home, away) from nba.com/standings
# NHL: (wins, losses, ot losses) from api-web.nhle.com
# --------------------------------------------------------------------------
NBA = {
    "ATL Hawks":  (2, 0, "W2", "2-0", "0-0", "2-0"),
    "BKN Nets":   (0, 1, "L1", "0-1", "0-1", "0-0"),
    "CHA Hornets": (1, 1, "L1", "1-1", "0-1", "1-0"),
    "CHI Bulls":  (1, 1, "W1", "1-1", "0-0", "1-1"),
    "CLE Cavaliers": (0, 1, "L1", "0-1", "0-0", "0-1"),
    "DAL Mavericks": (1, 1, "W1", "0-1", "0-0", "1-1"),
    "DEN Nuggets": (0, 1, "L1", "0-1", "0-0", "0-1"),
    "GS Warriors": (0, 2, "L2", "0-2", "0-1", "0-1"),
    "HOU Rockets": (2, 0, "W2", "2-0", "1-0", "1-0"),
    "MIA Heat":   (0, 2, "L2", "0-1", "0-2", "0-0"),
    "MIL Bucks":  (0, 2, "L2", "0-2", "0-1", "0-1"),
    "NO Pelicans": (0, 2, "L2", "0-1", "0-1", "0-1"),
    "PHI 76ers":  (2, 0, "W2", "2-0", "1-0", "1-0"),
    "PHX Suns":   (0, 1, "L1", "0-0", "0-0", "0-1"),
    "SA Spurs":   (0, 2, "L2", "0-2", "0-2", "0-0"),
    "WAS Wizards": (1, 1, "L1", "1-1", "1-1", "0-0"),
}
NHL = {
    "ANA Ducks": (4, 6, 0),
    "PHI Flyers": (3, 6, 3),
    "LAK Kings": (2, 4, 2),
    "NJD Devils": (6, 4, 0),
}

# Published partner prices on the NHL score feed (providerId: 9=DraftKings, 7=FanDuel, 8=Sportradar).
NHL_PARTNER_ODDS = {
    "lak-njd": {"LAK Kings": ["+160 (DraftKings)", "+159 (Sportradar)"],
                "NJD Devils": ["-194 (DraftKings)", "-198 (FanDuel)", "-192 (Sportradar)"]},
    "ana-phi": {"ANA Ducks": ["+102 (DraftKings)", "+100 (FanDuel)", "-101 (Sportradar)"],
                "PHI Flyers": ["-122 (DraftKings)", "-120 (FanDuel)", "-122 (Sportradar)"]},
}

# --------------------------------------------------------------------------
# Golf has no OLBG tips at all today.
# --------------------------------------------------------------------------
SPORTS = [
    dict(
        key="golf", name="Golf", route="https://www.olbg.com/betting-tips/Golf/5",
        market_note="Tournament outright, first-round leader, top-region and team-event markets are the families OLBG lists for golf.",
        fixtures=[],
        gap="The OLBG golf hub returned 'No tips found' when read at 17:01Z on 24 Oct 2026. No golf event, field or price is invented to fill this page.",
    ),
    dict(
        key="volleyball", name="Volleyball", route="https://www.olbg.com/betting-tips/Volleyball/21",
        market_note="Win Match is the OLBG market label seen on every volleyball card.",
        fixtures=[
            ("vb-trentino", "SuperLega / club", "Trentino", "Cisterna", "Tomorrow 12:00",
             "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Trentino_vs_Cisterna/21?event_id=36994"),
            ("vb-perugia", "SuperLega / club", "Perugia", "Pordenone", "Tomorrow 13:00",
             "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Perugia_vs_Pordenone/21?event_id=36997"),
            ("vb-chelm", "PlusLiga / club", "CHKS Chelm", "Resovia Rzeszow", "Tomorrow 13:00",
             "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/CHKS_Chelm_vs_Resovia_Rzeszow/21?event_id=36965"),
            ("vb-brusque", "Brazil Superliga W", "Abel-Moda Brusque W", "Praia Clube W", "Today 20:00",
             "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Abel-Moda_Brusque_W_vs_Praia_Clube_W/21?event_id=37003"),
            ("vb-mackenzie", "Brazil Superliga W", "Mackenzie W", "Osasco W", "Today 15:00",
             "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Mackenzie_W_vs_Osasco_W/21?event_id=37002"),
        ],
        gap="No official league table or squad availability was captured for these clubs in this session, so no price is issued. League position, set ratio and injury reports are the missing inputs.",
    ),
    dict(
        key="rugby_union", name="Rugby Union", route="https://www.olbg.com/betting-tips/Rugby_Union/9",
        market_note="OLBG lists To Win plus handicap families for union; the cards captured here carried To Win.",
        fixtures=[
            ("ru-usa", "International", "USA", "Australia A", "Today 19:00",
             "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/USA_v_Australia_A/9?event_id=609583"),
            ("ru-quins", "Premiership", "Harlequins", "Saracens", "Tomorrow 11:00",
             "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Harlequins_v_Saracens/9?event_id=609571"),
            ("ru-larochelle", "Top 14", "La Rochelle", "Bordeaux", "Tomorrow 16:05",
             "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/La_Rochelle_v_Bordeaux/9?event_id=609554"),
            ("ru-ospreys", "United Rugby Championship", "Ospreys", "Dragons", "Today 14:00",
             "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Ospreys_v_Dragons/9?event_id=609581"),
            ("ru-toulon", "Top 14", "Toulon", "Pau", "Today 15:00",
             "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Toulon_v_Pau/9?event_id=609555"),
        ],
        gap="No official league table, team sheet or injury list was captured for these five fixtures, so no price is issued. Both sides must be priced from the same sourced table to avoid inventing a rating.",
    ),
    dict(
        key="cricket", name="Cricket", route="https://www.olbg.com/betting-tips/Cricket/7",
        market_note="Win Match, Draw No Bet, Top Team1 Batsman and Outright Winner all appear on the captured cricket cards.",
        fixtures=[
            ("cr-toronto", "T20 / Canada", "Toronto Kings", "Vancouver Guardians", "Today 19:00",
             "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Toronto_Kings_vs_Vancouver_Guardians_T20/7?event_id=188845"),
            ("cr-pakeng", "ODI", "Pakistan", "England", "Tomorrow 04:00",
             "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Pakistan_vs_England_One_Day_Match/7?event_id=188838"),
            ("cr-nzind", "T20 international", "New Zealand", "India", "27 Oct 03:00",
             "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/New_Zealand_vs_India_3rd_T20_Match/7?event_id=188852"),
            ("cr-tuskers", "T20 / South Africa", "Tuskers", "Western Province", "Tomorrow 07:00",
             "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Tuskers_vs_Western_Province_T20/7?event_id=188850"),
            ("cr-boland", "T20 / South Africa", "Boland", "Titans", "Tomorrow 07:00",
             "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Boland_vs_Titans_T20/7?event_id=188849"),
        ],
        gap="No official scorecard, squad list or toss/weather input was captured, so no price is issued. Cricket lines move with the XI, the surface and the weather; none of those three was confirmed here.",
    ),
    dict(
        key="snooker", name="Snooker", route="https://www.olbg.com/betting-tips/Snooker/8",
        market_note="OLBG lists Win Match, Handicap Betting, Frame Betting and Win Tournament for snooker.",
        fixtures=[
            ("sn-willjones", "Ranking event", "Mark Williams", "Jak Jones", "Today 14:05",
             "https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Mark_Williams_v_Jak_Jones/8?event_id=9952"),
        ],
        gap="One snooker card only, and no official ranking, frame-score or match-time input was captured. The card clock had passed when the page was read at 17:03Z, so it is listed for completeness and not priced.",
    ),
    dict(
        key="darts", name="Darts", route="https://www.olbg.com/betting-tips/Darts/15",
        market_note="Win Match 2-way and Win Tournament are the market labels on the captured darts cards.",
        fixtures=[
            ("da-price", "Win Match 2-way", "Gerwyn Price", "Stephen Bunting", "Tomorrow 07:00",
             "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Gerwyn_Price_vs_Stephen_Bunting/15?event_id=32407"),
            ("da-ratajski", "Win Match 2-way", "Krzysztof Ratajski", "Kevin Doets", "Today 13:15",
             "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Krzysztof_Ratajski_vs_Kevin_Doets/15?event_id=32399"),
            ("da-clayton", "Win Match 2-way", "Jonny Clayton", "Josh Rock", "Today 16:15",
             "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Jonny_Clayton_vs_Josh_Rock/15?event_id=32400"),
            ("da-aspinall", "Win Match 2-way", "Nathan Aspinall", "Luke Littler", "Today 15:15",
             "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Nathan_Aspinall_vs_Luke_Littler/15?event_id=32397"),
            ("da-schindler", "Win Match 2-way", "Martin Schindler", "Jermaine Wattimena", "Today 14:15",
             "https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Martin_Schindler_vs_Jermaine_Wattimena/15?event_id=32398"),
        ],
        gap="The official PDC pages did not return readable content in this session (cookie-consent shell), so no three-dart average, checkout percentage or ranking input is confirmed. The four 'Today' cards had also passed their listed clock by the time of reading.",
    ),
    dict(
        key="baseball", name="Baseball", route="https://www.olbg.com/betting-tips/Baseball/12",
        market_note="Money Line, Run Line and Game Totals are the three OLBG baseball markets.",
        fixtures=[
            ("bb-ws2", "MLB World Series, Game 2", "Tampa Bay Rays", "Milwaukee Brewers", "Today 20:00",
             "https://www.olbg.com/betting-tips/Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160792"),
        ],
        gap="Game 2 is confirmed by MLB (00:00Z on 25 Oct, American Family Field, ifNecessary=N, Milwaukee lead the series 1-0). Starting pitchers, season run rates and lineups were not captured, so no run line or total is issued.",
    ),
    dict(
        key="gaelic", name="Gaelic Sports", route="https://www.olbg.com/betting-tips/Gaelic_Football/25",
        market_note="Match odds and handicap (for example '+3.50') appear on the captured Gaelic cards.",
        fixtures=[
            ("ga-moycullen", "Club championship", "Moycullen", "Salthill-Knocknacarra", "Tomorrow 12:00",
             "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532"),
            ("ga-finbarrs", "Club championship", "St Finbarrs", "Nemo Rangers", "Tomorrow 12:00",
             "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530"),
            ("ga-kanturk", "Club championship", "Kanturk", "Eire Og Cor", "01 Nov 09:00",
             "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Kanturk_v_Eire_Og_Cor/25?event_id=3531"),
            ("ga-frcaseys", "Club championship", "Fr Caseys", "Kildimo Pallaskenry", "01 Nov 10:30",
             "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Fr_Caseys_v_Kildimo_Pallaskenry/25?event_id=3537"),
        ],
        gap="No official GAA club fixture list, league placing or panel news was captured for these four ties, so no price is issued.",
    ),
    dict(
        key="greyhounds", name="Greyhounds", route="https://www.olbg.com/betting-tips/Greyhounds/28",
        market_note="'Daily Races' is the only market label on the captured greyhound cards.",
        fixtures=[
            ("gh-newcastle", "Newcastle 6:01", "Blackhouseharley", "field", "Today 13:01",
             "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/6:01_Newcastle/28?event_id=689950"),
            ("gh-monmore", "Monmore 8:54", "Crossfield Jess", "field", "Today 15:54",
             "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/8:54_Monmore/28?event_id=690013"),
            ("gh-dunstall", "Dunstall Park 10:14", "Greenwell Gypsy", "field", "Today 17:14",
             "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/10:14_Dunstall_Park/28?event_id=690035"),
            ("gh-doncaster", "Doncaster 7:58", "Lady Gambet", "field", "Today 14:58",
             "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/7:58_Doncaster/28?event_id=689890"),
            ("gh-central", "Central Park 6:30", "One More Tune", "field", "Today 13:30",
             "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/6:30_Central_Park/28?event_id=689957"),
        ],
        gap="GBGB publishes the regulatory register, not a form card. No trap draw, sectional time, going or starting-price input was captured, so no runner is priced. A dog name is not a form line.",
    ),
    dict(
        key="tennis", name="Tennis", route="https://www.olbg.com/betting-tips/Tennis/3",
        market_note="Win Match, Set Betting, Total Games, 1st Set Winner and Games Won are the OLBG tennis families.",
        fixtures=[
            ("tn-krueger", "WTA", "Ashlyn Krueger", "Katerina Siniakova", "Tomorrow 00:30",
             "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Ashlyn_Krueger_vs_Katerina_Siniakova/3?event_id=902171"),
            ("tn-rybakina", "WTA", "Elena Rybakina", "Leylah Fernandez", "Tomorrow 05:00",
             "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Elena_Rybakina_vs_Leylah_Fernandez/3?event_id=902207"),
            ("tn-medvedev", "ATP", "Daniil Medvedev", "Nikoloz Basilashvili", "Tomorrow 06:00",
             "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Daniil_Medvedev_vs_Nikoloz_Basilashvili/3?event_id=902251"),
            ("tn-eala", "WTA", "Alexandra Eala", "Mika Stojsavljevic", "26 Oct 22:00",
             "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Alexandra_Eala_vs_Mika_Stojsavljevic/3?event_id=902175"),
            ("tn-uchijima", "WTA", "Moyuka Uchijima", "Elise Mertens", "26 Oct 22:00",
             "https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Moyuka_Uchijima_vs_Elise_Mertens/3?event_id=902173"),
        ],
        gap="No official ATP or WTA ranking snapshot, service or return statistic, or withdrawal note was captured for these players, so no match price is issued. The tournament name is also absent from the OLBG cards, so it is left blank rather than guessed.",
    ),
    dict(
        key="motor_racing", name="Motor Racing", route="https://www.olbg.com/betting-tips/Motor_Racing/14",
        market_note="Win Race, Fastest Qualifier, Podium, Top 6, Points Finish, Fastest Lap and outright championship markets are listed by OLBG.",
        fixtures=[
            ("mr-usa", "Formula 1, USA Grand Prix", "Max Verstappen (win race)", "field", "Tomorrow 16:00",
             "https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/USA_Grand_Prix/14?event_id=913"),
        ],
        gap="One race card, priced as a win-race market. No official entry list, grid, championship points or practice times were captured, so no race price is issued.",
    ),
    dict(
        key="handball", name="Handball", route="https://www.olbg.com/betting-tips/Handball/20",
        market_note="Money Line is the OLBG label; tie is offered as an outcome, so this is a three-way market.",
        fixtures=[
            ("hb-granollers", "Liga ASOBAL", "BM Granollers", "Angel Ximenez Puente Genil", "Tomorrow 07:30",
             "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/BM_Granollers_vs_Angel_Ximenez_Puente_Genil/20?event_id=12102"),
            ("hb-rnl", "Handball-Bundesliga", "Rhein Neckar Lowen", "SC Magdeburg", "Tomorrow 10:00",
             "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Rhein_Neckar_Lowen_vs_SC_Magdeburg/20?event_id=12092"),
            ("hb-torrelavega", "Liga ASOBAL", "BM Torrelavega", "BM Proin", "Tomorrow 13:00",
             "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/BM_Torrelavega_vs_BM_Proin/20?event_id=12105"),
            ("hb-saintraphael", "Liqui Moly StarLigue", "Saint Raphael", "PSG Handball", "Tomorrow 11:00",
             "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Saint_Raphael_vs_PSG_Handball/20?event_id=12084"),
            ("hb-kielce", "EHF Champions League", "KS Kielce", "Kolstad", "28 Oct 15:45",
             "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/KS_Kielce_vs_Kolstad/20?event_id=12132"),
        ],
        gap="No official HBL, ASOBAL, StarLigue or EHF table was captured, so no three-way price is issued. A handball tie outcome cannot be priced without a goal-difference distribution from sourced scoring rates.",
    ),
    dict(
        key="basketball", name="Basketball", route="https://www.olbg.com/betting-tips/Basketball/4",
        market_note="Money Line and Pointspread are the OLBG basketball labels; both are offered on the captured NBA cards.",
        fixtures=[
            ("bk-hou-atl", "NBA", "HOU Rockets", "ATL Hawks", "Today 20:30",
             "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/HOU_Rockets_@_ATL_Hawks/4?event_id=536115"),
            ("bk-bkn-cle", "NBA", "BKN Nets", "CLE Cavaliers", "Today 19:30",
             "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/BKN_Nets_@_CLE_Cavaliers/4?event_id=536112"),
            ("bk-mil-phi", "NBA", "MIL Bucks", "PHI 76ers", "Today 19:30",
             "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIL_Bucks_@_PHI_76ers/4?event_id=536111"),
            ("bk-sa-dal", "NBA", "SA Spurs", "DAL Mavericks", "Today 20:00",
             "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/SA_Spurs_@_DAL_Mavericks/4?event_id=536114"),
            ("bk-was-chi", "NBA", "WAS Wizards", "CHI Bulls", "Today 20:00",
             "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/WAS_Wizards_@_CHI_Bulls/4?event_id=536113"),
            ("bk-no-den", "NBA", "NO Pelicans", "DEN Nuggets", "Today 22:00",
             "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/NO_Pelicans_@_DEN_Nuggets/4?event_id=536116"),
            ("bk-gs-phx", "NBA", "GS Warriors", "PHX Suns", "Today 23:00",
             "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/GS_Warriors_@_PHX_Suns/4?event_id=536118"),
            ("bk-mia-cha", "NBA", "MIA Heat", "CHA Hornets", "Today 18:00",
             "https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIA_Heat_@_CHA_Hornets/4?event_id=536117"),
        ],
        gap="Eight NBA cards are priced from the official NBA win-loss table. Point totals are withheld because no sourced season scoring rate exists yet, and injury reports were not captured.",
    ),
    dict(
        key="ice_hockey", name="Ice Hockey", route="https://www.olbg.com/betting-tips/Ice_Hockey/13",
        market_note="Money Line and Game Totals are the OLBG labels; the NHL feed also publishes partner prices.",
        fixtures=[
            ("ih-lak-njd", "NHL", "LAK Kings", "NJD Devils", "Today 15:37",
             "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/LAK_Kings_@_NJ_Devils/13?event_id=200000",
             "2026-10-24T19:30:00Z"),
            ("ih-car-stl", "NHL", "CAR Hurricanes", "STL Blues", "Today 19:07",
             "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/CAR_Hurricanes_@_STL_Blues/13?event_id=200002"),
            ("ih-nyr-ott", "NHL", "NY Rangers", "OTT Senators", "Today 19:07",
             "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/NY_Rangers_@_OTT_Senators/13?event_id=200008"),
            ("ih-sj-bos", "NHL", "SJ Sharks", "BOS Bruins", "Today 19:07",
             "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/SJ_Sharks_@_BOS_Bruins/13?event_id=200007"),
            ("ih-tor-edm", "NHL", "TOR Maple Leafs", "EDM Oilers", "Today 19:07",
             "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/TOR_Maple_Leafs_@_EDM_Oilers/13?event_id=200010"),
        ],
        gap="Only the NJD game and its four clubs' records were confirmed on the NHL feed before this session's reading budget ran out. The other four NHL cards are listed with their OLBG links and left unpriced rather than guessed.",
    ),
    dict(
        key="rugby_league", name="Rugby League", route="https://www.olbg.com/betting-tips/Rugby_League/10",
        market_note="To Win, handicap and Grand Final Winner markets are listed.",
        fixtures=[],
        gap="No upcoming rugby league match was on the OLBG hub at 17:11Z: the page carried only outright markets (State of Origin 2027, Super League 2027, NRL 2027). A 2027 futures market is not an upcoming match, so nothing is listed as one.",
    ),
]

# --------------------------------------------------------------------------
# Written predictions.  One per published selection, unique wording, 30+ words.
# Every factual clause below maps to an entry in the fixture's evidence list.
# --------------------------------------------------------------------------
PREDICTIONS = {
    "ih-lak-njd": dict(
        selection="New Jersey Devils to win (moneyline, include overtime and shootout)",
        text=("New Jersey Devils to win in New Jersey. The Devils are 6-4-0 through ten games, "
              "a .600 points rate, while Los Angeles arrive at 2-4-2 after eight games and have "
              "won only twice. New Jersey's twelve points from ten starts is double the Kings' "
              "six from eight, and the NHL's own published partner prices make New Jersey "
              "around -194, which sits with that gap. Goaltender confirmation and the injured "
              "list were not captured and are left blank."),
        evidence=["nhl-score", "nhl-standings", "olbg-hockey"],
    ),
    "bk-mil-phi": dict(
        selection="Philadelphia 76ers to win (moneyline)",
        text=("Philadelphia 76ers to win. Philadelphia are 2-0 after two wins, with a 2-0 "
              "conference record and a 1-0 mark at home, while Milwaukee are 0-2, have lost two "
              "straight and are 0-2 against Eastern Conference opponents. Two games is a thin "
              "sample, so the edge is real but modest, and the price should not be treated as a "
              "mismatch. Injury reports for both rosters were not captured and remain blank."),
        evidence=["nba-standings", "olbg-basketball"],
    ),
    "bk-sa-dal": dict(
        selection="Dallas Mavericks to win (moneyline)",
        text=("Dallas Mavericks to win. Dallas are 1-1 and won their most recent game, while San "
              "Antonio are 0-2, have lost twice in a row and are 0-2 inside the Western "
              "Conference. The Spurs have also played both of their games at home, so this is "
              "their first road trip of the season. One game separates the two records, which "
              "keeps this a low-conviction call rather than a strong one."),
        evidence=["nba-standings", "olbg-basketball"],
    ),
    "bk-no-den": dict(
        selection="Denver Nuggets to win (moneyline)",
        text=("Denver Nuggets to win. Denver are 0-1 after a single road defeat, while New Orleans "
              "are 0-2 and have lost both games, including one at home. The Pelicans are 0-1 in "
              "conference play and have not yet won. Because both teams have played one or two "
              "games, the records carry very little weight and this selection is the weakest on "
              "the card."),
        evidence=["nba-standings", "olbg-basketball"],
    ),
    "bk-gs-phx": dict(
        selection="Phoenix Suns to win (moneyline)",
        text=("Phoenix Suns to win. Phoenix are 0-1 after a single road game, while Golden State "
              "are 0-2 with two straight defeats and an 0-2 conference record. The Warriors have "
              "lost once at home and once on the road, so there is no venue pattern to lean on. "
              "Both samples are tiny, which is why this is published as a low-conviction call."),
        evidence=["nba-standings", "olbg-basketball"],
    ),
}

# Fixtures we deliberately refuse to price, with the reason a reader can check.
FLAGS = [
    ("F-3D-01", "high", "Golf", "No OLBG tips, no fixture",
     "The golf hub returned 'No tips found' at 17:01Z. Nothing is listed rather than inventing a tournament.",
     "olbg-golf"),
    ("F-3D-02", "high", "Rugby League", "Outright markets only",
     "The rugby league hub carried only 2027 futures at 17:11Z. Futures are not upcoming matches.",
     "olbg-rugbyl"),
    ("F-3D-03", "high", "Darts", "No official player data captured",
     "pdc.tv returned a cookie-consent shell instead of tournament or ranking content, so no three-dart average or ranking input exists. OLBG tip shares are votes, not probabilities, and were not used.",
     "olbg-darts"),
    ("F-3D-04", "high", "All sports", "OLBG clock has no timezone",
     "OLBG cards print a clock but no timezone. No UTC conversion is attempted; UTC is published only where the league feed supplies it. Four darts cards and one snooker card had passed their listed clock at reading time.",
     "olbg-darts"),
    ("F-3D-05", "high", "Ice Hockey", "Four NHL cards unpriced",
     "Only LAK@NJD had both club records read. CAR, STL, NYR, OTT, SJ, BOS, TOR and EDM records were not read, so those four cards carry no price.",
     "nhl-score"),
    ("F-3D-06", "medium", "Basketball", "Point totals withheld",
     "No official 2026-27 team scoring rate exists after one or two games, so no total is issued. Moneyline and pointspread only.",
     "nba-standings"),
    ("F-3D-07", "medium", "All priced fixtures", "Injuries not captured",
     "No injury, suspension or lineup report was read for any priced fixture. The predictions say so instead of implying a fully fit squad.",
     "olbg-basketball"),
    ("F-3D-08", "medium", "Baseball", "World Series Game 2 unpriced",
     "MLB confirms the game (00:00Z on 25 Oct, ifNecessary=N, Milwaukee 1-0 up). Starting pitchers and season run rates were not captured, so no run line or total is issued.",
     "mlb-schedule"),
    ("F-3D-09", "medium", "Confidence window", "Zero High picks published",
     "The brief asks for High picks at >70% probability inside a -250 to +10000 price band. That band's short end is -250 = 71.4%, so High lives in a 1.4-point sliver. Today's strongest selection, New Jersey at about 72.7%, prices at roughly -267 and therefore sits outside the stated window; it is published as Medium with the arithmetic shown, not relabelled.",
     "nhl-score"),
    ("F-3D-10", "low", "Handball, Volleyball, Tennis, Cricket, Gaelic, Greyhounds",
     "Fixtures listed, prices withheld",
     "Official tables, rankings and availability were not captured for these six sports in this session. Each sport page names the missing input for every fixture.",
     "olbg-handball"),
]


def fixture_rows():
    """Flatten the sport fixture tuples into dicts."""
    out = []
    for sport in SPORTS:
        for row in sport["fixtures"]:
            fid, comp, a, b, ko, url = row[:6]
            utc = row[6] if len(row) > 6 else None
            out.append(dict(id=fid, sport=sport["key"], sport_name=sport["name"],
                            comp=comp, a=a, b=b, ko=ko, utc=utc, olbg=url))
    return out
