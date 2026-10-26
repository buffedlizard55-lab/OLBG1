"""Gates for the independent 26 October 2026 desk (session aa2881ac-olbg1)."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'aa2881ac'
sys.path.insert(0, str(ROOT / 'scripts'))

import saa2881ac_content as C  # noqa: E402
import saa2881ac_data as D     # noqa: E402
import saa2881ac_model as M    # noqa: E402


class Desk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = subprocess.run([sys.executable, 'scripts/saa2881ac_build.py'], cwd=ROOT,
                                   capture_output=True, text=True)
        cls.desk = json.loads((ROOT / 'data' / 'aa2881ac' / 'desk.json').read_text(encoding='utf-8'))

    def test_build_and_validator_are_green(self):
        self.assertEqual(self.build.returncode, 0, self.build.stderr)
        val = subprocess.run([sys.executable, 'scripts/saa2881ac_validate.py'], cwd=ROOT,
                             capture_output=True, text=True)
        self.assertEqual(val.returncode, 0, val.stdout + val.stderr)
        self.assertIn('errors: 0', val.stdout)

    def test_build_is_deterministic(self):
        before = (SITE / 'index.html').read_text(encoding='utf-8')
        subprocess.run([sys.executable, 'scripts/saa2881ac_build.py'], cwd=ROOT, check=True,
                       capture_output=True)
        self.assertEqual(before, (SITE / 'index.html').read_text(encoding='utf-8'))

    def test_twenty_five_pages_and_all_fifteen_sports(self):
        pages = sorted(SITE.rglob('*.html'))
        self.assertEqual(len(pages), 25)
        self.assertEqual({p.stem for p in (SITE / 'sports').glob('*.html')}, set(D.SPORT_INDEX))
        self.assertEqual(len(D.SPORT_INDEX), 15)

    def test_grades_and_band(self):
        self.assertEqual(M.grade(0.70), 'High')
        self.assertEqual(M.grade(0.72), 'none')       # -257 is shorter than -250
        self.assertEqual(M.grade(0.57), 'Medium')
        self.assertEqual(M.grade(0.45), 'Low')
        self.assertEqual(M.grade(0.30), 'none')
        self.assertEqual(M.american(0.5), -100)
        for p in self.desk['picks']:
            self.assertTrue(-250 <= p['price'] <= 10000, p['id'])
            if p['grade'] == 'High':
                self.assertGreaterEqual(p['prob'], M.HIGH_MIN)

    def test_predictions_follow_the_writing_rules(self):
        preds = self.desk['predictions']
        self.assertTrue(preds)
        texts = [p['text'] for p in preds]
        self.assertEqual(len(texts), len(set(texts)))
        for p in preds:
            words = p['text'].lower().split()
            self.assertGreaterEqual(len(words), 30, p['pick'])
            self.assertNotIn('model', p['text'].lower())
            self.assertNotIn('verif', p['text'].lower())
            self.assertIn(p['price_text'], p['text'])
            self.assertIn('injury', p['availability'])

    def test_unconfirmed_dates_cap_the_grade(self):
        for p in self.desk['picks']:
            fx = next(f for f in self.desk['fixtures'] if f['key'] == p['fixture'])
            if not fx['confirmed']:
                self.assertEqual(p['grade'], 'Low', p['id'])

    def test_every_pick_and_fixture_has_an_official_source(self):
        from saa2881ac_validate import OFFICIAL_HOSTS
        from urllib.parse import urlsplit
        for f in self.desk['fixtures']:
            for s in f['sources']:
                self.assertIn(urlsplit(s['url']).netloc, OFFICIAL_HOSTS, f['key'])
        for p in self.desk['picks']:
            self.assertIn(urlsplit(p['source']).netloc, OFFICIAL_HOSTS, p['id'])

    def test_no_olbg_link_on_pick_pages(self):
        for name in ('index.html', 'picks.html', 'matches.html', 'predictions.html'):
            self.assertNotIn('olbg.com', (SITE / name).read_text(encoding='utf-8'), name)

    def test_audit_links_are_pinned_to_reviewed_commits(self):
        for r in C.audit():
            self.assertTrue('90646c82d7bd75d70a8769367d8a76ddb43d9705' in r['url']
                            or '4e4603ebf09953f9248dfa77c9e9d4a48548ef36' in r['url'], r['url'])

    def test_front_door_registers_the_desk(self):
        src = (ROOT / 'pipeline' / 'build.py').read_text(encoding='utf-8')
        self.assertIn("('aa2881ac/index.html'", src)
        self.assertIn("self.href('aa2881ac/picks.html'", src)


if __name__ == '__main__':
    unittest.main()
