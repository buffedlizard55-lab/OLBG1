"""Canonical gates for the T65331685 desk (unittest discover target)."""
import json
import os
import re
import unittest
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data", "65331685")
SITE = os.path.join(ROOT, "65331685")
BANNED = ["model", "verified", "verification", "algorithm", "our data shows"]


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


class TestDeskArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.harvest = load("harvest.json")
        cls.fixtures = load("fixtures.json")
        cls.lines = load("lines.json")
        cls.predictions = load("predictions.json")

    def test_artifacts_exist(self):
        for name in ["harvest.json", "fixtures.json", "lines.json", "predictions.json", "desk.json"]:
            self.assertTrue(os.path.exists(os.path.join(DATA, name)), name)

    def test_reads_have_url_and_time(self):
        self.assertGreaterEqual(len(self.harvest["reads"]), 20)
        for r in self.harvest["reads"]:
            self.assertTrue(r["url"].startswith("http"))
            self.assertRegex(r["read_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_fixture_ids_unique_and_unverified_flagged(self):
        seen = set()
        for f in self.fixtures["fixtures"]:
            self.assertNotIn(f["id"], seen)
            seen.add(f["id"])
            self.assertRegex(f["start_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
            if not f["official"]["sources"]:
                self.assertEqual(f["label"], "unverified", f["id"])

    def test_zero_vig_pairs(self):
        pairs = defaultdict(list)
        for g in self.lines["markets"]:
            for m in g["selections"]:
                pairs[(g["fixture_id"], m["market"])].append(m["prob"])
        checked = 0
        for key, probs in pairs.items():
            if len(probs) >= 2:
                self.assertAlmostEqual(sum(probs), 1.0, delta=0.002, msg=str(key))
                checked += 1
        self.assertGreater(checked, 50)

    def test_high_band_gate(self):
        for g in self.lines["markets"]:
            for m in g["selections"]:
                should = m["prob"] > 0.70 and (-250.0 - 1e-6) <= m["fair_american"] <= (10000.0 + 1e-6)
                if should:
                    self.assertEqual(m["tier"], "High", m)
                if m["tier"] == "High":
                    self.assertTrue(should, m)
                if m["tier"] == "Chalk (disclosed)":
                    self.assertGreater(m["prob"], 0.7143, m)

    def test_prediction_policy(self):
        grams = {}
        for p in self.predictions["predictions"]:
            toks = p["text"].lower().split()
            self.assertGreaterEqual(len(toks), 30, p["match"])
            for b in BANNED:
                self.assertIsNone(re.search(r"\b" + re.escape(b) + r"\b", p["text"].lower()),
                                  f"{b} in {p['match']}")
            for i in range(len(toks) - 5):
                g6 = " ".join(toks[i:i + 6])
                self.assertNotIn(g6, grams, f"6-gram {g6}")
                grams[g6] = p["match"]
            for fc in p["facts"]:
                self.assertTrue(fc["source"].startswith("http"))
                self.assertRegex(fc["read_utc"], r"^\d{4}-\d{2}-\d{2}T")

    def test_sport_coverage(self):
        c = Counter(p["sport"] for p in self.predictions["predictions"])
        for sp in ["Ice Hockey", "Baseball", "Basketball", "Rugby Union", "Rugby League", "Cricket",
                   "Tennis", "Snooker", "Darts", "Golf", "Gaelic Sports", "Greyhounds", "Motor Racing",
                   "Handball", "Volleyball"]:
            self.assertGreaterEqual(c.get(sp, 0), 3, sp)

    def test_site_pages(self):
        for page in ["index.html", "sports.html", "matches.html", "markets.html", "high-confidence.html",
                     "predictions.html", "analysis.html", "sources.html", "flagged.html",
                     "repo-audit.html", "methodology.html"]:
            path = os.path.join(SITE, page)
            self.assertTrue(os.path.exists(path), page)
            with open(path) as f:
                content = f.read()
            self.assertIn("T65331685", content)
            self.assertIn("</html>", content)


if __name__ == "__main__":
    unittest.main()
