"""Session e6fc2f12-olbg1 — static dashboard builder.

Writes a self-contained desk under ``e6fc2f12/``: one landing page, one page per
in-scope sport, a match list, a market explorer, the High-confidence page with its
predictions, an analysis page, a Flagged-for-Review page, a sources page and a
methodology page. No external asset, font, script or backend call is used, so the
pages work from GitHub Pages under ``/OLBG1/e6fc2f12/`` and from a local file
server alike.
"""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "e6fc2f12"
ROOT = Path(__file__).resolve().parents[1]
WORDS = {0: "No", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
         7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve"}

OUT = ROOT / "e6fc2f12"

SPORTS = [
    ("tennis", "Tennis", 3),
    ("basketball", "Basketball", 4),
    ("golf", "Golf", 5),
    ("cricket", "Cricket", 7),
    ("snooker", "Snooker", 8),
    ("rugby-union", "Rugby Union", 9),
    ("rugby-league", "Rugby League", 10),
    ("baseball", "Baseball", 12),
    ("ice-hockey", "Ice Hockey", 13),
    ("motor-racing", "Motor Racing", 14),
    ("darts", "Darts", 15),
    ("handball", "Handball", 22),
    ("volleyball", "Volleyball", 23),
    ("aussie-rules", "Australian Rules", 22),
    ("esports", "eSports", 23),
    ("gaelic-football", "Gaelic Football", 25),
    ("greyhounds", "Greyhounds", 31),
]
SPORT_NAME = {s: n for s, n, _ in SPORTS}

# OLBG sport ids are the values reverse-engineered in the repository's taxonomy
# record; they are used only for the discovery link, never as evidence.
OLBG_URL = {
    "tennis": "https://www.olbg.com/betting-tips/Tennis/3",
    "basketball": "https://www.olbg.com/betting-tips/Basketball/4",
    "golf": "https://www.olbg.com/betting-tips/Golf/5",
    "cricket": "https://www.olbg.com/betting-tips/Cricket/7",
    "snooker": "https://www.olbg.com/betting-tips/Snooker/8",
    "rugby-union": "https://www.olbg.com/betting-tips/Rugby_Union/9",
    "rugby-league": "https://www.olbg.com/betting-tips/Rugby_League/10",
    "baseball": "https://www.olbg.com/betting-tips/Baseball/12",
    "ice-hockey": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
    "motor-racing": "https://www.olbg.com/betting-tips/Motor_Racing/14",
    "darts": "https://www.olbg.com/betting-tips/Darts/15",
    "handball": "https://www.olbg.com/betting-tips/Handball/22",
    "volleyball": "https://www.olbg.com/betting-tips/Volleyball/23",
    "aussie-rules": "https://www.olbg.com/betting-tips/Aussie_Rules/22",
    "esports": "https://www.olbg.com/betting-tips/eSports/23",
    "gaelic-football": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
    "greyhounds": "https://www.olbg.com/betting-tips/Greyhounds/31",
}


def e(x) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def money(a) -> str:
    if a is None:
        return "—"
    return f"+{a}" if a > 0 else str(a)


def pct(p) -> str:
    return f"{100 * p:.1f}%"


def tier_badge(t: str) -> str:
    cls = {"High": "t-high", "Medium": "t-medium", "Low": "t-low"}.get(t, "t-low")
    return f'<span class="badge {cls}">{e(t)}</span>'


class Site:
    def __init__(self) -> None:
        self.fixtures = json.loads((DATA / "fixtures.json").read_text())
        self.markets = json.loads((DATA / "markets.json").read_text())
        self.sources = json.loads((DATA / "sources.json").read_text())
        self.coverage = json.loads((DATA / "coverage.json").read_text())
        self.model = json.loads((DATA / "model.json").read_text())
        self.predictions = json.loads((DATA / "predictions.json").read_text())
        self.ratings = json.loads((DATA / "ratings.json").read_text())
        self.src = {s["id"]: s for s in self.sources}
        self.by_fixture: dict[str, list] = {}
        for row in self.markets:
            self.by_fixture.setdefault(row["fixture_id"], []).append(row)
        self.counts = self.model["counts"]
        self.generated = self.model["generated_at"]

    # ---------------------------------------------------------------- helpers
    def source_links(self, ids: list[str]) -> str:
        out, seen = [], set()
        for sid in ids:
            s = self.src.get(sid)
            if not s or s["publisher"] in seen:
                continue
            seen.add(s["publisher"])
            out.append(f'<a href="{e(s["url"])}" rel="noopener">{e(s["publisher"])}</a>')
        return " · ".join(out) if out else "—"

    def fixture_when(self, f: dict) -> str:
        if f.get("starts_at_utc"):
            dt = datetime.fromisoformat(f["starts_at_utc"].replace("Z", "+00:00"))
            return dt.strftime("%d %b %Y · %H:%M UTC")
        return f.get("starts_local") or "date unpublished"

    def nav(self, active: str, prefix: str = "") -> str:
        items = [
            ("index.html", "Overview"),
            ("matches.html", "Match list"),
            ("markets.html", "Market explorer"),
            ("high-confidence.html", "High-confidence picks"),
            ("sports.html", "All sports"),
            ("analysis.html", "Analysis"),
            ("flagged.html", "Flagged for review"),
            ("sources.html", "Sources"),
            ("methodology.html", "Methodology"),
        ]
        links = "".join(
            f'<a class="nav-link{" active" if href == active else ""}" href="{prefix}{href}">'
            f"{e(label)}</a>"
            for href, label in items
        )
        return f'<nav class="nav" aria-label="Desk sections">{links}</nav>'

    def page(self, title: str, active: str, body: str, prefix: str = "",
             subtitle: str = "") -> str:
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'">
<title>{e(title)} · OLBG research desk</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="brand"><span class="mark" aria-hidden="true"></span>
    <span><strong>OLBG research desk</strong><small>independent · evidence-first</small></span>
  </div>
  <div class="meta"><span class="dot"></span> snapshot {e(self.generated)}</div>
</header>
{self.nav(active, prefix)}
<main id="main">
<header class="page-head">
  <p class="eyebrow">Session e6fc2f12-olbg1 · lines originated, not copied</p>
  <h1>{e(title)}</h1>
  {f'<p class="lede">{subtitle}</p>' if subtitle else ''}
</header>
{body}
</main>
<footer class="foot">
  <p>Independent research. Not affiliated with OLBG. No guarantee, no bookmaker quote and no
  staking advice. Prices shown are this desk's own model estimates, never observed market
  prices. 18+.</p>
  <p class="muted">Snapshot generated {e(self.generated)} · model {e(self.model["model_version"])}</p>
</footer>
</body>
</html>
"""

    # ---------------------------------------------------------------- pages
    def write_index(self) -> None:
        c = self.counts
        high = [r for r in self.markets if r["tier"] == "High"]
        high.sort(key=lambda r: -r["model_probability"])
        rows = []
        for slug, name, _ in SPORTS:
            sc = self.coverage["sport_counts"].get(slug, {"fixtures": 0, "priced": 0, "markets": 0})
            h = sum(1 for r in high if r["sport"] == slug)
            status = ("priced" if sc["priced"] else "fixtures, unpriced" if sc["fixtures"] else "no verified fixture")
            rows.append(
                f'<tr><td><a href="sports/{slug}.html">{e(name)}</a></td>'
                f'<td class="num">{sc["fixtures"]}</td><td class="num">{sc["priced"]}</td>'
                f'<td class="num">{sc["markets"]}</td><td class="num">{h}</td>'
                f'<td>{e(status)}</td>'
                f'<td><a href="{e(OLBG_URL[slug])}" rel="noopener">OLBG hub</a></td></tr>'
            )
        picks = "".join(
            f'<li><a href="high-confidence.html#{e(r["fixture_id"])}">'
            f'<strong>{e(r["selection"])}</strong> <span class="muted">{e(r["market"])}</span>'
            f'</a><span class="price">{money(r["american"])}</span>'
            f'<span class="muted small">{e(r["fixture_id"])}</span></li>'
            for r in high[:6]
        )
        body = f"""
<div class="kpis">
  <div class="kpi"><span>Fixtures verified</span><strong>{c["fixtures"]}</strong>
    <small>{c["fixtures_priced"]} priced · {c["fixtures_unpriced"]} unpriced</small></div>
  <div class="kpi"><span>Markets originated</span><strong>{c["markets"]}</strong>
    <small>winner, handicap, totals, team totals</small></div>
  <div class="kpi"><span>High-confidence picks</span><strong>{c["outcomes_by_tier"]["High"]}</strong>
    <small>70.0%–71.4% fair band</small></div>
  <div class="kpi"><span>Official sources</span><strong>{len(self.sources)}</strong>
    <small>league, governing body, tour</small></div>
</div>

<div class="notice">
  <strong>Read this first.</strong> This desk covers {c["fixtures"]} fixtures it could verify from an
  official source in a single session. {WORDS[len(self.coverage["unverified_sports"])]} in-scope sports
  are listed but carry no fixture,
  because their official pages could not be read; they are published as gaps with the attempted
  URL and the reason on the <a href="flagged.html">Flagged for review</a> page. Nothing here is a
  bookmaker price: every number is this desk's own fair estimate. There is no out-of-sample
  calibration yet, so a "High" label is a model statement at 70–71%, not a guaranteed outcome.
</div>

<section class="panel">
  <h2>Coverage by sport</h2>
  <p class="muted">In-scope categories only. Soccer, American football, boxing, UFC/MMA, hurling,
  horse racing, cycling and specials are excluded by the brief and are not listed.</p>
  <div class="scroll"><table class="grid">
    <thead><tr><th>Sport</th><th>Fixtures</th><th>Priced</th><th>Markets</th><th>High</th>
    <th>Status</th><th>Discovery</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
</section>

<div class="cols">
  <section class="panel">
    <h2>Highest-confidence selections</h2>
    <ul class="picks">{picks}</ul>
    <p><a class="button" href="high-confidence.html">All {c["outcomes_by_tier"]["High"]} High picks with predictions →</a></p>
  </section>
  <section class="panel">
    <h2>How the price is built</h2>
    <p>Win rates are Beta(2,2)-shrunk and combined with log5. Hockey and baseball totals and
    handicaps come from independent Poisson scoring counts; rugby union handicaps use a normal
    approximation with a disclosed standard deviation. Fair decimal is 1/p with no margin, and no
    market quote is invented.</p>
    <p><a class="button" href="methodology.html">Read the method →</a></p>
  </section>
</div>
"""
        self._write(OUT / "index.html", self.page(
            "The match research desk", "index.html", body,
            subtitle="Verified fixtures, independently originated lines, and an explicit list of "
                     "what this session could not verify."))

    def write_matches(self) -> None:
        rows = []
        for f in sorted(self.fixtures, key=lambda x: (x.get("starts_at_utc") or x.get("starts_date") or "", x["id"])):
            pick = f.get("primary_pick")
            pick_cell = "—"
            if pick:
                pick_cell = f'{e(pick["selection"])} <span class="price">{money(pick["american"])}</span> {tier_badge(pick["tier"])}'
            rows.append(
                f'<tr data-sport="{e(f["sport"])}" data-tier="{e(pick["tier"]) if pick else "none"}">'
                f'<td class="nowrap">{e(self.fixture_when(f))}</td>'
                f'<td><a href="sports/{e(f["sport"])}.html">{e(SPORT_NAME.get(f["sport"], f["sport"]))}</a></td>'
                f'<td>{e(f["competition"])}<br><span class="muted small">{e(f["round"])}</span></td>'
                f'<td><strong>{e(f["home"])}</strong><br><span class="muted">v</span> {e(f["away"])}</td>'
                f'<td>{e(f["venue"] or "—")}</td>'
                f'<td>{pick_cell}</td>'
                f'<td class="num">{f["markets_priced"]}</td>'
                f'<td class="small">{self.source_links(f["source_ids"])}</td></tr>'
            )
        body = f"""
<p class="lede">Every row below was read from an official league, tour or governing-body page in
this session. Where a start time or a rating could not be read, the field is blank and the row is
flagged rather than filled in.</p>
<div class="notice tight"><strong>{self.counts["fixtures"]} fixtures</strong> ·
{self.counts["fixtures_priced"]} priced · {self.counts["fixtures_unpriced"]} published unpriced
with a stated reason.</div>
<div class="scroll"><table class="grid sortable" id="matchTable">
<thead><tr><th>When</th><th>Sport</th><th>Competition</th><th>Fixture</th><th>Venue</th>
<th>Model pick</th><th>Markets</th><th>Official source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="muted small">The model pick is the higher-probability side of the match-winner market.
Its tier is the same rule used everywhere on this desk: High needs a probability above 70% and a
fair price inside the −250…+10000 band.</p>
"""
        self._write(OUT / "matches.html", self.page(
            "Match list", "matches.html", body,
            subtitle="All fixtures this session could verify, with the model's pick on each."))

    def write_markets(self) -> None:
        rows = []
        for row in sorted(self.markets, key=lambda r: (r["sport"], r["fixture_id"], r["market"],
                                                       r["selection"])):
            rows.append(
                f'<tr data-sport="{e(row["sport"])}" data-tier="{e(row["tier"])}">'
                f'<td><a href="sports/{e(row["sport"])}.html">{e(SPORT_NAME.get(row["sport"], row["sport"]))}</a></td>'
                f'<td class="small">{e(row["fixture_id"])}</td>'
                f'<td>{e(row["market"])}</td>'
                f'<td>{e(row["selection"])}</td>'
                f'<td class="num">{"" if row["line"] is None else e(row["line"])}</td>'
                f'<td class="num">{pct(row["model_probability"])}</td>'
                f'<td class="num">{row["fair_decimal"]:.3f}</td>'
                f'<td class="num price">{money(row["american"])}</td>'
                f'<td>{"yes" if row["fair_price_in_band"] else "no"}</td>'
                f'<td>{tier_badge(row["tier"])}</td></tr>'
            )
        body = f"""
<p class="lede">Every market this desk originated, including the ones it deliberately does not
recommend. There are no observed bookmaker prices in this repository; the American column is the
fair price implied by the model, with no margin applied.</p>
<div class="filterbar">
  <label>Sport <select id="sportFilter"><option value="">All</option>
    {''.join(f'<option value="{e(s)}">{e(SPORT_NAME[s])}</option>' for s, _, _ in SPORTS)}
  </select></label>
  <label>Tier <select id="tierFilter"><option value="">All</option>
    <option value="High">High</option><option value="Medium">Medium</option>
    <option value="Low">Low</option></select></label>
  <span class="muted small" id="rowCount"></span>
</div>
<div class="scroll tall"><table class="grid" id="marketTable">
<thead><tr><th>Sport</th><th>Fixture</th><th>Market</th><th>Selection</th><th>Line</th>
<th>Model p</th><th>Fair decimal</th><th>Fair American</th><th>In brief band</th>
<th>Tier</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="muted small">A market is High-eligible only where both sides' inputs were read from
official data <em>and</em> the model is defensible for that market. MLB markets are capped below
High for that reason. "In brief band" is the literal test from the brief: is the fair price between
−250 and +10000? A 75% favourite is priced about −300, so it fails that test and is graded Medium
even though it is a stronger favourite than any High pick on this page.</p>
<script src="assets/app.js"></script>
"""
        self._write(OUT / "markets.html", self.page(
            "Market explorer", "markets.html", body,
            subtitle=f'{self.counts["markets"]} originated markets across winner, handicap, totals '
                     "and team-total lines."))

    def write_high(self) -> None:
        cards = []
        for row in sorted(self.predictions, key=lambda r: -r["model_probability"]):
            f = next((x for x in self.fixtures if x["id"] == row["fixture_id"]), None)
            if not f:
                continue
            cards.append(f"""
<article class="card" id="{e(row["fixture_id"])}">
  <header class="card-head">
    <div>
      <p class="eyebrow">{e(SPORT_NAME.get(row["sport"], row["sport"]))} · {e(f["competition"])} · {e(f["round"])}</p>
      <h2>{e(f["home"])} v {e(f["away"])}</h2>
      <p class="muted small">{e(self.fixture_when(f))}{" · " + e(f["venue"]) if f.get("venue") else ""}</p>
    </div>
    {tier_badge(row["tier"])}
  </header>
  <dl class="facts">
    <div><dt>Selection</dt><dd><strong>{e(row["selection"])}</strong></dd></div>
    <div><dt>Market</dt><dd>{e(row["market"])}{"" if row["line"] is None else " · line " + e(row["line"])}</dd></div>
    <div><dt>Model probability</dt><dd>{pct(row["model_probability"])}</dd></div>
    <div><dt>Fair price</dt><dd>{money(row["american"])} <span class="muted">({row["fair_decimal"]:.3f} decimal)</span></dd></div>
  </dl>
  <p class="prediction">{e(row["prediction"])}</p>
  <p class="small muted">Model: {e(row["model_note"])}. Official source:
  {self.source_links(f["source_ids"])}.</p>
</article>""")
        body = f"""
<p class="lede">{len(self.predictions)} selections clear the desk's High bar: a model probability
above 70% <em>and</em> a fair price inside the brief's −250…+10000 window. Each has a prediction
written for that fixture alone, naming the selection and citing only facts read from an official
page in this session.</p>
<div class="notice">
  <strong>The band is narrow by construction.</strong> At a 70% probability the fair price is −233;
  at −250 it is 71.4%. A High pick is therefore a genuine favourite in the 70.0–71.4% slice, never
  an odds-on shot priced at −500. That arithmetic is why this desk refuses to label a −600
  favourite "High": the brief's own price window cannot express it.
</div>
{''.join(cards)}
<div class="panel">
  <h2>What is deliberately missing from these write-ups</h2>
  <p>No individual-player claim appears here. Naming a scorer, a goalie or a starting pitcher
  requires a player-level official read that this session did not perform, and inventing one was
  not an option. The gap is recorded on the <a href="flagged.html">Flagged for review</a> page. The
  same applies to injury news, line-ups and travel: all blank, all disclosed.</p>
</div>
"""
        self._write(OUT / "high-confidence.html", self.page(
            "High-confidence picks", "high-confidence.html", body,
            subtitle="Unique, fixture-specific predictions for every High selection."))

    def write_sports_index(self) -> None:
        rows = []
        for slug, name, _ in SPORTS:
            sc = self.coverage["sport_counts"].get(slug, {"fixtures": 0, "priced": 0, "markets": 0})
            status = "Priced" if sc["priced"] else ("Fixtures verified, unpriced" if sc["fixtures"] else "No verified fixture")
            rows.append(
                f'<tr><td><a href="sports/{slug}.html"><strong>{e(name)}</strong></a></td>'
                f'<td class="num">{sc["fixtures"]}</td><td class="num">{sc["priced"]}</td>'
                f'<td class="num">{sc["markets"]}</td><td>{e(status)}</td>'
                f'<td><a href="{e(OLBG_URL[slug])}" rel="noopener">OLBG hub</a></td></tr>'
            )
        body = f"""
<p class="lede">Seventeen in-scope categories, each with its own page. A category with no verified
fixture is still published, with the official page that was read and the reason it produced no
row, so the gap is visible rather than implied.</p>
<div class="scroll"><table class="grid">
<thead><tr><th>Category</th><th>Fixtures</th><th>Priced</th><th>Markets</th><th>Status</th>
<th>Discovery</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p class="muted small">OLBG hub links are discovery routes, not evidence. No OLBG figure is used as
a fixture fact anywhere on this desk.</p>
"""
        self._write(OUT / "sports.html", self.page("All sports", "sports.html", body))

    def write_sport_page(self, slug: str, name: str) -> None:
        fixtures = [f for f in self.fixtures if f["sport"] == slug]
        gap = next((g for g in self.coverage["unverified_sports"] if g[0] == slug), None)

        if not fixtures:
            reason = gap[3] if gap else "No fixture could be verified from an official source."
            url = gap[2] if gap else ""
            body = f"""
<div class="notice warn"><strong>No fixture published for {e(name)}.</strong> {e(reason)}</div>
<div class="panel">
  <h2>What was read</h2>
  <p>{f'<a href="{e(url)}" rel="noopener">{e(url)}</a>' if url else '—'}</p>
  <p class="muted">The same gap is listed on the <a href="../flagged.html">Flagged for review</a>
  page with the attempted official URL. A category is left empty rather than filled with an
  unverified listing.</p>
  <p><a class="button" href="{e(OLBG_URL[slug])}" rel="noopener">OLBG discovery hub (not evidence)</a></p>
</div>
"""
            self._write(OUT / "sports" / f"{slug}.html",
                        self.page(f"{name}", "sports.html", body, prefix="../",
                                  subtitle="Category page"))
            return

        frows = []
        for f in sorted(fixtures, key=lambda x: (x.get("starts_at_utc") or x.get("starts_date") or "")):
            pick = f.get("primary_pick")
            pick_cell = (f'{e(pick["selection"])} <span class="price">{money(pick["american"])}</span> '
                         f'{tier_badge(pick["tier"])}') if pick else "unpriced"
            frows.append(
                f'<tr><td class="nowrap">{e(self.fixture_when(f))}</td>'
                f'<td><strong>{e(f["home"])}</strong> v {e(f["away"])}</td>'
                f'<td>{e(f["competition"])}<br><span class="muted small">{e(f["round"])}</span></td>'
                f'<td>{e(f["venue"] or "—")}</td><td>{pick_cell}</td>'
                f'<td class="num">{f["markets_priced"]}</td>'
                f'<td class="small">{self.source_links(f["source_ids"])}</td></tr>'
            )

        ladders = []
        for f in sorted(fixtures, key=lambda x: (x.get("starts_at_utc") or x.get("starts_date") or "")):
            rows = self.by_fixture.get(f["id"], [])
            if not rows:
                continue
            by_market: dict[str, list] = {}
            for r in rows:
                by_market.setdefault(r["market"], []).append(r)
            blocks = []
            for market, items in by_market.items():
                items.sort(key=lambda r: (r["line"] if r["line"] is not None else 0,
                                          r["selection"]))
                trs = "".join(
                    f'<tr><td>{e(r["selection"])}</td><td class="num">{pct(r["model_probability"])}</td>'
                    f'<td class="num">{r["fair_decimal"]:.3f}</td>'
                    f'<td class="num price">{money(r["american"])}</td>'
                    f'<td>{tier_badge(r["tier"])}</td></tr>' for r in items)
                blocks.append(f'<h4>{e(market)}</h4><table class="grid tight"><thead><tr>'
                              f'<th>Selection</th><th>p</th><th>Decimal</th><th>American</th>'
                              f'<th>Tier</th></tr></thead><tbody>{trs}</tbody></table>')
            ladders.append(
                f'<details><summary>{e(f["home"])} v {e(f["away"])} '
                f'<span class="muted small">· {len(rows)} markets</span></summary>'
                f'{"".join(blocks)}</details>')

        sc = self.coverage["sport_counts"].get(slug, {})
        body = f"""
<div class="kpis small">
  <div class="kpi"><span>Fixtures</span><strong>{sc.get("fixtures", 0)}</strong></div>
  <div class="kpi"><span>Priced</span><strong>{sc.get("priced", 0)}</strong></div>
  <div class="kpi"><span>Markets</span><strong>{sc.get("markets", 0)}</strong></div>
  <div class="kpi"><span>High picks</span><strong>{sum(1 for r in self.predictions if r["sport"] == slug)}</strong></div>
</div>
<section class="panel">
  <h2>Fixtures</h2>
  <div class="scroll"><table class="grid">
  <thead><tr><th>When</th><th>Fixture</th><th>Competition</th><th>Venue</th><th>Model pick</th>
  <th>Markets</th><th>Official source</th></tr></thead><tbody>{''.join(frows)}</tbody></table></div>
</section>
<section class="panel">
  <h2>Originated markets</h2>
  <p class="muted">Every rung this desk priced, including the ones it does not recommend. Open a
  fixture to see the full ladder.</p>
  {''.join(ladders) if ladders else '<p class="muted">No priced markets for this category.</p>'}
</section>
"""
        self._write(OUT / "sports" / f"{slug}.html",
                    self.page(name, "sports.html", body, prefix="../",
                              subtitle=f"{sc.get('fixtures', 0)} verified fixtures in this category."))

    def write_analysis(self) -> None:
        tiers = self.counts["outcomes_by_tier"]
        high = [r for r in self.markets if r["tier"] == "High"]
        in_band = [r for r in self.markets if r["fair_price_in_band"]]
        excluded_favourites = [r for r in self.markets
                               if r["model_probability"] > 0.7143 and r["model_probability"] > 0.5]
        excluded_favourites.sort(key=lambda r: -r["model_probability"])
        top_outside = "".join(
            f'<tr><td>{e(r["selection"])}</td><td>{e(r["market"])}</td>'
            f'<td class="num">{pct(r["model_probability"])}</td>'
            f'<td class="num price">{money(r["american"])}</td>'
            f'<td class="muted small">{e(r["fixture_id"])}</td></tr>'
            for r in excluded_favourites[:8])
        sport_rows = "".join(
            f'<tr><td>{e(SPORT_NAME.get(s, s))}</td><td class="num">{v["fixtures"]}</td>'
            f'<td class="num">{v["priced"]}</td><td class="num">{v["markets"]}</td>'
            f'<td class="num">{sum(1 for r in high if r["sport"] == s)}</td></tr>'
            for s, v in sorted(self.coverage["sport_counts"].items())
        )
        body = f"""
<div class="kpis">
  <div class="kpi"><span>High</span><strong>{tiers["High"]}</strong><small>p &gt; 70% and inside the band</small></div>
  <div class="kpi"><span>Medium</span><strong>{tiers["Medium"]}</strong><small>p ≥ 65%</small></div>
  <div class="kpi"><span>Low</span><strong>{tiers["Low"]}</strong><small>everything else</small></div>
  <div class="kpi"><span>Fair price in band</span><strong>{len(in_band)}</strong><small>of {self.counts["markets"]} markets</small></div>
</div>

<section class="panel">
  <h2>Finding 1 — the brief's band and the brief's threshold cannot both be generous</h2>
  <p>At a probability of 70% the fair decimal price is 1.4286, which is −233 American. At −250 the
  implied probability is 71.43%. So the instruction "greater than 70% chance to win" combined with
  "odds between −250 and +10000" defines a window of roughly 1.4 percentage points. This desk
  applies both conditions literally, which is why {tiers["High"]} selections qualify rather than
  several hundred. The alternative would be to label heavy favourites "High" and quote them at
  prices the band forbids — the failure mode several earlier desks in this repository were flagged
  for.</p>
  <div class="scroll"><table class="grid">
  <thead><tr><th>Selection</th><th>Market</th><th>Model p</th><th>Fair price</th><th>Fixture</th></tr></thead>
  <tbody>{top_outside}</tbody></table></div>
  <p class="muted small">The rows above are <em>stronger</em> favourites than every High pick, and
  are deliberately excluded: at these prices the band cannot be expressed. They remain available in
  the <a href="markets.html">market explorer</a> as Medium or Low.</p>
</section>

<section class="panel">
  <h2>Finding 2 — coverage is uneven and the desk says so</h2>
  <p>Broad, machine-readable official feeds (NHL, MLB, URC) produced {self.counts["fixtures_priced"]}
  priced fixtures. Client-rendered or consent-walled official pages produced no fixture at all for
  eleven categories. Publishing an unpriced fixture list would have been easy; it would also have
  been guesswork about start times and participants, so those categories are gaps instead.</p>
  <div class="scroll"><table class="grid">
  <thead><tr><th>Sport</th><th>Fixtures</th><th>Priced</th><th>Markets</th><th>High</th></tr></thead>
  <tbody>{sport_rows}</tbody></table></div>
</section>

<section class="panel">
  <h2>Finding 3 — the model is honest about what it is not</h2>
  <ul class="list">
    <li>No home advantage is inserted, because no official home/road split was read. That biases
    estimates toward 50%, which suppresses High labels rather than manufacturing them.</li>
    <li>Beta(2,2) shrinkage stops a 3-0 start reading as a 100% team. It is a disclosed choice, not
    a sourced fact.</li>
    <li>Independent Poisson goals is a stated approximation. Real hockey goals are not independent
    and empty-net effects are not modelled.</li>
    <li>The rugby-union margin and total use a normal approximation with standard deviations of
    13.5 and 16.0 points. Those two numbers are assumptions and are labelled as such everywhere
    they appear.</li>
    <li>No market quote exists in this dataset. "Edge" is therefore unknowable here, and the desk
    does not claim any.</li>
  </ul>
</section>

<section class="panel">
  <h2>Finding 4 — where the earlier desks and this one disagree</h2>
  <p>A prior desk in this repository carried a High pick on the New York Islanders moneyline at a
  fair −250. Recomputing from the same official NHL records read today (Islanders 5-3-1, 27 goals
  for, 19 against) does not reproduce a 70%+ win probability for that fixture in this model. The
  discrepancy is a modelling difference — different shrinkage and no home edge here — not proof
  that either number is wrong. It is recorded on the <a href="flagged.html">Flagged</a> page as an
  open review item rather than silently overwritten.</p>
</section>
"""
        self._write(OUT / "analysis.html", self.page(
            "Analysis and findings", "analysis.html", body,
            subtitle="What the numbers say, including the parts that argue against the desk's own labels."))

    def write_flagged(self) -> None:
        gaps = "".join(
            f'<tr><td><strong>{e(name)}</strong></td><td class="small">{e(reason)}</td>'
            f'<td><a href="{e(url)}" rel="noopener">{e(url)}</a></td></tr>'
            for slug, name, url, reason in self.coverage["unverified_sports"]
        )
        unpriced = [f for f in self.fixtures if not f["priced"]]
        urows = "".join(
            f'<tr><td>{e(SPORT_NAME.get(f["sport"], f["sport"]))}</td>'
            f'<td>{e(f["home"])} v {e(f["away"])}</td>'
            f'<td>{e(f.get("starts_local") or self.fixture_when(f))}</td>'
            f'<td class="small">{e(f.get("reason", ""))}</td>'
            f'<td class="small">{self.source_links(f["source_ids"])}</td></tr>'
            for f in unpriced
        )
        body = f"""
<div class="notice warn">
  <strong>Flagged items do not block publication.</strong> They are published here, with the source
  link used, so every gap and every irregularity can be reviewed after the site is live.
</div>

<section class="panel">
  <h2>1. In-scope sports with no verified fixture ({len(self.coverage["unverified_sports"])})</h2>
  <p class="muted">Each of these official pages was fetched in this session. The reason column is
  the specific failure, not a general caveat.</p>
  <div class="scroll"><table class="grid">
  <thead><tr><th>Sport</th><th>Why no row is published</th><th>Official page read</th></tr></thead>
  <tbody>{gaps}</tbody></table></div>
</section>

<section class="panel">
  <h2>2. Verified fixtures published without a price ({len(unpriced)})</h2>
  <p class="muted">The fixture, date and venue are official. The price is absent because the input
  a defensible model needs was not read. A number would have looked tidier and meant less.</p>
  <div class="scroll"><table class="grid">
  <thead><tr><th>Sport</th><th>Fixture</th><th>When (as published)</th><th>Reason</th>
  <th>Official source</th></tr></thead><tbody>{urows}</tbody></table></div>
</section>

<section class="panel">
  <h2>3. Field-level gaps inside priced rows</h2>
  <div class="scroll"><table class="grid">
  <thead><tr><th>Item</th><th>What is missing</th><th>Why it matters</th></tr></thead>
  <tbody>
  <tr><td>Dallas Stars goals</td><td>Goals for and against, in 9 games</td>
      <td>The team summary payload was truncated at that club when read, so its totals markets are
      withheld rather than back-filled from memory. Moneyline prices still stand: they need only
      the win-loss record, which was read.</td></tr>
  <tr><td>URC kick-off timezone</td><td>The page states every time is "Local" and names no zone</td>
      <td>Converting to UTC would be an inference. The published local time is reproduced verbatim
      and no UTC field is shown.</td></tr>
  <tr><td>RLWC, snooker, F1 times</td><td>Timezones not stated on the source pages</td>
      <td>Same rule: reproduced as published, never converted.</td></tr>
  <tr><td>Player-level context</td><td>No starting goalie, pitcher, line-up or individual form read</td>
      <td>Every High prediction therefore cites team form and game results only. No player name is
      asserted anywhere in the write-ups.</td></tr>
  <tr><td>Market quotes</td><td>No bookmaker price was read anywhere</td>
      <td>The desk originates prices; it cannot claim value, edge or availability.</td></tr>
  <tr><td>Calibration</td><td>No out-of-sample scoring of this model yet</td>
      <td>"High" is a fixed threshold rule, not a calibrated frequency. Treat 70% as an estimate.</td></tr>
  </tbody></table></div>
</section>

<section class="panel">
  <h2>4. Open review item against an earlier desk</h2>
  <p>A previous session published a High pick on the New York Islanders moneyline at a fair −250.
  With the official records read today (5-3-1, 27 goals for, 19 against in nine games) this desk's
  model puts that fixture materially nearer 60%. Neither number is a fact about the future; the
  difference is shrinkage and the absence of a home edge here. Recorded for review, not
  overwritten.</p>
</section>

<section class="panel">
  <h2>5. Model-risk register</h2>
  <ul class="list">
    <li><strong>Small samples.</strong> NHL clubs have played 7–12 games. Shrinkage mitigates this
    but cannot remove it.</li>
    <li><strong>Poisson independence.</strong> Correlated scoring, empty-net goals and
    overtime rules are not modelled. Totals near the ladder's edges are the most exposed.</li>
    <li><strong>Rugby standard deviations.</strong> 13.5 (margin) and 16.0 (total) are assumptions.
    Handicap and total prices move a lot if they are wrong.</li>
    <li><strong>No home edge.</strong> Home teams are, if anything, underrated by this desk.</li>
    <li><strong>Stale-by-design snapshot.</strong> Every price is tied to a stated read time. A
    later lineup or injury changes the picture and this snapshot will not know.</li>
  </ul>
</section>
"""
        self._write(OUT / "flagged.html", self.page(
            "Flagged for review", "flagged.html", body,
            subtitle="Every gap, every withheld number and every assumption, with the source used."))

    def write_sources(self) -> None:
        rows = "".join(
            f'<tr><td><strong>{e(s["name"])}</strong><br><span class="muted small">{e(s["kind"])}</span></td>'
            f'<td>{e(s["publisher"])}</td>'
            f'<td><a href="{e(s["url"])}" rel="noopener">{e(s["url"])}</a></td>'
            f'<td class="small">{e(s["used_for"])}</td>'
            f'<td class="nowrap small">{e(s["read_at"])}</td></tr>'
            for s in self.sources
        )
        body = f"""
<p class="lede">Every value on this desk traces to one of these {len(self.sources)} official
reads. Media outlets, aggregators and betting sites are not used as evidence anywhere.</p>
<div class="scroll"><table class="grid">
<thead><tr><th>Source</th><th>Publisher</th><th>URL</th><th>Used for</th><th>Read at (UTC)</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="muted small">A read timestamp means the payload was fetched by this session. It does not
mean the league guarantees the value is still current: a published schedule is not proof of match
status, and records change with every game.</p>
"""
        self._write(OUT / "sources.html", self.page(
            "Sources and evidence", "sources.html", body,
            subtitle="The official reads this snapshot is built from."))

    def write_methodology(self) -> None:
        body = f"""
<section class="panel">
  <h2>The rule set</h2>
  <ol class="list">
    <li><strong>Discovery.</strong> OLBG's sport hubs are used only to know which categories exist
    and to link back for comparison. No OLBG number is treated as a fixture fact.</li>
    <li><strong>Verification.</strong> Every fixture, record and start time comes from the league,
    tour or governing body. If a field is not in the payload it stays blank and the row is flagged.</li>
    <li><strong>Origination.</strong> The desk prices its own lines. It never copies a bookmaker
    price, and it publishes no "market quote" field it did not read.</li>
    <li><strong>Grading.</strong> High = model probability above 70% and a fair price inside
    −250…+10000. Medium = 65% or better. Low = everything else.</li>
    <li><strong>Publication.</strong> Every High selection carries a unique prediction of at least
    30 words naming the selection, the participants, the current form and the recent results.</li>
  </ol>
</section>

<section class="panel">
  <h2>Mathematics</h2>
  <div class="formula">strength = (wins + 2) / (games + 4)              # Beta(2,2) shrinkage</div>
  <div class="formula">p(A beats B) = pA(1−pB) / [pA(1−pB) + pB(1−pA)]   # log5, no home edge</div>
  <div class="formula">λ_home = ½(goals_for_home/G + goals_against_away/G)   # Poisson rate</div>
  <div class="formula">fair decimal = 1/p ; American = −100p/(1−p) for p ≥ 0.5</div>
  <p>Handicaps are derived from the same scoring distributions: the probability that the home side
  wins by two or more goals is the Poisson mass where home goals minus away goals is at least two.
  Rugby union uses a normal approximation on the expected margin and total, with standard
  deviations stated in the risk register.</p>
</section>

<section class="panel">
  <h2>What "High" does and does not mean</h2>
  <p>It means the model puts the selection in the 70.0–71.4% slice and the price the brief asks for
  can express that. It does not mean the desk has beaten a market: no market price was read, so no
  edge was measured. It does not mean the model is calibrated: no out-of-sample scoring has been
  run on this model version. The label is a threshold, transparently applied.</p>
</section>

<section class="panel">
  <h2>Exclusions</h2>
  <p>Soccer, American football, boxing, UFC/MMA, hurling, horse racing, cycling and specials are
  excluded by the brief and appear nowhere in this desk. The GAA check found only a Shinty-Hurling
  International, an excluded sport, so Gaelic football has no in-scope fixture in this window.</p>
</section>

<section class="panel">
  <h2>Reproduction</h2>
  <div class="formula">python3 scripts/se6fc2f12_model.py      # writes data/e6fc2f12/*.json</div>
  <div class="formula">python3 scripts/se6fc2f12_build_site.py # writes e6fc2f12/*.html</div>
  <div class="formula">python3 scripts/se6fc2f12_validate.py   # gates the release</div>
  <p class="muted">The curated inputs are in <code>scripts/se6fc2f12_data.py</code>; each block
  names the URL it was transcribed from.</p>
</section>
"""
        self._write(OUT / "methodology.html", self.page(
            "Methodology", "methodology.html", body,
            subtitle="The exact arithmetic, the assumptions, and the parts that are guesses labelled as guesses."))

    # ---------------------------------------------------------------- output
    def exports(self) -> None:
        OUT.mkdir(parents=True, exist_ok=True)
        fx = OUT / "fixtures.csv"
        with fx.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["fixture_id", "sport", "competition", "round", "home", "away",
                        "starts_at_utc", "starts_local", "venue", "priced", "markets",
                        "pick", "pick_american", "pick_tier", "source_urls"])
            for f in self.fixtures:
                pick = f.get("primary_pick") or {}
                w.writerow([f["id"], f["sport"], f["competition"], f["round"], f["home"],
                            f["away"], f.get("starts_at_utc") or "", f.get("starts_local") or "",
                            f.get("venue") or "", f["priced"], f["markets_priced"],
                            pick.get("selection", ""), pick.get("american", ""),
                            pick.get("tier", ""),
                            " ".join(self.src[s]["url"] for s in f["source_ids"] if s in self.src)])
        mk = OUT / "markets.csv"
        with mk.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["fixture_id", "sport", "market", "selection", "line",
                        "model_probability", "fair_decimal", "fair_american", "tier"])
            for r in self.markets:
                w.writerow([r["fixture_id"], r["sport"], r["market"], r["selection"],
                            "" if r["line"] is None else r["line"],
                            r["model_probability"], r["fair_decimal"], r["american"], r["tier"]])

    def _write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def build(self) -> None:
        OUT.mkdir(parents=True, exist_ok=True)
        self.exports()
        self.write_index()
        self.write_matches()
        self.write_markets()
        self.write_high()
        self.write_sports_index()
        for slug, name, _ in SPORTS:
            self.write_sport_page(slug, name)
        self.write_analysis()
        self.write_flagged()
        self.write_sources()
        self.write_methodology()
        pages = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*.html"))
        print(f"built {len(pages)} pages")
        for p in pages:
            print("  ", p)


if __name__ == "__main__":
    Site().build()
