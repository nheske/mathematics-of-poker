# Chapter 12 – Heads-up Jam-or-Fold Games

Chapter 12 of *The Mathematics of Poker* studies shallow-stacked heads-up play where the attacker and defender act in a strict jam-or-fold structure. Each player receives a single private hand strength and can only choose between shoving all-in or folding/calling. These toy games reveal how stack depth and blind structure interact with equilibrium jamming and calling thresholds.

## Core Ideas
1. Example 12.1: **Game #1 (Winner Take All)** In this static model where the best hand wins the entire pot, optimal play is relatively tight. The defender holds a significant advantage for most stack sizes (specifically when stacks >2).
2. Example 12.2: **Game #2 (Loser Gets Equity)** Adjusting the game so the worst hand retains 33% equity (mimicking preflop realities) forces significantly looser strategies. This shift gives the attacker the advantage up to a stack size of 6 units.
3. Example 12.3: **No-Limit Hold’em Jam-or-Fold** Using real poker hand equities, optimal play is surprisingly aggressive; for example, with 16-chip stacks, the button should jam nearly 62% of hands. This "jam-or-fold" approach is considered near-optimal for stack sizes under 10–12 blinds.

![Chapter 12 jam-or-fold infographic](../../../assets/infographics/ch12_square_detail.png)


## Implemented examples

| Example | Description | Status |
|---------|-------------|--------|
| 12.1 | [0,1] Jam-or-Fold Game #1 | ✅ Implemented |
| 12.2 | [0,1] Jam-or-Fold Game #2 | ✅ Implemented |
| 12.3 | Jam-or-Fold No-limit Hold'em | ⏳ Planned |

This chapter builds on the Chapter 11 half-street utilities but introduces stack-size dependent payoffs and two-way all-in decisions.

## [0,1] Jam-or-Fold Game #1 (Example 12.1)

Both players draw a hand strength uniformly on ``[0,1]`` (lower is better). The defender (Player X) posts the big blind of 1 unit, while the attacker (Player Y) posts the small blind of 0.5 units and may either fold or jam all-in for a total stack of ``S`` units. If the attacker jams, the defender can call (putting in the rest of his stack) or fold. On a call, the lower hand wins the entire pot of ``2S``.

- **Analytic thresholds**: closed-form solutions yield the optimal jam threshold for Player Y and call threshold for Player X as functions of `S`:
- Jam threshold: $$ j = \frac{3S}{(S + 1)^2} $$
 
- Call threshold:  $$ c = \frac{3}{2(S + 1)} $$

- **Monte Carlo validation**: a helper estimates the attacker's EV under the analytic strategy profile.
- **MCCFR discretization**: the game is discretized into uniform hand buckets and solved via external-sampling MCCFR. The solver reports jam/call frequencies (which equal the thresholds on the uniform [0,1] scale) alongside the bucket index where the strategy mix drops below 50%, plus diagnostic plots for strategy and regret per iteration.

### Example script

```powershell
python examples\jam_or_fold_game_1.py --stack 10 --buckets 40 --iterations 250000 --samples 100000 --plot --plot-file plots\ch12_jam_or_fold_game_1.png
```

The saved figure shows Player Y's jam frequency (with regret per iteration) and Player X's call frequency across hand buckets, providing a visual check against the analytic thresholds.

Sample run (stack=10, buckets=40, iterations=250000):

```
```text
[0,1] JAM-OR-FOLD GAME #2
==========================
Stack size (S): 4.0
Big blind:      1.0
Small blind:    0.5
Buckets:        40
Iterations:     120000

ANALYTIC SOLUTION
=================
Stack size (S):           4.00
Regime:                   S > 3
Jam threshold (Y):        0.6316
Call threshold (X):       0.5526
Jam frequency:            0.6316
Call frequency:           0.5526
Attacker EV (chips):      0.0402
Defender EV (chips):     -0.0402

MONTE CARLO CHECK
=================
Samples:                  120000
Estimated EV (attacker):  0.0426
Analytic EV (attacker):   0.0402
Absolute error:           0.0024

MCCFR DIAGNOSTICS
==================
Estimated jam threshold:  0.7578 (jam frequency over uniform buckets)
Estimated call threshold: 0.6507 (call frequency over uniform buckets)
Jam bucket cutoff (≥50%):  0.6375
Call bucket cutoff (≥50%): 0.6375
Game value (attacker):    -0.0510
Attacker EV (MCCFR):      -0.0510
Defender EV (MCCFR):       0.0510

Sample run (stack=4, buckets=40, iterations=120000):

```text
[0,1] JAM-OR-FOLD GAME #2
==========================
Stack size (S): 4.0
Big blind:      1.0
Small blind:    0.5
Buckets:        40
Iterations:     120000

ANALYTIC SOLUTION
=================
Stack size (S):           4.00
Regime:                   S > 3
Jam threshold (Y):        0.6316
Call threshold (X):       0.5526
Jam frequency:            0.6316
Call frequency:           0.5526
Attacker EV (chips):      0.0402
Defender EV (chips):     -0.0402

MONTE CARLO CHECK
=================
Samples:                  120000
Estimated EV (attacker):  0.0426
Analytic EV (attacker):   0.0402
Absolute error:           0.0024

MCCFR DIAGNOSTICS
==================
Estimated jam threshold:  0.7578 (jam frequency over uniform buckets)
Estimated call threshold: 0.6507 (call frequency over uniform buckets)
Jam bucket cutoff (≥50%):  0.6375
Call bucket cutoff (≥50%): 0.6375
Game value (attacker):    -0.0510
Attacker EV (MCCFR):      -0.0510
Defender EV (MCCFR):       0.0510

Sample bucket strategies (jam probability shown):
  Y:bucket[0]: jam=1.000, fold=0.000
  Y:bucket[20]: jam=1.000, fold=0.000
  Y:bucket[39]: jam=0.001, fold=0.999

Jam takeaway:
  MCCFR keeps a live bluff band above the threshold, reflecting the weaker showdown edge.
  Avg jam prob. ≤ jam threshold:  0.998
  Avg jam prob. > jam threshold:   0.312

Call takeaway:
  X continues with a wider defense above the analytic call point due to baseline equity.
  Avg call prob. ≤ call threshold: 1.000
  Avg call prob. > call threshold:  0.179

Done.
```
```

Sample run (stack=4, buckets=40, iterations=120000):

```text
[0,1] JAM-OR-FOLD GAME #2
==========================
Stack size (S): 4.0
Big blind:      1.0
Small blind:    0.5
Buckets:        40
Iterations:     250000

ANALYTIC SOLUTION
=================
Stack size (S):           4.00
Regime:                   S > 3
Jam threshold (Y):        0.6316
Call threshold (X):       0.5526
Jam frequency:            0.6316
Call frequency:           0.5526
Attacker EV (chips):      0.0402
Defender EV (chips):     -0.0402

MONTE CARLO CHECK
=================
Samples:                  120000
Estimated EV (attacker):  0.0386
Analytic EV (attacker):   0.0402
Absolute error:           0.0016

MCCFR DIAGNOSTICS
==================
Estimated jam threshold:  0.6180 (jam frequency over uniform buckets)
Estimated call threshold: 0.5435 (call frequency over uniform buckets)
Jam bucket cutoff (≥50%):  0.5750
Call bucket cutoff (≥50%): 0.5250
Game value (attacker):    0.0468
Attacker EV (MCCFR):      0.0468
Defender EV (MCCFR):     -0.0468
Game value (attacker):    -0.0510
Attacker EV (MCCFR):      -0.0510
Defender EV (MCCFR):       0.0510

Jam takeaway:
  MCCFR keeps a live bluff band above the threshold, reflecting the weaker showdown edge.
  Avg jam prob. ≤ jam threshold:  0.998
  Avg jam prob. > jam threshold:   0.312

Call takeaway:
  X continues with a wider defense above the analytic call point due to baseline equity.
  Avg call prob. ≤ call threshold: 1.000
  Avg call prob. > call threshold:  0.179

Done.
```

Use the comparative summary to benchmark Solver #2 against the winner-take-all variant: looser calling ranges keep the defender in pots, while the attacker's showdown equity edge lets them pressure additional buckets without immediately gifting value.
