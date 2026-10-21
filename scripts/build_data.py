#!/usr/bin/env python3
"""Build data/matches.{csv,json} from OLBG sport-page snapshot (2026-10-21).

RAW rows below were transcribed line-by-line from live fetches of OLBG sport
pages on 2026-10-21 (see research/verification-log.md for URLs).
Fields: sport, competition, date_label (as displayed), date_iso, time_display,
match, leading_market, leading_selection, tips_for, tips_total, pct_display,
experts, event_id, olbg_url, event_type (match|outright|race)

Originated lines + confidence are computed here by the published formula
(research/methodology.md). No bookmaker odds are recorded: OLBG prices were
not visible in the fetched pages ("WIN @" with no price), so that field is
left blank and flagged site-wide.
"""
import csv, json, pathlib

SNAP = "2026-10-21"
WINNER_MARKETS = {"Win Match", "Money Line", "To Win", "Win Match 2-way", "Win Tournament",
                  "Outright Winner", "Grand Final Winner", "Win Race", "Daily Races", "Daily Racing"}

# sport, comp, date_label, date_iso, time, match, market, selection, k, n, pct, experts, event_id, url, etype
RAW = [
# ---- TENNIS (ID 3) ----
("Tennis","","Today","2026-10-21","02:30","Leylah Fernandez vs Aliaksandra Sasnovich","Win Match","Leylah Fernandez",6,7,86,0,902039,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Leylah_Fernandez_vs_Aliaksandra_Sasnovich/3?event_id=902039","match"),
("Tennis","","Today","2026-10-21","01:30","Katie Boulter vs Viktorija Golubic","Win Match","Katie Boulter",5,8,63,1,902065,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Katie_Boulter_vs_Viktorija_Golubic/3?event_id=902065","match"),
("Tennis","","Today","2026-10-21","02:30","James Duckworth vs Luciano Darderi","Win Match","Luciano Darderi",4,5,80,0,902038,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/James_Duckworth_vs_Luciano_Darderi/3?event_id=902038","match"),
("Tennis","","Today","2026-10-21","05:30","Adrian Mannarino vs Andrey Rublev","Win Match","Andrey Rublev",4,5,80,0,902037,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Adrian_Mannarino_vs_Andrey_Rublev/3?event_id=902037","match"),
("Tennis","","Today","2026-10-21","04:00","Sorana Cirstea vs Sara Bejlek","Win Match","Sara Bejlek",3,6,50,0,902074,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Sorana_Cirstea_vs_Sara_Bejlek/3?event_id=902074","match"),
("Tennis","","Today","2026-10-21","04:00","Zangar Nurlanuly vs Tomas Machac","1st Set Winner","Zangar Nurlanuly",3,4,75,0,901935,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Zangar_Nurlanuly_vs_Tomas_Machac/3?event_id=901935","match"),
("Tennis","","Today","2026-10-21","02:30","Mattia Bellucci vs Tomas Martin Etcheverry","Set Betting","Tomas Martin Etcheverry to win 2 - 1",2,3,67,0,901993,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Mattia_Bellucci_vs_Tomas_Martin_Etcheverry/3?event_id=901993","match"),
("Tennis","","Today","2026-10-21","05:30","Dino Prizmic vs Damir Dzumhur","Win Match","Damir Dzumhur",2,2,100,0,901896,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Dino_Prizmic_vs_Damir_Dzumhur/3?event_id=901896","match"),
("Tennis","","Today","2026-10-21","08:00","Stan Wawrinka vs Martin Landaluce","Win Match","Stan Wawrinka",2,2,100,0,901974,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Stan_Wawrinka_vs_Martin_Landaluce/3?event_id=901974","match"),
("Tennis","","Today","2026-10-21","12:00","David Goffin vs Remy Bertola","Win Match","David Goffin",2,2,100,0,902028,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/David_Goffin_vs_Remy_Bertola/3?event_id=902028","match"),
("Tennis","","Today","2026-10-21","04:00","Facundo Diaz Acosta vs Nikoloz Basilashvili","Set Betting","Nikoloz Basilashvili to win 2 - 1",1,2,50,0,902040,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Facundo_Diaz_Acosta_vs_Nikoloz_Basilashvili/3?event_id=902040","match"),
("Tennis","","Today","2026-10-21","05:30","Martin Damm vs Francisco Cerundolo","Set Betting","Francisco Cerundolo to win 2 - 1",1,1,100,0,902048,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Martin_Damm_vs_Francisco_Cerundolo/3?event_id=902048","match"),
("Tennis","","Today","2026-10-21","07:00","Mariano Navone vs Tallon Griekspoor","Win Match","Tallon Griekspoor",1,1,100,0,902085,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Mariano_Navone_vs_Tallon_Griekspoor/3?event_id=902085","match"),
("Tennis","","Today","2026-10-21","07:00","Ekaterina Alexandrova vs Marta Kostyuk","Win Match","Marta Kostyuk",1,1,100,0,902084,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Ekaterina_Alexandrova_vs_Marta_Kostyuk/3?event_id=902084","match"),
("Tennis","","Today","2026-10-21","08:30","Clement Chidekh vs Jacob Fearnley","Set Betting","Clement Chidekh to win 2 - 1",1,1,100,0,902094,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Clement_Chidekh_vs_Jacob_Fearnley/3?event_id=902094","match"),
("Tennis","","Today","2026-10-21","09:30","Corentin Moutet vs Felix Balshaw","Set Betting","Corentin Moutet to win 2 - 1",1,1,100,0,902095,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Corentin_Moutet_vs_Felix_Balshaw/3?event_id=902095","match"),
("Tennis","","Today","2026-10-21","10:30","Stefanos Tsitsipas vs Mikhail Kukushkin","Set Betting","Stefanos Tsitsipas to win 2 - 0",1,1,100,0,902083,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Stefanos_Tsitsipas_vs_Mikhail_Kukushkin/3?event_id=902083","match"),
("Tennis","","Today","2026-10-21","13:00","Moise Kouame vs Lorenzo Musetti","Win Match","Moise Kouame",1,2,50,0,902059,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Moise_Kouame_vs_Lorenzo_Musetti/3?event_id=902059","match"),
("Tennis","","Today","2026-10-21","14:30","Benjamin Bonzi vs Tommy Paul","Set Betting","Tommy Paul to win 2 - 1",1,1,100,0,902102,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Benjamin_Bonzi_vs_Tommy_Paul/3?event_id=902102","match"),
("Tennis","","Today","2026-10-21","23:00","Katarzyna Kawa vs Belinda Bencic","1st Set Winner","Belinda Bencic",1,1,100,0,902093,"https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Katarzyna_Kawa_vs_Belinda_Bencic/3?event_id=902093","match"),
# ---- BASKETBALL (ID 4) ----
("Basketball","NBA","Today","2026-10-21","19:10","MIL Bucks @ WAS Wizards","Money Line","WAS Wizards",9,11,82,0,534889,"https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIL_Bucks_@_WAS_Wizards/4?event_id=534889","match"),
("Basketball","Euroleague","Today","2026-10-21","12:00","Hapoel Tel Aviv vs Virtus Bologna","Money Line","Hapoel Tel Aviv",5,8,63,1,535919,"https://www.olbg.com/betting-tips/Basketball/European/Euroleague/Hapoel_Tel_Aviv_vs_Virtus_Bologna/4?event_id=535919","match"),
("Basketball","Korea KBL","Today","2026-10-21","06:00","Seoul Thunders vs KCC Egis","Money Line","Seoul Thunders",3,5,60,0,535966,"https://www.olbg.com/betting-tips/Basketball/Other/Korea_KBL/Seoul_Thunders_vs_KCC_Egis/4?event_id=535966","match"),
("Basketball","NBA","Today","2026-10-21","19:10","ATL Hawks @ ORL Magic","Money Line","ATL Hawks",3,5,60,0,534888,"https://www.olbg.com/betting-tips/Basketball/NBA/NBA/ATL_Hawks_@_ORL_Magic/4?event_id=534888","match"),
("Basketball","NBA","Today","2026-10-21","19:40","CHI Bulls @ TOR Raptors","Money Line","TOR Raptors",3,4,75,0,535673,"https://www.olbg.com/betting-tips/Basketball/NBA/NBA/CHI_Bulls_@_TOR_Raptors/4?event_id=535673","match"),
("Basketball","Euro Cup","Today","2026-10-21","13:00","PAOK vs Ratiopharm Ulm","Money Line","PAOK",2,2,100,0,535952,"https://www.olbg.com/betting-tips/Basketball/European/Euro_Cup/PAOK_vs_Ratiopharm_Ulm/4?event_id=535952","match"),
("Basketball","Euro Cup","Today","2026-10-21","13:30","Bosna Sarajevo vs Bahcesehir Koleji","Money Line","Bahcesehir Koleji",2,3,67,0,535950,"https://www.olbg.com/betting-tips/Basketball/European/Euro_Cup/Bosna_Sarajevo_vs_Bahcesehir_Koleji/4?event_id=535950","match"),
("Basketball","Euro Cup","Today","2026-10-21","14:00","Hapoel Jerusalem vs Rigas Zelli","Money Line","Hapoel Jerusalem",2,3,67,0,535956,"https://www.olbg.com/betting-tips/Basketball/European/Euro_Cup/Hapoel_Jerusalem_vs_Rigas_Zelli/4?event_id=535956","match"),
("Basketball","NBA","Today","2026-10-21","20:10","IND Pacers @ NO Pelicans","Money Line","NO Pelicans",2,4,50,0,534892,"https://www.olbg.com/betting-tips/Basketball/NBA/NBA/IND_Pacers_@_NO_Pelicans/4?event_id=534892","match"),
("Basketball","NBA","Today","2026-10-21","22:10","PHX Suns @ POR Trail Blazers","Money Line","PHX Suns",2,3,67,0,534893,"https://www.olbg.com/betting-tips/Basketball/NBA/NBA/PHX_Suns_@_POR_Trail_Blazers/4?event_id=534893","match"),
("Basketball","Euroleague","Tomorrow","2026-10-22","14:15","Panathinaikos vs Baskonia","Money Line","Panathinaikos",2,3,67,0,535923,"https://www.olbg.com/betting-tips/Basketball/European/Euroleague/Panathinaikos_vs_Baskonia/4?event_id=535923","match"),
("Basketball","NBA","Tomorrow","2026-10-22","21:40","DEN Nuggets @ OKC Thunder","Money Line","OKC Thunder",2,2,100,0,534843,"https://www.olbg.com/betting-tips/Basketball/NBA/NBA/DEN_Nuggets_@_OKC_Thunder/4?event_id=534843","match"),
("Basketball","Euro Cup","Today","2026-10-21","12:00","U BT Cluj Napoca vs London Lions","Money Line","London Lions",1,2,50,0,535949,"https://www.olbg.com/betting-tips/Basketball/European/Euro_Cup/U_BT_Cluj_Napoca_vs_London_Lions/4?event_id=535949","match"),
("Basketball","Basketball Champions League","Today","2026-10-21","12:00","AEK vs Antwerp Giants","Money Line","Antwerp Giants",1,2,50,0,535969,"https://www.olbg.com/betting-tips/Basketball/European/Basketball_Champions_League/AEK_vs_Antwerp_Giants/4?event_id=535969","match"),
("Basketball","Basketball Champions League","Today","2026-10-21","12:30","Bnei Herzliya vs FC Porto","Money Line","FC Porto",1,1,100,0,535970,"https://www.olbg.com/betting-tips/Basketball/European/Basketball_Champions_League/Bnei_Herzliya_vs_FC_Porto/4?event_id=535970","match"),
("Basketball","Euro Cup","Today","2026-10-21","13:00","Chemnitz 99 vs Slask Wroclaw","Money Line","Slask Wroclaw",1,1,100,0,535951,"https://www.olbg.com/betting-tips/Basketball/European/Euro_Cup/Chemnitz_99_vs_Slask_Wroclaw/4?event_id=535951","match"),
("Basketball","Euro Cup","Today","2026-10-21","13:00","Tortona vs San Pablo Burgos","Money Line","San Pablo Burgos",1,1,100,0,535953,"https://www.olbg.com/betting-tips/Basketball/European/Euro_Cup/Tortona_vs_San_Pablo_Burgos/4?event_id=535953","match"),
("Basketball","Euro Cup","Today","2026-10-21","13:30","Bourg vs Trento","Money Line","Trento",1,1,100,0,535954,"https://www.olbg.com/betting-tips/Basketball/European/Euro_Cup/Bourg_vs_Trento/4?event_id=535954","match"),
("Basketball","Euro Cup","Today","2026-10-21","13:30","Frankfurt Skyliners vs Tenerife","Money Line","Frankfurt Skyliners",1,1,100,0,535955,"https://www.olbg.com/betting-tips/Basketball/European/Euro_Cup/Frankfurt_Skyliners_vs_Tenerife/4?event_id=535955","match"),
("Basketball","Basketball Champions League","Today","2026-10-21","14:00","Joventut vs Telekom Bonn","Money Line","Joventut",1,1,100,0,535971,"https://www.olbg.com/betting-tips/Basketball/European/Basketball_Champions_League/Joventut_vs_Telekom_Bonn/4?event_id=535971","match"),
# ---- GOLF (ID 5) — outrights ----
("Golf","","25 Oct","2026-10-25","04:00","Genesis Championship","Win Tournament","Si Woo Kim",5,18,28,0,101905,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Genesis_Championship/5?event_id=101905","outright"),
("Golf","","25 Oct","2026-10-25","17:45","Bermuda Championship","Win Tournament","Ben James",3,12,25,0,101904,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Bermuda_Championship/5?event_id=101904","outright"),
("Golf","","25 Oct","2026-10-25","02:45","Players Series SA","Win Tournament","Josh Armstrong",2,2,100,1,101907,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Players_Series_SA/5?event_id=101907","outright"),
("Golf","","25 Oct","2026-10-25","04:00","BMW Ladies Championship","Win Tournament","Sei Young Kim",2,8,25,0,101906,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/BMW_Ladies_Championship/5?event_id=101906","outright"),
("Golf","","25 Oct","2026-10-25","17:45","Stifel Charity Classic","Win Tournament","Steven Alker",2,7,29,0,101903,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Stifel_Charity_Classic/5?event_id=101903","outright"),
("Golf","","24 Oct","2026-10-24","11:45","Senior Italian Open","Win Tournament","Mikael Lundberg",1,2,50,0,101911,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Senior_Italian_Open/5?event_id=101911","outright"),
("Golf","","25 Oct","2026-10-25","02:45","Fortinet Players Cup","Win Tournament","Ryosuke Kinoshita",1,2,50,0,101908,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Fortinet_Players_Cup/5?event_id=101908","outright"),
("Golf","","25 Oct","2026-10-25","03:45","Hong Kong Open","Win Tournament","Paul Casey",1,3,33,0,101910,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Hong_Kong_Open/5?event_id=101910","outright"),
("Golf","","25 Oct","2026-10-25","10:45","Stella Artois Players Championship","Win Tournament","Daniel van Tonder",1,2,50,0,101912,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Stella_Artois_Players_Championship/5?event_id=101912","outright"),
("Golf","","25 Oct","2026-10-25","08:00","Hero Womens Indian Open","Win Tournament","Avani Prashanth",0,0,None,0,101909,"https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Hero_Womens_Indian_Open/5?event_id=101909","outright"),
# ---- CRICKET (ID 7) ----
("Cricket","","Today","2026-10-21","07:30","Afghanistan vs Bangladesh One Day Match","Win Match","Afghanistan",7,7,100,1,188824,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Afghanistan_vs_Bangladesh_One_Day_Match/7?event_id=188824","match"),
("Cricket","","Today","2026-10-21","07:00","Northern Cape Heat vs Garden Route Badgers T20","Win Match","Garden Route Badgers",5,8,63,2,188823,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Northern_Cape_Heat_vs_Garden_Route_Badgers_T20/7?event_id=188823","match"),
("Cricket","","Today","2026-10-21","12:00","North West Dragons vs Limpopo Impalas T20","Win Match","North West Dragons",5,6,83,1,188810,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/North_West_Dragons_vs_Limpopo_Impalas_T20/7?event_id=188810","match"),
("Cricket","","Tomorrow","2026-10-22","03:00","New Zealand vs India 1st T20 Match","Win Match","India",5,7,71,1,188814,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/New_Zealand_vs_India_1st_T20_Match/7?event_id=188814","match"),
("Cricket","","Tomorrow","2026-10-22","12:00","Eastern Storm vs Tuskers T20","Win Match","Eastern Storm",4,4,100,0,188811,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Eastern_Storm_vs_Tuskers_T20/7?event_id=188811","match"),
("Cricket","","Tomorrow","2026-10-22","04:00","Namibia vs Ireland 1st ODI","Win Match","Ireland",3,3,100,2,188828,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Namibia_vs_Ireland_1st_ODI/7?event_id=188828","match"),
("Cricket","","Tomorrow","2026-10-22","04:00","England vs Sri Lanka One Day Match","Win Match","England",1,2,50,0,188829,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/England_vs_Sri_Lanka_One_Day_Match/7?event_id=188829","match"),
("Cricket","","Tomorrow","2026-10-22","04:15","Australia W vs New Zealand W 3rd T20 Match","Win Match","Australia W",1,2,50,0,188826,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Australia_W_vs_New_Zealand_W_3rd_T20_Match/7?event_id=188826","match"),
("Cricket","","Tomorrow","2026-10-22","07:00","Mpumalanga Rhinos vs South Africa Emerging T20","Win Match","South Africa Emerging",1,2,50,0,188825,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Mpumalanga_Rhinos_vs_South_Africa_Emerging_T20/7?event_id=188825","match"),
("Cricket","","21 Nov 2027","2027-11-21","05:00","World Cup 2027","Outright Winner","India",6,12,50,0,182606,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/World_Cup_2027/7?event_id=182606","outright"),
("Cricket","","05 Dec","2026-12-05","03:10","Big Bash Women 2026","Outright Winner","Sydney Sixers W",2,3,67,0,187184,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Big_Bash_Women_2026/7?event_id=187184","outright"),
("Cricket","","12 Dec","2026-12-12","03:15","T20 Big Bash 2026-27","Outright Winner","Adelaide Strikers",1,2,50,0,187503,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/T20_Big_Bash_2026-27/7?event_id=187503","outright"),
("Cricket","","24 Jan 2027","2027-01-24","11:30","SA20 2026-27","Outright Winner","Pretoria Capitals",1,1,100,0,187504,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/SA20_2026-27/7?event_id=187504","outright"),
("Cricket","","18 Jul 2027","2027-07-18","11:00","T20 Blast 2027","Outright Winner","Sussex",0,0,None,0,188350,"https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/T20_Blast_2027/7?event_id=188350","outright"),
# ---- SNOOKER (ID 8) ----
("Snooker","","Today","2026-10-21","05:00","Cheung Ka Wai v Stuart Bingham","Win Match","Cheung Ka Wai",8,11,73,0,9933,"https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Cheung_Ka_Wai_v_Stuart_Bingham/8?event_id=9933","match"),
("Snooker","","Today","2026-10-21","05:00","Pang Junxu v Liam Davies","Win Match","Pang Junxu",6,9,67,0,9929,"https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Pang_Junxu_v_Liam_Davies/8?event_id=9929","match"),
("Snooker","","Today","2026-10-21","15:00","Elliot Slessor v Jamie Jones","Win Match","Jamie Jones",4,4,100,0,9931,"https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Elliot_Slessor_v_Jamie_Jones/8?event_id=9931","match"),
("Snooker","","Today","2026-10-21","15:00","Luca Brecel v Martin O Donnell","Win Match","Martin O Donnell",4,5,80,0,9932,"https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Luca_Brecel_v_Martin_O_Donnell/8?event_id=9932","match"),
("Snooker","","Today","2026-10-21","08:00","John Higgins v Jak Jones","Win Match","John Higgins",3,6,50,0,9934,"https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/John_Higgins_v_Jak_Jones/8?event_id=9934","match"),
("Snooker","","Today","2026-10-21","09:00","Sam Craigie v Xu Si","Win Match","Sam Craigie",3,3,100,0,9930,"https://www.olbg.com/betting-tips/Snooker/All_Snooker/All_Events/Sam_Craigie_v_Xu_Si/8?event_id=9930","match"),
# ---- RUGBY UNION (ID 9) ----
("Rugby Union","","Tomorrow","2026-10-22","15:00","Montauban v Oyonnax","To Win","Oyonnax",5,7,71,0,609556,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Montauban_v_Oyonnax/9?event_id=609556","match"),
("Rugby Union","","23 Oct","2026-10-23","13:30","Agen v Nissa","To Win","Nissa",3,4,75,0,609558,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Agen_v_Nissa/9?event_id=609558","match"),
("Rugby Union","","23 Oct","2026-10-23","13:30","Soyaux Angouleme v Dax","To Win","Dax",3,3,100,0,609563,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Soyaux_Angouleme_v_Dax/9?event_id=609563","match"),
("Rugby Union","","23 Oct","2026-10-23","14:45","Connacht v Zebre Parma","To Win","Connacht",3,5,60,0,609577,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Connacht_v_Zebre_Parma/9?event_id=609577","match"),
("Rugby Union","","23 Oct","2026-10-23","13:00","Narbonne v Brive","To Win","Narbonne",2,2,100,0,609557,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Narbonne_v_Brive/9?event_id=609557","match"),
("Rugby Union","","23 Oct","2026-10-23","13:30","Aurillac v Nevers","To Win","Nevers",2,4,50,0,609560,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Aurillac_v_Nevers/9?event_id=609560","match"),
("Rugby Union","","24 Oct","2026-10-24","07:45","Bulls v Ulster","Handicap","Ulster +18.50",2,2,100,0,609576,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Bulls_v_Ulster/9?event_id=609576","match"),
("Rugby Union","","23 Oct","2026-10-23","13:30","Valence Romans v Colomiers","To Win","Colomiers",1,1,100,0,609559,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Valence_Romans_v_Colomiers/9?event_id=609559","match"),
("Rugby Union","","23 Oct","2026-10-23","15:00","Grenoble v Biarritz","Handicap","Biarritz +11.50",1,1,100,0,609561,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Grenoble_v_Biarritz/9?event_id=609561","match"),
("Rugby Union","","23 Oct","2026-10-23","15:00","Provence v Beziers","Handicap","Beziers +28.50",1,1,100,0,609562,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Provence_v_Beziers/9?event_id=609562","match"),
("Rugby Union","","24 Oct","2026-10-24","10:00","Stormers v Scarlets","To Win","Stormers",1,2,50,0,609580,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Stormers_v_Scarlets/9?event_id=609580","match"),
("Rugby Union","","24 Oct","2026-10-24","10:35","Bayonne v Lyon","Handicap","Lyon +10.50",1,1,100,0,609564,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Bayonne_v_Lyon/9?event_id=609564","match"),
("Rugby Union","","24 Oct","2026-10-24","10:35","Toulouse v Perpignan","Handicap","Perpignan +23.50",1,1,100,0,609567,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Toulouse_v_Perpignan/9?event_id=609567","match"),
("Rugby Union","","24 Oct","2026-10-24","13:00","Leinster v Munster","To Win","Leinster",1,1,100,0,609578,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Leinster_v_Munster/9?event_id=609578","match"),
("Rugby Union","","25 Oct","2026-10-25","16:05","La Rochelle v Bordeaux","To Win","La Rochelle",None,None,None,0,609554,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/La_Rochelle_v_Bordeaux/9?event_id=609554","match"),
("Rugby Union","","14 Mar 2027","2027-03-14","16:00","Six Nations 2027","Win Tournament","Ireland",3,9,33,0,609013,"https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Six_Nations_2027/9?event_id=609013","outright"),
# ---- RUGBY LEAGUE (ID 10) — outrights only on snapshot date ----
("Rugby League","","27 May 2027","2027-05-27","06:00","State of Origin 2027","Win Tournament","New South Wales",9,12,75,0,2695857,"https://www.olbg.com/betting-tips/Rugby_League/All_Rugby_League/All_Events/State_of_Origin_2027/10?event_id=2695857","outright"),
("Rugby League","","02 Oct 2027","2027-10-02","13:00","Super League 2027","Grand Final Winner","Leeds Rhinos",1,3,33,0,2801554,"https://www.olbg.com/betting-tips/Rugby_League/All_Rugby_League/All_Events/Super_League_2027/10?event_id=2801554","outright"),
("Rugby League","","03 Oct 2027","2027-10-03","04:30","NRL 2027","Grand Final Winner","Penrith Panthers",1,1,100,0,2801600,"https://www.olbg.com/betting-tips/Rugby_League/All_Rugby_League/All_Events/NRL_2027/10?event_id=2801600","outright"),
# ---- BASEBALL (ID 12) ----
("Baseball","MLB","23 Oct","2026-10-23","20:00","TB Rays @ MIL Brewers","Money Line","TB Rays",3,6,50,1,160789,"https://www.olbg.com/betting-tips/Baseball/MLB/MLB/TB_Rays_@_MIL_Brewers/12?event_id=160789","match"),
# ---- ICE HOCKEY (ID 13) ----
("Ice Hockey","Austria EHL","Today","2026-10-21","18:45","Pustertal vs Pioneers Vorarlberg","Money Line","Pustertal",2,2,100,0,199881,"https://www.olbg.com/betting-tips/Ice_Hockey/Other/Austria_EHL/Pustertal_vs_Pioneers_Vorarlberg/13?event_id=199881","match"),
("Ice Hockey","Austria EHL","Today","2026-10-21","18:45","HCB Sudtirol Alperia vs HC TWK Innsbruck","Money Line","HCB Sudtirol Alperia",2,2,100,0,199878,"https://www.olbg.com/betting-tips/Ice_Hockey/Other/Austria_EHL/HCB_Sudtirol_Alperia_vs_HC_TWK_Innsbruck/13?event_id=199878","match"),
("Ice Hockey","Swedish Hockey League","Tomorrow","2026-10-22","18:00","Timra IK vs Farjestad BK","Money Line","Farjestad BK",2,2,100,2,199901,"https://www.olbg.com/betting-tips/Ice_Hockey/Other/Swedish_Hockey_League/Timra_IK_vs_Farjestad_BK/13?event_id=199901","match"),
("Ice Hockey","Austria EHL","Today","2026-10-21","17:30","Graz 99ers vs Milano HC","Puck Line","Graz 99ers -1.50",1,1,100,0,199876,"https://www.olbg.com/betting-tips/Ice_Hockey/Other/Austria_EHL/Graz_99ers_vs_Milano_HC/13?event_id=199876","match"),
("Ice Hockey","Austria EHL","Today","2026-10-21","18:15","KAC Klagenfurt vs Fehervar AV19","Money Line","KAC Klagenfurt",1,1,100,0,199880,"https://www.olbg.com/betting-tips/Ice_Hockey/Other/Austria_EHL/KAC_Klagenfurt_vs_Fehervar_AV19/13?event_id=199880","match"),
("Ice Hockey","NHL","Tomorrow","2026-10-22","00:37","PHI Flyers @ BUF Sabres","Game Totals","Over 5.50",1,1,100,0,199897,"https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/PHI_Flyers_@_BUF_Sabres/13?event_id=199897","match"),
("Ice Hockey","NHL","Tomorrow","2026-10-22","00:37","FLA Panthers @ OTT Senators","Game Totals","Over 5.50",1,1,100,0,199896,"https://www.olbg.com/betting-tips/Ice_Hockey/NHL/NHL/FLA_Panthers_@_OTT_Senators/13?event_id=199896","match"),
# ---- MOTOR RACING (ID 14) ----
("Motor Racing","","25 Oct","2026-10-25","16:00","USA Grand Prix","Win Race","Max Verstappen",10,31,32,2,913,"https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/USA_Grand_Prix/14?event_id=913","outright"),
("Motor Racing","","06 Dec","2026-12-06","08:00","Formula 1 Drivers Championship 2026","Win Tournament","Max Verstappen",9,33,27,0,828,"https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/Formula_1_Drivers_Championship_2026/14?event_id=828","outright"),
("Motor Racing","","06 Dec","2026-12-06","08:00","Formula 1 Drivers Championship 2026 Without Kimi Antonelli","Win Tournament","Max Verstappen",4,6,67,0,912,"https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/Formula_1_Drivers_Championship_2026_Without_Kimi_Antonelli/14?event_id=912","outright"),
# ---- DARTS (ID 15) ----
("Darts","","Tomorrow","2026-10-22","13:15","Luke Woodhouse vs Dirk van Duijvenbode","Win Match 2-way","Dirk van Duijvenbode",7,8,88,1,32324,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Luke_Woodhouse_vs_Dirk_van_Duijvenbode/15?event_id=32324","match"),
("Darts","","Tomorrow","2026-10-22","14:15","Niels Zonneveld vs Cameron Menzies","Win Match 2-way","Niels Zonneveld",6,7,86,0,32334,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Niels_Zonneveld_vs_Cameron_Menzies/15?event_id=32334","match"),
("Darts","","Tomorrow","2026-10-22","14:45","Gerwyn Price vs Rob Cross","Win Match 2-way","Gerwyn Price",5,7,71,0,32325,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Gerwyn_Price_vs_Rob_Cross/15?event_id=32325","match"),
("Darts","","Tomorrow","2026-10-22","15:15","James Wade vs Damon Heta","Win Match 2-way","James Wade",5,8,63,0,32322,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/James_Wade_vs_Damon_Heta/15?event_id=32322","match"),
("Darts","","Tomorrow","2026-10-22","15:45","Luke Humphries vs Ryan Searle","Win Match 2-way","Luke Humphries",5,7,71,0,32337,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Luke_Humphries_vs_Ryan_Searle/15?event_id=32337","match"),
("Darts","","Tomorrow","2026-10-22","13:45","Danny Noppert vs Stephen Bunting","Total Legs","Over 9.50",4,4,100,1,32330,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Danny_Noppert_vs_Stephen_Bunting/15?event_id=32330","match"),
("Darts","","Tomorrow","2026-10-22","16:15","Gian van Veen vs Andrew Gilding","Win Match 2-way","Gian van Veen",4,6,67,0,32323,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Gian_van_Veen_vs_Andrew_Gilding/15?event_id=32323","match"),
("Darts","","Tomorrow","2026-10-22","16:45","Ross Smith vs Karel Sedlacek","Win Match 2-way","Ross Smith",4,8,50,0,32329,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Ross_Smith_vs_Karel_Sedlacek/15?event_id=32329","match"),
("Darts","","23 Oct","2026-10-23","14:45","Jonny Clayton vs Niko Springer","Win Match 2-way","Jonny Clayton",4,6,67,0,32335,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Jonny_Clayton_vs_Niko_Springer/15?event_id=32335","match"),
("Darts","","23 Oct","2026-10-23","13:15","Ryan Joyce vs Jermaine Wattimena","Win Match 2-way","Ryan Joyce",2,3,67,1,32332,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Ryan_Joyce_vs_Jermaine_Wattimena/15?event_id=32332","match"),
("Darts","","23 Oct","2026-10-23","13:45","Krzysztof Ratajski vs Dave Chisnall","Win Match 2-way","Krzysztof Ratajski",2,4,50,0,32333,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Krzysztof_Ratajski_vs_Dave_Chisnall/15?event_id=32333","match"),
("Darts","","23 Oct","2026-10-23","14:15","Nathan Aspinall vs Cristo Reyes","Win Match 2-way","Cristo Reyes",2,3,67,1,32327,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Nathan_Aspinall_vs_Cristo_Reyes/15?event_id=32327","match"),
("Darts","","23 Oct","2026-10-23","15:15","Luke Littler vs William OConnor","Handicap 2-way","William OConnor +3.50",2,2,100,1,32328,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Luke_Littler_vs_William_OConnor/15?event_id=32328","match"),
("Darts","","23 Oct","2026-10-23","15:45","Wessel Nijman vs Martin Schindler","Win Match 2-way","Martin Schindler",2,3,67,1,32326,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Wessel_Nijman_vs_Martin_Schindler/15?event_id=32326","match"),
("Darts","","23 Oct","2026-10-23","16:15","Kevin Doets vs Michael van Gerwen","Total Legs","Over 9.50",1,1,100,1,32331,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Kevin_Doets_vs_Michael_van_Gerwen/15?event_id=32331","match"),
("Darts","","23 Oct","2026-10-23","16:45","Josh Rock vs Chris Dobey","Win Match 2-way","Chris Dobey",1,2,50,0,32336,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Josh_Rock_vs_Chris_Dobey/15?event_id=32336","match"),
("Darts","","03 Jan 2027","2027-01-03","12:00","PDC World Championship 2027","Win Tournament","Luke Littler",23,36,64,0,26023,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/PDC_World_Championship_2027/15?event_id=26023","outright"),
("Darts","","25 Oct","2026-10-25","14:00","European Championship","Win Tournament","Luke Littler",2,9,22,1,32338,"https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/European_Championship/15?event_id=32338","outright"),
# ---- HANDBALL (ID 20) — Money Line is 3-way (incl. Tie) ----
("Handball","","Today","2026-10-21","12:45","RK Zagreb vs PSG Handball","Money Line","PSG Handball",8,13,62,0,12053,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/RK_Zagreb_vs_PSG_Handball/20?event_id=12053","match"),
("Handball","","Today","2026-10-21","14:45","Nantes vs HC Vardar","Money Line","Nantes",6,10,60,0,12050,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Nantes_vs_HC_Vardar/20?event_id=12050","match"),
("Handball","","Today","2026-10-21","12:45","Veszprem vs Fuchse Berlin","Money Line","Veszprem",5,11,45,0,12055,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Veszprem_vs_Fuchse_Berlin/20?event_id=12055","match"),
("Handball","","Today","2026-10-21","12:15","Sandefjord vs Runar","Money Line","Runar",4,5,80,0,12115,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Sandefjord_vs_Runar/20?event_id=12115","match"),
("Handball","","Today","2026-10-21","12:45","Dinamo Bucuresti vs Skanderborg Handbold","Money Line","Dinamo Bucuresti",4,11,36,0,12045,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Dinamo_Bucuresti_vs_Skanderborg_Handbold/20?event_id=12045","match"),
("Handball","","Today","2026-10-21","14:45","Aalborg Handbold vs RK Celje","Money Line","Tie",4,5,80,0,12044,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Aalborg_Handbold_vs_RK_Celje/20?event_id=12044","match"),
("Handball","","Today","2026-10-21","12:45","RK Partizan vs FC Porto","Money Line","RK Partizan",3,8,38,0,12052,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/RK_Partizan_vs_FC_Porto/20?event_id=12052","match"),
("Handball","","Today","2026-10-21","14:45","HC Kriens Luzern vs KS Kielce","Money Line","Tie",3,6,50,0,12047,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/HC_Kriens_Luzern_vs_KS_Kielce/20?event_id=12047","match"),
("Handball","","Tomorrow","2026-10-22","14:45","Kolstad vs SC Magdeburg","Money Line","Tie",3,6,50,0,12048,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Kolstad_vs_SC_Magdeburg/20?event_id=12048","match"),
("Handball","","Tomorrow","2026-10-22","14:45","Sporting CP vs IFK Kristianstad","Money Line","Tie",3,7,43,0,12054,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Sporting_CP_vs_IFK_Kristianstad/20?event_id=12054","match"),
("Handball","","Today","2026-10-21","13:00","IF Hallby HK vs IK Savehof","Money Line","IK Savehof",2,3,67,0,12114,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/IF_Hallby_HK_vs_IK_Savehof/20?event_id=12114","match"),
("Handball","","Today","2026-10-21","13:00","Hammarby IF HF vs Alingsas HK","Money Line","Hammarby IF HF",2,3,67,0,12112,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Hammarby_IF_HF_vs_Alingsas_HK/20?event_id=12112","match"),
("Handball","","Today","2026-10-21","14:00","Mors Thy Handbold vs Bjerringbro Silkeborg","Match Handicap","Mors Thy Handbold +3.50",2,2,100,1,12072,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Mors_Thy_Handbold_vs_Bjerringbro_Silkeborg/20?event_id=12072","match"),
("Handball","","Tomorrow","2026-10-22","12:45","MT Melsungen vs Wisla Plock","Money Line","MT Melsungen",2,4,50,0,12049,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/MT_Melsungen_vs_Wisla_Plock/20?event_id=12049","match"),
("Handball","","Tomorrow","2026-10-22","12:45","Pick Szeged vs GOG","Money Line","GOG",2,4,50,0,12051,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Pick_Szeged_vs_GOG/20?event_id=12051","match"),
("Handball","","Tomorrow","2026-10-22","14:45","FC Barcelona vs Montpellier","Money Line","Montpellier",2,6,33,0,12046,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/FC_Barcelona_vs_Montpellier/20?event_id=12046","match"),
("Handball","","23 Oct","2026-10-23","14:00","Estonia W vs Kosovo W","Money Line","Kosovo (W)",2,2,100,0,12110,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Estonia_W_vs_Kosovo_W/20?event_id=12110","match"),
("Handball","","24 Oct","2026-10-24","09:00","Skive FH vs Aalborg Handbold","Money Line","Aalborg Handbold",2,2,100,0,12076,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Skive_FH_vs_Aalborg_Handbold/20?event_id=12076","match"),
("Handball","","Today","2026-10-21","11:15","Belgium W vs Lithuania W","Money Line","Belgium (W)",1,2,50,0,12108,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Belgium_W_vs_Lithuania_W/20?event_id=12108","match"),
("Handball","","Today","2026-10-21","13:00","HK Malmo vs Lugi HF","Money Line","HK Malmo",1,2,50,0,12113,"https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/HK_Malmo_vs_Lugi_HF/20?event_id=12113","match"),
# ---- VOLLEYBALL (ID 21) ----
("Volleyball","","Today","2026-10-21","10:00","Puijo W vs Orpo W","Win Match","Puijo W",3,3,100,0,36981,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Puijo_W_vs_Orpo_W/21?event_id=36981","match"),
("Volleyball","","Today","2026-10-21","11:30","LUK Lublin vs Trefl Gdansk","Win Match","LUK Lublin",3,3,100,1,36961,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/LUK_Lublin_vs_Trefl_Gdansk/21?event_id=36961","match"),
("Volleyball","","Today","2026-10-21","12:00","Schweriner W vs Erfurt W","Win Match","Schweriner W",3,3,100,0,36945,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Schweriner_W_vs_Erfurt_W/21?event_id=36945","match"),
("Volleyball","","23 Oct","2026-10-23","11:30","Slepsk Suwalki vs GKS Katowice","Win Match","Slepsk Suwalki",2,2,100,0,36963,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Slepsk_Suwalki_vs_GKS_Katowice/21?event_id=36963","match"),
("Volleyball","","24 Oct","2026-10-24","12:00","PGE Skra Belchatow vs Projekt Warszawa","Win Match","Projekt Warszawa",2,2,100,0,36964,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/PGE_Skra_Belchatow_vs_Projekt_Warszawa/21?event_id=36964","match"),
("Volleyball","","25 Oct","2026-10-25","13:00","CHKS Chelm vs Resovia Rzeszow","Win Match","Resovia Rzeszow",2,2,100,0,36965,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/CHKS_Chelm_vs_Resovia_Rzeszow/21?event_id=36965","match"),
("Volleyball","","Today","2026-10-21","12:00","Jelcz Laskowice vs Stal Nysa","Win Match","Stal Nysa",1,1,100,0,36979,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Jelcz_Laskowice_vs_Stal_Nysa/21?event_id=36979","match"),
("Volleyball","","Today","2026-10-21","13:00","Netzhoppers KW vs Helios Grizzlys Giesen","Win Match","Helios Grizzlys Giesen",1,1,100,0,36984,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Netzhoppers_KW_vs_Helios_Grizzlys_Giesen/21?event_id=36984","match"),
("Volleyball","","Today","2026-10-21","13:30","WWK Volleys Munchen vs VfB Friedrichshafen","Win Match","VfB Friedrichshafen",1,1,100,0,36985,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/WWK_Volleys_Munchen_vs_VfB_Friedrichshafen/21?event_id=36985","match"),
("Volleyball","","Today","2026-10-21","14:00","SSC Karlsruhe vs SVG Luneburg","Win Match","SVG Luneburg",1,1,100,0,36986,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/SSC_Karlsruhe_vs_SVG_Luneburg/21?event_id=36986","match"),
("Volleyball","","Today","2026-10-21","14:00","VC Sneek W vs VV Utrecht W","Win Match","VC Sneek W",1,1,100,0,36968,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/VC_Sneek_W_vs_VV_Utrecht_W/21?event_id=36968","match"),
("Volleyball","","Today","2026-10-21","14:30","Warta Zawiercie vs Kedzierzyn Kozle","Win Match","Warta Zawiercie",1,1,100,0,36962,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Warta_Zawiercie_vs_Kedzierzyn_Kozle/21?event_id=36962","match"),
("Volleyball","","Today","2026-10-21","14:30","Vallefoglia W vs Cuneo W","Set Score","Cuneo W to win 3-0",1,1,100,0,36977,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Vallefoglia_W_vs_Cuneo_W/21?event_id=36977","match"),
("Volleyball","","Today","2026-10-21","14:30","Bergamo W vs Milano W","Win Match","Milano W",1,1,100,0,36974,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Bergamo_W_vs_Milano_W/21?event_id=36974","match"),
("Volleyball","","Today","2026-10-21","14:30","Novara W vs Marignano W","Win Match","Novara W",1,1,100,0,36976,"https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Novara_W_vs_Marignano_W/21?event_id=36976","match"),
# ---- GAELIC FOOTBALL (ID 25) — market label not shown on sport page; recorded as displayed ----
("Gaelic Football","","25 Oct","2026-10-25","12:00","St Finbarrs v Nemo Rangers","","Nemo Rangers +1.50",10,12,83,0,3530,"https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530","match"),
("Gaelic Football","","24 Oct","2026-10-24","14:00","Moycullen v Salthill-Knocknacarra","","Moycullen -3.50",9,17,53,0,3532,"https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532","match"),
("Gaelic Football","","01 Nov","2026-11-01","09:00","Kanturk v Eire Og Cor","","Kanturk",3,4,75,0,3531,"https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Kanturk_v_Eire_Og_Cor/25?event_id=3531","match"),
("Gaelic Football","","01 Nov","2026-11-01","10:30","Rathgormack v The Nire","","Rathgormack -2.50",1,1,100,0,3536,"https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Rathgormack_v_The_Nire/25?event_id=3536","match"),
("Gaelic Football","","25 Jul 2027","2027-07-25","10:30","All Ireland Football Championship 2027","","Kerry",5,7,71,0,3327,"https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/All_Ireland_Football_Championship_2027/25?event_id=3327","outright"),
# ---- GREYHOUNDS (ID 28) ----
("Greyhounds","","Today","2026-10-21","06:14","11:14 Kinsley","Daily Races","Swift Perry",2,2,100,0,689390,"https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:14_Kinsley/28?event_id=689390","race"),
("Greyhounds","","Today","2026-10-21","05:32","10:32 Harlow","Daily Races","Makeit Sway",1,1,100,0,689384,"https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/10:32_Harlow/28?event_id=689384","race"),
("Greyhounds","","Today","2026-10-21","05:48","10:48 Harlow","Daily Races","Moaning Cashout",1,1,100,0,689385,"https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/10:48_Harlow/28?event_id=689385","race"),
("Greyhounds","","Today","2026-10-21","06:03","11:03 Monmore","Daily Races","Relentless I Am",1,1,100,0,689387,"https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:03_Monmore/28?event_id=689387","race"),
("Greyhounds","","Today","2026-10-21","06:04","11:04 Harlow","Daily Races","Muinteoir Jane",1,1,100,0,689383,"https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:04_Harlow/28?event_id=689383","race"),
("Greyhounds","","Today","2026-10-21","06:09","11:09 Nottingham","Daily Races","Bluejig Polly",1,1,100,0,689386,"https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:09_Nottingham/28?event_id=689386","race"),
]

SPORT_URL = {
 "Tennis":"https://www.olbg.com/betting-tips/Tennis/3","Basketball":"https://www.olbg.com/betting-tips/Basketball/4",
 "Golf":"https://www.olbg.com/betting-tips/Golf/5","Cricket":"https://www.olbg.com/betting-tips/Cricket/7",
 "Snooker":"https://www.olbg.com/betting-tips/Snooker/8","Rugby Union":"https://www.olbg.com/betting-tips/Rugby_Union/9",
 "Rugby League":"https://www.olbg.com/betting-tips/Rugby_League/10","Baseball":"https://www.olbg.com/betting-tips/Baseball/12",
 "Ice Hockey":"https://www.olbg.com/betting-tips/Ice_Hockey/13","Motor Racing":"https://www.olbg.com/betting-tips/Motor_Racing/14",
 "Darts":"https://www.olbg.com/betting-tips/Darts/15","Handball":"https://www.olbg.com/betting-tips/Handball/20",
 "Volleyball":"https://www.olbg.com/betting-tips/Volleyball/21","Gaelic Football":"https://www.olbg.com/betting-tips/Gaelic_Football/25",
 "Greyhounds":"https://www.olbg.com/betting-tips/Greyhounds/28",
}

def opponent(match, sel):
    for sep in (" vs ", " v ", " @ "):
        if sep in match:
            a, b = [x.strip() for x in match.split(sep, 1)]
            for suf in (" One Day Match", " 1st T20 Match", " 3rd T20 Match", " 1st ODI", " T20"):
                if b.endswith(suf): b = b[: -len(suf)].strip()
                if a.endswith(suf): a = a[: -len(suf)].strip()
            base = sel.split(" to win")[0].split(" +")[0].split(" -")[0].strip()
            if base == a: return b
            if base == b: return a
            if base in (a, b): return b if base == a else a
            # selection may abbreviate (e.g. WAS Wizards vs MIL Bucks handled above);
            # fall back to the side that does not contain the selection text
            if base and base not in a and base not in b: return ""
            return b if base in a else a
    return ""

def winner_lean(market, sel, match):
    """Return (winner_pick, basis). Only direct/derived; totals -> none."""
    if market in ("Win Match","Money Line","To Win","Win Match 2-way"):
        return sel, "Leading winner-market selection on OLBG sport page"
    if market in ("Set Betting","Set Score"):
        return sel.split(" to win")[0].strip(), "Derived from leading set-score selection (implies match winner); set-score itself not rated High"
    if market in ("Handicap","Handicap 2-way","Match Handicap","Puck Line"):
        team = sel.rsplit(" ",1)[0].strip()
        return team + " (handicap lean only)", "Handicap selection does not require an outright win; shown as lean, not a winner bet"
    if market == "1st Set Winner":
        return sel + " (1st-set lean only)", "Leading tip is 1st-set market; no match-winner split captured on sport page"
    if market in ("Total Legs","Game Totals"):
        return "", "Leading tip is a totals market (" + sel + "); no winner split captured on sport page — no winner pick made"
    if market == "":
        # Gaelic: infer from selection shape
        if ("+" in sel) or ("-" in sel and sel.split("-")[-1].strip().replace(".","").isdigit()):
            return sel.rsplit(" ",1)[0] + " (handicap lean only)", "OLBG sport page showed no market label; selection carries a points line — treated as handicap lean"
        return sel, "OLBG sport page showed no market label; bare team name treated as winner selection (flagged for review)"
    return sel, "Leading selection on OLBG sport page"

def model(k, n, sport, market, etype):
    if k is None or n is None or n == 0:
        return None, None, None
    if etype in ("outright","race"):
        # multi-runner: tip-share index only, not a win probability
        return None, None, round(100.0*k/n, 1)
    ways = 3 if (sport == "Handball" and market == "Money Line") else 2
    p = (k + 1) / (n + ways)
    return round(p*100, 1), round(1.0/p, 2), round(100.0*k/n, 1)

def confidence(market, k, n, etype):
    if etype != "match" or k is None or n is None or n == 0:
        return "Low"
    if market not in ("Win Match","Money Line","To Win","Win Match 2-way"):
        return "Low"
    share = 100.0*k/n
    if n >= 7 and share >= 80: return "High"
    if (n >= 5 and 60 <= share < 80) or (4 <= n <= 6 and share >= 80): return "Medium"
    return "Low"

rows = []
for i, r in enumerate(RAW, 1):
    sport, comp, dlabel, diso, t, match, market, sel, k, n, pct, exp, eid, url, etype = r
    p_model, fair, share = model(k, n, sport, market, etype)
    conf = confidence(market, k, n, etype)
    wp, basis = winner_lean(market, sel, match) if etype == "match" else (sel, "Most-tipped outright selection (multi-runner field; not a 2-way price)")
    opp = opponent(match, sel) if etype == "match" else ""
    opp_fair = ""
    if p_model is not None and not (sport == "Handball" and market == "Money Line"):
        opp_fair = round(1.0/(1 - p_model/100.0), 2)
    flags = []
    if k is None: flags.append("tip counts not visible in fetch (page truncated)")
    if n == 0: flags.append("0 tips shown at snapshot — no price originated")
    if market == "": flags.append("market label not displayed on OLBG sport page")
    if etype in ("outright","race"): flags.append("multi-runner market — originated figure is a tip-share index, not a full book")
    if sport == "Handball" and sel == "Tie": flags.append("leading selection is the Tie (3-way market) — unusual; verify on event page before use")
    rows.append({
        "id": i, "snapshot_date": SNAP, "sport": sport, "competition": comp,
        "date_display": dlabel, "date_iso": diso, "time_display": t,
        "match": match, "event_type": etype, "leading_market": market,
        "leading_selection": sel, "tips_for": ("" if k is None else k),
        "tips_total": ("" if n is None else n), "tip_share_pct": ("" if share is None else share),
        "experts": exp, "winner_pick": wp, "pick_basis": basis,
        "model_prob_pct": ("" if p_model is None else p_model),
        "originated_fair_decimal": ("" if fair is None else fair),
        "opponent": opp, "opponent_fair_decimal": opp_fair,
        "confidence": conf, "bookmaker_odds": "",
        "olbg_event_url": url, "olbg_sport_url": SPORT_URL[sport],
        "flags": "; ".join(flags),
    })

out = pathlib.Path(__file__).resolve().parent.parent / "data"
out.mkdir(exist_ok=True)
with open(out/"matches.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
with open(out/"matches.json","w",encoding="utf-8") as f:
    json.dump({"snapshot_date": SNAP, "count": len(rows), "rows": rows}, f, indent=1, ensure_ascii=False)

from collections import Counter
print("rows:", len(rows))
print("by sport:", dict(Counter(r["sport"] for r in rows)))
print("by confidence:", dict(Counter(r["confidence"] for r in rows)))
print("HIGH:", [(r["sport"], r["match"], r["winner_pick"], r["tips_for"], r["tips_total"]) for r in rows if r["confidence"]=="High"])
print("MEDIUM count:", sum(1 for r in rows if r["confidence"]=="Medium"))
