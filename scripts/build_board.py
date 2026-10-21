#!/usr/bin/env python3
"""Generate the static GitHub Pages site in docs/ from data/matches.json."""
import json, pathlib, html, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT/"data/matches.json").read_text(encoding="utf-8"))
ROWS = DATA["rows"]; SNAP = DATA["snapshot_date"]
OUT = ROOT/"docs"; (OUT/"assets").mkdir(parents=True, exist_ok=True)

SLUG = {"Tennis":"tennis","Basketball":"basketball","Golf":"golf","Cricket":"cricket",
"Snooker":"snooker","Rugby Union":"rugby-union","Rugby League":"rugby-league","Baseball":"baseball",
"Ice Hockey":"ice-hockey","Motor Racing":"motor-racing","Darts":"darts","Handball":"handball",
"Volleyball":"volleyball","Gaelic Football":"gaelic-football","Greyhounds":"greyhounds"}
SPORTS = list(SLUG.keys())
OFFICIAL = {
 "Tennis":("ATP / WTA","https://www.wtatennis.com/"),"Basketball":("NBA","https://www.nba.com/"),
 "Golf":("PGA Tour","https://www.pgatour.com/"),"Cricket":("ICC","https://www.icc-cricket.com/"),
 "Snooker":("World Snooker Tour","https://www.wst.tv/"),"Rugby Union":("World Rugby","https://www.world.rugby/"),
 "Rugby League":("NRL","https://www.nrl.com/"),"Baseball":("MLB","https://www.mlb.com/"),
 "Ice Hockey":("NHL","https://www.nhl.com/"),"Motor Racing":("Formula 1","https://www.formula1.com/"),
 "Darts":("PDC","https://www.pdc.tv/"),"Handball":("EHF","https://www.eurohandball.com/"),
 "Volleyball":("Volleyball World","https://en.volleyballworld.com/"),"Gaelic Football":("GAA","https://www.gaa.ie/"),
 "Greyhounds":("GBGB","https://www.gbgb.org.uk/")}

CSS = """
:root{--bg:#0b1220;--card:#111a2e;--line:#22304d;--txt:#e8eefc;--mut:#9db0d1;--acc:#38bdf8;--ok:#34d399;--mid:#fbbf24;--low:#94a3b8;--bad:#f87171}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:var(--txt)}
a{color:var(--acc)}header{position:sticky;top:0;background:#0b1220f2;border-bottom:1px solid var(--line);z-index:5}
.wrap{max-width:1240px;margin:0 auto;padding:16px}nav{display:flex;flex-wrap:wrap;gap:8px;padding:10px 16px;max-width:1240px;margin:0 auto}
nav a{color:var(--txt);text-decoration:none;padding:6px 10px;border:1px solid var(--line);border-radius:999px;font-size:13px;background:var(--card)}
nav a:hover{border-color:var(--acc)}nav a.on{background:var(--acc);color:#04121f;font-weight:700}
h1{font-size:28px;margin:8px 0}h2{font-size:20px;margin:26px 0 10px}.mut{color:var(--mut)}.small{font-size:13px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}.big{font-size:26px;font-weight:800}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:13px}
th,td{padding:8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{background:#0e1730;position:sticky;top:0}
.tbl{overflow-x:auto;border-radius:12px}.pill{display:inline-block;padding:2px 8px;border-radius:999px;font-weight:700;font-size:12px}
.High{background:#064e3b;color:#6ee7b7}.Medium{background:#4a2f04;color:#fcd34d}.Low{background:#1e293b;color:#cbd5e1}
input,select{background:var(--card);color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:9px}
.controls{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}.note{background:#1a1207;border:1px solid #7c5c1e;border-radius:12px;padding:12px 14px}
.err{background:#2a0f14;border:1px solid #7f1d2d;border-radius:12px;padding:12px 14px}.ok{background:#07281d;border:1px solid #065f46;border-radius:12px;padding:12px 14px}
footer{border-top:1px solid var(--line);margin-top:36px}.pick{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:14px 0}
code{background:#0e1730;padding:2px 5px;border-radius:6px}ul{line-height:1.6}p{line-height:1.6}
"""

JS = """
function filt(){var q=document.getElementById('q').value.toLowerCase(),c=document.getElementById('cf').value,s=document.getElementById('sf')?document.getElementById('sf').value:'';
document.querySelectorAll('tbody tr').forEach(function(r){var ok=r.textContent.toLowerCase().includes(q);
if(c&&!r.dataset.conf.includes(c))ok=false; if(s&&r.dataset.sport!==s)ok=false; r.style.display=ok?'':'none';});}
"""

def esc(x): return html.escape(str(x if x is not None else ""))
def nav(cur=""):
    links = [("index.html","Dashboard"),("high-confidence.html","High confidence"),("markets.html","Markets"),
             ("methodology.html","Methodology"),("flagged.html","Flagged for Review")]
    h = "".join(f'<a class="{"on" if cur==u else ""}" href="{u}">{t}</a>' for u,t in links)
    h += "".join(f'<a class="{"on" if cur==SLUG[s]+".html" else ""}" href="{SLUG[s]}.html">{esc(s)}</a>' for s in SPORTS)
    return f"<header><nav>{h}</nav></header>"
def page(title, cur, body):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG1 Match Board</title><link rel="stylesheet" href="assets/style.css"></head><body>{nav(cur)}
<main class="wrap">{body}
<footer><p class="small mut">OLBG1 independent research snapshot {SNAP}. Originated prices are model outputs from OLBG tip counts only — not bookmaker odds and not financial advice. Fixture/tip data: OLBG (linked per row). 18+ Gamble responsibly: <a href="https://www.begambleaware.org/">BeGambleAware</a> · <a href="https://www.gamcare.org.uk/">GamCare</a>.</p></footer>
</main><script src="assets/site.js"></script></body></html>"""

def fmt(x):
    return "" if x in ("", None) else x

def table(rows, show_sport=False):
    trs = []
    for r in rows:
        price = fmt(r["originated_fair_decimal"])
        prob = fmt(r["model_prob_pct"])
        if r["event_type"] in ("outright","race"):
            priced = f'Tip-share index {esc(r["tip_share_pct"])}% (no full book)' if r["tip_share_pct"]!="" else "—"
        elif price == "":
            priced = "— (no price: see flags)"
        else:
            priced = f'<b>{esc(price)}</b> <span class="mut">({esc(prob)}% model)</span>'
            if r["opponent_fair_decimal"] not in ("", None):
                priced += f'<br><span class="mut">{esc(r["opponent"])} {esc(r["opponent_fair_decimal"])}</span>'
        tips = f'{esc(r["tips_for"])}/{esc(r["tips_total"])} ({esc(r["tip_share_pct"])}%)' if r["tips_total"] not in ("",0) else "—"
        sport_td = f'<td>{esc(r["sport"])}</td>' if show_sport else ""
        flag = f'<br><span class="mut">⚠ {esc(r["flags"])}</span>' if r["flags"] else ""
        trs.append(f'''<tr data-conf="{esc(r["confidence"])}" data-sport="{esc(r["sport"])}">
<td>{esc(r["date_iso"])}<br><span class="mut">{esc(r["date_display"])} {esc(r["time_display"])}*</span></td>{sport_td}
<td><b>{esc(r["match"])}</b><br><span class="mut">{esc(r["competition"])} {esc(r["event_type"])}</span></td>
<td>{esc(r["leading_market"] or "— (not shown)")}<br><b>{esc(r["leading_selection"])}</b><br><span class="mut">Tips {tips} · Experts {esc(r["experts"])}</span></td>
<td><b>{esc(r["winner_pick"] or "— no winner pick")}</b><br><span class="mut small">{esc(r["pick_basis"])}</span></td>
<td>{priced}</td><td><span class="pill {esc(r["confidence"])}">{esc(r["confidence"])}</span>{flag}</td>
<td><a href="{esc(r["olbg_event_url"])}">OLBG event</a><br><a href="{esc(r["olbg_sport_url"])}">OLBG sport</a></td></tr>''')
    sh = "<th>Sport</th>" if show_sport else ""
    return f'''<div class="tbl"><table><thead><tr><th>Date (snapshot)</th>{sh}<th>Match / event</th><th>Leading OLBG market &amp; selection</th><th>Our winner pick</th><th>Our originated fair price†</th><th>Confidence</th><th>Source</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div>
<p class="small mut">* Times exactly as displayed by OLBG at fetch; display timezone was not stated on the page — confirm on the OLBG event page / official league site before use (Flag F-02). † Model price from tip counts only; bookmaker odds were not visible on OLBG pages and are intentionally left blank everywhere (Flag F-03). See <a href="methodology.html">Methodology</a>.</p>'''

# ---------- index ----------
counts = collections.Counter(r["sport"] for r in ROWS)
conf = collections.Counter(r["confidence"] for r in ROWS)
matches_n = sum(1 for r in ROWS if r["event_type"]=="match")
cards = f"""
<div class="cards">
<div class="card"><div class="big">{len(ROWS)}</div><div class="mut">Events in snapshot<br>{matches_n} matches · {len(ROWS)-matches_n} outrights/races</div></div>
<div class="card"><div class="big">{len(SPORTS)}</div><div class="mut">Covered sports<br>(exclusions applied)</div></div>
<div class="card"><div class="big">{conf['High']}</div><div class="mut">High confidence<br><a href="high-confidence.html">Read write-ups →</a></div></div>
<div class="card"><div class="big">{conf['Medium']}</div><div class="mut">Medium confidence</div></div>
<div class="card"><div class="big">{conf['Low']}</div><div class="mut">Low / no-bet<br>thin or split signals</div></div>
</div>"""
sport_links = "".join(f'<li><a href="{SLUG[s]}.html">{esc(s)}</a> — {counts[s]} events · official: <a href="{OFFICIAL[s][1]}">{esc(OFFICIAL[s][0])}</a> · <a href="https://www.olbg.com/betting-tips/{s.replace(chr(32),chr(95))}">OLBG page</a></li>' for s in SPORTS)
sf_opts = '<option value="">All sports</option>' + "".join(f'<option>{esc(s)}</option>' for s in SPORTS)
body = f"""
<h1>OLBG1 Match Board — originated lines &amp; picks</h1>
<p class="mut">Independent snapshot of OLBG.com tip listings taken <b>{SNAP}</b> for 15 sports (of 17 in scope — Aussie Rules &amp; eSports were found via OLBG sitemap by a parallel session and are a logged gap, Flag F-13), with our own originated fair prices, a winner pick and a Low/Medium/High confidence grade for each event. Excluded as requested: soccer/football, boxing/UFC/MMA, American football, hurling, horse racing, cycling and specials (no specials page exists in OLBG's current tips menu — see Flag F-08).</p>
<div class="note"><b>How to read this:</b> "Leading selection" and tip counts are OLBG facts (click through to verify). "Originated fair price" and confidence are <b>our model</b>, computed only from those tip counts — never from invented form or stats. Anything unconfirmable is blank and listed on <a href="flagged.html">Flagged for Review</a>. Full method: <a href="methodology.html">Methodology</a> · Markets: <a href="markets.html">Markets investigated</a>.</div>
{cards}
<h2>Browse by sport</h2><ul>{sport_links}</ul>
<h2>All events</h2>
<div class="controls"><input id="q" placeholder="Search team, player, competition…" size="34" oninput="filt()">
<select id="sf" onchange="filt()">{sf_opts}</select>
<select id="cf" onchange="filt()"><option value="">All confidence</option><option>High</option><option>Medium</option><option>Low</option></select></div>
{table(ROWS, show_sport=True)}
<h2>Key findings (snapshot)</h2>
<ul>
<li>Only <b>5 of 164</b> events clear the High bar (≥7 tips and ≥80% on a winner market). Most OLBG listings carry 1–3 tips, so most grades are honestly Low — a "100%" from one tip is not a strong signal.</li>
<li>Strongest community consensus: Afghanistan over Bangladesh (7/7), Washington Wizards over Milwaukee Bucks (9/11), plus two European Championship darts first-rounders and Leylah Fernandez in Ningbo.</li>
<li>Rugby League listed <b>no matches</b> on the snapshot date (outrights only); Baseball listed one MLB game. Low volume is a calendar fact, not missing data handling.</li>
<li>Handball's 3-way market produced several "Tie" leading selections — flagged individually; do not treat them as winner picks.</li>
</ul>"""
(OUT/"index.html").write_text(page("Dashboard","index.html",body), encoding="utf-8")

# ---------- sport pages ----------
for s in SPORTS:
    rows = [r for r in ROWS if r["sport"]==s]
    off, ourl = OFFICIAL[s]
    b = f"""
<h1>{esc(s)}</h1>
<p class="mut">{len(rows)} events from the OLBG {esc(s)} page on {SNAP}. Verify fixtures on the official site: <a href="{ourl}">{esc(off)}</a> · Tip data source: <a href="{esc(rows[0]['olbg_sport_url'] if rows else '#')}">OLBG {esc(s)}</a>. Markets for this sport: see <a href="markets.html">Markets investigated</a>.</p>
<div class="controls"><input id="q" placeholder="Filter this page…" size="30" oninput="filt()">
<select id="cf" onchange="filt()"><option value="">All confidence</option><option>High</option><option>Medium</option><option>Low</option></select></div>
{table(rows)}
<p><a href="index.html">← Back to dashboard</a></p>"""
    (OUT/f"{SLUG[s]}.html").write_text(page(s, SLUG[s]+".html", b), encoding="utf-8")

# ---------- high confidence ----------
HIGH = [
 dict(title="Tennis · WTA Ningbo Open — Leylah Fernandez to beat Aliaksandra Sasnovich",
  sel="Selection: Leylah Fernandez — Win Match.",
  olbg="https://www.olbg.com/betting-tips/Tennis/All_Tennis/All_Events/Leylah_Fernandez_vs_Aliaksandra_Sasnovich/3?event_id=902039",
  off=[("WTA — Ningbo Open player list","https://www.wtatennis.com/tournaments/2092/ningbo/2026/player-list"),
       ("WTA Tour","https://www.wtatennis.com/"),
       ("ESPN — Fernandez results (Ningbo R1)","https://www.espn.com/tennis/player/_/id/3641/leylah-fernandez"),
       ("ESPN — Sasnovich results (Ningbo R1 + qualifying)","https://www.espn.com/tennis/player/_/id/1809/aliaksandra-sasnovich")],
  facts="OLBG signal: 6/7 tips (86%) — originated fair price 1.29 (77.8% model). Verified: second round, WTA 500 Ningbo Open, 21 Oct 2026; Fernandez WTA No. 30, Sasnovich WTA No. 122 (ESPN/WTA rankings). Fernandez beat seventh seed Elise Mertens 2-6, 6-3, 7-5 in round one; qualifier Sasnovich beat Daria Kasatkina 6-4, 6-2 after two qualifying wins.",
  text="Back Leylah Fernandez to win this match outright. The ranking gap is real — world No. 30 against No. 122 — and Fernandez has just done the hard part in Ningbo, coming from a set down to knock out seventh seed Elise Mertens in three sets. Sasnovich deserves respect: she has come through qualifying and brushed Kasatkina aside in straight sets, so she is match-sharp and dangerous early. But over a full match Fernandez's court speed and return game should ask more questions than Sasnovich faced in round one. Six of seven OLBG tipsters agree, and our numbers make her a clear favourite rather than a coin flip."),
 dict(title="Basketball · NBA — Washington Wizards to beat Milwaukee Bucks (Money Line)",
  sel="Selection: WAS Wizards — Money Line (to win the game). Secondary leans on OLBG-listed lines: Wizards −4.5, Under 239.5 points.",
  olbg="https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIL_Bucks_@_WAS_Wizards/4?event_id=534889",
  off=[("NBA.com — official game page, 21 Oct 2026","https://www.nba.com/game/mil-vs-was-0022600086")],
  facts="OLBG signal: Money Line 9/11 (82%) — originated fair price 1.30 (76.9% model); Pointspread WAS −4.5 5/7; Game Totals Under 239.5 4/4. Verified on NBA.com: season opener, Wed 21 Oct 2026, 7:00 PM ET, Capital One Arena. Washington won the last three meetings (109-99 on 29 Jan 2026, 114-113 on 31 Dec 2025, 129-126 on 1 Dec 2025) and last season's series 3-1. Milwaukee traded Giannis Antetokounmpo (Tyler Herro headline return) and changed head coach (Taylor Jenkins). Washington pair Anthony Davis with Trae Young (four-year extension). IMPORTANT CORRECTION: No. 1 pick AJ Dybantsa is ruled OUT (ankle, per NBA.com preview) — an OLBG tipster comment tipping him to lead Washington is wrong and was not relied on (Flag F-05).",
  text="Take the Washington Wizards on the money line to win their home opener. This is not the Milwaukee side of old: Giannis Antetokounmpo has been traded, the head coach is new, and Washington actually owned this fixture last season, winning the last three meetings — two of them thrillers decided by three points or fewer. With Anthony Davis and Trae Young leading the Wizards at Capital One Arena, home court matters. One honest warning: No. 1 pick AJ Dybantsa misses out with an ankle injury, so ignore any tip built around his debut. Even without him, nine of eleven tipsters and our originated price both side firmly with Washington."),
 dict(title="Cricket · UAE ODI Tri-Series — Afghanistan to beat Bangladesh",
  sel="Selection: Afghanistan — Win Match.",
  olbg="https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Afghanistan_vs_Bangladesh_One_Day_Match/7?event_id=188824",
  off=[("ICC — series announcement & schedule","https://www.icc-cricket.com/news/afghanistan-announce-multi-format-series-against-bangladesh-and-zimbabwe"),
       ("ESPNcricinfo — series schedule/results","https://www.cricinfo.com/series/afghanistan-v-bangladesh-2026-27-1555106/match-schedule-fixtures-and-results")],
  facts="OLBG signal: 7/7 tips (100%), 1 expert — originated fair price 1.12 (88.9% model). Verified (ICC): final league fixture of the ODI tri-series on 21 Oct 2026, final on 23 Oct. Common-opponent form vs Zimbabwe: Afghanistan won by 158 runs (19 Oct); Bangladesh lost by 99 runs, bowled out for 172 (17 Oct). Man-of-the-Match market lean: Rashid Khan 2/4. Venue is disputed between listings (Sharjah v Abu Dhabi) and is therefore not stated as fact (Flag F-06). Individual innings figures quoted in OLBG tipster comments were not independently verified against the ICC scorecard and are not used as facts here.",
  text="Afghanistan to win is the clearest call on the whole board. You rarely get a cleaner form line: against the same Zimbabwe side in this same tri-series, Afghanistan romped home by 158 runs while Bangladesh folded for 172 and lost by 99. That is not ancient history — it happened within the last four days, in the same event, and it leaves Bangladesh needing a huge turnaround just to stay competitive, let alone reach Friday's final. Every one of the seven OLBG tipsters is on Afghanistan, including an expert, and our originated price reflects that dominance. No heroics needed: back the stronger, in-form side to do the job again."),
 dict(title="Darts · European Championship R1 — Niels Zonneveld to beat Cameron Menzies",
  sel="Selection: Niels Zonneveld — Win Match 2-way.",
  olbg="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Niels_Zonneveld_vs_Cameron_Menzies/15?event_id=32334",
  off=[("PDC — official schedule (Thu 22 Oct, Dortmund)","https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/"),
       ("PDC — field & draw (seedings)","https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed")],
  facts="OLBG signal: 6/7 tips (86%) — originated fair price 1.29 (77.8% model). Verified (PDC): Round One, Thursday 22 Oct 2026, Westfalenhalle, Dortmund; Zonneveld is 4th seed, Menzies 29th seed (one-year European Tour rankings). The PDC confirms Zonneveld won the Dutch Darts Championship on 18 Oct — his first European Tour title — days before this match. Short first-round legs format increases variance (noted, not hidden).",
  text="Side with Niels Zonneveld to beat Cameron Menzies and reach round two. Timing is everything here: Zonneveld arrives in Dortmund having just won his first ever European Tour title in the Netherlands on Sunday, a run that lifted him to fourth seed for this championship. Menzies, the 29th seed, is a streaky scorer who can trouble anyone over a short race, so this is no walkover — first-round matches here are notoriously twitchy. But confidence is a genuine edge in darts, and right now nobody in Thursday's session has more of it than Zonneveld. Six of seven tipsters agree, and at our originated price he rates a confident, value-conscious favourite."),
 dict(title="Darts · European Championship R1 — Dirk van Duijvenbode to beat Luke Woodhouse ⚠ read the warning",
  sel="Selection (by the numbers): Dirk van Duijvenbode — Win Match 2-way. More defensive alternative on the OLBG-listed line: van Duijvenbode +1.5 legs; Total Legs lean: Over 9.5.",
  olbg="https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Luke_Woodhouse_vs_Dirk_van_Duijvenbode/15?event_id=32324",
  off=[("PDC — official schedule (Thu 22 Oct, Dortmund)","https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/"),
       ("PDC — field & draw (seedings)","https://www.pdc.tv/news/2026/october/18/2026-Machineseeker-European-Championship-field---draw-confirmed")],
  facts="OLBG signal: Win Match 7/8 (88%), 1 expert — originated fair price 1.25 (80.0% model); Handicap van Duijvenbode +1.5 legs 3/3; Total Legs Over 9.5 4/4. Verified (PDC): Round One, Thursday 22 Oct 2026, Dortmund. Seedings cut AGAINST the tip: Woodhouse is 9th seed, van Duijvenbode 24th. CONTRADICTION (Flag F-04): OLBG's own 'Best Tipster' text for this selection says Woodhouse should edge it on form and head-to-head while the recorded tip is van Duijvenbode. The High grade is therefore a pure tip-count grade with a documented conflict — treat stakes accordingly.",
  text="On numbers alone, Dirk van Duijvenbode to beat Luke Woodhouse is a High-confidence pick: seven of eight tipsters, unanimous support for him with a 1.5-leg start, and everyone expecting a long match over 9.5 legs. But you deserve the full picture before following it. Woodhouse is actually the higher seed here — ninth to van Duijvenbode's 24th — and OLBG's featured tipster comment literally argues Woodhouse should edge it before tipping the other way. If van Duijvenbode scores heavily from the start he can absolutely win this, yet the safer expression of the same opinion is van Duijvenbode +1.5 legs. Back the outright only with eyes open and stakes kept sensible."),
]
cards = ""
for h in HIGH:
    links = " · ".join(f'<a href="{esc(u)}">{esc(t)}</a>' for t,u in h["off"])
    cards += f"""<div class="pick"><h2 style="margin-top:4px">{esc(h['title'])}</h2>
<p><b>{esc(h['sel'])}</b></p><p>{esc(h['text'])}</p>
<div class="ok small"><b>Verified basis:</b> {esc(h['facts'])}</div>
<p class="small">Tip data: <a href="{esc(h['olbg'])}">OLBG event page</a> · Official checks: {links}</p></div>"""
body = f"""
<h1>High-confidence picks ({len(HIGH)})</h1>
<p class="mut">High means: winner market, at least 7 OLBG tips, at least 80% for one side (see <a href="methodology.html">Methodology</a>). Each write-up below uses only facts checked against the official sources linked underneath it. Originated prices are our model prices, not bookmaker odds. If a fact could not be verified officially, it was left out — see the cricket note and Flagged page.</p>
{cards}
<div class="note">No selection is a certainty. Tip-share measures popularity, not value. Only stake what you can afford to lose. 18+.</div>"""
(OUT/"high-confidence.html").write_text(page("High confidence","high-confidence.html",body), encoding="utf-8")

# ---------- markets ----------
body = """
<h1>Markets investigated</h1>
<p class="mut">What OLBG actually offers per sport, taken from OLBG sport-page guides and individual event pages opened on 2026-10-21 (✓ = event page checked). We originate fair prices for winner markets; for handicap/total markets we only record OLBG-listed lines and the verified tip-split lean — we never invent a spread.</p>
<div class="tbl"><table><thead><tr><th>Sport</th><th>Markets on OLBG</th><th>Checked example & our leans</th></tr></thead><tbody>
<tr><td>Tennis</td><td>Win Match · Set Betting · 1st Set Winner · Games Won (handicap) · Total Games · Tournament Winner</td><td>✓ Fernandez v Sasnovich: Win 6/7 Fernandez; Games −3.5 (1/1, thin); Total 21.5 no tips → no lean</td></tr>
<tr><td>Basketball</td><td>Money Line · Pointspread · Game Totals</td><td>✓ MIL @ WAS: ML 9/11 WAS; WAS −4.5 (5/7); Under 239.5 (4/4)</td></tr>
<tr><td>Golf</td><td>Win Tournament (each-way varies)</td><td>Outrights only in snapshot; tip-share index shown, no 2-way price</td></tr>
<tr><td>Cricket</td><td>Win Match · Man Of The Match · Top Team Batsman · Outright Winner</td><td>✓ AFG v BAN: Win 7/7 AFG; MotM Rashid Khan 2/4</td></tr>
<tr><td>Snooker</td><td>Win Match · Handicap Betting (frames) · Frame Betting · Win Tournament</td><td>✓ Wai v Bingham: Win 8/11 Wai; Wai +1.5 frames 4/4; Frame 4-3 Wai 2/3</td></tr>
<tr><td>Rugby Union</td><td>To Win · Handicap · Win Tournament</td><td>Sport-feed handicaps e.g. Ulster +18.5; event pages not individually opened → no extra leans</td></tr>
<tr><td>Rugby League</td><td>Match betting · Handicap · Grand Final Winner</td><td>No matches listed on snapshot date — outrights only</td></tr>
<tr><td>Baseball</td><td>Money Line · Run Line · Game Totals · Ante-post</td><td>One MLB game listed (TB @ MIL), Money Line split 3/6</td></tr>
<tr><td>Ice Hockey</td><td>Money Line · Puck Line · Game Totals</td><td>e.g. Graz −1.5 puck line; NHL Over 5.5 totals (1-tip samples — Low)</td></tr>
<tr><td>Motor Racing</td><td>Fastest Qualifier · Win Race · Podium · Top 6 · Points Finish · Fastest Lap · Win Tournament</td><td>Only Win Race / Win Tournament tipped in snapshot</td></tr>
<tr><td>Darts</td><td>Win Match 2-way · Handicap 2-way · Total Legs/Sets · Tournament Winner</td><td>✓ Woodhouse v DVD: Win 7/8 DVD; DVD +1.5 (3/3); Over 9.5 legs (4/4)</td></tr>
<tr><td>Handball</td><td>Money Line 3-way · Match Handicap · Points Total</td><td>✓ Zagreb v PSG: ML PSG 8/13 (Tie 3, Zagreb 2); Hcp −2.5 & Total 62.5 untipped</td></tr>
<tr><td>Volleyball</td><td>Win Match · Set Score</td><td>Two markets only; no draws possible</td></tr>
<tr><td>Gaelic Football</td><td>Match · Handicap · Outright (labels not shown in feed — flagged)</td><td>Points-line selections imply handicap market</td></tr>
<tr><td>Greyhounds</td><td>Daily Races — win (place/forecast terms vary)</td><td>Most-tipped dog only; full fields not transcribed (flagged)</td></tr>
</tbody></table></div>
<p class="small mut">Settlement rules (overtime, retirements, regular-time-only, etc.) vary by sport and bookmaker — always check the OLBG event page and your bookmaker's rules. Repo detail: <code>research/markets.md</code>.</p>"""
(OUT/"markets.html").write_text(page("Markets","markets.html",body), encoding="utf-8")

# ---------- methodology ----------
body = """
<h1>Methodology — how every number was produced</h1>
<h2>Originated fair price</h2>
<p>For a 2-way winner market with <code>k</code> tips for the leading selection from <code>n</code> total tips:</p>
<ul><li>Model probability <code>p = (k+1)/(n+2)</code> (Laplace smoothing toward 50%, so 1/1 cannot produce a fake 1.00 price)</li>
<li>Originated fair decimal price <code>= 1/p</code>; opponent price <code>= 1/(1-p)</code></li>
<li>Handball 3-way: <code>p = (k+1)/(n+3)</code>. Multi-runner outrights/races: no win price — tip-share index only. Zero-tip rows: no price.</li></ul>
<h2>Winner pick rules</h2>
<ul><li>Winner-market leader → that side. Set-score leader → implied winner (Low cap). Handicap leader → "lean only", never sold as a winner bet. Totals leader → <b>no winner pick</b>. 1st-set leader → "1st-set lean only".</li></ul>
<h2>Confidence rubric</h2>
<div class="tbl"><table><thead><tr><th>Level</th><th>Rule (winner markets; all else Low)</th></tr></thead><tbody>
<tr><td><span class="pill High">High</span></td><td>n ≥ 7 and share ≥ 80%</td></tr>
<tr><td><span class="pill Medium">Medium</span></td><td>(n ≥ 5 and share 60–79%) or (n = 4–6 and share ≥ 80%)</td></tr>
<tr><td><span class="pill Low">Low</span></td><td>Everything else — including "100%" from 1–3 tips</td></tr></tbody></table></div>
<h2>Verification standard</h2>
<ul><li>Every row links to its OLBG event page (source of record for tip data). High picks were additionally checked on official sites (NBA, ICC, PDC, WTA).</li>
<li>OLBG tipster comments are user opinion. They were never copied as facts; two were found wrong/contradictory and are flagged (F-04, F-05).</li>
<li>Bookmaker odds were not visible on fetched OLBG pages, so that field is blank on every row by design.</li>
<li>Reproduce everything: <code>python3 scripts/build_data.py && python3 scripts/build_board.py</code> in the repo. Full text: <code>research/methodology.md</code>, <code>research/verification-log.md</code>.</li></ul>
<div class="note">Tip-share is popularity, not proof of value. This board is research/organisation of public tip data with a transparent model on top — not a guarantee of winners and not financial advice.</div>"""
(OUT/"methodology.html").write_text(page("Methodology","methodology.html",body), encoding="utf-8")

# ---------- flagged ----------
FLAGS = [
 ("F-01","Completeness limit — 'Load More' pagination","OLBG sport pages paginate behind 'Load More Tips'. This board contains every event on the first page of each covered sport at fetch time (164 events). Later-page events, and events added after 2026-10-21, are not included. Re-run the collection before treating any list as 'today's full list'.","All sport URLs in research/olbg-structure.md"),
 ("F-02","Start-time timezone not stated","Times are reproduced exactly as OLBG displayed them; the pages do not state a display timezone. Example: OLBG shows MIL @ WAS at 19:10 while NBA.com (official) lists 7:00 PM ET. Confirm every start time on the official league site before use.","https://www.nba.com/game/mil-vs-was-0022600086"),
 ("F-03","Bookmaker odds unavailable — left blank","Fetched OLBG pages render prices as 'WIN @' with no visible odds, so no market odds could be verified or recorded. All prices on this site are our originated model prices. Do not mistake them for bookmaker prices.","Any OLBG event page, e.g. event 534889"),
 ("F-04","Darts contradiction — Woodhouse v van Duijvenbode","OLBG's 'Best Tipster' comment argues Woodhouse should win on form/H2H while the recorded tip is van Duijvenbode; official PDC seedings also favour Woodhouse (9 v 24). Kept as High strictly by tip-count rubric, with the conflict disclosed in the write-up. Owner may wish to downgrade manually.","https://www.olbg.com/betting-tips/Darts/All_Darts/All_Events/Luke_Woodhouse_vs_Dirk_van_Duijvenbode/15?event_id=32324"),
 ("F-05","Incorrect tipster team news — Wizards","OLBG comments claim rookie AJ Dybantsa will lead Washington vs Milwaukee. The official NBA.com preview rules him OUT (ankle). The pick (Wizards ML) does not depend on him, but any Dybantsa-based reasoning elsewhere should be disregarded.","https://www.nba.com/game/mil-vs-was-0022600086"),
 ("F-06","Cricket venue conflict — Afghanistan v Bangladesh","Listings disagree on the 21 Oct venue (Sharjah v Abu Dhabi). The fixture/date are ICC-confirmed; the venue is left unstated on this site until the official scorecard settles it.","https://www.icc-cricket.com/news/afghanistan-announce-multi-format-series-against-bangladesh-and-zimbabwe"),
 ("F-07","Gaelic Football — scope interpretation + missing market labels","Included on the reading that 'football' exclusion = soccer (OLBG ID 1) + American football (ID 11). If Gaelic was intended to be excluded, delete the 5 Gaelic rows/page. Separately, OLBG's Gaelic feed shows no market label; points-line selections were treated as handicap leans.","https://www.olbg.com/betting-tips/Gaelic_Football/25"),
 ("F-08","'Specials' — nothing to exclude","No Specials category appears in OLBG's current tips sport menu, so no rows were removed under that heading. Flagged in case specials appear under another OLBG section.","https://www.olbg.com/betting-tips"),
 ("F-09","Handball 'Tie' leading selections","Four handball matches are led by the Tie in the 3-way market (e.g. Aalborg v Celje 4/5). Ties are legitimate but unusual leaders on tiny samples; all graded Low. Verify on the event page before any use.","https://www.olbg.com/betting-tips/Handball/20"),
 ("F-10","Rows with no/partial tip data","Hero Womens Indian Open and T20 Blast 2027 showed 0 tips (no price originated); La Rochelle v Bordeaux tip counts were cut off in the fetch (pick shown without counts, no price). All flagged in-row in the tables.","OLBG event pages 101909, 188350, 609554"),
 ("F-11","Greyhounds — winner-only snapshot","Only the most-tipped dog per race is recorded; full fields, traps, grades and times beyond the race title were not transcribed. Six early races only — a full day's cards are far larger (see F-01).","https://www.olbg.com/betting-tips/Greyhounds/28"),
 ("F-13","Two in-scope sports missing from this board","A parallel session (ce5920e3) enumerated OLBG via its XML sitemap and found Aussie Rules (ID 22) and eSports (ID 23), absent from the HTML sport menu used here. This board covers 15 of 17 in-scope sports; no rows were invented to fill the gap. The root dashboard (same repo) documents full 22-sport taxonomy.","data/olbg_taxonomy.json in repo; COORDINATION.md section 6"),
 ("F-12","Snapshot decay","Tips accumulate and fixtures start/finish continuously. Tip counts, shares and therefore originated prices/confidence were true only at the 2026-10-21 fetch. Treat 'Today/Tomorrow' labels as 21/22 Oct 2026 respectively.","data/matches.csv (snapshot_date column)"),
]
trs = "".join(f'<tr><td><b>{esc(a)}</b></td><td><b>{esc(b)}</b><br>{esc(c)}</td><td class="small">{esc(d)}</td></tr>' for a,b,c,d in FLAGS)
body = f"""
<h1>Flagged for Review</h1>
<p class="mut">Everything below is <b>published, not hidden</b> — none of it blocks the site, but all of it should be read before acting on any pick. Status in COORDINATION.md terms: <b>needs review</b>. Unverified values were left blank in the data rather than filled in.</p>
<div class="tbl"><table><thead><tr><th>ID</th><th>Irregularity / limitation</th><th>Check it here</th></tr></thead><tbody>{trs}</tbody></table></div>
<p>Request changes after review (e.g. remove Gaelic Football, downgrade F-04, refresh the snapshot) and the board can be rebuilt from <code>scripts/build_data.py</code>.</p>"""
(OUT/"flagged.html").write_text(page("Flagged for Review","flagged.html",body), encoding="utf-8")

(OUT/"assets/style.css").write_text(CSS, encoding="utf-8")
(OUT/"assets/site.js").write_text(JS, encoding="utf-8")
print("site written:", sorted(p.name for p in OUT.glob("*.html")))
