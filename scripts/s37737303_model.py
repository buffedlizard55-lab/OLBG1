"""Price arithmetic for the 37737303 desk.

Everything here is arithmetic on inputs that are handed to it.  No input is
invented in this module: the calling script passes either a value read from an
official page this session or an explicit placeholder, and the placeholder is
carried through to the published row so a reader can see it.

Vocabulary used throughout:

* ``prob`` is our estimate of the chance the selection wins, 0..1.
* ``fair`` is the zero-margin American price implied by ``prob``.
* A price is inside the brief's band when it is >= -250 and <= +10000.
"""
from __future__ import annotations

import math

BAND_LOW = -250
BAND_HIGH = 10000

#: Documented placeholder used when an opponent's official record was not read.
#: It is the league-average point percentage we use rather than guessing a
#: specific club's form, and every row that uses it is labelled.
LEAGUE_AVERAGE_NHL = 0.550

#: Home-ice advantage expressed on the logit scale.  Applied once, to the home
#: side, and identical for every NHL fixture on the board.
HOME_ICE_LOGIT = 0.15

#: Rating spread.  Chosen so that a 0.200 point-percentage gap moves the home
#: side by roughly 17 percentage points, which is about what a top-versus-
#: bottom NHL matchup looks like at this point of a season.
RATING_SCALE = 3.2

#: Goal-difference weighting inside a club's rating.
GD_WEIGHT = 0.035


def american(prob: float) -> int:
    """Zero-margin American price for a probability, rounded to the nearest 5."""
    if not 0.0 < prob < 1.0:
        raise ValueError(f"probability out of range: {prob}")
    if prob >= 0.5:
        raw = -100.0 * prob / (1.0 - prob)
    else:
        raw = 100.0 * (1.0 - prob) / prob
    return int(round(raw / 5.0) * 5)


def decimal(prob: float) -> float:
    return round(1.0 / prob, 2)


def implied(price: int) -> float:
    if price >= 0:
        return 100.0 / (price + 100.0)
    return -price / (-price + 100.0)


def in_band(price: int) -> bool:
    return BAND_LOW <= price <= BAND_HIGH


def nhl_rating(point_pctg: float, goal_diff: float, games: int) -> float:
    return point_pctg + GD_WEIGHT * (goal_diff / games)


def nhl_moneyline(home_rating: float, away_rating: float) -> float:
    return 1.0 / (1.0 + math.exp(-(RATING_SCALE * (home_rating - away_rating) + HOME_ICE_LOGIT)))


def normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def over_prob(expectation: float, line: float, sd: float = 1.45) -> float:
    """Chance the total lands above *line*, given a normal expectation."""
    return 1.0 - normal_cdf((line - expectation) / sd)


def expected_goals(goals_for: float, games_for: int, goals_against: float, games_against: int) -> float:
    return (goals_for / games_for) + (goals_against / games_against)


def grade(prob: float, fair_price: int, verified: bool, fixture_verified: bool) -> str:
    """Confidence label under the desk's published policy.

    High    our chance is 60% or better, at least one side of the fixture rests
            on an official page read this session, and the fair price is inside
            the brief's band.
    Medium  chance is 55% or better with an official input, or 60% or better
            where only the fixture (not the form) is official.
    Low     everything else, including every row with no official input.
    """
    if not in_band(fair_price):
        return "low"
    if prob >= 0.60 and verified:
        return "high"
    if prob >= 0.60 and fixture_verified:
        return "medium"
    if prob >= 0.55 and (verified or fixture_verified):
        return "medium"
    return "low"


def confidence_reason(prob: float, fair_price: int, verified: bool, fixture_verified: bool) -> str:
    if not in_band(fair_price):
        side = "shorter than the -250 floor" if fair_price < BAND_LOW else "longer than the +10000 ceiling"
        return f"passed on the band: our fair price of {fair_price} is {side}"
    if prob >= 0.60 and verified:
        return "60%+ with an official form input and a price inside the band"
    if prob >= 0.60 and fixture_verified:
        return "60%+ but only the fixture is official, so the ceiling is medium"
    if prob >= 0.55 and (verified or fixture_verified):
        return "55%+ with an official input"
    return "below the 55% threshold, or no official input was read"
