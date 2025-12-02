# Chapter 12 – Heads-up Jam-or-Fold Games

Chapter 12 of *The Mathematics of Poker* studies shallow-stacked heads-up play where the attacker and defender act in a strict jam-or-fold structure. Each player receives a single private hand strength and can only choose between shoving all-in or folding/calling. These toy games reveal how stack depth and blind structure interact with equilibrium jamming and calling thresholds.

## Implemented examples

| Example | Description | Status |
|---------|-------------|--------|
| 12.1 | [0,1] Jam-or-Fold Game #1 | ✅ Implemented |
| 12.2 | [0,1] Jam-or-Fold Game #2 | ⏳ Planned |
| 12.3 | Jam-or-Fold No-limit Hold'em | ⏳ Planned |

This chapter builds on the Chapter 11 half-street utilities but introduces stack-size dependent payoffs and two-way all-in decisions.

## [0,1] Jam-or-Fold Game #1 (Example 12.1)

Both players draw a hand strength uniformly on ``[0,1]`` (lower is better). The defender (Player X) posts the big blind of 1 unit, while the attacker (Player Y) posts the small blind of 0.5 units and may either fold or jam all-in for a total stack of ``S`` units. If the attacker jams, the defender can call (putting in the rest of his stack) or fold. On a call, the lower hand wins the entire pot of ``2S``.

- **Analytic thresholds**: closed-form solutions yield the optimal jam threshold for Player Y and call threshold for Player X as functions of ``S``:
	- Jam threshold: ``j^* = \frac{3S}{(S + 1)^2}``
	- Call threshold: ``c^* = \frac{3}{2(S + 1)}``
- **Monte Carlo validation**: a helper estimates the attacker's EV under the analytic strategy profile.
- **MCCFR discretisation**: the game is discretised into uniform hand buckets and solved via external-sampling MCCFR. The solver reports jam/call frequencies (which equal the thresholds on the uniform [0,1] scale) alongside the bucket index where the strategy mix drops below 50%, plus diagnostic plots for strategy and regret per iteration.

### Example script

```powershell
python examples\jam_or_fold_game_1.py --stack 10 --buckets 40 --iterations 250000 --samples 100000 --plot --plot-file plots\ch12_jam_or_fold_game_1.png
```

The saved figure shows Player Y's jam frequency (with regret per iteration) and Player X's call frequency across hand buckets, providing a visual check against the analytic thresholds.
