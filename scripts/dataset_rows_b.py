"""
dataset_rows_b.py - Officially verified fixtures & multi-runner events (Part B):
Cricket, Rugby Union (URC + Top 14 + Gallagher Premiership cross-checked),
Rugby League (2026 Rugby League World Cup Round 2), Handball (EHF Champions League Men R5),
Volleyball (Italian SuperLega R2 + Polish PlusLiga), Aussie Rules (2026 NAB AFLW Round 11),
eSports (LoL Esports Worlds 2026 Swiss Round 1), Gaelic Football (4 GAA County SFC Finals),
Motor Racing (F1 US Grand Prix), Golf (PGA + DP World Tour + Champions), and Greyhounds (GBGB/OLBG).
"""
from __future__ import annotations

NZC_FIX = {"name": "New Zealand Cricket official fixtures", "url": "https://scoring.nzc.nz/fixtures"}
ICC_RANK = {"name": "ICC official team rankings (Men's & Women's T20I)", "url": "https://www.icc-cricket.com/rankings"}
CA_SERIES = {"name": "Cricket Australia official AUS W v NZ W series hub", "url": "https://www.cricket.com.au/"}
URC_FIX = {"name": "United Rugby Championship official 2026/27 fixtures", "url": "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/"}
TOP14_FIX = {"name": "LNR official Top 14 2026-2027 calendar & standings", "url": "https://top14.lnr.fr/calendrier-et-resultats"}
TOP14_TAB = {"name": "LNR official Top 14 Journée 6 standings", "url": "https://top14.lnr.fr/classement"}
PREM_FIX = {"name": "Gallagher Premiership official fixtures hub", "url": "https://www.premrugby.com/fixtures-results"}
RLWC_DRAW = {"name": "NRL / RLWC26 official Round 2 draw & match centre", "url": "https://www.nrl.com/draw/?competition=175&round=2&season=2026"}
RLWC_W = {"name": "NRL / RLWC26 Women's official draw", "url": "https://www.nrl.com/draw/?competition=176&round=2&season=2026"}
EHF_STAND = {"name": "EHF Champions League Men 2026/27 official standings", "url": "https://ehfcl.eurohandball.com/men/2026-27/standings/"}
EHF_SCHED = {"name": "EHF official 2026/27 group phase playing times PDF", "url": "https://www.eurohandball.com/media/jqal4wt0/ehfcl-men-2026-27-group-phase-playing-times.pdf"}
EHF_PREV = {"name": "EHF official Round 5 match preview", "url": "https://www.eurohandball.com/en/news/en/five-main-round-tickets-still-on-the-line-as-round-5-begins"}
LEGA_V = {"name": "Lega Pallavolo Serie A SuperLega Credem Banca calendar", "url": "https://www.legavolley.it/"}
PLUS_V = {"name": "PlusLiga official 2026/27 schedule", "url": "https://www.plusliga.pl/games.html"}
AFLW_FIX = {"name": "AFL official 2026 NAB AFLW fixture & ladder", "url": "https://www.afl.com.au/aflw"}
LOL_WORLDS = {"name": "LoL Esports official Worlds 2026 hub & primer", "url": "https://lolesports.com/en-US/"}
GAA_MUNSTER = {"name": "Munster GAA official county championship fixtures", "url": "https://munster.gaa.ie/fixtures/munster-gaa-fixtures/"}
GAA_CORK = {"name": "Cork GAA official Premier Senior Football fixtures", "url": "https://gaacork.ie/fixtures-results/"}
GAA_GALWAY = {"name": "Galway GAA official Senior Football Championship fixtures", "url": "https://www.galwaygaa.ie/results/"}
F1_USGP = {"name": "Formula 1 official 2026 United States Grand Prix hub", "url": "https://www.formula1.com/en/racing/2026/united-states"}
PGA_BERM = {"name": "PGA TOUR official Butterfield Bermuda Championship", "url": "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528"}
PGA_STIFEL = {"name": "PGA TOUR Champions Stifel Charity Classic", "url": "https://www.pgatour.com/pgatour-champions/schedule"}
DPWT_GEN = {"name": "DP World Tour official Genesis Championship", "url": "https://www.europeantour.com/dpworld-tour/schedule/2026/"}
LPGA_BMW = {"name": "LPGA official BMW Ladies Championship", "url": "https://www.lpga.com/tournaments"}
GBGB_OPEN = {"name": "Greyhound Board of Great Britain official open race calendar", "url": "https://www.gbgb.org.uk/"}


def get_rows_b() -> list[dict]:
    rows: list[dict] = []

    # =========================================================================
    # 7. CRICKET — ICC T20Is + NZ A v India A + Ford Trophy (all 7 original + ODI)
    # =========================================================================
    cricket_rows = [
        ("cric-nz-ind-t20-1", "Men's T20I Series", "1st T20I", "2026-10-22T06:15:00Z", None,
         "New Zealand", "India", "Hagley Oval, Christchurch", False,
         ("ICC Men's T20I rating", "No. 4 (247 rating)", 68.5), ("ICC Men's T20I rating", "No. 2 (267 rating, T20WC winners)", 81.5),
         [NZC_FIX, ICC_RANK],
         {"listed": True, "event_id": 188814, "selection": "India", "market": "Win Match", "consensus": "3/5 win tips (60%)",
          "url": "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/New_Zealand_vs_India_1st_T20_Match/7?event_id=188814"},
         []),
        ("cric-nz-ind-t20-2", "Men's T20I Series", "2nd T20I", "2026-10-24T06:15:00Z", None,
         "New Zealand", "India", "Hagley Oval, Christchurch", False,
         ("ICC Men's T20I rating", "No. 4 (247 rating)", 68.5), ("ICC Men's T20I rating", "No. 2 (267 rating, T20WC winners)", 81.5),
         [NZC_FIX, ICC_RANK], None, []),
        ("cric-ausw-nzw-t20-3", "Women's T20I Series", "3rd T20I", "2026-10-22T08:15:00Z", None,
         "Australia Women", "New Zealand Women", "Manuka Oval, Canberra", False,
         ("ICC Women's T20I rating", "No. 1 (287 rating)", 88.0), ("ICC Women's T20I rating", "No. 4 (253 rating)", 69.0),
         [CA_SERIES, NZC_FIX, ICC_RANK],
         {"listed": True, "event_id": 188826, "selection": "Australia W", "market": "Win Match", "consensus": "1/2 win tips (50%)",
          "url": "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Australia_W_vs_New_Zealand_W_3rd_T20_Match/7?event_id=188826"},
         []),
        ("cric-afg-ban-odi", "Men's One-Day International", "ODI Tri-Series", None, "2026-10-21",
         "Afghanistan", "Bangladesh", "Sharjah / UAE (neutral)", True,
         ("ICC Men's ODI rating", "No. 8 (92 rating)", 74.0), ("ICC Men's ODI rating", "No. 9 (82 rating)", 64.0),
         [ICC_RANK],
         {"listed": True, "event_id": 188824, "selection": "Afghanistan", "market": "Win Match", "consensus": "7/7 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Afghanistan_vs_Bangladesh_One_Day_Match/7?event_id=188824"},
         []),
        ("cric-nza-inda-fc1", "First-Class Tour Match", "1st Four-Day Match", None, "2026-10-22",
         "New Zealand A", "India A", "Saxton Oval, Nelson", False, None, None, [NZC_FIX], None,
         ["No official ICC rating for 'A' representative sides; baseline pricing",
          "No official four-day match-total baseline was captured; the total market is intentionally left blank rather than inferred"]),
        ("cric-ford-auck-cant", "Ford Trophy (List A 50-over)", "Round 1", None, "2026-10-24",
         "Auckland Aces", "Canterbury", "Kennards Hire Community Oval, Auckland", False, None, None, [NZC_FIX], None,
         ["Opening round of 2026-27 NZ domestic List A season; both sides 0-0"]),
        ("cric-ford-cds-nd", "Ford Trophy (List A 50-over)", "Round 1", None, "2026-10-24",
         "Central Stags", "Northern Districts", "Pukekura Park, New Plymouth", False, None, None, [NZC_FIX], None,
         ["Opening round of 2026-27 NZ domestic List A season; both sides 0-0"]),
        ("cric-ford-wgtn-otago", "Ford Trophy (List A 50-over)", "Round 1", None, "2026-10-24",
         "Wellington Firebirds", "Otago Volts", "Cello Basin Reserve, Wellington", False, None, None, [NZC_FIX], None,
         ["Opening round of 2026-27 NZ domestic List A season; both sides 0-0"]),
    ]
    for cid, comp, stg, utc, dloc, h, a, ven, neut, hi, ai, srcs, olbg, fl in cricket_rows:
        inp = {"home": {"label": hi[0], "value": hi[1], "rating": hi[2]},
               "away": {"label": ai[0], "value": ai[1], "rating": ai[2]}} if (hi and ai) else {}
        r = {
            "id": cid, "sport": "cricket", "competition": comp, "stage": stg,
            "start_utc": utc, "date_local": dloc, "home": h, "away": a, "venue": ven,
            "neutral": neut, "status": "verified", "sources": srcs, "inputs": inp, "flags": fl,
        }
        if olbg:
            r["olbg"] = olbg
        rows.append(r)

    # =========================================================================
    # 8. RUGBY UNION — Verified Top 14 J7 + Verified URC R4 + 5 Premiership Cross-Checked
    # =========================================================================
    top14_rows = [
        ("ru-top14-609567", "2026-10-24T14:35:00Z", "Stade Toulousain", "USA Perpignan",
         "Stade Ernest-Wallon, Toulouse", ("Top 14 standings (J6)", "1st, 24 pts (beat Bayonne 45-34)", 86.0),
         ("Top 14 standings (J6)", "9th, 13 pts", 55.0), 609567, "Perpignan +23.50", "Handicap", "1/1 win tips (100%)",
         "https://top14.lnr.fr/feuille-de-match/2026-2027/j7/11867-toulouse-perpignan"),
        ("ru-top14-609564", "2026-10-24T14:35:00Z", "Aviron Bayonnais", "LOU Rugby",
         "Stade Jean-Dauger, Bayonne", ("Top 14 standings (J6)", "5th, 17 pts", 68.0),
         ("Top 14 standings (J6)", "8th, 14 pts (lost 16-28 to La Rochelle)", 58.0), 609564, "Lyon +10.50", "Handicap", "1/1 win tips (100%)",
         "https://top14.lnr.fr/feuille-de-match/2026-2027/j7/11861-bayonne-lyon"),
        ("ru-top14-609554", "2026-10-25T20:05:00Z", "Stade Rochelais", "Union Bordeaux-Bègles",
         "Stade Marcel-Deflandre, La Rochelle", ("Top 14 standings (J6)", "4th, 18 pts (beat Lyon 28-16 away)", 72.0),
         ("Top 14 standings (J6)", "3rd, 19 pts", 74.0), 609554, "La Rochelle", "To Win", "1/2 win tips (50%)",
         "https://top14.lnr.fr/feuille-de-match/2026-2027/j7/11864-la-rochelle-bordeaux-begles"),
    ]
    for rid, utc, h, a, ven, hi, ai, eid, sel, mkt, cons, sheet in top14_rows:
        rows.append({
            "id": rid, "sport": "rugby-union", "competition": "French Top 14", "stage": "Journée 7",
            "start_utc": utc, "home": h, "away": a, "venue": ven, "neutral": False,
            "status": "verified",
            "sources": [TOP14_FIX, TOP14_TAB, {"name": "LNR official J7 match sheet", "url": sheet}],
            "inputs": {
                "home": {"label": hi[0], "value": hi[1], "rating": hi[2]},
                "away": {"label": ai[0], "value": ai[1], "rating": ai[2]},
            },
            "olbg": {"listed": True, "event_id": eid, "selection": sel, "market": mkt, "consensus": cons,
                     "url": f"https://www.olbg.com/betting-tips/Rugby_Union/9"},
            "flags": [],
        })

    urc_rows = [
        ("ru-urc-609577", "2026-10-23T18:45:00Z", "Connacht", "Zebre Parma", "Dexcom Stadium, Galway",
         609577, "Connacht", "To Win", "3/5 win tips (60%)"),
        ("ru-urc-609576", "2026-10-24T11:45:00Z", "Vodacom Bulls", "Ulster", "Loftus Versfeld, Pretoria",
         609576, "Ulster +18.50", "Handicap", "2/2 win tips (100%)"),
        ("ru-urc-609580", "2026-10-24T14:00:00Z", "DHL Stormers", "Scarlets", "DHL Stadium, Cape Town",
         609580, "Stormers", "To Win", "1/2 win tips (50%)"),
        ("ru-urc-609578", "2026-10-24T17:00:00Z", "Leinster", "Munster", "Aviva Stadium, Dublin",
         609578, "Leinster", "To Win", "1/1 win tips (100%)"),
    ]
    for rid, utc, h, a, ven, eid, sel, mkt, cons in urc_rows:
        rows.append({
            "id": rid, "sport": "rugby-union", "competition": "United Rugby Championship", "stage": "Round 4",
            "start_utc": utc, "home": h, "away": a, "venue": ven, "neutral": False,
            "status": "verified", "sources": [URC_FIX], "inputs": {},
            "olbg": {"listed": True, "event_id": eid, "selection": sel, "market": mkt, "consensus": cons,
                     "url": "https://www.olbg.com/betting-tips/Rugby_Union/9"},
            "flags": ["URC Round 3 live standings table client-rendered on stats.unitedrugby.com; fixture, venue and UTC kick-off verified on URC site"],
        })

    # Keep all 5 Gallagher Premiership rows from ce5920e3 preserved transparently as cross-checked
    prem_rows = [
        ("ru-gloucester-bath", "2026-10-23T18:45:00Z", "Gloucester", "Bath", "Kingsholm, Gloucester", []),
        ("ru-newcastle-sale", "2026-10-23T18:45:00Z", "Newcastle Red Bulls", "Sale Sharks", "Kingston Park, Newcastle", []),
        ("ru-leicester-northampton", "2026-10-24T14:05:00Z", "Leicester Tigers", "Northampton Saints", "Mattioli Woods Welford Road, Leicester",
         ["Kick-off time differs by 1h across secondary listings; cross-checked"]),
        ("ru-bristol-exeter", "2026-10-24T14:05:00Z", "Bristol Bears", "Exeter Chiefs", "Ashton Gate, Bristol", []),
        ("ru-harlequins-saracens", "2026-10-25T15:00:00Z", "Harlequins", "Saracens", "Twickenham Stoop, London",
         ["BST ends 25 Oct 2026 at 01:00 UTC"]),
    ]
    for rid, utc, h, a, ven, extra in prem_rows:
        rows.append({
            "id": rid, "sport": "rugby-union", "competition": "Gallagher Premiership", "stage": "Round 4",
            "start_utc": utc, "home": h, "away": a, "venue": ven, "neutral": False,
            "status": "cross-checked", "sources": [PREM_FIX],
            "external_checks": [{"name": "TNT Sports UK broadcaster listing", "url": "https://www.tntsports.co.uk/rugby/premiership/calendar-results.shtml"}],
            "inputs": {},
            "flags": ["Premiership Rugby client-rendered schedule returned zero server DOM rows; kept cross-checked and capped at low confidence"] + extra,
        })

    # =========================================================================
    # 9. RUGBY LEAGUE — 2026 Rugby League World Cup Round 2 (7 official NRL/RLWC26 ties!)
    # =========================================================================
    rlwc_rows = [
        ("rl-wc26-aus-fij", "RLWC26 Men's Tournament", "Round 2", "2026-10-25T09:05:00Z",
         "Australia", "Fiji", "Suncorp Stadium, Brisbane", False,
         ("IRL World Ranking", "No. 1 (beat NZ 24-22 R1; 19 straight WC wins)", 95.0), ("IRL World Ranking", "No. 7", 63.0), RLWC_DRAW),
        ("rl-wc26-nzl-cok", "RLWC26 Men's Tournament", "Round 2", "2026-10-25T05:05:00Z",
         "New Zealand", "Cook Islands", "One New Zealand Stadium, Christchurch", False,
         ("IRL World Ranking", "No. 2 (narrow 22-24 loss to AUS in opener)", 89.0), ("IRL World Ranking", "No. 9", 56.0), RLWC_DRAW),
        ("rl-wc26-eng-fra", "RLWC26 Men's Tournament", "Round 2", "2026-10-24T06:35:00Z",
         "England", "France", "HBF Park, Perth", True,
         ("IRL World Ranking", "No. 3", 84.0), ("IRL World Ranking", "No. 8 (lost 4-78 to Samoa in R1)", 50.0), RLWC_DRAW),
        ("rl-wc26-png-sam", "RLWC26 Men's Tournament", "Round 2", "2026-10-24T04:25:00Z",
         "Papua New Guinea", "Samoa", "Santos National Football Stadium, Port Moresby", False,
         ("IRL World Ranking", "No. 6", 68.0), ("IRL World Ranking", "No. 4 (beat France 78-4 in R1)", 80.0), RLWC_DRAW),
        ("rl-wc26-tga-lbn", "RLWC26 Men's Tournament", "Round 2", "2026-10-23T09:05:00Z",
         "Tonga", "Lebanon", "CommBank Stadium, Sydney", True,
         ("IRL World Ranking", "No. 5", 77.0), ("IRL World Ranking", "No. 11", 56.0), RLWC_DRAW),
        ("rl-wc26w-aus-eng", "RLWC26 Women's Tournament", "Round 2", "2026-10-24T09:05:00Z",
         "Australia Jillaroos", "England Women", "HBF Park, Perth", False,
         ("IRL Women's Ranking", "No. 1", 92.0), ("IRL Women's Ranking", "No. 2 (beat Wales 70-6 in R1)", 82.0), RLWC_W),
        ("rl-wc26w-sam-wal", "RLWC26 Women's Tournament", "Round 2", "2026-10-23T06:45:00Z",
         "Samoa Women", "Wales Women", "CommBank Stadium, Sydney", True,
         ("IRL Women's Ranking", "No. 5", 70.0), ("IRL Women's Ranking", "No. 7 (lost 6-70 to England W in R1)", 51.0), RLWC_W),
    ]
    for rid, comp, stg, utc, h, a, ven, neut, hi, ai, src in rlwc_rows:
        rows.append({
            "id": rid, "sport": "rugby-league", "competition": comp, "stage": stg,
            "start_utc": utc, "home": h, "away": a, "venue": ven, "neutral": neut,
            "status": "verified", "sources": [src],
            "inputs": {
                "home": {"label": hi[0], "value": hi[1], "rating": hi[2]},
                "away": {"label": ai[0], "value": ai[1], "rating": ai[2]},
            },
            "flags": ["OLBG blind spot: /betting-tips/Rugby_League/10 lists only 2027 ante-post markets and zero RLWC26 Round 2 matches"],
        })

    # =========================================================================
    # 10. HANDBALL — ALL 12 EHF Champions League Men Round 5 Ties (eurohandball.com)
    # =========================================================================
    ehf_rows = [
        ("hand-ehf-12055", "2026-10-21T16:45:00Z", "One Veszprém HC", "Füchse Berlin", "One Veszprém Arena, Veszprém",
         ("Group A standing", "1st, 4-0-0 (8 pts, +35 GD)", 88.0), ("Group A standing", "2nd, 3-0-1 (6 pts, +16 GD)", 80.0),
         12055, "Veszprem", "Money Line", "5/11 win tips (45%)"),
        ("hand-ehf-12052", "2026-10-21T16:45:00Z", "RK Partizan AdmiralBet", "FC Porto", "Hall Aleksandar Nikolic, Belgrade",
         ("Group A standing", "4th, 0-0-4 (0 pts, -36 GD)", 48.0), ("Group A standing", "3rd, 1-0-3 (2 pts, -15 GD)", 62.0),
         12052, "RK Partizan", "Money Line", "3/8 win tips (38%)"),
        ("hand-ehf-12053", "2026-10-21T16:45:00Z", "HC Zagreb", "Paris Saint-Germain", "Arena Zagreb, Zagreb",
         ("Group C standing", "3rd, 1-0-3 (2 pts, -13 GD)", 56.0), ("Group C standing", "1st, 3-1-0 (7 pts, +26 GD, beat Zagreb 34:30)", 84.0),
         12053, "PSG Handball", "Money Line", "8/13 win tips (62%)"),
        ("hand-ehf-12045", "2026-10-21T16:45:00Z", "CS Dinamo Bucuresti", "SAH Aarhus", "Sala Polivalenta, Bucharest",
         None, None, 12045, "Dinamo Bucuresti", "Money Line", "4/11 win tips (36%)"),
        ("hand-ehf-12050", "2026-10-21T18:45:00Z", "HBC Nantes", "HC Vardar 1961", "H Arena, Nantes",
         ("Group B standing", "2nd, 3-0-1 (6 pts, +5 GD)", 78.0), ("Group B standing", "4th, 1-0-3 (2 pts)", 57.0),
         12050, "Nantes", "Money Line", "6/10 win tips (60%)"),
        ("hand-ehf-12044", "2026-10-21T18:45:00Z", "Aalborg Håndbold", "RK Celje Pivovarna Laško", "Sparekassen Danmark Arena, Aalborg",
         ("Group C standing", "2nd, 3-1-0 (7 pts, +21 GD, won 36:26 at Celje)", 84.0), ("Group C standing", "4th, 0-0-4 (0 pts, -34 GD)", 51.0),
         12044, "Tie", "Money Line", "4/5 win tips (80%)"),
        ("hand-ehf-12047", "2026-10-21T18:45:00Z", "HC Kriens-Luzern", "Industria Kielce", "Pilatus Arena, Kriens",
         ("Group standing", "2-0-2 (4 pts)", 66.0), ("Group standing", "2-0-2 (4 pts)", 70.0),
         12047, "Tie", "Money Line", "3/6 win tips (50%)"),
        ("hand-ehf-12049", "2026-10-22T16:45:00Z", "MT Melsungen", "Orlen Wisla Plock", "Rothenbach-Halle, Kassel",
         ("Group B standing", "3rd, 1-0-3 (2 pts)", 63.0), ("Group B standing", "1st, 3-0-1 (6 pts)", 76.0),
         12049, "MT Melsungen", "Money Line", "2/4 win tips (50%)"),
        ("hand-ehf-12051", "2026-10-22T16:45:00Z", "OTP Bank - PICK Szeged", "GOG", "PICK Arena, Szeged",
         ("Group standing", "1-1-2 (3 pts)", 67.0), ("Group standing", "3-0-1 (6 pts)", 75.0),
         12051, "GOG", "Money Line", "2/4 win tips (50%)"),
        ("hand-ehf-12048", "2026-10-22T18:45:00Z", "Kolstad Håndball", "SC Magdeburg", "Trondheim Spektrum, Trondheim",
         ("Group standing", "4th, 0-0-4 (0 pts)", 52.0), ("Group standing", "1st, 4-0-0 (8 pts)", 86.0),
         12048, "Tie", "Money Line", "3/6 win tips (50%)"),
        ("hand-ehf-12054", "2026-10-22T18:45:00Z", "Sporting CP", "IFK Kristianstad", "Pavilhão João Rocha, Lisbon",
         None, None, 12054, "Tie", "Money Line", "3/7 win tips (43%)"),
        ("hand-ehf-12046", "2026-10-22T18:45:00Z", "Barça", "Montpellier Handball", "Palau Blaugrana, Barcelona",
         ("Group E standing", "1st, 4-0-0 (8 pts, +33 GD, beat Montpellier 28:27)", 90.0), ("Group E standing", "3rd, 1-0-3 (2 pts, -9 GD)", 64.0),
         12046, "Montpellier", "Money Line", "2/6 win tips (33%)"),
    ]
    for hid, utc, h, a, ven, hi, ai, eid, sel, mkt, cons in ehf_rows:
        inp = {"home": {"label": hi[0], "value": hi[1], "rating": hi[2]},
               "away": {"label": ai[0], "value": ai[1], "rating": ai[2]}} if (hi and ai) else {}
        fl = []
        if eid == 12045:
            fl.append("OLBG naming bug: event_id=12045 displays 'Skanderborg Handbold' instead of official EHF name 'SAH Aarhus'")
        rows.append({
            "id": hid, "sport": "handball", "competition": "EHF Champions League Men",
            "stage": "Group Phase - Round 5", "start_utc": utc, "home": h, "away": a,
            "venue": ven, "neutral": False, "status": "verified",
            "sources": [EHF_STAND, EHF_SCHED, EHF_PREV], "inputs": inp,
            "olbg": {"listed": True, "event_id": eid, "selection": sel, "market": mkt, "consensus": cons,
                     "url": "https://www.olbg.com/betting-tips/Handball/20"},
            "flags": fl,
        })

    # =========================================================================
    # 11. VOLLEYBALL — Polish PlusLiga + Italian SuperLega Credem Banca Round 2
    # =========================================================================
    volley_rows = [
        ("vol-plus-36961", "Polish PlusLiga", "Regular Season", "2026-10-21T15:30:00Z", "BOGDANKA LUK Lublin", "Trefl Gdansk",
         "Hala Globus, Lublin", PLUS_V, 36961, "LUK Lublin", "3/3 win tips (100%)"),
        ("vol-plus-36962", "Polish PlusLiga", "Regular Season", "2026-10-21T18:30:00Z", "Aluron CMC Warta Zawiercie", "ZAKSA Kedzierzyn-Kozle",
         "Hala OSiR II, Zawiercie", PLUS_V, 36962, "Warta Zawiercie", "1/1 win tips (100%)"),
        ("vol-plus-36963", "Polish PlusLiga", "Regular Season", "2026-10-23T15:30:00Z", "Slepsk Malow Suwalki", "GKS Katowice",
         "Suwalki Arena, Suwalki", PLUS_V, 36963, "Slepsk Suwalki", "2/2 win tips (100%)"),
        ("vol-plus-36964", "Polish PlusLiga", "Regular Season", "2026-10-24T16:00:00Z", "PGE GiEK Skra Belchatow", "PGE Projekt Warszawa",
         "Hala Energia, Belchatow", PLUS_V, 36964, "Projekt Warszawa", "2/2 win tips (100%)"),
        ("vol-plus-36965", "Polish PlusLiga", "Regular Season", "2026-10-25T17:00:00Z", "InPost ChKS Chelm", "Asseco Resovia Rzeszow",
         "MOSiR Hall, Chelm", PLUS_V, 36965, "Resovia Rzeszow", "2/2 win tips (100%)"),
        ("vol-lega-perugia", "SuperLega Credem Banca", "Regular Season - Round 2", "2026-10-25T16:00:00Z", "Sir Susa Scai Perugia", "Tinet Prata di Pordenone",
         "PalaBarton, Perugia", LEGA_V, None, "", ""),
        ("vol-lega-trentino", "SuperLega Credem Banca", "Regular Season - Round 2", "2026-10-25T17:00:00Z", "Itas Trentino", "Cisterna Volley",
         "ilT quotidiano Arena, Trento", LEGA_V, None, "", ""),
        ("vol-lega-lube", "SuperLega Credem Banca", "Regular Season - Round 2", "2026-10-25T17:00:00Z", "Cucine Lube Civitanova", "Sonepar Padova",
         "Eurosuole Forum, Civitanova Marche", LEGA_V, None, "", ""),
    ]
    for vid, comp, stg, utc, h, a, ven, src, eid, sel, cons in volley_rows:
        r = {
            "id": vid, "sport": "volleyball", "competition": comp, "stage": stg,
            "start_utc": utc, "home": h, "away": a, "venue": ven, "neutral": False,
            "status": "verified", "sources": [src], "inputs": {},
            "flags": ["Early-round 2026-27 league table sample (<3 rounds played); priced off neutral home baseline"],
        }
        if eid:
            r["olbg"] = {"listed": True, "event_id": eid, "selection": sel, "market": "Win Match", "consensus": cons,
                         "url": "https://www.olbg.com/betting-tips/Volleyball/21"}
        rows.append(r)

    # =========================================================================
    # 12. AUSSIE RULES — ALL 9 Official 2026 NAB AFLW Round 11 Matches (afl.com.au)
    # =========================================================================
    aflw_rows = [
        ("aflw-r11-01", "2026-10-23T08:15:00Z", "North Melbourne", "Adelaide Crows", "Arden Street Oval, Melbourne",
         ("2026 AFLW R10 ladder", "1st, 40 pts (10-0)", 96.0), ("2026 AFLW R10 ladder", "9th, 20 pts (5-5)", 60.0)),
        ("aflw-r11-02", "2026-10-24T02:05:00Z", "Geelong Cats", "Fremantle", "GMHBA Stadium, Geelong",
         ("2026 AFLW R10 ladder", "13th, 16 pts (4-6)", 50.0), ("2026 AFLW R10 ladder", "7th, 24 pts (6-4)", 66.0)),
        ("aflw-r11-03", "2026-10-24T04:05:00Z", "Western Bulldogs", "Melbourne", "Mission Whitten Oval, Melbourne",
         ("2026 AFLW R10 ladder", "12th, 16 pts (4-6)", 51.0), ("2026 AFLW R10 ladder", "3rd, 32 pts (8-2)", 82.0)),
        ("aflw-r11-04", "2026-10-24T04:05:00Z", "Carlton", "GWS GIANTS", "IKON Park, Melbourne",
         ("2026 AFLW R10 ladder", "6th, 24 pts (6-4)", 67.0), ("2026 AFLW R10 ladder", "16th, 8 pts (2-8)", 38.0)),
        ("aflw-r11-05", "2026-10-24T06:15:00Z", "Hawthorn", "Essendon", "Kinetic Stadium, Frankston",
         ("2026 AFLW R10 ladder", "4th, 32 pts (8-2)", 81.0), ("2026 AFLW R10 ladder", "14th, 14 pts (3-6-1)", 46.0)),
        ("aflw-r11-06", "2026-10-24T08:15:00Z", "Gold Coast SUNS", "Richmond", "People First Stadium, Gold Coast",
         ("2026 AFLW R10 ladder", "18th, 4 pts (1-9)", 31.0), ("2026 AFLW R10 ladder", "17th, 8 pts (2-8)", 37.0)),
        ("aflw-r11-07", "2026-10-25T02:05:00Z", "Port Adelaide", "Collingwood", "Alberton Oval, Adelaide",
         ("2026 AFLW R10 ladder", "11th, 20 pts (5-5)", 58.0), ("2026 AFLW R10 ladder", "15th, 12 pts (3-7)", 43.0)),
        ("aflw-r11-08", "2026-10-25T04:05:00Z", "Sydney Swans", "West Coast Eagles", "Henson Park, Sydney",
         ("2026 AFLW R10 ladder", "5th, 26 pts (6-3-1)", 71.0), ("2026 AFLW R10 ladder", "8th, 24 pts (6-4)", 65.0)),
        ("aflw-r11-09", "2026-10-25T06:05:00Z", "St Kilda", "Brisbane Lions", "RSEA Park, Melbourne",
         ("2026 AFLW R10 ladder", "10th, 20 pts (5-5)", 59.0), ("2026 AFLW R10 ladder", "2nd, 32 pts (8-2)", 84.0)),
    ]
    for aid, utc, h, a, ven, hi, ai in aflw_rows:
        rows.append({
            "id": aid, "sport": "aussie-rules", "competition": "NAB AFLW Premiership Season",
            "stage": "Round 11", "start_utc": utc, "home": h, "away": a, "venue": ven,
            "neutral": False, "status": "verified", "sources": [AFLW_FIX],
            "inputs": {
                "home": {"label": hi[0], "value": hi[1], "rating": hi[2]},
                "away": {"label": ai[0], "value": ai[1], "rating": ai[2]},
            },
            "flags": ["OLBG blind spot: /betting-tips/Aussie_Rules/22 returns 'No tips found' despite 9 official Round 11 AFLW fixtures"],
        })

    # =========================================================================
    # 13. ESPORTS — LoL Esports Worlds 2026 Swiss Round 1 (official lolesports.com)
    # =========================================================================
    rows.append({
        "id": "lol-worlds26-tsw-lyon", "sport": "esports",
        "competition": "League of Legends World Championship 2026",
        "stage": "Swiss Stage - Round 1 (Best of 1)", "date_local": "2026-10-24", "start_utc": None,
        "home": "Team Secret Whales", "away": "LYON",
        "venue": "Credit Union of Texas Event Center, Allen, TX", "neutral": True,
        "status": "verified", "sources": [LOL_WORLDS],
        "inputs": {
            "home": {"label": "Worlds Swiss draw pool", "value": "Pool 2 seed (VCS #1)", "rating": 66.0},
            "away": {"label": "Worlds Swiss draw pool", "value": "Pool 3 Play-In qualifier (LLA/LTA)", "rating": 54.0},
        },
        "flags": ["OLBG blind spot: /betting-tips/eSports/23 returns 'No tips found' ahead of LoL Worlds 2026 Swiss Round 1"],
    })

    # =========================================================================
    # 14. GAELIC FOOTBALL — 4 Official County SFC Finals (munster.gaa.ie / gaacork / galwaygaa)
    # =========================================================================
    gaa_rows = [
        ("gaa-galway-3532", "Galway Senior Football Championship", "County Final", "2026-10-24T18:00:00Z",
         "Moycullen", "Salthill-Knocknacarra", "Pearse Stadium, Salthill", [GAA_GALWAY],
         {"listed": True, "event_id": 3532, "selection": "Moycullen -3.50", "market": "Handicap", "consensus": "9/17 win tips (53%)",
          "url": "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532"},
         ["Borderline scope flag: Gaelic Football retained in scope across the repo (Football/Soccer ID 1 and American Football ID 11 excluded)"]),
        ("gaa-cork-3530", "Cork Premier Senior Football Championship", "County Final", "2026-10-25T16:00:00Z",
         "St Finbarrs", "Nemo Rangers", "SuperValu Páirc Uí Chaoimh, Cork", [GAA_CORK, GAA_MUNSTER],
         {"listed": True, "event_id": 3530, "selection": "Draw (10/20 FT) / Nemo Rangers +1.50 (10/12 Hcap)", "market": "To Win / Handicap", "consensus": "10/12 handicap tips (83%)",
          "url": "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530"},
         ["Borderline scope flag: Gaelic Football retained in scope"]),
        ("gaa-waterford-3536", "Waterford Senior Football Championship", "County Final", "2026-10-25T14:30:00Z",
         "Rathgormack", "The Nire", "Fraher Field, Dungarvan", [GAA_MUNSTER],
         {"listed": True, "event_id": 3536, "selection": "Rathgormack -2.50", "market": "Handicap", "consensus": "1/1 win tips (100%)",
          "url": "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Rathgormack_v_The_Nire/25?event_id=3536"},
         ["OLBG UPSTREAM DATE BUG: OLBG displays '01 Nov 10:30' on event_id=3536, whereas official Munster GAA schedules throw-in on Sunday 25 Oct 2026 at 14:30 UTC",
          "Borderline scope flag: Gaelic Football retained in scope"]),
        ("gaa-kerry-sfc", "Kerry Senior Football Championship", "County Final", "2026-10-25T14:00:00Z",
         "Dr. Crokes", "Kenmare Shamrocks", "Austin Stack Park / Fitzgerald Stadium, Kerry", [GAA_MUNSTER], None,
         ["Borderline scope flag: Gaelic Football retained in scope"]),
    ]
    for gid, comp, stg, utc, h, a, ven, srcs, olbg, fl in gaa_rows:
        r = {
            "id": gid, "sport": "gaelic-football", "competition": comp, "stage": stg,
            "start_utc": utc, "home": h, "away": a, "venue": ven, "neutral": True,
            "status": "verified", "sources": srcs, "inputs": {},
            "flags": fl + ["County final pairs separate group winners with no unified pre-final numeric rating; priced neutral"],
        }
        if olbg:
            r["olbg"] = olbg
        rows.append(r)

    # =========================================================================
    # 15-17. MULTI-RUNNER FIELD EVENTS (Motor Racing, Golf, Greyhounds) — event-only
    # =========================================================================
    multi_runner_events = [
        ("f1-usgp-2026", "motor-racing", "FIA Formula One World Championship",
         "Round 18 - United States Grand Prix (56 laps)", "2026-10-25T20:00:00Z", "2026-10-25",
         "United States Grand Prix", "Circuit of The Americas, Austin, TX", [F1_USGP],
         {"listed": True, "event_id": 913, "selection": "Max Verstappen", "market": "Outright Race Winner", "consensus": "OLBG event 913",
          "url": "https://www.olbg.com/betting-tips/Motor_Racing/14"},
         ["20-car Grand Prix field market (not a two-sided fixture); race start verified at 20:00 UTC (OLBG displays 16:00 EDT)"]),
        ("golf-bermuda-2026", "golf", "PGA TOUR FedExCup Fall",
         "Butterfield Bermuda Championship (72-hole stroke play)", None, "2026-10-22",
         "Butterfield Bermuda Championship", "Port Royal Golf Course, Southampton, Bermuda", [PGA_BERM],
         {"listed": True, "event_id": 101904, "selection": "Outright field market", "market": "Outright Winner", "consensus": "OLBG event 101904",
          "url": "https://www.olbg.com/betting-tips/Golf/5"},
         ["Full-field 72-hole stroke-play tournament; verified event, not a two-sided match"]),
        ("golf-genesis-2026", "golf", "DP World Tour & KPGA Co-Sanctioned",
         "Genesis Championship (72-hole stroke play)", None, "2026-10-22",
         "Genesis Championship", "Woo Jeong Hills Country Club / Republic of Korea", [DPWT_GEN],
         {"listed": True, "event_id": 101903, "selection": "Outright field market", "market": "Outright Winner", "consensus": "OLBG event 101903",
          "url": "https://www.olbg.com/betting-tips/Golf/5"},
         ["Full-field 72-hole stroke-play tournament; verified event"]),
        ("golf-bmw-ladies-2026", "golf", "LPGA Tour",
         "BMW Ladies Championship (72-hole stroke play)", None, "2026-10-22",
         "BMW Ladies Championship", "Pine Beach Golf Links, Haenam, Republic of Korea", [LPGA_BMW],
         {"listed": True, "event_id": 101906, "selection": "Outright field market", "market": "Outright Winner", "consensus": "OLBG event 101906",
          "url": "https://www.olbg.com/betting-tips/Golf/5"},
         ["Full-field 72-hole stroke-play tournament; verified event"]),
        ("golf-stifel-2026", "golf", "PGA TOUR Champions",
         "Stifel Charity Classic (54-hole stroke play)", None, "2026-10-23",
         "Stifel Charity Classic", "Norwood Hills Country Club, St. Louis, MO", [PGA_STIFEL],
         {"listed": True, "event_id": 101907, "selection": "Outright field market", "market": "Outright Winner", "consensus": "OLBG event 101907",
          "url": "https://www.olbg.com/betting-tips/Golf/5"},
         ["54-hole PGA TOUR Champions field event; verified event"]),
        ("grey-kinsley-1114", "greyhounds", "GBGB UK Graded Greyhound Racing",
         "6-Trap Graded Race (11:14 BST = 10:14 UTC)", "2026-10-21T10:14:00Z", "2026-10-21",
         "11:14 Kinsley Card", "Kinsley Greyhound Stadium, Pontefract", [GBGB_OPEN],
         {"listed": True, "event_id": 689388, "selection": "Trap selection", "market": "Win Race", "consensus": "OLBG event 689388",
          "url": "https://www.olbg.com/betting-tips/Greyhounds/28"},
         ["Definitive proof of OLBG UTC-4 clock bug: race titled '11:14 Kinsley' (11:14 BST = 10:14 UTC) renders 'Today 06:14' (EDT) on OLBG; 6-dog race, not H2H"]),
        ("grey-monmore-1103", "greyhounds", "GBGB UK Graded Greyhound Racing",
         "6-Trap Graded Race (11:03 BST = 10:03 UTC)", "2026-10-21T10:03:00Z", "2026-10-21",
         "11:03 Monmore Card", "Monmore Green Stadium, Wolverhampton", [GBGB_OPEN],
         {"listed": True, "event_id": 689386, "selection": "Trap selection", "market": "Win Race", "consensus": "OLBG event 689386",
          "url": "https://www.olbg.com/betting-tips/Greyhounds/28"},
         ["6-runner trap market verified against GBGB licensed stadium schedule"]),
        ("grey-nottingham-1109", "greyhounds", "GBGB UK Graded Greyhound Racing",
         "6-Trap Graded Race (11:09 BST = 10:09 UTC)", "2026-10-21T10:09:00Z", "2026-10-21",
         "11:09 Nottingham Card", "Nottingham Greyhound Stadium, Colwick Park", [GBGB_OPEN],
         {"listed": True, "event_id": 689390, "selection": "Trap selection", "market": "Win Race", "consensus": "OLBG event 689390",
          "url": "https://www.olbg.com/betting-tips/Greyhounds/28"},
         ["6-runner trap market verified against GBGB licensed stadium schedule"]),
    ]
    for mid, sp, comp, stg, utc, dloc, title, ven, srcs, olbg, fl in multi_runner_events:
        rows.append({
            "id": mid, "sport": sp, "competition": comp, "stage": stg,
            "start_utc": utc, "date_local": dloc, "home": title, "away": "",
            "venue": ven, "neutral": True, "status": "verified",
            "sources": srcs, "inputs": {}, "olbg": olbg, "flags": fl,
        })

    return rows
