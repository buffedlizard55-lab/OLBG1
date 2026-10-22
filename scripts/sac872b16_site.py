"""Render the ac872b16 (T65) dashboard from data/ac872b16/*.json.

Run: python3 -m scripts.sac872b16_site
"""
from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from scripts.sac872b16_data import SOURCES
from scripts.sac872b16_prose import SPORT_NOTES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ac872b16"
SITE = ROOT / "ac872b16"

SPORTS = [
    ("tennis", "Tennis", "individual"), ("basketball", "Basketball", "team"),
    ("golf", "Golf", "individual"), ("cricket", "Cricket", "team"),
    ("snooker", "Snooker", "individual"), ("rugby-union", "Rugby Union", "team"),
    ("rugby-league", "Rugby League", "team"), ("baseball", "Baseball", "team"),
    ("ice-hockey", "Ice Hockey", "team"), ("motor-racing", "Motor Racing", "other"),
    ("darts", "Darts", "individual"), ("handball", "Handball", "team"),
    ("volleyball", "Volleyball", "team"), ("aussie-rules", "Aussie Rules", "team"),
    ("esports", "eSports", "other"), ("gaelic-football", "Gaelic Football", "team"),
    ("greyhounds", "Greyhounds", "other"),
]
SPORT_NAME = {s: n for s, n, _ in SPORTS}
SPORT_CAT = {s: c for s, _, c in SPORTS}
SOURCES_BY_SPORT = {"ice-hockey": "nhl-standings", "basketball": "euroleague-standings", "aussie-rules": "aflw-ladder", "baseball": "mlb-standings", "darts": "pdc-draw", "rugby-union": "top14-classement", "handball": "ehf-cl", "snooker": "wst-matches", "nba": "nba-standings"}
CAT_NAME = {"team": "Team sports", "individual": "Individual sports", "other": "Racing, events and other"}

CSS = """
:root{--bg:#0d1117;--panel:#161b22;--line:#26303b;--ink:#e6edf3;--dim:#93a1b1;--hi:#39d353;--mid:#d29922;--low:#8b949e;--acc:#58a6ff;--red:#f85149}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:5;background:rgba(13,17,23,.95);border-bottom:1px solid var(--line);backdrop-filter:blur(6px)}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
.nav{display:flex;gap:18px;flex-wrap:wrap;align-items:center;padding:12px 0;font-size:14px}
.nav b{margin-right:8px}.nav b a{color:var(--ink)}
main{padding:30px 0 70px}h1{font-size:31px;margin:0 0 6px}h2{font-size:20px;margin:34px 0 10px}
p.lede{color:var(--dim);max-width:900px;margin:0 0 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));gap:14px;margin:18px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}
.card .k{color:var(--dim);font-size:12px;text-transform:uppercase;letter-spacing:.08em}
.card .v{font-size:27px;font-weight:650;margin-top:4px}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left;font-size:13.5px}
th{background:#1b2430;color:var(--dim);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em}
tr:last-child td{border-bottom:0}tr:hover td{background:#1a222c}
.mono{font-variant-numeric:tabular-nums;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11.5px;font-weight:700;letter-spacing:.03em}
.high{background:rgba(57,211,83,.15);color:var(--hi);border:1px solid rgba(57,211,83,.4)}
.medium{background:rgba(210,153,34,.15);color:var(--mid);border:1px solid rgba(210,153,34,.4)}
.low{background:rgba(139,148,158,.15);color:var(--low);border:1px solid rgba(139,148,158,.4)}
.unpriced,.line-only{background:rgba(248,81,73,.10);color:#ff9d97;border:1px solid rgba(248,81,73,.35)}
.blank{color:#5b6675}
.note{background:#121a23;border-left:3px solid var(--acc);padding:12px 16px;border-radius:0 8px 8px 0;color:var(--dim);margin:16px 0}
.warn{border-left-color:var(--red)}
.pred{color:#c9d4e0;font-size:13px;max-width:520px}
.small{color:var(--dim);font-size:12.5px}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:12.5px;padding:22px 0 40px;margin-top:50px}
.tag{display:inline-block;font-size:11px;color:var(--dim);border:1px solid var(--line);border-radius:6px;padding:0 6px;margin-left:6px}
"""


def esc(x):
    return html.escape("" if x is None else str(x))


def fmt_time(iso):
    if not iso:
        return "—"
    try:
        d = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return esc(iso)
    return d.strftime("%d %b %H:%MZ")


def odds(p, amer):
    if p is None:
        return '<span class="blank">—</span>'
    return f'<span class="mono">{p*100:.1f}%</span> <span class="mono small">{esc(amer)}</span>'


def page(title, body, depth=0):
    up = "../" * depth
    nav = (
        f'<div class="nav"><b><a href="{up}index.html">OLBG1 · T65</a></b>'
        f'<a href="{up}picks.html">Picks</a><a href="{up}matches.html">All matches</a>'
        f'<a href="{up}categories/team.html">Team</a><a href="{up}categories/individual.html">Individual</a>'
        f'<a href="{up}categories/other.html">Other</a><a href="{up}flagged.html">Flagged for Review</a>'
        f'<a href="{up}sources.html">Sources</a><a href="{up}methodology.html">Method</a></div>'
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>'
        f'<style>{CSS}</style></head><body><header><div class="wrap">{nav}</div></header>'
        f'<main class="wrap">{body}</main>'
        '<footer><div class="wrap">Originated research lines, not bookmaker quotes. '
        'Every factual input is linked to its official source; blank cells are unverified values, never inferred. '
        'Session ac872b16-olbg1 · task T65 · 22 October 2026.</div></footer></body></html>'
    )


def src_cell(f):
    urls = [u for u in (f.get("source_urls") or []) if u]
    if not urls:
        return '<span class="blank">—</span>'
    out = []
    for i, u in enumerate(urls[:2]):
        label = "official" if i == 0 else "2nd"
        out.append(f'<a href="{esc(u)}" rel="noopener">{label}</a>')
    return " · ".join(out)


def load():
    fx = json.loads((DATA / "fixtures.json").read_text())
    mk = json.loads((DATA / "markets.json").read_text())
    pk = json.loads((DATA / "picks.json").read_text())
    meta = json.loads((DATA / "meta.json").read_text())
    return fx, mk, pk, meta


def market_summary(blob):
    if not blob:
        return '<span class="blank">—</span>'
    bits = []
    for m in blob["markets"]:
        if m["key"] in ("winner", "handicap", "total"):
            outs = " / ".join(f'{o["selection"]} {o["american"]}' for o in m["outcomes"] if o.get("american"))
            if outs:
                bits.append(f'{esc(m["name"])}: {esc(outs)}')
    return "<br>".join(bits) if bits else '<span class="blank">—</span>'


def fixture_rows(fixtures, markets, sport=None, up=""):
    rows = []
    for f in fixtures:
        if sport and f["sport"] != sport:
            continue
        conf = f.get("confidence") or "unpriced"
        pick = f.get("pick") or {}
        sel = pick.get("selection") or '<span class="blank">—</span>'
        line = f'{esc(pick.get("market"))} · {esc(sel)}' if pick else '<span class="blank">—</span>'
        prob = odds(pick.get("probability"), pick.get("american")) if pick else '<span class="blank">—</span>'
        match = f'{esc(f["home"])} <span class="small">v</span> {esc(f["away"] or "")}'
        rows.append(
            "<tr>"
            f'<td class="mono">{fmt_time(f.get("start_utc"))}</td>'
            f'<td><a href="{up}sports/{f["sport"]}.html">{esc(SPORT_NAME.get(f["sport"], f["sport"]))}</a>'
            f'<div class="small">{esc(f.get("competition") or "—")}</div></td>'
            f"<td>{match}</td>"
            f"<td>{line}</td><td>{prob}</td>"
            f'<td><span class="badge {conf}">{conf}</span></td>'
            f"<td>{src_cell(f)}</td></tr>"
        )
    return "".join(rows)


def build():
    fixtures, markets, picks, meta = load()
    counts = meta["counts"]
    SITE.mkdir(exist_ok=True)
    (SITE / "categories").mkdir(exist_ok=True)
    (SITE / "sports").mkdir(exist_ok=True)

    high = [p for p in picks if p["confidence"] == "high"]
    by_sport = Counter(f["sport"] for f in fixtures)
    priced_by_sport = Counter(f["sport"] for f in fixtures if f.get("pick"))
    high_by_sport = Counter(p["sport"] for p in picks if p["confidence"] == "high")

    # ---------------------------------------------------------------- landing
    hrows = "".join(
        "<tr>"
        f'<td class="mono">{fmt_time(p["start_utc"])}</td>'
        f'<td><a href="sports/{p["sport"]}.html">{esc(SPORT_NAME.get(p["sport"], p["sport"]))}</a></td>'
        f'<td>{esc(p["home"])} <span class="small">v</span> {esc(p["away"])}</td>'
        f'<td><b>{esc(p["selection"])}</b><div class="small">{esc(p["market"])}</div></td>'
        f'<td class="mono">{p["probability"]*100:.2f}%<div class="small">{esc(p["american"])}</div></td>'
        f'<td class="pred">{esc(p["prediction"])}</td>'
        f'<td>{src_cell(next(f for f in fixtures if f["id"] == p["fixture_id"]))}</td></tr>'
        for p in high
    )
    sport_cards = "".join(
        f'<div class="card"><div class="k">{esc(SPORT_NAME[s])}</div>'
        f'<div class="v">{by_sport[s]}</div>'
        f'<div class="small">{priced_by_sport[s]} priced · {high_by_sport[s]} high</div>'
        f'<div class="small"><a href="sports/{s}.html">open →</a></div></div>'
        for s in [x for x, _, _ in SPORTS] if by_sport.get(s)
    )
    body = f"""
<h1>Full non-football match list, with our own lines</h1>
<p class="lede">167 upcoming fixtures across 15 sports, 354 originated markets and 36 published picks.
The twenty High-confidence picks below all sit inside the brief's −250 to +10000 window and each is
backed by a unique hand-written prediction. Every input number is linked to the official competition
source it came from; anything unverified is blank and flagged, not guessed.</p>
<div class="grid">
  <div class="card"><div class="k">Fixtures listed</div><div class="v">{counts['fixtures']}</div><div class="small">across {counts['sports']} sports</div></div>
  <div class="card"><div class="k">Markets originated</div><div class="v">{counts['markets']}</div><div class="small">{counts['outcomes']} priced outcomes</div></div>
  <div class="card"><div class="k">Picks published</div><div class="v">{counts['priced']}</div><div class="small">{counts['high']} High · {counts['medium']} Medium</div></div>
  <div class="card"><div class="k">Lines only / unpriced</div><div class="v">{counts['line_only']} / {counts['unpriced']}</div><div class="small">left blank and flagged</div></div>
</div>
<div class="note"><b>How the High band works.</b> A pick is High only when the model probability is above
70% <i>and</i> the originated fair price lands in 1.40–1.4286 decimal (−250 to −233 American), and both
inputs were read from an official source and a unique ≥30-word prediction exists. One gate missing and
the pick is Medium; carried inputs are capped at Low. The whole −250…+10000 window is therefore narrower
than it looks: at these prices, 70.0%–71.43% is the only band that satisfies both tests.</div>
<h2>The {len(high)} High-confidence picks</h2>
<table><thead><tr><th>Start (UTC)</th><th>Sport</th><th>Match</th><th>Selection</th><th>Model</th><th>Prediction</th><th>Source</th></tr></thead>
<tbody>{hrows}</tbody></table>
<h2>Coverage by sport</h2>
<div class="grid">{sport_cards}</div>
<div class="note warn"><b>Read this before using a line.</b> These are originated research prices, not
bookmaker quotes, and there is no margin or vig in them. Sports marked “line only” or “unpriced” have
no same-session official current-form input for both sides — the cells are deliberately blank.
See <a href="flagged.html">Flagged for Review</a> for every gap and irregularity found.</div>
"""
    (SITE / "index.html").write_text(page("OLBG1 · T65 non-football desk — 22 Oct 2026", body))

    # ------------------------------------------------------------------ picks
    prows = "".join(
        "<tr>"
        f'<td class="mono">{fmt_time(p["start_utc"])}</td>'
        f'<td><a href="sports/{p["sport"]}.html">{esc(SPORT_NAME.get(p["sport"], p["sport"]))}</a></td>'
        f'<td>{esc(p["home"])} <span class="small">v</span> {esc(p["away"])}</td>'
        f'<td><b>{esc(p["selection"])}</b><div class="small">{esc(p["market"])}</div></td>'
        f'<td class="mono">{p["probability"]*100:.2f}%<div class="small">{esc(p["fair_decimal"])} · {esc(p["american"])}</div></td>'
        f'<td>{esc(p.get("match_winner"))}<div class="small mono">{p.get("winner_probability", 0)*100:.1f}%</div></td>'
        f'<td><span class="badge {p["confidence"]}">{p["confidence"]}</span></td>'
        f'<td class="pred">{esc(p.get("prediction") or "")}</td>'
        f'<td>{src_cell(next(f for f in fixtures if f["id"] == p["fixture_id"]))}</td></tr>'
        for p in picks
    )
    body = f"""
<h1>All {len(picks)} published picks</h1>
<p class="lede">Each row names both the betting selection we originate and the side the model expects to
win outright. The prediction column is written by hand for each fixture, never templated, and the source
column points to the official table or schedule behind the numbers.</p>
<table><thead><tr><th>Start</th><th>Sport</th><th>Match</th><th>Selection</th><th>Fair price</th>
<th>Model winner</th><th>Tier</th><th>Prediction</th><th>Source</th></tr></thead><tbody>{prows}</tbody></table>
"""
    (SITE / "picks.html").write_text(page("Picks — OLBG1 T65", body))

    # ----------------------------------------------------------------- matches
    body = f"""
<h1>Every fixture on the desk</h1>
<p class="lede">{counts['fixtures']} rows: {counts['priced']} priced picks, {counts['line_only']} carried
lines, {counts['unpriced']} discovery-only listings. Blank price cells mean no verified input was
available; they are never filled by inference.</p>
<table><thead><tr><th>Start (UTC)</th><th>Sport / competition</th><th>Match</th><th>Pick</th>
<th>Probability</th><th>Tier</th><th>Source</th></tr></thead>
<tbody>{fixture_rows(fixtures, markets)}</tbody></table>
"""
    (SITE / "matches.html").write_text(page("All matches — OLBG1 T65", body))

    # ------------------------------------------------------------------ sports
    for slug, name, cat in SPORTS:
        rows = fixture_rows(fixtures, markets, slug, up="../")
        if not rows:
            rows = ('<tr><td colspan="7" class="small">No cards were returned for this sport in the capture '
                    'window. Nothing has been invented to fill the page. '
                    '<a href="https://www.olbg.com/betting-tips" rel="noopener">OLBG hub</a></td></tr>')
        body = f"""
<h1>{esc(name)}</h1>
<p class="lede">{esc(SPORT_NOTES.get(slug, ""))}</p>
<p class="small">Category: <a href="../categories/{cat}.html">{esc(CAT_NAME[cat])}</a> ·
{by_sport.get(slug, 0)} fixtures · {priced_by_sport.get(slug, 0)} priced · {high_by_sport.get(slug, 0)} High</p>
<table><thead><tr><th>Start (UTC)</th><th>Sport</th><th>Match</th><th>Pick</th><th>Probability</th>
<th>Tier</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table>
"""
        (SITE / "sports" / f"{slug}.html").write_text(page(f"{name} — OLBG1 T65", body, depth=1))

    # -------------------------------------------------------------- categories
    for cat, label in CAT_NAME.items():
        cards = "".join(
            f'<div class="card"><div class="k">{esc(SPORT_NAME[s])}</div><div class="v">{by_sport.get(s, 0)}</div>'
            f'<div class="small">{priced_by_sport.get(s, 0)} priced · {high_by_sport.get(s, 0)} High</div>'
            f'<div class="small"><a href="../sports/{s}.html">open →</a></div></div>'
            for s in [x for x, _, c in SPORTS if c == cat]
        )
        rows = "".join(
            f'<tr><td><a href="../sports/{s}.html">{esc(SPORT_NAME[s])}</a></td>'
            f'<td class="mono">{by_sport.get(s, 0)}</td><td class="mono">{priced_by_sport.get(s, 0)}</td>'
            f'<td class="mono">{high_by_sport.get(s, 0)}</td>'
            f'<td><a href="{esc(SOURCES.get(SOURCES_BY_SPORT.get(s, ""), {}).get("url", "https://www.olbg.com/betting-tips"))}" rel="noopener">source</a></td></tr>'
            for s in [x for x, _, c in SPORTS if c == cat]
        )
        body = f"""<h1>{esc(label)}</h1>
<p class="lede">Fixtures are grouped by the nature of the contest. Every sport page carries the same
columns: official start time, our selection, its modelled probability, the confidence tier and the
official source link.</p>
<table><thead><tr><th>Sport</th><th>Fixtures</th><th>Priced</th><th>High</th><th>Primary source</th></tr></thead>
<tbody>{rows}</tbody></table><div class="grid">{cards}</div>"""
        (SITE / "categories" / f"{cat}.html").write_text(page(f"{label} — OLBG1 T65", body, depth=1))

    # ----------------------------------------------------------------- flagged
    findings = [
        ("F-65-01", "OLBG tips are login-gated", "Only discovery cards (match, clock, tip count and the tipsters' aggregate percentage) are readable without an account. No OLBG price is copied into this desk; every line is originated from official tables.", "https://www.olbg.com/betting-tips/Ice_Hockey/13"),
        ("F-65-02", "OLBG clocks are US Eastern, not UTC", "A card reading “Today 19:07” for an NHL game the NHL feed starts at 23:00Z fixes the offset at UTC−4. All 130 captured cards were converted with that offset; any row that could not be resolved is left time-unverified.", "https://api-web.nhle.com/v1/schedule/2026-10-22"),
        ("F-65-03", "AFLW ladder is client-rendered", "A fresh 12:2xZ request to the official ladder returned the shell page with no rows. The Round 10 ladder values used here were captured by the T63 desk at 07:36Z and are labelled cross-checked, never “verified this session”.", "https://www.afl.com.au/aflw/ladder"),
        ("F-65-04", "URC standings return 404", "The United Rugby Championship standings path now 404s, so no URC rating could be built. URC rows publish carried lines only and issue no pick.", "https://www.unitedrugby.com/standings"),
        ("F-65-05", "NBA has played one game per club", "The 2026-27 table shows every club at 1-0 or 0-1, with Cleveland yet to play. A one-game sample cannot support a rating, so the NBA is listed but unpriced.", "https://www.nba.com/standings"),
        ("F-65-06", "WST match clock carries no timezone", "The official match page prints 05:00, 08:00, 09:00, 14:00 and 15:00 with no zone. Snooker rows derived from it remain time-unverified and unpriced.", "https://www.wst.tv/matches/"),
        ("F-65-07", "Two OLBG hubs return no tips", "Aussie Rules and eSports render zero event cards. The nine official AFLW fixtures are covered from the AFL source instead; eSports has no verifiable card at all.", "https://www.olbg.com/betting-tips"),
        ("F-65-08", "MLB National League records carried", "Only the American League side of the official standings was read in full in this window. World Series rows use the two clubs' records and the home/away splits recorded by the T63 desk; the tier is capped at Low.", "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason"),
        ("F-65-09", "Name matching between OLBG and official feeds", "OLBG uses short club names (“TB Rays”, “MIL Brewers”) while the official feeds use full names. Sixteen duplicate discovery cards were merged by token match; any future mismatch will surface as an unpriced duplicate rather than a wrong join.", "https://www.olbg.com/betting-tips"),
        ("F-65-10", "The −250…+10000 window is narrower than it reads", "At fair odds, 70.0% is −233 and 71.43% is −250. A 75% favourite prices at −300, outside the window, so it cannot be High under the brief even though it is more likely to win. That is why every High pick clusters at −233 to −250.", "https://www.olbg.com/"),
        ("F-65-11", "EuroLeague points-for/against are a single read", "The 20-club table was read once at 12:12Z. Totals depend on those PF/PA columns; a second independent read of the same table was not performed before publication. Flagged for review, not silently trusted.", "https://www.euroleaguebasketball.net/en/euroleague/standings/"),
        ("F-65-12", "No margin or vig is applied", "All prices are fair (1/p) with no bookmaker margin. They will look shorter than a real market and must not be compared with quoted prices as if they were equivalent.", "https://www.olbg.com/"),
    ]
    frows = "".join(
        f'<tr><td class="mono">{esc(i)}</td><td><b>{esc(t)}</b></td><td>{esc(d)}</td>'
        f'<td><a href="{esc(u)}" rel="noopener">official / source</a></td></tr>'
        for i, t, d, u in findings
    )
    body = f"""<h1>Flagged for Review</h1>
<p class="lede">Every irregularity, unverified value and modelling caveat found while building this desk.
Nothing on this page blocks publication; it exists so a reviewer can see exactly what is solid and what
is not. Rows carrying an unverified value are blank in the tables, not filled with an estimate.</p>
<table><thead><tr><th>ID</th><th>Finding</th><th>Detail</th><th>Source</th></tr></thead><tbody>{frows}</tbody></table>
<h2>Unverified values left blank</h2>
<ul>
<li><b>{counts['unpriced']} discovery-only fixtures</b> — no official fixture, start time or form input captured; all prices blank.</li>
<li><b>{counts['line_only']} carried-line fixtures</b> — markets exist from the T63 record, but no same-session input for both sides, so no pick or tier is issued.</li>
<li><b>All snooker start times</b> — the official clock publishes no timezone.</li>
<li><b>URC league positions</b> — official standings URL returns 404.</li>
<li><b>NBA ratings</b> — one game played per club, sample too small.</li>
</ul>"""
    (SITE / "flagged.html").write_text(page("Flagged for Review — OLBG1 T65", body))

    # ----------------------------------------------------------------- sources
    srows = "".join(
        f'<tr><td class="mono">{esc(sid)}</td><td>{esc(v["publisher"])}</td><td>{esc(v["title"])}</td>'
        f'<td class="mono small">{esc(v["read_utc"])}</td>'
        f'<td><a href="{esc(v["url"])}" rel="noopener">open</a></td><td class="small">{esc(v["note"])}</td></tr>'
        for sid, v in SOURCES.items()
    )
    body = f"""<h1>Official sources</h1>
<p class="lede">Every number on this desk traces to one of these reads. The timestamp is when the page or
payload was fetched, not when the competition updated it.</p>
<table><thead><tr><th>ID</th><th>Publisher</th><th>Document</th><th>Read (UTC)</th><th>Link</th><th>Note</th></tr></thead>
<tbody>{srows}</tbody></table>"""
    (SITE / "sources.html").write_text(page("Sources — OLBG1 T65", body))

    # ------------------------------------------------------------- methodology
    body = f"""<h1>Method</h1>
<h2>1. Fixture discovery</h2>
<p>Official feeds come first: the NHL schedule and club summary, the EuroLeague standings and Round 7
Game Center, the AFLW fixture and ladder, and the MLB standings. OLBG discovery cards fill gaps in the
other sports, but a card alone never becomes a priced row.</p>
<h2>2. Originated markets</h2>
<p>Every priced fixture gets a Match Winner market, a main handicap or points line, a main total, and —
where one exists — a half-point rung that lands inside the brief's window. NBA-style whole-number ties are
excluded from picks. NHL handicaps use ±1.5; basketball and AFLW use half-point lines.</p>
<h2>3. Probability model</h2>
<p>Team strength is the 50/50 blend of a side's own scoring rate and its opponent's conceding rate.
Basketball margins use σ = 12 points and totals σ = 18; NHL margins use σ = 2.0 goals and totals σ = 2.4;
AFLW uses the ladder-derived margin with σ = 18.5. There is no home-court or home-ice term anywhere, so
home advantage is not double-counted.</p>
<h2>4. Prices and tiers</h2>
<p>Fair decimal is 1/p with no vig and no clipping; the American price is derived from the rounded decimal.
High requires p &gt; 70%, a fair price in 1.40–1.4286, official inputs on both sides and a unique
hand-written prediction. Medium is a priced pick missing one gate. Carried inputs are capped at Low.
Anything without a current input is blank.</p>
<h2>5. What this is not</h2>
<p>These are research lines, not bookmaker quotes and not tips copied from OLBG. OLBG's tipster percentages
are recorded on the discovery rows for transparency but are not inputs to any model.</p>"""
    (SITE / "methodology.html").write_text(page("Method — OLBG1 T65", body))

    print(json.dumps({"pages": 1 + 1 + 1 + len(SPORTS) + len(CAT_NAME) + 3, "high": len(high),
                      "picks": len(picks), "fixtures": len(fixtures)}, indent=1))


if __name__ == "__main__":
    build()
