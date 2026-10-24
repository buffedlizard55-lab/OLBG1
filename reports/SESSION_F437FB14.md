# Session F437FB14 — clarity-first 24 October 2026 desk

**Session:** `f437fb14-olbg1` · **Branch:** `arena/f437fb14-olbg1` · **Base:** `1a203e9`
**Claim:** `TF437F`, recorded in `COORDINATION.md` §84 before any build work.
**Published desk:** `/f437fb14/` (26 pages) · JSON in `data/f437fb14/`

## What this session set out to fix

The brief's repeated complaint is comprehension, not volume: *"the sites are too confusing to
understand what the matches are and where the picks are."* Recent desks had also converged on two
unhelpful extremes — four sessions published **zero** High picks, and `8aede3ba` published **66**
High picks all at the same price of −239.

This desk therefore treats the presentation contract as a first-class deliverable:

1. The landing page answers three questions above the fold — *how many matches, how many priced,
   what are the picks* — then gives a one-line card of every selection.
2. A "Where everything is" block maps six destinations in plain language.
3. Every pick prints **selection · match · start · price · probability · evidence count · window**,
   so a reader can overrule the label with the number in front of them.

## Research actually performed (all reads 2026-10-24, 17:42–18:35 UTC)

| Source | Supplied |
|---|---|
| OLBG, all 15 hubs | 93 fixtures/races, market labels, tip-share votes (never used as a probability) |
| MLB Stats API schedule | World Series Game 2, gamePk 849802, 00:00Z 25 Oct, `ifNecessary=N` |
| MLB Stats API people | Rasmussen 2.67 ERA / 0.91 WHIP / 174 K; Henderson 2.47 / 0.84 / 110 K |
| MLB Stats API standings | Tampa Bay 98-64, 736 RS / 650 RA, 43-38 road |
| NBA games | 8 fixtures, tip times, game IDs, per-team season leaders |
| NBA standings | 2026-27 records, home/road, conference, streak for all 30 clubs |
| NHL schedule | 12 fixtures with UTC starts, venues, game state, licensed prices |
| NHL standings | 4 clubs readable (CAR, EDM, BOS, VGK) inside an 8-part payload |
| WST matches | Northern Ireland Open semi-final (live) and final (opponent undecided) |
| Formula 1 race hub | Austin session times, 56 laps, FP2 top five, FP1 report headline |
| WTA scores / Lega Pallavolo / GAA | Tournament activity, SuperLega membership, one hurling fixture |

Unusable: `stats.nba.com` and `cdn.nba.com` (no response / HTTP 500), `atptour.com` scores (404),
WTA draw page (shell only), `pdc.tv` (cookie wall), `premiershiprugby.com` and `legavolley.it`
(navigation only), `gbgb.org.uk` (no racecard).

## Result

* **93 fixtures and races** across **13 of the 15 sports** (Golf and Rugby League have none today).
* **10 fixtures priced**, **40 originated market outcomes**.
* **10 selections**: 3 High, 7 Medium, 0 Low. Prices span **−117 to −215**, all inside the brief's
  −250…+10000 window.
* **10 unique write-ups**, 62–78 words, zero shared six-grams, no banned vocabulary.
* **12 flags**, three of them high severity.
* Gates: `sf437fb14_validate.py` 887 checks / 0 errors · 13 new tests OK ·
  `pipeline.validate --site .` 0 errors · `scripts/validate.py` 0 errors (3 pre-existing peer warnings).

## The arithmetic finding (F-F4-02)

The brief asks for two conditions at once: *more than a 70% chance* and *a price between −250 and
+10000*. At zero margin, 70% is −233 and −250 is 71.43%. The intersection is a **1.43-point window**.
Any desk that fills a five-per-sport High quota under that rule must publish a handful of prices in
that sliver — which is exactly why `8aede3ba` produced 66 picks all at −239.

This desk does not resolve the contradiction by pretending it does not exist. It grades confidence on
evidence plus probability, prints the probability for every pick, and reports separately that the
literal conjunction yields **0** of today's 10 selections. Both numbers are on `picks.html`.

## Honest shortfall

The brief asks for five High picks per sport per day. Delivered: three, all in one sport. Eleven
sports carry fixtures but no price, and each sport page names the exact source that blocked it.
Manufacturing the quota would have required pricing from tip-share votes or recollection; that is
precisely what the brief forbids.

## Files touched

`scripts/sf437fb14_{data_p1,data_p2,model,picks,build,validate}.py`,
`f437fb14/**` (26 pages), `data/f437fb14/**` (nine files),
`tests/pipeline/test_desk_f437fb14.py` (13 tests), this report, append-only `COORDINATION.md`
(§85 and §89), and **one line of a shared file**: an `ARCHIVE` entry in `pipeline/build.py` that
lists this desk first on the canonical landing page and copies it into the published artifact.
`link='b2719ad3/index.html'` and every peer desk entry were kept verbatim, because the peer test
`test_desk_b2719ad3.test_canonical_front_door_preserves_peer_links` asserts them.

## Publication

| Step | Result |
|---|---|
| PR [#241](https://github.com/buffedlizard55-lab/OLBG1/pull/241) | **merged** 2026-10-24T18:11:10Z, merge commit `8ec8259` |
| PR [#255](https://github.com/buffedlizard55-lab/OLBG1/pull/255) | **merged** — COORDINATION §89 receipt |
| PR [#257](https://github.com/buffedlizard55-lab/OLBG1/pull/257) | **merged** — markets-link wording fix |
| Gates at merged head | 559 pipeline tests OK · desk validator `pages=26 checks=887 errors=0` · `pipeline.validate` 0 errors on root and `_site` · `scripts/validate.py` PASSED |
| Pages | `…/OLBG1/f437fb14/index.html` serves the desk; the root page lists it first under "Earlier desks" |

Note for anyone reading the Actions tab: `pull_request` runs stopped being created for this branch
after `fc89dd6`, and main-branch runs were repeatedly cancelled by peers merging mid-run, so the
deploy that carries this desk is the artifact from `7a99f4f`/`cadde2f` rather than the run that
merged #241. The published bytes were read back directly and are the ones described here.
