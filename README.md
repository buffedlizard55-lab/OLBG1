# Signal Ledger

A source-linked, timestamped audit of match listings visible on OLBG across the requested non-excluded sports. The project reconciles each discovery row against an official governing-body or competition source, originates independent fair lines, and publishes every uncertainty on a static GitHub Pages dashboard.

**Dashboard:** <https://buffedlizard55-lab.github.io/OLBG1/>

> Research only. Model outputs are estimates, not bookmaker prices or betting advice. No result is guaranteed. Adults 18+ only.

## Frozen capture

- **Cutoff:** 2026-10-21 05:45 UTC
- **Modeled matches:** 135
- **Included category records:** 15
- **Officially verified rows:** 131
- **Partially verified rows:** 1
- **Unverified rows:** 3
- **Flagged matches:** 16
- **High-confidence selections:** 10

OLBG is used only to discover its visible category rows. Fixture identity, scheduling, venues, records, rankings, form and recent-history facts come from official leagues, tours, federations or governing bodies. Several OLBG pages retain a “Load More Tips” control, so completeness is explicitly limited to the visible rows at the cutoff, plus two NBA fixtures found in the official schedule but absent from the visible Basketball capture.

## Included and excluded scope

Included category pages cover Baseball, Basketball, Cricket, Darts, Gaelic Football, Golf, Greyhounds, Handball, Ice Hockey, Motor Racing, Rugby League, Rugby Union, Snooker, Tennis and Volleyball.

As requested, the project excludes soccer, boxing, UFC, MMA, football, American football, hurling, horse racing, cycling and specials. Golf, Motor Racing and Rugby League exposed outright/event markets rather than match-level rows and are classified as such. Greyhound cards could not be reproduced from an official future-card feed, so the category remains visible as an unverified empty state rather than receiving invented runners or prices.

## What each match contains

Every dashboard row links directly to an official source and includes:

- normalized participants and competition;
- official date, time and venue where explicitly confirmed;
- schedule verification state;
- an independent match-winner selection and no-vig fair decimal odds;
- a sport-specific handicap midpoint;
- a format-aware total midpoint;
- low, medium or high confidence;
- source facts, model inputs, formula and audit rule;
- coded irregularities when discovery and official evidence disagree.

Blank official fields are intentional. They mean the value was not confirmed; the build does not infer or backfill it.

## Independent line model

The deterministic `evidence-shrink-v1` model applies a logistic transform to three directional inputs relative to participant A—strength, recent form and venue—then shrinks the result toward 50% according to evidence reliability:

```text
raw = logistic(0.92 × strength + 0.68 × form + 0.42 × venue)
P(A) = 0.5 + (raw − 0.5) × reliability
```

Fair decimal odds equal `1 / probability`; no bookmaker overround is included. Handicap and total values are research midpoints in each sport’s natural units, not claims about live market availability. OLBG crowd percentages, tip selections and displayed prices are excluded from all model inputs.

High confidence requires all of the following: probability of at least 70%, an officially verified fixture, reliability of at least 0.85, and unique source-grounded analysis of at least 30 words. Unverified fixtures are forced to low confidence.

See [`methodology.html`](methodology.html) for the complete market, source and confidence rules.

## Repository map

- `data/model-inputs.json` — human-auditable official facts, flags and deterministic model inputs.
- `data/matches.json` — generated strict output consumed by the dashboard.
- `data/categories.json` — category coverage and empty-state classifications.
- `scripts/build-model.mjs` — independent probability, fair-odds, handicap and total generator.
- `scripts/validate-data.mjs` — strict source, schema, probability, flag and analysis validation.
- `scripts/build-pages.mjs` — deterministic category-page and sitemap generator.
- `assets/app.js` — dependency-free filtering, table, dialog and category rendering.
- `assets/styles.css` — responsive visual system.
- `tests/data.test.mjs` — scope, reproducibility, blank-value, source and page tests.
- `COORDINATION.md` — ownership, verification, irregularity, integration and deployment log.

## Run locally

Node.js 20 or later is required. The project has no runtime dependencies.

```bash
npm ci
npm run check
python3 -m http.server 8000
```

Open <http://localhost:8000/>. `npm run check` rebuilds the strict dataset and category pages, validates all records, then runs the Node test suite.

## Deployment

`.github/workflows/pages.yml` validates the project before uploading and deploying the repository as a GitHub Pages artifact. Pull requests run the same build and tests without deploying. The production deployment runs only from `main` or by explicit workflow dispatch.

## Responsible use

This is a research artifact, not a prediction guarantee. Availability, lineups, venues and scheduling can change after the cutoff. If you choose to gamble, verify current official information and bookmaker settlement rules, never stake money you cannot afford to lose, and seek support from [GamCare](https://www.gamcare.org.uk/) or [GambleAware](https://www.begambleaware.org/) when needed.
