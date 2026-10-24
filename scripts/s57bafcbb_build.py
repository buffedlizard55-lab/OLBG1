#!/usr/bin/env python3
"""Desk 57bafcbb - builder.

Renders the desk's HTML pages into `57bafcbb/` and the JSON mirrors into
`data/57bafcbb/`. The builder only reads from `s57bafcbb_data.py` and
`s57bafcbb_model.py`; it never invents a price, and it never writes outside
the desk's own namespace (plus `data/57bafcbb/`).

Run:  python3 scripts/s57bafcbb_build.py
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import s57bafcbb_data as d
import s57bafcbb_model as m

ROOT = Path(__file__).resolve().parent.parent
DESK_DIR = ROOT / "57bafcbb"
DATA_DIR = ROOT / "data" / "57bafcbb"

CSS = """
:root { --ink:#1c2126; --muted:#5b6770; --line:#d7dbe0; --bg:#f4f6f8;
        --card:#ffffff; --accent:#0b5fff; --ok:#0a7a3e; --warn:#a15c00; }
* { box-sizing: border-box; }
body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       color:var(--ink); background:var(--bg); line-height:1.5; }
header.top { background:#0f1a2b; color:#fff; padding:18px 22px; }
header.top h1 { margin:0; font-size:21px; font-weight:650; letter-spacing:.2px; }
header.top p { margin:6px 0 0; color:#c6d0dc; font-size:13px; }
nav.crumbs { background:#12233c; color:#a9bdd4; padding:8px 22px; font-size:12.5px; }
nav.crumbs a { color:#9fc3ff; text-decoration:none; }
nav.crumbs a:hover { text-decoration:underline; }
main { max-width:1180px; margin:0 auto; padding:20px 22px 60px; }
h1 { font-size:22px; margin:0 0 4px; }
h2 { font-size:16px; margin:26px 0 8px; font-weight:650; }
p.lead { color:var(--muted); font-size:14px; margin:0 0 14px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:16px 18px; margin:0 0 16px; }
table { border-collapse:collapse; width:100%; background:var(--card); font-size:13.5px; }
th, td { border:1px solid var(--line); padding:7px 9px; text-align:left; vertical-align:top; }
th { background:#eef1f5; font-weight:650; white-space:nowrap; }
td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; }
a { color:var(--accent); text-decoration:none; word-break:break-all; }
a:hover { text-decoration:underline; }
.pill { display:inline-block; padding:1px 8px; border-radius:11px; font-size:11.5px; font-weight:650;
        border:1px solid var(--line); background:#f0f2f5; color:#3b4753; white-space:nowrap; }
.pill.high { background:#e5f5ec; color:#0a7a3e; border-color:#b9e3cb; }
.pill.medium { background:#fdf3e3; color:#8a4b00; border-color:#f0dcbc; }
.pill.low { background:#eef1f5; color:#4a5560; }
.pill.flagged { background:#fdeaea; color:#9c1f1f; border-color:#f3c8c8; }
.pill.ok { background:#e5f5ec; color:#0a7a3f; border-color:#b9e3cb; }
.flag { background:#fff6f0; border:1px solid #f0d2bc; }
.note { color:var(--muted); font-size:12.5px; }
pre.quote { background:#fbfcfd; border:1px solid var(--line); border-left:3px solid var(--accent);
            padding:12px 14px; margin:8px 0 0; font-size:13.5px; white-space:pre-wrap; }
ul.tight { margin:6px 0 0; padding-left:20px; }
ul.tight li { margin:3px 0; font-size:13.5px; }
.big { font-size:30px; font-weight:700; }
.kpis { display:flex; gap:12px; flex-wrap:wrap; }
.kpi { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px 16px; min-width:120px; }
.kpi .n { font-size:24px; font-weight:700; }
.kpi .l { font-size:12px; color:var(--muted); }
footer.foot { max-width:1180px; margin:0 auto; padding:0 22px 40px; color:var(--muted); font-size:12.5px; }
"""


def esc(s):
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def tier_pill(tier):
    cls = {"High": "high", "Medium": "medium", "Low": "low"}.get(tier, "low")
    return f'<span class="pill {cls}">{esc(tier)}</span>'


def source_links(ids):
    out = []
    for sid in ids:
        s = d.SOURCE_BY_ID.get(sid)
        if not s:
            continue
        tag = "official" if s.get("official") else "discovery"
        out.append(f'<a href="{esc(s["url"])}">{esc(sid)}</a> <span class="note">[{tag}]</span>')
    return "<br>".join(out) if out else '<span class="note">no link</span>'


def page(title, lead, body, crumbs=None):
    crumb = crumbs or '<a href="../index.html">home</a> / <a href="../picks.html">picks</a>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
<header class="top"><h1>{esc(title)}</h1><p>{esc(lead)}</p></header>
<nav class="crumbs">{crumb}</nav>
<main>
{body}
</main>
<footer class="foot">Desk 57bafcbb - an autonomous line-origination desk working the OLBG.com 15-sport brief.
All prices are the desk's own fair two-way lines, computed from official governing-body records; no bookmaker odds were read.</footer>
</body>
</html>
"""


def kpis(pairs):
    cells = "".join(f'<div class="kpi"><div class="n">{esc(v)}</div><div class="l">{esc(k)}</div></div>' for k, v in pairs)
    return f'<div class="kpis">{cells}</div>'


# The primary official source for each sport, used on the landing page so
# every sport row carries a link a human can open.
OFFICIAL_SOURCE = {
    "golf": "pga-bermuda",
    "volleyball": "legavolley",
    "rugby-union": "urc-r4",
    "cricket": "ecb-series",
    "snooker": "wst-home",
    "darts": "pdpa-ec",
    "baseball": "mlb-schedule",
    "gaelic-sports": "gaa-home",
    "greyhounds": "gbgb",
    "tennis": "atp-scores",
    "motor-racing": "f1-usgp",
    "handball": "eurohandball",
    "ice-hockey": "nhl-score-oct25",
    "basketball": "nba-games",
    "rugby-league": "nrl-rlwc",
}


# ---------------------------------------------------------------------------
def render_index(desk):
    picks = desk["picks"]
    fixtures = desk["fixtures"]
    tiers = {"High": 0, "Medium": 0, "Low": 0}
    for p in picks:
        tiers[p["tier"]] = tiers.get(p["tier"], 0) + 1
    priced_sports = sorted({p["sport"] for p in picks}, key=lambda s: d.SPORT_ORDER[s])
    unpriced = [s for s in d.SPORTS if s["slug"] not in priced_sports]

    rows = []
    for s in d.SPORTS:
        sp = [p for p in picks if p["sport"] == s["slug"]]
        if sp:
            note = f'{len(sp)} pick(s): ' + ", ".join(f'{p["pick"]} ({p["tier"]})' for p in sp)
        else:
            note = 'no priced pick this window - see the flagged page'
        official = d.SOURCE_BY_ID.get(OFFICIAL_SOURCE[s["slug"]])
        official_cell = (
            f'<a href="{esc(official["url"])}">{esc(OFFICIAL_SOURCE[s["slug"]])}</a>'
            if official
            else '<span class="note">see sources page</span>'
        )
        rows.append(
            f'<tr><td><a href="{esc(s["page"])}">{esc(s["name"])}</a></td>'
            f'<td class="num">{len([f for f in fixtures if f["sport"] == s["slug"]])}</td>'
            f'<td>{esc(note)}</td>'
            f'<td>{official_cell}</td></tr>'
        )

    top = [p for p in picks if p["tier"] == "High"]
    top_rows = "".join(
        f'<tr><td>{esc(p["sport"])}</td>'
        f'<td><a href="predictions.html">{esc(p["fixture_id"])}</a></td>'
        f'<td>{esc(p["pick"])}</td>'
        f'<td>{tier_pill(p["tier"])}</td>'
        f'<td class="num">{p["estimate"]:.0%}</td>'
        f'<td class="num">{p["american"]}</td>'
        f'<td>{source_links(p["sources"])}</td></tr>'
        for p in sorted(top, key=lambda x: (-x["estimate"], x["sport_order"]))
    ) or '<tr><td colspan="7">No pick cleared the High band this window.</td></tr>'

    body = f"""
<div class="card">
<h2>Executive summary</h2>
{kpis([
    ("fixtures", len(fixtures)),
    ("priced picks", len(picks)),
    ("High", tiers.get("High", 0)),
    ("Medium", tiers.get("Medium", 0)),
    ("Low", tiers.get("Low", 0)),
    ("sports priced", len(priced_sports)),
    ("sports unpriced", len(unpriced)),
])}
<p class="note" style="margin-top:12px">
Window {esc(d.WINDOW_NOTE)}. This desk originates its own fair two-way lines from the official governing-body
records and form lines recorded in each fixture. It does not read bookmaker odds.
</p>
</div>

<div class="card flag">
<h2 style="margin-top:0">Where the picks are</h2>
<p style="margin:0">The pick table, with the originated line, the confidence label and a link to the full
written prediction, is on the <a href="picks.html">picks page</a>. The full written predictions are on the
<a href="predictions.html">predictions page</a>. Fixtures that could not be priced because their official feed
did not render are on the <a href="flagged.html">flagged for review page</a> and are published there rather than
held back.</p>
</div>

<h2>High-confidence picks</h2>
<table>
<thead><tr><th>Sport</th><th>Fixture</th><th>Pick</th><th>Confidence</th><th class="num">Estimate</th>
<th class="num">Fair price</th><th>Sources</th></tr></thead>
<tbody>{top_rows}</tbody>
</table>

<h2>All 15 sports</h2>
<table>
<thead><tr><th>Sport</th><th class="num">Fixtures</th><th>Picks this window</th><th>Official source</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>

<h2>Pages in this desk</h2>
<ul class="tight">
<li><a href="picks.html">picks.html</a> - the pick table for every priced fixture</li>
<li><a href="predictions.html">predictions.html</a> - the full written predictions</li>
<li><a href="matches.html">matches.html</a> - every fixture, priced and directory</li>
<li><a href="markets.html">markets.html</a> - win, handicap and total lines per fixture</li>
<li><a href="flagged.html">flagged.html</a> - items that need a human, published not suppressed</li>
<li><a href="sources.html">sources.html</a> - every source with its link</li>
<li><a href="methodology.html">methodology.html</a> - how the lines and labels are built</li>
</ul>
"""
    return page(
        "Desk 57bafcbb - OLBG.com tips desk, 24-25 October 2026",
        f"{len(fixtures)} fixtures tracked, {len(picks)} priced picks, {len(priced_sports)} of 15 sports priced. "
        f"Fresh live window opened {d.WINDOW_NOW}.",
        body,
        crumbs='<a href="../index.html">home</a>',
    )


def render_picks(desk):
    picks = sorted(desk["picks"], key=lambda x: (x["sport_order"], -x["estimate"]))
    rows = []
    for p in picks:
        pred_href = "predictions.html"
        rows.append(
            f'<tr><td>{esc(p["sport"])}</td>'
            f'<td><a href="{esc(pred_href)}">{esc(p["fixture_id"])}</a></td>'
            f'<td>{esc(p["home"])} v {esc(p["away"])}</td>'
            f'<td>{esc(p["start_utc"])}</td>'
            f'<td><strong>{esc(p["pick"])}</strong></td>'
            f'<td>{esc(p["bet"])}</td>'
            f'<td>{tier_pill(p["tier"])}</td>'
            f'<td class="num">{p["estimate"]:.1%}</td>'
            f'<td class="num">{p["american"]}</td>'
            f'<td>{source_links(p["sources"])}</td></tr>'
        )
    body = f"""
<div class="card">
<h2 style="margin-top:0">Read this first</h2>
<p class="note" style="margin:0">Every row is a fair two-way line originated by this desk from the official
governing-body record for that fixture. The confidence label is the desk's own: High means the originated
estimate is 60% or better <em>and</em> the fair price sits inside the -250 to +10000 band; Medium means 55% or
better inside the band; Low is everything else, including prices outside the band.</p>
</div>
<table>
<thead><tr><th>Sport</th><th>Fixture</th><th>Fixture</th><th>Start (UTC)</th><th>Pick</th><th>Bet</th>
<th>Confidence</th><th class="num">Estimate</th><th class="num">Fair price</th><th>Sources</th></tr></thead>
<tbody>{''.join(rows) or '<tr><td colspan="10">No priced picks.</td></tr>'}</tbody>
</table>
<h2>Tiers</h2>
<ul class="tight">
<li><strong>High</strong> - estimate at or above 60% and fair price inside -250..+10000.</li>
<li><strong>Medium</strong> - estimate at or above 55% and fair price inside -250..+10000.</li>
<li><strong>Low</strong> - estimate below 55%, or a fair price outside the band.</li>
</ul>
"""
    return page(
        "Desk 57bafcbb - picks",
        "Every priced pick for the 24-25 October 2026 window, with the originated fair price and confidence label.",
        body,
    )


def render_predictions(desk):
    preds = sorted(desk["predictions"], key=lambda x: (x["sport_order"], -x["estimate"]))
    blocks = []
    for p in preds:
        blocks.append(
            f'<div class="card"><h2 style="margin-top:0">{esc(p["sport"])} - {esc(p["fixture_id"])}</h2>'
            f'<p class="note">Pick <strong>{esc(p["pick"])}</strong> - {esc(p["bet"])} - {tier_pill(p["tier"])} - '
            f'estimate {p["estimate"]:.1%}, fair price {p["american"]}. '
            f'{p["words"]} words.</p>'
            f'<pre class="quote">{esc(p["text"])}</pre></div>'
        )
    body = f"""
<div class="card">
<h2 style="margin-top:0">Read this first</h2>
<p class="note" style="margin:0">{len(preds)} written predictions, one per priced pick. Each carries the team or
player, the form line, the recent match history, the statistics and the selection. The selection is repeated at the
end of the prose so it is unmistakable.</p>
</div>
{''.join(blocks) or '<div class="card">No written predictions this window.</div>'}
"""
    return page(
        "Desk 57bafcbb - predictions",
        "The full written predictions for every priced pick in the 24-25 October 2026 window.",
        body,
    )


def render_matches(desk):
    rows = []
    for f in sorted(desk["fixtures"], key=lambda x: (x["sport_order"], x["start"])):
        status = f["status"]
        pill = {"upcoming": "pill ok", "directory-entry": "pill flagged", "completed": "pill low"}[status]
        book = f.get("book")
        priced = "yes" if book else "no"
        pick = f"{esc(book['pick'])} ({esc(book['tier'])})" if book else "-"
        rows.append(
            f'<tr><td>{esc(f["sport"])}</td>'
            f'<td><strong>{esc(f["home"])}</strong> v {esc(f["away"])}</td>'
            f'<td>{esc(f["competition"])}</td>'
            f'<td>{esc(f["start"])}</td>'
            f'<td>{esc(f["venue"])}, {esc(f["city"])}</td>'
            f'<td><span class="{pill}">{esc(status)}</span></td>'
            f'<td>{esc(priced)}</td>'
            f'<td>{pick}</td>'
            f'<td>{esc(f.get("labels", {}).get("note", ""))}</td>'
            f'<td>{source_links([s["id"] for s in f["sources"]])}</td></tr>'
        )
    body = f"""
<table>
<thead><tr><th>Sport</th><th>Fixture</th><th>Competition</th><th>Start (UTC)</th><th>Venue</th>
<th>Status</th><th>Priced</th><th>Pick</th><th>Note</th><th>Sources</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<p class="note">A fixture is <strong>priced</strong> only when the desk could read an official record or form
line for it. A fixture whose official feed did not render is published as a <strong>directory entry</strong>
and is carried on the flagged page; it is never priced from a discovery-only source.</p>
"""
    return page(
        "Desk 57bafcbb - matches",
        "Every fixture in the 24-25 October 2026 window, priced and directory.",
        body,
    )


def render_markets(desk):
    rows = []
    for f in sorted(desk["fixtures"], key=lambda x: (x["sport_order"], x["start"])):
        book = f.get("book")
        if not book:
            continue
        for mk in f["markets"]:
            rows.append(
                f'<tr><td>{esc(f["sport"])}</td>'
                f'<td>{esc(f["id"])}</td>'
                f'<td>{esc(mk["market"])}</td>'
                f'<td>{esc(mk["side"])}</td>'
                f'<td>{tier_pill(mk["tier"])}</td>'
                f'<td class="num">{mk["estimate"]:.1%}</td>'
                f'<td class="num">{mk["american"]}</td>'
                f'<td>{esc(mk["handicap"]) if mk["handicap"] is not None else "-"} {esc(mk["handicap_side"] or "")}</td>'
                f'<td class="num">{mk["handicap_price"] if mk["handicap_price"] is not None else "-"}</td>'
                f'<td class="num">{mk["total_line"] if mk["total_line"] is not None else "-"}</td>'
                f'<td class="num">{mk["over_price"] if mk["over_price"] is not None else "-"}</td>'
                f'<td class="num">{mk["under_price"] if mk["under_price"] is not None else "-"}</td>'
                f'<td>{source_links([s["id"] for s in f["sources"]])}</td></tr>'
            )
    body = f"""
<div class="card">
<h2 style="margin-top:0">Read this first</h2>
<p class="note" style="margin:0">Three families of line per priced fixture: the <strong>win</strong> market, a
<strong>handicap</strong> line, and a <strong>total</strong> line. Handicap and total prices are the desk's own
fair prices for those lines; the totals line is set at the venue scoring average recorded in the desk's
methodology and priced at 55/45.</p>
</div>
<table>
<thead><tr><th>Sport</th><th>Fixture</th><th>Market</th><th>Side</th><th>Confidence</th><th class="num">Estimate</th>
<th class="num">Win price</th><th>Handicap</th><th class="num">Hcp price</th><th class="num">Total line</th>
<th class="num">Over</th><th class="num">Under</th><th>Sources</th></tr></thead>
<tbody>{''.join(rows) or '<tr><td colspan="13">No priced markets.</td></tr>'}</tbody>
</table>
"""
    return page(
        "Desk 57bafcbb - markets",
        "The win, handicap and total lines originated for every priced fixture.",
        body,
    )


def render_sport(slug, desk):
    s = [x for x in d.SPORTS if x["slug"] == slug][0]
    fixtures = [f for f in desk["fixtures"] if f["sport"] == slug]
    picks = [p for p in desk["picks"] if p["sport"] == slug]
    preds = [p for p in desk["predictions"] if p["sport"] == slug]

    fx_rows = ""
    for f in sorted(fixtures, key=lambda x: x["start"]):
        if f.get("book"):
            stat = tier_pill(f["book"]["tier"])
        else:
            stat = '<span class="pill low">unpriced</span>'
        fx_rows += (
            f'<tr><td><strong>{esc(f["home"])}</strong> v {esc(f["away"])}</td>'
            f'<td>{esc(f["competition"])}</td>'
            f'<td>{esc(f["start"])}</td>'
            f'<td>{esc(f["venue"])}, {esc(f["city"])}</td>'
            f'<td>{stat}</td>'
            f'<td>{source_links([x["id"] for x in f["sources"]])}</td></tr>'
        )
    pick_rows = "".join(
        f'<tr><td><strong>{esc(p["pick"])}</strong></td><td>{esc(p["bet"])}</td><td>{tier_pill(p["tier"])}</td>'
        f'<td class="num">{p["estimate"]:.1%}</td><td class="num">{p["american"]}</td>'
        f'<td><a href="../predictions.html">prediction</a></td>'
        f'<td>{source_links(p["sources"])}</td></tr>'
        for p in picks
    ) or (
        '<tr><td colspan="7">No priced pick this window. The desk could not read an official '
        'record or form line for this sport, so no line was originated. See '
        '<a href="../flagged.html">flagged.html</a> and '
        f'<a href="{esc(d.SOURCE_BY_ID[OFFICIAL_SOURCE[slug]]["url"])}">'
        f'{esc(OFFICIAL_SOURCE[slug])}</a>.</td></tr>'
    )

    pred_blocks = "".join(
        f'<div class="card"><h2 style="margin-top:0">{esc(p["fixture_id"])}</h2>'
        f'<p class="note">Pick <strong>{esc(p["pick"])}</strong> - {tier_pill(p["tier"])} - estimate '
        f'{p["estimate"]:.1%}, fair price {p["american"]}.</p>'
        f'<pre class="quote">{esc(p["text"])}</pre></div>'
        for p in preds
    ) or '<div class="card flag">No written prediction for this sport this window; see the flagged page for why.</div>'

    body = f"""
<p class="lead">{len(fixtures)} fixture(s) tracked, {len(picks)} priced pick(s) for this window.</p>
<h2>Fixtures</h2>
<table>
<thead><tr><th>Fixture</th><th>Competition</th><th>Start (UTC)</th><th>Venue</th><th>Confidence</th><th>Sources</th></tr></thead>
<tbody>{fx_rows or '<tr><td colspan="6">No fixtures tracked.</td></tr>'}</tbody>
</table>
<h2>Picks</h2>
<table>
<thead><tr><th>Pick</th><th>Bet</th><th>Confidence</th><th class="num">Estimate</th><th class="num">Fair price</th>
<th>Prediction</th><th>Sources</th></tr></thead>
<tbody>{pick_rows}</tbody>
</table>
<h2>Written predictions</h2>
{pred_blocks}
"""
    return page(
        f"Desk 57bafcbb - {s['name']}",
        f"{s['name']} coverage for the 24-25 October 2026 window.",
        body,
        crumbs='<a href="../index.html">home</a> / <a href="../picks.html">picks</a> / '
               f'<a href="../sports/{slug}.html">{esc(s["name"])}</a>',
    )


def render_flagged(desk):
    rows = []
    for f in d.FLAG_ITEMS:
        cls = "flagged" if f["severity"] == "flagged" else "low"
        links = "<br>".join(f'<a href="{esc(u)}">{esc(u)}</a>' for u in f["source_links"])
        rows.append(
            f'<tr><td>{esc(f["id"])}</td>'
            f'<td>{esc(f["kind"])}</td>'
            f'<td><span class="pill {cls}">{esc(f["severity"])}</span></td>'
            f'<td>{esc(f["status"])}</td>'
            f'<td>{esc(f["where"])}</td>'
            f'<td>{esc(f["detail"])}</td>'
            f'<td>{links}</td></tr>'
        )
    body = f"""
<div class="card flag">
<h2 style="margin-top:0">Nothing here is suppressed</h2>
<p style="margin:0">These items are published rather than held back. A fixture whose official feed did not
render, a sport with no readable official source, and any methodological limitation are all listed here with
the link a human should open. None of them block the desk from publishing.</p>
</div>
<table>
<thead><tr><th>ID</th><th>Kind</th><th>Severity</th><th>Status</th><th>Where</th><th>Detail</th><th>Source links</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
"""
    return page(
        "Desk 57bafcbb - flagged for review",
        "Every item that needs a human, published rather than suppressed.",
        body,
    )


def render_sources(desk):
    rows = []
    for s in d.SOURCES:
        rows.append(
            f'<tr><td>{esc(s["id"])}</td><td>{esc(s["name"])}</td>'
            f'<td><a href="{esc(s["url"])}">{esc(s["url"])}</a></td>'
            f'<td>{"official" if s.get("official") else "discovery / unreadable"}</td>'
            f'<td>{"yes" if s.get("used") else "no"}</td></tr>'
        )
    body = f"""
<div class="card">
<h2 style="margin-top:0">How the desk treats these</h2>
<p class="note" style="margin:0"><strong>official</strong> means the governing body or league that owns the
fixture. <strong>discovery</strong> means the OLBG.com betting-tips hub, which is how the desk finds
fixtures but never how it prices one. <strong>unreadable</strong> means the page is linked for a human because
it is a JavaScript shell or blocked automated reading in this session.</p>
</div>
<table>
<thead><tr><th>ID</th><th>Name</th><th>URL</th><th>Type</th><th>Used by this desk</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
"""
    return page(
        "Desk 57bafcbb - sources",
        "Every source the desk used, with its link and its type.",
        body,
    )


def render_methodology(desk):
    picks = desk["picks"]
    n_high = sum(1 for p in picks if p["tier"] == "High")
    body = f"""
<div class="card">
<h2 style="margin-top:0">Line origination</h2>
<p style="margin:0">For every priced fixture the desk reads the official record and form line for both sides
and writes its own estimate of the probability that the selected side wins. The estimate is then converted
into an American price with p / (1-p), so the price is the desk's own and no bookmaker odds are read anywhere
in this pipeline. The two-way book is completed by giving the other side the remainder, which keeps the book
fair: the sum of the two implied probabilities is exactly 1.</p>
</div>
<div class="card">
<h2 style="margin-top:0">Confidence labels</h2>
<ul class="tight">
<li><strong>High</strong> - the originated estimate is at or above 60% <em>and</em> the fair price sits inside
the -250 to +10000 band. This window produced {n_high} such pick(s).</li>
<li><strong>Medium</strong> - the originated estimate is at or above 55% and the fair price is inside the band.</li>
<li><strong>Low</strong> - estimate below 55%, or a fair price outside the band. A price below -250 is
downgraded to Medium even when the estimate is very high, because the band is the desk's discipline against
backing extreme chalk.</li>
</ul>
</div>
<div class="card">
<h2 style="margin-top:0">Markets</h2>
<p style="margin:0">Three families are investigated per priced fixture. The <strong>win</strong> market carries
the full estimate. The <strong>handicap</strong> line is -1.5 for baseball and ice hockey and -1.0 for tennis,
darts, snooker, cricket and rugby league, priced at a reduced share of the win estimate because a handicap has
to cover more than the outright. The <strong>total</strong> line is set at the venue scoring average for the
sport and priced at 55/45. Where the official source does not give the desk a basis for a market, the cell is
left blank rather than filled in.</p>
</div>
<div class="card">
<h2 style="margin-top:0">Discovery-only fixtures</h2>
<p style="margin:0">A fixture found on the OLBG hub but not backed by an official feed the desk could read is
published as a directory entry. It carries a link to the official page a human should open and appears on the
flagged page. It is never priced, because pricing it would mean inventing a number the desk cannot support.</p>
</div>
<div class="card flag">
<h2 style="margin-top:0">What this desk did not do</h2>
<ul class="tight">
<li>It did not read bookmaker odds. Every price is arithmetic on the desk's own estimate.</li>
<li>It did not fill in a statistic it could not read. Blank cells stay blank.</li>
<li>It did not treat the OLBG hub as an official source. The hub finds fixtures; official pages confirm them.</li>
<li>It did not price the motor-racing or golf outrights as two-way books. They are multi-runner markets and
are published as Low confidence outrights with the field-level estimate stated.</li>
<li>It did not claim a fixture was confirmed when the official feed only rendered a JavaScript shell. Those are
on the flagged page.</li>
</ul>
</div>
"""
    return page(
        "Desk 57bafcbb - methodology",
        "How the lines, the confidence labels and the market families are built.",
        body,
    )


# ---------------------------------------------------------------------------
def write_json(name, obj):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / name).write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n")


def main():
    import s57bafcbb_model as model

    desk = model.build_all()
    DESK_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    tiers = {"High": 0, "Medium": 0, "Low": 0}
    for p in desk["picks"]:
        tiers[p["tier"]] = tiers.get(p["tier"], 0) + 1
    priced_sports = sorted({p["sport"] for p in desk["picks"]}, key=lambda s: d.SPORT_ORDER[s])
    unpriced_sports = [s for s in d.SPORTS if s["slug"] not in priced_sports]

    # ---- HTML ------------------------------------------------------------
    pages = {
        "index.html": render_index(desk),
        "picks.html": render_picks(desk),
        "predictions.html": render_predictions(desk),
        "matches.html": render_matches(desk),
        "markets.html": render_markets(desk),
        "flagged.html": render_flagged(desk),
        "sources.html": render_sources(desk),
        "methodology.html": render_methodology(desk),
    }
    for slug in d.SPORT_ORDER:
        pages[f"sports/{slug}.html"] = render_sport(slug, desk)
    for name, html in pages.items():
        path = DESK_DIR / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)

    # ---- JSON mirrors ----------------------------------------------------
    coverage = []
    for s in d.SPORTS:
        fx = [f for f in desk["fixtures"] if f["sport"] == s["slug"]]
        pk = [p for p in desk["picks"] if p["sport"] == s["slug"]]
        pr = [p for p in desk["predictions"] if p["sport"] == s["slug"]]
        official = [x for x in fx if any(x2.get("official") for x2 in x["sources"])]
        coverage.append({
            "sport": s["name"],
            "slug": s["slug"],
            "page": s["page"],
            "fixtures": len(fx),
            "priced": len(pk),
            "predictions": len(pr),
            "with_official_source": len(official),
            "priced_or_noted": bool(pk),
            "unpriced_reason": (
                "official feed did not render a readable record in this session" if not pk else None
            ),
        })

    manifest = {
        "session_id": d.SESSION_ID,
        "window_start": d.WINDOW_START,
        "window_end": d.WINDOW_END,
        "window_now": d.WINDOW_NOW,
        "window_note": d.WINDOW_NOTE,
        "generated_at": generated,
        "claim_id": "T57BAFCBB",
        "sports": len(d.SPORTS),
        "fixtures": len(desk["fixtures"]),
        "priced_fixtures": len(desk["picks"]),
        "predictions": len(desk["predictions"]),
        "sources": len(d.SOURCES),
        "official_sources": len([s for s in d.SOURCES if s.get("official")]),
        "flags": len(d.FLAG_ITEMS),
        "sports_priced": len(priced_sports),
        "sports_unpriced": len(unpriced_sports),
        "tiers": tiers,
        "band": {"high_floor": -250, "high_ceil": 10000, "high_floor_p": 0.60, "medium_floor_p": 0.55},
        "file_count": len(pages),
        "pages": sorted(pages.keys()),
        "data_dir": "data/57bafcbb",
    }

    write_json("fixtures.json", desk["fixtures"])
    write_json("picks.json", desk["picks"])
    write_json("predictions.json", desk["predictions"])
    write_json("sources.json", d.SOURCES)
    write_json("flags.json", d.FLAG_ITEMS)
    write_json("olbg.json", d.OLBG_LOG)
    write_json("coverage.json", coverage)
    write_json("manifest.json", manifest)
    write_json("lines.json", desk["fixtures"])

    print(f"desk {d.SESSION_ID}: {len(pages)} pages, {len(desk['fixtures'])} fixtures, "
          f"{len(desk['picks'])} picks, {len(desk['predictions'])} predictions, "
          f"{len(d.FLAG_ITEMS)} flags")
    print(f"tiers: {tiers}")
    print(f"priced sports: {len(priced_sports)}/15; unpriced: {[s['slug'] for s in unpriced_sports]}")


if __name__ == "__main__":
    main()
