# OLBG1 Coordination Board

Last updated: 2026-10-21T05:50:00Z

## Task board

| ID | Task | Status | Owner/session | Claimed at (UTC) | File scope |
| --- | --- | --- | --- | --- | --- |
| T-001 | Repository audit, verified sports-data pipeline, dashboard implementation, final integration, deployment, and release | in progress | `a41abce4` | 2026-10-21T05:13:53Z | `COORDINATION.md`, `README.md`, `.github/**`, `package*.json`, `assets/**`, `data/**`, `scripts/**`, `sports/**`, `tests/**`, and root Pages files |

## Coordination log

- 2026-10-21T05:13:53Z — Session `a41abce4` found only `README.md` in the repository and no existing task board or claims. Created this board and claimed the end-to-end implementation/integration scope.
- 2026-10-21T05:13:53Z — Arena requires this session to remain on branch `arena/a41abce4-olbg1`; no separate branch/worktree was created.
- 2026-10-21T05:14:00Z–05:44:59Z — Inspected the complete repository, canonical OLBG category routes, governing-body schedules, competition pages, standings, draws and official reports. No overlapping session claim, cross-scope request or merge conflict was encountered.
- 2026-10-21T05:45:00Z — Froze the visible category capture. Re-fetched the volatile Rugby Union route line by line; its current 15-row slate begins Montauban–Oyonnax and ends La Rochelle–Bordeaux-Bègles, matching current LNR/URC records. This recapture supersedes earlier volatile discovery content rather than blending it.
- 2026-10-21T05:46:00Z — Added known official Rugby Union and Gaelic Football start times. Unknown time and venue fields remain blank.
- 2026-10-21T05:48:00Z — Implemented and locally checked the model, strict validation, responsive dashboard, 15 category pages, filters, match-audit dialogs, review queue, tests, sitemap and Pages workflow.

## Source and verification record

- **Discovery only:** current canonical OLBG pages for Basketball, Cricket, Darts, Gaelic Football, Handball, Ice Hockey, Rugby Union, Snooker, Tennis and Volleyball. No OLBG percentages, selections or displayed prices enter the model.
- **Official fixture/form evidence:** PDC, World Snooker Tour, MLB, NBA, EuroLeague/EuroCup, Basketball Champions League, KBL, ICEHL, NHL, SHL, LNR Top 14/Pro D2, United Rugby Championship, EHF, Handbollsligan, Danish and Norwegian handball federations/leagues, ATP, WTA, national and club volleyball leagues/federations, ICC, Cricket South Africa, Cricket Australia, and Cork/Galway/Waterford GAA.
- Every generated match row stores and displays one official-source URL. The corresponding discovery URL is retained separately and labeled “discovery only.”
- Frozen result: **135 rows across 11 match-bearing categories; 131 verified, one partially verified, three unverified; 16 flagged matches; 10 high-confidence selections.** Four additional included categories document outright-only or officially unreproducible feeds without inventing head-to-head rows.
- Validation rejects excluded sports, duplicate IDs, missing official links, invalid probability sums, non-low confidence on unverified rows, and high-confidence copy that is short, duplicated or insufficiently identified.

## Irregularity record

The complete row-level wording and official links are in `data/matches.json` and `flagged.html`. Frozen code counts are:

| Code | Count | Recorded treatment |
| --- | ---: | --- |
| `FIXTURE_NOT_CONFIRMED` | 3 | Timrå–Färjestad, Puijo–OrPo and Jelcz-Laskowice–Stal Nysa retain blank official schedule fields and low confidence. |
| `OFFICIAL_ORDER_CORRECTION` | 3 | Current Cork/Galway GAA official ordering is used; OLBG ordering is preserved in the audit note. |
| `OLBG_OMISSION` | 2 | Charlotte–Brooklyn and Sacramento–LA Clippers are added from the NBA schedule and clearly labeled official-schedule gaps. |
| `MIXED_DATE_WINDOW` | 1 | Oklahoma City–Denver is identified as an October 22 row mixed into the visible October 21 slate. |
| `NEUTRAL_VENUE` | 1 | Herzliya–Porto receives no normal home edge because official material places it in Samokov. |
| `TIME_CONFLICT` | 1 | Estonia Women–Kosovo Women keeps time blank. |
| `DATE_NOT_CONFIRMED` | 1 | Friso Sneek–VV Utrecht keeps date/time blank. |
| `TIP_FORM_CONTRADICTION` | 1 | Vallefoglia–Cuneo records the official form evidence that conflicts with the displayed OLBG tip. |
| `DISPLAY_ORDER_MISMATCH` | 1 | Sri Lanka–England uses ICC ordering. |
| `TEAM_NAME_NORMALIZED` | 1 | CSA’s “CSA High Performance” name replaces OLBG’s alias. |
| `DATE_CONFLICT` | 1 | Rathgormack–The Nire uses Waterford GAA’s October 25 at 14:30 value, not OLBG’s November 1 display. |

Coverage-level limitations are also public: retained “Load More Tips” controls prevent claims beyond visible rows; Golf, Motor Racing and Rugby League are outright-only in the frozen capture; no reproducible official future-card feed was found for Greyhounds.

## Integration and release record

- `b0c9633` — ownership claim committed and pushed.
- `dc7afe1` — verified match inputs, generated strict dataset, model and validator committed.
- `55f2b8d` — responsive dashboard, category pages, client rendering and tests committed.
- Local `npm run check`: passing (135 rows, 15 categories, 10 unique high-confidence analyses, ten Node subtests after the final fixture/time assertions).
- Pull request, merge SHA, Actions checks, Pages source transition, deployment run and live URL verification remain pending and will be appended before T-001 is closed.

## Completion record

T-001 remains in progress until the final pull request is merged and the GitHub Pages production URL is verified live.
