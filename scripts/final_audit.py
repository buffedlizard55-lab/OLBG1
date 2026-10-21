#!/usr/bin/env python3
"""Generate a line-by-line, reviewable manifest for the primary OLBG desk.

This is an offline audit of the versioned snapshot.  It intentionally does not fetch
third-party sites: review readers can open each recorded official link themselves, and
``scripts/validate.py`` enforces the source-host, market, export and link rules.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "FINAL_INTEGRATION_AUDIT.md"


class TableRowLinks(HTMLParser):
    """Minimal collector for links found in HTML tbody rows."""

    def __init__(self) -> None:
        super().__init__()
        self.tbody_depth = 0
        self.in_row = False
        self.current: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "tbody":
            self.tbody_depth += 1
        elif tag == "tr" and self.tbody_depth:
            self.in_row = True
            self.current = []
        if tag == "a" and self.in_row and attrs_dict.get("href") is not None:
            self.current.append(str(attrs_dict["href"]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_row:
            self.rows.append(self.current)
            self.in_row = False
        elif tag == "tbody" and self.tbody_depth:
            self.tbody_depth -= 1


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def md_link(label: str, url: str) -> str:
    safe_label = label.replace("[", "\\[").replace("]", "\\]")
    return f"[{safe_label}]({url})"


def fixture_label(fixture: dict) -> str:
    if fixture.get("away"):
        return f"{fixture['home']} vs {fixture['away']}"
    return fixture["home"]


def archive_table_link_gaps() -> dict[str, list[int]]:
    """Surface historical table rows with no external URL; they are review flags, not facts."""
    gaps: dict[str, list[int]] = {}
    for namespace in ("docs", "ebfbd966", "aa4e9dbf", "2360a617"):
        for page in sorted((ROOT / namespace).rglob("*.html")):
            parser = TableRowLinks()
            parser.feed(page.read_text(encoding="utf-8"))
            missing = [
                index
                for index, row in enumerate(parser.rows, 1)
                if not any(link.startswith("https://") for link in row)
            ]
            if missing:
                gaps[page.relative_to(ROOT).as_posix()] = missing
    return gaps


def main() -> None:
    fixtures_doc = read_json("data/fixtures.json")
    lines_doc = read_json("data/lines.json")
    predictions_doc = read_json("data/predictions.json")
    flagged_doc = read_json("datasets/flagged_for_review.json")

    fixtures = fixtures_doc["fixtures"]
    lines = {line["id"]: line for line in lines_doc["lines"]}
    predictions = {item["match_id"]: item for item in predictions_doc["predictions"]}

    by_sport: dict[str, Counter] = defaultdict(Counter)
    source_hosts: Counter[str] = Counter()
    for fixture in fixtures:
        by_sport[fixture["sport"]]["events"] += 1
        by_sport[fixture["sport"]][fixture["status"]] += 1
        if fixture.get("away"):
            by_sport[fixture["sport"]]["h2h"] += 1
        for source in fixture["sources"]:
            source_hosts[urlparse(source["url"]).netloc] += 1

    total_coverage = Counter()
    for line in lines.values():
        market_keys = {market["key"] for market in line["markets"]}
        for key in ("winner", "handicap", "total", "dnb"):
            if key in market_keys:
                total_coverage[f"priced_{key}"] += 1
        for unavailable in line.get("unavailable_markets", []):
            total_coverage[f"unavailable_{unavailable['key']}"] += 1
        total_coverage[f"confidence_{line['confidence']}"] += 1

    archive_gaps = archive_table_link_gaps()
    out: list[str] = [
        "# Final Integration Audit — Primary OLBG Origination Desk",
        "",
        "**Snapshot date:** `2026-10-21 UTC`",
        "**Scope:** the current root desk (`data/fixtures.json`, `data/lines.json`, "
        "`data/predictions.json`), its `/f7fa77fc/` mirror, and repository-wide static-link scan.",
        "",
        "## What this audit establishes",
        "",
        "- The primary snapshot has a per-row governing-body source link recorded below. "
        "The links are source provenance for manual review, not bookmaker prices.",
        "- All prices are the repository's independently originated estimates. They are not "
        "copied odds and they are not verified sporting facts.",
        "- The validation gate checks URL scheme/authority allowlists, IDs, excluded-sport "
        "rules, market probability sums, explicit blank-market exceptions, high-pick "
        "writing rules, machine-readable exports, mirror parity and relative HTML links. "
        "It does not make live HTTP requests, so a later publisher-side URL/content change "
        "must be reviewed at the linked authority.",
        "",
        "## Snapshot totals",
        "",
        f"- **{len(fixtures)}** fixture/event rows across **{len(by_sport)}** in-scope sports.",
        f"- **{len(lines)}** head-to-head line books: Match Winner + Handicap for all; "
        f"Over/Under total for **{total_coverage['priced_total']}**; "
        f"**{total_coverage['unavailable_total']}** total explicitly blank/unverified.",
        f"- Confidence: **{total_coverage['confidence_high']} High**, "
        f"**{total_coverage['confidence_medium']} Medium**, "
        f"**{total_coverage['confidence_low']} Low**.  High-pick narratives: "
        f"**{len(predictions)}**.",
        f"- Published review registry: **{len(flagged_doc['findings'])}** systemic findings and "
        f"**{len(flagged_doc['rows'])}** row annotations.",
        "",
        "## Sport coverage",
        "",
        "| Sport | Events | H2H books | Verified | Cross-checked |",
        "|---|---:|---:|---:|---:|",
    ]
    for sport, counts in sorted(by_sport.items()):
        out.append(
            f"| {sport} | {counts['events']} | {counts['h2h']} | "
            f"{counts['verified']} | {counts['cross-checked']} |"
        )

    out += [
        "",
        "## Recorded official authority hosts",
        "",
        "| Authority host | Fixture-source links |",
        "|---|---:|",
    ]
    for host, count in sorted(source_hosts.items()):
        out.append(f"| `{host}` | {count} |")

    out += [
        "",
        "## Line-by-line primary fixture manifest",
        "",
        "Each row retains the exact official link(s) recorded in the fixture snapshot. "
        "`Total blank` means no price was invented; the reason is shown in the site and "
        "Flagged for Review register.",
        "",
        "| ID | Sport / fixture | Status | Official source links | Markets / pick / confidence | Flags |",
        "|---|---|---|---|---|---|",
    ]
    for fixture in fixtures:
        line = lines.get(fixture["id"])
        sources = "<br>".join(md_link(source["name"], source["url"]) for source in fixture["sources"])
        flags = "; ".join(fixture.get("flags", [])) or "—"
        if line is None:
            market_summary = "Field event — no two-sided line"
        else:
            market_names = ", ".join(market["key"] for market in line["markets"])
            unavailable = ", ".join(
                f"{market['name']} blank ({market['reason']})"
                for market in line.get("unavailable_markets", [])
            )
            if unavailable:
                market_names += "; " + unavailable
            market_summary = f"{market_names}; pick: {line['pick']} ({line['confidence']})"
        out.append(
            f"| `{fixture['id']}` | {fixture['sport']} — {fixture_label(fixture)} | "
            f"{fixture['status']} | {sources} | {market_summary} | {flags} |"
        )

    out += [
        "",
        "## High-confidence prediction coverage",
        "",
        "| Match ID | Selection | Words | Official source links |",
        "|---|---|---:|---|",
    ]
    for match_id, prediction in predictions.items():
        sources = "<br>".join(md_link(source["name"], source["url"]) for source in prediction["sources"])
        out.append(
            f"| `{match_id}` | {prediction['selection']} | {prediction['words']} | {sources} |"
        )

    out += [
        "",
        "## Historical-workspace review flags",
        "",
        "The repository preserves earlier, namespaced companion desks for comparison. They are "
        "not inputs to the primary 134-event source-backed dataset. The following HTML body-table "
        "rows have **no external HTTPS link at all**. Some are methodology/configuration rows rather "
        "than fixture records, but they are listed rather than silently treated as reviewed fixture "
        "provenance. Their pages' own Flagged-for-Review registers remain the authoritative archival "
        "context.",
        "",
        "| Page | Body-table row numbers without an external link |",
        "|---|---|",
    ]
    if archive_gaps:
        for page, rows in archive_gaps.items():
            rendered = ", ".join(map(str, rows))
            out.append(f"| `{page}` | {rendered} |")
    else:
        out.append("| None | — |")

    out += [
        "",
        "## Reproduce",
        "",
        "```bash",
        "python3 scripts/build_dataset.py",
        "python3 scripts/origin_lines.py",
        "python3 scripts/build_site.py",
        "python3 site/build.py",
        "python3 scripts/validate.py",
        "python3 scripts/final_audit.py",
        "```",
        "",
    ]
    REPORT.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}: {len(fixtures)} primary rows, {len(predictions)} high-pick rows, {len(archive_gaps)} archival table-link review entries.")


if __name__ == "__main__":
    main()
