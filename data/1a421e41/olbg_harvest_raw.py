# -*- coding: utf-8 -*-
"""
Raw live OLBG.com harvest for session 1a421e41-olbg1.

Every tuple below was transcribed directly from a live fetch of the OLBG sport hub
named in HARVEST_META on 2026-10-22 (UTC) by this session. Nothing is inferred:
the fields are exactly what the hub card rendered.

OLBG hub card fields observed (reverse-engineered, see reports/SESSION_1A421E41.md):
  card title          -> fixture name, links to the event page carrying ?event_id=
  day label           -> "Today" / "Tomorrow" / "<DD> <Mon>" / "<DD> <Mon> <YYYY>"
  clock               -> HH:MM with NO timezone label (GeoIP-localised silently)
  competition chip    -> rendered only on some sports (NBA, Euroleague, MLB, KBL, NBB, SHL, Liiga)
  tipped selection    -> the most-tipped outcome, with its market name
  win tips            -> "n/m Win Tips" = tips for that outcome / total tips in the market
  share               -> integer percentage n/m, or blank when m == 0 (the EW 0/0 bug)
  experts             -> "k experts" chip when k >= 1 tipster meets the expert thresholds
  comments            -> "c comments"

Row schema:
  (event_id, day_label, clock, competition, fixture, tipped_selection, market, win, total, share_pct, experts, comments)
"""

HARVEST_UTC = "2026-10-22T07:24:00Z"
SESSION = "1a421e41-olbg1"

HARVEST_META = {
    "tennis":        {"olbg_id": 3,  "hub": "https://www.olbg.com/betting-tips/Tennis/3"},
    "basketball":    {"olbg_id": 4,  "hub": "https://www.olbg.com/betting-tips/Basketball/4"},
    "golf":          {"olbg_id": 5,  "hub": "https://www.olbg.com/betting-tips/Golf/5"},
    "cricket":       {"olbg_id": 7,  "hub": "https://www.olbg.com/betting-tips/Cricket/7"},
    "snooker":       {"olbg_id": 8,  "hub": "https://www.olbg.com/betting-tips/Snooker/8"},
    "rugby_union":   {"olbg_id": 9,  "hub": "https://www.olbg.com/betting-tips/Rugby_Union/9"},
    "rugby_league":  {"olbg_id": 10, "hub": "https://www.olbg.com/betting-tips/Rugby_League/10"},
    "baseball":      {"olbg_id": 12, "hub": "https://www.olbg.com/betting-tips/Baseball/12"},
    "ice_hockey":    {"olbg_id": 13, "hub": "https://www.olbg.com/betting-tips/Ice_Hockey/13"},
    "motor_racing":  {"olbg_id": 14, "hub": "https://www.olbg.com/betting-tips/Motor_Racing/14"},
    "darts":         {"olbg_id": 15, "hub": "https://www.olbg.com/betting-tips/Darts/15"},
    "handball":      {"olbg_id": 20, "hub": "https://www.olbg.com/betting-tips/Handball/20"},
    "volleyball":    {"olbg_id": 21, "hub": "https://www.olbg.com/betting-tips/Volleyball/21"},
    "aussie_rules":  {"olbg_id": 22, "hub": "https://www.olbg.com/betting-tips/Aussie_Rules/22"},
    "esports":       {"olbg_id": 23, "hub": "https://www.olbg.com/betting-tips/eSports/23"},
    "gaelic_football": {"olbg_id": 25, "hub": "https://www.olbg.com/betting-tips/Gaelic_Football/25"},
    "greyhounds":    {"olbg_id": 28, "hub": "https://www.olbg.com/betting-tips/Greyhounds/28"},
}

OLBG_ROOT = "https://www.olbg.com/betting-tips"

HARVEST = {
# ---------------------------------------------------------------- TENNIS (id 3)
"tennis": [
 (902073, "Today", "07:00", "All Tennis", "Elena Rybakina vs Polina Kudermetova", "Elena Rybakina", "Win Match", 10, 12, 83, 0, 3),
 (902069, "Today", "05:30", "All Tennis", "Daniil Medvedev vs Sho Shimabukuro", "Daniil Medvedev", "Win Match", 8, 9, 89, 0, 3),
 (902110, "Today", "04:00", "All Tennis", "Tomas Machac vs Karen Khachanov", "Karen Khachanov", "Win Match", 4, 6, 67, 0, 2),
 (902072, "Today", "04:00", "All Tennis", "Alexandra Eala vs Diana Shnaider", "Diana Shnaider", "Win Match", 4, 5, 80, 0, 0),
 (902087, "Today", "09:30", "All Tennis", "Pierre Hugues Herbert vs Taylor Fritz", "Taylor Fritz", "Win Match", 4, 6, 67, 0, 2),
 (902104, "Today", "07:30", "All Tennis", "Raphael Collignon vs Jiri Lehecka", "Jiri Lehecka", "Win Match", 3, 5, 60, 0, 2),
 (902103, "Today", "08:00", "All Tennis", "Valentin Vacherot vs Luca Van Assche", "Valentin Vacherot", "Win Match", 3, 3, 100, 0, 1),
 (902082, "Today", "10:30", "All Tennis", "Alexander Bublik vs Fabian Marozsan", "Alexander Bublik", "Win Match", 3, 4, 75, 0, 1),
 (902100, "Today", "08:00", "All Tennis", "Borna Gojo vs Daniel Altmaier", "Borna Gojo", "Win Match", 2, 4, 50, 0, 1),
 (902131, "Today", "09:00", "All Tennis", "David Goffin vs Alex Michelsen", "David Goffin to win 2 - 1", "Set Betting", 1, 1, 100, 0, 0),
 (902120, "Today", "11:00", "All Tennis", "Damir Dzumhur vs Zizou Bergs", "Damir Dzumhur", "Win Match", 1, 1, 100, 0, 0),
 (902126, "Today", "13:00", "All Tennis", "Flavio Cobolli vs Stan Wawrinka", "Stan Wawrinka to win 2 - 1", "Set Betting", 1, 1, 100, 0, 0),
 (902105, "Today", "14:30", "All Tennis", "Kyrian Jacquet vs Brandon Nakashima", "Brandon Nakashima", "Win Match", 1, 1, 100, 0, 0),
 (902107, "Today", "22:30", "All Tennis", "Talia Gibson vs Ashlyn Krueger", "Ashlyn Krueger", "Win Match", 1, 1, 100, 0, 0),
],
# ------------------------------------------------------------ BASKETBALL (id 4)
"basketball": [
 (536021, "Today", "06:00", "Korea KBL", "Mobis Phoebus vs Changwon Sakers", "Mobis Phoebus", "Money Line", 4, 6, 67, 0, 3),
 (535921, "Today", "14:05", "Euroleague", "Maccabi Tel Aviv vs Real Madrid", "Real Madrid", "Money Line", 4, 6, 67, 0, 1),
 (535923, "Today", "14:15", "Euroleague", "Panathinaikos vs Baskonia", "Panathinaikos", "Money Line", 4, 6, 67, 0, 1),
 (534843, "Today", "21:40", "NBA", "DEN Nuggets @ OKC Thunder", "OKC Thunder", "Money Line", 4, 4, 100, 0, 1),
 (535918, "Today", "13:30", "Euroleague", "Anadolu Efes vs Besiktas", "Anadolu Efes", "Money Line", 3, 4, 75, 0, 0),
 (535920, "Today", "14:00", "Euroleague", "Bayern Munich vs BC Dubai", "BC Dubai", "Money Line", 2, 3, 67, 0, 1),
 (535924, "Today", "14:45", "Euroleague", "Partizan vs Crvena Zvezda", "Crvena Zvezda", "Money Line", 2, 2, 100, 0, 0),
 (536019, "Today", "18:30", "Brazil NBB", "Fortaleza BC vs Pinheiros", "Pinheiros", "Money Line", 2, 3, 67, 0, 0),
 (534845, "Today", "19:10", "NBA", "CLE Cavaliers @ PHI 76ers", "PHI 76ers", "Money Line", 2, 2, 100, 0, 1),
 (535928, "Tomorrow", "13:00", "Euroleague", "Zalgiris vs Asvel Lyon Villeurbanne", "Zalgiris", "Money Line", 2, 2, 100, 0, 0),
 (534841, "Tomorrow", "21:40", "NBA", "HOU Rockets @ SA Spurs", "SA Spurs", "Money Line", 2, 2, 100, 0, 0),
 (535922, "Today", "14:30", "Euroleague", "Milano vs Barcelona", "Barcelona", "Money Line", 1, 1, 100, 0, 0),
 (536020, "Today", "18:30", "Brazil NBB", "Uniao Corinthians vs Minas", "Minas", "Money Line", 1, 1, 100, 0, 0),
 (535925, "Tomorrow", "14:15", "Euroleague", "Olympiacos vs Fenerbahce", "Olympiacos", "Money Line", 1, 1, 100, 0, 0),
],
# ------------------------------------------------------------------ GOLF (id 5)
"golf": [
 (101904, "Today", "14:10", "All Golf", "Bermuda Championship", "Seamus Power", "Win Tournament", 6, 24, 25, 0, 7),
 (101903, "25 Oct", "17:45", "All Golf", "Stifel Charity Classic", "Steven Alker", "Win Tournament", 2, 11, 18, 0, 5),
 (101911, "24 Oct", "11:45", "All Golf", "Senior Italian Open", "Hennie Otto", "Win Tournament", 0, 2, None, 0, 0),
],
# --------------------------------------------------------------- CRICKET (id 7)
"cricket": [
 (188829, "Today", "09:00", "All Cricket", "England vs Sri Lanka One Day Match", "England", "Win Match", 14, 17, 82, 1, 10),
 (188828, "Today", "09:00", "All Cricket", "Namibia vs Ireland 1st ODI", "Ireland", "Win Match", 8, 14, 57, 2, 5),
 (188826, "Today", "09:15", "All Cricket", "Australia W vs New Zealand W 3rd T20 Match", "Australia W", "Win Match", 8, 10, 80, 2, 4),
 (188811, "Today", "17:00", "All Cricket", "Eastern Storm vs Tuskers T20", "Eastern Storm", "Win Match", 7, 8, 88, 0, 2),
 (188825, "Today", "12:00", "All Cricket", "Mpumalanga Rhinos vs South Africa Emerging T20", "Mpumalanga Rhinos", "Win Match", 6, 9, 67, 0, 2),
 (188831, "Tomorrow", "12:30", "All Cricket", "Afghanistan vs Zimbabwe One Day Match", "Afghanistan", "Win Match", 1, 1, 100, 0, 1),
 (182606, "21 Nov 2027", "10:00", "All Cricket", "World Cup 2027", "India", "Outright Winner", 6, 12, 50, 0, 0),
 (187184, "05 Dec", "08:10", "All Cricket", "Big Bash Women 2026", "Sydney Sixers W", "Outright Winner", 2, 3, 67, 0, 0),
 (187503, "12 Dec", "08:15", "All Cricket", "T20 Big Bash 2026-27", "Adelaide Strikers", "Outright Winner", 1, 2, 50, 0, 0),
 (187504, "24 Jan 2027", "16:30", "All Cricket", "SA20 2026-27", "Pretoria Capitals", "Outright Winner", 1, 1, 100, 0, 0),
 (188350, "18 Jul 2027", "16:00", "All Cricket", "T20 Blast 2027", "Sussex", "Outright Winner", 0, 0, None, 0, 0),
],
# --------------------------------------------------------------- SNOOKER (id 8)
"snooker": [
 (9942, "Today", "08:00", "All Snooker", "Matthew Selt v Sam Craigie", "Matthew Selt", "Win Match", 6, 8, 75, 0, 2),
 (9940, "Today", "08:00", "All Snooker", "Kyren Wilson v Pang Junxu", "Kyren Wilson", "Win Match", 5, 8, 63, 0, 2),
 (9947, "Today", "09:00", "All Snooker", "Elliot Slessor v Ricky Walden", "Elliot Slessor", "Win Match", 5, 7, 71, 0, 2),
 (9943, "Today", "14:00", "All Snooker", "Mark Williams v Martin O Donnell", "Mark Williams", "Win Match", 3, 3, 100, 0, 1),
 (9944, "Today", "15:00", "All Snooker", "Jordan Brown v Scott Donaldson", "Jordan Brown", "Win Match", 3, 3, 100, 0, 0),
 (9946, "Today", "09:00", "All Snooker", "Anthony McGill v Mateusz Baranowski", "Anthony McGill", "Win Match", 2, 4, 50, 0, 1),
 (9945, "Today", "14:00", "All Snooker", "David Gilbert v Cheung Ka Wai", "Cheung Ka Wai", "Win Match", 2, 3, 67, 0, 0),
 (9941, "Today", "15:00", "All Snooker", "Jak Jones v Daniel Wells", "Daniel Wells", "Win Match", 1, 1, 100, 0, 0),
],
# ----------------------------------------------------------- RUGBY UNION (id 9)
"rugby_union": [
 (609556, "Today", "20:00", "All Rugby Union", "Montauban v Oyonnax", "Oyonnax", "To Win", 13, 19, 68, 0, 9),
 (609560, "Tomorrow", "18:30", "All Rugby Union", "Aurillac v Nevers", "Aurillac", "To Win", 4, 6, 67, 0, 2),
 (609577, "Tomorrow", "19:45", "All Rugby Union", "Connacht v Zebre Parma", "Connacht", "To Win", 4, 6, 67, 0, 2),
 (609557, "Tomorrow", "18:00", "All Rugby Union", "Narbonne v Brive", "Brive", "To Win", 3, 5, 60, 0, 0),
 (609558, "Tomorrow", "18:30", "All Rugby Union", "Agen v Nissa", "Nissa", "To Win", 3, 6, 50, 0, 0),
 (609563, "Tomorrow", "18:30", "All Rugby Union", "Soyaux Angouleme v Dax", "Dax", "To Win", 3, 3, 100, 0, 0),
 (609561, "Tomorrow", "20:00", "All Rugby Union", "Grenoble v Biarritz", "Grenoble", "To Win", 2, 3, 67, 0, 2),
 (609576, "24 Oct", "12:45", "All Rugby Union", "Bulls v Ulster", "Ulster +18.50", "Handicap", 2, 2, 100, 0, 0),
 (609578, "24 Oct", "18:00", "All Rugby Union", "Leinster v Munster", "Leinster", "To Win", 2, 2, 100, 0, 0),
 (609559, "Tomorrow", "18:30", "All Rugby Union", "Valence Romans v Colomiers", "Colomiers", "To Win", 1, 1, 100, 0, 0),
 (609562, "Tomorrow", "20:00", "All Rugby Union", "Provence v Beziers", "Provence", "To Win", 1, 2, 50, 0, 0),
 (609580, "24 Oct", "15:00", "All Rugby Union", "Stormers v Scarlets", "Stormers", "To Win", 1, 2, 50, 0, 0),
 (609567, "24 Oct", "15:35", "All Rugby Union", "Toulouse v Perpignan", "Perpignan +23.50", "Handicap", 1, 1, 100, 0, 0),
 (609564, "24 Oct", "15:35", "All Rugby Union", "Bayonne v Lyon", "Lyon", "To Win", 1, 1, 100, 0, 0),
 (609554, "25 Oct", "20:05", "All Rugby Union", "La Rochelle v Bordeaux", "La Rochelle", "To Win", None, None, None, 0, 0),
],
# -------------------------------------------------------- RUGBY LEAGUE (id 10)
# No match cards rendered at all on 22 Oct 2026 - only three antepost outrights.
"rugby_league": [
 (2695857, "27 May 2027", "06:00", "All Rugby League", "State of Origin 2027", "New South Wales", "Win Tournament", 9, 12, 75, 0, 3),
 (2801554, "02 Oct 2027", "13:00", "All Rugby League", "Super League 2027", "Leeds Rhinos", "Grand Final Winner", 1, 3, 33, 0, 1),
 (2801600, "03 Oct 2027", "04:30", "All Rugby League", "NRL 2027", "Penrith Panthers", "Grand Final Winner", 1, 2, 50, 0, 1),
],
# -------------------------------------------------------------- BASEBALL (id 12)
"baseball": [
 (160789, "Tomorrow", "20:00", "MLB", "TB Rays @ MIL Brewers", "MIL Brewers", "Money Line", 14, 17, 82, 0, 7),
],
# ------------------------------------------------------------ ICE HOCKEY (id 13)
# Zero NHL cards rendered on a regular-season NHL night - see flagged finding F-1A-NHL-01.
"ice_hockey": [
 (199905, "Today", "13:00", "Swedish Hockey League", "Skelleftea AIK vs Djurgardens IF", "Skelleftea AIK", "Money Line", 4, 4, 100, 0, 2),
 (199912, "Today", "11:30", "Finland SM Liiga", "Jyp vs HPK", "Jyp", "Money Line", 3, 3, 100, 0, 0),
 (199901, "Today", "13:00", "Swedish Hockey League", "Timra IK vs Farjestad BK", "Farjestad BK", "Money Line", 2, 3, 67, 2, 2),
 (199900, "Today", "13:00", "Swedish Hockey League", "Orebro HK vs Brynas IF", "Orebro HK", "Money Line", 2, 4, 50, 0, 0),
 (199899, "Today", "13:00", "Swedish Hockey League", "IF Bjorkloven vs IF Malmo Redhawks", "IF Bjorkloven", "Money Line", 2, 2, 100, 0, 0),
 (199906, "Today", "13:00", "Swedish Hockey League", "Rogle BK vs Frolunda HC", "Frolunda HC +1.50", "Puck Line", 1, 1, 100, 0, 0),
 (199902, "Today", "13:00", "Swedish Hockey League", "Vaxjo Lakers HC vs Lulea HF", "Lulea HF +1.50", "Puck Line", 1, 1, 100, 0, 1),
],
# ----------------------------------------------------------------- DARTS (id 15)
"darts": [
 (32325, "Today", "14:45", "All Darts", "Gerwyn Price vs Rob Cross", "Gerwyn Price", "Win Match 2-way", 16, 20, 80, 0, 5),
 (32334, "Today", "14:15", "All Darts", "Niels Zonneveld vs Cameron Menzies", "Niels Zonneveld", "Win Match 2-way", 14, 18, 78, 0, 6),
 (32324, "Today", "13:15", "All Darts", "Luke Woodhouse vs Dirk van Duijvenbode", "Dirk van Duijvenbode", "Win Match 2-way", 13, 16, 81, 1, 5),
 (32337, "Today", "15:45", "All Darts", "Luke Humphries vs Ryan Searle", "Luke Humphries", "Win Match 2-way", 13, 16, 81, 0, 4),
 (32322, "Today", "15:15", "All Darts", "James Wade vs Damon Heta", "James Wade", "Win Match 2-way", 12, 18, 67, 0, 5),
 (32323, "Today", "16:15", "All Darts", "Gian van Veen vs Andrew Gilding", "Gian van Veen", "Win Match 2-way", 11, 16, 69, 0, 3),
 (32330, "Today", "13:45", "All Darts", "Danny Noppert vs Stephen Bunting", "Danny Noppert", "Win Match 2-way", 10, 16, 63, 0, 4),
 (32329, "Today", "16:45", "All Darts", "Ross Smith vs Karel Sedlacek", "Ross Smith", "Win Match 2-way", 9, 15, 60, 0, 3),
 (32332, "Tomorrow", "13:15", "All Darts", "Ryan Joyce vs Jermaine Wattimena", "Ryan Joyce", "Win Match 2-way", 7, 9, 78, 1, 4),
 (32335, "Tomorrow", "14:45", "All Darts", "Jonny Clayton vs Niko Springer", "Jonny Clayton", "Win Match 2-way", 7, 9, 78, 0, 2),
 (32333, "Tomorrow", "13:45", "All Darts", "Krzysztof Ratajski vs Dave Chisnall", "Dave Chisnall", "Win Match 2-way", 4, 7, 57, 1, 2),
 (32326, "Tomorrow", "15:45", "All Darts", "Wessel Nijman vs Martin Schindler", "Wessel Nijman", "Win Match 2-way", 4, 7, 57, 0, 1),
 (32336, "Tomorrow", "16:45", "All Darts", "Josh Rock vs Chris Dobey", "Josh Rock", "Win Match 2-way", 4, 6, 67, 1, 1),
 (32327, "Tomorrow", "14:15", "All Darts", "Nathan Aspinall vs Cristo Reyes", "Nathan Aspinall", "Win Match 2-way", 3, 6, 50, 0, 0),
],
}

# ---------------------------------------------------------- MOTOR RACING (id 14)
HARVEST["motor_racing"] = [
 (913, "25 Oct", "16:00", "All Motor Racing", "USA Grand Prix", "Max Verstappen", "Win Race", 12, 33, 36, 3, 6),
 (828, "06 Dec", "08:00", "All Motor Racing", "Formula 1 Drivers Championship 2026", "Max Verstappen", "Win Tournament", 9, 33, 27, 0, 4),
 (912, "06 Dec", "08:00", "All Motor Racing", "Formula 1 Drivers Championship 2026 Without Kimi Antonelli", "Max Verstappen", "Win Tournament", 4, 7, 57, 0, 1),
]

# -------------------------------------------------------------- HANDBALL (id 20)
HARVEST["handball"] = [
 (12046, "Today", "14:45", "All Handball", "FC Barcelona vs Montpellier", "FC Barcelona", "Money Line", 8, 14, 57, 0, 1),
 (12109, "Today", "12:00", "All Handball", "Bulgaria W vs Italy W", "Italy (W)", "Money Line", 6, 7, 86, 0, 2),
 (12094, "Today", "13:00", "All Handball", "TVB Stuttgart vs SG BBM Bietigheim", "TVB Stuttgart", "Money Line", 6, 9, 67, 0, 2),
 (12054, "Today", "14:45", "All Handball", "Sporting CP vs IFK Kristianstad", "Tie", "Money Line", 6, 13, 46, 0, 0),
 (12048, "Today", "14:45", "All Handball", "Kolstad vs SC Magdeburg", "Tie", "Money Line", 6, 13, 46, 0, 0),
 (12049, "Today", "12:45", "All Handball", "MT Melsungen vs Wisla Plock", "MT Melsungen", "Money Line", 4, 9, 44, 1, 1),
 (12051, "Today", "12:45", "All Handball", "Pick Szeged vs GOG", "GOG", "Money Line", 3, 9, 33, 0, 0),
 (12073, "Today", "13:30", "All Handball", "SonderjyskE vs Nordsjaelland Handbold", "Nordsjaelland Handbold", "Money Line", 3, 7, 43, 0, 0),
 (12074, "Today", "14:00", "All Handball", "KIF Kolding vs Fredericia HK", "Fredericia HK", "Money Line", 3, 6, 50, 0, 1),
 (12100, "Today", "14:00", "All Handball", "BM Granollers vs Ciudad Encantada", "BM Granollers", "Money Line", 3, 6, 50, 0, 0),
 (12110, "Tomorrow", "14:00", "All Handball", "Estonia W vs Kosovo W", "Kosovo (W)", "Money Line", 3, 3, 100, 0, 0),
 (12076, "24 Oct", "09:00", "All Handball", "Skive FH vs Aalborg Handbold", "Aalborg Handbold", "Money Line", 3, 4, 75, 0, 0),
 (12117, "Today", "12:30", "All Handball", "Skanela IF vs HIF Karlskrona", "Tie", "Money Line", 2, 6, 33, 0, 0),
 (12116, "Today", "13:00", "All Handball", "Onnereds HK vs Ystads IF HF", "Onnereds HK", "Money Line", 2, 4, 50, 0, 0),
 (12088, "Tomorrow", "14:00", "All Handball", "Frisch Auf Goppingen vs ThSV Eisenach", "ThSV Eisenach", "Money Line", 2, 3, 67, 0, 0),
]

# ------------------------------------------------------------ VOLLEYBALL (id 21)
HARVEST["volleyball"] = [
 (36988, "Today", "11:30", "All Volleyball", "Radomka Radom W vs Mielec W", "Radomka Radom W", "Win Match", 7, 10, 70, 1, 4),
 (36989, "Today", "12:00", "All Volleyball", "Brno vs Odolena Voda", "Brno", "Win Match", 6, 7, 86, 1, 4),
 (36992, "Today", "12:00", "All Volleyball", "Ostrava vs Kladno", "Ostrava", "Win Match", 4, 7, 57, 0, 2),
 (36990, "Today", "12:00", "All Volleyball", "Ceske Budejovice vs Beskydy", "Ceske Budejovice", "Win Match", 3, 5, 60, 1, 2),
 (36993, "Today", "12:00", "All Volleyball", "Usti Nad Labem vs Zlin", "Zlin", "Win Match", 3, 5, 60, 0, 2),
 (36991, "Today", "12:00", "All Volleyball", "Liberec vs Benatky nad Jizerou", "Liberec to win 3-1", "Set Score", 2, 4, 50, 0, 0),
 (36963, "Tomorrow", "11:30", "All Volleyball", "Slepsk Suwalki vs GKS Katowice", "Slepsk Suwalki", "Win Match", 2, 3, 67, 0, 0),
 (37001, "Tomorrow", "17:30", "All Volleyball", "Brasilia W vs Sesc RJ Flamengo W", "Brasilia W", "Win Match", 2, 2, 100, 0, 0),
 (36964, "24 Oct", "12:00", "All Volleyball", "PGE Skra Belchatow vs Projekt Warszawa", "Projekt Warszawa", "Win Match", 2, 3, 67, 0, 0),
 (36965, "25 Oct", "13:00", "All Volleyball", "CHKS Chelm vs Resovia Rzeszow", "Resovia Rzeszow", "Win Match", 2, 3, 67, 0, 0),
 (37000, "Tomorrow", "17:30", "All Volleyball", "Paulistano-Barueri W vs Minas W", "Paulistano/Barueri W to win 3-1", "Set Score", 1, 1, 100, 0, 0),
 (37002, "24 Oct", "15:00", "All Volleyball", "Mackenzie W vs Osasco W", "Mackenzie W to win 3-1", "Set Score", 1, 1, 100, 0, 0),
 (37003, "24 Oct", "20:00", "All Volleyball", "Abel-Moda Brusque W vs Praia Clube W", "Abel/Moda Brusque W", "Win Match", 1, 1, 100, 0, 0),
 (36994, "25 Oct", "12:00", "All Volleyball", "Trentino vs Cisterna", "Cisterna", "Win Match", 1, 1, 100, 0, 0),
 (36996, "25 Oct", "13:00", "All Volleyball", "Monza vs Verona", "Monza", "Win Match", 1, 1, 100, 0, 0),
]

# ------------------------------------------------------------ AUSSIE RULES (id 22)
# Hub rendered the literal string "No tips found." on 2026-10-22 - zero match cards.
# The SPORTS MENU chip also rendered "All Sports" instead of "Aussie Rules".
# AFLW fixtures therefore come from the official AFL source, not OLBG. See official_feed.py.
HARVEST["aussie_rules"] = []
AUSSIE_RULES_HUB_STATE = {
    "hub": "https://www.olbg.com/betting-tips/Aussie_Rules/22",
    "rendered": "No tips found.",
    "match_cards": 0,
    "sports_menu_chip": "All Sports",
    "page_claim_verbatim": "The **Women's Australian Rules Football** (WAFL) was introduced in just 2017.",
    "note": ("OLBG names the women's national competition 'WAFL'. WAFL is the West Australian Football "
             "League, a men's state competition; the women's national competition launched in 2017 is the "
             "AFLW. Cross-checked against afl.com.au - see finding F-1A-AFL-01."),
}

# --------------------------------------------------------------- ESPORTS (id 23)
# Hub rendered "No tips found." - zero match cards, during the LoL Worlds 2026 knockout window.
HARVEST["esports"] = []
ESPORTS_HUB_STATE = {
    "hub": "https://www.olbg.com/betting-tips/eSports/23",
    "rendered": "No tips found.",
    "match_cards": 0,
    "sports_menu_chip": "All Sports",
    "sub_routes_listed_on_page": [
        "https://www.olbg.com/betting-tips/eSports/All_eSports/CSGO/23",
        "https://www.olbg.com/betting-tips/eSports/All_eSports/DOTA2/23",
        "https://www.olbg.com/betting-tips/eSports/All_eSports/LOL/23",
        "https://www.olbg.com/betting-tips/eSports/All_eSports/Other_eSports/23",
    ],
    "page_claim_verbatim": "There is not a day of the week when there is not some sort of eSports tournament taking place, so our eSports tipsters are certainly kept busy.",
}

# -------------------------------------------------------- GAELIC FOOTBALL (id 25)
# Note: the market-name chip rendered EMPTY on all five club cards (no market label).
HARVEST["gaelic_football"] = [
 (3530, "25 Oct", "12:00", "All Gaelic Football", "St Finbarrs v Nemo Rangers", "Nemo Rangers +1.50", "", 10, 12, 83, 0, 2),
 (3532, "24 Oct", "14:00", "All Gaelic Football", "Moycullen v Salthill-Knocknacarra", "SalthillKnocknacarra +3.50", "", 9, 18, 50, 0, 1),
 (3531, "01 Nov", "09:00", "All Gaelic Football", "Kanturk v Eire Og Cor", "Kanturk", "", 4, 5, 80, 0, 1),
 (3536, "01 Nov", "10:30", "All Gaelic Football", "Rathgormack v The Nire", "Rathgormack -2.50", "", 2, 2, 100, 0, 1),
 (3537, "01 Nov", "10:30", "All Gaelic Football", "Fr Caseys v Kildimo Pallaskenry", "Fr Caseys -3.50", "", 2, 2, 100, 0, 1),
 (3327, "25 Jul 2027", "10:30", "All Gaelic Football", "All Ireland Football Championship 2027", "Kerry", "", 5, 7, 71, 0, 2),
]

# ------------------------------------------------------------ GREYHOUNDS (id 28)
# Card TITLE carries UK local time ("11:14 Kinsley") while the CLOCK on the SAME card reads
# "Today 06:14" - a 5h shift with no timezone label on either. See finding F-1A-CLOCK-01.
HARVEST["greyhounds"] = [
 (689570, "Today", "06:14", "All Greyhounds", "11:14 Kinsley", "Limited Blue", "Daily Races", 1, 1, 100, 0, 0),
 (689576, "Today", "06:36", "All Greyhounds", "11:36 Sheffield", "Drumdoit Pixie", "Daily Races", 1, 1, 100, 0, 0),
 (689581, "Today", "07:03", "All Greyhounds", "12:03 Kinsley", "Ballymac Alyssa", "Daily Races", 1, 1, 100, 0, 0),
 (689584, "Today", "07:14", "All Greyhounds", "12:14 Nottingham", "Ferryforth Mary", "Daily Races", 1, 1, 100, 0, 0),
]

# --------------------------------------------------- CROSS-PAGE CLOCK CONFLICT
# Same event, two OLBG pages, two different clocks, fetched within ~2 minutes, neither labelled.
CLOCK_CONFLICTS = [
 {"event_id": 188829, "fixture": "England vs Sri Lanka One Day Match",
  "page_a": "https://www.olbg.com/betting-tips", "clock_a": "Today 04:00",
  "page_b": "https://www.olbg.com/betting-tips/Cricket/7", "clock_b": "Today 09:00"},
 {"event_id": 689570, "fixture": "11:14 Kinsley",
  "page_a": "card title (UK local)", "clock_a": "11:14",
  "page_b": "https://www.olbg.com/betting-tips/Greyhounds/28 clock chip", "clock_b": "Today 06:14"},
]
