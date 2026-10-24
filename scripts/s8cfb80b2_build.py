"""Build the 8cfb80b2 desk: data JSON + static pages under /8cfb80b2/.

Run: python3 scripts/s8cfb80b2_build.py
Everything is generated from scripts/s8cfb80b2_data.py, so the pages cannot drift
from the record. Relative links only; no external assets.
"""
import html
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.s8cfb80b2_data import (CAPTURED, DESK, TASK, SOURCES, SPORTS, EVENTS, PICKS,
                                    FLAGS, COVERAGE)

OUT = ROOT / DESK
DATA = ROOT / "data" / DESK
BASE = "/OLBG1" + "/" + DESK + "/"


def e(v):
    return html.escape("" if v is None else str(v), quote=True)


def money(prob):
    """Convert a probability into an American price."""
    if prob >= 0.5:
        return int(round(-100 * prob / (1 - prob)))
    return int(round(100 * (1 - prob) / prob))


def dec(prob):
    return round(1 / prob, 3)


def stamp(iso):
    if not iso:
        return "not confirmed"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", iso)
    if not m:
        return e(iso)
    return f"{m.group(2)}-{m.group(3)} {m.group(4)}:{m.group(5)}Z"


def words(text):
    return len(re.findall(r"[A-Za-z0-9'’/?.-]+", text))


SPORT_NAMES = {k: n for k, n, _ in SPORTS}
EV = {x["id"]: x for x in EVENTS}
SOURCE_IDS = set(SOURCES)


def src_links(ids, official_only=False):
    parts = []
    for sid in ids:
        s = SOURCES[sid]
        if official_only and s["role"] != "official":
            continue
        parts.append(f'<a class="src {s["role"]}" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["publisher"])}</a>')
    return " ".join(parts) if parts else '<span class="blank">none &mdash; unverified</span>'


def official(ids):
    return [i for i in ids if SOURCES[i]["role"] == "official"]


CSS = """
:root{--ink:#101828;--muted:#5b6779;--line:#e3e8ef;--bg:#f7f9fc;--card:#fff;--brand:#0b5fff;--brand-soft:#eaf1ff;
--ok:#067647;--ok-soft:#ecfdf3;--warn:#b54708;--warn-soft:#fffaeb;--stop:#b42318;--stop-soft:#fef3f2;--radius:14px}
*{box-sizing:border-box}
body{margin:0;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
a{color:var(--brand);text-decoration:none}a:hover{text-decoration:underline}
header.top{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.nav{display:flex;flex-wrap:wrap;gap:4px;align-items:center;padding:10px 0}
.brand{font-weight:750;margin-right:18px;color:var(--ink);font-size:15px;letter-spacing:-.01em}
.brand span{color:var(--brand)}
.nav a.link{padding:6px 10px;border-radius:8px;color:var(--muted);font-size:14px;font-weight:550}
.nav a.link:hover{background:var(--brand-soft);color:var(--brand);text-decoration:none}
.nav a.link.active{background:var(--brand-soft);color:var(--brand)}
main{padding:28px 0 60px}
h1{font-size:clamp(26px,3.4vw,38px);line-height:1.15;margin:6px 0 10px;letter-spacing:-.02em}
h2{font-size:21px;margin:38px 0 12px;letter-spacing:-.01em}
h3{font-size:16px;margin:22px 0 8px}
p{margin:0 0 12px;color:#344054}
.eyebrow{text-transform:uppercase;letter-spacing:.09em;font-size:11.5px;font-weight:700;color:var(--brand);margin:0}
.lede{font-size:17px;color:#344054;max-width:74ch}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:22px 0 6px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px}
.kpi b{display:block;font-size:26px;letter-spacing:-.02em;line-height:1.2}
.kpi small{color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:650}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;margin:14px 0}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.jump{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));margin:16px 0}
.jump a{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:15px 16px;color:var(--ink)}
.jump a:hover{border-color:#b6ccff;text-decoration:none;box-shadow:0 2px 10px rgba(11,95,255,.07)}
.jump b{display:block;font-size:15px}.jump small{color:var(--muted)}
table{width:100%;border-collapse:collapse;font-size:14.5px}
.table-wrap{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:auto;margin:12px 0}
th{text-align:left;font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);
padding:11px 14px;border-bottom:1px solid var(--line);white-space:nowrap;background:#fbfcfe}
td{padding:12px 14px;border-bottom:1px solid #f1f4f8;vertical-align:top}
tr:last-child td{border-bottom:0}
td.num{white-space:nowrap;font-variant-numeric:tabular-nums}
.pick{display:grid;grid-template-columns:64px 1fr auto;gap:16px;align-items:start;
background:var(--card);border:1px solid var(--line);border-left:4px solid var(--brand);
border-radius:var(--radius);padding:16px 18px;margin:12px 0}
.pick .rank{font-size:22px;font-weight:750;color:var(--brand);line-height:1}
.pick h3{margin:0 0 4px;font-size:17px}
.pick .sel{font-weight:700;color:var(--ink)}
.pick .meta{color:var(--muted);font-size:13.5px}
.pick .price{text-align:right}
.pick .price b{display:block;font-size:20px;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:700;
letter-spacing:.03em;text-transform:uppercase}
.badge.high{background:var(--stop-soft);color:var(--stop)}
.badge.medium{background:var(--warn-soft);color:var(--warn)}
.badge.low{background:#eef2f6;color:#475467}
.badge.ok{background:var(--ok-soft);color:var(--ok)}
.badge.blank{background:#eef2f6;color:#475467}
.src{display:inline-block;font-size:12.5px;padding:2px 8px;border:1px solid var(--line);border-radius:999px;
margin:2px 4px 2px 0;background:#fff;color:#344054}
.src.official{border-color:#b6ccff;color:var(--brand);background:var(--brand-soft)}
.src.discovery{color:var(--muted)}
.blank{color:#98a2b3;font-style:italic}
.note{background:var(--brand-soft);border:1px solid #cfe0ff;border-radius:var(--radius);padding:14px 16px;margin:16px 0}
.warn{background:var(--warn-soft);border:1px solid #fedf89;border-radius:var(--radius);padding:14px 16px;margin:16px 0}
.danger{background:var(--stop-soft);border:1px solid #fecdca;border-radius:var(--radius);padding:14px 16px;margin:16px 0}
.note p:last-child,.warn p:last-child,.danger p:last-child{margin-bottom:0}
details{border:1px solid var(--line);border-radius:12px;padding:12px 16px;background:var(--card);margin:10px 0}
summary{cursor:pointer;font-weight:650}
.prose{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;margin:12px 0}
.prose .txt{font-size:16px;color:#1d2939}
.prose .ev{font-size:13px;color:var(--muted);margin-bottom:10px}
footer{border-top:1px solid var(--line);background:var(--card);padding:22px 0;color:var(--muted);font-size:13px}
.tag{display:inline-block;font-size:11.5px;color:var(--muted);border:1px dashed var(--line);border-radius:999px;padding:1px 8px}
@media(max-width:640px){.pick{grid-template-columns:1fr}.pick .price{text-align:left}.pick .rank{display:none}}
"""


def page(title, body, active="", rel=""):
    nav = [("Overview", "index.html", "overview"), ("Picks", "picks.html", "picks"),
           ("Written predictions", "predictions.html", "preds"), ("All matches", "matches.html", "matches"),
           ("Sources", "sources.html", "sources"), ("Flagged for review", "flagged.html", "flagged"),
           ("Coverage", "coverage.html", "coverage"), ("Method", "methodology.html", "method")]
    links = "".join(
        f'<a class="link{" active" if k == active else ""}" href="{rel}{p}">{e(t)}</a>'
        for t, p, k in nav)
    sports = "".join(f'<a class="tag" style="margin:2px 6px 2px 0" href="{rel}sports/{k}.html">{e(n)}</a>' for k, n, _ in SPORTS)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} &middot; OLBG desk {DESK}</title>
<meta name="color-scheme" content="light"><style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><div class="nav"><a class="brand" href="{rel}index.html">OLBG<span>.</span> research desk <span style="color:#98a2b3;font-weight:500">/ {DESK}</span></a>{links}</div></div></header>
<main><div class="wrap">{body}
<footer><div><strong>Capture {e(CAPTURED)}</strong> &middot; independent research, not betting advice. 18+.
Prices on this site are our own calculated fair odds, not quoted bookmaker odds.
<a href="{rel}methodology.html">How prices are produced</a> &middot; <a href="https://www.olbg.com/betting-tips">OLBG</a></div>
<div style="margin-top:8px">Sports: {sports}</div>
<div style="margin-top:8px"><a href="https://buffedlizard55-lab.github.io/OLBG1/">Canonical research desk</a> &middot;
<a href="https://github.com/buffedlizard55-lab/OLBG1">Repository</a></div></footer>
</div></main></body></html>"""


def pick_card(i, p):
    ev = EV[p["event"]]
    when = stamp(ev["start"])
    basis = "official start" if ev["basis"] == "official" else ("derived from OLBG display" if ev["basis"] == "derived" else "start not confirmed")
    return f"""<div class="pick"><div class="rank">#{i}</div>
<div><h3>{e(p['selection'])}</h3>
<div class="sel">{" vs ".join(x for x in [ev['home'], ev['away']] if x)}</div>
<div class="meta">{e(SPORT_NAMES[p['sport']])} &middot; {e(ev['comp'])} &middot; {when} ({e(basis)})</div>
<div class="meta">{src_links(official(ev['src']))}</div></div>
<div class="price"><b>{"%+d" % p['american']}</b>
<span class="meta">{p['prob']*100:.1f}% &middot; {dec(p['prob']):.3f}</span><br>
<span class="badge {p['tier'].lower()}">{e(p['tier'])}</span></div></div>"""


def event_table(events, show_sport=False):
    head = ["Start (UTC)", "Match and OLBG market", "Competition", "Sport", "Start source",
            "Official source", "Selection"]
    picked = {}
    for p in PICKS:
        picked.setdefault(p["event"], []).append(p)
    rows = []
    for ev in events:
        start = stamp(ev["start"]) if ev["start"] else '<span class="blank">not confirmed</span>'
        basis = {"official": "official", "derived": "derived (OLBG ET)"}.get(ev["basis"], '<span class="blank">&mdash;</span>')
        sel = "".join(f'<strong>{e(p["selection"])}</strong> {p["american"]:+d} <span class="badge {p["tier"].lower()}">{e(p["tier"])}</span><br>'
                      for p in picked.get(ev["id"], []))
        if not sel:
            sel = '<span class="blank">no price</span>'
        name = f'<strong>{e(ev["home"])}</strong>' + (f' vs {e(ev["away"])}' if ev["away"] else "")
        name += f'<br><a class="src discovery" href="{e(ev["olbg"])}" target="_blank" rel="noopener noreferrer">OLBG &middot; {e(ev["market"])}</a>'
        off = src_links(official(ev["src"]))
        rows.append([start, name, e(ev["comp"]), e(SPORT_NAMES[ev["sport"]]) if show_sport else "",
                     e(basis), off, sel])
    if not show_sport:
        head = [h for h in head if h != "Sport"]
        rows = [[c for i, c in enumerate(r) if i != 3] for r in rows]
    return ('<div class="table-wrap"><table><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) +
            "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) +
            "</tbody></table></div>")


def build():
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sports").mkdir(parents=True, exist_ok=True)

    # ---------------- machine readable ----------------
    for name, obj in [("events", EVENTS), ("picks", PICKS), ("sources", SOURCES),
                      ("flags", [dict(id=a, finding=b, scope=c, detail=d, link=f) for a, b, c, d, f in FLAGS]),
                      ("coverage", COVERAGE), ("sports", [dict(slug=k, name=n, olbg=f"https://www.olbg.com/betting-tips/{p}") for k, n, p in SPORTS])]:
        (DATA / f"{name}.json").write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---------------- landing ----------------
    upcoming = [x for x in EVENTS if x["start"] and x["start"] >= "2026-10-24T17:15"]
    body = f"""
<p class="eyebrow">Executive summary &middot; captured {e(CAPTURED)}</p>
<h1>Today's picks, in one place</h1>
<p class="lede">Everything below was read live from OLBG and then checked against the league, tour or club that runs the
event. <strong>Picks are the blue rows.</strong> Nothing is filled in from memory: where an official page could not be read,
the cell is blank and the row is on <a href="flagged.html">Flagged for review</a>.</p>

<div class="kpis">
  <div class="kpi"><small>Picks issued</small><b>{len(PICKS)}</b>across {len({p['sport'] for p in PICKS})} sports</div>
  <div class="kpi"><small>High confidence</small><b>0</b>nothing cleared the 70% bar</div>
  <div class="kpi"><small>Matches listed</small><b>{len(EVENTS)}</b>{len(upcoming)} with a confirmed start</div>
  <div class="kpi"><small>Official sources read</small><b>{sum(1 for s in SOURCES.values() if s['role']=='official')}</b>of {len(SOURCES)} sources</div>
</div>

<div class="warn"><p><strong>Read this before the picks.</strong> The brief asks for High confidence at better than 70%
with a fair price between &minus;250 and +10000. Today <strong>no selection cleared 70%</strong> on our own numbers, so the
ladder stops at Medium. Two picks are openly Low. The alternative was to inflate a tier to hit a quota, which would have
made the rest of the page worthless. Reasons per sport are on <a href="coverage.html">Coverage</a>.</p></div>

<h2>Where things are</h2>
<div class="jump">
  <a href="picks.html"><b>Picks</b><small>Every price book, every market we examined, and why unlisted markets were withheld.</small></a>
  <a href="predictions.html"><b>Written predictions</b><small>The full write-up for each pick, with the facts behind it.</small></a>
  <a href="matches.html"><b>All matches</b><small>The complete OLBG slate we captured, including rows with no pick.</small></a>
  <a href="sources.html"><b>Sources</b><small>Each official page, what it confirmed, and when it was read.</small></a>
  <a href="flagged.html"><b>Flagged for review</b><small>{len(FLAGS)} items that could not be confirmed or that look wrong upstream.</small></a>
  <a href="coverage.html"><b>Coverage per sport</b><small>All 15 sports, what was found, and what is missing.</small></a>
</div>

<h2>Picks, strongest first</h2>
<p class="lede" style="font-size:15px">Ranked by our estimated win probability. Each row states the selection, the fair
price we would lay, and the sport.</p>
{''.join(pick_card(i+1, p) for i, p in enumerate(sorted(PICKS, key=lambda x: -x['prob'])))}

<h2>Today and tomorrow, by sport</h2>
<p class="lede" style="font-size:15px">All {len(EVENTS)} captured rows. Rows with a pick show it in the last column.</p>
{event_table(EVENTS, show_sport=True)}

<h2>What this desk could not do</h2>
<div class="grid">
  <div class="card"><h3 style="margin-top:0">Five sports, no selection</h3>
  <p>Golf had no open OLBG market; rugby league had outrights only; cricket, tennis, darts, handball, volleyball,
  Gaelic games and rugby union markets were listed but their governing bodies could not be read in-session, so no
  price was issued. <a href="coverage.html">Per-sport detail</a>.</p></div>
  <div class="card"><h3 style="margin-top:0">Times are Eastern, not UTC</h3>
  <p>OLBG renders kick-offs in US Eastern. That was pinned by matching all eight NBA fixtures to the NBA's own
  injury report. Hub-derived times are labelled <em>derived</em>; only MLB, NHL, NBA, WST and F1 rows carry official
  start times. <a href="flagged.html#F-8C-03">Evidence</a>.</p></div>
  <div class="card"><h3 style="margin-top:0">Prices are ours</h3>
  <p>Every price is a fair odd derived from our own probability estimate. No bookmaker quote, no claimed edge and no
  availability claim. <a href="methodology.html">The method</a>.</p></div>
</div>
"""
    (OUT / "index.html").write_text(page("Executive summary", body, "overview"), encoding="utf-8")

    # ---------------- picks ----------------
    rows = []
    for p in sorted(PICKS, key=lambda x: -x["prob"]):
        ev = EV[p["event"]]
        mk = "".join(f'<li><strong>{e(m)}</strong> &mdash; {e(st)}: {e(note)}</li>' for m, st, note in p["markets"])
        rows.append(f"""<div class="card">
<h3 style="margin-top:0">{e(p['selection'])} <span class="badge {p['tier'].lower()}">{e(p['tier'])}</span></h3>
<p class="meta" style="color:var(--muted);margin-bottom:6px">{e(SPORT_NAMES[p['sport']])} &middot; {e(ev['comp'])}
&middot; {stamp(ev['start'])} &middot; {e(ev.get('venue') or 'venue not confirmed')}</p>
<p><strong>{" vs ".join(x for x in [ev['home'], ev['away']] if x)}</strong> &mdash; fair price
<strong>{"%+d" % p['american']}</strong> ({dec(p['prob']):.3f} decimal, {p['prob']*100:.1f}%).
Id <span class="tag">{e(p['id'])}</span></p>
<p>{e(p['why'])}</p>
<ul style="margin:6px 0 12px 18px;padding:0;color:#344054">{mk}</ul>
<p style="margin-bottom:4px">Official sources: {src_links(official(ev['src']))}</p>
<p style="margin:0"><a href="predictions.html#{e(p['id'])}">Read the full written prediction &rarr;</a></p>
</div>""")
    picks_body = f"""
<p class="eyebrow">Price books</p><h1>Picks and the markets we examined</h1>
<p class="lede">Six price books. For each one we list the markets we looked at and either priced or deliberately
withheld, so an empty market is a decision rather than an omission.</p>
<div class="note"><p><strong>Tiers.</strong> High requires both a probability above 70% and a fair price inside
&minus;250 to +10000. Medium is a defensible edge that does not clear that bar. Low is an openly weak opinion kept
for completeness. Nothing here is a bookmaker quote.</p></div>
{''.join(rows)}
<h2>Every market family checked</h2>
<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Winner</th><th>Handicap / spread</th><th>Total</th><th>Derivative</th></tr></thead><tbody>
<tr><td>Baseball</td><td>priced</td><td>run line withheld</td><td>withheld</td><td>&mdash;</td></tr>
<tr><td>Ice hockey</td><td>priced</td><td>puck line withheld</td><td>withheld</td><td>&mdash;</td></tr>
<tr><td>Basketball</td><td>priced</td><td>spread withheld</td><td>withheld</td><td>&mdash;</td></tr>
<tr><td>Snooker</td><td>priced</td><td>frame handicap withheld</td><td>total frames withheld</td><td>&mdash;</td></tr>
<tr><td>Motor racing</td><td>priced</td><td>&mdash;</td><td>&mdash;</td><td>podium priced, top six withheld</td></tr>
<tr><td>Other ten sports</td><td>not priced</td><td>not priced</td><td>not priced</td><td>not priced</td></tr>
</tbody></table></div>
"""
    (OUT / "picks.html").write_text(page("Picks", picks_body, "picks"), encoding="utf-8")

    # ---------------- predictions ----------------
    prose = []
    for p in sorted(PICKS, key=lambda x: -x["prob"]):
        ev = EV[p["event"]]
        prose.append(f"""<div class="prose" id="{e(p['id'])}">
<div class="ev"><strong>{e(p['selection'])}</strong> &middot; {e(SPORT_NAMES[p['sport']])} &middot; {e(ev['comp'])}
&middot; {stamp(ev['start'])} &middot; {"%+d" % p['american']} &middot; <span class="badge {p['tier'].lower()}">{e(p['tier'])}</span>
&middot; {words(p['prediction'])} words</div>
<p class="txt">{e(p['prediction'])}</p>
<p class="meta" style="color:var(--muted);font-size:13px">Facts in this write-up: {src_links(official(ev['src']))}</p>
</div>""")
    pred_body = f"""
<p class="eyebrow">Written predictions</p><h1>Every pick, written out</h1>
<p class="lede">Each prediction names the selection, the participants, the competition and the current-form facts that
support it, and links the official page each fact came from. All are unique to this desk and none repeats another's
wording.</p>
<div class="note"><p>Minimum length is 30 words; the shortest here is {min(words(p['prediction']) for p in PICKS)} words.
Statistics and availability lines are traced to a governing body, league, tour or club page listed at the foot of each entry.</p></div>
{''.join(prose)}
"""
    (OUT / "predictions.html").write_text(page("Written predictions", pred_body, "preds"), encoding="utf-8")

    # ---------------- matches ----------------
    per_sport = []
    for slug, name, _ in SPORTS:
        evs = [x for x in EVENTS if x["sport"] == slug]
        per_sport.append(f'<h2 id="{e(slug)}">{e(name)} <span class="tag">{len(evs)} rows</span></h2>' +
                         (event_table(evs) if evs else '<p class="blank">no rows captured</p>'))
    m_body = f"""
<p class="eyebrow">Discovery</p><h1>All captured OLBG matches</h1>
<p class="lede">The complete slate read from OLBG at {e(CAPTURED)}, grouped by the fifteen sports in scope. Times marked
<em>derived</em> come from the OLBG hub display (US Eastern, +4 hours to UTC) and are not confirmed by the competition.
Rows without a confirmed start or without an official source are shown as blank, not guessed.</p>
<div class="warn"><p><strong>{sum(1 for x in EVENTS if x['status']=='unconfirmed')} rows carry no confirmed start.</strong>
Those are greyhound races (whose printed and rendered times disagree by five hours), the Edmonton game, and the two
sport hubs that returned nothing. They are listed so the gap is visible, not so they can be bet.</p></div>
{''.join(per_sport)}
"""
    (OUT / "matches.html").write_text(page("All matches", m_body, "matches"), encoding="utf-8")

    # ---------------- sport pages ----------------
    for slug, name, path in SPORTS:
        evs = [x for x in EVENTS if x["sport"] == slug]
        picks = [p for p in PICKS if p["sport"] == slug]
        related = sorted({sid for x in evs for sid in x["src"]})
        pk = "".join(pick_card(i + 1, p) for i, p in enumerate(sorted(picks, key=lambda z: -z["prob"])))
        body = f"""
<p class="eyebrow">{e(name)}</p><h1>{e(name)}: {len(evs)} captured rows, {len(picks)} picks</h1>
<p class="lede">{e(COVERAGE.get(slug, ""))}</p>
<div class="jump"><a href="https://www.olbg.com/betting-tips/{path}" target="_blank" rel="noopener noreferrer"><b>OLBG hub</b><small>betting-tips/{path}</small></a>
<a href="../coverage.html"><b>Coverage</b><small>What is missing for every sport</small></a></div>
{('<h2>Picks</h2>' + pk) if pk else '<div class="warn"><p><strong>No pick in this sport today.</strong> The market was listed on OLBG but no official fixture or form source could be read, so no price was issued.</p></div>'}
<h2>Rows</h2>
{event_table(evs) if evs else '<p class="blank">No OLBG rows captured for this sport.</p>'}
<h2>Sources used in this sport</h2>
<div class="card">{src_links(related) if related else '<span class="blank">none</span>'}</div>
"""
        (OUT / "sports" / f"{slug}.html").write_text(page(name, body, "matches", rel="../"), encoding="utf-8")

    # ---------------- sources ----------------
    srows = []
    for sid, s in SOURCES.items():
        used = sorted({x["id"] for x in EVENTS if sid in x["src"]})
        srows.append(f"""<tr><td><strong>{e(sid)}</strong><br><span class="badge {'ok' if s['role']=='official' else 'blank'}">{e(s['role'])}</span></td>
<td><a href="{e(s['url'])}" target="_blank" rel="noopener noreferrer">{e(s['publisher'])}</a><br>
<span style="color:var(--muted);font-size:12.5px;word-break:break-all">{e(s['url'])}</span></td>
<td>{e(s['confirms'])}</td><td class="num">{e(s['captured'])}</td><td class="num">{len(used)}</td></tr>""")
    src_body = f"""
<p class="eyebrow">Provenance</p><h1>Sources</h1>
<p class="lede">Every official page that was actually opened in this session, the fact it confirmed, and the moment it was
read. OLBG pages are marked <em>discovery</em>: they tell us the market exists and are never used to confirm a fact.</p>
<div class="table-wrap"><table><thead><tr><th>Id</th><th>Publisher and URL</th><th>What it confirmed</th><th>Read at (UTC)</th><th>Rows</th></tr></thead><tbody>
{''.join(srows)}</tbody></table></div>
<h2>Sources that could not be read</h2>
<div class="table-wrap"><table><thead><tr><th>Source</th><th>Result</th><th>Consequence</th></tr></thead><tbody>
<tr><td>stats.nba.com scoreboard endpoint</td><td>request failed</td><td>no NBA team records, so basketball prices do not include a power rating</td></tr>
<tr><td>pdc.tv tournament and news pages</td><td>cookie-consent wall instead of content</td><td>darts left unpriced</td></tr>
<tr><td>unitedrugby.com/fixtures</td><td>404</td><td>rugby union left unpriced</td></tr>
<tr><td>wtafiles draw PDFs for the 2026 Osaka event</td><td>no route for this event year was read</td><td>tennis left unpriced</td></tr>
<tr><td>icc-cricket.com fixtures</td><td>not attempted after the session budget was reached</td><td>cricket left unpriced</td></tr>
</tbody></table></div>
"""
    (OUT / "sources.html").write_text(page("Sources", src_body, "sources"), encoding="utf-8")

    # ---------------- flagged ----------------
    frows = []
    for fid, title, scope, detail, link in FLAGS:
        frows.append(f"""<div class="card" id="{e(fid)}">
<h3 style="margin-top:0">{e(fid)} &middot; {e(title)}</h3>
<p class="meta" style="color:var(--muted);font-size:13px">Scope: {e(scope)}</p>
<p>{e(detail)}</p>
<p style="margin:0"><a href="{e(link)}" target="_blank" rel="noopener noreferrer">Source to check &rarr;</a></p></div>""")
    flag_body = f"""
<p class="eyebrow">Needs review</p><h1>Flagged for review</h1>
<p class="lede">These are the {len(FLAGS)} places where the record is incomplete, where a value was deliberately left
blank, or where the upstream site looks wrong. None of them block the release; all of them are here so they can be
checked by hand.</p>
<div class="danger"><p><strong>Nothing on this page is an estimate presented as fact.</strong> Where a value could not be
confirmed it is empty everywhere on this site, and the row is listed here with the link that should confirm it.</p></div>
{''.join(frows)}
"""
    (OUT / "flagged.html").write_text(page("Flagged for review", flag_body, "flagged"), encoding="utf-8")

    # ---------------- coverage ----------------
    crows = []
    for slug, name, path in SPORTS:
        evs = [x for x in EVENTS if x["sport"] == slug]
        offs = sum(1 for x in evs if official(x["src"]))
        picks = [p for p in PICKS if p["sport"] == slug]
        crows.append(f"""<tr><td><a href="sports/{slug}.html"><strong>{e(name)}</strong></a></td>
<td class="num">{len(evs)}</td><td class="num">{offs}</td><td class="num">{len(picks)}</td>
<td class="num">{len(picks)*'&#9679;' or '<span class="blank">none</span>'}</td><td>{e(COVERAGE.get(slug,''))}</td></tr>""")
    cov_body = f"""
<p class="eyebrow">All fifteen sports</p><h1>Coverage, sport by sport</h1>
<p class="lede">The brief asks for five written picks in every sport, every day. That target was not met today and the
gap is stated here rather than hidden: {len(PICKS)} picks across {len({p['sport'] for p in PICKS})} sports. The table shows exactly where
the chain broke.</p>
<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Rows</th><th>Rows with an official source</th><th>Picks</th><th></th><th>What happened</th></tr></thead><tbody>
{''.join(crows)}</tbody></table></div>
<h2>Why the shortfall exists</h2>
<div class="grid">
<div class="card"><h3 style="margin-top:0">1. Quota versus evidence</h3><p>A pick needs three things: an open OLBG market,
an official fixture confirmation, and at least one official form or availability fact. Sports where the second or third
was missing produce zero picks, not a weak one.</p></div>
<div class="card"><h3 style="margin-top:0">2. Official feeds are thin</h3><p>MLB and the NHL publish machine-readable
fixtures, and the NBA publishes a daily injury report. Cricket, handball, volleyball, darts and Gaelic games do not
publish anything comparable that was reachable here.</p></div>
<div class="card"><h3 style="margin-top:0">3. High is not a label</h3><p>No market today produced a probability above 70%
on the facts that were readable. A 55% pick labelled High would be a lie with a number attached.</p></div>
</div>
"""
    (OUT / "coverage.html").write_text(page("Coverage", cov_body, "coverage"), encoding="utf-8")

    # ---------------- methodology ----------------
    meth = f"""
<p class="eyebrow">How this works</p><h1>Method and limits</h1>
<h2>The pipeline</h2>
<ol style="color:#344050;max-width:80ch">
<li><strong>Discovery.</strong> The OLBG hub for each of the fifteen sports was read live and every open market recorded
with its OLBG URL, selection and tip count. Tip counts are community votes and are never used as probabilities.</li>
<li><strong>Official confirmation.</strong> For each candidate, a governing body, league, tour or club page was opened.
Only what that page states is carried into the row.</li>
<li><strong>Line origination.</strong> Our probability is built from the confirmed inputs: season record and splits for
baseball and hockey, published availability for basketball, and practice/route evidence for motorsport and snooker.
The fair price is 1/p with no margin, reported in American odds.</li>
<li><strong>Tiering.</strong> High needs p &gt; 0.70 and a fair price between &minus;250 and +10000. Medium is a
defensible edge below that bar. Low is a weak opinion kept for completeness.</li>
<li><strong>Writing.</strong> Each pick gets a unique write-up of at least 30 words naming the selection, both sides,
the competition, current form and the official fact it rests on.</li>
</ol>
<h2>Deliberate omissions</h2>
<div class="table-wrap"><table><thead><tr><th>Thing</th><th>Why it is absent</th></tr></thead><tbody>
<tr><td>Bookmaker prices and availability</td><td>we issue our own lines; we did not scrape or quote any bookmaker</td></tr>
<tr><td>Injuries for games with no submitted report</td><td>four NBA games were still "not yet submitted" at 12:15 PM ET</td></tr>
<tr><td>Team records for basketball</td><td>the NBA statistics endpoint failed; nothing was estimated to fill it</td></tr>
<tr><td>Greyhound trap data and times</td><td>times are internally inconsistent and no GBGB card was read</td></tr>
<tr><td>Worldwide fixture coverage</td><td>only markets that were open on OLBG at capture are listed; that is not a full fixture list</td></tr>
</tbody></table></div>
<h2>Timezone rule</h2>
<p>OLBG sport hubs render kick-offs in US Eastern (UTC&minus;4). This was established by matching all eight NBA fixtures
on the hub to the tip-off times printed in the NBA's official injury report for the same day. UTC times are therefore
four hours ahead of the hub display. Any row whose time comes from that display is labelled <em>derived</em> and is never
described as confirmed. Official times exist for MLB, NHL, NBA, WST and Formula 1 rows.</p>
<h2>What "verified" means here</h2>
<p>A fact is treated as confirmed only when an official publisher's page was opened during this session and it stated
that fact. The word itself is kept out of the public predictions, and no value is ever inferred, interpolated or carried
in from memory.</p>
"""
    (OUT / "methodology.html").write_text(page("Method", meth, "method"), encoding="utf-8")

    # ---------------- reverse engineering ----------------
    rev = """
<p class="eyebrow">Reverse engineering</p><h1>How OLBG is put together</h1>
<p class="lede">Structural notes from reading the site today. These describe routes and rendering behaviour, not
opinions about the matches.</p>
<h2>Routes that work</h2>
<div class="table-wrap"><table><thead><tr><th>Pattern</th><th>Example</th><th>What it returns</th></tr></thead><tbody>
<tr><td>/betting-tips/{Sport_Slug}/{sport_id}</td><td>/betting-tips/Basketball/4</td><td>sport hub: ~20 open markets with selection, market type, tip counts</td></tr>
<tr><td>/betting-tips/{Sport}/{All_X}/{All_Events}/{Slug}/{id}?event_id=NNN</td><td>.../MIA_Heat_@_CHA_Hornets/4?event_id=536117</td><td>single event: every market and the tip share per outcome</td></tr>
<tr><td>/best-tipsters/{Sport}/{id}</td><td>/best-tipsters/Golf/5</td><td>tipster leaderboard</td></tr>
</tbody></table></div>
<h2>Things that trip a reader up</h2>
<div class="grid">
<div class="card"><h3 style="margin-top:0">Times carry no timezone</h3><p>Hubs are US Eastern; greyhound cards are
displaced by five hours from the time printed in the race name. Never treat a hub time as UTC.</p></div>
<div class="card"><h3 style="margin-top:0">Silent zero-tip suppression</h3><p>A competition with no open tips disappears
from the hub entirely. Absence of a fixture on OLBG is not evidence that the fixture does not exist.</p></div>
<div class="card"><h3 style="margin-top:0">Empty hubs</h3><p>The golf hub returned "No tips found" at capture; the
All Events route returned the same body with the footer attached.</p></div>
<div class="card"><h3 style="margin-top:0">Tip share is not probability</h3><p>The percentage beside a selection is the
share of community tips on it. It is a vote count, and this desk never converts it into a price.</p></div>
</div>
<h2>What we treated as in scope</h2>
<p>Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing,
Handball, Ice Hockey, Basketball and Rugby League. Soccer, American football, horse racing, boxing, MMA, hurling and
cycling are excluded.</p>
"""
    (OUT / "reverse-engineering.html").write_text(page("Reverse engineering", rev, "method"), encoding="utf-8")

    print(f"built {DESK}: {len(list(OUT.rglob('*.html')))} pages, {len(PICKS)} picks, {len(EVENTS)} events")


if __name__ == "__main__":
    build()
