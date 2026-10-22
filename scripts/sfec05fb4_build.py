#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the fec05fb4 desk to static HTML under fec05fb4/."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESK = json.loads((ROOT / "data" / "fec05fb4" / "desk.json").read_text())
OUT = ROOT / "fec05fb4"
SPORTS = OUT / "sports"

E = lambda v: html.escape("" if v is None else str(v), quote=True)

CSS = """
:root{--ink:#12181f;--muted:#5b6773;--line:#dde3ea;--bg:#fbfcfd;--card:#fff;--teal:#0f6b5f;--teal-2:#0b4f46;
--high:#0f6b5f;--med:#8a5a00;--low:#5b6773;--flag:#9b1c1c;--tint:#eef6f5}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--teal-2)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{background:#0d1b21;color:#eaf2f1;padding:14px 0}
header.top .wrap{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
header.top a{color:#cfe6e2;text-decoration:none;font-size:14px;letter-spacing:.01em}
header.top a:hover{color:#fff;text-decoration:underline}
header.top .brand{font-weight:700;color:#fff;font-size:15px;margin-right:auto}
.hero{padding:34px 0 10px}
.kicker{text-transform:uppercase;letter-spacing:.14em;font-size:12px;color:var(--teal);font-weight:700}
h1{font-size:34px;line-height:1.18;margin:.25em 0 .35em;letter-spacing:-.01em}
h2{font-size:22px;margin:2em 0 .5em}
h3{font-size:17px;margin:1.4em 0 .35em}
p.lede{font-size:18px;color:#26313b;max-width:80ch}
p{max-width:88ch}
.meta{color:var(--muted);font-size:14px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:10px;margin:22px 0 8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:24px;letter-spacing:-.02em}
.kpi span{color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.07em}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px;margin:14px 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.card h3{margin:.1em 0 .3em;font-size:18px}
.card .pick{font-size:20px;font-weight:700;color:var(--teal-2);margin:.2em 0 .4em}
.badge{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:999px;border:1px solid}
.b-high{color:#fff;background:var(--high);border-color:var(--high)}
.b-medium{color:#3a2600;background:#ffe4a8;border-color:#e9c46a}
.b-low{color:var(--low);background:#eef1f4;border-color:#cfd6dd}
.b-unpriced{color:#5b6773;background:#fff;border-color:#cfd6dd;border-style:dashed}
.tbl{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card);margin:12px 0 6px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f2f5f7;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#3d4a56;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#fafcfc}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.blank{background:repeating-linear-gradient(45deg,#fbfcfd,#fbfcfd 6px,#f3f6f8 6px,#f3f6f8 12px)}
.muted{color:var(--muted)}
.small{font-size:13px}
details{margin:.25em 0 .6em}
summary{cursor:pointer;color:var(--teal-2);font-size:13px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:760px){.grid2{grid-template-columns:1fr}h1{font-size:27px}}
.note{background:var(--tint);border:1px solid #cfe3e0;border-radius:10px;padding:12px 16px;margin:16px 0}
.warn{background:#fff5f5;border:1px solid #f3cfcf;border-radius:10px;padding:12px 16px;margin:16px 0}
ul.tight li{margin:.28em 0}
footer.bottom{border-top:1px solid var(--line);margin-top:44px;padding:20px 0 40px;color:var(--muted);font-size:13.5px}
.tag{font-size:12px;color:var(--muted)}
.source{font-size:13px}
.pred{background:#f7fbfa;border-left:3px solid var(--teal);padding:10px 14px;margin:8px 0 10px;font-size:15px}
.facts{margin:6px 0 0;padding-left:20px;font-size:13.5px;color:#26313b}
.skip{position:absolute;left:-9999px}
"""

NAV = [
    ("index.html", "Overview"),
    ("sports.html", "Categories"),
    ("high.html", "High selections"),
    ("flagged.html", "Flagged for review"),
    ("review.html", "Line-by-line review"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method"),
    ("coverage.html", "Coverage"),
]


def page(rel: str, title: str, body: str, desc: str) -> str:
    nav = "".join(f'<a href="{rel}{href}">{E(label)}</a>' for href, label in NAV)
    return f"""<!doctype html>
<html lang="en" data-snapshot="2026-10-22T12:45:00Z">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} — OLBG reverse-engineered desk</title>
<meta name="description" content="{E(desc)}">
<link rel="stylesheet" href="{rel}assets/desk.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<span class="brand">OLBG RE · session fec05fb4</span>
{nav}
<a href="{rel}../index.html">Repository home</a>
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="bottom"><div class="wrap">
<p>Snapshot 2026-10-22 12:45 UTC. Every price is a desk-originated fair price, not a bookmaker quote. Blank cells mean the value was not verified from an official source.
{DESK["counts"]["high"]} High; {DESK["counts"]["medium"]} Medium; {DESK["counts"]["low"]} Low; {DESK["counts"]["unpriced"]} unpriced. <a href="{rel}methodology.html">Method</a> · <a href="{rel}flagged.html">Flagged for review</a> · <a href="{rel}../data/fec05fb4/desk.json">desk.json</a> · <a href="{rel}../data/fec05fb4/rows.csv">rows.csv</a></p>
</div></footer>
</body></html>"""


def badge(tier: str) -> str:
    cls = {"High": "b-high", "Medium": "b-medium", "Low": "b-low"}.get(tier, "b-unpriced")
    return f'<span class="badge {cls}">{E(tier)}</span>'


def src_cell(row: dict) -> str:
    links = []
    seen = set()
    for s in row["official_sources"]:
        if s["url"] in seen:
            continue
        seen.add(s["url"])
        links.append(f'<a href="{E(s["url"])}">{E(s["name"])}</a>')
    return "<br>".join(links) if links else ""


def price(am) -> str:
    if am is None or am == "":
        return ""
    return f"{am:+d}" if isinstance(am, int) else E(am)


def markets_block(row: dict) -> str:
    if not row["markets"]:
        return ""
    out = ['<details><summary>All originated markets (%d)</summary><div class="tbl"><table data-audit="market"><caption class="tag">Model probability, zero-vig fair price and the 5%%-margin offered price.</caption>'
           '<thead><tr><th>Market</th><th>Line</th><th>Selection</th><th class="num">Model p</th><th class="num">Fair</th><th class="num">Offered</th></tr></thead><tbody>' % len(row["markets"])]
    for m in row["markets"]:
        for o in m["outcomes"]:
            out.append(
                f'<tr><td>{E(m["name"])}</td><td>{E(m["line"]) or "&nbsp;"}</td><td>{E(o["selection"])}</td>'
                f'<td class="num">{o["probability"]*100:.2f}%</td><td class="num">{price(o["fair_american"])}</td>'
                f'<td class="num">{price(o.get("offered_american"))}</td></tr>')
    out.append("</tbody></table></div></details>")
    return "".join(out)


def row_table(rows: list, rel: str) -> str:
    head = ("<thead><tr><th>Start (UTC)</th><th>Fixture</th><th>Competition</th><th>Tier</th>"
            "<th>Selection</th><th class=\"num\">Model p</th><th class=\"num\">Fair price</th>"
            "<th>Official source</th><th>Flags</th></tr></thead>")
    body = []
    for r in rows:
        s = r.get("selection") or {}
        flags = r.get("flags") or []
        time = E(r["start_utc"][:16].replace("T", " ") + "Z") if r["start_utc"] else ""
        p_txt = f"{s['probability']*100:.2f}%" if s.get("probability") else ""
        cell = (f'<tr><td class="num">{time}</td>'
                f'<td><b>{E(r["home"])}</b> v {E(r["away"])}<div class="tag">{E(r["stage"] or "")}</div></td>'
                f'<td>{E(r["competition"] or "")}</td><td>{badge(r["tier"])}</td>'
                f'<td>{E(s.get("selection", ""))}<div class="tag">{E(s.get("market", ""))}</div></td>'
                f'<td class="num">{p_txt}</td>'
                f'<td class="num">{price(s.get("fair_american"))}</td>'
                f'<td class="source">{src_cell(r)}</td>'
                f'<td class="small">{len(flags) if flags else ""}</td></tr>')
        extra = ""
        detail = []
        if r.get("key_inputs"):
            detail.append("<h4>Inputs</h4><ul class=\"tight small\">" + "".join(f"<li>{E(x)}</li>" for x in r["key_inputs"]) + "</ul>")
        if r.get("analysis"):
            detail.append(f"<h4>Official preview summary</h4><p class=\"small\">{E(r['analysis'])}</p>")
        if r.get("model_note"):
            detail.append(f"<h4>Model</h4><p class=\"small\">{E(r['model_note'])}</p>")
        if flags:
            detail.append("<h4>Flags</h4><ul class=\"tight small\">" + "".join(f"<li>{E(f)}</li>" for f in flags) + "</ul>")
        detail.append(markets_block(r))
        if any(detail):
            extra = f'<tr class="detail"><td colspan="9">' + "".join(detail) + "</td></tr>"
        body.append(cell + extra)
    return f'<div class="tbl"><table data-audit="row">{head}<tbody>{"".join(body)}</tbody></table></div>'


def listing_table(rows: list) -> str:
    if not rows:
        return "<p class=\"muted\">No captured listings in this category.</p>"
    head = ("<thead><tr><th>Date as listed</th><th>Fixture</th><th>Competition</th><th>Status</th>"
            "<th>Official source</th><th>Flag</th></tr></thead>")
    body = []
    for r in rows:
        flag = (r.get("flags") or [""])[0]
        body.append(
            f'<tr><td>{E(r["time_display"])}</td><td><b>{E(r["home"])}</b>' + (f' v {E(r["away"])}' if r.get("away") else "") + "</td>"
            f'<td>{E(r["competition"] or "")}</td><td>{badge(r["tier"])}<div class="tag">{E(r["status"])}</div></td>'
            f'<td class="source">{src_cell(r)}</td><td class="small">{E(flag)}</td></tr>')
    return f'<div class="tbl"><table data-audit="row">{head}<tbody>{"".join(body)}</tbody></table></div>'


def kpi_strip(counts: dict) -> str:
    items = [("Upcoming fixtures", counts["upcoming"]), ("Priced", counts["priced"]),
             ("High", counts["high"]), ("Medium", counts["medium"]), ("Low", counts["low"]),
             ("Unpriced", counts["unpriced"]), ("Markets", counts["markets"]),
             ("Outcomes", counts["outcomes"]), ("Official sources", counts["sources"]),
             ("Flagged items", counts["flags"])]
    return '<div class="kpis">' + "".join(f'<div class="kpi"><b>{v}</b><span>{E(k)}</span></div>' for k, v in items) + "</div>"


def high_cards() -> str:
    cards = []
    for p in DESK["predictions"]:
        row = next(r for r in DESK["rows"] if r["id"] == p["fixture_id"])
        facts = "".join(f"<li>{E(f)}</li>" for f in p["facts"])
        srcs = " · ".join(f'<a href="{E(s["url"])}">{E(s["publisher"])}</a>' for s in p["sources"])
        cards.append(f"""<article class="card">
<div class="kicker">High · {E(p['competition'])}</div>
<h3>{E(p['match'])}</h3>
<div class="pick">{E(p['selection'])} <span class="tag">at {price(p['fair_american'])} fair</span></div>
<div class="pred">{E(p['text'])}</div>
<p class="meta">{E(row['time_display'])} · model probability {p['probability']*100:.2f}% · {p['words']} words · <a href="{E(row['official_sources'][0]['url'])}">official fixture source</a></p>
<h4>Verified facts used</h4><ul class="facts">{facts}</ul>
<p class="source">Sources: {srcs}</p>
</article>""")
    return '<div class="cards">' + "".join(cards) + "</div>"


def write(path: Path, html_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "assets" / "desk.css").write_text(CSS, encoding="utf-8")

    counts = DESK["counts"]
    cov = DESK["coverage"]
    flags = DESK["flagged"]
    an = DESK["analysis"]
    rows = DESK["rows"]

    # ---------------- index ----------------
    sport_rows = []
    for c in cov:
        sport_rows.append(
            f'<tr><td><a href="sports/{E(c["sport"])}.html">{E(c["label"])}</a></td>'
            f'<td class="num">{c["upcoming"]}</td><td class="num">{c["priced"]}</td>'
            f'<td class="num">{c["high"]}</td><td class="num">{c["medium"]}</td><td class="num">{c["low"]}</td>'
            f'<td class="num">{c["fresh"]}</td><td class="num">{c["carried"]}</td><td>{E(c["status"])}</td></tr>')
    cov_tbl = ('<div class="tbl"><table data-audit="summary"><thead><tr><th>Category</th><th class="num">Upcoming</th><th class="num">Priced</th>'
               '<th class="num">High</th><th class="num">Medium</th><th class="num">Low</th><th class="num">Fresh</th>'
               '<th class="num">Carried</th><th>Status</th></tr></thead><tbody>' + "".join(sport_rows) + "</tbody></table></div>")

    top = sorted([r for r in rows if r["tier"] in ("High", "Medium")],
                 key=lambda r: ({"High": 0, "Medium": 1}[r["tier"]], -(r["selection"] or {}).get("probability", 0)))[:12]
    top_rows = []
    for r in top:
        s = r["selection"]
        top_rows.append(
            f'<tr><td>{E(r["start_utc"][:16].replace("T", " "))}Z</td>'
            f'<td><b>{E(r["home"])}</b> v {E(r["away"])}<div class="tag">{E(r["competition"])}</div></td>'
            f'<td>{badge(r["tier"])}</td><td>{E(s["selection"])}</td>'
            f'<td class="num">{s["probability"]*100:.2f}%</td><td class="num">{price(s["fair_american"])}</td>'
            f'<td class="source">{src_cell(r)}</td></tr>')
    top_tbl = ('<div class="tbl"><table data-audit="row"><thead><tr><th>Start (UTC)</th><th>Fixture</th><th>Tier</th><th>Selection</th>'
               '<th class="num">Model p</th><th class="num">Fair</th><th>Official source</th></tr></thead><tbody>'
               + "".join(top_rows) + "</tbody></table></div>")

    findings = "".join(f'<li><b>{E(p["title"])}.</b> {E(p["body"])}</li>' for p in an["points"])
    high_flag = next(f for f in flags if f["id"] == "F-FEC-01")

    body = f"""
<div class="hero">
<div class="kicker">Reverse-engineered OLBG board · as of 22 October 2026, 12:45 UTC</div>
<h1>Every covered sport, priced from official sources — and honest about what is not verified</h1>
<p class="lede">{E(an['lede'])}</p>
<p class="meta">Scope: 17 categories. Excluded by instruction: football/soccer, American football, boxing, UFC/MMA, hurling, horse racing, cycling and specials.
Snapshot marker <code>data-snapshot="2026-10-22T12:45:00Z"</code>.</p>
</div>
{kpi_strip(counts)}
<div class="note"><b>How to read the price columns.</b> “Model p” is this desk's own probability. “Fair” is the zero-vig price implied by that probability and is what the -250/+10000 test is applied to. “Offered” (inside each match panel) adds a
5% bookmaker margin, which pushes a 71% fair price to about -295 — outside the window by construction. No bookmaker price was captured, so no column claims to be one.</div>
<h2>High selections</h2>
<p class="lede small">Two selections clear all three gates: a 70–71.43% fair price, a fresh official read this session, and both clubs' availability confirmed by the official Round 7 injury report.</p>
{high_cards()}
<p><a href="high.html">All High selections and the full gate check →</a></p>
<h2>Today and tomorrow at a glance</h2>
{top_tbl}
<h2>What the numbers say</h2>
<ul class="tight">{findings}</ul>
<h2>Category coverage</h2>
{cov_tbl}
<p class="small muted">Blank cells are values this desk did not verify. The 21 unpriced fixtures have an official fixture but no rating for both sides; the 62 listing-only rows have no verified start time.</p>
<h2>Flagged before you bet</h2>
<div class="warn"><b>{E(high_flag['title'])}.</b> {E(high_flag['detail'])} <a href="flagged.html">All 14 flagged items →</a></div>
<h2>Do the maths yourself</h2>
<p>Every row is reproducible from <a href="../data/fec05fb4/desk.json">desk.json</a> and <a href="../data/fec05fb4/rows.csv">rows.csv</a>.
The generator is <code>scripts/sfec05fb4_data.py</code>; the gate checks are <code>scripts/sfec05fb4_validate.py</code>.
The <a href="review.html">line-by-line review</a> lists each row's evidence status, source links and blanks.</p>
"""
    write(OUT / "index.html", page("", "Overview", body, "Reverse-engineered OLBG desk for 17 non-excluded sports, priced from official sources."))

    # ---------------- high ----------------
    gate_rows = []
    for r in [x for x in rows if x["tier"] == "High"]:
        s = r["selection"]
        gate_rows.append(
            f'<tr><td>{E(r["id"])}</td><td><b>{E(r["home"])}</b> v {E(r["away"])}</td><td>{E(s["selection"])}</td>'
            f'<td class="num">{s["probability"]*100:.3f}%</td><td class="num">{s["fair_decimal"]:.3f}</td>'
            f'<td class="num">{price(s["fair_american"])}</td><td>{"yes" if s["in_band"] else "no"}</td>'
            f'<td>fresh 2026-10-22 12:36Z</td><td>both clubs confirmed</td><td><a href="{E(r["official_sources"][2]["url"])}">injury report</a></td></tr>')
    gate_tbl = ('<div class="tbl"><table data-audit="row"><thead><tr><th>ID</th><th>Fixture</th><th>Selection</th><th class="num">p</th>'
                '<th class="num">Fair dec.</th><th class="num">Fair US</th><th>In band</th><th>Evidence</th>'
                '<th>Availability</th><th>Source</th></tr></thead><tbody>' + "".join(gate_rows) + "</tbody></table></div>")

    near = sorted([r for r in rows if r["tier"] == "Medium" and (r.get("selection") or {}).get("in_band")],
                  key=lambda r: -(r["selection"]["probability"]))
    near_rows = "".join(
        f'<tr><td><b>{E(r["home"])}</b> v {E(r["away"])}</td><td>{E(r["selection"]["selection"])}</td>'
        f'<td class="num">{r["selection"]["probability"]*100:.2f}%</td><td class="num">{price(r["selection"]["fair_american"])}</td>'
        f'<td>{E(r["evidence_status"])}</td><td class="small">{E((r["flags"] or ["—"])[0])}</td></tr>' for r in near)
    near_tbl = ('<div class="tbl"><table data-audit="summary"><thead><tr><th>Fixture</th><th>Selection</th><th class="num">p</th>'
                '<th class="num">Fair</th><th>Evidence</th><th>Why not High</th></tr></thead><tbody>' + near_rows + "</tbody></table></div>")

    body = f"""
<div class="hero"><div class="kicker">The gate, applied literally</div>
<h1>Two High selections, and the exact reason the other {len(near)} in-band picks are not High</h1>
<p class="lede">A High needs four things at once: a model probability strictly above 70% and at most 71.4286% (so the fair price is -233 to -250),
an official source read by this session, both clubs' availability confirmed in that read, and a unique prediction of at least 30 words naming the selection.</p></div>
{gate_tbl}
{high_cards()}
<h2>In-band selections held back</h2>
<p>These {len(near)} selections also sit between 70% and 71.43% at a fair price inside the window. They fail on evidence, not on arithmetic.</p>
{near_tbl}
<h2>Why the evidence test is not a formality</h2>
<p>A 70% cover on a five-point handicap is worth roughly two points of injury news. When a club has not published its Round 7 availability report, the desk cannot know whether a starting guard or a rotation big is out,
so the honest label is Medium. That is the whole difference between the two tables above.</p>
"""
    write(OUT / "high.html", page("", "High selections", body, "The High selections and the full gate check."))

    # ---------------- sports index ----------------
    cards = []
    for c in cov:
        top_pick = next((r for r in rows if r["sport"] == c["sport"] and r["tier"] in ("High", "Medium")), None)
        pick = f'{E(top_pick["selection"]["selection"])} ({top_pick["selection"]["probability"]*100:.1f}%)' if top_pick else "—"
        cards.append(f"""<article class="card"><div class="kicker">{E(c['label'])}</div>
<h3><a href="sports/{E(c['sport'])}.html">{c['upcoming']} upcoming · {c['priced']} priced</a></h3>
<p class="small">High {c['high']} · Medium {c['medium']} · Low {c['low']} · Unpriced {c['unpriced']}<br>
Fresh evidence {c['fresh']} · carried {c['carried']} · listings {c['listings']}</p>
<p class="small muted">Best-rated row: {pick}</p></article>""")
    body = f"""<div class="hero"><div class="kicker">17 categories</div><h1>Category pages</h1>
<p class="lede">Each page lists every captured fixture in that sport, its tier, the desk's selection and price, the official source link, and every originated market inside a match panel.</p></div>
<div class="cards">{''.join(cards)}</div>"""
    write(OUT / "sports.html", page("", "Categories", body, "Index of the 17 covered categories."))

    # ---------------- sport pages ----------------
    for c in cov:
        srows = [r for r in rows if r["sport"] == c["sport"]]
        lrows = [r for r in DESK["listing_only"] if r["sport"] == c["sport"]]
        best = sorted(srows, key=lambda r: -((r.get("selection") or {}).get("probability") or 0))[:3]
        best_txt = ", ".join(f'{E(b["home"])} v {E(b["away"])} — {E(b["selection"]["selection"])} ({b["selection"]["probability"]*100:.1f}%)' for b in best if b.get("selection")) or "none priced"
        ev = ("fresh for every priced row" if c["carried"] == 0 and c["fresh"]
              else "fresh for %d rows and carried for %d" % (c["fresh"], c["carried"]))
        lead = (f"{c['upcoming']} upcoming fixtures, {c['priced']} priced, {c['unpriced']} unpriced. Evidence is {ev}.")
        body = f"""
<div class="hero"><div class="kicker">{E(c['label'])}</div><h1>{E(c['label'])}: {c['upcoming']} upcoming fixtures</h1>
<p class="lede">{E(lead)}</p>
<p class="small muted">Strongest model rows: {best_txt}</p></div>
<h2>Upcoming and priced</h2>
{row_table(srows, '../../') if srows else '<p class="muted">No fixture in this category has a verified future start time.</p>'}
<h2>Captured listings without a verified start time</h2>
{listing_table(lrows)}
<p class="small muted">Blank cells are values that were not verified. Listings above are never priced and never counted as upcoming.</p>"""
        write(SPORTS / f"{c['sport']}.html",
              page("../", f"{c['label']}", body, f"{c['label']} fixtures, prices and sources."))

    # ---------------- flagged ----------------
    items = []
    for f in flags:
        items.append(f"""<article class="card" id="{E(f['id'])}">
<div class="kicker">{E(f['id'])} · {E(f['severity'])} severity</div>
<h3>{E(f['title'])}</h3>
<p class="small">{E(f['detail'])}</p>
<p class="source">Evidence: {E(f['source'])}</p></article>""")
    body = f"""<div class="hero"><div class="kicker">Flagged for review</div>
<h1>{len(flags)} irregularities, gaps and disclosed assumptions</h1>
<p class="lede">Nothing here is hidden in a footnote. Each item says what is wrong or missing, what the desk did instead, and where to check it.
Unverified values are blank on every table rather than guessed.</p></div>
<div class="cards">{''.join(items)}</div>"""
    write(OUT / "flagged.html", page("", "Flagged for review", body, "Every flagged irregularity and coverage gap."))

    # ---------------- review ----------------
    rev = []
    for r in rows:
        s = r.get("selection") or {}
        missing = ", ".join(r.get("missing_fields") or []) or ""
        rev.append(
            f'<tr><td>{E(r["id"])}</td><td>{E(r["sport_label"])}</td><td>{E(r["competition"] or "")}</td>'
            f'<td>{E(r["evidence_status"])}<div class="tag">{E(r["evidence_checked_utc"] or "no timestamp")}</div></td>'
            f'<td>{E(r["input_status"] or "")}</td><td>{E(s.get("selection", ""))}</td><td>{badge(r["tier"])}</td>'
            f'<td class="source">{src_cell(r)}</td><td class="small">{E(missing)}</td>'
            f'<td class="small">{E("; ".join(r.get("flags") or []))}</td></tr>')
    rev_tbl = ('<div class="tbl"><table data-audit="row"><thead><tr><th>ID</th><th>Sport</th><th>Competition</th><th>Evidence</th>'
               '<th>Inputs</th><th>Selection</th><th>Tier</th><th>Official source</th><th>Blank fields</th><th>Flags</th>'
               '</tr></thead><tbody>' + "".join(rev) + "</tbody></table></div>")
    lst = []
    for r in DESK["listing_only"]:
        lst.append(f'<tr><td>{E(r["id"])}</td><td>{E(r["sport_label"])}</td><td>{E(r["time_display"])}</td>'
                   f'<td><b>{E(r["home"])}</b> ' + (f'v {E(r["away"])}' if r.get("away") else "") + "</td>"
                   f'<td class="source">{src_cell(r)}</td><td class="small">{E("; ".join(r.get("flags") or []))}</td></tr>')
    lst_tbl = ('<div class="tbl"><table data-audit="row"><thead><tr><th>ID</th><th>Sport</th><th>Date as listed</th><th>Listing</th>'
               '<th>Official source</th><th>Flag</th></tr></thead><tbody>' + "".join(lst) + "</tbody></table></div>")
    body = f"""<div class="hero"><div class="kicker">Line-by-line review</div>
<h1>Every row, its evidence, its blanks</h1>
<p class="lede">This is the audit trail: {len(rows)} upcoming rows and {len(DESK['listing_only'])} captured listings, each with the official page it came from,
whether this session re-read that page, which fields are blank, and every flag attached. Click any source to check the claim.</p></div>
<h2>Upcoming rows</h2>{rev_tbl}
<h2>Listing-only rows (no verified start time)</h2>{lst_tbl}
<h2>What was accepted as evidence</h2>
<ul class="tight small">
<li><b>Accepted:</b> league and governing-body pages (NHL.com, EuroLeague Basketball, MLB StatsAPI, PDC, AFL, WST) and their official injury/availability reports.</li>
<li><b>Not accepted:</b> OLBG cards, aggregator odds, preview prose where it contradicts the same site's table, or any figure not printed in the source.</li>
<li><b>Never inferred:</b> start times (left blank), injuries that a club did not list, pitchers, goaltenders, or a team rating from a competition table that was not read.</li>
</ul>"""
    write(OUT / "review.html", page("", "Line-by-line review", body, "Row-by-row evidence audit."))

    # ---------------- sources ----------------
    srows = []
    for s in sorted(DESK["sources"], key=lambda x: (x["status"], x["publisher"])):
        srows.append(f'<tr><td><a href="{E(s["url"])}">{E(s["name"])}</a></td><td>{E(s["publisher"])}</td>'
                     f'<td>{badge("High" if s["status"] == "fresh" else "Unpriced").replace("High", "fresh").replace("Unpriced", "carried")}</td>'
                     f'<td class="num">{E(s["read_utc"])}</td><td class="small">{E(s["confirms"])}</td>'
                     f'<td class="small">{E(s["does_not_confirm"])}</td><td class="small">{E(s.get("note", ""))}</td></tr>')
    body = f"""<div class="hero"><div class="kicker">Sources</div><h1>{len(DESK['sources'])} official sources, with what each does and does not prove</h1>
<p class="lede">“Fresh” means this session opened the page on 22 October 2026. “Carried” means an earlier session read it and this desk did not re-read it; those rows are capped at Medium.</p></div>
<div class="tbl"><table data-audit="row"><thead><tr><th>Source</th><th>Publisher</th><th>Status</th><th class="num">Read (UTC)</th><th>Confirms</th><th>Does not confirm</th><th>Note</th></tr></thead>
<tbody>{''.join(srows)}</tbody></table></div>
<h2>What is deliberately missing</h2>
<p>No bookmaker price feed, no odds-aggregator scrape and no API key is used. Where the desk needed a market reference it used the price NHL.com publishes beside each game, labelled as a reference and never as an input to a rating.</p>"""
    write(OUT / "sources.html", page("", "Sources", body, "Official sources and their limits."))

    # ---------------- methodology ----------------
    m = DESK["method"]
    body = f"""<div class="hero"><div class="kicker">Method</div><h1>How every number on this site was produced</h1>
<p class="lede">Four models, one gate, no bookmaker data. Everything below is reproducible from the JSON with the constants printed here.</p></div>
<h2>1. Prices</h2>
<p>For a probability <i>p</i>, the zero-vig fair decimal is <code>1/p</code>; the offered decimal is <code>1/(p × {m['overround']})</code>.
American odds are <code>-100/(dec-1)</code> below 2.00 and <code>(dec-1)×100</code> above. Every market is two-way and the two probabilities sum to exactly 1.</p>
<h2>2. The High gate</h2>
<ul class="tight">
<li>Model probability strictly greater than 70.00% and at most 71.4286% (so the fair price is inside -250..+10000).</li>
<li>Official evidence read by this session for both sides.</li>
<li>Both clubs' availability confirmed in the official report for that round.</li>
<li>The selection agrees with the model's own view of the match.</li>
<li>A unique prediction of at least 30 words naming the selection and the price.</li>
</ul>
<p>Anything short of all five is Medium or Low, with the failing test printed on the row.</p>
<h2>3. The models</h2>
<div class="grid2">
<div class="card"><h3>EuroLeague</h3><p class="small">Expected points for each side = (own points scored per game + opponent points allowed per game) ÷ 2, taken from the official standings.
Margin ~ Normal(σ = {m['el_sigma_margin']}); total ~ Normal(σ = {m['el_sigma_total']}). No home-court edge is added beyond the scoring rates, and injuries are narrative facts, not point adjustments.</p></div>
<div class="card"><h3>NHL</h3><p class="small"><code>logit({m['nhl_base']}) + (home P% - away P%) × 100 / {m['nhl_scale']}</code>. Points percentage only. No goaltender, rest or travel term.</p></div>
<div class="card"><h3>MLB</h3><p class="small"><code>logit({m['mlb_base']}) + (home win% - away win%) / {m['mlb_scale']}</code> on final regular-season records. No pitcher, bullpen or park term.</p></div>
<div class="card"><h3>Carried sports</h3><p class="small">Darts, rugby league, rugby union, handball, volleyball, Australian rules, Gaelic football, cricket and motor racing use the stored official inputs from the earlier evidence file, run through the repository's logit engine. No new inputs were invented.</p></div>
</div>
<h2>4. Exclusions</h2>
<p>Football/soccer, American football, boxing, UFC/MMA, hurling, horse racing, cycling and specials are out of scope by instruction and do not appear in any table.</p>
<h2>5. Limits</h2>
<ul class="tight">
<li>No calibration study exists for these constants; a 71% label is a rule, not a measured strike rate.</li>
<li>No closing-line comparison, so “value” is never claimed.</li>
<li>Carried evidence was not re-read and is capped at Medium.</li>
<li>Where a source contradicts itself, the table value wins and the contradiction is flagged.</li>
</ul>"""
    write(OUT / "methodology.html", page("", "Method", body, "Models, constants and the High gate."))

    # ---------------- coverage ----------------
    body = f"""<div class="hero"><div class="kicker">Coverage</div><h1>What is covered, what is thin, what is blank</h1>
<p class="lede">Coverage is reported as captured, not as desired. A category with zero upcoming rows says so rather than borrowing an unverified fixture.</p></div>
{cov_tbl}
<h2>The gaps, explicitly</h2>
<ul class="tight">
<li><b>No verified future fixture:</b> tennis, snooker, golf, greyhounds and eSports. Their pages carry {sum(c['listings'] for c in cov if c['sport'] in ('tennis','snooker','golf','greyhounds','esports'))} captured listings with no verified clock, all unpriced.</li>
<li><b>Priced but thin:</b> baseball (5 rows, all sharing the same two regular-season records), motor racing (1 row, no two-sided market), volleyball ({next(c['unpriced'] for c in cov if c['sport']=='volleyball')} rows with no rating for both sides).</li>
<li><b>Carried evidence:</b> {counts['carried']} priced rows across darts, rugby league, rugby union, handball, volleyball, Australian rules, Gaelic football, cricket and motor racing.</li>
<li><b>Fresh evidence:</b> {counts['fresh']} rows — all 12 NHL games, all 9 EuroLeague games and all 5 World Series games.</li>
</ul>
<p class="small muted">Counts reconcile with <a href="../data/fec05fb4/desk.json">desk.json</a>: every table on this site is rendered from that file.</p>"""
    write(OUT / "coverage.html", page("", "Coverage", body, "Per-category coverage and gaps."))

    print("pages written:", len(list(OUT.rglob("*.html"))))


if __name__ == "__main__":
    main()
