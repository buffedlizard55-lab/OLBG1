import json, re, unittest
from pathlib import Path

DESK = Path("data/a4803a7b/desk.json")

class TestDeskA4803(unittest.TestCase):
    def test_desk_exists(self):
        self.assertTrue(DESK.is_file(), "desk.json missing")

    def test_band_and_confidence(self):
        j = json.loads(DESK.read_text())
        for f in j["fixtures"]:
            if f["confidence"] == "High":
                self.assertGreaterEqual(f["decimal"], 1.40, f"High out of band {f['id']}")
                self.assertLessEqual(f["decimal"], 101.0)
                self.assertGreaterEqual(f["p"], 0.60, f"High prob too low {f['id']}")
            if f["confidence"] == "Medium":
                self.assertGreaterEqual(f["decimal"], 1.40)
                self.assertLessEqual(f["decimal"], 101.0)
                self.assertGreaterEqual(f["p"], 0.55)

    def test_predictions_word_count_and_selection(self):
        j = json.loads(DESK.read_text())
        for f in j["fixtures"]:
            wc = len(f["prediction"].split())
            self.assertGreaterEqual(wc, 48, f"prediction too short {f['id']} {wc}")
            self.assertIn(f["selection"], f["prediction"], f"selection not named {f['id']}")
            self.assertIsNone(re.search(r"\b(unsure|perhaps|maybe|might|could be|possibly)\b", f["prediction"], re.I))

    def test_seven_gram_uniqueness(self):
        j = json.loads(DESK.read_text())
        seen=set()
        for f in j["fixtures"]:
            toks = re.findall(r"\w+", f["prediction"].lower())
            grams = set(tuple(toks[i:i+7]) for i in range(len(toks)-6))
            inter = grams & seen
            self.assertFalse(inter, f"duplicate 7-gram in {f['id']} {next(iter(inter)) if inter else ''}")
            seen |= grams

    def test_sport_coverage(self):
        j = json.loads(DESK.read_text())
        from collections import Counter
        c = Counter(f["sport"] for f in j["fixtures"])
        self.assertEqual(len(c), 15, f"expected 15 sports got {len(c)}")
        for sport, n in c.items():
            self.assertEqual(n, 5, f"{sport} expected 5 got {n}")

    def test_official_links(self):
        j = json.loads(DESK.read_text())
        for f in j["fixtures"]:
            self.assertTrue(f["official_url"].startswith("http"), f"missing official_url {f['id']}")
            self.assertTrue(f["olbg_url"].startswith("http"))

    def test_site_exists(self):
        self.assertTrue(Path("a4803a7b/index.html").is_file())
        self.assertTrue(Path("a4803a7b/picks.html").is_file())
        self.assertTrue(Path("a4803a7b/predictions.html").is_file())
        self.assertTrue(Path("a4803a7b/matches.html").is_file())
        self.assertTrue(Path("a4803a7b/markets.html").is_file())

if __name__ == "__main__":
    unittest.main()
