"""Build the 580f43c9 clarity-first desk.

Run:  python3 scripts/s580f43c9_build.py
Out:  580f43c9/*.html, 580f43c9/sports/*.html, data/580f43c9/*.json
"""

import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s580f43c9_data import (SOURCES, MATCHES, PICKS, GAPS, FLAGS, AUDIT, OBSERVED,
                            MARKET_FAMILIES, NHL_MARKET_FAMILIES, TENNIS_MARKET_FAMILIES,
                            MLB_MARKET_FAMILIES, GAA_MARKET_FAMILIES)
from s580f43c9_model import (originate, hockey_derivatives, tier, american_from_prob,
                             decimal_from_prob, in_band, INPUT_COMPLETE)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "580f43c9"
DATA = ROOT / "data" / "580f43c9"
LIVE = "https://buffedlizard55-lab.github.io/OLBG1/580f43c9/"
REPO = "https://github.com/buffedlizard55-lab/OLBG1"

SPORTS = [
    ("basketball", "Basketball", "NBA"),
    ("ice-hockey", "Ice Hockey", "NHL"),
    ("baseball", "Baseball", "MLB"),
    ("gaelic-football", "Gaelic Sports", "Cork GAA club championships"),
    ("tennis", "Tennis", "ATP Tour"),
    ("golf", "Golf", "—"),
    ("volleyball", "Volleyball", "—"),
    ("rugby-union", "Rugby Union", "URC"),
    ("cricket", "Cricket", "—"),
    ("snooker", "Snooker", "—"),
    ("darts", "Darts", "PDC European Championship"),
    ("greyhounds", "Greyhounds", "—"),
    ("motor-racing", "Motor Racing", "Formula 1"),
    ("handball", "Handball", "—"),
    ("rugby-league", "Rugby League", "—"),
]
SPORT_NAME = {s: n for s, n, _ in SPORTS}

MARKETS_BY_SPORT = {
    "ice-hockey": NHL_MARKET_FAMILIES,
    "tennis": TENNIS_MARKET_FAMILIES,
    "baseball": MLB_MARKET_FAMILIES,
    "gaelic-football": GAA_MARKET_FAMILIES,
}

SOURCE_BY_ID = {s["id"]: s for s in SOURCES}
MATCH_BY_ID = {m["id"]: m for m in MATCHES}


def e(v):
    return html.escape("" if v is None else str(v), quote=True)


def fmt_am(v):
    if v is None:
        return "—"
    return f"{v:+d}"


def fmt_dec(v):
    if v is None or v == float("inf"):
        return "—"
    return f"{v:.2f}"


def fmt_pct(v):
    return "—" if v is None else f"{v * 100:.1f}%"


def fmt_start(iso, label=""):
    if not iso:
        return label or "start not confirmed"
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc)
    return dt.strftime("%d %b %Y · %H:%M UTC")


def confidence_class(c):
    return {"high": "hi", "medium": "md", "low": "lo"}[c]


# ---------------------------------------------------------------------------
# Build the priced card
# ---------------------------------------------------------------------------

def build_cards():
    cards = []
    for pick in PICKS:
        fx = MATCH_BY_ID[pick["match"]]
        line = originate(fx)
        sport = fx["sport"]
        side = pick["side"]
        p = line["p_home"] if side == "b" else line["p_away"]
        sel = fx["b"] if side == "b" else fx["a"]
        other = fx["a"] if side == "b" else fx["b"]
        out_of_band = p > 0.70 and not in_band(p)
        p = round(p, 6)
        out_of_band = p > 0.70 and not in_band(p)
        conf = tier(p, sport, inputs_complete=INPUT_COMPLETE[sport], out_of_band=out_of_band)
        am = american_from_prob(p)
        card = dict(
            match_id=fx["id"], sport=sport, sport_name=SPORT_NAME[sport],
            comp=fx["comp"], round=fx["round"], match=f'{fx["a"]} v {fx["b"]}',
            venue=fx["venue"], start_utc=fx["start_utc"], start_label=fx["start_label"],
            selection=sel, opponent=other, side=side, market=pick["market"],
            prob=p, fair_decimal=round(decimal_from_prob(p), 3), fair_american=am,
            fair_prob_pct=round(p * 100, 1), in_band=in_band(p), out_of_band=out_of_band,
            confidence=conf, prose=pick["prose"], words=len(pick["prose"].split()),
            source=SOURCE_BY_ID[fx["source"]], facts=fx["facts"], injuries=fx["injuries"],
            injury_note=fx["injury_note"], units="probability of the selection winning",
        )
        if sport == "ice-hockey":
            card["derivatives"] = hockey_derivatives(fx)
        cards.append(card)
    order = {"high": 0, "medium": 1, "low": 2}
    cards.sort(key=lambda c: (order[c["confidence"]], c["start_utc"] or "9999", -c["prob"]))
    return cards


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

CSS = """
:root{--bg:#f4f6f9;--surface:#fff;--ink:#0f172a;--muted:#5b6675;--line:#e2e8f0;
--accent:#0b6b4f;--accent-dark:#08503b;--soft:#e8f7f0;--amber:#b54708;--amber-soft:#fff7e6;
--red:#b42318;--red-soft:#fef3f2;--blue:#1d4ed8;--blue-soft:#eef4ff;--radius:14px;
--shadow:0 1px 2px rgba(15,23,42,.06),0 1px 3px rgba(15,23,42,.08)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent-dark);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1200px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:30;background:rgba(255,255,255,.97);
border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;gap:16px;align-items:center;flex-wrap:wrap;min-height:62px}
.brand{font-weight:800;letter-spacing:-.01em;display:flex;gap:9px;align-items:center;color:var(--ink)}
.brand .dot{width:11px;height:11px;border-radius:50%;background:var(--accent)}
.brand small{display:block;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
color:var(--muted);font-weight:600}
nav.main{margin-left:auto;display:flex;gap:2px;flex-wrap:wrap}
nav.main a{padding:7px 10px;border-radius:9px;font-size:13.5px;font-weight:600;color:#334155}
nav.main a:hover{background:#eef2f7;text-decoration:none}
nav.main a[aria-current=page]{background:var(--soft);color:var(--accent-dark)}
.hero{padding:30px 0 6px}
.eyebrow{margin:0 0 8px;font-size:12px;font-weight:800;letter-spacing:.13em;text-transform:uppercase;
color:var(--accent-dark)}
h1{margin:0;font-size:clamp(27px,3.6vw,38px);line-height:1.12;letter-spacing:-.02em}
h2{margin:34px 0 10px;font-size:22px;letter-spacing:-.01em}
h3{margin:20px 0 8px;font-size:17px}
p.lede{color:var(--muted);font-size:17px;max-width:80ch;margin:12px 0 0}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:20px 0 4px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
padding:13px 15px;box-shadow:var(--shadow)}
.kpi b{display:block;font-size:25px;line-height:1.1;letter-spacing:-.02em}
.kpi span{font-size:12.5px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.06em}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
padding:18px;box-shadow:var(--shadow);margin:14px 0}
.card.tight{padding:14px 16px}
.starthere{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:18px 0}
.starthere a{display:block;background:var(--surface);border:1px solid var(--line);
border-radius:var(--radius);padding:15px 16px;box-shadow:var(--shadow)}
.starthere a:hover{border-color:var(--accent);text-decoration:none}
.starthere b{display:block;color:var(--accent-dark);font-size:15.5px;margin-bottom:3px}
.starthere span{color:var(--muted);font-size:13.5px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f8fafc;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:#475569;
position:sticky;top:62px}
tbody tr:hover{background:#fbfdff}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
table.scroll{display:block;overflow-x:auto;white-space:nowrap}
table.scroll tbody,table.scroll thead{display:table;width:100%}
.pick{font-weight:800;color:var(--accent-dark)}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:800;
letter-spacing:.04em;text-transform:uppercase}
.badge.hi{background:var(--soft);color:var(--accent-dark)}
.badge.md{background:var(--blue-soft);color:var(--blue)}
.badge.lo{background:var(--amber-soft);color:var(--amber)}
.badge.gap{background:var(--red-soft);color:var(--red)}
.badge.ok{background:var(--soft);color:var(--accent-dark)}
.note{background:var(--blue-soft);border:1px solid #cfe0ff;border-radius:12px;padding:13px 15px;
font-size:14px;margin:14px 0}
.warn{background:var(--amber-soft);border:1px solid #f6dfae;border-radius:12px;padding:13px 15px;
font-size:14px;margin:14px 0}
.danger{background:var(--red-soft);border:1px solid #f3c9c5;border-radius:12px;padding:13px 15px;
font-size:14px;margin:14px 0}
.okay{background:var(--soft);border:1px solid #bfe8d5;border-radius:12px;padding:13px 15px;
font-size:14px;margin:14px 0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.pred{border-left:4px solid var(--accent);background:#fcfdfe;padding:12px 15px;border-radius:0 10px 10px 0;
margin:10px 0;font-size:15px}
.small{font-size:13px;color:var(--muted)}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px}
footer{border-top:1px solid var(--line);margin-top:40px;padding:22px 0;color:var(--muted);font-size:13px}
ul.clean{margin:8px 0 0 18px;padding:0}ul.clean li{margin:4px 0}
@media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.starthere,.grid2,.grid3{grid-template-columns:1fr}
th{position:static}}
"""


def page(title, body, current, depth=0):
    prefix = "../" if depth else ""
    nav = [("index.html", "Summary"), ("picks.html", "Picks"), ("predictions.html", "Write-ups"),
           ("matches.html", "Matches"), ("markets.html", "Markets"), ("sports/basketball.html", "Sports"),
           ("sources.html", "Sources"), ("flagged.html", "Flagged"), ("repo-audit.html", "Repo audit"),
           ("methodology.html", "Method")]
    links = "".join(
        f'<a href="{prefix}{href}"{" aria-current=page" if href == current else ""}>{e(label)}</a>'
        for href, label in nav)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG research desk 580f43c9</title>
<style>{CSS}</style></head><body>
<header class="top"><div class="wrap">
<div class="brand"><span class="dot"></span><span>OLBG research desk<small>24–25 October 2026 · session 580f43c9</small></span></div>
<nav class="main">{links}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="wrap"><p><strong>Independent research, not a tipster service.</strong> Prices are our own
estimates, not bookmaker odds. Nothing here is a guarantee, and no bet is risk-free.
Built from official league, tour and governing-body sources read on 24 October 2026; every row links to the
page it came from. Not affiliated with OLBG. 18+. If gambling is causing harm, see
<a href="https://www.gamcare.org.uk/">GamCare</a> or <a href="https://www.begambleaware.org/">BeGambleAware</a>.</p>
<p class="small">Repository: <a href="{REPO}">{e(REPO.replace('https://', ''))}</a> ·
Live desk: <a href="{LIVE}">{e(LIVE.replace('https://', ''))}</a> ·
Evidence frozen at {e(OBSERVED)}</p></footer>
</body></html>"""


def picks_table(cards, prefix=""):
    rows = []
    for c in cards:
        rows.append(f"""<tr>
<td><a href="{prefix}sports/{e(c['sport'])}.html">{e(c['sport_name'])}</a></td>
<td>{e(c['match'])}<br><span class="small">{e(c['comp'])} · {e(c['round'])}</span></td>
<td class="pick">{e(c['selection'])}</td>
<td>{e(c['market'])}</td>
<td><span class="badge {confidence_class(c['confidence'])}">{e(c['confidence'])}</span></td>
<td class="num">{fmt_am(c['fair_american'])}<br><span class="small">{fmt_pct(c['prob'])} · {fmt_dec(c['fair_decimal'])}</span></td>
<td>{fmt_start(c['start_utc'], c['start_label'])}</td>
<td><a href="{e(c['source']['url'])}" rel="noopener">official source</a></td>
</tr>""")
    return f"""<table class="scroll"><thead><tr><th>Sport</th><th>Match</th><th>Our pick</th>
<th>Market</th><th>Confidence</th><th class="num">Fair price / chance</th><th>Start</th><th>Evidence</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table>"""


def build():
    cards = build_cards()
    counts = {k: sum(1 for c in cards if c["confidence"] == k) for k in ("high", "medium", "low")}
    by_sport = {}
    for c in cards:
        by_sport.setdefault(c["sport"], []).append(c)
    gap_by_sport = {g["sport"]: g for g in GAPS}
    today = [c for c in cards if c["start_utc"] and c["start_utc"][:10] == "2026-10-24"]
    upcoming = [c for c in cards if c not in today]

    # ---------------- JSON ----------------
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "sources.json").write_text(json.dumps(SOURCES, indent=2) + "\n")
    (DATA / "matches.json").write_text(json.dumps(MATCHES, indent=2) + "\n")
    (DATA / "picks.json").write_text(json.dumps(cards, indent=2) + "\n")
    (DATA / "gaps.json").write_text(json.dumps(GAPS, indent=2) + "\n")
    (DATA / "flags.json").write_text(json.dumps(FLAGS, indent=2) + "\n")
    (DATA / "audit.json").write_text(json.dumps(AUDIT, indent=2) + "\n")
    summary = dict(desk="580f43c9-olbg1", observed=OBSERVED, matches=len(MATCHES), picks=len(cards),
                   sports_priced=sorted(by_sport), sports_gap=[g["sport"] for g in GAPS],
                   tiers=counts, in_band=sum(1 for c in cards if c["in_band"]),
                   out_of_band=sum(1 for c in cards if c["out_of_band"]),
                   flags=len(FLAGS), sources=len(SOURCES),
                   official_sources=sum(1 for s in SOURCES if s["official"]))
    (DATA / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # ---------------- index ----------------
    over70 = [c for c in cards if c["prob"] > 0.70]
    if over70:
        over70_text = ("Selections above 70% but excluded by the −250 floor: " +
                       "; ".join(f"{c['selection']} ({fmt_pct(c['prob'])}, fair {fmt_am(c['fair_american'])})"
                                 for c in over70) +
                       ". Each is published at medium tier with the reason printed on its row.")
    else:
        over70_text = "No selection cleared 70% at all."
    head = f"""<section class="hero">
<p class="eyebrow">Executive summary · {e(OBSERVED)}</p>
<h1>Thirteen priced selections across five sports — and an honest list of the ten sports we could not price</h1>
<p class="lede">This page is the summary. The picks are the table directly below it, and every pick has a
full written case on <a href="picks.html">Picks</a> and a longer prediction on
<a href="predictions.html">Write-ups</a>. Sports we could not price are listed with the exact source that
blocked them.</p>
<div class="kpis">
<div class="kpi"><b>{len(cards)}</b><span>Priced selections</span></div>
<div class="kpi"><b>{len(by_sport)}/15</b><span>Sports with a pick</span></div>
<div class="kpi"><b>{counts['high']}</b><span>High confidence</span></div>
<div class="kpi"><b>{counts['medium']}</b><span>Medium confidence</span></div>
<div class="kpi"><b>{counts['low']}</b><span>Low confidence</span></div>
</div></section>

<div class="starthere">
<a href="picks.html"><b>The picks, in one table →</b><span>Every selection with its odds, confidence and
official source link. This is the page you want if you only read one.</span></a>
<a href="predictions.html"><b>The written predictions →</b><span>One original, non-repeating case per
selection, 55–95 words, naming the pick, the form and the match statistics behind it.</span></a>
<a href="flagged.html"><b>What is missing and why →</b><span>The ten sports with no line, the blank injury
fields and the arithmetic that leaves the High tier empty today.</span></a>
</div>

<div class="danger"><strong>Why there are no High-confidence picks today.</strong> The brief asks for
selections above 70% <em>and</em> for fair prices no shorter than −250. A −250 price is exactly 71.43%, so
only selections landing between 70.00% and 71.43% can satisfy both rules. Nothing on this card falls inside
that 1.4-point window. {over70_text} See <a href="flagged.html">Flagged for review F-01/F-02</a>.</div>

<h2>Every pick on the card</h2>
<p class="small">Sorted by confidence, then by start time. “Fair price” is our own no-margin price derived
from our probability — it is not a bookmaker quote and it is not a promise of availability.</p>
{picks_table(cards)}

<div class="grid2">
<div class="card tight"><h3>Today (24 October)</h3>
<p class="small">{len(today)} selections start on 24 October UTC.</p>
<ul class="clean">{''.join(f'<li><strong>{e(c["selection"])}</strong> — {e(c["match"])} · {fmt_am(c["fair_american"])}</li>' for c in today) or '<li>None.</li>'}</ul></div>
<div class="card tight"><h3>Upcoming (25 October onward)</h3>
<p class="small">{len(upcoming)} selections start later.</p>
<ul class="clean">{''.join(f'<li><strong>{e(c["selection"])}</strong> — {e(c["match"])} · {fmt_am(c["fair_american"])}</li>' for c in upcoming) or '<li>None.</li>'}</ul></div>
</div>

<h2>Sports we could not price</h2>
<p class="small">Each row names the source that blocked a line. Nothing is filled in to look complete.</p>
<table><thead><tr><th>Sport</th><th>Why no line</th><th>Source that blocked it</th></tr></thead><tbody>
{''.join(f'<tr><td><a href="sports/{slug_of(g["sport"])}.html">{e(g["sport"])}</a></td><td>{e(g["blocked"])}</td><td><a href="{e(g["source"])}" rel="noopener">{e(g["source"].replace("https://", ""))}</a></td></tr>' for g in GAPS)}
</tbody></table>

<h2>Where everything lives</h2>
<div class="grid3">
<div class="card tight"><h3>Picks &amp; write-ups</h3><ul class="clean">
<li><a href="picks.html">Picks</a> — the table, plus per-pick reasoning and market audit</li>
<li><a href="predictions.html">Write-ups</a> — the full predictions</li>
<li><a href="markets.html">Markets</a> — every market family examined, priced or withheld</li></ul></div>
<div class="card tight"><h3>Evidence</h3><ul class="clean">
<li><a href="matches.html">Matches</a> — all 13 fixtures with the facts read for them</li>
<li><a href="sources.html">Sources</a> — {len(SOURCES)} sources, {sum(1 for s in SOURCES if s['official'])} of them official</li>
<li><a href="methodology.html">Method</a> — the formulas and the confidence gate</li></ul></div>
<div class="card tight"><h3>Review</h3><ul class="clean">
<li><a href="flagged.html">Flagged for review</a> — {len(FLAGS)} items</li>
<li><a href="repo-audit.html">Repo audit</a> — {len(AUDIT)} checks, line by line</li>
<li><a href="sports/basketball.html">Sport pages</a> — 15 of them, one per brief sport</li></ul></div>
</div>"""

    write_page("index.html", "Executive summary", head, "index.html")

    # ---------------- picks ----------------
    rows = []
    for c in cards:
        deriv = ""
        if c["sport"] == "ice-hockey":
            d = c["derivatives"]
            deriv = (f"<div class='small'>Puck line −1.5 {e(c['match'].split(' v ')[1])}: "
                     f"{fmt_am(american_from_prob(d['home_puck_line']))} "
                     f"({fmt_pct(d['home_puck_line'])}); away −1.5 "
                     f"{fmt_am(american_from_prob(d['away_puck_line']))} ({fmt_pct(d['away_puck_line'])}); "
                     f"total {d['total_line']}: over {fmt_am(american_from_prob(d['over']))} "
                     f"({fmt_pct(d['over'])}) / under {fmt_am(american_from_prob(d['under']))} "
                     f"({fmt_pct(d['under'])})</div>")
        band = ("inside −250…+10000" if c["in_band"] else
                ("outside the band: price shorter than −250" if c["out_of_band"] else "outside the band"))
        rows.append(f"""<tr>
<td><a href="sports/{e(c['sport'])}.html">{e(c['sport_name'])}</a><br><span class="small">{e(c['comp'])}</span></td>
<td><strong>{e(c['match'])}</strong><br><span class="small">{fmt_start(c['start_utc'], c['start_label'])} · {e(c['venue'] or 'venue not read')}</span></td>
<td><span class="pick">{e(c['selection'])}</span><br><span class="small">{e(c['market'])}</span></td>
<td class="num"><strong>{fmt_am(c['fair_american'])}</strong><br><span class="small">{fmt_pct(c['prob'])} · dec {fmt_dec(c['fair_decimal'])}</span></td>
<td><span class="badge {confidence_class(c['confidence'])}">{e(c['confidence'])}</span><br><span class="small">{e(band)}</span></td>
<td style="min-width:280px">{e(c['prose'])}<div class="small" style="margin-top:6px">{c['words']} words</div>{deriv}</td>
<td><a href="{e(c['source']['url'])}" rel="noopener">{e(c['source']['publisher'])}</a><br>
<span class="small">read {e(c['source']['observed'])}</span></td>
</tr>""")
    picks_body = f"""<section class="hero"><p class="eyebrow">The picks</p>
<h1>All {len(cards)} selections, with the case and the evidence</h1>
<p class="lede">Each row names one selection, its market, our fair price and chance, the confidence tier, a
full written case, and a link to the official page the underlying facts came from. Picks are on the left of
the case column; the price column is ours, not a bookmaker's.</p></section>
<div class="warn"><strong>Confidence gate.</strong> High = better than 70% and fair price inside −250…+10000.
Medium = 60–70%, or above 70% but priced shorter than −250 (excluded by the band rule).
Low = below 60%, or a sport whose inputs are incomplete. Today: {counts['high']} high, {counts['medium']} medium,
{counts['low']} low.</div>
<table><thead><tr><th>Sport</th><th>Match &amp; start</th><th>Pick &amp; market</th><th class="num">Fair price</th>
<th>Confidence</th><th>Why (full case)</th><th>Evidence</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p class="small">Injury and availability fields are blank for every row: no official injury report was read
for any of these fixtures. See <a href="flagged.html">Flagged items F-03</a>.</p>"""
    write_page("picks.html", "Picks", picks_body, "picks.html")

    # ---------------- predictions ----------------
    pred_cards = []
    for c in cards:
        facts = "".join(
            f"<li><strong>{e(k.replace('_', ' '))}</strong>: {e(v)}</li>"
            for k, v in c["facts"].items())
        pred_cards.append(f"""<article class="card">
<h3>{e(c['match'])} — <span class="pick">{e(c['selection'])}</span> <span class="badge {confidence_class(c['confidence'])}">{e(c['confidence'])}</span></h3>
<p class="small">{e(c['sport_name'])} · {e(c['comp'])} · {e(c['round'])} · {fmt_start(c['start_utc'], c['start_label'])}
· our fair price {fmt_am(c['fair_american'])} ({fmt_pct(c['prob'])})</p>
<div class="pred">{e(c['prose'])}</div>
<details><summary class="small">Every fact used, straight from the official source</summary>
<ul class="clean small">{facts}
<li><strong>injuries</strong>: blank — {e(c['injury_note'])}</li></ul></details>
<p class="small">Source: <a href="{e(c['source']['url'])}" rel="noopener">{e(c['source']['publisher'])}</a>
({e(c['source']['observed'])}) — {e(c['source']['scope'])}</p>
</article>""")
    predictions_body = f"""<section class="hero"><p class="eyebrow">Written predictions</p>
<h1>One original case per pick — no repeated sentences, no filler</h1>
<p class="lede">Every write-up names the selection unambiguously, both participants, the current record or
run, the recent results behind it and the match-specific numbers we read; each then states the betting
selection in plain words. Lengths run {min(c['words'] for c in cards)}–{max(c['words'] for c in cards)} words.
Where an injury could not be established from an official report, the field is left blank rather than
guessed.</p></section>
{''.join(pred_cards)}"""
    write_page("predictions.html", "Write-ups", predictions_body, "predictions.html")

    # ---------------- matches ----------------
    mrows = []
    for m in MATCHES:
        src = SOURCE_BY_ID[m["source"]]
        fact_str = "; ".join(f"{k.replace('_', ' ')} {v}" for k, v in m["facts"].items())
        mrows.append(f"""<tr><td><a href="sports/{e(m['sport'])}.html">{e(SPORT_NAME[m['sport']])}</a></td>
<td>{e(m['a'])} v {e(m['b'])}<br><span class="small">{e(m['comp'])} · {e(m['round'])}</span></td>
<td>{fmt_start(m['start_utc'], m['start_label'])}</td><td>{e(m['venue'] or '—')}</td>
<td class="small">{e(fact_str)}</td>
<td class="small">{e(m['injury_note'])}</td>
<td><a href="{e(src['url'])}" rel="noopener">{e(src['publisher'])}</a></td></tr>""")
    matches_body = f"""<section class="hero"><p class="eyebrow">Fixtures</p>
<h1>The {len(MATCHES)} fixtures behind the card</h1>
<p class="lede">Only fixtures with an official read are here. Fields we could not read are blank and say so;
no start time, venue or statistic has been inferred.</p></section>
<table><thead><tr><th>Sport</th><th>Match</th><th>Start</th><th>Venue</th><th>Official facts read</th>
<th>Injuries</th><th>Source</th></tr></thead><tbody>{''.join(mrows)}</tbody></table>"""
    write_page("matches.html", "Matches", matches_body, "matches.html")

    # ---------------- markets ----------------
    mk_rows = []
    for c in cards:
        families = MARKETS_BY_SPORT.get(c["sport"], MARKET_FAMILIES)
        for name, status, why in families:
            price = ""
            if status == "Priced" and name.startswith("Match winner"):
                price = f"{fmt_am(c['fair_american'])} ({fmt_pct(c['prob'])})"
            elif status == "Priced" and c.get("derivatives"):
                d = c["derivatives"]
                if name.startswith("Puck line"):
                    price = (f"home −1.5 {fmt_am(american_from_prob(d['home_puck_line']))} / "
                             f"away −1.5 {fmt_am(american_from_prob(d['away_puck_line']))}")
                elif name.startswith("Match total"):
                    price = (f"line {d['total_line']} · over {fmt_am(american_from_prob(d['over']))} / "
                             f"under {fmt_am(american_from_prob(d['under']))}")
            mk_rows.append(f"""<tr><td><a href="sports/{e(c['sport'])}.html">{e(c['sport_name'])}</a></td>
<td>{e(c['match'])}</td><td>{e(name)}</td>
<td><span class="badge {'ok' if status == 'Priced' else 'gap'}">{e(status.lower())}</span></td>
<td class="num">{e(price) or '—'}</td><td class="small">{e(why)}</td></tr>""")
    markets_body = f"""<section class="hero"><p class="eyebrow">Market coverage</p>
<h1>Every market family we looked at — priced or withheld, with the reason</h1>
<p class="lede">Handicaps, totals and derivative markets were investigated for all {len(cards)} selections.
Where a family could not be originated, the missing input is named instead of a number being produced.</p></section>
<div class="note"><strong>What is actually priced:</strong> match winner on all {len(cards)} selections;
hockey puck lines and totals on the five NHL games (derived from official goals for/against);
{sum(1 for c in cards if c.get('derivatives'))} of {len(cards)} selections carry more than one market.</div>
<table><thead><tr><th>Sport</th><th>Match</th><th>Market family</th><th>Status</th><th class="num">Our price</th>
<th>Why</th></tr></thead><tbody>{''.join(mk_rows)}</tbody></table>"""
    write_page("markets.html", "Markets", markets_body, "markets.html")

    # ---------------- sources ----------------
    srows = "".join(f"""<tr><td class="mono">{e(s['id'])}</td><td>{e(s['publisher'])}</td>
<td><span class="badge {'ok' if s['official'] else 'gap'}">{'official' if s['official'] else 'discovery only'}</span></td>
<td><a href="{e(s['url'])}" rel="noopener">{e(s['url'])}</a></td><td class="small">{e(s['observed'])}</td>
<td class="small">{e(s['scope'])}</td></tr>""" for s in SOURCES)
    sources_body = f"""<section class="hero"><p class="eyebrow">Evidence register</p>
<h1>{len(SOURCES)} sources, {sum(1 for s in SOURCES if s['official'])} of them official</h1>
<p class="lede">Anything marked “discovery only” is an OLBG page used solely to learn which fixtures and
markets exist. It is never the source of a record, a time or a statistic. The official sources are the ones
linked in every price row.</p></section>
<table><thead><tr><th>ID</th><th>Publisher</th><th>Type</th><th>URL</th><th>Read at (UTC)</th><th>What was taken from it</th></tr>
</thead><tbody>{srows}</tbody></table>
<div class="warn"><strong>Dead ends this session.</strong> These were attempted and could not be read, so
they supply nothing: pdc.tv (consent wall), ehfcl.eurohandball.com and eurohandball.com (404),
lnr.fr (404), premrugby.com (JavaScript shell, no fixture rows), legavolley.it (landing page only),
pcb.com.pk fixture routes (site 404 page). They are listed on
<a href="flagged.html">Flagged for review</a> as F-07.</div>"""
    write_page("sources.html", "Sources", sources_body, "sources.html")

    # ---------------- flagged ----------------
    frows = "".join(f"""<tr><td class="mono">{e(f['id'])}</td>
<td><span class="badge {'gap' if f['severity'] == 'high' else 'lo' if f['severity'] == 'medium' else 'md'}">{e(f['severity'])}</span></td>
<td>{e(f['sport'])}</td><td><strong>{e(f['title'])}</strong><br><span class="small">{e(f['detail'])}</span></td>
<td><a href="{e(f['link'])}" rel="noopener">{e(f['link_label'])}</a></td></tr>""" for f in FLAGS)
    flagged_body = f"""<section class="hero"><p class="eyebrow">Flagged for review</p>
<h1>{len(FLAGS)} irregularities, published rather than buried</h1>
<p class="lede">These do not block publication, but each one changes how a number on this site should be
read. Every item links to the page that shows it.</p></section>
<table><thead><tr><th>ID</th><th>Severity</th><th>Sport</th><th>What is wrong</th><th>Where to look</th></tr>
</thead><tbody>{frows}</tbody></table>"""
    write_page("flagged.html", "Flagged for review", flagged_body, "flagged.html")

    # ---------------- repo audit ----------------
    arows = "".join(f"""<tr><td class="mono">{e(a['id'])}</td><td>{e(a['area'])}</td><td>{e(a['check'])}</td>
<td class="small">{e(a['result'])}</td>
<td><span class="badge {'ok' if a['verdict'] == 'pass' else 'gap'}">{e(a['verdict'])}</span></td>
<td class="small">{e(a['note'])}</td></tr>""" for a in AUDIT)
    audit_body = f"""<section class="hero"><p class="eyebrow">Repository audit</p>
<h1>{len(AUDIT)} mechanical checks run line by line against this checkout</h1>
<p class="lede">Each check was executed in this session and the observed result is recorded verbatim.
Checks that pass are shown with their numbers; checks that fail are flagged for review instead of being
quietly fixed inside another session's scope.</p></section>
<table><thead><tr><th>ID</th><th>Area</th><th>Check</th><th>Observed result</th><th>Verdict</th><th>Note</th></tr>
</thead><tbody>{arows}</tbody></table>
<div class="note"><strong>What this audit does not claim.</strong> It does not re-verify the 126 priced rows
in <span class="mono">data/lines.json</span> or the 30 canonical predictions. Those belong to earlier desks and
would need a fresh official read per row; A-03 records that limit explicitly.</div>"""
    write_page("repo-audit.html", "Repo audit", audit_body, "repo-audit.html")

    # ---------------- methodology ----------------
    method_body = f"""<section class="hero"><p class="eyebrow">Method</p>
<h1>How every number was produced</h1>
<p class="lede">The formulas were fixed before any match was priced. No probability was tuned to reach a
confidence tier, and no tier was adjusted to reach a quota.</p></section>
<div class="card"><h3>1. Probability</h3><ul class="clean">
<li><strong>Basketball</strong> — each record is shrunk toward .500 by six pseudo-games
(<span class="mono">(w+3)/(w+l+6)</span>), combined with log5, then the home side's odds are multiplied by 1.35.</li>
<li><strong>Ice hockey</strong> — points percentage, shrunk by <span class="mono">(pts+3)/(2·gp+6)</span>,
log5, home odds ×1.20.</li>
<li><strong>Baseball</strong> — full-season win rate (162 games needs no shrinkage), log5, home odds ×1.12.</li>
<li><strong>Gaelic football</strong> — three-game group record shrunk by four pseudo-games, log5, no home edge
(the final is at a neutral county ground).</li>
<li><strong>Tennis</strong> — a seed-anchored prior of 0.64 for the top seed against an unseeded player,
capped at low confidence because no ranking points or head-to-head were readable.</li></ul></div>
<div class="card"><h3>2. Price</h3><p>Fair decimal is <span class="mono">1/p</span> with no margin.
American is derived from the rounded decimal. The fair price is our own number: it says what we think the
selection is worth, not what any bookmaker will lay.</p></div>
<div class="card"><h3>3. Derivative markets</h3><p>Hockey goals are Poisson with
<span class="mono">λ = (own goals for/game + opponent goals against/game)/2</span>. The puck line is
<span class="mono">P(margin ≥ 2)</span>; the total is the sum of the two λ, published as the next half-goal
line above it. Basketball spreads, baseball run lines and Gaelic handicaps are withheld because the
scoring-rate inputs they need were not readable — see <a href="markets.html">Markets</a>.</p></div>
<div class="card"><h3>4. Confidence gate</h3><ul class="clean">
<li><strong>High</strong> — p &gt; 70% <em>and</em> fair American inside −250…+10000 <em>and</em> both sides rest
on read inputs.</li>
<li><strong>Medium</strong> — 60–70%, or &gt;70% but priced shorter than −250 (the band rule excludes it).</li>
<li><strong>Low</strong> — below 60%, or a sport with incomplete inputs (tennis today).</li></ul>
<p class="small">Because −250 is 71.43%, the High tier can only contain selections between 70.00% and
71.43%. That is a property of the brief's own two rules, not of the data, and it is why the tier is empty today.</p></div>
<div class="card"><h3>5. What we refuse to do</h3><ul class="clean">
<li>Fill an unread field with a plausible value.</li>
<li>Quote a bookmaker price we did not see.</li>
<li>Write a prediction for a match whose official facts we could not read.</li>
<li>Treat an OLBG listing as fixture evidence.</li></ul></div>"""
    write_page("methodology.html", "Method", method_body, "methodology.html")

    # ---------------- sport pages ----------------
    (OUT / "sports").mkdir(parents=True, exist_ok=True)
    for slug, name, comp in SPORTS:
        sport_cards = by_sport.get(slug, [])
        gap = gap_by_sport.get(name)
        if sport_cards:
            rows_html = picks_table(sport_cards, prefix="../")
            head_html = f"""<div class="okay"><strong>{len(sport_cards)} priced selection(s).</strong>
Every row carries the official source it rests on.</div>{rows_html}
<h3>Full cases</h3>""" + "".join(
                f'<div class="pred"><strong>{e(c["selection"])}</strong> ({e(c["match"])}): {e(c["prose"])}</div>'
                for c in sport_cards)
            status = f'<span class="badge ok">priced</span>'
        else:
            head_html = f"""<div class="danger"><strong>No line originated for {e(name)}.</strong>
<p>{e(gap["blocked"] if gap else "No official fixture or form source was readable.")}</p>
<p class="small">Blocking source: <a href="{e(gap['source'] if gap else '#')}" rel="noopener">
{e(gap['source'] if gap else '')}</a></p></div>
<p>This sport is published as a gap because a price without a read fixture and a read form line would be
invented. The five-per-sport target is not reached here, and that is recorded on
<a href="../flagged.html">Flagged for review</a>.</p>"""
            status = '<span class="badge gap">no line</span>'
        body = f"""<section class="hero"><p class="eyebrow">Sport · {e(name)}</p>
<h1>{e(name)}</h1><p class="lede">{status} · {e(comp)} ·
{len(sport_cards)} selection(s) · {len([m for m in MATCHES if m['sport'] == slug])} fixture(s) read</p></section>
{head_html}
<p class="small"><a href="../picks.html">← All picks</a> · <a href="../index.html">Summary</a></p>"""
        write_page(f"sports/{slug}.html", name, body, f"sports/{slug}.html", depth=1)

    # ---------------- reports ----------------
    (ROOT / "reports").mkdir(exist_ok=True)
    md = [f"# Session 580f43c9 — 24/25 October 2026 desk",
          "",
          f"Evidence frozen: **{OBSERVED}**. Picks: **{len(cards)}** across **{len(by_sport)}** sports "
          f"({counts['high']} high / {counts['medium']} medium / {counts['low']} low).",
          "", "## Picks", "", "| Sport | Match | Pick | Market | Confidence | Fair | Start | Source |",
          "|---|---|---|---|---|---|---|---|"]
    for c in cards:
        md.append(f"| {c['sport_name']} | {c['match']} | **{c['selection']}** | {c['market']} | "
                  f"{c['confidence']} | {fmt_am(c['fair_american'])} ({fmt_pct(c['prob'])}) | "
                  f"{fmt_start(c['start_utc'], c['start_label'])} | {c['source']['url']} |")
    md += ["", "## Gaps", ""]
    for g in GAPS:
        md.append(f"* **{g['sport']}** — {g['blocked']} Source: {g['source']}")
    md += ["", "## Flags", ""]
    for f in FLAGS:
        md.append(f"* **{f['id']}** ({f['severity']}) {f['title']} — {f['detail']} [{f['link_label']}]({f['link']})")
    md += ["", "## Repo audit", ""]
    for a in AUDIT:
        md.append(f"* **{a['id']}** {a['area']}: {a['check']} → {a['result']} ({a['verdict']}) — {a['note']}")
    (ROOT / "reports" / "SESSION_580F43C9.md").write_text("\n".join(md) + "\n")

    print(f"built {len(cards)} picks, {counts}, {len(GAPS)} gaps, {len(FLAGS)} flags")


def slug_of(name):
    for slug, n, _ in SPORTS:
        if n == name:
            return slug
    return name.lower().replace(" ", "-")


def write_page(rel, title, body, current, depth=0):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page(title, body, current, depth))
    return path


if __name__ == "__main__":
    build()
