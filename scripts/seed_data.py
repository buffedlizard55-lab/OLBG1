#!/usr/bin/env python3
"""Seed data — transcribed line by line from OLBG sport pages fetched 2026-10-21.
Every field below is what OLBG displayed at harvest time. Nothing is inferred:
unknown/cut-off values are None and flagged. Dates: OLBG 'Today'=2026-10-21,
'Tomorrow'=2026-10-22 (harvest date). Times are as displayed on OLBG (timezone
not stated by OLBG in fetched text -> flagged globally).
Outputs data/matches.json
"""
import json, pathlib

H = "2026-10-21"  # harvest date

# Official governing-body / league sources (stable canonical pages)
OFF = {
 "atp":  ("ATP Tour (official)", "https://www.atptour.com/"),
 "wta":  ("WTA Tour (official)", "https://www.wtatennis.com/"),
 "pdc":  ("PDC — 2026 European Championship field & draw confirmed (official, 18 Oct 2026)", "https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed"),
 "wst":  ("World Snooker Tour — Match Centre (official)", "https://www.wst.tv/match-centre/9a737c9a-19aa-4281-8c31-6a07b796e806"),
 "nba":  ("NBA (official schedule)", "https://www.nba.com/schedule"),
 "euroleague": ("EuroLeague Basketball (official)", "https://www.euroleaguebasketball.net/"),
 "bcl":  ("Basketball Champions League (official)", "https://www.championsleague.basketball/"),
 "fiba": ("FIBA (official)", "https://www.fiba.basketball/"),
 "mlb":  ("MLB — 2026 postseason & World Series schedule (official)", "https://www.mlb.com/news/2026-mlb-playoff-and-world-series-schedule"),
 "nhl":  ("NHL (official schedule)", "https://www.nhl.com/schedule"),
 "shl":  ("Swedish Hockey League (official)", "https://www.shl.se/"),
 "ice":  ("win2day ICE Hockey League (official)", "https://www.ice.hockey/"),
 "icc":  ("ICC (official)", "https://www.icc-cricket.com/"),
 "icc_nz": ("ICC — New Zealand home summer schedule incl. India tour (official)", "https://www.icc-cricket.com/news/new-zealand-announce-schedule-for-action-packed-home-summer"),
 "csa":  ("Cricket South Africa (official)", "https://cricket.co.za/"),
 "urc":  ("United Rugby Championship — 2026/27 fixtures in full (official)", "https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/"),
 "lnr":  ("Ligue Nationale de Rugby (official)", "https://www.lnr.fr/"),
 "ehf":  ("European Handball Federation (official)", "https://www.eurohandball.com/"),
 "fivb": ("FIVB / Volleyball World (official)", "https://www.fivb.com/"),
 "cev":  ("CEV — European Volleyball Confederation (official)", "https://www.cev.eu/"),
 "plusliga": ("PlusLiga (official, Poland)", "https://www.plusliga.pl/"),
 "gaa":  ("GAA (official)", "https://www.gaa.ie/"),
 "rfl":  ("Rugby Football League (official)", "https://www.rugby-league.com/"),
}

def olbg(sport_path, event_slug, sid, eid):
    return f"https://www.olbg.com/betting-tips/{sport_path}/All_{sport_path}/All_Events/{event_slug}/{sid}?event_id={eid}"

M = []
def add(**kw): M.append(kw)

# ---------------- TENNIS (OLBG id 3) — week of 19-25 Oct 2026: ATP Almaty/Lyon/Brussels, WTA Ningbo/Osaka (ATP official calendar) ----------------
TEN = [
 # home, away, date, time, market, selection, for, total, experts, event_id, tour
 ("Leylah Fernandez","Aliaksandra Sasnovich","2026-10-21","02:30","Win Match","Leylah Fernandez",6,7,0,902039,"wta"),
 ("Katie Boulter","Viktorija Golubic","2026-10-21","01:30","Win Match","Katie Boulter",5,8,1,902065,"wta"),
 ("James Duckworth","Luciano Darderi","2026-10-21","02:30","Win Match","Luciano Darderi",4,5,0,902038,"atp"),
 ("Adrian Mannarino","Andrey Rublev","2026-10-21","05:30","Win Match","Andrey Rublev",4,5,0,902037,"atp"),
 ("Sorana Cirstea","Sara Bejlek","2026-10-21","04:00","Win Match","Sara Bejlek",3,6,0,902074,"wta"),
 ("Zangar Nurlanuly","Tomas Machac","2026-10-21","04:00","1st Set Winner","Zangar Nurlanuly",3,4,0,901935,"atp"),
 ("Mattia Bellucci","Tomas Martin Etcheverry","2026-10-21","02:30","Set Betting","Tomas Martin Etcheverry to win 2-1",2,3,0,901993,"atp"),
 ("Dino Prizmic","Damir Dzumhur","2026-10-21","05:30","Win Match","Damir Dzumhur",2,2,0,901896,"atp"),
 ("Stan Wawrinka","Martin Landaluce","2026-10-21","08:00","Win Match","Stan Wawrinka",2,2,0,901974,"atp"),
 ("David Goffin","Remy Bertola","2026-10-21","12:00","Win Match","David Goffin",2,2,0,902028,"atp"),
 ("Facundo Diaz Acosta","Nikoloz Basilashvili","2026-10-21","04:00","Set Betting","Nikoloz Basilashvili to win 2-1",1,2,0,902040,"atp"),
 ("Martin Damm","Francisco Cerundolo","2026-10-21","05:30","Set Betting","Francisco Cerundolo to win 2-1",1,1,0,902048,"atp"),
 ("Mariano Navone","Tallon Griekspoor","2026-10-21","07:00","Win Match","Tallon Griekspoor",1,1,0,902085,"atp"),
 ("Ekaterina Alexandrova","Marta Kostyuk","2026-10-21","07:00","Win Match","Marta Kostyuk",None,None,0,902084,"wta"),
 ("Clement Chidekh","Jacob Fearnley","2026-10-21","08:30","Set Betting","Clement Chidekh to win 2-1",1,1,0,902094,"atp"),
 ("Corentin Moutet","Felix Balshaw","2026-10-21","09:30","Set Betting","Corentin Moutet to win 2-1",1,1,0,902095,"atp"),
 ("Stefanos Tsitsipas","Mikhail Kukushkin","2026-10-21","10:30","Set Betting","Stefanos Tsitsipas to win 2-0",1,1,0,902083,"atp"),
 ("Moise Kouame","Lorenzo Musetti","2026-10-21","13:00","Win Match","Moise Kouame",1,2,0,902059,"atp"),
 ("Benjamin Bonzi","Tommy Paul","2026-10-21","14:30","Set Betting","Tommy Paul to win 2-1",1,1,0,902102,"atp"),
 ("Katarzyna Kawa","Belinda Bencic","2026-10-21","23:00","1st Set Winner","Belinda Bencic",1,1,0,902093,"wta"),
]
for i,(h,a,d,t,mk,sel,f,tt,ex,eid,tour) in enumerate(TEN,1):
    slug = f"{h}_vs_{a}".replace(" ","_").replace("-","-")
    add(id=f"TEN-{i:02d}", sport="Tennis", league="ATP/WTA Tour — tournament per match not shown by OLBG feed (see Flagged)",
        home=h, away=a, date=d, time_olbg=t, olbg_url=olbg("Tennis",slug,3,eid),
        olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF[tour][0], official_url=OFF[tour][1], verification="OLBG-ONLY",
        verified_facts="ATP official 2026 calendar confirms ATP 250 events in Almaty, Lyon and Brussels run 19–25 Oct 2026; WTA Ningbo (500) and Osaka (250) run the same week. OLBG's feed does not name the tournament for each match, so no tournament is asserted per match.",
        flags=(["UNVERIFIED: tip counts cut off in OLBG page fetch — left blank, not estimated."] if f is None else []) + (["OLBG most-tipped market is not Win Match — win probability signal is indirect (see Methodology)."] if mk!="Win Match" else []))

# ---------------- DARTS (OLBG id 15) — PDC European Championship, Dortmund, 22-25 Oct 2026, R1 best of 11 legs ----------------
DAR = [
 ("Luke Woodhouse","Dirk van Duijvenbode","2026-10-22","13:15","Win Match 2-way","Dirk van Duijvenbode",7,8,1,32324,None,None,""),
 ("Niels Zonneveld","Cameron Menzies","2026-10-22","14:15","Win Match 2-way","Niels Zonneveld",6,7,0,32334,4,29,"PDC (official): Zonneveld starts as fourth seed after winning the final European Tour event of the year and faces Cameron Menzies."),
 ("Gerwyn Price","Rob Cross","2026-10-22","14:45","Win Match 2-way","Gerwyn Price",5,7,0,32325,13,20,"Headline first-round tie of the 2026 European Championship in Dortmund (PDC draw, 18 Oct 2026)."),
 ("James Wade","Damon Heta","2026-10-22","15:15","Win Match 2-way","James Wade",5,8,0,32322,None,None,""),
 ("Luke Humphries","Ryan Searle","2026-10-22","15:45","Win Match 2-way","Luke Humphries",5,7,0,32337,12,21,"PDC (official): world number two and last year's runner-up Luke Humphries is 12th seed and faces Ryan Searle. Humphries won the 2026 World Grand Prix (28 Sep–4 Oct, Leicester), beating Gerwyn Price 6–4 in the final."),
 ("Danny Noppert","Stephen Bunting","2026-10-22","13:45","Total Legs","Over 9.50",4,4,1,32330,None,None,"First round is best of 11 legs, so Over 9.5 legs needs at least 10 legs played (OLBG darts market guide)."),
 ("Gian van Veen","Andrew Gilding","2026-10-22","16:15","Win Match 2-way","Gian van Veen",4,6,0,32323,8,25,"Gian van Veen is the defending European champion and opens his title defence against former UK Open champion Andrew Gilding (PDC draw coverage)."),
 ("Ross Smith","Karel Sedlacek","2026-10-22","16:45","Win Match 2-way","Ross Smith",4,8,0,32329,None,None,""),
 ("Jonny Clayton","Niko Springer","2026-10-23","14:45","Win Match 2-way","Jonny Clayton",4,6,0,32335,None,None,""),
 ("Ryan Joyce","Jermaine Wattimena","2026-10-23","13:15","Win Match 2-way","Ryan Joyce",2,3,1,32332,None,None,""),
 ("Krzysztof Ratajski","Dave Chisnall","2026-10-23","13:45","Win Match 2-way","Krzysztof Ratajski",2,4,0,32333,None,None,""),
 ("Nathan Aspinall","Cristo Reyes","2026-10-23","14:15","Win Match 2-way","Cristo Reyes",2,3,1,32327,6,27,"SIGNAL CONFLICT: OLBG's most-tipped pick is 27th seed Cristo Reyes against 6th seed Nathan Aspinall — the crowd pick opposes the seeding gap."),
 ("Luke Littler","William OConnor","2026-10-23","15:15","Handicap 2-way","William OConnor +3.50",2,2,1,32328,11,22,"PDC (official): World Champion Luke Littler, who won two of the three European Tour events he played this year, starts against Ireland's William O'Connor. Littler is described as world number one in PDC draw coverage."),
 ("Wessel Nijman","Martin Schindler","2026-10-23","15:45","Win Match 2-way","Martin Schindler",2,3,1,32326,2,31,"SIGNAL CONFLICT: OLBG's most-tipped pick is Martin Schindler against 2nd seed Wessel Nijman — the crowd pick opposes the seeding gap."),
 ("Kevin Doets","Michael van Gerwen","2026-10-23","16:15","Total Legs","Over 9.50",1,1,1,32331,14,19,""),
 ("Josh Rock","Chris Dobey","2026-10-23","16:45","Win Match 2-way","Chris Dobey",1,2,0,32336,10,23,""),
]
for i,(h,a,d,t,mk,sel,f,tt,ex,eid,sh,sa,facts) in enumerate(DAR,1):
    slug = f"{h}_vs_{a}".replace(" ","_")
    fl = []
    if "SIGNAL CONFLICT" in facts: fl.append("IRREGULARITY: OLBG crowd majority opposes the official seeding gap — confidence forced to LOW (see Flagged page).")
    if mk not in ("Win Match 2-way",): fl.append("OLBG most-tipped market is not Win Match — win probability signal is indirect (see Methodology).")
    add(id=f"DAR-{i:02d}", sport="Darts", league="PDC European Championship 2026 — Round 1, Westfalenhallen, Dortmund (best of 11 legs)",
        home=h, away=a, date=d, time_olbg=t, olbg_url=olbg("Darts",slug,15,eid),
        olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF["pdc"][0], official_url=OFF["pdc"][1], verification="VERIFIED",
        seed_home=sh, seed_away=sa,
        verified_facts=("Top 32 of the European Tour Order of Merit contest the European Championship in Dortmund, 22–25 Oct 2026; prize fund £750,000 with £150,000 to the winner (PDC). " + facts).strip(),
        flags=fl)

# ---------------- SNOOKER (OLBG id 8) — BetVictor Northern Ireland Open, Belfast, R2 best of 7 ----------------
SNO = [
 ("Cheung Ka Wai","Stuart Bingham","2026-10-21","05:00","Win Match","Cheung Ka Wai",8,11,0,9933,"CONTESTED"),
 ("Pang Junxu","Liam Davies","2026-10-21","05:00","Win Match","Pang Junxu",6,9,0,9929,"VERIFIED"),
 ("Elliot Slessor","Jamie Jones","2026-10-21","15:00","Win Match","Jamie Jones",4,4,0,9931,"OLBG-ONLY"),
 ("Luca Brecel","Martin O Donnell","2026-10-21","15:00","Win Match","Martin O Donnell",4,5,0,9932,"CONTESTED"),
 ("John Higgins","Jak Jones","2026-10-21","08:00","Win Match","John Higgins",3,6,0,9934,"VERIFIED"),
 ("Sam Craigie","Xu Si","2026-10-21","09:00","Win Match","Sam Craigie",3,3,0,9930,"VERIFIED"),
]
SNO_RANK = {"Pang Junxu":26,"Liam Davies":89,"John Higgins":7,"Jak Jones":30}
for i,(h,a,d,t,mk,sel,f,tt,ex,eid,ver) in enumerate(SNO,1):
    slug = f"{h}_v_{a}".replace(" ","_").replace("'","")
    fl=[]
    facts="BetVictor Northern Ireland Open 2026, Waterfront Hall Belfast, 18–25 Oct 2026; Round 2 on 21 Oct is best of 7 frames; defending champion Jack Lisowski; winner receives £100,000 of a £550,400 fund (WST / tournament record)."
    if ver=="CONTESTED":
        fl.append("IRREGULARITY: this exact pairing could not be confirmed on the official WST Match Centre at harvest time (WST showed Cheung Ka Wai vs 'Winner of match 20' and listed other Round-2 ties). Fixture shown as OLBG lists it; do not treat as confirmed until re-checked on WST.")
        facts += " WST Match Centre at harvest listed Pang Junxu v Liam Davies, Sam Craigie v Xu Si and John Higgins v Winner of match 26 among 21 Oct Round-2 ties."
    if h in SNO_RANK and a in SNO_RANK:
        facts += f" World ranking numbers shown alongside the draw: {h} [{SNO_RANK[h]}] v {a} [{SNO_RANK[a]}] (secondary listing of the official draw — see WST for the live ranking list)."
    add(id=f"SNO-{i:02d}", sport="Snooker", league="BetVictor Northern Ireland Open 2026 — Round 2 (best of 7 frames)",
        home=h, away=a, date=d, time_olbg=t, olbg_url=olbg("Snooker",slug,8,eid),
        olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF["wst"][0], official_url=OFF["wst"][1], verification=ver,
        seed_home=SNO_RANK.get(h), seed_away=SNO_RANK.get(a), verified_facts=facts, flags=fl)

# ---------------- BASKETBALL (OLBG id 4) ----------------
BKB = [
 ("MIL Bucks","WAS Wizards","2026-10-21","19:10","Money Line","WAS Wizards",9,11,0,534889,"NBA","nba","VERIFIED","Milwaukee visits Washington (OLBG lists 'MIL Bucks @ WAS Wizards', so Washington is at home). The 2026-27 NBA regular season tipped off on 20 Oct 2026 (NBA official), so this is opening-week basketball with no meaningful current-season form. Two-time MVP Giannis Antetokounmpo makes his Miami Heat debut on 21 Oct vs Minnesota (NBA official schedule release) — i.e. he is no longer with Milwaukee."),
 ("ATL Hawks","ORL Magic","2026-10-21","19:10","Money Line","ATL Hawks",3,5,0,534888,"NBA","nba","VERIFIED","Atlanta at Orlando ('@' = away team first). Opening week of the 2026-27 NBA season (started 20 Oct, NBA official) — no current-season form base."),
 ("CHI Bulls","TOR Raptors","2026-10-21","19:40","Money Line","TOR Raptors",3,4,0,535673,"NBA","nba","VERIFIED","Chicago at Toronto. Opening week of the 2026-27 NBA season (NBA official)."),
 ("IND Pacers","NO Pelicans","2026-10-21","20:10","Money Line","NO Pelicans",2,4,0,534892,"NBA","nba","VERIFIED","Indiana at New Orleans. Opening week of the 2026-27 NBA season (NBA official)."),
 ("PHX Suns","POR Trail Blazers","2026-10-21","22:10","Money Line","PHX Suns",2,3,0,534893,"NBA","nba","VERIFIED","Phoenix at Portland. Opening week of the 2026-27 NBA season (NBA official)."),
 ("DEN Nuggets","OKC Thunder","2026-10-22","21:40","Money Line","OKC Thunder",2,2,0,534843,"NBA","nba","VERIFIED","Denver at Oklahoma City. OKC opened the season on 20 Oct at San Antonio in a rematch of the 2026 Western Conference Finals (NBA official)."),
 ("Hapoel Tel Aviv","Virtus Bologna","2026-10-21","12:00","Money Line","Hapoel Tel Aviv",5,8,1,535919,"EuroLeague","euroleague","OLBG-ONLY",""),
 ("Panathinaikos","Baskonia","2026-10-22","14:15","Money Line","Panathinaikos",2,3,0,535923,"EuroLeague","euroleague","OLBG-ONLY",""),
 ("Seoul Thunders","KCC Egis","2026-10-21","06:00","Money Line","Seoul Thunders",3,5,0,535966,"Korea KBL","fiba","OLBG-ONLY",""),
 ("PAOK","Ratiopharm Ulm","2026-10-21","13:00","Money Line","PAOK",2,2,0,535952,"EuroCup","euroleague","OLBG-ONLY",""),
 ("Bosna Sarajevo","Bahcesehir Koleji","2026-10-21","13:30","Money Line","Bahcesehir Koleji",2,3,0,535950,"EuroCup","euroleague","OLBG-ONLY",""),
 ("Hapoel Jerusalem","Rigas Zelli","2026-10-21","14:00","Money Line","Hapoel Jerusalem",2,3,0,535956,"EuroCup","euroleague","OLBG-ONLY",""),
 ("U BT Cluj Napoca","London Lions","2026-10-21","12:00","Money Line","London Lions",1,2,0,535949,"EuroCup","euroleague","OLBG-ONLY",""),
 ("Chemnitz 99","Slask Wroclaw","2026-10-21","13:00","Money Line","Slask Wroclaw",1,1,0,535951,"EuroCup","euroleague","OLBG-ONLY",""),
 ("Tortona","San Pablo Burgos","2026-10-21","13:00","Money Line","San Pablo Burgos",1,1,0,535953,"EuroCup","euroleague","OLBG-ONLY",""),
 ("Bourg","Trento","2026-10-21","13:30","Money Line","Trento",1,1,0,535954,"EuroCup","euroleague","OLBG-ONLY",""),
 ("Frankfurt Skyliners","Tenerife","2026-10-21","13:30","Money Line","Frankfurt Skyliners",1,1,0,535955,"EuroCup","euroleague","OLBG-ONLY",""),
 ("AEK","Antwerp Giants","2026-10-21","12:00","Money Line","Antwerp Giants",1,2,0,535969,"Basketball Champions League","bcl","OLBG-ONLY",""),
 ("Bnei Herzliya","FC Porto","2026-10-21","12:30","Money Line","FC Porto",1,1,0,535970,"Basketball Champions League","bcl","OLBG-ONLY",""),
 ("Joventut","Telekom Bonn","2026-10-21","14:00","Money Line","Joventut",1,1,0,535971,"Basketball Champions League","bcl","OLBG-ONLY",""),
]
for i,(h,a,d,t,mk,sel,f,tt,ex,eid,lg,off,ver,facts) in enumerate(BKB,1):
    url = ("https://www.olbg.com/betting-tips/Basketball/NBA/NBA/" if lg=="NBA" else
           "https://www.olbg.com/betting-tips/Basketball/European/Euroleague/" if lg=="EuroLeague" else
           "https://www.olbg.com/betting-tips/Basketball/European/Euro_Cup/" if lg=="EuroCup" else
           "https://www.olbg.com/betting-tips/Basketball/European/Basketball_Champions_League/" if lg=="Basketball Champions League" else
           "https://www.olbg.com/betting-tips/Basketball/Other/Korea_KBL/")
    sep = "_@_" if lg=="NBA" else "_vs_"
    url += f"{h}{sep}{a}/4?event_id={eid}".replace(" ","_")
    fl = ["NBA opening week: teams have played at most one regular-season game — no form base; confidence capped (see Methodology)."] if lg=="NBA" else []
    add(id=f"BKB-{i:02d}", sport="Basketball", league=lg, home=h, away=a, date=d, time_olbg=t, olbg_url=url,
        olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF[off][0], official_url=OFF[off][1], verification=ver, verified_facts=facts, flags=fl)

# ---------------- BASEBALL (OLBG id 12) — 2026 World Series Game 1 ----------------
add(id="BBA-01", sport="Baseball", league="MLB — 2026 World Series, Game 1 (American Family Field, Milwaukee)",
    home="TB Rays", away="MIL Brewers", date="2026-10-23", time_olbg="20:00",
    olbg_url="https://www.olbg.com/betting-tips/Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160789",
    olbg_market="Money Line", olbg_selection="TB Rays", tips_for=3, tips_total=6, experts=1,
    official_label=OFF["mlb"][0], official_url=OFF["mlb"][1], verification="VERIFIED",
    verified_facts="MLB (official): the 122nd World Series opens Fri 23 Oct with the AL champion Tampa Bay Rays (98–64) at the NL champion Milwaukee Brewers (103–59), 8 p.m. ET at American Family Field. Milwaukee holds home-field advantage on the better record. Milwaukee swept the defending champion Dodgers in the NLCS to reach its first World Series since 1982; Tampa Bay beat Cleveland in six games in the ALCS. Game 1 starting pitchers had not been confirmed in the official schedule release at harvest — left blank, not guessed.",
    flags=["Starting pitchers UNVERIFIED at harvest — pitching matchup drives baseball pricing, so confidence is capped until probables are confirmed on MLB.com."])

# ---------------- ICE HOCKEY (OLBG id 13) ----------------
ICE = [
 ("Pustertal","Pioneers Vorarlberg","2026-10-21","18:45","Money Line","Pustertal",2,2,0,199881,"Austria EHL (ICE Hockey League)","ice"),
 ("HCB Sudtirol Alperia","HC TWK Innsbruck","2026-10-21","18:45","Money Line","HCB Sudtirol Alperia",2,2,0,199878,"Austria EHL (ICE Hockey League)","ice"),
 ("Timra IK","Farjestad BK","2026-10-22","18:00","Money Line","Farjestad BK",2,2,2,199901,"Swedish Hockey League","shl"),
 ("Graz 99ers","Milano HC","2026-10-21","17:30","Puck Line","Graz 99ers -1.50",1,1,0,199876,"Austria EHL (ICE Hockey League)","ice"),
 ("KAC Klagenfurt","Fehervar AV19","2026-10-21","18:15","Money Line","KAC Klagenfurt",1,1,0,199880,"Austria EHL (ICE Hockey League)","ice"),
 ("PHI Flyers","BUF Sabres","2026-10-22","00:37","Game Totals","Over 5.50",1,1,0,199897,"NHL","nhl"),
 ("FLA Panthers","OTT Senators","2026-10-22","00:37","Game Totals","Over 5.50",1,1,0,199896,"NHL","nhl"),
]
for i,(h,a,d,t,mk,sel,f,tt,ex,eid,lg,off) in enumerate(ICE,1):
    url = ("https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/" if lg=="NHL" else
           "https://www.olbg.com/betting-tips/Ice_Hockey/Other/Swedish_Hockey_League/" if lg=="Swedish Hockey League" else
           "https://www.olbg.com/betting-tips/Ice_Hockey/Other/Austria_EHL/")
    sep = "_@_" if lg=="NHL" else "_vs_"
    url += f"{h}{sep}{a}/13?event_id={eid}".replace(" ","_")
    fl=[]
    facts=""
    if lg=="NHL":
        facts="Philadelphia at Buffalo / Florida at Ottawa (OLBG '@' format). OLBG's own guide: the NHL puck line is usually 1.5 goals; our originated lines follow that standard."
        fl.append("OLBG most-tipped market is Game Totals, not a winner market — win signal is indirect (see Methodology). Goalie starters UNVERIFIED at harvest.")
    add(id=f"ICE-{i:02d}", sport="Ice Hockey", league=lg, home=h, away=a, date=d, time_olbg=t, olbg_url=url,
        olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF[off][0], official_url=OFF[off][1], verification="OLBG-ONLY", verified_facts=facts, flags=fl)

# ---------------- CRICKET (OLBG id 7) ----------------
CRI = [
 ("Afghanistan","Bangladesh","2026-10-21","07:30","Win Match","Afghanistan",7,7,1,188824,"One Day International (UAE tri-series window, 17–21 Oct)","icc","OLBG-ONLY","ICC ODI team ratings (updated 19 Oct 2026, republished from ICC data): Afghanistan 8th, rating 92; Bangladesh 9th, rating 82 — Afghanistan rated 10 points higher. This ODI falls in the UAE ODI tri-series window (Afghanistan, Bangladesh, Zimbabwe, 17–21 Oct) per the international fixture list."),
 ("Northern Cape Heat","Garden Route Badgers","2026-10-21","07:00","Win Match","Garden Route Badgers",5,8,2,188823,"South Africa domestic T20","csa","OLBG-ONLY",""),
 ("North West Dragons","Limpopo Impalas","2026-10-21","12:00","Win Match","North West Dragons",5,6,1,188810,"South Africa domestic T20","csa","OLBG-ONLY",""),
 ("New Zealand","India","2026-10-22","03:00","Win Match","India",5,7,1,188814,"T20 International — 1st T20I, Hagley Oval, Christchurch","icc_nz","VERIFIED","ICC (official): India tour New Zealand for five T20Is, five ODIs and two Tests — the largest inbound tour in New Zealand Cricket history by matches (12). The 1st T20I is 22 Oct at Hagley Oval, Christchurch. ICC ODI ratings for context (19 Oct): India 1st (115), New Zealand 2nd (109) — note this is a T20I, so ODI ratings are background only, not a T20 ranking."),
 ("Eastern Storm","Tuskers","2026-10-22","12:00","Win Match","Eastern Storm",4,4,0,188811,"South Africa domestic T20","csa","OLBG-ONLY",""),
 ("Namibia","Ireland","2026-10-22","04:00","Win Match","Ireland",3,3,2,188828,"One Day International — 1st ODI","icc","OLBG-ONLY",""),
 ("England","Sri Lanka","2026-10-22","04:00","Win Match","England",1,2,0,188829,"One Day International","icc","OLBG-ONLY",""),
 ("Australia W","New Zealand W","2026-10-22","04:15","Win Match","Australia W",1,2,0,188826,"Women's T20 International — 3rd T20","icc","OLBG-ONLY",""),
 ("Mpumalanga Rhinos","South Africa Emerging","2026-10-22","07:00","Win Match","South Africa Emerging",1,2,0,188825,"South Africa domestic T20","csa","OLBG-ONLY",""),
]
for i,(h,a,d,t,mk,sel,f,tt,ex,eid,lg,off,ver,facts) in enumerate(CRI,1):
    suffix = {"188824":"_One_Day_Match","188814":"_1st_T20_Match","188828":"_1st_ODI","188829":"_One_Day_Match","188826":"_3rd_T20_Match"}.get(str(eid),"_T20")
    slug = f"{h}_vs_{a}{suffix}".replace(" ","_")
    add(id=f"CRI-{i:02d}", sport="Cricket", league=lg, home=h, away=a, date=d, time_olbg=t,
        olbg_url=olbg("Cricket",slug,7,eid), olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF[off][0], official_url=OFF[off][1], verification=ver, verified_facts=facts,
        flags=["Cricket has no standard match handicap / match-total market on OLBG (OLBG covers Win Match, Top Batter, Man of the Match) — handicap/total left as n/a rather than invented."])

# ---------------- RUGBY UNION (OLBG id 9) ----------------
RGU = [
 ("Montauban","Oyonnax","2026-10-22","15:00","To Win","Oyonnax",5,7,0,609556,"France Pro D2 (LNR)","lnr","OLBG-ONLY",""),
 ("Agen","Nissa","2026-10-23","13:30","To Win","Nissa",3,4,0,609558,"France Pro D2 (LNR)","lnr","OLBG-ONLY",""),
 ("Soyaux Angouleme","Dax","2026-10-23","13:30","To Win","Dax",3,3,0,609563,"France Pro D2 (LNR)","lnr","OLBG-ONLY",""),
 ("Connacht","Zebre Parma","2026-10-23","14:45","To Win","Connacht",3,5,0,609577,"United Rugby Championship — Round 4","urc","VERIFIED","URC (official fixture list): Connacht v Zebre, Fri 23 Oct, The Sportsground, Galway. OLBG's published URC averages (last 5 seasons): home teams win 64.4%, favourites win 75.3%, average total 48.9 points."),
 ("Narbonne","Brive","2026-10-23","13:00","To Win","Narbonne",2,2,0,609557,"France Pro D2 (LNR)","lnr","OLBG-ONLY",""),
 ("Aurillac","Nevers","2026-10-23","13:30","To Win","Nevers",2,4,0,609560,"France Pro D2 (LNR)","lnr","OLBG-ONLY",""),
 ("Bulls","Ulster","2026-10-24","07:45","Handicap","Ulster +18.50",2,2,0,609576,"United Rugby Championship — Round 4","urc","VERIFIED","URC (official): Vodacom Bulls v Ulster, Sat 24 Oct, Loftus Versfeld, Pretoria. OLBG's most-tipped selection is Ulster +18.5 on the handicap — i.e. the crowd expects a Bulls win but by fewer than 19 points."),
 ("Valence Romans","Colomiers","2026-10-23","13:30","To Win","Colomiers",1,1,0,609559,"France Pro D2 (LNR)","lnr","OLBG-ONLY",""),
 ("Grenoble","Biarritz","2026-10-23","15:00","Handicap","Biarritz +11.50",1,1,0,609561,"France Pro D2 (LNR)","lnr","OLBG-ONLY","OLBG's most-tipped selection is Biarritz +11.5 (handicap) — crowd expects Grenoble to win by fewer than 12, or Biarritz to win."),
 ("Provence","Beziers","2026-10-23","15:00","Handicap","Beziers +28.50",1,1,0,609562,"France Pro D2 (LNR)","lnr","OLBG-ONLY","OLBG's most-tipped selection is Beziers +28.5 (handicap) — a very large head start, implying Provence are rated far stronger."),
 ("Stormers","Scarlets","2026-10-24","10:00","To Win","Stormers",1,2,0,609580,"United Rugby Championship — Round 4","urc","VERIFIED","URC (official): Stormers v Scarlets, Sat 24 Oct, Cape Town."),
 ("Bayonne","Lyon","2026-10-24","10:35","Handicap","Lyon +10.50",1,1,0,609564,"France Top 14 (LNR)","lnr","OLBG-ONLY","OLBG's published Top 14 averages: home teams win 74.4% — the strongest home edge of the four leagues OLBG tracks; average total 49.7 points."),
 ("Toulouse","Perpignan","2026-10-24","10:35","Handicap","Perpignan +23.50",1,1,0,609567,"France Top 14 (LNR)","lnr","OLBG-ONLY","OLBG's most-tipped selection is Perpignan +23.5 (handicap), implying Toulouse are rated roughly three converted tries better at home."),
 ("Leinster","Munster","2026-10-24","13:00","To Win","Leinster",1,1,0,609578,"United Rugby Championship — Round 4","urc","VERIFIED","URC (official): Leinster v Munster, Sat 24 Oct, Aviva Stadium, Dublin — the interprovincial derby is the round's headline fixture."),
 ("La Rochelle","Bordeaux","2026-10-25","16:05","To Win","La Rochelle",None,None,0,609554,"France Top 14 (LNR)","lnr","OLBG-ONLY",""),
]
for i,(h,a,d,t,mk,sel,f,tt,ex,eid,lg,off,ver,facts) in enumerate(RGU,1):
    slug = f"{h}_v_{a}".replace(" ","_")
    fl=[]
    if f is None: fl.append("UNVERIFIED: tip counts cut off in OLBG page fetch — left blank, not estimated.")
    if mk=="Handicap": fl.append("OLBG most-tipped market is the Handicap — the selection's head start is used as a margin signal only (see Methodology).")
    add(id=f"RGU-{i:02d}", sport="Rugby Union", league=lg, home=h, away=a, date=d, time_olbg=t,
        olbg_url=olbg("Rugby_Union",slug,9,eid), olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF[off][0], official_url=OFF[off][1], verification=ver, verified_facts=facts, flags=fl)

# ---------------- VOLLEYBALL (OLBG id 21) — OLBG markets: Win Match + Set Score only ----------------
VOL = [
 ("Puijo W","Orpo W","2026-10-21","10:00","Win Match","Puijo W",3,3,0,36981,"Finland (W) — as listed by OLBG","cev"),
 ("LUK Lublin","Trefl Gdansk","2026-10-21","11:30","Win Match","LUK Lublin",3,3,1,36961,"Poland PlusLiga","plusliga"),
 ("Schweriner W","Erfurt W","2026-10-21","12:00","Win Match","Schweriner W",3,3,0,36945,"Germany (W) — as listed by OLBG","cev"),
 ("Slepsk Suwalki","GKS Katowice","2026-10-23","11:30","Win Match","Slepsk Suwalki",2,2,0,36963,"Poland PlusLiga","plusliga"),
 ("PGE Skra Belchatow","Projekt Warszawa","2026-10-24","12:00","Win Match","Projekt Warszawa",2,2,0,36964,"Poland PlusLiga","plusliga"),
 ("CHKS Chelm","Resovia Rzeszow","2026-10-25","13:00","Win Match","Resovia Rzeszow",2,2,0,36965,"Poland PlusLiga","plusliga"),
 ("Jelcz Laskowice","Stal Nysa","2026-10-21","12:00","Win Match","Stal Nysa",1,1,0,36979,"Poland — as listed by OLBG","plusliga"),
 ("Netzhoppers KW","Helios Grizzlys Giesen","2026-10-21","13:00","Win Match","Helios Grizzlys Giesen",1,1,0,36984,"Germany — as listed by OLBG","cev"),
 ("WWK Volleys Munchen","VfB Friedrichshafen","2026-10-21","13:30","Win Match","VfB Friedrichshafen",1,1,0,36985,"Germany — as listed by OLBG","cev"),
 ("SSC Karlsruhe","SVG Luneburg","2026-10-21","14:00","Win Match","SVG Luneburg",1,1,0,36986,"Germany — as listed by OLBG","cev"),
 ("VC Sneek W","VV Utrecht W","2026-10-21","14:00","Win Match","VC Sneek W",1,1,0,36968,"Netherlands (W) — as listed by OLBG","cev"),
 ("Warta Zawiercie","Kedzierzyn Kozle","2026-10-21","14:30","Win Match","Warta Zawiercie",1,1,0,36962,"Poland PlusLiga","plusliga"),
 ("Vallefoglia W","Cuneo W","2026-10-21","14:30","Set Score","Cuneo W to win 3-0",1,1,0,36977,"Italy (W) — as listed by OLBG","cev"),
 ("Bergamo W","Milano W","2026-10-21","14:30","Win Match","Milano W",1,1,0,36974,"Italy (W) — as listed by OLBG","cev"),
 ("Novara W","Marignano W","2026-10-21","14:30","Win Match","Novara W",None,None,0,36976,"Italy (W) — as listed by OLBG","cev"),
]
for i,(h,a,d,t,mk,sel,f,tt,ex,eid,lg,off) in enumerate(VOL,1):
    slug = f"{h}_vs_{a}".replace(" ","_")
    fl=["Domestic-league fixture confirmed on OLBG only; governing-body link given for manual league-level check (see Flagged page)."]
    if f is None: fl.append("UNVERIFIED: tip counts cut off in OLBG page fetch — left blank, not estimated.")
    if mk=="Set Score": fl.append("OLBG most-tipped market is Set Score (exact sets) — win signal is indirect.")
    add(id=f"VOL-{i:02d}", sport="Volleyball", league=lg, home=h, away=a, date=d, time_olbg=t,
        olbg_url=olbg("Volleyball",slug,21,eid), olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF[off][0], official_url=OFF[off][1], verification="OLBG-ONLY",
        verified_facts="Volleyball is best of 5 sets with no draws; OLBG tips cover Win Match and Set Score only (OLBG volleyball guide). Our set-handicap/total-sets lines are originated from the win probability and labelled as model lines.",
        flags=fl)

# ---------------- HANDBALL (OLBG id 20) — 3-way money line (Home/Tie/Away) ----------------
HND = [
 ("RK Zagreb","PSG Handball","2026-10-21","12:45","Money Line","PSG Handball",8,13,0,12053),
 ("Nantes","HC Vardar","2026-10-21","14:45","Money Line","Nantes",6,10,0,12050),
 ("Veszprem","Fuchse Berlin","2026-10-21","12:45","Money Line","Veszprem",5,11,0,12055),
 ("Sandefjord","Runar","2026-10-21","12:15","Money Line","Runar",4,5,0,12115),
 ("Dinamo Bucuresti","Skanderborg Handbold","2026-10-21","12:45","Money Line","Dinamo Bucuresti",4,11,0,12045),
 ("Aalborg Handbold","RK Celje","2026-10-21","14:45","Money Line","Tie",4,5,0,12044),
 ("RK Partizan","FC Porto","2026-10-21","12:45","Money Line","RK Partizan",3,8,0,12052),
 ("HC Kriens Luzern","KS Kielce","2026-10-21","14:45","Money Line","Tie",3,6,0,12047),
 ("Kolstad","SC Magdeburg","2026-10-22","14:45","Money Line","Tie",3,6,0,12048),
 ("Sporting CP","IFK Kristianstad","2026-10-22","14:45","Money Line","Tie",3,7,0,12054),
 ("IF Hallby HK","IK Savehof","2026-10-21","13:00","Money Line","IK Savehof",2,3,0,12114),
 ("Hammarby IF HF","Alingsas HK","2026-10-21","13:00","Money Line","Hammarby IF HF",2,3,0,12112),
 ("Mors Thy Handbold","Bjerringbro Silkeborg","2026-10-21","14:00","Match Handicap","Mors Thy Handbold +3.50",2,2,1,12072),
 ("MT Melsungen","Wisla Plock","2026-10-22","12:45","Money Line","MT Melsungen",2,4,0,12049),
 ("Pick Szeged","GOG","2026-10-22","12:45","Money Line","GOG",2,4,0,12051),
 ("FC Barcelona","Montpellier","2026-10-22","14:45","Money Line","Montpellier",2,6,0,12046),
 ("Estonia W","Kosovo W","2026-10-23","14:00","Money Line","Kosovo (W)",2,2,0,12110),
 ("Skive FH","Aalborg Handbold","2026-10-24","09:00","Money Line","Aalborg Handbold",2,2,0,12076),
 ("Belgium W","Lithuania W","2026-10-21","11:15","Money Line","Belgium (W)",1,2,0,12108),
 ("HK Malmo","Lugi HF","2026-10-21","13:00","Money Line","HK Malmo",1,2,0,12113),
]
for i,(h,a,d,t,mk,sel,f,tt,ex,eid) in enumerate(HND,1):
    slug = f"{h}_vs_{a}".replace(" ","_")
    fl=[]
    facts="European club handball. OLBG handball markets: 3-way money line (regular time), match handicap and points total. OLBG's published EHF Champions League (men) averages over the last five editions: 60.82 goals per game, average winning margin 5.04 goals, ties in 9.8% of games with a clear favourite — our originated total/handicap baselines use these published figures."
    if sel=="Tie":
        fl.append("IRREGULARITY: OLBG's most-tipped selection is the Tie in a 3-way market. Ties occurred in under 10% of comparable EHF Champions League games (OLBG stats), so a Tie cannot be the model winner pick. Winner pick falls back to the home side at LOW confidence and is flagged for manual review — the home/away split of the remaining tips is not shown in OLBG's feed.")
    if mk=="Match Handicap":
        fl.append("OLBG most-tipped market is the Match Handicap — used as a margin signal only.")
    add(id=f"HND-{i:02d}", sport="Handball", league="European club / international handball — competition per match not named in OLBG feed",
        home=h, away=a, date=d, time_olbg=t, olbg_url=olbg("Handball",slug,20,eid),
        olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF["ehf"][0], official_url=OFF["ehf"][1], verification="OLBG-ONLY", verified_facts=facts, flags=fl)

# ---------------- GAELIC FOOTBALL (OLBG id 25) — Hurling is EXCLUDED per brief; Gaelic Football is covered ----------------
GAE = [
 ("St Finbarrs","Nemo Rangers","2026-10-25","12:00","Handicap","Nemo Rangers +1.50",10,12,0,3530,"OLBG's hub also shows 'Draw' as most-tipped (10/20) in the match-result market for this fixture — two different markets point two ways (narrow home win or draw). Our winner pick uses the handicap signal: Nemo +1.5 with 83% support implies a one-score game."),
 ("Moycullen","Salthill-Knocknacarra","2026-10-24","14:00","Handicap","Moycullen -3.50",9,17,0,3532,""),
 ("Kanturk","Eire Og Cor","2026-11-01","09:00","To Win","Kanturk",3,4,0,3531,""),
 ("Rathgormack","The Nire","2026-11-01","10:30","Handicap","Rathgormack -2.50",1,1,0,3536,""),
]
for i,(h,a,d,t,mk,sel,f,tt,ex,eid,facts) in enumerate(GAE,1):
    slug = f"{h}_v_{a}".replace(" ","_").replace("-","-")
    fl=["Club championship fixture confirmed on OLBG only; GAA link given for manual check. OLBG does not name the specific county championship in its feed."]
    if mk=="Handicap": fl.append("OLBG most-tipped market is the Handicap — used as a margin signal (see Methodology).")
    add(id=f"GAE-{i:02d}", sport="Gaelic Football", league="GAA club football — as listed by OLBG",
        home=h, away=a, date=d, time_olbg=t, olbg_url=olbg("Gaelic_Football",slug,25,eid),
        olbg_market=mk, olbg_selection=sel, tips_for=f, tips_total=tt, experts=ex,
        official_label=OFF["gaa"][0], official_url=OFF["gaa"][1], verification="OLBG-ONLY",
        verified_facts=(facts + " Gaelic football matches can end level; our 3-way model carries an explicit draw allowance (see Methodology). Hurling fixtures on OLBG are excluded from this project by the brief and are not listed.").strip(),
        flags=fl)

out = {
 "meta": {
   "harvest_date": H,
   "source_site": "https://www.olbg.com/betting-tips",
   "note": "Snapshot of OLBG upcoming events with tips open at harvest. OLBG lists further fixtures with zero tips behind a 'Load More' control that could not be enumerated from fetched pages — coverage = every event visible in the fetched sport feeds. Bookmaker odds columns were not present in fetched page text and are therefore neither copied nor shown; all odds on this site are our own originated fair prices (see Methodology).",
   "excluded_sports": ["Football/Soccer","Boxing","UFC/MMA","American Football","Hurling","Horse Racing","Cycling","Specials"],
   "zero_match_sports": [
     {"sport":"Rugby League","reason":"Off-season on 21 Oct 2026: OLBG's Rugby League feed shows only outright markets (State of Origin 2027, Super League 2027, NRL 2027) and no upcoming matches. No fixtures invented.","olbg_url":"https://www.olbg.com/betting-tips/Rugby_League/10","official_label":"Rugby Football League (official)","official_url":"https://www.rugby-league.com/"},
     {"sport":"Golf","reason":"OLBG covers golf as tournament outrights, not head-to-head matches — there is no win-match / handicap / match-total market to originate. Out of match scope; see Flagged page.","olbg_url":"https://www.olbg.com/betting-tips","official_label":"PGA Tour (official)","official_url":"https://www.pgatour.com/"},
     {"sport":"Greyhound Racing","reason":"Races with multiple runners, not two-sided matches — no match winner/handicap/total market exists. Out of match scope; see Flagged page.","olbg_url":"https://www.olbg.com/betting-tips","official_label":"Greyhound Board of Great Britain (official)","official_url":"https://gbgb.org.uk/"},
     {"sport":"Motor Racing","reason":"Races/outrights, not two-sided matches — no match handicap or match total. Out of match scope; see Flagged page.","olbg_url":"https://www.olbg.com/betting-tips","official_label":"Formula 1 (official)","official_url":"https://www.formula1.com/"}
   ]
 },
 "matches": M
}
p = pathlib.Path(__file__).resolve().parent.parent / "data" / "matches.json"
p.write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(f"Wrote {len(M)} matches -> {p}")
from collections import Counter
print(Counter(m['sport'] for m in M))
