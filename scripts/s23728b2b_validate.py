"""Validate desk 23728b2b data and rendered HTML; write a persistent audit record."""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from scripts.s23728b2b_data import FIXTURES, FLAGS, OBSERVED, PICKS, SOURCES, SPORTS
from scripts.s23728b2b_lib import assemble, confidence, display_american, fair_american, fair_decimal, in_high_price_window, rounded_american

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "23728b2b"
DATA = ROOT / "data" / "23728b2b"
WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)
BANNED_RE = re.compile(r"\b(?:model|verified)\b", re.I)


class AuditHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.tables = []
        self._table = None
        self._row = None
        self._header = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
            if self._row is not None:
                self._row["links"].append(attrs["href"])
        if tag == "table":
            self._table = {"headers": [], "rows": []}
        elif tag == "tr" and self._table is not None:
            self._row = {"links": [], "cells": 0, "header_cells": 0, "data_cells": 0}
        elif tag in {"th", "td"} and self._row is not None:
            self._row["cells"] += 1
            self._row["header_cells" if tag == "th" else "data_cells"] += 1
            self._text = []
            self._header = tag == "th"

    def handle_data(self, data):
        if self._row is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag in {"th", "td"} and self._row is not None:
            if self._header:
                self._table["headers"].append("".join(self._text).strip())
            self._text = []
            self._header = None
        elif tag == "tr" and self._row is not None:
            if self._row["data_cells"]:
                self._table["rows"].append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            self.tables.append(self._table)
            self._table = None


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def normalized_shingles(text: str, size=6) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(tokens[i:i + size]) for i in range(max(0, len(tokens) - size + 1))}


def validate_sources(desk: dict) -> str:
    assert len(SPORTS) == 15 and len(set(SPORTS)) == 15
    assert [name for _, name in SPORTS] == ["Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts", "Baseball", "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing", "Handball", "Ice Hockey", "Basketball", "Rugby League"]
    source_ids = [s["id"] for s in SOURCES]
    assert len(source_ids) == len(set(source_ids)), "duplicate source IDs"
    assert sum(not s["official"] for s in SOURCES) == 15
    for src in SOURCES:
        assert src["url"].startswith("https://"), src["id"]
        assert src["observed_at"] == OBSERVED
    cut = datetime.fromisoformat(OBSERVED.replace("Z", "+00:00"))
    flag_ids = {flag["id"] for flag in FLAGS}
    assert len(flag_ids) == len(FLAGS)
    for fixture in FIXTURES:
        assert fixture["sport"] in dict(SPORTS)
        for sid in [fixture["source"], *fixture["extra_sources"]]:
            assert sid in desk["source_by_id"], (fixture["id"], sid)
            assert desk["source_by_id"][sid]["official"], (fixture["id"], "non-official sporting source", sid)
        assert fixture["facts"], fixture["id"]
        if fixture["start_utc"]:
            start = datetime.fromisoformat(fixture["start_utc"].replace("Z", "+00:00"))
            assert start > cut, (fixture["id"], "not upcoming at snapshot")
        else:
            assert "start_utc" in fixture["missing_fields"], fixture["id"]
            assert fixture["start_label"], fixture["id"]
            assert fixture["flag_ids"], (fixture["id"], "unflagged blank start")
        for fid in fixture["flag_ids"]:
            assert fid in flag_ids, (fixture["id"], fid)
        for field in fixture["missing_fields"]:
            assert fixture["flag_ids"], (fixture["id"], field, "missing field without flag")
    for flag in FLAGS:
        assert flag["source"] in desk["source_by_id"], flag["id"]
        assert all(flag.get(key) for key in ["issue", "impact", "action", "area", "severity"])
    return f"15 sports; {len(SOURCES)} sources; {len(FIXTURES)} official-source rows; all starts upcoming at cut-off or explicitly blank/flagged"


def validate_lines(desk: dict) -> str:
    fixture_ids = {f["id"] for f in FIXTURES}
    primary = [line for line in desk["lines"] if line["role"] == "primary"]
    alternative = [line for line in desk["lines"] if line["role"] == "alternative"]
    assert len(primary) == len(PICKS) == 53
    assert len(alternative) == 85
    assert len({line["id"] for line in desk["lines"]}) == len(desk["lines"])
    assert len({line["fixture"] for line in primary}) == len(primary)
    for line in desk["lines"]:
        assert line["fixture"] in fixture_ids
        fixture = desk["fixture_by_id"][line["fixture"]]
        assert fixture["scope"] == "OLBG-listed", (line["id"], "context row has a price")
        assert "official_pairing" not in fixture["missing_fields"], (line["id"], "unconfirmed pairing has a price")
        p = line["probability"]
        assert isinstance(p, (int, float)) and 0 < p < 1
        assert math.isclose(line["fair_decimal"], fair_decimal(p), abs_tol=5.1e-7), line["id"]
        assert line["fair_american"] == rounded_american(p), line["id"]
        assert line["fair_american_display"] == display_american(p), line["id"]
        assert line["confidence"] == confidence(p), line["id"]
        if line["confidence"] == "High":
            assert p > .70 and in_high_price_window(p), line["id"]
            sides = fixture["side_evidence"]
            assert sides.get("a") and sides.get("b"), (line["id"], "High lacks both-side evidence")
    priced = {line["fixture"] for line in primary}
    for fixture in FIXTURES:
        if fixture["scope"] != "OLBG-listed" or "official_pairing" in fixture["missing_fields"]:
            assert fixture["id"] not in priced
    return f"{len(primary)} primary + {len(alternative)} alternative lines; reciprocal decimal/American arithmetic and every confidence label pass"


def validate_predictions(desk: dict) -> str:
    predictions = desk["predictions"]
    assert len(predictions) == len(PICKS)
    normalized = set()
    shingles = {}
    high_count = 0
    for prediction in predictions:
        text = prediction["text"]
        count = len(words(text))
        assert count >= 30, (prediction["fixture"], count)
        assert not BANNED_RE.search(text), prediction["fixture"]
        norm = re.sub(r"\s+", " ", text.strip().lower())
        assert norm not in normalized, (prediction["fixture"], "duplicate prediction")
        normalized.add(norm)
        for shingle in normalized_shingles(text):
            assert shingle not in shingles, (prediction["fixture"], "repeated six-word phrase", shingle, shingles.get(shingle))
            shingles[shingle] = prediction["fixture"]
        assert prediction["sources"], prediction["fixture"]
        for sid in prediction["sources"]:
            assert desk["source_by_id"][sid]["official"]
        line = next(line for line in desk["lines"] if line["id"] == prediction["line_id"])
        if line["selection"].lower() not in {"over", "under"}:
            selection_tokens = {token.lower() for token in re.findall(r"[A-Za-zÀ-ž]{4,}", line["selection"])}
            prediction_tokens = {token.lower() for token in re.findall(r"[A-Za-zÀ-ž]{4,}", text)}
            assert selection_tokens & prediction_tokens, (prediction["fixture"], "selection not explicit in prose")
        if prediction["confidence"] == "High":
            high_count += 1
            assert count >= 30
    assert high_count == 7
    return f"{len(predictions)} unique predictions, all at least 30 words; {high_count} High analyses pass evidence, vocabulary and six-word-phrase checks"


def parse_html(path: Path) -> AuditHTMLParser:
    parser = AuditHTMLParser()
    parser.feed(path.read_text())
    return parser


def validate_html(desk: dict) -> str:
    expected = [SITE / name for name in ["index.html", "matches.html", "sources.html", "methodology.html", "flagged.html", "repository-audit.html", "style.css", "app.js"]]
    expected += [SITE / "sports" / f"{slug}.html" for slug, _ in SPORTS]
    for path in expected:
        assert path.is_file() and path.stat().st_size > 0, path
    official_urls = {s["url"] for s in SOURCES if s["official"]}
    parsed = {}
    table_count = 0
    row_count = 0
    for path in [p for p in expected if p.suffix == ".html"]:
        parser = parse_html(path)
        parsed[path] = parser
        assert len(parser.ids) == len(set(parser.ids)), (path, "duplicate HTML IDs")
        for href in parser.links:
            if href.startswith(("https://", "http://", "mailto:")):
                continue
            if href.startswith("#"):
                assert unquote(href[1:]) in parser.ids, (path, "missing same-page anchor", href)
                continue
            split = urlsplit(href)
            target = (path.parent / unquote(split.path)).resolve()
            assert target.is_file(), (path, "broken internal link", href, target)
            if split.fragment and target.suffix == ".html":
                target_parser = parsed.get(target) or parse_html(target)
                assert unquote(split.fragment) in target_parser.ids, (path, "broken target anchor", href)
        for table in parser.tables:
            table_count += 1
            assert any("Official review" in header for header in table["headers"]), (path, "table lacks official-source column", table["headers"])
            for row in table["rows"]:
                row_count += 1
                assert any(urlsplit(link).scheme == "https" and link in official_urls for link in row["links"]), (path, "table row lacks official review link")
    # Every fixture has a sport-page article and pick/context anchor.
    for fixture in FIXTURES:
        sport_path = SITE / "sports" / f"{fixture['sport']}.html"
        parser = parsed[sport_path]
        assert fixture["id"] in parser.ids
        assert f"pick-{fixture['id']}" in parser.ids
        assert fixture["source"] in desk["source_by_id"]
        assert desk["source_by_id"][fixture["source"]]["url"] in parser.links
    # Executive High cards point directly to the relevant pick anchor.
    index = parsed[SITE / "index.html"]
    for line in desk["lines"]:
        if line["role"] == "primary" and line["confidence"] == "High":
            fixture = desk["fixture_by_id"][line["fixture"]]
            expected_href = f"sports/{fixture['sport']}.html#pick-{fixture['id']}"
            assert expected_href in index.links, (line["id"], "missing executive anchor")
    match_parser = parsed[SITE / "matches.html"]
    match_tables = [table for table in match_parser.tables if "Match / scope" in table["headers"]]
    assert len(match_tables) == 1 and len(match_tables[0]["rows"]) == len(FIXTURES)
    return f"21 HTML pages; {table_count} tables and {row_count} body rows all carry official links; internal files, anchors and all 55 match rows pass"


def validate_structured_files(desk: dict) -> str:
    required = ["desk.json", "sources.json", "fixtures.json", "lines.json", "predictions.json", "flags.json", "evidence.json", "summary.json", "methodology.json"]
    for name in required:
        path = DATA / name
        assert path.is_file(), path
        json.loads(path.read_text())
    saved = json.loads((DATA / "desk.json").read_text())
    for key in ["captured_at", "sports", "sources", "fixtures", "lines", "predictions", "flags", "summary"]:
        assert saved[key] == desk[key], f"desk.json mismatch: {key}"
    assert saved["summary"]["total_lines"] == 138
    assert saved["summary"]["high_picks"] == 7
    return "Nine structured JSON artifacts parse and desk.json exactly matches the source records"


def main() -> int:
    desk = assemble()
    checks = []
    failures = []
    for name, function in [
        ("Official evidence and scope", validate_sources),
        ("Independent line arithmetic", validate_lines),
        ("Prediction quality and High gate", validate_predictions),
        ("Rendered HTML and source links", validate_html),
        ("Structured artifacts", validate_structured_files),
    ]:
        try:
            detail = function(desk)
            checks.append({"name": name, "status": "PASS", "detail": detail})
            print(f"PASS {name}: {detail}")
        except Exception as exc:
            failures.append({"name": name, "error": str(exc)})
            print(f"FAIL {name}: {exc}", file=sys.stderr)
    record = {
        "desk": "23728b2b",
        "validated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
    }
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "validation.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    if failures:
        print(f"{len(failures)} validation groups failed", file=sys.stderr)
        return 1
    print(f"PASS all {len(checks)} validation groups; record: {DATA / 'validation.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
