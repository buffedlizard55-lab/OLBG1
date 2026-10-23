#!/usr/bin/env python3
"""T6B47 pick selection.

Rules, applied in this order and recorded per row so the site can show why a row
was kept or dropped:

  R1  fixture must be upcoming at build time (21:30Z, 23 Oct 2026)
  R2  fixture must not carry a cross-desk directional conflict (audit F05)
  R3  fixture must have a recorded fact note (form / statistics / injury) from a
      source desk, because a write-up without a recorded fact would be invention
  R4  estimated implied probability must be > 0.70
  R5  probability must not exceed 0.88 -- anything above that is a near-certainty
      that pays nothing and is not a pick
  R6  selection must be a main line, not an alternate-line artefact: no underdog
      "+" handicap at a high probability, no "v Field" constructions
  R7  one pick per fixture; duplicated market labels across desks are collapsed by
      canonical bet key so the same bet never appears twice

Tier labels
  high-in-window : >70% AND fair American inside -250..+10000 (the brief's window)
  out-of-window : >70% but shorter than -250, i.e. stronger than the window allows;
                  published and labelled, never relabelled as in-window
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "6b47ea39"
NOW = "2026-10-23T21:30:00Z"

SPORT_ORDER = [
    "Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts", "Baseball",
    "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing", "Handball",
    "Ice Hockey", "Basketball", "Rugby League",
]
CODE = {
    "Golf": "GOL", "Volleyball": "VOL", "Rugby Union": "RGU", "Cricket": "CRI", "Snooker": "SNO",
    "Darts": "DAR", "Baseball": "BSB", "Gaelic Sports": "GAE", "Greyhounds": "GRY", "Tennis": "TEN",
    "Motor Racing": "MOT", "Handball": "HAN", "Ice Hockey": "ICE", "Basketball": "BAS", "Rugby League": "RGL",
}
FIELDISH = re.compile(r"\bfield\b|remaining|quarter|contingent|traps? [1-6]|bottom-half|points contenders|qualifying winner|scu v", re.I)


def norm(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", str(text).lower()).split())


def canonical_bet(event: dict, line: dict) -> str:
    """A desk-independent identity for 'the same bet', so duplicate labels collapse."""
    selection = str(line["selection"])
    low = selection.lower()
    total = re.search(r"\b(over|under)\s+([0-9]+(?:\.5)?)", low)
    if total:
        return f"TOTAL|{total.group(1)}|{total.group(2)}"
    handicap = re.search(r"([+-])\s*([0-9]+(?:\.5)?)", low)
    team = None
    for side in (event["home"], event["away"]):
        if norm(side) and norm(side) in norm(selection):
            team = norm(side)
            break
    if handicap and team:
        return f"HCP|{team}|{handicap.group(1)}{handicap.group(2)}"
    if team:
        return f"WIN|{team}"
    return "OTHER|" + norm(line["market"]) + "|" + norm(re.sub(r"\b(to win|to beat .*|top-?\d+ finish.*|winner)\b", "", low))


def is_alternate_artefact(line: dict) -> bool:
    low = str(line["selection"]).lower()
    if re.search(r"\+\s*[0-9]+(?:\.5)?", low) and line["probability"] > 0.72:
        return True
    if re.search(r"outside top|any other driver", low):
        return True
    return False


def main() -> None:
    slate = json.loads((OUT / "slate.json").read_text(encoding="utf-8"))
    audit = json.loads((OUT / "audit.json").read_text(encoding="utf-8"))
    conflicted = {c["event"] for c in audit["directional_conflicts"]}

    candidates = []
    watch: list[dict] = []
    dropped = defaultdict(int)
    for event in slate["events"]:
        seen_bets: set[str] = set()
        for line in event["markets"]:
            reasons = []
            if event["state"] != "upcoming":
                reasons.append("R1 elapsed")
            if event["id"] in conflicted:
                reasons.append("R2 cross-desk conflict")
            if not event["facts"]:
                reasons.append("R3 no recorded fact note")
            if line["probability"] <= 0.60:
                reasons.append("R4 below 60%")
            if line["probability"] > 0.88:
                reasons.append("R5 above 88%")
            if FIELDISH.search(event["home"] + " " + event["away"]):
                reasons.append("R6 field construction")
            if is_alternate_artefact(line):
                reasons.append("R6 alternate-line artefact")
            key = canonical_bet(event, line)
            if key in seen_bets:
                reasons.append("R7 duplicate bet")
            seen_bets.add(key)
            if reasons:
                dropped[reasons[0]] += 1
                continue
            if line["probability"] <= 0.70:
                watch.append(
                    {
                        "event_id": event["id"],
                        "sport": event["sport"],
                        "match": f"{event['home']} v {event['away']}",
                        "start_utc": event["start_utc"],
                        "competition": event["competition"],
                        "market": line["market"],
                        "selection": line["selection"],
                        "probability": round(1.0 / line["decimal"], 4),
                        "decimal": line["decimal"],
                        "american": line["american"],
                        "source_desk": line["source_desk"],
                        "official_sources": event["official_sources"],
                        "tier": "medium-watch",
                    }
                )
                continue
            candidates.append(
                {
                    "event_id": event["id"],
                    "sport": event["sport"],
                    "sport_slug": event["sport_slug"],
                    "match": f"{event['home']} v {event['away']}",
                    "home": event["home"],
                    "away": event["away"],
                    "competition": event["competition"],
                    "start_utc": event["start_utc"],
                    "venue": event["venue"],
                    "market": line["market"],
                    "selection": line["selection"],
                    "bet_key": key,
                    "probability": round(1.0 / line["decimal"], 4),
                    "decimal": line["decimal"],
                    "american": line["american"],
                    "tier": "high-in-window" if line["band"] == "in" else "out-of-window",
                    "band": line["band"],
                    "source_desk": line["source_desk"],
                    "desks": line["desks"],
                    "official_sources": event["official_sources"],
                    "facts": event["facts"],
                    "provenance": event["provenance"],
                }
            )

    # one pick per fixture: keep the strongest defensible line, preferring in-window
    by_event: dict[str, list[dict]] = defaultdict(list)
    for row in candidates:
        by_event[row["event_id"]].append(row)
    chosen = []
    for rows in by_event.values():
        rows.sort(key=lambda r: (r["band"] != "in", -r["probability"]))
        chosen.append(rows[0])

    by_sport: dict[str, list[dict]] = defaultdict(list)
    for row in chosen:
        by_sport[row["sport"]].append(row)

    picks = []
    shortfalls = []
    for sport in SPORT_ORDER:
        rows = sorted(by_sport.get(sport, []), key=lambda r: (r["band"] != "in", -r["probability"]))
        # prefer in-window rows first, then the strongest of the rest; cap five
        top = rows[:5]
        for index, row in enumerate(top, start=1):
            row["rank"] = index
            row["pick_id"] = f"{CODE[sport]}-{index:02d}"
            picks.append(row)
        if len(top) < 5:
            shortfalls.append(
                {
                    "sport": sport,
                    "available": len(rows),
                    "target": 5,
                    "reason": (
                        "No further fixture in this sport clears all seven selection rules. "
                        "Every remaining candidate is either elapsed at build time, carries a cross-desk "
                        "directional conflict, has no recorded fact note to write from, is below the 70% "
                        "threshold, is a near-certainty above 88%, or is an alternate-line artefact."
                    ),
                }
            )

    watch_by_sport: dict[str, list[dict]] = defaultdict(list)
    seen_watch: set[str] = set()
    for row in sorted(watch, key=lambda r: -r["probability"]):
        if row["event_id"] in seen_watch:
            continue
        seen_watch.add(row["event_id"])
        watch_by_sport[row["sport"]].append(row)
    watch_rows = []
    for sport in SPORT_ORDER:
        need = 5 - len([p for p in picks if p["sport"] == sport])
        for row in watch_by_sport.get(sport, [])[: max(0, need)]:
            row["rank"] = len([p for p in picks if p["sport"] == sport]) + len(
                [w for w in watch_rows if w["sport"] == sport]
            ) + 1
            row["pick_id"] = f"{CODE[sport]}-W{row['rank']:02d}"
            watch_rows.append(row)

    OUT.joinpath("picks.json").write_text(
        json.dumps(
            {
                "desk": "6b47ea39",
                "built_utc": NOW,
                "rules": [
                    "R1 upcoming only",
                    "R2 no cross-desk directional conflict",
                    "R3 recorded fact note required",
                    "R4 implied probability > 0.70",
                    "R5 implied probability <= 0.88",
                    "R6 main lines only (no field constructions or alternate artefacts)",
                    "R7 one pick per fixture, duplicate bets collapsed",
                ],
                "dropped_first_reason": dict(dropped),
                "count": len(picks),
                "in_window": sum(1 for p in picks if p["band"] == "in"),
                "out_of_window": sum(1 for p in picks if p["band"] == "out"),
                "shortfalls": shortfalls,
                "picks": picks,
                "watchlist": watch_rows,
            },
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"picks: {len(picks)} ({sum(1 for p in picks if p['band']=='in')} in window)")
    for sport in SPORT_ORDER:
        rows = [p for p in picks if p["sport"] == sport]
        print(f"  {sport:14s} {len(rows)}/5  " + " · ".join(f"{r['selection'][:26]} p={r['probability']:.3f} {r['american']:.0f}" for r in rows))
    print("shortfalls:", [(s['sport'], s['available']) for s in shortfalls])
    print("dropped by first reason:", dict(dropped))


if __name__ == "__main__":
    main()
