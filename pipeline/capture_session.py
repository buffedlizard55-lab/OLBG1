"""Create immutable *selected excerpts* read with Arena's retrieval tool on 22 Oct.

This is an evidence import, NOT a live scraper. Running it must not restamp old
facts. Exact HTTP status/headers were not exposed by that tool. No byte-for-byte
origin-response hash is claimed. JSON excerpts are field projections; prose
excerpts retain the relevant words only. Automated HTTP captures live elsewhere.
"""
from .common import save
from .evidence import seal_capture, fixture_from_observation
from .config import CURRENT

AFTER = '2026-10-22T07:17:40Z'  # clock read before retrieval began
BEFORE = '2026-10-22T07:30:30Z'  # clock read after the imported retrievals
CAPTURES, FIXTURES, STATS = [], [], []


def capture(cid, url, sport, scope, notes='', role='official', final_url=None, observations=None):
    c = {'id': cid, 'url': url, 'final_url': final_url or url, 'role': role,
         'sport': sport, 'method': 'retrieval-tool-selected-excerpts',
         'observed_after': AFTER, 'observed_before': BEFORE,
         'http_status': None, 'raw_response_sha256': None,
         'excerpt_policy': 'Selected, normalized excerpts and JSON field projections; not a byte-for-byte response or a verbatim full-page transcript.',
         'scope': scope, 'complete': False, 'notes': notes, 'observations': observations or []}
    CAPTURES.append(c)
    return c


def obs(c, oid, quote, values, locator=None):
    o = {'id': str(oid), 'locator': locator or str(oid), 'quote': quote, 'values': values}
    c['observations'].append(o)
    return o


def fixture(c, oid, quote, **values):
    notes = values.pop('notes', [])
    kind = values.pop('kind', 'match')
    provider = next((x for x in ('nhl', 'mlb', 'nba') if c['id'].startswith(x+'-') and ('schedule' in c['id'] or 'games' in c['id'])), c['id'])
    row = fixture_from_observation(c, obs(c, oid, quote, values), c['sport'], f'{provider}-{oid}', kind=kind, notes=notes)
    FIXTURES.append(row)
    return row


def record(c, oid, quote, **values):
    o = obs(c, oid, quote, values)
    STATS.append({'id': f'{c["id"]}-{oid}', 'source_id': c['id'], 'observation_id': o['id'],
                  'observed_after': AFTER, 'observed_before': BEFORE, **values})


def seed():
    CAPTURES.clear(); FIXTURES.clear(); STATS.clear()
    nhl = capture('nhl-schedule-20261022', 'https://api-web.nhle.com/v1/schedule/2026-10-22', 'ice-hockey',
                  'All 12 games under gameWeek date 2026-10-22; only chunks 0–2 read. Later week not enumerated.',
                  'Field projections from NHL JSON. Game-state FUT; gameScheduleState OK. No inference from OLBG clocks.')
    games = [
        (2026020154, 6, 'Boston Bruins', 18, 'Nashville Predators', '2026-10-22T23:00:00Z', 'TD Garden'),
        (2026020155, 10, 'Toronto Maple Leafs', 3, 'New York Rangers', '2026-10-22T23:00:00Z', 'Scotiabank Arena'),
        (2026020156, 9, 'Ottawa Senators', 28, 'San Jose Sharks', '2026-10-22T23:00:00Z', 'Canadian Tire Centre'),
        (2026020157, 1, 'New Jersey Devils', 24, 'Anaheim Ducks', '2026-10-22T23:00:00Z', 'Prudential Center'),
        (2026020158, 5, 'Pittsburgh Penguins', 13, 'Florida Panthers', '2026-10-22T23:00:00Z', 'PPG Paints Arena'),
        (2026020159, 2, 'New York Islanders', 26, 'Los Angeles Kings', '2026-10-22T23:30:00Z', 'UBS Arena'),
        (2026020160, 19, 'St. Louis Blues', 54, 'Vegas Golden Knights', '2026-10-23T00:00:00Z', 'Enterprise Center'),
        (2026020161, 25, 'Dallas Stars', 52, 'Winnipeg Jets', '2026-10-23T00:00:00Z', 'American Airlines Center'),
        (2026020162, 20, 'Calgary Flames', 30, 'Minnesota Wild', '2026-10-23T01:00:00Z', 'Scotiabank Saddledome'),
        (2026020163, 22, 'Edmonton Oilers', 12, 'Carolina Hurricanes', '2026-10-23T01:00:00Z', 'Rogers Place'),
        (2026020164, 55, 'Seattle Kraken', 68, 'Utah Mammoth', '2026-10-23T02:00:00Z', 'Climate Pledge Arena'),
        (2026020165, 23, 'Vancouver Canucks', 17, 'Detroit Red Wings', '2026-10-23T02:00:00Z', 'Rogers Arena'),
    ]
    for gid, hid, home, aid, away, start, venue in games:
        # Full names are the concatenation of NHL placeName.default and commonName.default.
        quote = f'gameWeek.date="2026-10-22"; id={gid}; homeTeam.id={hid}, {home}; awayTeam.id={aid}, {away}; startTimeUTC="{start}"; venue.default="{venue}"; gameState="FUT"; gameScheduleState="OK"; season=20262027.'
        fixture(nhl, gid, quote, participant_a=home, participant_b=away,
                participant_a_id=str(hid), participant_b_id=str(aid), date='2026-10-22',
                start_utc=start, venue=venue, competition='NHL', season='20262027', official_status='FUT')
    mlb_url = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-28&fields=totalGames,dates,date,games,gamePk,gameDate,status,detailedState,abstractGameState,teams,away,home,team,id,name,venue'
    mlb = capture('mlb-schedule-20261022', mlb_url, 'baseball', 'MLB API date range 22–28 October inclusive; all 5 returned games.',
                  'Reported totalGames=5 reconciles to 5 rows. Date is official league date; UTC can fall on next day. Conditional series games are not guarantees of play.')
    mlb['complete'] = True
    for gid, date, utc, home, hid, away, aid, venue in [
        (849805,'2026-10-23','2026-10-24T00:00:00Z','Milwaukee Brewers',158,'Tampa Bay Rays',139,'American Family Field'),
        (849802,'2026-10-24','2026-10-25T00:00:00Z','Milwaukee Brewers',158,'Tampa Bay Rays',139,'American Family Field'),
        (849804,'2026-10-26','2026-10-27T00:00:00Z','Tampa Bay Rays',139,'Milwaukee Brewers',158,'Tropicana Field'),
        (849803,'2026-10-27','2026-10-28T00:00:00Z','Tampa Bay Rays',139,'Milwaukee Brewers',158,'Tropicana Field'),
        (849799,'2026-10-28','2026-10-29T00:00:00Z','Tampa Bay Rays',139,'Milwaukee Brewers',158,'Tropicana Field'),
    ]:
        quote = f'gamePk {gid}; date {date}; gameDate {utc}; away team {aid} {away}; home team {hid} {home}; venue {venue}; abstractGameState Preview; detailedState Scheduled.'
        fixture(mlb, gid, quote, participant_a=home, participant_b=away, participant_a_id=str(hid), participant_b_id=str(aid),
                date=date, start_utc=utc, venue=venue, competition='MLB', season='2026', official_status='Scheduled', notes=['Series games may be conditional; starting pitchers not verified.'])
    nba = capture('nba-games-20261022', 'https://www.nba.com/games?date=2026-10-22', 'basketball', 'Both games displayed for 22 October; not the full week.')
    for gid, a, b, when in [('0022600006','Cavaliers','76ers','7:00 PM ET'), ('0022600007','Nuggets','Thunder','9:30 PM ET')]:
        fixture(nba, gid, f'October 2026, Thu22: {a} 0-0 — {when} — {b} 1-0; game {gid}.',
                participant_a=a, participant_b=b, date='2026-10-22', time_text=when, competition='NBA', season='2026-27',
                notes=['Time retained as published. No UTC start or venue imported from an assumed timezone. Zero-game records cannot justify a price.'])
    el = capture('euroleague-round7', 'https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/', 'basketball',
                 'Nine upcoming Round 7 match headings and associated W–L records from chunks 0–1; completed Hapoel–Virtus excluded.',
                 'Real Madrid prose says 3-3 overall and 1-4 away; inconsistent, so its W–L input is quarantined. No injury claim imported.')
    el_rows = [
        (64,22,'19:30','Anadolu Efes Istanbul',2,4,'Besiktas Istanbul',3,3),
        (65,22,'20:00','FC Bayern Munich',2,4,'Dubai Basketball',4,2),
        (62,22,'20:05','Maccabi Rapyd Tel Aviv',2,4,'Real Madrid',3,3),
        (67,22,'20:15','Panathinaikos AKTOR Athens',5,1,'Kosner Baskonia Vitoria-Gasteiz',1,5),
        (63,22,'20:30','Armani Olimpia Milan',1,5,'FC Barcelona',3,3),
        (66,22,'20:45','Partizan Mozzart Bet Belgrade',3,3,'Crvena Zvezda Meridianbet Belgrade',4,2),
        (68,23,'19:00','Zalgiris Kaunas',2,4,'LDLC ASVEL Villeurbanne',2,4),
        (70,23,'20:15','Olympiacos Piraeus',5,1,'Fenerbahce Tarfin Istanbul',5,1),
        (69,23,'20:45','Paris Basketball',1,5,'Valencia Basket',5,1),
    ]
    for gid, day, time, a, w, l, b, w2, l2 in el_rows:
        q = f'October {day}, 2026: {a} vs. {b} ({time} CEST). Records: {a} ({w}-{l}); {b} ({w2}-{l2}).'
        hour, minute = map(int,time.split(':'))
        fixture(el, gid, q, participant_a=a, participant_b=b, participant_a_id=a, participant_b_id=b, date=f'2026-10-{day}',
                start_utc=f'2026-10-{day}T{hour-2:02d}:{minute:02d}:00Z', time_text=time+' CEST',
                competition='EuroLeague', season='2026-27', notes=['UTC is a deterministic conversion of explicitly published CEST (UTC+02:00).'])
        for team, wins, losses in [(a,w,l),(b,w2,l2)]:
            if team == 'Real Madrid':
                continue
            record(el, 'record-'+str(gid)+'-'+str(wins)+'-'+('a' if team==a else 'b'), q, team=team, team_id=team, competition='EuroLeague', season='2026-27',
                   wins=wins, losses=losses, games_played=wins+losses, games_played_method='wins + losses', as_of='2026-10-22')
    wst = capture('wst-ni-open', 'https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5', 'snooker',
                  'All eight 22 Oct Round 3 ties in More Tournament Matches.', 'Displayed clocks have no timezone. No UTC start, venue, format or ranking inferred.')
    for i,(a,b,t) in enumerate([
        ('Kyren Wilson','Pang Junxu','08:00'),('Matthew Selt','Sam Craigie','08:00'),('Elliot Slessor','Ricky Walden','09:00'),
        ('Anthony McGill','Mateusz Baranowski','09:00'),('Mark Williams',"Martin O’Donnell",'14:00'),('David Gilbert','Cheung Ka Wai','14:00'),
        ('Jordan Brown','Scott Donaldson','15:00'),('Jak Jones','Daniel Wells','15:00')]):
        fixture(wst, i+1, f'22 Oct; BetVictor Northern Ireland Open 2026; Round 3; {a}; {t}; {b}.',
                participant_a=a, participant_b=b, date='2026-10-22', time_text=t+' (timezone not stated)', competition='BetVictor Northern Ireland Open 2026', notes=['Match status and timezone unverified; no bet.'])
    # Order-of-play is a listing, not proof that a match has not yet started.
    tennis = [
        ('atp-almaty-op','https://www.protennislive.com/posting/2026/9410/op.pdf','ATP Almaty',[
            ('Terence Atmane','Mattia Bellucci','Starts At 11:30','singles'),('Tomas Machac','Karen Khachanov','Not Before 13:00','singles'),
            ('Daniil Medvedev','Sho Shimabukuro','Followed By','singles'),('Alexander Bublik','Fabian Marozsan','Not Before 19:30','singles'),
            ('Alexander Donski / Filip Pieczonka','Yuki Bhambri / Ryan Seggerman','Starts At 11:30','doubles'),
            ('Jason Kubler / John Peers','Nathaniel Lammons / Jackson Withrow','Followed By','doubles'),
            ('N.Sriram Balaji / Evan King','Jean-Julien Rojer / Theodore Winegar','Followed By','doubles')]),
        ('atp-lyon-op','https://www.protennislive.com/posting/2026/496/op.pdf','ATP Lyon',[
            ('Valentin Vacherot','Luca Van Assche','Not Before 14:00','singles'),('Pierre-Hugues Herbert','Taylor Fritz','Followed By','singles'),
            ('Borna Gojo','Daniel Altmaier','Followed By','singles'),('Flavio Cobolli','Stan Wawrinka','Not Before 19:00','singles'),
            ('Kyrian Jacquet','Brandon Nakashima','Followed By','singles'),
            ('Romain Arneodo / Ugo Blanchet','Matisse Bobichon / Kilian Feldbausch','Starts At 12:00','doubles'),
            ('Santiago Gonzalez / Hendrik Jebens','Theo Arribage / Albano Olivetti','Starts At 11:00','doubles'),
            ('Julian Cash / Lloyd Glasspool','Andrew Paulson / Nino Serdarusic','Followed By','doubles')]),
        ('atp-brussels-op','https://www.protennislive.com/posting/2026/7485/op.pdf','ATP Brussels',[
            ('Raphael Collignon','Jiri Lehecka','Starts At 13:30','singles'),('David Goffin','Alex Michelsen','Followed By','singles'),
            ('Damir Dzumhur','Zizou Bergs','Not Before 17:00','singles'),
            ('Guido Andreozzi / Manuel Guinard','Nicolas Barrientos / David Pel','Starts At 15:00','doubles'),
            ('Constantin Frantzen / Robert Galloway','Raphael Collignon / David Goffin','Followed By','doubles')]),
        ('wta-ningbo-op','https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf','WTA Ningbo',[
            ('Iva Jovic','Jasmine Paolini','Starting at 1:00 PM','singles'),('Katarzyna Kawa','Belinda Bencic','Followed by','singles'),
            ('Alexandra Eala','Diana Shnaider','Followed by','singles'),('Elena Rybakina','Polina Kudermetova','Not before 7:00 PM','singles'),
            ('Hanyu Guo / Kristina Mladenovic','Ellen Perez / Demi Schuurs','Starting at 2:00 PM','doubles'),
            ('Mariia Kozyreva / Maia Lumsden','Desirae Krawczyk / Fanny Stollar','Not before 3:30 PM','doubles')]),
        ('wta-osaka-op','https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf','Kinoshita Group Japan Open',[
            ('Ann Li','Zeynep Sonmez','Starting at 11:30 AM','singles'),('Mary Stoiana','Moyuka Uchijima','Followed by','singles'),
            ('Magda Linette','Katerina Siniakova','Followed by','singles'),
            ('Ingrid Neel / Giuliana Olmos','Isabelle Haverlag / Lilli Tagger','Not before 1:00 PM','doubles'),
            ('Jesika Maleckova / Miriam Skoch','Hao-Ching Chan / Miyu Kato','Followed by','doubles')]),
    ]
    for cid,url,label,rows in tennis:
        c = capture(cid,url,'tennis','22 October order-of-play; singles AND doubles; no results polling.',
                    'Case normalized; pair membership retained. Clocks have no explicit timezone. Followed-by/not-before is not an exact start. Osaka Ruzic–Day RET row excluded.')
        for i,(a,b,t,fmt) in enumerate(rows):
            fixture(c,i+1,f'ORDER OF PLAY - THURSDAY, OCTOBER 22, 2026. {t}: {a} VS {b}.',
                    participant_a=a,participant_b=b,date='2026-10-22',time_text=t,competition=label if cid=='wta-osaka-op' else None,format=fmt,
                    notes=['Order-of-play only; current match state and UTC time unverified. Where the extraction omits the tournament heading, competition is blank; no name inferred from an old dataset or URL ID.'])
    obs(next(c for c in CAPTURES if c['id']=='wta-osaka-op'),'retired-entry','6-4 0-0 RET R16 | Antonia RUZIC CRO vs [LL] Kayla DAY USA.',{})
    top = capture('lnr-top14-j7','https://top14.lnr.fr/calendrier-et-resultats','rugby-union','TOP 14 2026/2027, all seven Round 7 fixtures.', 'Local clocks have no explicit timezone; do not guess the DST offset on 25 October.')
    for i,(a,b,day,t) in enumerate([
        ('RC Vannes','ASM Clermont',24,'14h30'),('Aviron Bayonnais','LOU Rugby',24,'16h35'),('Castres Olympique','Stade Français Paris',24,'16h35'),
        ('Racing 92','Montpellier Hérault Rugby',24,'16h35'),('Stade Toulousain','USA Perpignan',24,'16h35'),('RC Toulon','Section Paloise',24,'21h00'),
        ('Stade Rochelais','Union Bordeaux-Bègles',25,'21h05')]):
        fixture(top,i+1,f'Calendrier et résultats TOP 14 - 2026/2027; Journée 7; {day} octobre; {a}; {t}; {b}.',
                participant_a=a,participant_b=b,date=f'2026-10-{day}',time_text=t,competition='TOP 14',season='2026/2027')
    irl = capture('irl-fixtures','https://www.intrl.sport/fixtures-results','rugby-league','Visible dated fixtures through 25 October. Load-more control prevents a global completeness claim.',
                  'Men and women are separate competitions. No times converted without an explicit timezone.')
    irl_rows = [
        (2586,23,'Samoa','Wales','Women','17:50','CommBank Stadium, Sydney','IRL Women’s Rugby League World Cup'),
        (2569,23,'Tonga','Lebanon','Men','20:05','CommBank Stadium, Sydney','IRL Men’s Rugby League World Cup'),
        (2587,24,'Fiji','Papua New Guinea','Women','12:15','Santos National Football Stadium, Port Moresby','IRL Women’s Rugby League World Cup'),
        (2661,24,'Scotland','Wales','Men','14:00','Biggar RFC','Senior International Matches (Men)'),
        (2664,24,'Netherlands','Serbia','Men','14:00','FK Zemun Stadium','European Championship B (Men)'),
        (2570,24,'Papua New Guinea','Samoa','Men','14:25','Santos National Football Stadium, Port Moresby','IRL Men’s Rugby League World Cup'),
        (2571,24,'England','France','Men','14:35','HBF Park, Perth','IRL Men’s Rugby League World Cup'),
        (2646,24,'Italy','Czechia','Men','15:00','Stadio Giovanni Invernizzi, Abbiategrasso','European Championship D (Men)'),
        (2588,24,'Australia','England','Women','17:05','HBF Park, Perth','IRL Women’s Rugby League World Cup'),
        (2665,25,'Malta','Philippines','Women','15:00','Croom Oval','Senior International Matches (Women)'),
        (2589,25,'New Zealand','France','Women','15:50','One NZ Stadium, Christchurch','IRL Women’s Rugby League World Cup'),
        (2572,25,'New Zealand','Cook Islands','Men','18:05','One NZ Stadium, Christchurch','IRL Men’s Rugby League World Cup'),
        (2573,25,'Australia','Fiji','Men','19:05','Suncorp Stadium, Brisbane','IRL Men’s Rugby League World Cup'),
    ]
    for gid,day,a,b,gender,t,v,comp in irl_rows:
        fixture(irl,gid,f'{comp}; {day} October, 2026; Venue: {v}; {a}; {t}; {b}; match-details/{gid}.',
                participant_a=a,participant_b=b,date=f'2026-10-{day}',time_text=t,venue=v,competition=comp,format=gender)
    pcb = capture('pcb-odi-1465','https://www.pcb.com.pk/pakistan-england-and-sri-lanka-trination-odi-series-202627/tournament/1465.html','cricket',
                  'Tri-nation ODI series: three listed fixtures within 22–28 October. No time or current match state in this table.')
    for seq,day,a,b,venue in [(3,22,'Sri Lanka','England','Rawalpindi Cricket Stadium, Rawalpindi'),(4,25,'Pakistan','England','Gaddafi Stadium, Lahore'),(5,27,'Pakistan','Sri Lanka','Gaddafi Stadium, Lahore')]:
        fixture(pcb,seq,f'{day}-10-2026 | {a} vs {b} | {seq} Match | {venue}. Pakistan, England and Sri Lanka Tri-nation ODI Series 2026/27.',
                participant_a=a,participant_b=b,date=f'2026-10-{day}',venue=venue,competition='Pakistan, England and Sri Lanka Tri-nation ODI Series 2026/27',format='ODI')
    ehf = capture('ehf-cl-schedule','https://www.eurohandball.com/media/jqal4wt0/ehfcl-men-2026-27-group-phase-playing-times.pdf','handball',
                  'Five 22 October Round 5 entries. Publication says Status: July 29, 2026; current amendments NOT confirmed.',
                  'Document verified, not a fresh fixture-status feed. Do not use July schedule to certify October match availability.')
    for i,(a,b,t,v) in enumerate([
        ('MT Melsungen','Orlen Wisla Plock','18:45','Rothenbach-Halle (Kassel, GER)'),('OTP Bank-Pick Szeged','GOG','18:45','Pick Arena (Szeged, HUN)'),
        ('Sporting CP','IFK Kristianstad','20:45','Pavilhao Joao Rocha (Lisbon, POR)'),('Barça','Montpellier HB','20:45','Palau Blaugrana (Barcelona, ESP)'),
        ('Kolstad Handball','SC Magdeburg','20:45','Kolstad Arena (Kolstad, NOR)')]):
        fixture(ehf,i+1,f'EHF CHAMPIONS LEAGUE MEN 2026/27 | ROUND 5 | {a} vs {b} | {v} | Thursday 22.10.2026 | {t}h CEST | Status: July 29, 2026.',
                participant_a=a,participant_b=b,date='2026-10-22',time_text=t+' CEST',venue=v,competition='EHF Champions League Men',season='2026/27',
                notes=['Published July 29 schedule only; current fixture amendments/status unverified. Start UTC withheld pending current confirmation.'])
    f1=capture('f1-austin','https://www.formula1.com/en/racing/2026/united-states','motor-racing','United States GP session calendar; no complete runner field or qualifying results.',
               'The page switches My time/Track time, so the extracted clock cannot establish a timezone.')
    for oid,day,event,time in [('practice1',23,'Practice 1','13:30–14:30'),('practice2',23,'Practice 2','17:00–18:00'),('practice3',24,'Practice 3','13:30–14:30'),('qualifying',24,'Qualifying','17:00–18:00'),('race',25,'Race','16:00')]:
        fixture(f1,oid,f'FORMULA 1 MSC CRUISES UNITED STATES GRAND PRIX 2026. {day}Oct {event} {time}. Circuit of The Americas.',
                event=event,date=f'2026-10-{day}',time_text=time,competition='Formula 1 United States Grand Prix 2026',venue='Circuit of The Americas',kind='event',
                notes=['Clock timezone not established. No field, no invented two-runner winner market.'])
    gaa=capture('munster-calendar','https://munster.gaa.ie/fixtures/events-calendar/','gaelic-football','Three senior football finals on 25 October. Hurling and camogie/shinty entries not imported.')
    for oid,a,b,t,v,comp in [
        ('kerry','Dr. Crokes','Kenmare Shamrocks','2:00pm','Fitzgerald Stadium Killarney','2026 Kerry County Senior Football Championship Final'),
        ('waterford','Rathgormack','The Nire','2:30pm','Cappoquin Logistics Fraher Field, Dungarvan','2026 Waterford Senior Football Championship Final'),
        ('cork','St Finbarrs','Nemo Rangers','4:00pm','SuperValu Páirc Uí Chaoimh','2026 Cork Premier Senior Football Championship Final')]:
        fixture(gaa,oid,f'{comp} – {a} v {b}. Sun, Oct 25, 2026 @ {t}. {v}.',participant_a=a,participant_b=b,date='2026-10-25',time_text=t,venue=v,competition=comp,
                notes=['Gaelic football retained as a distinct historical project category; association football remains excluded.'])
    # Further captures and stats are imported below. Do not copy any legacy ratings.
    seed_additional()
    for c in CAPTURES:
        save(CURRENT/'evidence'/f'{c["id"]}.json',seal_capture(c))
    save(CURRENT/'session_import.json',{'schema_version':1,'session':'257e6674-olbg1','observed_after':AFTER,'observed_before':BEFORE,
          'method':'Selected excerpts of actually read official pages; not a raw HTTP archive; no legacy row recertification.',
          'fixtures':FIXTURES,'statistics':STATS,'source_ids':[c['id'] for c in CAPTURES]})


def seed_additional():
    nhl = capture('nhl-standings-20261021','https://www.nhl.com/standings/2026-10-21/wildcard','ice-hockey',
                  'Season standings as of 21 October: GP, W, L, OT and PTS for the 24 clubs on the imported slate.',
                  'W + L + OT = GP; 2W + OT = PTS checked for every record. NHL states shootout goals are included in GF/GA, so those aggregates are NOT used for regulation totals.')
    needed = {r['facts'][side]: r['facts'][side+'_id'] for r in FIXTURES if r['sport']=='ice-hockey' for side in ('participant_a','participant_b')}
    rows = [
        ('Boston Bruins',10,7,2,1,15),('Ottawa Senators',10,7,3,0,14),('Carolina Hurricanes',11,8,2,1,17),
        ('New York Rangers',11,7,3,1,15),('New York Islanders',9,5,3,1,11),('Florida Panthers',10,5,3,2,12),
        ('Toronto Maple Leafs',11,5,4,2,12),('New Jersey Devils',9,5,4,0,10),('Detroit Red Wings',9,3,3,3,9),
        ('Pittsburgh Penguins',10,3,6,1,7),('Utah Mammoth',10,7,3,0,14),('Minnesota Wild',10,6,2,2,14),
        ('Dallas Stars',9,5,3,1,11),('Vegas Golden Knights',11,8,3,0,16),('Edmonton Oilers',9,7,1,1,15),
        ('Seattle Kraken',10,6,3,1,13),('San Jose Sharks',10,5,4,1,11),('Winnipeg Jets',9,4,3,2,10),
        ('Nashville Predators',8,3,2,3,9),('St. Louis Blues',9,4,4,1,9),('Anaheim Ducks',9,4,5,0,8),
        ('Vancouver Canucks',11,2,8,1,5),('Los Angeles Kings',7,1,4,2,4),('Calgary Flames',8,2,6,0,4),
    ]
    for team,gp,w,l,ot,pts in rows:
        record(nhl,needed[team],f'Oct 21 standings | {team} | GP {gp} | W {w} | L {l} | OT {ot} | PTS {pts}.',
               team=team,team_id=needed[team],competition='NHL',season='20262027',as_of='2026-10-21',
               games_played=gp,wins=w,losses=l,ot_losses=ot,points=pts,
               period_note='Season standings table for the schedule season; not last-ten match logs.')
    mlb = capture('mlb-records-2026','https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason&fields=records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed,gamesPlayed,league,id,division',
                  'baseball','Selected JSON fields for the two World Series participants; chunks 0 and 2.',
                  'Regular season, NOT postseason form. IDs join to the MLB schedule; no fuzzy team-name match. Split records without type labels are not used.')
    for tid,name,w,l,rf,ra in [(139,'Rays',98,64,736,650),(158,'Brewers',103,59,832,618)]:
        record(mlb,tid,f'team.id={tid}; team.name="{name}"; gamesPlayed=162; wins={w}; losses={l}; runsScored={rf}; runsAllowed={ra}. Query: season=2026; standingsTypes=regularSeason.',
               team=name,team_id=str(tid),competition='MLB',season='2026',games_played=162,wins=w,losses=l,
               runs_scored=rf,runs_allowed=ra,as_of='2026-10-22',period_note='2026 regular season; as_of is observation date, not last game date.')
    afl = capture('aflw-8970','https://www.afl.com.au/aflw/matches/8970','aussie-rules',
                  'One directly read Round 11 match centre. Eight other fixtures on the hub were not imported as fully checked rows.')
    fixture(afl,8970,'2026 NAB AFLW Season. Port Adelaide v Collingwood. Round 11 • Friday 23 October 2026 • 4:15 AM (EDT). Alberton Oval, Adelaide • Kaurna.',
            participant_a='Port Adelaide',participant_b='Collingwood',date='2026-10-23',time_text='4:15 AM (EDT)',start_utc='2026-10-23T08:15:00Z',
            competition='2026 NAB AFLW Season',venue='Alberton Oval, Adelaide',notes=['UTC converted from explicitly stated EDT (UTC−04:00), not the user’s locale. No current ladder imported.'])
    golf = capture('pga-schedule','https://www.pgatour.com/schedule','golf',
                   'This Week section, chunk 4: one event in 22–28 October; not all golf tours or matchups.')
    fixture(golf,'R2026528','Season 2026. This Week: OCT 22 - 25. Butterfield Bermuda Championship. Port Royal Golf Course. Southampton • Bermuda.',
            event='Butterfield Bermuda Championship',competition='PGA TOUR',date='2026-10-22',time_text='22–25 October 2026',venue='Port Royal Golf Course, Southampton',kind='event',
            notes=['Full field, matchups, withdrawals and tee-time schedule not imported; no invented outright prices.'])
    vol = capture('pls-skra-calendar','https://www.tauronliga.pl/teams/tour/53/id/61.html','volleyball',
                  'Two dated opponent entries from the SKRA club calendar, chunk 7.',
                  'PlusLiga URL redirected to a page headed TAURON Liga. Competition and UTC time remain blank; identity mismatch is a review flag.')
    for day,opp,t in [(24,'PGE Projekt Warszawa','18:00'),(27,'GKS Katowice','17:30')]:
        fixture(vol,day,f'PGE GiEK SKRA Bełchatów - Sezon 2026/2027 - Kluby - TAURON Liga. {opp} -:- {day}.10.2026, {t}.',
                participant_a='PGE GiEK SKRA Bełchatów',participant_b=opp,date=f'2026-10-{day}',time_text=t,season='2026/2027',
                notes=['Competition identity conflict following PlusLiga → TAURON Liga redirect. Competition, home/away, venue and UTC time not established. No bet.'])
    lol = capture('riot-worlds-overview','https://lolesports.com/en-GB/tournament/115660540725177488/overview','esports',
                  'Worlds overview (chunks 0–1), not a dated fixture list.',
                  'The event overview does not verify any particular head-to-head or stage date. No match pairings inferred from qualifying teams.')
    fixture(lol,'worlds2026','Worlds Standings. IN PROGRESS. Oct – Nov. Winner of the 2026 League of Legends Esports season. Swiss: 16 teams ... 5 round Swiss format ... 8 teams with 3 wins ... Knockout stage.',
            event='Worlds 2026',competition='League of Legends',kind='event',notes=['No dated head-to-head returned in this overview. Date, start, participants and selection blank.'])
    for cid,url,sport,scope,quote in [
        ('pdc-extraction','https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/','darts','Inspected extraction chunks 0, 5 and 6; match schedule not obtained.','We value your privacy. We and our 1033 partners use cookies and other tracking technologies.'),
        ('gbgb-racing','https://www.gbgb.org.uk/racing/','greyhounds','Racing shell; no populated race rows in retrieved text.','Latest Results. Search Races. Track All. Class All. Date. Time. Winner.'),
        ('gbgb-open','https://www.gbgb.org.uk/racing/open-races/','greyhounds','Open-race calendar controls, but no runner-level cards in retrieved text.','Open Races. Filter the results by entering the dates or types of races you want to see. Clear Search.'),
        ('pga-missing-article','https://www.pgatour.com/article/news/latest/2026-10-20/butterfield-bermuda-championship-facts-and-figures-port-royal-golf-course-southampton-2026','golf','Legacy source URL now returns page-not-found text. HTTP status not exposed.','Page Not Found. The page you are looking for has either been moved, deleted or simply does not exist.'),
        ('aflw-empty-article','https://www.afl.com.au/aflw/news/1634367/finals-before-finals-the-games-that-will-shape-the-top-eight','aussie-rules','Both extracted chunks contain navigation/footer but no match preview body; do not recertify old prose.','Finals before finals: The games that will shape the AFLW top eight. Premier Partner. Major Partners. Download the Official AFL App.'),
        ('wst-empty-report','https://www.wst.tv/news/2026/october/21/betvictor-northern-ireland-open-2026-day-four-afternoon/','snooker','Headline and ads only; no score available in this extraction.','BetVictor Northern Ireland Open 2026 Day Four Afternoon. By World Snooker Tour.'),
    ]:
        c=capture(cid,url,sport,scope,'Not fixture verification; missing content is not proof of no fixtures.')
        obs(c,'retrieval',quote,{})
    robots=capture('olbg-robots','https://www.olbg.com/robots.txt',None,'Public robots policy read in full.',
                   'Respect /api/ and /storage/app/json_data/ disallows; do not use hidden-worker endpoints or rotate identities.',role='discovery')
    obs(robots,'policy','User-agent: *\nDisallow: /api/\nDisallow: /storage/app/json_data/\nDisallow: /premium/\nUser-agent: Python-urllib\nDisallow: /',{})
    sitemap=capture('olbg-sitemap','https://www.olbg.com/sitemap-betting-tips.xml',None,'Chunk 0 public sport route grammar only; all competitions not enumerated.',role='discovery')
    obs(sitemap,'routes','https://www.olbg.com/betting-tips/Tennis/3 | Golf/5 | Rugby_League/10 | Rugby_Union/9 | Cricket/7 | Basketball/4 | Baseball/12 | Darts/15 | Snooker/8 | Ice_Hockey/13 | Motor_Racing/14 | Handball/20 | Volleyball/21 | Greyhounds/28 | Gaelic_Football/25 | best-tipsters/eSports/23 | best-tipsters/Aussie_Rules/22',{})
    darts=capture('olbg-darts-sample','https://www.olbg.com/betting-tips/Darts/15','darts','First extracted chunk; partial public-card discovery only.',role='discovery')
    obs(darts,'32325','Gerwyn Price vs Rob Cross. Today 14:45. Gerwyn Price. Win Match 2-way. 16/20 Win Tips. 80%. event_id=32325.',{})
    obs(darts,'32334','Niels Zonneveld vs Cameron Menzies. Today 14:15. Niels Zonneveld. Win Match 2-way. 14/18 Win Tips. 78%. event_id=32334.',{})


if __name__=='__main__':
    seed()
    print(f'Imported {len(FIXTURES)} fixture/event listings from {len(CAPTURES)} captures; never a full-world coverage claim.')
