# REPO_AUDIT_5E86DC1A — root primary-desk line-by-line audit

Session: `5e86dc1a-olbg1` (branch `arena/5e86dc1a-olbg1`). Task T80, claimed 2026-10-23T19:30Z — takeover of the stale T9 claim (session `f7fa77fc-olbg1`, last commit 2026-10-21T05:26Z, idle >60 minutes; handoff logged in §4 of COORDINATION.md).

## Scope

Audited files: `data/fixtures.json`, `data/lines.json`, `data/predictions.json`, `data/sources.json`, plus the root HTML tables they feed (`index.html`, `sports/<15>.html`, `predictions.html`, `markets.html`, `flagged.html`). The audit covers exactly the 15 sports named in the brief: Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball, Rugby League.

Method: every row was checked against its recorded verification ledger and official source links. No live re-fetch was possible this session — sandbox egress is limited to GitHub/npm/PyPI, so official governing-body feeds could not be re-read. Rows therefore rest on the verification recorded at capture; nothing was inferred or filled in, and every unconfirmed gap is left blank and flagged (see the register below). This is a provenance audit of the retained record, not a recertification of live sporting truth.

## 1. Fixture register (data/fixtures.json)

| Metric | Value |
|---|---|
| Total captured fixtures | 134 |
| In the 15 brief sports | 124 |
| Outside the brief (retained, not published as covered) | 10 (Aussie Rules 9, eSports 1) |
| State — today 23 Oct 2026 (UTC) | 15 in-scope (16 all sports) |
| State — upcoming 24–28 Oct 2026 | 29 in-scope (37 all sports) |
| State — elapsed before 23 Oct 2026 19:30 UTC | 30 in-scope (49 all sports) |
| State — time not stated by publisher | 32 in-scope (32 all sports: Tennis 11, Snooker 11, Cricket 5, Golf 4, plus untimed others) |
| Rows missing governing-body sources | 0 |
| Rows with invalid status | 0 (all `verified` / `cross-checked` / `unverified`) |
| Rows missing verification ledger block | 0 |

Per-sport in-scope counts: Golf 4, Volleyball 8, Rugby Union 12, Cricket 8, Snooker 11, Darts 16, Baseball 4, Gaelic Sports 4, Greyhounds 3, Tennis 11, Motor Racing 1, Handball 12, Ice Hockey 6, Basketball 17, Rugby League 7.

Every fixture row carries at least one HTTPS link to a league/governing-body/tour source (NHL API, MLB stats API, NBA, EuroLeague, ATP/WTA, WST, PDC, NZC/ICC, LNR/Top 14, URC, NRL/IRL, EHF, PlusLiga, AFL, GAA, GBGB, PGA TOUR, Formula 1 — recorded in `data/sources.json`). OLBG itself is treated as discovery only, never as verification, per §0.5.

## 2. Originated lines (data/lines.json)

| Metric | Value |
|---|---|
| Priced H2H books | 126 (one per two-sided fixture; event-only sports — Golf, Greyhounds, Motor Racing — have no match-winner market and are published as event cards) |
| All prices inside the −250…+10000 window | yes (126/126) |
| Confidence — High / Medium / Low | 30 / 30 / 66 |
| High picks inside the 15 brief sports | 26 (plus 4 Aussie Rules, outside the brief) |
| Markets investigated per priced match | Match Winner, Handicap/Spread, Match Total (every line; missing totals carry an explicit unverified exception) |

High picks per in-scope sport vs the "five per sport" aim:

| Sport | High picks | Gap to 5 |
|---|---|---|
| Ice Hockey | 4 | 1 |
| Darts | 4 | 1 |
| Basketball | 3 | 2 |
| Cricket | 3 | 2 |
| Rugby League | 3 | 2 |
| Baseball | 2 | 3 |
| Tennis | 2 | 3 |
| Snooker | 2 | 3 |
| Handball | 2 | 3 |
| Rugby Union | 1 | 4 |
| Golf | 0 | 5 (event-only — no H2H market) |
| Volleyball | 0 | 5 |
| Gaelic Sports | 0 | 5 |
| Greyhounds | 0 | 5 (event-only — no H2H market) |
| Motor Racing | 0 | 5 (event-only — no H2H market) |

Gaps are published blank, not filled: no additional verified inputs exist in this snapshot to support more High picks.

Probability bar: no originated price in the window independently clears a strict greater-than-70% model win probability (best originated price is −250, ≈71% implied, at 68.1% desk conviction). The desk "High" tier = conviction ≥0.60 inside −250…+10000, and this weaker bar is disclosed on every pick page rather than represented as >70%.

## 3. Predictions (data/predictions.json)

| Metric | Value |
|---|---|
| Total predictions | 30 (exactly matching the 30 High desk picks) |
| In the 15 brief sports | 26 (4 Aussie Rules predictions are outside the brief) |
| All ≥30 words | yes |
| Selection equals the line pick | yes (30/30) |
| Pick named inside the prose | yes (30/30) |
| Bet line quotes pick + price | yes (30/30) |
| Flagged in-window | yes (30/30) |
| Official source(s) on every prediction | yes (30/30) |
| Duplicate 6-word n-grams | none |
| Prose compliance this session | 6 entries re-written to remove the prohibited words "model" and "verified": mlb-849802, snk-higgins-jones, snk-zhang-williams, cric-nz-ind-t20-1, rl-wc26-eng-fra, hand-ehf-12046. All remain ≥30 words with clear "Selection:" labels. |

Entry `aflw-r11-02` (Aussie Rules, outside the brief) was also re-written for consistency.

## 4. Sources register (data/sources.json)

20 entries, all HTTPS. `olbg` (sitemap/sport hubs) is marked discovery-only; every other entry is a league/governing-body/tour host. Fixture-level sources match the register.

## 5. Flagged-for-review register (published on flagged.html)

18 items: coverage gaps for event-only sports (Golf F-01, Greyhounds F-02, Motor Racing F-03), confidence gaps below the five-per-sport aim (F-04…F-14), the >70% bar disclosure (F-15), untimed fixtures left blank (F-16), out-of-scope retained data (F-17), and the prose-compliance correction (F-18). Two archived link targets retained for earlier sessions (F-257E-20 status gaps, F-257E-21 statistical expiry). Plus two standing notices: 49 elapsed fixtures are a historical record only, and this session could not independently re-fetch official feeds.

## 6. Irregularities flagged for manual review

None of these block publication; all are listed on the Flagged for Review page with source links:

1. No live re-verification possible this session (sandbox egress = GitHub/npm/PyPI only). All fixture facts are historical observations pending a manual re-check against the live official page.
2. `www.premrugby.com` and `www.galwaygaa.ie` were missing from `pipeline/config.py` PUBLISHERS (the canonical site's publisher allowlist) although both are official organisers and appear in `scripts/validate.py`'s allowlist; both hosts were added to `pipeline/config.py` (one line each, no data changed).
3. Aussie Rules and eSports fixtures remain captured in `data/fixtures.json` but are not published as covered categories for this brief.
4. Zero High picks clear the strict >70% model-probability bar requested in the brief; the desk's disclosed ≥0.60 tier is used instead.

## Verification performed

- `python3 scripts/validate.py`: 0 errors (3 pre-existing warnings in `f7fa77fc/flagged.html`, internal-policy citations only).
- `python -m pipeline.validate --site .`: 0 errors (canonical snapshot/manifest/links gate).
- `python -m unittest discover -s tests/pipeline` and root tests: 177 OK.
- `data/predictions.json` mirrored byte-identically to `f7fa77fc/data/predictions.json` (mirror-integrity rule).

No manual user input was required; all work was done from the retained repo record with no invented values.