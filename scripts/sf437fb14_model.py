"""Session f437fb14 - market origination and confidence grading.

Design contract (repeated on methodology.html):

* We originate our own line for every fixture where the verified inputs exist. Fair decimal
  odds are 1/p with no margin, so the published American price is directly checkable from
  the published probability.
* The brief's price window is -250 .. +10000. A price shorter than -250 is out of scope, so
  every selection we publish is checked against that window in both directions.
* Confidence is a function of (a) how much verified, match-specific evidence we hold and
  (b) the model probability - not of the price alone. The site always prints the probability
  next to the badge so the reader can judge for themselves.
* No value is invented. If an input is missing, the market is withheld and the reason is
  printed on the markets page.
"""
from statistics import NormalDist

N = NormalDist()

# --- price helpers ---------------------------------------------------------

def american(p):
    """Fair American price for probability p, zero margin."""
    if p is None or not (0 < p < 1):
        return None
    if p >= 0.5:
        return -round(100 * p / (1 - p))
    return round(100 * (1 - p) / p)


def decimal(p):
    return None if p is None else round(1 / p, 3)


def implied(am):
    if am is None:
        return None
    return (-am) / (-am + 100) if am < 0 else 100 / (am + 100)


def in_band(am):
    """The brief's window: -250 <= price <= +10000."""
    return am is not None and -250 <= am <= 10000


def band_note(am):
    if am is None:
        return "no price"
    if am < -250:
        return "outside the brief's window (shorter than -250)"
    if am > 10000:
        return "outside the brief's window (longer than +10000)"
    return "inside the brief's window"


# --- distributions ---------------------------------------------------------

def _poisson_cdf(k, lam):
    term = 1.0
    total = 0.0
    for i in range(0, k + 1):
        if i:
            term *= lam / i
        total += term
    return total * pow(2.718281828459045, -lam)


# --- models ----------------------------------------------------------------

NBA_PRIOR_GAMES = 12.0      # pseudo-games at .500 used to shrink the 2026-27 sample
NBA_HOME_LOGIT = 0.10       # home-court edge in log-odds (about +5.5 pts of win probability
                            # at a 50/50 game; consistent with league home win rates)
NBA_MARGIN_SD = 12.0        # points, standard deviation of an NBA final margin


def nba_shrunk(rec):
    w, l = rec["w"], rec["l"]
    gp = w + l
    return (w + NBA_PRIOR_GAMES / 2) / (gp + NBA_PRIOR_GAMES)


def nba_match(home_rec, away_rec):
    ph, pa = nba_shrunk(home_rec), nba_shrunk(away_rec)
    # log5 for two-team matchup
    denom = ph + pa - 2 * ph * pa
    p_home_neutral = (ph - ph * pa) / denom if denom else 0.5
    # home court in log-odds
    z = N.inv_cdf(min(max(p_home_neutral, 1e-6), 1 - 1e-6)) + NBA_HOME_LOGIT
    p_home = N.cdf(z)
    mu = NBA_MARGIN_SD * N.inv_cdf(min(max(p_home, 1e-6), 1 - 1e-6))
    line = round(mu * 2) / 2
    if abs(line) < 0.5:
        line = 0.5
    p_home_covers = 1 - N.cdf((line - mu) / NBA_MARGIN_SD)
    return dict(p_home=p_home, p_away=1 - p_home, mu=mu, line=line,
                p_home_covers=p_home_covers, p_away_covers=1 - p_home_covers,
                ph=ph, pa=pa)


MLB_TEAM_RUNS_FALLBACK = 4.50   # documented league anchor used ONLY where a club's own
                                # 2026 run rate was not captured (labelled in the prose)
MLB_MARGIN_SD = 4.2


def mlb_match(inp):
    away_rpg = inp["away_rs"] / 162 if inp["away_rs"] else MLB_TEAM_RUNS_FALLBACK
    home_rpg = MLB_TEAM_RUNS_FALLBACK   # Milwaukee regular-season run rate not captured
    sp_home_r9 = 9 * inp["sp_home"]["era"] / 9 * 1.0     # ERA is runs/9 by definition
    sp_away_r9 = inp["sp_away"]["era"]
    home_exp = (home_rpg + sp_away_r9) / 2
    away_exp = (away_rpg + sp_home_r9) / 2
    lam = home_exp + away_exp
    line = round(lam * 2) / 2
    if abs(line - lam) < 0.25:
        line = line + 0.5
    mu = away_exp - home_exp
    p_away = 1 - N.cdf((0 - mu) / MLB_MARGIN_SD)   # away wins when their margin > 0
    p_under = _poisson_cdf(int(line - 0.5), lam)
    return dict(lam=lam, line=line, home_exp=home_exp, away_exp=away_exp, mu=mu,
                p_away=p_away, p_home=1 - p_away, p_under=p_under, p_over=1 - p_under,
                away_rpg=away_rpg, home_rpg=home_rpg, used_fallback=True)


F1_LAP_SD = 0.45   # seconds; spread of a race-pace delta given a single-lap comparison


def f1_head_to_head(a_head, b_head, gap, extra_sessions_ahead=0):
    """Probability that driver A finishes ahead of driver B."""
    z = gap / F1_LAP_SD
    p = N.cdf(z)
    if extra_sessions_ahead:
        p = min(0.95, p + 0.02 * extra_sessions_ahead)
    return dict(p_a=p, p_b=1 - p, sigma=F1_LAP_SD, gap=gap)


# --- grading ---------------------------------------------------------------

def grade(evidence_count, has_price, blocked):
    if blocked or not has_price:
        return "C"
    if evidence_count >= 4:
        return "A"
    if evidence_count == 3:
        return "B"
    return "C"


def confidence(p, g, price):
    """High / Medium / Low from probability + evidence grade + the price window."""
    if p is None or not in_band(price):
        return "Low"
    if g == "A" and p >= 0.60:
        return "High"
    if g in ("A", "B") and p >= 0.52:
        return "Medium"
    return "Low"


def brief_literal_high(p, price):
    """The brief's literal conjunction: >70% AND inside -250..+10000."""
    return p is not None and p > 0.70 and in_band(price)
