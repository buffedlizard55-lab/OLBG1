#!/usr/bin/env python3
"""Independent, structural audit of the latest merged OLBG snapshot.

This audit is intentionally offline: it reads committed JSON/HTML and runs the
repository's local validators, but does not fetch OLBG or any governing-body page.
It must not be used as evidence that a remote source was freshly checked. The
row-level outcomes in data/verification.json belong to the separate T34
official-source re-verification pass and are reported as recorded, not re-certified here.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shlex
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = ROOT / "reports" / "SESSION_5A353E83_INDEPENDENT_AUDIT.md"
REPORT_HTML = ROOT / "reports" / "SESSION_5A353E83_INDEPENDENT_AUDIT.html"

# Use the same *host policy* as the primary structural validator. This recognizes
# source hosts; it does not prove that the linked page currently contains a claim.
sys.path.insert(0, str(ROOT))
from scripts.validate import OFFICIAL_FIXTURE_HOSTS  # noqa: E402
from scripts.c17a9192_validate import OFFICIAL_HOST_ALLOWLIST as C17_OFFICIAL_HOSTS  # noqa: E402

# Additional official authorities used by the 984d417f namespace, not already
# recognized by the root/c17 policies. These include signed ATP/WTA draw hosts,
# EuroLeague's calendar PDF host, and the official WNBA club site. OLBG itself is
# kept separate as an upstream discovery source, not a governing-body source.
S984_ADDITIONAL_OFFICIAL_HOSTS = {
    "ftpserver.euroleague.net",
    "valkyries.wnba.com",
    "wtafiles.wtatennis.com",
    "www.protennislive.com",
}
S984_OFFICIAL_HOSTS = OFFICIAL_FIXTURE_HOSTS | C17_OFFICIAL_HOSTS | S984_ADDITIONAL_OFFICIAL_HOSTS
S984_UPSTREAM_ONLY_HOSTS = {"www.olbg.com"}


class TableScan(HTMLParser):
    """Capture links and visible text for rows inside HTML <tbody> sections."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tbody_depth = 0
        self.in_row = False
        self.row_links: list[str] = []
        self.row_text: list[str] = []
        self.heading_text = ""
        self.pending_heading: list[str] = []
        self.in_heading = False
        self.rows: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        if tag in {"h1", "h2", "h3", "h4"}:
            self.in_heading = True
            self.pending_heading = []
        if tag == "tbody":
            self.tbody_depth += 1
        elif tag == "tr" and self.tbody_depth:
            self.in_row = True
            self.row_links = []
            self.row_text = []
        if tag == "a" and attrs_d.get("href") and self.in_row:
            self.row_links.append(str(attrs_d["href"]))

    def handle_data(self, data: str) -> None:
        if self.in_heading:
            self.pending_heading.append(data)
        if self.in_row:
            self.row_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4"} and self.in_heading:
            self.heading_text = " ".join(" ".join(self.pending_heading).split())
            self.in_heading = False
        elif tag == "tr" and self.in_row:
            self.rows.append(
                {
                    "heading": self.heading_text,
                    "text": " ".join(" ".join(self.row_text).split()),
                    "links": list(self.row_links),
                }
            )
            self.in_row = False
        elif tag == "tbody" and self.tbody_depth:
            self.tbody_depth -= 1


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def host_is_official(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in OFFICIAL_FIXTURE_HOSTS


def is_https(url: str) -> bool:
    return url.startswith("https://")


def nested_values(obj: object, key: str) -> list[object]:
    """Find values named by a field-level uncertainty marker in nested JSON."""
    found: list[object] = []
    if isinstance(obj, dict):
        for current_key, value in obj.items():
            if current_key == key:
                found.append(value)
            found.extend(nested_values(value, key))
    elif isinstance(obj, list):
        for value in obj:
            found.extend(nested_values(value, key))
    return found


def host_is_s984_official(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in S984_OFFICIAL_HOSTS


def load_table_rows(path: Path) -> list[dict[str, object]]:
    parser = TableScan()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.rows


def run_gate(command: list[str]) -> dict[str, object]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {"command": " ".join(command), "returncode": result.returncode, "output": result.stdout.strip()}


def word_count(text: str) -> int:
    return len(text.split())


def audit_s984_data() -> dict[str, object]:
    """Reconcile the separate 984d417f machine-readable snapshot offline."""
    errors: list[str] = []
    warnings: list[str] = []
    fixtures_doc = read_json("data/984d417f/fixtures.json")
    lines_doc = read_json("data/984d417f/lines.json")
    predictions_doc = read_json("data/984d417f/predictions.json")
    flagged_doc = read_json("data/984d417f/flagged.json")
    sources_doc = read_json("data/984d417f/sources.json")
    taxonomy_doc = read_json("data/984d417f/olbg_taxonomy.json")
    markets_doc = read_json("data/984d417f/markets_catalog.json")
    repo_audit_doc = read_json("data/984d417f/repo_audit.json")
    report_text = (ROOT / "reports" / "SESSION_984D417F_AUDIT.md").read_text(encoding="utf-8")

    fixtures = fixtures_doc.get("fixtures", [])
    lines = lines_doc.get("lines", [])
    predictions = predictions_doc.get("predictions", [])
    flagged_rows = flagged_doc.get("rows", [])
    source_records = sources_doc.get("sources", [])
    repo_findings = repo_audit_doc.get("repo_findings", [])
    upstream_defects = repo_audit_doc.get("upstream_olbg_defects", [])

    fixture_ids = [str(row.get("id", "")) for row in fixtures]
    line_ids = [str(row.get("id", "")) for row in lines]
    prediction_ids = [str(row.get("id", "")) for row in predictions]
    if len(fixtures) != 145 or len(set(fixture_ids)) != len(fixture_ids) or "" in fixture_ids:
        errors.append(f"984d417f fixture IDs/count invalid: {len(fixtures)} rows, {len(set(fixture_ids))} unique")
    if fixtures_doc.get("count") != len(fixtures):
        errors.append("984d417f fixtures count metadata does not match rows")
    if len(lines) != len(fixtures) or len(set(line_ids)) != len(line_ids) or set(line_ids) != set(fixture_ids):
        errors.append("984d417f line records do not map one-to-one to the 145 fixture IDs")
    if lines_doc.get("count") != len(lines):
        errors.append("984d417f lines count metadata does not match rows")
    if predictions_doc.get("count") != len(predictions) or len(set(prediction_ids)) != len(prediction_ids):
        errors.append("984d417f prediction IDs/count invalid")
    high_ids = {
        str(row.get("id", ""))
        for row in lines
        if str(row.get("pick", {}).get("confidence", "")).lower() == "high"
    }
    if set(prediction_ids) != high_ids:
        errors.append("984d417f prediction IDs do not exactly match high-confidence line IDs")

    status_counts = Counter(str(row.get("status", "missing")) for row in fixtures)
    confidence_counts = Counter(str(row.get("pick", {}).get("confidence", "missing")).lower() for row in lines)
    kind_counts = Counter(str(row.get("kind", "missing")) for row in fixtures)
    sport_counts = Counter(str(row.get("sport", "missing")) for row in fixtures)
    taxonomy_sports = {str(row.get("page_slug")) for row in taxonomy_doc.get("sports", []) if row.get("in_scope")}
    if set(sport_counts) != taxonomy_sports:
        errors.append("984d417f fixture sports do not match the in-scope OLBG taxonomy")
    if set(markets_doc.get("sports_markets", {})) != set(sport_counts):
        errors.append("984d417f market catalog sports do not match the fixture sports")
    declared_by_sport = fixtures_doc.get("by_sport", {})
    if declared_by_sport != dict(sorted(sport_counts.items())):
        errors.append("984d417f fixtures by_sport metadata does not match actual rows")
    declared_confidence = {str(key).lower(): int(value) for key, value in lines_doc.get("confidence_counts", {}).items()}
    if declared_confidence != dict(sorted(confidence_counts.items())):
        errors.append("984d417f confidence_counts metadata does not match line picks")

    source_errors: list[str] = []
    source_hosts: set[str] = set()
    event_source_links = 0
    official_source_links = 0
    olbg_source_links = 0
    for fixture in fixtures:
        sources = fixture.get("sources", [])
        if not sources:
            source_errors.append(f"{fixture.get('id')}: no sources")
        official_for_fixture = 0
        for source in sources:
            url = str(source.get("url", ""))
            host = urlparse(url).hostname or ""
            event_source_links += 1
            if host:
                source_hosts.add(host)
            if host in S984_UPSTREAM_ONLY_HOSTS:
                olbg_source_links += 1
                continue
            if not host_is_s984_official(url):
                source_errors.append(f"{fixture.get('id')}: {url}")
            else:
                official_source_links += 1
                official_for_fixture += 1
        if official_for_fixture == 0:
            source_errors.append(f"{fixture.get('id')}: no recognized governing-body source")
    if source_errors:
        errors.append(f"984d417f fixture source host/scheme failures: {source_errors[:8]}")

    registry_ids = [str(row.get("id", "")) for row in source_records]
    if sources_doc.get("count") != len(source_records) or len(set(registry_ids)) != len(registry_ids):
        errors.append("984d417f source registry count/IDs invalid")
    registry_source_errors = []
    for source in source_records:
        url = str(source.get("url", ""))
        if urlparse(url).hostname in S984_UPSTREAM_ONLY_HOSTS:
            continue
        if not host_is_s984_official(url):
            registry_source_errors.append(url)
    if registry_source_errors:
        errors.append(f"984d417f source registry contains non-allowlisted authorities: {registry_source_errors[:8]}")

    # Field-level markers are checked recursively in both the fixture and its line.
    # Absence/null/empty string/list/object count as blank; non-empty values are flagged.
    line_by_id = {str(row.get("id", "")): row for row in lines}
    unverified_field_counts = Counter(
        str(field) for fixture in fixtures for field in fixture.get("unverified_fields", [])
    )
    unverified_rows = sum(bool(fixture.get("unverified_fields")) for fixture in fixtures)
    nonblank_unverified: list[dict[str, str]] = []
    for fixture in fixtures:
        event_id = str(fixture.get("id", ""))
        for field in fixture.get("unverified_fields", []):
            values = nested_values(fixture, str(field)) + nested_values(line_by_id.get(event_id, {}), str(field))
            if any(value not in (None, "", [], {}) for value in values):
                nonblank_unverified.append({"id": event_id, "field": str(field)})
    if nonblank_unverified:
        errors.append(f"984d417f unverified_fields markers have populated values: {nonblank_unverified[:8]}")

    flagged_ids = [str(row.get("id", "")) for row in flagged_rows]
    if flagged_doc.get("count") != len(flagged_rows) or len(set(flagged_ids)) != len(flagged_ids):
        errors.append("984d417f flagged.json count/IDs invalid")
    if not set(flagged_ids).issubset(set(fixture_ids)):
        errors.append("984d417f flagged.json contains IDs absent from fixtures.json")
    repo_summary = repo_audit_doc.get("summary", {})
    if repo_summary.get("repo_audit_findings") != len(repo_findings):
        errors.append("984d417f repo_audit summary does not match repo_findings")
    if repo_summary.get("upstream_olbg_defects") != len(upstream_defects):
        errors.append("984d417f repo_audit summary does not match upstream OLBG defects")
    if repo_summary.get("flagged_or_blank_field_rows") != len(flagged_rows):
        errors.append("984d417f repo_audit flagged_or_blank_field_rows does not match flagged.json")
    if repo_summary.get("cross_checked_rows") != status_counts.get("cross-checked", 0):
        errors.append("984d417f repo_audit cross_checked_rows does not match fixture status labels")
    if repo_summary.get("rows_with_blank_unverified_fields") != unverified_rows:
        errors.append("984d417f repo_audit blank-unverified row count does not match fixtures")

    claimed_blank_match = re.search(r"\*\*(\d+)\*\* unconfirmed fields explicitly left blank", report_text)
    claimed_blank_fields = int(claimed_blank_match.group(1)) if claimed_blank_match else None
    explicit_field_entries = sum(unverified_field_counts.values())
    if claimed_blank_fields is not None and claimed_blank_fields != explicit_field_entries:
        warnings.append(
            f"The 984d417f audit report claims {claimed_blank_fields} unconfirmed fields explicitly blank, but fixtures.json lists {explicit_field_entries} unverified_fields entries across {unverified_rows} rows; all named fields are absent/empty in the fixture/line JSON. Reconcile the metric definition before repeating the headline count."
        )

    with (ROOT / "data" / "984d417f" / "matches.csv").open(encoding="utf-8", newline="") as csv_file:
        csv_rows = list(csv.DictReader(csv_file))
    if len(csv_rows) != len(fixtures) or {str(row.get("id", "")) for row in csv_rows} != set(fixture_ids):
        errors.append("984d417f matches.csv IDs do not match fixtures.json")
    csv_source_errors = [
        str(row.get("id", ""))
        for row in csv_rows
        if not host_is_s984_official(str(row.get("official_source_url", "")))
    ]
    if csv_source_errors:
        errors.append(f"984d417f matches.csv has non-allowlisted official_source_url values: {csv_source_errors[:8]}")

    return {
        "errors": errors,
        "warnings": warnings,
        "event_count": len(fixtures),
        "line_count": len(lines),
        "prediction_count": len(predictions),
        "status_counts": dict(sorted(status_counts.items())),
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "kind_counts": dict(sorted(kind_counts.items())),
        "sport_count": len(sport_counts),
        "source_record_count": len(source_records),
        "event_source_links": event_source_links,
        "official_source_links": official_source_links,
        "olbg_source_links": olbg_source_links,
        "official_source_host_count": len(source_hosts - S984_UPSTREAM_ONLY_HOSTS),
        "flagged_row_count": len(flagged_rows),
        "unverified_rows": unverified_rows,
        "unverified_field_entries": explicit_field_entries,
        "claimed_unverified_field_count": claimed_blank_fields,
        "nonblank_unverified_fields": nonblank_unverified,
        "source_hosts": sorted(source_hosts),
        "market_sport_count": len(markets_doc.get("sports_markets", {})),
    }


def audit_snapshot(args: argparse.Namespace) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    s984_metrics = audit_s984_data()
    errors.extend(s984_metrics["errors"])
    warnings.extend(s984_metrics["warnings"])

    fixtures_doc = read_json("data/fixtures.json")
    lines_doc = read_json("data/lines.json")
    predictions_doc = read_json("data/predictions.json")
    verification_doc = read_json("data/verification.json")
    live_doc = read_json("data/live_snapshot.json")
    diff_doc = read_json("data/live_diff.json")
    flags_doc = read_json("datasets/flagged_for_review.json")
    coverage_doc = read_json("data/coverage.json")
    c17_matches = read_json("data/c17a9192/matches.json")
    c17_lines = read_json("data/c17a9192/lines.json")
    c17_predictions = read_json("data/c17a9192/predictions.json")
    c17_flagged_doc = read_json("data/c17a9192/flagged.json")
    c17_sources = read_json("data/c17a9192/sources.json")
    c17_taxonomy = read_json("data/c17a9192/olbg_taxonomy.json")
    c17_repo_audit = read_json("data/c17a9192/repo_audit.json")
    coordination_text = (ROOT / "COORDINATION.md").read_text(encoding="utf-8")

    fixtures = fixtures_doc.get("fixtures", [])
    lines = lines_doc.get("lines", [])
    predictions = predictions_doc.get("predictions", [])
    verification_rows = verification_doc.get("rows", [])

    c17_errors: list[str] = []
    c17_ids = [row.get("id") for row in c17_matches]
    c17_line_ids = [row.get("event_id") for row in c17_lines]
    c17_prediction_ids = [row.get("event_id") for row in c17_predictions]
    if len(c17_ids) != 217 or len(c17_ids) != len(set(c17_ids)):
        c17_errors.append(f"c17a9192 matches should contain 217 unique IDs; found {len(c17_ids)}")
    if set(c17_line_ids) != set(c17_ids) or len(c17_line_ids) != len(set(c17_line_ids)):
        c17_errors.append("c17a9192 line IDs do not exactly match its 217 match IDs")
    c17_high_ids = {row.get("id") for row in c17_matches if row.get("confidence") == "high"}
    if set(c17_prediction_ids) != c17_high_ids or len(c17_prediction_ids) != len(set(c17_prediction_ids)):
        c17_errors.append("c17a9192 prediction IDs do not exactly match its high-confidence rows")
    c17_source_errors = []
    for match in c17_matches:
        match_sources = match.get("official_sources", [])
        if not match_sources:
            c17_source_errors.append(str(match.get("id")))
        for source in match_sources:
            url = str(source.get("url", ""))
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.hostname not in C17_OFFICIAL_HOSTS:
                c17_source_errors.append(f"{match.get('id')}: {url}")
    if c17_source_errors:
        c17_errors.append(f"c17a9192 source allowlist/scheme failures: {c17_source_errors[:8]}")
    c17_status_counts = Counter(str(row.get("verification_status")) for row in c17_matches)
    c17_kind_counts = Counter(str(row.get("kind")) for row in c17_matches)
    c17_confidence_counts = Counter(str(row.get("confidence")) for row in c17_matches)
    c17_blank_fields_by_status = {
        verdict: {
            field: sum(not bool(row.get(field)) for row in c17_matches if row.get("verification_status") == verdict)
            for field in ("start_utc", "venue", "stat_a", "stat_b")
        }
        for verdict in sorted(c17_status_counts)
    }
    c17_unverified_nonblank_fields = {
        field: sum(bool(row.get(field)) for row in c17_matches if row.get("verification_status") == "unverified")
        for field in ("start_utc", "venue", "stat_a", "stat_b")
    }
    c17_flag_summary = c17_flagged_doc.get("summary", {})
    if c17_flag_summary.get("unverified_events") != c17_status_counts.get("unverified", 0):
        c17_errors.append("c17a9192 flagged summary unverified_events does not match matches.json")
    if c17_flag_summary.get("prior_repo_audit_findings") != len(c17_repo_audit):
        c17_errors.append("c17a9192 flagged summary prior_repo_audit_findings does not match repo_audit.json")
    if c17_flag_summary.get("partial_blank_calendar_events") != c17_status_counts.get("tour_calendar_verified", 0):
        c17_errors.append("c17a9192 partial_blank_calendar_events does not match tour_calendar_verified rows")
    if c17_flag_summary.get("flagged_or_partial_total") != len(c17_flagged_doc.get("events_for_manual_review", [])):
        c17_errors.append("c17a9192 flagged_or_partial_total does not match events_for_manual_review")
    c17_taxonomy_sports = {str(row.get("name")) for row in c17_taxonomy if row.get("in_scope")}
    if {str(row.get("sport")) for row in c17_matches} != c17_taxonomy_sports:
        c17_errors.append("c17a9192 match sport set does not match the in-scope taxonomy")
    if any(row.get("confidence") == "high" and row.get("verification_status") != "verified" for row in c17_matches):
        c17_errors.append("c17a9192 contains a high-confidence event that is not fully verified")
    with (ROOT / "data" / "c17a9192" / "matches.csv").open(encoding="utf-8-sig", newline="") as c17_csv_file:
        c17_csv_rows = list(csv.DictReader(c17_csv_file))
    if len(c17_csv_rows) != len(c17_matches) or {row.get("id") for row in c17_csv_rows} != set(c17_ids):
        c17_errors.append("c17a9192 CSV export does not match its 217 match IDs")
    if any(not str(row.get("primary_official_source_url", "")).startswith("https://") for row in c17_csv_rows):
        c17_errors.append("c17a9192 CSV export contains a missing/non-HTTPS primary source URL")
    if c17_errors:
        errors.extend(c17_errors)

    c17_reported_market_counts = re.search(
        r"100% market coverage across all 217 events.*?`(\d+)` H2H.*?and `(\d+)` Multi-Runner",
        coordination_text,
        re.S,
    )
    c17_reported_h2h = int(c17_reported_market_counts.group(1)) if c17_reported_market_counts else None
    c17_reported_field = int(c17_reported_market_counts.group(2)) if c17_reported_market_counts else None
    c17_actual_h2h = sum(c17_kind_counts.get(kind, 0) for kind in ("h2h_2way", "h2h_3way"))
    c17_actual_field = sum(c17_kind_counts.get(kind, 0) for kind in ("outright", "race"))
    c17_market_claim_mismatch = (
        c17_reported_h2h is not None
        and (c17_reported_h2h != c17_actual_h2h or c17_reported_field != c17_actual_field)
    )
    if c17_market_claim_mismatch:
        warnings.append(
            f"PR #41/COORDINATION market-type headline says {c17_reported_h2h} H2H + {c17_reported_field} multi-runner, but data/c17a9192/matches.json contains {c17_actual_h2h} H2H ({c17_kind_counts.get('h2h_2way',0)} two-way + {c17_kind_counts.get('h2h_3way',0)} three-way) + {c17_actual_field} non-H2H ({c17_kind_counts.get('outright',0)} outright + {c17_kind_counts.get('race',0)} race) = {len(c17_matches)} total."
        )
    if c17_status_counts.get("unverified", 0) and any(c17_unverified_nonblank_fields.values()):
        warnings.append(
            "Some c17a9192 rows carry overall `unverified` status while field values remain populated: "
            + ", ".join(f"{field}={count}" for field, count in c17_unverified_nonblank_fields.items() if count)
            + ". Field-level evidence must be reviewed; retain only values supported by an official source and blank the rest."
        )
    if c17_taxonomy:
        c17_included_sports = {str(row.get("name")) for row in c17_taxonomy if row.get("in_scope")}
    else:
        c17_included_sports = set()

    fixture_ids = [row.get("id") for row in fixtures]
    line_ids = [row.get("id") for row in lines]
    prediction_ids = [row.get("match_id") for row in predictions]
    verification_ids = [row.get("id") for row in verification_rows]

    for label, ids in (
        ("fixture", fixture_ids),
        ("line", line_ids),
        ("prediction", prediction_ids),
        ("verification", verification_ids),
    ):
        if None in ids or len(ids) != len(set(ids)):
            errors.append(f"{label} IDs are missing or duplicated")

    fixture_by_id = {row["id"]: row for row in fixtures if row.get("id")}
    line_by_id = {row["id"]: row for row in lines if row.get("id")}
    prediction_by_id = {row["match_id"]: row for row in predictions if row.get("match_id")}
    verification_by_id = {row["id"]: row for row in verification_rows if row.get("id")}

    embedded_verdict_counts = Counter(
        str(row.get("verification", {}).get("verdict", "missing"))
        for row in fixtures
        if isinstance(row.get("verification"), dict)
    )
    verification_semantic_exceptions: list[dict[str, str]] = []
    verification_reconciliation_errors: list[str] = []
    expected_embedded_verdict = {
        "confirmed": "confirmed",
        "corrected": "corrected",
        "flagged": "conflict",
        "not_rechecked": "not-rechecked",
    }
    for fixture_id in set(fixture_by_id) & set(verification_by_id):
        fixture = fixture_by_id[fixture_id]
        ledger_row = verification_by_id[fixture_id]
        embedded = str(fixture.get("verification", {}).get("verdict", "missing"))
        ledger_status = str(ledger_row.get("status", "missing"))
        expected = expected_embedded_verdict.get(ledger_status)
        if (ledger_status, embedded, fixture.get("status")) == ("corrected", "unconfirmed", "unverified"):
            verification_semantic_exceptions.append({
                "id": fixture_id,
                "ledger_status": ledger_status,
                "embedded_verdict": embedded,
                "fixture_status": str(fixture.get("status")),
                "action": str(ledger_row.get("action", "")),
            })
        elif expected != embedded:
            verification_reconciliation_errors.append(
                f"{fixture_id}: separate ledger status {ledger_status!r} != expected embedded verdict {expected!r} (found {embedded!r})"
            )
    if verification_reconciliation_errors:
        errors.extend(verification_reconciliation_errors)

    if fixtures_doc.get("count") != len(fixtures):
        errors.append("data/fixtures.json count metadata does not match fixtures")
    if fixtures_doc.get("h2h_count") != sum(bool(row.get("away")) for row in fixtures):
        errors.append("data/fixtures.json H2H count does not match rows with an away side")
    if fixtures_doc.get("event_only_count") != sum(not bool(row.get("away")) for row in fixtures):
        errors.append("data/fixtures.json event-only count does not match rows without an away side")
    if lines_doc.get("count") != len(lines):
        errors.append("data/lines.json count metadata does not match lines")
    if predictions_doc.get("count") != len(predictions):
        errors.append("data/predictions.json count metadata does not match predictions")

    h2h_ids = {row["id"] for row in fixtures if row.get("id") and row.get("away")}
    high_ids = {row["id"] for row in lines if row.get("id") and row.get("confidence") == "high"}
    if set(line_by_id) != h2h_ids:
        errors.append("originated H2H line IDs do not exactly match H2H fixture IDs")
    if set(prediction_by_id) != high_ids:
        errors.append("high-confidence picks and prediction IDs do not exactly match")

    fixture_source_errors: list[str] = []
    for fixture in fixtures:
        sources = fixture.get("sources", [])
        if not sources:
            fixture_source_errors.append(str(fixture.get("id")))
            continue
        for source in sources:
            url = str(source.get("url", ""))
            if not host_is_official(url):
                fixture_source_errors.append(f"{fixture.get('id')}: {url}")
    if fixture_source_errors:
        errors.append(f"primary fixture source host/scheme failures: {fixture_source_errors[:8]}")

    prediction_lengths = [word_count(str(row.get("text", ""))) for row in predictions]
    if any(length < 30 for length in prediction_lengths):
        errors.append("one or more High-pick predictions are under 30 words")
    if any(not row.get("sources") for row in predictions):
        errors.append("one or more High-pick predictions have no source link")

    verification_status_counts = Counter(str(row.get("status")) for row in verification_rows)
    allowed_verification_statuses = {"confirmed", "corrected", "flagged", "not_rechecked"}
    if set(verification_status_counts) - allowed_verification_statuses:
        errors.append(f"unknown verification status(es): {sorted(set(verification_status_counts) - allowed_verification_statuses)}")
    if set(verification_by_id) != set(fixture_by_id):
        errors.append("verification ledger IDs do not exactly match primary fixture IDs")
    if verification_doc.get("summary", {}).get("rows") != len(verification_rows):
        errors.append("verification summary row count does not match ledger")
    for status in allowed_verification_statuses:
        expected = verification_doc.get("summary", {}).get(status)
        actual = verification_status_counts.get(status, 0)
        if expected != actual:
            errors.append(f"verification summary {status}={expected} but ledger has {actual}")
    verification_source_errors: list[str] = []
    verification_rows_missing_evidence: list[str] = []
    for row in verification_rows:
        if not host_is_official(str(row.get("source_url", ""))):
            verification_source_errors.append(str(row.get("id")))
        if not all(str(row.get(key, "")).strip() for key in ("source_name", "source_url", "evidence", "action", "checked_at")):
            verification_rows_missing_evidence.append(str(row.get("id")))
    if verification_source_errors:
        errors.append(f"verification ledger has missing/non-allowlisted source URLs: {verification_source_errors[:8]}")
    if verification_rows_missing_evidence:
        errors.append(f"verification ledger rows missing evidence fields: {verification_rows_missing_evidence[:8]}")

    def parse_utc(value: object) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None

    generated_at = parse_utc(verification_doc.get("generated"))
    embedded_checked_after_generation: list[dict[str, str]] = []
    unverified_source_crossrefs: list[dict[str, object]] = []
    for fixture in fixtures:
        f_id = str(fixture.get("id", ""))
        vblock = fixture.get("verification", {})
        checked_at = parse_utc(vblock.get("checked_utc")) if isinstance(vblock, dict) else None
        if generated_at and checked_at and checked_at > generated_at:
            embedded_checked_after_generation.append({
                "id": f_id,
                "checked_utc": str(vblock.get("checked_utc")),
                "generated": str(verification_doc.get("generated", "")),
            })
        ledger_row = verification_by_id.get(f_id, {})
        if fixture.get("status") == "unverified" and ledger_row:
            fixture_urls = {str(src.get("url", "")) for src in fixture.get("sources", [])}
            evidence_url = str(ledger_row.get("source_url", ""))
            if evidence_url and evidence_url not in fixture_urls:
                unverified_source_crossrefs.append({
                    "id": f_id,
                    "ledger_status": str(ledger_row.get("status", "")),
                    "source_name": str(ledger_row.get("source_name", "")),
                    "ledger_source_url": evidence_url,
                    "fixture_source_urls": sorted(fixture_urls),
                    "evidence": str(ledger_row.get("evidence", "")),
                })

    t34_run_match = re.search(
        r"## 27\. Session `b95dbd01-olbg1`[\s\S]*?\*\*Run:\*\*\s*([^\s]+)",
        coordination_text,
    )
    t34_run_claimed = t34_run_match.group(1).rstrip(".") if t34_run_match else "not found"
    t34_run_at = parse_utc(t34_run_claimed)
    timestamp_anomalies: list[str] = []
    if embedded_checked_after_generation:
        after_rows = sorted(embedded_checked_after_generation, key=lambda row: row["id"])
        sample_ids = ", ".join(row["id"] for row in after_rows[:5])
        timestamp_anomalies.append(
            f"{len(after_rows)} embedded fixture verification blocks have checked_utc later than data/verification.json generated {verification_doc.get('generated')} (sample IDs: {sample_ids})"
        )
    if t34_run_at and generated_at and t34_run_at > generated_at:
        timestamp_anomalies.append(
            f"COORDINATION.md §27 reports T34 run at {t34_run_claimed}, later than verification.json generated {verification_doc.get('generated')}"
        )
    pr39_merged_at = parse_utc(args.pr39_merged_at)
    if t34_run_at and pr39_merged_at and t34_run_at > pr39_merged_at:
        timestamp_anomalies.append(
            f"COORDINATION.md §27 T34 run time {t34_run_claimed} postdates PR #39 merge {args.pr39_merged_at}"
        )
    if timestamp_anomalies:
        warnings.append("Verification chronology is inconsistent: " + "; ".join(timestamp_anomalies))
    if verification_semantic_exceptions:
        warnings.append(
            "One documented status downgrade is counted as `corrected` in the verification action ledger, `unconfirmed` in the embedded row verdict, and `unverified` in the fixture status: "
            + ", ".join(row["id"] for row in verification_semantic_exceptions)
            + ". This is an action/status taxonomy distinction, not a confirmed match claim."
        )
    if unverified_source_crossrefs:
        warnings.append(
            "An unverified fixture's per-row verification source URL is not present in that fixture's source list; inspect the cited official source/evidence pairing: "
            + ", ".join(row["id"] for row in unverified_source_crossrefs)
            + "."
        )

    fixture_status_counts = Counter(str(row.get("status")) for row in fixtures)
    line_confidence_counts = Counter(str(row.get("confidence")) for row in lines)
    sport_counts = Counter(str(row.get("sport")) for row in fixtures)

    live_events = live_doc.get("events", [])
    live_summary = diff_doc.get("summary", {})
    live_metrics = {
        "events": len(live_events),
        "sports_with_tips": len(live_doc.get("sports_captured", [])),
        "sports_without_tips": len(live_doc.get("sports_with_no_live_tips", [])),
        "joined": live_summary.get("matched"),
        "changed": live_summary.get("consensus_or_selection_changed"),
        "selection_flips": live_summary.get("selection_flipped"),
        "new_unverified": len(diff_doc.get("new_not_in_dataset", [])),
        "absent_from_first_screen": len(diff_doc.get("dataset_rows_absent_from_capture", [])),
    }
    if live_summary.get("live_events_captured") != len(live_events):
        errors.append("live_diff summary event count does not match live_snapshot")
    if live_summary.get("dataset_rows") != len(fixtures):
        errors.append("live_diff dataset row count does not match primary fixtures")
    if live_summary.get("new_not_in_dataset") != live_metrics["new_unverified"]:
        errors.append("live_diff new/unverified count metadata does not match rows")
    if live_summary.get("dataset_rows_absent_from_capture") != live_metrics["absent_from_first_screen"]:
        errors.append("live_diff absent-from-first-screen count metadata does not match rows")

    flag_summary = flags_doc.get("summary", {})
    if flag_summary.get("upstream_and_audit_findings") != len(flags_doc.get("findings", [])):
        errors.append("flagged registry finding count does not match records")
    if flag_summary.get("flagged_fixture_rows") != len(flags_doc.get("rows", [])):
        errors.append("flagged registry row count does not match records")

    # Byte parity checks for the primary JSON mirror and complete export.
    mirror_checks: dict[str, bool] = {}
    for filename in ("fixtures.json", "lines.json", "predictions.json", "verification.json"):
        primary = ROOT / "data" / filename
        mirror = ROOT / "f7fa77fc" / "data" / filename
        same = primary.is_file() and mirror.is_file() and sha256(primary) == sha256(mirror)
        mirror_checks[filename] = same
        if not same:
            errors.append(f"root/mirror data drift or missing file: {filename}")

    full_doc = read_json("datasets/matches_full.json")
    full_ids = {row.get("id") for row in full_doc.get("matches", [])}
    if full_doc.get("count") != len(full_doc.get("matches", [])) or full_ids != set(fixture_by_id):
        errors.append("datasets/matches_full.json does not match the 134-row primary fixture set")
    with (ROOT / "datasets" / "matches_full.csv").open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != len(fixtures) or {row.get("id") for row in csv_rows} != set(fixture_by_id):
        errors.append("datasets/matches_full.csv does not match the primary fixture set")

    # Structural table-row scan across every published workspace. Rows in the root
    # picks and sport pages are match-data views; other rows can be summaries,
    # methodology, or preserved companion desks and are not silently reclassified.
    html_pages = sorted(path for path in ROOT.rglob("*.html") if ".git" not in path.parts)
    rows_by_page: dict[str, list[dict[str, object]]] = {}
    missing_https_by_page: Counter[str] = Counter()
    for page in html_pages:
        rel = page.relative_to(ROOT).as_posix()
        rows = load_table_rows(page)
        rows_by_page[rel] = rows
        for row in rows:
            links = row.get("links", [])
            if not any(is_https(str(url)) for url in links):
                missing_https_by_page[rel] += 1

    c17_html_pages = sorted(path for path in (ROOT / "c17a9192").rglob("*.html"))
    c17_rows = [row for page in c17_html_pages for row in rows_by_page.get(page.relative_to(ROOT).as_posix(), [])]
    c17_rows_with_https = sum(any(is_https(str(url)) for url in row.get("links", [])) for row in c17_rows)
    c17_rows_with_official = sum(
        any(
            is_https(str(url)) and urlparse(str(url)).hostname in C17_OFFICIAL_HOSTS
            for url in row.get("links", [])
        )
        for row in c17_rows
    )
    c17_html_metrics = {
        "page_count": len(c17_html_pages),
        "tbody_rows": len(c17_rows),
        "rows_with_https": c17_rows_with_https,
        "rows_with_official_source": c17_rows_with_official,
    }
    if c17_html_metrics["page_count"] != 24:
        errors.append(f"c17a9192 dashboard expected 24 HTML pages; found {c17_html_metrics['page_count']}")
    if c17_html_metrics["rows_with_https"] != c17_html_metrics["tbody_rows"]:
        errors.append("one or more c17a9192 table rows lack an HTTPS link")
    c17_missing_official_by_page = {
        page.relative_to(ROOT).as_posix(): sum(
            not any(
                is_https(str(url)) and urlparse(str(url)).hostname in C17_OFFICIAL_HOSTS
                for url in row.get("links", [])
            )
            for row in rows_by_page.get(page.relative_to(ROOT).as_posix(), [])
        )
        for page in c17_html_pages
        if any(
            not any(
                is_https(str(url)) and urlparse(str(url)).hostname in C17_OFFICIAL_HOSTS
                for url in row.get("links", [])
            )
            for row in rows_by_page.get(page.relative_to(ROOT).as_posix(), [])
        )
    }
    if c17_html_metrics["rows_with_official_source"] != c17_html_metrics["tbody_rows"]:
        warnings.append(
            f"{c17_html_metrics['tbody_rows'] - c17_html_metrics['rows_with_official_source']} c17a9192 table rows have HTTPS links but no host in its governing-body allowlist: {c17_missing_official_by_page}. These are largely OLBG taxonomy/defect rows and repository-audit rows, not all fixture rows; custom HTML validation checks HTTPS presence, not allowlist membership per row."
        )

    s984_html_pages = sorted(path for path in (ROOT / "984d417f").rglob("*.html"))
    s984_rows = [row for page in s984_html_pages for row in rows_by_page.get(page.relative_to(ROOT).as_posix(), [])]
    s984_rows_with_https = sum(any(is_https(str(url)) for url in row.get("links", [])) for row in s984_rows)
    s984_rows_with_official = sum(
        any(is_https(str(url)) and urlparse(str(url)).hostname in S984_OFFICIAL_HOSTS for url in row.get("links", []))
        for row in s984_rows
    )
    s984_missing_https_by_page = {
        page.relative_to(ROOT).as_posix(): sum(
            not any(is_https(str(url)) for url in row.get("links", []))
            for row in rows_by_page.get(page.relative_to(ROOT).as_posix(), [])
        )
        for page in s984_html_pages
        if any(
            not any(is_https(str(url)) for url in row.get("links", []))
            for row in rows_by_page.get(page.relative_to(ROOT).as_posix(), [])
        )
    }
    s984_missing_official_by_page = {
        page.relative_to(ROOT).as_posix(): sum(
            not any(is_https(str(url)) and urlparse(str(url)).hostname in S984_OFFICIAL_HOSTS for url in row.get("links", []))
            for row in rows_by_page.get(page.relative_to(ROOT).as_posix(), [])
        )
        for page in s984_html_pages
        if any(
            not any(is_https(str(url)) and urlparse(str(url)).hostname in S984_OFFICIAL_HOSTS for url in row.get("links", []))
            for row in rows_by_page.get(page.relative_to(ROOT).as_posix(), [])
        )
    }
    s984_fixture_table_pages = [
        ROOT / "984d417f" / "index.html",
        *sorted((ROOT / "984d417f" / "sports").glob("*.html")),
    ]
    s984_fixture_table_rows = [
        row
        for page in s984_fixture_table_pages
        for row in rows_by_page.get(page.relative_to(ROOT).as_posix(), [])
    ]
    s984_fixture_rows_with_official = sum(
        any(is_https(str(url)) and urlparse(str(url)).hostname in S984_OFFICIAL_HOSTS for url in row.get("links", []))
        for row in s984_fixture_table_rows
    )
    s984_html_metrics = {
        "page_count": len(s984_html_pages),
        "tbody_rows": len(s984_rows),
        "rows_with_https": s984_rows_with_https,
        "rows_with_official_source": s984_rows_with_official,
        "rows_missing_https_by_page": s984_missing_https_by_page,
        "rows_missing_official_by_page": s984_missing_official_by_page,
        "fixture_table_rows": len(s984_fixture_table_rows),
        "fixture_rows_with_official_source": s984_fixture_rows_with_official,
    }
    if s984_html_metrics["page_count"] != 23:
        errors.append(f"984d417f dashboard expected 23 HTML pages; found {s984_html_metrics['page_count']}")
    if s984_html_metrics["fixture_rows_with_official_source"] != s984_html_metrics["fixture_table_rows"]:
        errors.append("one or more 984d417f index/sport fixture-table rows lack a recognized governing-body source link")
    if s984_html_metrics["rows_missing_https_by_page"]:
        warnings.append(
            f"984d417f has {sum(s984_html_metrics['rows_missing_https_by_page'].values())} table rows without HTTPS, concentrated in {s984_html_metrics['rows_missing_https_by_page']}; these are in the cross-desk repository-audit table, not event rows."
        )
    if s984_html_metrics["rows_with_official_source"] != s984_html_metrics["tbody_rows"]:
        warnings.append(
            f"{s984_html_metrics['tbody_rows'] - s984_html_metrics['rows_with_official_source']} 984d417f table rows have HTTPS but no recognized governing-body host: {s984_missing_official_by_page}. Most are OLBG taxonomy/market descriptions, repository audit, or upstream-defect records rather than event rows."
        )

    primary_data_pages = ["picks.html", *[p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "sports").glob("*.html"))]]
    mirror_data_pages = ["f7fa77fc/picks.html", *[p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "f7fa77fc" / "sports").glob("*.html"))]]
    primary_data_link_counts: dict[str, dict[str, int]] = {}
    for rel in primary_data_pages + mirror_data_pages:
        rows = rows_by_page.get(rel, [])
        with_official = sum(
            any(host_is_official(str(url)) for url in row.get("links", []))
            for row in rows
        )
        primary_data_link_counts[rel] = {"rows": len(rows), "official_link_rows": with_official}
        if len(rows) and with_official != len(rows):
            errors.append(f"primary match table {rel} has rows without a recognized official source link")

    def rows_for_heading(page: str, fragment: str) -> list[dict[str, object]]:
        return [row for row in rows_by_page.get(page, []) if fragment in str(row.get("heading", ""))]

    refresh_capture_rows = rows_for_heading("live-refresh.html", "Full Live Capture")
    refresh_change_rows = rows_for_heading("live-refresh.html", "Consensus / Selection Changes")
    refresh_absent_rows = rows_for_heading("live-refresh.html", "Dataset Rows Not Present")
    def official_link_count(rows: list[dict[str, object]]) -> int:
        return sum(any(host_is_official(str(url)) for url in row.get("links", [])) for row in rows)

    def olbg_only_count(rows: list[dict[str, object]]) -> int:
        return sum(
            any(urlparse(str(url)).hostname == "www.olbg.com" for url in row.get("links", []))
            and not any(host_is_official(str(url)) for url in row.get("links", []))
            for row in rows
        )

    refresh_table_metrics = {
        "capture_rows": len(refresh_capture_rows),
        "capture_official_source_rows": official_link_count(refresh_capture_rows),
        "capture_olbg_only_rows": olbg_only_count(refresh_capture_rows),
        "change_rows": len(refresh_change_rows),
        "change_official_source_rows": official_link_count(refresh_change_rows),
        "change_olbg_only_rows": olbg_only_count(refresh_change_rows),
        "absent_rows": len(refresh_absent_rows),
        "absent_official_source_rows": official_link_count(refresh_absent_rows),
        "absent_olbg_only_rows": olbg_only_count(refresh_absent_rows),
        "all_event_rows": len(refresh_capture_rows) + len(refresh_change_rows) + len(refresh_absent_rows),
        "all_event_rows_official": official_link_count(refresh_capture_rows + refresh_change_rows + refresh_absent_rows),
        "all_event_rows_olbg_only": olbg_only_count(refresh_capture_rows + refresh_change_rows + refresh_absent_rows),
    }
    if refresh_table_metrics["capture_rows"] != len(live_events):
        errors.append("Live Refresh Full Capture table does not match live_snapshot event count")
    if refresh_table_metrics["capture_official_source_rows"] != live_metrics["joined"]:
        warnings.append("Live Refresh official-source links on the capture table differ from the joined-event count")
    if refresh_table_metrics["capture_olbg_only_rows"] != live_metrics["new_unverified"]:
        warnings.append("OLBG-only live-capture rows differ from the explicitly unverified diff count")

    verification_summary_rows = rows_for_heading("live-verification.html", "Coverage by sport")
    verification_finding_rows = rows_for_heading("live-verification.html", "Findings from this pass")
    verification_detail_rows = rows_for_heading("live-verification.html", "Row-by-row register")
    verification_table_metrics = {
        "sport_summary_rows": len(verification_summary_rows),
        "sport_summary_without_https": sum(not any(is_https(str(url)) for url in r.get("links", [])) for r in verification_summary_rows),
        "findings_rows": len(verification_finding_rows),
        "detail_rows": len(verification_detail_rows),
        "detail_rows_with_official_source": sum(any(host_is_official(str(url)) for url in r.get("links", [])) for r in verification_detail_rows),
    }
    if verification_table_metrics["detail_rows"] != len(verification_rows):
        warnings.append("Live Verification detail table row count differs from data/verification.json")

    # Scope note is an unresolved interpretation: the user's words can be read as
    # excluding every football code, while the existing taxonomy includes these.
    borderline_slugs = {"aussie-rules", "gaelic-football"}
    borderline_counts = {slug: sport_counts.get(slug, 0) for slug in sorted(borderline_slugs) if sport_counts.get(slug, 0)}

    all_tbody_rows = sum(len(rows) for rows in rows_by_page.values())
    all_rows_missing_https = sum(missing_https_by_page.values())
    gap_list = sorted(missing_https_by_page.items(), key=lambda item: (-item[1], item[0]))
    published_html_page_count = len(html_pages) + (0 if REPORT_HTML.exists() else 1)

    if verification_status_counts.get("not_rechecked", 0):
        warnings.append(f"The saved official-source ledger explicitly marks {verification_status_counts['not_rechecked']} of {len(fixtures)} fixture rows not_rechecked.")
    if live_metrics["new_unverified"]:
        warnings.append(f"The live OLBG capture has {live_metrics['new_unverified']} upstream-only cards without a primary verified fixture row.")
    if refresh_table_metrics["all_event_rows_olbg_only"]:
        warnings.append(f"Across the Live Refresh event tables, {refresh_table_metrics['all_event_rows_olbg_only']} rows cite OLBG but have no recognized governing-body source link.")
    if live_metrics["absent_from_first_screen"]:
        warnings.append(f"{live_metrics['absent_from_first_screen']} primary fixture rows are absent from the recaptured first screen; the source report notes hub truncation, so absence is not cancellation evidence.")
    if all_rows_missing_https:
        warnings.append(f"The whole-tree source-link scan found {all_rows_missing_https} <tbody> rows with no HTTPS link across {all_tbody_rows} rows.")
    if verification_table_metrics["sport_summary_without_https"]:
        warnings.append(f"The Live Verification page's {verification_table_metrics['sport_summary_without_https']} per-sport aggregate rows have no row-level HTTPS link.")
    if borderline_counts:
        warnings.append(f"Scope is unresolved for football-coded sports included under the current taxonomy: {borderline_counts}.")
    validator_source = (ROOT / "scripts" / "validate.py").read_text(encoding="utf-8")
    validator_reads_ledger = "verification.json" in validator_source
    validator_checks_embedded_verification = 'fixture.get("verification")' in validator_source
    validator_accepts_not_rechecked = "not-rechecked" in validator_source
    if not validator_reads_ledger:
        if validator_checks_embedded_verification and validator_accepts_not_rechecked:
            warnings.append("scripts/validate.py checks each fixture's embedded verification block, but does not load the separate data/verification.json register and explicitly allows `not-rechecked`; a passing gate confirms provenance shape, not fresh page reads.")
        else:
            warnings.append("scripts/validate.py does not inspect the separate data/verification.json register; a passing structural gate does not by itself enforce fresh per-row verification coverage.")

    coordination_pending_tasks: dict[str, str] = {}
    for task in ("T9", "T10", "T11", "T12", "T19"):
        match = re.search(rf"^\|\s*{task}\s*\|[^|]*\|\s*([^|]+)\|", coordination_text, re.M)
        if match and match.group(1).strip() in {"in progress", "queued"}:
            coordination_pending_tasks[task] = match.group(1).strip()
    if coordination_pending_tasks:
        pr_note = f" PR #{args.pr40_number} is {args.pr40_state} and proposes coordination updates to T9–T12." if args.pr40_number != "not supplied" else ""
        warnings.append("At the audited snapshot, the task board still records " + ", ".join(f"{task} `{state}`" for task, state in coordination_pending_tasks.items()) + "." + pr_note + " T40 does not change those task rows.")
    if "T35" in coordination_text and "| T35 |" in coordination_text and "| queued |" in next((line for line in coordination_text.splitlines() if line.startswith("| T35 |")), ""):
        warnings.append("Root-scope T35 remains queued for nine AFLW lines and three picks; PR #41 and PR #42 contain separately namespaced AFLW re-prices, but neither updates root data/lines.json or data/predictions.json.")

    return {
        "errors": errors,
        "warnings": warnings,
        "c17_event_count": len(c17_matches),
        "c17_olbg_listed_count": sum(bool(row.get("olbg", {}).get("listed")) for row in c17_matches),
        "c17_sport_counts": dict(sorted(Counter(str(row.get("sport")) for row in c17_matches).items())),
        "c17_status_counts": dict(sorted(c17_status_counts.items())),
        "c17_kind_counts": dict(sorted(c17_kind_counts.items())),
        "c17_actual_h2h_count": c17_actual_h2h,
        "c17_actual_field_count": c17_actual_field,
        "c17_reported_h2h_count": c17_reported_h2h,
        "c17_reported_field_count": c17_reported_field,
        "c17_confidence_counts": dict(sorted(c17_confidence_counts.items())),
        "c17_prediction_count": len(c17_predictions),
        "c17_official_source_records": len(c17_sources),
        "c17_event_source_links": sum(len(row.get("official_sources", [])) for row in c17_matches),
        "c17_repo_audit_findings": len(c17_repo_audit),
        "c17_olbg_irregularities": len(c17_flagged_doc.get("olbg_irregularities", [])),
        "c17_flagged_or_partial_events": c17_flag_summary.get("flagged_or_partial_total"),
        "c17_manual_review_events": len(c17_flagged_doc.get("events_for_manual_review", [])),
        "c17_blank_fields_by_status": c17_blank_fields_by_status,
        "c17_unverified_nonblank_fields": c17_unverified_nonblank_fields,
        "c17_included_sports": sorted(c17_included_sports),
        "c17_html_metrics": c17_html_metrics,
        "c17_rows_missing_official_by_page": c17_missing_official_by_page,
        "s984_metrics": s984_metrics,
        "s984_html_metrics": s984_html_metrics,
        "verification_embedded_checked_after_generation_count": len(embedded_checked_after_generation),
        "fixture_count": len(fixtures),
        "h2h_count": len(h2h_ids),
        "event_only_count": len(fixtures) - len(h2h_ids),
        "fixture_status_counts": dict(sorted(fixture_status_counts.items())),
        "line_count": len(lines),
        "line_confidence_counts": dict(sorted(line_confidence_counts.items())),
        "prediction_count": len(predictions),
        "prediction_word_min": min(prediction_lengths, default=0),
        "prediction_word_max": max(prediction_lengths, default=0),
        "verification_generated": verification_doc.get("generated", ""),
        "verification_status_counts": dict(sorted(verification_status_counts.items())),
        "embedded_verification_verdict_counts": dict(sorted(embedded_verdict_counts.items())),
        "verification_semantic_exceptions": verification_semantic_exceptions,
        "verification_timestamp_anomalies": timestamp_anomalies,
        "unverified_source_crossrefs": unverified_source_crossrefs,
        "t34_run_claimed": t34_run_claimed,
        "verification_fresh_read_count": sum(verification_status_counts.get(key, 0) for key in ("confirmed", "corrected", "flagged")),
        "verification_sources": len(verification_doc.get("sources", {})),
        "verification_by_sport_count": len(verification_doc.get("by_sport", {})),
        "validator_reads_verification_ledger": validator_reads_ledger,
        "validator_checks_embedded_verification": validator_checks_embedded_verification,
        "validator_accepts_not_rechecked": validator_accepts_not_rechecked,
        "coordination_pending_tasks": coordination_pending_tasks,
        "live_captured_utc": live_doc.get("fetched_utc", ""),
        "live_sport_count": len(live_doc.get("hub_urls", {})),
        "live_metrics": live_metrics,
        "live_table_metrics": refresh_table_metrics,
        "verification_table_metrics": verification_table_metrics,
        "flagged_findings": len(flags_doc.get("findings", [])),
        "flagged_rows": len(flags_doc.get("rows", [])),
        "missing_utc_flagged_rows": flag_summary.get("missing_utc_rows"),
        "sports_count": len(coverage_doc.get("included", [])),
        "borderline_sports": borderline_counts,
        "primary_data_link_counts": primary_data_link_counts,
        "mirror_checks": mirror_checks,
        "html_page_count": published_html_page_count,
        "all_tbody_rows": all_tbody_rows,
        "all_rows_missing_https": all_rows_missing_https,
        "rows_missing_https_by_page": gap_list,
        "fixture_source_host_count": len(
            {
                urlparse(str(source.get("url", ""))).hostname
                for fixture in fixtures
                for source in fixture.get("sources", [])
                if source.get("url")
            }
        ),
        "fixture_source_urls": sum(len(fixture.get("sources", [])) for fixture in fixtures),
        "html_page_count_expected_after_audit_page": len(html_pages) + (0 if REPORT_HTML.exists() else 1),
    }


def md_bullets(mapping: dict[str, int]) -> str:
    if not mapping:
        return "- None."
    return "\n".join(f"- `{key}` — {value} row(s)." for key, value in mapping.items())


def gate_text(gates: list[dict[str, object]]) -> str:
    if not gates:
        return "Not run."
    return "\n\n".join(
        f"`{gate['command']}` — exit {gate['returncode']}\n\n```text\n{gate['output']}\n```"
        for gate in gates
    )


def render_markdown(a: dict[str, object], args: argparse.Namespace, gates: list[dict[str, object]]) -> str:
    status = a["verification_status_counts"]
    live = a["live_metrics"]
    live_table = a["live_table_metrics"]
    ver_table = a["verification_table_metrics"]
    fixture_status = a["fixture_status_counts"]
    confidence = a["line_confidence_counts"]
    confidence_text = ", ".join(f"{key.title()} {value}" for key,value in sorted(confidence.items()))
    c17_status = a["c17_status_counts"]
    c17_kind = a["c17_kind_counts"]
    c17_blanks = a["c17_blank_fields_by_status"]
    s984 = a["s984_metrics"]
    s984_status = s984["status_counts"]
    s984_confidence = s984["confidence_counts"]
    s984_kind = s984["kind_counts"]
    s984_html = a["s984_html_metrics"]
    s984_official_gap = ", ".join(
        f"`{page}` {count}" for page, count in s984_html["rows_missing_official_by_page"].items()
    ) or "none"
    s984_https_gap = ", ".join(
        f"`{page}` {count}" for page, count in s984_html["rows_missing_https_by_page"].items()
    ) or "none"
    c17_blank_bullets = "\n".join(
        f"- `{tier}` ({c17_status.get(tier,0)} rows): blank `start_utc` {fields['start_utc']}, `venue` {fields['venue']}, `stat_a` {fields['stat_a']}, `stat_b` {fields['stat_b']}."
        for tier, fields in c17_blanks.items()
    )
    warnings = a["warnings"]
    errors = a["errors"]
    gap_lines = "\n".join(
        f"- [`{page}`](../{page}) — {count} row(s) with no HTTPS link in a `<tbody>` table."
        for page, count in a["rows_missing_https_by_page"]
    ) or "- None."
    c17_official_gap = ", ".join(
        f"`{page}` {count}" for page, count in a["c17_rows_missing_official_by_page"].items()
    ) or "none"
    border_labels = {"aussie-rules": "Aussie Rules", "gaelic-football": "Gaelic Football"}
    border = ", ".join(f"{border_labels.get(slug, slug)} ({count})" for slug, count in a["borderline_sports"].items()) or "none"
    page_info = (
        f"Pages API: `{args.pages_api_status}`; workflow run [`{args.pages_run_id}`]"
        f"({args.pages_run_status}) — [{args.pages_run_url}]({args.pages_run_url}); "
        f"main SHA `{args.pages_main_sha}`; observed `{args.pages_checked_at}` UTC."
        if args.pages_run_id != "not supplied"
        else "Pages deployment metadata was not supplied to this offline report."
    )
    pr40_info = (
        f"PR [#{args.pr40_number}]({args.pr40_url}) was `{args.pr40_state}` when checked at `{args.pr40_checked_at}` UTC."
        if args.pr40_number != "not supplied"
        else f"PR #40 state was `{args.pr40_state}` at `{args.pr40_checked_at}` UTC."
    )
    pr41_info = (
        f"PR [#41]({args.pr41_url}) merged at `{args.pr41_merged_at}`; its separate dashboard lives at [`/c17a9192/`](../c17a9192/index.html)."
    )
    pr42_info = (
        f"PR [#42]({args.pr42_url}) merged at `{args.pr42_merged_at}`; its separate dashboard lives at [`/984d417f/`](../984d417f/index.html)."
    )
    fresh_reads = a["verification_fresh_read_count"]
    embedded_counts = a["embedded_verification_verdict_counts"]
    exception_text = "\n".join(
        f"- `{row['id']}`: separate ledger `{row['ledger_status']}`, embedded verdict `{row['embedded_verdict']}`, fixture status `{row['fixture_status']}`; action: {row['action']}"
        for row in a["verification_semantic_exceptions"]
    ) or "- None."
    source_crossref_text = "\n".join(
        f"- `{row['id']}` is `unverified`; the verification ledger names [{row['source_name']}]({row['ledger_source_url']}) but that URL is absent from the fixture's source list ({', '.join(row['fixture_source_urls']) or 'none'}). Its evidence says no official fixture page was found."
        for row in a["unverified_source_crossrefs"]
    ) or "- None."
    anomaly_text = "\n".join(f"- {item}." for item in a["verification_timestamp_anomalies"]) or "- No timestamp-order anomalies detected."
    pending_tasks = ", ".join(f"{task} `{state}`" for task, state in a["coordination_pending_tasks"].items()) or "none found"
    warnings_text = "\n".join(f"- **REVIEW:** {item}" for item in warnings) or "- None."
    errors_text = "\n".join(f"- **ERROR:** {item}" for item in errors) or "- None."
    return f"""# Independent Structural Audit — OLBG Dashboard Snapshot

**Audit session:** `5a353e83-olbg1` (**T40**)<br>
**Audit time:** `{args.audit_time}` UTC<br>
**Snapshot:** latest merged-main baseline `{args.snapshot_main_sha}` (PR #42 / session `984d417f`); PR #40 state: `{args.pr40_state}`.<br>
**Scope:** root T34 desk + `/f7fa77fc/` mirror, separate `/c17a9192/` (217 events) and `/984d417f/` (145 events) dashboards, saved verification register, and all static HTML workspaces.
**Boundary:** this session performed **no outbound fetches** to OLBG or any governing body. It reviewed repository content and ran local gates. An HTTPS link or allowlisted host is not proof that the linked page was opened or supports the claim.

## Snapshot reconciliation

- **Fixtures/events:** {a['fixture_count']} rows across {a['sports_count']} in-scope sports: {a['h2h_count']} head-to-head and {a['event_only_count']} event-only cards. Each primary match row has recorded source link(s); source relevance is not established by this structural scan.
- **Fixture status labels:** {fixture_status.get('verified',0)} `verified`, {fixture_status.get('cross-checked',0)} `cross-checked`, {fixture_status.get('unverified',0)} `unverified`. These are not a count of rows freshly re-read in the T34 pass.
- **Originated H2H books:** {a['line_count']}; confidence distribution {confidence_text}. These are independent model estimates, not source facts or copied bookmaker prices.
- **High-pick write-ups:** {a['prediction_count']}; stored text length {a['prediction_word_min']}–{a['prediction_word_max']} whitespace-separated words. The local validator checks joins, sources and the 30-word minimum.
- **Live OLBG capture:** {live['events']} cards at `{a['live_captured_utc']}`; {a['live_sport_count']} hubs attempted, {live['sports_with_tips']} with tips, {live['sports_without_tips']} without. See [Live Refresh](../live-refresh.html); this is upstream discovery, not governing-body confirmation.
- **Feed comparison:** {live['joined']} joined, {live['changed']} consensus/selection changes, {live['selection_flips']} selection flips, {live['new_unverified']} upstream-only cards without a primary row, and {live['absent_from_first_screen']} primary rows absent from the truncated first screen.
- **Flagged registry:** {a['flagged_findings']} systemic findings and {a['flagged_rows']} row notes; {a['missing_utc_flagged_rows']} rows have a missing UTC value recorded on [Flagged for Review](../flagged.html).
- **Scope ambiguity:** {border} remain in the root taxonomy. Both separate `/c17a9192/` and `/984d417f/` taxonomies include Aussie Rules and Gaelic Football; this report does not assume that “football” means soccer only.
- **Task-ID collision:** this session's provisional T36 conflicted with PR #42's T36–T39 assignments. The active audit is T40; the other session's rows are preserved in COORDINATION.md §29, and this report does not claim T36–T39.

### Separate, newer `/c17a9192/` dashboard (PR #41)

- **217 events**, {a['c17_olbg_listed_count']} marked as live OLBG-listed and {a['c17_event_count']-a['c17_olbg_listed_count']} official blind-spot cards; 217 line records and {a['c17_prediction_count']} high-confidence predictions. Status split: {c17_status.get('verified',0)} fully `verified`, {c17_status.get('tour_calendar_verified',0)} `tour_calendar_verified`, {c17_status.get('unverified',0)} `unverified` and flagged.
- Event-type counts in the JSON are {c17_kind.get('h2h_2way',0)} two-way H2H + {c17_kind.get('h2h_3way',0)} three-way H2H = {a['c17_actual_h2h_count']} H2H, plus {c17_kind.get('outright',0)} outright + {c17_kind.get('race',0)} race = {a['c17_actual_field_count']} non-H2H. However, the coordination/PR headline says {a['c17_reported_h2h_count']} H2H + {a['c17_reported_field_count']} multi-runner; the category split is inconsistent even though both totals equal 217.
- Field blanks by verification tier are:

{c17_blank_bullets}

- Rows marked `unverified` still have some fields populated: {', '.join(f'`{field}` {count}' for field,count in a['c17_unverified_nonblank_fields'].items() if count)}. Their flags may explain which pieces are upstream-only, but the row-level status does not itself identify every unconfirmed field. Review each populated value against an official source; blank unsupported fields rather than treating a general host link as proof.
- The namespace contains {a['c17_official_source_records']} source-register records, {a['c17_event_source_links']} event-level official source links, {a['c17_repo_audit_findings']} repository-audit findings, {a['c17_olbg_irregularities']} OLBG defects, and {a['c17_manual_review_events']} event-level manual-review entries. The independent T40 scan covered {a['c17_html_metrics']['page_count']} pages and {a['c17_html_metrics']['tbody_rows']} table rows: all {a['c17_html_metrics']['rows_with_https']} have HTTPS, while {a['c17_html_metrics']['rows_with_official_source']} have a host in the sports governing-body allowlist. The remaining {a['c17_html_metrics']['tbody_rows']-a['c17_html_metrics']['rows_with_official_source']} are concentrated in {c17_official_gap} and link to OLBG taxonomy/defect or repository-audit sources; they are not all fixture rows. The c17 validator checks official hosts on event JSON sources but only HTTPS presence on rendered table rows. See [the dashboard](../c17a9192/index.html), [markets](../c17a9192/markets.html), [predictions](../c17a9192/predictions.html), and [session audit](SESSION_C17A9192_AUDIT.md).

### Separate, newest `/984d417f/` dashboard (PR #42)

{pr42_info}

- **145 fixtures and 145 line books** across 17 sports, with **{s984_status.get('verified',0)} `verified` and {s984_status.get('cross-checked',0)} `cross-checked`** status labels. Event kind counts are {s984_kind.get('h2h',0)} H2H and {s984_kind.get('field',0)} field events. Lines carry {s984_confidence.get('high',0)} High / {s984_confidence.get('medium',0)} Medium / {s984_confidence.get('low',0)} Low confidence; {s984['prediction_count']} prediction write-ups. These labels are in the repository snapshot and were not freshly source-checked here.
- Event records contain {s984['event_source_links']} source links: {s984['official_source_links']} to 33 recognized governing-body/tour hosts and {s984['olbg_source_links']} to OLBG upstream-discovery pages. All 145 fixture rows have at least one recognized governing-body source in the stored JSON. The source registry has {s984['source_record_count']} records; host recognition does not prove a link was opened or supports the claim.
- `flagged.json` has {s984['flagged_row_count']} rows. {s984['unverified_rows']} fixtures list {s984['unverified_field_entries']} individual `unverified_fields` markers; all named values are absent/empty in both the fixture and line JSON. However, the session report claims {s984['claimed_unverified_field_count']} unconfirmed fields explicitly blank. The stored markers total {s984['unverified_field_entries']}, not {s984['claimed_unverified_field_count']}; reconcile whether those are different metrics before repeating the headline.
- The independent HTML scan found **{s984_html['page_count']} pages and {s984_html['tbody_rows']} `<tbody>` rows**: {s984_html['rows_with_https']} have HTTPS and {s984_html['rows_with_official_source']} have a recognized governing-body host. The {s984_html['tbody_rows']-s984_html['rows_with_official_source']} rows without such a host are concentrated in {s984_official_gap}, largely OLBG taxonomy/market, upstream-defect, and repository-audit tables. The {sum(s984_html['rows_missing_https_by_page'].values())} rows with no HTTPS are in {s984_https_gap}, in the cross-desk compliance matrix. The index and 17 sport-page fixture tables have {s984_html['fixture_rows_with_official_source']}/{s984_html['fixture_table_rows']} rows with recognized official hosts; the five flagged-page rows without one are repository/OLBG-defect records, not fixture data. The local 984 validator checks HTTPS on selected table pages, not an official governing-body host on every table row. See [dashboard](../984d417f/index.html), [markets](../984d417f/markets.html), [flags](../984d417f/flagged.html), [repository audit](../984d417f/audit.html), and [session report](SESSION_984D417F_AUDIT.md).

## Saved official-source re-verification — not re-certified here

The root T34 `data/verification.json` was generated at `{a['verification_generated']}`. Its action statuses are **{status.get('confirmed',0)} confirmed + {status.get('corrected',0)} corrected + {status.get('flagged',0)} flagged + {status.get('not_rechecked',0)} not re-checked = {sum(status.values())} rows**. The source-pass ledger therefore records **{fresh_reads} of {a['fixture_count']}** rows as read/corrected/flagged and **{status.get('not_rechecked',0)}** as explicitly not re-read. “Corrected” includes a status downgrade; it is not necessarily a confirmed factual correction.

The fixture JSON's embedded verdicts reconcile as `{embedded_counts}`. One intentional status-taxonomy exception is:

{exception_text}

The `cric-afg-ban-odi` row is the one that the T34 record says has no official fixture page. It remains `unverified`, but its date, participants and venue are populated from OLBG rather than blank; its only fixture source is the ICC rankings page, which the project's own finding says publishes no fixtures. The T40 audit did not edit it, but records this as an unresolved mismatch with the standing instruction to leave unconfirmed facts blank. The separate verification record also names an NZC fixtures URL not listed in that fixture's sources:

{source_crossref_text}

The register has {a['verification_sources']} named source records across {a['verification_by_sport_count']} sports. The [Live Verification page](../live-verification.html) and [`data/verification.json`](../data/verification.json) preserve the row-level evidence. This audit read those local files only; it did not re-fetch any source.

### Verification chronology anomaly

The timestamps in the saved files do not form a consistent sequence:

{anomaly_text}

The GitHub record says PR #39 merged at `{args.pr39_merged_at}`. The report preserves the contradictory timestamps rather than guessing which is wrong; the owner should reconcile them append-only in `COORDINATION.md`.

## Structural source-link review

- The primary `picks.html` and sport-detail pages, including the `/f7fa77fc/` mirror, were scanned for at least one HTTPS host recognized by `scripts/validate.py` on every match row. This checks URL shape/host only, not that the source supports each field.
- On `live-refresh.html`, the “Full Live Capture” table has **{live_table['capture_rows']} rows**: {live_table['capture_official_source_rows']} with a recognized governing-body host and {live_table['capture_olbg_only_rows']} OLBG-only. Across its capture, change and absent-row tables, **{live_table['all_event_rows']} rows** total: {live_table['all_event_rows_official']} with a recognized governing-body link and {live_table['all_event_rows_olbg_only']} OLBG-only. The {live['new_unverified']} upstream-only cards are discovery records, not verified fixtures.
- `live-verification.html` has **{ver_table['detail_rows']} row-by-row entries**, {ver_table['detail_rows_with_official_source']} with a recognized official host. Its coverage-by-sport summary has {ver_table['sport_summary_rows']} rows; {ver_table['sport_summary_without_https']} have no row-level HTTPS link. Under the literal “every table row” rule this is a presentation gap.
- Across **{a['html_page_count']} published HTML files**, the scanner found **{a['all_tbody_rows']} `<tbody>` rows**; **{a['all_rows_missing_https']} have no HTTPS link**. The total includes summary, methodology and preserved companion-workspace tables—not just fixture rows.

Pages with rows lacking any HTTPS anchor:

{gap_lines}

## Remaining work and coordination boundaries

- **Root-scope AFLW repricing remains queued as T35.** T34 flags a mismatch between the root Round 10 ladder inputs and the official 2026 ladder for 16 of 18 clubs; nine root lines and three picks await the dedicated re-price. PR #41 and PR #42 contain re-priced alternatives only inside their separate namespaces; neither changed root `data/lines.json` or `data/predictions.json`.
- **New dashboards:** {pr41_info} {pr42_info} Both are separate from the root T34 dataset.
- **Parallel integration:** {pr40_info} It overlaps source/data/validator/site/coordination work; T40 did not edit those shared files. Current task-board entries still show {pending_tasks}; PR #40 proposes updates to T9–T12, but T19 remains a separate board item.
- **Local structural gates do not certify fresh source reads.** The primary validator checks each fixture's embedded verification block and source-host policy, but it does not load the separate `data/verification.json` file; its allowed verdicts include `not-rechecked`. It makes no live HTTP request. The 58 `not_rechecked` rows therefore remain an explicit verification gap despite a passing gate.
- **Table-link rule is not satisfied everywhere.** Primary fixture rows have recognized HTTPS sources, but the unlinked aggregate/methodology/companion rows listed above remain. No blanket claim is made that all such rows are sports facts.
- **Publication observation:** {page_info} This is GitHub API/workflow metadata only; T40 did not make a browser request to the published `github.io` content.
- **Other noted boundary:** the existing taxonomy includes Aussie Rules and Gaelic Football; the user's “football” exclusion remains ambiguous. No scope change was made.

## Local gates reproduced

{gate_text(gates)}

## Audit findings

{warnings_text}

{errors_text}

## Files and reproduction

- Structural audit: [`scripts/session_5a353e83_audit.py`](../scripts/session_5a353e83_audit.py)
- This report: `reports/SESSION_5A353E83_INDEPENDENT_AUDIT.md` and [HTML review page](SESSION_5A353E83_INDEPENDENT_AUDIT.html)
- Main audit pages: [All Lines](../picks.html), [Live Refresh](../live-refresh.html), [Live Verification](../live-verification.html), [Flagged for Review](../flagged.html), [Official Sources](../sources.html)

Reproduce offline from the repository root:

```bash
python3 scripts/session_5a353e83_audit.py \\
  --audit-time {args.audit_time} \\
  --snapshot-main-sha {args.snapshot_main_sha} \\
  --pr39-merged-at {args.pr39_merged_at} \\
  --pr40-number {args.pr40_number} \\
  --pr40-state {shlex.quote(args.pr40_state)} \\
  --pr40-url {args.pr40_url} \\
  --pr40-checked-at {args.pr40_checked_at} \\
  --pr41-merged-at {args.pr41_merged_at} \\
  --pr41-url {args.pr41_url} \\
  --pr42-merged-at {args.pr42_merged_at} \\
  --pr42-url {args.pr42_url} \\
  --pages-api-status {args.pages_api_status} \\
  --pages-run-id {args.pages_run_id} \\
  --pages-run-status {args.pages_run_status} \\
  --pages-main-sha {args.pages_main_sha} \\
  --pages-run-url {args.pages_run_url} \\
  --pages-checked-at {args.pages_checked_at}
```
"""


def render_html(a: dict[str, object], args: argparse.Namespace, gates: list[dict[str, object]]) -> str:
    status = a["verification_status_counts"]
    fixture_status = a["fixture_status_counts"]
    c17_status = a["c17_status_counts"]
    c17_kind = a["c17_kind_counts"]
    s984 = a["s984_metrics"]
    s984_status = s984["status_counts"]
    s984_kind = s984["kind_counts"]
    s984_confidence = s984["confidence_counts"]
    s984_html = a["s984_html_metrics"]
    s984_official_gap_text = ", ".join(
        f"{page} ({count})" for page, count in s984_html["rows_missing_official_by_page"].items()
    ) or "none"
    s984_https_gap_text = ", ".join(
        f"{page} ({count})" for page, count in s984_html["rows_missing_https_by_page"].items()
    ) or "none"
    live = a["live_metrics"]
    live_table = a["live_table_metrics"]
    ver_table = a["verification_table_metrics"]
    warnings = a["warnings"]
    errors = a["errors"]
    pages_link_list = "\n".join(
        f'<li><a href="../{html.escape(page, quote=True)}"><code>{html.escape(page)}</code></a> — {count} row(s) without HTTPS.</li>'
        for page, count in a["rows_missing_https_by_page"]
    ) or "<li>None.</li>"
    warning_list = "\n".join(f"<li>{html.escape(item)}</li>" for item in warnings) or "<li>None.</li>"
    error_list = "\n".join(f"<li><strong>ERROR:</strong> {html.escape(item)}</li>" for item in errors) or "<li>None.</li>"
    gate_sections = "\n".join(
        f'<section class="gate"><h3><code>{html.escape(str(gate["command"]))}</code></h3>'
        f'<p>Exit code: <strong>{gate["returncode"]}</strong></p>'
        f'<pre>{html.escape(str(gate["output"]))}</pre></section>'
        for gate in gates
    ) or "<p>Not run.</p>"
    scope_counts = ", ".join(f"{html.escape(k)}: {v}" for k, v in a["borderline_sports"].items()) or "none"
    t34_anomalies = "\n".join(f"<li>{html.escape(item)}</li>" for item in a["verification_timestamp_anomalies"]) or "<li>None.</li>"
    crossref = "\n".join(
        f'<li><code>{html.escape(str(row["id"]))}</code>: ledger source <a href="{html.escape(str(row["ledger_source_url"]), quote=True)}">{html.escape(str(row["source_name"]))}</a> is absent from the fixture source list; its evidence says no official fixture page was found.</li>'
        for row in a["unverified_source_crossrefs"]
    ) or "<li>None.</li>"
    pages_observation = (
        f'Pages API <code>{html.escape(args.pages_api_status)}</code>; '
        f'<a href="{html.escape(args.pages_run_url, quote=True)}">workflow run {html.escape(args.pages_run_id)}</a> '
        f'(<code>{html.escape(args.pages_run_status)}</code>) for main SHA '
        f'<code>{html.escape(args.pages_main_sha)}</code>, observed {html.escape(args.pages_checked_at)} UTC.'
        if args.pages_run_id != "not supplied"
        else "Pages deployment metadata was not supplied to this offline report."
    )
    pr40_link = (
        f'<a href="{html.escape(args.pr40_url, quote=True)}">PR #{html.escape(args.pr40_number)}</a>'
        if args.pr40_number != "not supplied"
        else "PR #40"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Independent Structural Audit · OLBG Origination Desk</title>
<meta name="description" content="Offline structural audit of provenance, verification coverage, table links and publication status for the OLBG dashboard.">
<link rel="stylesheet" href="../assets/style.css">
<style>
.audit-wrap{{max-width:1100px;margin:0 auto;padding:32px 22px 70px}}
.audit-wrap h1{{font-size:clamp(2rem,4vw,3.25rem);line-height:1.08;margin:.4rem 0 1rem}}
.audit-wrap h2{{margin:2rem 0 .7rem;border-bottom:1px solid #283244;padding-bottom:.45rem}}
.audit-wrap h3{{margin:1rem 0 .5rem}}
.audit-wrap p,.audit-wrap li{{line-height:1.65;color:#c7cfdb}}
.audit-wrap a{{color:#8bc5ff}}
.audit-kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:1.4rem 0}}
.audit-kpi,.audit-card{{border:1px solid #283244;background:#121a27;border-radius:14px;padding:16px}}
.audit-kpi strong{{display:block;font-size:1.65rem;color:#f1f5f9}}
.audit-kpi span,.muted{{font-size:.88rem;color:#9caabd}}
.audit-card{{margin:12px 0}}
.audit-card.warning{{border-color:#795a29;background:#251d10}}
.audit-card.danger{{border-color:#713f49;background:#25151a}}
.audit-wrap code{{overflow-wrap:anywhere}}
.audit-wrap pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#0b111a;border:1px solid #283244;padding:14px;border-radius:10px;color:#c7cfdb}}
.audit-wrap .lead{{font-size:1.08rem;color:#dce5ef}}
.audit-nav{{display:flex;flex-wrap:wrap;gap:10px;margin:1rem 0 1.6rem}}
.audit-nav a{{display:inline-block;border:1px solid #344258;border-radius:999px;padding:8px 12px;text-decoration:none}}
</style>
</head>
<body>
<header class="site-header"><div class="hdr-inner"><div class="brand"><a href="../index.html"><span class="dot"></span> OLBG Origination Desk <span class="sub">Independent Audit</span></a></div></div></header>
<main class="audit-wrap">
<p class="eyebrow">T40 · offline structural review · {html.escape(args.audit_time)} UTC · main {html.escape(args.snapshot_main_sha)}</p>
<h1>Independent Structural Audit</h1>
<p class="lead"><strong>Boundary:</strong> This session made no outbound fetches to OLBG or any governing body. It inspected repository files and ran local validators. A source URL's presence or allowlisted host does not prove the linked page was opened or still supports the claim.</p>
<nav class="audit-nav" aria-label="Audit links"><a href="../index.html">Dashboard</a><a href="../picks.html">All Lines</a><a href="../live-refresh.html">Live Refresh</a><a href="../live-verification.html">Live Verification</a><a href="../flagged.html">Flagged for Review</a><a href="../sources.html">Official Sources</a><a href="../c17a9192/index.html">c17 dashboard</a><a href="../984d417f/index.html">984 dashboard</a></nav>
<div class="audit-kpis">
<div class="audit-kpi"><strong>{a['fixture_count']}</strong><span>fixture/event rows</span></div>
<div class="audit-kpi"><strong>{a['line_count']}</strong><span>originated H2H books</span></div>
<div class="audit-kpi"><strong>{a['prediction_count']}</strong><span>High-pick write-ups</span></div>
<div class="audit-kpi"><strong>{status.get('not_rechecked',0)}</strong><span>source rows not re-read in T34</span></div>
<div class="audit-kpi"><strong>{live['events']}</strong><span>OLBG cards in saved capture</span></div>
<div class="audit-kpi"><strong>{s984['event_count']}</strong><span>events in separate 984d417f snapshot</span></div>
<div class="audit-kpi"><strong>{a['all_rows_missing_https']}</strong><span>of {a['all_tbody_rows']} table rows without HTTPS</span></div>
</div>
<section class="audit-card warning"><h2>Freshness boundary</h2>
<p>The saved T34 register records <strong>{status.get('confirmed',0)} confirmed, {status.get('corrected',0)} corrected, {status.get('flagged',0)} flagged, and {status.get('not_rechecked',0)} not re-checked</strong> ({a['fixture_count']} rows total). {a['verification_fresh_read_count']} rows were classified as read/corrected/flagged, but “corrected” includes a status downgrade. T40 did not re-fetch sources.</p>
<p>The main validator checks embedded per-fixture verification blocks, allows <code>not-rechecked</code>, and does not load the separate <code>data/verification.json</code> register. A passing result is not proof of fresh source reads.</p>
</section>
<section class="audit-card"><h2>Snapshot reconciliation</h2>
<ul>
<li>Primary data: {a['fixture_count']} rows across {a['sports_count']} sports; {a['h2h_count']} H2H fixtures and {a['event_only_count']} event-only cards.</li>
<li>Fixture status labels: {fixture_status.get('verified',0)} verified, {fixture_status.get('cross-checked',0)} cross-checked, {fixture_status.get('unverified',0)} unverified.</li>
<li>Model confidence counts: {html.escape(confidence_text)}; {a['prediction_count']} High-pick texts of {a['prediction_word_min']}–{a['prediction_word_max']} words.</li>
<li>OLBG capture: {live['events']} cards; {live['joined']} joined, {live['changed']} consensus/selection changes, {live['selection_flips']} selection flips, {live['new_unverified']} upstream-only, {live['absent_from_first_screen']} absent from the truncated first screen.</li>
<li>Flagged registry: {a['flagged_findings']} systemic findings and {a['flagged_rows']} row annotations; {a['missing_utc_flagged_rows']} rows have missing UTC explicitly recorded.</li>
<li>Taxonomy ambiguity: {scope_counts}. The word “football” remains unresolved; the c17 and 984 namespaces also include Aussie Rules and Gaelic Football.</li>
<li>Task-ID collision: this session's provisional T36 collided with PR #42's T36–T39. The current audit is T40, appended in COORDINATION.md §30.</li>
</ul></section>
<section class="audit-card"><h2>Separate /c17a9192/ dashboard (PR #41)</h2>
<p>The newer namespace contains <strong>{a['c17_event_count']} events</strong>: {c17_status.get('verified',0)} fully verified, {c17_status.get('tour_calendar_verified',0)} calendar-verified with partial blanks, and {c17_status.get('unverified',0)} unverified; {a['c17_manual_review_events']} manual-review entries. It has {a['c17_prediction_count']} high-confidence picks and {a['c17_html_metrics']['page_count']} pages with {a['c17_html_metrics']['tbody_rows']} table rows; all {a['c17_html_metrics']['rows_with_https']} rows have HTTPS, while {a['c17_html_metrics']['rows_with_official_source']} have a recognized governing-body host. The remaining {a['c17_html_metrics']['tbody_rows']-a['c17_html_metrics']['rows_with_official_source']} rows link to non-governing-body sources such as OLBG taxonomy or repository-audit notes.</p>
<p>The structured event types are {c17_kind.get('h2h_2way',0)} two-way H2H + {c17_kind.get('h2h_3way',0)} three-way H2H = {a['c17_actual_h2h_count']} H2H, plus {c17_kind.get('outright',0)} outrights + {c17_kind.get('race',0)} races = {a['c17_actual_field_count']} non-H2H. The coordination headline instead states {a['c17_reported_h2h_count']} H2H + {a['c17_reported_field_count']} multi-runner. These classifications disagree, although both totals equal 217.</p>
<p>Rows with overall <code>unverified</code> status still have populated values for: {html.escape(', '.join(f'{field} {count}' for field,count in a['c17_unverified_nonblank_fields'].items() if count))}. T40 did not fetch sources, so each populated field needs confirmation or a blank.</p>
<p><a href="../c17a9192/index.html">Open the separate dashboard</a> · <a href="../c17a9192/markets.html">Markets</a> · <a href="../c17a9192/predictions.html">Predictions</a> · <a href="SESSION_C17A9192_AUDIT.md">Session audit</a></p></section>
<section class="audit-card warning"><h2>Separate /984d417f/ dashboard (PR #42)</h2>
<p><a href="{html.escape(args.pr42_url, quote=True)}">PR #42</a> merged at <code>{html.escape(args.pr42_merged_at)}</code> and introduced this separate namespace. It contains <strong>{s984['event_count']} fixture/event rows and {s984['line_count']} line books</strong> across 17 sports; status labels are {s984_status.get('verified',0)} verified and {s984_status.get('cross-checked',0)} cross-checked. Kinds: {s984_kind.get('h2h',0)} H2H and {s984_kind.get('field',0)} field events. Confidence: {s984_confidence.get('high',0)} High / {s984_confidence.get('medium',0)} Medium / {s984_confidence.get('low',0)} Low; {s984['prediction_count']} predictions.</p>
<p>Stored event data has {s984['event_source_links']} source links: {s984['official_source_links']} to recognized official authority hosts and {s984['olbg_source_links']} to OLBG upstream discovery. Each of the 145 fixture records has at least one recognized authority source. The source register has {s984['source_record_count']} records; these are URL/host checks only, not fresh source verification.</p>
<p><strong>Blank markers:</strong> {s984['flagged_row_count']} flagged rows; {s984['unverified_rows']} fixtures list {s984['unverified_field_entries']} field-level uncertainty markers, and all named values are absent/empty in fixture and line JSON. The session report headline says {s984['claimed_unverified_field_count']} fields, so the count is inconsistent (stored marker total: {s984['unverified_field_entries']}).</p>
<p><strong>Rendered rows:</strong> {s984_html['page_count']} pages, {s984_html['tbody_rows']} table rows; {s984_html['rows_with_https']} with HTTPS, {s984_html['rows_with_official_source']} with recognized governing-body hosts. {s984_html['tbody_rows']-s984_html['rows_with_official_source']} lack such a host, concentrated in {html.escape(s984_official_gap_text)}. {sum(s984_html['rows_missing_https_by_page'].values())} rows have no HTTPS, in {html.escape(s984_https_gap_text)}. All {s984_html['fixture_rows_with_official_source']} of {s984_html['fixture_table_rows']} index/sport fixture table rows have a recognized authority link.</p>
<p><a href="../984d417f/index.html">Dashboard</a> · <a href="../984d417f/markets.html">Markets</a> · <a href="../984d417f/flagged.html">Flags</a> · <a href="../984d417f/audit.html">Repository audit</a> · <a href="SESSION_984D417F_AUDIT.md">Session report</a></p></section>
<section class="audit-card danger"><h2>Unverified Afghanistan–Bangladesh ODI row</h2>
<p><code>cric-afg-ban-odi</code> is marked unverified and the T34 finding says no official fixture page was found. However, the primary row still contains the date, participants and venue sourced from OLBG; its only fixture source link is an ICC rankings page that does not publish fixtures. The saved verification action ledger labels the status downgrade “corrected,” while the embedded verdict is “unconfirmed.” Under the standing instruction, those unconfirmed fixture values should be blank; this structural task records but does not edit the row.</p>
<ul>{crossref}</ul></section>
<section class="audit-card warning"><h2>Verification chronology</h2>
<p>The separate ledger says it was generated at <code>{html.escape(str(a['verification_generated']))}</code>; COORDINATION §27 reports a T34 run at <code>{html.escape(str(a['t34_run_claimed']))}</code>. PR #39 merged at <code>{html.escape(args.pr39_merged_at)}</code>. These timestamps conflict:</p>
<ul>{t34_anomalies}</ul>
<p>The audit preserves the discrepancy rather than guessing which timestamp is wrong.</p></section>
<section class="audit-card"><h2>Source-link structure</h2>
<p>Every primary match row in the root <a href="../picks.html">All Lines</a> and sport pages, plus the <a href="../f7fa77fc/index.html">mirror</a>, has at least one HTTPS host accepted by the validator's allowlist. This is only a host/shape check.</p>
<p>Live Refresh capture: {live_table['capture_rows']} rows, {live_table['capture_official_source_rows']} with a recognized governing-body link, {live_table['capture_olbg_only_rows']} OLBG-only. Across capture/change/absent tables: {live_table['all_event_rows']} rows, {live_table['all_event_rows_official']} with recognized official links, {live_table['all_event_rows_olbg_only']} OLBG-only.</p>
<p>Live Verification detail table: {ver_table['detail_rows']} rows, {ver_table['detail_rows_with_official_source']} with recognized official links. Sport-summary table: {ver_table['sport_summary_rows']} rows, {ver_table['sport_summary_without_https']} without a row-level HTTPS link.</p>
<p>Whole-tree scan: <strong>{a['all_tbody_rows']} table rows across {a['html_page_count']} HTML pages</strong>; {a['all_rows_missing_https']} have no HTTPS link. The count includes summary, methodology and historical companion pages.</p>
<ul>{pages_link_list}</ul></section>
<section class="audit-card danger"><h2>Outstanding work and coordination</h2>
<ul>
<li><strong>Root T35 AFLW re-price remains queued:</strong> nine root lines and three picks await the official 2026 Round 10 re-price (16 of 18 club inputs disagree). PR #41 and PR #42 carry separate alternatives only inside <code>/c17a9192/</code> and <code>/984d417f/</code>; root data is unchanged.</li>
<li><strong>{pr40_link}</strong> was <code>{html.escape(args.pr40_state)}</code> at {html.escape(args.pr40_checked_at)} UTC. It overlaps source/data/validator/site integration; T40 did not modify those paths.</li>
<li><strong>Board statuses:</strong> {html.escape(', '.join(f'{k} {v}' for k,v in a['coordination_pending_tasks'].items()) or 'none found')} remain pending/queued at the audited snapshot. PR #40 proposes updates to T9–T12; T19 is separate.</li>
<li><strong>Scope ambiguity:</strong> {scope_counts} remain in the taxonomy despite the brief's “football” exclusion; both new namespaces also include Gaelic Football and Aussie Rules. This audit did not infer the intended code.</li>
<li><strong>Whole-table source rule:</strong> aggregate/methodology/companion rows without HTTPS remain listed above; they are not silently called fixture claims.</li>
</ul></section>
<section class="audit-card"><h2>GitHub Pages observation</h2><p>{pages_observation}</p><p class="muted">GitHub API/workflow metadata only; no direct browser request was made to <code>github.io</code>.</p></section>
<section><h2>Local gates reproduced</h2>{gate_sections}</section>
<section class="audit-card"><h2>Limits</h2><p>This audit did not fetch official pages, certify the completeness of OLBG's truncated feeds, reprice the model, or verify predictive performance. Saved links and ledgers were inspected structurally only.</p></section>
<footer class="muted"><p>Task T40 · <code>scripts/session_5a353e83_audit.py</code> · <a href="../COORDINATION.md">COORDINATION.md</a> records task ownership and history.</p></footer>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-time", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"))
    parser.add_argument("--pages-api-status", default="not queried")
    parser.add_argument("--pages-run-id", default="not supplied")
    parser.add_argument("--pages-run-status", default="not supplied")
    parser.add_argument("--pages-main-sha", default="not supplied")
    parser.add_argument("--pages-run-url", default="https://github.com/buffedlizard55-lab/OLBG1/actions")
    parser.add_argument("--pages-checked-at", default="not supplied")
    parser.add_argument("--snapshot-main-sha", default="not supplied")
    parser.add_argument("--pr39-merged-at", default="not supplied")
    parser.add_argument("--pr40-number", default="not supplied")
    parser.add_argument("--pr40-state", default="not queried")
    parser.add_argument("--pr40-url", default="https://github.com/buffedlizard55-lab/OLBG1/pulls")
    parser.add_argument("--pr40-checked-at", default="not supplied")
    parser.add_argument("--pr41-merged-at", default="not supplied")
    parser.add_argument("--pr41-url", default="https://github.com/buffedlizard55-lab/OLBG1/pull/41")
    parser.add_argument("--pr42-merged-at", default="not supplied")
    parser.add_argument("--pr42-url", default="https://github.com/buffedlizard55-lab/OLBG1/pull/42")
    args = parser.parse_args()

    audit = audit_snapshot(args)
    # Render an initial HTML page so the repository's own link scanner includes it.
    REPORT_MD.write_text(render_markdown(audit, args, []), encoding="utf-8")
    REPORT_HTML.write_text(render_html(audit, args, []), encoding="utf-8")

    gates = [
        run_gate([sys.executable, "scripts/validate.py"]),
        run_gate([sys.executable, "scripts/ebfbd966_validate.py"]),
        run_gate([sys.executable, "scripts/ccb6bde2_validate.py"]),
        run_gate([sys.executable, "scripts/c17a9192_validate.py"]),
        run_gate([sys.executable, "scripts/s984d417f_validate.py"]),
    ]
    if any(int(gate["returncode"]) != 0 for gate in gates):
        audit["errors"].append("one or more repository validators failed; see captured output")

    # The final render includes captured local-gate output. The HTML scanner is then
    # rerun once more to ensure the published report page itself has no broken links.
    REPORT_MD.write_text(render_markdown(audit, args, gates), encoding="utf-8")
    REPORT_HTML.write_text(render_html(audit, args, gates), encoding="utf-8")
    final_gate = run_gate([sys.executable, "scripts/validate.py"])
    if int(final_gate["returncode"]) != 0:
        audit["errors"].append("final whole-tree HTML validation failed after rendering the report")
        REPORT_MD.write_text(render_markdown(audit, args, gates + [final_gate]), encoding="utf-8")
        REPORT_HTML.write_text(render_html(audit, args, gates + [final_gate]), encoding="utf-8")

    lines = [
        f"Fixtures: {audit['fixture_count']} | lines: {audit['line_count']} | predictions: {audit['prediction_count']}",
        f"Verification statuses: {audit['verification_status_counts']}",
        f"Live capture: {audit['live_metrics']}",
        f"HTML pages: {audit['html_page_count_expected_after_audit_page']} expected (includes audit page); tbody rows: {audit['all_tbody_rows']}; no-HTTPS rows: {audit['all_rows_missing_https']}",
        "Validator exits: " + ", ".join(f"{Path(str(gate['command'].split()[-1])).name}={gate['returncode']}" for gate in gates) + f"; final primary validator={final_gate['returncode']}",
        f"Structural errors: {len(audit['errors'])}; review notes: {len(audit['warnings'])}",
        f"Wrote: {REPORT_MD.relative_to(ROOT)} and {REPORT_HTML.relative_to(ROOT)}",
    ]
    print("\n".join(lines))
    for error in audit["errors"]:
        print("ERROR:", error)
    for warning in audit["warnings"]:
        print("REVIEW:", warning)
    return 1 if audit["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
