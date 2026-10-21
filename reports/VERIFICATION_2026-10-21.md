# Fresh official-source verification — 2026-10-21 (session `b95dbd01-olbg1`, task T17)

This pass did what every earlier pass had explicitly *not* done: it re-opened the governing-body
pages and compared them with the published rows, field by field. The machine-readable ledger is
[`data/verification.json`](../data/verification.json) and the public page is
[`verification.html`](https://buffedlizard55-lab.github.io/OLBG1/verification.html).

**Headline:** 136 rows published · **59 re-checked today** (52 confirmed, 7 corrected) · 6 time
conflicts · 1 unconfirmed · 16 blocked by a gated publisher · 54 not re-fetched (labelled
"not re-checked" everywhere they appear).

---

## 1. Sources actually fetched

| Official URL | What it showed | What changed |
|---|---|---|
| `api-web.nhle.com/v1/schedule/2026-10-21` | 2 games on 21 Oct; 12 on 22 Oct (incl. NSH@BOS, NYR@TOR) with venues | 4 NHL rows confirmed |
| `api-web.nhle.com/v1/standings/2026-10-20` | Live feed (`standingsDateTimeUtc 2026-10-21T07:05Z`): BOS 7-2-1; VGK 8-3-0 | Boston matched; **Vegas corrected**, pick downgraded High → Medium |
| `nba.com/games?date=2026-10-21` | 11 games, IDs `0022600085`–`0022600093`, tip times | 11 rows confirmed; synthetic Clippers ID now carries the real game ID |
| `statsapi.mlb.com/api/v1/schedule…` | 6 World Series games with first-pitch UTC and venues | 4 rows confirmed; **Game 5 (849799) added** (unpriced) |
| `statsapi.mlb.com/api/v1/standings` | Rays 98-64, home 55-26, away 43-38; Brewers home 55-26, away 48-33 | Split inputs confirmed — the two clubs genuinely share a 55-26 home record |
| `wst.tv` live/upcoming block | 11 Northern Ireland Open Round 2 ties with Match Centre IDs | 11 rows confirmed; **3 wrong links fixed, 2 missing links added** |
| `eurohandball.com` EHF CL playing-times PDF | Round 5: 12 fixtures, halls, 18:45/20:45 CEST | 12 rows confirmed incl. UTC conversion |
| `nrl.com/draw?competition=…round=2` | 5 men's RLWC26 Round 2 fixtures with venues | 5 rows confirmed |
| `euroleaguebasketball.net` Game Center | Round 7 fixtures and arenas | 3 rows confirmed; **coverage gap found** (22 Oct has 6 games) |
| `scoring.nzc.nz/fixtures` | T20I series, NZ A four-day, Ford Trophy Round 1 | **3 dates corrected, 1 fixture added**, all cricket times withheld |
| `afl.com.au/aflw` | Round 11 match-ups/venues, times only in visitor timezone | match-ups confirmed; **all 9 kick-off times withheld** |
| `pdc.tv` draw article + `/calendar/` | Cookie-consent interstitial only | **16 darts rows blocked**, nothing re-asserted |

## 2. Corrections applied

1. **Vegas Golden Knights** record `8-2-0 (.800, W3)` → `8-3-0 (.727, L1)`; the model re-priced the
   game at 59.9% and the pick fell from High to Medium. The High prediction was withdrawn rather
   than kept to protect a count.
2. **Snooker Match Centre links** — Holt–Brown, Gao–Gilbert and Noppon–Donaldson pointed at the
   wrong ties; Brecel–O'Donnell and Slessor–Jones had none. All eleven now match the official list.
3. **Cricket dates** — NZ A v India A moved to 23 Oct; all three Ford Trophy openers moved to
   27 Oct; the 3rd T20I (Wellington, 27 Oct) was missing and has been added.
4. **Cricket start times** — the NZC page prints times in the visitor's timezone only, so every
   cricket kick-off is now blank rather than a stored conversion.
5. **AFLW** — nine kick-off times withheld (see §3); the round and six match-ups are retained.
6. **MLB** — World Series Game 5 added, deliberately unpriced because no verified
   reverse-direction split exists for it.
7. **NBA** — the Clippers row carries `provider_game_id 0022600093`.
8. **Tennis** — the corrupted Osaka venue string (`ITC靱 …`) is blanked, not guessed.
9. **Afghanistan v Bangladesh ODI** — no official fixture page exists; the row is now `unverified`
   with no date, venue or time.

## 3. What could not be verified today

| Item | Why | Handling |
|---|---|---|
| 16 darts rows | `pdc.tv` returns a cookie-consent shell instead of article bodies | kept, marked **blocked**, listed on Flagged for Review |
| 9 AFLW kick-off times | AFL renders times in the visitor's timezone and the fixture page is script-rendered; displayed slots do not reconcile with the stored UTC | times withheld, 6 match-ups confirmed, 3 rows marked not re-checked |
| 11 tennis rows | ATP/WTA draw and ranking pages not re-fetched in this pass | marked **not re-checked** |
| 12 rugby union, 8 volleyball, 4 Gaelic, 4 golf, 3 greyhounds, 1 eSports, 1 F1, 2 EuroCup, 2 RLWC26 women | outside the fetch budget of this pass | marked **not re-checked**, prior-session provenance retained |
| EuroLeague 22 Oct remainder | snapshot prices 3 of the 6 games listed | published as a coverage gap, not filled with invented lines |

## 4. Reproduce

```bash
python3 scripts/build_dataset.py     # seed snapshot (overwrites fixtures.json)
python3 scripts/verify_pass.py       # apply the 2026-10-21 verification ledger + corrections
python3 scripts/origin_lines.py      # re-price, rebuild predictions and datasets/
python3 scripts/build_flagged.py     # regenerate the Flagged for Review register
python3 scripts/build_site.py        # render 28 pages at / and 28 at /f7fa77fc/
python3 scripts/validate.py          # must print VALIDATION PASSED
```

`verify_pass.py` must run after `build_dataset.py`; `validate.py` fails if any row is missing its
verification ledger block, so a rebuild that skips the verification step cannot pass the gate.
