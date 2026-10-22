"""Synthetic regression scenarios; these are not new official match facts."""
import copy
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from pipeline import capture_session as seed
from pipeline.assemble import assemble
from pipeline.common import iso, parse_time, save
from pipeline.evidence import fixture_state, seal_capture
from pipeline.model import originate, record_ok
from pipeline.validate import validate_data


class PriceLifetimes(unittest.TestCase):
    def setUp(self):
        seed.seed(write=False)
        self.rows = copy.deepcopy(seed.FIXTURES)
        self.stats = copy.deepcopy(seed.STATS)
        self.row = next(r for r in self.rows if r['id'] == 'nhl-2026020154')
        self.at = max(parse_time(c['observed_before']) for c in seed.CAPTURES) + timedelta(minutes=1)

    def test_blank_or_unrecognized_status_never_means_scheduled(self):
        for status in (None, '', 'New provider state', 'unknown', 'In Progress', 'Delayed', 'Suspended'):
            with self.subTest(status=status):
                self.row['facts']['official_status'] = status
                p = originate(self.row, self.stats, self.at)
                self.assertEqual(p['markets'], [])
                self.assertIsNone(p['selection'])
                self.assertIsNone(p['expires_at'])

    def test_explicit_supported_pre_match_states_can_be_priced(self):
        for status in ('FUT', 'PRE'):
            self.row['facts']['official_status'] = status
            self.assertTrue(originate(self.row, self.stats, self.at)['markets'])

    def test_price_expires_with_earliest_statistic_not_only_fixture(self):
        for r in self.stats:
            r['observed_after'] = iso(self.at - timedelta(hours=24) + timedelta(minutes=2))
            r['observed_before'] = iso(parse_time(r['observed_after']) + timedelta(seconds=1))
            r['as_of'] = (self.at - timedelta(days=1)).date().isoformat()
        p = originate(self.row, self.stats, self.at)
        self.assertTrue(p['markets'])
        self.assertEqual(p['expires_at'], iso(self.at + timedelta(minutes=2)))
        self.assertLess(parse_time(p['expires_at']), parse_time(self.row['expires_at']))
        self.assertEqual(originate(self.row, self.stats, self.at + timedelta(minutes=2))['markets'], [])

    def test_price_expires_with_fixture_or_start_if_earlier(self):
        p = originate(self.row, self.stats, self.at)
        self.assertEqual(p['expires_at'], self.row['expires_at'])
        self.row['facts']['start_utc'] = iso(self.at + timedelta(minutes=1))
        p = originate(self.row, self.stats, self.at)
        self.assertEqual(p['expires_at'], self.row['facts']['start_utc'])

    def test_exact_24_hour_statistical_boundary_is_expired(self):
        stat = self.stats[0]
        at = parse_time(stat['observed_after']) + timedelta(hours=24)
        self.assertTrue(record_ok(stat, at - timedelta(microseconds=1)))
        self.assertFalse(record_ok(stat, at))

    def test_future_observation_cannot_support_retrospective_price(self):
        at = parse_time(self.row['verified_before']) - timedelta(seconds=1)
        self.assertEqual(fixture_state(self.row, at), 'observation not yet available')
        self.assertEqual(originate(self.row, self.stats, at)['markets'], [])

    def test_missing_status_is_not_filled_from_a_future_start(self):
        row = next(r for r in self.rows if r['id'].startswith('euroleague-'))
        self.assertIsNone(row['facts']['official_status'])
        p = originate(row, self.stats, self.at)
        self.assertFalse(p['markets'])
        self.assertIn('pre-match status unverified', p['notes'][0])


class DerivedReleaseGates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        seed.seed(write=False)
        for c in seed.CAPTURES:
            save(self.directory / 'evidence' / f'{c["id"]}.json', seal_capture(c))
        save(self.directory / 'session_import.json', {
            'fixtures': copy.deepcopy(seed.FIXTURES), 'statistics': copy.deepcopy(seed.STATS)})
        at = max(parse_time(c['observed_before']) for c in seed.CAPTURES) + timedelta(minutes=1)
        self.snapshot = assemble(at, self.directory)

    def errors(self):
        save(self.directory / 'snapshot.json', self.snapshot)
        return validate_data(self.directory)

    def test_unchanged_snapshot_passes(self):
        self.assertEqual(self.errors(), [])

    def test_duplicate_price_books_rejected(self):
        self.snapshot['prices'].append(copy.deepcopy(self.snapshot['prices'][0]))
        self.assertIn('Duplicate price-book row', self.errors())

    def test_invented_kpi_rejected(self):
        self.snapshot['counts']['high'] = 42
        self.assertIn('Snapshot counts do not reconcile with retained rows', self.errors())

    def test_invented_coverage_count_rejected(self):
        self.snapshot['coverage'][0]['priced_count'] = 42
        self.assertTrue(any('coverage price count' in e for e in self.errors()))

    def test_invented_window_membership_rejected(self):
        self.snapshot['fixtures'][0]['in_window'] = not self.snapshot['fixtures'][0]['in_window']
        self.assertTrue(any('rolling-window membership' in e for e in self.errors()))

    def test_extended_price_lifetime_rejected(self):
        book = next(p for p in self.snapshot['prices'] if p['markets'])
        book['expires_at'] = iso(parse_time(book['expires_at']) + timedelta(hours=1))
        self.assertTrue(any('nonreproducible price' in e for e in self.errors()))

    def test_field_evidence_cannot_escape_its_expiry_scope(self):
        row = self.snapshot['fixtures'][0]
        # A genuine supporting observation hidden outside source_ids must not be
        # able to shorten the provenance set used to compute fixture expiry.
        supporting = copy.deepcopy(seed.CAPTURES[0])
        supporting['id'] = 'synthetic-extra-support'
        supporting['observations'] = [{'id': 'a', 'quote': 'Synthetic test only',
            'locator': 'synthetic', 'values': {'participant_a': row['facts']['participant_a']}}]
        save(self.directory / 'evidence/synthetic-extra-support.json', seal_capture(supporting))
        row['field_evidence']['participant_a'] = ['synthetic-extra-support#a']
        self.assertTrue(any('field source absent from expiry scope' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
