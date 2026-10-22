import unittest,copy,math,tempfile,json
from pathlib import Path
from datetime import timedelta
from urllib import error,request
from pipeline import capture_session as seed
from pipeline.common import parse_time,iso,digest,official_url,allowed_url
from pipeline.evidence import verify_capture,seal_capture,fixture_state,fixture_from_observation
from pipeline.model import price,american_from_decimal,log5,record_ok,originate,baseball_grid,confidence_gate,poisson_vector
from pipeline.discovery import event_link,Links,crawl
from pipeline.http import Fetcher,FetchError,SafeRedirect
from pipeline.adapters import nhl_schedule,mlb_schedule,nba_schedule,nhl_statistics,mlb_statistics,envelope,SchemaError
from pipeline.http import Response

class Seeds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed.seed(write=False)
        cls.rows=copy.deepcopy(seed.FIXTURES);cls.stats=copy.deepcopy(seed.STATS);cls.caps={c['id']:seal_capture(c) for c in seed.CAPTURES}
        cls.at=max(parse_time(c['observed_before']) for c in seed.CAPTURES)+timedelta(minutes=1)
    def fixture(self,prefix='nhl-2026020154'):return copy.deepcopy(next(r for r in self.rows if r['id']==prefix))
    def test_seventeen_category_policy(self):
        from pipeline.config import SPORT_INDEX,EXCLUDED_IDS
        self.assertEqual(len(SPORT_INDEX),17);self.assertFalse({s['olbg_id'] for s in SPORT_INDEX.values()}&EXCLUDED_IDS)
    def test_observed_counts(self):
        self.assertEqual(len(self.rows),108);self.assertEqual(len(self.stats),42)
    def test_every_capture_has_valid_hash(self):
        for c in self.caps.values():self.assertTrue(verify_capture(c))
    def test_tampered_capture_rejected(self):
        c=copy.deepcopy(next(iter(self.caps.values())));c['scope']='changed'
        with self.assertRaises(ValueError):verify_capture(c)
    def test_official_request_redirected_to_discovery_is_not_verified(self):
        c=copy.deepcopy(self.caps['nhl-schedule-20261022'])
        c['final_url']='https://www.olbg.com/betting-tips/Darts/15'
        with self.assertRaises(ValueError):verify_capture(seal_capture(c))
    def test_inverted_window_rejected(self):
        c=copy.deepcopy(next(iter(self.caps.values())));c['observed_before']='2000-01-01T00:00:00Z'
        with self.assertRaises(ValueError):verify_capture(seal_capture(c))
    def test_discovery_never_verifies_fixture(self):
        c=self.caps['olbg-darts-sample']
        with self.assertRaises(ValueError):fixture_from_observation(c,c['observations'][0],'darts','bad')
    def test_no_inferred_tennis_timezone_or_title(self):
        for r in self.rows:
            if r['sport']=='tennis':
                self.assertIsNone(r['facts']['start_utc'])
                if not r['id'].startswith('wta-osaka'):self.assertIsNone(r['facts']['competition'])
    def test_retired_tennis_not_upcoming(self):
        self.assertFalse(any('KAYLA DAY' in str(r['facts']).upper() for r in self.rows))
    def test_placeholder_participant_is_not_verified_identity(self):
        c=copy.deepcopy(self.caps['nhl-schedule-20261022']);o=copy.deepcopy(c['observations'][0]);o['values']['participant_a']='TBD';o['values']['participant_a_id']='0';r=fixture_from_observation(c,o,'ice-hockey','test')
        self.assertIsNone(r['facts']['participant_a']);self.assertIsNone(r['facts']['participant_a_id']);self.assertNotIn('participant_a',r['field_evidence'])
    def test_unknown_status_is_not_cleared_into_prematch(self):
        r=self.fixture();r['facts']['official_status']='unknown';self.assertEqual(fixture_state(r,self.at),'status not pre-match')
    def test_nashville_record_corrected(self):
        r=next(r for r in self.stats if r['team']=='Nashville Predators')
        self.assertEqual((r['wins'],r['losses'],r['ot_losses'],r['points']),(3,2,3,9))
    def test_madrid_record_quarantined(self):self.assertFalse(any(r['team']=='Real Madrid' for r in self.stats))
    def test_valencia_cross_source_conflict_has_no_price(self):
        self.assertFalse(any(r['team']=='Valencia Basket' for r in self.stats));f=next(r for r in self.rows if 'Valencia Basket' in (r['facts']['participant_a'],r['facts']['participant_b']));self.assertFalse(originate(f,self.stats,self.at)['markets'])
    def test_future_source_is_not_fresh(self):
        r=copy.deepcopy(self.stats[0]);r['observed_before']=iso(self.at+timedelta(seconds=1));self.assertFalse(record_ok(r,self.at))
    def test_bad_record_arithmetic_rejected(self):
        r=copy.deepcopy(self.stats[0]);r['games_played']+=1;self.assertFalse(record_ok(r,self.at))
    def test_bad_nhl_points_rejected(self):
        r=copy.deepcopy(next(r for r in self.stats if r.get('points')));r['points']+=1;self.assertFalse(record_ok(r,self.at))
    def test_boolean_not_record_count(self):
        r=copy.deepcopy(self.stats[0]);r['wins']=True;self.assertFalse(record_ok(r,self.at))
    def test_missing_timestamp_rejected(self):
        r=copy.deepcopy(self.stats[0]);r.pop('observed_after');self.assertFalse(record_ok(r,self.at))
    def test_old_record_rejected(self):self.assertFalse(record_ok(self.stats[0],self.at+timedelta(days=2)))
    def test_expiry_uses_original_lower_bound(self):
        r=self.fixture();self.assertEqual(parse_time(r['expires_at']),parse_time(seed.AFTER)+timedelta(hours=6))
    def test_expiry_exact_boundary(self):
        r=self.fixture();self.assertEqual(fixture_state(r,parse_time(r['expires_at'])),'stale')
    def test_elapsed_start_not_final(self):
        r=self.fixture();r['facts']['start_utc']=iso(self.at-timedelta(seconds=1));self.assertEqual(fixture_state(r,self.at),'start elapsed')
    def test_cancelled_never_priced(self):
        r=self.fixture();r['facts']['official_status']='Cancelled';self.assertFalse(originate(r,self.stats,self.at)['markets'])
    def test_live_never_priced(self):
        r=self.fixture();r['facts']['official_status']='LIVE';self.assertFalse(originate(r,self.stats,self.at)['markets'])
    def test_timezone_unknown_no_price(self):
        r=self.fixture();r['facts']['start_utc']=None;self.assertFalse(originate(r,self.stats,self.at)['markets'])
    def test_outside_horizon_no_price(self):
        r=self.fixture();r['in_window']=False;self.assertFalse(originate(r,self.stats,self.at)['markets'])
    def test_missing_one_side_has_no_fallback(self):
        stats=[r for r in self.stats if r['team']!='Nashville Predators'];self.assertFalse(originate(self.fixture(),stats,self.at)['markets'])
    def test_missing_identity_has_no_fuzzy_fallback(self):
        r=self.fixture();r['facts']['participant_b_id']=None;self.assertFalse(originate(r,self.stats,self.at)['markets'])
    def test_different_seasons_dont_join(self):
        r=self.fixture();r['facts']['season']='20252026';self.assertFalse(originate(r,self.stats,self.at)['markets'])
    def test_different_asof_periods_dont_join(self):
        stats=copy.deepcopy(self.stats)
        next(s for s in stats if s['team']=='Boston Bruins')['as_of']='2026-10-20'
        self.assertFalse(originate(self.fixture(),stats,self.at)['markets'])
    def test_no_automatic_high(self):
        p=originate(self.fixture(),self.stats,self.at);self.assertEqual(p['confidence'],'low');self.assertIsNone(p['market_quote'])
    def test_calibrated_boolean_cannot_unlock_high(self):self.assertEqual(confidence_gate(.71,1/.71,True,True,True)[0],'low')
    def test_no_seventy_percent_confidence_rule(self):
        self.assertFalse(any('70%' in reason for reason in confidence_gate(.4,2.5)[1]))
    def test_nhl_ot_losses_used_as_binary_defeats(self):
        a=next(r for r in self.stats if r['team']=='Boston Bruins');b=next(r for r in self.stats if r['team']=='Nashville Predators')
        self.assertAlmostEqual(log5(a,b),63/88)  # posterior strengths 9/14 vs 5/12
    def test_equal_strength_no_arbitrary_winner(self):
        r=self.fixture();stats=copy.deepcopy(self.stats);b=next(x for x in stats if x['team']=='Nashville Predators');a=next(x for x in stats if x['team']=='Boston Bruins')
        for k in ('wins','losses','ot_losses','games_played','points'):b[k]=a[k]
        p=originate(r,stats,self.at);self.assertIsNone(p['selection']);self.assertEqual(len(p['markets']),1)
    def test_model_is_deterministic(self):self.assertEqual(originate(self.fixture(),self.stats,self.at),originate(self.fixture(),self.stats,self.at))
    def test_baseball_six_books(self):
        p=originate(self.fixture('mlb-849805'),self.stats,self.at);self.assertEqual(len(p['markets']),6)
    def test_official_conditional_game_has_no_price_or_selection(self):
        r=self.fixture('mlb-849799')
        self.assertEqual(r['facts']['if_necessary'],'Y')
        self.assertEqual(fixture_state(r,self.at),'conditional')
        self.assertEqual(parse_time(r['expires_at']),parse_time(seed.AFTER)+timedelta(hours=6))
        ref=r['field_evidence']['if_necessary'][0]
        self.assertEqual(self.caps[ref.split('#')[0]]['observations'][-1]['values']['if_necessary'],'Y')
        p=originate(r,self.stats,self.at)
        self.assertEqual(p['markets'],[]);self.assertIsNone(p['selection']);self.assertIsNone(p['confidence'])
        self.assertIn('ifNecessary=Y',' '.join(p['notes']))
    def test_missing_conditional_flag_never_falls_back_to_regular_game(self):
        r=self.fixture('mlb-849805');r['facts']['if_necessary']=None
        self.assertFalse(originate(r,self.stats,self.at)['markets'])
    def test_no_score_model_without_both_run_inputs(self):
        stats=copy.deepcopy(self.stats);next(x for x in stats if x['team']=='Brewers').pop('runs_scored')
        p=originate(self.fixture('mlb-849805'),stats,self.at);self.assertEqual(len(p['markets']),1)
    def test_baseball_mass_and_no_ties(self):
        a,b=[r for r in self.stats if r['competition']=='MLB'];grid,rates,mass=baseball_grid(a,b)
        self.assertAlmostEqual(math.fsum(p for _,_,p in grid),1);self.assertTrue(all(i!=j for i,j,p in grid));self.assertLess(mass,1)
    def test_baseball_fixed_spreads_no_line_search(self):
        p=originate(self.fixture('mlb-849805'),self.stats,self.at);self.assertEqual([m['line'] for m in p['markets'] if m['market']=='handicap'],[-1.5,1.5])
    def test_all_market_families_investigated(self):
        from pipeline.config import SPORT_MARKETS
        for r in self.rows:
            p=originate(r,self.stats,self.at);self.assertEqual({m['market'] for m in p['markets']}|{m['market'] for m in p['withheld']},set(SPORT_MARKETS[r['sport']]))

class Numbers(unittest.TestCase):
    def test_price_floor(self):self.assertEqual(american_from_decimal('1.4'),-250)
    def test_price_ceiling(self):self.assertEqual(american_from_decimal('101'),10000)
    def test_even_money(self):self.assertEqual(american_from_decimal('2'),100)
    def test_half_away_rounding_positive(self):self.assertEqual(american_from_decimal('2.005'),101)
    def test_half_away_rounding_negative(self):self.assertEqual(american_from_decimal('1.8'),-125)
    def test_no_price_clipping(self):self.assertAlmostEqual(price(.001)['fair_decimal'],1000);self.assertFalse(price(.001)['fair_price_in_target_band'])
    def test_invalid_probabilities(self):
        for p in (0,1,-.5,math.nan,math.inf,True):
            with self.assertRaises(ValueError):price(p)
    def test_invalid_odds(self):
        for x in (0,1,-1,'NaN','Infinity'):
            with self.assertRaises(ValueError):american_from_decimal(x)
    def test_naive_time_rejected(self):
        with self.assertRaises(ValueError):parse_time('2026-10-22T15:00:00')
    def test_poisson_invalid_rates(self):
        for rate in (0,-1,21):
            with self.assertRaises(ValueError):poisson_vector(rate)
    def test_log5_symmetry(self):
        a={'wins':9,'games_played':12};b={'wins':5,'games_played':12};self.assertAlmostEqual(log5(a,b)+log5(b,a),1)

class DiscoveryTests(unittest.TestCase):
    def test_official_host_spoofs_rejected(self):
        for u in ['http://www.nhl.com/x','https://www.nhl.com.evil.test/x','https://user@www.nhl.com/x','https://www.nhl.com:444/x','https://www.nhl.com:bad/x','file:///etc/passwd','https://127.0.0.1/x']:
            self.assertFalse(official_url(u))
    def test_valid_official(self):self.assertTrue(official_url('https://www.nhl.com/schedule'))
    def test_olbg_discovery_not_official_sport_facts(self):self.assertFalse(official_url('https://www.olbg.com/betting-tips'));self.assertTrue(allowed_url('https://www.olbg.com/betting-tips',True))
    def test_public_event_key(self):
        e=event_link('/betting-tips/Darts/Test/15?event_id=123','https://www.olbg.com/');self.assertEqual(e['id'],'olbg-15-123');self.assertIsNone(e['probability'])
    def test_excluded_or_hidden_routes(self):
        for p in ['/api/events?event_id=1','/betting-tips/Football/1?event_id=1','/betting-tips/Darts/15?event_id=x','https://evil.test/betting-tips/Darts/15?event_id=1','/betting-tips/Darts/15?event_id=1&event_id=2']:
            self.assertIsNone(event_link(p,'https://www.olbg.com/'))
    def test_link_label_normalization(self):
        p=Links();p.feed('<a href="/x"> A <strong>B</strong> C </a>');self.assertEqual(p.links,[('/x','A B C')])

class FakeResponse:
    def __init__(self,url,body,status=200):self.url=url;self.body=body;self.status=status;self.headers={'Content-Type':'text/plain'}
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return self.body[:n]
    def geturl(self):return self.url
class FakeOpener:
    def __init__(self,robots,body=b'{}'):self.robots=robots;self.body=body;self.urls=[]
    def open(self,req,timeout):
        u=req.full_url;self.urls.append(u)
        if u.endswith('/robots.txt'):
            if isinstance(self.robots,Exception):raise self.robots
            return FakeResponse(u,self.robots)
        return FakeResponse(u,self.body)
class HTTPTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
    def client(self,robot):
        self.opener=FakeOpener(robot);return Fetcher(self.tmp.name,opener=self.opener,delay=0,attempts=1)
    def test_allowed_robots_retains_raw(self):
        f=self.client(b'User-agent: *\nAllow: /');r=f.get('https://www.nhl.com/schedule','test');self.assertEqual(r.sha256,digest(b'{}'));self.assertTrue((Path(self.tmp.name)/'test.body').exists())
    def test_python_urllib_disallow_respected(self):
        f=self.client(b'User-agent: *\nAllow: /\nUser-agent: Python-urllib\nDisallow: /')
        with self.assertRaises(FetchError):f.get('https://www.nhl.com/schedule','test')
        self.assertEqual(len(self.opener.urls),1)
    def test_robots_html_not_allow_all(self):
        f=self.client(b'<html>challenge</html>')
        with self.assertRaises(FetchError):f.get('https://www.nhl.com/schedule','test')
    def test_robots_403_fail_closed(self):
        f=self.client(error.HTTPError('x',403,'Forbidden',{},None))
        with self.assertRaises(FetchError):f.get('https://www.nhl.com/schedule','test')
    def test_robots_404_allows_public_source(self):
        f=self.client(error.HTTPError('x',404,'Not Found',{},None));self.assertEqual(f.get('https://www.nhl.com/schedule','test').status,200)
    def test_unsafe_raw_path_rejected(self):
        f=self.client(b'User-agent: *\nAllow: /')
        with self.assertRaises(FetchError):f.get('https://www.nhl.com/schedule','../bad')
    def test_unapproved_redirect_rejected_before_request(self):
        h=SafeRedirect(lambda u:True)
        with self.assertRaises(FetchError):h.redirect_request(request.Request('https://www.nhl.com/'),None,302,'',{},'https://evil.test/')
    def test_redirect_robots_unknown_rejected(self):
        h=SafeRedirect()
        with self.assertRaises(FetchError):h.redirect_request(request.Request('https://www.nhl.com/'),None,302,'',{},'https://www.nhl.com/private')
    def test_structured_source_cannot_launder_discovery_redirect(self):
        from pipeline.refresh import official_response
        r=Response('https://www.nhl.com/schedule','https://www.olbg.com/betting-tips',b'{}',200,'application/json',
                   '2026-10-22T12:00:00Z','2026-10-22T12:00:01Z',digest(b'{}'))
        with self.assertRaises(FetchError):official_response(r)
    def test_failure_is_not_empty_slate(self):
        f=self.client(error.URLError('offline'));result=crawl(f,max_pages=1);self.assertFalse(result['complete']);self.assertEqual(result['pages'][0]['status'],'unverified')

class Adapters(unittest.TestCase):
    def capture(self,sport='ice-hockey'):
        r=Response('https://api-web.nhle.com/v1/schedule/2026-10-22','https://api-web.nhle.com/v1/schedule/2026-10-22',b'{}',200,'application/json','2026-10-22T07:00:00Z','2026-10-22T07:00:01Z',digest(b'{}'))
        return envelope(r,'synthetic-test',sport,'Synthetic unit test, never published')
    def nhl(self):
        return {'gameWeek':[{'date':'2026-10-22','numberOfGames':1,'games':[{'id':1,'season':20262027,'gameState':'FUT','startTimeUTC':'2026-10-22T23:00:00Z','homeTeam':{'id':1,'placeName':{'default':'Test'},'commonName':{'default':'A'}},'awayTeam':{'id':2,'placeName':{'default':'Test'},'commonName':{'default':'B'}}}]}]}
    def test_nhl_normalization_and_partial_week(self):
        c=self.capture();rows=nhl_schedule(self.nhl(),c,'2026-10-22','2026-10-28');self.assertEqual(rows[0]['facts']['participant_a'],'Test A');self.assertFalse(c['complete']);self.assertEqual(c['covered_dates'],['2026-10-22']);self.assertIsNone(rows[0]['facts']['venue'])
    def test_nhl_only_full_date_coverage_can_replace_whole_week(self):
        d=self.nhl()
        d['gameWeek'] += [{'date':f'2026-10-{day}','numberOfGames':0,'games':[]} for day in range(23,29)]
        c=self.capture();nhl_schedule(d,c,'2026-10-22','2026-10-28')
        self.assertTrue(c['complete']);self.assertEqual(len(c['covered_dates']),7)
    def test_nhl_count_mismatch(self):
        d=self.nhl();d['gameWeek'][0]['numberOfGames']=2
        with self.assertRaises(SchemaError):nhl_schedule(d,self.capture(),'2026-10-22','2026-10-28')
    def test_nhl_unknown_schema_not_zero(self):
        with self.assertRaises(SchemaError):nhl_schedule({},self.capture(),'2026-10-22','2026-10-28')
    def test_nhl_duplicate_id(self):
        d=self.nhl();d['gameWeek'][0]['games']*=2;d['gameWeek'][0]['numberOfGames']=2
        with self.assertRaises(SchemaError):nhl_schedule(d,self.capture(),'2026-10-22','2026-10-28')
    def test_mlb_verified_zero_slate(self):
        c=self.capture('baseball');self.assertEqual(mlb_schedule({'dates':[],'totalGames':0},c,'2026-10-22','2026-10-28',2026),[]);self.assertTrue(c['complete'])
    def test_mlb_absent_count_not_zero_slate(self):
        with self.assertRaises(SchemaError):mlb_schedule({'dates':[]},self.capture(),'2026-10-22','2026-10-28',2026)
    def test_mlb_reported_count_must_reconcile(self):
        with self.assertRaises(SchemaError):mlb_schedule({'dates':[],'totalGames':1},self.capture(),'2026-10-22','2026-10-28',2026)
    def mlb(self,season='2026',necessary='Y'):
        game={'gamePk':849799,'season':season,'gameDate':'2026-10-29T00:00:00Z',
              'teams':{'home':{'team':{'id':139,'name':'Tampa Bay Rays'}},'away':{'team':{'id':158,'name':'Milwaukee Brewers'}}},
              'status':{'detailedState':'Scheduled','abstractGameState':'Preview'}}
        if necessary is not None:game['ifNecessary']=necessary
        return {'dates':[{'date':'2026-10-28','games':[game]}],'totalGames':1}
    def test_mlb_conditional_flag_from_official_game_not_request(self):
        c=self.capture('baseball');r=mlb_schedule(self.mlb(),c,'2026-10-22','2026-10-28',2026)[0]
        self.assertEqual(r['facts']['if_necessary'],'Y');self.assertEqual(r['facts']['season'],'2026')
        self.assertIn('if_necessary',r['field_evidence']);self.assertEqual(fixture_state(r,parse_time('2026-10-22T12:00:00Z')),'conditional')
    def test_mlb_unknown_if_necessary_and_missing_season_are_blank(self):
        r=mlb_schedule(self.mlb(season=None,necessary=None),self.capture('baseball'),'2026-10-22','2026-10-28',2026)[0]
        self.assertIsNone(r['facts']['if_necessary']);self.assertIsNone(r['facts']['season'])
        self.assertNotIn('season',r['field_evidence']);self.assertNotIn('if_necessary',r['field_evidence'])
    def test_mlb_season_does_not_inherit_requested_year(self):
        r=mlb_schedule(self.mlb(season='2025',necessary='N'),self.capture('baseball'),'2026-10-22','2026-10-28',2026)[0]
        self.assertEqual(r['facts']['season'],'2025');self.assertTrue(any('differs' in note for note in r['notes']))
    def test_nba_unknown_schema(self):
        with self.assertRaises(SchemaError):nba_schedule({},self.capture(),'2026-10-22','2026-10-28')
    def test_nba_empty_season_not_zero(self):
        with self.assertRaises(SchemaError):nba_schedule({'leagueSchedule':{'seasonYear':'2026-27','gameDates':[]}},self.capture(),'2026-10-22','2026-10-28')
    def test_mlb_wrong_period_rejected(self):
        with self.assertRaises(SchemaError):mlb_statistics({'records':[{'season':'2025','teamRecords':[]}]},self.capture(),2026,'2026-10-22')

if __name__=='__main__':unittest.main()
