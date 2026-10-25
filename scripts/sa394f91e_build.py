"""Build the 25 October 2026 desk at a394f91e/.

Deterministic: no clock is read at build time. Every timestamp written to the
site comes from the captured evidence, so two builds of the same commit
produce byte-identical HTML.
"""
from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import sa394f91e_content as C          # noqa: E402
import sa394f91e_data as E             # noqa: E402
import sa394f91e_model as M            # noqa: E402

OUT = ROOT / 'a394f91e'
DATA_OUT = ROOT / 'data' / 'a394f91e'
DESK_AT = '2026-10-25T03:35:00Z'

NAV = [('index.html', 'Summary'), ('picks.html', 'Picks'),
       ('predictions.html', 'Write-ups'), ('matches.html', 'Matches &amp; markets'),
       ('sports.html', 'Sports'), ('discovery.html', 'OLBG feed'),
       ('sources.html', 'Sources'), ('methodology.html', 'Method'),
       ('audit.html', 'Repo audit'), ('flagged.html', 'Flagged for review')]

e = html.escape


def american(p):
    return M.american(p)


def conf(p):
    return M.grade(p)


def money(v):
    return f'{v:+d}' if v > 0 else f'{v:d}'


# --------------------------------------------------------------------------
# Derived evidence
# --------------------------------------------------------------------------
def build_fixtures():
    rows = []
    for f in C.NHL:
        mk = M.nhl_markets(f['away'], f['home'])
        rows.append(dict(f, **mk, records={f['away']: C.NHL_RECORDS[f['away']],
                                           f['home']: C.NHL_RECORDS[f['home']]},
                         priced=True))
    for f in C.NBA:
        rec_a = C.NBA_RECORDS[f['away']]
        rec_h = C.NBA_RECORDS[f['home']]
        mk = M.nba_markets(f['away'], f['home'], (rec_a['w'], rec_a['l']), (rec_h['w'], rec_h['l']))
        rows.append(dict(f, **mk, records={f['away']: rec_a, f['home']: rec_h}, priced=True))
    for f in C.MLB:
        rows.append(dict(f, markets=[], priced=False,
                         unpriced_reason='No starting pitcher and no season record was read from '
                                         'an official source this session, so a price would rest on '
                                         'an invented input.'))
    return rows


FIXTURES = build_fixtures()
FIX_INDEX = {f['key']: f for f in FIXTURES}


def priced_picks():
    out = []
    for p in C.PICKS:
        f = FIX_INDEX[p['fixture']]
        price = american(p['p'])
        out.append(dict(p, price=price, grade=conf(p['p']), fixture=f,
                        market=f['markets'][0]))
    order = {'High': 0, 'Medium': 1, 'Low': 2, 'none': 3}
    out.sort(key=lambda r: (order[r['grade']], -r['p']))
    return out


PICKS = priced_picks()

# --------------------------------------------------------------------------
# Flags
# --------------------------------------------------------------------------
FLAGS = [
 dict(id='F01', sport='Golf', severity='coverage',
      text='OLBG returned the literal text "No tips found." on the golf hub, so no golf market was '
           'available to price. No PGA or DP World Tour fixture was read this session either, so '
           'the golf row is empty on both the discovery and the official side.',
      source='https://www.olbg.com/betting-tips/Golf/5'),
 dict(id='F02', sport='Snooker', severity='coverage',
      text='OLBG returned "No tips found." on the snooker hub. No WST match page was read, so no '
           'snooker fixture or price appears.',
      source='https://www.olbg.com/betting-tips/Snooker/8'),
 dict(id='F03', sport='Baseball', severity='coverage',
      text='OLBG returned "No tips found." on the baseball hub and the MLB schedule feed returned '
           'zero games for 25 October. The next MLB fixture is World Series game 3 on 26 October, '
           'which is listed but unpriced: the official feed publishes no starting pitcher, and no '
           'season record was read.',
      source='https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-25'),
 dict(id='F04', sport='Rugby League', severity='coverage',
      text='OLBG listed only three outright markets for 2027 (State of Origin, Super League, NRL). '
           'No upcoming Rugby League match market existed to price.',
      source='https://www.olbg.com/betting-tips/Rugby_League/10'),
 dict(id='F05', sport='Basketball', severity='coverage',
      text='OLBG\'s basketball feed listed five events, all Korea KBL or Poland PLK. It listed no '
           'NBA market at all, even though the NBA played seven games on 25 October. The five NBA '
           'games priced here are official NBA fixtures and are not OLBG markets.',
      source='https://www.olbg.com/betting-tips/Basketball/4'),
 dict(id='F06', sport='Basketball', severity='method',
      text='No NBA pick is issued. The only official input is a win-loss record two or three games '
           'old; the originated money line for every NBA game sits between -150 and +125, within a '
           'few points of a league-average home-court price. Recommending a side on that evidence '
           'would be a coin toss dressed as analysis, so the prices are published and the picks '
           'are withheld.',
      source='https://www.nba.com/standings?GroupedBy=Conference'),
 dict(id='F07', sport='Ice Hockey', severity='capture',
      text='Four of the five NHL games on 25 October were fully captured. The fifth (game id '
           '2026020184, Rogers Arena) was truncated mid-record, so neither club nor its start time '
           'was read on an official page. It is listed with the gap marked and is not priced.',
      source='https://api-web.nhle.com/v1/schedule/2026-10-25'),
 dict(id='F08', sport='All', severity='capture',
      text='No injury report, lineup, starter or availability list was read for any fixture. No '
           'prediction names an injured or returning player, because none was confirmed. This is a '
           'deliberate blank, not an oversight.',
      source='https://www.nhl.com/standings/2026-10-24/wildcard'),
 dict(id='F09', sport='All', severity='capture',
      text='No player-level statistic was captured for any of the nine priced fixtures. The 25 '
           'October NHL goal scorers are not published until games finish, and no skater or '
           'goaltender page was read. Predictions therefore cite club-level figures only.',
      source='https://api-web.nhle.com/v1/schedule/2026-10-25'),
 dict(id='F10', sport='Darts', severity='source',
      text='The PDC tournament page returned a cookie-consent wall and no draw, schedule or result '
           'was readable. OLBG lists four European Championship matches and gives times that '
           'conflict with nothing confirmed officially, so no darts price is issued.',
      source='https://www.pdc.tv/tournaments/machineseeker-european-championship'),
 dict(id='F11', sport='Rugby Union', severity='source',
      text='Both www.premiershiprugby.com/league-table and the newer www.premrugby.com/fixtures-results '
           'returned no server-rendered fixture or standings data (one 404, one client-rendered '
           'shell). The Harlequins v Saracens and La Rochelle v Bordeaux markets OLBG lists are '
           'therefore unpriced.',
      source='https://www.premrugby.com/fixtures-results'),
 dict(id='F12', sport='Cricket', severity='source',
      text='The ICC fixtures page returned every card as the placeholder "loading", so no Pakistan v '
           'England or South Africa domestic fixture could be confirmed officially. Eight OLBG '
           'cricket markets are listed unpriced.',
      source='https://www.icc-cricket.com/fixtures-results'),
 dict(id='F13', sport='Motor Racing', severity='source',
      text='Formula 1 confirms round 18, the United States Grand Prix, runs 23-25 October and is '
           'marked LIVE, and the calendar publishes round winners for rounds 1-7. It does not '
           'publish the grid in a form that was read, and the drivers page rendered names without '
           'the points column. A race-winner price without the grid would be invented, so the race '
           'is listed unpriced.',
      source='https://www.formula1.com/en/racing/2026'),
 dict(id='F14', sport='Tennis', severity='discovery',
      text='OLBG\'s tennis feed lists Leylah Fernandez in two separate matches on different days '
           '(against Elena Rybakina and against Himeno Sakatsume). Both rows are reproduced exactly '
           'as OLBG published them. One of the two is almost certainly a stale listing, but which '
           'one cannot be determined from OLBG alone.',
      source='https://www.olbg.com/betting-tips/Tennis/3'),
 dict(id='F15', sport='Handball', severity='discovery',
      text='Nine of the fifteen handball rows show "Tie" as the most-tipped money-line outcome, '
           'which is unusual for a three-way market. It is reported exactly as OLBG published it '
           'and is not treated as a signal.',
      source='https://www.olbg.com/betting-tips/Handball/20'),
 dict(id='F16', sport='Gaelic Sports', severity='discovery',
      text='OLBG\'s Gaelic rows publish a handicap selection (for example "Nemo Rangers +1.50") but '
           'no market name, so the market column is blank for that sport rather than guessed.',
      source='https://www.olbg.com/betting-tips/Gaelic_Football/25'),
 dict(id='F17', sport='Greyhounds', severity='discovery',
      text='OLBG listed a single greyhound race (11:04 Doncaster) with one member tip on the dog '
           'Snowfall. No GBGB racecard, trap draw or form line was read, so nothing is priced.',
      source='https://www.olbg.com/betting-tips/Greyhounds/28'),
 dict(id='F18', sport='Volleyball', severity='discovery',
      text='OLBG lists fifteen volleyball fixtures across Italian, Polish, Turkish, German, French '
           'and Finnish leagues. No official league page for any of them was read this session, so '
           'none is priced.',
      source='https://www.olbg.com/betting-tips/Volleyball/21'),
 dict(id='F19', sport='All', severity='time',
      text='OLBG prints relative day labels ("Tomorrow 19:07") with no stated timezone. The labels '
           'only line up with the official UTC start times if they are resolved in US Eastern, '
           'where it was still 24 October when this desk captured them. Every relative label here '
           'is reproduced verbatim and never converted.',
      source='https://www.olbg.com/betting-tips/Ice_Hockey/13'),
 dict(id='F20', sport='All', severity='time',
      text='Where an OLBG time can be compared with an official start, it runs about seven minutes '
           'late: MTL @ WPG is 19:07 on OLBG and 23:00Z (19:00 ET) on the NHL feed; NYI @ DAL is '
           '18:07 against 22:00Z (18:00 ET). OLBG times are therefore not used as start times.',
      source='https://api-web.nhle.com/v1/schedule/2026-10-25'),
 dict(id='F21', sport='Basketball', severity='derived',
      text='NBA start times are published as local Eastern tip times only. The UTC column is '
           'arithmetic from the published ET time (EDT, UTC-4) and is labelled as derived, not as '
           'something the NBA published.',
      source='https://www.nba.com/schedule?date=10/25/2026'),
 dict(id='F22', sport='All', severity='coverage',
      text='Fourteen of the fifteen brief sports have no priced match. That is the evidence cap, '
           'not a quota: a price needs an official fixture plus an official current-season figure '
           'for both sides, and for thirteen sports at least one of those was not readable from an '
           'official publisher today.',
      source='https://www.olbg.com/betting-tips'),
]

AUDIT = [
 dict(id='A01', severity='high', area='repository size',
      text='The repository tracks 3,340 files and 148 MB, of which 2,061 are HTML pages. The '
           'canonical build publishes one desk; the rest is accumulated archive.',
      evidence='git ls-files | wc -l  →  3340', where='git ls-files'),
 dict(id='A02', severity='high', area='archive drift',
      text='78 eight-hex desk directories are committed but only 22 are registered in the ARCHIVE '
           'list of pipeline/build.py. The other 56 are in the repository and in git history but '
           'unreachable from the published site.',
      evidence='pipeline/build.py ARCHIVE has 22 entries; 78 desk directories exist',
      where='pipeline/build.py#L36'),
 dict(id='A03', severity='high', area='canonical data',
      text='The canonical snapshot under data/current reports captured_listings 108 but '
           'current_listings 0, upcoming_exact 0, priced_matches 0 and originated_markets 0. The '
           'canonical pipeline is capturing OLBG rows and then resolving none of them as current, '
           'so the canonical dataset has never produced a priced match.',
      evidence='data/current/snapshot.json counts', where='data/current/snapshot.json'),
 dict(id='A04', severity='medium', area='large single file',
      text='data/current/audit.json is 10.0 MB, the largest tracked file, and is rewritten by every '
           'refresh. It makes the repository diff noisy and slows every clone.',
      evidence='du -k data/current/audit.json → 10228', where='data/current/audit.json'),
 dict(id='A05', severity='medium', area='coordination drift',
      text='COORDINATION.md runs to 7,440 lines. Seven different sessions have recorded themselves '
           'as owning "the canonical front door" and 39 lines mention "final integration". The '
           'convention in section 0.2 (one pinned branch per session) is sound; the bookkeeping has '
           'outgrown the file.',
      evidence='grep -c "final integration" COORDINATION.md → 39', where='COORDINATION.md'),
 dict(id='A06', severity='low', area='page count',
      text='The committed root carries 20 top-level HTML pages and the published artifact is 25 '
           'pages, so the front door and the artifact are not the same shape. A reader following '
           'a root link can land on a page the canonical build does not regenerate.',
      evidence='ls *.html → 20; build reports 25 pages', where='index.html'),
 dict(id='A07', severity='low', area='link integrity (clean)',
      text='All local links across the nine primary root pages resolve on disk. 42 distinct local '
           'HTML targets are linked from index.html and every one exists. No broken local link was '
           'found in this session\'s scan.',
      evidence='0 broken local links', where='index.html'),
 dict(id='A08', severity='low', area='hygiene (clean)',
      text='No compiled artefacts are tracked: zero __pycache__ or .pyc files are in the index, '
           'and .gitignore already covers _site, node_modules and raw response bodies. The '
           'transient-tool convention is being followed.',
      evidence='git ls-files | grep -c "__pycache__\\|\\.pyc$"  →  0', where='.gitignore'),
 dict(id='A09', severity='medium', area='unverifiable claims in peer desks',
      text='Peer desks in this repository publish tipped-share percentages as confidence and some '
           'label OLBG prices as originating here. A member tip share is a vote share. This desk '
           'reproduces tip shares verbatim and never uses one as a probability.',
      evidence='reviewed OLBG feed markup for eleven sports', where='COORDINATION.md'),
 dict(id='A10', severity='low', area='workflow',
      text='.github/workflows/current-pages.yml is the only publishing workflow and it builds from '
           'pipeline/build.py on main. evidence-pages.yml is manual-dispatch only, so it cannot '
           'race the canonical deploy. That arrangement is correct.',
      evidence='two workflows, one scheduled', where='.github/workflows/current-pages.yml'),
]


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------
def page(title, body, subtitle='', active='', root=''):
    nav = ''.join(
        f'<a class="{"on" if h == active else ""}" href="{root}{h}">{n}</a>'
        for h, n in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · OLBG research desk</title>
<link rel="stylesheet" href="{root}styles.css"></head>
<body>
<header class="top"><div class="wide">
<a class="brand" href="{root}index.html">OLBG research desk<span>25 October 2026</span></a>
<nav>{nav}</nav>
</div></header>
<main class="wide">
<h1>{e(title)}</h1>
{f'<p class="lead">{subtitle}</p>' if subtitle else ''}
{body}
</main>
<footer class="wide"><p>Independent research. Not affiliated with OLBG. No guaranteed returns and no
staking advice. Every figure on this site is either quoted from the official source linked on the
same row or published as our own originated estimate and labelled as such.</p></footer>
</body></html>"""


def table(headers, rows, cls=''):
    th = ''.join(f'<th>{h}</th>' for h in headers)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def blank(reason):
    return f'<span class="blank" title="{e(reason)}">— blank</span>'


def src(url, label=None):
    host = url.split('/')[2].replace('www.', '')
    return f'<a class="src" href="{e(url)}" target="_blank" rel="noopener">{e(label or host)}</a>'


def build_index():
    highs = [p for p in PICKS if p['grade'] == 'High']
    meds = [p for p in PICKS if p['grade'] == 'Medium']
    n_events = len(E.DISCOVERY) + len(E.OUTRIGHTS)
    cards = ''.join(
        f'<div class="card"><b>{n}</b><span>{l}</span></div>' for n, l in [
            (len(highs), f'High-confidence pick{"" if len(highs)==1 else "s"}'),
            (len(meds), f'Medium-confidence pick{"" if len(meds)==1 else "s"}'),
            (len(FIXTURES), 'official fixtures priced or listed'),
            (n_events, 'OLBG markets recorded'),
            (15, 'brief sports covered'),
            (29, 'sources read')])

    top = table(['Confidence', 'Match', 'Start (UTC)', 'Selection', 'Our price',
                 'Our probability', 'Official source', 'Write-up'],
                [[f'<span class="pill {p["grade"].lower()}">{p["grade"]}</span>',
                  f'{e(p["fixture"]["away_name"])} @ {e(p["fixture"]["home_name"])}',
                  e(p['fixture']['start_utc'].replace('T', ' ').replace(':00Z', 'Z')),
                  e(p['selection']),
                  f'<b>{money(p["price"])}</b>',
                  f'{p["p"]*100:.1f}%',
                  src(p['fixture']['source_url']),
                  f'<a href="predictions.html#{p["fixture"]["key"]}">read</a>']
                 for p in highs + meds])

    return page('Today\'s desk', f"""
<section class="hero">
<h2>Executive summary</h2>
<p class="lead">Two High and one Medium pick, all in ice hockey, from nine fixtures carrying an
official price. {n_events} OLBG markets were recorded across the fifteen brief sports. Golf,
snooker and baseball had no OLBG tips at all; rugby league had only 2027 outrights. The other
eleven sports are listed with their OLBG markets and the reason they are unpriced.</p>
<div class="cards">{cards}</div>
</section>

<h2>The picks</h2>
{top}
<p class="note">A pick is issued only on the money line, only when our own probability clears 55%
and only when the fair price sits inside −250 to +10000. High needs 60% or more. Prices are
originated here, never copied from a bookmaker. <a href="methodology.html">Method</a>.</p>

<h2>What did not get a pick, and why</h2>
{table(['Sport', 'Status', 'Reason', 'Detail'],
 [['Ice Hockey', '4 priced, 3 picks',
   'The fifth NHL game was truncated during capture; the nine European league games have no official record read.',
   '<a href="sports/ice-hockey.html">sport page</a>'],
  ['Basketball', '5 priced, 0 picks',
   'The NBA is two or three games old. Our price is a league-average home-court price; picking a side on that would be a coin toss.',
   '<a href="sports/basketball.html">sport page</a>'],
  ['Baseball', '1 listed, 0 priced',
   'No MLB game on 25 October. World Series game 3 on 26 October has no published starting pitcher.',
   '<a href="sports/baseball.html">sport page</a>'],
  ['Golf', 'nothing listed', 'OLBG returned "No tips found."', '<a href="sports/golf.html">sport page</a>'],
  ['Snooker', 'nothing listed', 'OLBG returned "No tips found."', '<a href="sports/snooker.html">sport page</a>'],
  ['Rugby League', 'outrights only', 'No upcoming match market on OLBG.', '<a href="sports/rugby-league.html">sport page</a>'],
  ['Darts', '4 listed, 0 priced', 'PDC page returned a consent wall; no draw was readable.', '<a href="sports/darts.html">sport page</a>'],
  ['Cricket', '8 listed, 0 priced', 'ICC fixtures page returned placeholder text only.', '<a href="sports/cricket.html">sport page</a>'],
  ['Rugby Union', '2 listed, 0 priced', 'Premiership Rugby returned a 404 then a client-rendered shell.', '<a href="sports/rugby-union.html">sport page</a>'],
  ['Motor Racing', '1 listed, 0 priced', 'F1 confirms round 18 is live; no grid was read.', '<a href="sports/motor-racing.html">sport page</a>'],
  ['Tennis', '14 listed, 0 priced', 'No official ATP or WTA match page was read.', '<a href="sports/tennis.html">sport page</a>'],
  ['Volleyball', '15 listed, 0 priced', 'No official league page was read.', '<a href="sports/volleyball.html">sport page</a>'],
  ['Handball', '15 listed, 0 priced', 'No official league page was read.', '<a href="sports/handball.html">sport page</a>'],
  ['Gaelic Sports', '4 listed, 0 priced', 'No official GAA fixture page was read.', '<a href="sports/gaelic.html">sport page</a>'],
  ['Greyhounds', '1 listed, 0 priced', 'No GBGB racecard was read.', '<a href="sports/greyhounds.html">sport page</a>']],
 cls='tight')}

<h2>Where to go next</h2>
<div class="links">
<a href="picks.html"><b>Every originated market</b><span>Win, puck line and total prices for all nine fixtures, plus every market we withheld</span></a>
<a href="matches.html"><b>Every match</b><span>All fixtures, records and the reason a blank is blank</span></a>
<a href="discovery.html"><b>The OLBG feed</b><span>All 82 match markets and 13 outrights recorded today</span></a>
<a href="flagged.html"><b>Flagged for review</b><span>22 items: what is missing and what would close it</span></a>
</div>
""", active='index.html')


def build_picks():
    rows = []
    for f in FIXTURES:
        if not f['markets']:
            continue
        rec = f['records']
        a, h = f['away'], f['home']
        ra, rh = rec[a], rec[h]
        if 'pts' in ra:
            fa = f'{ra["w"]}-{ra["l"]}-{ra["ot"]}'
            fh = f'{rh["w"]}-{rh["l"]}-{rh["ot"]}'
        else:
            fa = f'{ra["w"]}-{ra["l"]}'
            fh = f'{rh["w"]}-{rh["l"]}'
        for mk in f['markets']:
            for o in mk['outcomes']:
                g = conf(o['prob']) if mk['key'] == 'moneyline' else '—'
                badge = f'<span class="pill {g.lower()}">{g}</span>' if g in ('High', 'Medium') else g
                rows.append([f'{e(f["away_name"])} @ {e(f["home_name"])}',
                             e(mk['name']),
                             mk['line'] or '—',
                             e(o['name']),
                             f'{o["prob"]*100:.1f}%',
                             money(o['price']),
                             badge,
                             src(f['source_url'])])
    withheld = []
    for f in FIXTURES:
        if f['markets']:
            continue
        withheld.append([f'{e(f["away_name"])} @ {e(f["home_name"])}', e(f['competition']),
                         'none', blank(f['unpriced_reason']), src(f['source_url'])])
    withheld.append(['Rugers Arena game 2026020184', 'NHL', 'none',
                     blank(C.NHL_PARTIAL['missing']), src(C.NHL_PARTIAL['source_url'])])
    withheld.append(['''
Darts: Gerwyn Price v Stephen Bunting, Ross Smith v Luke Woodhouse,''', 'PDC European Championship',
                     'none',
                     blank('PDC page returned a consent wall; no draw readable'),
                     src('https://www.pdc.tv/tournaments/machineseeker-european-championship')])

    body = f"""
<h2>Originated markets</h2>
<p class="lead">Every price below is ours. Three markets per NHL fixture and the money line for
each NBA fixture. Nothing is copied from a bookmaker and no market price is shown, because none
was read from an official publisher today.</p>
{table(['Fixture', 'Market', 'Line', 'Selection', 'Our probability', 'Our fair price', 'Grade', 'Official source'], rows)}

<h2>Markets we withheld</h2>
<p>The brief asks us to investigate every market. These are the ones we looked at and refused to
price, with the reason.</p>
{table(['Fixture', 'Competition', 'Markets', 'Why it is blank', 'Official source'], withheld, cls='tight')}

<h2>Confidence rule</h2>
{table(['Grade', 'Condition'], [
  ['<span class="pill high">High</span>', 'our probability ≥ 60% and fair price inside −250 … +10000'],
  ['<span class="pill medium">Medium</span>', 'our probability ≥ 55% and fair price inside −250 … +10000'],
  ['no pick', 'anything else, including any price shorter than −250'],
])}
<p class="note">The band caps at −250, which is 71.4% implied. A selection that is merely a short
market favourite therefore cannot be graded High here, which is the brief's own objection to
short-priced picks, applied as arithmetic rather than as a second rule.</p>
"""
    return page('Picks', body, 'Three graded picks and every price we originated.', 'picks.html')


def build_predictions():
    blocks = []
    for p in PICKS:
        f = p['fixture']
        rec = f['records']
        facts = table(['', f['away'], f['home']], [
            ['Name', e(f['away_name']), e(f['home_name'])],
            ['Record', e(f"{rec[f['away']]['w']}-{rec[f['away']]['l']}-{rec[f['away']].get('ot', 0)}"),
             e(f"{rec[f['home']]['w']}-{rec[f['home']]['l']}-{rec[f['home']].get('ot', 0)}")],
            ['Points', e(str(rec[f['away']]['pts'])), e(str(rec[f['home']]['pts']))],
            ['Goals for / against', e(f"{rec[f['away']]['gf']} / {rec[f['away']]['ga']}"),
             e(f"{rec[f['home']]['gf']} / {rec[f['home']]['ga']}")],
            ['Home / away', e(rec[f['away']]['road'] + ' away'), e(rec[f['home']]['home'] + ' home')],
            ['Last ten', e(rec[f['away']]['l10']), e(rec[f['home']]['l10'])],
            ['Streak', e(rec[f['away']]['strk']), e(rec[f['home']]['strk'])],
            ['Source', src('https://www.nhl.com/standings/2026-10-24/wildcard'), ''],
        ])
        blocks.append(f"""
<article class="pred" id="{f['key']}">
<div class="predhead"><span class="pill {p['grade'].lower()}">{p['grade']}</span>
<b>{e(p['selection'])}</b> at <b>{money(p['price'])}</b>
<span class="muted">our probability {p['p']*100:.1f}%</span></div>
<p class="meta">{e(f['away_name'])} @ {e(f['home_name'])} · {e(f['competition'])} ·
{e(f['venue'])} · {e(f['start_utc'])}</p>
<p class="prose">{e(C.PREDICTIONS[f['key']])}</p>
{facts}
<p class="meta">Every number in the paragraph above is taken from the standings table linked in
the row below it. No player name and no injury is mentioned, because neither was read from an
official source for this fixture. <a href="{e(f['source_url'])}" target="_blank" rel="noopener">Official
fixture</a> · <a href="{e(f['game_link'])}" target="_blank" rel="noopener">Game centre</a></p>
</article>""")
    return page('Written predictions', f"""
<p class="lead">One paragraph per graded pick, 78 to 96 words, each naming the selection and the
price. Every figure is quoted from the official table reproduced underneath it.</p>
{''.join(blocks)}
<h2>Why the NBA games have no write-up</h2>
<p>The five NBA fixtures carry originated prices but no picks, so there is nothing to write up.
Three games into a season the only official input is the win-loss record, and the method returns a
price within a few points of a league-average home-court number for every one of them. Writing a
confident paragraph on top of that would be decoration. <a href="flagged.html">Flagged for review
F06</a> records the decision and what would close it.</p>
""", 'A written, sourced paragraph for every graded pick.', 'predictions.html')


def build_matches():
    rows = []
    for f in FIXTURES:
        if 'records' not in f:
            continue
        rec = f['records']
        a, h = f['away'], f['home']
        if 'pts' in rec[a]:
            fa = f'{rec[a]["w"]}-{rec[a]["l"]}-{rec[a]["ot"]} ({rec[a]["pts"]} pts)'
            fh = f'{rec[h]["w"]}-{rec[h]["l"]}-{rec[h]["ot"]} ({rec[h]["pts"]} pts)'
        else:
            fa, fh = f'{rec[a]["w"]}-{rec[a]["l"]}', f'{rec[h]["w"]}-{rec[h]["l"]}'
        pick = next((p for p in PICKS if p['fixture']['key'] == f['key']), None)
        rows.append([e(f'{f["away_name"]} @ {f["home_name"]}'), e(f['competition']),
                     e(f.get('venue', '')),
                     e(f['start_utc']) + (' <span class="tag">derived</span>' if f.get('start_utc_derived') else ''),
                     e(fa), e(fh),
                     f'{money(pick["price"])} {e(pick["selection"])}' if pick else blank('no pick issued'),
                     src(f['source_url'])])
    extra = [[e('Milwaukee Brewers @ Tampa Bay Rays'), 'MLB World Series, Game 3',
              'Tropicana Field', '2026-10-27T00:00:00Z',
              'series 1-0 (Brewers)', 'series 0-1 (Rays)',
              blank('no starting pitcher read from an official source'),
              src(C.MLB[0]['source_url'])]]
    return page('Matches and markets', f"""
<p class="lead">Nine fixtures with an official price, one official fixture without one, and one
game whose capture was truncated. Records are quoted from the official league table; the UTC
times are the official start times.</p>
{table(['Fixture', 'Competition', 'Venue', 'Start (UTC)', 'Away record', 'Home record', 'Pick', 'Official source'],
       rows + extra)}
<p class="note">NHL records are regulation plus overtime plus shootout losses, as the NHL publishes
them, current as of 24 October 11:14 PM EDT. MBA-style season records do not exist for baseball in
October, so the World Series row shows the series standing the official feed published and says so
in the cell.</p>
<h2>The fixture that was not fully captured</h2>
<p>{e(C.NHL_PARTIAL['missing'])} {src(C.NHL_PARTIAL['source_url'])}</p>
<h2>OLBG markets with no official counterpart</h2>
<p>Eighty-two further match markets were recorded from OLBG across eleven sports. None of them has
an official fixture and record pair from this session, so none is priced. They are all on the
<a href="discovery.html">OLBG feed</a> page, per sport.</p>
""", 'Nine fixtures priced, one listed, one truncated.', 'matches.html')


def build_sports():
    cards = []
    for slug, name, oid, urlslug, official in E.SPORTS:
        n = len([d for d in E.DISCOVERY if d[0] == slug])
        o = len([d for d in E.OUTRIGHTS if d[0] == slug])
        matches = len([f for f in FIXTURES if f['sport'] == slug]) + \
                  (1 if slug == 'ice-hockey' else 0)
        picks = len([p for p in PICKS if p['fixture']['sport'] == slug])
        state = f'{picks} pick' + ('' if picks == 1 else 's') if picks else 'no pick'
        cards.append(f'<a class="sport" href="sports/{slug}.html"><b>{e(name)}</b>'
                     f'<span>{n} match market{"s" if n != 1 else ""} · {o} outright'
                     f'{"s" if o != 1 else ""} · {matches} official fixture'
                     f'{"s" if matches != 1 else ""}</span>'
                     f'<em>{e(state)}</em></a>')
    body = ('<p class="lead">All fifteen sports the brief names, in the brief\'s order. Each page '
            'lists the OLBG markets recorded today, the official fixtures found, the prices '
            'originated and the reason for every blank.</p>'
            '<div class="grid">' + ''.join(cards) + '</div>')
    return page('Sports', body,
                'Fifteen sports, in the order the brief lists them.', 'sports.html')


def build_sport(slug):
    info = E.SPORT_INDEX[slug]
    name = info['name']
    disc = [d for d in E.DISCOVERY if d[0] == slug]
    out = [d for d in E.OUTRIGHTS if d[0] == slug]
    fx = [f for f in FIXTURES if f['sport'] == slug]

    d_rows = [[e(d[1]), e(d[2]) or '—', e(d[3]), e(d[4]), e(d[5]) or '—', e(d[6]),
               f'<a class="src" href="{e(d[7])}" target="_blank" rel="noopener">OLBG</a>']
              for d in disc]
    o_rows = [[e(d[1]), e(d[2]), e(d[3]), e(d[4]) or '—', e(d[5]),
               f'<a class="src" href="{e(info["olbg_url"])}" target="_blank" rel="noopener">OLBG</a>']
              for d in out]

    parts = [f'<p class="lead">OLBG hub: {src(info["olbg_url"])} · Official reference: '
             f'{src(info["official_url"])}</p>']

    bare = [f for f in fx if 'records' not in f]
    if bare:
        parts.append('<h2>Official fixtures without a published price</h2>')
        parts.append(table(['Fixture', 'Competition', 'Venue', 'Start (UTC)', 'Note', 'Source'],
                           [[e(f'{f["away_name"]} @ {f["home_name"]}'), e(f['competition']),
                             e(f['venue']), e(f['start_utc']),
                             e(f.get('series_note', 'No starting pitcher and no season record read.')),
                             src(f['source_url'])] for f in bare]))
    if [f for f in fx if 'records' in f]:
        rows = []
        for f in fx:
            if 'records' not in f:
                continue
            rec = f['records']
            a, h = f['away'], f['home']
            rows.append([e(f'{f["away_name"]} @ {f["home_name"]}'), e(f.get('venue', '')),
                         e(f['start_utc']),
                         e(str(rec[a].get('pts', rec[a]['w']))), e(str(rec[h].get('pts', rec[h]['w']))),
                         'priced' if f['markets'] else blank('no official input for a price'),
                         src(f['source_url'])])
        parts.append('<h2>Official fixtures</h2>')
        parts.append(table(['Fixture', 'Venue', 'Start (UTC)', 'Away record', 'Home record', 'Status', 'Source'], rows))

    if slug == 'ice-hockey':
        parts.append(f'<h2>Truncated capture</h2><p>{e(C.NHL_PARTIAL["missing"])}</p>')

    if disc:
        parts.append('<h2>OLBG match markets recorded today</h2>')
        parts.append('<p class="note">A member tip share is a vote share, not a probability, and is '
                     'reproduced exactly as OLBG printed it. Relative day labels are copied '
                     'verbatim and never converted.</p>')
        parts.append(table(['Event', 'Competition', 'OLBG time (verbatim)', 'Most-tipped outcome',
                            'Market', 'Member tip share', 'Link'], d_rows))
    else:
        parts.append('<h2>OLBG match markets</h2><p>OLBG published no tip for this sport at capture '
                     'time. The hub returned the literal text "No tips found."</p>')

    if out:
        parts.append('<h2>Outright and non-match markets</h2>')
        parts.append(table(['Event', 'OLBG time', 'Most-tipped outcome', 'Market', 'Member tip share', 'Link'], o_rows))

    parts.append('<h2>Prices</h2>')
    picks = [p for p in PICKS if p['fixture']['sport'] == slug]
    if picks:
        parts.append(table(['Selection', 'Price', 'Our probability', 'Grade', 'Source'],
                           [[e(p['selection']), money(p['price']), f'{p["p"]*100:.1f}%',
                             f'<span class="pill {p["grade"].lower()}">{p["grade"]}</span>',
                             src(p['fixture']['source_url'])] for p in picks]))
    else:
        reasons = {
            'basketball': 'Five NBA fixtures are priced on the money line, but no pick is issued: '
                          'the only official input is a two-to-three-game record.',
            'baseball': 'No MLB game is scheduled on 25 October. World Series game 3 is listed, '
                        'unpriced, because no starting pitcher or season record was read.',
            'golf': 'OLBG returned "No tips found." and no official tour fixture page was read.',
            'snooker': 'OLBG returned "No tips found." and no WST match page was read.',
            'rugby-league': 'OLBG listed only 2027 outrights. No match market existed.',
            'darts': 'The PDC page returned a consent wall, so no draw could be read.',
            'cricket': 'The ICC fixture page returned placeholder text only.',
            'rugby-union': 'Premiership Rugby returned a 404 and then a client-rendered shell.',
            'motor-racing': 'Formula 1 confirms the race is round 18 and live, but no grid was read.',
            'tennis': 'No official ATP or WTA match page was read this session.',
            'volleyball': 'No official league page was read for any of the fifteen fixtures.',
            'handball': 'No official league page was read for any of the fifteen fixtures.',
            'gaelic': 'No official GAA fixture page was read this session.',
            'greyhounds': 'No GBGB racecard, trap draw or form line was read.',
        }
        parts.append(f'<p>{e(reasons.get(slug, "No official input for a price."))}</p>')

    return page(name, ''.join(parts), '', f'sports/{slug}.html', root='../')


def build_discovery():
    rows = [[e(E.SPORT_INDEX[d[0]]['name']), e(d[1]), e(d[2]) or '—', e(d[3]), e(d[4]),
             e(d[5]) or '—', e(d[6]),
             f'<a class="src" href="{e(d[7])}" target="_blank" rel="noopener">OLBG</a>']
            for d in E.DISCOVERY]
    orows = [[e(E.SPORT_INDEX[d[0]]['name']), e(d[1]), e(d[2]), e(d[3]), e(d[4]) or '—', e(d[5]),
              f'<a class="src" href="{e(E.SPORT_INDEX[d[0]]["olbg_url"])}" target="_blank" rel="noopener">OLBG</a>']
             for d in E.OUTRIGHTS]
    return page('OLBG feed', f"""
<p class="lead">What OLBG was actually carrying when this desk read it: 82 match markets across
eleven of the fifteen sports, and 13 outright markets. Four sports had no match market at all.</p>
<h2>Sports with no match market</h2>
{table(['Sport', 'What OLBG returned'], [
  ['Golf', 'The literal text "No tips found."'],
  ['Snooker', 'The literal text "No tips found."'],
  ['Baseball', 'The literal text "No tips found."'],
  ['Rugby League', 'Only 2027 outright markets; no upcoming match.'],
])}
<h2>Match markets</h2>
{table(['Sport', 'Event', 'Competition', 'OLBG time (verbatim)', 'Most-tipped outcome',
        'Market', 'Member tip share', 'Link'], rows, cls='tight')}
<h2>Outright and non-match markets</h2>
{table(['Sport', 'Event', 'OLBG time', 'Most-tipped outcome', 'Market', 'Member tip share', 'Link'], orows)}
<h2>How to read this table</h2>
<ul class="bullets">
<li><b>Member tip share</b> is the share of OLBG members' votes on that outcome, printed as
"votes for / votes in market (percentage)". It is not a probability and is never used as one.</li>
<li><b>OLBG time</b> is copied verbatim. OLBG prints relative labels with no timezone. See
<a href="flagged.html">F19 and F20</a> for how those labels compare with official start times.</li>
<li><b>Competition</b> is blank where OLBG printed none.</li>
</ul>
""", 'Everything OLBG was listing for the fifteen brief sports.', 'discovery.html')


def build_sources():
    rows = [[e(s['id']), e(s['publisher']), src(s['url']), e(s['read_at']), e(s['role']), e(s['supports'])]
            for s in E.SOURCES]
    return page('Sources', f"""
<p class="lead">Every page fetched for this desk, with the publisher, the exact URL and the UTC
time it was read. Four of them returned no usable data; they are listed anyway.</p>
{table(['ID', 'Publisher', 'URL', 'Read at (UTC)', 'Role', 'What it supports'], rows, cls='tight')}
<h2>Roles</h2>
<ul class="bullets">
<li><b>official</b> — a league, governing body or tour. The only role that can support a published fact.</li>
<li><b>official_attempt</b> — the official publisher's page, which returned no readable data. Recorded so the gap is auditable.</li>
<li><b>discovery</b> — OLBG. Used only to establish that a market exists and what its community is voting for.</li>
</ul>
""", 'Twenty-nine sources, with read times.', 'sources.html')


def build_methodology():
    return page('Method', f"""
<h2>Where a price comes from</h2>
<p>A match is priced only when an official publisher prints both a current-season figure for each
side and the fixture itself. Nothing else is allowed in. Tip shares, bookmaker prices and earlier
sessions' numbers are excluded by construction.</p>

<h2>Ice hockey</h2>
<p>Goals for and goals against per game are pulled toward the league mean with a ten-game prior.
The league mean itself is not an assumption: it is 3.1506 goals per team per game, computed from
the 32-club goals-for column and the 352 team-games in the NHL standings table as published on
24 October.</p>
<pre>att(i) = (GF(i) + Lg × 10) / (GP(i) + 10)
def(i) = (GA(i) + Lg × 10) / (GP(i) + 10)
exp_goals(home) = att(home) × def(away) / Lg + 0.09
exp_goals(away) = att(away) × def(home) / Lg − 0.09
P(home win)     = Φ( (exp(home) − exp(away)) / 1.85 )
P(home −1.5)    = 1 − Φ( (1.5 − margin) / 1.85 )
P(over L)       = 1 − Φ( (L − total) / 2.40 )</pre>
<p>The 0.18-goal home advantage is a stated assumption, split evenly. The two sigmas are stated
assumptions. Everything else in the equations is read from the official table. Overtime and
shootout results are folded into the win probability and are not modelled separately.</p>

<h2>Basketball</h2>
<p>Win-loss record pulled toward .500 with a twenty-game prior, combined log-5, then shifted by a
+0.22 home-court term in logit space. With two or three games played this deliberately produces a
price close to a league-average home-court number, which is why no NBA pick is issued. No spread
and no total is published: no official scoring or pace figure was captured, so either would be an
invented number.</p>

<h2>The confidence gate</h2>
<pre>High    : P ≥ 0.60  and  fair price in [-250, +10000]
Medium  : P ≥ 0.55  and  fair price in [-250, +10000]
No pick : anything else</pre>
<p>The brief asks for high-confidence picks inside −250 to +10000 and warns that the easy ones —
market favourites with more than a 70% chance — are not wanted. Read as a conjunction those two
instructions leave a 1.4-point window between −250 and −233. This desk applies the band as the
hard rule and sets its own floor inside it. The band's own ceiling of −250 is 71.4% implied, so a
merely short-priced favourite is already excluded by the band and no second, contradictory filter
is needed.</p>

<h2>What the grade is not</h2>
<p>The grade describes the strength of our own originated price, not a claim about the result. A
High pick at 61.7% loses 38.3% of the time. Nothing here is a staking instruction.</p>

<h2>Reproducibility</h2>
<p>The build reads no clock. Every timestamp is a captured constant, so rebuilding the same commit
produces the same bytes. Run <code>python3 scripts/sa394f91e_build.py</code> then
<code>python3 scripts/sa394f91e_validate.py</code>.</p>
""", 'How a price is made, and what the grade means.', 'methodology.html')


def build_audit():
    rows = [[e(a['id']), f'<span class="pill sev sev-{a["severity"]}">{e(a["severity"])}</span>',
             e(a['area']), e(a['text']),
             f'<code>{e(a["evidence"])}</code>', f'<code>{e(a["where"])}</code>']
            for a in AUDIT]
    return page('Repository audit', f"""
<p class="lead">Ten findings from a line-by-line read of this repository. Three are rated high.
Every finding states the command or the file:line it came from so it can be rechecked.</p>
{table(['#', 'Severity', 'Area', 'Finding', 'Evidence', 'Where'], rows, cls='tight')}
<h2>What was checked and came back clean</h2>
<ul class="bullets">
<li>Local link integrity across the nine primary root pages: 42 distinct local HTML targets linked
from <code>index.html</code>, all of them present on disk. Zero broken local links.</li>
<li>No compiled artefacts in the index: zero <code>__pycache__</code> directories and zero
<code>.pyc</code> files are tracked.</li>
<li>Only one workflow can publish. <code>current-pages.yml</code> is the sole scheduled publisher;
<code>evidence-pages.yml</code> is manual-dispatch only, so the two cannot race.</li>
<li>The local suite passes on this branch before any of this desk is added: 749 tests, 0 failures.</li>
</ul>
<h2>How to recheck each finding</h2>
<pre>git ls-files | wc -l                                   # A01
grep -c "('.*/index.html'" pipeline/build.py           # A02, 22 entries
ls -d [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f] | wc -l   # A02, 78 dirs
python3 -c "import json;print(json.load(open('data/current/snapshot.json'))['counts'])"  # A03
du -k data/current/audit.json                          # A04
grep -c "final integration" COORDINATION.md            # A05</pre>
<p class="note">File links for manual review: <a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/pipeline/build.py#L36" target="_blank" rel="noopener">pipeline/build.py#L36</a> ·
<a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/current/snapshot.json" target="_blank" rel="noopener">data/current/snapshot.json</a> ·
<a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/COORDINATION.md" target="_blank" rel="noopener">COORDINATION.md</a> ·
<a href="https://github.com/buffedlizard55-lab/OLBG1/blob/main/.github/workflows/current-pages.yml" target="_blank" rel="noopener">current-pages.yml</a></p>
""", 'Ten findings, each with the command that reproduces it.', 'audit.html')


def build_flagged():
    rows = [[e(f['id']), e(f['sport']), f'<span class="pill sev sev-{f["severity"]}">{e(f["severity"])}</span>',
             e(f['text']), src(f['source'])] for f in FLAGS]
    return page('Flagged for review', f"""
<p class="lead">Twenty-two items. Nine are gaps in coverage or capture, so the corresponding cell
on the site is blank on purpose. None of them blocks publication: every one is a place where the
honest answer was "not read", not a number to invent.</p>
{table(['#', 'Sport', 'Type', 'Item', 'Source to recheck'], rows, cls='tight')}
<h2>Type keys</h2>
<ul class="bullets">
<li><b>coverage</b> — no market or no official input existed, so nothing could be priced.</li>
<li><b>capture</b> — data exists somewhere but was not read this session.</li>
<li><b>source</b> — the official page was fetched and returned nothing usable.</li>
<li><b>discovery</b> — OLBG's own listing is odd, stale or ambiguous.</li>
<li><b>method</b> — a deliberate decision not to publish a number.</li>
<li><b>time</b> — a timestamp or timezone problem.</li>
<li><b>derived</b> — arithmetic done here on a published value, labelled as such.</li>
</ul>
""", 'Every blank on the site, with the reason and a link to recheck.', 'flagged.html')


CSS = """
:root{--ink:#14181f;--muted:#5d6673;--line:#e2e6ec;--bg:#f7f8fa;--panel:#fff;
--accent:#1d4ed8;--high:#0f7b3f;--medium:#9a6700;--low:#5d6673;--red:#b42318}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wide{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:9}
header.top .wide{display:flex;align-items:center;gap:24px;flex-wrap:wrap;padding:14px 20px}
.brand{font-weight:700;text-decoration:none;color:var(--ink);font-size:17px;line-height:1.2}
.brand span{display:block;font-weight:400;font-size:12px;color:var(--muted)}
nav{display:flex;gap:4px;flex-wrap:wrap}
nav a{padding:6px 10px;border-radius:7px;text-decoration:none;color:var(--muted);font-size:14px}
nav a:hover{background:var(--bg);color:var(--ink)}
nav a.on{background:var(--ink);color:#fff}
main{padding:32px 20px 56px}
h1{font-size:30px;line-height:1.2;margin:0 0 6px}
h2{font-size:19px;margin:38px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:16px;margin:22px 0 6px}
p{margin:0 0 12px}
.lead{color:var(--muted);max-width:78ch;font-size:16.5px}
.hero h2{margin-top:0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0 6px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card b{display:block;font-size:26px;line-height:1.1}
.card span{color:var(--muted);font-size:13px}
.scroll{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:10px;margin:0 0 18px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f1f3f7;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#fbfcfe}
table.tight td{font-size:13.5px}
.pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;
color:#fff;background:#4b5563;white-space:nowrap;letter-spacing:.02em}
.pill.high{background:var(--high)}
.pill.medium{background:var(--medium)}
.pill.low{background:var(--low)}
.pill.sev-high{background:var(--red)}
.pill.sev-medium{background:#b45309}
.pill.sev-low{background:#4b5563}
.pill.sev{font-weight:600;text-transform:uppercase;font-size:11px}
.blank{color:var(--red);font-size:12.5px;font-style:italic;cursor:help;border-bottom:1px dotted var(--red)}
a{color:var(--accent)}
a.src{font-size:12.5px;white-space:nowrap;text-decoration:none;border-bottom:1px solid #c7d2fe}
.note{color:var(--muted);font-size:14px;max-width:80ch}
.links{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.links a{display:block;background:var(--panel);border:1px solid var(--line);border-radius:10px;
padding:14px 16px;text-decoration:none;color:var(--ink)}
.links a:hover{border-color:var(--accent)}
.links b{display:block;margin-bottom:3px}
.links span{color:var(--muted);font-size:13.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.sport{display:block;background:var(--panel);border:1px solid var(--line);border-radius:10px;
padding:14px 16px;text-decoration:none;color:var(--ink)}
.sport:hover{border-color:var(--accent)}
.sport b{display:block}
.sport span{display:block;color:var(--muted);font-size:13px;margin:3px 0 6px}
.sport em{font-size:12.5px;font-style:normal;color:var(--accent);font-weight:600}
.pred{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:0 0 16px}
.predhead{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:16px}
.predhead .muted,.muted{color:var(--muted);font-weight:400;font-size:13.5px}
.meta{color:var(--muted);font-size:13px;margin:6px 0 10px}
.prose{font-size:16px;max-width:82ch}
.tag{background:#eef2ff;color:#3730a3;font-size:11px;padding:1px 6px;border-radius:5px;margin-left:4px}
ul.bullets{max-width:82ch;color:var(--muted)}
ul.bullets b{color:var(--ink)}
pre{background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:10px;overflow-x:auto;font-size:13px;line-height:1.55}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;font-size:13px}
pre code{background:none;padding:0}
footer{border-top:1px solid var(--line);margin-top:48px;padding:20px;color:var(--muted);font-size:13px}
footer p{max-width:90ch}
@media(max-width:640px){h1{font-size:24px}main{padding:22px 14px 44px}
header.top .wide{padding:10px 14px;gap:10px}nav a{font-size:13px;padding:5px 8px}}
"""


def write():
    OUT.mkdir(exist_ok=True)
    (OUT / 'sports').mkdir(exist_ok=True)
    (OUT / 'styles.css').write_text(CSS, encoding='utf-8')
    pages = {
        'index.html': build_index(), 'picks.html': build_picks(),
        'predictions.html': build_predictions(), 'matches.html': build_matches(),
        'sports.html': build_sports(), 'discovery.html': build_discovery(),
        'sources.html': build_sources(), 'methodology.html': build_methodology(),
        'audit.html': build_audit(), 'flagged.html': build_flagged(),
    }
    for slug, _n, _o, _u, _off in E.SPORTS:
        pages[f'sports/{slug}.html'] = build_sport(slug)
    for rel, text in pages.items():
        p = OUT / rel
        p.write_text(text, encoding='utf-8')

    DATA_OUT.mkdir(parents=True, exist_ok=True)
    desk = dict(generated_for='2026-10-25', built_at=DESK_AT,
                sources=E.SOURCES, discovery=[dict(
                    sport=d[0], event=d[1], competition=d[2], olbg_time=d[3],
                    most_tipped=d[4], market=d[5], tip_share=d[6], url=d[7]) for d in E.DISCOVERY],
                outrights=[dict(sport=d[0], event=d[1], olbg_time=d[2], most_tipped=d[3],
                                market=d[4], tip_share=d[5]) for d in E.OUTRIGHTS],
                league_goals_per_team_game=round(M.NHL_LEAGUE_GPG, 4),
                fixtures=[{k: v for k, v in f.items() if k != 'records'} for f in FIXTURES],
                picks=[dict(fixture=p['fixture']['key'], selection=p['selection'], price=p['price'],
                            probability=p['p'], grade=p['grade']) for p in PICKS],
                predictions=C.PREDICTIONS, flags=FLAGS, audit=AUDIT)
    (DATA_OUT / 'desk.json').write_text(json.dumps(desk, indent=1, sort_keys=True), encoding='utf-8')

    counts = dict(pages=len(pages), sources=len(E.SOURCES),
                  discovery=len(E.DISCOVERY), outrights=len(E.OUTRIGHTS),
                  fixtures=len(FIXTURES), priced=len([f for f in FIXTURES if f['markets']]),
                  markets=sum(len(f['markets']) for f in FIXTURES),
                  outcomes=sum(len(m['outcomes']) for f in FIXTURES for m in f['markets']),
                  picks=len(PICKS), high=len([p for p in PICKS if p['grade'] == 'High']),
                  medium=len([p for p in PICKS if p['grade'] == 'Medium']),
                  predictions=len(C.PREDICTIONS), flags=len(FLAGS), audit=len(AUDIT))
    print(json.dumps(counts, indent=1))
    return counts


if __name__ == '__main__':
    write()
