"""Negative controls and independent structural gates for the corrected desk.

These tests do not certify external sporting truth; they enforce the retained
observation contract, timing, arithmetic and honest publication of limitations.
"""
from __future__ import annotations
import copy
import csv
import importlib
import json
import math
import re
import sys
import tempfile
import unittest
from datetime import timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from se455acb16_data import assemble_inputs,SPORT_ORDER,SPORT_NAMES,OFFICIAL_HOSTS,OBSERVED_AFTER,OBSERVED_BEFORE,digest
from se455acb16_model import (originate,parse_time,price,in_band,american,log5,confidence_for,
    record_ok,fixture_state,baseball_grid,poisson)
from se455acb16_build import create_dataset,validate_inputs,build,repository_review
from se455acb16_predictions import PREDICTIONS,RESEARCH_NOTES

AT=parse_time("2026-10-23T21:45:00Z")
DATA=ROOT/"data"/"455acb16"
SITE=ROOT/"455acb16"
EXPECTED={"Golf","Volleyball","Rugby Union","Cricket","Snooker","Darts","Baseball","Gaelic Sports",
    "Greyhounds","Tennis","Motor Racing","Handball","Ice Hockey","Basketball","Rugby League"}

class Rows(HTMLParser):
    def __init__(self):
        super().__init__();self.rows=[];self.current=None;self.in_td=False;self.header=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="tr":self.current=[];self.header=False
        if tag=="th":self.header=True
        if tag=="a" and self.current is not None:self.current.append(a.get("href",""))
    def handle_endtag(self,tag):
        if tag=="tr" and self.current is not None:
            if not self.header:self.rows.append(self.current)
            self.current=None

class Desk455ACB16(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs,cls.fixtures,cls.stats=assemble_inputs()
        cls.dataset=create_dataset(AT)
        cls.by_id={f["id"]:f for f in cls.fixtures}
        cls.books={b["fixture_id"]:b for b in cls.dataset["books"]}

    def test_exact_requested_category_scope(self):
        self.assertEqual(set(SPORT_NAMES.values()),EXPECTED)
        self.assertEqual(len(SPORT_ORDER),15)
        self.assertEqual({f["sport"] for f in self.fixtures},set(SPORT_ORDER))
        self.assertNotIn("aussie-rules",SPORT_ORDER);self.assertNotIn("esports",SPORT_ORDER)

    def test_gaelic_sports_mapping_is_explicit_and_does_not_pool_codes(self):
        rows=[f for f in self.fixtures if f["sport"]=="gaelic-sports"]
        self.assertTrue(any("Hurling" in f["competition"] for f in rows))
        self.assertTrue(any("Football" in f["competition"] for f in rows))
        self.assertTrue(any(s["id"]=="olbg-hurling" and "both covering Football and Hurling" in s["excerpt"] for s in self.obs))
        self.assertTrue(all(not self.books[f["id"]]["markets"] for f in rows))

    def test_no_copied_first_draft_ids_or_prose(self):
        self.assertFalse(any(re.fullmatch(r"[A-Z]{2}\d\d",f["id"]) for f in self.fixtures))
        self.assertEqual(PREDICTIONS,[])
        self.assertEqual(self.dataset["predictions"],[])
        self.assertNotIn("496eaf02",(ROOT/"scripts/se455acb16_data.py").read_text())

    def test_actual_observation_window_not_build_time(self):
        self.assertLess(parse_time(OBSERVED_AFTER),parse_time(OBSERVED_BEFORE))
        self.assertTrue(all(o["observed_after"]==OBSERVED_AFTER and o["observed_before"]==OBSERVED_BEFORE for o in self.obs))
        future=create_dataset(AT+timedelta(days=2))
        self.assertEqual(future["observation_window"],self.dataset["observation_window"])
        self.assertEqual(future["counts"]["priced_matches"],0)
        self.assertTrue(all(o["observed_after"]==OBSERVED_AFTER for o in future["observations"]))

    def test_missing_or_unknown_state_never_becomes_scheduled(self):
        f=copy.deepcopy(self.by_id["nhl-2026020166"])
        for state in (None,"", "new-unknown-code"):
            f["official_status"]=state
            self.assertEqual(originate(f,self.stats,AT)["markets"],[])

    def test_exact_source_projections_and_integrity_digests(self):
        self.assertEqual(validate_inputs(self.obs,self.fixtures,self.stats),[])
        for s in self.obs:
            self.assertEqual(s["content_sha256"],digest({"excerpt":s["excerpt"],"projection":s["projection"]}))
            if s["role"]=="official":self.assertIn(urlsplit(s["url"]).hostname,OFFICIAL_HOSTS)
            self.assertIsNone(s["http_status"],"Tool status must not be invented as transport metadata")

    def test_tampered_field_rejected(self):
        fs=copy.deepcopy(self.fixtures)
        fs[0]["participant_a"]="Invented Club"
        self.assertTrue(any("unsupported" in e for e in validate_inputs(self.obs,fs,self.stats)))

    def test_missing_observation_rejected(self):
        self.assertTrue(validate_inputs([o for o in self.obs if o["id"]!="nhl-schedule"],self.fixtures,self.stats))

    def test_changed_evidence_digest_rejected(self):
        obs=copy.deepcopy(self.obs);obs[0]["excerpt"]="rewritten proof"
        self.assertTrue(any("evidence changed" in e for e in validate_inputs(obs,self.fixtures,self.stats)))

    def test_olbg_cannot_verify_sporting_fields(self):
        obs=copy.deepcopy(self.obs)
        obs[0]["role"]="discovery"
        self.assertTrue(validate_inputs(obs,self.fixtures,self.stats))
        for f in self.fixtures:
            self.assertTrue(all(not sid.startswith("olbg-") for sid in f["source_ids"]))
            self.assertIsNone(f["olbg_eligibility"])
            self.assertIsNone(f["olbg_event_url"])

    def test_quotes_never_filled_from_fair_prices(self):
        for b in self.dataset["books"]:
            self.assertIsNone(b["market_quote"])
            self.assertIsNone(b["olbg_eligibility"])
            for m in b["markets"]:
                for o in m["outcomes"]:
                    self.assertIsNone(o["market_quote"])
                    self.assertEqual(o["confidence"],"low")

    def test_evidence_window_expiry_and_start_boundary(self):
        f=self.by_id["nhl-2026020166"]
        start=parse_time(f["start_utc"])
        self.assertTrue(originate(f,self.stats,start-timedelta(seconds=1))["markets"])
        self.assertFalse(originate(f,self.stats,start)["markets"])
        late=parse_time(OBSERVED_AFTER)+timedelta(hours=6)
        self.assertFalse(originate(f,self.stats,late)["markets"])
        before=parse_time(OBSERVED_BEFORE)-timedelta(seconds=1)
        self.assertFalse(originate(f,self.stats,before)["markets"])

    def test_price_expires_on_earliest_statistic(self):
        records=copy.deepcopy(self.stats)
        r=next(s for s in records if s["id"]=="nhl-stat-8")
        r["observed_after"]="2026-10-22T21:50:00Z"
        r["observed_before"]="2026-10-22T21:51:00Z"
        b=originate(self.by_id["nhl-2026020166"],records,AT)
        self.assertEqual(b["expires_at"],"2026-10-23T21:50:00Z")

    def test_missing_record_does_not_create_a_neutral_fallback(self):
        records=[r for r in self.stats if r["team_id"]!=16 or r["competition"]!="NHL"]
        self.assertFalse(originate(self.by_id["nhl-2026020166"],records,AT)["markets"])

    def test_records_preserve_otl_and_same_period(self):
        for r in self.stats:self.assertTrue(record_ok(r,AT),r["id"])
        records=copy.deepcopy(self.stats)
        next(r for r in records if r["id"]=="nhl-stat-16")["as_of"]="2026-10-22"
        self.assertFalse(originate(self.by_id["nhl-2026020166"],records,AT)["markets"])
        r=next(r for r in records if r["id"]=="nhl-stat-8")
        r["games_played"]-=r["ot_losses"]
        self.assertFalse(record_ok(r,AT))

    def test_mlb_does_not_invent_an_nhl_overtime_loss_statistic(self):
        records=[r for r in self.stats if r["competition"]=="MLB"]
        self.assertTrue(records)
        for r in records:
            self.assertNotIn("ot_losses",r)
            self.assertTrue(record_ok(r,AT))
            wrong=copy.deepcopy(r);wrong["ot_losses"]=0
            self.assertFalse(record_ok(wrong,AT))
        self.assertIn("W-L-OT (NHL) / W-L (MLB)",(SITE/"analysis.html").read_text())

    def test_mlb_conditional_and_unknown_necessity_have_no_prices(self):
        self.assertFalse(self.books["mlb-849799"]["markets"])
        self.assertFalse(self.books["mlb-849801"]["markets"])
        f=copy.deepcopy(self.by_id["mlb-849805"]);f["if_necessary"]=None
        self.assertFalse(originate(f,self.stats,AT)["markets"])

    def test_not_before_or_unlabelled_clocks_stay_null(self):
        for f in self.fixtures:
            if f["sport"] not in ("ice-hockey","baseball"):
                self.assertIsNone(f["start_utc"],f["id"])
                self.assertFalse(self.books[f["id"]]["markets"],f["id"])
            if f["published_clock"] and "Not before" in f["published_clock"]:
                self.assertIsNone(f["start_utc"])

    def test_corrected_wta_pairings(self):
        self.assertEqual(self.by_id["wta-ningbo-sf1"]["participant_b"],"Marie BOUZKOVA")
        self.assertEqual(self.by_id["wta-osaka-sf1"]["participant_b"],"Ashlyn KRUEGER")
        self.assertEqual(self.by_id["wta-osaka-sf2"]["participant_b"],"Katerina SINIAKOVA")

    def test_coherent_books_and_raw_odds_arithmetic(self):
        for b in self.books.values():
            for m in b["markets"]:
                self.assertAlmostEqual(math.fsum(o["probability"] for o in m["outcomes"]),1,places=12)
                for o in m["outcomes"]:
                    self.assertGreater(o["probability"],0);self.assertLess(o["probability"],1)
                    self.assertAlmostEqual(o["probability"]*o["fair_decimal"],1,places=12)
                    self.assertEqual(o["in_band"],in_band(o["probability"]))
                    self.assertEqual(o["fair_american"],american(o["probability"]))

    def test_boundaries_use_unrounded_prices_no_clipping(self):
        self.assertTrue(in_band(5/7));self.assertTrue(in_band(1/101))
        self.assertFalse(in_band(5/7+1e-8));self.assertFalse(in_band(1/101-1e-8))
        self.assertEqual(american(5/7+1e-8),-250,"Display can round into band but flag must remain false")
        self.assertEqual(price(.9)["fair_american"],-900)
        self.assertEqual(price(.005)["fair_decimal"],200)
        for bad in (0,1,True,float('nan'),float('inf'),-0.1):
            with self.assertRaises(ValueError):price(bad)

    def test_high_cannot_be_manufactured_with_an_unsigned_flag(self):
        self.assertEqual(confidence_for(.71,calibrated=True,current_context=True,quote=-240),"low")
        self.assertTrue(all(b["confidence"] in (None,"low") for b in self.books.values()))
        self.assertEqual(self.dataset["counts"]["high"],0)
        self.assertEqual(self.dataset["counts"]["medium"],0)

    def test_poisson_mass_and_fixed_lines(self):
        a,b=[r for r in self.stats if r["competition"]=="MLB"]
        grid,rates,mass=baseball_grid(a,b)
        self.assertAlmostEqual(math.fsum(z for i,j,z in grid),1,places=12)
        self.assertGreater(mass,0);self.assertLess(mass,1)
        self.assertTrue(all(i!=j for i,j,z in grid))
        for b in self.books.values():
            if b["fixture_id"].startswith("mlb-") and b["markets"]:
                self.assertEqual([m["line"] for m in b["markets"] if m["family"]=="handicap"],[-1.5,1.5])
                self.assertEqual(len([m for m in b["markets"] if m["family"]=="total"]),3)
                self.assertTrue(all(m["line"]%1==.5 for m in b["markets"] if m["line"] is not None))

    def test_every_listing_has_market_investigation_and_row_flag(self):
        flag_ids={r["id"] for r in self.dataset["flags"]}
        for f in self.dataset["fixtures"]:
            self.assertTrue(self.books[f["id"]]["investigated"])
            self.assertIn("ROW-"+f["id"],flag_ids)
            self.assertTrue(f["official_urls"])
            for m in self.books[f["id"]]["investigated"]:
                self.assertTrue(m["reason"])
                self.assertEqual(m["status"],"experimental" if m["family"] in {x["family"] for x in self.books[f["id"]]["markets"]} else "withheld")

    def test_count_and_quota_consistency(self):
        c=self.dataset["counts"]
        self.assertEqual(c["listings"],len(self.fixtures))
        self.assertEqual(c["match_listings"]+c["field_event_listings"],c["listings"])
        self.assertEqual(c["priced_matches"],18);self.assertEqual(c["markets"],38);self.assertEqual(c["outcomes"],76)
        for c in self.dataset["coverage"]:
            self.assertFalse(c["scope_complete"])
            self.assertEqual(c["high_shortfall"],5)
            self.assertEqual(len(c["top_research_ids"]),len(set(c["top_research_ids"])))
            self.assertLessEqual(len(c["top_research_ids"]),5)
            for fid in c["top_research_ids"]:self.assertTrue(in_band(self.books[fid]["probability"]))

    def test_notes_are_new_unique_long_and_banned_word_clean(self):
        texts=set()
        for n in RESEARCH_NOTES:
            t=n["text"]
            self.assertGreaterEqual(len(t.split()),30)
            self.assertNotIn("model",t.lower());self.assertNotIn("verified",t.lower())
            self.assertNotIn(t,texts);texts.add(t)
            self.assertTrue(n["source_ids"])
        self.assertEqual(len(RESEARCH_NOTES),6)

    def test_every_html_data_row_links_its_official_authority(self):
        # OLBG is the primary authority for its own robots/routes, never for
        # sporting facts. The separate field-provenance test rejects OLBG as
        # sporting proof even though its policy-review row may cite OLBG.
        authorities=OFFICIAL_HOSTS | {"www.olbg.com"}
        for p in SITE.rglob("*.html"):
            parser=Rows();parser.feed(p.read_text())
            for i,urls in enumerate(parser.rows):
                self.assertTrue(any(urlsplit(u).hostname in authorities for u in urls),f"{p.name}: data row {i} lacks an official link")

    def test_review_hashes_match_the_declared_git_revision_not_the_working_tree(self):
        import hashlib,subprocess
        # Exercise the builder at HEAD. A shallow CI checkout need not contain
        # historical commits addressed by an archived published review. Those
        # immutable remote locators are checked independently, not silently
        # replaced with current working-tree bytes or fetched during unit tests.
        audit=repository_review()
        for row in audit["findings"]:
            raw=subprocess.check_output(["git","show",f"{audit['revision']}:{row['file']}"],cwd=ROOT)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row["sha256"])
            self.assertIn(row["needle"],raw.decode("utf-8").splitlines()[row["line"]-1])

    def test_local_links_and_manifest_all_resolve(self):
        manifest=json.loads((DATA/"site-manifest.json").read_text())
        self.assertEqual(len(manifest["pages"]),28)
        self.assertEqual(len(list((SITE/"sports").glob("*.html"))),15)
        ids={}
        for rel in manifest["pages"]:
            page=SITE/rel;self.assertTrue(page.is_file())
            ids[page.resolve()]=set(re.findall(r'\bid="([^"]+)"',page.read_text()))
        for page in SITE.rglob("*.html"):
            for url in re.findall(r'(?:href|src)="([^"]+)"',page.read_text()):
                parts=urlsplit(html_unescape(url))
                if parts.scheme or parts.netloc:continue
                path=(page.parent/unquote(parts.path)).resolve() if parts.path else page.resolve()
                if path.is_dir():path=path/"index.html"
                self.assertTrue(path.is_file(),f"{page}: broken link {url}")
                if parts.fragment and path in ids:self.assertIn(unquote(parts.fragment),ids[path],f"{page}: missing anchor {url}")

    def test_no_external_browser_dependencies_or_fake_freshness(self):
        for p in SITE.rglob("*.html"):
            text=p.read_text()
            self.assertNotRegex(text,r'<script[^>]+src="https?://')
            self.assertNotIn('http://localhost',text);self.assertNotIn('127.0.0.1',text)
            self.assertIn('Source times never renewed',text)
        css=(SITE/"assets/style.css").read_text()
        self.assertIn('.estimate{visibility:hidden;display:none}',css)
        self.assertIn('Estimates withheld without JavaScript',(SITE/"index.html").read_text())

    def test_published_json_matches_calculations_and_retained_evidence(self):
        published=json.loads((DATA/"desk.json").read_text())
        expected=create_dataset(parse_time(published["generated_at"]))
        self.assertEqual(published,expected)
        self.assertEqual(json.loads((DATA/"fixtures.json").read_text())["fixtures"],published["fixtures"])
        self.assertEqual(json.loads((DATA/"books.json").read_text()),published["books"])
        self.assertEqual(json.loads((DATA/"statistics.json").read_text()),published["statistics"])
        self.assertEqual(json.loads((DATA/"sources.json").read_text())["sources"],published["observations"])
        self.assertEqual(json.loads((DATA/"summary.json").read_text())["counts"],published["counts"])
        self.assertEqual(json.loads((DATA/"predictions.json").read_text())["predictions"],[])
        self.assertIn("0 of the 75 daily target supported",(SITE/"index.html").read_text())

    def test_executive_rows_actually_follow_the_declared_probability_order(self):
        text=(SITE/"index.html").read_text()
        ids=re.findall(r'<tr id="([^"]+)" data-row',text)
        # The two executive tables are today-in-LA and the upcoming shortlist.
        today=[fid for fid in ids if self.by_id[fid]["start_utc"] in
               ("2026-10-24T00:00:00Z","2026-10-24T01:00:00Z")]
        upcoming=[fid for fid in ids if fid not in today]
        for group in (today,upcoming):
            chances=[self.books[fid]["probability"] for fid in group]
            self.assertEqual(chances,sorted(chances,reverse=True))

    def test_exports_do_not_fill_quotes_or_eligibility(self):
        with (DATA/"matches.csv").open(encoding="utf-8-sig") as fh:rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),len(self.fixtures))
        self.assertTrue(all(r["quote"]=='' and r["olbg_eligibility"]=='' for r in rows))
        with (DATA/"markets.csv").open(encoding="utf-8-sig") as fh:rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),76);self.assertTrue(all(r["quote"]=='' for r in rows))

    def test_scratch_build_is_non_mutating_and_does_not_refresh_sources(self):
        files=list(DATA.glob("*.json"))
        before={f:f.read_bytes() for f in files}
        with tempfile.TemporaryDirectory() as tmp:
            built=build(AT,Path(tmp))
            self.assertEqual(built["observation_window"],self.dataset["observation_window"])
            self.assertEqual(len(list((Path(tmp)/"455acb16/sports").glob("*.html"))),15)
        self.assertEqual(before,{f:f.read_bytes() for f in files})


def html_unescape(text):
    import html
    return html.unescape(text)

if __name__=="__main__":unittest.main()
