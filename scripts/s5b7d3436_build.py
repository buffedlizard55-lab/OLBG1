#!/usr/bin/env python3
"""Render the isolated /5b7d3436/ static research dashboard."""
from __future__ import annotations

import hashlib
import html
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "5b7d3436"
SITE = ROOT / "5b7d3436"
CAPTURE_AT = "2026-10-23T21:36:17Z"


def load(name, default=None):
    path = DATA / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


FIXTURE_DOC = load("fixtures.json")
SOURCE_DOC = load("sources.json")
DISCOVERY = load("discovery.json")
LINES = load("lines.json")
SUMMARY = load("summary.json")
FLAGGED = load("flagged.json")
PREDICTIONS = load("predictions.json")
VALIDATION = load("validation.json", {"commands": []})
FIXTURES = FIXTURE_DOC["fixtures"]
SOURCES = {s["id"]: s for s in SOURCE_DOC["sources"]}
BOOKS = {b["fixture_id"]: b for b in LINES["books"]}
DISCOVERY_ROWS = {r["sport"]: r for r in DISCOVERY["rows"]}
SPORT_ORDER = FIXTURE_DOC["sports"]
SLUGS = {f["sport"]: f["slug"] for f in FIXTURES}


def e(value):
    return html.escape("" if value is None else str(value), quote=True)


def save_json(name, value):
    (DATA / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def external(url, label, cls=""):
    return f'<a class="{e(cls)}" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)}<span class="sr-only"> (opens in new tab)</span><span aria-hidden="true"> ↗</span></a>'


def source_links(ids, short=False):
    links = []
    for sid in ids:
        s = SOURCES[sid]
        label = s["publisher"] if short else f"{s['publisher']} · {sid}"
        links.append(external(s["url"], label, "source-link"))
    return '<div class="source-stack">' + "".join(links) + "</div>" if links else '<span class="muted">—</span>'


def badge(text, tone="neutral"):
    return f'<span class="badge {e(tone)}">{e(text)}</span>'


def start_text(f):
    if f["start_utc"]:
        base = f["start_utc"].replace("T", " · ").replace(":00Z", " UTC")
        local = f"<small>{e(f['start_local'])}</small>" if f.get("start_local") else ""
        return f'<time datetime="{e(f["start_utc"])}">{e(base)}</time>{local}'
    return f'<span>{e(f.get("start_local") or f.get("date"))}</span><small>UTC not established</small>'


def preference(f, compact=False):
    p = BOOKS[f["id"]]["preferred_winner"]
    if not p:
        return '<span class="muted">—</span><small>Withheld</small>'
    return (f'<span class="price-value"><strong>{e(p["selection"])}</strong>'
            f'<small>{p["probability"]:.2%} · {e(p["american_display"])} · {p["fair_decimal"]:.3f} decimal</small></span>'
            f'<span class="price-value">{badge(p["research_confidence"] + " research", "medium" if p["research_confidence"] == "Medium" else "low")}</span>'
            f'<span class="expired-label" hidden>Research price expired</span>')


def flag_anchor(f):
    return f["id"] + ("-F1" if f["flags"] else "-M1")


NAV = [
    ("index.html", "Overview", "overview"), ("matches.html", "Matches", "matches"),
    ("markets.html", "Markets", "markets"), ("high-confidence.html", "High gate", "high"),
    ("analysis.html", "Analysis", "analysis"), ("discovery.html", "OLBG discovery", "discovery"),
    ("sources.html", "Sources", "sources"), ("flagged.html", "Flagged", "flagged"),
]


def frame(title, body, active="", prefix=""):
    nav = "".join(f'<a href="{prefix}{href}" class="{"active" if key == active else ""}">{e(label)}</a>' for href, label, key in NAV)
    flag_count = SUMMARY["flagged_findings"]
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Fresh 15-sport OLBG discovery and official-source research with explicit unavailable markets, independent fair-line calculations and source-linked review findings.">
<meta name="color-scheme" content="light"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; form-action 'none'; connect-src 'none'">
<title>{e(title)} · OLBG 15-sport desk</title><link rel="stylesheet" href="{prefix}assets/style.css"><noscript><link rel="stylesheet" href="{prefix}assets/nojs.css"></noscript><script defer src="{prefix}assets/app.js"></script>
</head><body data-capture="{CAPTURE_AT}"><a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner"><a class="brand" href="{prefix}index.html" aria-label="OLBG research desk overview"><span class="brand-mark" aria-hidden="true">O/</span><span>OLBG <b>research desk</b><small>SESSION 5B7D3436</small></span></a>
<button class="menu-button" id="menu-button" aria-expanded="false" aria-controls="primary-nav">Menu</button><span class="capture"><i></i> Fresh capture<small>23 Oct 2026 · 21:36 UTC</small></span></div>
<nav id="primary-nav" class="primary-nav" aria-label="Primary navigation">{nav}<a href="{prefix}flagged.html" class="flag-nav">Review <span>{flag_count}</span></a></nav></header>
<main id="main" class="page"><noscript><div class="notice"><strong>Estimates withheld without JavaScript.</strong> Browser-time freshness cannot be checked. Official fixture facts and source links remain available as historical observations.</div></noscript>{body}</main>
<footer class="footer"><div><strong>Independent research. Not affiliated with OLBG.</strong><p>Fair prices are not bookmaker quotes or guarantees. No available wager is asserted. 18+ · Never stake what you cannot afford to lose.</p></div>
<div class="footer-links"><a href="{prefix}methodology.html">Methodology</a><a href="{prefix}predictions.html">Predictions</a><a href="{prefix}sports.html">All 15 sports</a><a href="{prefix}repo-audit.html">Repository audit</a><a href="{prefix}../data/5b7d3436/matches.csv">CSV export</a></div></footer>
</body></html>'''


def hero(eyebrow, title, text, actions=""):
    return f'<section class="hero"><div class="eyebrow">{e(eyebrow)}</div><h1>{e(title)}</h1><p>{e(text)}</p>{actions}</section>'


def kpis(items):
    return '<section class="kpi-grid" aria-label="Release summary">' + "".join(
        f'<div class="kpi"><span>{e(label)}</span><strong>{e(value)}</strong><small>{e(note)}</small></div>' for value, label, note in items) + '</section>'


def fixture_sort(f):
    return (f.get("date") or "9999", f.get("start_utc") or "9999", f["id"])


def market_table(f, detailed=True):
    book = BOOKS[f["id"]]
    if not book["markets"]:
        return ""
    sections = []
    for market in book["markets"]:
        rows = []
        for o in market["outcomes"]:
            rows.append(f'<tr><td><strong>{e(o["selection"])}</strong></td><td>{o["probability"]:.2%}</td><td>{o["fair_decimal"]:.3f}</td><td>{e(o["american_display"])}</td><td>{badge("In band" if o["in_band"] else "Outside band", "green" if o["in_band"] else "neutral")}</td></tr>')
        sections.append(f'<h4>{e(market["label"])}</h4><div class="table-wrap"><table><thead><tr><th scope="col">Selection</th><th scope="col">Fair probability</th><th scope="col">Fair decimal</th><th scope="col">Fair American</th><th scope="col">−250…+10000</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
        if detailed:
            sections.append(f'<p class="fine-print">{e(market["settlement"])}</p>')
    return (f'<div class="price-block" data-price-expires="{e(book["expires_at"])}" data-start="{e(f["start_utc"])}">'
            f'<div class="price-meta price-value"><span>Expected score: {book["expected_home_score"]:.2f} {e(f["home"])} · {book["expected_away_score"]:.2f} {e(f["away"])}</span>'
            f'<span>Price evidence expires {e(book["expires_at"])}</span></div><div class="price-value">{"".join(sections)}</div>'
            f'<p class="expired-label expired-panel" hidden>This experimental price has expired or the event has started. Official fixture facts remain as historical observations.</p></div>')


def build_index():
    tonight = sorted(FIXTURES, key=fixture_sort)[:9]
    rows = []
    for f in tonight:
        rows.append(f'<tr><td>{e(f["id"])}</td><td><a href="sports/{e(f["slug"])}.html">{e(f["sport"])}</a></td><td><strong>{e(f["event"])}</strong><small>{e(f["competition"])}</small></td><td>{start_text(f)}</td><td data-price-expires="{e(BOOKS[f["id"]]["expires_at"])}" data-start="{e(f["start_utc"])}">{preference(f)}</td><td>{source_links(f["source_ids"][:1], True)}</td></tr>')
    cards = []
    for sport in SPORT_ORDER:
        slug = SLUGS[sport]
        fixtures = [f for f in FIXTURES if f["sport"] == sport]
        priced_count = sum(bool(BOOKS[f["id"]]["markets"]) for f in fixtures)
        d = DISCOVERY_ROWS[sport]
        cards.append(f'<a class="sport-card" href="sports/{slug}.html"><div><span class="sport-dot"></span>{badge("Expired sample" if d["event_id"] else "No open listing", "amber")}</div><h3>{e(sport)}</h3><p>{len(fixtures)} official watchlist row{"s" if len(fixtures) != 1 else ""} · {priced_count} priced</p><small>OLBG: {"no tournament/match listing" if d["hub_state"] == "no_tournament_or_matches" else "No tips found"} <span aria-hidden="true">→</span></small></a>')
    body = hero("FRIDAY DESK · 23 OCTOBER 2026", "Evidence before picks.",
                "A fresh 15-sport read of OLBG’s public surface, checked against official schedules and team news. No open OLBG market was established, so no High pick is published.",
                '<div class="hero-actions"><a class="button primary" href="matches.html">Review 20 fixtures</a><a class="button" href="high-confidence.html">Why zero High picks?</a></div>')
    body += '<aside class="alert"><strong>Expired means unavailable.</strong><p>Every displayed selection on all 11 sampled OLBG event pages was labeled Expired. Officially upcoming opponents stay on the watchlist, but those listings are not reopened or treated as available bets.</p><a href="discovery.html">Inspect the discovery ledger →</a></aside>'
    body += kpis([
        ("15 / 15", "Sports checked", "Exact requested brief"),
        (str(SUMMARY["fixtures"]), "Official watchlist rows", f'{SUMMARY["upcoming"]} upcoming · {SUMMARY["in_progress"]} in progress'),
        (str(SUMMARY["priced_fixtures"]), "Experimentally priced", f'{SUMMARY["originated_markets"]} two-way markets'),
        ("0", "Open OLBG markets", "11/11 event samples expired"),
        ("0", "High picks released", "No quota filling"),
        (str(SUMMARY["flagged_findings"]), "Review findings", "Timing, access and pricing gaps"),
    ])
    body += '<section class="section"><div class="section-head"><div><span class="eyebrow">EXECUTIVE SUMMARY</span><h2>Tonight and next up</h2></div><a href="matches.html">Full match list →</a></div><p>Start values are shown exactly as UTC or as the official local/date display when conversion is unsupported. A blank selection means pricing was withheld.</p><div class="table-wrap"><table><thead><tr><th scope="col">ID</th><th scope="col">Sport</th><th scope="col">Event</th><th scope="col">Official start</th><th scope="col">Research preference</th><th scope="col">Official source</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div></section>'
    body += '<section class="section"><div class="section-head"><div><span class="eyebrow">COVERAGE</span><h2>All 15 requested sports</h2></div><a href="sports.html">Coverage matrix →</a></div><div class="sports-grid">' + "".join(cards) + '</div></section>'
    body += '''<section class="three-col section"><article><span class="step">01</span><h3>Discover</h3><p>Public OLBG hubs, competition routes and event pages establish interface state only. Community tip counts never become probabilities.</p></article><article><span class="step">02</span><h3>Check officially</h3><p>League, governing-body, tour and team pages supply the participants, schedule, statistics and availability statements linked on every row.</p></article><article><span class="step">03</span><h3>Price—or withhold</h3><p>Only compatible numerical inputs produce fair lines. Missing runners, times, form or availability stay blank and appear in the review register.</p></article></section>'''
    write(SITE / "index.html", frame("Overview", body, "overview"))


def build_matches():
    rows = []
    for f in sorted(FIXTURES, key=fixture_sort):
        p = BOOKS[f["id"]]["preferred_winner"]
        rows.append(f'<tr id="{e(f["id"])}"><td>{e(f["id"])}</td><td><a href="sports/{e(f["slug"])}.html">{e(f["sport"])}</a><small>{e(f["competition"])}</small></td><td><strong>{e(f["event"])}</strong><small>{e(f["home"] or "Event field")}{" v " + e(f["away"]) if f["away"] else ""}</small></td><td>{start_text(f)}</td><td>{e(f["venue"])}</td><td>{badge(f["olbg_state"].replace("_", " "), "amber")}</td><td data-price-expires="{e(BOOKS[f["id"]]["expires_at"])}" data-start="{e(f["start_utc"])}">{preference(f)}</td><td>{source_links(f["source_ids"], True)}</td><td><a href="flagged.html#{e(flag_anchor(f))}">{len(f["flags"]) + len(f["market_gaps"])} notes</a></td></tr>')
    body = hero("OFFICIAL WATCHLIST", "Matches and event rows",
                "Twenty fresh official-source rows across the exact 15-sport brief. This is not represented as an exhaustive enumeration of every global fixture or every expired OLBG page.",
                '<div class="hero-actions"><a class="button" href="../data/5b7d3436/matches.csv" download>Download matches.csv</a><a class="button" href="../data/5b7d3436/fixtures.json" download>Fixture JSON</a></div>')
    body += '<aside class="notice"><strong>Reading the blanks.</strong> A research preference is an experimental fair-line output, not an available OLBG wager. “Withheld” means the necessary compatible inputs were not captured.</aside>'
    body += '<div class="table-wrap"><table class="dense"><thead><tr><th scope="col">ID</th><th scope="col">Sport / competition</th><th scope="col">Event</th><th scope="col">Start</th><th scope="col">Venue</th><th scope="col">OLBG state</th><th scope="col">Research preference</th><th scope="col">Official sources</th><th scope="col">Review</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>'
    write(SITE / "matches.html", frame("Matches", body, "matches"))


def build_sports():
    cards = []
    for sport in SPORT_ORDER:
        slug = SLUGS[sport]
        fs = [f for f in FIXTURES if f["sport"] == sport]
        d = DISCOVERY_ROWS[sport]
        cards.append(f'<a class="coverage-card" href="sports/{slug}.html"><div class="coverage-top"><h2>{e(sport)}</h2><span>OLBG {d["olbg_id"]}</span></div><p>{len(fs)} official row{"s" if len(fs) != 1 else ""} · {sum(bool(BOOKS[f["id"]]["markets"]) for f in fs)} priced · 0 High released</p><div class="coverage-state"><span>{e(d["hub_state"].replace("_", " "))}</span><span>{e(d["event_state"].replace("_", " "))}</span></div><b>Open category →</b></a>')
    body = hero("CATEGORY INDEX", "Fifteen sports, no silent substitutions",
                "Gaelic Football is the OLBG discovery route for this brief’s Gaelic Sports category. Australian Rules and eSports are outside scope and are not included.")
    body += '<div class="coverage-grid">' + "".join(cards) + '</div>'
    write(SITE / "sports.html", frame("Sports", body, "matches"))
    for sport in SPORT_ORDER:
        slug = SLUGS[sport]
        fs = [f for f in FIXTURES if f["sport"] == sport]
        d = DISCOVERY_ROWS[sport]
        subroutes = [r for r in DISCOVERY["subroutes"] if r["sport"] == sport]
        discovery_html = f'<div class="discovery-strip"><div><span>OLBG hub</span><strong>{e(d["hub_state"].replace("_", " "))}</strong>{external(d["hub_url"], "Open public hub")}</div><div><span>Sampled event</span><strong>{e(d["event_state"])}</strong>{external(d["event_url"], "Event " + d["event_id"]) if d["event_url"] else "<small>No event-page sample</small>"}</div><div><span>Release state</span><strong>0 open markets · 0 High</strong><small>Capture-time interface observation</small></div></div>'
        if subroutes:
            discovery_html += '<div class="inline-links">' + "".join(external(r["url"], f'{r["sport"]} subroute · No tips found') for r in subroutes) + '</div>'
        parts = [hero(f'{sport.upper()} · OLBG {d["olbg_id"]}', sport,
                      f'{len(fs)} official watchlist row{"s" if len(fs) != 1 else ""}. Expired OLBG samples and missing inputs remain visible; no market availability is inferred from the official schedule.')]
        parts.append(discovery_html)
        for f in fs:
            facts = "".join(f'<li>{e(x)}</li>' for x in f["facts"])
            availability = "".join(f'<li>{e(x)}</li>' for x in f["availability"])
            flags = "".join(f'<li>{e(x)}</li>' for x in f["flags"] + f["market_gaps"])
            parts.append(f'''<article class="fixture-card" id="{e(f["id"])}"><div class="fixture-head"><div><span class="eyebrow">{e(f["id"])} · {e(f["competition"])}</span><h2>{e(f["event"])}</h2></div>{badge(f["state"].replace("_", " "), "green" if f["state"] == "upcoming" else "amber")}</div>
<div class="fixture-meta"><div><span>Official start</span>{start_text(f)}</div><div><span>Venue</span><strong>{e(f["venue"])}</strong></div><div><span>OLBG listing</span><strong>{e(f["olbg_state"].replace("_", " "))}</strong></div></div>
<div class="two-col"><section><h3>Official facts</h3><ul>{facts or '<li class="muted">No additional factual note captured.</li>'}</ul>{f'<h3>Availability / team news</h3><ul>{availability}</ul>' if availability else ''}</section><section><h3>Source trail</h3>{source_links(f["source_ids"])}<h3>Review notes</h3><ul class="review-list">{flags}</ul></section></div>
{market_table(f)}</article>''')
        parts.append(f'<p class="back-link"><a href="../sports.html">← All sports</a> · <a href="../flagged.html#{e(flag_anchor(fs[0]))}">Review findings for {e(sport)}</a></p>')
        write(SITE / "sports" / f"{slug}.html", frame(sport, "".join(parts), "matches", "../"))


def build_markets():
    parts = [hero("INDEPENDENT FAIR LINES", "Experimental market sheet",
                  "Twenty-one two-way markets across seven NHL/MLB fixtures. Each outcome pair is zero-vig; fair prices are derived from official team totals and disclosed assumptions, not copied odds.",
                  '<div class="hero-actions"><a class="button" href="../data/5b7d3436/markets.csv" download>Download markets.csv</a><a class="button" href="methodology.html">Read the calculation</a></div>'),
             '<aside class="alert"><strong>Not available bets.</strong> No open OLBG market or bookmaker quote was established. Browser-time checks hide prices after their evidence expiry or event start.</aside>']
    for f in FIXTURES:
        book = BOOKS[f["id"]]
        if not book["markets"]:
            continue
        parts.append(f'<section class="market-card" id="market-{e(f["id"])}"><div class="section-head"><div><span class="eyebrow">{e(f["id"])} · {e(f["sport"])}</span><h2>{e(f["event"])}</h2><p>{start_text(f)}</p></div><div>{source_links(f["source_ids"], True)}</div></div>{market_table(f)}<p class="fine-print"><strong>Additional markets investigated but withheld:</strong> {e(" ".join(f["market_gaps"]))}</p></section>')
    gaps = []
    for f in FIXTURES:
        if not BOOKS[f["id"]]["markets"]:
            gaps.append(f'<tr><td>{e(f["id"])}</td><td><a href="sports/{e(f["slug"])}.html">{e(f["sport"])}</a></td><td>{e(f["event"])}</td><td>{e(" ".join(f["market_gaps"]))}</td><td>{source_links(f["source_ids"][:1], True)}</td></tr>')
    parts.append('<section class="section"><div class="section-head"><div><span class="eyebrow">WITHHELD BOOKS</span><h2>No price without a defensible input</h2></div></div><div class="table-wrap"><table><thead><tr><th scope="col">ID</th><th scope="col">Sport</th><th scope="col">Event</th><th scope="col">Reason</th><th scope="col">Official source</th></tr></thead><tbody>' + "".join(gaps) + '</tbody></table></div></section>')
    write(SITE / "markets.html", frame("Markets", "".join(parts), "markets"))


def build_high():
    rows = []
    for f in FIXTURES:
        p = BOOKS[f["id"]]["preferred_winner"]
        if not p:
            continue
        yn = lambda value: badge("Pass" if value else "Fail", "green" if value else "red")
        rows.append(f'<tr data-price-expires="{e(BOOKS[f["id"]]["expires_at"])}" data-start="{e(f["start_utc"])}"><td>{e(f["id"])}</td><td>{e(f["event"])}</td><td><span class="price-value">{e(p["selection"])}<small>{p["research_confidence"]} research only</small></span><span class="expired-label" hidden>Expired</span></td><td><span class="price-value">{p["probability"]:.2%}</span></td><td><span class="price-value">{e(p["american_display"])}</span></td><td>{yn(p["probability_gate"])}</td><td>{yn(p["band_gate"])}</td><td>{yn(p["open_olbg_market"])}</td><td>{yn(p["availability_complete"])}</td><td>{badge("Not publishable", "red")}</td></tr>')
    body = hero("STRICT RELEASE GATE", "Zero High picks—and why",
                "The daily target is up to five strongest High picks per sport, never a quota to manufacture. A High release requires every gate below, plus original matchup prose of at least 30 words.")
    body += kpis([("0", "High picks", "Across all 15 sports"), ("0", "Open OLBG markets", "Hard release blocker"), ("7", "Winner evaluations", "Research preferences only"), ("0", "Prediction articles", "No prose manufactured")])
    body += '''<section class="gate-grid"><article><span>1</span><h3>Open market</h3><p>A current, non-expired OLBG market must be established at capture.</p></article><article><span>2</span><h3>Official evidence</h3><p>Participants, schedule and relevant form/statistics require official links.</p></article><article><span>3</span><h3>Availability</h3><p>Relevant injury/availability information must be officially supported and complete enough for release.</p></article><article><span>4</span><h3>Price window</h3><p>Unrounded probability must exceed 70% and fair American odds must remain inside −250 through +10000.</p></article></section>'''
    body += '<section class="section"><div class="section-head"><div><span class="eyebrow">GATE AUDIT</span><h2>Why the seven research preferences stay unpublished</h2></div></div><p>Boston illustrates the independent band rule: its raw winner probability is above 70%, but the resulting fair price is shorter than −250. Every row also fails open-market and complete-availability gates.</p><div class="table-wrap"><table class="dense"><thead><tr><th scope="col">ID</th><th scope="col">Event</th><th scope="col">Preference</th><th scope="col">Probability</th><th scope="col">Fair American</th><th scope="col">&gt;70%</th><th scope="col">Band</th><th scope="col">Open</th><th scope="col">Availability</th><th scope="col">Release</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div></section>'
    write(SITE / "high-confidence.html", frame("High-confidence gate", body, "high"))


def build_predictions():
    body = hero("PUBLICATION REGISTER", "No prediction articles published",
                PREDICTIONS["reason"])
    body += '''<section class="empty-state"><span aria-hidden="true">0</span><h2>The prose gate stays closed</h2><p>A future High selection would need a clear betting selection, both participants, current form, relevant recent history or statistics, officially supported availability, and at least 30 unique natural words. Research-only fair lines on the market sheet are not relabeled as predictions.</p><div class="hero-actions"><a class="button primary" href="high-confidence.html">Inspect the release gate</a><a class="button" href="analysis.html">Read analysis</a></div></section>'''
    write(SITE / "predictions.html", frame("Predictions", body, "high"))


def build_analysis():
    constant_rows = "".join(f'<tr><td><code>{e(k)}</code></td><td>{e(v)}</td></tr>' for k, v in LINES["constants"].items())
    calc_rows = []
    for f in FIXTURES:
        b = BOOKS[f["id"]]
        if not b["markets"]:
            continue
        p = b["preferred_winner"]
        calc_rows.append(f'<tr data-price-expires="{e(b["expires_at"])}" data-start="{e(f["start_utc"])}"><td>{e(f["id"])}</td><td>{e(f["event"])}</td><td><span class="price-value">{b["expected_home_score"]:.3f}–{b["expected_away_score"]:.3f}</span></td><td><span class="price-value">{e(p["selection"])}</span></td><td><span class="price-value">{p["probability"]:.2%}</span></td><td><span class="price-value">{e(p["american_display"])}</span></td><td>{source_links(f["source_ids"], True)}</td></tr>')
    body = hero("ANALYSIS & FINDINGS", "What the evidence supports",
                "The central finding is an availability finding, not a claim that sport has stopped: OLBG’s sampled markets were expired while official competitions still list upcoming events.")
    body += '''<section class="findings-grid"><article><span class="finding-number">11 / 11</span><h2>Expired event samples</h2><p>Future-dated official opponents do not alter the captured Expired label. No current OLBG price or tip availability is inferred.</p></article><article><span class="finding-number">13 / 20</span><h2>Fixture rows unpriced</h2><p>Most categories lack a compatible current numerical package. Their official events remain visible with every pricing gap explained.</p></article><article><span class="finding-number">2 / 15</span><h2>Sports with fair lines</h2><p>NHL standings and MLB regular-season totals support reproducible experimental calculations. They do not establish a betting edge.</p></article></section>'''
    body += '<section class="section"><div class="section-head"><div><span class="eyebrow">CALCULATION OUTPUT</span><h2>Expected scores and winner preferences</h2></div><a href="markets.html">All markets →</a></div><div class="table-wrap"><table><thead><tr><th scope="col">ID</th><th scope="col">Event</th><th scope="col">Expected score</th><th scope="col">Preference</th><th scope="col">Probability</th><th scope="col">Fair American</th><th scope="col">Inputs</th></tr></thead><tbody>' + "".join(calc_rows) + '</tbody></table></div></section>'
    body += '''<section class="two-col section"><article class="panel"><h2>Material limitations</h2><ul><li>NHL starting goalies and complete availability were not captured. Montréal’s confirmed Suzuki absence is disclosed but receives no invented numerical adjustment.</li><li>MLB probable pitchers are named, but pitcher statistics are absent. Games 1 and 2 therefore share a team-total baseline and are not presented as pitcher-specific handicaps.</li><li>No independent price is compared with a real bookmaker quote. A fair probability alone does not demonstrate value.</li><li>Small early-season NHL samples are shrunk, not treated as settled team strength.</li></ul></article><article class="panel"><h2>Timing and source irregularities</h2><ul><li>Cricket’s source-displayed “Your time” has no established zone.</li><li>Snooker’s direct and indexed official displays conflict.</li><li>Handball’s newer preview conflicts with older schedule snippets.</li><li>The volleyball request crossed league domains; its explicit fixture text is retained with a routing flag.</li><li>Exact per-URL network times were unavailable, so the registry uses a common post-read registration timestamp.</li></ul></article></section>'''
    body += '<section class="section"><h2>Disclosed constants</h2><p>' + e(LINES["method"]) + '</p><div class="table-wrap"><table><thead><tr><th scope="col">Constant</th><th scope="col">Value</th></tr></thead><tbody>' + constant_rows + '</tbody></table></div></section>'
    write(SITE / "analysis.html", frame("Analysis", body, "analysis"))


def build_sources():
    rows = []
    for s in SOURCE_DOC["sources"]:
        kind = "official" if s["official"] else "discovery"
        rows.append(f'<tr data-kind="{kind}" data-search="{e((s["publisher"] + " " + s["takeaway"] + " " + s["url"]).lower())}"><td>{badge("Official" if s["official"] else "Discovery", "green" if s["official"] else "neutral")}</td><td><strong>{e(s["publisher"])}</strong><small>{e(s["id"])}</small></td><td>{e(s["method"])}<small>{e(s["registered_at"])}</small></td><td>{e(s["takeaway"])}</td><td>{external(s["url"], "Open source")}</td></tr>')
    body = hero("SOURCE REGISTER", "Every read has a trail",
                "Fifty-nine source records distinguish official evidence from OLBG discovery. Registration time is not misrepresented as an exact network timestamp or a publisher update time.",
                '<div class="hero-actions"><a class="button" href="../data/5b7d3436/sources.json" download>Download sources.json</a></div>')
    body += '''<div class="filter-bar" data-filter-group="kind"><label>Search sources<input type="search" id="source-search" placeholder="Publisher, fact or URL" aria-label="Search sources"></label><div class="filter-buttons" aria-label="Filter source type"><button class="active" data-filter="all">All</button><button data-filter="official">Official</button><button data-filter="discovery">Discovery</button></div><span id="filter-count" role="status"></span></div>'''
    body += '<div class="table-wrap"><table id="filter-table" class="dense"><thead><tr><th scope="col">Type</th><th scope="col">Publisher / ID</th><th scope="col">Method / registered</th><th scope="col">Takeaway used</th><th scope="col">Link</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>'
    write(SITE / "sources.html", frame("Sources", body, "sources"))


def build_discovery():
    rows = []
    for d in DISCOVERY["rows"]:
        rows.append(f'<tr><td><a href="sports/{e(d["slug"])}.html">{e(d["sport"])}</a></td><td>{d["olbg_id"]}</td><td>{external(d["hub_url"], "Public hub")}</td><td>{badge(d["hub_state"].replace("_", " "), "amber")}</td><td>{external(d["event_url"], d["event_id"]) if d["event_url"] else "—"}</td><td>{badge(d["event_state"], "red" if d["event_state"] == "expired" else "neutral")}</td><td>0</td></tr>')
    subroutes = "".join(f'<tr><td>{e(r["sport"])}</td><td>{external(r["url"], r["url"])}</td><td>{badge(r["state"].replace("_", " "), "amber")}</td></tr>' for r in DISCOVERY["subroutes"])
    body = hero("PUBLIC SURFACE ONLY", "OLBG discovery, separated from proof",
                "The public route map was checked without private APIs, member routes or access-control workarounds. OLBG supplies discovery leads; official publishers supply fixture facts.")
    body += '<aside class="alert"><strong>Main page:</strong> “No tips found” and “No tournaments tips found.” This capture state does not prove that no sporting fixtures exist.</aside>'
    body += '<section class="section"><h2>Public route semantics</h2><pre><code>/betting-tips/{sport}/{sport_id}\n/betting-tips/{sport}/{competition}/{sport_id}\n…?event_id={event_id}</code></pre><p>Sport IDs and slugs come from public hubs/sitemap leads. Event labels are not official verification. Tip counts and malformed popularity percentages are excluded from probabilities.</p><div class="inline-links">' + external("https://www.olbg.com/robots.txt", "robots.txt") + external("https://www.olbg.com/sitemap-betting-tips.xml", "Public sitemap") + external(DISCOVERY["main_url"], "Main all-sports page") + '</div></section>'
    body += '<section class="section"><div class="section-head"><div><span class="eyebrow">15 SPORT HUBS</span><h2>Capture-time discovery ledger</h2></div></div><div class="table-wrap"><table><thead><tr><th scope="col">Sport</th><th scope="col">ID</th><th scope="col">Hub</th><th scope="col">Hub state</th><th scope="col">Event sample</th><th scope="col">Event state</th><th scope="col">Open markets</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div></section>'
    body += '<section class="section"><h2>Five competition subroutes</h2><div class="table-wrap"><table><thead><tr><th scope="col">Sport</th><th scope="col">URL</th><th scope="col">State</th></tr></thead><tbody>' + subroutes + '</tbody></table></div></section>'
    write(SITE / "discovery.html", frame("OLBG discovery", body, "discovery"))


def build_flagged():
    rows = []
    for f in FLAGGED["flags"]:
        anchor = f["id"]
        rows.append(f'<tr id="{e(anchor)}" data-kind="{e(f["severity"])}" data-search="{e((f["title"] + " " + f["detail"]).lower())}"><td>{e(f["id"])}</td><td>{badge(f["severity"], "red" if f["severity"] == "blocking" else "amber" if f["severity"] in {"fixture", "pricing"} else "neutral")}</td><td><strong>{e(f["title"])}</strong><p>{e(f["detail"])}</p></td><td>{source_links(f["source_ids"], True)}</td></tr>')
    body = hero("FLAGGED FOR REVIEW", "Unresolved does not mean hidden",
                "Sixty-four findings cover unavailable markets, source conflicts, missing fields, retrieval limitations and withheld prices. These items do not block the static release; broken validation or deployment would.")
    body += '''<div class="filter-bar" data-filter-group="kind"><label>Search findings<input type="search" id="source-search" placeholder="Fixture, field or issue" aria-label="Search findings"></label><div class="filter-buttons" aria-label="Filter finding type"><button class="active" data-filter="all">All</button><button data-filter="blocking">Blocking</button><button data-filter="fixture">Fixture</button><button data-filter="pricing">Pricing</button><button data-filter="retrieval">Retrieval</button><button data-filter="audit">Audit</button></div><span id="filter-count" role="status"></span></div>'''
    body += '<div class="table-wrap"><table id="filter-table" class="dense"><thead><tr><th scope="col">ID</th><th scope="col">Type</th><th scope="col">Finding</th><th scope="col">Related sources</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>'
    write(SITE / "flagged.html", frame("Flagged for review", body, "flagged"))


def build_methodology():
    constants = "".join(f'<tr><td><code>{e(k)}</code></td><td>{e(v)}</td></tr>' for k, v in LINES["constants"].items())
    body = hero("METHODOLOGY", "Reproducible, conservative and expire-aware",
                "Run the data, lines and build scripts in that order. The generated site reads only committed local JSON; the browser makes no API calls.")
    body += f'''<section class="section prose"><h2>1 · Evidence boundary</h2><p>OLBG is a discovery surface. Official league, governing-body, tour, promoter and team pages are the only accepted sources for fixture facts, statistics and availability. Historical desk claims are leads, not fresh evidence. Unsupported fields remain blank and create review entries.</p><h2>2 · Fair-line calculation</h2><p>{e(LINES["method"])}</p><pre><code>shrunk_rate = (official_total + 5 × league_assumption) / (games + 5)
expected_home = league_rate × home_attack × away_allowance × home_factor
expected_away = league_rate × away_attack × home_allowance × away_factor
fair_decimal = 1 / probability</code></pre><p>The league-rate and home/away factors are modeling assumptions, not official facts. Every two-way market is zero-vig. Calculations use unrounded probabilities for gates and display rounded values afterward.</p><div class="table-wrap"><table><thead><tr><th>Constant</th><th>Value</th></tr></thead><tbody>{constants}</tbody></table></div><h2>3 · High release gate</h2><p>High requires an open non-expired OLBG market, official fixture evidence, sufficient official availability information, unrounded probability strictly above 70%, fair American odds from −250 through +10000, and a unique natural prediction of at least 30 words with participants, selection, current form and relevant history/statistics. Failure of any gate means no High release.</p><h2>4 · Expiry</h2><p>Evidence expires at 2026-10-24T03:36:17Z. A price expires at the earlier of that instant and its official UTC start. Browser-time code hides expired prices; source rows remain visible as historical observations. Rows without an established UTC start display the official local/date text instead of a fabricated timestamp.</p><h2>5 · Rebuild</h2><pre><code>python3 scripts/s5b7d3436_data.py
python3 scripts/s5b7d3436_lines.py
python3 scripts/s5b7d3436_build.py
python3 -m unittest tests.pipeline.test_desk_5b7d3436 -v</code></pre><h2>6 · Interpretation</h2><p>No odds are offered, no edge or return is promised, and no open wager is claimed. Research confidence is capped at Low or Medium because current market availability and complete availability packages are absent. High remains zero.</p></section>'''
    write(SITE / "methodology.html", frame("Methodology", body, "analysis"))


def inventory_and_audit():
    paths = sorted(ROOT.glob("scripts/s5b7d3436_*.py"))
    paths += sorted(DATA.glob("*.json"))
    paths += [ROOT / "tests" / "pipeline" / "test_desk_5b7d3436.py", ROOT / "reports" / "SESSION_5B7D3436.md"]
    records = []
    for path in paths:
        if not path.is_file() or path.name in {"site-manifest.json", "repo-inventory.json", "validation.json"}:
            continue
        raw = path.read_bytes()
        records.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
                        "lines": raw.count(b"\n") + (0 if raw.endswith(b"\n") else 1), "sha256": hashlib.sha256(raw).hexdigest()})
    save_json("repo-inventory.json", {"session": "T5B7D", "generated_at": CAPTURE_AT,
                                      "scope_note": "Every existing source/input file in this session's isolated scope; generated page hashes are in site-manifest.json.",
                                      "files": records})
    inv_rows = "".join(f'<tr><td><code>{e(r["path"])}</code></td><td>{r["lines"]:,}</td><td>{r["bytes"]:,}</td><td><code>{e(r["sha256"][:20])}…</code></td></tr>' for r in records)
    validation_rows = "".join(f'<tr><td><code>{e(c["command"])}</code></td><td>{badge("PASS" if c["exit_code"] == 0 else "FAIL", "green" if c["exit_code"] == 0 else "red")}</td><td>{e(c.get("finished_at"))}</td><td>{e(c.get("note"))}</td></tr>' for c in VALIDATION["commands"])
    if not validation_rows:
        validation_rows = '<tr><td colspan="4">Validation receipts are written after the local gate run; no unexecuted check is claimed as passed.</td></tr>'
    body = hero("REPOSITORY AUDIT", "Scoped line inventory, honest limits",
                "Every existing source and input file in this session’s isolated scope is inventoried below with line count, byte count and SHA-256. This does not falsely claim a manual factual recertification of every historical repository line.")
    body += '''<section class="two-col section"><article class="panel"><h2>Findings carried into review</h2><ul><li>COORDINATION.md has duplicate numbering and stale statuses; edits are append-only.</li><li>The canonical root describes an older 22 October, 17-sport brief.</li><li>Historical desks retain unsupported or unrecertified claims and are not imported.</li><li>OLBG popularity displays and community counts are not probabilities.</li><li>Official clock conflicts and cross-domain source routing remain explicit.</li></ul></article><article class="panel"><h2>Full-repository checks</h2><p>The canonical pipeline separately parses and audits tracked historical JSON/Python files and validates the root build. This desk runs those gates without modifying canonical evidence or other sessions’ namespaces.</p><div class="inline-links"><a href="../data/current/audit.json">Canonical historical audit JSON</a><a href="../archive.html">Canonical archive index</a><a href="flagged.html">This desk’s findings</a></div></article></section>'''
    body += '<section class="section"><div class="section-head"><div><span class="eyebrow">VALIDATION RECEIPTS</span><h2>Executed commands</h2></div></div><div class="table-wrap"><table><thead><tr><th>Command</th><th>Result</th><th>Finished</th><th>Note</th></tr></thead><tbody>' + validation_rows + '</tbody></table></div></section>'
    body += '<section class="section"><div class="section-head"><div><span class="eyebrow">LINE-BY-LINE FILE INVENTORY</span><h2>Isolated source scope</h2></div><a href="../data/5b7d3436/repo-inventory.json">Inventory JSON →</a></div><div class="table-wrap"><table><thead><tr><th>Path</th><th>Lines</th><th>Bytes</th><th>SHA-256 prefix</th></tr></thead><tbody>' + inv_rows + '</tbody></table></div></section>'
    write(SITE / "repo-audit.html", frame("Repository audit", body, "analysis"))


CSS = r'''
:root{--ink:#17251f;--muted:#64736b;--paper:#f5f7f4;--card:#fff;--line:#dce4de;--green:#166b4b;--green2:#e5f2eb;--navy:#183e59;--amber:#9a5b09;--amberbg:#fff4df;--red:#a53c3c;--redbg:#fff0ee;--shadow:0 12px 35px rgba(23,50,36,.07)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.58 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--green);text-decoration:none}a:hover{text-decoration:underline}button,input{font:inherit}button{cursor:pointer}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.skip{position:absolute;top:-60px;left:16px;background:var(--ink);color:#fff;padding:10px 16px;z-index:99}.skip:focus{top:10px}.site-header{background:#102d23;color:#fff;position:relative}.header-inner{max-width:1440px;margin:auto;padding:19px 32px;display:flex;align-items:center;gap:24px}.brand{display:flex;gap:11px;align-items:center;color:#fff}.brand:hover{text-decoration:none}.brand-mark{display:grid;place-items:center;width:40px;height:40px;border:1px solid #5d8172;border-radius:11px;color:#a8d9be;font-weight:800;font-size:18px}.brand b{font-weight:500;color:#b9cbc2}.brand small{display:block;font-size:9px;letter-spacing:.16em;color:#89a398;margin-top:2px}.capture{margin-left:auto;text-align:right;font-size:12px;color:#d6e7de}.capture i{display:inline-block;width:7px;height:7px;border-radius:50%;background:#78d7a5;margin-right:7px}.capture small{display:block;color:#8fab9e}.menu-button{display:none;background:transparent;color:#fff;border:1px solid #59776a;border-radius:7px;padding:7px 12px}.primary-nav{max-width:1440px;margin:auto;padding:0 32px 15px;display:flex;gap:4px;align-items:center;overflow-x:auto}.primary-nav a{color:#bcd0c6;padding:8px 11px;border-radius:7px;white-space:nowrap;font-size:13px}.primary-nav a:hover{background:#1c4134;text-decoration:none;color:#fff}.primary-nav a.active{background:#285343;color:#fff}.primary-nav .flag-nav{margin-left:auto;border:1px solid #49695b}.flag-nav span{display:inline-grid;place-items:center;background:#406454;border-radius:10px;min-width:22px;height:18px;font-size:10px}.page{max-width:1440px;margin:auto;padding:38px 32px 70px}.hero{padding:20px 0 28px;max-width:1020px}.eyebrow{font-size:11px;letter-spacing:.14em;font-weight:750;color:var(--green);text-transform:uppercase;margin-bottom:8px}.hero h1{font-size:clamp(34px,4.6vw,62px);line-height:1.04;letter-spacing:-.045em;margin:0 0 18px;font-weight:760}.hero p{font-size:18px;line-height:1.55;color:#50645a;margin:0;max-width:900px}.hero-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}.button{display:inline-block;padding:10px 16px;border:1px solid #bdcec3;border-radius:8px;background:#fff;font-weight:650;font-size:13px;color:#254d3c}.button:hover{text-decoration:none;border-color:#6f9b84}.button.primary{background:var(--green);border-color:var(--green);color:#fff}.alert,.notice{padding:19px 22px;border-radius:11px;margin:6px 0 26px;border:1px solid #ecd5a9;background:var(--amberbg);color:#634a1d}.alert strong{font-size:16px}.alert p{margin:5px 0 7px}.alert a{font-weight:700;color:#805610}.notice{background:#eaf1ed;border-color:#c9dbd0;color:#345344}.kpi-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:0 0 42px}.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:17px 16px;min-width:0}.kpi>span{display:block;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.07em}.kpi strong{display:block;font-size:29px;line-height:1.2;letter-spacing:-.035em;margin:7px 0 4px}.kpi small{color:var(--muted);font-size:11px}.section{margin-top:42px}.section-head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:14px}.section-head h2{margin:0;font-size:27px;letter-spacing:-.025em}.section-head p{margin:4px 0 0}.section-head>a{font-weight:650;white-space:nowrap}.section>p{color:var(--muted)}.table-wrap{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 3px 12px rgba(30,50,40,.025)}table{border-collapse:collapse;width:100%;font-size:13px}th{text-align:left;background:#eef3ef;color:#4a5e53;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:750}th,td{padding:12px 13px;border-bottom:1px solid #e6ece7;vertical-align:top}tr:last-child td{border-bottom:0}tbody tr:hover{background:#fafcfb}td small{display:block;color:var(--muted);font-size:11px;margin-top:3px;max-width:360px}td p{margin:3px 0;color:#4c5e54}.dense{font-size:12px}.dense th,.dense td{padding:10px 11px}.source-stack{display:flex;flex-direction:column;gap:4px;min-width:110px}.source-link{font-size:11px;white-space:nowrap}.badge{display:inline-block;border-radius:999px;padding:3px 8px;background:#edf1ee;color:#536158;font-size:10px;font-weight:700;white-space:nowrap;margin:2px 2px 2px 0}.badge.green{background:var(--green2);color:var(--green)}.badge.medium{background:#e7edf5;color:#355778}.badge.low{background:#eef0ed;color:#657069}.badge.amber{background:var(--amberbg);color:var(--amber)}.badge.red{background:var(--redbg);color:var(--red)}.muted{color:var(--muted)}.sports-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.sport-card{background:#fff;border:1px solid var(--line);border-radius:11px;padding:15px;color:var(--ink);transition:.15s}.sport-card:hover{transform:translateY(-2px);box-shadow:var(--shadow);text-decoration:none;border-color:#b3c9bb}.sport-card>div{display:flex;justify-content:space-between;align-items:center}.sport-dot{width:8px;height:8px;border-radius:50%;background:#63a783}.sport-card h3{margin:18px 0 5px;font-size:17px}.sport-card p{margin:0;color:var(--muted);font-size:12px}.sport-card small{display:block;border-top:1px solid #edf1ed;margin-top:15px;padding-top:10px;color:#6c7b72;font-size:10px}.three-col{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.three-col article{background:#e9efeb;border-radius:12px;padding:23px}.three-col h3{margin:9px 0}.three-col p{color:#52665a;margin:0}.step{font-size:11px;color:var(--green);font-weight:800}.coverage-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.coverage-card{background:#fff;border:1px solid var(--line);border-radius:13px;padding:22px;color:var(--ink)}.coverage-card:hover{text-decoration:none;box-shadow:var(--shadow)}.coverage-top{display:flex;justify-content:space-between;gap:10px}.coverage-top h2{margin:0;font-size:22px}.coverage-top span{font-size:11px;color:var(--muted)}.coverage-card p{color:var(--muted)}.coverage-state{display:flex;gap:6px;flex-wrap:wrap;margin:16px 0}.coverage-state span{background:#f0f3f0;padding:4px 7px;border-radius:5px;font-size:10px;color:#5d6d63}.coverage-card b{font-size:12px;color:var(--green)}.discovery-strip{display:grid;grid-template-columns:repeat(3,1fr);background:#152f26;color:#fff;border-radius:12px;padding:20px;margin-bottom:25px;gap:20px}.discovery-strip>div{border-right:1px solid #385148;padding-right:18px}.discovery-strip>div:last-child{border:0}.discovery-strip span,.discovery-strip small{display:block;color:#a6bdb2;font-size:11px}.discovery-strip strong{display:block;margin:5px 0;text-transform:capitalize}.discovery-strip a{color:#9edabb;font-size:11px}.inline-links{display:flex;gap:8px 18px;flex-wrap:wrap;margin:10px 0 20px}.fixture-card,.market-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:25px;margin:23px 0;box-shadow:0 4px 20px rgba(30,50,40,.035)}.fixture-head{display:flex;justify-content:space-between;gap:15px;align-items:start}.fixture-head h2{font-size:26px;margin:0;letter-spacing:-.025em}.fixture-meta{display:grid;grid-template-columns:2fr 2fr 1fr;gap:15px;background:#f3f6f3;border-radius:9px;padding:14px;margin:18px 0}.fixture-meta span{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:4px}.fixture-meta small{display:block;color:var(--muted);font-size:11px}.two-col{display:grid;grid-template-columns:1fr 1fr;gap:22px}.two-col h3{font-size:14px;margin:14px 0 6px}.two-col ul{padding-left:19px;margin:6px 0;color:#465b4f}.two-col li{margin-bottom:7px}.review-list{color:#795c2d!important;font-size:12px}.price-block{border-top:1px solid var(--line);margin-top:20px;padding-top:18px}.price-meta{display:flex;justify-content:space-between;gap:12px;color:var(--muted);font-size:11px;margin-bottom:12px}.price-block h4{font-size:14px;margin:20px 0 8px}.fine-print{font-size:11px;color:var(--muted)}.expired-panel{padding:18px;background:var(--redbg);color:var(--red);border-radius:8px}.market-card .section-head{margin-bottom:0}.gate-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.gate-grid article{border:1px solid var(--line);background:#fff;border-radius:11px;padding:20px}.gate-grid span{display:grid;place-items:center;background:var(--green2);color:var(--green);width:29px;height:29px;border-radius:50%;font-weight:800}.gate-grid h3{margin:12px 0 5px}.gate-grid p{color:var(--muted);font-size:12px;margin:0}.empty-state{text-align:center;background:#fff;border:1px solid var(--line);border-radius:14px;padding:55px 20px}.empty-state>span{font-size:70px;line-height:1;color:#a8b9af;font-weight:750}.empty-state h2{font-size:28px}.empty-state p{max-width:740px;margin:0 auto;color:var(--muted)}.empty-state .hero-actions{justify-content:center}.findings-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.findings-grid article{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px}.finding-number{font-size:30px;color:var(--green);font-weight:750}.findings-grid h2{font-size:19px}.findings-grid p{color:var(--muted);font-size:13px}.panel{background:#fff;border:1px solid var(--line);border-radius:12px;padding:23px}.panel h2{margin-top:0;font-size:21px}.panel li{margin-bottom:9px;color:#4b6054}.filter-bar{display:flex;align-items:end;gap:20px;flex-wrap:wrap;background:#eaf0eb;border-radius:10px;padding:14px;margin-bottom:15px}.filter-bar label{font-size:11px;font-weight:700;color:#4a6053}.filter-bar input{display:block;margin-top:5px;width:280px;max-width:75vw;padding:8px 10px;border:1px solid #bdcdc2;border-radius:7px;background:#fff}.filter-buttons{display:flex;gap:5px;flex-wrap:wrap}.filter-buttons button{border:1px solid #bdcdc2;background:#fff;color:#44594d;border-radius:6px;padding:7px 10px;font-size:11px}.filter-buttons button.active{background:var(--green);border-color:var(--green);color:#fff}#filter-count{margin-left:auto;font-size:11px;color:var(--muted)}pre{white-space:pre-wrap;background:#152d24;color:#d8e8df;border-radius:9px;padding:18px;overflow:auto;font-size:12px}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.92em}.prose{max-width:1020px}.prose h2{margin-top:32px}.prose p{color:#4b6054}.back-link{margin:30px 0}.footer{background:#102d23;color:#aac0b5;padding:28px 32px;display:flex;justify-content:space-between;gap:30px}.footer strong{color:#fff}.footer p{font-size:11px;margin:5px 0}.footer-links{display:flex;gap:8px 18px;flex-wrap:wrap;max-width:520px;justify-content:flex-end}.footer a{color:#b4d8c5;font-size:12px}.is-expired .price-value{display:none!important}.is-expired .expired-label{display:block!important}[hidden]{display:none!important}
@media(max-width:1180px){.kpi-grid{grid-template-columns:repeat(3,1fr)}.sports-grid{grid-template-columns:repeat(3,1fr)}.coverage-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:760px){.header-inner{padding:15px 18px}.capture{display:none}.menu-button{display:block;margin-left:auto}.primary-nav{display:none;padding:0 18px 14px;flex-wrap:wrap}.primary-nav.open{display:flex}.primary-nav .flag-nav{margin-left:0}.page{padding:24px 17px 50px}.hero{padding-top:10px}.hero h1{font-size:39px}.hero p{font-size:16px}.kpi-grid{grid-template-columns:repeat(2,1fr);gap:9px}.kpi{padding:14px}.kpi strong{font-size:25px}.sports-grid,.coverage-grid,.three-col,.findings-grid,.gate-grid{grid-template-columns:1fr}.two-col{grid-template-columns:1fr}.discovery-strip{grid-template-columns:1fr}.discovery-strip>div{border-right:0;border-bottom:1px solid #385148;padding-bottom:13px}.fixture-card,.market-card{padding:18px}.fixture-head{display:block}.fixture-meta{grid-template-columns:1fr}.section-head{align-items:start;flex-direction:column}.price-meta{flex-direction:column}.footer{padding:25px 18px;flex-direction:column}.footer-links{justify-content:flex-start}.filter-bar{align-items:start;gap:12px}#filter-count{margin-left:0}.table-wrap{border-radius:9px}th,td{padding:10px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.sport-card{transition:none}}
'''

JS = r'''
(function(){
  const button=document.getElementById('menu-button');
  const nav=document.getElementById('primary-nav');
  if(button&&nav){button.addEventListener('click',function(){const open=nav.classList.toggle('open');button.setAttribute('aria-expanded',String(open));});}
  const now=Date.now();
  document.querySelectorAll('[data-price-expires]').forEach(function(el){
    const expiry=el.getAttribute('data-price-expires');
    const start=el.getAttribute('data-start');
    const expired=(expiry&&Date.parse(expiry)<=now)||(start&&Date.parse(start)<=now);
    if(expired){el.classList.add('is-expired');el.querySelectorAll('.expired-label').forEach(function(x){x.hidden=false;});}
  });
  const table=document.getElementById('filter-table');
  if(!table){return;}
  const rows=Array.from(table.tBodies[0].rows);
  const search=document.getElementById('source-search');
  const buttons=Array.from(document.querySelectorAll('[data-filter]'));
  const count=document.getElementById('filter-count');
  let active='all';
  function apply(){
    const q=(search&&search.value||'').trim().toLowerCase();let shown=0;
    rows.forEach(function(row){const kind=row.getAttribute('data-kind');const text=row.getAttribute('data-search')||row.textContent.toLowerCase();const visible=(active==='all'||kind===active)&&(!q||text.includes(q));row.hidden=!visible;if(visible){shown++;}});
    if(count){count.textContent=shown+' of '+rows.length+' rows';}
  }
  buttons.forEach(function(btn){btn.addEventListener('click',function(){active=btn.getAttribute('data-filter');buttons.forEach(function(b){b.classList.toggle('active',b===btn);});apply();});});
  if(search){search.addEventListener('input',apply);}apply();
})();
'''


def finalize():
    write(SITE / "assets" / "style.css", CSS)
    write(SITE / "assets" / "nojs.css", ".price-value,.price-meta{display:none!important}\n")
    write(SITE / "assets" / "app.js", JS)
    write(SITE / "404.html", frame("Not found", '<section class="empty-state"><h1>Page not found</h1><p>A missing page implies no result or selection.</p><a class="button primary" href="index.html">Return to overview</a></section>'))
    write(SITE / ".nojekyll", "")
    pages = sorted(p for p in SITE.rglob("*.html"))
    manifest = {"session": "T5B7D", "generated_at": CAPTURE_AT, "site": "5b7d3436",
                "pages": [{"path": p.relative_to(SITE).as_posix(), "sha256": sha(p)} for p in pages],
                "assets": [{"path": p.relative_to(SITE).as_posix(), "sha256": sha(p)} for p in sorted((SITE / "assets").glob("*"))],
                "counts": SUMMARY}
    save_json("site-manifest.json", manifest)
    print(f"Built {len(pages)} HTML pages in {SITE}; {SUMMARY['fixtures']} fixtures, {SUMMARY['high_picks']} High picks")


def main():
    build_index()
    build_matches()
    build_sports()
    build_markets()
    build_high()
    build_predictions()
    build_analysis()
    build_sources()
    build_discovery()
    build_flagged()
    build_methodology()
    inventory_and_audit()
    finalize()


if __name__ == "__main__":
    main()
