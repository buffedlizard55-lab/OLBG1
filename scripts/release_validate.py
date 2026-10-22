#!/usr/bin/env python3
"""Strict structural/model/freshness gate. Does not certify remote facts or model accuracy."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from release_model import american, enrich, timestamp

ROOT = Path(__file__).resolve().parents[1]
SPORTS = {"tennis", "basketball", "golf", "cricket", "snooker", "rugby-union", "rugby-league", "baseball", "ice-hockey", "motor-racing", "darts", "handball", "volleyball", "aussie-rules", "esports", "gaelic-football", "greyhounds"}
OFFICIAL = {"api-web.nhle.com", "statsapi.mlb.com", "www.nba.com", "www.euroleaguebasketball.net", "ehfcl.eurohandball.com", "www.eurohandball.com", "www.protennislive.com", "wtafiles.wtatennis.com", "www.wst.tv", "www.unitedrugby.com", "top14.lnr.fr", "prod2.lnr.fr", "www.nrl.com", "scoring.nzc.nz", "www.legavolley.it", "www.plusliga.pl", "www.formula1.com", "www.pgatour.com", "www.afl.com.au", "www.pdc.tv", "lolesports.com", "gaacork.ie", "www.galwaygaa.ie", "www.gbgb.org.uk"}
SKIP = {".git", ".output", ".cache", "node_modules", ".venv", "__pycache__"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.rows = [], [], []
        self.in_body, self.row = 0, None
        self.lang = None
    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if tag == "html": self.lang = a.get("lang")
        if a.get("id"): self.ids.append(a["id"])
        if tag == "tbody": self.in_body += 1
        if tag == "tr" and self.in_body: self.row = []
        for attribute in ("href", "src"):
            if attribute in a:
                self.links.append(a[attribute] or "")
                if self.row is not None and tag == "a" and attribute == "href": self.row.append(a[attribute] or "")
    def handle_endtag(self, tag):
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row); self.row = None
        if tag == "tbody": self.in_body -= 1


def official(url):
    p = urlsplit(url)
    return p.scheme == "https" and p.hostname in OFFICIAL


def html_files():
    for base, directories, files in os.walk(ROOT):
        directories[:] = [d for d in directories if d not in SKIP]
        for filename in files:
            if filename.endswith(".html"): yield Path(base) / filename


def validate():
    errors = []
    data = json.loads((ROOT / "data/release/evidence.json").read_text())
    bundle = json.loads((ROOT / "data/release/bundle.json").read_text())
    manifest = json.loads((ROOT / "data/release/build.json").read_text())
    sources = {s["id"]: s for s in data["sources"]}
    require = lambda condition, message: errors.append(message) if not condition else None
    require(len(sources) == len(data["sources"]), "Duplicate evidence source IDs")
    require({c["sport"] for c in data["coverage"]} == SPORTS, "Coverage categories differ from exactly 17 allowed sports")
    require(len(data["coverage"]) == 17, "Coverage must have one row per eligible sport")
    for c in data["coverage"]:
        require(not c["exhaustive"], f"{c['sport']}: unproven exhaustive-coverage claim")
        require(c["official_source"] in sources and official(sources[c["official_source"]]["url"]), f"{c['sport']}: no official review destination")
    for source in sources.values():
        if source["kind"] == "official": require(official(source["url"]), "Unrecognized official host: " + source["url"])
        else: require(urlsplit(source["url"]).hostname == "www.olbg.com", "Non-OLBG discovery source")
        if source.get("retrieved_at_utc"):
            require(timestamp(source["retrieved_at_utc"]) <= timestamp(bundle["as_of_utc"]), f"{source['id']}: exact observation is after build cutoff")
        require(source["read_on"] <= bundle["as_of_utc"][:10], f"{source['id']}: source read date is in the future")
    require(len({r["id"] for r in data["fixtures"]}) == len(data["fixtures"]), "Duplicate fixture IDs")
    require({r["id"] for r in data["fixtures"]} == {r["id"] for r in bundle["fixtures"]}, "Compiled and input fixture IDs differ")
    current = {r["id"]: r for r in data["fixtures"]}
    for row in bundle["fixtures"]:
        fid = row["id"]
        require(row["sport"] in SPORTS, fid + ": excluded/unknown sport")
        require(bool(row["participant_a"]), fid + ": missing observed event/participant")
        require(bool(row["fixture_evidence"]), fid + ": no fixture evidence")
        for sid in row["fixture_evidence"]:
            require(sid in sources and sources[sid]["kind"] == "official" and sources[sid]["status"] != "blocked", fid + ": fixture evidence is blocked/discovery-only")
            require(fid in sources[sid].get("extracted_fixture_ids", []), fid + ": no source-specific extracted fixture ID")
        if row["start_utc"]:
            require("start_utc" in row["field_sources"], fid + ": inferred UTC without exact field evidence")
            try: timestamp(row["start_utc"])
            except (TypeError, ValueError): errors.append(fid + ": invalid timezone-aware start")
        require(row["approved_pick"] is None, fid + ": unapproved release must not invent an approved selection")
        require(row["confidence"] in (None, "Low", "Medium"), fid + ": High disabled until calibration and quote evidence")
        require(bool(row["high_gate_rejections"]), fid + ": approval blockers missing")
        regenerated = enrich(current[fid], sources, timestamp(bundle["as_of_utc"]), data["coverage_window"])
        require(row == regenerated, fid + ": compiled facts/model do not reproduce exactly")
        if row["markets"]:
            require(all(current[fid]["inputs"].get(side) for side in ("a", "b")), fid + ": priced without both observed sides")
        for market in row["markets"]:
            outcomes = market["outcomes"]
            require(abs(sum(o["probability"] for o in outcomes) - 1) < 1e-9, fid + ": market outcomes do not complement to one")
            for o in outcomes:
                p = o["probability"]
                require(math.isfinite(p) and 0 < p < 1, fid + ": invalid probability")
                require(abs(o["fair_decimal"] * p - 1) < 1e-10, fid + ": incorrect fair decimal")
                require(abs(o["fair_american"] - american(p)) < 1e-8, fid + ": incorrect fair US odds")
                require(o["bookmaker_american"] is None and o["expected_value"] is None, fid + ": unsupported bookmaker quote or EV")
                require(o["high_eligible"] is False, fid + ": uncalibrated High eligibility")
    for relative, digest in manifest["input_sha256"].items():
        require(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, relative + ": build input fingerprint changed")
    require(bundle["counts"]["approved_bets"] == bundle["counts"]["high"] == 0, "Approved / High count must stay zero")
    require(bundle["counts"]["fixtures"] == len(bundle["fixtures"]), "Displayed fixture count drift")
    require(bundle["counts"]["model_outcomes"] == sum(len(m["outcomes"]) for r in bundle["fixtures"] for m in r["markets"]), "Displayed model-price count drift")
    seen = set()
    for fid, note in bundle["commentary"].items():
        require(fid in current, "Commentary for unknown fixture: " + fid)
        require(len(note["text"].split()) >= 30, "Research note too short: " + fid)
        require(note["text"] not in seen, "Duplicated commentary")
        seen.add(note["text"])
        require(all(s in sources and sources[s]["kind"] == "official" for s in note["evidence"]), "Commentary lacks official evidence: " + fid)
    with (ROOT / "data/release/rows.csv").open(newline="") as stream:
        export = list(csv.DictReader(stream))
    require(len(export) == len(current), "CSV fixture count mismatch")
    for row in export:
        require(not row["approved_selection"], row["id"] + ": CSV approved selection not blank")
        if row["status"] != "scheduled":
            require(not row["projected_winner"] and not row["fair_american"], row["id"] + ": stale/unknown-time CSV live projection")
    canonical = set(manifest["pages"])
    parsers = {}
    for path in html_files():
        parser = Page(); parser.feed(path.read_text()); parsers[path.resolve()] = parser
    for path, parser in parsers.items():
        relative = path.relative_to(ROOT).as_posix()
        primary = relative in canonical
        if primary:
            require(parser.lang == "en", relative + ": missing page language")
            require(len(parser.ids) == len(set(parser.ids)), relative + ": duplicate HTML IDs")
            for number, links in enumerate(parser.rows, 1):
                require(any(official(u) for u in links), f"{relative}: table row {number} lacks an official review link")
        for href in parser.links:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                if primary: require(parsed.scheme == "https", relative + ": unsafe/non-HTTPS URL " + href)
                continue
            if not parsed.path:
                if primary and parsed.fragment: require(unquote(parsed.fragment) in parser.ids, relative + ": missing local fragment " + href)
                continue
            clean = unquote(parsed.path)
            if clean.startswith("/OLBG1/"): target = ROOT / clean.removeprefix("/OLBG1/")
            elif clean.startswith("/"):
                errors.append(relative + ": root-relative path breaks project hosting: " + href); continue
            else: target = path.parent / clean
            target = target.resolve()
            if target.is_dir(): target /= "index.html"
            try: target.relative_to(ROOT)
            except ValueError:
                errors.append(relative + ": path escapes site: " + href); continue
            require(target.is_file(), relative + ": broken local link " + href)
            if primary and parsed.fragment and target in parsers:
                require(unquote(parsed.fragment) in parsers[target].ids, relative + ": broken cross-page fragment " + href)
    for relative in canonical: require((ROOT / relative).is_file(), "Missing canonical page: " + relative)
    if errors:
        print("RELEASE VALIDATION FAILED")
        for error in errors: print(" - " + error)
        return False
    print(f"RELEASE VALIDATION PASSED: {len(canonical)} canonical / {len(parsers)} total HTML pages; {len(current)} official-linked extracts; 0 approved bets; model complements, cutoff, source roles and local links checked. Not factual certification.")
    return True


if __name__ == "__main__":
    sys.exit(0 if validate() else 1)
