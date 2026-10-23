# Session `6b47ea39-olbg1` — T6B47 consolidated gap-closing desk

**Build:** 2026-10-23T21:30:00Z · **Branch:** `arena/6b47ea39-olbg1` · **Baseline:** `main` @ `5cb7c69` (PR #193)

## 1. Why this desk exists

Eight desks published a 23 October slate before this session. Three problems recurred across them, and this
task is aimed at those rather than at publishing a ninth parallel copy of the same numbers:

1. **The five-picks-per-sport promise is not met.** `496eaf02` headlines 51 High picks but only three of its own
   priced lines satisfy the brief's stated rule. `65331685` publishes 7. Golf, Snooker, Gaelic Sports and
   Greyhounds are empty or near-empty on every desk that applies the rule strictly.
2. **Cross-desk contradictions are published side by side without reconciliation.** After collapsing name
   variants across desks, **22 fixtures carry opposite favourites** on different desks in this slate.
3. **Prose drifts into templates and internal chatter**, and one desk credits the same scoreline to two
   different players in the same round.

## 2. Environment constraint (disclosed, not worked around)

Sandbox egress is GitHub / npm / PyPI only. Probes this session:

| Host | Result |
|---|---|
| `www.olbg.com` | TLS `SSL_ERROR_SYSCALL` |
| `api-web.nhle.com` | TLS `SSL_ERROR_SYSCALL` |
| `statsapi.mlb.com` | TLS `SSL_ERROR_SYSCALL` |
| `buffedlizard55-lab.github.io` | TLS `SSL_ERROR_SYSCALL` |

Therefore **nothing was re-certified**. Every fixture and fact keeps the official URL and the capture timestamp
of the desk that read it, and every page says so. This is a capability limit, not a verification result.

## 3. Method

* **Ingest** (`scripts/s6b47ea39_ingest.py`) — reads three retained desks only:
  `8a900c04` (75 events, 472 markets, form/injury/statistics notes, captured 16:45Z),
  `496eaf02` (81 fixtures, 460 outcomes, 20:30Z), `65331685` (62 fixtures, 723 prices, 20:40Z).
* **Coalesce** — the same club under different spellings is one fixture. "Papua New Guinea Kumuls" =
  "Papua New Guinea", "Llanelli Scarlets" = "Scarlets", "Helios Grizzlys Giesen" = "VC Giesen". 218 raw rows
  become **125 fixtures**. Every alias is kept and shown on the row.
* **Recompute** — every American price is re-derived from its decimal value; every probability from 1/decimal.
* **Re-gate** — seven documented rules decide publishability, with the rejection count for each rule published.
* **Write** — 29 predictions, each built only from the fact register that travels with the pick.

## 4. The structural finding

A −250 price is decimal 1.40 → **71.43% implied**. The brief's two conditions (>70% *and* −250…+10000) therefore
only both hold inside **70.00%–71.43%** — a band 1.43 points wide. Consequences, all visible in the retained data:

* Both evening desks cluster probabilities at 0.7045–0.7140 across unrelated matches and sports.
* `496eaf02` can headline 51 High picks while only **3** of its published outcomes satisfy the rule.
* Genuine strong favourites — Perugia at 89%, Ireland at 80%, Kiel at 82% — are all *shorter* than −250 and
  therefore outside the window the brief asks for.
* Five genuine high-confidence picks per sport inside that band cannot be produced from real markets.

This desk publishes both tiers separately and never relabels one as the other: **25 in-window** and **4
out-of-window** picks, plus **26 medium watchlist** rows, with the per-sport shortfall registered.

## 5. Deliverables

* `data/6b47ea39/` — `slate.json` (125 fixtures, 1,616 priced lines), `picks.json`, `predictions.json`,
  `flags.json` (13), `audit.json`, `repo_audit` content.
* `scripts/s6b47ea39_{ingest,audit,picks,predictions,build,validate}.py`
* `tests/pipeline/test_desk_6b47ea39.py` — 11 offline contract tests.
* `6b47ea39/` — 26-page dashboard: overview with today/tomorrow executive summary, picks, predictions,
  watchlist, all matches, filterable market explorer, flagged-for-review, repository audit, OLBG discovery,
  sources, methodology, and 15 sport subpages.

## 6. Findings register (published on `/6b47ea39/flagged.html`)

| ID | Severity | Finding |
|---|---|---|
| F01 | medium | 11 prices shorter than −1000 disagree with the 3-decimal price they were derived from (rounding only; none near the band edge) |
| F02 | high | The requested High window is 1.43 probability points wide (§4) |
| F03 | high | Desk 496eaf02 labels 51 picks High; only 3 satisfy its own published rule |
| F04 | high | High-tier probabilities cluster within two points of the 70% threshold |
| F05 | high | 22 fixtures carry opposite favourites on different desks |
| F06 | medium | 38 lines differ by ≥0.10 decimal between desks |
| F07 | medium | 1 row still labelled "upcoming" after its official start |
| F08 | high | Greyhound, motor-race and stroke-play golf events modelled as two-sided matches with a constructed "Field" side |
| F09 | high | The identical 4-6 7-6(5) 7-6(5) scoreline is credited to two different winners on adjacent rows (496eaf02 TN01/TN02) |
| F10 | medium | 32 inherited prose lines fail a written-rule check (internal vocabulary, length, or repeated six-gram) |
| F11 | medium | 6 source links are media, aggregator or wiki rather than governing body |
| F12 | medium | 1 fixture carries no official source link |
| F13 | info | 65 of 125 fixtures rest on a single desk |

## 7. Repository findings (published on `/6b47ea39/repo-audit.html`)

* **Resolved upstream** — `scripts/se58210b8_predictions.py` carried committed git conflict markers at this desk's
  baseline, breaking the module and one test on `main`. Peer session `3c021b49-olbg1` restored the known-good
  version in PR #194 (merge `95cca9f`) while this desk was open; re-checked after rebase, zero markers remain.
* **High** — the canonical landing page shows "Snapshot 21 Oct 2026" while `data/current/snapshot.json` is
  2026-10-22T12:29:50Z, i.e. 33 hours old against `FIXTURE_TTL_HOURS = 6`.
* **High** — `pipeline/config.py:36` excludes OLBG hurling (id 26) although "Gaelic Sports" covers both 25 and 26;
  the 8a900c04 desk uses `/betting-tips/Hurling/26` for Gaelic Sports.
* **Medium** — `aussie-rules` (22) and `esports` (23) are inside the canonical scope but outside the brief's 15.
* **Medium** — 41 desk namespaces, 45 data namespaces, 227 scripts; nothing on the root site says which to trust.
* **Low** — 105 MB tree, 41 MB of it `data/`; `markets.html` is 2.2 MB.

## 8. Gates

| Gate | Result |
|---|---|
| `python3 scripts/s6b47ea39_validate.py` | **PASSED** — 26 pages, 29 picks, 29 predictions, 13 flags; every relative link resolves |
| `python3 -m unittest tests.pipeline.test_desk_6b47ea39` | **11 tests OK** |
| `python3 -m unittest discover -s tests -p 'test*.py'` | **38 tests OK** |
| `python3 -m pipeline.validate --site .` | **0 errors** |
| `python3 scripts/validate.py` | **0 errors** (3 pre-existing `f7fa77fc` warnings) |
| `python3 -m unittest discover -s tests/pipeline` | **258 tests OK** on the rebased branch (the two baseline failures were fixed upstream in PR #194) |

## 9. Limits, stated plainly

* No OLBG page was harvested and no official page was re-read in this session.
* Prices are this project's own estimates, inherited from the desks named on each row, not bookmaker quotes.
* Fixture facts are inherited; a human should re-open the linked official page before acting on any row.
* The five-per-sport target is **not** met: 29 High picks, with Greyhounds at zero. The gap is registered on the
  picks page with the rule that caused it rather than filled with invented numbers.
