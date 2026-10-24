"""Session f437fb14 - discovery rows for the remaining twelve sports.

These rows come from the OLBG sport hubs read this session. They are DISCOVERY rows:
OLBG is a tipster aggregator, not a governing body, so nothing here is treated as a
verified fixture fact. Each row keeps its OLBG link plus the official page that was
attempted; where that official page returned no fixture data the row stays
`verify="discovery"`, publishes blank time in the official column, and is flagged.

Times: OLBG prints US Eastern. `start_utc` is the ET reading converted to UTC
(EDT = UTC-4 on 24-25 October 2026). The conversion is recorded, not hidden.
"""

TENNIS_SRC = "https://www.wtatennis.com/tournaments/1056/tokyo/2026/draws"
CRICKET_SRC = "https://www.icc-cricket.com/"
SNOOKER_SRC = "https://www.wst.tv/matches/"
DARTS_SRC = "https://www.pdc.tv/tournaments/european-championship"
RU_SRC = "https://www.premiershiprugby.com/fixtures"
RL_SRC = "https://www.rugby-league.com/"
VOLLEY_SRC = "https://www.legavolley.it/classifica/"
HANDBALL_SRC = "https://ehfcl.eurohandball.com/en/men/"
GAA_SRC = "https://www.gaa.ie/fixtures-results/"
DOG_SRC = "https://www.gbgb.org.uk/"
F1_SRC = "https://www.formula1.com/en/racing/2026/united-states"
GOLF_SRC = "https://www.pgatour.com/schedule"

OLBG = {
    "Tennis": "https://www.olbg.com/betting-tips/Tennis/3",
    "Cricket": "https://www.olbg.com/betting-tips/Cricket/7",
    "Snooker": "https://www.olbg.com/betting-tips/Snooker/8",
    "Darts": "https://www.olbg.com/betting-tips/Darts/15",
    "Rugby Union": "https://www.olbg.com/betting-tips/Rugby_Union/9",
    "Rugby League": "https://www.olbg.com/betting-tips/Rugby_League/10",
    "Volleyball": "https://www.olbg.com/betting-tips/Volleyball/21",
    "Handball": "https://www.olbg.com/betting-tips/Handball/20",
    "Gaelic Sports": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
    "Greyhounds": "https://www.olbg.com/betting-tips/Greyhounds/28",
    "Motor Racing": "https://www.olbg.com/betting-tips/Motor_Racing/14",
    "Golf": "https://www.olbg.com/betting-tips/Golf/5",
}


def _row(fid, sport, comp, home, away, utc, et, verify="discovery", official=None, note=""):
    return dict(id=fid, sport=sport, competition=comp, home=home, away=away,
                start_utc=utc, time_source="olbg-et" if utc else None, et=et,
                olbg_url=OLBG[sport], official_url=official,
                verify=verify, note=note)


TENNIS = [
    _row("TN-01", "Tennis", "WTA Tokyo (Toray Pan Pacific Open)", "Elena Rybakina", "Leylah Fernandez",
         "2026-10-25T09:00:00Z", "Sun 05:00", official=TENNIS_SRC,
         note="OLBG lists this under All Tennis with no tournament tag; Tokyo is the WTA event "
              "whose draw was released ~11h before the read, but the draw page returned no readable "
              "match list, so the link between this match and Tokyo is unconfirmed."),
    _row("TN-02", "Tennis", "WTA Tokyo (Toray Pan Pacific Open)", "Ashlyn Krueger", "Katerina Siniakova",
         "2026-10-25T04:30:00Z", "Sun 00:30", official=TENNIS_SRC),
    _row("TN-03", "Tennis", "ATP (tournament not stated by OLBG)", "Daniil Medvedev", "Nikoloz Basilashvili",
         "2026-10-25T10:00:00Z", "Sun 06:00", official="https://www.atptour.com/en/scores/current",
         note="atptour.com/en/scores/current/united-states/0930/scores returned a 404 body; the "
              "correct event route for this match was not found."),
    _row("TN-04", "Tennis", "WTA Tokyo (Toray Pan Pacific Open)", "Alexandra Eala", "Mika Stojsavljevic",
         "2026-10-27T02:00:00Z", "26 Oct 22:00", official=TENNIS_SRC),
    _row("TN-05", "Tennis", "WTA Tokyo (Toray Pan Pacific Open)", "Moyuka Uchijima", "Elise Mertens",
         "2026-10-27T02:00:00Z", "26 Oct 22:00", official=TENNIS_SRC),
    _row("TN-06", "Tennis", "WTA Tokyo (Toray Pan Pacific Open)", "Leylah Fernandez", "Himeno Sakatsume",
         "2026-10-27T02:00:00Z", "26 Oct 22:00", official=TENNIS_SRC,
         note="Fernandez also appears on 25 Oct versus Rybakina (TN-01). Two fixtures for one player "
              "inside 48 hours is possible on a 32-draw but is flagged for confirmation."),
]

CRICKET = [
    _row("CR-01", "Cricket", "Global T20 (Canada)", "Toronto Kings", "Vancouver Guardians T20",
         "2026-10-24T23:00:00Z", "Today 19:00", official=CRICKET_SRC),
    _row("CR-02", "Cricket", "ODI", "Pakistan", "England",
         "2026-10-25T08:00:00Z", "Sun 04:00", official="https://www.pcb.com.pk/"),
    _row("CR-03", "Cricket", "CSA T20 Challenge", "North West Dragons", "Northern Cape Heat",
         "2026-10-25T11:00:00Z", "Sun 07:00", official="https://cricket.co.za/"),
    _row("CR-04", "Cricket", "CSA T20 Challenge", "Tuskers", "Western Province",
         "2026-10-25T11:00:00Z", "Sun 07:00", official="https://cricket.co.za/"),
    _row("CR-05", "Cricket", "T20 International", "New Zealand", "India",
         "2026-10-27T07:00:00Z", "27 Oct 03:00", official="https://www.nzc.nz/",
         note="OLBG titles this the 3rd T20 of the series."),
    _row("CR-06", "Cricket", "ODI (women)", "India W", "Zimbabwe W",
         "2026-10-25T08:30:00Z", "Sun 04:30", official="https://www.bcci.tv/",
         note="OLBG titles this the 2nd ODI of the series."),
    _row("CR-07", "Cricket", "CSA T20 Challenge", "Eastern Storm", "South Africa Emerging",
         "2026-10-25T11:00:00Z", "Sun 07:00", official="https://cricket.co.za/"),
    _row("CR-08", "Cricket", "CSA T20 Challenge", "Boland", "Titans",
         "2026-10-25T11:00:00Z", "Sun 07:00", official="https://cricket.co.za/"),
    _row("CR-09", "Cricket", "Tour match", "South Africa", "Australia",
         "2026-10-31T08:30:00Z", "31 Oct 04:30", official="https://cricket.co.za/"),
]

# Snooker is the one sport besides hockey/baseball where an official page DID confirm the
# fixture. WST prints local UK time (BST = UTC+1 on 24-25 October 2026).
SNOOKER = [
    dict(id="SN-01", sport="Snooker", competition="BetVictor Northern Ireland Open 2026 - Semi-Final",
         home="Mark Williams", away="Jak Jones", start_utc="2026-10-24T13:00:00Z",
         time_source="official", et="Sat 14:00 UK", olbg_url=OLBG["Snooker"],
         official_url=SNOOKER_SRC, verify="verified", state="LIVE at read time",
         note="wst.tv lists this as Match 62, Saturday 24 October 14:00, marked Live Now. "
              "It has already started, so no pre-match selection is published against it."),
    dict(id="SN-02", sport="Snooker", competition="BetVictor Northern Ireland Open 2026 - Final",
         home="Kyren Wilson", away="Winner of Match 62", start_utc="2026-10-25T07:00:00Z",
         time_source="official", et="Sun 08:00 UK", olbg_url=OLBG["Snooker"],
         official_url=SNOOKER_SRC, verify="partial", state="Scheduled",
         note="wst.tv lists Kyren Wilson against 'Winner of match 62'. One side is undecided, so a "
              "two-way price cannot be originated without inventing the opponent."),
]

DARTS = [
    _row("DA-01", "Darts", "PDC European Championship", "Martin Schindler", "Jermaine Wattimena",
         "2026-10-24T18:15:00Z", "Today 14:15", official=DARTS_SRC),
    _row("DA-02", "Darts", "PDC European Championship", "Nathan Aspinall", "Luke Littler",
         "2026-10-24T19:15:00Z", "Today 15:15", official=DARTS_SRC),
    _row("DA-03", "Darts", "PDC European Championship", "Jonny Clayton", "Josh Rock",
         "2026-10-24T20:15:00Z", "Today 16:15", official=DARTS_SRC),
    _row("DA-04", "Darts", "PDC European Championship", "Gerwyn Price", "Stephen Bunting",
         "2026-10-25T11:00:00Z", "Sun 07:00", official=DARTS_SRC),
]

RUGBY_UNION = [
    _row("RU-01", "Rugby Union", "United Rugby Championship", "Ospreys", "Dragons",
         "2026-10-24T18:00:00Z", "Today 14:00", official=RU_SRC),
    _row("RU-02", "Rugby Union", "Top 14", "Toulon", "Pau",
         "2026-10-24T19:00:00Z", "Today 15:00", official="https://www.lnr.fr/"),
    _row("RU-03", "Rugby Union", "International", "USA", "Australia A",
         "2026-10-24T23:00:00Z", "Today 19:00", official=RU_SRC),
    _row("RU-04", "Rugby Union", "Premiership Rugby", "Harlequins", "Saracens",
         "2026-10-25T15:00:00Z", "Sun 11:00", official=RU_SRC),
    _row("RU-05", "Rugby Union", "Top 14", "La Rochelle", "Bordeaux",
         "2026-10-25T20:05:00Z", "Sun 16:05", official="https://www.lnr.fr/"),
]

VOLLEYBALL = [
    _row("VB-01", "Volleyball", "Austrian league (women)", "UVC Graz W", "Sportunion St Polten W",
         "2026-10-24T18:00:00Z", "Today 14:00"),
    _row("VB-02", "Volleyball", "Polish Tauron Liga (women)", "Mogilno W", "Chemik Police W",
         "2026-10-24T18:30:00Z", "Today 14:30", official="https://www.plusliga.pl/"),
    _row("VB-03", "Volleyball", "Brazilian Superliga (women)", "Mackenzie W", "Osasco W",
         "2026-10-24T19:00:00Z", "Today 15:00", official="https://www.cbv.com.br/"),
    _row("VB-04", "Volleyball", "Brazilian Superliga (women)", "Abel-Moda Brusque W", "Praia Clube W",
         "2026-10-25T00:00:00Z", "Today 20:00", official="https://www.cbv.com.br/"),
    _row("VB-05", "Volleyball", "Italian SuperLega", "Itas Trentino", "Cisterna Volley",
         "2026-10-25T16:00:00Z", "Sun 12:00", official=VOLLEY_SRC),
    _row("VB-06", "Volleyball", "Polish PlusLiga", "CHKS Chelm", "Resovia Rzeszow",
         "2026-10-25T17:00:00Z", "Sun 13:00", official="https://www.plusliga.pl/"),
    _row("VB-07", "Volleyball", "Italian SuperLega", "Sir Susa Scai Perugia", "Tinet Prata di Pordenone",
         "2026-10-25T17:00:00Z", "Sun 13:00", official=VOLLEY_SRC),
    _row("VB-08", "Volleyball", "Italian SuperLega", "Cucine Lube Civitanova", "Pallavolo Padova",
         "2026-10-25T17:00:00Z", "Sun 13:00", official=VOLLEY_SRC),
    _row("VB-09", "Volleyball", "Dutch Eredivisie (women)", "Sliedrecht W", "Apollo 8 W",
         "2026-10-24T18:00:00Z", "Today 14:00"),
    _row("VB-10", "Volleyball", "Dutch Eredivisie (women)", "VV Utrecht W", "Dynamo Apeldoorn W",
         "2026-10-24T18:00:00Z", "Today 14:00"),
    _row("VB-11", "Volleyball", "French Ligue A", "Royan", "Tours",
         "2026-10-24T18:00:00Z", "Today 14:00"),
    _row("VB-12", "Volleyball", "French Ligue A (women)", "Nantes W", "Terville Florange W",
         "2026-10-24T18:00:00Z", "Today 14:00"),
    _row("VB-13", "Volleyball", "Italian Serie A1 (women)", "Talmassons W", "Chieri W",
         "2026-10-24T18:45:00Z", "Today 14:45"),
    _row("VB-14", "Volleyball", "German Bundesliga (women)", "ETV Hamburg W", "Munster W",
         "2026-10-25T14:30:00Z", "Sun 10:30"),
]

HANDBALL = [
    _row("HB-01", "Handball", "German Bundesliga", "HBW Balingen Weilstetten", "MT Melsungen",
         "2026-10-24T18:00:00Z", "Today 14:00", official=HANDBALL_SRC),
    _row("HB-02", "Handball", "Spanish Liga ASOBAL", "BM Granollers", "Angel Ximenez Puente Genil",
         "2026-10-25T11:30:00Z", "Sun 07:30", official="https://www.asobal.es/"),
    _row("HB-03", "Handball", "German Bundesliga", "Rhein Neckar Lowen", "SC Magdeburg",
         "2026-10-25T14:00:00Z", "Sun 10:00", official="https://www.dhb.de/"),
    _row("HB-04", "Handball", "International (women)", "Luxembourg W", "Great Britain W",
         "2026-10-25T15:00:00Z", "Sun 11:00", official="https://www.eurohandball.com/"),
    _row("HB-05", "Handball", "French LNH", "Saint Raphael", "PSG Handball",
         "2026-10-25T15:00:00Z", "Sun 11:00", official="https://www.lnh.fr/"),
    _row("HB-06", "Handball", "Spanish Liga ASOBAL", "BM Torrelavega", "BM Proin",
         "2026-10-25T17:00:00Z", "Sun 13:00", official="https://www.asobal.es/"),
    _row("HB-07", "Handball", "EHF Champions League", "SC Magdeburg", "HC Kriens Luzern",
         "2026-10-28T19:45:00Z", "28 Oct 15:45", official=HANDBALL_SRC),
    _row("HB-08", "Handball", "EHF Champions League", "HC Vardar", "MT Melsungen",
         "2026-10-28T17:45:00Z", "28 Oct 13:45", official=HANDBALL_SRC),
    _row("HB-09", "Handball", "EHF Champions League", "KS Kielce", "Kolstad",
         "2026-10-28T19:45:00Z", "28 Oct 15:45", official=HANDBALL_SRC),
    _row("HB-10", "Handball", "EHF Champions League", "GOG", "Sporting CP",
         "2026-10-29T17:45:00Z", "29 Oct 13:45", official=HANDBALL_SRC),
    _row("HB-11", "Handball", "EHF Champions League", "Fuchse Berlin", "RK Partizan",
         "2026-10-29T17:45:00Z", "29 Oct 13:45", official=HANDBALL_SRC),
    _row("HB-12", "Handball", "Swedish Handbollsligan", "Ystads IF HF", "Hammarby IF HF",
         "2026-10-25T13:00:00Z", "Sun 09:00"),
]

GAELIC = [
    _row("GA-01", "Gaelic Sports", "Galway SFC", "Moycullen", "Salthill-Knocknacarra",
         "2026-10-25T16:00:00Z", "Sun 12:00", official=GAA_SRC,
         note="gaa.ie/fixtures-results listed only the Shinty-Hurling International on 24 October; "
              "club championship fixtures are not published on the national site."),
    _row("GA-02", "Gaelic Sports", "Cork SFC", "St Finbarrs", "Nemo Rangers",
         "2026-10-25T16:00:00Z", "Sun 12:00", official=GAA_SRC),
    _row("GA-03", "Gaelic Sports", "Cork Premier IFC", "Kanturk", "Eire Og Cor",
         "2026-11-01T14:00:00Z", "01 Nov 09:00", official=GAA_SRC),
    _row("GA-04", "Gaelic Sports", "Limerick SFC", "Fr Caseys", "Kildimo Pallaskenry",
         "2026-11-01T15:30:00Z", "01 Nov 10:30", official=GAA_SRC),
]

# Greyhounds: OLBG prints the race name in UK track clock and the "Today" column in ET.
# The pair is consistent (UK clock = ET + 5h during BST). Dog names are the OLBG most-tipped
# runner, not a verified betting selection.
_DOGS = [
    ("GR-01", "6:42 Romford", "Today 13:42", "Snoopys Star", "expired"),
    ("GR-02", "6:46 Doncaster", "Today 13:46", "Headford Asher", "open"),
    ("GR-03", "6:50 Central Park", "Today 13:50", "Clairekeith Mary", "open"),
    ("GR-04", "6:54 Monmore", "Today 13:54", "Son Of Thor", "open"),
    ("GR-05", "6:56 Star Pelaw", "Today 13:56", "Loxleys Ace", "open"),
    ("GR-06", "6:58 Dunstall Park", "Today 13:58", "Millbank Got It", "open"),
    ("GR-07", "7:02 Romford", "Today 14:02", "Noreason Amelia", "open"),
    ("GR-08", "7:04 Doncaster", "Today 14:04", "Salems Brianna", "open"),
    ("GR-09", "7:08 Yarmouth", "Today 14:08", "Peppered Bedlam", "open"),
    ("GR-10", "7:10 Central Park", "Today 14:10", "Bubbly Everest", "open"),
    ("GR-11", "7:58 Doncaster", "Today 14:58", "Lady Gambet", "open"),
    ("GR-12", "8:54 Monmore", "Today 15:54", "Crossfield Jess", "open"),
    ("GR-13", "9:14 Monmore", "Today 16:14", "Skylars Vision", "open"),
    ("GR-14", "9:18 Dunstall Park", "Today 16:18", "Avarua Lake", "open"),
    ("GR-15", "10:14 Dunstall Park", "Today 17:14", "Greenwell Gypsy", "open"),
]
GREYHOUNDS = []
for _i, (_id, _race, _et, _dog, _state) in enumerate(_DOGS):
    _track = _race.split(" ", 1)[1]
    _hhmm = _race.split(" ", 1)[0]
    _h, _m = (int(x) for x in _hhmm.split(":"))
    GREYHOUNDS.append(dict(
        id=_id, sport="Greyhounds", competition=f"Daily card - {_track}",
        home=f"{_dog} (most-tipped runner)", away=f"{_race} at {_track}",
        start_utc=None, time_source="olbg-et", et=_et,
        race_clock_uk=_race, dog=_dog, state=_state,
        olbg_url=OLBG["Greyhounds"], official_url=DOG_SRC, verify="discovery",
        note="Runner list, trap draw and going were not readable from an official source, so no "
             "price and no selection are published for this race."))

MOTOR_RACING = [
    dict(id="MR-01", sport="Motor Racing", competition="Formula 1 - MSC Cruises United States Grand Prix 2026",
         home="Circuit of The Americas, Austin", away="Race (Round 19 of the 2026 season)",
         start_utc="2026-10-25T21:00:00Z", time_source="official",
         et="Sun 16:00 track time (CDT)", olbg_url=OLBG["Motor Racing"],
         official_url=F1_SRC, verify="verified", state="Scheduled",
         facts=[
             "formula1.com race hub: Race on 25 Oct at 16:00 track time; Qualifying 24 Oct 17:00-18:00; "
             "FP1 and FP2 on 23 Oct both completed.",
             "Circuit of The Americas: 5.513 km, 56 laps, 308.432 km race distance.",
             "FP2 classification read from the hub: 1 Leclerc 1:35.291, 2 Antonelli +0.042, "
             "3 Verstappen +0.189, 4 Hamilton +0.615, 5 Russell +0.744.",
             "The FP1 report headline on formula1.com reads 'Leclerc fastest in first practice ... "
             "ahead of Verstappen and Norris'.",
         ],
         note="OLBG prints 'Tomorrow 16:00'; the official hub times the race at 16:00 track time "
              "(CDT), which is 21:00Z. OLBG's clock is treated as an ET reading and flagged."),
]

GOLF_NOTE = ("OLBG's Golf hub returned 'No tips found.' at 17:45Z on 24 October 2026, so there is no "
             "OLBG fixture to reverse-engineer for this sport today. No tournament was added from a "
             "second-hand list.")
RUGBY_LEAGUE_NOTE = ("OLBG's Rugby League hub contains no upcoming match market at 17:46Z on 24 October "
                     "2026. The only rows are 2027 outrights: State of Origin 2027 (27 May 2027), "
                     "Super League 2027 Grand Final (2 Oct 2027) and NRL 2027 Grand Final (3 Oct 2027).")

ALL_OTHER = TENNIS + CRICKET + SNOOKER + DARTS + RUGBY_UNION + VOLLEYBALL + HANDBALL + GAELIC + GREYHOUNDS + MOTOR_RACING
