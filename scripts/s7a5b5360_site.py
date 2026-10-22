"""Session 7a5b5360-olbg1 — static dashboard builder for the /7a5b5360/ desk.

Plain HTML + one stylesheet, relative links only, so the tree works directly on GitHub Pages.
"""
import html
import os

SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "7a5b5360")

SPORT_SLUG = {
    "Baseball": "baseball", "Ice Hockey": "ice-hockey", "Rugby Union": "rugby-union",
    "Snooker": "snooker", "Motor Racing": "motor-racing",
}

CSS = """
:root{--bg:#0f1216;--panel:#161b22;--panel2:#1c232c;--line:#2a333f;--txt:#e6edf3;--dim:#9aa7b4;
--high:#3fb950;--med:#d29922;--low:#8b949e;--accent:#58a6ff;--warn:#f85149}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header.top{position:sticky;top:0;z-index:20;background:rgba(15,18,22,.96);border-bottom:1px solid var(--line);backdrop-filter:blur(6px)}
.wrap{max-width:1280px;margin:0 auto;padding:0 20px}
.top .wrap{display:flex;align-items:center;gap:18px;height:58px;flex-wrap:wrap}
.brand{font-weight:700;letter-spacing:.02em;white-space:nowrap}
.brand span{color:var(--accent)}
nav.main{display:flex;gap:14px;flex-wrap:wrap;font-size:13.5px}
nav.main a{color:var(--dim)}nav.main a.on{color:var(--txt);font-weight:600}
main{padding:26px 0 60px}
h1{font-size:26px;margin:0 0 6px}h2{font-size:19px;margin:34px 0 10px;padding-bottom:8px;border-bottom:1px solid var(--line)}
h3{font-size:15.5px;margin:22px 0 8px}
p.lede{color:var(--dim);max-width:900px;margin:0 0 18px}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));margin:18px 0 6px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card .k{font-size:11.5px;text-transform:uppercase;letter-spacing:.08em;color:var(--dim)}
.card .v{font-size:25px;font-weight:700;margin-top:4px}
.card .s{font-size:12.5px;color:var(--dim);margin-top:2px}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:13.5px;margin:10px 0 6px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--panel2);font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--dim);position:sticky;top:58px}
tbody tr:hover{background:#1a212a}
tbody tr:last-child td{border-bottom:none}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.high{background:rgba(63,185,80,.15);color:var(--high);border:1px solid rgba(63,185,80,.35)}
.medium{background:rgba(210,153,34,.15);color:var(--med);border:1px solid rgba(210,153,34,.35)}
.low{background:rgba(139,148,158,.15);color:var(--low);border:1px solid rgba(139,148,158,.35)}
.ok{color:var(--high)}.no{color:var(--warn)}.dim{color:var(--dim)}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px}
.pill{display:inline-block;padding:1px 7px;border-radius:6px;background:var(--panel2);border:1px solid var(--line);font-size:11.5px;color:var(--dim);margin:1px 3px 1px 0}
.prose{max-width:900px}.prose p{margin:8px 0}
.note{background:var(--panel);border-left:3px solid var(--med);padding:10px 14px;border-radius:0 8px 8px 0;margin:14px 0;color:var(--dim);font-size:13.5px}
.warnbox{border-left-color:var(--warn)}
footer{border-top:1px solid var(--line);padding:18px 0 40px;color:var(--dim);font-size:12.5px}
ul.tight{margin:6px 0 6px 18px;padding:0}ul.tight li{margin:3px 0}
@media(max-width:720px){th{position:static}.top .wrap{height:auto;padding:10px 16px}}
"""

NAV = [("index.html", "Overview"), ("picks.html", "Picks"), ("markets.html", "Markets"),
       ("predictions.html", "Predictions"), ("coverage.html", "Coverage"),
       ("verification.html", "Verification"), ("flagged.html", "Flagged for Review"),
       ("sources.html", "Sources"), ("methodology.html", "Methodology")]


def e(s):
    return html.escape(str(s), quote=True)


def dec_fmt(d):
    return "" if d is None else f"{d:.2f}"


def page(name, title, body, here):
    up = "../" if "/" in name else ""
    nav = "".join(
        f'<a class="{"on" if href == here else ""}" href="{up}{href}">{e(label)}</a>'
        for href, label in NAV + ([("../index.html", "Repository dashboard")]))
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} — OLBG desk 7a5b5360</title>
<link rel="stylesheet" href="{up}assets/style.css">
</head><body>
<header class="top"><div class="wrap">
<div class="brand">OLBG<span>/</span> desk 7a5b5360</div>
<nav class="main">{nav}</nav>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
Snapshot 22–26 October 2026 · harvested 2026-10-22T01:30Z · session <span class="mono">7a5b5360-olbg1</span> (task T41).
Prices on this site are originated by a model, not quoted from any bookmaker. Facts carry a link to the official page they were read from.
</div></footer>
</body></html>
"""
    path = os.path.join(SITE, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(doc)


def src_links(keys, SOURCES):
    out = []
    for k in keys:
        s = SOURCES[k]
        label = {"read": "", "read_no_fixture": " (no fixture)", "blocked_consent_wall": " (blocked)",
                 "http_404": " (404)", "http_500": " (500)", "client_rendered_empty": " (no content)"}.get(s["status"], "")
        out.append(f'<a href="{e(s["url"])}" title="{e(s["name"])}">{e(s["org"].split(" (")[0])}{label}</a>')
    return " · ".join(out)


def badge(tier):
    return f'<span class="badge {tier}">{tier}</span>'


def build_site(bundle, fixtures, markets, picks, preds, high_prob, SOURCES, COVERAGE, FLAGS,
               METHOD_TEXT, REPO_REVIEW, ASSUMPTIONS, FIELD, F1_EVENT, EXCLUDED, IN_SCOPE):
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "sports"), exist_ok=True)
    with open(os.path.join(SITE, "assets", "style.css"), "w") as fh:
        fh.write(CSS)

    c = bundle["counts"]
    by_id = {f["id"]: f for f in fixtures}
    boards = {m["id"]: m["markets"] for m in markets}
    tiers = {t: sum(1 for p in picks if p["confidence"] == t) for t in ("high", "medium", "low")}
    in_band_high = sum(1 for h in high_prob if h["in_brief_band"])

    # ------------------------------------------------------------------ index
    cards = [
        ("Fixtures verified", c["fixtures"], "5 sports · 22–26 Oct 2026"),
        ("Markets originated", c["markets"], "winner · handicap · total · outright"),
        ("High-confidence picks", tiers["high"], f'{tiers["medium"]} medium · {tiers["low"]} low'),
        ("Written predictions", c["predictions"], "≥30 words, unique"),
        ("70%+ selections", c["high_probability_selections"], f"{in_band_high} inside the -250 band"),
        ("Flagged items", len(FLAGS), "published, do not block"),
    ]
    card_html = "".join(
        f'<div class="card"><div class="k">{e(k)}</div><div class="v">{v}</div><div class="s">{e(s)}</div></div>'
        for k, v, s in cards)

    order = {"high": 0, "medium": 1, "low": 2}
    top = sorted(picks, key=lambda p: (order[p["confidence"]], -p["prob"]))[:8]
    rows = "".join(
        f'<tr><td>{e(p["sport"])}</td><td>{e(p["competition"])}</td>'
        f'<td>{e(p["home"])} v {e(p["away"])}</td><td>{e(p["selection"])}</td>'
        f'<td class="num">{p["prob"]*100:.1f}%</td><td class="num">{dec_fmt(p["fair_decimal"])}</td>'
        f'<td>{badge(p["confidence"])}</td><td>{src_links(p["sources"], SOURCES)}</td></tr>'
        for p in top)

    cov_rows = "".join(
        f'<tr><td>{e(sport)}</td><td class="num">{COVERAGE[sport]["fixtures"]}</td>'
        f'<td>{e(COVERAGE[sport]["state"].replace("_", " "))}</td>'
        f'<td>{e(COVERAGE[sport]["note"])}</td>'
        f'<td>{src_links(COVERAGE[sport]["source"], SOURCES) if COVERAGE[sport]["source"] else "—"}</td></tr>'
        for sport in IN_SCOPE)

    body = f"""
<h1>Fresh matchday desk — 22 to 26 October 2026</h1>
<p class="lede">Every fixture below was read from an official governing-body page during this session, priced with
our own model across winner, handicap, total and outright markets, and given a written prediction where the
model's probability clears 70%. Where an official page did not publish a value it is blank and listed on
<a href="flagged.html">Flagged for Review</a>.</p>
<div class="grid">{card_html}</div>

<div class="note warnbox"><strong>Read this first.</strong> The brief asks for picks that are both 70%+ and priced
between -250 and +10000. Once any margin is applied those two rules cannot both hold: a 70% chance is a 1.43
fair price, which is shorter than -250. This desk publishes the probability, the fair price and an in-band flag
for every selection instead of silently dropping a rule. See <a href="flagged.html">F-7A-01</a>.</div>

<h2>Strongest picks on the board</h2>
<table><thead><tr><th>Sport</th><th>Competition</th><th>Match</th><th>Selection</th><th>Model</th>
<th>Fair price</th><th>Tier</th><th>Official source</th></tr></thead><tbody>{rows}</tbody></table>
<p class="dim">Full board: <a href="picks.html">all {c["fixtures"]} picks</a> ·
<a href="markets.html">every originated market</a> ·
<a href="predictions.html">{c["predictions"]} written predictions</a></p>

<h2>Coverage across the seventeen in-scope sports</h2>
<p class="lede">Excluded by the brief: {e(", ".join(EXCLUDED))}. Everything else is listed below with the
result of the attempt, including the sports where no fixture could be verified today.</p>
<table><thead><tr><th>Sport</th><th class="num">Fixtures</th><th>State</th><th>What happened</th><th>Official source tried</th></tr></thead>
<tbody>{cov_rows}</tbody></table>

<h2>By sport</h2>
<div class="grid">
{"".join(f'<div class="card"><div class="k">{e(s)}</div><div class="v">{COVERAGE[s]["fixtures"]}</div><div class="s"><a href="sports/{SPORT_SLUG[s]}.html">open board →</a></div></div>' for s in SPORT_SLUG)}
</div>

<h2>How to read the numbers</h2>
<div class="prose">
<p><strong>Model</strong> is the probability this model assigns to the selection. <strong>Fair price</strong> is
1 ÷ that probability, i.e. our line with no margin. <strong>Book price</strong> adds a 4.5–7.5% margin so the
number can be compared with a real market. Nothing here is a quote from a bookmaker.</p>
<p><strong>Tiers</strong>: High ≥ 70%, Medium 55–69.9%, Low &lt; 55%. The tier describes probability, not stake.
Rugby union is capped at Low because no official league table could be read (F-7A-04).</p>
</div>

<h2>Repository review</h2>
<p class="lede">Six findings from reading the existing tree line by line, with the command or file and line that
produced each one. Detail on <a href="flagged.html">Flagged for Review</a>.</p>
<ul class="tight">{"".join(f'<li><span class="mono">{e(r["id"])}</span> {e(r["where"])} — {e(r["status"])}: {e(r["finding"].split(".")[0])}.</li>' for r in REPO_REVIEW)}</ul>
"""
    page("index.html", "Overview", body, "index.html")

    # ------------------------------------------------------------------ picks
    rows = ""
    for p in sorted(picks, key=lambda p: (order[p["confidence"]], p["start_utc"] or "", -p["prob"])):
        rows += (
            f'<tr><td class="mono">{e(p["match_id"])}</td><td>{e(p["sport"])}</td>'
            f'<td>{e(p["home"])}<br><span class="dim">v {e(p["away"])}</span></td>'
            f'<td class="mono">{e(p["start_utc"] or "—")}</td>'
            f'<td><strong>{e(p["selection"])}</strong><br><span class="dim">{e(p["market"])}</span></td>'
            f'<td class="num">{p["prob"]*100:.1f}%<br><span class="dim">{dec_fmt(p["fair_decimal"])}</span></td>'
            f'<td>{badge(p["confidence"])}</td>'
            f'<td class="num">{e(p["best_selection"])}<br><span class="dim">{p["best_prob"]*100:.1f}% @ {dec_fmt(p["best_fair_decimal"])}</span></td>'
            f'<td>{"yes" if p["in_brief_band"] else "<span class=no>no</span>"}</td>'
            f'<td>{src_links(p["sources"], SOURCES)}</td></tr>')
    body = f"""
<h1>Picks — all {c["fixtures"]} fixtures</h1>
<p class="lede">One match-winner selection per fixture (the brief's "pick a match winner"), plus the
highest-probability selection anywhere on that fixture's board. Tiers come from the model, not from the price.
Every row links to the official page the fixture facts were read from.</p>
<div class="note">"In band" answers the brief's filter: is the originated fair price between 1.40 (-250) and
101.00 (+10000)? A 70%+ pick usually is not — that is arithmetic, not an error. See <a href="flagged.html">F-7A-01</a>.</div>
<table><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Start (UTC)</th><th>Winner pick</th><th>Model</th>
<th>Tier</th><th>Best market</th><th>In band</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table>
"""
    page("picks.html", "Picks", body, "picks.html")

    # ------------------------------------------------------------------ markets
    blocks = ""
    for fx in fixtures:
        ms = boards[fx["id"]]
        if fx.get("kind") == "field":
            head = (f'<h3>{e(fx["competition"])} — {e(fx["stage"])} <span class="dim">'
                    f'{e(fx["start_published"])}</span></h3>')
        else:
            head = (f'<h3>{e(fx["home"])} v {e(fx["away"])} <span class="dim">· {e(fx["competition"])} '
                    f'{e(fx["stage"])} · {e(fx["start_utc"] or fx["start_published"])}</span></h3>')
        inp = ""
        if fx["inputs"]:
            inp = ('<p class="dim" style="margin:4px 0 8px">Inputs — '
                   + " · ".join(f'{e(fx["inputs"][s]["label"])}: <span class="mono">{e(fx["inputs"][s]["value"] or "blank")}</span>'
                                for s in ("home", "away")) + "</p>")
        rws = "".join(
            f'<tr><td>{e(m["market"])}</td><td>{e(m["sel"])}</td><td class="dim">{e(m["detail"])}</td>'
            f'<td class="num">{m["prob"]*100:.1f}%</td><td class="num">{dec_fmt(m["fair"])}</td>'
            f'<td class="num">{e(m["american"])}</td><td class="num">{dec_fmt(m["book"])}</td>'
            f'<td>{"<span class=ok>yes</span>" if 1.40 <= (m["fair"] or 0) <= 101.0 else "<span class=dim>no</span>"}</td></tr>'
            for m in sorted(ms, key=lambda m: -m["prob"]))
        blocks += head + inp + (
            '<table><thead><tr><th>Market</th><th>Selection</th><th>Definition</th><th>Model</th>'
            '<th>Fair</th><th>American</th><th>Book</th><th>In band</th></tr></thead>'
            f'<tbody>{rws}</tbody></table>')

    a = ASSUMPTIONS
    ass_rows = ""
    for sport, v in a["moneyline_shrink"].items():
        ass_rows += (f'<tr><td>{e(sport)}</td><td class="num">{v["k"]}</td><td class="num">{v["home"]}</td>'
                     f'<td>{e(v["why"])}</td></tr>')
    tot_rows = "".join(
        f'<tr><td>{e(k)}</td><td class="num">{v.get("line", "—")}</td><td class="num">{v.get("mean", "—")}</td>'
        f'<td class="num">{v.get("sd", "—")}</td><td>{e(v.get("why", "Normal approximation around a documented baseline."))}</td></tr>'
        for k, v in a["totals"].items())
    hc_rows = "".join(
        f'<tr><td>{e(k)}</td><td class="num">{v.get("line", "—")}</td><td class="num">{v.get("sd", "—")}</td>'
        f'<td class="num">{v.get("mu_scale", "—")}</td><td>{e(v.get("why", "Goal/run/point margin modelled as normal around a scaled probability edge."))}</td></tr>'
        for k, v in a["handicap"].items())

    body = f"""
<h1>Markets — {c["markets"]} originated selections</h1>
<p class="lede">Every market we could originate from a sourced input, per fixture. Winner, handicap and total
boards are shown for each two-sided match; the Formula One meeting gets a 23-runner outright field board.
Rugby union carries only a winner board and a draw, because no sourced points baseline exists (F-7A-04).</p>
<div class="note">On the twelve NHL games our goal model is a documented baseline (6.0 goals, sd 2.0) rather than a
team-specific rate, so total-goal prices repeat across the slate. That is a stated modelling choice, not an
independent observation about each game.</div>
{blocks}

<h2>Assumptions, printed in full</h2>
<h3>Winner model</h3>
<table><thead><tr><th>Sport</th><th class="num">Shrinkage k</th><th class="num">Home term (logit)</th><th>Why</th></tr></thead>
<tbody>{ass_rows}</tbody></table>
<h3>Total baselines</h3>
<table><thead><tr><th>Sport</th><th class="num">Line</th><th class="num">Mean</th><th class="num">SD</th><th>Note</th></tr></thead>
<tbody>{tot_rows}</tbody></table>
<h3>Handicap</h3>
<table><thead><tr><th>Sport</th><th class="num">Line</th><th class="num">SD</th><th class="num">Mean scale</th><th>Note</th></tr></thead>
<tbody>{hc_rows}</tbody></table>
<h3>Field board</h3>
<p class="prose">{e(a["field"]["why"])} Exponent {a["field"]["exponent"]}, offset {a["field"]["offset"]}.</p>
<h3>Margin and tiers</h3>
<p class="prose">Book price = 1 / (probability × (1 + margin)), with margins of
{a["overround"]["two_way"]*100:.1f}% two-way, {a["overround"]["three_way"]*100:.1f}% three-way and
{a["overround"]["field"]*100:.1f}% for the F1 field. Tiers: High ≥ {a["tiers"]["high"]:.0%},
Medium ≥ {a["tiers"]["medium"]:.0%}, otherwise Low. Brief band: {a["band"]["min_decimal"]} to
{a["band"]["max_decimal"]} decimal.</p>
"""
    page("markets.html", "Markets", body, "markets.html")

    # ------------------------------------------------------------------ predictions
    blocks = ""
    for pr in sorted(preds, key=lambda p: (order[p["confidence"]], -p["probability"])):
        blocks += f"""
<div class="card" style="margin:12px 0">
<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap">
<div><strong>{e(pr["home"])} v {e(pr["away"])}</strong>
<span class="pill">{e(pr["sport"])}</span><span class="pill">{e(pr["competition"])}</span></div>
<div>{badge(pr["confidence"])}</div></div>
<p style="margin:10px 0 6px"><strong>Selection:</strong> {e(pr["selection"])} — {e(pr["market"])}
<span class="dim">· model {pr["probability"]*100:.1f}% · fair {dec_fmt(pr["fair_decimal"])} ·
{pr["words"]} words</span></p>
<p class="prose" style="margin:0">{e(pr["text"])}</p>
<p class="dim" style="margin:8px 0 0;font-size:12px">Verified against: {src_links(pr["sources"], SOURCES)}</p>
</div>"""
    body = f"""
<h1>Written predictions — {c["predictions"]}</h1>
<p class="lede">One hand-written paragraph per selection, minimum 30 words, stating the pick and the price.
Each claim about form or history is repeated from a value stored in the fixture row, which links to the official
page it was read from. No injury, team-news, weather or head-to-head claims are made anywhere, because none of
those was read today.</p>
<div class="note">The brief asks for predictions on high-confidence picks. Four match-winner picks clear 70% on
this board; the other {c["predictions"] - 4} writeups cover the strongest 70%+ handicap selections and the
best of the Medium tier, and each one is labelled with the tier it actually earned.</div>
{blocks}
"""
    page("predictions.html", "Predictions", body, "predictions.html")

    # ------------------------------------------------------------------ coverage
    rows = ""
    for sport in IN_SCOPE:
        cvg = COVERAGE[sport]
        rows += (f'<tr><td>{e(sport)}</td><td class="num">{cvg["fixtures"]}</td>'
                 f'<td>{e(cvg["state"].replace("_", " "))}</td><td>{e(cvg["note"])}</td>'
                 f'<td>{src_links(cvg["source"], SOURCES) if cvg["source"] else "—"}</td></tr>')
    body = f"""
<h1>Coverage — 17 in-scope sports</h1>
<p class="lede">Excluded by the brief: {e(", ".join(EXCLUDED))}.</p>
<p class="lede">Five sports carry verified fixtures on this desk. The other twelve are reported honestly with the
URL that was tried and what came back, so a reader can retry any of them. No row is invented to fill a gap.</p>
<table><thead><tr><th>Sport</th><th class="num">Fixtures</th><th>State</th><th>What happened</th><th>Official source tried</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>What "state" means</h2>
<ul class="tight">
<li><span class="mono">verified</span> — fixture facts read on an official page, both sides have a sourced input.</li>
<li><span class="mono">verified fixture only</span> — the fixture is confirmed but no strength input was readable, so the price is neutral and the tier is capped.</li>
<li><span class="mono">no fixture in window</span> — the official board was read and publishes no in-scope match for 22–26 October.</li>
<li><span class="mono">blocked</span> / <span class="mono">client rendered</span> — the official page was reached but served no fixture data to this client.</li>
<li><span class="mono">not attempted</span> — the sport has no static official board this session; named so the gap is explicit.</li>
</ul>
"""
    page("coverage.html", "Coverage", body, "coverage.html")

    # ------------------------------------------------------------------ verification
    rows = ""
    for fx in fixtures:
        rows += (f'<tr><td class="mono">{e(fx["id"])}</td><td>{e(fx["sport"])}</td>'
                 f'<td>{e(fx["home"])} v {e(fx["away"])}</td>'
                 f'<td class="mono">{e(fx["start_utc"]) if fx["start_utc"] else "<span class=no>blank</span>"}</td>'
                 f'<td>{e(fx["venue"]) if fx.get("venue") else "<span class=no>blank</span>"}</td>'
                 f'<td class="mono">{e(fx["inputs"]["home"]["value"]) if fx["inputs"] else "—"}</td>'
                 f'<td class="mono">{e(fx["inputs"]["away"]["value"]) if fx["inputs"] else "—"}</td>'
                 f'<td>{src_links(fx["sources"], SOURCES)}</td></tr>')
    flag_rows = "".join(
        f'<tr><td>{e(f["id"])}</td><td>{e(f["title"])}</td><td class="dim">{e(f["detail"])}</td>'
        f'<td>{src_links(f["sources"], SOURCES) if f["sources"] else "—"}</td></tr>'
        for f in FLAGS if f["severity"] != "low")
    counts = "".join(
        f'<tr><td class="mono">{e(k)}</td><td>{e(v["status"])}</td><td>{e(v["name"])}</td>'
        f'<td><a href="{e(v["url"])}">{e(v["url"])}</a></td></tr>' for k, v in SOURCES.items())
    body = f"""
<h1>Verification ledger</h1>
<p class="lede">One row per fixture, showing exactly which official page each value came from. Blank cells are
values the official page did not publish — they are left empty on purpose rather than filled in.</p>
<div class="grid">
<div class="card"><div class="k">Rows</div><div class="v">{c["fixtures"]}</div><div class="s">all source-linked</div></div>
<div class="card"><div class="k">Values left blank</div><div class="v">{sum(1 for f in fixtures if not f["start_utc"]) + sum(1 for f in fixtures if not f.get("venue"))}</div><div class="s">named on the flagged page</div></div>
<div class="card"><div class="k">Official pages read</div><div class="v">{sum(1 for v in SOURCES.values() if v["status"].startswith("read"))}</div><div class="s">of {len(SOURCES)} attempted</div></div>
</div>
<table><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Start (UTC)</th><th>Venue</th><th>Home input</th>
<th>Away input</th><th>Official source</th></tr></thead><tbody>{rows}</tbody></table>

<h2>Source register — every URL attempted this session</h2>
<table><thead><tr><th>Key</th><th>Status</th><th>Page</th><th>URL</th></tr></thead><tbody>{counts}</tbody></table>

<h2>Findings at Medium severity or above</h2>
<table><thead><tr><th>ID</th><th>Finding</th><th>Detail</th><th>Source</th></tr></thead><tbody>{flag_rows}</tbody></table>
"""
    page("verification.html", "Verification", body, "verification.html")

    # ------------------------------------------------------------------ flagged
    flag_blocks = ""
    for f in FLAGS:
        flag_blocks += f"""
<div class="card" style="margin:12px 0">
<div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap">
<div><span class="mono">{e(f["id"])}</span> <strong>{e(f["title"])}</strong></div>
<div><span class="pill">{e(f["severity"])}</span><span class="pill">{e(f["status"])}</span></div></div>
<p style="margin:9px 0 0">{e(f["detail"])}</p>
<p class="dim" style="margin:8px 0 0;font-size:12px">Source: {src_links(f["sources"], SOURCES) if f["sources"] else "no external source — internal arithmetic or coverage record"}</p>
</div>"""
    repo_rows = "".join(
        f'<tr><td class="mono">{e(r["id"])}</td><td class="mono">{e(r["where"])}</td>'
        f'<td>{e(r["status"])}</td><td>{e(r["finding"])}</td>'
        f'<td class="mono dim">{e(r["evidence"])}</td></tr>' for r in REPO_REVIEW)
    body = f"""
<h1>Flagged for review</h1>
<p class="lede">Everything on this page is published deliberately: values the official sources did not supply,
sources that blocked this client, and irregularities found in the repository. Nothing here blocks the release —
it is the list to read after the site is live.</p>
<h2>Data and coverage flags ({len(FLAGS)})</h2>
{flag_blocks}
<h2>Repository review — findings with the evidence that produced them</h2>
<table><thead><tr><th>ID</th><th>Where</th><th>Status</th><th>Finding</th><th>Evidence</th></tr></thead>
<tbody>{repo_rows}</tbody></table>
<h2>What this desk did not touch</h2>
<p class="prose">No file belonging to another session's scope was edited. This desk is additive: a new
<span class="mono">data/7a5b5360/</span> namespace, new <span class="mono">scripts/s7a5b5360_*.py</span> files, a
new <span class="mono">7a5b5360/</span> page tree, and an append-only entry in
<span class="mono">COORDINATION.md</span>.</p>
"""
    page("flagged.html", "Flagged for review", body, "flagged.html")

    # ------------------------------------------------------------------ sources
    rows = ""
    for k, v in SOURCES.items():
        used = ", ".join(v["used_for"]) if v["used_for"] else "—"
        rows += (f'<tr><td class="mono">{e(k)}</td><td>{e(v["org"])}</td><td>{e(v["name"])}</td>'
                 f'<td>{e(v["status"])}</td><td>{e(used)}</td>'
                 f'<td><a href="{e(v["url"])}">{e(v["url"])}</a></td></tr>')
    body = f"""
<h1>Sources</h1>
<p class="lede">Only governing bodies, leagues, tours and the teams themselves count as official here. No news
outlet, aggregator, tipster site or Wikipedia page is used to confirm a fact on this desk. Every URL below was
fetched during this session, including the ones that failed.</p>
<table><thead><tr><th>Key</th><th>Organisation</th><th>Page</th><th>Status</th><th>Used for</th><th>URL</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>Status vocabulary</h2>
<ul class="tight">
<li><span class="mono">read</span> — fetched and read; values extracted.</li>
<li><span class="mono">read / no fixture</span> — fetched and read; the page publishes no in-scope fixture for the window.</li>
<li><span class="mono">blocked</span> — consent wall, or HTTP 4xx/5xx.</li>
<li><span class="mono">client-rendered</span> — the page was reached but the fixture grid is assembled in the browser, so the fetch returned an empty shell.</li>
</ul>
"""
    page("sources.html", "Sources", body, "sources.html")

    # ------------------------------------------------------------------ methodology
    prose = "".join(f"<h2>{e(t)}</h2><p>{e(b)}</p>" for t, b in METHOD_TEXT)
    body = f"""
<h1>Methodology</h1>
<p class="lede">What this desk does, what it refuses to do, and where every number comes from.</p>
<div class="prose">{prose}</div>
<h2>Worked example</h2>
<p class="prose">New York Islanders v Los Angeles Kings, 22 October. Sourced inputs: Islanders 5-3-1
(11 points from 18, .611), Kings 1-4-2 (4 from 14, .286). Log-odds difference 1.367, shrunk by k = 0.55 and
given a 0.20 home term, gives logistic(0.952) = 72.1%. Fair price 1/0.721 = 1.39; with a 4.5% margin the book
price is 1.32. The pick is the Islanders to win, graded High because 72.1% clears the 70% line, and flagged as
out of band because 1.39 is shorter than -250.</p>
<h2>Files</h2>
<ul class="tight">
<li><span class="mono">scripts/s7a5b5360_data.py</span> — the sourced fixtures, inputs and source register.</li>
<li><span class="mono">scripts/s7a5b5360_build.py</span> — the model, the market generator and the exports.</li>
<li><span class="mono">scripts/s7a5b5360_content.py</span> — predictions, flags and this text.</li>
<li><span class="mono">scripts/s7a5b5360_site.py</span> — this dashboard.</li>
<li><span class="mono">data/7a5b5360/</span> — fixtures, markets, picks, predictions, high-probability selections, sources, coverage, flags and matches.csv.</li>
</ul>
"""
    page("methodology.html", "Methodology", body, "methodology.html")

    # ------------------------------------------------------------------ per sport
    pages = 9
    for sport, slug in SPORT_SLUG.items():
        sfixtures = [f for f in fixtures if f["sport"] == sport]
        spicks = {p["match_id"]: p for p in picks if p["sport"] == sport}
        rows = ""
        for fx in sfixtures:
            p = spicks[fx["id"]]
            rows += (f'<tr><td class="mono">{e(fx["start_utc"] or fx["start_published"])}</td>'
                     f'<td>{e(fx["home"])} v {e(fx["away"])}</td><td>{e(fx.get("venue") or "—")}</td>'
                     f'<td class="mono">{e(fx["inputs"]["home"]["value"]) if fx["inputs"] else "—"}<br>'
                     f'<span class="dim">{e(fx["inputs"]["away"]["value"]) if fx["inputs"] else ""}</span></td>'
                     f'<td><strong>{e(p["selection"])}</strong><br><span class="dim">{e(p["market"])}</span></td>'
                     f'<td class="num">{p["prob"]*100:.1f}%<br><span class="dim">{dec_fmt(p["fair_decimal"])}</span></td>'
                     f'<td>{badge(p["confidence"])}</td><td>{src_links(fx["sources"], SOURCES)}</td></tr>')
        board_blocks = ""
        for fx in sfixtures:
            ms = boards[fx["id"]]
            rws = "".join(
                f'<tr><td>{e(m["market"])}</td><td>{e(m["sel"])}</td><td class="num">{m["prob"]*100:.1f}%</td>'
                f'<td class="num">{dec_fmt(m["fair"])}</td><td class="num">{e(m["american"])}</td>'
                f'<td class="num">{dec_fmt(m["book"])}</td></tr>' for m in sorted(ms, key=lambda m: -m["prob"]))
            board_blocks += (f'<h3>{e(fx["home"])} v {e(fx["away"])} '
                             f'<span class="dim">· {e(fx["stage"])}</span></h3>'
                             '<table><thead><tr><th>Market</th><th>Selection</th><th>Model</th><th>Fair</th>'
                             '<th>American</th><th>Book</th></tr></thead>'
                             f'<tbody>{rws}</tbody></table>')
        cvg = COVERAGE[sport]
        body = f"""
<h1>{e(sport)} — {len(sfixtures)} fixtures</h1>
<p class="lede">{e(cvg["note"])}</p>
<table><thead><tr><th>Start</th><th>Match</th><th>Venue</th><th>Sourced inputs</th><th>Pick</th>
<th>Model</th><th>Tier</th><th>Official source</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Full board</h2>
{board_blocks}
<p class="dim"><a href="../picks.html">All picks</a> · <a href="../markets.html">All markets</a> ·
<a href="../coverage.html">Coverage</a></p>
"""
        page(f"sports/{slug}.html", sport, body, f"sports/{slug}.html")
        pages += 1

    return pages
