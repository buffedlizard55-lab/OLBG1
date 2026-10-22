"""Read every tracked legacy JSON and Python file; inventory every fixture/price/prose row.

This is a structural audit, not live recertification. JSON pointers and source-file
lines identify each observed claim. A URL in an old row is never treated as proof.
The current evidence import is independently read and separately published.
"""
import ast
from collections import Counter
from pathlib import Path
import json
import re
import subprocess
from .common import load,save,digest,official_url,parse_time,iso
from .config import ROOT,CURRENT,SPORT_INDEX

REPO='https://github.com/buffedlizard55-lab/OLBG1'


def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for v in value.values():yield from strings(v)
    elif isinstance(value,list):
        for v in value:yield from strings(v)


def pointers(value,path=''):
    if isinstance(value,dict):
        yield path,value
        for k,v in value.items():yield from pointers(v,path+'/'+str(k).replace('~','~0').replace('/','~1'))
    elif isinstance(value,list):
        for i,v in enumerate(value):yield from pointers(v,path+'/'+str(i))


def kind(row):
    if ('home' in row and 'away' in row) or ('team1' in row and 'team2' in row) or ('player1' in row and 'player2' in row):
        return 'fixture / price book'
    if 'match_id' in row and ('text' in row or 'prediction' in row):return 'prediction'
    if 'id' in row and 'sport' in row and any(x in row for x in ('event','match','participants','markets','pick')):return 'event / price book'
    return None


def sport_slug(value):
    s=str(value or '').lower().replace('_','-').replace(' ','-')
    return {'icehockey':'ice-hockey','australian-rules':'aussie-rules','rugby':'rugby-union','gaelic-football':'gaelic-football','e-sports':'esports'}.get(s,s)


def line_for(text,field,value,used):
    needle=re.escape(json.dumps(field))+r'\s*:\s*'+re.escape(json.dumps(value,ensure_ascii=False))
    matches=list(re.finditer(needle,text))
    # Same records can be aliased in JSON; track occurrences rather than claiming
    # that the first line matches all aliases. JSON pointer is the exact locator.
    for m in matches:
        if m.start() not in used:
            used.add(m.start());return text.count('\n',0,m.start())+1
    return None


def build_audit(at):
    tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    files=[];rows=[];hashes={};python_errors=[]
    for rel in tracked:
        path=ROOT/rel
        if rel.startswith(('data/current/','pipeline/','tests/pipeline/','archive/root-20261022/')) or not path.is_file():continue
        if path.suffix not in ('.json','.py'):continue
        raw=path.read_bytes();hashes[rel]=digest(raw)
        entry={'path':rel,'sha256':digest(raw),'line_count':len(raw.splitlines()),'bytes':len(raw),'status':'parsed','records':0}
        try:
            text=raw.decode('utf-8')
            if path.suffix=='.py':ast.parse(text,filename=rel)
            else:
                doc=json.loads(text);used=set();seen_payload={}
                for pointer,record in pointers(doc):
                    rkind=kind(record)
                    if not rkind:continue
                    payload=digest(record)
                    identifier=record.get('id',record.get('match_id'))
                    field='id' if 'id' in record else 'match_id'
                    line=line_for(text,field,identifier,used) if identifier is not None else None
                    sport=sport_slug(record.get('sport'))
                    urls=sorted({s for s in strings(record) if s.startswith('https://') and official_url(s)})
                    fallback=SPORT_INDEX.get(sport,{}).get('official_url')
                    observed_start=record.get('start_utc')
                    elapsed=None
                    if observed_start:
                        try:elapsed=parse_time(observed_start)<=at
                        except (ValueError,TypeError):pass
                    label=record.get('home',record.get('team1',record.get('player1','')))
                    away=record.get('away',record.get('team2',record.get('player2','')))
                    if away:label=str(label)+' vs '+str(away)
                    if not label:label=str(record.get('selection',record.get('event',record.get('match',identifier or ''))))
                    alias=seen_payload.get(payload)
                    seen_payload.setdefault(payload,pointer)
                    row={'file':rel,'pointer':pointer,'line':line,'kind':rkind,'record_id':identifier,
                         'observed_label':label,'sport':sport,'prior_status':record.get('status'),
                         'observed_start_utc':observed_start,'stored_start_elapsed':elapsed,
                         'current_verification':'unverified — historical claim not promoted',
                         'accepted_participant_a':None,'accepted_participant_b':None,'accepted_start_utc':None,
                         'approved_selection':None,'approved_confidence':None,'approved_prediction':None,
                         'official_urls':urls,'lookup_url':fallback,'alias_of':alias,
                         'repository_url':f'{REPO}/blob/{baseline}/{rel}'+(f'#L{line}' if line else ''),
                         'notes':['Source link presence is not retained evidence; this row has NOT been re-certified.']}
                    if not urls:row['notes'].append('No direct official URL found in this record; references may be indirect. A lookup link is not verification.')
                    if elapsed:row['notes'].append('Stored start elapsed; actual result/current status not inferred.')
                    rows.append(row);entry['records']+=1
        except (ValueError,SyntaxError,UnicodeError) as e:
            entry['status']='needs review';entry['error']=str(e);python_errors.append(rel)
        files.append(entry)
    findings=make_findings(baseline)
    output={'as_of':iso(at),'baseline':baseline,'scope':'Every tracked legacy JSON and Python file; every detected fixture, price-book and prediction object. Source semantics NOT re-certified.',
            'counts':{'files':len(files),'json_files':sum(x['path'].endswith('.json') for x in files),
                      'python_files':sum(x['path'].endswith('.py') for x in files),'parse_errors':len(python_errors),
                      'row_occurrences':len(rows),'non_alias_rows':sum(r['alias_of'] is None for r in rows),
                      'start_elapsed_occurrences':sum(r['stored_start_elapsed'] is True for r in rows),
                      'findings':len(findings)},
            'files':files,'rows':rows,'findings':findings,'input_sha256':digest(hashes)}
    save(CURRENT/'audit.json',output)
    return output


def make_findings(baseline):
    nhl='https://www.nhl.com/standings/2026-10-21/wildcard'
    el='https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/'
    mlb='https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason'
    findings=[]
    def add(n,severity,title,detail,source,path=None,needle=None,status='needs review'):
        line=None
        if path and needle:
            txt=(ROOT/path).read_text()
            if needle in txt:line=txt[:txt.index(needle)].count('\n')+1
        findings.append({'id':f'F-257E-{n:02d}','severity':severity,'status':status,'title':title,'detail':detail,
                         'official_url':source,'file':path,'line':line,
                         'repository_url':f'{REPO}/blob/{baseline}/{path}'+(f'#L{line}' if line else '') if path else None})
    add(1,'high','Competing snapshots are not one current match list',
        'Historical desks contain different windows, IDs, verification assertions and prices. They remain archives; none is imported as verified merely because a status string says so. The canonical dataset has its own evidence and coverage limits.',
        'https://www.olbg.com/betting-tips','data/fixtures.json','"retrieved"','resolved in canonical site')
    add(2,'high','Missing ratings can create a spurious legacy edge',
        'v3 substitutes 58.0 for missing ratings and subtracts it from the other side. A one-sided measurement is not a measured matchup edge. Canonical model refuses any price when either required record is missing.',
        'https://www.atptour.com/en/rankings/singles','scripts/v3_model.py','rh, dh = _rating','resolved in canonical model; archive retained')
    add(3,'high','Published clocks must not be guessed as UTC',
        'OLBG relative Today/Tomorrow clocks, WST clocks without timezone and F1 My time/Track time are not exact UTC. Canonical UTC cells stay blank unless explicitly published or deterministically converted from an explicit offset.',
        'https://www.formula1.com/en/racing/2026/united-states',status='resolved by blank-and-flag')
    add(4,'high','High confidence has no measured calibration here',
        'Legacy thresholds and labelled constants do not establish predictive reliability. The new independent model has no temporal out-of-sample evaluation; it issues Low experimental estimates only, not unsupported High claims.',
        nhl,'scripts/model.py','total=6.5')
    add(5,'medium','Legacy probability/price clipping changes the estimate',
        'The original to_odds clamps both probabilities and odds. Canonical fair prices use 1/p without clamping, with a separately derived American display and an unrounded target-band test.',
        mlb,'scripts/model.py','def to_odds','resolved in canonical model')
    add(6,'high','Static snapshots outlive kickoff',
        'Historical generators can leave scheduled dates and predictions displayed after the stored start. Canonical sources expire after six hours; elapsed starts are not offered as pre-match picks, and the browser rechecks expiry without waiting for a deployment.',
        'https://api-web.nhle.com/v1/schedule/2026-10-22','scripts/build_site.py','def fmt_when','resolved in canonical site')
    add(7,'medium','Fair-price eligibility is not a bookmaker quote',
        '−250 means decimal 1.40; +10000 means 101.00. The fair-probability band is about 0.99%–71.43%. A >70% probability cutoff would admit only a narrow slice, so that is NOT this release’s confidence rule. No bookmaker prices were verified; quote/edge fields stay blank. No alternate is searched to manufacture confidence.',
        'https://www.olbg.com/betting-tips/Darts/15',status='disclosed; quotes unverified')
    add(8,'high','Old NHL record is internally inconsistent',
        'The f71557b5 Boston–Nashville row says Nashville 3-3-2 and 9 points. Three wins plus two overtime losses is 8 points. The freshly read NHL table instead shows 3-2-3, 9 points, 8 games. Old text is not inherited.',
        nhl,'data/f71557b5/fixtures.json','Nashville Predators 3-3-2')
    add(9,'medium','PDC matchup verification incomplete',
        'Inspected PDC extraction chunks returned consent text rather than a usable fixture schedule. OLBG darts cards are discovery only; accepted matchup, start, price and confidence fields remain blank.',
        'https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/')
    add(10,'medium','Previously cited PGA article returns page-not-found text',
        'The facts-and-figures URL could not support the prior claims in this retrieval. The current event date/course are instead checked on the PGA TOUR schedule; fields and golfer predictions are not recovered from the missing article.',
        'https://www.pgatour.com/article/news/latest/2026-10-20/butterfield-bermuda-championship-facts-and-figures-port-royal-golf-course-southampton-2026')
    add(11,'high','EHF schedule publication predates matchday',
        'The retrieved playing-times PDF explicitly says Status: July 29, 2026. The document supports its listed pairings but cannot establish current amendments, availability or form. These listings are unpriced pending a current feed.',
        'https://www.eurohandball.com/media/jqal4wt0/ehfcl-men-2026-27-group-phase-playing-times.pdf')
    add(12,'high','EuroLeague record contradiction quarantined',
        'The Round 7 preview describes Real Madrid as 3-3 overall and 1-4 away. Four road losses cannot fit three total losses in the same scope. The pairing/time remain sourced; Madrid’s rating input and that match price are blank.',
        el)
    add(13,'high','Partial automation is not full multi-sport coverage',
        'Continuous structured adapters currently cover NHL, MLB and NBA schedules. Other official checks are explicit unparsed/partial gaps; cached document extracts expire and are never stamped as refreshed by a failed request. No worldwide completeness claim.',
        'https://www.olbg.com/sitemap-betting-tips.xml')
    add(14,'medium','Respect OLBG crawler restrictions',
        'OLBG robots disallows /api/, hidden JSON storage, and the Python-urllib client. The scheduled collector identifies its library and obeys these restrictions. It does not call hidden endpoints, rotate identities or treat denied access as zero events.',
        'https://www.olbg.com/robots.txt',status='enforced')
    add(15,'medium','Regular-season baseball data is not current postseason form',
        'The MLB inputs are explicitly 2026 regular-season W/L and runs. No probable starters, current lineup, last-match report or postseason adjustment was verified. All six originated market families/lines per game remain Low and experimental.',
        mlb)
    add(16,'medium','Tennis orders of play contain non-exact and retired entries',
        'Followed by and Not before are not exact starts. The Osaka sheet also shows a Ruzic–Day 6-4 0-0 RET entry; it is not offered as an upcoming match. No timezone, tournament name absent from extraction, player form or recent score is inferred from a bracket.',
        'https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf',status='resolved by conservative import')
    add(17,'medium','Volleyball competition identity conflict',
        'The PlusLiga games request redirects to TAURON Liga; the SKRA calendar likewise carries that heading. Two opponent/date listings are retained as document facts, but competition, venue, UTC time and all prices remain blank.',
        'https://www.tauronliga.pl/teams/tour/53/id/61.html')
    add(18,'medium','Field sports require a complete runner model',
        'F1 practice/qualifying/race and golf tournament listings are event cards, not two-sided matches. A complete field, withdrawals and placement/dead-heat rules are required before originating outright or placement prices.',
        'https://www.pgatour.com/schedule')
    return findings

if __name__=='__main__':
    from .common import now_utc
    print(build_audit(now_utc())['counts'])
