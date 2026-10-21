# Independent Structural Audit — OLBG Dashboard Snapshot

**Audit session:** `5a353e83-olbg1` (**T40**)<br>
**Audit time:** `2026-10-21T07:57Z` UTC<br>
**Snapshot:** latest merged-main baseline `6d26d5ec28b074d2c5000f536fe67ec7f922d64e` (PR #43 / session `984d417f`, including PR #42); PR #40 state: `open (conflicting)`.<br>
**Scope:** root T34 desk + `/f7fa77fc/` mirror, separate `/c17a9192/` (217 events) and `/984d417f/` (145 events) dashboards, saved verification register, and all static HTML workspaces.
**Boundary:** this session performed **no outbound fetches** to OLBG or any governing body. It reviewed repository content and ran local gates. An HTTPS link or allowlisted host is not proof that the linked page was opened or supports the claim.

## Snapshot reconciliation

- **Fixtures/events:** 134 rows across 17 in-scope sports: 126 head-to-head and 8 event-only cards. Each primary match row has recorded source link(s); source relevance is not established by this structural scan.
- **Fixture status labels:** 128 `verified`, 5 `cross-checked`, 1 `unverified`. These are not a count of rows freshly re-read in the T34 pass.
- **Originated H2H books:** 126; confidence distribution High 31, Low 61, Medium 34. These are independent model estimates, not source facts or copied bookmaker prices.
- **High-pick write-ups:** 31; stored text length 49–82 whitespace-separated words. The local validator checks joins, sources and the 30-word minimum.
- **Live OLBG capture:** 141 cards at `2026-10-21T07:05Z`; 17 hubs attempted, 15 with tips, 2 without. See [Live Refresh](../live-refresh.html); this is upstream discovery, not governing-body confirmation.
- **Feed comparison:** 69 joined, 47 consensus/selection changes, 20 selection flips, 72 upstream-only cards without a primary row, and 18 primary rows absent from the truncated first screen.
- **Flagged registry:** 42 systemic findings and 111 row notes; 32 rows have a missing UTC value recorded on [Flagged for Review](../flagged.html).
- **Scope ambiguity:** Aussie Rules (9), Gaelic Football (4) remain in the root taxonomy. Both separate `/c17a9192/` and `/984d417f/` taxonomies include Aussie Rules and Gaelic Football; this report does not assume that “football” means soccer only.
- **Task-ID collision:** this session's provisional T36 conflicted with PR #42's T36–T39 assignments. The active audit is T40; the other session's rows are preserved in COORDINATION.md §29, and this report does not claim T36–T39.

### Separate, newer `/c17a9192/` dashboard (PR #41)

- **217 events**, 200 marked as live OLBG-listed and 17 official blind-spot cards; 217 line records and 46 high-confidence predictions. Status split: 151 fully `verified`, 53 `tour_calendar_verified`, 13 `unverified` and flagged.
- Event-type counts in the JSON are 121 two-way H2H + 65 three-way H2H = 186 H2H, plus 25 outright + 6 race = 31 non-H2H. However, the coordination/PR headline says 192 H2H + 25 multi-runner; the category split is inconsistent even though both totals equal 217.
- Field blanks by verification tier are:

- `tour_calendar_verified` (53 rows): blank `start_utc` 17, `venue` 11, `stat_a` 32, `stat_b` 32.
- `unverified` (13 rows): blank `start_utc` 2, `venue` 7, `stat_a` 7, `stat_b` 13.
- `verified` (151 rows): blank `start_utc` 17, `venue` 0, `stat_a` 0, `stat_b` 0.

- Rows marked `unverified` still have some fields populated: `start_utc` 11, `venue` 6, `stat_a` 6. Their flags may explain which pieces are upstream-only, but the row-level status does not itself identify every unconfirmed field. Review each populated value against an official source; blank unsupported fields rather than treating a general host link as proof.
- The namespace contains 45 source-register records, 281 event-level official source links, 19 repository-audit findings, 12 OLBG defects, and 137 event-level manual-review entries. The independent T40 scan covered 24 pages and 1185 table rows: all 1185 have HTTPS, while 1151 have a host in the sports governing-body allowlist. The remaining 34 are concentrated in `c17a9192/flagged.html` 4, `c17a9192/repo-audit.html` 5, `c17a9192/reverse-engineering.html` 24, `c17a9192/sources.html` 1 and link to OLBG taxonomy/defect or repository-audit sources; they are not all fixture rows. The c17 validator checks official hosts on event JSON sources but only HTTPS presence on rendered table rows. See [the dashboard](../c17a9192/index.html), [markets](../c17a9192/markets.html), [predictions](../c17a9192/predictions.html), and [session audit](SESSION_C17A9192_AUDIT.md).

### Separate, newest `/984d417f/` dashboard (PR #42)

PR [#42](https://github.com/buffedlizard55-lab/OLBG1/pull/42) merged at `2026-10-21T07:47:01Z`; its separate dashboard lives at [`/984d417f/`](../984d417f/index.html). PR [#43](https://github.com/buffedlizard55-lab/OLBG1/pull/43) merged at `2026-10-21T07:49:42Z`; it syncs Round 11 AFLW alternate venues and prediction percentage provenance in the same separate namespace.

- **145 fixtures and 145 line books** across 17 sports, with **140 `verified` and 5 `cross-checked`** status labels. Event kind counts are 134 H2H and 11 field events. Lines carry 40 High / 34 Medium / 71 Low confidence; 40 prediction write-ups. These labels are in the repository snapshot and were not freshly source-checked here.
- Event records contain 258 source links: 248 to 33 recognized governing-body/tour hosts and 10 to OLBG upstream-discovery pages. All 145 fixture rows have at least one recognized governing-body source in the stored JSON. The source registry has 27 records; host recognition does not prove a link was opened or supports the claim.
- The line-by-line review records 11 repository-audit groups and 6 upstream OLBG defects. `flagged.json` has 127 rows. 84 fixtures list 100 individual `unverified_fields` markers; all named values are absent/empty in both the fixture and line JSON. However, the session report claims 64 unconfirmed fields explicitly blank. The stored markers total 100, not 64; reconcile whether those are different metrics before repeating the headline.
- The independent HTML scan found **23 pages and 591 `<tbody>` rows**: 585 have HTTPS and 478 have a recognized governing-body host. The 113 rows without such a host are concentrated in `984d417f/audit.html` 9, `984d417f/flagged.html` 5, `984d417f/markets.html` 72, `984d417f/reverse-engineering.html` 27, largely OLBG taxonomy/market, upstream-defect, and repository-audit tables. The 6 rows with no HTTPS are in `984d417f/audit.html` 6, in the cross-desk compliance matrix. The index and 17 sport-page fixture tables have 290/290 rows with recognized official hosts; the five flagged-page rows without one are repository/OLBG-defect records, not fixture data. The local 984 validator checks HTTPS on selected table pages, not an official governing-body host on every table row. See [dashboard](../984d417f/index.html), [markets](../984d417f/markets.html), [flags](../984d417f/flagged.html), [repository audit](../984d417f/audit.html), and [session report](SESSION_984D417F_AUDIT.md).

## Saved official-source re-verification — not re-certified here

The root T34 `data/verification.json` was generated at `2026-10-21T07:20Z`. Its action statuses are **41 confirmed + 33 corrected + 2 flagged + 58 not re-checked = 134 rows**. The source-pass ledger therefore records **76 of 134** rows as read/corrected/flagged and **58** as explicitly not re-read. “Corrected” includes a status downgrade; it is not necessarily a confirmed factual correction.

The fixture JSON's embedded verdicts reconcile as `{'confirmed': 41, 'conflict': 2, 'corrected': 32, 'not-rechecked': 58, 'unconfirmed': 1}`. One intentional status-taxonomy exception is:

- `cric-afg-ban-odi`: separate ledger `corrected`, embedded verdict `unconfirmed`, fixture status `unverified`; action: status downgraded from 'verified' to 'unverified' and flagged; date and venue remain as OLBG lists them, with nothing invented to fill the gap.

The `cric-afg-ban-odi` row is the one that the T34 record says has no official fixture page. It remains `unverified`, but its date, participants and venue are populated from OLBG rather than blank; its only fixture source is the ICC rankings page, which the project's own finding says publishes no fixtures. The T40 audit did not edit it, but records this as an unresolved mismatch with the standing instruction to leave unconfirmed facts blank. The separate verification record also names an NZC fixtures URL not listed in that fixture's sources:

- `cric-afg-ban-odi` is `unverified`; the verification ledger names [New Zealand Cricket official fixtures & results service](https://scoring.nzc.nz/fixtures) but that URL is absent from the fixture's source list (https://www.icc-cricket.com/rankings). Its evidence says no official fixture page was found.

The register has 27 named source records across 17 sports. The [Live Verification page](../live-verification.html) and [`data/verification.json`](../data/verification.json) preserve the row-level evidence. This audit read those local files only; it did not re-fetch any source.

### Verification chronology anomaly

The timestamps in the saved files do not form a consistent sequence:

- 42 embedded fixture verification blocks have checked_utc later than data/verification.json generated 2026-10-21T07:20Z (sample IDs: aflw-r11-01, aflw-r11-02, aflw-r11-03, aflw-r11-04, aflw-r11-05).
- COORDINATION.md §27 reports T34 run at 2026-10-21T09:05Z, later than verification.json generated 2026-10-21T07:20Z.
- COORDINATION.md §27 T34 run time 2026-10-21T09:05Z postdates PR #39 merge 2026-10-21T07:27:45Z.

The GitHub record says PR #39 merged at `2026-10-21T07:27:45Z`. The report preserves the contradictory timestamps rather than guessing which is wrong; the owner should reconcile them append-only in `COORDINATION.md`.

## Structural source-link review

- The primary `picks.html` and sport-detail pages, including the `/f7fa77fc/` mirror, were scanned for at least one HTTPS host recognized by `scripts/validate.py` on every match row. This checks URL shape/host only, not that the source supports each field.
- On `live-refresh.html`, the “Full Live Capture” table has **141 rows**: 69 with a recognized governing-body host and 72 OLBG-only. Across its capture, change and absent-row tables, **206 rows** total: 69 with a recognized governing-body link and 137 OLBG-only. The 72 upstream-only cards are discovery records, not verified fixtures.
- `live-verification.html` has **134 row-by-row entries**, 134 with a recognized official host. Its coverage-by-sport summary has 17 rows; 17 have no row-level HTTPS link. Under the literal “every table row” rule this is a presentation gap.
- Across **208 published HTML files**, the scanner found **4894 `<tbody>` rows**; **206 have no HTTPS link**. The total includes summary, methodology and preserved companion-workspace tables—not just fixture rows.

Pages with rows lacking any HTTPS anchor:

- [`aa4e9dbf/flagged.html`](../aa4e9dbf/flagged.html) — 27 row(s) with no HTTPS link in a `<tbody>` table.
- [`f7fa77fc/live-verification.html`](../f7fa77fc/live-verification.html) — 17 row(s) with no HTTPS link in a `<tbody>` table.
- [`f7fa77fc/methodology.html`](../f7fa77fc/methodology.html) — 17 row(s) with no HTTPS link in a `<tbody>` table.
- [`live-verification.html`](../live-verification.html) — 17 row(s) with no HTTPS link in a `<tbody>` table.
- [`methodology.html`](../methodology.html) — 17 row(s) with no HTTPS link in a `<tbody>` table.
- [`docs/markets.html`](../docs/markets.html) — 15 row(s) with no HTTPS link in a `<tbody>` table.
- [`analysis.html`](../analysis.html) — 14 row(s) with no HTTPS link in a `<tbody>` table.
- [`f7fa77fc/analysis.html`](../f7fa77fc/analysis.html) — 14 row(s) with no HTTPS link in a `<tbody>` table.
- [`docs/flagged.html`](../docs/flagged.html) — 13 row(s) with no HTTPS link in a `<tbody>` table.
- [`ebfbd966/markets.html`](../ebfbd966/markets.html) — 11 row(s) with no HTTPS link in a `<tbody>` table.
- [`ebfbd966/index.html`](../ebfbd966/index.html) — 7 row(s) with no HTTPS link in a `<tbody>` table.
- [`984d417f/audit.html`](../984d417f/audit.html) — 6 row(s) with no HTTPS link in a `<tbody>` table.
- [`aa4e9dbf/tennis.html`](../aa4e9dbf/tennis.html) — 6 row(s) with no HTTPS link in a `<tbody>` table.
- [`aa4e9dbf/cricket.html`](../aa4e9dbf/cricket.html) — 4 row(s) with no HTTPS link in a `<tbody>` table.
- [`aa4e9dbf/handball.html`](../aa4e9dbf/handball.html) — 4 row(s) with no HTTPS link in a `<tbody>` table.
- [`ebfbd966/high-confidence.html`](../ebfbd966/high-confidence.html) — 4 row(s) with no HTTPS link in a `<tbody>` table.
- [`docs/methodology.html`](../docs/methodology.html) — 3 row(s) with no HTTPS link in a `<tbody>` table.
- [`ebfbd966/methodology.html`](../ebfbd966/methodology.html) — 3 row(s) with no HTTPS link in a `<tbody>` table.
- [`aa4e9dbf/basketball.html`](../aa4e9dbf/basketball.html) — 2 row(s) with no HTTPS link in a `<tbody>` table.
- [`ebfbd966/sports/darts.html`](../ebfbd966/sports/darts.html) — 2 row(s) with no HTTPS link in a `<tbody>` table.
- [`aa4e9dbf/volleyball.html`](../aa4e9dbf/volleyball.html) — 1 row(s) with no HTTPS link in a `<tbody>` table.
- [`ebfbd966/sports/cricket.html`](../ebfbd966/sports/cricket.html) — 1 row(s) with no HTTPS link in a `<tbody>` table.
- [`ebfbd966/sports/snooker.html`](../ebfbd966/sports/snooker.html) — 1 row(s) with no HTTPS link in a `<tbody>` table.

## Remaining work and coordination boundaries

- **Root-scope AFLW repricing remains queued as T35.** T34 flags a mismatch between the root Round 10 ladder inputs and the official 2026 ladder for 16 of 18 clubs; nine root lines and three picks await the dedicated re-price. PR #41 and PR #42 contain re-priced alternatives only inside their separate namespaces; neither changed root `data/lines.json` or `data/predictions.json`.
- **New dashboards:** PR [#41](https://github.com/buffedlizard55-lab/OLBG1/pull/41) merged at `2026-10-21T07:32:28Z`; its separate dashboard lives at [`/c17a9192/`](../c17a9192/index.html). PR [#42](https://github.com/buffedlizard55-lab/OLBG1/pull/42) merged at `2026-10-21T07:47:01Z`; its separate dashboard lives at [`/984d417f/`](../984d417f/index.html). PR [#43](https://github.com/buffedlizard55-lab/OLBG1/pull/43) merged at `2026-10-21T07:49:42Z`; it syncs Round 11 AFLW alternate venues and prediction percentage provenance in the same separate namespace. Both dashboard namespaces remain separate from the root T34 dataset.
- **Parallel integration:** PR [#40](https://github.com/buffedlizard55-lab/OLBG1/pull/40) was `open (conflicting)` when checked at `2026-10-21T07:57:28Z` UTC. It overlaps source/data/validator/site/coordination work; T40 did not edit those shared files. Current task-board entries still show T9 `in progress`, T10 `queued`, T11 `queued`, T12 `queued`, T19 `in progress`; PR #40 proposes updates to T9–T12, but T19 remains a separate board item.
- **Local structural gates do not certify fresh source reads.** The primary validator checks each fixture's embedded verification block and source-host policy, but it does not load the separate `data/verification.json` file; its allowed verdicts include `not-rechecked`. It makes no live HTTP request. The 58 `not_rechecked` rows therefore remain an explicit verification gap despite a passing gate.
- **Table-link rule is not satisfied everywhere.** Primary fixture rows have recognized HTTPS sources, but the unlinked aggregate/methodology/companion rows listed above remain. No blanket claim is made that all such rows are sports facts.
- **Publication observation:** Pages API: `built`; workflow run [`39564737670`](success) — [https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39564737670](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39564737670); main SHA `6d26d5ec28b074d2c5000f536fe67ec7f922d64e`; observed `2026-10-21T07:57:28Z` UTC. This is GitHub API/workflow metadata only; T40 did not make a browser request to the published `github.io` content.
- **Other noted boundary:** the existing taxonomy includes Aussie Rules and Gaelic Football; the user's “football” exclusion remains ambiguous. No scope change was made.

## Local gates reproduced

`/usr/bin/python3 scripts/validate.py` — exit 0

```text
Primary data: 134 fixtures | 126 H2H line books | 31 high-confidence predictions
Validated relative links across 208 published HTML pages
Errors: 0   Warnings: 0

VALIDATION PASSED — primary provenance, exports, markets, writing rules, and site links are consistent
```

`/usr/bin/python3 scripts/ebfbd966_validate.py` — exit 0

```text
Matches: 133 | HIGH/MED/LOW: Counter({'LOW': 98, 'MEDIUM': 31, 'HIGH': 4})
Pages: 18 | Writeups: 4 (words: [117, 129, 119, 130])
VALIDATION PASSED
```

`/usr/bin/python3 scripts/ccb6bde2_validate.py` — exit 0

```text
validated 126 matches, 2031 markets, 19 high-confidence predictions, 636 internal links
VALIDATION PASSED
```

`/usr/bin/python3 scripts/c17a9192_validate.py` — exit 0

```text
PASS: 217 events across all 17 sports | 100% official allowlist | 46 unique human high-confidence predictions (min 57w, 0 shared 6-grams) | 19 repo audit items | 12 OLBG defects | 24 HTML pages & 1185 table rows verified with 0 broken links!
```

`/usr/bin/python3 scripts/s984d417f_validate.py` — exit 0

```text
VALIDATION PASSED 100%: 145 verified events across 17 sports | 40 unique human High predictions | 127 blank flags | 11 repo audit groups | 23 HTML pages | 2946 links & anchors verified with 0 errors.
```

`/usr/bin/python3 scripts/final_audit.py` — exit 0

```text
Wrote reports/FINAL_INTEGRATION_AUDIT.md: 134 primary rows, 31 high-pick rows, 16 archival table-link review entries.
```

## Audit findings

- **REVIEW:** The 984d417f audit report claims 64 unconfirmed fields explicitly blank, but fixtures.json lists 100 unverified_fields entries across 84 rows; all named fields are absent/empty in the fixture/line JSON. Reconcile the metric definition before repeating the headline count.
- **REVIEW:** PR #41/COORDINATION market-type headline says 192 H2H + 25 multi-runner, but data/c17a9192/matches.json contains 186 H2H (121 two-way + 65 three-way) + 31 non-H2H (25 outright + 6 race) = 217 total.
- **REVIEW:** Some c17a9192 rows carry overall `unverified` status while field values remain populated: start_utc=11, venue=6, stat_a=6. Field-level evidence must be reviewed; retain only values supported by an official source and blank the rest.
- **REVIEW:** Verification chronology is inconsistent: 42 embedded fixture verification blocks have checked_utc later than data/verification.json generated 2026-10-21T07:20Z (sample IDs: aflw-r11-01, aflw-r11-02, aflw-r11-03, aflw-r11-04, aflw-r11-05); COORDINATION.md §27 reports T34 run at 2026-10-21T09:05Z, later than verification.json generated 2026-10-21T07:20Z; COORDINATION.md §27 T34 run time 2026-10-21T09:05Z postdates PR #39 merge 2026-10-21T07:27:45Z
- **REVIEW:** One documented status downgrade is counted as `corrected` in the verification action ledger, `unconfirmed` in the embedded row verdict, and `unverified` in the fixture status: cric-afg-ban-odi. This is an action/status taxonomy distinction, not a confirmed match claim.
- **REVIEW:** An unverified fixture's per-row verification source URL is not present in that fixture's source list; inspect the cited official source/evidence pairing: cric-afg-ban-odi.
- **REVIEW:** 34 c17a9192 table rows have HTTPS links but no host in its governing-body allowlist: {'c17a9192/flagged.html': 4, 'c17a9192/repo-audit.html': 5, 'c17a9192/reverse-engineering.html': 24, 'c17a9192/sources.html': 1}. These are largely OLBG taxonomy/defect rows and repository-audit rows, not all fixture rows; custom HTML validation checks HTTPS presence, not allowlist membership per row.
- **REVIEW:** 984d417f has 6 table rows without HTTPS, concentrated in {'984d417f/audit.html': 6}; these are in the cross-desk repository-audit table, not event rows.
- **REVIEW:** 113 984d417f table rows have HTTPS but no recognized governing-body host: {'984d417f/audit.html': 9, '984d417f/flagged.html': 5, '984d417f/markets.html': 72, '984d417f/reverse-engineering.html': 27}. Most are OLBG taxonomy/market descriptions, repository audit, or upstream-defect records rather than event rows.
- **REVIEW:** The saved official-source ledger explicitly marks 58 of 134 fixture rows not_rechecked.
- **REVIEW:** The live OLBG capture has 72 upstream-only cards without a primary verified fixture row.
- **REVIEW:** Across the Live Refresh event tables, 137 rows cite OLBG but have no recognized governing-body source link.
- **REVIEW:** 18 primary fixture rows are absent from the recaptured first screen; the source report notes hub truncation, so absence is not cancellation evidence.
- **REVIEW:** The whole-tree source-link scan found 206 <tbody> rows with no HTTPS link across 4894 rows.
- **REVIEW:** The Live Verification page's 17 per-sport aggregate rows have no row-level HTTPS link.
- **REVIEW:** Scope is unresolved for football-coded sports included under the current taxonomy: {'aussie-rules': 9, 'gaelic-football': 4}.
- **REVIEW:** scripts/validate.py checks each fixture's embedded verification block, but does not load the separate data/verification.json register and explicitly allows `not-rechecked`; a passing gate confirms provenance shape, not fresh page reads.
- **REVIEW:** At the audited snapshot, the task board still records T9 `in progress`, T10 `queued`, T11 `queued`, T12 `queued`, T19 `in progress`. PR #40 is open (conflicting) and proposes coordination updates to T9–T12. T40 does not change those task rows.
- **REVIEW:** Root-scope T35 remains queued for nine AFLW lines and three picks; PR #41 and PR #42 contain separately namespaced AFLW re-prices, but neither updates root data/lines.json or data/predictions.json.

- None.

## Files and reproduction

- Structural audit: [`scripts/session_5a353e83_audit.py`](../scripts/session_5a353e83_audit.py)
- This report: `reports/SESSION_5A353E83_INDEPENDENT_AUDIT.md` and [HTML review page](SESSION_5A353E83_INDEPENDENT_AUDIT.html)
- Main audit pages: [All Lines](../picks.html), [Live Refresh](../live-refresh.html), [Live Verification](../live-verification.html), [Flagged for Review](../flagged.html), [Official Sources](../sources.html)

Reproduce offline from the repository root:

```bash
python3 scripts/session_5a353e83_audit.py \
  --audit-time 2026-10-21T07:57Z \
  --snapshot-main-sha 6d26d5ec28b074d2c5000f536fe67ec7f922d64e \
  --pr39-merged-at 2026-10-21T07:27:45Z \
  --pr40-number 40 \
  --pr40-state 'open (conflicting)' \
  --pr40-url https://github.com/buffedlizard55-lab/OLBG1/pull/40 \
  --pr40-checked-at 2026-10-21T07:57:28Z \
  --pr41-merged-at 2026-10-21T07:32:28Z \
  --pr41-url https://github.com/buffedlizard55-lab/OLBG1/pull/41 \
  --pr42-merged-at 2026-10-21T07:47:01Z \
  --pr42-url https://github.com/buffedlizard55-lab/OLBG1/pull/42 \
  --pr43-merged-at 2026-10-21T07:49:42Z \
  --pr43-url https://github.com/buffedlizard55-lab/OLBG1/pull/43 \
  --pages-api-status built \
  --pages-run-id 39564737670 \
  --pages-run-status success \
  --pages-main-sha 6d26d5ec28b074d2c5000f536fe67ec7f922d64e \
  --pages-run-url https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39564737670 \
  --pages-checked-at 2026-10-21T07:57:28Z
```
