#!/usr/bin/env python3
"""T9958 static dashboard builder for the 99582dd3 independent verification desk.

Renders the audited slate in ``data/99582dd3/`` (produced by
``s99582dd3_audit.py``) into a self-contained, dependency-free static site under
``99582dd3/``. Every sporting table row carries its retained official governing-body
link; unconfirmed OLBG discovery cards appear only on the flagged page. All links are
relative so the site works under ``/OLBG1/99582dd3/`` on GitHub Pages.
"""
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path

import s99582dd3_audit as audit

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "99582dd3"
DATA = ROOT / "data" / "99582dd3"
REPO_URL = "https://github.com/buffedlizard55-lab/OLBG1"

e = html.escape

NAV = [
    ("index.html", "Executive summary"),
    ("todays-picks.html", "Today & elapsed"),
    ("upcoming-picks.html", "Upcoming picks"),
    ("markets.html", "All markets"),
    ("predictions.html", "Predictions"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("repo-audit.html", "Cross-desk audit"),
    ("methodology.html", "Methodology"),
]

BADGE = {
    "high": "badge badge-high", "medium": "badge badge-med", "low": "badge badge-low",
    "elapsed": "badge badge-elapsed", "today": "badge badge-today",
    "upcoming": "badge badge-up",
}


def money(am) -> str:
    if am is None:
        return ""
    return f"+{am}" if am > 0 else f"{am}"


def pct(p) -> str:
    return "—" if p is None else f"{p * 100:.1f}%"


def src_links(urls: list[str], label: str = "Official source") -> str:
    if not urls:
        return '<span class="blank">blank — no official link retained</span>'
    out = []
    for i, u in enumerate(urls):
        text = label if len(urls) == 1 else f"{label} {i + 1}"
        out.append(f'<a href="{e(u)}" target="_blank" rel="noopener noreferrer">{text}</a>')
    return "<br>".join(out)


def layout(title: str, active: str, body: str, stamp: str, prefix: str = "") -> str:
    nav = []
    for href, label in NAV:
        cls = ' class="active"' if href == active else ""
        nav.append(f'<a{cls} href="{prefix}{href}">{label}</a>')
    sports_nav = "".join(
        f'<a href="{prefix}sports/{slug}.html">{name}</a>' for name, slug in audit.SPORTS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'none'; form-action 'none'; connect-src 'none'">
<title>{e(title)} · 99582dd3 verification desk</title>
<link rel="stylesheet" href="{prefix}assets/desk.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<aside class="sidebar">
  <a class="brand" href="{prefix}index.html"><span class="brand-mark">9958</span>
    <span><strong>OLBG verification desk</strong><small>session 99582dd3 · offline audit</small></span></a>
  <nav class="nav-group">
    <div class="nav-label">Workspace</div>
    {''.join(nav)}
  </nav>
  <nav class="nav-group">
    <div class="nav-label">15 covered sports</div>
    <div class="nav-sports">{sports_nav}</div>
  </nav>
  <div class="sidebar-foot">
    <p>Independent research · not affiliated with OLBG<br>18+ — never stake what you cannot afford to lose.</p>
  </div>
</aside>
<div class="shade" id="shade" hidden></div>
<main class="main" id="main">
  <header class="topbar">
    <button class="menu-btn" id="menuBtn" aria-label="Toggle navigation" aria-expanded="false">☰</button>
    <div><h1>{e(title)}</h1><p class="stamp">Evidence captured {audit.CAPTURE_AT} · desk built {e(stamp)}</p></div>
  </header>
  <div class="notice">
    <strong>Offline verification desk.</strong> This session's network egress is limited to GitHub,
    npm and PyPI, so no live OLBG or official-source fetch was possible. Every row below is inherited
    from retained evidence captured on 2026-10-23, re-checked arithmetically and for provenance, and
    linked to the official governing-body page recorded by the originating desk. Values that cannot be
    re-confirmed are left blank and <a href="{prefix}flagged.html">flagged</a>, never inferred.
  </div>
{body}
  <footer class="footer">
    <span>Experimental fair prices only — no bookmaker quotes, no guaranteed returns, no staking advice.</span>
    <span><a href="{REPO_URL}">Project repository</a> · <a href="{prefix}methodology.html">Methodology &amp; limitations</a></span>
  </footer>
</main>
<script src="{prefix}assets/desk.js" defer></script>
</body>
</html>
"""


def kpi(label: str, value: str, sub: str = "") -> str:
    return f'<div class="kpi"><div class="kpi-val">{value}</div><div class="kpi-label">{label}</div><div class="kpi-sub">{sub}</div></div>'


def table(headers: list[str], rows: list[list[str]], table_id: str,
          filters: tuple[str, ...] = ()) -> str:
    fbar = ""
    if filters:
        chips = ['<button class="chip active" data-filter="all">All</button>']
        for f in filters:
            chips.append(f'<button class="chip" data-filter="{f}">{f.capitalize()}</button>')
        fbar = ('<div class="filterbar" data-table="' + table_id + '">'
                '<input type="search" placeholder="Filter rows…" aria-label="Filter rows" class="rowfilter">'
                + "".join(chips) + "</div>")
    head = "".join(f"<th>{h}</th>" for h in headers)
    # Cell builders already emit their own <td> wrappers.
    body_rows = [f"<tr>{''.join(cells)}</tr>" for cells in rows]
    return f"""{fbar}
<div class="table-wrap"><table id="{table_id}">
<thead><tr>{head}</tr></thead>
<tbody>{''.join(body_rows)}</tbody></table></div>"""


def event_cells(r: dict, include_sport: bool = True) -> list[str]:
    mw, rec = r["match_winner"], r["recommended"]
    badge = BADGE.get(r["timing"], "")
    timing = f'<span class="{badge}">{r["timing"]}</span>'
    conflict = ('<br><span class="badge badge-conflict">cross-desk conflict</span>'
                if r["cross_flags"] else "")
    sport = f"<td>{e(r['sport'])}</td>" if include_sport else ""
    return [
        f"<td>{e(r['id'])}</td>",
        sport,
        f'<td class="evt"><strong>{e(r["event"])}</strong><br><span class="muted">{e(r["competition"])}</span>'
        f'<br><span class="muted">{e(r["venue"]) or "—"} · {e(r["start_utc"].replace("T", " ").replace("Z", " UTC"))}</span>{conflict}</td>',
        timing,
        f'<td>{e(mw["selection"] or "—")}<br><span class="muted">{pct(mw["prob"])} · {money(mw["american"])} · '
        f'<span class="{BADGE.get(mw["stored_grade"], "")}">{e(mw["stored_grade"])}</span></span></td>',
        f'<td><strong>{e(rec["selection"] or "—")}</strong><br><span class="muted">{e(rec["market"] or "")}</span></td>',
        f'<td><span class="{BADGE.get(rec["stored_grade"], "")}">{e(rec["stored_grade"])}</span> '
        f'{pct(rec["prob"])}<br><span class="muted">{money(rec["american"])} · dec {rec["decimal"]:.4f}</span></td>',
        f'<td>{src_links(r["official_urls"])}</td>',
    ]


def build(now_iso: str | None = None, out: Path = SITE) -> dict:
    summary = audit.run(now_iso, DATA)
    stamp = summary["generated_at"].replace("T", " ").replace("Z", " UTC")
    slate = json.loads((DATA / "slate.json").read_text())
    flags = json.loads((DATA / "flags.json").read_text())
    sources = json.loads((DATA / "sources.json").read_text())
    cross = json.loads((DATA / "cross_desk.json").read_text())
    preds = json.loads((DATA / "predictions_gated.json").read_text())
    out.mkdir(parents=True, exist_ok=True)
    (out / "sports").mkdir(exist_ok=True)
    (out / "assets").mkdir(exist_ok=True)
    (out / "assets" / "desk.css").write_text(CSS, encoding="utf-8")
    (out / "assets" / "desk.js").write_text(JS, encoding="utf-8")

    def page(name: str, title: str, body: str):
        (out / name).parent.mkdir(parents=True, exist_ok=True)
        depth = len(Path(name).parts) - 1
        prefix = "../" * depth
        active = name if depth == 0 else ""
        (out / name).write_text(layout(title, active, body, stamp, prefix), encoding="utf-8")

    # ---------------- Executive summary ---------------- #
    current_high = [r for r in slate if r["recommended"]["is_high"]
                    and r["timing"] != "elapsed" and not r["cross_flags"]]
    current_high.sort(key=lambda r: -(r["recommended"]["prob"] or 0))
    conflict_high = [r for r in slate if r["recommended"]["is_high"] and r["cross_flags"]]
    clean_high_by_sport = {name: [r for r in current_high if r["sport"] == name]
                           for name, _ in audit.SPORTS}
    kpis = "".join([
        kpi("Covered sports", str(summary["sports"]), "exact brief list, 5 events each"),
        kpi("Audited events", str(summary["events"]),
            f'{summary["timing"]["upcoming"]} upcoming · {summary["timing"]["today"]} today · {summary["timing"]["elapsed"]} elapsed'),
        kpi("Originated markets", str(summary["markets_total"]), "fair lines, re-checked arithmetically"),
        kpi("Current High picks", str(summary["high_recommended_current"]),
            f'{summary["high_recommended_with_conflict"]} carry a cross-desk conflict badge'),
        kpi("Predictions released", str(summary["predictions_released"]),
            f'{summary["predictions_withheld"]} withheld by prose gates'),
        kpi("Review flags", str(summary["flags_total"]),
            f'{summary["flags_by_severity"]["high"]} high · {summary["flags_by_severity"]["medium"]} medium · {summary["flags_by_severity"]["low"]} low'),
    ])
    top_rows = [event_cells(r) for r in current_high[:15]]
    sport_grid = "".join(
        f'<a class="sport-card" href="sports/{slug}.html"><strong>{name}</strong>'
        f'<span>{len(clean_high_by_sport[name])} clean High · {sum(1 for r in slate if r["sport"] == name)} events</span></a>'
        for name, slug in audit.SPORTS)
    conflict_rows = []
    for r in conflict_high:
        conflict_rows.append([
            e(r["id"]), e(r["sport"]),
            f'<strong>{e(r["event"])}</strong><br><span class="muted">{e("; ".join(r["cross_flags"]))}</span>',
            f'{e(r["recommended"]["selection"])}<br><span class="muted">{pct(r["recommended"]["prob"])} · {money(r["recommended"]["american"])}</span>',
            src_links(r["official_urls"]),
            '<a href="flagged.html">see flagged page</a>',
        ])
    body = f"""
<section class="panel"><h2>Key figures</h2><div class="kpis">{kpis}</div></section>
<section class="panel">
  <h2>Executive summary — highest-confidence current picks</h2>
  <p class="muted">Recommended selections above the 70% fair-probability floor, priced inside the
  −250 to +10000 window, with starts still in the future at build time and no cross-desk conflict.
  Ranked by fair probability; the complete list is on each sport page.</p>
  {table(['ID', 'Sport', 'Event', 'Timing', 'Match-winner line', 'Recommended selection', 'Grade & fair price', 'Official source'], top_rows, 'exec-table')}
</section>
<section class="panel">
  <h2>Conflict watch — not promoted to the executive summary</h2>
  <p class="muted">High-probability selections whose match-winner direction is contradicted by another
  retained desk, or whose probability diverges by more than 15 points. They remain published on their
  sport pages with a badge, but cannot be reconciled offline and need manual review against the official sources.</p>
  {table(['ID', 'Sport', 'Event', 'Desk selection', 'Official source', 'Detail'], conflict_rows, 'conflict-table')}
</section>
<section class="panel"><h2>Sport coverage</h2><div class="sport-grid">{sport_grid}</div></section>
"""
    page("index.html", "Executive summary", body)

    # ---------------- Today / elapsed & upcoming ---------------- #
    def picks_page(filename: str, title: str, subset, note: str):
        rows = [event_cells(r) for r in subset]
        body = (f'<section class="panel"><h2>{e(title)}</h2><p class="muted">{e(note)}</p>'
                + table(['ID', 'Sport', 'Event', 'Timing', 'Match-winner line',
                         'Recommended selection', 'Grade & fair price', 'Official source'],
                        rows, filename.replace(".html", ""),
                        filters=("high", "medium", "low")) + "</section>")
        page(filename, title, body)

    today_rows = [r for r in slate if r["timing"] in ("today", "elapsed")]
    picks_page("todays-picks.html", "Today's card and elapsed snapshot", today_rows,
               "Elapsed rows retain their pre-match fair lines as a historical record only; they are "
               "not current recommendations. Every row links the official source captured before start.")
    upcoming = [r for r in slate if r["timing"] == "upcoming"]
    picks_page("upcoming-picks.html", "Upcoming picks", upcoming,
               "Events starting after the build timestamp, grouped table with client-side grade filters.")

    # ---------------- Sport pages ---------------- #
    for name, slug in audit.SPORTS:
        rows_events = [r for r in slate if r["sport"] == name]
        rows_events.sort(key=lambda r: r["start_utc"])
        n_high = sum(1 for r in rows_events if r["recommended"]["is_high"] and not r["cross_flags"])
        body = [f'<section class="panel"><h2>{e(name)}</h2>',
                f'<p class="muted">{len(rows_events)} audited events · {n_high} clean current High picks · '
                f'fair lines and grades recomputed under the published rule.</p>',
                table(['ID', 'Event', 'Timing', 'Match-winner line', 'Recommended selection',
                       'Grade & fair price', 'Official source'],
                      [event_cells(r, include_sport=False) for r in rows_events],
                      f"sport-{slug}", filters=("high", "medium", "low"))]
        # compact market table for the sport
        mrows = []
        for r in rows_events:
            for m in r["markets"]:
                mrows.append([
                    e(r["id"]), e(m.get("market_label", "")), e(m.get("selection", "")),
                    pct(m.get("fair_prob")), f'{m.get("fair_decimal"):.4f}', money(m.get("fair_american")),
                    f'<span class="{BADGE.get((m.get("confidence") or "").lower(), "")}">{e(m.get("confidence", ""))}</span>',
                    src_links(r["official_urls"][:1]),
                ])
        body.append("</section><section class='panel'><h2>All originated markets</h2>"
                    + table(['Event', 'Market', 'Selection', 'Fair prob', 'Decimal', 'American',
                             'Grade', 'Official source'], mrows, f"markets-{slug}") + "</section>")
        page(f"sports/{slug}.html", name, "".join(body))

    # ---------------- Markets master table ---------------- #
    mrows = []
    for r in slate:
        for m in r["markets"]:
            mrows.append([
                e(r["id"]), e(r["sport"]), e(m.get("market_label", "")), e(m.get("selection", "")),
                pct(m.get("fair_prob")), f'{m.get("fair_decimal"):.4f}', money(m.get("fair_american")),
                ("yes" if m.get("in_window") else "no"),
                f'<span class="{BADGE.get((m.get("confidence") or "").lower(), "")}">{e(m.get("confidence", ""))}</span>',
                src_links(r["official_urls"][:1]),
            ])
    body = ('<section class="panel"><h2>All originated market lines</h2>'
            '<p class="muted">Every retained two-way market with re-derived fair price and grade. '
            '“In window” means −250 ≤ American ≤ +10000 (decimal 1.40–101.00).</p>'
            + table(['Event', 'Sport', 'Market', 'Selection', 'Fair prob', 'Decimal', 'American',
                     'In window', 'Grade', 'Official source'], mrows, "all-markets",
                    filters=("high", "medium", "low")) + "</section>")
    page("markets.html", "All markets", body)

    # ---------------- Predictions ---------------- #
    prows = []
    for p in sorted(preds, key=lambda x: (x["sport"], x["event_id"])):
        if p["withheld"] or not p["prediction"]:
            prose = '<span class="blank">withheld — failed prose gate; see flagged page</span>'
        else:
            prose = e(p["prediction"])
        badge = ('<span class="badge badge-conflict">conflict</span>' if p["cross_flags"] else "")
        prows.append([
            e(p["event_id"]), e(p["sport"]),
            f'<strong>{e(p["event"])}</strong><br><span class="muted">{e(p["start_utc"].replace("T", " "))} UTC · {e(p["timing"])}</span>',
            f'<strong>{e(p["selection"] or "—")}</strong><br><span class="muted">{e(p["market"] or "")}</span> {badge}',
            f'{pct(p["prob"])} · {money(p["american"])} · {p["word_count"]} words',
            prose, src_links(p["official_urls"]),
        ])
    body = ('<section class="panel"><h2>High-confidence predictions (gated)</h2>'
            '<p class="muted">Each prediction is at least 30 words, names its selection and both '
            'participants, contains no internal vocabulary, and carries the official source for its '
            'claims. Two minor repeated-phrase findings and one directional clause are listed on the '
            'flagged page; the affected prose remains published with the finding attached.</p>'
            + table(['ID', 'Sport', 'Event', 'Selection', 'Price / length', 'Prediction',
                     'Official source'], prows, "predictions") + "</section>")
    page("predictions.html", "Predictions", body)

    # ---------------- Flagged ---------------- #
    frows = []
    for f in flags:
        if f["source_urls"]:
            links = src_links(f["source_urls"], "Source")
        elif f["code"] == "G5-UNIQUE":
            links = '<a href="predictions.html">internal finding — see predictions page</a>'
        else:
            links = '<a href="repo-audit.html">internal finding — see cross-desk audit</a>'
        frows.append([
            e(f["id"]), f'<span class="badge badge-{f["severity"]}">{e(f["severity"])}</span>',
            e(f["code"]), e(f["sport"]), e(f["event_id"]),
            f'<strong>{e(f["subject"])}</strong><br>{e(f["detail"])}', links,
        ])
    body = ('<section class="panel"><h2>Flagged for review</h2>'
            '<p class="muted">Every irregularity found by the offline audit. High-severity flags are '
            'cross-desk directional conflicts on a match winner; medium flags cover unconfirmed OLBG '
            'cards, probability divergences and one directional prose clause; low flags are minor '
            'uniqueness findings. Nothing here is silently corrected — values stay blank until an '
            'official source confirms them.</p>'
            + table(['Flag', 'Severity', 'Code', 'Sport', 'Event', 'Finding', 'Source link'],
                    frows, "flags") + "</section>")
    page("flagged.html", "Flagged for review", body)

    # ---------------- Sources ---------------- #
    srows = []
    for s in sources:
        role = s["role"]
        links = "<br>".join(f'<a href="{e(u)}" target="_blank" rel="noopener noreferrer">{e(hostlabel(u))}</a>'
                            for u in s["urls"])
        srows.append([e(s["host"]), "official" if s["official"] else "review",
                      e(role), str(s["event_count"]), str(s["url_count"]), links])
    body = ('<section class="panel"><h2>Official source registry</h2>'
            '<p class="muted">Distinct hosts cited by the audited slate. OLBG appears only as a '
            'discovery source and is deliberately absent here; no sporting fact is accepted from it.</p>'
            + table(['Host', 'Status', 'Source role', 'Events', 'URLs', 'Recorded URLs'],
                    srows, "sources") + "</section>")
    page("sources.html", "Sources", body)

    # ---------------- Cross-desk / repo audit ---------------- #
    crows = []
    for c in cross:
        crows.append([
            e(c["event_id"]), e(c["sport"]), e(c["desk"]),
            f'{e(c["own_selection"])}<br><span class="muted">{pct(c["own_prob"])} · {money(c["own_american"])}</span>',
            f'{e(c["other_selection"])}<br><span class="muted">{pct(c["other_prob"])} · {money(c["other_american"])}</span>',
            e(c["finding"]),
            src_links([u for u in [c.get("other_official_url")] if u], "Other desk source")
            if c.get("other_official_url") else '<a href="flagged.html">see flagged page</a>',
        ])
    inventory = [
        ("8a900c04 (primary)", "75 events, 472 markets, 75 predictions", "data/8a900c04/"),
        ("429a54a2", "96 fixtures with log5 price books", "data/429a54a2/"),
        ("3ee30bba", "140 fixtures; 13 high picks; winner family reconciled", "data/3ee30bba/"),
        ("7f000cb6", "122 fixtures; 40 priced books; winner picks reconciled", "data/7f000cb6/"),
        ("cf2699ba", "6 officially confirmed fixtures (fixture corroboration only)", "data/cf2699ba/"),
        ("efe12010", "100 harvested fixtures, different schema", "data/efe12010/"),
    ]
    inv_rows = [[e(a), e(b),
                 f'<a href="{REPO_URL}/tree/main/{c.strip("/")}" target="_blank" rel="noopener noreferrer">'
                 f'<code>{e(c)}</code></a>'] for a, b, c in inventory]
    body = f"""
<section class="panel"><h2>Cross-desk reconciliation</h2>
<p class="muted">Matchups were matched on participant-name tokens (Jaccard ≥ 0.5) against three
retained desks that publish winner prices. Opposite favorite directions are high-severity conflicts;
same-side probability gaps over 15 points are divergences. Name matching cannot distinguish repeated
team pairings such as playoff rematches, which is stated in each flag.</p>
{table(['Event', 'Sport', 'Other desk', '8a900c04 winner', 'Other desk winner', 'Finding', 'Source'], crows, 'cross')}
</section>
<section class="panel"><h2>Retained datasets reviewed</h2>
{table(['Desk', 'Contents', 'Path'], inv_rows, 'inventory').replace('<table id="inventory">', '<table id="inventory" data-row-policy="internal">')}
</section>"""
    page("repo-audit.html", "Cross-desk audit", body)

    # ---------------- Methodology ---------------- #
    page("methodology.html", "Methodology and limitations", METHODOLOGY)
    return summary


def hostlabel(u: str) -> str:
    return u.replace("https://", "")[:72]


METHODOLOGY = """
<section class="panel prose">
<h2>What this desk is</h2>
<p>Session <code>99582dd3</code> is an independent <strong>offline verification and reconciliation
desk</strong>. Its sandbox can only reach GitHub, npm and PyPI; live probes confirmed that OLBG and
every sporting governing-body host fail at TLS egress. It therefore cannot harvest new fixtures or
re-fetch official pages. Instead it audits the evidence already captured and merged in this
repository, principally the <code>8a900c04</code> desk's 2026-10-23T16:45Z snapshot, which is the only
retained dataset covering five events for each of the fifteen brief-listed sports.</p>
<h2>Gate definitions</h2>
<ul>
<li><strong>G1 Provenance.</strong> Every slate row must cite at least one HTTPS URL on a curated
official governing-body, league, tour, federation or organiser host. OLBG is discovery-only and can
never verify a sporting fact. Unregistered hosts raise a manual-review flag; OLBG-only cards stay
unpriced on the flagged page.</li>
<li><strong>G2 Arithmetic.</strong> Each market must satisfy fair decimal = 1/probability (tolerance
0.011), two-way probability mass summing to 1 (tolerance 0.011), and an American price re-derived
from the probability with a 1.5% relative tolerance for long shots. American prices are derived from
the clamped probability, mirroring the originating desk, not from the rounded decimal.</li>
<li><strong>G3 Grade and window.</strong> High confidence requires probability strictly above 70% and
a fair American price between −250 and +10000 (decimal 1.40–101.00). Favorites above 70% priced
shorter than −250 are chalk-suppressed to medium. Medium otherwise begins at 57.5%; below that is low.
Every stored grade is recomputed and compared.</li>
<li><strong>G4 Timing.</strong> Starts are compared to the build timestamp: <em>today</em>,
<em>upcoming</em> or <em>elapsed</em>. Elapsed rows keep their pre-match lines as a historical record
and leave the current executive summary.</li>
<li><strong>G5 Prose.</strong> A released prediction exists, is at least 30 words, has an accurate
word-count field, contains neither internal vocabulary term, states a selection, and names a
participant. Corpus uniqueness scans for shared seven-word phrases.</li>
<li><strong>G6 Direction.</strong> The explicit selection sentence is scanned for a non-favorite
described as beating the priced match-winner favorite. Historical form clauses and distance phrases
are excluded.</li>
<li><strong>G7 Cross-desk reconciliation.</strong> Matchups are token-matched against the 429a54a2,
3ee30bba and 7f000cb6 desks. Opposite favorite directions are high-severity conflicts; same-side
probability gaps above 15 points are medium divergences. Conflicted events keep a visible badge and
are excluded from the clean executive summary rather than silently picked.</li>
</ul>
<h2>What is and is not verified</h2>
<p>The audit verifies internal consistency, provenance shape, price arithmetic, grading rule
compliance, prose quality and cross-desk agreement. It does <strong>not</strong> recertify that a
remote official page still shows the same fixture, score, injury or statistic — that requires network
access this session does not have. All factual claims remain attributed to the originating desk's
captured official sources, whose URLs are attached to every row. Unsupported values are blank and
flagged; this desk never infers, interpolates or remembers a fact.</p>
<h2>Prices are experimental</h2>
<p>Fair prices are 1/p with no bookmaker margin. No actual sportsbook quote, availability or edge is
claimed. The −250…+10000 band is the brief's eligibility window for high-confidence selections, not a
betting recommendation. Nothing here is staking advice.</p>
</section>
"""

CSS = """
:root{--bg:#f4f6f8;--panel:#fff;--ink:#16202b;--muted:#5d6b7a;--line:#e2e8ef;--accent:#175e47;--accent2:#0f4433;--warn:#9a6700;--high:#116339;--med:#8a5a00;--low:#5b6570;--conf:#a23a3a;}
*{box-sizing:border-box}body{margin:0;font:14px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg)}
.skip{position:absolute;left:-999px}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.sidebar{position:fixed;inset:0 auto 0 0;width:264px;background:#10231c;color:#dfe9e4;padding:18px 14px;overflow-y:auto}
.brand{display:flex;gap:10px;align-items:center;color:#fff;margin-bottom:18px}.brand-mark{background:var(--accent);border-radius:9px;padding:7px 9px;font-weight:800;letter-spacing:.5px}.brand small{display:block;color:#9db8ac;font-size:11px}
.nav-group{margin-bottom:16px}.nav-label{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#88a497;margin:8px 8px 6px}.nav-group a{display:block;color:#d5e1db;padding:7px 10px;border-radius:8px;font-size:13.5px}.nav-group a:hover{background:#1d3a2e;text-decoration:none}.nav-group a.active{background:var(--accent);color:#fff}
.nav-sports{display:grid;grid-template-columns:1fr 1fr;gap:2px}.nav-sports a{font-size:12.5px;padding:5px 8px}
.sidebar-foot{font-size:11.5px;color:#93ada2;border-top:1px solid #244034;margin-top:14px;padding-top:12px}
.main{margin-left:264px;padding:22px 28px 60px;max-width:1500px}.topbar{display:flex;gap:14px;align-items:center;margin-bottom:14px}.topbar h1{font-size:23px;margin:0}.stamp{margin:2px 0 0;color:var(--muted);font-size:12.5px}.menu-btn{display:none;background:none;border:1px solid var(--line);border-radius:8px;font-size:18px;padding:4px 10px}
.notice{background:#eef5f1;border:1px solid #cfe2d8;border-left:4px solid var(--accent);padding:12px 16px;border-radius:10px;margin-bottom:20px;font-size:13.5px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:22px}.panel h2{margin:0 0 10px;font-size:17px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}.kpi{background:#f8faf9;border:1px solid var(--line);border-radius:12px;padding:14px}.kpi-val{font-size:27px;font-weight:800;color:var(--accent2)}.kpi-label{font-weight:650;margin-top:2px}.kpi-sub{color:var(--muted);font-size:12px;margin-top:3px}
.sport-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}.sport-card{display:flex;flex-direction:column;gap:4px;background:#f8faf9;border:1px solid var(--line);border-radius:12px;padding:13px 15px;color:var(--ink)}.sport-card:hover{border-color:var(--accent);text-decoration:none}.sport-card span{color:var(--muted);font-size:12.5px}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px}table{border-collapse:collapse;width:100%;font-size:13px;background:#fff}th,th{position:sticky;top:0;background:#eef2f5;text-align:left;padding:9px 11px;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#41505e;white-space:nowrap}td{padding:9px 11px;border-top:1px solid var(--line);vertical-align:top;min-width:90px}td.evt{min-width:260px}tbody tr:hover{background:#f7faf8}.muted{color:var(--muted);font-size:12px}.blank{color:var(--conf);font-style:italic;font-size:12px}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:700;white-space:nowrap}.badge-high{background:#dcf3e6;color:var(--high)}.badge-med{background:#fdf0d5;color:var(--med)}.badge-low{background:#e7ebef;color:var(--low)}.badge-elapsed{background:#f3e0e0;color:var(--conf)}.badge-today{background:#e3edfb;color:#1d4f8f}.badge-up{background:#e6f4ea;color:#1d6b3c}.badge-conflict{background:#f9e2e2;color:var(--conf)}.badge-high.severity,.badge-medium.severity,.badge-low.severity,.badge-info.severity{background:#eee}
.badge-high{}.badge-medium{background:#f9e2e2;color:var(--conf)}.badge-low{background:#eef0f2;color:var(--low)}.badge-info{background:#e3edfb;color:#1d4f8f}
.filterbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}.rowfilter{padding:8px 12px;border:1px solid var(--line);border-radius:9px;min-width:240px;font-size:13px}.chip{border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 14px;cursor:pointer;font-size:12.5px}.chip.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.prose h2{margin-top:22px}.prose li{margin-bottom:7px}.prose code{background:#eef2f5;padding:1px 6px;border-radius:6px}
.footer{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:12px;border-top:1px solid var(--line);padding-top:16px;margin-top:10px}
@media(max-width:960px){.sidebar{transform:translateX(-100%);transition:transform .2s;z-index:30}.sidebar.open{transform:none}.main{margin-left:0;padding:16px}.menu-btn{display:block}.shade{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:20}}
"""

JS = """
(function(){
  var btn=document.getElementById('menuBtn'),side=document.querySelector('.sidebar'),shade=document.getElementById('shade');
  if(btn&&side){btn.addEventListener('click',function(){var open=side.classList.toggle('open');btn.setAttribute('aria-expanded',open);if(shade)shade.hidden=!open;});}
  if(shade){shade.addEventListener('click',function(){side.classList.remove('open');shade.hidden=true;btn.setAttribute('aria-expanded',false);});}
  document.querySelectorAll('.filterbar').forEach(function(bar){
    var table=document.getElementById(bar.dataset.table);if(!table)return;
    var input=bar.querySelector('.rowfilter');var active='all';
    function apply(){var q=(input.value||'').toLowerCase();
      table.querySelectorAll('tbody tr').forEach(function(tr){
        var text=tr.textContent.toLowerCase();
        var grade=(tr.querySelector('.badge-high,.badge-med,.badge-low')||{}).textContent||'';
        var okText=!q||text.indexOf(q)>=0;var okFilter=active==='all'||grade.toLowerCase()===active;
        tr.style.display=(okText&&okFilter)?'':'none';});}
    if(input)input.addEventListener('input',apply);
    bar.querySelectorAll('.chip').forEach(function(chip){chip.addEventListener('click',function(){
      bar.querySelectorAll('.chip').forEach(function(c){c.classList.remove('active');});
      chip.classList.add('active');active=chip.dataset.filter;apply();});});
  });
})();
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", help="UTC ISO timestamp for deterministic builds/tests")
    ap.add_argument("--out", type=Path, default=SITE)
    args = ap.parse_args()
    summary = build(args.now, args.out)
    pages = sorted(p.relative_to(args.out).as_posix() for p in args.out.rglob("*.html"))
    print(f"Built {len(pages)} pages under {args.out}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
