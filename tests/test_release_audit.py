import importlib.util
from pathlib import Path
import unittest
import json
import hashlib
spec = importlib.util.spec_from_file_location('audit', Path(__file__).resolve().parents[1]/'scripts/release_audit.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class AuditTests(unittest.TestCase):
    def test_price_boundaries(self):
        for n in [-250,-100,100,10000]:
            self.assertTrue(a.in_window(n))
        for n in [-251,10001,0,-99,99,None,'invalid',float('nan')]:
            self.assertFalse(a.in_window(n))
    def test_fail_closed_and_past_start(self):
        f = {'id':'test','home':'<Team>','sport':'tennis','status':'verified','start_utc':'2026-10-21T00:00:00Z','sources':[{'url':'https://www.atptour.com/'}]}
        l = {'id':'test','confidence':'high','pick_probability':.70,'pick_american':'-250'}
        r = a.audit([f],[l],[],'2026-10-22T00:00:00Z')
        row = r['rows'][0]
        self.assertTrue(row['stored_start_passed'])
        self.assertEqual(row['current_verification'],'unverified')
        self.assertIsNone(row['approved_selection'])
        self.assertIsNone(row['verified_home'])
        self.assertTrue(any('does not exceed' in x for x in row['flags']))
        self.assertIn('&lt;Team&gt;',a.render(r))
    def test_missing_time_not_inferred(self):
        r = a.audit([{'id':'x','sport':'boxing'}],[],[],'2026-10-22T00:00:00Z')['rows'][0]
        self.assertFalse(r['stored_start_passed'])
        self.assertTrue(any('Excluded sport' in x for x in r['flags']))
        self.assertIsNone(r['verified_start_utc'])
    def test_published_register_integrity(self):
        root = Path(__file__).resolve().parents[1]
        report = json.loads((root/'reports/RELEASE_AUDIT.json').read_text())
        fixtures = json.loads((root/'data/fixtures.json').read_text())['matches']
        self.assertEqual({f['id'] for f in fixtures}, {r['id'] for r in report['rows']})
        self.assertEqual(len(fixtures), len(report['rows']))
        for path, digest in report['input_sha256'].items():
            self.assertEqual(hashlib.sha256((root/path).read_bytes()).hexdigest(), digest)
        for row in report['rows']:
            self.assertTrue(row['sources'])
            self.assertEqual(row['current_verification'], 'unverified')
            for key, value in row.items():
                if key.startswith(('approved_', 'verified_')):
                    self.assertIsNone(value)
        self.assertEqual((root/'release-review.html').read_text(), a.render(report))

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            a.instant('2026-10-22T00:00:00')

if __name__ == '__main__':
    unittest.main()
