"""Focused tests for the 733888f2 desk (session T733888F2)."""
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

import s733888f2_data as D          # noqa: E402
import s733888f2_model as M         # noqa: E402
import s733888f2_build as B         # noqa: E402
import s733888f2_validate as V      # noqa: E402

DESK = ROOT / '733888f2'
DATA = ROOT / 'data' / '733888f2'


class TestDeskFiles(unittest.TestCase):
    def test_desk_pages_exist(self):
        for name in V.EXPECTED:
            self.assertTrue((DESK / name).is_file(), name)

    def test_all_fifteen_sports_have_a_page(self):
        slugs = [s[0] for s in D.SPORTS]
        self.assertEqual(len(slugs), 15)
        for slug in slugs:
            self.assertTrue((DESK / 'sports' / f'{slug}.html').is_file(), slug)

    def test_data_mirrors_parse(self):
        for name in ('fixtures.json', 'lines.json', 'picks.json', 'flags.json',
                     'sources.json', 'manifest.json', 'olbg.json'):
            json.loads((DATA / name).read_text())

    def test_manifest_counts_match_data(self):
        man = json.loads((DATA / 'manifest.json').read_text())['counts']
        self.assertEqual(man['priced_matches'], len(D.MATCHES))
        self.assertEqual(man['unpriced_listings'], len(D.UNPRICED))
        self.assertEqual(man['sports'], 15)
        self.assertEqual(man['flags'], len(B.FLAGS))

    def test_archive_registration(self):
        build = (ROOT / 'pipeline' / 'build.py').read_text()
        self.assertIn("'733888f2/index.html'", build)


class TestPricing(unittest.TestCase):
    def test_two_way_books_are_margin_free(self):
        for m in D.MATCHES:
            card = M.price_match(m)
            self.assertIsNotNone(card, m['id'])
            w = card['market_winner']
            self.assertAlmostEqual(w['home']['p'] + w['away']['p'], 1.0, places=12)

    def test_high_tier_requires_the_conjunction(self):
        # 70.5% inside the band is High; 72% is outside because -250 is 71.43%.
        self.assertEqual(M.tier(0.705, M.american(0.705)), 'High')
        self.assertEqual(M.tier(0.75, M.american(0.75)), 'Strong')
        self.assertEqual(M.tier(0.60, M.american(0.60)), 'Medium')
        self.assertEqual(M.tier(0.50, M.american(0.50)), 'Low')

    def test_band_edges(self):
        self.assertTrue(M.in_band(-250))
        self.assertTrue(M.in_band(10000))
        self.assertFalse(M.in_band(-251))
        self.assertFalse(M.in_band(10001))

    def test_american_conversion(self):
        self.assertEqual(M.american(0.5), -100.0)
        self.assertEqual(M.american(0.7), -233.0)
        self.assertEqual(M.american(0.25), 300.0)

    def test_neutral_site_drops_the_home_term(self):
        m = [x for x in D.MATCHES if x['id'] == 'NHL-3'][0]
        card = M.price_match(m)
        self.assertAlmostEqual(card['p_home'], 0.469, places=3)

    def test_every_priced_match_is_upcoming(self):
        for m in D.MATCHES:
            self.assertGreater(m['start'], '2026-10-24T22:25:00Z', m['id'])


class TestProse(unittest.TestCase):
    def test_predictions_are_at_least_thirty_words(self):
        for mid, text in B.PREDICTIONS.items():
            self.assertGreaterEqual(len(V.words(text)), 30, mid)

    def test_predictions_avoid_internal_vocabulary(self):
        for mid, text in B.PREDICTIONS.items():
            low = text.lower()
            for bad in V.BANNED:
                self.assertNotIn(bad, low, f'{mid} contains {bad}')

    def test_predictions_are_unique(self):
        seen = {}
        for mid, text in B.PREDICTIONS.items():
            g = V.grams(text)
            for other, og in seen.items():
                self.assertFalse(g & og, f'{mid} overlaps {other}')
            seen[mid] = g

    def test_prediction_names_the_selection(self):
        for m in D.MATCHES:
            pick = M.price_match(m)['pick']['selection']
            first = pick.split()[0].lower()
            self.assertIn(first, B.PREDICTIONS[m['id']].lower(), m['id'])


class TestVerification(unittest.TestCase):
    def test_every_priced_match_links_an_official_publisher(self):
        for m in D.MATCHES:
            host = m['official'].split('/')[2]
            self.assertTrue(any(host == h or host.endswith('.' + h) for h in V.OFFICIAL_HOSTS), host)

    def test_every_unpriced_row_says_why(self):
        for u in D.UNPRICED:
            self.assertGreaterEqual(len(u['reason']), 20, u['event'])

    def test_sources_carry_read_times_and_roles(self):
        for s in D.SOURCES:
            self.assertRegex(s['read_utc'], r'^2026-10-24T\d\d:\d\d:\d\dZ$')
            self.assertIn(s['role'], ('fact', 'discovery'))

    def test_fact_sources_are_not_olbg(self):
        for s in D.SOURCES:
            if s['role'] == 'fact':
                self.assertNotIn('olbg.com', s['url'], s['id'])

    def test_flags_all_have_links(self):
        for fid, title, kind, url, detail in B.FLAGS:
            self.assertTrue(url.startswith('https://'), fid)
            self.assertGreater(len(detail), 40, fid)


class TestValidator(unittest.TestCase):
    def test_validator_reports_no_errors(self):
        self.assertEqual(V.run(), [])

    def test_pages_have_a_single_h1(self):
        for path in sorted(DESK.rglob('*.html')):
            text = path.read_text()
            self.assertEqual(len(re.findall(r'<h1', text)), 1, path.name)


if __name__ == '__main__':
    unittest.main()
