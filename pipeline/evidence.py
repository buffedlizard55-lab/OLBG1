"""Evidence envelopes with field-level references and conservative expiry."""
from datetime import timedelta
from .common import digest, iso, parse_time, official_url
from .config import FIXTURE_TTL_HOURS

FACT_FIELDS = ('participant_a', 'participant_b', 'participant_a_id', 'participant_b_id',
               'event', 'competition', 'season', 'date', 'start_utc', 'time_text',
               'venue', 'official_status', 'format', 'if_necessary')


def seal_capture(capture):
    obj = dict(capture)
    obj.pop('sha256', None)
    obj['sha256'] = digest(obj)
    return obj


def verify_capture(capture):
    obj = dict(capture)
    expected = obj.pop('sha256', None)
    if expected != digest(obj):
        raise ValueError(f"Evidence checksum mismatch: {capture.get('id')}")
    if capture['role'] == 'official' and (not official_url(capture['url']) or
                                        not official_url(capture.get('final_url'))):
        raise ValueError('Non-official request or redirect cannot verify match facts')
    start, end = parse_time(capture['observed_after']), parse_time(capture['observed_before'])
    if end < start:
        raise ValueError('Invalid observation window')
    for item in capture.get('observations', []):
        if not item.get('quote') or not item.get('locator'):
            raise ValueError('An observation needs a retained excerpt and locator')
    return True


def fixture_from_observation(capture, observation, sport, official_id, **meta):
    if capture['role'] != 'official' or not official_url(capture['url']):
        raise ValueError('Discovery is not fixture verification')
    values = observation['values']
    facts = {field: values.get(field) for field in FACT_FIELDS}
    placeholders={'tbd','tba','tbc','unknown','to be determined','n/a','?'}
    for key,value in list(facts.items()):
        if isinstance(value,str) and not value.strip():facts[key]=None
        elif key not in ('official_status','time_text') and isinstance(value,str) and value.strip().lower() in placeholders:facts[key]=None
        elif key.endswith('_id') and value in (0,'0'):facts[key]=None
    ref = f"{capture['id']}#{observation['id']}"
    return {
        'id': official_id, 'sport': sport, 'facts': facts,
        'field_evidence': {key: [ref] for key, value in facts.items() if value is not None},
        'source_ids': [capture['id']],
        'verified_after': capture['observed_after'],
        'verified_before': capture['observed_before'],
        'expires_at': iso(parse_time(capture['observed_after']) + timedelta(hours=FIXTURE_TTL_HOURS)),
        'notes': [], **meta,
    }


def fixture_state(row, at):
    """An elapsed start is NOT a verified final result. Date-only never means live."""
    f = row['facts']
    if parse_time(row['verified_before']) > at:
        return 'observation not yet available'
    if f['official_status'] in ('Final', 'OFF', 'FINAL', 'completed', 'cancelled', 'postponed', 'Cancelled', 'Postponed'):
        return 'closed'
    if f['official_status'] in ('LIVE', 'CRIT', 'In Progress', 'Delayed', 'Suspended', 'unknown'):
        return 'status not pre-match'
    if at >= parse_time(row['expires_at']):
        return 'stale'
    if f['start_utc']:
        if parse_time(f['start_utc']) <= at:
            return 'start elapsed'
        # A scheduled series date is not necessarily a match that will happen.
        # MLB explicitly labels some postseason games "If Necessary".
        return 'conditional' if row['sport'] == 'baseball' and f.get('if_necessary') == 'Y' else 'upcoming'
    if f['date'] and f['date'] < at.date().isoformat():
        return 'date elapsed'
    return 'time unverified'
