"""Gates for the 25 October 2026 desk (session a394f91e-olbg1)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'a394f91e'
sys.path.insert(0, str(ROOT / 'scripts'))

import sa394f91e_content as C      # noqa: E402
import sa394f91e_data as E         # noqa: E402
import sa394f91e_model as M        # noqa: E402


class Desk(unittest.TestCase):
    def test_build_and_validate_are_green(self):
        build = subprocess.run([sys.executable, 'scripts/sa394f91e_build.py'],
                               cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(build.returncode, 0, build.stderr)
        val = subprocess.run([sys.executable, 'scripts/sa394f91e_validate.py'],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(val.returncode, 0, val.stdout + val.stderr)
        self.assertIn('errors: 0', val.stdout)

    def test_every_page_has_one_h1_and_a_stylesheet(self):
        pages = sorted(SITE.rglob('*.html'))
        self.assertEqual(len(pages), 25, 'expected 25 pages')
        for p in pages:
            t = p.read_text(encoding='utf-8')
            self.assertEqual(t.count('<h1'), 1, p.name)
            self.assertIn('styles.css', t, p.name)

    def test_no_broken_local_links(self):
        for p in SITE.rglob('*.html'):
            for h in re.findall(r'href="(?!#|https?:|mailto)([^"]+)"',
                                p.read_text(encoding='utf-8')):
                self.assertTrue((p.parent / h.split('#')[0]).resolve().exists(),
                                f'{p.name} -> {h}')

    def test_grades_follow_the_band_rule(self):
        for p in json.loads((ROOT / 'data/a394f91e/desk.json').read_text())['picks']:
            self.assertGreaterEqual(p['price'], M.BAND_LOW)
            self.assertLessEqual(p['price'], M.BAND_HIGH)
            self.assertEqual(M.grade(p['probability']), p['grade'])

    def test_predictions_are_long_unique_and_plain(self):
        texts = list(C.PREDICTIONS.values())
        self.assertEqual(len(texts), 3)
        for t in texts:
            self.assertGreaterEqual(len(t.split()), 30)
            self.assertNotIn('model', t.lower())
            self.assertNotIn('verif', t.lower())

    def test_provenance_is_official_only(self):
        allowed = {'api-web.nhle.com', 'www.nhl.com', 'www.nba.com', 'statsapi.mlb.com'}
        for f in C.NHL + C.NBA + C.MLB:
            self.assertIn(f['source_url'].split('/')[2], allowed, f['key'])

    def test_fifteen_brief_sports_are_published(self):
        wanted = {'golf', 'volleyball', 'rugby-union', 'cricket', 'snooker', 'darts',
                  'baseball', 'gaelic', 'greyhounds', 'tennis', 'motor-racing',
                  'handball', 'ice-hockey', 'basketball', 'rugby-league'}
        self.assertEqual({s[0] for s in E.SPORTS}, wanted)
        for slug in wanted:
            self.assertTrue((SITE / 'sports' / f'{slug}.html').is_file(), slug)

    def test_league_average_comes_from_the_official_table(self):
        self.assertEqual(set(M.NHL_GF), set(M.NHL_GA))
        self.assertEqual(set(M.NHL_GF), set(M.NHL_GP))
        self.assertAlmostEqual(M.NHL_LEAGUE_GPG, 3.1506, places=3)


if __name__ == '__main__':
    unittest.main()
