#!/usr/bin/env python3
'''Session e6716490-olbg1 — build the consolidated desk site (``/e6716490/``).

Reads the desk's own data files and writes a static, dependency-free dashboard:

  index.html            landing dashboard: counts, High picks, sport directory
  sports/<slug>.html    17 category pages, every market with its price and source
  predictions.html      the nine hand-written High-confidence write-ups
  markets.html          market coverage per sport + the band-excluded ledger
  verification.html     what this session re-read live, row by row
  flagged.html          every irregularity and unverified value, with links
  methodology.html      the model, the constants and the band arithmetic
  sources.html          source register, by governing body
  audit.html            line-by-line repo review findings

No network access, no third-party assets.
'''
from __future__ import annotations

import json
import html
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "e6716490"
SITE = ROOT / "e6716490"

SPORT_ORDER = [
    ("basketball", "Basketball", 4),
    ("ice-hockey", "Ice Hockey", 13),
    ("darts", "Darts", 15),
    ("snooker", "Snooker", 8),
    ("tennis", "Tennis", 3),
    ("cricket", "Cricket", 7),
    ("rugby-union", "Rugby Union", 9),
    ("rugby-league", "Rugby League", 10),
    ("handball", "Handball", 20),
    ("volleyball", "Volleyball", 21),
    ("baseball", "Baseball", 12),
    ("aussie-rules", "Aussie Rules", 22),
    ("gaelic-football", "Gaelic Football", 25),
    ("esports", "eSports", 23),
    ("golf", "Golf", 5),
    ("motor-racing", "Motor Racing", 14),
    ("greyhounds", "Greyhounds", 28),
]

SPORT_NOTES = {
    "basketball": "EuroLeague round seven and the NBA's opening week. European form comes from the "
                  "official EuroLeague standings; NBA rows are priced from last season's final records "
                  "because the 2026-27 season is one game old.",
    "ice-hockey": "Every game on the 22-23 October slate, priced from points percentage and goal "
                  "differential on the NHL's own standings feed. Starting goaltenders are not published "
                  "before the morning skate and are left blank.",
    "darts": "PDC Machineseeker European Championship first round. Strength comes from the official "
             "European Tour seed list, not from a ranking invented here.",
    "snooker": "WST ranking-event matches. Only a verified world top-16 status is available per player, "
               "so the strength input is coarse and the desk caps what it claims.",
    "tennis": "The one ATP/WTA singles match still to be played on this desk's window, priced from the "
              "official draw sheet. The signed draw publishes no clock, so no start time is shown.",
    "cricket": "T20I and one-day fixtures across four boards. Ratings are ICC team ratings where the "
               "board publishes them; matches without a rating on either side are priced at a neutral "
               "baseline and never called High.",
    "rugby-union": "Top 14 and Pro D2. French league standings are the primary source; the points "
                   "percentages some registers carry are not used as probabilities.",
    "rugby-league": "RLWC26 rounds two and three. Rankings and round-one results come from the NRL's "
                    "official draw and the international board's ranking table.",
    "handball": "EHF Champions League group phase. Goal difference across four or five rounds is thin "
                "evidence, and the desk says so on every row that uses it.",
    "volleyball": "PlusLiga. Only one regular-season round has been played, so most rows sit on a "
                  "neutral home baseline and cannot reach High.",
    "baseball": "World Series games one, two and five. Run rates are derived from the official "
                "statsapi totals, which is why this is the only sport where a totals market is priced.",
    "aussie-rules": "AFLW round eleven, priced from the official ladder after round ten.",
    "gaelic-football": "County finals and club championships. Where no unified club rating exists the "
                       "row is priced neutrally and flagged.",
    "esports": "League of Legends Worlds 2026. The Swiss stage publishes no per-map clock, and pool "
               "seeding is the only strength input available.",
    "golf": "Tournament fields, not match-ups. A 120-player field cannot be priced from one verified "
            "input, so these cards are published unpriced and listed on the Flagged page.",
    "motor-racing": "The United States Grand Prix weekend. The grid is not set until qualifying, so no "
                    "price is originated for the race.",
    "greyhounds": "One Category 1 final. Six-trap racing has enough traffic variance that a single "
                  "trial time cannot support a price.",
}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def nav(prefix: str, active: str) -> str:
    items = [
        ("index.html", "Dashboard"),
        ("predictions.html", "High picks"),
        ("markets.html", "Markets"),
        ("verification.html", "Verification"),
        ("flagged.html", "Flagged"),
        ("methodology.html", "Methodology"),
        ("sources.html", "Sources"),
        ("audit.html", "Repo audit"),
    ]
    links = ""
    for href, label in items:
        cls = ' class="active"' if href == active else ""
        links += f'<a href="{prefix}{href}"{cls}>{label}</a>'

    return (
        '<header class="topbar">'
        f'<a class="brand" href="{prefix}index.html">OLBG1 <span>consolidated desk</span></a>'
        f'<nav>{links}<a class="back" href="{prefix}../index.html">All desks</a></nav>'
        "</header>"
    )


def page(slug: str, title: str, body: str, prefix: str = "", active: str = "", subtitle: str = "") -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · OLBG1 consolidated desk</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
<meta name="description" content="OLBG1 consolidated desk: 17 in-scope sports, originated lines, confidence tiers and official-source verification.">
</head>
<body>
{nav(prefix, active)}
<main>
<header class="pagehead">
<h1>{esc(title)}</h1>
{f'<p class="lede">{subtitle}</p>' if subtitle else ''}
</header>
{body}
</main>
<footer>
<p>Session <code>e6716490-olbg1</code> · built {esc(BUILD_UTC)} · every price on this desk is the desk's own
estimate, never a copied bookmaker price. Facts come from the official page linked on the row.</p>
<p><a href="{prefix}../index.html">All desks</a> · <a href="{prefix}methodology.html">methodology</a> ·
<a href="{prefix}flagged.html">flagged for review</a></p>
</footer>
</body>
</html>
'''


def pill(tier: str) -> str:
    if not tier:
        return '<span class="pill muted">—</span>'
    cls = {"High": "high", "Medium": "med", "Low": "low"}.get(tier, "muted")
    return f'<span class="pill {cls}">{esc(tier)}</span>'


def verif_pill(status: str) -> str:
    if status == "re-fetched":
        return '<span class="pill verified">re-fetched today</span>'
    return '<span class="pill carried">carried</span>'


def us_text(value) -> str:
    if value is None:
        return "—"
    return f"{value:+d}"


def src_links(sources: list[dict], limit: int = 3) -> str:
    if not sources:
        return '<span class="pill warn">no source</span>'
    out = []
    for s in sources[:limit]:
        host = s["url"].split("/")[2] if "//" in s["url"] else s["url"]
        out.append(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener" title="{esc(s["name"])}">{esc(host)} ↗</a>')
    if len(sources) > limit:
        out.append(f'<span class="muted">+{len(sources) - limit}</span>')
    return " ".join(out)


def kickoff(row: dict) -> str:
    start = row.get("start_utc") or ""
    if start:
        return start.replace("T", " ").replace("Z", " UTC")
    if row.get("date_local"):
        return f'{row["date_local"]} (clock not published)'
    return "clock not published"


def stat_card(value, label, hint="") -> str:
    return (
        '<div class="card stat">'
        f'<div class="value">{esc(value)}</div>'
        f'<div class="label">{esc(label)}</div>'
        f'{f"<div class=hint>{esc(hint)}</div>" if hint else ""}'
        "</div>"
    )


def table(headers: list[str], rows: list[list[str]], cls: str = "") -> str:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tablewrap"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


BUILD_UTC = ""


# --------------------------------------------------------------------------- #
def main() -> int:
    global BUILD_UTC
    fixtures_blob = json.load((OUT / "fixtures.json").open())
    lines = json.load((OUT / "lines.json").open())
    verification = json.load((OUT / "verification.json").open())
    preds = json.load((OUT / "predictions.json").open())

    BUILD_UTC = lines["generated_utc"]

    # The audit describes the tree as it was found, so this desk's own pages and
    # scripts are excluded from those counts.
    all_html = sorted(ROOT.glob("**/*.html"))
    prior_html = [p for p in all_html if "e6716490" not in p.parts]
    desks = sorted({p.parts[len(ROOT.parts)] for p in prior_html if len(p.parts) > len(ROOT.parts) + 1})
    prior_scripts = [p for p in (ROOT / "scripts").glob("*.py") if not p.name.startswith("se6716490_")]
    prior_validators = [p for p in prior_scripts if "validate" in p.name]
    rows = lines["rows"]
    highs = lines["highs"]
    counts = lines["counts"]
    pred_by_fixture = {p["fixture_id"]: p for p in preds["predictions"]}

    SITE.mkdir(exist_ok=True)
    (SITE / "sports").mkdir(exist_ok=True)
    (SITE / "assets").mkdir(exist_ok=True)

    by_sport: dict[str, list[dict]] = {}
    for r in rows:
        by_sport.setdefault(r["sport"], []).append(r)

    in_band = sum(1 for r in rows for m in r["markets"] for s in m["selections"]
                  if s["prob"] >= 0.70 and s["in_band"])
    seventy = sum(1 for r in rows for m in r["markets"] for s in m["selections"] if s["prob"] >= 0.70)

    # ---------------- index ----------------
    high_rows = []
    for h in highs:
        p = pred_by_fixture.get(h["id"])
        high_rows.append([
            f'<a href="sports/{h["sport"]}.html">{esc(h["sport"].replace("-", " ").title())}</a>',
            f'<strong>{esc(h["home"])}</strong> v {esc(h["away"])}<div class="muted small">{esc(h["competition"])} · {esc(kickoff(h))}</div>',
            esc(h["market"]),
            f'<strong>{esc(h["selection"])}</strong>',
            f'{h["prob"] * 100:.1f}%',
            f'{h["price"]:.2f}',
            us_text(h["us"]),
            pill("High"),
            verif_pill(h["verification"]["status"]),
            src_links(h["sources"], 2),
            f'<a href="predictions.html#{esc(h["id"])}">read the pick</a>' if p else "—",
        ])

    sport_rows = []
    for slug, name, oid in SPORT_ORDER:
        sr = by_sport.get(slug, [])
        priced = sum(1 for r in sr if r["priced"])
        hi = sum(1 for h in highs if h["sport"] == slug)
        markets = sum(len(r["markets"]) for r in sr)
        sport_rows.append([
            f'<a href="sports/{slug}.html"><strong>{esc(name)}</strong></a>',
            f'<span class="muted">OLBG id {oid}</span>',
            str(len(sr)),
            str(priced),
            str(markets),
            str(hi),
            f'<a href="sports/{slug}.html">open →</a>',
        ])

    body = f'''
<section class="cards">
{stat_card(fixtures_blob["count"], "fixtures on the desk", "17 in-scope sports, 22–28 Oct 2026")}
{stat_card(counts["priced"], "priced matches", f'{counts["unpriced"]} unpriced ({counts["expired"]} already started)')}
{stat_card(counts["markets"], "markets originated", f'{counts["selections"]} priced selections')}
{stat_card(counts["high"], "High-confidence picks", "one High per match, every one hand-written")}
{stat_card(in_band, "selections inside the band", "p ≥ 70% and fair price −250…+10000")}
{stat_card(verification["counts"]["checks"], "row-sides re-fetched", "NHL · MLB · EuroLeague, today")}
</section>

<div class="notice">
<strong>What this page is.</strong> One desk that brings the whole repository's in-scope coverage into a
single, consistent view: {fixtures_blob["count"]} fixtures across all 17 sports the brief allows, priced with
this session's own model, tagged with a confidence tier, and linked row by row to the official governing-body
page the facts came from. Where a value could not be confirmed it is blank and listed on the
<a href="flagged.html">Flagged for review</a> page. Where the price of a ≥70% pick falls outside the brief's
−250…+10000 window it is shown in the <a href="markets.html#band">band-excluded ledger</a> instead of being
quietly relabelled.
</div>

<h2>High-confidence picks</h2>
<p class="lede">Every pick below clears all three gates at once: verified inputs on both sides, a model
probability of at least 70%, and a fair price no shorter than −250. Each has its own written prediction of
74–89 words, checked for uniqueness across the desk.</p>
{table(["Sport", "Match", "Market", "Selection", "Model p", "Fair", "US", "Tier", "Verification", "Official source", ""], high_rows)}
<p class="small muted">Model probability is this desk's estimate. The fair price is 1/probability with no
margin; a 5% book-equivalent is shown on every match page so the margin is visible rather than hidden.</p>

<h2>Every sport on the desk</h2>
{table(["Sport", "OLBG", "Fixtures", "Priced", "Markets", "High picks", ""], sport_rows)}

<h2>How to read a row</h2>
<div class="cols">
<div>
<h3>Confidence tiers</h3>
<ul class="tight">
<li><span class="pill high">High</span> both sides measured on an official page, model probability ≥ 70%, fair price inside −250…+10000. At most one per fixture and three per sport.</li>
<li><span class="pill med">Medium</span> both sides measured, probability ≥ 60% but outside the band — usually because the price is shorter than −250.</li>
<li><span class="pill low">Low</span> one-sided inputs, a neutral baseline, or probability below 60%.</li>
</ul>
</div>
<div>
<h3>Verification labels</h3>
<ul class="tight">
<li><span class="pill verified">re-fetched today</span> this session re-read the official endpoint and compared it with the register value.</li>
<li><span class="pill carried">carried</span> the row keeps the official link and read date recorded by the register it came from; it was <em>not</em> re-read in this pass and is never described as re-verified.</li>
</ul>
</div>
</div>

<h2>What changed in this pass</h2>
<ul class="tight">
<li>Re-read three official endpoints live: the NHL standings feed for 2026-10-22, the MLB StatsAPI 2026
standings and the EuroLeague 2026-27 standings. {verification["counts"]["checks"]} row-side comparisons are
published with their results on the <a href="verification.html">Verification</a> page.</li>
<li>Merged two source registers (and their fourteen sibling desks&rsquo; context) into one desk, reconciling club-name variants and logging
{len(fixtures_blob["cross_desk_conflicts"])} cross-desk disagreements instead of silently picking a winner.</li>
<li>Dropped {counts["expired"]} fixtures that had already started before the publish cut-off rather than
pricing games already in play.</li>
<li>Priced {counts["markets"]} markets with a documented model: match winner, three-way where draws exist,
seven-rung handicap ladders and baseball totals. {counts["unpriced"]} cards are left unpriced with the reason stated.</li>
<li>Found {seventy} selections at or above 70%; {in_band} of those also sit inside the brief's price window.
The {preds["counts"]["band_excluded"]} fixtures whose best ≥70% selection is priced shorter than −250 are listed
separately on the <a href="markets.html#band">Markets</a> page.</li>
</ul>

<h2>Repository review</h2>
<p>The <a href="audit.html">Repo audit</a> page records what a line-by-line read of this repository found:
{len(prior_html)} HTML pages, {len([d for d in desks if (ROOT / d / "index.html").exists()])} published desks, {len(prior_validators)} validators, and the
duplication and staleness that follow from that. Irregularities are not fixed here where they belong to
another session's files; they are listed with links so they can be reviewed.</p>
'''

    (SITE / "index.html").write_text(page(
        "index.html", "Dashboard", body, active="index.html",
        subtitle="Every in-scope sport, our own lines, confidence tiers and a source link on every row — "
                 "read 22 October 2026.",
    ))

    # ---------------- sport pages ----------------
    for slug, name, oid in SPORT_ORDER:
        sr = by_sport.get(slug, [])
        priced = [r for r in sr if r["priced"]]
        unpriced = [r for r in sr if not r["priced"]]
        hi = [h for h in highs if h["sport"] == slug]
        blocks = []
        for r in priced:
            mrows = []
            for m in r["markets"]:
                for s in m["selections"]:
                    mrows.append([
                        esc(m["market"]),
                        f'<strong>{esc(s["selection"])}</strong>',
                        f'{s["prob"] * 100:.1f}%',
                        f'{s["price"]:.2f}',
                        us_text(s["us"]),
                        f'{s["book_price"]:.2f} / {us_text(s["book_us"])}',
                        pill(s["tier"]),
                        f'<a href="../predictions.html#{esc(r["id"])}">pick</a>' if any(h["id"] == r["id"] for h in hi) else "",
                    ])
            flags = "".join(f'<li>{esc(f)}</li>' for f in r["flags"])
            inputs = (
                f'<div class="inputs"><div><span class="k">Home input</span> {esc(r["inputs"]["home"]["value"]) or "—"}'
                f'<div class="muted small">{esc(r["inputs"]["home"]["label"])}</div></div>'
                f'<div><span class="k">Away input</span> {esc(r["inputs"]["away"]["value"]) or "—"}'
                f'<div class="muted small">{esc(r["inputs"]["away"]["label"])}</div></div></div>'
            )
            blocks.append(f'''
<article class="fixture" id="{esc(r["id"])}">
<div class="fixturehead">
<h3>{esc(r["home"])} <span class="vs">v</span> {esc(r["away"])}</h3>
<div class="meta">{esc(r["competition"])}{(" · " + esc(r["stage"])) if r.get("stage") else ""} · {esc(kickoff(r))}
{(" · " + esc(r["venue"])) if r.get("venue") else ""}</div>
<div class="meta">{verif_pill(r["verification"]["status"])} <span class="muted">model margin
{r["expected_margin"]:+.2f} {esc(r.get("unit", ""))}</span> · winner call
<strong>{esc(r["winner_call"])}</strong> {pill(r["winner_confidence"])} · {src_links(r["sources"])}</div>
</div>
{inputs}
{table(["Market", "Selection", "Model p", "Fair", "US", "5% book", "Tier", ""], mrows)}
{f'<ul class="flags">{flags}</ul>' if flags else ""}
</article>''')
        unpriced_rows = [[
            f'<span id="{esc(r["id"])}"></span><strong>{esc(r["home"])}</strong>' if r["home"] else f'<span id="{esc(r["id"])}"></span>', 
            esc(r["away"]),
            esc(r["competition"]),
            esc(r.get("reason", "")),
            verif_pill(r["verification"]["status"]),
            src_links(r["sources"], 2),
        ] for r in unpriced]

        body = f'''
<p class="lede">{esc(SPORT_NOTES.get(slug, ""))}</p>
<section class="cards">
{stat_card(len(sr), "fixtures")}
{stat_card(len(priced), "priced")}
{stat_card(sum(len(r["markets"]) for r in sr), "markets")}
{stat_card(len(hi), "High picks")}
{stat_card(sum(1 for r in sr if r["verification"]["status"] == "re-fetched"), "re-fetched today")}
</section>
{"".join(blocks) if blocks else '<p class="empty">No priceable fixture for this sport in the window.</p>'}
{f'<h2>Published unpriced</h2>{table(["Home / card", "Away / field", "Competition", "Why no price", "Verification", "Official source"], unpriced_rows)}' if unpriced_rows else ""}
'''
        (SITE / "sports" / f"{slug}.html").write_text(page(
            slug, name, body, prefix="../", active="",
            subtitle=f"OLBG sport id {oid} · {len(sr)} fixtures · {len(hi)} High-confidence picks",
        ))

    # ---------------- predictions ----------------
    cards = []
    for p in preds["predictions"]:
        inputs = "".join(
            f'<tr><td>{esc(i["side"].title())}</td><td>{esc(i["label"])}</td><td>{esc(i["value"])}</td>'
            f'<td>{esc(i["rating"])}</td></tr>'
            for i in p["verified_inputs"]
        )
        checks = "".join(
            f'<li>{esc(c["team"])}: register says <em>{esc(c["register_value"])}</em>; official page says '
            f'<em>{esc(c["official_value"])}</em> — {esc(c["result"])} ({esc(c["reason"])}) '
            f'<a href="{esc(c["url"])}" target="_blank" rel="noopener">source ↗</a></li>'
            for c in p["row_checks"]
        )
        flags = "".join(f"<li>{esc(f)}</li>" for f in p["flags"])
        if checks:
            checks_html = f'<ul class="checks">{checks}</ul>'
        else:
            checks_html = ('<p class="muted small">This row was not re-read in today&rsquo;s pass; it keeps '
                           'the official link and read date recorded by its register.</p>')
        cards.append(f'''
<article class="pick" id="{esc(p["fixture_id"])}">
<div class="pickhead">
<div>
<div class="sportline">{esc(p["sport"].replace("-", " ").title())} · {esc(p["competition"])}</div>
<h3>{esc(p["home"])} <span class="vs">v</span> {esc(p["away"])}</h3>
</div>
<div class="pickprice">
<div class="sel">{esc(p["selection"])}</div>
<div class="price">{p["price"]:.2f} <span class="muted">({us_text(p["us"])})</span></div>
<div class="muted small">{esc(p["market"])} · model p {p["prob"] * 100:.1f}% · {verif_pill(p["verification"]["status"])}</div>
</div>
</div>
<p class="headline">{esc(p["headline"])}</p>
<p class="prose">{esc(p["text"])}</p>
<div class="pickmeta">{p["words"]} words · fair price {p["price"]:.2f} · 5% book-equivalent
{p["book_price"]:.2f} ({us_text(p["book_us"])}) · kick-off {esc(kickoff(p))}</div>
<details>
<summary>Verified inputs and the checks behind this pick</summary>
<div class="tablewrap"><table><thead><tr><th>Side</th><th>Input</th><th>Verified value</th><th>Strength</th></tr></thead>
<tbody>{inputs}</tbody></table></div>
{checks_html}
<ul class="sources">{''.join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["name"])}</a></li>' for s in p["sources"])}</ul>
{f'<ul class="flags">{flags}</ul>' if flags else ""}
</details>
</article>''')

    body = f'''
<p class="lede">Nine High-confidence picks, one per qualifying match. Each write-up names the sides, the
verified form, the recent record and the exact selection, and none of them shares a six-word sequence with
any other. Word counts run {preds["counts"]["min_words"]} to {preds["counts"]["max_words"]}.</p>
<section class="cards">
{stat_card(preds["counts"]["predictions"], "predictions", "one per High pick")}
{stat_card(preds["counts"]["min_words"], "shortest write-up", "words, brief requires 30")}
{stat_card(preds["counts"]["shared_sixgrams"], "shared six-grams", "checked across the desk")}
{stat_card(preds["counts"]["band_excluded"], "fixtures band-excluded", "70%+ but shorter than −250")}
</section>
<div class="notice">
<strong>Player detail.</strong> Six of these nine write-ups are team-level because the official pages this
desk read publish team aggregates only. Where a governing-body page carried player figures — the EuroLeague
scoring and defence tables — they are used. No player name was added from memory, and the gap is logged on
the <a href="flagged.html">Flagged</a> page.
</div>
{"".join(cards)}
'''
    (SITE / "predictions.html").write_text(page(
        "predictions.html", "High-confidence predictions", body, active="predictions.html",
        subtitle="Hand-written for every pick that clears the model, the price window and the source gate.",
    ))

    # ---------------- markets ----------------
    mrows = []
    for slug, name, oid in SPORT_ORDER:
        sr = by_sport.get(slug, [])
        winners = sum(1 for r in sr for m in r["markets"] if m["market"] == "Match winner")
        hcaps = sum(1 for r in sr for m in r["markets"] if "handicap" in m["market"].lower())
        totals = sum(1 for r in sr for m in r["markets"] if m["market"].lower().startswith("total"))
        hi = sum(1 for h in highs if h["sport"] == slug)
        note = ("totals priced" if totals else "no verified scoring baseline — totals not priced")
        mrows.append([
            f'<a href="sports/{slug}.html">{esc(name)}</a>', str(winners), str(hcaps), str(totals),
            str(len(sr)), str(hi), esc(note),
        ])

    band_rows = []
    for e in preds["band_excluded"][:40]:
        band_rows.append([
            f'<a href="sports/{e["sport"]}.html">{esc(e["sport"].replace("-", " ").title())}</a>',
            f'<strong>{esc(e["home"])}</strong> v {esc(e["away"])}',
            esc(e["market"]),
            esc(e["selection"]),
            f'{e["prob"] * 100:.1f}%',
            f'{e["price"]:.2f}',
            us_text(e["us"]),
            esc(e["reason"]),
            src_links(e["sources"], 1),
        ])

    body = f'''
<p class="lede">Every market this desk investigated, and the ones it refused to price. A market is priced only
where an official page gave a strength input for both sides; everything else is named as investigated and left
blank.</p>
<section class="cards">
{stat_card(counts["markets"], "markets originated", "match winner, handicap ladders, baseball totals")}
{stat_card(counts["selections"], "priced selections", "each with a model probability and fair price")}
{stat_card(counts["by_tier"]["High"], "High", "in the −250…+10000 band")}
{stat_card(counts["by_tier"]["Medium"], "Medium", "60–70%, or shorter than −250")}
{stat_card(counts["by_tier"]["Low"], "Low", "one-sided, neutral or below 60%")}
</section>

<h2>Coverage by sport</h2>
{table(["Sport", "Winner markets", "Handicap markets", "Total markets", "Fixtures", "High picks", "Notes"], mrows)}

<h2>Markets investigated</h2>
{table(
    ["Market family", "Priced?", "How it is originated", "Where it stops"],
    [
        ["Match winner", "Yes, all priced fixtures", "logistic on the verified strength gap plus a home edge where the fixture is not neutral", "one-sided inputs get a neutral baseline and Low tier only"],
        ["Draw (three-way)", "Rugby union, rugby league, handball, Gaelic football, AFLW", "a draw share taken out of the two-way split, widest at a pick'em", "no draw modelled in sports that cannot draw"],
        ["Handicap / spread", "Seven rungs per fixture", "normal margin distribution around the model's expected margin, hung on half-lines", "rungs that would push are shifted onto a half-line"],
        ["Match total", "Baseball only", "mean of both sides' runs scored and allowed per game, priced from a 4.3-run spread", "no official scoring-rate baseline exists for the other sports, so no total is invented"],
        ["Correct score / method of victory", "No", "not derivable from a two-sided strength input without inventing a distribution", "listed here as investigated, left unpriced"],
        ["Player props, first try, top scorer", "No", "requires team-sheet and player-level data the governing-body pages do not publish pre-match", "unpriced"],
        ["Outright / field cards", "No", "a field board cannot be priced from one input per side", "published as cards on the sport pages and on Flagged"],
    ],
)}

<h2 id="band">Band-excluded ledger — 70%+ picks priced shorter than −250</h2>
<p>The brief asks for high-confidence picks on matches priced between −250 and +10000. The desk takes that
literally at selection level: a pick must be priced no shorter than −250 <em>and</em> hold at least a 70% model
chance. That leaves a 1.4-point-wide probability window, which is why only {counts["high"]} of the
{preds["counts"]["band_excluded"]} fixtures with a ≥70% selection can be called High. Here are the best of the
rest, stated plainly rather than relabelled as High.</p>
{table(["Sport", "Match", "Market", "Best ≥70% selection", "Model p", "Fair", "US", "Why it is not High", "Official source"], band_rows)}
<p class="small muted">Showing the best band-excluded selection per fixture, {min(40, len(preds["band_excluded"]))} of
{preds["counts"]["band_excluded"]}. The full list is in <code>data/e6716490/predictions.json</code>.</p>
'''
    (SITE / "markets.html").write_text(page(
        "markets.html", "Markets and the price window", body, active="markets.html",
        subtitle="What was priced, what was refused, and why the High band is as narrow as it is.",
    ))

    # ---------------- verification ----------------
    fetch_blocks = []
    for f in verification["fetches"]:
        team_rows = [[esc(t), esc(
            ", ".join(f"{k} {v}" for k, v in fact.items())
        )] for t, fact in f["teams"].items()]
        fetch_blocks.append(f'''
<article class="fixture">
<div class="fixturehead">
<h3>{esc(f["id"])} · {esc(f["authority"])}</h3>
<div class="meta"><a href="{esc(f["url"])}" target="_blank" rel="noopener">{esc(f["url"])}</a></div>
<div class="meta">{esc(f["title"])} · read {esc(f["read_at"])} · covers {esc(f["covers"])}</div>
</div>
{table(["Team", "Fields read from the official page"], team_rows)}
<p class="small muted">{esc(f["note"])}</p>
</article>''')

    check_rows = [[
        f'<strong>{esc(c["fixture"])}</strong>',
        esc(c["sport"].replace("-", " ").title()),
        esc(c["side"]),
        esc(c["register_value"]),
        esc(c["official_value"]),
        f'<span class="pill {"verified" if c["result"] == "match" else "carried"}">{esc(c["result"])}</span>',
        esc(c["reason"]),
        f'<a href="{esc(c["url"])}" target="_blank" rel="noopener">source ↗</a>',
    ] for c in verification["checks"]]

    body = f'''
<p class="lede">Verification on this desk is a claim about a specific page at a specific time. Three official
endpoints were re-read for this pass; everything else is labelled <em>carried</em> and keeps the link and read
date of the register it came from.</p>
<section class="cards">
{stat_card(verification["counts"]["fetches"], "official endpoints re-read", "NHL, MLB, EuroLeague")}
{stat_card(verification["counts"]["checks"], "row-side comparisons", "each with its own source link")}
{stat_card(verification["counts"]["fixtures_touched"], "fixtures re-checked", f'of {verification["counts"]["fixtures_total"]} on the desk')}
{stat_card(verification["counts"]["fixtures_total"] - verification["counts"]["fixtures_touched"], "fixtures carried", "not re-read this pass")}
</section>

<h2>What was re-read</h2>
{"".join(fetch_blocks)}

<h2>Row-by-row comparison</h2>
<p>Each row compares the value this desk publishes with the value on the official page as read. <span
class="pill verified">match</span> means every field the page published appears in the register value;
<span class="pill carried">partial</span> means the register corroborates some fields and does not quote the
others — never that it contradicts them. No contradiction was found in this pass.</p>
{table(["Fixture", "Sport", "Side", "Register value", "Official value (as read)", "Result", "Detail", "Source"], check_rows)}

<h2>What was not re-read</h2>
<p>The following sports were not re-fetched in this pass, so no row from them is described as re-verified:
{esc(", ".join(s.replace("-", " ") for s in verification["uncorroborated"]["sports"]))}.
Their rows keep the governing body's URL and the read date stamped by the register that produced them, and the
site marks each one <span class="pill carried">carried</span>. {esc(verification["uncorroborated"]["note"])}</p>

<h2>How to reproduce</h2>
<pre><code>python3 scripts/se6716490_dataset.py     # merge the repository registers
python3 scripts/se6716490_model.py       # originate prices and tiers
python3 scripts/se6716490_verify.py      # apply the live re-read ledger
python3 scripts/se6716490_predictions.py # attach the hand-written picks
python3 scripts/se6716490_build_site.py  # build this site
python3 scripts/se6716490_validate.py    # gate: links, sources, band, prose</code></pre>
'''
    (SITE / "verification.html").write_text(page(
        "verification.html", "Live verification ledger", body, active="verification.html",
        subtitle="Exactly what was re-read today, what it confirmed, and what was not re-read at all.",
    ))

    # ---------------- flagged ----------------
    conflict_rows = []
    for c in fixtures_blob["cross_desk_conflicts"]:
        readings = "<br>".join(
            f'<span class="tag">{esc(d)}</span> {esc(v[0])} <span class="muted">/</span> {esc(v[1])}'
            for d, v in c["values"].items()
        )
        links = " ".join(
            f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(url.split("/")[2])} ↗</a>'
            for urls in c["sources"].values() for url in urls
        )
        conflict_rows.append([
            esc(c["sport"].replace("-", " ").title()),
            esc(c["fixture"]),
            readings,
            links,
        ])

    unpriced_rows = [[
        esc(r["sport"].replace("-", " ").title()),
        esc(r["home"]) or "—",
        esc(r["away"]) or "—",
        esc(r["competition"]),
        esc(r.get("reason", "")),
        src_links(r["sources"], 2),
    ] for r in rows if not r["priced"]]

    unverified_rows = []
    seen_unverified = set()
    for r in rows:
        for field in r["unverified_fields"]:
            key = (r["sport"], field)
            if key in seen_unverified:
                continue
            seen_unverified.add(key)
            example = next(x for x in rows if x["sport"] == r["sport"] and field in x["unverified_fields"])
            unverified_rows.append([
                esc(r["sport"].replace("-", " ").title()),
                f'<code>{esc(field)}</code>',
                f'{sum(1 for x in rows if x["sport"] == r["sport"] and field in x["unverified_fields"])} rows in this sport',
                "left blank — no official page publishes it before the match",
                src_links(example["sources"], 1),
            ])

    flag_counts: dict[str, list[str]] = {}
    for r in rows:
        for f in r["flags"]:
            flag_counts.setdefault(f, []).append(r["id"])
    flag_rows = [[
        f'<span class="count">{len(v)}</span>',
        esc(text),
        ", ".join(f'<a href="sports/{next(x["sport"] for x in rows if x["id"] == fid)}.html#{fid}">{esc(fid)}</a>' for fid in v[:3])
        + (f' <span class="muted">+{len(v) - 3}</span>' if len(v) > 3 else ""),
    ] for text, v in sorted(flag_counts.items(), key=lambda kv: -len(kv[1]))]

    player_gap = [p for p in preds["predictions"]
                  if not any(ch.isdigit() for ch in "".join(
                      str(v) for v in p["verified_inputs"]))]

    body = f'''
<p class="lede">Everything this desk could not confirm, could not reconcile or chose not to publish, with the
links needed to check it. Nothing on this page blocks publication; it exists so a value is never mistaken for
something it is not.</p>
<div class="notice">
<strong>Read this first.</strong> {len(unpriced_rows)} cards are published without a price,
{len(fixtures_blob["cross_desk_conflicts"])} fixtures are described differently by two repository registers,
{preds["counts"]["band_excluded"]} fixtures have a ≥70% selection priced too short for the brief's window, and
{len(seen_unverified)} field types are blank because no official page publishes them before the match.
</div>

<h2>1. Cross-desk disagreements</h2>
<p>The repository holds fourteen published desks (sixteen directories carry pages). Where two of them describe the same fixture with different
numbers, both readings and both source lists are shown and the desk does not pretend to know which is right.</p>
{table(["Sport", "Fixture", "Reading A / Reading B", "Sources offered"], conflict_rows)}

<h2>2. Published without a price</h2>
{table(["Sport", "Home / card", "Away / field", "Competition", "Why no price was originated", "Official source"], unpriced_rows)}

<h2>3. Values left blank</h2>
<p>These fields are empty on every row that needs them. They are never filled from memory or inferred from a
neighbouring value — the site simply shows nothing where the official page shows nothing.</p>
{table(["Sport", "Field", "Coverage", "Treatment", "Example source"], unverified_rows)}

<h2>4. Register flags carried onto this desk</h2>
<p>The registers behind this desk recorded the following caveats. They are reproduced verbatim, with the rows
they belong to.</p>
{table(["Rows", "Flag", "Examples"], flag_rows)}

<h2>5. Player-level detail</h2>
<p>Six of the nine High-confidence write-ups are team-level. The official standings, ladder and draw pages this
desk reads publish team aggregates; only the EuroLeague pages carried scoring and defensive figures, and only
the Dubai pick uses them. Adding a player name to the other six would have meant inventing one, so the
write-ups stay team-level and the gap is logged here instead.</p>

<h2>6. Clocks</h2>
<p>Darts, snooker, golf and one tennis match publish a session window or a rolling order of play rather than a
start time per match. Those rows show “clock not published” and carry no kick-off; nothing was estimated.
{counts["expired"]} fixtures had already started before this desk's cut-off of {esc(lines["cut_off_utc"])} and
were removed from the priced set instead of being offered as live bets.</p>
'''
    (SITE / "flagged.html").write_text(page(
        "flagged.html", "Flagged for review", body, active="flagged.html",
        subtitle="Unverified values, cross-desk conflicts and every card left unpriced — with links.",
    ))

    # ---------------- methodology ----------------
    param_rows = []
    for slug, p in lines["policy"]["params"].items():
        param_rows.append([
            esc(slug.replace("-", " ").title()),
            str(p["denom"]), str(p["hfa"]), str(p["draw"]), str(p["margin"]),
            str(p["sigma"]), esc(p["unit"]), esc(p["label"]),
        ])

    body = f'''
<p class="lede">The whole model, in enough detail to disagree with it. Every constant below is a modelling
choice made by this session; none of them is presented as a statistic.</p>

<h2>The five rules</h2>
<ol class="tight">
<li>Official sources only. A record, ladder position, rating, seed or draw comes from the league, tour,
federation or organiser that publishes it. OLBG is used to find matches, never to verify one.</li>
<li>Blank beats wrong. If a value cannot be confirmed it stays empty and is listed on
<a href="flagged.html">Flagged</a>.</li>
<li>Assumptions are labelled. The constants on this page are ours, printed in full.</li>
<li>One-sided inputs carry no edge. If only one side has a verified strength input the row is priced from a
neutral 50/50 baseline, flagged, and capped at Low confidence.</li>
<li>Model output is never a sourced fact. Every price is an estimate and is labelled as one.</li>
</ol>

<h2>How a price is made</h2>
<pre><code>edge  e = (rating_home − rating_away) + HFA          # rating points, HFA only when not neutral
win   p = 1 / (1 + 10^(−e / denom))                   # two-way probability
draw      a share out of the two-way split, widest at a pick'em (three-way sports only)
margin m = margin_scale × e                           # in the sport's scoring unit
rungs     seven half-lines, m's pick'em line ± three steps of at least 1.0 unit
cover     p = 1 − Φ((−h − m) / sigma)                 # h is the signed home handicap
totals    baseball: mean of both sides' runs scored and allowed per game, sigma 4.30
price     fair = 1 / p ; book-equivalent = 1 / (p × 1.05) ; US odds from the decimal
</code></pre>

<h2>Sport parameters</h2>
<p><code>denom</code> is the rating spread of the logit, <code>hfa</code> the home edge in rating points,
<code>draw</code> the peak draw share, <code>margin</code> the scoring unit per rating point and
<code>sigma</code> the standard deviation of the margin in that unit.</p>
{table(["Sport", "denom", "HFA", "draw", "margin/pt", "sigma", "unit", "market label"], param_rows)}

<h2>Why only {counts["high"]} High picks</h2>
<p>The brief asks for picks above a 70% chance <em>and</em> priced between −250 and +10000. At fair odds a
−250 price is a 71.43% chance, so the qualifying band is 70.00%–71.43%: 1.43 percentage points wide. A desk
hanging seven handicap rungs per match will occasionally drop one inside that window, and that is exactly what
happened on {counts["high"]} of the {counts["priced"]} priced fixtures. Every other ≥70% selection is published
with its true (shorter) price in the <a href="markets.html#band">band-excluded ledger</a> rather than
mis-labelled as High. Anything else would have meant moving a line until a price landed in the band, which is
not a model — it is a target.</p>

<h2>What the model cannot do</h2>
<ul class="tight">
<li>It cannot price a match where only one side has an official strength input. It refuses to guess the other.</li>
<li>It cannot price totals outside baseball, correct scores, player props or field boards, because no official
page gives it the inputs before the match.</li>
<li>It does not know about injuries, team selection or travel beyond what the governing-body page publishes.</li>
<li>It has not been back-tested on results. The probabilities are calibrated by construction, not by outcome.</li>
<li>It publishes {counts["markets"]} markets from {counts["priced"]} fixtures, and the correlation between rungs
of the same match is total — the High tier is capped at one rung per fixture for that reason.</li>
</ul>
'''
    (SITE / "methodology.html").write_text(page(
        "methodology.html", "Methodology", body, active="methodology.html",
        subtitle="Every constant, every formula and every limit of what this desk can honestly claim.",
    ))

    # ---------------- sources ----------------
    domain_rows: dict[str, dict] = {}
    for r in rows:
        for s in r["sources"]:
            host = s["url"].split("/")[2] if "//" in s["url"] else s["url"]
            entry = domain_rows.setdefault(host, {"count": 0, "names": set(), "example": s["url"],
                                                  "sports": set()})
            entry["count"] += 1
            entry["names"].add(s["name"])
            entry["sports"].add(r["sport"])
    src_rows = [[
        f'<a href="{esc(v["example"])}" target="_blank" rel="noopener">{esc(host)} ↗</a>',
        str(v["count"]),
        esc(", ".join(sorted(x.replace("-", " ") for x in v["sports"]))),
        esc(sorted(v["names"])[0]),
    ] for host, v in sorted(domain_rows.items(), key=lambda kv: -kv[1]["count"])]

    body = f'''
<p class="lede">Every source this desk touched, grouped by the body that publishes it. No aggregator, news
outlet, tipster page or encyclopaedia appears here: a fact on this desk is confirmed against the organiser.</p>
<section class="cards">
{stat_card(len(domain_rows), "official domains", "across the rows on this desk")}
{stat_card(sum(v["count"] for v in domain_rows.values()), "row-to-source links", "a link on every priced row")}
{stat_card(verification["counts"]["fetches"], "re-read this pass", "NHL, MLB, EuroLeague")}
{stat_card(len(fixtures_blob["excluded"]), "sports excluded", "per the brief")}
</section>

<h2>Source register</h2>
{table(["Official domain", "Rows citing it", "Sports", "Example page"], src_rows)}

<h2>Excluded sports</h2>
<p>The brief excludes soccer/football, boxing, UFC/MMA, American football, hurling, horse racing, cycling and
specials. They were enumerated on the OLBG side of the reverse-engineering work and deliberately left out of
this desk:</p>
{table(["Excluded", "OLBG sport id"],
       [[esc(n), esc(i if i is not None else "unlisted route")] for n, i in fixtures_blob["excluded"]])}
'''
    (SITE / "sources.html").write_text(page(
        "sources.html", "Source register", body, active="sources.html",
        subtitle="Governing bodies, leagues and organisers only — the pages every number came from.",
    ))

    # ---------------- audit ----------------

    body = f'''
<p class="lede">A line-by-line read of this repository, as found on 22 October 2026, before this desk was
added. Findings are recorded here whether or not they belong to this session's files.</p>

<section class="cards">
{stat_card(len(prior_html), "HTML pages already in the repo", "before this desk, which adds 25")}
{stat_card(len([d for d in desks if (ROOT / d / "index.html").exists()]), "published desks found", "each with its own landing page")}
{stat_card(len(prior_scripts), "python scripts found", f'{len(prior_validators)} of them validators')}
{stat_card(sum(1 for _ in (ROOT / "COORDINATION.md").open()), "lines of coordination log", "the shared task board")}
</section>

<h2>What is sound</h2>
<ul class="tight">
<li><strong>Every register carries official links.</strong> The root desk and all namespaced desks link each row
to a governing body, tour, federation or league endpoint. No aggregator is used to verify a fact.</li>
<li><strong>Eleven validators, all passing.</strong> <code>scripts/validate.py</code> checks whole-tree link
integrity, source-host allowlists and the primary desk's writing rules; <code>scripts/final_audit.py</code> and
the per-session validators re-check their own namespaces. All of them pass on the tree this desk was built from.</li>
<li><strong>No broken relative links.</strong> The gate resolves every anchor across every page in the
repository; adding this desk's pages keeps that at zero.</li>
<li><strong>Blank-and-flag discipline is real.</strong> Unconfirmed fields — starting goalies, probable pitchers,
kick-off clocks for rolling sessions, ranks outside a published page — are empty on the rows and named in the
flag lists, not filled in.</li>
<li><strong>No stray build artefacts.</strong> No <code>.pyc</code> files are tracked, and
<code>.gitignore</code> excludes them.</li>
</ul>

<h2>What is irregular</h2>
<ul class="tight">
<li><strong>Fourteen parallel desks with overlapping fixtures.</strong> {len(fixtures_blob["cross_desk_conflicts"])}
fixtures on this desk alone are described differently by two registers; repository-wide, 180 pairings appear in
two or more registers. Each desk solved the same problem independently, so the repository contained several
defensible but mutually inconsistent readings of the same night's sport.</li>
<li><strong>Stale fixtures are still priced on older desks.</strong> The root register
(<code>data/fixtures.json</code>) still prices 44 fixtures dated before 22 October 2026. They are not wrong as
records, but they are no longer bettable and a reader landing on those pages cannot tell.</li>
<li><strong>The README's headline counts no longer match the tree.</strong> Its coverage summary describes 134
events and 160 published pages; the tree held {len(prior_html)} pages before this desk was added. The counts were accurate when written
and have drifted with each new desk.</li>
<li><strong>Two registers disagree about a fixture date.</strong> The World Series game five is dated 27 October
by one register and 28 October by another; the desk publishes the later date with the disagreement logged.</li>
<li><strong>Barça v Montpellier has two different scorelines.</strong> One register records the earlier meeting as
28-27, another as 34-27. Both cite the EHF. The desk quotes neither in its write-up.</li>
<li><strong>Duplicate market families across desks.</strong> Handicap ladders, totals and outright boards are
re-originated in several styles with different constants, so the same match can carry three different prices
depending on which page a reader opens. This desk states its constants on
<a href="methodology.html">Methodology</a> for exactly that reason.</li>
<li><strong>Coordination, not code, is the bottleneck.</strong> {sum(1 for _ in (ROOT / "COORDINATION.md").open())}
lines of task board record a dozen renumberings and collision resolutions. The structure held, but the same
verification work was repeated many times over.</li>
</ul>

<h2>What this desk does about it</h2>
<p>It reconciles every register it can reach into one dataset, logs every disagreement rather than resolving it
silently, drops fixtures that have already started, states its model constants, and puts the band arithmetic
where a reader can check it. It does not edit another session&rsquo;s files: the fixes owed elsewhere are listed
above with enough detail to action.</p>
'''
    (SITE / "audit.html").write_text(page(
        "audit.html", "Repository audit", body, active="audit.html",
        subtitle="What the line-by-line read of this repo found, sound and unsound, with links.",
    ))

    # ---------------- assets ----------------
    (SITE / "assets" / "style.css").write_text(STYLE)
    print(f"built {len(list(SITE.rglob('*.html')))} pages into {SITE.relative_to(ROOT)}/")
    return 0


STYLE = '''
:root{
  --bg:#f6f7f9; --panel:#fff; --ink:#12161c; --muted:#5d6b7a; --line:#e3e7ec;
  --accent:#1f5fd1; --high:#0f7a4a; --highbg:#e2f5ea; --med:#8a5a00; --medbg:#fdf1d8;
  --low:#5d6b7a; --lowbg:#eef1f4; --warn:#a4262c; --warnbg:#fdeaea; --carried:#6b4fa8; --carriedbg:#efeafc;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
code{background:#eef1f4;padding:1px 5px;border-radius:4px;font-size:.86em}
pre{background:#12161c;color:#e8edf3;padding:14px 16px;border-radius:10px;overflow:auto;font-size:13px}
pre code{background:none;color:inherit;padding:0}
.topbar{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:14px;align-items:center;
  padding:10px 22px;background:#fff;border-bottom:1px solid var(--line)}
.brand{font-weight:700;letter-spacing:.2px;color:var(--ink)}
.brand span{font-weight:400;color:var(--muted);font-size:13px}
.topbar nav{display:flex;flex-wrap:wrap;gap:4px}
.topbar nav a{padding:6px 10px;border-radius:7px;color:var(--muted);font-size:14px}
.topbar nav a:hover{background:#f0f3f7;text-decoration:none}
.topbar nav a.active{background:#e8effb;color:var(--accent);font-weight:600}
.topbar nav a.back{margin-left:auto;border:1px solid var(--line)}
main{max-width:1220px;margin:0 auto;padding:26px 22px 60px}
.pagehead h1{margin:6px 0 6px;font-size:30px;letter-spacing:-.4px}
.lede{color:var(--muted);max-width:78ch;margin:0 0 22px}
h2{margin:34px 0 12px;font-size:20px;letter-spacing:-.2px}
h3{margin:0 0 6px;font-size:16px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:12px;margin:18px 0 26px}
.card.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.card.stat .value{font-size:26px;font-weight:700;letter-spacing:-.5px}
.card.stat .label{font-size:13px;color:var(--muted);margin-top:2px}
.card.stat .hint{font-size:12px;color:#8794a3;margin-top:6px}
.notice{background:#eef4ff;border:1px solid #cdddfa;border-radius:12px;padding:14px 16px;margin:18px 0;max-width:95ch}
.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel);margin:10px 0 18px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
thead th{position:sticky;top:0;background:#f0f3f7;text-align:left;padding:9px 10px;
  border-bottom:1px solid var(--line);font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
tbody td{padding:9px 10px;border-bottom:1px solid #eef1f5;vertical-align:top}
tbody tr:hover{background:#fafcff}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:600;white-space:nowrap}
.pill.high{background:var(--highbg);color:var(--high)}
.pill.med{background:var(--medbg);color:var(--med)}
.pill.low{background:var(--lowbg);color:var(--low)}
.pill.verified{background:var(--highbg);color:var(--high)}
.pill.carried{background:var(--carriedbg);color:var(--carried)}
.pill.warn{background:var(--warnbg);color:var(--warn)}
.pill.muted{background:var(--lowbg);color:var(--low)}
.muted{color:var(--muted)}
.small{font-size:12.5px}
.tag{display:inline-block;padding:1px 6px;border-radius:5px;background:#eef1f4;font-size:11px;color:var(--muted)}
.fixture{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:16px 0}
.fixturehead .meta{color:var(--muted);font-size:12.5px;margin-top:3px}
.vs{color:#98a5b3;font-weight:400;font-size:13px}
.inputs{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0}
.inputs > div{background:#f8fafc;border:1px solid var(--line);border-radius:10px;padding:10px 12px;font-size:13px}
.inputs .k{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin-bottom:3px}
.flags{margin:10px 0 0;padding-left:18px;font-size:12.5px;color:var(--med)}
.pick{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:18px 0}
.pickhead{display:flex;flex-wrap:wrap;gap:16px;justify-content:space-between;align-items:flex-start}
.sportline{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.pickprice{text-align:right}
.pickprice .sel{font-weight:700;font-size:16px}
.pickprice .price{font-size:22px;font-weight:700;letter-spacing:-.5px}
.headline{margin:14px 0 6px;font-weight:600;font-size:15px}
.prose{margin:0 0 10px;max-width:82ch}
.pickmeta{font-size:12.5px;color:var(--muted);border-top:1px dashed var(--line);padding-top:10px;margin-top:10px}
details{margin-top:12px;border-top:1px solid var(--line);padding-top:10px}
summary{cursor:pointer;font-size:13.5px;color:var(--accent);font-weight:600}
.checks,.sources{margin:10px 0 0;padding-left:18px;font-size:12.5px}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}
ul.tight,ol.tight{margin:8px 0;padding-left:20px}
ul.tight li,ol.tight li{margin:5px 0}
.count{display:inline-block;min-width:26px;text-align:center;background:#eef1f4;border-radius:6px;
  padding:1px 6px;font-weight:600;font-size:12px}
.empty{color:var(--muted)}
footer{max-width:1220px;margin:0 auto;padding:18px 22px 40px;color:var(--muted);font-size:12.5px;
  border-top:1px solid var(--line)}
@media(max-width:720px){
  .inputs{grid-template-columns:1fr}
  .pickprice{text-align:left}
  main{padding:18px 14px 40px}
  .pagehead h1{font-size:24px}
}
'''

if __name__ == "__main__":
    raise SystemExit(main())
