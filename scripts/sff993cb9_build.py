"""Build the ff993cb9 desk site into ff993cb9/ and data mirrors into data/ff993cb9/."""
import csv, html, io, json, math, os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import sff993cb9_data as D1
import sff993cb9_data2 as D2

OUT = ROOT / "ff993cb9"
DATA_OUT = ROOT / "data" / "ff993cb9"
PICKS = D1.PICKS + D2.PICKS2
SPORTS = D1.SPORTS
SNAP = D1.SNAPSHOT_LABEL

def conf(p):
    if 0.70 <= p <= 0.7142857: return "High"
    if p >= 0.55: return "Medium"
    return "Low"

def amer(p):
    if p >= 0.5: return -round(100 * p / (1 - p))
    return round(100 * (1 - p) / p)

def fam(p):
    return f"{amer(p):+d}"

def dec(p): return round(1 / p, 3)

for pk in PICKS:
    pk["confidence"] = conf(pk["prob"])
    pk["fair_american"] = fam(pk["prob"])
    pk["fair_decimal"] = dec(pk["prob"])
    pk["words"] = len(pk["prediction"].split())
    pk["sport_name"] = D1.SPORT_NAME[pk["sport"]]

def e(x): return html.escape("" if x is None else str(x), quote=True)
def ext(url, label): return f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} ↗</a>'

CSS = """
:root{--ink:#17251f;--muted:#5b6f66;--line:#dfe7e2;--bg:#f6f8f7;--card:#fff;--green:#0f6b45;--green2:#e7f2ec;--amber:#8a5a00;--amber2:#fdf3df;--grey:#eef1ef;--red:#8e2f2f;--red2:#fbeaea}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--green)}h1{font-size:30px;line-height:1.2;margin:0 0 12px}h2{font-size:22px;margin:26px 0 10px}h3{font-size:17px;margin:0 0 6px}p{margin:0 0 12px}
.wrap{max-width:1160px;margin:0 auto;padding:0 20px}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.toprow{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;align-items:center;padding:12px 0 4px}
.brand{font-weight:800;text-decoration:none;color:var(--ink);font-size:18px}.brand small{display:block;font-weight:600;color:var(--muted);font-size:11px;letter-spacing:.08em;text-transform:uppercase}
nav.main{display:flex;gap:4px;flex-wrap:wrap;padding:8px 0 12px}nav.main a{padding:6px 11px;border-radius:999px;text-decoration:none;color:var(--muted);font-size:14px;border:1px solid transparent}
nav.main a.active{background:var(--green2);color:var(--green);border-color:#cfe3d8;font-weight:700}
main{padding:26px 0 60px}.lede{font-size:17px;color:var(--muted);max-width:82ch}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:0 0 18px}
.highlight{border-color:#bcd6c8;background:linear-gradient(180deg,#eff7f1,#fff)}
.where{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:14px 0}
.where a{display:block;background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--ink)}
.where a b{display:block;color:var(--green);margin-bottom:2px}.where a small{color:var(--muted)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:0 0 18px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px}.kpi b{display:block;font-size:27px;line-height:1.1}.kpi small{color:var(--muted)}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff;margin:0 0 18px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);background:#fbfcfb}
.pick{font-weight:700}.num{font-variant-numeric:tabular-nums;font-weight:700;white-space:nowrap}.muted{color:var(--muted)}.small{font-size:13px}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;white-space:nowrap}
.badge.High{background:var(--green);color:#fff}.badge.Medium{background:var(--amber2);color:var(--amber)}.badge.Low{background:var(--grey);color:var(--muted)}
.badge.none{background:var(--red2);color:var(--red)}
.article{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:0 0 14px}
.article .meta{font-size:13px;color:var(--muted);margin-bottom:8px}.article .sel{font-size:18px;font-weight:800}
.flag{background:#fff;border:1px solid var(--line);border-left:4px solid var(--amber);border-radius:12px;padding:16px 18px;margin:0 0 14px}
.notice{background:var(--amber2);border:1px solid #ecd9ae;color:#6b4700;border-radius:12px;padding:12px 16px;margin:0 0 18px;font-size:14px}
footer.foot{border-top:1px solid var(--line);padding:18px 0 40px;color:var(--muted);font-size:13px}
ul.plain{padding-left:20px}ul.plain li{margin-bottom:6px}code{background:#f0f4f2;padding:1px 5px;border-radius:5px;font-size:13px}
@media(max-width:820px){h1{font-size:25px}}
"""

NAV = [("index.html","★ Executive summary"),("picks.html","All picks"),("predictions.html","Written predictions"),
       ("matches.html","Every match"),("sports.html","Sports"),("markets.html","Our lines"),
       ("flagged.html","Flagged for review"),("sources.html","Sources"),("methodology.html","Method"),
       ("olbg.html","Inside OLBG"),("repo-audit.html","Repo audit")]

def page(title, active, body, depth=0):
    prefix = "../" * depth
    nav = "".join(f'<a class="{"active" if u==active else ""}" href="{prefix}{u}">{e(t)}</a>' for u, t in NAV)
    n_high = sum(1 for p in PICKS if p["confidence"] == "High")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Source-linked written predictions for upcoming matches across 15 sports. Independent research desk, not affiliated with OLBG.">
<title>{e(title)} · OLBG Research Desk (ff993cb9)</title>
<link rel="stylesheet" href="{prefix}assets/style.css"></head>
<body data-snapshot="{D1.SNAPSHOT}">
<header class="top"><div class="wrap"><div class="toprow">
<a class="brand" href="{prefix}index.html">OLBG Research Desk — Picks Desk<small>Independent · every row source-linked · snapshot {e(SNAP)}</small></a>
<span class="small muted">{n_high} High · {len(PICKS)} written picks · 15 sports</span></div>
<nav class="main" aria-label="Sections">{nav}</nav></div></header>
<main><div class="wrap">{body}</div></main>
<footer class="foot"><div class="wrap"><p>Independent research, not betting advice and not affiliated with OLBG. Every price on this desk is our own originated fair (no-vig) estimate. 18+ only.</p>
<p>Snapshot {e(SNAP)} · Desk <code>ff993cb9</code> · <a href="{prefix}flagged.html">Flagged for review</a> · <a href="{prefix}sources.html">Sources with read times</a></p></div></footer>
</body></html>"""

def pick_row(p, prefix=""):
    return (f'<tr id="{e(p["id"])}"><td class="small">{e(p["start"])}</td>'
            f'<td>{e(p["sport_name"])}<br><span class="small muted">{e(p["competition"])}</span></td>'
            f'<td>{e(p["match"])}</td>'
            f'<td class="pick">▶ {e(p["selection"])}<br><span class="small muted">{e(p["market"])}</span></td>'
            f'<td><span class="num">{e(p["fair_american"])}</span><br><span class="small muted">{p["prob"]*100:.1f}% · {p["fair_decimal"]:.3f} dec</span></td>'
            f'<td><span class="badge {e(p["confidence"])}">{e(p["confidence"])}</span></td>'
            f'<td class="small"><a href="{prefix}predictions.html#{e(p["id"])}">Read the {p["words"]}-word prediction</a><br>{ext(p["official"], p["official_label"])}</td></tr>')

PICK_HEAD = "<tr><th>Start</th><th>Sport / competition</th><th>Match</th><th>▶ OUR PICK (selection · market)</th><th>Our fair price</th><th>Confidence</th><th>Prediction + official source</th></tr>"

def picks_table(rows, prefix=""):
    return f'<div class="table-wrap"><table><thead>{PICK_HEAD}</thead><tbody>' + "".join(pick_row(p, prefix) for p in rows) + "</tbody></table></div>"

def article(p):
    return (f'<article class="article" id="{e(p["id"])}"><div class="meta">{e(p["sport_name"])} · {e(p["competition"])} · {e(p["start"])} · '
            f'<span class="badge {e(p["confidence"])}">{e(p["confidence"])}</span> {p["prob"]*100:.1f}% · our fair price <span class="num">{e(p["fair_american"])}</span> ({p["fair_decimal"]:.3f} decimal)</div>'
            f'<h3>{e(p["match"])}</h3><p class="sel">▶ Pick: {e(p["selection"])} <span class="muted small">({e(p["market"])})</span></p>'
            f'<p>{e(p["prediction"])}</p>'
            f'<p class="small muted">Key figures on the official page: {e(p["evidence"])} · {ext(p["official"], p["official_label"])} · {ext(p["olbg"], "OLBG " + p["sport_name"] + " hub (discovery)")} · Pick ID {e(p["id"])} · {p["words"]} words</p></article>')

def by_sport(slug): return [p for p in PICKS if p["sport"] == slug]

def distinct_matches(rows):
    seen = {}
    for p in rows: seen.setdefault((p["competition"], p["match"]), p)
    return list(seen.values())

# ---------- INDEX ----------
def build_index():
    highs = [p for p in PICKS if p["confidence"] == "High"]
    best = []
    for slug, name, hub in SPORTS:
        rows = by_sport(slug)
        best.append((slug, name, max(rows, key=lambda x: x["prob"]) if rows else None))
    n_matches = len(distinct_matches(PICKS)) + len(D2.TRACKED)
    NOPICK = '<span class="badge none">No pick \u2014 see Flagged</span>'
    def _top(slug):
        _rows = by_sport(slug)
        return ('\u25b6 ' + e(max(_rows, key=lambda x: x['prob'])['selection'])) if _rows else NOPICK
    sport_rows = "".join(
        f'<tr><td><a href="sports/{slug}.html"><b>{e(name)}</b></a></td><td class="num">{len(by_sport(slug))}</td>'
        f'<td class="num">{len(distinct_matches(by_sport(slug)))}</td>'
        f'<td class="num">{sum(1 for p in by_sport(slug) if p["confidence"]=="High")}</td>'
        f'<td class="small">{_top(slug)}</td>'
        f'<td class="small"><a href="sports/{slug}.html">Sport page</a> · {ext(hub, "OLBG hub")}</td></tr>'
        for slug, name, hub in SPORTS)
    best_rows = "".join(
        (f'<tr><td><a href="sports/{slug}.html"><b>{e(name)}</b></a></td><td class="small">{e(p["match"])}<br><span class="muted">{e(p["start"])}</span></td>'
         f'<td class="pick">▶ {e(p["selection"])}<br><span class="small muted">{e(p["market"])}</span></td>'
         f'<td><span class="num">{e(p["fair_american"])}</span><br><span class="small muted">{p["prob"]*100:.1f}%</span></td>'
         f'<td><span class="badge {e(p["confidence"])}">{e(p["confidence"])}</span></td>'
         f'<td class="small"><a href="predictions.html#{e(p["id"])}">Why — read it</a></td></tr>') if p else
        (f'<tr><td><a href="sports/{slug}.html"><b>{e(name)}</b></a></td><td colspan="4"><span class="badge none">No pick today</span> '
         f'<span class="small">Meetings are tracked, but no official runner form was read — nothing is tipped blind.</span></td>'
         f'<td class="small"><a href="flagged.html#F-FF-01">See flag F-FF-01</a></td></tr>')
        for slug, name, p in best)
    body = f"""
<h1>Today's picks — executive summary</h1>
<div class="panel highlight">
<p style="font-size:18px"><strong>The picks are on this page.</strong> The ⭐ High-confidence picks are in the first table below.
The single best pick in <em>every</em> sport is in the second table. The full written reason for every pick is on
<a href="predictions.html">Written predictions</a> — use the “Why — read it” link on any row.</p>
<div class="where">
<a href="#high"><b>⭐ 1 · High-confidence picks</b><small>First table on this page — {len(highs)} picks</small></a>
<a href="#best"><b>2 · Best pick in every sport</b><small>Second table — one headline pick per sport (15 sports)</small></a>
<a href="picks.html"><b>3 · Every pick, by sport</b><small>All {len(PICKS)} picks grouped sport by sport</small></a>
<a href="predictions.html"><b>4 · Every written prediction</b><small>Full 45–95 word analysis per pick, nothing bare</small></a>
<a href="matches.html"><b>5 · Every match we looked at</b><small>Including matches with no pick, and exactly why</small></a>
<a href="sports.html"><b>6 · One page per sport</b><small>15 sport pages with picks + predictions together</small></a>
</div>
<p class="small" style="margin-bottom:0">How to read a row: <b>▶ OUR PICK</b> is the selection and its market. <b>Our fair price</b> is the price <em>we</em> originated
(no bookmaker margin) — American odds, with our estimated win percentage and the decimal equivalent underneath. <b>Confidence</b> is High / Medium / Low —
High is only awarded at a 70%+ estimated chance <em>and</em> a fair price inside the brief's −250 to +10000 window, which mathematically confines High to
70.0–71.4% (see <a href="methodology.html">Method</a>). The aim was 5–10 written picks per sport. Where a sport's calendar or the official evidence
would not support that honestly, the shortfall is stated plainly on <a href="flagged.html">Flagged for review</a> — it was never filled with guesses.</p>
</div>
<section class="kpis">
<div class="kpi"><b>{len(highs)}</b><small>⭐ High-confidence picks</small></div>
<div class="kpi"><b>{len(PICKS)}</b><small>Picks, each with a unique written prediction</small></div>
<div class="kpi"><b>{n_matches}</b><small>Matches / meetings tracked</small></div>
<div class="kpi"><b>{sum(1 for s,_,_ in SPORTS if by_sport(s))} / 15</b><small>Sports with at least one pick</small></div>
<div class="kpi"><b>{len(D2.FLAGS)}</b><small>Items flagged for your review</small></div>
</section>
<h2 id="high">⭐ High-confidence picks</h2>
<p class="lede">Three picks clear both hurdles this snapshot: an estimated chance of 70% or better, and a fair price no shorter than −250.
One puck-line, one set handicap, one short-priced cricket favourite — each written up in full.</p>
{picks_table(highs)}
<h2 id="best">Best pick in every sport</h2>
<p class="lede">If you read nothing else, read this table: the highest-rated pick in each of the 15 requested sports.
Greyhounds is the one honest blank — five meetings are tracked but no official runner form was read, so no dog is tipped.</p>
<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Match</th><th>▶ Best pick</th><th>Our fair price</th><th>Confidence</th><th>The reasoning</th></tr></thead><tbody>{best_rows}</tbody></table></div>
<h2>Coverage by sport — where everything lives</h2>
<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Written picks</th><th>Distinct matches with a pick</th><th>High</th><th>Top pick in that sport</th><th>Pages</th></tr></thead><tbody>{sport_rows}</tbody></table></div>
<div class="notice"><strong>Sports below the 5-per-sport aim, and why:</strong> Snooker (one match exists — Sunday's final), Rugby Union (two Sunday fixtures before
the 6 Nov Nations Championship), Baseball (two series in the window), Handball (three matches priced from the groups whose official tables rendered) and Greyhounds (no official form read).
Each carries extra markets per match instead of invented fixtures. Full detail: <a href="flagged.html">Flagged for review</a>.</div>
<p class="small muted">Every fact in every prediction — records, scores, qualifying times, semi-final results — was read from the official source linked on its row at the snapshot time above.
OLBG was used only to discover which markets exist. Prices are our own: see <a href="markets.html">Our lines</a> for both sides of every market we priced.</p>
"""
    return page("Executive summary — today's picks", "index.html", body)

def build_picks():
    parts = ["<h1>All picks, by sport</h1><p class=\"lede\">Every pick on this desk, grouped by sport. The selection is always in the <b>▶ OUR PICK</b> column. "
             "Click “Read the prediction” on any row for the full written analysis.</p>"]
    for slug, name, hub in SPORTS:
        rows = by_sport(slug)
        parts.append(f'<h2 id="{slug}">{e(name)} — {len(rows)} pick{"s" if len(rows)!=1 else ""}</h2>')
        if rows: parts.append(picks_table(rows))
        else: parts.append('<div class="panel"><p style="margin:0"><span class="badge none">No picks</span> Meetings are tracked on the <a href="matches.html">matches page</a>, but no official runner form was read this session, so nothing is tipped. See <a href="flagged.html#F-FF-01">flag F-FF-01</a>.</p></div>')
    return page("All picks by sport", "picks.html", "\n".join(parts))

def build_predictions():
    parts = ["<h1>Written predictions</h1><p class=\"lede\">One full written prediction per pick — form, recent results and the statistics behind the number, "
             "with the selection named in the first line of every card. No bare winners anywhere on this page.</p>"]
    for slug, name, hub in SPORTS:
        rows = by_sport(slug)
        if not rows: continue
        parts.append(f'<h2>{e(name)}</h2>' + "".join(article(p) for p in rows))
    return page("Written predictions", "predictions.html", "\n".join(parts))

def build_matches():
    parts = ["<h1>Every match we looked at</h1><p class=\"lede\">Part 1: matches carrying at least one pick. Part 2: everything else tracked — fixtures and meetings "
             "with no pick, each with the exact reason and its official source. A blank always means “not read from an official source”, never “forgotten”.</p><h2>Matches with a pick</h2>"]
    rows = "".join(
        f'<tr><td class="small">{e(p["start"])}</td><td>{e(p["sport_name"])}</td><td>{e(p["match"])}<br><span class="small muted">{e(p["competition"])}</span></td>'
        f'<td class="small">' + "<br>".join(f'▶ <a href="predictions.html#{e(q["id"])}">{e(q["selection"])}</a> <span class="badge {e(q["confidence"])}">{e(q["confidence"])}</span>' for q in PICKS if q["match"]==p["match"] and q["competition"]==p["competition"]) + "</td>"
        f'<td class="small">{ext(p["official"], p["official_label"])}</td></tr>'
        for p in distinct_matches(PICKS))
    parts.append(f'<div class="table-wrap"><table><thead><tr><th>Start</th><th>Sport</th><th>Match</th><th>Pick(s) on this match</th><th>Official source</th></tr></thead><tbody>{rows}</tbody></table></div>')
    parts.append("<h2>Tracked with no pick</h2>")
    rows2 = "".join(
        f'<tr><td class="small">{e(m["start"])}</td><td>{e(D1.SPORT_NAME[m["sport"]])}</td><td>{e(m["match"])}<br><span class="small muted">{e(m["competition"])}</span></td>'
        f'<td><span class="badge none">{e(m["status"])}</span></td><td class="small">{e(m["reason"])}</td><td class="small">{ext(m["official"], m["official_label"])}</td></tr>'
        for m in D2.TRACKED)
    parts.append(f'<div class="table-wrap"><table><thead><tr><th>When</th><th>Sport</th><th>Match / meeting</th><th>Status</th><th>Why there is no price</th><th>Official source</th></tr></thead><tbody>{rows2}</tbody></table></div>')
    return page("Every match tracked", "matches.html", "\n".join(parts))

def build_markets():
    rows = "".join(
        f'<tr><td class="small">{e(p["id"])}</td><td>{e(p["sport_name"])}</td><td class="small">{e(p["match"])}</td><td>{e(p["market"])}</td>'
        f'<td class="pick">▶ {e(p["selection"])}<br><span class="num">{e(p["fair_american"])}</span> <span class="small muted">({p["fair_decimal"]:.3f} · {p["prob"]*100:.1f}%)</span></td>'
        f'<td class="small">Other side of the same line: <span class="num">{fam(1-p["prob"])}</span> ({(1-p["prob"])*100:.1f}%)</td>'
        f'<td><span class="badge {e(p["confidence"])}">{e(p["confidence"])}</span></td></tr>' for p in PICKS)
    body = f"""<h1>Our originated lines</h1>
<p class="lede">Every price below was built here, from the official figures quoted in the matching prediction — never copied from a bookmaker or from OLBG.
They are <b>fair (no-vig) prices</b>: the two sides of each line sum to exactly 100%, so “other side” is the honest complement of our estimate.
For outright, podium and top-5/top-6 positions markets the “other side” means the rest of the field combined.</p>
<p>Markets priced, by type: match winner, puck/points/set/leg handicaps, match and team totals, total sets/frames, tournament outright, race winner,
podium, top-3/5/6 finishes and a draw-no-bet. The full method — how a record becomes a percentage — is on the <a href="methodology.html">Method</a> page.</p>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Market</th><th>▶ Our line: selection · fair price</th><th>Fair price, other side</th><th>Confidence</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Markets deliberately withheld</h2>
<ul class="plain">
<li><b>Short-priced match-winner markets above the band</b> (e.g. India Women to beat Zimbabwe Women, New Zealand to beat the Cook Islands): our win estimates imply prices shorter than −250, outside the brief's window, so a team-total or handicap line inside the window is priced instead.</li>
<li><b>NBA totals and spreads:</b> one or two games of scoring data cannot support a defensible total; moneylines only, all capped at Medium.</li>
<li><b>Greyhound race winners:</b> no official racecard form read — no line at all (flag F-FF-01).</li>
<li><b>Player props everywhere:</b> no official player-stat lines were read, so no scorer, points or wicket props are offered.</li>
</ul>"""
    return page("Our originated lines", "markets.html", body)

def build_sports_index():
    cards = "".join(
        f'<div class="kpi"><b style="font-size:19px"><a href="sports/{slug}.html">{e(name)}</a></b>'
        f'<small>{len(by_sport(slug))} written picks · {len(distinct_matches(by_sport(slug)))} matches priced · '
        f'{sum(1 for p in by_sport(slug) if p["confidence"]=="High")} High<br>{ext(hub, "OLBG hub")}</small></div>'
        for slug, name, hub in SPORTS)
    return page("Sports", "sports.html", f'<h1>Sports</h1><p class="lede">The exact fifteen sports requested. Each sport page holds that sport\'s picks table <em>and</em> its full written predictions in one place.</p><section class="kpis">{cards}</section>')

def build_sport(slug, name, hub):
    rows = by_sport(slug)
    tracked = [m for m in D2.TRACKED if m["sport"] == slug]
    body = f'<h1>{e(name)}</h1><p class="lede">{len(rows)} written pick{"s" if len(rows)!=1 else ""} across {len(distinct_matches(rows))} match{"es" if len(distinct_matches(rows))!=1 else ""}. '
    body += f'Discovery: {ext(hub, "OLBG " + name + " hub")}.</p>'
    if rows:
        body += "<h2>Picks</h2>" + picks_table(rows, prefix="../") + "<h2>Written predictions</h2>" + "".join(article(p) for p in rows)
    else:
        body += '<div class="panel"><p style="margin:0"><span class="badge none">No picks at this snapshot</span> The meetings below are real and source-linked, but no official form was read, so this desk tips nothing. See <a href="../flagged.html#F-FF-01">flag F-FF-01</a>.</p></div>'
    if tracked:
        tr = "".join(f'<tr><td class="small">{e(m["start"])}</td><td>{e(m["match"])}<br><span class="small muted">{e(m["competition"])}</span></td><td><span class="badge none">{e(m["status"])}</span></td><td class="small">{e(m["reason"])}</td><td class="small">{ext(m["official"], m["official_label"])}</td></tr>' for m in tracked)
        body += f'<h2>Also tracked (no pick)</h2><div class="table-wrap"><table><thead><tr><th>When</th><th>Match / meeting</th><th>Status</th><th>Why no price</th><th>Official source</th></tr></thead><tbody>{tr}</tbody></table></div>'
    return page(f"{name} picks and predictions", "sports.html", body, depth=1)

def build_flagged():
    items = "".join(f'<div class="flag" id="{e(fid)}"><h3>{e(fid)} — {e(t)}</h3><p>{e(d)}</p><p class="small" style="margin:0">Check it yourself: {ext(u, "Official source")}</p></div>' for fid, t, d, u in D2.FLAGS)
    return page("Flagged for review", "flagged.html",
        f'<h1>Flagged for review</h1><p class="lede">Everything that could not be confirmed from an official source, every shortfall against the brief, and every disagreement found — published, not hidden, and none of it blocks the picks that <em>are</em> supported. Ask for changes against these IDs.</p>{items}')

def build_sources():
    rows = "".join(f'<tr><td>{e(pub)}</td><td>{e(title)}</td><td class="small">{ext(url, url.replace("https://","")[:64])}</td><td class="small num">{e(read)}</td><td class="small">{e(used)}</td></tr>'
                   for pub, title, url, read, used in D1.SOURCES)
    return page("Sources", "sources.html",
        f'<h1>Sources</h1><p class="lede">Every page read to build this desk, with the exact URL and the UTC time it was read. Governing bodies, leagues and tours are the fact sources; OLBG appears once, as discovery only. One scorecard publisher (ESPNcricinfo) is segregated in its own row — see flag F-FF-07.</p>'
        f'<div class="table-wrap"><table><thead><tr><th>Publisher</th><th>Page</th><th>URL</th><th>Read (UTC)</th><th>What it was used for</th></tr></thead><tbody>{rows}</tbody></table></div>')

def build_method():
    body = """<h1>Method — how a price and a rating are made</h1>
<h2>1. Discovery (OLBG)</h2><p>OLBG's fifteen sport hubs tell us which matches and which headline markets (“Win Match”) exist. That is all they are used for. Tip counts and percentages on OLBG are counts of member tips, not probabilities, and they never enter a price. The route map is on the <a href="olbg.html">Inside OLBG</a> page.</p>
<h2>2. Facts (official sources only)</h2><p>For each candidate match we read the governing body / league / tour page linked on its row: fixture, venue, start time, season records, points and set totals, qualifying times, semi-final scores. If the input a price needs (for example both teams' records) was not on an official page as read, the match is listed with no price and the missing input named.</p>
<h2>3. Originating the price</h2><p>From those official figures we estimate a win/cover probability <em>p</em> for each selection (rating gaps from points/goals/set differentials, home advantage, head-to-head meeting in the same competition where an official table records it). The published price is the fair, margin-free conversion: decimal = 1/<em>p</em>; American = −100·<em>p</em>/(1−<em>p</em>) for favourites, +100·(1−<em>p</em>)/<em>p</em> for outsiders. Estimates are deliberately conservative early in a season — one or two games of form can never produce a rating above Medium on this desk.</p>
<h2>4. Confidence and the −250…+10000 window</h2>
<div class="table-wrap"><table><thead><tr><th>Rating</th><th>Estimated chance</th><th>Fair American price</th></tr></thead><tbody>
<tr><td><span class="badge High">High</span></td><td>70.0% – 71.4%</td><td>−250 to −233 (must also sit inside −250…+10000)</td></tr>
<tr><td><span class="badge Medium">Medium</span></td><td>55.0% – 69.9%</td><td>−232 to +10000</td></tr>
<tr><td><span class="badge Low">Low</span></td><td>below 55%, or thin evidence at any price</td><td>inside the window</td></tr></tbody></table></div>
<p>The brief asks for high-confidence picks that are both “better than 70%” and priced between −250 and +10000 (not short-priced market chalk). Applied honestly to a fair price, 70% and −250 meet at 71.4%, so High is necessarily a narrow slice. Where a side is stronger than that (India Women, New Zealand in the RLWC), this desk prices a handicap or team-total line that lands back inside the window instead of dressing up a −900 favourite as analysis.</p>
<h2>5. The written prediction</h2><p>Each pick carries a unique prediction of at least 30 words (this desk: 45–95 words) naming the selection, the team or player, current form, recent results and the specific official figures behind the percentage. Injury or lineup claims appear only where an official list was read (on this desk: the RLWC team lists). The build is machine-checked for word count, for repeated six-word phrases across predictions, and for the band and rating rules above.</p>
<h2>6. What would change a price</h2><p>Prices are frozen at the snapshot time on every page. Team news, a confirmed finalist (snooker), Game 2's result (both baseball series) and Sunday's results feeding later rounds (RLWC, Basel) all move fair prices — flagged where relevant so you can re-check before acting.</p>"""
    return page("Methodology", "methodology.html", body)

def build_olbg():
    rows = "".join(f'<tr><td>{e(name)}</td><td class="small">{ext(hub, hub.replace("https://www.olbg.com",""))}</td><td class="num">{hub.rsplit("/",1)[-1]}</td><td class="num">{len(by_sport(slug))}</td></tr>' for slug, name, hub in SPORTS)
    body = f"""<h1>Inside OLBG — how the site is put together</h1>
<p class="lede">Read live on 24 Oct 2026. This desk is independent of OLBG; the notes below exist so you can cross-check any pick against the market listing it came from.</p>
<h2>Sport hubs (discovery entry points)</h2>
<div class="table-wrap"><table><thead><tr><th>Sport (this desk)</th><th>OLBG hub route</th><th>OLBG sport ID</th><th>Written picks here</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Event pages</h2>
<ul class="plain">
<li>Hub pattern: <code>/betting-tips/&lt;Sport&gt;/&lt;id&gt;</code> — e.g. <code>/betting-tips/Tennis/3</code>.</li>
<li>Event pattern observed on the tennis hub: <code>/betting-tips/Tennis/All_Tennis/All_Events/&lt;Player_A&gt;_vs_&lt;Player_B&gt;/3?event_id=902207</code> — a sport slug, an “All_Events” bucket, the two names, then a numeric <code>event_id</code>.</li>
<li>Each listing shows a headline market label (“Win Match”), an <code>n/m Win Tips</code> count with a percentage, and a comments count. The percentage is the share of member tips on that selection — a popularity count, not a win probability — and several Basel listings showed “100%” from a single tip. This desk never converts it into a price.</li>
<li>Hub clocks are display artefacts: every Basel first-round match was stamped “26 Oct 06:00”, and one listing (“Ben Shelton vs Casper Ruud”) did not match the ATP's official draw at all (flag F-FF-10). Fixtures, pairings and times on this desk therefore always come from the official source, never the hub.</li>
</ul>
<h2>What we take from OLBG, and what we never take</h2>
<ul class="plain"><li><b>Taken:</b> that a match and a market type are being offered for tipping (so the selection is genuinely “available on OLBG”).</li>
<li><b>Never taken:</b> scores, records, odds, tip percentages, tipster comments — none of them are official facts, and none appear in any price or prediction here.</li></ul>"""
    return page("Inside OLBG", "olbg.html", body)

def build_audit():
    hexdirs = [d for d in ROOT.iterdir() if d.is_dir() and re.fullmatch(r"[0-9a-f]{8}", d.name)]
    root_html = list(ROOT.glob("*.html"))
    coord_kb = (ROOT / "COORDINATION.md").stat().st_size // 1024
    body = f"""<h1>Repo audit — what was already here (line by line)</h1>
<p class="lede">Read at the start of this session, before any new files were written. Counts below were measured from the working tree at build time, so they stay honest as the repo grows.</p>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Finding</th><th>Evidence in the repo</th><th>What this desk did about it</th></tr></thead><tbody>
<tr><td>A1</td><td>The live root site is a single dated desk, not a rolling service: its own README says only 2 of the 15 requested sports were priced (NHL, MLB), with 11 picks.</td><td><code>README.md</code> (“15 sports requested, 2 priced… 11 picks: 6 High, 5 Medium”); <code>index.html</code> header stamp 24 Oct 2026 18:00 UTC.</td><td>New desk under <code>ff993cb9/</code> covers all 15 sports with an explicit per-sport count table.</td></tr>
<tr><td>A2</td><td>The repository root has accumulated <b>{len(hexdirs)}</b> eight-hex session directories plus <b>{len(root_html)}</b> root HTML files — the “too confusing to find the picks” problem in physical form.</td><td>Directory listing at repo root (measured at build).</td><td>This desk is one self-contained folder whose first page is the picks; nothing was added to root.</td></tr>
<tr><td>A3</td><td><code>COORDINATION.md</code> is a {coord_kb} KB shared board with 90+ numbered session sections; claims are append-only and several older tasks still read “in progress” long after their desks shipped.</td><td><code>COORDINATION.md</code> §1 table and §§91–92 receipts.</td><td>Claimed as TFF99 in a new §93 before starting, pushed immediately, per the board's own rules; receipts appended at the end.</td></tr>
<tr><td>A4</td><td>Canonical publishing is allow-list based: a new desk 404s on GitHub Pages unless it is registered in the publisher's archive list (this bit at least two previous sessions).</td><td><code>pipeline/build.py</code> <code>ARCHIVE</code> list; the §92.2 receipt describing the same one-line fix.</td><td>Declared in the claim upfront: exactly one additive <code>ARCHIVE</code> line for <code>ff993cb9/index.html</code>, nothing else in the canonical pipeline touched.</td></tr>
<tr><td>A5</td><td>Previous desks repeatedly resolved the “&gt;70% and −250…+10000” brief differently (some used a 60% floor, producing more “High” picks at prices that break the stated conjunction).</td><td><code>README.md</code> band-rule section (60% floor) vs the strict 70% rule in later session reports.</td><td>This desk applies the strict reading (70.0–71.4% ⇒ −250…−233) and shows the arithmetic on the Method page.</td></tr>
<tr><td>A6</td><td>Stale root data files from the first desk (October 21) still sit beside current ones with near-identical names.</td><td><code>data/fixtures.json</code>, <code>data/lines.json</code> next to <code>data/desk/</code> and 70+ per-session folders under <code>data/</code>.</td><td>All new data is namespaced under <code>data/ff993cb9/</code> with the snapshot time inside every file.</td></tr>
<tr><td>A7</td><td>One legacy page is over 2 MB of markup, which is why “find the pick” failed for the user even when the pick existed.</td><td><code>markets.html</code> ≈ 2.24 MB, <code>verification.html</code> ≈ 0.90 MB (file listing, 24 Oct).</td><td>This desk caps itself at small, single-purpose pages with the picks in the first table.</td></tr>
</tbody></table></div>
<p class="small muted">Nothing above accuses any earlier desk of inventing data — the ones sampled carry the same official-source discipline. The failure was findability, which is a presentation bug, and it is the bug this desk is built to fix.</p>"""
    return page("Repo audit", "repo-audit.html", body)

def main():
    (OUT / "sports").mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "assets" / "style.css").write_text(CSS)
    pages = {"index.html": build_index(), "picks.html": build_picks(), "predictions.html": build_predictions(),
             "matches.html": build_matches(), "markets.html": build_markets(), "sports.html": build_sports_index(),
             "flagged.html": build_flagged(), "sources.html": build_sources(), "methodology.html": build_method(),
             "olbg.html": build_olbg(), "repo-audit.html": build_audit()}
    for name, doc in pages.items(): (OUT / name).write_text(doc)
    for slug, name, hub in SPORTS: (OUT / "sports" / f"{slug}.html").write_text(build_sport(slug, name, hub))
    # data mirrors
    payload = {"session": "ff993cb9-olbg1", "task": "TFF99", "snapshot_utc": D1.SNAPSHOT,
               "counts": {"picks": len(PICKS), "high": sum(1 for p in PICKS if p["confidence"]=="High"),
                          "medium": sum(1 for p in PICKS if p["confidence"]=="Medium"),
                          "low": sum(1 for p in PICKS if p["confidence"]=="Low"),
                          "matches_with_picks": len(distinct_matches(PICKS)), "tracked_no_pick": len(D2.TRACKED),
                          "flags": len(D2.FLAGS)},
               "picks": PICKS, "tracked": D2.TRACKED, "flags": [dict(id=f[0], title=f[1], detail=f[2], source=f[3]) for f in D2.FLAGS],
               "sources": [dict(publisher=s[0], title=s[1], url=s[2], read_utc=s[3], used_for=s[4]) for s in D1.SOURCES]}
    (DATA_OUT / "desk.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False))
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(["id","sport","competition","match","start","market","selection","prob","fair_american","fair_decimal","confidence","words","official_source"])
    for p in PICKS: w.writerow([p["id"],p["sport"],p["competition"],p["match"],p["start"],p["market"],p["selection"],p["prob"],p["fair_american"],p["fair_decimal"],p["confidence"],p["words"],p["official"]])
    (DATA_OUT / "picks.csv").write_text(buf.getvalue())
    print(f"Built {len(pages)+len(SPORTS)} pages, {len(PICKS)} picks "
          f"(H{payload['counts']['high']}/M{payload['counts']['medium']}/L{payload['counts']['low']}), "
          f"{payload['counts']['matches_with_picks']} priced matches, {len(D2.TRACKED)} tracked, {len(D2.FLAGS)} flags.")

if __name__ == "__main__":
    main()
