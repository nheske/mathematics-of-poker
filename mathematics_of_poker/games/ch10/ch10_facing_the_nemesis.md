# Chapter 10 – Facing the Nemesis

Chapter 10 introduces *Facing the Nemesis*: a setting where each player knows the
opponent will exploit any predictable leak. Before tackling richer poker trees, it is
useful to sanity-check our MCCFR infrastructure on the tiniest simultaneous game we can
write down.

![Chapter 10 Facing The Nemesis infographic](../../../assets/infographics/ch10_square_detail.png)

## Odds and Evens (Example 10.1)

- **Rules:** Each player secretly chooses to reveal a penny (`penny`) or an empty hand
  (`none`). Reveals happen simultaneously. Player Y ("evens") wins one chip when the total
  number of pennies is even; Player X ("odds") wins when it is odd.
- **Payoff matrix:**

|             | X: none | X: penny |
|-------------|:-------:|:--------:|
| **Y: none** |   -1    |    +1    |
| **Y: penny**|   +1    |    -1    |

Values are shown from Player X's perspective (positive numbers favour odds).

- **Analytic Nash equilibrium:** Both players mix `penny` with probability 0.5, producing
  a game value of zero for each player.

## Implementation Notes

- Class: `mathematics_of_poker.games.ch10.OddsAndEvensGame`
- Tree construction reuses the `GameTree`, `InformationSet`, and `MonteCarloCFR` helpers
  from previous chapters. We model the simultaneous move by giving Player X two decision
  nodes that share the same information set, so the solver treats them as indistinguishable.
- Analytic helper: `OddsAndEvensGame.analytic_solution()` reports the closed-form mix and
  values, while `solve_mccfr_equilibrium()` runs MCCFR on the two-node tree to recover a
  numerical approximation.

## Example Run

```bash
python examples/odds_and_evens.py --iterations 200000 --seed 23
```

Sample output:

```text
ODDS AND EVENS (Chapter 10)
===========================
Payoff per win: 1.00

ANALYTIC EQUILIBRIUM
=====================
Y (evens) mix on penny: 0.500
X (odds) mix on penny:  0.500
Game value to Y:        0.000
Game value to X:        0.000

MCCFR DIAGNOSTICS
==================
Iterations:             200000
Estimated EV (Player X): -0.0000
Y strategy:             none=0.500, penny=0.500
X strategy:             none=0.498, penny=0.502

Done.
```

Even this 2x2 matrix game benefits from the shared infrastructure: we can swap in new
payoffs, run MCCFR, and inspect the learned strategies without writing solver logic from
scratch. The next step is to escalate the complexity (e.g., half-street games or PLO
subgames) while relying on the same primitives.
