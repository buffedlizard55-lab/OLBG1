#!/usr/bin/env python3
"""live_diff.py - deterministic diff between the live OLBG hub capture and the desk dataset.

Reads:
  data/live_snapshot.json   (captured from OLBG sport hubs; each row keeps its OLBG event URL)
  data/live_baseline.json   (frozen pre-refresh OLBG fields, so the diff stays stable after a rebuild)
  data/fixtures.json        (the verified desk dataset; used for ids, status and official sources)

Writes:
  data/live_diff.json

No network request is made here.  The capture itself was performed with a browser-class
fetcher against the public OLBG sport hubs and is timestamped in the snapshot file.  This
script only compares what was captured with what is committed, so the comparison is
reproducible from the repository alone.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONSENSUS_RE = re.compile(r"^\d+/\d+ win tips \(\d+%\)$")


def norm(value: str | None) -> str:
    return (value or "").strip().lower()


def main() -> None:
    snap = json.loads((ROOT / "data" / "live_snapshot.json").read_text())
    fixtures = json.loads((ROOT / "data" / "fixtures.json").read_text())["fixtures"]
    baseline_path = ROOT / "data" / "live_baseline.json"
    # The baseline is frozen so that re-running the pipeline after the consensus overlay has
    # been applied cannot silently erase the change history.
    baseline = json.loads(baseline_path.read_text())["rows"] if baseline_path.exists() else {}

    by_event: dict[int, dict] = {}
    for fx in fixtures:
        olbg = fx.get("olbg") or {}
        if olbg.get("event_id"):
            by_event[int(olbg["event_id"])] = fx

    live = snap["events"]
    live_ids = {int(ev["event_id"]) for ev in live}

    matched: list[dict] = []
    changed: list[dict] = []
    new: list[dict] = []
    for ev in live:
        eid = int(ev["event_id"])
        fx = by_event.get(eid)
        if fx is None:
            new.append(ev)
            continue
        matched.append(ev)
        olbg = baseline.get(str(eid)) or fx["olbg"]
        if (
            norm(olbg.get("selection")) != norm(ev["selection"])
            or norm(olbg.get("market")) != norm(ev["market"])
            or norm(olbg.get("consensus")) != norm(ev["consensus"])
        ):
            changed.append(
                {
                    "event_id": eid,
                    "sport": ev["sport"],
                    "title": ev["title"],
                    "fixture_id": fx["id"],
                    "was": {
                        "market": olbg.get("market"),
                        "selection": olbg.get("selection"),
                        "consensus": olbg.get("consensus"),
                    },
                    "now": {
                        "market": ev["market"],
                        "selection": ev["selection"],
                        "consensus": ev["consensus"],
                    },
                    "selection_flipped": norm(olbg.get("selection")) != norm(ev["selection"]),
                    "olbg_url": ev["url"],
                }
            )

    not_in_capture = [
        {
            "fixture_id": fx["id"],
            "sport": fx["sport"],
            "event_id": int(fx["olbg"]["event_id"]),
            "home": fx.get("home"),
            "away": fx.get("away"),
            "competition": fx.get("competition"),
            "start_utc": fx.get("start_utc"),
            "olbg_url": fx["olbg"].get("url"),
            "status": fx.get("status"),
        }
        for fx in fixtures
        if (fx.get("olbg") or {}).get("event_id")
        and int(fx["olbg"]["event_id"]) not in live_ids
    ]

    per_sport = Counter(ev["sport"] for ev in live)
    flips = [c for c in changed if c["selection_flipped"]]

    doc = {
        "captured_utc": snap["fetched_utc"],
        "snapshot_source": snap["source"],
        "capture_note": snap.get("capture_note"),
        "summary": {
            "live_events_captured": len(live),
            "sports_with_live_events": len(per_sport),
            "sports_with_no_live_tips": snap.get("sports_with_no_live_tips", []),
            "dataset_rows": len(fixtures),
            "dataset_rows_with_olbg_event_id": len(by_event),
            "matched": len(matched),
            "consensus_or_selection_changed": len(changed),
            "selection_flipped": len(flips),
            "new_not_in_dataset": len(new),
            "dataset_rows_absent_from_capture": len(not_in_capture),
        },
        "per_sport_live_capture": dict(sorted(per_sport.items(), key=lambda kv: (-kv[1], kv[0]))),
        "changed": changed,
        "new_not_in_dataset": new,
        "dataset_rows_absent_from_capture": not_in_capture,
    }
    (ROOT / "data" / "live_diff.json").write_text(json.dumps(doc, indent=1) + "\n")
    s = doc["summary"]
    print(
        f"Live capture {doc['captured_utc']}: {s['live_events_captured']} events across "
        f"{s['sports_with_live_events']} sports | matched {s['matched']} | changed "
        f"{s['consensus_or_selection_changed']} ({s['selection_flipped']} selection flips) | "
        f"new {s['new_not_in_dataset']} | dataset rows absent {s['dataset_rows_absent_from_capture']}"
    )


if __name__ == "__main__":
    main()
