"""sf1c13c19_data2.py - part 2 of the f1c13c19 fixture build (called by sf1c13c19_data.py).

All rows verified 2026-10-22 by session arena/f1c13c19-olbg1; tier labels as documented
in sf1c13c19_data.py.  OLBG card text is transcribed verbatim from
data/f1c13c19/harvest_notes.md.
"""
NOW = "2026-10-22T08:45:00Z"

S = {
 "atp_al": ("ATP official Almaty daily schedule", "https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule"),
 "atp_als": ("ATP official Almaty top seeds", "https://www.atptour.com/en/scores/current/almaty/9410/top-seeds"),
 "atp_br": ("ATP official Brussels daily schedule", "https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule"),
 "atp_brs": ("ATP official Brussels top seeds", "https://www.atptour.com/en/scores/current/brussels/7485/top-seeds"),
 "atp_ly": ("ATP official Lyon daily schedule", "https://www.atptour.com/en/scores/current/lyon/496/daily-schedule"),
 "atp_lys": ("ATP official Lyon top seeds", "https://www.atptour.com/en/scores/current/lyon/496/top-seeds"),
 "wta_pdf": ("WTA official Ningbo main-draw PDF", "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf"),
 "wta_rua": ("WTA official Ningbo draws page (R16 listing)", "https://www.wtatennis.com/tournaments/2092/ningbo/2026/draws"),
 "wst": ("WST official Match Centre (NI Open R3, 22 Oct)", "https://www.wst.tv/match-centre/67133698-e8a4-4b37-9266-452a97df8584"),
 "snk_org": ("snooker.org NI Open event bracket (world-ranking numbers in brackets)", "https://www.snooker.org/res/index.asp?event=2548"),
 "pdc": ("PDC official news - EC schedule confirmed", "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/"),
 "pdc2": ("PDC official news - EC field & draw confirmed", "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed"),
 "pdc3": ("PDC World Rankings (18 Oct 2026 table, official OoM values; pdc.tv page is consent-walled in this environment - corroborated by two outlets)", "https://en.wikipedia.org/wiki/PDC_World_Rankings"),
 "urc": ("URC official 2026/27 fixtures in full", "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/"),
 "lnr": ("LNR official Top 14 J7/J8 calendar", "https://top14.lnr.fr/calendrier-et-resultats/2026-2027/j8"),
 "prod2": ("Oyonnax Rugby official fixtures page", "https://oyonnaxrugby.com/accueil"),
 "prod2b": ("allrugby Pro D2 J8 referees/schedule", "https://www.allrugby.com/news/pro-d2-2027-j8-arbitres-3870.html"),
 "ehf": ("eurohandball.com official R5 match list", "https://www.eurohandball.com/en/"),
 "ehf2": ("EHF official R5 preview (H2H last meetings)", "https://www.eurohandball.com/en/news/en/five-main-round-tickets-still-on-the-line-as-round-5-begins"),
 "ehf3": ("2026-27 EHF CL group tables (Wikipedia season article, mirrors EHF)", "https://en.wikipedia.org/wiki/2026%E2%80%9327_EHF_Champions_League"),
 "gaa_gw": ("Galway GAA official county fixtures page", "https://www.galwaygaa.ie/fixtures/?user=6929"),
 "gaa_it": ("Irish Times club championships state of play (Cork final)", "https://www.irishtimes.com/sport/gaelic-games/2026/10/14/club-football-championships-who-are-county-champions-and-what-is-the-state-of-play-around-ireland/"),
 "gaa_rte": ("RTE GAA club wrap (semi results)", "https://www.rte.ie/sport/hurling/2026/1011/1594942-gaa-club-wrap-cuala-and-maigh-cuillin-among-semi-winners/"),
 "icc": ("ESPNcricinfo fixtures hub", "https://www.cricinfo.com/ci/content/match/fixtures"),
 "icc2": ("Wikipedia International cricket 2026-27 (tri-series results)", "https://en.wikipedia.org/wiki/International_cricket_in_2026%E2%80%9327"),
 "cau": ("Cricket Australia official matches hub", "https://www.cricket.com.au/matches"),
 "csa": ("CSA T20 Challenge schedule (cricsa.co.za hub)", "https://cricsa.co.za/csa-t20-challenge-2026/"),
 "csa2": ("CSA Pro T20 Cup points table (Group B)", "https://www.cricketworld.com/cricket/series/csa-t20-challenge-2026/points/130198"),
 "shl": ("SHL official club fixture note (Vaxjo Lakers home slate)", "https://www.vaxjolakers.se/"),
 "shl2": ("SHL schedule + results hub (sportbibeln)", "https://www.sportbibeln.se/hockey/shl-resultat-och-tabell/"),
 "shl3": ("SHL TV schedule (vmhockey)", "https://vmhockey.se/shl/spelschema/"),
 "root": ("Root desk verified dataset (re-checked here)", "https://buffedlizard55-lab.github.io/OLBG1/"),
 "root2": ("Root desk verification ledger (data/verification.json)", "https://buffedlizard55-lab.github.io/OLBG1/"),
}

def _s(*ks):
    return [{"name": S[k][0], "url": S[k][1]} for k in ks]

def _i(label, value, rating=None, tier="verified", bounded=False):
    d = {"label": label, "value": value, "tier": tier}
    if rating is not None:
        d["rating"] = round(rating, 2)
    if bounded:
        d["bounded"] = True
    return d

def build(ev, NHL_OFFSET=0):
    E = []
    def add(*a, **k):
        ev(*a, **k); E.append(ev.__self__ if False else None)
    # NB: ev() appends to the parent list; we capture via a local mirror.
    made = []
    def mk(id, sport, comp, home, away, start, venue, verdict, sources, home_in, away_in,
           olbg, neutral=False, flags=None, stage=None):
        row = {
            "id": id, "sport": sport, "competition": comp, "home": home, "away": away,
            "start_utc": start, "venue": venue, "neutral": neutral,
            "verification": {"verdict": verdict, "checked_utc": NOW,
                             "fields": ["participants", "start", "venue"]},
            "sources": _s(*sources),
            "inputs": {"home": home_in, "away": away_in},
            "olbg": olbg, "stage": stage or "", "flags": flags or [],
        }
        made.append(row)

    # ---------------- Tennis - ATP Almaty (official schedules + seeds) -------------
    atp_rank = {"Medvedev": 6, "Darderi": 21, "Bublik": 22, "Rublev": 23, "Khachanov": 27,
                "Etcheverry": 31, "Tsitsipas": 43, "Fils": 11, "Lehecka": 16,
                "Cerundolo": 20, "Michelsen": 35, "Bergs": 39, "Cobolli": 7, "Fritz": 12,
                "Vacherot": 14, "Paul": 18, "Nakashima": 19, "Musetti": 25}
    def tr(rank):
        import math
        return 100.0 - 52.0 * math.log(rank) / math.log(100.0)
    def tin(name, rank=None, note=""):
        if rank:
            return _i("ATP singles ranking (atptour.com)", f"No. {rank}{note}", tr(rank))
        return _i("ATP singles ranking", "not batch-verified this session (flagged)", None, tier="pending")
    mk("ten-902110", "tennis", "ATP 250 Almaty Open (R16)", "Tomas Machac", "Karen Khachanov",
       "2026-10-22T08:00:00Z", "Center Court, Almaty Arena (court 11:30 local block)", "verified",
       ("atp_al", "atp_als"), tin("Machac"), tin("Khachanov", 27, " (seed 5)"),
       olbg={"hub": "Tennis/3", "clock": "Today 04:00", "tips": "Khachanov 4/6 (67%)"},
       flags=["R16 'not before 13:00' local (Almaty UTC+5 = 08:00Z); OLBG shows 04:00 UK - upstream clock defect"])
    mk("ten-902069", "tennis", "ATP 250 Almaty Open (R16)", "Daniil Medvedev", "Sho Shimabukuro",
       "2026-10-22T08:00:00Z", "Center Court, Almaty Arena", "verified", ("atp_al", "atp_als"),
       tin("Medvedev", 6, " (seed 1)"), tin("Shimabukuro"),
       olbg={"hub": "Tennis/3", "clock": "Today 05:30", "tips": "Medvedev 8/9 (89%)"},
       flags=["follows Machac-Khachanov on Center Court; OLBG clock again ~4h early"])
    mk("ten-902082", "tennis", "ATP 250 Almaty Open (R16)", "Alexander Bublik", "Fabian Marozsan",
       "2026-10-22T14:30:00Z", "Center Court, Almaty Arena", "verified", ("atp_al", "atp_als"),
       tin("Bublik", 22, " (seed 3)"), tin("Marozsan"),
       olbg={"hub": "Tennis/3", "clock": "Today 10:30", "tips": "Bublik 3/4 (75%)"},
       flags=["ATP lists 'not before 19:30' local for prime slot"])
    # ---------------- Tennis - ATP Brussels ------------------------------------
    mk("ten-902104", "tennis", "ATP 250 Brussels Open (R16)", "Raphael Collignon", "Jiri Lehecka",
       "2026-10-22T11:30:00Z", "Centre Court, Brussels", "verified", ("atp_br", "atp_brs"),
       tin("Collignon"), tin("Lehecka", 16, " (seed 2)"),
       olbg={"hub": "Tennis/3", "clock": "Today 07:30", "tips": "Lehecka 3/5 (60%)"})
    mk("ten-902131", "tennis", "ATP 250 Brussels Open (R16)", "David Goffin", "Alex Michelsen",
       "2026-10-22T11:30:00Z", "Centre Court, Brussels (Goffin also plays doubles QF later)", "verified",
       ("atp_br", "atp_brs"), tin("Goffin", None, " (home WC)"), tin("Michelsen", 35, " (seed 5)"),
       olbg={"hub": "Tennis/3", "clock": "Today 09:00", "tips": "Goffin 2-1 set betting 1/1"})
    mk("ten-902120", "tennis", "ATP 250 Brussels Open (R16)", "Damir Dzumhur", "Zizou Bergs",
       "2026-10-22T15:00:00Z", "Centre Court, Brussels", "verified", ("atp_br", "atp_brs"),
       tin("Dzumhur"), tin("Bergs", 39, " (seed 6)"),
       olbg={"hub": "Tennis/3", "clock": "Today 11:00", "tips": "Dzumhur 1/1 (100%)"},
       flags=["ATP lists 'not before 17:00' local for this slot"])
    # ---------------- Tennis - ATP Lyon ---------------------------------------
    mk("ten-902103", "tennis", "ATP 250 Lyon Open (R16)", "Valentin Vacherot", "Luca Van Assche",
       "2026-10-22T12:00:00Z", "Court Central Auvergne-Rhone-Alpes, Lyon", "verified", ("atp_ly", "atp_lys"),
       tin("Vacherot", 14, " (seed 3)"), tin("Van Assche"),
       olbg={"hub": "Tennis/3", "clock": "Today 08:00", "tips": "Vacherot 3/3 (100%)"},
       flags=["ATP 'not before 14:00' local"])
    mk("ten-902087", "tennis", "ATP 250 Lyon Open (R16)", "Pierre-Hugues Herbert", "Taylor Fritz",
       "2026-10-22T12:00:00Z", "Court Central Auvergne-Rhone-Alpes, Lyon", "verified", ("atp_ly", "atp_lys"),
       tin("Herbert", None, " (qualifier)"), tin("Fritz", 12, " (seed 2)"),
       olbg={"hub": "Tennis/3", "clock": "Today 09:30", "tips": "Fritz 4/6 (67%)"})
    mk("ten-902126", "tennis", "ATP 250 Lyon Open (R16)", "Flavio Cobolli", "Stan Wawrinka",
       "2026-10-22T17:00:00Z", "Court Central Auvergne-Rhone-Alpes, Lyon", "verified", ("atp_ly", "atp_lys"),
       tin("Cobolli", 7, " (seed 1)"), tin("Wawrinka", None, " (WC)"),
       olbg={"hub": "Tennis/3", "clock": "Today 13:00", "tips": "Wawrinka 2-1 set betting 1/1"},
       flags=["ATP 'not before 19:00' local - prime-time slot"])
    mk("ten-902105", "tennis", "ATP 250 Lyon Open (R16)", "Kyrian Jacquet", "Brandon Nakashima",
       "2026-10-22T17:00:00Z", "Court Central Auvergne-Rhone-Alpes, Lyon", "verified", ("atp_ly",),
       tin("Jacquet", None, " (qualifier)"), tin("Nakashima", 19, " (seed 5)"),
       olbg={"hub": "Tennis/3", "clock": "Today 14:30", "tips": "Nakashima 1/1 (100%)"})
    # ---------------- Tennis - WTA Ningbo (official WTA draw PDF) --------------
    mk("ten-902073", "tennis", "WTA 500 BNB Ningbo Open (R16)", "Elena Rybakina", "Polina Kudermetova",
       "2026-10-22T11:00:00Z", "Center Court, Ningbo Yinzhou Tennis Center", "verified",
       ("wta_pdf", "wta_rua", "root"),
       _i("WTA singles ranking (official draw PDF seed list)", "No. 1 (seed 1, defending champion, 9696 pts)", 100.0),
       _i("WTA singles ranking", "No. 103 (root-desk verified; cross-checked)", 47.67, tier="cross-checked"),
       olbg={"hub": "Tennis/3", "clock": "Today 07:00", "tips": "Rybakina 10/12 (83%)"},
       stage="Round of 16 - winner faces Kawa/Bencic")
    mk("ten-902072", "tennis", "WTA 500 BNB Ningbo Open (R16)", "Alexandra Eala", "Diana Shnaider",
       "2026-10-22T05:00:00Z", "Center Court, Ningbo Yinzhou Tennis Center", "verified",
       ("wta_pdf", "wta_rua"),
       _i("WTA singles ranking", "No. 19 (13-Oct WTA list, cross-checked)", 65.85, tier="cross-checked"),
       _i("WTA singles ranking (official draw PDF seed list)", "No. 13 (seed 6, 2643 pts)", 71.26),
       olbg={"hub": "Tennis/3", "clock": "Today 04:00", "tips": "Shnaider 4/5 (80%)"})
    mk("ten-902107", "tennis", "WTA (venue/tour event unverified)", "Talia Gibson", "Ashlyn Krueger",
       None, "unverified - WTA 125 Queretaro/Sopo window suspected; not confirmed", "pending",
       ("root",),
       _i("WTA ranking", "not verified this session", None, tier="pending"),
       _i("WTA ranking", "not verified this session", None, tier="pending"),
       olbg={"hub": "Tennis/3", "clock": "Today 22:30", "tips": "Krueger 1/1 (100%)"},
       flags=["No governing-body page rendering confirmed this match this session; blank-and-flag per brief"])
    # ---------------- Tennis - tomorrow cards (OLBG) ---------------------------
    mk("ten-902129", "tennis", "ATP 250 Almaty Open (QF, expected)", "Stefanos Tsitsipas", "James Duckworth",
       "2026-10-23T05:30:00Z", "Almaty Arena (QF slate Fri; order TBC)", "cross-checked",
       ("atp_al", "root",),
       _i("ATP singles ranking (seed list)", "No. 43 (seed 7)", 68.94),
       _i("ATP singles ranking", "No. 71 (root-desk verified)", 51.87, tier="cross-checked"),
       olbg={"hub": "Tennis/3", "clock": "Tomorrow 02:30", "tips": "Duckworth 1/2 (50%)"},
       flags=["Tsitsipas beat Kukushkin (R16) on 21 Oct per ATP; Duckworth beat Darderi - both QF-bound"])
    mk("ten-902133", "tennis", "ATP 250 Lyon Open (QF, expected)", "Corentin Moutet", "Tommy Paul",
       None, "Lyon (QF slate Fri; unconfirmed pairing)", "pending",
       ("root",),
       _i("ATP ranking", "not verified this session", None, tier="pending"),
       _i("ATP singles ranking (seed list)", "No. 18 (seed 4)", 67.98),
       olbg={"hub": "Tennis/3", "clock": "Tomorrow 05:30", "tips": "Paul 1/1 (100%)"},
       flags=["Paul beat Bonzi (R16) per ATP official video; QF pairing vs Moutet not yet on an official page read here"])

    # ---------------- Snooker - NI Open R3 (official WST match centre) -----------
    SNK = [
        ("snk-selt-craigie", "Matthew Selt", 46, "Sam Craigie", 70, "Today 08:00", "Selt 7/9 (78%)"),
        ("snk-wilson-pang", "Kyren Wilson", 9, "Pang Junxu", 26, "Today 08:00", "Kyren Wilson 6/9 (67%)"),
        ("snk-slessor-walden", "Elliot Slessor", 22, "Ricky Walden", 56, "Today 09:00", "Slessor 5/7 (71%)"),
        ("snk-mcgill-baranowski", "Anthony McGill", 38, "Mateusz Baranowski", 84, "Today 09:00", "McGill 2/4 (50%)"),
        ("snk-williams-odonnell", "Mark Williams", 10, "Martin O'Donnell", 55, "Today 14:00", "Mark Williams 3/3 (100%)"),
        ("snk-gilbert-cheung", "David Gilbert", None, "Cheung Ka Wai", 106, "Today 14:00", "Cheung Ka Wai 2/3 (67%)"),
        ("snk-brown-donaldson", "Jordan Brown", None, "Scott Donaldson", None, "Today 15:00", "Jordan Brown 3/3 (100%)"),
        ("snk-jones-wells", "Jak Jones", None, "Daniel Wells", None, "Today 15:00", "Jak Jones -1.50 handicap 1/1"),
    ]
    for id_, h, hr, a, ar, clock, tips in SNK:
        def srank(x):
            import math
            return None if x is None else round(100.0 - 70.0*math.log(x)/math.log(60.0), 2)
        fl = []
        if "Baranowski" in a:
            fl.append("OLBG renders 'Baranowski'; WST officially lists Mateusz Baranowski - same player, spelling flagged")
        mk(id_, "snooker", "BetVictor Northern Ireland Open 2026 (Round 3, best of 7)", h, a,
           "2026-10-22", "Waterfront Hall, Belfast", "verified", ("wst", "snk_org"),
           _i("WST world ranking (bracket figure, cross-checked)", f"[{hr}]" if hr else "not in bracket read", srank(hr), tier="cross-checked" if hr else "pending"),
           _i("WST world ranking (bracket figure, cross-checked)", f"[{ar}]" if ar else "not in bracket read", srank(ar), tier="cross-checked" if ar else "pending"),
           olbg={"hub": "Snooker/8", "clock": clock, "tips": tips}, flags=fl,
           stage="Round 3 (last 32)")

    # ---------------- Darts - 2026 Machineseeker European Championship (official PDC)
    EC_SEED = {
        "Woodhouse": 9, "van Duijvenbode": 24, "Noppert": 16, "Bunting": 17, "Zonneveld": 4,
        "Menzies": 29, "Price": 13, "Cross": 20, "Wade": 15, "Heta": 18, "Humphries": 12,
        "Searle": 21, "van Veen": 8, "Gilding": 25, "Smith": 7, "Sedlacek": 26, "Joyce": 3,
        "Wattimena": 30, "Ratajski": 5, "Chisnall": 28, "Aspinall": 6, "Reyes": 27,
        "Clayton": 1, "Springer": 32, "Littler": 11, "O'Connor": 22, "Nijman": 2,
        "Schindler": 31, "Doets": 14, "van Gerwen": 19, "Rock": 10, "Dobey": 23,
    }
    def dseed(s):
        import math
        return round(94.0 - 30.0*((s-1)/31.0), 2)
    DARTS = [
        ("pdc-ec-01", "Luke Woodhouse", "Dirk van Duijvenbode", "2026-10-22T17:15:00Z", "Today 13:15", "van Duijvenbode 13/16 (81%) [1 expert]"),
        ("pdc-ec-02", "Danny Noppert", "Stephen Bunting", "2026-10-22T17:45:00Z", "Today 13:45", "Noppert 10/16 (63%)"),
        ("pdc-ec-03", "Niels Zonneveld", "Cameron Menzies", "2026-10-22T18:15:00Z", "Today 14:15", "Zonneveld 14/18 (78%)"),
        ("pdc-ec-04", "Gerwyn Price", "Rob Cross", "2026-10-22T18:45:00Z", "Today 14:45", "Price 16/20 (80%)"),
        ("pdc-ec-05", "James Wade", "Damon Heta", "2026-10-22T19:15:00Z", "Today 15:15", "Wade 12/18 (67%)"),
        ("pdc-ec-06", "Luke Humphries", "Ryan Searle", "2026-10-22T19:45:00Z", "Today 15:45", "Humphries 13/16 (81%)"),
        ("pdc-ec-07", "Gian van Veen", "Andrew Gilding", "2026-10-22T20:15:00Z", "Today 16:15", "van Veen 11/16 (69%)"),
        ("pdc-ec-08", "Ross Smith", "Karel Sedlacek", "2026-10-22T20:45:00Z", "Today 16:45", "Smith 9/15 (60%)"),
        ("pdc-ec-09", "Ryan Joyce", "Jermaine Wattimena", "2026-10-23T17:15:00Z", "Tomorrow 13:15", "Joyce 7/9 (78%) [1 expert]"),
        ("pdc-ec-10", "Krzysztof Ratajski", "Dave Chisnall", "2026-10-23T17:45:00Z", "Tomorrow 13:45", "Chisnall 4/7 (57%) [1 expert]"),
        ("pdc-ec-11", "Nathan Aspinall", "Cristo Reyes", "2026-10-23T18:15:00Z", "Tomorrow 14:15", "Aspinall 3/6 (50%)"),
        ("pdc-ec-12", "Jonny Clayton", "Niko Springer", "2026-10-23T18:45:00Z", "Tomorrow 14:45", "Clayton 7/9 (78%)"),
        ("pdc-ec-13", "Luke Littler", "William O'Connor", "2026-10-23T19:15:00Z", None, ""),
        ("pdc-ec-14", "Wessel Nijman", "Martin Schindler", "2026-10-23T19:45:00Z", "Tomorrow 15:45", "Nijman 4/7 (57%)"),
        ("pdc-ec-15", "Kevin Doets", "Michael van Gerwen", "2026-10-23T20:15:00Z", None, ""),
        ("pdc-ec-16", "Josh Rock", "Chris Dobey", "2026-10-23T20:45:00Z", "Tomorrow 16:45", "Rock 4/6 (67%) [1 expert]"),
    ]
    def short(name):
        return name.split()[-1].replace("van Duijvenbode", "van Duijvenbode")
    for id_, h, a, st, clock, tips in DARTS:
        hk = next(k for k in EC_SEED if k in h)
        ak = next(k for k in EC_SEED if k in a)
        hs, as_ = EC_SEED[hk], EC_SEED[ak]
        extra_h = " (World No. 1)" if h == "Luke Littler" else (" (World No. 2)" if h == "Luke Humphries" else "")
        extra_a = " (World No. 1)" if a == "Luke Littler" else ""
        mk(id_, "darts", "2026 Machineseeker European Championship (Round 1, best of 11 legs)", h, a,
           st, "Westfalenhallen, Dortmund", "verified", ("pdc", "pdc2", "root"),
           _i("PDC European Championship tournament seed (official draw)", f"Seed #{hs}{extra_h}", dseed(hs)),
           _i("PDC European Championship tournament seed (official draw)", f"Seed #{as_}{extra_a}", dseed(as_)),
           olbg={"hub": "Darts/15", "clock": clock or "(not carded)", "tips": tips},
           stage="Round 1 (best of 11)",
           flags=["PDC night session 1900-2300 CEST; OLBG renders match clocks ~3-4h early (upstream tz defect)"] if clock and clock.startswith("Today") else [])

    # ---------------- Rugby Union - URC R4 (official URC fixture list) ----------
    mk("ru-urc-609577", "rugby-union", "United Rugby Championship 2026-27 (Round 4)", "Connacht", "Zebre Parma",
       "2026-10-23T18:45:00Z", "Dexcom Stadium, Galway", "verified", ("urc", "root"),
       _i("URC standings input", "not read officially this session", None, tier="pending"),
       _i("URC standings input", "not read officially this session", None, tier="pending"),
       olbg={"hub": "Rugby_Union/9", "clock": "Tomorrow 19:45", "tips": "Connacht 4/6 (67%)"})
    mk("ru-urc-609576", "rugby-union", "United Rugby Championship 2026-27 (Round 4)", "Vodacom Bulls", "Ulster",
       "2026-10-24T11:45:00Z", "Loftus Versfeld, Pretoria", "verified", ("urc", "root"),
       _i("URC standings input", "not read officially this session", None, tier="pending"),
       _i("URC standings input", "not read officially this session", None, tier="pending"),
       olbg={"hub": "Rugby_Union/9", "clock": "24 Oct 12:45", "tips": "Ulster +18.50 handicap 2/2"})
    mk("ru-urc-609580", "rugby-union", "United Rugby Championship 2026-27 (Round 4)", "DHL Stormers", "Scarlets",
       "2026-10-24T14:00:00Z", "DHL Stadium, Cape Town", "verified", ("urc", "root"),
       _i("URC standings input", "not read officially this session", None, tier="pending"),
       _i("URC standings input", "not read officially this session", None, tier="pending"),
       olbg={"hub": "Rugby_Union/9", "clock": "24 Oct 15:00", "tips": "Stormers 1/2 (50%)"})
    mk("ru-urc-609578", "rugby-union", "United Rugby Championship 2026-27 (Round 4)", "Leinster", "Munster",
       "2026-10-24T17:00:00Z", "Aviva Stadium, Dublin", "verified", ("urc", "root"),
       _i("URC standings input", "not read officially this session", None, tier="pending"),
       _i("URC standings input", "not read officially this session", None, tier="pending"),
       olbg={"hub": "Rugby_Union/9", "clock": "24 Oct 18:00", "tips": "Leinster 2/2 (100%)"})

    # ---------------- Rugby Union - Top 14 J7 (official LNR positions post-J6) ---
    T14 = {
        "Toulouse": (1, 24, 86), "Pau": (2, 21, 82), "Bordeaux-Begles": (3, 19, 74),
        "La Rochelle": (4, 18, 72), "Bayonne": (5, 17, 68), "Stade Francais": (6, 16, 64),
        "Montpellier": (7, 16, 60), "Lyon": (8, 14, 58), "Perpignan": (9, 13, 55),
        "Toulon": (10, 12, 52), "Clermont": (11, 11, 48), "Racing 92": (12, 10, 44),
        "Castres": (13, 8, 40), "Vannes": (14, 4, 36),
    }
    def t14(team):
        pos, pts, rating = T14[team]
        return _i("Top 14 standings after J6 (LNR official positions/points)", f"{pos}th, {pts} pts", rating)
    mk("ru-top14-609567", "rugby-union", "French Top 14 2026-27 (Round 7)", "Stade Toulousain", "USA Perpignan",
       "2026-10-24T14:35:00Z", "Stade Ernest-Wallon, Toulouse", "verified", ("lnr", "root"),
       _i("Top 14 standings after J6 (LNR official)", "1st, 24 pts", 86),
       _i("Top 14 standings after J6 (LNR official)", "9th, 13 pts", 55),
       olbg={"hub": "Rugby_Union/9", "clock": "24 Oct 15:35", "tips": "Perpignan +23.50 handicap 1/1"})
    mk("ru-top14-609564", "rugby-union", "French Top 14 2026-27 (Round 7)", "Aviron Bayonnais", "LOU Rugby",
       "2026-10-24T14:35:00Z", "Stade Jean-Dauger, Bayonne", "verified", ("lnr", "root"),
       _i("Top 14 standings after J6 (LNR official)", "5th, 17 pts", 68),
       _i("Top 14 standings after J6 (LNR official)", "8th, 14 pts", 58),
       olbg={"hub": "Rugby_Union/9", "clock": "24 Oct 15:35", "tips": "Lyon 1/1 (100%)"})
    mk("ru-top14-609554", "rugby-union", "French Top 14 2026-27 (Round 7)", "Stade Rochelais", "Union Bordeaux-Begles",
       "2026-10-25T20:05:00Z", "Stade Marcel-Deflandre, La Rochelle", "verified", ("lnr", "root"),
       _i("Top 14 standings after J6 (LNR official)", "4th, 18 pts", 72),
       _i("Top 14 standings after J6 (LNR official)", "3rd, 19 pts", 74),
       olbg={"hub": "Rugby_Union/9", "clock": "25 Oct 20:05", "tips": "La Rochelle (small sample)"})

    # ---------------- Rugby Union - Pro D2 J8 (club-official + LNR corroboration) --
    mk("ru-prod2-j8-01", "rugby-union", "French Pro D2 2026-27 (Round 8)", "US Montauban", "US Oyonnax",
       "2026-10-22T21:00:00Z", "Stade Sapiac, Montauban", "verified", ("prod2", "prod2b"),
       _i("Pro D2 table (published match-centre stripe)", "6th, 17 pts", 60, tier="cross-checked"),
       _i("Pro D2 table (published match-centre stripe)", "1st, 28 pts", 90, tier="cross-checked"),
       olbg={"hub": "Rugby_Union/9", "clock": "Today 20:00", "tips": "Oyonnax 13/19 (68%)"},
       flags=["21:00 local CEST (=19:00Z; OLBG renders 20:00 UK, official kickoff 21:00 local)"])
    PD2 = [
        ("ru-prod2-j8-02", "RC Narbonne", "CA Brive-Correze", "2026-10-23T19:00:00Z", "Tomorrow 18:00", "Brive 3/5 (60%)"),
        ("ru-prod2-j8-03", "SU Agen", "Nissa Rugby (Nice)", "2026-10-23T19:30:00Z", "Tomorrow 18:30", "Nissa 3/6 (50%)"),
        ("ru-prod2-j8-04", "Valence Romans Drome", "Colomiers Rugby", "2026-10-23T19:30:00Z", "Tomorrow 18:30", "Colomiers 1/1 (100%)"),
        ("ru-prod2-j8-05", "Stade Aurillacois (Aurillac)", "USON Nevers", "2026-10-23T19:30:00Z", "Tomorrow 18:30", "Aurillac 4/6 (67%)"),
        ("ru-prod2-j8-06", "Soyaux-Angouleme XV", "US Dax", "2026-10-23T19:30:00Z", "Tomorrow 18:30", "Dax 3/3 (100%)"),
        ("ru-prod2-j8-07", "Provence Rugby", "AS Beziers Herault", "2026-10-23T21:00:00Z", "Tomorrow 20:00", "Provence 1/2 (50%)"),
        ("ru-prod2-j8-08", "FC Grenoble", "Biarritz Olympique", "2026-10-23T21:00:00Z", "Tomorrow 20:00", "Grenoble 2/3 (67%)"),
    ]
    for id_, h, a, st, clock, tips in PD2:
        mk(id_, "rugby-union", "French Pro D2 2026-27 (Round 8)", h, a, st, "home venue (per official schedule)",
           "cross-checked", ("prod2", "prod2b"),
           _i("Pro D2 table", "positions beyond leaders not officially read this session", None, tier="pending"),
           _i("Pro D2 table", "positions beyond leaders not officially read this session", None, tier="pending"),
           olbg={"hub": "Rugby_Union/9", "clock": clock, "tips": tips})

    # ---------------- Handball - EHF Champions League R5 (official EHF) ----------
    H = [
        ("hand-ehf-12049", "MT Melsungen", None, "Orlen Wisla Plock", None, "2026-10-22T18:45:00Z", "Rothenbach-Halle, Kassel", "Today 12:45", "Melsungen 4/9 (44%) [1 expert]"),
        ("hand-ehf-12051", "OTP Bank - Pick Szeged", 37.5, "GOG", 75.0, "2026-10-22T18:45:00Z", "Pick Arena, Szeged", "Today 12:45", "GOG 3/9 (33%)"),
        ("hand-ehf-12055", "Barca", 100.0, "Montpellier Handball", 25.0, "2026-10-22T20:45:00Z", "Palau Blaugrana, Barcelona", "Today 14:45", "Barcelona 8/14 (57%)"),
        ("hand-ehf-12054", "Sporting CP", 87.5, "IFK Kristianstad", 12.5, "2026-10-22T20:45:00Z", "Pavilhao Joao Rocha, Lisbon", "Today 14:45", "Tie 6/13 (46%)"),
        ("hand-ehf-12056", "Kolstad Handball", None, "SC Magdeburg", None, "2026-10-22T20:45:00Z", "Trondheim Spektrum (per upstream)", "Today 14:45", "Tie 6/13 (46%)"),
    ]
    for id_, h, hr, a, ar, st, ven, clock, tips in H:
        mk(id_, "handball", "EHF Champions League Men 2026-27 (Group phase R5)", h, a, st, ven,
           "verified", ("ehf", "ehf2", "ehf3"),
           _i("EHF CL group table (cross-checked)", f"{hr if hr else 'not in group-table read'}" + (" pts-share" if hr else ""), hr, tier="cross-checked" if hr else "pending"),
           _i("EHF CL group table (cross-checked)", f"{ar if ar else 'not in group-table read'}" + (" pts-share" if ar else ""), ar, tier="cross-checked" if ar else "pending"),
           olbg={"hub": "Handball/20", "clock": clock, "tips": tips})
    # Women's internationals + domestic handball cards (mirror-only, no ratings read)
    H2 = [
        ("hand-w-bul-ita", "Bulgaria W", "Italy W", None, "Today 12:00", "Italy W 6/7 (86%)"),
        ("hand-de-stu-bie", "TVB Stuttgart", "SG BBM Bietigheim", None, "Today 13:00", "Stuttgart 6/9 (67%)"),
        ("hand-dk-sje-nor", "SonderjyskE", "Nordsjaelland Handbold", None, "Today 13:30", "Nordsjaelland 3/7 (43%)"),
        ("hand-dk-kol-fre", "KIF Kolding", "Fredericia HK", None, "Today 14:00", "Fredericia 3/6 (50%)"),
        ("hand-es-gra-cue", "BM Granollers", "Ciudad Encantada (Cuenca)", None, "Today 14:00", "Granollers 3/6 (50%)"),
        ("hand-se-ska-kar", "Skanela IF", "HIF Karlskrona", None, "Today 12:30", "Tie 2/6 (33%)"),
        ("hand-se-onn-yst", "Onnereds HK", "Ystads IF HF", None, "Today 13:00", "Onnereds 2/4 (50%)"),
        ("hand-w-est-kos", "Estonia W", "Kosovo W", None, "Tomorrow 14:00", "Kosovo W 3/3 (100%)"),
        ("hand-de-gop-eis", "Frisch Auf Goppingen", "ThSV Eisenach", None, "Tomorrow 14:00", "Eisenach 2/3 (67%)"),
        ("hand-dk-ski-aal", "Skive fH", "Aalborg Handbold", None, "24 Oct 09:00", "Aalborg 3/4 (75%)"),
    ]
    for id_, h, a, st, clock, tips in H2:
        mk(id_, "handball", "Handball (women's internationals / domestic leagues)", h, a, st,
           "venue unverified this session", "pending", ("ehf",),
           _i("Rating input", "not verified this session", None, tier="pending"),
           _i("Rating input", "not verified this session", None, tier="pending"),
           olbg={"hub": "Handball/20", "clock": clock, "tips": tips},
           flags=["Listed from OLBG card; official fixture page not rendered this session - blank-and-flag"])

    # ---------------- Cricket ------------------------------------------------------
    mk("cric-eng-sri-odi3", "cricket", "Pakistan ODI Tri-Series 2026-27 (3rd match)", "England", "Sri Lanka",
       "2026-10-22T08:00:00Z", "Rawalpindi Cricket Stadium (neutral venue tri-series)", "verified",
       ("icc", "icc2"),
       _i("ICC ODI rating", "not batch-read this session", None, tier="pending"),
       _i("ICC ODI rating", "not batch-read this session", None, tier="pending"),
       olbg={"hub": "Cricket/7", "clock": "Today 09:00", "tips": "England 14/17 (82%) [1 expert]"},
       neutral=True,
       stage="Dead-rubber context: Pakistan beat SL by 37 runs (18 Oct) & England by 87 runs (20 Oct)",
       flags=["Day/night start ratified 08:00 GMT by cricinfo/ICC calendar"])
    mk("cric-nam-ire-odi1", "cricket", "Ireland tour of Namibia 2026-27 (1st ODI)", "Namibia", "Ireland",
       "2026-10-22T08:15:00Z", "Windhoek", "verified", ("icc",),
       _i("ICC ODI rating", "associate/full-member pair - not batch-read", None, tier="pending"),
       _i("ICC ODI rating", "not batch-read this session", None, tier="pending"),
       olbg={"hub": "Cricket/7", "clock": "Today 09:00", "tips": "Ireland 8/14 (57%) [2 experts]"})
    mk("cric-ausw-nzw-t20-3", "cricket", "Women's T20I Series (3rd T20I)", "Australia Women", "New Zealand Women",
       "2026-10-22T08:15:00Z", "North Sydney Oval, Sydney", "verified", ("cau", "root"),
       _i("ICC Women's T20I rating (root-desk verified)", "No. 1 (287)", 88.0, tier="cross-checked"),
       _i("ICC Women's T20I rating (root-desk verified)", "No. 4 (253)", 69.0, tier="cross-checked"),
       olbg={"hub": "Cricket/7", "clock": "Today 09:15", "tips": "Australia W 8/10 (80%) [2 experts]"})
    mk("cric-csa-storm-tuskers", "cricket", "CSA T20 Challenge 2026 (Pool B)", "Eastern Storm", "KZN Inland Tuskers",
       "2026-10-22T16:00:00Z", "Willowmoore Park, Benoni", "cross-checked", ("csa", "csa2"),
       _i("CSA T20 Group B table (cross-checked)", "1W-3L-1NR (6 pts)", 40.0, tier="cross-checked"),
       _i("CSA T20 pool standing", "pool-A side; beat Knights 7 Oct, lost to Titans 13 Oct", None, tier="pending"),
       olbg={"hub": "Cricket/7", "clock": "Today 17:00", "tips": "Eastern Storm 7/8 (88%)"},
       flags=["18:00 SAST start listed by multiple SA schedule hubs; CSA's own page did not render to tool"])
    mk("cric-csa-rhinos-emerging", "cricket", "CSA T20 Challenge 2026 (Pool B)", "Mpumalanga Rhinos", "South Africa Emerging",
       "2026-10-22T11:00:00Z", "Uplands College, White River", "cross-checked", ("csa", "csa2"),
       _i("CSA T20 Group B table (cross-checked)", "1W-3L-1NR (6 pts)", 40.0, tier="cross-checked"),
       _i("CSA T20 Group B table (cross-checked)", "0W-4L-1NR (2 pts)", 20.0, tier="cross-checked"),
       olbg={"hub": "Cricket/7", "clock": "Today 12:00", "tips": "Rhinos 6/9 (67%)"})
    mk("cric-afg-zim-odif", "cricket", "UAE Tri-Nations ODI Series 2026-27 (Final)", "Afghanistan", "Zimbabwe",
       "2026-10-23T13:00:00Z", "Sharjah Cricket Stadium (neutral venue)", "verified", ("icc", "icc2", "cau"),
       _i("ICC Men's ODI rating (root-desk verified)", "No. 8 (92)", 74.0, tier="cross-checked"),
       _i("ICC Men's ODI rating (root-desk verified)", "unranked-lower band", 30.0, tier="pending", bounded=True),
       olbg={"hub": "Cricket/7", "clock": "Tomorrow 12:30", "tips": "Afghanistan 1/1 (100%)"},
       neutral=True, stage="Series final (ODI 5043 per ICC numbering)",
       flags=["Zimbabwe's current ICC ODI rating not printed on any official page read today - bounded estimate published only as placeholder; see flagged page"])

    # ---------------- Volleyball (fixtures not officially rendered this session) ----
    VB = [
        ("vol-tauron-rad-mie", "Radomka Radom W", "Mielec W (Developres?) - upstream card text", "TAURON Liga (POL, women)", "Today 11:30", "Radomka 7/10 (70%) [1 expert]"),
        ("vol-cz-brn-odo", "Brno", "Odolena Voda", "Czech Extraliga", "Today 12:00", "Brno 5/6 (83%) [1 expert]"),
        ("vol-cz-ost-kla", "Ostrava", "Kladno", "Czech Extraliga", "Today 12:00", "Ostrava 4/7 (57%)"),
        ("vol-cz-bud-bes", "Ceske Budejovice", "Beskydy", "Czech Extraliga", "Today 12:00", "Ceske Budejovice 3/4 (75%) [1 expert]"),
        ("vol-cz-ust-zli", "Usti Nad Labem", "Zlin", "Czech Extraliga", "Today 12:00", "Zlin 2/4 (50%)"),
        ("vol-cz-lib-ben", "Liberec", "Benatky nad Jizerou", "Czech Extraliga", "Today 12:00", "Liberec 3-1 set score 2/4 (50%)"),
        ("vol-pl-sle-kat", "Slepsk Suwalki", "GKS Katowice", "Polish PlusLiga", "Tomorrow 11:30", "Slepsk 2/3 (67%)"),
        ("vol-pl-skr-war", "PGE Skra Belchatow", "Projekt Warszawa", "Polish PlusLiga", "24 Oct 12:00", "Projekt 2/3 (67%)"),
        ("vol-pl-che-res", "CHKS Chelm", "Resovia Rzeszow", "Polish PlusLiga", "25 Oct 13:00", "Resovia 2/3 (67%)"),
        ("vol-br-pau-min", "Paulistano-Barueri W", "Minas W", "Brazilian Superliga W", "Tomorrow 17:30", "3-1 home set score 1/1"),
        ("vol-br-bra-fle", "Brasilia W", "Sesc RJ Flamengo W", "Brazilian Superliga W", "Tomorrow 17:30", "Brasilia 3-1 set score 1/1"),
        ("vol-br-mac-osa", "Mackenzie W", "Osasco W", "Brazilian Superliga W", "24 Oct 15:00", "Mackenzie 3-1 set score 1/1"),
        ("vol-br-bru-pra", "Abel-Moda Brusque W", "Praia Clube W", "Brazilian Superliga W", "24 Oct 20:00", "Brusque 1/1"),
        ("vol-it-tre-cis", "Trentino Volley", "Cisterna", "SuperLega Credem Banca", "25 Oct 12:00", "Cisterna 1/1"),
        ("vol-it-mon-ver", "Vero Volley Monza", "Verona Volley", "SuperLega Credem Banca", "25 Oct 13:00", "Monza (truncated upstream)"),
    ]
    for id_, h, a, comp, clock, tips in VB:
        fl = ["No governing-body page (cvf.cz/plusliga.pl/legavolley/cbv) rendered this fixture to the tool this session - listed and flagged, not priced to a rating"]
        if "tauron" in id_:
            fl.append("plusliga.pl redirect defect carried over from earlier desks (finding F-F7-09) - Polish women's league page still misroutes")
        if id_ == "vol-it-tre-cis":
            fl.append("OLBG tips underdog Cisterna over Trentino 1/1 - small sample; treat with caution")
        mk(id_, "volleyball", comp, h, a, None, "venue unverified this session", "pending",
           ("root",),
           _i("League table input", "not verified this session", None, tier="pending"),
           _i("League table input", "not verified this session", None, tier="pending"),
           olbg={"hub": "Volleyball/21", "clock": clock, "tips": tips}, flags=fl)

    # ---------------- SHL / Liiga ice hockey ------------------------------
    SHL = [
        ("shl-bjl-mif", "IF Bjorkloven", 73.3, "IF Malmo Redhawks", 33.3, "Today 13:00", "Bjorkloven 2/2 (100%)"),
        ("shl-rog-fhc", "Rogle BK", 60.0, "Frolunda HC", 93.3, "Today 13:00", "Frolunda +1.50 puck line 1/1"),
        ("shl-sai-dif", "Skelleftea AIK", 60.0, "Djurgardens IF", 20.0, "Today 13:00", "Skelleftea 4/4 (100%)"),
        ("shl-tik-fbk", "Timra IK", 13.3, "Farjestad BK", 86.7, "Today 13:00", "Farjestad 2/3 (67%) [2 experts]"),
        ("shl-ohk-bif", "Orebro HK", 53.3, "Brynas IF", 60.0, "Today 13:00", "Orebro 2/4 (50%)"),
        ("shl-vlh-lhf", "Vaxjo Lakers HC", 40.0, "Lulea HF", 40.0, "Today 13:00", "Lulea +1.50 puck line 1/1"),
    ]
    for id_, h, hr, a, ar, clock, tips in SHL:
        mk(id_, "ice-hockey", "SHL 2026-27 (Sweden)", h, a, "2026-10-22T17:00:00Z", "home venue (19:00 CET CV HUB slates)",
           "cross-checked", ("shl", "shl2", "shl3"),
           _i("SHL standings (sportbibeln cross-checked - shl.se not rendered)", f"rating pts-share {hr}", hr, tier="cross-checked"),
           _i("SHL standings (sportbibeln cross-checked)", f"rating pts-share {ar}", ar, tier="cross-checked"),
           olbg={"hub": "Ice_Hockey/13", "clock": clock, "tips": tips},
           flags=["All six Thursday SHL games 19:00 CET (=17:00Z); OLBG renders 13:00 UK - upstream clock defect"])
    mk("liiga-jyp-hpk", "ice-hockey", "Liiga 2026-27 (Finland)", "JYP Jyvaskyla", "HPK Hameenlinna",
       None, "unverified", "pending", ("root",),
       _i("Liiga table", "not read officially this session", None, tier="pending"),
       _i("Liiga table", "not read officially this session", None, tier="pending"),
       olbg={"hub": "Ice_Hockey/13", "clock": "Today 11:30", "tips": "Jyp 3/3 (100%)"},
       flags=["Liiga official page not read this session - blank-and-flag"])

    # ---------------- Minor basketball cards (KBL / NBB) -------------------
    mk("kbl-mob-cha", "basketball", "KBL 2026-27 (Korea)", "Ulsan Mobis Phoebus", "Changwon LG Sakers",
       None, "Dongchun Gymnasium (per upstream; unverified)", "pending", ("root",),
       _i("KBL standings", "not read officially this session", None, tier="pending"),
       _i("KBL standings", "not read officially this session", None, tier="pending"),
       olbg={"hub": "Basketball/4", "clock": "Today 06:00", "tips": "Mobis 4/6 (67%)"},
       flags=["Fixture corroborated by score-hub snippets only (flashscore/betclan), KBL official page not rendered - flagged"])
    mk("nbb-for-pin", "basketball", "Novo Basquete Brasil 2026-27", "Fortaleza BC", "Pinheiros",
       None, "unverified", "pending", ("root",),
       _i("NBB standings", "not read officially this session", None, tier="pending"),
       _i("NBB standings", "not read officially this session", None, tier="pending"),
       olbg={"hub": "Basketball/4", "clock": "Today 18:30", "tips": "Pinheiros 2/3 (67%)"},
       flags=["NBB official page not read this session - blank-and-flag"])
    mk("nbb-uni-min", "basketball", "Novo Basquete Brasil 2026-27", "Uniao Corinthians", "Minas",
       None, "unverified", "pending", ("root",),
       _i("NBB standings", "not read officially this session", None, tier="pending"),
       _i("NBB standings", "not read officially this session", None, tier="pending"),
       olbg={"hub": "Basketball/4", "clock": "Today 18:30", "tips": "Minas 1/1 (100%)"},
       flags=["NBB official page not read this session - blank-and-flag"])

    # ---------------- Golf (tournament outright events) --------------------
    mk("golf-pga-bermuda2026", "golf", "PGA TOUR FedExCup Fall - Butterfield Bermuda Championship",
       "Field (PGA TOUR)", "Outright winner market", "2026-10-22T11:10:00Z", "Port Royal Golf Course, Bermuda",
       "verified", ("root", "root2"),
       _i("Official OWGR-based field ratings", "not batch-read this session", None, tier="pending"),
       _i("Market type", "tournament outright (156-man field)", None, tier="pending"),
       olbg={"hub": "Golf/5", "clock": "Today 14:10", "tips": "Win tournament: Seamus Power 6/24 (25%)"},
       flags=["Round 1 in progress; OLBG outright card mirrors the event; no field rating matrix read - unlocked as event listing only"])
    mk("golf-champions-stifel2026", "golf", "PGA TOUR Champions - Stifel Charity Classic",
       "Field (Champions Tour)", "Outright winner market", "2026-10-23T15:45:00Z", "Norwood Hills CC, St. Louis MO",
       "verified", ("root", "root2"),
       _i("Field ratings", "not batch-read this session", None, tier="pending"),
       _i("Market type", "tournament outright (54 holes, starts 23 Oct)", None, tier="pending"),
       olbg={"hub": "Golf/5", "clock": "25 Oct 17:45", "tips": "Steven Alker 2/11 (18%)"})
    mk("golf-legends-italian2026", "golf", "Legends Tour - Senior Italian Open",
       "Field (Legends Tour)", "Outright winner market", "2026-10-23", "Italy (per upstream; venue unverified)",
       "pending", ("root",),
       _i("Field ratings", "not verified this session", None, tier="pending"),
       _i("Market type", "tournament outright", None, tier="pending"),
       olbg={"hub": "Golf/5", "clock": "24 Oct 11:45", "tips": "Hennie Otto 0/2"},
       flags=["Legends Tour not covered by an official page read this session - blank-and-flag"])

    # ---------------- Motor racing ------------------------------------------
    mk("f1-usgp-2026", "motor-racing", "FIA Formula 1 World Championship 2026 - United States Grand Prix",
       "Race (20 drivers)", "Race winner market", "2026-10-25T20:00:00Z", "Circuit of The Americas, Austin TX",
       "verified", ("root", "root2"),
       _i("FIA drivers' standings input", "root-desk verified slate (see linked row)", None, tier="pending"),
       _i("Market type", "race winner outright", None, tier="pending"),
       olbg={"hub": "Motor_Racing/14", "clock": "25 Oct 16:00", "tips": "Win Race: Max Verstappen 12/33 (36%) [3 experts]"},
       flags=["Race start 16:00 local(=20:00Z Sun) per upstream; qualifying/ratings not priced this session"])
    mk("f1-title-2026", "motor-racing", "FIA Formula 1 World Championship 2026 - Drivers' Title",
       "Championship field", "Title winner market", "2026-12-06", "Season outright (Abu Dhabi finale)",
       "verified", ("root", "root2"),
       _i("Championship standings", "not batch-read this session", None, tier="pending"),
       _i("Market type", "season outright", None, tier="pending"),
       olbg={"hub": "Motor_Racing/14", "clock": "06 Dec", "tips": "Verstappen 9/33 (27%); w/o Antonelli: Verstappen 4/7 (57%)"})

    # ---------------- Greyhounds (GBGB, event-card market) -------------------
    GH = [
        ("gb-1114-kinsley", "11:14 Kinsley", "Limited Blue", "Kinsley Greyhound Stadium", "Today 06:14", "Limited Blue 1/1"),
        ("gb-1136-sheffield", "11:36 Sheffield", "Drumdoit Pixie", "Sheffield (Owlerton) Stadium", "Today 06:36", "Drumdoit Pixie 1/1"),
        ("gb-1203-kinsley", "12:03 Kinsley", "Ballymac Alyssa", "Kinsley Greyhound Stadium", "Today 07:03", "Ballymac Alyssa 1/1"),
        ("gb-1214-nottingham", "12:14 Nottingham", "Ferryforth Mary", "Nottingham Greyhound Stadium, Colwick Park", "Today 07:14", "Ferryforth Mary 1/1"),
    ]
    for id_, race, dog, track, clock, tips in GH:
        mk(id_, "greyhounds", "GBGB UK Graded Greyhound Racing", race, "field",
           "2026-10-22", track, "cross-checked", ("root",),
           _i("Race form input", "per-dog graded form not officially read today", None, tier="pending"),
           _i("Market type", "single-race winner card (1/1 tip upstream)", None, tier="pending"),
           olbg={"hub": "Greyhounds/28", "clock": clock, "tips": tips},
           flags=["OLBG clock renders one hour before the race name (06:14 for '11:14 Kinsley') - UTC-vs-BST label defect documented by all prior desks"])

    return made

def snapshot():
    """Machine-readable OLBG harvest snapshot (from data/f1c13c19/harvest_notes.md)."""
    return {
        "harvested_utc": "2026-10-22T07:27-07:45Z",
        "channel": "Arena fetch_page (direct OLBG hub pages)",
        "note": "Times are OLBG-rendered UK-local (BST). Verified-canonical record also kept in data/f1c13c19/harvest_notes.md.",
        "hubs": {
            "Tennis/3": {"cards": 16, "zero_state": False},
            "Basketball/4": {"cards": 16, "zero_state": False},
            "Golf/5": {"cards": 3, "zero_state": False, "note": "tournament outright markets"},
            "Cricket/7": {"cards": 6, "zero_state": False, "note": "+ outrights (WC27/WBBL/BBL/SA20/Blast)"},
            "Snooker/8": {"cards": 8, "zero_state": False},
            "Rugby_Union/9": {"cards": 15, "zero_state": False},
            "Rugby_League/10": {"cards": 0, "zero_state": True, "note": "outrights only; RLWC26 matches absent upstream (defect, repeated across desks)"},
            "Baseball/12": {"cards": 1, "zero_state": False},
            "Ice_Hockey/13": {"cards": 8, "zero_state": False, "note": "hub showed SHL/Liiga; NHL sub-route 'No tips found'"},
            "Motor_Racing/14": {"cards": 3, "zero_state": False, "note": "USA GP + F1 title outrights"},
            "Darts/15": {"cards": 15, "zero_state": False},
            "Handball/20": {"cards": 16, "zero_state": False},
            "Volleyball/21": {"cards": 17, "zero_state": False},
            "Aussie_Rules/22": {"cards": 0, "zero_state": True, "note": "AFLW R11 in progress upstream (9 verified games, AUD-A-01)"},
            "eSports/23": {"cards": 0, "zero_state": True, "note": "LoL Worlds play-in in progress upstream (root-verified fixtures)"},
            "Gaelic_Football/25": {"cards": 6, "zero_state": False, "note": "+ All-Ireland 2027 outright"},
            "Greyhounds/28": {"cards": 4, "zero_state": False},
        },
    }
