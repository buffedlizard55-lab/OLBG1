import copy
import json
import math
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import release_model as model
import release_fetch as fetch
import release_build as build

DATA = json.loads((ROOT / "data/release/evidence.json").read_text())
SOURCES = {s["id"]: s for s in DATA["sources"]}
FIXTURES = {f["id"]: f for f in DATA["fixtures"]}
CUTOFF = model.timestamp("2026-10-22T07:30:00Z")
WINDOW = {"from_utc": "2026-10-22T00:00:00Z", "to_utc_exclusive": "2026-10-29T00:00:00Z"}


class OddsTests(unittest.TestCase):
    def test_decimal_and_american(self):
        self.assertAlmostEqual(model.american(.5), 100)
        self.assertAlmostEqual(model.american(.75), -300)
        self.assertAlmostEqual(model.american(.25), 300)
        self.assertAlmostEqual(model.outcome("A", .4)["fair_decimal"], 2.5)

    def test_exact_window_boundaries_not_rounded_or_clamped(self):
        self.assertTrue(model.odds_in_high_window(5 / 7))
        self.assertTrue(model.odds_in_high_window(1 / 101))
        self.assertFalse(model.odds_in_high_window(math.nextafter(5 / 7, 1)))
        self.assertFalse(model.odds_in_high_window(math.nextafter(1 / 101, 0)))
        self.assertFalse(model.odds_in_high_window(.8))
        self.assertGreater(model.american(.8), -401)
        self.assertLess(model.american(.8), -399)

    def test_invalid_probabilities_rejected(self):
        for p in (0, 1, -1, 1.01, math.nan, math.inf):
            with self.subTest(p=p), self.assertRaises(ValueError):
                model.american(p)

    def test_window_arithmetic(self):
        self.assertTrue(model.odds_in_high_window(.705))
        self.assertFalse(model.odds_in_high_window(.72))
        self.assertLess(.70, 5 / 7)


class ModelTests(unittest.TestCase):
    def fixture(self, key="nhl-2026020154"):
        return copy.deepcopy(FIXTURES[key])

    def test_log5_complements_and_symmetry(self):
        p = model.log5(.6, .4)
        self.assertAlmostEqual(p + model.log5(.4, .6), 1)
        self.assertAlmostEqual(model.log5(.7, .7), .5)

    def test_ot_losses_are_losses_not_half_wins(self):
        r = {"wins": 3, "losses": 2, "ot_losses": 3, "games": 8}
        self.assertAlmostEqual(model.record_rate(r), 5 / 12)

    def test_missing_one_side_abstains_instead_of_neutral_baseline(self):
        f = self.fixture(); del f["inputs"]["b"]
        row = model.enrich(f, SOURCES, CUTOFF, WINDOW)
        self.assertFalse(row["markets"])
        self.assertIsNone(row["winner_projection"])
        self.assertTrue(row["model_errors"])

    def test_zero_games_abstains(self):
        f = self.fixture()
        f["inputs"]["a"] = {"wins": 0, "losses": 0, "games": 0, "evidence": ["nhl-score"]}
        self.assertFalse(model.enrich(f, SOURCES, CUTOFF, WINDOW)["markets"])

    def test_inconsistent_record_is_not_priced(self):
        f = self.fixture(); f["inputs"]["a"]["games"] += 1
        self.assertFalse(model.enrich(f, SOURCES, CUTOFF, WINDOW)["markets"])

    def test_nba_no_fabricated_rating(self):
        self.assertFalse(model.enrich(self.fixture("nba-0022600006"), SOURCES, CUTOFF, WINDOW)["markets"])

    def test_poisson_retained_mass(self):
        for mu in (1, 27.5, 38):
            self.assertAlmostEqual(sum(model.poisson_mass(mu)), 1, places=12)

    def test_handball_retains_draw(self):
        markets = model.poisson_markets(self.fixture("ehf-oct22-4"))
        result = markets[0]
        self.assertEqual(len(result["outcomes"]), 3)
        self.assertEqual(result["outcomes"][1]["selection"], "Draw")
        self.assertGreater(result["outcomes"][1]["probability"], 0)
        for market in markets:
            self.assertAlmostEqual(sum(o["probability"] for o in market["outcomes"]), 1, places=10)

    def test_half_goal_ladders_have_no_push_and_not_tuned_for_high(self):
        row = model.enrich(self.fixture("ehf-oct22-3"), SOURCES, CUTOFF, WINDOW)
        totals = [m for m in row["markets"] if m["id"].startswith("total-")]
        lines = [float(m["id"].removeprefix("total-")) for m in totals]
        self.assertEqual(lines[1] - lines[0], 2)
        self.assertEqual(lines[2] - lines[1], 2)
        self.assertTrue(all(x % 1 == .5 for x in lines))
        for m in row["markets"]:
            for o in m["outcomes"]:
                self.assertFalse(o["high_eligible"])
                self.assertEqual(o["confidence"], "Low")

    def test_no_bookmaker_quote_or_ev_in_own_lines(self):
        row = model.enrich(self.fixture(), SOURCES, CUTOFF, WINDOW)
        for market in row["markets"]:
            for o in market["outcomes"]:
                self.assertIsNone(o["bookmaker_american"])
                self.assertIsNone(o["expected_value"])
        self.assertIsNone(row["approved_pick"])
        self.assertNotEqual(row["confidence"], "High")

    def test_reproducible_estimates(self):
        f = self.fixture()
        self.assertEqual(model.enrich(f, SOURCES, CUTOFF, WINDOW), model.enrich(f, SOURCES, CUTOFF, WINDOW))

    def test_quote_cannot_bypass_real_price_time_and_settlement_checks(self):
        row = self.fixture()
        market = model.record_market(row)
        market["availability"] = "verified"
        row["bookmaker_quote"] = {"american": -400, "market_id": "different", "selection": "wrong", "settlement": "wrong", "confirmed_available": True, "retrieved_at_utc": "2026-10-21T00:00:00Z", "source_url": "https://example.com/market"}
        reasons = model.high_gate(row, market, model.outcome("Boston Bruins", .705), "scheduled", as_of=CUTOFF)
        self.assertTrue(any("Actual quoted American price" in reason for reason in reasons))
        self.assertTrue(any("settlement must match" in reason for reason in reasons))
        self.assertTrue(any("five minutes" in reason for reason in reasons))

    def test_high_numerical_output_does_not_create_high_confidence(self):
        row = model.enrich(self.fixture(), SOURCES, CUTOFF, WINDOW)
        reasons = model.high_gate(row, row["markets"][0], model.outcome("Boston Bruins", .705), "scheduled")
        self.assertTrue(any("calibration" in r for r in reasons))
        self.assertTrue(any("matching market" in r for r in reasons))
        self.assertTrue(any("30+" in r for r in reasons))


class TimeTests(unittest.TestCase):
    def test_timezone_must_be_explicit(self):
        with self.assertRaises(ValueError): model.timestamp("2026-10-22T07:00:00")

    def test_cutoff_uses_actual_time_not_midnight(self):
        f = FIXTURES["nhl-2026020154"]
        at_start = model.timestamp(f["start_utc"])
        self.assertEqual(model.temporal_status(f, SOURCES, at_start, WINDOW), "start-passed")

    def test_build_does_not_renew_manual_evidence(self):
        f = copy.deepcopy(FIXTURES["nhl-2026020164"])
        f["fixture_evidence"] = ["nhl-score"]
        for side in ("a", "b"):
            f["inputs"][side]["evidence"] = ["nhl-score"]
        at_midnight = model.timestamp("2026-10-23T00:00:00Z")
        self.assertEqual(model.temporal_status(f, SOURCES, at_midnight, WINDOW), "snapshot-stale")
        self.assertEqual(model.expiry_for(f, SOURCES), at_midnight)

    def test_unknown_timezone_never_marked_live(self):
        f = FIXTURES["atp-almaty-1"]
        self.assertIsNone(f["start_utc"])
        self.assertEqual(model.temporal_status(f, SOURCES, CUTOFF, WINDOW), "time-unconfirmed")

    def test_window_has_exclusive_end(self):
        f = copy.deepcopy(FIXTURES["mlb-849803"])
        f.update(event_date="2026-10-29", start_utc="2026-10-29T00:00:00Z")
        self.assertEqual(model.temporal_status(f, SOURCES, CUTOFF, WINDOW), "outside-window")

    def test_non_pregame_state_not_approved(self):
        f = copy.deepcopy(FIXTURES["nhl-2026020154"]); f["official_state"] = "PPD"
        self.assertEqual(model.temporal_status(f, SOURCES, CUTOFF, WINDOW), "not-pregame")


class CollectorTests(unittest.TestCase):
    def test_official_collector_allowlist(self):
        with self.assertRaises(ValueError): fetch.get_json("https://example.com/fake", ROOT / ".cache/nope.json")

    def test_nhl_parser_orients_home_and_away(self):
        payload = {"games": [{"id": 2026020154, "gameState": "FUT", "gameScheduleState": "OK", "startTimeUTC": "2026-10-22T23:00:00Z",
            "homeTeam": {"placeName": {"default": "Boston"}, "commonName": {"default": "Bruins"}, "record": "7-2-1"},
            "awayTeam": {"placeName": {"default": "Nashville"}, "commonName": {"default": "Predators"}, "record": "3-2-3"}}]}
        row = fetch.nhl_rows(payload, "test-source")[0]
        self.assertEqual(row["participant_a"], "Boston Bruins")
        self.assertEqual(row["participant_b"], "Nashville Predators")
        self.assertEqual(row["inputs"]["b"]["losses"], 2)
        self.assertIsNone(row["bookmaker_quote"])

    def test_missing_nhl_record_not_invented(self):
        payload = {"games": [{"id": 2026020154, "gameState": "FUT", "gameScheduleState": "OK", "startTimeUTC": "2026-10-22T23:00:00Z",
            "homeTeam": {"placeName": {"default": "Boston"}, "commonName": {"default": "Bruins"}},
            "awayTeam": {"placeName": {"default": "Nashville"}, "commonName": {"default": "Predators"}, "record": "3-2-3"}}]}
        self.assertEqual(fetch.nhl_rows(payload, "test-source")[0]["inputs"], {})

    def test_mlb_regular_season_inputs_not_series_zero_zero(self):
        records = fetch.mlb_records({"records": [{"teamRecords": [{"team": {"id": 139}, "wins": 98, "losses": 64, "runsScored": 736, "runsAllowed": 650}]}]}, "official-stats")
        self.assertEqual(records[139]["games"], 162)
        game = {"gamePk": 849805, "gameDate": "2026-10-24T00:00:00Z", "status": {"abstractGameState": "Preview", "startTimeTBD": False},
                "teams": {"home": {"team": {"id": 139, "name": "Tampa Bay Rays"}, "leagueRecord": {"wins": 0, "losses": 0}},
                          "away": {"team": {"id": 158, "name": "Milwaukee Brewers"}}}}
        row = fetch.mlb_rows({"dates": [{"games": [game]}]}, "official-schedule", records)[0]
        self.assertEqual(row["inputs"], {})  # one observed side is not enough
        game["ifNecessary"] = "Y"
        self.assertEqual(fetch.mlb_rows({"dates": [{"games": [game]}]}, "official-schedule", records), [])

    def test_successful_empty_snapshot_withdraws_not_invents_cancellation(self):
        fixtures = {"nhl-2026020154": copy.deepcopy(FIXTURES["nhl-2026020154"])}
        fixtures["nhl-2026020154"]["fixture_evidence"] = ["nhl-score"]
        withdrawn = fetch.apply_schedule_snapshot(fixtures, SOURCES, "fresh-source", SOURCES["nhl-score"]["url"], {"games": []}, [], date(2026, 10, 22), date(2026, 10, 29))
        self.assertEqual(withdrawn, ["nhl-2026020154"])
        self.assertEqual(fixtures[withdrawn[0]]["official_state"], "not-returned")
        self.assertIn("Absence is not asserted", fixtures[withdrawn[0]]["notes"])
        self.assertEqual(fixtures[withdrawn[0]]["fixture_evidence"], ["nhl-score"])

    def test_successful_refresh_keeps_previous_observation_immutable(self):
        cache = ROOT / ".cache"
        cache.mkdir(exist_ok=True)
        def response(url, path):
            payload = {"games": []} if "nhle.com" in url else {"dates": []} if "schedule" in url else {"records": []}
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload))
            return payload, "2026-10-22T08:00:00Z"
        with tempfile.TemporaryDirectory(dir=cache) as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(DATA))
            with patch.object(fetch, "get_json", side_effect=response):
                attempts = fetch.refresh(path, date(2026, 10, 22))
            refreshed = json.loads(path.read_text())
            old_sources = {s["id"]: s for s in DATA["sources"]}
            new_sources = {s["id"]: s for s in refreshed["sources"]}
            for sid, source in old_sources.items():
                self.assertEqual(new_sources[sid], source)
            self.assertTrue(any(a["status"] == "success" for a in attempts))
            self.assertGreater(len(new_sources), len(old_sources))

    def test_failed_refresh_preserves_old_observation_dates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(DATA))
            with patch.object(fetch, "get_json", side_effect=URLError("test: outside allowed egress")):
                attempts = fetch.refresh(path, date(2026, 10, 22))
            refreshed = json.loads(path.read_text())
        self.assertEqual(len(attempts), 9)
        self.assertTrue(all(a["status"] == "failed" for a in attempts))
        self.assertEqual(refreshed["sources"], DATA["sources"])
        self.assertEqual({f["id"]: f for f in refreshed["fixtures"]}, FIXTURES)
        self.assertEqual(refreshed["captured_at_utc"], DATA["captured_at_utc"])


class PresentationTests(unittest.TestCase):
    def test_escape_text_and_attributes(self):
        self.assertEqual(build.e('<script>"x"</script>'), '&lt;script&gt;&quot;x&quot;&lt;/script&gt;')

    def test_every_sport_is_explicitly_partial_or_blocked(self):
        self.assertEqual(len(DATA["coverage"]), 17)
        self.assertTrue(all(not c["exhaustive"] for c in DATA["coverage"]))

    def test_research_notes_are_individual_and_source_linked(self):
        notes = json.loads((ROOT / "data/release/commentary.json").read_text())
        self.assertEqual(len({v["text"] for v in notes.values()}), len(notes))
        for key, value in notes.items():
            self.assertIn(key, FIXTURES)
            self.assertGreaterEqual(len(value["text"].split()), 30)
            self.assertTrue(value["evidence"])


if __name__ == "__main__": unittest.main()
