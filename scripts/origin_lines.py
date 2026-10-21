#!/usr/bin/env python3
"""
origin_lines.py - Deterministic multi-market line origination & unified dataset export.

Reads data/fixtures.json and emits:
  - data/lines.json
  - data/predictions.json
  - datasets/matches_full.json
  - datasets/matches_full.csv
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from model import OVERROUND, SPORTS, price_match
from high_predictions import HIGH_PREDICTION_LINES, HIGH_PREDICTION_TEXTS

DATE_ANCHOR = "2026-10-21"


def source_backed_prediction(fixture: dict, line: dict, selection_line: str) -> str:
    """Render the unique fact-only prose reserved for this high-confidence fixture."""
    return HIGH_PREDICTION_TEXTS[fixture["id"]].format(selection=selection_line)


def main() -> None:
    fixtures_doc = json.loads((ROOT / "data" / "fixtures.json").read_text())
    fixtures = fixtures_doc["fixtures"]

    priced_lines: list[dict] = []
    for f in fixtures:
        if f.get("away"):
            priced_lines.append(price_match(f))

    high_ids = [l["id"] for l in priced_lines if l["confidence"] == "high"]
    line_ids = set(HIGH_PREDICTION_LINES)
    text_ids = set(HIGH_PREDICTION_TEXTS)
    missing = set(high_ids) - line_ids
    extra = line_ids - set(high_ids)
    if missing or extra or line_ids != text_ids:
        raise RuntimeError(
            f"High-prediction bijection mismatch! missing={missing}, extra={extra}, "
            f"line_ids!=text_ids={line_ids != text_ids}"
        )

    fixtures_by_id = {f["id"]: f for f in fixtures}
    priced_by_id = {l["id"]: l for l in priced_lines}

    predictions_out = []
    for mid in high_ids:
        selection_line = HIGH_PREDICTION_LINES[mid]
        fx = fixtures_by_id[mid]
        ln = priced_by_id[mid]
        prediction_text = source_backed_prediction(fx, ln, selection_line)
        wc = len(prediction_text.split())
        assert wc >= 30, f"{mid} prediction under 30 words ({wc})"
        facts = [
            f"{fx['home']}: {fx['inputs']['home']['label']} — {fx['inputs']['home']['value']}",
            f"{fx['away']}: {fx['inputs']['away']['label']} — {fx['inputs']['away']['value']}",
            f"Recommended market: {selection_line}",
        ]
        predictions_out.append({
            "match_id": mid,
            "selection": ln["pick"],
            "bet_line": selection_line,
            "text": prediction_text,
            "words": wc,
            "facts": facts,
            "sources": fx["sources"],
        })

    lines_doc = {
        "generated": DATE_ANCHOR,
        "model": "olbg-independent-logit-normal-v2.0",
        "overround": OVERROUND,
        "sports": {k: {kk: vv for kk, vv in v.items()} for k, v in SPORTS.items()},
        "count": len(priced_lines),
        "confidence_counts": dict(Counter(l["confidence"] for l in priced_lines)),
        "lines": priced_lines,
    }
    predictions_doc = {
        "generated": DATE_ANCHOR,
        "rule": "Unique, non-repetitive, human-written >=30-word analysis limited to each fixture's versioned, source-linked governing-body inputs and explicitly labelled independent model selection.",
        "count": len(predictions_out),
        "items": predictions_out,
        "predictions": predictions_out,
    }

    (ROOT / "data" / "lines.json").write_text(json.dumps(lines_doc, indent=2) + "\n")
    (ROOT / "data" / "predictions.json").write_text(json.dumps(predictions_doc, indent=2) + "\n")

    # Build unified matches_full.json + matches_full.csv across all 134 rows
    lines_by_id = {l["id"]: l for l in priced_lines}
    preds_by_id = {p["match_id"]: p for p in predictions_out}

    full_rows = []
    csv_rows = []
    for f in fixtures:
        lid = lines_by_id.get(f["id"])
        pred = preds_by_id.get(f["id"])
        mk_map = {m["key"]: m for m in lid["markets"]} if lid else {}

        w_mkt = mk_map.get("winner")
        h_mkt = mk_map.get("handicap")
        t_mkt = mk_map.get("total")
        dnb_mkt = mk_map.get("dnb")

        home_odds = w_mkt["outcomes"][0]["odds"] if w_mkt else ""
        draw_odds = (w_mkt["outcomes"][1]["odds"] if (w_mkt and len(w_mkt["outcomes"]) == 3) else "")
        away_odds = (w_mkt["outcomes"][-1]["odds"] if w_mkt else "")

        hcap_summary = (
            f"{h_mkt['outcomes'][0]['selection']} @ {h_mkt['outcomes'][0]['odds']} | "
            f"{h_mkt['outcomes'][1]['selection']} @ {h_mkt['outcomes'][1]['odds']}"
            if h_mkt else ""
        )
        total_summary = (
            f"{t_mkt['outcomes'][0]['selection']} @ {t_mkt['outcomes'][0]['odds']} | "
            f"{t_mkt['outcomes'][1]['selection']} @ {t_mkt['outcomes'][1]['odds']}"
            if t_mkt else ""
        )
        dnb_summary = (
            f"{dnb_mkt['outcomes'][0]['selection']} @ {dnb_mkt['outcomes'][0]['odds']} | "
            f"{dnb_mkt['outcomes'][1]['selection']} @ {dnb_mkt['outcomes'][1]['odds']}"
            if dnb_mkt else ""
        )

        merged = {
            **f,
            "is_h2h": bool(f.get("away")),
            "pricing": lid,
            "prediction": pred,
        }
        full_rows.append(merged)

        csv_rows.append({
            "id": f["id"],
            "sport": f["sport"],
            "competition": f["competition"],
            "stage": f.get("stage", ""),
            "start_utc": f.get("start_utc") or "",
            "date_local": f.get("date_local") or "",
            "home": f["home"],
            "away": f.get("away", ""),
            "venue": f.get("venue", ""),
            "status": f["status"],
            "official_source_name": f["sources"][0]["name"],
            "official_source_url": f["sources"][0]["url"],
            "olbg_event_id": (f.get("olbg") or {}).get("event_id", ""),
            "olbg_consensus": (f.get("olbg") or {}).get("consensus", ""),
            "home_odds": home_odds,
            "draw_odds": draw_odds,
            "away_odds": away_odds,
            "dnb_market": dnb_summary,
            "handicap_market": hcap_summary,
            "total_market": total_summary,
            "pick": lid["pick"] if lid else "Field event (no H2H line)",
            "confidence": lid["confidence"] if lid else "",
            "prediction_selection": pred["selection"] if pred else "",
            "prediction_text": pred["text"] if pred else "",
            "flags": " ; ".join(f.get("flags", [])),
        })

    (ROOT / "datasets").mkdir(exist_ok=True)
    (ROOT / "datasets" / "matches_full.json").write_text(
        json.dumps({"generated": DATE_ANCHOR, "count": len(full_rows), "matches": full_rows}, indent=2) + "\n"
    )
    with (ROOT / "datasets" / "matches_full.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(csv_rows)

    print(
        f"Originated lines for {len(priced_lines)} H2H matches "
        f"(confidence={lines_doc['confidence_counts']}), "
        f"{len(predictions_out)} high-confidence human predictions, and exported datasets/matches_full.{{json,csv}}."
    )


if __name__ == "__main__":
    main()
