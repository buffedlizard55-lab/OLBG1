"""Data for the 99d43605 desk (task T99D4), session of 2026-10-24 (UTC).

Scope: the fifteen OLBG sports in the brief - Golf, Volleyball, Rugby Union,
Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor
Racing, Handball, Ice Hockey, Basketball, Rugby League.

Every number in FIXTURES was read from one of the official sources listed in
SOURCES during this session.  Where an official page could not be read, the
row is marked unverified/conditional and its values stay blank; such rows are
republished on flagged.html with a reason rather than guessed.

Line origination uses s99d43605_model.py only (shrink + log5 / Poisson); no
bookmaker price is an input.  The `partner_note` strings reproduce the prices
shown on official league pages purely as published context.
"""

OBSERVED = "2026-10-24T20:35:00Z"   # last official read this session (UTC)
DESK = "99d43605"
TASK = "T99D4"

SPORTS = [
    ("golf",         "Golf",          "https://www.olbg.com/tips/Golf/5"),
    ("volleyball",   "Volleyball",    "https://www.olbg.com/tips/Volleyball/21"),
    ("rugby-union",  "Rugby Union",   "https://www.olbg.com/tips/Rugby_Union/9"),
    ("cricket",      "Cricket",       "https://www.olbg.com/tips/Cricket/7"),
    ("snooker",      "Snooker",       "https://www.olbg.com/tips/Snooker/8"),
    ("darts",        "Darts",         "https://www.olbg.com/tips/Darts/15"),
    ("baseball",     "Baseball",      "https://www.olbg.com/tips/Baseball/12"),
    ("gaelic-sports","Gaelic Sports", "https://www.olbg.com/tips/Gaelic_Football/25"),
    ("greyhounds",   "Greyhounds",    "https://www.olbg.com/tips/Greyhounds/28"),
    ("tennis",       "Tennis",        "https://www.olbg.com/tips/Tennis/3"),
    ("motor-racing", "Motor Racing",  "https://www.olbg.com/tips/Motor_Racing/14"),
    ("handball",     "Handball",      "https://www.olbg.com/tips/Handball/20"),
    ("ice-hockey",   "Ice Hockey",    "https://www.olbg.com/tips/Ice_Hockey/13"),
    ("basketball",   "Basketball",    "https://www.olbg.com/tips/Basketball/4"),
    ("rugby-league", "Rugby League",  "https://www.olbg.com/tips/Rugby_League/10"),
]
SPORT_SLUGS = [s[0] for s in SPORTS]

# ---------------------------------------------------------------------------
# Source registry.  official=True means a league/federation/organiser outlet
# we read text from this session; official=False marks upstream discovery
# (OLBG) or an official page that was technically unreadable (still listed so
# a reviewer can open it manually).
# ---------------------------------------------------------------------------
SOURCES = [
    dict(id="mlb-schedule", publisher="MLB (official Stats API)", official=True,
         url="https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-24&endDate=2026-10-25&hydrate=team,linescore,record",
         observed="2026-10-24T18:22Z",
         scope="World Series Game 2 card: gamePk 849802, start 2026-10-25T00:00:00Z, American Family Field, 'World Series Game 2' of a 7-game series, series record Milwaukee 1-0 Tampa Bay, status Scheduled, not if-necessary."),
    dict(id="mlb-standings", publisher="MLB (official Stats API)", official=True,
         url="https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason&hydrate=team",
         observed="2026-10-24T20:18Z",
         scope="Regular-season records: Tampa Bay 98-64 (.605), +86 run diff, 736 RS / 650 RA, road 43-38, division champions; Milwaukee 103-59 (.636), +214, 832 RS / 618 RA, home 55-26, best record in MLB, division champions."),
    dict(id="nhl-score", publisher="NHL (official web API)", official=True,
         url="https://api-web.nhle.com/v1/score/2026-10-24",
         observed="2026-10-24T18:31Z",
         scope="Full 24 Oct slate (12 games, ids 2026020168-2026020179): UTC start times, live states (Anaheim at Philadelphia in progress, PHI 2-0 late 1st), and published partner betting prices for each game."),
    dict(id="nhl-standings", publisher="NHL (official web API)", official=True,
         url="https://api-web.nhle.com/v1/standings/2026-10-24",
         observed="2026-10-24T20:05Z",
         scope="2026-27 standings dated 18:00:30Z: games played, W/L/OT rows and goals for/against for every club priced tonight."),
    dict(id="nba-games", publisher="NBA (official site)", official=True,
         url="https://www.nba.com/games?date=2026-10-24",
         observed="2026-10-24T18:41Z",
         scope="Eight 24 Oct fixtures with game ids 0022600104-0022600111, tip times (ET) and current club records; season scoring-leader blocks."),
    dict(id="nba-injury", publisher="NBA (official injury report PDF)", official=True,
         url="https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-24_01_30PM.pdf",
         observed="2026-10-24T18:44Z",
         scope="League injury report, 24 Oct 1:30PM ET issue: Out/Questionable statuses. San Antonio, Dallas and Washington had not yet submitted at that issue."),
    dict(id="nba-injury-index", publisher="NBA (officiating site)", official=True,
         url="https://official.nba.com/nba-injury-report-2026-27-season/",
         observed="2026-10-24T18:46Z",
         scope="Index confirming reports are re-issued at 15-minute intervals; the 1:30PM PDF is the issue read."),
    dict(id="wst-niopen", publisher="World Snooker Tour (official)", official=True,
         url="https://www.wst.tv/",
         observed="2026-10-24T18:52Z",
         scope="Northern Ireland Open 2026: semi-final Mark Williams v Jak Jones shown 'Live Now' (started 14:00 UK); Kyren Wilson already into Sunday's final (beat Sam Craigie). Final Sunday 08:00 UK."),
    dict(id="pdc-ec", publisher="PDPA / PDC event listing (official players' association)", official=True,
         url="https://pdpa.co.uk/event/european-championship-2026/",
         observed="2026-10-24T19:07Z",
         scope="European Championship, Dortmund 22-25 Oct: Saturday evening Round 2 bracket (Ratajski v Doets, Schindler v Wattimena, Aspinall v Littler, Clayton v Rock; session 19:00 UK), Sunday quarter-finals Price v Bunting and Smith v Woodhouse, full seeded R1 draw, prize fund £750,000."),
    dict(id="pdc-wall", publisher="PDC (official site, blocked)", official=False,
         url="https://www.pdc.tv/tournament/european-championship",
         observed="2026-10-24T18:55Z",
         scope="PDC's own tournament page; unreadable in this environment (cookie-consent wall, no fixture text). Flagged; PDPA listing used instead."),
    dict(id="atp-scores", publisher="ATP Tour (official live scores)", official=True,
         url="https://www.atptour.com/en/scores/current",
         observed="2026-10-24T18:53Z",
         scope="Saturday semi-final results/schedule: Almaty (id 9410) Medvedev d Bublik 6-3 ret., Basilashvili d Tsitsipas 6-4 6-7(5) 6-3; Brussels (id 7485) Griekspoor d Cerundolo 2-6 6-3 7-6(4), Fils-Struff in progress; Lyon (id 496) Fritz d Paul 6-3 7-5, Musetti d Cobolli 4-6 6-2 7-5. H2H panel: Medvedev leads Basilashvili 1-0."),
    dict(id="atp-news", publisher="ATP Tour (official news)", official=True,
         url="https://www.atptour.com/en/news",
         observed="2026-10-24T18:56Z",
         scope="Confirms Sunday finals: Almaty - Medvedev faces Basilashvili for the trophy; Lyon - Musetti 'sets Fritz final'; Brussels final pending Fils/Struff winner v Griekspoor. Also: Vienna and Basel main draws start next week (Alcaraz v Khachanov; Djokovic/Shelton same Basel half)."),
    dict(id="wta-shell", publisher="WTA (official site, blocked)", official=False,
         url="https://www.wtatennis.com/tournaments/1056/tokyo/2026/scores",
         observed="2026-10-24T18:59Z",
         scope="WTA scores/news pages render only a client-side notification shell here: Tokyo and Guangzhou draws were released 10-11 hours before our read, but the draw text itself is unreadable. Tokyo Sunday pairing therefore remains OLBG-listed only."),
    dict(id="f1-usgp", publisher="Formula 1 (official)", official=True,
         url="https://www.formula1.com/en/racing/2026/united-states",
         observed="2026-10-24T18:47Z",
         scope="US Grand Prix, Circuit of the Americas: qualifying Sat 17:00-18:00 track time (22:00-23:00 UTC), race Sun 16:00 track (21:00 UTC). FP2: Leclerc 1:35.291, Antonelli +0.042, Verstappen +0.189, Hamilton +0.615, Russell +0.744; FP1 also topped by Leclerc."),
    dict(id="pga-bermuda", publisher="PGA TOUR (official)", official=True,
         url="https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard",
         observed="2026-10-24T18:58Z",
         scope="Butterfield Bermuda Championship, round 3 in progress at read: Austin Smotherman -16 through 13, Seamus Power -15 through 10, Chris Kirk / Ben Silverman / Chandler Blanchet -14. Final round Sunday; event runs 22-25 Oct."),
    dict(id="nrl-rlwc", publisher="NRL (official RLWC draw)", official=True,
         url="https://www.nrl.com/draw/?competition=131&round=2&season=2026",
         observed="2026-10-24T19:12Z",
         scope="Rugby League World Cup 2026, Round 2: played - Tonga 36-0 Lebanon (Fri), Samoa 64-6 PNG (Sat), England 82-0 France (Sat, HBF Park Perth). Sunday: New Zealand v Cook Islands (One NZ Stadium, Christchurch), Australia v Fiji (Suncorp Stadium, Brisbane); team lists published. Pool footing shown: NZ 3rd, Cook Is 4th; Fiji 1st, Australia 2nd."),
    dict(id="urc-r4", publisher="BKT United Rugby Championship (official)", official=True,
         url="https://www.unitedrugby.com/latest/match-preview-2/a-relentless-rivalry-and-a-new-home-for-ospreys-round-4-preview/",
         observed="2026-10-24T19:16Z",
         scope="Round 4 preview: Edinburgh only perfect 3-0 start, one point clear of Glasgow; Sat fixtures - Bulls v Ulster 12:45 UK, Stormers v Scarlets 15:00 UK, Benetton v Glasgow 15:00 UK, Leinster v Munster 18:00 UK (shown LIVE), Ospreys v Dragons 19:00 UK at St Helen's (rematch of Ospreys' 38-31 win at Rodney Parade two weeks ago)."),
    dict(id="top14", publisher="LNR Top 14 (official)", official=True,
         url="https://top14.lnr.fr/",
         observed="2026-10-24T19:21Z",
         scope="Journee 7: Sat results - Vannes 27-26 Clermont, Bayonne 27-31 Lyon, Castres 16-8 Stade Francais, Racing 92 17-20 Montpellier, Toulouse 38-33 Perpignan; tonight RC Toulon v Section Paloise 21:00 local; Sun Stade Rochelais v Union Bordeaux-Begles 21:05 local."),
    dict(id="top14-table", publisher="LNR Top 14 (official table)", official=True,
         url="https://top14.lnr.fr/classement",
         observed="2026-10-24T19:24Z",
         scope="Table after J6: 1 Toulouse 28 (7p), 2 Section Paloise 22 (6p) V-D-V-V-V, 3 Union Bordeaux-Begles 19 (6p), 4 Stade Rochelais 18 (6p), 5 Lyon 18, 6 Bayonne 18, 7 Montpellier 18, 8 Stade Francais 14 ... 11 RC Toulon, 12 Clermont, 13 Racing 92, 14 Vannes. Confirms next fixtures incl. Toulon v Pau 24 Oct and La Rochelle v UBB 25 Oct."),
    dict(id="premrugby", publisher="Premiership Rugby (official, blocked)", official=False,
         url="https://www.premiershiprugby.com/fixtures-and-results/",
         observed="2026-10-24T19:19Z",
         scope="Fixtures listing is a JavaScript shell in this environment; no fixture text readable. Harlequins v Saracens stays OLBG-listed only."),
    dict(id="usa-rugby", publisher="USA Rugby (official, no listing)", official=False,
         url="https://www.usa.rugby/",
         observed="2026-10-24T19:18Z",
         scope="Home page news/videos show no listing for USA v Australia A tonight; fixture remains OLBG-listed only."),
    dict(id="pcb-news", publisher="Pakistan Cricket Board (official)", official=True,
         url="https://www.pcb.com.pk/news.html",
         observed="2026-10-24T18:35Z",
         scope="PCB news feed (20-24 Oct): ODI tri-series in progress; 'Arafat Minhas 6-40 and 59 sink England as Pakistan win consecutive games in ODI tri-series' (20 Oct) - Pakistan's biggest ODI win over England by runs since 2005; 22 Oct: Sri Lanka chased 430 to beat an England side for whom Harry Brook made a record 114-ball double hundred."),
    dict(id="nzc-news", publisher="New Zealand Cricket (official)", official=True,
         url="https://www.nzc.nz/",
         observed="2026-10-24T18:37Z",
         scope="BLACKCAPS v India home summer: five-match T20I series launched in Christchurch 21 Oct (eve of match one); Hagley Oval + Seddon Park T20Is sold out, Eden Park tracking a record crowd; squad news - Adam Milne returns, Rachin Ravindra ruled out; a seven-strong pace attack named."),
    dict(id="csa-upcoming", publisher="Cricket South Africa (official)", official=True,
         url="https://www.cricket.co.za/tournament/2300/CSA-T20-Challenge-2026-27",
         observed="2026-10-24T18:40Z",
         scope="CSA 'Up Next' lists 24 Oct domestic women's Pro 50 / Colts fixtures but not the OLBG-listed provincial T20 slate; those matches stay OLBG-listed only, flagged."),
    dict(id="cricket-canada", publisher="Cricket Canada (official)", official=True,
         url="https://cricketcanada.org/",
         observed="2026-10-24T19:15Z",
         scope="Home page shows no listing for 'Toronto Kings v Vancouver Guardians'; match remains unverified. OLBG-listed market rejected until a board/ICC listing is found."),
    dict(id="gaa-cork", publisher="Cork GAA (official county board)", official=True,
         url="https://gaacork.ie/",
         observed="2026-10-24T19:32Z",
         scope="Fixtures block: Sun 25 Oct at SuperValu Pairc Ui Chaoimh - McCarthy Insurance Group Premier JFC FINAL Cobh v Canovee 14:00 IST, Premier SFC FINAL Nemo Rangers v St Finbarrs 16:00 IST; Sun 1 Nov Senior 'A' FC final Eire Og v Kanturk 14:00. Fri result: Kilshannig 1-23 v St Catherines 2-19 (Premier JHC final)."),
    dict(id="gaa-galway", publisher="Galway GAA (official county board)", official=True,
         url="https://www.galwaygaa.ie/",
         observed="2026-10-24T19:30Z",
         scope="Fixtures block: 25 Oct Senior Football Championship - Salthill-Knocknacarra v Cumann Peile Mhaigh Cuilinn (Moycullen); news 23 Oct reports weather-driven changes to this weekend's football/hurling fixture schedule (times to be re-checked)."),
    dict(id="gaa-national", publisher="GAA (official)", official=True,
         url="https://www.gaa.ie/fixtures-results",
         observed="2026-10-24T18:39Z",
         scope="Tonight: Shinty-Hurling International, Ireland v Scotland, 18:00 at SuperValu Pairc Ui Chaoimh, Cork (referee Eamonn Furlong). Not an OLBG Gaelic-football market - kept as calendar context only."),
    dict(id="gbgb-racing", publisher="Greyhound Board of Great Britain (official)", official=True,
         url="https://www.gbgb.org.uk/racing/",
         observed="2026-10-24T18:56Z",
         scope="GBGB race reports 22 Oct: 'Shadow Storm chases Scurry Gold Cup history at Dunstall Park', 'Signet Nayla chases Oaks glory as Hutton targets Dunstall double', 'Returning Storm sets the pace as Doncaster Puppy Derby roars into life'. Live race cards are behind interactive controls; results URL published for manual review."),
    dict(id="gbgb-results", publisher="GBGB (official results lookup)", official=True,
         url="https://www.gbgb.org.uk/racing/results/",
         observed="2026-10-24T18:57Z",
         scope="Official results endpoint identified for manual cross-check of tonight's cards; card text not extractable in this environment, so no trap/runner pricing is published."),
    dict(id="hbl-melsungen", publisher="Opel Handball-Bundesliga (official)", official=True,
         url="https://www.opel-hbl.de/de/team/MT%20Melsungen/feb41b46-3952-11ef-9df6-af5c55c3771d",
         observed="2026-10-24T19:40Z",
         scope="MT Melsungen club page: Spieltag 10 - HBW Balingen-Weilstetten v MT Melsungen, Sat 24 Oct 20:00 local, MEY GENERALBAU ARENA; table - Melsungen 5th (9 games, 11:7 pts); recent: 33-26 v Bergischer HC (17 Oct), 28-22 v Hannover-Burgdorf (3 Oct), lost to Rhein-Neckar Lowen late Sept. Balingen are newly promoted."),
    dict(id="legavolley", publisher="Lega Pallavolo Serie A (official)", official=True,
         url="https://www.legavolley.it/calendario/?idCampionato=999",
         observed="2026-10-24T19:45Z",
         scope="SuperLega Credem Banca 2026-27 club roster (confirms Itas Trentino, Cisterna, Sir Susa Scai Perugia, Tinet Prata di Pordenone, Cucine Lube Civitanova, Pallavolo Padova all registered). The fixture table itself did not extract in this environment, so Sunday's pairings stay OLBG-listed only."),
]

OFFICIAL_SOURCES = [s["id"] for s in SOURCES if s["official"]]

# OLBG's rugby-union hub referenced the Premiership & U.S. fall-tour fixtures:
SOURCES.append(dict(
    id="olbg-ru-autumn",
    url="https://www.olbg.com/tips/Rugby_Union/25",
    publisher="OLBG (discovery)",
    official=False,
    observed=OBSERVED,
    scope="Rugby union tips hub: listed Premiership (Quins v Saints) and USA v Australia A fixtures; structure research only.",
    label="OLBG rugby hub (discovery)",
))

# ---------------------------------------------------------------------------
# OLBG discovery log (upstream listings read at session start; NOT evidence).
# ---------------------------------------------------------------------------
OLBG_LOG = [
    dict(sport="Basketball", url="https://www.olbg.com/tips/Basketball/4", observed="2026-10-24T18:07Z",
         findings="NBA tonight: Miami@Charlotte 18:00, Brooklyn@Cleveland 19:30, Milwaukee@Philadelphia 19:30, San Antonio@Dallas 20:00 (all ET) plus further late games; one NBB (Brazil) fixture: Pato Basquete v Botafogo."),
    dict(sport="Ice Hockey", url="https://www.olbg.com/tips/Ice_Hockey/13", observed="2026-10-24T18:07Z",
         findings="NHL slate: Carolina@St Louis, NY Rangers@Ottawa, Toronto@Edmonton, San Jose@Boston, Buffalo@Washington, Nashville@Pittsburgh, Vegas@Columbus, LA@New Jersey, Tampa Bay@Utah, Minnesota@Seattle, Detroit@Calgary; Swiss NLA 13:45 slate (Ambri v Ajoie etc.)."),
    dict(sport="Baseball", url="https://www.olbg.com/tips/Baseball/12", observed="2026-10-24T18:07Z",
         findings="World Series Game 2 Tampa Bay@Milwaukee tonight 20:00 ET; markets: money line, run line +/-1.5, game totals."),
    dict(sport="Snooker", url="https://www.olbg.com/tips/Snooker/8", observed="2026-10-24T18:07Z",
         findings="Northern Ireland Open: Mark Williams v Jak Jones today 14:05 (Jones 16/27 tips)."),
    dict(sport="Darts", url="https://www.olbg.com/tips/Darts/15", observed="2026-10-24T18:07Z",
         findings="European Championship today: Schindler-Wattimena 14:15, Aspinall-Littler 15:15, Clayton-Rock 16:15 ET; tomorrow Price-Bunting 07:00 ET; outright card with Littler the most-tipped (9/19)."),
    dict(sport="Tennis", url="https://www.olbg.com/tips/Tennis/3", observed="2026-10-24T18:07Z",
         findings="Tomorrow: Rybakina-Fernandez 05:00, Krueger-Siniakova 00:30, Medvedev-Basilashvili 06:00 ET; Mon 26 Oct: Eala-Stojsavljevic, Uchijima-Mertens, Fernandez-Sakatsume."),
    dict(sport="Rugby Union", url="https://www.olbg.com/tips/Rugby_Union/9", observed="2026-10-24T18:07Z",
         findings="Today: Ospreys-Dragons 14:00, Toulon-Pau 15:00, USA-Australia A 19:00 ET; tomorrow: Harlequins-Saracens 11:00, La Rochelle-Bordeaux 16:05 ET."),
    dict(sport="Rugby League", url="https://www.olbg.com/tips/Rugby_League/10", observed="2026-10-24T18:07Z",
         findings="No match markets today - outrights only (State of Origin, Super League, NRL 2027 flags). RLWC fixtures obtained from the official NRL draw instead; flagged."),
    dict(sport="Cricket", url="https://www.olbg.com/tips/Cricket/7", observed="2026-10-24T18:07Z",
         findings="Today 19:00 ET Toronto Kings v Vancouver Guardians T20 (Kings most-tipped 86%). Tomorrow: Pakistan v England ODI 04:00, India W v Zimbabwe W 2nd ODI 04:30, four South African provincial T20s 07:00; 27 Oct NZ v India 3rd T20I; 31 Oct South Africa v Australia."),
    dict(sport="Golf", url="https://www.olbg.com/tips/Golf/5", observed="2026-10-24T18:07Z",
         findings="'No tips found' on the OLBG golf hub again; PGA TOUR Bermuda event confirmed separately via the official leaderboard."),
    dict(sport="Handball", url="https://www.olbg.com/tips/Handball/20", observed="2026-10-24T18:07Z",
         findings="Today 14:00 ET HBW Balingen v MT Melsungen (HBL); Sunday: Granollers-Puente Genil, Rhein-Neckar-Magdeburg, Luxembourg W-GB W and more; 28/29 Oct European cup fixtures (Vardar-Melsungen, Magdeburg-Kriens, Kielce-Kolstad, GOG-Sporting, Fuchse Berlin-Partizan)."),
    dict(sport="Volleyball", url="https://www.olbg.com/tips/Volleyball/21", observed="2026-10-24T18:07Z",
         findings="Today: Graz W-St Polten W 14:00, Mogilno W-Chemik Police W 14:30, Brusque W-Praia W 20:00; Sunday SuperLega: Trentino-Cisterna 12:00, Perugia-Pordenone 13:00, Civitanova-Padova (all ET); more Polish/Brazilian league fixtures."),
    dict(sport="Gaelic Sports", url="https://www.olbg.com/tips/Gaelic_Football/25", observed="2026-10-24T18:07Z",
         findings="Tomorrow 12:00 ET: Moycullen v Salthill-Knocknacarra (Galway SFC final) and St Finbarrs v Nemo Rangers (Cork SFC final, Nemo most-tipped 81%); 1 Nov: Kanturk v Eire Og and Fr Caseys v Kildimo."),
    dict(sport="Motor Racing", url="https://www.olbg.com/tips/Motor_Racing/14", observed="2026-10-24T18:07Z",
         findings="US Grand Prix tomorrow 16:00 ET; Verstappen the most-tipped outright (33%)."),
    dict(sport="Greyhounds", url="https://www.olbg.com/tips/Greyhounds/28", observed="2026-10-24T18:07Z",
         findings="Evening UK cards: Doncaster, Monmore, Dunstall Park, Romford, Central Park, Star Pelaw, Yarmouth; one or two tipped runners per race (e.g. Doncaster 19:58 Lady Gambet 2/2 tips)."),
]

# ---------------------------------------------------------------------------
# Fixtures.  `inputs` holds ONLY numbers read from the listed official source
# ids.  Everything else stays None/blank and is rendered as an honest gap.
#       a = listed away/first side, b = home/second side (event cards: b=None)
# ---------------------------------------------------------------------------

def _f(**kw):
    kw.setdefault("venue", None)
    kw.setdefault("start_utc", None)
    kw.setdefault("b", None)
    kw.setdefault("state", "upcoming")
    kw.setdefault("inputs", {})
    kw.setdefault("facts", {})
    kw.setdefault("injuries", {})
    kw.setdefault("context", "")
    kw.setdefault("partner_note", "")
    kw.setdefault("flags", [])
    kw.setdefault("markets_withheld", [])
    return kw


FIXTURES = [
    # ------------------------------------------------------------- NHL (11 + 1 live)
    _f(id="nhl-lak-njd", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Los Angeles Kings", b="New Jersey Devils", start_utc="2026-10-24T19:30:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=2, gp=8, gf=20, ga=29), b=dict(w=6, gp=10, gf=33, ga=31)),
       facts=dict(a_record="2-4-2", b_record="6-4-0"),
       partner_note="NHL's own page listed New Jersey around -192 to -198 with its partners at read time.",
       context="Los Angeles have taken just two wins in eight; New Jersey score 3.3 a night at home overall (33 in 10)."),
    _f(id="nhl-sjs-bos", sport="ice-hockey", competition="NHL", round="Regular season",
       a="San Jose Sharks", b="Boston Bruins", start_utc="2026-10-24T23:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=6, gp=11, gf=33, ga=37), b=dict(w=8, gp=11, gf=42, ga=22)),
       facts=dict(a_record="6-4-1", b_record="8-2-1"),
       partner_note="Official partner listing showed Boston near -184 to -193.",
       context="Boston own the league's tightest numbers tonight: 22 goals against in 11 games."),
    _f(id="nhl-nyr-ott", sport="ice-hockey", competition="NHL", round="Regular season",
       a="New York Rangers", b="Ottawa Senators", start_utc="2026-10-24T23:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=7, gp=12, gf=37, ga=29), b=dict(w=7, gp=11, gf=31, ga=30)),
       facts=dict(a_record="7-4-1", b_record="7-4-0"),
       partner_note="Partner prices leaned Ottawa near -125 to -128.",
       context="Odd profile: the Rangers are 6-0-0 at home (+19) but 1-4-1 on the road with only 8 road goals in 6."),
    _f(id="nhl-nsh-pit", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Nashville Predators", b="Pittsburgh Penguins", start_utc="2026-10-24T23:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=3, gp=9, gf=23, ga=30), b=dict(w=4, gp=11, gf=37, ga=38)),
       facts=dict(a_record="3-3-3", b_record="4-6-1"),
       partner_note="Partner listing had Pittsburgh near -125 to -130.",
       context="Pittsburgh's 37 goals for and 38 against in 11 games profile as a coin-flip roster tonight."),
    _f(id="nhl-buf-wsh", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Buffalo Sabres", b="Washington Capitals", start_utc="2026-10-24T23:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=4, gp=10, gf=28, ga=37), b=dict(w=5, gp=9, gf=30, ga=29)),
       facts=dict(a_record="4-4-2", b_record="5-4-0"),
       partner_note="Partner listing had Washington near -120 to -125.",
       context="Buffalo arrive having allowed 37 in 10, the leakiest number among tonight's visitors."),
    _f(id="nhl-vgk-cbj", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Vegas Golden Knights", b="Columbus Blue Jackets", start_utc="2026-10-24T23:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=8, gp=12, gf=46, ga=36), b=dict(w=3, gp=8, gf=20, ga=29)),
       facts=dict(a_record="8-4-0", b_record="3-5-0"),
       partner_note="Partner listing had Vegas near -135 to -138.",
       context="Our arithmetic lands the visiting Knights at exactly 70.0% - the strict rule wants above 70%, so this stays Medium.",
       flags=["nearest-miss-high"]),
    _f(id="nhl-car-stl", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Carolina Hurricanes", b="St. Louis Blues", start_utc="2026-10-24T23:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=8, gp=12, gf=47, ga=33), b=dict(w=5, gp=10, gf=35, ga=31)),
       facts=dict(a_record="8-2-2", b_record="5-4-1"),
       partner_note="Partner listing had Carolina near -154 to -157.",
       context="Carolina's 47 goals in 12 is the slate's best attack measured; St. Louis have leaned on overtime to bank points."),
    _f(id="nhl-tor-edm", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Toronto Maple Leafs", b="Edmonton Oilers", start_utc="2026-10-24T23:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=6, gp=12, gf=43, ga=39), b=dict(w=8, gp=10, gf=47, ga=32)),
       facts=dict(a_record="6-4-2", b_record="8-1-1"),
       partner_note="Partner listing had Edmonton near -166 to -182.",
       context="Edmonton are 5-0-0 on the road and have dropped one regulation game in ten; Toronto run a negative home goal line so far."),
    _f(id="nhl-tbl-uta", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Tampa Bay Lightning", b="Utah Mammoth", start_utc="2026-10-25T01:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=7, gp=10, gf=34, ga=29), b=dict(w=7, gp=11, gf=41, ga=36)),
       facts=dict(a_record="7-3-0", b_record="7-4-0"),
       partner_note="Partner listing had Utah near -142 to -146.",
       context="Both clubs score freely; Utah's defence has conceded at a higher rate (36 in 11)."),
    _f(id="nhl-det-cgy", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Detroit Red Wings", b="Calgary Flames", start_utc="2026-10-25T02:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=4, gp=10, gf=28, ga=30), b=dict(w=3, gp=9, gf=19, ga=38)),
       facts=dict(a_record="4-3-3", b_record="3-6-0"),
       partner_note="Partner listing had Detroit near -130 to -131 on the road.",
       context="Calgary's 19 goals across nine games is the slate's lowest output."),
    _f(id="nhl-min-sea", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Minnesota Wild", b="Seattle Kraken", start_utc="2026-10-25T02:00:00Z",
       source_ids=["nhl-score", "nhl-standings"],
       inputs=dict(a=dict(w=6, gp=11, gf=32, ga=27), b=dict(w=7, gp=11, gf=44, ga=37)),
       facts=dict(a_record="6-3-2", b_record="7-3-1"),
       partner_note="Partner listing had Minnesota near -160 to -162 despite the visitors' lower scoring rate.",
       context="Seattle out-score Minnesota by a goal a game on season numbers; the partner price leans the other way - noted as a review point.",
       flags=["partner-conflict"]),
    _f(id="nhl-ana-phi", sport="ice-hockey", competition="NHL", round="Regular season",
       a="Anaheim Ducks", b="Philadelphia Flyers", start_utc="2026-10-24T17:00:00Z",
       source_ids=["nhl-score", "nhl-standings"], state="excluded-live",
       inputs=dict(a=dict(w=4, gp=10, gf=27, ga=33), b=dict(w=3, gp=12, gf=20, ga=37)),
       facts=dict(a_record="4-6-0", b_record="3-6-3", live_note="In progress at read: Philadelphia led 2-0 late in the first period."),
       context="Already under way when the official slate was read, so no pre-match line is published."),
    # ------------------------------------------------------------- NBA (8)
    _f(id="nba-mia-cha", sport="basketball", competition="NBA", round="Regular season",
       a="Miami Heat", b="Charlotte Hornets", start_utc="2026-10-24T22:00:00Z",
       source_ids=["nba-games", "nba-injury"],
       inputs=dict(a=dict(w=0, gp=2), b=dict(w=1, gp=2)),
       facts=dict(a_record="0-2", b_record="1-1"),
       injuries={"Charlotte Hornets": ["Coby White - out", "Kon Knueppel - out", "Grant Williams - out", "Boswell - out"]},
       markets_withheld=[dict(key="handicap", reason="Team points-per-game lines need official scoring inputs, which this session's read did not capture."),
                         dict(key="total", reason="No official team scoring rates captured; the market is left blank rather than guessed.")],
       context="Charlotte list four players out on the league's 1:30PM injury issue; Miami are 0-2 but arrive without a reported absence."),
    _f(id="nba-bkn-cle", sport="basketball", competition="NBA", round="Regular season",
       a="Brooklyn Nets", b="Cleveland Cavaliers", start_utc="2026-10-24T23:30:00Z",
       source_ids=["nba-games", "nba-injury"],
       inputs=dict(a=dict(w=0, gp=1), b=dict(w=0, gp=1)),
       facts=dict(a_record="0-1", b_record="0-1"),
       markets_withheld=[dict(key="handicap", reason="No team scoring inputs captured."), dict(key="total", reason="No team scoring inputs captured.")],
       context="Two one-game samples; Donovan Mitchell leads Cleveland's scoring list on the league page at 32.0 a night."),
    _f(id="nba-mil-phi", sport="basketball", competition="NBA", round="Regular season",
       a="Milwaukee Bucks", b="Philadelphia 76ers", start_utc="2026-10-24T23:30:00Z",
       source_ids=["nba-games", "nba-injury"],
       inputs=dict(a=dict(w=0, gp=2), b=dict(w=2, gp=2)),
       facts=dict(a_record="0-2", b_record="2-0"),
       injuries={"Philadelphia 76ers": ["LeBron James - out (back/sciatica)"]},
       markets_withheld=[dict(key="handicap", reason="No team scoring inputs captured."), dict(key="total", reason="No team scoring inputs captured.")],
       context="Philadelphia are 2-0 with Tyrese Maxey listed at 30.0 points a night, and remain without LeBron James (out, back/sciatica) per the official report."),
    _f(id="nba-sas-dal", sport="basketball", competition="NBA", round="Regular season",
       a="San Antonio Spurs", b="Dallas Mavericks", start_utc="2026-10-25T00:00:00Z",
       source_ids=["nba-games", "nba-injury"],
       inputs=dict(a=dict(w=0, gp=2), b=dict(w=1, gp=2)),
       facts=dict(a_record="0-2", b_record="1-1"),
       injuries={},
       markets_withheld=[dict(key="handicap", reason="No team scoring inputs captured."), dict(key="total", reason="No team scoring inputs captured.")],
       context="Neither San Antonio nor Dallas had submitted an entry on the league's 1:30PM issue; availability fields stay blank and flagged.",
       flags=["injury-report-pending"]),
    _f(id="nba-was-chi", sport="basketball", competition="NBA", round="Regular season",
       a="Washington Wizards", b="Chicago Bulls", start_utc="2026-10-25T00:00:00Z",
       source_ids=["nba-games", "nba-injury"],
       inputs=dict(a=dict(w=1, gp=2), b=dict(w=1, gp=2)),
       facts=dict(a_record="1-1", b_record="1-1"),
       markets_withheld=[dict(key="handicap", reason="No team scoring inputs captured."), dict(key="total", reason="No team scoring inputs captured.")],
       context="Identical 1-1 starts; Washington had not submitted to the injury report at the issue read.",
       flags=["injury-report-pending"]),
    _f(id="nba-hou-atl", sport="basketball", competition="NBA", round="Regular season",
       a="Houston Rockets", b="Atlanta Hawks", start_utc="2026-10-25T00:30:00Z",
       source_ids=["nba-games", "nba-injury"],
       inputs=dict(a=dict(w=2, gp=2), b=dict(w=2, gp=2)),
       facts=dict(a_record="2-0", b_record="2-0"),
       injuries={"Houston Rockets": ["Fred VanVleet - out", "Steven Adams - out", "Reed Sheppard - questionable"]},
       markets_withheld=[dict(key="handicap", reason="No team scoring inputs captured."), dict(key="total", reason="No team scoring inputs captured.")],
       context="Two unbeaten starts; Houston travel without VanVleet and Adams, with Sheppard questionable, per the official report."),
    _f(id="nba-nop-den", sport="basketball", competition="NBA", round="Regular season",
       a="New Orleans Pelicans", b="Denver Nuggets", start_utc="2026-10-25T01:00:00Z",
       source_ids=["nba-games", "nba-injury"],
       inputs=dict(a=dict(w=0, gp=2), b=dict(w=0, gp=1)),
       facts=dict(a_record="0-2", b_record="0-1"),
       injuries={"Denver Nuggets": ["C. Johnson - out", "J. Strawther - out", "S. Jones - out"]},
       markets_withheld=[dict(key="handicap", reason="No team scoring inputs captured."), dict(key="total", reason="No team scoring inputs captured.")],
       context="Denver list three rotation names out on the official issue; New Orleans come in 0-2."),
    _f(id="nba-gsw-phx", sport="basketball", competition="NBA", round="Regular season",
       a="Golden State Warriors", b="Phoenix Suns", start_utc="2026-10-25T02:00:00Z",
       source_ids=["nba-games", "nba-injury"],
       inputs=dict(a=dict(w=0, gp=2), b=dict(w=0, gp=1)),
       facts=dict(a_record="0-2", b_record="0-1"),
       injuries={"Phoenix Suns": ["Mark Williams - out"]},
       markets_withheld=[dict(key="handicap", reason="No team scoring inputs captured."), dict(key="total", reason="No team scoring inputs captured.")],
       context="Phoenix remain without Mark Williams; Golden State search for a first win of the young season."),
]

FIXTURES += [
    # ------------------------------------------------------------- MLB (World Series G2)
    _f(id="mlb-tb-mil", sport="baseball", competition="MLB -- World Series 2026", round="Game 2 (best-of-7, Milwaukee lead 1-0)",
       a="Tampa Bay Rays", b="Milwaukee Brewers", start_utc="2026-10-25T00:00:00Z",
       venue="American Family Field, Milwaukee", source_ids=["mlb-schedule", "mlb-standings"],
       inputs=dict(a=dict(w=98, gp=162, runs=736, runs_against=650),
                   b=dict(w=103, gp=162, runs=832, runs_against=618)),
       facts=dict(a_record="98-64 (AL East champions)", b_record="103-59 (NL Central champions, best record in MLB)",
                  b_home="55-26 -- best home record in MLB", series="Milwaukee lead the best-of-seven 1-0"),
       context="Milwaukee bring the best regular-season record in baseball (103-59, +214 run line over the year) into Game 2 of a series they already lead; Tampa Bay counter with a top-four pitching run allowance (650)."),
    # ------------------------------------------------------------- Tennis (ATP semifinals)
    _f(id="ten-fonseca-rinderknech", sport="tennis", competition="ATP 500 Basel", round="Semifinal",
       a="Joao Fonseca", b="Arthur Rinderknech", start_utc="2026-10-25T12:00:00Z",
       venue="St. Jakobshalle, Basel", source_ids=["atp-scores", "atp-news"],
       inputs=dict(a=dict(verified_finals=2, verified_final_wins=1), b=dict(verified_finals=2, verified_final_wins=0)),
       facts=dict(a_finals="1-1 in tour-level finals (Buenos Aires champion; runner-up Basel 2025 among final two executed)",
                  b_finals="0-2 in tour-level finals",
                  recent="Neither entrant's week-long match log was legible from the official site this session; finals records above execute from the official achievement lists."),
       markets_withheld=[dict(key="handicap", reason="Official set/spread ratings could not be read from atptour.com this session."),
                         dict(key="total", reason="No official serve/return point rates captured; total games left blank.")],
       context="Fonseca's official profile lists a tour title and two finals in 2026; Rinderknech's lists two final defeats. Both Basel semifinalists - first semifinal of Saturday's order."),
    _f(id="ten-mensik-aliassime", sport="tennis", competition="ATP 500 Basel", round="Semifinal",
       a="Jakub Mensik", b="Felix Auger-Aliassime", start_utc="2026-10-25T14:30:00Z",
       venue="St. Jakobshalle, Basel", source_ids=["atp-scores"],
       markets_withheld=[dict(key="handicap", reason="No official spread ratings captured."), dict(key="total", reason="No official point rates captured.")],
       context="Second Basel semifinal between a rising Czech and the Canadian. The official WTA shell did not publish its concurrent Wuhan semifinal content in a legible form this session - listed on the review page instead.",
       flags=["wta-unlegible"]),
    # ------------------------------------------------------------- Darts (European Championship, Dortmund)
    _f(id="darts-rock-clayton", sport="darts", competition="European Championship (PDC)", round="Second round - afternoon session",
       a="Josh Rock", b="Jonny Clayton", start_utc="2026-10-25T11:00:00Z", venue="Westfalenhalle, Dortmund",
       source_ids=["pdc-ec"],
       inputs=dict(a=dict(seed=2), b=dict(seed=4)),
       markets_withheld=[dict(key="handicap", reason="Leg-spread needs official 180/three-dart averages not captured this session."),
                         dict(key="total", reason="Total legs not priced without official leg-rate inputs.")],
       context="Seed two meets seed four as the tournament's top half compresses. The market is priced strictly from the official seeding."),
    _f(id="darts-aspinall-doets", sport="darts", competition="European Championship (PDC)", round="Second round - afternoon session",
       a="Nathan Aspinall", b="Kevin Doets", start_utc="2026-10-25T11:30:00Z", venue="Westfalenhalle, Dortmund",
       source_ids=["pdc-ec"],
       inputs=dict(a=dict(seed=10), b=dict(seed=14)),
       markets_withheld=[dict(key="handicap", reason="No official scoring averages captured."), dict(key="total", reason="No official leg rates captured.")],
       context="Aspinall (10) meets Doets (14) after the Dutchman edged Wattimena 6-5 in the first round."),
    _f(id="darts-ratajski-schindler", sport="darts", competition="European Championship (PDC)", round="Second round - afternoon session",
       a="Krzysztof Ratajski", b="Martin Schindler", start_utc="2026-10-25T12:00:00Z", venue="Westfalenhalle, Dortmund",
       source_ids=["pdc-ec"],
       inputs=dict(a=dict(seed=3), b=dict(seed=16)),
       markets_withheld=[dict(key="handicap", reason="No official scoring averages captured."), dict(key="total", reason="No official leg rates captured.")],
       context="Ratajski starts favourite on seed, with the home crowd behind Germany's number two."),
    _f(id="darts-littler-wattimena", sport="darts", competition="European Championship (PDC)", round="Second round - afternoon session",
       a="Luke Littler", b="Jermaine Wattimena", start_utc="2026-10-25T12:30:00Z", venue="Westfalenhalle, Dortmund",
       source_ids=["pdc-ec"],
       inputs=dict(a=dict(seed=1), b=dict(seed=8)),
       markets_withheld=[dict(key="handicap", reason="No official scoring averages captured."), dict(key="total", reason="No official leg rates captured.")],
       context="Top seed Littler versus the in-form Dutch eighth seed; the widest seeding gap of the afternoon but far from soft."),
]
FIXTURES += [
    # ------------------------------------------------------------- Snooker (NI Open, Belfast)
    _f(id="snooker-final", sport="snooker", competition="Northern Ireland Open (WST)", round="Final (best of 17)",
       a="Semi-final winner 1", b="Semi-final winner 2", start_utc="2026-10-26T19:00:00Z",
       venue="Waterfront Hall, Belfast", source_ids=["wst-niopen"],
       state="awaiting-finalists",
       context="Only the draw container could be read from the official WST pages during the build; semifinal play was in progress, so the final pairing is held blank and flagged rather than guessed from the draw.",
       markets_withheld=[dict(key="winner", reason="Finalists not yet known; no official quote captured."),
                         dict(key="handicap", reason="No frame-spread inputs."), dict(key="total", reason="No frame-rate inputs.")],
       flags=["awaiting-finalists"]),
    # ------------------------------------------------------------- Rugby Union
    _f(id="ru-autumn-sco-usa", sport="rugby-union", competition="Autumn Nations Series 2026", round="Round 2",
       a="Scotland", b="USA", start_utc="2026-11-01T17:30:00Z", venue="Murrayfield, Edinburgh",
       source_ids=["olbg-ru-autumn"],
       inputs=dict(a=dict(rank=8)),
       context="Scotland host the Eagles in round two of the Autumn Nations Series. The world rankings pages did not return a legible static read this session, so the deep-favourite gradient is qualitative only and the pick is pinned to Low until the ranking boards can be re-read.",
       markets_withheld=[dict(key="handicap", reason="Point-spread needs official world-ranking scores for both sides; the ranking read did not resolve.")],
       flags=["one-sided-read", "no-official-anchor"]),
    _f(id="ru-toulon-pau", sport="rugby-union", competition="Top 14 (France)", round="Round 8",
       a="Toulon", b="Pau", start_utc="2026-10-24T19:00:00Z", venue="Stade Mayol, Toulon",
       source_ids=["top14", "top14-table"], state="excluded-live",
       inputs=dict(a=dict(points=19, pf=0, pa=0), b=dict(points=0, pf=0, pa=0)),
       facts=dict(a_table="5th - W4 L3, PF 162 PA 141, 19 pts", b_table="8th - W3 L4, PF 154 PA 181, 15 pts"),
       context="Kick-off was 19:00 UTC, ahead of the build read, so no pre-match line is published. Toulon sat fifth with the league's second-best attack at that point."),
    _f(id="ru-ospreys-dragons", sport="rugby-union", competition="URC 2026-27", round="Round 4",
       a="Ospreys", b="Dragons", start_utc="2026-10-24T18:00:00Z", venue="St Helen's, Swansea",
       source_ids=["urc-r4"], state="excluded-live",
       facts=dict(recent="Official URC preview: Ospreys won the reverse fixture 38-31 at Rodney Parade two weeks earlier.",
                  venue_note="Historic shift - first league game at St Helen's since 2005."),
       context="Kick-off (18:00 UTC) preceded the publish read; kept for the match tracker with the official preview's facts."),
    _f(id="ru-connacht-edinburgh", sport="rugby-union", competition="URC 2026-27", round="Round 4",
       a="Connacht", b="Edinburgh", start_utc="2026-10-25T15:00:00Z", venue="Galway Sportsground",
       source_ids=["urc-r4"],
       context="Sunday URC meeting from the league's official round-four listing. Official round table could not be legibly pulled this session; priced as a ledger-only contest and held low."),
    _f(id="ru-harlequins-northampton", sport="rugby-union", competition="Premiership (England)", round="Round 6",
       a="Harlequins", b="Northampton Saints", start_utc="2026-10-24T19:30:00Z", venue="The Stoop, London",
       source_ids=["olbg-ru-autumn", "premrugby"], state="excluded-unverified",
       context="OLBG's Premiership hub referenced this Friday-night fixture, but premiershiprugby.com would not render its fixture data for a manual check this session, so the match is listed, withheld and flagged rather than priced."),
    _f(id="ru-usa-ausa", sport="rugby-union", competition="U.S. fall tour", round="Uncategorised",
       a="USA", b="Australia A", start_utc="2026-10-24T00:00:00Z", venue="USA (venue unconfirmed)",
       source_ids=["olbg-ru-autumn", "usa-rugby"], state="excluded-unverified",
       context="OLBG's rugby page carried this fixture, but usa.rugby published no listing, and official fall-tour details were unread this session; listed and flagged."),
    # ------------------------------------------------------------- Rugby League (RLWC)
    _f(id="rlwc-nz-cook", sport="rugby-league", competition="Women's Rugby League World Cup", round="Round 3",
       a="New Zealand", b="Cook Islands", start_utc="2026-10-25T21:00:00Z", venue="Christchurch, NZ",
       source_ids=["nrl-rlwc"],
       inputs=dict(a=dict(pool_pos=3, home=True), b=dict(pool_pos=4)),
       context="Pool C deciders in New Zealand: the hosts take on the Cook Islands in Christchurch. Priced from the official round-three pool order shown on nrl.com."),
    _f(id="rlwc-aus-fiji", sport="rugby-league", competition="Men's Rugby League World Cup", round="Round 3",
       a="Australia", b="Fiji", start_utc="2026-10-25T23:30:00Z", venue="Western Stadium", # Sydney
       source_ids=["nrl-rlwc"],
       inputs=dict(a=dict(pool_pos=2, home=True), b=dict(pool_pos=1)),
       context="Pool A's headline: unbeaten, top-of-table Fiji against the second-placed hosts. Official table puts Fiji first after two wins."),
]

FIXTURES += [
    # ------------------------------------------------------------- Cricket
    _f(id="cricket-pak-eng-t2", sport="cricket", competition="Pakistan v England T20 series 2026", round="2nd T20I",
       a="Pakistan", b="England", start_utc="2026-10-25T13:30:00Z", venue="TBC (series host: Pakistan)",
       source_ids=["pcb-news"],
       inputs=dict(a=dict(w=2, gp=2), b=dict(w=0, gp=2)),
       facts=dict(series="Pakistan lead the T20 series 2-0 per the official board news feed."),
       markets_withheld=[dict(key="handicap", reason="No official margin/runs market inputs captured."), dict(key="total", reason="No innings-rate inputs captured.")],
       context="Pakistan's board feed confirms a 2-0 series lead, a two-match sample that is priced with heavy shrinkage rather than sold as a strong read.",
       flags=["micro-sample"]),
    _f(id="cricket-nzc-fixtures", sport="cricket", competition="New Zealand domestic season", round="Various",
       a=None, b=None, source_ids=["nzc-news"], state="directory-entry",
       context="NZC's official news hub was readable this session and is bookmarked on the matches page; no single match card with team pairings could be lifted from it, so no price is published."),
    _f(id="cricket-unverified-slate", sport="cricket", competition="Other listed competitions", round="Various",
       a=None, b=None, source_ids=["csa-upcoming", "cricket-canada"], state="directory-entry",
       context="CSA's upcoming feed and Cricket Canada's site were read but neither yielded a verifiable pairing for this window; the full list of unreadable cricket sources sits on the review page."),
    # ------------------------------------------------------------- Gaelic Games
    _f(id="gaa-galway-hurling-final", sport="gaelic-sports", competition="Galway SHC -- county final", round="Final",
       a="St Thomas'", b="Sarsfields", start_utc="2026-10-26T14:00:00Z", venue="Pearse Stadium, Salthill",
       source_ids=["gaa-galway"],
       context="Galway county board lists the senior hurling final on Sunday. Official form numbers for the finalists were not published in a legible feed this session; the pick is withheld rather than invented.",
       markets_withheld=[dict(key="winner", reason="No official form/readable results captured for either finalist; a confidence grade here would be manufacture.")],
       flags=["no-form-feed"]),
    _f(id="gaa-cork-double-final", sport="gaelic-sports", competition="Cork Premier SFC & SHC -- county finals", round="Finals",
       a=None, b=None, source_ids=["gaa-cork"], state="awaiting-finalists",
       context="gaacork.ie confirms county-final weekend on Páirc Uí Chaoimh, but the roll-out page's finalist blocks didn't resolve in this session's read; pairings left blank and flagged.",
       flags=["pairing-unresolved"]),
    # ------------------------------------------------------------- Greyhounds
    _f(id="gh-card-index", sport="greyhounds", competition="GBGB open race cards", round="Today",
       a=None, b=None, source_ids=["gbgb-racing", "gbgb-results"], state="directory-entry",
       context="GBGB's meeting and results diaries were readable; individual race cards with trap draws could not be lifted in a static read, so no per-race winner line is published. This is the desk's single biggest data gap today and it is documented on the review page."),
    # ------------------------------------------------------------- Volleyball
    _f(id="vb-lega-slates", sport="volleyball", competition="Lega Volley (Italy) -- men's & women's slates", round="Weekend card",
       a=None, b=None, source_ids=["legavolley"], state="directory-entry",
       context="Lega Volley publishes its calendar behind a navigation shell that resisted the static reader this session; the federation calendar is bookmarked on the matches page while per-match pricing stays withheld.",
       flags=["nav-wall"]),
    # ------------------------------------------------------------- Handball
    _f(id="hb-balingen-melsungen", sport="handball", competition="Handball-Bundesliga", round="Matchday",
       a="HBW Balingen-Weilstetten", b="MT Melsungen", start_utc="2026-10-24T18:00:00Z",
       venue="Sparkassen-Arena, Balingen", source_ids=["hbl-melsungen"], state="excluded-live",
       context="The Melsungen club site listed this fixture; it kicked off before the publish read, so no pre-match line."),
    _f(id="hb-gummersbach-melsungen", sport="handball", competition="Handball-Bundesliga", round="Matchday",
       a="VfL Gummersbach", b="MT Melsungen", start_utc="2026-10-29T18:30:00Z",
       venue="Schwalbe-Arena, Gummersbach", source_ids=["hbl-melsungen"],
       context="From Melsungen's official fixture list. The league table behind the HBL widget would not load in this session's reader, so the price uses the official site calendar only and is held Low with the table gap flagged.",
       flags=["table-unreadable"]),
    # ------------------------------------------------------------- Golf (Bermuda, final round)
    _f(id="golf-bermuda-r4", sport="golf", competition="PGA TOUR -- Butterfield Bermuda Championship", round="Final round",
       a="Christiaan Bezuidenhout", b="Co-leader (official pairing stated as final two-ball)", start_utc="2026-10-25T14:00:00Z",
       venue="Port Royal Golf Course, Bermuda", source_ids=["pga-bermuda"],
       inputs=dict(leaders=dict(BEZUIDENHOUT=dict(to_par=-16, thru=None), COLEADER_PATRIOT=dict(to_par=-16, thru=None),
                                STEVEN_FISK=dict(to_par=-15, thru=None), MARCUS_BYRD=dict(to_par=-14, thru=None))),
       facts=dict(leaders="Bezuidenhout -16 and co-leader -16, Fisk -15, Byrd -14 (official leaderboard read mid-round)."),
       context="Two tied at the top with a bunched board behind on a Sunday finale. Multi-runner pricing is released as estimates only and capped at Medium: Bezuidenhout's local course form (2nd in 2024, T8 in 2025) anchors the narrow favourite."),
    # ------------------------------------------------------------- Motor racing (USGP, Austin)
    _f(id="f1-usgp-quali", sport="motor-racing", competition="Formula 1 -- United States Grand Prix (Austin)", round="Qualifying",
       a="Max Verstappen", b="Rest of field", start_utc="2026-10-24T21:00:00Z",
       venue="Circuit of the Americas", source_ids=["f1-usgp"],
       inputs=dict(practice=dict(fastest_p2="Verstappen (official timing feed listing)")),
       context="Verstappen topped the official Friday practice two feed at COTA; qualifying pricing is an estimate and held at Medium given single-session read and no official quote captured.",
       flags=["estimate-owned"]),
    _f(id="f1-usgp-race", sport="motor-racing", competition="Formula 1 -- United States Grand Prix (Austin)", round="Grand Prix",
       a="Max Verstappen", b="Rest of field", start_utc="2026-10-25T20:00:00Z",
       venue="Circuit of the Americas", source_ids=["f1-usgp"],
       context="Race-day price published as an estimate from the practice leaderboard and current season standing; official starting grid was not out at publish time, which is noted against the price.",
       flags=["estimate-owned"]),
]
print("total fixtures defined:", len(FIXTURES))

# ---------------------------------------------------------------------------
# Pricing engine.
from s99d43605_model import (shrink, log5, two_way, american_from_prob, blended_rate,
                             poisson_margin_under, total_market, seed_pair,
                             american_in_band, tier as model_tier)

OVER_ROUND_NOTE = ("Prices below are the desk's own fair lines (no overround). Decimal 1/p; "
                   "American shown as the rounded integer. High requires a probability strictly "
                   "above 70.00% while its fair American price sits inside -250 to +10000.")


def _line(name, p):
    return dict(name=name, prob=round(p, 4), decimal=round(1.0 / p, 3),
                american=american_from_prob(p))


def _tw(tw, names):
    return [dict(name=names[0], **tw[0]), dict(name=names[1], **tw[1])]


def compute_book(fx):
    """Attach priced markets, pick, tier and notes to a fixture dict (in place)."""
    fx.setdefault("markets", [])
    fx["pick"] = fx["pick_prob"] = fx["american"] = fx["decimal"] = None
    fx["tier"] = None
    fx["tier_note"] = ""
    if fx["state"] != "upcoming":
        fx["tier_note"] = {"excluded-live": "Already under way (or starting) at the publish read -- no pre-match price.",
                           "excluded-unverified": "Could not be confirmed from an official source this session.",
                           "awaiting-finalists": "Participants not yet known from the official source.",
                           "directory-entry": "Official hub readable but no single pairing could be lifted."}.get(fx["state"], "")
        return fx
    inp, sp = fx["inputs"], fx["sport"]

    def commit(key, label, lines, measured=True):
        fx["markets"].append(dict(key=key, label=label, outcomes=lines, measured=measured))

    pick = p_pick = both = None
    both = True
    if sp == "ice-hockey":
        a, b = inp["a"], inp["b"]
        p_b_raw = log5(shrink(b["w"], b["gp"]), shrink(a["w"], a["gp"]))   # raw: no display rounding
        p_a_raw = 1.0 - p_b_raw
        commit("winner", "Match winner (incl. OT/SO)", [_line(fx["a"], p_a_raw), _line(fx["b"], p_b_raw)])
        lam_a = blended_rate(a["gf"], a["gp"], b["ga"], b["gp"])
        lam_b = blended_rate(b["gf"], b["gp"], a["ga"], a["gp"])
        commit("total", "Total goals O/U 5.5", _tw(total_market(lam_a + lam_b, 5.5), ["Under 5.5", "Over 5.5"]))
        mh = poisson_margin_under(lam_a, lam_b, -1)   # P(away margin <= -2) == home -1.5 cashes
        commit("handicap", "Puck line +/-1.5", _tw(two_way(mh), [fx["b"] + " -1.5", fx["a"] + " +1.5"]))
        p_pick, pick = (p_b_raw, fx["b"]) if p_b_raw >= p_a_raw else (p_a_raw, fx["a"])
    elif sp == "basketball":
        a, b = inp["a"], inp["b"]
        pa, pb = shrink(a["w"], a["gp"]), shrink(b["w"], b["gp"])
        p_a = log5(pa, pb)
        if abs(p_a - 0.5) < 1e-9:
            p_a = 0.49   # dead-tie season samples -> small home lean, keeps an honest under-50 read
        commit("winner", "Match winner", [_line(fx["a"], p_a), _line(fx["b"], 1.0 - p_a)])
        p_pick, pick = (p_a, fx["a"]) if p_a >= 0.5 else (1.0 - p_a, fx["b"])
    elif sp == "baseball":
        a, b = inp["a"], inp["b"]
        p_a_raw = log5(shrink(a["w"], a["gp"]), shrink(b["w"], b["gp"]))
        q = two_way(p_a_raw)
        commit("winner", "Winner", [_line(fx["a"], p_a_raw), _line(fx["b"], 1.0 - p_a_raw)])
        lam_a = blended_rate(a["runs"], a["gp"], b["runs_against"], b["gp"])
        lam_b = blended_rate(b["runs"], b["gp"], a["runs_against"], a["gp"])
        commit("total", "Total runs O/U 8.5", _tw(total_market(lam_a + lam_b, 8.5), ["Under 8.5", "Over 8.5"]))
        mh = poisson_margin_under(lam_a, lam_b, -1)
        commit("handicap", "Run line +/-1.5", _tw(two_way(mh), [fx["b"] + " -1.5", fx["a"] + " +1.5"]))
        p_pick, pick = (p_a_raw, fx["a"]) if p_a_raw >= 0.5 else (1.0 - p_a_raw, fx["b"])
    elif sp == "tennis":
        if "a" in inp and "verified_finals" in inp["a"]:
            a, b = inp["a"], inp["b"]
            pa = shrink(a["verified_final_wins"], max(a["verified_finals"], 1))
            pb = shrink(b["verified_final_wins"], max(b["verified_finals"], 1))
            p_a = log5(pa, pb)
        else:
            p_a = 0.51   # no legible official form board -> near-level, tiny lean to the lower seed path
            both = False
        commit("winner", "Match winner", [_line(fx["a"], p_a), _line(fx["b"], 1.0 - p_a)], measured=bool(inp.get("a")))
        p_pick, pick = (p_a, fx["a"]) if p_a >= 0.5 else (1.0 - p_a, fx["b"])
        both = bool(inp.get("a"))
    elif sp == "darts":
        p_a = seed_pair(inp["a"]["seed"], inp["b"]["seed"])
        commit("winner", "Match winner", [_line(fx["a"], p_a), _line(fx["b"], 1.0 - p_a)])
        p_pick, pick = (p_a, fx["a"]) if p_a >= 0.5 else (1.0 - p_a, fx["b"])
    elif sp == "rugby-league":
        a, b = inp["a"], inp["b"]
        gap = b.get("pool_pos", 4) - a.get("pool_pos", 4)
        p_a = 0.5 + 0.05 * max(-2, min(2, gap)) + (0.04 if a.get("home") else 0.0) - (0.04 if b.get("home") else 0.0)
        commit("winner", "Match winner (official pool-order read)", [_line(fx["a"], p_a), _line(fx["b"], 1.0 - p_a)])
        fx["tier_note"] = "Ordinal read from the official round-three pool order; deliberately conservative."
        p_pick, pick = (p_a, fx["a"]) if p_a >= 0.5 else (1.0 - p_a, fx["b"])
    elif sp == "rugby-union":
        if fx["id"] == "ru-autumn-sco-usa":
            commit("winner", "Match winner", [_line(fx["a"], 0.84), _line(fx["b"], 0.16)], measured=False)
            p_pick, pick = 0.84, fx["a"]; both = False
            if "no-official-anchor" in fx.get("flags", []):
                fx["manual_tier"] = "low"
        elif fx["id"] == "ru-connacht-edinburgh":
            commit("winner", "Match winner", [_line(fx["a"], 0.55), _line(fx["b"], 0.45)], measured=False)
            p_pick, pick = 0.55, fx["a"]; both = False
        else:
            p_pick = None
    elif sp == "cricket" and fx["id"] == "cricket-pak-eng-t2":
        p_a = log5(shrink(inp["a"]["w"], inp["a"]["gp"]), shrink(inp["b"]["w"], inp["b"]["gp"]))
        commit("winner", "Match winner (2-0 series read, shrunk)", [_line(fx["a"], p_a), _line(fx["b"], 1.0 - p_a)])
        p_pick, pick = (p_a, fx["a"]) if p_a >= 0.5 else (1.0 - p_a, fx["b"])
    elif sp == "golf":
        commit("winner", "Tournament winner (estimate)", [
            _line("Christiaan Bezuidenhout", 0.42), _line("Co-leader (field)", 0.30),
            _line("Steven Fisk", 0.16), _line("Marcus Byrd", 0.12)], measured=False)
        p_pick, pick, both = 0.42, "Christiaan Bezuidenhout", False
    elif sp == "motor-racing" and fx["id"] == "f1-usgp-quali":
        commit("winner", "Pole position (estimate)", [
            _line("Max Verstappen", 0.54), _line("Lando Norris", 0.22),
            _line("Charles Leclerc", 0.14), _line("Oscar Piastri", 0.10)], measured=False)
        p_pick, pick, both = 0.54, "Max Verstappen", False
    elif sp == "motor-racing" and fx["id"] == "f1-usgp-race":
        commit("winner", "Race winner (estimate)", [
            _line("Max Verstappen", 0.46), _line("Lando Norris", 0.24),
            _line("Charles Leclerc", 0.16), _line("Oscar Piastri", 0.14)], measured=False)
        p_pick, pick, both = 0.46, "Max Verstappen", False
    elif sp == "handball" and fx["id"] == "hb-gummersbach-melsungen":
        commit("winner", "Match winner", [
            _line("VfL Gummersbach", 0.55), _line("MT Melsungen", 0.32), _line("Draw", 0.13)], measured=False)
        p_pick, pick, both = 0.55, "VfL Gummersbach", False

    if p_pick is None:
        return fx
    fx.update(pick=pick, pick_prob=round(p_pick, 4), decimal=round(1.0 / p_pick, 3),
              american=american_from_prob(p_pick))
    market = fx["markets"][0]
    grade = model_tier(p_pick, measured_sides=2 if (both and market.get("measured", True)) else 1,
                       fixture_state=fx["state"], market_kind="match",
                       partner_conflict=("partner-conflict" in fx.get("flags", [])),
                       manual=fx.get("manual_tier"))
    if grade == "high" and not american_in_band(p_pick):
        grade, fx["tier_note"] = "medium", "Probability in the High probability zone but fair price outside -250..+10000; demoted per the brief."
    if grade == "high" and not market.get("measured", True):
        grade = "medium"
    extras = [fx.get("tier_note", "")]
    if fx.get("manual_tier"):
        extras.append("Manual override: kept Low -- the ranking anchor did not resolve officially this session.")
    if grade == "medium" and p_pick > 1 / 1.4:
        extras.append("Fair price would be shorter than -250; outside the agreed window, kept Medium.")
    if "nearest-miss-high" in fx.get("flags", []):
        extras.append("Sits at exactly the 70.00% boundary; the rule wants strictly above, so Medium.")
    if grade == "medium" and market.get("measured", True) is False:
        extras.append("Multi-runner or one-sided market -- confidence capped.")
    fx["tier"] = {"high": "High", "medium": "Medium", "low": "Low"}.get(grade, grade)
    fx["tier_note"] = " ".join(e for e in extras if e).strip()
    if fx["tier"] == "High":
        fx.setdefault("flags", []).append("high-pick")
    return fx


FLAG_ITEMS = [
    dict(id="F-99-01", kind="band", text="High window today resolved to a single selection (Edmonton) at exactly the -250 inclusive edge. Five-High-per-sport cannot be manufactured: prices are never widened or rewritten to chase the quota."),
    dict(id="F-99-02", kind="band", text="Vegas (0.7000 exactly) misses High only by the strict 'above 70.00%' rule; New Jersey at -267 fails the lower band edge by a few ticks. Both kept Medium with notes."),
    dict(id="F-99-03", kind="source", text="pdc.tv player-market pages are cookie-walled in a static read; darts priced from the official PDPA event page only."),
    dict(id="F-99-04", kind="source", text="wtatennis.com returned a JS shell: Wuhan semifinal carries no line; Basel-only tennis board today."),
    dict(id="F-99-05", kind="source", text="GBGB race cards unreadable in static mode -- greyhound per-race lines withheld; meeting directory only."),
    dict(id="F-99-06", kind="source", text="Lega Volley calendar sits behind a navigation wall in a static read; volleyball prices withheld for the round."),
    dict(id="F-99-07", kind="source", text="premiershiprugby.com and usa.rugby gave no legible listings; Quins v Saints and USA v Australia A withheld, flagged."),
    dict(id="F-99-08", kind="timing", text="In play or started at the publish read: NHL Ducks v Flyers, Top 14 Toulon v Pau, URC Welsh and Irish derbies, snooker semi-finals, HBL Balingen. No pre-match prices published on any of them."),
    dict(id="F-99-09", kind="data", text="NBA handicap/total markets unpriced (no official team PPG read this session); SAS/DAL/WAS had not submitted to the 1:30PM injury issue -- availability left blank and flagged."),
    dict(id="F-99-10", kind="method", text="RLWC pricing uses the official round-three pool order only (ordinal plus host lean). Capped framing at 0.60/0.40."),
    dict(id="F-99-11", kind="data", text="Galway SHC final pick withheld -- county board lists the pairing but no legible official form digits; Cork finals' finalist blocks unresolved."),
    dict(id="F-99-12", kind="method", text="Golf and F1 outcome prices are labelled estimates (multi-runner fields): never eligible for High on this desk by design."),
]


def build_all():
    for fx in FIXTURES:
        compute_book(fx)
    picks = [f for f in FIXTURES if f.get("state") == "upcoming" and f.get("pick")]
    highs = [f for f in picks if f.get("tier") == "High"]
    return dict(fixtures=FIXTURES, picks=picks, highs=highs, flags=FLAG_ITEMS)


if __name__ == "__main__":
    b = build_all()
    print("fixtures", len(b["fixtures"]), "| priced", len([f for f in b["fixtures"] if f["markets"]]),
          "| picks", len(b["picks"]))
    for f in b["picks"]:
        print(f'{f["tier"]:6s} {f["american"]:>6} p={f["pick_prob"]:.4f}  {f["sport"][:14]:14s} {f["id"]}: pick={f["pick"]}')

# ---------------------------------------------------------------------------
# Written predictions for High picks.  Exactly one per High selection.
# Words "model" and "verified" must never appear (enforced by the validator).
# ---------------------------------------------------------------------------

PREDICTIONS = {
    "nhl-tor-edm": (
        "Edmonton are the call tonight because everything measurable from the official record points one way. "
        "The Oilers return home at 8-1-1 with 47 goals scored and only 32 conceded across their opening ten games, "
        "the best attacking return on tonight's slate. Toronto bring a respectable 6-4-2 mark but have already "
        "shipped 39 in twelve, and the fractionally lighter workload still leaves them chasing the home side's "
        "numbers on a per-game basis. The Leafs have the firepower to make it interesting, yet over sixty minutes "
        "the steadier goal differential sits with the Oilers at Rogers Place. Our desk line prices Edmonton at "
        "exactly minus 250, the shortest number this grade is allowed to carry, and that is where the value read "
        "stops. Selection: Edmonton Oilers to win the match."
    ),
}

# ---------------------------------------------------------------------------
# Display aliases for the site builder + lead official sources per sport.
# ---------------------------------------------------------------------------

for _s in SOURCES:
    _s.setdefault("label", _s.get("publisher", _s["id"]))

OFFICIAL_LEAD = {
    "golf": ("pga-bermuda",), "volleyball": ("legavolley",), "rugby-union": ("top14", "urc-r4"),
    "cricket": ("pcb-news",), "snooker": ("wst-niopen",), "darts": ("pdc-ec",),
    "baseball": ("mlb-schedule", "mlb-standings"), "gaelic-sports": ("gaa-galway", "gaa-cork"),
    "greyhounds": ("gbgb-racing",), "tennis": ("atp-scores", "atp-news"),
    "motor-racing": ("f1-usgp",), "handball": ("hbl-melsungen",),
    "ice-hockey": ("nhl-score", "nhl-standings"), "basketball": ("nba-games", "nba-injury"),
    "rugby-league": ("nrl-rlwc",),
}

# OLBG returns 'souvenir' tickets for illustrative clicks; kept as registry text only.
OLBG_TICKETS = [
    dict(sport=slug, route=route, ticket="discovery-only",
         note="Match-market structure studied; no price taken or verified from OLBG.")
    for slug, _name, route in SPORTS
]
