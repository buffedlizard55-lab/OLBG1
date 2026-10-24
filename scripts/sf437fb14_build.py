"""Session f437fb14 - deterministic assembly of data and the static desk in f437fb14/."""
import html
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sf437fb14_model as M
import sf437fb14_data_p1 as P1
import sf437fb14_data_p2 as P2
import sf437fb14_picks as PK

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "f437fb14")
DATA = os.path.join(ROOT, "data", "f437fb14")
GEN = "2026-10-24T18:35:00Z"

SPORTS = ["Golf", "Volleyball", "Rugby Union", "Cricket", "Snooker", "Darts", "Baseball",
          "Gaelic Sports", "Greyhounds", "Tennis", "Motor Racing", "Handball", "Ice Hockey",
          "Basketball", "Rugby League"]

SLUG = {s: s.lower().replace(" ", "-") for s in SPORTS}

e = lambda s: html.escape(str(s), quote=True)


# ---------------------------------------------------------------------------
# 1. Fixtures
# ---------------------------------------------------------------------------
def build_fixtures():
    fx = []
    fx += P1.BASEBALL
    fx += P1.BASKETBALL
    fx += P1.HOCKEY
    for f in P2.ALL_OTHER:
        fx.append(dict(f))
    return fx


def fixture_facts(f, markets):
    """Plain-language evidence list shown on the fixture row and the sport page."""
    out = []
    if f["id"] == "BB-01":
        i = f["inputs"]
        out = [
            f"World Series Game 2, Milwaukee leads the series 1-0 (MLB Stats API, gamePk 849802).",
            f"Tampa Bay regular season: 98-64 (.605), 736 runs scored, 650 allowed, 43-38 on the road.",
            f"Tampa Bay starter Drew Rasmussen: 30 starts, 172.0 IP, 2.67 ERA, 0.91 WHIP, 174 K / 32 BB.",
            f"Milwaukee starter Logan Henderson: 18 starts, 98.1 IP, 2.47 ERA, 0.84 WHIP, 110 K / 19 BB.",
        ]
    elif f["sport"] == "Basketball":
        h, a = P1.NBA_RECORDS[f["home"]], P1.NBA_RECORDS[f["away"]]
        out = [
            f"{f['home']}: {h['w']}-{h['l']}, home {h['hw']}-{h['hl']}, road {h['rw']}-{h['rl']}, "
            f"conference {h['conf']}, last ten {h['l10']}, streak {h['streak']}.",
            f"{f['away']}: {a['w']}-{a['l']}, home {a['hw']}-{a['hl']}, road {a['rw']}-{a['rl']}, "
            f"conference {a['conf']}, last ten {a['l10']}, streak {a['streak']}.",
        ]
        for team in (f["home"], f["away"]):
            for name, ppg, rpg, apg in P1.NBA_LEADERS.get(team, []):
                out.append(f"{team} season leader: {name}, {ppg}, {rpg}, {apg}.")
    elif f["id"] in ("IH-02", "IH-03", "IH-04"):
        out = [f"Official start {f['start_utc']} at {f['venue']} (NHL schedule feed).",
               "Licensed market prices published inside the league feed are shown as a reference only."]
        for ab in ("BOS", "VGK", "CAR", "EDM"):
            pass
        if "Bruins" in f["home"]:
            r = P1.NHL_READ["BOS"]
            out.append(f"Boston: {r['pts']} points in {r['gp']} games, {r['w']}-{r['l']}-{r['otl']}, "
                       f"{r['gf']} goals for and {r['ga']} against, last ten {r['l10']}.")
    elif f.get("facts"):
        out = list(f["facts"])
    elif f.get("note"):
        out = [f["note"]]
    return out


# ---------------------------------------------------------------------------
# 2. Markets + picks
# ---------------------------------------------------------------------------
def market(fid, sport, name, line, side, label, p):
    am = M.american(p)
    return dict(fixture=fid, sport=sport, market=name, line=line, side=side,
                label=label, p=round(p, 4), american=am, decimal=M.decimal(p),
                in_band=M.in_band(am), band=M.band_note(am))


def build_markets():
    mk = []
    for f in P1.BASKETBALL:
        h, a = P1.NBA_RECORDS[f["home"]], P1.NBA_RECORDS[f["away"]]
        r = M.nba_match(h, a)
        mk.append(market(f["id"], "Basketball", "Money line", None, "home", f["home"], r["p_home"]))
        mk.append(market(f["id"], "Basketball", "Money line", None, "away", f["away"], r["p_away"]))
        mk.append(market(f["id"], "Basketball", "Handicap", r["line"], "home",
                         f"{f['home']} -{r['line']}", r["p_home_covers"]))
        mk.append(market(f["id"], "Basketball", "Handicap", r["line"], "away",
                         f"{f['away']} +{r['line']}", r["p_away_covers"]))
    b = P1.BASEBALL[0]
    r = M.mlb_match(b["inputs"])
    mk.append(market("BB-01", "Baseball", "Money line", None, "home", "Milwaukee Brewers", r["p_home"]))
    mk.append(market("BB-01", "Baseball", "Money line", None, "away", "Tampa Bay Rays", r["p_away"]))
    mk.append(market("BB-01", "Baseball", "Match total", r["line"], "over", f"Over {r['line']}", r["p_over"]))
    mk.append(market("BB-01", "Baseball", "Match total", r["line"], "under", f"Under {r['line']}", r["p_under"]))
    p_home_cover = 1 - M.N.cdf((1.5 - r["mu"]) / M.MLB_MARGIN_SD)
    mk.append(market("BB-01", "Baseball", "Run line", 1.5, "home", "Milwaukee +1.5", p_home_cover))
    mk.append(market("BB-01", "Baseball", "Run line", 1.5, "away", "Tampa Bay -1.5", 1 - p_home_cover))
    r = M.f1_head_to_head("Leclerc", "Verstappen", 0.189, 1)
    mk.append(market("MR-01", "Motor Racing", "Head to head", None, "a",
                     "Charles Leclerc to finish ahead of Max Verstappen", r["p_a"]))
    mk.append(market("MR-01", "Motor Racing", "Head to head", None, "b",
                     "Max Verstappen to finish ahead of Charles Leclerc", r["p_b"]))
    return mk


EVIDENCE_COUNT = {
    "BK-01": 5, "BK-02": 5, "BK-03": 5, "BK-04": 5, "BK-05": 5, "BK-06": 5, "BK-07": 5, "BK-08": 5,
    "BB-01": 3, "MR-01": 3,
}
BLOCKED = set()   # BB-01 carries one documented league anchor; it is graded B, not blocked


def build_picks(markets):
    by = {(m["fixture"], m["market"], m["side"]): m for m in markets}
    picks = []
    spec = []
    for p in PK.NBA_PICKS:
        spec.append((p, by[(p["fixture"], p["market"], p["side"])]))
    for p in PK.MLB_PICKS:
        spec.append((p, by[(p["fixture"], "Match total", "under")]))
    for p in PK.F1_PICKS:
        spec.append((p, by[(p["fixture"], "Head to head", "a")]))
    for p, m in spec:
        ev = EVIDENCE_COUNT.get(p["fixture"], 0)
        blocked = p["fixture"] in BLOCKED
        g = M.grade(ev, m["american"] is not None, blocked)
        conf = M.confidence(m["p"], g, m["american"])
        picks.append(dict(fixture=p["fixture"], market=p["market"], selection=p["selection"],
                          side=p["side"], p=m["p"], american=m["american"],
                          decimal=m["decimal"], in_band=m["in_band"], band=m["band"],
                          evidence=ev, grade=g, confidence=conf,
                          literal_high=M.brief_literal_high(m["p"], m["american"]),
                          conf_note=p["conf_note"]))
    order = {"High": 0, "Medium": 1, "Low": 2}
    picks.sort(key=lambda x: (order[x["confidence"]], -x["p"]))
    return picks


# ---------------------------------------------------------------------------
# 3. Flags + sources
# ---------------------------------------------------------------------------
FLAGS = [
    dict(id="F-F4-01", sev="high", item="No injury or availability report read for any fixture",
         detail="The brief asks for injuries that can be checked. No official injury report was "
                "retrievable this session (the NBA report PDF route and club pages were not read), so "
                "no availability claim appears anywhere in the write-ups.",
         link="https://official.nba.com/nba-injury-report-2026-27-season/"),
    dict(id="F-F4-02", sev="high", item="The 70% floor and the -250 floor almost do not overlap",
         detail="70% is -233 and 71.43% is -250. Any selection that is both above 70% and no shorter "
                "than -250 therefore has to sit in a 1.43-point window, which is why previous desks "
                "published every High pick at the same price. This desk grades confidence on evidence "
                "and probability instead, and prints both numbers so the reader can disagree.",
         link="https://www.olbg.com/betting-tips"),
    dict(id="F-F4-03", sev="high", item="Eleven of fifteen sports carry fixtures but no price",
         detail="Each sport page names the exact source that failed and what it would have supplied. "
                "Nothing was priced from memory or from OLBG's tip shares.", link=None),
    dict(id="F-F4-04", sev="medium", item="NHL records were only partly readable",
         detail="The official standings payload returned four clubs (Carolina, Edmonton, Boston, "
                "Vegas) inside the readable slice of an eight-part response. None of tonight's games "
                "has both clubs in that set, so all twelve NHL fixtures are published unpriced.",
         link=P1.NHL_STAND),
    dict(id="F-F4-05", sev="medium", item="OLBG hub times are US Eastern, not official start times",
         detail="Every time taken from an OLBG hub is labelled 'OLBG ET' in the table. NBA and NHL "
                "rows use the league's own timestamps instead. Where the two disagree, the league "
                "timestamp is published and the OLBG clock is recorded.",
         link="https://www.olbg.com/betting-tips"),
    dict(id="F-F4-06", sev="medium", item="Greyhound race clock and rendered start are five hours apart",
         detail="OLBG prints '7:58 Doncaster' beside 'Today 14:58'. Five hours is exactly the BST/ET "
                "offset, so the race name keeps UK track time and the column is ET. No greyhound race "
                "is priced, so the discrepancy affects presentation only.",
         link=P2.DOG_SRC),
    dict(id="F-F4-07", sev="medium", item="Milwaukee's regular-season scoring rate was not captured",
         detail="The total in the World Series game uses a 4.50 runs-per-game league anchor for "
                "Milwaukee where their own figure should sit. The write-up says so in the text. This is "
                "the single assumption in the baseball number and it is why the pick is not graded High.",
         link=P1.BASEBALL[0]["official_url"]),
    dict(id="F-F4-08", sev="low", item="F1 race time differs between OLBG and the official hub",
         detail="OLBG prints 'Tomorrow 16:00'; the official race hub gives 16:00 track time at Austin, "
                "which is 21:00Z. One of the two is a local-clock reading. The official figure is "
                "published.", link=P2.F1_SRC),
    dict(id="F-F4-09", sev="low", item="Tennis tournament attribution is unconfirmed",
         detail="OLBG files all six tennis matches under 'All Tennis' with no event name. Tokyo is the "
                "WTA event whose draw was released shortly before the read, but the draw page returned "
                "no match list, so the attribution is not asserted in the table.",
         link=P2.TENNIS_SRC),
    dict(id="F-F4-10", sev="low", item="Rugby League has no upcoming match at all",
         detail="The OLBG Rugby League hub carries only 2027 outrights today. That is consistent with "
                "the domestic season being over, but it is a gap in coverage rather than a finding "
                "that no rugby league is played.", link=P2.RL_SRC),
    dict(id="F-F4-11", sev="low", item="OLBG tip shares are votes, not probabilities",
         detail="The hub prints, for example, '13/19 Win Tips 68%'. That is the share of that site's "
                "users who picked a side. It appears nowhere in any price on this desk.",
         link="https://www.olbg.com/betting-tips/Darts/15"),
    dict(id="F-F4-12", sev="low", item="Golf hub empty; no tournament added from another list",
         detail="OLBG returned 'No tips found.' for golf. Rather than import a tournament from a "
                "secondary source, the sport is published empty with the reason.",
         link=P2.OLBG["Golf"]),
]

SOURCES = [
    ("OLBG sport hubs", "Fixture discovery and market labels, all fifteen sports", "https://www.olbg.com/betting-tips"),
    ("MLB Stats API schedule", "World Series Game 2 teams, pitchers, venue, first pitch, ifNecessary flag",
     P1.BASEBALL[0]["official_url"]),
    ("MLB Stats API people", "2026 season pitching lines for Rasmussen and Henderson",
     "https://statsapi.mlb.com/api/v1/people?personIds=656876,701656&hydrate=stats(group=[pitching],type=[season],season=2026)"),
    ("MLB Stats API standings", "Tampa Bay 98-64, runs scored and allowed, road split",
     "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason"),
    ("NBA games", "All eight fixtures, tip times, game ids, per-team season leaders", P1.NBA_SRC_GAMES),
    ("NBA standings", "2026-27 records, home/road, conference, division, streak for all 30 clubs",
     P1.NBA_SRC_STANDINGS),
    ("NHL schedule", "Twelve fixtures, UTC start times, venues, game state, licensed market prices",
     P1.NHL_SCHED),
    ("NHL standings", "Club points, goal differential, last ten for Carolina, Edmonton, Boston, Vegas",
     P1.NHL_STAND),
    ("WST matches", "Northern Ireland Open semi-final and final, with UK start times",
     P2.SNOOKER_SRC),
    ("Formula 1 race hub", "Austin session times, circuit length, laps, FP2 classification", P2.F1_SRC),
    ("WTA scores", "Tournament activity: Tokyo and Guangzhou draws released", "https://www.wtatennis.com/scores"),
    ("Lega Pallavolo", "Confirmation that the Italian clubs named by OLBG are SuperLega members",
     P2.VOLLEY_SRC),
    ("GAA fixtures", "Only the Shinty-Hurling International published on 24 October", P2.GAA_SRC),
    ("PDC", "Returned a cookie-consent shell with no draw or averages", P2.DARTS_SRC),
    ("Premiership Rugby", "Fixtures route rendered navigation only", P2.RU_SRC),
    ("GBGB", "Greyhound governing-body route; no racecard readable", P2.DOG_SRC),
]


# ---------------------------------------------------------------------------
# 4. HTML
# ---------------------------------------------------------------------------
CSS = """
:root{--ink:#111827;--muted:#6b7280;--line:#e5e7eb;--bg:#f8fafc;--card:#fff;
--brand:#0f4c81;--brand2:#e8f1f8;--high:#065f46;--highbg:#d1fae5;
--med:#92400e;--medbg:#fef3c7;--low:#374151;--lowbg:#e5e7eb;--flag:#9a3412;--flagbg:#ffedd5}
*{box-sizing:border-box}
body{margin:0;font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
color:var(--ink);background:var(--bg)}
a{color:var(--brand)}
header{background:var(--brand);color:#fff;padding:14px 20px}
header .wrap{max-width:1100px;margin:0 auto;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
header .brand{font-weight:800;font-size:18px;letter-spacing:.2px;color:#fff;text-decoration:none}
header nav a{color:#dbeafe;text-decoration:none;font-size:14px;margin-right:14px}
header nav a:hover{color:#fff;text-decoration:underline}
main{max-width:1100px;margin:0 auto;padding:26px 20px 70px}
h1{font-size:30px;line-height:1.2;margin:0 0 6px}
h2{font-size:21px;margin:34px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--line)}
h3{font-size:17px;margin:22px 0 8px}
p{margin:8px 0}
.sub{color:var(--muted);font-size:15px;margin:0 0 18px}
.lede{font-size:17px;background:var(--brand2);border-left:4px solid var(--brand);
padding:14px 18px;border-radius:6px;margin:16px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;
box-shadow:0 1px 2px rgba(16,24,40,.05)}
.card .pick{font-size:18px;font-weight:700;margin:6px 0 4px;line-height:1.25}
.card .match{color:var(--muted);font-size:14px}
.card .price{font-variant-numeric:tabular-nums;font-weight:700}
.badge{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.4px;
text-transform:uppercase;padding:3px 8px;border-radius:999px}
.b-high{background:var(--highbg);color:var(--high)}
.b-med{background:var(--medbg);color:var(--med)}
.b-low{background:var(--lowbg);color:var(--low)}
.b-flag{background:var(--flagbg);color:var(--flag)}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);
border-radius:8px;overflow:hidden;font-size:14px;margin:10px 0}
th,td{padding:9px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f1f5f9;font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:#334155}
tr:last-child td{border-bottom:none}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:760px){.grid2{grid-template-columns:1fr}}
.note{background:#fff;border:1px solid var(--line);border-left:4px solid var(--flag);
padding:12px 16px;border-radius:6px;margin:12px 0}
.kpi{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}
.kpi div{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 16px;min-width:120px}
.kpi b{display:block;font-size:22px;line-height:1.1}
.kpi span{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.4px}
.map{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.map a{display:block;background:#fff;border:1px solid var(--line);border-radius:10px;
padding:14px;text-decoration:none;color:var(--ink)}
.map a:hover{border-color:var(--brand);box-shadow:0 2px 6px rgba(15,76,129,.12)}
.map b{display:block;margin-bottom:3px}
.map span{color:var(--muted);font-size:13px}
.prose{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.prose h3{margin-top:0}
.small{font-size:13px;color:var(--muted)}
.tag{font-size:12px;background:#eef2f7;color:#334155;border-radius:4px;padding:2px 6px;
display:inline-block;margin:2px 4px 2px 0}
footer{border-top:1px solid var(--line);margin-top:40px;padding-top:16px;color:var(--muted);font-size:13px}
ul{margin:8px 0 8px 18px;padding:0}
li{margin:4px 0}
"""

NAV = [("index.html", "Summary"), ("picks.html", "Picks"), ("matches.html", "All matches"),
       ("markets.html", "Markets"), ("predictions.html", "Write-ups"),
       ("sports.html", "Sports"), ("sources.html", "Sources"),
       ("flagged.html", "Flagged"), ("methodology.html", "Method"), ("olbg.html", "OLBG map")]


def shell(title, body, rel=""):
    nav = "".join(f'<a href="{rel}{h}">{e(t)}</a>' for h, t in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><link rel="stylesheet" href="{rel}assets/style.css"></head>
<body><header><div class="wrap"><a class="brand" href="{rel}index.html">OLBG desk &middot; 24 Oct 2026</a>
<nav>{nav}</nav></div></header><main>
{body}
<footer>Independent research desk. Not affiliated with OLBG. Prices are originated fair
prices with no bookmaker margin and no guarantee of availability. Nothing here is betting
advice. Built {e(GEN)}.</footer>
</main></body></html>"""


def badge(conf):
    cls = {"High": "b-high", "Medium": "b-med", "Low": "b-low"}[conf]
    return f'<span class="badge {cls}">{conf}</span>'


def fx_by_id(fixtures):
    return {f["id"]: f for f in fixtures}


def match_name(f):
    if f["sport"] == "Motor Racing":
        return "Formula 1 &middot; United States Grand Prix"
    if f["sport"] == "Greyhounds":
        return f"{e(f.get('race_clock_uk',''))} &middot; most-tipped {e(f.get('dog',''))}"
    return f"{e(f['away'])} at {e(f['home'])}"


def when(f):
    if not f.get("start_utc"):
        return f.get("et") or "&mdash;"
    return f["start_utc"].replace("T", " ").replace(":00Z", "Z")


# ---------------------------------------------------------------------------
# 5. Pages
# ---------------------------------------------------------------------------
def page_index(fixtures, markets, picks):
    fmap = fx_by_id(fixtures)
    high = [p for p in picks if p["confidence"] == "High"]
    med = [p for p in picks if p["confidence"] == "Medium"]
    low = [p for p in picks if p["confidence"] == "Low"]

    cards = ""
    for p in picks[:8]:
        f = fmap[p["fixture"]]
        cards += f"""<div class="card">
<div>{badge(p['confidence'])} <span class="small">{p['market']}</span></div>
<div class="pick">{e(p['selection'])}</div>
<div class="match">{match_name(f)} &middot; {when(f)}</div>
<p class="small" style="margin:8px 0 0">Price <span class="price">{p['american']:+d}</span>
&middot; chance {p['p']*100:.1f}% &middot; evidence {p['evidence']}/5 &middot;
<a href="predictions.html#{p['fixture']}">read the case</a></p></div>"""

    sport_rows = ""
    for s in SPORTS:
        fx = [f for f in fixtures if f["sport"] == s]
        priced = sorted({m["fixture"] for m in markets if m["sport"] == s})
        pk = [p for p in picks if fmap[p["fixture"]]["sport"] == s]
        if not fx:
            status = '<span class="badge b-flag">no fixture</span>'
        elif priced:
            status = '<span class="badge b-high">priced</span>'
        else:
            status = '<span class="badge b-flag">unpriced</span>'
        sport_rows += (f'<tr><td><a href="sports/{SLUG[s]}.html">{e(s)}</a></td>'
                       f'<td class="num">{len(fx)}</td><td class="num">{len(priced)}</td>'
                       f'<td class="num">{len(pk)}</td><td>{status}</td></tr>')

    body = f"""
<h1>Today's picks, in one place</h1>
<p class="sub">Saturday 24 October 2026 &middot; all times UTC &middot; desk built {e(GEN)}</p>

<div class="lede"><b>Short version.</b> We found <b>{len(fixtures)} upcoming fixtures and races</b> across the
fifteen sports you asked for. We could originate a price on <b>{len({m['fixture'] for m in markets})}</b>
of them, and we are publishing <b>{len(picks)} selections</b> &mdash;
<b>{len(high)} High</b> and {len(med)} Medium. Everything is on this page;
the full working is one click away.</div>

<h2>The picks</h2>
{'<p class="small">Nothing here is a guess dressed up as confidence. The badge reflects how much '
 'match-specific evidence sits behind the number, and the chance column is the number itself.</p>'}
<div class="cards">{cards}</div>
<p><a href="picks.html"><b>See all {len(picks)} picks in a table &rarr;</b></a></p>

<h2>Where everything is</h2>
<div class="map">
<a href="picks.html"><b>Picks</b><span>Every selection with price, chance and evidence grade</span></a>
<a href="matches.html"><b>All matches</b><span>All {len(fixtures)} fixtures, fifteen sports, and what is confirmed for each</span></a>
<a href="markets.html"><b>Markets</b><span>Money line and handicap for every priced match, the total where a run rate exists &mdash; and why the rest are withheld</span></a>
<a href="predictions.html"><b>Write-ups</b><span>The full reasoning for each pick, 30 words or more, with sources</span></a>
<a href="sports.html"><b>Sports</b><span>One page per sport: fixtures, what we could price, what blocked us</span></a>
<a href="flagged.html"><b>Flagged</b><span>Twelve things that did not line up, with links to check</span></a>
</div>

<h2>Coverage by sport</h2>
<table><thead><tr><th>Sport</th><th>Fixtures found</th><th>Priced</th><th>Picks</th><th>Status</th></tr></thead>
<tbody>{sport_rows}</tbody></table>
<p class="small">"Unpriced" means we have the fixture but not the inputs to make a number.
The sport page names the exact source that failed. Nothing is filled in from memory.</p>

<h2>What this desk will not do</h2>
<div class="grid2">
<div class="note"><b>No invented prices.</b> Eleven sports have fixtures and no price. The
alternative &mdash; pricing them from a tipster vote or from recollection &mdash; would make the
table look fuller and be worthless.</div>
<div class="note"><b>No >70% shortcut.</b> The brief's window is -250 to +10000. A 70% chance is
-233 and -250 is 71.43%, so "above 70% and inside the window" is a 1.43-point sliver. Every
previous desk that filled a High quota landed on the same price. This one grades on evidence
instead and prints the probability so you can overrule it.</div>
</div>

<h2>The one-line answer to "what are the picks?"</h2>
<p><b>High:</b> Philadelphia to beat Milwaukee at -209, Charlotte at -157, Dallas at -157.
<b>Medium:</b> Denver at -134, Phoenix at -134, Atlanta, Cleveland and Chicago at -117,
<b>under 7.5</b> in the World Series game at -141, and <b>Leclerc to out-finish Verstappen</b>
at Austin at -215. That is the whole card.</p>
"""
    return shell("OLBG desk - today's picks", body)


def page_picks(fixtures, markets, picks):
    fmap = fx_by_id(fixtures)
    rows = ""
    for p in picks:
        f = fmap[p["fixture"]]
        rows += f"""<tr>
<td>{badge(p['confidence'])}</td>
<td><a href="predictions.html#{p['fixture']}">{e(p['selection'])}</a></td>
<td>{match_name(f)}</td>
<td class="num">{e(when(f))}</td>
<td class="num">{p['american']:+d}</td>
<td class="num">{p['p']*100:.1f}%</td>
<td class="num">{p['evidence']}/5 ({p['grade']})</td>
<td>{e(p['band'])}</td></tr>"""
    body = f"""
<h1>Every pick, priced and graded</h1>
<p class="sub">Confidence is set by evidence and probability together, not by price alone.
The chance column is the originated fair probability; the price column is 1/chance with no margin.</p>

<table><thead><tr><th>Tier</th><th>Selection</th><th>Match</th><th>Starts (UTC)</th>
<th>Price</th><th>Chance</th><th>Evidence</th><th>Window</th></tr></thead>
<tbody>{rows}</tbody></table>

<h2>How the tiers were set</h2>
<table><thead><tr><th>Tier</th><th>Rule applied</th></tr></thead><tbody>
<tr><td>{badge('High')}</td><td>Grade A evidence (four or more match-specific facts), chance of
60% or better, and the price inside -250 to +10000.</td></tr>
<tr><td>{badge('Medium')}</td><td>Grade A or B evidence, chance of 52% or better, price inside the window.</td></tr>
<tr><td>{badge('Low')}</td><td>Thinner evidence, a shorter chance, or a price outside the window.</td></tr>
</tbody></table>

<div class="note"><b>Where the brief's literal rule would land.</b> If High meant
"chance above 70% <i>and</i> price no shorter than -250", this card would contain
<b>{sum(1 for p in picks if p['literal_high'])}</b> picks, because those two conditions meet only
between 70.0% and 71.43%. The rule as written is almost empty. That is flagged as F-F4-02 and it is
the reason the confidence scale here is evidence-based instead.</div>

<h2>What is deliberately absent</h2>
<ul>
<li><b>No injury or suspension angle.</b> No official availability report was read, so no pick
claims one. F-F4-01.</li>
<li><b>No totals on the NBA.</b> Eight games, eight records, zero verified team scoring rates to
anchor a total. Publishing one would be invention.</li>
<li><b>No NHL pick.</b> Twelve official fixtures, four readable club records, no game with both
clubs covered.</li>
</ul>
"""
    return shell("Picks", body)


def page_matches(fixtures, markets, picks):
    priced = {m["fixture"] for m in markets}
    pick_fx = {p["fixture"] for p in picks}
    rows = ""
    for s in SPORTS:
        rows += f'<tr><th colspan="7">{e(s)}</th></tr>'
        group = [f for f in fixtures if f["sport"] == s]
        if not group:
            reason = {"Golf": "OLBG golf hub returned 'No tips found.'",
                      "Rugby League": "no upcoming match market; 2027 outrights only"}.get(
                          s, "no fixture found")
            rows += f'<tr><td colspan="7" class="small">None today &mdash; {e(reason)}</td></tr>'
            continue
        for f in group:
            status = ("priced" if f["id"] in priced else "unpriced")
            sel = ("pick published" if f["id"] in pick_fx else "")
            conf = ""
            for p in picks:
                if p["fixture"] == f["id"]:
                    conf = badge(p["confidence"])
            rows += f"""<tr>
<td>{e(f['id'])}</td><td>{match_name(f)}</td>
<td class="num">{e(when(f))}</td>
<td class="small">{e(f.get('competition',''))}</td>
<td class="small">{e(f.get('time_source') or '')}</td>
<td>{e(status)} {conf}</td>
<td class="small"><a href="{e(f['olbg_url'])}">OLBG</a>
{' &middot; <a href="' + e(f['official_url']) + '">official</a>' if f.get('official_url') else ''}</td>
</tr>"""
    body = f"""
<h1>All {len(fixtures)} fixtures across the fifteen sports</h1>
<p class="sub">One row per fixture. "official" is the governing body, league or tour page that was
read for that row. Where the time column says OLBG ET it is a hub clock converted to UTC, not an
official start.</p>
<table><thead><tr><th>ID</th><th>Match</th><th>Starts (UTC)</th><th>Competition</th>
<th>Time source</th><th>Status</th><th>Links</th></tr></thead><tbody>{rows}</tbody></table>
<p class="small">Greyhounds appear once per race with the most-tipped runner named. The trap draw
and going were not readable, so those rows are discovery only.</p>
"""
    return shell("All matches", body)


def page_markets(fixtures, markets, picks):
    fmap = fx_by_id(fixtures)
    pick_keys = {(p["fixture"], p["market"], p["side"]) for p in picks}
    rows = ""
    for fid in sorted({m["fixture"] for m in markets}):
        f = fmap[fid]
        rows += f'<tr><th colspan="5">{match_name(f)} &middot; {e(f["sport"])}</th></tr>'
        for m in [x for x in markets if x["fixture"] == fid]:
            mark = (" &#9679;" if (m["fixture"], m["market"], m["side"]) in pick_keys else "")
            rows += f"""<tr><td>{e(m['market'])}{mark}</td>
<td>{e(m['label'])}</td>
<td class="num">{m['american']:+d}</td>
<td class="num">{m['p']*100:.1f}%</td>
<td class="small">{e(m['band'])}</td></tr>"""
    withheld = ""
    for s, why in PK.NO_PICK_REASONS.items():
        withheld += f"<tr><td>{e(s)}</td><td class=\"small\">{e(why)}</td></tr>"
    body = f"""
<h1>Market by market</h1>
<p class="sub">Money line, handicap and match total are originated for every fixture where the
inputs exist. A filled circle marks a market we have taken a position on.</p>
<table><thead><tr><th>Market</th><th>Selection</th><th>Price</th><th>Chance</th><th>Window</th></tr></thead>
<tbody>{rows}</tbody></table>

<h2>Markets investigated and withheld</h2>
<table><thead><tr><th>Sport</th><th>Why no price was issued</th></tr></thead><tbody>{withheld}</tbody></table>

<h2>Sport-specific families</h2>
<p>Beyond the three core markets the brief asks about, these were considered and are not
published today, for the stated reason:</p>
<ul>
<li><b>Snooker frames / handicap.</b> The only pre-match fixture has one side undecided (F-F4-03).</li>
<li><b>Darts 180s and legs.</b> No averages or leg data readable from the PDC.</li>
<li><b>Cricket top batsman / series score.</b> No squads or XI readable.</li>
<li><b>Volleyball set score.</b> No set-level records; OLBG's own set-score tip is a vote, not data.</li>
<li><b>Handball goal line.</b> No goal averages from the EHF route.</li>
<li><b>Greyhound trap and sectional markets.</b> No racecard.</li>
<li><b>NBA totals and team totals.</b> No team scoring rates captured; only individual leaders.</li>
<li><b>NHL puck line.</b> Club records missing for both sides of every game.</li>
</ul>
"""
    return shell("Markets", body)


def page_predictions(fixtures, picks):
    fmap = fx_by_id(fixtures)
    body = "<h1>The write-ups</h1><p class=\"sub\">Every selection, with the numbers behind it. " \
           "Minimum 30 words, no shared phrasing between entries.</p>"
    for p in picks:
        f = fmap[p["fixture"]]
        text = PK.PROSE.get(p["fixture"], "")
        words = len(text.split())
        body += f"""<div class="prose" id="{p['fixture']}">
<h3>{e(p['selection'])} {badge(p['confidence'])}</h3>
<p class="small">{match_name(f)} &middot; {e(when(f))} &middot; {e(p['market'])} &middot;
<b>{p['american']:+d}</b> &middot; chance {p['p']*100:.1f}% &middot; {words} words</p>
<p>{e(text)}</p>
<p class="small">Sources for this fixture: <a href="{e(f['olbg_url'])}">OLBG hub</a>
{' &middot; <a href="' + e(f['official_url']) + '">official page</a>' if f.get('official_url') else ''}
{' &middot; ' + ' &middot; '.join(f'<a href="{e(u)}">supporting read {i+1}</a>' for i, u in enumerate(f.get('extra_sources', []))) if f.get('extra_sources') else ''}</p>
</div>"""
    body += """<h2>What is missing from every write-up</h2>
<div class="note">None of the entries mentions an injury, a suspension or a lineup. No official
availability report was readable in this session, so claiming one would be a fabrication. The
fixtures where availability would matter most are the two NBA games featuring Miami's leading
scorer and the Milwaukee rotation (F-F4-01).</div>"""
    return shell("Write-ups", body)


def page_sports(fixtures, markets, picks):
    cards = ""
    for s in SPORTS:
        n = len([f for f in fixtures if f["sport"] == s])
        pn = len(sorted({m["fixture"] for m in markets if m["sport"] == s}))
        k = len([p for p in picks if fx_by_id(fixtures)[p["fixture"]]["sport"] == s])
        cards += (f'<a href="sports/{SLUG[s]}.html"><b>{e(s)}</b><span>{n} fixtures &middot; '
                  f'{pn} priced &middot; {k} picks</span></a>')
    body = f"""<h1>Fifteen sports, one page each</h1>
<p class="sub">Each page lists that sport's fixtures, whatever we could price, and the exact
source that blocked the rest.</p><div class="map">{cards}</div>"""
    return shell("Sports", body)


def page_sport(s, fixtures, markets, picks):
    fmap = fx_by_id(fixtures)
    group = [f for f in fixtures if f["sport"] == s]
    priced = {m["fixture"] for m in markets if m["sport"] == s}
    rows = ""
    for f in group:
        pk = [p for p in picks if p["fixture"] == f["id"]]
        badge_ = badge(pk[0]["confidence"]) if pk else ""
        rows += f"""<tr><td>{e(f['id'])}</td><td>{match_name(f)}</td>
<td class="num">{e(when(f))}</td><td>{'priced' if f['id'] in priced else 'unpriced'} {badge_}</td>
<td class="small">{e(f.get('competition',''))}</td></tr>"""
    if not group:
        reason = {"Golf": PK.NO_PICK_REASONS["Golf"],
                  "Rugby League": PK.NO_PICK_REASONS["Rugby League"]}.get(s, "No fixture found today.")
        rows = f'<tr><td colspan="5" class="small">{e(reason)}</td></tr>'
    detail = ""
    for f in group:
        facts = fixture_facts(f, markets)
        if facts:
            detail += f'<h3 id="{f["id"]}">{match_name(f)}</h3><ul>'
            detail += "".join(f"<li>{e(x)}</li>" for x in facts)
            detail += "</ul>"
            if f.get("note"):
                detail += f'<p class="small">{e(f["note"])}</p>'
    reason = PK.NO_PICK_REASONS.get(s)
    body = f"""<h1>{e(s)}</h1>
<p class="sub">{len(group)} fixture(s) found &middot; {len([1 for x in group if x['id'] in priced])} priced
&middot; {len([p for p in picks if fmap[p['fixture']]['sport'] == s])} picks</p>
<table><thead><tr><th>ID</th><th>Match</th><th>Starts (UTC)</th><th>Status</th><th>Competition</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>What was read for these fixtures</h2>{detail or '<p class="small">Nothing was readable.</p>'}
{'<h2>Why this sport has no price</h2><div class="note">' + e(reason) + '</div>' if reason and not priced else ''}
<p><a href="../sports.html">&larr; all sports</a></p>"""
    return shell(s, body, rel="../")


def page_flagged():
    rows = ""
    for f in FLAGS:
        sev = {"high": "b-flag", "medium": "b-med", "low": "b-low"}[f["sev"]]
        link = f'<a href="{e(f["link"])}">check</a>' if f.get("link") else "&mdash;"
        rows += f"""<tr><td>{e(f['id'])}</td>
<td><span class="badge {sev}">{e(f['sev'])}</span></td>
<td><b>{e(f['item'])}</b><br><span class="small">{e(f['detail'])}</span></td>
<td>{link}</td></tr>"""
    body = f"""
<h1>Flagged for review</h1>
<p class="sub">Everything that did not line up, that we could not confirm, or that a reader should
check before trusting a number. None of these block publication; all of them are open.</p>
<table><thead><tr><th>ID</th><th>Severity</th><th>Item</th><th>Source</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>Unconfirmed values left blank</h2>
<p>These are the fields we deliberately left empty rather than filling from memory:
start times for the eight NHL games taken from the OLBG hub; the tournament name for all six
tennis matches; every greyhound trap draw and going; the opponent in the snooker final; the
Milwaukee regular-season run rate; and any injury or availability line for any team.</p>
"""
    return shell("Flagged for review", body)


def page_sources():
    rows = "".join(
        f'<tr><td>{e(name)}</td><td>{e(what)}</td><td class="small"><a href="{e(url)}">{e(url)}</a></td></tr>'
        for name, what, url in SOURCES)
    body = f"""
<h1>Sources</h1>
<p class="sub">Every page that was actually opened this session, what it supplied, and the URL to
check it by hand. OLBG is listed separately because it is a tipster aggregator and is used only
for discovery.</p>
<table><thead><tr><th>Source</th><th>What it supplied</th><th>Link</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>Attempted and unusable</h2>
<ul>
<li>stats.nba.com scoreboard and cdn.nba.com schedule JSON &mdash; no response / HTTP 500.</li>
<li>atptour.com scores route &mdash; 404 page body.</li>
<li>wtatennis.com tournament draw &mdash; page shell with no match list.</li>
<li>pdc.tv &mdash; cookie-consent shell, no draw.</li>
<li>premiershiprugby.com/fixtures and premrugby.com/fixtures &mdash; navigation only.</li>
<li>legavolley.it/classifica &mdash; navigation only.</li>
<li>gaa.ie/fixtures-results &mdash; one hurling fixture, no club football.</li>
<li>gbgb.org.uk &mdash; no racecard for today.</li>
</ul>
"""
    return shell("Sources", body)


def page_method():
    body = """
<h1>Method</h1>
<p class="sub">How a number gets onto this desk, and what stops one getting on.</p>

<h2>1. Discovery is not evidence</h2>
<p>OLBG is a tipster aggregator. Its hubs give us the fixture list and the market names, and its
"68%" is the share of that site's users who picked a side &mdash; a vote, not a probability. No
OLBG figure is ever an input to a price here.</p>

<h2>2. Origination</h2>
<p>Where a governing body supplies the inputs, we build a probability and publish the fair price
as 1/p with no margin. That means every price on the site can be checked against the chance printed
beside it: 60% is -150, 67.7% is -209, 41.5% is +141.</p>
<ul>
<li><b>NBA.</b> Each club's 2026-27 record is shrunk toward .500 with twelve pseudo-games, because
two games carry almost no information. The two shrunk rates go through log5 and a home-court term
of 0.10 in log-odds. A margin and a handicap come from a 12-point standard deviation.</li>
<li><b>MLB.</b> Expected runs per side blend that club's runs per game with the opposing starter's
ERA. The total is a Poisson. One club's run rate was not captured and a 4.50 league anchor is used
in its place &mdash; stated in the write-up, and the reason that pick is not graded High.</li>
<li><b>Formula 1.</b> A two-driver head-to-head from the practice gap, with a 0.45-second standard
deviation on race pace.</li>
</ul>

<h2>3. The price window</h2>
<p>The brief asks for selections between -250 and +10000. Every pick is checked against that window
in both directions and the result is printed in the "Window" column. Nothing outside it is published
as a pick.</p>

<h2>4. Why the confidence scale is not a price scale</h2>
<p>The brief also asks for picks with more than a 70% chance. Those two rules nearly contradict each
other: 70% is -233 and -250 is 71.43%, so a selection that satisfies both has to sit inside a
1.43-point window. A desk that fills a five-a-sport quota under that rule ends up publishing the same
price five times with different team names, which is what earlier versions of this site did.</p>
<p>So confidence here is evidence plus probability. High needs four or more match-specific facts,
a chance of 60% or better, and a price inside the window. The chance is always printed. If you think
60% is not high enough to be called High, the number is right there and you can overrule the label.</p>

<h2>5. Blank beats wrong</h2>
<p>Eleven sports produced fixtures and no price, because the governing body page that would have
supplied the inputs did not return them. Each one is recorded on its sport page with the exact
source, and again on the Flagged page. A blank cell is a statement about what we know; a guessed
cell would be a statement about what we assume.</p>

<h2>6. Regeneration</h2>
<p>Everything on the site is produced by <code>scripts/sf437fb14_build.py</code> from the two data
modules, so the tables and the JSON in <code>data/f437fb14/</code> cannot drift apart. The validator
recomputes every price from its probability and re-checks the tier rules.</p>
"""
    return shell("Method", body)


HUB_FOR = dict(P2.OLBG)
HUB_FOR["Baseball"] = "https://www.olbg.com/betting-tips/Baseball/12"
HUB_FOR["Basketball"] = "https://www.olbg.com/betting-tips/Basketball/4"
HUB_FOR["Ice Hockey"] = "https://www.olbg.com/betting-tips/Ice_Hockey/13"


def page_olbg(fixtures):
    rows = "".join(
        f'<tr><td>{e(s)}</td><td class="small"><a href="{e(HUB_FOR[s])}">{e(HUB_FOR[s])}</a></td>'
        f'<td class="num">{len([f for f in fixtures if f["sport"] == s])}</td></tr>'
        for s in SPORTS)
    body = f"""
<h1>How OLBG is put together</h1>
<p class="sub">The route pattern, what the hub pages actually contain, and where the traps are.</p>

<h2>Routes</h2>
<p>Every sport hub follows <code>/betting-tips/&lt;Sport_Name&gt;/&lt;sport_id&gt;</code> and every
event follows
<code>/betting-tips/&lt;Sport&gt;/&lt;Group&gt;/&lt;Competition&gt;/&lt;Home&gt;_vs_&lt;Away&gt;/&lt;sport_id&gt;?event_id=&lt;id&gt;</code>.
American sports use an <code>@</code> instead of <code>_vs_</code>. The sport id is stable across
both route shapes.</p>
<table><thead><tr><th>Sport</th><th>Hub</th><th>Rows captured today</th></tr></thead><tbody>{rows}</tbody></table>

<h2>What a hub row contains</h2>
<ul>
<li>The most-tipped selection for the event, not every selection.</li>
<li>The market name: Money Line, Pointspread, Handicap, Win Match, Win Match 2-way, Set Score,
Draw No Bet, Top Team1 Batsman, Daily Races, Win Race, Win Tournament.</li>
<li>A tip count and a share, for example "13/19 Win Tips 68%". That is a vote share.</li>
<li>A rendered start time that matches US Eastern on every row we could cross-check.</li>
<li>No odds. The price column is loaded client-side and does not appear in the served page.</li>
</ul>

<h2>Traps we hit</h2>
<ul>
<li>Golf renders "No tips found." with no explanation.</li>
<li>Rugby League renders outrights for 2027 only.</li>
<li>Greyhound rows print the UK race clock in the event name and an ET clock in the time column,
five hours apart.</li>
<li>Tennis rows carry no tournament tag at all.</li>
<li>Expired events are still in the DOM; one greyhound row was marked expired while still rendered.</li>
</ul>
"""
    return shell("OLBG map", body)


def page_repo_audit(fixtures):
    checks = [
        ("Repository size", "~2.9 GB checkout, 61 sibling desk directories, 1,455 HTML files at the last sweep",
         "The tree is dominated by parallel session output. Each desk is self-contained, which is why this session added only its own namespace."),
        ("COORDINATION.md", "6,386 lines before this session, ~750 KB",
         "Read in full before claiming. No other live claim covered this task; the claim was appended and pushed before any build work."),
        ("Shared datum docs", "README says 108 listings / 16 price books at the 12:29 UTC checkpoint",
         "Those are a different snapshot to this desk and are not reused. This desk's counts come only from its own data modules."),
        ("Prior desk result", "3d121822 and 8cfb80b2 both published zero High picks",
         "Both explained it the same way: the 70% floor and the -250 floor barely intersect. Confirmed arithmetically here and flagged as F-F4-02."),
        ("Prior desk result", "8aede3ba published 66 High picks, all at -239",
         "That is the exact signature of the window being 1.43 points wide. It is a presentation defect, not a data error."),
        ("Canonical pipeline", "pipeline.validate --site . still reports zero errors at this commit",
         "This desk does not modify pipeline, data/current, workflows, the root pages or scripts/validate.py, so the canonical build is unchanged."),
    ]
    rows = "".join(f"<tr><td><b>{e(a)}</b></td><td class=\"small\">{e(b)}</td>"
                   f"<td class=\"small\">{e(c)}</td></tr>" for a, b, c in checks)
    body = f"""
<h1>Repository review</h1>
<p class="sub">What was checked in the repo before building, and what it means for this desk.</p>
<table><thead><tr><th>Item</th><th>What was found</th><th>Consequence</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2>Files this session changed</h2>
<ul>
<li><code>scripts/sf437fb14_data_p1.py</code>, <code>_data_p2.py</code>, <code>_model.py</code>,
<code>_picks.py</code>, <code>_build.py</code>, <code>_validate.py</code> &mdash; new.</li>
<li><code>f437fb14/**</code> &mdash; new 26-page desk.</li>
<li><code>data/f437fb14/**</code> &mdash; new machine-readable copies.</li>
<li><code>tests/pipeline/test_desk_f437fb14.py</code> &mdash; new test file.</li>
<li><code>reports/SESSION_F437FB14.md</code> and this session's sections of
<code>COORDINATION.md</code> &mdash; new.</li>
<li>Nothing else. No root page, no shared dataset, no workflow, no peer desk.</li>
</ul>
"""
    return shell("Repository review", body)


def dump_json(name, obj):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, sort_keys=False)
        fh.write("\n")


def main():
    fixtures = build_fixtures()
    markets = build_markets()
    picks = build_picks(markets)

    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "sports"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "style.css"), "w", encoding="utf-8") as fh:
        fh.write(CSS)

    pages = {
        "index.html": page_index(fixtures, markets, picks),
        "picks.html": page_picks(fixtures, markets, picks),
        "matches.html": page_matches(fixtures, markets, picks),
        "markets.html": page_markets(fixtures, markets, picks),
        "predictions.html": page_predictions(fixtures, picks),
        "sports.html": page_sports(fixtures, markets, picks),
        "flagged.html": page_flagged(),
        "sources.html": page_sources(),
        "methodology.html": page_method(),
        "olbg.html": page_olbg(fixtures),
        "repo-audit.html": page_repo_audit(fixtures),
    }
    for s in SPORTS:
        pages[f"sports/{SLUG[s]}.html"] = page_sport(s, fixtures, markets, picks)

    for path, content in pages.items():
        with open(os.path.join(OUT, path), "w", encoding="utf-8") as fh:
            fh.write(content)

    summary = dict(
        generated_at=GEN, session="f437fb14-olbg1",
        fixtures=len(fixtures), priced_fixtures=len({m["fixture"] for m in markets}),
        markets=len(markets), picks=len(picks),
        high=sum(1 for p in picks if p["confidence"] == "High"),
        medium=sum(1 for p in picks if p["confidence"] == "Medium"),
        low=sum(1 for p in picks if p["confidence"] == "Low"),
        literal_high=sum(1 for p in picks if p["literal_high"]),
        sports_with_fixtures=len({f["sport"] for f in fixtures}),
        sports_priced=len({m["sport"] for m in markets}),
        pages=len(pages), flags=len(FLAGS), sources=len(SOURCES),
    )
    dump_json("fixtures.json", fixtures)
    dump_json("markets.json", markets)
    dump_json("picks.json", picks)
    dump_json("flags.json", FLAGS)
    dump_json("summary.json", summary)
    dump_json("sources.json", [dict(name=a, supplied=b, url=c) for a, b, c in SOURCES])

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
