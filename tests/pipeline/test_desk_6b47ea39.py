"""Offline contract tests for the T6B47 consolidated desk (session 6b47ea39).

No network access. These assert the published artefacts against the rules the
desk claims to follow, so a future edit cannot quietly break a label.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "6b47ea39"
SITE = ROOT / "6b47ea39"
BRIEF_SPORTS = [
    "Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts", "Baseball",
    "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing", "Handball",
    "Ice Hockey", "Basketball", "Rugby League",
]


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class Desk6B47Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slate = load("slate.json")
        cls.picks = load("picks.json")
        cls.preds = load("predictions.json")
        cls.flags = load("flags.json")
        cls.audit = load("audit.json")

    def test_exactly_the_brief_sports(self):
        sports = {e["sport"] for e in self.slate["events"]}
        self.assertEqual(sports, set(BRIEF_SPORTS))
        self.assertEqual(len(self.slate["sports"]), 15)

    def test_fixtures_have_sport_state_and_unique_ids(self):
        ids = [e["id"] for e in self.slate["events"]]
        self.assertEqual(len(ids), len(set(ids)))
        for event in self.slate["events"]:
            self.assertIn(event["sport"], BRIEF_SPORTS)
            self.assertIn(event["state"], {"upcoming", "elapsed", "time not stated"})
            self.assertTrue(event["provenance"], event["id"])

    def test_picks_obey_the_band_label(self):
        for pick in self.picks["picks"]:
            if pick["tier"] == "high-in-window":
                self.assertTrue(-250.0 - 1e-6 <= pick["american"] <= 10000.0 + 1e-6, pick["pick_id"])
                self.assertGreater(pick["probability"], 0.70, pick["pick_id"])
            else:
                self.assertEqual(pick["tier"], "out-of-window")
                self.assertGreater(pick["probability"], 0.70, pick["pick_id"])

    def test_picks_are_upcoming_and_unique_per_fixture(self):
        events = {e["id"]: e for e in self.slate["events"]}
        seen = set()
        for pick in self.picks["picks"]:
            self.assertEqual(events[pick["event_id"]]["state"], "upcoming")
            self.assertNotIn(pick["event_id"], seen)
            seen.add(pick["event_id"])

    def test_every_pick_has_an_official_source(self):
        for pick in self.picks["picks"]:
            self.assertTrue(pick["official_sources"], pick["pick_id"])
            for url in pick["official_sources"]:
                self.assertTrue(url.startswith("https://"), url)

    def test_predictions_meet_the_writing_rules(self):
        banned = ("model", "verified", "verification", "algorithm")
        seen: dict[str, str] = {}
        for row in self.preds["predictions"]:
            words = len(re.findall(r"\b[\w'-]+\b", row["text"]))
            self.assertGreaterEqual(words, 30, row["pick_id"])
            for word in banned:
                self.assertNotRegex(row["text"].lower(), rf"\b{word}\b", row["pick_id"])
            tokens = re.findall(r"[a-z0-9']+", row["text"].lower())
            grams = {" ".join(tokens[i : i + 6]) for i in range(max(0, len(tokens) - 5))}
            for gram in grams:
                self.assertNotIn(gram, seen, f"{row['pick_id']} repeats '{gram}' from {seen.get(gram)}")
                seen[gram] = row["pick_id"]
        self.assertFalse(self.preds["problems"])

    def test_prediction_and_pick_sets_match(self):
        self.assertEqual({p["pick_id"] for p in self.preds["predictions"]}, {p["pick_id"] for p in self.picks["picks"]})

    def test_flags_carry_a_source(self):
        for flag in self.flags["flags"]:
            self.assertTrue(flag["source"], flag["id"])
            self.assertIn(flag["severity"], {"high", "medium", "low", "info"})

    def test_band_arithmetic_is_reported(self):
        high = [f for f in self.flags["flags"] if "1.43" in f["detail"]]
        self.assertTrue(high, "the band-width finding must be published")
        self.assertGreater(self.audit["boundary_clustering"]["lines_between_0.700_and_0.720"], 100)

    def test_every_brief_sport_has_a_page(self):
        for sport in BRIEF_SPORTS:
            slug = sport.lower().replace(" ", "-")
            self.assertTrue((SITE / "sports" / f"{slug}.html").is_file(), sport)

    def test_desk_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "s6b47ea39_validate.py")],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
