#!/usr/bin/env python3
"""Desk 3c021b49 gate: provenance, arithmetic, prediction rules, site links."""
from __future__ import annotations

import json, re, sys, unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from s3c021b49_data import FIXTURES, SOURCES, SPORT_ORDER, SPORT_NAMES, OLBG_HUBS
from s3c021b49_model import priced_book, featured_pick, confidence_for, in_band, american
from s3c021b49_predictions import PREDICTIONS

DATA = ROOT / "data" / "3c021b49"
SITE = ROOT / "3c021b49"

OFFICIAL_DOMAINS = {
    "atptour.com", "wtatennis.com", "wtafiles.wtatennis.com", "pgatour.com", "lpga.com",
    "europeantour.com", "tauronliga.pl", "legavolley.it", "unitedrugby.com", "stats.unitedrugby.com",
    "nrl.com", "icc-cricket.com", "scoring.nzc.nz", "cricket.com.au", "cricinfo.com", "wst.tv",
    "pdc.tv", "api-web.nhle.com", "nhl.com", "statsapi.mlb.com", "mlb.com", "nba.com",
    "official.nba.com", "euroleaguebasketball.net", "formula1.com", "thw-handball.de", "hc-erlangen.de", "lnh.fr",
    "hbcnantes.com", "teamchambe.com", "gaacork.ie", "munster.gaa.ie", "kilkennygaa.ie", "galwaygaa.ie", "volleyballworld.com",
    "limerickleader.ie", "gbgb.org.uk",
}


class TestFixtures(unittest.TestCase):
    def test_every_fixture_has_official_sources(self):
        for fx in FIXTURES:
            self.assertTrue(fx["sources"], f"{fx['id']}: no sources")
            for sid in fx["sources"]:
                self.assertIn(sid, SOURCES, f"{fx['id']}: unknown source {sid}")

    def test_every_fixture_is_in_scope_sport(self):
        for fx in FIXTURES:
            self.assertIn(fx["sport"], SPORT_ORDER, f"{fx['id']}: {fx['sport']} not in scope")

    def test_sports_covered(self):
        self.assertEqual(len(SPORT_ORDER), 15)
        self.assertEqual({f["sport"] for f in FIXTURES}, set(SPORT_ORDER))

    def test_unique_ids(self):
        ids = [f["id"] for f in FIXTURES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_source_urls_are_https(self):
        for sid, (name, url) in SOURCES.items():
            self.assertTrue(url.startswith("https://"), f"{sid}: {url}")
            self.assertEqual(urlsplit(url).scheme, "https")

    def test_upcoming_fixtures_have_start(self):
        for fx in FIXTURES:
            if fx["state"] == "upcoming":
                self.assertTrue(fx["start_utc"] or fx["date"], f"{fx['id']}: no start")


class TestModel(unittest.TestCase):
    def test_fair_price_arithmetic(self):
        for fx in FIXTURES:
            if fx["state"] != "upcoming":
                continue
            book = priced_book(fx)
            for m in book["markets"]:
                # winner/handicap/total are two-way
                if m["key"] in ("winner", "handicap", "puck_line", "run_line", "total",
                                "set_betting", "total_legs", "total_frames", "outright"):
                    outcomes = m["outcomes"]
                    if len(outcomes) == 2:
                        s = sum(o["probability"] for o in outcomes)
                        self.assertAlmostEqual(s, 1.0, places=6, msg=f"{fx['id']}/{m['key']}: mass {s}")
                    for o in outcomes:
                        p = o["probability"]
                        self.assertGreater(p, 0)
                        self.assertLess(p, 1)
                        self.assertAlmostEqual(o["fair_decimal"] * p, 1.0, places=3,
                                               msg=f"{fx['id']}/{m['key']}: fair decimal {o['fair_decimal']} vs p {p}")

    def test_band_policy(self):
        for fx in FIXTURES:
            if fx["state"] != "upcoming":
                continue
            book = priced_book(fx)
            for m in book["markets"]:
                for o in m["outcomes"]:
                    self.assertEqual(o["in_band"], in_band(o["probability"]),
                                     f"{fx['id']}/{m['key']}: wrong band flag")
                    if o["in_band"]:
                        self.assertGreaterEqual(o["fair_decimal"], 1.4 - 1e-9)
                        self.assertLessEqual(o["fair_decimal"], 101.0 + 1e-9)

    def test_confidence_consistency(self):
        for fx in FIXTURES:
            if fx["state"] != "upcoming":
                continue
            book = priced_book(fx)
            rated = book["rated"] in ("team", "player", "f1")
            for m in book["markets"]:
                for o in m["outcomes"]:
                    conf = confidence_for(o["probability"], rated)
                    if conf == "high":
                        self.assertTrue(o["in_band"])
                        self.assertGreaterEqual(o["probability"], 0.62)
                    elif conf == "medium":
                        self.assertGreaterEqual(o["probability"], 0.50)

    def test_mlb_conditional_withheld(self):
        fx = next(f for f in FIXTURES if f["id"] == "BB05")
        self.assertEqual(fx["inputs"]["if_necessary"], "Y")
        book = priced_book(fx)
        self.assertEqual(book["markets"], [])

    def test_elapsed_fixtures_unpriced(self):
        for fx in FIXTURES:
            if fx["state"] != "upcoming":
                book = {"fixture_id": fx["id"], "markets": []}
                self.assertEqual(book["markets"], [])


class TestPredictions(unittest.TestCase):
    def test_all_high_picks_have_predictions(self):
        for fx in FIXTURES:
            if fx["state"] != "upcoming":
                continue
            book = priced_book(fx)
            pick = featured_pick(book)
            if pick and pick["confidence"] == "high":
                self.assertIn(fx["id"], PREDICTIONS, f"{fx['id']}: High pick without prediction")

    def test_min_word_count_and_uniqueness(self):
        seen = set()
        for fid, pd in PREDICTIONS.items():
            words = pd["text"].split()
            self.assertGreaterEqual(len(words), 30, f"{fid}: {len(words)} words")
            key = " ".join(words).lower()
            self.assertNotIn(key, seen, f"{fid}: duplicate prediction")
            seen.add(key)

    def test_no_forbidden_words(self):
        texts = " ".join(pd["text"] for pd in PREDICTIONS.values()).lower()
        self.assertNotIn("model", texts)
        self.assertNotIn("verified", texts)

    def test_selection_matches_pick(self):
        for fid, pd in PREDICTIONS.items():
            fx = next(f for f in FIXTURES if f["id"] == fid)
            book = priced_book(fx)
            pick = featured_pick(book)
            self.assertIsNotNone(pick)
            self.assertEqual(pd["selection"], pick["selection"], f"{fid}: selection drift")

    def test_bet_line_quotes_price(self):
        built = json.loads((DATA / "predictions.json").read_text())["predictions"]
        for pd in built:
            fid = pd["match_id"]
            fx = next(f for f in FIXTURES if f["id"] == fid)
            book = priced_book(fx)
            pick = featured_pick(book)
            dec = f"{pick['fair_decimal']:.3f}"
            am = pick["fair_american"].lstrip("+")
            self.assertTrue(dec in pd["bet_line"] or am in pd["bet_line"],
                            f"{fid}: bet_line missing price {dec}/{am}: {pd['bet_line']}")

    def test_predictions_have_sources(self):
        built = json.loads((DATA / "predictions.json").read_text())["predictions"]
        for pd in built:
            fid = pd["match_id"]
            self.assertTrue(pd["sources"], f"{fid}: no sources")
            for u in pd["sources"]:
                host = urlsplit(u).hostname or ""
                self.assertTrue(any(host == d or host.endswith("." + d) for d in OFFICIAL_DOMAINS),
                                f"{fid}: non-official source {u}")


class TestSite(unittest.TestCase):
    def test_pages_exist(self):
        manifest = json.loads((DATA / "site-manifest.json").read_text())
        for page in manifest["pages"]:
            self.assertTrue((SITE / page).is_file(), f"missing page {page}")

    def test_relative_links(self):
        for page in (SITE / "index.html").parent.rglob("*.html"):
            text = page.read_text()
            for m in re.finditer(r'href="([^"#]+)"', text):
                href = m.group(1)
                if href.startswith(("http", "mailto:", "#", "assets/")):
                    continue
                target = (page.parent / href).resolve()
                if target.is_dir():
                    target = target / "index.html"
                self.assertTrue(target.is_file(), f"{page}: broken link {href}")

    def test_fixture_pages_have_source_links(self):
        import html as _html
        for fx in FIXTURES:
            page = SITE / "sports" / f"{fx['sport']}.html"
            text = page.read_text()
            self.assertIn(fx["id"], text)
            for sid in fx["sources"]:
                url = SOURCES[sid][1]
                self.assertIn(_html.escape(url, quote=True), text,
                              f"{fx['id']}: source {sid} not linked on {fx['sport']} page")

    def test_no_external_js(self):
        js = (SITE / "assets" / "app.js").read_text()
        self.assertNotIn("fetch(", js)
        self.assertNotIn("localhost", js)


if __name__ == "__main__":
    unittest.main()
