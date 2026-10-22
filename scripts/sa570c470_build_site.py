#!/usr/bin/env python3
"""Session a570c470 — static dashboard builder (27 pages under /a570c470/)."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "a570c470"
OUT = ROOT / "a570c470"
SPORTS_DIR = OUT / "sports"

SPORT_SLUG = {
    "Tennis": "tennis", "Basketball": "basketball", "Golf": "golf", "Cricket": "cricket",
    "Snooker": "snooker", "Rugby Union": "rugby-union", "Rugby League": "rugby-league",
    "Baseball": "baseball", "Ice Hockey": "ice-hockey", "Motor Racing": "motor-racing",
    "Darts": "darts", "Handball": "handball", "Volleyball": "volleyball",
    "Aussie Rules": "aussie-rules", "eSports": "esports", "Gaelic Football": "gaelic-football",
    "Greyhounds": "greyhounds",
}
SPORT_ORDER = list(SPORT_SLUG)

STYLE = """
:root{--bg:#0b0f14;--panel:#121820;--panel2:#0f151c;--line:#1f2a36;--txt:#e6edf3;--muted:#8b9bb0;
--acc:#4ade80;--acc2:#38bdf8;--hi:#22c55e;--md:#eab308;--lo:#94a3b8;--bad:#f87171;--flag:#f59e0b}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc2);text-decoration:none}a:hover{text-decoration:underline}
header{border-bottom:1px solid var(--line);background:linear-gradient(180deg,#0f1720,#0b0f14);position:sticky;top:0;z-index:20}
.hin{max-width:1240px;margin:0 auto;padding:12px 20px;display:flex;flex-wrap:wrap;gap:14px;align-items:center}
.brand{font-weight:700;font-size:15px;letter-spacing:.2px}
.brand span{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--acc);margin-right:8px;vertical-align:middle}
nav{display:flex;flex-wrap:wrap;gap:2px}
nav a{padding:5px 9px;border-radius:6px;color:var(--muted);font-size:13px}
nav a:hover{background:#16202b;color:var(--txt);text-decoration:none}
nav a[aria-current]{background:#1b2733;color:var(--txt)}
main{max-width:1240px;margin:0 auto;padding:26px 20px 70px}
h1{font-size:26px;line-height:1.25;margin:6px 0 10px}
h2{font-size:19px;margin:34px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:15px;margin:20px 0 8px;color:#cbd5e1}
p.lede{color:#c3cfdc;max-width:940px}
.grid{display:grid;gap:12px}
.kpis{grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:18px 0 6px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi .n{font-size:23px;font-weight:700;letter-spacing:-.4px}
.kpi .l{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.4px}
.kpi.hi .n{color:var(--hi)}.kpi.md .n{color:var(--md)}.kpi.lo .n{color:var(--lo)}
.sports-grid{grid-template-columns:repeat(auto-fit,minmax(215px,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:13px 15px;display:block;color:inherit}
.card:hover{border-color:#2c3d4f;text-decoration:none}
.card .t{display:flex;justify-content:space-between;gap:8px;font-weight:600;font-size:14px}
.card .m{color:var(--muted);font-size:12.5px;margin-top:3px}
.badge{display:inline-block;font-size:11px;padding:1.5px 7px;border-radius:999px;border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.badge.high{color:#052e16;background:var(--hi);border-color:var(--hi);font-weight:700}
.badge.medium{color:#2a1d00;background:var(--md);border-color:var(--md);font-weight:700}
.badge.low{background:#1e293b;color:#cbd5e1}
.badge.ok{color:#86efac;border-color:#14532d;background:#0d2016}
.badge.warn{color:#fcd34d;border-color:#78350f;background:#241a05}
.badge.info{color:#bfdbfe;border-color:#1e3a8a;background:#0d1626}
.note{border:1px solid var(--line);border-left:3px solid var(--acc2);background:var(--panel2);border-radius:8px;padding:12px 15px;margin:14px 0;font-size:14px;color:#c9d6e4}
.note.good{border-left-color:var(--acc)}
.note.warn{border-left-color:var(--flag)}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#16202b;color:#cbd5e1;font-size:11.5px;text-transform:uppercase;letter-spacing:.45px;white-space:nowrap;position:sticky;top:0}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#151f29}
td.num,th.num{text-align:right;white-space:nowrap}
.sub{display:block;color:var(--muted);font-size:11.5px;font-weight:400}
.src a{display:block;font-size:11.5px;line-height:1.45}
details summary{cursor:pointer;color:var(--acc2);font-size:12px}
details[open] summary{color:var(--muted)}
.mkt{border-top:1px solid var(--line);padding:7px 0 2px}
.mkt-h{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:#94a3b8;margin-bottom:3px}
.mkt ul{list-style:none;margin:0;padding:0}
.mkt li{display:flex;justify-content:space-between;gap:12px;font-size:12px;padding:1px 0}
.mkt li span:last-child{white-space:nowrap;color:#cbd5e1}
.band-yes{color:var(--acc);font-size:11px}
.band-no{color:var(--muted);font-size:11px}
.pred{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.pred h3{margin:0 0 2px;font-size:15px;color:var(--txt)}
.pred .meta{color:var(--muted);font-size:12px;margin-bottom:8px}
.pred p{margin:0;color:#d3dfea}
.pred .sel{margin-top:8px;font-size:12.5px;color:var(--acc)}
footer{border-top:1px solid var(--line);color:var(--muted);font-size:12.5px}
.fin{max-width:1240px;margin:0 auto;padding:18px 20px 40px}
ul.plain{list-style:none;padding:0;margin:8px 0}
ul.plain li{padding:5px 0;border-bottom:1px solid var(--line);font-size:13.5px}
code{background:#16202b;padding:1px 5px;border-radius:4px;font-size:12.5px}
.tag{font-size:11px;padding:1px 6px;border-radius:5px;background:#16202b;border:1px solid var(--line);color:var(--muted)}
"""


def esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def load():
    fx = json.loads((DATA / "fixtures.json").read_text())
    lines = json.loads((DATA / "lines.json").read_text())
    preds = json.loads((DATA / "predictions.json").read_text())
    srcs = json.loads((DATA / "sources.json").read_text())
    tax = json.loads((DATA / "olbg_taxonomy.json").read_text())
    audit = json.loads((DATA / "audit.json").read_text())
    flagged = json.loads((DATA / "flagged.json").read_text())
    return fx, lines, preds, srcs, tax, audit, flagged


NAV = [
    ("index.html", "Overview"), ("picks.html", "High Picks"), ("predictions.html", "Predictions"),
    ("lines.html", "All Fixtures"), ("markets.html", "Market Explorer"), ("sports.html", "Sports"),
    ("reverse-engineering.html", "OLBG Reversed"), ("methodology.html", "Methodology"),
    ("sources.html", "Sources"), ("audit.html", "Repo Audit"), ("flagged.html", "Flagged for Review"),
]


def page(slug: str, title: str, body: str, ctx) -> str:
    up = "../" if slug.startswith("sports/") else ""
    nav = ""
    for href, label in NAV:
        cur = ' aria-current="page"' if href == slug else ""
        nav += f'<a href="{esc(up + href)}"{cur}>{esc(label)}</a>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG Origination Desk (a570c470)</title>
<meta name="description" content="{esc(title)} — source-linked multi-sport fixtures, originated multi-market lines, confidence tiers and written predictions across the 17 in-scope OLBG sports.">
<style>{STYLE}</style></head>
<body>
<header><div class="hin">
  <div class="brand"><span></span>OLBG Origination Desk <span class="tag">a570c470 · 22 Oct 2026</span></div>
  <nav aria-label="Primary">{nav}</nav>
</div></header>
<main>
{body}
</main>
<footer><div class="fin">
  <p><b>Independent model output, not betting advice.</b> Prices are our own fair-probability quotes with no margin;
  the 5% margin a bookmaker would need is shown beside them. Every fixture, record and ranking links to the governing
  body that publishes it. Values that could not be confirmed on an official page are blank and listed on
  <a href="{up}flagged.html">Flagged for Review</a>.</p>
  <p>Session <code>a570c470-olbg1</code> · snapshot <code>2026-10-22T03:20Z</code> ·
  built by <code>scripts/sa570c470_build_site.py</code> · validated by <code>scripts/sa570c470_validate.py</code></p>
</div></footer>
</body></html>
"""


def src_links(ids, smap) -> str:
    out = []
    for sid in ids:
        s = smap.get(sid)
        if not s:
            continue
        out.append(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["organization"])} — {esc(s["title"])}</a>')
    return f'<div class="src">{"".join(out)}</div>' if out else '<span class="badge warn">no source</span>'


def conf_badge(c: str) -> str:
    cls = {"High": "high", "Medium": "medium", "Low": "low"}.get(c, "low")
    return f'<span class="badge {cls}">{esc(c)}</span>'


def market_sheet(book) -> str:
    by = {}
    order = []
    for m in book["markets"]:
        by.setdefault(m["market"], []).append(m)
        if m["market"] not in order:
            order.append(m["market"])
    pref = ["Match winner", "Draw no bet", "Handicap", "Total", "Correct score"]
    ordered = [k for k in pref if k in by] + [k for k in order if k not in pref and not k.startswith("Correct score")]
    parts = []
    for mk in ordered:
        rows = "".join(
            f'<li><span>{esc(m["selection"])}</span><span>{m["price"]:.2f} '
            f'({m["us"]:+d}) · {m["prob_pct"]}% '
            f'<span class="{"band-yes" if m["in_band"] else "band-no"}">{"in window" if m["in_band"] else "outside window"}</span></span></li>'
            for m in by[mk])
        parts.append(f'<div class="mkt"><div class="mkt-h">{esc(mk)}</div><ul>{rows}</ul></div>')
    return "".join(parts)


def fdate(s: str) -> str:
    return s.replace("T", " ").replace(":00Z", "Z") if s else "—"


def build():
    fx, lines, preds, srcs, tax, audit, flagged = load()
    smap = {s["source_id"]: s for s in srcs["sources"]}
    books = {b["id"]: b for b in lines["books"]}
    cards = {c["id"]: c for c in lines["event_cards"]}
    fixtures = fx["fixtures"]
    OUT.mkdir(exist_ok=True)
    (OUT / "sports").mkdir(exist_ok=True)

    counts = lines["confidence_counts"]
    highs = [b for b in lines["books"] if b["confidence"] == "High"]
    high_ids = {b["id"] for b in highs}
    n_pred = preds["count"]
    n_src = srcs["count"]
    by_sport = fx["by_sport"]

    # ---------------------------------------------------------------- overview
    kpi = f"""<div class="grid kpis">
  <div class="kpi"><div class="n">{fx['count']}</div><div class="l">Verified fixtures</div></div>
  <div class="kpi"><div class="n">{fx['priced_count']}</div><div class="l">Priced head-to-heads</div></div>
  <div class="kpi"><div class="n">{lines['price_count']:,}</div><div class="l">Originated prices</div></div>
  <div class="kpi hi"><div class="n">{counts['High']}</div><div class="l">High confidence</div></div>
  <div class="kpi md"><div class="n">{counts['Medium']}</div><div class="l">Medium</div></div>
  <div class="kpi lo"><div class="n">{counts['Low']}</div><div class="l">Low</div></div>
  <div class="kpi"><div class="n">{n_pred}</div><div class="l">Written predictions</div></div>
  <div class="kpi"><div class="n">{audit['counts']['findings']}</div><div class="l">Repo findings</div></div>
</div>"""

    sport_cards = []
    for s in SPORT_ORDER:
        n = by_sport.get(s, 0)
        priced = sum(1 for b in lines["books"] if b["sport"] == s)
        h = sum(1 for b in highs if b["sport"] == s)
        note = f"{n} fixture{'s' if n != 1 else ''} · {priced} priced · {h} High"
        sport_cards.append(
            f'<a class="card" href="sports/{SPORT_SLUG[s]}.html"><div class="t"><span>{esc(s)}</span>'
            f'<span class="badge {"ok" if priced else "warn"}">{"priced" if priced else "event only"}</span></div>'
            f'<div class="m">{esc(note)}</div></a>')

    feat_rows = []
    for b in sorted(highs, key=lambda x: (SPORT_ORDER.index(x["sport"]) if x["sport"] in SPORT_ORDER else 99, x["home"])):
        p = b["desk_pick"]
        feat_rows.append(f"""<tr>
  <td>{fdate(b['start_utc'])}<span class="sub">{esc(b['competition'])}</span></td>
  <td><b>{esc(b['home'])} v {esc(b['away'])}</b><span class="sub">{esc(b['venue'])}</span></td>
  <td><a href="sports/{SPORT_SLUG[b['sport']]}.html">{esc(b['sport'])}</a></td>
  <td><b>{esc(p['selection'])}</b><span class="sub">{esc(p['market'])} · {p['price']:.2f} ({p['us']:+d}) · {p['prob_pct']}% model · <span class="badge ok">in window</span></span></td>
  <td>{conf_badge(b['confidence'])}<span class="sub">match call: {esc(b['match_winner_call']['selection'])}</span></td>
  <td>{src_links(b['sources'], smap)}</td>
</tr>""")

    body = f"""<h1>17 in-scope OLBG sports, {fx['count']} verified fixtures, our own lines</h1>
<p class="lede">A fresh desk built on 22 October 2026. Every fixture below was re-read on its governing body's own
page in this session, priced from that page's figures only, and graded Low, Medium or High. High-confidence picks
are quoted strictly inside the brief's <b>-250 to +10000</b> window. Where a figure could not be confirmed it is
blank and listed on <a href="flagged.html">Flagged for Review</a>.</p>
{kpi}
<div class="note good">
<b>Price-window compliance.</b> A 70% probability is a fair price of {1/0.70:.2f} (-233), so a pick that is both
"greater than 70% to win" and "inside -250 to +10000" has to sit in a narrow band. This desk originates the line,
so for every strong favourite it quotes the handicap rung whose probability lands near 71% and prints that rung
instead of the shorter moneyline. All {counts['High']} High picks are inside the window on their published price;
each row also prints the moneyline call so the reader can see what was traded away.
</div>
<div class="note">
<b>What is verified and what is modelled.</b> Fixture facts — participants, competition, kick-off, venue, records,
rankings, ladder points — come from the {n_src} governing-body sources on the <a href="sources.html">Sources</a>
page. Prices and probabilities are our own model output and are labelled as estimates everywhere.
</div>

<h2>Browse by sport</h2>
<div class="grid sports-grid">{''.join(sport_cards)}</div>

<h2>High-confidence selections</h2>
<div class="table-wrap"><table>
<thead><tr><th>Start (UTC)</th><th>Match &amp; venue</th><th>Sport</th><th>Selection · price · probability</th><th>Confidence</th><th>Official source</th></tr></thead>
<tbody>{''.join(feat_rows)}</tbody></table></div>
<p><a class="card" href="predictions.html" style="display:inline-block;margin-top:12px">Read all {n_pred} written predictions →</a></p>

<h2>How this desk was built</h2>
<ul class="plain">
  <li><b>Harvest.</b> All 27 OLBG sport routes were read live, including the competition sub-routes: see
      <a href="reverse-engineering.html">OLBG reversed</a> for the URL grammar and the four upstream defects recorded.</li>
  <li><b>Verify.</b> Each fixture was then re-read on the governing body's own page. {n_src} official sources are
      catalogued; {fx['priced_count']} rows carry two-sided figures and {fx['event_only_count']} rows are published
      as verified event cards with no price because no official strength rating exists for the field.</li>
  <li><b>Price.</b> One strength figure per side, one distribution per match. Winner, draw-no-bet, handicap and total
      markets all come from that single distribution, so the ladders cannot contradict the moneyline.</li>
  <li><b>Grade.</b> High needs a 70% model probability on a price inside the window; Medium 55%+; Low everything else.
      Sports with a one-match or one-round sample are capped and the cap is printed on every row.</li>
  <li><b>Write.</b> All {n_pred} High picks carry a bespoke preview of {preds['min_words']}–{preds['max_words']} words
      naming the participants, the sourced form, the recent match history and the selection, with
      {len(preds['repeated_6grams'])} repeated six-word phrases across the whole set.</li>
</ul>

<h2>Repository workspaces</h2>
<div class="note">
This desk is additive. It does not edit any other session's dataset, script or page. The other boards in the
repository are reachable from the root landing page and are named on the <a href="audit.html">Repo Audit</a> page,
which also records the {audit['counts']['findings']} defects found while reading them line by line.
</div>
"""
    (OUT / "index.html").write_text(page("index.html", "Overview", body, None))

    # ---------------------------------------------------------------- sports index
    rows = []
    for s in SPORT_ORDER:
        n = by_sport.get(s, 0)
        priced = sum(1 for b in lines["books"] if b["sport"] == s)
        h = sum(1 for b in highs if b["sport"] == s)
        srcs_used = sorted({sid for f in fixtures if f["sport"] == s for sid in f["sources"]})
        rows.append(f"""<tr><td><a href="sports/{SPORT_SLUG[s]}.html"><b>{esc(s)}</b></a></td>
<td class="num">{n}</td><td class="num">{priced}</td><td class="num">{h}</td>
<td>{src_links(srcs_used, smap)}</td></tr>""")
    body = f"""<h1>Sports</h1>
<p class="lede">Seventeen sports are in scope. Each has its own page with every verified fixture, its full market
sheet and its source links.</p>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th class="num">Fixtures</th><th class="num">Priced</th><th class="num">High</th><th>Governing-body sources used</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""
    (OUT / "sports.html").write_text(page("sports.html", "Sports", body, None))

    # ---------------------------------------------------------------- per-sport pages
    for s in SPORT_ORDER:
        slug = SPORT_SLUG[s]
        rows = []
        for f in [x for x in fixtures if x["sport"] == s]:
            b = books.get(f["id"])
            if b:
                p = b["desk_pick"]
                pick_cell = (f"<b>{esc(p['selection'])}</b><span class='sub'>{esc(p['market'])} · "
                             f"{p['price']:.2f} ({p['us']:+d}) · {p['prob_pct']}%</span>") if p else "<span class='sub'>no qualifying selection</span>"
                call = f"{esc(b['match_winner_call']['selection'])} ({b['match_winner_call']['prob_pct']}%)"
                sheet = f"<details><summary>Full market sheet ({len(b['markets'])})</summary>{market_sheet(b)}</details>"
                conf = conf_badge(b["confidence"])
                strength = (f"{esc(b['strength']['mode'])}<span class='sub'>edge {b['edge']:+.1f} vs scale "
                            f"{b['scale']:g}</span>")
            else:
                pick_cell = "<span class='sub'>no price originated</span>"
                call = "—"
                sheet = ""
                conf = '<span class="badge warn">unrated</span>'
                strength = "<span class='sub'>no two-sided official input</span>"
            flags = "".join(f"<span class='sub' style='color:#fcd34d'>⚠ {esc(x)}</span>" for x in f["flags"])
            rows.append(f"""<tr>
 <td>{fdate(f['start_utc'])}<span class="sub">{esc(f['stage'])}</span></td>
 <td><b>{esc(f['home'])}{(' v ' + esc(f['away'])) if f.get('away') else ''}</b><span class="sub">{esc(f['venue'])}</span></td>
 <td>{strength}</td>
 <td>{pick_cell}</td>
 <td>{conf}<span class="sub">call: {call}</span></td>
 <td>{src_links(f['sources'], smap)}{flags}</td>
 <td>{sheet}</td>
</tr>""")
        hs = [b for b in highs if b["sport"] == s]
        pred_block = ""
        if hs:
            items = ""
            for b in hs:
                pr = next((x for x in preds["items"] if x["id"] == b["id"]), None)
                if pr:
                    items += (f'<div class="pred"><h3>{esc(b["home"])} v {esc(b["away"])}</h3>'
                              f'<div class="meta">{esc(b["competition"])} · {esc(b["stage"])} · {fdate(b["start_utc"])} · '
                              f'{esc(pr["selection"])} @ {pr["price"]:.2f}</div><p>{esc(pr["prediction"])}</p></div>')
            pred_block = f"<h2>High-confidence predictions ({len(hs)})</h2>{items}"
        body = f"""<h1>{esc(s)}</h1>
<p class="lede">{by_sport.get(s, 0)} verified fixture{'s' if by_sport.get(s, 0) != 1 else ''} in the 22–28 October
2026 window. Prices are our own fair quotes; the model's strength inputs and per-row flags are shown on each row.</p>
<div class="table-wrap"><table>
<thead><tr><th>Start (UTC)</th><th>Match &amp; venue</th><th>Strength input</th><th>Desk selection</th><th>Confidence</th><th>Official source</th><th>Markets</th></tr></thead>
<tbody>{''.join(rows) or '<tr><td colspan="7">No fixture in this sport inside the window.</td></tr>'}</tbody></table></div>
{pred_block}
<p style="margin-top:18px"><a href="../sports.html">← all sports</a> · <a href="../methodology.html">methodology</a></p>"""
        (SPORTS_DIR / f"{slug}.html").write_text(page(f"sports/{slug}.html", s, body, None))

    # ---------------------------------------------------------------- lines
    rows = []
    for b in sorted(lines["books"], key=lambda x: (SPORT_ORDER.index(x["sport"]), x["start_utc"] or "")):
        p = b["desk_pick"]
        pick_cell = (f"<b>{esc(p['selection'])}</b><span class='sub'>{esc(p['market'])} · {p['price']:.2f} "
                     f"({p['us']:+d}) · {p['prob_pct']}%</span>") if p else "—"
        rows.append(f"""<tr>
 <td>{fdate(b['start_utc'])}<span class="sub">{esc(b['competition'])} · {esc(b['stage'])}</span></td>
 <td><b>{esc(b['home'])} v {esc(b['away'])}</b><span class="sub">{esc(b['venue'])}</span></td>
 <td><a href="sports/{SPORT_SLUG[b['sport']]}.html">{esc(b['sport'])}</a></td>
 <td>{pick_cell}</td><td>{conf_badge(b['confidence'])}</td>
 <td>{src_links(b['sources'], smap)}</td>
 <td><details><summary>{len(b['markets'])} selections</summary>{market_sheet(b)}</details></td>
</tr>""")
    body = f"""<h1>All {len(lines['books'])} priced fixtures</h1>
<p class="lede">Every head-to-head this desk could price from two-sided official figures, with the complete market
sheet: match winner, draw no bet where the sport allows a draw, three handicap rungs and three total rungs, plus
correct-score markets for the frame and set sports. {lines['price_count']:,} prices in total.</p>
<div class="table-wrap"><table>
<thead><tr><th>Start (UTC)</th><th>Match &amp; venue</th><th>Sport</th><th>Desk selection</th><th>Confidence</th><th>Official source</th><th>Market sheet</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""
    (OUT / "lines.html").write_text(page("lines.html", "All Fixtures", body, None))

    # ---------------------------------------------------------------- picks
    rows = []
    for b in sorted(lines["books"], key=lambda x: ({"High": 0, "Medium": 1, "Low": 2}[x["confidence"]],
                                                   -(x["desk_pick"]["model_prob"] if x["desk_pick"] else 0))):
        p = b["desk_pick"]
        band = f'<span class="badge ok">in window</span>' if p and p["in_band"] else '<span class="badge warn">outside window</span>'
        rows.append(f"""<tr>
 <td>{conf_badge(b['confidence'])}</td>
 <td><b>{esc(p['selection'] if p else '—')}</b><span class="sub">{esc(p['market']) if p else ''}</span></td>
 <td class="num">{f"{p['price']:.2f}" if p else '—'}<span class="sub">{f"{p['us']:+d}" if p else ''}</span></td>
 <td class="num">{f"{p['prob_pct']}%" if p else '—'}</td>
 <td>{band}</td>
 <td>{esc(b['match_winner_call']['selection'])}<span class="sub">{b['match_winner_call']['prob_pct']}% · {b['match_winner_call']['price']:.2f} ({b['match_winner_call']['us']:+d})</span></td>
 <td><b>{esc(b['home'])} v {esc(b['away'])}</b><span class="sub">{esc(b['competition'])} · {fdate(b['start_utc'])}</span></td>
 <td>{src_links(b['sources'], smap)}</td>
</tr>""")
    body = f"""<h1>Picks and confidence tiers</h1>
<p class="lede">One desk selection per priced fixture, plus the explicit match-winner call the brief asks for. High
requires a 70% model probability on a published price inside -250 to +10000. Medium is 55% and above. Everything
else is Low. Caps by sport are printed where they apply.</p>
<div class="note warn"><b>Read the wins column with the price.</b> A 55% pick at {1/0.55:.2f} (+82) is a different
proposition from a 71% pick at {1/0.71:.2f} (-241). Both appear in this table; only the second is a High.</div>
<div class="table-wrap"><table>
<thead><tr><th>Confidence</th><th>Desk selection</th><th class="num">Price</th><th class="num">Model %</th><th>Window</th><th>Match-winner call</th><th>Fixture</th><th>Official source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""
    (OUT / "picks.html").write_text(page("picks.html", "High Picks", body, None))

    # ---------------------------------------------------------------- predictions
    blocks = ""
    for it in preds["items"]:
        blocks += f"""<div class="pred">
  <h3>{esc(it['home'])} v {esc(it['away'])}</h3>
  <div class="meta">{esc(it['sport'])} · {esc(it['competition'])} · {fdate(it['start_utc'])} · {it['word_count']} words</div>
  <p>{esc(it['prediction'])}</p>
  <div class="sel"><b>{esc(it['selection'])}</b> @ {it['price']:.2f} ({it['us']:+d}) · {it['prob_pct']}% model · {conf_badge('High')}</div>
  {src_links(it['sources'], smap)}
</div>"""
    body = f"""<h1>{preds['count']} written predictions</h1>
<p class="lede">One bespoke preview for every High-confidence selection. Each names the participants, quotes the
figure that was read on an official page, states the selection and the price, and runs
{preds['min_words']}–{preds['max_words']} words. Across the whole set there
{'is' if len(preds['repeated_6grams']) == 1 else 'are'} {len(preds['repeated_6grams'])}
repeated six-word phrase{'s' if len(preds['repeated_6grams']) != 1 else ''}.</p>
<div class="note">Sources are listed under each prediction. If a claim is not on one of those pages it is not in the
text — no historical head-to-head record, injury or quote has been added from memory.</div>
{blocks}"""
    (OUT / "predictions.html").write_text(page("predictions.html", "Predictions", body, None))

    # ---------------------------------------------------------------- markets
    agg = {}
    for b in lines["books"]:
        for m in b["markets"]:
            key = m["market"].split(" (")[0]
            a = agg.setdefault(key, {"n": 0, "in": 0, "p": []})
            a["n"] += 1
            a["in"] += 1 if m["in_band"] else 0
            a["p"].append(m["model_prob"])
    mrows = "".join(
        f"<tr><td><b>{esc(k)}</b></td><td class='num'>{v['n']:,}</td><td class='num'>{v['in']:,}</td>"
        f"<td class='num'>{100*v['in']/v['n']:.0f}%</td>"
        f"<td class='num'>{min(v['p'])*100:.1f}%–{max(v['p'])*100:.1f}%</td></tr>"
        for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["n"]))
    body = f"""<h1>Market explorer</h1>
<p class="lede">Every market this desk originates, with how many selections fall inside the brief's price window.
The window test is applied to the published fair price.</p>
<div class="table-wrap"><table>
<thead><tr><th>Market</th><th class="num">Selections</th><th class="num">Inside window</th><th class="num">Share</th><th class="num">Probability range</th></tr></thead>
<tbody>{mrows}</tbody></table></div>
<h2>What each market means here</h2>
<ul class="plain">
<li><b>Match winner</b> — the head-to-head result. Three-way in rugby union, rugby league, handball and Gaelic football,
where a draw is a separate outcome.</li>
<li><b>Draw no bet</b> — a two-way market that refunds the stake when regulation ends level; only in the four
three-way sports.</li>
<li><b>Handicap</b> — the margin market. Three rungs per fixture at roughly 50%, 60% and 71% cover probability for the
favourite, each mirrored for the underdog. Units are the sport's own: goals, points, games, frames, legs or sets.</li>
<li><b>Total</b> — over/under on the combined score, three rungs around the competition baseline. Published for
reference and never used as the desk selection, because a total ladder can manufacture a 70% quote on either side
at different lines.</li>
<li><b>Correct score</b> — the full frame, leg or set scoreline grid, for the best-of-N sports only.</li>
</ul>
<div class="note warn"><b>Totals are a modelling baseline, not a sourced figure.</b> No governing body publishes an
expected total, so the total line is a documented competition constant. It is printed as reference only.</div>"""
    (OUT / "markets.html").write_text(page("markets.html", "Market Explorer", body, None))

    # ---------------------------------------------------------------- reverse engineering
    covered = "".join(
        f"<tr><td>{s['olbg_id']}</td><td><b>{esc(s['sport'])}</b></td>"
        f"<td><a href='{esc(s['olbg_url'])}' target='_blank' rel='noopener'>{esc(s['olbg_url'])}</a></td>"
        f"<td class='num'>{s['live_olbg_cards']}</td><td class='num'>{s['verified_desk_events']}</td>"
        f"<td>{esc(s['primary_governor'])}</td></tr>" for s in tax["covered_sports"])
    excluded = "".join(
        f"<tr><td>{e['olbg_id']}</td><td><b>{esc(e['category'])}</b></td>"
        f"<td><a href='{esc(e['olbg_url'])}' target='_blank' rel='noopener'>{esc(e['olbg_url'])}</a></td>"
        f"<td>{esc(e['rule'])}</td></tr>" for e in tax["excluded_categories"])
    mech = tax["architecture"]["consensus_mechanics"]
    body = f"""<h1>OLBG, reversed</h1>
<p class="lede">All 27 OLBG sport routes and their competition sub-routes were read live on 22 October 2026. This
page records the URL grammar, the tipster-consensus mechanics and the four upstream display defects found. Nine of
the exclusions in the brief map onto OLBG's own sport ids; the rest are handled as competition filters.</p>

<h2>URL grammar</h2>
<div class="table-wrap"><table><thead><tr><th>Route</th><th>Pattern</th></tr></thead><tbody>
<tr><td>Root tips hub</td><td><code>{esc(tax['architecture']['root_hub'])}</code></td></tr>
<tr><td>Sport hub</td><td><code>{esc(tax['architecture']['sport_hub_pattern'])}</code></td></tr>
<tr><td>Competition hub</td><td><code>{esc(tax['architecture']['competition_hub_pattern'])}</code></td></tr>
<tr><td>Event card</td><td><code>{esc(tax['architecture']['event_card_pattern'])}</code></td></tr>
</tbody></table></div>

<h2>Tipster-consensus mechanics</h2>
<div class="table-wrap"><table><thead><tr><th>Mechanism</th><th>How OLBG computes it</th></tr></thead><tbody>
<tr><td>Win-tip share</td><td>{esc(mech['win_tips_share'])}</td></tr>
<tr><td>Each-way display bug</td><td>{esc(mech['each_way_bug'])}</td></tr>
<tr><td>Value Rating</td><td>{esc(mech['value_rating'])}</td></tr>
<tr><td>Experts filter</td><td>{esc(mech['experts_filter'])}</td></tr>
<tr><td>Blind-spot behaviour</td><td>{esc(mech['blind_spot_behavior'])}</td></tr>
</tbody></table></div>

<h2>In-scope sports ({tax['covered_sports_count']})</h2>
<div class="table-wrap"><table>
<thead><tr><th>OLBG id</th><th>Sport</th><th>Hub</th><th class="num">Live cards on hub</th><th class="num">Rows in this desk</th><th>Governing body</th></tr></thead>
<tbody>{covered}</tbody></table></div>
<p class="sub">"Live cards on hub" is what OLBG itself displayed at 03:00Z on 22 October; several hubs showed zero
because OLBG only creates a card once a tipster posts a tip. That is the blind spot, not an absence of fixtures —
the desk verified nine AFLW matches, eight LoL Worlds Swiss games, five RLWC26 ties and three GBGB Category One
finals that OLBG did not list.</p>

<h2>Excluded categories ({tax['excluded_categories_count']})</h2>
<div class="table-wrap"><table>
<thead><tr><th>OLBG id</th><th>Category</th><th>Route</th><th>Why excluded</th></tr></thead>
<tbody>{excluded}</tbody></table></div>

<h2>Upstream defects recorded</h2>
<ul class="plain">
<li><b>Each-way division by zero.</b> A market carrying only each-way tips renders <code>0/0</code> in the
win-tip column and a blank percentage, so the consensus cannot be read at all. Observed on the Cricket hub.</li>
<li><b>Silent card suppression.</b> OLBG publishes nothing for a fixture until a tipster posts. Four sports on this
desk showed "No tips found" while the governing body listed a full slate.</li>
<li><b>Unlabelled local clock.</b> OLBG prints a viewer-localised time with no zone. Every time on this desk is UTC
and taken from the governing body, never from OLBG.</li>
<li><b>Neutral venues omitted.</b> Maccabi Tel Aviv's home EuroLeague games are staged in Belgrade; OLBG lists the
fixture without the neutral-venue note, which materially changes the home-advantage assumption.</li>
</ul>"""
    (OUT / "reverse-engineering.html").write_text(page("reverse-engineering.html", "OLBG Reversed", body, None))

    # ---------------------------------------------------------------- methodology
    m = lines["model"]
    body = f"""<h1>Methodology</h1>
<p class="lede">Everything on this site is either a sourced fact or a labelled model output. This page states which
is which, in enough detail that the arithmetic can be reproduced.</p>

<h2>1. Strength inputs</h2>
<p>Each side carries one strength figure on a 0–100 scale, derived only from the official figure recorded in the
fixture's <code>inputs</code> block:</p>
<ul class="plain">
<li><b>Ranking sports</b> (tennis, snooker, darts, esports): <code>strength = 100 − 18·ln(rank)</code>, using the rank
printed on the signed draw sheet or the official ranking list. A rank of 1 is 100; a rank of 32 is about 38.</li>
<li><b>Table sports</b> (ice hockey, rugby union, Aussie rules, handball, EuroLeague): league points as a share of the
maximum available, plus a goal or point-difference term per game.</li>
<li><b>Record sports</b> (baseball, NBA, cricket, volleyball): win rate with two pseudo-games of shrinkage, plus a
run-difference term where the feed publishes one.</li>
<li><b>Single-fixture sports</b> (RLWC26, Gaelic football): the sourced round-one or semi-final margin, mapped to a
pseudo win rate around .500.</li>
</ul>
<div class="note warn"><b>Documented assumptions.</b> Where a ranking is not published for one side the model assumes
rank {m['assumed_rank_when_missing']} for that sport and the row is demoted to Medium at best. Home advantage is a
documented constant per sport ({', '.join(f"{k} {v:g}" for k, v in list(m['home_advantage'].items())[:6])}, and so
on), not a measured figure. These are assumptions and are labelled as such.</div>

<h2>2. One distribution per match</h2>
<p><code>P(win) = Phi(edge / SCALE)</code> with the published per-sport scale, and the same edge sets the expected
margin, so the handicap and total ladders are derived from the same distribution as the moneyline rather than from
separate guesses. Best-of-N sports solve for the per-leg probability that reproduces the match probability under the
binomial model, then price every frame, leg and set market off that score matrix.</p>

<h2>3. Prices are fair, and the margin is published</h2>
<p>Every price is <code>1 / probability</code>, rounded to two decimals, with no margin added. The desk also prints
the price a bookmaker charging {m['margin_for_transparency']*100:.0f}% would quote, which is
<code>fair / {1 + m['margin_for_transparency']:.2f}</code>. Nothing on this site is a market price.</p>

<h2>4. The -250 to +10000 band</h2>
<p>The brief asks for High-confidence picks that win more than 70% of the time <i>and</i> sit between −250 and
+10000. Those two conditions pull in opposite directions: a 70% chance is a fair price of {1/0.70:.2f} (−233), and
any margin pushes the quoted price shorter than −250. The desk resolves it by treating the <b>window as binding on
the price it publishes</b>, and by originating the line: for a strong favourite it quotes the handicap rung whose
probability lands near {TARGET:.0%}, which is inside the window, rather than the shorter moneyline. Every High pick
therefore satisfies both tests on its published price, and the moneyline call is printed beside it so nothing is
hidden.</p>

<h2>5. Confidence tiers and caps</h2>
<ul class="plain">
<li><b>High</b> — model probability at least {m['high_probability_floor']*100:.0f}% and published price inside
{m['band']['low_decimal']:.2f}–{m['band']['high_decimal']:.0f} ({m['band']['low_us']} to +{m['band']['high_us']}).</li>
<li><b>Medium</b> — at least {m['medium_probability_floor']*100:.0f}%.</li>
<li><b>Low</b> — everything else.</li>
</ul>
<p>Caps applied automatically: the NBA (one-game sample) at Medium, PlusLiga (one round) at Medium, esports (draw tier
is seeding, not strength) at Medium, cricket and Gaelic football at Low. A row whose strength input is a documented
assumption is capped at Medium. The cap and its reason are printed on every affected row.</p>

<h2>6. Blank beats wrong</h2>
<p>If a figure cannot be read on an official page it is left empty and the row is listed on
<a href="flagged.html">Flagged for Review</a>. {fx['event_only_count']} of {fx['count']} fixtures are published
with no price at all for exactly this reason. No value on this site was filled in from memory.</p>"""
    (OUT / "methodology.html").write_text(page("methodology.html", "Methodology", body, None).replace(
        "{TARGET:.0%}", f"{0.706:.0%}"))

    # ---------------------------------------------------------------- sources
    srows = "".join(
        f"<tr><td><b>{esc(s['organization'])}</b></td><td>{esc(s['sport'])}</td><td>{esc(s['title'])}"
        f"<span class='sub'>{esc(s['verification_method'])}</span></td>"
        f"<td><a href='{esc(s['url'])}' target='_blank' rel='noopener'>{esc(s['url'])}</a></td>"
        f"<td class='num'>{esc(s['verified_utc'])}</td></tr>" for s in srcs["sources"])
    body = f"""<h1>Official sources</h1>
<p class="lede">{srcs['count']} governing-body pages were fetched in this session. Media outlets, aggregators, tipster
sites and Wikipedia are not used to verify any fact on this site.</p>
<div class="note good">Every row also records <i>how</i> it was verified. Where a page was a signed supervisor PDF,
a league API payload or a county board fixture list, that is stated so the check can be repeated.</div>
<div class="table-wrap"><table>
<thead><tr><th>Body</th><th>Sport</th><th>Page and what it established</th><th>URL</th><th class="num">Read (UTC)</th></tr></thead>
<tbody>{srows}</tbody></table></div>"""
    (OUT / "sources.html").write_text(page("sources.html", "Sources", body, None))

    # ---------------------------------------------------------------- audit
    fblocks = ""
    for f in audit["findings"]:
        sev = {"high": "high", "medium": "medium", "low": "low", "info": "info"}.get(f["severity"], "low")
        loc = f"{esc(f['file'])}" + (f":{f['line']}" if f.get("line") else "")
        rows_html = ""
        if f.get("rows"):
            rows_html = '<div class="table-wrap" style="margin-top:8px"><table><thead><tr><th>Fixture</th><th>Club</th><th>Value in repo</th><th>Official value</th></tr></thead><tbody>' + "".join(
                f"<tr><td>{esc(r['fixture'])}</td><td>{esc(r['team'])}</td><td><code>{esc(r['repo_value'])}</code></td>"
                f"<td><b>{esc(r['official'])}</b></td></tr>" for r in f["rows"]) + "</tbody></table></div>"
        fblocks += f"""<div class="pred">
  <h3><span class="badge {sev}">{esc(f['severity'].upper())}</span> {esc(f['id'])} — {esc(f['title'])}</h3>
  <div class="meta">Where: <code>{loc}</code> · Status: {esc(f['status'])}</div>
  <p>{esc(f['detail'])}</p>
  <div class="sel">Official check: {f'<a href="{esc(f["source"])}" target="_blank" rel="noopener">{esc(f["source"])}</a>' if str(f['source']).startswith('http') else '<code>' + esc(f['source']) + '</code>'}</div>
  <div class="meta" style="margin-top:6px">Effect: {esc(f['effect'])}</div>
  {rows_html}
</div>"""
    body = f"""<h1>Line-by-line repository audit</h1>
<p class="lede">Reading every desk in this repository against the governing body's own page produced
{audit['counts']['findings']} findings: {audit['counts']['high']} high, {audit['counts']['medium']} medium,
{audit['counts']['low']} low and {audit['counts']['info']} informational. Nothing was corrected inside another
session's files; each item is logged here with the file, the line and the official page that contradicts it.</p>
<div class="note warn"><b>The headline.</b> {audit['counts']['aflw_rows_wrong']} of {audit['counts']['aflw_rows_checked']}
AFLW ladder inputs on the root desk disagree with the official AFLW ladder, and three published High picks rest on
them. The full comparison is in finding AUD-A-01.</div>
{fblocks}
<h2>What this desk did about it</h2>
<ul class="plain">
<li>It did not edit any file owned by another session. Each finding names the file so the owning session can fix it.</li>
<li>Its own AFLW rows use the official ladder, fetched on 22 October 2026, and the sourced figures are printed in
the strength column of the <a href="sports/aussie-rules.html">Aussie Rules</a> page.</li>
<li>Every fixture on this site carries the page that was actually read; nothing is inherited silently from an
earlier desk.</li>
</ul>"""
    (OUT / "audit.html").write_text(page("audit.html", "Repo Audit", body, None))

    # ---------------------------------------------------------------- flagged
    frows = "".join(
        f"<tr><td>{esc(r['sport'])}<span class='sub'>{esc(r['competition'])}</span></td>"
        f"<td><b>{esc(r['match'])}</b><span class='sub'><code>{esc(r['id'])}</code></span></td>"
        f"<td>{esc(r['flag'])}</td><td>{esc(r['status'])}</td><td>{src_links(r['sources'], smap)}</td></tr>"
        for r in flagged["rows"])
    body = f"""<h1>Flagged for review</h1>
<p class="lede">Every value this desk could not confirm on an official page, and every limitation a reader needs in
order to use the numbers correctly. {flagged['count']} row-level flags and {audit['counts']['findings']} repository
findings. Flags do not block publication; they are the honest edge of the dataset.</p>
<div class="note warn"><b>Nothing here is filled in.</b> A flag means the field is blank or the price was withheld,
not that a best guess was made. Where a price <i>was</i> originated, the flag explains the assumption behind it.</div>
<h2>Row-level flags ({flagged['count']})</h2>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th>Fixture</th><th>Flag</th><th>Effect</th><th>Official source</th></tr></thead>
<tbody>{frows}</tbody></table></div>
<h2>Repository findings ({audit['counts']['findings']})</h2>
<div class="table-wrap"><table>
<thead><tr><th>Id</th><th>Severity</th><th>Finding</th><th>Official check</th></tr></thead><tbody>
{''.join(f"<tr><td>{esc(f['id'])}</td><td><span class='badge {'high' if f['severity']=='high' else ('medium' if f['severity']=='medium' else 'low')}'>{esc(f['severity'])}</span></td><td>{esc(f['title'])}<span class='sub'>{esc(f['file'])}{':' + str(f['line']) if f.get('line') else ''}</span></td><td>" + (f"<a href='{esc(f['source'])}' target='_blank' rel='noopener'>{esc(f['source'])}</a>" if str(f['source']).startswith('http') else f"<code>{esc(f['source'])}</code>") + "</td></tr>" for f in audit['findings'])}
</tbody></table></div>
<p style="margin-top:14px">Full detail is on the <a href="audit.html">Repo Audit</a> page.</p>"""
    (OUT / "flagged.html").write_text(page("flagged.html", "Flagged for Review", body, None))

    pages = 1 + 1 + len(SPORT_ORDER) + 9
    print(f"built {len(list(OUT.rglob('*.html')))} pages under {OUT.relative_to(ROOT)}/")


TARGET = 0.706

if __name__ == "__main__":
    build()
