"""Fixtures, picks, written predictions, flags and the repo audit for the desk.

Everything here is assembled from saa2881ac_data (captured evidence) and
saa2881ac_model (originated prices). Nothing is typed in by hand except the
prose, and every number in the prose is either taken from the data module or
filled in from the computed price at build time.
"""
from __future__ import annotations

import saa2881ac_data as D
import saa2881ac_model as M

GRADE_RANK = {'High': 3, 'Medium': 2, 'Low': 1, 'none': 0}
MAX_PICKS_PER_SPORT = 10
PREDICTIONS_PER_SPORT = 5
REPO = 'https://github.com/buffedlizard55-lab/OLBG1/blob/90646c82d7bd75d70a8769367d8a76ddb43d9705'
PEER = 'https://github.com/buffedlizard55-lab/OLBG1/blob/4e4603ebf09953f9248dfa77c9e9d4a48548ef36'
AVAILABILITY = ('No official injury report, lineup or team sheet was read for this fixture, '
                'so no player availability is claimed.')

OLBG_BY_ID = {row[7]: row for row in D.DISCOVERY}


def _src(sid):
    s = D.SOURCE[sid]
    return dict(id=sid, url=s['url'], publisher=s['publisher'])


def _olbg(eid):
    row = OLBG_BY_ID.get(eid)
    if not row:
        return None
    return dict(event_id=eid, label=row[3], tip=row[4], market=row[5], share=row[6],
                url=D.SPORT_INDEX[row[0]]['olbg_url'])


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------
def fixtures():
    out = []
    for gid, date, away, home, venue, start in D.NHL_GAMES:
        a, h = D.NHL[away], D.NHL[home]
        out.append(dict(
            key=f'nhl-{gid}', sport='ice-hockey', competition='NHL', event=f"{a['name']} @ {h['name']}",
            home=h['name'], away=a['name'], date=date, start=start, venue=venue,
            sources=[_src('nhl-schedule'), _src('nhl-standings')], olbg=_olbg(D.NHL_ON_OLBG.get(gid)),
            confirmed=True, priced=M.nhl_markets(away, home)))
    out.append(dict(
        key='del-koe-man', sport='ice-hockey', competition='PENNY DEL', event='Adler Mannheim @ Koelner Haie',
        home='Koelner Haie', away='Adler Mannheim', date='2026-10-27', start='2026-10-27 19:00 CET',
        venue='', sources=[_src('del-table')], olbg=_olbg(200100), confirmed=True,
        priced=M.del_markets('Adler Mannheim', 'Koelner Haie')))
    out.append(dict(
        key='mlb-849804', sport='baseball', competition='MLB World Series, Game 3',
        event='Milwaukee Brewers @ Tampa Bay Rays', home='Tampa Bay Rays', away='Milwaukee Brewers',
        date='2026-10-26', start='2026-10-27T00:00Z', venue='Tropicana Field',
        sources=[_src('mlb-ws'), _src('mlb-team-hitting'), _src('mlb-starters')], olbg=None,
        confirmed=True, priced=M.mlb_g3()))
    out.append(dict(
        key='mlb-849803', sport='baseball', competition='MLB World Series, Game 4',
        event='Milwaukee Brewers @ Tampa Bay Rays', home='Tampa Bay Rays', away='Milwaukee Brewers',
        date='2026-10-27', start='2026-10-28T00:00Z', venue='Tropicana Field',
        sources=[_src('mlb-ws')], olbg=None, confirmed=True, priced=None,
        unpriced='The official feed lists no probable starter for either club yet, and the Game 3 '
                 'method needs both starters.'))
    for key, event, rnd, note, a, b, seeds, sid, eid in D.TENNIS:
        priced = M.tennis_markets(a, b)
        reason = None
        if priced is None:
            outside = [p for p in (a, b) if D.ATP[p] is None]
            reason = (', '.join(outside) + ' sits outside the top 150 on the ATP list that was read, '
                      'so no exact ranking-points figure is available and the match is not priced.')
        out.append(dict(
            key=key, sport='tennis', competition=f'{event}, {rnd}', event=f'{a} v {b}', home=a, away=b,
            date='2026-10-26' if 'Mon 26 Oct' in note else '', start=note, venue='', seeds=seeds,
            sources=[_src(sid), _src('atp-rankings')], olbg=_olbg(eid), confirmed=True,
            priced=priced, unpriced=reason))
    for mid, date, time, home, away, eid in D.EHF_GAMES:
        url = f'https://ehfcl.eurohandball.com/men/2026-27/matches/details/{mid}/{D.EHF_SLUGS[mid]}/'
        out.append(dict(
            key=f'ehf-{mid}', sport='handball', competition=f'EHF Champions League, Group {D.EHF[home][0]}',
            event=f'{home} v {away}', home=home, away=away, date=date, start=f'{date} {time} CET', venue='',
            sources=[dict(id='ehf-match', url=url, publisher='EHF'), _src('ehf-cl')], olbg=_olbg(eid),
            confirmed=True, priced=M.handball_markets(home, away)))
    for key, home, away, label, eid in D.LVF_GAMES:
        out.append(dict(
            key=key, sport='volleyball', competition='Serie A1 Tigotà (women)', event=f'{home} v {away}',
            home=home, away=away, date='', start=f'OLBG label: {label}', venue='',
            sources=[_src('lvf-table')], olbg=_olbg(eid), confirmed=False,
            priced=M.volleyball_markets(home, away)))
    out.append(dict(
        key='f1-mexico', sport='motor-racing', competition='Formula 1 World Championship',
        event='Mexico City Grand Prix', home='', away='', date='', start='OLBG label: 01 Nov 15:00',
        venue='', sources=[_src('f1-races')], olbg=_olbg(914), confirmed=True, priced=M.f1_markets()))
    for eid, (icc_id, url) in D.ICC_MATCHES.items():
        row = OLBG_BY_ID[eid]
        out.append(dict(
            key=f'icc-{icc_id}', sport='cricket', competition=row[2], event=row[1], home='', away='',
            date='', start=f'OLBG label: {row[3]}', venue='',
            sources=[dict(id='icc-match', url=url, publisher='ICC')], olbg=_olbg(eid), confirmed=True,
            priced=None, unpriced='The ICC fixture page confirms the match, but the ICC team-rankings table '
                                  'rendered empty, so no official rating was available to price it.'))
    return out


# --------------------------------------------------------------------------
# Picks: always back the side we make the winner.
# --------------------------------------------------------------------------
def _winner_pick(fx):
    markets = fx['priced']['markets']
    main = markets[0]
    fav = max((o for o in main['outcomes'] if o['name'] != 'Draw'), key=lambda o: o['prob'])
    side = fav['name'].rsplit(' win', 1)[0]
    chosen, market = fav, main
    if not M.in_band(fav['price']):
        for m in markets[1:]:
            for o in m['outcomes']:
                if o['name'].startswith(side + ' -'):
                    chosen, market = o, m
    return [(chosen, market)]


def _pick_rows(fx):
    if fx['sport'] == 'motor-racing':
        win, team = fx['priced']['markets']
        return [(win['outcomes'][0], win), (team['outcomes'][0], team)]
    return _winner_pick(fx)


def picks(fixture_list):
    out = []
    for fx in fixture_list:
        if not fx.get('priced'):
            continue
        for o, m in _pick_rows(fx):
            g = M.grade(o['prob'])
            if g == 'none':
                continue
            capped = False
            if not fx['confirmed'] and GRADE_RANK[g] > GRADE_RANK['Low']:
                g, capped = 'Low', True
            out.append(dict(
                id=f"{fx['key']}-{m['key']}", fixture=fx['key'], sport=fx['sport'], event=fx['event'],
                competition=fx['competition'], start=fx['start'], selection=o['name'], market=m['name'],
                prob=o['prob'], price=o['price'], price_text=M.fmt(o['price']), grade=g, capped=capped,
                source=fx['sources'][0]['url']))
    kept = []
    for slug in D.SPORT_INDEX:
        rows = sorted((p for p in out if p['sport'] == slug),
                      key=lambda p: (-GRADE_RANK[p['grade']], -p['prob']))
        kept.extend(rows[:MAX_PICKS_PER_SPORT])
    return kept


# --------------------------------------------------------------------------
# Written predictions. {price} and {pct} are filled from the pick itself.
# --------------------------------------------------------------------------
PROSE = {
    'nhl-2026020185-ml':
        'New York Rangers to beat Los Angeles at Madison Square Garden. The Rangers are a perfect 6-0-0 at '
        'home, outscoring visitors 29-10, although they arrive on a two-game losing run. The Kings are 2-5-2, '
        'have scored only 21 goals in nine games while allowing 32, and the NHL schedule has them in Chicago '
        'the following night. We set the Rangers at {pct}, a fair {price}.',
    'nhl-2026020197-ml':
        'Anaheim Ducks to beat Vancouver at Honda Center. Vancouver are 2-10-1 with 60 goals against in 13 '
        'games and have taken one point from their last ten (0-9-1), the current skid running to four. '
        "Anaheim's own home form is weak at 1-3-0, which is the reason the number stops at {price} ({pct}) "
        'instead of going shorter.',
    'nhl-2026020187-ml':
        'Edmonton Oilers over Detroit at Rogers Place. Edmonton are 8-2-1 with 49 goals in 11 games and won '
        'eight of their last ten. Detroit are 4-4-3 and have one regulation-or-overtime win in four road '
        "trips. Edmonton's home split (3-2-1, 22 scored, 26 allowed) is the soft spot, so we hold the "
        'Oilers at {pct}, fair {price}.',
    'nhl-2026020193-ml':
        'Dallas Stars to beat New Jersey at American Airlines Center. Dallas have conceded 20 goals in 11 '
        'games, the fewest in the league table read on 26 October, and bring a five-game winning streak. '
        'New Jersey are 6-2-0 at home but 1-2-0 away, with just seven road goals. Our fair line on Dallas '
        'is {price}, or {pct}.',
    'nhl-2026020196-ml':
        "Vegas Golden Knights over Ottawa at T-Mobile Arena. Vegas are 5-2-0 at home and have 47 goals "
        "overall. Ottawa's 8-4-0 record looks stronger than its plus-four goal difference, and their last "
        'ten games finished dead level at 31 goals for and against. Medium confidence at {price} ({pct}): '
        'the edge is real but not wide.',
    'del-koe-man-ml':
        'Adler Mannheim to win in Cologne on Tuesday night. Mannheim are fifth in the PENNY DEL on 23 points '
        'from 12 games and have allowed 29 goals; Koelner Haie, seventh on 19, have conceded 45 in the same '
        'number of games. Cologne do score freely (45 goals), so we expect goals as well and price '
        'Mannheim at {pct}, fair {price}.',
    'bas-djo-hum-ml':
        'Novak Djokovic to beat Ugo Humbert in the Basel first round. Djokovic is the fourth seed, entered '
        'on a wildcard, and holds 3,090 points at No. 12 against Humbert\'s 1,270 at No. 38. That ratio puts '
        'Djokovic at {pct}, a fair {price}. The order of play for this match was not yet out when we read '
        'it, so the day shown is OLBG\'s label.',
    'vie-van-tie-ml':
        "Learner Tien to beat Luca Van Assche in Vienna's late session, not before 20:00 CET. Tien is No. 18 "
        'on 2,345 points, more than double Van Assche\'s 1,105 at No. 46. The points split makes Tien {pct}, '
        'a fair {price}. OLBG carried no tip on this match, so there is no crowd view to compare against.',
    'bas-tab-jod-ml':
        'Rafael Jodar, the Basel third seed, to beat Alejandro Tabilo. Jodar is No. 11 with 3,234 points; '
        'Tabilo is No. 30 with 1,565. The most-tipped OLBG side is Tabilo, on two of four tips, which runs '
        'against a ranking gap of that size. We make Jodar {pct}, fair {price}.',
    'vie-fer-fea-ml':
        'Arthur Fery to beat qualifier Jacob Fearnley on the Glaubandich Court at 17:30 CET. Fery is No. 35 '
        'with 1,406 points and Fearnley No. 86 with 686, close to a two-to-one edge on the ATP list. That '
        'converts to {pct}, a fair {price}. The single OLBG tip on this match backed Fearnley.',
    'vie-dar-arn-ml':
        'Luciano Darderi over Matteo Arnaldi in an all-Italian Vienna opener, second on the Glaubandich '
        'Court. Darderi is No. 23 on 2,160 points and Arnaldi No. 36 on 1,311. We price Darderi at {pct}, '
        'fair {price}; a straight-sets win on its own is less likely than not, so the match result is the '
        'cleaner way to back him.',
    'ehf-202711020101046-1x2':
        'OTP Bank-PICK Szeged to win away at IFK Kristianstad. Kristianstad have lost all five group games '
        'and conceded 197 goals, the most of any club in the competition; Szeged are 1-2-2 but have a '
        'positive goal difference (172-169). We make a Szeged win in regulation {pct}, fair {price}, with '
        'the draw priced as its own outcome.',
    'ehf-202711020101016-1x2':
        'Orlen Wisla Plock to beat HBC Nantes in Group B, where the top three all have six points. Plock have '
        'the best defence in the group, 136 conceded in five games, and the best goal difference at plus '
        'five; Nantes are minus one. Home court adds to that, giving {pct} and a fair {price}. Most OLBG '
        'tipsters chose the tie.',
    'ehf-202711020101036-1x2':
        'HC Zagreb to win at RK Celje. Celje are bottom of Group C with no points from five games and 188 '
        'goals against; Zagreb have two wins and four points. The line already credits Celje with home court '
        'and still makes Zagreb {pct}, fair {price}. This is Medium rather than High because Zagreb sit on '
        'minus 12 themselves.',
    'ehf-202711020101026-1x2':
        'Paris Saint-Germain to beat Aalborg in the Group C top-two game. Both clubs are plus 25 on goal '
        'difference, but PSG have scored 182 to Aalborg\'s 170 and they are at home. Aalborg lead the group '
        'unbeaten at 4-1-0, which is why this is only Medium at {price} ({pct}).',
    'ehf-202711020101040-1x2':
        'Sporting CP to win at GOG in the Group D top-of-table meeting. Sporting have 191 goals in five '
        'games, the highest tally in the competition, and are unbeaten at 4-1-0; GOG are 3-1-1 with a '
        'thinner margin of plus six. GOG\'s home floor keeps this Low at {pct}, fair {price}. GOG is the '
        'most-tipped side on OLBG.',
    'ehf-202711020101055-1x2':
        'Montpellier to beat Dinamo Bucuresti at home, a meeting of the bottom two in Group E. Montpellier '
        'are 1-0-4 but score more, 150 goals to 134; Dinamo concede fewer, 145 to 165. Our number is a '
        'narrow {pct}, fair {price}, so treat it as a Low-confidence lean rather than a strong opinion.',
    'mlb-849804-ml':
        'Milwaukee Brewers to win Game 3 at Tropicana Field and go 3-0 up in the World Series, after 3-2 and '
        '5-4 wins at home. Robert Gasser starts for Milwaukee with a 3.87 ERA over 20 starts; Freddy Peralta '
        'starts for Tampa Bay with 4.42 over 32, split between the Mets and the Rays. His ten Rays starts '
        'came at 3.25, which is why we stop at Medium: {pct}, fair {price}.',
    'lvf-con-val-sets':
        'Imoco Conegliano to beat Savio Vallefoglia 3-0 or 3-1. Conegliano are 4-0 without dropping a set '
        '(12-0) and have won 58 percent of rally points; Vallefoglia are also 4-0 but have lost four sets '
        'and won under 52 percent of points. The outright winner price is too short for the band, so the '
        'set handicap carries the view at {price}. It is graded Low only because the match date is not on '
        'an official page.',
    'lvf-oma-ber-ml':
        'Omag Consolini Volley 1907, listed as Marignano on OLBG, to edge Volley Bergamo at home. On rally '
        'points the two are almost level, 49.8 percent for Omag and 50.4 for Bergamo, while the records '
        'read 1-3 and 3-1. Home court tips our number to Omag at {pct}, fair {price}; this is a lean, and '
        'the date comes from OLBG alone.',
    'f1-mexico-team':
        'A Mercedes driver to win the Mexico City Grand Prix. Mercedes have won 12 of the 18 Grands Prix run '
        'in 2026, nine for Kimi Antonelli and three for George Russell, including Austin on 25 October. A '
        'smoothed share of wins gives the team {pct}, a fair {price}. No grid or qualifying result existed '
        'when we read, so this rests on season results alone.',
    'f1-mexico-win':
        'Kimi Antonelli to win in Mexico City. He has won nine of the 18 races this season, exactly half, '
        'and took the most recent one in the United States. After shrinking that record toward the rest of '
        'the field we make him {pct}, fair {price}. Low confidence, because a single driver rarely clears '
        'even money before qualifying.',
}


def predictions(pick_list):
    out = []
    for slug in D.SPORT_INDEX:
        rows = [p for p in pick_list if p['sport'] == slug][:PREDICTIONS_PER_SPORT]
        for p in rows:
            text = PROSE[p['id']].format(price=p['price_text'], pct=f"{p['prob'] * 100:.0f}%")
            out.append(dict(pick=p['id'], sport=slug, event=p['event'], selection=p['selection'],
                            market=p['market'], grade=p['grade'], price_text=p['price_text'],
                            text=text, availability=AVAILABILITY, source=p['source']))
    return out


# --------------------------------------------------------------------------
# Flags (published on flagged.html, each with a source to recheck)
# --------------------------------------------------------------------------
def flags():
    S = D.SOURCE
    f = [
        ('basketball', 'source', 'No official NBA game list for 26 October could be read: the cdn.nba.com '
         'scoreboard and schedule JSON returned HTTP 500, stats.nba.com did not answer, and nba.com/games is '
         'rendered in the browser. OLBG listed no basketball market either. No basketball fixture or pick is '
         'published.', S['nba-games']['url']),
        ('golf', 'coverage', 'OLBG returned "No tips found." on the golf hub. The PGA TOUR schedule page was read '
         'but no field or player figure was captured, so nothing is priced.', S['pga-schedule']['url']),
        ('snooker', 'coverage', 'OLBG returned "No tips found." on the snooker hub and no WST draw was read.',
         S['olbg-snooker']['url']),
        ('darts', 'coverage', 'OLBG listed only the 2027 PDC World Championship outright (Luke Littler most '
         'tipped). Earlier desks recorded a cookie wall on pdc.tv; no darts match is priced.', S['olbg-darts']['url']),
        ('rugby-union', 'coverage', 'OLBG listed only the Six Nations 2027 outright. No rugby union match '
         'market existed to price.', S['olbg-rugby-union']['url']),
        ('rugby-league', 'coverage', 'OLBG listed three 2027 outrights (State of Origin, Super League, NRL) and '
         'no match market.', S['olbg-rugby-league']['url']),
        ('gaelic', 'source', 'OLBG lists two club football handicaps for 1 November (Cork and Limerick club '
         'competitions). No county board fixture page was read, so the rows are discovery only and unpriced.',
         S['olbg-gaelic-football']['url']),
        ('greyhounds', 'source', 'OLBG listed one Monmore race (3:19) with one tip on Tullymurry Skies. No GBGB '
         'racecard was read, so trap, form and price are blank.', S['olbg-greyhounds']['url']),
        ('cricket', 'source', 'Four OLBG cricket fixtures were matched to ICC match pages, but the ICC '
         'team-rankings table rendered empty, so there is no official rating to price from. The WBBL rows '
         'were not matched to any official page.', S['icc-fixtures']['url']),
        ('tennis', 'capture', 'Holger Rune, Lukas Neumayer, Stan Wawrinka, Dominic Stricker and Mika Brunold are '
         'outside the top 150 on the ATP list that was read (rank 150 holds 378 points). Their exact points are '
         'not on that list, so their matches are not priced. Wawrinka v Lehecka sits in the half of the Basel '
         'draw that was not captured, so it is listed by OLBG only.', S['atp-rankings']['url']),
        ('tennis', 'time', 'The Basel order of play for Djokovic v Humbert and Tabilo v Jodar was not yet '
         'published at read time. Both matches are confirmed in the official draw; the date column is blank.',
         S['atp-basel-draw']['url']),
        ('tennis', 'coverage', 'Every WTA, ITF and Challenger row on OLBG is listed unpriced: no official draw '
         'or ranking list for those events was read this session.', S['olbg-tennis']['url']),
        ('volleyball', 'time', 'Omag Consolini v Bergamo (27 Oct on OLBG) and Conegliano v Vallefoglia (28 Oct '
         'on OLBG) involve clubs with one game fewer than the rest, which fits rescheduled fixtures, but no '
         'official LVF page read this session gave their dates. Both are priced from the official table and '
         'their grade is capped at Low.', S['lvf-table']['url']),
        ('volleyball', 'naming', 'OLBG names the LVF club "Marignano"; the official table calls it "Omag '
         'Consolini Volley 1907". The match is treated as the same fixture on that basis.', S['lvf-table']['url']),
        ('volleyball', 'source', 'tauronliga.pl/table.html, the women\'s TAURON Liga address, returned tiles naming '
         'men\'s PlusLiga clubs (for example Slepsk Suwalki). No women\'s table was extracted, so the three Polish '
         'women\'s rows on OLBG are unpriced.', S['tauron-liga']['url']),
        ('volleyball', 'coverage', 'Brazilian Superliga and Austrian AVL rows on OLBG are unpriced: no official '
         'league table was read for them.', S['olbg-volleyball']['url']),
        ('ice-hockey', 'capture', 'The PENNY DEL table that was read stops at 13 clubs; the Iserlohn Roosters row '
         'was cut off. The league scoring average used for the DEL price is therefore built from 13 clubs.',
         S['del-table']['url']),
        ('ice-hockey', 'source', 'Danish Metal Ligaen, Swedish SHL and Finnish Liiga rows on OLBG are unpriced: '
         'shl.se returned no table and liiga.fi returned 404.', S['olbg-ice-hockey']['url']),
        ('baseball', 'method', 'The league runs-per-game baseline (4.64) comes from the 11 clubs on the first '
         'page of the MLB team-stats read, not all 30.', S['mlb-team-hitting']['url']),
        ('baseball', 'irregularity', 'Freddy Peralta\'s 2026 line is split: 22 starts for the Mets (4.99 ERA) and '
         '10 for the Rays (3.25 ERA). The Game 3 price uses his full-season figure.', S['mlb-peralta']['url']),
        ('baseball', 'coverage', 'The OLBG baseball hub page read here showed no tips, so the MLB rows carry no OLBG '
         'comparison. The peer desk 103ea76b reports the World Series game on an OLBG MLB sub-hub that this desk '
         'did not read.', S['olbg-baseball']['url']),
        ('handball', 'discovery', 'Ten of the twelve EHF Champions League rows on OLBG show "Tie" as the most-tipped '
         'money-line outcome. That is reproduced as published and not used as a signal.', S['olbg-handball']['url']),
        ('handball', 'naming', 'OLBG lists "Skanderborg v Barcelona"; the official EHF fixture is SAH-Aarhus v '
         'Barca (match 202711020101054).', S['ehf-cl']['url']),
        ('motor-racing', 'source', 'The formula1.com drivers page returned names without a points column, and no '
         'Mexico City grid existed at read time. The race-winner price uses 2026 race wins only. The race date '
         'and time are OLBG\'s label.', S['f1-drivers']['url']),
        ('all', 'capture', 'No injury report, lineup or team sheet was read for any fixture, so no written '
         'prediction names an injured or returning player.', S['nhl-standings']['url']),
        ('all', 'time', 'OLBG prints relative labels such as "Today 19:07" in US Eastern time; the NHL feed gives '
         '23:00Z (19:00 ET) for the same Rangers game, so OLBG times are never used as start times.',
         S['nhl-schedule']['url']),
    ]
    return [dict(id=f'F{i:02d}', sport=s, kind=k, text=t, url=u) for i, (s, k, t, u) in enumerate(f, 1)]


# --------------------------------------------------------------------------
# Repo review: concrete findings with line links at the base commit.
# --------------------------------------------------------------------------
def audit():
    a = [
        ('high', 'pipeline/build.py', 'L261-L266',
         'The front-door banner is a hard-coded paragraph about the 25 October desk, including literal counts '
         '("Nine fixtures", "three graded picks"). Nothing ties those words to data/a394f91e/desk.json, so they '
         'go stale the moment a new desk lands. This desk repoints the banner, but the text is still literal.'),
        ('high', 'pipeline/build.py', 'L265',
         'The banner says "the twelve with no priced match". The a394f91e desk priced two sports '
         '(basketball and ice hockey), which leaves thirteen, and its own flag F22 says fourteen. Three '
         'different numbers describe the same desk.'),
        ('medium', 'scripts/sa394f91e_build.py', 'L203',
         'Flag F22 of the 25 October desk opens "Fourteen of the fifteen brief sports have no priced match" and '
         'then says "for thirteen sports" in the same sentence. Only thirteen is consistent with its fixtures.'),
        ('high', 'pipeline/build.py', 'L281-L288',
         'The canonical summary hard-codes "Six high-confidence picks are live for the next two days" and '
         '"ice hockey and baseball" next to computed KPIs. The cron in current-pages.yml rebuilds this page every '
         'three hours, so the sentence can contradict the KPI tiles directly under it.'),
        ('medium', 'pipeline/build.py', 'L37',
         'ARCHIVE labels carry literal counts ("9 official fixtures ... 22 flags"). They are never reconciled '
         'with the desk data they describe.'),
        ('medium', 'pipeline/build.py', 'L349',
         'archive_panel silently drops any ARCHIVE entry whose file is missing (`if (ROOT / d).is_file()`), so a '
         'typo in a desk path removes it from the front door without any error.'),
        ('medium', 'pipeline/build.py', 'L859-L862',
         'The artifact copy loop also skips missing desk folders with `continue`. Combined with the line above, a '
         'broken ARCHIVE entry fails silently in both places.'),
        ('high', 'pipeline/validate.py', 'L293',
         'validate_desk only walks manifest["pages"], the root pages. Desk subfolders such as a394f91e/ are copied '
         'into the artifact but never checked for broken links, missing sources or empty tables by the canonical '
         'gate; each desk relies on its own optional script.'),
        ('medium', 'pipeline/validate.py', 'L334',
         'The unregistered-HTML check globs only site/*.html, so stray pages inside desk subfolders are never '
         'caught.'),
        ('low', '.github/workflows/current-pages.yml', 'L43',
         'CI runs `python -m pipeline.refresh` against live sites before building, so the same commit can build '
         'different pages depending on which publishers answer within 10 seconds.'),
        ('low', 'pipeline/config.py', 'L40-L67',
         'PUBLISHERS, which feeds OFFICIAL_HOSTS in pipeline/validate.py line 161, lists www.legavolley.it (the '
         "men's Lega Pallavolo) but not legavolleyfemminile.it, and no German ice hockey host such as "
         'penny-del.org. Women\'s Serie A1 and DEL rows could not pass the canonical source check even when the '
         'link is the official league page.'),
        ('low', 'repository root', '',
         '79 eight-character session folders contain an index.html but only 20 of them are registered in ARCHIVE. '
         'The other 59 (for example 0c9bc692/, 1707d752/, 2360a617/) are committed but are neither copied into '
         'the Pages artifact nor linked from the front door.'),
    ]
    peer = [
        ('medium', 'data/103ea76b/desk.json', 'L1035-L1050',
         'The peer 26 October desk (103ea76b, merged as PR #300 while this desk was being built) prices World '
         'Series Game 5 and grades Tampa Bay +1.5 High at -167. The official MLB schedule marks Game 5 "if '
         'necessary"; Milwaukee lead 2-0, so the game only happens if Tampa Bay win at least once first. The '
         'conditional status is not shown next to the pick.'),
        ('medium', 'data/103ea76b/desk.json', 'L902',
         'Games 3, 4 and 5 on that desk carry the identical probability (0.625908) and price, so the published '
         'Game 3 probable starters (Gasser and Peralta, both on the official feed) do not enter its price.'),
        ('medium', 'data/103ea76b/desk.json', 'L1663',
         'NBA picks there are graded High (for example Oklahoma City -177) on fixtures whose start time is blank '
         'because no official schedule was readable; fixture existence rests on the OLBG listing plus the NBA '
         'standings. This desk read the same gap and issued no basketball pick.'),
        ('low', '103ea76b/sports/baseball.html', 'L15',
         'The baseball page says "No price today" directly above a picks table that lists a priced World Series '
         'pick.'),
    ]
    out = []
    for i, (sev, path, lines, text) in enumerate(a, 1):
        if path == 'repository root':
            url = 'https://github.com/buffedlizard55-lab/OLBG1/tree/90646c82d7bd75d70a8769367d8a76ddb43d9705'
        else:
            url = f'{REPO}/{path}' + (f'#{lines}' if lines else '')
        out.append(dict(id=f'R{i:02d}', severity=sev, path=path, lines=lines, text=text, url=url))
    for i, (sev, path, lines, text) in enumerate(peer, len(a) + 1):
        out.append(dict(id=f'R{i:02d}', severity=sev, path=path, lines=lines, text=text,
                        url=f'{PEER}/{path}#{lines}'))
    return out
