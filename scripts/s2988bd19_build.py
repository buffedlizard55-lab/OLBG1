"""Render the /2988bd19/ dashboard and write data/2988bd19/desk.json."""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s2988bd19_data as D
import s2988bd19_model as M

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "2988bd19"
DATA = ROOT / "data" / "2988bd19"
REPO = "https://github.com/buffedlizard55-lab/OLBG1"


def e(v):
    return html.escape("" if v is None else str(v), quote=True)


def money(p):
    a = D.american(p)
    return f"{a:+.0f}" if a > 0 else f"{a:.0f}"


def moneyv(a):
    return f"{a:+.0f}" if a > 0 else f"{a:.0f}"


def dec(p):
    return f"{1/p:.3f}"


MONTHS = {m: n for m, n in zip(range(1, 13),
          ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"))}


def start(f):
    if f.get("start_utc"):
        t = f["start_utc"]
        return f"{int(t[8:10])} {MONTHS[int(t[5:7])]} · {t[11:16]} UTC"
    return f.get("start_local") or ""


TIER_CLASS = {"High": "b-high", "Medium": "b-med", "Low": "b-low"}
VERIF = {
    "official": ("Official", "b-ok"),
    "discovery": ("Discovery only", "b-gap"),
}


def table(headers, rows, numeric=(), cls=""):
    th = "".join(f'<th class="{"num" if i in numeric else ""}">{h}</th>' for i, h in enumerate(headers))
    body = "".join("<tr>" + "".join(f'<td class="{"num" if i in numeric else ""}">{c}</td>'
                                    for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tablewrap"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


NAV = [
    ("overview", "index.html", "Overview"),
    ("matches", "matches.html", "Match list"),
    ("markets", "markets.html", "Markets"),
    ("high", "high-confidence.html", "High confidence"),
    ("predictions", "predictions.html", "Predictions"),
    ("analysis", "analysis.html", "Analysis"),
    ("flags", "flagged.html", "Coverage & flags"),
    ("sources", "sources.html", "Sources"),
    ("method", "methodology.html", "Methodology"),
    ("review", "repo-review.html", "Repo review"),
    ("sports", "sports/index.html", "Sport pages"),
]


def page(path, title, desc, body, active, extra_head=""):
    depth = path.count("/")
    up = "../" * depth
    links = "".join(
        f'<a class="nav" href="{up}{href}"{" aria-current=page" if key == active else ""}>{label}'
        f'{"<span class=count>" + str(COUNTS["fixtures"]) + "</span>" if key == "matches" else ""}'
        f'{"<span class=count>" + str(COUNTS["high"]) + "</span>" if key == "high" else ""}'
        f'{"<span class=count>" + str(COUNTS["flags"]) + "</span>" if key == "flags" else ""}</a>'
        for key, href, label in NAV)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{e(desc)}">
<title>{e(title)} · OLBG independent desk 2988bd19</title>
<link rel="stylesheet" href="{up}assets/style.css">{extra_head}</head><body><div class="shell">
<aside class="side"><a class="brand" href="{up}index.html"><b>OLBG · independent desk</b><span>SESSION 2988bd19 · T2988</span></a>
<div class="grp">WORKSPACE</div>{links}
<div class="foot">Official-source fixtures, our own lines.<br>Blank means unverified.<br><br>
18+ · No guarantees. Prices are estimates, not bookmaker offers.<br><br>
<a style="color:#93c5fd" href="{REPO}">Repository</a></div></aside>
<main class="main"><div class="top"><span class="pill">Snapshot {e(D.BUILT)}</span>
<span class="pill">17 in-scope sports · 8 excluded</span>
<a class="pill" href="{up}flagged.html">Flags do not block publication</a></div>
{body}
<div class="foot"><span>Independent research · not affiliated with OLBG · no betting advice.</span> 
<span>Session {e(D.SESSION)} · task {e(D.TASK)} · <a href="{REPO}">source</a></span></div>
</main></div></body></html>"""
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(doc, encoding="utf-8")


COUNTS = {}


def main():
    fixtures, markets, discovered = M.build()
    summ = M.summarise(fixtures, markets, discovered)
    cov = M.coverage(fixtures, discovered)
    by_id = {f["id"]: f for f in fixtures}
    mkt = {m["id"]: m for m in markets}

    TOTAL = len(fixtures) + len(discovered)
    priced = [f for f in fixtures if f.get("priced")]
    official = [f for f in fixtures if f["verification"] == "official"]
    market_lines = sum(len(m["groups"]) for m in markets)
    COUNTS.update(fixtures=TOTAL, official=len(official), priced=len(priced),
                  markets=market_lines, selections=len(summ["selections"]),
                  high=len(summ["high"]), predictions=len(M.PREDICTIONS),
                  flags=len(M.FLAGS), sources=len(D.SOURCES),
                  verified_teams=len(D.NHL_TEAMS))

    HIGH = summ["high"]
    high_ids = {s["id"] for s in HIGH}
    capped = [s for s in summ["in_band"] if s["id"] not in high_ids]

    # ---------------------------------------------------------------- desk.json
    desk = dict(
        session=D.SESSION, task=D.TASK, generated_at=D.BUILT,
        scope=dict(included=[s for s, _ in D.SPORTS],
                   excluded=["football/soccer", "american football", "boxing", "UFC/MMA",
                             "hurling", "horse racing", "cycling", "specials"]),
        counts=dict(listings=TOTAL, officially_verified=len(official),
                    priced_fixtures=len(priced), market_lines=market_lines,
                    priced_selections=len(summ["selections"]), high=len(HIGH),
                    medium=sum(1 for s in summ["selections"] if s["tier"] == "Medium"),
                    low=sum(1 for s in summ["selections"] if s["tier"] == "Low"),
                    predictions=len(M.PREDICTIONS), flags=len(M.FLAGS), sources=len(D.SOURCES)),
        read_window=D.READ_WINDOW,
        read_note=D.READ_NOTE,
        sources=[dict(order=i + 1, **x) for i, x in enumerate(D.SOURCES)],
        fixtures=fixtures,
        markets=[dict(id=m["id"], sport=m["sport"], lambda_home=m["lambda_home"],
                      lambda_away=m["lambda_away"], total=m["total"],
                      groups=[dict(market=g["market"], selections=g["selections"]) for g in m["groups"]])
                 for m in markets],
        model_picks=summ["picks"],
        high_selections=HIGH,
        capped_in_band=capped,
        predictions=M.PREDICTIONS,
        coverage=cov,
        flags=M.FLAGS,
        repo_review=M.REPO_REVIEW,
        nhl_teams={k: dict(name=v[0], gp=v[1], w=v[2], l=v[3], otl=v[4], pts=v[5],
                           gf=v[6], ga=v[7], pp_pct=v[8]) for k, v in D.NHL_TEAMS.items()},
        nhl_skaters=D.NHL_SKATERS,
        recent_results=D.RECENT_RESULTS,
        euroleague=[dict(club=r[0], gp=r[1], w=r[2], l=r[3], pf=r[4], pa=r[5]) for r in D.EUROLEAGUE],
    )
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "desk.json").write_text(json.dumps(desk, indent=1), encoding="utf-8")

    # ---------------------------------------------------------------- index
    kpis = [("Listings", TOTAL, f"{len(official)} officially verified"),
            ("Priced fixtures", len(priced), f"{market_lines} market lines"),
            ("Priced selections", len(summ["selections"]), "probability + fair price"),
            ("High picks", len(HIGH), "strict window + evidence"),
            ("Predictions", len(M.PREDICTIONS), "≥30 words, unique"),
            ("Flags", len(M.FLAGS), "published for review"),
            ("Sources read", len(D.SOURCES), "URL + read window")]
    kpi_html = '<div class="grid kpis">' + "".join(
        f'<div class="card kpi"><div class="l">{e(l)}</div><div class="v">{v}</div>'
        f'<div class="n">{e(n)}</div></div>' for l, v, n in kpis) + "</div>"

    next_rows = []
    for f in sorted(priced, key=lambda x: x["start_utc"])[:8]:
        pk = next(p for p in summ["picks"] if p["fixture_id"] == f["id"])
        next_rows.append([
            e(start(f)), e(D.SPORT_NAME[f["sport"]]), e(f["competition"]),
            f'<a href="matches.html#{e(f["id"])}">{e(f["away_name"])} at {e(f["home_name"])}</a>',
            e(pk["selection"]), f'<span class="mono">{money(pk["p"])}</span>',
            f'{pk["p"]*100:.2f}%', f'<span class="badge {TIER_CLASS[pk["tier"]]}">{pk["tier"]}</span>',
        ])
    next_table = table(["Start (UTC)", "Sport", "Competition", "Fixture", "Model winner",
                        "Fair price", "Chance", "Tier"], next_rows, numeric=(5, 6))

    sport_cards = "".join(
        f'<a class="sportcard" href="sports/{s}.html"><b>{e(n)}</b>'
        f'<span>{c["listings"]} listings · {c["verified"]} verified · {c["priced"]} priced</span></a>'
        for (s, n), c in zip(D.SPORTS, cov))

    body = f"""<p class="eyebrow">Independent research desk · 22 October 2026</p>
<h1>Every match we could verify, priced by our own model.</h1>
<p class="lede">This desk reads official league feeds, originates its own two-way lines, and publishes a
High label only when a selection clears <strong>both</strong> rules in the brief: a model chance above 70%
<em>and</em> a fair price inside −250…+10000. {TOTAL} listings across the in-scope sports are shown;
{len(official)} are confirmed on an official source and {len(priced)} carry prices. Everything else is
blank on purpose.</p>
{kpi_html}
<div class="notice"><strong>Read this first.</strong> Soccer/football, American football, boxing, UFC/MMA,
hurling, horse racing, cycling and specials are out of scope and absent. Fourteen in-scope sports have no
officially verified fixture in this snapshot, eleven of them with no listing at all; each appears with the
reason it is missing, never as an empty slate.
<a href="flagged.html">See coverage and flags →</a></div>
<div class="grid two mt">
  <div class="card"><h2 style="margin-top:0">Next priced fixtures</h2>
    <p class="small muted">Model winner is the higher-probability side of our own money line. Prices are
    fair odds (1/p), with no margin and no bookmaker input.</p>
    {next_table}
    <p class="scrollnote"><a href="matches.html">All {TOTAL} listings →</a> ·
    <a href="markets.html">All {market_lines} market lines →</a></p>
  </div>
  <div>
    <div class="card"><h2 style="margin-top:0">The two High picks</h2>
      {''.join(f'<div class="pickcard" style="margin-bottom:12px"><h3><a href="high-confidence.html#{e(s["id"])}">{e(s["label"])}</a></h3>'
               f'<div class="meta"><span class="badge b-high">High</span>'
               f'<span>{s["p"]*100:.2f}% model chance</span><span>fair {money(s["p"])}</span>'
               f'<span>decimal {dec(s["p"])}</span></div>'
               f'<p class="small muted" style="margin:0">{e(by_id[s["id"].split(":")[0]]["away_name"])} at '
               f'{e(by_id[s["id"].split(":")[0]]["home_name"])} · {e(start(by_id[s["id"].split(":")[0]]))}</p></div>'
               for s in HIGH)}
      <p class="small"><a href="high-confidence.html">Why only two, and which five other selections fell in the window →</a></p>
    </div>
    <div class="card mt"><h2 style="margin-top:0">Verify it yourself</h2>
      <p class="small">Every fixture row links to the official page it was read from. {len(D.SOURCES)} official
      and discovery sources are listed with the exact URL and the session read window. Nothing is filled in from memory.</p>
      <p class="small"><a href="sources.html">Sources and read times →</a></p>
    </div>
  </div>
</div>
<h2>Coverage by sport</h2>
<p class="small muted">Status is about evidence, not about how many matches exist in the world.</p>
<div class="sportcards">{sport_cards}</div>
<h2>How a High pick is earned here</h2>
<div class="steps">
  <div class="step"><b>01 · Official fixture</b><p class="small">The game must be confirmed on the league's own
  feed with a venue and a UTC start — not on an aggregator.</p></div>
  <div class="step"><b>02 · Our own price</b><p class="small">Goals are modelled from official season rates;
  the fair price is 1/p with no margin. No copied bookmaker number.</p></div>
  <div class="step"><b>03 · Both rules</b><p class="small">Above 70% <em>and</em> fair price no shorter than
  −250. That intersection is only 1.43 points wide, which is why two picks survived.</p></div>
  <div class="step"><b>04 · Written case</b><p class="small">A unique ≥30-word prediction naming team, player,
  form and recent results — every claim tied to a page read this session.</p></div>
</div>
<div class="notice warn mt"><strong>Limits.</strong> The NHL model ignores goaltenders, injuries and rest.
The MLB model uses regular-season run rates and ignores starting pitchers. NBA and EuroLeague fixtures are
not priced. Read <a href="methodology.html">methodology</a> and <a href="flagged.html">the flag register</a>
before using any number here.</div>"""
    page("index.html", "Overview", "Official-source fixtures, our own lines and strict High-confidence gates for 22 October 2026.", body, "overview")

    # ---------------------------------------------------------------- matches
    rows = []
    for f in fixtures:
        if f["verification"] == "official":
            v = '<span class="badge b-ok">Official</span>'
            src = f'<a href="{e(f["official_url"])}" rel="noopener">{e(f["official_label"])}</a>'
            if f.get("priced"):
                pk = next(p for p in summ["picks"] if p["fixture_id"] == f["id"])
                pick_cell = e(pk["selection"])
                price_cell = f'<span class="mono">{money(pk["p"])}</span>'
                tier = f'<span class="badge {TIER_CLASS[pk["tier"]]}">{pk["tier"]}</span>'
            else:
                pick_cell = '<span class="tag">withheld</span>'
                price_cell = '<span class="tag">—</span>'
                tier = '<span class="badge b-gap">Not priced</span>'
        else:
            v = '<span class="badge b-gap">Discovery only</span>'
            src = '<span class="tag">no official page read</span>'
            pick_cell = '<span class="tag">withheld</span>'
            price_cell = '<span class="tag">—</span>'
            tier = '<span class="badge b-gap">Unverified</span>'
        rows.append([e(start(f)), e(D.SPORT_NAME[f["sport"]]), e(f["competition"]),
                     f'<span id="{e(f["id"])}"><strong>{e(f["away_name"])}</strong> at <strong>{e(f["home_name"])}</strong></span>',
                     e(f["venue"]) or '<span class="tag">—</span>', v, pick_cell, price_cell, tier, src])
    matches_table = table(["Start", "Sport", "Competition", "Fixture", "Venue", "Verification",
                           "Model winner", "Fair price", "Tier", "Official source"], rows, numeric=(7,))
    body = f"""<p class="eyebrow">Match list</p><h1>All {TOTAL} listings in the snapshot</h1>
<p class="lede">Confirmed fixtures come first from the official feeds. Discovery-only rows are events OLBG
carries that this session could not confirm on a governing body's own page; their price cells stay blank
and they are not counted as verified.</p>
<div class="notice">Official confirmation means the fixture, venue and start time were read from the league's
own feed. It does not confirm team selection, player availability or that the game will finish.</div>
{matches_table}
<h2>Notes on rows that look empty</h2>
<ul class="clean small">
<li><strong>NBA (2)</strong> — fixtures confirmed on nba.com, deliberately unpriced: one-game sample and no
default rating. See F-2988-02.</li>
<li><strong>EuroLeague (3), cricket (3), darts (3), tennis (15)</strong> — discovery only. The official pages
either render no fixture list (EuroLeague game centre, ATP current scores, PDC consent wall) or were not read
(cricket). See F-2988-03 to F-2988-05 and F-2988-11.</li>
<li><strong>Games 2-6 of the World Series</strong> are scheduled in advance and only played if the series
continues. See F-2988-09.</li></ul>"""
    page("matches.html", "Match list", "Every listing with its verification state and official source.", body, "matches")

    # ---------------------------------------------------------------- markets
    blocks = []
    for f in sorted(priced, key=lambda x: (x["sport"], x["start_utc"])):
        m = mkt[f["id"]]
        inner = []
        for g in m["groups"]:
            rows = [[e(s["label"]), f'{s["p"]*100:.2f}%', f'<span class="mono">{s["fair_decimal"]:.3f}</span>',
                     f'<span class="mono">{money(s["p"])}</span>',
                     f'<span class="badge {TIER_CLASS[s["tier"]]}">{s["tier"]}</span>',
                     f'<span class="tag">{e(s["tier_note"])}</span>'] for s in g["selections"]]
            inner.append(f'<h3 style="margin-top:14px">{e(g["market"])}</h3>'
                         + table(["Selection", "Chance", "Fair decimal", "Fair American", "Tier", "Note"],
                                 rows, numeric=(1, 2, 3)))
        caveat = ("Full-season run rates only: no starting pitchers, bullpen, park or postseason form. No MLB "
                  "selection can be High on this evidence." if f["sport"] == "baseball" else
                  "Club goals-for and goals-against per game only: no goaltender, injury, rest or home-ice adjustment.")
        blocks.append(f"""<details id="{e(f["id"])}"><summary><span>{e(f["away_name"])} at {e(f["home_name"])}
        <span class="tag"> · {e(f["competition"])} · {e(start(f))}</span></span>
        <span class="tag">λ {m["lambda_away"]:.2f} – {m["lambda_home"]:.2f} · total {m["total"]:.2f}</span></summary>
        <div class="body"><p class="small muted">{e(caveat)} <a href="{e(f["official_url"])}" rel="noopener">Official fixture</a></p>
        {''.join(inner)}</div></details>""")
    body = f"""<p class="eyebrow">Market explorer</p><h1>{market_lines} market lines, {len(summ["selections"])} prices</h1>
<p class="lede">Match winner, puck line / run line, match totals on several half-point rungs, team totals and
first-period totals where a period split is defensible. Every probability comes from the same goals model,
so the rows are internally consistent rather than copied from different books.</p>
<div class="notice">These are <strong>our</strong> fair prices, not offers. They contain no margin, no
bookmaker line and no claimed edge. A price being shorter than −250 does not make it a High pick.</div>
{''.join(blocks)}
<h2>Market coverage per fixture</h2>
<p class="small">NHL: money line including overtime, puck line ±1.5 both ways, four total rungs, eight team-total
rungs, two first-period totals. MLB: money line, run line ±1.5 and ±2.5 both ways, five total rungs, six
team-total rungs. Markets that need inputs we did not read — correct score, player props, series prices —
are not invented.</p>"""
    page("markets.html", "Markets", "Every originated market line with its probability and fair price.", body, "markets")

    # ---------------------------------------------------------------- high confidence
    cards = []
    for s in HIGH:
        f = by_id[s["id"].split(":")[0]]
        pred = next(p for p in M.PREDICTIONS if p["selection"] == s["id"])
        cards.append(f"""<div class="pickcard" id="{e(s["id"])}" style="margin:14px 0">
        <h3>{e(pred["selection_label"])}</h3>
        <div class="meta"><span class="badge b-high">High</span>
        <span>{s["p"]*100:.2f}% model chance · fair {money(s["p"])} · decimal {dec(s["p"])}</span>
        <span>{e(f["away_name"])} at {e(f["home_name"])} · {e(start(f))} · {e(f["venue"])}</span></div>
        <p class="prose">{e(pred["body"])}</p>
        <p class="small muted">{e(pred["model_note"])}</p>
        <p class="small"><a href="predictions.html#{e(pred["id"])}">Full write-up and evidence table →</a> ·
        <a href="{e(f["official_url"])}" rel="noopener">Official fixture source</a></p></div>""")
    capped_rows = []
    for s in capped:
        f = by_id[s["id"].split(":")[0]]
        capped_rows.append([e(f"{f['away_name']} at {f['home_name']}"), e(s["label"]),
                            f'{s["p"]*100:.2f}%', f'<span class="mono">{s["fair_decimal"]:.3f}</span>',
                            f'<span class="mono">{money(s["p"])}</span>',
                            "Inside the window, capped: no player-level or recent-result evidence was read for this selection."])
    body = f"""<p class="eyebrow">High-confidence picks</p><h1>Two selections earned the label</h1>
<p class="lede">A High pick has to satisfy both rules the brief sets: more than 70% and a fair price inside
−250…+10000. That intersection runs from 70.00% to 71.43%. {len(summ["above_70"])} of the
{len(summ["selections"])} prices clear 70%; {len(summ["in_band"])} land inside the window; {len(HIGH)} also
have the player, form and recent-result evidence needed for a written case.</p>
{''.join(cards)}
<h2>The five in-window selections that were capped</h2>
<p class="small muted">Each of these is inside the probability/price window. They stay at Medium because the
written case the brief requires — named players, verified current form and recent match history — could not be
completed from pages actually read in this session.</p>
{table(["Fixture", "Selection", "Chance", "Fair decimal", "Fair American", "Why it is not High"],
       capped_rows, numeric=(2, 3, 4))}
<h2>What the 70% rule does to the slate</h2>
<p class="small">The strongest money-line favourite on the slate is Minnesota at Calgary at 73.08%
(−271). It is excluded outright: at that probability the fair price is shorter than the −250 floor, so it
cannot be a High pick even though it is the most likely winner. That is the brief's rule applied literally,
and the same rule removes {len(summ["above_band"])} selections from consideration. The full arithmetic is on
the <a href="analysis.html">analysis page</a>.</p>"""
    page("high-confidence.html", "High confidence", "The two High picks and the in-window selections that were capped.", body, "high")

    # ---------------------------------------------------------------- predictions
    arts = []
    for p in M.PREDICTIONS:
        f = by_id[p["fixture"]]
        rows = [[e(t), f'<a href="{e(next(s["url"] for s in D.SOURCES if s["id"] == sid))}" rel="noopener">{e(sid)}</a>']
                for t, sid in p["facts"]]
        arts.append(f"""<article class="card" id="{e(p["id"])}" style="margin:16px 0">
        <p class="eyebrow">{e(p["id"])} · {e(f["competition"])} · {e(start(f))}</p>
        <h2 style="margin-top:0">{e(p["title"])}</h2>
        <div class="meta small muted" style="margin-bottom:10px"><span class="badge b-high">High</span>
        <span>{e(p["selection_label"])}</span></div>
        <div class="prose"><p>{e(p["body"])}</p></div>
        <p class="small muted">{e(p["model_note"])}</p>
        <h3>Claims checked against the pages read</h3>{table(["Claim", "Source id"], rows)}
        <p class="small"><a href="{e(f["official_url"])}" rel="noopener">Official fixture page</a> ·
        {e(len(p["body"].split()))} words</p></article>""")
    body = f"""<p class="eyebrow">Predictions</p><h1>Two written cases, no templates</h1>
<p class="lede">Each prediction is written for one selection, names the teams and the players involved,
states current form from official season totals, cites recent results that were actually read, and makes the
betting selection explicit. Nothing here is generated from a shared sentence pattern, and every numeric claim
is listed with the source it came from.</p>
{''.join(arts)}
<div class="notice"><strong>What these are not.</strong> They are not tips, stakes or guarantees. The model
price is an estimate; the fixture can still change, and an unverified late team-news item is not modelled.</div>"""
    page("predictions.html", "Predictions", "Two unique written cases with every claim tied to a source.", body, "predictions")

    # ---------------------------------------------------------------- analysis
    total_chance = sum(1 for s in summ["selections"] if s["p"] > 0.70)
    tiers = {t: sum(1 for s in summ["selections"] if s["tier"] == t) for t in ("High", "Medium", "Low")}
    sens_rows = []
    for key, fid, sel in ((None, "nhl-2026020155", "home_+1.5"), (None, "nhl-2026020156", "away_over_1.5")):
        m = mkt[fid]
        base_h, base_a = m["lambda_home"], m["lambda_away"]
        cells = []
        for factor in (0.90, 0.95, 1.00, 1.05, 1.10):
            p = D.two_way(base_h * factor, base_a * factor)[sel]
            cells.append(f"{p*100:.2f}%" + (' <span class="badge b-high">in</span>' if 0.70 < p <= 0.7142857
                                            else ' <span class="badge b-low">out</span>'))
        sens_rows.append([e(mkt[fid]["groups"][0]["selections"][0]["label"].split(" to ")[0] + " · " + sel),
                          e(fid)] + cells)
    scoring = sum(v[6] for v in D.NHL_TEAMS.values()) / sum(v[1] for v in D.NHL_TEAMS.values())
    body = f"""<p class="eyebrow">Analysis</p><h1>The window is 1.43 points wide</h1>
<p class="lede">The brief asks for selections that are both above 70% and priced between −250 and +10000.
Those two conditions overlap in a very small range, and that range — not a shortage of favourites — is what
limits the High tier.</p>
<div class="card"><h2 style="margin-top:0">The arithmetic, worked in full</h2>
<ul class="clean">
<li>A 70% chance has fair decimal <span class="mono">1/0.70 = 1.4286</span>, which is American
<span class="mono">−233.33</span>. Anything more likely is a shorter price than that.</li>
<li>The brief's floor of −250 is a decimal price of 1.40, which is a chance of
<span class="mono">1/1.40 = 71.4286%</span>.</li>
<li>So the only probabilities that satisfy both are <strong>70.00% &lt; p ≤ 71.4286%</strong> — a band
1.43 percentage points wide.</li>
<li>+10000 corresponds to 0.99%. No two-way match market on this slate reaches it, so the upper half of the
brief's range cannot bind for a selection that is also above 70%.</li>
</ul></div>
<h2>What happened to {len(summ["selections"])} prices</h2>
{table(["Measure", "Count", "Share"], [
    ["Priced selections", str(len(summ["selections"])), "100.00%"],
    ["Above 70%", str(total_chance), f'{total_chance/len(summ["selections"])*100:.1f}%'],
    ["Above 70% but price shorter than −250", str(len(summ["above_band"])), f'{len(summ["above_band"])/len(summ["selections"])*100:.1f}%'],
    ["Inside the 1.43-point window", str(len(summ["in_band"])), f'{len(summ["in_band"])/len(summ["selections"])*100:.2f}%'],
    ["Of those, labelled High", str(len(HIGH)), f'{len(HIGH)/len(summ["in_band"])*100:.1f}% of the window'],
], numeric=(1, 2))}
<h2>Confidence tiers across every priced selection</h2>
{table(["Tier", "Selections", "Rule applied"], [
    ["High", str(tiers["High"]), "inside the window and a complete written case exists"],
    ["Medium", str(tiers["Medium"]), "60-70%, or in the window but capped, or above the window"],
    ["Low", str(tiers["Low"]), "below 60%"],
], numeric=(1,))}
<h2>How fragile the two High picks are</h2>
<p class="small">If both expected-goal rates move together by 5%, does the pick stay in the window? This is a
sensitivity check on the model input, not a confidence interval.</p>
{table(["Selection", "Fixture", "−10%", "−5%", "as built", "+5%", "+10%"], sens_rows, numeric=(2, 3, 4, 5, 6))}
<p class="small muted">The check is deliberately blunt: it scales both teams' expected goals by the same
factor. A goaltender change or an injury to a top-six forward could move one side only, which this test does
not capture.</p>
<h2>League context</h2>
<p class="small">Across the 26 NHL clubs whose totals were read, the average is
<strong>{scoring:.2f} goals per team per game</strong>. A model line of 5.7 goals in a match is therefore
close to league average, and the totals rungs around 5.5 and 6.5 are where most of the close probabilities
land. The MLB model line is 8.75 runs, built from 162-game rates for both teams.</p>
<h2>Why the NBA and EuroLeague are not priced</h2>
<p class="small">The NBA has played one game per club. A model built on that sample would be a default rating
in disguise, which this repository's evidence rules forbid. EuroLeague has six or seven games per club — enough
for a record, not enough for this session to confirm the fixtures themselves, because the official game centre
rendered no schedule rows. Both are published as gaps with their official links intact.</p>"""
    page("analysis.html", "Analysis", "The band arithmetic, tier distribution and model sensitivity.", body, "analysis")

    # ---------------------------------------------------------------- flagged + coverage
    flag_rows = []
    for fl in M.FLAGS:
        links = " · ".join(f'<a href="{e(next(s["url"] for s in D.SOURCES if s["id"] == sid))}" rel="noopener">{e(sid)}</a>'
                           for sid in fl["sources"])
        sev = {"high": "b-gap", "medium": "b-med", "low": "b-low", "info": "b-ok"}[fl["severity"]]
        flag_rows.append([e(fl["id"]), f'<span class="badge {sev}">{e(fl["severity"].upper())}</span>',
                          f'<strong>{e(fl["title"])}</strong>', e(fl["detail"]), links])
    cov_rows = [[f'<a href="sports/{c["sport"]}.html">{e(c["name"])}</a>', e(c["status"]),
                 str(c["listings"]), str(c["verified"]), str(c["priced"]), str(c["high"]), e(c["note"])]
                for c in cov]
    body = f"""<p class="eyebrow">Flagged for review</p><h1>{len(M.FLAGS)} findings, and every sport accounted for</h1>
<p class="lede">Flagged items do not block publication — they are the parts a human should look at first.
Each carries the source it relates to. Unverified values are blank on every page; they are never filled in
to make a table look complete.</p>
{table(["Flag", "Severity", "Finding", "Detail", "Sources"], flag_rows)}
<h2 id="coverage">Coverage register</h2>
<p class="small muted">Verified means the fixture was read from a governing body's own page. Priced means the
desk published model lines for it. A gap is a statement about this session, not about the sport.</p>
{table(["Sport", "Status", "Listings", "Verified", "Priced", "High", "Note"], cov_rows, numeric=(2, 3, 4, 5))}
<div class="notice warn mt"><strong>The honest summary:</strong> two sports are properly covered, one is
partial, three are discovery-only and eleven are gaps. That is a snapshot of what {len(D.SOURCES)} reads
could establish in one session, not a claim of worldwide coverage.</div>"""
    page("flagged.html", "Coverage & flags", "The flag register and the per-sport coverage status.", body, "flags")

    # ---------------------------------------------------------------- sources
    src_rows = [[str(i + 1), e(s["id"]), f'<a href="{e(s["url"])}" rel="noopener">{e(s["publisher"])}</a>',
                 e(s["what"]), e(s["label"])] for i, s in enumerate(D.SOURCES)]
    body = f"""<p class="eyebrow">Sources</p><h1>{len(D.SOURCES)} pages read, with times</h1>
<p class="lede">Official league and governing-body feeds come first. OLBG pages are used only to discover
events, never to price them, and the PDC/ATP/URC reads are recorded precisely because they failed to give a
fixture list.</p>
<div class="notice"><strong>Read window: {e(D.READ_WINDOW)}.</strong> {e(D.READ_NOTE)} A page read inside
that window can change afterwards; treat each value as an observation, not as a live feed.</div>
{table(["#", "Id", "Publisher", "What was read", "Label"], src_rows, numeric=(0,))}
<h2>Verification method</h2>
<ul class="clean small">
<li>Fixtures: NHL schedule feed, MLB StatsAPI schedule, NBA schedule page. Venue and start time transcribed
per game; no timezone guessed.</li>
<li>Team strength: NHL club summary endpoint, MLB season splits per club. Values transcribed, not recalculated
from partial match lists.</li>
<li>Players: NHL skater summary, top three by points per club, used only where a High pick needed a player-level
fact.</li>
<li>Results: NHL scoreboard feed for 19 and 20 October, used verbatim in the two predictions.</li>
<li>Discovery-only: OLBG hubs. Their tip percentages are votes; they are not probabilities and were not used.</li>
</ul>"""
    page("sources.html", "Sources", "Every page read this session, with its URL and the session read window.", body, "sources")

    # ---------------------------------------------------------------- methodology
    body = f"""<p class="eyebrow">Methodology</p><h1>How the numbers were made</h1>
<p class="lede">One transparent model, one set of gates, and a rule that blank beats invented. Nothing on this
desk is copied from a bookmaker or from another session's files.</p>
<div class="card"><h2 style="margin-top:0">The model</h2>
<p class="small">Goals are independent Poisson variables.</p>
<blockquote><span class="mono">λ<sub>home</sub> = (home goals for/game + away goals against/game) / 2</span><br>
<span class="mono">λ<sub>away</sub> = (away goals for/game + home goals against/game) / 2</span></blockquote>
<p class="small mt">Every market is derived from the joint distribution of the two scores: money line (ties
split 50/50 for NHL overtime), puck or run line at ±1.5 and ±2.5, match totals on half-point rungs, team
totals, and a first-period total from λ/3. The fair decimal price is <span class="mono">1/p</span> with no
margin; the American price is derived from that probability, never from a bookmaker quote.</p></div>
<div class="card mt"><h2 style="margin-top:0">The gates</h2>
<ul class="clean">
<li><strong>Official fixture only.</strong> No price is published on an event that was not read from a
governing-body page.</li>
<li><strong>High needs both rules.</strong> p &gt; 70% and a fair price no shorter than −250, i.e.
70.00% &lt; p ≤ 71.4286%.</li>
<li><strong>High needs a written case.</strong> Named players, current form and recent results, each tied to a
page read this session, in a unique piece of at least 30 words.</li>
<li><strong>No defaults.</strong> An absent rating, an absent record or an absent fixture is left blank and
flagged, not filled with a league average.</li>
</ul></div>
<div class="card mt"><h2 style="margin-top:0">Known weaknesses</h2>
<ul class="clean">
<li>NHL: no goaltender, injury, rest, travel or home-ice term. Independent Poisson understates the effect of
team quality on totals and overstates the chance of a tie.</li>
<li>MLB: regular-season rates only; starting pitchers, bullpens, park and weather are excluded. Later World
Series games are conditional on the series continuing.</li>
<li>Basketball: no price published — the samples are too small for an honest rating.</li>
<li>Form: the NHL sample is 7-12 games per club, so a single hot or cold week moves the inputs noticeably.
The sensitivity table on the analysis page quantifies that.</li>
</ul></div>
<h2>Reproducibility</h2>
<p class="small">The data is generated by <span class="mono">scripts/s2988bd19_data.py</span> and
<span class="mono">scripts/s2988bd19_model.py</span>, written to
<span class="mono">data/2988bd19/desk.json</span>, and rendered by
<span class="mono">scripts/s2988bd19_build.py</span>. The validator
<span class="mono">scripts/s2988bd19_validate.py</span> re-derives every price from the published inputs and
fails the build if a link, a source or a High gate breaks.</p>"""
    page("methodology.html", "Methodology", "The Poisson model, the gates and the known weaknesses.", body, "method")

    # ---------------------------------------------------------------- repo review
    rev_rows = []
    for r in M.REPO_REVIEW:
        sev = {"high": "b-gap", "medium": "b-med", "low": "b-low", "info": "b-ok"}[r["severity"]]
        ev = []
        for part in r["evidence"].split(","):
            part = part.strip()
            if part.startswith("COORDINATION.md:"):
                lines = part.split(":", 1)[1]
                links = []
                for token in lines.split("-"):
                    if token.isdigit():
                        links.append(f'<a href="{REPO}/blob/main/COORDINATION.md#L{token}" rel="noopener">L{token}</a>')
                ev.append("COORDINATION.md " + " ".join(links) if links else e(part))
            else:
                ev.append(e(part))
        rev_rows.append([e(r["id"]), f'<span class="badge {sev}">{e(r["severity"].upper())}</span>',
                         f'<strong>{e(r["title"])}</strong>', e(r["detail"]), " · ".join(ev)])
    body = f"""<p class="eyebrow">Repository review</p><h1>Line-by-line check of the shared board</h1>
<p class="lede">Eight findings from reading the task board and running the repository's own gates. This desk
does not edit another session's files; irregularities are published with file:line evidence instead.</p>
{table(["Id", "Severity", "Finding", "Detail", "Evidence"], rev_rows)}
<h2>Gates run for this build</h2>
<ul class="clean small">
<li><span class="mono">python3 scripts/validate.py</span> — 134 primary fixtures, 126 H2H line books,
765 pages link-checked, <strong>0 errors</strong>, 3 pre-existing warnings in
<span class="mono">f7fa77fc/flagged.html</span>.</li>
<li><span class="mono">python3 -m pipeline.validate --site .</span> — canonical root, 0 errors.</li>
<li><span class="mono">python3 scripts/s2988bd19_validate.py</span> — this desk's own gate, including a
re-derivation of every price.</li>
</ul>
<div class="notice"><strong>Scope.</strong> This session edits only
<span class="mono">data/2988bd19/**</span>, <span class="mono">scripts/s2988bd19_*.py</span>,
<span class="mono">2988bd19/**</span>, <span class="mono">reports/SESSION_2988BD19.md</span> and append-only
<span class="mono">COORDINATION.md</span>. The task-board defects above are reported, not patched, because
that file is shared with live sessions.</div>"""
    page("repo-review.html", "Repository review", "Eight findings with file:line evidence, plus the gates run.", body, "review")

    # ---------------------------------------------------------------- sports pages
    sport_counts = {c["sport"]: c for c in cov}
    for slug, name in D.SPORTS:
        rows = []
        for f in fixtures:
            if f["sport"] != slug:
                continue
            if f["verification"] == "official":
                v = '<span class="badge b-ok">Official</span>'
                src = f'<a href="{e(f["official_url"])}" rel="noopener">{e(f["official_label"])}</a>'
                if f.get("priced"):
                    pk = next(p for p in summ["picks"] if p["fixture_id"] == f["id"])
                    pick = f'{e(pk["selection"])} · {money(pk["p"])} · {pk["p"]*100:.2f}%'
                    tier = f'<span class="badge {TIER_CLASS[pk["tier"]]}">{pk["tier"]}</span>'
                else:
                    pick, tier = '<span class="tag">withheld</span>', '<span class="badge b-gap">Not priced</span>'
            else:
                v = '<span class="badge b-gap">Discovery only</span>'
                src = '<span class="tag">no official page read</span>'
                pick, tier = '<span class="tag">withheld</span>', '<span class="badge b-gap">Unverified</span>'
            rows.append([e(start(f)), f'<strong>{e(f["away_name"])}</strong> at <strong>{e(f["home_name"])}</strong>',
                         e(f["competition"]), e(f["venue"]) or '<span class="tag">—</span>', v, pick, tier, src])
        c = sport_counts[slug]
        if rows:
            content = table(["Start", "Fixture", "Competition", "Venue", "Verification", "Model winner", "Tier", "Source"], rows)
        else:
            content = ('<div class="notice warn">No fixture for this sport was readable this session. Nothing is '
                       'listed rather than listing events that could not be verified.</div>')
        body = f"""<p class="eyebrow">Sport</p><h1>{e(name)}</h1>
<p class="lede">{e(c["note"])}</p>
<div class="grid kpis">
<div class="card kpi"><div class="l">Listings</div><div class="v">{c["listings"]}</div></div>
<div class="card kpi"><div class="l">Officially verified</div><div class="v">{c["verified"]}</div></div>
<div class="card kpi"><div class="l">Priced</div><div class="v">{c["priced"]}</div></div>
<div class="card kpi"><div class="l">High picks</div><div class="v">{c["high"]}</div></div>
</div>
<h2>Fixtures</h2>{content}
<p class="small mt"><a href="../matches.html">Back to the full match list</a> ·
<a href="../flagged.html#coverage">Coverage register</a></p>"""
        page(f"sports/{slug}.html", name, f"{name} coverage, fixtures and verification state.", body, "sports")

    # sports index
    cards = "".join(
        f'<a class="sportcard" href="{c["sport"]}.html"><b>{e(c["name"])}</b>'
        f'<span>{e(c["status"])} · {c["verified"]} verified · {c["priced"]} priced</span></a>' for c in cov)
    body = f"""<p class="eyebrow">Sport pages</p><h1>All 17 in-scope sports</h1>
<p class="lede">Every category the brief keeps in scope has a page, including the ones with no verified
fixture. A page with an empty table is a statement about this session's reads.</p>
<div class="sportcards">{cards}</div>
<h2>Excluded by the brief</h2>
<p class="small">Soccer/football, American football, boxing, UFC/MMA, hurling, horse racing, cycling and
specials. No fixture from those categories is imported, even where OLBG carries them.</p>"""
    page("sports/index.html", "Sports", "One page per in-scope sport, gaps included.", body, "sports")

    print("built", len(list(OUT.rglob('*.html'))), "pages")
    print("counts", COUNTS)


if __name__ == "__main__":
    main()
