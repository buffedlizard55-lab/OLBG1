"""Session 9dfd0b48-olbg1 (task T44) — verified inputs for the 22–24 Oct 2026 matchday desk.

Every number in this file was read from the cited official page during the session
(fetch timestamps in SOURCES).  Nothing is inferred: where a figure could not be read
from an official source it is left as None and the fixture is routed to the flag list.

OLBG hub clock: times on olbg.com hub pages render in US Eastern (UTC-4 on these dates;
see reports/OLBG_REVERSE_ENGINEERING.md).  OLBG times below are already converted to UTC.
"""

HARVEST_UTC = "2026-10-22T03:10Z"

SOURCES = {
    # --- official ---
    "atp_sched_almaty": {"url": "https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule",
                         "title": "ATP Tour — Almaty order of play, Thu 22 Oct 2026 (Day 6)", "fetched": "2026-10-22T03:40Z"},
    "atp_sched_brussels": {"url": "https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule",
                           "title": "ATP Tour — Brussels order of play, Thu 22 Oct 2026 (Day 6)", "fetched": "2026-10-22T03:44Z"},
    "atp_sched_lyon": {"url": "https://www.atptour.com/en/scores/current/lyon/496/daily-schedule",
                       "title": "ATP Tour — Lyon order of play, Thu 22 Oct 2026 (Day 5)", "fetched": "2026-10-22T03:40Z"},
    "atp_scores": {"url": "https://www.atptour.com/en/scores/current",
                   "title": "ATP Tour — completed R16 results 21 Oct 2026 (Duckworth d. Darderi, Mannarino d. Rublev, Cerundolo d. Damm, Griekspoor d. Navone, Paul d. Bonzi, Musetti d. Kouame)", "fetched": "2026-10-22T03:40Z"},
    "atp_rank": {"url": "https://www.atptour.com/en/rankings/singles?rankRange=0-100",
                 "title": "PIF ATP Rankings (singles), list dated 2026-10-19, ranks 1–100", "fetched": "2026-10-22T03:48Z"},
    "atp_rank2": {"url": "https://www.atptour.com/en/rankings/singles?rankRange=101-200",
                  "title": "PIF ATP Rankings (singles), list dated 2026-10-19, ranks 101–191 read", "fetched": "2026-10-22T04:05Z"},
    "wst_matches": {"url": "https://www.wst.tv/matches",
                    "title": "World Snooker Tour — Northern Ireland Open match list (R1/R2 results, R3 schedule Thu 22 Oct)", "fetched": "2026-10-22T03:36Z"},
    "wst_rank": {"url": "https://www.wst.tv/rankings/abfba8fe-1423-5a2a-a96b-d77e8b413ca8?showLive=false",
                 "title": "WST — Johnstone's Paint World Rankings (official list, top 36 shown)", "fetched": "2026-10-22T04:12Z"},
    "el_gc": {"url": "https://www.euroleaguebasketball.net/en/euroleague/game-center/",
              "title": "EuroLeague Game Center — Round 7 (21–23 Oct 2026)", "fetched": "2026-10-22T03:36Z"},
    "el_stand": {"url": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
                 "title": "EuroLeague 2026-27 regular-season standings (after Round 6 + HTA/VIR of R7)", "fetched": "2026-10-22T03:52Z"},
    "mlb_sched": {"url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-28",
                  "title": "MLB Stats API — World Series schedule (games 1–5)", "fetched": "2026-10-22T03:30Z"},
    "mlb_stand_al": {"url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason",
                     "title": "MLB Stats API — 2026 AL regular-season standings", "fetched": "2026-10-22T04:00Z"},
    "mlb_stand_nl": {"url": "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason",
                     "title": "MLB Stats API — 2026 NL regular-season standings", "fetched": "2026-10-22T04:02Z"},
    "nhl_sched": {"url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
                  "title": "NHL API — schedule week of 22 Oct 2026 (12 games on 22 Oct; only first chunk read)", "fetched": "2026-10-22T03:30Z"},
    # --- blocked / failed official endpoints (recorded for the flag page) ---
    "pdc_blocked": {"url": "https://www.pdc.tv/", "title": "PDC — every page returned only a CookieYes consent wall (7 chunks, no content)", "fetched": "2026-10-22T03:28Z"},
    "nba_blocked": {"url": "https://www.nba.com/schedule", "title": "NBA — cdn.nba.com todaysScoreboard returned HTTP 500; schedule not verified", "fetched": "2026-10-22T03:30Z"},
    "wta_blocked": {"url": "https://www.wtatennis.com/tournaments/405/osaka/2026/draws", "title": "WTA — Osaka (Kinoshita Group Japan Open) draw page rendered only the notification panel; no match data", "fetched": "2026-10-22T03:44Z"},
    "atp_no_draw": {"url": "https://www.atptour.com/en/scores/current/basel/328/draws", "title": "ATP Basel/Vienna — 'no draw available' (events start 26 Oct)", "fetched": "2026-10-22T03:34Z"},
    # --- OLBG hubs ---
    "olbg_tennis": {"url": "https://www.olbg.com/betting-tips/Tennis/3", "title": "OLBG Tennis hub", "fetched": HARVEST_UTC},
    "olbg_basketball": {"url": "https://www.olbg.com/betting-tips/Basketball/4", "title": "OLBG Basketball hub", "fetched": HARVEST_UTC},
    "olbg_snooker": {"url": "https://www.olbg.com/betting-tips/Snooker/8", "title": "OLBG Snooker hub", "fetched": HARVEST_UTC},
    "olbg_darts": {"url": "https://www.olbg.com/betting-tips/Darts/15", "title": "OLBG Darts hub", "fetched": HARVEST_UTC},
    "olbg_icehockey": {"url": "https://www.olbg.com/betting-tips/Ice_Hockey/13", "title": "OLBG Ice Hockey hub", "fetched": HARVEST_UTC},
    "olbg_baseball": {"url": "https://www.olbg.com/betting-tips/Baseball/12", "title": "OLBG Baseball hub", "fetched": HARVEST_UTC},
    "olbg_golf": {"url": "https://www.olbg.com/betting-tips/Golf/5", "title": "OLBG Golf hub", "fetched": HARVEST_UTC},
    "olbg_cricket": {"url": "https://www.olbg.com/betting-tips/Cricket/7", "title": "OLBG Cricket hub", "fetched": HARVEST_UTC},
    "olbg_rugbyunion": {"url": "https://www.olbg.com/betting-tips/Rugby_Union/9", "title": "OLBG Rugby Union hub", "fetched": HARVEST_UTC},
    "olbg_rugbyleague": {"url": "https://www.olbg.com/betting-tips/Rugby_League/10", "title": "OLBG Rugby League hub", "fetched": HARVEST_UTC},
    "olbg_motor": {"url": "https://www.olbg.com/betting-tips/Motor_Racing/14", "title": "OLBG Motor Racing hub", "fetched": HARVEST_UTC},
    "olbg_handball": {"url": "https://www.olbg.com/betting-tips/Handball/20", "title": "OLBG Handball hub", "fetched": HARVEST_UTC},
    "olbg_volleyball": {"url": "https://www.olbg.com/betting-tips/Volleyball/21", "title": "OLBG Volleyball hub", "fetched": HARVEST_UTC},
    "olbg_aussie": {"url": "https://www.olbg.com/betting-tips/Aussie_Rules/22", "title": "OLBG Aussie Rules hub", "fetched": HARVEST_UTC},
    "olbg_esports": {"url": "https://www.olbg.com/betting-tips/eSports/23", "title": "OLBG eSports hub", "fetched": HARVEST_UTC},
    "olbg_gaelic": {"url": "https://www.olbg.com/betting-tips/Gaelic_Football/25", "title": "OLBG Gaelic Football hub", "fetched": HARVEST_UTC},
    "olbg_greyhounds": {"url": "https://www.olbg.com/betting-tips/Greyhounds/28", "title": "OLBG Greyhounds hub", "fetched": HARVEST_UTC},
}

# ---------------------------------------------------------------- ATP (points, rank; list 2026-10-19)
ATP = {
    "Daniil Medvedev": (5, 3660), "Flavio Cobolli": (6, 3640), "Taylor Fritz": (14, 2880),
    "Brandon Nakashima": (17, 2375), "Alexander Bublik": (19, 2275), "Jiri Lehecka": (20, 2235),
    "Karen Khachanov": (25, 1990), "Valentin Vacherot": (32, 1480), "Alex Michelsen": (37, 1370),
    "Stefanos Tsitsipas": (39, 1330), "Zizou Bergs": (41, 1220), "Luca Van Assche": (48, 1065),
    "Raphael Collignon": (55, 978), "Fabian Marozsan": (64, 860), "Daniel Altmaier": (65, 849),
    "Mattia Bellucci": (68, 812), "Tomas Machac": (72, 779), "James Duckworth": (73, 774),
    "Damir Dzumhur": (83, 712), "Kyrian Jacquet": (85, 703), "Terence Atmane": (98, 616),
    "Sho Shimabukuro": (109, 555), "Stan Wawrinka": (140, 401), "Borna Gojo": (148, 378),
    # not inside the 191 ranks read -> None (unpriced, flagged)
    "Pierre-Hugues Herbert": (None, None), "David Goffin": (None, None),
}

# ---------------------------------------------------------------- WST world ranking money (top 36 list)
WST = {
    "Mark Williams": (8, 747400), "Kyren Wilson": (9, 716800), "Elliot Slessor": (23, 329200),
    "Jak Jones": (24, 319300), "Pang Junxu": (29, 272750), "David Gilbert": (34, 221200),
}
WST_36TH_MONEY = 198500  # Jackson Page, 36th: every player not in the list is verified to sit below this

# ---------------------------------------------------------------- EuroLeague standings (GP, W, L, PF, PA, home, away, L10)
EL = {
    "Panathinaikos AKTOR Athens": (6, 5, 1, 528, 438, "4-1", "1-0", "5-1"),
    "Fenerbahce Tarfin Istanbul": (6, 5, 1, 501, 447, "5-0", "0-1", "5-1"),
    "Olympiacos Piraeus": (6, 5, 1, 564, 524, "1-0", "4-1", "5-1"),
    "Valencia Basket": (6, 4, 2, 583, 537, "2-2", "2-0", "4-2"),
    "Crvena Zvezda Meridianbet Belgrade": (6, 4, 2, 485, 457, "2-2", "2-0", "4-2"),
    "Dubai Basketball": (6, 4, 2, 490, 493, "2-1", "2-1", "4-2"),
    "Real Madrid": (6, 3, 3, 554, 531, "2-0", "1-3", "3-3"),
    "FC Barcelona": (6, 3, 3, 534, 525, "2-2", "1-1", "3-3"),
    "Besiktas Istanbul": (6, 3, 3, 554, 555, "1-2", "2-1", "3-3"),
    "Partizan Mozzart Bet Belgrade": (6, 3, 3, 466, 471, "1-1", "2-2", "3-3"),
    "Anadolu Efes Istanbul": (6, 2, 4, 492, 510, "1-1", "1-3", "2-4"),
    "Zalgiris Kaunas": (6, 2, 4, 490, 517, "0-2", "2-2", "2-4"),
    "FC Bayern Munich": (6, 2, 4, 521, 552, "0-2", "2-2", "2-4"),
    "Maccabi Rapyd Tel Aviv": (6, 2, 4, 509, 540, "1-1", "1-3", "2-4"),
    "LDLC ASVEL Villeurbanne": (6, 2, 4, 527, 572, "1-2", "1-2", "2-4"),
    "Paris Basketball": (6, 1, 5, 504, 545, "1-3", "0-2", "1-5"),
    "Armani Olimpia Milan": (6, 1, 5, 504, 559, "1-2", "0-3", "1-5"),
    "Kosner Baskonia Vitoria-Gasteiz": (6, 1, 5, 504, 564, "1-3", "0-2", "1-5"),
}

# ---------------------------------------------------------------- MLB 2026 regular season
MLB = {
    "Milwaukee Brewers": {"w": 103, "l": 59, "rs": 832, "ra": 618, "home": "55-26", "streak": "W5", "src": "mlb_stand_nl"},
    "Tampa Bay Rays": {"w": 98, "l": 64, "rs": 736, "ra": 650, "home": "55-26", "streak": "L1", "src": "mlb_stand_al"},
}

OLBG_EV = "https://www.olbg.com/betting-tips/{sport}/All_{sport}/All_Events/{slug}/{sid}?event_id={eid}"


def olbg(sport, sid, slug, eid):
    return OLBG_EV.format(sport=sport, sid=sid, slug=slug, eid=eid)


# ---------------------------------------------------------------- verified fixtures
# kind: tennis | snooker | basketball | baseball
FIXTURES = [
    # ---- ATP Almaty (UTC+5). Center Court starts 11:30 local = 06:30Z
    dict(id="T01", kind="tennis", sport="Tennis", comp="ATP 250 Almaty — R16", a="Terence Atmane", b="Mattia Bellucci",
         start="2026-10-22T06:30Z", note="Center Court, first match (11:30 local)", src=["atp_sched_almaty", "atp_rank"],
         olbg=olbg("Tennis", 3, "Terence_Atmane_vs_Mattia_Bellucci", 902109), olbg_time="2026-10-22T06:30Z", olbg_tips="no consensus shown"),
    dict(id="T02", kind="tennis", sport="Tennis", comp="ATP 250 Almaty — R16", a="Tomas Machac", b="Karen Khachanov",
         start="2026-10-22T08:00Z", note="Center Court, not before 13:00 local; Khachanov seeded 5", src=["atp_sched_almaty", "atp_rank"],
         olbg=olbg("Tennis", 3, "Tomas_Machac_vs_Karen_Khachanov", 902110), olbg_time="2026-10-22T08:00Z", olbg_tips="no consensus shown"),
    dict(id="T03", kind="tennis", sport="Tennis", comp="ATP 250 Almaty — R16", a="Daniil Medvedev", b="Sho Shimabukuro",
         start="2026-10-22T09:30Z", note="Center Court, followed by (OLBG lists 05:30 ET = 09:30Z); Medvedev seeded 1", src=["atp_sched_almaty", "atp_rank", "atp_rank2"],
         olbg=olbg("Tennis", 3, "Daniil_Medvedev_vs_Sho_Shimabukuro", 902069), olbg_time="2026-10-22T09:30Z", olbg_tips="no consensus shown"),
    dict(id="T04", kind="tennis", sport="Tennis", comp="ATP 250 Almaty — R16", a="Alexander Bublik", b="Fabian Marozsan",
         start="2026-10-22T14:30Z", note="Center Court, not before 19:30 local (after concert); Bublik seeded 3", src=["atp_sched_almaty", "atp_rank"],
         olbg=olbg("Tennis", 3, "Alexander_Bublik_vs_Fabian_Marozsan", 902082), olbg_time="2026-10-22T14:30Z", olbg_tips="no consensus shown"),
    # ---- ATP Brussels (UTC+2). Centre Court starts 13:30 local = 11:30Z
    dict(id="T05", kind="tennis", sport="Tennis", comp="ATP 250 Brussels — R16", a="Raphael Collignon", b="Jiri Lehecka",
         start="2026-10-22T11:30Z", note="Centre Court, first match; Lehecka seeded 2", src=["atp_sched_brussels", "atp_rank"],
         olbg=olbg("Tennis", 3, "Raphael_Collignon_vs_Jiri_Lehecka", 902104), olbg_time="2026-10-22T11:30Z", olbg_tips="no consensus shown"),
    dict(id="T06", kind="tennis", sport="Tennis", comp="ATP 250 Brussels — R16", a="David Goffin", b="Alex Michelsen",
         start="2026-10-22T13:00Z", note="Centre Court, followed by (OLBG 09:00 ET); Goffin wildcard, Michelsen seeded 5", src=["atp_sched_brussels", "atp_rank"],
         olbg=olbg("Tennis", 3, "David_Goffin_vs_Alex_Michelsen", 902131), olbg_time="2026-10-22T13:00Z", olbg_tips="no consensus shown"),
    dict(id="T07", kind="tennis", sport="Tennis", comp="ATP 250 Brussels — R16", a="Damir Dzumhur", b="Zizou Bergs",
         start="2026-10-22T15:00Z", note="Centre Court, not before 17:00 local; Bergs seeded 6", src=["atp_sched_brussels", "atp_rank"],
         olbg=olbg("Tennis", 3, "Damir_Dzumhur_vs_Zizou_Bergs", 902120), olbg_time="2026-10-22T15:00Z", olbg_tips="no consensus shown"),
    # ---- ATP Lyon (UTC+2). Court Central starts 12:00 local; R16 not before 14:00 = 12:00Z
    dict(id="T08", kind="tennis", sport="Tennis", comp="ATP 250 Lyon — R16", a="Valentin Vacherot", b="Luca Van Assche",
         start="2026-10-22T12:00Z", note="Court Central, not before 14:00 local; Vacherot seeded 3", src=["atp_sched_lyon", "atp_rank"],
         olbg=olbg("Tennis", 3, "Valentin_Vacherot_vs_Luca_Van_Assche", 902103), olbg_time="2026-10-22T12:00Z", olbg_tips="no consensus shown"),
    dict(id="T09", kind="tennis", sport="Tennis", comp="ATP 250 Lyon — R16", a="Pierre-Hugues Herbert", b="Taylor Fritz",
         start="2026-10-22T13:30Z", note="Court Central, followed by (OLBG 09:30 ET); Herbert qualifier, Fritz seeded 2", src=["atp_sched_lyon", "atp_rank"],
         olbg=olbg("Tennis", 3, "Pierre_Hugues_Herbert_vs_Taylor_Fritz", 902087), olbg_time="2026-10-22T13:30Z", olbg_tips="no consensus shown"),
    dict(id="T10", kind="tennis", sport="Tennis", comp="ATP 250 Lyon — R16", a="Flavio Cobolli", b="Stan Wawrinka",
         start="2026-10-22T17:00Z", note="Court Central, not before 19:00 local; Cobolli seeded 1, Wawrinka wildcard", src=["atp_sched_lyon", "atp_rank", "atp_rank2"],
         olbg=olbg("Tennis", 3, "Flavio_Cobolli_vs_Stan_Wawrinka", 902126), olbg_time="2026-10-22T17:00Z", olbg_tips="Wawrinka 1/1"),
    dict(id="T11", kind="tennis", sport="Tennis", comp="ATP 250 Lyon — R16", a="Kyrian Jacquet", b="Brandon Nakashima",
         start="2026-10-22T18:30Z", note="Court Central, followed by (OLBG 14:30 ET); Jacquet qualifier, Nakashima seeded 5", src=["atp_sched_lyon", "atp_rank"],
         olbg=olbg("Tennis", 3, "Kyrian_Jacquet_vs_Brandon_Nakashima", 902105), olbg_time="2026-10-22T18:30Z", olbg_tips="no consensus shown"),
    # ---- WST Northern Ireland Open R3 (Belfast, UTC+1). wst.tv lists session times in the viewer clock (UTC-4 here) -> +4h
    dict(id="S01", kind="snooker", sport="Snooker", comp="NI Open — Round 3 (best of 7)", a="Matthew Selt", b="Sam Craigie",
         start="2026-10-22T12:00Z", note="Match 51. Selt bt Heathcote 4-2 (R2), Vafaei 4-3 (R1); Craigie bt Xu Si 4-3, Xiao Guodong 4-3", src=["wst_matches", "wst_rank"],
         olbg=olbg("Snooker", 8, "Matthew_Selt_vs_Sam_Craigie", 9942), olbg_time="2026-10-22T12:00Z", olbg_tips="Selt 1/2"),
    dict(id="S02", kind="snooker", sport="Snooker", comp="NI Open — Round 3 (best of 7)", a="Kyren Wilson", b="Pang Junxu",
         start="2026-10-22T12:00Z", note="Match 50. Wilson bt Un-Nooh 4-2, Mertens 4-0; Pang bt Davies 4-3, Burden 4-2", src=["wst_matches", "wst_rank"],
         olbg=olbg("Snooker", 8, "Kyren_Wilson_vs_Pang_Junxu", 9940), olbg_time="2026-10-22T12:00Z", olbg_tips="Wilson 1/2"),
    dict(id="S03", kind="snooker", sport="Snooker", comp="NI Open — Round 3 (best of 7)", a="Anthony McGill", b="Mateusz Baranowski",
         start="2026-10-22T13:00Z", note="Match 49. McGill bt Lisowski 4-1; Baranowski bt Wang Xinbo 4-3", src=["wst_matches", "wst_rank"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    dict(id="S04", kind="snooker", sport="Snooker", comp="NI Open — Round 3 (best of 7)", a="Elliot Slessor", b="Ricky Walden",
         start="2026-10-22T13:00Z", note="Match 52. Slessor bt Jamie Jones 4-1; Walden bt Joe O'Connor 4-3", src=["wst_matches", "wst_rank"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    dict(id="S05", kind="snooker", sport="Snooker", comp="NI Open — Round 3 (best of 7)", a="Mark Williams", b="Martin O'Donnell",
         start="2026-10-22T18:00Z", note="Match 54. Williams bt Zhang Anda 4-2, Robbie Williams 4-2; O'Donnell bt Brecel 4-2, Trump 4-3", src=["wst_matches", "wst_rank"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    dict(id="S06", kind="snooker", sport="Snooker", comp="NI Open — Round 3 (best of 7)", a="David Gilbert", b="Ka Wai Cheung",
         start="2026-10-22T18:00Z", note="Match 53. Gilbert bt Gao Yang 4-3; Cheung bt Bingham 4-0, O'Sullivan 4-3", src=["wst_matches", "wst_rank"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    dict(id="S07", kind="snooker", sport="Snooker", comp="NI Open — Round 3 (best of 7)", a="Jordan Brown", b="Scott Donaldson",
         start="2026-10-22T19:00Z", note="Match 56. Brown bt Holt 4-3, Allen 4-2; Donaldson bt Saengkham 4-1", src=["wst_matches", "wst_rank"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    dict(id="S08", kind="snooker", sport="Snooker", comp="NI Open — Round 3 (best of 7)", a="Jak Jones", b="Daniel Wells",
         start="2026-10-22T19:00Z", note="Match 55. Jones bt Higgins 4-2, Ford 4-1; Wells bt Ryan Day 4-3", src=["wst_matches", "wst_rank"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    # ---- EuroLeague Round 7 (home listed first; game-center clock read in UTC-4 -> +4h)
    dict(id="B01", kind="basketball", sport="Basketball", comp="EuroLeague R7", a="Anadolu Efes Istanbul", b="Besiktas Istanbul",
         start="2026-10-22T17:30Z", note="Turkcell Basketball Development Center", src=["el_gc", "el_stand"],
         olbg=olbg("Basketball", 4, "Anadolu_Efes_vs_Besiktas", 535918), olbg_time="2026-10-22T17:30Z", olbg_tips="Efes 2/3"),
    dict(id="B02", kind="basketball", sport="Basketball", comp="EuroLeague R7", a="FC Bayern Munich", b="Dubai Basketball",
         start="2026-10-22T18:00Z", note="SAP Garden", src=["el_gc", "el_stand"],
         olbg=olbg("Basketball", 4, "Bayern_Munich_vs_Dubai", 535920), olbg_time="2026-10-22T18:00Z", olbg_tips="Dubai 1/1"),
    dict(id="B03", kind="basketball", sport="Basketball", comp="EuroLeague R7", a="Maccabi Rapyd Tel Aviv", b="Real Madrid",
         start="2026-10-22T18:05Z", note="Aleksandar Nikolic Hall, Belgrade", src=["el_gc", "el_stand"],
         olbg=olbg("Basketball", 4, "Maccabi_Tel_Aviv_vs_Real_Madrid", 535921), olbg_time="2026-10-22T18:05Z", olbg_tips="Maccabi 2/3"),
    dict(id="B04", kind="basketball", sport="Basketball", comp="EuroLeague R7", a="Panathinaikos AKTOR Athens", b="Kosner Baskonia Vitoria-Gasteiz",
         start="2026-10-22T18:15Z", note="Telekom Center Athens", src=["el_gc", "el_stand"],
         olbg=olbg("Basketball", 4, "Panathinaikos_vs_Baskonia", 535923), olbg_time="2026-10-22T18:15Z", olbg_tips="Baskonia 2/4"),
    dict(id="B05", kind="basketball", sport="Basketball", comp="EuroLeague R7", a="Armani Olimpia Milan", b="FC Barcelona",
         start="2026-10-22T18:30Z", note="Unipol Forum", src=["el_gc", "el_stand"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    dict(id="B06", kind="basketball", sport="Basketball", comp="EuroLeague R7", a="Partizan Mozzart Bet Belgrade", b="Crvena Zvezda Meridianbet Belgrade",
         start="2026-10-22T18:45Z", note="Belgrade Arena", src=["el_gc", "el_stand"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    dict(id="B07", kind="basketball", sport="Basketball", comp="EuroLeague R7", a="Zalgiris Kaunas", b="LDLC ASVEL Villeurbanne",
         start="2026-10-23T17:00Z", note="Zalgirio Arena", src=["el_gc", "el_stand"],
         olbg=olbg("Basketball", 4, "Zalgiris_vs_ASVEL", 535928), olbg_time="2026-10-23T17:00Z", olbg_tips="no consensus shown"),
    dict(id="B08", kind="basketball", sport="Basketball", comp="EuroLeague R7", a="Olympiacos Piraeus", b="Fenerbahce Tarfin Istanbul",
         start="2026-10-23T18:15Z", note="SUNEL Arena", src=["el_gc", "el_stand"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    dict(id="B09", kind="basketball", sport="Basketball", comp="EuroLeague R7", a="Paris Basketball", b="Valencia Basket",
         start="2026-10-23T18:45Z", note="Adidas Arena", src=["el_gc", "el_stand"],
         olbg=None, olbg_time=None, olbg_tips="not listed on OLBG hub at harvest"),
    # ---- MLB World Series Game 1
    dict(id="M01", kind="baseball", sport="Baseball", comp="MLB World Series — Game 1", a="Milwaukee Brewers", b="Tampa Bay Rays",
         start="2026-10-24T00:00Z", note="American Family Field; gamePk 849805", src=["mlb_sched", "mlb_stand_nl", "mlb_stand_al"],
         olbg=olbg("Baseball", 12, "Tampa_Bay_Rays_vs_Milwaukee_Brewers", 160789), olbg_time="2026-10-24T00:00Z", olbg_tips="Brewers 13/16"),
]

# ---------------------------------------------------------------- OLBG listings harvested but NOT verified -> blank + flagged
UNVERIFIED = [
    # (sport, label, start_utc, olbg_url, olbg_tips, reason-code)
    ("Tennis", "WTA Osaka — Stoiana v Uchijima", "2026-10-22T04:00Z", olbg("Tennis", 3, "Stoiana_vs_Uchijima", 902067), "", "WTA"),
    ("Tennis", "WTA Osaka — Jovic v Paolini", "2026-10-22T05:00Z", olbg("Tennis", 3, "Jovic_vs_Paolini", 902075), "", "WTA"),
    ("Tennis", "WTA Osaka — Linette v Siniakova", "2026-10-22T05:30Z", olbg("Tennis", 3, "Linette_vs_Siniakova", 902071), "", "WTA"),
    ("Tennis", "WTA Osaka — Kawa v Bencic", "2026-10-22T06:30Z", olbg("Tennis", 3, "Kawa_vs_Bencic", 902093), "", "WTA"),
    ("Tennis", "WTA Osaka — Eala v Shnaider", "2026-10-22T08:00Z", olbg("Tennis", 3, "Eala_vs_Shnaider", 902072), "", "WTA"),
    ("Tennis", "WTA Osaka — Rybakina v P. Kudermetova", "2026-10-22T11:00Z", olbg("Tennis", 3, "Rybakina_vs_Kudermetova", 902073), "", "WTA"),
    ("Tennis", "WTA — Gibson v Krueger", "2026-10-23T02:30Z", olbg("Tennis", 3, "Gibson_vs_Krueger", 902107), "", "WTA"),
    ("Tennis", "ATP Brussels — Gojo v Altmaier", "2026-10-22T12:00Z", olbg("Tennis", 3, "Borna_Gojo_vs_Daniel_Altmaier", 902100), "", "ATP-NOTSEEN"),
    ("Tennis", "ATP Almaty QF — Tsitsipas v Duckworth", "2026-10-23T06:30Z", olbg("Tennis", 3, "Tsitsipas_vs_Duckworth", 902129), "Duckworth 1/1", "ATP-QF"),
    ("Basketball", "NBA — Denver Nuggets @ Oklahoma City Thunder", "2026-10-23T01:40Z", olbg("Basketball", 4, "Denver_Nuggets_vs_Oklahoma_City_Thunder", 534843), "Thunder 3/3", "NBA"),
    ("Basketball", "NBA — Cleveland Cavaliers @ Philadelphia 76ers", "2026-10-22T23:10Z", olbg("Basketball", 4, "Cleveland_Cavaliers_vs_Philadelphia_76ers", 534845), "", "NBA"),
    ("Basketball", "NBA — Houston Rockets @ San Antonio Spurs", "2026-10-24T01:40Z", olbg("Basketball", 4, "Houston_Rockets_vs_San_Antonio_Spurs", 534841), "", "NBA"),
    ("Basketball", "NBA — New York Knicks @ Boston Celtics", "2026-10-23T23:10Z", olbg("Basketball", 4, "New_York_Knicks_vs_Boston_Celtics", 534842), "Knicks 1/2", "NBA"),
    ("Basketball", "KBL — Ulsan Hyundai Mobis v Changwon LG", "2026-10-22T10:00Z", olbg("Basketball", 4, "Mobis_vs_Changwon", 536021), "", "NOSRC"),
    ("Basketball", "NBB — Fortaleza v Pinheiros", "2026-10-22T22:30Z", olbg("Basketball", 4, "Fortaleza_vs_Pinheiros", 536019), "", "NOSRC"),
    ("Darts", "PDC European Championship R1 — Woodhouse v van Duijvenbode", "2026-10-22T17:15Z", olbg("Darts", 15, "Woodhouse_vs_van_Duijvenbode", 32324), "van Duijvenbode 11/13", "PDC"),
    ("Darts", "PDC European Championship R1 — Noppert v Bunting", "2026-10-22T17:45Z", olbg("Darts", 15, "Noppert_vs_Bunting", 32330), "Noppert 9/13", "PDC"),
    ("Darts", "PDC European Championship R1 — Zonneveld v Menzies", "2026-10-22T18:15Z", olbg("Darts", 15, "Zonneveld_vs_Menzies", 32334), "Zonneveld 11/14", "PDC"),
    ("Darts", "PDC European Championship R1 — Price v Cross", "2026-10-22T18:45Z", olbg("Darts", 15, "Price_vs_Cross", 32325), "Price 10/13", "PDC"),
    ("Darts", "PDC European Championship R1 — Wade v Heta", "2026-10-22T19:15Z", olbg("Darts", 15, "Wade_vs_Heta", 32322), "Wade 9/14", "PDC"),
    ("Darts", "PDC European Championship R1 — Humphries v Searle", "2026-10-22T19:45Z", olbg("Darts", 15, "Humphries_vs_Searle", 32337), "Humphries 10/13", "PDC"),
    ("Darts", "PDC European Championship R1 — van Veen v Gilding", "2026-10-22T20:15Z", olbg("Darts", 15, "van_Veen_vs_Gilding", 32323), "van Veen 9/14", "PDC"),
    ("Darts", "PDC European Championship R1 — R. Smith v Sedlacek", "2026-10-22T20:45Z", olbg("Darts", 15, "Smith_vs_Sedlacek", 32329), "Smith 7/13", "PDC"),
    ("Darts", "PDC European Championship R1 — Joyce v Wattimena", "2026-10-23T17:15Z", olbg("Darts", 15, "Joyce_vs_Wattimena", 32332), "Joyce 6/8", "PDC"),
    ("Darts", "PDC European Championship R1 — Ratajski v Chisnall", "2026-10-23T17:45Z", olbg("Darts", 15, "Ratajski_vs_Chisnall", 32333), "Chisnall 4/7", "PDC"),
    ("Darts", "PDC European Championship R1 — Aspinall v Reyes", "2026-10-23T18:15Z", olbg("Darts", 15, "Aspinall_vs_Reyes", 32327), "Aspinall 3/6", "PDC"),
    ("Darts", "PDC European Championship R1 — Clayton v Springer", "2026-10-23T18:45Z", olbg("Darts", 15, "Clayton_vs_Springer", 32335), "Clayton 7/9", "PDC"),
    ("Darts", "PDC European Championship R1 — Littler v W. O'Connor", "2026-10-23T19:15Z", olbg("Darts", 15, "Littler_vs_OConnor", 32328), "Littler 2/4", "PDC"),
    ("Darts", "PDC European Championship R1 — Nijman v Schindler", "2026-10-23T19:45Z", olbg("Darts", 15, "Nijman_vs_Schindler", 32326), "Nijman 4/7", "PDC"),
    ("Darts", "PDC European Championship R1 — Doets v van Gerwen", "2026-10-23T20:15Z", olbg("Darts", 15, "Doets_vs_van_Gerwen", 32331), "van Gerwen 2/3", "PDC"),
    ("Darts", "PDC European Championship R1 — Rock v Dobey", "2026-10-23T20:45Z", olbg("Darts", 15, "Rock_vs_Dobey", 32336), "Rock 3/5", "PDC"),
    ("Ice Hockey", "SHL — Skelleftea AIK v Djurgardens IF", "2026-10-22T17:00Z", olbg("Ice_Hockey", 13, "Skelleftea_vs_Djurgarden", 199905), "Skelleftea 2/2", "NOSRC"),
    ("Ice Hockey", "SHL — Timra IK v Farjestad BK", "2026-10-22T17:00Z", olbg("Ice_Hockey", 13, "Timra_vs_Farjestad", 199901), "Farjestad 2/2", "NOSRC"),
    ("Ice Hockey", "SHL — Orebro HK v Brynas IF", "2026-10-22T17:00Z", olbg("Ice_Hockey", 13, "Orebro_vs_Brynas", 199900), "Brynas 1/2", "NOSRC"),
    ("Ice Hockey", "Liiga — JYP v HPK", "2026-10-22T15:30Z", olbg("Ice_Hockey", 13, "JYP_vs_HPK", 199912), "JYP 1/1", "NOSRC"),
    ("Ice Hockey", "NHL — 12-game slate of 22 Oct (NSH@BOS, NYR@TOR, SJS@OTT, ANA@NJD, @PIT ... first five at 23:00Z)", "2026-10-22T23:00Z", "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/13", "OLBG NHL sub-hub: no tips", "NHL-PARTIAL"),
    ("Cricket", "T20I — New Zealand v India (1st T20I)", "2026-10-22T07:00Z", olbg("Cricket", 7, "New_Zealand_vs_India", 188814), "India 13/17", "NOSRC"),
    ("Cricket", "ODI — England v Sri Lanka", "2026-10-22T08:00Z", olbg("Cricket", 7, "England_vs_Sri_Lanka", 188829), "England 8/10", "NOSRC"),
    ("Cricket", "ODI — Namibia v Ireland", "2026-10-22T08:00Z", olbg("Cricket", 7, "Namibia_vs_Ireland", 188828), "Ireland 7/11", "NOSRC"),
    ("Cricket", "Women's T20I — Australia W v New Zealand W", "2026-10-22T08:15Z", olbg("Cricket", 7, "Australia_W_vs_New_Zealand_W", 188826), "Australia 7/9", "NOSRC"),
    ("Cricket", "Mpumalanga v South Africa Emerging", "2026-10-22T11:00Z", olbg("Cricket", 7, "Mpumalanga_vs_SA_Emerging", 188825), "", "NOSRC"),
    ("Cricket", "Eastern Storm v Tuskers", "2026-10-22T16:00Z", olbg("Cricket", 7, "Eastern_Storm_vs_Tuskers", 188811), "", "NOSRC"),
    ("Cricket", "ODI — Afghanistan v Zimbabwe", "2026-10-23T11:30Z", olbg("Cricket", 7, "Afghanistan_vs_Zimbabwe", 188831), "", "NOSRC"),
    ("Rugby Union", "Pro D2 — Montauban v Oyonnax", "2026-10-22T19:00Z", olbg("Rugby_Union", 9, "Montauban_vs_Oyonnax", 609556), "Oyonnax 11/16", "NOSRC"),
    ("Rugby Union", "URC — Connacht v Zebre", "2026-10-23T18:45Z", olbg("Rugby_Union", 9, "Connacht_vs_Zebre", 609577), "Connacht 4/6", "NOSRC"),
    ("Rugby Union", "Pro D2 / Nationale 23 Oct — Aurillac v Nevers, Narbonne v Brive, Soyaux v Dax, Agen v Nissa, Valence v Colomiers, Grenoble v Biarritz, Provence v Beziers", "2026-10-23T17:00Z", "https://www.olbg.com/betting-tips/Rugby_Union/9", "", "NOSRC"),
    ("Rugby Union", "URC 24 Oct — Bulls v Ulster, Stormers v Scarlets, Leinster v Munster; Top 14 — Toulouse v Perpignan, Bayonne v Lyon; La Rochelle v Bordeaux 25 Oct", "2026-10-24T11:45Z", "https://www.olbg.com/betting-tips/Rugby_Union/9", "Ulster +18.5; Leinster 2/2; Perpignan 1/2", "NOSRC"),
    ("Rugby League", "Outrights only on hub (State of Origin 2027, Super League 2027, NRL 2027) — no matches", None, "https://www.olbg.com/betting-tips/Rugby_League/10", "", "EMPTY"),
    ("Motor Racing", "F1 United States GP — race 25 Oct 20:00Z", "2026-10-25T20:00Z", olbg("Motor_Racing", 14, "USA_Grand_Prix", 913), "Verstappen 12/33", "NOSRC"),
    ("Handball", "EHF Champions League 22 Oct — Sporting v Kristianstad, Barcelona v Montpellier, Kolstad v Magdeburg (18:45Z); Szeged v GOG, Melsungen v Plock (16:45Z)", "2026-10-22T16:45Z", "https://www.olbg.com/betting-tips/Handball/20", "Tie 5/10 (Sporting); Tie (Kolstad)", "NOSRC"),
    ("Handball", "Women's Euro qualifiers — Bulgaria W v Italy W (16:00Z); Estonia W v Kosovo W 23 Oct (18:00Z)", "2026-10-22T16:00Z", "https://www.olbg.com/betting-tips/Handball/20", "Italy -4.5 4/4", "NOSRC"),
    ("Handball", "Domestic 22–23 Oct — Stuttgart v Bietigheim, Sonderjyske v Nordsjaelland, Kolding v Fredericia, Onnereds v Ystads, Granollers v C. Encantada, Limoges v Dunkerque, Aix v Toulouse, Goppingen v Eisenach", "2026-10-22T17:00Z", "https://www.olbg.com/betting-tips/Handball/20", "", "NOSRC"),
    ("Volleyball", "Tauron Liga W — Radomka Radom v Mielec", "2026-10-22T15:30Z", olbg("Volleyball", 21, "Radomka_Radom_vs_Mielec", 36988), "Radom 4/5", "NOSRC"),
    ("Volleyball", "Czech Extraliga 22 Oct 16:00Z — C. Budejovice v Beskydy, Ostrava v Kladno, Brno v Odolena Voda, Usti v Zlin, Liberec v Benatky", "2026-10-22T16:00Z", "https://www.olbg.com/betting-tips/Volleyball/21", "", "NOSRC"),
    ("Volleyball", "PlusLiga — Suwalki v Katowice 23 Oct 15:30Z; Belchatow v Projekt 24 Oct 16:00Z; Chelm v Resovia 25 Oct 17:00Z", "2026-10-23T15:30Z", "https://www.olbg.com/betting-tips/Volleyball/21", "", "NOSRC"),
    ("Golf", "Butterfield Bermuda Championship (PGA Tour)", "2026-10-22T11:00Z", olbg("Golf", 5, "Bermuda_Championship", 101904), "Ben James FRL 5/11", "NOSRC"),
    ("Golf", "Senior Italian Open / Stella Artois Players Championship / Stifel Charity Classic", "2026-10-22T07:00Z", "https://www.olbg.com/betting-tips/Golf/5", "Baker 2/6; van Tonder 2/8; Cink 2/11", "NOSRC"),
    ("Gaelic Football", "Cork SFC — St Finbarr's v Nemo Rangers 25 Oct 16:00Z; Galway SFC — Moycullen v Salthill-Knocknacarra 24 Oct 18:00Z", "2026-10-24T18:00Z", "https://www.olbg.com/betting-tips/Gaelic_Football/25", "Nemo +1.5 10/12; Moycullen -3.5 9/18", "NOSRC"),
    ("Gaelic Football", "1 Nov — Kanturk v Eire Og, Fr Caseys v Kildimo, Rathgormack v The Nire", "2026-11-01T13:00Z", "https://www.olbg.com/betting-tips/Gaelic_Football/25", "", "NOSRC"),
    ("Aussie Rules", "Hub returned 'No tips found' (off-season)", None, "https://www.olbg.com/betting-tips/Aussie_Rules/22", "", "EMPTY"),
    ("eSports", "Hub returned 'No tips found'", None, "https://www.olbg.com/betting-tips/eSports/23", "", "EMPTY"),
    ("Greyhounds", "Hub returned 'No tips found' at 03:00Z (cards populate later in the day)", None, "https://www.olbg.com/betting-tips/Greyhounds/28", "", "EMPTY"),
]

REASONS = {
    "WTA": ("WTA Osaka draw page did not render match data (wtatennis.com returned only the notifications panel); OLBG's 'Tokyo' label also conflicts with the WTA calendar, which lists this week's event in Osaka.", "wta_blocked"),
    "ATP-NOTSEEN": ("Not on the first chunk of any ATP order of play read this session; later-court chunks were not fetched.", "atp_sched_brussels"),
    "ATP-QF": ("Quarter-final: Duckworth's R16 win over Darderi is verified on atptour.com but Tsitsipas' R16 result was not read, so the pairing is unconfirmed.", "atp_scores"),
    "NBA": ("cdn.nba.com live scoreboard returned HTTP 500 and no other NBA official endpoint was read; teams/times stand on OLBG only.", "nba_blocked"),
    "PDC": ("pdc.tv served only a CookieYes consent wall on every chunk; the European Championship draw could not be read from the PDC.", "pdc_blocked"),
    "NOSRC": ("Official source not fetched this session (time budget); listing is OLBG-only and carries no price.", None),
    "NHL-PARTIAL": ("api-web.nhle.com confirms 12 games on 22 Oct but only five matchups were read; slate left unpriced rather than partially listed.", "nhl_sched"),
    "EMPTY": ("OLBG hub carried no match events at harvest time.", None),
}

# ---------------------------------------------------------------- repository review findings (line-by-line audit of inherited material)
REPO_FINDINGS = [
    ("COORDINATION.md §1", "T41 row still says 'Not started / —' for PR and merge while §33 records the 7a5b5360 desk as merged; the table and the section disagree.",
     "https://github.com/buffedlizard55-lab/OLBG1/blob/main/COORDINATION.md"),
    ("data/7a5b5360/fixtures.json + README.md §'Fresh matchday desk'", "The 7a5b5360 desk prices Round 3 of the NI Open from an order of play captured 21 Oct; this desk re-read wst.tv on 22 Oct and the eight R3 pairings and session times match (no drift found).",
     "https://www.wst.tv/matches"),
    ("reports/OLBG_REVERSE_ENGINEERING.md (clock finding)", "Re-confirmed: OLBG hub times for Almaty, Brussels, Lyon and EuroLeague are exactly 4h behind the UTC start derived from each official local time, i.e. US Eastern without a label.",
     "https://www.atptour.com/en/scores/current/lyon/496/daily-schedule"),
    ("OLBG Tennis hub labelling", "OLBG files this week's WTA 500 as 'Tokyo'; the WTA calendar read this session lists the Kinoshita Group Japan Open in Osaka (Toray Pan Pacific Open Tokyo is a separate later entry). Flagged as an OLBG taxonomy irregularity.",
     "https://www.wtatennis.com/tournaments/405/osaka/2026/draws"),
    ("OLBG Basketball hub: Efes v Besiktas 535918", "OLBG lists Efes as home; EuroLeague Game Center shows the venue as Turkcell Basketball Development Center (Efes) — consistent. Maccabi v Real Madrid is staged in Belgrade (Aleksandar Nikolic Hall), not Tel Aviv; OLBG does not surface the neutral venue.",
     "https://www.euroleaguebasketball.net/en/euroleague/game-center/"),
]
