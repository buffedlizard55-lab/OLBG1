"""Tests for desk 1707d752 — arithmetic, honesty rules and rendered navigation."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import s1707d752_compute as C
import s1707d752_data as D
import s1707d752_model as M

OUT = ROOT / "1707d752"


class Desk1707(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = C.build()
        cls.rows = cls.data["rows"]
        cls.picks = [r for r in cls.rows if r["priced"] and r.get("pick")]

    def test_prices_are_reciprocal_probabilities(self):
        for r in self.picks:
            p = r["pick"]
            self.assertAlmostEqual(p["decimal"], 1 / p["probability"], places=2, msg=r["id"])
            self.assertEqual(p["american"], M.american_from_decimal(1 / p["probability"]), r["id"])

    def test_band_boundaries(self):
        self.assertTrue(M.in_brief_band(-250))
        self.assertTrue(M.in_brief_band(10000))
        self.assertFalse(M.in_brief_band(-251))
        self.assertFalse(M.in_brief_band(10001))

    def test_literal_high_gate_is_a_thin_window(self):
        # -250 is 71.43%, so ">70% and inside the window" is only 70.0-71.4%.
        self.assertFalse(M.brief_literal_high(0.70, -233))
        self.assertFalse(M.brief_literal_high(0.80, -400))
        self.assertTrue(M.brief_literal_high(0.71, -245))

    def test_high_tier_requires_every_condition(self):
        self.assertEqual(M.grade(0.65, complete=True, band=True, sample_games=20, sample_floor=8)["tier"], "High")
        self.assertEqual(M.grade(0.65, complete=True, band=False, sample_games=20, sample_floor=8)["tier"], "Medium")
        self.assertEqual(M.grade(0.65, complete=False, band=True, sample_games=20, sample_floor=8)["tier"], "Medium")
        self.assertNotEqual(M.grade(0.65, complete=True, band=True, sample_games=2, sample_floor=20)["tier"], "High")
        self.assertEqual(M.grade(0.52, complete=True, band=True, sample_games=20, sample_floor=8)["tier"], "Low")

    def test_every_priced_match_has_an_official_source(self):
        official = {s["id"] for s in D.SOURCES if s["official"]}
        for r in self.rows:
            if r["priced"]:
                self.assertTrue(set(r["sources"]) & official, r["id"])

    def test_predictions_state_the_selection_and_clear_the_word_floor(self):
        for r in self.picks:
            p = r["pick"]
            self.assertGreaterEqual(len(p["prose"].split()), 30, r["id"])
            self.assertIn(p["name"], p["prose"], r["id"])
            for banned in ("model", "verified", "verify"):
                self.assertNotIn(banned, p["prose"].lower(), r["id"])

    def test_predictions_are_not_templated(self):
        seen = {}
        for r in self.picks:
            tokens = re.findall(r"[a-z0-9']+", r["pick"]["prose"].lower())
            for i in range(len(tokens) - 5):
                gram = " ".join(tokens[i:i + 6])
                self.assertNotIn(gram, seen, f"{r['id']} repeats {gram} from {seen.get(gram)}")
                seen[gram] = r["id"]

    def test_unpriced_rows_explain_themselves(self):
        for r in self.rows:
            if not r["priced"]:
                self.assertTrue(r.get("incomplete_reason") or r.get("why"), r["id"])
        for r in D.LISTINGS:
            self.assertGreater(len(r["why"]), 15, r["event"])

    def test_pages_exist_and_pick_anchors_are_reachable(self):
        index = (OUT / "index.html").read_text()
        preds = (OUT / "predictions.html").read_text()
        for r in self.picks:
            anchor = r["pick"]["anchor"]
            self.assertIn(f'id="{anchor}"', preds)
            self.assertIn(anchor, index)
        for rel in ("picks.html", "matches.html", "markets.html", "coverage.html",
                    "flagged.html", "sources.html", "method.html", "repo-review.html"):
            self.assertTrue((OUT / rel).is_file(), rel)

    def test_summary_json_matches_the_build(self):
        summary = json.loads((ROOT / "data/1707d752/summary.json").read_text())
        self.assertEqual(summary["picks"], len(self.picks))
        self.assertEqual(summary["matches_priced"], len([r for r in self.rows if r["priced"]]))
        self.assertEqual(summary["high"], sum(1 for r in self.picks if r["pick"]["confidence"] == "High"))

    def test_all_fifteen_requested_sports_are_represented(self):
        wanted = {"Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts", "Baseball",
                  "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing", "Handball",
                  "Ice Hockey", "Basketball", "Rugby League"}
        present = {r["sport"] for r in self.rows} | {r["sport"] for r in D.LISTINGS}
        self.assertEqual(present, wanted)


if __name__ == "__main__":
    unittest.main()
