"""Join only evidence-backed inputs, calculate prices, and publish explicit gaps."""
from collections import Counter
from copy import deepcopy
from datetime import timedelta
from .common import load, save, now_utc, iso, parse_time, digest
from .config import CURRENT, SPORT_INDEX, SCHEMA_VERSION, HORIZON_DAYS
from .evidence import verify_capture, fixture_state
from .model import originate, MODEL_VERSION, ASSUMPTIONS

COVERAGE_NOTES = {
    'tennis': 'Five official order-of-play PDFs, including doubles. No live-result polling; timezones, rolling starts and many competition headings unconfirmed.',
    'basketball': 'NBA 22 Oct and EuroLeague Round 7 subset. Neither is worldwide basketball coverage. Madrid record conflict excluded from pricing.',
    'golf': 'PGA TOUR event calendar only; other tours, complete fields and matchup markets not captured.',
    'cricket': 'PCB ODI tri-series subset only. No invented format-neutral run baseline; other series need official adapters.',
    'snooker': 'Eight listed Northern Ireland Open ties. Extracted clock has no timezone and does not establish current match status.',
    'rugby-union': 'Seven TOP 14 fixtures only. Other leagues not enumerated. No arbitrary ranking-to-point spread.',
    'rugby-league': 'Visible IRL listings, with men and women separated; load-more pagination prevents a completeness claim.',
    'baseball': 'MLB date-window schedule only, not all baseball leagues. If Necessary or unknown-necessity games are unpriced until eligibility is established. No verified starting pitchers.',
    'ice-hockey': 'NHL subset, not all hockey competitions. Match-winner model includes OT/SO; season goals cannot verify regulation totals.',
    'motor-racing': 'F1 Austin session listings only. Timezone switch is ambiguous; no verified complete runner model.',
    'darts': 'OLBG cards discovered but no official matchup table obtained from inspected PDC extraction. Verified match values blank.',
    'handball': 'EHF July 29 playing-times document, not a current amendment/status feed. No current-form inputs.',
    'volleyball': 'Two club-calendar listings; PlusLiga→TAURON Liga redirect/competition identity unresolved. No price.',
    'aussie-rules': 'One AFLW match centre checked; not the full round. Old ladder values are not inherited.',
    'esports': 'Riot Worlds overview only; no dated head-to-head verified. Participants/date/selection blank.',
    'gaelic-football': 'Three Munster county finals. Hurling and camogie/shinty excluded. Gaelic football treated as a distinct project category.',
    'greyhounds': 'Official GBGB calendar rendered controls without runner cards. Unknown coverage is NOT a zero-race finding.',
}


def assemble(at=None, directory=CURRENT, *, write=True):
    at = at or now_utc()
    imported = load(directory/'session_import.json')
    captures = {p.stem:load(p) for p in sorted((directory/'evidence').glob('*.json'))}
    for c in captures.values():
        verify_capture(c)
    fixtures = deepcopy(imported['fixtures'])
    stats = deepcopy(imported['statistics'])
    network = load(directory/'network.json') if (directory/'network.json').exists() else {'attempts':[], 'fixtures':[], 'statistics':[], 'successful_feeds':[]}
    # Successful authoritative feeds replace their own listings, even if there are
    # zero scheduled games. An error never silently becomes "no fixtures".
    for prefix in network.get('successful_feeds', []):
        fixtures = [r for r in fixtures if not r['id'].startswith(prefix+'-')]
    # A partially covered official week only supersedes dates the source
    # actually returned. Uncovered seed dates retain their *original* expiry;
    # absence from a partial response is not proof of zero fixtures.
    for prefix, dates in network.get('replace_fixture_dates', {}).items():
        covered = set(dates)
        fixtures = [r for r in fixtures if not (r['id'].startswith(prefix+'-') and r['facts']['date'] in covered)]
    by_id = {r['id']:r for r in fixtures}
    for row in network.get('fixtures', []):
        by_id[row['id']] = row
    fixtures = list(by_id.values())
    # Do NOT fall back to a stale seed if a fresh stat source is internally contradictory.
    invalid_stat_scopes = set(network.get('replace_stat_scopes', []))
    stats = [s for s in stats if s['competition'] not in invalid_stat_scopes]
    stats += network.get('statistics', [])
    # Filter to the declared *source date* window; undated event cards stay visible,
    # with blank date and no pricing. Elapsed captures stay only in review/export.
    start_day, end_day = at.date().isoformat(), (at.date()+timedelta(days=HORIZON_DAYS-1)).isoformat()
    for row in fixtures:
        row['state'] = fixture_state(row, at)
        row['missing_fields'] = [k for k in ('competition','date','start_utc','venue','official_status') if row['facts'][k] is None]
        if row['kind']=='match':
            row['missing_fields'] += [k for k in ('participant_a','participant_b') if row['facts'][k] is None]
        row['field_status'] = {k: ('verified in captured source' if v is not None else 'unverified') for k,v in row['facts'].items()}
        d=row['facts']['date']
        if row['facts']['start_utc']:
            start=parse_time(row['facts']['start_utc'])
            row['in_window'] = at <= start < at+timedelta(days=HORIZON_DAYS)
        else:
            row['in_window'] = d is None or start_day<=d<=end_day
    fixtures.sort(key=lambda r: (r['facts']['start_utc'] or (r['facts']['date'] or '9999')+'T99',r['sport'],r['id']))
    prices = [originate(row,stats,at) for row in fixtures]
    coverage = []
    for sport, meta in SPORT_INDEX.items():
        rows = [r for r in fixtures if r['sport']==sport and r['in_window']]
        fresh = [r for r in rows if r['state'] not in ('stale','closed','date elapsed','start elapsed','observation not yet available','status not pre-match')]
        used = {sid for r in rows for sid in r['source_ids']}
        checks = [c for c in captures.values() if c.get('sport')==sport and c['role']=='official']
        coverage.append({**meta, 'status':'partial' if fresh else 'unverified', 'scope_complete':False,
                         'listing_count':len(fresh), 'captured_count':len(rows),
                         'priced_count':sum(bool(p['markets']) for p in prices if p['fixture_id'] in {r['id'] for r in fresh}),
                         'source_ids':sorted(used or {c['id'] for c in checks}), 'note':COVERAGE_NOTES[sport]})
    counts = {
        'captured_listings':len(fixtures),
        'current_listings':sum(r['in_window'] and r['state'] not in ('stale','closed','date elapsed','start elapsed','observation not yet available','status not pre-match') for r in fixtures),
        'upcoming_exact':sum(r['in_window'] and r['state']=='upcoming' for r in fixtures),
        'categories':len(SPORT_INDEX), 'categories_with_listings':sum(c['listing_count']>0 for c in coverage),
        'fully_covered_categories':0, 'sources':sum(c['role']=='official' for c in captures.values()),
        'priced_matches':sum(bool(p['markets']) for p in prices),
        'originated_markets':sum(len(p['markets']) for p in prices),
        'originated_outcomes':sum(len(m['outcomes']) for p in prices for m in p['markets']),
        'high':sum(p['confidence']=='high' for p in prices),
        'medium':sum(p['confidence']=='medium' for p in prices),
        'low':sum(p['confidence']=='low' for p in prices),
        'unpriced':sum(not p['markets'] for p in prices),
    }
    snapshot = {'schema_version':SCHEMA_VERSION,'generated_at':iso(at),
                'window':{'source_date_from':start_day,'source_date_through':end_day,'days':HORIZON_DAYS,'utc_from':iso(at),'utc_until_exclusive':iso(at+timedelta(days=HORIZON_DAYS)),
                          'rule':'Exact UTC starts use the rolling UTC interval; undated/date-only rows use the declared source-calendar window with explicit flags.'},
                'complete':False,'facts_policy':'Only captured official-source fields. Blank = unverified. A published schedule is not proof of current match status.',
                'model_version':MODEL_VERSION,'assumptions':ASSUMPTIONS,'counts':counts,'coverage':coverage,
                'fixtures':fixtures,'statistics':stats,'prices':prices,'predictions':[],
                'source_ids':sorted(captures),'network_attempts':network.get('attempts',[]),
                'input_sha256':digest({'import':imported,'network':network,'captures':captures})}
    if write:
        save(directory/'snapshot.json',snapshot)
    return snapshot

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--at')
    args=p.parse_args()
    out=assemble(parse_time(args.at) if args.at else None)
    print(out['counts'])
