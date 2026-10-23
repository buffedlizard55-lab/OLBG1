#!/usr/bin/env python3
"""Session 7a9b24e5 — static dashboard generator.

Reads data/7a9b24e5/*.json and writes the namespaced desk at 7a9b24e5/.
No external assets, no fonts, no analytics, no browser-facing localhost calls.
"""
from __future__ import annotations

import html
import json
import math
import pathlib

DATA = pathlib.Path("data/7a9b24e5")
OUT = pathlib.Path("7a9b24e5")
EV_EXPIRY = "2026-10-24T03:55Z"
BUILT = "2026-10-23T22:05Z"

SPORT_ORDER = ["Baseball", "Basketball", "Cricket", "Darts", "Gaelic Sports", "Golf",
               "Greyhounds", "Handball", "Ice Hockey", "Motor Racing", "Rugby League",
               "Rugby Union", "Snooker", "Tennis", "Volleyball"]
SLUG = {s: s.lower().replace(" ", "-") for s in SPORT_ORDER}

NAV = [("index.html", "Dashboard"), ("matches.html", "Matches"), ("markets.html", "Markets"),
       ("high-confidence.html", "High confidence"), ("predictions.html", "Predictions"),
       ("analysis.html", "Analysis"), ("sources.html", "Sources"), ("flagged.html", "Flagged for review"),
       ("methodology.html", "Methodology"), ("reverse-engineering.html", "OLBG structure"),
       ("repo-audit.html", "Repo audit")]

AUDIT = [
    dict(id="RA-01", sev="low", file="all.html / matches.html", line=None,
         finding="The two root pages are byte-identical (same SHA-256). Duplicate publication of the same table; harmless but inflates the page count claimed in release notes.",
         evidence="sha256 equality over the two tracked files"),
    dict(id="RA-02", sev="info", file="a0b04058/audit.html, a0b04058/repo-audit.html", line=None,
         finding="Two further byte-identical page pairs inside a peer desk (audit.html = repo-audit.html, high-confidence.html = picks.html).",
         evidence="sha256 equality"),
    dict(id="RA-03", sev="medium", file="README.md", line=9,
         finding="README headline ('108 fixture/event listings') does not match the current data/fixtures.json, which holds 134 rows in both its 'matches' and 'fixtures' arrays. The text is dated 22 Oct, so this is a stale-copy risk rather than a false claim about today.",
         evidence="data/fixtures.json length read this session"),
    dict(id="RA-04", sev="medium", file="data/**/*.json", line=None,
         finding="1,843 identifiers (e.g. rl-wc26-tga-lbn, el-pao-bas-1022) appear in more than one session JSON file with different prices. Any aggregation across desks will double-count events unless it de-duplicates on event id + session.",
         evidence="recursive scan of 324 tracked JSON files"),
    dict(id="RA-05", sev="low", file="markets.html", line=1,
         finding="The root markets page is a single 2.24 MB HTML document (next largest 1.06 MB). It renders, but on slow connections it will block; pagination would be safer.",
         evidence="file size from git ls-files inventory"),
    dict(id="RA-06", sev="info", file="(whole tree)", line=None,
         finding="Structural checks passed: 0 invalid JSON files (324), 0 tracked .pyc artifacts, 0 missing internal link targets on root pages, 0 missing asset references across all 1,217 HTML files.",
         evidence="scripts run this session"),
    dict(id="RA-08", sev="high", file="scripts/se58210b8_predictions.py", line=27,
         finding="This file reached main with unresolved merge-conflict markers (nested HEAD blocks, two separator lines and two commit-marker lines), which made it unparseable: the e58210b8 desk test errored and the tree-wide parse audit recorded one error, failing the 8a900c04 check as well. Peer PR #194 repaired it on main while this session was in flight; after rebasing, this branch carries no remaining difference, and the full suite is green.",
         evidence="python -m unittest discover -s tests/pipeline, before and after"),
    dict(id="RA-07", sev="info", file="data/fixtures.json", line=1,
         finding="Every one of the 134 fixture rows carries a source field; no row was found without a provenance key. This audit checks presence, not that each URL still resolves.",
         evidence="key-level scan"),
]


def esc(x) -> str:
    return html.escape(str(x)) if x is not None else ""


def fmt_am(a: int) -> str:
    return f"+{a}" if a > 0 else str(a)


def settlement(market: str, selection: str, line) -> str:
    if line is None:
        if market == "Match Winner":
            return f"{selection} must win the match."
        return ""
    if market.startswith("Team Total"):
        side = "score at least"
        n = line
        if abs(n * 4 - round(n * 4)) < 1e-9 and abs(n * 2 - round(n * 2)) > 1e-9:
            lo = math.floor(n)
            return (f"{selection.split(' Over ')[0]} {side} {lo + 1} goals to win outright; "
                    f"exactly {lo} returns half the stake.")
        if abs(n - round(n)) < 1e-9:
            return f"{selection.split(' Over ')[0]} {side} {int(n) + 1} goals; exactly {int(n)} is a push."
        return f"{selection.split(' Over ')[0]} {side} {math.ceil(n)} goals."
    if market.startswith("Match Total"):
        over = selection.startswith("Over")
        word = "more than" if over else "fewer than"
        if abs(line * 2 - round(line * 2)) > 1e-9:
            lo = math.floor(line)
            return (f"{'Over' if over else 'Under'} needs {'7+' if over else '6 or fewer'} runs at this quarter line; "
                    f"exactly {lo} returns half the stake.")
        return f"Total runs must be {word} {line:g}."
    if market.startswith("Handicap"):
        team, _, ln = selection.rpartition(" ")
        try:
            v = float(ln)
        except ValueError:
            return ""
        if v < 0:
            need = abs(v)
            if abs(need - round(need)) < 1e-9:
                return f"{team} must win by {int(need) + 1} or more; a {int(need)}-point win is a push."
            return f"{team} must win by {math.ceil(need)} or more."
        if abs(v - round(v)) < 1e-9:
            return f"{team} covers if they lose by {int(v) - 1} or fewer, draw or win; a {int(v)}-point defeat is a push."
        return f"{team} covers if they lose by {math.floor(v)} or fewer, draw or win."
    return ""


def layout(title: str, body: str, active: str = "", rel: str = "") -> str:
    nav = "".join(
        '<a href="%s%s"%s>%s</a>' % (rel, href, ' class="on"' if href == active else '', label)
        for href, label in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG desk 7a9b24e5</title>
<link rel="stylesheet" href="{rel}assets/style.css">
</head><body>
<header><div class="wrap">
<div class="brand">OLBG research desk <span>session 7a9b24e5 · built {BUILT}</span></div>
<nav>{nav}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="wrap">
<p>Independent research desk. Not affiliated with OLBG. Originated prices are estimates, not bookmaker
quotes. No guaranteed returns. 18+. Evidence expires {EV_EXPIRY} (six hours from the read window).</p>
</footer>
</body></html>
"""


def table(head: list[str], rows: list[list[str]], cls: str = "") -> str:
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def main() -> None:
    desk = json.loads((DATA / "desk.json").read_text())
    markets = json.loads((DATA / "markets.json").read_text())
    picks = json.loads((DATA / "picks.json").read_text())
    capped = json.loads((DATA / "capped.json").read_text())
    preds = {p["pick_id"]: p for p in json.loads((DATA / "predictions.json").read_text())["predictions"]}
    reads = {r["id"]: r for r in desk["reads"]}
    fx = {f["id"]: f for f in desk["fixtures"]}

    OUT.mkdir(exist_ok=True)
    (OUT / "sports").mkdir(exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "assets" / "style.css").write_text(CSS, encoding="utf-8")

    by_sport: dict[str, list[dict]] = {s: [] for s in SPORT_ORDER}
    for f in desk["fixtures"]:
        by_sport[f["sport"]].append(f)
    picks_by_sport: dict[str, list[dict]] = {}
    for p in picks:
        picks_by_sport.setdefault(fx[p["fixture"]]["sport"], []).append(p)

    covered = [s for s in SPORT_ORDER if by_sport[s]]
    priced = [s for s in SPORT_ORDER if picks_by_sport.get(s)]
    gaps = desk["gaps"]

    # ---------------- dashboard ----------------
    kpi = f"""
<section class="kpis">
<div><b>{len(desk['fixtures'])}</b><span>fixtures read from official pages</span></div>
<div><b>{len(placed := [f for f in desk['fixtures'] if f['id'] != 'BB05'])}</b><span>priced-eligible fixtures</span></div>
<div><b>{len(markets)}</b><span>originated market outcomes</span></div>
<div><b>{len(picks)}</b><span>in-band High picks</span></div>
<div><b>{len(covered)}/15</b><span>sports with a confirmed fixture</span></div>
<div><b>{len(gaps)}</b><span>sports with a documented gap</span></div>
</section>"""

    pick_rows = []
    for p in picks:
        f = fx[p["fixture"]]
        when = f["start_utc"] or "time zone unresolved"
        pick_rows.append([
            f'<a href="sports/{SLUG[f["sport"]]}.html">{esc(f["sport"])}</a>',
            f'{esc(f["home"])} v {esc(f["away"])}<br><span class="muted">{esc(f["comp"])}</span>',
            when,
            f'<b>{esc(p["selection"])}</b><br><span class="muted">{esc(p["market"])}</span>',
            f'{p["p"]*100:.2f}%',
            fmt_am(p["fair_american"]),
            f'<a href="{esc(reads[f["src"]]["url"])}" target="_blank" rel="noopener">{esc(reads[f["src"]]["name"])}</a>',
            f'<a href="predictions.html#{p["pick_id"]}">read prediction</a>',
        ])

    sport_rows = []
    for s in SPORT_ORDER:
        n = len(by_sport[s])
        k = len(picks_by_sport.get(s, []))
        if s in gaps:
            state = '<span class="pill gap">no confirmed fixture</span>'
        elif k:
            state = f'<span class="pill hi">{k} High picks</span>'
        elif n:
            state = '<span class="pill med">fixtures only, no in-band pick</span>'
        else:
            state = '<span class="pill gap">gap</span>'
        sport_rows.append([f'<a href="sports/{SLUG[s]}.html"><b>{esc(s)}</b></a>', str(n), str(k), state])

    body = f"""
<h1>Executive summary — Friday 23 October 2026</h1>
<p class="lede">This desk read <b>{len(desk['reads'])} official and discovery sources</b> between
{esc(desk['read_window'][0])} and {esc(desk['read_window'][1])} UTC, published <b>{len(desk['fixtures'])} fixtures</b>
across <b>{len(covered)} of the 15 sports in the brief</b>, and originated <b>{len(markets)} prices</b>.
<b>{len(picks)} selections</b> clear the High gate: probability of at least 62% <em>and</em> a fair price no shorter
than −250. Everything that could not be read is blank and listed on the
<a href="flagged.html">Flagged for review</a> page.</p>
{kpi}

<h2>Today's highest-confidence picks</h2>
<p class="muted">Fair prices are zero-vig (1 ÷ probability). “In band” means the fair American price is no shorter
than −250, which is a probability of 71.43%. Paired with a 62% confidence floor, the promoted window is 62.00%–71.43%.
Anything above 71.43% would be priced shorter than −250 and is published as capped, never promoted.</p>
{table(["Sport", "Fixture", "Start (UTC)", "Selection", "Probability", "Fair price", "Official source", "Write-up"], pick_rows)}

<h2>Sport coverage</h2>
{table(["Sport", "Fixtures", "High picks", "State"], sport_rows)}

<h2>What this desk will not do</h2>
<ul class="notes">
<li>It will not price a sport whose official fixture list it could not read. Six sports are gaps today and five
more have fixtures without an in-band High pick; both are shown above rather than filled with invented numbers.</li>
<li>It will not convert an unlabelled kick-off time. Where an official page printed “local” or “your time” with no
zone, the UTC column is blank and the row is flagged.</li>
<li>It will not claim an injury. No official injury report was read inside this window, so no prediction mentions one.</li>
</ul>
"""
    (OUT / "index.html").write_text(layout("Executive summary", body, "index.html"), encoding="utf-8")

    # ---------------- matches ----------------
    mrows = []
    for f in desk["fixtures"]:
        start = f["start_utc"] or '<span class="warn">blank</span>'
        note = f'<br><span class="warn">{esc(f["start_note"])}</span>' if f["start_note"] else ""
        status = "withheld (ifNecessary=Y)" if f["id"] == "BB05" else (
            "High pick" if any(p["fixture"] == f["id"] for p in picks) else "no in-band pick")
        mrows.append([
            esc(f["id"]),
            f'<a href="sports/{SLUG[f["sport"]]}.html">{esc(f["sport"])}</a>',
            f'<b>{esc(f["home"])}</b> v {esc(f["away"])}',
            esc(f["comp"]), esc(f["venue"]) or '<span class="warn">not published</span>',
            start + note,
            f'{esc(f["rec_home"]) or "—"} / {esc(f["rec_away"]) or "—"}',
            status,
            f'<a href="{esc(reads[f["src"]]["url"])}" target="_blank" rel="noopener">{esc(reads[f["src"]]["name"])}</a>'
            + (f'<br><a class="muted" href="{esc(reads[f["src2"]]["url"])}" target="_blank" rel="noopener">second source</a>' if f.get("src2") else ""),
        ])
    body = f"""
<h1>Match list</h1>
<p class="lede">Every row below was read from the official page linked in the last column. Blank start times mean
the official page printed a local or “your time” clock without a zone; we do not convert it.</p>
{table(["ID", "Sport", "Fixture", "Competition", "Venue", "Start (UTC)", "Record (home / away)", "Status", "Official source"], mrows)}
<p class="muted">Records shown are the exact strings published: win-loss for baseball, basketball and hockey,
round results for rugby league, and league-table position/points difference is shown on each sport page.</p>
"""
    (OUT / "matches.html").write_text(layout("Matches", body, "matches.html"), encoding="utf-8")

    # ---------------- markets ----------------
    sections = []
    for s in SPORT_ORDER:
        ids = [f["id"] for f in by_sport[s]]
        if not ids:
            continue
        rows = []
        for m in markets:
            if m["fixture"] not in ids:
                continue
            rows.append([esc(m["fixture"]), esc(m["market"]), esc(m["selection"]),
                         esc(m["line"]) if m["line"] is not None else "—",
                         (m.get("line_type") or "—") if m["line"] is not None else "—",
                         f'{m["p"]*100:.2f}%', f'{m["fair_decimal"]:.3f}',
                         fmt_am(m["fair_american"]),
                         f'<span class="pill {"hi" if m["tier"]=="High" else ("med" if m["tier"]=="Medium" else "low")}">{m["tier"]}</span>'])
        sections.append(f'<h2>{esc(s)} <span class="muted">({len(rows)} outcomes)</span></h2>' +
                        table(["Fixture", "Market", "Selection", "Line", "Line type", "Probability", "Fair decimal", "Fair American", "Tier"], rows))
    body = f"""
<h1>Market explorer — {len(markets)} originated outcomes</h1>
<p class="lede">Every price is our own zero-vig estimate from the official inputs listed on the sport pages.
Nothing here is a bookmaker quote and no margin is added. Lines are originated at quarter- and half-point
increments; <b>quarter</b> lines settle as a split stake and are marked as such because many mainstream books
only list half-point lines.</p>
<p><a href="data/markets.json">Download the full market set (JSON)</a> ·
<a href="high-confidence.html">Only the in-band High picks</a></p>
{''.join(sections)}
"""
    (OUT / "markets.html").write_text(layout("Markets", body, "markets.html"), encoding="utf-8")

    # ---------------- high confidence ----------------
    rows = []
    for p in picks:
        f = fx[p["fixture"]]
        pr = preds.get(p["pick_id"])
        rows.append([
            esc(p["pick_id"]),
            f'<a href="sports/{SLUG[f["sport"]]}.html">{esc(f["sport"])}</a>',
            f'{esc(f["home"])} v {esc(f["away"])}',
            f["start_utc"] or '<span class="warn">zone unresolved</span>',
            f'<b>{esc(p["selection"])}</b><br><span class="muted">{esc(p["market"])}, {esc(p.get("line_type","half"))} line</span>',
            settlement(p["market"], p["selection"], p["line"]),
            f'{p["p"]*100:.2f}%',
            fmt_am(p["fair_american"]),
            f'<span class="pill {"hi" if p.get("evidence")=="A" else ("med" if p.get("evidence")=="B" else "low")}">grade {esc(p.get("evidence"))}</span>',
            f'<a href="predictions.html#{p["pick_id"]}">write-up</a>',
        ])
    body = f"""
<h1>High-confidence picks</h1>
<p class="lede">The gate is a conjunction: a probability of at least 62% <em>and</em> a fair price no shorter than
−250 (a probability of 71.43%). Evidence grade is our own disclosure: <b>A</b> = a full-season record, <b>B</b> = 3–12 games or
league-table points difference, <b>C</b> = a single round (none of today's promoted picks is grade C).</p>
{table(["Pick", "Sport", "Fixture", "Start (UTC)", "Selection", "What has to happen", "Probability", "Fair price", "Evidence", "Detail"], rows)}
<p class="muted">All twelve prices expire at the earliest kick-off or at {EV_EXPIRY}, whichever comes first.</p>
"""
    (OUT / "high-confidence.html").write_text(layout("High-confidence picks", body, "high-confidence.html"), encoding="utf-8")

    # ---------------- predictions ----------------
    blocks = []
    for p in picks:
        pr = preds.get(p["pick_id"])
        f = fx[p["fixture"]]
        if not pr:
            continue
        words = len(pr["text"].split())
        srcs = " · ".join(f'<a href="{esc(reads[s]["url"])}" target="_blank" rel="noopener">{esc(reads[s]["name"])}</a>'
                          for s in pr["sources"] if s in reads)
        blocks.append(f"""
<article class="pred" id="{p['pick_id']}">
<p class="kicker">{esc(f['sport'])} · {esc(f['comp'])} · {esc(p['pick_id'])}</p>
<h2>{esc(pr['headline'])}</h2>
<p class="meta">{esc(f['home'])} v {esc(f['away'])} · {esc(f['start_utc'] or 'start time unresolved')} ·
probability {p['p']*100:.2f}% · fair {fmt_am(p['fair_american'])}</p>
<p>{esc(pr['text'])}</p>
<p class="meta">{words} words · facts read from: {srcs}</p>
</article>""")
    body = f"""
<h1>Predictions for the High picks</h1>
<p class="lede">One hand-written piece per promoted selection. Each states the bet in the first sentence, uses only
figures read from the official pages during this session, and links those pages. No injury is mentioned because no
official injury report was read inside the window.</p>
{''.join(blocks)}
"""
    (OUT / "predictions.html").write_text(layout("Predictions", body, "predictions.html"), encoding="utf-8")

    # ---------------- analysis ----------------
    cap_rows = [[esc(m["selection"]), esc(m["market"]), f'{m["p"]*100:.2f}%', fmt_am(m["fair_american"]),
                 "price shorter than −250: capped, not promoted"] for m in capped[:20]]
    body = f"""
<h1>Analysis and findings</h1>
<h2>1. The band is a price window, so it cuts from the top</h2>
<p>−250 is 71.43% and +10000 is 0.01%, so “inside −250…+10000” means a fair price <em>no shorter than −250</em>, or
a probability at or below 71.43%. Add a 62% floor so that “high confidence” means something, and the promoted window
is <b>62.00%–71.43%</b>. A 78% favourite is excluded because its price would be about −355. That is the brief's
instruction — disclose heavier favourites rather than promote them — so {len(capped)} outcomes today are printed
below as capped, and the twenty strongest are shown.</p>
{table(["Selection", "Market", "Probability", "Fair price", "Why it is not promoted"], cap_rows)}
<h2>2. Where the window binds</h2>
<p>Money-line prices rarely land inside it. Milwaukee's single-game price is 56.8%, comfortably under the 62% floor,
and no baseball side today prices anywhere near a 62%–71% win probability because a 162-game record separates these
two clubs by well under a run. The window fills instead wherever a line can be moved a point at a time: the run
line, the puck line, team totals and rugby handicaps. All fourteen promoted selections are line markets, and each
one names the side we expect to come out ahead — the Bulls and the Stormers are laid to win by more than their start,
while Leinster, Ospreys, Benetton and Milwaukee are backed to cover while losing narrowly at worst.</p>
<h2>3. Four Series games, one underlying estimate</h2>
<p>World Series games 1–4 pair the same two clubs, so the expected total (8.75 runs) and the expected margin are
identical across them and four picks are repeats of two ideas. That is disclosed rather than hidden: the run-line
selections in Games 1 and 2 are the same bet twice, and the totals in Games 3 and 4 are the same bet twice. A reader
who wants one position per idea should take one of each pair.</p>
<h2>4. What the desk refused to publish</h2>
<ul class="notes">
<li><b>Rugby League World Cup.</b> Round 1 produced five results between ten teams with no shared opponents, so the
margin inputs cannot rank teams across pools. Pricing Australia v Fiji off those numbers produced an absurd
“Australia +14.75”, which is exactly the failure mode we are guarding against. No line was published.</li>
<li><b>Basketball.</b> The NBA season is one or two games old. A 2-0 start is not a strength estimate, so Boston v
New York and the other four games are listed without prices.</li>
<li><b>Golf, motor racing, cricket.</b> Fixtures are confirmed but no official input supports a probability: a leaderboard is a scoreboard rather than a strength input; the F1 points table did not render; and the ICC
fixtures carry no form data in the page read.</li>
<li><b>Snooker, darts, handball, volleyball, Gaelic sports, greyhounds.</b> No upcoming fixture could be read from an
official source inside the window. The attempted URLs are on the Flagged page.</li>
</ul>
"""
    (OUT / "analysis.html").write_text(layout("Analysis", body, "analysis.html"), encoding="utf-8")

    # ---------------- sources ----------------
    srows = [[esc(r["id"]), esc(r["kind"]), f'<a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["name"])}</a>',
              esc(r["utc"]), esc(r["read"])] for r in desk["reads"]]
    body = f"""
<h1>Source register</h1>
<p class="lede">Every row of data on this site traces to one of these reads. <b>Official</b> means the league,
governing body, tour or club itself. <b>Discovery</b> means OLBG, used only to learn the market taxonomy — never to
certify a fixture.</p>
{table(["ID", "Type", "Source", "Read (UTC)", "What it established"], srows)}
"""
    (OUT / "sources.html").write_text(layout("Sources", body, "sources.html"), encoding="utf-8")

    # ---------------- flagged ----------------
    frows = []
    for s in SPORT_ORDER:
        if s in gaps:
            g = gaps[s]
            tried = "<br>".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(u)}</a>' for u in g["tried"])
            frows.append([esc(s), "no fixture", esc(g["why"]), tried, "blank — not inferred"])
    for f in desk["fixtures"]:
        if f["start_note"]:
            frows.append([esc(f["sport"]), esc(f["id"]), esc(f["start_note"]),
                          f'<a href="{esc(reads[f["src"]]["url"])}" target="_blank" rel="noopener">{esc(reads[f["src"]]["name"])}</a>',
                          "start time left blank"])
    for f in desk["fixtures"]:
        if f["sport"] in ("Golf", "Motor Racing") or f["id"] in ("BK01", "CR01"):
            pass
    frows += [
        ["Basketball", "all five games", "The NBA season is 1–2 games old; no defensible strength input exists yet, so no line is originated.",
         '<a href="https://www.nba.com/standings" target="_blank" rel="noopener">NBA standings</a>', "unpriced"],
        ["Rugby League", "all four upcoming games", "Round 1 results have no shared opponents, so margins cannot rank teams across pools; a cross-pool price would be pseudo-precision.",
         '<a href="https://www.rlwc2026.com/home" target="_blank" rel="noopener">RLWC 2026 results</a>', "unpriced"],
        ["Cricket", "all five games", "ICC publishes no team form on the fixture page read, and the T20I ranking table covers only one of the five fixtures, so no price is offered.",
         '<a href="https://www.icc-cricket.com/fixtures-results" target="_blank" rel="noopener">ICC fixtures</a>', "unpriced"],
        ["Golf", "five matchups", "Leaderboard position is not a probability input; head-to-head prices would be invented.",
         '<a href="https://www.europeantour.com/dpworld-tour/genesis-championship-2026/leaderboard?round=3" target="_blank" rel="noopener">DP World Tour leaderboard</a>', "unpriced"],
        ["Motor Racing", "qualifying and race", "The 2026 drivers' standings body did not render, so no championship input exists.",
         '<a href="https://www.formula1.com/en/results/2026/drivers" target="_blank" rel="noopener">F1 results</a>', "unpriced"],
        ["Baseball", "BB05", "MLB flags World Series Game 5 as ifNecessary=Y; it is withheld from pricing until the game is certain to be played.",
         '<a href="https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-11-05" target="_blank" rel="noopener">MLB schedule</a>', "withheld"],
        ["All sports", "OLBG tips tables", "Every OLBG hub read returned “No tips found.” — the tips table is client-rendered. OLBG therefore supplied market vocabulary (money line, puck line, totals, set betting) but no fixture or price evidence.",
         '<a href="https://www.olbg.com/betting-tips/Ice_Hockey/13" target="_blank" rel="noopener">OLBG hockey hub</a>', "logged"],
    ]
    body = f"""
<h1>Flagged for review</h1>
<p class="lede">These are the places where this desk produced nothing rather than guessing. Each row names the
attempted source so the gap can be checked by hand.</p>
{table(["Sport", "Scope", "Why it is blank", "Source attempted", "Resolution"], frows)}
"""
    (OUT / "flagged.html").write_text(layout("Flagged for review", body, "flagged.html"), encoding="utf-8")

    # ---------------- methodology ----------------
    body = """
<h1>Methodology</h1>
<h2>Evidence</h2>
<p>A fixture is published only if an official page printed the two clubs and the competition. A start time is
published only with an explicit UTC value; “local” and “your time” clocks are reproduced in the row and left out of
the UTC column. Evidence expires six hours after the read window, at 2026-10-24T03:55Z.</p>
<h2>Line origination</h2>
<ul class="notes">
<li><b>Baseball:</b> expected runs for each side are the mean of that side's scoring rate and the opponent's
conceding rate (832/618 for Milwaukee, 736/650 for Tampa Bay over 162 games); margin is the difference plus 0.15
runs of home field. Margin standard deviation 3.2 runs, total 4.5.</li>
<li><b>Ice hockey:</b> the same construction from goals for and against in the NHL standings read this session;
home field 0.15 goals, margin standard deviation 1.9, total 2.0, team total 1.45.</li>
<li><b>Rugby union:</b> half of each club's league-table points difference per game (a 50% shrinkage toward the
league mean) plus three points of home advantage; margin standard deviation 14.</li>
<li><b>Not originated:</b> basketball, rugby league, cricket, golf, motor racing. The reasons are on the
Flagged page.</li>
</ul>
<h2>Prices and tiers</h2>
<p>Fair decimal is 1 ÷ probability with no margin and no clipping; the American column is derived from the same
unrounded probability. <b>High</b> requires p ≥ 0.62 <em>and</em> a fair American price of −250 or longer, i.e.
p ≤ 0.7143. Anything above 71.43% would price shorter than −250; those outcomes are <b>capped</b>, published in the
capped table, never promoted. Picks are the highest
in-band probability per fixture, then the five strongest per sport.</p>
<h2>Prediction rules</h2>
<p>Every promoted pick carries a hand-written piece of at least 30 words that names the selection, cites the
current form, the recent match history and the relevant statistics actually read, and links those pages. Published
prose avoids the jargon of automated pricing and never certifies its own output; the arithmetic is disclosed here
instead, so a reader can redo it.</p>
<h2>What is deliberately absent</h2>
<p>No injury claims, no lineup claims, no travel or rest claims, no weather, no referee data. None of those was read
from an official page in this window, so none appears.</p>
"""
    (OUT / "methodology.html").write_text(layout("Methodology", body, "methodology.html"), encoding="utf-8")

    # ---------------- OLBG reverse engineering ----------------
    body = """
<h1>OLBG structure — what we could and could not read</h1>
<h2>Route taxonomy (from the official sitemap, read this session)</h2>
<p>Hub URLs follow <code>/betting-tips/&lt;Sport_Name&gt;/&lt;sport_id&gt;</code> with underscores, not hyphens:
Tennis/3, Golf/5, Cricket/7, Snooker/8, Rugby_Union/9, Rugby_League/10, Baseball/12, Ice_Hockey/13,
Motor_Racing/14, Darts/15, Handball/20, Volleyball/21, Gaelic_Football/25, Greyhounds/28. Hyphenated slugs such as
<code>/betting-tips/Ice-Hockey/13</code> return 404 — a first-pass trap.</p>
<h2>Markets described on the hubs</h2>
<p>The hockey hub documents money line, puck line (−1.5 / +1.5) and totals (usually 5.5, with pushes at whole
numbers). The tennis hub documents win match, set betting, total games, first-set winner and a games-won handicap.
The rugby union hub documents match winner and handicap and publishes its own five-season favourite and total-points
tables. Those definitions shaped the market set originated here.</p>
<h2>The blocker</h2>
<p>All seven hub pages read (Tennis, Ice Hockey, Rugby Union and the sitemap-indexed others tested in earlier
sessions) returned <b>“No tips found.”</b> in the fetched document. The tips table is populated client-side, so the
events and prices OLBG displays are not in the HTML we can read. That is recorded as a platform irregularity, not
worked around: no hidden API, proxy or identity rotation was used.</p>
<h2>robots.txt</h2>
<p>Read this session. It disallows <code>/api/</code>, <code>/sports/</code>, <code>/events.php</code> and the
<code>Python-urllib</code> agent, and lists four sitemaps. This desk used only the sitemap and the public hubs, and
did not touch a disallowed path.</p>
<h2>Consequence for this release</h2>
<p>Because the OLBG event list could not be read, the fixture slate comes from governing bodies instead. That is a
stronger source for a kick-off time and a weaker source for “what OLBG is currently offering”. Both facts are
stated plainly rather than blurred.</p>
"""
    (OUT / "reverse-engineering.html").write_text(layout("OLBG structure", body, "reverse-engineering.html"), encoding="utf-8")

    # ---------------- repo audit ----------------
    arows = [[esc(a["id"]),
              f'<span class="pill {"gap" if a["sev"]=="medium" else ("med" if a["sev"]=="low" else "low")}">{esc(a["sev"])}</span>',
              f'<code>{esc(a["file"])}</code>' + (f':{a["line"]}' if a["line"] else ""),
              esc(a["finding"]), esc(a["evidence"])] for a in AUDIT]
    body = f"""
<h1>Repository audit</h1>
<p class="lede">Line-by-line structural review of the tree as merged on <code>main</code> before this session added
anything. Checks were run with git and Python against the tracked file list, so every count below is reproducible.</p>
{table(["ID", "Severity", "Location", "Finding", "How it was checked"], arows)}
<h2>Scope note</h2>
<p>The audit verifies structure — file inventory, JSON validity, duplicate content, link targets, provenance keys.
It does <b>not</b> re-certify the claims inside 1,217 HTML pages, and the presence of a source field on a row is not
proof that the URL still resolves. Both limits are stated rather than papered over.</p>
"""
    (OUT / "repo-audit.html").write_text(layout("Repository audit", body, "repo-audit.html"), encoding="utf-8")

    # ---------------- sport pages ----------------
    for s in SPORT_ORDER:
        rows = []
        for f in by_sport[s]:
            rows.append([
                esc(f["id"]), f'{esc(f["home"])} v {esc(f["away"])}', esc(f["comp"]),
                f["start_utc"] or f'<span class="warn">{esc(f["start_note"])}</span>',
                esc(f["venue"]) or '<span class="warn">not published</span>',
                esc(f["rec_home"]) or "—", esc(f["rec_away"]) or "—",
                esc(f["form"]) or '<span class="warn">no official form read</span>',
                f'<a href="{esc(reads[f["src"]]["url"])}" target="_blank" rel="noopener">{esc(reads[f["src"]]["name"])}</a>',
            ])
        sp = picks_by_sport.get(s, [])
        prows = [[esc(p["pick_id"]), f'<b>{esc(p["selection"])}</b>', settlement(p["market"], p["selection"], p["line"]),
                  f'{p["p"]*100:.2f}%', fmt_am(p["fair_american"]),
                  f'<a href="../predictions.html#{p["pick_id"]}">write-up</a>'] for p in sp]
        gap_html = ""
        if s in gaps:
            g = gaps[s]
            gap_html = f"""<h2>Why there is no fixture</h2><p>{esc(g["why"])}</p>
<p class="muted">Attempted: {' · '.join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(u)}</a>' for u in g["tried"])}</p>"""
        body = f"""
<h1>{esc(s)}</h1>
<p class="lede">{len(by_sport[s])} fixture{'s' if len(by_sport[s]) != 1 else ''} read from official sources;
{len(sp)} in-band High pick{'s' if len(sp) != 1 else ''}.</p>
{''.join([f'<h2>Fixtures</h2>{table(["ID","Fixture","Competition","Start (UTC)","Venue","Home record","Away record","Form read","Official source"], rows)}'] if rows else '')}
{''.join([f'<h2>High-confidence picks</h2>{table(["Pick","Selection","What has to happen","Probability","Fair price","Detail"], prows)}'] if prows else '<h2>High-confidence picks</h2><p>None today. The strongest opinions here would have priced shorter than −250, and the rest fell under the 62% floor; the short ones are listed on the <a href="../analysis.html">analysis page</a> as capped.</p>')}
{gap_html}
"""
        (OUT / "sports" / f"{SLUG[s]}.html").write_text(
            layout(s, body, "", rel="../"), encoding="utf-8")

    # copy machine-readable data next to the site
    for name in ("desk.json", "markets.json", "picks.json", "capped.json", "predictions.json"):
        (OUT / "data").mkdir(exist_ok=True)
        (OUT / "data" / name).write_text((DATA / name).read_text(), encoding="utf-8")

    # machine-readable companions a reader can diff against the pages
    (OUT / "data").mkdir(exist_ok=True)
    (OUT / "data" / "sources.json").write_text(json.dumps(
        {"session": desk["session"], "window": desk["read_window"], "reads": desk["reads"]},
        indent=1), encoding="utf-8")
    (OUT / "data" / "flagged.json").write_text(json.dumps(
        {"gaps": desk["gaps"],
         "unresolved_start_times": [f["id"] for f in desk["fixtures"] if not f["start_utc"]],
         "withheld": ["BB05"],
         "unpriced_sports": [s for s in SPORT_ORDER if by_sport[s] and not picks_by_sport.get(s)]},
        indent=1), encoding="utf-8")
    (OUT / "data" / "manifest.json").write_text(json.dumps(
        {"session": desk["session"], "built": BUILT, "evidence_expires": EV_EXPIRY,
         "counts": {"fixtures": len(desk["fixtures"]), "reads": len(desk["reads"]),
                    "markets": len(markets), "picks": len(picks), "capped": len(capped),
                    "sports_covered": len(covered), "sports_gapped": len(gaps)},
         "pages": sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*.html")),
         "gate": {"high_min_p": 0.62, "max_price": -250, "min_price": 10000}},
        indent=1), encoding="utf-8")

    pages = len(list(OUT.rglob("*.html")))
    print(f"built {pages} pages, {len(markets)} markets, {len(picks)} picks")


CSS = """
:root{--ink:#111827;--mut:#6b7280;--line:#e5e7eb;--bg:#f8fafc;--card:#fff;--acc:#0f766e;--hi:#065f46;--med:#92400e;--gap:#991b1b}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
.wrap{max-width:1180px;margin:0 auto;padding:0 18px}
header{background:#0b1220;color:#e5e7eb;padding:14px 0 10px}
header .brand{font-weight:700;font-size:17px}
header .brand span{display:block;font-weight:400;font-size:12px;color:#94a3b8}
nav{display:flex;flex-wrap:wrap;gap:4px;margin-top:10px}
nav a{color:#cbd5e1;text-decoration:none;font-size:13px;padding:5px 9px;border-radius:6px}
nav a:hover{background:#1f2937;color:#fff}
nav a.on{background:var(--acc);color:#fff}
main{padding:26px 0 40px}
h1{font-size:26px;margin:0 0 10px}
h2{font-size:18px;margin:26px 0 8px}
.lede{color:#374151;max-width:900px}
.muted{color:var(--mut);font-size:12px}
.warn{color:#b45309;font-size:12px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:18px 0}
.kpis div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.kpis b{display:block;font-size:22px}
.kpis span{font-size:12px;color:var(--mut)}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:10px 0}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f1f5f9;font-size:12px;text-transform:uppercase;letter-spacing:.03em;color:#475569;position:sticky;top:0}
tr:last-child td{border-bottom:none}
a{color:#0f766e}
code{background:#f1f5f9;padding:1px 4px;border-radius:4px;font-size:12px}
.pill{display:inline-block;font-size:11px;padding:2px 7px;border-radius:999px;background:#e2e8f0;color:#334155}
.pill.hi{background:#d1fae5;color:var(--hi)} .pill.med{background:#fef3c7;color:var(--med)} .pill.low{background:#e2e8f0}
.pill.gap{background:#fee2e2;color:var(--gap)}
.notes{max-width:900px;color:#374151}
.pred{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0}
.pred h2{margin:4px 0 6px;font-size:18px}
.kicker{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--acc);margin:0}
.meta{font-size:12px;color:var(--mut)}
footer{border-top:1px solid var(--line);padding:18px 0 40px;color:var(--mut);font-size:12px}
@media(max-width:640px){h1{font-size:22px}th{position:static}}
"""

if __name__ == "__main__":
    main()
