"""Tests for the f840c28a desk (session f840c28a-olbg1, task TF840C).

These tests are the executable form of the desk's contract:

* the pricing engine is internally consistent (probabilities in [0,1], prices
  that invert back to the same probability, band and tier agreeing)
* the brief's High rule is applied, not approximated
* the published artefact passes its own gate
* the written predictions meet the 30-word floor, avoid internal vocabulary and
  do not repeat one another

Run:  python3 -m unittest tests.pipeline.test_desk_f840c28a -v
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import sf840c28a_engine as E   # noqa: E402
import sf840c28a_facts as F    # noqa: E402

DESK_DIR = ROOT / "f840c28a"
DATA_DIR = ROOT / "data" / "f840c28a"


def load(name):
    return json.loads((DATA_DIR / name).read_text())


class TestAmericanOdds(unittest.TestCase):
    def test_round_trip(self):
        for p in (0.05, 0.2, 0.5, 0.6, 0.7, 0.7142857, 0.9):
            price = E.american(p)
            back = (-price) / (-price + 100) if price < 0 else 100 / (price + 100)
            self.assertAlmostEqual(back, p, places=6, msg=f"p={p} price={price}")

    def test_known_points(self):
        self.assertAlmostEqual(E.american(0.50), -100.0, places=6)
        self.assertAlmostEqual(E.american(2 / 3), -200.0, places=6)
        self.assertAlmostEqual(E.american(0.5 / 1.5), 200.0, places=6)

    def test_band_boundaries(self):
        self.assertEqual(E.band_state(-250), "in")
        self.assertEqual(E.band_state(-251), "out")
        self.assertEqual(E.band_state(10000), "in")
        self.assertEqual(E.band_state(10001), "out")

    def test_band_edge_is_the_documented_probability(self):
        # -250 is 71.43%; a 70% selection is -233 and is inside the band.
        self.assertAlmostEqual(100 * 250 / 350, 71.4285, places=3)
        self.assertAlmostEqual(E.american(0.70), -233.3333, places=3)
        self.assertLess(abs(E.american(0.70)), 250)


class TestHighRule(unittest.TestCase):
    def test_high_requires_more_than_seventy_percent(self):
        self.assertEqual(E.tier(0.70, E.american(0.70)), "Medium")
        self.assertEqual(E.tier(0.7001, E.american(0.7001)), "High")

    def test_nothing_shorter_than_minus_250_is_a_tier(self):
        self.assertEqual(E.tier(0.80, E.american(0.80)), "outside band")

    def test_medium_and_low_floors(self):
        self.assertEqual(E.tier(0.60, E.american(0.60)), "Medium")
        self.assertEqual(E.tier(0.5999, E.american(0.5999)), "Low")
        self.assertEqual(E.tier(0.52, E.american(0.52)), "Low")
        self.assertEqual(E.tier(0.519, E.american(0.519)), "outside band")


class TestHockeyGrid(unittest.TestCase):
    def test_grid_is_a_distribution(self):
        lam = E.nhl_lambdas("BOS", "SJS")
        self.assertIsNotNone(lam)
        grid = E.nhl_grid(*lam)
        self.assertAlmostEqual(sum(grid.values()), 1.0, places=3)

    def test_known_hand_computed_tail(self):
        lam = E.nhl_lambdas("BOS", "SJS")
        grid = E.nhl_grid(*lam)
        by_three = sum(p for (h, a), p in grid.items() if h - a > 2.5)
        self.assertTrue(0.10 < by_three < 0.40, by_three)

    def test_puck_line_sides_are_exhaustive(self):
        for g in F.NHL_GAMES:
            ms = E.nhl_markets(g["home"], g["away"])
            if ms is None:
                continue
            for m in ms:
                if m["market"] == "Puck line":
                    self.assertAlmostEqual(m["home_p"] + m["away_p"], 1.0, places=6)

    def test_shrunk_rate_sits_between_sample_and_league(self):
        self.assertGreater(E.shrunk(5.0, 10), 3.0)
        self.assertLess(E.shrunk(5.0, 10), 5.0)
        self.assertAlmostEqual(E.shrunk(3.0, 10), 3.0, places=9)

    def test_detroit_is_not_priced(self):
        self.assertIsNone(E.nhl_markets("CGY", "DET"))
        self.assertIsNone(E.nhl_markets("DET", "CGY"))


class TestBasketball(unittest.TestCase):
    def test_probit_inverts_normal(self):
        for p in (0.05, 0.3, 0.5, 0.7, 0.95):
            self.assertAlmostEqual(E.norm_cdf(E._probit(p)), p, places=4)

    def test_unknown_record_is_not_priced(self):
        self.assertIsNone(E.nba_markets("SAC", "MEM"))

    def test_spread_is_monotonic(self):
        ms = E.nba_markets("PHI", "MIL")
        spreads = [m for m in ms if m["market"] == "Point spread"]
        values = [m["home_p"] for m in spreads]
        self.assertEqual(values, sorted(values, reverse=True))


class TestPublishedBoard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.desk = load("desk.json")

    def test_counts_are_consistent(self):
        d, c = self.desk, self.desk["counts"]
        self.assertEqual(c["fixtures"], len(d["fixtures"]))
        self.assertEqual(c["picks"], len(d["picks"]))
        self.assertEqual(c["high"] + c["medium"] + c["low"], c["picks"])
        self.assertEqual(c["sports"], 15)

    def test_every_pick_is_inside_the_band(self):
        for p in self.desk["picks"]:
            self.assertGreaterEqual(p["price"], -250, p["selection"])
            self.assertLessEqual(p["price"], 10000, p["selection"])

    def test_every_pick_is_confirmed_by_an_official_fixture(self):
        for p in self.desk["picks"]:
            self.assertIsNotNone(p["fixture_source"], p["selection"])

    def test_priced_fixtures_carry_markets(self):
        for f in self.desk["fixtures"]:
            if f["priced"]:
                self.assertTrue(f["markets"], f"{f['away']}@{f['home']}")

    def test_unconfirmed_fixtures_are_not_priced(self):
        for f in self.desk["fixtures"]:
            if not f["confirmed"]:
                self.assertFalse(f["priced"], f"{f['away']}@{f['home']}")
                self.assertIsNone(f["pick"])


class TestPredictions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.desk = load("desk.json")
        cls.preds = [(p["fixture"], p["prediction"]) for p in cls.desk["picks"]
                     if p.get("prediction")]

    def test_at_least_five(self):
        self.assertGreaterEqual(len(self.preds), 5)

    def test_thirty_word_floor(self):
        for fixture, text in self.preds:
            self.assertGreaterEqual(len(text.split()), 30, fixture)

    def test_no_internal_vocabulary(self):
        for fixture, text in self.preds:
            low = text.lower()
            for bad in ("model", "verified", "verification"):
                self.assertNotIn(bad, low, f"{fixture} says {bad}")

    def test_no_shared_six_gram(self):
        seen = {}
        for fixture, text in self.preds:
            words = re.findall(r"[a-z0-9']+", text.lower())
            grams = {tuple(words[i:i + 6]) for i in range(len(words) - 5)}
            for other, og in seen.items():
                self.assertFalse(grams & og, f"{fixture} repeats {other}")
            seen[fixture] = grams

    def test_each_prediction_names_its_selection(self):
        picks = {p["fixture"]: p for p in self.desk["picks"] if p.get("prediction")}
        for fixture, text in self.preds:
            sel = picks[fixture]["selection"]
            head = sel.split()[0]
            candidates = {head, F.NHL_TEAM_NAMES.get(head, ""), F.NBA_TEAM_NAMES.get(head, "")}
            candidates.discard("")
            candidates |= {w for n in list(candidates) for w in n.split() if len(w) > 4}
            low = text.lower()
            hit = any(c.lower() in low for c in candidates)
            self.assertTrue(hit, f"{fixture} does not name {sel}")


class TestArtefact(unittest.TestCase):
    def test_pages_exist(self):
        for name in ("index.html", "picks.html", "predictions.html", "flagged.html",
                     "sources.html", "methodology.html", "repo-review.html"):
            self.assertTrue((DESK_DIR / name).is_file(), name)

    def test_fifteen_sport_pages(self):
        pages = sorted(p.stem for p in (DESK_DIR / "sports").glob("*.html"))
        self.assertEqual(len(pages), 15, pages)

    def test_every_relative_link_resolves(self):
        for path in DESK_DIR.rglob("*.html"):
            for href in re.findall(r'href="([^"#?]+\.html)"', path.read_text()):
                if href.startswith("http"):
                    continue
                self.assertTrue((path.parent / href).resolve().is_file(),
                                f"{path.name} -> {href}")

    def test_gate_passes(self):
        res = subprocess.run([sys.executable, str(SCRIPTS / "sf840c28a_validate.py"), "--quiet"],
                             capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

    def test_sources_all_have_urls_and_times(self):
        for s in load("sources.json"):
            self.assertTrue(s["url"].startswith("http"))
            self.assertTrue(s["read_utc"])


if __name__ == "__main__":
    unittest.main()
