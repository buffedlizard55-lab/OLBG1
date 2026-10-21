#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the static OLBG-reverse dashboard: index.html, sports/*.html,
flagged.html, methodology.html, plus data/picks.json. Session 2360a617."""
import json, glob, os, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = os.path.join(ROOT, "2360a617")   # this session's desk (main-root namespace convention)
sys.path.insert(0, os.path.join(ROOT, "site"))
from picks_data import PICKS

SPORT_META = {
    "tennis": ("Tennis", "ATP 250s (Almaty, Lyon, Brussels) + WTA (Ningbo 500, Osaka 250) — singles, R1/R2/R16"),
    "basketball": ("Basketball", "NBA opening week + EuroLeague R7 + EuroCup/BCL/KBL"),
    "handball": ("Handball", "EHF Champions League group phase + Nordic domestic leagues"),
    "darts": ("Darts", "PDC European Championship, Dortmund — Round 1 (best of 11), Oct 22-23"),
    "volleyball": ("Volleyball", "Poland PlusLiga, German Bundesliga, Italy Serie A1 (W), Nordic leagues"),
    "rugby_union": ("Rugby Union", "Top 14, United Rugby Championship, Pro D2 (inferred)"),
    "golf": ("Golf", "Genesis Championship, BMW Ladies, Bermuda + minor/senior tour outrights"),
    "cricket": ("Cricket", "UAE ODI Tri-Series, Pakistan ODI Tri-Series, IND in NZ T20Is, Ireland in Namibia, SA domestic T20"),
    "ice_hockey": ("Ice Hockey", "NHL + ICE Hockey League (Austria) + SHL (Sweden)"),
    "snooker": ("Snooker", "BetVictor Northern Ireland Open, Belfast — Round 2"),
    "greyhounds": ("Greyhounds", "GBGB daily races (UK morning card) — win-market community tips only"),
    "gaelic_football": ("Gaelic Football", "Cork/Galway/Waterford senior club championships"),
    "motor_racing": ("Motor Racing", "Formula 1 — United States GP (COTA) + Drivers' Championship outrights"),
    "baseball": ("Baseball", "MLB — 2026 World Series Game 1 (Rays @ Brewers)"),
    "rugby_league": ("Rugby League", "No match events listed — only 2027 outright futures"),
    "aussie_rules": ("Aussie Rules", "No events — 'No tips found' on OLBG"),
    "esports": ("eSports", "No events — 'No tips found' on OLBG"),
}
ZERO_NOTES = {
    "rugby_league": "OLBG's Rugby League tips page listed <b>no upcoming matches</b> on 2026-10-21 — only 2027 outright futures (State of Origin: NSW 9/12; Super League Grand Final: Leeds 1/3; NRL Grand Final: Penrith 1/1). Outrights are season-long markets, not matches, so nothing was reverse-engineered into the table.",
    "aussie_rules": "OLBG returned <b>'No tips found'</b> for Aussie Rules (AFL season concluded; next season unpriced). The page's 'recent winners' table stops in 2023 — flagged as stale site content.",
    "esports": "OLBG returned <b>'No tips found'</b> for eSports, while still advertising CS:GO/FIFA sub-pages (both retired titles) — flagged as stale site content. No matches to originate lines for.",
}
EXCLUDED = ["Football (soccer)", "Horse Racing", "American Football (NFL)", "Boxing", "Cycling", "MMA/UFC", "Hurling", "Specials"]

CSS = """
:root{--bg:#0f1420;--card:#1a2233;--ink:#e8ecf4;--mut:#9aa7bd;--acc:#4da3ff;--hi:#2ecc8f;--md:#f5b942;--lo:#8b98ad;--warn:#ff6b6b;--line:#2a3550}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1280px;margin:0 auto;padding:20px}
header{border-bottom:1px solid var(--line);padding:18px 0;margin-bottom:22px}
h1{font-size:1.5rem;margin:0 0 4px}h2{font-size:1.2rem;margin:26px 0 10px;color:var(--acc)}
.sub{color:var(--mut);font-size:.92rem}
nav.top{display:flex;gap:14px;flex-wrap:wrap;margin-top:10px;font-size:.95rem}
nav.top a{font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:block;color:var(--ink)}
.card:hover{border-color:var(--acc);text-decoration:none}
.card .n{font-size:1.6rem;font-weight:700;color:var(--acc)}
.card .t{font-weight:600;margin-bottom:2px}.card .d{color:var(--mut);font-size:.82rem}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:.88rem}
th,td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{background:#141b2b;color:var(--mut);font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}
tr:last-child td{border-bottom:none}
.badge{display:inline-block;padding:1px 9px;border-radius:20px;font-size:.75rem;font-weight:700}
.b-high{background:rgba(46,204,143,.15);color:var(--hi);border:1px solid var(--hi)}
.b-medium{background:rgba(245,185,66,.13);color:var(--md);border:1px solid var(--md)}
.b-low{background:rgba(139,152,173,.15);color:var(--lo);border:1px solid var(--lo)}
.flagpill{display:inline-block;padding:1px 8px;border-radius:20px;font-size:.72rem;font-weight:700;background:rgba(255,107,107,.12);color:var(--warn);border:1px solid var(--warn)}
.okpill{display:inline-block;padding:1px 8px;border-radius:20px;font-size:.72rem;font-weight:700;background:rgba(46,204,143,.12);color:var(--hi);border:1px solid var(--hi)}
details{margin:2px 0}summary{cursor:pointer;color:var(--acc);font-size:.82rem}
.pred{background:#10182a;border-left:3px solid var(--hi);padding:8px 10px;border-radius:6px;margin:6px 0;font-size:.86rem}
.note{background:#141b2b;border:1px solid var(--line);border-left:3px solid var(--md);padding:10px 14px;border-radius:8px;margin:14px 0;color:var(--ink);font-size:.9rem}
.small{color:var(--mut);font-size:.8rem}
.mono{font-variant-numeric:tabular-nums}
footer{margin-top:36px;border-top:1px solid var(--line);padding:16px 0;color:var(--mut);font-size:.8rem}
.srcs{font-size:.78rem;line-height:1.7}
"""

def esc(s):
    return html.escape(str(s)) if s is not None else ""

def load_raw():
    sports = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "raw", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        sports[d["sport"]] = d
    return sports

def eid_of(url):
    return url.split("event_id=")[1] if "event_id=" in url else url

def slug_of(sport):
    return {"Rugby Union": "rugby_union", "Rugby League": "rugby_league", "Ice Hockey": "ice_hockey",
            "Motor Racing": "motor_racing", "Aussie Rules": "aussie_rules", "eSports": "esports",
            "Gaelic Football": "gaelic_football"}.get(sport, sport.lower().replace(" ", "_"))

def confidence_badge(c):
    return f'<span class="badge b-{c}">{c}</span>'

def srcs_html(p):
    out = []
    if p.get("srcs"):
        for label, url in p["srcs"]:
            out.append(f'<a href="{esc(url)}" rel="noopener">{esc(label)}</a>')
    if out:
        return '<div class="srcs">' + "<br>".join(out) + '</div>'
    return '<span class="flagpill">UNVERIFIED</span><div class="srcs small">No independent source captured — OLBG listing only.</div>'

def header(active, prefix=""):
    navlinks = [("", "Home"), ("flagged.html", "Flagged for Review"), ("methodology.html", "Methodology & Sources")]
    nav = ""
    for href, label in navlinks:
        cls = ' style="color:var(--ink)"' if href == active else ""
        nav += f'<a href="{prefix}{href}"{cls}>{label}</a> '
    return f"""<header><div class="wrap">
<h1>OLBG Reverse-Engineered Lines &amp; Picks</h1>
<div class="sub">152 events across 17 covered sports — collected from OLBG.com on 21 Oct 2026, re-priced with our own originated lines, verified against official sources. Times are US Eastern (ET) as displayed on OLBG.</div>
<nav class="top">{nav}<a href="https://github.com/buffedlizard55-lab/OLBG1" rel="noopener">GitHub repo</a></nav>
</div></header>"""

def footer():
    return """<footer><div class="wrap">Built by session 2360a617 · Data snapshot 2026-10-21 05:25–06:05 UTC · For research/entertainment only — not betting advice. Unverified rows are flagged, never inferred.</div></footer>"""

def match_row(sport_data, e, p):
    ev, comp, when, mkt, tip, odds, pct, url = e
    comp_disp = comp if comp else (p.get("tour", "") or "")
    olbg_cons = f'{esc(tip)} <b>{esc(odds)}</b> <span class="small">({pct}% of tips, top mkt: {esc(mkt)})</span>'
    analysis = ""
    if p.get("pred"):
        analysis += f'<div class="pred"><b>Prediction:</b> {esc(p["pred"])}</div>'
    analysis += f'<div class="small"><b>Basis:</b> {esc(p.get("basis",""))}</div>'
    if p.get("flag"):
        analysis += f'<div class="small"><span class="flagpill">FLAG</span> {esc(p["flag"])}</div>'
    ver = '<span class="okpill">VERIFIED</span>' if p.get("srcs") else '<span class="flagpill">UNVERIFIED</span>'
    return f"""<tr>
<td><b>{esc(ev)}</b><br><span class="small mono">{esc(when)} (ET)</span><br><span class="small">{esc(comp_disp)}</span></td>
<td>{olbg_cons}</td>
<td class="small">{esc(p["mk"])}</td>
<td><b>{esc(p["pick"])}</b></td>
<td>{confidence_badge(p["conf"])}</td>
<td>{ver}</td>
<td><details><summary>Analysis</summary>{analysis}</details></td>
<td class="srcs"><a href="{esc(url)}" rel="noopener">OLBG event</a>{("<br>" + "<br>".join(f'<a href="{esc(u)}" rel="noopener">{esc(l)}</a>' for l, u in p["srcs"])) if p.get("srcs") else ""}</td>
</tr>"""

def build():
    sports = load_raw()
    os.makedirs(os.path.join(NS, "sports"), exist_ok=True)
    order = sorted(sports.values(), key=lambda d: (-len(d["events"]), d["sport"]))
    total = sum(len(d["events"]) for d in sports.values())
    hi = sum(1 for p in PICKS.values() if p["conf"] == "high")
    med = sum(1 for p in PICKS.values() if p["conf"] == "medium")
    lo = sum(1 for p in PICKS.values() if p["conf"] == "low")
    nflag = sum(1 for p in PICKS.values() if p.get("flag") or not p.get("srcs"))

    # ---------- index ----------
    cards = ""
    for d in order:
        slug = slug_of(d["sport"])
        meta = SPORT_META.get(slug, (d["sport"], ""))
        n = len(d["events"])
        cards += f'<a class="card" href="sports/{slug}.html"><div class="t">{esc(meta[0])}</div><div class="n">{n}</div><div class="d">{esc(meta[1]) if n else esc(ZERO_NOTES.get(slug, "no events")[:90] + "…")}</div></a>'
    hi_picks = [p for p in PICKS.values() if p["conf"] == "high"]
    hi_html = "".join(
        f'<tr><td><b>{esc(p.get("tour","").split("—")[0])}</b></td><td>{esc(p["pick"])}</td><td class="small">{esc(p["pred"][:150])}…</td></tr>'
        for p in hi_picks)
    idx = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OLBG Reverse-Engineered — Lines &amp; Picks Dashboard (21 Oct 2026)</title>
<style>{CSS}</style></head><body>
{header("")}
<div class="wrap">
<div class="cards">
<div class="card"><div class="t">Events collected</div><div class="n">{total}</div><div class="d">17 covered sports · snapshot 2026-10-21</div></div>
<div class="card"><div class="t">High confidence</div><div class="n" style="color:var(--hi)">{hi}</div><div class="d">each with a ≥30-word verified prediction</div></div>
<div class="card"><div class="t">Medium confidence</div><div class="n" style="color:var(--md)">{med}</div><div class="d">partially verified context</div></div>
<div class="card"><div class="t">Low confidence</div><div class="n" style="color:var(--lo)">{lo}</div><div class="d">consensus/model only</div></div>
<div class="card"><div class="t">Flagged items</div><div class="n" style="color:var(--warn)">{nflag}</div><div class="d"><a href="flagged.html">review list →</a></div></div>
</div>
<h2>Sports covered</h2>
<div class="cards">{cards}</div>
<h2>High-confidence picks (with predictions)</h2>
<table><tr><th>Sport event</th><th>Our pick</th><th>Prediction (excerpt)</th></tr>{hi_html}</table>
<div class="note"><b>Scope:</b> excluded per brief — {", ".join(EXCLUDED)}. Every row links to its OLBG source event page plus any independent sources consulted; rows we could not verify carry an <span class="flagpill">UNVERIFIED</span> badge and appear on the <a href="flagged.html">Flagged for Review</a> page rather than being filled with guesses. See <a href="methodology.html">Methodology</a>.</div>
</div>{footer()}</body></html>"""
    open(os.path.join(NS, "index.html"), "w", encoding="utf-8").write(idx)

    # ---------- sport pages ----------
    for d in order:
        slug = slug_of(d["sport"])
        meta = SPORT_META.get(slug, (d["sport"], ""))
        rows = ""
        for e in d["events"]:
            p = PICKS.get(eid_of(e[-1]))
            if p:
                rows += match_row(d, e, p)
        body = ""
        if d["events"]:
            body = f"""<table><tr><th>Match / Event</th><th>OLBG community tip</th><th>Our originated line</th><th>Our pick</th><th>Confidence</th><th>Verification</th><th>Analysis</th><th>Sources</th></tr>{rows}</table>"""
        else:
            body = f'<div class="note"><b>No match events on this sport today.</b> {ZERO_NOTES.get(slug, "")}</div>'
        extra = ""
        if d.get("tz_note"):
            extra += f'<div class="note small"><b>Timezone note:</b> {esc(d["tz_note"])}</div>'
        page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(meta[0])} — Lines &amp; Picks (OLBG reverse-engineered)</title>
<style>{CSS}</style></head><body>
{header("", prefix="../")}
<div class="wrap">
<h1>{esc(meta[0])} <span class="small">({len(d["events"])} events)</span></h1>
<div class="sub">{esc(meta[1])} — OLBG page: <a href="{esc(d.get("olbg_page",""))}" rel="noopener">{esc(d.get("olbg_page",""))}</a> · fetched {esc(d.get("fetched_utc",""))} · displayed times ET</div>
{extra}
{body}
</div>{footer()}</body></html>"""
        open(os.path.join(NS, "sports", slug + ".html"), "w", encoding="utf-8").write(page)

    # ---------- flagged ----------
    frows = ""
    zero_html = ""
    for d in order:
        slug = slug_of(d["sport"])
        if not d["events"]:
            zero_html += f'<div class="note"><b>{esc(SPORT_META.get(slug,(d["sport"],""))[0])}:</b> {ZERO_NOTES.get(slug,"")}</div>'
        for e in d["events"]:
            p = PICKS.get(eid_of(e[-1]))
            if not p:
                continue
            issues = []
            if p.get("flag"):
                issues.append(esc(p["flag"]))
            if not p.get("srcs"):
                issues.append("No independent source captured — listing/pick rests on OLBG only.")
            if not issues:
                continue
            links = f'<a href="{esc(e[-1])}" rel="noopener">OLBG</a>'
            for l, u in p.get("srcs", []):
                links += f' · <a href="{esc(u)}" rel="noopener">{esc(l.split("—")[0].strip()[:40])}</a>'
            frows += f'<tr><td>{esc(SPORT_META.get(slug,(d["sport"],""))[0])}</td><td><b>{esc(e[0])}</b><br><span class="small mono">{esc(e[2])}</span></td><td class="small">{"<br>".join(issues)}</td><td class="srcs">{links}</td></tr>'
    nflagrows = frows.count("<tr>")
    flagged = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Flagged for Review — OLBG reverse-engineered</title>
<style>{CSS}</style></head><body>
{header("flagged.html")}
<div class="wrap">
<h1>Flagged for Review</h1>
<div class="sub">{nflagrows} items: irregularities, consensus divergences, data-quality issues and every row lacking independent verification. Per the brief these do not block publication — they are surfaced honestly instead of inferred away.</div>
<h2>Sports with no match events (plus stale-content findings)</h2>
{zero_html}
<div class="note"><b>Greyhounds data-quality note:</b> OLBG's greyhound pages expose only the single most-tipped dog per race — full fields, trap draws and per-runner odds were not capturable, so no numeric win price could be originated for any of the six races. Race-time mapping (UK BST titles vs ET display, −5h) was verified.</div>
<div class="note"><b>Time discrepancies:</b> OLBG displayed tip-offs of 19:10 ET for NBA games (NBA.com says 7:00pm) and 19:37 ET for NHL games (official puck drop 7:30pm). OLBG's clocks run ~7-10 minutes hot — logged, not corrected silently.</div>
<h2>All flagged rows</h2>
<table><tr><th>Sport</th><th>Event</th><th>Issue(s)</th><th>Links for manual review</th></tr>{frows}</table>
</div>{footer()}</body></html>"""
    open(os.path.join(NS, "flagged.html"), "w", encoding="utf-8").write(flagged)

    # ---------- methodology ----------
    meth = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Methodology &amp; Sources — OLBG reverse-engineered</title>
<style>{CSS}</style></head><body>
{header("methodology.html")}
<div class="wrap">
<h1>Methodology, verification &amp; source log</h1>
<h2>1. Collection</h2>
<p>All match lists were scraped from OLBG.com's public betting-tips pages on <b>21 Oct 2026, 05:25–06:05 UTC</b> (raw snapshots committed under <code>data/raw/</code>). Covered sports (17): Tennis, Basketball, Golf, Cricket, Snooker, Darts, Rugby Union, Rugby League, Baseball, Ice Hockey, Motor Racing, Handball, Volleyball, Aussie Rules, eSports, Gaelic Football, Greyhounds. Excluded per brief: {", ".join(EXCLUDED)}. Rugby League, Aussie Rules and eSports had zero match events (documented on <a href="flagged.html">Flagged</a>).</p>
<h2>2. Timezone determination</h2>
<p>OLBG displayed times are <b>US Eastern</b>, not UK: the greyhound race titled “11:14 Kinsley” (UK) displayed as “Today 06:14” — exactly BST−5h. Corroborated by Littler–O'Connor (15:15 ET = 21:15 Dortmund local, per Sky/Sportingnews) and India–NZ T20I (03:00 ET = 07:00 GMT = 20:00 NZDT, per BCCI/ICC). All tables show ET as displayed.</p>
<h2>3. Originating our lines</h2>
<p>For each event we investigated the market landscape OLBG exposes (win/moneyline, handicaps &amp; point/puck/game/leg spreads, totals, set/first-set/frame markets, outrights) and originated our own line from: (a) verified records/standings/rankings, (b) verified recent results, (c) OLBG's own published historical base rates (e.g. Top 14 home win 74.4%, EHF CL draw ~9.8%, volleyball favourites 77.9–84.4%), and (d) consensus odds as a market prior. Where no verified data existed, numeric lines are <b>left blank or explicitly labelled “model estimate”</b> — never presented as fact.</p>
<h2>4. Confidence policy</h2>
<p><b>High</b> ({hi} picks): verified official-grade evidence (league standings, official rankings, governing-body schedules) pointing one way; each carries a unique ≥30-word prediction. <b>Medium</b> ({med}): partial verification (event + one or two verified facts). <b>Low</b> ({lo}): consensus/model only — honest uncertainty, often deliberately diverging from OLBG's crowd tip with a stated reason.</p>
<h2>5. Verification &amp; irregularities</h2>
<p>Every row links its OLBG source event page. Independent sources consulted (all accessed 21 Oct 2026): official bodies — <b>MLB.com, NBA.com, Formula1.com, LPGA.com, BCCI.tv, ICC-cricket.com, WTA (draws + rankings PDFs), ATP Tour draw pages, eurohandball.com/EHFCL, URC stats site</b>; reference/data — ESPN, BBC Sport, Sky Sports, Wikipedia event pages, ESPNcricinfo, Hockey-Reference, Basketball-Reference, Sofascore, L'Equipe, all.rugby, Planet Rugby, Racing Post, AP, Seoul Economic Daily/SBS, Kalshi/lineups (model cross-checks), Tennis Tonic/Britwatch (draw results). Where values could not be confirmed the cells say so and the row is flagged. Notable irregularities logged on the <a href="flagged.html">Flagged page</a>: OLBG consensus backing Verstappen for the F1 title despite Antonelli's verified 102-point lead; handball “Tie” tips at 43–80% against a ~10% base rate; a wildcard backed for first set at 75% vs a top-100 seed (Almaty); stale CS:GO/FIFA and 2023-era AFL content; minor tip-off clock offsets; a competition label (Dinamo Bucuresti v Skanderborg) that doesn't match the verified EHF CL field.</p>
<h2>6. Machine-readable data</h2>
<p>Full pick set: <code>data/picks.json</code> (regenerated by <code>site/build.py</code>). Raw OLBG captures: <code>data/raw/*.json</code>. Coordination log: <code>COORDINATION.md</code>.</p>
<div class="note"><b>Disclaimer:</b> research/entertainment only; not betting advice. Odds shown are fractional as listed on OLBG at capture time and move constantly.</div>
</div>{footer()}</body></html>"""
    open(os.path.join(NS, "methodology.html"), "w", encoding="utf-8").write(meth)

    # ---------- data/picks.json ----------
    out = {}
    for d in sports.values():
        rows = []
        for e in d["events"]:
            p = PICKS.get(eid_of(e[-1]))
            rows.append(dict(event=e[0], competition=e[1], when_et=e[2], olbg_top_market=e[3],
                             olbg_top_tip=e[4], olbg_top_odds=e[5], olbg_tip_pct=e[6], olbg_url=e[7],
                             our_line=p["mk"], our_pick=p["pick"], confidence=p["conf"],
                             verified=bool(p.get("srcs")), basis=p.get("basis"),
                             prediction=p.get("pred"), sources=p.get("srcs", []),
                             flags=[x for x in [p.get("flag")] if x] or ([] if p.get("srcs") else ["unverified-olbg-only"]),
                             tournament=p.get("tour")))
        out[d["sport"]] = rows
    json.dump(out, open(os.path.join(ROOT, "data", "picks.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"Built: index.html, flagged.html, methodology.html, {len(order)} sport pages, data/picks.json")
    print(f"Events: {total} | high {hi} / med {med} / low {lo} | flagged rows: {nflagrows + len([d for d in order if not d['events']])}")

if __name__ == "__main__":
    build()
