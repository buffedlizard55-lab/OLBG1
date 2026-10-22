"""Small schema-checked adapters for official public NHL, MLB and NBA feeds.

Each normalized field references a retained source observation; raw JSON is saved
by the fetch layer. Incomplete/malformed data raises, not a fabricated zero slate.
"""
import json
from datetime import datetime, timedelta
from .common import iso, parse_time
from .evidence import fixture_from_observation, seal_capture

class SchemaError(ValueError):
    pass


def require(value, kind, context):
    if type(value) is not kind: raise SchemaError(context+' missing or wrong type')
    return value


def text(obj,key):
    v=require(obj.get(key),str,key)
    if not v.strip(): raise SchemaError(key+' empty')
    return v


def number(obj,key):
    n=require(obj.get(key),int,key)
    if n<0: raise SchemaError(key+' negative')
    return n


def envelope(response,cid,sport,scope):
    return {'id':cid,'url':response.url,'final_url':response.final_url,'role':'official','sport':sport,
            'method':'http-json-parser','observed_after':response.observed_after,'observed_before':response.observed_before,
            'http_status':response.status,'raw_response_sha256':response.sha256,'raw_path':f'data/current/raw/{cid}.body',
            'scope':scope,'complete':False,'notes':'Full response retained in deployment evidence artifact; keys validated, not guessed.', 'observations':[]}


def observe(c,oid,raw,values,locator):
    o={'id':str(oid),'locator':locator,'quote':json.dumps(raw,ensure_ascii=False,sort_keys=True), 'values':values}
    c['observations'].append(o)
    return o


def make_row(c,oid,raw,values,locator,prefix):
    o=observe(c,oid,raw,values,locator)
    return fixture_from_observation(c,o,c['sport'],prefix+'-'+str(oid),kind='match')


def normalized_utc(value):
    # Only used with a provider field explicitly named UTC, never with locale text.
    require(value,str,'UTC datetime')
    if value.endswith('Z') or '+' in value[10:]: return iso(parse_time(value))
    if len(value)>=19: return iso(parse_time(value+'Z'))
    raise SchemaError('UTC value is incomplete')


def nhl_schedule(data,c,first,last):
    weeks=require(data.get('gameWeek'),list,'gameWeek')
    if not weeks: raise SchemaError('Empty gameWeek does not demonstrate date coverage')
    rows=[];seen=set(); covered=set()
    for di,day in enumerate(weeks):
        date=text(day,'date');datetime.strptime(date,'%Y-%m-%d')
        games=require(day.get('games'),list,'games')
        if number(day,'numberOfGames')!=len(games): raise SchemaError('NHL reported count mismatch')
        if not first<=date<=last: continue
        covered.add(date)
        for gi,g in enumerate(games):
            gid=number(g,'id')
            if gid in seen: raise SchemaError('Duplicate official NHL game ID')
            seen.add(gid)
            a=require(g.get('homeTeam'),dict,'homeTeam');b=require(g.get('awayTeam'),dict,'awayTeam')
            def name(t):return text(t['placeName'],'default')+' '+text(t['commonName'],'default')
            values={'participant_a':name(a),'participant_b':name(b),'participant_a_id':str(number(a,'id')),
                    'participant_b_id':str(number(b,'id')),'date':date,'start_utc':normalized_utc(text(g,'startTimeUTC')),
                    'venue':g.get('venue',{}).get('default'),'competition':'NHL','season':str(number(g,'season')),
                    'official_status':text(g,'gameState')}
            if g.get('gameScheduleState') not in ('OK',None):
                values['official_status']='postponed'
            rows.append(make_row(c,gid,g,values,f'/gameWeek/{di}/games/{gi}','nhl'))
    expected={(datetime.fromisoformat(first).date()+timedelta(days=n)).isoformat() for n in range((datetime.fromisoformat(last)-datetime.fromisoformat(first)).days+1)}
    c['complete']=expected<=covered
    return rows


def mlb_schedule(data,c,first,last,season):
    days=require(data.get('dates'),list,'dates');rows=[];seen=set();reported=number(data,'totalGames');n=0
    for di,day in enumerate(days):
        date=text(day,'date');datetime.strptime(date,'%Y-%m-%d')
        games=require(day.get('games'),list,'games');n+=len(games)
        for gi,g in enumerate(games):
            if not first<=date<=last: continue
            gid=number(g,'gamePk')
            if gid in seen: raise SchemaError('Duplicate MLB gamePk')
            seen.add(gid)
            teams=require(g.get('teams'),dict,'teams');a=teams['home']['team'];b=teams['away']['team']
            status=require(g.get('status'),dict,'status')
            state=text(status,'detailedState')
            if status.get('abstractGameState')=='Final':state='Final'
            start=None if g.get('startTimeTBD') or status.get('startTimeTBD') else normalized_utc(text(g,'gameDate'))
            values={'participant_a':text(a,'name'),'participant_b':text(b,'name'),'participant_a_id':str(number(a,'id')),
                    'participant_b_id':str(number(b,'id')),'date':date,'start_utc':start,
                    'venue':g.get('venue',{}).get('name'),'competition':'MLB','season':str(season),'official_status':state}
            row=make_row(c,gid,g,values,f'/dates/{di}/games/{gi}','mlb')
            row['notes'].append('Series games can be conditional; no starting-pitcher or lineup assumption.')
            rows.append(row)
    if reported!=n: raise SchemaError('MLB totalGames does not reconcile')
    c['complete']=True  # ONLY this API query, NOT the whole sport.
    return rows


def nba_schedule(data,c,first,last):
    league=require(data.get('leagueSchedule'),dict,'leagueSchedule')
    season=text(league,'seasonYear');days=require(league.get('gameDates'),list,'gameDates')
    if not days:raise SchemaError('Empty NBA season feed')
    rows=[];seen=set()
    for di,day in enumerate(days):
        raw_date=text(day,'gameDate')
        try:date=datetime.strptime(raw_date[:10],'%m/%d/%Y').date().isoformat()
        except ValueError:date=datetime.strptime(raw_date[:10],'%Y-%m-%d').date().isoformat()
        if not first<=date<=last:continue
        for gi,g in enumerate(require(day.get('games'),list,'games')):
            gid=text(g,'gameId')
            if gid in seen:raise SchemaError('Duplicate NBA gameId')
            seen.add(gid);a=g['homeTeam'];b=g['awayTeam']
            def name(t):return (text(t,'teamCity')+' '+text(t,'teamName')).strip()
            state={1:'Scheduled',2:'In Progress',3:'Final'}.get(number(g,'gameStatus'),'unknown')
            values={'participant_a':name(a),'participant_b':name(b),'participant_a_id':str(number(a,'teamId')),
                    'participant_b_id':str(number(b,'teamId')),'date':date,
                    'start_utc':normalized_utc(text(g,'gameDateTimeUTC')) if g.get('gameDateTimeUTC') else None,
                    'venue':g.get('arenaName') or None,'competition':'NBA','season':season,'official_status':state}
            row=make_row(c,gid,g,values,f'/leagueSchedule/gameDates/{di}/games/{gi}','nba')
            if 'TBD' in g.get('gameStatusText','').upper():row['facts']['start_utc']=None;row['field_evidence'].pop('start_utc',None)
            rows.append(row)
    c['complete']=True
    return rows


def nhl_statistics(data,c,fixtures,as_of):
    records=require(data.get('standings'),list,'standings')
    if not records:raise SchemaError('Empty NHL standings')
    identity={r['facts'][side]:r['facts'][side+'_id'] for r in fixtures for side in ('participant_a','participant_b')}
    out=[];seen=set()
    for i,r in enumerate(records):
        team=text(r['teamName'],'default')
        if team not in identity:continue
        if team in seen:raise SchemaError('Duplicate standings team')
        seen.add(team)
        gp,w,l,ot,points=(number(r,k) for k in ('gamesPlayed','wins','losses','otLosses','points'))
        if gp!=w+l+ot or points!=2*w+ot:raise SchemaError('NHL inconsistent W/L/OT/points: '+team)
        if r.get('date')!=as_of:raise SchemaError('NHL standings date differs from request')
        values={'team':team,'team_id':identity[team],'competition':'NHL','season':str(number(r,'seasonId')),'as_of':as_of,
                'games_played':gp,'wins':w,'losses':l,'ot_losses':ot,'points':points}
        oid=identity[team];observe(c,oid,r,values,f'/standings/{i}')
        out.append({'id':c['id']+'-'+oid,'source_id':c['id'],'observation_id':oid,
                    'observed_after':c['observed_after'],'observed_before':c['observed_before'],**values})
    return out


def mlb_statistics(data,c,season,as_of):
    blocks=require(data.get('records'),list,'records')
    if not blocks:raise SchemaError('Empty MLB standings')
    out=[];seen=set()
    for bi,block in enumerate(blocks):
        if str(block.get('season',season))!=str(season):raise SchemaError('Wrong MLB standings season')
        for ri,r in enumerate(require(block.get('teamRecords'),list,'teamRecords')):
            tid=str(number(r['team'],'id'))
            if tid in seen:raise SchemaError('Duplicate MLB team')
            seen.add(tid)
            gp,w,l=(number(r,k) for k in ('gamesPlayed','wins','losses'))
            if gp!=w+l:raise SchemaError('MLB inconsistent record for '+tid)
            if str(r.get('season',season))!=str(season):raise SchemaError('Wrong MLB season')
            values={'team':text(r['team'],'name'),'team_id':tid,'competition':'MLB','season':str(season),'as_of':as_of,
                    'games_played':gp,'wins':w,'losses':l,'runs_scored':number(r,'runsScored'),'runs_allowed':number(r,'runsAllowed'),
                    'period_note':'Regular-season totals, not postseason form'}
            observe(c,tid,r,values,f'/records/{bi}/teamRecords/{ri}')
            out.append({'id':c['id']+'-'+tid,'source_id':c['id'],'observation_id':tid,
                        'observed_after':c['observed_after'],'observed_before':c['observed_before'],**values})
    return out
