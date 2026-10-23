#!/usr/bin/env python3
"""Session 5b7d3436 evidence, price, release and static-site gates."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import s5b7d3436_lines as line_engine

DATA = ROOT / "data" / "5b7d3436"
SITE = ROOT / "5b7d3436"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


class DeskTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture_doc = load("fixtures.json")
        cls.fixtures = cls.fixture_doc["fixtures"]
        cls.fixture_map = {f["id"]: f for f in cls.fixtures}
        cls.source_doc = load("sources.json")
        cls.sources = {s["id"]: s for s in cls.source_doc["sources"]}
        cls.discovery = load("discovery.json")
        cls.lines = load("lines.json")
        cls.books = {b["fixture_id"]: b for b in cls.lines["books"]}
        cls.summary = load("summary.json")
        cls.flagged = load("flagged.json")
        cls.predictions = load("predictions.json")
        cls.manifest = load("site-manifest.json")


class TestEvidence(DeskTestCase):
    def test_exact_sport_brief(self):
        expected = {"Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts",
                    "Baseball", "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing",
                    "Handball", "Ice Hockey", "Basketball", "Rugby League"}
        self.assertEqual(set(self.fixture_doc["sports"]), expected)
        self.assertEqual({f["sport"] for f in self.fixtures}, expected)
        self.assertEqual(len(self.fixture_doc["sports"]), 15)
        self.assertNotIn("Australian Rules", expected)
        self.assertNotIn("eSports", expected)

    def test_fixture_ids_and_counts(self):
        ids = [f["id"] for f in self.fixtures]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 20)
        self.assertEqual(self.summary["fixtures"], 20)
        self.assertEqual(self.summary["upcoming"], 19)
        self.assertEqual(self.summary["in_progress"], 1)

    def test_source_ids_unique_and_urls_https(self):
        ids = [s["id"] for s in self.source_doc["sources"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 59)
        for s in self.source_doc["sources"]:
            self.assertEqual(urlsplit(s["url"]).scheme, "https", s["id"])
            self.assertTrue(s["registered_at"].endswith("Z"))
            self.assertTrue(s["takeaway"].strip(), s["id"])
            self.assertTrue(s["method"].strip(), s["id"])

    def test_every_fixture_has_only_official_fact_sources(self):
        official_hosts = {
            "api-web.nhle.com", "www.nhl.com", "statsapi.mlb.com", "www.nba.com",
            "ak-static.cms.nba.com", "official.nba.com", "www.icc-cricket.com",
            "wtafiles.wtatennis.com", "www.tauronliga.pl", "www.unitedrugby.com",
            "www.pdc.tv", "gaacork.ie", "www.formula1.com", "thw-handball.de",
            "www.pgatour.com", "www.wst.tv", "www.gbgb.org.uk", "www.nrl.com",
        }
        for f in self.fixtures:
            self.assertTrue(f["source_ids"], f["id"])
            for sid in f["source_ids"]:
                self.assertIn(sid, self.sources, f"{f['id']} / {sid}")
                source = self.sources[sid]
                self.assertTrue(source["official"], f"{f['id']} uses discovery as fact source")
                self.assertIn(urlsplit(source["url"]).hostname, official_hosts, source["url"])

    def test_discovery_is_not_open_market_evidence(self):
        self.assertEqual(self.discovery["open_markets"], 0)
        self.assertEqual(len(self.discovery["rows"]), 15)
        self.assertEqual(sum(r["event_state"] == "expired" for r in self.discovery["rows"]), 11)
        self.assertEqual(len(self.discovery["subroutes"]), 5)
        for row in self.discovery["rows"]:
            self.assertFalse(row["open_market_established"])
            self.assertTrue(row["hub_url"].startswith("https://www.olbg.com/"))
        for f in self.fixtures:
            self.assertFalse(f["open_olbg_market"])
            if f["olbg_event_id"]:
                self.assertEqual(f["olbg_state"], "expired")
                self.assertIn(f"olbg-event-{f['olbg_event_id']}", self.sources)

    def test_start_fields_never_invent_utc(self):
        capture = dt(self.fixture_doc["registered_at"])
        for f in self.fixtures:
            if f["start_utc"]:
                self.assertIsNotNone(dt(f["start_utc"]))
                self.assertTrue(f["start_utc_basis"], f["id"])
                if f["state"] == "upcoming":
                    self.assertGreater(dt(f["start_utc"]), capture, f["id"])
            else:
                self.assertTrue(f["start_local"] or f["date"], f["id"])
            if f["state"] == "upcoming":
                self.assertTrue(f["start_utc"] or f["start_local"] or f["date"], f["id"])
            self.assertGreater(dt(f["evidence_expires_at"]), capture)

    def test_pdc_method_is_disclosed(self):
        source = self.sources["pdc-report"]
        self.assertIn("search", source["method"])
        self.assertIn("consent", source["method"])

    def test_every_gap_is_in_review_register(self):
        flag_ids = {f["id"] for f in self.flagged["flags"]}
        for f in self.fixtures:
            for i in range(1, len(f["flags"]) + 1):
                self.assertIn(f"{f['id']}-F{i}", flag_ids)
            for i in range(1, len(f["market_gaps"]) + 1):
                self.assertIn(f"{f['id']}-M{i}", flag_ids)
        self.assertEqual(self.flagged["count"], len(self.flagged["flags"]))
        self.assertEqual(self.summary["flagged_findings"], self.flagged["count"])


class TestPrices(DeskTestCase):
    def test_reproducible_from_fixture_inputs(self):
        for f in self.fixtures:
            self.assertEqual(line_engine.price_fixture(f), self.books[f["id"]], f["id"])

    def test_counts(self):
        priced = [f for f in self.fixtures if self.books[f["id"]]["markets"]]
        self.assertEqual(len(priced), 7)
        self.assertEqual({f["sport"] for f in priced}, {"Ice Hockey", "Baseball"})
        self.assertEqual(sum(len(self.books[f["id"]]["markets"]) for f in self.fixtures), 21)
        outcomes = [o for f in self.fixtures for m in self.books[f["id"]]["markets"] for o in m["outcomes"]]
        self.assertEqual(len(outcomes), 42)
        self.assertEqual(self.summary["originated_outcomes"], 42)

    def test_two_way_mass_and_price_arithmetic(self):
        for f in self.fixtures:
            for market in self.books[f["id"]]["markets"]:
                outcomes = market["outcomes"]
                self.assertEqual(len(outcomes), 2, f"{f['id']} / {market['key']}")
                self.assertAlmostEqual(sum(o["probability"] for o in outcomes), 1.0, places=7)
                for o in outcomes:
                    p = o["probability"]
                    self.assertGreater(p, 0.0)
                    self.assertLess(p, 1.0)
                    self.assertAlmostEqual(o["fair_decimal"], 1.0 / p, places=5)
                    expected_band = 1.40 <= 1.0 / p <= 101.0
                    self.assertEqual(o["in_band"], expected_band)
                    self.assertIsNone(o["bookmaker_quote"])
                    if market["key"] in {"handicap", "total"}:
                        self.assertIsNotNone(o["line"])
                        self.assertEqual((o["line"] * 2) % 2, 1)

    def test_unpriced_books_have_explicit_reasons(self):
        for f in self.fixtures:
            book = self.books[f["id"]]
            if not f["inputs"]:
                self.assertEqual(book["markets"], [])
                self.assertIsNone(book["preferred_winner"])
                self.assertTrue(book["withheld_reason"].strip(), f["id"])
            else:
                self.assertEqual(len(book["markets"]), 3)
                self.assertEqual({m["key"] for m in book["markets"]}, {"winner", "handicap", "total"})
                self.assertGreater(book["retained_poisson_mass_before_normalization"], 0.999999)

    def test_price_expiry_is_earlier_of_evidence_and_start(self):
        for f in self.fixtures:
            book = self.books[f["id"]]
            if not book["markets"]:
                self.assertIsNone(book["expires_at"])
                continue
            expected = min(dt(f["evidence_expires_at"]), dt(f["start_utc"]))
            self.assertEqual(dt(book["expires_at"]), expected)

    def test_no_real_quote_or_available_wager(self):
        for book in self.books.values():
            p = book["preferred_winner"]
            if p:
                self.assertFalse(p["open_olbg_market"])
                self.assertFalse(p["availability_complete"])
                self.assertFalse(p["publishable_high"])

    def test_high_band_is_not_just_probability(self):
        boston = self.books["IH05"]["preferred_winner"]
        self.assertTrue(boston["probability_gate"])
        self.assertGreater(boston["probability"], 0.70)
        self.assertFalse(boston["band_gate"])
        self.assertLess(boston["fair_decimal"], 1.40)
        self.assertFalse(boston["publishable_high"])
        at_floor = line_engine.outcome("test", "floor", 1 / 1.4)
        beyond_floor = line_engine.outcome("test", "beyond", 0.72)
        self.assertTrue(at_floor["in_band"])
        self.assertFalse(beyond_floor["in_band"])

    def test_summary_and_prediction_release_are_zero(self):
        self.assertEqual(self.summary["open_olbg_markets"], 0)
        self.assertEqual(self.summary["high_picks"], 0)
        self.assertEqual(self.summary["published_predictions"], 0)
        self.assertEqual(self.predictions["count"], 0)
        self.assertEqual(self.predictions["predictions"], [])
        self.assertIn("No selection passed", self.predictions["reason"])

    def test_any_future_prediction_would_obey_prose_contract(self):
        seen = set()
        for p in self.predictions["predictions"]:
            text = p["text"]
            self.assertGreaterEqual(len(text.split()), 30)
            normalized = " ".join(text.lower().split())
            self.assertNotIn(normalized, seen)
            seen.add(normalized)
            self.assertNotRegex(normalized, r"\bmodel\b|\bverified\b")
            self.assertIn(p["selection"], text)


class TestExports(DeskTestCase):
    def test_matches_csv(self):
        with (DATA / "matches.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 20)
        self.assertEqual({r["id"] for r in rows}, set(self.fixture_map))
        for row in rows:
            self.assertTrue(row["official_urls"].startswith("https://"))
            self.assertEqual(row["open_olbg_market"], "False")
            self.assertEqual(row["bookmaker_quote"], "")
            if not self.fixture_map[row["id"]]["inputs"]:
                self.assertEqual(row["experimental_selection"], "")
                self.assertEqual(row["probability"], "")

    def test_markets_csv(self):
        with (DATA / "markets.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 42)
        for row in rows:
            self.assertTrue(row["official_urls"].startswith("https://"))
            self.assertEqual(row["bookmaker_quote"], "")
            self.assertEqual(row["open_olbg_market"], "False")


class TestStaticSite(DeskTestCase):
    def test_manifest_and_hashes(self):
        self.assertEqual(len(self.manifest["pages"]), 28)
        for record in self.manifest["pages"] + self.manifest["assets"]:
            path = SITE / record["path"]
            self.assertTrue(path.is_file(), record["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"], record["path"])

    def test_all_sport_pages_exist(self):
        for sport in self.fixture_doc["sports"]:
            slug = self.fixture_map[next(f["id"] for f in self.fixtures if f["sport"] == sport)]["slug"]
            self.assertTrue((SITE / "sports" / f"{slug}.html").is_file(), sport)

    def test_relative_links_assets_and_fragments(self):
        for page in SITE.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            for match in re.finditer(r'(?:href|src)="([^"]+)"', text):
                href = html.unescape(match.group(1))
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (page.parent / unquote(parsed.path)).resolve()
                if target.is_dir():
                    target = target / "index.html"
                self.assertTrue(target.is_file(), f"{page.relative_to(SITE)} -> {href}")
                if parsed.fragment and target.suffix == ".html":
                    target_text = target.read_text(encoding="utf-8")
                    self.assertRegex(target_text, rf'id="{re.escape(parsed.fragment)}"',
                                     f"{page.relative_to(SITE)} -> {href}")

    def test_no_duplicate_ids_and_page_basics(self):
        for page in SITE.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            ids = re.findall(r'\bid="([^"]+)"', text)
            self.assertEqual(len(ids), len(set(ids)), page)
            self.assertIn('<html lang="en">', text)
            self.assertIn('<meta name="viewport"', text)
            self.assertIn('<main id="main"', text)
            self.assertIn("Content-Security-Policy", text)

    def test_fixture_pages_link_all_their_official_sources(self):
        for f in self.fixtures:
            text = (SITE / "sports" / f"{f['slug']}.html").read_text(encoding="utf-8")
            self.assertIn(f'id="{f["id"]}"', text)
            for sid in f["source_ids"]:
                self.assertIn(html.escape(self.sources[sid]["url"], quote=True), text, f"{f['id']} / {sid}")

    def test_review_anchors_exist_for_every_finding(self):
        text = (SITE / "flagged.html").read_text(encoding="utf-8")
        for flag in self.flagged["flags"]:
            self.assertIn(f'id="{flag["id"]}"', text, flag["id"])

    def test_no_browser_network_or_localhost(self):
        js = (SITE / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("fetch(", js)
        self.assertNotIn("XMLHttpRequest", js)
        self.assertNotIn("localhost", js)
        self.assertNotIn("127.0.0.1", js)
        self.assertIn("Date.now()", js)

    def test_high_and_prediction_pages_do_not_claim_picks(self):
        high = (SITE / "high-confidence.html").read_text(encoding="utf-8")
        predictions = (SITE / "predictions.html").read_text(encoding="utf-8")
        self.assertIn("Zero High picks", high)
        self.assertIn("Not publishable", high)
        self.assertIn("No prediction articles published", predictions)
        self.assertNotIn("Selection:", predictions)

    def test_repo_inventory_hashes(self):
        inventory = load("repo-inventory.json")
        self.assertTrue(inventory["files"])
        for record in inventory["files"]:
            path = ROOT / record["path"]
            self.assertTrue(path.is_file(), record["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"], record["path"])

    def test_recorded_validation_never_hides_failure(self):
        validation = load("validation.json") if (DATA / "validation.json").exists() else {"commands": []}
        for command in validation["commands"]:
            self.assertIn("exit_code", command)
            self.assertIn("finished_at", command)
            self.assertTrue(command["command"])


if __name__ == "__main__":
    unittest.main()
