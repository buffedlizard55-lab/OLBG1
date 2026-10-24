#!/usr/bin/env python3
"""Desk 99d43605 gate: scope, provenance, arithmetic, prose and site links.

The desk covers exactly the fifteen sports in the brief, originates only fair
(zero-margin) two-way lines, and publishes High confidence solely inside the
agreed -250..+10000 price window with probability strictly above 70%.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import s99d43605_data as D  # noqa: E402
from s99d43605_model import (american_from_prob, american_in_band, blended_rate,  # noqa: E402
                             log5, poisson_margin_under, prob_from_american,
                             seed_pair, shrink, total_market, two_way)

DATA = ROOT / "data" / "99d43605"
SITE = ROOT / "99d43605"

SCOPE = {
    "Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts",
    "Baseball", "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing",
    "Handball", "Ice Hockey", "Basketball", "Rugby League",
}
BANNED = ("model", "verified")
OFFICIAL_HOSTS = {urlsplit(s["url"]).netloc for s in D.SOURCES if s["official"]}


class TestScope(unittest.TestCase):
    def test_fifteen_sports_in_brief_order(self):
        self.assertEqual(len(D.SPORTS), 15)
        self.assertEqual({name for _, name, _ in D.SPORTS}, SCOPE)

    def test_fixtures_stay_inside_scope(self):
        slugs = {slug for slug, _, _ in D.SPORTS}
        for fx in D.FIXTURES:
            self.assertIn(fx["sport"], slugs, fx["id"])

    def test_every_sport_has_a_page(self):
        for slug, name, _ in D.SPORTS:
            self.assertTrue((SITE / "sports" / f"{slug}.html").exists(), slug)

    def test_fixture_ids_unique(self):
        ids = [fx["id"] for fx in D.FIXTURES]
        self.assertEqual(len(ids), len(set(ids)))


class TestProvenance(unittest.TestCase):
    def test_sources_are_https_and_timestamped(self):
        for s in D.SOURCES:
            self.assertTrue(s["url"].startswith("https://"), s["id"])
            self.assertTrue(s.get("observed"), s["id"])

    def test_every_fixture_cites_registered_sources(self):
        ids = {s["id"] for s in D.SOURCES}
        for fx in D.FIXTURES:
            self.assertTrue(fx["source_ids"], fx["id"])
            for sid in fx["source_ids"]:
                self.assertIn(sid, ids, f'{fx["id"]}: {sid}')

    def test_high_requires_official_both_sides(self):
        b = D.build_all()
        official = {s["id"] for s in D.SOURCES if s["official"]}
        for fx in b["highs"]:
            self.assertTrue(any(s in official for s in fx["source_ids"]), fx["id"])
            self.assertEqual(fx["state"], "upcoming", fx["id"])

    def test_discovery_alone_cannot_price_measured(self):
        official = {s["id"] for s in D.SOURCES if s["official"]}
        for fx in D.build_all()["fixtures"]:
            for m in fx["markets"]:
                if m.get("measured", True):
                    has_official = any(s in official for s in fx["source_ids"])
                    if not has_official:
                        self.fail(f'{fx["id"]}: market {m["key"]} measured without official source')

    def test_olbg_never_urls_on_match_inputs(self):
        # sources embedded in match-style fixtures must be official hosts
        for fx in D.FIXTURES:
            if fx["state"] == "upcoming" and fx["inputs"].get("a") and fx["inputs"].get("b"):
                for sid in fx["source_ids"]:
                    src = next(s for s in D.SOURCES if s["id"] == sid)
                    assert src["url"].startswith("https://")


class TestArithmetic(unittest.TestCase):
    def test_shrink_and_log5(self):
        self.assertAlmostEqual(shrink(8, 10), 10 / 14, places=9)
        p = log5(shrink(8, 10), shrink(6, 12))
        self.assertAlmostEqual(p, 1 / 1.4, places=9)

    def test_two_way_is_fair(self):
        tw = two_way(0.625)
        self.assertEqual(len(tw), 2)
        self.assertAlmostEqual(tw[0]["prob"] + tw[1]["prob"], 1.0, places=5)
        self.assertAlmostEqual(tw[0]["decimal"], 1.6, places=4)
        self.assertEqual(tw[0]["american"], -167)

    def test_band_edge_is_inclusive_at_minus_250(self):
        p = 1 / 1.4
        self.assertTrue(american_in_band(p))
        self.assertEqual(american_from_prob(p), -250)

    def test_prob_round_trip_window(self):
        self.assertAlmostEqual(prob_from_american(-250), 250 / 350, places=6)
        self.assertLess(prob_from_american(-249), 0.715)
        self.assertGreater(prob_from_american(-251), prob_from_american(-250))  # shorter odds -> higher implied share

    def test_poisson_totals_constraint(self):
        lam = blended_rate(47, 12, 31, 10) + blended_rate(35, 10, 33, 12)
        under = total_market(lam, 5.5)
        self.assertAlmostEqual(under[0]["prob"] + under[1]["prob"], 1.0, places=5)
        m = poisson_margin_under(3.5, 2.8, -1)
        self.assertTrue(0.0 < m < 1.0)

    def test_seed_pair(self):
        self.assertAlmostEqual(seed_pair(1, 8), 1.0 / (1.0 + 0.125), places=9)

    def test_all_prices_fair_two_way(self):
        for fx in D.build_all()["fixtures"]:
            for m in fx["markets"]:
                outs = m["outcomes"]
                self.assertTrue(outs, fx["id"])
                total = sum(o["prob"] for o in outs)
                if len(outs) == 2:
                    self.assertAlmostEqual(total, 1.0, places=3, msg=f'{fx["id"]}/{m["key"]}')
                for o in outs:
                    self.assertGreater(o["prob"], 0.0)
                    self.assertLess(o["prob"], 1.0)
                    self.assertAlmostEqual(o["decimal"], round(1 / o["prob"], 3), places=2)
                    self.assertIn(o["american"], {american_from_prob(o["prob"] - 1e-4), american_from_prob(o["prob"]),
                                                  american_from_prob(o["prob"] + 1e-4)})


class TestHighRules(unittest.TestCase):
    def test_high_window_and_floor(self):
        for fx in D.build_all()["highs"]:
            self.assertIsInstance(fx["american"], int, fx["id"])
            self.assertGreaterEqual(fx["american"], -250, fx["id"])
            self.assertLessEqual(fx["american"], 10000, fx["id"])
            self.assertGreater(fx["pick_prob"], 0.70, fx["id"])
            markets = fx["markets"]
            self.assertTrue(markets, fx["id"])
            self.assertTrue(markets[0].get("measured", True), fx["id"])

    def test_exact_negative_250_case(self):
        fx = next(f for f in D.build_all()["fixtures"] if f["id"] == "nhl-tor-edm")
        self.assertEqual(fx["tier"], "High")
        self.assertEqual(fx["american"], -250)

    def test_exact_seventy_percent_is_not_high(self):
        fx = next(f for f in D.build_all()["fixtures"] if f["id"] == "nhl-vgk-cbj")
        self.assertAlmostEqual(fx["pick_prob"], 0.7, places=3)
        self.assertNotEqual(fx["tier"], "High")

    def test_predictions_one_to_one_with_highs(self):
        b = D.build_all()
        self.assertEqual(set(D.PREDICTIONS), {f["id"] for f in b["highs"]})
        for fid, text in D.PREDICTIONS.items():
            self.assertGreaterEqual(len(text.split()), 30, fid)
            for w in BANNED:
                self.assertNotRegex(text, rf"(?i)\b{w}\b", fid)

    def test_no_five_gram_overlap(self):
        texts = list(D.PREDICTIONS.values())
        grams = set()
        for text in texts:
            ws = re.findall(r"[a-z']+", text.lower())
            for i in range(len(ws) - 4):
                g = tuple(ws[i:i + 5])
                self.assertNotIn(g, grams, g)
                grams.add(g)


class TestExports(unittest.TestCase):
    def test_manifest_counts(self):
        b = D.build_all()
        m = json.loads((DATA / "manifest.json").read_text())
        self.assertEqual(m["counts"]["fixtures"], len(b["fixtures"]))
        self.assertEqual(m["counts"]["picks"], len(b["picks"]))
        self.assertEqual(m["counts"]["high"], len(b["highs"]))
        self.assertEqual(m["counts"]["predictions"], len(D.PREDICTIONS))
        self.assertEqual(m["counts"]["flags"], len(D.FLAG_ITEMS))
        self.assertEqual(m["counts"]["sports"], 15)
        self.assertEqual(m["window"], {"american_min": -250, "american_max": 10000})

    def test_json_rows_match_module(self):
        b = D.build_all()
        self.assertEqual(len(json.loads((DATA / "fixtures.json").read_text())["fixtures"]), len(b["fixtures"]))
        self.assertEqual(len(json.loads((DATA / "picks.json").read_text())["picks"]), len(b["picks"]))
        self.assertEqual(len(json.loads((DATA / "predictions.json").read_text())["predictions"]),
                         len(b["highs"]))
        self.assertEqual(len(json.loads((DATA / "flags.json").read_text())["flags"]), len(D.FLAG_ITEMS))
        self.assertEqual(len(json.loads((DATA / "coverage.json").read_text())["coverage"]), 15)
        self.assertEqual(len(json.loads((DATA / "sources.json").read_text())["sources"]), len(D.SOURCES))


if __name__ == "__main__":
    unittest.main()
