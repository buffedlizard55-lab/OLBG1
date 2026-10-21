#!/usr/bin/env python3
"""Generate the static GitHub Pages site into docs/ from data/*.json"""
import json, pathlib, html, csv, io, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT/"docs"
M = json.loads((ROOT/"data"/"matches.json").read_text())
L = json.loads((ROOT/"data"/"lines.json").read_text())["lines"]
W = json.loads((ROOT/"data"/"writeups.json").read_text())["writeups"]
matches = M["matches"]; meta = M["meta"]
HDATE = meta["harvest_date"]
by_sport = collections.OrderedDict()
SPORT_ORDER = ["Tennis","Darts","Snooker","Basketball","Baseball","Ice Hockey","Cricket","Rugby Union","Volleyball","Handball","Gaelic Football"]
for s in SPORT_ORDER: by_sport[s] = [m for m in matches if m["sport"]==s]
SLUG = {s: s.lower().replace(" ","-") for s in SPORT_ORDER}
SLUG["Rugby League"]="rugby-league"
def e(x): return html.escape(str(x)) if x is not None else ""
def conf_chip(c): return f'<span class="chip {c.lower()}">{c}</span>'
def tips_str(m):
    if m.get("tips_for") is None: return '<span class="unv">— unverified —</span>'
    ex = f' · {m["experts"]} expert' + ("s" if m["experts"]>1 else "") if m.get("experts") else ""
    return f'{m["tips_for"]}/{m["tips_total"]}{ex}'

NAV = [('index.html','Dashboard')] + [(f'sports/{SLUG[s]}.html', s) for s in SPORT_ORDER] + \
      [('sports/rugby-league.html','Rugby League'),('high-confidence.html','High Confidence'),
       ('methodology.html','Methodology'),('markets.html','OLBG Markets Map'),('flagged.html','Flagged for Review'),('sources.html','Sources')]

def page(title, body, rel=""):
    nav = "".join(f'<a href="{rel}{h}">{t}</a>' for h,t in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} — OLBG1 Originated Lines</title>
<meta name="description" content="Independent originated betting lines for OLBG-listed matches, snapshot {HDATE}. Model estimates, not bookmaker odds. 18+">
<link rel="stylesheet" href="{rel}assets/style.css"></head>
<body>
<header class="top"><div class="wrap">
<div class="brand">OLBG1 <span>Originated Lines Desk</span></div>
<div class="snap">Fixture snapshot: <strong>{HDATE}</strong> · {len(matches)} matches · 11 sports priced<br>
<span class="muted">Our own model lines — not bookmaker odds. Every row links OLBG + an official source.</span></div>
</div><nav class="wrap nav">{nav}</nav></header>
<main class="wrap">{body}</main>
<footer class="wrap foot">
<p><strong>18+ only.</strong> This site publishes independent statistical estimates for information and research. Originated lines are model outputs, not bookmaker prices, and no outcome is guaranteed. Only ever stake what you can afford to lose. Free, confidential help: <a href="https://www.gamcare.org.uk/" rel="noopener">GamCare</a> · <a href="https://www.gambleaware.org/" rel="noopener">GambleAware</a>.</p>
<p>Fixtures transcribed from <a href="https://www.olbg.com/betting-tips" rel="noopener">OLBG.com</a> sport feeds on {HDATE}. Excluded per brief: football/soccer, boxing, UFC/MMA, American football, hurling, horse racing, cycling, specials. Data: <a href="{rel}data/matches.csv">matches.csv</a> · <a href="{rel}data/matches.json">matches.json</a> · Build scripts in the <a href="https://github.com/buffedlizard55-lab/OLBG1" rel="noopener">GitHub repo</a>.</p>
</footer>
<script src="{rel}assets/app.js"></script></body></html>"""

def row_html(m, with_sport=False):
    ln = L[m["id"]]
    flags = m.get("flags",[]) + ln.get("extra_flags",[])
    flag_html = "".join(f'<div class="flagline">⚠ {e(f)}</div>' for f in flags)
    hcap = f'{e(ln["handicap_pick"])}' if ln.get("handicap_pick") else '<span class="muted">n/a</span>'
    tot = f'{e(ln["total_pick"])}' if ln.get("total_pick") else '<span class="muted">n/a</span>'
    write = W.get(m["id"])
    w_html = ""
    if write:
        w_html = f'<tr class="writerow"><td colspan="9"><strong>Selection: {e(write["selection_label"])}</strong><p>{e(write["text"])}</p></td></tr>'
    ver = m.get("verification","")
    verb = {"VERIFIED":'<span class="ver ok">Fixture confirmed on official source</span>',
            "OLBG-ONLY":'<span class="ver mid">Fixture on OLBG; official link for manual check</span>',
            "CONTESTED":'<span class="ver bad">CONTESTED — see flag</span>'}.get(ver, e(ver))
    draw = f'<br><span class="muted">Draw/Tie: {ln["draw_prob"]*100:.1f}% (fair {1/ln["draw_prob"]:.2f})</span>' if ln.get("draw_prob") else ""
    sport_td = f'<td>{e(m["sport"])}</td>' if with_sport else ""
    return f"""<tr data-conf="{ln['confidence']}" data-text="{e((m['home']+' '+m['away']+' '+m['league']+' '+m['sport']).lower())}">
<td class="id">{m['id']}</td>{sport_td}
<td><strong>{e(m['home'])} v {e(m['away'])}</strong><br><span class="muted">{e(m['league'])}</span><br><span class="muted">{m['date']} · {e(m['time_olbg'])} (as shown on OLBG)</span>{flag_html}</td>
<td>{e(m['olbg_market'])}: <strong>{e(m['olbg_selection'])}</strong><br><span class="muted">{tips_str(m)} win tips</span></td>
<td class="pick"><strong>{e(ln['pick'])}</strong><br>{ln['pick_prob']*100:.1f}% · fair <strong>{ln['fair_decimal_pick']}</strong> ({ln['fair_fractional_pick']})<br><span class="muted">Other side: {ln['other_prob']*100:.1f}% · fair {ln['fair_decimal_other']} ({ln['fair_fractional_other']})</span>{draw}</td>
<td>{hcap}</td><td>{tot}</td><td>{conf_chip(ln['confidence'])}</td>
<td class="src"><a href="{m['olbg_url']}" rel="noopener">OLBG event</a><br><a href="{m['official_url']}" rel="noopener">{e(m['official_label'].split('—')[0].strip())}</a><br>{verb}</td>
<td class="deriv">{e(ln['derivation'])}<br><span class="muted">{e(ln.get('total_basis') or '')}</span></td></tr>{w_html}"""

TABLE_HEAD = """<div class="tools"><input id="q" type="search" placeholder="Filter: team, player, league…">
<select id="cf"><option value="">All confidence levels</option><option>HIGH</option><option>MEDIUM</option><option>LOW</option></select>
<span id="count" class="muted"></span></div>
<div class="tablewrap"><table class="grid"><thead><tr><th>ID</th><th>Match</th><th>OLBG most-tipped</th>
<th>Our winner pick &amp; fair odds</th><th>Our handicap pick</th><th>Our total pick</th><th>Confidence</th><th>Sources</th><th>Derivation</th></tr></thead><tbody>"""

# ---------- per-sport pages ----------
SPORT_INTRO = {
 "Tennis": "Week of 19–25 Oct 2026: ATP 250 events in Almaty, Lyon and Brussels plus WTA Ningbo (500) and Osaka (250), per the official ATP 2026 calendar. OLBG's feed does not name each match's tournament, so none is asserted. No per-player ATP/WTA ranking gap was verified this pass — by our rules that caps every tennis pick below HIGH (see Flagged page).",
 "Darts": "Every tie below is a PDC European Championship first-round match (Westfalenhallen, Dortmund, 22–25 Oct 2026, best of 11 legs), confirmed against the official PDC draw of 18 Oct 2026. Field: top 32 of the European Tour Order of Merit; £750,000 fund, £150,000 to the winner.",
 "Snooker": "BetVictor Northern Ireland Open, Waterfront Hall Belfast, 18–25 Oct 2026. Round 2 (21 Oct) is best of 7 frames. Two OLBG pairings could not be confirmed on the official WST match centre at harvest and are flagged CONTESTED — they are shown exactly as OLBG lists them and forced to LOW confidence.",
 "Basketball": "The 2026-27 NBA regular season tipped off on 20 Oct 2026 (NBA official), so NBA rows are opening-week games with effectively no current-season form — confidence is capped at MEDIUM by rule. European rows are EuroLeague, EuroCup, Basketball Champions League and Korea KBL fixtures as listed by OLBG.",
 "Baseball": "One game on the board — but it's the big one: Game 1 of the 2026 World Series. Confirmed on MLB's official schedule. Starting pitchers were unconfirmed at harvest, which caps confidence.",
 "Ice Hockey": "NHL plus Austria's ICE Hockey League and Sweden's SHL. OLBG's NHL interest sits in Game Totals (Over 5.5), which gives no direct winner signal — those winner picks start from a 50/50 base plus home edge and are LOW by construction.",
 "Cricket": "Internationals headline: New Zealand v India (1st T20I, Hagley Oval, 22 Oct — ICC official) and an Afghanistan v Bangladesh ODI inside the UAE tri-series window. Cricket has no standard match handicap/total market on OLBG, so those columns read n/a rather than inventing a market.",
 "Rugby Union": "United Rugby Championship Round 4 (official URC fixture list) plus France's Pro D2 and Top 14 (LNR). Totals and home edges use OLBG's own published five-season league averages (URC 48.9 pts/game, Top 14 home-win rate 74.4%).",
 "Volleyball": "Best-of-5-sets club volleyball. OLBG tips cover Win Match and Set Score only; set-handicap and total-sets lines are our model lines derived from win probability and labelled as such.",
 "Handball": "European club and international handball with a 3-way money line (Home / Tie / Away, regular time). Note the four matches where OLBG's most-tipped selection is the Tie — ties land in under 10% of comparable EHF Champions League games, so our winner pick falls back to the home side at LOW and each case is flagged for manual review.",
 "Gaelic Football": "GAA club football as listed by OLBG. Hurling is excluded from this project by the brief and does not appear. Draws are a real outcome in Gaelic football, so the model carries an explicit 8% draw allowance (model assumption, flagged).",
}
for s in SPORT_ORDER:
    ms = by_sport[s]
    counts = collections.Counter(L[m["id"]]["confidence"] for m in ms)
    body = f"""<h1>{s}</h1><p class="lede">{e(SPORT_INTRO[s])}</p>
<p>{len(ms)} matches · {counts['HIGH']} HIGH · {counts['MEDIUM']} MEDIUM · {counts['LOW']} LOW · OLBG feed: <a href="https://www.olbg.com/betting-tips" rel="noopener">olbg.com/betting-tips</a></p>
{TABLE_HEAD}""" + "".join(row_html(m) for m in ms) + "</tbody></table></div>"
    (DOCS/"sports"/f"{SLUG[s]}.html").write_text(page(s, body, rel="../"))

# Rugby League zero page
zl = meta["zero_match_sports"][0]
body = f"""<h1>Rugby League</h1><div class="callout"><strong>No upcoming matches to price — verified zero.</strong>
<p>{e(zl['reason'])}</p><p>Sources: <a href="{zl['olbg_url']}" rel="noopener">OLBG Rugby League feed</a> · <a href="{zl['official_url']}" rel="noopener">{e(zl['official_label'])}</a>. Checked {HDATE}. When the 2027 Super League/NRL seasons publish fixtures with OLBG tips open, this page gets the same treatment as every other sport.</p></div>"""
(DOCS/"sports"/"rugby-league.html").write_text(page("Rugby League", body, rel="../"))

# ---------- dashboard ----------
conf_all = collections.Counter(L[m["id"]]["confidence"] for m in matches)
high = [m for m in matches if L[m["id"]]["confidence"]=="HIGH"]
cards = ""
for s in SPORT_ORDER:
    ms = by_sport[s]; c = collections.Counter(L[m["id"]]["confidence"] for m in ms)
    cards += f'<a class="card" href="sports/{SLUG[s]}.html"><strong>{s}</strong><span>{len(ms)} matches</span><span class="muted">{c["HIGH"]} high · {c["MEDIUM"]} med · {c["LOW"]} low</span></a>'
cards += '<a class="card" href="sports/rugby-league.html"><strong>Rugby League</strong><span>0 matches</span><span class="muted">off-season — verified</span></a>'
high_rows = "".join(row_html(m, with_sport=True) for m in high)
best = sorted(matches, key=lambda m: -L[m["id"]]["pick_prob"])[:12]
body = f"""<h1>Dashboard — every OLBG match in scope, independently priced</h1>
<p class="lede">We reverse-engineered OLBG's tipping feeds, took every upcoming match in the sports covered by the brief (133 matches, snapshot {HDATE}), threw away the bookmaker prices, and originated our own win probabilities, handicap lines and totals from documented inputs only: OLBG crowd share with sample sizes, official seedings/ratings where verified, and published league scoring averages. Anything we could not verify is blank or flagged — never filled in.</p>
<div class="stats">
<div class="stat"><strong>{len(matches)}</strong><span>matches priced</span></div>
<div class="stat"><strong>11 + 1</strong><span>sports (Rugby League: 0 fixtures, off-season)</span></div>
<div class="stat"><strong>{conf_all['HIGH']}</strong><span>HIGH confidence</span></div>
<div class="stat"><strong>{conf_all['MEDIUM']}</strong><span>MEDIUM confidence</span></div>
<div class="stat"><strong>{conf_all['LOW']}</strong><span>LOW confidence (most OLBG markets rest on 1–3 tips — the model refuses to pretend otherwise)</span></div>
</div>
<h2>Browse by sport</h2><div class="cards">{cards}</div>
<h2>High-confidence picks (with full previews)</h2>
<p>Only four matches cleared the HIGH bar: a ≥70% originated win probability backed by at least six OLBG tips <em>and</em> a corroborating official seeding/rating gap (or an 80%+ probability with a double-digit seeding gap at a verified event). Each carries a hand-written preview using facts from the official source on its row. <a href="high-confidence.html">Open the dedicated page →</a></p>
<div class="tablewrap"><table class="grid"><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>OLBG most-tipped</th><th>Our winner pick &amp; fair odds</th><th>Our handicap pick</th><th>Our total pick</th><th>Confidence</th><th>Sources</th><th>Derivation</th></tr></thead><tbody>{high_rows}</tbody></table></div>
<h2>Strongest model leanings (all confidence levels)</h2>
<p class="muted">Ranked by originated win probability. Probability alone does not make a pick HIGH — sample size and official corroboration decide that. See <a href="methodology.html">Methodology</a>.</p>
<div class="tablewrap"><table class="grid"><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>OLBG most-tipped</th><th>Our winner pick &amp; fair odds</th><th>Our handicap pick</th><th>Our total pick</th><th>Confidence</th><th>Sources</th><th>Derivation</th></tr></thead><tbody>{''.join(row_html(m, with_sport=True) for m in best)}</tbody></table></div>
<h2>Headline findings</h2>
<ul class="findings">
<li><strong>The World Series is the week's centrepiece:</strong> OLBG's only baseball match is Rays (98–64) @ Brewers (103–59), Game 1 on 23 Oct — confirmed on MLB's official schedule. With starters unconfirmed and OLBG split 3/3, we make Milwaukee a wafer-thin 52.0% home favourite, LOW confidence. <a href="sports/baseball.html">Baseball →</a></li>
<li><strong>OLBG's crowd sometimes opposes official seedings:</strong> in Dortmund, tipsters' most-backed picks include 27th seed Cristo Reyes over 6th seed Nathan Aspinall and Martin Schindler over 2nd seed Wessel Nijman. Both are flagged as signal conflicts and forced to LOW. <a href="flagged.html">Flagged →</a></li>
<li><strong>Two OLBG snooker pairings don't match the official WST draw</strong> at harvest time (Cheung Ka Wai v Stuart Bingham; Luca Brecel v Martin O'Donnell). Shown as OLBG lists them, marked CONTESTED, forced LOW. <a href="sports/snooker.html">Snooker →</a></li>
<li><strong>Handball's 'Tie' pile-ups are a trap:</strong> four matches have the Tie as most-tipped selection, yet ties occur in under 10% of comparable EHF Champions League games. Our model will not pick a sub-10% outcome as a 'winner'. <a href="sports/handball.html">Handball →</a></li>
<li><strong>Milwaukee Bucks are being opposed for a verifiable reason:</strong> 9 of 11 OLBG tips take Washington over Milwaukee on NBA opening week — two-time MVP Giannis Antetokounmpo now plays for Miami (NBA official schedule release). Still only MEDIUM: game one of a season is chaos. <a href="sports/basketball.html">Basketball →</a></li>
<li><strong>Thin samples dominate OLBG beyond the headline sports:</strong> 100 of 133 matches rest on five or fewer tips in the most-tipped market. Any site calling those 'bankers' is guessing; ours labels them LOW and shows the arithmetic.</li>
</ul>"""
(DOCS/"index.html").write_text(page("Dashboard", body))

# ---------- high confidence page ----------
body = f"""<h1>High-confidence picks</h1>
<p class="lede">Four matches from {len(matches)} cleared our HIGH bar (see <a href="methodology.html">Methodology</a> for the exact rules). Each preview below is written for that match alone — no templates, no repeated boilerplate — using only facts traceable to the official source linked on the row. The selection is stated in bold inside every preview.</p>
{TABLE_HEAD}""" + "".join(row_html(m) for m in high) + "</tbody></table></div>"
# fix table head mismatch (9 cols, no sport col) — fine as built
(DOCS/"high-confidence.html").write_text(page("High Confidence Picks", body))

# ---------- methodology ----------
body = f"""<h1>Methodology — how every line was originated</h1>
<p class="lede">No bookmaker odds are used anywhere on this site. OLBG's odds columns were not present in the fetched pages, and the brief is independent origination. Fair odds = 1 ÷ probability (zero margin). The engine is <code>scripts/originate.py</code> in the repo — deterministic and re-runnable.</p>
<h2>Inputs (the only ones)</h2>
<ol>
<li><strong>OLBG crowd signal</strong> — for each match, the share of OLBG win tips behind the most-tipped selection, <em>with its sample size</em>, transcribed line by line from OLBG's sport feeds on {HDATE}. Smoothed toward 50% for small samples: <code>s = (tips_for + 2) / (tips_total + 4)</code>.</li>
<li><strong>Official seeding/rating gaps</strong> — only where verified against an official source this session: PDC European Championship draw (pdc.tv, 18 Oct 2026), snooker world-rank numbers published alongside the WST draw, ICC ODI team ratings (19 Oct 2026 update). Better-ranked side gains <code>min(12, 0.5 × gap)</code> percentage points (ICC ratings: 0.5pp per point, capped at 6pp — one match only).</li>
<li><strong>Home edge</strong> — small fixed allowances per league (NBA/European basketball +2–3pp, NHL +2pp, rugby union +4pp reflecting OLBG's published 64–74% home-win rates, handball +3pp, volleyball +2pp, MLB +2pp). Neutral-venue individual sports (tennis, darts, snooker) get zero.</li>
<li><strong>Published league scoring averages</strong> for totals/handicap baselines: OLBG's five-season rugby union averages (URC 48.9 total points; Top 14 49.7), OLBG's EHF Champions League handball averages (60.82 goals, 5.04 margin, 9.8% ties), and OLBG market standards (NHL puck line 1.5, MLB run line 1.5, darts best-of-11 total-legs line 9.5). Where no published average was fetched (e.g. NBA game totals), the line is tagged <strong>MODEL-BASELINE</strong> in the Derivation column — our estimate, openly.</li>
</ol>
<h2>From inputs to a price</h2>
<ul>
<li><strong>Winner markets</strong> (Win Match / Money Line / To Win): the named side starts at the smoothed share <code>s</code>.</li>
<li><strong>Directional markets</strong> (Set Betting, 1st Set Winner, Set Score): imply an eventual winner at half strength — <code>p = 0.5 + 0.5×(s−0.5)</code>.</li>
<li><strong>Handicap markets</strong>: a backed '+' side is the underdog by that many units; the favourite's probability comes from inverting the sport's margin map, nudged by crowd enthusiasm <code>(s−0.5)×0.1</code>. A backed '−' side is the favourite, same map.</li>
<li><strong>Totals-only markets</strong> (e.g. NHL Over 5.5): winner probability starts 50/50; the crowd's Over/Under becomes our total pick at that line.</li>
<li><strong>Tie/Draw most-tipped</strong> (handball): OLBG's feed does not reveal the home/away split of the remaining tips, so the winner pick falls back to a 52% home lean, forced LOW and flagged — never a sub-10% tie dressed up as a 'winner pick'.</li>
<li>Ranking and home adjustments are added, the favourite's probability is capped to [52%, 88%], and exact coin flips lean to the first-named side at 52% (documented, arbitrary, flagged LOW by construction).</li>
<li><strong>3-way sports</strong> (rugby union, handball, Gaelic football) carry a draw allowance: rugby 2.3% (OLBG published), handball 9.0% (OLBG EHF CL tie rate), Gaelic 8% (model assumption). Two-way probabilities are scaled by (1 − draw rate).</li>
<li><strong>Handicap line</strong> = expected margin from win probability (NBA 28 pts, European basketball 24, rugby union 45, handball 16 goals, tennis 12 games, Gaelic 30 pts per full probability unit; fixed/stepped in NHL, MLB, darts, snooker, volleyball). We lay the favourite only at ≥62% win probability; otherwise we take the underdog's head start — the standard 'take the points in a close one' heuristic, stated as such.</li>
<li><strong>Total pick</strong>: follows the OLBG crowd where the crowd tipped a total; otherwise Over in competitive-match probability bands and Under in mismatch/coin-flip bands (bands per sport in code). Totals without team-level pace data are the weakest part of any such model — treat accordingly.</li>
<li><strong>Cricket</strong> handicap/total = n/a: OLBG covers Win Match, Top Batter and Man of the Match. We do not invent markets that don't exist.</li>
</ul>
<h2>Confidence — deterministic rules</h2>
<table class="grid"><thead><tr><th>Level</th><th>Rule</th></tr></thead><tbody>
<tr><td>{conf_chip('HIGH')}</td><td>Path A: win probability ≥70% <em>and</em> ≥6 OLBG tips in a winner market <em>and</em> a corroborating official seeding/rating gap that agrees with the pick. Path B: probability ≥80% with an official gap of ≥11 seeds (darts) or ≥40 ranking places (snooker) at a verified event. Any conflict/contested flag disqualifies.</td></tr>
<tr><td>{conf_chip('MEDIUM')}</td><td>Probability ≥60% on ≥4 tips, or ≥70% on ≥2 tips; no conflicts. NBA opening week is capped here regardless (no form base — season started 20 Oct).</td></tr>
<tr><td>{conf_chip('LOW')}</td><td>Everything else, plus forced LOW for: crowd-vs-seeding conflicts, CONTESTED fixtures, Tie-most-tipped matches, and rows whose tip counts OLBG's page fetch cut off (left blank, never estimated).</td></tr>
</tbody></table>
<h2>What 'verified' means on each row</h2>
<ul>
<li><strong>Fixture confirmed on official source</strong> — the exact fixture appears in an official schedule/draw fetched this session (MLB, PDC, WST, ICC, URC, NBA slate).</li>
<li><strong>Fixture on OLBG; official link for manual check</strong> — fixture confirmed on OLBG's feed; the governing-body/league link is provided so a human can re-check. We do not claim more than we checked.</li>
<li><strong>CONTESTED</strong> — OLBG's pairing could not be reconciled with the official draw at harvest. Shown as listed, flagged, LOW.</li>
</ul>
<h2>Known limitations (also on the Flagged page)</h2>
<ul>
<li>OLBG hides zero-tip and lower-ranked fixtures behind a 'Load More' control; coverage is every event visible in the fetched feeds, not a promise about fixtures with no tips at all.</li>
<li>OLBG does not state a timezone for displayed times in the fetched text; times are reproduced 'as shown on OLBG'.</li>
<li>ATP/WTA per-player ranking gaps were not verified this pass, so no tennis pick can reach HIGH yet. Same for team standings in European basketball/hockey/handball domestic leagues.</li>
<li>Starting pitchers (MLB) and goalie starters (NHL) were unconfirmed at harvest and are left blank.</li>
</ul>"""
(DOCS/"methodology.html").write_text(page("Methodology", body))

# ---------- markets map ----------
body = f"""<h1>OLBG reverse-engineered: site &amp; market map</h1>
<p class="lede">What OLBG is and how its tipping engine works, documented from its own pages on {HDATE} — the map we priced against. OLBG (Online Betting Guide, founded 2002 per its own history) runs a free tipster community across 20+ sports: every tip is tracked, tipsters are ranked by 12-month profit, and each sport feed surfaces the <em>most-tipped selection per event</em> with its market, tip counts, comment count and 'expert' flags (profitable tipsters). Its Value Rating compares a selection's tip share with the probability implied by its odds.</p>
<h2>Markets OLBG carries per covered sport (from OLBG's own guides)</h2>
<table class="grid"><thead><tr><th>Sport</th><th>Match markets on OLBG</th><th>Our originated equivalents</th></tr></thead><tbody>
<tr><td>Tennis</td><td>Win Match, Set Betting, Total Games, 1st Set Winner, Games Won (handicap), Tournament Winner</td><td>Winner + games handicap + total games</td></tr>
<tr><td>Darts</td><td>Win Match 2-way, Handicap 2-way (legs, standard ±1.5), Total Legs/Sets (e.g. 9.5 in best-of-11), Tournament Winner</td><td>Winner + legs handicap + total legs</td></tr>
<tr><td>Snooker</td><td>Win Match, Handicap Betting (frames), Frame Betting (exact score), Win Tournament</td><td>Winner + frame handicap + total frames</td></tr>
<tr><td>Basketball</td><td>Money Line, Pointspread, Game Totals</td><td>Winner + point spread + game total</td></tr>
<tr><td>Baseball</td><td>Money Line, Run Line (usually ±1.5), Game Totals</td><td>Winner + run line 1.5 + game total</td></tr>
<tr><td>Ice Hockey</td><td>Money Line (NHL 2-way incl. OT), Puck Line (usually ±1.5), Game Totals</td><td>Winner + puck line 1.5 + game total</td></tr>
<tr><td>Cricket</td><td>Win Match, Top Batter, Man of the Match, outrights</td><td>Winner only — handicap/total n/a (no such standard market)</td></tr>
<tr><td>Rugby Union / League</td><td>To Win, Handicap, outrights (winning-margin markets exist with bookmakers)</td><td>Winner (3-way with draw) + points handicap + total points</td></tr>
<tr><td>Volleyball</td><td>Win Match, Set Score (exact sets, 6 outcomes)</td><td>Winner + set handicap + total sets (model lines — OLBG lists no handicap/total)</td></tr>
<tr><td>Handball</td><td>Money Line 3-way (regular time), Match Handicap, Points Total</td><td>Winner (3-way) + goals handicap + points total</td></tr>
<tr><td>Gaelic Football</td><td>Match result (incl. Draw), Handicap, outrights (Sam Maguire etc.)</td><td>Winner (3-way) + points handicap + total points (model)</td></tr>
</tbody></table>
<h2>How to read an OLBG feed row (and its traps)</h2>
<ul>
<li>The highlighted selection is the <strong>most-tipped outcome in whichever market attracted interest</strong> — not necessarily the match-winner market. A 'Total Legs: Over 9.5' or 'Underdog +3.5' row must be decoded before it says anything about who wins. Our engine does this explicitly per market type.</li>
<li>Percentages without denominators mislead: '100%' on site often means 1/1 or 2/2 tips. Every row here shows the fraction.</li>
<li>In 3-way handball, the Tie is a perpetual long-odds magnet for tipsters hunting value ratings — four matches this week have Tie as the most-tipped selection despite a sub-10% base rate.</li>
<li>'Expert' flags denote tipsters with strong recent profit/strike rate in that sport (OLBG's definition) — a useful quality hint, recorded on every row here.</li>
<li>Outrights (tournament winners, 2027 championships etc.) are listed in the same feeds. They are out of match scope and excluded from pricing; Rugby League currently has <em>only</em> outrights, hence zero matches.</li>
</ul>
<p>Primary sources: <a href="https://www.olbg.com/betting-tips" rel="noopener">OLBG betting tips hub</a> and its per-sport guides (tennis, darts, snooker, basketball, baseball, ice hockey, cricket, rugby union, rugby league, volleyball, handball, Gaelic football), all fetched {HDATE}.</p>"""
(DOCS/"markets.html").write_text(page("OLBG Markets Map", body))

# ---------- flagged page ----------
flag_rows = []
for m in matches:
    fl = m.get("flags",[]) + L[m["id"]].get("extra_flags",[])
    serious = [f for f in fl if f.startswith(("IRREGULARITY","UNVERIFIED","Model note"))]
    if serious or m.get("verification")=="CONTESTED":
        flag_rows.append((m, serious or fl))
flag_html = "".join(
 f'<tr><td class="id">{m["id"]}</td><td>{e(m["sport"])}</td><td><strong>{e(m["home"])} v {e(m["away"])}</strong> ({m["date"]})</td>'
 f'<td>{"<br>".join("⚠ "+e(f) for f in fl)}</td>'
 f'<td class="src"><a href="{m["olbg_url"]}" rel="noopener">OLBG event</a><br><a href="{m["official_url"]}" rel="noopener">Official source</a></td>'
 f'<td>{conf_chip(L[m["id"]]["confidence"])}</td></tr>' for m,fl in flag_rows)
zeros = "".join(f'<tr><td>—</td><td>{e(z["sport"])}</td><td>Zero matches priced</td><td>{e(z["reason"])}</td><td class="src"><a href="{z["olbg_url"]}" rel="noopener">OLBG</a> · <a href="{z["official_url"]}" rel="noopener">{e(z["official_label"])}</a></td><td>—</td></tr>' for z in meta["zero_match_sports"])
body = f"""<h1>Flagged for Review</h1>
<p class="lede">Everything below is published deliberately, not buried. None of it blocks the site — it is the manual-review queue. Items marked UNVERIFIED are blank in the data (never estimated). CONTESTED and conflict rows are forced to LOW confidence. Review each against its official link and request changes in the repo.</p>
<h2>Match-level irregularities ({len(flag_rows)})</h2>
<div class="tablewrap"><table class="grid"><thead><tr><th>ID</th><th>Sport</th><th>Match</th><th>Issue</th><th>Check it</th><th>Confidence</th></tr></thead><tbody>{flag_html}</tbody></table></div>
<h2>Sports with zero priced matches</h2>
<div class="tablewrap"><table class="grid"><thead><tr><th>ID</th><th>Sport</th><th>Status</th><th>Reason</th><th>Check it</th><th></th></tr></thead><tbody>{zeros}</tbody></table></div>
<h2>Dataset-level caveats for the reviewer</h2>
<ul>
<li><strong>Seed/rank provenance:</strong> PDC European Championship seeds beyond Zonneveld (4th) and Humphries (12th) — both stated in the PDC's official draw article — were transcribed from published draw tables summarising that official draw. Snooker rank numbers (Pang 26, Davies 89, Higgins 7, J. Jones 30) come from a secondary listing of the WST draw. The PDC/WST pages are linked on every affected row for re-checking; the HIGH grade for SNO-02 depends in part on the 63-place gap and should be re-confirmed on the official WST ranking list.</li>
<li><strong>No ATP/WTA ranking gaps, no league standings</strong> (EuroLeague, SHL, domestic handball/volleyball) were verified this pass. Consequence: no tennis pick above MEDIUM, and team-sport totals tagged MODEL-BASELINE. This is the top enrichment task for the next session.</li>
<li><strong>OLBG 'Load More' tail:</strong> fixtures with zero tips may exist beyond the fetched feed pages. Our universe = events with tips open in the feeds as fetched. Stated on the Methodology page.</li>
<li><strong>Times:</strong> OLBG displayed times without a timezone in fetched text; reproduced as shown. Do not use for scheduling without checking the OLBG event page.</li>
<li><strong>NBA home/away:</strong> OLBG uses US 'Away @ Home' format for NBA/NHL/MLB; rows preserve OLBG's naming order and the model credits home edge to the '@' host. Spot-check BKB-01…06, ICE-06/07, BBA-01.</li>
<li><strong>Handball competitions unnamed:</strong> OLBG's feed does not label each handball fixture's competition (Champions League vs domestic leagues); league field says so rather than guessing. EHF link on each row.</li>
<li><strong>Gaelic club championships unnamed</strong> in OLBG's feed for the same reason; GAA link provided.</li>
<li><strong>Cricket tri-series label</strong> for Afghanistan v Bangladesh (UAE window 17–21 Oct) rests on the international fixture list rather than an ICC match page fetched this session — ICC rankings link on the row.</li>
</ul>"""
(DOCS/"flagged.html").write_text(page("Flagged for Review", body))

# ---------- sources page ----------
srcs = collections.OrderedDict()
for m in matches: srcs.setdefault((m["official_label"], m["official_url"]), 0); srcs[(m["official_label"], m["official_url"])] += 1
srows = "".join(f'<tr><td><a href="{u}" rel="noopener">{e(lab)}</a></td><td>{n} rows</td></tr>' for (lab,u),n in srcs.items())
body = f"""<h1>Sources</h1>
<p class="lede">Two links ride on every one of the {len(matches)} rows: the OLBG event page (fixture + crowd data, harvested {HDATE}) and an official league or governing-body page. The table below lists every official source used. Line-origination inputs drawn from OLBG's own published statistics (rugby union league averages, EHF handball averages, market-standard lines) are cited in the Derivation column of each affected row and on the <a href="methodology.html">Methodology</a> page.</p>
<div class="tablewrap"><table class="grid"><thead><tr><th>Official source</th><th>Used by</th></tr></thead><tbody>{srows}</tbody></table></div>
<h2>Also consulted (verification context)</h2>
<ul>
<li>ATP Tour official 2026 calendar (atptour.com) — confirmed 19–25 Oct events: Almaty, Lyon, Brussels.</li>
<li>NBA official: key dates + 2026-27 schedule release (nba.com / pr.nba.com) — season start 20 Oct 2026; Antetokounmpo's Miami debut 21 Oct.</li>
<li>MLB official World Series schedule (mlb.com) — Rays (98–64) @ Brewers (103–59), Game 1 Fri 23 Oct, American Family Field; LCS outcomes.</li>
<li>ICC official (icc-cricket.com) — India tour of New Zealand itinerary (1st T20I 22 Oct, Christchurch); ICC ODI ratings as republished 19 Oct 2026.</li>
<li>URC official fixture release (unitedrugby.com) — Round 4, 23–24 Oct 2026.</li>
<li>PDC official draw article (pdc.tv, 18 Oct 2026) — European Championship field, seeds for Zonneveld/Humphries, Littler's European Tour wins.</li>
<li>WST official match centre (wst.tv) — Northern Ireland Open Round 2, 21 Oct 2026.</li>
</ul>"""
(DOCS/"sources.html").write_text(page("Sources", body))

# ---------- data downloads ----------
(DOCS/"data").mkdir(exist_ok=True)
(DOCS/"data"/"matches.json").write_text(json.dumps({"meta":meta,"matches":matches,"lines":L,"writeups":W}, indent=1, ensure_ascii=False))
buf = io.StringIO(); w = csv.writer(buf)
w.writerow(["id","sport","league","home","away","date","time_as_shown_on_olbg","olbg_market","olbg_selection","olbg_tips_for","olbg_tips_total","olbg_experts","our_pick","our_pick_prob","fair_decimal_pick","our_handicap_pick","our_total_pick","confidence","verification","olbg_url","official_label","official_url","flags"])
for m in matches:
    ln = L[m["id"]]
    w.writerow([m["id"],m["sport"],m["league"],m["home"],m["away"],m["date"],m["time_olbg"],m["olbg_market"],m["olbg_selection"],m.get("tips_for"),m.get("tips_total"),m.get("experts"),ln["pick"],ln["pick_prob"],ln["fair_decimal_pick"],ln.get("handicap_pick"),ln.get("total_pick"),ln["confidence"],m.get("verification"),m["olbg_url"],m["official_label"],m["official_url"]," | ".join(m.get("flags",[])+ln.get("extra_flags",[]))])
(DOCS/"data"/"matches.csv").write_text(buf.getvalue())
print("Site built:", sum(1 for _ in DOCS.rglob("*.html")), "pages")
