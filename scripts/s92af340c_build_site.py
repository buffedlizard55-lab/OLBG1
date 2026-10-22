#!/usr/bin/env python3
"""Desk 92af340c — static site builder (session 92af340c-olbg1, 2026-10-22).

Renders 92af340c/** from data/92af340c/{dataset,predictions,flagged,verification}.json
and data/92af340c/harvest/*.json. Self-contained desk: it links to the canonical root
research desk and the archived pre-release desk but never writes outside 92af340c/.
Every table row carries its official-source links; unknown values render blank.
"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "92af340c"
OUT = ROOT / "92af340c"

SPORT_NAMES = {
    "tennis": "Tennis", "basketball": "Basketball", "golf": "Golf", "cricket": "Cricket",
    "snooker": "Snooker", "rugby-union": "Rugby Union", "rugby-league": "Rugby League",
    "baseball": "Baseball", "ice-hockey": "Ice Hockey", "motor-racing": "Motor Racing",
    "darts": "Darts", "handball": "Handball", "volleyball": "Volleyball",
    "aussie-rules": "Aussie Rules", "esports": "eSports", "gaelic-football": "Gaelic Football",
    "greyhounds": "Greyhounds",
}
TIER_LABEL = {"high": "High", "medium": "Medium", "low": "Low", None: "—"}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def esc(value):
    return html.escape("" if value is None else str(value))


def src_links(sources):
    if not sources:
        return ""
    return " ".join(f'<a class="src" href="{esc(s["url"])}" rel="noopener">{esc(s["name"])}</a>'
                    for s in sources)


def companion(prefix=""):
    links = [f'<a href="{prefix}../index.html">Canonical research desk</a>',
             f'<a href="{prefix}../archive/index.html">Archived pre-release desk</a>']
    for desk, label in (("8fc47dcb", "8fc47dcb"), ("v3", "v3"), ("6a081cf6", "6a081cf6"),
                        ("f7fa77fc", "f7fa77fc (mirror)"), ("e6716490", "e6716490"),
                        ("7ad0d336", "7ad0d336")):
        if (ROOT / desk / "index.html").exists():
            links.append(f'<a href="{prefix}../{desk}/index.html">{esc(label)}</a>')
    return '<nav class="companion">Other desks: ' + " · ".join(links) + "</nav>"


def nav(active, prefix=""):
    pages = [("index.html", "Dashboard"), ("picks.html", "All Picks"), ("predictions.html", "High Predictions"),
             ("sports.html", "Sports"), ("verification.html", "Verification"), ("flagged.html", "Flagged"),
             ("methodology.html", "Methodology"), ("sources.html", "Sources"),
             ("reverse-engineering.html", "OLBG Reverse-Engineering")]
    items = " ".join(f'<a class="{"active" if f == active else ""}" href="{prefix}{f}">{esc(t)}</a>' for f, t in pages)
    return f"<nav class=\"desk-nav\">{items}</nav>"


def page(title, active, body, prefix=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Desk 92af340c</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<header class="desk-header">
<h1><a href="{prefix}index.html">Desk 92af340c</a> — live OLBG harvest + strict-band origination</h1>
<p class="desk-sub">Session <code>92af340c-olbg1</code> (T63/T35) · built {esc(BUILT)} · cutoff {esc(CUTOFF)} · research only, 18+</p>
{nav(active, prefix)}
{companion(prefix)}
</header>
<main>
{body}
</main>
<footer class="desk-footer"><p>Desk 92af340c — an isolated namespaced desk inside the OLBG reverse-engineering repo. Fair prices are model outputs, not factual certification; nothing is inferred: unconfirmed values render blank and are flagged. Do not bet money you cannot afford to lose.</p></footer>
<script src="{prefix}assets/app.js" defer></script>
</body>
</html>
"""


DATASET = load("dataset.json")
PREDICTIONS = load("predictions.json")
FLAGGED = load("flagged.json")
VERIFICATION = load("verification.json")
OLBG_INDEX = json.loads((DATA / "olbg.json").read_text(encoding="utf-8"))
HARVEST = {}
for file in sorted((DATA / "harvest").glob("*.json")):
    entry = json.loads(file.read_text(encoding="utf-8"))
    HARVEST[entry["sport"]] = entry
BUILT = DATASET["generated"]
CUTOFF = DATASET["cutoff_utc"]
ROWS = DATASET["rows"]
COUNTS = DATASET["counts"]


def crossref_cell(row):
    xr = row.get("olbg_crossref")
    if not xr:
        return '<td class="muted">no OLBG card (id not stored on row)</td>'
    now = xr.get("harvest_2026_10_22") or {}
    if now.get("listed_now"):
        drift = ' <span class="drift">(consensus drift — see Flagged)</span>' if xr.get("drift_note") else ""
        return (f'<td>card {esc(xr["event_id"])}: <strong>{esc(now.get("selection"))}</strong> '
                f'{esc(now.get("market") or "")} — {esc(now.get("tips"))} tips ({esc(now.get("pct"))}){drift}</td>')
    return f'<td class="muted">card {esc(xr["event_id"])} not rendered in 2026-10-22 read</td>'


def row_tr(row):
    fx, view = row["fixture"], row.get("view")
    tier = TIER_LABEL[row["desk_confidence"]]
    led = row["ledger"]
    if view:
        pick = (f'<strong>{esc(view["pick"])}</strong> {esc(view["pick_market"])}'
                + (f' {esc(view["pick_line"])}' if view["pick_line"] else "")
                + f' · p={view["probability"]:.3f} · book {view["odds"]:.2f} ({esc(view["american"])})')
        fair = ""
        for m in view["markets"]:
            if m["key"] == "winner":
                for o in m["outcomes"]:
                    if o["selection"] == view["pick"]:
                        fair = f' · fair {esc(o["fair_american"])}'
        pick += fair
        winner = f'{esc(view["favourite"])}'
    else:
        pick = '<span class="muted">not priced — left blank, never inferred</span>'
        winner = '<span class="muted">—</span>'
    led_cell = (f'{esc(led["status"] or "—")}'
                + (f' <span class="muted">({esc(led["checked_at"])})</span>' if led.get("checked_at") else ""))
    return (f'<tr data-tier="{esc(row["desk_confidence"] or "")}"><td><code>{esc(fx["id"])}</code></td>'
            f'<td>{esc(fx["home"])} v {esc(fx["away"])}</td>'
            f'<td>{esc(fx["start_utc"] or "")}</td>'
            f'<td class="tier-{esc(row["desk_confidence"] or "none")}">{tier}</td>'
            f'<td>{pick}</td><td>{winner}</td><td>{led_cell}</td>'
            f'{crossref_cell(row)}'
            f'<td class="srcs">{src_links(fx["sources"])}</td></tr>')


def sport_table(sport):
    rows = [r for r in ROWS if r["fixture"]["sport"] == sport and r["time_status"] == "future"]
    if not rows:
        return '<p class="muted">No future priced rows for this sport at the desk cutoff.</p>'
    head = ('<table class="desk-table"><thead><tr><th>Row</th><th>Match</th><th>Start (UTC)</th><th>Tier</th>'
            '<th>Desk pick (book price)</th><th>Winner call</th><th>Ledger</th><th>OLBG hub read 22 Oct</th>'
            '<th>Official sources</th></tr></thead><tbody>')
    return head + "".join(row_tr(r) for r in rows) + "</tbody></table>"


def build():
    OUT.mkdir(exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "sports").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "site_src" / "style.css", OUT / "assets" / "style.css")
    shutil.copyfile(ROOT / "site_src" / "app.js", OUT / "assets" / "app.js")

    # index ------------------------------------------------------------------
    h = DATASET["harvest"]
    grid = "".join(f'<div class="stat"><span class="stat-n">{esc(n)}</span><span class="stat-l">{esc(l)}</span></div>'
                   for n, l in [(COUNTS["future"], "future fixtures"), (COUNTS["priced"], "priced views"),
                                (COUNTS["high"], "High picks"), (COUNTS["medium"], "Medium"),
                                (COUNTS["low"], "Low"), (COUNTS["expired"], "expired"),
                                (COUNTS["undated"], "undated"), (h["event_cards"], "OLBG cards harvested")])
    high_rows = "".join(
        f'<tr><td><code>{esc(p["match_id"])}</code></td><td>{esc(p["match"])}</td><td>{esc(p["sport"])}</td>'
        f'<td>{esc(p["start_utc"])}</td><td><strong>{esc(p["selection"])}</strong></td><td>{esc(p["market"])}</td>'
        f'<td>{esc(p["american"])}</td><td>{p["probability"]:.3f}</td><td>{esc(p["winner_call"])}</td>'
        f'<td>{p["word_count"]} words</td><td class="srcs">{src_links(p["sources"])}</td></tr>'
        for p in PREDICTIONS["items"])
    body = f"""
<section><h2>What this desk is</h2>
<p>A fresh live harvest of all <strong>17 in-scope OLBG sport hubs</strong> read on 2026-10-22
({esc(h["window"])}), published beside strict-band origination lines for every future fixture the repo
verifies from official governing-body sources. Excluded by brief: soccer/football, boxing, UFC/MMA,
American football, hurling, horse racing, cycling and specials. High-tier picks sit strictly inside the
<strong>-250..+10000</strong> window, carry hand-authored predictions of at least 30 words, and pass a
freshness gate the root desk does not apply.</p>
<div class="stat-grid">{grid}</div></section>
<section><h2>High-confidence picks ({esc(len(PREDICTIONS["items"]))})</h2>
<table class="desk-table"><thead><tr><th>Row</th><th>Match</th><th>Sport</th><th>Start (UTC)</th><th>Selection</th>
<th>Market</th><th>Book</th><th>p</th><th>Winner call</th><th>Prediction</th><th>Official sources</th></tr></thead>
<tbody>{high_rows}</tbody></table>
<p><a class="btn" href="predictions.html">Read the full predictions →</a></p></section>
<section><h2>Live hub harvest</h2>
<p>{esc(h["hubs"])} hubs fetched · {esc(h["event_cards"])} event cards captured · zero-tip hubs:
{esc(", ".join(h["zero_tip_hubs"]) or "none")}. Full per-hub evidence on the
<a href="reverse-engineering.html">reverse-engineering page</a> and in
<code>data/92af340c/harvest/</code>.</p></section>"""
    (OUT / "index.html").write_text(page("Dashboard", "index.html", body), encoding="utf-8")

    # picks -------------------------------------------------------------------
    body = ("<h2>All future priced rows by sport</h2>"
            "<p>Tiers: <strong>High</strong> (strict window + measured ratings + fresh ledger + authored prediction) · "
            "<strong>Medium</strong> (window + ratings, gate missing) · <strong>Low</strong>. Expired and undated rows are "
            "counted on the dashboard and excluded here. OLBG consensus is recorded as read, never adopted.</p>")
    for slug in sorted(SPORT_NAMES):
        n = sum(1 for r in ROWS if r["fixture"]["sport"] == slug and r["time_status"] == "future")
        body += f'<section id="{slug}"><h3>{esc(SPORT_NAMES[slug])} ({n} future rows)</h3>{sport_table(slug)}</section>'
    (OUT / "picks.html").write_text(page("All Picks", "picks.html", body), encoding="utf-8")

    # predictions ---------------------------------------------------------------
    cards = ""
    for p in PREDICTIONS["items"]:
        cards += f"""<article class="pred-card">
<h3>{esc(p["match"])} <span class="muted">· {esc(p["competition"])}</span></h3>
<p class="pred-meta"><code>{esc(p["match_id"])}</code> · {esc(p["start_utc"])} · {esc(p["venue"])}</p>
<p class="pred-pick">Selection: <strong>{esc(p["selection"])}</strong> ({esc(p["market"])}{(" " + esc(p["line"])) if p["line"] else ""}) ·
book {p["odds"]:.2f} ({esc(p["american"])}) · model p={p["probability"]:.3f} · winner call: {esc(p["winner_call"])}</p>
<p class="pred-text">{esc(p["text"])}</p>
<p class="srcs">Official sources: {src_links(p["sources"])}</p></article>"""
    body = (f'<h2>High-confidence predictions ({esc(len(PREDICTIONS["items"]))})</h2>'
            f'<p>{esc(PREDICTIONS["rule"])} Window: {esc(PREDICTIONS["high_window"])}.</p>' + cards)
    (OUT / "predictions.html").write_text(page("High Predictions", "predictions.html", body), encoding="utf-8")

    # sports index + per-sport pages --------------------------------------------
    items = ""
    for slug in sorted(SPORT_NAMES):
        srows = [r for r in ROWS if r["fixture"]["sport"] == slug]
        fut = [r for r in srows if r["time_status"] == "future"]
        hi = sum(1 for r in fut if r["desk_confidence"] == "high")
        hub = HARVEST.get(slug, {})
        items += (f'<tr><td><a href="sports/{slug}.html">{esc(SPORT_NAMES[slug])}</a></td>'
                  f'<td>{len(fut)}</td><td>{hi}</td><td>{esc(hub.get("event_cards_captured", 0))}</td>'
                  f'<td>{esc(hub.get("read_utc", ""))}</td><td class="srcs"><a class="src" href="{esc(hub.get("url", "#"))}" rel="noopener">OLBG hub</a></td></tr>')
    body = ('<h2>Sports covered (17 in scope)</h2><table class="desk-table"><thead><tr><th>Sport</th>'
            '<th>Future rows</th><th>High</th><th>Hub cards</th><th>Hub read (UTC)</th><th>Hub link</th>'
            '</tr></thead><tbody>' + items + "</tbody></table>")
    (OUT / "sports.html").write_text(page("Sports", "sports.html", body), encoding="utf-8")

    for slug in sorted(SPORT_NAMES):
        hub = HARVEST.get(slug, {})
        obs = "".join(f"<li>{esc(o)}</li>" for o in hub.get("observations", []))
        cards_html = ""
        if hub.get("events"):
            cards_html = ('<table class="desk-table"><thead><tr><th>event_id</th><th>Match</th><th>Time label (as rendered)</th>'
                          '<th>Most-tipped</th><th>Market</th><th>Tips</th><th>%</th></tr></thead><tbody>'
                          + "".join(f'<tr><td>{esc(c["event_id"])}</td><td>{esc(c["match"])}</td><td>{esc(c["time_label"])}</td>'
                                    f'<td>{esc(c["selection"])}</td><td>{esc(c.get("market") or "—")}</td>'
                                    f'<td>{esc(c.get("tips") or "—")}</td><td>{esc(c.get("pct") or "—")}</td></tr>'
                                    for c in hub["events"]) + "</tbody></table>")
        else:
            cards_html = f'<p class="warn">Hub state at read time: {esc(hub.get("page_state", "unknown"))}</p>'
        body = f"""<h2>{esc(SPORT_NAMES[slug])}</h2>
<section><h3>OLBG hub read — {esc(hub.get("read_utc", ""))}</h3>
<p>Hub: <a href="{esc(hub.get("url", "#"))}" rel="noopener">{esc(hub.get("url", ""))}</a> ·
page state: {esc(hub.get("page_state", ""))} · chunks read: {esc(hub.get("chunks_read"))} of {esc(hub.get("chunks_total"))} ·
cards captured: {esc(hub.get("event_cards_captured", 0))}. {esc(hub.get("pagination_note", ""))}</p>
{cards_html}
<h4>Harvest observations</h4><ul>{obs}</ul></section>
<section><h3>Desk rows (future)</h3>{sport_table(slug)}</section>"""
        (OUT / "sports" / f"{slug}.html").write_text(page(SPORT_NAMES[slug], "sports.html", body, prefix="../"), encoding="utf-8")

    # flagged -------------------------------------------------------------------
    items = ""
    for it in FLAGGED["items"]:
        items += (f'<tr><td><code>{esc(it["id"])}</code></td><td>{esc(it["severity"])}</td><td>{esc(it["scope"])}</td>'
                  f'<td>{esc(it["finding"])}</td><td class="srcs">{src_links(it["sources"])}</td></tr>')
    body = ('<h2>Flagged for review — desk findings</h2>'
            '<p>Every finding below carries its source links. Desk rows never adopt OLBG labels, ids or consensus '
            'as facts; official governing-body pages are the only pricing inputs.</p>'
            '<table class="desk-table"><thead><tr><th>Finding</th><th>Severity</th><th>Scope</th><th>Detail</th>'
            '<th>Sources</th></tr></thead><tbody>' + items + "</tbody></table>")
    (OUT / "flagged.html").write_text(page("Flagged for Review", "flagged.html", body), encoding="utf-8")

    # methodology ---------------------------------------------------------------
    body = f"""<h2>Methodology</h2>
<section><h3>Tier rules (this desk)</h3><p>{esc(DATASET["tier_rules"])}</p></section>
<section><h3>Pricing</h3><p>{esc(DATASET["pricing"])}</p>
<p>Ratings and probabilities come from the repo's published model conventions (<code>scripts/model.py</code>) applied to
official governing-body inputs stored per row in <code>data/fixtures.json</code> — points percentages, ladder positions,
IRL/ICC rankings, EHF group tables and measured splits. The desk does not originate new numeric ratings; it originates
the tier gates, the harvest evidence layer and the predictions.</p></section>
<section><h3>Harvest method</h3><p>{esc(OLBG_INDEX["method"])}</p>
<p>Excluded hubs (never fetched): {esc(OLBG_INDEX["excluded_hubs"])}.</p></section>
<section><h3>Verification policy</h3><p>Every row links the official source(s) it was built from; the live verification
ledger ({esc(VERIFICATION["ledger_summary"])} rows) records per-row re-checks. Where a value cannot be confirmed
officially it is left blank and flagged — never inferred.</p></section>"""
    (OUT / "methodology.html").write_text(page("Methodology", "methodology.html", body), encoding="utf-8")

    # verification ---------------------------------------------------------------
    items = "".join(
        f'<tr><td>{esc(h["sport"])}</td><td class="srcs"><a class="src" href="{esc(h["hub"])}" rel="noopener">{esc(h["hub"])}</a></td>'
        f'<td>{esc(h["read_utc"])}</td><td>{esc(h["cards"])}</td><td>{esc(h["chunks_read"])} / {esc(h["chunks_total"])}</td></tr>'
        for h in VERIFICATION["harvest"])
    led = VERIFICATION["ledger_summary"]
    body = f"""<h2>Verification view</h2>
<section><h3>Hub reads (this desk's harvest)</h3>
<table class="desk-table"><thead><tr><th>Sport</th><th>Hub URL</th><th>Read (UTC)</th><th>Cards</th><th>Chunks</th></tr></thead>
<tbody>{items}</tbody></table></section>
<section><h3>Repo live-verification ledger summary</h3>
<p>{esc(led["rows"])} primary rows — {esc(led["confirmed"])} confirmed, {esc(led["corrected"])} corrected,
{esc(led["flagged"])} flagged, {esc(led["not_rechecked"])} not re-checked. Row-level evidence:
<code>reports/LIVE_VERIFICATION.md</code> and <code>data/verification.json</code>. {esc(VERIFICATION["method"])}</p></section>"""
    (OUT / "verification.html").write_text(page("Verification", "verification.html", body), encoding="utf-8")

    # sources --------------------------------------------------------------------
    seen, items = set(), ""
    for r in ROWS:
        for s in r["fixture"]["sources"]:
            key = s["url"]
            if key in seen:
                continue
            seen.add(key)
            items += f'<tr><td>{esc(s["name"])}</td><td class="srcs"><a class="src" href="{esc(s["url"])}" rel="noopener">{esc(s["url"])}</a></td></tr>'
    hubs = "".join(f'<tr><td>{esc(SPORT_NAMES.get(h["sport"], h["sport"]))} hub</td>'
                   f'<td class="srcs"><a class="src" href="{esc(h["hub"])}" rel="noopener">{esc(h["hub"])}</a></td></tr>'
                   for h in VERIFICATION["harvest"])
    body = ('<h2>Official sources used by desk rows</h2>'
            '<table class="desk-table"><thead><tr><th>Source</th><th>URL</th></tr></thead><tbody>' + items + "</tbody></table>"
            "<h2>OLBG hubs read this session (observation layer, not pricing input)</h2>"
            '<table class="desk-table"><thead><tr><th>Hub</th><th>URL</th></tr></thead><tbody>' + hubs + "</tbody></table>")
    (OUT / "sources.html").write_text(page("Sources", "sources.html", body), encoding="utf-8")

    # reverse-engineering ----------------------------------------------------------
    obs = "".join(f"<li>{esc(o)}</li>" for o in OLBG_INDEX["cross_cutting_observations"])
    per = ""
    for slug in sorted(SPORT_NAMES):
        hub = HARVEST.get(slug, {})
        per += (f'<tr><td>{esc(SPORT_NAMES[slug])}</td><td class="srcs"><a class="src" href="{esc(hub.get("url", "#"))}" rel="noopener">hub</a></td>'
                f'<td>{esc(hub.get("read_utc", ""))}</td><td>{esc(hub.get("event_cards_captured", 0))}</td>'
                f'<td>{esc(hub.get("page_state", ""))}</td></tr>')
    body = f"""<h2>OLBG reverse-engineering — 2026-10-22 hub harvest</h2>
<section><h3>Cross-cutting findings</h3><ul>{obs}</ul></section>
<section><h3>Per-hub read state</h3>
<table class="desk-table"><thead><tr><th>Sport</th><th>Hub</th><th>Read (UTC)</th><th>Cards</th><th>Page state</th></tr></thead>
<tbody>{per}</tbody></table></section>
<section><h3>Structural notes</h3>
<p>Hub URL pattern <code>https://www.olbg.com/betting-tips/{{slug}}/{{id}}</code> re-confirmed live for all 17 in-scope
sports; sport ids unchanged since the committed taxonomy. Cards expose <code>event_id</code> in query strings; ids are
recycled across days and are never used as durable keys by this desk. Time labels never carry a timezone; the desk uses
only governing-body start times. Deeper pagination chunks beyond chunk 0 were not re-read this session — per-hub chunk
coverage is recorded in every harvest file.</p></section>"""
    (OUT / "reverse-engineering.html").write_text(page("OLBG Reverse-Engineering", "reverse-engineering.html", body), encoding="utf-8")

    pages = 10 + len(SPORT_NAMES)
    print(f"desk 92af340c built: {pages} pages + assets (High {COUNTS['high']} / Med {COUNTS['medium']} / Low {COUNTS['low']})")


if __name__ == "__main__":
    build()
