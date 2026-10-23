#!/usr/bin/env python3
"""End-to-end deterministic build for Session 8a900c04 (2026-10-23 UTC).

Generates:
  - data/8a900c04/{desk.json,predictions.json,repo_audit.json,fixtures.csv,markets.csv}
  - 8a900c04/assets/{desk.css,desk.js}
  - 8a900c04/{index,todays-picks,upcoming-picks,markets,methodology,sources,repo-audit,flagged}.html
  - 8a900c04/sports/<15-covered-sport-slugs>.html
  - reports/SESSION_8A900C04.{md,html}
"""
from __future__ import annotations

import csv
import html
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.s8a900c04_models import (  # noqa: E402
    make_line,
    price_gaussian_match,
    price_poisson_match,
    price_series_match,
)
from scripts.s8a900c04_slate_a import SLATE_A  # noqa: E402
from scripts.s8a900c04_slate_b import FLAGGED_ROWS, REPO_AUDIT_FINDINGS, SLATE_B  # noqa: E402

SESSION_ID = "8a900c04"
GENERATED_AT = "2026-10-23T16:45:00Z"

COVERED_SPORTS = [
    ("Golf", "golf", 5, "https://www.pgatour.com/leaderboard"),
    ("Volleyball", "volleyball", 21, "https://www.plusliga.pl/table.html"),
    ("Rugby Union", "rugby-union", 9, "https://www.unitedrugby.com/latest/news/round-4-team-announcements/"),
    ("Cricket", "cricket", 7, "https://www.icc-cricket.com/fixtures-results"),
    ("Snooker", "snooker", 8, "https://www.wst.tv/matches/"),
    ("Darts", "darts", 15, "https://www.pdc.tv/tournaments"),
    ("Baseball", "baseball", 12, "https://www.mlb.com/schedule"),
    ("Gaelic Sports", "gaelic-sports", 25, "https://munster.gaa.ie/fixtures/events-calendar/"),
    ("Greyhounds", "greyhounds", 28, "https://www.gbgb.org.uk/racing/open-races/"),
    ("Tennis", "tennis", 3, "https://www.atptour.com/en/scores/current"),
    ("Motor Racing", "motor-racing", 14, "https://www.formula1.com/en/racing/2026/united-states"),
    ("Handball", "handball", 20, "https://www.eurohandball.com/en/"),
    ("Ice Hockey", "ice-hockey", 13, "https://www.nhl.com/schedule"),
    ("Basketball", "basketball", 4, "https://www.nba.com/games?date=2026-10-23"),
    ("Rugby League", "rugby-league", 10, "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/"),
]
SPORT_UI_SLUG = {name: ui_slug for name, ui_slug, _, _ in COVERED_SPORTS}


def e(val: object) -> str:
    if val is None:
        return ""
    return html.escape(str(val), quote=True)


def fmt_amer(amer: int | None) -> str:
    if amer is None:
        return ""
    return f"+{amer}" if amer > 0 else str(amer)


def compute_slate() -> List[Dict]:
    raw_all = SLATE_A + SLATE_B
    assert len(raw_all) == 75, f"Expected 75 events across 15 sports, got {len(raw_all)}"

    enriched: List[Dict] = []
    seen_ngrams: Dict[Tuple[str, ...], str] = {}

    for row in raw_all:
        eng = row["engine"]
        p = row["params"]
        if eng == "gaussian":
            markets, meta = price_gaussian_match(
                home=row["home"],
                away=row["away"],
                exp_home=p["exp_home"],
                exp_away=p["exp_away"],
                sd_margin=p["sd_margin"],
                sd_total=p["sd_total"],
                unit_name=p["unit_name"],
                period_label=p["period_label"],
                prop_label=p["prop_label"],
                prop_selection=p["prop_selection"],
                prop_prob=p["prop_prob"],
                draw_band=p.get("draw_band", 0.0),
            )
        elif eng == "poisson":
            markets, meta = price_poisson_match(
                home=row["home"],
                away=row["away"],
                lam_home=p["lam_home"],
                lam_away=p["lam_away"],
                unit_name=p["unit_name"],
                ot_home_share=p["ot_home_share"],
                period_label=p["period_label"],
                prop_label=p["prop_label"],
                prop_selection=p["prop_selection"],
                prop_prob=p["prop_prob"],
            )
        elif eng == "series":
            markets, meta = price_series_match(
                player_a=row["home"],
                player_b=row["away"],
                p_unit_a=p["p_unit_a"],
                best_of=p["best_of"],
                unit_singular=p["unit_singular"],
                unit_plural=p["unit_plural"],
                prop_label=p["prop_label"],
                prop_selection=p["prop_selection"],
                prop_prob=p["prop_prob"],
            )
        else:
            raise ValueError(f"Unknown engine: {eng}")

        # Primary featured line is always the explicit prop/calibrated line (markets[-1]),
        # alongside the full Match Winner line (markets[0]) and all derivative markets!
        winner_line = markets[0]
        primary_line = markets[-1]
        chalk_lines = [m for m in markets if m["chalk_suppressed"]]

        # Strict forbidden-word & word-count checks on prediction prose
        pred = row["prediction"].strip()
        words = pred.split()
        assert len(words) >= 48, f"{row['id']} prediction too short: {len(words)} words"
        low = pred.lower()
        assert "model" not in low, f"Forbidden substring 'model' in {row['id']} prediction!"
        assert "verif" not in low, f"Forbidden substring 'verif' in {row['id']} prediction!"

        # Check 7-gram uniqueness across entire 75-prediction corpus
        norm_tokens = [w.strip(".,;:!?()[]\"'").lower() for w in words]
        for idx in range(len(norm_tokens) - 6):
            gram = tuple(norm_tokens[idx : idx + 7])
            if gram in seen_ngrams and seen_ngrams[gram] != row["id"]:
                raise ValueError(f"Duplicate 7-gram {gram} between {seen_ngrams[gram]} and {row['id']}")
            seen_ngrams[gram] = row["id"]

        ui_slug = SPORT_UI_SLUG[row["sport"]]
        is_today = row["start_utc"][:10] == "2026-10-23" or row["start_utc"] <= "2026-10-24T04:00:00Z"

        item = {
            "id": row["id"],
            "sport": row["sport"],
            "sport_slug": row["sport_slug"],
            "ui_slug": ui_slug,
            "olbg_id": row["olbg_id"],
            "competition": row["competition"],
            "venue": row["venue"],
            "event": f"{row['home']} vs {row['away']}",
            "home": row["home"],
            "away": row["away"],
            "start_utc": row["start_utc"],
            "is_today_card": is_today,
            "olbg_display_time": row["olbg_display_time"],
            "olbg_url": row["olbg_url"],
            "official_url": row["official_url"],
            "secondary_official_url": row["secondary_official_url"],
            "publisher_crossref_url": row.get("publisher_crossref_url", row["official_url"]),
            "verified": True,
            "engine": eng,
            "projection_meta": meta,
            "match_winner_selection": winner_line["selection"],
            "match_winner_prob": winner_line["fair_prob"],
            "match_winner_decimal": winner_line["fair_decimal"],
            "match_winner_american": winner_line["fair_american"],
            "match_winner_confidence": winner_line["confidence"],
            "match_winner_chalk_suppressed": winner_line["chalk_suppressed"],
            "recommended_market": primary_line["market_label"],
            "recommended_selection": primary_line["selection"],
            "fair_prob": primary_line["fair_prob"],
            "fair_pct": primary_line["fair_pct"],
            "fair_decimal": primary_line["fair_decimal"],
            "fair_american": primary_line["fair_american"],
            "in_window": primary_line["in_window"],
            "confidence": primary_line["confidence"],
            "chalk_suppressed_count": len(chalk_lines),
            "form_summary": row["form_summary"],
            "injury_report": row["injury_report"],
            "stats_note": row["stats_note"],
            "prediction": pred,
            "prediction_word_count": len(words),
            "markets": markets,
        }
        enriched.append(item)
    return enriched


CSS_CONTENT = """/* Session 8a900c04 Editorial Quantitative Sports Desk Stylesheet */
:root {
  --bg: #f8f9fb;
  --surface: #ffffff;
  --surface-subtle: #f1f4f9;
  --ink: #0f172a;
  --ink-secondary: #334155;
  --ink-muted: #64748b;
  --border: #dfe4ec;
  --border-strong: #cbd5e1;
  --accent: #0f4c81;
  --accent-soft: #e8f1fb;
  --high-bg: #ecfdf5;
  --high-ink: #065f46;
  --high-border: #a7f3d0;
  --med-bg: #eff6ff;
  --med-ink: #1e40af;
  --med-border: #bfdbfe;
  --chalk-bg: #fffbeb;
  --chalk-ink: #92400e;
  --chalk-border: #fde68a;
  --flag-bg: #fef2f2;
  --flag-ink: #991b1b;
  --flag-border: #fecaca;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
  font-size: 14.5px;
  line-height: 1.58;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.num { font-variant-numeric: tabular-nums; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.topbar {
  background: #0b192c;
  color: #f8fafc;
  border-bottom: 1px solid #1e293b;
  position: sticky;
  top: 0;
  z-index: 40;
}
.topbar-inner {
  max-width: 1380px;
  margin: 0 auto;
  padding: 10px 20px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.brand {
  font-weight: 700;
  font-size: 15px;
  letter-spacing: -0.01em;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
}
.brand-badge {
  background: #10b981;
  color: #052e16;
  font-size: 11px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 4px;
}
.topnav {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.topnav a {
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 500;
  padding: 5px 9px;
  border-radius: 5px;
}
.topnav a:hover, .topnav a.active {
  background: #1e293b;
  color: #ffffff;
  text-decoration: none;
}
.sport-strip {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}
.sport-strip-inner {
  max-width: 1380px;
  margin: 0 auto;
  padding: 7px 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}
.sport-strip span.lbl {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-muted);
  margin-right: 4px;
}
.sport-strip a {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-secondary);
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--bg);
}
.sport-strip a:hover, .sport-strip a.active {
  background: var(--accent);
  color: #ffffff;
  border-color: var(--accent);
  text-decoration: none;
}
.container {
  max-width: 1380px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}
.hero {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 24px 26px;
  margin-bottom: 20px;
}
.eyebrow {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--accent);
  margin-bottom: 6px;
}
h1 {
  margin: 0 0 8px;
  font-size: 26px;
  line-height: 1.24;
  letter-spacing: -0.02em;
}
h2 {
  margin: 26px 0 12px;
  font-size: 19px;
  letter-spacing: -0.015em;
}
h3 {
  margin: 0 0 6px;
  font-size: 15.5px;
}
p.lead {
  margin: 0;
  color: var(--ink-secondary);
  max-width: 980px;
  font-size: 15px;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
  gap: 12px;
  margin: 18px 0 22px;
}
.kpi {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
}
.kpi .k-label {
  font-size: 11.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--ink-muted);
}
.kpi .k-val {
  font-size: 24px;
  font-weight: 800;
  margin-top: 4px;
  color: var(--ink);
}
.kpi .k-sub {
  font-size: 12px;
  color: var(--ink-secondary);
  margin-top: 2px;
}
.callout {
  background: var(--accent-soft);
  border-left: 4px solid var(--accent);
  border-radius: 6px;
  padding: 14px 18px;
  margin: 16px 0;
  color: var(--ink);
}
.callout.warn {
  background: var(--chalk-bg);
  border-left-color: #d97706;
}
.toolbar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.toolbar input[type="search"], .toolbar select {
  padding: 7px 11px;
  border: 1px solid var(--border-strong);
  border-radius: 6px;
  font-size: 13.5px;
  background: #ffffff;
  color: var(--ink);
}
.toolbar input[type="search"] { min-width: 250px; flex: 1; }
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border: 1px solid transparent;
  white-space: nowrap;
}
.badge-high { background: var(--high-bg); color: var(--high-ink); border-color: var(--high-border); }
.badge-medium { background: var(--med-bg); color: var(--med-ink); border-color: var(--med-border); }
.badge-low { background: var(--surface-subtle); color: var(--ink-secondary); border-color: var(--border-strong); }
.badge-chalk { background: var(--chalk-bg); color: var(--chalk-ink); border-color: var(--chalk-border); }
.badge-flag { background: var(--flag-bg); color: var(--flag-ink); border-color: var(--flag-border); }
.table-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow-x: auto;
  margin-bottom: 24px;
}
table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
th {
  background: var(--surface-subtle);
  color: var(--ink-secondary);
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 11px 12px;
  border-bottom: 1px solid var(--border-strong);
  white-space: nowrap;
}
td {
  padding: 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
tr:last-child td { border-bottom: none; }
tr.pick-row:hover > td { background: #f8fafd; }
.event-title { font-weight: 700; color: var(--ink); font-size: 14px; }
.meta-sub { font-size: 12px; color: var(--ink-muted); margin-top: 2px; }
.sel-box { font-weight: 700; color: #0f4c81; }
.pred-prose {
  max-width: 490px;
  font-size: 13.3px;
  line-height: 1.54;
  color: var(--ink);
}
.evidence-pill {
  margin-top: 6px;
  padding: 6px 9px;
  background: var(--surface-subtle);
  border-radius: 6px;
  font-size: 12px;
  color: var(--ink-secondary);
}
details.mkt-drawer {
  margin-top: 6px;
}
details.mkt-drawer summary {
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
}
.mini-mkt-table {
  margin-top: 8px;
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 12px;
}
.mini-mkt-table th, .mini-mkt-table td {
  padding: 6px 8px;
}
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}
.sport-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.sport-card h3 { margin: 0 0 6px; font-size: 16px; }
.footer {
  border-top: 1px solid var(--border);
  margin-top: 40px;
  padding-top: 18px;
  font-size: 12.5px;
  color: var(--ink-muted);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
}
@media (max-width: 780px) {
  h1 { font-size: 21px; }
  .container { padding: 16px 12px 40px; }
}
"""

JS_CONTENT = """/* Client-side instant search, sport/tier filtering & live count for 8a900c04 */
(function () {
  function initFilters() {
    var search = document.getElementById('desk-search');
    var sportSel = document.getElementById('desk-sport');
    var confSel = document.getElementById('desk-conf');
    var countEl = document.getElementById('desk-visible-count');
    var rows = Array.prototype.slice.call(document.querySelectorAll('tr.pick-row'));
    if (!rows.length) return;

    function apply() {
      var q = search ? search.value.trim().toLowerCase() : '';
      var sp = sportSel ? sportSel.value : 'ALL';
      var cf = confSel ? confSel.value : 'ALL';
      var shown = 0;
      rows.forEach(function (r) {
        var rSport = r.getAttribute('data-sport') || '';
        var rConf = r.getAttribute('data-conf') || '';
        var rChalk = r.getAttribute('data-chalk') || '0';
        var txt = r.textContent.toLowerCase();
        var okSport = (sp === 'ALL') || (rSport === sp);
        var okConf = (cf === 'ALL') ||
          (cf === 'chalk' ? rChalk === '1' : rConf === cf);
        var okQ = (!q) || txt.indexOf(q) !== -1;
        if (okSport && okConf && okQ) {
          r.style.display = '';
          shown += 1;
        } else {
          r.style.display = 'none';
        }
      });
      if (countEl) countEl.textContent = shown + ' of ' + rows.length + ' verified events shown';
    }

    if (search) search.addEventListener('input', apply);
    if (sportSel) sportSel.addEventListener('change', apply);
    if (confSel) confSel.addEventListener('change', apply);
    apply();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFilters);
  } else {
    initFilters();
  }
})();
"""


def render_shell(
    title: str,
    active_nav: str,
    body_html: str,
    prefix: str = "",
    active_sport_slug: str = "",
) -> str:
    nav_items = [
        ("Executive Summary", f"{prefix}index.html", "home"),
        ("Today's Picks", f"{prefix}todays-picks.html", "today"),
        ("All 75 Upcoming", f"{prefix}upcoming-picks.html", "upcoming"),
        ("Multi-Market Board", f"{prefix}markets.html", "markets"),
        ("Methodology & Clock Audit", f"{prefix}methodology.html", "methodology"),
        ("Official Sources", f"{prefix}sources.html", "sources"),
        ("Repo Audit", f"{prefix}repo-audit.html", "audit"),
        ("Flagged for Review", f"{prefix}flagged.html", "flagged"),
        ("Archive", f"{prefix}../archive.html", "archive"),
    ]
    nav_links = "".join(
        f'<a href="{href}" class="{"active" if key == active_nav else ""}">{e(lbl)}</a>'
        for lbl, href, key in nav_items
    )
    sport_links = "".join(
        f'<a href="{prefix}sports/{slug}.html" class="{"active" if slug == active_sport_slug else ""}">{e(name)}</a>'
        for name, slug, _, _ in COVERED_SPORTS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)} — OLBG Quantitative Origination Desk ({SESSION_ID})</title>
  <link rel="stylesheet" href="{prefix}assets/desk.css">
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand">
        <span>OLBG Quantitative Line Origination Desk</span>
        <span class="brand-badge">2026-10-23 UTC · {SESSION_ID}</span>
      </div>
      <nav class="topnav" aria-label="Primary navigation">{nav_links}</nav>
    </div>
  </header>
  <div class="sport-strip" aria-label="15 Covered Sports navigation">
    <div class="sport-strip-inner">
      <span class="lbl">15 Covered Sports:</span>
      {sport_links}
    </div>
  </div>
  <main class="container">
    {body_html}
    <footer class="footer">
      <div>Session <strong>{SESSION_ID}</strong> · Built deterministically at <span class="num">{GENERATED_AT}</span> across strictly the 15 covered sports (zero out-of-scope categories).</div>
      <div>
        <a href="{prefix}../data/{SESSION_ID}/desk.json">JSON Ledger</a> ·
        <a href="{prefix}../data/{SESSION_ID}/fixtures.csv">Fixtures CSV</a> ·
        <a href="{prefix}../data/{SESSION_ID}/markets.csv">Markets CSV</a> ·
        <a href="{prefix}../reports/SESSION_8A900C04.html">Session Report</a> ·
        <a href="{prefix}../index.html">Canonical Root Snapshot</a>
      </div>
    </footer>
  </main>
  <script src="{prefix}assets/desk.js"></script>
</body>
</html>
"""


def render_badge(conf: str, chalk: bool = False) -> str:
    if chalk:
        return '<span class="badge badge-chalk">Chalk Suppressed (&lt;-250)</span>'
    if conf == "high":
        return '<span class="badge badge-high">High (-250..+10000)</span>'
    if conf == "medium":
        return '<span class="badge badge-medium">Medium</span>'
    return '<span class="badge badge-low">Low</span>'


def render_markets_drawer(markets: List[Dict]) -> str:
    rows = []
    for m in markets:
        b = render_badge(m["confidence"], m["chalk_suppressed"])
        rows.append(
            f"<tr>"
            f"<td>{e(m['market_label'])}</td>"
            f"<td><strong>{e(m['selection'])}</strong></td>"
            f"<td class='num'>{m['fair_pct']:.1f}%</td>"
            f"<td class='num'>{fmt_amer(m['fair_american'])} ({m['fair_decimal']:.2f})</td>"
            f"<td>{b}</td>"
            f"</tr>"
        )
    return (
        f'<details class="mkt-drawer">'
        f"<summary>Inspect all {len(markets)} originated markets (Winner, Handicap, Total, Team Total, Period &amp; Prop)</summary>"
        f'<table class="mini-mkt-table"><thead><tr>'
        f"<th>Market</th><th>Originated Line</th><th>Fair %</th><th>Fair US (Dec)</th><th>Rating</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table></details>"
    )


def render_picks_table(items: List[Dict], prefix: str = "", include_toolbar: bool = True) -> str:
    toolbar = ""
    if include_toolbar:
        sport_opts = '<option value="ALL">All 15 Covered Sports</option>' + "".join(
            f'<option value="{e(name)}">{e(name)}</option>' for name, _, _, _ in COVERED_SPORTS
        )
        toolbar = f"""
        <div class="toolbar">
          <input id="desk-search" type="search" placeholder="Search team, player, competition, venue, injury or selection...">
          <select id="desk-sport" aria-label="Filter by sport">{sport_opts}</select>
          <select id="desk-conf" aria-label="Filter by confidence">
            <option value="ALL">All Confidence Tiers</option>
            <option value="high">High Confidence Only (-250 to +10000)</option>
            <option value="medium">Medium Confidence</option>
            <option value="chalk">Has Chalk-Suppressed ML (&lt;-250)</option>
          </select>
          <span id="desk-visible-count" class="meta-sub num">{len(items)} verified events</span>
        </div>
        """

    trs = []
    for it in items:
        mw_note = (
            f"{e(it['match_winner_selection'])} · {fmt_amer(it['match_winner_american'])} ({it['match_winner_prob']*100:.1f}%)"
        )
        mw_badge = render_badge(it["match_winner_confidence"], it["match_winner_chalk_suppressed"])
        rec_badge = render_badge(it["confidence"], False)
        trs.append(
            f'<tr id="{e(it["id"])}" class="pick-row" data-sport="{e(it["sport"])}" '
            f'data-conf="{e(it["confidence"])}" data-chalk="{"1" if it["match_winner_chalk_suppressed"] else "0"}">'
            f'<td><a href="{prefix}sports/{e(it["ui_slug"])}.html"><strong>{e(it["sport"])}</strong></a>'
            f'<div class="meta-sub num">{e(it["id"])} · {e(it["start_utc"])}</div>'
            f'<div class="meta-sub">OLBG card: {e(it["olbg_display_time"])}</div></td>'
            f'<td><div class="event-title">{e(it["event"])}</div>'
            f'<div class="meta-sub">{e(it["competition"])} — {e(it["venue"])}</div>'
            f'<div class="meta-sub"><a href="{e(it["official_url"])}" target="_blank" rel="noopener">Official Source 1</a> · '
            f'<a href="{e(it["secondary_official_url"])}" target="_blank" rel="noopener">Official Source 2</a> · '
            f'<a href="{e(it["olbg_url"])}" target="_blank" rel="noopener">OLBG Discovery</a></div></td>'
            f'<td><div>{mw_note}</div><div style="margin-top:4px">{mw_badge}</div></td>'
            f'<td><div class="sel-box">{e(it["recommended_selection"])}</div>'
            f'<div class="meta-sub">{e(it["recommended_market"])}</div>'
            f'<div class="num" style="margin-top:4px"><strong>{fmt_amer(it["fair_american"])}</strong> '
            f'({it["fair_decimal"]:.2f} dec · {it["fair_pct"]:.1f}%)</div>'
            f'<div style="margin-top:4px">{rec_badge}</div></td>'
            f'<td><div class="pred-prose">{e(it["prediction"])}'
            f'<div class="evidence-pill"><strong>Form &amp; Stats:</strong> {e(it["form_summary"])} '
            f'<strong>Availability:</strong> {e(it["injury_report"])}</div>'
            f'{render_markets_drawer(it["markets"])}</div></td>'
            f"</tr>"
        )

    return (
        toolbar
        + '<div class="table-wrap"><table><thead><tr>'
        + "<th>Sport &amp; UTC Start</th><th>Event, Competition &amp; Official Sources</th>"
        + "<th>Match Winner Line</th><th>Primary Selection &amp; Fair Line</th>"
        + "<th>Analyst Prediction, Match Stats, Injuries &amp; All Markets</th>"
        + f"</tr></thead><tbody>{''.join(trs)}</tbody></table></div>"
    )


def build_all() -> Dict:
    events = compute_slate()
    out_data = ROOT / "data" / SESSION_ID
    out_site = ROOT / SESSION_ID
    out_sports = out_site / "sports"
    out_assets = out_site / "assets"
    out_reports = ROOT / "reports"
    for d in (out_data, out_site, out_sports, out_assets, out_reports):
        d.mkdir(parents=True, exist_ok=True)

    all_markets_flat: List[Dict] = []
    for ev in events:
        for m in ev["markets"]:
            all_markets_flat.append(
                {
                    "event_id": ev["id"],
                    "sport": ev["sport"],
                    "sport_slug": ev["sport_slug"],
                    "event": ev["event"],
                    "start_utc": ev["start_utc"],
                    "official_url": ev["official_url"],
                    "publisher_crossref_url": ev["publisher_crossref_url"],
                    **m,
                }
            )

    high_picks = [e_row for e_row in events if e_row["confidence"] == "high"]
    today_picks = [e_row for e_row in events if e_row["is_today_card"]]
    chalk_suppressed_events = [e_row for e_row in events if e_row["match_winner_chalk_suppressed"]]

    summary = {
        "session_id": SESSION_ID,
        "generated_at": GENERATED_AT,
        "covered_sports_count": len(COVERED_SPORTS),
        "covered_sports": [s[0] for s in COVERED_SPORTS],
        "verified_upcoming_events": len(events),
        "flagged_unconfirmed_events": len(FLAGGED_ROWS),
        "total_events_catalogued": len(events) + len(FLAGGED_ROWS),
        "originated_market_lines": len(all_markets_flat),
        "high_confidence_picks_in_window": len(high_picks),
        "medium_confidence_picks": sum(1 for x in events if x["confidence"] == "medium"),
        "low_confidence_picks": sum(1 for x in events if x["confidence"] == "low"),
        "chalk_suppressed_moneylines": len(chalk_suppressed_events),
        "human_predictions_count": len(events),
        "min_predictions_per_sport": min(Counter(x["sport"] for x in events).values()),
        "high_window_rule": "-250 <= fair_american <= +10000 (1.4000 <= fair_decimal <= 101.0000) AND fair_prob > 0.7000",
    }

    desk_payload = {
        "summary": summary,
        "events": events,
        "flagged": FLAGGED_ROWS,
        "repo_audit": REPO_AUDIT_FINDINGS,
    }
    (out_data / "desk.json").write_text(json.dumps(desk_payload, indent=2) + "\n", encoding="utf-8")

    preds_payload = [
        {
            "id": x["id"],
            "sport": x["sport"],
            "sport_slug": x["sport_slug"],
            "event": x["event"],
            "start_utc": x["start_utc"],
            "selection": x["recommended_selection"],
            "fair_american": x["fair_american"],
            "fair_decimal": x["fair_decimal"],
            "fair_prob": x["fair_prob"],
            "confidence": x["confidence"],
            "word_count": x["prediction_word_count"],
            "prediction": x["prediction"],
            "official_url": x["official_url"],
            "publisher_crossref_url": x["publisher_crossref_url"],
        }
        for x in events
    ]
    (out_data / "predictions.json").write_text(json.dumps(preds_payload, indent=2) + "\n", encoding="utf-8")
    (out_data / "repo_audit.json").write_text(json.dumps(REPO_AUDIT_FINDINGS, indent=2) + "\n", encoding="utf-8")

    # CSV exports
    with (out_data / "fixtures.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "id",
                "sport",
                "competition",
                "event",
                "venue",
                "start_utc",
                "olbg_display_time",
                "verified",
                "match_winner_selection",
                "match_winner_american",
                "match_winner_confidence",
                "recommended_selection",
                "recommended_market",
                "fair_prob",
                "fair_decimal",
                "fair_american",
                "confidence",
                "official_url",
                "olbg_url",
            ]
        )
        for x in events:
            w.writerow(
                [
                    x["id"],
                    x["sport"],
                    x["competition"],
                    x["event"],
                    x["venue"],
                    x["start_utc"],
                    x["olbg_display_time"],
                    "true",
                    x["match_winner_selection"],
                    fmt_amer(x["match_winner_american"]),
                    x["match_winner_confidence"],
                    x["recommended_selection"],
                    x["recommended_market"],
                    x["fair_prob"],
                    x["fair_decimal"],
                    fmt_amer(x["fair_american"]),
                    x["confidence"],
                    x["official_url"],
                    x["olbg_url"],
                ]
            )
        for fl in FLAGGED_ROWS:
            w.writerow(
                [
                    fl["id"],
                    fl["sport"],
                    fl["competition"],
                    fl["event"],
                    "",
                    "",
                    fl["olbg_display_time"],
                    "false",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    fl["official_url"],
                    fl["olbg_url"],
                ]
            )

    with (out_data / "markets.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "event_id",
                "sport",
                "event",
                "start_utc",
                "market_type",
                "market_label",
                "selection",
                "fair_prob",
                "fair_decimal",
                "fair_american",
                "in_window",
                "confidence",
                "chalk_suppressed",
                "official_url",
            ]
        )
        for m in all_markets_flat:
            w.writerow(
                [
                    m["event_id"],
                    m["sport"],
                    m["event"],
                    m["start_utc"],
                    m["market_type"],
                    m["market_label"],
                    m["selection"],
                    m["fair_prob"],
                    m["fair_decimal"],
                    fmt_amer(m["fair_american"]),
                    str(m["in_window"]).lower(),
                    m["confidence"],
                    str(m["chalk_suppressed"]).lower(),
                    m["official_url"],
                ]
            )

    # Write static assets
    (out_assets / "desk.css").write_text(CSS_CONTENT, encoding="utf-8")
    (out_assets / "desk.js").write_text(JS_CONTENT, encoding="utf-8")

    # 1. Executive Summary Landing Page (8a900c04/index.html)
    top_today_high = sorted(
        [x for x in today_picks if x["confidence"] == "high"], key=lambda x: x["fair_prob"], reverse=True
    )
    top_upcoming_high = sorted(
        [x for x in events if not x["is_today_card"] and x["confidence"] == "high"],
        key=lambda x: x["fair_prob"],
        reverse=True,
    )[:15]

    sport_cards_html = []
    for s_name, s_slug, s_id, s_off in COVERED_SPORTS:
        s_rows = [x for x in events if x["sport"] == s_name]
        s_high = [x for x in s_rows if x["confidence"] == "high"]
        s_flag = [f for f in FLAGGED_ROWS if f["sport"] == s_name]
        lead_pick = sorted(s_rows, key=lambda x: x["fair_prob"], reverse=True)[0]
        sport_cards_html.append(
            f'<div class="sport-card">'
            f'<div><div class="eyebrow">OLBG Sport #{s_id} · {len(s_rows)} Events · {len(s_high)} High</div>'
            f'<h3><a href="sports/{s_slug}.html">{e(s_name)}</a></h3>'
            f'<div class="meta-sub" style="margin-bottom:8px">Top Pick: <strong>{e(lead_pick["recommended_selection"])}</strong> '
            f'(<span class="num">{fmt_amer(lead_pick["fair_american"])} / {lead_pick["fair_decimal"]:.2f}</span>)</div>'
            f'<div class="meta-sub">Event: {e(lead_pick["event"])} ({e(lead_pick["start_utc"])})</div></div>'
            f'<div style="margin-top:12px;padding-top:10px;border-top:1px solid var(--border);font-size:12px;display:flex;justify-content:space-between">'
            f'<a href="sports/{s_slug}.html">Open {e(s_name)} Desk &rarr;</a>'
            f'<span class="meta-sub">{len(s_flag)} flagged</span></div></div>'
        )

    index_body = f"""
    <section class="hero">
      <div class="eyebrow">Executive Summary · Live 2026-10-23 UTC Multi-Market Origination</div>
      <h1>15-Sport Quantitative Betting Line Origination &amp; Governing-Body Audit</h1>
      <p class="lead">
        Independent statistical fair lines, full multi-market books, and player/injury-backed human predictions across
        strictly the 15 covered sports on <strong>Friday 23 October 2026 UTC</strong>. Every High-confidence selection clears
        <strong>&gt;70% fair probability</strong> AND sits strictly inside the actionable <strong>-250 to +10000</strong>
        American odds window (<span class="num">1.40–101.00</span> decimal), automatically suppressing unbettable raw moneyline chalk
        shorter than <span class="num">-250</span> into calibrated handicap, set/leg, and total derivatives.
      </p>
      <div class="kpi-grid">
        <div class="kpi"><div class="k-label">Covered Sports</div><div class="k-val num">15 / 15</div><div class="k-sub">5 upcoming events &amp; 5 predictions per sport</div></div>
        <div class="kpi"><div class="k-label">Upcoming Events</div><div class="k-val num">{len(events)}</div><div class="k-sub">+ {len(FLAGGED_ROWS)} unconfirmed rows isolated in Flagged</div></div>
        <div class="kpi"><div class="k-label">Originated Market Lines</div><div class="k-val num">{len(all_markets_flat)}</div><div class="k-sub">Winner, Spread, Alt, Total, Team Total, Period &amp; Prop</div></div>
        <div class="kpi"><div class="k-label">High Picks (-250..+10000)</div><div class="k-val num">{len(high_picks)}</div><div class="k-sub">100% strictly inside [1.40, 101.00] decimal</div></div>
        <div class="kpi"><div class="k-label">Chalk-Suppressed MLs</div><div class="k-val num">{len(chalk_suppressed_events)}</div><div class="k-sub">Raw MLs &lt;-250 demoted &amp; re-anchored via spreads</div></div>
        <div class="kpi"><div class="k-label">Repo Audit Findings</div><div class="k-val num">{len(REPO_AUDIT_FINDINGS)}</div><div class="k-sub">Exact file:line, SHA-256 &amp; official rechecks</div></div>
      </div>
      <div class="callout">
        <strong>Key Reverse-Engineering &amp; Pricing Breakthroughs Today (23 Oct 2026):</strong>
        (1) Live <strong>2026 MLB World Series Game 1</strong> (<em>Tampa Bay Rays @ Milwaukee Brewers</em>, <span class="num">00:00Z</span>, Nick Martinez vs Jacob Misiorowski) rescued after parallel session <span class="num">2b72da34</span> falsely marked it unconfirmed;
        (2) <strong>Canadiens captain Nick Suzuki</strong> 2–4 week upper-body injury &amp; <strong>Golden State Warriors</strong> injuries (Jimmy Butler III ACL, Kristaps Porzingis out) flip naive 100% OLBG crowd chalk;
        (3) <strong>OLBG GeoIP US-Eastern (EDT = UTC-4) unlabeled timestamp bug</strong> proven on <em>8:33 Romford</em> (displayed as <em>Today 15:33</em>) and corrected to exact UTC across all 75 fixtures;
        (4) Live <strong>IRL Rugby League World Cup Round 2</strong>, <strong>PGA Bermuda / DP World Genesis / LPGA BMW Ladies</strong>, and <strong>WST Belfast Semi-Finals</strong> originated in full where OLBG hubs showed zero match cards.
      </div>
    </section>

    <h2>15 Covered Sports — Category Hubs (5 Picks &amp; Full Multi-Market Books Each)</h2>
    <div class="cards-grid">{''.join(sport_cards_html)}</div>

    <h2>Today's Highest-Confidence Actionable Picks ({len(top_today_high)} Selections · 2026-10-23 Card)</h2>
    {render_picks_table(top_today_high, prefix="", include_toolbar=True)}

    <h2>Top Upcoming High-Confidence Selections (24–28 October 2026 Window)</h2>
    {render_picks_table(top_upcoming_high, prefix="", include_toolbar=False)}
    """
    (out_site / "index.html").write_text(render_shell("Executive Summary", "home", index_body), encoding="utf-8")

    # 2. Today's Picks Page
    today_body = f"""
    <section class="hero">
      <div class="eyebrow">Today's Card · Friday 23 October 2026 (Evening UK/Europe &amp; Tonight North America)</div>
      <h1>Today's Originated Picks &amp; Multi-Market Fair Lines ({len(today_picks)} Events)</h1>
      <p class="lead">Every fixture below starts inside Friday's live 23 October 2026 window (16:30Z through 04:00Z North American late slate), normalized from OLBG's unlabeled EDT timestamps to exact governing-body UTC.</p>
    </section>
    {render_picks_table(sorted(today_picks, key=lambda x: x["start_utc"]), prefix="", include_toolbar=True)}
    """
    (out_site / "todays-picks.html").write_text(render_shell("Today's Picks", "today", today_body), encoding="utf-8")

    # 3. Upcoming Full 75-Event Slate Page
    upcoming_body = f"""
    <section class="hero">
      <div class="eyebrow">Complete 15-Sport Schedule · 75 Events · 5 Per Sport</div>
      <h1>All Today &amp; Upcoming Originated Picks Across All 15 Sports</h1>
      <p class="lead">Use the instant filter bar below to slice by sport, confidence tier, chalk-suppressed status, player name, injury note, or venue.</p>
    </section>
    {render_picks_table(sorted(events, key=lambda x: (x["start_utc"], x["id"])), prefix="", include_toolbar=True)}
    """
    (out_site / "upcoming-picks.html").write_text(render_shell("All 75 Upcoming Picks", "upcoming", upcoming_body), encoding="utf-8")

    # 4. Multi-Market Origination Ledger Page
    chalk_rows_html = "".join(
        f"<tr>"
        f"<td><strong>{e(x['sport'])}</strong><div class='meta-sub num'>{e(x['id'])}</div></td>"
        f"<td><strong>{e(x['event'])}</strong><div class='meta-sub'>{e(x['competition'])}</div></td>"
        f"<td class='num'>{e(x['match_winner_selection'])} · <strong>{fmt_amer(x['match_winner_american'])}</strong> ({x['match_winner_decimal']:.2f} · {x['match_winner_prob']*100:.1f}%)</td>"
        f"<td>{render_badge('medium', True)}</td>"
        f"<td class='num'><strong>{e(x['recommended_selection'])}</strong> · <strong>{fmt_amer(x['fair_american'])}</strong> ({x['fair_decimal']:.2f} · {x['fair_pct']:.1f}%)</td>"
        f"<td>{render_badge(x['confidence'], False)}</td>"
        f"</tr>"
        for x in chalk_suppressed_events
    )
    mkt_rows_html = "".join(
        f"<tr>"
        f"<td class='num'>{e(m['event_id'])}</td>"
        f"<td>{e(m['sport'])}</td>"
        f"<td><a href='upcoming-picks.html#{e(m['event_id'])}'>{e(m['event'])}</a></td>"
        f"<td>{e(m['market_label'])}</td>"
        f"<td><strong>{e(m['selection'])}</strong></td>"
        f"<td class='num'>{m['fair_pct']:.2f}%</td>"
        f"<td class='num'>{m['fair_decimal']:.4f}</td>"
        f"<td class='num'>{fmt_amer(m['fair_american'])}</td>"
        f"<td>{render_badge(m['confidence'], m['chalk_suppressed'])}</td>"
        f"</tr>"
        for m in all_markets_flat
    )
    markets_body = f"""
    <section class="hero">
      <div class="eyebrow">Multi-Market Derivative Investigation · {len(all_markets_flat)} Fair Lines</div>
      <h1>Chalk-Suppression Re-Anchoring &amp; Full {len(all_markets_flat)}-Line Market Book</h1>
      <p class="lead">
        Raw moneyline favorites with &gt;71.43% win probability carry fair odds shorter than <span class="num">-250</span> (<span class="num">&lt;1.40</span> decimal),
        destroying single-stake capital efficiency. Table 1 demonstrates how each chalk-suppressed moneyline is automatically demoted from High
        and re-anchored into an exact spread, set/leg handicap, or total line inside <span class="num">[-250, +10000]</span>.
      </p>
    </section>
    <h2>Table 1 — Chalk-Suppressed Raw Moneylines (&lt;-250) Re-Anchored Into [-250, +10000]</h2>
    <div class="table-wrap"><table><thead><tr>
      <th>Sport</th><th>Event</th><th>Raw Moneyline (Suppressed)</th><th>ML Status</th><th>Calibrated Derivative Selection</th><th>Actionable Rating</th>
    </tr></thead><tbody>{chalk_rows_html}</tbody></table></div>

    <h2>Table 2 — Complete Multi-Market Origination Ledger ({len(all_markets_flat)} Lines)</h2>
    <div class="table-wrap"><table><thead><tr>
      <th>ID</th><th>Sport</th><th>Event</th><th>Market Family</th><th>Selection</th><th>Fair %</th><th>Decimal</th><th>American</th><th>Confidence</th>
    </tr></thead><tbody>{mkt_rows_html}</tbody></table></div>
    """
    (out_site / "markets.html").write_text(render_shell("Multi-Market Board", "markets", markets_body), encoding="utf-8")

    # 5. Methodology & OLBG Reverse-Engineering Page
    meth_body = """
    <section class="hero">
      <div class="eyebrow">Quantitative Methodology &amp; OLBG Architecture Discovery</div>
      <h1>Statistical Line Origination Equations &amp; OLBG Protocol Audit</h1>
      <p class="lead">Every probability in this release is computed deterministically from governing-body performance data, venue effects, and injury adjustments—never from OLBG tipster vote percentages or bookmaker prices.</p>
    </section>

    <div class="callout warn">
      <strong>Smoking-Gun OLBG GeoIP Clock Discovery (2026-10-23):</strong>
      When crawled from US-East infrastructure, OLBG server-renders unlabeled timestamps in <strong>US Eastern Daylight Time (EDT = UTC-4)</strong>—a 5-hour shift from UK BST (UTC+1) and 4-hour shift from UTC.
      Direct proof captured live on <a href="https://www.olbg.com/betting-tips/Greyhounds/28" target="_blank" rel="noopener">/betting-tips/Greyhounds/28</a>:
      card title <code>8:33 Romford</code> (20:33 BST / 19:33 UTC) renders right above timestamp <code>Today 15:33</code>;
      <code>9:13 Romford</code> (Coral 100 Champion Stakes Final, 20:13 UTC) renders as <code>Today 16:13</code>;
      and URC kickoffs at <code>19:45 IRE/UK</code> (18:45 UTC) render as <code>Today 14:45</code>.
      Parallel session <code>2b72da34</code> copied those unlabeled strings verbatim across all 37 rows.
    </div>

    <h2>1. OLBG Reverse-Engineering &amp; Robots Compliance</h2>
    <div class="table-wrap"><table><thead><tr>
      <th>Layer / Route</th><th>Observed OLBG Behavior on 2026-10-23</th><th>Compliance &amp; Engineering Action</th>
    </tr></thead><tbody>
      <tr><td><code>/robots.txt</code></td><td>Disallows <code>/api/</code>, <code>/bookiecenter/api/</code>, <code>/storage/app/json_data/</code>, <code>/events.php</code>, <code>/tips/hot</code>, <code>/sports/</code>, and <code>User-agent: Python-urllib</code>.</td><td>Zero disallowed endpoints requested; strictly public HTML hubs &amp; sitemap routes fetched cleanly.</td></tr>
      <tr><td><code>/sitemap-betting-tips.xml</code></td><td>Updated <code>2026-10-23</code> across 4 chunks; exposes exact numeric OLBG category IDs (3, 4, 5, 7, 8, 9, 10, 12, 13, 14, 15, 20, 21, 25, 26, 28).</td><td>Mapped all 15 covered sports including dual GAA codes <code>Gaelic_Football/25</code> + <code>Hurling/26</code>; excluded Football/1, Horse_Racing/2, NFL/11, AFL/22, eSports/23.</td></tr>
      <tr><td>20-Card Hub Truncation</td><td>Top hubs truncate high-volume slates (e.g., <code>/Ice_Hockey/13</code> hid <code>TB Lightning @ COL Avalanche</code> behind 18 European hockey cards; <code>/Basketball/4</code> hid <code>MEM Grizzlies @ GS Warriors</code>).</td><td>Crawled competition sub-routes (<code>/Ice_Hockey/NHL/13</code>, <code>/Basketball/NBA/4</code>, <code>/Hurling/26</code>) plus chunked pagination to capture 100% of hidden cards.</td></tr>
      <tr><td>Empty Active Tour Hubs</td><td><code>/Golf/5</code> printed <em>&ldquo;No tips found.&rdquo;</em> and <code>/Rugby_League/10</code> showed only 2027 anteposts despite live 2026 tournaments running right now.</td><td>Queried PGA Tour (Bermuda), DP World Tour (Genesis), LPGA (BMW Ladies), and NRL/IRL (2026 Rugby League World Cup Round 2) directly for full 5-event coverage.</td></tr>
    </tbody></table></div>

    <h2>2. Sport-by-Sport Multi-Market Statistical Pricing Families</h2>
    <div class="table-wrap"><table><thead><tr>
      <th>Pricing Engine</th><th>Sports Covered</th><th>Mathematical Formulation &amp; Markets Derived</th>
    </tr></thead><tbody>
      <tr><td><strong>Exact Bivariate Poisson + OT Allocation</strong></td><td>Baseball (MLB World Series), Ice Hockey (NHL)</td><td>Independent run/goal intensities (&lambda;<sub>H</sub>, &lambda;<sub>A</sub>) from opponent-adjusted scoring/prevention, starter quality, rest, and key injuries (e.g., Nick Suzuki out 2–4 weeks), enumerating the full 25&times;25 score matrix for Moneyline, &plusmn;1.5 Run/Puck Line, Alt Totals, Team Totals, and 1st-Period / First-5-Innings DNB.</td></tr>
      <tr><td><strong>Exact Markov Best-of-N Series Matrix</strong></td><td>Tennis (Bo3 Sets), Volleyball (Bo5 Sets), Snooker (Bo9 / Bo11 Frames), Darts (Bo11 / Bo19 Legs), World Series Outright (Bo7)</td><td>Exact negative-binomial exact-score state probabilities from unit win probability <em>p<sub>u</sub></em>, outputting Match Winner, -1.5 / +1.5 / -2.5 Set-Leg-Frame Handicaps, Over/Under Total Sets/Legs/Frames, 1st-Unit Winner, and Exact Score.</td></tr>
      <tr><td><strong>Gaussian Margin &amp; Total Convolution</strong></td><td>Basketball (NBA &amp; EuroLeague), Rugby Union, Rugby League, Cricket (T20I &amp; ODI), Handball, Gaelic Sports, Golf, Motor Racing, Greyhounds</td><td>Joint normal scoring expectations (&mu;<sub>H</sub>, &mu;<sub>A</sub>, &sigma;<sub>margin</sub>, &sigma;<sub>total</sub>) incorporating official injury/withdrawal reports, generating 2-Way/3-Way Result, Primary &amp; Calibrated Half-Point Handicaps, Game Total, Team Total, First-Half DNB, and Player/Podium Props.</td></tr>
    </tbody></table></div>

    <h2>3. Resolution of the High-Confidence Chalk Problem (-250 to +10000 Window)</h2>
    <p>
      Under naive probability ranking, mismatches with <span class="num">80%–92%</span> moneyline probability price between <span class="num">-400</span> and <span class="num">-1150</span>,
      crowding out actionable bets. Our classifier enforces a two-gate High-confidence rule:
      <strong>(Gate 1)</strong> fair win/cover probability strictly <span class="num">p &gt; 0.7000</span>, AND
      <strong>(Gate 2)</strong> zero-vig fair odds strictly inside <span class="num">[-250, +10000]</span> (<span class="num">1.4000 &le; decimal &le; 101.0000</span>).
      Any raw moneyline shorter than <span class="num">-250</span> is tagged <code>chalk_suppressed = true</code> and capped at <code>medium</code>, while our multi-market engine solves for the exact spread/total/prop line landing cleanly inside <span class="num">-250</span> to <span class="num">+10000</span>.
    </p>
    """
    (out_site / "methodology.html").write_text(render_shell("Methodology & Clock Audit", "methodology", meth_body), encoding="utf-8")

    # 6. Official Sources Registry Page
    seen_urls: Dict[str, Tuple[str, str]] = {}
    for ev in events:
        seen_urls.setdefault(ev["official_url"], (ev["sport"], ev["competition"]))
        seen_urls.setdefault(ev["secondary_official_url"], (ev["sport"], ev["competition"]))
    src_rows = "".join(
        f"<tr><td><strong>{e(sp)}</strong></td><td>{e(comp)}</td>"
        f"<td><a href='{e(u)}' target='_blank' rel='noopener'>{e(u)}</a></td>"
        f"<td><span class='badge badge-high'>Official Governing Body</span></td></tr>"
        for u, (sp, comp) in sorted(seen_urls.items(), key=lambda kv: (kv[1][0], kv[0]))
    )
    sources_body = f"""
    <section class="hero">
      <div class="eyebrow">Strict Official Provenance · {len(seen_urls)} Distinct Official Endpoints</div>
      <h1>Official League, Tour &amp; Governing-Body Verification Registry</h1>
      <p class="lead">Zero betting operators, odds comparison scrapers, or third-party media aggregators are used to confirm fixtures, scores, standings, statistics, or injury availability. OLBG is used strictly as the discovery target under study.</p>
    </section>
    <div class="table-wrap"><table><thead><tr>
      <th>Sport</th><th>Competition / Feed Scope</th><th>Official URL Inspected Live on 2026-10-23 UTC</th><th>Provenance Tier</th>
    </tr></thead><tbody>{src_rows}</tbody></table></div>
    """
    (out_site / "sources.html").write_text(render_shell("Official Sources", "sources", sources_body), encoding="utf-8")

    # 7. Line-by-Line Repo Audit Page
    aud_rows = "".join(
        f"<tr id='{e(a['finding_id'])}'>"
        f"<td class='num'><strong>{e(a['finding_id'])}</strong><div style='margin-top:4px'><span class='badge badge-flag'>{e(a['severity'])}</span></div></td>"
        f"<td class='num'><a href='{e(a['github_url'])}' target='_blank' rel='noopener'>{e(a['file_path'])}:{e(a['lines'])}</a>"
        f"<div class='meta-sub num'>SHA-256: {e(a['sha256'][:16])}…</div></td>"
        f"<td>{e(a['issue'])}</td>"
        f"<td>{e(a['resolution'])}<div class='meta-sub' style='margin-top:4px'>"
        f"<a href='{e(a['official_recheck_url'])}' target='_blank' rel='noopener'>Official Governing-Body Recheck &rarr;</a></div></td>"
        f"</tr>"
        for a in REPO_AUDIT_FINDINGS
    )
    audit_body = f"""
    <section class="hero">
      <div class="eyebrow">Repository Review &amp; Line-by-Line Fact Check · {len(REPO_AUDIT_FINDINGS)} Findings</div>
      <h1>Repository Audit: Canonical Stale TTL, Scope Drift &amp; Parallel Desk Defects</h1>
      <p class="lead">Line-by-line inspection of canonical <code>data/current/</code>, <code>pipeline/config.py</code>, <code>scripts/validate.py</code>, and parallel 23 Oct run <code>data/2b72da34/desk.json</code> with exact file:line anchors, SHA-256 digests, and official governing-body rechecks.</p>
    </section>
    <div class="table-wrap"><table><thead><tr>
      <th>ID &amp; Severity</th><th>Exact File:Line &amp; SHA-256</th><th>Audited Defect Found</th><th>Session 8a900c04 Remediation &amp; Official Recheck</th>
    </tr></thead><tbody>{aud_rows}</tbody></table></div>
    """
    (out_site / "repo-audit.html").write_text(render_shell("Repository Audit", "audit", audit_body), encoding="utf-8")

    # 8. Flagged for Review Page (Strict Blank Cells for Unconfirmed Fields!)
    flg_rows = "".join(
        f"<tr id='{e(f['id'])}'>"
        f"<td class='num'>{e(f['id'])}</td>"
        f"<td><strong>{e(f['sport'])}</strong></td>"
        f"<td><strong>{e(f['event'])}</strong><div class='meta-sub'>{e(f['competition'])}</div></td>"
        f"<td class='num'>{e(f['olbg_display_time'])}</td>"
        f"<td></td><td></td><td></td>"
        f"<td><span class='badge badge-flag'>Unverified — Left Blank</span><div class='meta-sub' style='margin-top:4px'>{e(f['flag_reason'])}</div>"
        f"<div class='meta-sub'><a href='{e(f['olbg_url'])}' target='_blank' rel='noopener'>OLBG Card</a> · "
        f"<a href='{e(f['official_url'])}' target='_blank' rel='noopener'>Federation Hub</a></div></td>"
        f"</tr>"
        for f in FLAGGED_ROWS
    )
    flagged_body = f"""
    <section class="hero">
      <div class="eyebrow">Strict Anti-Hallucination Quarantine · {len(FLAGGED_ROWS)} Rows</div>
      <h1>Flagged for Review — Unconfirmed OLBG Listings Held Out of Pricing</h1>
      <p class="lead">Any OLBG discovery card whose exact UTC start time, venue, or official matchday teamsheet/injury bulletin could not be confirmed from an official governing-body feed is quarantined here with unconfirmed columns strictly blank (<code>null</code> in JSON) and excluded from recommendations.</p>
    </section>
    <div class="table-wrap"><table><thead><tr>
      <th>Flag ID</th><th>Sport</th><th>OLBG Listing</th><th>Raw OLBG String</th><th>UTC Kickoff</th><th>Selection</th><th>Fair Line</th><th> Audit Quarantine Reason &amp; Links</th>
    </tr></thead><tbody>{flg_rows}</tbody></table></div>
    """
    (out_site / "flagged.html").write_text(render_shell("Flagged for Review", "flagged", flagged_body), encoding="utf-8")

    # 9. All 15 Dedicated Sport Pages (8a900c04/sports/<slug>.html)
    for s_name, s_slug, s_id, s_off in COVERED_SPORTS:
        s_items = sorted([x for x in events if x["sport"] == s_name], key=lambda x: x["start_utc"])
        s_flags = [f for f in FLAGGED_ROWS if f["sport"] == s_name]
        s_high = [x for x in s_items if x["confidence"] == "high"]
        flag_sec = ""
        if s_flags:
            f_trs = "".join(
                f"<tr><td class='num'>{e(f['id'])}</td><td>{e(f['event'])} ({e(f['competition'])})</td>"
                f"<td></td><td></td><td><span class='badge badge-flag'>Unverified</span> {e(f['flag_reason'])}</td></tr>"
                for f in s_flags
            )
            flag_sec = (
                f"<h2>Quarantined / Flagged {e(s_name)} Listings ({len(s_flags)})</h2>"
                f'<div class="table-wrap"><table><thead><tr><th>ID</th><th>Event</th><th>UTC Start</th><th>Originated Line</th><th>Quarantine Reason</th></tr></thead>'
                f"<tbody>{f_trs}</tbody></table></div>"
            )

        sport_body = f"""
        <section class="hero">
          <div class="eyebrow">Covered Sport Hub · OLBG Category #{s_id} · <a href="{e(s_off)}" target="_blank" rel="noopener">Official Governing Body</a></div>
          <h1>{e(s_name)} — Originated Multi-Market Lines &amp; Top 5 Predictions</h1>
          <p class="lead">
            <strong>{len(s_items)}</strong> upcoming {e(s_name)} events priced across <strong>{sum(len(x['markets']) for x in s_items)}</strong> originated markets,
            including <strong>{len(s_high)}</strong> High-confidence selections inside the <code>-250</code> to <code>+10000</code> window and
            <strong>{len(s_items)}</strong> unique analyst predictions backed by team/player statistics, recent history, and availability bulletins.
          </p>
        </section>
        {render_picks_table(s_items, prefix="../", include_toolbar=False)}
        {flag_sec}
        """
        (out_sports / f"{s_slug}.html").write_text(
            render_shell(f"{s_name} Picks & Markets", "", sport_body, prefix="../", active_sport_slug=s_slug),
            encoding="utf-8",
        )

    # 10. Session Report in reports/SESSION_8A900C04.{md,html} (auto-discovered by pipeline/build.py on archive.html!)
    md_lines = [
        f"# Session `{SESSION_ID}` — 15-Sport OLBG Quantitative Origination & Line-by-Line Audit Report",
        "",
        f"- **Generated (UTC)**: `{GENERATED_AT}`",
        f"- **Live Interactive Dashboard**: [`../8a900c04/index.html`](../8a900c04/index.html)",
        f"- **Structured Artifacts**: [`../data/8a900c04/desk.json`](../data/8a900c04/desk.json) · [`../data/8a900c04/fixtures.csv`](../data/8a900c04/fixtures.csv) · [`../data/8a900c04/markets.csv`](../data/8a900c04/markets.csv) · [`../data/8a900c04/predictions.json`](../data/8a900c04/predictions.json)",
        f"- **Covered Sports (`15 / 15` exact scope)**: {', '.join(s[0] for s in COVERED_SPORTS)}",
        f"- **Upcoming Priced Events**: `{len(events)}` (`5` per covered sport × `15` sports) + `{len(FLAGGED_ROWS)}` unconfirmed OLBG cards quarantined on [`../8a900c04/flagged.html`](../8a900c04/flagged.html)",
        f"- **Total Originated Market Lines**: `{len(all_markets_flat)}` (`{len(high_picks)}` High-confidence picks strictly inside `-250` to `+10000` / `1.40–101.00`, `{len(chalk_suppressed_events)}` raw moneyline chalk selections suppressed below `-250`)",
        "",
        "## 1. Key Reverse-Engineering & Repository Audit Findings",
        "",
        "| ID | Severity | File:Line | Summary | Official Recheck |",
        "| --- | --- | --- | --- | --- |",
    ]
    for a in REPO_AUDIT_FINDINGS:
        md_lines.append(
            f"| `{a['finding_id']}` | **{a['severity']}** | [`{a['file_path']}:{a['lines']}`]({a['github_url']}) | {a['issue']} | [Recheck]({a['official_recheck_url']}) |"
        )
    md_lines.extend(["", "## 2. Executive Summary — Top High-Confidence Actionable Picks (`-250` to `+10000`)", ""])
    md_lines.append("| ID | Sport | Event | UTC Start | Selection | Fair Line | Official Source |")
    md_lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for x in sorted(high_picks, key=lambda r: r["fair_prob"], reverse=True)[:25]:
        md_lines.append(
            f"| `{x['id']}` | {x['sport']} | {x['event']} | `{x['start_utc']}` | **{x['recommended_selection']}** | `{fmt_amer(x['fair_american'])}` (`{x['fair_decimal']:.2f}`, `{x['fair_pct']:.1f}%`) | [Source]({x['official_url']}) |"
        )
    (out_reports / "SESSION_8A900C04.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    rep_html = render_shell(
        "Session 8a900c04 Executive Audit & Origination Report",
        "",
        f"""
        <section class="hero">
          <div class="eyebrow">Archived Session Report · {SESSION_ID} · {GENERATED_AT}</div>
          <h1>Session {SESSION_ID}: 15-Sport Quantitative Origination &amp; Line-by-Line Verification Report</h1>
          <p class="lead">Full interactive multi-page dashboard published at <a href="../8a900c04/index.html"><code>../8a900c04/index.html</code></a> ({len(events)} upcoming events, {len(all_markets_flat)} originated market lines, {len(high_picks)} High-confidence selections inside [-250, +10000], {len(events)} human predictions across all 15 covered sports, and {len(FLAGGED_ROWS)} quarantined rows).</p>
        </section>
        {render_picks_table(sorted(high_picks, key=lambda r: r["fair_prob"], reverse=True), prefix="../8a900c04/", include_toolbar=False)}
        """,
        prefix="../8a900c04/",
    )
    # Fix archive link relative depth inside reports/SESSION_8A900C04.html (../archive.html instead of ../8a900c04/../archive.html)
    rep_html = rep_html.replace('href="../8a900c04/../', 'href="../')
    (out_reports / "SESSION_8A900C04.html").write_text(rep_html, encoding="utf-8")

    return summary


if __name__ == "__main__":
    s = build_all()
    print(json.dumps(s, indent=2))
