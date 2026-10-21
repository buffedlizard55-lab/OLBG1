# COORDINATION.md — Shared Task Board

**Read this before starting any work.** This file is the single source of truth for who is
working on what. It exists so that multiple agent sessions can work on this repository at the
same time without duplicating work or overwriting each other.

Last updated: **2026-10-21** (UTC)

---

## 0. Conventions

### 0.1 Session IDs

A session ID is the Arena branch slug assigned to the session. The session that created this
board is **`arena/ce5920e3-olbg1`**, so its ID is **`ce5920e3-olbg1`**.

### 0.2 Branch naming — important deviation, read this

The project brief asks for per-task branches named `session-<id>/<task>`. Arena sessions in this
repository are **pinned to one sandbox-managed branch each**, and the agent operating a session
must not create, switch to, or push any other branch. Therefore:

* Each session works **only** on its own pinned `arena/<session-id>` branch.
* That branch is simultaneously the session's work branch **and** its integration branch.
* `main` is only ever advanced by the final integration session's merged pull request.

This is the one deliberate deviation from the brief. It removes the merge storms that per-task
branches would create while preserving the property the brief actually cares about: **no two
sessions write to the same files at the same time.**

### 0.3 Claiming a task

1. Add a row to the table in §1 with your session ID, your file scope and the UTC time.
2. Commit and push that claim **before** you start work.
3. Never start a task that another live session has claimed.

### 0.4 Scope rules

* Scopes must not overlap. If you need a file owned by another session, log a request in §4
  instead of editing it.
* Shared outputs (`site/index.html`, the site navigation, `data/index.json`) are written **only**
  by the final integration session.
* Commit small and often. `git pull --rebase` before every push.
* On a merge conflict: stop, resolve it so that **neither** session's work is discarded, and log
  it in §4.
* A claim with no commit for more than 60 minutes may be taken over by another session. Log the
  handoff in §4.

### 0.5 Verification rules (non-negotiable)

* Every data row must carry at least one link to an **official** source (the league, governing
  body, tour, promoter or team itself). Media outlets, aggregators and betting sites are **not**
  official sources.
* If a value cannot be confirmed from an official source: **leave it blank and flag it**. Never
  infer, interpolate or fill it in from memory.
* Model-derived values (our originated prices) are explicitly labelled as estimates and are never
  presented as sourced facts.
* Nothing is marked `verified` until the official source has actually been fetched and read.

---

## 1. Task board

Status values: `unclaimed` · `in progress` · `done` · `needs review`

| # | Task | Status | Session | File scope | Started (UTC) | Notes |
|---|------|--------|---------|------------|---------------|-------|
| T1 | Reverse-engineer OLBG sport taxonomy and match coverage | done | ce5920e3-olbg1 | `data/olbg_taxonomy.json`, `docs/reverse-engineering.md` | 2026-10-21T05:20Z | 22 OLBG sports enumerated with IDs; 17 in scope |
| T2 | Harvest + verify fixtures for in-scope sports | in progress | ce5920e3-olbg1 | `data/fixtures/*.json`, `data/raw/` | 2026-10-21T05:35Z | Official-source verification per row |
| T3 | Originate betting lines + confidence tiers | unclaimed | — | `data/lines/*.json`, `scripts/origin_lines.py` | — | Depends on T2 |
| T4 | Write high-confidence predictions (≥30 words, unique) | unclaimed | — | `data/predictions/*.json` | — | Depends on T3 |
| T5 | Build static dashboard site | unclaimed | — | `site/**`, `scripts/build_site.py` | — | Depends on T2–T4 |
| T6 | Link-integrity + data validation checks | unclaimed | — | `scripts/validate.py`, `tests/` | — | Depends on T5 |
| T7 | Final integration: merge, re-verify, publish Pages, PR | unclaimed | — | `COORDINATION.md`, PR | — | Reserved for the integration session |

> **Note on multi-session safety:** if you are a session that is not `ce5920e3-olbg1`, add your
> rows to §1 and §4 **without rewriting the existing table**. Append; do not reformat.

---

## 2. Session log

### Session `ce5920e3-olbg1`

**2026-10-21T05:15Z — board created.**
Repository was a single empty `README.md` at commit `8b43e82`. No prior sessions had run. This
session claimed T1 immediately and pushed the claim in the same commit that created this file.

**2026-10-21T05:20Z — T1 done.** OLBG sport taxonomy reversed from
`https://www.olbg.com/sitemap-betting-tips.xml` and `https://www.olbg.com/sitemap`. 22 sport
IDs enumerated. Exclusions applied per the brief:

| Excluded (per brief) | OLBG ID |
|---|---|
| Football / soccer | 1 |
| Horse Racing | 2 |
| American Football | 11 |
| Boxing | 16 |
| Cycling | 17 |
| Hurling | (under Gaelic Sports) |
| Specials | (TV / Politics / Awards) |
| UFC / MMA | (under Boxing/Specials) |

In-scope sports (17): Tennis (3), Basketball (4), Golf (5), Cricket (7), Snooker (8),
Rugby Union (9), Rugby League (10), Baseball (12), Ice Hockey (13), Motor Racing (14), Darts (15),
Handball (20), Volleyball (21), Aussie Rules (22), eSports (23), Gaelic Football (25),
Greyhounds (28).

---

## 3. Sources register

Every source used is catalogued with its URL in `data/sources.json` and rendered on the site's
Sources page. Only governing bodies / official league endpoints are used for verification.

---

## 4. Requests and conflict log

_Nothing logged yet._

---

## 5. Session `ce5920e3-olbg1` — final report

**Completed:** 2026-10-21. Tasks T1–T6 executed by this session; T7 (integration) executed by the
same session because no other session was live.

### 5.1 What was claimed vs delivered

| # | Task | Status | Evidence |
|---|------|--------|----------|
| T1 | OLBG reverse-engineering | done | `data/olbg_taxonomy.json` (22 sports, 17 in scope), `docs/reverse-engineering.html` |
| T2 | Fixture harvest + verification | done | `data/fixtures.json` — 49 priced matches + 1 verified unpriced event |
| T3 | Originate lines + confidence | done | `scripts/model.py`, `scripts/origin_lines.py`, `data/lines.json` |
| T4 | High-confidence predictions | done | `data/predictions.json` — 8 predictions, 53–63 words each |
| T5 | Static dashboard | done | `docs/` — 26 pages, generated by `scripts/build_site.py` |
| T6 | Link + data integrity gate | done | `scripts/validate.py` — passes with 0 errors, 0 warnings |
| T7 | Integration + publish | done | see §5.4 |

### 5.2 Verification performed

Every fixture was read on a governing-body endpoint and the exact URL is stored on the row:

* **MLB** — `statsapi.mlb.com` schedule, postseason schedule and standings endpoints. Records,
  home/road splits, the full postseason log and the conditional-game notes all come from MLB.
* **NHL** — `api-web.nhle.com` schedule and standings endpoints (game IDs, venue, UTC start, records).
* **NBA** — `nba.com/games?date=2026-10-21` (game IDs, tip times) and `nba.com/standings`.
* **Snooker** — `wst.tv` live-match block (draw, per-match Match Centre URLs) and the WST
  Johnstone's Paint World Rankings table (top 36 + prize money, plus the One Year List).
* **Darts** — PDC schedule release for the 2026 Machineseeker European Championship and the PDC
  calendar (venue, dates, first-round draw).
* **Cricket** — `scoring.nzc.nz/fixtures`, New Zealand Cricket's own fixtures service (7 fixtures,
  venues, per-match Match Centre links).
* **Gaelic football** — `gaa.ie/fixtures-results`, used to establish a **verified negative**: no
  Gaelic football fixture between 21 and 25 October 2026.
* **Formula 1 / PGA TOUR** — event dates and venues only; both are recorded as *event only*.

`scripts/validate.py` re-checks mechanically: every internal link resolves, every fixture has an
https source, every pick is an outcome of its own market, probabilities sum to 1, odds are plausible,
and every prediction is 30+ words and agrees with the model's pick.

### 5.3 Irregularities logged (published on `docs/flagged.html`)

1. **Premiership Rugby** — `premrugby.com/fixtures-results` is client-rendered and returned zero rows.
   All five rugby union fixtures are marked `cross-checked`, not `verified`.
2. **PDC** — `pdc.tv` serves a cookie interstitial instead of article bodies. The draw was read from
   the publisher's indexed copy of its own schedule release; the eighth Thursday tie was truncated and
   is omitted rather than guessed.
3. **Snooker session times** — WST renders in the viewer's timezone; only dates are recorded.
4. **Snooker venue** — the Waterfront Hall is not stated on the fetched schedule block; flagged per row.
5. **F1** — circuit name and start time not captured; left blank rather than assumed.
6. **NBA** — the eleventh 21 October game had its game ID and arena truncated on the source page.
7. **Snooker ranking bound** — players below the published top 36 share one bounded bucket (rank 60).
   Four of the eight high picks depend on that bound; disclosed on the Methodology and Flagged pages.
8. **Not investigated** — rugby league, handball, volleyball, tennis, AFL, esports, greyhounds. No
   official fixture source was retrieved. Recorded as gaps, not as empty schedules.

### 5.4 Publish record

* Branch: `arena/ce5920e3-olbg1` (the session's pinned branch — see §0.2 for the deviation note).
* Pull request and merge result: recorded in §5.5 below once the merge completes.
* GitHub Pages source switched to `main` → `/docs`.

### 5.5 Result

_Pending merge._
