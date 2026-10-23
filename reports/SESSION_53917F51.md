# Session `53917f51-olbg1` — independent audit of T496E (2026-10-23)

**Review dashboard:** [`../53917f51/index.html`](../53917f51/index.html) · [Flagged for Review](../53917f51/flagged.html) · [Official page reads](../53917f51/sources.html)
**Subject desk:** [`../496eaf02/index.html`](../496eaf02/index.html) · T496 source data is read-only in this task.
**As of:** 2026-10-23 21:58 UTC. T496 capture stamp: 2026-10-23 20:30 UTC.

## Scope and method

This is a read-only compliance audit of the merged `496eaf02` evening desk, not a new 15-sport match harvest. The audit script parses all 81 fixture records, 460 market outcomes, 51 featured-pick rows and 51 prediction texts; it recomputes thresholds, time/status consistency, source-domain issues and word-count/uniqueness checks. Inputs are SHA-256 checksummed in [`data/53917f51/audit.json`](../data/53917f51/audit.json). It does not modify `data/496eaf02/**`, `496eaf02/**`, the canonical root or any other session namespace.

Fresh official pages were fetched only for targeted review findings, through Arena's page tools, during **2026-10-23 21:30–21:47 UTC**. Their URLs and excerpts are retained in [`data/53917f51/evidence.json`](../data/53917f51/evidence.json). This is not line-by-line re-certification of all facts in all 15 sports; facts outside the targeted checks remain unverified in this audit.

## Executive summary

**Do not rely on T496 pick TN04 or its four High EuroLeague picks BK07–BK10.** T496 lists Leylah Fernandez v Marta Kostyuk as an upcoming Ningbo semifinal and recommends Over 17.5. Official WTA reporting says Kostyuk retired in the second round on 21 October; a separate WTA report says Iva Jovic—not Kostyuk—beat Jasmine Paolini 6-4, 6-3; the WTA semifinal preview dated 23 October lists Fernandez v Marie Bouzkova and Rybakina v Shnaider. T496's TN04 prose both names the wrong opponent and assigns a result to the wrong player. Separately, the official EuroLeague calendar has Round 7 on 21–23 October and Round 8 on 27–28 October; the four T496 Round 7 fixtures are not on the official 24 October schedule, and their cited injury URL returns 404. See [F-53917-01](../53917f51/flagged.html#F-53917-01) and [F-53917-14](../53917f51/flagged.html#F-53917-14).

Other high-priority findings:

- T496 publishes **51 High** labels, but only **3** are strictly above 70%; **2** are exactly 70%; **46** are below 70% (62–<70%). All 51 displayed fair American estimates are in the stated band, but the task's >70% threshold is not met by most of the set.
- GH01 is recorded as starting at 20:13Z but was observed at 20:30Z and still marked `upcoming`; its generated market/match pages retain it as upcoming. The linked GBGB schedule confirms the event date, not the exact 20:13Z timestamp.
- Four High EuroLeague picks (BK07–BK10) claim Round 7 fixtures on 24 October; the official calendar has no EuroLeague matches that date and lists different Round 7 pairings. The four attached injury notes mix statuses from unrelated Round 7 games; the T496-linked Round 7 injury URL returned 404.
- Two High-B cricket totals (CR01 and CR05) use ratings explicitly flagged as not re-fetched this session.
- CR02 and GS05 link only to sports-media publishers in their fixture rows. Official PCB and Limerick GAA pages read in this audit provide suitable governing-body review links; the T496 desk should add these rather than treating media links as official evidence.
- The T496 source register has 44 entries but no source-level retrieval time, HTTP status, captured excerpt or content hash. That is an auditability gap, not proof the listed pages were never read.

## Structural checks that pass

- T496's own suite: `python3 -m unittest tests.pipeline.test_desk_496eaf02 -v` — **21/21 passed**.
- 51 prediction texts, **39–91 words**, all unique by normalized full text; zero occurrences of the forbidden terms `model` and `verified` in prediction prose.
- 51 High-labelled displayed fair American prices are within −250…+10000.
- 81 fixture records, 67 priced fixture rows, 200 markets / 460 outcomes, all 15 sports represented.
- T496 discloses that no actual bookmaker quote is copied and that some sports have no High selections. The five-pick target is met in 7/15 sports; 8 sports have fewer than five, including four with zero. That is a disclosed coverage gap, not a reason to manufacture picks.

The T496 tests do not catch the TN04 opponent/result error, a fixture time earlier than its own observation timestamp, publisher authority, unsupported source-to-input mapping, or stale rating flags attached to a High pick.

## Validation boundary

Validation below was run after rebasing this session onto the current `main` snapshot. It checks the audit artifacts and the repository release gates; it does not expand the audit's source-verification scope.

- `python3 -m unittest tests.pipeline.test_desk_53917f51 tests.pipeline.test_desk_496eaf02 -v` — **28/28 passed** (7 audit checks and 21 T496E tests); namespaced HTML local links and fragments resolve.
- `python3 -m unittest discover -s tests/pipeline -v` — **335 tests passed**.
- `python3 -m unittest discover -s tests -p 'test*.py' -v` — **38 tests passed** (preserved release tests).
- `python3 -m pipeline.build --out _site` built **92 canonical pages**. `python3 -m pipeline.validate --site _site` reported **0 errors**; the generated release correctly reports no current/upcoming exact fixture or originated market rows from its retained observations.
- `NODE_PATH="${TMPDIR:-/tmp}/olbg-browser/node_modules" node tests/pipeline/browser.cjs` — **passed** desktop/mobile, project-subpath, filters/reset/sort, odds toggle, CSV, evidence links, expiry, and no-JavaScript checks.
- The validation results do not convert stale or unsupported T496 fields into verified facts. The audit remains read-only, and no peer-owned files were edited.

## Line-by-line findings

### F-53917-01 — Critical: TN04 is a stale fixture and the prediction misattributes a result

- **Repository rows:** [`data/496eaf02/fixtures.json#L113-L145`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L113-L145) records Fernandez v Kostyuk as an upcoming 24 October semifinal. [`data/496eaf02/predictions.json#L41`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/predictions.json#L41) is its prediction; `matches.csv` row 5 marks Over 17.5 High at 64.73% / −184.
- **Official WTA evidence:** [21 Oct: Kostyuk retired against Alexandrova](https://www.wtatennis.com/news/4596745/fernandezs-marathon-win-kostyuks-retirement-headline-day-3-in-ningbo); [22 Oct: Jovic beat Paolini 6-4, 6-3](https://www.wtatennis.com/news/4597089/jovic-rallies-past-paolini-to-reach-ningbo-quarterfinals); [23 Oct: WTA's Ningbo semifinal preview](https://www.wtatennis.com/news/4597893/ningbo-semifinals-preview-leylah-fernandez-vs-marie-bouzkova-diana-shnaider-vs-elena-rybakina) lists Fernandez v Bouzkova and Rybakina v Shnaider.
- **Disposition:** withdraw TN04 and its prediction/markets from active selection views. Rebuild only from an official current order of play. This audit does not edit the peer-owned desk.

### F-53917-14 — Critical: four High EuroLeague picks are absent from the official 24 October schedule

- T496 lists BK07–BK10 as EuroLeague Round 7 games on 24 October, all High, with predictions about “Saturday” fixtures. The four fixture records begin at [`fixtures.json#L2988`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L2988), [`#L3034`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L3034), [`#L3079`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L3079) and [`#L3125`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L3125); the featured rows are [`matches.csv#L79-L82`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/matches.csv#L79-L82).
- The [EuroLeague official full-season calendar PDF](https://media-cdn.cortextech.io/1dU3kpCqReRp93/1BSdBWIjChWbPc/de89146d-ddb7-4931-9deb-f72672b4d63b.pdf), linked from the [official schedule announcement](https://www.euroleaguebasketball.net/en/euroleague/news/the-2026-27-euroleague-schedule-is-official/), puts Round 7 on 21–23 October and the next round on 27–28 October. Actual Round 7 pairings include Efes–Besiktas, Bayern–Dubai, Partizan–Crvena Zvezda, Panathinaikos–Baskonia, and Olympiacos–Fenerbahce; none matches BK07–BK10, and there are no EuroLeague games listed on 24 October.
- The [current official Round 7 injury report](https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-fantasy/) confirms that T496's injury statements refer to different fixtures: Efes absences were reported for Efes v Besiktas; Fenerbahce was full-strength for Fenerbahce v Olympiacos, whose report listed Fournier and Dorsey out and Montero doubtful. T496's cited [Round 7 URL](https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-el2627/) returned a 404 page in this audit.
- **Disposition:** withdraw BK07–BK10 and their markets/predictions. Rebuild only from a current official fixture schedule and the corresponding per-game injury report. This review does not edit the peer-owned desk.

### F-53917-02 — High: most “High” labels fall below the >70% brief threshold

- Recomputed from [`data/496eaf02/matches.csv`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/matches.csv) and `markets.csv`: **3 >70%**, **2 exactly 70%**, **46 <70%**, among 51 High-labelled featured picks. The code explicitly promotes 0.62–<0.70 outcomes to `high` ([`scripts/se496eaf02_model.py#L22-L29`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/scripts/se496eaf02_model.py#L22-L29), [`#L67-L90`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/scripts/se496eaf02_model.py#L67-L90)); the dashboard says “62% or more” ([`496eaf02/high-confidence.html`](../496eaf02/high-confidence.html)).
- **Disposition:** if the brief's strict >70% threshold governs High, relabel/suppress all below-threshold picks. The two 70.00% rows do not satisfy a strict “greater than 70%” condition. T496's disclosed High-B policy is different from the requested threshold.

### F-53917-03 — High: GH01 is marked upcoming after its stored start

- [`data/496eaf02/fixtures.json#L1913-L1949`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L1913-L1949) records GH01 start `2026-10-23T20:13:00Z`, observation `2026-10-23T20:30:00Z`, `state=upcoming`, and price expiry `02:30Z`. The generated [`matches.html`](../496eaf02/matches.html) and [`sports/greyhounds.html`](../496eaf02/sports/greyhounds.html) still display the row as upcoming.
- GBGB's [2026 Category One schedule](https://www.gbgb.org.uk/racing/open-races/2025-category-one-schedule/) confirms Friday 23 October at Romford but does not give the 20:13Z start. Its [Champion Stakes preview](https://www.gbgb.org.uk/category-one-glory-beckons-in-coral-100-champion-stakes-final/) also says the final is Friday, without that exact time.
- **Disposition:** withhold GH01 from “upcoming” and active markets. If the exact time cannot be confirmed from an official schedule/racecard, blank it and leave status unknown; if confirmed at 20:13Z, classify it elapsed.

### F-53917-04 — High: TN03 has a populated time the record itself says is unverified

- [`data/496eaf02/fixtures.json#L84-L111`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L84-L111) stores `2026-10-24T09:30:00Z` while the row flag says the value was rendered by OLBG and the official WTA draw does not publish the UTC time. The linked [WTA draw PDF](https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf) was read; its draw/seed text does not establish that exact start.
- **Disposition:** blank the exact UTC start until an official order of play supplies it; keep only a separately confirmed date. A warning does not make an unconfirmed value compliant with the brief's blank-if-unverified rule.

### F-53917-05 — High: media-source domains pass as “official”

- [`CR02`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L997-L1031) lists only ESPNcricinfo; [`GS05`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L1876-L1911) lists Limerick Leader and The 42. The validator's `OFFICIAL_DOMAINS` includes `cricinfo.com` and `limerickleader.ie` ([`tests/pipeline/test_desk_496eaf02.py#L19-L27`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/tests/pipeline/test_desk_496eaf02.py#L19-L27)); its fixture test checks source IDs, not whether a publisher is the governing body ([`#L30-L35`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/tests/pipeline/test_desk_496eaf02.py#L30-L35)).
- **Official alternatives fetched:** [PCB's schedule](https://www.pcb.com.pk/press-release-detail/pakistan-to-host-sri-lanka-and-england-for-t20is-odi-tri-series-and-tests.html), [PCB's 22 October results and 25 October fixture](https://www.pcb.com.pk/news-detail/sri-lanka-seal-second-highest-chase-in-odi-history-as-brook-s-record-double-ton-goes-in-vain.html), [PCB's Pakistan v England result](https://www.pcb.com.pk/news-detail/arafat-minhas-6-40-and-59-sink-england-as-pakistan-win-consecutive-games-in-odi-tri-series.html), and [Limerick GAA's official fixtures page](https://limerickgaa.ie/senior-hurling-fixtures/). Limerick GAA's current official page confirms Kilmallock v Na Piarsaigh on 25 October at 3:45pm at TUS Gaelic Grounds; its [official results page](https://limerickgaa.ie/senior-hurling-results/) confirms the semifinal results.
- **Disposition:** replace media-only fixture evidence with governing-body links and test authority at the per-row source level. The sports facts may be right; the linked source authority in those rows is not.

### F-53917-06 — High: two High-B cricket totals rely on flagged stale inputs

- [`CR01`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L956-L995) and [`CR05`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L1110-L1150) are both High-B totals at 65.95% / −194 in `matches.csv`, while their fixture flags explicitly say the team/A-team ratings were not re-fetched this session.
- The linked ICC/NZC/Cricket Australia sources support fixture discovery; the data rows do not provide official links for the reused rating inputs. The site tests check fair-price arithmetic and confidence consistency, not whether the input rating is current or supported.
- **Disposition:** keep these inputs/picks unverified or downgrade/suppress them until current official evidence supports the ratings. Do not treat a flagged stale input as a current verified statistic.

### F-53917-07 — High: GH01’s semi time conflicts with the official figure

- T496 stores “fastest semi 35.69s” in the GH01 input note ([`data/496eaf02/fixtures.json#L1941-L1947`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/fixtures.json#L1941-L1947)). GBGB's official [Champion Stakes preview](https://www.gbgb.org.uk/category-one-glory-beckons-in-coral-100-champion-stakes-final/) says Grouchos Gregor won the third semi in **35.36sec (-20)** and calls him the fastest semi-final winner.
- **Disposition:** correct the note or leave the value blank pending an official correction. This remains a factual discrepancy even though GH01 is Low confidence.

### F-53917-08 — Medium: source registry has no per-source fetch record

- [`data/496eaf02/sources.json`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/sources.json) contains 44 `id` / `name` / `url` entries; none records access time, response status, content excerpt or content hash. T496's report claims 60 official-source reads, but the available registry cannot map a retrieved page to a specific row/input or reproduce the observation.
- **Disposition:** add per-source retrieval metadata and row/field-level evidence pointers. This is an auditability gap, not proof that the pages were never read.

### F-53917-09 — Medium: fair odds are not available bookmaker quotes

- T496 explicitly says its prices are zero-vig fair estimates and no bookmaker quote is copied ([methodology](../496eaf02/methodology.html), [predictions](../496eaf02/predictions.html)). The model code selects several handicap/total lines to target a probability of 0.66 ([`scripts/se496eaf02_model.py#L26-L29`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/scripts/se496eaf02_model.py#L26-L29), [`#L480-L490`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/scripts/se496eaf02_model.py#L480-L490)) and features an in-band pick from 0.62 ([`#L493-L520`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/scripts/se496eaf02_model.py#L493-L520)). No observed book quote or availability evidence accompanies those prices.
- **Disposition:** keep “fair-price estimate — not an available sportsbook offer” adjacent to every price. A custom line's estimated probability is not a measured edge or proof it can be placed on OLBG.

### F-53917-10 — Medium: prediction-level injury/availability completeness is unproven

A case-insensitive text scan found explicit injury/availability wording in **7 of 51** prediction texts (including “without,” “doubtful,” “questionable,” and “available”). That is a prose count, not proof that the other 44 matches had no relevant availability issue. For NBA picks, the official 23 October 4:15 p.m. ET report was issued 15 minutes before T496’s 20:30Z capture; the report includes game-specific statuses (for example, Dallas’s Dereck Lively II and Indiana’s T.J. McConnell listed out, with Aaron Nesmith and Ben Sheppard questionable). For EuroLeague, the official Round 7 injury report is tied to specific 21–23 October matchups, not the four nonexistent T496 fixtures described in F-53917-14. Keep a per-pick source/time/status ledger; otherwise full coverage remains unproven.

### F-53917-11 — High: PDC Order of Merit inputs lack readable official evidence

- T496's report says PDC ranking values were cross-checked on multiple outlets because the official PDC rankings page rendered behind a consent wall ([`reports/SESSION_496EAF02.md#L91-L92`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/reports/SESSION_496EAF02.md#L91-L92)). The four Darts picks labelled High use rank/prize inputs in [`scripts/se496eaf02_data.py#L349-L375`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/scripts/se496eaf02_data.py#L349-L375), while their `pdc` source entry is a tournament-hub URL rather than a captured ranking table ([`#L38`](https://github.com/buffedlizard55-lab/OLBG1/blob/main/scripts/se496eaf02_data.py#L38)).
- The official [PDC rankings page](https://www.pdc.tv/rankings) was fetched for this audit but returned a cookie-consent screen with no readable player values. No rank values are promoted as confirmed here.
- **Disposition:** keep the rank/prize inputs and resulting picks flagged until a readable official PDC ranking source is linked and the player values are retained.

### F-53917-12 — Low: discovery date says 2023 in three artifacts

`reports/SESSION_496EAF02.md#L16`, `496eaf02/methodology.html#L9` and `scripts/se496eaf02_build.py#L327` print `2023-10-23`, although the T496 capture is 2026-10-23. Correct the editorial date so freshness is not ambiguous.

### F-53917-13 — Informational: five-pick target is unmet in eight sports

Only 7/15 sports reach five High-labelled picks; four have zero. T496 discloses this rather than inventing selections. It remains a coverage gap against the daily target, but does not justify promoting unsupported picks.

## Source register and manual review

All official-page URLs and excerpts freshly read for the targeted findings are in [`data/53917f51/evidence.json`](../data/53917f51/evidence.json) and the [source-read page](../53917f51/sources.html). Repository references resolve to the T496 data/site and its validator. The key official pages are:

- WTA: [Kostyuk retirement](https://www.wtatennis.com/news/4596745/fernandezs-marathon-win-kostyuks-retirement-headline-day-3-in-ningbo), [Jovic–Paolini result](https://www.wtatennis.com/news/4597089/jovic-rallies-past-paolini-to-reach-ningbo-quarterfinals), [Ningbo semifinal pairings](https://www.wtatennis.com/news/4597893/ningbo-semifinals-preview-leylah-fernandez-vs-marie-bouzkova-diana-shnaider-vs-elena-rybakina), and [order-of-play route](https://www.wtatennis.com/tournaments/2092/ningbo/2026/order-of-play) (the fetch did not expose a schedule).
- EuroLeague: [full 2026–27 calendar PDF](https://media-cdn.cortextech.io/1dU3kpCqReRp93/1BSdBWIjChWbPc/de89146d-ddb7-4931-9deb-f72672b4d63b.pdf), [schedule announcement](https://www.euroleaguebasketball.net/en/euroleague/news/the-2026-27-euroleague-schedule-is-official/), and [current Round 7 injury report](https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-fantasy/); the broken T496-linked injury URL is recorded in the evidence register.
- NBA: [23 Oct 4:15 p.m. ET injury report](https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_04_15PM.pdf) (15 minutes before T496 capture) and [5:30 p.m. ET update](https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_05_30PM.pdf).
- PCB: [tri-series schedule](https://www.pcb.com.pk/press-release-detail/pakistan-to-host-sri-lanka-and-england-for-t20is-odi-tri-series-and-tests.html), [official recent results](https://www.pcb.com.pk/news-detail/sri-lanka-seal-second-highest-chase-in-odi-history-as-brook-s-record-double-ton-goes-in-vain.html).
- Limerick GAA: [official final fixture](https://limerickgaa.ie/senior-hurling-fixtures/) and [official semifinal results](https://limerickgaa.ie/senior-hurling-results/).
- Greyhound Board of Great Britain: [Champion Stakes preview](https://www.gbgb.org.uk/category-one-glory-beckons-in-coral-100-champion-stakes-final) and [2026 Category One schedule](https://www.gbgb.org.uk/racing/open-races/2025-category-one-schedule/).
- PDC: [official rankings route](https://www.pdc.tv/rankings); the page read in this audit returned only a consent screen, not the rankings.

## Task status

Independent review is complete. All irregularities are published on [`53917f51/flagged.html`](../53917f51/flagged.html). The subject desk was not edited. The final integration session can regenerate the canonical archive; `pipeline/build.py` auto-indexes namespaced `index.html` directories and HTML reports. No task/fixture fact is marked newly verified outside the sources and facts explicitly listed above.
