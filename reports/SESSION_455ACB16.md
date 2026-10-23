# 455acb16 — corrected evidence-first research release

**Dashboard:** [455acb16/](https://buffedlizard55-lab.github.io/OLBG1/455acb16/)
**Review register:** [Flagged for Review](https://buffedlizard55-lab.github.io/OLBG1/455acb16/flagged.html)
**Evidence:** [field ledger](https://buffedlizard55-lab.github.io/OLBG1/455acb16/verification.html) · [retained excerpts](https://buffedlizard55-lab.github.io/OLBG1/455acb16/sources.html)
**PR:** [#196](https://github.com/buffedlizard55-lab/OLBG1/pull/196)

## Status and scope

This is an independently checked **partial** research release, not completion of the full worldwide/daily-prediction brief. The 15 requested categories are Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball and Rugby League. Australian Rules and eSports are not included.

Gaelic Sports contains **Gaelic Football and Hurling**, under separate competition identities. A fresh read of [OLBG's Hurling page](https://www.olbg.com/betting-tips/Hurling/26) explicitly states that its Gaelic Sports competitions cover both. This corrects the inherited football-only scope assumption; it does not add a sixteenth category. Shinty/camogie hybrid events are not silently treated as hurling matches, and football/hurling scoring data are not pooled.

All work is on the assigned `arena/455acb16-olbg1` branch. Changes are confined to this namespace and append-only/session-owned coordination entries. Shared root pages, canonical pipeline/workflows, other desks and their inputs are preserved.

## Correction of the initial draft

The first draft **copied the 496eaf02 snapshot and prose, changed its observation time, and incorrectly asserted fresh official checks**. Its 81-fixture / 51-High / 51-prediction counts, new timestamps and calibration claims are withdrawn. The initial PR description and its first implementation-receipt text are superseded, not evidence. A comment was added to PR #196 and it was made a draft while the replacement was built.

The replacement does not import prior fixture facts, statistical values, prices or prose. Each accepted non-null sporting field is taken from an actual new official-source read. The source observation window is **2026-10-23T21:34:10Z–21:44:36Z**, bracketed by actual workspace UTC clock checks around the retrieval work. These are honest shared observation bounds, not fabricated per-request timestamps. Builds retain them unchanged.

`observations.json` holds selected excerpts and field projections transcribed from `fetch_page` Markdown. They are **not original HTTP response bodies**, and the tool did not provide per-request HTTP headers/statuses for successful reads. Hashes prove retained-content integrity, not external truth or transport authenticity. The one explicit failed NBA JSON attempt is recorded as a failure, never as a zero-game response.

The attempted peer syntax repair was also superseded during rebase: upstream fixed `se58210b8_predictions.py`. This session restores the exact upstream bytes and does not claim the peer fix or retain duplicated prose.

## What the replacement contains

| Metric | As-of replacement result |
|---|---:|
| Retained listings | 84 |
| Match listings / bracket slots | 77 |
| Field-event/session listings | 7 |
| Exact upcoming listings with supported status | 18 |
| Calendar/time/status-gap listings | 64 |
| Priced matches | 18 |
| Originated markets / outcomes | 38 / 76 |
| Low / Medium / High winner preferences | 18 / 0 / 0 |
| Approved High predictions | 0 |
| Newly written Low research notes | 6 |
| Accepted statistical records | 29 |
| Retained source observations | 49 |
| Successful official-page observations | 29 |
| Failed official-feed attempt | 1 |
| OLBG discovery/policy observations | 19 |
| Published review entries | 97 |
| Globally complete categories | 0 of 15 |

These counts are explicitly dated. A later rebuild or browser expiry can withhold estimates but cannot refresh a source observation. "Match listings" includes two unfilled snooker bracket slots, not 77 fully confirmed playable fixtures. A field calendar is not a complete racecard or a fabricated head-to-head.

The five-per-sport **daily High** target has a shortfall of **75**. Five distinct in-band NHL winner estimates and four MLB winner estimates can form a Low research shortlist; other categories lack the evidence/implementation needed to price them. Multiple totals on one game are not counted as extra matches. No High predictions are invented to reach the quota.

## Actual source reads and important findings

The full ledger, observed bounds, chunk indices, selected excerpts, hashes and field projections are in [`data/455acb16/observations.json`](../data/455acb16/observations.json).

- **NHL:** [schedule API](https://api-web.nhle.com/v1/schedule/2026-10-23), chunks 0–3, supports the two league-date-23 and twelve league-date-24 games; later week dates are not claimed complete. [Official standings](https://www.nhl.com/standings/2026-10-23/wildcard), both chunks, supports the 27 paired team records used here. Overtime defeats count as defeats, not half-wins or points percentage. The [Suzuki injury report](https://www.nhl.com/news/montreal-canadiens-nick-suzuki-injury-status-update-october-22-2026) is dated 22 October and is not misrepresented as a complete current lineup check. A selected [24 October scoreboard excerpt](https://www.nhl.com/scores/2026-10-24) supports the Pastrnak context in one Low note.
- **MLB:** [filtered schedule](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-30&fields=dates,date,games,gamePk,gameType,season,gameDate,status,detailedState,startTimeTBD,teams,away,home,team,id,name,venue,seriesGameNumber,description,ifNecessary) supports World Series Games 1–6. Games 5 and 6 have `ifNecessary=Y` and are not priced; Game 6 is outside the exact rolling horizon. [Official regular-season standings](https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason&fields=records,standingsType,teamRecords,team,id,name,season,gamesPlayed,wins,losses,runsScored,runsAllowed,lastUpdated), selected team records in chunks 0 and 2, supports both 162-game run aggregates. The Brewers' original provider update date is retained, not relabelled as new playoff form.
- **Tennis:** official [Almaty](https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule), [Brussels](https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule), [Ningbo order of play](https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf) and [Osaka order of play](https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf) support 12 singles/doubles listings. "Not Before" is not an exact start. The new Ningbo sheet names **Fernandez–Bouzkova**, not Fernandez–Kostyuk; the [draw](https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf) contains a Kostyuk right-wrist injury entry. Osaka lists **Li–Krueger** and **Boulter–Siniakova**, not Li–Boulter. Source abbreviations and the Ningbo sheet's "Laylah" spelling are preserved with an explicit identity note. Friday [Lyon results](https://www.atptour.com/en/scores/current/lyon/496/daily-schedule) were not reconstructed into inferred Saturday pairings.
- **Darts:** [PDC hub](https://www.pdc.tv/tournament-hub/10870), sporting content in chunk 6, supports eight last-16 pairings dated Saturday 24 October. No timezone label, individual leg rates, updated rankings or current market quote was established. The long consent notice was not treated as a denial to work around.
- **Snooker:** [WST matches](https://www.wst.tv/matches/), chunks 2–3, identifies Wilson–Craigie plus two scheduled bracket slots. Quarter-final results/live scores are separated from pre-match opportunities. Unknown semi-final/final participants and unlabelled clocks remain blank.
- **Rugby Union:** the official [URC season fixture publication](https://www.unitedrugby.com/latest/news/2026-27-fixtures-in-full/) supports five Saturday Round 4 matchups and their published regional clocks. It is not a fresh match-status feed; the Leinster–Munster venue is TBC and remains null. No rating or home advantage is invented.
- **Cricket:** [NZC fixtures](https://scoring.nzc.nz/fixtures), selected first chunk, supports two T20I and three Ford Trophy pairings with venues. Its extracted clocks lack timezone labels; no UTC conversion is inferred from the host country's location. Other cricket competitions remain incomplete. ESPNcricinfo is not promoted to ICC authority by an inherited source label.
- **Handball:** [LNH calendar](https://www.lnh.fr/liquimoly-starligue/calendrier) resolves to the Daikin StarLigue page and lists Nantes–Chambéry, Saint-Raphaël–Paris and Montpellier–Saran. Friday score-bearing rows are not future selections. No unobserved venue/timezone is filled.
- **Volleyball:** the [Lega calendar](https://www.legavolley.it/calendario/?idCampionato=999), chunks 3–5, supports six Round 2 matches and the explicitly rescheduled Perugia–Padova game. Calendar `0-0` placeholders are not played results or a current state feed. The [PlusLiga request](https://www.plusliga.pl/games.html) resolves to TAURON Liga while carrying men's team names; that identity conflict is flagged and no Polish price is imported from it.
- **Gaelic Sports:** [Munster calendar](https://munster.gaa.ie/fixtures/events-calendar/), both chunks, supports three football county finals and the Limerick hurling final with venues. All quoted clocks remain source calendar text rather than inferred UTC. Full current form, availability and club strength are missing.
- **Golf:** the official [PGA schedule](https://www.pgatour.com/schedule), chunks 4–5, supports the current Bermuda tournament and next Mexico event. The former has an R2 Complete widget. Neither is turned into an invented two-golfer matchup; complete fields/tee times/withdrawals and current betting availability are unknown.
- **Greyhounds:** the [2026 GBGB Category One calendar](https://www.gbgb.org.uk/racing/open-races/2025-category-one-schedule/) supports three finals/event calendars, not full racecards, trap allocations, runners or scratchings. Its URL retains `2025`, while its heading explicitly says `2026`. Friday's event is not automatically declared still upcoming. The [open-races filter page](https://www.gbgb.org.uk/racing/open-races/) did not expose individual cards.
- **Motor Racing:** the official [F1 US GP hub](https://www.formula1.com/en/racing/2026/united-states) supports qualifying/race dates. Its My time / Track time switch is ambiguous in extraction, so exact UTC and all field prices stay blank. Two sessions of one GP are not two independent matches toward a quota.
- **Basketball:** [NBA games](https://www.nba.com/games?date=2026-10-23) returned a card-rendering error; the [public JSON attempt](https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json) failed HTTP 500. The [official newsletter](https://www.nba.com/news/starting-5-october-23-2026) supplies only three pairings from the 12-game Friday slate; nine remain unknown. The [EuroLeague Round 7 report](https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/) contains completed games and does not substantiate the previous draft's Saturday pairings.
- **Rugby League:** official [men's](https://www.nrl.com/draw/?competition=131&round=2&season=2026) and [women's](https://www.nrl.com/draw/womens-rugby-league-world-cup/2026/round-2/) Round 2 pages support seven schedule listings; Tonga–Lebanon and Samoa–Wales are already full-time and excluded. The site positions are not international strength ratings, and unlabelled clocks are not converted to UTC.

All 15 main OLBG sport hubs, Hurling, NHL and MLB routes were actually read. The extraction exposed no live event-card rows. The cause is **unknown**; there is no unsupported assertion that OLBG has no events, suppresses all zero-tip events, or uses a particular location clock for these empty cards. [OLBG robots](https://www.olbg.com/robots.txt) restrictions on private API/storage paths and Python-urllib were read. No bypass, agent impersonation, proxy or hidden feed was used.

## Pricing, confidence and prose

- NHL winner: independent Beta(2,2) record shrinkage and log5 on compatible season records; no neutral/default rating and no guessed home or injury adjustment.
- MLB: paired official regular-season run rates with independent Poisson scores, conditioned on no tied final score. Fixed ±1.5 run handicaps and a three-point half-run totals ladder. No starter/park/lineup/bullpen/weather/postseason adjustment is claimed.
- Decimal = `1/p`; American is derived from the unrounded chance and rounded only for display. The target-band flag uses unrounded prices, not clipped or rounded display values.
- Every price expires at the earliest fixture observation deadline, statistical deadline or scheduled start. Both the browser and rebuild path withhold expired estimates. With JavaScript disabled, estimates are hidden, since runtime freshness cannot be enforced.
- Every unmatched market family has a blank price and a specific missing-input/settlement reason. There are 504 per-listing market-family assessments, not a claim of 504 currently available offers.
- **No measured held-out calibration, complete recent-history/availability checks, eligible actual quote or confirmed OLBG tip-submission evidence exists for a higher confidence tier here. All outputs remain Low.** A 70%+ chance alone is not High, nor is a 62% threshold a substitute for calibration.
- Six independently written, source-linked Low research notes have at least 30 words and contain none of the user's prohibited internal-processing terms. No copied prose is retained. There are **zero approved High write-ups**. Missing form/history/injury facts are not invented to fill the daily target.

## Repository review

The read-only inventory parses every tracked JSON and Python file for syntax and records seven selected file/line semantic findings with SHA-256 and revision-specific GitHub links at [Repository review](https://buffedlizard55-lab.github.io/OLBG1/455acb16/repo-audit.html). It is **not** independent factual recertification of every sentence in the many historical desks. The canonical row-occurrence audit remains separate.

The important findings are the inherited 62% High threshold, the two WTA pairing conflicts, misleading media provenance, a stale canonical snapshot, source-code/generated-data consistency and this session's own withdrawn restamping. External sporting comparisons point to actual retained reads. Hashes alone do not verify content.

## Build and validation

```sh
python3 scripts/se455acb16_build.py
python3 scripts/se455acb16_validate.py
python3 -m unittest discover -s tests/pipeline -v
python3 -m unittest discover -s tests -p 'test*.py' -v
python3 -m pipeline.validate --site .
python3 scripts/validate.py
python3 -m pipeline.build --out _site
python3 -m pipeline.validate --site _site
NODE_PATH=/home/user/.cache/olbg-browser/node_modules node scripts/se455acb16_browser.cjs
NODE_PATH=/home/user/.cache/olbg-browser/node_modules node tests/pipeline/browser.cjs
```

`--at` on the desk builder is a deterministic evaluation clock, never a source observation time. `--out` writes a repository-shaped scratch tree and never changes original observation times. The current desk manifest contains 28 pages, including all 15 category subpages. No production JS/CSS/font dependency calls the network.

Observed gates so far: **31 desk tests**, **359 pipeline tests**, **38 preserved tests**, and the dedicated real-Chromium desktop/mobile/project-prefix/filter/odds/timezone/CSV/evidence-anchor/start-expiry/no-JavaScript suite pass. The combined-tree root and staged canonical validators passed with zero errors. The historical relative-link gate passed with zero errors and three existing archived warnings (not an endorsement of historical sporting claims). Both the dedicated desk browser suite against `_site` and the canonical real-Chromium suite passed. The canonical build produced 94 canonical pages plus preserved independent desks, with this desk and its evidence JSON present. Publication/CI receipts follow in COORDINATION.md.

## Remaining limitations and publication

Full worldwide enumeration, every live available market, verified bookmaker odds, sport-specific calibrated pricing for all matches, complete current player/form/history/injury context, five supported High picks per sport daily, and fully automated 15-sport collection remain **not achieved**. They are published as review items, not concealed behind fabricated rows or confidence tiers. This selected import has automatic expiry, **not automatic collection**; the repository's existing canonical scheduled collectors are separate and partial.

**Published:** [PR #196](https://github.com/buffedlizard55-lab/OLBG1/pull/196) merged at 2026-10-23T22:10:52Z as `4332f34856c9411458416c9c32e0ee8b138e4e52`. [PR check run 40031731758](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/40031731758) passed. [Production run 40031925014](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/40031925014), including validation job 120682063906 and Pages deployment job 120682629018, succeeded.

**Live content independently checked at 22:13 UTC:** the deployed dashboard, summary JSON and Flagged for Review page served the expected corrected content. Live summary: 84 listings, 18 Low books, 38 markets, 76 outcomes, zero Medium/High, six Low notes and 97 flags; source bounds still 21:34:10–21:44:36Z. The live flags page includes the explicit initial-draft withdrawal and WTA corrections. Pages' separate legacy status was building while the tested artifact was already serving; no hosting setting change is claimed.

A small presentation follow-up labels KPIs as-of-build and sorts the two executive tables by estimated chance, with a regression test. It does not re-fetch or restamp any source. Final follow-up receipts are in COORDINATION.md §T455ACB16.


## Publication follow-up and final record semantics

[PR #216](https://github.com/buffedlizard55-lab/OLBG1/pull/216) merged at 2026-10-23T22:19:22Z as `26630eb4776a42c5bcbef3ada5e2194e298dab39`. [Production run 40032844369](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/40032844369) succeeded, including validation job 120685073687 and Pages deployment 120685616979. Live read-back confirmed the as-of-build label and correctly ranked executive tables.

The final check removes a common-schema MLB `ot_losses: 0` normalization: NHL's OTL category is not an official MLB statistic. It is omitted from accepted MLB inputs and from their W–L display, rather than asserted as a sourced zero. An injected MLB OTL zero is now rejected by validation. NHL's actual OTL fields are preserved. No probability, price, source observation bound or confidence tier changes. This is a projection/display correction over the retained read, explicitly noted in the source ledger—not a newly fetched source. The desk has 33 regression tests; the combined 372-test suite passes at this checkpoint.


## Final integration receipt

[PR #220](https://github.com/buffedlizard55-lab/OLBG1/pull/220) merged at 2026-10-23T22:25:39Z as `94aca1268ecaf0b34ccbd333b03958a65f746eb4`. PR run 40033404733 passed. Direct push runs were superseded by the next main update; [production run 40033553452](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/40033553452) on descendant `525db628dda2874c83dbbc666bada00b1ba15a5e` succeeded, including Pages job 120688000592. GitHub compare confirmed the descendant contains the final integration.

At 22:28 UTC the live analysis page independently served the corrected NHL/MLB record headings and MLB W–L display; live summary JSON confirmed 84 listings, 18 Low books, 38 markets, 76 outcomes, zero Medium/High, six Low notes and 97 flags. Source bounds remain 21:34:10–21:44:36Z. Publication is complete; global/daily-confidence/automation limits remain openly flagged, not marked achieved. No source or price changes are part of this receipt.


Review-locator integrity is separately enforced: each published file hash and line locator is computed from the exact committed revision used by its GitHub URL, not from an uncommitted working-tree version. The regression gate compares all seven findings against `git show` at that declared revision. This review-metadata correction changes no sporting observation or price and does not make a whole-archive factual-certification claim.
