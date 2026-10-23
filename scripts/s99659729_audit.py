#!/usr/bin/env python3
"""Independent structural/freshness audit of the retained 496eaf02 snapshot.

This script does not fetch network sources or assert that inherited observations remain
current. It records its as-of time, checks the persisted evidence shape and applies the
brief's strict High gate to the inherited recommendations.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "496eaf02"
OUTPUT = ROOT / "data" / "99659729" / "audit.json"
SITE = ROOT / "99659729"
SPORTS = [
    "golf", "volleyball", "rugby-union", "cricket", "snooker", "darts",
    "baseball", "gaelic-sports", "greyhounds", "tennis", "motor-racing",
    "handball", "ice-hockey", "basketball", "rugby-league",
]
BANNED = re.compile(r"\b(?:model|verified)\b", re.IGNORECASE)


def parse_time(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.astimezone(dt.timezone.utc) if result.tzinfo else None
    except (TypeError, ValueError):
        return None


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def audit(as_of: dt.datetime) -> dict:
    fixture_doc = json.loads((INPUT / "fixtures.json").read_text(encoding="utf-8"))
    source_doc = json.loads((INPUT / "sources.json").read_text(encoding="utf-8"))
    pred_doc = json.loads((INPUT / "predictions.json").read_text(encoding="utf-8"))
    fixtures = fixture_doc["fixtures"]
    matches = read_csv(INPUT / "matches.csv")
    markets = read_csv(INPUT / "markets.csv")
    predictions = pred_doc["predictions"]
    captured = parse_time(fixture_doc.get("captured_utc"))
    if captured is None:
        raise ValueError("Snapshot capture timestamp is missing or invalid")
    age_seconds = int((as_of - captured).total_seconds())

    market_ids = {r.get("fixture_id", "") for r in markets}
    fixture_by_id = {f["id"]: f for f in fixtures}
    no_fixture = sorted(i for i in market_ids if i not in fixture_by_id)
    no_source_market = sum(not _https(r.get("source", "")) for r in markets)
    source_missing = []
    for fixture in fixtures:
        if not any(_https(src.get("url", "")) for src in fixture.get("sources", [])):
            source_missing.append(fixture["id"])

    # A row is called a strict-gate match only if it was already labeled high in the
    # source register, its stored probability is strictly above 70%, and its fair
    # American price is within the brief's inclusive -250..+10000 band.
    high_rows = [r for r in matches if r.get("confidence", "").lower() == "high"]
    strict_high = []
    high_outside_gate = []
    for row in high_rows:
        try:
            probability = float(row.get("model_probability", ""))
            american = float(row.get("fair_american", ""))
        except (TypeError, ValueError):
            high_outside_gate.append({"id": row.get("id", ""), "reason": "missing or unparsable probability/price"})
            continue
        if probability > 0.70 and -250 <= american <= 10000:
            fixture = fixture_by_id.get(row.get("id", ""), {})
            source = next((src.get("url", "") for src in fixture.get("sources", []) if _https(src.get("url", ""))), "")
            strict_high.append({
                "id": row.get("id", ""), "sport": row.get("sport", ""),
                "event": row.get("event", ""), "selection": row.get("selection", ""),
                "probability": probability, "fair_american": american,
                "source": source,
            })
        else:
            reason = []
            if probability <= 0.70:
                reason.append("probability is not greater than 70%")
            if not (-250 <= american <= 10000):
                reason.append("fair American price is outside -250..+10000")
            high_outside_gate.append({"id": row.get("id", ""), "reason": "; ".join(reason)})

    elapsed_starts = []
    upcoming_soon = []
    missing_start = []
    for f in fixtures:
        if f.get("state") != "upcoming":
            continue
        start = parse_time(f.get("start_utc"))
        base = {
            "id": f.get("id", ""), "sport": f.get("sport", ""),
            "event": f.get("event", ""), "start_utc": f.get("start_utc", ""),
            "source": next((s.get("url", "") for s in f.get("sources", []) if _https(s.get("url", ""))), ""),
        }
        if start is None:
            missing_start.append(base)
        elif start <= as_of:
            elapsed_starts.append(base)
        elif start <= as_of + dt.timedelta(hours=2):
            upcoming_soon.append(base)

    prediction_lengths = [len(p.get("text", "").split()) for p in predictions]
    prediction_violations = [
        p.get("match_id", "") for p in predictions
        if len(p.get("text", "").split()) < 30 or BANNED.search(p.get("text", ""))
    ]
    prediction_texts = [re.sub(r"\s+", " ", p.get("text", "").strip().lower()) for p in predictions]
    duplicate_prediction_texts = len(prediction_texts) - len(set(prediction_texts))
    prediction_missing_source = [p.get("match_id", "") for p in predictions if not any(_https(u) for u in p.get("sources", []))]

    # Coverage checks must respect market semantics. Set-score outcomes in a best-of-five
    # match have six mutually exclusive final scores (3-0/3-1/3-2 for each side). Podium
    # and top-six driver outcomes are overlapping events, so their probabilities must NOT
    # be tested as if they summed to one.
    market_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in markets:
        market_groups[(r.get("fixture_id", ""), r.get("market", ""))].append(r)
    incomplete_market_coverage = []
    nonexclusive_aggregates = []
    for (fixture_id, market), rows in market_groups.items():
        if market == "Set Score (best of 5)" and len(rows) != 6:
            incomplete_market_coverage.append({
                "fixture_id": fixture_id, "market": market,
                "outcomes_listed": len(rows), "expected_outcomes": 6,
                "listed_selections": [r.get("selection", "") for r in rows],
                "note": "A best-of-five match has six possible terminal scorelines; listed set-score book is incomplete.",
            })
        if market in {"Podium Finish", "Top 6 Finish"}:
            try:
                total = sum(float(r.get("probability", "")) for r in rows)
            except (TypeError, ValueError):
                total = None
            nonexclusive_aggregates.append({
                "fixture_id": fixture_id, "market": market,
                "selections_listed": len(rows),
                "probability_sum_not_a_one-sum_test": round(total, 8) if total is not None else None,
                "note": "Driver outcomes overlap; a sum-to-one check is not valid. Verify driver field coverage and joint consistency against official entry/classification data.",
            })

    sports = sorted({f.get("sport", "") for f in fixtures})
    domains = sorted({urlparse(s.get("url", "")).netloc for s in source_doc.get("sources", []) if s.get("url")})
    return {
        "audit_id": "99659729-independent-freshness-audit",
        "as_of_utc": as_of.isoformat().replace("+00:00", "Z"),
        "source_snapshot_utc": fixture_doc.get("captured_utc", ""),
        "snapshot_age_minutes": round(age_seconds / 60, 2),
        "live_official_refresh_performed": False,
        "scope": SPORTS,
        "counts": {
            "fixtures": len(fixtures), "sports_present": len(sports), "sports": sports,
            "listed_upcoming": sum(f.get("state") == "upcoming" for f in fixtures),
            "fixture_source_missing": len(source_missing), "markets": len(markets),
            "market_rows_without_https_source": no_source_market,
            "market_rows_with_unknown_fixture": len(no_fixture),
            "predictions": len(predictions), "high_labeled_rows": len(high_rows),
            "strict_high_gate_rows": len(strict_high),
            "high_labeled_rows_failing_strict_gate": len(high_outside_gate),
            "starts_elapsed_but_still_labeled_upcoming": len(elapsed_starts),
            "upcoming_starts_within_two_hours": len(upcoming_soon),
            "upcoming_rows_without_exact_start": len(missing_start),
            "incomplete_best_of_five_score_books": len(incomplete_market_coverage),
            "nonexclusive_driver_markets_flagged_for_joint_consistency": len(nonexclusive_aggregates),
        },
        "official_source_domains_listed_in_snapshot": domains,
        "findings": {
            "fixture_source_missing_ids": source_missing,
            "market_fixture_id_orphans": no_fixture,
            "market_source_missing_count": no_source_market,
            "high_labels_failing_strict_gate": high_outside_gate,
            "strict_high_gate_rows": strict_high,
            "elapsed_start_rows": elapsed_starts,
            "starts_within_two_hours": upcoming_soon,
            "missing_exact_start_rows": missing_start,
            "incomplete_best_of_five_score_books": incomplete_market_coverage,
            "nonexclusive_driver_markets": nonexclusive_aggregates,
            "prediction_prose_violations": prediction_violations,
            "duplicate_prediction_text_count": duplicate_prediction_texts,
            "prediction_source_missing_ids": prediction_missing_source,
        },
        "interpretation": [
            "This is a structural audit of retained files, not a new live OLBG or governing-body harvest.",
            "Source URLs are preserved for manual review; link presence does not mean this audit re-fetched or re-confirmed the linked page.",
            "A scheduled start at or before the audit timestamp is not a claim about the result or actual start; pre-match recommendations must be withheld pending a fresh official status check.",
            "Only rows meeting probability > 0.70 AND fair American odds -250..+10000 are counted as strict-gate High; all other inherited High labels are flagged for review.",
        ],
    }


def _https(value: str) -> bool:
    parsed = urlparse(value or "")
    return parsed.scheme == "https" and bool(parsed.netloc)


def write_site(data: dict) -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    (OUTPUT.parent).mkdir(parents=True, exist_ok=True)
    (OUTPUT).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    fixture_doc = json.loads((INPUT / "fixtures.json").read_text(encoding="utf-8"))
    fixtures = fixture_doc["fixtures"]
    match_rows = {r.get("id", ""): r for r in read_csv(INPUT / "matches.csv")}
    styles = """<style>:root{color-scheme:light;--ink:#172b3a;--muted:#647789;--line:#dce5eb;--blue:#176b87;--bg:#f3f7f9;--red:#a4362c;--amber:#855a08}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}header{background:#102c3e;color:white;padding:26px max(5vw,20px)}header h1{margin:0 0 5px;font-size:26px}header p{margin:0;color:#c6d9e4}.wrap{max-width:1250px;margin:24px auto;padding:0 18px}.nav{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 18px}.nav a{color:#075e78;font-weight:650;text-decoration:none}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:18px 0}.card,.panel{background:white;border:1px solid var(--line);border-radius:10px;padding:16px}.card strong{display:block;font-size:25px}.card span,.muted{color:var(--muted);font-size:13px}.warning{border-left:4px solid #bd5c39;background:#fff7f1;padding:14px;margin:16px 0}.note{border-left:4px solid var(--blue);background:#eff8fb;padding:14px;margin:16px 0}table{width:100%;border-collapse:collapse;background:white;font-size:13px}th,td{padding:9px 10px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}th{background:#eaf1f5;position:sticky;top:0}td a{color:#075e78}.scroll{overflow:auto;max-height:75vh;border:1px solid var(--line);border-radius:8px}h2{margin-top:24px}footer{color:var(--muted);font-size:12px;margin:24px 0} .badge{display:inline-block;padding:2px 7px;border-radius:10px;background:#eef2f5}.bad{color:var(--red);font-weight:700}.warn{color:var(--amber);font-weight:700}</style>"""

    def page(title: str, body: str, filename: str) -> None:
        nav = '<nav class="nav"><a href="index.html">Overview</a><a href="matches.html">Fixture audit</a><a href="flagged.html">Flagged for review</a><a href="../reports/SESSION_99659729.md">Audit report</a><a href="../496eaf02/index.html">Source desk (20:30Z snapshot)</a></nav>'
        doc = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · OLBG Audit</title>{styles}</head><body><header><h1>{html.escape(title)}</h1><p>Independent retained-evidence review · as of {html.escape(data["as_of_utc"])}</p></header><main class="wrap">{nav}{body}<footer>Built from repository snapshot files only. No live sports-source refresh was performed for this audit. Follow official links and re-check event status before using any pre-match information.</footer></main></body></html>'
        (SITE / filename).write_text(doc, encoding="utf-8")

    c = data["counts"]
    finding = data["findings"]
    high_outside_rows = "".join(f'<tr><td>{html.escape(x["id"])}</td><td>{html.escape(x["reason"])}</td></tr>' for x in finding["high_labels_failing_strict_gate"])
    strict_rows = "".join(f'<tr><td>{html.escape(x["sport"])}</td><td>{html.escape(x["event"])}</td><td>{html.escape(x["selection"])}</td><td>{x["probability"]:.1%}</td><td>{x["fair_american"]:+.0f}</td><td><a href="{html.escape(x["source"], quote=True)}" rel="noopener">official source link</a></td></tr>' for x in finding["strict_high_gate_rows"])
    body = f'''<section class="warning"><strong>Important:</strong> this is not a live fixtures or betting feed. The latest retained snapshot was captured at {html.escape(data["source_snapshot_utc"])}. This audit did not fetch OLBG or any sports body's current page. Do not treat inherited selections as currently actionable without re-checking the official event status and market.</section>
<div class="cards"><div class="card"><strong>{c["fixtures"]}</strong><span>fixture listings · {c["sports_present"]}/15 listed sports</span></div><div class="card"><strong>{c["markets"]}</strong><span>originated market outcomes</span></div><div class="card"><strong>{c["high_labeled_rows"]}</strong><span>inherited High labels</span></div><div class="card"><strong>{c["strict_high_gate_rows"]}</strong><span>pass strict >70% + odds gate</span></div><div class="card"><strong>{c["starts_elapsed_but_still_labeled_upcoming"]}</strong><span>scheduled starts elapsed but status remains upcoming</span></div><div class="card"><strong>{data["snapshot_age_minutes"]:.0f} min</strong><span>snapshot age at audit time</span></div></div>
<section class="panel"><h2>Executive review</h2><p>The inherited desk labels {c["high_labeled_rows"]} selections High. Under the brief's explicit rule—probability strictly above 70% and fair American odds from −250 through +10000—only <strong>{c["strict_high_gate_rows"]}</strong> pass from retained line data. The remaining {c["high_labeled_rows_failing_strict_gate"]} High labels fail at least one gate and should not be presented as qualifying high-confidence picks.</p><p>There are {c["starts_elapsed_but_still_labeled_upcoming"]} event(s) whose stored scheduled start precedes this audit timestamp while the retained fixture row still says “upcoming.” The audit does not infer a result; it recommends withholding the pre-match pick pending a current official status check.</p><p>All {c["fixtures"]} retained fixture entries have an HTTPS source URL: {c["fixture_source_missing"]} missing source links. Link presence is not fresh confirmation.</p></section>
<h2>Strict-gate rows in the retained data</h2><div class="scroll"><table><thead><tr><th>Sport</th><th>Event</th><th>Selection</th><th>Probability</th><th>Fair price</th><th>Source</th></tr></thead><tbody>{strict_rows or '<tr><td colspan="6">No rows passed.</td></tr>'}</tbody></table></div>
<h2>Quality checks</h2><ul><li>{c["market_rows_without_https_source"]} market rows without an HTTPS source URL.</li><li>{c["market_rows_with_unknown_fixture"]} market rows reference an unknown fixture.</li><li>{c["incomplete_best_of_five_score_books"]} best-of-five set-score books list fewer than all six possible final scorelines.</li><li>{c["nonexclusive_driver_markets_flagged_for_joint_consistency"]} F1 driver-placement books are non-exclusive and require field/joint-consistency review rather than a sum-to-one test.</li><li>{len(finding["prediction_prose_violations"])} prediction prose violations; {len(finding["prediction_source_missing_ids"])} predictions without a source URL.</li></ul>'''
    page("15-sport desk: freshness & evidence audit", body, "index.html")

    fixture_rows = []
    elapsed = {r["id"] for r in finding["elapsed_start_rows"]}
    soon = {r["id"] for r in finding["starts_within_two_hours"]}
    missing = {r["id"] for r in finding["missing_exact_start_rows"]}
    for f in fixtures:
        row = match_rows.get(f["id"], {})
        source = next((s.get("url", "") for s in f.get("sources", []) if _https(s.get("url", ""))), "")
        if f["id"] in elapsed:
            status = "Scheduled start elapsed; withhold pending official status refresh"
        elif f["id"] in soon:
            status = "Scheduled within two hours; immediate official re-check advised"
        elif f["id"] in missing:
            status = "Exact UTC start unavailable in retained data"
        else:
            status = "Retained status only; no live refresh"
        recommendation = row.get("selection", "") or ""
        conf = row.get("confidence", "") or ""
        probability = row.get("model_probability", "") or ""
        fixture_rows.append(f'<tr><td>{html.escape(f["id"])}</td><td>{html.escape(f.get("sport", ""))}</td><td>{html.escape(f.get("event", ""))}</td><td>{html.escape(f.get("start_utc") or f.get("date") or "")}</td><td>{html.escape(status)}</td><td>{html.escape(conf)}</td><td>{html.escape(recommendation)} {html.escape(probability)}</td><td><a href="{html.escape(source, quote=True)}" rel="noopener">official source</a></td></tr>')
    body = '<section class="note">Rows below link to the official source carried in the saved desk. Those links were not fetched again during this audit. The status column is computed only from the retained UTC timestamp and audit clock.</section><div class="scroll"><table><thead><tr><th>ID</th><th>Sport</th><th>Fixture</th><th>Stored start</th><th>Audit status</th><th>Inherited tier</th><th>Inherited selection / p</th><th>Source</th></tr></thead><tbody>' + "".join(fixture_rows) + '</tbody></table></div>'
    page("Fixture-by-fixture review", body, "matches.html")

    flags = []
    flags.append(("High confidence threshold mismatch", f'{c["high_labeled_rows"]} rows are labeled High, but only {c["strict_high_gate_rows"]} meet probability >70% and fair odds −250..+10000. Review the {c["high_labeled_rows_failing_strict_gate"]} rows below; source confidence labels are not equivalent to the brief\'s stricter gate.', "../496eaf02/matches.html"))
    for r in finding["elapsed_start_rows"]:
        flags.append(("Scheduled start elapsed", f'{r["id"]}: {r["event"]} has stored start {r["start_utc"]}, before the audit time. Result / live status not fetched; withhold any pre-match recommendation until the official source is re-read.', r["source"]))
    for r in finding["starts_within_two_hours"]:
        flags.append(("Upcoming start requires immediate refresh", f'{r["id"]}: {r["event"]} is scheduled for {r["start_utc"]}. This timestamp is inherited and no current status was fetched.', r["source"]))
    flags.append(("Live recertification unavailable in this task", "This audit performed no network fetch of OLBG or official sports sources. Retained URLs are provided for review; no claim is made that fixtures, injuries, form, or prices remain current.", "../496eaf02/sources.html"))
    flagrows = "".join(f'<tr><td>{html.escape(label)}</td><td>{html.escape(text)}</td><td><a href="{html.escape(url, quote=True)}" rel="noopener">review source</a></td></tr>' for label, text, url in flags)
    body = f'<section class="warning"><strong>{len(flags)} review notices.</strong> None are silently repaired by inference. Refresh official sources before resuming pre-match picks.</section><div class="scroll"><table><thead><tr><th>Finding</th><th>Detail</th><th>Review</th></tr></thead><tbody>{flagrows}</tbody></table></div><h2>Inherited High labels outside the strict gate</h2><div class="scroll"><table><thead><tr><th>Fixture ID</th><th>Reason</th></tr></thead><tbody>{high_outside_rows}</tbody></table></div>'
    page("Flagged for review", body, "flagged.html")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", help="Fixed UTC ISO timestamp for reproducible audit, e.g. 2026-10-23T21:26:46Z")
    args = parser.parse_args()
    if args.as_of:
        as_of = parse_time(args.as_of)
        if as_of is None:
            raise SystemExit("--as-of must be an ISO-8601 timestamp with timezone")
    else:
        as_of = dt.datetime.now(dt.timezone.utc)
    data = audit(as_of)
    write_site(data)
    print(json.dumps(data["counts"], indent=2))


if __name__ == "__main__":
    main()
