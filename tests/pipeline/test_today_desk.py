"""Contract tests for the clarity desk at today/ (session 7f1bf9f7-olbg1)."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import today_data as D  # noqa: E402

SITE = ROOT / "today"


class DataContract(unittest.TestCase):
    def test_fifteen_sports_in_brief_order(self):
        self.assertEqual(len(D.SPORTS), 15)
        self.assertEqual([s[1] for s in D.SPORTS], [
            "Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts",
            "Baseball", "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing",
            "Handball", "Ice Hockey", "Basketball", "Rugby League"])

    def test_every_fixture_has_an_official_source(self):
        official = ("nhle.com", "mlb.com", "formula1.com", "atptour.com")
        for f in D.FIXTURES:
            self.assertIn(f["source_id"], D.SOURCES)
            url = D.SOURCES[f["source_id"]]["url"]
            self.assertTrue(url.startswith("https://"), f["id"])
            self.assertTrue(any(h in url for h in official), f["id"])

    def test_unread_values_are_blank_not_guessed(self):
        for f in D.FIXTURES:
            for value in f["facts"].values():
                self.assertNotEqual(value, "", f["id"])
        # the known gaps must stay None rather than be filled in
        mlb = next(f for f in D.FIXTURES if f["id"] == "B-01")
        self.assertIsNone(mlb["facts"]["Milwaukee Brewers"])

    def test_market_probabilities_are_in_range(self):
        for m in D.MARKETS:
            self.assertGreater(m["prob"], 0)
            self.assertLess(m["prob"], 1)
            self.assertTrue(m["basis"], m["selection"])

    def test_every_pick_names_a_known_fixture(self):
        ids = {f["id"] for f in D.FIXTURES}
        for p in D.PICKS:
            self.assertIn(p["fixture"], ids)


class PredictionContract(unittest.TestCase):
    def test_predictions_are_long_enough(self):
        for p in D.PICKS:
            self.assertGreaterEqual(len(p["prediction"].split()), 30, p["fixture"])

    def test_predictions_avoid_banned_vocabulary(self):
        for p in D.PICKS:
            for word in ("model", "verified"):
                self.assertIsNone(re.search(rf"\b{word}\b", p["prediction"].lower()), p["fixture"])

    def test_predictions_are_unique_and_state_the_selection(self):
        seen = set()
        for p in D.PICKS:
            self.assertNotIn(p["prediction"], seen)
            seen.add(p["prediction"])
            self.assertIn(p["selection"].split()[0].lower(), p["prediction"].lower())

    def test_high_picks_sit_inside_the_briefs_band(self):
        for p in D.PICKS:
            if p["confidence"] == "High":
                dec = 1 / p["prob"]
                fair = round((dec - 1) * 100) if dec >= 2 else round(-100 / (dec - 1))
                self.assertGreaterEqual(p["prob"], 0.70)
                self.assertGreaterEqual(fair, -250)


class SiteContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "scripts" / "today_build.py")],
                       check=True, capture_output=True)

    def test_pages_exist(self):
        for name in ("index.html", "picks.html", "predictions.html", "matches.html",
                     "discovery.html", "markets.html", "sports.html", "flagged.html",
                     "repo-audit.html", "sources.html", "methodology.html"):
            self.assertTrue((SITE / name).is_file(), name)
        for slug, *_ in D.SPORTS:
            self.assertTrue((SITE / "sports" / f"{slug}.html").is_file(), slug)

    def test_validator_passes(self):
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "today_validate.py")],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_front_page_puts_picks_first(self):
        body = (SITE / "index.html").read_text(encoding="utf-8")
        self.assertLess(body.index("highest confidence first"),
                        body.index("How to read this desk"))
        for p in D.PICKS:
            self.assertIn(p["selection"].replace("'", "&#x27;"), body)

    def test_no_remote_assets(self):
        for page in SITE.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotIn('<script', text.lower(), page.name)
            self.assertNotIn('src="http', text.lower(), page.name)

    def test_exports_are_written(self):
        picks = json.loads((SITE / "data" / "picks.json").read_text(encoding="utf-8"))
        self.assertEqual(picks["counts"]["picks"], len(D.PICKS))
        self.assertTrue((SITE / "data" / "picks.csv").is_file())
        self.assertTrue((SITE / "data" / "discovery.json").is_file())
        self.assertTrue((SITE / "data" / "flags.json").is_file())


if __name__ == "__main__":
    unittest.main()
