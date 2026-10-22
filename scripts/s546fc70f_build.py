"""Builds the namespaced desk /546fc70f/ from data/546fc70f/*.json|csv (no network access).
All numbers come from data/546fc70f/model_output.json (produced by scripts/s546fc70f_model.py)."""
import csv, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "546fc70f")
OUT = os.path.join(ROOT, "546fc70f")
SPORTS_OUT = os.path.join(OUT, "sports")

EL_RESULTS = "https://api-live.euroleague.net/v1/results?seasonCode=E2026"
EL_SCHEDULE = "https://api-live.euroleague.net/v1/schedules?seasonCode=E2026&limit=5"
NHL_STANDINGS = "https://api-web.nhle.com/v1/standings/now"
NHL_SCORE = "https://api-web.nhle.com/v1/score/2026-10-22"
NHL_SCHEDULE = "https://api-web.nhle.com/v1/schedule/2026-10-22"
MLB_SCHEDULE = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=10/22/2026"
NBA_SCOREBOARD = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
ATP_SCORES = "https://www.atptour.com/en/scores/current"
ATP_RANKINGS = "https://www.atptour.com/en/rankings/singles"
OLBG_HOCKEY = "https://www.olbg.com/betting-tips/Ice_Hockey/13"
OLBG_ROBOTS = "https://www.olbg.com/robots.txt"

CATEGORIES = [
    ("tennis", "Tennis", "Not covered in this desk. ATP scores and rankings pages were read (discovery only); no ATP match was priced."),
    ("basketball", "Basketball", "EuroLeague only. Official E2026 results and schedule read; the NBA official scoreboard returned HTTP 500 and is not covered."),
    ("golf", "Golf", "Not covered in this desk. No official golf source was read."),
    ("cricket", "Cricket", "Not covered in this desk. No official cricket source was read."),
    ("snooker", "Snooker", "Not covered in this desk. No official snooker source was read."),
    ("rugby-union", "Rugby Union", "Not covered in this desk. No official rugby union source was read."),
    ("rugby-league", "Rugby League", "Not covered in this desk. No official rugby league source was read."),
    ("baseball", "Baseball", "MLB Stats API (official) returned zero games for 2026-10-22, so there is nothing to price on that date. Other dates not covered."),
    ("ice-hockey", "Ice Hockey", "NHL only. Official standings and score/schedule feeds read; 4 of the 12 games on 22 Oct confirmed in the official feed and priced; 8 not confirmed."),
    ("motor-racing", "Motor Racing", "Not covered in this desk. No official motor racing source was read."),
    ("darts", "Darts", "Not covered in this desk. No official PDC fixture or statistics page was read (pdc.tv loaded only its cookie banner)."),
    ("handball", "Handball", "Not covered in this desk. No official EHF source was read."),
    ("volleyball", "Volleyball", "Not covered in this desk. No official volleyball source was read."),
    ("aussie-rules", "Aussie Rules", "Not covered in this desk. No official AFL source was read."),
    ("esports", "eSports", "Not covered in this desk. No official eSports source was read."),
    ("gaelic-football", "Gaelic Football", "Not covered in this desk. No official GAA source was read."),
    ("greyhounds", "Greyhounds", "Not covered in this desk. No official GBGB source was read."),
]
CAT_TITLE = {c[0]: c[1] for c in CATEGORIES}
CAT_NOTE = {c[0]: c[2] for c in CATEGORIES}

CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1d2330;background:#f6f7fb;line-height:1.45}
header{background:#14213d;color:#fff;padding:14px 20px}
header a{color:#fff;margin-right:14px;text-decoration:none;font-size:14px}
header .brand{font-weight:700;margin-right:24px;font-size:16px}
main{max-width:1200px;margin:0 auto;padding:18px 20px 40px}
h1{font-size:24px;margin:6px 0 10px} h2{font-size:18px;margin:24px 0 8px}
.note{background:#fff8e1;border:1px solid #f0d98a;padding:10px 12px;border-radius:6px;font-size:14px}
.kpis{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
.kpi{background:#fff;border:1px solid #dfe3ee;border-radius:8px;padding:10px 14px;min-width:150px}
.kpi b{display:block;font-size:22px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.card{background:#fff;border:1px solid #dfe3ee;border-radius:8px;padding:10px 12px;font-size:14px}
.card a{font-weight:600;color:#1d4ed8;text-decoration:none}
table{border-collapse:collapse;width:100%;background:#fff;font-size:13px;margin:8px 0 16px}
th,td{border-bottom:1px solid #e6e9f2;padding:6px 8px;text-align:left;vertical-align:top}
th{background:#eef1f8;position:sticky;top:0}
tr:hover td{background:#fafbff}
.tier-High{color:#0a7d33;font-weight:700} .tier-Medium{color:#9a6700;font-weight:700} .tier-Low{color:#555;font-weight:600}
.flag{color:#b42318;font-weight:600}
a{color:#1d4ed8}
.small{font-size:12px;color:#55607a}
.pred{background:#fff;border:1px solid #dfe3ee;border-radius:8px;padding:12px 14px;margin:10px 0}
.pred p{margin:6px 0}
"""

NAV = [("index.html", "Dashboard"), ("matches.html", "Matches"), ("markets.html", "Markets"),
       ("high-confidence.html", "High confidence"), ("predictions.html", "Predictions"),
       ("analysis.html", "Analysis"), ("sports.html", "Sports"), ("flagged.html", "Flagged for Review"),
       ("sources.html", "Sources")]


def page(title, body, depth=0):
    prefix = "../" * depth
    nav = "".join(f'<a href="{prefix}{h}">{html.escape(t)}</a>' for h, t in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · 546fc70f desk</title><style>{CSS}</style></head>
<body><header><span class="brand">OLBG1 · 546fc70f desk</span>{nav}</header>
<main>{body}
<p class="small">Not affiliated with OLBG. Experimental model prices, not bookmaker odds. No guaranteed returns and no personal staking advice. Generated 2026-10-22 from official endpoints read in this session.</p>
</main></body></html>
"""


def esc(x):
    return html.escape(str(x))


def link(url, text=None):
    return f'<a href="{esc(url)}" rel="noopener">{esc(text or url)}</a>'


def tier_html(t):
    return f'<span class="tier-{esc(t)}">{esc(t)}</span>' if t in ("High", "Medium", "Low") else esc(t)


def load():
    model = json.load(open(os.path.join(DATA, "model_output.json"), encoding="utf-8"))
    preds = json.load(open(os.path.join(DATA, "predictions.json"), encoding="utf-8"))
    return model, preds


def fixture_source(f):
    if f["sport"].startswith("EuroLeague"):
        return EL_SCHEDULE, EL_RESULTS
    return NHL_SCORE if str(f["game_no"]) in ("2026020154", "2026020155") else NHL_SCHEDULE, NHL_STANDINGS


def winner_rows(model):
    rows = []
    for f in model["fixtures"]:
        w = [k for k in f["markets"] if k["market"].startswith("Match winner")]
        best = max(w, key=lambda k: k["p"])
        other = [k for k in w if k is not best][0]
        rows.append((f, best, other))
    rows.sort(key=lambda r: -r[1]["p"])
    return rows


def build():
    model, preds = load()
    W = winner_rows(model)
    tiers = {"High": 0, "Medium": 0, "Low": 0}
    for f, b, o in W:
        tiers[b["tier"]] += 1
    n_fix = len(model["fixtures"])
    n_el = sum(1 for f in model["fixtures"] if f["sport"].startswith("EuroLeague"))
    n_nhl = n_fix - n_el
    n_markets = sum(len(f["markets"]) for f in model["fixtures"])
    n_flags = len(FLAGS)
    os.makedirs(SPORTS_OUT, exist_ok=True)

    # ---------- landing ----------
    cards = "".join(
        f'<div class="card"><a href="sports/{slug}.html">{esc(name)}</a><div class="small">{esc(note[:140])}{"…" if len(note)>140 else ""}</div></div>'
        for slug, name, note in CATEGORIES)
    top = W[:5]
    top_rows = "".join(
        f"<tr><td>{esc(f['sport'])}</td><td>{esc(f['home'])} v {esc(f['away'])}</td><td>{esc(b['selection'])}</td>"
        f"<td>{b['p']*100:.1f}%</td><td>{b['american']:+d}</td><td>{tier_html(b['tier'])}</td>"
        f"<td>{link(fixture_source(f)[0], 'official fixture')}</td></tr>" for f, b, o in top)
    index = f"""<h1>Evidence-first desk, 22 October 2026</h1>
<div class="note"><b>Read this first.</b> Only two of the 17 in-scope sports were verified against official feeds in this session: EuroLeague basketball and the NHL. Everything else is listed as not covered. The High tier is <b>empty</b>: no winner pick met the brief's strict rule (probability above 70% <i>and</i> price between -250 and +10000). Predictions are published for the five strongest EuroLeague picks and the four confirmed NHL games, and each is labelled with its real tier.</div>
<div class="kpis">
<div class="kpi"><b>{n_fix}</b>official fixtures priced ({n_el} EuroLeague, {n_nhl} NHL)</div>
<div class="kpi"><b>{n_markets}</b>originated market rows</div>
<div class="kpi"><b>{tiers['High']}</b>High picks (strict)</div>
<div class="kpi"><b>{tiers['Medium']}</b>Medium picks</div>
<div class="kpi"><b>{tiers['Low']}</b>Low picks</div>
<div class="kpi"><b>{n_flags}</b>items on Flagged for Review</div>
</div>
<h2>Categories (17 in scope)</h2>
<div class="grid">{cards}</div>
<h2>Five strongest winner picks this desk</h2>
<table><tr><th>Sport</th><th>Match</th><th>Pick</th><th>Model probability</th><th>Fair American</th><th>Tier</th><th>Source</th></tr>{top_rows}</table>
<p class="small">The fair American price is our own estimate derived from the official inputs. It is not a bookmaker price. The tier applies to the winner pick only.</p>
"""
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page("Dashboard", index))

    # ---------- matches ----------
    rows = []
    for f, b, o in W:
        fs, ss = fixture_source(f)
        rows.append(f"<tr><td>{esc(f['sport'])}</td><td>{esc(f['game_no'])}</td><td>{esc(f['date_as_published'])}</td>"
                    f"<td>{esc(f['time_as_published'])}</td><td>{esc(f['home'])} v {esc(f['away'])}</td>"
                    f"<td>{esc(f['home_record'])} / {esc(f['away_record'])}</td>"
                    f"<td>{f['expected_margin_home']:+.2f}</td><td>{f['expected_total']:.1f}</td>"
                    f"<td>{esc(b['selection'])}</td><td>{b['p']*100:.1f}%</td><td>{b['american']:+d}</td>"
                    f"<td>{tier_html(b['tier'])}</td><td class='small'>{esc(b['tier_note'])}</td>"
                    f"<td>{link(fs,'fixture')}<br>{link(ss,'results/standings')}</td></tr>")
    matches = f"""<h1>All priced fixtures</h1>
<div class="note">Times are shown exactly as the official source publishes them. The time zone is not stated by the EuroLeague feed, so no time zone has been assumed. NHL times are UTC from the official feed. Expected margin is in points (EuroLeague) or goals (NHL, from Poisson rates). Records: wins-losses (EuroLeague), wins-losses-OT losses (NHL).</div>
<table><tr><th>Sport</th><th>Game</th><th>Date</th><th>Time (as published)</th><th>Match (home v away)</th><th>Record H / A</th><th>Exp. margin (home)</th><th>Exp. total</th><th>Winner pick</th><th>Model p</th><th>Fair American</th><th>Tier</th><th>Note</th><th>Source</th></tr>
{''.join(rows)}</table>"""
    open(os.path.join(OUT, "matches.html"), "w", encoding="utf-8").write(page("Matches", matches))

    # ---------- markets ----------
    mrows = []
    for f in model["fixtures"]:
        fs, ss = fixture_source(f)
        for k in f["markets"]:
            t = tier_html(k["tier"]) if k["tier"] in ("High", "Medium", "Low") else "lean only (not a winner pick)"
            mrows.append(f"<tr><td>{esc(f['sport'])}</td><td>{esc(f['home'])} v {esc(f['away'])}</td><td>{esc(k['market'])}</td>"
                         f"<td>{esc(k['selection'])}</td><td>{k['p']*100:.1f}%</td><td>{k['american']:+d}</td>"
                         f"<td>{k['decimal']:.3f}</td><td>{t}</td><td>{link(fs,'fixture')}</td></tr>")
    markets = f"""<h1>Originated markets</h1>
<div class="note">Match winner, handicap ladder, total ladder (EuroLeague) and puck line / total goals (NHL). Non-winner rows show a lean probability only and carry no confidence tier. Fair prices are model estimates, not bookmaker odds.</div>
<table><tr><th>Sport</th><th>Match</th><th>Market</th><th>Selection</th><th>Model p</th><th>Fair American</th><th>Fair decimal</th><th>Tier</th><th>Source</th></tr>
{''.join(mrows)}</table>"""
    open(os.path.join(OUT, "markets.html"), "w", encoding="utf-8").write(page("Markets", markets))

    # ---------- high confidence gate ----------
    gate_rows = []
    for f, b, o in W:
        strict = b["p"] > 0.70 and -250 <= b["american"] <= 10000
        gate_rows.append(f"<tr><td>{esc(f['sport'])}</td><td>{esc(f['home'])} v {esc(f['away'])}</td><td>{esc(b['selection'])}</td>"
                         f"<td>{b['p']*100:.2f}%</td><td>{b['american']:+d}</td>"
                         f"<td>{'yes' if b['p']>0.70 else 'no'}</td><td>{'yes' if -250 <= b['american'] <= 10000 else 'no'}</td>"
                         f"<td>{'<span class=tier-High>PASS (High)</span>' if strict else 'fail'}</td>"
                         f"<td>{tier_html(b['tier'])}</td><td>{link(fixture_source(f)[0],'fixture')}</td></tr>")
    hc = f"""<h1>High-confidence gate</h1>
<div class="note"><b>Result: {tiers['High']} High picks.</b> The brief asks for a probability above 70% and a price between -250 and +10000. These two tests cannot both pass for a favourite unless the probability sits in a very narrow band: a price of -250 implies 71.4%, and a price of -233 implies 70%. So the test is effectively p in (70.0%, 71.4%]. Under the brief's own literal rule nothing in this desk passes. Probabilities above 71.4% are priced shorter than -250 and are labelled Medium, flagged as outside the window. We did not lower the bar to fill a quota.</div>
<table><tr><th>Sport</th><th>Match</th><th>Winner pick</th><th>Model p</th><th>Fair American</th><th>p &gt; 70%?</th><th>Price in -250..+10000?</th><th>High gate</th><th>Tier</th><th>Source</th></tr>
{''.join(gate_rows)}</table>
<h2>Near misses (for review)</h2>
<ul>
<li>Valencia Basket at Paris Basketball (EuroLeague game 69): p = 71.7%, fair price -253. Three points outside the window. <a href="predictions.html#P546-03">Prediction P546-03</a>.</li>
<li>Real Madrid at Kosner Baskonia (game 73): p = 74.7%, fair price -295. Outside the window. <a href="predictions.html#P546-02">Prediction P546-02</a>.</li>
<li>Panathinaikos v Armani Olimpia Milan (game 76): p = 84.7%, fair price -555. Outside the window. <a href="predictions.html#P546-01">Prediction P546-01</a>.</li>
</ul>"""
    open(os.path.join(OUT, "high-confidence.html"), "w", encoding="utf-8").write(page("High confidence", hc))

    # ---------- predictions ----------
    pb = []
    for p in preds:
        words = len(re.findall(r"\S+", p["text"]))
        srcs = " · ".join(link(u, u.split("?")[0].split("/v1/")[-1][:60]) for u in p["sources"])
        pb.append(f"""<div class="pred" id="{p['id']}"><div class="small">{esc(p['id'])} · {esc(p['sport'])} · {esc(p['fixture_ref'])}</div>
<h3 style="margin:6px 0">{esc(p['selection'])}</h3>
<p>Tier: {tier_html(p['tier'])} · Model p {p['model_p']*100:.1f}% · Fair American {p['fair_american']:+d} · {words} words</p>
<p>{esc(p['text'])}</p>
<p class="small">Official sources: {srcs}</p></div>""")
    preds_html = f"""<h1>Predictions (5 EuroLeague, 4 NHL)</h1>
<div class="note">The brief asks for predictions on the five highest-confidence picks per covered sport. This desk has no High pick, so each prediction states its real tier and is not labelled High. Each one names the team, the selection, the official record and recent results read from the feed. Player-level form is included only where an official feed listed it (NHL team leaders). Where it was not verified, the text says so.</div>
{''.join(pb)}"""
    open(os.path.join(OUT, "predictions.html"), "w", encoding="utf-8").write(page("Predictions", preds_html))

    # ---------- analysis ----------
    bt = model["backtest_euroleague"]
    bt_rows = "".join(f"<tr><td>{esc(k)}</td><td>{v['n']}</td><td>{v['mean_fav_p']*100:.1f}%</td><td>{v['observed_fav_win_rate']*100:.1f}%</td></tr>"
                      for k, v in bt["calibration_by_favourite_band"].items())
    a = model["assumptions"]
    analysis = f"""<h1>Method, assumptions and backtest</h1>
<h2>Inputs</h2>
<ul>
<li>EuroLeague E2026 official results: {link(EL_RESULTS)} (66 played games).</li>
<li>EuroLeague E2026 official schedule: {link(EL_SCHEDULE)} (14 upcoming games in the next two rounds).</li>
<li>NHL official standings: {link(NHL_STANDINGS)} (32 teams, date stamp 2026-10-22 20:49 UTC).</li>
<li>NHL official score and schedule feeds: {link(NHL_SCORE)} and {link(NHL_SCHEDULE)} (4 games confirmed with official start times).</li>
</ul>
<h2>Model (our estimates, not sourced facts)</h2>
<table><tr><th>Parameter</th><th>Value</th><th>Status</th></tr>
<tr><td>EuroLeague shrinkage</td><td>{a['EL_SHRINK_K']} pseudo-games at league average</td><td>Assumption</td></tr>
<tr><td>EuroLeague margin SD (sample)</td><td>{a['EL_sigma_margin_sample_sd']} points</td><td>Computed from the 66 official games</td></tr>
<tr><td>EuroLeague total SD (sample)</td><td>{a['EL_sigma_total_sample_sd']} points</td><td>Computed from the 66 official games</td></tr>
<tr><td>EuroLeague league average</td><td>{a['EL_league_pts_per_team_per_game']} points per team per game</td><td>Computed</td></tr>
<tr><td>NHL shrinkage</td><td>{a['NHL_SHRINK_K']} pseudo-games at league average</td><td>Assumption</td></tr>
<tr><td>NHL league average</td><td>{a['NHL_league_goals_per_team_per_game']} goals per team per game</td><td>Computed from standings</td></tr>
<tr><td>Home advantage</td><td>{esc(a['home_advantage_term'])}</td><td>Not applied: no official value sourced</td></tr>
</table>
<h2>Walk-forward backtest (EuroLeague winner model)</h2>
<p>Each of the {bt['n_predictions']} games from rounds 3 to 7 is predicted using only games from earlier rounds. Log loss {bt['log_loss_model']} against {bt['log_loss_coin_flip_baseline']} for a coin flip. Brier {bt['brier_model']}. Accuracy {bt['accuracy_model']*100:.1f}%.</p>
<table><tr><th>Favourite band</th><th>Games</th><th>Mean favourite probability</th><th>Observed favourite win rate</th></tr>{bt_rows}</table>
<p class="small">{esc(bt['note'])} The 60-70% band won 80% of its games against a mean probability of 63.7%, which suggests the model under-rates that band. The 70%+ band has only four games, so no calibration claim is made for it.</p>
<h2>Limits</h2>
<ul>
<li>No injuries, rest, travel, roster or player-level data. No home-court term.</li>
<li>No bookmaker prices were used or verified. Every price here is our own estimate.</li>
<li>NHL was not backtested: the feed gave season totals only, not game-by-game results.</li>
<li>Only 4 NHL games were confirmed in the official feed this session (see Flagged for Review).</li>
</ul>"""
    open(os.path.join(OUT, "analysis.html"), "w", encoding="utf-8").write(page("Analysis", analysis))

    # ---------- flagged ----------
    frows = "".join(f"<tr><td>{esc(fid)}</td><td>{esc(sev)}</td><td>{esc(txt)}</td><td>{' · '.join(link(u, label) for u,label in srcs)}</td></tr>"
                    for fid, sev, txt, srcs in FLAGS)
    unverified = "".join(f"<li>{esc(x)}</li>" for x in UNVERIFIED)
    flagged = f"""<h1>Flagged for Review</h1>
<div class="note">Irregularities and unverified items are published here for review. They do not block the merge. Each flag links to the official page or the OLBG page where it was observed.</div>
<table><tr><th>ID</th><th>Severity</th><th>Finding</th><th>Source</th></tr>{frows}</table>
<h2>Unverified items (not priced, no official value confirmed)</h2>
<ul>{unverified}</ul>"""
    open(os.path.join(OUT, "flagged.html"), "w", encoding="utf-8").write(page("Flagged for Review", flagged))

    # ---------- sources ----------
    srows = "".join(f"<tr><td>{link(u)}</td><td>{esc(what)}</td><td>{esc(status)}</td><td>{esc(used)}</td></tr>" for u, what, status, used in SOURCES)
    sources = f"""<h1>Sources read this session</h1>
<div class="note">Only endpoints listed here were read. "Official" means the league, governing body, tour or team's own domain. OLBG pages are discovery only, not verification.</div>
<table><tr><th>URL</th><th>What was read</th><th>Result</th><th>Used for</th></tr>{srows}</table>"""
    open(os.path.join(OUT, "sources.html"), "w", encoding="utf-8").write(page("Sources", sources))

    # ---------- sports index + subpages ----------
    sp = "".join(f'<li><a href="sports/{s}.html">{esc(n)}</a></li>' for s, n, _ in CATEGORIES)
    open(os.path.join(OUT, "sports.html"), "w", encoding="utf-8").write(page("Sports", f"<h1>Sports (17 in scope)</h1><ul>{sp}</ul>"))
    for slug, name, note in CATEGORIES:
        body = f"<h1>{esc(name)}</h1><div class='note'>{esc(note)}</div>"
        if slug == "basketball":
            rr = [r for r in W if r[0]["sport"].startswith("EuroLeague")]
            trs = "".join(f"<tr><td>{esc(f['game_no'])}</td><td>{esc(f['date_as_published'])} {esc(f['time_as_published'])}</td><td>{esc(f['home'])} v {esc(f['away'])}</td><td>{esc(b['selection'])}</td><td>{b['p']*100:.1f}%</td><td>{b['american']:+d}</td><td>{tier_html(b['tier'])}</td><td>{link(fixture_source(f)[0],'fixture')} · {link(EL_RESULTS,'results')}</td></tr>" for f,b,o in rr)
            body += f"<table><tr><th>Game</th><th>Date and time (as published, zone not stated)</th><th>Match</th><th>Winner pick</th><th>Model p</th><th>Fair American</th><th>Tier</th><th>Source</th></tr>{trs}</table>"
        elif slug == "ice-hockey":
            rr = [r for r in W if r[0]["sport"].startswith("NHL")]
            trs = "".join(f"<tr><td>{esc(f['game_no'])}</td><td>{esc(f['time_as_published'])}</td><td>{esc(f['home'])} v {esc(f['away'])}</td><td>{esc(b['selection'])}</td><td>{b['p']*100:.1f}%</td><td>{b['american']:+d}</td><td>{tier_html(b['tier'])}</td><td>{link(fixture_source(f)[0],'score feed')} · {link(NHL_STANDINGS,'standings')}</td></tr>" for f,b,o in rr)
            body += f"<table><tr><th>NHL game ID</th><th>Start (UTC, official)</th><th>Match</th><th>Winner pick</th><th>Model p</th><th>Fair American</th><th>Tier</th><th>Source</th></tr>{trs}</table>"
            body += "<h2>OLBG-listed games not confirmed by the official feed (not priced)</h2><ul>" + "".join(f"<li>{esc(x)}</li>" for x in NHL_UNCONFIRMED) + "</ul>"
        elif slug == "baseball":
            body += f"<p>Source checked: {link(MLB_SCHEDULE)} returned <code>totalGames: 0</code> for 10/22/2026.</p>"
        else:
            body += "<p class='small'>No rows are published for this category in this desk. See the Flagged for Review page for the coverage gap.</p>"
        open(os.path.join(SPORTS_OUT, f"{slug}.html"), "w", encoding="utf-8").write(page(name, body, depth=1))

    print("built pages:", len(os.listdir(OUT)), "root files;", len(os.listdir(SPORTS_OUT)), "sports pages")
    print("tiers", tiers, "fixtures", n_fix, "markets", n_markets, "flags", n_flags)


NHL_UNCONFIRMED = [
    "FLA Panthers at PIT Penguins (OLBG event 199934): not confirmed in the official NHL feed read this session.",
    "VGK Golden Knights at STL Blues (OLBG event 199940): not confirmed in the official feed read this session.",
    "CAR Hurricanes at EDM Oilers (OLBG event 199931): not confirmed in the official feed read this session.",
    "DET Red Wings at VAN Canucks (OLBG event 199933): not confirmed in the official feed read this session.",
    "WPG Jets at DAL Stars (OLBG event 199941): not confirmed in the official feed read this session.",
    "MIN Wild at CGY Flames (OLBG event 199935): not confirmed in the official feed read this session.",
    "LA Kings at NY Islanders (OLBG event 199938): not confirmed in the official feed read this session.",
    "UTA Mammoth at SEA Kraken (OLBG event 199939): not confirmed in the official feed read this session.",
]

UNVERIFIED = [
    "Eight of the twelve NHL games listed on OLBG for 22 October (see the Ice Hockey page). Official confirmation was not completed this session, so they are not priced.",
    "EuroLeague kick-off times. The official feed publishes two time columns with no time-zone label, so no time zone has been assumed.",
    "EuroLeague game 66 (Partizan v Crvena Zvezda, published 20:45 on 22 Oct). The feed still shows it unplayed, but its published time may already have passed at build time. Status unverified.",
    "All player-level form for EuroLeague (the feed read was game-level only).",
    "All NHL recent match-by-match form (the standings were read as season totals).",
    "Any bookmaker price (none was verified; OLBG tip percentages are votes and were not used as probabilities).",
    "Fifteen of the seventeen in-scope categories (see the Sports page).",
]

FLAGS = [
    ("F-546-01", "Medium", "OLBG hub lists the NSH @ BOS game as 'Today 19:07'. The official NHL feed gives a start of 23:00 UTC (19:00 Eastern). A 7-minute discrepancy on the discovery source.",
     [(OLBG_HOCKEY, "OLBG hub (discovery)"), (NHL_SCORE, "NHL score feed (official)")]),
    ("F-546-02", "High", "Coverage gap: 15 of 17 in-scope categories have no official source read in this session. Only EuroLeague and the NHL were priced.",
     [(MLB_SCHEDULE, "MLB Stats API (official)"), (ATP_SCORES, "ATP scores (read, not used)")]),
    ("F-546-03", "Medium", "NBA official scoreboard returned HTTP 500, so NBA could not be verified.",
     [(NBA_SCOREBOARD, "NBA scoreboard (HTTP 500)")]),
    ("F-546-04", "Medium", "EuroLeague feed publishes two time columns (for example 20:15 and 23:45) with no time-zone label. Kick-off times are shown as published and not converted.",
     [(EL_SCHEDULE, "EuroLeague schedule (official)")]),
    ("F-546-05", "Medium", "EuroLeague game 66 (Partizan v Crvena Zvezda) shows played=false, but its published time (20:45 on 22 Oct) may already have passed when this desk was built. Status not confirmed.",
     [(EL_SCHEDULE, "EuroLeague schedule (official)")]),
    ("F-546-06", "High", "High tier is empty. The brief's price window (-250..+10000) and the >70% rule only overlap for p in (70.0%, 71.4%]. No pick falls in that band.",
     [(EL_SCHEDULE, "EuroLeague schedule (official)"), (NHL_STANDINGS, "NHL standings (official)")]),
    ("F-546-07", "Medium", "Eight of the twelve NHL games listed on OLBG for 22 Oct are not confirmed by the official feed read here. Not priced.",
     [(OLBG_HOCKEY, "OLBG hub (discovery)"), (NHL_SCHEDULE, "NHL schedule (official)")]),
    ("F-546-08", "Medium", "EuroLeague backtest: the 60-70% favourite band won 80% of 20 games against a mean of 63.7%, suggesting under-rating. The 70%+ band has only four games. Small sample; no recalibration applied.",
     [(EL_RESULTS, "EuroLeague results (official)")]),
    ("F-546-09", "Low", "Model has no home-court term and no injury, roster or rest data. Probabilities are estimates, not verified facts.",
     [(EL_RESULTS, "EuroLeague results (official)")]),
    ("F-546-10", "Low", "OLBG tip percentages are user votes, not probabilities. They were not used in any calculation.",
     [(OLBG_HOCKEY, "OLBG hub (discovery)")]),
    ("F-546-11", "Medium", "Repository state: COORDINATION.md lists T97DC and T-FEC as in progress with no recent commits (more than 60 minutes), and two other PRs (#40, #63) are still open. These were left untouched.",
     [("https://github.com/buffedlizard55-lab/OLBG1/pull/63", "PR #63 (open)"), ("https://github.com/buffedlizard55-lab/OLBG1/pull/40", "PR #40 (open)")]),
]

SOURCES = [
    (EL_RESULTS, "EuroLeague E2026 results: 66 played games with scores", "Read in full (1 chunk)", "Records, points for and against, last three results, backtest"),
    (EL_SCHEDULE, "EuroLeague E2026 schedule (chunks 0 and 1)", "Read rounds 1 to 12", "Upcoming games in rounds 7 and 8 (14 games)"),
    (NHL_STANDINGS, "NHL standings snapshot (8 chunks, all 32 teams)", "Read in full", "Team records and goals for and against"),
    (NHL_SCORE, "NHL score feed for 22 Oct (first chunk)", "Read games 2026020154 and 2026020155, plus team leaders", "Official start times, records, team leaders"),
    (NHL_SCHEDULE, "NHL schedule for 22 Oct (first chunk)", "Read games 2026020156 and 2026020157", "Official start times"),
    (MLB_SCHEDULE, "MLB Stats API schedule, sportId 1, 10/22/2026", "Returned totalGames 0", "Baseball coverage check"),
    (NBA_SCOREBOARD, "NBA live scoreboard JSON", "HTTP 500", "NBA coverage check (failed)"),
    (ATP_SCORES, "ATP scores page (current)", "Read first chunk (completed Round of 16 matches listed)", "Coverage check only; no tennis priced"),
    (ATP_RANKINGS, "ATP singles rankings page", "Read first chunk (navigation only)", "Coverage check only"),
    (OLBG_HOCKEY, "OLBG Ice Hockey betting-tips hub (first chunk)", "Read; 12 NHL events listed", "Discovery only, not verification"),
    (OLBG_ROBOTS, "OLBG robots.txt", "Read; /betting-tips/ not disallowed for generic agents", "Access check"),
]

if __name__ == "__main__":
    build()
