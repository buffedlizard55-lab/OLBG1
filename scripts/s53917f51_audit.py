#!/usr/bin/env python3
"""Read-only requirements audit for the merged T496E (496eaf02) desk.

This tool reads the peer desk, computes structural discrepancies, and writes only
into this session's namespaced data/site/report files. It never edits T496E inputs.
Official-page excerpts in data/53917f51/evidence.json were separately fetched via
Arena's page tools and are included with their original URLs for manual review.
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = "496eaf02"
DATA = ROOT / "data" / SUBJECT
OUT_DATA = ROOT / "data" / "53917f51"
SITE = ROOT / "53917f51"
EVIDENCE_PATH = OUT_DATA / "evidence.json"
AUDIT_PATH = OUT_DATA / "audit.json"
REPORT_MD = ROOT / "reports" / "SESSION_53917F51.md"
REPORT_HTML = ROOT / "reports" / "SESSION_53917F51.html"

REPO = "https://github.com/buffedlizard55-lab/OLBG1"
GITHUB_BLOB = REPO + "/blob/main/"
NON_OFFICIAL_SOURCE_IDS = {
    "cricinfo": "ESPNcricinfo is a sports-media publisher, not the governing body or competition organizer.",
    "limerick": "Limerick Leader is a newspaper; the source name also mentions The 42.",
    "the42": "The 42 is a sports-media publisher, not the county governing body.",
}

SPORT_ORDER = [
    "tennis", "volleyball", "rugby-union", "rugby-league", "cricket",
    "darts", "baseball", "ice-hockey", "basketball", "handball",
    "motor-racing", "golf", "snooker", "gaelic-sports", "greyhounds",
]
SPORT_LABELS = {
    "tennis": "Tennis", "volleyball": "Volleyball", "rugby-union": "Rugby Union",
    "rugby-league": "Rugby League", "cricket": "Cricket", "darts": "Darts",
    "baseball": "Baseball", "ice-hockey": "Ice Hockey", "basketball": "Basketball",
    "handball": "Handball", "motor-racing": "Motor Racing", "golf": "Golf",
    "snooker": "Snooker", "gaelic-sports": "Gaelic Sports", "greyhounds": "Greyhounds",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def line_of(path: str, needle: str) -> int | None:
    target = ROOT / path
    for n, line in enumerate(target.read_text(encoding="utf-8").splitlines(), start=1):
        if needle in line:
            return n
    return None


def github_ref(path: str, line: int | None = None) -> str:
    url = GITHUB_BLOB + path
    return url + (f"#L{line}" if line else "")


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def american_number(value: str | int | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(str(value).replace("+", ""))
    except ValueError:
        return None


def html_page(title: str, body: str, active: str = "overview") -> str:
    links = [
        ("overview", "index.html", "Overview"),
        ("findings", "flagged.html", "Flagged for Review"),
        ("sources", "sources.html", "Official source reads"),
    ]
    nav = "".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for key, href, label in links
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Independent, source-linked audit of the 23 Oct 2026 T496E OLBG sports desk.">
<title>{html.escape(title)} · 53917f51 audit</title><link rel="stylesheet" href="assets/style.css"></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><a class="brand" href="index.html">OLBG / Independent QA</a><nav aria-label="Primary">{nav}</nav></header>
<main id="main">{body}</main>
<footer><span>Independent audit · not affiliated with OLBG · no betting advice</span>
<span>Audit data: <a href="../data/53917f51/audit.json">JSON</a> · <a href="../reports/SESSION_53917F51.html">HTML report</a> · <a href="../reports/SESSION_53917F51.md">Markdown</a></span></footer>
</body></html>'''


def finding_card(finding: dict) -> str:
    refs = []
    for ref in finding.get("references", []):
        refs.append(f'<a href="{html.escape(ref["url"], quote=True)}">{html.escape(ref["label"])}</a>')
    for ref in finding.get("official_sources", []):
        refs.append(f'<a href="{html.escape(ref["url"], quote=True)}">{html.escape(ref["label"])} ↗</a>')
    links = " · ".join(refs) if refs else "No external source claim; see audit method."
    sev = finding["severity"].lower().replace(" ", "-")
    return (f'<article class="finding {sev}" id="{html.escape(finding["id"])}">'
            f'<div class="meta"><span class="badge {sev}">{html.escape(finding["severity"])}</span>'
            f'<span>{html.escape(finding["id"])}</span><span>{html.escape(finding["status"])}</span></div>'
            f'<h2>{html.escape(finding["title"])}</h2>'
            f'<p>{html.escape(finding["summary"])}</p>'
            f'<p class="refs"><strong>Review links:</strong> {links}</p></article>')


def build_audit(now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    now = now.astimezone(timezone.utc)
    fixture_doc = read_json(DATA / "fixtures.json")
    fixture_rows = fixture_doc["fixtures"]
    fixtures = {row["id"]: row for row in fixture_rows}
    source_doc = read_json(DATA / "sources.json")
    sources = {row["id"]: row for row in source_doc["sources"]}
    prediction_doc = read_json(DATA / "predictions.json")
    predictions = prediction_doc["predictions"]

    with (DATA / "matches.csv").open(encoding="utf-8-sig", newline="") as stream:
        matches = list(csv.DictReader(stream))
    with (DATA / "markets.csv").open(encoding="utf-8-sig", newline="") as stream:
        market_rows = list(csv.DictReader(stream))

    high = [row for row in matches if row.get("confidence", "").lower() == "high"]
    pvals = [float(row["model_probability"]) for row in high]
    high_gt70 = [row for row in high if float(row["model_probability"]) > 0.70]
    high_eq70 = [row for row in high if abs(float(row["model_probability"]) - 0.70) < 1e-9]
    high_lt70 = [row for row in high if float(row["model_probability"]) < 0.70]
    in_band = []
    for row in high:
        price = american_number(row.get("fair_american"))
        if price is not None and -250 <= price <= 10000:
            in_band.append(row)

    sport_counts = Counter(row.get("sport", "") for row in high)
    sport_coverage = [
        {"sport": SPORT_LABELS[slug], "slug": slug, "high_picks": sport_counts[slug],
         "target": 5, "shortfall": max(0, 5 - sport_counts[slug]),
         "desk_url": f"../{SUBJECT}/sports/{slug}.html"}
        for slug in SPORT_ORDER
    ]

    starts_before_capture = []
    starts_before_audit = []
    unverified_start_values = []
    for row in fixture_rows:
        start = parse_time(row.get("start_utc"))
        observed = parse_time(row.get("observed_after"))
        if row.get("state") == "upcoming" and start and observed and start <= observed:
            starts_before_capture.append(row["id"])
        if row.get("state") == "upcoming" and start and start <= now:
            starts_before_audit.append(row["id"])
        flags = " ".join(row.get("flags", [])).lower()
        if start and ("official utc start not published" in flags or "rendered by olbg discovery" in flags):
            unverified_start_values.append(row["id"])

    high_with_stale_inputs = []
    for row in high:
        fid = row.get("id") or row.get("\ufeffid")
        fixture = fixtures.get(fid, {})
        if any("not re-fetched" in flag.lower() for flag in fixture.get("flags", [])):
            high_with_stale_inputs.append({
                "id": fid, "sport": fixture.get("sport"), "selection": row.get("selection"),
                "probability": float(row["model_probability"]), "fair_american": row.get("fair_american"),
            })

    non_official_rows = []
    for fixture in fixture_rows:
        for source in fixture.get("sources", []):
            sid = source.get("id")
            if sid not in NON_OFFICIAL_SOURCE_IDS:
                continue
            non_official_rows.append({
                "fixture_id": fixture["id"], "sport": fixture["sport"],
                "source_id": sid, "publisher": source.get("name"), "url": source.get("url"),
                "note": NON_OFFICIAL_SOURCE_IDS[sid],
            })

    source_meta_fields = {
        "accessed_at", "accessed_at_utc", "retrieved_at", "retrieved_at_utc", "fetched_at",
        "http_status", "sha256", "content_sha256", "excerpt", "body_sha256",
    }
    source_records_with_capture_metadata = sum(
        any(key in record for key in source_meta_fields) for record in source_doc["sources"]
    )
    non_official_fixture_count = len({row["fixture_id"] for row in non_official_rows})

    word_counts = [len(row.get("text", "").split()) for row in predictions]
    unique_texts = len({" ".join(row.get("text", "").split()).casefold() for row in predictions})
    injury_pattern = re.compile(
        r"\b(injur\w*|ruled out|will be without|without [A-Z]|unavailable|availability|"
        r"available|doubtful|questionable|sidelined|miss(?:es|ed|ing)?|full roster)\b", re.I
    )
    prediction_injury_mentions = sum(bool(injury_pattern.search(row.get("text", ""))) for row in predictions)
    forbidden_hits = sum(
        len(re.findall(r"\b(?:model|verified)\b", row.get("text", ""), re.I))
        for row in predictions
    )

    date_typos = []
    for path in [
        "reports/SESSION_496EAF02.md", "496eaf02/methodology.html", "scripts/se496eaf02_build.py",
    ]:
        line = line_of(path, "2023-10-23")
        if line:
            date_typos.append({"path": path, "line": line, "url": github_ref(path, line)})

    tn04 = next(row for row in predictions if row.get("match_id") == "TN04")
    gh01 = fixtures["GH01"]
    tn03 = fixtures["TN03"]
    cr01 = fixtures["CR01"]
    cr05 = fixtures["CR05"]
    gs05 = fixtures["GS05"]
    cr02 = fixtures["CR02"]

    refs = {
        "tn04_fixture": github_ref("data/496eaf02/fixtures.json", line_of("data/496eaf02/fixtures.json", '"id": "TN04"')),
        "tn04_prediction": github_ref("data/496eaf02/predictions.json", line_of("data/496eaf02/predictions.json", '"match_id": "TN04"')),
        "tn04_site": "../496eaf02/predictions.html",
        "high_model": github_ref("scripts/se496eaf02_model.py", 26),
        "high_tests": github_ref("tests/pipeline/test_desk_496eaf02.py", 19),
        "gh01_fixture": github_ref("data/496eaf02/fixtures.json", line_of("data/496eaf02/fixtures.json", '"id": "GH01"')),
        "tn03_fixture": github_ref("data/496eaf02/fixtures.json", line_of("data/496eaf02/fixtures.json", '"id": "TN03"')),
        "source_tests": github_ref("tests/pipeline/test_desk_496eaf02.py", 19),
        "cr02_fixture": github_ref("data/496eaf02/fixtures.json", line_of("data/496eaf02/fixtures.json", '"id": "CR02"')),
        "gs05_fixture": github_ref("data/496eaf02/fixtures.json", line_of("data/496eaf02/fixtures.json", '"id": "GS05"')),
        "source_registry": github_ref("data/496eaf02/sources.json", 1),
        "model_inputs": github_ref("data/496eaf02/fixtures.json", line_of("data/496eaf02/fixtures.json", '"id": "CR01"')),
        "line_search": github_ref("scripts/se496eaf02_model.py", 29),
        "test_report": github_ref("reports/SESSION_496EAF02.md", 1),
        "date_typo": github_ref("reports/SESSION_496EAF02.md", 16),
    }

    audit = {
        "schema_version": 1,
        "audit_id": "53917f51",
        "subject_desk": SUBJECT,
        "as_of_utc": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "scope": "Independent read-only review of the merged T496E desk. Static checks cover all 81 fixtures, 460 market outcomes, and all 51 predictions. Official external pages were freshly fetched only for the targeted findings recorded in evidence.json; this is not a recertification of all 15 sports.",
        "subject_capture_utc": fixture_doc.get("captured_utc"),
        "subject_sha256": {
            name: sha256(DATA / name)
            for name in ["fixtures.json", "matches.csv", "markets.csv", "predictions.json", "sources.json"]
        },
        "counts": {
            "fixtures": len(fixture_rows),
            "fixtures_claimed_upcoming": sum(row.get("state") == "upcoming" for row in fixture_rows),
            "market_outcomes": len(market_rows),
            "priced_fixtures": sum(str(row.get("priced", "")).lower() == "true" for row in matches),
            "predictions": len(predictions),
            "predictions_min_words": min(word_counts, default=0),
            "predictions_max_words": max(word_counts, default=0),
            "predictions_unique_texts": unique_texts,
            "predictions_with_injury_or_availability_term": prediction_injury_mentions,
            "prediction_forbidden_word_occurrences": forbidden_hits,
            "high_labeled": len(high),
            "high_strictly_over_70_percent": len(high_gt70),
            "high_exactly_70_percent": len(high_eq70),
            "high_at_least_70_percent": len(high_gt70) + len(high_eq70),
            "high_below_70_percent": len(high_lt70),
            "high_labeled_in_fair_american_band": len(in_band),
            "high_with_stale_or_not_refetched_inputs": len(high_with_stale_inputs),
            "sports_with_at_least_five_high_picks": sum(sport_counts[s] >= 5 for s in SPORT_ORDER),
            "sports_below_five_high_picks": sum(sport_counts[s] < 5 for s in SPORT_ORDER),
            "sports_with_zero_high_picks": sum(sport_counts[s] == 0 for s in SPORT_ORDER),
            "upcoming_with_start_at_or_before_capture": len(starts_before_capture),
            "upcoming_with_start_at_or_before_audit_time": len(starts_before_audit),
            "flagged_unverified_start_but_start_value_populated": len(unverified_start_values),
            "fixture_rows_using_known_media_sources": non_official_fixture_count,
            "fixture_source_refs_from_known_media": len(non_official_rows),
            "source_registry_entries": len(source_doc["sources"]),
            "source_registry_entries_with_fetch_metadata": source_records_with_capture_metadata,
            "date_typo_occurrences": len(date_typos),
        },
        "high_picks_by_sport": sport_coverage,
        "high_picks_below_70_percent": [
            {"fixture_id": row.get("id") or row.get("\ufeffid"), "sport": row.get("sport"),
             "selection": row.get("selection"), "probability": float(row["model_probability"]),
             "fair_american": row.get("fair_american")}
            for row in high_lt70
        ],
        "high_picks_with_stale_inputs": high_with_stale_inputs,
        "fixture_rows_using_known_media_sources": non_official_rows,
        "upcoming_start_conflicts_at_capture": [
            {"fixture_id": row["id"], "start_utc": row.get("start_utc"),
             "observed_after": row.get("observed_after"), "state": row.get("state"),
             "sources": [source.get("url") for source in row.get("sources", [])]}
            for row in fixture_rows
            if row.get("state") == "upcoming" and parse_time(row.get("start_utc"))
            and parse_time(row.get("observed_after"))
            and parse_time(row["start_utc"]) <= parse_time(row["observed_after"])
        ],
        "unverified_start_fields_populated": [
            {"fixture_id": fid, "start_utc": fixtures[fid].get("start_utc"),
             "flags": fixtures[fid].get("flags", []),
             "sources": [source.get("url") for source in fixtures[fid].get("sources", [])]}
            for fid in unverified_start_values
        ],
        "date_typo_locations": date_typos,
        "findings": [],
    }

    official = {
        "wta_retirement": "https://www.wtatennis.com/news/4596745/fernandezs-marathon-win-kostyuks-retirement-headline-day-3-in-ningbo",
        "wta_jovic_paolini": "https://www.wtatennis.com/news/4597089/jovic-rallies-past-paolini-to-reach-ningbo-quarterfinals",
        "wta_semis": "https://www.wtatennis.com/news/4597893/ningbo-semifinals-preview-leylah-fernandez-vs-marie-bouzkova-diana-shnaider-vs-elena-rybakina",
        "wta_draw_pdf": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf",
        "pcb_schedule": "https://www.pcb.com.pk/press-release-detail/pakistan-to-host-sri-lanka-and-england-for-t20is-odi-tri-series-and-tests.html",
        "pcb_recent_results": "https://www.pcb.com.pk/news-detail/sri-lanka-seal-second-highest-chase-in-odi-history-as-brook-s-record-double-ton-goes-in-vain.html",
        "pcb_oct20_result": "https://www.pcb.com.pk/news-detail/arafat-minhas-6-40-and-59-sink-england-as-pakistan-win-consecutive-games-in-odi-tri-series.html",
        "pcb_oct17_schedule": "https://www.pcb.com.pk/press-release-detail/pakistan-england-sri-lanka-set-to-begin-preparations-for-odi-world-cup-with-tri-series-from-18-to-31.html",
        "limerick_fixtures": "https://limerickgaa.ie/senior-hurling-fixtures/",
        "limerick_results": "https://limerickgaa.ie/senior-hurling-results/",
        "gbgb_preview": "https://www.gbgb.org.uk/category-one-glory-beckons-in-coral-100-champion-stakes-final/",
        "gbgb_schedule": "https://www.gbgb.org.uk/racing/open-races/2025-category-one-schedule/",
        "pdc_rankings": "https://www.pdc.tv/rankings",
        "nba_injury_portal": "https://official.nba.com/nba-injury-report-2026-27-season/",
        "nba_injury_415": "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_04_15PM.pdf",
        "nba_injury_530": "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_05_30PM.pdf",
        "el_schedule_article": "https://www.euroleaguebasketball.net/en/euroleague/news/the-2026-27-euroleague-schedule-is-official/",
        "el_schedule_pdf": "https://media-cdn.cortextech.io/1dU3kpCqReRp93/1BSdBWIjChWbPc/de89146d-ddb7-4931-9deb-f72672b4d63b.pdf",
        "el_r7_current": "https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-fantasy/",
        "el_r7_t496": "https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-el2627/",
    }
    finding_defs = [
        {
            "id": "F-53917-01", "severity": "Critical", "status": "needs review",
            "title": "TN04 is a stale fixture and its prediction misattributes a result",
            "summary": ("T496 publishes Leylah Fernandez v Marta Kostyuk as an upcoming Ningbo semifinal and recommends Over 17.5. The accompanying prose says Kostyuk beat Jasmine Paolini 6-4, 6-3. Official WTA reporting dated 21 Oct says Kostyuk retired against Ekaterina Alexandrova in the second round; WTA reporting dated 22 Oct says Iva Jovic—not Kostyuk—beat Paolini 6-4, 6-3; the WTA 23 Oct semifinal preview lists Fernandez v Marie Bouzkova and Rybakina v Shnaider. The TN04 fixture/pick should be withdrawn and only rebuilt from a current official draw/order of play. This audit does not edit the peer desk."),
            "references": [
                {"label": "T496 TN04 fixture", "url": refs["tn04_fixture"]},
                {"label": "T496 TN04 prediction", "url": refs["tn04_prediction"]},
                {"label": "T496 predictions page", "url": refs["tn04_site"]},
            ],
            "official_sources": [
                {"label": "WTA: Kostyuk retired (21 Oct)", "url": official["wta_retirement"]},
                {"label": "WTA: Jovic beat Paolini (22 Oct)", "url": official["wta_jovic_paolini"]},
                {"label": "WTA: actual Ningbo semifinals (23 Oct)", "url": official["wta_semis"]},
            ],
            "data": {"fixture_id": "TN04", "prediction_selection": tn04.get("selection"),
                     "prediction_bet_line": tn04.get("bet_line")},
        },
        {
            "id": "F-53917-02", "severity": "High", "status": "needs review",
            "title": "The High label is applied below the brief’s >70% threshold",
            "summary": (f"The desk labels {len(high)} picks High. Recomputed from matches.csv, {len(high_gt70)} are strictly above 70%, {len(high_eq70)} equal 70%, and {len(high_lt70)} fall below 70% (62–<70%). Its own page defines High as starting at 62%; the session claim/brief calls for >70% high confidence. All {len(in_band)} High-labeled rows fall inside the displayed fair-American band, but those are originated fair prices, not bookmaker quotes."),
            "references": [
                {"label": "T496 high-confidence page", "url": "../496eaf02/high-confidence.html"},
                {"label": "T496 confidence implementation", "url": refs["high_model"]},
                {"label": "T496 test domain/confidence policy", "url": refs["high_tests"]},
            ],
            "official_sources": [],
            "data": {"high": len(high), "gt70": len(high_gt70), "eq70": len(high_eq70), "lt70": len(high_lt70)},
        },
        {
            "id": "F-53917-03", "severity": "High", "status": "needs review",
            "title": "GH01 is marked upcoming after its own recorded start time",
            "summary": (f"GH01 records start_utc={gh01.get('start_utc')}, observed_after={gh01.get('observed_after')}, and state=upcoming. The start precedes the recorded capture by 17 minutes; the generated matches/sport pages still publish it as upcoming, and its price expiry is later. GBGB’s official schedule supports Fri 23 Oct but not the exact 20:13Z time in this row, so the exact time also needs an official recheck or blanking."),
            "references": [
                {"label": "T496 GH01 fixture", "url": refs["gh01_fixture"]},
                {"label": "T496 matches page", "url": "../496eaf02/matches.html"},
                {"label": "T496 greyhounds page", "url": "../496eaf02/sports/greyhounds.html"},
            ],
            "official_sources": [
                {"label": "GBGB 2026 Category One schedule", "url": official["gbgb_schedule"]},
                {"label": "GBGB Champion Stakes preview", "url": official["gbgb_preview"]},
            ],
            "data": {"start_utc": gh01.get("start_utc"), "observed_after": gh01.get("observed_after"),
                     "state": gh01.get("state")},
        },
        {
            "id": "F-53917-04", "severity": "High", "status": "needs review",
            "title": "TN03 retains a populated UTC start explicitly flagged as unverified",
            "summary": (f"TN03 has start_utc={tn03.get('start_utc')}, while its own flag says the time came from OLBG discovery and was not published in the fetched WTA draw. The official WTA draw PDF lists participants/seeds/results, not this UTC start. Under the brief’s blank-if-unconfirmed rule, retain the official date if supported but leave the exact UTC start blank until an official order of play supplies it."),
            "references": [
                {"label": "T496 TN03 fixture", "url": refs["tn03_fixture"]},
                {"label": "WTA Ningbo draw PDF used by T496", "url": official["wta_draw_pdf"]},
            ],
            "official_sources": [{"label": "WTA official order-of-play route", "url": "https://www.wtatennis.com/tournaments/2092/ningbo/2026/order-of-play"}],
            "data": {"start_utc": tn03.get("start_utc"), "flags": tn03.get("flags", [])},
        },
        {
            "id": "F-53917-05", "severity": "High", "status": "needs review",
            "title": "Media sources are classified as official and fixture tests do not check publisher authority",
            "summary": (f"CR02 lists ESPNcricinfo as its only source, and GS05 lists Limerick Leader/The 42 only; both are media sources. The T496 test allowlist nevertheless includes cricinfo.com and limerickleader.ie as OFFICIAL_DOMAINS, and the fixture test checks only that source IDs exist. Fresh official PCB pages confirm CR02’s schedule/results; Limerick GAA’s current fixtures page confirms the Limerick final’s date, time and venue. Add the governing-body links and test source authority, not only URL shape."),
            "references": [
                {"label": "T496 CR02 fixture", "url": refs["cr02_fixture"]},
                {"label": "T496 GS05 fixture", "url": refs["gs05_fixture"]},
                {"label": "T496 source-authority tests", "url": refs["source_tests"]},
            ],
            "official_sources": [
                {"label": "PCB official tri-series fixture schedule", "url": official["pcb_schedule"]},
                {"label": "PCB official 22 Oct results + 25 Oct fixture", "url": official["pcb_recent_results"]},
                {"label": "PCB official Pakistan v England result", "url": official["pcb_oct20_result"]},
                {"label": "Limerick GAA official final fixture", "url": official["limerick_fixtures"]},
                {"label": "Limerick GAA official semifinal results", "url": official["limerick_results"]},
            ],
            "data": {"affected_fixture_ids": sorted({r["fixture_id"] for r in non_official_rows})},
        },
        {
            "id": "F-53917-06", "severity": "High", "status": "needs review",
            "title": "Two High-B cricket totals use inputs flagged as not re-fetched",
            "summary": (f"CR01 and CR05 are still assigned High confidence (both 65.95%, fair -194) despite fixture flags saying the team/A-team ratings were not re-fetched this session. Their official schedule links establish the fixtures, not those rating inputs. Until current official inputs are linked, the affected totals should not be promoted as verified high-confidence picks."),
            "references": [{"label": "T496 CR01/CR05 input rows", "url": refs["model_inputs"]}],
            "official_sources": [
                {"label": "ICC NZ v India fixture", "url": "https://www.icc-cricket.com/matches/271647/new-zealand-vs-india"},
                {"label": "New Zealand Cricket fixtures", "url": "https://scoring.nzc.nz/fixtures"},
            ],
            "data": {"affected": high_with_stale_inputs},
        },
        {
            "id": "F-53917-07", "severity": "High", "status": "needs review",
            "title": "GH01’s official-source-backed semi-final time conflicts with the stored input",
            "summary": ("T496’s GH01 input note says Grouchos Gregor’s fastest semi was 35.69 seconds. GBGB’s official Champion Stakes preview says the third semi-final winning time was 35.36 seconds. Correct the value or remove it; it is part of the public form record even though GH01 is Low confidence."),
            "references": [{"label": "T496 GH01 input", "url": refs["gh01_fixture"]}],
            "official_sources": [{"label": "GBGB Champion Stakes preview (35.36 sec)", "url": official["gbgb_preview"]}],
            "data": {"stored_input": "35.69s", "official_source_value": "35.36sec (-20)"},
        },
        {
            "id": "F-53917-08", "severity": "Medium", "status": "needs review",
            "title": "Source registry cannot reproduce the claimed source reads",
            "summary": (f"The registry contains {len(source_doc['sources'])} records with id/name/URL only; {source_records_with_capture_metadata} records include access time, HTTP status, content hash or retained excerpt. Fixture timestamps are repeated at the dataset level, so a reviewer cannot map a particular fact/input to a particular page retrieval. This is an auditability gap, not proof that the pages were not read."),
            "references": [
                {"label": "T496 source registry", "url": refs["source_registry"]},
                {"label": "T496 session report", "url": refs["test_report"]},
            ],
            "official_sources": [],
            "data": {"registry_entries": len(source_doc["sources"]),
                     "entries_with_fetch_metadata": source_records_with_capture_metadata},
        },
        {
            "id": "F-53917-09", "severity": "Medium", "status": "needs review",
            "title": "Originate fair prices are not evidence of available bookmaker odds",
            "summary": ("The T496 pages correctly disclose that prices are zero-vig fair estimates and that no bookmaker quote is copied. However, the predictions render an American price beside the selection and no source confirms an available OLBG/bookmaker offer. The model code also chooses several handicap/total lines to target 0.66 probability, then features an in-band pick from 0.62; this is not a calibrated market edge. Keep the estimate label adjacent to every price and do not present it as a placeable quote."),
            "references": [
                {"label": "T496 line-target implementation", "url": refs["line_search"]},
                {"label": "T496 methodology", "url": "../496eaf02/methodology.html"},
                {"label": "T496 predictions", "url": "../496eaf02/predictions.html"},
            ],
            "official_sources": [],
            "data": {"line_target_probability": 0.66, "featured_pick_floor": 0.62,
                     "bookmaker_quotes_in_source_registry": False},
        },
        {
            "id": "F-53917-10", "severity": "Medium", "status": "needs review",
            "title": "Prediction-level injury/availability coverage is not demonstrated",
            "summary": (f"Only {prediction_injury_mentions} of {len(predictions)} prediction texts contain an explicit injury/availability term. This text search does not prove the remaining matches had injuries; it shows the desk has no per-pick ledger confirming that availability was checked or that no relevant issue was reported. This requirement remains unverified, not cleared."),
            "references": [{"label": "T496 predictions page", "url": "../496eaf02/predictions.html"}],
            "official_sources": [{"label": "NBA 23 Oct 4:15 p.m. ET injury report", "url": official["nba_injury_415"]},
                                 {"label": "EuroLeague current Round 7 injury report", "url": official["el_r7_current"]}],
            "data": {"prediction_texts_with_injury_or_availability_term": prediction_injury_mentions,
                     "prediction_texts": len(predictions)},
        },
        {
            "id": "F-53917-11", "severity": "High", "status": "needs review",
            "title": "Darts Order of Merit inputs are not linked to readable official ranking evidence",
            "summary": (f"T496 reports that PDC Order of Merit figures were cross-checked on multiple outlets because the official PDC rankings page showed a consent wall. The four Darts picks labelled High use player rank/prize inputs, but their source link is the tournament hub, not a captured ranking table; the official rankings page fetched during this audit returned only a consent screen. Keep those rank-derived picks unverified or supply a readable official source and per-value evidence."),
            "references": [
                {"label": "T496 Darts model inputs", "url": github_ref("scripts/se496eaf02_data.py", 38)},
                {"label": "T496 Darts rows", "url": github_ref("scripts/se496eaf02_data.py", line_of("scripts/se496eaf02_data.py", '"id": "DA02"'))},
                {"label": "T496 session note on PDC rankings", "url": github_ref("reports/SESSION_496EAF02.md", 91)},
            ],
            "official_sources": [{"label": "PDC official rankings page (consent screen only in fetch)", "url": official["pdc_rankings"]}],
            "data": {"high_darts_picks": sport_counts["darts"], "rank_inputs_available": True,
                     "ranking_values_readable_from_fetched_official_page": False},
        },
        {
            "id": "F-53917-12", "severity": "Low", "status": "needs review",
            "title": "The discovery date is printed as 2023 in three T496 artifacts",
            "summary": (f"The T496 session report, methodology page and page builder each contain 2023-10-23, although the desk capture and the corresponding source-note say 2026-10-23. This is an editorial date mismatch that can make freshness unclear."),
            "references": [{"label": f"{row['path']}:{row['line']}", "url": row["url"]} for row in date_typos],
            "official_sources": [],
            "data": {"locations": date_typos},
        },
        {
            "id": "F-53917-14", "severity": "Critical", "status": "needs review",
            "title": "Four High EuroLeague picks are for fixtures absent from the official 24 October schedule",
            "summary": ("T496 publishes BK07-BK10 as four High EuroLeague Round 7 fixtures on 24 Oct. EuroLeague’s official calendar places Round 7 on 21-23 Oct and Round 8 on 27-28 Oct; the 22-23 Oct pairings differ from all four T496 listings, and the schedule has no EuroLeague games on 24 Oct. The player-availability text also splices information from different real games: BK07 uses Efes absences for Efes v Besiktas and Fenerbahce availability for Fenerbahce v Olympiacos; BK09 combines Olympiacos absences from its Fenerbahce game with a Bayern v Dubai fixture; BK10 combines Paris information from Paris v Valencia and Partizan information from Partizan v Crvena Zvezda. T496’s cited Round 7 injury URL returns 404. Withdraw all four current picks and rebuild from the official round calendar and per-game injury reports."),
            "references": [
                {"label": "T496 BK07 fixture", "url": github_ref("data/496eaf02/fixtures.json", line_of("data/496eaf02/fixtures.json", '"id": "BK07"'))},
                {"label": "T496 BK08-BK10 fixtures", "url": github_ref("data/496eaf02/fixtures.json", line_of("data/496eaf02/fixtures.json", '"id": "BK08"'))},
                {"label": "T496 BK07-BK10 displayed picks", "url": github_ref("data/496eaf02/matches.csv", line_of("data/496eaf02/matches.csv", "BK07,basketball"))},
                {"label": "T496 EuroLeague Round 7 source record", "url": github_ref("data/496eaf02/sources.json", line_of("data/496eaf02/sources.json", '"id": "el-r7"'))},
            ],
            "official_sources": [
                {"label": "EuroLeague 2026-27 full official schedule PDF", "url": official["el_schedule_pdf"]},
                {"label": "EuroLeague schedule announcement", "url": official["el_schedule_article"]},
                {"label": "EuroLeague current Round 7 injury report", "url": official["el_r7_current"]},
                {"label": "T496-linked EuroLeague injury URL (404)", "url": official["el_r7_t496"]},
            ],
            "data": {"affected_fixture_ids": ["BK07", "BK08", "BK09", "BK10"],
                     "affected_high_picks": 4, "t496_claimed_start_date": "2026-10-24",
                     "official_round7_dates": "2026-10-21/23", "official_round8_dates": "2026-10-27/28"},
        },
        {
            "id": "F-53917-13", "severity": "Informational", "status": "needs review",
            "title": "The target of five High picks is met in only part of the sports list",
            "summary": (f"Only {audit['counts']['sports_with_at_least_five_high_picks']} of 15 sports have at least five picks labeled High; {audit['counts']['sports_with_zero_high_picks']} sports have none. T496 discloses this and avoids inventing picks. Treat it as a coverage gap, not a reason to manufacture selections."),
            "references": [{"label": "T496 high-confidence page", "url": "../496eaf02/high-confidence.html"}],
            "official_sources": [],
            "data": {"by_sport": sport_coverage},
        },
    ]
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Informational": 4}
    finding_defs.sort(key=lambda item: (severity_order[item["severity"]], int(item["id"].rsplit("-", 1)[1])))
    audit["findings"] = finding_defs
    return audit


def write_json(audit: dict) -> None:
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_pages(audit: dict) -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    c = audit["counts"]
    current = html.escape(audit["as_of_utc"])

    metrics = [
        ("T496 fixtures", str(c["fixtures"])),
        ("Picks labelled High", str(c["high_labeled"])),
        ("Strictly >70%", str(c["high_strictly_over_70_percent"])),
        ("Below 70% but labelled High", str(c["high_below_70_percent"])),
        ("Started but upcoming", str(c["upcoming_with_start_at_or_before_capture"])),
        ("Rows with media-only sources", str(c["fixture_rows_using_known_media_sources"])),
    ]
    metric_html = "".join(
        f'<article class="metric"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></article>'
        for label, value in metrics
    )
    cards = "".join(finding_card(item) for item in audit["findings"])
    coverage_rows = "".join(
        f'<tr><th scope="row">{html.escape(row["sport"])}</th>'
        f'<td>{row["high_picks"]}</td><td>{row["target"]}</td><td>{row["shortfall"]}</td>'
        f'<td><a href="{html.escape(row["desk_url"], quote=True)}">T496 category page ↗</a></td></tr>'
        for row in audit["high_picks_by_sport"]
    )
    coverage_table = (
        '<div class="table-wrap"><table><thead><tr><th>Sport</th><th>T496 High</th>'
        '<th>Target</th><th>Gap</th><th>Review</th></tr></thead><tbody>'
        + coverage_rows + '</tbody></table></div>'
    )
    body = f'''<section class="hero">
<p class="eyebrow">Independent audit · captured 23 Oct 2026</p>
<h1>T496E compliance review</h1>
<p>This page audits the merged <a href="../496eaf02/index.html">496eaf02 evening desk</a>. It does not change or recertify that desk, and it publishes no picks. Current official-source checks were fetched only for the targeted findings below; this is not a live re-verification of all 15 sports.</p>
<p class="asof">Audit generated {current}. T496 capture: {html.escape(audit["subject_capture_utc"] or "unknown")}.</p>
</section>
<section class="metrics" aria-label="Audit counts">{metric_html}</section>
<div class="alert"><strong>Critical source-backed issues:</strong> TN04 names a withdrawn player and misattributes a result; four High EuroLeague picks claim Round 7 fixtures on a date absent from the official calendar. See <a href="flagged.html#F-53917-01">F-53917-01</a> and <a href="flagged.html#F-53917-14">F-53917-14</a>.</div>
<section class="panel"><h2>What passes—and what does not</h2>
<ul><li>All {c['predictions']} prediction texts are at least 30 words (minimum {c['predictions_min_words']}) and unique by normalized full text; the T496 test suite passes 21/21.</li>
<li>The High-labelled fair American estimates fall inside the desk’s displayed range; only {c['high_strictly_over_70_percent']} of {c['high_labeled']} exceed 70% (two are exactly 70%, {c['high_below_70_percent']} are below).</li>
<li>Source-link presence is not the same as official authority or claim-level support: media-only fixtures and stale source reads are flagged.</li>
<li>Only {c['sports_with_at_least_five_high_picks']} of 15 sports reach five High-labeled picks; the desk discloses this rather than inventing the rest.</li></ul></section>
<section class="panel"><h2>Flagged findings</h2><div class="finding-list">{cards}</div></section>
<section class="panel"><h2>High-pick coverage by sport</h2><p>Five is the requested target, not a quota to fabricate. This table reports the T496 count; each category row links back to the preserved desk.</p>{coverage_table}</section>
<section class="panel links"><h2>Inspect source artifacts</h2>
<a href="../496eaf02/matches.html">T496 all matches</a><a href="../496eaf02/high-confidence.html">T496 High-confidence list</a><a href="../496eaf02/predictions.html">T496 predictions</a><a href="../496eaf02/flagged.html">T496 flags</a><a href="sources.html">Official pages freshly read for this audit</a><a href="../data/53917f51/audit.json">Audit JSON</a></section>'''
    (SITE / "index.html").write_text(html_page("T496E compliance review", body), encoding="utf-8")

    def flagged_row(item: dict) -> str:
        review_links = item.get("references", []) + item.get("official_sources", [])
        link_markup = " · ".join(
            '<a href="' + html.escape(link["url"], quote=True) + '">' +
            html.escape(link["label"]) + ' ↗</a>'
            for link in review_links
        ) or "No external factual source; see repository reference."
        severity_class = item["severity"].lower().replace(" ", "-")
        return (
            f'<tr id="{html.escape(item["id"])}"><td><strong>{html.escape(item["id"])}</strong>'
            f'<span class="badge {severity_class}">{html.escape(item["severity"])}</span></td>'
            f'<td>{html.escape(item["title"])}<p>{html.escape(item["summary"])}</p></td>'
            f'<td>{link_markup}</td></tr>'
        )

    flagged_rows = "".join(flagged_row(item) for item in audit["findings"])
    flagged_body = f'''<section class="hero"><p class="eyebrow">Public review register · 23 Oct 2026</p><h1>Flagged for Review</h1>
<p>Findings below are about T496E’s own published snapshot. They are not fixes to its files. Every external factual claim here is linked to an official governing body or tournament source; code/policy findings link to the repository.</p></section>
<div class="alert"><strong>Do not rely on TN04 or BK07–BK10.</strong> WTA records contradict TN04; the official EuroLeague calendar contradicts all four 24 October Round 7 fixtures. See F-53917-01 and F-53917-14.</div>
<div class="table-wrap"><table><thead><tr><th>Finding / severity</th><th>Issue and basis</th><th>Manual-review sources</th></tr></thead><tbody>{flagged_rows}</tbody></table></div>
<section class="panel"><h2>Audit limits</h2><p>This is a read-only independent review, not a 15-sport re-harvest. Static checks cover the T496 fixture, market and prediction files. Fresh official pages were fetched for WTA Ningbo, the GBGB Champion Stakes, the Pakistan Cricket Board tri-series, and Limerick GAA. Facts outside those targeted checks remain unverified here.</p><p>See the <a href="../reports/SESSION_53917F51.html">full HTML report</a>, <a href="../reports/SESSION_53917F51.md">Markdown report</a>, and <a href="sources.html">source excerpts</a>.</p></section>'''
    (SITE / "flagged.html").write_text(html_page("Flagged for Review", flagged_body, "findings"), encoding="utf-8")

    evidence = read_json(EVIDENCE_PATH)
    source_rows = "".join(
        f'<tr><td>{html.escape(item["publisher"])}</td><td><a href="{html.escape(item["url"], quote=True)}">{html.escape(item["title"])} ↗</a></td>'
        f'<td>{html.escape(item["read_window_utc"])}</td><td>{html.escape(item["supports"])}<blockquote>{html.escape(item["excerpt"])}</blockquote></td></tr>'
        for item in evidence["sources"]
    )
    source_body = f'''<section class="hero"><p class="eyebrow">Official evidence · fetched through Arena page tools</p><h1>Source reads</h1>
<p>Read window: {html.escape(evidence["read_window_utc"])}. Each link is a league, tour, governing-body or team source. The excerpts state exactly what each page supported in this audit; they do not validate unrelated model inputs.</p></section>
<div class="table-wrap"><table><thead><tr><th>Publisher</th><th>Official page</th><th>Read window UTC</th><th>Claim supported</th></tr></thead><tbody>{source_rows}</tbody></table></div>
<section class="panel"><h2>What these pages do not establish</h2><ul><li>They do not verify the other T496 fixture rows or prices.</li><li>They do not turn T496 fair prices into bookmaker offers.</li><li>They do not certify all prediction prose or injury status.</li></ul></section>'''
    (SITE / "sources.html").write_text(html_page("Official source reads", source_body, "sources"), encoding="utf-8")


def inline_markdown(text: str) -> str:
    # Render the safe inline-Markdown subset used by this audit report.
    held_links: list[tuple[str, str]] = []

    def hold_link(match: re.Match) -> str:
        label, url = match.group(1), match.group(2).strip()
        parsed = urlsplit(url)
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            return match.group(0)
        token = f"AUDITLINKTOKEN{len(held_links)}END"
        markup = '<a href="' + html.escape(url, quote=True) + '">' + inline_markdown(label) + '</a>'
        held_links.append((token, markup))
        return token

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", hold_link, text)
    held_code: list[tuple[str, str]] = []

    def hold_code(match: re.Match) -> str:
        token = f"AUDITCODETOKEN{len(held_code)}END"
        held_code.append((token, "<code>" + html.escape(match.group(1)) + "</code>"))
        return token

    text = re.sub(r"`([^`]+)`", hold_code, text)
    rendered = html.escape(text)
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    for token, markup in held_code + held_links:
        rendered = rendered.replace(token, markup)
    return rendered


def markdown_body(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    blocks: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            i += 1
            continue
        if line.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                item = lines[i].lstrip()[2:]
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                    item += " " + lines[i].strip()
                    i += 1
                items.append("<li>" + inline_markdown(item) + "</li>")
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue
        paragraph = [line]
        i += 1
        while i < len(lines):
            following = lines[i].strip()
            if not following or re.match(r"^#{1,6}\s+", following) or following.startswith("- "):
                break
            paragraph.append(following)
            i += 1
        blocks.append("<p>" + inline_markdown(" ".join(paragraph)) + "</p>")
    return "\n".join(blocks)


def write_report_html() -> None:
    content = markdown_body(REPORT_MD.read_text(encoding="utf-8"))
    REPORT_HTML.parent.mkdir(parents=True, exist_ok=True)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Independent source-linked compliance audit of the T496E sports desk.">
<title>T496E independent audit · 53917f51</title><link rel="stylesheet" href="../53917f51/assets/style.css"></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><a class="brand" href="../53917f51/index.html">OLBG / Independent QA</a>
<nav aria-label="Review pages"><a href="../53917f51/index.html">Dashboard</a><a href="../53917f51/flagged.html">Flagged for Review</a><a href="../53917f51/sources.html">Official source reads</a><a href="SESSION_53917F51.md">Markdown report</a></nav></header>
<main id="main"><article class="panel report">{content}</article></main>
<footer><span>Independent audit · not affiliated with OLBG · no betting advice</span>
<span><a href="../data/53917f51/audit.json">Audit JSON</a> · <a href="../53917f51/index.html">Dashboard</a></span></footer>
</body></html>'''
    REPORT_HTML.write_text(page, encoding="utf-8")

def main() -> None:
    audit = build_audit()
    write_json(audit)
    build_pages(audit)
    write_report_html()
    print(json.dumps({"as_of_utc": audit["as_of_utc"], "counts": audit["counts"],
                      "findings": len(audit["findings"]), "written": [
                          "data/53917f51/audit.json", "53917f51/index.html",
                          "53917f51/flagged.html", "53917f51/sources.html",
                          "reports/SESSION_53917F51.html"]}, indent=2))


if __name__ == "__main__":
    main()
