import unittest,tempfile,copy,shutil,json
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
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
    def test_tampered_mlb_conditional_flag_rejected(self):
        row=next(r for r in self.s['fixtures'] if r['id']=='mlb-849799')
        row['facts']['if_necessary']='N';self.persist()
        self.assertTrue(any('unsupported value if_necessary' in x for x in validate_data(self.dir)))
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
    def test_partial_week_cannot_erase_unobserved_day(self):
        doc=load(self.dir/'session_import.json');r=next(x for x in doc['fixtures'] if x['id'].startswith('nhl-'))
        original_expiry=r['expires_at'];r['facts']['date']='2026-10-23' # synthetic future-day test, not published evidence
        save(self.dir/'session_import.json',doc)
        save(self.dir/'network.json',{'fixtures':[],'statistics':[],'successful_feeds':[],
             'replace_fixture_dates':{'nhl':['2026-10-22']},'attempts':[]})
        after=assemble(self.at,self.dir)
        self.assertEqual([x['id'] for x in after['fixtures'] if x['id'].startswith('nhl-')],[r['id']])
        self.assertEqual(next(x for x in after['fixtures'] if x['id']==r['id'])['expires_at'],original_expiry)
    def test_unbacked_partial_week_replacement_rejected(self):
        save(self.dir/'network.json',{'fixtures':[],'statistics':[],'successful_feeds':[],
             'replace_fixture_dates':{'nhl':['2026-10-22']},'attempts':[]})
        assemble(self.at,self.dir)
        self.assertTrue(any('partial date replacement not backed' in x for x in validate_data(self.dir)))
    def test_unbacked_full_week_replacement_rejected(self):
        save(self.dir/'network.json',{'fixtures':[],'statistics':[],'successful_feeds':['nhl'],'attempts':[]})
        assemble(self.at,self.dir)
        self.assertTrue(any('full-slate replacement without complete official capture' in x for x in validate_data(self.dir)))
    def test_refresh_partial_nhl_week_retains_proof_and_flags_scope(self):
        from pipeline.http import FetchError,Response
        from pipeline.common import digest
        from pipeline.refresh import refresh
        at=parse_time('2026-10-22T12:10:02Z')
        class OnlyOneDay:
            def __init__(self,raw_dir,**kwargs):
                self.raw=Path(raw_dir);self.raw.mkdir(parents=True,exist_ok=True);self.log=[]
            def get(self,url,source_id):
                if source_id!='http-nhl-schedule':raise FetchError('offline in synthetic test')
                body=json.dumps({'gameWeek':[{'date':'2026-10-22','numberOfGames':0,'games':[]}]}).encode()
                (self.raw/(source_id+'.body')).write_bytes(body)
                return Response(url,url,body,200,'application/json','2026-10-22T12:10:00Z','2026-10-22T12:10:01Z',digest(body))
        with patch('pipeline.refresh.Fetcher',OnlyOneDay),patch('pipeline.refresh.now_utc',return_value=at),\
             patch('pipeline.refresh.crawl',return_value={'complete':False,'pages':[],'events':[]}):
            s=refresh(self.dir,probe=False)
        network=load(self.dir/'network.json')
        self.assertNotIn('nhl',network['successful_feeds'])
        self.assertEqual(network['replace_fixture_dates'],{'nhl':['2026-10-22']})
        self.assertTrue(any(a['status']=='partial' for a in network['attempts']))
        self.assertFalse(any(r['id'].startswith('nhl-') for r in s['fixtures']))  # confirmed zero only on the covered day
        self.assertEqual(validate_data(self.dir),[])
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
