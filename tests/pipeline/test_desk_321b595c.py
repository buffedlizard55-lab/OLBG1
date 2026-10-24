"""Contract tests for desk 321b595c (24 October 2026).

Run with:  python3 -m pytest tests/pipeline/test_desk_321b595c.py -q
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import s321b595c_data as D  # noqa: E402

DATA = ROOT / "data" / "321b595c"
SITE = ROOT / "321b595c"


def load(name):
    return json.loads((DATA / f"{name}.json").read_text())


class DeskContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {s["id"]: s for s in load("sources")["sources"]}
        cls.fixtures = load("fixtures")["fixtures"]
        cls.preds = load("predictions")["predictions"]
        cls.flags = load("flags")["flags"]
        cls.coverage = load("coverage")["sports"]
        cls.summary = load("summary")

    def test_the_brief_scope_is_exactly_fifteen_sports(self):
        self.assertEqual(len(self.coverage), 15)
        self.assertEqual({c["sport"] for c in self.coverage}, {s[0] for s in D.SPORTS})

    def test_every_fixture_carries_a_discovery_link_and_a_source(self):
        for f in self.fixtures:
            self.assertTrue(f["olbg_url"].startswith("https://www.olbg.com/"), f["id"])
            self.assertTrue(f["sources"], f["id"])
            for s in f["sources"]:
                self.assertIn(s, self.sources, f["id"])

    def test_no_pick_without_a_priceable_model_and_an_official_source(self):
        for f in self.fixtures:
            if f["selection"]:
                self.assertTrue(f["priced"], f["id"])
                self.assertTrue(f["model"], f["id"])
                kinds = {self.sources[s]["kind"] for s in f["sources"]}
                self.assertIn("official", kinds, f["id"])

    def test_confidence_labels_follow_the_published_bands(self):
        for f in self.fixtures:
            if not f["selection"]:
                continue
            want = "High" if f["prob"] >= 0.65 else ("Medium" if f["prob"] >= 0.575 else "Low")
            self.assertEqual(f["confidence"], want, f["id"])

    def test_every_fair_price_sits_inside_the_brief_band(self):
        for f in self.fixtures:
            if f["selection"]:
                self.assertGreaterEqual(f["fair"], -250, f["id"])
                self.assertLessEqual(f["fair"], 10000, f["id"])

    def test_high_predictions_clear_the_word_floor(self):
        for p in self.preds:
            self.assertGreaterEqual(p["words"], 30, p["fixture_id"])

    def test_predictions_avoid_internal_vocabulary(self):
        for p in self.preds:
            self.assertNotRegex(p["text"].lower(), r"\b(model|verified)\b", p["fixture_id"])

    def test_predictions_are_textually_distinct(self):
        for a in self.preds:
            for b in self.preds:
                if a is b:
                    continue
                self.assertNotEqual(a["text"], b["text"])

    def test_every_sport_states_why_it_has_fewer_than_five_picks(self):
        for c in self.coverage:
            if c["predictions"] < 5:
                self.assertTrue(c["blocker"].strip(), c["sport"])
                self.assertIn(c["blocker_source"], self.sources, c["sport"])

    def test_flags_reference_known_sources(self):
        for f in self.flags:
            self.assertTrue(f["sources"], f["id"])
            for s in f["sources"]:
                self.assertIn(s, self.sources, f["id"])

    def test_summary_agrees_with_the_tables(self):
        self.assertEqual(self.summary["fixtures"], len(self.fixtures))
        self.assertEqual(self.summary["predictions"], len(self.preds))
        self.assertEqual(self.summary["picks"], len([f for f in self.fixtures if f["selection"]]))
        self.assertEqual(self.summary["flags"], len(self.flags))
        self.assertEqual(self.summary["sources"], len(self.sources))

    def test_site_is_built_with_all_category_pages(self):
        for page in ("index.html", "picks.html", "predictions.html", "matches.html", "markets.html",
                     "coverage.html", "sources.html", "flagged.html", "methodology.html", "repo-review.html"):
            self.assertTrue((SITE / page).is_file(), page)
        for sport in (s[0] for s in D.SPORTS):
            self.assertTrue((SITE / "sports" / f"{sport}.html").is_file(), sport)

    def test_landing_page_puts_the_picks_above_the_fold(self):
        html = (SITE / "index.html").read_text()
        head = html[: html.index("</body>")]
        self.assertIn("executive summary", head.lower())
        self.assertIn("Today&rsquo;s picks", head)
        self.assertLess(head.lower().index("read this first"), head.lower().index("all fifteen sports"))

    def test_validator_passes(self):
        import importlib
        v = importlib.import_module("s321b595c_validate")
        self.assertEqual(v.main(), 0)


if __name__ == "__main__":
    unittest.main()
