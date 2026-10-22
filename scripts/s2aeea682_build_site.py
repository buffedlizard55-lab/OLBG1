"""Build the dependency-free, source-linked /2aeea682/ static dashboard."""
from pathlib import Path
from urllib.parse import urlparse
import html
import json
import shutil
import s2aeea682_data as D

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "2aeea682"
OUT = ROOT / "2aeea682"
DESK = json.loads((DATA/"desk.json").read_text(encoding="utf-8"))
FLAGS = json.loads((DATA/"flags.json").read_text(encoding="utf-8"))
REPO = json.loads((DATA/"repo_audit.json").read_text(encoding="utf-8"))
SOURCES = {s["id"]:s for s in DESK["sources"]}
FIXTURES = {f["id"]:f for f in DESK["fixtures"]}
COVERAGE_SOURCE = {
    "tennis":"wta-ningbo","basketball":"euroleague-r7","golf":"pga","cricket":"pcb","snooker":"wst",
    "rugby-union":"urc-fixtures","rugby-league":"irl","baseball":"mlb-schedule","ice-hockey":"nhl-schedule",
    "motor-racing":"f1","darts":"pdc","handball":"ehf","volleyball":"volleyball","aussie-rules":"aflw",
    "esports":"lol","gaelic-football":"gaa","greyhounds":"gbgb",
}
DISCOVERY_RECHECK = {"olbg-sitemap":"nhl-schedule","olbg-baseball":"mlb-schedule","olbg-basketball":"euroleague-r7","olbg-tennis":"wta-ningbo","olbg-hockey":"nhl-schedule"}


def esc(value):
    return html.escape("" if value is None else str(value),quote=True)


def link(url,label="Official source",cls="source-link"):
    return f'<a class="{cls}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)} <span aria-hidden="true">↗</span></a>'


def tr(cells,url,label="Official source",attrs=""):
    return f'<tr data-source-row {attrs}>' + "".join(f"<td>{c}</td>" for c in cells) + f"<td>{link(url,label)}</td></tr>"


def table(headers,rows,table_id="",cls=""):
    return (f'<div class="table-wrap"><table id="{esc(table_id)}" class="data-table {esc(cls)}"><thead><tr>'
            + "".join(f"<th>{esc(h)}</th>" for h in headers) + "<th>Verification</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table></div>")


def fixture_name(f):
    if f["kind"] == "event":
        return esc(f["side_a"])
    if f["away"] and f["home"]:
        return f"{esc(f['away'])} <span class='at'>@</span> {esc(f['home'])}"
    return f"{esc(f['side_a'])} <span class='at'>v</span> {esc(f['side_b'])}"


def tier(t):
    return f'<span class="tier {esc((t or "").lower())}">{esc(t)}</span>' if t else ""


def price_cell(wp):
    if not wp:
        return ""
    probability = f"{100*wp['probability']:.2f}%"
    american = f"{wp['fair_american']:+d}"
    return f"<strong>{esc(wp['selection'])}</strong><br><span class='muted'>{probability} · fair {american} · {tier(wp['tier'])}</span>"


def high_cell(h):
    if not h:
        return ""
    return f"<strong>{esc(h['selection'])}</strong><br><span class='muted'>{100*h['probability']:.2f}% · fair {h['fair_american']:+d}</span>"


NAV = [("index.html","Overview"),("matches.html","Matches"),("markets.html","Markets"),("high-confidence.html","High confidence"),("predictions.html","Predictions"),("coverage.html","Coverage"),("flagged.html","Flagged")]


def page(title,body,prefix="",description="Officially sourced fixtures and experimental originated lines"):
    nav = "".join(f'<a href="{prefix}{href}">{label}</a>' for href,label in NAV)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · OLBG Research Desk</title><meta name="description" content="{esc(description)}">
<link rel="stylesheet" href="{prefix}assets/style.css"><script defer src="{prefix}assets/app.js"></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="header-inner">
<a class="brand" href="{prefix}index.html"><span class="brand-mark">OL</span><span><strong>OLBG Research Desk</strong><small>Fresh evidence · 22 Oct 2026</small></span></a>
<nav aria-label="Primary">{nav}</nav></div></header>
<div class="notice"><strong>Independent research.</strong> Originated fair prices are experimental estimates, not bookmaker quotes or guarantees. Not affiliated with OLBG.</div>
<main id="main" class="container"><div class="page-heading"><div><p class="eyebrow">SESSION 2AEEA682 · READ {esc(DESK['read_at_utc'])}</p><h1>{esc(title)}</h1></div>
<a class="button secondary" href="{prefix}matches.html">Browse all rows</a></div>{body}</main>
<footer><div><strong>Evidence before certainty.</strong> Blank cells are intentional. Every sporting row links to an official publisher.</div>
<div class="footer-links"><a href="{prefix}methodology.html">Methodology</a><a href="{prefix}sources.html">Sources</a><a href="{prefix}analysis.html">Analysis</a><a href="{prefix}reverse-engineering.html">Reverse engineering</a><a href="{prefix}repo-audit.html">Repo audit</a><a href="{prefix}../archive.html">Canonical archive</a></div></footer></body></html>'''


def write(name,title,body,prefix=""):
    path = OUT/prefix/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(page(title,body,"../" if prefix else "",),encoding="utf-8")


def fixture_rows(items,prefix=""): 
    rows = []
    for f in items:
        wp,hp = f["winner_pick"],f["featured_high"]
        attrs = f'data-sport="{esc(f["sport"])}" data-priced="{str(f["priced"]).lower()}" data-search="{esc((f["side_a"] or "")+" "+(f["side_b"] or "")+" "+f["competition"])}"'
        gap = "" if f["priced"] else f'<span class="gap-text">{esc(f["unpriced_reason"])}</span>'
        start = esc(f["display_time"]) if f["display_time"] else ""
        venue = esc(f["venue"]) if f["venue"] else ""
        high = high_cell(hp)
        if hp:
            high = f'<a href="{prefix}predictions.html#{esc(hp["fixture_id"])}">{high}</a>'
        rows.append(tr([f'<strong>{esc(f["date"])}</strong>',esc(f["sport_name"]),esc(f["competition"]),
                        f'<strong>{fixture_name(f)}</strong><br><span class="muted">{esc(f["id"])}</span>',
                        start,venue,("Priced" if f["priced"] else "")+gap,price_cell(wp),high],f["official_link"],attrs=attrs))
    return rows


def filters(id_prefix,sports=True):
    sport_options = '<option value="">All sports</option>'+''.join(f'<option value="{s}">{n}</option>' for s,n,_,_ in D.SPORTS) if sports else ''
    return f'''<section class="filters" aria-label="Table filters"><label>Search<input id="{id_prefix}-search" type="search" placeholder="Team, player or competition"></label>
<label>Sport<select id="{id_prefix}-sport">{sport_options}</select></label><label>Price status<select id="{id_prefix}-priced"><option value="">All rows</option><option value="true">Priced</option><option value="false">Unpriced</option></select></label>
<button class="button" id="{id_prefix}-reset" type="button">Reset</button><span class="filter-count" id="{id_prefix}-count" aria-live="polite"></span></section>'''


def build_index():
    c = DESK["counts"]
    cards = [(c["fixtures"],"Officially read listings"),(c["sports_with_fixtures"],"Sports with rows"),(c["priced"],"Priced fixtures"),(c["markets"],"Originated markets"),(c["featured_high"],"Featured High picks"),(c["unpriced"],"Blank-and-flag rows")]
    card_html = "".join(f'<div class="kpi"><strong>{value}</strong><span>{esc(label)}</span></div>' for value,label in cards)
    sport_cards = []
    for row in DESK["coverage"]:
        sport_cards.append(f'<a class="sport-card" href="sports/{row["sport"]}.html"><span>{esc(row["name"])}</span><strong>{row["fixtures"]}</strong><small>{row["priced"]} priced · {row["markets"]} markets</small></a>')
    high_rows = [tr([f'<strong>{esc(FIXTURES[h["fixture_id"]]["side_a"])} v {esc(FIXTURES[h["fixture_id"]]["side_b"])}</strong>',esc(h["market"]),esc(h["selection"]),f'{100*h["probability"]:.2f}%',f'{h["fair_american"]:+d}'],h["official_link"]) for h in DESK["featured_high"]]
    body = f'''<section class="hero"><div><p class="eyebrow">FRESH OFFICIAL READS · NO INHERITED FRESHNESS</p><h2>A transparent match board, including what we could not verify.</h2>
<p>Seventeen sport categories are organised below. Ten have current official rows; seven remain visible with a named source gap. Only seven fixtures have paired inputs for originated lines. Everything else stays blank and reviewable.</p>
<div class="actions"><a class="button" href="matches.html">View 71 listings</a><a class="button secondary" href="predictions.html">Read 4 High previews</a><a class="button secondary" href="coverage.html">Check coverage</a></div></div>
<aside class="freshness"><strong>Evidence cutoff</strong><span>{esc(DESK['read_at_utc'])}</span><small>Fixed snapshot. Do not treat a rebuild as a fresh official read.</small></aside></section>
<section class="kpi-grid">{card_html}</section>
<section class="panel warning"><h2>High is a narrow model label</h2><p>All four featured selections are <strong>Under 10 runs, push refunded at ten</strong>. Each clears the gate at 70.04% and fair −234. That is only 0.04 percentage points above the threshold; no pitcher, lineup, park or postseason adjustment is claimed.</p></section>
<section><div class="section-heading"><h2>Sports</h2><a href="sports.html">All category pages</a></div><div class="sport-grid">{''.join(sport_cards)}</div></section>
<section><div class="section-heading"><h2>Featured High selections</h2><a href="high-confidence.html">Gate details</a></div>{table(["Fixture","Market","Selection","Model probability","Fair American"],high_rows)}</section>
<section class="panel"><h2>What “verified” means here</h2><p>Fixture fields were directly observed on the linked league, governing-body, tour or federation page. Model numbers are separately labelled estimates. A source URL by itself is not proof; inaccessible, incomplete or contradictory reads are published on the <a href="flagged.html">Flagged for Review page</a>.</p></section>'''
    write("index.html","Research overview",body)


def build_matches():
    body = f'''<p class="lede">All 71 officially read listings. Empty price and winner cells mean no defensible model input was available; the gap column says why.</p>{filters("matches")}
{table(["Date","Sport","Competition","Fixture","Published start","Venue","Price status / gap","Winner preference (model)","Featured High"],fixture_rows(DESK["fixtures"]),"matches-table")}
<p class="footnote"><a href="../data/2aeea682/fixtures.csv">Download fixtures CSV</a> · Times remain in their published zone; blank UTC values are never inferred.</p>'''
    write("matches.html","All matches and events",body)


def build_markets():
    rows=[]
    for f in DESK["fixtures"]:
        for m in f["markets"]:
            for o in m["outcomes"]:
                featured = f["featured_high"] and f["featured_high"]["market_id"] == m["id"] and f["featured_high"]["selection"] == o["selection"]
                attrs=f'data-sport="{esc(f["sport"])}" data-priced="true" data-search="{esc(f["side_a"]+" "+f["side_b"]+" "+m["market"]+" "+o["selection"])}"'
                rows.append(tr([esc(f["sport_name"]),f'<strong>{fixture_name(f)}</strong>',esc(m["market"]),f'<strong>{esc(o["selection"])}</strong>',f'{100*o["probability"]:.2f}%',f'{o["fair_decimal"]:.4f}',f'{o["fair_american"]:+d}',"Yes" if o["in_brief_window"] else "No",tier("High") if featured else ""],f["official_link"],attrs=attrs))
    investigation=[]
    for slug,name,_,_ in D.SPORTS:
        src=SOURCES[COVERAGE_SOURCE[slug]]
        for market_name,status,reason in D.MARKET_INVESTIGATION[slug]:
            investigation.append(tr([esc(name),esc(market_name),esc(status),esc(reason)],src["url"]))
    body=f'''<p class="lede">Every originated outcome, with zero-margin fair prices derived from unrounded probabilities. “Window” is the brief’s −250…+10000 range, not an availability claim.</p>{filters("markets")}
{table(["Sport","Fixture","Market","Selection","Probability","Fair decimal","Fair American","In window","Featured"],rows,"markets-table")}
<p class="footnote"><a href="../data/2aeea682/markets.csv">Download markets CSV</a> · 87 markets / 178 outcomes across seven priced fixtures.</p>
<section><div class="section-heading"><h2>Market investigation by sport</h2><span>Priced or withheld with a reason</span></div>{table(["Sport","Market family","Status","Evidence / limitation"],investigation)}</section>'''
    write("markets.html","Originated markets",body)


def build_high():
    rows=[]
    for f in DESK["fixtures"]:
        for h in f["high_candidates"]:
            featured = f["featured_high"] and h["selection"] == f["featured_high"]["selection"] and h["market_id"] == f["featured_high"]["market_id"]
            rows.append(tr([fixture_name(f),esc(h["market"]),esc(h["selection"]),f'{100*h["probability"]:.4f}%',f'{h["fair_american"]:+d}',tier("High") if featured else "Alternate"],h["official_link"]))
    body=f'''<section class="panel"><h2>Strict gate</h2><p>A High candidate must have <strong>probability above 70%</strong> and an <strong>unrounded fair American price from −250 through +10000</strong>. The strongest qualifying outcome per fixture receives bespoke prose; alternates would remain listed here. All four current candidates are featured, so there are no hidden qualifying outcomes.</p></section>
{table(["Fixture","Market","Selection","Exact probability","Fair American","Publication"],rows)}
<section class="panel warning"><h2>Do not read High as certainty</h2><p>The featured line is 70.0400%, fair −234, generated from a transparent but uncalibrated regular-season Poisson model. It omits known-important baseball context. Four games share the same team inputs and therefore the same numbers; they are not four independent model confirmations.</p></section>'''
    write("high-confidence.html","High-confidence gate",body)


def build_predictions():
    sections=[]
    for p in DESK["predictions"]:
        f=FIXTURES[p["fixture_id"]]
        facts=[tr([esc(x["kind"]),esc(x["claim"])],SOURCES[x["source_id"]]["url"],"Official evidence") for x in p["facts"]]
        sections.append(f'''<article class="prediction" id="{esc(p["fixture_id"])}"><div class="prediction-head"><div><p class="eyebrow">{esc(p["id"])} · {esc(f["competition"])}</p><h2>{fixture_name(f)}</h2></div>{tier("High")}</div>
<p class="selection"><strong>Selection: {esc(p["selection"])}</strong> · {100*p["probability"]:.2f}% · fair {p["fair_american"]:+d}</p>
<p class="prediction-text">{esc(p["text"])}</p><p class="muted">{p["word_count"]} words · model selection, not a bookmaker recommendation</p>
<details><summary>Verify the evidence behind this preview</summary>{table(["Evidence type","Claim checked"],facts)}</details>
<p>{link(f["official_link"],"Official fixture page")}</p></article>''')
    body=f'''<p class="lede">Four unique, source-bounded previews. Team and player mentions, current form and recent results are linked underneath each card. No starting role is inferred from roster membership.</p>{''.join(sections)}'''
    write("predictions.html","High-confidence predictions",body)


def build_coverage():
    rows=[]
    for c in DESK["coverage"]:
        src=SOURCES[COVERAGE_SOURCE[c["sport"]]]
        rows.append(tr([f'<a href="sports/{c["sport"]}.html"><strong>{esc(c["name"])}</strong></a>',str(c["fixtures"]),str(c["priced"]),str(c["unpriced"]),str(c["markets"]),esc(c["note"])],src["url"],"Official recheck"))
    body=f'''<p class="lede">Coverage is deliberately explicit. Zero rows means no fixture was promoted from the official read—not that the sport has no matches anywhere.</p>{table(["Sport","Listings","Priced","Unpriced","Markets","Coverage finding"],rows)}
<section class="panel"><h2>Excluded categories</h2><p>{esc(", ".join(D.EXCLUDED))}. Gaelic football and Aussie rules remain distinct inherited OLBG categories; hurling and shinty-hurling are not imported.</p></section>'''
    write("coverage.html","Coverage and gaps",body)


def build_sports():
    cards=[]
    for c in DESK["coverage"]:
        cards.append(f'<a class="sport-card" href="sports/{c["sport"]}.html"><span>{esc(c["name"])}</span><strong>{c["fixtures"]}</strong><small>{c["priced"]} priced · {c["markets"]} markets</small></a>')
    write("sports.html","Sport categories",f'<p class="lede">Choose a category for its fixture table, source status and market limitations.</p><div class="sport-grid">{"".join(cards)}</div>')


def build_sport_pages():
    for slug,name,_,_ in D.SPORTS:
        items=[f for f in DESK["fixtures"] if f["sport"]==slug]
        note=D.COVERAGE_NOTES[slug]
        src=SOURCES[COVERAGE_SOURCE[slug]]
        if items:
            content=table(["Date","Sport","Competition","Fixture","Published start","Venue","Price status / gap","Winner preference (model)","Featured High"],fixture_rows(items,"../"))
        else:
            content=f'<section class="empty"><h2>No verified rows published</h2><p>This is an evidence gap, not a zero-fixture claim. Values are left blank rather than recovered from expired desks.</p><p>{link(src["url"],"Official recheck source")}</p></section>'
        investigations=[]
        for market_name,status,reason in D.MARKET_INVESTIGATION[slug]:
            investigations.append(tr([esc(market_name),esc(status),esc(reason)],src["url"]))
        body=f'''<section class="panel"><h2>Coverage finding</h2><p>{esc(note)}</p><p>{link(src["url"],"Official source / recheck")}</p></section>{content}
<section><div class="section-heading"><h2>Market coverage</h2><span>{len(items)} listings</span></div>{table(["Market family","Status","Evidence / limitation"],investigations)}</section>'''
        write(f"{slug}.html",name,body,prefix="sports/")


def build_sources():
    rows=[]
    for s in DESK["sources"]:
        if s["official"]:
            official=s["url"]
        else:
            official=SOURCES[DISCOVERY_RECHECK[s["id"]]]["url"]
        role=s["role"]+(" (not official)" if not s["official"] else "")
        rows.append(tr([esc(s["publisher"]),esc(role),esc(s["observed"]),esc(s["limitation"]),link(s["url"],"Open cited page")],official,"Official recheck"))
    body=f'''<p class="lede">Read timestamp for this fixed snapshot: {esc(DESK["read_at_utc"])}. OLBG appears only as a discovery source and is always paired with an official recheck destination.</p>{table(["Publisher","Role","Actually observed","Limitation","Citation"],rows)}'''
    write("sources.html","Source register",body)


def build_flagged():
    rows=[]
    for f in FLAGS:
        affected=", ".join(f["fixture_ids"]) if f["fixture_ids"] else "Coverage / policy"
        extra = f'<br>{link(D.SOURCE_MAP["olbg-baseball"]["url"],"OLBG discovery")}' if f["id"]=="F-2AEE-21" else ""
        rows.append(tr([f'<strong>{esc(f["id"])}</strong>',f'<span class="severity {esc(f["severity"])}">{esc(f["severity"])}</span>',f'<strong>{esc(f["title"])}</strong><br>{esc(f["detail"])}',esc(affected)+extra],f["url"],"Official review"))
    body=f'''<p class="lede">Non-blocking issues for manual review. Nothing here is silently corrected, hidden or promoted to verified.</p>{table(["ID","Severity","Finding and impact","Affected rows"],rows,"flagged-table")}
<section class="panel"><h2>Repository-specific findings</h2><p>{len(REPO)} additional file-and-line findings are published separately on the <a href="repo-audit.html">Repo Audit page</a>.</p></section>'''
    write("flagged.html","Flagged for Review",body)


def build_analysis():
    c=DESK["counts"]
    high=DESK["featured_high"][0]
    comparison_rows=[
        tr(["Independent winner model","Milwaukee Brewers","55.54%","fair -125","Regular-season runs model; not a market quote"],SOURCES["mlb-al"]["url"]),
        tr(["OLBG tip share (discovery)","Milwaukee Brewers","80% (16/20)","", "Community tip share; not used in the model"],SOURCES["mlb-schedule"]["url"]),
    ]
    body=f'''<section class="kpi-grid"><div class="kpi"><strong>{c["high_candidates"]}</strong><span> qualifying High outcomes</span></div><div class="kpi"><strong>{c["winner_medium"]}</strong><span> Medium winner leans</span></div><div class="kpi"><strong>{c["winner_low"]}</strong><span> Low / no-lean winners</span></div><div class="kpi"><strong>70.04%</strong><span> narrowest High clearance</span></div></section>
<section class="panel"><h2>Selection finding</h2><p>The model favours Milwaukee on the moneyline at only 55.54% (Medium), but its full-game run distribution makes Under 10 with a push the strongest in-window outcome at 70.04% (High). This is why match-winner confidence and featured market confidence are shown separately.</p></section>
<section><div class="section-heading"><h2>Market-price caution</h2><span>Different measures, not an edge calculation</span></div>{table(["Measure","Selection","Published value","Fair price","Interpretation"],comparison_rows)}</section>
<section class="panel warning"><h2>Model risk</h2><p>The 8.7531 expected total is calculated from regular-season scoring and allowance rates. Starting pitchers, bullpens, lineups, park, weather, rest and postseason behaviour are not in the model. The 70.04% result should be read as a fragile model output, not a verified 70.04% real-world chance.</p></section>
<section class="panel"><h2>Reproducibility</h2><p><code>python3 scripts/s2aeea682_model.py</code> rebuilds the dataset and CSV exports. <code>python3 scripts/s2aeea682_audit.py</code> rebuilds findings. <code>python3 scripts/s2aeea682_build_site.py</code> renders this desk. <code>python3 scripts/s2aeea682_validate.py</code> checks every row, price, prediction and local link.</p></section>'''
    write("analysis.html","Analysis and findings",body)


def build_methodology():
    body='''<section class="panel"><h2>Verification contract</h2><ol><li>OLBG routes are discovery only.</li><li>A fixture is published only after its fields are observed on an official league, tour, federation or governing-body page.</li><li>Unknown values remain blank and carry a coverage note or flag.</li><li>Model-derived values are estimates, never sourced facts.</li><li>Expired desks are historical leads, not fresh evidence.</li></ol></section>
<section class="panel"><h2>MLB independent Poisson v1</h2><p>For away team A and home team B, <code>λA = ((RS_A/G_A)+(RA_B/G_B))/2</code> and <code>λB = ((RS_B/G_B)+(RA_A/G_A))/2</code>. Independent Poisson score grids produce winner, nine-inning, run-line, match-total and team-total probabilities. Nine-inning ties are split by expected-run share for the match-winner estimate. Integer total prices condition on no push.</p><p>No pitcher, park, weather, lineup, rest or postseason adjustment is inserted. Conditional Game 5 is not priced.</p></section>
<section class="panel"><h2>EuroLeague log5 v1</h2><p>Official records are Beta(2,2) shrunk, then combined using log5. No home advantage is inserted. Exact 50/50 games show <strong>No winner preference</strong>. Spreads and totals are withheld because paired margin/scoring inputs are incomplete.</p></section>
<section class="panel"><h2>Price and confidence arithmetic</h2><p><code>Fair decimal = 1/p</code>. American prices derive from the unrounded probability with no margin or clipping. High requires <code>p &gt; 0.70</code> and <code>-250 ≤ fair American ≤ +10000</code>. Because fair prices shorter than −250 correspond to probabilities above 71.4286%, the literal High band for favourites is narrow.</p><p>The strongest qualifying outcome per fixture is featured. Winner preference has its own Low/Medium/High label; derivative High selections do not change that winner label.</p></section>
<section class="panel"><h2>Prose gate</h2><p>Every featured High has a unique 30+ word preview. Automated checks require team, player, current-form and recent-history evidence categories, an obvious selection, official fact links and no repeated eight-word passage across previews. Roster presence is never described as confirmation of a start.</p></section>'''
    write("methodology.html","Methodology",body)


def build_reverse():
    rows=[]
    for slug,name,olbg_id,route in D.SPORTS:
        olbg=f"https://www.olbg.com/betting-tips/{route}/{olbg_id}"
        official=SOURCES[COVERAGE_SOURCE[slug]]["url"]
        rows.append(tr([esc(name),str(olbg_id),f'<code>/betting-tips/{esc(route)}/{olbg_id}</code>',link(olbg,"OLBG hub")],official,"Official recheck"))
    taxonomy=[
        tr(["Baseball","Money Line; Run Line; Game Totals; Ante-post","OLBG's own explanatory text; player props noted as not carrying OLBG tips"],SOURCES["mlb-schedule"]["url"]),
        tr(["Basketball","Money Line; Pointspread","Observed on current NBA and EuroLeague cards"],SOURCES["euroleague-r7"]["url"]),
        tr(["Tennis","Win Match; Set Betting; Games Won; Total Games","Observed on current cards"],SOURCES["wta-ningbo"]["url"]),
        tr(["Ice hockey","Money Line; Game Totals; Puck Line","Observed on current NHL and European cards"],SOURCES["nhl-schedule"]["url"]),
    ]
    body=f'''<section class="panel"><h2>Route grammar and scope</h2><p>The sitemap exposes numeric sport IDs and <code>/betting-tips/&lt;sport&gt;/&lt;id&gt;</code> hubs. Event links add competition path segments and <code>event_id</code>. Cards expose tip counts and market labels; those are community inputs, not official fixture evidence or bookmaker odds.</p><p>The visible page includes a <strong>Load More Tips</strong> control, so one extraction is not treated as a complete event census. No hidden/private API or access-control bypass is used.</p></section>
{table(["Sport","OLBG ID","Hub route","Discovery link"],rows)}
<section><div class="section-heading"><h2>Observed market labels</h2><span>Discovery only</span></div>{table(["Sport","Labels observed","Evidence boundary"],taxonomy)}</section>
<section class="panel warning"><h2>Exclusions applied</h2><p>{esc(", ".join(D.EXCLUDED))}. The GAA Shinty-Hurling International was explicitly excluded. Gaelic football and Aussie rules remain separate categories, consistent with the repository’s inherited scope.</p></section>'''
    write("reverse-engineering.html","OLBG reverse engineering",body)


def build_repo_audit():
    rows=[tr([f'<strong>{esc(r["id"])}</strong>',f'<span class="severity {esc(r["severity"])}">{esc(r["severity"])}</span>',f'<strong>{esc(r["title"])}</strong><br>{esc(r["detail"])}',f'<code>{esc(r["locator"])}</code>'],r["url"],"Immutable file review") for r in REPO]
    body=f'''<p class="lede">Bounded review of current coordination and canonical-release claims, plus fresh source irregularities. This does not pretend to recertify every historical sentence in the repository.</p>{table(["ID","Severity","Finding","File and line"],rows)}
<section class="panel"><h2>Scope control</h2><p>This session changes only its namespaced data, scripts, site and report, plus its own append-only coordination record. Canonical pages, pipeline code and historical desks are not edited.</p></section>'''
    write("repo-audit.html","Repository audit",body)


def assets():
    (OUT/"assets").mkdir(parents=True,exist_ok=True)
    (OUT/"assets"/"style.css").write_text('''
:root{--ink:#15263b;--muted:#607086;--line:#dce4ec;--paper:#f5f7fa;--card:#fff;--navy:#102a43;--teal:#087f8c;--amber:#fff5d6;--red:#a62b2b;--green:#17745b}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}a{color:#076b78;text-underline-offset:2px}a:hover{text-decoration-thickness:2px}.skip{position:absolute;left:-999px}.skip:focus{left:10px;top:10px;background:white;padding:8px;z-index:20}.site-header{background:var(--navy);color:white}.header-inner{max-width:1500px;margin:auto;padding:18px 24px;display:flex;gap:28px;align-items:center;justify-content:space-between}.brand{display:flex;align-items:center;gap:11px;color:white;text-decoration:none;white-space:nowrap}.brand small{display:block;color:#b9ccdd;font-size:11px}.brand-mark{display:grid;place-items:center;width:38px;height:38px;border:1px solid #5e7b93;border-radius:9px;color:#8fe5e8;font-weight:800}nav{display:flex;gap:18px;flex-wrap:wrap}nav a{color:#dce9f2;text-decoration:none;font-size:13px}nav a:hover{color:white;text-decoration:underline}.notice{text-align:center;background:#e4f4f3;color:#174d51;padding:8px 20px;font-size:12px}.container{max-width:1500px;margin:auto;padding:28px 24px 60px}.page-heading{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:20px}.page-heading h1{margin:0;font-size:30px;letter-spacing:-.5px}.eyebrow{font-size:11px;letter-spacing:1.2px;font-weight:750;color:#587087;margin:0 0 6px;text-transform:uppercase}.lede{max-width:980px;color:var(--muted);font-size:16px}.hero{display:grid;grid-template-columns:1fr 280px;gap:28px;background:var(--navy);color:white;border-radius:14px;padding:30px;margin-bottom:22px}.hero h2{font-size:29px;line-height:1.18;max-width:800px;margin:5px 0 14px}.hero p:not(.eyebrow){color:#d5e2ec;max-width:850px}.hero .eyebrow{color:#8fe5e8}.freshness{border-left:1px solid #49647a;padding-left:24px;display:flex;flex-direction:column;justify-content:center}.freshness span{font-size:18px;margin:8px 0}.freshness small{color:#b9ccdd}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}.button{display:inline-block;border:0;border-radius:7px;background:var(--teal);color:white;padding:9px 14px;text-decoration:none;font-weight:650;cursor:pointer;font-size:13px}.button.secondary{background:#e4edf2;color:#173b4d}.hero .button.secondary{background:#28465e;color:white}.kpi-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:18px 0 26px}.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:17px}.kpi strong{display:block;font-size:26px;line-height:1.1}.kpi span{display:block;color:var(--muted);font-size:12px;margin-top:6px}.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:20px;margin:20px 0}.panel h2{margin-top:0}.panel.warning,.warning{background:var(--amber);border-color:#e4cf84}.section-heading{display:flex;align-items:center;justify-content:space-between;gap:15px;margin:28px 0 12px}.section-heading h2{margin:0;font-size:20px}.section-heading span{color:var(--muted);font-size:12px}.sport-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}.sport-card{background:white;border:1px solid var(--line);border-radius:9px;padding:14px;text-decoration:none;color:var(--ink)}.sport-card:hover{border-color:var(--teal)}.sport-card span,.sport-card small{display:block}.sport-card strong{display:block;font-size:24px;margin:5px 0}.sport-card small{color:var(--muted)}.table-wrap{overflow:auto;background:white;border:1px solid var(--line);border-radius:10px;margin-bottom:16px}.data-table{border-collapse:collapse;width:100%;min-width:900px;font-size:12px}.data-table th{position:sticky;top:0;background:#edf2f6;text-align:left;color:#40546a;font-size:10px;text-transform:uppercase;letter-spacing:.5px}.data-table th,.data-table td{padding:11px 12px;border-bottom:1px solid #e7edf2;vertical-align:top}.data-table tbody tr:hover{background:#f5fafb}.data-table td:last-child{min-width:125px}.data-table tr[hidden]{display:none}.source-link{white-space:nowrap;font-size:11px}.muted{color:var(--muted);font-size:11px}.at{color:#8190a0;padding:0 3px}.tier,.severity{display:inline-block;border-radius:20px;padding:1px 7px;font-size:10px;font-weight:750;text-transform:uppercase}.tier.high,.severity.high{background:#d9f1e7;color:#116149}.tier.medium,.severity.medium{background:#fff0c2;color:#775900}.tier.low,.severity.low{background:#e8edf1;color:#526577}.severity.info{background:#dfecf7;color:#375f7d}.gap-text{display:block;color:#7c5d17;max-width:320px;font-size:11px}.filters{display:flex;gap:12px;align-items:end;flex-wrap:wrap;background:white;border:1px solid var(--line);border-radius:10px;padding:13px;margin:18px 0}.filters label{font-size:11px;color:var(--muted);font-weight:650}.filters input,.filters select{display:block;margin-top:4px;border:1px solid #bccbd7;border-radius:6px;padding:8px;background:white;color:var(--ink);min-width:145px}.filters input{min-width:260px}.filter-count{font-size:12px;color:var(--muted);padding-bottom:8px}.footnote{color:var(--muted);font-size:12px}.prediction{background:white;border:1px solid var(--line);border-radius:12px;padding:22px;margin:20px 0;scroll-margin-top:20px}.prediction-head{display:flex;justify-content:space-between;gap:15px}.prediction h2{margin:0}.prediction .selection{background:#e8f5f3;border-radius:7px;padding:11px}.prediction-text{font-size:16px;line-height:1.7}.prediction details{margin:14px 0}.prediction summary{cursor:pointer;font-weight:650}.empty{padding:28px;background:white;border:1px dashed #aebdca;border-radius:10px}code{font-size:12px;overflow-wrap:anywhere}footer{border-top:1px solid var(--line);padding:24px;display:flex;justify-content:space-between;gap:20px;color:var(--muted);font-size:12px;background:white}.footer-links{display:flex;gap:14px;flex-wrap:wrap}
@media(max-width:1150px){.kpi-grid{grid-template-columns:repeat(3,1fr)}.sport-grid{grid-template-columns:repeat(4,1fr)}.header-inner{align-items:flex-start;flex-direction:column;gap:12px}.hero{grid-template-columns:1fr}.freshness{border-left:0;border-top:1px solid #49647a;padding:15px 0 0}}@media(max-width:700px){.container{padding:20px 12px 40px}.header-inner{padding:15px 14px}nav{gap:11px}.page-heading{align-items:flex-start}.page-heading .button{display:none}.hero{padding:20px}.hero h2{font-size:24px}.kpi-grid{grid-template-columns:repeat(2,1fr)}.sport-grid{grid-template-columns:repeat(2,1fr)}.filters{align-items:stretch;flex-direction:column}.filters input,.filters select{width:100%;min-width:0}.filters .button{align-self:flex-start}footer{flex-direction:column}.prediction{padding:16px}}
''',encoding="utf-8")
    (OUT/"assets"/"app.js").write_text('''
(function(){function setup(prefix,tableId){var table=document.getElementById(tableId);if(!table)return;var search=document.getElementById(prefix+'-search'),sport=document.getElementById(prefix+'-sport'),priced=document.getElementById(prefix+'-priced'),reset=document.getElementById(prefix+'-reset'),count=document.getElementById(prefix+'-count');var rows=Array.from(table.tBodies[0].rows);function apply(){var q=(search.value||'').toLowerCase(),s=sport.value,p=priced.value,n=0;rows.forEach(function(r){var show=(!q||(r.dataset.search||r.textContent).toLowerCase().includes(q))&&(!s||r.dataset.sport===s)&&(!p||r.dataset.priced===p);r.hidden=!show;if(show)n++;});count.textContent=n+' of '+rows.length+' rows';}search.addEventListener('input',apply);sport.addEventListener('change',apply);priced.addEventListener('change',apply);reset.addEventListener('click',function(){search.value='';sport.value='';priced.value='';apply();});apply();}setup('matches','matches-table');setup('markets','markets-table');})();
''',encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    assets()
    build_index();build_matches();build_markets();build_high();build_predictions();build_coverage();build_sports();build_sport_pages();build_sources();build_flagged();build_analysis();build_methodology();build_reverse();build_repo_audit()
    print(f"Built {len(list(OUT.rglob('*.html')))} HTML pages at {OUT}")

if __name__ == "__main__":
    main()
