# TEE3C — canonical release integrity audit

Session: `ee3c3e8f-olbg1` · branch: `arena/ee3c3e8f-olbg1` · 22 October 2026 UTC.

## Scope and honest limits

This is a follow-up integration of the existing evidence-first dashboard, not another parallel betting desk. The baseline is `d9df68e47404e40768b1067b8d9aecaeb713cc27`. The coordination claim was committed and pushed before implementation. The initial pull of the new Arena branch failed because no remote branch existed yet; `git pull --rebase origin main` then succeeded, followed by the claim push. No branch switch, conflicting owner edit, legacy-data rewrite or overwrite of archived desks was performed.

Every retained canonical fixture field is checked against its saved official observation, and generated tables are checked for source links. That is **retained-evidence consistency**, not a claim that every repository sentence or every worldwide fixture was freshly verified. The 108 imported listings, 42 accepted statistical observations and 31 official-source captures retain their original observation windows. Builds do not restamp them. Current category coverage remains partial/unverified. There are no calibrated High-confidence forecasts, verified bookmaker quotes, or complete form/player/history packages to justify the requested High write-ups.

## Reproducible findings and fixes

| Finding | Reproduction / consequence | Resolution | Official source / review target |
|---|---|---|---|
| F-257E-20 | Seven priced EuroLeague books in the baseline had a null `official_status`. A published future UTC start had effectively qualified them for pre-match pricing. | Explicit supported official pre-match status is now required. Missing, unknown and unsupported states withhold all estimates and selections. No Scheduled value is inferred. Missing status appears in the field-gap table. Existing schedule facts remain visible. | [EuroLeague Round 7 official article](https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/) |
| F-257E-21 | Browser expiry checked fixture evidence and start, but not the statistical inputs. If fixture evidence were refreshed while statistics approached their 24-hour limit, old estimates could remain displayed. | Each price book expires at the earliest of fixture expiry, start and both statistical observation deadlines. Table, market and research-note views use this deadline. An expired statistic withdraws the estimate without relabelling an independently valid fixture. Exact 24-hour statistical boundary is expired. No-JavaScript views hide estimates and explain why. | [NHL official standings](https://api-web.nhle.com/v1/standings/2026-10-21) |
| F-257E-22 | Duplicate price books were collapsed by dictionary construction; displayed totals/window flags and field references outside the expiry-source scope were not independently gated. | Reject duplicate books, KPI/coverage mismatches, unsupported rolling-window membership, extended price lifetimes and hidden expiry-source references. Future observations cannot support retrospective prices. Rendered price deadlines must agree with model books and cannot exceed fixture/start deadlines. | [NHL official schedule](https://api-web.nhle.com/v1/schedule/2026-10-22) |

The public review register contains these findings with repository locations. Its existing `F-257E-*` numbering is preserved for continuity; this session's ownership is TEE3C, not a new claim to the prior session's research.

## Official live spot checks in this session

The Arena page-retrieval tool was used directly. These were **selected excerpts**, not complete HTTP captures: no response headers, per-request exact timestamps or fresh whole-feed certification are claimed. They do not rejuvenate canonical data.

| Check actually read on 22 October 2026 | Result and scope | Official URL |
|---|---|---|
| NHL schedule, chunk 0 of 12 | First four complete game objects agreed with retained home/away IDs and names, date, 23:00 UTC start, venue and FUT state: 2026020154 Boston–Nashville, 2026020155 Toronto–NY Rangers, 2026020156 Ottawa–San Jose, 2026020157 New Jersey–Anaheim. Remainder not recertified by this spot check; `numberOfGames=12` alone is not a full row-by-row check. | [NHL API](https://api-web.nhle.com/v1/schedule/2026-10-22) |
| OLBG robots.txt, entire returned text | Confirmed `/api/` and `/storage/app/json_data/*` disallows, and Python-urllib disallow-all. Existing compliant collector policy retained. No hidden-feed circumvention attempted. | [OLBG robots](https://www.olbg.com/robots.txt) |
| EuroLeague `/game-center/2026-27/`, returned 404 page | The page extraction redirected to the official 404 page. It cannot verify current matchup status. This is not evidence of no matches. | [Attempted official route](https://www.euroleaguebasketball.net/en/euroleague/game-center/2026-27/) |
| Actual imported EuroLeague Round 7 article, chunk 0 of 3 | Returned the Hapoel–Virtus completed-game report and Thursday Efes–Besiktas preview heading. A preview is not a structured current status feed; no status or player/form value was promoted from this partial reread. | [Official article](https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/) |

## Checkpoint and verification

At the approximately 12:20 UTC local build: **108 captured listings, 17 price books, 42 originated two-way markets, 84 outcome prices, 17 Low winner preferences, 0 Medium, 0 High; 91 unpriced listings**. Those are as-of counts, not a promise that values remain current. Runtime expiry and subsequent refreshes can legitimately change them. No originated price is an available bookmaker offer.

Completed local gates:

- 113 canonical Python tests, including 18 new synthetic regression scenarios; all pass. Synthetic mutations are explicitly labelled and never published as real match facts.
- 38 preserved upstream tests; all pass.
- `pipeline.build` produces 77 canonical pages at this checkpoint; `pipeline.validate --site _site` reports zero errors. Every canonical data row has an official/project source link; internal targets/fragments resolve.
- Real Chromium desktop/mobile/project-prefix tests pass: filters, sort, CSV download, odds formats, evidence links, market search, fixture expiry, statistical expiry without fixture-state mutation, and no-JavaScript withholding.
- Historical `scripts/validate.py`: zero errors, three pre-existing archived mirror warnings (rows cite internal methodology). Its 30 historical High predictions are **not** canonical recommendations.

The new browser regression initially failed: the first edit was in the generated asset, while the builder copies `site_templates/current.js`. Corrected the source template, rebuilt, and the test passed; no assertion was weakened to bypass the behavior. Historical link validation also initially traversed ignored local Playwright HTML; browser dependencies were moved outside the repository, and the documented local install now uses an external temporary directory. No legacy validator was changed to hide that tooling issue.

## Publication

PR, CI and deployment receipts will be recorded below after their actual results are observed. Coverage gaps and missing High picks are public review items, not fabricated completion claims.
