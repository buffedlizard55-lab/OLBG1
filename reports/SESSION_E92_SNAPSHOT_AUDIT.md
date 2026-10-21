# Independent snapshot-integrity audit — session `e92c2bf4-olbg1`

**Audit date:** 2026-10-21 (UTC)  
**Scope:** Read-only structural audit of the committed snapshot, model outputs, validators, and all published HTML trees. This report does **not** certify match facts against live official feeds. No live official-source page was fetched as part of this audit; links below are references for manual verification, not evidence that their current contents were checked here.

## Summary

The root data exports are internally aligned and the existing root validator passes. Every one of the 134 fixture records has at least one HTTPS source URL, including at least one non-OLBG source URL. However, the current tests establish URL presence and file/link structure, **not** that a source is genuinely official, reachable, current, or supports each displayed field. The dataset is a dated static snapshot, not a continuously updated feed.

## Checks performed

1. Ran `python3 scripts/validate.py`: **54 root/mirror HTML pages; 0 errors, 0 warnings**. This is the repository's own structural/model gate.
2. Ran `python3 scripts/ebfbd966_validate.py`: **133 matches, 18 pages, 4 writeups; pass**.
3. Independently checked local relative `href`/`src` targets across every HTML file in the checkout, resolving directory URLs to their `index.html`: **130 HTML pages, 3,402 relative references, 0 unresolved targets**. This checks local files only; it does not issue HTTP requests to live external links.
4. Compared the two fixture arrays in `data/fixtures.json`, the canonical dataset in `datasets/matches_full.json`, model lines, and prediction IDs:
   - 134 fixture rows in each exported fixture copy; fixture arrays are identical and fixture IDs match the full-dataset IDs.
   - Fixture statuses: **129 `verified`, 5 `cross-checked`** as recorded in the data; this audit did not independently re-confirm those statuses.
   - All 134 fixture rows have at least one HTTPS source URL and at least one URL whose host is not `olbg.com`; 31 distinct non-OLBG hosts occur. This is a URL-presence test, **not** official-domain allowlisting or source-content verification.
   - 126 two-sided fixtures have matching originated line records; no two-sided fixture is unpriced in the line export.
   - 31 high-confidence line IDs match the 31 prediction IDs; the existing validator checks prediction length and selection consistency.
5. Counted market signatures in `data/lines.json`: 90 matches have Winner + Handicap + Total; 35 have Winner + Draw No Bet + Handicap + Total; 1 has Winner + Handicap only.

## Findings / flagged gaps

### A. Static snapshot is not auto-updating — **review before treating as current**

`data/fixtures.json`, `data/lines.json`, `data/predictions.json`, and `datasets/matches_full.json` are dated **2026-10-21**. The fixture window is **2026-10-21 through 2026-10-28**. The build scripts generate files from checked-in data; no scheduled refresh or live feed is established by the validator. Future readers should treat this as a dated snapshot and refresh/reverify the inputs before relying on it as a current fixture list.

### B. Eight multi-runner event cards have no originated event-market prices

The dataset contains **8 event-only cards** rather than head-to-head matches: four golf tournaments, one motor-racing Grand Prix, and three greyhound race cards. They are represented as event cards, but there are no corresponding entries in the 126-match line export. This is a documented modeling boundary in the current dashboard, but it does not satisfy a literal requirement to originate a line for every market on those events. Do not infer or fabricate prices; add sourced field/runner data and a suitable model, or keep the pricing blank and visibly flagged.

### C. One cricket match has no total market

`cric-nza-inda-fc1` (New Zealand A v India A) has a Winner and Runs/Wickets Handicap market, but no Total market. The root validator only requires Winner and Handicap, so its success does not detect this missing market. This should be surfaced as a row-level coverage exception or supplied only after a documented, sport-appropriate total model is available.

### D. Validator does not prove source authority or freshness

`python3 scripts/validate.py` requires fixture source URLs to start with `https://` and checks that each row carries a link. It does not verify that the hostname belongs to a governing body, fetch the page/API, confirm an HTTP success response, or compare the page's values to the record. Likewise, its prediction-source check tests that a source list exists, not that the prediction's factual claims are individually supported. Therefore the printed `VALIDATION PASSED` means structural/model checks passed; it must not be described as a fresh, line-by-line official-source audit.

For manual source review, see the link register at [`data/sources.json`](../data/sources.json), the match-level source URLs in [`data/fixtures.json`](../data/fixtures.json), and the methodology in [`methodology.html`](../methodology.html). The source domains represented in this snapshot include the official sites/APIs named in those files (for example NHL, NBA, MLB, ATP, WTA, PDC, WST, ICC, EHF, AFL, NRL, PGA TOUR, FIA/F1, GBGB, and league/federation sites). Their presence in the data is not a claim that this audit fetched or revalidated them.

### E. Source presence is not uniform proof for every field

The audit established a source-link presence for each fixture record, but did not verify that each source URL supports every field in the record (time, venue, participants, competition, form inputs, rankings, or derived lines). Several match starts are explicitly marked as UTC-time-unconfirmed in the rendered pages; preserve those blanks/labels unless an official order of play or schedule confirms the exact time.

## Recommendations for the integration owner

- Keep the snapshot timestamp/window prominent and add a refresh date whenever official feeds are rechecked.
- Publish findings A–D on the dashboard's **Flagged for Review** page. The existing generated/shared dashboard and flag dataset are outside this audit's file scope, so this session has not edited them.
- Extend validation with an explicit governing-body host registry, per-row official-source requirement, market-coverage exceptions (event-only cards and the one no-total cricket match), and an optional fetch/checksum log. A host allowlist alone still cannot prove that a URL supports each claimed fact; that requires source-content review.
- Keep originated odds labeled as model estimates, separate from factual inputs and bookmaker prices.

## References

- [`data/fixtures.json`](../data/fixtures.json) — fixture snapshot and match-level sources.
- [`data/lines.json`](../data/lines.json) — originated market records.
- [`data/predictions.json`](../data/predictions.json) — high-confidence writeups and attached sources.
- [`datasets/matches_full.json`](../datasets/matches_full.json) — consolidated fixture records.
- [`datasets/flagged_for_review.json`](../datasets/flagged_for_review.json) — existing audit/upstream flags.
- [`data/sources.json`](../data/sources.json) — source URL register.
- [`scripts/validate.py`](../scripts/validate.py) and [`scripts/ebfbd966_validate.py`](../scripts/ebfbd966_validate.py) — validation gates.
