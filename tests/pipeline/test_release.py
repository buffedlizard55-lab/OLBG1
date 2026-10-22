import unittest,tempfile,copy,shutil
from pathlib import Path
from datetime import timedelta
from pipeline import capture_session as seed
from pipeline.common import save,load,parse_time
from pipeline.evidence import seal_capture
from pipeline.assemble import assemble
from pipeline.validate import validate_data,HTML
from pipeline.build import e

class ReleaseIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.dir=Path(self.tmp.name)
        seed.seed(write=False)
        for c in seed.CAPTURES:save(self.dir/'evidence'/f'{c["id"]}.json',seal_capture(c))
        save(self.dir/'session_import.json',{'fixtures':copy.deepcopy(seed.FIXTURES),'statistics':copy.deepcopy(seed.STATS)})
        self.at=max(parse_time(c['observed_before']) for c in seed.CAPTURES)+timedelta(minutes=1)
        self.s=assemble(self.at,self.dir)
    def persist(self):save(self.dir/'snapshot.json',self.s)
    def test_original_evidence_reconciles(self):self.assertEqual(validate_data(self.dir),[])
    def test_mutated_field_rejected(self):
        self.s['fixtures'][0]['facts']['participant_a']='Invented';self.persist();self.assertTrue(any('unsupported value' in x for x in validate_data(self.dir)))
    def test_source_removed_rejected(self):
        self.s['fixtures'][0]['field_evidence'].pop('participant_a');self.persist();self.assertTrue(validate_data(self.dir))
    def test_build_cannot_rejuvenate_evidence(self):
        before=self.s['fixtures'][0]['expires_at'];future=assemble(self.at+timedelta(days=2),self.dir)
        self.assertEqual(future['fixtures'][0]['expires_at'],before);self.assertEqual(future['counts']['priced_matches'],0)
    def test_no_inherited_predictions(self):self.assertEqual(self.s['predictions'],[]);self.assertEqual(self.s['counts']['high'],0)
    def test_failed_feed_does_not_restamp_seed(self):
        save(self.dir/'network.json',{'attempts':[{'status':'unverified'}],'fixtures':[],'statistics':[],'successful_feeds':[]})
        after=assemble(self.at+timedelta(hours=1),self.dir);self.assertEqual(self.s['fixtures'][0]['verified_after'],after['fixtures'][0]['verified_after'])
    def test_successful_zero_feed_replaces_own_seed(self):
        save(self.dir/'network.json',{'attempts':[],'fixtures':[],'statistics':[],'successful_feeds':['nhl']})
        after=assemble(self.at,self.dir);self.assertFalse(any(r['id'].startswith('nhl-') for r in after['fixtures']));self.assertTrue(any(r['id'].startswith('mlb-') for r in after['fixtures']))
    def test_contradictory_new_stats_do_not_fallback(self):
        save(self.dir/'network.json',{'attempts':[],'fixtures':[],'statistics':[],'successful_feeds':[],'replace_stat_scopes':['NHL']})
        after=assemble(self.at,self.dir);self.assertTrue(all(not p['markets'] for p in after['prices'] if p['fixture_id'].startswith('nhl-')))
    def test_overnight_future_utc_not_lost_to_old_local_date(self):
        doc=load(self.dir/'session_import.json');r=doc['fixtures'][0];r['facts']['date']=(self.at.date()-timedelta(days=1)).isoformat();r['facts']['start_utc']=(self.at+timedelta(hours=1)).isoformat();save(self.dir/'session_import.json',doc)
        after=assemble(self.at,self.dir);self.assertTrue(next(x for x in after['fixtures'] if x['id']==r['id'])['in_window'])
    def test_coverage_does_not_become_complete(self):self.assertFalse(self.s['complete']);self.assertTrue(all(not c['scope_complete'] for c in self.s['coverage']))
    def test_every_fixture_has_price_or_explicit_withholding(self):
        self.assertEqual(len(self.s['fixtures']),len(self.s['prices']))
        for p in self.s['prices']:self.assertTrue(p['markets'] or p['withheld'])
    def test_render_escapes_untrusted_text(self):
        self.assertEqual(e('<script>"&'), '&lt;script&gt;&quot;&amp;')
    def test_html_parser_detects_unlinked_row(self):
        h=HTML();h.feed('<table><tr><th>x</th></tr><tr><td>x</td></tr><tr><td><a href="https://www.nhl.com/">NHL</a></td></tr></table>')
        self.assertEqual(h.rows,[[],['https://www.nhl.com/']])
if __name__=='__main__':unittest.main()
