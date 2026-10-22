"""T424375B4 — hand-written predictions and previews.

Every factual clause below was read from an official source during this session
(source ids attached). Selections are stated plainly. Graded predictions carry a
confidence tier; previews name a selection but are explicitly ungraded because
the inputs needed to grade them were not read.
"""

PREDICTIONS = [
    # ------------------------------------------------- HIGH (brief band) ---
    dict(id='P-42B-01', fixture_id='NHL-2026020160', tier='High',
         selection='Vegas Golden Knights to win (money line)',
         sources=['S-NHL-STAND', 'S-NHL-SCHED'],
         text=(
             "Back the Vegas Golden Knights to win in St. Louis. Vegas is 8-3-0 for "
             "sixteen points with forty-four goals scored in eleven games and a +14 "
             "goal differential, and a 7-3 mark over its last ten; the Blues sit at "
             "4-4-1 with an even goal differential and nine points. St. Louis won its "
             "last start and Vegas lost its own, so the form line is not one-way, but "
             "the season-long gap at the Enterprise Center (00:00 UTC) is: the "
             "Knights have scored almost a goal a game more than they have allowed. "
             "Our model prices Vegas at 70.0% (fair −233), inside the −250…+10000 "
             "band, and the NHL feed's own price snapshot sits shorter for Vegas.")),
    dict(id='P-42B-02', fixture_id='T14-TOU-PER', tier='High',
         selection='Toulouse to win (head-to-head)',
         sources=['S-TOP14-TABLE', 'S-TOP14-J7'],
         text=(
             "Take Stade Toulousain to beat USA Perpignan at the Ernest-Wallon. "
             "Toulouse set the Top 14 pace with 24 points, a 5-0-1 record and a +73 "
             "differential — 197 points scored in six rounds — after five consecutive "
             "victories, the latest over Bayonne. Perpignan come in ninth at 3-0-3 "
             "with 166 points scored and 199 conceded, and they have already lost on "
             "the road at Montpellier and Racing. Nothing about the official table "
             "suggests the gap narrows on Saturday afternoon: our model makes "
             "Toulouse a 70.0% favourite (fair −233), squarely inside the "
             "−250…+10000 window, and the J7 match sheet is on LNR's official site.")),

    # ------------------------------------------------- ICE HOCKEY top five --
    dict(id='P-42B-03', fixture_id='NHL-2026020159', tier='Top-5 pick (out-of-window favourite)',
         selection='New York Islanders to win (money line)',
         sources=['S-NHL-STAND', 'S-NHL-SCHED'],
         text=(
             "Take the New York Islanders at home to the Los Angeles Kings. The "
             "Islanders are 5-3-1 with a +7 goal differential and two straight wins, "
             "holding one of the Eastern Conference's tighter defensive records at "
             "twenty goals allowed in nine games. Los Angeles has one win in seven "
             "(1-4-2) and a −10 differential, although the Kings did win their most "
             "recent game, so this is not a side in freefall. Still, at UBS Arena at "
             "23:30 UTC the class gap is real: our model makes the Islanders 75.7%, "
             "though the fair price of −311 sits beyond −250, so this is disclosed "
             "as an out-of-window favourite rather than a High pick.")),
    dict(id='P-42B-04', fixture_id='NHL-2026020162', tier='Top-5 pick (out-of-window favourite)',
         selection='Minnesota Wild to win (money line)',
         sources=['S-NHL-STAND', 'S-NHL-SCHED'],
         text=(
             "Take the Minnesota Wild in Calgary. Minnesota is 6-2-2 for fourteen "
             "points with thirty-one goals in ten games and a +6 differential, and "
             "the Wild have taken points in eight of ten (6-2-2 last ten), their "
             "latest outing an overtime loss. Calgary's 2-6-0 record comes with the "
             "worst goal differential in the NHL at −20 — thirty-seven goals "
             "surrendered in eight games — even though the Flames won last time out. "
             "The model makes Minnesota 72.7% at the Saddledome (01:00 UTC); the "
             "−267 fair price is just outside the −250 line, so it is published as "
             "an out-of-window favourite with the observed NHL price snapshot "
             "(−205…−215) shown for comparison.")),
    dict(id='P-42B-05', fixture_id='NHL-2026020154', tier='Top-5 pick (out-of-window favourite)',
         selection='Boston Bruins to win (money line)',
         sources=['S-NHL-STAND', 'S-NHL-SCHED'],
         text=(
             "Take Boston at TD Garden over Nashville. The Bruins are 7-2-1 with "
             "thirty-six goals in ten games and a +14 differential, matching their "
             "7-2-1 last-ten line; Nashville is 3-2-3, has needed overtime three "
             "times and carries a −1 differential into the 23:00 UTC face-off. The "
             "Predators won their last start while Boston dropped one in overtime, "
             "so the short-term form is mixed — but the underlying season numbers "
             "run the Bruins' way. The model prices Boston at 71.6% (fair −252, "
             "just outside the window), so the pick is graded below High even "
             "though the NHL feed's own snapshot has Boston no worse than −152.")),
    dict(id='P-42B-06', fixture_id='NHL-2026020156', tier='Medium',
         selection='Ottawa Senators to win (money line)',
         sources=['S-NHL-STAND', 'S-NHL-SCHED'],
         text=(
             "Take Ottawa at home over San Jose. The Senators are 7-3-0 with "
             "twenty-nine goals scored and twenty-four allowed, winners of their "
             "last start; San Jose is 5-4-1 with a −8 differential and — the "
             "standings' own regulation-wins column shows zero — every one of the "
             "Sharks' five victories has come beyond regulation. That makes San "
             "Jose's record flatter than it looks, and at the Canadian Tire Centre "
             "(23:00 UTC) the model gives Ottawa 64.3% (fair −180), a Medium "
             "confidence selection inside the price window.")),

    # -------------------------------------------------- RUGBY UNION picks ---
    dict(id='P-42B-07', fixture_id='P2-PRO-BEZ', tier='Top-5 pick (out-of-window favourite)',
         selection='Provence to win (head-to-head)',
         sources=['S-PROD2-TABLE', 'S-PROD2-J8'],
         text=(
             "Take Provence at home against Béziers. Provence are the only unbeaten "
             "side in Pro D2 at 7-0-0, top of the table on 29 points with 222 "
             "scored and a division-best 158 conceded, and their official form line "
             "reads five straight wins. Béziers are fourteenth at 2-0-5 with 147 "
             "scored and 240 conceded, a −93 differential, and they arrive on two "
             "defeats. Friday's 21:00 local kickoff at the Stade du Pays d'Aix "
             "matches the division's clearest form gap; the model says 88.7% for "
             "Provence, and the −788 fair price is published as an out-of-window "
             "favourite rather than a High pick.")),
    dict(id='P-42B-08', fixture_id='P2-AUR-NEV', tier='Top-5 pick (out-of-window favourite)',
         selection='Aurillac to win (head-to-head)',
         sources=['S-PROD2-TABLE', 'S-PROD2-J8'],
         text=(
             "Take Aurillac to beat Nevers at home on Friday evening. Aurillac have "
             "won their last two — including at Béziers last round — to climb to "
             "ninth with 240 points scored, while Nevers are bottom on four points "
             "at 0-0-7, with 222 conceded and five straight official form entries "
             "reading defeat. The 16-versus-4 points gap is the widest of the J8 "
             "card outside the Provence game, and the model makes Aurillac 78.9% "
             "(fair −375), which is disclosed as an out-of-window favourite.")),
    dict(id='P-42B-09', fixture_id='T14-TOU-PAU', tier='Top-5 pick (out-of-window favourite)',
         selection='Pau to win (head-to-head)',
         sources=['S-TOP14-TABLE', 'S-TOP14-J7'],
         text=(
             "Take Section Paloise to win at Toulon. Pau carry the Top 14's most "
             "productive attack — 239 points in six rounds — and a 5-0-1 record "
             "second only to Toulouse, with four wins in their last five including "
             "successes over Bayonne, La Rochelle and Castres. Toulon are 2-0-4 "
             "with exactly 130 points scored and 130 conceded, and their official "
             "form shows defeats in three of the last five. Saturday's 21:00 local "
             "kickoff at the Mayol is Pau's to control: the model rates them 77.8% "
             "(fair −350), an out-of-window favourite disclosure.")),
    dict(id='P-42B-10', fixture_id='URC-BEN-GLA', tier='Top-5 pick (out-of-window favourite)',
         selection='Glasgow Warriors to win (head-to-head)',
         sources=['S-URC-TABLE', 'S-URC-R4'],
         text=(
             "Take Glasgow Warriors away to Benetton. The Warriors are unbeaten at "
             "2-1-0 with thirteen points and a league-best 95 points scored, and "
             "their most recent outing was a 36-19 win in Connacht; Benetton are "
             "fifteenth at 0-1-2 with sixty-four points in three games and a form "
             "line of draw, defeat, defeat. Saturday at Stadio Monigo (10:00 local) "
             "pits the table's sharpest attack against a side still seeking a first "
             "win, and the model makes Glasgow 76.4% (fair −324), so the pick is "
             "published as an out-of-window favourite rather than High.")),
    dict(id='P-42B-11', fixture_id='P2-NAR-BRI', tier='Top-5 pick (out-of-window favourite)',
         selection='Brive to win (head-to-head)',
         sources=['S-PROD2-TABLE', 'S-PROD2-J8'],
         text=(
             "Take Brive to win in Narbonne. Brive are 5-0-2 and unbeaten in five — "
             "their official form reads three wins followed by two draws — with the "
             "second-tightest defence in Pro D2 at 164 points conceded in seven. "
             "Narbonne have shipped 296 points, the division's worst defensive "
             "record, and sit fifteenth on nine points despite winning two of their "
             "last four. Friday's 19:00 local kickoff still tilts to the visitors: "
             "the model gives Brive 75.4% (fair −306), disclosed as an "
             "out-of-window favourite.")),

    # ------------------------------------------------- BASKETBALL picks ----
    dict(id='P-42B-12', fixture_id='EL-PAR-VAL', tier='Top-5 pick (out-of-window favourite)',
         selection='Valencia Basket to win (money line)',
         sources=['S-EL-STAND'],
         text=(
             "Take Valencia Basket to win in Paris. Valencia are 4-2 and averaging "
             "97.2 points across six EuroLeague rounds (583 scored, 537 allowed, "
             "+46), with a 2-0 mark on the road; Paris have lost five of six, "
             "conceding 90.8 points per game at home in their 1-3 home split. The "
             "official table's L10 columns read 4-2 Valencia against 1-5 Paris. "
             "Our model prices Valencia at 77.8% (fair −350), an out-of-window "
             "favourite — the start time itself is flagged because the EuroLeague "
             "game-centre row would not render for verification.")),
    dict(id='P-42B-13', fixture_id='NBA-0022600006', tier='Medium',
         selection='Philadelphia 76ers to win (money line)',
         sources=['S-NBA-CLEPHI', 'S-NBA-NEWS', 'S-NBA-SCHED-NEWS'],
         text=(
             "Take the Philadelphia 76ers at Xfinity Mobile Arena tonight. The Sixers "
             "are 1-0 and, per NBA.com, hand home debuts to LeBron James and Jaylen "
             "Brown against a Cleveland side opening its season at 0-0 with "
             "seven-time All-Star Donovan Mitchell. With a single game apiece the "
             "sample is tiny and Beta(2,2) shrinkage dominates, so the model's 60.0% "
             "(fair −150) is a Medium-confidence read at 23:00 UTC — not a High "
             "pick — but the verified debut storyline, the home floor and the "
             "official 1-0 start all point the same way.")),
    dict(id='P-42B-14', fixture_id='NBA-0022600008', tier='Low (model coin-flip)',
         selection='Boston Celtics to win (money line)',
         sources=['S-NBA-NYKBOS', 'S-NBA-KNICKS'],
         text=(
             "Lean Boston at TD Garden on Friday (23:00 UTC) in a game the model "
             "rates exactly even. The official NBA team pages show both clubs at "
             "0-1 — the Knicks lost their opener at Madison Square Garden and the "
             "Celtics theirs — so neither has a form edge to sell. The selection is "
             "the home side in their first TD Garden appearance of the season, with "
             "New York travelling on the back of a defeat; this is a Low-confidence "
             "lean at 50.0%, and anyone expecting a High pick here will not find "
             "one, because the official numbers simply do not separate the teams.")),
    dict(id='P-42B-15', fixture_id='EL-ZAL-ASV', tier='Low (model coin-flip)',
         selection='Zalgiris Kaunas to win (money line)',
         sources=['S-EL-STAND'],
         text=(
             "Lean Zalgiris at home to ASVEL in Kaunas. Both clubs are 2-4 and the "
             "official table cannot separate them on record (the model returns "
             "exactly 50.0%), but the underlying numbers do: Zalgiris concede 86.2 "
             "points a game against ASVEL's 95.3, and ASVEL's −45 differential is "
             "the weaker of the two despite scoring more. Zalgiris are 0-2 at home, "
             "so this is no fortress argument either — it is a Low-confidence lean "
             "on the defensive profile alone, with the EuroLeague start time still "
             "flagged as unverified.")),
    dict(id='P-42B-16', fixture_id='EL-OLY-FEN', tier='Low (model coin-flip)',
         selection='Olympiacos to win (money line)',
         sources=['S-EL-STAND'],
         text=(
             "Lean Olympiacos at home against Fenerbahce in Piraeus. Both sides are "
             "5-1 and the model cannot split identical records (50.0%), so this is a "
             "Low-confidence lean — but the official home/away splits can: "
             "Fenerbahce's five wins are all at the Ulker Sports Hall (5-0 home, "
             "0-1 away), while Olympiacos already banked four wins on the road. "
             "With 564 points scored in six and a 1-0 home mark, the home side gets "
             "the nod in what the table says is the round's heavyweight bout.")),

    # ------------------------------------------- UNPRICED SHOWCASE PREVIEWS --
    dict(id='P-42B-17', fixture_id='MLB-849805', tier='Unpriced preview (record gap — F-03)',
         selection='Selection withheld',
         sources=['S-MLB-SCHED', 'S-MLB-AL-EAST'],
         text=(
             "World Series Game 1 opens at American Family Field at 00:00 UTC on 24 "
             "October with Nick Martinez starting for Tampa Bay and Jacob "
             "Misiorowski for Milwaukee, per the official MLB feed, which also "
             "confirms the game is a normal fixture (ifNecessary = N). The Rays "
             "arrived here as AL East champions at 98-64 with 736 runs scored and "
             "650 allowed. No selection is published: the Brewers' official 2026 "
             "record was not readable this session, and our rules forbid pricing a "
             "winner without both records. Flag F-03 has the source link for the "
             "manual check.")),
    dict(id='P-42B-18', fixture_id='PDC-EC-R1-5', tier='Unpriced preview (selection named, not graded)',
         selection='Luke Littler to win (opinion — no model price)',
         sources=['S-PDC-PREVIEW', 'S-PDC-SCHED'],
         text=(
             "In Friday's European Championship first round the selection is Luke "
             "Littler to beat William O'Connor. The PDC's own preview calls Littler "
             "the world number one and records that he won two of the three European "
             "Tour events he entered in 2026, while O'Connor is described as "
             "Ireland's number one; the tie anchors a Friday session the PDC "
             "publishes as 1800-2200 BST. This is an opinion, not a graded pick: "
             "the PDC rankings page would not render for this session (flag F-04), "
             "so no probability is attached and anyone staking should treat it as "
             "Low confidence.")),
    dict(id='P-42B-19', fixture_id='PDC-EC-R1-7', tier='Unpriced preview (selection named, not graded)',
         selection='Michael van Gerwen to win (opinion — no model price)',
         sources=['S-PDC-PREVIEW', 'S-PDC-SCHED'],
         text=(
             "The selection is Michael van Gerwen to see off fellow Dutchman Kevin "
             "Doets in Friday's first round. The PDC preview identifies van Gerwen "
             "as a four-time European Championship champion and calls this pairing "
             "one of the standout ties of the session; Doets' own 2026 form was not "
             "read from an official rankings surface this session. The pick is "
             "therefore named but ungraded — no probability, no confidence tier — "
             "and it lands on Friday evening in Dortmund inside the 1800-2200 BST "
             "window the PDC publishes.")),
    dict(id='P-42B-20', fixture_id='PDC-EC-R1-4', tier='Unpriced preview (selection named, not graded)',
         selection='Jonny Clayton to win (opinion — no model price)',
         sources=['S-PDC-PREVIEW', 'S-PDC-SCHED'],
         text=(
             "The selection is Jonny Clayton against Niko Springer in the European "
             "Championship first round. The PDC's official preview records Clayton "
             "as a former World Grand Prix winner and places the tie in Friday's "
             "Round One block; Springer's current ranking was not read from an "
             "official surface, so this preview names the pick without grading it. "
             "Treat the selection as Low confidence opinion rather than a modelled "
             "price, consistent with the darts gap logged at flag F-04.")),
    dict(id='P-42B-21', fixture_id='F1-USA-2026', tier='Unpriced preview (field model withheld)',
         selection='Selection withheld',
         sources=['S-F1-USA'],
         text=(
             "Formula 1's MSC Cruises United States Grand Prix takes the flag at "
             "Circuit of The Americas at 16:00 track time on 25 October, with "
             "qualifying the previous evening at 17:00 and 56 laps of a 5.513km "
             "circuit ahead (308.432km race distance, official F1 page). OLBG's "
             "tipsters split 35% to Max Verstappen, but that share is a vote, not a "
             "price. No selection is published: the official championship standings "
             "and a complete verified entry list were not read this session, and a "
             "multi-runner winner market needs both before it can be priced.")),
]

# Per-sport shortfall notes for the coverage table.
SHORTFALLS = {
    'tennis': ('13 upcoming match-ups unverified (F-09/F-10); ATP R16 results were '
               'read and are used as context only. No predictions can be written '
               'without confirmed pairings.'),
    'darts': ('8 Round One ties officially listed (class B) but no rankings body '
              'read (F-04): three previews name selections, none is graded.'),
    'cricket': ('4 listings; no official board read (F-11) — no predictions.'),
    'handball': ('15 listings; no official body read (F-12) — no predictions.'),
    'volleyball': ('14 listings; no official body read (F-12) — no predictions.'),
    'ice-hockey': ('4 European-club listings unverified (F-12) on top of 12 NHL '
                   'games; NHL top five carry graded predictions.'),
    'basketball': ('3 Brazil NBB listings unverified (F-12); 3 NBA rows lack '
                   'records (F-06/F-07); the 5 priced games all carry predictions.'),
    'gaelic-football': '5 club listings unverified (F-12) — no predictions.',
    'golf': '1 outright listing; PGA Tour Champions page not read (F-12) — no prediction.',
    'rugby-league': ('Only 2027 anteposts on the hub; no matches inside the window '
                     '(F-12) — no predictions.'),
    'motor-racing': 'Race preview written; multi-runner winner withheld (see P-42B-21).',
    'baseball': 'World Series G1 preview written; price withheld on the Brewers record gap (F-03).',
    'rugby-union': '23 fixtures priced from official tables; top six carry graded predictions.',
}
