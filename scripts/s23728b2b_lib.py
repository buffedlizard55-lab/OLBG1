"""Shared fair-price arithmetic and record assembly for desk 23728b2b."""
from __future__ import annotations

import math

from scripts.s23728b2b_data import FIXTURES, FLAGS, OBSERVED, PICKS, SOURCES, SPORTS


def fair_decimal(probability: float) -> float:
    """Reciprocal no-margin decimal price, before display rounding."""
    if not 0 < probability < 1:
        raise ValueError("probability must be strictly between zero and one")
    return 1.0 / probability


def fair_american(probability: float) -> float:
    """Convert an independent probability directly to a no-margin American price."""
    dec = fair_decimal(probability)
    return 100.0 * (dec - 1.0) if dec >= 2.0 else -100.0 / (dec - 1.0)


def in_high_price_window(probability: float) -> bool:
    price = fair_american(probability)
    # The tolerance only removes binary floating-point noise at exact boundaries.
    return price >= -250.0 - 1e-9 and price <= 10000.0 + 1e-9


def confidence(probability: float) -> str:
    """High requires both strict probability and price tests; 70% is not High."""
    if probability > 0.70 and in_high_price_window(probability):
        return "High"
    return "Medium" if probability >= 0.55 else "Low"


def rounded_american(probability: float) -> int:
    """Nearest integer, with exact halves rounded away from zero."""
    value = fair_american(probability)
    return math.floor(value + 0.5) if value >= 0 else math.ceil(value - 0.5)


def display_american(probability: float) -> str:
    return f"{rounded_american(probability):+d}"


def display_decimal(probability: float) -> str:
    return f"{fair_decimal(probability):.3f}"


def line_record(fixture_id: str, line_id: str, role: str, market: str, selection: str, probability: float) -> dict:
    return {
        "id": line_id,
        "fixture": fixture_id,
        "role": role,
        "market": market,
        "selection": selection,
        "probability": probability,
        "fair_decimal": round(fair_decimal(probability), 6),
        "fair_american": rounded_american(probability),
        "fair_american_display": display_american(probability),
        "confidence": confidence(probability),
    }


def assemble() -> dict:
    fixture_by_id = {f["id"]: f for f in FIXTURES}
    source_by_id = {s["id"]: s for s in SOURCES}
    pick_by_fixture = {p["fixture"]: p for p in PICKS}
    lines = []
    predictions = []
    for p in PICKS:
        primary = line_record(p["fixture"], p["id"], "primary", p["market"], p["selection"], p["prob"])
        lines.append(primary)
        predictions.append({
            "id": p["id"], "fixture": p["fixture"], "line_id": p["id"],
            "confidence": primary["confidence"], "text": p["prediction"],
            "sources": [fixture_by_id[p["fixture"]]["source"], *fixture_by_id[p["fixture"]]["extra_sources"]],
        })
        for index, alternative in enumerate(p["alternatives"], 1):
            lines.append(line_record(
                p["fixture"], f"{p['id']}-a{index}", "alternative",
                alternative["market"], alternative["selection"], alternative["prob"],
            ))
    primary_lines = [line for line in lines if line["role"] == "primary"]
    high = [line for line in primary_lines if line["confidence"] == "High"]
    priced_sports = {fixture_by_id[line["fixture"]]["sport"] for line in primary_lines}
    summary = {
        "captured_at": OBSERVED,
        "sports_requested": len(SPORTS),
        "fixture_rows": len(FIXTURES),
        "priced_fixtures": len(PICKS),
        "withheld_fixtures": sum(f["id"] not in pick_by_fixture and f["scope"] == "OLBG-listed" for f in FIXTURES),
        "official_context_fixtures": sum(f["scope"] != "OLBG-listed" for f in FIXTURES),
        "sports_with_prices": len(priced_sports),
        "primary_lines": len(primary_lines),
        "alternative_lines": len(lines) - len(primary_lines),
        "total_lines": len(lines),
        "high_picks": len(high),
        "medium_picks": sum(line["confidence"] == "Medium" for line in primary_lines),
        "low_picks": sum(line["confidence"] == "Low" for line in primary_lines),
        "official_sources": sum(s["official"] for s in SOURCES),
        "discovery_sources": sum(not s["official"] for s in SOURCES),
        "flags": len(FLAGS),
    }
    return {
        "captured_at": OBSERVED,
        "sports": [{"slug": slug, "name": name} for slug, name in SPORTS],
        "sources": SOURCES,
        "fixtures": FIXTURES,
        "lines": lines,
        "predictions": predictions,
        "flags": FLAGS,
        "summary": summary,
        "source_by_id": source_by_id,
        "fixture_by_id": fixture_by_id,
        "pick_by_fixture": pick_by_fixture,
    }
