# Session 99582dd3 — T9958 independent offline verification, reconciliation and 15-sport desk

**Branch:** `arena/99582dd3-olbg1` · **Task:** T9958 (COORDINATION.md §73)
**Build timestamp (deterministic):** 2026-10-23T19:45:00Z
**Desk:** <https://buffedlizard55-lab.github.io/OLBG1/99582dd3/index.html>

## 1. Environment constraint and method

This sandbox has outbound HTTPS only to `github.com`, `api.github.com`,
`codeload.github.com`, `registry.npmjs.org`, `pypi.org` and
`files.pythonhosted.org`. Live probes at session start confirmed that
`olbg.com`, `api-web.nhle.com`, `statsapi.mlb.com`, `atptour.com` and
`pdc.tv` (and every other sporting host) fail at TLS egress. A new live OLBG
harvest or a fresh official-source recertification was therefore impossible,
and none is claimed.

The session instead performs an independent **offline** audit of evidence
already captured and merged in the repository, principally the `8a900c04`
desk snapshot captured 2026-10-23T16:45Z — the only retained dataset with five
events for each of the fifteen brief-listed sports, 472 originated market
lines and 75 predictions, each row carrying an official governing-body URL.
Nothing is marked verified without a fetch, so inherited facts stay
attributed to their originating capture; values that fail a gate are blanked
or flagged, never inferred.

## 2. Gate suite (scripts/s99582dd3_audit.py)

| Gate | Checks |
|------|--------|
| G1 Provenance | ≥1 HTTPS official governing-body URL per row; OLBG is discovery-only; unregistered hosts flagged; OLBG-only cards stay unpriced |
| G2 Arithmetic | fair decimal = 1/p (±0.011); two-way mass sums to 1 (±0.011); American re-derived from clamped probability (mirrors source formula; 1.5% relative tolerance for long shots) |
| G3 Grade/window | High ⇔ p > 0.70 and −250 ≤ American ≤ +10000 (decimal 1.40–101.00); >70% chalk shorter than −250 suppressed to medium; medium otherwise ≥ 57.5% |
| G4 Timing | each start classified today / upcoming / elapsed at the build timestamp; elapsed rows leave the current executive summary |
| G5 Prose | ≥30 words, accurate word-count field, no internal vocabulary (`model`, `verified`), explicit selection, participant named, 7-gram uniqueness scan |
| G6 Direction | selection sentence scanned for a non-favorite described over the priced favorite; historical form and distance phrases excluded |
| G7 Cross-desk | token matching (Jaccard ≥ 0.5) against 429a54a2, 3ee30bba and 7f000cb6 winner prices; opposite favorites = high-severity conflict; same-side gap >15 pts = divergence |

## 3. Headline results

- **15/15 brief sports, 5 audited events each = 75 events** (Golf, Volleyball,
  Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds,
  Tennis, Motor Racing, Handball, Ice Hockey, Basketball, Rugby League).
- Timing at build: **52 upcoming, 6 today, 17 elapsed** (elapsed rows retained
  as historical pre-match records only).
- **472 markets** re-checked arithmetically; **zero hard failures** — every
  stored price and grade reproduces under the published rules.
- **45 current High recommendations** with future starts; **4 of them carry a
  cross-desk conflict/divergence badge** and are held out of the clean
  executive summary. 59 High recommendations exist including the elapsed card.
- **75/75 predictions pass the hard prose gates** (63–86 words each); two minor
  repeated-phrase findings and one directional-clause finding are flagged,
  prose retained with the finding attached.
- **37 distinct official source hosts**, every cited URL on a curated
  governing-body/league/tour domain.
- **18 flags**: 6 high, 9 medium, 2 low, 1 info.

## 4. Findings requiring manual review (all on `/99582dd3/flagged.html`)

### High severity — cross-desk directional conflicts (6)

Two independent retained desks price opposite match-winner favorites. They
cannot be reconciled without re-fetching the official feeds, which this
session's network policy blocks.

1. **IH01 Chicago Blackhawks v Montreal Canadiens (NHL, 2026-10-24)** — 8a900c04
   prices Chicago 56.0% (−127); 429a54a2 prices Montreal 71.4% (−250); 7f000cb6
   prices Montréal 59.8% (−149). Sources:
   [NHL schedule](https://api-web.nhle.com/v1/schedule/2026-10-23),
   [NHL injury update](https://www.nhl.com/news/montreal-canadiens-nick-suzuki-injury-status-update-october-22-2026).
2. **IH02 Colorado Avalanche v Tampa Bay Lightning (NHL)** — 8a900c04 Colorado
   52.7% (−111); 429a54a2 Tampa Bay 74.1% (−286).
3. **IH04 Philadelphia Flyers v Anaheim Ducks (NHL)** — opposite lean in both
   429a54a2 (Anaheim 52.6%) and 7f000cb6 (Anaheim 60.1%) versus 8a900c04
   (Philadelphia 60.8%).
4. **BB03 Tampa Bay Rays v Milwaukee Brewers (MLB)** — 7f000cb6 prices
   Milwaukee 65.7% (−192); 8a900c04 prices Tampa Bay 55.5% (−125). Name
   matching cannot distinguish World Series rematches; the flag says so.
   Source: [MLB schedule API](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-18&endDate=2026-10-27&hydrate=team,probablePitcher,linescore).

### Medium severity (9)

- **G7-DIVERGENCE IH05 Edmonton Oilers v Toronto Maple Leafs** — same favorite
  in both desks but probabilities differ by 16.0 points (80.2% vs 64.2%).
- **G6-DIRECTION GF01 Corey Conners v Seamus Power (PGA Bermuda)** — the
  selection sentence adds "Conners over Seamus Power in 72-hole match play"
  while the match-winner line prices Power as the 70.9% favorite.
  [PGA Tour leaderboard](https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard).
- **7× G1-OLBG-UNCONFIRMED** — OLBG hub cards (Pro D2, Brazilian Superliga,
  CSA T20, Liga ASOBAL, Metal Ligaen, Kinsley greyhounds, PLK) with no retained
  official confirmation; kept unpriced and off the slate, OLBG discovery link only.

### Low (2) and info (1)

- Two shared seven-word phrases across prediction pairs VB01/VB05 and
  DA03/DA05 (uniqueness nit, prose retained).
- **G3-CLUSTER (info):** all 59 High probabilities fall inside 0.7045–0.7140.
  The originating engine explicitly builds alternate lines nearest p≈0.708,
  so the cluster on the −250 boundary is a calibration shape to review, not 59
  independent strong edges.

## 5. Verification performed

- `python3 scripts/s99582dd3_audit.py --now 2026-10-23T19:45:00Z` — deterministic,
  byte-identical across repeated runs.
- `python3 scripts/s99582dd3_validate.py` — **0 errors, 0 warnings** across 24
  pages: page structure, internal link resolution, external-HTTPS row sourcing,
  grade invariants, prose gates and determinism.
- `python3 -m unittest discover -s tests/pipeline` — **187 tests OK** including
  10 new `test_desk_99582dd3.py` contract tests.
- `python3 -m unittest discover -s tests -p 'test*.py'` — preserved suite OK.
- `python3 -m pipeline.validate --site .` — **0 errors** (canonical gate).
- `python3 scripts/validate.py` — **0 errors**, only the three pre-existing
  `f7fa77fc` warnings.
- `node --check` on the desk JavaScript; CSP meta tag permits only same-origin
  resources; no external scripts, fonts or trackers.

## 6. Limitations

No remote page was fetched this session, so fixture status, injuries, form and
statistics are not recertified as current; they are inherited from the cited
2026-10-23 captures. Fair prices are experimental 1/p values with no bookmaker
margin, quote or availability. Cross-desk name matching cannot tell repeated
team pairings (playoff rematches) apart. Elapsed cards are history, not advice.

## 7. Files

- `99582dd3/**` — 24 static pages and desk assets.
- `data/99582dd3/**` — `audit.json`, `slate.json`, `flags.json`,
  `predictions_gated.json`, `sources.json`, `cross_desk.json`, `slate.csv`,
  `markets.csv`, `flags.csv`.
- `scripts/s99582dd3_audit.py`, `scripts/s99582dd3_build.py`,
  `scripts/s99582dd3_validate.py`.
- `tests/pipeline/test_desk_99582dd3.py` (10 offline tests).
- Append-only COORDINATION.md §73.
