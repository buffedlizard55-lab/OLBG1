"""Build the standalone GitHub Pages dashboard for desk 23728b2b.

Run from the repository root: python -m scripts.s23728b2b_build
Only the desk namespace and its own data directory are written.
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from scripts.s23728b2b_data import FLAGS, FIXTURES, OBSERVED, PICKS, SOURCES, SPORTS
from scripts.s23728b2b_lib import assemble, confidence, display_american, display_decimal, fair_american

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "23728b2b"
DATA = ROOT / "data" / "23728b2b"
SPORT_NAME = dict(SPORTS)
SPORT_ORDER = {slug: index for index, (slug, _) in enumerate(SPORTS)}


def e(value) -> str:
    return html.escape(str(value), quote=True)


def pct(probability: float) -> str:
    return f"{probability * 100:.1f}%"


def tier_badge(tier: str) -> str:
    return f'<span class="badge tier-{tier.lower()}">{e(tier)}</span>'


def source_link(source: dict, label="Official review") -> str:
    return f'<a class="source-link" href="{e(source["url"])}" target="_blank" rel="noopener noreferrer">{e(label)} <span aria-hidden="true">↗</span></a>'


def start_cell(fixture: dict) -> str:
    if fixture["start_utc"]:
        dt = datetime.fromisoformat(fixture["start_utc"].replace("Z", "+00:00"))
        return f'<time datetime="{e(fixture["start_utc"])}">{e(dt.strftime("%d %b · %H:%M UTC"))}</time>'
    return f'<span class="blank-field">Time not captured</span><small>{e(fixture["start_label"])}</small>'


def fixture_name(fixture: dict) -> str:
    if fixture["sport"] in {"motor-racing", "greyhounds"}:
        return fixture["a"]
    return f'{fixture["a"]} v {fixture["b"]}'


def analysis_url(fixture: dict, prefix="") -> str:
    return f'{prefix}sports/{fixture["sport"]}.html#pick-{fixture["id"]}'


def official_sources_for(fixture: dict) -> list[dict]:
    ids = [fixture["source"], *fixture["extra_sources"]]
    by_id = {s["id"]: s for s in SOURCES}
    return [by_id[sid] for sid in dict.fromkeys(ids)]


def page(title: str, body: str, *, prefix="", description="Source-linked sports research") -> str:
    # The canonical archive publisher retains HTML/CSS/SVG only. Inline the desk's
    # small dependency-free controller so its filters work in that artifact too.
    inline_js = (SITE / "app.js").read_text()
    nav = [
        ("index.html", "Executive summary"),
        ("matches.html", "All matches"),
        ("sources.html", "Sources"),
        ("methodology.html", "Methodology"),
        ("flagged.html", "Flagged for Review"),
        ("repository-audit.html", "Repository audit"),
    ]
    links = "".join(f'<a href="{prefix}{href}">{e(label)}</a>' for href, label in nav)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{e(description)}">
  <title>{e(title)} · Desk 23728b2b</title>
  <link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="{prefix}index.html"><span class="brand-mark">24</span><span>OLBG research desk<small>23728b2b · 24 Oct 2026</small></span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav id="site-nav" aria-label="Desk navigation">{links}</nav>
  </div>
</header>
<main id="main" class="page-shell">
{body}
</main>
<footer class="site-footer">
  <div><strong>Research snapshot, not a live odds service.</strong> Prices are independent fair-price estimates, not bookmaker offers. Sporting facts were read at {e(OBSERVED)}; recheck status, availability and start times before use.</div>
  <div>18+ · No outcome is guaranteed · <a href="{prefix}methodology.html">How lines and confidence work</a> · <a href="{prefix}flagged.html">{len(FLAGS)} disclosed review items</a></div>
</footer>
<script>{inline_js}</script>
</body>
</html>'''


def line_cells(line: dict) -> str:
    return f'<td><strong>{e(line["selection"])}</strong><small>{e(line["market"])}</small></td><td>{pct(line["probability"])}</td><td><strong>{e(line["fair_american_display"])}</strong><small>decimal {display_decimal(line["probability"])}</small></td>'


def build_index(desk: dict) -> str:
    lines = [line for line in desk["lines"] if line["role"] == "primary"]
    fixtures = desk["fixture_by_id"]
    sources = desk["source_by_id"]
    high = sorted((line for line in lines if line["confidence"] == "High"), key=lambda x: -x["probability"])
    medium = sorted((line for line in lines if line["confidence"] == "Medium"), key=lambda x: -x["probability"])[:8]
    summary = desk["summary"]
    high_rows = []
    for line in high:
        fixture = fixtures[line["fixture"]]
        high_rows.append(f'''<tr>
<td>{tier_badge("High")}</td>
<td><a class="selection-link" href="{analysis_url(fixture)}">{e(line["selection"])}</a><small>{e(line["market"])}</small></td>
<td>{e(fixture_name(fixture))}<small>{e(SPORT_NAME[fixture["sport"]])} · {e(fixture["competition"])}</small></td>
<td>{pct(line["probability"])}</td>
<td><strong>{e(line["fair_american_display"])}</strong><small>decimal {display_decimal(line["probability"])}</small></td>
<td><a class="button button-small" href="{analysis_url(fixture)}">Read analysis</a></td>
<td>{source_link(sources[fixture["source"]])}</td>
</tr>''')
    medium_rows = []
    for line in medium:
        fixture = fixtures[line["fixture"]]
        reason = "Fair price shorter than −250" if line["probability"] > .70 else "Probability not above 70%"
        medium_rows.append(f'''<tr>
<td>{tier_badge("Medium")}</td>
<td><a class="selection-link" href="{analysis_url(fixture)}">{e(line["selection"])}</a><small>{e(line["market"])}</small></td>
<td>{e(SPORT_NAME[fixture["sport"]])}<small>{e(fixture_name(fixture))}</small></td>
<td>{pct(line["probability"])}</td>
<td>{e(line["fair_american_display"])}</td>
<td>{e(reason)}</td>
<td><a href="{analysis_url(fixture)}">Analysis</a></td>
<td>{source_link(sources[fixture["source"]])}</td>
</tr>''')
    cards = []
    for slug, name in SPORTS:
        sport_fixtures = [f for f in FIXTURES if f["sport"] == slug]
        sport_lines = [line for line in lines if fixtures[line["fixture"]]["sport"] == slug]
        sport_high = sum(line["confidence"] == "High" for line in sport_lines)
        if not sport_lines:
            note = "No priced pick: see the disclosed coverage reason."
        elif len(sport_lines) < 5:
            note = f'{len(sport_lines)} supported priced row{"s" if len(sport_lines) != 1 else ""}; the five-match aim is not force-filled.'
        else:
            note = f'{len(sport_lines)} priced rows with official review links.'
        cards.append(f'''<a class="sport-card" href="sports/{slug}.html">
<span class="sport-card-top"><strong>{e(name)}</strong><span>{len(sport_lines)} priced</span></span>
<span class="sport-card-meta">{sport_high} High · {len(sport_fixtures)} total row{"s" if len(sport_fixtures) != 1 else ""}</span>
<small>{e(note)}</small><span class="card-arrow" aria-hidden="true">→</span>
</a>''')
    body = f'''
<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow">Executive summary · independent lines · official evidence</p>
    <h1>Upcoming OLBG-listed events, with the strongest picks first.</h1>
    <p class="lede">Fifteen requested sports, one transparent snapshot. Start with a High selection, open its match analysis, then use the official link to review the underlying sporting evidence.</p>
    <div class="hero-actions"><a class="button" href="#high-picks">View {summary["high_picks"]} High picks</a><a class="button button-secondary" href="matches.html">Browse all {summary["fixture_rows"]} match rows</a></div>
  </div>
  <div class="snapshot-card">
    <span class="status-dot"></span><strong>Research cut-off</strong>
    <time datetime="{OBSERVED}">24 Oct 2026 · 17:56:39 UTC</time>
    <p>Events were upcoming at this cut-off unless explicitly withheld. This is not a live tracker; Ospreys–Dragons is especially time-sensitive.</p>
    <a href="flagged.html#F-OSPREYS-CUTOFF">Read the timing flag</a>
  </div>
</section>
<section class="metric-strip" aria-label="Coverage totals">
  <div><strong>{summary["sports_requested"]}</strong><span>requested sports</span></div>
  <div><strong>{summary["priced_fixtures"]}</strong><span>priced fixtures</span></div>
  <div><strong>{summary["total_lines"]}</strong><span>independent lines</span></div>
  <div><strong>{summary["high_picks"]}</strong><span>High picks</span></div>
  <div><strong>{summary["official_sources"]}</strong><span>official sources</span></div>
</section>
<section id="high-picks" class="section-block">
  <div class="section-heading"><div><p class="eyebrow">Start here</p><h2>High-confidence selections</h2></div><p>Every High pick is strictly above 70% and its unrounded fair American price lies within −250 to +10000. Each has unique analysis of at least 30 words.</p></div>
  <div class="table-wrap"><table><thead><tr><th>Tier</th><th>Selection</th><th>Event</th><th>Probability</th><th>Fair price</th><th>Location</th><th>Official review</th></tr></thead><tbody>{''.join(high_rows)}</tbody></table></div>
  <p class="table-note">Fair prices are calculated from the stated probabilities; they are not quoted odds. <a href="methodology.html">See the arithmetic and confidence rules.</a></p>
</section>
<section class="section-block">
  <div class="section-heading"><div><p class="eyebrow">Next best</p><h2>Leading Medium selections</h2></div><p>These are not High: either the probability does not clear the strict threshold or the reciprocal price is too short.</p></div>
  <div class="table-wrap"><table><thead><tr><th>Tier</th><th>Selection</th><th>Sport / event</th><th>Probability</th><th>Fair price</th><th>Why not High</th><th>Location</th><th>Official review</th></tr></thead><tbody>{''.join(medium_rows)}</tbody></table></div>
</section>
<section class="section-block">
  <div class="section-heading"><div><p class="eyebrow">Coverage</p><h2>Choose a sport</h2></div><p>Coverage follows available evidence. Golf, Snooker and Rugby League have no priced selection; the reason is disclosed rather than replaced with a filler pick.</p></div>
  <div class="sport-grid">{''.join(cards)}</div>
</section>
<section class="split-panels">
  <div class="info-panel"><p class="eyebrow">Full card</p><h2>Priced, withheld and official-context rows</h2><p>The match list contains {summary["priced_fixtures"]} priced fixtures, {summary["withheld_fixtures"]} withheld OLBG-listed fixture and {summary["official_context_fixtures"]} official-context fixture. Unsupported discoveries are documented on the review page.</p><a class="button button-secondary" href="matches.html">Open the organized match list</a></div>
  <div class="info-panel warning-panel"><p class="eyebrow">Manual review</p><h2>{summary["flags"]} irregularities and evidence limits</h2><p>Conflicting kick-offs, missing order-of-play times, an official date typo and incomplete availability remain visible. Flags do not hide otherwise supported rows.</p><a class="button button-secondary" href="flagged.html">Open Flagged for Review</a></div>
</section>
'''
    return page("Executive summary", body, description="Executive-first dashboard for 15 OLBG sports with independent fair lines and official evidence")


def build_matches(desk: dict) -> str:
    line_by_fixture = {line["fixture"]: line for line in desk["lines"] if line["role"] == "primary"}
    rows = []
    ordered = sorted(FIXTURES, key=lambda f: (SPORT_ORDER[f["sport"]], f["start_utc"] or "9999", f["a"]))
    for fixture in ordered:
        line = line_by_fixture.get(fixture["id"])
        sport = fixture["sport"]
        if line:
            selection = f'<a class="selection-link" href="{analysis_url(fixture)}">{e(line["selection"])}</a><small>{e(line["market"])}</small>'
            probability = pct(line["probability"])
            price = f'<strong>{e(line["fair_american_display"])}</strong><small>decimal {display_decimal(line["probability"])}</small>'
            tier = tier_badge(line["confidence"])
            data_tier = line["confidence"].lower()
        else:
            label = "Official context only" if fixture["scope"] != "OLBG-listed" else "Withheld"
            selection = f'<span class="muted">{label}</span><small>No selection or price</small>'
            probability = price = '<span class="blank-field">—</span>'
            tier = f'<span class="badge tier-withheld">{label}</span>'
            data_tier = "withheld"
        search = e(" ".join([fixture_name(fixture), fixture["competition"], SPORT_NAME[sport], line["selection"] if line else "withheld"]).lower())
        rows.append(f'''<tr data-sport="{e(sport)}" data-confidence="{data_tier}" data-search="{search}">
<td>{e(SPORT_NAME[sport])}</td>
<td>{start_cell(fixture)}</td>
<td><a href="{analysis_url(fixture)}">{e(fixture_name(fixture))}</a><small>{e(fixture["competition"])} · {e(fixture["scope"])}</small></td>
<td>{selection}</td><td>{probability}</td><td>{price}</td><td>{tier}</td>
<td>{source_link(desk["source_by_id"][fixture["source"]])}</td>
</tr>''')
    options = "".join(f'<option value="{e(slug)}">{e(name)}</option>' for slug, name in SPORTS)
    body = f'''
<section class="page-heading"><p class="eyebrow">Full organized match list</p><h1>All {len(FIXTURES)} official-source fixture rows</h1><p>Priced rows show an independent selection and reciprocal fair price. Withheld and context-only rows deliberately leave those fields blank. Every row opens an official sporting source.</p></section>
<div class="filters" aria-label="Match filters">
  <label>Sport<select id="sport-filter"><option value="all">All 15 sports</option>{options}</select></label>
  <label>Confidence<select id="confidence-filter"><option value="all">All states</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option><option value="withheld">Withheld / context</option></select></label>
  <label class="filter-search">Search<input id="match-search" type="search" placeholder="Team, player or competition"></label>
  <span id="filter-count" class="filter-count" aria-live="polite">{len(FIXTURES)} rows</span>
</div>
<div class="table-wrap"><table id="match-table"><thead><tr><th>Sport</th><th>Start</th><th>Match / scope</th><th>Selection</th><th>Probability</th><th>Fair price</th><th>State</th><th>Official review</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p id="no-filter-results" class="empty-state" hidden>No rows match these filters.</p>
<p class="table-note">Blank exact times are identified in the start column and explained on the relevant sport and review pages. OLBG supplies discovery context only; the links in this table are official sporting sources.</p>
'''
    return page("All matches", body)


def build_sport_page(desk: dict, slug: str, name: str) -> str:
    sport_fixtures = [f for f in FIXTURES if f["sport"] == slug]
    sport_fixtures.sort(key=lambda f: (f["start_utc"] or "9999", f["a"]))
    line_by_fixture = {line["fixture"]: line for line in desk["lines"] if line["role"] == "primary"}
    alternatives = {}
    for line in desk["lines"]:
        if line["role"] == "alternative":
            alternatives.setdefault(line["fixture"], []).append(line)
    predictions = {p["fixture"]: p for p in desk["predictions"]}
    discovery = desk["source_by_id"][f"olbg-{slug}"]
    cards = []
    for fixture in sport_fixtures:
        line = line_by_fixture.get(fixture["id"])
        official = official_sources_for(fixture)
        links = "".join(f'<li>{source_link(src, src["publisher"] + " · " + src["title"])}</li>' for src in official)
        facts = "".join(f'<li>{e(fact)}</li>' for fact in fixture["facts"])
        flag_links = "".join(f'<a href="../flagged.html#{e(fid)}">{e(fid)}</a>' for fid in fixture["flag_ids"])
        if line:
            alt_rows = []
            for alternative in alternatives.get(fixture["id"], []):
                alt_rows.append(f'<tr><td>{e(alternative["market"])}</td><td>{e(alternative["selection"])}</td><td>{pct(alternative["probability"])}</td><td>{e(alternative["fair_american_display"])}<small>decimal {display_decimal(alternative["probability"])}</small></td><td>{tier_badge(alternative["confidence"])}</td><td>{source_link(desk["source_by_id"][fixture["source"]])}</td></tr>')
            alt_table = f'<div class="table-wrap"><table class="alternative-table"><thead><tr><th>Alternative market</th><th>Selection</th><th>Probability</th><th>Fair price</th><th>Tier</th><th>Official review</th></tr></thead><tbody>{"".join(alt_rows)}</tbody></table></div>' if alt_rows else '<p class="muted">No additional price is published for this fixture.</p>'
            pick_panel = f'''
<div class="pick-panel" id="pick-{e(fixture["id"])}">
  <div class="pick-top"><div><span class="eyebrow">Primary selection · {e(line["market"])}</span><h3>{e(line["selection"])}</h3></div>{tier_badge(line["confidence"])}</div>
  <div class="price-trio"><div><span>Probability</span><strong>{pct(line["probability"])}</strong></div><div><span>Fair American</span><strong>{e(line["fair_american_display"])}</strong></div><div><span>Fair decimal</span><strong>{display_decimal(line["probability"])}</strong></div></div>
  <p class="prediction">{e(predictions[fixture["id"]]["text"])}</p>
</div>
<h4>Multi-market ladder</h4>{alt_table}
<p class="market-note"><strong>Market investigation:</strong> {e(fixture["market_note"])}</p>'''
        else:
            pick_panel = f'''<div class="withheld-panel" id="pick-{e(fixture["id"])}"><span class="badge tier-withheld">{"Official context only" if fixture["scope"] != "OLBG-listed" else "Withheld"}</span><h3>No selection or independent price</h3><p>{e(fixture["market_note"])}</p></div>'''
        cards.append(f'''
<article class="match-card" id="{e(fixture["id"])}">
  <div class="match-card-heading"><div><p class="eyebrow">{e(fixture["competition"])}</p><h2>{e(fixture_name(fixture))}</h2></div><div class="match-time">{start_cell(fixture)}<small>{e(fixture["scope"])}</small></div></div>
  <details class="evidence-details" open><summary>Official evidence and review links</summary><ul class="fact-list">{facts}</ul><ul class="source-list">{links}</ul></details>
  {pick_panel}
  {f'<p class="fixture-flags"><strong>Review flags:</strong> {flag_links}</p>' if flag_links else ''}
</article>''')
    priced = sum(f["id"] in line_by_fixture for f in sport_fixtures)
    high = sum(line_by_fixture[f["id"]]["confidence"] == "High" for f in sport_fixtures if f["id"] in line_by_fixture)
    sport_flags = [flag for flag in FLAGS if flag["area"] == name or (slug == "gaelic-sports" and flag["area"] == "Gaelic Sports")]
    if not sport_fixtures:
        empty_reason = {
            "golf": "No current OLBG tips were found, and the official PGA Tour context was already in progress. There is no upcoming match to price.",
            "snooker": "Williams–Jones was not upcoming on the official read. With no settled subsequent final pairing, no new event is manufactured.",
        }.get(slug, "No supported fixture is available in this snapshot.")
        cards.append(f'<div class="empty-state"><h2>No priced fixture</h2><p>{e(empty_reason)}</p><a class="button button-secondary" href="../flagged.html">Read the coverage flags</a></div>')
    body = f'''
<section class="page-heading sport-heading"><p class="eyebrow">{priced} priced · {high} High · {len(sport_fixtures)} total rows</p><h1>{e(name)}</h1><p>{e(discovery["note"])}</p><div class="heading-actions"><a class="button button-secondary" href="../matches.html">All sports</a><a href="{e(discovery["url"])}" target="_blank" rel="noopener noreferrer">OLBG discovery hub ↗</a></div></section>
<div class="snapshot-note"><strong>Snapshot:</strong> {e(OBSERVED)}. Exact blank times and missing availability are not inferred. Prices are independent estimates, not bookmaker quotes.</div>
{''.join(cards)}
'''
    return page(name, body, prefix="../", description=f"{name} fixtures, independent lines and official sporting evidence")


def build_sources(desk: dict) -> str:
    official_rows = []
    for src in SOURCES:
        if not src["official"]:
            continue
        official_rows.append(f'<tr><td><code>{e(src["id"])}</code></td><td>{e(src["publisher"])}</td><td>{e(src["title"])}<small>{e(src["note"]) if src["note"] else "Direct official source read."}</small></td><td><time datetime="{OBSERVED}">24 Oct · 17:56 UTC</time></td><td>{source_link(src, "Open official source")}</td></tr>')
    discovery_items = "".join(f'<li><strong>{e(SPORT_NAME[src["id"].removeprefix("olbg-")])}</strong> — {e(src["note"])} <a href="{e(src["url"])}" target="_blank" rel="noopener noreferrer">Open OLBG discovery hub ↗</a></li>' for src in SOURCES if not src["official"])
    body = f'''
<section class="page-heading"><p class="eyebrow">Provenance</p><h1>Sources and evidence roles</h1><p>Official leagues, governing bodies, clubs and tours substantiate fixtures, results, statistics and availability. OLBG is retained only to explain discovery and is never used as official sporting confirmation.</p></section>
<section class="section-block"><div class="section-heading"><div><p class="eyebrow">{len(official_rows)} records</p><h2>Official sporting evidence</h2></div><p>The consolidated observation time is {e(OBSERVED)}. Notes disclose extraction limitations, source conflicts and stale-snippet handling.</p></div><div class="table-wrap"><table><thead><tr><th>ID</th><th>Publisher</th><th>Evidence / access note</th><th>Observed</th><th>Official review</th></tr></thead><tbody>{''.join(official_rows)}</tbody></table></div></section>
<section class="section-block"><div class="section-heading"><div><p class="eyebrow">Discovery only</p><h2>Fifteen OLBG hubs</h2></div><p>These links explain why an event was researched. They do not substantiate teams, times, form, injuries or results.</p></div><ul class="discovery-list">{discovery_items}</ul></section>
'''
    return page("Sources", body)


def build_methodology(desk: dict) -> str:
    body = f'''
<section class="page-heading"><p class="eyebrow">Transparent calculations</p><h1>Methodology and confidence</h1><p>The desk separates sporting evidence, editorial probability assessment and price arithmetic. No sportsbook price is copied and no missing sporting fact is silently filled.</p></section>
<div class="method-grid">
<article><span class="method-number">01</span><h2>Discovery and scope</h2><p>Exactly 15 requested sport pages are built. OLBG hubs identify candidate events and market context. The full list distinguishes priced OLBG-listed fixtures, withheld OLBG-listed fixtures and official-context-only rows.</p></article>
<article><span class="method-number">02</span><h2>Official evidence</h2><p>Teams, players, dates, results, form, statistics and availability come from official competition, governing-body, club or tour pages. Every match-table row and alternative-ladder row carries an official review link. A discovery link never substitutes for one.</p></article>
<article><span class="method-number">03</span><h2>Independent probability</h2><p>Analyst probabilities weigh the displayed official evidence, venue, current form and availability where available. They are estimates, not guarantees. Unsupported totals, props, traps and exact times remain blank. Alternatives are separate research lines, not accumulator instructions.</p></article>
<article><span class="method-number">04</span><h2>Reciprocal fair price</h2><p>For probability <em>p</em>, fair decimal price is <strong>1 / p</strong>. If decimal is at least 2.0, fair American price is <strong>100 × (decimal − 1)</strong>; otherwise it is <strong>−100 / (decimal − 1)</strong>. Displayed prices are rounded, but the High gate uses the unrounded value.</p><p class="formula">Example: p = 0.68 → decimal 1.470588 → American −212.5 → displayed −213.</p></article>
<article><span class="method-number">05</span><h2>Confidence gates</h2><p><strong>High:</strong> probability strictly greater than 70% <em>and</em> fair American price from −250 through +10000. Exactly 70% is not High. A probability above 70% with a price shorter than −250 remains Medium.</p><p><strong>Medium:</strong> non-High selections at 55% or above, including short-priced candidates outside the High window. <strong>Low:</strong> below 55%.</p></article>
<article><span class="method-number">06</span><h2>Written analysis</h2><p>Every primary prediction is unique prose of at least 30 words, including all High picks. High team/head-to-head selections also require source-bound evidence for both sides. The copy must state an explicit selection and acknowledge important contrary evidence or uncertainty.</p></article>
<article><span class="method-number">07</span><h2>Time and missing fields</h2><p>The research cut-off is <strong>{e(OBSERVED)}</strong>. Events live at that cut-off are excluded. A missing exact start remains blank with a display label and review flag. Later injury, lineup, weather and schedule changes can invalidate a pre-match read.</p></article>
<article><span class="method-number">08</span><h2>Review and limitations</h2><p>Flagged for Review records conflicts, unsupported discoveries, source-access limitations and evidence-capped coverage. Flags do not automatically invalidate unrelated supported rows. This dashboard is research for adults, not a promise of profit or a live betting service.</p></article>
</div>
<section class="section-block"><h2>Worked High gate</h2><div class="formula-panel"><p>A 71.0% selection has fair decimal 1.408451 and fair American −244.83. It can be High because 71.0% is above 70% and −244.83 is inside the required window.</p><p>An 86.0% selection has fair American −614.29. It remains Medium because the price is shorter than −250, even though its probability is higher.</p></div></section>
'''
    return page("Methodology", body)


def build_flags(desk: dict) -> str:
    cards = []
    for flag in FLAGS:
        src = desk["source_by_id"][flag["source"]]
        label = "Official review" if src["official"] else "Discovery review"
        cards.append(f'''<article class="flag-card" id="{e(flag["id"])}"><div class="flag-card-top"><span class="badge flag-badge">{e(flag["severity"])}</span><code>{e(flag["id"])}</code></div><p class="eyebrow">{e(flag["area"])}</p><h2>{e(flag["issue"])}</h2><dl><div><dt>Impact</dt><dd>{e(flag["impact"])}</dd></div><div><dt>Manual action</dt><dd>{e(flag["action"])}</dd></div></dl>{source_link(src, label)}</article>''')
    body = f'''
<section class="page-heading"><p class="eyebrow">Irregularities stay visible</p><h1>Flagged for Review</h1><p>These {len(FLAGS)} items describe conflicts, exclusions, blank fields and evidence limits. They do not block unrelated valid research, but they must not be ignored when using the affected row.</p></section>
<div class="flag-summary"><strong>{len(FLAGS)} review items</strong><span>Missing values remain blank · no unsupported fixture is promoted · official links are supplied wherever official evidence exists</span></div>
<section class="flag-grid">{''.join(cards)}</section>
'''
    return page("Flagged for Review", body)


def build_audit(desk: dict) -> str:
    validation_path = DATA / "validation.json"
    if validation_path.exists():
        validation = json.loads(validation_path.read_text())
        checks = validation.get("checks", [])
        check_items = "".join(f'<li><span class="check-pass">PASS</span><div><strong>{e(check["name"])}</strong><small>{e(check["detail"])}</small></div></li>' for check in checks)
        status = f'{len(checks)} checks passed at {e(validation.get("validated_at", "recorded time"))}'
    else:
        check_items = '<li><span class="check-pending">PENDING</span><div><strong>Desk validation has not yet been recorded.</strong><small>Run scripts.s23728b2b_validate and rebuild this page.</small></div></li>'
        status = "Validation record pending"
    summary = desk["summary"]
    body = f'''
<section class="page-heading"><p class="eyebrow">Repository audit</p><h1>Scope, provenance and validation</h1><p>{e(status)}. This page concerns desk 23728b2b. Canonical integration is limited to one separately claimed archive-registration line; no canonical data, pricing or validation logic is changed.</p></section>
<section class="metric-strip audit-metrics"><div><strong>{summary["fixture_rows"]}</strong><span>source-linked rows</span></div><div><strong>{summary["total_lines"]}</strong><span>arithmetic-checked lines</span></div><div><strong>{summary["high_picks"]}</strong><span>High gate checks</span></div><div><strong>{summary["flags"]}</strong><span>disclosed flags</span></div></section>
<div class="audit-grid">
<section class="audit-panel"><h2>Owned paths</h2><ul><li><code>data/23728b2b/</code> — evidence, fixtures, lines, predictions, flags and validation record</li><li><code>23728b2b/</code> — standalone Pages dashboard and all 15 sport pages</li><li><code>scripts/s23728b2b_*</code> — data, shared arithmetic, builder and validator</li><li><code>tests/pipeline/test_desk_23728b2b.py</code> — preserved desk tests</li><li><code>reports/SESSION_23728B2B.*</code> — session report and served-content checks</li><li><code>pipeline/build.py</code> — one archive-registration line only, separately claimed for Pages inclusion</li><li><code>COORDINATION.md</code> — scoped claim and final desk entry only</li></ul></section>
<section class="audit-panel"><h2>Data checks</h2><ul class="check-list">{check_items}</ul></section>
</div>
<section class="section-block"><h2>Publication controls</h2><div class="method-grid compact"><article><h3>Source completeness</h3><p>Every fixture references an official source. Every match and ladder table row repeats that review path. Discovery sources are labeled separately.</p></article><article><h3>High-pick integrity</h3><p>Probability, unrounded price window, both-side evidence, 30-word minimum, unique prose and direct executive-to-match anchors are checked.</p></article><article><h3>Blank-field policy</h3><p>Missing start fields must be attached to a disclosed flag. Withheld rows cannot carry a selection, probability or price.</p></article><article><h3>Deployment proof</h3><p>Final acceptance requires the canonical pipeline and browser gates, then a GitHub Pages read-back of served HTML rather than relying only on API status.</p></article></div></section>
<p class="report-links"><a class="button button-secondary" href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/reports/SESSION_23728B2B.html">Open session report</a> <a class="button button-secondary" href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/23728b2b/desk.json">Open structured desk JSON</a></p>
'''
    return page("Repository audit", body)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def write_html(path: Path, content: str) -> None:
    """Write deterministic HTML without trailing whitespace on template lines."""
    path.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n")


def main() -> None:
    desk = assemble()
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "sports").mkdir(parents=True, exist_ok=True)
    write_html(SITE / "index.html", build_index(desk))
    write_html(SITE / "matches.html", build_matches(desk))
    write_html(SITE / "sources.html", build_sources(desk))
    write_html(SITE / "methodology.html", build_methodology(desk))
    write_html(SITE / "flagged.html", build_flags(desk))
    write_html(SITE / "repository-audit.html", build_audit(desk))
    for slug, name in SPORTS:
        write_html(SITE / "sports" / f"{slug}.html", build_sport_page(desk, slug, name))
    public = {key: desk[key] for key in ["captured_at", "sports", "sources", "fixtures", "lines", "predictions", "flags", "summary"]}
    write_json(DATA / "desk.json", public)
    for key in ["sources", "fixtures", "lines", "predictions", "flags"]:
        write_json(DATA / f"{key}.json", {"captured_at": OBSERVED, key: desk[key]})
    write_json(DATA / "evidence.json", {"captured_at": OBSERVED, "sources": SOURCES, "fixtures": FIXTURES})
    write_json(DATA / "summary.json", desk["summary"])
    write_json(DATA / "methodology.json", {
        "captured_at": OBSERVED,
        "source_roles": {"OLBG": "discovery only", "official": "sporting evidence"},
        "price": "independent reciprocal no-margin price; no bookmaker quote",
        "decimal": "1 / p",
        "american": "100 * (decimal - 1) if decimal >= 2 else -100 / (decimal - 1)",
        "high": "p > 0.70 and -250 <= unrounded fair American <= +10000",
        "medium": "non-High and p >= 0.55, including short-priced candidates outside the High window",
        "low": "p < 0.55",
        "prediction_words_minimum": 30,
    })
    print(json.dumps(desk["summary"], indent=2))
    print(f"Built {SITE.relative_to(ROOT)} and {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
