"""Publication gate for the e58210b8 desk.

Cheap and read-only: it runs the desk's own validator, then re-asserts from
``data/e58210b8/lines.json`` the invariants the brief is strictest about, so a
hand edit to the JSON or a hand edit to the HTML cannot pass silently.

The band rule is checked in *decimal* terms as well as American terms, because
``-250 <= us <= 10000`` reads as an ordering trap: a -337 favourite is shorter
than -250, not "at least -250".
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
LINES = ROOT / "data" / "e58210b8" / "lines.json"
DESK = ROOT / "e58210b8"
VALIDATOR = SCRIPTS / "se58210b8_validate.py"

BAND_LOW_AMERICAN = -250
BAND_HIGH_AMERICAN = 10000
BAND_LOW_DECIMAL = 1.0 + 100 / 250  # -250 == 1.400 decimal
BAND_HIGH_DECIMAL = 101.0           # +10000 == 101.000 decimal
MIN_HIGH_PROBABILITY = 0.70
BANNED = ("model", "verified")


@unittest.skipUnless(LINES.is_file(), "desk data not present")
class DeskE58210B8Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lines = json.loads(LINES.read_text(encoding="utf-8"))
        cls.books = cls.lines["books"]
        cls.priced = [b for b in cls.books if not b.get("unpriced")]

    def test_validator_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR)], cwd=str(SCRIPTS),
            capture_output=True, text=True, timeout=180)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_every_book_is_priced_or_explicitly_unpriced(self) -> None:
        for book in self.books:
            with self.subTest(book=book["id"]):
                if book.get("unpriced"):
                    self.assertTrue(book.get("unpriced_reason"))
                    self.assertEqual(book["markets"], [])
                else:
                    self.assertTrue(book["pick"])
                    self.assertGreater(book["pick_probability"], 0.5)

    def test_outcome_probabilities_sum_to_one_and_prices_are_fair(self) -> None:
        for book in self.priced:
            for market in book["markets"]:
                with self.subTest(book=book["id"], market=market["market"]):
                    self.assertAlmostEqual(
                        sum(o["probability"] for o in market["outcomes"]), 1.0, places=9)
                    for outcome in market["outcomes"]:
                        self.assertAlmostEqual(
                            outcome["fair_decimal"], 1.0 / outcome["probability"], delta=0.001)

    def test_band_flag_agrees_with_american_and_decimal_terms(self) -> None:
        """The two readings of the band must agree; they did not before this check."""
        for book in self.priced:
            us, dec = book["pick_american"], book["pick_decimal"]
            american_ok = BAND_LOW_AMERICAN <= us <= BAND_HIGH_AMERICAN
            decimal_ok = dec >= BAND_LOW_DECIMAL and dec <= BAND_HIGH_DECIMAL
            with self.subTest(book=book["id"], us=us, dec=dec):
                self.assertEqual(book["pick_in_window"], american_ok)
                self.assertEqual(book["pick_in_window"], decimal_ok)

    def test_high_tier_requires_the_probability_floor(self) -> None:
        for book in self.priced:
            with self.subTest(book=book["id"]):
                if book["confidence"] == "high":
                    self.assertGreaterEqual(book["pick_probability"], MIN_HIGH_PROBABILITY)
                else:
                    self.assertLess(book["pick_probability"], MIN_HIGH_PROBABILITY)

    def test_out_of_window_high_calls_are_disclosed_not_hidden(self) -> None:
        """All four >70% calls price shorter than -250; the desk must say so."""
        high = [b for b in self.priced if b["confidence"] == "high"]
        self.assertEqual(len(high), 4)
        for book in high:
            with self.subTest(book=book["id"]):
                self.assertLess(book["pick_american"], BAND_LOW_AMERICAN)
                self.assertFalse(book["high_and_in_window"])
        text = (DESK / "high-confidence.html").read_text(encoding="utf-8")
        for book in high:
            self.assertIn(f"{book['pick_american']:+d}", text)
        self.assertIn("shorter than", text)

    def test_strongest_in_window_call_is_labelled_medium(self) -> None:
        """Nothing above 70% sits in the band, so no in-window call may read as high."""
        in_window = [b for b in self.priced if b["pick_in_window"]]
        self.assertTrue(in_window)
        best = max(in_window, key=lambda b: b["pick_probability"])
        self.assertEqual(best["id"], "nhl-2026020168")  # Anaheim at Philadelphia, -214
        self.assertEqual(best["confidence"], "medium")
        index = (DESK / "index.html").read_text(encoding="utf-8")
        self.assertIn(f"{best['pick_american']:+d}", index)

    def test_predictions_clear_the_writing_rules(self) -> None:
        import se58210b8_data as data
        import se58210b8_predictions as preds

        sources = {s["id"]: s for s in data.SOURCES}
        self.assertEqual(len(preds.PREDICTIONS), 6)
        self.assertEqual({p["fixture_id"] for p in preds.PREDICTIONS},
                         {"nhl-2026020174", "nhl-2026020169", "nhl-2026020170",
                          "nhl-2026020176", "nhl-2026020168", "nhl-2026020175"})
        bodies = []
        for item in preds.PREDICTIONS:
            body, selection = item["text"], item["selection"]
            words = body.split()
            lowered = body.lower()
            with self.subTest(fixture=item["fixture_id"]):
                self.assertGreaterEqual(len(words), 30)
                for banned in BANNED:
                    self.assertNotIn(banned, lowered)
                self.assertIn(selection, body)
                self.assertTrue(item["sources"])
                for sid in item["sources"]:
                    self.assertTrue(sources[sid]["url"].startswith("https://"), sid)
            bodies.append(body)
        self.assertEqual(len(bodies), len(set(bodies)), "duplicate prediction text")

    def test_pages_exist_and_sport_pages_cover_all_fifteen(self) -> None:
        import se58210b8_data as data

        for name in ("index.html", "matches.html", "markets.html", "high-confidence.html",
                     "predictions.html", "flagged.html", "methodology.html", "sources.html",
                     "analysis.html"):
            self.assertTrue((DESK / name).is_file(), name)
        for slug in data.SPORT_LABEL:
            self.assertTrue((DESK / "sports" / f"{slug}.html").is_file(), slug)
        index = (DESK / "index.html").read_text(encoding="utf-8")
        for slug in data.SPORT_LABEL:
            self.assertIn(f"sports/{slug}.html", index)

    def test_coverage_gaps_are_published_not_silently_dropped(self) -> None:
        import se58210b8_data as data

        flagged = (DESK / "flagged.html").read_text(encoding="utf-8")
        covered = {b["sport"] for b in self.books}
        self.assertEqual(covered, {"ice_hockey", "baseball"})
        for slug in data.SPORT_LABEL:
            if slug not in covered:
                with self.subTest(sport=slug):
                    self.assertIn(slug, data.COVERAGE_GAPS)
                    self.assertIn(data.COVERAGE_GAPS[slug][:40], flagged)


if __name__ == "__main__":
    unittest.main()
