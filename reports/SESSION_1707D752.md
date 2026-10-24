# Session `1707d752-olbg1` — task `T1707`

Fresh 24 October 2026 desk, built to the "clarity first" brief: an executive summary that states the picks in
plain language, every pick carrying the exact page and anchor where its full written prediction lives, and no
label that the underlying evidence cannot carry.

* **Branch:** `arena/1707d752-olbg1` (base `1a203e9`).
* **Published:** `1707d752/index.html` (also deployed, since `pipeline/build.py` copies every namespaced desk into
  the Pages artifact).
* **Rebuild:** `python3 scripts/s1707d752_build.py && python3 scripts/s1707d752_validate.py`.
* **Source read window:** 17:42–18:05 UTC, 24 October 2026.

## What was delivered

| Artefact | Count |
| --- | --- |
| Sports scanned on OLBG | 15 |
| Events listed (priced + unpriced + hub-only listings) | 100 |
| Matches priced from official inputs | 19 |
| Market boards issued (money line, puck line/run line, totals) | 39 |
| Written predictions (≥30 words, unique, specific) | 19 |
| High confidence picks | 4 |
| Medium | 13 |
| Low | 2 |
| Review flags | 12 |

## The picks

| # | Sport | Match | Selection | Our price | Our chance | Confidence | Where it lives |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ice Hockey | Boston Bruins v San Jose Sharks | Boston Bruins | -252 (1.40) | 71.6% | Medium | `predictions.html#pick-nhl-sjs-bos` |
| 2 | Ice Hockey | Columbus Blue Jackets v Vegas Golden Knights | Vegas Golden Knights | -175 (1.57) | 63.6% | High | `predictions.html#pick-nhl-vgk-cbj` |
| 3 | Ice Hockey | New Jersey Devils v Los Angeles Kings | New Jersey Devils | -172 (1.58) | 63.2% | High | `predictions.html#pick-nhl-lak-njd` |
| 4 | Basketball | Philadelphia 76ers v Milwaukee Bucks | Philadelphia 76ers | -166 (1.60) | 62.4% | Medium | `predictions.html#pick-nba-mil-phi` |
| 5 | Ice Hockey | Washington Capitals v Buffalo Sabres | Washington Capitals | -155 (1.65) | 60.7% | High | `predictions.html#pick-nhl-buf-wsh` |
| 6 | Ice Hockey | Edmonton Oilers v Toronto Maple Leafs | Edmonton Oilers | -154 (1.65) | 60.6% | High | `predictions.html#pick-nhl-tor-edm` |
| 7 | Basketball | Charlotte Hornets v Miami Heat | Charlotte Hornets | -142 (1.70) | 58.8% | Medium | `predictions.html#pick-nba-mia-cha` |
| 8 | Basketball | Dallas Mavericks v San Antonio Spurs | Dallas Mavericks | -142 (1.70) | 58.8% | Medium | `predictions.html#pick-nba-sas-dal` |
| 9 | Baseball | Milwaukee Brewers v Tampa Bay Rays | Milwaukee Brewers | -133 (1.75) | 57.1% | Medium | `predictions.html#pick-mlb-tb-mil` |
| 10 | Ice Hockey | Pittsburgh Penguins v Nashville Predators | Pittsburgh Penguins | -132 (1.76) | 56.9% | Medium | `predictions.html#pick-nhl-nsh-pit` |
| 11 | Basketball | Denver Nuggets v New Orleans Pelicans | Denver Nuggets | -132 (1.76) | 56.8% | Medium | `predictions.html#pick-nba-nop-den` |
| 12 | Basketball | Phoenix Suns v Golden State Warriors | Phoenix Suns | -132 (1.76) | 56.8% | Medium | `predictions.html#pick-nba-gsw-phx` |
| 13 | Ice Hockey | St. Louis Blues v Carolina Hurricanes | Carolina Hurricanes | -123 (1.81) | 55.2% | Medium | `predictions.html#pick-nhl-car-stl` |
| 14 | Basketball | Cleveland Cavaliers v Brooklyn Nets | Cleveland Cavaliers | -122 (1.82) | 55.0% | Medium | `predictions.html#pick-nba-bkn-cle` |
| 15 | Basketball | Atlanta Hawks v Houston Rockets | Atlanta Hawks | -122 (1.82) | 55.0% | Medium | `predictions.html#pick-nba-hou-atl` |
| 16 | Basketball | Chicago Bulls v Washington Wizards | Chicago Bulls | -122 (1.82) | 55.0% | Medium | `predictions.html#pick-nba-was-chi` |
| 17 | Ice Hockey | Ottawa Senators v New York Rangers | New York Rangers | -119 (1.84) | 54.3% | Medium | `predictions.html#pick-nhl-nyr-ott` |
| 18 | Ice Hockey | Utah Mammoth v Tampa Bay Lightning | Utah Mammoth | -111 (1.90) | 52.5% | Low | `predictions.html#pick-nhl-tbl-uta` |
| 19 | Ice Hockey | Seattle Kraken v Minnesota Wild | Seattle Kraken | -109 (1.92) | 52.2% | Low | `predictions.html#pick-nhl-min-sea` |

## How the prices are made

No bookmaker price is copied, and no OLBG tip percentage is treated as a probability.

* **Ice hockey** — each club's goals for and against per game are shrunk toward the league rate with an eight-game
  prior (league rate today: **3.152 goals per team per game**). Expected goals = own scoring rate × opponent
  concession rate ÷ league rate, × 1.03 at home and × 0.97 away; a Poisson grid over 0–12 goals gives the result,
  the −1.5 puck line and the 5.5 total.
* **Basketball** — win rates shrunk toward .500 with a Beta(12,12) prior, in logits, plus a 0.20 home term.
  Handicap and total are withheld, because the NBA standings page publishes wins and losses only.
* **Baseball** — log5 on the 162-game records plus a mild prior and a 0.16 home term.

Fair decimal is `1/p` with no margin; the American price is derived from the unrounded decimal.

**The High gate actually applied:** our chance ≥ 60%, the selection's fair price inside −250…+10000, every input
captured, and both sides past the sample floor (hockey 8 games, basketball 20, baseball 60). A pick that misses one
condition is published as Medium **with the missed condition printed on it**, never relabelled.

## The brief's own arithmetic

A fair price of −250 is exactly 71.43%. Any selection above 70% prices shorter than −233, so "more than 70% **and**
inside −250…+10000" describes a 70.0–71.4% sliver. That is why the desk publishes the occupied probability for
every pick and marks, per row, whether it also clears the literal test (flag **F-17-01**). Boston at 71.6% is the
clearest example: the strongest call of the day is priced −252, two cents outside the window, so it is a Medium.

## Coverage, stated plainly

Only three sports published records this desk could read: the NHL team summary and schedule, the NBA standings and
game list, and the MLB World Series game feed. Those three produced all 19 priced matches and all 19 predictions.

Twelve sports are listed but unpriced, and each says exactly what blocked it: tennis (ATP rankings page rendered an
empty filter shell), cricket (NZC 404, no PCB fixture row read), rugby union (Premiership Rugby served a marketing
page), rugby league (no match listed, only 2027 outrights), darts (PDC cookie wall), snooker (the listed semi-final
is already live and the final's opponent is undecided), golf (hub returned "No tips found."), volleyball and handball
(no club league tables captured), Gaelic sports (no club fixtures captured), greyhounds (no GBGB card captured and
the hub's clocks do not reconcile), motor racing (qualifying had not run). Five High picks per sport is not
reachable on that evidence; flag **F-17-12** says so on the site.

## Times

Every priced match now carries the **official UTC start** from the league feed (NHL schedule API, NBA game list,
MLB game feed), converted on the page to US Pacific, US Eastern, UK and Central European time, with both date
formats. Hub-only listings reproduce OLBG's clock verbatim, labelled "clock unstated", and are not converted
(flag **F-17-02**). Games already under way at the read window — Anaheim at Philadelphia, 17:00 UTC — were excluded
rather than priced.

## Gates

* `python3 scripts/s1707d752_validate.py` — 1,695 checks, 0 failures: price arithmetic, tier recomputation from the
  published rule, prose length and uniqueness, market withholding, link and anchor resolution, JSON freshness.
* `python3 -m unittest discover -s tests/pipeline` — 493 tests OK (14 of them this desk's).
* `python3 -m pipeline.validate --site .` and `--site _site` — 0 errors.
* `python3 scripts/validate.py` — 0 errors, 3 pre-existing warnings owned by desk `f7fa77fc`.

## Disclosures

* This session changed **one line** of `pipeline/build.py`: `latest_desk()` now points at `1707d752/index.html`
  instead of `3d121822/index.html`, so the deployed homepage surfaces today's desk. Nothing else in
  `pipeline/**`, `data/current/**`, the workflows, the root pages or any peer desk was touched.
* `Venue` for Toronto at Edmonton was flagged earlier in the session as unconfirmed and then confirmed against the
  league schedule; the flag was rewritten rather than deleted so the correction stays visible.
* No injury, availability or lineup claim appears anywhere: no official injury report was read (flag **F-17-05**).
