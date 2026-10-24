"""Unit gates for the namespaced 0239d718 OLBG clarity desk."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "0239d718"
SITE = ROOT / "0239d718"


def desk():
    return json.loads((DATA / "desk.json").read_text(encoding="utf-8"))


class Desk0239D718(unittest.TestCase):
    def test_dedicated_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "s0239d718_validate.py")],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 errors", result.stdout)

    def test_fifteen_sports_and_five_picks_each(self):
        d = desk()
        self.assertEqual(len(d["sports"]), 15)
        self.assertEqual(len(d["picks"]), 75)
        by_sport = {}
        for pick in d["picks"]:
            by_sport[pick["sport"]] = by_sport.get(pick["sport"], 0) + 1
        self.assertEqual(set(by_sport), {s["slug"] for s in d["sports"]})
        self.assertTrue(all(v == 5 for v in by_sport.values()), by_sport)

    def test_strict_high_gate(self):
        d = desk()
        highs = [p for p in d["picks"] if p["confidence"] == "high"]
        self.assertGreaterEqual(len(highs), 15)
        for pick in highs:
            self.assertGreater(pick["probability"], 0.70)
            self.assertGreaterEqual(pick["fair_american"], -250)
            self.assertLessEqual(pick["fair_american"], 10000)

    def test_predictions_are_long_distinct_and_clean(self):
        d = desk()
        banned = ("model", "verified", "verification", "algorithm", "machine learning")
        texts = []
        for pick in d["picks"]:
            text = pick["prediction"]
            self.assertGreaterEqual(len(re.findall(r"\b[\w'-]+\b", text)), 30)
            self.assertIn(pick["selection"].lower(), text.lower())
            for word in banned:
                self.assertNotIn(word, text.lower())
            texts.append(text)
        self.assertEqual(len(texts), len(set(texts)))
        seen = {}
        for pick in d["picks"]:
            toks = re.findall(r"\b[\w'-]+\b", pick["prediction"].lower())
            for i in range(len(toks) - 24):
                gram = " ".join(toks[i:i+25])
                seen.setdefault(gram, set()).add(pick["id"])
        # A 25-word passage cannot be shared by two predictions.
        self.assertFalse(any(len(v) > 1 for v in seen.values()))

    def test_key_pages_exist(self):
        for rel in ("index.html", "picks.html", "predictions.html", "matches.html",
                    "markets.html", "sports.html", "categories.html", "sources.html",
                    "flagged.html", "audit.html", "reverse-engineering.html",
                    "methodology.html", "styles.css"):
            self.assertTrue((SITE / rel).is_file(), rel)
        for sport in desk()["sports"]:
            self.assertTrue((SITE / "sports" / f"{sport['slug']}.html").is_file(), sport["slug"])


if __name__ == "__main__":
    unittest.main()
