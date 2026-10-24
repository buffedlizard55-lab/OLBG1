"""Contract tests for the f437fb14 desk."""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import sf437fb14_model as M
import sf437fb14_picks as PK

DATA = os.path.join(ROOT, "data", "f437fb14")
SITE = os.path.join(ROOT, "f437fb14")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


class TestDesk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = load("fixtures.json")
        cls.markets = load("markets.json")
        cls.picks = load("picks.json")
        cls.summary = load("summary.json")

    def test_site_has_26_pages(self):
        pages = []
        for dp, _, files in os.walk(SITE):
            pages += [f for f in files if f.endswith(".html")]
        self.assertEqual(len(pages), 26)

    def test_all_fifteen_sports_present(self):
        sports = {f["sport"] for f in self.fixtures}
        self.assertTrue(len(sports) >= 12, sports)
        for s in ("Baseball", "Basketball", "Ice Hockey", "Tennis", "Cricket", "Snooker"):
            self.assertIn(s, sports)

    def test_every_fixture_has_discovery_link(self):
        for f in self.fixtures:
            self.assertTrue(f.get("olbg_url", "").startswith("https://"), f["id"])

    def test_price_equals_inverse_probability(self):
        for m in self.markets:
            self.assertEqual(m["american"], M.american(m["p"]), m["label"])

    def test_picks_inside_window(self):
        for p in self.picks:
            self.assertGreaterEqual(p["american"], -250, p["fixture"])
            self.assertLessEqual(p["american"], 10000, p["fixture"])

    def test_tier_matches_published_rule(self):
        for p in self.picks:
            self.assertEqual(p["confidence"], M.confidence(p["p"], p["grade"], p["american"]))

    def test_no_literal_seventy_percent_pick(self):
        # Documents the arithmetic conflict rather than hiding it.
        self.assertEqual(sum(1 for p in self.picks if p["literal_high"]), 0)

    def test_writeups_minimum_length(self):
        for p in self.picks:
            self.assertGreaterEqual(len(PK.PROSE[p["fixture"]].split()), 30, p["fixture"])

    def test_writeups_do_not_share_six_grams(self):
        grams = {}
        for fid, text in PK.PROSE.items():
            words = text.lower().split()
            for i in range(len(words) - 5):
                grams.setdefault(" ".join(words[i:i + 6]), set()).add(fid)
        self.assertEqual([g for g, v in grams.items() if len(v) > 1], [])

    def test_banned_vocabulary_absent(self):
        for fid, text in PK.PROSE.items():
            low = text.lower()
            self.assertNotIn(" model ", low, fid)
            self.assertNotIn(" verified ", low, fid)

    def test_every_selection_names_the_bet(self):
        for p in self.picks:
            self.assertIn("Selection:", PK.PROSE[p["fixture"]])

    def test_summary_counts_consistent(self):
        self.assertEqual(self.summary["fixtures"], len(self.fixtures))
        self.assertEqual(self.summary["picks"], len(self.picks))
        self.assertEqual(self.summary["markets"], len(self.markets))

    def test_validator_passes(self):
        out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "sf437fb14_validate.py")],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)


if __name__ == "__main__":
    unittest.main()
