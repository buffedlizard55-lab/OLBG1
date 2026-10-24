#!/usr/bin/env python3
"""Desk 37737303 gate: scope, provenance, arithmetic, prose and site links.

The desk covers exactly the fifteen sports in the brief. Every price is our own
zero-margin arithmetic, every fact cites an official page read this session,
and the confidence label has to follow the published rule rather than being
assigned by hand.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "37737303"
DESK = ROOT / "37737303"

BRIEF_SPORTS = {"golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
                "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball", "ice-hockey",
                "basketball", "rugby-league"}
BANNED = ("model", "verified", "verification", "hallucinat", "algorithm")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class DeskData:
    fixtures = load("fixtures.json")["fixtures"]
    sources = {s["id"]: s for s in load("sources.json")["sources"]}
    coverage = load("coverage.json")
    flags = load("flags.json")["flags"]
    predictions = load("predictions.json")["predictions"]

    @staticmethod
    def row(fid):
        return next(f for f in DeskData.fixtures if f["id"] == fid)


def american(prob: float) -> int:
    raw = -100.0 * prob / (1 - prob) if prob >= 0.5 else 100.0 * (1 - prob) / prob
    return int(round(raw / 5.0) * 5)


class TestScope(unittest.TestCase):
    def test_all_fifteen_brief_sports_have_a_page_and_a_coverage_row(self):
        sports = {s["sport"] for s in DeskData.coverage["sports"]}
        self.assertTrue(BRIEF_SPORTS <= sports)
        for sport in BRIEF_SPORTS:
            self.assertTrue((DESK / "sports" / f"{sport}.html").is_file(), sport)

    def test_every_sport_is_either_picked_or_explicitly_without_a_market(self):
        with_picks = {f["sport"] for f in DeskData.fixtures}
        without = {n["sport"] for n in DeskData.coverage["no_market"]}
        self.assertEqual(with_picks | without, BRIEF_SPORTS)
        self.assertFalse(with_picks & without)


class TestPricing(unittest.TestCase):
    def test_prices_are_arithmetic_not_copied(self):
        for f in DeskData.fixtures:
            for m in f["markets"]:
                self.assertLessEqual(abs(american(m["prob"]) - m["fair"]), 5, (f["id"], m))
                self.assertEqual(m["decimal"], round(1 / m["prob"], 2), (f["id"], m))
                self.assertGreater(m["prob"], 0.02, f["id"])
                self.assertLess(m["prob"], 0.98, f["id"])

    def test_every_pick_is_one_of_its_own_published_markets(self):
        for f in DeskData.fixtures:
            pairs = {(m["market"], m["side"]) for m in f["markets"]}
            self.assertIn((f["pick"]["market"], f["pick"]["selection"]), pairs, f["id"])

    def test_confidence_follows_the_published_rule(self):
        for f in DeskData.fixtures:
            p = f["pick"]["prob"]
            fair = f["pick"]["fair"]
            in_band = -250 <= fair <= 10000
            expected = "low"
            if in_band:
                if p >= 0.60 and f["evidence"] in ("both", "one"):
                    expected = "high"
                elif p >= 0.55 and f["evidence"] in ("both", "one", "fixture"):
                    expected = "medium"
                elif p >= 0.60 and f["evidence"] == "sentiment":
                    expected = "medium"
            self.assertEqual(f["confidence"], expected, f["id"])

    def test_no_high_pick_sits_outside_the_brief_band(self):
        for f in DeskData.fixtures:
            if f["confidence"] == "high":
                self.assertTrue(-250 <= f["pick"]["fair"] <= 10000, f["id"])
                self.assertIn(f["evidence"], ("both", "one"), f["id"])


class TestProvenance(unittest.TestCase):
    def test_facts_only_cite_official_sources(self):
        for f in DeskData.fixtures:
            for fact in f["facts"]:
                src = DeskData.sources[fact["source"]]
                self.assertEqual(src["kind"], "official", (f["id"], fact))
                self.assertTrue(src["status"].startswith("read"), (f["id"], fact))

    def test_every_fixture_links_an_olbg_event_and_a_resolvable_source(self):
        for f in DeskData.fixtures:
            self.assertTrue(f["olbg_url"].startswith("https://www.olbg.com/"), f["id"])
            self.assertIn(f["official_source"], DeskData.sources, f["id"])

    def test_flag_sources_resolve(self):
        for flag in DeskData.flags:
            for sid in flag["sources"]:
                self.assertIn(sid, DeskData.sources, (flag["id"], sid))


class TestPredictions(unittest.TestCase):
    def test_predictions_are_at_least_thirty_words(self):
        for pred in DeskData.predictions:
            self.assertGreaterEqual(len(pred["text"].split()), 30, pred["id"])

    def test_predictions_avoid_internal_vocabulary(self):
        for pred in DeskData.predictions:
            low = pred["text"].lower()
            for word in BANNED:
                self.assertNotIn(word, low, (pred["id"], word))

    def test_predictions_are_not_templated_repeats(self):
        seen = {}
        for pred in DeskData.predictions:
            tokens = re.findall(r"[a-z0-9']+", pred["text"].lower())
            for i in range(len(tokens) - 5):
                gram = " ".join(tokens[i:i + 6])
                self.assertNotIn(gram, seen, (pred["id"], seen.get(gram), gram))
                seen[gram] = pred["id"]

    def test_every_prediction_names_its_selection_and_a_side(self):
        for pred in DeskData.predictions:
            row = DeskData.row(pred["id"])
            text = pred["text"].lower()
            sel = [w.strip(".,()").lower() for w in pred["selection"].replace("-", " ").split()]
            self.assertTrue(any(len(w) > 3 and w in text for w in sel), pred["id"])
            sides = [w.strip(".,()").lower() for t in (row["home"], row["away"]) for w in t.split()]
            self.assertTrue(any(len(w) > 3 and w in text for w in sides), pred["id"])

    def test_no_prediction_on_a_fixture_with_no_input_at_all(self):
        for pred in DeskData.predictions:
            self.assertNotEqual(DeskData.row(pred["id"])["evidence"], "none", pred["id"])


class TestPublication(unittest.TestCase):
    def test_coverage_counts_match_the_data(self):
        c = DeskData.coverage["counts"]
        self.assertEqual(c["fixtures"], len(DeskData.fixtures))
        self.assertEqual(c["picks"], len(DeskData.fixtures))
        self.assertEqual(c["markets"], sum(len(f["markets"]) for f in DeskData.fixtures))
        self.assertEqual(c["predictions"], len(DeskData.predictions))
        self.assertEqual(c["flags"], len(DeskData.flags))
        self.assertEqual(c["high"], sum(1 for f in DeskData.fixtures if f["confidence"] == "high"))
        self.assertEqual(c["sports_with_picks"] + c["sports_without_market"], 15)

    def test_desk_validator_script_passes(self):
        result = subprocess.run([sys.executable, "scripts/s37737303_validate.py"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_headline_page_states_the_count_and_points_at_the_write_ups(self):
        text = (DESK / "index.html").read_text(encoding="utf-8")
        c = DeskData.coverage["counts"]
        self.assertIn(f"{c['picks']} picks", text)
        self.assertIn("predictions.html#", text)
        self.assertIn("Executive summary", text)

    def test_no_broken_internal_links_in_the_desk(self):
        for page in DESK.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            for href in re.findall(r'href="([^"#:]+\.html)"', text):
                self.assertTrue((page.parent / href).resolve().exists(), (page.name, href))


if __name__ == "__main__":
    unittest.main()
