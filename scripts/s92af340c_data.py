#!/usr/bin/env python3
"""Desk 92af340c — dataset compiler (session 92af340c-olbg1, 2026-10-22).

Builds data/92af340c/{dataset,predictions,flagged,verification}.json from:
  * the desk's own live 17-hub OLBG harvest (data/92af340c/harvest/*.json,
    data/92af340c/olbg.json — read 2026-10-22T08:31Z..09:01Z),
  * the repo's officially-sourced fixtures (data/fixtures.json — every row carries
    governing-body source links; the desk never re-states a fact without one),
  * the published model views (data/lines.json, scripts/model.py conventions), and
  * the live verification ledger (data/verification.json, statuses 44/32/2/56).

Desk tier rules (stricter than the root desk; documented on the Methodology page):
  HIGH   future at cutoff, priced, pick inside the strict -250..+10000 book window,
         both sides officially rated AND measured, ledger-fresh (confirmed/corrected
         within the last 48h) and a hand-authored >=30-word prediction exists.
  MEDIUM future, priced, inside the window with both sides rated, but missing a High
         requirement (stale ledger, unmeasured input or no authored prediction).
  LOW    everything else that is future and priced.
  Rows that are expired, undated or unpriced are published with a null tier — never
  inferred. OLBG hub cards are cross-referenced by event_id only; name matching is
  deliberately not attempted.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from s92af340c_prose import PROSE, SELECTION_LABEL

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DESK = DATA / "92af340c"
CUTOFF = "2026-10-22T09:05:00Z"
FRESH = {"confirmed", "corrected"}


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def rows_of(obj, key):
    return obj if isinstance(obj, list) else obj[key]


def main():
    fixtures = {x["id"]: x for x in rows_of(load("data/fixtures.json"), "fixtures")}
    lines = {x["id"]: x for x in rows_of(load("data/lines.json"), "lines")}
    ledger = {r["id"]: r for r in load("data/verification.json")["rows"]}
    harvest = {}
    for file in sorted((DESK / "harvest").glob("*.json")):
        entry = json.loads(file.read_text(encoding="utf-8"))
        harvest[entry["sport"]] = entry
        for card in entry["events"]:
            harvest.setdefault("_cards", {})[str(card["event_id"])] = (entry["sport"], card)
    olbg_index = load("data/92af340c/olbg.json")

    rows, counts = [], {"future": 0, "expired": 0, "undated": 0, "priced": 0,
                        "high": 0, "medium": 0, "low": 0, "untiered_future": 0}
    for fid, fx in fixtures.items():
        start = fx.get("start_utc") or ""
        ln = lines.get(fid)
        led = ledger.get(fid, {})
        row = {
            "fixture": {
                "id": fid, "sport": fx["sport"], "competition": fx.get("competition"),
                "stage": fx.get("stage"), "start_utc": fx.get("start_utc"),
                "home": fx.get("home"), "away": fx.get("away"),
                "venue": fx.get("venue"), "neutral": fx.get("neutral"),
                "status": fx.get("status"), "sources": fx.get("sources") or [],
            },
            "priced": bool(ln),
            "ledger": {"status": led.get("status"), "checked_at": led.get("checked_at"),
                       "source_name": led.get("source_name"), "source_url": led.get("source_url")},
            "olbg_crossref": None,
        }
        # OLBG harvest cross-reference: event_id matches only, never name-guessed.
        stored = fx.get("olbg") or {}
        eid = stored.get("event_id")
        if eid is not None:
            hit = harvest.get("_cards", {}).get(str(eid))
            card = hit[1] if hit else None
            cross = {
                "event_id": eid,
                "stored_snapshot": {"listed": stored.get("listed"),
                                    "selection": stored.get("selection"),
                                    "market": stored.get("market"),
                                    "consensus": stored.get("consensus")},
                "harvest_2026_10_22": None if not card else {
                    "listed_now": True, "selection": card.get("selection"),
                    "market": card.get("market"), "tips": card.get("tips"),
                    "pct": card.get("pct"), "time_label": card.get("time_label"),
                    "hub": harvest[hit[0]]["url"], "read_utc": harvest[hit[0]]["read_utc"]},
            }
            if card is None:
                cross["harvest_2026_10_22"] = {"listed_now": False,
                    "note": "event_id not rendered in this session's hub read (chunk 0); absence recorded, not inferred"}
            elif (card.get("selection") or "") != (stored.get("selection") or "") or \
                 (card.get("market") or "") != (stored.get("market") or ""):
                cross["drift_note"] = ("consensus differs from the stored snapshot; OLBG tips move intraday — "
                                       "the desk prices from official sources only and records both reads")
            row["olbg_crossref"] = cross

        if not start:
            row["time_status"] = "undated"; counts["undated"] += 1
        elif start > CUTOFF:
            row["time_status"] = "future"; counts["future"] += 1
        else:
            row["time_status"] = "expired"; counts["expired"] += 1

        tier, reasons = None, []
        if ln:
            counts["priced"] += 1
            row["view"] = {
                "pick": ln["pick"], "pick_market": ln["pick_market"], "pick_line": ln["pick_line"],
                "probability": ln["pick_probability"], "odds": ln["pick_odds"],
                "american": ln["pick_american"], "in_window": ln["pick_in_window"],
                "expected_margin": ln["expected_margin"],
                "rating_home": ln["rating_home"], "rating_away": ln["rating_away"],
                "measured_home": ln["rating_measured_home"], "measured_away": ln["rating_measured_away"],
                "both_rated": ln["both_rated"], "both_measured": ln["both_measured"],
                "favourite": ln["favourite"], "markets": ln["markets"],
                "unavailable_markets": ln.get("unavailable_markets") or [],
                "model_notes": ln.get("model_notes") or [],
            }
            if row["time_status"] == "future":
                gates = {
                    "in_window": bool(ln["pick_in_window"]),
                    "both_rated": bool(ln["both_rated"]),
                    "both_measured": bool(ln["both_measured"]),
                    "ledger_fresh": led.get("status") in FRESH,
                    "authored_prediction": fid in PROSE,
                }
                row["gates"] = gates
                if all(gates.values()):
                    tier, counts["high"] = "high", counts["high"] + 1
                    reasons = ["all High gates passed: strict window, measured official ratings both sides, ledger-fresh, authored prediction"]
                elif gates["in_window"] and gates["both_rated"]:
                    tier, counts["medium"] = "medium", counts["medium"] + 1
                    reasons = [f"High gate missing: {k}" for k, ok in gates.items() if not ok]
                else:
                    tier, counts["low"] = "low", counts["low"] + 1
                    reasons = [f"High gate missing: {k}" for k, ok in gates.items() if not ok] or \
                              ["outside the strict window or ratings incomplete"]
        else:
            if row["time_status"] == "future":
                counts["untiered_future"] += 1
            reasons = ["no priced line in the published model views; tier left null rather than inferred"]
        row["desk_confidence"] = tier
        row["tier_reasons"] = reasons
        rows.append(row)

    order = {"high": 0, "medium": 1, "low": 2, None: 3}
    rows.sort(key=lambda r: (order[r["desk_confidence"]], r["fixture"]["sport"], r["fixture"]["id"]))

    dataset = {
        "desk": "92af340c",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cutoff_utc": CUTOFF,
        "session": "92af340c-olbg1 (T63/T35)",
        "pricing": ("Fair (0% overround) headline odds with the 5%-vig book price alongside, per the repo's "
                    "published model conventions (scripts/model.py). The High window is judged on the book "
                    "price, strictly inside -250..+10000."),
        "tier_rules": ("HIGH: future at cutoff + priced + strict window + both sides officially rated and "
                       "measured + ledger-fresh (confirmed/corrected) + hand-authored >=30-word prediction. "
                       "MEDIUM: future + priced + window + both rated, missing another High gate. LOW: all "
                       "other future priced rows. Expired/undated/unpriced rows publish with a null tier."),
        "harvest": {"window": olbg_index["harvest_window_utc"], "hubs": olbg_index["hubs_fetched"],
                    "event_cards": olbg_index["event_cards_total"],
                    "zero_tip_hubs": olbg_index["zero_tip_hubs"]},
        "counts": counts,
        "rows": rows,
    }
    (DESK / "dataset.json").write_text(json.dumps(dataset, indent=1) + "\n", encoding="utf-8")

    preds = []
    for row in rows:
        if row["desk_confidence"] != "high":
            continue
        fid = row["fixture"]["id"]; view = row["view"]; fx = row["fixture"]
        preds.append({
            "match_id": fid, "sport": fx["sport"], "competition": fx["competition"],
            "start_utc": fx["start_utc"], "match": f"{fx['home']} v {fx['away']}",
            "venue": fx["venue"],
            "selection": SELECTION_LABEL[fid], "market": view["pick_market"],
            "line": view["pick_line"], "probability": round(view["probability"], 6),
            "odds": view["odds"], "american": view["american"],
            "winner_call": view["favourite"],
            "sources": fx["sources"],
            "text": PROSE[fid],
            "word_count": len(PROSE[fid].split()),
        })
    predictions = {
        "rule": ("Unique >=30-word hand-authored prediction per strict High pick, written for this desk only "
                 "from facts stored on the fixture row (official-source inputs, ledger evidence, this "
                 "session's fresh hub read). Selection stated verbatim; nothing inferred."),
        "high_window": "-250..+10000 judged on the book price",
        "count": len(preds), "items": preds,
    }
    (DESK / "predictions.json").write_text(json.dumps(predictions, indent=1) + "\n", encoding="utf-8")

    flagged = {"cutoff_utc": CUTOFF, "items": [
        {"id": "H92-BLINDSPOT-AFLW", "severity": "high", "scope": "Aussie Rules hub (Aussie_Rules/22)",
         "finding": "Hub renders 'No tips found.' on the 2026-10-22T08:31Z read despite nine official NAB AFLW Round 11 fixtures (afl.com.au). The desk's four AFLW High picks therefore have no OLBG consensus to compare against.",
         "sources": [{"name": "OLBG Aussie Rules hub (read 2026-10-22)", "url": "https://www.olbg.com/betting-tips/Aussie_Rules/22"},
                     {"name": "Official AFLW fixtures/ladder", "url": "https://www.afl.com.au/aflw/ladder"}]},
        {"id": "H92-BLINDSPOT-LOL", "severity": "high", "scope": "eSports hub (eSports/23)",
         "finding": "Hub renders zero event cards while the LoL Worlds 2026 Swiss stage is live (lolesports.com); the desk row lol-worlds26-tsw-lyon stays priced from the official source with no hub consensus.",
         "sources": [{"name": "OLBG eSports hub (read 2026-10-22)", "url": "https://www.olbg.com/betting-tips/eSports/23"},
                     {"name": "LoL Esports official schedule", "url": "https://lolesports.com/"}]},
        {"id": "H92-CLOCK-EDT", "severity": "high", "scope": "at least eight hubs",
         "finding": "UTC-4 clock defect reproduces (BUG-OLBG-CLOCK-EDT family): '11:14 Kinsley' renders 'Today 06:14' (event 689570); SHL cards show 'Today 13:00' for 17:00Z face-offs; EuroLeague 'Today 14:05' for 18:05Z tip-offs. Motor racing is the exception, rendering local track time (USA GP '25 Oct 16:00' CDT = 21:00Z). Desk never uses hub labels for start times.",
         "sources": [{"name": "OLBG Greyhounds hub (read 2026-10-22)", "url": "https://www.olbg.com/betting-tips/Greyhounds/28"},
                     {"name": "Official F1 race page (US GP)", "url": "https://www.formula1.com/en/racing/2026/united-states"}]},
        {"id": "H92-GAA-DATE", "severity": "high", "scope": "Gaelic Football hub, event 3536",
         "finding": "Rathgormack v The Nire still shows '01 Nov 10:30' on the 2026-10-22 read; official Munster GAA fixtures schedule the Waterford SFC final for Sun 25 Oct 2026 14:30 UTC. Desk keeps the corrected official value (BUG-OLBG-3536-DATE reproduces).",
         "sources": [{"name": "OLBG Gaelic Football hub (read 2026-10-22)", "url": "https://www.olbg.com/betting-tips/Gaelic_Football/25"},
                     {"name": "Munster GAA official fixtures", "url": "https://www.munster.gaa.ie/"}]},
        {"id": "H92-ID-REUSE", "severity": "medium", "scope": "Basketball hub, event 535918",
         "finding": "event_id 535918 renders 'Anadolu Efes vs Besiktas' today; earlier this week the same id carried a different tie (finding BUG-OLBG-535918-EUROCUP). OLBG ids are recycled and must not be used as durable keys.",
         "sources": [{"name": "OLBG Basketball hub (read 2026-10-22)", "url": "https://www.olbg.com/betting-tips/Basketball/4"}]},
        {"id": "H92-DRIFT-12046", "severity": "low", "scope": "Handball hub, event 12046",
         "finding": "Barça v Montpellier consensus moved from the stored snapshot (Montpellier 2/6) to Barcelona 8/14 (57%) on the fresh read; tips move intraday. The desk prices from official EHF standings only and records both reads.",
         "sources": [{"name": "OLBG Handball hub (read 2026-10-22)", "url": "https://www.olbg.com/betting-tips/Handball/20"},
                     {"name": "EHF Champions League official", "url": "https://ehfcl.eurohandball.com/"}]},
        {"id": "H92-MARKET-LABEL", "severity": "low", "scope": "Gaelic Football hub",
         "finding": "Gaelic cards render no market label beside handicap-style selections ('Nemo Rangers +1.50'), unique among the seventeen hubs in this read.",
         "sources": [{"name": "OLBG Gaelic Football hub (read 2026-10-22)", "url": "https://www.olbg.com/betting-tips/Gaelic_Football/25"}]},
        {"id": "H92-PAGINATION", "severity": "low", "scope": "all 17 hubs",
         "finding": "Only chunk 0 of each hub's paginated text layer was re-read this session; per-hub chunk coverage is recorded in each harvest file and truncated boundary cards are listed as observations, never as data.",
         "sources": [{"name": "Desk harvest index", "url": "https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/92af340c/olbg.json"}]},
        {"id": "H92-STALE-TIERS", "severity": "medium", "scope": "rows excluded from High",
         "finding": "Future priced rows inside the window but with a not_rechecked or flagged ledger status (e.g. the two EuroLeague rows and four PDC rows) are held at Medium/Low by the desk's freshness gate; two flagged NHL rows (LIVE-F-V4 family) stay out of High until re-confirmed.",
         "sources": [{"name": "Live verification ledger", "url": "https://github.com/buffedlizard55-lab/OLBG1/blob/main/reports/LIVE_VERIFICATION.md"}]},
    ]}
    (DESK / "flagged.json").write_text(json.dumps(flagged, indent=1) + "\n", encoding="utf-8")

    verification = {
        "method": ("Desk-level verification view: the seventeen hub reads of 2026-10-22 (this desk's harvest) "
                   "plus the repo's live verification ledger summary. Row-level official-source evidence lives "
                   "on each fixture and in reports/LIVE_VERIFICATION.md; nothing here is inferred."),
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "harvest": [{"sport": h["sport"], "hub": h["url"], "read_utc": h["read_utc"],
                     "cards": h["event_cards_captured"], "chunks_read": h["chunks_read"],
                     "chunks_total": h["chunks_total"]}
                    for h in (harvest[k] for k in sorted(harvest) if not k.startswith("_"))],
        "ledger_summary": load("data/verification.json")["summary"],
    }
    (DESK / "verification.json").write_text(json.dumps(verification, indent=1) + "\n", encoding="utf-8")

    print(f"desk dataset: {counts} | predictions: {len(preds)} | flagged: {len(flagged['items'])}")
    for p in preds:
        print(f"  HIGH {p['match_id']:22} {p['selection']:26} {p['american']:>5} p={p['probability']:.3f} words={p['word_count']}")


if __name__ == "__main__":
    main()
