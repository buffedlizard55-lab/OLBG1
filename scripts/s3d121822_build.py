"""Render the 3d121822 dashboard.  python3 scripts/s3d121822_build.py"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import s3d121822_data as D
import s3d121822_model as M

OUT = M.OUT
DATA = M.DATA


def fx_index():
    return {f["id"]: f for f in D.fixture_rows()}


def sorted_picks(prices):
    rows = [(fid, p) for fid, p in prices.items() if p["written"] and p["side"]]
    return sorted(rows, key=lambda kv: -kv[1]["p_pick"])


# ------------------------------------------------------------------ overview
def overview(prices, fixtures):
    picks = sorted_picks(prices)
    priced = len(prices)
    markets = sum(len(M.market_rows(fixtures[fid], prices[fid])) for fid in prices)
    cards = "".join(f"""
    <article class="pick">
      <div class="where">{M.esc(fixtures[fid]['sport_name'])} · {M.esc(fixtures[fid]['comp'])}</div>
      <div class="sel">{M.esc(p['selection'])}</div>
      <div class="mkt">{M.esc(fixtures[fid]['a'])} vs {M.esc(fixtures[fid]['b'])} · {M.kickoff(fixtures[fid])}</div>
      <div class="foot">
        <span class="price">{p['decimal']:.2f} ({M.esc(p['american'])})</span>
        <span class="muted">fair price · {p['p_pick']*100:.1f}%</span>
        {M.conf_chip(p['conf'])}
        <a href="predictions.html#{M.esc(fid)}">Read the analysis →</a>
      </div>
    </article>""" for fid, p in picks)

    summary_rows = []
    for fid, p in sorted(prices.items(), key=lambda kv: -kv[1]["p_pick"]):
        fx = fixtures[fid]
        if p["written"] and p["side"]:
            pick_cell = (f'<div class="pickcell"><b>{M.esc(p["selection"])}</b>'
                         f'<small>{M.decimal_text(p["decimal"])} · {M.esc(p["american"])}</small></div>')
            conf = M.conf_chip(p["conf"])
        else:
            pick_cell = ('<div class="pickcell"><b class="blank">No selection</b>'
                         '<small>price within five points of even</small></div>')
            conf = M.conf_chip("")
        summary_rows.append(
            f"<tr><td>{M.esc(fx['sport_name'])}</td>"
            f"<td><a href=\"matches.html#{M.esc(fid)}\">{M.esc(fx['a'])} vs {M.esc(fx['b'])}</a><br>"
            f"<span class='small muted'>{M.esc(fx['ko'])}</span></td>"
            f"<td>{pick_cell}</td><td>{conf}</td>"
            f"<td>{M.src_link('olbg-' + ('basketball' if fx['sport']=='basketball' else 'hockey'))}</td></tr>")

    body = f"""
<h1>Today's picks, in one place</h1>
<p class="lede">One dashboard for the sports you asked us to cover. Every match below was
listed on OLBG today, every price is ours, and every fact links to the league, tour or
governing body that published it. Where we could not confirm an input we left the cell
blank and said why — we did not fill it in.</p>

<div class="kpis">
  <div class="kpi"><b>15</b><small>sports scanned on OLBG</small></div>
  <div class="kpi"><b>{len(fixtures)}</b><small>matches listed</small></div>
  <div class="kpi"><b>{priced}</b><small>matches with our own prices</small></div>
  <div class="kpi"><b>{markets}</b><small>market prices issued</small></div>
  <div class="kpi"><b>{len(picks)}</b><small>written predictions</small></div>
  <div class="kpi"><b>0</b><small>High picks today</small></div>
</div>

<div class="note">
  <strong>Start here.</strong> The five strongest calls are the cards below. The full list is on
  <a href="picks.html">Picks</a>, every match we found is on <a href="matches.html">Matches</a>,
  and the reasoning behind each call is on <a href="predictions.html">Written predictions</a>.
  Anything we could not confirm is listed on <a href="flagged.html">Flagged for review</a>.
</div>

<h2>Executive summary — the strongest calls</h2>
<div class="picks">{cards}</div>

<div class="warn">
  <strong>No High-confidence pick is published today, and that is deliberate.</strong>
  The brief sets two rules that overlap in a narrow window: a pick needs better than a 70%
  chance, and its price must be no shorter than −250. A price of −250 is itself 71.4%, so
  "High" only exists between 70.0% and 71.4%. Today's strongest call, New Jersey at about
  72.7%, prices near −267 and therefore falls outside the window. It is shown as Medium with
  the arithmetic on the page rather than relabelled to fit. <a href="flagged.html#F-3D-09">See F-3D-09</a>.
</div>

<h2>Every priced match</h2>
<table>
<thead><tr><th>Sport</th><th>Match</th><th>Our pick</th><th>Confidence</th><th>Discovery source</th></tr></thead>
<tbody>{''.join(summary_rows)}</tbody>
</table>
<p class="small muted">Prices are fair (margin-free) decimal and American equivalents of our own
probability estimate. They are research estimates, not quotes you can take to a bookmaker.</p>

<h2>What the labels mean</h2>
<div class="grid2">
  <div class="card">
    <h3 style="margin-top:0">Confidence</h3>
    <ul class="tight small">
      <li><span class="chip high">High</span> 70.0%–71.4% fair and inside the −250…+10000 window.</li>
      <li><span class="chip med">Medium</span> 55%–70%, or stronger than −250 and therefore outside the window.</li>
      <li><span class="chip low">Low</span> a marginal edge below 55%.</li>
      <li><span class="chip none">No pick</span> the price is within five points of even; we do not force a side.</li>
    </ul>
  </div>
  <div class="card">
    <h3 style="margin-top:0">Where things live</h3>
    <ul class="tight small">
      <li><a href="picks.html">Picks</a> — every selection, one row each.</li>
      <li><a href="matches.html">Matches</a> — all {len(fixtures)} listings, priced or not.</li>
      <li><a href="sports/index.html">Sports</a> — one page per sport, with the missing inputs named.</li>
      <li><a href="flagged.html">Flagged for review</a> — every blank value and why it is blank.</li>
    </ul>
  </div>
</div>
"""
    return M.page("Today's picks", body, "index.html")


# ------------------------------------------------------------------ picks
def picks_page(prices, fixtures):
    picks = sorted_picks(prices)
    rows = []
    for fid, p in picks:
        fx = fixtures[fid]
        rows.append(
            f"<tr><td>{M.esc(fx['sport_name'])}</td>"
            f"<td><a href=\"matches.html#{M.esc(fid)}\">{M.esc(fx['a'])} vs {M.esc(fx['b'])}</a><br>"
            f"<span class='small muted'>{M.esc(fx['comp'])}</span></td>"
            f"<td>{M.kickoff(fx)}</td>"
            f"<td class='pickcell'><b>{M.esc(p['selection'])}</b><small>{M.esc(p['conf_reason'])}</small></td>"
            f"<td class='num'>{p['decimal']:.2f}<br><span class='small muted'>{M.esc(p['american'])}</span></td>"
            f"<td class='num'>{p['p_pick']*100:.1f}%</td>"
            f"<td>{M.conf_chip(p['conf'])}</td>"
            f"<td><a href=\"predictions.html#{M.esc(fid)}\">Analysis</a> · "
            f"<a href=\"{M.esc(fx['olbg'])}\" rel=\"noopener\">OLBG card</a></td></tr>")
    no_pick = []
    for fid, p in sorted(prices.items(), key=lambda kv: -kv[1]["p_pick"]):
        if p["written"] and p["side"]:
            continue
        fx = fixtures[fid]
        no_pick.append(
            f"<tr><td>{M.esc(fx['sport_name'])}</td>"
            f"<td>{M.esc(fx['a'])} vs {M.esc(fx['b'])}</td><td>{M.kickoff(fx)}</td>"
            f"<td class='num'>{M.decimal_text(p['calc']['p_home'])}</td>"
            f"<td class='num'>{p['calc']['p_home']*100:.1f}%</td>"
            f"<td class='blank'>No selection — {max(p['calc']['p_home'], 1-p['calc']['p_home'])*100:.1f}% is too close to even</td>"
            f"<td><a href=\"{M.esc(fx['olbg'])}\" rel=\"noopener\">OLBG card</a></td></tr>")

    body = f"""
<h1>Picks</h1>
<p class="lede">{len(picks)} selections are published today, each with a written analysis. Every
row shows the exact selection, the market, our own fair price and the confidence label. A pick is
never published without the written reasoning behind it.</p>

<table>
<thead><tr><th>Sport</th><th>Match</th><th>Kick-off</th><th>Pick</th><th>Our price</th>
<th>Fair chance</th><th>Confidence</th><th>Where</th></tr></thead>
<tbody>{''.join(rows) or '<tr><td colspan="8" class="blank">No selection met the threshold.</td></tr>'}</tbody>
</table>

<h2>Matches we priced but did not pick</h2>
<p class="lede small">The price is published for transparency; the two sides are close enough that
we will not manufacture an edge.</p>
<table>
<thead><tr><th>Sport</th><th>Match</th><th>Kick-off</th><th>Home price</th><th>Home chance</th>
<th>Why no pick</th><th>Source</th></tr></thead>
<tbody>{''.join(no_pick)}</tbody>
</table>
"""
    return M.page("Picks", body, "picks.html")


# ------------------------------------------------------------------ matches
def matches_page(fixtures):
    rows = []
    for sp in D.SPORTS:
        for fx in [f for f in fixtures.values() if f["sport"] == sp["key"]]:
            priced = fx["id"] in PRICES
            status = ('<span class="chip med">priced</span>' if priced
                      else '<span class="chip none">unpriced</span>')
            rows.append(
                f"<tr id=\"{M.esc(fx['id'])}\"><td>{M.esc(sp['name'])}</td>"
                f"<td>{M.esc(fx['comp'])}</td>"
                f"<td><b>{M.esc(fx['a'])}</b> vs <b>{M.esc(fx['b'])}</b></td>"
                f"<td>{M.kickoff(fx)}</td><td>{status}</td>"
                f"<td><a href=\"{M.esc(fx['olbg'])}\" rel=\"noopener\">OLBG</a></td></tr>")
    body = f"""
<h1>Matches</h1>
<p class="lede">Every fixture this desk found on OLBG for the 15 sports you asked us to cover, in
one table. {sum(1 for f in fixtures.values() if f['id'] in PRICES)} are priced; the rest are listed
with the reason they are not on their sport page. The clock column is reproduced exactly as OLBG
prints it — OLBG does not publish a timezone, so no conversion is attempted.</p>
<div class="warn"><strong>Clock warning.</strong> A card reading "Today 19:30" is OLBG's own clock,
not UTC. Where a league feed supplied an exact UTC start, it is printed underneath in small text.
Never assume the OLBG clock is your local time.</div>
<table>
<thead><tr><th>Sport</th><th>Competition</th><th>Match</th><th>Clock (as listed)</th>
<th>Price status</th><th>Card</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
"""
    return M.page("Matches", body, "matches.html")


# ------------------------------------------------------------------ predictions
def predictions_page(fixtures, prices):
    cards = []
    for fid, p in sorted_picks(prices):
        fx = fixtures[fid]
        pred = D.PREDICTIONS[fid]
        words = len(pred["text"].split())
        ev = " · ".join(M.src_link(s) for s in pred["evidence"])
        cards.append(f"""
<article class="pred" id="{M.esc(fid)}">
  <h3>{M.esc(fx['a'])} vs {M.esc(fx['b'])} <span class="muted small">· {M.esc(fx['sport_name'])} · {M.esc(fx['comp'])}</span></h3>
  <div class="small muted">{M.kickoff(fx)}</div>
  <p class="sel" style="margin:10px 0 6px">{M.esc(pred['selection'])}</p>
  <p class="body">{M.esc(pred['text'])}</p>
  <div class="small" style="margin-top:8px">
    {M.conf_chip(p['conf'])} <span class="muted">our fair price {p['decimal']:.2f} ({M.esc(p['american'])}) · {p['p_pick']*100:.1f}% · {words} words</span>
  </div>
  <div class="src">Evidence read this session: {ev} · <a href="{M.esc(fx['olbg'])}" rel="noopener">OLBG card</a></div>
</article>""")
    body = f"""
<h1>Written predictions</h1>
<p class="lede">One written analysis per published pick. Each is original prose of at least 30
words, names the selection in plain language, states the current record, and says explicitly which
inputs were not captured. No sentence here rests on a fact that is not on the
<a href="sources.html">sources page</a>.</p>
{''.join(cards)}
<div class="note"><strong>Why some sports have no prediction.</strong> A prediction needs a
confirmed input for both sides. For tennis, handball, volleyball, cricket, Gaelic games and
greyhounds, no official table, ranking or availability was readable in this session, so those
sports carry fixtures and links but no pick. The exact missing input is named on each
<a href="sports/index.html">sport page</a>.</div>
"""
    return M.page("Written predictions", body, "predictions.html")


# ------------------------------------------------------------------ markets
def markets_page(prices, fixtures):
    blocks = []
    for fid, p in sorted(prices.items(), key=lambda kv: -kv[1]["p_pick"]):
        fx = fixtures[fid]
        rows = "".join(
            f"<tr><td>{M.esc(r['market'])}</td><td><b>{M.esc(r['selection'])}</b></td>"
            f"<td class='num'>{r['price']:.2f}</td><td class='num'>{M.esc(r['american'])}</td>"
            f"<td class='num'>{r['prob']*100:.1f}%</td><td class='small muted'>{M.esc(r['basis'])}</td>"
             f"<td><a href=\"{M.esc(fx['olbg'])}\" rel=\"noopener\">Card</a></td></tr>"
            for r in M.market_rows(fx, p))
        blocks.append(f"""
<h2 id="{M.esc(fid)}">{M.esc(fx['a'])} vs {M.esc(fx['b'])}
  <span class="muted small">· {M.esc(fx['sport_name'])}</span></h2>
<table><thead><tr><th>Market</th><th>Selection</th><th>Price</th><th>American</th>
<th>Fair chance</th><th>Input used</th><th>Card</th></tr></thead><tbody>{rows}
<tr><td>Game Totals</td><td class="blank">withheld</td><td class="blank">—</td><td class="blank">—</td>
<td class="blank">—</td><td class="small muted">no sourced season scoring rate yet; see F-3D-06</td>
<td><a href="{M.esc(fx['olbg'])}" rel="noopener">Card</a></td></tr>
</tbody></table>""")
    body = f"""
<h1>Markets</h1>
<p class="lede">Every market we originated, fixture by fixture: moneyline, handicap and the total
we deliberately withheld. Handicap numbers are our own model lines, not bookmaker offers. Prices
are margin-free, so they are longer than a bookmaker's on both sides.</p>
<div class="note"><strong>Markets we investigated and did not price.</strong> Match totals need a
sourced scoring rate. Player props, correct score and first-scorer markets need lineup data. None
of those inputs was available today, so none is priced.</div>
{''.join(blocks)}
"""
    return M.page("Markets", body, "markets.html")


# ------------------------------------------------------------------ sports
def sports_index(fixtures, prices):
    rows = []
    for sp in D.SPORTS:
        fxs = [f for f in fixtures.values() if f["sport"] == sp["key"]]
        priced = [f for f in fxs if f["id"] in prices]
        picks = [f for f in fxs if prices.get(f["id"], {}).get("written")]
        status = ("priced" if picks else ("priced, no pick" if priced else "no price"))
        cls = "med" if picks else ("low" if priced else "none")
        rows.append(
            f"<tr><td><a href=\"{M.esc(sp['key'])}.html\"><b>{M.esc(sp['name'])}</b></a></td>"
            f"<td class='num'>{len(fxs)}</td><td class='num'>{len(priced)}</td>"
            f"<td class='num'>{len(picks)}</td>"
            f"<td><span class='chip {cls}'>{status}</span></td>"
            f"<td class='small muted'>{M.esc(sp['gap'][:110])}{'…' if len(sp['gap'])>110 else ''}</td>"
            f"<td><a href=\"{M.esc(sp['route'])}\" rel=\"noopener\">OLBG hub</a></td></tr>")
    body = f"""
<h1>Sports</h1>
<p class="lede">One page per sport, in the order you listed them. Each page shows the matches we
found, the markets we looked at, the price where an input existed, and the exact input that is
missing where it did not.</p>
<table><thead><tr><th>Sport</th><th>Matches</th><th>Priced</th><th>Picks</th><th>Status</th>
<th>Today's limit</th><th>Source</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
"""
    return M.page("Sports", body, "sports/index.html", prefix="../")


def sport_page(sp, fixtures, prices):
    fxs = [f for f in fixtures.values() if f["sport"] == sp["key"]]
    rows = []
    for fx in fxs:
        p = prices.get(fx["id"])
        if p and p["written"] and p["side"]:
            pick = f'<b>{M.esc(p["selection"])}</b><br>{M.conf_chip(p["conf"])} {p["decimal"]:.2f}'
        elif p:
            pick = '<span class="blank">No selection</span><br><span class="small muted">price too close to even</span>'
        else:
            pick = '<span class="blank">Not priced</span><br><span class="small muted">input missing</span>'
        rows.append(
            f"<tr id=\"{M.esc(fx['id'])}\"><td>{M.esc(fx['comp'])}</td>"
            f"<td><b>{M.esc(fx['a'])}</b> vs <b>{M.esc(fx['b'])}</b></td>"
            f"<td>{M.kickoff(fx)}</td><td>{pick}</td>"
            f"<td><a href=\"{M.esc(fx['olbg'])}\" rel=\"noopener\">Card</a></td></tr>")
    detail = ""
    for fx in fxs:
        p = prices.get(fx["id"])
        if not p:
            continue
        mrows = "".join(
            f"<tr><td>{M.esc(r['market'])}</td><td>{M.esc(r['selection'])}</td>"
            f"<td class='num'>{r['price']:.2f}</td><td class='num'>{r['prob']*100:.1f}%</td>"
            f"<td><a href=\"{M.esc(fx['olbg'])}\" rel=\"noopener\">Card</a></td></tr>"
            for r in M.market_rows(fx, p))
        detail += f"""<h2 id="{M.esc(fx['id'])}-markets">{M.esc(fx['a'])} vs {M.esc(fx['b'])}</h2>
<table><thead><tr><th>Market</th><th>Selection</th><th>Price</th><th>Fair chance</th><th>Card</th></tr></thead>
<tbody>{mrows}</tbody></table>"""
    body = f"""
<h1>{M.esc(sp['name'])}</h1>
<p class="lede">{len(fxs)} match{'es' if len(fxs)!=1 else ''} listed on OLBG today.
{'Markets: ' + M.esc(sp['market_note'])}</p>
<div class="warn"><strong>What is missing today.</strong> {M.esc(sp['gap'])}</div>
<table><thead><tr><th>Competition</th><th>Match</th><th>Clock (as listed)</th><th>Our pick</th>
<th>Card</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan="5" class="blank">No upcoming listing on the OLBG hub today.</td><td><a href="' + M.esc(sp['route']) + '" rel="noopener">Hub</a></td></tr>'}</tbody></table>
{('<h2>Our prices</h2>' + detail) if detail else ''}
<p class="small"><a href="../sports/index.html">← All sports</a> ·
<a href="{M.esc(sp['route'])}" rel="noopener">OLBG {M.esc(sp['name'])} hub</a></p>
"""
    return M.page(sp["name"], body, "sports/index.html", prefix="../")


# ------------------------------------------------------------------ flagged
def flagged_page():
    rows = []
    for fid, sev, sport, title, detail, src in D.FLAGS:
        cls = {"high": "none", "medium": "med", "low": "low"}[sev]
        rows.append(
            f"<tr id=\"{M.esc(fid)}\"><td class='num'>{M.esc(fid)}</td>"
            f"<td><span class='chip {cls}'>{M.esc(sev)}</span></td><td>{M.esc(sport)}</td>"
            f"<td><b>{M.esc(title)}</b></td><td class='small'>{M.esc(detail)}</td>"
            f"<td>{M.src_link(src)}</td></tr>")
    body = f"""
<h1>Flagged for review</h1>
<p class="lede">Everything this desk could not confirm, with the source we tried and the reason it
stayed blank. These items do not block the release; they are the honest edge of today's evidence.
Each one is checkable in under a minute.</p>
<div class="note"><strong>Rule applied.</strong> A value is published only if an official page
states it. If the page was unreadable, silent, or simply did not exist, the value stays blank and
appears here with a link.</div>
<table><thead><tr><th>Ref</th><th>Severity</th><th>Scope</th><th>Finding</th>
<th>Detail</th><th>Source checked</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
"""
    return M.page("Flagged for review", body, "flagged.html")


# ------------------------------------------------------------------ sources
def sources_page():
    rows = []
    for sid, (url, pub, what, at) in sorted(D.SOURCES.items(), key=lambda kv: kv[1][1]):
        kind = "Discovery only" if pub == "OLBG" else "Official"
        cls = "low" if pub == "OLBG" else "high"
        rows.append(
            f"<tr><td>{M.esc(pub)}</td><td><span class='chip {cls}'>{kind}</span></td>"
            f"<td class='small'>{M.esc(what)}</td><td class='num small'>{M.esc(at)}</td>"
            f"<td><a href=\"{M.esc(url)}\" rel=\"noopener\">{M.esc(url[:72])}{'…' if len(url)>72 else ''}</a></td></tr>")
    body = f"""
<h1>Sources</h1>
<p class="lede">Every URL this desk read, what it was used for, and when it was read. Official
sources verify facts. OLBG is used only to discover which matches exist and what the market is
called — its tip percentages are votes, not probabilities, and are never used as a price input.</p>
<table><thead><tr><th>Publisher</th><th>Role</th><th>Used for</th><th>Read at (UTC)</th><th>URL</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<div class="warn"><strong>Freshness.</strong> Schedule facts decay. These were read between 17:05
and 17:12 UTC on 24 October 2026. Always re-check the official link before acting on a row.</div>
"""
    return M.page("Sources", body, "sources.html")


# ------------------------------------------------------------------ method
def method_page(prices, fixtures):
    body = f"""
<h1>How this desk works</h1>
<p class="lede">Five steps, in order, for every match. A step that cannot be completed stops the
chain — it does not get filled in by hand.</p>

<h2>1. Find the matches (OLBG, discovery only)</h2>
<div class="prose"><p>We read the public OLBG hub for each of the 15 sports you listed:
golf, volleyball, rugby union, cricket, snooker, darts, baseball, Gaelic sports, greyhounds,
tennis, motor racing, handball, ice hockey, basketball and rugby league. The hub gives the
match name, competition where OLBG shows one, a clock with no timezone, the most-tipped outcome and
the market label. That is all we take from it. Tip shares are votes and are never used as a
probability.</p></div>

<h2>2. Confirm the fixture (official source)</h2>
<div class="prose"><p>A fixture is only priced if a league, tour or governing body confirms it.
Today that was possible for the NBA, the NHL and MLB. For the other twelve sports the card exists
on OLBG but no official confirmation was read, so the match is listed and left unpriced.</p></div>

<h2>3. Originate our own price</h2>
<div class="prose"><p>Every price starts from a sourced record and shrink toward .500 with a
Beta(2,2) prior, so a 2-0 start is not treated as a 100% team. The two shrunken rates are combined
with log5. No home-field edge and no league-average default is inserted: if a side has no record,
the fixture is not priced at all.</p>
<p>Handicap lines come from a normal margin family around that probability, with a disclosed
spread of {M.NBA_SIGMA} points for basketball and {M.NHL_SIGMA} goals for hockey. Those are
assumptions, and they are stated here rather than hidden. Prices are margin-free:
decimal&nbsp;=&nbsp;1&nbsp;/&nbsp;probability, with the American equivalent derived from the same
number.</p></div>

<h2>4. Grade the confidence</h2>
<div class="prose"><p>High needs a fair chance of at least 70% <em>and</em> a price no shorter than
−250. Because −250 is 71.4%, that is a 1.4-point window. Medium is 55–70%, or anything stronger
than −250 (which is outside the stated window). Low is a marginal edge. A price within five points
of even gets no selection at all — we will not pick a coin toss to fill a quota.</p></div>

<h2>5. Write it up, or leave it blank</h2>
<div class="prose"><p>Every published pick carries an original analysis of at least 30 words that
names the selection, both participants, the current record and the specific gap. Where an input is
missing — injuries, lineups, a ranking, a timezone — the sentence says so. The
<a href="flagged.html">flagged page</a> collects those gaps with links.</p></div>

<h2>What we did not do</h2>
<ul class="tight">
  <li>No tipster percentage was converted into a probability.</li>
  <li>No value was copied from another desk in this repository without re-reading its source.</li>
  <li>No clock was converted to UTC unless a league feed supplied one.</li>
  <li>No pick was published without a written analysis.</li>
  <li>No sport was padded to five picks when the evidence did not support one.</li>
</ul>
"""
    return M.page("Method", body, "method.html")


# ------------------------------------------------------------------ repo review
def repo_page():
    body = """
<h1>Repository review</h1>
<p class="lede">What is actually in this repository, read line by line where it mattered, with the
numbers checked on 24 October 2026 at 17:11 UTC. These are structural observations, not a
re-verification of every historical sentence.</p>

<table><thead><tr><th>#</th><th>Observation</th><th>Evidence</th><th>Effect on you</th><th>Repo evidence</th></tr></thead>
<tbody><tr><td>1</td><td><b>59 separate dashboards</b> each with their own <code>index.html</code></td><td><code>find . -maxdepth 2 -name index.html</code> returns 59 results</td><td>This is why the site felt confusing: there is no single front door.</td><td><a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/archive.html">Bundle of every historical desk</a></td></tr><tr><td>2</td><td><b>The canonical front page is two days stale</b></td><td><code>data/current/snapshot.json</code> is stamped <code>2026-10-22T12:29:50Z</code></td><td>The landing page shows none of this week's work; the new band fixes that.</td><td><a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/current/snapshot.json">Canonical snapshot</a></td></tr><tr><td>3</td><td><b>1,431 HTML files</b> are tracked</td><td>Repository-wide count at commit 0f6a849</td><td>Navigation, not data, is the problem.</td><td><a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/archive.html">Archive index</a></td></tr><tr><td>4</td><td><b>333 KB / 6,266 lines in the coordination board</b></td><td><code>COORDINATION.md</code></td><td>It is the audit trail, not a task list you can read in a minute.</td><td><a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/COORDINATION.md">Coordination board</a></td></tr><tr><td>5</td><td><b>No merge-conflict markers remain</b></td><td><code>grep -rl '^&lt;&lt;&lt;&lt;&lt;&lt;&lt; ' --include='*.py' --include='*.html' --include='*.md' .</code> returns nothing</td><td>The tree is clean at this commit.</td><td><a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/README.md">Repository readme</a></td></tr><tr><td>6</td><td><b>Golf, darts, greyhounds and rugby league still have no verified price</b></td><td>Repeated in the canonical README and in this session's own discovery</td><td>Today is no different, and it is stated rather than faked.</td><td><a href="flagged.html">Flagged register</a></td></tr><tr><td>7</td><td><b>The −250…+10000 window and the 70% floor overlap by 1.4 points</b></td><td>−250 implies 71.43%; the floor is 70.00%</td><td>It is still the reason High is rare; explained on F-3D-09.</td><td><a href="flagged.html#F-3D-09">Flagged item F-3D-09</a></td></tr><tr><td>8</td><td><b>Historical desks disagree with each other</b></td><td>e.g. <code>data/fixtures.json</code> versus the 22 Oct canonical snapshot</td><td>This desk re-read its own sources instead of inheriting those rows.</td><td><a href="sources.html">Sources read this session</a></td></tr></tbody></table>

<h2>What this desk changed</h2>
<ul class="tight">
  <li>Added this dashboard under <code>3d121822/</code> with machine-readable data in
      <code>data/3d121822/</code>.</li>
  <li>Added a single landing band on the canonical front page that points here, so the newest work
      is findable in one click.</li>
  <li>Added a validator and tests that enforce: every row has a source link, every pick has a
      written analysis, every analysis is at least 30 words, and no analysis repeats another.</li>
  <li>Changed no historical desk, no canonical dataset and no workflow.</li>
</ul>

<h2>How to check this page</h2>
<p class="small">Each observation is reproducible with the command or file named in the Evidence
column. Nothing here depends on a private feed or a paid API.</p>
"""
    return M.page("Repository review", body, "repo-review.html")


PRICES: dict = {}


def main():
    global PRICES
    OUT.mkdir(exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    (OUT / "sports").mkdir(exist_ok=True)
    (OUT / "assets" / "desk.css").write_text(M.CSS, encoding="utf-8")

    fixtures = fx_index()
    PRICES = M.build_prices()

    pages = {
        "index.html": overview(PRICES, fixtures),
        "picks.html": picks_page(PRICES, fixtures),
        "matches.html": matches_page(fixtures),
        "predictions.html": predictions_page(fixtures, PRICES),
        "markets.html": markets_page(PRICES, fixtures),
        "flagged.html": flagged_page(),
        "sources.html": sources_page(),
        "method.html": method_page(PRICES, fixtures),
        "repo-review.html": repo_page(),
        "sports/index.html": sports_index(fixtures, PRICES),
    }
    for sp in D.SPORTS:
        pages[f"sports/{sp['key']}.html"] = sport_page(sp, fixtures, PRICES)
    for name, html in pages.items():
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    # machine-readable exports
    fixtures_out = []
    for fx in fixtures.values():
        p = PRICES.get(fx["id"])
        fixtures_out.append(dict(fx, priced=bool(p),
                                 pick=(p["selection"] if p and p["written"] else None),
                                 confidence=(p["conf"] if p and p["written"] else None),
                                 fair_decimal=(p["decimal"] if p and p["written"] else None),
                                 fair_american=(p["american"] if p and p["written"] else None),
                                 fair_probability=(round(p["p_pick"], 4) if p and p["written"] else None),
                                 markets=(M.market_rows(fx, p) if p else [])))
    (DATA / "fixtures.json").write_text(json.dumps({
        "desk": D.DESK, "built_utc": D.OBSERVED_END, "count": len(fixtures_out),
        "priced": len(PRICES),
        "picks": len(sorted_picks(PRICES)),
        "fixtures": fixtures_out}, indent=1), encoding="utf-8")
    (DATA / "predictions.json").write_text(json.dumps({
        "desk": D.DESK, "count": len(D.PREDICTIONS),
        "predictions": [dict(fixture=k, **v) for k, v in D.PREDICTIONS.items()]}, indent=1),
        encoding="utf-8")
    (DATA / "flags.json").write_text(json.dumps({
        "desk": D.DESK, "count": len(D.FLAGS),
        "flags": [dict(ref=a, severity=b, scope=c, title=d, detail=e, source=f)
                  for a, b, c, d, e, f in D.FLAGS]}, indent=1), encoding="utf-8")
    (DATA / "sources.json").write_text(json.dumps({
        "desk": D.DESK, "read_window": [D.OBSERVED, D.OBSERVED_END],
        "sources": [dict(id=k, url=v[0], publisher=v[1], used_for=v[2], read_at=v[3])
                    for k, v in D.SOURCES.items()]}, indent=1), encoding="utf-8")

    print(f"built {len(pages)} pages · {len(fixtures)} fixtures · {len(PRICES)} priced · "
          f"{len(sorted_picks(PRICES))} picks · {len(D.PREDICTIONS)} predictions")


if __name__ == "__main__":
    main()
