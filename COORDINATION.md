# COORDINATION — OLBG1 shared task board

> Multiple agent sessions may work on this repo. Read this file before starting.
> Claim a task (session ID + file scope), commit + push the claim immediately,
> never start a claimed task, keep scopes non-overlapping, small frequent commits,
> `git pull --rebase` before every push. Log cross-session file-change requests
> here instead of editing another session's files.
> `needs review` = published on the Flagged for Review page; does not block merge.
> Shared outputs (table data, site index/navigation) change only in a final
> integration pass. Never mark anything verified without an official source link.

**Branch note (Arena constraint):** This session must stay on `arena/4f44f7d9-olbg1`
(Arena tracks the session by branch and forbids switching/creating other branches).
The `session-<id>/<task>` branch pattern in the original brief therefore cannot be
followed literally here; scope separation is by file claims below instead. Other
sessions on their own Arena branches should follow the same file-claim discipline.

## Session registry

| Session ID | Branch | Status |
|---|---|---|
| `4f44f7d9` (this session) | `arena/4f44f7d9-olbg1` | active |

## Task board

| # | Task | Status | Owner | File scope |
|---|---|---|---|---|
| T1 | Reverse-engineer OLBG.com structure (sports, URL patterns, markets) | done | 4f44f7d9 | `research/olbg-structure.md` |
| T2 | Collect full match list for covered sports (excl. soccer/football, boxing/UFC/MMA, American football, hurling, horse racing, cycling, specials) from OLBG sport pages, snapshot 2026-10-21 | in progress | 4f44f7d9 | `data/matches.csv`, `data/matches.json`, `data/README.md` |
| T3 | Originate own lines + winner pick + confidence (low/medium/high) per match; document market availability per sport | in progress | 4f44f7d9 | `data/matches.csv`, `data/matches.json`, `research/methodology.md`, `research/markets.md` |
| T4 | High-confidence write-ups (≥30 words, verified facts only, official sources) | in progress | 4f44f7d9 | `docs/high-confidence.html`, `research/verification-log.md` |
| T5 | GitHub Pages dashboard site (landing + per-sport subpages + markets + methodology + flagged) | in progress | 4f44f7d9 | `docs/**` |
| T6 | Line-by-line verification pass; every row has OLBG source link; unconfirmed values blank + flagged | in progress | 4f44f7d9 | `research/verification-log.md`, `docs/flagged.html` |
| T7 | Final integration: re-verify combined data, check build/links, enable Pages, PR to main + merge, confirm deploy | unclaimed → claimed by 4f44f7d9 as integrator (single-session run; no other session has claimed work) | 4f44f7d9 | all (integration only) |

## Log

- 2026-10-21 — Session `4f44f7d9` created this board (repo contained only `README.md`).
  Claimed T1–T7 (no prior claims existed). File scopes above are exclusive to this
  session until marked done. Handoff rule: a claim idle >60 min with no commits may
  be taken over; note the handoff here.
- 2026-10-21 — T1 done. OLBG structure documented in `research/olbg-structure.md`
  from live fetches of `https://www.olbg.com/betting-tips` and per-sport pages.

## Sources & verification record (filled on completion)

_To be completed in T6/T7: sources used, verification performed, irregularities,
PR link and merge result._

## Cross-session requests

_None._
