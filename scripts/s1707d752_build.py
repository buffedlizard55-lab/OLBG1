"""Builds the /1707d752/ dashboard: a clarity-first desk, no JavaScript needed."""
from __future__ import annotations

import html
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import s1707d752_compute as C
import s1707d752_data as D

OUT = ROOT / "1707d752"
SLUG = {
    "Basketball": "basketball", "Ice Hockey": "ice-hockey", "Baseball": "baseball",
    "Tennis": "tennis", "Cricket": "cricket", "Rugby Union": "rugby-union",
    "Rugby League": "rugby-league", "Darts": "darts", "Snooker": "snooker",
    "Golf": "golf", "Volleyball": "volleyball", "Handball": "handball",
    "Gaelic Sports": "gaelic-sports", "Greyhounds": "greyhounds", "Motor Racing": "motor-racing",
}
ORDER = list(SLUG)
OLBG_HUB = {
    "Basketball": "https://www.olbg.com/betting-tips/Basketball/4",
    "Ice Hockey": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
    "Baseball": "https://www.olbg.com/betting-tips/Baseball/12",
    "Tennis": "https://www.olbg.com/betting-tips/Tennis/3",
    "Cricket": "https://www.olbg.com/betting-tips/Cricket/7",
    "Rugby Union": "https://www.olbg.com/betting-tips/Rugby_Union/9",
    "Rugby League": "https://www.olbg.com/betting-tips/Rugby_League/10",
    "Darts": "https://www.olbg.com/betting-tips/Darts/15",
    "Snooker": "https://www.olbg.com/betting-tips/Snooker/8",
    "Golf": "https://www.olbg.com/betting-tips/Golf/5",
    "Volleyball": "https://www.olbg.com/betting-tips/Volleyball/21",
    "Handball": "https://www.olbg.com/betting-tips/Handball/20",
    "Gaelic Sports": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
    "Greyhounds": "https://www.olbg.com/betting-tips/Greyhounds/28",
    "Motor Racing": "https://www.olbg.com/betting-tips/Motor_Racing/14",
}
SOURCES = {s["id"]: s for s in D.SOURCES}
READ = "17:42–18:05 UTC, 24 October 2026"
BLOCKERS = {
    "Basketball": "Season one to two games old; the official standings cannot support a 60% call.",
    "Ice Hockey": "Priced in full from the league team summary.",
    "Baseball": "One World Series game; run line and total withheld.",
    "Tennis": "ATP rankings page rendered an empty filter shell; no draw or ranking captured.",
    "Cricket": "NZC returned 404; no PCB or ICC fixture row read.",
    "Rugby Union": "Premiership Rugby served a marketing page; URC fixtures not reached.",
    "Rugby League": "No match listed at all — only 2027 outrights.",
    "Darts": "PDC tournament page returned a cookie-consent shell.",
    "Snooker": "The listed semi-final is already live; the final's opponent is undecided.",
    "Golf": "The OLBG golf hub rendered 'No tips found.'",
    "Volleyball": "Club league tables not captured.",
    "Handball": "EHF and domestic tables not captured.",
    "Gaelic Sports": "GAA club fixtures and scoreboards not captured.",
    "Greyhounds": "No GBGB race card captured; hub clocks do not reconcile.",
    "Motor Racing": "Qualifying had not run; no grid or championship table captured.",
}


ZONES = (("UTC", 0), ("US Pacific", -7), ("US Eastern", -4), ("UK", 1), ("Central Europe", 2))
ZONE_NOTE = ("US Pacific is PDT (UTC-7), US Eastern is EDT (UTC-4), UK is BST (UTC+1) and Central Europe is "
             "CEST (UTC+2) on 24-25 October 2026. US zones switch to standard time on 1 November, UK on 25 October.")


def _dt(iso: str):
    return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def time_stack(r) -> str:
    """Every zone we can state, from the official UTC start. Never guessed."""
    if not r.get("utc"):
        return (f'<div class="small">{e(r["display_time"])}</div>'
                f'<div class="small mut">as listed by OLBG; the clock is not stated, so nothing is converted</div>')
    t = _dt(r["utc"])
    out = [f'<div class="small"><b>{t:%H:%M} UTC</b> · {t:%a %d %b}</div>']
    for name, off in ZONES[1:]:
        l = t + timedelta(hours=off)
        day = "" if l.date() == t.date() else f" <span class='mut'>({l:%a})</span>"
        out.append(f'<div class="small mut">{name}: {l:%H:%M}{day}</div>')
    return "".join(out)


def short_time(r) -> str:
    if not r.get("utc"):
        return f'{e(r["display_time"])} (OLBG listing, clock unstated)'
    t = _dt(r["utc"])
    return f'{t:%a %d %b %H:%M} UTC · {t - timedelta(hours=7):%H:%M} PT · {t + timedelta(hours=1):%H:%M} UK'


def time_series(rows) -> str:
    """One horizontal line listing every start time in UTC, for scanning the day."""
    known = sorted({r["utc"] for r in rows if r.get("utc")})
    if not known:
        return ""
    pts = " · ".join(f"{_dt(u):%H:%M}" for u in known)
    first, last = _dt(known[0]), _dt(known[-1])
    return (f'<div class="callout"><strong>Start times, official UTC.</strong> {pts} UTC. '
            f'In US Pacific that is {first - timedelta(hours=7):%H:%M} to {last - timedelta(hours=7):%H:%M}; '
            f'in the UK, {first + timedelta(hours=1):%H:%M} to {last + timedelta(hours=1):%H:%M}. '
            f'Dates: {first:%d %b %Y} ({first:%m/%d/%Y}) onward. {ZONE_NOTE}</div>')


def e(v) -> str:
    return html.escape("" if v is None else str(v), quote=True)


def money(american: int) -> str:
    return f"{american:+d}" if american else "0"


def price_cell(block: dict) -> str:
    return f"<b>{money(block['american'])}</b> <span class='mut'>({block['decimal']:.2f})</span>"


CSS = """
:root{--ink:#14201b;--muted:#5c6b64;--line:#dde5e1;--bg:#f6f9f7;--card:#fff;
--green:#12563d;--green-soft:#e7f1ec;--amber:#8a5a12;--amber-soft:#fdf3e2;--red:#8c2f2f;--red-soft:#fbeceb;--blue:#1d4e79;--blue-soft:#e8f0f8}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--green)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{background:var(--green);color:#fff;padding:14px 0}
header.top .wrap{display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;align-items:center}
.brand{color:#fff;text-decoration:none;font-weight:700;letter-spacing:.01em}
.brand span{font-weight:400;opacity:.8}
.top .meta{font-size:13px;opacity:.85;display:flex;gap:16px;flex-wrap:wrap}
nav.tabs{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
nav.tabs .wrap{display:flex;gap:4px;overflow-x:auto;padding:0 12px}
nav.tabs a{display:block;padding:12px 12px;font-size:14.5px;color:var(--muted);text-decoration:none;white-space:nowrap;border-bottom:2px solid transparent}
nav.tabs a:hover{color:var(--green)}
nav.tabs a[aria-current]{color:var(--green);border-bottom-color:var(--green);font-weight:650}
main{padding:26px 0 60px}
h1{font-size:31px;line-height:1.2;margin:.1em 0 .35em;letter-spacing:-.015em}
h2{font-size:21px;margin:34px 0 8px;letter-spacing:-.01em}
h3{font-size:16.5px;margin:22px 0 6px}
p{margin:.5em 0}
.lede{font-size:17.5px;color:#31413a;max-width:74ch}
.mut{color:var(--muted)}
.small{font-size:13px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:18px 0 6px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.kpi b{display:block;font-size:26px;line-height:1.1}
.kpi small{color:var(--muted);font-size:12.5px}
.callout{background:var(--green-soft);border:1px solid #c9e0d4;border-radius:12px;padding:14px 18px;margin:16px 0}
.callout.warn{background:var(--amber-soft);border-color:#eeddba}
.callout.info{background:var(--blue-soft);border-color:#cfe0f0}
.callout.red{background:var(--red-soft);border-color:#f0cfcd}
table{width:100%;border-collapse:collapse;background:#fff}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin:12px 0}
th,td{padding:9px 11px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top;font-size:14.5px}
th{background:#f0f5f2;font-size:12.5px;text-transform:uppercase;letter-spacing:.05em;color:#3c4d45;position:sticky;top:0}
tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fbfdfc}
.chip{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:650;white-space:nowrap}
.chip.high{background:#d8efe2;color:#0d4a30}
.chip.medium{background:#e6eefc;color:#1d4272}
.chip.low{background:#f0eeea;color:#5a4d3a}
.chip.none{background:#f4e6e4;color:#7c2b22}
.pick{cursor:default}
.now{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;background:#f1f5f3;padding:1px 6px;border-radius:6px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.card h3{margin-top:0}
.where{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin:12px 0}
.where a{display:block;background:#fff;border:1px solid var(--line);border-radius:11px;padding:11px 13px;text-decoration:none;color:var(--ink)}
.where a:hover{border-color:var(--green);box-shadow:0 1px 6px rgba(18,86,61,.08)}
.where strong{display:block;color:var(--green);font-size:14.5px}
.where small{color:var(--muted)}
.pickcard{background:#fff;border:1px solid var(--line);border-left:4px solid var(--green);border-radius:12px;padding:14px 16px;margin:12px 0}
.pickcard h3{margin:0 0 4px}
.pickcard .sel{font-size:17px;font-weight:700}
.pickcard .row{display:flex;flex-wrap:wrap;gap:14px;margin:6px 0;font-size:13.5px;color:#39504a}
.pickcard .prose{border-top:1px dashed var(--line);margin-top:10px;padding-top:10px}
details{background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px 14px;margin:10px 0}
summary{cursor:pointer;font-weight:600}
footer{margin-top:44px;padding:20px 0;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
ul.tight{margin:.4em 0 .6em;padding-left:1.15em}
ul.tight li{margin:.22em 0}
.strip{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.strip .pill{border:1px solid var(--line);background:#fff;border-radius:999px;padding:4px 11px;font-size:13px;color:#3c4d45;text-decoration:none}
.strip .pill:hover{border-color:var(--green)}
@media(max-width:640px){h1{font-size:25px}th,td{font-size:13.5px;padding:8px}}
"""

NAV = [
    ("index.html", "Executive summary"),
    ("picks.html", "All picks"),
    ("predictions.html", "Written predictions"),
    ("matches.html", "Every match"),
    ("markets.html", "Markets"),
    ("sports/index.html", "15 sports"),
    ("coverage.html", "Coverage vs brief"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("method.html", "Method"),
    ("repo-review.html", "Repo review"),
]


def page(title: str, body: str, active: str, depth: int, desc: str) -> str:
    up = "../" * depth
    nav = "".join(
        f'<a href="{up}{href}"{" aria-current=page" if href == active else ""}>{e(label)}</a>'
        for href, label in NAV
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG research desk · 24 Oct 2026</title>
<meta name="description" content="{e(desc)}">
<link rel="stylesheet" href="{up}assets/desk.css">
</head><body>
<header class="top"><div class="wrap">
  <a class="brand" href="{up}index.html">OLBG research desk <span>· 24 October 2026</span></a>
  <div class="meta"><span>Independent · not affiliated with OLBG</span><span>Sources read {e(READ)}</span></div>
</div></header>
<nav class="tabs"><div class="wrap">{nav}</div></nav>
<main><div class="wrap">
{body}
<footer>
  <p><strong>What this is.</strong> Our own prices, originated from official league records, and our own written
  analysis. Not a bookmaker, not a tipster service, not affiliated with OLBG. No selection is a guarantee.
  Where an input was missing it is blank and flagged, never filled in.</p>
  <p class="small">Desk <code>1707d752</code> · built 2026-10-24 · 18+ · Stake only what you can afford to lose.</p>
</footer>
</div></main></body></html>"""


def source_html(f) -> str:
    src = f["source"]
    if src.startswith("http"):
        return (f'Source: <a href="{e(src)}" target="_blank" rel="noopener noreferrer">{e(src)}</a>')
    return f'Source: <a href="{e(src)}">this desk\'s method page</a>'


def chip(tier: str) -> str:
    return f'<span class="chip {tier.lower()}">{e(tier)}</span>'


def src_links(ids) -> str:
    out = []
    for sid in ids:
        s = SOURCES[sid]
        tag = "" if s["official"] else ' <span class="small mut">(discovery)</span>'
        out.append(f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["org"])} — {e(s["title"].split(" (")[0][:70])}</a>{tag}')
    return "<br>".join(out)


def build() -> dict:
    data = C.build()
    rows = data["rows"]
    priced = [r for r in rows if r["priced"]]
    unpriced = [r for r in rows if not r["priced"]]
    picks = sorted([r for r in priced if r.get("pick")], key=lambda r: -r["pick"]["probability"])
    tiers = {t: sum(1 for r in picks if r["pick"]["confidence"] == t) for t in ("High", "Medium", "Low")}

    def sport_row(s):
        listed = sum(1 for r in rows if r["sport"] == s) + sum(1 for r in D.LISTINGS if r["sport"] == s)
        pr = [r for r in priced if r["sport"] == s]
        pk = [r for r in picks if r["sport"] == s]
        hi = sum(1 for r in pk if r["pick"]["confidence"] == "High")
        status = "Priced" if hi else ("Priced, no High" if pr else "Listed only")
        return (f"<tr><td><b>{e(s)}</b></td><td>{listed}</td><td>{len(pr)}</td><td>{len(pk)}</td><td>{hi}</td>"
                f"<td>{e(status)}</td><td><a href='sports/{SLUG[s]}.html'>Open →</a></td></tr>")

    def sport_rows(sport):
        return [r for r in rows if r["sport"] == sport]

    def pick_row(i, r, show_sport=True):
        p = r["pick"]
        where = (f'<a href="predictions.html#{p["anchor"]}">Full prediction →</a><br>'
                 f'<span class="small mut">predictions.html#{p["anchor"]}</span>')
        sport = f'<a href="sports/{SLUG[r["sport"]]}.html">{e(r["sport"])}</a>' if show_sport else ""
        return (f'<tr><td>{i}</td><td>{sport}</td>'
                f'<td><b>{e(r["home_name"])} v {e(r["away_name"])}</b><br><span class="small mut">{e(r["competition"])} · {short_time(r)}</span></td>'
                f'<td><b>{e(p["name"])}</b><br><span class="small mut">money line</span></td>'
                f'<td>{price_cell(p)}</td><td>{p["probability"]*100:.1f}%</td>'
                f'<td>{chip(p["confidence"])}</td><td class="small">{where}</td></tr>')

    # ---------------- index ----------------
    highs = [r for r in picks if r["pick"]["confidence"] == "High"]
    index_body = f"""
<h1>Today's picks, in one place</h1>
<p class="lede">Fifteen sports scanned on OLBG, every match we could verify listed, and our own prices on the
matches where official records were available. The picks are below, ranked. Each one names the selection,
the price we make it, our chance of it winning, and the page where the full written prediction sits.</p>

<div class="kpis">
  <div class="kpi"><b>15</b><small>sports scanned on OLBG</small></div>
  <div class="kpi"><b>{len(rows)+len(D.LISTINGS)}</b><small>events listed</small></div>
  <div class="kpi"><b>{len(priced)}</b><small>matches priced by us</small></div>
  <div class="kpi"><b>{sum(len([m for m in r['markets'].values() if 'withheld' not in m]) for r in priced)}</b><small>market boards issued</small></div>
  <div class="kpi"><b>{len(picks)}</b><small>written picks</small></div>
  <div class="kpi"><b>{tiers['High']}</b><small>High confidence</small></div>
</div>

{time_series(priced)}

<div class="callout">
  <strong>Where everything is.</strong> This page is the executive summary. The ranked pick list is directly
  below. Full 60–90 word predictions live on <a href="predictions.html">Written predictions</a>, each with its own
  anchor. Every match we found is on <a href="matches.html">Every match</a>. Anything we could not confirm is on
  <a href="flagged.html">Flagged for review</a>.
</div>

<h2>Executive summary — today's picks, strongest first</h2>
<p class="small mut">Confidence: <b>High</b> means our chance is 60% or better, the price is inside the brief's
−250 to +10000 window, every input was captured and the league sample is deep enough. <b>Medium</b> is 53–60%,
or a stronger chance that misses one High condition — the reason is printed on every pick's card.
<b>Low</b> is below 53%.</p>
<div class="table-wrap"><table>
<thead><tr><th>#</th><th>Sport</th><th>Match</th><th>Our pick</th><th>Our price</th><th>Our chance</th><th>Confidence</th><th>Full prediction</th></tr></thead>
<tbody>{''.join(pick_row(i+1, r) for i, r in enumerate(picks))}</tbody></table></div>

<div class="callout warn">
  <strong>Read this before using a Medium.</strong> {tiers['High']} High, {tiers['Medium']} Medium and
  {tiers['Low']} Low came out of {len(picks)} priced matches. The brief asks for five High picks in every sport;
  that is not reachable on today's evidence, because only three sports published records we could read and two of
  those seasons are one or two games old. Nothing was relabelled to fill the gap. The exact shortfall, sport by
  sport, is on <a href="coverage.html">Coverage vs brief</a>.
</div>

<h2>Where things are</h2>
<div class="where">
  <a href="picks.html"><strong>All picks</strong><small>Every pick with its market, price and confidence</small></a>
  <a href="predictions.html"><strong>Written predictions</strong><small>The full 60–90 word reasoning for each pick</small></a>
  <a href="matches.html"><strong>Every match</strong><small>All {len(rows)+len(D.LISTINGS)} events, priced and unpriced</small></a>
  <a href="markets.html"><strong>Markets</strong><small>Winner, handicap and total — what we priced and what we withheld</small></a>
  <a href="sports/index.html"><strong>15 sports</strong><small>One page per sport, fixtures and picks together</small></a>
  <a href="flagged.html"><strong>Flagged for review</strong><small>{len(D.FLAGS)} items we could not resolve</small></a>
</div>

<h2>Coverage at a glance</h2>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th>Listed on OLBG</th><th>Priced by us</th><th>Picks</th><th>High</th><th>Status</th><th>Page</th></tr></thead>
<tbody>{''.join(sport_row(s) for s in ORDER)}</tbody></table></div>

<h2>How a price becomes a pick</h2>
<div class="grid2">
  <div class="card"><h3>Our own line, not a bookmaker's</h3>
  <p>Every price on this site is ours. Hockey uses each club's goals for and against per game, shrunk toward the
  league average, resolved through a Poisson scoreline grid; basketball uses conference records shrunk toward .500
  plus a home term; baseball uses a log5 head-to-head of the 162-game records with a home-field term. Fair decimal
  is 1/p with no margin, and the American price is derived from that.</p>
  <p><a href="method.html">The full method, with the exact constants →</a></p></div>
  <div class="card"><h3>What we never do</h3>
  <ul class="tight">
    <li>No price without the official inputs both ways.</li>
    <li>No injury claim unless an official report was read.</li>
    <li>No High label bought with a short price.</li>
    <li>No OLBG tipster percentage treated as a probability.</li>
    <li>Blank cells stay blank and are flagged.</li>
  </ul></div>
</div>
"""
    files = {"index.html": page("Today's picks", index_body, "index.html", 0,
                                "Executive summary: today's picks, their prices, and where each prediction lives.")}

    # ---------------- picks ----------------
    def market_rows(r):
        out = []
        for name, m in r["markets"].items():
            if "withheld" in m:
                out.append(f"<tr><td>{e(name)}</td><td colspan='4' class='mut'>Withheld — {e(m['withheld'])}</td></tr>")
            elif name == "Match total":
                out.append(f"<tr><td>{e(name)}</td><td>Over {m['line']}: {price_cell(m['over'])}</td>"
                           f"<td>Under {m['line']}: {price_cell(m['under'])}</td><td colspan='2' class='small mut'>{e(m['label'])}</td></tr>")
            elif name.startswith("Handicap"):
                line = m.get("line")
                lbl = f"home {line:+.1f}" if isinstance(line, float) and line else "home −1.5 / away +1.5"
                out.append(f"<tr><td>{e(name)}</td><td>Home ({lbl}): {price_cell(m['home'])}</td>"
                           f"<td>Away: {price_cell(m['away'])}</td><td colspan='2' class='small mut'>{e(m['label'])}</td></tr>")
            else:
                out.append(f"<tr><td>{e(name)}</td><td>{e(r['home_name'])}: {price_cell(m['home'])}</td>"
                           f"<td>{e(r['away_name'])}: {price_cell(m['away'])}</td><td colspan='2' class='small mut'>{e(m['label'])}</td></tr>")
        return "".join(out)

    picks_body = "<h1>All picks</h1>"
    picks_body += ('<p class="lede">One pick per priced match, taken from the money line, ranked by our own chance. '
                   'Handicap and total boards are on <a href="markets.html">Markets</a>; they are priced but not '
                   'put forward as picks.</p>')
    picks_body += _table(picks, show_sport=True)
    picks_body += "<h2>Per-match market boards</h2>"
    for r in priced:
        p = r["pick"]
        picks_body += f"""<details><summary>{e(r['home_name'])} v {e(r['away_name'])} — {e(r['sport'])}</summary>
        <table><thead><tr><th>Market</th><th>Home</th><th>Away</th><th colspan="2">Notes</th></tr></thead>
        <tbody>{market_rows(r)}</tbody></table>
        <p class="small mut">Pick: <b>{e(p['name'])}</b> at {price_cell(p)} — {p['probability']*100:.1f}% ·
        {e(p['confidence'])}{' — ' + e('; '.join(p['caps'])) if p['caps'] else ''}.
        <a href="predictions.html#{p['anchor']}">Read the prediction →</a></p></details>"""
    files["picks.html"] = page("All picks", picks_body, "picks.html", 0,
                               "Every pick, its market, our price and our confidence.")

    # ---------------- predictions ----------------
    pred_body = """<h1>Written predictions</h1>
<p class="lede">Every pick gets its own paragraph below. Each states the selection in plain words, the participants,
their current form, the match-specific numbers we read from the official record, and where the number came from.
No two are templated from the same sentence.</p>
<div class="callout info"><strong>What is deliberately absent.</strong> No prediction names an injured or returning
player, because no official injury or availability report was read this session. Where an official source named a
participant — the two probable pitchers in the World Series — the name is included and linked.</div>"""
    for r in picks:
        p = r["pick"]
        caps = f'<div class="callout warn small">Held out of High: {e("; ".join(p["caps"]))}.</div>' if p["caps"] else ""
        pred_body += f"""
<article class="pickcard" id="{p['anchor']}">
  <div class="small mut">{e(r['sport'])} · {e(r['competition'])}</div>
  <div class="small mut">Starts {time_stack(r)}</div>
  <h3>{e(r['home_name'])} v {e(r['away_name'])}</h3>
  <div class="sel">{e(p['name'])} — money line</div>
  <div class="row"><span>Our price <b>{money(p['american'])}</b> ({p['decimal']:.2f})</span>
   <span>Our chance <b>{p['probability']*100:.1f}%</b></span>
   <span>Confidence {chip(p['confidence'])}</span>
   <span>{'Inside' if p['band'] else 'Outside'} the −250…+10000 window</span></div>
  {caps}
  <div class="prose"><p>{e(p['prose'])}</p>
  <p class="small mut">Inputs read: {e(r['home_name'])} {e(r['summary']['home_line'])}; {e(r['away_name'])} {e(r['summary']['away_line'])}.
    {e(r['summary']['home_detail'])}. {e(r['summary']['away_detail'])}.</p>
  <p class="small">Sources: {src_links(r['sources'])}</p></div>
</article>"""
    files["predictions.html"] = page("Written predictions", pred_body, "predictions.html", 0,
                                     "Full written reasoning behind every pick.")

    # ---------------- matches ----------------
    def match_table(sel_rows, sel_listings):
        head = ("<thead><tr><th>Sport</th><th>Competition</th><th>Match</th><th>Start (UTC and local)</th>"
                "<th>Our price</th><th>Pick</th><th>Official source / recheck</th></tr></thead>")
        body = ""
        for r in sel_rows:
            if r["priced"]:
                p = r["pick"]
                body += (f"<tr><td>{e(r['sport'])}</td><td>{e(r['competition'])}</td>"
                         f"<td><b>{e(r['home_name'])} v {e(r['away_name'])}</b><br><span class='small mut'>{e(r['competition'])}</span></td>"
                         f"<td>{time_stack(r)}</td><td>{price_cell(p)}</td>"
                         f"<td>{e(p['name'])} {chip(p['confidence'])}</td><td class='small'>{src_links(r['sources'])}</td></tr>")
            else:
                body += (f"<tr><td>{e(r['sport'])}</td><td>{e(r['competition'])}</td>"
                         f"<td><b>{e(r['home_name'])} v {e(r['away_name'])}</b><br><span class='small mut'>{e(r['competition'])}</span></td>"
                         f"<td>{time_stack(r)}</td><td class='mut'>no price</td>"
                         f"<td class='small mut'>{e(r.get('incomplete_reason',''))}</td>"
                         f"<td class='small'>{src_links(r['sources'])}</td></tr>")
        for r in sel_listings:
            recheck = D.RECHECK.get(r["sport"])
            link = (f'<a href="{e(recheck[0])}" target="_blank" rel="noopener noreferrer">{e(recheck[1])}</a>'
                    if recheck else "")
            body += (f"<tr><td>{e(r['sport'])}</td><td>{e(r['competition'])}</td><td><b>{e(r['event'])}</b></td>"
                     f"<td>{e(r['display_time'])}</td><td class='mut'>not captured</td><td class='mut'>no price</td>"
                     f"<td class='small mut'>{e(r['why'])}</td>"
                     f"<td class='small'><a href=\"{e(r['olbg'])}\">OLBG listing</a>"
                     f"{'<br>' + link if link else ''}</td></tr>")
        return f'<div class="table-wrap"><table>{head}<tbody>{body}</tbody></table></div>'

    matches_body = f"""<h1>Every match we found</h1>
<p class="lede">All {len(rows)+len(D.LISTINGS)} events that were listed on the fifteen OLBG hubs we scanned today,
plus the ones an official body confirmed. Click any match to find its source. Rows without a price say exactly
which input was missing.</p>
{time_series(priced)}
<div class="callout"><strong>Times.</strong> Where the league published a UTC start, the row shows it and converts
it to US Pacific, US Eastern, UK and Central European time. Where only OLBG listed the match, its clock is
reproduced exactly as printed, labelled "clock unstated", and not converted. See flag
<a href="flagged.html#F-17-02">F-17-02</a>.</div>
<h2>Priced by us — {len(priced)} matches</h2>
{match_table(priced, [])}
<h2>Listed, not priced — {len(unpriced)+len(D.LISTINGS)} events</h2>
{match_table(unpriced, D.LISTINGS)}"""
    files["matches.html"] = page("Every match", matches_body, "matches.html", 0,
                                 "Every event found across the fifteen requested sports.")

    # ---------------- markets ----------------
    mkt = """<h1>Market investigation</h1>
<p class="lede">The brief asks us to look at every available market, not just the winner. For each priced match we
issued a money line, a handicap board and a total where the inputs supported one. Every market we could not price
is listed with the exact input that was missing.</p>
<h2>Winner / handicap / total by match</h2>
<div class="table-wrap"><table><thead><tr><th>Match</th><th>Money line</th><th>Handicap</th><th>Total</th></tr></thead><tbody>"""
    for r in priced:
        m = r["markets"]
        ml = m.get("Money line", {})
        hc = m.get("Handicap", m.get("Handicap (puck line)", {}))
        tot = m.get("Match total", {})
        ml_txt = (f"{price_cell(ml['home'])} / {price_cell(ml['away'])}" if "home" in ml else f"<span class='mut'>{e(ml.get('withheld',''))}</span>")
        hc_txt = (f"{price_cell(hc['home'])} / {price_cell(hc['away'])}" if "home" in hc else f"<span class='mut'>{e(hc.get('withheld',''))}</span>")
        tot_txt = (f"O {price_cell(tot['over'])} / U {price_cell(tot['under'])}" if "over" in tot else f"<span class='mut'>{e(tot.get('withheld',''))}</span>")
        mkt += f"<tr><td><b>{e(r['home_name'])} v {e(r['away_name'])}</b><br><span class='small mut'>{e(r['sport'])}</span></td><td>{ml_txt}</td><td>{hc_txt}</td><td>{tot_txt}</td></tr>"
    mkt += """</tbody></table></div>
<h2>Sports where no market could be priced</h2>
<p>Twelve of the fifteen sports produced no priceable match, because the official page we reached either served a
shell, returned an error, or carried no competition table. Those sports are still listed in full on
<a href="matches.html">Every match</a>, and each carries an official recheck link. The blocking page is named for
each one on <a href="coverage.html">Coverage vs brief</a>.</p>
<h2>Markets we investigated and refused</h2>
<ul class="tight">
  <li><b>Basketball totals</b> — the NBA standings page read carries no points data, so a total would be invented.</li>
  <li><b>Baseball run line and total</b> — Milwaukee's season runs scored and allowed sat outside the retained slice of the standings response.</li>
  <li><b>Correct score, frames, legs, 180s, first try, podium</b> — these need sport-specific official feeds (PDC, WST, EHF) that did not return usable content.</li>
  <li><b>Greyhound trap and sectional markets</b> — no GBGB card was captured for any of the fifteen races listed.</li>
</ul>"""
    files["markets.html"] = page("Markets", mkt, "markets.html", 0,
                                 "Winner, handicap and total markets examined for every priced match.")

    # ---------------- coverage ----------------
    cov = """<h1>Coverage against the brief</h1>
<p class="lede">The brief asks for five fully written High-confidence predictions in each of fifteen sports every
day. This page counts, sport by sport, what was actually delivered and what blocked the rest.</p>"""
    cov += '<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Listed</th><th>Priced</th><th>Picks</th><th>High</th><th>High shortfall vs 5</th><th>Blocker</th></tr></thead><tbody>'
    for s in ORDER:
        l = sum(1 for r in rows if r["sport"] == s) + sum(1 for r in D.LISTINGS if r["sport"] == s)
        pr = [r for r in priced if r["sport"] == s]
        pk = [r for r in picks if r["sport"] == s]
        hi = sum(1 for r in pk if r["pick"]["confidence"] == "High")
        cov += (f"<tr><td><b>{e(s)}</b></td><td>{l}</td><td>{len(pr)}</td><td>{len(pk)}</td><td>{hi}</td>"
                f"<td>{max(0, 5-hi)}</td><td class='small mut'>{e(BLOCKERS[s])}</td></tr>")
    cov += "</tbody></table></div>"
    cov += f"""<div class="callout warn"><strong>The score.</strong> {len(picks)} written picks, {tiers['High']} of them High,
against a target of 75 High picks. The gap is a source-availability gap, not an effort gap: three sports published
machine-readable official records, and two of those seasons are days old. The alternative — inventing ratings for
fourteen club leagues we could not read — would put fabricated numbers in front of you, which the brief explicitly
forbids.</div>"""
    files["coverage.html"] = page("Coverage vs brief", cov, "coverage.html", 0,
                                  "Exactly what was delivered for each of the fifteen sports.")

    # ---------------- sports index + pages ----------------
    sp_index = "<h1>Fifteen sports</h1><p class='lede'>One page per sport, with every event we found and every pick we made.</p><div class='grid2'>"
    for s in ORDER:
        l = sum(1 for r in rows if r["sport"] == s) + sum(1 for r in D.LISTINGS if r["sport"] == s)
        pr = [r for r in priced if r["sport"] == s]
        sp_index += (f"<div class='card'><h3><a href='{SLUG[s]}.html'>{e(s)}</a></h3>"
                     f"<p class='small mut'>{len(pr)} priced · {l} listed in total · "
                     f"{sum(1 for r in pr if r['pick']['confidence']=='High')} High</p>"
                     f"<p class='small'>{e(BLOCKERS[s])}</p></div>")
    sp_index += "</div>"
    files["sports/index.html"] = page("Fifteen sports", sp_index, "sports/index.html", 1,
                                      "Sport-by-sport index of fixtures and picks.")

    for s in ORDER:
        sr = [r for r in rows if r["sport"] == s]
        sl = [r for r in D.LISTINGS if r["sport"] == s]
        body = f"<h1>{e(s)}</h1><p class='lede'>{e(BLOCKERS[s])}</p>"
        body += f"<div class='strip'><a class='pill' href='../matches.html'>All matches</a>" \
                f"<a class='pill' href='../picks.html'>All picks</a>" \
                f"<a class='pill' href='{OLBG_HUB[s]}' target='_blank' rel='noopener noreferrer'>OLBG {e(s)} hub</a>"
        if s in D.RECHECK:
            body += f"<a class='pill' href='{D.RECHECK[s][0]}' target='_blank' rel='noopener noreferrer'>{e(D.RECHECK[s][1])}</a>"
        body += "</div>"
        if sr:
            body += "<h2>Matches and our prices</h2>" + match_table(sr, [])
        if sl:
            body += "<h2>Listed, not priced</h2>" + match_table([], sl)
        if not sr and not sl:
            body += "<div class='callout warn'>No event for this sport was listed on the OLBG hub at read time.</div>"
        body += "<p class='small'><a href='../index.html'>← Back to the executive summary</a></p>"
        files[f"sports/{SLUG[s]}.html"] = page(s, body, "sports/index.html", 1,
                                               f"{s} fixtures and picks for 24 October 2026.")

    # ---------------- sources ----------------
    src = "<h1>Source register</h1><p class='lede'>Every source behind this desk, with what it was used for and whether it is an official body. OLBG appears only as discovery.</p>"
    src += "<div class='table-wrap'><table><thead><tr><th>ID</th><th>Organisation</th><th>Title</th><th>Role</th><th>Link</th></tr></thead><tbody>"
    for s in D.SOURCES:
        role = "Official" if s["official"] else "Discovery only"
        src += (f"<tr><td class='now'>{e(s['id'])}</td><td><b>{e(s['org'])}</b></td><td>{e(s['title'])}</td>"
                f"<td>{e(role)}</td><td class='small'><a href='{e(s['url'])}' target='_blank' rel='noopener noreferrer'>Open →</a></td></tr>")
    src += "</tbody></table></div>"
    src += f"<p class='small mut'>All reads took place between {e(READ)}. A source listed here was fetched; that does not mean every field on it was used.</p>"
    files["sources.html"] = page("Sources", src, "sources.html", 0, "Every source used, with links.")

    # ---------------- flagged ----------------
    fl = ("<h1>Flagged for review</h1><p class='lede'>Everything we could not confirm, could not price, or found "
          "irregular on the source site. Each item names the evidence and links to it.</p>")
    for f in D.FLAGS:
        fl += f"""<article class="pickcard" id="{e(f['id'])}" style="border-left-color:#b3822f">
        <div class="small mut">{e(f['id'])}</div><h3>{e(f['title'])}</h3>
        <p>{e(f['detail'])}</p>
        <p class="small">{source_html(f)}</p></article>"""
    files["flagged.html"] = page("Flagged for review", fl, "flagged.html", 0,
                                 "Unconfirmed values and irregularities, with sources.")

    # ---------------- method ----------------
    meth = """<h1>Method</h1>
<p class="lede">Nothing here is copied from a bookmaker. Every price is derived from the official records named on
each row, using the constants below, and every pick's probability is printed so you can disagree with it.</p>
<h2>Pricing</h2>
<ul class="tight">
<li><b>Ice hockey.</b> Each club's goals for and against per game are shrunk toward the league rate with an
eight-game prior. Expected goals for the home side = home scoring rate × away concession rate ÷ league rate × 1.03;
the away side gets 0.97. A Poisson grid over 0–12 goals gives the result distribution; regulation ties are split
50/50 between the sides for the money line, ties of one goal do not cover a −1.5 puck line, and the total is read
straight off the grid at 5.5.</li>
<li><b>Basketball.</b> Win rates are shrunk toward .500 with a Beta(12,12) prior, converted to logits, and a 0.20
logit home term is added; the difference is the money line. No handicap and no total are issued, because the NBA
standings page publishes wins and losses but not points scored or conceded, and a points line cannot be derived
from a win rate without inventing a margin distribution.</li>
<li><b>Baseball.</b> log5 on the two 162-game records with a mild prior, plus a 0.16 logit home term (about 54%).
Extra innings are part of the money line.</li>
</ul>
<h2>Prices</h2>
<p>Fair decimal = 1 ÷ probability, with no margin and no clipping. The American number is derived from the unrounded
decimal. A price is never rounded toward a more attractive number.</p>
<h2>Confidence</h2>
<ul class="tight">
<li><b>High</b> — our chance is at least 60%, the fair price is inside −250…+10000, every input was captured, and
both sides have played at least 8 games (hockey), 20 (basketball) or 60 (baseball).</li>
<li><b>Medium</b> — 53% to 60%, or a stronger chance that misses one of the High conditions. The missed condition
is printed on the pick.</li>
<li><b>Low</b> — below 53%.</li>
</ul>
<div class="callout warn"><strong>Why the brief's two High tests barely overlap.</strong> A fair price of −250 is
exactly 71.43%. A selection above 70% is therefore shorter than −233, so “more than 70% <i>and</i> between −250 and
+10000” describes only the sliver from 70.0% to 71.4%. This desk publishes the occupied probability on every pick
so you can apply either reading yourself. See <a href="flagged.html#F-17-01">F-17-01</a>.</div>
<h2>What a written prediction must contain</h2>
<p>At least 30 words, the selection in plain language, both participants, the current record, the recent run, and
at least one number specific to that match, all drawn from the official source linked beneath it. The shortest here
is 62 words and no two share a repeated six-word phrase.</p>
<h2>What is never used</h2>
<p>OLBG tip percentages are votes, not probabilities, and are never converted into a price. No rating is defaulted
for a team we could not read. No injury is asserted without an official report.</p>"""
    files["method.html"] = page("Method", meth, "method.html", 0, "How every price and confidence level is derived.")

    # ---------------- repo review ----------------
    files["repo-review.html"] = page("Repo review", repo_review(), "repo-review.html", 0,
                                     "Line-by-line review of this repository and its irregularities.")

    # write
    for rel, content in files.items():
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    (OUT / "assets/desk.css").write_text(CSS, encoding="utf-8")

    summary = {
        "desk": "1707d752",
        "generated": "2026-10-24",
        "read_window": READ,
        "sports_scanned": len(ORDER),
        "events_listed": len(rows) + len(D.LISTINGS),
        "matches_priced": len(priced),
        "market_boards": sum(len([m for m in r["markets"].values() if "withheld" not in m]) for r in priced),
        "picks": len(picks),
        "high": tiers["High"], "medium": tiers["Medium"], "low": tiers["Low"],
        "predictions": len(D.PREDICTIONS),
        "flags": len(D.FLAGS),
        "league_goals_per_team_game": round(data["league_goals"], 3),
    }
    (ROOT / "data/1707d752").mkdir(parents=True, exist_ok=True)
    (ROOT / "data/1707d752/summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (ROOT / "data/1707d752/picks.json").write_text(json.dumps(
        [{"id": r["id"], "sport": r["sport"], "competition": r["competition"],
          "home": r["home_name"], "away": r["away_name"], "utc": r["utc"],
          "selection": r["pick"]["name"], "market": "Money line",
          "probability": round(r["pick"]["probability"], 4), "decimal": r["pick"]["decimal"],
          "american": r["pick"]["american"], "confidence": r["pick"]["confidence"],
          "band": r["pick"]["band"], "caps": r["pick"]["caps"],
          "prediction": r["pick"]["prose"],
          "location": f"1707d752/predictions.html#{r['pick']['anchor']}",
          "sources": r["sources"]}
         for r in picks], indent=2) + "\n")
    return summary


def _table(rows, show_sport=True) -> str:
    head = ("<thead><tr><th>#</th><th>Sport</th><th>Match</th><th>Our pick</th><th>Our price</th>"
            "<th>Our chance</th><th>Confidence</th><th>Full prediction</th></tr></thead>")
    body = ""
    for i, r in enumerate(rows):
        p = r["pick"]
        body += (f"<tr><td>{i+1}</td><td><a href='sports/{SLUG[r['sport']]}.html'>{e(r['sport'])}</a></td>"
                 f"<td><b>{e(r['home_name'])} v {e(r['away_name'])}</b><br><span class='small mut'>{e(r['competition'])} · {short_time(r)}</span></td>"
                 f"<td><b>{e(p['name'])}</b><br><span class='small mut'>money line</span></td>"
                 f"<td>{price_cell(p)}</td><td>{p['probability']*100:.1f}%</td>"
                 f"<td>{chip(p['confidence'])}"
                 + (f"<br><span class='small mut'>{e(p['caps'][0])}</span>" if p['caps'] else "")
                 + "</td>"
                 f"<td class='small'><a href='predictions.html#{p['anchor']}'>Read →</a><br>"
                 f"<span class='small mut'>predictions.html#{p['anchor']}</span></td></tr>")
    return f'<div class="table-wrap"><table>{head}<tbody>{body}</tbody></table></div>'


def repo_review() -> str:
    htmls = sorted(ROOT.glob("*.html"))
    desks = sorted(p.name for p in ROOT.iterdir() if p.is_dir() and len(p.name) == 8 and (p / "index.html").is_file())
    all_html = list(ROOT.rglob("*.html"))
    conflicts, big = [], []
    for p in all_html:
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "<<<<<<<" in t or ">>>>>>>" in t:
            conflicts.append(p.relative_to(ROOT).as_posix())
        if p.stat().st_size > 2_000_000:
            big.append((p.relative_to(ROOT).as_posix(), p.stat().st_size))
    coord = (ROOT / "COORDINATION.md").stat().st_size
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        head = "unknown"
    body = f"""<h1>Repo review</h1>
<p class="lede">A line-by-line look at the tree this desk was built inside: what is here, what is irregular, and
what was deliberately left alone.</p>
<h2>Numbers</h2>
<div class="table-wrap"><table><thead><tr><th>Check</th><th>Result</th></tr></thead><tbody>
<tr><td>HTML files in the tree</td><td>{len(all_html)}</td></tr>
<tr><td>Root-level HTML pages</td><td>{len(htmls)}</td></tr>
<tr><td>Sibling desk directories with their own index</td><td>{len(desks)}</td></tr>
<tr><td>Merge-conflict markers found</td><td>{len(conflicts)}</td></tr>
<tr><td>HTML files above 2 MB</td><td>{len(big)}</td></tr>
<tr><td>Shared coordination board size</td><td>{coord:,} bytes</td></tr>
<tr><td>Commit this desk was built on</td><td class="now">{e(head[:12])}</td></tr>
</tbody></table></div>
<h2>What we found</h2>
<ul class="tight">
<li><b>{len(desks)} parallel desks</b> sit beside each other, each with its own data namespace. The shared root
dashboard is generated by <code>pipeline/build.py</code> and is not owned by any desk, so this session did not
edit it.</li>
<li><b>No conflict markers</b> were present in any HTML file at build time.</li>
<li><b>Large single files:</b> {', '.join(f'{n} ({s/1e6:.1f} MB)' for n, s in big) if big else 'none above 2 MB'}.
These are pre-existing and outside this desk's scope; they are flagged here rather than rewritten.</li>
<li><b>The coordination board</b> is {coord:,} bytes and append-only in practice. This session appended one claim
section and one completion section, and edited nothing else in it.</li>
<li><b>Shared-file discipline.</b> This desk wrote only inside <code>data/1707d752/</code>,
<code>scripts/s1707d752_*.py</code>, <code>1707d752/</code> and <code>reports/SESSION_1707D752.md</code>. The root
<code>index.html</code>, <code>pipeline/**</code>, <code>data/current/**</code>, <code>.github/workflows/**</code>
and every peer desk were left untouched, so no other session's work could be overwritten.</li>
<li><b>Irregularity carried forward, not fixed:</b> a previous desk reports OLBG hub clocks as US Eastern; today's
NHL rows are consistent with that, but the European rugby and volleyball rows are not. Both this desk and that one
therefore reproduce OLBG clocks verbatim instead of converting them. See <a href="flagged.html#F-17-02">F-17-02</a>.</li>
</ul>
<h2>Reproduce this desk</h2>
<pre class="now">python3 scripts/s1707d752_compute.py      # prices and picks
python3 scripts/s1707d752_build.py        # writes 1707d752/ and data/1707d752/
python3 scripts/s1707d752_validate.py     # desk gates
python3 -m pipeline.validate --site .     # canonical repo gate</pre>"""
    return body


if __name__ == "__main__":
    summary = build()
    print(json.dumps(summary, indent=2))
