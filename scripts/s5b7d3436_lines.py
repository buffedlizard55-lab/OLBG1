#!/usr/bin/env python3
"""Derive session 5b7d3436 experimental fair lines from saved official inputs.

The calculations are intentionally small and inspectable.  No bookmaker quote,
OLBG tip share, archived probability or hidden rating is read.  An open OLBG
market is required separately before any selection can be released as High.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "5b7d3436"

CONSTANTS = {
    "nhl_league_goals_per_team_assumption": 3.0,
    "mlb_league_runs_per_team_assumption": 4.5,
    "shrinkage_prior_games": 5.0,
    "nhl_home_scoring_factor": 1.05,
    "nhl_away_scoring_factor": 0.95,
    "mlb_home_scoring_factor": 1.04,
    "mlb_away_scoring_factor": 0.96,
    "poisson_score_cutoff": 30,
    "high_probability_strictly_above": 0.70,
    "fair_decimal_band_min": 1.40,
    "fair_decimal_band_max": 101.0,
    "medium_research_probability_min": 0.60,
}
METHOD = (
    "Team scoring and allowance rates are each shrunk toward a disclosed league-rate assumption with a five-game prior. "
    "Expected home/away scores combine the attack rate with the opponent allowance rate and disclosed scoring factors. "
    "Independent Poisson regulation scores are enumerated through 30. Tie mass is split evenly between a one-score home "
    "or away final margin and adds one score to the total. Winner markets include overtime/extra innings; handicap and "
    "total markets use the same disclosed tie approximation. These are experimental fair prices, not calibrated betting claims."
)


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save(name, value):
    (DATA / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def iso(value):
    return value.isoformat().replace("+00:00", "Z")


def american_value(probability):
    if probability >= 0.5:
        return -100.0 * probability / (1.0 - probability)
    return 100.0 * (1.0 - probability) / probability


def american_display(probability):
    value = int(round(american_value(probability)))
    return f"+{value}" if value > 0 else str(value)


def outcome(market, selection, probability, line=None):
    probability = min(max(probability, 1e-12), 1.0 - 1e-12)
    decimal = 1.0 / probability
    return {
        "market": market, "selection": selection, "line": line,
        "probability": round(probability, 8),
        "fair_decimal": round(decimal, 6),
        "american": int(round(american_value(probability))),
        "american_display": american_display(probability),
        "in_band": CONSTANTS["fair_decimal_band_min"] <= decimal <= CONSTANTS["fair_decimal_band_max"],
        "bookmaker_quote": None,
    }


def poisson_vector(rate, cutoff):
    values = [math.exp(-rate)]
    for score in range(1, cutoff + 1):
        values.append(values[-1] * rate / score)
    return values


def distributions(home_rate, away_rate):
    cutoff = CONSTANTS["poisson_score_cutoff"]
    home = poisson_vector(home_rate, cutoff)
    away = poisson_vector(away_rate, cutoff)
    winner_home = 0.0
    margins = {}
    totals = {}
    retained_mass = 0.0
    for hs, hp in enumerate(home):
        for a_s, ap in enumerate(away):
            mass = hp * ap
            retained_mass += mass
            if hs > a_s:
                winner_home += mass
                margins[hs - a_s] = margins.get(hs - a_s, 0.0) + mass
                totals[hs + a_s] = totals.get(hs + a_s, 0.0) + mass
            elif hs < a_s:
                margins[hs - a_s] = margins.get(hs - a_s, 0.0) + mass
                totals[hs + a_s] = totals.get(hs + a_s, 0.0) + mass
            else:
                winner_home += mass * 0.5
                margins[1] = margins.get(1, 0.0) + mass * 0.5
                margins[-1] = margins.get(-1, 0.0) + mass * 0.5
                totals[hs + a_s + 1] = totals.get(hs + a_s + 1, 0.0) + mass
    # The cutoff is deliberately deep; normalize any residual tail rather than
    # silently dropping probability mass from the published two-way books.
    winner_home /= retained_mass
    margins = {k: v / retained_mass for k, v in margins.items()}
    totals = {k: v / retained_mass for k, v in totals.items()}
    return winner_home, margins, totals, retained_mass


def nearest_half_below(value):
    return max(0.5, math.floor(value + 0.5) - 0.5)


def expected_scores(inputs):
    kind = inputs["kind"]
    if kind == "nhl":
        average = CONSTANTS["nhl_league_goals_per_team_assumption"]
        home_factor = CONSTANTS["nhl_home_scoring_factor"]
        away_factor = CONSTANTS["nhl_away_scoring_factor"]
        scored, allowed = "goals_for", "goals_against"
    elif kind == "mlb":
        average = CONSTANTS["mlb_league_runs_per_team_assumption"]
        home_factor = CONSTANTS["mlb_home_scoring_factor"]
        away_factor = CONSTANTS["mlb_away_scoring_factor"]
        scored, allowed = "runs_scored", "runs_allowed"
    else:
        raise ValueError(f"Unsupported pricing input: {kind}")
    prior = CONSTANTS["shrinkage_prior_games"]
    home, away = inputs["home"], inputs["away"]
    home_games = home["games"] + prior
    away_games = away["games"] + prior
    home_attack = (home[scored] + prior * average) / home_games / average
    home_allow = (home[allowed] + prior * average) / home_games / average
    away_attack = (away[scored] + prior * average) / away_games / average
    away_allow = (away[allowed] + prior * average) / away_games / average
    home_rate = average * home_attack * away_allow * home_factor
    away_rate = average * away_attack * home_allow * away_factor
    return home_rate, away_rate, {
        "league_rate_assumption": average,
        "home_attack_factor": home_attack, "home_allowance_factor": home_allow,
        "away_attack_factor": away_attack, "away_allowance_factor": away_allow,
        "home_scoring_factor": home_factor, "away_scoring_factor": away_factor,
    }


def price_fixture(f):
    if not f.get("inputs"):
        return {
            "fixture_id": f["id"], "sport": f["sport"], "markets": [],
            "preferred_winner": None, "expires_at": None,
            "withheld_reason": " ".join(f["market_gaps"]),
        }
    home_rate, away_rate, factors = expected_scores(f["inputs"])
    home_win, margins, totals, retained = distributions(home_rate, away_rate)
    expected_margin = home_rate - away_rate
    spread = nearest_half_below(abs(expected_margin))
    home_line = -spread if expected_margin >= 0 else spread
    away_line = -home_line
    total_line = nearest_half_below(home_rate + away_rate)
    home_cover = sum(p for margin, p in margins.items() if margin + home_line > 0)
    over = sum(p for total, p in totals.items() if total > total_line)
    kind_label = "Moneyline · includes OT" if f["inputs"]["kind"] == "nhl" else "Moneyline · includes extra innings"
    spread_label = "Puck line" if f["inputs"]["kind"] == "nhl" else "Run line"
    total_label = "Total goals" if f["inputs"]["kind"] == "nhl" else "Total runs"
    home_name, away_name = f["home"], f["away"]
    markets = [
        {"key": "winner", "label": kind_label, "settlement": "Full game; tie mass split evenly in the disclosed overtime/extra-innings approximation",
         "outcomes": [outcome(kind_label, f"{home_name} to win", home_win),
                      outcome(kind_label, f"{away_name} to win", 1.0 - home_win)]},
        {"key": "handicap", "label": spread_label, "settlement": "Final margin after the disclosed tie approximation; half-point line means no push",
         "outcomes": [outcome(spread_label, f"{home_name} {home_line:+g}", home_cover, home_line),
                      outcome(spread_label, f"{away_name} {away_line:+g}", 1.0 - home_cover, away_line)]},
        {"key": "total", "label": total_label, "settlement": "Combined final score after the disclosed one-score tie adjustment; half-point line means no push",
         "outcomes": [outcome(total_label, f"Over {total_line:g}", over, total_line),
                      outcome(total_label, f"Under {total_line:g}", 1.0 - over, total_line)]},
    ]
    preferred = markets[0]["outcomes"][0] if home_win >= 0.5 else markets[0]["outcomes"][1]
    p = preferred["probability"]
    research_confidence = "Medium" if p >= CONSTANTS["medium_research_probability_min"] else "Low"
    expiry_candidates = [parse(f["evidence_expires_at"])]
    if f.get("start_utc"):
        expiry_candidates.append(parse(f["start_utc"]))
    expires = min(expiry_candidates)
    evaluation = {
        "selection": preferred["selection"], "probability": p,
        "fair_decimal": preferred["fair_decimal"], "american_display": preferred["american_display"],
        "research_confidence": research_confidence,
        "official_fixture": True, "open_olbg_market": False,
        "availability_complete": False,
        "probability_gate": p > CONSTANTS["high_probability_strictly_above"],
        "band_gate": preferred["in_band"],
        "prediction_gate": False, "publishable_high": False,
        "reason": "Research only: no open OLBG market was established and the availability package is incomplete.",
    }
    return {
        "fixture_id": f["id"], "sport": f["sport"], "markets": markets,
        "expected_home_score": round(home_rate, 6), "expected_away_score": round(away_rate, 6),
        "expected_total": round(home_rate + away_rate, 6),
        "expected_regulation_margin": round(expected_margin, 6),
        "derived_factors": factors, "retained_poisson_mass_before_normalization": retained,
        "preferred_winner": evaluation, "expires_at": iso(expires),
        "withheld_reason": " ".join(f["market_gaps"]),
    }


def csv_safe(value):
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def main():
    fixture_doc = load("fixtures.json")
    source_doc = load("sources.json")
    flag_doc = load("flagged.json")
    fixtures = fixture_doc["fixtures"]
    sources = {s["id"]: s for s in source_doc["sources"]}
    books = {f["id"]: price_fixture(f) for f in fixtures}
    priced = [f for f in fixtures if books[f["id"]]["markets"]]
    preferences = [books[f["id"]]["preferred_winner"] for f in priced]
    summary = {
        "session": fixture_doc["session"], "generated_at": fixture_doc["registered_at"],
        "evidence_expires_at": fixture_doc["evidence_expires_at"],
        "sports": len(fixture_doc["sports"]), "fixtures": len(fixtures),
        "upcoming": sum(f["state"] == "upcoming" for f in fixtures),
        "in_progress": sum(f["state"] == "in_progress" for f in fixtures),
        "official_source_rows": len(fixtures), "sources": source_doc["count"],
        "priced_fixtures": len(priced), "sports_with_prices": len({f["sport"] for f in priced}),
        "originated_markets": sum(len(books[f["id"]]["markets"]) for f in fixtures),
        "originated_outcomes": sum(len(m["outcomes"]) for f in fixtures for m in books[f["id"]]["markets"]),
        "winner_preferences": len(preferences),
        "medium_research_preferences": sum(p["research_confidence"] == "Medium" for p in preferences),
        "low_research_preferences": sum(p["research_confidence"] == "Low" for p in preferences),
        "open_olbg_markets": 0, "high_picks": 0, "published_predictions": 0,
        "flagged_findings": flag_doc["count"],
        "quota_policy": "Target up to five High picks per sport, but publish none unless every evidence, availability, probability, band and open-market gate passes.",
    }
    save("lines.json", {"session": fixture_doc["session"], "generated_at": fixture_doc["registered_at"],
                        "constants": CONSTANTS, "method": METHOD,
                        "books": [books[f["id"]] for f in fixtures]})
    save("summary.json", summary)
    save("predictions.json", {"session": fixture_doc["session"], "generated_at": fixture_doc["registered_at"],
                              "count": 0, "predictions": [],
                              "reason": "No selection passed the open-market, availability, >70% probability, fair-price band and original-prose gates. No prediction text was manufactured."})

    with (DATA / "matches.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        fields = ["id", "sport", "competition", "event", "home", "away", "date", "start_utc",
                  "start_local", "state", "venue", "olbg_event_id", "olbg_state", "open_olbg_market",
                  "experimental_selection", "research_confidence", "probability", "fair_decimal",
                  "american_display", "bookmaker_quote", "price_expires_at", "official_urls", "flags"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for f in fixtures:
            book = books[f["id"]]
            p = book["preferred_winner"]
            row = {k: f.get(k) for k in ["id", "sport", "competition", "event", "home", "away", "date",
                                          "start_utc", "start_local", "state", "venue", "olbg_event_id", "olbg_state"]}
            row.update({
                "open_olbg_market": False,
                "experimental_selection": p["selection"] if p else "",
                "research_confidence": p["research_confidence"] if p else "",
                "probability": p["probability"] if p else "",
                "fair_decimal": p["fair_decimal"] if p else "",
                "american_display": p["american_display"] if p else "",
                "bookmaker_quote": "", "price_expires_at": book["expires_at"] or "",
                "official_urls": " | ".join(sources[s]["url"] for s in f["source_ids"]),
                "flags": " | ".join(f["flags"] + f["market_gaps"]),
            })
            writer.writerow({k: csv_safe("" if v is None else v) for k, v in row.items()})

    with (DATA / "markets.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        fields = ["fixture_id", "sport", "event", "market", "selection", "line", "probability",
                  "fair_decimal", "american", "american_display", "in_band", "open_olbg_market",
                  "bookmaker_quote", "price_expires_at", "official_urls"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for f in fixtures:
            book = books[f["id"]]
            urls = " | ".join(sources[s]["url"] for s in f["source_ids"])
            for market in book["markets"]:
                for o in market["outcomes"]:
                    writer.writerow({"fixture_id": f["id"], "sport": f["sport"], "event": f["event"],
                                     "market": market["label"], "selection": o["selection"], "line": o["line"],
                                     "probability": o["probability"], "fair_decimal": o["fair_decimal"],
                                     "american": o["american"], "american_display": o["american_display"],
                                     "in_band": o["in_band"], "open_olbg_market": False, "bookmaker_quote": "",
                                     "price_expires_at": book["expires_at"], "official_urls": urls})
    print(json.dumps(summary, indent=2))
    for f in priced:
        b = books[f["id"]]
        p = b["preferred_winner"]
        print(f"{f['id']}: {p['selection']} {p['probability']:.4%} {p['american_display']} · {p['research_confidence']} research only")


if __name__ == "__main__":
    main()
