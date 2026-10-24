# Session 733888f2 — T733888F2 desk report

**Session / branch:** `733888f2-olbg1` on `arena/733888f2-olbg1`
**Captured:** 2026-10-24T22:28–23:15Z (research cut 23:15Z)
**Desk:** `/733888f2/` — 27 pages (12 top-level pages plus 15 sport pages)
**Data:** `data/733888f2/*.json`

## What was asked

Find upcoming OLBG matches for fifteen named sports; originate our own lines on every match across
winner / handicap / total; pick a winner with a low–medium–high confidence label; write unique,
non-robotic predictions of at least 30 words for the high-confidence picks, using official facts;
make the picks obvious with an executive summary; verify line by line and flag anything that cannot
be confirmed; publish a clean dashboard; and merge without waiting for approval.

## What was actually possible tonight

| | Count |
|---|---|
| OLBG events discovered across the fifteen hubs | 59 |
| Matches priced with an official input for both sides | **7** |
| Picks (one per priced match) | **7** |
| High picks (probability > 70% **and** fair price inside −250…+10000) | **0** |
| Strong picks (≥ 70% but above the −250 ceiling) | **2** |
| Events listed with no price, each with the missing input named | **52** |
| Flags published | **18** |
| Official pages read for facts | 11 |
| OLBG pages read for discovery only | 16 |

### Priced matches

| Match | Start (UTC) | Input | Pick | Fair price | Prob. | Tier |
|---|---|---|---|---|---|---|
| Florida Panthers @ Chicago Blackhawks | 2026-10-25T19:00Z | 5-4-2 v 3-7-0 | Florida ML | −166 | 62.4% | Medium |
| New York Islanders @ Dallas Stars | 2026-10-25T22:00Z | 5-3-2 v 6-3-1 | Dallas ML | −128 | 56.1% | Medium |
| Montreal Canadiens @ Winnipeg Jets (Heritage Classic, neutral) | 2026-10-25T23:00Z | 5-3-2 v 4-3-3 | Montreal ML | −113 | 53.1% | Low |
| Colorado Avalanche @ Nashville Predators | 2026-10-26T00:00Z | 6-4-1 v 3-3-3 | Colorado ML | −114 | 53.3% | Low |
| Minnesota Wild @ Vancouver Canucks | 2026-10-26T02:00Z | 6-3-2 v 2-9-1 | Minnesota ML | −263 | 72.5% | Strong |
| Tampa Bay Rays @ Milwaukee Brewers (WS G2) | 2026-10-25T00:00Z | 98-64 v 103-59; MIL lead 1-0 | Milwaukee ML | −139 | 58.2% | Medium |
| Harlequins v Saracens | 2026-10-25T15:00Z | 2 pts (−68) v 11 pts (+21) | Saracens ML | −457 | 82.1% | Strong |

## The band arithmetic (why there is no High pick)

A fair price of −250 is 71.43%. The brief asks for picks that are both "greater than 70%" and
"between −250 and +10000". Those two conditions intersect in a window from 70.00% to 71.43%.
Six of the seven picks fall outside it: five below 70%, and the two strongest (Minnesota 72.5%,
Saracens 82.1%) above the ceiling. Both are published as **Strong — outside the requested band**
rather than relabelled as High. This is flag F-13 on the site.

## Method

Documented in `scripts/s733888f2_model.py` and on `/733888f2/methodology.html`:

* hockey `s = (points+1)/(games+2)`, `logit(p) = 1.5 (s_home − s_away) + 0.12`, home term removed at a neutral site
* baseball `s = ln(pct/(1−pct))`, `logit(p) = 1.0 (s_home − s_away) + 0.20`
* rugby `s = (points+1)/(games+2)`, `logit(p) = 0.9 (s_home − s_away) + 0.10`
* prices are margin-free (`decimal = 1/p`); the even-money handicap is derived from the same
  probability with a stated per-sport margin sigma and labelled a structural estimate

## Verification performed

Every number in a published row, and every number used in a write-up, was read in this session from:

* **NHL** — `api-web.nhle.com/v1/score/2026-10-25` (records, start times, venues, club leaders) and
  `/standings/2026-10-24`
* **MLB** — `statsapi.mlb.com` schedule with `hydrate=probablePitcher` (World Series G2, probable
  pitchers, series state) and both league standings endpoints (TB 98-64, MIL 103-59)
* **Premiership Rugby** — `premrugby.com/competitions/gallagher-prem/standings` (round 3 table)
* **Harlequins FC** — official match preview (15:00 Sunday 25 October, Twickenham Stoop, referee,
  both named 23s, Marcus Smith's 200th appearance, Saracens' Connacht defeat)
* **ATP** — official Basel draw report (Djokovic v Humbert, Wawrinka v Lehecka)
* **ECB** — official Pakistan tri-series schedule (25/27/29/31 October, venues)
* **PDC** — official European Championship schedule and day-one report (which is what exposes the
  stale OLBG darts listing)
* **Lega Pallavolo Serie A** — official SuperLega round-one page, opened; only site chrome was
  retrievable, so no table value is published

OLBG was read for discovery only, on sixteen hub pages. No OLBG tip percentage entered a price.

## What could not be done, and why

Twelve sports carry no price. Each row on the site names the exact missing input:

* **Golf, Snooker, Motor Racing** — hubs served no events at all (F-01, F-02, F-03).
* **Rugby League** — only 2027 outrights, no match market (F-04).
* **Darts** — the two listed matches had already been played on the PDC's own schedule (F-05).
* **Basketball** — nba.com served a calendar shell only; the CDN scoreboard returned HTTP 500 and
  stats.nba.com was unreachable (F-08).
* **Volleyball** — official league page body not retrievable (F-09).
* **Tennis, Cricket, Gaelic, Greyhounds, Handball** — fixtures found, official form inputs not read
  (F-10, F-11, F-12, F-06).

No injury report was read for any fixture, so no injury claim is made anywhere (F-14).

## Repository review

`/733888f2/repo-audit.html` measures the checkout at build time: 3,032 tracked files, 1,856 HTML
pages, 75 desks with an `index.html`, 89 top-level directories, 97 data directories, 16 publisher
archive entries.

* **AUD-733-01** the publisher serves 16 of the 75 desks — 59 exist in git but not on the live site
* **AUD-733-02** `README.md` still describes a 25-page artifact
* **AUD-733-03** one directory per session with no supersession index — the root cause of "the site
  is too confusing to understand"
* **AUD-733-04** a naive whole-tree link scan reported 1,129 broken links; every sampled hit was an
  absolute https URL, i.e. a scanner defect. Recorded so the figure is not repeated as a finding.

## Gates (all run in this session)

```
python3 -m unittest discover -s tests/pipeline -p 'test_*.py'   ->  633 tests OK
python3 scripts/s733888f2_validate.py                            ->  0 errors
python3 -m pipeline.validate --site .                            ->  0 errors
python3 scripts/validate.py                                      ->  PASSED, 3 pre-existing
                                                                    f7fa77fc warnings
python3 -m pipeline.build --out /tmp/_site733                    ->  25 pages, desk included
python3 -m pipeline.validate --site /tmp/_site733                 ->  0 errors
```

## Scope touched

`data/733888f2/**`, `scripts/s733888f2_*.py`, `733888f2/**`, `tests/pipeline/test_desk_733888f2.py`,
`reports/SESSION_733888F2.md`, append-only `COORDINATION.md`, and one additive `ARCHIVE`
registration line for `733888f2/index.html` in `pipeline/build.py` (declared in the claim before the
edit, per the T23728B2B-INT / T99D4 precedent).
