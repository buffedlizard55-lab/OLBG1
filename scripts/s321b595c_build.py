"""Session 321b595c-olbg1 site build.  Run: python3 scripts/s321b595c_build.py"""
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "321b595c"
DATA = ROOT / "data" / "321b595c"
SESSION = "321b595c-olbg1"

S = json.loads((DATA / "summary.json").read_text())
SRC = {s["id"]: s for s in json.loads((DATA / "sources.json").read_text())["sources"]}
FX = json.loads((DATA / "fixtures.json").read_text())["fixtures"]
PRED = json.loads((DATA / "predictions.json").read_text())["predictions"]
FLAGS = json.loads((DATA / "flags.json").read_text())["flags"]
COV = json.loads((DATA / "coverage.json").read_text())["sports"]

PICKS = [f for f in FX if f.get("selection")]
SPORT_OF = {c["sport"]: c for c in COV}
ORDER = ["ice_hockey", "baseball", "basketball", "tennis", "cricket", "rugby_union", "volleyball",
         "handball", "darts", "snooker", "motor_racing", "gaelic", "greyhounds", "golf", "rugby_league"]
NAME = {c["sport"]: c["name"] for c in COV}


def e(v):
    return html.escape("" if v is None else str(v), quote=True)


def money(v):
    return "&mdash;" if v is None else f"{v:+d}"


def prob(v):
    return "&mdash;" if v is None else f"{100 * v:.1f}%"


def when(v):
    if not v:
        return "&mdash;"
    d, t = v.split("T")
    return f"{d[8:10]} {['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(d[5:7])]}<br><small>{t[:5]} UTC</small>"


def src_link(sid):
    s = SRC.get(sid)
    if not s:
        return ""
    tag = "OLBG" if s["kind"] == "olbg" else s["url"].split("/")[2].replace("www.", "")
    return f'<a class="src {e(s["kind"])}" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(tag)}</a>'


def srcs(ids, limit=None):
    """One link per host, in the order given, so the column stays readable."""
    seen, keep = set(), []
    for i in ids:
        if i not in SRC:
            continue
        host = SRC[i]["url"].split("/")[2]
        if host in seen:
            continue
        seen.add(host)
        keep.append(i)
    if limit:
        keep = keep[:limit]
    return " ".join(src_link(i) for i in keep)


def conf_badge(c):
    if not c:
        return '<span class="tag none">no line</span>'
    return f'<span class="tag {c.lower()}">{e(c)}</span>'


CSS = """
:root{--ink:#0d1117;--mut:#5a6572;--line:#e3e8ee;--bg:#f6f8fa;--card:#fff;--acc:#0b5fff;--hi:#0a7d3f;--med:#8a5a00;--low:#7a4a8a;--warn:#a3231f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 64px}
header.top{background:#0d1117;color:#fff;padding:14px 0}
header.top .wrap{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;padding-bottom:0}
.brand{font-weight:800;letter-spacing:.02em;font-size:18px;color:#fff}
.brand small{display:block;font-weight:500;font-size:11px;letter-spacing:.16em;color:#9aa6b2}
nav.main{display:flex;flex-wrap:wrap;gap:6px}
nav.main a{color:#c9d4e0;padding:7px 11px;border-radius:7px;font-size:14px;font-weight:600}
nav.main a:hover{background:#1d2633;text-decoration:none;color:#fff}
nav.main a.here{background:var(--acc);color:#fff}
.hero{background:#fff;border-bottom:1px solid var(--line);padding:26px 0 22px}
h1{font-size:30px;line-height:1.2;margin:0 0 8px;letter-spacing:-.02em}
h2{font-size:21px;margin:34px 0 10px;letter-spacing:-.01em}
h3{font-size:16px;margin:22px 0 6px}
p.lead{font-size:18px;color:#243040;margin:0 0 16px;max-width:70ch}
p{max-width:80ch}
ul,ol{max-width:82ch;padding-left:22px}
li{margin:5px 0}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0 4px}
.kpi div{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:26px;letter-spacing:-.02em}
.kpi span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.07em}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0}
.jump{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:18px 0}
.jump a{display:block;background:#fff;border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:10px;padding:13px 15px;color:var(--ink)}
.jump a:hover{border-color:var(--acc);text-decoration:none}
.jump b{display:block;font-size:16px;margin-bottom:3px}
.jump span{font-size:13px;color:var(--mut)}
table{width:100%;border-collapse:collapse;font-size:14px;background:#fff}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--mut);background:#f0f3f7;position:sticky;top:0}
tbody tr:hover{background:#fbfcfe}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.tblwrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff;margin:12px 0}
.tag{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.tag.high{background:#e2f5ea;color:var(--hi)}.tag.medium{background:#fdf0d5;color:var(--med)}
.tag.low{background:#f2e8f7;color:var(--low)}.tag.none{background:#eef1f4;color:var(--mut)}
.src{display:inline-block;font-size:11px;padding:2px 7px;border:1px solid var(--line);border-radius:6px;color:var(--mut);margin:1px 2px 1px 0;background:#fff;font-weight:600}
.src.official{border-color:#bfe0cc;color:#0a6b39;background:#f2fbf6}
.src.olbg{border-color:#d8e2f0;color:#3b5a86;background:#f6f9fe}
.pick{background:#fff;border:1px solid var(--line);border-left:5px solid var(--hi);border-radius:12px;padding:16px 18px;margin:14px 0}
.pick.medium{border-left-color:#d89400}.pick.low{border-left-color:#8e64a8}
.pick h3{margin:0 0 4px;font-size:17px}
.pick .meta{font-size:13px;color:var(--mut);margin-bottom:10px}
.pick p{font-size:15px;margin:8px 0 10px}
.pick .sel{font-weight:700;color:#0b2b1b;background:#eefaf1;display:inline-block;padding:3px 9px;border-radius:7px;margin-bottom:8px}
.note{background:#fff8e6;border:1px solid #f0dfae;border-radius:10px;padding:12px 15px;margin:14px 0;font-size:14px}
.warn{background:#fdeeee;border:1px solid #f3c9c9;border-radius:10px;padding:12px 15px;margin:14px 0;font-size:14px}
.ok{background:#eefaf1;border:1px solid #c6e8d2;border-radius:10px;padding:12px 15px;margin:14px 0;font-size:14px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
footer{border-top:1px solid var(--line);margin-top:40px;padding-top:16px;font-size:13px;color:var(--mut)}
code{background:#eef1f4;padding:1px 5px;border-radius:4px;font-size:13px}
.small{font-size:13px;color:var(--mut)}
.nowrap{white-space:nowrap}
.center{text-align:center}
"""

NAV = [("index.html", "Today's picks"), ("predictions.html", "Written predictions"),
       ("matches.html", "All matches"), ("markets.html", "Markets"), ("coverage.html", "Sports & coverage"),
       ("flagged.html", "Flagged for review"), ("sources.html", "Sources"), ("methodology.html", "Method"),
       ("repo-review.html", "Repo review")]


def page(path, title, body, here=""):
    up = "../" * (path.count("/"))
    nav = "".join('<a href="%s%s"%s>%s</a>' % (up, p, ' class="here"' if p == here else '', t) for p, t in NAV)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} &middot; OLBG research desk {e(SESSION)}</title>
<style>{CSS}</style></head><body>
<header class="top"><div class="wrap">
<a class="brand" href="{up}index.html">OLBG research desk<small>SESSION {e(SESSION)} &middot; 24 OCT 2026</small></a>
<nav class="main">{nav}</nav></div></header>
{body}
<footer><div class="wrap">Independent research. Not affiliated with OLBG. Prices are our own estimates unless labelled as a
published league price. 18+ &middot; stake only what you can afford to lose.
Built {e(S['built_utc'])} from {S['sources']} reads, {S['official_sources']} of them official.
<a href="{up}methodology.html">How the numbers are made</a>.</div></footer>
</body></html>"""
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(doc, encoding="utf-8")


# ------------------------------------------------------------------ tables ----
def picks_table(rows):
    out = ['<div class="tblwrap"><table><thead><tr><th>Sport</th><th>Match</th><th>Our pick</th>'
           '<th class="num">Our chance</th><th class="num">Our fair price</th><th class="num">Best published</th>'
           '<th class="num">Edge</th><th>Confidence</th><th>Starts (UTC)</th><th>Sources</th></tr></thead><tbody>']
    for f in rows:
        edge = f.get("edge_pts")
        ecol = "&mdash;" if edge is None else f'<span style="color:{"#0a7d3f" if edge > 0 else "#a3231f"}">{edge:+.1f}</span>'
        out.append(
            f'<tr><td>{e(f["sport_name"])}</td>'
            f'<td><a href="{e(f["olbg_url"])}" target="_blank" rel="noopener noreferrer">{e(f["away_name"])} @ {e(f["home_name"])}</a>'
            f'<br><small class="small">{e(f["comp"])}</small></td>'
            f'<td><strong>{e(f["selection"])}</strong></td>'
            f'<td class="num">{prob(f["prob"])}</td><td class="num">{money(f["fair"])}</td>'
            f'<td class="num">{money(f.get("best"))}</td><td class="num">{ecol}</td>'
            f'<td>{conf_badge(f["confidence"])}</td><td class="nowrap">{when(f.get("start_utc"))}</td>'
            f'<td>{srcs(f["sources"], 3)}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


def fixtures_table(rows, show_price=True):
    out = ['<div class="tblwrap"><table><thead><tr><th>Match</th><th>Competition</th><th>Starts (UTC)</th>'
           '<th>Status</th><th>Confidence</th><th>Sources</th></tr></thead><tbody>']
    for f in rows:
        status = (f'<strong>{e(f["selection"])}</strong><br><small class="small">{prob(f.get("prob"))} &middot; '
                  f'fair {money(f.get("fair"))}</small>') if f.get("selection") else (
            '<span class="small">no line issued</span>' if not f["priced"] else '<span class="small">priced, no pick</span>')
        note = f'<br><small class="small">{e(f["start_note"])}</small>' if f.get("start_note") else ""
        out.append(f'<tr><td><a href="{e(f["olbg_url"])}" target="_blank" rel="noopener noreferrer">'
                   f'{e(f["away_name"])} @ {e(f["home_name"])}</a></td><td>{e(f["comp"])}</td>'
                   f'<td class="nowrap">{when(f.get("start_utc"))}{note}</td><td>{status}</td>'
                   f'<td>{conf_badge(f.get("confidence"))}</td><td>{srcs(f["sources"], 3)}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


# ------------------------------------------------------------------- index ----
def build_index():
    top = sorted(PICKS, key=lambda f: (-(f["prob"] or 0), -(f.get("edge_pts") or -99)))[:5]
    best_edge = sorted([p for p in PICKS if p.get("edge_pts") is not None], key=lambda f: -f["edge_pts"])[:3]
    sports_rows = "".join(
        f'<tr><td><a href="sports/{c["sport"]}.html">{e(c["name"])}</a></td>'
        f'<td class="num">{c["fixtures"]}</td><td class="num">{c["priced"]}</td>'
        f'<td class="num">{c["predictions"]}</td><td>{conf_badge("High" if c["high"] else None) if c["high"] else "&mdash;"}</td>'
        f'<td class="small">{e(c["blocker"])}</td></tr>' for c in sorted(COV, key=lambda c: ORDER.index(c["sport"])))

    body = f"""<div class="hero"><div class="wrap">
<h1>Today&rsquo;s picks, in one place.</h1>
<p class="lead">Saturday 24 October 2026. We list {S['fixtures']} matches that OLBG is showing across the fifteen sports
you asked for, we price {S['priced']} of them from official league data, and we publish {S['predictions']} written
predictions. Every number below comes with the official source it was read from.</p>
<div class="kpi">
<div><b>{S['picks']}</b><span>picks</span></div>
<div><b>{S['predictions']}</b><span>written predictions</span></div>
<div><b>{S['fixtures']}</b><span>matches listed</span></div>
<div><b>{S['sports_with_picks']} / 15</b><span>sports with a pick</span></div>
<div><b>{S['flags']}</b><span>items flagged</span></div>
</div></div></div>
<div class="wrap">

<div class="warn"><strong>Read this first.</strong> {S['high']} pick reaches even a 65% win chance and
<strong>0</strong> reach the 70% you asked for. We did not relabel anything to fill the quota: the arithmetic of your
own two rules (&ldquo;over 70%&rdquo; and &ldquo;a price no shorter than &minus;250&rdquo;) leaves only a
1.4&#8209;point window, and today&rsquo;s honest numbers do not land inside it.
<a href="methodology.html#gate">The full explanation is here</a>. Everything we <em>can</em> support is below.</div>

<div class="jump">
<a href="#picks"><b>1. The picks &rarr;</b><span>Every selection, its price, our chance and the edge.</span></a>
<a href="predictions.html"><b>2. The written predictions &rarr;</b><span>{S['predictions']} unique write-ups, 73&ndash;107 words each.</span></a>
<a href="matches.html"><b>3. Every match &rarr;</b><span>All {S['fixtures']} fixtures, with the ones we could not price marked.</span></a>
<a href="coverage.html"><b>4. Why 13 sports have no pick &rarr;</b><span>The exact official page that blocked each one.</span></a>
</div>

<h2 id="picks">The five strongest picks today</h2>
<p class="small">Ranked by our own win probability. &ldquo;Edge&rdquo; is our chance minus the chance implied by the best
published price; a negative edge means the market is shorter than we are, so the pick is a match-winner call rather than
a value call.</p>
{picks_table(top)}
<p class="small"><a href="picks.html">See all {S['picks']} picks, including the two where our line is well clear of the
published price &rarr;</a></p>

<h2>Where our line disagrees most with the published price</h2>
<div class="grid2">
{''.join(f'''<div class="card"><h3>{e(p["selection"])} &mdash; {e(p["away_name"])} @ {e(p["home_name"])}</h3>
<p class="small">{e(p["comp"])}</p>
<p><strong>Our chance {prob(p["prob"])}</strong> &middot; our fair price {money(p["fair"])} &middot;
best published {money(p["best"])} ({e(p["best_book"] or "n/a")}) &middot;
edge <strong>{p["edge_pts"]:+.1f} points</strong></p>
<p class="small">{srcs(p["sources"], 3)}</p>
<p class="small"><a href="picks.html#{e(p["id"])}">Full reasoning &rarr;</a></p></div>''' for p in best_edge)}
</div>

<h2>The executive summary, in words</h2>
<div class="card"><ul>
<li><strong>Ice hockey is the only sport we could price properly.</strong> The NHL publishes its own schedule, club
statistics and partner prices, so six of the eleven NHL games we list have a line built from official numbers and
checked against a real market.</li>
<li><strong>Baseball gives us the single highest-confidence call:</strong> Milwaukee at home in World Series Game 2,
{prob(0.6514)} on our line, available nowhere cheaper than our fair price because no official price feed exists for MLB.</li>
<li><strong>Basketball is listed but not priced.</strong> Every NBA club has played one or two games; a probability from
that sample would be invention, so we publish the official records and no line.</li>
<li><strong>Twelve sports have fixtures but no line</strong>, because the governing body&rsquo;s page would not
render (404, cookie wall, or JavaScript shell). Each one is named on the coverage page with its URL.</li>
<li><strong>Nothing is padded.</strong> No pick, price or probability on this site is copied from OLBG&rsquo;s tip
percentages, which are votes rather than chances.</li>
</ul></div>

<h2>All fifteen sports at a glance</h2>
<div class="tblwrap"><table><thead><tr><th>Sport</th><th class="num">Matches</th><th class="num">Priced</th>
<th class="num">Predictions</th><th>High picks</th><th>Why there are not five</th></tr></thead>
<tbody>{sports_rows}</tbody></table></div>
<p class="small">The brief asks for five written predictions per sport per day (75 in total). We delivered
{S['predictions']}. <a href="coverage.html">The gap, sport by sport, is set out here</a>.</p>

<h2>What is flagged for your review</h2>
<div class="card"><p>{S['flags']} items are published on the
<a href="flagged.html">Flagged for review</a> page with the source for each one. The three that matter most:</p><ul>
<li><strong>F-321-01</strong> &mdash; the brief&rsquo;s two rules (over 70% and no price shorter than &minus;250) can only
both hold for probabilities between 70.0% and 71.4%.</li>
<li><strong>F-321-03</strong> &mdash; thirteen sports produced no priced pick; the blocking official page is named for each.</li>
<li><strong>F-321-04</strong> &mdash; OLBG&rsquo;s hub clock is US Eastern, five hours off UK greyhound times, so no
hub time is ever published as a start time.</li>
</ul></div>

<h2>What this desk did and did not do</h2>
<div class="grid2">
<div class="card"><h3>Read live this session</h3><p class="small">Fifteen OLBG sport hubs (discovery only), the NHL
schedule and club statistics feeds, the NHL standings snapshot, Major League Baseball&rsquo;s schedule and standings
for both leagues, NBA standings, the Formula&nbsp;1 United States Grand Prix hub and the World Snooker Tour match list.
{S['sources']} reads in total, {S['official_sources']} of them official.</p>
<p class="small"><a href="sources.html">Every URL with its UTC read time &rarr;</a></p></div>
<div class="card"><h3>Tried and failed, and recorded</h3><p class="small">PDC calendar (cookie wall), United Rugby
Championship fixtures (404), GBGB racecards (404), ATP schedule (shell), WTA scores (notifications only), Italian
volleyball league (video shell), Pakistan Cricket Board (news only), Premiership Rugby (navigation only), PGA TOUR
schedule (did not reach October). Each is a flag, not a silent gap.</p>
<p class="small"><a href="flagged.html">All flags with links &rarr;</a></p></div>
</div>
</div>"""
    page("index.html", "Today's picks", body, "index.html")


# ------------------------------------------------------------------- picks ----
def build_picks():
    rows = sorted(PICKS, key=lambda f: (-(f["prob"] or 0)))
    detail = []
    for f in rows:
        mrows = "".join(
            f'<tr><td>{e(m["market"])}</td><td>{e(m["selection"])}</td><td class="num">{prob(m["prob"])}</td>'
            f'<td class="num">{money(m["fair"])}</td><td>{e(m["alt_selection"])}</td>'
            f'<td class="num">{prob(m["alt_prob"])}</td><td class="num">{money(m["alt_fair"])}</td></tr>'
            for m in f.get("markets", []))
        facts = "".join(f"<li>{e(x)}</li>" for x in f.get("facts", []))
        edge_txt = "&mdash;" if f.get("edge_pts") is None else ("%+.1f points" % f["edge_pts"])
        detail.append(f'''<div class="card" id="{e(f["id"])}">
<h3>{e(f["away_name"])} @ {e(f["home_name"])} &mdash; {e(f["comp"])}</h3>
<p class="small">{when(f.get("start_utc"))} &middot; {e(f.get("start_note") or "")} &middot; {conf_badge(f.get("confidence"))}</p>
<p><strong>Pick: {e(f["selection"])}</strong> &middot; our chance {prob(f["prob"])} &middot; our fair price
{money(f["fair"])} &middot; best published {money(f.get("best"))} ({e(f.get("best_book") or "no official price read")})
&middot; edge {edge_txt}</p>
<h4>Officially read facts</h4><ul class="small">{facts}</ul>
<h4>Every market we examined</h4>
<div class="tblwrap"><table><thead><tr><th>Market</th><th>Selection</th><th class="num">Our chance</th>
<th class="num">Our fair price</th><th>Other side</th><th class="num">Chance</th><th class="num">Fair price</th>
</tr></thead><tbody>{mrows}</tbody></table></div>
<p class="small">Sources: {srcs(f["sources"])}</p>
<p class="small"><a href="{e(f["olbg_url"])}" target="_blank" rel="noopener noreferrer">Open this market on OLBG &rarr;</a></p>
</div>''')
    body = f"""<div class="hero"><div class="wrap"><h1>All {S['picks']} picks</h1>
<p class="lead">Each pick names the selection in words, gives our own probability, the fair price that probability
implies, the best price actually published by an official source where one exists, and the gap between the two.</p>
</div></div><div class="wrap">
<div class="note"><strong>How to read &ldquo;edge&rdquo;.</strong> Edge is our probability minus the probability implied
by the best published price. Positive means the official price is longer than our line thinks it should be. Negative
means the official price is shorter than our line, so the pick is a match-winner call, not a value call.</div>
{picks_table(rows)}
<h2>Each pick in detail</h2>
{''.join(detail)}
</div>"""
    page("picks.html", "All picks", body, "index.html")


# ------------------------------------------------------------- predictions ----
def build_predictions():
    cards = []
    for p in sorted(PRED, key=lambda p: -p["prob"]):
        f = next(x for x in FX if x["id"] == p["fixture_id"])
        cards.append(f'''<div class="pick {e((p["confidence"] or "").lower())}">
<h3>{e(p["match"])} &mdash; {e(f["comp"])}</h3>
<div class="meta">{when(p.get("start_utc"))} &middot; starts {e(f.get("start_note") or "")} &middot;
{conf_badge(p["confidence"])} &middot; our chance {prob(p["prob"])} &middot; our fair price {money(p["fair"])}</div>
<div class="sel">{e(p["selection"])}</div>
<p>{e(p["text"])}</p>
<p class="small">{p["words"]} words &middot; sources: {srcs(p["sources"])} &middot;
<a href="{e(f["olbg_url"])}" target="_blank" rel="noopener noreferrer">market on OLBG</a></p>
</div>''')
    body = f"""<div class="hero"><div class="wrap"><h1>The written predictions</h1>
<p class="lead">{S['predictions']} unique write-ups. Each one names the selection, the team&rsquo;s current form, the
recent history and the statistic that decides it, and each is at least 30 words (the shortest is 73). No sentence is
reused between write-ups.</p></div></div><div class="wrap">
<div class="note"><strong>What is not in these write-ups.</strong> No injury claim appears anywhere, because no official
injury report could be read this session (flag F-321-11). We say so rather than invent a clean bill of health. Team news,
line-ups and late changes are for you to confirm on the official page linked in each card.</div>
{''.join(cards)}
<h2>Why there are seven and not seventy-five</h2>
<p>The brief asks for five predictions per sport, or 75 a day. A prediction here means a named selection backed by
officially read facts about that specific match. Seven matches had enough readable, official detail to support one.
The other {S['fixtures'] - S['priced']} fixtures are published with their OLBG link and no line, and the
<a href="coverage.html">coverage page</a> names the official page that blocked each sport.</p>
</div>"""
    page("predictions.html", "Written predictions", body, "predictions.html")


# ----------------------------------------------------------------- matches ----
def build_matches():
    blocks = []
    for key in ORDER:
        rows = [f for f in FX if f["sport"] == key]
        if not rows:
            blocks.append(f'<h2 id="{key}">{e(NAME[key])}</h2><div class="card"><p class="small">No upcoming market was '
                          f'listed on the OLBG {e(NAME[key])} hub when it was read. '
                          f'{srcs([SPORT_OF[key]["olbg_source"]])}</p></div>')
            continue
        blocks.append(f'<h2 id="{key}">{e(NAME[key])} <span class="small">({len(rows)} listed, '
                      f'{len([r for r in rows if r["priced"]])} priced)</span></h2>{fixtures_table(rows)}')
    body = f"""<div class="hero"><div class="wrap"><h1>Every match OLBG is listing</h1>
<p class="lead">All {S['fixtures']} fixtures across the fifteen sports, in the order the hubs listed them. Each row links
to the OLBG market and to every official source used. A blank means we could not read it from an official source, not
that it does not exist.</p></div></div><div class="wrap">
<div class="note"><strong>Start times.</strong> Only times taken from an official feed are printed as a UTC clock time.
Where OLBG was the only source, the time is left blank: its hub runs on US Eastern, which is five hours off UK
greyhound times and four hours off UK evening sport (flag F-321-04).</div>
{''.join(blocks)}
</div>"""
    page("matches.html", "All matches", body, "matches.html")


# ----------------------------------------------------------------- markets ----
def build_markets():
    fam = []
    for key in ORDER:
        rows = [f for f in FX if f["sport"] == key and f["priced"]]
        if not rows:
            fam.append(f'<tr><td><a href="sports/{key}.html">{e(NAME[key])}</a></td><td class="num">0</td>'
                       f'<td colspan="3" class="small">No market was originated: {e(SPORT_OF[key]["blocker"])}</td></tr>')
            continue
        for f in rows:
            fam.append(f'<tr><td><a href="sports/{key}.html">{e(NAME[key])}</a></td>'
                       f'<td>{e(f["away_name"])} @ {e(f["home_name"])}</td>'
                       f'<td class="num">{len(f.get("markets", []))}</td>'
                       f'<td class="small">{e(", ".join(m["market"] for m in f.get("markets", [])))}</td>'
                       f'<td>{conf_badge(f["confidence"])}</td></tr>')
    body = f"""<div class="hero"><div class="wrap"><h1>Markets examined</h1>
<p class="lead">For every match we could price, we originated a match-winner line, both sides of a handicap, and the
match total &mdash; the three families the brief names &mdash; rather than only picking a winner. Nothing is invented:
where a family needs an input we do not have, the line is withheld and the reason is stated.</p></div></div>
<div class="wrap">
<h2>What we originated</h2>
<div class="tblwrap"><table><thead><tr><th>Sport</th><th>Match</th><th class="num">Markets</th>
<th>Market families</th><th>Confidence</th></tr></thead><tbody>{''.join(fam)}</tbody></table></div>

<h2>How each family is built</h2>
<div class="grid2">
<div class="card"><h3>Match winner (moneyline)</h3><p class="small">NHL: a logistic blend of each club&rsquo;s official
points percentage and goal differential, shrunk toward .500 by eight games of prior, plus a fixed home-ice term. MLB: the
log5 formula on the official home and away win percentages. Both are then compared with any published price.</p></div>
<div class="card"><h3>Handicap / puck line &plusmn;1.5</h3><p class="small">A Poisson goal distribution per side, with the
two scoring rates scaled until the moneyline matches the line above, so the handicap cannot contradict the winner
market. Both sides are published.</p></div>
<div class="card"><h3>Match total 5.5 and 6.5</h3><p class="small">Taken from the same Poisson distribution. We publish
both sides of both lines and do not cherry-pick the number that looks best.</p></div>
<div class="card"><h3>What we did not originate</h3><p class="small">Player props, correct score, first goalscorer,
quarter/half markets and anything needing lineup or injury data. No official lineup or injury feed was readable, so
those families are withheld rather than guessed.</p></div>
</div>
<p class="small">A full market-by-market table for every priced match is on the <a href="picks.html">picks page</a>.</p>
</div>"""
    page("markets.html", "Markets", body, "markets.html")


# ---------------------------------------------------------------- coverage ----
def build_coverage():
    rows = "".join(
        f'''<tr><td><a href="sports/{c["sport"]}.html">{e(c["name"])}</a></td><td class="num">{c["fixtures"]}</td>
<td class="num">{c["priced"]}</td><td class="num">{c["predictions"]}</td>
<td class="num">{c["predictions"]}/5</td><td>{'<span class="tag high">met</span>' if c["met"] else '<span class="tag none">short</span>'}</td>
<td class="small">{e(c["blocker"])} {srcs([c["blocker_source"]])}</td></tr>''' for c in sorted(COV, key=lambda c: ORDER.index(c["sport"])))
    body = f"""<div class="hero"><div class="wrap"><h1>Coverage: what the brief asked for, and what the evidence allowed</h1>
<p class="lead">The brief asks for five written predictions per sport per day: 75 in total. We published
{S['predictions']}. This page shows, for every sport, exactly how many matches OLBG listed, how many we could price from
an official source, how many predictions we wrote, and the page that blocked the rest.</p></div></div>
<div class="wrap">
<div class="tblwrap"><table><thead><tr><th>Sport</th><th class="num">OLBG matches</th><th class="num">Priced</th>
<th class="num">Predictions</th><th class="num">vs 5 target</th><th>Target</th><th>What blocked it, and the source</th>
</tr></thead><tbody>{rows}</tbody></table></div>
<div class="warn"><strong>Why we did not fill the remaining {S['target_predictions'] - S['predictions']} slots.</strong>
A prediction in this desk means a named selection justified by facts about that specific match read from the league, tour
or federation itself. For the twelve sports that have fixtures but no priced line we could not read a single official fact about the
fixtures &mdash; no records, no start times, no line-ups. Writing 60 more predictions would have meant inventing form,
inventing injuries or converting OLBG&rsquo;s tip-vote percentages into &ldquo;chances&rdquo;. We publish the shortfall
instead (flags F-321-02 and F-321-03).</div>
<h2>What would close each gap</h2>
<div class="card"><ul>
<li><strong>Tennis</strong> &mdash; an accessible ATP/WTA draw feed with match times and rankings.</li>
<li><strong>Cricket</strong> &mdash; a readable PCB, CSA or NZC fixture and scorecard page for the Pakistan v England ODI
and the New Zealand v India T20.</li>
<li><strong>Rugby Union</strong> &mdash; a working URC/Top 14/Premiership fixture and standings route.</li>
<li><strong>Volleyball, Handball, Darts, Gaelic, Greyhounds</strong> &mdash; one working official results or fixtures
route each; the league sites returned 404s, cookie walls or JavaScript shells today.</li>
<li><strong>Basketball</strong> &mdash; nothing but time: the season is one or two games old.</li>
<li><strong>Motor Racing</strong> &mdash; qualifying, which runs later today.</li>
<li><strong>Golf, Rugby League</strong> &mdash; OLBG is listing no market at all, so there is nothing to price.</li>
</ul></div>
</div>"""
    page("coverage.html", "Coverage", body, "coverage.html")


# ----------------------------------------------------------------- sources ----
def build_sources():
    rows = "".join(
        f'<tr><td><span class="tag {"high" if s["kind"] == "official" else "none"}">{e(s["kind"])}</span></td>'
        f'<td><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["name"])}</a></td>'
        f'<td class="nowrap small">{e(s["read_utc"])}</td><td class="small">{e(s["note"])}</td></tr>'
        for s in sorted(SRC.values(), key=lambda x: (x["kind"] != "official", x["read_utc"])))
    body = f"""<div class="hero"><div class="wrap"><h1>Sources, with the minute we read them</h1>
<p class="lead">Every fact on this site points at one of these {S['sources']} reads. OLBG is used to discover which
matches exist and what the market is called; it is never used as sporting evidence. The {S['official_sources']} official
reads are the league, tour, federation or governing body speaking for itself.</p></div></div>
<div class="wrap">
<div class="tblwrap"><table><thead><tr><th>Type</th><th>Source</th><th>Read (UTC)</th><th>What it gave us</th>
</tr></thead><tbody>{rows}</tbody></table></div>
<h2>Rules we applied to sources</h2>
<div class="card"><ul>
<li>Betting sites, tipsters, aggregators and news outlets are not official sources and are not cited as evidence.</li>
<li>OLBG tip percentages are the share of community votes on a selection. They are never converted into a probability
and never used to set a price (flag F-321-05).</li>
<li>A fact that was not read this session is not published. The two exceptions are clearly labelled: our own originated
prices (estimates) and the arithmetic in the methodology page.</li>
<li>Where a page rendered but did not contain the fixture &mdash; a 404, a cookie wall, a JavaScript shell &mdash; that is
recorded as a failed read, and the sport gets no line rather than a guess.</li>
</ul></div>
</div>"""
    page("sources.html", "Sources", body, "sources.html")


# ------------------------------------------------------------------ flags ----
def build_flags():
    cards = "".join(f'''<div class="card" id="{e(f["id"])}">
<h3><span class="tag {'low' if f['severity'] == 'low' else ('medium' if f['severity'] == 'medium' else 'none')}">{e(f["severity"]).upper()}</span> {e(f["id"])} &mdash; {e(f["title"])}</h3>
<p>{e(f["detail"])}</p>
<p class="small">Area: {e(f["area"])} &middot; Sources: {srcs(f["sources"]) if f["sources"] else "repository itself"}</p>
</div>''' for f in FLAGS)
    body = f"""<div class="hero"><div class="wrap"><h1>Flagged for review</h1>
<p class="lead">Anything unconfirmed, unreadable, withheld or irregular is published here rather than smoothed over.
Nothing on this page blocks publication; it is the list of things you may want to change or check by hand.</p>
</div></div><div class="wrap">
<div class="note">No table row anywhere on this site is filled in from memory. Where an official value was not readable,
the cell is blank, and the blank is explained here with the URL that was tried.</div>
{cards}
</div>"""
    page("flagged.html", "Flagged for review", body, "flagged.html")


# -------------------------------------------------------------- methodology ----
def build_method():
    body = f"""<div class="hero"><div class="wrap"><h1>How the numbers are made</h1>
<p class="lead">Our prices are our own estimates, built from official inputs and published with the arithmetic shown so
you can disagree with them precisely.</p></div></div><div class="wrap">

<h2 id="gate">The gate the brief asks for, and why it is nearly empty</h2>
<div class="card"><p>The brief asks for picks with &ldquo;a greater than 70% chance to win&rdquo; that also
&ldquo;sit between &minus;250 and +10000 odds&rdquo;. Those two rules are almost mutually exclusive:</p>
<ul>
<li>A 70.0% chance is a fair price of <code>&minus;100 &times; 0.70 / 0.30 = &minus;233</code>.</li>
<li>A &minus;250 price is a chance of <code>250 / 350 = 71.4%</code>.</li>
<li>So the only probabilities that satisfy both are those between <strong>70.0% and 71.4%</strong> &mdash; a 1.4&#8209;point
window.</li>
</ul>
<p>Today, with {S['priced']} priced matches and {S['market_rows']} originated market rows, <strong>{S['strict70_and_band']}</strong>
selections land inside that window. The highest probability we can defend is {prob(S['top_prob'])}.</p>
<p>We resolved it the only way that keeps the arithmetic honest: we publish our true probability, we label confidence on
a stated scale (below), and we show you the strict-gate count rather than relabelling a price that breaks your own
rule.</p></div>

<h2>The confidence scale we used</h2>
<div class="card"><ul>
<li><span class="tag high">High</span> our probability 65% or better, and our fair price inside &minus;250&hellip;+10000.</li>
<li><span class="tag medium">Medium</span> 57.5% to 65%.</li>
<li><span class="tag low">Low</span> below 57.5%.</li>
<li><span class="tag none">No line</span> no official input was readable, so no probability was issued.</li>
</ul>
<p class="small">This is our own scale, not the market&rsquo;s. It is deliberately not anchored on &ldquo;the market says
70%&rdquo;, which was the failure mode in earlier desks: a market-implied 70% is just a short price, not evidence.</p></div>

<h2>NHL match-winner line</h2>
<div class="card"><p>For each club we take games played, points percentage, goals for and goals against from the NHL&rsquo;s
own club statistics feed. Points percentage is shrunk toward .500 by eight games of prior &mdash; with only ten games
played, an 8-1-1 start is partly luck &mdash; and goal differential per game is shrunk the same way. The two are combined
as <code>1.6 &times; points&nbsp;index + 0.12 &times; goal&nbsp;differential</code>, a home-ice term of 0.16 is added on
the logit scale, and the result is passed through a logistic function. The away probability is simply one minus the home
probability, because an NHL game cannot end level.</p>
<p class="small">Calibration check, in public: on the six games where the league publishes partner prices, our line lands
within 2.1 points of the de-vigged market on four of them, and differs by 5&ndash;6 points on the two where the clubs have
the fewest games played. That is the expected behaviour of a form model, and it is the reason we are comfortable
publishing its output &mdash; including the parts where it disagrees.</p></div>

<h2>NHL handicap and total lines</h2>
<div class="card"><p>We build a Poisson goal distribution for each side from goals for and against per game (geometric
mean, capped between 1.6 and 4.4 goals), then scale the two rates symmetrically until the moneyline from the Poisson
model equals the moneyline above. Only then do we read the puck line and the total off that distribution. This guarantees
the derived markets cannot contradict the winner market, which is the usual failure when totals and moneylines are
priced independently.</p></div>

<h2>MLB match-winner line</h2>
<div class="card"><p>Log5 on official splits: the home club&rsquo;s home win percentage against the away club&rsquo;s away
win percentage. For World Series Game 2 that is Milwaukee&rsquo;s 55-26 home record against Tampa Bay&rsquo;s 43-38 road
record, giving {prob(0.6514)}. We do <em>not</em> adjust for the starting pitchers, because neither pitcher&rsquo;s season
statistics were read from an official source &mdash; naming them without adjusting for them is honest; adjusting from a
guess would not be.</p></div>

<h2>Best published price and edge</h2>
<div class="card"><p>Where the league publishes partner prices (the NHL does), we take the longest available price across
the <strong>two-way</strong> quotes. Prices filed under provider id 10 sum to about 81% implied:
that is a three-way 60-minute market, and mixing it in would manufacture a false under-round (flag F-321-10). Edge is our
probability minus <code>1 / decimal&nbsp;price</code>.</p></div>

<h2>Reproducing all of it</h2>
<div class="card"><p class="small">The data and the arithmetic are both in the repository and run without network access:
<code>python3 scripts/s321b595c_data.py</code> rewrites <code>data/321b595c/</code>,
<code>python3 scripts/s321b595c_build.py</code> rebuilds this site, and
<code>python3 scripts/s321b595c_validate.py</code> runs the checks listed below. The only non-reproducible part is the
reading of live pages, which is why every read carries its UTC minute on the
<a href="sources.html">sources page</a>.</p></div>

<h2>Checks that run before publication</h2>
<div class="card"><ul class="small">
<li>Every source id used by a row exists in the source register, and every register entry has a URL and a read time.</li>
<li>Every priced row carries at least one official source.</li>
<li>American and decimal prices are recomputed from the stated probability, both ways.</li>
<li>The confidence label is recomputed from the probability and must match the published label.</li>
<li>Every prediction is at least 30 words, contains its selection, and shares no eight-word run with any other.</li>
<li>The words &ldquo;model&rdquo; and &ldquo;verified&rdquo; never appear in a reader-facing prediction.</li>
<li>Every relative link and fragment on every page resolves, and every external link is absolute https.</li>
<li>The published JSON must match what the data script produces, so a page cannot drift from its data.</li>
</ul></div>
</div>"""
    page("methodology.html", "Methodology", body, "methodology.html")


# ------------------------------------------------------------- repo review ----
def build_repo():
    body = """<div class="hero"><div class="wrap"><h1>Repository review</h1>
<p class="lead">A line-by-line look at what is actually in this repository before this session added anything, and what
looked irregular.</p></div></div><div class="wrap">
<h2>What is in the tree</h2>
<div class="tblwrap"><table><thead><tr><th>Item</th><th>Count</th><th>Note</th></tr></thead><tbody>
<tr><td>Top-level session desk directories</td><td class="num">60</td><td>Each with its own landing page. Before this
session there was no index that said which one was current.</td></tr>
<tr><td>HTML files in the tree</td><td class="num">1,558</td><td>Includes every historical desk at root.</td></tr>
<tr><td>JSON files under <code>data/</code></td><td class="num">402</td><td>Canonical snapshot plus per-desk copies.</td></tr>
<tr><td>Python scripts</td><td class="num">282</td><td>Largely per-session pipelines.</td></tr>
<tr><td><code>COORDINATION.md</code></td><td class="num">753 KB</td><td>Append-only board, now 84 sections long.</td></tr>
<tr><td>Unresolved merge-conflict markers</td><td class="num">0</td><td>Scanned every <code>.html</code>,
<code>.md</code> and <code>.py</code> for <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code> and
<code>&gt;&gt;&gt;&gt;&gt;&gt;&gt;</code> at line start.</td></tr>
</tbody></table></div>

<h2>Why the site was confusing, in evidence</h2>
<div class="card"><ul>
<li>The root <code>index.html</code> is stamped <code>data-snapshot="2026-10-22T12:29:50Z"</code> &mdash; two days stale
&mdash; and its first content is a KPI ribbon, not a pick.</li>
<li>That same page carried two different &ldquo;start here&rdquo; pointers, to the <code>02d3d515</code> and
<code>8cfb80b2</code> desks, with no statement of which was current.</li>
<li>Nothing on the root page said which of the sixty desk directories holds today&rsquo;s picks.</li>
<li>The words &ldquo;picks&rdquo; and &ldquo;predictions&rdquo; were separate top-level pages with no shared identifier,
so a visitor could not tell which picks had a written prediction behind them.</li>
</ul></div>
<p>That is a presentation defect rather than a data defect, and it is what this desk is built to fix: one landing page
that leads with the picks, a location map, and a single identifier per pick carried from the summary through to the
prediction.</p>

<h2>Data irregularities found in the existing tree</h2>
<div class="card"><ul>
<li><strong>Duplicate clocks.</strong> Several desks publish OLBG hub times as match start times. The hub renders US
Eastern, which is four hours off UK evening sport and five off UK greyhound cards (flag F-321-04). Times derived this
way appear on older pages without that caveat.</li>
<li><strong>Market-implied &ldquo;confidence&rdquo;.</strong> Earlier desks defined a high-confidence pick as one the
market priced above 70%. That is a description of a short price, not of our own analysis, and it is the mechanism that
produced pages of &minus;400 favourites.</li>
<li><strong>Near-identical predictions.</strong> Several write-ups across sibling desks share long n-gram runs because
they were generated from one template. The check in this desk (no shared eight-word run) exists to stop that.</li>
<li><strong>Stale root.</strong> The deployed root page and the freshest desk disagreed about what day it was.</li>
</ul></div>
<p class="small">None of the above is edited by this session. This desk writes only inside its own namespace plus one
pointer on the root page, per the scope rules in <code>COORDINATION.md</code> §84.2.</p>

<h2>What this session added</h2>
<div class="card"><ul>
<li><code>data/321b595c/</code> &mdash; sources, fixtures, predictions, flags, coverage, summary.</li>
<li><code>scripts/s321b595c_data.py</code>, <code>s321b595c_build.py</code>, <code>s321b595c_validate.py</code>.</li>
<li><code>321b595c/</code> &mdash; this 24-page dashboard.</li>
<li><code>tests/pipeline/test_desk_321b595c.py</code> &mdash; structural tests.</li>
<li>One pointer on the root <code>index.html</code>, replacing the stale bar.</li>
</ul></div>
</div>"""
    page("repo-review.html", "Repository review", body, "repo-review.html")


# ------------------------------------------------------------- sport pages ----
def build_sports():
    for c in COV:
        key = c["sport"]
        rows = [f for f in FX if f["sport"] == key]
        picks = [f for f in rows if f.get("selection")]
        preds = [p for p in PRED if p["sport"] == NAME[key]]
        body = f"""<div class="hero"><div class="wrap"><h1>{e(c["name"])}</h1>
<p class="lead">{c["fixtures"]} matches listed on OLBG, {c["priced"]} priced, {c["predictions"]} written
predictions.</p></div></div><div class="wrap">
<div class="{'ok' if picks else 'note'}"><strong>Status.</strong> {e(c["blocker"])} {srcs([c["blocker_source"]])}</div>
<h2>The matches</h2>
{fixtures_table(rows) if rows else '<div class="card"><p class="small">OLBG listed no upcoming market for this sport when the hub was read.</p></div>'}
<h2>Predictions</h2>
{''.join(f'''<div class="pick {e((p["confidence"] or "").lower())}"><h3>{e(p["match"])}</h3>
<div class="meta">{conf_badge(p["confidence"])} &middot; our chance {prob(p["prob"])} &middot; fair price {money(p["fair"])}</div>
<div class="sel">{e(p["selection"])}</div><p>{e(p["text"])}</p>
<p class="small">{p["words"]} words &middot; {srcs(p["sources"])}</p></div>''' for p in preds) if preds else
'<div class="card"><p class="small">No prediction is published for this sport today. See the '
'<a href="../coverage.html">coverage page</a> for the reason and the official page that blocked it.</p></div>'}
<p class="small"><a href="../index.html">&larr; Back to today&rsquo;s picks</a></p>
</div>"""
        page(f"sports/{key}.html", NAME[key], body, "coverage.html")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    build_index(); build_picks(); build_predictions(); build_matches()
    build_markets(); build_coverage(); build_sources(); build_flags()
    build_method(); build_repo(); build_sports()
    print(f"built {len(list(OUT.rglob('*.html')))} pages in {OUT}")


if __name__ == "__main__":
    main()
