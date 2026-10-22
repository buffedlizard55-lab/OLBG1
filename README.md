# OLBG1 — evidence-first independent research desk

**Dashboard:** <https://buffedlizard55-lab.github.io/OLBG1/>
**Review ledger:** <https://buffedlizard55-lab.github.io/OLBG1/flagged.html>
**Coverage:** <https://buffedlizard55-lab.github.io/OLBG1/coverage.html>

One canonical front door, 17 sport subpages, readable tables, official review links and
explicit abstentions. Previous desks are retained as **unrecertified history**, not as
competing live recommendations. This project is not affiliated with OLBG.

## Current release: what is and is not complete

The manually observed 2026-10-22 ledger contains **97 fixture/event extracts**, **46 source
observations** and a first-chunk discovery read of **all 17 eligible OLBG sport hubs**.
It supports **30 experimental fixture models, 75 model markets and 165 fair outcome prices**.
These counts describe that saved snapshot; deployed structured refreshes can change them.

**Zero approved bets and zero High-confidence selections.** The observations do not include
held-out forecast calibration or sufficiently verified matching bookmaker markets/settlement.
A model output above 70% is not a measured win rate. No prices, neutral ratings or High
previews are fabricated to fill missing coverage. Eight individual source-grounded research
notes are provided, explicitly not High-confidence betting previews.

**Not complete:** exhaustive worldwide seven-day match collection, all available bookmaker
markets, full private-system reverse engineering, current lineups and sport-specific validated
betting models. Every category is marked **partial** or **blocked**. Empty JS output, consent
screens and “No tips found” do not prove that no fixtures exist. These gaps remain published
under Flagged for Review and do not block the site release.

### Included / excluded

Included categories: tennis, basketball, golf, cricket, snooker, rugby union, rugby league,
baseball, ice hockey, motor racing, darts, handball, volleyball, Australian rules, eSports,
Gaelic football and greyhounds.

Excluded: soccer / football, American football, boxing, UFC / MMA, hurling, horse racing,
cycling and specials / entertainment. Gaelic football and Australian rules are distinct
included OLBG categories.

## Evidence and model contract

- Every canonical data/review table row links to an official manual-review destination.
  An official URL alone is not a blanket verification stamp.
- Unknown exact UTC starts, bookmaker prices, current availability, history and unsupported
  model values remain **null in JSON / blank in tables**. Printed clocks and “followed by”
  qualifiers are retained without inventing a timezone or a fixed start.
- Manual read dates are separate from ledger transcription and build time. Rebuilding never
  renews a source observation. Date-only evidence expires conservatively at the next UTC
  midnight; exact API observations expire after 24 hours.
- The build defaults to **actual UTC**, not a midnight-only fixed cutoff. A passed start is
  not represented as a known final result. Browser-side expiry also removes current projection
  cells after start/expiry.
- Own odds are **zero-vig fair estimates**, not bookmaker offers. No invented 5% margin,
  -250 clamp, market-implied tip probability or generic cricket total is supplied.
- Record-only winner baselines require both observed nonempty records. They use a disclosed
  Beta(2,2) prior and log5-style comparison; missing data causes abstention, not equal strength.
- Illustrative EHF goal models use paired scoring/concession rates and independent Poisson
  regulation scores. Draw, half-goal handicaps, totals, team totals and score complements are
  handled explicitly. Four-game samples cap these estimates **Low**.
- Low/Medium are descriptive experimental tiers, not calibrated accuracy. High is disabled
  until reliability evidence, exact timing, matching quote/rules, confirmed relevant context
  and unique, evidence-grounded 30+ word preview requirements are met.
- At zero vig, `p > .70` and fair odds no shorter than `-250` intersect only at
  `.70 < p <= 5/7`. That arithmetic does not establish an edge. All screens use unrounded
  values; none are tuned or clamped to manufacture High eligibility.

Official rereads corrected Efes/Bayern home orientation and Nashville's record. NHL provider
quote conflicts, Tonga lineup contradictions, EHF Oct 28 time ambiguity, AFLW/T35 retrieval
limits, PDC consent extraction and unsupported inherited recommendations are explicitly
recorded. Full details: [release audit](reports/RELEASE_T61.md).

## Build, test and preview

Python 3.11+ standard library is sufficient. No application dependencies, API keys, secret
configuration or paid feed are required.

```sh
# Build the canonical root / sports pages from saved observations.
python3 scripts/release_build.py

# Whole-repository line/fingerprint inventory, then strict canonical validation.
python3 scripts/release_inventory.py
python3 scripts/release_validate.py

# Includes the preserved independent audit's integrity tests.
python3 -m unittest discover -s tests -p 'test*.py' -v

# Create the public-only deployment artifact; excludes Git, credentials and tooling.
python3 scripts/release_package.py

# Local preview; all browser-facing URLs are relative and project-path safe.
python3 -m http.server 8000 --bind 0.0.0.0
```

Optional browser smoke (Chromium binaries/tools remain ignored):

```sh
npm install --prefix .cache/browser --no-audit --no-fund playwright-core @sparticuz/chromium
node tests/release/browser_smoke.cjs
```

`--as-of 2026-10-22T07:30:00Z` on `release_build.py` is available for reproducible tests.
It does **not** mean the sources were read at that time. Normal publication uses the actual
clock, not that example cutoff.

Optional structured refresh:

```sh
python3 scripts/release_fetch.py
python3 scripts/release_build.py
python3 scripts/release_inventory.py
python3 scripts/release_validate.py
```

Only official NHL and MLB JSON collectors are implemented. A successful response saves raw
JSON and exact retrieval time. A failed request records the error **without renewing old
observations or inventing facts**. Other sports retain their manual read dates and become
visibly stale. Raw responses are deployment artifacts, ignored by Git. Editorial notes retain
their original observation date; they are not silently rewritten by a schedule refresh.

## Publishing

`.github/workflows/evidence-pages.yml`:

- validates pull requests;
- builds and deploys a static Pages artifact on `main` pushes and manual dispatch;
- attempts supported official JSON refreshes every six hours;
- runs tests, source/model/time/link gates and public-file packaging before deployment;
- uses read-only repository contents and narrow Pages deployment permissions;
- **never commits or pushes to any repository branch**.

Pinned action revisions were resolved from the official `actions/*` repositories. The
static site has no external JavaScript, analytics, remote font dependency or browser-facing
localhost service. The Pages artifact includes source-linked data and the review register.
Final PR, merge and deployment confirmation are recorded in `COORDINATION.md` §46 and the
release report after GitHub reports success.

## Files and audit scope

| Path | Purpose |
| --- | --- |
| `data/release/evidence.json` | Observed facts, source scopes/dates, per-field references, category blockers |
| `data/release/commentary.json` | Eight individual, explicitly dated research notes |
| `data/release/bundle.json` | Reproducible model outcomes, time statuses, approval blockers and counts |
| `data/release/rows.csv` | One row per current extract; unknown/approved fields remain blank |
| `data/release/build.json` | Input fingerprints, exact build cutoff and canonical page manifest |
| `scripts/release_model.py` | All model assumptions, fair odds, draw handling, time and High gates |
| `scripts/release_fetch.py` | Limited official NHL/MLB JSON refresh, raw capture and failure disclosure |
| `scripts/release_build.py` | Canonical root and sport-page compiler |
| `scripts/release_validate.py` | Strict reproducibility/source-role/model/time/local-link gate |
| `scripts/release_inventory.py` | Whole-repository file/line counts and manual-review links |
| `reports/release_file_inventory.csv` | File fingerprints and exact GitHub review locations |
| `reports/release_line_findings.csv.gz` | Compressed line-level URL / risk-term register |
| `reports/RELEASE_T61.md` | Factual checks, limitations, preservation, tests and publication record |
| `tests/release/` | Offline regression tests for the canonical evidence-first release |

The line inventory includes tracked and newly authored files but excludes its own generated
CSV outputs to avoid self-referential hashes. It is an **automated inspection aid**, not a claim
that every historical line has been manually checked against official sporting evidence.
Structural tests and source-link checks do not prove external factual truth or model accuracy.

## Historical work and coordination

The previous root and sport pages are preserved under `archive/pre-release-20261022/` with
conspicuous historical warnings and rebased relative links. The old README is preserved
there too. `data/release/archive.json` records original file hashes. All namespaced desks
(including later `e6716490/` and `7ad0d336/` additions) remain unchanged and are linked from
the archive index. The earlier `release-review.html`, its report, script and tests remain
byte-compatible; the canonical navigation uses the current Flagged for Review page.

The old `scripts/build_site.py`, `model.py`, namespaced generators and datasets remain for
historical reproducibility. They are **not the canonical publishing command** and must not
be used to overwrite the evidence-first root without a coordinated integration.

Work stays on Arena's assigned branch `arena/6ad5a3a8-olbg1`. Concurrent upstream sessions
were preserved on rebase; task-ID collisions were resolved by renumbering this session to
**T61 / §46**. See `COORDINATION.md` for owners, claims, handoffs and publication history.

18+ · Research only. Do not bet money you cannot afford to lose.
