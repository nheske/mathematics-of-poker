# Chapter 11 – Half-Street Games

Chapter 11 of *The Mathematics of Poker* introduces half-street games, a family of simplified
poker situations where Player X acts first by checking, Player Y optionally bets, and X decides
whether to call. These games highlight how information and betting leverage interact in a
one-decision-point structure.

## Implemented examples

| Example | Description | Status |
|---------|-------------|--------|
| 11.1 | Clairvoyance Game (Y sees both hands) | ✅ Implemented |

Planned additions for this chapter include the `[0, 1] Game #1` and `[0, 1] Game #2` variants.

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
python examples\clairvoyance_example.py --solver mccfr --iterations 50000 --plot --plot-file ch11_clairvoyance.png
```

For the closed-form solution instead, use:

```powershell
python examples\clairvoyance_example.py --solver analytic
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

## Tests

Chapter-specific tests live under `tests/ch11/`:

- `test_clairvoyance.py` – strategy payoffs, equilibrium checks
- `test_game_tree.py` – extensive-form structure validation
- `test_half_street_solver.py` – regression tests for CFR utilities

Run all chapter tests:

```powershell
pytest tests\ch11
```

Or run the full suite:

```powershell
pytest
```

## Roadmap

- Add MCCFR solvers for `[0, 1] Game #1` and `[0, 1] Game #2`
- Share common half-street utilities (hand distributions, payoff helpers)
- Expand visualization to compare bluff/value trajectories across iterations
