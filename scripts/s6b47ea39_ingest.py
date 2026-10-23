#!/usr/bin/env python3
"""T6B47 ingest: build one reconciled slate from the retained 23-Oct-2026 desks.

This script reads only files already committed to the repository. It never
fetches anything and never invents a value. Every output fact keeps the
official URL and the capture timestamp of the desk that recorded it.

Sources of record
-----------------
8a900c04 : 75 events, 5 per brief sport, 472 originated markets, per-event
           form / injury / statistics notes, captured 2026-10-23T16:45Z.
496eaf02 : 81 fixtures, 200 markets / 460 outcomes, captured 2026-10-23T20:30Z.
65331685 : 62 fixtures, 723 prices, captured 2026-10-23T20:40Z.

Output: data/6b47ea39/slate.json
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "6b47ea39"

SPORTS = [
    ("Golf", "golf"),
    ("Volleyball", "volleyball"),
    ("Rugby Union", "rugby-union"),
    ("Cricket", "cricket"),
    ("Snooker", "snooker"),
    ("Darts", "darts"),
    ("Baseball", "baseball"),
    ("Gaelic Sports", "gaelic-sports"),
    ("Greyhounds", "greyhounds"),
    ("Tennis", "tennis"),
    ("Motor Racing", "motor-racing"),
    ("Handball", "handball"),
    ("Ice Hockey", "ice-hockey"),
    ("Basketball", "basketball"),
    ("Rugby League", "rugby-league"),
]
SPORT_NAME = dict(SPORTS)
SLUG_OF = {name.lower(): slug for name, slug in SPORTS}
ALIASES = {
    "gaelic football": "Gaelic Sports",
    "gaelic games": "Gaelic Sports",
    "hurling": "Gaelic Sports",
    "ice-hockey": "Ice Hockey",
    "rugby league": "Rugby League",
    "rugby union": "Rugby Union",
    "motor racing": "Motor Racing",
}


def american(decimal: float) -> float:
    if decimal <= 1.0:
        raise ValueError(f"decimal odds must exceed 1.0, got {decimal}")
    return round(-100.0 / (decimal - 1.0), 1) if decimal < 2.0 else round(100.0 * (decimal - 1.0), 1)


def implied(decimal: float) -> float:
    return 1.0 / decimal


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def canonical_sport(value: str) -> str:
    raw = str(value).strip().lower().replace("-", " ")
    for name, _slug in SPORTS:
        if raw == name.lower().replace("-", " "):
            return name
    if raw in ALIASES:
        return ALIASES[raw]
    raise KeyError(f"sport outside the brief: {value!r}")


def matchup_key(home: str, away: str, start_utc: str = "") -> str:
    """Same two sides *and* the same fixture date. Series games between the same two
    teams (MLB World Series, multi-day racing cards) are distinct fixtures and must not
    collapse into one row."""
    date = str(start_utc)[:10]
    return " | ".join(sorted([norm(home), norm(away)])) + " | " + date


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


# --------------------------------------------------------------------------
# 8a900c04 — fact base (form / injuries / statistics per event)
# --------------------------------------------------------------------------
def read_8a():
    desk = load(DATA / "8a900c04" / "desk.json")
    captured = "2026-10-23T16:45:00Z"
    events = []
    for event in desk["events"]:
        sport = canonical_sport(event["sport"])
        markets = []
        for market in event["markets"]:
            dec = float(market["fair_decimal"])
            markets.append(
                {
                    "desk": "8a900c04",
                    "market": market["market_label"],
                    "market_type": market["market_type"],
                    "selection": market["selection"],
                    "probability": round(float(market["fair_prob"]), 4),
                    "decimal": round(dec, 3),
                    "american": american(dec),
                    "declared_american": market["fair_american"],
                    "declared_confidence": market.get("confidence"),
                    "desk_captured_utc": captured,
                }
            )
        events.append(
            {
                "desk": "8a900c04",
                "desk_id": event["id"],
                "sport": sport,
                "competition": event.get("competition") or "",
                "home": event.get("home") or "",
                "away": event.get("away") or "",
                "start_utc": event.get("start_utc") or "",
                "venue": event.get("venue") or "",
                "official_sources": [
                    url
                    for url in {
                        event.get("official_url"),
                        event.get("secondary_official_url"),
                        event.get("publisher_crossref_url"),
                    }
                    if url
                ],
                "olbg_url": event.get("olbg_url"),
                "facts": {
                    "form": event.get("form_summary"),
                    "injuries": event.get("injury_report"),
                    "statistics": event.get("stats_note"),
                },
                "fact_read_utc": captured,
                "markets": markets,
                "declared": {
                    "winner_selection": event.get("match_winner_selection"),
                    "winner_probability": event.get("match_winner_prob"),
                    "confidence": event.get("confidence"),
                    "recommended_market": event.get("recommended_market"),
                    "recommended_selection": event.get("recommended_selection"),
                },
                "flags": list(event.get("flags") or []),
                "captured_utc": captured,
            }
        )
    return events


# --------------------------------------------------------------------------
# 496eaf02 — evening desk, fixture + market book
# --------------------------------------------------------------------------
def read_496e():
    doc = load(DATA / "496eaf02" / "fixtures.json")
    captured = doc.get("captured_utc") or "2026-10-23T20:30:00Z"
    with (DATA / "496eaf02" / "markets.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    books: dict[str, list] = {}
    for row in rows:
        dec = float(row["fair_decimal"])
        books.setdefault(row["fixture_id"], []).append(
            {
                "desk": "496eaf02",
                "market": row["market"],
                "market_type": "",
                "selection": row["selection"],
                "probability": round(float(row["probability"]), 4),
                "decimal": round(dec, 3),
                "american": american(dec),
                "declared_american": float(row["fair_american"]),
                "declared_confidence": None,
                "desk_captured_utc": captured,
            }
        )
    events = []
    for fixture in doc["fixtures"]:
        events.append(
            {
                "desk": "496eaf02",
                "desk_id": fixture["id"],
                "sport": canonical_sport(fixture["sport"]),
                "competition": fixture.get("competition") or "",
                "home": fixture.get("participant_a") or "",
                "away": fixture.get("participant_b") or "",
                "start_utc": fixture.get("start_utc") or "",
                "venue": fixture.get("venue") or "",
                "official_sources": [s["url"] for s in fixture.get("sources") or []],
                "olbg_url": None,
                "facts": {},
                "fact_read_utc": captured,
                "markets": books.get(fixture["id"], []),
                "declared": {},
                "flags": list(fixture.get("flags") or []),
                "state_declared": fixture.get("state"),
                "captured_utc": captured,
            }
        )
    return events


# --------------------------------------------------------------------------
# 65331685 — evening desk with official record strings
# --------------------------------------------------------------------------
def read_653():
    doc = load(DATA / "65331685" / "desk.json")
    captured = doc.get("generated_utc") or "2026-10-23T20:40:00Z"
    books: dict[str, list] = {}
    for market in doc["markets"]:
        dec = float(market["fair_decimal"])
        books.setdefault(market["fixture_id"], []).append(
            {
                "desk": "65331685",
                "market": market["market"],
                "market_type": "",
                "selection": market["selection"],
                "probability": round(float(market["prob"]), 4),
                "decimal": round(dec, 3),
                "american": american(dec),
                "declared_american": float(market["fair_american"]),
                "declared_confidence": market.get("tier"),
                "desk_captured_utc": captured,
            }
        )
    events = []
    for event in doc["events"]:
        official = event.get("official") or {}
        facts = {}
        if official.get("record_home") or official.get("record_away"):
            facts["form"] = (
                f"Official record at capture: {event['home']} {official.get('record_home','')}"
                f"; {event['away']} {official.get('record_away','')}."
            )
        if event.get("note"):
            facts["statistics"] = event["note"]
        events.append(
            {
                "desk": "65331685",
                "desk_id": event["id"],
                "sport": canonical_sport(event["sport"]),
                "competition": event.get("competition") or "",
                "home": event.get("home") or "",
                "away": event.get("away") or "",
                "start_utc": event.get("start_utc") or "",
                "venue": event.get("venue") or "",
                "official_sources": list(dict.fromkeys(official.get("sources") or [])),
                "olbg_url": (event.get("olbg") or {}).get("url"),
                "facts": facts,
                "fact_read_utc": official.get("read_utc") or captured,
                "markets": books.get(event["id"], []),
                "declared": {},
                "flags": [],
                "state_declared": event.get("state"),
                "official_record": {
                    "home": official.get("record_home"),
                    "away": official.get("record_away"),
                    "game_id": official.get("game_id"),
                },
                "captured_utc": captured,
            }
        )
    return events


def merge(desks: list[list[dict]]) -> list[dict]:
    """Group observations into fixtures: same two sides, same fixture date.

    Desks disagree about whether a start time is published (496eaf02 leaves golf
    starts blank). A blank-dated observation therefore joins the single dated bucket
    for that matchup when exactly one exists; with several dated buckets it is kept
    separate and surfaced by the audit rather than guessed onto a date.
    """
    groups: dict[str, list[dict]] = {}
    for events in desks:
        for event in events:
            groups.setdefault(matchup_key(event["home"], event["away"]), []).append(event)

    records: list[dict] = []
    for pair, observations in groups.items():
        dated: dict[str, list[dict]] = {}
        undated: list[dict] = []
        for observation in observations:
            date = str(observation.get("start_utc") or "")[:10]
            (dated.setdefault(date, []) if date else undated).append(observation)
        if len(dated) == 1:
            (list(dated.values())[0]).extend(undated)
            undated = []
        for date, bucket in dated.items():
            records.append(_merge_bucket(pair, date, bucket))
        if undated:
            records.append(_merge_bucket(pair, "", undated))
    return records


def _merge_bucket(pair: str, date: str, events: list[dict]) -> dict:
    record = {
        "key": pair + " | " + date,
        "sport": events[0]["sport"],
        "home": events[0]["home"],
        "away": events[0]["away"],
        "competition": "",
        "start_utc": "",
        "venue": "",
        "official_sources": [],
        "olbg_urls": [],
        "provenance": [],
        "markets": [],
        "facts": {},
        "declared": {},
        "flags": [],
    }
    for event in sorted(events, key=lambda e: e["captured_utc"]):
        if event["start_utc"] and (not record["start_utc"] or event["captured_utc"] > record.get("_start_src", "")):
            record["start_utc"] = event["start_utc"]
            record["_start_src"] = event["captured_utc"]
        if event["competition"] and not record["competition"]:
            record["competition"] = event["competition"]
        if event["venue"] and not record["venue"]:
            record["venue"] = event["venue"]
        for url in event["official_sources"]:
            if url not in record["official_sources"]:
                record["official_sources"].append(url)
        if event.get("olbg_url") and event["olbg_url"] not in record["olbg_urls"]:
            record["olbg_urls"].append(event["olbg_url"])
        record["provenance"].append(
            {
                "desk": event["desk"],
                "desk_id": event["desk_id"],
                "captured_utc": event["captured_utc"],
                "markets": len(event["markets"]),
                "fact_read_utc": event.get("fact_read_utc"),
            }
        )
        for name, value in (event.get("facts") or {}).items():
            if value and name not in record["facts"]:
                record["facts"][name] = {
                    "text": value,
                    "desk": event["desk"],
                    "read_utc": event.get("fact_read_utc"),
                    "sources": event["official_sources"],
                }
        for name, value in (event.get("declared") or {}).items():
            if value and name not in record["declared"]:
                record["declared"][name] = value
        for flag in event.get("flags") or []:
            if flag not in record["flags"]:
                record["flags"].append(flag)
        record["markets"].extend(event["markets"])
    if len(record["provenance"]) > 1:
        record["provenance"].sort(key=lambda p: p["captured_utc"], reverse=True)
    return record



STOPWORDS = {"fc", "rfc", "the", "women", "men", "handball", "rugby", "club", "de", "hb", "sc"}


def tokens(name: str) -> set[str]:
    return {t for t in norm(name).split() if t not in STOPWORDS and len(t) > 2}


def same_side(a: str, b: str) -> bool:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return False
    if ta == tb or ta & tb == ta or ta & tb == tb:
        return True
    return len(ta & tb) / len(ta | tb) >= 0.6


def same_fixture(a: dict, b: dict) -> bool:
    if a["sport"] != b["sport"]:
        return False
    if a["start_utc"][:10] != b["start_utc"][:10]:
        return False
    return (same_side(a["home"], b["home"]) and same_side(a["away"], b["away"])) or (
        same_side(a["home"], b["away"]) and same_side(a["away"], b["home"])
    )


def coalesce(records: list[dict]) -> list[dict]:
    """Desks spell the same club differently ('Papua New Guinea Kumuls' vs 'Papua New
    Guinea', 'Helios Grizzlys Giesen' vs 'VC Giesen'). Collapse those into one fixture
    and record every alias so the rename is visible rather than silent."""
    merged: list[dict] = []
    for record in records:
        target = next((m for m in merged if same_fixture(m, record)), None)
        if target is None:
            record["aliases"] = [f"{record['home']} v {record['away']}"]
            merged.append(record)
            continue
        alias = f"{record['home']} v {record['away']}"
        if alias not in target["aliases"]:
            target["aliases"].append(alias)
        target["provenance"].extend(record["provenance"])
        target["markets"].extend(record["markets"])
        for url in record["official_sources"]:
            if url not in target["official_sources"]:
                target["official_sources"].append(url)
        for url in record["olbg_urls"]:
            if url not in target["olbg_urls"]:
                target["olbg_urls"].append(url)
        for name, value in record["facts"].items():
            target["facts"].setdefault(name, value)
        for name, value in record["declared"].items():
            target["declared"].setdefault(name, value)
        for item in record["flags"]:
            if item not in target["flags"]:
                target["flags"].append(item)
        if record.get("start_utc") and record["_start_src"] > target.get("_start_src", ""):
            target["start_utc"] = record["start_utc"]
            target["_start_src"] = record["_start_src"]
        if len(record["home"]) > len(target["home"]):
            target["home"] = record["home"]
        if len(record["away"]) > len(target["away"]):
            target["away"] = record["away"]
    return merged

def dedupe_markets(record: dict) -> None:
    """Collapse identical (market, selection) lines into one row with all observations."""
    grouped: dict[tuple[str, str], dict] = {}
    for market in record["markets"]:
        key = (norm(market["market"]), norm(market["selection"]))
        slot = grouped.get(key)
        if slot is None:
            slot = {"observations": [], "market": market["market"], "selection": market["selection"]}
            grouped[key] = slot
        slot["observations"].append(market)
    lines = []
    for slot in grouped.values():
        observations = sorted(slot["observations"], key=lambda m: m["desk_captured_utc"], reverse=True)
        head = observations[0]
        decimals = sorted({round(o["decimal"], 3) for o in observations})
        lines.append(
            {
                "market": slot["market"],
                "selection": slot["selection"],
                "probability": head["probability"],
                "decimal": head["decimal"],
                "american": head["american"],
                "band": "in" if -250.0 - 1e-6 <= head["american"] <= 10000.0 + 1e-6 else "out",
                "source_desk": head["desk"],
                "desks": sorted({o["desk"] for o in observations}),
                "divergence": round(max(decimals) - min(decimals), 3) if len(decimals) > 1 else 0.0,
                "observations": [
                    {
                        "desk": o["desk"],
                        "decimal": o["decimal"],
                        "american": o["american"],
                        "probability": o["probability"],
                        "captured_utc": o["desk_captured_utc"],
                    }
                    for o in observations
                ],
            }
        )
    lines.sort(key=lambda line: -line["probability"])
    record["markets"] = lines


def favourite(record: dict):
    """Highest estimated win probability among win-market lines, for cross-desk comparison."""
    wins = [
        line
        for line in record["markets"]
        if re.search(r"winner", line["market"], re.I)
        and not re.search(r"1st|set|frame|leg|first", line["market"], re.I)
    ]
    if not wins:
        return None
    top = max(wins, key=lambda line: line["probability"])
    return {"selection": top["selection"], "probability": top["probability"], "desk": top["source_desk"]}


def main() -> None:
    events = coalesce(merge([read_8a(), read_496e(), read_653()]))
    now = "2026-10-23T21:30:00Z"
    slate = []
    for index, record in enumerate(events, start=1):
        record.pop("_start_src", None)
        dedupe_markets(record)
        record["id"] = f"6B{SPORTS.index((record['sport'], SLUG_OF[record['sport'].lower()])) + 1:02d}-{index:03d}"
        record["sport_slug"] = SLUG_OF[record["sport"].lower()]
        record["state"] = (
            "upcoming"
            if record["start_utc"] and record["start_utc"] > now
            else "elapsed"
            if record["start_utc"]
            else "time not stated"
        )
        record["favourite"] = favourite(record)
        record["official_sources"] = list(dict.fromkeys(record["official_sources"]))
        slate.append(record)
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "desk": "6b47ea39",
        "task": "T6B47",
        "built_utc": now,
        "policy": {
            "high_band": "estimated implied probability > 0.70 AND fair American price within -250..+10000",
            "band_ceiling_note": (
                "A -250 price is decimal 1.40, i.e. an implied probability of 71.43%. "
                "Any selection that is both above 70% and inside the requested window must therefore "
                "sit between 70.00% and 71.43%. See internal_analysis in audit.json."
            ),
            "no_inference": "blank beats invented; unconfirmed values are omitted and flagged",
        },
        "inherited_from": {
            "8a900c04": "2026-10-23T16:45:00Z",
            "496eaf02": "2026-10-23T20:30:00Z",
            "65331685": "2026-10-23T20:40:00Z",
        },
        "sports": [{"name": name, "slug": slug} for name, slug in SPORTS],
        "events": slate,
    }
    (OUT / "slate.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"slate: {len(slate)} events across {len({e['sport'] for e in slate})} sports")
    for name, _slug in SPORTS:
        rows = [e for e in slate if e["sport"] == name]
        upcoming = [e for e in rows if e["state"] == "upcoming"]
        print(f"  {name:14s} {len(rows):3d} events · {len(upcoming):3d} upcoming · {sum(len(e['markets']) for e in rows):4d} lines")


if __name__ == "__main__":
    main()
