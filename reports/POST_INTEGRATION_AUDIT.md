# Post-integration repository audit (2026-10-21)

## Scope and limits

This is an independent, read-only audit of the checked-in root dataset and existing build gates. It covers machine-readable count/ID/market/prediction consistency, source-link presence and a review of whether prediction prose is traceable to its structured evidence. It does **not** claim to have fetched and re-read every linked official page during this pass. A link being present, or a previous session recording a verification, is not proof that the linked page currently confirms every claim. Keep claims that were not freshly substantiated flagged rather than upgrading them to verified.

The audited source records are in [`data/fixtures.json`](../data/fixtures.json), [`data/lines.json`](../data/lines.json), [`data/predictions.json`](../data/predictions.json), [`data/sources.json`](../data/sources.json), and [`datasets/matches_full.json`](../datasets/matches_full.json). The existing live dashboard is [OLBG1 on GitHub Pages](https://buffedlizard55-lab.github.io/OLBG1/) and its [Flagged for Review page](https://buffedlizard55-lab.github.io/OLBG1/flagged.html).

## Reproducible checks run

Commands run from the repository root:

```text
python3 scripts/validate.py
Validated HTML pages: 27 at / + 27 at /f7fa77fc/ = 54 pages
Errors: 0   Warnings: 0
VALIDATION PASSED — ZERO ERRORS, ZERO BROKEN LINKS, ZERO DUPLICATE N-GRAMS

python3 scripts/ebfbd966_validate.py
Matches: 133 | HIGH/MED/LOW: 4/31/98
Pages: 18 | Writeups: 4 (words: 117, 129, 119, 130)
VALIDATION PASSED

Whole-repository relative-link sweep: 130 HTML files; 0 missing local href/src targets.
```

An independent in-memory cross-check of the root JSON files found:

| Check | Result |
|---|---:|
| Fixture rows / unique fixture IDs | 134 / 134 |
| Line rows / unique line IDs | 126 / 126 |
| Prediction rows / unique prediction IDs | 31 / 31 |
| Full-dataset rows / unique IDs | 134 / 134 |
| Fixture IDs lacking a priced line | 8 event-only field cards (4 golf, 1 motor racing, 3 greyhound); expected by the dataset's H2H vs field-card split |
| High-confidence lines missing a prediction; predictions not linked to a high-confidence line | 0 / 0 |
| Lines without a fixture; predictions without a line | 0 / 0 |
| Fixture rows missing a source or a non-OLBG source URL | 0 / 0 |
| Fixture status | 129 `verified`, 5 `cross-checked` |
| Market families | 126 winner, 126 handicap, 125 total, 35 draw-no-bet |
| Market outcome probability sums outside 0.002 from 1.0 | 0 |
| High-confidence lines without both measured ratings | 0 |
| Declared fixture/line/prediction counts vs actual array lengths | 134/134, 126/126, 31/31 |

Five Gallagher Premiership records remain explicitly `cross-checked`, rather than `verified`: Gloucester–Bath, Newcastle Red Bulls–Sale Sharks, Leicester–Northampton, Bristol–Exeter, and Harlequins–Saracens. They have official Premiership fixture-page URLs in the records, but the status difference must not be flattened in summaries that say all 134 are “officially verified.”

## Findings requiring review

### F1 — Prediction claim-level sourcing is not established (needs review)

All 31 high-confidence writeups meet the stored 60–70 word count and have official-source URLs attached. The validators check word count, linkage, uniqueness and model consistency; they do not establish that every factual clause in the prose appears on the linked official page. The structured `facts` arrays are generally narrower than the prose. Examples from `data/predictions.json`:

* `nhl-2026020152` says “far steadier five-on-five control” and suggests “empty-net pressure”; neither claim appears in its structured facts, which report records, points percentage and goal differential.
* `nhl-2026020154` asserts a strong road penalty kill and “four balanced lines,” while its structured facts contain standings and goal differential only.
* `nhl-2026020158` describes “bleeding high-danger slot looks”; the structured evidence only supplies records and a winning/losing streak.
* `nba-sac-lac-20261021` attributes performance to “half-court physicality and low turnover rates”; its cited facts contain prior-season records only.

These examples are not asserted false; they are **unsubstantiated by the evidence fields stored with the prediction**. Until each clause is checked against an official, linked source or removed/reworded, those predictions do not satisfy a strict “verified information only” standard. The same claim-level review should be applied to all 31 writeups, not only the examples above.

### F2 — Status wording is easy to overstate (needs review)

The root dashboard/README summaries describe 134 events as officially verified, while the underlying fixture data distinguishes 129 `verified` from 5 `cross-checked` rows. Preserve the distinction in public summaries and in exports. Do not change the five statuses without actually confirming each fixture against a source that meets the project's verification rule.

### F3 — Official-source page content was not re-fetched in this pass (needs review)

Every root fixture row carries at least one source URL outside OLBG, and the registered source hosts are the relevant governing bodies/leagues (for example [NHL's official schedule API](https://api-web.nhle.com/v1/schedule/2026-10-21), [WTA's official tournament listing](https://www.wtatennis.com/tournaments), [World Snooker Tour rankings](https://www.wst.tv/rankings/), and [LNR's Top 14 calendar](https://top14.lnr.fr/calendrier-et-resultats)). The structural audit did not fetch those URLs or compare individual names, dates, standings and statistics against current page contents. Consequently it supports “source link present,” not a new “line-by-line source verification completed” claim.

## Recommended follow-up

1. Recheck every factual prediction clause against the official source(s) linked on that prediction; delete or qualify anything unsupported and keep the 30-word minimum.
2. Keep the five cross-checked fixtures visibly labeled and align summary language with the 129/5 status split.
3. For any row whose official page is unavailable, ambiguous or contradictory, leave the disputed value blank where appropriate and retain it on the Flagged for Review page.
4. Rerun both validators after any data or page changes and verify the GitHub Pages deployment separately.

## Source register and verification performed

The dataset's source register, including official provider names, roles and links, is [`data/sources.json`](../data/sources.json). This audit verified JSON consistency and source-link presence by reading the checked-in files, and reran the two validators listed above. It did not make a fresh official-site fetch; see F1–F3 before treating source-dependent prose or values as newly verified.
