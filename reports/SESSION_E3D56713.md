# Session `e3d56713-olbg1` — T64 canonical-release health pass (22 Oct 2026)

Scope: re-run the canonical gates on `main` (`d9df68e`), compare the committed release with the deployed GitHub Pages site, spot-check one row against an official source, and log irregularities. No shared data, root page, confidence rule or price logic was changed. No High or Medium picks were issued (see "Why no High picks" below).

Checked at: 2026-10-22 ~12:00 UTC.

## 1. Gates run locally (branch `arena/e3d56713-olbg1`, base `d9df68e`)

| Gate | Command | Result |
|---|---|---|
| Pipeline unit tests | `python3 -m unittest discover -s tests/pipeline` | 95 tests, OK |
| Preserved upstream tests | `python3 -m unittest discover -s tests -p 'test*.py'` | OK |
| Committed root validation | `python3 -m pipeline.validate --site .` | 0 errors |
| Scratch build | `python3 -m pipeline.build --out /tmp/e3site` | 77 pages built |
| Built-site validation | `python3 -m pipeline.validate --site /tmp/e3site` | 0 errors |

Canonical counts in the committed snapshot (`data/current/snapshot.json`, generated 10:27:50Z): 108 captured listings, 42 accepted inputs in the README narrative, 24 priced matches, 49 originated two-way markets, 98 outcome prices, **0 High, 0 Medium, 22 Low**, 84 unpriced.

## 2. Irregularities found

| ID | Severity | Finding | Evidence |
|---|---|---|---|
| E3-01 | **High (deployment integrity)** | Pages is configured as **legacy** mode, branch `main`, path `/`. The canonical workflow *also* deploys an artifact. So each push to `main` produces two deploys: the legacy root build and the artifact. The root `index.html` is the committed 10:27:50Z snapshot, while the artifact is the CI build from 10:49:57Z. Whichever finishes last determines the live site. | [Pages config API](https://api.github.com/repos/buffedlizard55-lab/OLBG1/pages) (`build_type: legacy`, `source.path: /`); [canonical run 39766032226](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39766032226) (push, success); [legacy "pages build and deployment" run 39766030731](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39766030731) (completed 10:51:25Z). |
| E3-02 | **High (repo ≠ live)** | The live site currently shows the CI-refreshed snapshot: 147 captured listings, 61 priced, 86 unpriced, generated 10:51:11Z ([live snapshot](https://buffedlizard55-lab.github.io/OLBG1/data/current/snapshot.json)). The committed `data/current/snapshot.json` shows 108 / 24 / 84 (10:27:50Z). The committed counts in README and on the board therefore do not describe the deployed site. Refresh output is not committed, by design, but this is not disclosed on the public page. | Live [index](https://buffedlizard55-lab.github.io/OLBG1/) KPIs vs committed `data/current/snapshot.json`. |
| E3-03 | Medium (repo hygiene) | `python3 -m pipeline.build --out <anywhere>` **rewrites tracked files** `data/current/audit.json` and `data/current/snapshot.json` in the source tree with the current time and a new baseline hash, even when `--out` is a scratch directory. The validators and tests do not. Restored with `git checkout --` here; not committed. | `git status` after build; diff shows `generated_at` changed to build time. |
| E3-04 | Low (non-defect, presentation) | On the live index, rows read like "−15060.0% model chance". This is the price (`-150`) and the probability (`60.0%`) rendered as adjacent spans and joined by text extraction. The committed local build renders `-150` and `60.0% model chance` as separate spans. Not a calculation error. The visual separation depends on CSS and should be checked in a browser. | Local build `/tmp/e3site/index.html` vs live `index.html` text. |
| E3-05 | Medium (process) | The canonical workflow's "Check committed canonical root before regenerating anything" step passes on the committed tree. No tests reproduce E3-02, so the gap between committed and deployed is not checked by any gate. | `.github/workflows/current-pages.yml`. |
| E3-06 | Info (carried over) | Flagged items F-257E-01…16 on the live [Flagged page](https://buffedlizard55-lab.github.io/OLBG1/flagged.html) remain open as the owning session logged them. Not re-adjudicated here. | Live flagged page. |

## 3. Spot-check against an official source

| Live row | Official check | Result |
|---|---|---|
| 22 Oct 23:00 UTC — Boston Bruins vs Nashville Predators (NHL) | [NHL public schedule API, 2026-10-22](https://api-web.nhle.com/v1/schedule/2026-10-22) | Game `2026020154`, `startTimeUTC 2026-10-22T23:00:00Z`, `gameState FUT`, venue TD Garden, Nashville away / Boston home. **Matches.** |

Only this one row was re-read in this session. The other 147 live rows were not re-verified line by line; that remains open for a verification session.

## 4. Why no High picks were issued

The committed methodology (`README.md`, §Evidence and pricing contract) and the live release criteria both require out-of-sample calibration, a current bookmaker quote, and sourced form/player/history context before High. None of these exist in the repo for any of the 24 committed priced matches, so issuing High would contradict the published rule. The brief's "> 70% model probability" shortcut is also explicitly rejected in the canonical flags (F-257E-07). No High picks were created here.

## 5. Recommendations (for the integration owner)

1. **Resolve E3-01 before any further merge to `main`.** Either disable the legacy Pages source (set the Pages build type to "workflow" so only the artifact deploys), or stop committing root files. Until one of these is done, every merge can roll the live site back to the 10:27Z snapshot. This session did **not** merge its PR for that reason.
2. Make `pipeline.build` write only to `--out` (or require `--write-tracked` for `data/current/*`).
3. Add a gate that the deployed snapshot's counts match what the workflow built, or disclose on the page that deployed counts come from the CI refresh.
4. Do a browser check of the price/probability layout (E3-04).

## 6. Sources

- Live site: https://buffedlizard55-lab.github.io/OLBG1/ · [flagged](https://buffedlizard55-lab.github.io/OLBG1/flagged.html) · [snapshot JSON](https://buffedlizard55-lab.github.io/OLBG1/data/current/snapshot.json)
- Official: [NHL schedule API](https://api-web.nhle.com/v1/schedule/2026-10-22)
- GitHub: [Pages config](https://api.github.com/repos/buffedlizard55-lab/OLBG1/pages) · [canonical run](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39766032226) · [legacy Pages run](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39766030731)
- Repo: `README.md`, `.github/workflows/current-pages.yml`, `data/current/snapshot.json`, `pipeline/build.py`
