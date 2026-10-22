#!/usr/bin/env python3
"""Optional official-JSON refresh; failure never re-stamps or fabricates evidence.

Only NHL and MLB have structured collectors in this release. Other categories keep their
original observation dates and expire. The GitHub Actions artifact contains raw responses;
no workflow commits, branch writes, credentials or market-provider scraping are needed.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_HOSTS = {"api-web.nhle.com", "statsapi.mlb.com"}


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def get_json(url: str, raw_path: Path):
    if urlparse(url).hostname not in ALLOWED_HOSTS:
        raise ValueError("Collector URL is not an official allowlisted structured API")
    req = Request(url, headers={"User-Agent": "OLBG1-evidence-desk/1.0 (public research; source-linked)", "Accept": "application/json"})
    with urlopen(req, timeout=20) as response:
        body = response.read(4_000_001)
        if len(body) > 4_000_000:
            raise ValueError("Official response exceeds safe capture limit")
        payload = json.loads(body)
        retrieved = iso(datetime.now(timezone.utc))
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(body)
    return payload, retrieved


def official_source(sid, title, url, retrieved, raw_path):
    return {"id": sid, "name": title, "url": url, "kind": "official", "read_on": retrieved[:10],
            "retrieved_at_utc": retrieved, "status": "read", "scope": "Structured fields parsed from official API response",
            "chunks_read": None, "limitations": "No bookmaker settlement, calibrated accuracy or confirmed lineup certified by this capture.",
            "capture_kind": "raw official JSON + validated structured extraction", "raw_path": raw_path,
            "extracted_fixture_ids": []}


def base_fixture(fid, sport, comp, home, away, start, sid, state):
    # Validate the offset; dates and exact starts must be explicitly returned by the API.
    dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
    if dt.tzinfo is None or not home or not away or home == away:
        raise ValueError("Invalid official participants/start")
    start = iso(dt)
    return {"id": fid, "sport": sport, "competition": comp, "participant_a": home, "participant_b": away,
            "participant_order": "home-away", "event_date": start[:10], "start_utc": start,
            "printed_time": None, "fixture_evidence": [sid],
            "field_sources": {"participants": [sid], "event_date": [sid], "start_utc": [sid]},
            "inputs": {}, "form": [], "notes": "Automatically read official schedule; no executable recommendation.",
            "bookmaker_quote": None, "verified_available_markets": [], "head_to_head": None,
            "lineups_confirmed": False, "official_state": state}


def localized(value):
    return value.get("default", "") if isinstance(value, dict) else str(value or "")


def nhl_rows(payload, sid):
    games = payload.get("games")
    if not isinstance(games, list):
        raise ValueError("Missing official NHL games array")
    rows = []
    for game in games:
        state = game.get("gameState")
        if state not in ("FUT", "PRE") or game.get("gameScheduleState") not in ("OK", None):
            continue
        teams = [game["homeTeam"], game["awayTeam"]]
        names = []
        records = []
        for team in teams:
            name = localized(team.get("placeName")) + " " + localized(team.get("commonName"))
            if not name.strip():
                raise ValueError("No NHL team name")
            names.append(name.strip())
            record = team.get("record", "")
            if not re.fullmatch(r"\d+-\d+-\d+", record):
                records.append(None)
            else:
                w, l, ot = map(int, record.split("-"))
                records.append({"wins": w, "losses": l, "ot_losses": ot, "games": w + l + ot, "evidence": [sid]})
        row = base_fixture("nhl-" + str(game["id"]), "ice-hockey", "NHL", *names, game["startTimeUTC"], sid, state)
        if all(r and r["games"] > 0 for r in records):
            row["inputs"] = {"a": records[0], "b": records[1], "model": "smoothed-log5-record"}
            row["form"] = [f"{n}: {r['wins']}-{r['losses']}-{r['ot_losses']} W-L-OT in {r['games']} games."
                           for n, r in zip(names, records)]
        row["notes"] += " Win records only; no goalie, shot-quality or goal-rate inputs. Provider quotes deliberately not interpreted as matching markets."
        rows.append(row)
    return rows


def mlb_records(payload, sid):
    records = {}
    for group in payload.get("records", []):
        for record in group.get("teamRecords", []):
            w, l = record.get("wins"), record.get("losses")
            if not isinstance(w, int) or not isinstance(l, int) or min(w, l) < 0 or w + l <= 0:
                continue
            records[record["team"]["id"]] = {"wins": w, "losses": l, "games": w + l,
                "runs_for": record.get("runsScored"), "runs_against": record.get("runsAllowed"), "evidence": [sid]}
    if not records:
        raise ValueError("No usable regular-season MLB records")
    return records


def mlb_rows(payload, sid, records):
    if not isinstance(payload.get("dates"), list):
        raise ValueError("Missing official MLB dates array")
    rows = []
    for day in payload["dates"]:
        for game in day.get("games", []):
            if game.get("status", {}).get("abstractGameState") != "Preview" or game["status"].get("startTimeTBD"):
                continue
            if game.get("ifNecessary") == "Y":
                continue  # conditional games stay out of a current firm fixture slate
            home, away = (game["teams"][s]["team"] for s in ("home", "away"))
            row = base_fixture("mlb-" + str(game["gamePk"]), "baseball", "MLB — " + game.get("description", game.get("seriesDescription", "Scheduled game")),
                               home["name"], away["name"], game["gameDate"], sid, "Preview")
            if home["id"] in records and away["id"] in records:
                row["inputs"] = {"a": copy.deepcopy(records[home["id"]]), "b": copy.deepcopy(records[away["id"]]),
                                 "model": "smoothed-log5-record"}
                row["form"] = [f"{team['name']}: {records[team['id']]['wins']}-{records[team['id']]['losses']} regular-season record."
                               for team in (home, away)]
            row["notes"] += " Regular-season record baseline, not postseason form. Starting pitchers unavailable; no run line or total asserted."
            rows.append(row)
    return rows


def refresh(path: Path, today=None):
    data = json.loads(path.read_text())
    current = datetime.now(timezone.utc)
    today = today or current.date()
    end = today + timedelta(days=7)
    sources = {s["id"]: s for s in data["sources"]}
    fixtures = {r["id"]: r for r in data["fixtures"]}
    attempts = []
    raw_dir = path.parent / "raw"

    def attempt(label, url, parser):
        sid = label if re.search(r"\d{4}-\d{2}-\d{2}$", label) else label + "-" + today.isoformat()
        raw_path = raw_dir / (sid + ".json")
        try:
            payload, retrieved = get_json(url, raw_path)
            parsed = parser(payload, sid)
            sources[sid] = official_source(sid, label.replace("-", " ").upper(), url, retrieved,
                                            str(raw_path.relative_to(ROOT)))
            if isinstance(parsed, list):
                for row in parsed:
                    fixtures[row["id"]] = row
                sources[sid]["extracted_fixture_ids"] = [r["id"] for r in parsed]
            attempts.append({"source": sid, "url": url, "status": "success", "retrieved_at_utc": retrieved,
                             "fixture_count": len(parsed) if isinstance(parsed, list) else None})
            return parsed
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError, OSError) as exc:
            attempts.append({"source": sid, "url": url, "status": "failed", "attempted_at_utc": iso(datetime.now(timezone.utc)),
                             "error": str(exc)[:400], "policy": "Old observation dates unchanged; no replacement facts generated."})
            return None

    for offset in range(7):
        day = today + timedelta(days=offset)
        attempt("nhl-score-" + day.isoformat(), "https://api-web.nhle.com/v1/score/" + day.isoformat(), nhl_rows)
    standings_url = "https://statsapi.mlb.com/api/v1/standings?" + urlencode({"leagueId": "103,104", "season": today.year,
        "standingsTypes": "regularSeason", "fields": "records,teamRecords,team,id,name,wins,losses,runsScored,runsAllowed"})
    records = attempt("mlb-regular-standings", standings_url, mlb_records) or {}
    schedule_url = "https://statsapi.mlb.com/api/v1/schedule?" + urlencode({"sportId": 1, "startDate": today.isoformat(),
        "endDate": (end - timedelta(days=1)).isoformat(), "hydrate": "team,venue"})
    attempt("mlb-schedule", schedule_url, lambda p, sid: mlb_rows(p, sid, records))
    data["sources"] = list(sources.values())
    data["fixtures"] = sorted(fixtures.values(), key=lambda r: (r["event_date"], r.get("start_utc") or "~", r["id"]))
    data["coverage_window"] = {"from_utc": today.isoformat() + "T00:00:00Z", "to_utc_exclusive": end.isoformat() + "T00:00:00Z"}
    data["last_automatic_collection"] = {"attempted_at_utc": iso(current), "scope": "NHL and MLB only; never an all-sport recertification",
                                         "attempts": attempts}
    # Do not alter manual read_on, captured_at_utc or any other category's original evidence date.
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    successes = sum(a["status"] == "success" for a in attempts)
    print(f"Official collection: {successes}/{len(attempts)} successful; failures disclosed, not fabricated.")
    return attempts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=ROOT / "data/release/evidence.json")
    args = parser.parse_args()
    refresh(args.evidence)
