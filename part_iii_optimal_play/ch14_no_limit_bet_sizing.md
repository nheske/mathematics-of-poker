# Chapter 14: You Don't Have To Guess: No-Limit Bet Sizing

## Overview

This chapter explores optimal bet sizing in no-limit poker. Unlike limit poker where bet sizes are fixed, no-limit allows for a continuous range of bet sizes, adding significant strategic depth.

## Key Concepts

### Bet Sizing Fundamentals
- **Small Bets**: Easier to call, require less equity to be profitable
- **Large Bets**: Harder to call, provide better pot odds for bluffs
- **Pot-Sized Bets**: Common benchmark, offer 2:1 pot odds

### Strategic Implications
Bet sizing affects:
- Optimal calling ranges
- Bluffing frequencies
- Expected value of different holdings
- Information revealed

## Mathematical Framework

### Continuous Bet Sizing
Instead of discrete bet options, players can choose any bet size b ∈ [0, ∞).

### Optimal Bet Size Selection
Factors determining optimal bet size:
1. **Hand strength distribution**
2. **Opponent's calling tendencies**
3. **Stack depths**
4. **Position**

## Game Theory Optimal Betting

### Polarized vs. Merged Ranges

**Polarized Range:**
- Very strong hands
- Bluffs
- No medium-strength hands
- Typically use larger bet sizes

**Merged Range:**
- Mix of strong and medium hands
- Typically use smaller bet sizes
- More difficult for opponent to respond to

### Bet Sizing in Equilibrium

At equilibrium:
- Bet sizes chosen make opponent indifferent (or properly balanced)
- Bluffing frequency matches pot odds offered
- Cannot be exploited by any counter-strategy

## No-Limit vs. Limit

### Strategic Differences
**No-Limit:**
- Bet sizing becomes a strategic variable
- Can protect hands with larger bets
- Can control pot size more precisely

**Limit:**
- Fixed bet sizes simplify analysis
- Less control over pot size
- Different optimal strategies

## Toy Game Analysis

### Simple No-Limit Game
Consider a game where:
- Players have hand distributions on [0, 1]
- Player 1 can bet any amount b ≥ 0
- Player 2 can call or fold

**Questions:**
- What bet size should P1 choose with strong hands?
- What bet size should P1 choose when bluffing?
- How does P2's optimal calling range change with bet size?

## Key Results

### Bet Sizing with the Nuts
With an unbeatable hand:
- Generally bet large to maximize value
- But not so large that opponent never calls
- Balance between maximizing call frequency and amount

### Optimal Bluffing Bet Sizes
When bluffing:
- Larger bets require fewer bluffs (better pot odds)
- Smaller bets require more bluffs but risk less
- Trade-off between efficiency and risk

### Geometric Bet Sizing
Using geometric (multiplicative) bet sizing across multiple streets:
- Maintains constant pot odds
- Simplifies strategic decisions
- Common in real poker play

## Multiple Streets

### Bet Sizing Sequences
On multi-street games:
- Bet sizes should relate across streets
- Early street bets affect later options
- Stack-to-pot ratio evolves

### Path Dependency
Later street decisions depend on:
- Previous bet sizes
- Remaining stack sizes
- Information revealed

## Implementation Considerations

### Discretization
For computational tractability:
- Limit bet sizes to discrete set
- e.g., {0.5×pot, 1×pot, 2×pot}
- Approximate continuous solution

### Solving Methods
- Linear programming for simplified models
- Counterfactual regret minimization (CFR) for complex games
- Numerical optimization

## Example: [0,1] Game with No-Limit Betting

**Setup:**
- Hands uniformly distributed on [0, 1]
- Player 1 chooses bet size b
- Player 2 calls or folds

**Analysis:**
Find optimal bet sizing strategy and calling ranges that form Nash equilibrium.

## Applications to Real Poker

### Practical Bet Sizing
Real poker considerations:
- **1/3 pot**: Small bet, wide range
- **2/3 pot**: Medium bet, balanced range
- **Pot-sized**: Polarized range
- **Overbet**: Very polarized range

### Exploitative Adjustments
Against non-optimal opponents:
- Bet larger with value hands vs. calling stations
- Bet smaller as bluffs vs. loose callers
- Adjust based on observed tendencies

## Implementation Notes

The Python implementation includes:
- Continuous bet sizing models
- Optimal bet size calculators
- Equilibrium solvers for no-limit games
- Comparison tools for different bet sizes
- Visualization of strategy spaces

## Key Takeaways

1. Bet sizing is a powerful strategic tool
2. Optimal sizes depend on hand ranges and opponent strategies
3. Larger bets need fewer bluffs but risk more
4. Multiple bet sizes can coexist in equilibrium
5. Real poker benefits from understanding these principles
