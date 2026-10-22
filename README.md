# OLBG1 · evidence-first research desk

[Dashboard](https://buffedlizard55-lab.github.io/OLBG1/) · [Match list](https://buffedlizard55-lab.github.io/OLBG1/picks.html) · [Markets](https://buffedlizard55-lab.github.io/OLBG1/markets.html) · [Flagged for Review](https://buffedlizard55-lab.github.io/OLBG1/flagged.html)

One canonical dashboard, **17 sport pages**, explicit evidence gaps and independently calculated **experimental fair prices**. Not affiliated with OLBG. No guaranteed returns, bookmaker execution or personalized staking advice.

## What this release actually contains

The selected **22 October 2026** import contains **108 fixture/event listings**, **42 accepted statistical input observations** and **31 official-source checks**. It spans 15 categories; darts and greyhound fixture/runner details remain unverified. Every category is **partial or unverified**, never globally complete.

At the import checkpoint, compatible inputs support **17 price books / 42 two-way markets / 84 outcome prices** after the TEE3C status gate (22 October, approximately 12:20 UTC build). There are **17 Low experimental winner preferences** and **zero Medium/High selections**. EuroLeague schedules without an explicit supported pre-match status no longer produce estimates. Valencia’s disputed record is quarantined after separate official preview/standings rereads. These are as-of counts, not permanently current numbers; refreshes, expiry and the UTC window can change them.

**Not complete:** worldwide fixtures, every bookmaker market, calibrated sport-specific models, current player availability, recent game-by-game histories or verified available bookmaker odds. Unsupported values remain **null in JSON and blank in tables**, with reasons and official recheck links. We do not invent High predictions to fill a quota. Any future High write-up must be unique, at least 30 words, state the selection and participants, and support its current form/player/history claims with official evidence.

## Scope

Included: tennis, basketball, golf, cricket, snooker, rugby union/league, baseball, ice hockey, motor racing, darts, handball, volleyball, Australian rules, eSports, Gaelic football and greyhounds.

Excluded: soccer/football, American football, boxing, UFC/MMA, hurling, horse racing, cycling and specials. Gaelic and Australian rules are explicitly distinct inherited categories. No hurling/camogie/shinty listings are imported.

## Evidence and pricing contract

- OLBG public routes/cards are **discovery**, not official fixture verification. Tip shares are votes, not model probabilities. Robots restrictions, including the Python-urllib disallow, are respected; no private/hidden API, proxy or identity rotation is used.
- Selected retrieval-tool excerpts have an honest observation window, not invented per-request HTTP metadata. Automated parsed JSON responses retain bytes, hashes and JSON locators; unparsed HTML probe bodies are not published as evidence. Hashes prove integrity, not truth.
- Every accepted fixture field references an official-source observation. Missing timezones are not guessed; a published schedule is not proof of current match status.
- Fixture evidence expires **six hours from its original lower observation bound**; statistics expire after 24 hours. Builds and failed refreshes never rejuvenate them. Elapsed starts cannot produce pre-match selections. Every estimate expires at the earliest fixture, start or statistical-input deadline; the browser suppresses expired values within its 30-second check interval. With JavaScript disabled, estimates are hidden rather than left indefinitely current. Explicit supported official pre-match status is required; a future start alone does not qualify.
- Exact UTC starts use a rolling seven-day interval. Date-only entries retain the source calendar and explicit time/status gaps. Previous league dates are checked for still-future overnight UTC starts.
- Record pricing uses disclosed Beta(2,2) shrinkage and log5, requires both compatible records, and inserts no home edge or missing-rating default. NHL binary defeats include OT losses; points percentage is not a win probability.
- MLB research score markets use paired official regular-season run rates and independent Poisson scores conditional on no tie. Fixed ±1.5-run handicaps and three centered half-run totals are **model lines, not available sportsbook offers**. Pitchers, parks, current lineups and postseason effects are not modeled; all remain Low.
- Fair decimal is `1/p`, with no margin or clipping. American displays are derived consistently; unrounded prices determine the −250…+10000 fair-price flag. Actual quotes/availability/edge remain blank.
- **No >70% shortcut for High.** Confidence needs measured calibration, current relevant context and an eligible actual quote—not merely a favorite's probability. Version evidence-v1.0 cannot issue Medium/High.

## Build and test

Python 3.11+ standard library; no paid feed, API key or application dependency.

```sh
python3 -m unittest discover -s tests/pipeline -v
python3 -m unittest discover -s tests -p 'test*.py' -v  # preserved upstream tests
python3 -m pipeline.build --out _site
python3 -m pipeline.validate --site _site
python3 -m http.server 8000 --bind 0.0.0.0 --directory _site
```

Browser tests (tooling/binaries stay ignored):

```sh
BROWSER_TOOLS="${TMPDIR:-/tmp}/olbg-browser"
npm install --prefix "$BROWSER_TOOLS" --no-save --no-package-lock --ignore-scripts \
  playwright-core@1.55.0 @sparticuz/chromium@138.0.2
NODE_PATH="$BROWSER_TOOLS/node_modules" node tests/pipeline/browser.cjs
```

The browser suite tests desktop/mobile, `/OLBG1/` hosting, filters/reset/sort, odds formatting, CSV downloads, evidence deep-links, empty states, expiry removal and no-JavaScript rows. All browser URLs are relative; there is no localhost backend call.

```sh
python3 -m pipeline.refresh             # bounded official HTTP attempts, failures logged
python3 -m pipeline.build --out _site
python3 -m pipeline.validate --site _site

# Only the final integration publishes checked-in root files for main:/ Pages:
python3 -m pipeline.build --out .
```

`python3 scripts/build_site.py` delegates to the canonical pipeline. Other session/release generators are **historical reproduction tools**, not canonical commands; run them only in an isolated checkout. `--at <UTC timestamp>` supports deterministic build tests, never pretends a source was fetched then. `pipeline.capture_session` is a fixed selected-evidence import, **not a live scraper**.

## Automation and actual hosting mode

`.github/workflows/current-pages.yml` is the single canonical PR/test/refresh/publication workflow. Pinned actions, read-only checkout, 113 pipeline tests plus 38 preserved tests, data/link/fragment gates and real browser tests precede artifact creation. Public structured collectors cover NHL/MLB/NBA schedules; other categories remain explicitly unparsed/partial. A failed request is not a zero-fixture finding.

**Pages is already enabled and its configuration API reports `main:/` / legacy mode.** The interactive integration cannot change that setting (API403), but the standard GitHub Actions artifact deployment is proven to work with the repository’s authorized job token: upstream run `39745549884` succeeded and the live T61 page was fetched. The canonical workflow uses that same pinned configure/deploy path; it does not request new credentials or pretend the settings change succeeded. The separate legacy branch-build status can say cancelled/errored while an artifact deployment succeeds. Verify the actual deployment job and live content, not that legacy status alone.

**Preserved T61 publication receipt (historical, not this release):**

Pinned action revisions were resolved from the official `actions/*` repositories. The
static site has no external JavaScript, analytics, remote font dependency or browser-facing
localhost service. The Pages artifact includes source-linked data and the review register.
Publication confirmed: [PR #84](https://github.com/buffedlizard55-lab/OLBG1/pull/84), merge
`6e8570c`, [successful production run 39745549884](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39745549884),
Pages deployment `7247180107` succeeded at **2026-10-22T08:17:32Z**. Live root and build metadata
were checked independently. Receipt follow-up: PR #90. Full records are in `COORDINATION.md`
§46 and [the release report](reports/RELEASE_T61.md).

Three-hour refresh attempts publish only after tests/build/browser gates pass. Source failures remain gaps; scheduled execution is not guaranteed latency. The retained branch-based build can also trigger on pushes, so checked-in root files use the same canonical UI and expiry policy. A single custom deployment workflow publishes current artifacts, serialized in the `pages` concurrency group. The final publication receipt is recorded only after the live revision is confirmed.

The previous T61 workflow is retained as a manual, non-publishing historical check so it cannot race the canonical publisher. Coverage gaps do not block a release; build/test failures do. Final merge and actual Pages receipts belong in `COORDINATION.md` and `reports/SESSION_257E6674_RELEASE.md`.

## Review and preservation

- `data/current/`: current facts, calculations, source captures, network attempts and complete machine-readable audit.
- `audit/rows-*.html`: paginated historical row occurrences with file lines, exact JSON pointers and source/recheck links. Mirrors/aliases are labelled; these are **not unique recertified matches**.
- `pipeline/audit.py`: reads tracked legacy JSON/Python files, inventories detectable fixture/price/prose objects and publishes 22 traced findings. Parsing every file is not semantic verification of every sentence.
- `archive/root-20261022/`: complete pre-T257E root (including T61), original hashes, rewritten links and an archive warning.
- `archive/pre-release-20261022/`: T61's earlier archive, untouched.
- All parallel desks, `data/release`, `scripts/release_*`, `tests/release` and independent review reports are preserved. Their claims are never silently promoted to current evidence.

[Methodology](https://buffedlizard55-lab.github.io/OLBG1/methodology.html) · [Field evidence](https://buffedlizard55-lab.github.io/OLBG1/verification.html) · [Archive](https://buffedlizard55-lab.github.io/OLBG1/archive.html)

## Canonical integrity follow-up (TEE3C)

[Session audit](reports/SESSION_EE3C3E8F.md): explicit pre-match status gate, statistical-input expiry in both table and market views, no-JavaScript withholding, and count/window/provenance regression gates. These checks do not recertify every archived statement or establish full live coverage. New findings are [published for review](https://buffedlizard55-lab.github.io/OLBG1/flagged.html#F-257E-20).
