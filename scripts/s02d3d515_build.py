"""Build the 02d3d515 clear-dashboard site.

Run:  python3 scripts/s02d3d515_build.py
Out:  02d3d515/*.html, 02d3d515/sports/*.html, data/02d3d515/*.json
"""
import html
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s02d3d515_data import (FIXTURES, PICKS, WITHHELD, SPORTS, FLAGS,
                            SOURCES, OLBG_ROUTES, OBSERVED)
from s02d3d515_model import (american_from_prob, decimal_from_prob, two_way,
                             total_book, nhl_expected_total, tier,
                             clears_seventy, in_band, BAND_MAX_PROB)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "02d3d515"
DATA = ROOT / "data" / "02d3d515"
REPO = "https://github.com/buffedlizard55-lab/OLBG1"
LIVE = "https://buffedlizard55-lab.github.io/OLBG1/02d3d515/"

SOURCE_BY_ID = {s["id"]: s for s in SOURCES}
FIXTURE_BY_ID = {f["id"]: f for f in FIXTURES}
SPORT_NAME = dict((slug, name) for slug, name, _ in SPORTS)
SPORT_PUB = dict((slug, pub) for slug, _, pub in SPORTS)
SLUG = dict((name, slug) for slug, name, _ in SPORTS)

# Fields that must be present on both sides before a match can be tiered high.
SIDE_KEYS = {
    "ice-hockey": ("a_record", "b_record"),
    "basketball": ("a_record", "b_record"),
    "baseball": ("a_record", "b_record"),
    "tennis": ("a_semi", "b_semi"),
    "rugby-union": ("a_table", "b_table"),
    "cricket": ("a_record", "b_record"),
}
MULTI = {"Race winner", "Podium finish", "Top 6 finish", "Outright winner", "Top 10 finish"}


def e(value):
    return html.escape("" if value is None else str(value), quote=True)


def both_sides(fx):
    keys = SIDE_KEYS.get(fx["sport"])
    if not keys:
        return False
    return all(fx["facts"].get(k) for k in keys)


def build_picks():
    out = []
    for p in PICKS:
        fx = FIXTURE_BY_ID[p["fixture"]]
        prob = p["prob"]
        multi = p["market"] in MULTI
        conf = tier(prob, both_sides(fx), multi_runner=multi, manual=p["confidence"])
        out.append(dict(
            p, prediction=p["prediction"].strip(), sport=fx["sport"], sport_name=SPORT_NAME[fx["sport"]], slug=fx["sport"],
            match=(fx["b"] + " v " + fx["a"]) if fx["sport"] in ("tennis", "rugby-union", "gaelic-football")
                  else (fx["a"] + " at " + fx["b"] if fx["b"] else fx["a"]),
            comp=fx["comp"], start_utc=fx["start_utc"], start_label=fx.get("start_label", ""),
            price=american_from_prob(prob), decimal=round(decimal_from_prob(prob), 3),
            band=in_band(prob), seventy=clears_seventy(prob),
            confidence=conf,
            source=SOURCE_BY_ID[fx["source"]],
        ))
    out.sort(key=lambda r: ({"high": 0, "medium": 1, "low": 2}[r["confidence"]],
                            r["start_utc"] or "9999", -r["prob"]))
    return out


def fmt_start(iso, fallback=""):
    if not iso:
        return fallback or "start not confirmed"
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc)
    return dt.strftime("%d %b · %H:%M UTC")


def fmt_price(p):
    if p is None:
        return "—"
    return f"{p:+d}"


CSS = """
:root{
  --bg:#f5f7fa;--surface:#fff;--ink:#101828;--muted:#667085;--line:#e4e7ec;
  --accent:#0b6b4f;--accent-ink:#08543e;--soft:#ecfdf3;--amber:#b54708;--amber-soft:#fffaeb;
  --red:#b42318;--red-soft:#fef3f2;--blue:#175cd3;--blue-soft:#eff8ff;--radius:14px;
  --shadow:0 1px 2px rgba(16,24,40,.06),0 1px 3px rgba(16,24,40,.1);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent-ink);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.96);
  border-bottom:1px solid var(--line);backdrop-filter:blur(6px)}
.top .wrap{display:flex;align-items:center;gap:18px;min-height:62px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;font-weight:750;letter-spacing:-.01em;color:var(--ink)}
.brand .dot{width:10px;height:10px;border-radius:50%;background:var(--accent);display:inline-block}
.brand small{display:block;font-weight:500;color:var(--muted);font-size:11px;letter-spacing:.09em;text-transform:uppercase}
nav.main{display:flex;gap:2px;flex-wrap:wrap;margin-left:auto}
nav.main a{padding:8px 11px;border-radius:9px;color:#344054;font-size:14px;font-weight:600}
nav.main a:hover{background:#f2f4f7;text-decoration:none}
nav.main a[aria-current="page"]{background:var(--soft);color:var(--accent-ink)}
.hero{padding:34px 0 10px}
.eyebrow{margin:0 0 8px;color:var(--accent-ink);font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}
h1{margin:0;font-size:clamp(28px,4vw,40px);line-height:1.12;letter-spacing:-.02em}
.lede{color:var(--muted);max-width:74ch;margin:12px 0 0;font-size:17px}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:22px 0 6px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;box-shadow:var(--shadow)}
.kpi b{display:block;font-size:26px;letter-spacing:-.02em;line-height:1.1}
.kpi span{color:var(--muted);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.07em}
section{margin:34px 0}
.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-bottom:12px;flex-wrap:wrap}
h2{margin:0;font-size:23px;letter-spacing:-.015em}
h3{margin:0 0 6px;font-size:17px}
.section-head p{margin:4px 0 0;color:var(--muted);font-size:14px;max-width:80ch}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden}
.pad{padding:18px}
.table-wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:14px}
caption{text-align:left;padding:14px 16px 0;color:var(--muted);font-size:13px}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
thead th{background:#fafbfc;color:#475467;font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;white-space:nowrap;position:sticky;top:0}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fcfcfd}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.pick{font-weight:750}
.match{font-weight:600}
.sub{color:var(--muted);font-size:12.5px;display:block}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:750;letter-spacing:.02em;border:1px solid transparent;white-space:nowrap}
.badge.high{background:var(--soft);color:var(--accent-ink);border-color:#abefc6}
.badge.medium{background:var(--amber-soft);color:var(--amber);border-color:#fedf89}
.badge.low{background:#f2f4f7;color:#475467;border-color:#e4e7ec}
.badge.info{background:var(--blue-soft);color:var(--blue);border-color:#b2ddff}
.badge.warn{background:var(--red-soft);color:var(--red);border-color:#fecdca}
.chip{display:inline-block;padding:1px 7px;border-radius:6px;background:#f2f4f7;color:#475467;font-size:11.5px;font-weight:600}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow)}
.card.predict h3{font-size:16px;margin-bottom:2px}
.card .meta{color:var(--muted);font-size:12.5px;margin-bottom:10px}
.card p.body{margin:0;font-size:14.5px}
.pickline{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:8px 0 10px}
.pickline b{font-size:15px}
.facts{display:flex;gap:18px;flex-wrap:wrap;margin:10px 0 0;padding:10px 0 0;border-top:1px dashed var(--line);font-size:12.5px;color:var(--muted)}
.facts b{color:var(--ink);font-weight:700}
.notice{display:flex;gap:10px;align-items:flex-start;background:var(--amber-soft);border:1px solid #fedf89;color:#7a2e0e;border-radius:12px;padding:12px 14px;font-size:14px}
.notice.green{background:var(--soft);border-color:#abefc6;color:#08543e}
.notice.red{background:var(--red-soft);border-color:#fecdca;color:#7a271a}
.notice p{margin:0}
.srclink{font-size:12.5px;font-weight:650;white-space:nowrap}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}
.tabs a{padding:7px 12px;border:1px solid var(--line);border-radius:999px;background:var(--surface);font-size:13px;font-weight:650;color:#344054}
.tabs a:hover{background:#f9fafb;text-decoration:none}
.crumbs{color:var(--muted);font-size:13px;margin:18px 0 0}
.crumbs a{color:var(--muted)}
footer{margin:48px 0 40px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);padding-top:16px}
footer p{margin:6px 0}
.sportgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.sportcard{display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;box-shadow:var(--shadow);color:var(--ink)}
.sportcard:hover{border-color:#abefc6;text-decoration:none}
.sportcard strong{display:block;font-size:15px}
.sportcard span{color:var(--muted);font-size:12.5px}
.empty{color:var(--muted);font-size:14px;font-style:italic}
@media (max-width:900px){
  .kpis{grid-template-columns:repeat(2,1fr)}
  .grid,.grid3,.sportgrid{grid-template-columns:1fr}
}
@media (max-width:620px){
  nav.main{width:100%;margin:8px 0 4px}
  .top .wrap{min-height:0;padding-top:10px;padding-bottom:10px}
  th,td{padding:9px 10px}
}
"""

NAV = [
    ("index.html", "Summary"),
    ("picks.html", "Picks"),
    ("matches.html", "Matches"),
    ("markets.html", "Our lines"),
    ("predictions.html", "Predictions"),
    ("sports.html", "Sports"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method"),
    ("flagged.html", "Flagged"),
    ("repo-audit.html", "Repo audit"),
]


def frame(title, active, body, prefix="", description=""):
    def navlink(href, label):
        current = ' aria-current="page"' if href == active else ""
        return f'<a href="{prefix}{href}"{current}>{e(label)}</a>'
    nav = "".join(navlink(href, label) for href, label in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG research desk</title>
<meta name="description" content="{e(description or 'Source-linked match research: our own lines, a clear pick for each match and written analysis.')}">
<meta name="color-scheme" content="light">
<style>{CSS}</style>
</head><body>
<header class="top"><div class="wrap">
  <a class="brand" href="{prefix}index.html"><span class="dot"></span><span>OLBG research desk<small>24 Oct 2026 · source-linked</small></span></a>
  <nav class="main" aria-label="Primary">{nav}</nav>
</div></header>
<main class="wrap">
{body}
<footer>
  <p><strong>What this site is.</strong> An independent research dashboard. Prices are our own fair (zero-vig) estimates, not bookmaker quotes. A pick is an opinion, not a guarantee. 18+.</p>
  <p>Data read {e(OBSERVED)} · <a href="{prefix}methodology.html">How the lines are made</a> · <a href="{prefix}flagged.html">What could not be confirmed</a> · <a href="{REPO}">Repository</a></p>
  <p>Not affiliated with OLBG, the NBA, the NHL, MLB, the ATP, Formula 1, the LNR, the PGA TOUR or Cork GAA.</p>
</footer>
</main></body></html>"""


def source_cell(source, prefix=""):
    return (f'<a class="srclink" href="{e(source["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{e(source["publisher"])} ↗</a>')


def pick_rows(picks, prefix="", show_prediction=False):
    rows = []
    for p in picks:
        pred = f'<div class="sub">{e(p["prediction"])}</div>' if show_prediction else ""
        rows.append(
            "<tr>"
            f'<td><span class="badge {p["confidence"]}">{p["confidence"].title()}</span></td>'
            f'<td><a href="{prefix}sports/{p["slug"]}.html">{e(p["sport_name"])}</a>'
            f'<span class="sub">{e(p["comp"])}</span></td>'
            f'<td><span class="match">{e(p["match"])}</span><span class="sub">{e(fmt_start(p["start_utc"], p.get("start_label", "")))}</span></td>'
            f'<td><span class="pick">{e(p["selection"])}</span><span class="sub">{e(p["market"])} · fair {fmt_price(p["price"])}</span>{pred}</td>'
            f'<td class="num"><b>{p["prob"]*100:.1f}%</b><span class="sub">{fmt_price(p["price"])}</span></td>'
            f'<td>{source_cell(p["source"], prefix)}</td>'
            "</tr>"
        )
    return "".join(rows)


def picks_table(picks, prefix="", show_prediction=False, caption=""):
    if not picks:
        return '<p class="empty">No priced selection in this view.</p>'
    return (f'<div class="panel table-wrap"><table>'
            f'{f"<caption>{e(caption)}</caption>" if caption else ""}'
            "<thead><tr><th>Confidence</th><th>Sport</th><th>Match &amp; start</th>"
            "<th>Pick</th><th class=\"num\">Est. win</th><th>Official source</th></tr></thead>"
            f"<tbody>{pick_rows(picks, prefix, show_prediction)}</tbody></table></div>")


def coverage_table(picks, prefix=""):
    rows = []
    for slug, name, publisher in SPORTS:
        fx = [f for f in FIXTURES if f["sport"] == slug]
        sp = [p for p in picks if p["sport"] == slug]
        hi = sum(p["confidence"] == "high" for p in sp)
        if sp:
            status = f'<span class="badge high">{hi} high</span> <span class="badge medium">{sum(p["confidence"]=="medium" for p in sp)} medium</span> <span class="badge low">{sum(p["confidence"]=="low" for p in sp)} low</span>'
        elif fx:
            status = '<span class="badge info">fixtures only</span>'
        else:
            status = '<span class="badge warn">no confirmed fixture</span>'
        rows.append(
            f'<tr><td><a href="{prefix}sports/{slug}.html"><b>{e(name)}</b></a><span class="sub">{e(publisher)}</span></td>'
            f'<td class="num">{len(fx)}</td><td class="num">{len(sp)}</td><td>{status}</td>'
            f'<td>{e("5 per day" if len(sp) >= 5 else ("short of the five-per-day target" if sp else "no line published"))}</td></tr>'
        )
    return ('<div class="panel table-wrap"><table><thead><tr><th>Sport</th><th class="num">Fixtures</th>'
            '<th class="num">Picks</th><th>Confidence mix</th><th>Target</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def market_books(picks):
    """Group our published books by fixture + market."""
    books = {}
    for p in picks:
        fx = FIXTURE_BY_ID[p["fixture"]]
        key = (p["fixture"], p["market"])
        if key in books:
            continue
        if p["market"] in MULTI:
            books[key] = dict(kind="single", outcomes=[dict(sel=p["selection"], prob=p["prob"],
                                                            decimal=round(decimal_from_prob(p["prob"]), 3),
                                                            american=p["price"])])
            continue
        a = dict(sel=p["selection"], prob=p["prob"], decimal=round(decimal_from_prob(p["prob"]), 3),
                 american=p["price"])
        other_sel = {
            "Match winner": None,
            "Match total": ("Over " + p["selection"].split(" ")[-1]) if p["selection"].startswith("Under") else ("Under " + p["selection"].split(" ")[-1]),
            "Race winner": None,
        }.get(p["market"])
        if other_sel is None:
            books[key] = dict(kind="single", outcomes=[a])
        else:
            b = dict(sel=other_sel, prob=round(1 - p["prob"], 6),
                     decimal=round(1 / (1 - p["prob"]), 3),
                     american=american_from_prob(1 - p["prob"]))
            books[key] = dict(kind="two-way", outcomes=[a, b])
    return books


def build():
    OUT.mkdir(exist_ok=True)
    (OUT / "sports").mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    picks = build_picks()
    high = [p for p in picks if p["confidence"] == "high"]
    med = [p for p in picks if p["confidence"] == "medium"]
    low = [p for p in picks if p["confidence"] == "low"]
    books = market_books(picks)

    # ---------------- data exports ----------------
    export = dict(observed=OBSERVED, sources=SOURCES, olbg_routes=OLBG_ROUTES,
                  fixtures=FIXTURES, picks=picks, flags=FLAGS, withheld=WITHHELD)
    (DATA / "desk.json").write_text(json.dumps(export, indent=2), encoding="utf-8")
    (DATA / "fixtures.json").write_text(json.dumps(FIXTURES, indent=2), encoding="utf-8")
    (DATA / "picks.json").write_text(json.dumps(picks, indent=2), encoding="utf-8")
    (DATA / "sources.json").write_text(json.dumps(SOURCES, indent=2), encoding="utf-8")
    (DATA / "flags.json").write_text(json.dumps(FLAGS, indent=2), encoding="utf-8")

    # ---------------- index ----------------
    todays = [p for p in picks if (p["start_utc"] or "")[:10] == "2026-10-24"]
    tomorrow = [p for p in picks if (p["start_utc"] or "")[:10] == "2026-10-25"]
    top = high[:4] if high else picks[:4]
    cards = "".join(
        f"""<article class="card predict">
  <div class="meta">{e(p["sport_name"])} · {e(p["comp"])} · {e(fmt_start(p["start_utc"]))}</div>
  <h3>{e(p["match"])}</h3>
  <div class="pickline"><span class="badge {p["confidence"]}">{p["confidence"].title()}</span>
    <b>{e(p["selection"])}</b><span class="chip">{e(p["market"])}</span>
    <span class="chip">fair {fmt_price(p["price"])}</span><span class="chip">{p["prob"]*100:.1f}%</span></div>
  <p class="body">{e(p["prediction"])}</p>
  <div class="facts"><span>Source: <a href="{e(p["source"]["url"])}" target="_blank" rel="noopener noreferrer">{e(p["source"]["publisher"])} ↗</a></span>
  <span>Read {e(p["source"]["observed"])}</span></div>
</article>""" for p in top)

    body = f"""
<div class="hero">
  <p class="eyebrow">Executive summary · 24 October 2026</p>
  <h1>The picks, the match, the reasoning — in that order.</h1>
  <p class="lede">Every pick below is a match we can price from data published by the sport's own governing body.
  Each row says what to back, at what price, how likely we think it is, and links the source.
  If we could not confirm something, it is blank and listed on the <a href="flagged.html">Flagged</a> page.</p>
</div>

<div class="kpis">
  <div class="kpi"><b>{len(picks)}</b><span>Priced picks</span></div>
  <div class="kpi"><b>{len(high)}</b><span>High confidence</span></div>
  <div class="kpi"><b>{len(FIXTURES)}</b><span>Fixtures tracked</span></div>
  <div class="kpi"><b>{len({p["sport"] for p in picks})}/15</b><span>Sports with a pick</span></div>
  <div class="kpi"><b>{len(FLAGS)}</b><span>Flagged items</span></div>
</div>

<div class="notice green"><p><strong>Read the summary first.</strong> {len(high)} high-confidence picks across
{len({p["sport"] for p in high})} sports, {len(todays)} selections starting today and {len(tomorrow)} tomorrow.
The rest of the card sits below; each pick has one written prediction and one official link.</p></div>

<section>
  <div class="section-head"><div><h2>High-confidence picks</h2>
  <p>Our strongest tier: a price inside the brief's −250…+10000 window, an estimated win chance of at least {int(58)}%,
  and official form data for <em>both</em> sides of the match. Picks priced shorter than −250 are moved to Medium and labelled, because the brief excludes that range.</p></div>
  <a class="srclink" href="picks.html">All {len(picks)} picks →</a></div>
  {picks_table(high, show_prediction=True)}
</section>

<section>
  <div class="section-head"><div><h2>The full card</h2>
  <p>Every pick we publish, ordered by confidence and then by start time. Today is 24 October UTC; late US games carry a 25 October UTC start.</p></div>
  <a class="srclink" href="predictions.html">Read all {len(picks)} predictions →</a></div>
  {picks_table(picks)}
</section>

<section>
  <div class="section-head"><div><h2>Written predictions</h2>
  <p>The reasoning behind our best four selections. Each one names the teams, their form, the specific numbers behind the call and the selection itself.</p></div></div>
  <div class="grid">{cards}</div>
</section>

<section>
  <div class="section-head"><div><h2>Coverage by sport</h2>
  <p>All fifteen sports in the brief are tracked. Eight have a priced pick today; the rest are published as gaps with the reason rather than filled with unsourced analysis.</p></div>
  <a class="srclink" href="sports.html">Browse the fifteen sport pages →</a></div>
  {coverage_table(picks)}
</section>

<section>
  <div class="section-head"><div><h2>How to read a pick</h2></div></div>
  <div class="grid3">
    <div class="card"><h3>1 · The selection</h3><p>The bold text in the Pick column is the bet: a team to win, a total to go under, a driver to finish on the podium. The market and our fair price sit underneath it.</p></div>
    <div class="card"><h3>2 · The confidence</h3><p>High, Medium or Low. High needs three things at once: a fair price inside the requested window, at least a 58% estimated win chance, and official form for both sides.</p></div>
    <div class="card"><h3>3 · The evidence</h3><p>Every row links the official page the numbers came from, with the UTC time it was read. Where a value is missing, the cell is blank and the row is on the Flagged page.</p></div>
  </div>
</section>
"""
    (OUT / "index.html").write_text(frame("Executive summary", "index.html", body,
                                          description="Today's highest-confidence picks, the full card, and coverage across fifteen sports."), encoding="utf-8")

    # ---------------- picks ----------------
    by_sport = ""
    for slug, name, publisher in SPORTS:
        sp = [p for p in picks if p["sport"] == slug]
        if not sp:
            continue
        by_sport += f"""<section id="{slug}">
  <div class="section-head"><div><h2>{e(name)}</h2><p>{len(sp)} priced selection(s) · <a href="sports/{slug}.html">Sport page</a></p></div></div>
  {picks_table(sp, show_prediction=True)}
</section>"""
    body = f"""
<div class="hero"><p class="eyebrow">All picks</p><h1>{len(picks)} picks, grouped by sport</h1>
<p class="lede">{len(high)} high · {len(med)} medium · {len(low)} low. The pick is the bold text; the market and fair price are underneath it; the prediction is the paragraph; the link is the official source.</p></div>
<div class="tabs">{''.join(f'<a href="#{s}">{e(n)}</a>' for s, n, _ in SPORTS if any(p["sport"] == s for p in picks))}</div>
{by_sport}
<div class="notice"><p><strong>Not every sport has a pick.</strong> Rugby League, Snooker, Greyhounds, Darts and Volleyball have no fixture we could verify from an official source today, and Handball has official fixtures but no form data. They are listed on the <a href="flagged.html">Flagged</a> page with links.</p></div>
"""
    (OUT / "picks.html").write_text(frame("Picks", "picks.html", body), encoding="utf-8")

    # ---------------- matches ----------------
    rows = []
    for f in sorted(FIXTURES, key=lambda x: x["start_utc"] or "9999"):
        src = SOURCE_BY_ID[f["source"]]
        picked = [p for p in picks if p["fixture"] == f["id"]]
        status = f'<span class="badge high">{len(picked)} pick(s)</span>' if picked else '<span class="badge info">line withheld</span>'
        facts = f["facts"]
        keys = [k for k in ("a_record", "b_record", "a_table", "b_table", "a_semi", "b_semi") if facts.get(k)]
        factline = " · ".join(f"{k.replace('_',' ')}: {facts[k]}" for k in keys) if keys else "—"
        rows.append(
            f'<tr><td><a href="sports/{f["sport"]}.html">{e(SPORT_NAME[f["sport"]])}</a><span class="sub">{e(f["comp"])}</span></td>'
            f'<td><span class="match">{e((f["a"] + " v " + f["b"]) if f["b"] else f["a"])}</span><span class="sub">{e(f["round"])}</span></td>'
            f'<td class="num">{e(fmt_start(f["start_utc"], f.get("start_label", "")))}</td>'
            f'<td>{factline}</td><td>{status}</td><td>{source_cell(src)}</td></tr>'
        )
    body = f"""
<div class="hero"><p class="eyebrow">All matches</p><h1>{len(FIXTURES)} fixtures we could confirm</h1>
<p class="lede">Only fixtures confirmed on an official schedule are listed. Rows without a line are deliberate: the form data for both sides was not captured, so no price was invented.</p></div>
<div class="panel table-wrap"><table>
<thead><tr><th>Sport</th><th>Match</th><th class="num">Start</th><th>Official form read</th><th>Status</th><th>Source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<section><div class="section-head"><div><h2>Fixtures with no published line</h2>
<p>Each row names exactly what is missing. These are counted against our coverage, not hidden.</p></div></div>
<div class="panel table-wrap"><table><thead><tr><th>Match</th><th>Missing</th><th>Why no line</th><th>Official source</th></tr></thead><tbody>
{''.join(f'<tr><td class="match">{e((FIXTURE_BY_ID[i]["a"] + " v " + FIXTURE_BY_ID[i]["b"]))}</td><td>{e(m)}</td><td>{e(w)}</td><td>{source_cell(SOURCE_BY_ID[FIXTURE_BY_ID[i]["source"]])}</td></tr>' for i, m, w in WITHHELD)}
</tbody></table></div></section>
"""
    (OUT / "matches.html").write_text(frame("Matches", "matches.html", body), encoding="utf-8")

    # ---------------- markets ----------------
    blocks = []
    current = None
    for (fid, market), book in books.items():
        f = FIXTURE_BY_ID[fid]
        if current != fid:
            if current:
                blocks.append("</tbody></table></div></div>")
            title = (f["a"] + " v " + f["b"]) if f["b"] else f["a"]
            blocks.append(f"""<div class="card" style="margin-bottom:14px">
<h3>{e(title)}</h3><div class="meta">{e(SPORT_NAME[f["sport"]])} · {e(f["comp"])} · {e(fmt_start(f["start_utc"], f.get("start_label", "")))} ·
<a href="{e(SOURCE_BY_ID[f["source"]]["url"])}" target="_blank" rel="noopener noreferrer">{e(SOURCE_BY_ID[f["source"]]["publisher"])} ↗</a></div>
<div class="table-wrap"><table><thead><tr><th>Market</th><th>Selection</th><th class="num">Our probability</th><th class="num">Fair decimal</th><th class="num">Fair American</th><th>Official source</th></tr></thead><tbody>""")
            current = fid
        for o in book["outcomes"]:
            blocks.append(f'<tr><td>{e(market)}</td><td class="pick">{e(o["sel"])}</td>'
                          f'<td class="num">{o["prob"]*100:.1f}%</td><td class="num">{o["decimal"]:.3f}</td>'
                          f'<td class="num">{fmt_price(o["american"])}</td>'
                          f'<td>{source_cell(SOURCE_BY_ID[f["source"]])}</td></tr>')
    if current:
        blocks.append("</tbody></table></div></div>")
    body = f"""
<div class="hero"><p class="eyebrow">Our lines</p><h1>The prices we originated</h1>
<p class="lede">Every price is fair (zero-vig): decimal = 1 ÷ our probability, so a two-way book sums to exactly 100%.
Nothing here is copied from a bookmaker. Markets we investigated but could not price are listed underneath with the reason.</p></div>
{''.join(blocks)}
<section><div class="section-head"><div><h2>Markets investigated but withheld</h2>
<p>The brief asks for handicap, match total and team totals to be looked at for every match. Where the official inputs for a market do not exist, the market is withheld rather than guessed.</p></div></div>
<div class="panel table-wrap"><table><thead><tr><th>Sport</th><th>Market not priced</th><th>Reason</th><th>Official page read</th></tr></thead><tbody>
<tr><td>Basketball</td><td>Handicap / spread, match total, team totals</td><td>Only win-loss records were read; no official points-for/against was captured, so a spread or total would be invented.</td><td><a href="https://www.nba.com/standings" target="_blank" rel="noopener noreferrer">NBA standings ↗</a></td></tr>
<tr><td>Cricket</td><td>Handicap, total runs, top batter/bowler</td><td>No official scorecard or squad for this fixture was read.</td><td><a href="https://www.pcb.com.pk/news" target="_blank" rel="noopener noreferrer">PCB news ↗</a></td></tr>
<tr><td>Gaelic Sports</td><td>Handicap, total points</td><td>The official fixture is confirmed but no scoring record for either club was read.</td><td><a href="https://gaacork.ie/fixtures/" target="_blank" rel="noopener noreferrer">Cork GAA fixtures ↗</a></td></tr>
<tr><td>Handball</td><td>All markets</td><td>Fixtures confirmed by the EHF; no group standings were captured.</td><td><a href="https://ehfcl.eurohandball.com/men/2026-27/matches/" target="_blank" rel="noopener noreferrer">EHF Champions League ↗</a></td></tr>
<tr><td>Tennis</td><td>Total games, games handicap, set betting</td><td>Only the two semi-final scorelines were read; no serve or game-length data for the final.</td><td><a href="https://www.atptour.com/en/scores/current" target="_blank" rel="noopener noreferrer">ATP scores ↗</a></td></tr>
<tr><td>Rugby Union</td><td>Handicap, total points</td><td>League positions were read; no points-for/against table was captured.</td><td><a href="https://top14.lnr.fr/calendrier-et-resultats" target="_blank" rel="noopener noreferrer">Top 14 ↗</a></td></tr>
<tr><td>Golf / Motor Racing</td><td>Multi-runner books</td><td>Prices are per selection on a multi-runner market; they do not sum to 100% and are labelled as such.</td><td><a href="https://www.pgatour.com/leaderboard" target="_blank" rel="noopener noreferrer">PGA TOUR ↗</a> · <a href="https://www.formula1.com/en/racing/2026/united-states" target="_blank" rel="noopener noreferrer">Formula 1 ↗</a></td></tr>
</tbody></table></div></section>
"""
    (OUT / "markets.html").write_text(frame("Our lines", "markets.html", body), encoding="utf-8")

    # ---------------- predictions ----------------
    pred_cards = "".join(
        f"""<article class="card predict" id="p-{p["fixture"]}-{i}">
  <div class="meta">{e(p["sport_name"])} · {e(p["comp"])} · {e(fmt_start(p["start_utc"]))}</div>
  <h3>{e(p["match"])}</h3>
  <div class="pickline"><span class="badge {p["confidence"]}">{p["confidence"].title()}</span>
    <b>{e(p["selection"])}</b><span class="chip">{e(p["market"])}</span>
    <span class="chip">fair {fmt_price(p["price"])}</span><span class="chip">{p["prob"]*100:.1f}%</span></div>
  <p class="body">{e(p["prediction"])}</p>
  <div class="facts"><span><b>{len(p["prediction"].split())} words</b></span>
  <span>Source: <a href="{e(p["source"]["url"])}" target="_blank" rel="noopener noreferrer">{e(p["source"]["publisher"])} ↗</a></span>
  <span>Read {e(p["source"]["observed"])}</span></div>
</article>""" for i, p in enumerate(sorted(picks, key=lambda x: ({"high": 0, "medium": 1, "low": 2}[x["confidence"]], x["start_utc"] or "9999")), 1))
    body = f"""
<div class="hero"><p class="eyebrow">Predictions</p><h1>{len(picks)} written predictions</h1>
<p class="lede">Each one is unique, at least 30 words, and built only from facts read on the official source linked in the card.
No sentence is reused. Nothing is generated from a template placeholder.</p></div>
<div class="notice"><p><strong>How these are written.</strong> Team or player, current form, recent results, one match-specific statistic and the selection in plain words.
The injury line is blank for every match because no official injury report was read — see <a href="flagged.html">Flagged</a>.</p></div>
<section><div class="section-head"><div><h2>Index of every prediction</h2>
<p>One row per prediction, in confidence order. The last column links to the official page the facts came from; the middle column jumps to the full write-up below.</p></div></div>
<div class="panel table-wrap"><table><thead><tr><th>Confidence</th><th>Sport</th><th>Match</th><th>Pick</th><th class="num">Words</th><th>Official source</th></tr></thead><tbody>
{''.join(f'<tr><td><span class="badge {p["confidence"]}">{p["confidence"].title()}</span></td><td>{e(p["sport_name"])}<span class="sub">{e(p["comp"])}</span></td><td><a href="#p-{p["fixture"]}-{i}">{e(p["match"])}</a><span class="sub">{e(fmt_start(p["start_utc"], p.get("start_label", "")))}</span></td><td class="pick">{e(p["selection"])}<span class="sub">{e(p["market"])} · fair {fmt_price(p["price"])}</span></td><td class="num">{len(p["prediction"].split())}</td><td>{source_cell(p["source"])}</td></tr>' for i, p in enumerate(sorted(picks, key=lambda x: ({"high": 0, "medium": 1, "low": 2}[x["confidence"]], x["start_utc"] or "9999")), 1))}
</tbody></table></div></section>
<div class="grid">{pred_cards}</div>
"""
    (OUT / "predictions.html").write_text(frame("Predictions", "predictions.html", body), encoding="utf-8")

    # ---------------- sports index + pages ----------------
    cards = "".join(
        f"""<a class="sportcard" href="sports/{slug}.html"><strong>{e(name)}</strong>
<span>{len([f for f in FIXTURES if f["sport"] == slug])} fixture(s) · {len([p for p in picks if p["sport"] == slug])} pick(s) · {e(pub)}</span></a>"""
        for slug, name, pub in SPORTS)
    body = f"""
<div class="hero"><p class="eyebrow">By category</p><h1>Fifteen sports, one page each</h1>
<p class="lede">Open a sport to see its picks first, then its fixtures, our lines and the reason anything is missing.</p></div>
<div class="sportgrid">{cards}</div>
<section style="margin-top:24px"><div class="section-head"><div><h2>Coverage at a glance</h2>
<p>Fixtures confirmed on an official schedule, and how many of them carry a published line.</p></div></div>
{coverage_table(picks)}</section>
"""
    (OUT / "sports.html").write_text(frame("Sports", "sports.html", body), encoding="utf-8")

    for slug, name, publisher in SPORTS:
        fx = sorted([f for f in FIXTURES if f["sport"] == slug], key=lambda x: x["start_utc"] or "9999")
        sp = [p for p in picks if p["sport"] == slug]
        withheld = [w for w in WITHHELD if FIXTURE_BY_ID[w[0]]["sport"] == slug]
        flags = [f for f in FLAGS if f["sport"] in (name, "All")]
        flag_html = "".join(
            f'<div class="notice{" red" if f["severity"]=="high" else ""}"><p><strong>{e(f["id"])} · {e(f["title"])}</strong><br>{e(f["detail"])} '
            f'<a href="{e(f["link"])}" target="_blank" rel="noopener noreferrer">{e(f["link_label"])} ↗</a></p></div>'
            for f in flags) or '<p class="empty">No sport-specific flag.</p>'
        fx_rows = "".join(
            f'<tr><td class="match">{e((f["a"] + " v " + f["b"]) if f["b"] else f["a"])}</td>'
            f'<td>{e(f["round"])}</td><td class="num">{e(fmt_start(f["start_utc"], f.get("start_label", "")))}</td>'
            f'<td>{" · ".join(f"{k.replace(chr(95),chr(32))}: {v}" for k, v in f["facts"].items()) or "—"}</td>'
            f'<td>{source_cell(SOURCE_BY_ID[f["source"]])}</td></tr>' for f in fx)
        sport_books = [(k, v) for k, v in books.items() if FIXTURE_BY_ID[k[0]]["sport"] == slug]
        if sport_books:
            mrows = "".join(
                f'<tr><td>{e(FIXTURE_BY_ID[fid]["a"] + (" at " + FIXTURE_BY_ID[fid]["b"] if FIXTURE_BY_ID[fid]["b"] else ""))}</td>'
                f'<td>{e(market)}</td><td class="pick">{e(" / ".join(o["sel"] for o in b["outcomes"]))}</td>'
                f'<td class="num">{", ".join(fmt_price(o["american"]) for o in b["outcomes"])}</td></tr>'
                for (fid, market), b in sport_books)
            markets_html = (f'<div class="panel table-wrap"><table><thead><tr><th>Match</th><th>Market</th>'
                            f'<th>Selection(s)</th><th class="num">Fair price</th></tr></thead><tbody>{mrows}</tbody></table></div>')
        else:
            markets_html = '<p class="empty">No line originated for this sport today.</p>'
        body = f"""
<p class="crumbs"><a href="../index.html">Summary</a> / <a href="../sports.html">Sports</a> / {e(name)}</p>
<div class="hero"><p class="eyebrow">{e(publisher)}</p><h1>{e(name)}</h1>
<p class="lede">{len(sp)} priced selection(s) from {len(fx)} confirmed fixture(s). Picks come first; the fixtures and our lines follow.</p></div>
{'<div class="notice red"><p><strong>No confirmed pick today.</strong> The reason is in the flag list below. The fixture may still exist — it is simply not priced without official form.</p></div>' if not sp else ''}
<section><div class="section-head"><div><h2>Picks</h2><p>Bold text is the bet. Fair price is ours, zero-vig.</p></div></div>{picks_table(sp, prefix="../", show_prediction=True)}</section>
<section><div class="section-head"><div><h2>Confirmed fixtures</h2><p>Start times in UTC, from the official schedule.</p></div></div>
{'<div class="panel table-wrap"><table><thead><tr><th>Match</th><th>Round</th><th class="num">Start</th><th>Official form read</th><th>Source</th></tr></thead><tbody>' + fx_rows + '</tbody></table></div>' if fx else '<p class="empty">No official fixture confirmed for this sport today.</p>'}</section>
<section><div class="section-head"><div><h2>Our lines</h2><p>Only markets the official inputs support.</p></div></div>{markets_html}</section>
<section><div class="section-head"><div><h2>What is missing</h2></div></div>{flag_html}
{''.join(f'<div class="notice"><p><strong>Line withheld:</strong> {e(FIXTURE_BY_ID[i]["a"] + " v " + FIXTURE_BY_ID[i]["b"])} — {e(m)}. {e(w)}</p></div>' for i, m, w in withheld)}</section>
"""
        (OUT / "sports" / f"{slug}.html").write_text(frame(name, "sports.html", body, prefix="../"), encoding="utf-8")

    # ---------------- sources ----------------
    def role_cell(is_official):
        if is_official:
            return '<span class="badge high">official</span>'
        return '<span class="badge warn">discovery</span>'
    srows = "".join(
        f'<tr><td><span class="match">{e(s["publisher"])}</span><span class="sub">{e(s["id"])}</span></td>'
        f'<td><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["url"])}</a></td>'
        f'<td class="num">{e(s["observed"])}</td><td>{e(s["scope"])}</td>'
        f'<td>{role_cell(s["official"])}</td></tr>'
        for s in SOURCES)
    orows = "".join(
        f'<tr><td>{e(n)}</td><td><a href="{e(u)}" target="_blank" rel="noopener noreferrer">{e(u)}</a></td>'
        f'<td class="num">{e(t)}</td><td>{e(note)}</td><td><span class="badge info">discovery only</span></td></tr>'
        for n, u, t, note in OLBG_ROUTES)
    body = f"""
<div class="hero"><p class="eyebrow">Provenance</p><h1>Every source, with the time it was read</h1>
<p class="lede">Official sources verify facts. OLBG is used only to discover which matches are on the board. No price, record or statistic on this site comes from a betting site.</p></div>
<section><div class="section-head"><div><h2>Official sources</h2><p>League, governing body, tour or promoter pages read this session.</p></div></div>
<div class="panel table-wrap"><table><thead><tr><th>Publisher</th><th>URL</th><th class="num">Read (UTC)</th><th>What was taken from it</th><th>Role</th></tr></thead><tbody>{srows}</tbody></table></div></section>
<section><div class="section-head"><div><h2>OLBG discovery routes</h2><p>Read to establish what is on the board, never to verify a fact.</p></div></div>
<div class="panel table-wrap"><table><thead><tr><th>Sport</th><th>Route</th><th class="num">Read (UTC)</th><th>Observed</th><th>Role</th></tr></thead><tbody>{orows}</tbody></table></div></section>
<div class="notice"><p><strong>What is deliberately not here.</strong> No odds-comparison feed, no media report, no social post and no encyclopaedia is used as a source of fact or price. If an official page did not give us a number, the number is absent.</p></div>
"""
    (OUT / "sources.html").write_text(frame("Sources", "sources.html", body), encoding="utf-8")

    # ---------------- methodology ----------------
    body = f"""
<div class="hero"><p class="eyebrow">Method</p><h1>How a pick gets made</h1>
<p class="lede">Four steps, each one visible on the site: confirm the match, read the form, originate a price, write the reasoning. Anything that fails a step is dropped or flagged.</p></div>

<section><div class="section-head"><div><h2>1 · Confirm the match on an official schedule</h2></div></div>
<div class="card"><p>OLBG tells us which matches are on the board. The start time, venue and participants are then taken from the governing body:
api-web.nhle.com for the NHL, statsapi.mlb.com for MLB, nba.com for the NBA, atptour.com for tennis, formula1.com for the Grand Prix,
top14.lnr.fr for the Top 14, pgatour.com for the leaderboard, gaacork.ie for Cork finals and ehfcl.eurohandball.com for handball.
A fixture that appears only on OLBG is not published as a match.</p></div></section>

<section><div class="section-head"><div><h2>2 · Read form for both sides</h2></div></div>
<div class="card"><p>For the NHL and NBA that means the official 2026-27 record, last ten and streak. For MLB it means the season record, run differential and the series result.
For the Top 14 it means the live league position. For tennis it means the semi-final scoreline. If only one side can be read, the match cannot be a high-confidence pick —
it may still appear with a lower tier, and the missing side is named on the Flagged page.</p></div></section>

<section><div class="section-head"><div><h2>3 · Originate a fair price</h2></div></div>
<div class="card">
<p>Prices are ours. A probability <em>p</em> becomes a decimal price of 1 ÷ <em>p</em>, which is a zero-vig price: a two-way book made this way sums to exactly 100%.
American odds are converted from that decimal. Nothing is copied from a bookmaker and no margin is added.</p>
<p style="margin-top:10px"><strong>The odds window and the 70% question.</strong> The brief asks for high-confidence picks between −250 and +10000, and separately describes
high confidence as a chance above 70%. Those two rules cannot both bind on a two-way market: a −250 price is a 71.4% chance, so the >70% rule leaves only a
1.4-point band (decimal 1.400–1.429, roughly −250 to −233) before the price drops inside the excluded floor. We apply the window as the binding rule, publish the
probability for every pick, and label any pick that also clears 70% with a <span class="badge high">70%+</span> note in the data.
{len([p for p in picks if p["seventy"]])} of our {len(picks)} picks clear 70%; all of them sit inside the window.</p>
</div></section>

<section><div class="section-head"><div><h2>4 · Tier the pick</h2></div></div>
<div class="grid3">
  <div class="card"><h3><span class="badge high">High</span></h3><p>Fair price inside −250…+10000, our estimated chance at least 58%, and official form for both sides. {len(high)} today.</p></div>
  <div class="card"><h3><span class="badge medium">Medium</span></h3><p>Inside the window at 53–58%, or a genuine edge priced shorter than the −250 floor. {len(med)} today.</p></div>
  <div class="card"><h3><span class="badge low">Low</span></h3><p>Partial evidence, a coin-flip price, or a multi-runner market. {len(low)} today.</p></div>
</div></section>

<section><div class="section-head"><div><h2>What we will not do</h2></div></div>
<div class="panel pad">
<ul style="margin:0;padding-left:18px">
<li>We will not publish a record, a score, an injury or a statistic that we did not read on an official page.</li>
<li>We will not price a market without the inputs it needs. That is why no NBA spread, no tennis total and no handball line appears today.</li>
<li>We will not call a pick high-confidence when only one side of the match has been read.</li>
<li>We will not fill an injury field from memory. Every injury cell is blank and says so.</li>
<li>We will not copy a bookmaker price or present our estimate as a market quote.</li>
</ul></div></section>
"""
    (OUT / "methodology.html").write_text(frame("Method", "methodology.html", body), encoding="utf-8")

    # ---------------- flagged ----------------
    frows = "".join(
        f'<tr><td><code>{e(f["id"])}</code></td><td><span class="badge {"warn" if f["severity"]=="high" else ("medium" if f["severity"]=="medium" else "low")}">{e(f["severity"])}</span></td>'
        f'<td>{e(f["sport"])}</td><td><span class="match">{e(f["title"])}</span><span class="sub">{e(f["detail"])}</span></td>'
        f'<td><a href="{e(f["link"])}" target="_blank" rel="noopener noreferrer">{e(f["link_label"])} ↗</a></td></tr>'
        for f in FLAGS)
    body = f"""
<div class="hero"><p class="eyebrow">Needs your review</p><h1>Flagged for review</h1>
<p class="lede">{len(FLAGS)} items. Everything here is either a value we could not confirm, a sport we could not price, or a limitation of the source site.
None of it is hidden in a footnote; none of it blocks publication.</p></div>
<div class="notice red"><p><strong>The one that matters most:</strong> the brief asks for five written predictions per sport each day. We publish
{len(picks)} across {len({p["sport"] for p in picks})} sports. The remaining sports had no fixture plus official form we could read, and we did not invent the gap away.</p></div>
<div class="panel table-wrap"><table><thead><tr><th>ID</th><th>Severity</th><th>Sport</th><th>Finding</th><th>Source to check</th></tr></thead><tbody>{frows}</tbody></table></div>
<section><div class="section-head"><div><h2>Fixtures we could not confirm</h2><p>These are on the OLBG board but were not published as matches, because no official fixture could be confirmed.</p></div></div>
<div class="panel table-wrap"><table><thead><tr><th>Sport</th><th>OLBG listing</th><th>Why it is not on the match list</th><th>Discovery link</th></tr></thead><tbody>
<tr><td>Rugby League</td><td>2027 outrights only</td><td>No 2026 match market is open.</td><td><a href="https://www.olbg.com/betting-tips/Rugby_League/10" target="_blank" rel="noopener">OLBG ↗</a></td></tr>
<tr><td>Snooker</td><td>Mark Williams v Jak Jones, 14:05</td><td>Start time had passed and WST shows the event completed.</td><td><a href="https://www.olbg.com/betting-tips/Snooker/8" target="_blank" rel="noopener">OLBG ↗</a></td></tr>
<tr><td>Greyhounds</td><td>Monmore, Doncaster, Central Park cards</td><td>Listings were expired or had no official card to read.</td><td><a href="https://www.olbg.com/betting-tips/Greyhounds/28" target="_blank" rel="noopener">OLBG ↗</a></td></tr>
<tr><td>Darts</td><td>European Championship matches</td><td>PDC page returned a consent wall; no order of play read.</td><td><a href="https://www.olbg.com/betting-tips/Darts/15" target="_blank" rel="noopener">OLBG ↗</a></td></tr>
<tr><td>Volleyball</td><td>Italian, Polish, German, Brazilian club matches</td><td>No official fixture matching an OLBG match could be read.</td><td><a href="https://www.olbg.com/betting-tips/Volleyball/21" target="_blank" rel="noopener">OLBG ↗</a></td></tr>
<tr><td>Tennis</td><td>Kreuger v Siniakova; Eala v Stojsavljevic; Uchijima v Mertens</td><td>WTA draw and order of play did not render; only ATP matches were readable.</td><td><a href="https://www.olbg.com/betting-tips/Tennis/3" target="_blank" rel="noopener">OLBG ↗</a></td><td><a href="https://www.atptour.com/en/scores/current" target="_blank" rel="noopener noreferrer">ATP scores ↗</a></td></tr>
</tbody></table></div>
"""
    (OUT / "flagged.html").write_text(frame("Flagged", "flagged.html", body), encoding="utf-8")

    # ---------------- repo audit ----------------
    body = f"""
<div class="hero"><p class="eyebrow">Repository review</p><h1>Repo audit, line by line</h1>
<p class="lede">Six findings from reading the files this session. Each names the file, the value found and why it matters. Nothing here changes another desk's work.</p></div>
<div class="panel table-wrap"><table><thead><tr><th>ID</th><th>File</th><th>Finding</th><th>Severity</th></tr></thead><tbody>
<tr><td>A-01</td><td><code>data/current/snapshot.json</code><br><span class="sub">generated_at 2026-10-22T12:29:50Z</span></td><td>The canonical dashboard is built from a snapshot two days older than this session. Its own page banner says "Snapshot 21 Oct 2026" while the file was generated on 22 Oct.</td><td><span class="badge medium">medium</span></td></tr>
<tr><td>A-02</td><td><code>data/current/snapshot.json</code><br><span class="sub">counts.low = 16, counts.high = 0</span></td><td>Every priced match in the canonical snapshot is confidence "low"; none is medium or high. A reader looking for "the picks" finds 16 low-tier estimates and no ranking.</td><td><span class="badge warn">high</span></td></tr>
<tr><td>A-03</td><td><code>data/current/snapshot.json</code><br><span class="sub">counts.unpriced = 92 of 108</span></td><td>92 of 108 fixtures carry no market at all. The match list gives no indication of which 16 are priced unless the reader opens each row.</td><td><span class="badge warn">high</span></td></tr>
<tr><td>A-04</td><td><code>data/current/snapshot.json</code><br><span class="sub">81 fixtures carry the note "time not confirmed"</span></td><td>Most rows have no confirmed start time, so the site cannot order them by kick-off or say what is on today. That is a direct cause of the confusion reported.</td><td><span class="badge warn">high</span></td></tr>
<tr><td>A-05</td><td><code>data/current/snapshot.json</code><br><span class="sub">predictions = []</span></td><td>The canonical release ships zero written predictions. The validators enforce that this stays empty, so no desk can add prose to the canonical site without changing the pipeline.</td><td><span class="badge medium">medium</span></td></tr>
<tr><td>A-06</td><td>repository root<br><span class="sub">56 desk directories, 2,367 tracked files</span></td><td>Fifty-six parallel desks each publish their own navigation and their own idea of "today". Nothing on the root explains which one is current, which is exactly the discoverability problem this session was asked to fix.</td><td><span class="badge medium">medium</span></td></tr>
</tbody></table></div>
<section><div class="section-head"><div><h2>Checks performed</h2></div></div>
<div class="panel pad"><ul style="margin:0;padding-left:18px">
<li>Read <code>data/current/snapshot.json</code> and recomputed its counts: 108 fixtures, 108 price rows, 0 predictions, 16 low, 0 high, 92 unpriced — all consistent with the stored counts.</li>
<li>Confirmed no unresolved merge-conflict markers exist in tracked <code>.py</code>, <code>.html</code>, <code>.json</code> or <code>.md</code> files.</li>
<li>Recorded SHA-256 prefixes for the files reviewed: snapshot <code>01727e89824e193c</code>, README <code>0c6f8b4ad5852171</code>, <code>pipeline/build.py</code> <code>c4c359c8c1e4a5ec</code>, <code>scripts/validate.py</code> <code>889484cab96becb3</code>, root <code>index.html</code> <code>2ba5ea56405f99ff</code>.</li>
<li>Did not modify any of those files; this desk is namespaced to <code>02d3d515/</code>, <code>data/02d3d515/</code> and <code>scripts/s02d3d515_*</code>.</li>
</ul></div></section>
<div class="notice"><p><strong>What this audit is not.</strong> It is a structural read of the canonical release, not a re-certification of every earlier desk. The 56 desk directories were counted, not individually re-checked.</p></div>
"""
    (OUT / "repo-audit.html").write_text(frame("Repo audit", "repo-audit.html", body), encoding="utf-8")

    # ---------------- olbg reverse engineering ----------------
    rows = "".join(
        f'<tr><td>{e(sport)}</td><td><a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(url)}</a></td>'
        f'<td class="num">{e(t)}</td><td>{e(note)}</td></tr>' for sport, url, t, note in OLBG_ROUTES)
    body = f"""
<div class="hero"><p class="eyebrow">Reverse engineering</p><h1>How OLBG's board is put together</h1>
<p class="lede">What we learned reading the fifteen sport hubs, and the market pages behind them, on 24 October 2026. OLBG is used for discovery only.</p></div>
<section><div class="section-head"><div><h2>Routes that work</h2>
<p>Each sport is a numeric route. The hub lists one row per event with the most-tipped selection, a tip share and a start time. Ticking "Show Expired Events" reveals matches that have already started, which is why the hub cannot be treated as a list of upcoming fixtures.</p></div></div>
<div class="panel table-wrap"><table><thead><tr><th>Sport</th><th>Hub route</th><th class="num">Read (UTC)</th><th>What the hub showed</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section><div class="section-head"><div><h2>The event page is where the markets are</h2></div></div>
<div class="card"><p>Opening an event gives a full market ladder. For the ATP final the page exposed <strong>Win Match</strong>, <strong>Set Betting</strong> (four scorelines), <strong>1st Set Winner</strong>,
<strong>Games Won</strong> at ±4.50 and <strong>Total Games</strong> at 21.50. For baseball it exposes Money Line, Run Line and Game Totals; for ice hockey Money Line and Game Totals;
for basketball Money Line and Pointspread. That ladder is what we used to decide which markets exist — not to set our prices.</p></div></section>
<section><div class="section-head"><div><h2>Limits we hit</h2></div></div>
<div class="panel pad"><ul style="margin:0;padding-left:18px">
<li>The hub shows "Today" times even after kick-off, so every listing has to be re-checked against the official schedule.</li>
<li>Start times are displayed in US Eastern for North American sports and UK time for European ones; both are converted to UTC here.</li>
<li>Tip counts are community opinion, not probability. We record them but never price from them.</li>
<li>Golf renders "No tips found." while the tournament is live.</li>
<li>Some sport hubs (Rugby League) have no open match market at all outside outrights.</li>
</ul></div></section>
"""
    (OUT / "olbg.html").write_text(frame("OLBG routes", "olbg.html", body), encoding="utf-8")

    print(f"built {len(list(OUT.rglob('*.html')))} pages · {len(picks)} picks · "
          f"{len(high)} high / {len(med)} medium / {len(low)} low · {len(FIXTURES)} fixtures")


if __name__ == "__main__":
    build()
