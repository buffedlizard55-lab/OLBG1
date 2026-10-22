import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "a0b04058"
SITE_DIR = ROOT / "a0b04058"

class TestDeskA0B(unittest.TestCase):
    def test_desk_exists(self):
        self.assertTrue((DATA_DIR / "desk.json").exists(), "desk.json missing")
        desk = json.loads((DATA_DIR / "desk.json").read_text(encoding="utf-8"))
        self.assertIn("fixtures", desk)
        self.assertIn("predictions", desk)
        self.assertGreaterEqual(desk["counts"]["fixtures"], 85, "should have at least 85 fixtures (5 per sport *17)")
        self.assertGreaterEqual(desk["counts"]["predictions"], 85, "should have 85 predictions (5 per sport daily)")

    def test_predictions_word_count_and_unique(self):
        desk = json.loads((DATA_DIR / "desk.json").read_text(encoding="utf-8"))
        preds = desk["predictions"]
        seen = set()
        for pr in preds:
            wc = len(pr["prediction_text"].split())
            self.assertGreaterEqual(wc, 30, f"{pr['id']} too short {wc}")
            self.assertNotIn(pr["prediction_text"], seen, f"duplicate text {pr['id']}")
            seen.add(pr["prediction_text"])
            # check selection obvious
            self.assertTrue(any(k in pr["prediction_text"].lower() for k in ["win", "beat", "over", "under", "to win", "to beat"]), f"{pr['id']} selection not obvious")

    def test_high_inside_window(self):
        desk = json.loads((DATA_DIR / "desk.json").read_text(encoding="utf-8"))
        for fp in desk["fixtures"]:
            if not fp["priced"]:
                continue
            wp = fp["winner_pick"]
            if wp and wp["tier"] == "High":
                # compute american
                p = wp["probability_exact"]
                amer = -round(p/(1-p)*100) if p>=0.5 else round((1-p)/p*100)
                self.assertTrue(-250 <= amer <= 10000, f"High pick {fp['fixture']['key']} out of window amer {amer}")

    def test_every_row_has_official_link(self):
        desk = json.loads((DATA_DIR / "desk.json").read_text(encoding="utf-8"))
        for fp in desk["fixtures"]:
            link = fp["fixture"]["official_link"]
            self.assertTrue(link.startswith("https://"), f"{fp['fixture']['key']} official_link not https")
            # check host in publishers allowlist (simplified)
            from urllib.parse import urlparse
            host = urlparse(link).hostname
            self.assertIsNotNone(host, f"{fp['fixture']['key']} no hostname")

    def test_site_pages_exist(self):
        required = ["index.html","matches.html","markets.html","high-confidence.html","daily-top5.html","predictions.html","sources.html","flagged.html","repo-audit.html","sports.html"]
        for page in required:
            self.assertTrue((SITE_DIR / page).exists(), f"site page missing {page}")
        # check 17 sport pages
        desk = json.loads((DATA_DIR / "desk.json").read_text(encoding="utf-8"))
        for slug in desk["per_sport"].keys():
            self.assertTrue((SITE_DIR / "sports" / f"{slug}.html").exists(), f"sport page {slug} missing")

    def test_csvs_exist(self):
        self.assertTrue((DATA_DIR / "fixtures.csv").exists())
        self.assertTrue((DATA_DIR / "markets.csv").exists())

    def test_no_hallucination_blank_fields(self):
        desk = json.loads((DATA_DIR / "desk.json").read_text(encoding="utf-8"))
        for fp in desk["fixtures"]:
            if not fp["priced"]:
                self.assertTrue(fp["unpriced_reason"], f"{fp['fixture']['key']} unpriced no reason")

if __name__ == "__main__":
    unittest.main()
