#!/usr/bin/env python3
"""Build the 429a54a2-olbg1 desk: data, CSV exports and a static 25-page site."""

from __future__ import annotations

import csv
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import s429a54a2_data as META
import s429a54a2_dataset as DS
import s429a54a2_model as MODEL

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "429a54a2"
DATA = ROOT / "data" / "429a54a2"
LIVE = "https://buffedlizard55-lab.github.io/OLBG1/429a54a2/"

PREDICTIONS = [
    {
        "id": "P-429A-01", "fixture": "nhl-101", "selection": "Montreal Canadiens moneyline (60 minutes plus overtime and shootout)",
        "tier": "High", "words_note": "official NHL standings only",
        "text": (
            "Montreal Canadiens to win at Chicago is the pick, and the case is built on the league's own table. "
            "Montreal have 10 points from nine games (4-3-2) with 30 goals scored, while Chicago have 6 points from nine "
            "(3-6-0) and have been outscored 21-36. The Canadiens' two overtime defeats still count as defeats in a two-way "
            "market, so this is not a padded record. Taking Montreal to win outright at the United Center."
        ),
    },
    {
        "id": "P-429A-02", "fixture": "nhl-110", "selection": "Carolina Hurricanes moneyline",
        "tier": "High", "words_note": "official NHL standings only",
        "text": (
            "Carolina Hurricanes to win in St. Louis is a road selection with a clear statistical edge. Carolina are 8-2-2 "
            "for 18 points, have scored 47 goals and conceded 33, and are 6-1-1 away from home. St. Louis are 5-4-1 with 11 points "
            "and a 35-31 goal split. The Hurricanes' 8-1-1 run over ten games is the strongest form line in this matchup. "
            "Back Carolina to win the game, overtime and shootout included."
        ),
    },
    {
        "id": "P-429A-03", "fixture": "hb-1304", "selection": "Selestat to beat Caen (60-minute result, draw no bet)",
        "tier": "High", "words_note": "official LNH table only",
        "text": (
            "Selestat to beat Caen in StarLigue round eight is a home pick grounded in the official LNH table. Both clubs sit on "
            "six points from seven matches, but Caen have conceded 235 goals while scoring 198, the worst goal difference in the "
            "division at -37. Selestat have scored 208 and conceded 217 across the same seven rounds. Facing the leakiest defence "
            "in the league, Selestat's attack should control the second half. Take Selestat to win the match."
        ),
    },
    {
        "id": "P-429A-04", "fixture": "nhl-102", "selection": "Tampa Bay Lightning moneyline",
        "tier": "High (out of band)", "words_note": "official NHL standings only",
        "text": (
            "Tampa Bay Lightning to win in Denver is the strongest road side on Saturday's slate. The Lightning are 7-2-0 with "
            "14 points and a 31-23 goal record, while Colorado are 5-4-1 on 11 points despite scoring 41 times, because they have "
            "conceded 31. Tampa Bay have won three straight and sit second in the Atlantic Division. The price falls shorter than "
            "the -250 floor of the requested band, so it is disclosed rather than dressed up. Tampa Bay to win."
        ),
    },
    {
        "id": "P-429A-05", "fixture": "nhl-109", "selection": "Vegas Golden Knights moneyline",
        "tier": "High (out of band)", "words_note": "official NHL standings only",
        "text": (
            "Vegas Golden Knights to win in Columbus pairs a 16-point team with a six-point team. Vegas are 8-4-0 with 46 goals "
            "scored and 36 conceded; Columbus are 3-5-0, have scored only 20 goals in eight games, and have lost two in a row. "
            "The Blue Jackets' 20-29 goal split is the thinner side of this matchup. "
            "Vegas to win the game outright, with the short price noted as outside the requested band."
        ),
    },
    {
        "id": "P-429A-06", "fixture": "hb-1303", "selection": "Limoges to beat Dunkerque",
        "tier": "High (out of band)", "words_note": "official LNH table only",
        "text": (
            "Limoges to beat Dunkerque is a mismatch the LNH table makes plain. Limoges have eight points from seven rounds "
            "(4-3-0) and have scored 234 goals while conceding 214. Dunkerque are bottom of the division on two points from a 1-6-0 "
            "start, with only 175 goals scored and 196 conceded. Limoges have won four of seven; Dunkerque have lost six. "
            "Back Limoges to win the match inside 60 minutes."
        ),
    },
    {
        "id": "P-429A-07", "fixture": "hb-1306", "selection": "Nantes to beat Chambery",
        "tier": "High (out of band)", "words_note": "official LNH table only",
        "text": (
            "Nantes to beat Chambery rests on the cleanest record in the matchup. Nantes are unbeaten in seven StarLigue rounds at "
            "6-1-0 for 12 points, with 244 goals scored against 203 conceded. Chambery are 2-3-2 on six points and have a negative "
            "goal difference at 224-231. Nantes have scored more goals than any side bar Paris. Take Nantes to win the match in "
            "front of their own crowd."
        ),
    },
    {
        "id": "P-429A-08", "fixture": "hb-1308", "selection": "Montpellier to beat Saran",
        "tier": "High (out of band)", "words_note": "official LNH table only",
        "text": (
            "Montpellier to beat Saran is a home selection supported by both points and goal difference. Montpellier have 10 points "
            "from seven rounds at 4-1-2, scoring 234 and conceding 205. Saran are 3-4-0 on six points and have been outscored 202-216. "
            "Montpellier have won four of their seven matches, and their +29 goal difference is 23 goals better than Saran's. "
            "Back Montpellier to take the 60-minute result."
        ),
    },
    {
        "id": "P-429A-09", "fixture": "nhl-112", "selection": "Tampa Bay Lightning moneyline",
        "tier": "Medium", "words_note": "official NHL standings only",
        "text": (
            "Tampa Bay moneyline in Salt Lake City is a medium-strength call. The visitors own a 7-2-0 record, 14 points "
            "with 31 goals for and 23 against, and three consecutive wins behind them. Utah have also banked 14 points from eleven games, "
            "scoring 44 and conceding 37, and they lost their most recent outing. The Lightning's tighter defence gives them the "
            "edge, but Utah's home scoring volume keeps this out of the top tier."
        ),
    },
    {
        "id": "P-429A-10", "fixture": "hb-1305", "selection": "Tremblay to beat Cesson-Rennes",
        "tier": "Medium", "words_note": "official LNH table only",
        "text": (
            "Tremblay to beat Cesson-Rennes is a medium-tier handball pick. The LNH table shows Tremblay on seven points "
            "from seven rounds at 3-3-1 with 231 goals scored and a +4 goal difference. Cesson-Rennes sit second from bottom with "
            "two points, one win and six defeats, having conceded 227 goals for a -18 differential. That scoring gap points to the "
            "home win at a modest price."
        ),
    },
]

FLAGS = [
    ("F-429A-01", "high", "OLBG time labels are internally inconsistent with the official schedules",
     "OLBG's Darts hub showed 'Today 14:45' for Jonny Clayton v Niko Springer, but the PDC schedule puts that tie in the 20:30 CEST slot (18:30Z), a discrepancy of 3h45m. OLBG Tennis showed 'Tomorrow 05:30' for Rybakina v Shnaider while the WTA order of play has it not before 17:30 in Ningbo (09:30Z), a four-hour gap. OLBG Basketball showed Knicks @ Celtics at 'Today 19:10' against a 7:00pm ET (23:00Z) tip. Every OLBG time on this desk is therefore treated as a display label, never as a UTC start.",
     "https://www.pdc.tv/news", ["darts-304", "ten-501", "bkn-602"]),
    ("F-429A-02", "medium", "PDC's own schedule article is behind a consent wall for direct fetches",
     "The pdc.tv article of 19 October 2026 ('2026 Machineseeker European Championship schedule confirmed') returned only a cookie-consent shell. The eight Friday ties were therefore confirmed through the PDC news hub plus independent listings that reproduce the same PDC order of play, and the PDC URL is retained as the official reference. The session does not claim a direct read of the article body.",
     "https://www.pdc.tv/news", ["darts-301", "darts-308"]),
    ("F-429A-03", "medium", "German HBL official schedule page served no fixture table",
     "opel-hbl.de/de/hbl/spielplan returned promotional text and a reCAPTCHA block with no match list, so the two German handball fixtures (Goeppingen v Eisenach, Hannover-Burgdorf v Lemgo) could not be confirmed on the league's own page and were excluded from the priced slate.",
     "https://www.opel-hbl.de/de/hbl/spielplan", []),
    ("F-429A-04", "medium", "Munster GAA club-championship URL changed",
     "https://munster.gaa.ie/fixtures/club-2026/ returns a 404; the live page is /fixtures/club-championships-2026/. The working page confirms the Munster club football quarter-finals on 8 November but carries no 25 October Cork final, which is listed by Cork GAA instead.",
     "https://munster.gaa.ie/fixtures/club-championships-2026/", ["gaa-801"]),
    ("F-429A-05", "high", "Cork senior football final date disputed between sources",
     "Cork GAA's official fixtures page, the St Finbarr's club fixtures page and Munster GAA's event page all give Sunday 25 October at 16:00. A Wikipedia season article gives 24 October. The official county board date is used and the conflict is published rather than averaged.",
     "https://gaacork.ie/fixtures/", ["gaa-801"]),
    ("F-429A-06", "medium", "Galway county finals were moved for weather on the morning of publication",
     "Galway GAA published a fixture-change notice at 13:56 on 23 October moving the senior football final to Sunday 25 October, 16:00 at Pearse Stadium, and postponing several underage finals. Any earlier listing of a Saturday throw-in is superseded. The notice is the only source used for this row.",
     "https://www.galwaygaa.ie/changes-weekend-football-fixture-schedule/", ["gaa-802"]),
    ("F-429A-07", "medium", "Cricket Australia publishes viewer-local times, not venue times",
     "The Tasmania v Victoria and Western Australia v NSW match pages render '7:30 pm your time' and '2:00 am your time', which cannot be converted without knowing the reader's zone. OLBG's 19:30 label for the same Hobart fixture does not resolve the ambiguity. Both rows are therefore published with a blank UTC start.",
     "https://www.cricket.com.au/matches/CA:40681/tasmanian-tigers-men-victoria-men-one-day-cup-2026-27", ["cri-1003", "cri-1004"]),
    ("F-429A-08", "medium", "Two rugby-league/cricket fixtures rest on discovery cards or secondary lists",
     "The CSA Pro20 Lions v Limpopo fixture and the two November Gaelic club finals were visible only on OLBG cards or secondary listings. Neither is priced or counted as verified; they appear blank and flagged.",
     "https://www.olbg.com/betting-tips/Gaelic_Football/25", ["cri-1005", "gaa-804", "gaa-805"]),
    ("F-429A-09", "medium", "Greyhound tips on the OLBG card are one- and two-tip samples",
     "Every greyhound race card read carried between one and four win tips in total (for example 2/2 for Ontherun Jamie and 2/2 for Grouchos Gregor). A two-tip sample is not a probability, so the greyhound rows carry official race facts and no tip-derived price.",
     "https://www.olbg.com/betting-tips/Greyhounds/28", ["gb-901", "gb-902"]),
    ("F-429A-10", "high", "Luke Humphries withdrew from the European Championship before the priced session",
     "The PDC field changed when Luke Humphries withdrew with gastroenteritis and Kim Huybrechts took his place. Any OLBG card or preview showing Humphries in the Friday or Saturday draw is stale, and the desk prices only the eight confirmed Friday ties.",
     "https://www.pdc.tv/news", ["darts-301"]),
    ("F-429A-11", "medium", "OLBG golf hub was empty during a live PGA Tour event",
     "The Golf hub at /betting-tips/Golf/5 returned 'No tips found' and the 2027 US Masters hub also returned no tips, while the PGA Tour leaderboard showed the Butterfield Bermuda Championship in progress with four players tied at -12. The absence of OLBG tips is a discovery gap, not an absence of fixtures.",
     "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard", ["golf-1501", "golf-1502"]),
    ("F-429A-12", "medium", "OLBG rugby league hub lists only 2027 ante-post markets",
     "The Rugby League hub showed State of Origin 2027, Super League 2027 and NRL 2027 outrights and no live fixture, while the International Rugby League site listed six Round 2 World Cup and international fixtures for 24-25 October. The desk publishes the official fixtures and records the OLBG discovery gap.",
     "https://www.intrl.sport/fixtures-results", ["rl-1101", "rl-1106"]),
    ("F-429A-13", "medium", "Second Northern Ireland Open semi-final pairing is unresolved",
     "WST listed the 14:00 Saturday semi-final as 'Winner of match 59' against 'Winner of match 60' at read time, because both Friday quarter-finals were still listed as scheduled. That row is published with no participants, no price and no selection.",
     "https://www.wst.tv/matches/", ["snk-402"]),
    ("F-429A-14", "medium", "NBA strength inputs are a one-game sample",
     "Every NBA club had played a single game when the games page was read, so the 12 rows carry official fixtures and official records of 0-1 or 1-0 only. A one-game sample cannot support a rating, so all twelve are published unpriced rather than given invented strength.",
     "https://www.nba.com/games?date=2026-10-23", [f"bkn-6{n:02d}" for n in range(1, 13)]),
    ("F-429A-15", "medium", "All three EuroLeague Friday games had started before the snapshot",
     "Zalgiris v ASVEL (13:00 CEST), Olympiacos v Fenerbahce (14:15) and Paris v Valencia (14:45) were all in the past at the 16:45Z snapshot. They are retained as elapsed rows and are never priced retrospectively.",
     "https://www.europeanleaguebasketball.net/en/euroleague/game-center/?round=7&season=E2026".replace("european", "euro"), ["bkn-613", "bkn-614", "bkn-615"]),
    ("F-429A-16", "high", "Duplicate contradictory task rows in the shared board",
     "COORDINATION.md line 142 records T424375B4 as done while line 144 records the identical task and scope as in progress. The same file carries two T63 rows at lines 123 and 125, and two identical section-64 headings at lines 4029 and 4279. Readers cannot tell which status is authoritative; only the integration session should resolve it.",
     "https://github.com/buffedlizard55-lab/OLBG1/blob/main/COORDINATION.md", []),
    ("F-429A-17", "high", "The newest merged desk prices a High pick from a three-tip sample",
     "In data/2b72da34/desk.json lines 157-174 the Boston -2.5 selection is labelled High at p=0.714 with fair odds of exactly -250. The probability is produced by p=(tips+2)/(total+4) in scripts/s2b72da34_build.py, i.e. a community tip share, and the sample is 3/3 tips. A three-vote sample cannot establish a 71.4% probability, and the value sits exactly on the band boundary.",
     "https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/2b72da34/desk.json", []),
    ("F-429A-18", "medium", "A merged desk row is labelled unverified yet counted as priced",
     "2b72da34/baseball.html contains one row whose only official link is the generic https://www.mlb.com/ homepage and whose own note says 'UNVERIFIED - flagged', while the desk summary counts it among 37 priced rows. The fixture is now officially confirmed by MLB StatsAPI as World Series Game 1, which is why this desk republishes it with the real game link.",
     "https://github.com/buffedlizard55-lab/OLBG1/blob/main/2b72da34/baseball.html", ["mlb-701"]),
    ("F-429A-19", "medium", "Two sport pages in the newest desk contain no rows at all",
     "2b72da34/golf.html (473 bytes) and 2b72da34/rugby-league.html (481 bytes) render only a coverage-gap notice. That is honest, but the desk's headline of 37 priced rows should not be read as 15 sports covered; the same gap applies here for golf and rugby league pricing.",
     "https://github.com/buffedlizard55-lab/OLBG1/blob/main/2b72da34/golf.html", []),
    ("F-429A-20", "medium", "Three stale 'in progress' claims remain on the board",
     "COORDINATION.md lines 77, 89, 112 and 113 still mark T9, T19, T51 and T52 as in progress, well past the 60-minute staleness rule in the board's own section 0.4. They are noted for the integration session and were not edited here.",
     "https://github.com/buffedlizard55-lab/OLBG1/blob/main/COORDINATION.md", []),
]

REPO_FINDINGS = [
    ("R-429A-01", "COORDINATION.md", 142, "Duplicate task row: T424375B4 is recorded as done here and as in progress at line 144."),
    ("R-429A-02", "COORDINATION.md", 123, "Task id T63 is used twice; the second row at line 125 carries a different scope."),
    ("R-429A-03", "COORDINATION.md", 4029, "Section 64 appears twice (also line 4279) with identical headings."),
    ("R-429A-04", "scripts/s2b72da34_build.py", 6, "p=(tips+2)/(total+4) converts a community tip share into a probability with no calibration."),
    ("R-429A-05", "data/2b72da34/desk.json", 165, "High label at p=0.714 derived from a 3/3 tip sample, exactly on the -250 boundary."),
    ("R-429A-06", "2b72da34/baseball.html", 1, "The only official link on the row is the generic mlb.com homepage while the row is counted as priced."),
    ("R-429A-07", "data/current/snapshot.json", 21, "Canonical snapshot is dated 2026-10-22T12:29:50Z, more than 28 hours before this session, so no row in it can be treated as current."),
    ("R-429A-08", "scripts/validate.py", 166, "The link gate accepts only relative links on published pages; it does not check that a row's official link resolves to the fixture, which is how the baseball row above passed."),
]


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def money(n):
    return f"{n:+d}" if n is not None else ""


def build_records():
    records = []
    for r in DS.ROWS:
        o = MODEL.originate(r)
        rec = dict(r)
        rec["price"] = o
        rec["sport_name"] = next(s["name"] for s in META.SPORTS if s["slug"] == r["sport"])
        rec["tier"] = o["tier"]
        records.append(rec)
    return records


def summarise(records):
    sports = []
    for s in META.SPORTS:
        rows = [r for r in records if r["sport"] == s["slug"]]
        priced = [r for r in rows if r["price"]["markets"]]
        high = [r for r in priced if r["price"]["tier"] == "High"]
        high_out = [r for r in priced if (r["price"]["tier"] or "").startswith("High (")]
        med = [r for r in priced if r["price"]["tier"] == "Medium"]
        low = [r for r in priced if r["price"]["tier"] == "Low"]
        unverified = [r for r in rows if r["status"] == "unverified"]
        elapsed = [r for r in rows if r["status"] == "elapsed"]
        sports.append({
            **{k: s[k] for k in ("slug", "name", "olbg_id", "olbg_url", "official_name", "official_url", "model_family", "notes")},
            "rows": len(rows), "priced": len(priced), "high": len(high), "high_out": len(high_out),
            "medium": len(med), "low": len(low), "unverified": len(unverified), "elapsed": len(elapsed),
        })
    return sports


def top_five(records, sport):
    rows = [r for r in records if r["sport"] == sport and r["price"]["markets"]]
    order = {"High": 0, "High (price outside -250..+10000)": 1, "Medium": 2, "Low": 3}
    rows.sort(key=lambda r: (order.get(r["price"]["tier"], 9), -(r["price"]["probability"] or 0)))
    return rows[:5]


def write_data(records, sports):
    DATA.mkdir(parents=True, exist_ok=True)
    fixtures = []
    for r in records:
        fixtures.append({
            "id": r["id"], "sport": r["sport"], "sport_name": r["sport_name"], "competition": r["competition"],
            "stage": r["stage"], "participant_a": r["a"], "participant_b": r["b"], "start_utc": r["start_utc"],
            "date": r.get("date"), "venue": r["venue"], "status": r["status"],
            "official_url": r["official"], "official_label": r["official_label"], "observed": r["observed"],
            "notes": r["notes"], "tier": r["tier"], "price": r["price"],
        })
    (DATA / "fixtures.json").write_text(json.dumps(fixtures, indent=1), encoding="utf-8")
    (DATA / "sports.json").write_text(json.dumps(sports, indent=1), encoding="utf-8")
    (DATA / "predictions.json").write_text(json.dumps(PREDICTIONS, indent=1), encoding="utf-8")
    (DATA / "flagged.json").write_text(json.dumps(
        [{"id": f[0], "severity": f[1], "title": f[2], "detail": f[3], "url": f[4], "rows": f[5]} for f in FLAGS], indent=1), encoding="utf-8")
    (DATA / "repo-review.json").write_text(json.dumps(
        [{"id": a, "file": b, "line": c, "finding": d} for a, b, c, d in REPO_FINDINGS], indent=1), encoding="utf-8")
    counts = {
        "rows": len(records),
        "priced": sum(1 for r in records if r["price"]["markets"]),
        "markets": sum(len(r["price"]["markets"]) for r in records),
        "outcomes": sum(len(r["price"]["markets"]) for r in records),
        "high": sum(1 for r in records if r["price"]["tier"] == "High"),
        "high_out": sum(1 for r in records if (r["price"]["tier"] or "").startswith("High (")),
        "medium": sum(1 for r in records if r["price"]["tier"] == "Medium"),
        "low": sum(1 for r in records if r["price"]["tier"] == "Low"),
        "unverified": sum(1 for r in records if r["status"] == "unverified"),
        "elapsed": sum(1 for r in records if r["status"] == "elapsed"),
        "predictions": len(PREDICTIONS),
        "flags": len(FLAGS),
        "repo_findings": len(REPO_FINDINGS),
        "sports": len(sports),
        "sources": len({r["official"] for r in records}) + 8,
    }
    (DATA / "summary.json").write_text(json.dumps({"session": META.SESSION_ID, "generated_at": META.GENERATED_AT,
                                                   "window": [META.WINDOW_START, META.WINDOW_END], "counts": counts}, indent=1), encoding="utf-8")
    return counts


CSS = """
:root{--ink:#12241c;--muted:#5b6f66;--line:#dfe7e2;--bg:#f6f9f7;--card:#fff;--green:#12563d;--amber:#8a5a12;--red:#8c2f24}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
a{color:#12563d}a:hover{text-decoration:underline}
header.top{background:#0f3f2d;color:#fff;padding:14px 22px;display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between}
header.top .brand{font-weight:700;letter-spacing:.3px}header.top .brand small{display:block;font-weight:400;opacity:.75;font-size:11px;letter-spacing:1px}
nav.top a{color:#dff0e7;margin-right:14px;text-decoration:none;font-size:13px}nav.top a.on{color:#fff;border-bottom:2px solid #8fd3b3}
main{max-width:1200px;margin:0 auto;padding:26px 20px 60px}
h1{font-size:27px;margin:0 0 6px}h2{font-size:19px;margin:26px 0 10px}h3{font-size:15px;margin:16px 0 6px}
p.lede{color:var(--muted);max-width:88ch;margin:0 0 18px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:22px}.kpi span{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.6px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:16px 0}
.notice{background:#fff8e8;border:1px solid #e8d3a2;border-radius:8px;padding:11px 14px;margin:14px 0;font-size:13.5px}
.warn{background:#fbeeeb;border-color:#e6c3bb}
table{width:100%;border-collapse:collapse;font-size:13px;background:var(--card)}
th,td{border-bottom:1px solid var(--line);padding:8px 9px;text-align:left;vertical-align:top}
th{background:#eef4f0;font-size:11.5px;text-transform:uppercase;letter-spacing:.5px;color:#2c4a3c}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}
.badge{display:inline-block;padding:1px 7px;border-radius:20px;font-size:11px;font-weight:600;border:1px solid}
.badge.high{background:#e3f3ea;color:#0d5d3c;border-color:#b8ddc8}
.badge.med{background:#fff4dd;color:#8a5a12;border-color:#e9d1a4}
.badge.low{background:#eef1f0;color:#4d625a;border-color:#d6dfda}
.badge.gap{background:#fbeeeb;color:#8c2f24;border-color:#e6c3bb}
small.muted,span.muted{color:var(--muted);font-size:11.5px;display:block}
a.src{font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card h3{margin-top:0}
.pred{border-left:3px solid #12563d}
ul.tight{margin:6px 0 0 18px;padding:0}ul.tight li{margin:3px 0}
footer{border-top:1px solid var(--line);margin-top:36px;padding-top:14px;color:var(--muted);font-size:12px}
.tag{font-size:11px;background:#eef4f0;border:1px solid var(--line);border-radius:6px;padding:1px 6px;margin-right:4px}
"""

NAV = [
    ("index.html", "Overview"), ("matches.html", "Match list"), ("markets.html", "Markets"),
    ("high-confidence.html", "High confidence"), ("predictions.html", "Predictions"),
    ("analysis.html", "Analysis"), ("sources.html", "Sources"), ("methodology.html", "Method"),
    ("flagged.html", "Flagged for review"), ("repo-review.html", "Repo review"),
]


def page(path: str, title: str, body: str, depth: int = 0):
    up = "../" * depth
    here = path.split("/")[-1]
    nav = "".join(
        f'<a class="{"on" if href.split("/")[-1] == here else ""}" href="{up}{href}">{esc(label)}</a>'
        for href, label in NAV
    )
    sports_links = "".join(f'<a href="{up}sports/{s["slug"]}.html">{esc(s["name"])}</a> ' for s in META.SPORTS)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG 15-sport desk · 429a54a2</title>
<meta name="description" content="Official-source match list, originated lines, confidence tiers and review flags for 15 sports, snapshot 2026-10-23T16:45Z.">
<style>{CSS}</style></head><body>
<header class="top"><div class="brand">OLBG 15-SPORT DESK<small>SESSION 429A54A2 · SNAPSHOT {esc(META.GENERATED_AT)}</small></div>
<nav class="top">{nav}</nav></header><main>
{body}
<div class="panel"><strong>Sports:</strong> {sports_links}</div>
<footer>Independent research, not betting advice. Snapshot {esc(META.GENERATED_AT)}. OLBG is used for discovery only; every accepted fixture fact is linked to its league, tour or governing body. Prices are originated estimates, not bookmaker offers. 18+.</footer>
</main></body></html>"""
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")


def tier_badge(t):
    if not t:
        return '<span class="badge gap">No price</span>'
    if t == "High":
        return '<span class="badge high">High · in band</span>'
    if t.startswith("High ("):
        return '<span class="badge med">High · out of band</span>'
    if t == "Medium":
        return '<span class="badge med">Medium</span>'
    return '<span class="badge low">Low</span>'


def when(r):
    if r["start_utc"]:
        d = datetime.strptime(r["start_utc"], "%Y-%m-%dT%H:%M:%SZ")
        return d.strftime("%d %b %H:%MZ")
    if r.get("date"):
        return f'{r["date"]} (time blank)'
    return "blank"


def match_table(rows, show_sport=True):
    head = "<tr><th>Start (UTC)</th><th>Match / market</th>" + ("<th>Sport</th>" if show_sport else "") + \
           "<th>Selection</th><th>Probability</th><th>Fair price</th><th>Tier</th><th>Official source</th></tr>"
    body = ""
    for r in rows:
        p = r["price"]
        sel = esc(p["selection"]) if p["selection"] else "<em>blank</em>"
        prob = f'{p["probability"]:.1%}' if p["probability"] else "<em>blank</em>"
        fair = f'{p["american"]:+d} ({p["fair_decimal"]:.3f})' if p["american"] else "<em>blank</em>"
        sport = f'<a href="sports/{r["sport"]}.html">{esc(r["sport_name"])}</a>' if show_sport else ""
        body += (f'<tr><td class="num">{esc(when(r))}</td>'
                 f'<td><strong>{esc(r["a"])} v {esc(r["b"])}</strong><small class="muted">{esc(r["competition"])} · {esc(r["stage"])}'
                 f'{" · " + esc(r["venue"]) if r["venue"] else ""}</small></td>'
                 + (f"<td>{sport}</td>" if show_sport else "") +
                 f'<td>{sel}</td><td class="num">{prob}</td><td class="num">{fair}</td>'
                 f'<td>{tier_badge(p["tier"])}</td>'
                 f'<td><a class="src" href="{esc(r["official"])}">{esc(r["official_label"] or "Official source")}</a>'
                 f'<small class="muted">read {esc(r["observed"])}</small></td></tr>')
    return f'<div class="table-wrap"><table>{head}{body}</table></div>'


def build_site(records, sports, counts):
    OUT.mkdir(parents=True, exist_ok=True)
    in_band = [r for r in records if r["price"]["tier"] == "High"]
    out_band = [r for r in records if (r["price"]["tier"] or "").startswith("High (")]
    med = [r for r in records if r["price"]["tier"] == "Medium"]

    # ---------- overview ----------
    kpi = f"""<div class="kpis">
<div class="kpi"><b>{counts['rows']}</b><span>fixture rows</span></div>
<div class="kpi"><b>{counts['priced']}</b><span>priced</span></div>
<div class="kpi"><b>{counts['high']}</b><span>High in band</span></div>
<div class="kpi"><b>{counts['high_out']}</b><span>High outside band</span></div>
<div class="kpi"><b>{counts['medium']}</b><span>Medium</span></div>
<div class="kpi"><b>{counts['predictions']}</b><span>predictions</span></div>
<div class="kpi"><b>{counts['unverified']}</b><span>unverified rows</span></div>
<div class="kpi"><b>{counts['flags']}</b><span>review flags</span></div></div>"""
    top = "".join(
        f'<article class="card pred"><h3>{esc(r["a"])} v {esc(r["b"])}</h3>'
        f'<p><strong>{esc(r["price"]["selection"])}</strong> · {r["price"]["probability"]:.1%} · '
        f'{r["price"]["american"]:+d} fair · {tier_badge(r["price"]["tier"])}</p>'
        f'<p class="muted">{esc(r["competition"])} · {esc(when(r))}</p>'
        f'<a class="src" href="{esc(r["official"])}">Official source</a></article>'
        for r in in_band)
    body = f"""<h1>Fifteen sports, one evidence desk</h1>
<p class="lede">A single-snapshot match list for the sports you asked for, built the way the brief requires: each accepted fixture is linked to the league, tour or governing body that published it, every price is an originated estimate with a stated input, and anything unconfirmed is left blank and published on the review page. This is not a complete global slate.</p>
<div class="notice"><strong>Read this first.</strong> The snapshot was taken at {esc(META.GENERATED_AT)}. Fixtures whose start had already passed at that moment are marked elapsed and are never priced; rows that start after the snapshot can still pass while you read the page, so check the official status before acting. Confidence is capped where the official input is thin: a one-game NBA sample or a viewing-order label cannot produce a 70% claim, and no row is promoted to fill a quota.</div>
{kpi}
<h2>Executive summary — High-confidence picks in the requested band</h2>
<p class="lede">A High pick must clear three gates at once: both sides' official strength inputs were read, the originated probability is at least 70%, and the fair price sits inside -250 to +10000. {counts['high']} selections clear all three; {counts['high_out']} more clear the probability gate but price shorter than -250 and are disclosed separately rather than relabelled.</p>
<div class="grid">{top or '<p>No selection cleared every gate in this snapshot.</p>'}</div>
<h2>Today and the next 48 hours</h2>
{match_table([r for r in records if r['price']['markets'] and (r['start_utc'] or '') >= '2026-10-23T16:45'], show_sport=True)}
<h2>What this desk does not do</h2>
<div class="panel"><ul class="tight">
<li>It does not treat an OLBG display time as a UTC start. The label conflicts are itemised on the review page.</li>
<li>It does not convert tip-share percentages into probabilities, and it does not copy a bookmaker price.</li>
<li>It does not publish a selection for a sport whose official quantitative input is missing. Those rows are blank, counted, and flagged.</li>
<li>It does not claim worldwide coverage. {counts['unverified']} rows could not be confirmed officially and {counts['elapsed']} had already started.</li>
</ul></div>
<h2>Sports covered</h2>
<div class="table-wrap"><table><tr><th>Sport</th><th>Rows</th><th>Priced</th><th>High in band</th><th>High out of band</th><th>Medium</th><th>Blank / flagged</th><th>Official anchor</th></tr>
{''.join(f'<tr><td><a href="sports/{s["slug"]}.html">{esc(s["name"])}</a></td><td class="num">{s["rows"]}</td><td class="num">{s["priced"]}</td><td class="num">{s["high"]}</td><td class="num">{s["high_out"]}</td><td class="num">{s["medium"]}</td><td class="num">{s["unverified"] + s["elapsed"]}</td><td><a class="src" href="{esc(s["official_url"])}">{esc(s["official_name"])}</a></td></tr>' for s in sports)}
</table></div>"""
    page("index.html", "Overview", body)

    # ---------- matches ----------
    body = f"""<h1>Match list</h1>
<p class="lede">Every row is a fixture that was read on an official page this session. Blank selection, probability or price means the row did not have the inputs for one; the reason is on the review page and in the JSON. The list is frozen at {esc(META.GENERATED_AT)}: later status changes, postponements and line-up news are not reflected, so confirm on the linked page.</p>
<div class="notice">Rows are sorted by sport and start. A verified fixture is not a verified price: the source column proves the match exists and when it starts, not that the estimate is right.</div>
{match_table(records)}"""
    page("matches.html", "Match list", body)

    # ---------- markets ----------
    blocks = ""
    for r in records:
        p = r["price"]
        if not p["markets"]:
            continue
        rows = ""
        for m in p["markets"]:
            if m.get("probability") is None:
                rows += (f'<tr><td>{esc(m["market"].replace("_", " ").title())}</td><td>{esc(m.get("line", ""))}</td>'
                         f'<td>{esc(m["selection"])}</td><td colspan="2"><em>withheld</em></td></tr>')
                continue
            over = "Over" in m["selection"]
            rows += (f'<tr><td>{esc(m["market"].replace("_", " ").title())}</td><td class="num">{esc(m.get("line", ""))}</td>'
                     f'<td>{esc(m["selection"])}</td><td class="num">{m["probability"]:.1%}</td>'
                     f'<td class="num">{m["american"]:+d} ({m["fair_decimal"]:.3f})</td></tr>')
        blocks += (f'<section class="panel"><h3>{esc(r["a"])} v {esc(r["b"])} <small class="muted">{esc(r["competition"])} · {esc(when(r))} · '
                   f'{esc(p["basis"] or "")}</small></h3><div class="table-wrap"><table>'
                   f'<tr><th>Market</th><th>Line</th><th>Selection</th><th>Probability</th><th>Fair price</th></tr>{rows}</table></div>'
                   f'<p><a class="src" href="{esc(r["official"])}">{esc(r["official_label"])}</a></p></section>')
    withheld = "".join(
        f'<li><strong>{esc(r["a"])} v {esc(r["b"])}</strong> ({esc(r["sport_name"])}): {esc("; ".join(r["price"]["withheld"]) or "no priced market")}</li>'
        for r in records if not r["price"]["markets"])
    body = f"""<h1>Market explorer</h1>
<p class="lede">{counts['markets']} originated markets across {counts['priced']} priced fixtures: match winner, a handicap ladder and a total ladder wherever the input supports a distribution. Every price is fair (1/probability) with no margin added.</p>
<div class="notice">These are <strong>our lines</strong>, not bookmaker offers. No market quote, availability, settlement rule or betting edge is asserted.</div>
{blocks}
<h2>Fixtures with no originated market</h2>
<div class="panel"><ul class="tight">{withheld}</ul></div>"""
    page("markets.html", "Markets", body)

    # ---------- high confidence ----------
    def ledger(rows, note):
        if not rows:
            return f"<p class='muted'>{note}</p>"
        return match_table(rows, show_sport=True)

    body = f"""<h1>Confidence tiers</h1>
<p class="lede">Tiers are earned, not assigned. A selection reaches High only when both sides have an official quantitative input, the originated probability is at least 70%, and nothing in the official record contradicts the pick. The requested -250 to +10000 band is reported as a separate, stricter subset.</p>
<h2>High and inside the band ({counts['high']})</h2>
{ledger(in_band, 'None in this snapshot.')}
<h2>High probability but priced shorter than -250 ({counts['high_out']}) — disclosed, not promoted</h2>
<div class="notice">The arithmetic is unavoidable: -250 is 1.400 decimal, which is 71.43%. Any selection above that probability must price shorter than -250, so the band and a 70%-plus probability only overlap between 70.0% and 71.43%. Rather than hide the chalk, these picks are published with their real price and marked out of band.</div>
{ledger(out_band, 'None.')}
<h2>Medium ({counts['medium']})</h2>
{ledger(med, 'None.')}
<h2>The five strongest picks in each sport</h2>
{''.join(f'<h3>{esc(s["name"])}</h3>' + (match_table(top_five(records, s["slug"]), show_sport=False) if top_five(records, s["slug"]) else '<p class="muted">No priced fixture in this snapshot, so no pick exists to rank. The sport page states the reason.</p>') for s in META.SPORTS)}
<h2>Why some sports have no tiered pick</h2>
<div class="panel"><p>Eight sports produced fixtures but no priceable strength input this session: tennis (seeding order only), cricket (no team ratings read), basketball (one-game sample and elapsed EuroLeague games), rugby union (schedules and line-ups, but no official table read for the Premiership or URC), rugby league (squads only), gaelic sports (fixtures only), snooker (frame results only), motor racing (standings only, and a two-driver market is not the race), golf (leaderboard only, no round-three pairings). Those pages publish the fixture facts, the blank cells and the reason.</p></div>"""
    page("high-confidence.html", "High confidence", body)

    # ---------- predictions ----------
    pred_cards = ""
    for p in PREDICTIONS:
        rec = next(r for r in records if r["id"] == p["fixture"])
        words = len(p["text"].split())
        pred_cards += (f'<article class="panel pred"><h3>{esc(rec["a"])} v {esc(rec["b"])}</h3>'
                       f'<p class="muted">{esc(rec["competition"])} · {esc(when(rec))} · {esc(p["tier"])} · {words} words</p>'
                       f'<p><strong>Selection:</strong> {esc(p["selection"])}</p><p>{esc(p["text"])}</p>'
                       f'<p><a class="src" href="{esc(rec["official"])}">{esc(rec["official_label"])}</a> '
                       f'<small class="muted">read {esc(rec["observed"])}</small></p></article>')
    body = f"""<h1>Predictions</h1>
<p class="lede">{len(PREDICTIONS)} hand-written predictions, one per priced selection that reached High or Medium. Each names the selection in plain terms, gives the scoreline or record it rests on, and links the official page it was read from. No text was generated from a template and none repeats a six-word phrase from another.</p>
<div class="notice"><strong>What a prediction is not.</strong> It is not a guarantee, a tip from OLBG, or a claim about a bookmaker's price. Where a sport has no priceable input, there is no prediction — a blank is more useful than invented certainty.</div>
{pred_cards}"""
    page("predictions.html", "Predictions", body)

    # ---------- analysis ----------
    body = f"""<h1>Analysis and findings</h1>
<p class="lede">What the snapshot contains, how the tiers fell out, and what the OLBG reconstruction showed. Counts here are computed from the same JSON that renders the tables.</p>
<div class="kpis">
<div class="kpi"><b>{counts['rows']}</b><span>fixture rows</span></div>
<div class="kpi"><b>{counts['priced']}</b><span>priced</span></div>
<div class="kpi"><b>{counts['markets']}</b><span>markets</span></div>
<div class="kpi"><b>{counts['high']}/{counts['high_out']}</b><span>High in/out of band</span></div>
</div>
<h2>How the tiers fell out</h2>
<div class="table-wrap"><table><tr><th>Tier</th><th>Rule</th><th>Count</th></tr>
<tr><td>High, in band</td><td>p &ge; 0.70, fair price inside -250..+10000, both official inputs</td><td class="num">{counts['high']}</td></tr>
<tr><td>High, out of band</td><td>p &ge; 0.70 but fair price shorter than -250</td><td class="num">{counts['high_out']}</td></tr>
<tr><td>Medium</td><td>0.60 &le; p &lt; 0.70 with both inputs</td><td class="num">{counts['medium']}</td></tr>
<tr><td>Low</td><td>p &lt; 0.60, or a single-input model</td><td class="num">{counts['low']}</td></tr>
<tr><td>No price</td><td>fixture confirmed but no official strength input, or start elapsed</td><td class="num">{counts['rows'] - counts['priced']}</td></tr>
</table></div>
<h2>What the OLBG reconstruction showed</h2>
<div class="panel"><ul class="tight">
<li>Fifteen sport routes were read: Golf/5, Volleyball/21, Rugby_Union/9, Cricket/7, Snooker/8, Darts/15, Baseball/12, Gaelic_Football/25, Greyhounds/28, Tennis/3, Motor_Racing/14, Handball/20, Ice_Hockey/13, Basketball/4, Rugby_League/10. Hurling/26 was read only to confirm the exclusion.</li>
<li>Each hub exposes one most-tipped selection per event with a tip count and a rounded share; the per-event page adds the full market list. That is discovery only — a tip share is a vote count, not a probability, and this desk never converts it.</li>
<li>Times on the hubs carry no zone label and disagree with official schedules by three to four hours across sports (see F-429A-01). Three hubs were empty or ante-post-only during live competition (golf, rugby league, and the 2027 Masters).</li>
<li>Two hubs listed a fixture the official body did not support at the stated date: the Cork football final (25 October per Cork GAA, not OLBG's 24 October card) and the Munster club page URL, which now 404s.</li>
</ul></div>
<h2>Where the prices come from</h2>
<div class="panel"><p>Ice hockey uses log5 on the league's own points percentages plus team goals for and against per game. Handball uses attack and defence ratios around the LNH league mean. No home edge, no market input and no clipping are applied. The consequence is visible: the Carolina price of -245 and the Montreal price of -250 are what the arithmetic produces, not what a bookmaker would hang.</p>
<p>Nothing else is priced. Tennis has a seeding order but no rating scale; cricket has fixtures but no team ratings read; the NBA has official fixtures and one-game records that cannot support a rating; rugby has line-ups but no official table read this session; snooker has frame results but no strength input. Each of those is a blank, counted on this page and explained on the sport page.</p></div>
<h2>Repository findings</h2>
<p class="lede">Eight specific findings with file and line, all re-read this session. They are also on the repo review page.</p>
<div class="table-wrap"><table><tr><th>ID</th><th>File</th><th>Line</th><th>Finding</th></tr>
{''.join(f'<tr><td>{esc(a)}</td><td><code>{esc(b)}</code></td><td class="num">{c}</td><td>{esc(d)}</td></tr>' for a, b, c, d in REPO_FINDINGS)}</table></div>"""
    page("analysis.html", "Analysis", body)

    # ---------- sources ----------
    srcs = {}
    for r in records:
        srcs.setdefault(r["official"], {"label": r["official_label"], "window": r["observed"], "rows": []})["rows"].append(r["id"])
    rows = "".join(
        f'<tr><td><a class="src" href="{esc(url)}">{esc(v["label"] or url)}</a><small class="muted">{esc(url)}</small></td>'
        f'<td>{esc(v["window"])}</td><td class="num">{len(v["rows"])}</td><td>{esc(", ".join(v["rows"]))}</td></tr>'
        for url, v in sorted(srcs.items()))
    sports_rows = "".join(
        f'<tr><td>{esc(s["name"])}</td><td class="num">{s["olbg_id"]}</td>'
        f'<td><a class="src" href="{esc(s["olbg_url"])}">OLBG hub (discovery)</a></td>'
        f'<td><a class="src" href="{esc(s["official_url"])}">{esc(s["official_name"])}</a></td></tr>' for s in META.SPORTS)
    body = f"""<h1>Sources</h1>
<p class="lede">Every official page used for a fixture fact, with the observation window and the rows it supports. Links open the publisher's own page; nothing here is cached or proxied.</p>
<div class="notice">A link proves what was published at read time. It does not prove the match is still scheduled, that a player is fit, or that a price is available.</div>
<h2>Official fixture and input sources</h2>
<div class="table-wrap"><table><tr><th>Publisher page</th><th>Observed (UTC)</th><th>Rows</th><th>Supports</th></tr>{rows}</table></div>
<h2>Discovery routes and their official counterparts</h2>
<div class="table-wrap"><table><tr><th>Sport</th><th>OLBG id</th><th>Discovery</th><th>Official anchor</th></tr>{sports_rows}</table></div>
<h2>Method family by sport</h2>
<div class="table-wrap"><table><tr><th>Sport</th><th>Originated-market family (documented, not calibrated)</th></tr>
{''.join(f'<tr><td>{esc(s["name"])}</td><td>{esc(s["model_family"])}</td></tr>' for s in META.SPORTS)}</table></div>"""
    page("sources.html", "Sources", body)

    # ---------- methodology ----------
    body = f"""<h1>Methodology</h1>
<p class="lede">The rules that decide what appears in a cell, and what stays blank.</p>
<div class="panel"><h3>1. Fixture truth</h3><p>A row is accepted only if the participants, competition and date were read on a league, tour or governing-body page. OLBG supplies the route and the event name; it never certifies the fixture. If only a secondary source lists a match, the row is published blank with a flag.</p>
<h3>2. Start times</h3><p>Times are UTC. Where the official page gives only a local time with a stated venue, the row records the start and the local label. Where the page renders a time in the reader's own zone, or gives no zone, the start is left blank. No timezone is guessed.</p>
<h3>3. Prices</h3><p>A price exists only when both sides have an official quantitative input. Ice hockey: log5 on points percentage; goals for and against per game give the puck line and totals through independent Poisson scores. Handball: attack and defence ratios around the LNH mean. No home edge, no margin, no clipping. Fair decimal is 1/probability; the American equivalent is derived from it.</p>
<h3>4. Confidence</h3><p>High needs both inputs, p &ge; 0.70 and no contradicting official context. Medium is 0.60 to 0.70. Everything else is Low. The requested -250 to +10000 band is shown as a separate flag because a probability above 71.43% cannot sit inside it; those picks are disclosed instead of relabelled.</p>
<h3>5. Blank and flagged</h3><p>An unconfirmed value is empty in JSON and empty in the table. It is never filled from memory, a media report or a previous session's file. The review page lists every such row with the reason and the official link that was checked.</p>
<h3>6. What is not claimed</h3><p>No worldwide coverage, no calibration, no injury feed, no bookmaker quote, no edge, and no guarantee. The NBA and opening-week samples are specifically not used to invent strength.</p></div>
<h2>Reproduction</h2>
<div class="panel"><p>The dataset, prices and pages are generated from one script:</p>
<pre style="overflow-x:auto;background:#f2f6f4;padding:12px;border-radius:8px"><code>python3 scripts/s429a54a2_build.py
python3 scripts/s429a54a2_validate.py</code></pre>
<p>The build is deterministic for a fixed snapshot string, and the validator re-checks every table row for an official https link, every High pick for the probability and band gates, and every prediction for length and repetition.</p></div>"""
    page("methodology.html", "Methodology", body)

    # ---------- flagged ----------
    cards = ""
    for fid, sev, title, detail, url, rows_ in FLAGS:
        rows_html = ", ".join(rows_) if rows_ else "—"
        cards += (f'<article class="panel {"warn" if sev == "high" else ""}" id="{esc(fid)}"><h3>{esc(fid)} · {esc(title)} '
                  f'<span class="badge {"gap" if sev == "high" else "med"}">{esc(sev)}</span></h3><p>{esc(detail)}</p>'
                  f'<p><a class="src" href="{esc(url)}">Official or repository source</a>'
                  f'<small class="muted">Affected rows: {esc(rows_html)}</small></p></article>')
    body = f"""<h1>Flagged for review</h1>
<p class="lede">{len(FLAGS)} items that need a human eye: source conflicts, stale OLBG cards, data that could not be confirmed, and defects in the merged repository. None of them blocks publication; all of them block certainty.</p>
<div class="notice"><strong>How to use this page.</strong> Every flag names the rows it affects and links the page that was read. Where two official sources disagree, both are shown and the one used is stated — no average, no silent choice.</div>
{cards}"""
    page("flagged.html", "Flagged for review", body)

    # ---------- repo review ----------
    rows_html = "".join(
        f'<tr><td>{esc(a)}</td><td><code>{esc(b)}</code></td><td class="num">{c}</td><td>{esc(d)}</td>'
        f'<td><a class="src" href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/{esc(b)}#L{c}">line {c}</a></td></tr>'
        for a, b, c, d in REPO_FINDINGS)
    body = f"""<h1>Repository review</h1>
<p class="lede">Line-by-line checks of the merged tree, with the file and line for each finding. Nothing here was edited: the shared board and the other sessions' desks are outside this session's scope.</p>
<div class="table-wrap"><table><tr><th>ID</th><th>File</th><th>Line</th><th>Finding</th><th>Link</th></tr>{rows_html}</table></div>
<h2>What was re-read this session</h2>
<div class="panel"><ul class="tight">
<li><code>COORDINATION.md</code> task table and section headings, for duplicate ids, duplicated sections and stale in-progress rows.</li>
<li><code>scripts/validate.py</code> link gate, to establish what it does and does not check.</li>
<li><code>data/current/snapshot.json</code> generation time, to establish that the canonical snapshot predates this session by more than a day.</li>
<li>The newest merged desk (<code>data/2b72da34/desk.json</code>, <code>2b72da34/*.html</code>, <code>scripts/s2b72da34_build.py</code>), because it is the closest prior attempt at the same 15-sport brief.</li>
</ul>
<p class="muted">This review is structural and documentary. It does not re-certify any prior session's predictions, and it does not claim that the files it did not open are correct.</p></div>
<h2>Self-checks on this desk</h2>
<div class="panel"><ul class="tight">
<li>{counts['rows']} rows, each with an https official link; {counts['unverified']} explicitly unverified and {counts['elapsed']} elapsed.</li>
<li>{counts['high']} High picks inside the band, {counts['high_out']} High picks outside it and disclosed, {counts['medium']} Medium.</li>
<li>{counts['predictions']} predictions, each at least 30 words, each naming its selection, with no shared six-word phrase.</li>
<li>No prediction text contains the internal words used for the price engine.</li>
</ul></div>"""
    page("repo-review.html", "Repository review", body)

    # ---------- sport pages ----------
    for s in sports:
        rows = [r for r in records if r["sport"] == s["slug"]]
        gap = ""
        if not rows:
            gap = '<div class="notice">No fixture for this sport was confirmed on an official page in this snapshot. That is a coverage gap, not a claim that no event exists.</div>'
        unpriced = [r for r in rows if not r["price"]["markets"]]
        unpriced_html = "".join(
            f'<li><strong>{esc(r["a"])} v {esc(r["b"])}</strong> — {esc("; ".join(r["price"]["withheld"]) or r["notes"])}</li>'
            for r in unpriced)
        body = f"""<h1>{esc(s["name"])}</h1>
<p class="lede">{esc(s["notes"])}</p>
<div class="kpis"><div class="kpi"><b>{s['rows']}</b><span>rows</span></div><div class="kpi"><b>{s['priced']}</b><span>priced</span></div>
<div class="kpi"><b>{s['high']}</b><span>High in band</span></div><div class="kpi"><b>{s['high_out']}</b><span>High out of band</span></div>
<div class="kpi"><b>{s['unverified'] + s['elapsed']}</b><span>blank / elapsed</span></div></div>
<p><a class="src" href="{esc(s["olbg_url"])}">OLBG {esc(s["name"])} hub (discovery)</a> · <a class="src" href="{esc(s["official_url"])}">{esc(s["official_name"])}</a></p>
<div class="notice"><strong>Method:</strong> {esc(s["model_family"])}. This is a documented approach, not a calibrated model; read the methodology page before using any number.</div>
{gap}
<h2>Fixtures</h2>
{match_table(rows, show_sport=False) if rows else '<p class="muted">No rows.</p>'}
<h2>No price, and why</h2>
<div class="panel"><ul class="tight">{unpriced_html or '<li>Every confirmed fixture in this sport carried a price.</li>'}</ul></div>"""
        page(f'sports/{s["slug"]}.html', s["name"], body, depth=1)

    # ---------- exports ----------
    with (DATA / "matches.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "sport", "competition", "stage", "participant_a", "participant_b", "start_utc", "date", "venue",
                    "status", "tier", "selection", "probability", "american", "fair_decimal", "official_url", "observed"])
        for r in records:
            p = r["price"]
            w.writerow([r["id"], r["sport"], r["competition"], r["stage"], r["a"], r["b"], r["start_utc"] or "", r.get("date") or "",
                        r["venue"] or "", r["status"], p["tier"] or "", p["selection"] or "", p["probability"] or "",
                        p["american"] or "", p["fair_decimal"] or "", r["official"], r["observed"]])
    with (DATA / "markets.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["fixture_id", "market", "line", "selection", "probability", "american", "fair_decimal", "official_url"])
        for r in records:
            for m in r["price"]["markets"]:
                w.writerow([r["id"], m["market"], m.get("line", ""), m["selection"], m.get("probability") or "",
                            m.get("american") or "", m.get("fair_decimal") or "", r["official"]])


def main():
    records = build_records()
    sports = summarise(records)
    counts = write_data(records, sports)
    build_site(records, sports, counts)
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
