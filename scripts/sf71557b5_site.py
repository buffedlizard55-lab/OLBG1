#!/usr/bin/env python3
"""
sf71557b5_site.py - renders the session f71557b5-olbg1 (task T50) dashboard into
f71557b5/. Self-contained namespace: no other session's page, dataset or generator
is read or written.

Run:  python3 scripts/sf71557b5_site.py      (after data + model + audit)
"""
from __future__ import annotations

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data" / "f71557b5"
SITE = ROOT / "f71557b5"
(SITE / "sports").mkdir(parents=True, exist_ok=True)
(SITE / "assets").mkdir(parents=True, exist_ok=True)

# Official page read for a sport that produced no priced row - so the sport page still
# cites the governing body that settles why nothing is published.
FALLBACK_SRC = {
    "tennis": ("ATP official signed Tour Supervisor main draw - Almaty, released 21/10/2026 20:51:24, "
               "showing every Round of 32 tie already scored",
               "https://www.protennislive.com/posting/2026/9410/mds.pdf"),
    "volleyball": ("TAURON Liga official club page carrying the men's Skra Belchatow v Projekt Warszawa "
                   "fixture for 24 October 2026", "https://www.tauronliga.pl/teams/tour/53/id/61.html"),
    "greyhounds": ("Greyhound Board of Great Britain - the sport's licensing body; not reachable this "
                   "session, so coverage stays zero and unconfirmed", "https://www.gbgb.org.uk/"),
    "esports": ("LoL Esports official Worlds 2026 primer - stage dates, Swiss format and seeded tiers",
                "https://lolesports.com/en-US/news/worlds-2026-primer"),
}
SPORTS = [
    ("tennis", "Tennis", 3), ("basketball", "Basketball", 4), ("golf", "Golf", 5),
    ("cricket", "Cricket", 7), ("snooker", "Snooker", 8), ("rugby-union", "Rugby Union", 9),
    ("rugby-league", "Rugby League", 10), ("baseball", "Baseball", 12), ("ice-hockey", "Ice Hockey", 13),
    ("motor-racing", "Motor Racing", 14), ("darts", "Darts", 15), ("handball", "Handball", 20),
    ("volleyball", "Volleyball", 21), ("aussie-rules", "Aussie Rules", 22), ("esports", "eSports", 23),
    ("gaelic-football", "Gaelic Football", 25), ("greyhounds", "Greyhounds", 28),
]
SLUG = {s[0]: s for s in SPORTS}

FX = json.loads((D / "fixtures.json").read_text(encoding="utf-8"))
LN = json.loads((D / "lines.json").read_text(encoding="utf-8"))
SRC = json.loads((D / "sources.json").read_text(encoding="utf-8"))
COV = json.loads((D / "coverage.json").read_text(encoding="utf-8"))
FLG = json.loads((D / "flagged.json").read_text(encoding="utf-8"))
WIN = json.loads((D / "window.json").read_text(encoding="utf-8"))
AUD = json.loads((D / "repo_audit.json").read_text(encoding="utf-8"))
HARV = json.loads((D / "olbg_harvest.json").read_text(encoding="utf-8"))

C = LN["counts"]
ROWS = {r["id"]: r for r in LN["rows"]}
ORDER = [r["id"] for r in LN["rows"]]

e = html.escape


def srcs(row, limit=4):
    out = []
    for s in row["sources"][:limit]:
        out.append(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"][:64])}</a>')
    if len(row["sources"]) > limit:
        out.append(f'<span class="muted">+{len(row["sources"]) - limit} more on the sources page</span>')
    return '<div class="src">' + "".join(out) + "</div>"


def badge(t):
    return {"High": "hi", "Medium": "med", "Low": "lo"}.get(t, "mut")


def money(us):
    return f"{us:+d}"


NAV = [("index.html", "Overview"), ("picks.html", "All Fixtures"), ("markets.html", "Markets"),
       ("predictions.html", "High Picks"), ("window.html", "Price Window"),
       ("sports.html", "17 Sports"), ("coverage.html", "Coverage"),
       ("verification.html", "Verification"), ("audit.html", "Repo Audit"),
       ("reverse-engineering.html", "OLBG Teardown"), ("flagged.html", "Flagged for Review"),
       ("sources.html", "Official Sources"), ("methodology.html", "Methodology")]

CSS = """
:root{--bg:#0d1117;--panel:#161b22;--line:#2b333d;--fg:#e6edf3;--mut:#9aa7b4;--acc:#4ea1ff;
--hi:#2ea043;--med:#d29922;--lo:#8b949e;--bad:#f85149}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,
"Segoe UI",Helvetica,Arial,sans-serif}
header{background:#11161d;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:9}
.hd{max-width:1460px;margin:0 auto;padding:13px 20px;display:flex;flex-wrap:wrap;gap:14px;align-items:baseline}
.brand{font-weight:700;letter-spacing:.2px}.brand a{color:var(--fg);text-decoration:none}
.brand .sub{color:var(--mut);font-weight:400;font-size:.8rem;margin-left:8px}
nav.main{display:flex;flex-wrap:wrap;gap:3px}
nav.main a{color:var(--mut);text-decoration:none;padding:5px 9px;border-radius:6px;font-size:.84rem}
nav.main a:hover{background:#1c242e;color:var(--fg)}
nav.main a[aria-current=page]{background:#1f6feb22;color:#9ecbff}
main{max-width:1460px;margin:0 auto;padding:20px}
h1{font-size:1.55rem;margin:6px 0 4px}h2{font-size:1.13rem;margin:26px 0 8px;border-bottom:1px solid
var(--line);padding-bottom:6px}h3{font-size:.98rem;margin:16px 0 6px}
p.lede{color:var(--mut);max-width:105ch;margin:4px 0 14px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));margin:14px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:11px 13px}
.kpi b{display:block;font-size:1.5rem;line-height:1.15}
.kpi span{color:var(--mut);font-size:.76rem;text-transform:uppercase;letter-spacing:.06em}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
table{width:100%;border-collapse:collapse;font-size:.845rem;margin:8px 0}
th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:.75rem;text-transform:uppercase;letter-spacing:.05em;
position:sticky;top:0;background:var(--panel)}
tr:hover td{background:#1a212a}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--panel)}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:.72rem;font-weight:700;
border:1px solid transparent;white-space:nowrap}
.badge.hi{background:#12321c;color:#56d364;border-color:#1f6f35}
.badge.med{background:#332701;color:#e3b341;border-color:#6b5207}
.badge.lo{background:#21262d;color:#9aa7b4;border-color:#3a444f}
.badge.v{background:#0d2a4d;color:#79c0ff;border-color:#1f4f82}
.badge.x{background:#3d1418;color:#ff7b72;border-color:#7d2029}
.odds{font-variant-numeric:tabular-nums;font-weight:600}
.muted{color:var(--mut)}.small{font-size:.79rem}
.src{display:flex;flex-direction:column;gap:2px}
.src a{color:#79c0ff;text-decoration:none;font-size:.76rem}
.src a:hover{text-decoration:underline}
a{color:var(--acc)}
ul.tight{margin:6px 0 6px 18px;padding:0}ul.tight li{margin:3px 0}
details{margin:6px 0;border:1px solid var(--line);border-radius:8px;background:#12171e}
summary{cursor:pointer;padding:7px 11px;font-size:.83rem;font-weight:600}
details[open] summary{border-bottom:1px solid var(--line)}
.dm{padding:9px 12px}
.dm table{margin:4px 0}
.basis{color:var(--mut);font-size:.76rem;margin:3px 0 8px;padding-left:8px;border-left:2px solid var(--line)}
code{background:#1c232c;padding:1px 5px;border-radius:4px;font-size:.82em}
.flag{border-left:3px solid var(--bad);padding:8px 12px;margin:8px 0;background:#1a1215;border-radius:0 8px 8px 0}
.flag.med{border-color:var(--med);background:#1a1710}
.flag.info{border-color:#30475e;background:#111a22}
.flag b{display:block;margin-bottom:2px}
.nowrap{white-space:nowrap}
footer{max-width:1460px;margin:0 auto;padding:18px 20px 40px;color:var(--mut);font-size:.78rem;
border-top:1px solid var(--line)}
"""


def page(rel, title, body, h1=None, lede=None):
    depth = rel.count("/")
    pre = "../" * depth
    nav = "".join(
        f'<a href="{pre}{h}"{" aria-current=page" if h == rel else ""}>{e(t)}</a>' for h, t in NAV)
    sportnav = "".join(f'<a href="{pre}sports/{s}.html">{e(n)}</a>' for s, n, _ in SPORTS)
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG Desk f71557b5</title>
<meta name="description" content="Session f71557b5-olbg1: live 22 October 2026 OLBG harvest across all 17 in-scope sports, official-source verification, originated multi-market lines and in-window high-confidence picks.">
<link rel="stylesheet" href="{pre}assets/style.css">
</head>
<body>
<header><div class="hd">
<div class="brand"><a href="{pre}index.html">OLBG Origination Desk <span class="sub">f71557b5 · 2026-10-22 UTC · official sources only</span></a></div>
<nav class="main" aria-label="Primary">{nav}</nav>
</div>
<div class="hd" style="padding-top:0"><nav class="main" aria-label="Sports">{sportnav}</nav></div>
</header>
<main>
<h1>{e(h1 or title)}</h1>
{f'<p class="lede">{lede}</p>' if lede else ""}
{body}
</main>
<footer>
Session <code>f71557b5-olbg1</code>, task T50. Every row on every page carries at least one link to an
official governing body, tour, federation, league or club page that was actually read on 2026-10-22.
Values that could not be read there are left blank and listed on the Flagged for Review page. Prices are
our own model output at zero vig — not market prices, not betting advice.
</footer>
</body>
</html>
"""
    (SITE / rel).write_text(doc, encoding="utf-8")


(SITE / "assets" / "style.css").write_text(CSS, encoding="utf-8")

# ============================================================ OVERVIEW =======
highs = [r for r in LN["rows"] if r["selection"] and r["selection"]["confidence"] == "High"]
body = f"""
<div class="grid">
<div class="kpi"><b>{C['fixtures']}</b><span>fixtures &amp; cards</span></div>
<div class="kpi"><b>{C['priced']}</b><span>priced matches</span></div>
<div class="kpi"><b>{C['prices']:,}</b><span>originated prices</span></div>
<div class="kpi"><b>{C['high']}</b><span>high confidence</span></div>
<div class="kpi"><b>{C['medium']}</b><span>medium</span></div>
<div class="kpi"><b>{C['low']}</b><span>low</span></div>
<div class="kpi"><b>{C['no_bet']}</b><span>no bet</span></div>
<div class="kpi"><b>{C['sports']}</b><span>sports with rows</span></div>
<div class="kpi"><b>{len(SRC['sources'])}</b><span>official source URLs</span></div>
<div class="kpi"><b>{len(FLG['flags'])}</b><span>flags</span></div>
</div>

<div class="panel">
<b>What this desk is.</b> All 17 in-scope OLBG sport hubs were read live on 22 October 2026, then every
fixture was re-read on the governing body's own page before it was priced. Sports OLBG excludes and this
brief excludes — soccer/football, horse racing, american football, boxing, UFC/MMA, hurling, cycling and
specials — were enumerated and dropped, not skipped. Lines are originated here at zero vig; the 5%
book-equivalent is printed beside every price for comparison but is never the number the window is tested
against. See <a href="methodology.html">Methodology</a> and finding
<a href="flagged.html">F-F7-01</a> for why that choice matters.
</div>

<h2>High-confidence selections — every one inside −250 … +10000 and above 70%</h2>
<p class="lede">A High pick on this desk must clear four gates at once: the row is <code>verified</code> against a
page read today, both sides carry a sourced rating, the model probability is at least 0.700, and the
originated fair price is inside the brief's window. Because −250 is exactly a 71.43% fair price, the
admissible band is 0.700–0.7143 and the qualifying rung is taken from a standard sport ladder — never a
model-calibrated alternate line. Fixtures whose favourite is shorter than −250 are published in the
<a href="window.html">Rejected Highs</a> table instead.</p>
<div class="tw"><table>
<thead><tr><th>Fixture</th><th>Sport</th><th>Competition</th><th>Selection</th><th>Market</th>
<th>Model</th><th>Fair</th><th>US</th><th>5% book</th><th>Tier</th><th>Official source</th></tr></thead><tbody>
"""
for r in highs:
    s = r["selection"]
    body += (f'<tr id="row-{e(r["id"])}"><td class="nowrap"><a href="picks.html#{e(r["id"])}">'
             f'{e(r["home"])}{(" v " + e(r["away"])) if r["away"] else ""}</a><br>'
             f'<span class="muted small">{e(r["start_local"] or r["start_utc"] or "date not published")}</span></td>'
             f'<td>{e(SLUG[r["sport"]][1])}</td><td>{e(r["competition"])}</td>'
             f'<td><b>{e(s["selection"])}</b></td><td class="small">{e(s["market"])}</td>'
             f'<td class="odds">{s["prob"]*100:.1f}%</td><td class="odds">{s["price"]:.2f}</td>'
             f'<td class="odds">{money(s["us"])}</td><td class="odds muted">{s["book_price"]:.2f} '
             f'({money(s["book_us"])})</td><td><span class="badge {badge(s["confidence"])}">High</span></td>'
             f'<td>{srcs(r, 2)}</td></tr>\n')
body += """</tbody></table></div>

<h2>Sport-by-sport coverage</h2>
<div class="tw"><table>
<thead><tr><th>Sport</th><th>OLBG id</th><th>OLBG cards seen</th><th>Rows verified</th><th>Priced</th>
<th>Outcome</th><th>Live OLBG hub read today</th></tr></thead><tbody>
"""
for c in COV["sports"]:
    hub = next((h for h in HARV["in_scope"] if h["sport"] == c["sport"]), None)
    body += (f'<tr><td><a href="sports/{e(c["sport"])}.html">{e(SLUG[c["sport"]][1])}</a></td>'
             f'<td>{c["olbg_id"]}</td><td>{c["olbg_cards"]}</td><td>{c["verified_rows"]}</td>'
             f'<td>{c["priced_rows"]}</td><td>{e(c["outcome"])}</td>'
             f'<td><a href="{e(c["hub"])}" target="_blank" rel="noopener">{e(c["hub"])}</a></td></tr>\n')
body += f"""</tbody></table></div>

<h2>Headline findings from this pass</h2>
"""
for f in [x for x in FLG["flags"] if x["id"] in ("F-F7-01", "F-F7-02", "F-F7-03", "F-F7-04", "F-F7-06",
                                                  "F-F7-NHL-01", "F-F7-13")]:
    body += (f'<div class="flag {e(f["severity"])}"><b>{e(f["id"])} — {e(f["title"])}</b>'
             f'{e(f["text"])}<br><span class="small">Official source: '
             f'<a href="{e(f["source"])}" target="_blank" rel="noopener">{e(f["source"])}</a></span></div>\n')
page("index.html", "Overview", body,
     "Live 22 October 2026 desk — 17 in-scope sports, official sources only",
     f'{C["fixtures"]} fixtures and event cards harvested from all 17 in-scope OLBG sport hubs and re-read on '
     f'the governing body&rsquo;s own page, {C["priced"]} priced across {C["prices"]:,} originated selections, '
     f'{C["high"]} High-confidence picks every one inside the −250 to +10000 window, and {len(FLG["flags"])} '
     f'flagged irregularities published for review.')

# ============================================================== PICKS =======
body = f"""<p class="lede">Every fixture this desk verified on 22 October 2026, one row each. The
<b>match-winner call</b> is the moneyline (or draw-no-bet) side the model favours with its own tier, so each
match always carries an explicit winner pick as the brief requires. The <b>desk selection</b> is the
strongest line that is both inside the −250…+10000 window and at or above 52%; where nothing qualifies the
row prints <span class="badge x">no bet</span> with the reason. Each row links the official page it was read
from. {C['fixtures']} rows, {C['selections']} tips, {C['no_bet']} no-bets.</p>
<div class="tw"><table>
<thead><tr><th>Start (as published)</th><th>Match / event</th><th>Sport</th><th>Competition</th>
<th>Match-winner call</th><th>Desk selection</th><th>All originated markets</th><th>Status</th>
<th>Official source</th></tr></thead><tbody>
"""
for rid in ORDER:
    r = ROWS[rid]
    wc = r["winner_call"]
    sel = r["selection"]
    name = f'{e(r["home"])}' + (f' <span class="muted">v</span> {e(r["away"])}' if r["away"] else "")
    if r["venue"]:
        name += f'<br><span class="muted small">{e(r["venue"])}</span>'
    wc_cell = ("<span class='muted'>event card — no head-to-head</span>" if r["event_only"]
               else (f'<b>{e(wc["selection"])}</b><br><span class="odds small">{wc["price"]:.2f} '
                     f'({money(wc["us"])})</span> · <span class="small">{wc["prob"]*100:.1f}%</span><br>'
                     f'<span class="badge {badge(wc["confidence"])}">{e(wc["confidence"])}</span>'
                     + (f'<br><span class="muted small">{e(wc["cap"])}</span>' if wc.get("cap") else "")))
    if sel:
        sel_cell = (f'<b>{e(sel["selection"])}</b><br><span class="small">{e(sel["market"])}</span><br>'
                    f'<span class="odds">{sel["price"]:.2f} ({money(sel["us"])})</span> · '
                    f'<span class="small">{sel["prob"]*100:.1f}%</span><br>'
                    f'<span class="badge {badge(sel["confidence"])}">{e(sel["confidence"])}</span>'
                    + (' <span class="badge v">in window</span>' if sel["us"] >= -250 else "")
                    + (f'<br><span class="muted small">{e(sel["cap"])}</span>' if sel.get("cap") else ""))
    else:
        reason = next((n["reason"] for n in WIN["no_bet"] if n["id"] == rid),
                      "no priced market on this row")
        sel_cell = f'<span class="badge x">no bet</span><br><span class="muted small">{e(reason)}</span>'
    mk = ("<span class='muted'>not priced — see flag</span>" if not r["markets"]
          else f'<a href="markets.html#{e(rid)}">{len(r["markets"])} markets · '
               f'{sum(len(m["outcomes"]) for m in r["markets"])} prices</a>')
    body += (f'<tr id="{e(rid)}"><td class="nowrap">{e(r["start_local"] or r["start_utc"] or "—")}'
             + (f'<br><span class="muted small">{e(r["start_utc"])}</span>'
                if r["start_local"] and r["start_utc"] else "")
             + f'</td><td>{name}</td><td><a href="sports/{e(r["sport"])}.html">{e(SLUG[r["sport"]][1])}</a></td>'
             f'<td>{e(r["competition"])}<br><span class="muted small">{e(r["round"])}</span></td>'
             f'<td>{wc_cell}</td><td>{sel_cell}</td><td class="nowrap">{mk}</td>'
             f'<td><span class="badge v">{e(r["status"])}</span></td><td>{srcs(r)}</td></tr>\n')
body += "</tbody></table></div>"
page("picks.html", "All Fixtures", body, "Every verified fixture, its match-winner call and its desk selection")

# =========================================================== MARKETS ========
body = f"""<p class="lede">{C['prices']:,} originated prices across {C['priced']} fixtures. Every price is a
zero-vig fair price derived from the model probability printed beside it; the 5% book-equivalent is shown in
grey for comparison only. Each market prints the basis it was built from, including which values are sourced
and which are labelled modelling assumptions. Rungs outside 5%–95% are dropped so no degenerate price is
published. Totals exist only for the sports where both clubs' scoring rates were read on an official page.</p>
"""
by_sport = {}
for rid in ORDER:
    by_sport.setdefault(ROWS[rid]["sport"], []).append(rid)
for slug, nname, sid in SPORTS:
    ids = by_sport.get(slug, [])
    if not ids:
        continue
    body += f'<h2>{e(nname)} <span class="muted small">OLBG sport id {sid}</span></h2>\n'
    for rid in ids:
        r = ROWS[rid]
        body += (f'<details id="{e(rid)}"><summary>{e(r["home"])}'
                 + (f' v {e(r["away"])}' if r["away"] else "")
                 + f' — {e(r["competition"])}'
                 + (f' · {len(r["markets"])} markets' if r["markets"] else " · not priced")
                 + f' · <a href="{e(r["sources"][0]["url"])}" target="_blank" rel="noopener">official source</a>'
                 + '</summary><div class="dm">\n')
        if r["event_only"]:
            body += f'<p class="small muted">{e(r.get("note", ""))}</p>\n'
        if not r["markets"] and not r["event_only"]:
            body += ('<p class="small">No price originated: the official pages read do not carry a sourced '
                     'rating for both sides, so repository rule 4 refuses the edge. '
                     '<a href="flagged.html">See the flag register.</a></p>\n')
        for m in r["markets"]:
            body += f'<h3>{e(m["market"])}</h3><div class="tw"><table><thead><tr><th>Outcome</th>' \
                    '<th>Model</th><th>Fair (0% vig)</th><th>US</th><th>Book @5%</th><th>US</th>' \
                    '<th>In window</th></tr></thead><tbody>\n'
            for o in m["outcomes"]:
                win_badge = "<span class='badge v'>yes</span>" if o["in_band"] else "<span class='badge x'>no</span>"
                capped = ' <span class="muted">(capped)</span>' if o.get("capped") else ''
                body += (f'<tr><td>{e(o["selection"])}</td><td class="odds">{o["prob"]*100:.2f}%'
                         + capped
                         + f'</td><td class="odds">{o["price"]:.2f}</td><td class="odds">{money(o["us"])}</td>'
                         f'<td class="odds muted">{o["book_price"]:.2f}</td>'
                         f'<td class="odds muted">{money(o["book_us"])}</td>'
                         f'<td>{win_badge}</td></tr>\n')
            body += f'</tbody></table></div><div class="basis">{e(m["basis"])}</div>\n'
        if r.get("model_notes"):
            body += '<div class="basis"><b>Model derivation.</b> ' + \
                " ".join(e(n) for n in r["model_notes"]) + '</div>\n'
        for fl in r["flags"]:
            body += f'<div class="flag med small"><b>{e(fl["code"])}</b>{e(fl["text"])}</div>\n'
        body += f'<div class="small">Sources: {srcs(r, 8)}</div></div></details>\n'
page("markets.html", "Markets", body, "Every originated market, rung by rung, with its basis")

# ======================================================== PREDICTIONS =======
body = f"""<p class="lede">One hand-written preview for each of the {C['high']} High-confidence selections.
Each names the team or player, states current form, gives recent match history and makes the betting
selection explicit with its price. Every factual clause comes from an official page read on 22 October 2026
and is listed under the preview. No six-word sequence repeats inside a preview or anywhere across the
corpus; the validator fails the build if one does.</p>
"""
for r in highs:
    s = r["selection"]
    body += f"""<div class="panel" id="{e(r['id'])}">
<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;justify-content:space-between">
<h2 style="border:0;margin:0;padding:0">{e(r['home'])}{(' v ' + e(r['away'])) if r['away'] else ''}</h2>
<span class="badge {badge(s['confidence'])}">High · {s['prob']*100:.1f}%</span>
</div>
<p class="small muted">{e(r['competition'])}{(' · ' + e(r['round'])) if r['round'] else ''} ·
{e(r['start_local'] or r['start_utc'] or 'date not published')}{(' · ' + e(r['venue'])) if r['venue'] else ''}</p>
<p><b>The selection: {e(s['selection'])}</b> — {e(s['market'])} at <span class="odds">{s['price']:.2f}</span>
(<span class="odds">{money(s['us'])}</span>, inside the −250…+10000 window; 5% book-equivalent
{s['book_price']:.2f} / {money(s['book_us'])}).</p>
<p>{e(s['prose'])}</p>
<h3>Match-winner call</h3>
<p class="small">{e(r['winner_call']['selection'])} to win at {r['winner_call']['price']:.2f}
({money(r['winner_call']['us'])}), {r['winner_call']['prob']*100:.1f}% —
<span class="badge {badge(r['winner_call']['confidence'])}">{e(r['winner_call']['confidence'])}</span></p>
<h3>Verified inputs behind this preview</h3>
<div class="tw"><table><thead><tr><th>Input</th><th>Value as published</th><th>Official source</th></tr></thead><tbody>
"""
    for ev in r["evidence"]:
        body += (f'<tr><td>{e(ev["label"])}</td><td>{e(ev["value"])}</td>'
                 f'<td><a href="{e(ev["source"])}" target="_blank" rel="noopener">{e(ev["source_name"][:70])}</a>'
                 f'</td></tr>\n')
    body += f'</tbody></table></div><div class="small">All sources: {srcs(r, 10)}</div></div>\n'
page("predictions.html", "High Picks", body,
     f"{C['high']} high-confidence previews, all in-window, all sourced")

# ============================================================ WINDOW ========
rej_by_fix = {}
for x in WIN["rejected_highs"]:
    rej_by_fix.setdefault(x["id"], []).append(x)
mw_rej = []
for rid, items in rej_by_fix.items():
    best = max([i for i in items if i["market"] == "Match winner"] or items, key=lambda y: y["prob"])
    mw_rej.append((rid, best, len(items)))
mw_rej.sort(key=lambda x: -x[1]["prob"])
body = f"""<p class="lede">This page is the answer to the brief's central complaint: that most "high
confidence" picks are simply anything above 70%, which prices shorter than −250 and carries no value. Here
is the arithmetic, and both sides of the ledger.</p>
<div class="panel">
<b>The window arithmetic.</b> At a zero-vig fair line a probability of 0.700 prices at 1.4286 (−233) and
0.7143 prices at exactly 1.40 (−250). So the two rules the brief states — above 70% to win, and inside
−250…+10000 — can only both hold in the band <b>0.700 ≤ p ≤ 0.7143</b>. Add a bookmaker margin and the
band empties completely: at a 5% overround 0.700 prices at 1.3606 (−277), already through the floor. That
is why this desk originates at zero vig and publishes the 5% equivalent alongside rather than pretending
both rules can bind on a margined line. Recorded as finding
<a href="flagged.html">F-F7-01</a>.
</div>
<div class="grid">
<div class="kpi"><b>{len(mw_rej)}</b><span>fixtures with a &gt;70% winner the window rejects</span></div>
<div class="kpi"><b>{len(WIN['rejected_highs'])}</b><span>individual rungs rejected</span></div>
<div class="kpi"><b>{C['high']}</b><span>selections that cleared both gates</span></div>
<div class="kpi"><b>{C['no_bet']}</b><span>fixtures with no bet at all</span></div>
</div>

<h2>Rejected Highs — above 70% but shorter than −250</h2>
<p class="lede">One row per fixture: the strongest match-winner probability the model produced that the
window excludes. These are exactly the "trivial favourite" picks the brief asks us not to dress up as high
confidence. The full rung-level list ({len(WIN['rejected_highs'])} entries) is in
<code>data/f71557b5/window.json</code>.</p>
<div class="tw"><table><thead><tr><th>Fixture</th><th>Sport</th><th>Selection above 70%</th>
<th>Model</th><th>Fair</th><th>US</th><th>Rungs rejected</th><th>Official source</th></tr></thead><tbody>
"""
for rid, best, n in mw_rej:
    r = ROWS[rid]
    body += (f'<tr><td><a href="picks.html#{e(rid)}">{e(r["home"])}'
             f'{(" v " + e(r["away"])) if r["away"] else ""}</a></td>'
             f'<td>{e(SLUG[r["sport"]][1])}</td><td>{e(best["selection"])}</td>'
             f'<td class="odds">{best["prob"]*100:.1f}%</td><td class="odds">{best["price"]:.2f}</td>'
             f'<td class="odds"><span class="badge x">{money(best["us"])}</span></td><td>{n}</td>'
             f'<td>{srcs(r, 1)}</td></tr>\n')
body += """</tbody></table></div>

<h2>No-bet cards — nothing in the window reaches 52%</h2>
<div class="tw"><table><thead><tr><th>Fixture</th><th>Sport</th><th>Reason</th>
<th>Official source</th></tr></thead><tbody>
"""
for n in WIN["no_bet"]:
    r = ROWS[n["id"]]
    body += (f'<tr><td><a href="picks.html#{e(n["id"])}">{e(n["match"])}</a></td>'
             f'<td>{e(SLUG[n["sport"]][1])}</td><td>{e(n["reason"])}</td><td>{srcs(r, 1)}</td></tr>\n')
body += "</tbody></table></div>"
page("window.html", "Price Window", body, "The −250 … +10000 window, enforced in code")

# ============================================================= SPORTS =======
for slug, nname, sid in SPORTS:
    ids = [r for r in ORDER if ROWS[r]["sport"] == slug]
    cov = next((c for c in COV["sports"] if c["sport"] == slug), None)
    hub = next((h for h in HARV["in_scope"] if h["sport"] == slug), None)
    body = f"""<div class="grid">
<div class="kpi"><b>{sid}</b><span>OLBG sport id</span></div>
<div class="kpi"><b>{hub['cards_seen'] if hub else '—'}</b><span>OLBG cards seen live</span></div>
<div class="kpi"><b>{cov['verified_rows'] if cov else len(ids)}</b><span>rows verified today</span></div>
<div class="kpi"><b>{cov['priced_rows'] if cov else 0}</b><span>priced</span></div>
</div>
<div class="panel"><b>Live OLBG hub, read 2026-10-22:</b>
<a href="{e(hub['hub']) if hub else '#'}" target="_blank" rel="noopener">{e(hub['hub']) if hub else ''}</a>
<br><span class="small muted">{e(hub['note']) if hub else ''}</span></div>
"""
    if cov:
        body += f'<div class="panel"><b>Coverage outcome:</b> {e(cov["outcome"])}<br>{e(cov["detail"])}</div>\n'
    if not ids and slug in FALLBACK_SRC:
        fb = FALLBACK_SRC[slug]
        body += (f'<div class="panel small"><b>Official page that settles it:</b> {e(fb[0])} &mdash; '
                 f'<a href="{e(fb[1])}" target="_blank" rel="noopener">{e(fb[1])}</a></div>\n')
    if not ids:
        body += ('<div class="flag info"><b>No verified row for this sport on 22 October 2026</b>'
                 'Nothing could be confirmed on an official page, so nothing is published. '
                 'See the <a href="../coverage.html">coverage</a> and '
                 '<a href="../flagged.html">flag</a> pages.</div>\n')
    else:
        body += ('<div class="tw"><table><thead><tr><th>Start</th><th>Match / event</th><th>Competition</th>'
                 '<th>Match-winner call</th><th>Desk selection</th><th>Tier</th><th>Official source</th>'
                 '</tr></thead><tbody>\n')
        for rid in ids:
            r = ROWS[rid]
            sel, wc = r["selection"], r["winner_call"]
            if wc:
                wc_cell = f'{e(wc["selection"])} &middot; <span class="odds">{wc["price"]:.2f}</span>'
            else:
                wc_cell = "<span class='muted'>event card</span>"
            if sel:
                sel_cell = (f'{e(sel["selection"])}<br><span class="small muted">{e(sel["market"])}</span>'
                            f'<br><span class="odds">{sel["price"]:.2f} ({sel["us"]:+d})</span>')
                tier_cell = f'<span class="badge {badge(sel["confidence"])}">{e(sel["confidence"])}</span>'
            else:
                sel_cell, tier_cell = "<span class='badge x'>no bet</span>", "&mdash;"
            name = e(r["home"]) + (f' v {e(r["away"])}' if r["away"] else "")
            if r["venue"]:
                name += f'<br><span class="muted small">{e(r["venue"])}</span>'
            body += (f'<tr><td class="nowrap">{e(r["start_local"] or r["start_utc"] or "—")}</td>'
                     f'<td>{name}</td><td>{e(r["competition"])}</td><td>{wc_cell}</td>'
                     f'<td>{sel_cell}</td><td>{tier_cell}</td><td>{srcs(r, 2)}</td></tr>\n')
        body += "</tbody></table></div>\n"
    page(f"sports/{slug}.html", nname, body, f"{nname} — OLBG sport id {sid}")

body = ('<div class="tw"><table><thead><tr><th>Sport</th><th>OLBG id</th><th>Rows</th>'
        '<th>Live OLBG hub (upstream, measured not trusted)</th>'
        '<th>Official source read for this sport</th></tr></thead><tbody>\n')
for slug, nname, sid in SPORTS:
    ids = [r for r in ORDER if ROWS[r]["sport"] == slug]
    hub = next((h for h in HARV["in_scope"] if h["sport"] == slug), None)
    if ids:
        s0 = ROWS[ids[0]]["sources"][0]
        off = f'<a href="{e(s0["url"])}" target="_blank" rel="noopener">{e(s0["name"][:80])}</a>'
    else:
        fb = FALLBACK_SRC.get(slug)
        off = (f'<a href="{e(fb[1])}" target="_blank" rel="noopener">{e(fb[0][:80])}</a>' if fb
               else '<span class="muted">none read &mdash; see the flag register</span>')
    body += (f'<tr><td><a href="sports/{e(slug)}.html">{e(nname)}</a><br>'
             f'<span class="muted small">sports/{e(slug)}.html</span></td><td>{sid}</td><td>{len(ids)}</td>'
             f'<td><a href="{e(hub["hub"]) if hub else "#"}" target="_blank" rel="noopener">'
             f'{e(hub["hub"]) if hub else "—"}</a></td><td class="small">{off}</td></tr>\n')
body += "</tbody></table></div>"
page("sports.html", "17 Sports", body, "All 17 in-scope sports",
     "Soccer/football (1), horse racing (2), american football (11), boxing (16), cycling (17), "
     "specials/entertainment (18), hurling (26) and UFC/MMA are excluded by the brief and are enumerated on "
     "the <a href='reverse-engineering.html'>OLBG teardown</a> page rather than silently skipped.")

# =========================================================== COVERAGE =======
body = '<div class="tw"><table><thead><tr><th>Sport</th><th>OLBG cards seen</th><th>Verified rows</th>' \
       '<th>Priced rows</th><th>Outcome</th><th>What was and was not confirmed, with the official page</th>' \
       '</tr></thead><tbody>\n'
for c in COV["sports"]:
    hub = next((h for h in HARV["in_scope"] if h["sport"] == c["sport"]), None)
    ids = [r for r in ORDER if ROWS[r]["sport"] == c["sport"]]
    if ids:
        first_src, first_name = ROWS[ids[0]]["sources"][0]["url"], ROWS[ids[0]]["sources"][0]["name"]
    elif c["sport"] in FALLBACK_SRC:
        first_src, first_name = FALLBACK_SRC[c["sport"]][1], FALLBACK_SRC[c["sport"]][0]
    else:
        first_src, first_name = "", ""
    body += (f'<tr><td><a href="sports/{e(c["sport"])}.html">{e(SLUG[c["sport"]][1])}</a></td>'
             f'<td>{c["olbg_cards"]}</td><td>{c["verified_rows"]}</td><td>{c["priced_rows"]}</td>'
             f'<td>{e(c["outcome"])}</td><td>{e(c["detail"])} '
             + (f'<a href="{e(first_src)}" target="_blank" rel="noopener">{e(first_name[:78])}</a>'
                if first_src else '<span class="muted">no official page read &mdash; flagged</span>')
             + '</td></tr>\n')
body += f"""</tbody></table></div>
<h2>Excluded sports (by the brief)</h2>
<div class="tw"><table><thead><tr><th>Sport</th><th>OLBG id</th><th>Reason excluded</th>
<th>OLBG hub</th></tr></thead><tbody>
"""
for x in HARV["excluded"]:
    hub = x.get("hub", "")
    body += (f'<tr><td>{e(x["slug"])}</td><td>{x["olbg_id"] if x["olbg_id"] else "—"}</td>'
             f'<td>{e(x["reason"])}</td><td>'
             + (f'<a href="{e(hub)}" target="_blank" rel="noopener">{e(hub)}</a>' if hub else
                "no hub of its own - listed by OLBG inside the boxing and specials hubs") + "</td></tr>\n")
body += ("</tbody></table></div>"
         '<div class="panel small muted"><b>About the two tables above.</b> The OLBG hub links in the '
         'excluded-sport rows and in the sport index are the <i>measurement</i> being reported - what OLBG '
         'itself published on 22 October 2026 - not evidence for a fact. Where a row cites only an OLBG hub '
         'it is because no official governing-body page was read for that sport today; the validator prints '
         'those rows as notes and the reason is recorded on the '
         '<a href="flagged.html">Flagged for Review</a> page.</div>')
page("coverage.html", "Coverage", body, "What was harvested, what was verified, what was left blank",
     f'All 17 in-scope OLBG hubs were opened live on 2026-10-22 and {HARV["totals"]["cards_seen"]} upstream '
     f'cards were counted. A card is only counted as verified once the governing body&rsquo;s own page was '
     f'read; where that page was unreachable, the row is blank and flagged rather than inferred.')

# ======================================================= VERIFICATION =======
body = f"""<p class="lede">Per-row verification ledger: what was read, on which official page, on what date,
and what was deliberately left blank. {C['fixtures']} rows, {len(SRC['sources'])} distinct official URLs,
all read 2026-10-22. A row is marked <code>verified</code> only where a page was actually fetched and read
in this session; nothing here is carried forward from an earlier desk.</p>
<div class="tw"><table><thead><tr><th>Row</th><th>Sport</th><th>Inputs read on the official page</th>
<th>Left blank / refused</th><th>Status</th><th>Official source</th></tr></thead><tbody>
"""
for rid in ORDER:
    r = ROWS[rid]
    ev = "<ul class='tight'>" + "".join(
        f'<li><b>{e(x["label"])}:</b> {e(x["value"][:210])}</li>' for x in r["evidence"]) + "</ul>"
    blanks = "<ul class='tight'>" + "".join(
        f'<li><code>{e(f["code"])}</code> {e(f["text"][:230])}</li>' for f in r["flags"]) + "</ul>" \
        if r["flags"] else "<span class='muted'>nothing withheld on this row</span>"
    body += (f'<tr><td class="nowrap"><a href="picks.html#{e(rid)}">{e(rid)}</a><br>'
             f'<span class="small">{e(r["home"])}{(" v " + e(r["away"])) if r["away"] else ""}</span></td>'
             f'<td>{e(SLUG[r["sport"]][1])}</td><td class="small">{ev}</td><td class="small">{blanks}</td>'
             f'<td><span class="badge v">{e(r["status"])}</span></td><td>{srcs(r)}</td></tr>\n')
body += "</tbody></table></div>"
page("verification.html", "Verification", body, "Line-by-line verification ledger")

# ============================================================== AUDIT =======
body = f"""<p class="lede">Line-by-line review of the repository as it stands on this commit
({AUD['counts']['html_pages']} live HTML pages, {AUD['counts']['tracked_pyc']} tracked .pyc files,
{len(AUD['findings'])} findings). Every finding is either computed from a tracked file with the line number
printed, or a disagreement between a tracked value and an official page read today with that URL printed.
Nothing is asserted from memory.</p>
<div class="grid">
<div class="kpi"><b>{sum(1 for f in AUD['findings'] if f['severity']=='high')}</b><span>high severity</span></div>
<div class="kpi"><b>{sum(1 for f in AUD['findings'] if f['severity']=='medium')}</b><span>medium</span></div>
<div class="kpi"><b>{sum(1 for f in AUD['findings'] if f['severity']=='info')}</b><span>informational</span></div>
<div class="kpi"><b>{AUD['counts']['html_pages']}</b><span>live HTML pages</span></div>
</div>
"""
for f in AUD["findings"]:
    body += (f'<div class="flag {e(f["severity"])}"><b>{e(f["code"])} · {e(f["severity"].upper())} — '
             f'{e(f["title"])}</b>{e(f["text"])}'
             + ('<br><span class="small">Files: ' + ", ".join(f"<code>{e(x)}</code>" for x in f["files"]) + "</span>"
                if f["files"] else "")
             + (f'<br><span class="small">Official source: <a href="{e(f["source"])}" target="_blank" '
                f'rel="noopener">{e(f["source"])}</a></span>' if f["source"] else "")
             + "</div>\n")
body += "<h2>Desk row counts</h2><div class='tw'><table><thead><tr><th>Desk</th><th>Fixture rows</th>" \
        "<th>Where</th></tr></thead><tbody>"
for k, v in AUD["counts"]["desk_row_counts"].items():
    body += f"<tr><td>{e(k)}</td><td>{v}</td><td><code>data/</code></td></tr>"
body += "</tbody></table></div>"
page("audit.html", "Repo Audit", body, "Line-by-line repository audit with official-source cross-checks")

# ================================================== REVERSE ENGINEERING =====
body = f"""<p class="lede">OLBG's URL grammar and sport taxonomy, reconstructed from the live site and its
XML sitemap on 2026-10-22. {HARV['totals']['hubs_read']} in-scope hubs were opened directly; the excluded
sports are enumerated so the exclusion is auditable rather than assumed.</p>
<div class="panel">
<b>URL grammar.</b><br>
Hub: <code>{e(HARV['hub_pattern'])}</code><br>
Event: <code>{e(HARV['event_pattern'])}</code><br>
Sitemap: <code>https://www.olbg.com/sitemap-betting-tips.xml</code> — lists 22 sport hubs with
<code>lastmod</code> and <code>priority</code>; the Entertainment (18) and Hurling (26) routes answer HTTP
200 but are absent from it, which is how earlier sessions found them.
</div>
<h2>In-scope hubs, as read today</h2>
<div class="tw"><table><thead><tr><th>Sport</th><th>id</th><th>Cards seen</th><th>Hub URL</th>
<th>What the hub actually published</th></tr></thead><tbody>
"""
for h in HARV["in_scope"]:
    body += (f'<tr><td><a href="sports/{e(h["sport"])}.html">{e(SLUG[h["sport"]][1])}</a></td>'
             f'<td>{h["olbg_id"]}</td><td>{h["cards_seen"]}</td>'
             f'<td><a href="{e(h["hub"])}" target="_blank" rel="noopener">{e(h["hub"])}</a></td>'
             f'<td>{e(h["note"])}</td></tr>\n')
body += """</tbody></table></div>
<h2>Upstream defects found on OLBG itself</h2>
"""
for f in [x for x in FLG["flags"] if x["severity"] == "upstream"]:
    body += (f'<div class="flag med"><b>{e(f["id"])} — {e(f["title"])}</b>{e(f["text"])}<br>'
             f'<span class="small">Official source that settles it: <a href="{e(f["source"])}" '
             f'target="_blank" rel="noopener">{e(f["source"])}</a></span></div>\n')
body += """<div class="panel"><b>Known OLBG behaviours carried forward from the reverse-engineering record.</b>
<ul class="tight">
<li>Sport hubs truncate at roughly twenty cards, so a hub listing fewer events than the governing body
publishes is normal — snooker (2 of 8) and ice hockey (0 of 12 NHL games) are both truncation-plus-coverage
gaps, not evidence the fixtures do not exist.</li>
<li>Start times are printed with no timezone label and are silently localised to the reader's GeoIP, so a
clock scraped from a hub cannot be trusted as UTC. This desk stores the official body's own clock and leaves
<code>start_utc</code> blank where the governing body published only a local time.</li>
<li>Each-way-only outright markets render a <code>0 / 0 Win Tips</code> division-by-zero display, which is
why outright cards are treated as event cards here rather than as priced markets.</li>
</ul></div>"""
page("reverse-engineering.html", "OLBG Teardown", body, "OLBG.com reverse-engineered: taxonomy, URL grammar, upstream defects")

# ============================================================== FLAGGED =====
body = f"""<p class="lede">Everything this desk could not confirm on an official page, every irregularity
found in the repository or upstream, and every value deliberately left blank. Nothing on this page blocks
publication — it is published so it can be reviewed. {len(FLG['flags'])} register entries plus
{sum(len(r['flags']) for r in LN['rows'])} row-level flags.</p>
<h2>Flag register</h2>
"""
for f in FLG["flags"]:
    body += (f'<div class="flag {e(f["severity"])}" id="{e(f["id"])}"><b>{e(f["id"])} · '
             f'{e(f["severity"].upper())} · {e(f["sport"])} — {e(f["title"])}</b>{e(f["text"])}<br>'
             f'<span class="small">Source: <a href="{e(f["source"])}" target="_blank" rel="noopener">'
             f'{e(f["source"])}</a></span></div>\n')
body += '<h2>Row-level flags</h2><div class="tw"><table><thead><tr><th>Row</th><th>Code</th>' \
        '<th>What is blank or refused, and why</th><th>Official source</th></tr></thead><tbody>\n'
for rid in ORDER:
    r = ROWS[rid]
    for fl in r["flags"]:
        body += (f'<tr><td class="nowrap"><a href="picks.html#{e(rid)}">{e(rid)}</a><br>'
                 f'<span class="small">{e(r["home"])}</span></td><td><code>{e(fl["code"])}</code></td>'
                 f'<td>{e(fl["text"])}</td><td>{srcs(r, 1)}</td></tr>\n')
body += "</tbody></table></div>"
page("flagged.html", "Flagged for Review", body, "Flagged for Review — every unverified value and irregularity",
     "Left blank rather than filled in. Each entry names the official page that was tried and what it did or "
     "did not publish.")

# ============================================================= SOURCES =====
body = f"""<p class="lede">{len(SRC['sources'])} official URLs, every one fetched and read on 2026-10-22.
Governing bodies, tours, federations, leagues and the clubs themselves only. Media outlets, aggregators,
tipster sites and Wikipedia were never used to verify a fact; OLBG is listed only as the upstream whose
coverage is being measured.</p>
<div class="tw"><table><thead><tr><th>#</th><th>What it is</th><th>URL</th></tr></thead><tbody>
"""
for i, s in enumerate(SRC["sources"], 1):
    body += (f'<tr><td>{i}</td><td>{e(s["name"])}</td>'
             f'<td><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["url"])}</a></td></tr>\n')
body += "</tbody></table></div>"
page("sources.html", "Official Sources", body, "Official source register — read 2026-10-22")

# ========================================================== METHODOLOGY =====
POL = LN["policy"]
body = f"""<p class="lede">How every price on this desk was produced, and which numbers are sourced facts
versus labelled modelling choices.</p>
<h2>1. The five rules</h2>
<div class="panel"><ul class="tight">
<li><b>Official sources only.</b> A fixture, record or ranking counts once it has been read on the governing
body, tour, federation, league or club's own page. {len(SRC['sources'])} such pages were read on
2026-10-22.</li>
<li><b>Blank beats wrong.</b> Any value not read on an official page is left empty and flagged — see
<a href="flagged.html">Flagged for Review</a>.</li>
<li><b>Assumptions are labelled.</b> Home-advantage constants, spread values and format assumptions are
printed in full below and repeated in every market's basis string. They are never presented as
statistics.</li>
<li><b>One-sided ratings are refused.</b> Where only one participant has a sourced input the line falls back
to a neutral baseline and confidence is capped at Low. That is why the four RLWC2026 fixtures, both NBA
games, the EHF Kolstad tie and two cricket rows carry no High pick here.</li>
<li><b>Every High pick gets its own written preview</b> — 30 words minimum, naming the side, its form and
its recent results, and the selection itself.</li>
</ul></div>

<h2>2. Line origination and the price window</h2>
<div class="panel">
The originated line is the <b>zero-vig fair price</b>, <code>1 / p</code>. The 5% book-equivalent
<code>1 / (1.05 p)</code> is printed beside it for comparison only.<br><br>
<b>Why zero vig.</b> At a 5% overround a 70% chance prices at 1.3606 (−277), already through the brief's
−250 floor, so "above 70%" and "inside −250…+10000" cannot both bind on a margined line. At zero vig,
0.700 prices at −233 and 0.7143 prices at exactly −250, so the two rules are jointly satisfiable in the
band <b>0.700 ≤ p ≤ 0.7143</b>. This desk tests the window against the fair price and publishes the
margined equivalent next to it. Recorded as <a href="flagged.html">F-F7-01</a>.<br><br>
<b>High confidence requires all four:</b> row status <code>verified</code> · a sourced rating on both sides ·
model probability ≥ 0.700 · fair price inside −250…+10000.<br>
<b>Medium</b> = in-window and ≥ 0.55. <b>Low</b> = in-window and ≥ 0.52, or any row whose ratings are
one-sided. <b>No bet</b> = nothing in-window reaches 0.52.<br>
<b>Rung choice:</b> among in-window rungs at or above 0.700 the <i>tightest</i> line wins, not the highest
probability — a 71% call on a 3.5-point handicap is a real bet, a 71% call on a 66.5-point alternate is an
artefact of the ladder. No model-calibrated alternate lines are generated.
</div>

<h2>3. Labelled modelling constants (choices, not statistics)</h2>
<div class="tw"><table><thead><tr><th>Constant</th><th>Value</th><th>What it does</th></tr></thead><tbody>
"""
DESC = {
    "nhl_hfa": "goals of home ice added to the expected margin",
    "nhl_sigma": "goal spread used to turn an expected margin into a probability",
    "nhl_ppg_k": "goals per 1.000 of official points-per-game difference",
    "mlb_hfa": "runs of home-field advantage",
    "mlb_sigma": "run spread for the margin market",
    "mlb_sigma_total": "run spread for the total market",
    "nba_hfa": "home-court edge expressed as a fraction of the spread",
    "nba_sigma": "point spread for basketball margins",
    "el_k": "points per 1.000 of EuroLeague win percentage",
    "el_hfa": "points of home court in the EuroLeague",
    "el_sigma": "point spread for EuroLeague margins",
    "ru_sigma": "point spread used to convert LNR's published win probability back into a margin",
    "gaa_sigma": "point spread for Gaelic county finals",
    "aflw_sigma": "point spread for AFLW margins",
    "aflw_scale": "shrink applied to the ladder-derived margin, calibrated against the two Round 10 margins read on AFL.com.au (51 and 53 points)",
    "hb_h2h_shrink": "shrink applied to a single verified head-to-head goal margin",
    "hb_hfa": "goals of home court in handball",
    "hb_sigma": "goal spread for handball margins",
    "neutral_hfa": "home edge applied when a strength edge is refused under rule 4",
    "neutral_sigma": "spread used with the neutral baseline",
    "darts_seed_k": "per-leg probability per seed position of gap",
    "darts_oom_k": "per-leg probability weight on the Order of Merit gap",
    "darts_legs_to_win": "FORMAT ASSUMPTION — legs needed to win a Round One tie",
    "snooker_top16": "per-frame edge for a verified world top-16 player",
    "snooker_frames_to_win": "FORMAT ASSUMPTION — frames needed to win a Round 3 tie",
}
for k, v in POL["constants"].items():
    body += f'<tr><td><code>{e(k)}</code></td><td class="odds">{v}</td><td>{e(DESC.get(k, ""))}</td></tr>\n'
body += """</tbody></table></div>

<h2>4. Markets investigated, and which are priced</h2>
<div class="panel">
<b>Priced:</b> match winner (or draw-no-bet where the competition can level), handicap ladders on the
sport's own unit — goals, points, runs, frames, legs — and match totals for the NHL and MLB only, because
those are the only competitions where both sides' scoring rates were read on an official page.<br><br>
<b>Investigated, not priced</b> (missing official input named per sport on the
<a href="coverage.html">coverage</a> page): match totals everywhere else; correct score and frame/set score;
first-set, first-try, first-touchdown and player props; golf, Formula 1 and eSports outrights. Each is left
blank with the exact missing input recorded rather than filled from a league-average constant.<br><br>
<b>Rejected rungs:</b> any handicap rung whose model probability falls outside 5%–95% is dropped, so no
degenerate price is published on either side of a mismatch.
</div>

<h2>5. Sport ladders</h2>
<div class="tw"><table><thead><tr><th>Sport</th><th>Handicap rungs</th><th>Unit</th><th>Total rungs</th>
</tr></thead><tbody>
"""
for slug, nname, _ in SPORTS:
    lad = POL["ladders"].get(slug)
    if lad is None:
        continue
    tot = POL["total_ladders"].get(slug)
    body += (f'<tr><td>{e(nname)}</td><td class="small">{e(", ".join(str(x) for x in lad))}</td>'
             f'<td>{e(POL["units"].get(slug, "—"))}</td>'
             f'<td class="small">{e(", ".join(str(x) for x in tot)) if tot else "not priced — see flag"}</td>'
             f'</tr>\n')
body += f"""</tbody></table></div>

<h2>6. What this desk does not claim</h2>
<div class="panel">No remote page is re-read by the validator. Verification is recorded per row
(<code>status</code>, <code>sources</code>, <code>evidence</code>) and the gate checks structure,
arithmetic, provenance and links — not the live web. Prices are model output at zero vig, not market prices
and not betting advice. {C['prices']:,} originated prices are estimates built from published records,
standings, seedings and results.</div>
"""
page("methodology.html", "Methodology", body, "Methodology, constants and the price-window policy")

print(f"f71557b5 site: {len(list(SITE.rglob('*.html')))} pages written to f71557b5/")
