#!/usr/bin/env python3
"""Build the root 15-sport OLBG research desk from the primary data.

Produces server-rendered HTML (no JavaScript dependency):

  index.html            landing dashboard + executive summary
  sports/<15 slugs>.html per-category match tables
  predictions.html      high-confidence picks register
  markets.html          full multi-market explorer
  flagged.html          Flagged for Review register
  analysis.html         methodology & findings

Every fixture row carries its recorded official governing-body source link(s).
Originated prices are labelled estimates, never bookmaker quotes. Blank cells
are unverified values left empty, never inferred.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SPORTS_DIR = ROOT / "sports"
SNAPSHOT = "2026-10-22T12:29:50Z"  # must match data/current/site-manifest.json generated_at
BUILT_LABEL = "23 Oct 2026 · 19:30 UTC"

IN_SCOPE = [
    ("golf", "Golf"),
    ("volleyball", "Volleyball"),
    ("rugby-union", "Rugby Union"),
    ("cricket", "Cricket"),
    ("snooker", "Snooker"),
    ("darts", "Darts"),
    ("baseball", "Baseball"),
    ("gaelic-football", "Gaelic Sports"),
    ("greyhounds", "Greyhounds"),
    ("tennis", "Tennis"),
    ("motor-racing", "Motor Racing"),
    ("handball", "Handball"),
    ("ice-hockey", "Ice Hockey"),
    ("basketball", "Basketball"),
    ("rugby-league", "Rugby League"),
]
SLUGS = [s for s, _ in IN_SCOPE]
NAMES = dict(IN_SCOPE)
OUT_OF_SCOPE = ["aussie-rules", "esports"]
EXTERNAL_SVG = (
    '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    ' stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M14 3h7v7M21 3L10 14M10 3H4v17h17v-6"/></svg>'
)

fix = lambda t: html.escape(str(t), quote=True) if t is not None else ""

fixtures = json.loads((DATA / "fixtures.json").read_text(encoding="utf-8"))["fixtures"]
lines_by_id = {
    l["id"]: l for l in json.loads((DATA / "lines.json").read_text(encoding="utf-8"))["lines"]
}
preds_by_id = {
    p["match_id"]: p
    for p in json.loads((DATA / "predictions.json").read_text(encoding="utf-8"))["predictions"]
}
coverage = json.loads((DATA / "coverage.json").read_text(encoding="utf-8"))
COV_BY_SLUG = {c["sport"]: c for c in coverage["included"]}

NOW = datetime(2026, 10, 23, 19, 30, tzinfo=timezone.utc)
REV = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                     capture_output=True, text=True).stdout.strip() or "unknown"


def fixture_state(m):
    s = m.get("start_utc")
    if not s:
        return "untimed"
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.date() == NOW.date():
        return "today"
    return "upcoming" if dt > NOW else "elapsed"


def conf_badge(conf):
    return {'high': 'green', 'medium': 'amber', 'low': 'low'}.get(conf, 'gray')


def state_badge(st):
    return {'upcoming': 'green', 'today': 'amber', 'elapsed': 'gray', 'untimed': 'gray'}.get(st, 'gray')


def state_label(st):
    return {'upcoming': 'Upcoming', 'today': 'Today', 'elapsed': 'Elapsed', 'untimed': 'Time not stated'}.get(st, st)


def sources_html(fixture, label="Official source"):
    stack = []
    for src in (fixture.get("sources") or []):
        name = fix(src.get("name") or label)
        url = src.get("url") or ""
        if url.startswith("https://"):
            stack.append(f'<a class="source-link" href="{url}" target="_blank" rel="noopener noreferrer">{name}{EXTERNAL_SVG}</a>')
        else:
            stack.append(fix(name))
    return '<div class="sources-stack">' + "".join(stack) + "</div>" if stack else '<span class="secondary">no source recorded</span>'


def match_cell(m, same_page=False):
    aid = m["id"]
    when = m.get("start_utc")
    if when:
        dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
        time_html = f'<span class="time">{dt:%d %b}<small>{dt:%H:%M} UTC</small></span>'
    else:
        time_html = '<span class="time">-<small>time not stated</small></span>'
    versus = f'{fix(m.get("home"))} <span class="versus">vs</span> {fix(m.get("away") or "-")}'
    comp = f'<small>{fix(m.get("competition"))}</small>'
    link = f'#{aid}' if same_page else f'sports/{m["sport"]}.html#{aid}'
    match_html = (f'<div class="match"><a href="{link}">{versus}</a>{comp}</div>')
    if m.get("venue"):
        match_html += f'<div class="secondary venue">{fix(m["venue"])}</div>'
    return time_html, match_html


def markets_html(line):
    """Render every originated market for one line as a compact block."""
    blocks = []
    for mk in line.get("markets", []):
        outs = []
        for o in mk.get("outcomes", []):
            price = o.get("american")
            outs.append(f'{fix(o.get("selection"))} <span class="number price">{fix(price)}</span>')
        line_txt = f" {mk['line']}" if mk.get("line") else ""
        blocks.append(
            f'<div class="market-row"><span class="secondary market-key">{fix(mk.get("name"))}{fix(line_txt)}:</span> '
            + " <span class=" + '"' + "sep" + '"' + ">/</span> ".join(outs) + "</div>"
        )
    if not blocks:
        return '<span class="secondary">no originated markets</span>'
    return '<div class="markets">' + "".join(blocks) + "</div>"


def prediction_html(p, line):
    return (
        f'<div class="prediction"><p class="prose">{fix(p["text"])}</p>'
        f'<p class="secondary bet-line">Bet line: {fix(p["bet_line"])} · {state_badge_html(line.get("confidence"))}</p>'
        f'{sources_line(p)}</div>'
    )


def sources_line(obj):
    stack = []
    for src in (obj.get("sources") or []):
        url = src.get("url") or ""
        name = fix(src.get("name") or "official source")
        if url.startswith("https://"):
            stack.append(f'<a class="source-link" href="{url}" target="_blank" rel="noopener noreferrer">{name}{EXTERNAL_SVG}</a>')
    return '<div class="sources-stack">' + "".join(stack) + "</div>" if stack else ""


def state_badge_html(conf):
    return f'<span class="badge {conf_badge(conf)}">{fix(conf).title()}</span>'


def page_shell(title, active="index", base=""):
    """base = "" for root pages, "../" for pages inside sports/."""
    nav = []
    items = [
        ("index.html", "Overview"),
        ("picks.html", "Match list"),
        ("markets.html", "Market explorer"),
        ("predictions.html", "High-confidence picks"),
        ("sports.html", "All sports"),
        ("flagged.html", "Flagged for Review"),
        ("analysis.html", "Analysis & findings"),
        ("sources.html", "Sources & evidence"),
        ("methodology.html", "Methodology"),
        ("reverse-engineering.html", "OLBG discovery"),
        ("archive.html", "Earlier snapshots"),
    ]
    for href, label in items:
        cls = "nav-link active" if href == active else "nav-link"
        nav.append(f'<a class="{cls}" href="{base}{href}"><span>{fix(label)}</span></a>')
    sidebar = f"""<aside class="sidebar" aria-label="Primary navigation">
<a class="brand" href="{base}index.html"><span class="brand-mark"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20V10m7 10V4m7 16v-7M2 22h20"/></svg></span><span><strong>OLBG<span style="font-weight:400">.</span></strong><small>RESEARCH DESK</small></span></a>
<div class="nav-label">WORKSPACE</div>{''.join(nav)}
<div class="nav-label">RESEARCH &amp; TRANSPARENCY</div>
<div class="sidebar-bottom"><div class="status-card"><strong><span class="status-dot"></span> Evidence-first research</strong><p>Originated prices are estimates, not bookmaker quotes.<br>Blank means unverified — never filled in.</p></div><p>Independent project · Not affiliated with OLBG</p></div>
</aside>"""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Independent source-linked match research for the 15 sports in the brief. Not affiliated with OLBG."><title>{fix(title)} · OLBG Research</title><link rel="icon" href="{base}assets/current-mark.svg" type="image/svg+xml"><link rel="stylesheet" href="{base}assets/current-style.css"></head><body data-snapshot="{SNAPSHOT}"><a class="skip" href="{base}#main">Skip to content</a>{sidebar}<div class="layout"><header class="topbar"><button class="mobile-menu" id="menu-button" aria-label="Open navigation" aria-expanded="false" aria-controls="sidebar"><svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button><div class="crumb"><span class="workspace-label">Research workspace <span aria-hidden="true">/</span></span><strong>{fix(title)}</strong></div><div class="topbar-right"><span><span class="status-dot"></span><span class="freshness">Snapshot 21 Oct 2026</span></span><span class="date">{BUILT_LABEL}</span><a href="https://github.com/buffedlizard55-lab/OLBG1" aria-label="View project on GitHub"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 5L2 12l6 7M16 5l6 7-6 7M14 3l-4 18"/></svg></a></div></header><main class="main" id="main">"""


def page_footer(base=""):
    return f"""<footer class="footer"><span>Independent research, not betting guarantees. 18+ · Never stake what you cannot afford to lose.</span><span>Built {BUILT_LABEL} · revision {REV} · <a href="{base}methodology.html">How this works</a> · <a href="{base}flagged.html">Flagged for Review</a></span></footer></main></div></body></html>"""


def sport_rows(slug):
    return [m for m in fixtures if m["sport"] == slug]


def rendered_markets(line):
    return markets_html(line)


# ---------------------------------------------------------------- index.html
def match_tr_attrs(m, same_page=False):
    return ""


def build_index():
    in_scope = [m for m in fixtures if m["sport"] in SLUGS]
    lines = [l for l in lines_by_id.values() if l["sport"] in SLUGS]
    high = [l for l in lines if l["confidence"] == "high"]
    n_today = sum(1 for m in in_scope if fixture_state(m) == "today")
    n_up = sum(1 for m in in_scope if fixture_state(m) == "upcoming")
    n_elapsed = sum(1 for m in in_scope if fixture_state(m) == "elapsed")
    n_untimed = sum(1 for m in in_scope if fixture_state(m) == "untimed")
    priced_in_scope = sum(1 for l in lines)
    markets_n = sum(len(l.get("markets", [])) for l in lines)

    def fixture_rows(selection_pred):
        rows = []
        for m in selection_pred:
            st = fixture_state(m)
            line = lines_by_id.get(m["id"])
            time_html, match_html = match_cell(m)
            conf = line["confidence"] if line else "-"
            pick = fix(line["pick"]) if line else "-"
            price = fix(line["pick_american"]) if line else "-"
            conf_html = state_badge_html(conf) if line else '<span class="badge gray">-</span>'
            p = preds_by_id.get(m["id"])
            pred_html = f'<div class="prediction">{fix(p["text"])}</div>' if p and line and line["confidence"] == "high" else '<span class="secondary">-</span>'
            src = sources_html(m)
            rows.append((m, st, time_html, match_html, conf_html, pick, price, pred_html, src))
        return rows

    today_rows = fixture_rows([m for m in in_scope if fixture_state(m) == "today"])
    today_rows.sort(key=lambda r: r[0].get("start_utc") or "")
    up_rows = fixture_rows([m for m in in_scope if fixture_state(m) == "upcoming"])
    up_rows.sort(key=lambda r: r[0].get("start_utc") or "")

    def row_tr(m, st, time_html, match_html, conf_html, pick, price, pred_html, src):
        st_cls = {"today": "today", "upcoming": "upcoming", "elapsed": "elapsed", "untimed": "untimed"}.get(st, "")
        return (
            f'<tr id="{m["id"]}-desk" class="fixture-row {st_cls}">'
            f'<td>{time_html}</td>'
            f'<td>{match_html}</td>'
            f'<td><span class="badge {state_badge(st)}">{state_label(st)}</span></td>'
            f'<td>{conf_html}</td>'
            f'<td>{pick}</td>'
            f'<td><span class="number price">{price}</span></td>'
            f'<td>{pred_html}</td>'
            f'<td>{src}</td>'
            f'</tr>'
        )

    today_body = "".join(row_tr(*r) for r in today_rows)
    up_body = "".join(row_tr(*r) for r in up_rows)

    sport_cards = "".join(
        f'<a class="sport-card" href="sports/{slug}.html">'
        f'<span class="sport-icon"><svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c-5 5-5 13 0 18M12 3c5 5 5 13 0 18"/></svg></span>'
        f'<span><strong>{fix(name)}</strong><small>{COV_BY_SLUG.get(slug, {}).get("fixtures", "?")} listings · {COV_BY_SLUG.get(slug, {}).get("status", "partial")}</small></span>'
        f'<span class="arrow"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M14 7l5 5-5 5"/></svg></span>'
        f'</a>'
        for slug, name in IN_SCOPE
    )

    content = f"""<section class="panel pad">
<div class="card-topline"><strong>{len(in_scope)} captured listings across the 15 brief sports</strong></div>
<p class="tiny">Fixture window captured 21 Oct 2026 (runs to 28 Oct 2026). Prices are our own originated fair prices — estimates, not bookmaker offers — and every row links to the governing body or organiser that supplied it.</p>
</section>

<div class="kpis">
<div class="kpi"><div class="kpi-label">In-scope fixtures<span class="kpi-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg></span></div><div class="kpi-value">{len(in_scope)}</div><div class="kpi-foot"><span>{n_today} today · {n_up} upcoming · {n_elapsed} elapsed · {n_untimed} time not stated</span></div></div>
<div class="kpi"><div class="kpi-label">Originated price books<span class="kpi-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20V10m7 10V4m7 16v-7M2 22h20"/></svg></span></div><div class="kpi-value">{priced_in_scope}</div><div class="kpi-foot">{markets_n} market lines · all inside −250…+10000</div></div>
<div class="kpi"><div class="kpi-label">High-confidence picks (desk tier)<span class="kpi-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l8 3v6c0 5-8 9-8 9S4 17 4 12V6zM9 12l2 2 4-5"/></svg></span></div><div class="kpi-value">{len(high)}</div><div class="kpi-foot"><span>{sum(1 for l in high if l['sport'] in SLUGS)} in the 15 brief sports</span> · conviction ≥0.60</div></div>
<div class="kpi"><div class="kpi-label">Unique predictions<span class="kpi-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6z"/></svg></span></div><div class="kpi-value">30</div><div class="kpi-foot"><span>{sum(1 for p in preds_by_id.values() if next((l for l in lines_by_id.values() if l['id']==p['match_id']), None) and lines_by_id[p['match_id']]['sport'] in SLUGS)} in the 15 brief sports</span> · ≥30 words each</div></div>
</div>

<div class="notice neutral"><strong>Confidence bar — read before the picks.</strong> A pick is "high confidence" on this desk when its originated conviction is at least 0.60 <em>and</em> its price sits inside −250…+10000. No price in this window independently clears a strict greater-than-70% model-probability bar (the best originated price is −250, ≈71% implied). Picks shorter than −250 are not published as High. Nothing here is a betting recommendation.</div>

<section class="panel">
<div class="panel-head"><div><h2>Highest-confidence picks — today, 23 Oct 2026 (UTC)</h2><p>Exact UTC starts from official sources · table state shows elapsed vs still-to-come</p></div><a class="text-link" href="predictions.html">View all picks <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M14 7l5 5-5 5"/></svg></a></div>
<div class="table-wrap">
<table class="wide-table"><caption class="sr-only">Today's in-scope fixtures, official sources and originated selections</caption>
<thead><tr><th><button class="sort-btn" data-sort="start">Start (UTC) ↕</button></th><th>Match / event</th><th>State</th><th>Confidence</th><th>Our selection</th><th>Fair price</th><th>Prediction (High picks)</th><th>Official source</th></tr></thead>
<tbody>{today_body}</tbody></table>
</div>
<p class="table-note">{len(today_rows)} in-scope fixtures captured for 23 Oct 2026. Aussie Rules and eSport rows are captured in the data but outside this brief.</p>
</section>

<section class="panel">
<div class="panel-head"><div><h2>Upcoming — 24 to 28 Oct 2026 (UTC)</h2><p>Fixtures with published start times after today, across the 15 brief sports</p></div><a class="text-link" href="markets.html">Explore every market <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M14 7l5 5-5 5"/></svg></a></div>
<div class="table-wrap">
<table class="wide-table"><caption class="sr-only">Upcoming in-scope fixtures, official sources and originated selections</caption>
<thead><tr><th><button class="sort-btn" data-sort="start">Start (UTC) ↕</button></th><th>Match / event</th><th>Competition</th><th>Confidence</th><th>Our selection</th><th>Fair price</th><th>Prediction (High picks)</th><th>Official source</th></tr></thead>
<tbody>{up_body}</tbody></table>
</div>
<p class="table-note">{len(up_rows)} upcoming in-scope fixtures. Rows without an originated price have no two-sided market supported by the recorded inputs.</p>
</section>

<div class="section-heading"><div><h2>Explore by sport</h2><p>One category page per sport in the brief, with full market tables and sources.</p></div></div>
<div class="sport-grid">{sport_cards}</div>

<div class="grid-two">
<section class="panel pad">
<h3>How to read the tables</h3>
<ul class="checklist">
<li><span class="ring"></span>Confidence: <span class="badge green">High</span> desk tier (conviction ≥0.60, price −250…+10000) · <span class="badge amber">Medium</span> · <span class="badge gray">Low</span></li>
<li><span class="ring"></span>Fair prices are our own originated estimates, shaded −250…+10000; they are not bookmaker odds.</li>
<li><span class="ring"></span>Every row links to the governing body, league or tour that supplied the fixture facts.</li>
<li><span class="ring"></span>Blank cells are values the publisher did not state — left empty, never inferred.</li>
</ul>
</section>
<section class="panel pad">
<h3>What needs review</h3>
<ul class="checklist">
<li><span class="ring"></span>Golf, greyhounds and motor racing are event-only in OLBG — no two-sided match market exists for them (see <a href="flagged.html">Flagged for Review</a>).</li>
<li><span class="ring"></span>Five high-confidence picks per sport is the aim; this window delivers fewer for several sports — gaps are registered, not filled.</li>
<li><span class="ring"></span>This session could not independently re-fetch official feeds (sandbox egress is GitHub/npm/PyPI only); all rows rest on recorded verification and are flagged for manual re-verification.</li>
</ul>
</section>
</div>
"""
    html_doc = page_shell("OLBG research desk — landing", active="index") + f'<header class="page-heading"><div><p class="eyebrow">OFFICIAL FIXTURES · ORIGINATED LINES · EXPLICIT FLAGS</p><h1>The match research desk</h1><p>A source-linked register of matches for the 15 sports in the brief: Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball, Rugby League.</p></div></header>' + content + page_footer()
    (ROOT / "index.html").write_text(html_doc, encoding="utf-8")
    print("wrote index.html")


# ---------------------------------------------------------------- sport pages
def build_sport(slug):
    rows = sport_rows(slug)
    rows.sort(key=lambda m: (fixture_state(m) != "upcoming", fixture_state(m) != "today", m.get("start_utc") or "", m["id"]))
    groups = {}
    for m in rows:
        groups.setdefault(fixture_state(m), []).append(m)
    order = ["upcoming", "today", "untimed", "elapsed"]

    body_parts = []
    for st in order:
        items = groups.get(st, [])
        if not items:
            continue
        body_parts.append(f'<h3 class="section-heading"><span>{state_label(st)} ({len(items)})</span></h3>')
        trs = []
        for m in items:
            line = lines_by_id.get(m["id"])
            time_html, match_html = match_cell(m, same_page=True)
            conf = line["confidence"] if line else "-"
            conf_html = state_badge_html(conf) if line else '<span class="badge gray">-</span>'
            pick = fix(line["pick"]) if line else "-"
            price = fix(line["pick_american"]) if line else "-"
            mk = markets_html(line) if line else '<span class="secondary">no originated markets</span>'
            p = preds_by_id.get(m["id"])
            pred = prediction_html(p, line) if (p and line and line["confidence"] == "high") else '<span class="secondary">-</span>'
            trs.append(
                f'<tr id="{m["id"]}">'
                f'<td>{time_html}</td>'
                f'<td>{match_html}</td>'
                f'<td>{mk}</td>'
                f'<td>{conf_html}</td>'
                f'<td>{pick}</td>'
                f'<td>{pred}</td>'
                f'<td><span class="badge {state_badge(st)}">{state_label(st)}</span></td>'
                f'<td>{sources_html(m)}</td>'
                f'</tr>'
            )
        body_parts.append(
            f'<div class="table-wrap"><table class="wide-table"><caption class="sr-only">{fix(NAMES[slug])} fixtures</caption>'
            f'<thead><tr><th>Start (UTC)</th><th>Match / event</th><th>Originated markets</th><th>Confidence</th><th>Our selection</th><th>Prediction (High)</th><th>State</th><th>Official source</th></tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table></div>'
        )

    cov = COV_BY_SLUG.get(slug, {})
    n_lines = sum(1 for l in lines_by_id.values() if l["sport"] == slug)
    n_high = sum(1 for l in lines_by_id.values() if l["sport"] == slug and l["confidence"] == "high")
    content = f"""<section class="panel pad">
<div class="card-topline"><strong>{len(rows)} {fix(NAMES[slug])} listings · {n_lines} originated books · {n_high} High desk picks</strong><span class="badge {'amber' if n_high < 5 else 'green'}">{'below 5-pick aim' if n_high < 5 else 'on aim'}</span></div>
<p class="tiny">{fix(cov.get('note',''))}</p>
</section>
{"".join(body_parts)}
<p class="table-note">Blank cells are values the publisher did not state — left empty, never inferred. Originated prices are estimates, not bookmaker quotes.</p>
"""
    html_doc = page_shell(f"{fix(NAMES[slug])} · OLBG Research", active=f"sports/{slug}.html", base="../") + \
        f'<header class="page-heading"><div><p class="eyebrow">CATEGORY · {fix(NAMES[slug]).upper()}</p><h1>{fix(NAMES[slug])}</h1><p>Every captured {fix(NAMES[slug])} fixture in the window, with originated markets, confidence tier and official sources.</p></div><a class="button" href="../index.html">← Back to overview <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M14 7l5 5-5 5"/></svg></a></header>' + content + page_footer("../")
    (SPORTS_DIR / f"{slug}.html").write_text(html_doc, encoding="utf-8")
    print(f"wrote sports/{slug}.html ({len(rows)} rows)")


# ---------------------------------------------------------------- predictions
def build_predictions():
    in_scope_lines = [l for l in lines_by_id.values() if l["sport"] in SLUGS]
    high = sorted(
        [l for l in in_scope_lines if l["confidence"] == "high"],
        key=lambda l: -l["pick_probability"],
    )
    out = []
    for rank, l in enumerate(high, 1):
        p = preds_by_id[l["id"]]
        m = next(x for x in fixtures if x["id"] == l["id"])
        st = fixture_state(m)
        out.append((rank, l, p, m, st))
    rows = []
    for rank, l, p, m, st in out:
        time_html, match_html = match_cell(m)
        rows.append(
            f'<tr id="pred-{l["id"]}">'
            f'<td><span class="number">{rank}</span></td>'
            f'<td>{time_html}</td>'
            f'<td>{match_html}</td>'
            f'<td><span class="number price">{fix(l["pick_american"])}</span><span class="secondary number">{l["pick_odds"]:.2f}</span></td>'
            f'<td><span class="number">{l["highlight"]["implied_pct"]}%</span></td>'
            f'<td>{state_badge_html(l["confidence"])}</td>'
            f'<td><div class="prediction">{fix(p["text"])}</div></td>'
            f'<td><span class="badge {state_badge(st)}">{state_label(st)}</span></td>'
            f'<td>{sources_line(p)}</td>'
            f'</tr>'
        )
    content = f"""<section class="panel pad">
<div class="card-topline"><strong>{len(out)} in-scope High-confidence picks</strong> (30 desk-wide; 4 Aussie Rules picks are outside this brief)</div>
<p class="tiny">Every pick is inside the −250…+10000 window with desk conviction ≥0.60. None independently clears a strict greater-than-70% model-probability bar — disclosed, not suppressed. Predictions are unique, hand-written, ≥30 words, and cite only facts read from the recorded official sources.</p>
</section>
<div class="table-wrap">
<table class="wide-table"><caption class="sr-only">In-scope high-confidence picks ranked by originated probability</caption>
<thead><tr><th>Rank</th><th>Start (UTC)</th><th>Match / event</th><th>Price (fair)</th><th>Implied</th><th>Confidence</th><th>Prediction</th><th>State</th><th>Official source</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>
</div>
<p class="table-note">Bet line for each selection is quoted on its prediction card; the selection named in the prose matches the originated pick.</p>
"""
    html_doc = page_shell("High-confidence picks · OLBG Research", active="predictions.html") + \
        '<header class="page-heading"><div><p class="eyebrow">HIGH-CONFIDENCE PICKS REGISTER</p><h1>High-confidence picks</h1><p>The desk\'s highest-confidence originated selections for the 15 brief sports, ranked by originated probability. All prices inside −250…+10000.</p></div></header>' + content + page_footer()
    (ROOT / "predictions.html").write_text(html_doc, encoding="utf-8")
    print(f"wrote predictions.html ({len(out)} picks)")


# ---------------------------------------------------------------- markets
def build_markets():
    rows = []
    for l in sorted(lines_by_id.values(), key=lambda x: (x["sport"], x["id"])):
        if l["sport"] not in SLUGS:
            continue
        m = next((x for x in fixtures if x["id"] == l["id"]), None)
        if not m:
            continue
        time_html, match_html = match_cell(m)
        for mk in l.get("markets", []):
            for o in mk.get("outcomes", []):
                rows.append(
                    f'<tr id="mk-{l["id"]}-{mk["key"]}-{fix(o.get("selection")).replace(" ", "-")}">'
                    f'<td>{time_html}</td><td>{match_html}</td>'
                    f'<td>{fix(mk.get("name"))}{" " + fix(mk.get("line")) if mk.get("line") else ""}</td>'
                    f'<td>{fix(o.get("selection"))}</td>'
                    f'<td><span class="number price">{fix(o.get("american"))}</span><span class="secondary number">{o.get("odds", 0):.2f}</span></td>'
                    f'<td><span class="number">{o.get("fair_odds", 0):.2f}</span></td>'
                    f'<td><span class="number">{o.get("implied_pct")}%</span></td>'
                    f'<td>{fix((mk.get("role") or "main line"))}</td>'
                    f'<td>{sources_html(m)}</td>'
                    f'</tr>'
                )
    content = f"""<section class="panel pad">
<div class="card-topline"><strong>{sum(len(l.get("markets", [])) for l in lines_by_id.values() if l["sport"] in SLUGS)} originated market lines</strong> across {sum(1 for l in lines_by_id.values() if l["sport"] in SLUGS)} in-scope priced books</div>
<p class="tiny">Markets investigated per match: match winner (money line), handicap/spread ladder, match total ladder — plus unavailable markets explicitly recorded as unverified where the desk found no supported input.</p>
</section>
<div class="table-wrap">
<table class="wide-table"><caption class="sr-only">Every originated market outcome, per in-scope match</caption>
<thead><tr><th>Start (UTC)</th><th>Match / event</th><th>Market</th><th>Selection</th><th>American</th><th>Decimal (fair)</th><th>Implied</th><th>Line role</th><th>Official source</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>
</div>
<p class="table-note">Fair prices are originated estimates: 1/probability, calibrated on governing-body inputs. They are not bookmaker quotes and do not include any bookmaker margin.</p>
"""
    html_doc = page_shell("Market explorer · OLBG Research", active="markets.html") + \
        '<header class="page-heading"><div><p class="eyebrow">MARKET EXPLORER</p><h1>All markets</h1><p>Every originated market outcome for every priced in-scope match: winner, handicap/spread and match total ladders.</p></div></header>' + content + page_footer()
    (ROOT / "markets.html").write_text(html_doc, encoding="utf-8")
    print(f"wrote markets.html ({len(rows)} outcome rows)")


# ---------------------------------------------------------------- flagged
def build_flagged():
    from collections import Counter
    high_by_sport = Counter(l["sport"] for l in lines_by_id.values() if l["confidence"] == "high" and l["sport"] in SLUGS)
    rows = []
    def flag(ref, area, sport, match, finding, disp, src_html):
        rows.append(f'<tr id="{ref}"><td><span class="secondary">{fix(ref)}</span></td><td>{fix(area)}</td><td>{fix(sport)}</td><td>{fix(match)}</td><td>{finding}</td><td>{fix(disp)}</td><td>{src_html}</td></tr>')

    def sport_src(slug):
        cov = COV_BY_SLUG.get(slug, {})
        url = cov.get("olbg_url")
        # olbg.com is not an official source; fall back to first fixture's source
        for m in fixtures:
            if m["sport"] == slug and m.get("sources"):
                s = m["sources"][0]
                if s.get("url", "").startswith("https://"):
                    return sources_html(m)
        return '<span class="secondary">no official link recorded</span>'

    flag('F-01', 'Coverage gap', 'Golf', '4 tournament field cards',
         'Event-only sport in OLBG: multi-runner outright cards (PGA Bermuda, DP World Tour Genesis, LPGA BMW Ladies, Champions Stifel); no two-sided match-winner market exists, so no originated match line or High pick can be built.',
         'Published blank — event cards only; no High pick.',
         sources_html(next(m for m in fixtures if m["sport"] == "golf")))
    flag('F-02', 'Coverage gap', 'Greyhounds', '3 stadium cards',
         'Event-only sport: GBGB cards (Kinsley, Monmore, Nottingham) are race cards, not head-to-head matches; no match-winner market.',
         'Published blank — event cards only.',
         sources_html(next(m for m in fixtures if m["sport"] == "greyhounds")))
    flag('F-03', 'Coverage gap', 'Motor Racing', 'F1 United States Grand Prix',
         '20-car race outright at COTA (25 Oct 20:00 UTC); not a two-sided fixture, so no match-winner line or High pick.',
         'Published blank — event card.',
         sources_html(next(m for m in fixtures if m["sport"] == "motor-racing")))
    flag('F-04', 'Confidence gap', 'Gaelic Sports', '4 county senior finals',
         '4 fixtures captured, 0 High desk picks (all originated lines below conviction floor).',
         'Below the 5-per-sport aim; published as-is, no High pick.',
         sport_src("gaelic-football"))
    flag('F-05', 'Confidence gap', 'Volleyball', '8 fixtures',
         '8 fixtures captured (PlusLiga ×5, SuperLega ×3), 0 High desk picks.',
         'Below the 5-per-sport aim; published as-is.',
         sport_src("volleyball"))
    flag('F-06', 'Confidence gap', 'Rugby Union', '12 fixtures',
         f"{high_by_sport.get('rugby-union', 0)} High desk pick vs 5 sought.",
         'Below aim; no additional verified inputs available to support more High picks.',
         sport_src("rugby-union"))
    flag('F-07', 'Confidence gap', 'Cricket', '8 fixtures',
         f"{high_by_sport.get('cricket', 0)} High desk picks vs 5 sought.",
         'Below aim; published as-is.',
         sport_src("cricket"))
    flag('F-08', 'Confidence gap', 'Snooker', '11 fixtures',
         f"{high_by_sport.get('snooker', 0)} High desk picks vs 5 sought.",
         'Below aim; published as-is.',
         sport_src("snooker"))
    flag('F-09', 'Confidence gap', 'Tennis', '11 fixtures',
         f"{high_by_sport.get('tennis', 0)} High desk picks vs 5 sought.",
         'Below aim; published as-is.',
         sport_src("tennis"))
    flag('F-10', 'Confidence gap', 'Handball', '12 fixtures',
         f"{high_by_sport.get('handball', 0)} High desk picks vs 5 sought.",
         'Below aim; published as-is.',
         sport_src("handball"))
    flag('F-11', 'Confidence gap', 'Baseball', '4 fixtures',
         f"{high_by_sport.get('baseball', 0)} High desk picks vs 5 sought.",
         'Below aim; published as-is.',
         sport_src("baseball"))
    flag('F-12', 'Confidence gap', 'Basketball', '17 fixtures',
         f"{high_by_sport.get('basketball', 0)} High desk picks vs 5 sought.",
         'Below aim; published as-is.',
         sport_src("basketball"))
    flag('F-13', 'Confidence gap', 'Rugby League', '7 fixtures',
         f"{high_by_sport.get('rugby-league', 0)} High desk picks vs 5 sought.",
         'Below aim; published as-is.',
         sport_src("rugby-league"))
    flag('F-14', 'Confidence gap', 'Ice Hockey', '6 fixtures',
         f"{high_by_sport.get('ice-hockey', 0)} High desk picks vs 5 sought.",
         'Below aim; published as-is.',
         sport_src("ice-hockey"))
    flag('F-15', 'Bar disclosure', 'All 15 sports', '126 priced books',
         'Strict user bar (>70% model win probability AND price −250…+10000): 0 books clear it. Best originated price −250 ≈ 71% implied (conviction 68.1%). Desk "High" tier = conviction ≥0.60 inside the window — disclosed as a weaker bar than requested.',
         'Disclosed on every pick page; no pick mis-sold as >70%.',
         sources_html(next(m for m in fixtures if m["sport"] == "ice-hockey")))
    flag('F-16', 'Untimed fixtures', 'Tennis · Snooker · Cricket · Golf', '32 fixtures',
         'Publisher states no start time (tennis 11, snooker 11, cricket 5, golf 4); e-sports 1 also untimed. Rows kept with blank start, never inferred.',
         'Blank start times, flagged.',
         sources_html(next(m for m in fixtures if m["sport"] == "tennis")))
    flag('F-17', 'Out of scope', 'Aussie Rules · eSports', '10 fixtures',
         'Captured but outside this brief: not published as covered categories (4 Aussie Rules High picks and 4 AFLW predictions likewise excluded from the desk displays).',
         'Retained in data; not linked from the 15-sport navigation.',
         sources_html(next(m for m in fixtures if m["sport"] == "aussie-rules")))
    flag('F-18', 'Prose compliance', 'Predictions', '6 entries edited',
         'Prediction entries mlb-849802, snk-higgins-jones, snk-zhang-williams, cric-nz-ind-t20-1, rl-wc26-eng-fra, hand-ehf-12046 contained the prohibited words "model" or "verified"; re-written this session (≥30 words retained, clear "Selection:" label, official sources kept).',
         'Corrected in data/predictions.json and f7fa77fc/data/predictions.json (byte-identical mirror).',
         sources_line(preds_by_id["mlb-849802"]))
    flag('F-257E-20', 'Archived desk flag', 'All sports', 'status gaps',
         'Retained link target from an earlier desk session: pre-match status requires an explicit supported official state; blank or unknown provider states withhold estimates.',
         'Retained as an archived flag; no new data added.',
         sources_line(next(p for p in preds_by_id.values() if p['match_id']=='nhl-2026020152')))
    flag('F-257E-21', 'Archived desk flag', 'All sports', 'statistical expiry',
         'Retained link target from an earlier desk session: estimates expire at the earliest of fixture evidence expiry, the published start, and an input\'s statistical observation limit.',
         'Retained as an archived flag; no new data added.',
         sources_line(next(p for p in preds_by_id.values() if p['match_id']=='nhl-2026020152')))

    body = "".join(rows)
    content = f"""<section class="panel pad" id="coverage">
<div class="card-topline"><strong>{len(rows)} flagged items</strong> — coverage gaps, confidence gaps and disclosure items</div>
<p class="tiny">Nothing here blocks publication. Items marked "gap" are published blank rather than filled in, per the verification rule: if a value cannot be confirmed from an official source, it stays blank.</p>
</section>
<div class="table-wrap">
<table class="wide-table"><caption class="sr-only">Flagged for Review register</caption>
<thead><tr><th>Ref</th><th>Area</th><th>Sport</th><th>Match / scope</th><th>Finding</th><th>Disposition</th><th>Official source</th></tr></thead>
<tbody>{body}</tbody></table>
</div>

<div class="notice neutral"><strong>Elapsed records.</strong> 49 captured fixtures (across all 17 sports) started before 23 Oct 2026 19:30 UTC and are kept as a historical record only; originated prices are stale and not republished as current.</div>
<div class="notice neutral"><strong>Re-verification limit this session.</strong> Sandbox egress is limited to GitHub, npm and PyPI, so official feeds could not be re-fetched independently. Every published row rests on the verification recorded at capture (source links in each row). Treat all fixture facts as historical observations pending a manual re-check against the live official page.</div>
"""
    html_doc = page_shell("Flagged for Review · OLBG Research", active="flagged.html") + \
        '<header class="page-heading"><div><p class="eyebrow">FLAGGED FOR REVIEW REGISTER</p><h1>Flagged for Review</h1><p>Coverage gaps, confidence gaps, blank cells and disclosure items. None of these blocks publication; they are listed so they can be reviewed and closed.</p></div></header>' + content + page_footer()
    (ROOT / "flagged.html").write_text(html_doc, encoding="utf-8")
    print(f"wrote flagged.html ({len(rows)} flags)")


# ---------------------------------------------------------------- analysis
def build_analysis():
    in_scope = [m for m in fixtures if m["sport"] in SLUGS]
    lines = [l for l in lines_by_id.values() if l["sport"] in SLUGS]
    high = [l for l in lines if l["confidence"] == "high"]
    med = [l for l in lines if l["confidence"] == "medium"]
    content_sections = ""
    for slug, name in IN_SCOPE:
        rows_s = [m for m in fixtures if m["sport"] == slug]
        ls = [l for l in lines_by_id.values() if l["sport"] == slug]
        hi_n = sum(1 for l in ls if l["confidence"] == "high")
        content_sections += f"<tr><td>{fix(name)}</td><td><span class='number'>{len(rows_s)}</span></td><td><span class='number'>{len(ls)}</span></td><td><span class='number'>{hi_n}</span></td><td>{sources_html(next(iter(rows_s), {}), 'recorded source') if rows_s else '-'}<span class='secondary'>{COV_BY_SLUG.get(slug, {}).get('status','partial')}</span></td></tr>"
    content = f"""<section class="panel pad">
<div class="card-topline"><strong>Methodology and line-by-line findings</strong></div>
<p class="tiny">Fixture facts are read from governing-body / league / tour sources (links on every row). Prices are independently originated: a logistic rating from official standings/rankings inputs, Gaussian margin projection for handicaps, Poisson-derived totals — calibrated so fair decimal = 1/probability. No bookmaker prices are copied and no missing input is defaulted.</p>
</section>
<section class="panel">
<div class="panel-head"><div><h2>Coverage by sport (15 in the brief)</h2><p>Captured fixtures · originated books · High desk picks · status from the coverage register.</p></div></div>
<div class="table-wrap">
<table class="wide-table"><caption class="sr-only">Coverage register per sport</caption>
<thead><tr><th>Sport</th><th>Fixtures</th><th>Priced books</th><th>High picks</th><th>Coverage note</th></tr></thead>
<tbody>{content_sections}</tbody></table>
</div>
<p class="table-note">Aussie Rules (9 fixtures) and eSports (1 fixture) are captured in the data but are outside this brief and are not listed above.</p>
</section>
<section class="panel">
<div class="panel-head"><div><h2>Findings</h2><p>Irregularities and gaps recorded line by line.</p></div></div>
<ul class="checklist">
<li><span class="ring"></span>No originated price in the window clears a strict greater-than-70% model-probability bar; best implied price ≈71% at −250. Desk High tier uses conviction ≥0.60 inside −250…+10000 and is disclosed as such.</li>
<li><span class="ring"></span>Golf, greyhounds and motor racing are event-only in OLBG — no match-winner market exists; published blank.</li>
<li><span class="ring"></span>Six prediction entries were re-written this session to remove the prohibited words "model" and "verified" (mlb-849802, snk-higgins-jones, snk-zhang-williams, cric-nz-ind-t20-1, rl-wc26-eng-fra, hand-ehf-12046).</li>
<li><span class="ring"></span>32 fixtures (incl. esports) have no published start time — left blank, never inferred.</li>
<li><span class="ring"></span>49 fixtures have elapsed — historical record only.</li>
</ul>
</section>
"""
    html_doc = page_shell("Analysis & findings · OLBG Research", active="analysis.html") + \
        '<header class="page-heading"><div><p class="eyebrow">ANALYSIS &amp; FINDINGS</p><h1>Analysis &amp; findings</h1><p>How the lines are originated, what the confidence tiers mean, and what remains unverified.</p></div></header>' + content + page_footer()
    (ROOT / "analysis.html").write_text(html_doc, encoding="utf-8")
    print("wrote analysis.html")


def main():
    (SPORTS_DIR).mkdir(exist_ok=True)
    build_index()
    for slug, _ in IN_SCOPE:
        build_sport(slug)
    build_predictions()
    build_markets()
    build_flagged()
    build_analysis()
    print("desk build complete")


if __name__ == "__main__":
    main()
