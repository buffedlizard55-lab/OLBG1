"""Autonomous refresh; all failures are preserved as flags, never synthetic facts.

Run on ordinary GitHub-hosted runners. The restricted development sandbox may not
reach publishers. It never proxies around that restriction or circumvents robots.
"""
import argparse
from datetime import timedelta
import json
from .config import CURRENT,SPORT_INDEX,HORIZON_DAYS
from .common import now_utc,iso,save,official_url
from .http import Fetcher,FetchError
from .adapters import envelope,nhl_schedule,mlb_schedule,nba_schedule,nhl_statistics,mlb_statistics
from .evidence import seal_capture
from .discovery import crawl
from .assemble import assemble


def official_response(response):
    """A request to a league is not evidence if it lands on a discovery host."""
    if not official_url(response.url) or not official_url(response.final_url):
        raise FetchError('Official source redirected outside verified publisher list')
    return response


def refresh(directory=CURRENT,timeout=10,probe=True):
    at=now_utc();first=at.date().isoformat();last=(at.date()+timedelta(days=HORIZON_DAYS-1)).isoformat()
    prior=(at.date()-timedelta(days=1)).isoformat();season=at.year
    fetch=Fetcher(directory/'raw',timeout=timeout)
    output={'started_at':iso(at),'fixtures':[],'statistics':[],'successful_feeds':[],
            'replace_fixture_dates':{},'replace_stat_scopes':[], 'attempts':[]}
    # Raw evidence is latest-run only, bounded by fixed sources/crawl limit. Old
    # tool imports have immutable separate IDs and are not silently restamped.
    for path in (directory/'raw').glob('*.body'):path.unlink()
    for path in (directory/'evidence').glob('http-*.json'):path.unlink()
    specs=[
        ('http-nhl-schedule','ice-hockey','nhl',f'https://api-web.nhle.com/v1/schedule/{first}',nhl_schedule,()),
        ('http-mlb-schedule','baseball','mlb',f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={prior}&endDate={last}&hydrate=team,venue',mlb_schedule,(season,)),
        ('http-nba-schedule','basketball','nba','https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_1.json',nba_schedule,()),
    ]
    for cid,sport,prefix,url,parser,extra in specs:
        try:
            resp=official_response(fetch.get(url,cid))
            c=envelope(resp,cid,sport,f'{prefix.upper()} schedule {first} through {last}')
            # Full-season NBA feed and MLB range include previous local date
            # to retain still-future UTC overnight starts.
            rows=parser(json.loads(resp.body),c,prior if prefix in ('mlb','nba') else first,last,*extra)
            if not c['complete'] and prefix!='nhl':
                raise ValueError('Schedule did not demonstrate the requested date range')
            save(directory/'evidence'/f'{cid}.json',seal_capture(c))
            output['fixtures']+=rows
            if c['complete']:
                output['successful_feeds'].append(prefix)
            elif prefix=='nhl':
                # NHL's gameWeek sometimes stops before the requested horizon.
                # Replace only the league dates explicitly present, even if a
                # covered date has zero games. Never erase an unseen future day.
                output['replace_fixture_dates']['nhl']=c['covered_dates']
                output['attempts'].append({'url':url,'source_id':cid,'status':'partial',
                    'error':'NHL response did not cover every requested league date; only covered dates supersede old rows. Other rows keep their original expiry.',
                    'at':resp.observed_before})
        except (FetchError,ValueError,TypeError,KeyError) as e:
            output['attempts'].append({'url':url,'source_id':cid,'status':'unverified','error':'Fixture feed not accepted: '+str(e)[:250],'at':iso(now_utc())})
    # A previous NHL league-date can still contain a future UTC start. Read it
    # separately without declaring a successful full-slate replacement on failure.
    cid='http-nhl-overnight';url=f'https://api-web.nhle.com/v1/schedule/{prior}'
    try:
        resp=official_response(fetch.get(url,cid))
        c=envelope(resp,cid,'ice-hockey',f'Previous league-date {prior}; overnight UTC bridge only')
        rows=nhl_schedule(json.loads(resp.body),c,prior,prior)
        save(directory/'evidence'/f'{cid}.json',seal_capture(c));output['fixtures']+=rows
    except (FetchError,ValueError,TypeError,KeyError) as e:
        output['attempts'].append({'url':url,'source_id':cid,'status':'unverified','error':'Overnight bridge not accepted: '+str(e)[:250],'at':iso(now_utc())})
    for cid,sport,comp,url,parser,args in [
        ('http-nhl-standings','ice-hockey','NHL',f'https://api-web.nhle.com/v1/standings/{prior}',nhl_statistics,([r for r in output['fixtures'] if r['sport']=='ice-hockey'],prior)),
        ('http-mlb-standings','baseball','MLB',f'https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season={season}&standingsTypes=regularSeason',mlb_statistics,(season,first)),
    ]:
        try:
            resp=official_response(fetch.get(url,cid))
            # Any successfully retrieved new stats feed replaces its seed scope,
            # including parse errors, to prevent hiding contradictions with a fallback.
            output['replace_stat_scopes'].append(comp)
            c=envelope(resp,cid,sport,comp+' official season records')
            data=parser(json.loads(resp.body),c,*args)
            save(directory/'evidence'/f'{cid}.json',seal_capture(c));output['statistics']+=data
        except (FetchError,ValueError,TypeError,KeyError) as e:
            output['attempts'].append({'url':url,'source_id':cid,'status':'unverified','error':'Stats feed not accepted: '+str(e)[:250],'at':iso(now_utc())})
    if probe:
        # Checking a landing page is NOT field verification. Unsupported adapters
        # are surfaced, not green ticks or claims of zero fixtures.
        for sport,meta in SPORT_INDEX.items():
            if sport in ('baseball','ice-hockey','basketball'):continue
            url=meta['official_url']
            try:
                resp=official_response(fetch.get(url,'probe-'+sport))
                output['attempts'].append({'url':url,'source_id':'probe-'+sport,'sport':sport,'status':'read / unparsed',
                    'http_status':resp.status,'at':resp.observed_before,'error':'No schema-validated continuous fixture adapter for this source. No fields promoted.'})
            except FetchError as exc:
                output['attempts'].append({'url':url,'source_id':'probe-'+sport,'sport':sport,
                    'status':'unverified','error':'Source probe not accepted: '+str(exc)[:250],
                    'at':iso(now_utc())})
    discovery=crawl(fetch,max_pages=24)
    save(directory/'discovery.json',discovery)
    output['attempts']+=fetch.log;output['finished_at']=iso(now_utc())
    save(directory/'network.json',output)
    return assemble(now_utc(),directory)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--timeout',type=int,default=10);p.add_argument('--no-probes',action='store_true')
    a=p.parse_args();s=refresh(timeout=a.timeout,probe=not a.no_probes)
    print(json.dumps(s['counts'],indent=2));print('Coverage incomplete by design when a source cannot be confirmed. See network.json.')
