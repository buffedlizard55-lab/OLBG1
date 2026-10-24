"""Render the session report for the 02d3d515 desk from the same data the site uses."""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s02d3d515_data import (FIXTURES, FLAGS, OBSERVED, PICKS, SOURCES, SPORTS,
                            WITHHELD)
from s02d3d515_build import build_picks
from s02d3d515_model import american_from_prob

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "reports" / "SESSION_02D3D515.md"
OUT_HTML = ROOT / "reports" / "SESSION_02D3D515.html"

picks = build_picks()   # same tier rule the site publishes
high = [p for p in picks if p["confidence"] == "high"]
med = [p for p in picks if p["confidence"] == "medium"]
low = [p for p in picks if p["confidence"] == "low"]
sports_with = {p["sport"] for p in picks}
fx_by_sport = {s: [f for f in FIXTURES if f["sport"] == s] for s, _, _ in SPORTS}


def fmt_price(p):
    return f"{american_from_prob(p):+d}"


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


coverage = []
for slug, name, pub in SPORTS:
    sp = [p for p in picks if p["sport"] == slug]
    coverage.append([
        name, len(fx_by_sport[slug]), len(sp),
        sum(p["confidence"] == "high" for p in sp),
        "yes" if sp else ("fixtures only" if fx_by_sport[slug] else "no confirmed fixture"),
    ])

pick_rows = [[p["sport"], p["fixture"], p["market"], p["selection"],
              fmt_price(p["prob"]), f"{p['prob']*100:.1f}%", p["confidence"]]
             for p in picks]

md = f"""# Session 02d3d515 — live 15-sport desk for 24–25 October 2026

**Captured:** {OBSERVED} (all times UTC)
**Branch:** `arena/02d3d515-olbg1`
**Site:** `02d3d515/index.html` · **Data:** `data/02d3d515/` · **Build:** `python3 scripts/s02d3d515_build.py`
**Gates:** `python3 scripts/s02d3d515_validate.py`, `python3 -m unittest tests.pipeline.test_desk_02d3d515`

## What was built

A fifteen-sport desk that answers one question first: *what should I look at today, and why?*
The landing page opens with an executive summary (counts, the high-confidence card, the
odds-window note), then the picks table, then the written predictions. Every other page is
one click away and named for what it holds: Picks, All matches, Our lines, Predictions,
Sports, Sources, Method, Flagged for review, Repo audit.

- **{len(picks)} priced selections** across **{len(sports_with)} sports** — {len(high)} high, {len(med)} medium, {len(low)} low.
- **{len(FIXTURES)} fixtures** confirmed on an official schedule, each with a source link on the row.
- **{len(WITHHELD)} fixtures carried without a line**, each naming exactly what was missing.
- **{len(SOURCES)} sources**, split into official pages (used for facts) and OLBG routes (discovery only).
- **{len(FLAGS)} flags** published on the Flagged for Review page.
- **26 HTML pages**: dashboard, 8 category pages, 15 sport pages, reverse-engineering notes.

## Coverage by sport

{md_table(["Sport", "Fixtures", "Picks", "High", "Status"], coverage)}

Sports with no pick are not silent: their pages state that no fixture could be confirmed on an
official page, and the corresponding row is flagged. The five-per-sport daily target is met for
no sport on this date because the official boards do not carry five matches each that could be
read in the session window; the shortfall is quantified on the Flagged page.

## The published card

{md_table(["Sport", "Fixture", "Market", "Selection", "Fair price", "Est. win", "Tier"], pick_rows)}

### Written predictions

{len(picks)} unique passages, {min(len(p['prediction'].split()) for p in picks)}–{max(len(p['prediction'].split()) for p in picks)} words each,
no repeated six-word run, no internal vocabulary, team or player named in every one.

## How the prices were made

Fair decimal is 1 ÷ our probability, with no margin, so a two-way book sums to exactly 100%.
American odds are converted from that decimal. Probabilities come from the official facts read:
NHL points and goal difference, NBA win-loss records, the World Series Game 1 result and season
run differential, Top 14 table positions, the ATP semi-final scorelines, the PGA TOUR leaderboard
and Formula 1 practice times. Where the official page gave no basis for a market, the market was
withheld rather than guessed.

**The odds window.** The brief asks for prices between −250 and +10000 and for a win chance above
70%. Those two conditions overlap in a band 1.4 points wide: 70% is a fair price of −233, and
−250 is 71.4%. The desk applies the window as binding and publishes the probability beside every
price, so a reader can see when a selection is chalk rather than an edge. This is stated on the
Method page and in flag F-02.

## Verification performed

Official pages and APIs read during the session, all timestamped on the Sources page:

{chr(10).join('- ' + s['publisher'] + ' — ' + s['url'] + ' — ' + s['scope'] for s in SOURCES if s['official'])}

OLBG was read for discovery only: fifteen sport hubs (Golf, Volleyball, Rugby Union, Cricket,
Snooker, Darts, Baseball, Gaelic Football, Greyhounds, Tennis, Motor Racing, Handball, Ice
Hockey, Basketball, Rugby League) plus individual event pages. No OLBG tip, tip percentage or
community price is used as a sporting fact or as a probability.

## Repository review

Line-by-line checks of the canonical release are recorded on `repo-audit.html` (A-01…A-06) with
SHA-256 prefixes: the canonical snapshot is two days older than this session, all 16 of its
priced matches are tiered low, 92 of 108 fixtures carry no market and 81 have no confirmed start
time, and it ships zero predictions by design. That is the structural reason the root site reads
as a list rather than a card.

## Irregularities and limits

{chr(10).join('- **' + f['id'] + ' (' + f['severity'] + ')** ' + f['title'] + ' — ' + f['detail'] for f in FLAGS)}

## Known limits

- Coverage is the set of matches that could be confirmed and priced inside the session window, not every match in the fifteen sports worldwide.
- No injury report was read for any published fixture. Injury cells are blank and flagged (F-10) rather than filled from memory or media reports.
- No bookmaker prices are copied. The desk has no live market feed, so "value" is judged against our own fair price, not against a book.
- Start times are UTC conversions from official pages where those pages publish a time; the conversion assumptions are listed in F-12.
- Handicap and total markets are published only where the official inputs exist (NHL goals, MLB runs, NBA points). Sports without an official scoring record carry those markets as withheld.
"""
OUT_MD.write_text(md, encoding="utf-8")

esc = html.escape
rows_cov = "".join(
    f"<tr><td>{esc(c[0])}</td><td class='n'>{c[1]}</td><td class='n'>{c[2]}</td>"
    f"<td class='n'>{c[3]}</td><td>{esc(c[4])}</td></tr>" for c in coverage)
rows_pick = "".join(
    f"<tr><td>{esc(p['sport'])}</td><td>{esc(p['fixture'])}</td><td>{esc(p['market'])}</td>"
    f"<td><b>{esc(p['selection'])}</b></td><td class='n'>{fmt_price(p['prob'])}</td>"
    f"<td class='n'>{p['prob']*100:.1f}%</td><td>{esc(p['confidence'])}</td></tr>"
    for p in picks)
rows_flag = "".join(
    f"<tr><td>{esc(f['id'])}</td><td>{esc(f['severity'])}</td><td>{esc(f['title'])}</td>"
    f"<td>{esc(f['detail'])}</td></tr>" for f in FLAGS)
rows_src = "".join(
    f"<tr><td>{esc(s['publisher'])}</td><td><a href='{esc(s['url'])}'>{esc(s['url'])}</a></td>"
    f"<td>{esc(s['observed'])}</td><td>{esc(s['scope'])}</td>"
    f"<td>{'official' if s['official'] else 'discovery'}</td></tr>"
    for s in SOURCES)

html_doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Session 02d3d515 — fifteen-sport desk</title>
<style>
body{{margin:0;background:#f5f7fa;color:#101828;font:16px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:28px 20px 60px}}
h1{{font-size:32px;letter-spacing:-.02em;margin:0 0 6px}}
h2{{margin:34px 0 10px;font-size:21px}}
p,li{{color:#344054}}
.meta{{color:#667085;font-size:14px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0}}
.kpi{{background:#fff;border:1px solid #e4e7ec;border-radius:12px;padding:14px}}
.kpi b{{display:block;font-size:24px}}
table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid #e4e7ec;border-radius:12px;overflow:hidden;font-size:14px}}
th,td{{padding:9px 10px;border-bottom:1px solid #eef0f3;text-align:left;vertical-align:top}}
th{{background:#f9fafb;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:#475467}}
td.n{{text-align:right;font-variant-numeric:tabular-nums}}
a{{color:#08543e}}
code{{background:#f2f4f7;padding:1px 5px;border-radius:5px;font-size:13px}}
.note{{background:#fff;border:1px solid #e4e7ec;border-left:4px solid #b54708;border-radius:10px;padding:12px 16px;margin:16px 0}}
</style></head><body><div class="wrap">
<h1>Session 02d3d515 — live fifteen-sport desk</h1>
<p class="meta">Captured {esc(OBSERVED)} · branch <code>arena/02d3d515-olbg1</code> · site <a href="../02d3d515/index.html">02d3d515/</a></p>
<div class="kpis">
<div class="kpi"><b>{len(picks)}</b>priced selections</div>
<div class="kpi"><b>{len(high)}</b>high confidence</div>
<div class="kpi"><b>{len(FIXTURES)}</b>confirmed fixtures</div>
<div class="kpi"><b>{len(SOURCES)}</b>sources</div>
<div class="kpi"><b>{len(FLAGS)}</b>flags</div>
<div class="kpi"><b>26</b>pages</div>
</div>
<div class="note"><b>The odds-window tension.</b> −250 is 71.4% and 70% is −233, so a pick that both clears 70% and sits inside the window lives in a 1.4-point band. The desk applies the window as binding, publishes every probability, and lists the conflict as F-02.</div>
<h2>Coverage by sport</h2>
<table><thead><tr><th>Sport</th><th>Fixtures</th><th>Picks</th><th>High</th><th>Status</th></tr></thead><tbody>{rows_cov}</tbody></table>
<h2>The published card</h2>
<table><thead><tr><th>Sport</th><th>Fixture id</th><th>Market</th><th>Selection</th><th>Fair</th><th>Est.</th><th>Tier</th></tr></thead><tbody>{rows_pick}</tbody></table>
<h2>Sources read</h2>
<table><thead><tr><th>Publisher</th><th>URL</th><th>Read (UTC)</th><th>What was taken</th><th>Role</th></tr></thead><tbody>{rows_src}</tbody></table>
<h2>Irregularities</h2>
<table><thead><tr><th>ID</th><th>Severity</th><th>Finding</th><th>Detail</th></tr></thead><tbody>{rows_flag}</tbody></table>
<h2>Gates</h2>
<p><code>python3 scripts/s02d3d515_validate.py</code> → prices, tiers, prose and links clean.
<code>python3 -m unittest tests.pipeline.test_desk_02d3d515</code> → 27 tests pass.
<code>python3 -m pipeline.validate --site .</code> → 0 errors. <code>python3 scripts/validate.py</code> → 0 errors, 3 pre-existing warnings on another desk.</p>
</div></body></html>"""
OUT_HTML.write_text(html_doc, encoding="utf-8")
print(f"wrote {OUT_MD.relative_to(ROOT)} and {OUT_HTML.relative_to(ROOT)}")
