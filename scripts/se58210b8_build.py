#!/usr/bin/env python3
"""T5821 desk site builder. Writes only inside e58210b8/ and data/e58210b8/."""
from __future__ import annotations

import html
import json
from pathlib import Path

import se58210b8_data as D
import se58210b8_model as M
from se58210b8_predictions import PREDICTIONS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "e58210b8"
DATA = ROOT / "data" / "e58210b8"
SOURCES = {s["id"]: s for s in D.SOURCES}
SNAPSHOT = D.HARVEST_UTC

CSS = """
:root{--bg:#0f1720;--panel:#16212c;--line:#26374a;--fg:#e8eef5;--mut:#9db0c4;--acc:#4cc38a;--warn:#f0b429;--bad:#ef6461}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
header{padding:22px 28px;border-bottom:1px solid var(--line);background:#111c26}
h1{margin:0 0 6px;font-size:23px}h2{margin:26px 0 10px;font-size:18px}h3{margin:18px 0 8px;font-size:15px}
p{margin:8px 0}a{color:#7fd3ff;text-decoration:none}a:hover{text-decoration:underline}
main{padding:22px 28px;max-width:1240px;margin:0 auto}
nav{display:flex;flex-wrap:wrap;gap:6px 14px;padding:10px 28px;background:#111c26;border-bottom:1px solid var(--line);font-size:14px}
.sub{color:var(--mut);font-size:13px;margin:0}
table{width:100%;border-collapse:collapse;margin:10px 0 4px;font-size:13.5px}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{background:#1b2836;font-weight:600;white-space:nowrap}
tbody tr:nth-child(even){background:#131e29}
.kpis{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 14px;min-width:132px}
.kpi b{display:block;font-size:21px}.kpi span{color:var(--mut);font-size:12px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin:12px 0}
.tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11.5px;border:1px solid var(--line)}
.high{background:#143c2b;color:#7fe0b0;border-color:#23684a}.medium{background:#3a2f12;color:#f5cf6b;border-color:#6b5620}
.low{background:#2a3340;color:#b9c8d8}.blank{background:#3a1f1f;color:#f0a3a1;border-color:#6b3030}
.warn{border-left:3px solid var(--warn)}.bad{border-left:3px solid var(--bad)}
code{background:#101a24;padding:1px 5px;border-radius:4px;font-size:12.5px}
footer{padding:18px 28px;color:var(--mut);font-size:12.5px;border-top:1px solid var(--line);margin-top:26px}
.small{font-size:12.5px;color:var(--mut)}
"""


def esc(x) -> str:
    return html.escape("" if x is None else str(x))


def ext(url: str, label: str | None = None) -> str:
    return f'<a href="{esc(url)}" rel="nofollow noopener" target="_blank">{esc(label or url)}</a>'


def src_links(ids) -> str:
    return " ".join(ext(SOURCES[i]["url"], SOURCES[i]["name"].split(",")[0]) for i in ids)


def page(title: str, heading: str, body: str, active: str = "", prefix: str = "") -> str:
    nav = [
        ("index.html", "Dashboard"), ("matches.html", "Matches"), ("markets.html", "Markets"),
        ("high-confidence.html", "High confidence"), ("predictions.html", "Predictions"),
        ("flagged.html", "Flagged for review"), ("methodology.html", "Methodology"),
        ("sources.html", "Sources"), ("analysis.html", "Repo &amp; OLBG review"),
    ]
    parts = []
    for href, label in nav:
        cur = ' aria-current="page"' if href == active else ""
        parts.append('<a href="%s%s"%s>%s</a>' % (prefix, href, cur, label))
    links = " ".join(parts)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><link rel="stylesheet" href="{prefix}assets/desk.css"></head>
<body><header><h1>{heading}</h1>
<p class="sub">OLBG1 · T5821 desk · session <code>e58210b8-olbg1</code> · evidence snapshot {esc(SNAPSHOT)} · not affiliated with OLBG · 18+ only, no staking advice</p></header>
<nav>{links}</nav><main>{body}</main>
<footer>Built from official publisher reads recorded at {esc(SNAPSHOT)}. Prices are originated estimates with no bookmaker margin and are not offers.
Unread values stay blank and are flagged on <a href="{prefix}flagged.html">Flagged for review</a>.</footer></body></html>
"""


def band_tag(b) -> str:
    if b.get("unpriced"):
        return '<span class="tag blank">unpriced</span>'
    if b.get("high_and_in_window"):
        return '<span class="tag high">high · in window</span>'
    if b.get("confidence") == "high":
        return '<span class="tag high">high · shorter than -250</span>'
    if b.get("confidence") == "medium":
        return '<span class="tag medium">medium · in window</span>'
    return '<span class="tag low">low</span>'


def pick_cell(b: dict) -> str:
    """Selection cell: dash when unpriced, otherwise pick, probability and fair American price."""
    if b.get("unpriced"):
        return "—"
    prob = "%.1f%%" % (b["pick_probability"] * 100)
    return "%s %s (%+d)" % (esc(b["pick"]), prob, b["pick_american"])


def sport_row(b: dict) -> str:
    cells = [b["date"], b["start_utc"], b["away"], b["home"], b["venue"]]
    out = "".join("<td>%s</td>" % esc(c) for c in cells)
    out += "<td>%s</td><td>%s</td><td>%s</td>" % (
        pick_cell(b), band_tag(b), src_links(b["source_ids"]))
    return "<tr>%s</tr>" % out


def build() -> None:
    doc = M.build()
    books = doc["books"]
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "lines.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    (OUT / "assets" / "desk.css").write_text(CSS, encoding="utf-8")
    (OUT / "sports").mkdir(parents=True, exist_ok=True)

    nhl = [b for b in books if b["sport"] == "ice_hockey"]
    mlb = [b for b in books if b["sport"] == "baseball"]
    high = sorted([b for b in books if b.get("confidence") == "high"], key=lambda x: -x["pick_probability"])
    medium = sorted([b for b in books if b.get("confidence") == "medium"], key=lambda x: -x["pick_probability"])
    priced = [b for b in books if not b.get("unpriced")]
    carolina = next(b for b in books if b["id"] == "nhl-2026020175")
    anaheim = next(b for b in books if b["id"] == "nhl-2026020168")
    slate = high + [anaheim, carolina]
    markets = sum(len(b["markets"]) for b in books)
    outcomes = sum(len(m["outcomes"]) for b in books for m in b["markets"])

    # ---------------------------------------------------------------- index
    kpis = "".join(
        f'<div class="kpi"><b>{v}</b><span>{k}</span></div>' for k, v in [
            ("Fixture rows", len(books)), ("Priced", len(priced)), ("Unpriced", len(books) - len(priced)),
            ("Originated markets", markets), ("Outcome prices", outcomes),
            ("High confidence", len(high)), ("In -250..+10000", sum(1 for b in priced if b["pick_in_window"])),
            ("Write-ups", len(PREDICTIONS)), ("Sports with a gap", len(D.COVERAGE_GAPS)),
        ])
    top = "".join(
        f"<tr><td>{i}</td><td>{esc(b['away'])} @ {esc(b['home'])}</td><td>{esc(b['date'])} "
        f"{esc(b['start_utc'][11:16])} UTC</td><td>{esc(b['pick'])}</td>"
        f"<td>{b['pick_probability']*100:.1f}%</td><td>{b['pick_american']:+d} ({b['pick_decimal']:.3f})</td>"
        f"<td>{band_tag(b)}</td><td>{src_links(b['source_ids'])}</td></tr>"
        for i, b in enumerate(slate, 1))
    cov = "".join(
        f'<tr><td><a href="sports/{slug}.html">{esc(D.SPORT_LABEL[slug])}</a></td>'
        f'<td>{D.OLBG_ROUTES[slug][1]}</td>'
        f'<td>{ext("https://www.olbg.com/betting-tips/" + D.OLBG_ROUTES[slug][0] + "/" + str(D.OLBG_ROUTES[slug][1]), "OLBG hub")}</td>'
        f'<td>{len([b for b in books if b["sport"] == slug])}</td>'
        f'<td>{"priced" if slug == "ice_hockey" else ("listed, unpriced" if slug == "baseball" else "none published")}</td></tr>'
        for slug in D.SPORT_LABEL)
    index = page("T5821 · OLBG1 evidence desk", "OLBG1 evidence desk — 23 October 2026", f"""
<div class="kpis">{kpis}</div>
<div class="panel"><h2 style="margin-top:0">Executive summary</h2>
<p>Everything below was read from official publishers on 23 October 2026. The desk carries
<b>{len(books)} fixture rows</b>: {len(nhl)} National Hockey League games from the league's own schedule
feed (2 on 23 October, 12 on 24 October and the first of 5 on 25 October) and the three scheduled
2026 World Series games between the Tampa Bay Rays and the Milwaukee Brewers.</p>
<p><b>{len(high)} calls clear the 70% floor</b> — Vegas Golden Knights ({high[0]['pick_probability']*100:.1f}%),
New Jersey Devils, Boston Bruins and Edmonton Oilers. Each of the four originates a price
<b>shorter than −250</b>, so none of them sits inside the −250…+10000 window the brief asks us to
focus on; that is reported rather than papered over. The strongest call that <em>does</em> sit inside
the window is Anaheim at Philadelphia at {anaheim['pick_american']:+d} ({anaheim['pick_probability']*100:.1f}%),
and every call inside the window carries a medium tier, not a high one. Carolina at St. Louis at
{carolina['pick_american']:+d} is the other in-window call written up here.</p>
<p>Thirteen of the fifteen covered sports have <b>no fixture rows in this release</b>. The official
fixture list for those sports was not read in this pass, and rows were not invented to fill the
table; each gap is itemised on <a href="flagged.html">Flagged for review</a>. Baseball is listed but
unpriced because only one side's official season record was read.</p></div>
<h2>Today's and tomorrow's highest-confidence calls</h2>
<table><thead><tr><th>#</th><th>Match</th><th>Start (UTC)</th><th>Selection</th><th>Probability</th>
<th>Fair price</th><th>Tier / window</th><th>Official source</th></tr></thead><tbody>{top}</tbody></table>
<p class="small">Prices are fair values (1 ÷ probability) with no bookmaker margin. They are not offers
and no bookmaker quote was read.</p>
<h2>Coverage by sport</h2>
<table><thead><tr><th>Sport</th><th>OLBG sport id</th><th>OLBG discovery route</th><th>Rows</th><th>Status</th></tr></thead>
<tbody>{cov}</tbody></table>
<h2>Where to go next</h2>
<p><a href="matches.html">Every fixture row</a> · <a href="markets.html">Every originated market</a> ·
<a href="high-confidence.html">Ranked calls</a> · <a href="predictions.html">Written calls</a> ·
<a href="flagged.html">Flagged for review</a> · <a href="methodology.html">Methodology</a> ·
<a href="sources.html">Source register</a> · <a href="analysis.html">Repository and OLBG review</a></p>
""", "index.html")

    # -------------------------------------------------------------- matches
    rows = []
    for b in books:
        pick = "—" if b.get("unpriced") else f"{esc(b['pick'])} {b['pick_probability']*100:.1f}% ({b['pick_american']:+d})"
        rows.append(
            f"<tr><td>{esc(b['id'])}</td><td>{esc(D.SPORT_LABEL[b['sport']])}</td><td>{esc(b['date'])}</td>"
            f"<td>{esc(b['start_utc'])}</td><td>{esc(b['away'])}</td><td>{esc(b['home'])}</td>"
            f"<td>{esc(b['venue'])}</td><td>{pick}</td><td>{band_tag(b)}</td>"
            f"<td>{src_links(b['source_ids'])}</td></tr>")
    matches = page("Matches · T5821", "Fixture rows read from official publishers", f"""
<p>{len(books)} rows. A blank cell means the publisher did not state that value in the page read, or
this desk did not read it; nothing is filled in from memory.</p>
<table><thead><tr><th>Row id</th><th>Sport</th><th>Date</th><th>Start (UTC)</th><th>Away</th><th>Home</th>
<th>Venue</th><th>Selection</th><th>Tier</th><th>Official source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<div class="panel warn"><h3>Unpriced rows</h3><p>{esc(mlb[0]['unpriced_reason'])} The three World Series
games therefore publish no price, no handicap and no total.</p></div>
""", "matches.html")

    # -------------------------------------------------------------- markets
    mrows = []
    for b in books:
        for m in b["markets"]:
            cells = " · ".join(
                f"{esc(o['selection'])} {o['probability']*100:.1f}% ({o['american_display']:+d})"
                for o in m["outcomes"])
            mrows.append(f"<tr><td>{esc(b['away'])} @ {esc(b['home'])}</td><td>{esc(b['date'])}</td>"
                         f"<td>{esc(m['market'])}</td><td>{cells}</td><td>{esc(m['note'])}</td>"
                         f"<td>{src_links(b['source_ids'])}</td></tr>")
    wrows = []
    for b in books:
        for w in b.get("withheld", []):
            wrows.append(f"<tr><td>{esc(b['away'])} @ {esc(b['home'])}</td><td>{esc(w['market'])}</td>"
                         f"<td>{esc(w['status'])}</td><td>{esc(w['reason'])}</td>"
                         f"<td>{src_links(b['source_ids'])}</td></tr>")
    markets_page = page("Markets · T5821", "Originated markets and deliberately blank ones", f"""
<p>{markets} two-way books across three families — money line, puck line −1.5 and match total 5.5 —
giving {outcomes} outcome prices. Every probability sums to 1.00 across its two sides and every price
is the fair value 1 ÷ probability with no margin added. Handicap and total lines are originated
lines, not quoted offers.</p>
<table><thead><tr><th>Match</th><th>Date</th><th>Market</th><th>Outcomes (probability, fair American)</th>
<th>Basis</th><th>Official source</th></tr></thead><tbody>{''.join(mrows)}</tbody></table>
<h2>Market families left blank</h2>
<p>These are published blank with a reason instead of being estimated.</p>
<table><thead><tr><th>Match</th><th>Market</th><th>Status</th><th>Reason</th><th>Official source</th></tr></thead>
<tbody>{''.join(wrows)}</tbody></table>
""", "markets.html")

    # ------------------------------------------------------- high confidence
    hrows = "".join(
        f"<tr><td>{i}</td><td>{esc(b['away'])} @ {esc(b['home'])}</td><td>{esc(b['date'])} "
        f"{esc(b['start_utc'][11:16])} UTC</td><td>{esc(b['pick'])}</td>"
        f"<td>{b['pick_probability']*100:.1f}%</td><td>{b['pick_decimal']:.3f}</td>"
        f"<td>{b['pick_american']:+d}</td><td>{band_tag(b)}</td>"
        f"<td>{esc(b['inputs']['home']['record'])} v {esc(b['inputs']['away']['record'])}</td>"
        f"<td>{src_links(b['source_ids'])}</td></tr>"
        for i, b in enumerate(high, 1))
    mrows2 = "".join(
        f"<tr><td>{i}</td><td>{esc(b['away'])} @ {esc(b['home'])}</td><td>{esc(b['pick'])}</td>"
        f"<td>{b['pick_probability']*100:.1f}%</td><td>{b['pick_american']:+d}</td><td>{band_tag(b)}</td>"
        f"<td>{src_links(b['source_ids'])}</td></tr>" for i, b in enumerate(medium, 1))
    hc = page("High confidence · T5821", "Ranked calls and the price-window test", f"""
<div class="panel"><p>The brief asks for high-confidence calls whose price sits between −250 and
+10000. On this slate the two conditions pull apart: the four calls that clear 70% all originate a
price <b>shorter</b> than −250, and every call inside the window sits below 70%. Both facts are
published rather than reconciled by lowering the evidence bar.</p></div>
<h2>Calls above the 70% floor</h2>
<table><thead><tr><th>#</th><th>Match</th><th>Start (UTC)</th><th>Selection</th><th>Probability</th>
<th>Fair decimal</th><th>Fair American</th><th>Tier / window</th><th>Records read</th>
<th>Official source</th></tr></thead><tbody>{hrows}</tbody></table>
<h2>Strongest calls inside the −250…+10000 window</h2>
<table><thead><tr><th>#</th><th>Match</th><th>Selection</th><th>Probability</th><th>Fair American</th>
<th>Tier / window</th><th>Official source</th></tr></thead><tbody>{mrows2}</tbody></table>
""", "high-confidence.html")

    # ---------------------------------------------------------- predictions
    blocks = []
    for p in PREDICTIONS:
        b = next(x for x in books if x["id"] == p["fixture_id"])
        blocks.append(f"""<div class="panel"><h3>{esc(p['match'])}</h3>
<p class="small">{esc(b['date'])} · {esc(b['start_utc'])} · {esc(b['venue'])} · selection
<b>{esc(p['selection'])}</b> on the {esc(p['market'])} · {b['pick_probability']*100:.1f}% ·
{b['pick_american']:+d} fair · {band_tag(b)}</p>
<p>{esc(p['text'])}</p>
<p class="small">Numbers read from {src_links(p['sources'])}</p></div>""")
    preds = page("Predictions · T5821", "Written calls", f"""
<p>Six hand-written calls, each at least 30 words, each unique, none repeating another's phrasing.
Four of them are calls above the 70% floor; the other two are the strongest calls inside the
−250…+10000 window, led by Anaheim at Philadelphia at −214, and both carry a medium tier because
that is what the evidence supports. No injury or line-up claim
appears in any of them: no official availability page was read in this pass, so nothing was
inferred.</p>{''.join(blocks)}
<div class="panel warn"><h3>Target shortfall, stated plainly</h3><p>The brief aims for five calls per
covered sport per day. This release carries six calls in total, all in ice hockey, because ice
hockey is the only sport where an official fixture list <em>and</em> official records were both read.
Calls were not manufactured for the other fourteen sports.</p></div>
""", "predictions.html")

    # -------------------------------------------------------------- flagged
    flags = [
        ("F-5821-01", "coverage", "Thirteen sports carry no fixture rows",
         "Tennis, snooker, golf, cricket, rugby union, rugby league, motor racing, darts, handball, "
         "volleyball, Gaelic sports, greyhounds and basketball publish zero rows. The official "
         "fixture list for each was not read in this pass and no row was invented.",
         "https://www.olbg.com/sitemap-betting-tips.xml", "official route list read; per-sport pages not read"),
        ("F-5821-02", "data", "Baseball rows are unpriced",
         "Only the Milwaukee Brewers' official 2026 record (103-59, 832 runs for, 618 against) was "
         "read. The Tampa Bay Rays' record was not read, and the pricing rule needs both measured "
         "records, so no money line, run line or total is published.",
         SOURCES["mlb-nl-standings"]["url"], "single-sided input"),
        ("F-5821-03", "pricing", "All four high-confidence calls price shorter than −250",
         "Vegas −337, New Jersey −325, Boston −317 and Edmonton −260. They clear the 70% floor but "
         "fall outside the −250…+10000 window, so none is presented as an in-window call.",
         SOURCES["nhl-standings"]["url"], "window conflict disclosed"),
        ("F-5821-04", "irregularity", "NHL schedule feed embeds inconsistent bookmaker odds",
         "The official schedule response carries an odds array per side whose providers mix decimal "
         "and American formats and disagree on which side is favoured (for Montreal at Chicago one "
         "provider shows 2.35 and another −169 on the same side). It was not used as a price input.",
         SOURCES["nhl-schedule-1023"]["url"], "upstream data quality"),
        ("F-5821-05", "irregularity", "OLBG hubs served an empty tip listing",
         "The tennis hub, the ice hockey hub and the NHL competition sub-route all returned the "
         "literal text 'No tips found.' with no event rows in the delivered HTML, so OLBG supplied "
         "route grammar only. This does not prove OLBG lists zero events; it proves this desk could "
         "not read any.",
         SOURCES["olbg-hub-tennis"]["url"], "discovery blocked, not a zero-fixture finding"),
        ("F-5821-06", "irregularity", "Clock times are published without a timezone label",
         "wst.tv prints Northern Ireland Open session times such as '05:00 Sun 18 Oct' with no zone, "
         "and Belfast is on BST until 25 October. No snooker start time is published by this desk.",
         SOURCES["wst-ni-open-matches"]["url"], "timezone ambiguity"),
        ("F-5821-07", "data", "2026-10-25 NHL games are counted but not all enumerated",
         "The official feed states five games for Sunday 25 October. Only Florida at Chicago was read "
         "individually; the remaining four are counted from the feed's numberOfGames field and are "
         "not published as rows.",
         SOURCES["nhl-schedule-1024"]["url"], "partial enumeration"),
        ("F-5821-08", "data", "No injury or line-up evidence",
         "No official availability page was read for any club, so no prediction makes an injury "
         "claim and no price is adjusted for absences.",
         SOURCES["nhl-standings"]["url"], "input absent by design"),
        ("F-5821-09", "scope", "Totals exclude overtime and shootout goals",
         "The 5.5-goal book is built from a regulation goal distribution only, which biases the under "
         "side. It is published as an originated line, not a quoted offer.",
         SOURCES["nhl-standings"]["url"], "disclosed limitation"),
        ("F-5821-10", "scope", "Eight to twelve games of season data only",
         "Every NHL club has played between 8 and 12 games, so records are volatile and no "
         "calibration claim is made. Confidence tiers are probability bands, not calibrated "
         "frequencies.",
         SOURCES["nhl-standings"]["url"], "small-sample disclosure"),
    ]
    frows = "".join(
        f'<tr><td>{esc(i)}</td><td>{esc(k)}</td><td>{esc(t)}</td><td>{esc(d)}</td>'
        f'<td>{ext(u, "official page")}</td><td>{esc(n)}</td></tr>'
        for i, k, t, d, u, n in flags)
    flagged = page("Flagged for review · T5821", "Flagged for review", f"""
<p>{len(flags)} items. None of them blocks publication; each one is a place where this desk would
rather show a hole than fill it with a guess.</p>
<table><thead><tr><th>Id</th><th>Kind</th><th>Finding</th><th>Detail</th><th>Source</th><th>Note</th></tr></thead>
<tbody>{frows}</tbody></table>
<h2>Sport-by-sport gap statements</h2>
<table><thead><tr><th>Sport</th><th>OLBG route read</th><th>Why no rows</th></tr></thead><tbody>
{''.join(f'<tr><td>{esc(D.SPORT_LABEL[s])}</td><td>{ext("https://www.olbg.com/betting-tips/" + D.OLBG_ROUTES[s][0] + "/" + str(D.OLBG_ROUTES[s][1]), "hub")}</td><td>{esc(D.COVERAGE_GAPS[s])}</td></tr>' for s in D.COVERAGE_GAPS)}
</tbody></table>
""", "flagged.html")

    # ---------------------------------------------------------- methodology
    meth = page("Methodology · T5821", "How these numbers were produced", f"""
<h2>What counts as a fact</h2>
<p>A value appears in a table only if it was read from an official publisher — the league, tour or
governing body — during this session, at the timestamp recorded in the
<a href="sources.html">source register</a>. OLBG routes are discovery: they tell us where a sport
lives, never what happened in a match. Media and aggregator pages are not used at all. Anything not
read stays blank and is listed on <a href="flagged.html">Flagged for review</a>.</p>
<h2>How a price is originated</h2>
<p>Two estimators are computed per club from the official standings and then averaged:</p>
<ol><li><b>Binary record share</b> — wins ÷ games played, with overtime and shootout losses counted
as defeats.</li>
<li><b>Pythagorean expectation</b> — goals for² ÷ (goals for² + goals against²), exponent 2.</li></ol>
<p>The two sides are compared with log5, <code>(pa − pa·pb) ÷ (pa + pb − 2·pa·pb)</code>. No home-ice
edge is inserted, no default rating is substituted for a missing club, and no bookmaker quote is
used anywhere. Fair decimal is <code>1 ÷ p</code> with no margin; the American display follows from
the decimal, so a −250 fair price is exactly a 71.43% probability.</p>
<h2>Handicap and totals</h2>
<p>Expected goals per side come from the two clubs' official scoring rates, again with no venue
adjustment. A Poisson goal distribution gives the −1.5 cover chance and the 5.5 total. Overtime and
shootout goals are excluded, which is disclosed on every totals row.</p>
<h2>Confidence tiers and the price window</h2>
<p>High means a probability of 70% or more. Medium is 60–70%. Everything else is low. The −250…+10000
window is reported as a separate flag on every call, because on this slate the four high calls all
price shorter than −250 and nothing above 70% lands inside the window. Publishing that conflict is
the point: it is the honest reading of the two rules together.</p>
<h2>Expiry</h2>
<p>The snapshot is {esc(SNAPSHOT)}. Each row's relevance ends at its start time; the three World
Series rows run to 27 October. A later build never re-dates an earlier read.</p>
<h2>What this desk is not</h2>
<p>Not affiliated with OLBG. Not bookmaker execution, not staking advice, not a calibrated
probability service. 18+ only.</p>
""", "methodology.html")

    # -------------------------------------------------------------- sources
    srows = "".join(
        f'<tr><td>{esc(s["id"])}</td><td>{esc(s["name"])}</td><td>{esc(s["role"])}</td>'
        f'<td>{esc(s["read_utc"])}</td><td>{ext(s["url"], s["url"])}</td><td>{esc(s["note"])}</td></tr>'
        for s in D.SOURCES)
    sources = page("Sources · T5821", "Source register", f"""
<p>Every page read during this session, with the time it was read. Official publishers verify facts;
discovery routes only show where a sport is listed.</p>
<table><thead><tr><th>Id</th><th>Name</th><th>Role</th><th>Read (UTC)</th><th>URL</th><th>What it gave us</th></tr></thead>
<tbody>{srows}</tbody></table>
""", "sources.html")

    # ------------------------------------------------------------- analysis
    analysis = page("Repo & OLBG review · T5821", "Repository review and OLBG route grammar", f"""
<h2>OLBG route grammar confirmed on 2026-10-23</h2>
<p>The public sitemap <code>sitemap-betting-tips.xml</code> was read in full and carries
<code>lastmod 2026-10-23</code> on every route. Sport hubs follow
<code>/betting-tips/&#123;Sport_Slug&#125;/&#123;sport_id&#125;</code>; the fifteen sports in the brief map to
the identifiers below. <code>robots.txt</code> disallows <code>/api/</code> and
<code>/storage/app/json_data/</code>, and neither was requested.</p>
<table><thead><tr><th>Sport</th><th>Slug</th><th>Sport id</th><th>Route</th></tr></thead><tbody>
{''.join(f'<tr><td>{esc(D.SPORT_LABEL[s])}</td><td>{esc(D.OLBG_ROUTES[s][0])}</td><td>{D.OLBG_ROUTES[s][1]}</td><td>{ext("https://www.olbg.com/betting-tips/" + D.OLBG_ROUTES[s][0] + "/" + str(D.OLBG_ROUTES[s][1]), "open hub")}</td></tr>' for s in D.OLBG_ROUTES)}
</tbody></table>
<h2>What the hubs returned</h2>
<p>The tennis hub, the ice hockey hub and the NHL competition sub-route each returned server-rendered
SEO prose plus the literal empty state <code>No tips found.</code> — no event rows in the delivered
HTML. That is recorded as a discovery limitation, not as evidence that OLBG lists no events.</p>
<h2>Repository observations</h2>
<ul>
<li>The canonical gates in <code>.github/workflows/current-pages.yml</code> run the pipeline tests,
<code>pipeline.validate --site .</code>, <code>scripts/validate.py</code>, a build to
<code>_site</code> and browser tests before publishing. This desk adds files only inside
<code>e58210b8/</code>, <code>data/e58210b8/</code> and <code>scripts/se58210b8_*.py</code>, so no
shared page or workflow was touched.</li>
<li><code>pipeline.build.stage_existing</code> copies every tracked file into the deployed artifact,
so this desk is served from <code>/OLBG1/e58210b8/</code> without editing shared navigation.</li>
<li><code>scripts/validate.py</code> link-checks every HTML file in the repository, including this
desk; all links here are relative or HTTPS and were checked by
<code>scripts/se58210b8_validate.py</code>.</li>
<li>The repository's <code>COORDINATION.md</code> board was read before claiming. Task
<code>T5821</code> and section <code>§73</code> were claimed and pushed before any file was written,
per §0.3.</li>
<li>Peer desks <code>429a54a2/</code>, <code>fa24508c/</code>, <code>8a900c04/</code> and
<code>efe12010/</code> were left untouched.</li>
</ul>
<h2>Irregularities worth a second pair of eyes</h2>
<p>The NHL odds array inconsistency, the OLBG empty-state behaviour and the unlabeled snooker clock
are all written up on <a href="flagged.html">Flagged for review</a> with their source pages.</p>
""", "analysis.html")

    # ----------------------------------------------------------- sport pages
    for slug in D.SPORT_LABEL:
        rows = [b for b in books if b["sport"] == slug]
        route = "https://www.olbg.com/betting-tips/" + D.OLBG_ROUTES[slug][0] + "/" + str(D.OLBG_ROUTES[slug][1])
        if rows:
            body_rows = "".join(sport_row(b) for b in rows)
            table = (f"<table><thead><tr><th>Date</th><th>Start (UTC)</th><th>Away</th><th>Home</th>"
                     f"<th>Venue</th><th>Selection</th><th>Tier</th><th>Official source</th></tr></thead>"
                     f"<tbody>{body_rows}</tbody></table>")
        else:
            table = (f"<div class='panel warn'><p><b>No rows published.</b> {esc(D.COVERAGE_GAPS[slug])}</p>"
                     f"<p class='small'>Discovery route read: {ext(route, route)}</p></div>")
        doc_page = page(f"{D.SPORT_LABEL[slug]} · T5821", f"{D.SPORT_LABEL[slug]}", f"""
<p>OLBG discovery route: {ext(route, route)} (sport id {D.OLBG_ROUTES[slug][1]}).</p>
{table}
<p class="small">A blank cell means the publisher did not state the value in the page read, or the
value was not read at all. Nothing is filled in from memory.</p>
<p><a href="../index.html">← Dashboard</a></p>
""", prefix="../")
        (OUT / "sports" / f"{slug}.html").write_text(doc_page, encoding="utf-8")

    for name, content in [("index.html", index), ("matches.html", matches), ("markets.html", markets_page),
                          ("high-confidence.html", hc), ("predictions.html", preds),
                          ("flagged.html", flagged), ("methodology.html", meth),
                          ("sources.html", sources), ("analysis.html", analysis)]:
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(list(OUT.rglob('*.html')))} pages to {OUT.relative_to(ROOT)}")
    print(f"books={len(books)} high={len(high)} medium={len(medium)} markets={markets} outcomes={outcomes}")


if __name__ == "__main__":
    build()
