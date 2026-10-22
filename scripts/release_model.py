#!/usr/bin/env python3
"""Evidence-first, zero-vig research estimates. No scraping, implicit ratings or bet approval.

Every numerical assumption lives here. Uncalibrated estimates never earn High confidence.
The record model is a smoothed log5 baseline, not a trained predictive model. The handball
model is independent Poisson scoring, not a claim that real goals are independent.
"""
from __future__ import annotations

import math
from urllib.parse import urlsplit
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
MODEL_VERSION = "evidence-baselines-1.0"
PRIOR_GAMES = 4.0  # symmetric Beta(2,2), explicitly an assumption, never an observed rating
SOURCE_TTL_HOURS = 24
HIGH_PRICE_MIN = -250.0
HIGH_PRICE_MAX = 10000.0


def timestamp(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("UTC/offset required; never infer a timezone")
    return dt.astimezone(UTC)


def american(probability: float) -> float:
    if not math.isfinite(probability) or not 0 < probability < 1:
        raise ValueError("A finite probability strictly between zero and one is required")
    return -100 * probability / (1 - probability) if probability > 0.5 else 100 * (1 - probability) / probability


def odds_in_high_window(probability: float) -> bool:
    """Compare unrounded odds, never clamp or reprice a selection to fit the window."""
    american(probability)  # validate first; compare exact probability bounds to avoid binary error at −250
    return 1 / 101 <= probability <= 5 / 7


def outcome(name: str, p: float) -> dict:
    return {"selection": name, "probability": p, "fair_decimal": 1 / p,
            "fair_american": american(p), "bookmaker_american": None,
            "expected_value": None}


def record_rate(record: dict, prior: float = PRIOR_GAMES) -> float:
    # Missing one side is an abstention, NOT a neutral assumed strength.
    required = ("games", "wins", "losses")
    if any(k not in record or record[k] is None for k in required):
        raise ValueError("Missing paired observed win/loss input")
    games, wins, losses = (record[k] for k in required)
    ot = record.get("ot_losses", 0)
    draws = record.get("draws", 0)
    values = (games, wins, losses, ot, draws)
    if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in values):
        raise ValueError("Records must be nonnegative integers")
    if games <= 0 or wins + losses + ot + draws != games or draws:
        raise ValueError("Nonempty, draw-free and internally consistent records required")
    return (wins + prior / 2) / (games + prior)


def log5(pa: float, pb: float) -> float:
    a = pa * (1 - pb)
    b = pb * (1 - pa)
    return a / (a + b)


def record_market(fixture: dict) -> dict:
    ins = fixture["inputs"]
    pa, pb = record_rate(ins["a"]), record_rate(ins["b"])
    p = log5(pa, pb)
    stress = []
    for prior in (2.0, 4.0, 8.0):
        q = log5(record_rate(ins["a"], prior), record_rate(ins["b"], prior))
        # No home advantage is fitted. This is a sensitivity check, NOT a confidence interval.
        for home_odds_factor in (1.0, 1.15):
            factor = home_odds_factor if fixture["participant_order"] == "home-away" else 1.0
            stress.append(q * factor / (1 - q + q * factor))
    return {"id": "winner", "name": "Match winner — record-only proxy",
            "settlement": "Two-way including extra time; a model convention, not verified bookmaker rules",
            "availability": "unverified", "model": "smoothed-log5-record",
            "input_evidence": sorted(set(ins["a"]["evidence"] + ins["b"]["evidence"])),
            "outcomes": [outcome(fixture["participant_a"], p), outcome(fixture["participant_b"], 1 - p)],
            "sensitivity_a": [min(stress), max(stress)],
            "assumptions": "Beta(2,2) smoothed wins, neutral venue, no opponent-strength adjustment; sensitivity uses priors of 2/4/8 games and a hypothetical home-odds factor 1.00/1.15. Overtime losses count as losses, not half-wins."}


def poisson_mass(mu: float) -> list[float]:
    if not math.isfinite(mu) or mu <= 0:
        raise ValueError("Positive observed-rate mean required")
    # Tail bound is generous; normalize the retained mass and verify it in tests.
    size = math.ceil(mu + 12 * math.sqrt(mu) + 20)
    terms = [math.exp(-mu)]
    for k in range(1, size + 1):
        terms.append(terms[-1] * mu / k)
    mass = sum(terms)
    if mass < 1 - 1e-10:
        raise ValueError("Insufficient score-grid probability mass")
    return [v / mass for v in terms]


def poisson_markets(fixture: dict) -> list[dict]:
    ins = fixture["inputs"]
    rates = []
    for side in ("a", "b"):
        r = ins[side]
        if any(r.get(k) is None for k in ("games", "goals_for", "goals_against")):
            raise ValueError("Missing paired goal-rate inputs")
        if r["games"] <= 0 or r["goals_for"] <= 0 or r["goals_against"] <= 0:
            raise ValueError("Invalid observed scoring sample")
        if r["wins"] + r["draws"] + r["losses"] != r["games"]:
            raise ValueError("Inconsistent handball record")
        rates.append((r["goals_for"] / r["games"], r["goals_against"] / r["games"]))
    ma = (rates[0][0] + rates[1][1]) / 2
    mb = (rates[1][0] + rates[0][1]) / 2
    a, b = poisson_mass(ma), poisson_mass(mb)
    grid = [(i, j, x * y) for i, x in enumerate(a) for j, y in enumerate(b)]
    common = {"settlement": "60-minute regulation only; draw retained where applicable",
              "availability": "unverified", "model": "independent-poisson-regulation",
              "input_evidence": sorted(set(ins["a"]["evidence"] + ins["b"]["evidence"])),
              "projected_goals": {"a": ma, "b": mb},
              "assumptions": "Each mean is the average of the team's observed scoring rate and opponent's concession rate. Independent Poisson goals; no venue, injuries, schedule-strength or overdispersion adjustment. Four-game samples are weak. Rungs centered on estimated mean, never selected to hit a confidence target."}
    markets = []

    def add(i, name, probs):
        markets.append(dict(common, id=i, name=name,
                            outcomes=[outcome(label, prob) for label, prob in probs]))

    an, bn = fixture["participant_a"], fixture["participant_b"]
    add("winner-regulation", "Regulation result (1X2)", [
        (an, sum(p for i, j, p in grid if i > j)),
        ("Draw", sum(p for i, j, p in grid if i == j)),
        (bn, sum(p for i, j, p in grid if i < j))])
    total_center = math.floor(ma + mb) + 0.5
    for shift in (-2, 0, 2):
        line = total_center + shift
        over = sum(p for i, j, p in grid if i + j > line)
        add(f"total-{line}", f"Total goals {line:g}", [(f"Over {line:g}", over), (f"Under {line:g}", 1 - over)])
    handicap_center = -(math.floor(ma - mb) + 0.5)
    for shift in (-2, 0, 2):
        line = handicap_center + shift
        cover = sum(p for i, j, p in grid if i + line > j)
        add(f"handicap-{line}", "Goal handicap", [(f"{an} {line:+g}", cover), (f"{bn} {-line:+g}", 1 - cover)])
    for label, mean, masses in ((an, ma, a), (bn, mb, b)):
        line = math.floor(mean) + 0.5
        over = sum(p for k, p in enumerate(masses) if k > line)
        add("team-total-" + ("a" if label == an else "b"), f"{label} team total {line:g}",
            [(f"Over {line:g}", over), (f"Under {line:g}", 1 - over)])
    top = sorted(grid, key=lambda x: x[2], reverse=True)[:3]
    add("correct-score", "Top three regulation scores + all other scores", [
        (f"{an} {i}–{j} {bn}", p) for i, j, p in top] + [("All other scores", 1 - sum(p for _, _, p in top))])
    return markets


def expiry_for(fixture: dict, sources: dict) -> datetime:
    evidence_ids = set(fixture["fixture_evidence"])
    for r in (fixture.get("inputs", {}).get("a", {}), fixture.get("inputs", {}).get("b", {})):
        evidence_ids.update(r.get("evidence", []))
    observed = []
    for sid in evidence_ids:
        s = sources[sid]
        # Date-only observations expire conservatively 24h after that day's midnight.
        dt = timestamp(s["retrieved_at_utc"]) if s.get("retrieved_at_utc") else timestamp(s["read_on"] + "T00:00:00Z")
        observed.append(dt + timedelta(hours=SOURCE_TTL_HOURS))
    return min(observed)


def temporal_status(fixture: dict, sources: dict, as_of: datetime, window: dict) -> str:
    if not window["from_utc"] <= fixture["event_date"] + "T00:00:00Z" < window["to_utc_exclusive"]:
        return "outside-window"
    if fixture.get("start_utc") and timestamp(fixture["start_utc"]) <= as_of:
        return "start-passed"  # not a claim that the event is completed
    if expiry_for(fixture, sources) <= as_of:
        return "snapshot-stale"
    if not fixture.get("start_utc"):
        return "time-unconfirmed"
    if fixture.get("official_state") not in (None, "FUT", "PRE", "Scheduled", "Preview"):
        return "not-pregame"
    return "scheduled"


def high_gate(fixture: dict, market: dict, selection: dict, status: str, calibrated: bool = False,
              preview: str = "", as_of: datetime | None = None) -> list[str]:
    """Every reason for abstention is exposed. No approved picks in the initial release."""
    reasons = []
    if status != "scheduled":
        reasons.append("Exact future start and fresh evidence required")
    if not calibrated:
        reasons.append("No held-out calibration / reliability evidence")
    if selection["probability"] <= 0.70:
        reasons.append("Estimated probability is not above 70%")
    if not odds_in_high_window(selection["probability"]):
        reasons.append("Unrounded fair odds outside −250…+10000")
    quote = fixture.get("bookmaker_quote")
    if not isinstance(quote, dict) or market["availability"] != "verified":
        reasons.append("No verified available quote with matching market and settlement")
    else:
        if (quote.get("market_id") != market["id"] or quote.get("selection") != selection["selection"]
                or quote.get("settlement") != market["settlement"] or quote.get("confirmed_available") is not True):
            reasons.append("Quoted market, selection, availability and settlement must match exactly")
        price = quote.get("american")
        if (isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price)
                or not -250 <= price <= 10000 or -100 < price < 100):
            reasons.append("Actual quoted American price outside valid −250…+10000 range")
        try:
            age = ((as_of or datetime.now(timezone.utc)) - timestamp(quote["retrieved_at_utc"])).total_seconds()
            if not 0 <= age <= 300:
                reasons.append("Verified quote must be no more than five minutes old, not future-dated")
        except (KeyError, TypeError, ValueError):
            reasons.append("Exact quote retrieval time missing or invalid")
        parsed_url = urlsplit(quote.get("source_url") or "")
        if parsed_url.scheme != "https" or not parsed_url.hostname:
            reasons.append("Direct quoted-market source URL missing")
    if not fixture.get("head_to_head") or not fixture.get("lineups_confirmed"):
        reasons.append("Relevant recent history / participant availability not fully confirmed")
    if len(preview.split()) < 30:
        reasons.append("Evidence-grounded unique 30+ word High preview unavailable")
    return reasons


def enrich(fixture: dict, sources: dict, as_of: datetime, window: dict) -> dict:
    row = dict(fixture)
    status = temporal_status(fixture, sources, as_of, window)
    row.update(status=status, evidence_expires_utc=expiry_for(fixture, sources).isoformat().replace("+00:00", "Z"),
               markets=[], winner_projection=None, confidence=None, approved_pick=None,
               model_version=MODEL_VERSION, model_errors=[])
    model = fixture.get("inputs", {}).get("model")
    try:
        if model == "smoothed-log5-record":
            row["markets"] = [record_market(fixture)]
        elif model == "independent-poisson-regulation":
            row["markets"] = poisson_markets(fixture)
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        row["model_errors"].append(str(exc))
    if row["markets"]:
        winner_market = row["markets"][0]
        selected = max(winner_market["outcomes"], key=lambda x: x["probability"])
        row["winner_projection"] = dict(selected)
        n = min(fixture["inputs"][s]["games"] for s in ("a", "b"))
        row["confidence"] = "Medium" if selected["probability"] >= 0.60 and n >= 8 else "Low"
        row["high_gate_rejections"] = high_gate(fixture, winner_market, selected, status, as_of=as_of)
        for m in row["markets"]:
            for o in m["outcomes"]:
                o["confidence"] = "Low" if model == "independent-poisson-regulation" else row["confidence"]
                o["passes_probability_and_fair_price_only"] = o["probability"] > 0.70 and odds_in_high_window(o["probability"])
                o["high_eligible"] = False
    else:
        row["high_gate_rejections"] = ["Missing paired verified model inputs; no neutral fallback price"]
    return row
