#!/usr/bin/env python3
"""Uncalibrated, source-gated research estimates. No invented ratings or quotes.

All outputs of this version are Low. A probability threshold or an alternate
line chosen to land near 71% is NOT evidence of predictive confidence.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import math

VERSION = "455acb16-research-v2"
FIXTURE_TTL = timedelta(hours=6)
STAT_TTL = timedelta(hours=24)
HORIZON = timedelta(days=7)
MARKET_REQUIREMENTS = {
    "winner": "Exact future UTC start, explicit pre-match state, two compatible official performance records and appropriate settlement.",
    "handicap": "Official score distributions for both participants, meaningful units, line and push/overtime/retirement rules.",
    "total": "Paired official scoring histories and an appropriate sport/format distribution with settlement and tail treatment.",
    "team-total": "Team scoring histories, opposition adjustments and explicit period/settlement scope.",
    "period": "Period, half, set, frame or innings logs and a period-specific calculation.",
    "correct-score": "Joint score distribution respecting match length, ties, retirements and an explicit tail.",
    "player-prop": "Player identity, current availability and official individual game logs; prop and settlement definition.",
    "outright": "Complete current field, withdrawals and normalized multi-runner strength estimates.",
    "placement": "Full field and finishing distribution; places, each-way, tie/dead-heat and withdrawal rules.",
}
SPORT_MARKETS = {
    "golf": ["winner","handicap","total","outright","placement","period"],
    "volleyball": ["winner","handicap","total","team-total","period","correct-score"],
    "rugby-union": ["winner","handicap","total","team-total","period","player-prop"],
    "cricket": ["winner","handicap","total","team-total","period","player-prop"],
    "snooker": ["winner","handicap","total","period","correct-score","player-prop"],
    "darts": ["winner","handicap","total","period","correct-score","player-prop"],
    "baseball": ["winner","handicap","total","team-total","period","player-prop"],
    "gaelic-sports": ["winner","handicap","total","team-total","period","player-prop"],
    "greyhounds": ["winner","handicap","total","outright","placement","correct-score"],
    "tennis": ["winner","handicap","total","period","correct-score","player-prop"],
    "motor-racing": ["winner","handicap","total","outright","placement","player-prop"],
    "handball": ["winner","handicap","total","team-total","period","player-prop"],
    "ice-hockey": ["winner","handicap","total","team-total","period","player-prop"],
    "basketball": ["winner","handicap","total","team-total","period","player-prop"],
    "rugby-league": ["winner","handicap","total","team-total","period","player-prop"],
}
ASSUMPTIONS = {
    "record": "Beta(2,2) posterior means followed by log5; W/(W+L+OTL), not points percentage. No home edge or missing-rating fallback.",
    "baseball": "Independent Poisson scores from paired 2026 regular-season runs/game and runs-allowed/game, conditional on unequal scores. No starter, lineup, park, weather, bullpen or postseason adjustment. A research approximation, not a sportsbook offer.",
    "lines": "MLB fixed A ±1.5 run lines; three half-run totals centered on floor(expected total)+0.5, selected mechanically without optimizing a confidence tier.",
    "confidence": "All originated estimates Low until held-out calibration and current player/form/history/quote/OLBG-eligibility evidence support a versioned higher tier. No generic-strength, seed-gap or tuned-variance shortcuts.",
}


def parse_time(value):
    d=datetime.fromisoformat(value.replace("Z","+00:00"))
    if d.tzinfo is None:
        raise ValueError("Explicit UTC offset required")
    return d.astimezone(timezone.utc)


def iso(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")


def american(p):
    if type(p) not in (int,float) or not math.isfinite(p) or not 0 < p < 1:
        raise ValueError("Probability must be finite and strictly between zero and one")
    q=Decimal(str(p))
    raw=(1-q)/q*100 if q <= Decimal("0.5") else -100*q/(1-q)
    return int(raw.quantize(Decimal("1"),rounding=ROUND_HALF_UP))


def in_band(p):
    american(p)  # same strict validation
    return 1/101 <= p <= 5/7


def price(p):
    a=american(p)
    return {"probability":p,"fair_decimal":1/p,"fair_american":a,
            "in_band":in_band(p),"confidence":"low","market_quote":None,
            "olbg_eligibility":None,"status":"experimental"}


def confidence_for(p, *args, **kwargs):
    # Deliberately cannot be promoted by supplying an unsigned 'calibrated=True'.
    price(p)
    return "low"


def fixture_state(f,at):
    before=parse_time(f["observed_before"])
    after=parse_time(f["observed_after"])
    if before > at or after > before:
        return "not-yet-observed"
    if at >= after+FIXTURE_TTL:
        return "stale"
    status=f.get("official_status")
    if status in {"Final","Full Time","LIVE","OFF"}:
        return "elapsed / in play"
    if f.get("start_utc"):
        t=parse_time(f["start_utc"])
        if t <= at:
            return "start elapsed"
        if t >= at+HORIZON:
            return "outside window"
        if f.get("if_necessary")=="Y":
            return "conditional"
        return "upcoming" if status in {"FUT","PRE","Pre-Game","Scheduled"} else "status unverified"
    if f.get("kind")=="field-event":
        return "field calendar / time unverified"
    return "calendar / time unverified"


def record_ok(r,at):
    if not r:
        return False
    for k in ("wins","losses","games_played"):
        if type(r.get(k)) is not int or r[k] < 0:
            return False
    if r.get("competition")=="NHL":
        ot=r.get("ot_losses")
        if type(ot) is not int or ot<0:
            return False
    elif r.get("competition")=="MLB":
        # NHL's OTL category does not exist in this MLB record. Zero here is
        # arithmetic only, never stored/displayed as an official MLB statistic.
        if r.get("ot_losses") is not None:
            return False
        ot=0
    else:
        return False
    if r["wins"]+r["losses"]+ot != r["games_played"] or r["games_played"]<5:
        return False
    if "points" in r and r["points"] != 2*r["wins"]+ot:
        return False
    try:
        a,b=parse_time(r["observed_after"]),parse_time(r["observed_before"])
    except (KeyError,ValueError,TypeError):
        return False
    return a<=b<=at and at<a+STAT_TTL


def log5(a,b):
    pa=(a["wins"]+2)/(a["games_played"]+4)
    pb=(b["wins"]+2)/(b["games_played"]+4)
    return pa*(1-pb)/(pa*(1-pb)+pb*(1-pa))


def poisson(rate,maximum=60):
    if not math.isfinite(rate) or not 0<rate<20:
        raise ValueError("Score rate outside tested domain")
    values=[math.exp(-rate)]
    for n in range(1,maximum+1):
        values.append(values[-1]*rate/n)
    if 1-math.fsum(values)>1e-10:
        raise ValueError("Score tail not accounted for")
    return values


def baseball_grid(a,b):
    for r in (a,b):
        if r["games_played"]<30 or any(type(r.get(k)) is not int or r[k]<=0 for k in ("runs_scored","runs_allowed")):
            raise ValueError("Both official run aggregates and at least 30 games required")
    la=(a["runs_scored"]/a["games_played"]+b["runs_allowed"]/b["games_played"])/2
    lb=(b["runs_scored"]/b["games_played"]+a["runs_allowed"]/a["games_played"])/2
    va,vb=poisson(la),poisson(lb)
    grid=[(i,j,x*y) for i,x in enumerate(va) for j,y in enumerate(vb) if i!=j]
    mass=math.fsum(z for _,_,z in grid)
    return [(i,j,z/mass) for i,j,z in grid],(la,lb),mass


def originate(f,statistics,at):
    book={"fixture_id":f["id"],"version":VERSION,"markets":[],"selection":None,
          "probability":None,"confidence":None,"expires_at":None,"input_ids":[],
          "market_quote":None,"olbg_eligibility":None,"notes":[],"investigated":[]}
    state=fixture_state(f,at)
    reason=None
    if state!="upcoming":
        reason="No price: "+state+"; exact future start and explicit pre-match status required."
    elif f["sport"]=="baseball" and f.get("if_necessary")!="N":
        reason="No price: MLB must explicitly say ifNecessary=N."
    elif f["sport"] not in {"ice-hockey","baseball"}:
        reason="No compatible two-sided official performance series or tested sport-specific implementation."
    else:
        records=[]
        for identity in (f.get("participant_a_id"),f.get("participant_b_id")):
            options=[s for s in statistics if identity is not None and s.get("team_id")==identity
                     and s.get("competition")==f.get("competition") and s.get("season")==f.get("season") and record_ok(s,at)]
            records.append(sorted(options,key=lambda r:r["observed_after"],reverse=True)[0] if options else None)
        a,b=records
        if not a or not b:
            reason="No price: missing, expired, inconsistent or insufficient official record on one side."
        elif a["as_of"]!=b["as_of"] or a["period"]!=b["period"]:
            reason="No price: statistical periods do not match."
        else:
            deadline=min(parse_time(f["observed_after"])+FIXTURE_TTL,parse_time(f["start_utc"]),
                         *(parse_time(r["observed_after"])+STAT_TTL for r in records))
            book.update(expires_at=iso(deadline),input_ids=[a["id"],b["id"]])
            source_ids=list(dict.fromkeys(f["source_ids"]+[a["source_id"],b["source_id"]]))
            pa,pb=f["participant_a"],f["participant_b"]
            def market(key,labels,p,settlement,line=None):
                return {"id":f["id"]+"-"+key,"family":key.split(":")[0],"line":line,
                        "source_ids":source_ids,"settlement":settlement,"expires_at":book["expires_at"],
                        "outcomes":[{"selection":labels[0],**price(p)},{"selection":labels[1],**price(1-p)}]}
            if f["sport"]=="baseball":
                try:
                    grid,rates,mass=baseball_grid(a,b)
                    p=math.fsum(z for i,j,z in grid if i>j)
                    settlement="Full-game research approximation conditional on unequal final scores; not a sportsbook offer."
                    book["markets"].append(market("winner",[pa,pb],p,settlement))
                    for line in (-1.5,1.5):
                        pc=math.fsum(z for i,j,z in grid if i+line>j)
                        book["markets"].append(market(f"handicap:{line}",[f"{pa} {line:+g} runs",f"{pb} {-line:+g} runs"],pc,settlement,line))
                    center=math.floor(sum(rates))+0.5
                    for line in (center-1,center,center+1):
                        over=math.fsum(z for i,j,z in grid if i+j>line)
                        book["markets"].append(market(f"total:{line}",[f"Over {line:g} runs",f"Under {line:g} runs"],over,settlement,line))
                    book["notes"]=[ASSUMPTIONS["baseball"],ASSUMPTIONS["lines"]]
                    book["expected_runs"]=list(rates)
                    book["non_tie_mass"]=mass
                except ValueError as e:
                    reason="No score price: "+str(e)
            else:
                p=log5(a,b)
                book["markets"].append(market("winner",[pa,pb],p,"Full match including overtime and shootout; not regulation 3-way."))
                book["notes"]=[ASSUMPTIONS["record"]]
            if book["markets"]:
                win=book["markets"][0]
                pref=max(win["outcomes"],key=lambda r:r["probability"])
                if abs(pref["probability"]-.5)>1e-12:
                    book.update(selection=pref["selection"],probability=pref["probability"],confidence="low")
                book["notes"].append(ASSUMPTIONS["confidence"])
    priced={m["family"] for m in book["markets"]}
    for family in SPORT_MARKETS[f["sport"]]:
        available=family in priced
        book["investigated"].append({"family":family,"status":"experimental" if available else "withheld",
            "reason":("Own research line; actual quote/OLBG placement availability unverified." if available else reason or MARKET_REQUIREMENTS[family]),
            "source_ids":f["source_ids"],"market_quote":None})
    if reason:
        book["notes"].append(reason)
    return book
