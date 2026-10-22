# Session `424375b4-olbg1` — T424375B4 independent live desk (22 Oct 2026, evening)

**Branch:** `arena/424375b4-olbg1` (pinned; this session's work and integration branch per
COORDINATION.md §0.2). **Claim:** T424375B4, board row + §60, pushed at 21:55Z-ish before
deliverable work (§0.3). **Harvest window:** 2026-10-22T20:55Z–21:10Z.

## 1. What this desk is

A strictly namespaced live desk (`424375b4/`, `data/424375b4/`, `scripts/s424375b4_*.py`)
that:

1. reverse-engineers the 17 in-scope OLBG sport hubs live (discovery only);
2. verifies every included fixture and every prose fact against the governing body's
   own surface (class A) or an official-URL excerpt where the publisher serves a
   cookie-consent shell (class B, flagged);
3. originates zero-vig experimental fair prices from official records only
   (log5 + Beta(2,2) shrinkage; paired-rate Poisson score markets where official
   scoring rates exist);
4. grades confidence with the brief's literal High band (p ≥ 70% **and** the
   unrounded fair price inside −250…+10000 **and** class A/B evidence **and** a
   written prediction), publishing every 70%+ favourite beyond −250 as a
   disclosure instead of hiding it;
5. writes unique ≥30-word hand-made predictions naming the selection and the
   participants, using only facts read from official pages this session;
6. publishes a 29-page dashboard with a Flagged for Review page and a repo audit.

Scope exclusions honoured: soccer/football, American football, boxing, UFC/MMA,
hurling, horse racing, cycling, specials. No root canonical files, `pipeline/**`,
`data/current/**`, `README.md`, `assets/**`, `sports/**` (repo root) or any other
session's desk was edited.

## 2. Live OLBG discovery (hub reads 20:56–20:57Z)

| Hub | State at harvest |
|---|---|
| Tennis | 14 upcoming match-ups (WTA + ATP mix) |
| Basketball | 11 events (NBA 5, EuroLeague 3, Brazil NBB 3) |
| Rugby Union | 15 events (Pro D2, Top 14, URC, Premiership) |
| Ice Hockey | 15 events (NHL 12, Denmark 2, Austria 2 partial) |
| Handball | 15 events (France/Germany/Spain/Denmark/international) |
| Volleyball | 14 events (Brazil, Poland, Italy, Germany, Austria, Finland) |
| Darts | 8 European Championship R1 ties + 2 anteposts |
| Cricket | 4 match-market events + 5 anteposts |
| Gaelic Football | 5 club fixtures + 1 antepost |
| Baseball | 1 event (World Series G1) |
| Motor Racing | 1 race + 2 anteposts |
| Golf | 1 tournament outright |
| Rugby League | 3 anteposts only (no matches) |
| Snooker / Aussie Rules / eSports / Greyhounds | "No tips found." |

OLBG tip shares are votes and never entered a price (flag F-14). OLBG start labels
are internally inconsistent across sports and are never used as start times (F-01).

## 3. Official verification performed (source ledger on the site)

Class A bodies fetched and read this session (26 reads total on `sources.html`):

* **NHL** `api-web.nhle.com` schedule 2026-10-22 (12 games, exact `startTimeUTC`,
  embedded third-party price snapshots) and standings stamped
  `standingsDateTimeUtc 2026-10-22T20:57:30Z` (all 32 clubs: W-L-OTL, points,
  GF/GA, home/road, L10, streaks).
* **MLB** `statsapi.mlb.com` schedule 10/23 (World Series Game 1, gamePk 849805,
  `ifNecessary="N"`, probable pitchers Martinez / Misiorowski) and 2026 regular
  standings (Rays 98-64, 736/650).
* **URC** `stats.unitedrugby.com` match-centre Round 4 (8 fixtures, local times,
  match ids) and the official table (all 16 clubs, W-D-L, PF/PA, form).
* **LNR** `prod2.lnr.fr` J8 calendar + table (8 fixtures, 16 clubs) and
  `top14.lnr.fr` J7 calendar + table (7 fixtures, 14 clubs).
* **Euroleague Basketball** standings page (all 20 clubs, GP/W-L/PTS+/PTS−/L10).
* **ATP Tour** `scores/current` (six R16 results read verbatim, plus ATP's own
  Lyon news line) and **WTA** `scores` hub (this-week tournament identities).
* **Formula 1** `formula1.com/en/racing/2026/united-states` (session schedule,
  56 laps × 5.513 km = 308.432 km, race 25 Oct 16:00 track time).

Class B (official URL + search-engine excerpt of that exact URL; cookie wall to the
fetcher; flagged F-04): PDC schedule + preview articles; four nba.com surfaces
(event-details JSON-LD for CLE@PHI, Starting-5 news, schedule release, Knicks team
page / NYK@BOS game page).

Class C (OLBG discovery only, all official cells blank): 55 rows across tennis
(13 upcoming), handball (15), volleyball (14), European ice hockey (4), Brazil NBB
(3), cricket (4), GAA (5), golf (1), rugby-league anteposts (3), F1 anteposts (2),
CHI@MIL and 2 ATP-adjacent pairings. Every one is on the Flagged page with an
official recheck link.

## 4. Origination and grading results

* **117 listings** harvested; **40 priced**; **77 unpriced** with reasons.
* **771 originated market prices** (40 winner prices + 731 handicap/total research
  model lines where official scoring rates exist). Basketball line/total markets are
  withheld (no official scoring-variance input — methodology page).
* Winner tiers: **2 High**, **8 out-of-window favourites (p ≥ 70%)**, **14 Medium**,
  **16 Low**.
* **High (brief band, fair price):** Vegas Golden Knights (70.0%, −233, at STL) and
  Toulouse (70.0%, −233, v Perpignan). Both sit exactly at the p = 0.70 boundary;
  the tier test uses the probability rounded to six decimals (the binary-noise
  lesson logged by TD7D19).
* **Out-of-window disclosures:** Provence 88.7% (−788), Aurillac 78.9% (−375),
  Valencia 77.8% (−350), Pau 77.8% (−350), Glasgow 76.4% (−324), NY Islanders
  75.7% (−311), Brive 75.4% (−306), Minnesota 72.7% (−267), Clermont 72.7% (−267),
  Boston Bruins 71.6% (−252). The NHL rows additionally publish the official
  feed's own price snapshot (e.g. BOS −152…−156, MIN −205…−215) so both readings
  of the −250…+10000 window are visible.
* **21 predictions/previews**, every one ≥30 words, unique, selection named, facts
  cited to `sources.html` ids: 16 graded (top five each for ice hockey, rugby
  union, basketball + Toulouse as the sixth rugby case) and 5 unpriced previews
  (MLB WS G1, three PDC ties, F1 USA GP) that name a selection or explicitly
  withhold one and are never graded.

## 5. Shortfalls (honest, not filled)

The brief aims for five predictions per covered sport. Verified depth allowed five
for ice hockey (NHL), rugby union and basketball; the rest are documented on
`coverage.html`:

* tennis 13 listings, 0 verified pairings → 0 predictions (F-09/F-10);
* darts 8 verified ties, no rankings body read → 3 named ungraded previews (F-04);
* handball 15, volleyball 14, European hockey 4, Brazil NBB 3, cricket 4, GAA 5,
  golf 1, rugby league 3 → 0 predictions (F-11/F-12);
* baseball 1 → preview only (Brewers record gap F-03);
* motor racing 1 race → preview only (field model withheld).

## 6. Irregularities flagged (16 flags, `flagged.html`)

Highlights: F-03 high — Brewers 2026 record unread, all MLB prices withheld
including the brief's headline fixture; F-09/F-10 high — the 14 OLBG tennis
match-ups cannot be confirmed on official draw surfaces this session (WTA pages
render client-side; ATP draws not printed on the scores page); F-11 high — cricket
boards unread (nzc.nz/fixtures 404 at fetch time); F-04 medium — pdc.tv cookie
wall (class B handling); F-01 medium — OLBG time-label inconsistency; F-02 low —
NHL feed embeds third-party odds snapshots (published as observation bands, not as
asserted offers); F-08 low — URC publishes venue-local times only and Europe's DST
change falls inside the window, so UTC cells stay blank; F-15 — EuroLeague
game-centre rows would not render (starts blank, records still official).

## 7. Repo audit (line-by-line scope, `repo-audit.html`)

Seven findings (1 high, 2 medium, 2 low, 2 info): stale in-progress/queued board
rows past the 60-minute rule; duplicate task id T63; duplicate section numbers;
three open root-navigation requests; oversized published pages; canonical gates
green at this checkpoint; this session's footprint confined to its claimed scope.

## 8. Gates run at this checkpoint

| Gate | Result |
|---|---|
| `python3 -m unittest discover -s tests/pipeline` | 135 tests, OK |
| `python3 -m unittest discover -s tests -p 'test*.py'` | 38 tests, OK |
| `python3 -m pipeline.validate --site .` | 0 errors |
| `python3 scripts/validate.py` | PASSED (1 pre-existing warning in `f7fa77fc/flagged.html`) |
| `python3 scripts/s424375b4_validate.py` | VALIDATION PASSED — 1183 checks, 0 errors |
| `python3 -m pipeline.build --out _site` + `pipeline.validate --site _site` | see receipts below |

## 9. Verification of this desk's own rows

Every row on `matches.html` carries at least one source id and an official link
(enforced by `s424375b4_validate.py`). No value was inferred: where an official read
did not happen, the cell is blank and the row is listed on `flagged.html` with the
official URL to recheck. Model outputs are labelled experimental fair prices
everywhere; the word "verified" is used only for class A/B reads described in the
ledger.

## 10. PR / merge / Pages receipts (appended post-merge)

*(filled in after merge — see COORDINATION.md §60)*
