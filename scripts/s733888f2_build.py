"""Build the 733888f2 desk: data mirrors + static HTML pages."""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import s733888f2_data as D          # noqa: E402
import s733888f2_model as M         # noqa: E402

OUT = ROOT / '733888f2'
DATA = ROOT / 'data' / '733888f2'

FLAGS = [
    ('F-01', 'Golf hub served no events', 'discovery',
     'https://www.olbg.com/betting-tips/Golf/5',
     'The Golf hub returned "No tips found" at 2026-10-24T22:29Z, so no golf market could be listed '
     'and no golf pick exists. Nothing is invented to fill the gap.'),
    ('F-02', 'Snooker hub served no events', 'discovery',
     'https://www.olbg.com/betting-tips/Snooker/8',
     'The Snooker hub returned "No tips found" at 2026-10-24T22:31Z.'),
    ('F-03', 'Motor Racing hub served no events', 'discovery',
     'https://www.olbg.com/betting-tips/Motor_Racing/14',
     'The Motor Racing hub returned "No tips found" although its page still prints the 2026 F1 calendar.'),
    ('F-04', 'Rugby League has outrights only', 'discovery',
     'https://www.olbg.com/betting-tips/Rugby_League/10',
     'The only Rugby League rows are State of Origin 2027, Super League 2027 and NRL 2027 outrights. '
     'There is no match market to price in the next 48 hours.'),
    ('F-05', 'OLBG lists completed darts matches as upcoming', 'upstream data defect',
     'https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/',
     'OLBG shows "Ross Smith v Luke Woodhouse" and "Price v Bunting" as tomorrow. The PDC schedule puts '
     'them in Saturday\'s second round, and PDC reports show Smith beat Heta 10-7 and Woodhouse beat van '
     'Veen 10-6; Price beat Menzies 10-4 and Bunting beat Huybrechts 10-3. Publishing a pick on either '
     'would be publishing on a played match, so both are excluded.'),
    ('F-06', 'Handball "most popular selection" is the draw', 'upstream data defect',
     'https://www.olbg.com/betting-tips/Handball/20',
     'On most handball fixtures OLBG highlights "Tie" as the most-tipped selection. That reflects tipster '
     'behaviour, not probability, and cannot be converted into a price.'),
    ('F-07', 'NHL listing prints one identical start time', 'upstream data defect',
     'https://www.olbg.com/betting-tips/Ice_Hockey/13',
     'All ten NHL games on the hub carry the same 19:07 start time and no timezone. The NHL feed shows '
     'five different start times between 19:00Z and 02:00Z the next day. This desk times every hockey row '
     'from the NHL feed and never from OLBG.'),
    ('F-08', 'NBA machine-readable data unreachable', 'access limitation',
     'https://www.nba.com/games',
     'nba.com/games served a calendar shell (8 games on 24 Oct, 7 on 25 Oct) with no matchup data and the '
     'message "Sorry, something went wrong". cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json '
     'returned HTTP 500 twice and stats.nba.com was unreachable. No official record was read, so all seven '
     'NBA games are listed without a price.'),
    ('F-09', 'SuperLega page body not retrievable', 'access limitation',
     'https://www.legavolley.it/2026/1a-giornata-and-18-10-2026-regular-season-superlega-stagione-2026-risultati-classifica/',
     'The official Lega Pallavolo page opened, but the retrieval layer returned only navigation chrome, so '
     'no standings value is published. The five Italian fixtures appear in the table without a price.'),
    ('F-10', 'Tennis draw confirmed but form not read', 'evidence gap',
     'https://www.atptour.com/en/news/djokovic-basel-2026-draw-preview',
     'The ATP report confirms Djokovic v Humbert and Wawrinka v Lehecka in Basel, and those two rows cite it. '
     'No ATP ranking or 2026 match record was read, so all tennis rows are listed without a price.'),
    ('F-11', 'Cricket: fixtures confirmed, form not read', 'evidence gap',
     'https://www.ecb.co.uk/news/4562387/pakistan-to-host-sri-lanka-and-england-in-odi-triseries',
     'Three tri-series fixtures carry an official date and venue from the ECB. No PCB scorecard, squad or '
     'toss was read, so no cricket price is published.'),
    ('F-12', 'Gaelic and greyhound inputs missing', 'evidence gap',
     'https://www.olbg.com/betting-tips/Gaelic_Football/25',
     'No GAA county board fixture page and no GBGB card was read, so none of the four Gaelic fixtures or the '
     'single Doncaster race carries a price.'),
    ('F-13', 'Zero band-qualifying High picks, and why', 'arithmetic disclosure',
     'https://www.olbg.com/betting-tips',
     'A fair price of -250 is 71.43%. Requiring both "more than 70%" and "inside -250 to +10000" leaves a '
     'window from 70.00% to 71.43%. Six of this desk\'s seven picks sit outside it: five below 70%, and the two '
     'strongest (Minnesota at 72.5%, Saracens at 82.1%) above the ceiling. Both are published as "Strong, '
     'outside the requested band" rather than being relabelled High.'),
    ('F-14', 'No injury document was read', 'evidence gap',
     'https://www.nhl.com',
     'No NHL, MLB or Premiership Rugby injury/availability report was read this session. The rugby row uses '
     'the two named 23s because both clubs published them; no player is described as injured anywhere on '
     'this site.'),
    ('F-15', 'Repository publishes a fraction of its desks', 'repo finding',
     'https://github.com/buffedlizard55-lab/OLBG1/blob/main/pipeline/build.py',
     'The repository holds 75 top-level desks with an index.html, but the canonical publisher registers 16 '
     'of them in ARCHIVE. The other 59 are reachable in git and in the repository tree but not on the live '
     'site.'),
    ('F-16', 'Root README no longer matches the tree', 'repo finding',
     'https://github.com/buffedlizard55-lab/OLBG1/blob/main/README.md',
     'README.md describes "one dashboard, nine top-level pages and fifteen sport pages" and a 25-page '
     'artifact, while the checkout holds 1,856 HTML files and 89 top-level directories.'),
    ('F-17', 'Session desks have fragmented the tree', 'repo finding',
     'https://github.com/buffedlizard55-lab/OLBG1',
     '89 top-level directories and 97 data directories, one set per session, with no shared index of which '
     'desk supersedes which. This desk is namespaced under 733888f2/ for that reason and adds one archive line.'),
    ('F-18', 'OLBG clock is not a timezone we can assert', 'discovery caveat',
     'https://www.olbg.com/betting-tips/Tennis/3',
     'OLBG prints event times on a geo-adjusted clock ("Today", "Tomorrow"), with no timezone label. Every '
     'time taken from OLBG is reproduced as displayed and is never converted or asserted as UTC.'),
]

# --------------------------------------------------------------------------
# Predictions: one per priced pick. Every number traces to the row's facts.
# --------------------------------------------------------------------------
PREDICTIONS = {
    'NHL-1': (
        'Florida Panthers moneyline. The Panthers arrive at the United Center at 5-4-2, with Brady Tkachuk '
        'already on seven goals, Matthew Tkachuk on twelve assists and Jacob Markstrom on three wins. '
        'Chicago\'s 3-7-0 start has produced three goals from its leading scorer, Roman Kantserov, so the '
        'visitors\' top-line output looks the likelier source of the decisive goal.'),
    'NHL-2': (
        'Dallas Stars moneyline. Both clubs have played ten games; Dallas are 6-3-1 and the Islanders 5-3-2, '
        'and Dallas hold the better points rate on home ice. Mikko Rantanen\'s five goals and Jason '
        'Robertson\'s eight assists give the Stars two separate scoring routes in front of Jake Oettinger, '
        'who already has five wins, while New York lean on Ilya Sorokin\'s five wins and Bo Horvat\'s five goals.'),
    'NHL-3': (
        'Montreal Canadiens moneyline in the Heritage Classic. The NHL lists this as a neutral-site game at '
        'Princess Auto Stadium, which takes Winnipeg\'s home advantage out of the equation. Montreal are 5-3-2 '
        'with Cole Caufield on six goals and Nick Suzuki on seven assists; Winnipeg are 4-3-3, so the edge '
        'belongs to the Canadiens\' slightly better points rate rather than to the venue.'),
    'NHL-4': (
        'Colorado Avalanche moneyline. Colorado are 6-4-1 against Nashville\'s 3-3-3, and the Avalanche carry '
        'the stronger scoring profile into Bridgestone Arena: Artturi Lehkonen has nine goals, Nathan '
        'MacKinnon thirteen assists and Mackenzie Blackwood five wins. Juuse Saros has three wins and Roman '
        'Josi eight assists for Nashville, but the Predators have won only three of their nine games.'),
    'NHL-5': (
        'Minnesota Wild moneyline. This is the widest record gap on the two-day slate: Minnesota are 6-3-2 '
        'with Kirill Kaprizov on eleven goals, Quinn Hughes on eleven assists and Jesper Wallstedt on six '
        'wins, while Vancouver are 2-9-1 and their leading scorer has four goals. Record, goaltending wins '
        'and top-line production all point the same way, which is why the price is short rather than generous.'),
    'MLB-1': (
        'Milwaukee Brewers moneyline. The Brewers finished the regular season 103-59 and lead this best-of-seven '
        'World Series 1-0 after game one. Logan Henderson is the home probable pitcher against Tampa Bay\'s '
        'Drew Rasmussen, and the Rays\' 98-64 season was six wins lighter. Home field and the stronger season '
        'record make Milwaukee the side to take at American Family Field.'),
    'RU-1': (
        'Saracens to win at the Twickenham Stoop. The official Gallagher PREM table has Saracens on 11 points '
        'from three rounds with a +21 points difference and a W-L-W sequence, against Harlequins\' 2 points, '
        '-68 and three defeats. Saracens also start Fergus Burke at fly-half behind a pack captained by Maro '
        'Itoje; Harlequins have won the last two meetings at The Stoop, but the current table points one way.'),
}


def e(x):
    return html.escape(str(x), quote=True)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


CSS = """
:root{--ink:#101c2c;--muted:#5a6b80;--line:#e2e8f0;--bg:#f7f9fc;--card:#fff;
--blue:#1d4ed8;--blue-soft:#e8efff;--green:#0f6b45;--green-soft:#e6f4ec;
--amber:#8a5a00;--amber-soft:#fdf3df;--red:#8e2f2f;--red-soft:#fbeaea;--grey-soft:#eef2f7}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
header{background:var(--ink);color:#fff}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:16px;padding-top:12px;padding-bottom:12px}
.brand{font-weight:700;font-size:17px;color:#fff}
.brand span{color:#9db4d8;font-weight:400;font-size:13px;display:block}
nav{display:flex;flex-wrap:wrap;gap:4px;margin-left:auto}
nav a{color:#d7e2f3;padding:6px 10px;border-radius:8px;font-size:14px}
nav a:hover{background:#22314a;text-decoration:none}
nav a.on{background:#2f4160}
main{padding:28px 0 56px}
h1{font-size:30px;line-height:1.2;margin:0 0 6px}
h2{font-size:21px;margin:34px 0 10px}
h3{font-size:17px;margin:22px 0 8px}
p.lede{font-size:17px;color:var(--muted);margin:0 0 18px;max-width:78ch}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));margin:16px 0}
.kpi{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.kpi b{display:block;font-size:26px;line-height:1.1}
.kpi span{color:var(--muted);font-size:13px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:9px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--grey-soft);font-size:12.5px;text-transform:uppercase;letter-spacing:.03em;color:#41536b}
tbody tr:hover{background:#fbfdff}
.table-wrap{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:12px}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.high{background:var(--green-soft);color:var(--green)}
.strong{background:var(--blue-soft);color:var(--blue)}
.medium{background:var(--amber-soft);color:var(--amber)}
.low{background:var(--grey-soft);color:#41536b}
.gap{background:var(--red-soft);color:var(--red)}
.pick{font-weight:700}
.muted{color:var(--muted)}
.small{font-size:13px}
.small a{word-break:break-all}
ul.plain{padding-left:18px;margin:8px 0}
ul.plain li{margin:4px 0}
.note{background:var(--amber-soft);border:1px solid #f0d9a8;color:#6b4600;border-radius:10px;padding:12px 14px;margin:14px 0}
.ok{background:var(--green-soft);border:1px solid #b9e0cb;color:#0b4f33;border-radius:10px;padding:12px 14px;margin:14px 0}
.pred{background:#fff;border:1px solid var(--line);border-left:4px solid var(--blue);border-radius:10px;padding:14px 16px;margin:12px 0}
.pred h4{margin:0 0 6px;font-size:15px}
.pred p{margin:0 0 8px}
footer{border-top:1px solid var(--line);color:var(--muted);font-size:13px;padding:22px 0}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;font-size:13px}
"""


def nav(active, base=''):
    items = [('index.html', 'Summary'), ('picks.html', 'Picks'), ('predictions.html', 'Write-ups'),
             ('matches.html', 'Matches'), ('markets.html', 'Markets'), ('sports.html', 'Sports'),
             ('flag.html' if False else 'flagged.html', 'Flagged'), ('sources.html', 'Sources'),
             ('methodology.html', 'Method'), ('repo-audit.html', 'Repo audit'),
             ('reverse-engineering.html', 'OLBG'), ('archive.html', 'All desks')]
    out = []
    for href, label in items:
        cls = ' class="on"' if href == active else ''
        out.append(f'<a href="{base}{href}"{cls}>{e(label)}</a>')
    return '<nav>' + ''.join(out) + '</nav>'


def page(title, active, body, sub='', base=''):
    head = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)}</title><style>{CSS}</style></head><body>')
    hdr = ('<header><div class="wrap"><div class="brand">OLBG research desk'
           '<span>15-sport desk &middot; captured 2026-10-24</span></div>'
           + nav(active, base) + '</div></header>')
    subline = f'<p class="lede">{sub}</p>' if sub else ''
    foot = ('<footer><div class="wrap">Independent research. Not affiliated with OLBG. '
            'Prices on this site are this desk\'s own margin-free estimates, not quotes from any '
            'bookmaker. No staking advice. Every published number carries a link to the official '
            'page it came from.</div></footer></body></html>')
    return head + hdr + '<main><div class="wrap">' + subline + body + '</div></main>' + foot


def src_link(sid, text=None):
    s = D.SOURCE_INDEX[sid]
    return f'<a href="{e(s["url"])}">{e(text or s["publisher"])}</a>'


def money(am):
    if am is None:
        return '&mdash;'
    return ('+' + str(int(am))) if am > 0 else str(int(am))


def build_data():
    """Attach prices to priced matches and assemble the JSON mirrors."""
    rows = []
    for match in D.MATCHES:
        card = M.price_match(match)
        if card is None:
            continue
        row = dict(match)
        row.update({'price': card, 'prediction': PREDICTIONS.get(match['id'], '')})
        rows.append(row)
    return rows


def coverage(rows):
    cov = []
    for slug_, name, _, _ in D.SPORTS:
        listed = [u for u in D.UNPRICED if u['sport'] == slug_]
        priced = [r for r in rows if r['sport'] == slug_]
        picks = len(priced)
        high = len([r for r in priced if r['price']['pick']['tier'] == 'High'])
        strong = len([r for r in priced if r['price']['pick']['tier'] == 'Strong'])
        if picks:
            status = ('<span class="badge high">Priced</span>')
        elif listed:
            status = '<span class="badge medium">Listed, not priced</span>'
        else:
            status = '<span class="badge gap">No market on OLBG</span>'
        cov.append({'slug': slug_, 'name': name, 'listed': len(listed), 'priced': len(priced),
                    'picks': picks, 'high': high, 'strong': strong, 'status': status,
                    'olbg': D.olbg_url(slug_)})
    return cov


def index_html(rows, cov):
    picks = sorted([r['price']['pick'] | {'match': r} for r in rows],
                   key=lambda p: -p['p'])
    kpis = [('Priced matches', len(rows)), ('Picks', len(picks)),
            ('High (in band)', sum(1 for p in picks if p['tier'] == 'High')),
            ('Strong (outside band)', sum(1 for p in picks if p['tier'] == 'Strong')),
            ('Sports with a price', len({r['sport'] for r in rows})),
            ('OLBG events listed', len(D.UNPRICED) + len(rows)),
            ('Flagged items', len(FLAGS))]
    b = ['<h1>Today\'s picks, in one place</h1>',
         '<p class="lede">Captured 24 October 2026, 23:15 UTC. Every pick below is on a match that '
         'had not started when the official schedule was read. Each price is originated here from the '
         'official records linked on the row; nothing is copied from a bookmaker or from OLBG tip shares.</p>',
         '<div class="grid">']
    for label, val in kpis:
        b.append(f'<div class="kpi"><b>{val}</b><span>{e(label)}</span></div>')
    b.append('</div>')

    b.append('<h2>Executive summary</h2>')
    strong = [p for p in picks if p['tier'] in ('High', 'Strong')]
    if strong:
        names = '; '.join(f'{e(p["selection"])} ({money(p["american"])})' for p in strong)
        n_high = len([p for p in strong if p['tier'] == 'High'])
        n_str = len([p for p in strong if p['tier'] == 'Strong'])
        if n_high:
            tail = (f'{n_high} of them are High: probability above 70% and a fair price inside the '
                    f'-250 to +10000 band. The other {n_str} are above the band\'s ceiling and are '
                    f'labelled Strong (see F-13).')
        else:
            tail = (f'Both sit above the -250 ceiling of the requested price band, where a fair price of '
                    f'-250 already means 71.43%, so neither can be labelled High under the brief\'s own '
                    f'rule. They are published as Strong and the arithmetic is disclosed as F-13.') if n_str == 2 else (
                    f'All {n_str} sit above the -250 ceiling (71.43%), so they are labelled Strong and the '
                    f'arithmetic is disclosed as F-13.')
        b.append(f'<div class="ok"><b>Highest-confidence selections:</b> {names}. {tail}</div>')
    b.append(f'<div class="note"><b>Where the picks are:</b> the table immediately below is the whole '
             f'list. <a href="picks.html">Picks</a> repeats it with the market detail, '
             f'<a href="predictions.html">Write-ups</a> holds one written analysis per pick, and '
             f'<a href="matches.html">Matches</a> shows every fixture including the ones we could not price. '
             f'{len(D.UNPRICED)} OLBG listings across 12 sports have no price because no official input was '
             f'read; they are shown as blanks, never guessed.</div>')

    b.append('<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Match (start, UTC)</th>'
             '<th>Selection</th><th class="num">Fair price</th><th class="num">Probability</th>'
             '<th>Confidence</th><th>Official source</th></tr></thead><tbody>')
    for p in picks:
        r = p['match']
        b.append(
            f'<tr><td>{e(D.SPORT_NAME[r["sport"]])}</td>'
            f'<td><b>{e(r["away"])} @ {e(r["home"])}</b><br><span class="small muted">{e(r["start_label"])}'
            f' &middot; {e(r["comp"])}</span></td>'
            f'<td class="pick">{e(p["selection"])} ML</td>'
            f'<td class="num">{money(p["american"])}</td>'
            f'<td class="num">{p["implied_pct"]}%</td>'
            f'<td><span class="badge {p["tier"].lower()}">{e(p["tier"])}</span></td>'
            f'<td class="small"><a href="{e(r["official"])}">official</a></td></tr>')
    b.append('</tbody></table></div>')

    b.append('<h2>Coverage across the 15 requested sports</h2>')
    b.append('<div class="table-wrap"><table><thead><tr><th>Sport</th><th class="num">Listed on OLBG</th>'
             '<th class="num">Priced here</th><th class="num">High</th><th class="num">Strong</th>'
             '<th>Status</th><th>OLBG hub</th></tr></thead><tbody>')
    for c in cov:
        b.append(f'<tr><td><a href="sports/{c["slug"]}.html">{e(c["name"])}</a></td>'
                 f'<td class="num">{c["listed"]}</td><td class="num">{c["priced"]}</td>'
                 f'<td class="num">{c["high"]}</td><td class="num">{c["strong"]}</td>'
                 f'<td>{c["status"]}</td>'
                 f'<td class="small"><a href="{e(c["olbg"])}">hub</a></td></tr>')
    b.append('</tbody></table></div>')
    b.append('<p class="small muted">The brief asks for five to ten picks per sport. Two sports carry '
             'prices tonight, plus one rugby match; twelve do not. The shortfall is the finding, not an '
             'oversight: <a href="flagged.html">Flagged for review</a> names, sport by sport, the exact '
             'official input that was missing.</p>')
    return page("Today's picks — 24 October 2026", 'index.html', ''.join(b))


def picks_html(rows):
    b = ['<h1>Picks</h1>',
         '<p class="lede">One pick per priced match, always the stronger side on our own fair line. '
         'The tier is a function of the originated probability and the requested price band only.</p>',
         '<div class="table-wrap"><table><thead><tr><th>#</th><th>Match</th><th>Selection</th>'
         '<th class="num">Fair decimal</th><th class="num">Fair American</th><th class="num">Prob.</th>'
         '<th>Tier</th><th>In -250..+10000?</th><th>Source</th></tr></thead><tbody>']
    for i, r in enumerate(rows, 1):
        p = r['price']['pick']
        b.append(f'<tr><td class="num">{i}</td>'
                 f'<td><b>{e(r["away"])} @ {e(r["home"])}</b><br><span class="small muted">{e(D.SPORT_NAME[r["sport"]])}'
                 f' &middot; {e(r["start_label"])}</span></td>'
                 f'<td class="pick">{e(p["selection"])} ML</td>'
                 f'<td class="num">{p["decimal"]:.3f}</td><td class="num">{money(p["american"])}</td>'
                 f'<td class="num">{p["implied_pct"]}%</td>'
                 f'<td><span class="badge {p["tier"].lower()}">{e(p["tier"])}</span></td>'
                 f'<td>{"yes" if p["in_band"] else "no"}</td>'
                 f'<td class="small"><a href="{e(r["official"])}">official</a></td></tr>')
    b.append('</tbody></table></div>')
    b.append('<h2>Markets we investigated and could not price</h2>')
    b.append('<p class="lede">Published so the gaps are visible rather than hidden.</p>')
    b.append('<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Market</th><th>Why no number</th>'
             '</tr></thead><tbody>')
    gaps = [
        ('Ice Hockey', 'Match total (goals)', 'No official team goals-for/against totals were read for the ten clubs.'),
        ('Ice Hockey', 'Team total', 'Same missing input; also no period-split scoring data.'),
        ('Ice Hockey', 'Player shots/props', 'No official player game logs or confirmed lineups.'),
        ('Baseball', 'Game total (runs)', 'No official park/run environment or season runs data read.'),
        ('Baseball', 'Run line -1.5', 'Only the moneyline is published; the run line needs a measured margin distribution.'),
        ('Baseball', 'Player props', 'No confirmed starting line-ups beyond the two probable pitchers.'),
        ('Rugby Union', 'Match total (points)', 'Official standings gave points difference only, not points for/against.'),
        ('Rugby Union', 'First try scorer', 'No confirmed 23-man availability document for either side beyond the named squads.'),
        ('All other sports', 'Winner, handicap, total', 'No official form input was read; see Flagged for review.'),
    ]
    for s, mk, why in gaps:
        b.append(f'<tr><td>{e(s)}</td><td>{e(mk)}</td><td>{e(why)}</td></tr>')
    b.append('</tbody></table></div>')
    return page('Picks', 'picks.html', ''.join(b))


def predictions_html(rows):
    b = ['<h1>Written predictions</h1>',
         '<p class="lede">One hand-written analysis per pick: the selection first, then the team, its '
         'record, the current form and the named statistical leaders, each traceable to the official '
         'page linked under the heading.</p>']
    for r in rows:
        p = r['price']['pick']
        b.append(f'<div class="pred" id="{e(r["id"])}">'
                 f'<h4>{e(p["selection"])} &mdash; {e(r["away"])} @ {e(r["home"])} '
                 f'<span class="badge {p["tier"].lower()}">{e(p["tier"])}</span></h4>'
                 f'<p>{e(r["prediction"])}</p>'
                 f'<p class="small muted">{e(r["comp"])} &middot; {e(r["start_label"])} &middot; '
                 f'{e(r["venue"])} &middot; fair price {money(p["american"])} ({p["implied_pct"]}%) &middot; '
                 f'<a href="{e(r["official"])}">official match page</a></p>'
                 f'<ul class="plain small">')
        for f in r['facts']:
            b.append(f'<li>{e(f)}</li>')
        b.append('</ul></div>')
    b.append('<div class="note"><b>On injuries:</b> no official injury or availability report was read '
             'for these fixtures, so no injury claim is made. The rugby row uses only the two squads the '
             'clubs published. This is recorded as F-14.</div>')
    return page('Written predictions', 'predictions.html', ''.join(b))


def matches_html(rows, cov):
    b = ['<h1>Every match</h1>',
         '<p class="lede">Priced matches first, then every other event OLBG listed, grouped by sport. '
         'A blank price always has a reason next to it.</p>',
         '<h2>Priced matches</h2>',
         '<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Match</th><th>Start (UTC)</th>'
         '<th>Venue</th><th>Official inputs</th><th>Source</th></tr></thead><tbody>']
    for r in rows:
        ins = '; '.join(f'{e(k)}: {e(v if not isinstance(v, dict) else ", ".join(f"{a} {b}" for a, b in v.items()))}'
                        for k, v in r['inputs'].items())
        b.append(f'<tr><td>{e(D.SPORT_NAME[r["sport"]])}</td>'
                 f'<td><b>{e(r["away"])} @ {e(r["home"])}</b><br><span class="small muted">{e(r["comp"])}</span></td>'
                 f'<td class="small">{e(r["start_label"])}</td><td class="small">{e(r["venue"])}</td>'
                 f'<td class="small">{ins}</td>'
                 f'<td class="small"><a href="{e(r["official"])}">official</a></td></tr>')
    b.append('</tbody></table></div>')
    b.append('<h2>Listed on OLBG, not priced</h2>')
    for c in cov:
        items = [u for u in D.UNPRICED if u['sport'] == c['slug']]
        if not items and c['priced'] == 0:
            b.append(f'<h3>{e(c["name"])}</h3><p class="small muted">No event rows were served by the '
                     f'hub at read time. <a href="{e(c["olbg"])}">OLBG hub</a></p>')
            continue
        if not items:
            continue
        b.append(f'<h3>{e(c["name"])} <span class="small muted">({len(items)})</span></h3>')
        b.append('<div class="table-wrap"><table><thead><tr><th>Competition</th><th>Event</th>'
                 '<th>OLBG listing</th><th>Why no price</th><th>Source</th></tr></thead><tbody>')
        for it in items:
            b.append(f'<tr><td class="small">{e(it["comp"])}</td><td><b>{e(it["event"])}</b></td>'
                     f'<td class="small">{e(it["when"])}</td><td class="small">{e(it["reason"])}</td>'
                     f'<td class="small"><a href="{e(it["olbg"])}">source</a></td></tr>')
        b.append('</tbody></table></div>')
    return page('Every match', 'matches.html', ''.join(b))


def markets_html(rows):
    b = ['<h1>Markets</h1>',
         '<p class="lede">For each priced match: the two-way winner market at zero margin, the even-money '
         'handicap derived from it, and the markets withheld with the missing input named.</p>']
    for r in rows:
        pr = r['price']
        w, h = pr['market_winner'], pr['market_handicap']
        b.append(f'<div class="card"><h3 style="margin-top:0">{e(r["away"])} @ {e(r["home"])}</h3>'
                 f'<p class="small muted">{e(D.SPORT_NAME[r["sport"]])} &middot; {e(r["comp"])} &middot; '
                 f'{e(r["start_label"])} &middot; <a href="{e(r["official"])}">official match page</a></p>'
                 '<div class="table-wrap"><table><thead><tr><th>Market</th><th>Selection</th>'
                 '<th class="num">Fair decimal</th><th class="num">Fair American</th>'
                 '<th class="num">Probability</th></tr></thead><tbody>')
        for side, label in (('home', r['home']), ('away', r['away'])):
            b.append(f'<tr><td>Match winner (2-way, no margin)</td><td>{e(label)}</td>'
                     f'<td class="num">{w[side]["decimal"]:.3f}</td>'
                     f'<td class="num">{money(w[side]["american"])}</td>'
                     f'<td class="num">{w[side]["p"]*100:.1f}%</td></tr>')
        b.append(f'<tr><td>Handicap, even money (structural estimate, sigma {h["sigma"]})</td>'
                 f'<td>{e(r["home"])} {h["line"]:+.1f}</td>'
                 f'<td class="num">{1/h["p_home_covers"]:.3f}</td>'
                 f'<td class="num">{money(h["home_american"])}</td>'
                 f'<td class="num">{h["p_home_covers"]*100:.1f}%</td></tr>')
        b.append(f'<tr><td>Handicap, even money (structural estimate, sigma {h["sigma"]})</td>'
                 f'<td>{e(r["away"])} {-h["line"]:+.1f}</td>'
                 f'<td class="num">{1/(1-h["p_home_covers"]):.3f}</td>'
                 f'<td class="num">{money(h["away_american"])}</td>'
                 f'<td class="num">{(1-h["p_home_covers"])*100:.1f}%</td></tr>')
        b.append('</tbody></table></div>'
                 '<p class="small muted">Two-way book sums to 100.0%. The handicap line is derived, not '
                 'observed: it assumes a normal margin distribution with the sigma shown. No total or '
                 'player market is published for this match because the official scoring input for it '
                 'was not read.</p></div>')
    return page('Markets', 'markets.html', ''.join(b))


def sport_pages(rows, cov):
    pages = {}
    for c in cov:
        slug_ = c['slug']
        priced = [r for r in rows if r['sport'] == slug_]
        listed = [u for u in D.UNPRICED if u['sport'] == slug_]
        b = [f'<h1>{e(c["name"])}</h1>',
             f'<p class="lede">{len(priced)} priced match(es), {len(listed)} OLBG listing(s) without a price. '
             f'<a href="{e(c["olbg"])}">OLBG hub</a></p>']
        if priced:
            b.append('<div class="table-wrap"><table><thead><tr><th>Match</th><th>Selection</th>'
                     '<th class="num">Fair price</th><th class="num">Prob.</th><th>Tier</th>'
                     '<th>Source</th></tr></thead><tbody>')
            for r in priced:
                p = r['price']['pick']
                b.append(f'<tr><td><b>{e(r["away"])} @ {e(r["home"])}</b><br>'
                         f'<span class="small muted">{e(r["start_label"])}</span></td>'
                         f'<td class="pick">{e(p["selection"])} ML</td>'
                         f'<td class="num">{money(p["american"])}</td><td class="num">{p["implied_pct"]}%</td>'
                         f'<td><span class="badge {p["tier"].lower()}">{e(p["tier"])}</span></td>'
                         f'<td class="small"><a href="{e(r["official"])}">official</a></td></tr>')
            b.append('</tbody></table></div>')
        if listed:
            b.append('<h3>Listed, not priced</h3><div class="table-wrap"><table><thead><tr>'
                     '<th>Competition</th><th>Event</th><th>OLBG listing</th><th>Why no price</th>'
                     '</tr></thead><tbody>')
            for it in listed:
                b.append(f'<tr><td class="small">{e(it["comp"])}</td><td>{e(it["event"])}</td>'
                         f'<td class="small">{e(it["when"])}</td><td class="small">{e(it["reason"])}</td></tr>')
            b.append('</tbody></table></div>')
        if not priced and not listed:
            b.append('<div class="note">The OLBG hub served no event rows for this sport at '
                     '2026-10-24T22:29-22:44Z. There is nothing to price and nothing is invented to fill '
                     'the page.</div>')
        pages[slug_] = page(f'{c["name"]} — matches and picks', 'sports.html', ''.join(b), base='../')
    return pages


def flagged_html():
    b = ['<h1>Flagged for review</h1>',
         '<p class="lede">Eighteen items: upstream OLBG defects, access limits, evidence gaps and repo '
         'findings. Each carries the source that shows it. None of them blocks publication, and every one '
         'is a place where a number is missing rather than guessed.</p>',
         '<div class="table-wrap"><table><thead><tr><th>#</th><th>Item</th><th>Type</th>'
         '<th>What we saw</th><th>Source</th></tr></thead><tbody>']
    for fid, title, kind, url, detail in FLAGS:
        b.append(f'<tr><td class="num">{e(fid)}</td><td><b>{e(title)}</b></td>'
                 f'<td class="small">{e(kind)}</td><td class="small">{e(detail)}</td>'
                 f'<td class="small"><a href="{e(url)}">link</a></td></tr>')
    b.append('</tbody></table></div>')
    return page('Flagged for review', 'flagged.html', ''.join(b))


def sources_html():
    facts = [s for s in D.SOURCES if s['role'] == 'fact']
    disc = [s for s in D.SOURCES if s['role'] == 'discovery']
    b = ['<h1>Sources</h1>',
         f'<p class="lede">{len(facts)} official pages were read for facts and {len(disc)} OLBG pages '
         'were read for discovery only. Discovery pages never supply a number.</p>',
         '<h2>Official sources used for facts</h2>',
         '<div class="table-wrap"><table><thead><tr><th>Publisher</th><th>URL</th><th>Read (UTC)</th>'
         '<th>What it gave us</th></tr></thead><tbody>']
    for s in facts:
        b.append(f'<tr><td>{e(s["publisher"])}</td><td class="small"><a href="{e(s["url"])}">{e(s["url"])}</a></td>'
                 f'<td class="small">{e(s["read_utc"])}</td><td class="small">{e(s["what"])}</td></tr>')
    b.append('</tbody></table></div><h2>OLBG pages read for discovery</h2>'
             '<div class="table-wrap"><table><thead><tr><th>URL</th><th>Read (UTC)</th><th>What it gave us</th>'
             '</tr></thead><tbody>')
    for s in disc:
        b.append(f'<tr><td class="small"><a href="{e(s["url"])}">{e(s["url"])}</a></td>'
                 f'<td class="small">{e(s["read_utc"])}</td><td class="small">{e(s["what"])}</td></tr>')
    b.append('</tbody></table></div>')
    return page('Sources', 'sources.html', ''.join(b))


def methodology_html(rows):
    b = ['<h1>How this desk works</h1>',
         '<h2>The line-origination method</h2>',
         '<p>Prices are this desk\'s own estimates, converted to a margin-free two-way book '
         '(<code>decimal = 1 / p</code>). The formulas are fixed in advance and applied identically to '
         'every row:</p>',
         '<ul class="plain">'
         '<li><b>Hockey:</b> <code>s = (points + 1) / (games + 2)</code>; '
         '<code>logit(p_home) = 1.5 (s_home - s_away) + 0.12</code>, with the home term dropped for the '
         'neutral-site Heritage Classic.</li>'
         '<li><b>Baseball:</b> <code>s = ln(pct / (1 - pct))</code>; '
         '<code>logit(p_home) = 1.0 (s_home - s_away) + 0.20</code>.</li>'
         '<li><b>Rugby:</b> <code>s = (league points + 1) / (games + 2)</code>; '
         '<code>logit(p_home) = 0.9 (s_home - s_away) + 0.10</code>.</li></ul>',
         '<p>The shrinkage term stops a three-game record from producing an absurd price. The handicap '
         'line is derived from the same probability with a normal margin assumption (sigma 1.9 goals, '
         '3.4 runs, 12 points) and is labelled a structural estimate wherever it appears.</p>',
         '<h2>The confidence rule, and its arithmetic</h2>',
         '<p><b>High</b> requires both parts of the brief: an originated probability above 70% '
         '<i>and</i> a fair American price inside &minus;250 to +10000. A fair price of &minus;250 is '
         '71.43%, so the qualifying window is 70.00% to 71.43%.</p>',
         '<p><b>Strong</b> is anything at 70% or better that lands outside that window &mdash; which in '
         'practice means the short-priced favourites the band excludes. <b>Medium</b> runs 55-70% and '
         '<b>Low</b> below 55%. Picks are not promoted to High to make the page look better: this desk '
         'publishes '
         f'{len([r for r in rows if r["price"]["pick"]["tier"] == "High"])} High, '
         f'{len([r for r in rows if r["price"]["pick"]["tier"] == "Strong"])} Strong, '
         f'{len([r for r in rows if r["price"]["pick"]["tier"] == "Medium"])} Medium and '
         f'{len([r for r in rows if r["price"]["pick"]["tier"] == "Low"])} Low.</p>',
         '<h2>What a row must have before it is priced</h2>',
         '<ul class="plain">'
         '<li>The fixture on an official schedule with a start time that had not passed.</li>'
         '<li>A numeric input for <i>both</i> sides from an official publisher.</li>'
         '<li>A link to that publisher on the row itself.</li></ul>',
         '<p>If any of the three is missing the row stays blank and the missing input is named. That is '
         'why twelve of the fifteen sports have no price tonight.</p>',
         '<h2>Prose rules</h2>',
         '<p>Each write-up names the selection in its first clause, is at least 30 words, quotes only '
         'numbers that appear in the official source linked on the same card, and avoids internal '
         'vocabulary. The build fails if any write-up is shorter than 30 words or shares a six-word run '
         'with another.</p>']
    return page('Methodology', 'methodology.html', ''.join(b))


def repo_audit_html():
    def sh(cmd):
        try:
            return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True).stdout.strip()
        except Exception:
            return ''
    tracked = len(sh("git ls-files").split())
    htmls = len(sh("git ls-files '*.html'").split())
    desks = sh("ls -d */index.html 2>/dev/null | wc -l").strip()
    tops = len([p for p in Path(ROOT).iterdir() if p.is_dir() and p.name != '.git'])
    datas = len([p for p in (ROOT / 'data').iterdir() if p.is_dir()])
    archive = sh("grep -c \"index.html',\" pipeline/build.py").strip()
    tests = len(sh("ls tests/pipeline/test_*.py").split())
    findings = [
        ('AUD-733-01', 'Publisher registers 16 of the 75 desks',
         f'<code>pipeline/build.py</code> ARCHIVE lists {archive} entries; {desks} top-level directories '
         f'contain an <code>index.html</code>. The remaining desks are in git but not on the live site.',
         'pipeline/build.py'),
        ('AUD-733-02', 'README describes a much smaller artifact',
         'README.md says "one dashboard, nine top-level pages and fifteen sport pages" and a 25-page '
         f'artifact; the checkout holds {htmls} HTML files over {tops} top-level directories.',
         'README.md'),
        ('AUD-733-03', 'One directory per session, no supersession index',
         f'{tops} top-level directories and {datas} directories under data/. Nothing states which desk '
         'supersedes which, which is why the brief\'s complaint about a confusing site is fair.',
         'COORDINATION.md'),
        ('AUD-733-04', 'Historical link checker over-counts',
         'A naive scan of 1,856 HTML files flagged 1,129 "broken relative links"; the first ten are all '
         'absolute https URLs, so that number measures the scanner, not the site. Recorded so the figure '
         'is not repeated as a finding.', 'tests/pipeline'),
        ('AUD-733-05', 'Test surface is fragmented',
         f'{tests} desk-specific test modules plus the canonical suites. The canonical suite is the gate '
         'that matters; this desk adds one focused module rather than a new framework.',
         'tests/pipeline'),
        ('AUD-733-06', 'No tracked build artifacts',
         'No <code>.pyc</code>, <code>__pycache__</code>, <code>_site</code> or <code>node_modules</code> '
         'path is tracked, and .gitignore covers all four. Clean.', '.gitignore'),
    ]
    b = ['<h1>Repository audit</h1>',
         '<p class="lede">Structural review of the checkout this desk was built from, measured at build '
         'time rather than remembered.</p>',
         '<div class="grid">',
         f'<div class="kpi"><b>{tracked}</b><span>tracked files</span></div>',
         f'<div class="kpi"><b>{htmls}</b><span>tracked HTML pages</span></div>',
         f'<div class="kpi"><b>{desks}</b><span>desks with index.html</span></div>',
         f'<div class="kpi"><b>{tops}</b><span>top-level directories</span></div>',
         f'<div class="kpi"><b>{datas}</b><span>data directories</span></div>',
         f'<div class="kpi"><b>{archive}</b><span>published archive entries</span></div>',
         '</div>',
         '<div class="table-wrap"><table><thead><tr><th>#</th><th>Finding</th><th>Detail</th>'
         '<th>File</th></tr></thead><tbody>']
    for fid, title, detail, path in findings:
        b.append(f'<tr><td class="num">{e(fid)}</td><td><b>{e(title)}</b></td><td class="small">{detail}</td>'
                 f'<td class="small"><a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/{e(path)}">'
                 f'{e(path)}</a></td></tr>')
    b.append('</tbody></table></div>')
    b.append('<h2>What this session changed</h2>'
             '<p>Only <code>data/733888f2/</code>, <code>scripts/s733888f2_*</code>, '
             '<code>733888f2/</code>, <code>tests/pipeline/test_desk_733888f2.py</code>, '
             '<code>reports/SESSION_733888F2.md</code>, one append to <code>COORDINATION.md</code> and one '
             'additive ARCHIVE registration line for <code>733888f2/index.html</code>. No peer desk, root '
             'page, workflow or canonical data file was edited.</p>')
    return page('Repository audit', 'repo-audit.html', ''.join(b))


def reverse_html(cov):
    b = ['<h1>Inside OLBG</h1>',
         '<p class="lede">How the hub pages behave, read live at 2026-10-24T22:28-22:44Z, and what that '
         'means for anyone trying to find out what the matches are.</p>',
         '<h2>Route pattern</h2>',
         '<p>Each sport hub is <code>https://www.olbg.com/betting-tips/&lt;Sport&gt;/&lt;sport_id&gt;</code>, '
         'and each event carries its own route of the form '
         '<code>/betting-tips/&lt;Sport&gt;/&lt;Group&gt;/&lt;Competition&gt;/&lt;Home&gt;_vs_&lt;Away&gt;/&lt;sport_id&gt;?event_id=&lt;n&gt;</code>. '
         'The hub shows only one selection per event &mdash; the most-tipped outcome &mdash; with a tip '
         'count and a percentage of tips, never a price history.</p>',
         '<h2>The five things that make it confusing</h2>',
         '<ul class="plain">'
         '<li>The tip percentage is a share of member votes. It is not a probability and it is not odds.</li>'
         '<li>Times are printed on a geo-adjusted clock ("Today", "Tomorrow") with no timezone, and NHL '
         'games all print the same 19:07.</li>'
         '<li>Finished matches can still be listed as upcoming: both darts ties offered on the hub had '
         'already been played on the PDC\'s own schedule (F-05).</li>'
         '<li>Handball\'s most popular selection is "Tie" on most fixtures (F-06).</li>'
         '<li>Four hubs served no events at all tonight: Golf, Snooker, Motor Racing and Rugby League '
         '(the last has outrights only).</li></ul>',
         '<h2>What this desk takes from OLBG, and what it refuses</h2>',
         '<p>OLBG is used for one thing: naming the events and the markets that exist. Every number '
         'published here comes from the league, tour, club or governing body, linked on the row. Tip '
         'shares never enter a price.</p>',
         '<h2>Route inventory by sport</h2>',
         '<div class="table-wrap"><table><thead><tr><th>Sport</th><th>Hub</th><th>Events served</th>'
         '<th>Outcome</th></tr></thead><tbody>']
    for c in cov:
        outcome = 'priced' if c['priced'] else ('listed, unpriced' if c['listed'] else 'no events served')
        b.append(f'<tr><td>{e(c["name"])}</td><td class="small"><a href="{e(c["olbg"])}">{e(c["olbg"])}</a></td>'
                 f'<td class="num">{c["listed"] + c["priced"]}</td><td>{e(outcome)}</td></tr>')
    b.append('</tbody></table></div>')
    return page('Inside OLBG', 'reverse-engineering.html', ''.join(b))


def archive_html():
    b = ['<h1>All desks</h1>',
         '<p class="lede">This repository carries many session desks. This page lists the ones registered '
         'for publication plus the neighbours a reader is most likely to want.</p>',
         '<div class="table-wrap"><table><thead><tr><th>Desk</th><th>What it is</th></tr></thead><tbody>']
    try:
        text = (ROOT / 'pipeline' / 'build.py').read_text()
        block = text.split('ARCHIVE = [')[1].split(']')[0]
        for mth in re.finditer(r"\('([^']+index\.html)',\s*'([^']*)'\)", block):
            b.append(f'<tr><td><a href="../{e(mth.group(1))}">{e(mth.group(1).split("/")[0])}</a></td>'
                     f'<td class="small">{e(mth.group(2))}</td></tr>')
    except Exception:
        b.append('<tr><td colspan="2">Archive list unavailable in this build.</td></tr>')
    b.append(f'<tr><td><a href="index.html">733888f2</a></td><td class="small">This desk: 7 priced '
             f'matches across 3 sports, 7 picks, 18 flags.</td></tr>')
    b.append('</tbody></table></div>')
    return page('All desks', 'archive.html', ''.join(b))


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / 'sports').mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    rows = build_data()
    cov = coverage(rows)

    written = {
        'index.html': index_html(rows, cov),
        'picks.html': picks_html(rows),
        'predictions.html': predictions_html(rows),
        'matches.html': matches_html(rows, cov),
        'markets.html': markets_html(rows),
        'sports.html': page('Sports', 'sports.html', '<h1>Sports</h1><p class="lede">All fifteen sports '
                            'named in the brief, in the brief\'s order, with what was found in each.</p>'
                            '<div class="table-wrap"><table><thead><tr><th>Sport</th>'
                            '<th class="num">Listed</th><th class="num">Priced</th><th>Status</th>'
                            '<th>Page</th></tr></thead><tbody>' + ''.join(
                                f'<tr><td>{e(c["name"])}</td><td class="num">{c["listed"]}</td>'
                                f'<td class="num">{c["priced"]}</td><td>{c["status"]}</td>'
                                f'<td class="small"><a href="sports/{c["slug"]}.html">open</a></td></tr>'
                                for c in cov) + '</tbody></table></div>'),
        'flagged.html': flagged_html(),
        'sources.html': sources_html(),
        'methodology.html': methodology_html(rows),
        'repo-audit.html': repo_audit_html(),
        'reverse-engineering.html': reverse_html(cov),
        'archive.html': archive_html(),
    }
    for name, body in written.items():
        (OUT / name).write_text(body)
    for slug_, body in sport_pages(rows, cov).items():
        (OUT / 'sports' / f'{slug_}.html').write_text(body)
    (OUT / '.nojekyll').write_text('')

    # JSON mirrors
    fixtures = {'captured_utc': D.CAPTURED_UTC, 'session': D.SESSION,
                'priced': [{'id': r['id'], 'sport': r['sport'], 'competition': r['comp'],
                            'start_utc': r['start'], 'venue': r['venue'],
                            'home': r['home'], 'away': r['away'], 'neutral': r.get('neutral', False),
                            'official_url': r['official'], 'inputs': r['inputs'],
                            'facts': r['facts']} for r in rows],
                'unpriced': D.UNPRICED}
    lines = {'method': 'fair two-way prices, decimal = 1/p, no margin added',
             'model_source': 'scripts/s733888f2_model.py',
             'rows': [{'id': r['id'], 'winner': {'home': r['price']['market_winner']['home'],
                                                 'away': r['price']['market_winner']['away']},
                       'handicap': r['price']['market_handicap'],
                       'pick': r['price']['pick'],
                       'pick_id': r['price']['pick']['selection']} for r in rows]}
    picks = {'tiers': {'High': 'p > 0.70 and fair American in [-250, +10000]',
                       'Strong': 'p >= 0.70 outside that band',
                       'Medium': '0.55 <= p < 0.70', 'Low': 'p < 0.55'},
             'picks': [{'id': r['id'], 'sport': r['sport'], 'selection': r['price']['pick']['selection'],
                        'market': r['price']['pick']['market'],
                        'fair_american': r['price']['pick']['american'],
                        'probability': round(r['price']['pick']['p'], 4),
                        'tier': r['price']['pick']['tier'],
                        'prediction': r['prediction']} for r in rows]}
    flags = {'items': [{'id': f[0], 'title': f[1], 'type': f[2], 'source': f[3], 'detail': f[4]}
                       for f in FLAGS]}
    manifest = {'session': D.SESSION, 'task': D.TASK, 'captured_utc': D.CAPTURED_UTC,
                'pages': sorted(list(written) + [f'sports/{s}.html' for s in [c['slug'] for c in cov]]),
                'counts': {'priced_matches': len(rows),
                           'picks': len(rows),
                           'high': sum(1 for r in rows if r['price']['pick']['tier'] == 'High'),
                           'strong': sum(1 for r in rows if r['price']['pick']['tier'] == 'Strong'),
                           'unpriced_listings': len(D.UNPRICED),
                           'sources': len(D.SOURCES),
                           'flags': len(FLAGS),
                           'sports': len(D.SPORTS)}}
    for name, obj in (('fixtures.json', fixtures), ('lines.json', lines), ('picks.json', picks),
                      ('flags.json', flags), ('sources.json', {'sources': D.SOURCES}),
                      ('manifest.json', manifest),
                      ('olbg.json', {'captured_utc': D.CAPTURED_UTC,
                                     'hubs': [{'sport': c['name'], 'url': c['olbg'],
                                               'listed': c['listed'], 'priced': c['priced']}
                                              for c in cov]})):
        (DATA / name).write_text(json.dumps(obj, indent=2) + '\n')

    print(f'built {len(written) + len(cov)} pages, {len(rows)} priced matches, '
          f'{len(D.UNPRICED)} unpriced listings, {len(FLAGS)} flags')


if __name__ == '__main__':
    main()
