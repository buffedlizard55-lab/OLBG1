# T61 — Evidence-first canonical root release

Owner/session: `6ad5a3a8-olbg1`
Assigned branch: `arena/6ad5a3a8-olbg1`
Integration PR: <https://github.com/buffedlizard55-lab/OLBG1/pull/84>

## What is supported

`data/release/evidence.json` saves **97 fixture/event extracts**, **46 source observations**,
all **17 eligible OLBG category first-chunk reads**, observation precision, field references,
source-specific fixture IDs and coverage blockers. Manual observations were read on
2026-10-22 through `fetch_page`. The ledger capture timestamp is transcription time, not
an invented timestamp for each HTTP request. It contains structured extracts, not full raw
manual page bodies. The optional automatic NHL/MLB collectors save raw official JSON.

The independent rereads include all chunks of the NHL Oct 22 score response, EuroLeague
Round 7 article, EHF playing-times PDF, ATP and WTA order-of-play PDFs, MLB schedule and
regular-season standings. EHF standings were read through the group tables. LNR fixtures,
URC Round 4 and the NRL men's World Cup Round 2 list were also read. Other sources have
explicit partial / blocked read scopes in the ledger.

Each canonical fixture, model-outcome, coverage and finding table row links to an official
manual-review destination. Unknown UTC times, bookmaker offers, current lineups,
head-to-head histories and unsupported prices remain null/blank. A governing-body homepage
or a consent page is never treated as proof of every event field.

## Important corrections and abstentions

- EuroLeague's official Round 7 article puts **Efes at home to Besiktas** and **Bayern at home
  to Dubai**; inherited v3 orientation is not reused.
- Official NHL score data says **Nashville 3-2-3**, not an inherited 3-3-2 record.
- NHL provider quotes have unresolved market/settlement metadata and inconsistent apparent
  favorite orientation. No comparable moneyline quote or betting EV is approved.
- ATP/WTA, WST, LNR, NZC and some other display clocks lack an explicit timezone. The printed
  time or session qualifier is retained, never converted to an invented exact UTC start.
- EHF's July schedule PDF and live Oct 28 Porto clocks disagree. No silent conversion or
  price is supplied for those unresolved future times.
- Tonga late-mail prose rules out Isaiya Katoa while its static team list still names him.
  The lineup is not called confirmed.
- AFLW fixture/ladder/news extraction did not return usable current facts; T35 prices are not
  recertified. PDC extraction remains consent-dominated. GBGB runner cards and full Riot
  current pairings remain unavailable in the collected text.
- Earlier reports allege eliminated Higgins/Darderi root picks. Those picks are withdrawn
  from the canonical slate, without claiming a result this session did not independently read.
- MLB's series `leagueRecord: 0-0` is not season form. The model uses separately fetched
  regular-season records: Milwaukee 103-59; Tampa Bay 98-64. Conditional Game 5 at Oct 29
  00:00Z falls outside the manual release's UTC window and is not added as a firm match.

## Independent models — and what they do not prove

The versioned, deterministic compiler does not import inherited model probabilities.
Record-only baselines use a disclosed symmetric four-game prior and a log5 comparison,
only when both observed sides have nonempty consistent records. NHL overtime losses count
as losses in the explicitly declared two-way model convention. There is no neutral-price
fallback for a missing team rating.

Five EHF matches have paired official scoring/concession inputs. An explicitly illustrative
independent-Poisson model supplies regulation 1X2 including draw, half-goal handicap ladders,
goal-total ladders, team totals and top-three-score/all-other-score complements. Four-game
samples and uncalibrated variance are serious limitations, so these estimates stay Low.

Fair decimal and American odds are zero-vig mathematical prices, not bookmaker offers.
There is no 5% fabricated offer, -250 clamp, price manipulation, generic cricket total or
crowd-tip share passed off as an independent probability. Probability/fair-price screens
use unrounded numbers, not display rounding.

**No High selections and no approved bets are published.** A numerical output over 70%
is not a measured success rate. Held-out calibration, matching quoted market/settlement,
confirmed relevant history/availability and evidence-grounded 30+ word High prose are not
available. Eight individual, source-linked research notes are supplied instead, explicitly
not High-confidence betting previews.

## Repository review scope

`release_inventory.py` enumerates repository files, counts UTF-8 lines, fingerprints content
and supplies file/line-specific GitHub review links for URLs and potentially risky verification
claims. The generated CSVs exclude themselves to avoid self-referential hashes.
This is an automated line inventory and inspection aid, **not manual factual verification of
every historical sentence**. Historical work is preserved and labelled unrecertified.

Prior root HTML and sport pages are copied to `archive/pre-release-20261022/`, with an archive
warning and rebased relative links. All namespaced desks, old datasets, safety-audit scripts,
tests and reports remain unchanged. The existing `release-review.html` is retained byte-for-byte
for compatibility with the independent audit's integrity test; the canonical nav uses the new
Flagged for Review register instead. New build and validation entrypoints are distinct from
legacy generators. PR #63's archive/consolidation approach informed the single front door;
its fixed-time v3-dependent builder and prices were not imported as fresh evidence.

Concurrent main updates were preserved on rebase. This session's colliding T55/§40 and then
T58/§43 claims were renumbered **T61 / §46**, without deleting the other owners' claims or work.

## Release gates and deployment

Canonical command sequence:

```sh
python3 scripts/release_build.py
python3 scripts/release_inventory.py
python3 scripts/release_validate.py
python3 -m unittest discover -s tests -p 'test*.py' -v
python3 scripts/release_package.py
```

The validator checks category exclusions, field/source roles, complete model probability
complements, fair-odds arithmetic, no missing-input fallback, conservative expiry, actual-time
cutoffs, blank unapproved fields, reproducibility, source links, primary fragment links and
all published HTML local file links. These are structural/model gates, not remote factual
certification or empirical forecast validation.

GitHub Actions validates pull requests and deploys static Pages artifacts on main pushes,
manual dispatch and scheduled refresh. It writes no repository branch. Optional refresh is
limited to NHL/MLB official structured APIs; failed requests never renew old observation dates.
Full multi-sport collection and all available bookmaker markets remain incomplete and are
visibly flagged rather than falsely represented as completed.

Final test, merge and Pages run identifiers will be appended after confirmation.

### Local validation checkpoint (2026-10-22)

- Canonical build: **33 pages**, **97** source-linked extracts, **30** models / **75** model
  markets / **165** fair outcomes. **46** exact future UTC starts and **51** timing-unconfirmed
  extracts at the saved build cutoff. All price values are experimental; **0 approved / 0 High**.
- New strict gate: **PASS**, covering all **408** published HTML pages and every canonical
  table-row official destination. Page and fragment counts are generated, not factual source proof.
- **38 unittest cases PASS**, including all five preserved independent audit integrity tests.
- Legacy `scripts/validate.py` also passed: **0 errors**, **3 warnings** confined to historical
  `/f7fa77fc/flagged.html` internal-policy citations. Its old 134/29 counts refer to retained
  historical data, not the new primary release.
- Headless Chromium / Playwright browser smoke: all **33** canonical routes returned HTTP 200;
  desktop **1440×1080** and mobile **390×844**; search, sport filter, regulation draw, blank unknown
  UTC, no mobile body overflow, client-side expiry and zero browser console errors all passed.
- Public artifact staging passed. Git, credentials, scripts, tests, dependency folders and
  transient tools are excluded. The optional browser dependencies and screenshots remain
  ignored scratch files, not published application assets.
- Automated refresh tests used mocks. Those tests are **not** new live official-source reads.

The file/line inventory is recomputed per build, so its counts and hashes follow the exact
current tree. The large line-level register is stored as reproducible compressed CSV rather
than a redundant 14 MB uncompressed tracked dataset.

Main then advanced through PR #87 (`8fc47dcb` / T60 / §45). This integration adopts
**T61 / §46**, preserving that namespace and all PR #85/#86 corrections unchanged.
The quote gate additionally checks actual quoted price, exact market/selection/rules,
availability, source URL and a five-minute age policy; fair prices cannot substitute for offers.

### Post-rebase integration checkpoint

Rebased onto main `31c63ba` including PR #87. New gate result: **33 canonical / 429 total
HTML pages**, **38 tests PASS**, full desktop/mobile browser smoke PASS. All upstream task
rows/sections and every namespace (including later `e6716490` corrections) were retained.
The root/sport HTML replacement is intentional; prior states remain archived and the new
`8fc47dcb` namespace is included automatically in the current archive directory index.

### Hosting/queue observation

At 08:05Z, PR #84's hosted validation job had no runner assigned. Pinned Ubuntu 24.04 rather
than the moving latest label; no local gate failed. The existing `main:/` Pages configuration
is branch-based. Direct Pages-settings changes return API403 for the Arena integration,
although repository and PR writes work. The validated static root supports that legacy mode;
custom artifact deployment success is not presumed from the presence of a workflow file.

### Merge receipt

- Integration PR **#84**: <https://github.com/buffedlizard55-lab/OLBG1/pull/84>.
- **MERGED 2026-10-22T08:08:30Z**, commit `6e8570c6605e711376ab48045beba88dfcac22e6`.
- Normal merge, no admin check bypass. Hosted validation was queued, not failed; the local
  38-test, structural/model/link and real-browser suites passed before merge.
- Main workflow **39745549884** has acquired a hosted runner. Build/deploy success and
  actual live content are checked separately below; they are not implied by the merge.
- Subsequent main runs retain active production deployments rather than cancelling them
  on documentation-only pushes. Superseded PR checks can still be cancelled.

## Confirmed production publication

- **Primary PR #84:** MERGED `6e8570c6605e711376ab48045beba88dfcac22e6`,
  2026-10-22T08:08:30Z.
- **Production workflow [39745549884](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39745549884): SUCCESS.**
  Build job `119712960477` and deployment job `119714983504` both succeeded, including
  the 38-test suite and full structural/model/source-role/local-link gate.
- **GitHub Pages environment deployment 7247180107:** `state=success`,
  **2026-10-22T08:17:32Z**; live URL <https://buffedlizard55-lab.github.io/OLBG1/>.
- Independent live fetches confirmed the new root, JSON build manifest, coverage page,
  tennis blanks and full archive directory. Published build cutoff **2026-10-22T08:13:14Z**;
  **33 pages / 97 extracts / 17 categories / 30 models / 75 markets / 165 outcomes / 0 approved / 0 High**.
- Production collection: **2/9 requests succeeded**. Failure dates were not renewed;
  success does not prove an exhaustive query or verify every inherited field. Source dates
  and editorial dates remain distinct from the new build timestamp.
- The separate branch-based Pages run `39745550531` built but its deploy job was cancelled.
  This can leave the legacy summary API in an error/building state despite the successful
  custom artifact deployment. The explicit successful environment status and live content
  above are the publication proof. No failing model/link/test gate was ignored.
- Direct Pages-settings updates remain restricted for the Arena integration. The workflow's
  scoped GITHUB_TOKEN demonstrably deployed the artifact; no user credentials or manual
  configuration were requested.
- Receipt/concurrency follow-up **PR #90** stays on the same assigned Arena branch. T61
  integration is complete; exhaustive match/market collection, empirical calibration and
  fully supported High selections remain incomplete and openly flagged, not claimed done.
