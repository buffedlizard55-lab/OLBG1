#!/usr/bin/env python3
"""Desk 99d43605 static-site builder.

Renders the 15-sport research desk into ``99d43605/`` and exports the
machine-readable mirrors into ``data/99d43605/``.

Aesthetic mirrors the project's house style (flat palette, no gradients).
Every table row carries at least one official https source link; unpriced
rows are shown with explicit states instead of invented numbers.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import s99d43605_data as D          # noqa: E402

OUT = ROOT / "99d43605"
DATA = ROOT / "data" / "99d43605"
GENERATED = "2026-10-24T21:00:00Z"
STAMP_HUMAN = "Saturday 24 October 2026, 21:00 UTC"
REPO = "https://github.com/buffedlizard55-lab/OLBG1"

SOURCE_BY_ID = {s["id"]: s for s in D.SOURCES}
_NAME2SLUG = {name: slug for slug, name, *_ in D.SPORTS}
OLBG_LOG = {_NAME2SLUG.get(e["sport"], e["sport"]): e for e in D.OLBG_LOG}
SPORT_NAME = {slug: name for slug, name, *_ in D.SPORTS}
SPORT_ORDER = [slug for slug, *_ in D.SPORTS]

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def esc(x) -> str:
    return html.escape(str(x), quote=True)


def price(x) -> str:
    return esc(f"{x:+d}") if isinstance(x, int) else "&mdash;"


def pct(p) -> str:
    return f"{p*100:.1f}%" if isinstance(p, (int, float)) else "&mdash;"


def dec3(x) -> str:
    return f"{x:.3f}" if isinstance(x, (int, float)) else "&mdash;"


def kickoff(iso) -> str:
    if not iso:
        return "&mdash;"
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%d %b %Y %H:%M UTC")


def src_links(ids, small=True) -> str:
    """Anchor stack of official source links; every table row embeds one."""
    out = []
    for sid in ids:
        s = SOURCE_BY_ID[sid]
        out.append(
            f'<a class="src" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{esc(s["label"])}<span class="arrow">&#8599;</span></a>'
        )
    return '<div class="src-stack%ss">%s</div>' % ((" smal" if small else ""), "".join(out))


def tier_badge(t) -> str:
    cls = {"High": "high", "Medium": "medium", "Low": "low"}.get(t or "", "low")
    return f'<span class="badge {cls}">{esc(t) if t else "&mdash;"}</span>'


STATE_BADGE = {
    "upcoming": ('<span class="badge slate">Upcoming</span>'),
    "excluded-live": ('<span class="badge red">In play at read</span>'),
    "excluded-unverified": ('<span class="badge red">Unconfirmed</span>'),
    "awaiting-finalists": ('<span class="badge amber">Awaiting finalists</span>'),
    "directory-entry": ('<span class="badge slate">Directory entry</span>'),
}


def state_badge(s) -> str:
    return STATE_BADGE.get(s, esc(s))


# ---------------------------------------------------------------------------
# house CSS (flat colours; absolutely no gradients)
# ---------------------------------------------------------------------------

FLAG_REFS = {
    "F-99-01": ["nhl-standings"], "F-99-02": ["nhl-standings"], "F-99-03": ["pdc-wall"],
    "F-99-04": ["wta-shell"], "F-99-05": ["gbgb-racing"], "F-99-06": ["legavolley"],
    "F-99-07": ["premrugby", "usa-rugby"], "F-99-08": ["urc-r4"], "F-99-09": ["nba-injury"],
    "F-99-10": ["nrl-rlwc"], "F-99-11": ["gaa-galway"], "F-99-12": ["pga-bermuda", "f1-usgp"],
}
CSS = """
:root{--bg:#f5f6f8;--card:#ffffff;--ink:#14213d;--muted:#5c667a;--line:#e5e8ef;
--brand:#0b6b4f;--brand-ink:#054a37;--brand-soft:#e6f4ee;--amber:#92400e;--amber-soft:#fdf3e3;
--red:#b42318;--red-soft:#fdeceb;--navy:#1d3557;--navy-soft:#e9eef7;--radius:12px;
--shadow:0 1px 2px rgba(16,24,40,.05),0 1px 3px rgba(16,24,40,.08)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--brand-ink);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1200px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:30;background:rgba(255,255,255,.97);
border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;gap:16px;min-height:60px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;font-weight:760;color:var(--ink)}
.brand .dot{width:10px;height:10px;border-radius:50%;background:var(--brand);display:inline-block}
.brand small{display:block;font-weight:500;color:var(--muted);font-size:11px;letter-spacing:.1em;text-transform:uppercase}
nav.main{margin-left:auto;display:flex;gap:2px;flex-wrap:wrap}
nav.main a{padding:7px 10px;border-radius:8px;color:#39435a;font-size:13.5px;font-weight:600}
nav.main a:hover{background:#f0f2f7;text-decoration:none}
nav.main a[aria-current="page"]{background:var(--brand-soft);color:var(--brand-ink)}
.hero{padding:36px 0 6px}
.eyebrow{margin:0 0 8px;color:var(--brand-ink);font-size:12px;font-weight:700;letter-spacing:.13em;text-transform:uppercase}
h1{margin:0;font-size:clamp(28px,4vw,42px);line-height:1.12;letter-spacing:-.02em}
.lede{color:var(--muted);max-width:78ch;margin:12px 0 0;font-size:17px}
.stamp{margin-top:10px;color:var(--muted);font-size:13px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:24px 0 4px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
padding:14px 16px;box-shadow:var(--shadow)}
.kpi b{display:block;font-size:27px;letter-spacing:-.02em;line-height:1.1}
.kpi span{color:var(--muted);font-size:12px;font-weight:650;text-transform:uppercase;letter-spacing:.06em}
section{margin:34px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
box-shadow:var(--shadow);overflow:hidden;margin:16px 0}
.pad{padding:18px 20px}
.head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-bottom:10px;flex-wrap:wrap}
h2{margin:0;font-size:22px;letter-spacing:-.015em}
h3{margin:0 0 6px;font-size:16px}
.head p{margin:4px 0 0;color:var(--muted);font-size:14px;max-width:86ch}
.table-wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:14px}
caption{text-align:left;padding:12px 16px 0;color:var(--muted);font-size:13px}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
thead th{background:#f7f8fb;color:#4a5568;font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fafbfc}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.pick{font-weight:720}
.match{font-weight:640}
.sub{display:block;color:var(--muted);font-size:12.5px}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:720;
letter-spacing:.02em;border:1px solid transparent;white-space:nowrap}
.badge.high{background:var(--brand-soft);color:var(--brand-ink);border-color:#9fd6bd}
.badge.medium{background:var(--amber-soft);color:var(--amber);border-color:#f0cd95}
.badge.low{background:#eef0f4;color:#4a5568;border-color:#dfe3ea}
.badge.slate{background:var(--navy-soft);color:var(--navy);border-color:#c3cfe0}
.badge.red{background:var(--red-soft);color:var(--red);border-color:#f2b8b4}
.badge.amber{background:var(--amber-soft);color:var(--amber);border-color:#f0cd95}
.badge.outline{background:#fff;border-color:#cbd5e1;color:#39435a}
.src-stack{display:flex;flex-direction:column;gap:4px;min-width:190px}
a.src{display:inline-flex;align-items:center;gap:4px;font-size:12.5px;font-weight:600;color:var(--brand-ink)}
a.src .arrow{font-size:11px;color:var(--muted)}
.grid{display:grid;gap:14px}
.grid.cols-3{grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}
.grid.cols-2{grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}
.tile{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
box-shadow:var(--shadow);padding:16px 18px}
.tile h3 a{color:var(--ink)}
.mini{font-size:13px;color:var(--muted)}
.note{background:#fffbea;border:1px solid #f1e1a5;border-radius:var(--radius);padding:14px 18px;margin:16px 0;font-size:14.5px}
.note.ok{background:var(--brand-soft);border-color:#9fd6bd}
.note.bad{background:var(--red-soft);border-color:#f2b8b4}
.markets{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
box-shadow:var(--shadow);margin:16px 0}
.markets header{padding:14px 18px;border-bottom:1px solid var(--line);display:flex;gap:10px;flex-wrap:wrap;align-items:center}
table.lines td.idx{width:34%;font-weight:620}
.kind{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
footer.foot{margin-top:48px;border-top:1px solid var(--line);background:#fff}
.foot .wrap{padding:26px 20px 40px;color:var(--muted);font-size:13px;display:grid;gap:8px}
.pred{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--brand);
border-radius:var(--radius);box-shadow:var(--shadow);padding:20px 22px;margin:18px 0}
.pred .who{font-size:18px;font-weight:760;margin-bottom:6px}
.pred .body{font-size:16px;line-height:1.65}
.pred .meta{margin-top:12px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
ul.ticks{margin:0;padding-left:18px}
ul.ticks li{margin:6px 0}
.callout{border:1px solid var(--line);border-radius:var(--radius);background:#fbfcfe;padding:14px 18px;margin:14px 0;font-size:14.5px}
"""

NAV = [
    ("index.html", "Executive summary"),
    ("picks.html", "Picks"),
    ("predictions.html", "Predictions"),
    ("markets.html", "Markets"),
    ("matches.html", "Matches"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("methodology.html", "Methodology"),
    ("olbg.html", "OLBG research"),
    ("sports.html", "All 15 sports"),
]


def page(title: str, description: str, current: str, body: str, depth: int = 0) -> str:
    pre = "../" * depth
    parts = []
    for href, label in NAV:
        mark = ' aria-current="page"' if href == current else ""
        parts.append(f'<a href="{pre}{href}"{mark}>{esc(label)}</a>')
    nav = "".join(parts)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG research desk 99d43605</title>
<meta name="description" content="{esc(description)}"><meta name="color-scheme" content="light">
<style>{CSS}</style></head><body>
<header class="top"><div class="wrap">
<span class="brand"><span class="dot"></span><span>OLBG research desk<small>session 99d43605 · {esc(GENERATED[:10])}</small></span></span>
<nav class="main" aria-label="Desk">{nav}</nav></div></header>
<main class="wrap">{body}</main>
<footer class="foot"><div class="wrap">
<div><strong>Independently originated research.</strong> This desk is not affiliated with OLBG. Prices are our own fair lines (no overround included), published as estimates for review alongside their official sources.</div>
<div>Generated {esc(STAMP_HUMAN)} from the official reads listed on the sources page. Nothing here is a betting recommendation.</div>
<div><a href="{pre}methodology.html">How pricing works</a> · <a href="{pre}flagged.html">Flagged for review</a> · <a href="{REPO}">Repository</a></div>
</div></footer></body></html>"""


# ---------------------------------------------------------------------------
# computed pieces
# ---------------------------------------------------------------------------

def built():
    return D.build_all()


def row_fixture(fx, with_sport=True, with_markets_note=False, id_suffix=""):
    st = state_badge(fx["state"])
    pick = f'<span class="pick">{esc(fx["pick"])}</span>' if fx.get("pick") else '<span class="mini">No pick published</span>'
    tcel = tier_badge(fx.get("tier")) if fx.get("tier") else '<span class="mini">&mdash;</span>'
    sport = f'{esc(SPORT_NAME.get(fx["sport"], fx["sport"]))}<span class="sub">{esc(fx.get("competition",""))}</span>'
    note = (fx.get("tier_note") or "").strip()
    note = f'<span class="sub">{esc(note)}</span>' if note else ""
    mw = ""
    if with_markets_note:
        mw_o = fx.get("markets_withheld") or []
        mw = ("<span class=sub>Withheld: " + "; ".join(esc(m["key"]) for m in mw_o) + "</span>") if mw_o else ""
    return f'''<tr id="{esc(fx["id"])}{id_suffix}">
<td class="match">{esc(fx["a"] or fx["competition"])}<br><span class="mini">v</span> {esc(fx["b"] or "(pairing open)")}
<span class="sub">{esc(fx.get("round") or "")}</span></td>
<td>{sport}</td>
<td><span class="mini">{esc(kickoff(fx["start_utc"]))}</span>{st}</td>
<td>{pick}{note}</td>
<td>{tcel}</td>
<td class="num">{price(fx.get("american"))}</td>
<td class="num">{dec3(fx.get("decimal"))}</td>
<td class="num">{pct(fx.get("pick_prob"))}</td>
<td>{src_links(fx["source_ids"])}{mw}</td></tr>'''


def row_high(fx):
    return f'''<tr id="{esc(fx["id"])}"><td class="match">{esc(fx["a"])} <span class="mini">@</span> {esc(fx["b"])}
<span class="sub">{esc(fx["competition"])} &middot; {esc(kickoff(fx["start_utc"]))}</span></td>
<td>{esc(SPORT_NAME.get(fx["sport"], fx["sport"]))}</td>
<td><span class="pick">{esc(fx["pick"])}</span></td>
<td class="num">{price(fx["american"])}</td>
<td class="num">{dec3(fx["decimal"])}</td>
<td class="num">{pct(fx["pick_prob"])}</td>
<td>{tier_badge("High")}</td>
<td>{src_links(fx["source_ids"])}</td></tr>'''


# ---------------------------------------------------------------------------
# pages
# ---------------------------------------------------------------------------

def page_index(b):
    highs, picks = b["highs"], b["picks"]
    per_sport = Counter(fx["sport"] for fx in b["fixtures"])
    priced_by_sport = Counter(fx["sport"] for fx in b["fixtures"] if fx["markets"])
    best_tier = {}
    order = {"High": 3, "Medium": 2, "Low": 1}
    for fx in picks:
        t = fx["tier"]
        if order.get(t, 0) > order.get(best_tier.get(fx["sport"], "Low"), 0):
            best_tier[fx["sport"]] = t
    table = "".join(f'''<tr><td class="match"><a href="sports/{esc(slug)}.html"><strong>{esc(name)}</strong></a></td>
<td class="num">{per_sport.get(slug, 0)}</td><td class="num">{priced_by_sport.get(slug, 0)}</td>
<td class="num">{sum(1 for fx in picks if fx['sport'] == slug)}</td>
<td>{tier_badge(best_tier.get(slug)) if slug in best_tier else '<span class="mini">Directory only</span>'}</td>
<td>{src_links([s for s in next((f["source_ids"] for f in b["fixtures"] if f["sport"] == slug), D.OFFICIAL_LEAD.get(slug, ()))])}</td></tr>'''
                    for slug, name, *_ in D.SPORTS)
    highs_rows = "".join(row_high(fx) for fx in highs)
    body = f'''
<div class="hero"><p class="eyebrow">Executive summary &middot; Independent 15-sport card</p>
<h1>Today&rsquo;s best picks, with everything one click away</h1>
<p class="lede">Every line on this desk is originated independently, in the same spirit as OLBG&rsquo;s
match pages, and every row carries a link to the governing body or league that supplied the inputs.
Picks are graded Low, Medium or High. High means a strict read above 70.00% whose own fair price
stays inside the agreed &minus;250 to +10000 window &mdash; both tests, never one.</p>
<p class="stamp">Slate read and priced: {esc(STAMP_HUMAN)}</p></div>
<div class="kpis">
<div class="kpi"><b>{len(highs)}</b><span>High-confidence pick</span></div>
<div class="kpi"><b>{len(picks)}</b><span>Graded picks</span></div>
<div class="kpi"><b>{len(b["fixtures"])}</b><span>Matches &amp; entries tracked</span></div>
<div class="kpi"><b>15/15</b><span>Sports covered</span></div>
<div class="kpi"><b>&minus;250&hellip;+10000</b><span>High window</span></div>
</div>
<div class="note ok"><strong>Where are the picks?</strong> Right below, first. The full graded card sits on
<a class="src" href="picks.html">Picks</a>, the written selection for the High pick on
<a class="src" href="predictions.html">Predictions</a>, and every unresolved question on
<a class="src" href="flagged.html">Flagged for review</a>.</div>
<div class="note"><strong>Honesty note on the High window.</strong> Today&rsquo;s numbers resolved to exactly one High
(Edmonton, fair price precisely &minus;250, the window&rsquo;s edge). Vegas priced at 70.00% on the nose &mdash; the rule
asks for <em>strictly above</em> 70.00%, so it stays Medium, and New Jersey at &minus;267 sits just outside the band.
We do not stretch prices to manufacture a quota; the shortfall versus the five-High-per-sport aim is logged on the
Flagged page.</div>
<section><div class="head"><div><h2>High-confidence selection</h2>
<p>The single pick that passed both tests this evening.</p></div></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Match</th><th>Sport</th><th>Selection</th>
<th class="num">American</th><th class="num">Decimal</th><th class="num">Reason share</th><th>Tier</th><th>Official sources</th></tr></thead>
<tbody>{highs_rows}</tbody></table></div></div></section>
<section><div class="head"><div><h2>Coverage at a glance &mdash; all fifteen sports</h2>
<p>Matches tracked includes tonight&rsquo;s fixtures, entries that started before our read (kept, no price),
and directory-level coverage where an official hub was readable but individual rows were not.</p></div></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Sport</th><th class="num">Tracked</th>
<th class="num">Priced books</th><th class="num">Graded picks</th><th>Best tier</th><th>Lead official source</th></tr></thead>
<tbody>{table}</tbody></table></div></div></section>
<section class="grid cols-3">
<div class="tile"><h3><a href="markets.html">Markets</a></h3><p class="mini">Winner, totals and handicaps per
fixture with the two-way fair arithmetic shown out in the open.</p></div>
<div class="tile"><h3><a href="matches.html">Matches</a></h3><p class="mini">The full tracker: lines, states,
kick-off times, venues and what was playing when the slate was read.</p></div>
<div class="tile"><h3><a href="methodology.html">Methodology</a></h3><p class="mini">Shrinkage-and-log5 winners,
Poisson totals, seed-based darts pricing, and exactly what High requires.</p></div>
<div class="tile"><h3><a href="sources.html">Sources</a></h3><p class="mini">Every official page read this session,
with timestamps and exactly which numbers were taken.</p></div>
<div class="tile"><h3><a href="olbg.html">OLBG research</a></h3><p class="mini">Our reverse-engineering log of
OLBG&rsquo;s match market coverage for the same 15 sports.</p></div>
<div class="tile"><h3><a href="flagged.html">Flagged for review</a></h3><p class="mini">Blocked reads, novel edge
cases and anything a human should double-check.</p></div>
</section>'''
    return page("Executive summary", "Today's picks first, then every match, price and official source across the 15 sports in the brief.", "index.html", body)


def page_picks(b):
    rows = "".join(row_fixture(fx) for fx in b["picks"])
    body = f'''
<div class="hero"><p class="eyebrow">The graded card</p><h1>Picks &mdash; {len(b["picks"])} graded selections</h1>
<p class="lede">One selection per priced fixture, graded High, Medium or Low. Prices are the desk&rsquo;s own fair
lines. Use the source links in each row to check us.</p></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Match</th><th>Sport / competition</th><th>Stage</th>
<th>Selection</th><th>Tier</th><th class="num">American</th><th class="num">Decimal</th><th class="num">Share</th><th>Official sources</th></tr></thead>
<tbody>{rows}</tbody></table></div></div>'''
    return page("Picks", f"{len(b['picks'])} graded picks across the 15 sports in the brief.", "picks.html", body)


def page_predictions(b):
    blocks = ""
    for fx in b["highs"]:
        txt = D.PREDICTIONS[fx["id"]]
        blocks += f'''<div class="pred" id="{esc(fx["id"])}"><div class="who">{esc(fx["b"])} to beat {esc(fx["a"])} &mdash; {esc(fx["competition"])}</div>
<div class="meta">{tier_badge("High")}<span class="badge outline">{price(fx["american"])}</span>
<span class="badge outline">{dec3(fx["decimal"])} decimal</span>
<span class="badge outline">{pct(fx["pick_prob"])} on our ledger</span>
<span class="mini">{esc(kickoff(fx["start_utc"]))}</span></div>
<p class="body">{esc(txt)}</p>
{src_links(fx["source_ids"], small=False)}</div>'''
    n = len(b["highs"])
    body = f'''
<div class="hero"><p class="eyebrow">Written selections</p><h1>Predictions &mdash; one per High pick</h1>
<p class="lede">Every High-graded selection carries a written breakdown of at least thirty words,
grounded in the official numbers linked underneath it. Today that means {n} prediction{suf(n)}.</p></div>
{blocks}
<div class="note"><strong>Why so few?</strong> Predictions exist only where the price window and the strict
70% floor intersected tonight. Medium picks get grading and notes, not padding; see the
<a class="src" href="picks.html">picks card</a>.</div>'''
    return page("Predictions", "Written predictions for today's High-confidence selections.", "predictions.html", body)


def page_markets(b):
    chunks = ""
    for fx in [f for f in b["fixtures"] if f["markets"]]:
        sub = []
        for m in fx["markets"]:
            outs = "".join(f'''<tr><td class="idx">{esc(o["name"])}</td>
<td class="num">{price(o["american"])}</td><td class="num">{dec3(o["decimal"])}</td>
<td class="num">{pct(o["prob"])}</td><td>{src_links(fx["source_ids"])}</td></tr>''' for o in m["outcomes"])
            sub.append(f'''<div class="pad"><div class="kind">{esc(m["label"])}{'' if m.get("measured", True) else " &middot; estimate"}</div>
<div class="table-wrap"><table class="lines"><thead><tr><th>Line</th><th class="num">American</th>
<th class="num">Decimal</th><th class="num">Share</th><th>Official sources</th></tr></thead><tbody>{outs}</tbody></table></div></div>''')
        withheld = "".join(f'<span class="badge amber">Withheld: {esc(w["key"])}</span> <span class="mini">{esc(w["reason"])}</span>'
                           for w in (fx.get("markets_withheld") or []))
        chunks += f'''<div class="markets" id="{esc(fx["id"])}"><header>
<span class="match">{esc(fx["a"])} <span class="mini">v</span> {esc(fx["b"])}</span>
<span class="badge slate">{esc(SPORT_NAME.get(fx["sport"], fx["sport"]))}</span>
<span class="mini">{esc(fx.get("competition",""))} &middot; {esc(kickoff(fx["start_utc"]))}</span>
{('<span class="badge outline">Pick: ' + esc(fx["pick"]) + " " + price(fx["american"]) + " (" + esc(fx["tier"]) + ")</span>") if fx.get("pick") else ""}
</header>{"".join(sub)}{("<div class='pad'>" + withheld + "</div>") if withheld else ""}</div>'''
    body = f'''
<div class="hero"><p class="eyebrow">Originated lines</p><h1>Markets &mdash; every priced book, shown open-book</h1>
<p class="lede">Match winner, totals and handicap books per fixture, two-way fair with zero margin added.
Shares are probabilities implied by our own numbers; the official source of every input is linked on each row.</p></div>
{chunks}'''
    return page("Markets", "Every originated market line with its official inputs, per fixture.", "markets.html", body)


def page_matches(b):
    rows = "".join(row_fixture(fx, with_markets_note=True) for fx in b["fixtures"])
    body = f'''
<div class="hero"><p class="eyebrow">Tracker</p><h1>Matches &mdash; {len(b["fixtures"])} tracked entries</h1>
<p class="lede">Everything on the board, including fixtures already in play at read time (kept, unpriced),
entries awaiting a pairing, and directory-level coverage where a hub was readable but rows were not.</p></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Entry</th><th>Sport / competition</th><th>Stage</th>
<th>Selection</th><th>Tier</th><th class="num">American</th><th class="num">Decimal</th><th class="num">Share</th>
<th>Official sources</th></tr></thead><tbody>{rows}</tbody></table></div></div>'''
    return page("Matches", f"Full tracker: {len(b['fixtures'])} entries with states, times and sources.", "matches.html", body)


def page_flagged(b):
    fr = "".join(f'''<tr><td class="match">{esc(f["id"])}<span class="sub">{esc(f["kind"])}</span></td>
<td>{esc(f["text"])}</td><td>{src_links(FLAG_REFS.get(f["id"], ["nhl-standings"]))}</td></tr>'''
                 for f in b["flags"])
    fx_rows = ""
    for fx in b["fixtures"]:
        fl = fx.get("flags") or []
        if not fl:
            continue
        detail = esc(fx.get("tier_note") or fx.get("context") or "")
        fx_rows += f'''<tr><td class="match">{esc(fx["a"] or fx["competition"])} <span class="mini">/</span> {esc(fx["b"] or "open")}
<span class="sub">{esc(SPORT_NAME.get(fx["sport"], fx["sport"]))}</span></td>
<td>{"".join(f'<span class="badge outline">{esc(x)}</span> ' for x in fl)}</td>
<td>{detail}</td><td>{src_links(fx["source_ids"])}</td></tr>'''
    holder = []
    for fx in b["fixtures"]:
        for w in (fx.get("markets_withheld") or []):
            holder.append(f'''<tr><td class="match">{esc(fx["a"] or fx["competition"])} <span class="mini">v</span> {esc(fx["b"] or "open")}</td>
<td><span class="badge amber">{esc(w["key"])}</span></td><td>{esc(w["reason"])}</td>
<td>{src_links(fx["source_ids"])}</td></tr>''')
    body = f'''
<div class="hero"><p class="eyebrow">Transparency</p><h1>Flagged for review</h1>
<p class="lede">The registers a human should read first: price-window edge cases, sources that resisted a static
read, matches that were live before our own page views, and every market we declined to originate rather than guess.</p></div>
<section><div class="head"><div><h2>Desk-level flags</h2><p>Recorded against the session as a whole.</p></div></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Flag</th><th>What happened</th><th>Reference</th></tr></thead>
<tbody>{fr}</tbody></table></div></div></section>
<section><div class="head"><div><h2>Fixture-level flags</h2><p>Carried by individual entries.</p></div></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Entry</th><th>Labels</th><th>Detail</th><th>Official sources</th></tr></thead>
<tbody>{fx_rows}</tbody></table></div></div></section>
<section><div class="head"><div><h2>Withheld markets</h2><p>Markets deliberately blank &mdash; the inputs were not officially readable this session.</p></div></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Entry</th><th>Market</th><th>Reason</th><th>Official sources</th></tr></thead>
<tbody>{"".join(holder) if holder else '<tr><td colspan="4">None on today&rsquo;s books.</td></tr>'}</tbody></table></div></div></section>'''
    return page("Flagged for review", "Every edge case, blocked source and withheld market, on one page.", "flagged.html", body)


def page_sources(b):
    rows = "".join(f'''<tr><td class="match">{esc(s["label"])}<span class="sub">{s["id"]}</span></td>
<td>{('<span class="badge high">Official</span>' if s["official"] else '<span class="badge slate">Discovery</span>')}</td>
<td><span class="mini">{esc(s["observed"])}</span></td><td>{esc(s["scope"])}</td>
<td><a class="src" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["url"].split('/')[2])}<span class="arrow">&#8599;</span></a></td></tr>'''
                   for s in D.SOURCES)
    body = f'''
<div class="hero"><p class="eyebrow">Provenance</p><h1>Sources read this session</h1>
<p class="lede">The ledger of every page consulted. Scope says, in its own words, which numbers were taken.
Discovery sources (OLBG included) are never used to back a match price; official means governing body,
league, tour or federation.</p></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Source</th><th>Role</th><th>Observed (UTC)</th>
<th>Numbers taken / scope</th><th>Publisher</th></tr></thead><tbody>{rows}</tbody></table></div></div>'''
    return page("Sources", "All sources consulted, with observed timestamps and the numbers taken.", "sources.html", body)


def page_methodology(b):
    body = f'''
<div class="hero"><p class="eyebrow">How the pricing works</p><h1>Methodology</h1>
<p class="lede">The desk never copies a bookmaker line. Every price is originated from officially published
numbers using the documented estimator below, shown open-book on the markets page.</p></div>
<section class="grid cols-2">
<div class="tile"><h3>Match winners &mdash; shrinkage, then log5</h3>
<ul class="ticks"><li>Each side&rsquo;s season win share is shrunk toward 50% with a Beta(2,2) prior:
<code>(wins + 2) / (games + 4)</code>.</li>
<li>Two shrunk shares are paired with the Bradley&ndash;Terry / Bill James log5:
<code>p = a(1&minus;b) / (a(1&minus;b) + b(1&minus;a))</code>.</li>
<li>No home adjustment, no player adjustment, no market reading is layered on. Where the only official
evidence is partial, the market is flagged as one-sided and graded down.</li></ul></div>
<div class="tile"><h3>Totals &amp; handicaps &mdash; Poisson from official goals/points</h3>
<ul class="ticks"><li>Each side&rsquo;s expected rate blends its own attack average with the opponent&rsquo;s
defensive average, both read from official tables: <code>(GF/g + GA_allowed/g) / 2</code>.</li>
<li>Independent Poisson scores give Under/Over for the standard half-lines (5.5 hockey, 8.5 baseball),
and a margin distribution prices &plusmn;1.5 handicaps as an exact two-way complement.</li></ul></div>
<div class="tile"><h3>Darts &amp; rugby league &mdash; bracketed reads</h3>
<ul class="ticks"><li>Darts matches are priced from official PDC tournament seeds alone
(rate = 1/seed, normalised). Where official scoring averages were not readable, spread/total markets
stayed blank.</li>
<li>Rugby League World Cup fixtures use the official pool order, nudged slightly for the host side,
and are explicitly capped in confidence.</li></ul></div>
<div class="tile"><h3>The confidence tiers</h3>
<ul class="ticks"><li><span class="badge high">High</span> requires <em>both</em> tests: our probability strictly
above 70.00%, while its own fair American price stays inside &minus;250 to +10000; must be a match market with
both sides measured from official sources, on an upcoming fixture. Estimates (multi-runner golf/F1) are never High.</li>
<li><span class="badge medium">Medium</span> covers 55&ndash;70% reads, cleanly-priced near-misses at the window edges
(Vegas at exactly 70.00%, New Jersey at &minus;267), and stronger probabilities whose price would be shorter than &minus;250.</li>
<li><span class="badge low">Low</span> is everything else priced: coin-flips, one-sided reads, conflicted reads.</li></ul></div>
<div class="tile"><h3>Fair lines, no margin</h3><p>Prices are decimal 1/p with the integer American shown alongside.
Nothing is padded for profit &mdash; the card is a research ledger, not an offer. The brief&rsquo;s window is enforced on
our own fair integer; at the edges the rule is inclusive of &minus;250 and strict above 70.00%.</p></div>
<div class="tile"><h3>Source discipline</h3><p>Only governing bodies, leagues, tours and federations count as
official. OLBG is used for discovery and market-structure research only and never backs a number. Anything that
resisted a static read (scripts, cookie walls, navigation shells) is left blank and logged on the
<a class="src" href="flagged.html">Flagged for review</a> page.</p></div>
</section>'''
    return page("Methodology", "How every line is originated: shrinkage+log5, Poisson totals, seed reads and the confidence tiers.", "methodology.html", body)


def page_olbg(b):
    rows = ""
    for slug, name, route in D.SPORTS:
        log = OLBG_LOG.get(slug, {}).get("findings", "")
        off = next((f["source_ids"] for f in b["fixtures"] if f["sport"] == slug), D.OFFICIAL_LEAD.get(slug, ()))
        rows += f'''<tr><td class="match"><a href="sports/{esc(slug)}.html"><strong>{esc(name)}</strong></a></td>
<td><a class="src" href="{esc(route)}" target="_blank" rel="noopener noreferrer">{esc(route.split('/tips/')[-1])}<span class="arrow">&#8599;</span></a></td>
<td>{esc(log)}</td><td>{src_links(list(off))}</td></tr>'''
    body = f'''
<div class="hero"><p class="eyebrow">Reverse-engineering log</p><h1>OLBG research</h1>
<p class="lede">What OLBG lists for each of the 15 sports in the brief, in their own match-market structure &mdash; winner,
handicap, match totals and related lines. These pages taught us which markets to originate; they are
never used as the source of a number.</p></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Sport</th><th>OLBG tips route</th><th>What the hub showed at read time</th><th>Our official counterparty</th></tr></thead>
<tbody>{rows}</tbody></table></div></div>
<div class="callout"><strong>Why OLBG appears on the Sources page as &lsquo;discovery&rsquo;.</strong> OLBG is the site being
studied, not an authority on the sport. A market structure can be learned from it; a score, table or
injury can only be confirmed from the league&rsquo;s own pages, which is what the links in every betting row provide.</div>'''
    return page("OLBG research", "The reverse-engineering log: OLBG's match-market coverage for the 15 sports in the brief.", "olbg.html", body)


def page_sports_index(b):
    tiles = ""
    for slug, name, *_ in D.SPORTS:
        fs = [fx for fx in b["fixtures"] if fx["sport"] == slug]
        priced = sum(1 for f in fs if f["markets"])
        picks = sum(1 for f in fs if f.get("pick"))
        highs = sum(1 for f in fs if f.get("tier") == "High")
        tiles += f'''<div class="tile"><h3><a href="sports/{esc(slug)}.html">{esc(name)}</a></h3>
<p class="mini">{esc(f"{len(fs)} entr{'y' if len(fs)==1 else 'ies'} &middot; {priced} priced &middot; {picks} picks &middot; {highs} high")}</p></div>'''
    body = f'''
<div class="hero"><p class="eyebrow">Fifteen sports, one ledger</p><h1>All sports</h1>
<p class="lede">The brief&rsquo;s full slate. Each sport page keeps its own card, its own tracker and its own flags.</p></div>
<section class="grid cols-3">{tiles}</section>'''
    return page("All 15 sports", "Every sport in the brief with its own card page.", "sports.html", body)


def page_sport(b, slug, name, route):
    fs = [fx for fx in b["fixtures"] if fx["sport"] == slug]
    picks = [fx for fx in fs if fx.get("pick")]
    log = OLBG_LOG.get(slug, {}).get("findings", "")
    fallback = ('<tr><td colspan="8">No graded picks on this board today &mdash; see the tracker and flags below.</td>'
                f'<td>{src_links(list(fs[0]["source_ids"]) if fs else D.OFFICIAL_LEAD.get(slug, ()))}</td></tr>')
    pick_rows = "".join(row_fixture(fx) for fx in picks) or fallback
    track_rows = "".join(row_fixture(fx, with_markets_note=True, id_suffix="_t") for fx in fs)
    body = f'''
<div class="hero"><p class="eyebrow">{esc(name)} desk</p><h1>{esc(name)}</h1>
<p class="lede">{esc(log)}</p>
<p class="stamp">OLBG route studied: <a class="src" href="{esc(route)}" target="_blank" rel="noopener noreferrer">{esc(route)}<span class="arrow">&#8599;</span></a></p></div>
<section><div class="head"><div><h2>Picks</h2></div></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Match</th><th>Sport / competition</th><th>Stage</th>
<th>Selection</th><th>Tier</th><th class="num">American</th><th class="num">Decimal</th><th class="num">Share</th><th>Official sources</th></tr></thead>
<tbody>{pick_rows}</tbody></table></div></div></section>
<section><div class="head"><div><h2>Tracker</h2></div></div>
<div class="card"><div class="table-wrap"><table><thead><tr><th>Entry</th><th>Sport / competition</th><th>Stage</th>
<th>Selection</th><th>Tier</th><th class="num">American</th><th class="num">Decimal</th><th class="num">Share</th><th>Official sources</th></tr></thead>
<tbody>{track_rows}</tbody></table></div></div></section>'''
    return page(name, f"{name} picks, tracker and official sources from today's independent card.", "", body, depth=1)


# ---------------------------------------------------------------------------
# JSON exports
# ---------------------------------------------------------------------------

def write_json(name, obj):
    (DATA / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def export_json(b):
    fixture_view = []
    for fx in b["fixtures"]:
        fixture_view.append({
            "id": fx["id"], "sport": fx["sport"], "competition": fx["competition"],
            "round": fx.get("round"), "a": fx["a"], "b": fx["b"], "venue": fx.get("venue"),
            "start_utc": fx["start_utc"], "state": fx["state"], "source_ids": fx["source_ids"],
            "facts": fx.get("facts") or {}, "injuries": fx.get("injuries") or {},
            "context": fx.get("context", ""), "flags": fx.get("flags") or [],
            "markets_withheld": fx.get("markets_withheld") or [],
        })
    lines = []
    picks = []
    for fx in b["fixtures"]:
        for m in fx["markets"]:
            lines.append({"fixture": fx["id"], "sport": fx["sport"], "market": m["key"],
                          "label": m["label"], "measured": m.get("measured", True),
                          "outcomes": m["outcomes"]})
        if fx.get("pick"):
            picks.append({"fixture": fx["id"], "sport": fx["sport"], "match": [fx["a"], fx["b"]],
                          "pick": fx["pick"], "american": fx["american"], "decimal": fx["decimal"],
                          "probability": fx["pick_prob"], "tier": fx["tier"],
                          "tier_note": fx.get("tier_note", ""), "source_ids": fx["source_ids"]})
    preds = [{"fixture": fx["id"], "sport": fx["sport"], "selection": fx["pick"],
              "american": fx["american"], "text": D.PREDICTIONS[fx["id"]],
              "source_ids": fx["source_ids"]} for fx in b["highs"]]
    coverage = []
    for slug, name, *_ in D.SPORTS:
        fs = [fx for fx in b["fixtures"] if fx["sport"] == slug]
        coverage.append({"sport": slug, "name": name, "tracked": len(fs),
                         "priced": sum(1 for f in fs if f["markets"]),
                         "picks": sum(1 for f in fs if f.get("pick")),
                         "high": sum(1 for f in fs if f.get("tier") == "High")})
    olbg = [{"sport": slug, "name": name, "route": route, "log": OLBG_LOG.get(slug, {}).get("findings", "")}
            for slug, name, route in D.SPORTS]
    manifest = {
        "generated_at": GENERATED, "desk": D.DESK, "task": D.TASK,
        "counts": {"fixtures": len(b["fixtures"]),
                   "priced": sum(1 for f in b["fixtures"] if f["markets"]),
                   "picks": len(b["picks"]), "high": len(b["highs"]),
                   "predictions": len(preds), "lines": len(lines),
                   "flags": len(b["flags"]), "sports": len(D.SPORTS),
                   "sources": len(D.SOURCES)},
        "window": {"american_min": -250, "american_max": 10000},
        "input_sha256": hashlib.sha256((ROOT / "scripts" / "s99d43605_data.py").read_bytes()).hexdigest(),
        "pages": ["index.html", "picks.html", "predictions.html", "markets.html", "matches.html",
                  "flagged.html", "sources.html", "methodology.html", "olbg.html", "sports.html"]
        + [f"sports/{slug}.html" for slug, *_ in D.SPORTS],
    }
    write_json("fixtures.json", {"generated_at": GENERATED, "fixtures": fixture_view})
    write_json("lines.json", {"generated_at": GENERATED, "lines": lines})
    write_json("picks.json", {"generated_at": GENERATED, "picks": picks})
    write_json("predictions.json", {"generated_at": GENERATED, "predictions": preds})
    write_json("flags.json", {"generated_at": GENERATED, "flags": b["flags"]})
    write_json("sources.json", {"generated_at": GENERATED, "sources": D.SOURCES})
    write_json("coverage.json", {"generated_at": GENERATED, "coverage": coverage})
    write_json("olbg.json", {"generated_at": GENERATED, "routes": olbg, "tickets": D.OLBG_TICKETS})
    write_json("manifest.json", manifest)
    return manifest


def suf(n):
    return "" if n == 1 else "s"


def main():
    b = built()
    OUT.mkdir(exist_ok=True)
    (OUT / "sports").mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    pages = {
        "index.html": page_index(b),
        "picks.html": page_picks(b),
        "predictions.html": page_predictions(b),
        "markets.html": page_markets(b),
        "matches.html": page_matches(b),
        "flagged.html": page_flagged(b),
        "sources.html": page_sources(b),
        "methodology.html": page_methodology(b),
        "olbg.html": page_olbg(b),
        "sports.html": page_sports_index(b),
    }
    for slug, name, route in D.SPORTS:
        pages[f"sports/{slug}.html"] = page_sport(b, slug, name, route)
    for rel, content in pages.items():
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    manifest = export_json(b)
    print(f"built {len(pages)} pages into {OUT.relative_to(ROOT)} + {len(manifest['pages'])} mirrored, "
          f"counts={manifest['counts']}")


if __name__ == "__main__":
    main()
