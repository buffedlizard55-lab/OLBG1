# Session `76950c25-olbg1` — live OLBG refresh, verification boundary and publication

**Capture time:** 2026-10-21T07:05Z (UTC)
**Capture target:** the 17 in-scope OLBG sport hubs (`/betting-tips/<Sport>/<sport_id>`)
**Machine-readable outputs:** `data/live_snapshot.json`, `data/live_diff.json`, `data/live_baseline.json`
**Public page:** `live-refresh.html` (root) and `/f7fa77fc/live-refresh.html` (mirror)
**Flagged items:** `flagged.html`, IDs `F-LIVE-01` … `F-LIVE-06`

---

## 1. What was asked

The desk brief requires a full list of **updated** matches for every sport in scope (all 17 OLBG
sports excluding soccer, boxing, UFC/MMA, American football, hurling, horse racing, cycling and
specials), with lines originated by us, a winner pick, a confidence tier, and written predictions
for the high-confidence picks — with no value ever inferred.

The previously published desk was built from a 05:25Z capture. Between that capture and this
session the OLBG hubs had moved, so the desk was showing stale tip consensus and was missing
cards that OLBG had since published. This session re-captured every hub, diffed the result
against the committed dataset, refreshed the upstream counters, and published everything that
could **not** be verified as an explicitly unverified row.

## 2. Capture method and coverage

Each hub was fetched once with a browser-class fetcher against the public OLBG URL. The capture
keeps, per card: OLBG `event_id`, sport, competition label (where OLBG prints one), event title,
the clock string exactly as OLBG rendered it, the market, OLBG's most-tipped selection, OLBG's
`x/y win tips (z%)` counter, and the event URL containing the `event_id`.

| Sport | OLBG ID | Cards captured | Hub URL |
|---|---|---|---|
| Tennis | 3 | 14 | https://www.olbg.com/betting-tips/Tennis/3 |
| Basketball | 4 | 14 | https://www.olbg.com/betting-tips/Basketball/4 |
| Golf | 5 | 10 | https://www.olbg.com/betting-tips/Golf/5 |
| Cricket | 7 | 9 | https://www.olbg.com/betting-tips/Cricket/7 |
| Snooker | 8 | 9 | https://www.olbg.com/betting-tips/Snooker/8 |
| Rugby Union | 9 | 15 | https://www.olbg.com/betting-tips/Rugby_Union/9 |
| Rugby League | 10 | 3 (2027 outrights only) | https://www.olbg.com/betting-tips/Rugby_League/10 |
| Baseball | 12 | 1 | https://www.olbg.com/betting-tips/Baseball/12 |
| Ice Hockey | 13 | 10 | https://www.olbg.com/betting-tips/Ice_Hockey/13 |
| Motor Racing | 14 | 3 | https://www.olbg.com/betting-tips/Motor_Racing/14 |
| Darts | 15 | 14 | https://www.olbg.com/betting-tips/Darts/15 |
| Handball | 20 | 15 | https://www.olbg.com/betting-tips/Handball/20 |
| Volleyball | 21 | 14 | https://www.olbg.com/betting-tips/Volleyball/21 |
| Aussie Rules | 22 | 0 — "No tips found" | https://www.olbg.com/betting-tips/Aussie_Rules/22 |
| eSports | 23 | 0 — "No tips found" | https://www.olbg.com/betting-tips/eSports/23 |
| Gaelic Football | 25 | 4 | https://www.olbg.com/betting-tips/Gaelic_Football/25 |
| Greyhounds | 28 | 6 | https://www.olbg.com/betting-tips/Greyhounds/28 |

**Total: 141 cards across 15 sports with live tips; 2 in-scope sports returned no tips.**

## 3. Diff against the committed dataset

Reproduce with:

```bash
python3 scripts/live_diff.py     # data/live_snapshot.json + data/live_baseline.json -> data/live_diff.json
```

`data/live_baseline.json` freezes the pre-refresh OLBG fields committed at `abe1dd9`, so the diff
stays stable even after the consensus overlay has rewritten `data/fixtures.json`. The pipeline is
idempotent: a second full run reproduces byte-identical `data/live_diff.json` and
`live-refresh.html` (sha256-checked in this session).

| Measure | Count |
|---|---|
| Live cards captured | 141 |
| Dataset rows | 134 |
| Dataset rows carrying an OLBG `event_id` | 87 |
| Joined to a dataset row by `event_id` | 69 |
| Consensus or selection changed since the committed capture | 47 |
| …of which the most-tipped **selection flipped** | 20 |
| Live cards with **no** dataset row (unverified) | 72 |
| Dataset rows not on the recaptured first screen | 18 |

### 3.1 Selection flips (20)

Examples, all visible in full on `live-refresh.html`:

| OLBG event | Committed capture | 07:05Z recapture |
|---|---|---|
| 902074 Sorana Cirstea vs Sara Bejlek | Sara Bejlek, 3/6 (50%) | Sorana Cirstea, 5/8 (63%) |
| 902083 Stefanos Tsitsipas vs Mikhail Kukushkin | Tsitsipas 2-0, 1/1 | Mikhail Kukushkin, 2/2 |
| 9934 John Higgins v Jak Jones | John Higgins, 3/6 | Jak Jones, 7/9 (78%) |
| 32329 Ross Smith vs Karel Sedlacek | Ross Smith, 4/8 | Karel Sedlacek, 5/9 |
| 12045 Dinamo Bucuresti vs Skanderborg | Dinamo Bucuresti, 4/11 | Skanderborg, 5/12 |
| 12047 HC Kriens Luzern vs KS Kielce | Tie, 3/6 | HC Kriens-Luzern, 3/7 |
| 534892 IND Pacers @ NO Pelicans | IND Pacers, 2/4 | NO Pelicans, 3/5 |
| 534890 CHA Hornets @ BKN Nets | CHA Hornets, 2/4 | BKN Nets, 2/3 |
| 160789 TB Rays @ MIL Brewers | MIL Brewers money line, 4/5 | Over 5.50 total, 4/4 |

**Why this matters and what it does not change:** OLBG consensus is an upstream *opinion counter*,
not a sporting fact. The refresh therefore updates `olbg.consensus`, `olbg.selection`,
`olbg.market` and stamps `olbg.captured_utc`, keeping the superseded value in
`olbg.consensus_prior`. Fixtures, kick-off times, venues, records, ratings, originated prices,
picks and confidence tiers are **not** recalculated from OLBG and are unchanged by this pass.

### 3.2 Unverified upstream-only cards (72)

72 live cards have no verified dataset row: 10 volleyball, 9 tennis, 8 ice hockey, 8 rugby union,
6 basketball, 6 cricket, 6 handball, 6 golf, 4 greyhounds, 3 snooker, 3 rugby-league outrights,
2 motor racing and 1 Gaelic football. These are published on `live-refresh.html` with:

* the OLBG event link (upstream discovery only),
* the OLBG clock string **as rendered** (never converted into an asserted UTC time),
* the market, selection and tip counter,
* a red **Unverified** badge and the note "Blank — not confirmed from an official source".

No price, pick, confidence tier or prediction is produced for any of them.

### 3.3 Dataset rows not on the recaptured first screen (18)

Six basketball rows, five tennis rows, three handball rows, two darts rows, one volleyball row and
one greyhound card. OLBG renders roughly 20 cards per hub before a "Load More Tips" control,
so absence from the first screen is **not** evidence of cancellation or expiry. These rows keep
their governing-body kick-off times and are listed, with that caveat, on the Live Refresh page.

## 4. Verification performed in this session

| Check | Method | Result |
|---|---|---|
| OLBG tip counters / selections | Re-fetched all 17 hubs at 07:05Z | 141 cards captured; 69 joined by `event_id` |
| MLB World Series Game 2 | Official MLB StatsAPI schedule, 2026-10-24 | Confirmed gamePk **849802**, "World Series Game 2", Tampa Bay Rays at Milwaukee Brewers, American Family Field, `gameDate 2026-10-25T00:00:00Z` — https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-10-24 |
| Every other fixture fact | Not re-fetched this pass | Retained from the governing-body source recorded on each row; the gate is structural, not a fresh source fetch (see `F3` in the earlier audit) |
| Site integrity | `python3 scripts/validate.py` | 133 published HTML pages, **0 errors, 0 warnings** |
| Parallel board checks | `python3 scripts/ebfbd966_validate.py` | PASSED (133 matches) |

The refresh deliberately does **not** claim fresh official confirmation of the 72 new cards. That
is the honest boundary: they are labelled unverified rather than promoted.

## 5. Irregularities flagged for review

All six are published on `flagged.html` with their source links.

1. **F-LIVE-01-DRIFT** — 47 of 69 joined cards moved inside the capture window (20 selection
   flips). Published before/after on the Live Refresh page. No sporting value changed.
2. **F-LIVE-02-NO-OFFICIAL** — 72 live cards with no governing-body confirmation. Left blank,
   unpriced, and excluded from the 134-event verified count.
3. **F-LIVE-03-TRUNCATION** — 18 dataset rows absent from the first screen; the hub truncates at
   ~20 cards, so this is logged as a coverage gap, not an expiry.
4. **F-LIVE-04-EMPTY-HUBS** — Aussie Rules and eSports returned "No tips found"; Rugby League
   returned 2027 outrights only, while the desk carries 9 AFLW, 1 LoL Worlds and 7 RLWC26 rows
   from their governing bodies. Those rows keep the earlier OLBG capture timestamp.
5. **F-LIVE-05-ZERO-TIPS** — Golf `event_id=101909` still renders an empty tip counter / 0% share
   on an each-way outright card.
6. **F-LIVE-06-MLB-CLOCK** — OLBG labels TB Rays @ MIL Brewers "24 Oct 01:00"; the official MLB
   StatsAPI schedules the same game for `2026-10-25T00:00:00Z` (≈19h later even after reading the
   OLBG clock as UTC-4). The desk keeps the official time.

## 6. Reproduce

```bash
python3 scripts/live_diff.py       # rebuild the diff from the frozen baseline + committed capture
python3 scripts/build_dataset.py   # apply the consensus overlay + publish findings
python3 scripts/origin_lines.py    # re-price (deterministic; unchanged by a consensus refresh)
python3 scripts/build_site.py      # 28 root pages + 28 mirror pages
python3 scripts/validate.py        # strict gate, must print VALIDATION PASSED
```
