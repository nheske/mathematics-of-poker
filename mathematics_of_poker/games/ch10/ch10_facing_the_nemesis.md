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

## Roshambo (Example 10.2)

- **Rules:** Classic rock-paper-scissors with the standard win/loss relationships; victories
  are worth one chip, losses cost one chip, and ties break even.
- **Analytic Nash equilibrium:** Both players mix each action with probability 1/3, yielding
  zero expected value.
- **Implementation:** `mathematics_of_poker.games.ch10.RoshamboGame` mirrors the Odds and
  Evens structure with three actions per player. MCCFR recovers the uniform mix quickly.

### Roshambo Example Run

```bash
python examples/roshambo.py --iterations 200000 --seed 23
```

Sample output:

```text
ROSHAMBO (Chapter 10)
====================
Payoff per win: 1.00

ANALYTIC EQUILIBRIUM
=====================
Y mix: rock=0.333, paper=0.333, scissors=0.333
X mix: rock=0.333, paper=0.333, scissors=0.333
Game value to Y: 0.000
Game value to X: 0.000

MCCFR DIAGNOSTICS
==================
Iterations:              200000
Estimated EV (Player X): -0.0000
Y strategy:             rock=0.340, paper=0.328, scissors=0.332
X strategy:             rock=0.331, paper=0.334, scissors=0.336

Done.
```

Rock-paper-scissors is still a tiny matrix game, but it demonstrates that the same data
structures scale seamlessly from two to three actions while MCCFR converges toward the
uniform equilibrium.

## Roshambo-S (Example 10.3)

- **Rules:** Same move set as Roshambo, but any player who wins *with scissors* receives a
  double payout. Normal rock and paper victories remain worth one chip.
- **Analytic Nash equilibrium:** The bonus skews the mix toward rock. Both players play rock
  50% of the time, paper 25%, and scissors 25%, keeping the game value at zero.
- **Implementation:** `mathematics_of_poker.games.ch10.RoshamboSGame` generalises the payoff
  table so the scissors bonus can be configured. The analytic helper solves the equilibrium
  for any positive bonus multiple, and MCCFR validates the mix numerically.

### Roshambo-S Example Run

```bash
python examples/roshambo_s.py --iterations 200000 --seed 23
```

Sample output:

```text
ROSHAMBO-S (Chapter 10)
======================
Payoff per non-scissor win: 1.00
Payoff per scissor win:     2.00

ANALYTIC EQUILIBRIUM
=====================
Y mix: rock=0.500, paper=0.250, scissors=0.250
X mix: rock=0.500, paper=0.250, scissors=0.250
Game value to Y: 0.000
Game value to X: 0.000

MCCFR DIAGNOSTICS
==================
Iterations:              200000
Estimated EV (Player X): -0.0001
Y strategy:             rock=0.450, paper=0.270, scissors=0.280
X strategy:             rock=0.500, paper=0.250, scissors=0.250

Done.
```

Roshambo-S highlights how even small payoff perturbations reshape optimal strategies, yet the
same MCCFR scaffolding keeps pace—simply adjust the payoff helper and rerun the solver.

## Roshambo-F (Example 10.4)

- **Rules:** Adds a fourth action, *flower*, that ties with paper/flower and loses to rock and
  scissors. Flower is strictly dominated by paper, so optimal play should assign it zero weight.
- **Analytic Nash equilibrium:** Identical to base Roshambo once the dominated action is
  removed: rock/paper/scissors each receive 1/3 frequency; flower gets 0.
- **Implementation:** `mathematics_of_poker.games.ch10.RoshamboFGame` extends the action set
  and payoff matrix, but the analytic helper still collapses to the classic 1/3 mix. MCCFR
  converges to the same outcome, leaving flower unused.

### Roshambo-F Example Run

```bash
python examples/roshambo_f.py --iterations 200000 --seed 23
```

Sample output:

```text
ROSHAMBO-F (Chapter 10)
======================
Flower is a dominated action; optimal play ignores it.

ANALYTIC EQUILIBRIUM
=====================
Y mix: rock=0.333, paper=0.333, scissors=0.333, flower=0.000
X mix: rock=0.333, paper=0.333, scissors=0.333, flower=0.000
Game value to Y: 0.000
Game value to X: 0.000

MCCFR DIAGNOSTICS
==================
Iterations:              200000
Estimated EV (Player X): 0.0000
Y strategy:             rock=0.327, paper=0.323, scissors=0.350, flower=0.000
X strategy:             rock=0.335, paper=0.333, scissors=0.332, flower=0.000

Done.
```

The flower option showcases dominated-strategy elimination in practice: both the analytic mix
and the MCCFR learner quickly drop it, reinforcing that extra actions can be ignored when they
never improve expectation.

## Cops and Robbers (Example 10.5)

- **Rules:** Player X (the cop) chooses whether to `patrol` or `stand_down`; Player Y (the
  robber) simultaneously chooses to `rob` or `stay_home`. Patrolling while the robber stays
  home costs the cop one chip (default `patrol_cost=1`). Catching a robber while on patrol nets
  one chip (`arrest_reward=1`), and failing to patrol while the robber robs loses one chip
  (`robbery_reward=1`).
- **Analytic Nash equilibrium:** For positive patrol cost, arrest reward, and robbery reward,
  the cop patrols with probability `robbery_reward / (patrol_cost + arrest_reward + robbery_reward)`
  and the robber robs with probability `patrol_cost / (patrol_cost + arrest_reward + robbery_reward)`.
  With the unit payoffs above, both players mix their aggressive action one-third of the time
  and the cop's expected value is
  `-(patrol_cost * robbery_reward) / (patrol_cost + arrest_reward + robbery_reward)`.
- **Implementation:** `mathematics_of_poker.games.ch10.CopsAndRobbersGame` parametrises the
  payoffs, exposes an analytic helper, and reuses `solve_mccfr_equilibrium()` to confirm the
  mixed strategy numerically.

### Cops and Robbers Example Run

```bash
python examples/cops_and_robbers.py --iterations 200000 --seed 23
```

Sample output:

```text
COPS AND ROBBERS (Chapter 10)
=============================
Patrol cost:     1.00
Arrest reward:   1.00
Robbery reward:  1.00

ANALYTIC EQUILIBRIUM
=====================
Cop mix: patrol=0.333, stand_down=0.667
Robber mix: rob=0.333, stay_home=0.667
Game value to Cop (X): -0.333
Game value to Robber (Y): 0.333

MCCFR DIAGNOSTICS
==================
Iterations:              200000
Estimated EV (Player X): -0.3335
Cop strategy:          patrol=0.379, stand_down=0.621
Robber strategy:       rob=0.332, stay_home=0.668

Done.
```

The dominated standby/patrol trade-off mirrors the book's Example 10.5: the cop must patrol
just often enough to deter the robber, and MCCFR tracks the closed-form mix within a few
hundred thousand iterations.
