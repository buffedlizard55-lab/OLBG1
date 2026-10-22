import tempfile,unittest
from pathlib import Path
from pipeline.common import save
from pipeline.validate import validate_site

class CanonicalRouteGates(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.out=Path(self.tmp.name)
        self.at='2026-10-22T09:00:00Z'
        save(self.out/'data/current/site-manifest.json',{'pages':['index.html'],'generated_at':self.at})
        (self.out/'index.html').write_text(f'<html><head><title>Test</title></head><body data-snapshot="{self.at}"><h1>Canonical</h1></body></html>')
    def test_registered_snapshot_passes(self):self.assertEqual(validate_site(self.out),[])
    def test_old_builder_cannot_masquerade_as_canonical(self):
        p=self.out/'index.html';p.write_text(p.read_text().replace(f' data-snapshot="{self.at}"',''));self.assertTrue(any('snapshot marker' in e for e in validate_site(self.out)))
    def test_orphan_root_route_cannot_compete_silently(self):
        (self.out/'old-dashboard.html').write_text('<h1>Old recommendations</h1>');self.assertTrue(any('Unregistered root HTML' in e for e in validate_site(self.out)))
    def test_preserved_independent_audit_not_rewritten(self):
        (self.out/'release-review.html').write_text('<h1>Independent audit</h1>');self.assertEqual(validate_site(self.out),[])
    def test_current_match_row_needs_league_not_olbg_or_repo(self):
        p=self.out/'index.html'
        p.write_text(p.read_text().replace('</body>',
            '<table><tr><td><a href="https://www.olbg.com/betting-tips">Discovery</a>'
            '<a href="https://github.com/buffedlizard55-lab/OLBG1/">Repo</a></td></tr></table></body>'))
        self.assertTrue(any('official sporting source' in err for err in validate_site(self.out)))
        p.write_text(p.read_text().replace('</td>',
            '<a href="https://www.nhl.com/schedule">NHL official</a></td>'))
        self.assertEqual(validate_site(self.out),[])

class PublicEvidenceExports(unittest.TestCase):
    def test_only_parsed_json_proof_is_published(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from pipeline.build import Site
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);inputs=base/'inputs';out=base/'site'
            (inputs/'raw').mkdir(parents=True);(inputs/'raw/http-json.body').write_bytes(b'{}');(inputs/'raw/unparsed-page.body').write_text('<html>Not parsed or verified</html>')
            (out/'data/current/raw').mkdir(parents=True);(out/'data/current/raw/unparsed-page.body').write_text('Old artifact residue')
            site=SimpleNamespace(out=out,c={'http-json':{'id':'http-json','method':'http-json-parser'}},s={'fixtures':[]},prices={})
            with patch('pipeline.build.CURRENT',inputs):Site.exports(site)
            self.assertEqual((out/'data/current/raw/http-json.body').read_bytes(),b'{}')
            self.assertFalse((out/'data/current/raw/unparsed-page.body').exists())
            self.assertTrue((inputs/'raw/unparsed-page.body').exists())


class RenderedPriceExpiryGates(unittest.TestCase):
    setUp = CanonicalRouteGates.setUp

    def record(self, deadline):
        attr='' if deadline is None else f' data-price-expires="{deadline}"'
        p=self.out/'index.html'
        p.write_text(p.read_text().replace('</body>',
            '<section id="synthetic-book" class="market-book" data-record'+attr+
            ' data-expires="2026-10-22T15:00:00Z" data-start="2026-10-22T20:00:00Z"></section></body>'))

    def test_rendered_price_requires_deadline(self):
        self.record(None)
        self.assertTrue(any('rendered price expiry' in e for e in validate_site(self.out)))

    def test_rendered_price_cannot_extend_fixture_deadline(self):
        self.record('2026-10-22T16:00:00Z')
        self.assertTrue(any('rendered price expiry' in e for e in validate_site(self.out)))

    def test_rendered_price_can_expire_before_fixture(self):
        self.record('2026-10-22T12:00:00Z')
        self.assertEqual(validate_site(self.out), [])

    def test_rendered_price_must_match_book_deadline(self):
        self.record('2026-10-22T12:00:00Z')
        save(self.out/'data/current/snapshot.json', {'prices':[
            {'fixture_id':'synthetic-book','expires_at':'2026-10-22T11:00:00Z'}]})
        self.assertTrue(any('deadline differs from price book' in e for e in validate_site(self.out)))


class PreservedDeskRouting(unittest.TestCase):
    def test_completed_desk_links_stay_within_the_project(self):
        from urllib.parse import urlsplit, unquote
        from pipeline.config import ROOT
        from pipeline.validate import HTML
        pages=list((ROOT/'53674ac8').rglob('*.html'))
        self.assertEqual(len(pages),13)
        for page in pages:
            parsed=HTML();parsed.feed(page.read_text())
            for href in parsed.links:
                url=urlsplit(href)
                if url.scheme or url.netloc or not url.path:continue
                with self.subTest(page=page.name,href=href):
                    self.assertFalse(url.path.startswith('/'),'Do not escape the GitHub Pages project prefix')
                    target=(page.parent/unquote(url.path)).resolve()
                    target.relative_to(ROOT)
                    if target.is_dir():target=target/'index.html'
                    self.assertTrue(target.is_file())


if __name__ == '__main__':
    unittest.main()
