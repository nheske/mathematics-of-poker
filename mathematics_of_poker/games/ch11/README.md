# This documentation has moved

Please see `ch11_half_street_games.md` for the current Chapter 11 write-up.
This no-fold half-street game deals each player a real number in ``[0,1]`` (lower wins).
Player Y chooses whether to bet knowing Player X must call. Without the option to fold,
the pot size is irrelevant and the decision reduces to a threshold strategy.

- **Analytic structure**: Y bets every hand below the threshold ``y = 0.5`` and checks the rest,
	yielding an expected value of ``-0.25`` bets for Player X (``+0.25`` for Player Y).
- **CFR tooling**: the implementation buckets the continuum into discrete intervals and runs
	external-sampling MCCFR to recover the betting region while exposing bucket-level regrets.

```python
from mathematics_of_poker.games.ch11.zero_one_game_1 import ZeroOneGame1

game = ZeroOneGame1(num_buckets=20)
analytic = game.analytic_solution()
mccfr = game.solve_mccfr_equilibrium(iterations=100_000, seed=2025)
```

Use ``simulate_expected_value`` for an optional Monte Carlo sanity check of the analytic value:

```python
from mathematics_of_poker.games.ch11.zero_one_game_1 import simulate_expected_value

estimate = simulate_expected_value(game, samples=100_000)
```

### Running the example script

```powershell
python examples\zero_one_game_1.py --buckets 40 --iterations 120000 --plot --plot-file plots\ch11_zero_one.png
```

Sample run (buckets=40, iterations=120000):

```
ANALYTIC SOLUTION
===================
Threshold (Y bets below this hand strength): 0.5000
Player X expected value: -0.2500
Player Y expected value: 0.2500

MONTE CARLO CHECK
==================
Estimated EV for Player X: -0.2478
Analytic EV:               -0.2500
Absolute error:            0.0022
```

## [0,1] Game #2 (Example 11.3)

This extension allows Player X to fold facing a bet, so the initial pot size ``P`` now
changes incentives. Player Y chooses between value bets below threshold ``a`` and bluffs
above threshold ``b``, while Player X calls up to threshold ``c = 2a``.

- **Analytic solution**: Closed-form thresholds
	- ``a = \frac{P (2P + 1)}{(P + 1)(6P + 1)}``
	- ``b = \frac{(2P + 1)^2}{(P + 1)(6P + 1)}``
	- ``c = 2a``
- **EV check**: `simulate_expected_value` Monte Carlo helper validates the closed form.
- **MCCFR solver**: Discretises hands into buckets and recovers betting/calling regions via external-sampling MCCFR.

```python
from mathematics_of_poker.games.ch11.zero_one_game_2 import ZeroOneGame2

game = ZeroOneGame2(pot_size=1.0, num_buckets=40)
analytic = game.analytic_solution()
mccfr = game.solve_mccfr_equilibrium(iterations=250_000, seed=11)
```

Optional Monte Carlo validation:

```python
from mathematics_of_poker.games.ch11.zero_one_game_2 import simulate_expected_value

estimate = simulate_expected_value(game, samples=200_000, seed=7)
```

### Running the example script

```powershell
python examples\zero_one_game_2.py --pot 1.0 --buckets 40 --iterations 250000 --simulate 50000 --plot --plot-file plots\ch11_zero_one2.png
```

Sample run (pot=1, buckets=40, iterations=250000):

```
Analytic solution thresholds:
	Value Threshold: 0.214286
	Call Threshold: 0.428571
	Bluff Threshold: 0.642857
	Expected value for X: -0.173469
	Expected value for Y: 0.173469
Monte Carlo EV estimate for X (samples=50000): -0.176400

Running MCCFR ...
	Estimated game value (X): -0.098082
	Estimated thresholds (value / bluff / call): 0.287 0.887 0.362
	Analytic thresholds: 0.214 / 0.643 / 0.429
```

Key flags:

- `--simulate N` runs a Monte Carlo EV sanity check with `N` samples.
- `--plot` enables interactive charts for Player Y's betting and Player X's calling buckets (requires a GUI backend).
- `--plot-file PATH` writes the same chart to disk—combine with `--plot` for both, or use alone on a headless machine.

The saved figure visualises Y's bet probability per bucket (plus regret per iteration) on the top axis and X's call probability on the bottom axis, mirroring the diagnostics available for Example 11.2.

## Tests

Chapter-specific tests live under `tests/ch11/`:

- `test_clairvoyance.py` – strategy payoffs, equilibrium checks
- `test_game_tree.py` – extensive-form structure validation
- `test_half_street_solver.py` – regression tests for CFR utilities
- `test_zero_one_game_1.py` – analytic and MCCFR checks for the [0,1] game
- `test_zero_one_game_2.py` – analytic thresholds and EV checks for the folding variant

Run all chapter tests:

```powershell
pytest tests\ch11
```

Or run the full suite:

```powershell
pytest
```

## Roadmap
- Share common half-street utilities (hand distributions, payoff helpers)
- Expand visualization to compare bluff/value trajectories across iterations
