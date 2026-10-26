"""Gates for the 26 October 2026 desk (session b1b210b4-olbg1)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'b1b210b4'
DESK = ROOT / 'data' / 'b1b210b4' / 'desk.json'


class Desk(unittest.TestCase):
    def test_build_and_validate_are_green(self):
        build = subprocess.run([sys.executable, 'scripts/sb1b210b4_build.py'],
                               cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(build.returncode, 0, build.stderr)
        val = subprocess.run([sys.executable, 'scripts/sb1b210b4_validate.py'],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(val.returncode, 0, val.stdout + val.stderr)
        self.assertIn('0 errors', val.stdout)

    def test_every_page_has_one_h1_and_a_stylesheet(self):
        pages = sorted(SITE.rglob('*.html'))
        self.assertEqual(len(pages), 25, f'expected 25 pages, got {len(pages)}')
        for p in pages:
            t = p.read_text(encoding='utf-8')
            self.assertEqual(t.count('<h1'), 1, p.name)
            self.assertTrue(('styles.css' in t) or ('desk.css' in t), p.name)

    def test_no_broken_local_links(self):
        for p in SITE.rglob('*.html'):
            for h in re.findall(r'href="(?!#|https?:|mailto)([^"]+)"',
                                p.read_text(encoding='utf-8')):
                target = h.split('#')[0].split('?')[0]
                if not target:
                    continue
                self.assertTrue((p.parent / target).resolve().exists(),
                                f'{p.name} -> {h}')

    def test_grades_follow_the_band_rule(self):
        desk = json.loads(DESK.read_text())
        for f in desk['fixtures']:
            pick = f.get('pick')
            if not pick:
                continue
            self.assertGreaterEqual(pick['american'], -250, f"{f['id']} price below band floor")
            self.assertLessEqual(pick['american'], 10000, f"{f['id']} price above band ceiling")
            self.assertIn(pick['confidence'], ('high', 'medium', 'low'))

    def test_predictions_meet_word_floor(self):
        desk = json.loads(DESK.read_text())
        for f in desk['fixtures']:
            pick = f.get('pick')
            if not pick:
                continue
            words = len([w for w in re.split(r'\s+', pick['prose']) if re.search(r'[A-Za-z0-9]', w)])
            self.assertGreaterEqual(words, 30, f"{f['id']} prose only {words} words")

    def test_no_forbidden_vocabulary(self):
        desk = json.loads(DESK.read_text())
        for f in desk['fixtures']:
            pick = f.get('pick')
            if not pick:
                continue
            text = pick['prose'].lower()
            self.assertNotIn('model', text, f"{f['id']} uses forbidden word 'model'")
            self.assertNotIn('verified', text, f"{f['id']} uses forbidden word 'verified'")


if __name__ == '__main__':
    unittest.main()
