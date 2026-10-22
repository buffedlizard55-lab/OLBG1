#!/usr/bin/env python3
"""Canonical evidence-first GitHub Pages builder (stdlib only).

Default clock is actual UTC; --as-of exists for reproducible tests. Building does NOT
refresh official observations. Only release_fetch.py may update its limited API inputs.
Prior desk outputs remain explicitly historical, never silently recertified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from release_archive import preserve
from release_model import MODEL_VERSION, enrich, timestamp

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/release"
TITLE = "OLBG1 · Independent research desk"
LABELS = {"scheduled": "Scheduled at capture", "time-unconfirmed": "UTC unconfirmed", "snapshot-stale": "Evidence expired",
          "start-passed": "Start time passed", "outside-window": "Outside UTC window", "not-pregame": "Not confirmed pregame"}
DESKS = ["984d417f", "c17a9192", "ccb6bde2", "f7fa77fc", "docs", "ebfbd966", "aa4e9dbf", "7a5b5360",
         "a570c470", "9dfd0b48", "f71557b5", "v3", "6a081cf6", "2360a617"]


def e(value):
    return html.escape(str(value) if value is not None else "", quote=True)


def load(path):
    return json.loads(path.read_text())


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def pct(value):
    return f"{value * 100:.1f}%" if value is not None else ""


def us(value):
    return f"{value:+.0f}" if value is not None else ""


def badge(text, css=None):
    return f'<span class="badge {e(css or str(text).lower())}">{e(text)}</span>'


def source_links(ids, sources):
    urls = set()
    links = []
    for sid in ids:
        source = sources[sid]
        if source["url"] in urls:
            continue
        urls.add(source["url"])
        links.append(f'<a href="{e(source["url"])}" rel="noopener noreferrer" target="_blank" title="{e(source["scope"])}">{e(source["name"])}</a>')
    return '<div class="sources">' + "".join(links) + "</div>"


def row_sources(row):
    ids = list(row["fixture_evidence"])
    for field in row.get("field_sources", {}).values():
        ids.extend(field)
    for side in ("a", "b"):
        ids.extend(row.get("inputs", {}).get(side, {}).get("evidence", []))
    return list(dict.fromkeys(ids))


def shell(title, description, body, path, bundle, active=""):
    prefix = "../" if "/" in path else ""
    links = [("Overview", "index.html"), ("Sports", "sports.html"), ("Models", "picks.html"),
             ("Coverage", "coverage.html"), ("Flagged for Review", "flagged.html"), ("Archive", "archive/index.html")]
    nav = "".join(f'<a href="{prefix}{href}"' + (' aria-current="page"' if href == active else "") + f'>{name}</a>' for name, href in links)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG1</title><meta name="description" content="{e(description)}">
<link rel="stylesheet" href="{prefix}assets/release.css"><script src="{prefix}assets/release.js" defer></script>
</head><body><a class="skip" href="#main">Skip to content</a>
<header class="mast"><div class="mast-inner"><a class="brand" href="{prefix}index.html">OLBG1<span>INDEPENDENT RESEARCH DESK</span></a>
<nav aria-label="Main navigation">{nav}</nav></div></header>
<main id="main"><p class="eyebrow">Evidence-led snapshot · {e(bundle['as_of_utc'][:10])} UTC</p>
{body}
</main><footer><p><strong>Research, not a betslip.</strong> Zero approved bets; experimental estimates are not a verified win rate. Odds are zero-vig fair model prices, not bookmaker offers.</p>
<p>Built {e(bundle['as_of_utc'])}. Source observation dates are independent of build time. This build never renews a source check. Blank values mean unconfirmed, not zero.</p>
<p>Not affiliated with OLBG. 18+ · Never bet money you cannot afford to lose. <a href="https://www.ncpgambling.org/help-treatment/">US gambling support</a> ·
<a href="{prefix}sources.html">Sources</a> · <a href="{prefix}methodology.html">Methodology</a> · <a href="{prefix}audit.html">Audit scope</a> · <a href="{prefix}reverse-engineering.html">OLBG discovery</a></p></footer></body></html>'''


def warning(prefix=""):
    return f'''<div class="notice" role="note"><strong>No approved High-confidence selections.</strong>
Officially supported fixture fields are separated from experimental model prices. No held-out calibration or matching bookmaker settlement was verified.
Missing facts remain blank. <a href="{prefix}flagged.html">See all review items</a> · <a href="{prefix}methodology.html">Read the assumptions</a>.</div>'''


def table(headers, rows, caption="", attrs=""):
    return f'<div class="table-wrap"><table {attrs}>' + (f'<caption>{caption}</caption>' if caption else "") + '<thead><tr>' + "".join(f'<th scope="col">{e(h)}</th>' for h in headers) + '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>'


def toolbar(bundle, sport_select=True):
    select = ''
    if sport_select:
        options = ''.join(f'<option value="{e(c["sport"])}">{e(c["name"])}</option>' for c in bundle['coverage'])
        select = f'<label>Sport<select aria-label="Filter by sport"><option value="">All sports</option>{options}</select></label>'
    return f'<div class="toolbar" data-toolbar><label>Search<input type="search" placeholder="Team, event or league" aria-label="Search table"></label>{select}<span class="result-count" data-result-count aria-live="polite"></span></div>'


def fixtures_table(fixtures, bundle, prefix="", filterable=True, sport_select=True):
    sources = bundle['source_map']
    rows = []
    for row in fixtures:
        pair = row['participant_a'] + (' vs ' + row['participant_b'] if row['participant_b'] else '')
        when = e(row['start_utc'].replace('T', ' ').replace(':00Z', ' UTC')) if row.get('start_utc') else ''
        printed = ('<small class="muted">Printed: ' + e(row['printed_time']) + ' · timezone not confirmed</small>') if row.get('printed_time') and not when else ''
        projection = row['winner_projection'] if row['status'] == 'scheduled' else None
        pick = e(projection['selection']) if projection else ''
        price = (f'<span class="numeric">{us(projection["fair_american"])}<br><small>{projection["fair_decimal"]:.3f} decimal · {pct(projection["probability"])}</small></span>') if projection else ''
        confidence = badge(row['confidence']) if projection else ''
        attrs = f'data-search="{e(pair + " " + row["competition"] + " " + row["sport"])}" data-sport="{e(row["sport"])}" data-start="{e(row.get("start_utc") or "")}" data-expires="{e(row["evidence_expires_utc"])}"'
        rows.append(f'''<tr {attrs}><td class="fixture-name"><a href="{prefix}sports/{e(row['sport'])}.html#{e(row['id'])}">{e(pair)}</a><small>{e(row['competition'])} · {e(row['event_date'])}</small></td>
<td class="small nowrap">{when}{printed}</td><td><span data-live-status>{badge(LABELS[row['status']], row['status'])}</span></td>
<td data-live-projection class="blank">{pick}</td><td data-live-projection class="blank">{price}</td><td data-live-projection>{confidence}</td>
<td>{source_links(row_sources(row), sources)}</td></tr>''')
    if not rows:
        return '<div class="empty">No independently priceable, exact-time future fixtures in this view. This is an evidence gap, not a claim that no matches exist.</div>'
    return (toolbar(bundle, sport_select) if filterable else '') + table(
        ['Fixture / event', 'Start (UTC)', 'Time & evidence status', 'Projected winner¹', 'Fair odds / model %¹', 'Confidence¹', 'Official evidence'], rows,
        '¹ Experimental research only. No approved selections. Numeric fields stay blank if exact future timing, freshness or paired inputs are missing.')


def sport_cards(bundle):
    cards = []
    for category in bundle['coverage']:
        rows = [r for r in bundle['fixtures'] if r['sport'] == category['sport']]
        prices = sum(bool(r['markets']) for r in rows)
        cards.append(f'''<a class="sport-card" href="sports/{e(category['sport'])}.html"><div class="card-top"><h3>{e(category['name'])}</h3><span class="arrow" aria-hidden="true">↗</span></div>
<p>{len(rows)} source-linked extracts · {prices} experimental models</p><p>{badge(category['status'])} Coverage is not exhaustive</p></a>''')
    return '<div class="grid">' + ''.join(cards) + '</div>'


def index_page(bundle):
    counts = bundle['counts']
    watch = [r for r in bundle['fixtures'] if r['status'] == 'scheduled' and r['markets']]
    watch.sort(key=lambda r: (r['start_utc'], r['sport'], r['id']))
    return f'''<h1>A clearer view of the slate.</h1><p class="lede">Independent fair lines, source-linked facts, and a visible line between what we know and what still needs checking.</p>
{warning()}<div class="stats"><div class="stat"><strong>{counts['fixtures']}</strong><span>Officially supported fixture / event extracts</span></div>
<div class="stat"><strong>17</strong><span>Sport reviews · all partial or blocked</span></div><div class="stat"><strong>{counts['model_outcomes']}</strong><span>Experimental fair prices · not offers</span></div>
<div class="stat"><strong>0</strong><span>Approved bets · 0 High selections</span></div></div>
<div class="section-head"><h2>Upcoming research watchlist</h2><p>Exact future UTC starts + paired model inputs</p></div>
{fixtures_table(watch, bundle)}
<div class="section"><div class="section-head"><h2>Explore the sports</h2><a href="coverage.html">Coverage & blockers →</a></div>{sport_cards(bundle)}</div>
<div class="section two-col"><div class="panel"><h3>What changed in this release</h3><p class="small muted">Official rereads corrected the Efes and Bayern home/away orientation and Nashville’s record. Unclear display clocks, unverified inherited ratings and stale recommendations are not carried onto the current board.</p><a class="small" href="flagged.html">Open the review ledger →</a></div>
<div class="panel"><h3>All prior desks are retained</h3><p class="small muted">The old primary pages and every session’s namespaced work remain available as unrecertified history, rather than competing live dashboards.</p><a class="small" href="archive/index.html">Browse historical work →</a></div></div>
<div class="section downloads"><a href="data/release/bundle.json">Download current research JSON</a><a href="data/release/rows.csv">Download fixture CSV</a><a href="sources.html">See source observations</a></div>'''


def coverage_page(bundle):
    rows = []
    for category in bundle['coverage']:
        group = [r for r in bundle['fixtures'] if r['sport'] == category['sport']]
        rows.append(f'''<tr data-search="{e(category['name'] + ' ' + category['limitations'])}" data-sport="{e(category['sport'])}"><td><a href="sports/{e(category['sport'])}.html">{e(category['name'])}</a></td>
<td>{len(group)}</td><td>{badge(category['status'])}</td><td>{e(category['limitations'])}</td><td>{source_links([category['official_source'], category['olbg_source']], bundle['source_map'])}</td></tr>''')
    automatic = bundle.get('last_automatic_collection')
    auto_note = '<p>Structured automatic collectors exist only for NHL and MLB; all other observations retain their original dates.</p>'
    if automatic:
        ok = sum(r['status'] == 'success' for r in automatic['attempts'])
        auto_note += f'<p>Last automatic attempt: {e(automatic["attempted_at_utc"])}. {ok}/{len(automatic["attempts"])} requests succeeded. Failures are listed in the JSON download; a failed request never renews an old observation.</p>'
    return f'''<h1>Coverage, honestly measured.</h1><p class="lede">Every eligible OLBG category has a review. None is labelled complete merely because a hub or official homepage loaded.</p>{warning()}
<div class="panel small"><strong>UTC window:</strong> {e(bundle['coverage_window']['from_utc'])} to {e(bundle['coverage_window']['to_utc_exclusive'])} (exclusive). Local schedule dates may differ.
{auto_note}<p>OLBG first rendered chunks are discovery only. Load More, every bookmaker, every competition, every market and all seven days have <strong>not</strong> been exhausted. Empty text is a retrieval limitation, not evidence that a sport has no fixtures.</p></div>
<div class="section">{toolbar(bundle)}{table(['Sport', 'Extracts', 'Status', 'Unresolved collection / model scope', 'Official review + discovery'], rows)}</div>'''


def market_tables(rows, bundle, prefix=""):
    parts = []
    for row in rows:
        if not row['markets']:
            continue
        label = row['participant_a'] + ' vs ' + row['participant_b']
        lines = []
        for market in row['markets']:
            for o in market['outcomes']:
                lines.append(f'''<tr><td>{e(market['name'])}<br><small class="muted">{e(market['settlement'])}</small></td><td>{e(o['selection'])}</td>
<td class="numeric">{pct(o['probability'])}</td><td class="numeric">{o['fair_decimal']:.3f}</td><td class="numeric">{us(o['fair_american'])}</td>
<td>{badge(o['confidence'])}</td><td class="blank" aria-label="Bookmaker quote unverified"></td><td>{source_links(market['input_evidence'] + row['fixture_evidence'], bundle['source_map'])}</td></tr>''')
        parts.append(f'''<details id="model-{e(row['id'])}"><summary>{e(label)} · {len(row['markets'])} model markets · {e(LABELS[row['status']])}</summary>
<p class="market-note">Uncalibrated captured research, never a live betting offer. Rungs are not proof of bookmaker availability. {e(row['markets'][0]['assumptions'])}</p>
{table(['Model market / convention', 'Outcome', 'Model %', 'Fair decimal', 'Fair US', 'Confidence', 'Book quote', 'Official inputs'], lines)}
<p class="market-note"><a href="{prefix}sports/{e(row['sport'])}.html#{e(row['id'])}">Input ledger and limitations →</a></p></details>''')
    return ''.join(parts) or '<div class="empty">No paired source-backed inputs support numerical prices for this category. No equal-strength fallback is used.</div>'


def models_page(bundle):
    market_families = [
        ('Winner / regulation 1X2', 'NHL, EuroLeague and MLB record baselines; EHF regulation 1X2', 'Only the explicitly documented model convention is priced; bookmaker settlement unconfirmed.', ['nhl-score', 'el-r7', 'mlb-standings', 'ehf-standings']),
        ('Handicap / spread', 'Illustrative EHF goal-handicap ladder only', 'Other sports lack the necessary paired score distribution; fields withheld.', ['ehf-standings']),
        ('Total / team totals', 'Illustrative EHF regulation goal totals only', 'No generic cricket total, guessed NBA pace or NHL goal total.', ['ehf-standings', 'nzc', 'nba-22', 'nhl-score']),
        ('Correct score / set / frame / leg scores', 'EHF top-three scores plus all other scores', 'Tennis, snooker and darts lack verified paired rate/format evidence.', ['ehf-standings', 'atp-op', 'wst-matches', 'pdc-schedule']),
        ('Player props / period markets / DNB', '', 'No reliable lineup, period rate or matching settlement; no price.', ['nba-22', 'nhl-score', 'rlwc']),
        ('Outrights / places / head-to-head golf & racing', '', 'Full fields, recent performance, place terms and market quotes not collected.', ['pga-bermuda', 'f1-usa'])]
    mr = [f'<tr><td>{e(f)}</td><td>{e(a)}</td><td>{e(b)}</td><td>{source_links(ids,bundle["source_map"])}</td></tr>' for f,a,b,ids in market_families]
    return f'''<h1>Our lines. Their limitations.</h1><p class="lede">Reproducible, zero-vig estimates wherever paired observed inputs exist. A model price is not proof that a bookmaker offers that market.</p>{warning()}
{table(['Market family investigated', 'Numerical coverage', 'Missing evidence / abstention', 'Official review'], mr)}
<div class="section"><h2>All captured model outcomes</h2><p class="market-note">The full complement of each modelled market is shown. Low and Medium are capped experimental tiers, not empirical accuracy. Values below remain historical calculations when their evidence expires.</p>
{market_tables(bundle['fixtures'],bundle)}</div>'''


def sport_page(category, bundle):
    rows = [r for r in bundle['fixtures'] if r['sport'] == category['sport']]
    ids = ''.join(f'<a href="#{e(r["id"])}">{e(r["participant_a"])}</a>' for r in rows)
    details = []
    for row in rows:
        title = row['participant_a'] + (' vs ' + row['participant_b'] if row['participant_b'] else '')
        facts = ''.join('<li>' + e(fact) + '</li>' for fact in row['form'])
        inputs = '<pre>' + e(json.dumps(row['inputs'], ensure_ascii=False, indent=2)) + '</pre>' if row['inputs'] else '<p class="muted small">Paired performance inputs: unconfirmed. Winner, confidence and fair odds remain blank.</p>'
        note = bundle['commentary'].get(row['id'])
        prose = f'<h3>{e(note["title"])}</h3><p>{e(note["text"])}</p>' if note else ''
        details.append(f'''<article class="research-card" id="{e(row['id'])}" data-start="{e(row.get('start_utc') or '')}" data-expires="{e(row['evidence_expires_utc'])}"><h3>{e(title)}</h3>
<div class="kicker"><span data-live-status>{badge(LABELS[row['status']], row['status'])}</span><span class="small muted">{e(row['competition'])} · {e(row['event_date'])}</span></div>
<p class="small"><strong>Participant order:</strong> {e(row['participant_order'])}. <strong>Exact UTC:</strong> {e(row.get('start_utc'))}.
<strong>Printed clock / qualifier:</strong> {e(row.get('printed_time'))}.</p>
{prose}<ul class="fact-list">{facts}</ul><p class="small muted">{e(row['notes'])}</p>
{source_links(row_sources(row) + (note['evidence'] if note else []), bundle['source_map'])}
<details><summary>Model inputs & approval blockers</summary>{inputs}<ul class="fact-list">{''.join('<li>'+e(reason)+'</li>' for reason in row['high_gate_rejections'])}</ul>
<p class="small muted">Evidence expires conservatively at {e(row['evidence_expires_utc'])}. Build time does not renew it.</p></details></article>''')
    return f'''<h1>{e(category['name'])}</h1><p class="lede">{e(category['limitations'])}</p>{warning('../')}
<div class="panel small"><strong>Coverage status:</strong> {badge(category['status'])} · Not exhaustive. {source_links([category['official_source'],category['olbg_source']],bundle['source_map'])}</div>
<div class="section">{fixtures_table(rows,bundle,'../',sport_select=False)}</div>
<div class="section"><h2>Fixture evidence & context</h2>{''.join(details) or '<div class="empty">No current official fixture extract supports a row here. Names, starts, odds and confidence are deliberately blank, rather than copied from an unverified legacy desk.</div>'}</div>
<div class="section"><h2>Experimental model markets</h2>{market_tables(rows,bundle,'../')}</div>'''


def flags_page(bundle):
    finding_rows = []
    for finding in bundle['facts_requiring_recheck']:
        finding_rows.append(f'''<tr><td>{e(finding['id'])}<br><strong>{e(finding['subject'])}</strong></td><td>{e(finding.get('observed'))}</td><td>{e(finding.get('inherited'))}</td><td>{e(finding['resolution'])}</td><td>{source_links(finding['sources'],bundle['source_map'])}</td></tr>''')
    for category in bundle['coverage']:
        finding_rows.append(f'''<tr><td>COVERAGE-{e(category['sport'])}</td><td>{e(category['name'])}: {e(category['limitations'])}</td><td></td><td>Partial or blocked; no unsupported replacement facts.</td><td>{source_links([category['official_source']],bundle['source_map'])}</td></tr>''')
    rrows = []
    for row in bundle['fixtures']:
        reason = '; '.join(row['high_gate_rejections'])
        rrows.append(f'''<tr data-search="{e(row['participant_a']+' '+(row['participant_b'] or '')+' '+reason)}" data-sport="{e(row['sport'])}"><td><a href="sports/{e(row['sport'])}.html#{e(row['id'])}">{e(row['participant_a'])}{' vs '+e(row['participant_b']) if row['participant_b'] else ''}</a><br><small>{e(row['id'])}</small></td><td>{badge(LABELS[row['status']],row['status'])}</td>
<td>{e(reason)}</td><td class="blank" aria-label="Approved selection unconfirmed"></td><td>{source_links(row_sources(row),bundle['source_map'])}</td></tr>''')
    return f'''<h1>Flagged for Review</h1><p class="lede">A published gap is better than an invented fact. These findings do not block the site; broken builds and links do.</p>{warning()}
<h2>Corrections, conflicts & collection limits</h2>{table(['Review ID / subject','Observed evidence / limitation','Inherited claim','Action / resolution','Official manual-review links'],finding_rows)}
<div class="section"><h2>Every current extract, reviewed row by row</h2><p class="market-note">Blank approved selections are intentional. Structural checks cannot certify sporting truth or betting performance.</p>{toolbar(bundle)}
{table(['Fixture / event','Time status','Why no High / approved bet','Approved selection','Official evidence'],rrows)}</div>'''


def sources_page(bundle):
    rows = []
    for s in bundle['sources']:
        official = [c['official_source'] for c in bundle['coverage'] if c['olbg_source'] == s['id']]
        rows.append(f'''<tr data-search="{e(s['name']+' '+s['scope'])}" data-sport=""><td><strong>{e(s['name'])}</strong><br><small>{e(s['id'])}</small></td><td>{e(s['kind'])}<br>{badge(s['status'])}</td><td class="small nowrap">{e(s['read_on'])}<br>{e(s.get('retrieved_at_utc'))}</td><td>{e(s['scope'])}<br><small class="muted">{e(s['limitations'])}</small></td><td>{source_links([s['id']] + official,bundle['source_map'])}</td></tr>''')
    return f'''<h1>A source is a trail, not a stamp.</h1><p class="lede">Each entry names exactly what was read. An official URL alone does not verify every claim made about its event.</p>
<div class="notice"><strong>Observation precision:</strong> manual reads have a date, not an invented per-page UTC timestamp. The ledger transcription time is {e(bundle['captured_at_utc'])}. Only automatic API responses carry exact retrieval times and raw JSON. Partial chunks, consent walls and empty JS shells are disclosed.</div>
{toolbar(bundle,False)}{table(['Source / ID','Role / read status','Observed date / exact retrieval','Observed fields & limitations','Source link'],rows)}
<div class="section downloads"><a href="data/release/evidence.json">Original evidence ledger</a><a href="data/release/bundle.json">Enriched research bundle</a><a href="coverage.html">Coverage audit</a></div>'''


def methodology_page(bundle):
    return f'''<h1>Transparent by design.</h1><p class="lede">All estimates are reproducible from the saved observations. None has been validated as a betting edge.</p>{warning()}
<div class="body-copy"><h2>1. Facts, assumptions and offers are different things</h2><p>Official schedules and statistics support only the fields actually observed. Display clocks without a timezone are not converted. Model probabilities, score means and fair odds are calculated estimates. Bookmaker quotes, settlement, lineup confirmation and head-to-head fields stay blank unless specifically evidenced.</p>
<h2>2. Record-only match-winner baseline</h2><p>For each team, use its observed games and wins, treating an NHL overtime loss as a loss in a two-way result. A symmetric Beta(2,2) prior gives <code>r = (wins + 2) / (games + 4)</code>. Compare teams using <code>p(A) = rA(1−rB) / [rA(1−rB) + rB(1−rA)]</code>. Both sides must have a nonempty, consistent record. Missing inputs cause abstention, never a neutral 50% line.</p>
<p>This log5-style formula is a baseline assumption, not an empirically fitted skill rating. It ignores opposition strength, travel, injuries, starters and venue. NBA zero-game sides cannot be priced. MLB inputs are explicitly regular-season records, not postseason form. A sensitivity range varies the symmetric prior across 2, 4 and 8 games and a hypothetical home odds multiplier across 1.00 and 1.15; it is not a statistical confidence interval.</p>
<h2>3. Illustrative handball regulation lines</h2><p>For each side, average its observed goals scored per game with the opponent’s goals conceded per game. Assume two independent Poisson scores. Enumerate the distribution to obtain regulation 1X2 (including draw), half-goal handicaps, totals, team totals and the three most likely scores plus an all-other-scores outcome. A retained score grid is normalized only after its missing mass is below 10⁻¹⁰.</p>
<p>Total ladders are centered at <code>floor(mean total)+0.5</code> and ±2 goals. Handicap ladders are centered on the mean difference at half-goal rungs, also ±2. No rung is tuned to reach 70% or squeeze inside a price window. The four-game samples, Poisson variance, independence and missing availability are material limitations; every handball line is capped Low.</p>
<h2>4. Zero-vig odds and the High window</h2><p>Decimal fair odds are <code>1/p</code>. American odds are <code>−100p/(1−p)</code> above 50%, or <code>+100(1−p)/p</code> otherwise. Values displayed are rounded; gates compare the unrounded numbers. There is no artificial five-percent bookmaker margin, no −250 clamp and no market-implied tip probability substituted for an independent estimate.</p>
<p>At zero vig, a probability above 70% and fair odds no shorter than −250 intersect only at <code>0.70 &lt; p ≤ 5/7</code>. That narrow arithmetic interval is not evidence of forecast quality. A real quoted price can differ; an expected-value comparison requires a time-stamped quote for the same outcome and settlement. No comparable quote is approved here.</p>
<h2>5. Confidence and abstention</h2><ul><li><strong>Low:</strong> experimental winner estimates below 60% or with fewer than eight observed games on either side; all illustrative handball outcomes.</li>
<li><strong>Medium:</strong> an uncalibrated record-baseline winner at least 60%, with at least eight observed games on each side. This is a descriptive tier, not a measured win rate.</li>
<li><strong>High:</strong> disabled in this release. It would require independent held-out reliability evidence, fresh exact timing, a valid −250…+10000 quoted price with matching settlement, confirmed relevant form/history and a unique, evidence-grounded preview of at least 30 words. A high numerical model output alone is insufficient.</li></ul>
<p>The user’s requested High board is therefore empty, not padded with trivial favorites or unsupported alternate lines. All approved selection fields are null.</p>
<h2>6. Time, freshness and updates</h2><p>The default build cutoff is actual UTC, not midnight on a hardcoded date. Starts at or before the cutoff are marked “start time passed”, which is not a fabricated result. Date-only rows are not declared currently upcoming. Manual date-only observations expire conservatively at the following UTC midnight; exact API observations expire after 24 hours. Browser-side expiry removes current projection cells after either start or expiry without changing archived calculations.</p>
<p>Building never renews observation dates. Optional automatic collectors cover only official NHL and MLB JSON, preserve raw responses, and leave old dates unchanged on failure. Other sports become visibly stale until genuinely reread. Automated scheduled publication updates the artifact, not repository branches.</p>
<h2>7. What is not finished</h2><p>Worldwide seven-day match coverage, all bookmaker markets, sport-specific validated models, current lineups and full historical backtests remain incomplete. The coverage and row-level review pages name the gaps. No site build, URL check, model formula or official homepage visit substitutes for this missing work.</p>
<p><a href="https://github.com/buffedlizard55-lab/OLBG1/blob/arena/6ad5a3a8-olbg1/scripts/release_model.py">Review the model implementation</a> · <a href="data/release/evidence.json">Inspect the exact inputs</a></p></div>'''


def discovery_page(bundle):
    return f'''<h1>How OLBG discovery was mapped.</h1><p class="lede">An empirical reading of the public taxonomy and rendered category content, not a claim to have replicated OLBG’s private systems.</p>
<div class="body-copy"><h2>Observed public surface</h2><p>All 17 eligible category hubs were opened at their numbered routes. Rendered cards supply event labels, competition context, displayed times and tip or market snippets. The route IDs and official review destinations appear on <a href="coverage.html">Coverage</a>. Load More and unread chunks mean the captured front page is not the complete event database.</p>
<h2>Extraction contract</h2><ol><li>Use the category route as discovery, never as an official record of a participant’s form.</li><li>Resolve the actual event and participants against a league, governing body or official tournament source.</li><li>Record field-specific evidence, observation precision, competition format, timezone and source limitations.</li><li>Do not interpret tip shares as independent win probabilities or call a fair model line a bookmaker quote.</li><li>Keep actual market availability and settlement separate. A winner, handicap, total or player prop needs its own matching contract; discovery text alone is insufficient.</li></ol>
<h2>Known failure modes</h2><p>OLBG display clocks disagree across pages and greyhound event labels. Aussie Rules and eSports returned “No tips found”; this does not show that no real fixtures exist. Some official destinations return navigation, consent screens or broken dynamic lists. These are recorded as blockers, not successful verification.</p>
<h2>Excluded categories</h2><p>Soccer / football, American football, boxing, UFC / MMA, hurling, horse racing, cycling and specials / entertainment are excluded from canonical sport coverage. Gaelic football remains included as its distinct OLBG category, as does Australian rules.</p>
<h2>Collection limits</h2><p>Private endpoints, pagination payloads, bookmaker integrations, every odds market and OLBG’s internal ranking / tipster algorithms have not been fully reverse-engineered. The current release does not claim otherwise. Public evidence is collected without bypassing access controls.</p></div>
<div class="section downloads"><a href="coverage.html">All route IDs and official review links</a><a href="sources.html">Source read ledger</a><a href="flagged.html">Open issues</a></div>'''


def archive_page(bundle, archive):
    desks = sorted({p.parent.name for p in ROOT.glob('*/index.html') if p.parent.name not in {'archive','sports'}})
    links = ''.join(f'<li><a href="../{e(name)}/index.html">{e(name)} desk</a> — retained, unrecertified historical work</li>' for name in desks)
    return f'''<h1>One front door. History intact.</h1><p class="lede">Previous sessions are preserved for auditability, not presented as competing current recommendations.</p>
<div class="notice"><strong>Historical labels are not current verification.</strong> Old High picks, counts, form, times and bookmaker-like quotes may be stale, unsupported or contradicted. Use the canonical evidence ledger for the current release.</div>
<div class="two-col"><section class="panel"><h2>Previous primary dashboard</h2><p>The complete root and sport pages from before this release were copied with conspicuous archive warnings and rebased local links.</p>
<p><a href="pre-release-20261022/index.html">Open the archived primary desk →</a></p><p><a href="pre-release-20261022/release-review.html">Earlier 134-row safety audit →</a></p><p><a href="../data/release/archive.json">Original-file SHA-256 manifest</a></p></section>
<section class="panel"><h2>Attribution & handoffs</h2><p>All namespaced session outputs remain unchanged. PR #63’s consolidation approach informed the single-entrypoint / archive decision; its builder, fixed clock and inherited pricing were not imported as current evidence.</p>
<p><a href="https://github.com/buffedlizard55-lab/OLBG1/pull/63">PR #63</a> · <a href="../COORDINATION.md">Coordination record</a></p></section></div>
<section class="section panel"><h2>Historical session desks</h2><ul>{links}</ul><p class="small muted">These pages predate the canonical release. Their own claims are not endorsed by linking them.</p></section>'''


def analysis_page(bundle):
    cards = []
    lookup = {r['id']:r for r in bundle['fixtures']}
    for fid, note in bundle['commentary'].items():
        if fid not in lookup:
            continue
        row = lookup[fid]
        cards.append(f'''<article class="research-card" data-start="{e(row.get('start_utc') or '')}" data-expires="{e(row['evidence_expires_utc'])}"><h2>{e(note['title'])}</h2><p>{e(note['text'])}</p>
<p><span data-live-status>{badge(LABELS[row['status']],row['status'])}</span> <a class="small" href="sports/{e(row['sport'])}.html#{e(fid)}">Fixture inputs & model →</a></p>{source_links(note['evidence'],bundle['source_map'])}</article>''')
    return f'''<h1>Context before conviction.</h1><p class="lede">Individual research notes grounded in the observed official records. These are not High-confidence betting previews.</p>{warning()}{''.join(cards)}'''


def audit_page(bundle):
    return f'''<h1>What the audit proves.</h1><p class="lede">Line inventory, structural validation and official factual checks have different scopes. They are not interchangeable.</p>{warning()}
<div class="body-copy"><h2>Fresh factual review</h2><p>This release transcribes {len(bundle['fixtures'])} fixture/event observations from identified official sources, with field-level references and explicit read scope. All 17 OLBG hubs were read at their first chunk. The <a href="flagged.html">review ledger</a> records missing times, absent inputs, orientation corrections, conflicting records and excluded inherited prices. This is not a manual factual review of every line in every historical desk.</p>
<h2>Whole-repository line inventory</h2><p>The inventory tool enumerates tracked and newly authored files, counts UTF-8 lines, fingerprints every file and records line numbers for source URLs and risk terms. It supplies exact GitHub manual-review links and distinguishes generated, canonical and historical files. It is an automated inspection aid, not proof that every historical sentence is true.</p>
<h2>Executable gates</h2><p>The current validator checks eligible categories, source roles, paired inputs, probability complements, fair-odds arithmetic, past-start handling, freshness, no neutral missing-data prices, absent approved bets, unique commentary and local links including fragments. Unit tests exercise malformed data, timezone ambiguity, draw handling, score-grid mass, boundary odds and failed refreshes. Live external URLs are not certified merely by structural tests.</p>
<h2>Preservation</h2><p>Prior root HTML is archived; every namespaced desk and dataset is retained unchanged. The independent T56/T57 audit scripts and reports are not overwritten. The old generators remain historical and are no longer the canonical publishing command.</p>
<h2>Unresolved user goals</h2><p>Exhaustive all-market, all-match coverage and empirically supported new High selections are not completed. Rather than disguise those gaps with verification labels, the release exposes them and approves zero bets.</p></div>
<div class="section downloads"><a href="reports/RELEASE_T58.md">Release audit report</a><a href="reports/release_file_inventory.csv">File-by-file line inventory</a><a href="reports/release_line_findings.csv">Line-level URL / risk register</a><a href="data/release/bundle.json">Every current row & gate reason</a></div>'''


def build(as_of=None):
    archive = preserve()
    data = load(DATA/'evidence.json')
    now = timestamp(as_of) if as_of else datetime.now(timezone.utc)
    sources = {s['id']:s for s in data['sources']}
    rows = [enrich(r,sources,now,data['coverage_window']) for r in data['fixtures']]
    rows.sort(key=lambda r:(r['event_date'],r.get('start_utc') or '~',r['sport'],r['id']))
    bundle = {k:v for k,v in data.items() if k != 'fixtures'}
    bundle.update(as_of_utc=iso(now), model_version=MODEL_VERSION, fixtures=rows,
                  commentary=load(DATA/'commentary.json'), source_map=sources,
                  counts={'fixtures':len(rows),'sports':len(data['coverage']),
                    'models':sum(bool(r['markets']) for r in rows),
                    'model_markets':sum(len(r['markets']) for r in rows),
                    'model_outcomes':sum(len(m['outcomes']) for r in rows for m in r['markets']),
                    'approved_bets':0,'high':0,'statuses':dict(Counter(r['status'] for r in rows))})
    pages = {}
    def page(path,title,body,active=''):
        pages[path]=shell(title,title,body,path,bundle,active)
    page('index.html','Independent evidence-first research',index_page(bundle),'index.html')
    page('sports.html','All 17 sport reviews','<h1>Every sport. A clear status.</h1><p class="lede">Open a category for observed fixtures, readable tables, official evidence and the gaps that stop a bet.</p>'+warning()+sport_cards(bundle),'sports.html')
    page('coverage.html','Coverage and collection limits',coverage_page(bundle),'coverage.html')
    page('picks.html','Independent experimental model lines',models_page(bundle),'picks.html')
    page('flagged.html','Flagged for Review',flags_page(bundle),'flagged.html')
    page('sources.html','Source observation ledger',sources_page(bundle))
    page('methodology.html','Model and evidence methodology',methodology_page(bundle))
    page('reverse-engineering.html','OLBG public discovery mapping',discovery_page(bundle))
    page('analysis.html','Evidence-grounded research notes',analysis_page(bundle))
    page('predictions.html','High-confidence board','<h1>High confidence has to be earned.</h1><p class="lede">No selections qualify. No unsupported 30-word previews are generated to fill this page.</p>'+warning()+'<div class="panel body-copy"><h2>Why the board is empty</h2><p>A numerical probability above 70% is not a measured success rate. The saved inputs lack held-out calibration, matching bookmaker settlement, fully confirmed participant availability and sufficiently complete recent history. Fair odds in the requested −250…+10000 range do not fix those gaps.</p><p><a href="analysis.html">Read the individual research notes</a> · <a href="flagged.html">Review every blocked row</a> · <a href="methodology.html">See the exact gates</a></p></div>')
    page('audit.html','Release audit scope and line inventory',audit_page(bundle))
    page('archive/index.html','Historical desk archive',archive_page(bundle,archive),'archive/index.html')
    for category in bundle['coverage']:
        page('sports/'+category['sport']+'.html',category['name']+' evidence and analysis',sport_page(category,bundle),'sports.html')
    for alias in ('verification.html','live-verification.html','live-refresh.html'):
        page(alias,'Current verification and refresh status','<h1>Verification belongs to the evidence.</h1><p class="lede">Earlier review pages are preserved in the archive. This release uses one canonical row-level register.</p>'+warning()+'<div class="panel"><p><a href="flagged.html">Current Flagged for Review →</a></p><p><a href="sources.html">Actual source read dates →</a></p><p><a href="coverage.html">Refresh scope and limitations →</a></p><p><a href="archive/pre-release-20261022/'+alias+'">Previous page, unrecertified archive →</a></p></div>')
    page('404.html','Page not found','<h1>That page is not here.</h1><p class="lede">The canonical research desk and all historical desks are still available.</p><div class="downloads"><a href="index.html">Return to dashboard</a><a href="archive/index.html">Find a historical page</a></div>')
    for path,text in pages.items():
        target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text+'\n')
    # source_map is a rendering convenience, not duplicated in the public JSON.
    public = {k:v for k,v in bundle.items() if k != 'source_map'}
    (DATA/'bundle.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
    stream=io.StringIO(newline='');writer=csv.writer(stream)
    writer.writerow(['id','sport','competition','participant_a','participant_b','event_date','start_utc','status','projected_winner','fair_decimal','fair_american','model_probability','experimental_confidence','approved_selection','official_sources'])
    for row in rows:
        w=row['winner_projection'] if row['status']=='scheduled' else None
        writer.writerow([row['id'],row['sport'],row['competition'],row['participant_a'],row['participant_b'],row['event_date'],row['start_utc'],row['status'],w['selection'] if w else '',w['fair_decimal'] if w else '',w['fair_american'] if w else '',w['probability'] if w else '',row['confidence'] if w else '', '', '; '.join(sources[sid]['url'] for sid in row_sources(row))])
    (DATA/'rows.csv').write_text(stream.getvalue())
    manifest={'builder':'scripts/release_build.py','as_of_utc':bundle['as_of_utc'],
              'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (DATA/'evidence.json',DATA/'commentary.json')},
              'pages':sorted(pages),'counts':bundle['counts']}
    (DATA/'build.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f"Canonical build: {len(pages)} pages, {len(rows)} source-linked extracts, {bundle['counts']['model_outcomes']} experimental prices, 0 approved bets. Cutoff {bundle['as_of_utc']}")
    return public


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of',help='Explicit UTC cutoff for reproducible tests; default is actual UTC')
    args=parser.parse_args();build(args.as_of)
