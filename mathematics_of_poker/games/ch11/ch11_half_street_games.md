# Chapter 11 – Half-Street Games

Chapter 11 of *The Mathematics of Poker* introduces half-street games, a family of simplified
poker situations where Player X acts first by checking, Player Y optionally bets, and X decides
whether to call. These games highlight how information and betting leverage interact in a
one-decision-point structure.

![Chapter 11 half-street games infographic](../../../assets/infographics/ch11_square_detail.png)

## Implemented examples

| Example | Description | Status |
|---------|-------------|--------|
| 11.1 | Clairvoyance Game (Y sees both hands) | ✅ Implemented |
| 11.2 | [0,1] Game #1 (no-fold half street) | ✅ Implemented |
| 11.3 | [0,1] Game #2 (fold allowed) | ✅ Implemented |

Planned additions for this chapter include further threshold-based half-street variants.

> **Tip:** Generated plots from the example scripts are routed to a `plots/` directory in these
> snippets. The repository ignores that folder by default, keeping diagnostic PNG files out of
> version control. Create it once (`mkdir plots`) and point `--plot-file` there for all runs.

## Clairvoyance Game (Example 11.1)

The Clairvoyance Game models a value/bluff decision for Player Y, who has perfect information
about hand strength. Our implementation provides:

- **Closed-form solver** (`solve_nash_equilibrium`) using linear programming
	- Solves the zero-sum game exactly via the classic Minimax LP formulation. Returns the Nash strategy profile in one pass—ideal for ground-truth checks on small games.
- **Normal-form CFR** (`solve_cfr_equilibrium`) for deterministic convergence checks
	- Runs regret matching on the normal-form payoff matrix. Deterministic per iteration and converges toward the same equilibrium as the analytic solver while exercising CFR logic.
- **External-sampling MCCFR** (`solve_mccfr_equilibrium`) with regret diagnostics and visualization
	- Traverses the extensive-form tree with Monte Carlo sampling, producing average strategies plus per–information set regret data that we can chart for deeper diagnostics.

### Running the example script

From the repository root:

```powershell
python examples\clairvoyance_example.py --solver mccfr --iterations 50000 --plot --plot-file plots\ch11_clairvoyance.png
```

For the closed-form solution instead, use:

```powershell
python examples\clairvoyance_example.py --solver analytic
```

Typical analytic output (P = B = 1):

```
Game value (X): -0.333333
X call probability: 0.666667
Y bluff frequency: 0.333333
```

Key flags:

- `--solver {analytic|cfr|mccfr}` selects the algorithm
- `--iterations` controls CFR / MCCFR run length
- `--plot` enables interactive charts (requires a GUI backend)
- `--plot-file` saves the MCCFR strategy/regret bar charts for headless environments

### Module usage

```python
from mathematics_of_poker.games.ch11.clairvoyance import ClairvoyanceGame

game = ClairvoyanceGame(pot_size=1.0, bet_size=1.0)
solution = game.solve_mccfr_equilibrium(iterations=50000, seed=42)
print(solution["info_set_strategies"])
```

## [0,1] Game #1 (Example 11.2)

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
Estimated EV for Player X: -0.2502
Analytic EV:               -0.2500
Absolute error:            0.0002

MCCFR DIAGNOSTICS
==================
Iterations:        120000
Buckets:           40
Estimated thresh.: 0.4625
Analytic thresh.:  0.5000
Game value (X):    -0.2470

Sample bucket strategies (bet probability shown):
	Y:bucket[0]: bet=1.000, check=0.000
	Y:bucket[20]: bet=0.002, check=0.998
	Y:bucket[39]: bet=0.000, check=1.000

Bluffing takeaway:
	MCCFR confirms Y's optimal play is a pure value bet region—betting dries up above the threshold, so bluffing provides no gain in this structure.
	Avg bet prob. below threshold buckets:  0.929
	Avg bet prob. above threshold buckets: 0.004
```

The driver now spells out that the MCCFR strategy quickly converges to “value only” betting—average bluff frequencies above the equilibrium threshold are effectively zero, so bluffing just burns chips in this half-street format.

## [0,1] Game #2 (Example 11.3)

This extension allows Player X to fold facing a bet, so the initial pot size ``P`` now
changes incentives. Player Y chooses between value bets below threshold ``a`` and bluffs
above threshold ``b``, while Player X calls up to threshold ``c = 2a``.

- **Analytic solution**: Closed-form thresholds
	- ``a = \frac{P (2P + 1)}{(P + 1)(6P + 1)}``
	- ``b = \frac{(2P + 1)^2}{(P + 1)(6P + 1)}``
	- ``c = 2a``
- **EV check**: `simulate_expected_value` Monte Carlo helper validates the closed form.
- **MCCFR solver**: Discretizes hands into buckets and recovers betting/calling regions via external-sampling MCCFR.

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
Monte Carlo EV estimate for X (samples=50000): -0.172740

Running MCCFR ...
	Estimated game value (X): -0.097663
	Estimated thresholds (value / bluff / call): 0.263 0.912 0.562
	Analytic thresholds: 0.214 / 0.643 / 0.429

	Bluffing takeaway:
		MCCFR preserves a live bluff band above the threshold; Y still fires selectively to balance X's calling region.
		Avg bet prob. (value buckets): 0.998
		Avg bet prob. (check buckets): 0.167
		Avg bet prob. (bluff buckets): 0.271
```

Key flags:

- `--simulate N` runs a Monte Carlo EV sanity check with `N` samples.
- `--plot` enables interactive charts for Player Y's betting and Player X's calling buckets (requires a GUI backend).
- `--plot-file PATH` writes the same chart to disk—combine with `--plot` for both, or use alone on a headless machine.

The saved figure visualises Y's bet probability per bucket (plus regret per iteration) on the top axis and X's call probability on the bottom axis, mirroring the diagnostics available for Example 11.2.

Because X can fold, the optimal half-street solution keeps a non-zero bluff band. The MCCFR summary above makes that explicit by averaging bet frequencies in the value, check, and bluff regions—use it to sanity check that your discretization still carries enough bluffing pressure.

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
