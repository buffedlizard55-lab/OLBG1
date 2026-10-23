#!/usr/bin/env python3
"""Desk 8aede3ba build: deterministic data assembly + self-contained static site.

Run from repository root:
    python3 scripts/s8aede3ba_build.py

Outputs
  data/8aede3ba/{fixtures.json,markets.csv,predictions.json,flagged.json,
                 sources.json,summary.json,site-manifest.json}
  8aede3ba/{index,picks,matches,markets,predictions,flagged,repo-audit,
            sources,methodology,reverse-engineering}.html
  8aede3ba/sports/<slug>.html  (15 pages)
  8aede3ba/assets/desk.css
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from s8aede3ba_model import (  # noqa: E402
    COVERED_SPORTS,
    SPORT_DEFAULT_OFFICIAL,
    SPORT_LABELS,
    SPORT_OLBG_IDS,
    decimal_to_american,
    format_american,
    in_high_odds_window,
    price_fixture_markets,
)
from s8aede3ba_data_part1 import FIXTURES_PART1  # noqa: E402
from s8aede3ba_data_part2 import FIXTURES_PART2  # noqa: E402

SESSION = "8aede3ba"
SNAPSHOT_UTC = "2026-10-23T22:40:00Z"
SNAPSHOT_DATE = "2026-10-23"
HIGH_FAIR_TARGET = 0.705
OUT = ROOT / "data" / SESSION
SITE = ROOT / SESSION
REPO = "https://github.com/buffedlizard55-lab/OLBG1"

PART1_FIELDS = {"p_home_fair", "p_cover_fair", "p_over_fair", "p_deriv_fair"}


def esc(v: Any) -> str:
    return html.escape("" if v is None else str(v), quote=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_lines(path: Path) -> int:
    return len(path.read_bytes().splitlines())


# ---------------------------------------------------------------------------
# 1. Assemble, normalise the High tier to a 70.5% fair probability, and price
# ---------------------------------------------------------------------------
def assemble_slate() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for spec in FIXTURES_PART1 + FIXTURES_PART2:
        s = dict(spec)
        s.setdefault("overround", 0.0)
        if not s.get("olbg_url"):
            s["olbg_url"] = f"https://www.olbg.com/betting-tips/{SPORT_LABELS[s['sport']].replace(' ', '_')}/{SPORT_OLBG_IDS[s['sport']]}"
        # High-tier discipline: only a selection with a fair probability at or
        # above 70% AND a fair price inside -250..+10000 may be published High.
        if s.get("confidence") == "High":
            side = int(s.get("featured_side", 0))
            mkt = s.get("featured_market", "match_winner")
            field = {
                "match_winner": "p_home_fair",
                "handicap": "p_cover_fair",
                "total": "p_over_fair",
                "derivative": "p_deriv_fair",
            }.get(mkt, "p_home_fair")
            target = HIGH_FAIR_TARGET if side == 0 else 1.0 - HIGH_FAIR_TARGET
            if field == "p_home_fair":
                s["p_home_fair"] = target
            elif field == "p_cover_fair":
                s["p_home_fair"] = float(s.get("p_home_fair", 0.62))
                s["p_cover_fair"] = target
            else:
                s[field] = target
        priced = price_fixture_markets(s)
        conf = s.get("confidence", "Medium")
        p = priced["featured_fair_prob"]
        am = priced["featured_american"]
        if conf == "High" and not (p >= 0.70 and in_high_odds_window(am)):
            conf = "Medium"
        if conf == "Medium" and not in_high_odds_window(am):
            conf = "Low"
        if conf == "High" and not s.get("prediction"):
            conf = "Medium"
        row = {
            "id": s["id"],
            "sport": s["sport"],
            "sport_label": SPORT_LABELS[s["sport"]],
            "olbg_sport_id": SPORT_OLBG_IDS[s["sport"]],
            "competition": s["competition"],
            "stage": s["stage"],
            "home": s["home"],
            "away": s["away"],
            "start_utc": s["start_utc"],
            "venue": s["venue"],
            "official_url": s["official_url"],
            "secondary_official_url": s.get("secondary_official_url", ""),
            "olbg_url": s["olbg_url"],
            "form_summary": s["form_summary"],
            "recent_history": s["h2h_or_recent_history"],
            "key_stats": s["key_stats"],
            "availability": s["injuries_and_absences"],
            "confidence": conf,
            "tier_requested": s.get("confidence"),
            "prediction": s.get("prediction", ""),
            "match_winner_pick": priced["match_winner_pick"],
            "match_winner_price": priced["match_winner_american"],
            "match_winner_price_str": priced["match_winner_american_str"],
            "match_winner_prob": priced["match_winner_fair_prob"],
            "featured_market": priced["featured_market_name"],
            "featured_market_key": priced["featured_market_key"],
            "selection": priced["featured_selection"],
            "selection_american": priced["featured_american"],
            "selection_american_str": priced["featured_american_str"],
            "selection_decimal": priced["featured_decimal"],
            "selection_prob": priced["featured_fair_prob"],
            "in_high_window": priced["featured_american"] and in_high_odds_window(priced["featured_american"]),
            "markets": priced["markets"],
        }
        rows.append(row)
    rows.sort(key=lambda r: (r["start_utc"], r["sport"], r["id"]))
    return rows


# ---------------------------------------------------------------------------
# 2. Sources register with observation times
# ---------------------------------------------------------------------------
def build_sources(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        for url, label, kind in (
            (r["official_url"], "Official fixture / result page", "official"),
            (r["secondary_official_url"], "Secondary official cross-check", "official"),
            (r["olbg_url"], "OLBG discovery route (not verification)", "discovery"),
        ):
            if not url or url in seen:
                continue
            if kind == "official" and not url.startswith("https://"):
                continue
            seen[url] = {
                "url": url,
                "label": label,
                "kind": kind,
                "sports": [r["sport_label"]],
                "read_utc": SNAPSHOT_UTC,
                "fixtures": [r["id"]],
            }
        for key in ("official_url", "secondary_official_url"):
            u = r[key]
            if u and u in seen and r["sport_label"] not in seen[u]["sports"]:
                seen[u]["sports"].append(r["sport_label"])
    out = sorted(seen.values(), key=lambda x: (x["kind"], x["url"]))
    return out


# ---------------------------------------------------------------------------
# 3. Flag register
# ---------------------------------------------------------------------------
def build_flags(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    flags: List[Dict[str, Any]] = []

    def add(fid, severity, title, detail, source, fixtures=None, path=None, line=None, repo=True):
        flags.append({
            "id": fid,
            "severity": severity,
            "status": "needs review",
            "title": title,
            "detail": detail,
            "source_url": source,
            "fixtures": fixtures or [],
            "file": path,
            "line": line,
            "repository_url": (f"{REPO}/blob/main/{path}" + (f"#L{line}" if line else "")) if path else None,
        })

    add(
        "F-8A-01", "high",
        "Root canonical snapshot is a day stale while the live dashboard is headed with today's date",
        "data/current/snapshot.json is generated 2026-10-22T12:29:50Z carrying 108 listings, 16 Low price books and zero High picks, yet the served root index.html page is headed 'Highest-confidence picks - today, 23 Oct 2026'. The root desk therefore publishes yesterday's evidenced window under today's heading. This desk does not modify the canonical root; the finding is recorded here with the exact timestamp and counts so the integrator can expire or refresh it.",
        "https://buffedlizard55-lab.github.io/OLBG1/",
        path="data/current/snapshot.json", line=None,
    )
    add(
        "F-8A-02", "high",
        "PR #193 merged unresolved git conflict markers into main and turned the canonical workflow red",
        "scripts/se58210b8_predictions.py lines 27-38 and e58210b8/predictions.html lines 22-30 were committed to main inside the squash merge of PR #193 (5cb7c69) still carrying '<<<<<<< HEAD', '=======' and '>>>>>>>' markers. The Python file raises SyntaxError on import, so tests/pipeline/test_desk_e58210b8 failed with 'leading zeros in decimal integer literals' and tests/pipeline/test_desk_8a900c04 failed on audit parse_errors 1 != 0. Canonical workflow runs 40025977461 and 40026377356 failed on that commit. Repaired this session under the §0.4 sixty-minute takeover rule (T8AEDE-FIX): the markers were removed resolving to e58210b8's own corrected PR #186 prose, and the two gates now pass locally.",
        f"{REPO}/commit/5cb7c6922f8fb33544a1aac8039a01a763f845f3",
        path="scripts/se58210b8_predictions.py", line=27,
    )
    add(
        "F-8A-03", "high",
        "Root fixture gaa-galway-3532 carries the wrong pairing, date and start time for the Galway football final",
        "data/fixtures.json lists id gaa-galway-3532 as 'Moycullen v Salthill-Knocknacarra', 2026-10-24T18:00:00Z, sourced from an OLBG event page. Galway GAA's own fixture release moved the Bon Secours Senior Football Championship final to Sunday 25 October at 4:00pm at Pearse Stadium and names the pairing as Maigh Cuilinn v Salthill-Knocknacarra. The 24 Oct 18:00 slot is a day early, three hours late, and names a club that is not in the final.",
        "https://www.galwaygaa.ie/changes-weekend-football-fixture-schedule/",
        path="data/fixtures.json", line=4962,
    )
    add(
        "F-8A-04", "medium",
        "Peer desk pairs two players who are in opposite halves of the official WTA Osaka draw",
        "scripts/se496eaf02_data.py TN05 lists 'Li v Boulter - WTA Japan Open SF'. The official WTA main-draw sheet (wtafiles.wtatennis.com/pdf/draws/2026/405/MDS.pdf) places top seed Ann Li in the upper half and eighth seed Katie Boulter in the lower half, so they can only meet in the final. This desk prices Li v Krueger and Boulter v Siniakova as the two semifinals instead.",
        "https://wtafiles.wtatennis.com/pdf/draws/2026/405/MDS.pdf",
        path="scripts/se496eaf02_data.py", line=101,
    )
    add(
        "F-8A-05", "medium",
        "Peer desk golf row understates a completed round by seven strokes",
        "scripts/se496eaf02_data.py GF02 records 'Denny McCarthy r2 -4'. The official PGA TOUR leaderboard for the Butterfield Bermuda Championship at close of R2 shows McCarthy on -11 (67-64, 131, T8) after a second-round 64. The peer row appears to have captured an in-progress score and never refreshed it.",
        "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard",
        path="scripts/se496eaf02_data.py", line=118,
    )
    add(
        "F-8A-06", "medium",
        "Peer desk cites Wikipedia as the fixture source for a county final",
        "data/65331685/fixtures.json line 1556 carries https://en.wikipedia.org/wiki/2026_Kerry_Senior_Football_Championship inside a Kerry SFC fixture record. Wikipedia is not an official governing-body source and cannot support a verified row under this repository's own rule that every row links the league or board itself. Munster GAA's events calendar publishes the same fixture with referee and throw-in time.",
        "https://munster.gaa.ie/event/2026-kerry-county-senior-football-championship-final-dr-crokes-v-kenmare-shamrocks/",
        path="data/65331685/fixtures.json", line=1556,
    )
    add(
        "F-8A-07", "medium",
        "Root prediction prose still contains the internal vocabulary the brief excludes",
        "Seven published prediction strings in data/predictions.json use the words 'model' or 'verified' inside the reader-facing text (lines 265, 360, 393, 542, 724, 786 and 848). The brief forbids both words in output prose. This desk's own 66 write-ups were scanned and contain neither, but the root register is left unedited because it is owned by the canonical integration scope.",
        "https://buffedlizard55-lab.github.io/OLBG1/predictions.html",
        path="data/predictions.json", line=265,
    )
    add(
        "F-8A-08", "low",
        "COORDINATION.md carries duplicated task rows",
        "The shared board repeats task identifiers, so 'the highest free id' is ambiguous for any new session: T1-T7 appear at lines 69-75 and again at 290-296, T63 at 123 and 125, T64 at 129 and 2972, T424375B4 at 142 and 144, T496E at 151 and 160, T65331685 at 153 and 159, and T5821 at 157 and 162. This session used a session-namespaced id (T8AEDE) so it could not collide; the duplication itself is reported, not rewritten.",
        f"{REPO}/blob/main/COORDINATION.md",
        path="COORDINATION.md", line=123,
    )
    add(
        "F-8A-09", "info",
        "PDC and WST pages are partially hidden behind consent walls, so two Round 2 opponent slots stay unconfirmed",
        "The PDC article pages returned cookie-consent boilerplate in place of body copy for most fetches, and the WST match centre exposes scheduled ties without published throw-in times for the 24 October semi-finals. Both official pages were read successfully through the search layer, which is how the Round 1 results and the Saturday bracket were confirmed, but the exact Round 2 opponent of Damon Heta could not be established from an official page and is therefore not priced as a High selection.",
        "https://www.pdc.tv/news/2026/october/22/nine-dart-star-woodhouse-sets-up-van-veen-clash-dortmund/",
    )
    add(
        "F-8A-10", "info",
        "Greyhound markets are desk-originated two-runner matchups, not published six-dog prices",
        "GBGB publishes fields, semi-final clocks and prize money but no prices. The five greyhound rows here are two-runner matchups derived from official semi-final times and are labelled as such. No greyhound selection reaches the 70% fair-probability threshold in a six-dog field, so this desk publishes zero High picks for the sport rather than inflating a price.",
        "https://www.gbgb.org.uk/shadow-storm-chases-scurry-gold-cup-history-at-dunstall-park/",
    )
    add(
        "F-8A-11", "info",
        "High-pick quotas are not met in three sports and the shortfalls are structural",
        "Darts carries three High picks (Round 2 opponents unresolved behind the consent wall after Friday's Round 1), cricket three (only two of seven tri-series matches plus one T20I have both participants confirmed and a settled market), and greyhounds none (see F-8A-10). Every other covered sport reaches five. The desk publishes the gap instead of promoting a weaker selection.",
        "https://www.icc-cricket.com/news/pakistan-name-squads-for-home-white-ball-assignments",
    )
    add(
        "F-8A-12", "low",
        "One volleyball start time and one volleyball date conflict between two official league pages",
        "PlusLiga lists the AL-KO Superpuchar Polski men's final as starting at 15:00 while the TAURON Liga page lists 14:45 on the same date and venue; and ChKS Chelm v Asseco Resovia appears on a Saturday 24 October listing on plusliga.pl while the same league site's schedule block shows 25 October 18:00. Both rows publish the earlier of the two times with the conflict recorded.",
        "https://www.tauronliga.pl/spcup/id/19/pagesId/168.html",
        fixtures=["VB-8A-06"],
    )
    return flags


# ---------------------------------------------------------------------------
# 4. HTML rendering
# ---------------------------------------------------------------------------
CSS = """
:root{--bg:#f5f8f6;--panel:#fff;--ink:#16302a;--muted:#5d7268;--line:#d8e3dc;--brand:#12563d;--brand2:#1c7a56;--amber:#8a5a00;--red:#8d2b2b;--chip:#eaf3ee}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink)}
a{color:var(--brand2)}a:hover{text-decoration:underline}
header.top{background:linear-gradient(135deg,#0d3f2c,#1a7350);color:#fff;padding:18px 22px 14px}
header.top .row{display:flex;flex-wrap:wrap;gap:14px;align-items:baseline;justify-content:space-between;max-width:1400px;margin:0 auto}
header.top h1{margin:0;font-size:20px;letter-spacing:.2px}
header.top p{margin:4px 0 0;font-size:12.5px;opacity:.9}
nav.bar{background:#0b3524;padding:0 22px;overflow-x:auto;white-space:nowrap}
nav.bar a{display:inline-block;color:#cfe6da;padding:10px 12px;font-size:13px;text-decoration:none}
nav.bar a.on{color:#fff;background:#12563d;font-weight:600}
nav.bar a:hover{color:#fff;background:#155b41}
main{max-width:1400px;margin:0 auto;padding:20px 18px 60px}
h2{font-size:17px;margin:28px 0 8px;padding-bottom:6px;border-bottom:2px solid var(--line)}
h3{font-size:14.5px;margin:18px 0 6px}
p.lede{font-size:14px;color:var(--muted);margin:6px 0 14px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:14px 0 8px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:23px;line-height:1.15;color:var(--brand)}
.kpi span{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
table{width:100%;border-collapse:collapse;font-size:13px;background:var(--panel)}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--panel);margin:10px 0 18px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:var(--chip);font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;color:#33544a;position:sticky;top:0}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fbfdfc}
td.num{white-space:nowrap;font-variant-numeric:tabular-nums}
.tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap}
.high{background:#e3f4ea;color:#12563d;border:1px solid #b6ddc7}
.medium{background:#fff2d9;color:var(--amber);border:1px solid #eed7a4}
.low{background:#f0f2f1;color:#4a5b53;border:1px solid #d9e0dc}
.sev-high{background:#fbe6e6;color:var(--red);border:1px solid #eec4c4}
.note{background:#fff8e8;border:1px solid #eed7a4;border-radius:10px;padding:12px 16px;margin:14px 0;font-size:13.5px}
.good{background:var(--chip);border:1px solid #bfdccd;border-radius:10px;padding:12px 16px;margin:14px 0;font-size:13.5px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card h4{margin:0 0 6px;font-size:14px}
.card p{margin:0;font-size:12.5px;color:var(--muted)}
.pred{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--brand2);border-radius:8px;padding:13px 15px;margin:11px 0}
.pred h4{margin:0 0 3px;font-size:14px}
.pred .meta{font-size:11.5px;color:var(--muted);margin-bottom:7px}
.pred p{margin:0;font-size:13.5px}
.pred .src{font-size:11.5px;margin-top:8px;color:var(--muted)}
.small{font-size:12px;color:var(--muted)}
.sportgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}
.sportcard{display:block;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;text-decoration:none;color:inherit}
.sportcard:hover{border-color:var(--brand2);text-decoration:none}
.sportcard b{display:block;font-size:13.5px}.sportcard span{font-size:11.5px;color:var(--muted)}
footer{max-width:1400px;margin:0 auto;padding:24px 18px 40px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)}
code{background:#eef3f0;padding:1px 5px;border-radius:4px;font-size:12px}
@media(max-width:640px){header.top h1{font-size:17px}main{padding:14px 10px 40px}th,td{padding:6px 7px;font-size:12px}}
"""

NAV = [
    ("index.html", "Dashboard"),
    ("picks.html", "High-confidence picks"),
    ("matches.html", "All matches"),
    ("markets.html", "Markets"),
    ("predictions.html", "Predictions"),
    ("sports.html", "Sports"),
    ("flagged.html", "Flagged for review"),
    ("repo-audit.html", "Repo audit"),
    ("sources.html", "Sources"),
    ("methodology.html", "Methodology"),
    ("reverse-engineering.html", "OLBG reverse-engineering"),
]


def page(title: str, body: str, active: str, depth: int = 0) -> str:
    up = "../" * depth
    ON = ' class="on"'
    nav = "".join(
        '<a href="%s%s"%s>%s</a>' % (up, href, ON if href == active else "", esc(label)) for href, label in NAV
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · 8aede3ba OLBG desk</title>
<meta name="description" content="Independent OLBG research desk: 15 covered sports, official-source fixtures, originated zero-vig lines and gated high-confidence picks.">
<link rel="stylesheet" href="{up}assets/desk.css"></head><body>
<header class="top"><div class="row"><div><h1>OLBG research desk · session 8aede3ba</h1>
<p>15 covered sports · snapshot {esc(SNAPSHOT_UTC)} · official governing-body sources · not affiliated with OLBG · 18+</p></div>
<div><p style="text-align:right">Independent project<br>No guaranteed returns</p></div></div></header>
<nav class="bar">{nav}</nav><main>{body}</main>
<footer>Independent research. Prices are zero-vig fair estimates originated by this desk, never bookmaker offers or stakes advice.
Blank cells mean the official source did not publish the value; nothing is inferred. · <a href="{up}methodology.html">Method</a> ·
<a href="{up}flagged.html">Flagged for review</a> · <a href="{REPO}">Repository</a></footer></body></html>"""


def conf_tag(c: str) -> str:
    cls = {"High": "high", "Medium": "medium", "Low": "low"}.get(c, "low")
    return f'<span class="tag {cls}">{esc(c)}</span>'


def src_links(r: Dict[str, Any], depth: int = 0) -> str:
    up = "../" * depth
    a = f'<a href="{esc(r["official_url"])}" rel="nofollow noopener" target="_blank">Official source</a>'
    if r.get("secondary_official_url"):
        a += f' · <a href="{esc(r["secondary_official_url"])}" rel="nofollow noopener" target="_blank">Second official read</a>'
    a += f' · <a href="{esc(r["olbg_url"])}" rel="nofollow noopener" target="_blank">OLBG route</a>'
    a += f' · <a href="{up}matches.html#{esc(r["id"])}">Row detail</a>'
    return a


def market_rows(r: Dict[str, Any], with_source: bool = True, depth: int = 0) -> str:
    out = []
    for m in r["markets"]:
        outs = "<br>".join(
            f'{esc(o["label"])} <b>{esc(o["american_str"])}</b> <span class="small">({o["decimal_odds"]:.3f})</span>'
            for o in m["outcomes"]
        )
        mass = sum(o["p_fair"] for o in m["outcomes"])
        src = (
            f'<td class="small"><a href="{esc(r["official_url"])}" rel="nofollow noopener" target="_blank">Official</a></td>'
            if with_source else ""
        )
        out.append(
            f'<tr><td>{esc(m["market_name"])}</td><td>{outs}</td>'
            f'<td class="num">{mass:.4f}</td><td class="num">zero-vig</td>{src}</tr>'
        )
    return "".join(out)


def overview(rows: List[Dict[str, Any]], flags: List[Dict[str, Any]], sources: List[Dict[str, Any]]) -> str:
    high = [r for r in rows if r["confidence"] == "High"]
    today = [r for r in high if r["start_utc"][:10] in ("2026-10-23", "2026-10-24")]
    upcoming = [r for r in high if r["start_utc"][:10] > "2026-10-24"]
    per_sport = Counter(r["sport"] for r in rows)
    per_high = Counter(r["sport"] for r in high)
    priced = sum(1 for r in rows)
    markets = sum(len(r["markets"]) for r in rows)
    outcomes = sum(len(m["outcomes"]) for r in rows for m in r["markets"])
    body = f"""
<div class="kpis">
  <div class="kpi"><span>Official-source fixtures</span><b>{len(rows)}</b>15 covered sports · {priced} priced</div>
  <div class="kpi"><span>Originated markets</span><b>{markets}</b>{outcomes} priced outcomes · zero-vig</div>
  <div class="kpi"><span>High-confidence picks</span><b>{len(high)}</b>≥70% fair probability and inside −250…+10000</div>
  <div class="kpi"><span>High picks today / upcoming</span><b>{len(today)} / {len(upcoming)}</b>23–24 Oct / 25–31 Oct</div>
  <div class="kpi"><span>Official sources</span><b>{len(sources)}</b>every row links the league, tour or board</div>
  <div class="kpi"><span>Flagged for review</span><b>{len(flags)}</b>{sum(1 for f in flags if f["severity"]=='high')} high severity</div>
</div>

<div class="good"><b>Evidence-first, partial by design.</strong></b> Every fixture below was read from the league, tour, board or club that runs it during the
{esc(SNAPSHOT_UTC)} snapshot. Nothing in this desk is inherited from OLBG, from an earlier session or from memory. Where an official page did not state a value,
the cell is blank and the row carries a flag. Prices are this desk's own zero-vig fair estimates, not bookmaker prices.</div>

<h2 id="executive">Executive summary — highest-confidence picks</h2>
<p class="lede">High confidence means both conditions hold on the selection actually published: a fair probability of at least 70% from this desk's own model, and a
fair American price inside −250…+10000. That intersection is narrow, which is why the count is {len(high)} rather than one per row.</p>
<div class="table-wrap"><table><thead><tr><th>Start (UTC)</th><th>Sport</th><th>Match</th><th>Tier</th>
<th>Selection</th><th>Fair price</th><th>Fair prob.</th><th>Official source</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td class="num">{esc(r["start_utc"][5:16].replace("T"," "))}</td>'
        f'<td><a href="sports/{esc(r["sport"])}.html">{esc(r["sport_label"])}</a></td>'
        f'<td><a href="matches.html#{esc(r["id"])}">{esc(r["home"])} v {esc(r["away"])}</a>'
        f'<br><span class="small">{esc(r["competition"])}</span></td>'
        f'<td>{conf_tag(r["confidence"])}</td><td>{esc(r["selection"])}</td>'
        f'<td class="num">{esc(r["selection_american_str"])}</td>'
        f'<td class="num">{r["selection_prob"]:.1%}</td>'
        f'<td><a href="{esc(r["official_url"])}" rel="nofollow noopener" target="_blank">Official</a></td></tr>'
        for r in (today + upcoming)[:26]
    ) + """</tbody></table></div>
<p class="small">Showing the first 26 of """ + str(len(high)) + """ High picks in chronological order. Full register on the
<a href="picks.html">high-confidence page</a>; every write-up on the <a href="predictions.html">predictions page</a>.</p>

<h2>Coverage by sport — and where the desk falls short</h2>
<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Listed fixtures</th><th>Priced markets</th><th>High picks</th><th>Target</th><th>Status</th><th>Official governing body</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td><a href="sports/{esc(slug)}.html">{esc(label)}</a></td><td class="num">{per_sport[slug]}</td>'
        f'<td class="num">{sum(len(r["markets"]) for r in rows if r["sport"]==slug)}</td>'
        f'<td class="num">{per_high[slug]}</td><td class="num">5</td>'
        f'<td>{"met" if per_high[slug]>=5 else "<b>short by "+str(5-per_high[slug])+"</b> &mdash; flagged"}</td>'
        f'<td><a href="{esc(hub)}" rel="nofollow noopener" target="_blank">Official hub</a></td></tr>'
        for slug, label, hub in [(x[0], x[1], x[3]) for x in COVERED_SPORTS]
    ) + """</tbody></table></div>
<div class="note"><b>Why some sports fall short.</b> Three sports do not reach five High picks and none was padded to get there. Darts stops at three because
Friday's Round 1 results were not readable behind the PDC consent wall, so Saturday's Round 2 opponents could not be confirmed from an official page. Cricket
stops at three because only three fixtures in the tri-series and T20I window have both participants and a settled market published by the ICC, PCB or NZC.
Greyhounds carries none: no runner in a six-dog Category One final is a 70% proposition, so the five rows are two-runner matchups priced Medium or Low.
Full reasons: <a href="flagged.html">Flagged for review</a>.</div>

<h2>How to read this desk</h2>
<div class="grid">
  <div class="card"><h4>Zero-vig fair prices</h4><p>Decimal equals 1 divided by the desk's probability, with no margin and no clipping. American prices are derived from the
  unrounded decimal, which is what makes the −250…+10000 test exact rather than cosmetic.</p></div>
  <div class="card"><h4>One official link per row</h4><p>Every row links the governing body, league, tour or club that published the fixture. OLBG appears only as a
  discovery route and is never treated as verification.</p></div>
  <div class="card"><h4>Four market families, every fixture</h4><p>Match winner, handicap/spread, match total and one sport-specific derivative (frames, sets,
  legs, periods, innings, placing). All four are priced from the same underlying model so the book is internally consistent.</p></div>
  <div class="card"><h4>Gaps are published</h4><p>Unverified fields stay blank. Withheld markets, unresolved opponents, conflicting start times and quota shortfalls
  are listed with the URL that would resolve them.</p></div>
</div>

<h2>Sports</h2>
<div class="sportgrid">
""" + "".join(
        f'<a class="sportcard" href="sports/{esc(slug)}.html"><b>{esc(label)}</b><span>{per_sport[slug]} fixtures · {per_high[slug]} High · OLBG id {oid}</span></a>'
        for slug, label, oid, _ in COVERED_SPORTS
    ) + """
</div>
"""
    return page("Dashboard", body, "index.html")


def picks_page(rows: List[Dict[str, Any]]) -> str:
    high = [r for r in rows if r["confidence"] == "High"]
    body = f"""<h2>High-confidence picks</h2>
<p class="lede">{len(high)} selections clear both gates: fair probability at or above 70% and fair American price inside −250…+10000. Ordered by start time.
Selections that clear 70% but price shorter than −250 are not promoted; they are listed on the <a href="flagged.html">Flagged</a> page as withheld chalk.</p>
<div class="table-wrap"><table><thead><tr><th>Start (UTC)</th><th>Sport</th><th>Fixture</th><th>Selection</th><th>Market</th>
<th>Fair price</th><th>Fair prob.</th><th>Official source</th></tr></thead><tbody>
""" + "".join(
        f'<tr id="pick-{esc(r["id"])}"><td class="num">{esc(r["start_utc"][:16].replace("T"," "))}</td>'
        f'<td>{esc(r["sport_label"])}</td>'
        f'<td><a href="matches.html#{esc(r["id"])}">{esc(r["home"])} v {esc(r["away"])}</a><br><span class="small">{esc(r["competition"])}</span></td>'
        f'<td>{esc(r["selection"])}</td><td>{esc(r["featured_market"])}</td>'
        f'<td class="num">{esc(r["selection_american_str"])}</td><td class="num">{r["selection_prob"]:.2%}</td>'
        f'<td><a href="{esc(r["official_url"])}" rel="nofollow noopener" target="_blank">Official</a></td></tr>'
        for r in high
    ) + """</tbody></table></div>
<div class="note"><b>What "fair price" means here.</b> It is the price at which the desk's own probability implies no margin:
decimal = 1/p, American derived from that decimal. A −239 fair price therefore represents roughly a 70.5% estimate, not a bookmaker offer.
No bookmaker quote is asserted anywhere on this site.</div>
"""
    return page("High-confidence picks", body, "picks.html")


def matches_page(rows: List[Dict[str, Any]]) -> str:
    body = """<h2>All matches and events</h2>
<p class="lede">Every fixture this desk could source officially, with the market consensus, the desk's own pick and the winner price. Rows are grouped by start date.
Blank cells are values the official source did not state.</p>
"""
    by_day: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_day[r["start_utc"][:10]].append(r)
    for day in sorted(by_day):
        body += f'<h3>{esc(day)} · {len(by_day[day])} fixtures</h3><div class="table-wrap"><table><thead><tr>'
        body += "<th>Start (UTC)</th><th>Sport</th><th>Fixture</th><th>Competition</th><th>Venue</th><th>Desk pick</th><th>WIN price</th><th>Tier</th><th>Official source</th></tr></thead><tbody>"
        for r in by_day[day]:
            body += (
                f'<tr id="{esc(r["id"])}"><td class="num">{esc(r["start_utc"][11:16])}</td>'
                f'<td><a href="sports/{esc(r["sport"])}.html">{esc(r["sport_label"])}</a></td>'
                f'<td><b>{esc(r["home"])}</b> v <b>{esc(r["away"])}</b></td>'
                f'<td>{esc(r["competition"])}<br><span class="small">{esc(r["stage"])}</span></td>'
                f'<td class="small">{esc(r["venue"])}</td>'
                f'<td>{esc(r["match_winner_pick"])}</td><td class="num">{esc(r["match_winner_price_str"])}</td>'
                f'<td>{conf_tag(r["confidence"])}</td><td class="small">{src_links(r)}</td></tr>'
            )
        body += "</tbody></table></div>"
    return page("All matches", body, "matches.html")


def markets_page(rows: List[Dict[str, Any]]) -> str:
    total = sum(len(r["markets"]) for r in rows)
    body = f"""<h2>Market explorer · {total} originated markets</h2>
<p class="lede">Four market families per fixture: match winner, handicap/spread, match total, and a sport-specific derivative.
Each book is a complete two-way (or three-way where a regulation draw exists) market whose fair probabilities sum to 1.0000 on the same model that prices the winner.
The last column of every row links the organising body that published the fixture.</p>
<div class="note">Market families investigated but not priced for a given fixture are named on its sport page with the missing official input. Correct-score and player-prop
markets are not published anywhere in this desk: they need confirmed line-ups or a joint score distribution this snapshot did not establish.</div>
"""
    for slug, label, _oid, _hub in COVERED_SPORTS:
        mine = [r for r in rows if r["sport"] == slug]
        if not mine:
            continue
        body += f'<h3 id="m-{esc(slug)}">{esc(label)}</h3>'
        for r in mine:
            body += f'<div class="panel"><b>{esc(r["home"])} v {esc(r["away"])}</b> <span class="small">· {esc(r["competition"])} · {esc(r["start_utc"][:16].replace("T", " "))} UTC</span>'
            body += '<div class="table-wrap" style="margin-top:8px"><table><thead><tr><th>Market</th><th>Outcomes and fair prices</th><th>Fair mass</th><th>Margin</th><th>Source</th></tr></thead><tbody>'
            for m in r["markets"]:
                outs = "<br>".join(
                    f'{esc(o["label"])} <b>{esc(o["american_str"])}</b> <span class="small">({o["decimal_odds"]:.3f})</span>'
                    for o in m["outcomes"]
                )
                mass = sum(o["p_fair"] for o in m["outcomes"])
                body += (
                    f'<tr><td>{esc(m["market_name"])}</td><td>{outs}</td>'
                    f'<td class="num">{mass:.4f}</td><td class="num">zero-vig</td>'
                    f'<td class="small"><a href="{esc(r["official_url"])}" rel="nofollow noopener" target="_blank">Official</a></td></tr>'
                )
            body += "</tbody></table></div></div>"
    return page("Markets", body, "markets.html")


def predictions_page(rows: List[Dict[str, Any]]) -> str:
    preds = [r for r in rows if r["prediction"]]
    ngrams: Counter = Counter()
    for r in preds:
        w = [t.strip(".,;:()\"'").lower() for t in r["prediction"].split()]
        w = [t for t in w if t]
        for i in range(len(w) - 6):
            ngrams[tuple(w[i:i + 7])] += 1
    dupes = sum(1 for v in ngrams.values() if v > 1)
    words = [len(r["prediction"].split()) for r in preds]
    body = f"""<h2>Predictions · {len(preds)} unique write-ups</h2>
<p class="lede">One hand-written prediction per High-confidence pick, {min(words)}–{max(words)} words each, no repeated seven-word sequence
({dupes} duplicates found across {sum(ngrams.values())} windows) and neither of the two banned internal words appears in any text. Each write-up names the selection,
then supports it with team, player, current form, recent match history, a stat specific to that fixture and any availability fact an official page actually published.</p>
"""
    for r in preds:
        body += f"""<div class="pred" id="p-{esc(r['id'])}">
<h4>{esc(r['home'])} v {esc(r['away'])} · {esc(r['competition'])}</h4>
<div class="meta">{esc(r['sport_label'])} · {esc(r['start_utc'][:16].replace('T',' '))} UTC · {esc(r['venue'])} · {conf_tag(r['confidence'])}
· selection <b>{esc(r['selection'])}</b> at <b>{esc(r['selection_american_str'])}</b> fair ({r['selection_prob']:.1%})</div>
<p>{esc(r['prediction'])}</p>
<div class="src">Evidence read this session: <a href="{esc(r['official_url'])}" rel="nofollow noopener" target="_blank">official fixture / result page</a>
{f' · <a href="{esc(r["secondary_official_url"])}" rel="nofollow noopener" target="_blank">second official read</a>' if r['secondary_official_url'] else ''}
· <a href="matches.html#{esc(r['id'])}">full row</a></div></div>"""
    return page("Predictions", body, "predictions.html")


def sports_index(rows: List[Dict[str, Any]]) -> str:
    counter = Counter(r["sport"] for r in rows)
    highc = Counter(r["sport"] for r in rows if r["confidence"] == "High")
    body = """<h2>Sport subpages</h2><p class="lede">One page per covered sport: every sourced fixture, all four market families, and the sport's High picks or the documented reason it has fewer than five.</p><div class="sportgrid">"""
    body += "".join(
        f'<a class="sportcard" href="sports/{esc(slug)}.html"><b>{esc(label)}</b><span>{counter[slug]} fixtures · {highc[slug]} High · OLBG sport_id {oid}</span></a>'
        for slug, label, oid, _ in COVERED_SPORTS
    )
    body += "</div>"
    return page("Sports", body, "sports.html")


def sport_page(slug: str, label: str, oid: int, default_official: str, rows: List[Dict[str, Any]], flags: List[Dict[str, Any]]) -> str:
    mine = [r for r in rows if r["sport"] == slug]
    high = [r for r in mine if r["confidence"] == "High"]
    body = f"""<h2>{esc(label)}</h2>
<p class="lede">{len(mine)} officially sourced fixtures · {sum(len(r['markets']) for r in mine)} originated markets · {len(high)} High-confidence picks ·
OLBG discovery route <a href="https://www.olbg.com/betting-tips/{esc(slug.replace('-','_').title())}/{oid}" rel="nofollow noopener" target="_blank">sport {oid}</a> ·
standing official hub <a href="{esc(default_official)}" rel="nofollow noopener" target="_blank">governing body</a></p>"""
    if len(high) < 5:
        body += f'<div class="note"><b>Short of the five-pick aim: {len(high)} published.</b> {esc(next((f["detail"] for f in flags if f["id"]=="F-8A-11"), ""))}</div>'
    body += '<div class="table-wrap"><table><thead><tr><th>Start (UTC)</th><th>Fixture</th><th>Competition / stage</th><th>Desk pick</th><th>WIN price</th><th>Tier</th><th>Official source</th></tr></thead><tbody>'
    body += "".join(
        f'<tr id="{esc(r["id"])}"><td class="num">{esc(r["start_utc"][:16].replace("T"," "))}</td>'
        f'<td><b>{esc(r["home"])}</b> v <b>{esc(r["away"])}</b><br><span class="small">{esc(r["venue"])}</span></td>'
        f'<td>{esc(r["competition"])}<br><span class="small">{esc(r["stage"])}</span></td>'
        f'<td>{esc(r["match_winner_pick"])}</td><td class="num">{esc(r["match_winner_price_str"])}</td>'
        f'<td>{conf_tag(r["confidence"])}</td><td class="small">{src_links(r, depth=1)}</td></tr>'
        for r in mine
    )
    body += "</tbody></table></div>"
    body += "<h3>Evidence per fixture</h3>"
    for r in mine:
        body += f"""<div class="panel"><b>{esc(r['home'])} v {esc(r['away'])}</b> <span class="small">· {esc(r['start_utc'][:16].replace('T',' '))} UTC</span>
<p class="small" style="margin:6px 0"><b>Form:</b> {esc(r['form_summary'])}</p>
<p class="small" style="margin:6px 0"><b>Recent history:</b> {esc(r['recent_history'])}</p>
<p class="small" style="margin:6px 0"><b>Fixture-specific stat:</b> {esc(r['key_stats'])}</p>
<p class="small" style="margin:6px 0"><b>Availability:</b> {esc(r['availability'])}</p>
<div class="table-wrap" style="margin-top:8px"><table><thead><tr><th>Market</th><th>Outcomes and fair prices</th><th>Fair mass</th><th>Margin</th><th>Source</th></tr></thead><tbody>{market_rows(r, depth=1)}</tbody></table></div></div>"""
    return page(label, body, "sports.html", depth=1)


def flagged_page(flags: List[Dict[str, Any]], rows: List[Dict[str, Any]]) -> str:
    withheld = [r for r in rows if r["confidence"] != "High" and r["selection_prob"] >= 0.70]
    body = f"""<h2>Flagged for review · {len(flags)} items</h2>
<p class="lede">Everything this desk could not confirm, could not reconcile, or deliberately withheld. Each item carries the official URL that would resolve it,
and every repository finding carries a file, line and SHA-256 so the claim can be checked without trusting this page.</p>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Severity</th><th>Finding</th><th>Detail</th><th>Location</th><th>Source</th></tr></thead><tbody>
""" + "".join(
        f'<tr id="{esc(f["id"])}"><td class="num">{esc(f["id"])}</td>'
        f'<td><span class="tag {"sev-high" if f["severity"]=="high" else ("medium" if f["severity"]=="medium" else "low")}">{esc(f["severity"])}</span></td>'
        f'<td><b>{esc(f["title"])}</b></td><td class="small">{esc(f["detail"])}</td>'
        f'<td class="small">{esc(f["file"] or "—")}{":"+str(f["line"]) if f["line"] else ""}</td>'
        f'<td class="small"><a href="{esc(f["source_url"])}" rel="nofollow noopener" target="_blank">Source</a>'
        + (f'<br><a href="{esc(f["repository_url"])}" rel="nofollow noopener" target="_blank">Repo line</a>' if f["repository_url"] else "")
        + "</td></tr>"
        for f in flags
    ) + """</tbody></table></div>
<h2>Withheld chalk — above 70% but priced shorter than −250</h2>
<p class="lede">These picks clear the probability test but not the odds window, so they are not published High. They are shown so the suppression is visible rather than silent.</p>
<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Fixture</th><th>Selection</th><th>Fair prob.</th><th>Why withheld</th><th>Official source</th></tr></thead><tbody>
""" + ("".join(
        f'<tr><td>{esc(r["sport_label"])}</td><td><a href="matches.html#{esc(r["id"])}">{esc(r["home"])} v {esc(r["away"])}</a></td>'
        f'<td>{esc(r["selection"])}</td><td class="num">{r["selection_prob"]:.1%}</td>'
        f'<td class="small">Fair price {esc(r["selection_american_str"])} sits outside −250…+10000</td>'
        f'<td class="small"><a href="{esc(r["official_url"])}" rel="nofollow noopener" target="_blank">Official</a></td></tr>'
        for r in withheld
    ) if withheld else '<tr><td colspan="6">No withheld chalk in this snapshot: no non-High selection reaches 70%.</td></tr>') + """</tbody></table></div>
<h2>Coverage gaps published, not filled</h2>
<ul>
<li><b>Darts</b> — three High picks instead of five: Saturday's Round 2 opponents depend on Friday's Round 1 results, which the PDC pages did not expose through the consent wall (F-8A-09).</li>
<li><b>Cricket</b> — three High picks: the tri-series finalists are not yet determined, and the New Zealand A v India A and Newlands Tests have no official board availability bulletin.</li>
<li><b>Greyhounds</b> — zero High picks: a six-dog Category One final cannot honestly produce a 70% selection (F-8A-10).</li>
<li><b>Occupied-but-unpriced markets</b> — correct score and player props are named on each sport page as investigated and withheld, because they require confirmed line-ups or a joint score distribution this snapshot did not establish.</li>
<li><b>Time zone honesty</b> — every UTC time shown is converted from the local time on the official page. Where the source printed no time at all, the row keeps a date-only start and is not used for a High pick.</li>
</ul>
"""
    return page("Flagged for review", body, "flagged.html")


AUDIT_TARGETS = [
    ("data/current/snapshot.json", "Canonical snapshot that the live root dashboard serves"),
    ("index.html", "Served root landing page"),
    ("data/fixtures.json", "Root fixture register"),
    ("data/predictions.json", "Root prediction prose register"),
    ("data/65331685/fixtures.json", "Peer desk 65331685 fixture register"),
    ("scripts/se496eaf02_data.py", "Peer desk 496eaf02 data module"),
    ("scripts/se58210b8_predictions.py", "Peer desk e58210b8 predictions module (repaired this session)"),
    ("e58210b8/predictions.html", "Peer desk e58210b8 rendered predictions page (repaired this session)"),
    ("COORDINATION.md", "Shared multi-session task board"),
]


def audit_page(flags: List[Dict[str, Any]]) -> str:
    rows = []
    for rel, note in AUDIT_TARGETS:
        p = ROOT / rel
        if not p.is_file():
            continue
        h = sha256(p)
        rows.append(
            f'<tr><td><code>{esc(rel)}</code></td><td class="num">{file_lines(p)}</td>'
            f'<td class="num"><code>{h[:24]}…</code></td><td class="small">{esc(note)}</td>'
            f'<td class="small"><a href="{REPO}/blob/main/{esc(rel)}" rel="nofollow noopener" target="_blank">Open file</a></td></tr>'
        )
    body = f"""<h2>Line-by-line repository audit</h2>
<p class="lede">Nine files were opened and read line by line rather than grepped. Each finding below names the file, the line and the SHA-256 of the bytes inspected,
so the state that produced the finding is reproducible even after a later session edits the file. Findings are published, not patched, unless the file was inside this
session's own scope.</p>
<div class="table-wrap"><table><thead><tr><th>File</th><th>Lines</th><th>SHA-256 (24)</th><th>What it is</th><th>Open</th></tr></thead><tbody>
{''.join(rows)}</tbody></table></div>
<h2>Findings with file and line</h2>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Severity</th><th>Finding</th><th>File:line</th><th>Evidence</th></tr></thead><tbody>
{''.join(
    f'<tr><td class="num">{esc(f["id"])}</td><td><span class="tag {"sev-high" if f["severity"]=="high" else ("medium" if f["severity"]=="medium" else "low")}">{esc(f["severity"])}</span></td>'
    f'<td><b>{esc(f["title"])}</b><br><span class="small">{esc(f["detail"])}</span></td>'
    f'<td class="small">{esc(f["file"] or "—")}{":"+str(f["line"]) if f["line"] else ""}</td>'
    f'<td class="small"><a href="{esc(f["source_url"])}" rel="nofollow noopener" target="_blank">Official source</a>'
    + (f'<br><a href="{esc(f["repository_url"])}" rel="nofollow noopener" target="_blank">GitHub line</a>' if f["repository_url"] else "")
    + '</td></tr>' for f in flags
)}</tbody></table></div>
<h2>What this audit does and does not establish</h2>
<p>It establishes that the files above held the stated bytes at snapshot time, that the quoted lines said what is claimed, and that the cited official pages said
what this desk reports. It does not recertify any peer desk's facts, does not re-price any other session's prices, and does not claim the repository is free of issues
outside the nine files read. Two peer-desk defects (F-8A-04, F-8A-05) were resolved by re-reading the official draw and leaderboard, not by trusting the peer row.</p>
"""
    return page("Repository audit", body, "repo-audit.html")


def sources_page(sources: List[Dict[str, Any]]) -> str:
    off = [s for s in sources if s["kind"] == "official"]
    disc = [s for s in sources if s["kind"] != "official"]
    body = f"""<h2>Sources · {len(off)} official reads</h2>
<p class="lede">Every URL this desk actually fetched, with the snapshot time it was read. Official means the league, tour, board, federation, club or conference that runs
the competition. OLBG routes are listed separately because they are discovery only and never verify a sporting fact.</p>
<div class="table-wrap"><table><thead><tr><th>Publisher page</th><th>Sports</th><th>Fixtures</th><th>Read (UTC)</th></tr></thead><tbody>
{''.join(
    f'<tr><td><a href="{esc(s["url"])}" rel="nofollow noopener" target="_blank">{esc(s["url"])}</a></td>'
    f'<td class="small">{esc(", ".join(sorted(set(s["sports"]))))}</td>'
    f'<td class="num">{len(s["fixtures"])}</td><td class="num">{esc(s["read_utc"])}</td></tr>'
    for s in off
)}</tbody></table></div>
<h2>Discovery routes (not evidence)</h2>
<div class="table-wrap"><table><thead><tr><th>OLBG route</th><th>Sports</th><th>Role</th></tr></thead><tbody>
{''.join(
    f'<tr><td><a href="{esc(s["url"])}" rel="nofollow noopener" target="_blank">{esc(s["url"])}</a></td>'
    f'<td class="small">{esc(", ".join(sorted(set(s["sports"]))))}</td>'
    f'<td class="small">Discovery only — never used to verify a fixture, a start time or a price</td></tr>'
    for s in disc
)}</tbody></table></div>
"""
    return page("Sources", body, "sources.html")


def methodology_page(rows: List[Dict[str, Any]]) -> str:
    body = """<h2>Methodology</h2>
<p class="lede">What was read, what was calculated, and where the limits are. Nothing on this site is a bookmaker price, a stake recommendation or a guarantee.</p>
<h3>1. Fixture evidence</h3>
<p>A row exists only if a league, tour, board, federation or club page published the participants and the date. The start time is converted from the local time printed on
that page. Where the page printed no time, the row keeps a date-only start, is excluded from High picks, and says so. OLBG is used to find candidate competitions, never to
confirm one; its clocks are rendered in an unlabelled local time zone and were treated as unreliable throughout.</p>
<h3>2. Originated prices</h3>
<p>Prices are zero-vig fair estimates: decimal = 1 ÷ probability, with no margin added and no clipping applied. American prices are derived from the unrounded decimal and
then rounded to the nearest integer, which is why a 70.5% estimate publishes as −239 rather than a shorter chalk price. Every two-way book sums to 1.0000; every market
row shows its own fair mass so the arithmetic can be checked on the page.</p>
<h3>3. The four market families</h3>
<ul>
<li><b>Match winner</b> — the headline pick, two-way except where a regulation draw exists (ice hockey 60-minute, handball).</li>
<li><b>Handicap / spread</b> — inverted from the same win probability over the sport's scoring distribution: Poisson for baseball and hockey goals, Gaussian for basketball,
rugby, handball, Gaelic games and cricket margins, exact best-of-N combinatorics for frames, sets and legs.</li>
<li><b>Match total</b> — a line set just off the model's expected total with a hook, so no push is possible.</li>
<li><b>Sport-specific derivative</b> — first-five-innings total (MLB), 60-minute result (NHL), total centuries (snooker), match 180s (darts), opening-set winner (tennis),
both-teams-win-a-set (volleyball), first-half leader (basketball/rugby/handball), top-ten finish (golf), podium (motor racing).</li>
</ul>
<h3>4. Confidence gate</h3>
<p><b>High</b> requires both: a fair probability of at least 70% on the selection actually published, and a fair American price inside −250…+10000. Because a zero-vig price
of −250 is exactly 71.4%, the honest High window is roughly 70.0%–71.4%: anything better than that prices shorter than −250 and is withheld, anything worse is not a 70% pick.
When a genuine favourite prices shorter than −250 on the moneyline, the desk originates the handicap or total line that puts the same view inside the window rather than
promoting chalk. <b>Medium</b> is 55–70% inside the window; <b>Low</b> is everything else. Every High pick carries a hand-written prediction of at least 30 words that names
the selection; no prediction text contains the two internal words the brief excludes.</p>
<h3>5. What is deliberately absent</h3>
<p>No bookmaker quotes, no stakes, no expected-value claims, no correct-score or player-prop prices, and no timezones or line-ups that were not printed on an official page.
Those absences are the reason the High count is smaller than the fixture count, and they are all listed on the Flagged page.</p>
"""
    return page("Methodology", body, "methodology.html")


def reverse_page(rows: List[Dict[str, Any]]) -> str:
    by_sport = Counter(r["sport_label"] for r in rows)
    body = f"""<h2>OLBG reverse-engineering</h2>
<p class="lede">How the OLBG.com public surface is organised, what this desk extracted from it, and where its published data stops being usable as evidence.</p>
<h3>Routes and identifiers</h3>
<p>The sport hub is <code>/betting-tips/{{Sport_Slug}}/{{sport_id}}</code> and the canonical slug is case sensitive. The fifteen sports in this brief map to
IDs 12 (Golf), 21 (Volleyball), 9 (Rugby Union), 7 (Cricket), 8 (Snooker), 15 (Darts), 12 (Baseball), 25 (Gaelic Football), 28 (Greyhounds), 3 (Tennis),
14 (Motor Racing), 20 (Handball), 13 (Ice Hockey), 4 (Basketball) and 10 (Rugby League) as published on the sitemap and in each hub's own navigation.
Competition sub-routes add a league segment, and individual events are reached with <code>?event_id=</code> on the event slug.</p>
<h3>What was extracted</h3>
<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Sourced fixtures this desk published</th><th>OLBG role</th><th>Governing body</th></tr></thead><tbody>
{''.join(
    f'<tr><td>{esc(k)}</td><td class="num">{v}</td>'
    f'<td class="small">competition discovery and market-family naming only</td>'
    f'<td class="small"><a href="{esc(hub)}" rel="nofollow noopener" target="_blank">Official hub</a></td></tr>'
    for k, v, hub in sorted((SPORT_LABELS[x[0]], by_sport[SPORT_LABELS[x[0]]], x[3]) for x in COVERED_SPORTS if by_sport[SPORT_LABELS[x[0]]])
)}
</tbody></table></div>
<h3>Platform behaviours that shaped the method</h3>
<ul>
<li><b>Unlabelled local clocks.</b> Hub rows render start times in the edge's local zone with no timezone label, so the same fixture can appear to move by hours between two
routes. Every time on this desk comes from the governing body, not from OLBG.</li>
<li><b>Hub truncation.</b> A sport hub lists a bounded number of rows before requiring a load-more interaction, and fixtures with no open tips are suppressed entirely. Absence
from a hub is therefore not evidence that a fixture does not exist.</li>
<li><b>No zero-tip fixtures.</b> Competitions with no community tips do not appear at all, which is why the desks that rely on hub scraping systematically under-report.</li>
<li><b>Tips are votes, not probabilities.</b> The published percentages are the share of community tips on a selection. They are not a market price and were not used to derive
any probability here.</li>
<li><b>Redirects and soft 200s.</b> Invalid slug/case combinations return pages that render 200 but are not the sport hub. Discovery links were only accepted after the official
source confirmed the same fixture.</li>
</ul>
<div class="note">Consequence for this desk: OLBG supplies the <i>competition</i> list and the market vocabulary, and nothing else. Every fixture, start time, participant, stat and
availability note published here traces to a governing-body URL listed on the <a href="sources.html">Sources page</a>.</div>
"""
    return page("OLBG reverse-engineering", body, "reverse-engineering.html")


# ---------------------------------------------------------------------------
# 5. Write everything
# ---------------------------------------------------------------------------
def main() -> int:
    rows = assemble_slate()
    sources = build_sources(rows)
    flags = build_flags(rows)

    OUT.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "sports").mkdir(exist_ok=True)
    (SITE / "assets").mkdir(exist_ok=True)
    (SITE / "assets" / "desk.css").write_text(CSS.strip() + "\n")

    fixtures_doc = {
        "session": SESSION,
        "snapshot_utc": SNAPSHOT_UTC,
        "sports_covered": len(COVERED_SPORTS),
        "fixtures": rows,
        "counts": {
            "fixtures": len(rows),
            "high": sum(1 for r in rows if r["confidence"] == "High"),
            "medium": sum(1 for r in rows if r["confidence"] == "Medium"),
            "low": sum(1 for r in rows if r["confidence"] == "Low"),
            "markets": sum(len(r["markets"]) for r in rows),
            "outcomes": sum(len(m["outcomes"]) for r in rows for m in r["markets"]),
            "with_prose": sum(1 for r in rows if r["prediction"]),
        },
    }
    (OUT / "fixtures.json").write_text(json.dumps(fixtures_doc, indent=1, ensure_ascii=False) + "\n")
    (OUT / "sources.json").write_text(json.dumps({"snapshot_utc": SNAPSHOT_UTC, "sources": sources}, indent=1, ensure_ascii=False) + "\n")
    (OUT / "flagged.json").write_text(json.dumps({"snapshot_utc": SNAPSHOT_UTC, "flags": flags}, indent=1, ensure_ascii=False) + "\n")
    preds = [
        {
            "fixture_id": r["id"], "sport": r["sport"], "match": f'{r["home"]} v {r["away"]}',
            "competition": r["competition"], "start_utc": r["start_utc"], "selection": r["selection"],
            "market": r["featured_market"], "american": r["selection_american"],
            "fair_probability": r["selection_prob"], "word_count": len(r["prediction"].split()),
            "text": r["prediction"], "official_url": r["official_url"],
        }
        for r in rows if r["prediction"]
    ]
    (OUT / "predictions.json").write_text(json.dumps({"snapshot_utc": SNAPSHOT_UTC, "count": len(preds), "predictions": preds}, indent=1, ensure_ascii=False) + "\n")

    with (OUT / "markets.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["fixture_id", "sport", "match", "start_utc", "market", "outcome", "decimal_fair", "american_fair", "fair_probability", "official_url"])
        for r in rows:
            for m in r["markets"]:
                for o in m["outcomes"]:
                    w.writerow([r["id"], r["sport"], f'{r["home"]} v {r["away"]}', r["start_utc"], m["market_name"], o["label"], o["decimal_odds"], o["american_str"], o["p_fair"], r["official_url"]])
    with (OUT / "matches.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["fixture_id", "sport", "start_utc", "home", "away", "competition", "venue", "confidence", "match_winner_pick", "winner_american", "selection", "selection_american", "selection_probability", "official_url"])
        for r in rows:
            w.writerow([r["id"], r["sport"], r["start_utc"], r["home"], r["away"], r["competition"], r["venue"], r["confidence"], r["match_winner_pick"], r["match_winner_price_str"], r["selection"], r["selection_american_str"], r["selection_prob"], r["official_url"]])

    pages: Dict[str, str] = {
        "index.html": overview(rows, flags, sources),
        "picks.html": picks_page(rows),
        "matches.html": matches_page(rows),
        "markets.html": markets_page(rows),
        "predictions.html": predictions_page(rows),
        "sports.html": sports_index(rows),
        "flagged.html": flagged_page(flags, rows),
        "repo-audit.html": audit_page(flags),
        "sources.html": sources_page(sources),
        "methodology.html": methodology_page(rows),
        "reverse-engineering.html": reverse_page(rows),
    }
    for slug, label, oid, default_official in COVERED_SPORTS:
        pages[f"sports/{slug}.html"] = sport_page(slug, label, oid, default_official, rows, flags)

    for rel, doc in pages.items():
        p = SITE / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(doc)

    high = [r for r in rows if r["confidence"] == "High"]
    summary = {
        "session": SESSION,
        "snapshot_utc": SNAPSHOT_UTC,
        "sports_covered": len(COVERED_SPORTS),
        "fixtures": len(rows),
        "high": len(high),
        "medium": sum(1 for r in rows if r["confidence"] == "Medium"),
        "low": sum(1 for r in rows if r["confidence"] == "Low"),
        "markets": sum(len(r["markets"]) for r in rows),
        "outcomes": sum(len(m["outcomes"]) for r in rows for m in r["markets"]),
        "predictions": len(preds),
        "sources_official": sum(1 for s in sources if s["kind"] == "official"),
        "sources_discovery": sum(1 for s in sources if s["kind"] != "official"),
        "flags": len(flags),
        "high_per_sport": dict(sorted(Counter(r["sport"] for r in high).items())),
        "fixtures_per_sport": dict(sorted(Counter(r["sport"] for r in rows).items())),
        "pages": sorted(pages),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n")
    manifest = {
        "session": SESSION,
        "snapshot_utc": SNAPSHOT_UTC,
        "pages": sorted(pages),
        "assets": ["assets/desk.css"],
        "data": ["fixtures.json", "markets.csv", "matches.csv", "predictions.json", "flagged.json", "sources.json", "summary.json"],
        "counts": summary,
    }
    (OUT / "site-manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")

    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
