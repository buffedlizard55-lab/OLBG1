# Methodology — originated lines, winner picks, confidence

All originated numbers are **model outputs computed only from verified OLBG
tip counts**. They are not bookmaker odds, not official prices, and use no
invented form, injuries or statistics. The model is deliberately simple and
fully reproducible (`scripts/build_data.py`).

## Originated fair price (2-way winner markets)

For a leading selection with `k` tips from `n` total tips in its market:

```
model probability  p = (k + 1) / (n + 2)        # Laplace smoothing toward 50%
originated fair decimal price = 1 / p           # rounded to 2dp
opponent fair price           = 1 / (1 - p)
```

Smoothing stops a single tip (1/1 = "100%") producing a false 1.00 price:
1/1 → p = 66.7% → 1.50. Larger samples move closer to the raw tip share.

- **Handball Money Line is 3-way** (Home / Tie / Away): `p = (k+1)/(n+3)`;
  no single opponent price is shown.
- **Multi-runner markets** (golf outrights, greyhound races, tournament
  winners, Grand Prix winner): a 2-way formula would be meaningless without
  the full field, so **no win probability/price is originated** — only the
  tip-share index (`k/n`) is shown, flagged as "not a full book".
- Rows with 0 tips at snapshot get **no originated price** (blank, flagged).

## Handicap & totals lines

We do **not** fabricate spread/total numbers. Where OLBG itself lists a line
(e.g. WAS Wizards −4.5, Over/Under 239.5 on the event page), the line is
recorded as "OLBG-listed" and our contribution is the **side lean** from the
verified tip split in that market (see `research/markets.md`). Where the line
was not captured, the cell points to the OLBG event page instead of guessing.

## Winner pick

- Winner market leads (Win Match / Money Line / To Win / Win Match 2-way):
  pick = leading selection.
- Set-score leads (Set Betting / Set Score): pick = player/team in the
  set-score selection (logically implies the winner); confidence capped Low.
- Handicap leads: shown as "handicap lean only" — a handicap pick does not
  require winning the match, so it is never presented as a winner bet.
- Totals leads (Total Legs / Game Totals): **no winner pick** (blank) — a
  totals lean says nothing about who wins.
- 1st-set leads: shown as "1st-set lean only".

## Confidence rubric (winner markets only; everything else = Low)

| Level | Rule |
|---|---|
| **High** | n ≥ 7 tips **and** tip share ≥ 80% |
| **Medium** | (n ≥ 5 and share 60–79%) **or** (n = 4–6 and share ≥ 80%) |
| **Low** | All other rows: small samples, split opinion, non-winner markets, outrights/races |

"100%" from 1–3 tips is still Low — sample size matters more than the headline
percentage. Expert flags (OLBG-defined profitable tipsters) are displayed for
context but never raise a grade on their own.

## What "verified" means here

- Fixture, market, selection, tip counts: verified against OLBG (source of
  record for its own tips data) — every row links to its OLBG event page.
- High-confidence fixtures/form: additionally checked against official
  governing-body/league sources (NBA.com, ICC, PDC, WTA) — see
  `research/verification-log.md`. OLBG tipster comments were treated as
  unverified claims and only used where an official source corroborated them.
- Originated prices/confidence: model judgements, labelled as such.
- Anything that could not be confirmed is blank + flagged (Flagged page).

*Betting involves risk. Tip-share is a popularity signal, not evidence of
value, and past tipster performance does not guarantee future returns. 18+.
Gamble responsibly — GamCare / GambleAware.*
