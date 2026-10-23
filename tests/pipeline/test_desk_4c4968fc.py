"""Contract tests for Session 4c4968fc — the fifteen-sport OLBG-derived desk."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "4c4968fc"
SITE = ROOT / "4c4968fc"
SCRIPTS = ROOT / "scripts"

EXPECTED = {
    "golf": "Golf", "volleyball": "Volleyball", "rugby-union": "Rugby Union",
    "cricket": "Cricket", "snooker": "Snooker", "darts": "Darts",
    "baseball": "Baseball", "gaelic-sports": "Gaelic Sports", "greyhounds": "Greyhounds",
    "tennis": "Tennis", "motor-racing": "Motor Racing", "handball": "Handball",
    "ice-hockey": "Ice Hockey", "basketball": "Basketball", "rugby-league": "Rugby League",
}
EXCLUDED = {"soccer", "football", "american-football", "boxing", "mma", "ufc",
            "hurling", "cycling", "horse-racing", "specials"}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class TestDesk4c4968fc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = load("fixtures.json")["fixtures"]
        cls.markets = load("markets.json")["markets"]
        cls.picks = load("picks.json")["picks"]
        cls.preds = load("predictions.json")["predictions"]
        cls.flags = load("flagged.json")["items"]
        cls.sources = load("sources.json")["sources"]
        cls.manifest = load("site-manifest.json")

    # ---------------------------------------------------------------- scope
    def test_scope_is_exactly_the_fifteen_required_sports(self):
        self.assertEqual(len(EXPECTED), 15)
        sports = {f["sport"] for f in self.fixtures}
        self.assertFalse(sports - set(EXPECTED), f"out-of-scope sports: {sports - set(EXPECTED)}")
        self.assertFalse(sports & EXCLUDED)
        # every required sport is either covered or explicitly flagged
        for key in EXPECTED:
            if key not in sports:
                self.assertTrue(any(fl["sport"] == key for fl in self.flags),
                                f"{key} has no fixtures and no flag")

    def test_every_sport_has_a_page_even_without_fixtures(self):
        for key in EXPECTED:
            self.assertTrue((SITE / "sports" / f"{key}.html").exists(), key)

    # ------------------------------------------------------------ provenance
    def test_every_fixture_row_carries_an_official_link(self):
        for f in self.fixtures:
            self.assertTrue(f["sources"], f["id"])
            self.assertTrue(f["facts"], f["id"])
            for s in f["sources"]:
                self.assertTrue(s["url"].startswith("https://"), s)
                self.assertFalse(s["id"].startswith("olbg"),
                                 f"{f['id']} cites OLBG as fixture evidence")

    def test_sources_registry_separates_taxonomy_from_evidence(self):
        roles = {s["id"]: s["role"] for s in self.sources}
        self.assertTrue(any("taxonomy" in r for r in roles.values()))
        self.assertGreaterEqual(sum(1 for r in roles.values() if "official" in r), 20)

    def test_flags_carry_a_link_for_manual_review(self):
        self.assertGreater(len(self.flags), 0)
        for fl in self.flags:
            self.assertTrue(fl["source_list"], fl["id"])
            for s in fl["source_list"]:
                self.assertTrue(s["url"].startswith("https://"))

    def test_greyhounds_are_flagged_not_invented(self):
        self.assertFalse([f for f in self.fixtures if f["sport"] == "greyhounds"])
        self.assertTrue(any(fl["sport"] == "greyhounds" for fl in self.flags))

    # ---------------------------------------------------------------- prices
    def test_high_gate_is_a_conjunction(self):
        for p in self.picks:
            self.assertEqual(p["tier"], "High")
            self.assertGreater(p["p"], 0.70, p)
            self.assertGreaterEqual(p["american"], -250, p)
            self.assertLessEqual(p["american"], 10000, p)
            self.assertAlmostEqual(p["decimal"], 1 / p["p"], places=3)

    def test_no_qualifying_price_is_left_unlabelled(self):
        sys.path.insert(0, str(SCRIPTS))
        import s4c4968fc_model as model
        for m in self.markets:
            qualifies = m["p"] > 0.70 and model.in_band(m["p"])
            self.assertEqual(m["tier"] == "High", qualifies, m)

    def test_two_sided_markets_are_complementary(self):
        pairs = {}
        for m in self.markets:
            pairs.setdefault((m["fixture"], m["market"]), []).append(m["p"])
        for key, ps in pairs.items():
            if key[1] in ("Match winner", "Head-to-head"):
                self.assertAlmostEqual(sum(ps), 1.0, places=6, msg=str(key))

    def test_per_sport_cap_of_five(self):
        counts = {}
        for p in self.picks:
            counts[p["sport"]] = counts.get(p["sport"], 0) + 1
        for sport, n in counts.items():
            self.assertLessEqual(n, 5, sport)

    def test_pick_markets_are_unique_per_fixture(self):
        keys = [(p["fixture"], p["market"]) for p in self.picks]
        self.assertEqual(len(keys), len(set(keys)))

    # ----------------------------------------------------------- predictions
    def test_one_prediction_per_pick_stating_the_selection(self):
        self.assertEqual(len(self.preds), len(self.picks))
        for p in self.preds:
            words = p["text"].split()
            self.assertGreaterEqual(len(words), 30, p["fixture"])
            low = p["text"].lower()
            self.assertIn(p["selection_line"].lower(), low, p["fixture"])
            for bad in ("model", "verified"):
                self.assertIsNone(re.search(rf"\b{bad}\b", low), f"{p['fixture']} uses '{bad}'")

    def test_predictions_do_not_repeat_phrases(self):
        def grams(t, n=6):
            w = re.findall(r"[a-z]+", t.lower())
            return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}
        for i in range(len(self.preds)):
            for j in range(i + 1, len(self.preds)):
                self.assertFalse(grams(self.preds[i]["text"]) & grams(self.preds[j]["text"]),
                                 f"{self.preds[i]['fixture']} vs {self.preds[j]['fixture']}")

    def test_predictions_cite_their_fixture_sources(self):
        fx = {f["id"]: f for f in self.fixtures}
        for p in self.preds:
            self.assertEqual(set(p["sources"]), {s["url"] for s in fx[p["fixture"]]["sources"]})

    # ------------------------------------------------------------------ site
    def test_pages_exist_and_avoid_banned_vocabulary(self):
        self.assertGreaterEqual(len(self.manifest["pages"]), 20)
        for page in self.manifest["pages"]:
            path = SITE / page
            self.assertTrue(path.exists(), page)
            body = path.read_text(encoding="utf-8")
            for bad in ("model", "verified"):
                self.assertIsNone(re.search(rf"\b{bad}\b", body, re.I), f"{page}: {bad}")

    def test_data_export_tables_balance(self):
        with (DATA / "matches.csv").open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), len(self.fixtures))
        for r in rows:
            self.assertTrue(r["official_sources"].startswith("https://"))
        with (DATA / "markets.csv").open(encoding="utf-8") as fh:
            mk = list(csv.DictReader(fh))
        self.assertEqual(len(mk), len(self.markets))
        with (DATA / "predictions.csv").open(encoding="utf-8") as fh:
            pr = list(csv.DictReader(fh))
        self.assertEqual(len(pr), len(self.preds))

    def test_desk_gate_script_passes(self):
        res = subprocess.run([sys.executable, str(SCRIPTS / "s4c4968fc_validate.py")],
                             capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)


if __name__ == "__main__":
    unittest.main()
