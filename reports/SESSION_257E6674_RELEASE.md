# T257E canonical research release — session 257e6674-olbg1

## Publication status

PR [#88](https://github.com/buffedlizard55-lab/OLBG1/pull/88) is the integration vehicle. **Merge and this session's final deployment are not yet confirmed at this checkpoint.** Prior PR #84's successful deployment is not claimed as ours.

## Evidence and output

- 108 fixture/event listings in the selected 22 October import; 43 statistical observations; 29 official-source checks (32 total captures including OLBG discovery/policy).
- 15 categories with captured listings; all 17 categories partial/unverified. Darts and greyhound accepted fixture fields remain blank.
- 25 independent experimental price books, 50 two-way markets, 100 outcome prices; 23 Low preferences, two equal-line books without an arbitrary winner; no Medium/High, no actual bookmaker quotes or value claims.
- Separate complete MLB game-ID/season projection re-read; original matchup/start evidence expiry was not renewed. NBA season not explicitly extracted remains blank.
- Official sources include NHL, MLB, NBA, EuroLeague, ATP/WTA, WST, PCB, IRL, LNR, EHF, AFLW, PGA TOUR, F1, Munster GAA, PLS, Riot and GBGB. Captures state actual read scope; selected excerpts are not raw full-page archives.
- Specific findings include the internally inconsistent archived Nashville 3–3–2/9-points input (official reread 3–2–3/9), contradictory Madrid overall/away records, source-time ambiguity, the missing PGA article, and volleyball competition identity conflict.
- The file/row audit is structural and location-specific, not semantic certification of every repository sentence. Every detected historical row has a review/source link and blank accepted-current fields. Mirrors, nested books and JSON aliases are explicit.

## Local release gates

- 89 pipeline unit/integration tests; 38 preserved upstream tests.
- Canonical field/hash/timestamp/price/source-row/link/fragment validator: 0 errors.
- Headless Chromium desktop/mobile and `/OLBG1/` prefix: filter/search/reset/sort, odds format, CSV, source deep-links, empty states, expiry removal and no-JS tables pass.
- No price clipping, missing-side rating fallback, automatic High label or 70% confidence shortcut.
- UTC overnight starts are retained even when the league's calendar date is the previous date. Placeholder participants/IDs stay null; unknown status never becomes pre-match.

## Coordination and preservation

The earlier active T257E claim was pushed at 07:18 UTC. T61 independently claimed root at 07:20 and merged PR #84 at 08:08. The collision was disclosed in #84/#88 and the board. This integration rebases on and preserves PR #84 rather than discarding it. Its root/README/assets are archived at `archive/root-20261022/` with original hashes, an archive warning and rewritten links. Its earlier archive and all `data/release`, `scripts/release_*`, `tests/release` and parallel namespaces remain unchanged.

One custom publisher remains: `current-pages.yml`. The previous T61 workflow is an explicit manual, non-publishing reproduction check; its code/evidence are retained. The original `scripts/build_site.py` command delegates to the canonical pipeline. Legacy generators are not silently run by the canonical publication workflow.

## Hosting observation, not a guessed blocker

The Pages API reports legacy `main:/`. An attempted interactive PUT to select workflow mode returned **403 Resource not accessible by integration**. Content, PR and workflow writes work; no credentials were requested.

Importantly, the existing standard artifact route **does work**: upstream Actions run [39745549884](https://github.com/buffedlizard55-lab/OLBG1/actions/runs/39745549884) completed successfully, including Pages deployment, and its 97-entry T61 landing page was fetched from the live URL. The separate legacy branch-build run was cancelled and its legacy status endpoint reported errored; that is not the artifact deployment result. The canonical workflow uses the proven pinned configure-pages/deploy-pages path with the repository's authorized job token. No Pages-setting success or current-session publication is assumed from this observation.

Final merge SHA, current-session workflow receipt and live-content checks will be appended below after they actually happen.
