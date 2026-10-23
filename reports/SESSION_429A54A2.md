# Session 429a54a2-olbg1 — T429A 15-sport desk, 23 October 2026

**Snapshot:** 2026-10-23T16:45:00Z · **Desk:** `/429a54a2/` (25 pages) · **Data:** `data/429a54a2/`
**Branch:** `arena/429a54a2-olbg1` · **Task:** T429A (COORDINATION.md §67)

## What the brief asked for

A full, updated match list from OLBG for exactly fifteen sports; our own lines for every match with
the winner called and a Low/Medium/High label; every available market investigated; unique,
non-robotic predictions of at least 30 words for high-confidence picks, carrying verified team, player,
form, recent history, match statistics and injuries, with the selection obvious; the high-confidence
work concentrated in the −250…+10000 price window; five high-confidence picks per sport per day
where possible; a clean GitHub Pages dashboard with a category subpage each and a Flagged for Review
page; line-by-line verification with official links and no invention.

## What shipped

| Metric | Value |
|---|---:|
| Fixture rows | **96** |
| Priced fixtures | **19** |
| Originated markets | **188** |
| High picks inside −250…+10000 | **3** |
| High probability but priced shorter than −250 (disclosed) | **5** |
| Medium | **2** |
| Unverified (blank, flagged) | **7** |
| Elapsed before snapshot (never priced) | **6** |
| Predictions (≥30 words, one per priced High/Medium) | **10** |
| Review flags | **20** |
| Repository findings with file:line | **8** |
| Pages | **25** (10 desk pages + 15 sport pages) |

## The fifteen sports and what was actually read

| Sport | Rows | Priced | Official anchor |
|---|---:|---:|---|
| Golf | 2 | 0 | PGA Tour leaderboard, Butterfield Bermuda Championship (R2 in progress) |
| Volleyball | 6 | 0 | VBL official schedule/table; SKRA official PlusLiga fixtures; LegaVolley calendar; Flamengo official preview |
| Rugby Union | 13 | 0 | URC match centre; LNR Pro D2 J8; Bath and Gloucester official team news; Newcastle Red Bulls team news; JRFU team announcement |
| Cricket | 5 | 0 | Cricket Australia match centres; BCCI fixtures |
| Snooker | 4 | 0 | WST match centre |
| Darts | 8 | 0 | PDC news hub / European Championship order of play |
| Baseball | 2 | 0 | MLB StatsAPI World Series schedule (gamePk 849805, 849802) |
| Gaelic Sports | 5 | 0 | Cork GAA, Galway GAA, Kilkenny GAA, Munster GAA |
| Greyhounds | 3 | 0 | GBGB race report and results API |
| Tennis | 5 | 0 | WTA official order-of-play PDFs (Ningbo 2092, Osaka 405) |
| Motor Racing | 1 | 0 | Formula1.com race page and 2026 drivers' standings |
| Handball | 9 | 8 | LNH official calendar and classement; FC Barcelona official calendar |
| Ice Hockey | 12 | 11 | api-web.nhle.com schedule and standings (standingsDateTimeUtc 16:16:15Z) |
| Basketball | 15 | 0 | NBA.com games page (12 fixtures); EuroLeague game centre (3 elapsed) |
| Rugby League | 6 | 0 | International Rugby League match pages |

## Why only two sports are priced

A price needs a quantitative official input for **both** sides. That existed for ice hockey (the NHL
publishes points percentage and goals for/against per club) and for French handball (the LNH publishes
points, wins, draws, losses and goals for/against for all sixteen clubs). Every other sport had
fixtures but no comparable input that was read this session:

* **Tennis** — the WTA order of play and main draw give the seeding and ranking order, but no rating
  scale or serve/return data; a rank-to-probability mapping would be an invention.
* **Cricket** — fixtures and venues, no team ratings.
* **Basketball** — twelve NBA fixtures with 1–0 / 0–1 records (a one-game sample), and three
  EuroLeague games that had already tipped.
* **Rugby Union / Rugby League / Gaelic / Snooker / Motor Racing / Golf / Volleyball** — line-ups,
  squads, frame results, standings or leaderboards, but no two-sided performance input.

Those rows are published with blank price and selection and an explicit reason, per the brief's
instruction to leave unconfirmed values blank and flag them.

## The −250…+10000 window, stated plainly

−250 is 1.400 decimal, which is 71.43%. A selection with a probability above 71.43% *cannot* be priced
inside the band. The overlap between "above 70%" and "inside −250…+10000" is therefore only
**70.00%–71.43%**. This desk publishes both readings:

* **3 High picks inside the band** — Montreal −250 (71.43%, on the boundary), Carolina −245 (71.05%),
  Selestat −240 (70.55%).
* **5 High-probability picks outside the band** — Tampa Bay −286, Vegas −333, Limoges −359,
  Nantes −462, Montpellier −378. They are labelled "High · out of band" and are never described as
  in-window.
* The five-per-sport-per-day aim is **not met and not invented**. It is reported as unmet on the
  High-confidence page and in the flagged register.

## Predictions

Ten predictions, one for each priced High or Medium selection, 70–95 words each. Each names the
selection explicitly ("Montreal Canadiens moneyline", "Selestat to beat Caen"), states the official
table or record the claim rests on, and links the page that was read. None contains the internal
words used by the price engine, and a validator gate rejects any six-word phrase shared between two
predictions. No injury claim is made for a match where no injury list was read; where injuries were
read (Gloucester, Newcastle, Sale, Bath, the PDC withdrawal), they are published on those rows and in
the flags rather than being attached to a prediction without a price.

## OLBG reverse-engineering findings

* Fifteen in-scope sport routes were read: Golf/5, Volleyball/21, Rugby_Union/9, Cricket/7, Snooker/8,
  Darts/15, Baseball/12, Gaelic_Football/25, Greyhounds/28, Tennis/3, Motor_Racing/14, Handball/20,
  Ice_Hockey/13, Basketball/4, Rugby_League/10. Hurling/26 was read only to confirm the exclusion.
* A hub shows one most-tipped selection per event with a tip count and rounded share; the event page
  adds every market and every tip. That is discovery, and a tip share is a vote count, not a probability.
* Hub times carry **no zone label** and disagree with official schedules by three to four hours
  (F-429A-01). Example: OLBG "Today 14:45" for Clayton v Springer against a 20:30 CEST PDC slot.
* Two hubs were empty or ante-post-only during live competition: golf returned "No tips found" while
  a PGA Tour event was on the course, and rugby league listed only 2027 outrights while the Rugby
  League World Cup was in Round 2.

## Verification and gates

* `scripts/s429a54a2_validate.py` → **VALIDATION PASSED**, 96 rows / 25 pages / 10 predictions / 0 errors.
* `tests/pipeline/test_desk_429a54a2.py` → 6 tests OK.
* `python3 -m unittest discover -s tests/pipeline` → OK.
* `python3 scripts/validate.py` → PASSED, 0 errors, 3 pre-existing `f7fa77fc` warnings.
* `python3 -m pipeline.validate --site .` → 0 errors.
* Whole-desk link check: every internal link resolves; every table row carries an external source link.

## Limits, stated for the record

No worldwide fixture census, no calibration, no bookmaker quote, no availability, no edge. The NHL
and LNH engines use no home edge and no market input. The files of other sessions were read but not
edited; the eight repository findings are published with file and line and left for the integration
owner.

## Publication receipts

* **PR #173** — https://github.com/buffedlizard55-lab/OLBG1/pull/173 — base `main`, head
  `arena/429a54a2-olbg1`. Pre-merge CI `Evidence, model, site and browser gates` **SUCCESS**
  (run 39991274191); the Pages publish job correctly skipped on the PR event. **Merged
  2026-10-23T17:00:03Z** as `30775ff12c07ab3ffbeb18151b3cba92a3abf03f` without waiting for approval,
  per the brief.
* **Production run 39991436722** on `main`: validate job SUCCESS and `Publish canonical GitHub Pages`
  SUCCESS; the repository's legacy `pages-build-deployment` run 39991435745 also succeeded.
* **Live byte read-back (cache-busted, independent of the Pages API) at ≈17:26Z:**
  `/OLBG1/429a54a2/index.html` served this merge's own content — the KPI strip 96 rows / 19 priced /
  3 High in band / 5 High outside band / 2 Medium / 10 predictions / 6 unverified / 20 flags, the three
  in-band cards (Montreal −250, Carolina −245, Selestat −240) and the full table with per-row official
  links and observation windows. `/OLBG1/429a54a2/high-confidence.html` served all three ledgers
  (3 / 5 / 2) with the −250 = 71.43% arithmetic and the per-sport top-five sections.
* **Wording correction after that read-back:** the overview and match-list notices now state that the
  list is frozen at the snapshot and that a row starting after 16:45Z can pass while the reader is on
  the page, rather than implying the page re-checks status. Desk validator re-run: PASSED, 0 errors.
* **Note on this follow-up:** its own merge and deploy cannot be confirmed by the text that ships in
  it; what is confirmed above is that the merged desk artifact was the content served by GitHub Pages
  at the times read.
