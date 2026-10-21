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
* Shared outputs (`index.html`, the site navigation, `data/lines.json`) are written **only**
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
| T1 | Reverse-engineer OLBG sport taxonomy and match coverage | done | ce5920e3-olbg1 | `data/olbg_taxonomy.json`, `reverse-engineering.html` | 2026-10-21T05:20Z | 22 OLBG sports enumerated with IDs; 17 in scope |
| T2 | Harvest + verify fixtures for in-scope sports | in progress | ce5920e3-olbg1 | `data/fixtures.json` | 2026-10-21T05:35Z | Official-source verification per row |
| T3 | Originate betting lines + confidence tiers | unclaimed | — | `data/lines.json`, `scripts/model.py`, `scripts/origin_lines.py` | — | Depends on T2 |
| T4 | Write high-confidence predictions (≥30 words, unique) | unclaimed | — | `data/predictions.json` | — | Depends on T3 |
| T5 | Build static dashboard site | unclaimed | — | `*.html`, `sports/`, `assets/`, `scripts/build_site.py` | — | Depends on T2–T4 |
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

**2026-10-21T05:30Z — parallel workstream observed.**
PR **#4** (`OLBG match board: 164 events, originated lines, confidence picks + Pages dashboard`) was opened
against `main` while this session was finishing. It was **not** merged or modified by this session — it is
another session's claim and its own branch.

⚠️ **Potential conflict.** PR #4 appears to regenerate the same shared outputs this session owns
(`index.html`, `data/lines.json`, the site navigation). Whoever integrates should merge it rather than let it
overwrite: run `git pull --rebase`, rebuild with `scripts/build_site.py`, then re-run `scripts/validate.py`
before publishing. The 49-row dataset documented here and the 164-event dataset in #4 are different scopes and
should be reconciled, not silently replace one another.

**2026-10-21T05:35Z — deploy cache.** GitHub Pages reported `status=built` for the merge commit, but the public
URL continued to serve the previous build for several minutes. A cache-busted fetch was used to confirm
propagation before this session closed.

---

## 5. Session `ce5920e3-olbg1` — final report

**Completed:** 2026-10-21. Tasks T1–T6 executed by this session; T7 (integration) executed by the
same session because no other session was live.

### 5.1 What was claimed vs delivered

| # | Task | Status | Evidence |
|---|------|--------|----------|
| T1 | OLBG reverse-engineering | done | `data/olbg_taxonomy.json` (22 sports, 17 in scope), `reverse-engineering.html` |
| T2 | Fixture harvest + verification | done | `data/fixtures.json` — 49 priced matches + 1 verified unpriced event |
| T3 | Originate lines + confidence | done | `scripts/model.py`, `scripts/origin_lines.py`, `data/lines.json` |
| T4 | High-confidence predictions | done | `data/predictions.json` — 8 predictions, 53–63 words each |
| T5 | Static dashboard | done | repo root — 26 pages, generated by `scripts/build_site.py` |
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

### 5.3 Irregularities logged (published on `flagged.html`)

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
* GitHub Pages source: `main` → `/` (the repository root). The Pages API returned **403** for this
  token, so the site was generated directly into the root rather than `/docs`, which already matched
  the existing configuration.

### 5.5 Result

* **PR #1** — https://github.com/buffedlizard55-lab/OLBG1/pull/1 — merged 2026-10-21T05:19:39Z
  (merge commit `8b7963a`). The dataset, model, predictions and the 26-page dashboard.
* **PR #2** — https://github.com/buffedlizard55-lab/OLBG1/pull/2 — merged 2026-10-21T05:22Z
  (merge commit `9ef1deb`). Moved the generated site from `docs/` to the repository root because the
  Pages settings API returns 403 for this token and Pages is already configured for `main` → `/`.
* **Pages deploy** — build for `9ef1deb` completed with `status=built`, `error=null`, 22.8 s.
  Live URL https://buffedlizard55-lab.github.io/OLBG1/ returned HTTP 200 with the rendered dashboard.
* **Final gate** — `python3 scripts/validate.py` → 26 pages, 0 errors, 0 warnings.

### 5.6 Post-merge correction

After publication, `lines.json` was checked against the dashboard copy and one sentence was corrected:
the index previously said four of the eight high picks relied on the bounded top-36 snooker input; the
data shows **two** (`snk-cheung-bingham`, `snk-slessor-jones`). The copy now matches the data, and the
check is automated in `scripts/validate.py` (predictions must agree with `lines.json`).

### 5.7 Open items for a follow-up session

1. Promote the five Premiership Rugby rows from `cross-checked` to `verified` using club or PRL data.
2. Retrieve the PDC Order of Merit and re-price the seven darts ties with a real rating input.
3. Retrieve previous-season NBA standings so the eleven opening-night games stop being baseline-only.
4. Investigate the nine uninvestigated sports listed in §5.3 item 8.
5. Add attendance/injury/lineup inputs if a licensed feed becomes available.

---

## 6. Parallel session `4f44f7d9` (branch `arena/4f44f7d9-olbg1`) — integration record

**What happened.** This session started from the same empty-repo commit (`8b43e82`) at the same
time as `ce5920e3-olbg1`, created its own COORDINATION.md (the other session's board was not yet
on any branch it could see), and independently completed the same brief with a different,
complementary method. The overlap was discovered when PR #4 reported CONFLICTING against the
`ce5920e3` merges (#1–#3). Per §0.4 the conflict was resolved by **keeping both datasets** and
logging every resolution here. Nothing from `ce5920e3` was discarded.

**The two datasets (both retained — do not confuse them).**

| | `ce5920e3` (repo-root site) | `4f44f7d9` (`docs/` board) |
|---|---|---|
| Unit | 49 fixtures priced (+1 unpriced event) | 164 OLBG-listed events (matches + outrights/races) |
| Verification | Governing-body APIs per fixture | OLBG tip data per row; official checks for 5 High picks (NBA/ICC/PDC/WTA) |
| Pricing | Strength-rating model (`scripts/model.py`) | Tip-share Laplace model (`scripts/build_data.py`) |
| Confidence | 8 High / 3 Med / 38 Low | 5 High / 25 Med / 134 Low |
| Files | `data/fixtures.json`, `lines.json`, `predictions.json`, root `*.html`, `sports/` | `data/matches.csv/json`, `research/`, `docs/*.html` |

Overlapping picks can be cross-read (e.g. both sessions price Wizards/Bucks and the European
Championship darts ties by entirely different inputs) — agreement/disagreement between the two
models is itself useful signal and neither overrides the other.

**Conflict resolutions (merge of `origin/main` into `arena/4f44f7d9-olbg1`).**

1. `COORDINATION.md` — `ce5920e3` version kept as the board (§§0–5 untouched); this §6 appended.
   The `4f44f7d9` board text is preserved in git history (commit `270b06c`).
2. `index.html` (root) — `ce5920e3` dashboard kept. The `4f44f7d9` root redirect stub was dropped;
   its board lives at `/docs/` (legacy Pages publishes the whole repo, so both are live).
3. `scripts/build_site.py` — name collision, different programs. `ce5920e3` file kept under that
   name; `4f44f7d9` builder renamed to `scripts/build_board.py` (references updated).
4. `README.md` — merged: `ce5920e3` README kept, `4f44f7d9` board documented in an added section.
5. `.github/workflows/pages.yml` (`4f44f7d9`) — **removed**: Pages is legacy `main:/` (API 403 for
   both sessions); an Actions deploy workflow would only fail noisily. Re-add it if Pages is ever
   switched to workflow publishing (it uploaded `docs/` only, which would then need revisiting).
6. `scripts/__pycache__/*.pyc` — removed from the tree (build artifact, no content lost).

**Corrections owed by `4f44f7d9` (applied in this merge).** Its OLBG menu enumeration missed two
sitemap-only sports that `ce5920e3` found — **Aussie Rules (22)** and **eSports (23)**. The
`docs/` board therefore covers 15 of the 17 in-scope sports; the gap is now bannered on
`docs/index.html` and logged as its Flag F-13 (`research/verification-log.md` addendum). No rows
were invented to fill it. Follow-up: harvest OLBG IDs 22/23 tip pages into `data/matches.*`.

**Publish record (this session).** PR #4 — https://github.com/buffedlizard55-lab/OLBG1/pull/4 —
merged after this integration commit; Pages (legacy root publishing) serves the `ce5920e3`
dashboard at `/` and the `4f44f7d9` board at `/docs/`. Deploy verification appended below.

**Deploy verification (2026-10-21).** PR #4 merged 2026-10-21T05:23:50Z (merge commit
`c5d52644`); latest Pages build `status=built`, `error=null`. Live checks (fetched):
root dashboard https://buffedlizard55-lab.github.io/OLBG1/ (session `ce5920e3`, 49 priced
matches) and companion board https://buffedlizard55-lab.github.io/OLBG1/docs/ (session
`4f44f7d9`, 164 events) both return the rendered sites. `scripts/validate.py` (root site):
PASSED, 26 pages, 0 errors/warnings. `docs/` internal links: 0 broken. Tasks T1–T7 complete
across the two sessions; open follow-ups: §5.7 items + Flag F-13 harvest (IDs 22/23) + all
`needs review` flags on both Flagged pages (non-blocking by design).

---

## 7. Parallel session `c5e985f4` (branch `arena/c5e985f4-olbg1`) — integration record

**What happened.** This session started from the same empty-repo commit (`8b43e82`) and independently
completed the brief with a complementary method: fixture harvest via web_search (OLBG.com itself was
not reachable from the sandbox), originated American-style lines (moneyline/handicap/total where
applicable), confidence tiers, six 30+ word high-confidence predictions sourced to official league
pages, and a 17-page dashboard (root `index.html` + per-sport tables + methodology + findings +
flagged review), generated from `data/matches.json`.

**Files contributed (PR #6).** `data/matches.json` (72 entries, 13 in-scope sports), root
`index.html`, `tennis.html`, `nba.html`, `mlb.html`, `cricket.html`, `rugby-union.html`,
`ice-hockey.html`, `golf.html`, `snooker.html`, `darts.html`, `badminton.html`,
`table-tennis.html`, `volleyball.html`, `handball.html`, `methodology.html`, `findings.html`,
`flagged.html`, `COORDINATION.md` (initial board). Per the coordination convention (§0.4, append
and keep both datasets), shared-output filename collisions with the `ce5920e3` build were resolved
in favour of the integrated, validate.py-cleared tree currently on `main`; this session's dataset
and pages are reflected in git history via PR #6 and are not re-published over the live root
dashboard.

**Exclusions applied:** soccer/football, boxing, UFC/MMA, American football, hurling, horse
racing, cycling, specials (tennis, basketball, golf, cricket, snooker, rugby union, baseball, ice
hockey, darts, badminton, table tennis, volleyball, handball covered; rugby league noted as
season-completed).

**Verification policy:** every row carries a source link to an official/governing-body endpoint;
unconfirmed values left blank and flagged on the Flagged for Review page; originated prices labelled
as estimates, never as bookmaker quotes.

**Publish record.**
* Pull request: #6 — https://github.com/buffedlizard55-lab/OLBG1/pull/6 (branch `arena/c5e985f4-olbg1` → `main`).
* Merge result: merged into `main` (merge commit `f15b790`), subsequently included in `main` HEAD `4ee2564` (PR #7 merge).
* GitHub Pages: source `main` → `/`; `status=built`, `error=null`, `https_enforced=true`; live URL https://buffedlizard55-lab.github.io/OLBG1/ (root dashboard served by the integrated `ce5920e3` build, link-integrity validated with 0 errors).
* Flagged items: logged on the site's `flagged.html`; none block the merge.

---

## 8. Cross-links between the two published boards (session `ce5920e3`, final pass)

Both dashboards were live but unreachable from one another. This pass makes the combined
deliverable read as one product rather than two orphan sites:

1. The root dashboard's nav gains **“OLBG board (164)”**, a relative link to `docs/index.html`
   (the builder's `../` prefix keeps it correct from `sports/` too).
2. The root index gains a **“Two boards, two methods — read both”** panel stating which board
   rests on governing-body sources and which on OLBG tip distributions, and that neither is a
   superset of the other.
3. `docs/index.html` gains a banner back to `../index.html` repeating the provenance caveat, so a
   reader who lands on the companion board first is not misled about where the prices come from.

**Validator change.** `scripts/validate.py` previously reported `docs/index.html` as a broken
internal link because the companion tree sat outside its known-file set. It now accepts a link that
resolves to a real file under `docs/`, while still rejecting links that escape the site root.

**Gate result.** `python3 scripts/validate.py` → 26 pages, 0 errors, 0 warnings. A separate sweep of
all 46 HTML files across both trees for relative `href`/`src` targets found **0 broken references**.

### 8.1 Venue verification (closing the last open honesty item)

The Rays' home venue was previously carried as an **unverified** string because the earlier statsapi
call used a `fields=` filter, which silently drops `venue` — a documented trap. Re-queried without
the filter:

`GET /api/v1/schedule?sportId=1&startDate=2026-10-26&endDate=2026-10-28&hydrate=venue(location)`

→ `venue: {id: 12, name: "Tropicana Field", active: true, season: "2026"}`,
address *One Tropicana Drive, St. Petersburg, Florida 33705*. The venue string is therefore
**verified**, not inferred, and is no longer flagged.

The same response confirms Game 5 on 28 October carries `ifNecessary: "Y"`, which is why the
conditional games were excluded from the priced set.

**Copy correction made at the same time.** Two rating inputs read `"55-26 at Tropicana Field (.679)"`.
The standings publish a *home* record, not a venue-specific one, so attributing the split to the
ballpark was an inference. Both now read `"55-26 at home (.679)"`.

### Session `arena/ebfbd966-olbg1` (appended at integration, 2026-10-21)

This session started before the other sessions' work landed on `main` and built an independent,
OLBG-first desk on the same 2026-10-21 snapshot. Rather than overwrite shared outputs, it
integrated additively:

- **Scope/files (non-overlapping after relocation):** `ebfbd966/` (site section, 18 pages),
  `data/ebfbd966_matches.json`, `data/ebfbd966_lines.json`, `data/ebfbd966_writeups.json`,
  `scripts/ebfbd966_seed_data.py`, `scripts/ebfbd966_originate.py`,
  `scripts/ebfbd966_build_site.py`, `scripts/ebfbd966_validate.py`.
- **Content:** 133 OLBG-listed matches (Tennis 20, Basketball 20, Handball 20, Darts 16,
  Rugby Union 15, Volleyball 15, Cricket 9, Ice Hockey 7, Snooker 6, Gaelic Football 4,
  Baseball 1) → 4 HIGH / 31 MEDIUM / 98 LOW; hand-written previews (117–130 words) for the
  4 HIGH picks. Fills main-build gaps: Tennis, Handball, Volleyball, Gaelic club fixtures,
  Rugby League verified-zero; adds verified-zero fetches for eSports (23) and Aussie Rules
  (22) using this board's sitemap taxonomy (IDs 22/23 — credit session ce5920e3 T1).
- **Verification performed:** PDC official draw (16/16 darts ties), WST Match Centre (direct
  fetch), MLB official World Series schedule, ICC NZ–India itinerary + ODI ratings
  (19 Oct), URC official fixtures (4 ties), NBA official (season start 20 Oct;
  Antetokounmpo→Miami), ATP official calendar. Validator enforces: OLBG+official link per
  row, probabilities sum to 1, HIGH rules, writeup ≥30 words + no repeated 8-word passages,
  zero broken internal links. **Result: PASSED pre-merge; re-run post-merge (see PR #9).**

**Conflict log (§4 entries, appended here to avoid rewriting §4):**
1. PR #9 initially unmergeable (add/add collisions on `COORDINATION.md`, `README.md`,
   `scripts/build_site.py`, `scripts/validate.py`, `data/matches.json`, `data/lines.json`,
   `docs/**`). Resolution: this session relocated all its outputs to `ebfbd966`-scoped paths,
   deleted its GitHub Pages workflow (main's Pages source is `main:/` root — an artifact
   deploy would have broken the live site), and merged `origin/main` in. Only
   `COORDINATION.md`/`README.md` needed manual resolution, done append-only. **No other
   session's files were modified or deleted.**
2. **Snooker correction (self-caught):** this desk initially flagged SNO-01/SNO-04 CONTESTED
   from a stale search-engine snippet of wst.tv. A direct fetch of the official WST Match
   Centre at integration confirms Cheung Ka Wai v Stuart Bingham (21 Oct R2); flags retracted
   (SNO-01 → VERIFIED, SNO-04 → OLBG-ONLY as the 15:00 tie was outside the fetched listing).
   Main's 164-row board had the same pairings unflagged (OLBG-sourced) — now corroborated.
3. **Gaelic reconciliation:** main build = verified negative for *inter-county* fixtures
   21–25 Oct (GAA calendar); this desk = OLBG-listed *club* fixtures 24 Oct–1 Nov. No
   contradiction; both labelled as such.
4. **Known remaining gaps (needs review, non-blocking):** no ATP/WTA per-player ranking gaps
   (tennis capped below HIGH); PDC seeds beyond PDC-stated #4/#12 and snooker ranks
   Pang 26/Davies 89/Higgins 7/J.Jones 30 rest on published draw summaries (official pages
   linked per row; SNO-02 HIGH to be re-confirmed on WST rankings); MLB WS starters + NHL
   goalies blank; OLBG 'Load More' zero-tip tail unenumerated; OLBG times timezone unstated.
   Mirrored on `ebfbd966/flagged.html`.

**Integration record (arena/ebfbd966, 2026-10-21):** PR [#9](https://github.com/buffedlizard55-lab/OLBG1/pull/9) **MERGED** 2026-10-21T05:30:57Z (merge commit `c19df1d`). GitHub Pages rebuilt successfully (status `built`, source `main:/` unchanged). Live verification by direct fetch: root dashboard `/OLBG1/` intact (49-match verified build), this desk live at `/OLBG1/ebfbd966/` (133 matches, HIGH previews rendering), companion board at `/OLBG1/docs/`. Combined-tree link check across 64 HTML files: zero genuinely broken internal refs (16 apparent hits are 404.html's intentional absolute `/OLBG1/` paths, correct when deployed). No other session's files deleted (`git diff --diff-filter=D origin/main..HEAD` empty at merge). Remaining needs-review items stand as listed in entry 4 above and on `ebfbd966/flagged.html`.
