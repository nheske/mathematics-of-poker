python examples\clairvoyance_example.py --solver cfr --iterations 50000 --seed 42

THE MATHEMATICS OF POKER - EXAMPLE 11.1
The Clairvoyance Game
============================================================

Game Setup:
- Initial pot size: 1.0
- Bet size: 1.0
- Y is clairvoyant (knows both hands)
- Y's hand beats X's hand 50% of the time
- X checks in the dark
- Y can check or bet
- If Y bets, X can call or fold

Payoff Matrix for Player X:
Strategies: ['Always Fold', 'Always Call']
Y Strategies: ['Check Always', 'Bet Nuts Only', 'Bluff Only', 'Bet Always']
[[ 0.   0.  -1.  -1. ]
 [ 0.  -0.5  0.5  0. ]]

Payoff Matrix for Player Y:
[[-0.  -0.   1.   1. ]
 [-0.   0.5 -0.5 -0. ]]

Solving for Nash Equilibrium (CFR)...
Iterations: 50000
Seed: 42
OPTIMAL STRATEGIES
==================================================
Game Value: 0.3333

Player X (First Player) Strategy:
  Always Fold: 0.3350 (33.5%)
  Always Call: 0.6650 (66.5%)

Player Y (Second Player) Strategy:
  Bet Nuts Only: 0.6674 (66.7%)
  Bet Always: 0.3326 (33.3%)

STRATEGY INTERPRETATION
========================================
X calls when Y bets: 0.6650 (66.5%)
Y bets with winning hands: 1.0000 (100.0%)
Y bets with losing hands (bluffs): 0.3326 (33.3%)

Expected outcomes when Y has a winning hand:
  Checks and wins at showdown: 0.0%
  Bets, X folds: 33.5%
  Bets, X calls and loses: 66.5%

Expected outcomes when Y has a losing hand:
  Checks and loses at showdown: 66.7%
  Bluffs, X folds: 11.1%
  Bluffs, X calls and wins: 22.1%

CFR highlights:
- Average call probability: 0.665007
- Average bluff fraction: 0.332644
- Average game value (X): 0.333328

Approximate equilibrium verification: PASSED

GAME THEORY INSIGHTS
==============================
This game demonstrates several key concepts:
1. The value of information - Y's clairvoyance gives them an advantage
2. Mixed strategies arise naturally in adversarial settings
3. Bluffing frequency must be balanced with value betting
4. Calling frequency must balance between being exploited by bluffs vs value bets

SENSITIVITY ANALYSIS
=========================
How do optimal strategies change with different bet sizes?

================================================

python examples\clairvoyance_example.py --solver mccfr --iterations 50000 --seed 42

THE MATHEMATICS OF POKER - EXAMPLE 11.1
The Clairvoyance Game
============================================================

Game Setup:
- Initial pot size: 1.0
- Bet size: 1.0
- Y is clairvoyant (knows both hands)
- Y's hand beats X's hand 50% of the time
- X checks in the dark
- Y can check or bet
- If Y bets, X can call or fold

Payoff Matrix for Player X:
Strategies: ['Always Fold', 'Always Call']
Y Strategies: ['Check Always', 'Bet Nuts Only', 'Bluff Only', 'Bet Always']
[[ 0.   0.  -1.  -1. ]
 [ 0.  -0.5  0.5  0. ]]

Payoff Matrix for Player Y:
[[-0.  -0.   1.   1. ]
 [-0.   0.5 -0.5 -0. ]]

Solving for Nash Equilibrium (Monte Carlo CFR)...
Iterations: 50000
Seed: 42
OPTIMAL STRATEGIES
==================================================
Game Value: -0.3333

Player X (First Player) Strategy:
  Always Fold: 0.3335 (33.4%)
  Always Call: 0.6665 (66.6%)

Player Y (Second Player) Strategy:
  Bet Nuts Only: 0.6354 (63.5%)
  Bet Always: 0.3645 (36.5%)

STRATEGY INTERPRETATION
========================================
X calls when Y bets: 0.6665 (66.6%)
Y bets with winning hands: 1.0000 (100.0%)
Y bets with losing hands (bluffs): 0.3645 (36.5%)

Expected outcomes when Y has a winning hand:
  Checks and wins at showdown: 0.0%
  Bets, X folds: 33.4%
  Bets, X calls and loses: 66.6%

Expected outcomes when Y has a losing hand:
  Checks and loses at showdown: 63.5%
  Bluffs, X folds: 12.2%
  Bluffs, X calls and wins: 24.3%

Monte Carlo CFR highlights:
- Average call probability: 0.666467
- Average value-bet frequency: 0.999960
- Average bluff fraction: 0.364540
- Estimated game value (X): -0.333329

Info-set strategies:
  Y:nuts: check=0.0000, bet=1.0000
  Y:bluff: check=0.6355, bet=0.3645
  X:bet_response: fold=0.3335, call=0.6665

Approximate equilibrium verification: PASSED

GAME THEORY INSIGHTS
==============================
This game demonstrates several key concepts:
1. The value of information - Y's clairvoyance gives them an advantage
2. Mixed strategies arise naturally in adversarial settings
3. Bluffing frequency must be balanced with value betting
4. Calling frequency must balance between being exploited by bluffs vs value bets

SENSITIVITY ANALYSIS
=========================
How do optimal strategies change with different bet sizes?

Bet size: 0.5
  X calling frequency: 0.800
  Y value betting frequency: 1.000
  Y bluffing frequency: 0.256
  Game value: -0.2000