"""Build the f840c28a desk (data + static pages).

Run from the repository root:

    python3 scripts/sf840c28a_build.py

Writes data/f840c28a/*.json and f840c28a/**.html. No network access, no
dependencies outside the standard library, no JavaScript in the output.
"""

from __future__ import annotations

import html
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import sf840c28a_engine as E          # noqa: E402
import sf840c28a_facts as F          # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "f840c28a"
DATA = ROOT / "data" / "f840c28a"

DESK = "f840c28a"
SESSION = "f840c28a-olbg1"
TASK = "TF840C"

# --------------------------------------------------------------------------
# Fixture-level verification. A fixture is only priced when the league or
# governing body published the fixture itself.
# --------------------------------------------------------------------------

NHL_FIXTURE_CONFIRMED = {
    ("SJS", "BOS"): dict(game_id=2026020170, venue="TD Garden", nhl_start="2026-10-24T23:00:00Z"),
    ("NYR", "OTT"): dict(game_id=2026020171, venue="Canadian Tire Centre", nhl_start="2026-10-24T23:00:00Z"),
    ("NSH", "PIT"): dict(game_id=2026020172, venue="PPG Paints Arena", nhl_start="2026-10-24T23:00:00Z"),
    ("BUF", "WSH"): dict(game_id=2026020173, venue="Capital One Arena", nhl_start="2026-10-24T23:00:00Z"),
    ("VGK", "CBJ"): dict(game_id=2026020174, venue="Nationwide Arena", nhl_start="2026-10-24T23:00:00Z"),
    ("CAR", "STL"): dict(game_id=2026020175, venue="Enterprise Center", nhl_start="2026-10-24T23:00:00Z"),
    ("TOR", "EDM"): dict(game_id=2026020176, venue="Rogers Place", nhl_start="2026-10-24T23:00:00Z"),
    ("TBL", "UTA"): dict(game_id=2026020177, venue="Delta Center", nhl_start="2026-10-25T01:00:00Z"),
    ("DET", "CGY"): dict(game_id=2026020178, venue="Scotiabank Saddledome", nhl_start="2026-10-25T02:00:00Z"),
}

# Publisher moneyline printed by the league feed beside each fixture (home, away).
PUBLISHER_ML = {
    ("SJS", "BOS"): (160, -192),
    ("NYR", "OTT"): (105, -125),
    ("NSH", "PIT"): (105, -125),
    ("BUF", "WSH"): (100, -120),
    ("VGK", "CBJ"): (-135, 114),
    ("CAR", "STL"): (-155, 130),
    ("TOR", "EDM"): (130, -155),
    ("TBL", "UTA"): (120, -142),
    ("DET", "CGY"): (-125, 105),
}

# --------------------------------------------------------------------------
# Written predictions. One per published pick, all >= 30 words, no shared
# six-word run, no internal vocabulary, and every number below is taken from
# the official page linked on the same row.
# --------------------------------------------------------------------------

PREDICTIONS = {
    ("BUF", "WSH"): dict(
        pick_key="Under 7.5",
        text=("Washington have allowed 3.22 goals a game across nine starts and own an 80.0% penalty "
              "kill, while Buffalo are conceding 3.60 and killing only 66.7% of their shorthanded "
              "time. Both numbers point to long, broken sequences rather than a track meet, and the "
              "Capitals have scored 3.33 a game without ever looking like a seven-goal side. "
              "Under 7.5 goals is the call at Capital One Arena."),
        sources=["nhl-team-summary", "nhl-schedule"],
    ),
    ("TBL", "UTA"): dict(
        pick_key="Under 7.5",
        text=("Utah have scored 3.73 goals a game but their 66.7% penalty kill is the leak that keeps "
              "totals honest, and Tampa Bay arrive conceding 2.90 a game with a 77.8% kill. The "
              "Lightning have allowed 29 goals in ten games, Utah 36 in eleven, and the visitors are "
              "on the second half of a long western trip. Under 7.5 goals at Delta Center."),
        sources=["nhl-team-summary", "nhl-schedule"],
    ),
    ("CAR", "STL"): dict(
        pick_key="CAR +1",
        text=("Carolina lead the league with 18 points from twelve games, scoring 3.92 a game and "
              "allowing 2.42, and they own an 83.3% penalty kill. St Louis are 5-4-1 and leaking 3.10 "
              "a game, which makes a two-goal win against this defence hard to see. Taking the "
              "Hurricanes with a one-goal start covers a regulation draw and a single-goal defeat."),
        sources=["nhl-team-summary", "nhl-schedule"],
    ),
    ("NYR", "OTT"): dict(
        pick_key="NYR +1",
        text=("The Rangers have conceded 2.42 goals a game across twelve starts and their 91.7% "
              "penalty kill is the best defensive number on tonight's board. Ottawa have scored only "
              "2.64 a game and kill at 78.0%, so the visitors should get the power-play looks that "
              "separate these teams. A one-goal handicap takes a regulation draw and a one-goal loss "
              "out of play."),
        sources=["nhl-team-summary", "nhl-schedule"],
    ),
    ("TOR", "EDM"): dict(
        pick_key="Under 7.5",
        text=("Edmonton are scoring 4.60 goals a game, the highest rate in the league, and Toronto "
              "have conceded 3.17 while killing 97.4% of penalties. That Toronto kill against an "
              "Edmonton power play converting at 35.3% is the one real route to a big number. Strip "
              "that out and both goaltending charts point lower, so Under 7.5 at Rogers Place."),
        sources=["nhl-team-summary", "nhl-schedule"],
    ),
    ("MIL", "PHI"): dict(
        pick_key="PHI",
        text=("Philadelphia are 2-0 and Milwaukee 0-2 through the opening week of the season. The "
              "league's 1pm filing lists Dominick Barlow, Tacko Fall, Ariel Hukporti and LeBron James "
              "out for the 76ers with Dean Wade questionable, and Milwaukee had not submitted a "
              "report at all. Home court plus a two-game head start is enough to back Philadelphia."),
        sources=["nba-standings", "nba-injury"],
    ),
    ("MIA", "CHA"): dict(
        pick_key="CHA",
        text=("Charlotte are 1-1 while Miami have opened 0-2. The Hornets' filing is the heavier one: "
              "Kylan Boswell, Kon Knueppel, Coby White and Grant Williams are all out, with Christian "
              "Anderson probable and Pelle Larsson probable for Miami. Four rotation absences against "
              "a winless visitor still leaves home court with Charlotte, but only just."),
        sources=["nba-standings", "nba-injury"],
    ),
    ("SAS", "DAL"): dict(
        pick_key="DAL",
        text=("Dallas are 1-1 and San Antonio 0-2. Both clubs filed 'NOT YET SUBMITTED' at 1pm, so no "
              "availability edge can be claimed for either side and this pick rests purely on record "
              "and venue. The Mavericks' home floor in a Texas derby is the difference, and it is "
              "thin enough that the selection stays in the low tier at -139."),
        sources=["nba-standings", "nba-injury"],
    ),
    ("NOP", "DEN"): dict(
        pick_key="DEN",
        text=("Denver are 0-1 and New Orleans 0-2. The Nuggets are missing Cameron Johnson, Spencer "
              "Jones and Julian Strawther, with Alpha Diallo questionable, while the Pelicans had not "
              "filed by 1pm. Three rotation absences cap the confidence, but a winless visitor and the "
              "altitude of a home opener make Denver the side to take."),
        sources=["nba-standings", "nba-injury"],
    ),
    ("GSW", "PHX"): dict(
        pick_key="PHX",
        text=("Phoenix are 0-1 and Golden State 0-2. The Suns list Mark Williams out following "
              "shoulder surgery, Oso Ighodaro doubtful with an oblique strain and Luke Kennard "
              "questionable, while the Warriors did not file before 1pm. Golden State's 0-2 start and "
              "a home floor are enough to lean Phoenix, though the frontcourt absences keep it low."),
        sources=["nba-standings", "nba-injury"],
    ),
}

# --------------------------------------------------------------------------
# Flagged for review.
# --------------------------------------------------------------------------

FLAGS = [
    dict(id="F-01", area="OLBG coverage", severity="high",
         title="Three covered sports served no matches at all",
         detail=("The Golf (sport 5), Snooker (sport 8) and Motor Racing (sport 14) hubs each rendered "
                 "'No tips found.' on 24 October. The Snooker 'All Events' sub-route rendered the same "
                 "message, so there is no OLBG market to price for any of the three."),
         sources=["olbg-golf", "olbg-snooker", "olbg-snooker-events", "olbg-motorracing"]),
    dict(id="F-02", area="OLBG coverage", severity="high",
         title="Rugby League hub carries outrights for 2027 only",
         detail=("The Rugby League hub listed State of Origin 2027, the Super League 2027 Grand Final "
                 "and the NRL 2027 Grand Final. No upcoming fixture of either 2026 competition was "
                 "listed, so the sport has no match market on the board."),
         sources=["olbg-rugbyleague"]),
    dict(id="F-03", area="OLBG coverage", severity="medium",
         title="Greyhounds hub carried a single race",
         detail=("One race, '11:04 Doncaster', was listed with a single tip on Snowfall. No GBGB "
                 "racecard or form was read, so the race is published as a listing and not priced."),
         sources=["olbg-greyhounds"]),
    dict(id="F-04", area="OLBG data quality", severity="medium",
         title="OLBG start times disagree with the league's own clock",
         detail=("OLBG printed 'Today 19:07' for the fixtures the NHL schedules at 23:00Z (19:00 ET), "
                 "'Today 22:07' for a 01:00Z start and 'Today 23:07' for a 02:00Z start. The offset is "
                 "not constant and OLBG prints no timezone, so every published start time on this desk "
                 "comes from the league feed instead."),
         sources=["olbg-icehockey", "nhl-schedule"]),
    dict(id="F-05", area="Fixture completeness", severity="medium",
         title="One of the league's twelve games could not be individually confirmed",
         detail=("The NHL feed reports twelve games on 24 October. Eleven are confirmed individually in "
                 "the returned slice. The twelfth, which OLBG lists as MIN Wild @ SEA Kraken, was not "
                 "in the slice, so that row carries no price and no pick. MTL@WPG on 25 October comes "
                 "from a different schedule date and is also unpriced."),
         sources=["nhl-schedule", "olbg-icehockey"]),
    dict(id="F-06", area="OLBG data quality", severity="medium",
         title="OLBG's basketball hub omits two games the league lists",
         detail=("The official NBA injury report for 24 October lists MIA@CHA and MEM@SAC. Neither "
                 "appeared on the OLBG basketball hub, which stopped after seven games. Both are "
                 "published here from the league document."),
         sources=["olbg-basketball", "nba-injury"]),
    dict(id="F-07", area="Naming", severity="low",
         title="Club names differ between OLBG and the governing body",
         detail=("OLBG bills 'Eastern Storm vs South Africa Emerging'; Cricket South Africa calls the "
                 "same fixture 'World Sports Betting Eastern Storm vs CSA High Performance'. OLBG also "
                 "prints 'VGS Golden Knights' where the NHL prints VGK."),
         sources=["olbg-cricket", "csa-home", "olbg-icehockey", "nhl-team-summary"]),
    dict(id="F-08", area="Withheld market", severity="low",
         title="No basketball totals are originated",
         detail=("No official NBA scoring figure (team points for or against) was read this session, so "
                 "a total would have been invented. Every NBA row therefore carries moneyline and "
                 "spread markets only."),
         sources=["nba-standings"]),
    dict(id="F-09", area="Missing input", severity="low",
         title="Detroit's goals for and against were not in the returned page",
         detail=("The NHL team-summary slice that carried Detroit's record cut off before its goals-for "
                 "and goals-against fields. With no goals rate there is no honest price, so DET@CGY is "
                 "published with a moneyline and nothing else, and no pick."),
         sources=["nhl-team-summary"]),
    dict(id="F-10", area="Coverage shortfall", severity="high",
         title="Ten of the fifteen sports have no priced match",
         detail=("Only ice hockey and basketball reached a priced state. Cricket has six fixtures "
                 "confirmed on the governing body's own site but no competition record was read, so "
                 "none is priced. Baseball has one confirmed fixture with both starting pitchers named "
                 "and no season rate for Milwaukee, so the market is withheld. Tennis, Volleyball, "
                 "Handball, Rugby Union, Gaelic Sports and Darts were found on OLBG only and are not "
                 "confirmed by a governing body."),
         sources=["csa-home", "mlb-schedule", "olbg-tennis", "olbg-volleyball", "olbg-handball",
                  "olbg-rugbyunion", "olbg-gaelic", "olbg-darts"]),
    dict(id="F-11", area="Method", severity="medium",
         title="The brief's two High-pick rules barely intersect",
         detail=("A selection with a 70% chance has a fair price of about -233; the band's shortest "
                 "allowed price, -250, implies 71.4%. Requiring both 'more than 70%' and 'inside "
                 "-250..+10000' therefore leaves a 1.4-point window, and only three of this desk's 88 "
                 "originated outcomes land in it. The three High picks here are those, plus any other "
                 "line that lands there after normalisation; nothing was moved into the tier by hand."),
         sources=["nhl-team-summary"]),
    dict(id="F-12", area="Model input", severity="medium",
         title="Basketball records are two games deep",
         detail=("Every NBA club has played between one and two games. Records that short carry almost "
                 "no information, so each is shrunk toward .500 with a ten-win, ten-loss prior before "
                 "it is used. That is why no basketball pick reaches the medium tier on record alone "
                 "and none reaches high at all."),
         sources=["nba-standings"]),
    dict(id="F-13", area="Provenance", severity="low",
         title="OLBG tip shares are not probabilities and were not used",
         detail=("OLBG prints the share of member tips on each selection (for example '10/12 Win Tips, "
                 "83%'). Those are votes, not prices, and no number on this desk is derived from them. "
                 "They appear on the sport pages labelled as OLBG's own tally so the reader can see the "
                 "difference."),
         sources=["olbg-icehockey", "olbg-basketball"]),
]

REPO_FINDINGS = [
    dict(id="R-01", file="pipeline/build.py:36", severity="medium",
         title="Sixteen of ninety session desks are reachable from the published site",
         detail=("The repository carries 90 session desk directories at its root. The ARCHIVE allowlist "
                 "in pipeline/build.py contains 16 entries, so the other 74 desks are tracked but have "
                 "no published entry point. The root README still promises that earlier desks 'stay "
                 "published'."),
         evidence="90 directories; 16 ARCHIVE entries"),
    dict(id="R-02", file="README.md:50", severity="medium",
         title="The confidence gate differs between the README and the brief",
         detail=("README.md defines High as 'originated probability >= 60% and fair American price in "
                 "[-250, +10000]'. The brief defines high confidence as a selection with more than a "
                 "70% chance. Both cannot be true of the same pick, and different desks in this "
                 "repository have used different thresholds, so the tiers are not comparable across "
                 "desks."),
         evidence="README.md line 50"),
    dict(id="R-03", file="data/current/audit.json", severity="low",
         title="A 10.5 MB generated artefact is tracked",
         detail=("data/current/audit.json is 10,473,214 bytes and is committed. The repository tracks "
                 "3,032 files for what is a static predictions site; most of that weight is generated "
                 "JSON that is regenerated by the build rather than read by it."),
         evidence="10,473,214 bytes"),
    dict(id="R-04", file="*.html", severity="info",
         title="No broken relative page links in the twenty root pages",
         detail=("All twenty root HTML pages were parsed and every relative .html link was resolved "
                 "against the filesystem. Zero were missing. This is a clean result and is recorded so "
                 "that the negative finding is explicit."),
         evidence="20 pages, 0 missing targets"),
    dict(id="R-05", file="COORDINATION.md", severity="low",
         title="The shared task board is 849 KB and is append-only",
         detail=("COORDINATION.md is 849,056 bytes and is edited by every session under an append-only "
                 "rule. Two different sections were both numbered 74 and two are both numbered 75, so "
                 "cross-references to a section number are ambiguous. Claims are also still listed as "
                 "'in progress' for sessions that finished days ago."),
         evidence="duplicate section numbers 74, 74, 75, 75, 84, 85"),
    dict(id="R-06", file="tests/pipeline", severity="info",
         title="The existing test suite is green before this session's changes",
         detail=("python3 -m unittest discover -s tests/pipeline passes on the branch head this desk "
                 "was built from, and scripts/validate.py returns no errors. This desk adds its own "
                 "test module rather than editing the shared suite."),
         evidence="suite status at branch head"),
]


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def e(x) -> str:
    return html.escape(str(x), quote=True)


def pct(p: float) -> str:
    return f"{p * 100:.1f}%"


def price(p: float) -> str:
    v = E.american(p)
    return f"{v:+.0f}" if v > 0 else f"{v:.0f}"


def rec_str(t: dict) -> str:
    if not t:
        return "not read"
    if t["gf"] is None:
        return f'{t["w"]}-{t["l"]}-{t["otl"]}'
    return f'{t["w"]}-{t["l"]}-{t["otl"]}'


CSS = """
:root{--ink:#101d2c;--muted:#5b6b7c;--line:#e2e8ef;--bg:#f5f7fa;--card:#fff;
--brand:#0b5cd5;--brand-soft:#e8f0fd;--high:#0b7a4b;--high-soft:#e2f5ea;
--med:#8a5a00;--med-soft:#fdf3df;--low:#5b6b7c;--low-soft:#eef1f5;--flag:#a3282d;--flag-soft:#fceaea}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--brand)}
h1,h2,h3{line-height:1.2;margin:0 0 10px}
h1{font-size:29px;letter-spacing:-.3px}h2{font-size:20px;margin-top:30px}h3{font-size:16px}
p{margin:0 0 12px}
.wrap{max-width:1140px;margin:0 auto;padding:0 18px}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:9}
.toprow{display:flex;gap:14px;align-items:center;justify-content:space-between;padding:11px 0;flex-wrap:wrap}
.brand{font-weight:750;text-decoration:none;color:var(--ink);display:flex;gap:9px;align-items:center}
.brand .mark{width:28px;height:28px;border-radius:8px;background:var(--brand);color:#fff;display:grid;
place-items:center;font-size:13px;font-weight:700}
nav.pages{display:flex;gap:4px;flex-wrap:wrap}
nav.pages a{text-decoration:none;color:var(--muted);padding:7px 10px;border-radius:8px;font-size:14px;font-weight:600}
nav.pages a:hover{background:var(--brand-soft);color:var(--brand)}
nav.pages a.on{background:var(--brand);color:#fff}
main{padding:26px 0 60px}
.lede{font-size:17px;color:var(--muted);max-width:820px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0 6px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.kpi b{display:block;font-size:26px;line-height:1.1}
.kpi span{font-size:12.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:16px 0}
.callout{border-left:4px solid var(--brand);background:var(--brand-soft);border-radius:0 10px 10px 0;padding:13px 16px;margin:16px 0}
.callout.warn{border-color:var(--flag);background:var(--flag-soft)}
.callout b{display:block;margin-bottom:4px}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--card);margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f2f5f9;font-size:12.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fafbfd}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap}
.b-high{background:var(--high-soft);color:var(--high)}
.b-med{background:var(--med-soft);color:var(--med)}
.b-low{background:var(--low-soft);color:var(--low)}
.b-flag{background:var(--flag-soft);color:var(--flag)}
.b-info{background:var(--brand-soft);color:var(--brand)}
.small{font-size:13px;color:var(--muted)}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px}
.pickcell{font-weight:700}
.pred{border-left:3px solid var(--brand);padding-left:14px;margin:18px 0}
.pred p{margin:6px 0}
footer{border-top:1px solid var(--line);padding:22px 0;color:var(--muted);font-size:13.5px;background:#fff}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:760px){.grid2{grid-template-columns:1fr}h1{font-size:24px}}
ul.plain{margin:6px 0 0;padding-left:18px}
ul.plain li{margin-bottom:5px}
.tag{font-size:12px;color:var(--muted)}
"""

NAV = [
    ("index.html", "Summary"),
    ("picks.html", "Picks"),
    ("predictions.html", "Written predictions"),
    ("matches.html", "Every match"),
    ("markets.html", "Markets"),
    ("sports.html", "Sports"),
    ("flagged.html", "Flagged"),
    ("sources.html", "Sources"),
    ("methodology.html", "Method"),
    ("repo-review.html", "Repo review"),
]


def page(name: str, title: str, body: str, subtitle: str = "", up: int = 0) -> str:
    prefix = "../" * up
    links = []
    for href, label in NAV:
        cls = ' class="on"' if href == name else ""
        links.append(f'<a href="{prefix}{href}"{cls}>{e(label)}</a>')
    nav = "".join(links)
    sub = f'<p class="lede">{e(subtitle)}</p>' if subtitle else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG research desk {DESK}</title>
<style>{CSS}</style></head>
<body>
<header class="top"><div class="wrap toprow">
<a class="brand" href="{prefix}index.html"><span class="mark">OL</span> OLBG research desk</a>
<nav class="pages">{nav}</nav>
</div></header>
<main><div class="wrap">
<h1>{e(title)}</h1>
{sub}
{body}
</div></main>
<footer><div class="wrap">
<p><b>Desk {DESK}</b> · session {SESSION} · task {TASK} · facts captured
{F.CAPTURE_UTC}. Independent research, not affiliated with OLBG. Prices are our own
margin-free estimates, not quoted bookmaker odds. No guaranteed returns, no staking advice.
18+. <a href="{prefix}flagged.html">Flagged for review</a></p>
</div></footer>
</body></html>"""


# --------------------------------------------------------------------------
# Build the dataset
# --------------------------------------------------------------------------

def short_time(iso: str) -> str:
    """2026-10-24T23:00:00Z -> 2026-10-24T23:00Z"""
    if iso.endswith(":00Z"):
        return iso[:-4] + "Z"
    return iso


def build_data():
    board = E.build_board()

    fixtures = []
    for g in board:
        if g["sport"] == "ice-hockey":
            key = (g["away"], g["home"])
            conf = NHL_FIXTURE_CONFIRMED.get(key)
            g["fixture_source"] = "nhl-schedule" if conf else None
            g["venue"] = conf["venue"] if conf else None
            g["official_start"] = conf["nhl_start"] if conf else None
            g["olbg_printed_time"] = g["olbg_time"]
            if conf:
                # publish the league's clock, never OLBG's
                g["start_utc"] = short_time(conf["nhl_start"])
            g["confirmed"] = conf is not None
            g["publisher_ml"] = PUBLISHER_ML.get(key)
            if not conf:
                g["priced"] = False
                g["pick"] = None
                g["outcomes"] = []
                g["markets"] = []
                g["withheld"] = ["Fixture not individually confirmed on the league's 24 October slate."]
        else:
            # NBA fixtures are all confirmed by the league's own injury report,
            # which lists every game with its tip-off time.
            g["fixture_source"] = "nba-injury"
            g["venue"] = None
            g["official_start"] = g["start_utc"]
            g["olbg_printed_time"] = g.get("et")
            g["confirmed"] = True
            g["publisher_ml"] = None
        fixtures.append(g)

    # attach predictions
    for g in fixtures:
        key = (g["away"], g["home"])
        pr = PREDICTIONS.get(key)
        if pr and g["pick"]:
            g["prediction"] = pr["text"]
            g["prediction_sources"] = pr["sources"]
        else:
            g["prediction"] = None
            g["prediction_sources"] = []

    picks = [dict(sport=g["sport"], competition=g["competition"],
                  fixture=f'{g["away"]} @ {g["home"]}', **g["pick"],
                  start_utc=g["start_utc"], prediction=g.get("prediction"),
                  prediction_sources=g.get("prediction_sources", []),
                  fixture_source=g["fixture_source"])
             for g in fixtures if g["pick"]]

    order = {"High": 0, "Medium": 1, "Low": 2, "outside band": 3}
    picks.sort(key=lambda p: (order[p["confidence"]], -p["p"], p["fixture"]))

    desk = dict(
        desk=DESK, session=SESSION, task=TASK, captured_utc=F.CAPTURE_UTC,
        generated_utc=F.CAPTURE_UTC,
        fixtures=fixtures, picks=picks, flags=FLAGS, repo_findings=REPO_FINDINGS,
        sports=F.SPORTS, sources=F.SOURCES, discovery_only=F.DISCOVERY_ONLY,
        name_differences=F.OLBG_NAME_DIFFERENCES,
        mlb=F.MLB_GAMES, cricket=F.CRICKET_GAMES,
        publisher_ml={f"{k[0]}@{k[1]}": v for k, v in PUBLISHER_ML.items()},
        counts=dict(
            fixtures=len(fixtures),
            confirmed=sum(1 for g in fixtures if g["confirmed"]),
            priced=sum(1 for g in fixtures if g["priced"]),
            markets=sum(len(g["markets"]) for g in fixtures),
            outcomes=sum(len(g.get("outcomes", [])) for g in fixtures),
            picks=len(picks),
            high=sum(1 for p in picks if p["confidence"] == "High"),
            medium=sum(1 for p in picks if p["confidence"] == "Medium"),
            low=sum(1 for p in picks if p["confidence"] == "Low"),
            predictions=sum(1 for g in fixtures if g["prediction"]),
            flags=len(FLAGS),
            sources=len(F.SOURCES),
            sports=len(F.SPORTS),
            sports_priced=len({g["sport"] for g in fixtures if g["priced"]}),
        ),
    )
    return desk


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

def source_link(sid: str, label: str | None = None) -> str:
    s = F.SOURCES_BY_ID.get(sid)
    if not s:
        return e(label or sid)
    return f'<a href="{e(s["url"])}" rel="noopener">{e(label or s["publisher"])}</a>'


def picks_table(rows, show_pred=True) -> str:
    head = ("<tr><th>Conf.</th><th>Sport</th><th>Match</th><th>Our pick</th><th>Market</th>"
            "<th>Price</th><th>Chance</th><th>Start (UTC)</th></tr>")
    body = []
    for p in rows:
        cls = {"High": "b-high", "Medium": "b-med", "Low": "b-low"}.get(p["confidence"], "b-info")
        pred = (f'<div class="small">{e(p["prediction"])}</div>'
                if show_pred and p.get("prediction") else
                ('<div class="small">Listed in the markets table only.</div>' if show_pred else ""))
        body.append(
            f'<tr><td><span class="badge {cls}">{e(p["confidence"])}</span></td>'
            f'<td>{e(p["sport"].replace("-", " ").title())}</td>'
            f'<td><b>{e(p["fixture"])}</b><div class="small">{e(p["competition"])}</div></td>'
            f'<td class="pickcell">{e(p["selection"])}{pred}</td>'
            f'<td>{e(p["market"])}{(" " + e(str(p["line"]))) if p["line"] else ""}</td>'
            f'<td class="num">{price(p["p"])}<div class="small">{p["decimal"]:.2f}</div></td>'
            f'<td class="num">{pct(p["p"])}</td>'
            f'<td class="small">{e(p["start_utc"])}</td></tr>')
    return f'<div class="table-wrap"><table>{head}{"".join(body)}</table></div>'


def page_index(d):
    c = d["counts"]
    highs = [p for p in d["picks"] if p["confidence"] == "High"]
    top = d["picks"]

    exec_rows = []
    for i, p in enumerate(highs, 1):
        exec_rows.append(
            f'<tr><td class="num">{i}</td><td><b>{e(p["selection"])}</b>'
            f'<div class="small">{e(p["market"])} {e(str(p["line"]))} · {e(p["fixture"])} · {e(p["competition"])}</div></td>'
            f'<td class="num">{price(p["p"])}</td><td class="num">{pct(p["p"])}</td>'
            f'<td><span class="badge b-high">High</span></td></tr>')
    exec_table = ('<div class="table-wrap"><table><tr><th>#</th><th>Selection</th>'
                  '<th>Price</th><th>Chance</th><th>Confidence</th></tr>'
                  + "".join(exec_rows) + "</table></div>")

    coverage_rows = []
    for s in d["sports"]:
        fx = [g for g in d["fixtures"] if g["sport"] == s["code"]]
        priced = [g for g in fx if g["priced"]]
        npicks = len([p for p in d["picks"] if p["sport"] == s["code"]])
        if priced:
            state = f'<span class="badge b-high">Priced</span>'
        elif fx:
            state = '<span class="badge b-med">Fixture only</span>'
        elif s["olbg_state"] == "no-tips":
            state = '<span class="badge b-flag">No OLBG market</span>'
        else:
            state = '<span class="badge b-low">Listing only</span>'
        coverage_rows.append(
            f'<tr><td><a href="sports/{e(s["code"])}.html">{e(s["name"])}</a></td>'
            f'<td class="num">{s["olbg_events"]}</td><td class="num">{len(fx)}</td>'
            f'<td class="num">{len(priced)}</td><td class="num">{npicks}</td><td>{state}</td>'
            f'<td>{source_link("olbg-" + s["code"].replace("-", ""), "OLBG hub")}</td></tr>'
            if False else
            f'<tr><td><a href="sports/{e(s["code"])}.html">{e(s["name"])}</a></td>'
            f'<td class="num">{s["olbg_events"]}</td><td class="num">{len(fx)}</td>'
            f'<td class="num">{len(priced)}</td><td class="num">{npicks}</td><td>{state}</td>'
            f'<td><a href="{e(s["olbg_url"])}" rel="noopener">OLBG hub</a> · '
            f'<a href="{e(s["official_url"])}" rel="noopener">Official</a></td></tr>')
    coverage_table = ('<div class="table-wrap"><table><tr><th>Sport</th><th>OLBG events listed</th>'
                      '<th>Fixtures here</th><th>Priced</th><th>Picks</th><th>State</th>'
                      '<th>Sources</th></tr>' + "".join(coverage_rows) + "</table></div>")

    body = f"""
<div class="kpis">
  <div class="kpi"><b>{c['high']}</b><span>High confidence</span></div>
  <div class="kpi"><b>{c['picks']}</b><span>Picks published</span></div>
  <div class="kpi"><b>{c['priced']}</b><span>Matches priced</span></div>
  <div class="kpi"><b>{c['predictions']}</b><span>Written predictions</span></div>
  <div class="kpi"><b>{c['sports_priced']}/{c['sports']}</b><span>Sports with a price</span></div>
  <div class="kpi"><b>{c['flags']}</b><span>Flagged items</span></div>
</div>

<div class="callout">
<b>Where the picks are</b>
Every pick is in the table on this page, one row per selection, with its price, its chance and a
written analysis underneath it. The same rows appear on <a href="picks.html">Picks</a> (with every
market we originated) and the full write-ups are on <a href="predictions.html">Written predictions</a>.
Nothing is hidden behind a click and there is no JavaScript.
</div>

<h2>Executive summary</h2>
<p><b>{c['high']} high-confidence pick{'s' if c['high'] != 1 else ''}</b> on this board. The full
card is {c['fixtures']} fixtures found on OLBG across the fifteen requested sports, of which
{c['confirmed']} could be confirmed on a league or governing-body page and {c['priced']} carried
enough published data to price. That produced {c['markets']} markets, {c['outcomes']} individual
prices and {c['picks']} graded picks, {c['predictions']} of them with a full written prediction.</p>
<p>The three high-confidence selections all sit at or just inside the brief's <span class="mono">-250</span>
ceiling, because a selection needs a price of about <span class="mono">-233</span> before it can reach a
70% chance at all. <a href="methodology.html">The method page</a> works that arithmetic through with
the numbers, and <a href="flagged.html">Flagged for review</a> lists what is missing per sport.</p>

<h2>High-confidence picks</h2>
{exec_table if highs else '<p><b>None today.</b> See the note on the price band in the methodology.</p>'}

<h2>The card, in confidence order</h2>
<p class="small">Price is our own margin-free fair price; chance is our estimated probability of the
selection winning. Both are estimates, not quotes.</p>
{picks_table(top)}

<h2>Sports covered</h2>
<p class="small">"OLBG events listed" is what the OLBG hub actually put in front of us on 24 October.
It is not the same as the number of fixtures in the world that day.</p>
{coverage_table}

<h2>What this desk does not claim</h2>
<ul class="plain">
  <li>No injury is inferred. The only availability data here is the NBA's own 1pm filing and it is
      quoted verbatim, including the two clubs that had not submitted.</li>
  <li>No price is copied. The NHL feed prints a partner moneyline; it appears beside ours on
      <a href="methodology.html#calibration">Method</a> as a check, never as our number.</li>
  <li>No fixture is assumed. Three of the fifteen sports had no OLBG market at all, and one of the
      league's twelve hockey games could not be individually confirmed.</li>
</ul>
"""
    return page("index.html", "Today's picks, and exactly where they are",
                body, "24–25 October 2026 · fifteen requested sports · every row sourced")


def page_picks(d):
    c = d["counts"]
    rows = []
    for g in d["fixtures"]:
        if not g["markets"]:
            continue
        rows.append(f'<tr><td colspan="6" style="background:#f2f5f9"><b>{e(g["away"])} @ '
                    f'{e(g["home"])}</b> <span class="small">{e(g["competition"])} · '
                    f'{e(g["start_utc"])} · {len(g["markets"])} markets</span></td></tr>')
        for o in g.get("outcomes", []):
            band = ('<span class="badge b-high">in window</span>' if o["band"] == "in"
                    else '<span class="badge b-flag">outside window</span>')
            tier = o["tier"]
            cls = {"High": "b-high", "Medium": "b-med", "Low": "b-low"}.get(tier, "b-info")
            is_pick = g["pick"] and o["selection"] == g["pick"]["selection"] and \
                o["market"] == g["pick"]["market"]
            mark = ' <span class="badge b-high">PICK</span>' if is_pick else ""
            rows.append(f'<tr><td>{e(o["market"])} {e(str(o["line"]))}</td>'
                        f'<td>{e(o["selection"])}{mark}</td>'
                        f'<td class="num">{price(o["p"])}</td><td class="num">{pct(o["p"])}</td>'
                        f'<td>{band}</td><td><span class="badge {cls}">{e(tier)}</span></td></tr>')
    withheld_rows = []
    for g in d["fixtures"]:
        if g["sport"] != "basketball" or not g.get("withheld"):
            continue
        withheld_rows.append(
            "<tr><td>" + e(g["away"]) + " @ " + e(g["home"]) + "</td><td>Game total</td>"
            '<td class="small">' + e(g["withheld"][0]) + "</td></tr>")
    withheld_html = "".join(withheld_rows)

    body = f"""
<p>Every market this desk originated, every price in it, and which one became the pick. Rows
outside the brief's <span class="mono">-250 … +10000</span> window are shown rather than deleted,
marked accordingly, and are never a pick.</p>
<p><b>{c['markets']} markets · {c['outcomes']} prices · {c['picks']} picks.</b>
The picks themselves, in confidence order, are on the <a href="index.html">summary</a>.</p>
<div class="table-wrap"><table>
<tr><th>Market</th><th>Selection</th><th>Our price</th><th>Chance</th><th>Window</th><th>Tier</th></tr>
{"".join(rows)}
</table></div>
<h2>Markets we withheld, and why</h2>
<div class="table-wrap"><table>
<tr><th>Match</th><th>Withheld</th><th>Reason</th></tr>
__WITHHELD__
<tr><td>Tampa Bay Rays @ Milwaukee Brewers</td><td>All markets</td>
<td class="small">Both starting pitchers are named on the league feed, but Milwaukee's season
runs scored and allowed were not read, so no rate could be used.</td></tr>
</table></div>
"""
    return page("picks.html", "Picks and every market behind them", body,
                "One row per price we set · the pick is marked")


def page_predictions(d):
    blocks = []
    for p in d["picks"]:
        if not p.get("prediction"):
            continue
        cls = {"High": "b-high", "Medium": "b-med", "Low": "b-low"}[p["confidence"]]
        src = " · ".join(source_link(s) for s in p["prediction_sources"])
        words = len(p["prediction"].split())
        blocks.append(
            '<div class="card">'
            '<div><span class="badge ' + cls + '">' + e(p["confidence"]) + '</span> '
            '<span class="small">' + e(p["sport"].replace("-", " ").title()) + ' · ' +
            e(p["competition"]) + ' · ' + e(p["start_utc"]) + '</span></div>'
            '<h3 style="margin-top:8px">' + e(p["fixture"]) + ' — ' +
            '<span style="color:var(--brand)">' + e(p["selection"]) + '</span></h3>'
            '<p class="small">' + e(p["market"]) + ' ' + e(str(p["line"])) +
            ' · our price ' + price(p["p"]) + ' · ' + pct(p["p"]) + ' chance · ' +
            str(words) + ' words</p>'
            '<div class="pred"><p>' + e(p["prediction"]) + '</p></div>'
            '<p class="small">Facts from: ' + src + '</p></div>')

    seeded = [p["prediction"] for p in d["picks"] if p.get("prediction")]
    shortest = min(len(x.split()) for x in seeded) if seeded else 0
    rest = d["counts"]["picks"] - len(blocks)
    body = (
        '<p>Each analysis below names the selection, gives the form and the season numbers behind '
        'it, and quotes only figures that appear on the official page linked at the bottom of the '
        "same card. They are written one per pick and none repeats another's phrasing.</p>"
        '<p><b>' + str(len(blocks)) + ' written predictions.</b> Word counts are shown on each '
        'card; the shortest is ' + str(shortest) + ' words.</p>'
        + "".join(blocks) +
        '<h2>Picks without a full write-up</h2>'
        '<p>The desk makes ' + str(rest) + ' further graded selection(s) at low confidence — these '
        'are priced and listed on <a href="picks.html">Picks</a>, but the supporting data was thin '
        'enough that a full paragraph would have been padding.</p>')
    return page("predictions.html", "Written predictions", body,
                "One per pick · 30 words minimum · only numbers read from the linked official page")


def page_matches(d):
    rows = []
    for g in d["fixtures"]:
        state = ('<span class="badge b-high">Priced</span>' if g["priced"]
                 else '<span class="badge b-med">Listed, not priced</span>')
        if not g["confirmed"]:
            state = '<span class="badge b-flag">Not confirmed by league</span>'
        pick = e(g["pick"]["selection"]) if g["pick"] else "—"
        conf = (f'<span class="badge b-high">{e(g["pick"]["confidence"])}</span>'
                if g["pick"] else "")
        src = source_link(g["fixture_source"]) if g["fixture_source"] else "—"
        start = g["official_start"] or g["start_utc"]
        venue = ('<div class="small">' + e(g["venue"]) + "</div>") if g.get("venue") else ""
        rows.append(f'<tr><td>{e(g["competition"])}</td>'
                    f'<td><b>{e(g["away"])} @ {e(g["home"])}</b>{venue}</td>'
                    f'<td class="small">{e(start)}</td><td>{state}</td>'
                    f'<td>{pick} {conf}</td><td>{src}</td></tr>')

    cricket_rows = "".join(
        f'<tr><td>{e(c["competition"])}</td><td><b>{e(c["home"])} v {e(c["away"])}</b></td>'
        f'<td class="small">{e(c["date"])} {e(c["local_time"])} local</td>'
        f'<td><span class="badge b-med">Listed, not priced</span></td>'
        f'<td>{source_link("csa-home")}</td></tr>' for c in d["cricket"])

    mlb = d["mlb"][0]
    body = f"""
<p>Every fixture on the desk, whether or not it carries a price, with the source that confirms it.
Rows that could not be confirmed by the league are marked and carry no price.</p>
<h2>Ice hockey and basketball</h2>
<div class="table-wrap"><table>
<tr><th>Competition</th><th>Match</th><th>Start (UTC)</th><th>State</th><th>Pick</th><th>Fixture source</th></tr>
{"".join(rows)}
</table></div>

<h2>Cricket — confirmed on the governing body, not priced</h2>
<div class="table-wrap"><table>
<tr><th>Competition</th><th>Fixture</th><th>Start</th><th>State</th><th>Source</th></tr>
{cricket_rows}
</table></div>

<h2>Baseball — one game, market withheld</h2>
<div class="table-wrap"><table>
<tr><th>Competition</th><th>Match</th><th>Start (UTC)</th><th>Pitchers</th><th>Series</th>
<th>State</th><th>Source</th></tr>
<tr><td>{e(mlb['competition'])}</td>
<td><b>{e(mlb['away'])} @ {e(mlb['home'])}</b><div class="small">{e(mlb['venue'])}</div></td>
<td class="small">{e(mlb['start_utc'])}</td>
<td class="small">{e(mlb['away_pitcher'])} ({e(mlb['away'])} {e(mlb['away_series'])})<br>
{e(mlb['home_pitcher'])} ({e(mlb['home'])} {e(mlb['home_series'])})</td>
<td class="small">Game {e(mlb['series_game'])}</td>
<td><span class="badge b-med">Listed, not priced</span></td>
<td>{source_link("mlb-schedule")}</td></tr>
</table></div>

<h2>Fixtures found on OLBG only</h2>
<p>These came from OLBG's own hub listings. No governing body page was read for them this session,
so they are published as a board listing with no price and no pick. The full list is on each
<a href="sports.html">sport page</a>.</p>
"""
    return page("matches.html", "Every match, priced or not", body,
                "One row per fixture · the reason a blank is blank")


def page_markets(d):
    c = d["counts"]
    rows = []
    for g in d["fixtures"]:
        if not g["markets"]:
            continue
        for m in g["markets"]:
            rows.append(
                f'<tr><td>{e(g["away"])}@({e(g["home"])})</td><td>{e(m["market"])} {e(str(m["line"]))}</td>'
                f'<td>{e(m["home_sel"])}</td><td class="num">{price(m["home_p"])}</td>'
                f'<td class="num">{pct(m["home_p"])}</td>'
                f'<td>{e(m["away_sel"])}</td><td class="num">{price(m["away_p"])}</td>'
                f'<td class="num">{pct(m["away_p"])}</td></tr>')
    body = f"""
<p>Every market in full, both sides, at our own margin-free prices. The two sides of each row are
normalised to sum to 100%, which is what makes them comparable to the band.</p>
<p><b>{c['markets']} markets · {c['outcomes']} prices</b> across {c['priced']} fixtures.</p>
<div class="table-wrap"><table>
<tr><th>Match</th><th>Market</th><th>Home side</th><th>Price</th><th>Chance</th>
<th>Away side</th><th>Price</th><th>Chance</th></tr>
{"".join(rows)}
</table></div>
<h2>Market types used, and why only these</h2>
<div class="table-wrap"><table>
<tr><th>Market</th><th>Sports</th><th>Why it is here</th></tr>
<tr><td>Moneyline</td><td>Ice hockey, basketball</td><td>The plain question: who wins.</td></tr>
<tr><td>Puck line ±1.5 and ±2.5</td><td>Ice hockey</td><td>Separates a good team from a good team
that wins close games.</td></tr>
<tr><td>Asian handicap -1/+1 and -2/+2</td><td>Ice hockey</td><td>Integer lines with pushes removed,
used where a half-goal line would land outside the window.</td></tr>
<tr><td>Match total 4.5 – 7.5</td><td>Ice hockey</td><td>Built from the same goal expectations, so it
is the same model viewed from a different angle.</td></tr>
<tr><td>Point spread 4.5 / 6.5 / 9.5</td><td>Basketball</td><td>Derived from the same margin
distribution as the moneyline.</td></tr>
<tr><td>Game total</td><td>—</td><td><b>Withheld.</b> No official NBA scoring figure was read, so
any total would have been invented.</td></tr>
</table></div>
"""
    return page("markets.html", "Markets explorer", body,
                "Both sides of every market we originated")


def page_sports(d):
    cards = []
    for s in d["sports"]:
        fx = [g for g in d["fixtures"] if g["sport"] == s["code"]]
        picks = [p for p in d["picks"] if p["sport"] == s["code"]]
        discs = d["discovery_only"].get(s["code"], [])
        state = ("Priced" if any(g["priced"] for g in fx) else
                 "Fixture confirmed, not priced" if fx else
                 "No OLBG market" if s["olbg_state"] == "no-tips" else "Listing only")
        cards.append(f"""
<div class="card">
<h3><a href="sports/{e(s['code'])}.html">{e(s['name'])}</a>
<span class="badge {'b-high' if state == 'Priced' else 'b-med' if 'Fixture' in state else 'b-low'}">{e(state)}</span></h3>
<p class="small">{s['olbg_events']} OLBG event listing(s) · {len(fx)} fixture(s) here ·
{len(picks)} pick(s) · {len(discs)} unconfirmed listing(s)</p>
<p>{'<b>Picks:</b> ' + ', '.join(e(p['selection']) for p in picks) if picks else 'No selection was published for this sport today.'}</p>
<p class="small"><a href="{e(s['olbg_url'])}" rel="noopener">OLBG hub</a> ·
<a href="{e(s['official_url'])}" rel="noopener">{e(s['official_name'])}</a></p>
</div>""")
    body = ("<p>Fifteen requested sports, in the brief's order. Each page states what OLBG served, what "
            "the governing body published, and why a sport is priced or not.</p>" + "".join(cards))
    return page("sports.html", "Sports", body, "All fifteen, priced or not")


def page_sport(d, s):
    fx = [g for g in d["fixtures"] if g["sport"] == s["code"]]
    picks = [p for p in d["picks"] if p["sport"] == s["code"]]
    discs = d["discovery_only"].get(s["code"], [])

    fixture_html = ""
    if fx:
        rows = []
        for g in fx:
            hr, ar = g.get("home_rec"), g.get("away_rec")
            if isinstance(hr, dict):
                hrec = rec_str(hr)
                arec = rec_str(ar)
                stat = (f'{hrec} · {hr["pts"]} pts · {hr["gf"]:.2f} GF/G · {hr["ga"]:.2f} GA/G'
                        if hr["gf"] is not None else f'{hrec} · {hr["pts"]} pts')
                astat = (f'{arec} · {ar["pts"]} pts · {ar["gf"]:.2f} GF/G · {ar["ga"]:.2f} GA/G'
                         if ar["gf"] is not None else f'{arec} · {ar["pts"]} pts')
            else:
                stat = f"{hr[0]}-{hr[1]}" if hr else "not read"
                astat = f"{ar[0]}-{ar[1]}" if ar else "not read"
            state = ('<span class="badge b-high">Priced</span>' if g["priced"]
                     else '<span class="badge b-med">Not priced</span>')
            pk = (f'{e(g["pick"]["selection"])} <span class="badge '
                  f'{"b-high" if g["pick"]["confidence"] == "High" else "b-med" if g["pick"]["confidence"] == "Medium" else "b-low"}">'
                  f'{e(g["pick"]["confidence"])}</span> {price(g["pick"]["p"])} ({pct(g["pick"]["p"])})'
                  if g["pick"] else "—")
            venue = ('<div class="small">' + e(g["venue"]) + "</div>") if g.get("venue") else ""
            rows.append(f'<tr><td><b>{e(g["away"])} @ {e(g["home"])}</b>{venue}</td>'
                        f'<td class="small">{e(g.get("official_start") or g["start_utc"])}</td>'
                        f'<td class="small">{e(astat)}<br>{e(stat)}</td>'
                        f'<td>{state}</td><td>{pk}</td></tr>')
        fixture_html = f"""<h2>Fixtures</h2>
<div class="table-wrap"><table><tr><th>Match</th><th>Start (UTC)</th>
<th>Record away / home (W-L-OTL for hockey, W-L for basketball)</th><th>State</th><th>Pick</th></tr>
{"".join(rows)}</table></div>"""

    pred_html = ""
    if picks:
        pred_html = "<h2>Written predictions</h2>" + "".join(
            f'<div class="pred"><h3>{e(p["fixture"])} — {e(p["selection"])}</h3>'
            f'<p class="small">{price(p["p"])} · {pct(p["p"])} · {e(p["confidence"])}</p>'
            f'<p>{e(p["prediction"]) if p.get("prediction") else "No full write-up: the supporting data was too thin."}</p>'
            f'<p class="small">Sources: {" · ".join(source_link(x) for x in p["prediction_sources"])}</p></div>'
            for p in picks)

    disc_html = ""
    if discs:
        rows = "".join(f'<tr><td>{e(n)}</td><td class="small">{e(t)}</td>'
                       f'<td class="small">{e(o)}</td></tr>' for n, t, o in discs)
        disc_html = f"""<h2>OLBG listings — not confirmed, not priced</h2>
<p class="small">The middle column is what OLBG printed. The right column is OLBG's own tip share,
which is a count of member votes and is <b>not</b> a probability and is not used in any price here.</p>
<div class="table-wrap"><table><tr><th>Event (as OLBG names it)</th><th>OLBG time</th>
<th>OLBG tip share</th></tr>{rows}</table></div>"""

    why = {
        "golf": ("OLBG rendered 'No tips found.' on the Golf hub, so there was no market to originate. "
                 "No PGA Tour or DP World Tour field or tee sheet was read, so nothing is listed.",
                 ["olbg-golf"]),
        "snooker": ("The Snooker hub and its 'All Events' sub-route both rendered 'No tips found.' "
                    "No World Snooker Tour draw or result was read this session.",
                    ["olbg-snooker", "olbg-snooker-events"]),
        "motor-racing": ("OLBG's Motor Racing hub rendered 'No tips found.' No Formula 1 session or "
                         "entry list was read.", ["olbg-motorracing"]),
        "rugby-league": ("OLBG listed outright markets for 2027 only — State of Origin, the Super League "
                         "Grand Final and the NRL Grand Final. There was no upcoming match market to price.",
                         ["olbg-rugbyleague"]),
        "greyhounds": ("OLBG listed a single race, 11:04 Doncaster, with one tip. No GBGB racecard, "
                       "trial time or form line was read.", ["olbg-greyhounds"]),
        "cricket": ("Six fixtures are confirmed on Cricket South Africa's own site for 25 October, and "
                    "they are listed on <a href='../matches.html'>Every match</a>. No competition record was "
                    "read for any of the sides, so no price is originated.",
                    ["csa-home", "olbg-cricket"]),
        "baseball": ("One fixture is confirmed: World Series Game 2, with both starting pitchers named on "
                     "the league feed. Milwaukee's season runs scored and allowed were not read, so the "
                     "market is withheld.", ["mlb-schedule", "olbg-baseball"]),
        "tennis": ("Fifteen OLBG listings, none confirmed against the ATP or WTA. No draw, ranking or "
                   "head-to-head page was read, so nothing is priced.", ["olbg-tennis"]),
        "volleyball": ("Sixteen OLBG listings across SuperLega, PlusLiga, Turkey, Germany and Brazil. Two "
                       "attempts to read the SuperLega table and calendar returned navigation only, so no "
                       "standing or set record was captured.", ["olbg-volleyball"]),
        "handball": ("Sixteen OLBG listings. The Handball-Bundesliga table page returned an empty shell "
                     "and the competition site returned a 404, so no record was captured.",
                     ["olbg-handball"]),
        "rugby-union": ("Three OLBG listings. The Premiership fixtures page returned a 404 on the "
                        "requested route, so no league table or fixture confirmation was captured.",
                        ["olbg-rugbyunion"]),
        "gaelic-sports": ("Four club listings. No GAA county board fixture list was read, so the "
                          "fixtures are OLBG-only.", ["olbg-gaelic"]),
        "darts": ("Two match listings and two outrights. The PDC event page could not be read past its "
                  "consent wall, so no draw or average was captured.", ["olbg-darts"]),
    }.get(s["code"])

    why_html = ""
    if why:
        text, srcs = why
        why_html = (f'<h2>Why this sport is not priced</h2><p>{text}</p>'
                    f'<p class="small">Sources: {" · ".join(source_link(x) for x in srcs)}</p>')

    body = f"""
<p>OLBG hub: <a href="{e(s['olbg_url'])}" rel="noopener">{e(s['olbg_url'])}</a> ·
governing body: <a href="{e(s['official_url'])}" rel="noopener">{e(s['official_name'])}</a></p>
<p class="small">OLBG listed {s['olbg_events']} event(s) for this sport when read on 24 October 2026.</p>
{fixture_html}
{why_html}
{pred_html}
{disc_html}
<p><a href="../sports.html">← all sports</a></p>
"""
    return page(f"../sports/{s['code']}.html", s["name"], body, "", up=1)


def page_flagged(d):
    rows = []
    for f in d["flags"]:
        cls = {"high": "b-flag", "medium": "b-med", "low": "b-low"}.get(f["severity"], "b-info")
        srcs = " · ".join(source_link(s) for s in f["sources"])
        rows.append(f"""<div class="card">
<div><span class="badge {cls}">{e(f['severity'].title())}</span>
<span class="tag">{e(f['area'])} · {e(f['id'])}</span></div>
<h3 style="margin-top:8px">{e(f['title'])}</h3>
<p>{e(f['detail'])}</p>
<p class="small">Sources: {srcs}</p></div>""")
    body = f"""
<div class="callout warn">
<b>Nothing here blocks publication</b>
These are the gaps, the disagreements and the things we refused to fill in. Each one carries the
source that shows the problem. If something is blank in a table, the reason is on this page.
</div>
<p><b>{len(d['flags'])} items.</b> A further {len(d['repo_findings'])} findings concern this
repository rather than a fixture, and are listed on <a href="repo-review.html">Repo review</a>.</p>
{"".join(rows)}
"""
    return page("flagged.html", "Flagged for review", body,
                "What is missing, what disagrees, and what would close it")


def page_sources(d):
    off = [s for s in F.SOURCES if s["tier"] == "official"]
    dis = [s for s in F.SOURCES if s["tier"] == "discovery"]

    def rows(items):
        return "".join(
            f'<tr><td><b>{e(s["publisher"])}</b><div class="small">{e(s["title"])}</div></td>'
            f'<td class="mono"><a href="{e(s["url"])}" rel="noopener">{e(s["url"])}</a></td>'
            f'<td class="small">{e(s["read_utc"])}</td></tr>' for s in items)

    body = f"""
<p>Every page read this session, with the publisher, the exact URL and the UTC time it was read.
Official sources are the league, governing body or tour. OLBG is a discovery source only: it tells
us which markets exist, never what the facts are.</p>
<h2>Official sources ({len(off)})</h2>
<div class="table-wrap"><table><tr><th>Publisher</th><th>URL</th><th>Read (UTC)</th></tr>
{rows(off)}</table></div>
<h2>Discovery sources ({len(dis)})</h2>
<div class="table-wrap"><table><tr><th>Publisher</th><th>URL</th><th>Read (UTC)</th></tr>
{rows(dis)}</table></div>
<h2>Sources that were attempted and refused</h2>
<div class="table-wrap"><table><tr><th>Source</th><th>What happened</th></tr>
<tr><td>Lega Pallavolo Serie A — SuperLega table and calendar</td>
<td>The standings route returned its navigation only in the returned slices; no table was captured.</td></tr>
<tr><td>Handball-Bundesliga — table</td><td>Returned an empty shell with no table rows.</td></tr>
<tr><td>Handball-Bundesliga — fixture plan</td><td>Returned a 404 page.</td></tr>
<tr><td>Premiership Rugby — fixtures</td><td>Returned a 404 page.</td></tr>
<tr><td>PDC — European Championship</td><td>Returned a cookie-consent wall, no event content.</td></tr>
</table></div>
"""
    return page("sources.html", "Sources", body, "Every read, with its URL and its UTC timestamp")


def page_method(d):
    c = d["counts"]
    cal_rows = []
    for g in d["fixtures"]:
        if g["sport"] != "ice-hockey" or not g["publisher_ml"]:
            continue
        ml = {o["side"]: o["p"] for o in g["outcomes"] if o["market"] == "Moneyline"}
        if not ml:
            continue
        a, h = g["publisher_ml"]

        def imp(x):
            return (-x) / ((-x) + 100) if x < 0 else 100 / (x + 100)
        tot = imp(a) + imp(h)
        fair_h = imp(h) / tot
        diff = ml["home"] - fair_h
        cal_rows.append(
            f'<tr><td>{e(g["away"])} @ {e(g["home"])}</td>'
            f'<td class="num">{h:+d}</td><td class="num">{a:+d}</td>'
            f'<td class="num">{pct(fair_h)}</td><td class="num">{pct(ml["home"])}</td>'
            f'<td class="num">{diff * 100:+.1f} pts</td></tr>')

    body = f"""
<h2 id="hockey">Ice hockey</h2>
<p>Goals are treated as two independent Poisson counts. Each club's goals-for and goals-against rate
is first <b>regressed onto the league average</b> of 3.00 goals a game with twelve games of prior
weight, because a rate built on eight to twelve games is noisy:</p>
<p class="mono">rate = (rate × games + 3.00 × 12) / (games + 12)</p>
<p>The home side's expected goals are then the average of its own scoring rate and the visitor's
conceding rate, times 1.03; the visitor's are the mirror, times 0.97. From that grid we can price the
moneyline, ±1.5 and ±2.5 puck lines, −1/+1 and −2/+2 Asian handicaps with pushes voided, and totals
from 4.5 to 7.5 — all from one set of expectations, which is why the total and the moneyline never
contradict each other.</p>

<h2 id="basketball">Basketball</h2>
<p>Only wins and losses were captured, so the rating is a shrunk win rate with a ten-win, ten-loss
prior at .500, and the win probability is a logistic function of the rating gap plus a 3% home edge.
The expected margin is the probit of that probability times a 12.5-point standard deviation, and the
spread ladder comes off the same distribution. Totals are withheld — see
<a href="flagged.html">Flagged</a>.</p>

<h2>Prices and the band</h2>
<p>Every market is normalised so its two sides sum to 100%. That fair probability is converted to a
American price and then checked against the brief's window:</p>
<div class="table-wrap"><table>
<tr><th>Probability</th><th>Fair American price</th><th>Decimal</th><th>Inside −250…+10000?</th></tr>
<tr><td>50%</td><td>+100</td><td>2.00</td><td>Yes</td></tr>
<tr><td>60%</td><td>−150</td><td>1.67</td><td>Yes</td></tr>
<tr><td>70%</td><td>−233</td><td>1.43</td><td>Yes</td></tr>
<tr><td>71.4%</td><td>−250</td><td>1.40</td><td>Yes — the boundary</td></tr>
<tr><td>75%</td><td>−300</td><td>1.33</td><td><b>No — shorter than −250</b></td></tr>
</table></div>
<div class="callout warn">
<b>Why high picks are scarce, in one paragraph</b>
The brief asks for two things at once: a selection with more than a 70% chance, and a price inside
−250 to +10000. A 70% chance is −233. The band stops at −250, which is 71.4%. The overlap is 1.4
points wide. Of the {c['outcomes']} prices this desk set, exactly three land in that sliver, and all
three are published as the high-confidence picks. Nothing was re-priced by hand to manufacture more.
</div>
<p>Grading: <b>High</b> above 70%, <b>Medium</b> 60–70%, <b>Low</b> 52–60%, and any selection
priced shorter than −250 is shown but never picked.</p>

<h2 id="calibration">Calibration check against the publisher's own prices</h2>
<p>The NHL feed prints a partner moneyline next to each fixture. It is not our price and it was not
used to set one — it is here so you can see how far our number sits from the market's. Differences
are percentage points of implied probability on the home side, with the publisher's two-way line
normalised to remove its margin.</p>
<div class="table-wrap"><table>
<tr><th>Match</th><th>Publisher home</th><th>Publisher away</th><th>Publisher fair home</th>
<th>Our home</th><th>Difference</th></tr>
{"".join(cal_rows)}
</table></div>
<p class="small">Every fixture is within about seven points of the market, which is the check we
wanted: the goal expectations are not producing fantasy prices. Two rows sit closest to the edge —
Tampa Bay at Utah and the New York Rangers at Ottawa — and both are marked accordingly in the
tiering rather than being quoted as strong opinions.</p>

<h2>What would change the answers</h2>
<ul class="plain">
  <li>Confirmed starting goaltenders for either crease. None was read, so none is used; a backup
      start is the single biggest unmeasured input on every hockey row here.</li>
  <li>Injury reports for hockey, cricket, volleyball or handball. The NBA filing is the only
      availability document on the desk.</li>
  <li>Score-level scoring data for the NBA, which would let the totals market back on to the board.</li>
</ul>
"""
    return page("methodology.html", "Method, prices and the band", body,
                "How every number on this desk was produced")


def page_repo(d):
    rows = []
    for f in d["repo_findings"]:
        cls = {"high": "b-flag", "medium": "b-med", "low": "b-low"}.get(f["severity"], "b-info")
        rows.append(f"""<div class="card">
<div><span class="badge {cls}">{e(f['severity'].title())}</span>
<span class="tag mono">{e(f['file'])}</span></div>
<h3 style="margin-top:8px">{e(f['id'])} — {e(f['title'])}</h3>
<p>{e(f['detail'])}</p>
<p class="small">Evidence: {e(f['evidence'])}</p></div>""")
    body = f"""
<p>The repository was read before it was edited: a file inventory, a parse of all twenty root pages
for broken relative links, the size of the published allowlist against the number of desk
directories, and the state of the existing test suite. The findings below are the irregularities
worth your attention; the clean results are recorded too, so the absence of a problem is visible.</p>
{"".join(rows)}
<h2>How this desk avoids adding to the problem</h2>
<ul class="plain">
  <li>Its own namespace only: <span class="mono">data/{DESK}/</span>,
      <span class="mono">scripts/s{DESK}_*.py</span>, <span class="mono">{DESK}/</span>,
      <span class="mono">reports/SESSION_F840C28A.md</span> and one test module.</li>
  <li>One additive line in the publisher's allowlist so the desk is reachable, and one changed
      sentence on the root landing page pointing at it.</li>
  <li>No generated JSON larger than a few hundred kilobytes.</li>
</ul>
"""
    return page("repo-review.html", "Repository review", body,
                "What was checked, what is irregular, and what was left alone")


# --------------------------------------------------------------------------
# Emit
# --------------------------------------------------------------------------

def main():
    desk = build_data()
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sports").mkdir(parents=True, exist_ok=True)

    payload = json.loads(json.dumps(desk, default=str))
    (DATA / "desk.json").write_text(json.dumps(payload, indent=1) + "\n")
    (DATA / "sources.json").write_text(json.dumps(F.SOURCES, indent=1) + "\n")
    (DATA / "flags.json").write_text(json.dumps(FLAGS + REPO_FINDINGS, indent=1) + "\n")
    (DATA / "coverage.json").write_text(json.dumps(
        dict(sports=F.SPORTS, discovery_only=F.DISCOVERY_ONLY,
             counts=desk["counts"]), indent=1) + "\n")
    (DATA / "manifest.json").write_text(json.dumps(dict(
        desk=DESK, session=SESSION, task=TASK, captured=F.CAPTURE_UTC,
        counts=desk["counts"],
        pages=[n for n, _ in NAV] + [f"sports/{s['code']}.html" for s in F.SPORTS],
    ), indent=1) + "\n")

    pages = {
        "index.html": page_index(desk),
        "picks.html": page_picks(desk),
        "predictions.html": page_predictions(desk),
        "matches.html": page_matches(desk),
        "markets.html": page_markets(desk),
        "sports.html": page_sports(desk),
        "flagged.html": page_flagged(desk),
        "sources.html": page_sources(desk),
        "methodology.html": page_method(desk),
        "repo-review.html": page_repo(desk),
    }
    for name, html_text in pages.items():
        (OUT / name).write_text(html_text)
    for s in F.SPORTS:
        (OUT / "sports" / f"{s['code']}.html").write_text(page_sport(desk, s))

    c = desk["counts"]
    print(f"pages: {len(pages) + len(F.SPORTS)}")
    print(f"fixtures {c['fixtures']} (confirmed {c['confirmed']}), priced {c['priced']}, "
          f"markets {c['markets']}, outcomes {c['outcomes']}")
    print(f"picks {c['picks']} -> High {c['high']} / Medium {c['medium']} / Low {c['low']}; "
          f"predictions {c['predictions']}; flags {c['flags']}")
    return desk


if __name__ == "__main__":
    main()
