"""TFF99 desk gates (session ff993cb9)."""
import json, re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESK = json.loads((ROOT / "data" / "ff993cb9" / "desk.json").read_text())
PICKS = DESK["picks"]
OUT = ROOT / "ff993cb9"

class TestDeskFF993CB9(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(PICKS), 80)
        self.assertEqual(DESK["counts"]["high"], 3)
        self.assertEqual(len(DESK["flags"]), 14)

    def test_band_and_ratings(self):
        for p in PICKS:
            am = int(p["fair_american"])
            self.assertGreaterEqual(am, -250, p["id"])
            self.assertLessEqual(am, 10000, p["id"])
            if p["confidence"] == "High":
                self.assertGreaterEqual(p["prob"], 0.70, p["id"])

    def test_prose_rules(self):
        for p in PICKS:
            self.assertGreaterEqual(p["words"], 30, p["id"])
            low = p["prediction"].lower()
            self.assertNotIn("model", low, p["id"])
            self.assertNotIn("verified", low, p["id"])

    def test_official_sources_not_olbg(self):
        for p in PICKS:
            self.assertTrue(p["official"].startswith("https://"), p["id"])
            self.assertNotIn("olbg.com", p["official"], p["id"])

    def test_coverage(self):
        from collections import Counter
        c = Counter(p["sport"] for p in PICKS)
        for s in ["golf","volleyball","cricket","darts","gaelic-sports","tennis",
                  "motor-racing","handball","ice-hockey","basketball","rugby-league"]:
            self.assertGreaterEqual(c[s], 5, s)
        self.assertEqual(c.get("greyhounds", 0), 0)

    def test_pages_exist_and_single_h1(self):
        for name in ["index.html","picks.html","predictions.html","matches.html","markets.html",
                     "sports.html","flagged.html","sources.html","methodology.html","olbg.html","repo-audit.html"]:
            f = OUT / name
            self.assertTrue(f.exists(), name)
            self.assertEqual(f.read_text().count("<h1"), 1, name)
        for s in ["golf","volleyball","rugby-union","cricket","snooker","darts","baseball","gaelic-sports",
                  "greyhounds","tennis","motor-racing","handball","ice-hockey","basketball","rugby-league"]:
            self.assertTrue((OUT / "sports" / f"{s}.html").exists(), s)

    def test_index_is_executive_summary(self):
        idx = (OUT / "index.html").read_text()
        self.assertIn("High-confidence picks", idx)
        self.assertIn("Best pick in every sport", idx)
        self.assertIn("The picks are on this page", idx)

    def test_no_broken_internal_links(self):
        for f in OUT.rglob("*.html"):
            for href in re.findall(r'href="([^"#]+)"', f.read_text()):
                if href.startswith(("http", "mailto")):
                    continue
                self.assertTrue((f.parent / href).resolve().exists(), f"{f} -> {href}")

if __name__ == "__main__":
    unittest.main()
