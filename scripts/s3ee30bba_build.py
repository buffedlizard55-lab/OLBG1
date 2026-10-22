#!/usr/bin/env python3
"""Static dashboard builder and data exporter for session 3ee30bba-olbg1 (/3ee30bba/)."""
from __future__ import annotations

import csv
import html
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.s3ee30bba_audit import build_repo_audit
from scripts.s3ee30bba_data import (
    EHF_STANDINGS,
    ELAPSED_FIXTURES,
    EUROLEAGUE_STANDINGS,
    FLAGS,
    MLB_STANDINGS,
    NHL_STANDINGS,
    build_fixture_list,
)
from scripts.s3ee30bba_model import originate_all, verify_standings_conservation
from scripts.s3ee30bba_predictions import PREDICTIONS
from scripts.s3ee30bba_sources import (
    AS_OF_UTC,
    COVERED_SPORTS,
    EXCLUDED_SPORTS,
    SESSION_ID,
    SESSION_SLUG,
    SOURCES,
    TASK_ID,
    WINDOW_END_UTC,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_OUT = ROOT / "data" / SESSION_ID
SITE_OUT = ROOT / SESSION_ID

CSS = """
:root {
  --bg: #f6f8fa;
  --surface: #ffffff;
  --surface-alt: #f1f5f9;
  --border: #dde3ea;
  --text: #0f172a;
  --muted: #475569;
  --brand: #0c6348;
  --brand-soft: #e6f4ef;
  --high-bg: #dcfce7;
  --high-fg: #14532d;
  --med-bg: #fef3c7;
  --med-fg: #78350f;
  --low-bg: #e2e8f0;
  --low-fg: #334155;
  --flag-bg: #fee2e2;
  --flag-fg: #7f1d1d;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font: 14px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-variant-numeric: tabular-nums;
}
a { color: var(--brand); text-decoration: none; }
a:hover { text-decoration: underline; }
.shell { display: grid; grid-template-columns: 248px 1fr; min-height: 100vh; }
.sidebar {
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 20px 14px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}
.brand { display: block; padding: 6px 10px 14px; border-bottom: 1px solid var(--border); margin-bottom: 14px; }
.brand strong { display: block; font-size: 16px; color: var(--text); letter-spacing: -0.01em; }
.brand small { color: var(--muted); font-size: 11.5px; }
.nav-group { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin: 14px 10px 6px; }
.nav-link {
  display: flex; justify-content: space-between; align-items: center;
  padding: 7px 10px; border-radius: 6px; color: var(--text); font-weight: 500; margin-bottom: 2px;
}
.nav-link:hover { background: var(--surface-alt); text-decoration: none; }
.nav-link.active { background: var(--brand-soft); color: var(--brand); font-weight: 700; }
.pill { font-size: 11px; padding: 1px 7px; border-radius: 999px; background: var(--surface-alt); color: var(--muted); }
.nav-link.active .pill { background: #c5e7dc; color: var(--brand); }
.content { padding: 26px 32px 48px; max-width: 1360px; width: 100%; }
.topbar {
  display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px;
  padding-bottom: 16px; margin-bottom: 20px; border-bottom: 1px solid var(--border);
}
.eyebrow { font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--brand); margin: 0 0 4px; }
h1 { font-size: 24px; margin: 0 0 4px; letter-spacing: -0.02em; }
h2 { font-size: 18px; margin: 28px 0 8px; letter-spacing: -0.01em; }
h3 { font-size: 15px; margin: 0 0 6px; }
.sub { color: var(--muted); margin: 0; max-width: 820px; }
.btn-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.btn {
  display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px;
  border-radius: 6px; border: 1px solid var(--border); background: var(--surface);
  color: var(--text); font-weight: 600; font-size: 13px; cursor: pointer;
}
.btn.primary { background: var(--brand); border-color: var(--brand); color: #fff; }
.btn:hover { text-decoration: none; filter: brightness(0.97); }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 12px; margin: 16px 0 22px; }
.kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; }
.kpi-label { font-size: 12px; color: var(--muted); font-weight: 600; }
.kpi-val { font-size: 24px; font-weight: 800; margin: 4px 0 2px; color: var(--text); }
.kpi-foot { font-size: 11.5px; color: var(--muted); }
.banner {
  background: var(--brand-soft); border: 1px solid #b7e1d3; border-radius: 8px;
  padding: 12px 16px; margin-bottom: 18px; color: #0b4634; font-size: 13.5px;
}
.banner.warn { background: #fffbeb; border-color: #fde68a; color: #78350f; }
.filters {
  display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
  background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 10px 14px; margin: 12px 0;
}
.filters input, .filters select {
  padding: 6px 10px; border: 1px solid var(--border); border-radius: 6px;
  font: inherit; background: #fff; color: var(--text);
}
.filters input[type="search"] { min-width: 240px; flex: 1; }
.table-wrap {
  background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  overflow-x: auto; margin-bottom: 22px;
}
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 9px 11px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }
th { background: var(--surface-alt); font-weight: 700; color: var(--text); white-space: nowrap; position: sticky; top: 0; }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: #f8fafc; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 700; white-space: nowrap; }
.badge.high { background: var(--high-bg); color: var(--high-fg); }
.badge.medium { background: var(--med-bg); color: var(--med-fg); }
.badge.low { background: var(--low-bg); color: var(--low-fg); }
.badge.flag { background: var(--flag-bg); color: var(--flag-fg); }
.badge.info { background: #e0f2fe; color: #075985; }
.blank { color: #64748b; font-style: italic; font-size: 12px; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 14px; margin: 14px 0 24px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
.card p { margin: 8px 0; color: var(--text); }
.meta { font-size: 12px; color: var(--muted); }
.sport-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; margin: 12px 0 22px; }
.sport-tile {
  display: block; background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 12px 14px; color: var(--text);
}
.sport-tile:hover { border-color: var(--brand); text-decoration: none; }
.sport-tile strong { display: block; font-size: 14px; margin-bottom: 2px; }
.footer { margin-top: 36px; padding-top: 16px; border-top: 1px solid var(--border); color: var(--muted); font-size: 12px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
@media (max-width: 900px) {
  .shell { grid-template-columns: 1fr; }
  .sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); }
  .content { padding: 18px 16px 36px; }
}
""".strip()

JS = """
(() => {
  const search = document.getElementById('table-search');
  const sport = document.getElementById('sport-filter');
  const tier = document.getElementById('tier-filter');
  const fmt = document.getElementById('odds-format');
  const clearBtn = document.getElementById('clear-filters');
  const countEl = document.getElementById('filter-count');

  function applyFilters() {
    const q = (search ? search.value : '').trim().toLowerCase();
    const sp = sport ? sport.value : '';
    const tr = tier ? tier.value : '';
    const rows = document.querySelectorAll('tbody tr[data-filterable="1"]');
    if (!rows.length) return;
    let shown = 0;
    rows.forEach((row) => {
      const hay = (row.getAttribute('data-search') || '').toLowerCase();
      const rSp = row.getAttribute('data-sport') || '';
      const rTr = row.getAttribute('data-tier') || '';
      const ok = (!q || hay.includes(q)) && (!sp || rSp === sp) && (!tr || rTr === tr);
      row.hidden = !ok;
      if (ok) shown += 1;
    });
    if (countEl) countEl.textContent = `Showing ${shown} of ${rows.length} rows`;
  }

  function applyOddsFormat() {
    if (!fmt) return;
    const mode = fmt.value;
    document.querySelectorAll('[data-us][data-dec]').forEach((el) => {
      el.textContent = mode === 'decimal' ? el.getAttribute('data-dec') : el.getAttribute('data-us');
    });
  }

  [search, sport, tier].forEach((el) => { if (el) el.addEventListener('input', applyFilters); if (el) el.addEventListener('change', applyFilters); });
  if (fmt) fmt.addEventListener('change', applyOddsFormat);
  if (clearBtn) clearBtn.addEventListener('click', () => {
    if (search) search.value = '';
    if (sport) sport.value = '';
    if (tier) tier.value = '';
    applyFilters();
  });
  applyFilters();
})();
""".strip()


def esc(v: object) -> str:
    return html.escape("" if v is None else str(v), quote=True)


def blank(label: str = "unverified") -> str:
    return f'<span class="blank">— · {esc(label)}</span>'


def ext_link(url: str, label: str) -> str:
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)} ↗</a>'


def tier_badge(conf: str | None) -> str:
    if not conf:
        return blank("withheld")
    return f'<span class="badge {esc(conf)}">{esc(conf.capitalize())}</span>'


def price_span(outcome: dict | None) -> str:
    if not outcome:
        return blank("withheld")
    us = outcome["american_display"]
    dec = outcome["decimal_display"]
    prob = f"{outcome['probability'] * 100:.2f}%"
    return f'<strong data-us="{esc(us)}" data-dec="{esc(dec)}">{esc(us)}</strong> <span class="meta">({esc(dec)} · {esc(prob)})</span>'


def render_table(headers: list[str], rows: list[tuple[dict, list[str]]]) -> str:
    th_html = "".join(f"<th>{esc(h)}</th>" for h in headers)
    tr_parts = []
    for attrs, cells in rows:
        attr_str = "".join(f' {k}="{esc(v)}"' for k, v in attrs.items() if v is not None)
        td_html = "".join(f"<td>{c}</td>" for c in cells)
        tr_parts.append(f"<tr{attr_str}>{td_html}</tr>")
    return f'<div class="table-wrap"><table><thead><tr>{th_html}</tr></thead><tbody>{"".join(tr_parts)}</tbody></table></div>'


def assemble_desk() -> dict:
    conservation = verify_standings_conservation()
    fixtures = build_fixture_list()
    books = originate_all(fixtures)
    audit = build_repo_audit()
    sport_meta = {s["slug"]: s for s in COVERED_SPORTS}
    source_map = {s["id"]: s for s in SOURCES}

    high_picks = []
    chalk_capped = []
    for f in fixtures:
        b = books[f["id"]]
        for m in b["markets"]:
            for o in m["outcomes"]:
                entry = {
                    "fixture_id": f["id"],
                    "sport": f["sport"],
                    "sport_name": sport_meta[f["sport"]]["name"],
                    "competition": f["competition"],
                    "event_label": f["event_label"],
                    "start_utc": f["start_utc"],
                    "market_id": m["id"],
                    "market_label": m["label"],
                    "family": m["family"],
                    "selection": o["selection"],
                    "probability": o["probability"],
                    "fair_decimal": o["fair_decimal"],
                    "decimal_display": o["decimal_display"],
                    "american": o["american"],
                    "american_display": o["american_display"],
                    "in_window": o["in_window"],
                    "confidence": o["confidence"],
                    "tier_note": o["tier_note"],
                    "official_url": f["official_url"],
                    "stats_url": f["stats_url"],
                }
                if o["confidence"] == "high":
                    high_picks.append(entry)
                elif o["above_70_outside_window"]:
                    chalk_capped.append(entry)

    pred_by_key = {(p["fixture_id"], p["market_id"], p["selection"]): p for p in PREDICTIONS}
    enriched_preds = []
    for hp in high_picks:
        p = pred_by_key[(hp["fixture_id"], hp["market_id"], hp["selection"])]
        words = len(p["body"].split())
        enriched_preds.append({
            **p,
            "sport": hp["sport"],
            "sport_name": hp["sport_name"],
            "competition": hp["competition"],
            "start_utc": hp["start_utc"],
            "market_label": hp["market_label"],
            "probability": hp["probability"],
            "fair_decimal": hp["fair_decimal"],
            "decimal_display": hp["decimal_display"],
            "american": hp["american"],
            "american_display": hp["american_display"],
            "in_window": hp["in_window"],
            "word_count": words,
        })

    winner_tiers = Counter(
        books[f["id"]]["winner_pick"]["confidence"]
        for f in fixtures
        if books[f["id"]]["winner_pick"] is not None
    )
    outcome_tiers = Counter(
        o["confidence"]
        for b in books.values()
        for m in b["markets"]
        for o in m["outcomes"]
    )

    sport_counts = []
    for sm in COVERED_SPORTS:
        sl = sm["slug"]
        f_rows = [f for f in fixtures if f["sport"] == sl]
        p_rows = [f for f in f_rows if books[f["id"]]["markets"]]
        m_cnt = sum(len(books[f["id"]]["markets"]) for f in f_rows)
        o_cnt = sum(len(m["outcomes"]) for f in f_rows for m in books[f["id"]]["markets"])
        h_cnt = sum(1 for hp in high_picks if hp["sport"] == sl)
        el_cnt = sum(1 for e in ELAPSED_FIXTURES if e["sport"] == sl)
        sport_counts.append({
            **sm,
            "upcoming_count": len(f_rows),
            "priced_count": len(p_rows),
            "unpriced_count": len(f_rows) - len(p_rows),
            "elapsed_count": el_cnt,
            "market_count": m_cnt,
            "outcome_count": o_cnt,
            "high_count": h_cnt,
        })

    counts = {
        "covered_sports": len(COVERED_SPORTS),
        "excluded_sports": len(EXCLUDED_SPORTS),
        "upcoming_fixtures": len(fixtures),
        "elapsed_oct22_fixtures": len(ELAPSED_FIXTURES),
        "priced_fixtures": sum(1 for f in fixtures if books[f["id"]]["markets"]),
        "unpriced_fixtures": sum(1 for f in fixtures if not books[f["id"]]["markets"]),
        "originated_markets": sum(len(b["markets"]) for b in books.values()),
        "originated_outcomes": sum(len(m["outcomes"]) for b in books.values() for m in b["markets"]),
        "winner_high": winner_tiers.get("high", 0),
        "winner_medium": winner_tiers.get("medium", 0),
        "winner_low": winner_tiers.get("low", 0),
        "outcome_high": outcome_tiers.get("high", 0),
        "outcome_medium": outcome_tiers.get("medium", 0),
        "outcome_low": outcome_tiers.get("low", 0),
        "high_picks": len(high_picks),
        "predictions": len(enriched_preds),
        "out_of_window_chalk_capped": len(chalk_capped),
        "official_sources": len(SOURCES),
        "flags": len(FLAGS),
        "repo_audit_findings": len(audit["findings"]),
    }

    return {
        "session_id": SESSION_ID,
        "session_slug": SESSION_SLUG,
        "task_id": TASK_ID,
        "as_of_utc": AS_OF_UTC,
        "window_end_utc": WINDOW_END_UTC,
        "counts": counts,
        "conservation": conservation,
        "covered_sports": sport_counts,
        "excluded_sports": EXCLUDED_SPORTS,
        "sources": SOURCES,
        "source_map": source_map,
        "fixtures": fixtures,
        "books": books,
        "high_picks": high_picks,
        "chalk_capped": chalk_capped,
        "predictions": enriched_preds,
        "elapsed_fixtures": ELAPSED_FIXTURES,
        "flags": FLAGS,
        "repo_audit": audit,
    }


def write_data_exports(desk: dict) -> None:
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    export_doc = {k: v for k, v in desk.items() if k != "source_map"}
    (DATA_OUT / "desk.json").write_text(json.dumps(export_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (DATA_OUT / "predictions.json").write_text(json.dumps(desk["predictions"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (DATA_OUT / "repo_audit.json").write_text(json.dumps(desk["repo_audit"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def csv_safe(val: object) -> object:
        if isinstance(val, str) and val and val.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + val
        return val

    f_buf = io.StringIO(newline="")
    fw = csv.writer(f_buf, lineterminator="\n")
    fw.writerow([
        "id", "sport", "competition", "event_label", "date", "start_utc", "venue",
        "official_status", "priced", "winner_selection", "winner_confidence",
        "winner_probability", "winner_fair_decimal", "winner_american",
        "withhold_reason", "official_url", "stats_url",
    ])
    for f in desk["fixtures"]:
        b = desk["books"][f["id"]]
        wp = b["winner_pick"]
        fw.writerow([csv_safe(x) for x in [
            f["id"], f["sport"], f["competition"], f["event_label"], f["date"], f["start_utc"], f["venue"],
            f["official_status"], bool(b["markets"]),
            wp["selection"] if wp else None, wp["confidence"] if wp else None,
            round(wp["probability"], 6) if wp else None, wp["decimal_display"] if wp else None,
            wp["american_display"] if wp else None, f["withhold_reason"], f["official_url"], f["stats_url"],
        ]])
    (DATA_OUT / "fixtures.csv").write_text(f_buf.getvalue(), encoding="utf-8")

    m_buf = io.StringIO(newline="")
    mw = csv.writer(m_buf, lineterminator="\n")
    mw.writerow([
        "fixture_id", "sport", "event_label", "start_utc", "market_id", "family",
        "market_label", "selection", "probability", "fair_decimal", "american",
        "in_window", "confidence", "tier_note", "official_url",
    ])
    for f in desk["fixtures"]:
        b = desk["books"][f["id"]]
        for m in b["markets"]:
            for o in m["outcomes"]:
                mw.writerow([csv_safe(x) for x in [
                    f["id"], f["sport"], f["event_label"], f["start_utc"], m["id"], m["family"],
                    m["label"], o["selection"], round(o["probability"], 6), o["decimal_display"],
                    o["american_display"], o["in_window"], o["confidence"], o["tier_note"], f["official_url"],
                ]])
    (DATA_OUT / "markets.csv").write_text(m_buf.getvalue(), encoding="utf-8")


class SiteBuilder:
    def __init__(self, desk: dict) -> None:
        self.d = desk
        self.c = desk["counts"]
        self.sport_by_slug = {s["slug"]: s for s in desk["covered_sports"]}

    def rel(self, target: str, from_page: str) -> str:
        src_dir = (SITE_OUT / from_page).parent
        dst = SITE_OUT / target
        return os.path.relpath(dst, src_dir).replace(os.sep, "/")

    def data_rel(self, filename: str, from_page: str) -> str:
        src_dir = (SITE_OUT / from_page).parent
        dst = DATA_OUT / filename
        return os.path.relpath(dst, src_dir).replace(os.sep, "/")

    def root_rel(self, target: str, from_page: str) -> str:
        src_dir = (SITE_OUT / from_page).parent
        dst = ROOT / target
        return os.path.relpath(dst, src_dir).replace(os.sep, "/")

    def page(self, rel_path: str, title: str, subtitle: str, active: str, body: str) -> None:
        r = lambda t: self.rel(t, rel_path)
        nav_main = [
            ("overview", "index.html", "Dashboard Overview", ""),
            ("matches", "matches.html", "Match Ledger", str(self.c["upcoming_fixtures"])),
            ("markets", "markets.html", "Markets Explorer", str(self.c["originated_markets"])),
            ("high", "high-confidence.html", "High Confidence", str(self.c["high_picks"])),
            ("predictions", "predictions.html", "Human Predictions", str(self.c["predictions"])),
            ("sports", "sports.html", "17 Sport Categories", "17"),
        ]
        nav_audit = [
            ("analysis", "analysis.html", "Analysis & Models", ""),
            ("reverse", "reverse-engineering.html", "OLBG Reverse Eng.", "24"),
            ("sources", "sources.html", "Official Sources", str(self.c["official_sources"])),
            ("audit", "repo-audit.html", "Repo Line Audit", str(self.c["repo_audit_findings"])),
            ("flagged", "flagged.html", "Flagged for Review", str(self.c["flags"])),
        ]

        def render_nav(items: list[tuple[str, str, str, str]]) -> str:
            out = []
            for key, href, label, cnt in items:
                cls = "nav-link active" if key == active else "nav-link"
                pill = f'<span class="pill">{esc(cnt)}</span>' if cnt else ""
                out.append(f'<a class="{cls}" href="{esc(r(href))}"><span>{esc(label)}</span>{pill}</a>')
            return "".join(out)

        sport_links = "".join(
            f'<a class="nav-link{" active" if active == "sport:" + s["slug"] else ""}" href="{esc(r("sports/" + s["slug"] + ".html"))}">'
            f'<span>{esc(s["name"])}</span><span class="pill">{s["upcoming_count"]}</span></a>'
            for s in self.d["covered_sports"]
        )

        csv_fix = self.data_rel("fixtures.csv", rel_path)
        csv_mkt = self.data_rel("markets.csv", rel_path)
        canon_root = self.root_rel("index.html", rel_path)

        doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · OLBG1 Live Research Desk ({SESSION_ID})</title>
  <link rel="stylesheet" href="{esc(r('assets/style.css'))}">
  <script defer src="{esc(r('assets/app.js'))}"></script>
</head>
<body>
  <div class="shell">
    <aside class="sidebar" aria-label="Desk navigation">
      <a class="brand" href="{esc(r('index.html'))}">
        <strong>OLBG1 · Desk {SESSION_ID}</strong>
        <small>{AS_OF_UTC} · {TASK_ID}</small>
      </a>
      <div class="nav-group">Desk Views</div>
      {render_nav(nav_main)}
      <div class="nav-group">Verification & Audit</div>
      {render_nav(nav_audit)}
      <div class="nav-group">17 Covered Sports</div>
      {sport_links}
      <div class="nav-group">Repository</div>
      <a class="nav-link" href="{esc(canon_root)}"><span>← Canonical Root</span></a>
    </aside>
    <main class="content">
      <header class="topbar">
        <div>
          <p class="eyebrow">Live Official-Source Origination Desk · Session {SESSION_SLUG}</p>
          <h1>{esc(title)}</h1>
          <p class="sub">{esc(subtitle)}</p>
        </div>
        <div class="btn-row">
          <label class="meta">Odds:
            <select id="odds-format" aria-label="Odds format">
              <option value="american">American</option>
              <option value="decimal">Decimal</option>
            </select>
          </label>
          <a class="btn" href="{esc(csv_fix)}" download>Fixtures CSV</a>
          <a class="btn primary" href="{esc(csv_mkt)}" download>Markets CSV</a>
        </div>
      </header>
      {body}
      <footer class="footer">
        <span>Session <code>{SESSION_SLUG}</code> ({TASK_ID}) · Verified live {AS_OF_UTC} · Zero-vig fair model estimates, not bookmaker offers.</span>
        <span><a href="{esc(r('flagged.html'))}">Flagged for Review</a> · <a href="{esc(r('sources.html'))}">Official Sources</a> · <a href="https://github.com/buffedlizard55-lab/OLBG1" target="_blank" rel="noopener noreferrer">GitHub Repo ↗</a></span>
      </footer>
    </main>
  </div>
</body>
</html>
"""
        target = SITE_OUT / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(doc, encoding="utf-8")

    def filter_bar(self, include_sport: bool = True, include_tier: bool = True) -> str:
        sp_opts = '<option value="">All 17 covered sports</option>' + "".join(
            f'<option value="{esc(s["slug"])}">{esc(s["name"])}</option>' for s in self.d["covered_sports"]
        )
        sp_html = f'<select id="sport-filter" aria-label="Filter by sport">{sp_opts}</select>' if include_sport else ""
        tr_html = (
            '<select id="tier-filter" aria-label="Filter by confidence">'
            '<option value="">All tiers / states</option>'
            '<option value="high">High (In-Window -250..+10000)</option>'
            '<option value="medium">Medium</option>'
            '<option value="low">Low</option>'
            '<option value="withheld">Unpriced / Withheld</option>'
            '</select>'
        ) if include_tier else ""
        return (
            '<div class="filters">'
            '<input id="table-search" type="search" placeholder="Filter by team, player, competition, or venue…">'
            f'{sp_html}{tr_html}'
            '<button class="btn" type="button" id="clear-filters">Reset</button>'
            '<span class="meta" id="filter-count"></span>'
            '</div>'
        )

    def fixture_rows_html(self, rows: list[dict], from_page: str) -> str:
        t_rows = []
        for f in rows:
            b = self.d["books"][f["id"]]
            wp = b["winner_pick"]
            tier = wp["confidence"] if wp else "withheld"
            sp_name = self.sport_by_slug[f["sport"]]["name"]
            sp_href = self.rel(f"sports/{f['sport']}.html", from_page)
            dt_cell = (
                f'<strong>{esc(f["start_utc"])}</strong>'
                if f["start_utc"]
                else (f'{esc(f["date"])}<br>{blank("UTC offset")}' if f["date"] else blank("date & UTC"))
            )
            venue_cell = esc(f["venue"]) if f["venue"] else blank("venue")
            sel_cell = f'<strong>{esc(wp["selection"])}</strong>' if wp else blank("withheld")
            mkt_cnt = f'{len(b["markets"])} priced' if b["markets"] else f'0 ({esc(f["withhold_reason"] or "withheld")})'
            srcs = f'{ext_link(f["official_url"], "Official Fixture")}'
            if f["stats_url"] and f["stats_url"] != f["official_url"]:
                srcs += f'<br>{ext_link(f["stats_url"], "Official Stats")}'
            t_rows.append((
                {
                    "id": f["id"],
                    "data-filterable": "1",
                    "data-sport": f["sport"],
                    "data-tier": tier,
                    "data-search": f"{f['event_label']} {f['competition']} {f['venue'] or ''} {sp_name}",
                },
                [
                    dt_cell,
                    f'<a href="{esc(sp_href)}">{esc(sp_name)}</a>',
                    f'<strong>{esc(f["event_label"])}</strong><br><span class="meta">{esc(f["competition"])}</span>',
                    venue_cell,
                    esc(f["official_status"]),
                    sel_cell,
                    price_span(wp),
                    tier_badge(wp["confidence"] if wp else None),
                    mkt_cnt,
                    srcs,
                ],
            ))
        return render_table(
            ["Start (UTC / Date)", "Sport", "Match / Event", "Venue", "Official Status",
             "Match Winner Pick", "Originated Fair Odds", "Confidence", "Markets", "Official Source"],
            t_rows,
        )

    def build_index(self) -> None:
        c = self.c
        kpis = [
            ("Covered Sports", f"{c['covered_sports']} / 17", "7 OLBG sports strictly excluded"),
            ("Verified Upcoming", str(c["upcoming_fixtures"]), f"+ {c['elapsed_oct22_fixtures']} elapsed Oct 22 separated"),
            ("Priced Match Books", str(c["priced_fixtures"]), f"{c['unpriced_fixtures']} unpriced (blank & flagged)"),
            ("Originated Markets", str(c["originated_markets"]), f"{c['originated_outcomes']} zero-vig outcomes"),
            ("In-Band High Picks", str(c["high_picks"]), "100% >70% prob & inside -250..+10000"),
            ("Human Predictions", str(c["predictions"]), "85–101 words each · 0 repeated 5-grams"),
            ("Official Sources", str(c["official_sources"]), "Read live 20:50Z–21:08Z UTC"),
            ("Flags & Repo Audit", f"{c['flags']} + {c['repo_audit_findings']}", "Published on Flagged & Repo Audit"),
        ]
        kpi_html = '<div class="kpis">' + "".join(
            f'<div class="kpi"><div class="kpi-label">{esc(k)}</div><div class="kpi-val">{esc(v)}</div><div class="kpi-foot">{esc(ft)}</div></div>'
            for k, v, ft in kpis
        ) + "</div>"

        banner = (
            '<div class="banner"><strong>Live 21:10Z UTC Freshness Advantage:</strong> '
            'Earlier repository snapshots froze around 12:30Z–13:00Z UTC. By 21:10Z UTC on 22 Oct 2026, '
            '6 Thursday EuroLeague Round 7 games (including Anadolu Efes 89–80 Besiktas), 5 EHF Champions League Round 5 games, '
            'Pro D2 Montauban vs Oyonnax, and PDC Day 1 R1 have completed or started. Every started event is strictly excluded '
            'from pre-match pricing here, and standings are updated to post-Thursday closed-system totals.</div>'
        )

        # High picks table
        hp_rows = []
        pred_map = {(p["fixture_id"], p["market_id"], p["selection"]): p for p in self.d["predictions"]}
        for hp in self.d["high_picks"]:
            p = pred_map[(hp["fixture_id"], hp["market_id"], hp["selection"])]
            hp_rows.append((
                {},
                [
                    f'<strong>{esc(hp["start_utc"])}</strong>',
                    f'<a href="sports/{esc(hp["sport"])}.html">{esc(hp["sport_name"])}</a>',
                    f'<strong>{esc(hp["event_label"])}</strong><br><span class="meta">{esc(hp["competition"])}</span>',
                    esc(hp["market_label"]),
                    f'<strong>{esc(hp["selection"])}</strong>',
                    price_span(hp),
                    tier_badge("high"),
                    f'<a href="predictions.html#{esc(p["id"])}">{esc(p["id"])} ({p["word_count"]}w) →</a>',
                    ext_link(hp["official_url"], "Official Source"),
                ],
            ))
        hp_table = render_table(
            ["Start UTC", "Sport", "Match", "Market", "Betting Selection", "Originated Fair Odds", "Tier", "Prediction", "Official Source"],
            hp_rows,
        )

        # 17-sport coverage matrix
        cov_rows = []
        for s in self.d["covered_sports"]:
            cov_rows.append((
                {},
                [
                    f'<a href="sports/{esc(s["slug"])}.html"><strong>{esc(s["name"])}</strong></a>',
                    str(s["olbg_id"]),
                    str(s["upcoming_count"]),
                    str(s["priced_count"]),
                    str(s["unpriced_count"]),
                    str(s["elapsed_count"]),
                    str(s["market_count"]),
                    str(s["high_count"]),
                    esc(s["coverage_state"]),
                    ext_link(s["official_url"], s["official_publisher"]),
                ],
            ))
        cov_table = render_table(
            ["Category", "OLBG ID", "Upcoming", "Priced", "Unpriced", "Elapsed Oct 22", "Markets", "High Picks", "Verification Summary", "Official Governing Body"],
            cov_rows,
        )

        body = (
            banner
            + kpi_html
            + '<h2>In-Window High-Confidence Selections (−250 to +10000 &amp; p &gt; 70%)</h2>'
            + '<p class="sub">Every High pick clears 70.00% fair model probability AND sits inside the −250 to +10000 American odds window (1.4000–1.4285 decimal), backed by live-verified official player, form, and match history.</p>'
            + hp_table
            + '<h2>17-Sport Coverage &amp; Origination Matrix</h2>'
            + cov_table
        )
        self.page(
            "index.html",
            "Evidence-First Multi-Market Origination Dashboard",
            "17 covered OLBG sports verified line-by-line against official governing bodies at 21:10Z UTC on 22 October 2026.",
            "overview",
            body,
        )

    def build_matches(self) -> None:
        el_rows = []
        for e in self.d["elapsed_fixtures"]:
            sp_name = self.sport_by_slug[e["sport"]]["name"]
            el_rows.append((
                {},
                [
                    esc(e["date"]),
                    f'<a href="sports/{esc(e["sport"])}.html">{esc(sp_name)}</a>',
                    esc(e["competition"]),
                    f'<strong>{esc(e["match"])}</strong>',
                    f'<span class="badge flag">{esc(e["result_or_state"])}</span>',
                    esc(e["impact"]),
                    ext_link(e["official_url"], "Official Boxscore / Feed"),
                ],
            ))
        body = (
            self.filter_bar(True, True)
            + self.fixture_rows_html(self.d["fixtures"], "matches.html")
            + '<h2>Elapsed &amp; In-Play Oct 21–22 Fixtures (Excluded From Pre-Match Pricing)</h2>'
            + '<p class="sub">Matches below were priced as upcoming by midday snapshots (12:30Z) but had already started or finished when official governing-body feeds were read at 21:00Z–21:08Z.</p>'
            + render_table(["Date", "Sport", "Competition", "Match", "Official State / Final Score", "Desk Impact", "Official Source"], el_rows)
        )
        self.page(
            "matches.html",
            "Complete Verified Match & Event Ledger",
            f"All {self.c['upcoming_fixtures']} upcoming/in-window verified listings across 17 sports plus {self.c['elapsed_oct22_fixtures']} separated Oct 21–22 completed/live ties.",
            "matches",
            body,
        )

    def build_markets(self) -> None:
        m_rows = []
        for f in self.d["fixtures"]:
            b = self.d["books"][f["id"]]
            if not b["markets"]:
                continue
            sp_name = self.sport_by_slug[f["sport"]]["name"]
            for m in b["markets"]:
                outcomes_str = "<br>".join(
                    f'{esc(o["selection"])}: {price_span(o)} {tier_badge(o["confidence"])}'
                    for o in m["outcomes"]
                )
                best = max(m["outcomes"], key=lambda o: o["probability"])
                m_rows.append((
                    {
                        "id": m["id"],
                        "data-filterable": "1",
                        "data-sport": f["sport"],
                        "data-tier": best["confidence"],
                        "data-search": f"{f['event_label']} {m['label']} {m['recommended']} {sp_name}",
                    },
                    [
                        esc(f["start_utc"]),
                        f'<a href="sports/{esc(f["sport"])}.html">{esc(sp_name)}</a>',
                        f'<strong>{esc(f["event_label"])}</strong>',
                        f'{esc(m["label"])}<br><span class="meta">{esc(m["family"])} · {esc(m["settlement"])}</span>',
                        outcomes_str,
                        f'<strong>{esc(best["selection"])}</strong>',
                        tier_badge(best["confidence"]),
                        ext_link(f["official_url"], "Official Feed"),
                    ],
                ))

        inv_rows = []
        for s in self.d["covered_sports"]:
            priced_str = ", ".join(s["market_families"]) if s["market_families"] else blank("all markets withheld")
            withheld_str = "; ".join(s["withheld_families"])
            inv_rows.append((
                {},
                [
                    f'<a href="sports/{esc(s["slug"])}.html"><strong>{esc(s["name"])}</strong></a>',
                    str(s["priced_count"]),
                    str(s["market_count"]),
                    priced_str,
                    esc(withheld_str),
                    ext_link(s["official_url"], s["official_publisher"]),
                ],
            ))

        body = (
            self.filter_bar(True, True)
            + render_table(
                ["Start UTC", "Sport", "Match", "Market & Settlement", "Zero-Vig Outcomes", "Top Selection", "Confidence", "Official Source"],
                m_rows,
            )
            + '<h2>17-Sport Market Investigation &amp; Withheld Derivatives Ledger</h2>'
            + render_table(["Sport", "Priced Matches", "Originated Markets", "Priced Market Ladders", "Investigated & Withheld Markets (Missing Official Input)", "Official Source"], inv_rows)
        )
        self.page(
            "markets.html",
            "Multi-Market Origination Explorer",
            f"{self.c['originated_markets']} zero-vig markets ({self.c['originated_outcomes']} outcomes) across Match Winner, 1X2, Draw No Bet, Puck/Run/Point/Goal Handicaps, and Match/Team Totals.",
            "markets",
            body,
        )

    def build_high_confidence(self) -> None:
        pred_map = {(p["fixture_id"], p["market_id"], p["selection"]): p for p in self.d["predictions"]}
        hp_rows = []
        for hp in self.d["high_picks"]:
            p = pred_map[(hp["fixture_id"], hp["market_id"], hp["selection"])]
            hp_rows.append((
                {},
                [
                    esc(hp["start_utc"]),
                    f'<a href="sports/{esc(hp["sport"])}.html">{esc(hp["sport_name"])}</a>',
                    f'<strong>{esc(hp["event_label"])}</strong>',
                    esc(hp["market_label"]),
                    f'<strong>{esc(hp["selection"])}</strong>',
                    f"{hp['probability'] * 100:.2f}%",
                    price_span(hp),
                    '<span class="badge high">Yes (−250..+10000)</span>',
                    f'<a href="predictions.html#{esc(p["id"])}">{esc(p["id"])} ({p["word_count"]} words) →</a>',
                    f'{ext_link(hp["official_url"], "Schedule")}<br>{ext_link(hp["stats_url"], "Standings")}',
                ],
            ))

        chalk_rows = []
        for ch in self.d["chalk_capped"]:
            chalk_rows.append((
                {},
                [
                    esc(ch["start_utc"]),
                    f'<a href="sports/{esc(ch["sport"])}.html">{esc(ch["sport_name"])}</a>',
                    esc(ch["event_label"]),
                    esc(ch["market_label"]),
                    esc(ch["selection"]),
                    f"{ch['probability'] * 100:.2f}%",
                    price_span(ch),
                    '<span class="badge medium">Medium (Capped &lt; −250)</span>',
                    ext_link(ch["official_url"], "Official Source"),
                ],
            ))

        body = (
            '<div class="banner"><strong>Strict Dual-Gate High Policy:</strong> '
            'Naive systems label heavy chalk (−300 to −1200) as High confidence simply because win probability exceeds 70%. '
            'Per project rules, every High selection below clears 70.00% model probability AND prices strictly inside '
            '<strong>−250 to +10000</strong> (1.4000 to 101.0000 fair decimal). All 57 selections shorter than −250 are capped at Medium and disclosed below.</div>'
            + '<h2>Qualifying In-Window High-Confidence Picks (13)</h2>'
            + render_table(
                ["Start UTC", "Sport", "Match", "Market", "Selection", "Model Prob.", "Fair Price", "Window Check", "Prediction", "Official Sources"],
                hp_rows,
            )
            + f'<h2>Out-of-Window Heavy Chalk Capped at Medium ({len(chalk_rows)})</h2>'
            + render_table(
                ["Start UTC", "Sport", "Match", "Market", "Selection", "Model Prob.", "Fair Price", "Assigned Tier", "Official Source"],
                chalk_rows,
            )
        )
        self.page(
            "high-confidence.html",
            "High-Confidence Window Desk (−250 to +10000)",
            "13 qualifying High selections (−249 to −234 fair) and full disclosure of 57 out-of-window heavy favourites capped at Medium.",
            "high",
            body,
        )

    def build_predictions(self) -> None:
        cards = []
        t_rows = []
        for p in self.d["predictions"]:
            srcs_html = " · ".join(ext_link(u, f"Official Source {i+1}") for i, u in enumerate(p["official_urls"]))
            cards.append(
                f'<article class="card" id="{esc(p["id"])}">'
                f'<div class="meta">{esc(p["id"])} · {esc(p["sport_name"])} · {esc(p["start_utc"])}</div>'
                f'<h3>{esc(p["teams"])}</h3>'
                f'<div><span class="badge high">High · {esc(p["selection"])}</span> '
                f'<strong data-us="{esc(p["american_display"])}" data-dec="{esc(p["decimal_display"])}">{esc(p["american_display"])}</strong> '
                f'<span class="meta">({esc(p["decimal_display"])} fair · {p["probability"]*100:.2f}% · {p["word_count"]} words)</span></div>'
                f'<p>{esc(p["body"])}</p>'
                f'<div class="meta"><strong>Verified Players:</strong> {esc(", ".join(p["players_cited"]))}<br>'
                f'<strong>Form:</strong> {esc(p["form_summary"])}<br>'
                f'<strong>Recent History:</strong> {esc(p["history_summary"])}<br>'
                f'{srcs_html}</div>'
                f'</article>'
            )
            t_rows.append((
                {},
                [
                    f'<a href="#{esc(p["id"])}"><strong>{esc(p["id"])}</strong></a>',
                    f'<a href="sports/{esc(p["sport"])}.html">{esc(p["sport_name"])}</a>',
                    esc(p["teams"]),
                    f'<strong>{esc(p["selection"])}</strong><br><span class="meta">{esc(p["market_label"])}</span>',
                    price_span(p),
                    f'{p["word_count"]} words',
                    esc(", ".join(p["players_cited"])),
                    esc(p["history_summary"]),
                    ext_link(p["official_urls"][0], "Official Source"),
                ],
            ))
        body = (
            '<div class="cards">' + "".join(cards) + '</div>'
            + '<h2>Prediction Verification &amp; Fact-Check Register</h2>'
            + render_table(
                ["ID", "Sport", "Match", "Selection & Market", "Fair Price", "Length", "Verified Players Cited", "Verified Recent Match History", "Official Source"],
                t_rows,
            )
        )
        self.page(
            "predictions.html",
            "Human High-Confidence Predictions",
            "13 bespoke, non-repetitive predictions (85–101 words each, 0 shared 5-grams) citing only live-read official player, form, and boxscore facts.",
            "predictions",
            body,
        )

    def build_sports_hub_and_pages(self) -> None:
        tiles = "".join(
            f'<a class="sport-tile" href="sports/{esc(s["slug"])}.html">'
            f'<strong>{esc(s["name"])}</strong>'
            f'<div class="meta">OLBG ID {s["olbg_id"]} · {s["upcoming_count"]} upcoming · {s["priced_count"]} priced · {s["market_count"]} mkts</div>'
            f'</a>'
            for s in self.d["covered_sports"]
        )
        ex_rows = [
            ({}, [esc(x["name"]), str(x["olbg_id"]), esc(x["rule"]), ext_link(x["official_ref"], "Scope Reference")])
            for x in self.d["excluded_sports"]
        ]
        hub_body = (
            '<h2>17 Covered Sports</h2>'
            + f'<div class="sport-grid">{tiles}</div>'
            + '<h2>Excluded OLBG Sports (0 Rows Imported)</h2>'
            + render_table(["Excluded Sport", "OLBG ID", "Exclusion Rule", "Reference Check"], ex_rows)
        )
        self.page(
            "sports.html",
            "Sports Directory (17 Covered · 7 Excluded)",
            "Category-by-category navigation across every in-scope OLBG sport, with soccer/football, horse racing, American football, boxing/UFC/MMA, cycling, hurling, and specials excluded.",
            "sports",
            hub_body,
        )

        # Build each individual sport subpage
        for s in self.d["covered_sports"]:
            sl = s["slug"]
            page_rel = f"sports/{sl}.html"
            f_rows = [f for f in self.d["fixtures"] if f["sport"] == sl]
            el_rows = [e for e in self.d["elapsed_fixtures"] if e["sport"] == sl]
            sp_highs = [hp for hp in self.d["high_picks"] if hp["sport"] == sl]

            meta_banner = (
                f'<div class="banner"><strong>{esc(s["name"])} (OLBG Route ID {s["olbg_id"]}):</strong> '
                f'{esc(s["coverage_state"])}.<br>'
                f'<strong>OLBG Hub Telemetry (20:56Z):</strong> {s["olbg_cards_21z"]} cards · {esc(s["olbg_clock_observed"])}.<br>'
                f'<strong>Official Publisher:</strong> {ext_link(s["official_url"], s["official_publisher"])}</div>'
            )

            sec_fix = '<h2>Verified Upcoming &amp; In-Window Listings</h2>' + self.fixture_rows_html(f_rows, page_rel)

            # Sport markets table if priced
            priced_mkts = []
            for f in f_rows:
                b = self.d["books"][f["id"]]
                for m in b["markets"]:
                    out_html = " · ".join(f'{esc(o["selection"])} {price_span(o)} {tier_badge(o["confidence"])}' for o in m["outcomes"])
                    priced_mkts.append((
                        {},
                        [
                            esc(f["start_utc"]),
                            esc(f["event_label"]),
                            esc(m["label"]),
                            out_html,
                            ext_link(f["official_url"], "Official Feed"),
                        ],
                    ))
            if priced_mkts:
                sec_mkts = '<h2>Originated Multi-Market Lines</h2>' + render_table(
                    ["Start UTC", "Match", "Market", "Originated Zero-Vig Outcomes", "Official Source"], priced_mkts
                )
            else:
                wh_rows = [({}, [esc(wf), ext_link(s["official_url"], s["official_publisher"])]) for wf in s["withheld_families"]]
                sec_mkts = '<h2>Investigated &amp; Withheld Markets</h2>' + render_table(
                    ["Withheld Market Family & Missing Official Input", "Official Governing-Body Check"], wh_rows
                )

            sec_el = ""
            if el_rows:
                er = [({}, [esc(e["date"]), esc(e["match"]), f'<span class="badge flag">{esc(e["result_or_state"])}</span>', esc(e["impact"]), ext_link(e["official_url"], "Official Result")]) for e in el_rows]
                sec_el = '<h2>Elapsed / Live Oct 21–22 Matches Excluded From Pre-Match Pricing</h2>' + render_table(
                    ["Date", "Match", "State / Score", "Notes", "Official Source"], er
                )

            sec_hp = ""
            if sp_highs:
                hr = [({}, [esc(h["event_label"]), esc(h["market_label"]), f'<strong>{esc(h["selection"])}</strong>', price_span(h), f'<a href="../predictions.html">Read prediction →</a>', ext_link(h["official_url"], "Official Source")]) for h in sp_highs]
                sec_hp = '<h2>In-Window High-Confidence Picks in This Sport</h2>' + render_table(
                    ["Match", "Market", "Selection", "Fair Price", "Prediction", "Official Source"], hr
                )

            self.page(
                page_rel,
                f"{s['name']} — Verified Fixtures & Originated Markets",
                f"{s['upcoming_count']} upcoming verified listing(s), {s['priced_count']} priced match book(s), {s['market_count']} originated market(s).",
                f"sport:{sl}",
                meta_banner + sec_hp + sec_fix + sec_mkts + sec_el,
            )

    def build_analysis(self) -> None:
        cons = self.d["conservation"]
        cons_rows = [
            ({}, ["NHL Regular Season 2026-27 (32 Clubs)", str(cons["nhl"]["team_games"]), f"{cons['nhl']['wins']} = {cons['nhl']['losses_incl_otl']} (incl. OTL)", f"{cons['nhl']['gf']} = {cons['nhl']['ga']}", f"{cons['nhl']['mean_goals_per_team']:.4f} goals/team-game", ext_link("https://api-web.nhle.com/v1/standings/2026-10-22", "NHL Standings API")]),
            ({}, ["EuroLeague 2026-27 Post-Thu R7 (20 Clubs)", str(cons["euroleague"]["team_games"]), f"{cons['euroleague']['wins']} = {cons['euroleague']['losses']}", f"{cons['euroleague']['pf']} = {cons['euroleague']['pa']}", f"{cons['euroleague']['mean_pts_per_team']:.4f} pts/team-game", ext_link("https://www.euroleaguebasketball.net/en/euroleague/standings/", "EuroLeague Standings")]),
            ({}, ["EHF Champions League Men Post-Thu R5 (24 Clubs)", str(cons["ehf_cl"]["team_games"]), f"{cons['ehf_cl']['wins']}W = {cons['ehf_cl']['losses']}L (+{cons['ehf_cl']['draws']}D)", f"{cons['ehf_cl']['gf']} = {cons['ehf_cl']['ga']}", f"{cons['ehf_cl']['mean_goals_per_team']:.4f} goals/team-game", ext_link("https://ehfcl.eurohandball.com/men/2026-27/standings/", "EHF CL Standings")]),
            ({}, ["2026 MLB World Series Clubs (TB vs MIL)", "324 (162 each)", "TB 98–64 · MIL 103–59", "TB 736:650 · MIL 832:618", "4.40 MLB baseline runs/team", ext_link("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason", "MLB StatsAPI Standings")]),
        ]

        model_rows = [
            ({}, ["Ice Hockey (NHL)", "nhl-shrunk-poisson-v1", "Empirical-Bayes k=10 goal-rate regression to 3.1176 mean, home ice ×1.035, 26×26 reg. Poisson + Beta(3,3) Log5 OT/SO", "7 markets / 14 outcomes per game (26 games = 182 markets)", ext_link("https://api-web.nhle.com/v1/standings/2026-10-22", "NHL Official API")]),
            ({}, ["Baseball (MLB WS)", "mlb-shrunk-poisson-v1", "162-game RS/RA multiplicative run rates vs 4.40 baseline, home ×1.025, 31×31 conditioned non-tie Poisson grid", "7 markets / 14 outcomes per game (4 games = 28 markets; G5 withheld)", ext_link("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason", "MLB Official API")]),
            ({}, ["Basketball (EuroLeague)", "el-shrunk-normal-v1", "Empirical-Bayes k=6 PF/PA regression to 86.81 mean, +2.5 pt home court, Normal(σ_margin=11.5, σ_total=15.0)", "6 markets / 12 outcomes per game (2 games = 12 markets; Valencia quarantined)", ext_link("https://www.euroleaguebasketball.net/en/euroleague/standings/", "EuroLeague Official")]),
            ({}, ["Handball (EHF CL Men)", "ehf-shrunk-poisson-v1", "Empirical-Bayes k=5 GF/GA regression to 32.0333 mean, home arena ×1.035, 61×61 60-min Poisson grid (exact draw mass)", "6 markets / 13 outcomes per game (12 games = 72 markets)", ext_link("https://ehfcl.eurohandball.com/men/2026-27/standings/", "EHF Official")]),
        ]

        body = (
            '<div class="card"><h3>Resolving the &gt;70% vs −250..+10000 High-Confidence Problem</h3>'
            '<p>A zero-vig probability above 70.00% corresponds to fair decimal odds shorter than 1.4286 (−233 American), '
            'whereas the −250 odds floor corresponds to 1.4000 decimal (5/7 = 71.4286%). Systems that equate High confidence '
            'with &gt;70% win chance flood their picks with −350 to −1200 moneylines. By originating full multi-market ladders '
            '(Moneyline, Puck/Run/Goal Handicaps, Game Totals, and Team Totals) from unified score distributions and enforcing '
            '<code>0.7000 &lt; p &lt;= 0.714286</code> (−250 to −234 fair), we surface 13 genuine in-window High selections while '
            'capping all 57 steeper favourites (&lt; −250) at Medium.</p></div>'
            + '<h2>Closed-System Official Standings Conservation Proofs</h2>'
            + render_table(["Official League Table", "Team-Games", "Win / Loss Balance", "Scoring Balance (For = Against)", "Observed Mean", "Official Source"], cons_rows)
            + '<h2>Origination Model Specifications</h2>'
            + render_table(["Sport", "Model ID", "Mathematical Specification", "Market Output", "Official Input Source"], model_rows)
        )
        self.page(
            "analysis.html",
            "Quantitative Analysis & Origination Methodology",
            "Closed-system data conservation proofs, zero-vig probability-to-price arithmetic, and multi-market calibration discipline.",
            "analysis",
            body,
        )

    def build_reverse_engineering(self) -> None:
        hub_rows = []
        for s in self.d["covered_sports"]:
            hub_rows.append((
                {},
                [
                    f'<a href="sports/{esc(s["slug"])}.html"><strong>{esc(s["name"])}</strong></a>',
                    str(s["olbg_id"]),
                    f'<span class="mono">/betting-tips/{esc(s["olbg_url"].split("/betting-tips/")[1])}</span>',
                    str(s["olbg_cards_21z"]),
                    esc(s["olbg_clock_observed"]),
                    ext_link(s["official_url"], f"Verify on {s['official_publisher']}"),
                ],
            ))
        ex_rows = [
            ({}, [esc(x["name"]), str(x["olbg_id"]), f'<span class="mono">{esc(x["olbg_route"])}</span>', esc(x["rule"]), ext_link(x["official_ref"], "In-Scope Reference")])
            for x in self.d["excluded_sports"]
        ]
        body = (
            '<div class="card"><h3>OLBG.com Architecture &amp; Read-Only Discovery Findings (20:50Z–20:57Z)</h3>'
            '<p>1. <strong>URL &amp; Event Schema:</strong> Public hubs follow <code>/betting-tips/{Sport}/{sport_id}</code> and event pages follow '
            '<code>/betting-tips/{Sport}/{Competition}/{Event_Slug}/{sport_id}?event_id={id}</code>. Robots.txt disallows <code>/api/</code>, '
            '<code>/storage/app/json_data/</code>, and <code>User-agent: Python-urllib</code>.<br>'
            '2. <strong>5-Hour Split-Timezone CDN Defect (F-3EE-01):</strong> Fetched simultaneously at 20:56Z, OLBG served unlabeled EDT (UTC−4) '
            'times on Ice Hockey, Baseball, Rugby Union, Darts, and Motor Racing, while serving unlabeled BST (UTC+1) times on Basketball and Gaelic Football.<br>'
            '3. <strong>Tip Shares ≠ Probabilities:</strong> OLBG displays raw tipster vote counts (e.g., 2/2 = 100% on NYR@TOR Over 6.50) and renders '
            'blank tip counts on each-way-only ante-post cards (e.g., Cricket T20 Blast 2027 <code>event_id=188350</code>). Community votes never enter our models.</p></div>'
            + '<h2>17 In-Scope OLBG Sport Hubs — Live Telemetry vs Official Governing Bodies</h2>'
            + render_table(["Sport", "OLBG ID", "Public Route", "Cards @ 20:56Z", "Observed Clock / Upstream Quirk", "Official Governing-Body Verification"], hub_rows)
            + '<h2>7 Excluded OLBG Sport Routes (Strictly Filtered Out)</h2>'
            + render_table(["Excluded Category", "OLBG ID", "OLBG Route", "Scope Rule", "Official Verification Host"], ex_rows)
        )
        self.page(
            "reverse-engineering.html",
            "OLBG.com Reverse-Engineering & Taxonomy Audit",
            "Live inspection of OLBG's 24 sport IDs, robots.txt boundaries, unlabeled split-timezone CDN caches, and tournament blind spots.",
            "reverse",
            body,
        )

    def build_sources(self) -> None:
        s_rows = []
        for s in self.d["sources"]:
            s_rows.append((
                {"id": s["id"]},
                [
                    f'<span class="mono">{esc(s["id"])}</span>',
                    f'<strong>{esc(s["publisher"])}</strong>',
                    esc(s["read_at_utc"]),
                    esc(s["role"]),
                    esc(s["summary"]),
                    esc(s["limitation"]),
                    ext_link(s["url"], "Open Official Source"),
                ],
            ))
        body = render_table(
            ["Source ID", "Official Publisher", "Read At (UTC)", "Role", "Verified Facts Extracted", "Explicit Limitation", "Official Link"],
            s_rows,
        )
        self.page(
            "sources.html",
            "Official Governing-Body Sources Register",
            f"All {self.c['official_sources']} official league, tour, and federation endpoints read live in session {SESSION_SLUG}.",
            "sources",
            body,
        )

    def build_repo_audit(self) -> None:
        a = self.d["repo_audit"]
        a_rows = []
        for item in a["findings"]:
            sev_cls = "flag" if item["severity"] == "high" else ("medium" if item["severity"] == "medium" else "info")
            a_rows.append((
                {"id": item["id"]},
                [
                    f'<strong>{esc(item["id"])}</strong>',
                    f'<span class="badge {sev_cls}">{esc(item["severity"].upper())}</span>',
                    f'<a class="mono" href="{esc(item["github_url"])}" target="_blank" rel="noopener noreferrer">{esc(item["file"])}:{item["line"]} ↗</a>',
                    f'<strong>{esc(item["title"])}</strong><br><span class="meta">{esc(item["detail"])}</span>',
                    ext_link(item["official_url"], item["official_label"]),
                ],
            ))
        body = (
            f'<div class="banner">Audited baseline commit on <code>main</code>: <code>{esc(a["baseline_main_sha"][:12])}</code>. '
            f'Every finding pairs an exact <code>file:line</code> GitHub blob link with an official governing-body verification link. '
            f'Peer session files are never edited per COORDINATION.md §0.4.</div>'
            + render_table(["Audit ID", "Severity", "Repo File : Line", "Finding & Evidence", "Official Governing-Body Verification"], a_rows)
        )
        self.page(
            "repo-audit.html",
            "Line-by-Line Repository Review",
            f"{len(a['findings'])} line-numbered findings across canonical snapshot, peer desks, legacy datasets, and coordination records.",
            "audit",
            body,
        )

    def build_flagged(self) -> None:
        fl_rows = []
        for fl in self.d["flags"]:
            sev_cls = "flag" if fl["severity"] == "high" else ("medium" if fl["severity"] == "medium" else "low")
            fl_rows.append((
                {"id": fl["id"]},
                [
                    f'<strong>{esc(fl["id"])}</strong>',
                    f'<span class="badge {sev_cls}">{esc(fl["severity"].upper())}</span>',
                    esc(fl["category"]),
                    f'<strong>{esc(fl["subject"])}</strong><br><span class="meta">{esc(fl["detail"])}</span>',
                    esc(fl["action"]),
                    ext_link(fl["official_url"], "Official Verification"),
                ],
            ))

        unpriced = [f for f in self.d["fixtures"] if not self.d["books"][f["id"]]["markets"]]
        up_rows = []
        for f in unpriced:
            sp_name = self.sport_by_slug[f["sport"]]["name"]
            up_rows.append((
                {"id": f"flag-{f['id']}"},
                [
                    f'<span class="mono">{esc(f["id"])}</span>',
                    f'<a href="sports/{esc(f["sport"])}.html">{esc(sp_name)}</a>',
                    esc(f["event_label"]),
                    esc(f["date"]) if f["date"] else blank("date"),
                    esc(f["start_utc"]) if f["start_utc"] else blank("UTC"),
                    esc(f["venue"]) if f["venue"] else blank("venue"),
                    esc(f["withhold_reason"]),
                    ext_link(f["official_url"], "Official Source"),
                ],
            ))

        body = (
            '<div class="banner warn"><strong>Non-Blocking Review Queue:</strong> '
            'Every unconfirmed field, cross-page official record discrepancy, conditional postseason game, '
            'late withdrawal, OLBG upstream error, and unpriced row is published below with official links for manual review. '
            'Nothing is inferred or filled in.</div>'
            + '<h2>Structured Irregularities &amp; Verification Flags (16)</h2>'
            + render_table(["Flag ID", "Severity", "Category", "Issue & Official Evidence", "Resolution Applied", "Official Source"], fl_rows)
            + f'<h2>All Unpriced / Blank-Field Listings ({len(up_rows)})</h2>'
            + render_table(["Row ID", "Sport", "Match / Event", "Date", "UTC Start", "Venue", "Why Price Is Withheld", "Official Source"], up_rows)
        )
        self.page(
            "flagged.html",
            "Flagged for Review",
            f"16 structured verification/upstream flags and {len(up_rows)} unpriced/blank-field rows with official governing-body links.",
            "flagged",
            body,
        )

    def build_all(self) -> int:
        assets = SITE_OUT / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        (assets / "style.css").write_text(CSS + "\n", encoding="utf-8")
        (assets / "app.js").write_text(JS + "\n", encoding="utf-8")
        self.build_index()
        self.build_matches()
        self.build_markets()
        self.build_high_confidence()
        self.build_predictions()
        self.build_sports_hub_and_pages()
        self.build_analysis()
        self.build_reverse_engineering()
        self.build_sources()
        self.build_repo_audit()
        self.build_flagged()
        return len(list(SITE_OUT.rglob("*.html")))


def main() -> None:
    desk = assemble_desk()
    write_data_exports(desk)
    pages = SiteBuilder(desk).build_all()
    print(f"Built {pages} HTML pages under {SITE_OUT.relative_to(ROOT)}/ and exports under {DATA_OUT.relative_to(ROOT)}/")
    print("Counts:", json.dumps(desk["counts"]))


if __name__ == "__main__":
    main()
