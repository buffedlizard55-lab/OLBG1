"""Gates for the published dashboard.

These replace the earlier ``validate_site`` contract, which described a page set
that no longer exists. The properties they protect are the ones the brief asks
for: one registered page set, a visible snapshot marker, an official source on
every table row, prices inside the brief's band, and prose that names the
selection without internal vocabulary.
"""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from pipeline.build import build_site
from pipeline.common import load, save
from pipeline.desk import build_desk
from pipeline.validate import validate_desk


class DeskSiteGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.tmp.name) / 'site'
        build_site(cls.site, None)
        cls.desk = load(cls.site / 'data' / 'desk' / 'desk.json')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def mutate(self, desk=None, page=None, drop=()):
        """Copy the built site, apply a change, and return its validation errors."""
        work = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, work, True)
        shutil.copytree(self.site, work / 'site')
        target = work / 'site'
        for rel in drop:
            (target / rel).unlink(missing_ok=True)
        if page is not None:
            path = target / page[0]
            path.write_text(path.read_text().replace(page[1], page[2]))
        if desk is not None:
            save(target / 'data' / 'desk' / 'desk.json', desk)
        return validate_desk(target)

    def test_published_site_passes(self):
        self.assertEqual(validate_desk(self.site), [])

    def test_snapshot_marker_is_required(self):
        marker = f'data-snapshot="{self.desk["generated_at"]}"'
        errors = self.mutate(page=('index.html', marker, 'data-snapshot=""'))
        self.assertTrue(any('snapshot marker' in e for e in errors), errors)

    def test_orphan_root_page_cannot_compete_with_the_registered_set(self):
        errors = self.mutate()
        self.assertEqual(errors, [])
        work = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, work, True)
        shutil.copytree(self.site, work / 'site')
        (work / 'site' / 'old-dashboard.html').write_text('<h1>Old recommendations</h1>')
        self.assertTrue(any('unregistered root HTML' in e for e in validate_desk(work / 'site')))

    def test_every_table_row_needs_an_official_source(self):
        errors = self.mutate(page=('matches.html', 'https://api-web.nhle.com/v1/schedule/2026-10-24',
                                   'https://www.olbg.com/betting-tips/Ice_Hockey/13'))
        self.assertTrue(any('no official source link' in e for e in errors), errors)

    def test_a_pick_outside_the_band_is_refused(self):
        desk = copy.deepcopy(self.desk)
        pick = next(f for f in desk['fixtures'] if f['pick'])['pick']
        pick['american'] = -400
        errors = self.mutate(desk=desk)
        self.assertTrue(any('outside the -250..+10000 band' in e for e in errors), errors)

    def test_a_short_prediction_is_refused(self):
        desk = copy.deepcopy(self.desk)
        pick = next(f for f in desk['fixtures'] if f['pick'])['pick']
        pick['prediction'] = 'Short pick.'
        errors = self.mutate(desk=desk)
        self.assertTrue(any('shorter than 30 words' in e for e in errors), errors)

    def test_internal_vocabulary_is_refused_in_prose(self):
        desk = copy.deepcopy(self.desk)
        pick = next(f for f in desk['fixtures'] if f['pick'])['pick']
        pick['prediction'] = pick['prediction'] + ' The model verified this number.'
        errors = self.mutate(desk=desk)
        self.assertTrue(any('contains "model"' in e for e in errors), errors)
        self.assertTrue(any('contains "verified"' in e for e in errors), errors)

    def test_a_pick_must_name_its_selection(self):
        desk = copy.deepcopy(self.desk)
        pick = next(f for f in desk['fixtures'] if f['pick'])['pick']
        pick['prediction'] = ('This write-up deliberately never names the side being backed, and it '
                              'runs long enough to clear the thirty word floor without saying what '
                              'the selection actually is, which is exactly what the gate should '
                              'catch before publication.')
        errors = self.mutate(desk=desk)
        self.assertTrue(any('does not name the selection' in e for e in errors), errors)

    def test_counts_must_reconcile(self):
        desk = copy.deepcopy(self.desk)
        desk['counts']['high'] = desk['counts']['high'] + 1
        errors = self.mutate(desk=desk)
        self.assertTrue(any('counts do not reconcile' in e for e in errors), errors)

    def test_thresholds_are_the_published_ones(self):
        desk = build_desk()
        for fixture in desk['fixtures']:
            pick = fixture['pick']
            if not pick:
                continue
            self.assertGreaterEqual(pick['probability'], 0.55)
            self.assertGreaterEqual(pick['american'], -250)
            self.assertLessEqual(pick['american'], 10000)
            expected = 'high' if pick['probability'] >= 0.60 else 'medium'
            self.assertEqual(pick['confidence'], expected)


class PreservedDeskRouting(unittest.TestCase):
    def test_completed_desk_links_stay_within_the_project(self):
        from urllib.parse import urlsplit, unquote
        from pipeline.config import ROOT
        from pipeline.validate import HTML
        pages = list((ROOT / '53674ac8').rglob('*.html'))
        self.assertEqual(len(pages), 13)
        for page in pages:
            parsed = HTML()
            parsed.feed(page.read_text())
            for href in parsed.links:
                url = urlsplit(href)
                if url.scheme or url.netloc or not url.path:
                    continue
                with self.subTest(page=page.name, href=href):
                    self.assertFalse(url.path.startswith('/'), 'Do not escape the GitHub Pages project prefix')
                    target = (page.parent / unquote(url.path)).resolve()
                    target.relative_to(ROOT)
                    if target.is_dir():
                        target = target / 'index.html'
                    self.assertTrue(target.is_file())


if __name__ == '__main__':
    unittest.main()
