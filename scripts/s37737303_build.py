# -*- coding: utf-8 -*-
"""Build the 37737303 desk: a small, linear dashboard.

Pages
    index.html            executive summary, the picks, and where everything lives
    picks.html            every pick, grouped by sport
    predictions.html      the written predictions
    matches.html          every fixture, with our price on every market investigated
    markets.html          every market line we originated
    sports/<slug>.html    one page per brief sport
    sources.html          every page read, and every page that refused
    flagged.html          the review queue
    methodology.html      how the numbers were made
    olbg.html             what OLBG exposes and how it was read
    repo-audit.html       line-by-line review of this repository
"""
from __future__ import annotations

import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "37737303"
OUT = ROOT / "37737303"

SPORTS = [
    ("golf", "Golf"), ("volleyball", "Volleyball"), ("rugby-union", "Rugby Union"),
    ("cricket", "Cricket"), ("snooker", "Snooker"), ("darts", "Darts"),
    ("baseball", "Baseball"), ("gaelic-sports", "Gaelic Sports"), ("greyhounds", "Greyhounds"),
    ("tennis", "Tennis"), ("motor-racing", "Motor Racing"), ("handball", "Handball"),
    ("ice-hockey", "Ice Hockey"), ("basketball", "Basketball"), ("rugby-league", "Rugby League"),
]
SPORT_LABEL = dict(SPORTS)

CSS = """
:root{--ink:#132019;--muted:#5d6f65;--line:#dfe6e1;--bg:#f5f7f5;--card:#fff;
--green:#0d6b45;--green-soft:#e6f2ec;--amber:#8a5300;--amber-soft:#fdf2de;--red:#8f2f2f;--red-soft:#fbeaea;--blue:#1d4f8a;--blue-soft:#e8eff8}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--green)}
h1,h2,h3{line-height:1.2;margin:0 0 10px}
h1{font-size:31px;letter-spacing:-.4px}h2{font-size:22px}h3{font-size:17px}
p{margin:0 0 12px}
.small{font-size:13px}.muted{color:var(--muted)}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:9}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.toprow{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:11px 0;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700}
.brand .mark{width:30px;height:30px;border-radius:9px;background:var(--green);color:#fff;display:grid;place-items:center;font-size:13px;font-weight:800}
.brand small{display:block;font-weight:500;font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
nav.main{display:flex;gap:4px;flex-wrap:wrap;padding:0 0 9px}
nav.main a{padding:6px 11px;border-radius:999px;text-decoration:none;color:var(--muted);font-size:14px;border:1px solid transparent}
nav.main a.active{background:var(--green-soft);color:var(--green);border-color:#cbe1d6;font-weight:600}
nav.main a:hover{border-color:var(--line)}
.hero{background:linear-gradient(180deg,#fff,#fbfdfb);border:1px solid var(--line);border-radius:16px;padding:22px 24px;margin:20px 0}
.hero h1{margin-bottom:6px}
.hero .kicker{font-size:12px;letter-spacing:.11em;text-transform:uppercase;color:var(--green);font-weight:700;margin-bottom:8px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0 4px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.kpi b{display:block;font-size:24px;line-height:1.1}
.kpi small{color:var(--muted);font-size:12px}
.panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:18px 0}
.panel h2{margin-top:0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.card{display:block;background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px;text-decoration:none;color:var(--ink)}
.card b{display:block;margin-bottom:4px;color:var(--green)}
.card small{color:var(--muted)}
.card:hover{border-color:#bcd6c8}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:9px 11px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f3f7f4;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fafcfb}
.pick{font-weight:700}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.badge.high{background:var(--green-soft);color:var(--green)}
.badge.medium{background:var(--blue-soft);color:var(--blue)}
.badge.low{background:#eef0ef;color:#5d6f65}
.badge.flag{background:var(--amber-soft);color:var(--amber)}
.badge.pass{background:var(--red-soft);color:var(--red)}
.num{font-variant-numeric:tabular-nums;font-weight:600}
.tagt{display:inline-block;font-size:11px;padding:2px 7px;border-radius:6px;background:#eef2f0;color:#41564b;margin:1px 3px 1px 0}
.lede{font-size:16.5px;color:#31463b}
.jump{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0 18px}
.jump a{font-size:13px;padding:5px 10px;border:1px solid var(--line);border-radius:999px;text-decoration:none;background:#fff;color:#33463c}
article.pred{border:1px solid var(--line);background:#fff;border-radius:14px;padding:18px 20px;margin:16px 0}
article.pred h3{margin-bottom:4px}
.predmeta{font-size:13px;color:var(--muted);margin-bottom:10px}
.predbody{font-size:16px}
.facts{margin:12px 0 0;padding:12px 14px;background:#f7faf8;border:1px dashed var(--line);border-radius:10px}
.facts li{margin:4px 0}
footer{border-top:1px solid var(--line);margin-top:34px;padding:20px 0 40px;color:var(--muted);font-size:13px}
.note{border-left:4px solid var(--green);background:var(--green-soft);padding:12px 16px;border-radius:0 10px 10px 0;margin:14px 0}
.warn{border-left:4px solid var(--amber);background:var(--amber-soft);padding:12px 16px;border-radius:0 10px 10px 0;margin:14px 0}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}
.srclink{white-space:nowrap}
.crumb{font-size:13px;color:var(--muted);margin:16px 0 0}
.crumb a{text-decoration:none}
"""

NAV = [("index.html", "Summary"), ("picks.html", "Picks"), ("predictions.html", "Write-ups"),
       ("matches.html", "Matches"), ("markets.html", "Markets"), ("sports.html", "Sports"),
       ("flagged.html", "Review queue"), ("sources.html", "Sources"), ("methodology.html", "Method"),
       ("olbg.html", "OLBG"), ("repo-audit.html", "Repo audit")]


def esc(x) -> str:
    return html.escape("" if x is None else str(x))


def dec(p: float) -> str:
    return f"{p*100:.1f}%"


def load():
    get = lambda n: json.loads((DATA / n).read_text(encoding="utf-8"))
    return (get("sources.json"), get("fixtures.json"), get("flags.json"),
            get("olbg.json"), get("coverage.json"), get("predictions.json"))


def link_src(source_id, sources) -> str:
    s = next((x for x in sources["sources"] if x["id"] == source_id), None)
    if not s:
        return '<span class="small muted">no source</span>'
    label = "OLBG" if s["kind"] == "discovery" else s["publisher"]
    return (f'<a class="srclink" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(label)}'
            f'<span aria-hidden="true"> &#8599;</span></a>')


def head(title: str, page: str, prefix: str = "") -> str:
    nav = "".join(
        f'<a class="{"active" if href == page else ""}" href="{prefix}{href}">{esc(label)}</a>'
        for href, label in NAV)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG 15-sport desk · 24 October 2026</title>
<style>{CSS}</style></head><body>
<header class="top"><div class="wrap">
<div class="toprow"><a class="brand" href="{prefix}index.html"><span class="mark">OL</span>
<span>OLBG 15-sport desk<small>Session 37737303 · 24 Oct 2026</small></span></a>
<span class="small muted">Sources read 22:35–23:10Z · UTC</span></div>
<nav class="main">{nav}</nav></div></header><main class="wrap">"""


def foot() -> str:
    return """</main><footer><div class="wrap">
<p><strong>What this page is.</strong> Our own prices, our own picks and our own write-ups for the fifteen sports
the brief names. OLBG is used to find which events carry a live market and to see what its crowd is backing;
it is never treated as an official source. Every factual claim links to the governing body, league, tour or
promoter page it came from. Values we could not confirm are blank and listed on the
<a href="flagged.html">review queue</a>.</p>
<p class="small">Prices are estimates, not quotes, and a pick is an opinion, not a guarantee. 18+. If gambling
stops being fun, GambleAware and GamCare offer free support.</p>
</div></footer></body></html>"""


ROOT_PAGES = re.compile(
    r'href="(index|picks|predictions|matches|markets|sports|flagged|sources|methodology|olbg|repo-audit)\.html')


def page(path: Path, title: str, nav: str, body: str, prefix: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    page_html = head(title, nav, prefix) + body + foot()
    if prefix:
        page_html = page_html.replace('href="index.html"', f'href="{prefix}index.html"')
        page_html = ROOT_PAGES.sub(lambda m: f'href="{prefix}{m.group(1)}.html"', page_html)
    path.write_text(page_html, encoding="utf-8")


def source_cell(f, sources) -> str:
    """One source cell per row: the official page when there is one, otherwise an
    honest note that the only input was OLBG's crowd, plus the market link."""
    src = sources.get("sources") and next((x for x in sources["sources"] if x["id"] == f["official_source"]), None)
    market = (f'<a href="{esc(f["olbg_url"])}" target="_blank" rel="noopener noreferrer">'
              f'OLBG market<span aria-hidden="true"> &#8599;</span></a>')
    if src and src["kind"] == "official":
        return link_src(f["official_source"], sources) + "<br>" + market
    return '<span class="muted">no official page; OLBG crowd only</span><br>' + market


def conf_badge(f) -> str:
    """Confidence badge. Rows whose fair price falls outside the brief's band are
    marked 'passed' instead of being dressed up as a low-confidence opinion."""
    if not f["pick"]["in_band"]:
        return '<span class="badge pass">passed &middot; price outside band</span>'
    return f'<span class="badge {f["confidence"]}">{f["confidence"]}</span>'


def pick_rows(rows, sources, with_sport=True, anchor_prefix=""):
    out = []
    for f in rows:
        p = f["pick"]
        badge = conf_badge(f)
        band = "" if p["in_band"] else ' <span class="badge pass">outside band</span>'
        sport = f'<td class="small">{esc(SPORT_LABEL.get(f["sport"], f["sport"]))}</td>' if with_sport else ""
        out.append(
            f'<tr id="{esc(anchor_prefix+f["id"])}">{sport}'
            f'<td><strong>{esc(f["away"])}</strong> at <strong>{esc(f["home"])}</strong>'
            f'<br><span class="small muted">{esc(f["competition"])} · {esc(f["start_label"])}</span></td>'
            f'<td class="pick">{esc(p["selection"])}'
            f'<br><span class="small muted">{esc(p["market"])}{" " + str(p["line"]) if p["line"] else ""}</span></td>'
            f'<td><span class="num">{p["fair"]:+d}</span><br><span class="small muted">{dec(p["prob"])} · {p["decimal"]}</span>{band}</td>'
            f'<td>{badge}</td>'
            f'<td class="small">{source_cell(f, sources)}</td>'
            f'</tr>')
    return "".join(out)


def source_block(f, sources, limit=2):
    items = []
    for fact in f["facts"][:limit]:
        items.append(f'<li>{esc(fact["text"])} — {link_src(fact["source"], sources)}</li>')
    if not items:
        return ('<p class="small muted">No official page for this fixture was readable this session, so no '
                'fact is asserted. The basis of the price is stated on the row.</p>')
    return '<ul class="facts small">' + "".join(items) + "</ul>"


def build_index(rows, sources, coverage, flags):
    high = [r for r in rows if r["confidence"] == "high"]
    med = [r for r in rows if r["confidence"] == "medium"]
    c = coverage["counts"]
    body = f"""
<div class="hero">
<div class="kicker">Executive summary · 24–26 October 2026 · all times as OLBG shows them</div>
<h1>Fifteen sports, {c['fixtures']} fixtures, {c['picks']} picks — and every pick is on this screen.</h1>
<p class="lede">The short version: <strong>{c['high']} High picks</strong> are listed immediately below with the page
and row where their write-up sits. The other {c['medium'] + c['low']} picks follow, grouped by confidence, then by
sport. Three of the fifteen brief sports had <strong>no bettable market at all</strong> on OLBG when the hubs were
read at 22:40Z — golf, snooker and motor racing — and they are named rather than padded.</p>
<div class="kpis">
<div class="kpi"><b>{c['high']}</b><small>High-confidence picks</small></div>
<div class="kpi"><b>{c['medium']}</b><small>Medium</small></div>
<div class="kpi"><b>{c['low']}</b><small>Low</small></div>
<div class="kpi"><b>{c['picks']}</b><small>Picks in total</small></div>
<div class="kpi"><b>{c['predictions']}</b><small>Written predictions (30+ words)</small></div>
<div class="kpi"><b>{c['markets']}</b><small>Lines we originated</small></div>
<div class="kpi"><b>{c['sports_with_picks']} / 15</b><small>Sports with a live market</small></div>
<div class="kpi"><b>{c['flags']}</b><small>Items on the review queue</small></div>
</div>
</div>

<div class="panel" id="high">
<h2>1. The High-confidence picks</h2>
<p>These are the two selections where our own numbers, an official page read this session, and the brief's
&minus;250 to +10000 price band all line up. The <em>Where</em> column is the exact page and row of the full
write-up.</p>
<div class="table-wrap"><table>
<thead><tr><th>Where the pick lives</th><th>Sport</th><th>Match</th><th>Our pick</th><th>Our fair price</th><th>Confidence</th><th>Source</th></tr></thead>
<tbody>{''.join(
  f'<tr><td class="small"><a href="predictions.html#{esc(r["id"])}">predictions.html#{esc(r["id"])}</a><br>'
  f'<a class="small" href="picks.html#{esc(r["id"])}">picks.html#{esc(r["id"])}</a></td>'
  f'<td class="small">{esc(SPORT_LABEL[r["sport"]])}</td>'
  f'<td><strong>{esc(r["away"])}</strong> at <strong>{esc(r["home"])}</strong><br>'
  f'<span class="small muted">{esc(r["competition"])} · {esc(r["start_label"])}</span></td>'
  f'<td class="pick">{esc(r["pick"]["selection"])}<br><span class="small muted">{esc(r["pick"]["market"])}</span></td>'
  f'<td><span class="num">{r["pick"]["fair"]:+d}</span><br><span class="small muted">{dec(r["pick"]["prob"])}</span></td>'
  f'<td><span class="badge high">high</span></td>'
  f'<td class="small">{link_src(r["official_source"], sources)}</td></tr>' for r in high)}</tbody></table></div>
<p class="small muted" style="margin-top:10px">Why only two? The band caps a High pick at a fair price no shorter
than &minus;250, which is a 71.4% implied chance, so a team our numbers make a heavy favourite fails the band rather
than the analysis. Boston (&minus;291) and Edmonton (&minus;358) are the clearest examples: both are marked
<em>passed on the band</em> and their puck lines are offered instead. The full arithmetic is on
<a href="methodology.html">Method</a>.</p>
</div>

<div class="panel">
<h2>2. Where everything is</h2>
<div class="cards">
<a class="card" href="picks.html"><b>Picks &rarr;</b><small>All {c['picks']} selections, one row each, grouped by sport.</small></a>
<a class="card" href="predictions.html"><b>Written predictions &rarr;</b><small>{c['predictions']} full write-ups, 30 words or more, each naming its selection.</small></a>
<a class="card" href="matches.html"><b>Every match &rarr;</b><small>{c['fixtures']} fixtures with our price on every market we investigated.</small></a>
<a class="card" href="markets.html"><b>Markets &rarr;</b><small>{c['markets']} originated lines: winner, handicap, total and outright.</small></a>
<a class="card" href="sports.html"><b>Sports &rarr;</b><small>Sport by sport, including the three with no market.</small></a>
<a class="card" href="flagged.html"><b>Review queue &rarr;</b><small>{c['flags']} items where data was missing or a rule needed a decision.</small></a>
<a class="card" href="sources.html"><b>Sources &rarr;</b><small>Every official page read, plus every page that refused.</small></a>
<a class="card" href="olbg.html"><b>Inside OLBG &rarr;</b><small>Hub routes, sport ids and the quirks we hit reading them.</small></a>
</div>
</div>

<div class="panel">
<h2>3. Also issued today, at medium confidence</h2>
<p>{len(med)} selections. Each has an official or publisher input behind it, but the price is closer to a coin
flip than the two above.</p>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th>Match</th><th>Our pick</th><th>Our fair price</th><th>Confidence</th><th>Source</th></tr></thead>
<tbody>{pick_rows(med, sources)}</tbody></table></div>
</div>

<div class="panel">
<h2>4. The rest of the board, at low confidence</h2>
<p class="lede">The remaining {c['low']} picks are published because the brief asks for five or more per sport, but
they are honestly labelled: most rest on OLBG's crowd split alone, because no official form page for those
fixtures could be read. Nothing on this list is dressed up as analysis it does not have.</p>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th>Match</th><th>Our pick</th><th>Our fair price</th><th>Confidence</th><th>Source</th></tr></thead>
<tbody>{pick_rows([r for r in rows if r['confidence']=='low'], sources)}</tbody></table></div>
</div>

<div class="panel">
<h2>5. Coverage against the brief</h2>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th>Fixtures</th><th>Picks</th><th>High</th><th>Medium</th><th>Low</th><th>Write-ups</th><th>Page</th><th>Market status</th></tr></thead>
<tbody>{''.join(
  f'<tr><td><strong>{esc(SPORT_LABEL[s["sport"]])}</strong></td><td class="num">{s["fixtures"]}</td>'
  f'<td class="num">{s["picks"]}</td><td class="num">{s["high"]}</td><td class="num">{s["medium"]}</td>'
  f'<td class="num">{s["low"]}</td><td class="num">{s["written"]}</td>'
  f'<td><a href="sports/{esc(s["sport"])}.html">open</a></td>'
  f'<td class="small">{esc(next((n["finding"][:96]+"…" for n in coverage["no_market"] if n["sport"]==s["sport"]), "live market on OLBG"))}</td></tr>'
  for s in coverage["sports"])}</tbody></table></div>
</div>
"""
    page(OUT / "index.html", "Executive summary", "index.html", body)


def build_picks(rows, sources, coverage):
    blocks = []
    for slug, label in SPORTS:
        sub = [r for r in rows if r["sport"] == slug]
        if not sub:
            nom = next((n for n in coverage["no_market"] if n["sport"] == slug), None)
            blocks.append(f"""<div class="panel" id="{slug}"><h2>{label}</h2>
<div class="warn"><strong>No bettable market.</strong> {esc(nom['finding']) if nom else ''}
The hub we read was <a href="{esc(nom['hub']) if nom else '#'}" target="_blank" rel="noopener noreferrer">OLBG {label}<span aria-hidden="true"> &#8599;</span></a>.</div></div>""")
            continue
        blocks.append(f"""<div class="panel" id="{slug}"><h2>{label} — {len(sub)} pick{'s' if len(sub)!=1 else ''}</h2>
<div class="table-wrap"><table>
<thead><tr><th>Match</th><th>Our pick</th><th>Our fair price</th><th>Confidence</th><th>Basis</th><th>Source</th></tr></thead>
<tbody>{pick_rows(sub, sources, with_sport=False)}</tbody></table></div>
<p class="small"><a href="sports/{slug}.html">Open the {label} page &rarr;</a></p></div>""")
    jump = "".join(f'<a href="#{s}">{esc(l)}</a>' for s, l in SPORTS)
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Picks</div>
<h1 style="margin-top:10px">Every pick, grouped by sport</h1>
<p class="lede">One row per selection. The <em>Our fair price</em> column is the zero-margin American price our own
numbers imply; the confidence column says how much evidence stands behind it. Where a price falls outside the
brief's &minus;250 to +10000 band it is marked, and the reason is on the row's match page.</p>
<div class="note small"><strong>Reading the rows.</strong>
<span class="badge high">high</span> our strongest view, official form read, and a price inside the band ·
<span class="badge medium">medium</span> same discipline, closer call or thinner evidence ·
<span class="badge low">low</span> the only input is OLBG's crowd, so it is published but not recommended ·
<span class="badge pass">passed &middot; price outside band</span> our view is strong but the fair price is shorter
than the brief's &minus;250 floor, so the pick does not qualify.</div>
<div class="jump">{jump}</div>
{''.join(blocks)}"""
    page(OUT / "picks.html", "Picks", "picks.html", body)


def build_predictions(rows, sources):
    ps = [r for r in rows if r["prediction"]]
    order = {s: i for i, (s, _) in enumerate(SPORTS)}
    rank = {"high": 0, "medium": 1, "low": 2}
    ps.sort(key=lambda r: (rank.get(r["confidence"], 3), order.get(r["sport"], 99), r["id"]))
    arts = []
    for r in ps:
        p = r["pick"]
        arts.append(f"""<article class="pred" id="{esc(r['id'])}">
<h3>{esc(r['away'])} at {esc(r['home'])}</h3>
<div class="predmeta">{esc(SPORT_LABEL[r['sport']])} · {esc(r['competition'])} · {esc(r['start_label'])} ·
selection <strong>{esc(p['selection'])}</strong> ({esc(p['market'])}) at <span class="num">{p['fair']:+d}</span> ·
<span class="badge {r['confidence']}">{r['confidence']}</span> · {len(r['prediction'].split())} words</div>
<p class="predbody">{esc(r['prediction'])}</p>
{source_block(r, sources, limit=4)}
<p class="small" style="margin-top:10px">Market on OLBG: <a href="{esc(r['olbg_url'])}" target="_blank" rel="noopener noreferrer">open the event page<span aria-hidden="true"> &#8599;</span></a></p>
</article>""")
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Written predictions</div>
<h1 style="margin-top:10px">{len(ps)} written predictions</h1>
<p class="lede">Each of these is at least 30 words, names the selection and the price, and is built only from
facts printed on the official page linked underneath it. The other {len(rows)-len(ps)} picks on the board are
listed with a basis line but no essay, because there was no official fact to write about — padding them out
would have meant inventing detail.</p>
{''.join(arts)}"""
    page(OUT / "predictions.html", "Written predictions", "predictions.html", body)


def build_matches(rows, sources):
    order = {s: i for i, (s, _) in enumerate(SPORTS)}
    rows = sorted(rows, key=lambda r: (order.get(r["sport"], 99), r["start_label"] or ""))
    out = []
    for r in rows:
        def _band(m):
            return ('<span class="badge pass">outside band</span>'
                    if not (-250 <= m["fair"] <= 10000) else "")
        mk = "".join(
            f'<tr><td>{esc(m["market"])}{" " + str(m["line"]) if m["line"] else ""}</td>'
            f'<td>{esc(m["side"])}</td><td class="num">{m["fair"]:+d}</td>'
            f'<td class="num">{dec(m["prob"])}</td><td class="num">{m["decimal"]}</td>'
            f'<td>{_band(m)}</td></tr>'
            for m in r["markets"])
        out.append(f"""<div class="panel" id="{esc(r['id'])}">
<h2>{esc(r['away'])} at {esc(r['home'])} {conf_badge(r)}</h2>
<p class="small muted">{esc(SPORT_LABEL[r['sport']])} · {esc(r['competition'])} ·
<span class="tagt">as OLBG shows it: {esc(r['start_label'])}</span>
{'<span class="tagt">official start ' + esc(r['start_utc']) + '</span>' if r['start_utc'] else '<span class="tagt">no official start time read</span>'}
{'<span class="tagt">' + esc(r['venue']) + '</span>' if r['venue'] else ''}
<span class="tagt">evidence: {esc(r['evidence'])}</span></p>
<p><strong>Our pick:</strong> {esc(r['pick']['selection'])} ({esc(r['pick']['market'])}) at
<span class="num">{r['pick']['fair']:+d}</span> — {dec(r['pick']['prob'])} chance.
<span class="small muted">OLBG crowd for context: {esc(r['olbg_tip'])}.</span></p>
{source_block(r, sources, limit=3)}
<div class="table-wrap" style="margin-top:12px"><table>
<thead><tr><th>Market</th><th>Selection</th><th>Our price</th><th>Our chance</th><th>Decimal</th><th>Band</th></tr></thead>
<tbody>{mk}</tbody></table></div>
<p class="small" style="margin-top:10px"><a href="{esc(r['olbg_url'])}" target="_blank" rel="noopener noreferrer">OLBG event page<span aria-hidden="true"> &#8599;</span></a>
{' · <a href="predictions.html#' + esc(r['id']) + '">read the write-up</a>' if r['prediction'] else ''}</p>
</div>""")
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Matches</div>
<h1 style="margin-top:10px">Every match, with every line we originated</h1>
<p class="lede">{len(rows)} fixtures. For each one: when OLBG says it starts, the official start where we could
read one, the facts we could confirm, and our price on each market we investigated. Markets we did not price are
explained on <a href="markets.html">Markets</a>.</p>
{''.join(out)}"""
    page(OUT / "matches.html", "Matches", "matches.html", body)


def build_markets(rows, coverage):
    by_market = {}
    for r in rows:
        for m in r["markets"]:
            by_market.setdefault(m["market"], []).append((r, m))
    blocks = []
    for name in sorted(by_market):
        items = by_market[name]
        rows_html = "".join(
            f'<tr><td>{esc(r["away"])} at {esc(r["home"])}<br><span class="small muted">{esc(SPORT_LABEL[r["sport"]])}</span></td>'
            f'<td>{esc(m["side"])}{" " + str(m["line"]) if m["line"] else ""}</td>'
            f'<td class="num">{m["fair"]:+d}</td><td class="num">{dec(m["prob"])}</td><td class="num">{m["decimal"]}</td></tr>'
            for r, m in items)
        blocks.append(f"""<div class="panel"><h2>{esc(name)} — {len(items)} lines</h2>
<div class="table-wrap"><table><thead><tr><th>Match</th><th>Selection</th><th>Our price</th><th>Our chance</th><th>Decimal</th></tr></thead>
<tbody>{rows_html}</tbody></table></div></div>""")
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Markets</div>
<h1 style="margin-top:10px">The markets we investigated, and the ones we withheld</h1>
<p class="lede">Every line here is ours: a zero-margin conversion of our own probability estimate. No bookmaker
price was copied. Four markets are covered across the board — match winner, handicap or puck line, match total,
and outright.</p>

<div class="panel"><h2>Which markets we price, by sport</h2>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th>Match winner</th><th>Handicap / spread</th><th>Match total</th><th>Outright</th><th>Reason where withheld</th></tr></thead>
<tbody>
<tr><td>Ice Hockey</td><td>yes</td><td>yes (puck line, where both records exist)</td><td>yes (where both records exist)</td><td>no</td><td>Totals need both clubs' goals for and against; six fixtures had only one side.</td></tr>
<tr><td>Tennis</td><td>yes</td><td>no</td><td>no</td><td>no</td><td>No set or game handicap was priced without a match-level scoring input.</td></tr>
<tr><td>Baseball</td><td>yes</td><td>yes (run line)</td><td>yes</td><td>no</td><td>Only one game is on the board.</td></tr>
<tr><td>Cricket</td><td>yes</td><td>no</td><td>no</td><td>no</td><td>No board page read, so run lines and totals are withheld.</td></tr>
<tr><td>Gaelic Sports</td><td>yes</td><td>yes (as listed by OLBG)</td><td>no</td><td>yes</td><td>Scoring totals withheld: no official scoreline data.</td></tr>
<tr><td>Handball</td><td>no</td><td>yes</td><td>no</td><td>no</td><td>Handicap only, because only the fixture is official.</td></tr>
<tr><td>Volleyball</td><td>yes</td><td>no</td><td>no</td><td>no</td><td>Set handicaps withheld without a set-level input.</td></tr>
<tr><td>Basketball</td><td>yes</td><td>no</td><td>no</td><td>no</td><td>Spreads and totals withheld: the NBA feed returned HTTP 500.</td></tr>
<tr><td>Darts</td><td>yes</td><td>no</td><td>yes (180s)</td><td>yes</td><td>Leg handicaps withheld without a PDC draw.</td></tr>
<tr><td>Rugby Union</td><td>yes</td><td>no</td><td>no</td><td>yes</td><td>Handicaps withheld: no league page read.</td></tr>
<tr><td>Rugby League</td><td>no</td><td>no</td><td>no</td><td>yes</td><td>No match market exists between seasons.</td></tr>
<tr><td>Greyhounds</td><td>yes</td><td>no</td><td>no</td><td>no</td><td>One race, one runner.</td></tr>
<tr><td>Golf / Snooker / Motor Racing</td><td>no</td><td>no</td><td>no</td><td>no</td><td>No market open on OLBG at this read.</td></tr>
</tbody></table></div></div>
{''.join(blocks)}"""
    page(OUT / "markets.html", "Markets", "markets.html", body)


def build_sports_index(rows, coverage):
    cards = []
    for slug, label in SPORTS:
        s = next(x for x in coverage["sports"] if x["sport"] == slug)
        nom = next((n for n in coverage["no_market"] if n["sport"] == slug), None)
        status = (f'<span class="badge pass">no market</span>' if nom
                  else f'<span class="badge {("high" if s["high"] else "medium" if s["medium"] else "low")}">'
                       f'{s["picks"]} picks</span>')
        cards.append(f'<a class="card" href="sports/{slug}.html"><b>{esc(label)}</b>'
                     f'<small>{s["fixtures"]} fixtures · {s["written"]} write-ups · {status}</small></a>')
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Sports</div>
<h1 style="margin-top:10px">The fifteen sports in the brief</h1>
<p class="lede">Each page carries the fixture list, the prices and the reason anything is missing.</p>
<div class="cards">{''.join(cards)}</div>"""
    page(OUT / "sports.html", "Sports", "sports.html", body)


def build_sport_pages(rows, sources, coverage):
    for slug, label in SPORTS:
        sub = [r for r in rows if r["sport"] == slug]
        s = next(x for x in coverage["sports"] if x["sport"] == slug)
        nom = next((n for n in coverage["no_market"] if n["sport"] == slug), None)
        if not sub and nom:
            body = f"""<div class="crumb"><a href="index.html">Summary</a> / <a href="sports.html">Sports</a> / {esc(label)}</div>
<h1 style="margin-top:10px">{esc(label)}</h1>
<div class="warn"><strong>No bettable market at this read.</strong><p>{esc(nom['finding'])}</p>
<p><strong>How {esc(label)} is priced:</strong> {esc(nom['rule'])}</p>
<p class="small">Hub read: <a href="{esc(nom['hub'])}" target="_blank" rel="noopener noreferrer">OLBG {esc(label)}<span aria-hidden="true"> &#8599;</span></a></p></div>
<p>Rather than invent a selection for the brief's sake, this page stays empty until a market opens. The item is
on the <a href="../flagged.html">review queue</a> as {esc(nom['flag'])}.</p>"""
        else:
            facts = "".join(source_block(r, sources, limit=3) for r in sub[:1])
            body = f"""<div class="crumb"><a href="index.html">Summary</a> / <a href="sports.html">Sports</a> / {esc(label)}</div>
<h1 style="margin-top:10px">{esc(label)}</h1>
<div class="kpis">
<div class="kpi"><b>{s['fixtures']}</b><small>Fixtures</small></div>
<div class="kpi"><b>{s['picks']}</b><small>Picks</small></div>
<div class="kpi"><b>{s['high']}</b><small>High</small></div>
<div class="kpi"><b>{s['medium']}</b><small>Medium</small></div>
<div class="kpi"><b>{s['low']}</b><small>Low</small></div>
<div class="kpi"><b>{s['written']}</b><small>Write-ups</small></div>
</div>
<div class="panel"><h2>Picks</h2>
<div class="table-wrap"><table>
<thead><tr><th>Match</th><th>Our pick</th><th>Our fair price</th><th>Confidence</th><th>Basis</th><th>Source</th></tr></thead>
<tbody>{pick_rows(sub, sources, with_sport=False)}</tbody></table></div></div>
<div class="panel"><h2>Fixtures and facts</h2>
{''.join(f"<div style='margin-bottom:18px'><h3>{esc(r['away'])} at {esc(r['home'])}</h3>"
         f"<p class='small muted'>{esc(r['competition'])} · as OLBG shows it: {esc(r['start_label'])} · evidence: {esc(r['evidence'])}</p>"
         f"{source_block(r, sources, limit=3)}</div>" for r in sub)}</div>"""
        page(OUT / "sports" / f"{slug}.html", label, "sports.html", body, prefix="../")


def build_sources(sources):
    rows = []
    for s in sorted(sources["sources"], key=lambda x: (x["kind"] != "official", x["id"])):
        klass = {"read": "high", "read-partial": "medium", "blocked": "pass"}[s["status"]]
        rows.append(f'<tr><td><span class="badge {klass}">{esc(s["status"])}</span></td>'
                    f'<td>{esc(s["publisher"])}</td><td>{esc(s["title"])}</td>'
                    f'<td><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["url"][:78])}'
                    f'<span aria-hidden="true"> &#8599;</span></a></td>'
                    f'<td class="small">{esc(s["note"])}</td></tr>')
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Sources</div>
<h1 style="margin-top:10px">Source ledger</h1>
<p class="lede">Two kinds of page are listed. <strong>Official</strong> means a governing body, league, tour or
promoter: those are the only pages allowed to support a fact. <strong>Discovery</strong> means OLBG, which is used
to find events and to read the crowd's split, never to establish a fact. Blocked pages are kept on the list so a
reviewer can see exactly what the desk could not read.</p>
<div class="table-wrap"><table>
<thead><tr><th>Status</th><th>Publisher</th><th>Page</th><th>Link</th><th>What it gave us</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""
    page(OUT / "sources.html", "Sources", "sources.html", body)


def build_flags(flags, sources):
    arts = []
    for f in flags["flags"]:
        src = " ".join(link_src(s, sources) for s in f["sources"]) or '<span class="small muted">no external source: policy item</span>'
        arts.append(f"""<article class="pred" id="{esc(f['id'])}">
<h3>{esc(f['id'])} — {esc(f['title'])}</h3>
<div class="predmeta"><span class="badge flag">{esc(f['severity'])}</span> · {esc(SPORT_LABEL.get(f['sport'], f['sport']))}</div>
<p>{esc(f['detail'])}</p>
<p class="small">{src}</p></article>""")
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Review queue</div>
<h1 style="margin-top:10px">Flagged for review</h1>
<p class="lede">Everything that could not be confirmed, every page that refused, and every rule that forced a
judgement call. None of these blocked publication; all of them are here with their source so the call can be
checked.</p>
{''.join(arts)}"""
    page(OUT / "flagged.html", "Flagged for review", "flagged.html", body)


def build_method(coverage):
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Method</div>
<h1 style="margin-top:10px">How the numbers were made</h1>

<div class="panel"><h2>1. Discovery, then verification</h2>
<p>OLBG's fifteen hubs were read first, in the order the brief lists the sports. Each hub gives the events that
carry a live market, the crowd's most-tipped selection and, for most sports, a tip share. That is
<em>discovery</em>. Nothing from a hub is published as a fact.</p>
<p>The second pass fetches the governing body, league, tour or promoter page for the fixtures that matter, and
only numbers visible on those pages are written into the desk. Where the second pass failed, the row keeps its
market but loses its facts, and the failure goes on the review queue with the HTTP result.</p></div>

<div class="panel"><h2>2. Originating a price</h2>
<p>No bookmaker price is copied. For the NHL the rating is a club's point percentage plus 0.035 times its goal
difference per game, with a 0.15 logit home-ice adjustment; the money line is the logistic of three-point-two
times the rating gap plus that adjustment. Where a club's record could not be read, a 0.550 point-percentage
placeholder is used and the row says so. Match totals use each side's goals for and against per game averaged
and a normal model with a 1.45-goal standard deviation. The puck line is the money-line probability less 0.22 in
log-odds terms, floored at 30%.</p>
<p>For tennis the price is set from the two semi-final results read on the ATP scores page — who was seeded,
who needed three sets, who retired. For baseball it is a deliberately conservative home-field estimate, because
only one postseason game of form existed. For every sport where no official form page could be read, the price is
the crowd's split shrunk 40% toward a coin flip, and the row is labelled <em>sentiment</em>, never
<em>official</em>.</p></div>

<div class="panel"><h2>3. The confidence rule</h2>
<div class="table-wrap"><table>
<thead><tr><th>Label</th><th>Needs</th><th>What it means in practice</th></tr></thead>
<tbody>
<tr><td><span class="badge high">high</span></td><td>60% or better on our numbers, at least one side's form read from an official page this session, and a fair price inside &minus;250 to +10000</td><td>The pick is our strongest view and the price is one a bettor could actually take.</td></tr>
<tr><td><span class="badge medium">medium</span></td><td>55% or better with an official input, or 60% or better where only the fixture is official</td><td>Same discipline, closer call or thinner evidence.</td></tr>
<tr><td><span class="badge low">low</span></td><td>Everything else, including every row whose only input is the OLBG crowd</td><td>Published for completeness. Not a recommendation to stake on.</td></tr>
<tr><td><span class="badge pass">outside band</span></td><td>Fair price shorter than &minus;250 or longer than +10000</td><td>The match is still listed, but the pick cannot be High. Boston and Edmonton are today's examples.</td></tr>
</tbody></table></div>
<p style="margin-top:12px">This is deliberately not the "greater than 70% chance the market gives it" shortcut the
brief warns about. A &minus;250 price is already 71.4%, so requiring more than 70% <em>and</em> a price inside
the band leaves almost no room. Confidence here is about evidence plus price, and the probability is always
printed next to the pick so a reader can apply a stricter rule if they prefer.</p></div>

<div class="panel"><h2>4. What is deliberately not claimed</h2>
<ul>
<li><strong>No injuries.</strong> Not one injury or team-sheet claim is published, because no official team-news
page was readable for these fixtures. The brief asks for verified injuries; the honest answer here is that none
could be confirmed, so none appears.</li>
<li><strong>No head-to-head history</strong> unless an official page printed it, which none did on these reads.</li>
<li><strong>No conversion of OLBG's clock.</strong> The hub prints edge-local times with no zone label, so they
are printed verbatim in a column that says so.</li>
<li><strong>No padding.</strong> {coverage['counts']['low']} of {coverage['counts']['picks']} picks are Low and are labelled as such rather than promoted.</li>
</ul></div>"""
    page(OUT / "methodology.html", "Method", "methodology.html", body)


def build_olbg(coverage):
    hubs = coverage["no_market"]
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Inside OLBG</div>
<h1 style="margin-top:10px">How the OLBG side was read</h1>
<div class="panel"><h2>Routes and ids</h2>
<p>Every hub follows <code>/betting-tips/&lt;Sport_Slug&gt;/&lt;sport_id&gt;</code>, and the id is the number the
site itself uses in its event links. The ids used for this desk:</p>
<div class="table-wrap"><table>
<thead><tr><th>Sport</th><th>OLBG route</th><th>Id</th><th>What the hub gave us</th></tr></thead>
<tbody>
<tr><td>Tennis</td><td>/betting-tips/Tennis/3</td><td>3</td><td>15+ matches</td></tr>
<tr><td>Basketball</td><td>/betting-tips/Basketball/4</td><td>4</td><td>7 NBA, 3 KBL</td></tr>
<tr><td>Golf</td><td>/betting-tips/Golf/5</td><td>5</td><td>No tips found</td></tr>
<tr><td>Cricket</td><td>/betting-tips/Cricket/7</td><td>7</td><td>10 matches, 4 outrights</td></tr>
<tr><td>Snooker</td><td>/betting-tips/Snooker/8</td><td>8</td><td>No tips found</td></tr>
<tr><td>Rugby Union</td><td>/betting-tips/Rugby_Union/9</td><td>9</td><td>3 matches, 1 outright</td></tr>
<tr><td>Rugby League</td><td>/betting-tips/Rugby_League/10</td><td>10</td><td>Outrights only</td></tr>
<tr><td>Baseball</td><td>/betting-tips/Baseball/12</td><td>12</td><td>1 game</td></tr>
<tr><td>Ice Hockey</td><td>/betting-tips/Ice_Hockey/13</td><td>13</td><td>10 NHL, European club fixtures</td></tr>
<tr><td>Motor Racing</td><td>/betting-tips/Motor_Racing/14</td><td>14</td><td>No tips found</td></tr>
<tr><td>Darts</td><td>/betting-tips/Darts/15</td><td>15</td><td>2 matches, 2 outrights</td></tr>
<tr><td>Handball</td><td>/betting-tips/Handball/20</td><td>20</td><td>15+ fixtures</td></tr>
<tr><td>Volleyball</td><td>/betting-tips/Volleyball/21</td><td>21</td><td>15+ fixtures</td></tr>
<tr><td>Gaelic Football</td><td>/betting-tips/Gaelic_Football/25</td><td>25</td><td>4 club finals, 1 outright</td></tr>
<tr><td>Greyhounds</td><td>/betting-tips/Greyhounds/28</td><td>28</td><td>1 tipped race</td></tr>
</tbody></table></div></div>

<div class="panel"><h2>What the hubs hide</h2>
<ul>
<li><strong>Zero-tip events vanish.</strong> A fixture with no community tip is not rendered, which is why golf,
snooker and motor racing read as empty even though their seasons are running.</li>
<li><strong>Twenty-row cap.</strong> The default table stops after roughly twenty upcoming events and needs a
"Load more tips" click, so a hub read can miss fixtures that a competition sub-route shows.</li>
<li><strong>Unlabelled clocks.</strong> Times are edge-local with no zone suffix. The same match can read
"Today 19:07" on one route and a different hour on a cached sub-route.</li>
<li><strong>Wrong label on the sports menu.</strong> The golf and motor racing hubs rendered "All Sports" in the
menu where the sport name belongs, which is a rendering fault rather than a data one.</li>
<li><strong>Event links carry the id twice</strong> — once as a path segment and once as an <code>event_id</code>
query parameter; both are needed to reopen the exact market.</li>
</ul></div>

<div class="panel"><h2>The three sports with no market</h2>
{''.join(f"<p><strong>{esc(n['label'])}</strong> — {esc(n['finding'])}</p>" for n in hubs)}</div>"""
    page(OUT / "olbg.html", "Inside OLBG", "olbg.html", body)


def build_repo_audit():
    audit = repo_audit()
    rows = "".join(f'<tr><td>{esc(a["area"])}</td><td>{esc(a["check"])}</td>'
                   f'<td><span class="badge {"high" if a["status"]=="ok" else "flag"}">{esc(a["status"])}</span></td>'
                   f'<td class="small">{esc(a["detail"])}</td></tr>' for a in audit["checks"])
    body = f"""<div class="crumb"><a href="index.html">Summary</a> / Repo audit</div>
<h1 style="margin-top:10px">Line-by-line look at this repository</h1>
<p class="lede">The checks below were run against the working tree this session, not copied from an earlier
report. Each row states the check, the result and what it means.</p>
<div class="table-wrap"><table>
<thead><tr><th>Area</th><th>Check</th><th>Result</th><th>Detail</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<div class="panel"><h2>What a reviewer should look at first</h2>
<ol>
<li><strong>Two front doors.</strong> The repository root <code>index.html</code> is the earlier "today" desk, and
this desk lives at <code>/37737303/</code>. The root page gained one pointer line; merging the two front doors is
left to the next integration pass.</li>
<li><strong>Namespaced desks accumulate.</strong> {audit['desk_count']} session directories now sit at the
repository root. Each is preserved so old links keep working, but the root listing is becoming long, and a
reader arriving cold has no obvious single entry point.</li>
<li><strong>Stale snapshots in prose.</strong> {audit['prose_mismatch']} root pages still narrate the 21 October
snapshot. They are preserved as-is because they belong to other sessions, but a reader can land on one and think
it is current.</li>
</ol></div>"""
    page(OUT / "repo-audit.html", "Repo audit", "repo-audit.html", body)


def repo_audit():
    checks = []
    root = ROOT
    html_files = sorted(p for p in root.glob("*.html"))
    data_files = sorted((root / "data").glob("*.json"))

    # 1. tracked artefacts
    tracked = subprocess.run(["git", "ls-files", "*.pyc"], cwd=root, capture_output=True, text=True).stdout.split()
    checks.append(dict(area="Git hygiene", check="Compiled .pyc artefacts tracked in git",
                       status="ok" if not tracked else "flag",
                       detail=f"{len(tracked)} tracked .pyc files." if tracked else "None tracked; .gitignore already covers them."))

    # 2. root pages link check
    broken = []
    for p in html_files:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for href in __import__("re").findall(r'href="([^"#:]+\.html)"', txt):
            target = (p.parent / href).resolve()
            if not target.exists():
                broken.append(f"{p.name} -> {href}")
    checks.append(dict(area="Links", check="Root HTML files with a broken local .html link",
                       status="ok" if not broken else "flag",
                       detail=f"{len(broken)} broken: " + ", ".join(broken[:4]) if broken else "None found across the root pages."))

    # 3. data json parse
    bad = []
    for d in data_files:
        try:
            json.loads(d.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - reported, not raised
            bad.append(f"{d.name}: {exc.__class__.__name__}")
    checks.append(dict(area="Data", check="Root data/*.json files that fail to parse",
                       status="ok" if not bad else "flag",
                       detail=", ".join(bad) if bad else f"All {len(data_files)} files parse."))

    # 4. desk count
    desks = sorted(p.name for p in root.iterdir()
                   if p.is_dir() and not p.name.startswith(".") and p.name not in
                   {"data", "scripts", "tests", "pipeline", "sports", "assets", "docs", "reports",
                    "datasets", "site", "site_src", "site_templates", "desk", "today", "tools", "audit",
                    "research", "archive", "v3"})
    checks.append(dict(area="Structure", check="Session desk directories at the repository root",
                       status="flag" if len(desks) > 20 else "ok",
                       detail=f"{len(desks)} desks; each keeps its own namespace so old links stay live."))

    # 5. our own desk internal links
    our_broken = []
    for p in (OUT).rglob("*.html"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for href in __import__("re").findall(r'href="([^"#:]+\.html)"', txt):
            target = (p.parent / href).resolve()
            if not target.exists():
                our_broken.append(f"{p.relative_to(OUT)} -> {href}")
    checks.append(dict(area="Links", check="This desk's own internal links",
                       status="ok" if not our_broken else "flag",
                       detail="None broken." if not our_broken else f"{len(our_broken)} broken: " + ", ".join(our_broken[:4])))

    # 6. stale snapshot dates in the root pages
    stale = []
    for page in html_files:
        txt = page.read_text(encoding="utf-8", errors="ignore")
        if "2026-10-21" in txt or "21 Oct 2026" in txt:
            stale.append(page.name)
    checks.append(dict(area="Content", check="Root pages still narrating the 21 October snapshot",
                       status="flag" if stale else "ok",
                       detail=f"{len(stale)} pages: " + ", ".join(sorted(stale)[:6]) if stale
                              else "None: every root page describes the current window."))

    # 7. page weight
    heavy = sorted(((p.stat().st_size, p.name) for p in html_files), reverse=True)[:3]
    checks.append(dict(area="Performance", check="Heaviest root HTML pages",
                       status="flag" if heavy and heavy[0][0] > 500_000 else "ok",
                       detail=", ".join(f"{n} ({b/1024:.0f} KB)" for b, n in heavy)))

    # 8. biggest single data files
    big = sorted(((d.stat().st_size, d.relative_to(root).as_posix()) for d in root.glob("data/*.json")),
                 reverse=True)[:3]
    checks.append(dict(area="Data", check="Largest committed JSON files",
                       status="flag" if big and big[0][0] > 2_000_000 else "ok",
                       detail=", ".join(f"{n} ({b/1024:.0f} KB)" for b, n in big)))
    return dict(checks=checks, desk_count=len(desks), prose_mismatch=len(stale))


def main():
    sources, fixtures, flags, olbg, coverage, predictions = load()
    rows = fixtures["fixtures"]
    OUT.mkdir(parents=True, exist_ok=True)
    build_index(rows, sources, coverage, flags)
    build_picks(rows, sources, coverage)
    build_predictions(rows, sources)
    build_matches(rows, sources)
    build_markets(rows, coverage)
    build_sports_index(rows, coverage)
    build_sport_pages(rows, sources, coverage)
    build_sources(sources)
    build_flags(flags, sources)
    build_method(coverage)
    build_olbg(coverage)
    build_repo_audit()
    pages = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*.html"))
    print(json.dumps(dict(pages=len(pages), files=pages), indent=1))


if __name__ == "__main__":
    main()
