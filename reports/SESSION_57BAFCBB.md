# Desk 57bafcbb — session report

| Field | Value |
| --- | --- |
| Session | `57bafcbb-olbg1` |
| Claim | `T57BAFCBB` (`COORDINATION.md` §93) |
| Branch | `arena/57bafcbb-olbg1` |
| Base | `eb80e51` (main tip) |
| Window | 24–25 October 2026, opened 2026-10-24 22:35 UTC |
| Sports | 15, in brief order |
| Pages | 23 (`57bafcbb/`) |
| Fixtures tracked | 29 |
| Graded picks | 14 |
| High / Medium / Low | 5 / 7 / 2 |
| Written predictions | 14 (one per pick) |
| Flags | 9 |
| Sports priced | 9 of 15 |

## 1. What this desk does

It works the fresh 24–25 October 2026 overnight window for the 15-sport OLBG brief.
For every fixture it reads the official governing-body record or form line, writes its own
probability estimate, converts that estimate into an American price, and labels the pick
Low / Medium / High. No bookmaker odds are read anywhere in the pipeline.

Three market families are investigated per priced fixture: the win market, a handicap line,
and a totals line.

## 2. Line origination and the confidence band

The estimate is the desk's own figure, built from the official record and form line recorded
against each fixture. It is turned into a price with `p / (1 − p)`, and the other side of the
book is given the remainder so the book is strictly fair (margin exactly 0).

| Label | Rule |
| --- | --- |
| High | estimate ≥ 60% **and** fair price inside −250..+10000 |
| Medium | estimate ≥ 55% **and** fair price inside −250..+10000 |
| Low | estimate below 55%, or a price outside the band |

A price below −250 is downgraded to Medium even when the estimate is very high: the band is
the desk's discipline against backing extreme chalk, which is the failure mode the brief calls
out. This window produced 5 High picks, of which 1 clears the stricter 70% gate
(`rl-aus-fiji`, Australia at −245).

The 60% floor is the repository's canonical desk rule (`pipeline/desk.py`). It is published on
the desk's methodology page so the choice is visible rather than implicit.

## 3. The picks

| Sport | Fixture | Pick | Confidence | Estimate | Price |
| --- | --- | --- | --- | --- | --- |
| Baseball | `bs-ws-g2` World Series G2 | Milwaukee Brewers | Medium | 56.5% | −131 |
| Ice Hockey | `ih-fla-chi` FLA @ CHI | Florida Panthers | Medium | 57.5% | −135 |
| Ice Hockey | `ih-nyi-dal` NYI @ DAL | Dallas Stars | Medium | 57.0% | −133 |
| Tennis | `tn-almaty-final` ATP Almaty | Danil Medvedev | High | 62.0% | −163 |
| Tennis | `tn-lyon-final` ATP Lyon | Tommy Paul | High | 60.0% | −150 |
| Tennis | `tn-brussels-final` ATP Brussels | Jan-Lennard Struff | Medium | 57.5% | −135 |
| Darts | `dt-price-bunting` EC QF | Gerwyn Price | Medium | 56.0% | −127 |
| Darts | `dt-smith-woodhouse` EC QF | Ross Smith | Medium | 55.0% | −122 |
| Snooker | `sn-niopen-final` NI Open final | Kyren Wilson | High | 63.5% | −174 |
| Cricket | `cr-eng-pak` Eng v Pak ODI | Pakistan | Medium | 59.0% | −144 |
| Rugby League | `rl-aus-fiji` RLWC | Australia | High | 71.0% | −245 |
| Rugby League | `rl-nz-ci` RLWC | New Zealand | High | 66.0% | −194 |
| Motor Racing | `mr-f1-usgp-race` F1 US GP | Antonelli | Low | 30.0% | +233 |
| Golf | `golf-bermuda` Bermuda Champ | Austin Smotherman | Low | 30.0% | +233 |

The motor-racing and golf outrights are multi-runner markets. They cannot carry a High label
under the banding rule, because singleing out one runner always puts the fair price outside
−250..+10000 once the field is priced. Both are published as Low confidence outrights with the
field-level estimate stated.

## 4. Official sources read this session

| Sport | Official source | What it supplied |
| --- | --- | --- |
| Baseball | `statsapi.mlb.com` schedule + standings | World Series G2/G3 dates, venues, series state, 103-59 / 98-64 records |
| Ice Hockey | `api-web.nhle.com/v1/score/2026-10-25` | Sunday matchups, venues, 5-4-2 / 3-7-0 / 6-3-1 / 5-3-2 records |
| Tennis | `atptour.com` scores + news | Three Sunday finals, semi-final scores, rankings |
| Darts | `pdpa.co.uk` European Championship | Quarter-final draw, round-two scores, Sunday sessions |
| Snooker | `wst.tv` | NI Open final slot, semi-final score, defending champion |
| Cricket | `ecb.co.uk` itinerary | England v Pakistan 25 Oct, 08:00 GMT, Lahore, 3rd ODI |
| Rugby League | `nrl.com` World Cup draw | NZ v Cook Islands, Australia v Fiji, 25 Oct, points |
| Rugby Union | `unitedrugby.com` Round 4 preview | Full URC round with UK kickoffs (complete by read time) |
| Motor Racing | `formula1.com` US GP | Qualifying order, Antonelli 1:34.035, 56 laps / 5.513 km |
| Golf | `pgatour.com` Bermuda leaderboard | Final-round leaders, T1 −16 Smotherman / Gerard, T3 −14 |
| Gaelic Sports | `gaa.ie` | Shinty-Hurling International, Tyrone SFC final, Dublin SHC final |
| Handball | `eurohandball.com` | European Cup + WCh 2027 material only |
| Greyhounds | `gbgb.org.uk` | Meeting list and track directory |
| Basketball | `nba.com/games` | Game count for 24 Oct (8 games) only |
| Volleyball | `legavolley.it` | JavaScript shell — no fixture list rendered |

## 5. Irregularities, dead ends and flags

Everything below is published on the desk's `flagged.html` page rather than suppressed.

1. **Volleyball — no priced pick.** The Italian SuperLega site is a JavaScript shell and
   rendered no fixture list. Two fixtures are published as directory entries.
2. **Basketball — no priced pick.** `nba.com/games` returned a JavaScript shell with an
   error for both 24 and 25 October; only the game count was readable.
3. **Handball — no priced pick.** EHF carries European Cup and World Championship material
   only; the domestic league fixtures fall outside it.
4. **Gaelic Sports — no priced pick.** `gaa.ie/fixtures-results` renders a results list for
   the current weekend only.
5. **Greyhounds — no priced pick.** GBGB carries the latest meeting list and track
   directory, not the per-race card for 25 October.
6. **Rugby Union — no priced pick.** URC Round 4 was complete by read time; the Top 14 and
   Premiership fixture feeds did not render (`top14.lnr.fr` blocking, `premierrugby.com`
   blocked).
7. **Two darts quarter-finals held back.** The PDPA draw confirmed Littler v Clayton and
   Ratajski v Schindler, but only the two most prominent quarter-finals were read a second
   time from the official draw, so those two are directory entries rather than priced lines.
8. **OLBG hub times are US Eastern.** The hub prints "Today/Tomorrow + HH:MM" in EDT
   (UTC−4). Cross-checked against ECB (Lahore 08:00 GMT) and MLB
   (`2026-10-25T00:00:00Z`).
9. **`OLBG.com/tips/{Sport}/{id}` is dead** (returns "Page Error"). The working hub is
   `olbg.com/betting-tips/{Sport}/{sport_id}`.

Sports with the weakest official coverage are flagged `awaiting-review`; none of them blocks
the merge.

## 6. What was deliberately not done

- No bookmaker odds were read. Every price is arithmetic on the desk's own estimate.
- No statistic was filled in that could not be read. Blank cells stay blank.
- The OLBG hub was not treated as an official source. It finds fixtures; official pages
  confirm them. A fixture found only on the hub is never priced.
- Statistics that could not be read from an official page were removed from the prose rather
  than approximated. Every prediction is built from results, records, venues and series state
  that appear in the sources table above.

## 7. Verification

- `python3 scripts/s57bafcbb_validate.py` → OK
- `python3 -m unittest tests.pipeline.test_desk_57bafcbb` → 28 tests, OK
- `python3 scripts/validate.py` → VALIDATION PASSED, 0 errors (3 pre-existing warnings
  from another desk's flagged page)

## 8. Publish

| Step | Result |
| --- | --- |
| PR opened | [#288](https://github.com/buffedlizard55-lab/OLBG1/pull/288) from `arena/57bafcbb-olbg1` to `main` |
| Moving-main rebases | 2. Both required conflict resolution. `COORDINATION.md` resolved as a strictly additive union — all peer bytes retained, this session's section renumbered §93 → §96 and re-appended at the end. `index.html` and `pipeline/build.py` resolved by keeping main's list and re-appending this desk's one additive line. No peer entry was edited or removed. |
| Merged | Yes — `gh pr merge 288 --squash --delete-branch` exit 0; main at `763fdca` |
| Gates on merge | `scripts/s57bafcbb_validate.py` OK; 28 desk tests OK; `scripts/validate.py` VALIDATION PASSED, 0 errors across 2008 published HTML pages |
| Pages read-back | `https://buffedlizard55-lab.github.io/OLBG1/57bafcbb/index.html` serves the executive summary (29 fixtures / 14 picks / 5 High / 7 Medium / 2 Low / 9 sports priced / 6 unpriced), the High-picks table and the 15-sport navigation. `picks.html`, `sports/golf.html` and `flagged.html` also serve. Read from served bytes, not from API status. |
| Root pointer | `index.html` on the live site lists `57bafcbb/index.html` in the front-door desk directory. |

## 9. Disposition

Claim status: **done**. The desk is published, the PR is merged, and the served bytes
were read back. Six sports carry no priced pick and say so on their own pages and on the
flagged page rather than manufacturing coverage; the motor-racing and golf outrights are
published as Low confidence multi-runner estimates rather than being relabelled as
two-way matches.
