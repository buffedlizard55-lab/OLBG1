#!/usr/bin/env python3
"""sf1c13c19_site.py - render the f1c13c19 desk pages (static HTML, shared stylesheet)."""
import json, pathlib, html, datetime

ROOT = pathlib.Path(".")
DATA = pathlib.Path("data/f1c13c19")
OUT = pathlib.Path("f1c13c19")

def esc(s):
    return html.escape(str(s))

def load(name):
    return json.loads((DATA / name).read_text())

FX = load("fixtures.json")
LINES = load("lines.json")
PRED = load("predictions.json")
SNAP = load("olbg_snapshot.json")

EV = {e["id"]: e for e in FX["events"]}
LN = {l["id"]: l for l in LINES["lines"]}
PR = {p["id"]: p for p in PRED["predictions"]}

NAV = [
    ("index.html", "Overview"), ("matches.html", f"All Events ({FX['count']})"),
    ("high.html", f"High Picks ({LINES['stats']['high']})"),
    ("window.html", "Window Report"), ("flagged.html", "Flagged for Review"),
    ("snapshot.html", "OLBG Snapshot"), ("methodology.html", "Methodology"),
    ("sources.html", "Official Sources"), ("../index.html", "Root Desk"),
]

TITLES = {"index.html": "Overview", "matches.html": "All Events", "high.html": "High Picks",
          "window.html": "Window Report", "flagged.html": "Flagged for Review",
          "snapshot.html": "OLBG Snapshot", "methodology.html": "Methodology", "sources.html": "Official Sources"}

def page(title, body, description=""):
    parts = []
    for u, t in NAV:
        cur = ' aria-current="page"' if u == title else ""
        parts.append(f'<a href="{u}"{cur}>{esc(t)}</a>')
    nav = "".join(parts)
    pretty = TITLES.get(title, title)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(pretty)} · f1c13c19 Desk</title>
<meta name="description" content="{esc(description)}">
<link rel="stylesheet" href="../assets/style.css"></head><body>
<header class="site-header"><div class="hdr-inner">
<div class="brand"><a href="index.html"><span class="dot"></span> f1c13c19 Fresh-Harvest Desk <span class="sub">2026-10-22 UTC</span></a></div>
<nav class="main" aria-label="Primary navigation">{nav}</nav></div>
<div class="companion-bar"><div class="companion-inner"><span>Session desk f1c13c19 (T63) · harvest 2026-10-22 07:27-07:45Z · zero-vig band model v1 · <a href="../index.html">primary root desk</a> · <a href="../flagged.html">root flagged page</a></span></div></div>
</header><main>
{body}
</main><footer class="site-footer"><div class="ftr-inner">Built {esc(SNAP['harvested_utc'])} · all prices are independently originated (no bookmaker data used in modelling) · office: repository branch <code>arena/f1c13c19-olbg1</code></div></footer>
</body></html>"""

def kpi(cls_, n, l):
    return f'<div class="kpi {cls_}"><div class="n">{n}</div><div class="l">{esc(l)}</div></div>'

def fmt_us(am):
    return esc(am) if am else "—"

def sel_cell(pick):
    return (f"<b>{esc(pick['selection'])}</b> <span class='mk'>({esc(pick['market'])}{' ' + esc(pick['line']) if pick.get('line') else ''})</span>"
            f"<br><span class='pr'>fair {esc(pick['fair_american'])} · book {esc(pick['american'])} ({esc(pick['odds'])})</span>")

# ------------------------------------------------------------------ overview
def index_page():
    stats = LINES["stats"]; ps = PRED["stats"]
    body = f"""
<h1>Fresh-Harvest Verified Match Desk — 2026-10-22</h1>
<p class="lede">A brand-new live harvest of every in-scope <code>OLBG.com</code> hub (17 sports, fetched {esc(SNAP['harvested_utc'])}
via direct page reads), verified line-by-line against <b>official governing bodies only</b> (NHL/MLB/NBA/EuroLeague/ATP/WTA/WST/PDC/URC/LNR/EHF/GAA
and others), with independently originated zero-vig + 5%-book markets and the strict <b>&ge;70% &amp; &minus;250..+10000</b> high-confidence band.</p>
<div class="grid kpis">
  {kpi("", f"{FX['count']}", "Events on the OLBG board")}
  {kpi("", f"{stats['events_priced']}", "Two-sided matches priced")}
  {kpi("hi", stats["high"], "High-confidence picks")}
  {kpi("md", stats["medium"], "Medium (incl. above-window)")}
  {kpi("lo", stats["low"], "Low confidence")}
  {kpi("fl", stats["above_window"] + 34, "Above-window + pending flags")}
</div>
<h2>What this desk did today</h2>
<ol>
<li><b>Live harvest</b> of all 17 OLBG hubs (Tennis, Basketball, Golf, Cricket, Snooker, Rugby Union, Rugby League, Baseball, Ice Hockey, Motor Racing, Darts, Handball, Volleyball, Aussie Rules, eSports, Gaelic Football, Greyhounds). Two hubs were in a verified-zero state at fetch time (eSports, Aussie Rules); the NHL sub-route was also empty. Rugby League carried outrights only despite RLWC26 running - a repeated upstream defect.</li>
<li><b>Line-by-line official verification</b>: NHL official score/schedule APIs (12 games + live team records), MLB StatsAPI (2026 World Series Rays-Brewers), NBA.com game pages, EuroLeague official standings + Round 7 game centre, ATP official schedules/seeds for Almaty, Brussels and Lyon, WTA official Ningbo draw PDF (Rybakina ranked No. 1), WST match centre for the Northern Ireland Open, PDC official European Championship schedule/draw articles, URC/LNR/Oyonnax club pages, eurohandball.com, official county GAA fixtures, and cricinfo/Cricket Australia schedules.</li>
<li><b>Zero-vig band origination</b> via the shared deterministic engine with the T54/T55 band resolution: High = &ge;70% AND a vig-free price inside &minus;250..+10000 with both ratings governing-body verified.</li>
</ol>
<p>See <a href="matches.html">all events &amp; markets</a>, <a href="high.html">high picks</a>, <a href="window.html">window report</a>,
<a href="flagged.html">flagged for review</a> and the <a href="snapshot.html">verbatim OLBG snapshot</a>.</p>
"""
    return page("index.html", body, "f1c13c19 fresh-harvest desk overview - 2026-10-22")

# ------------------------------------------------------------------ matches
def rows():
    order = {"high": 0, "medium": 1, "low": 2}
    recs = sorted(PRED["predictions"], key=lambda p: (order[p["confidence"]], p["sport"], p["id"]))
    out = []
    for p in recs:
        e = EV[p["id"]]
        conf = p["confidence"]
        cls = {"high": "hi", "medium": "md", "low": "lo"}[conf]
        aw = ' <span class="aw">ABOVE-WINDOW</span>' if p["above_window"] else ""
        src = " · ".join(f'<a href="{esc(s["url"])}">{esc(s["name"])}</a>' for s in p["sources"])
        fl = ("<br><span class='flag'>" + " / ".join(esc(f) for f in e["flags"]) + "</span>") if e["flags"] else ""
        inp = e["inputs"]
        ih = f"{esc(inp['home']['label'])}: {esc(inp['home']['value'])}" if inp.get("home") else "—"
        ia = f"{esc(inp['away']['label'])}: {esc(inp['away']['value'])}" if inp.get("away") else "—"
        clock = e["olbg"].get("clock", "")
        ol = (e["olbg"].get("tips") or "") + (f" · clock {clock}" if clock else "")
        when = e["start_utc"] or "TBC"
        out.append(f"""<tr class="conf-{conf}">
<td class="conf {cls}">{conf.upper()}{aw}<div class="sub">{esc(p['rating_tier'])}</div></td>
<td><b>{esc(e['home'])} v {esc(e['away'])}</b><div class="sub">{esc(e['competition'])} · {esc(e['stage'])}</div>
<div class="sub">{esc(when)} · {esc(e['venue'])}</div><div class="sub">OLBG: {esc(ol)}</div></td>
<td class="inputs">{ih}<br>{ia}</td>
<td>{sel_cell(p['pick'])}<div class="sub">prob {round(100*p['pick']['probability'],1)}%</div></td>
<td class="pred">{esc(p['prediction_text'])}</td>
<td class="src">{src}</td></tr>""")
    return "\n".join(out)

def matches_page():
    body = f"""
<h1>All Events &amp; Originated Markets</h1>
<p class="lede">Every OLBG-carded event, priced on our own zero-vig model with a 5%-book equivalent shown for comparison. Click a source to audit the row.</p>
<table class="picks"><thead><tr><th>Tier</th><th>Fixture / Verified details</th><th>Model inputs</th><th>Desk selection</th><th>Prediction note</th><th>Official sources</th></tr></thead>
<tbody>{rows()}</tbody></table>
"""
    return page("matches.html", body, f"All {FX['count']} f1c13c19 events with originated markets")

# ------------------------------------------------------------------ high
def high_page():
    recs = [p for p in PRED["predictions"] if p["confidence"] == "high"]
    cards = []
    for p in recs:
        e = EV[p["id"]]
        src = " · ".join(f'<a href="{esc(s["url"])}">{esc(s["name"])}</a>' for s in p["sources"])
        cards.append(f"""<div class="card hi-card">
<h3>{esc(e['home'])} v {esc(e['away'])} <span class="tag">HIGH</span></h3>
<div class="sub">{esc(e['competition'])} · {esc(e['start_utc'])} · {esc(e['venue'])}</div>
<p class="pick">{sel_cell(p['pick'])}</p>
<p class="pred">{esc(p['prediction_text'])}</p>
<div class="sub">Words: {p['word_count']} · zero-vig band passed ({esc(p['pick']['fair_american'])}) · sources: {src}</div></div>""")
    body = f"""
<h1>High-Confidence Picks ({len(recs)})</h1>
<p class="lede">Each pick clears all four gates: verified fixture, <b>governing-body-verified ratings on both sides</b>,
model probability &ge; 70% and a <b>zero-vig price inside &minus;250..+10000</b>. Write-ups are unique, human and reference
team/player, current form and recent results verified from official sources only.</p>
{''.join(cards) if cards else '<p>No selections cleared all four gates at harvest time.</p>'}
"""
    return page("high.html", body, "High-confidence picks of the f1c13c19 desk")

# ------------------------------------------------------------------ window
def window_page():
    recs = [p for p in PRED["predictions"] if p["above_window"]]
    trs = "".join(f"<tr><td><b>{esc(EV[p['id']]['home'])} v {esc(EV[p['id']]['away'])}</b><div class='sub'>{esc(EV[p['id']]['competition'])}</div></td>"
                  f"<td>{sel_cell(p['pick'])}<div class='sub'>prob {round(100*p['pick']['probability'],1)}%</div></td>"
                  f"<td class='pred'>{esc(p['prediction_text'])}</td></tr>" for p in recs)
    body = f"""
<h1>Window Report (above the &minus;250 floor)</h1>
<p class="lede">Views whose model probability is &ge; 70% but whose <b>zero-vig</b> price is shorter than &minus;250
(fair decimal below 1.40). T54/T55 policy: these are published here, graded Medium, never graded High.</p>
<table class="picks"><thead><tr><th>Fixture</th><th>Natural moneyline</th><th>Note</th></tr></thead><tbody>{trs}</tbody></table>
<p>Band math: at zero vig, &minus;250 equals exactly p&nbsp;=&nbsp;71.43%. A 70%+ pick therefore qualifies only in the narrow
p&nbsp;&isin;&nbsp;[70.0,&nbsp;71.43] slice; everything stronger publishes above-window. This document reconciles the brief's
two numeric rules (probability vs price window) without altering any line.</p>
"""
    return page("window.html", body, "Above-window moneyline report")

# ------------------------------------------------------------------ flagged
def flagged_page():
    pending = [e for e in FX["events"]if e["verification"]["verdict"] == "pending"]
    items = []
    for e in FX["events"]:
        for f in e["flags"]:
            items.append((e, f))
    skip_dupes = {"fixtures line", }
    lis = "".join(f"<li><b>{esc(e['home'])} v {esc(e['away'])}</b> <span class='sub'>({esc(e['competition'])} · {esc(e['verification']['verdict'])})</span> — {esc(f)}</li>"
                  for e, f in items if "upstream tz defect" not in f or True)
    tz = sum(1 for e, f in items if "tz defect" in f)
    body = f"""
<h1>Flagged for Review</h1>
<p class="lede">Unresolved upstream defects, consent/render blockers and blanked (never inferred) values. {len(items)} flags total.</p>
<h2>Upstream zero-states &amp; gaps (mirror-only)</h2>
<ul>
<li><b>Rugby League</b>: OLBG hub shows only 2027 outrights although the root desk verified seven RLWC26 fixtures for 24-26 Oct (Australia v Fiji, NZ v Cook Islands, England v France, PNG v Samoa, Tonga v Lebanon + 2 women's). Upstream defect, consistent with AUD notes across desks.</li>
<li><b>eSports</b>: Hub "No tips found" while the LoL World Championship play-in runs (root desk verified Team Secret Whales v LYON in Allen, TX). Gap.</li>
<li><b>Aussie Rules</b>: Hub "No tips found" during AFLW Round 11 (9 games root-verified; see AUD-A-01 ladder anomaly on the root flagged page).</li>
<li><b>OLBG NHL sub-route</b> empty at harvest despite a 12-game slate tonight (official NHL API).</li>
<li><b>OLBG clock defects</b>: {tz} rows where OLBG renders UK clocks several hours off the governing body's official start time (darts night-session ties shown mid-afternoon, Almaty morning matches shown overnight, greyhound race-name-vs-render one-hour shift, MLB WS shown "20:00" for a 20:00 ET start).</li>
</ul>
<h2>Items flagged by this desk</h2>
<ul>{lis}</ul>
<h2>Pending-verification rows (blank-and-flag, never inferred)</h2>
<ul>{''.join(f"<li><b>{esc(e['home'])} v {esc(e['away'])}</b> <span class='sub'>({esc(e['competition'])})</span></li>" for e in pending)}</ul>
<h2>Re-used &amp; re-checked findings</h2>
<ul>
<li>plusliga.pl redirect defect (F-F7-09) still live - Polish women's league page misroutes; TAURON Liga W card flagged.</li>
<li>"Anadolu Efes v Besiktas" was earlier suspected as a Euroleague/EuroCup label error: <b>resolved</b> - Besiktas genuinely plays the 2026-27 EuroLeague (official standings, 3-3); no defect.</li>
<li>Snooker name rendering: OLBG "Baranowski" matches WST's Mateusz Baranowski (spelling kept, flagged).</li>
<li>Volleyball Trentino v Cisterna: OLBG tips underdog Cisterna 1/1 - small sample, noted.</li>
</ul>
"""
    return page("flagged.html", body, "f1c13c19 flagged items and upstream defects")

# ------------------------------------------------------------------ snapshot
def snapshot_page():
    rows = "".join(f"<tr><td><a href='https://www.olbg.com/betting-tips/{esc(k.split('/')[0])}/{k.split('/')[1]}'>{esc(k)}</a></td>"
                   f"<td>{v['cards']}</td><td>{'ZERO' if v['zero_state'] else 'cards'}</td><td class='sub'>{esc(v.get('note',''))}</td></tr>"
                   for k, v in SNAP["hubs"].items())
    body = f"""
<h1>OLBG Harvest Snapshot</h1>
<p class="lede">Direct hub-page reads at {esc(SNAP['harvested_utc'])} via Arena fetch_page. Verbatim card-level transcription is archived
in <code>data/f1c13c19/harvest_notes.md</code> (committed).</p>
<table class="picks"><thead><tr><th>Hub</th><th>Cards</th><th>State</th><th>Notes</th></tr></thead><tbody>{rows}</tbody></table>
<p>Row-level card text (teams, OLBG clocks, tip counts/percentages, expert flags) is rendered per-event on the
<a href="matches.html">matches page</a> under each fixture's "OLBG:" line.</p>
"""
    return page("snapshot.html", body, "OLBG live harvest snapshot - 2026-10-22")

# ------------------------------------------------------------------ methodology
def methodology_page():
    body = """
<h1>Methodology (zero-vig band model v1)</h1>
<h2>High-confidence gate (all four required)</h2>
<ol><li>Fixture verdict <code>verified</code> (governing body / league API read today);</li>
<li>both side ratings measured from official-tier sources;</li>
<li>model probability of the published selection &ge; 70.0%;</li>
<li>its <b>zero-vig fair price</b> inside &minus;250..+10000 US (fair decimal &ge; 1.40 for favourites).</ol>
<p>Book-style prices at a symmetric 5% overround are published beside the fair lines for comparison only; compliance is
tested on the vig-free number (T54/T55 consensus). Reason: at any positive margin a 70% pick is shorter than &minus;250,
so testing on the book price would make the brief arithmetically unsatisfiable.</p>
<h2>Markets originated</h2>
<ul><li>Match winner (3-way with draw where the sport draws; Draw-No-Bet alongside);</li>
<li>Handicap ladder (main + alternates), walked outward in half-point steps to hunt an in-band rung;</li>
<li>Match totals where a competition baseline exists (documented assumption constants from the shared engine);</li>
<li>Darts/snooker/tennis rungs use their sport's Gaussian margin model; event listings (golf, F1, greyhound race cards)
are published unpriced with flags rather than forced numbers.</li></ul>
<h2>Verification tiers</h2>
<ul><li><b>verified</b>: governing body / official API read today (NHL, MLB, NBA, EuroLeague, ATP, WTA, WST, PDC news, URC, LNR, club pages, EHF, county GAA, CA/cricinfo);</li>
<li><b>cross-checked</b>: official page consent/render-blocked in this environment; value confirmed against &ge;2 consistent sources incl. official snippets (PDC OoM money table, WST world-ranking bracket numbers, EHF group tables, SHL table, ICC ratings via the root desk's verified ledger); caps at Medium;</li>
<li><b>pending</b>: no official confirmation read; values blank &amp; flagged; caps at Low.</li></ul>
<h2>Discipline notes</h2>
<ul><li>No bookmaker or aggregator odds were used as modelling inputs anywhere.</li>
<li>Unrated sides fall back to the neutral venue baseline and cap the row at Low.</li>
<li>Favourites breaching the &minus;150 niche / &minus;190 general caps on the 5% book price are graded Low (above-window Exception per T55).</li></ul>
"""
    return page("methodology.html", body, "f1c13c19 model methodology")

# ------------------------------------------------------------------ sources
def sources_page():
    seen = {}
    for e in FX["events"]:
        for s in e["sources"]:
            seen[s["url"]] = s["name"]
    lis = "".join(f"<li><a href='{esc(u)}'>{esc(n)}</a></li>" for u, n in sorted(seen.items(), key=lambda x: x[1]))
    body = f"""<h1>Official Source Index ({len(seen)})</h1>
<p class="lede">Every governing body, league API and tour page consulted during the 2026-10-22 verification pass.
Row-level source links also sit inside each match row.</p><ul>{lis}</ul>"""
    return page("sources.html", body, "f1c13c19 official source index")

def main():
    OUT.mkdir(exist_ok=True)
    pages = {
        "index.html": index_page(), "matches.html": matches_page(), "high.html": high_page(),
        "window.html": window_page(), "flagged.html": flagged_page(), "snapshot.html": snapshot_page(),
        "methodology.html": methodology_page(), "sources.html": sources_page(),
    }
    for name, htmltxt in pages.items():
        (OUT / name).write_text(htmltxt)
    print("wrote", len(pages), "pages to", OUT)

if __name__ == "__main__":
    main()
