# Chapter 16: Small Bets, Big Pots: No-Fold [0,1] Games

## Overview

No-fold games are a class of poker models where folding is never optimal for either player. These games arise when the pot is large relative to the bet sizes, making it correct to always call. This simplification enables deep analysis of betting patterns and bluffing strategies.

## Key Concepts

### No-Fold Condition
Folding is suboptimal when:
- Pot odds are very favorable
- Bet sizes are small relative to pot
- Any hand has sufficient pot equity to call

### Game Structure
Typical no-fold [0,1] game:
- Hands uniformly distributed on [0, 1]
- Small bet sizes relative to pot
- Players always call bets
- Only betting decisions matter

## Why No-Fold Games?

### Analytical Benefits
No-fold games provide:
- **Simplified analysis**: No folding decisions
- **Clear equilibrium**: Focus on betting patterns
- **Bluffing study**: Pure bluffing scenarios
- **Tractable solutions**: Often solvable analytically

### Real Poker Relevance
Applies when:
- Very large pots relative to remaining bets
- Short-stacked situations
- River situations with good pot odds

## Mathematical Model

### [0,1] Uniform Distribution
- Each player's hand is x ∈ [0, 1]
- Uniform distribution: f(x) = 1
- Higher values beat lower values

### Bet Sizing
- Pot size: P
- Bet size: b
- Condition for no-fold: b/P ratio small enough that any hand calls

### Strategy Space
Since folding is never optimal:
- Only decision is whether to bet
- Strategy: Frequency of betting with each hand strength
- Represented as function β(x): [0,1] → [0,1]

## Simple No-Fold Game

### One Betting Round
**Setup:**
- Pot: P = 1
- Bet size: b (small)
- Player 1: Bet or check with hand x₁
- Player 2: Always calls if P1 bets
- Showdown: Higher hand wins

### Optimal Strategy
Player 1's optimal strategy:
- Bet with very strong hands (value betting)
- Bet with very weak hands (bluffing)
- Check with medium hands

This creates a **polarized betting range**.

## Equilibrium Analysis

### Value Betting Threshold
Player 1 bets with hands x > t_high where:
- These hands win often enough to profit from betting
- Threshold depends on bet size and pot size

### Bluffing Threshold  
Player 1 also bets with hands x < t_low where:
- These hands rarely win at showdown anyway
- Betting provides additional equity through opponent's mistakes
- Properly balanced with value bets

### Middle Range
Hands in (t_low, t_high):
- Have some showdown value
- Not strong enough to bet for value
- Too strong to use as bluffs
- Checking is optimal

## Mathematical Results

### Threshold Calculations
For bet size b and pot size P:
- Optimal thresholds satisfy equilibrium conditions
- Depend on ratio b/P
- Can be derived analytically

### Expected Values
At equilibrium:
- EV(Bet, x) for each hand strength
- EV(Check, x) for each hand strength
- Thresholds where these are equal

### Bluff-to-Value Ratio
Optimal ratio of bluffs to value bets:
- Related to pot odds
- Ensures opponent is indifferent
- Formula: (Bluffs)/(Value) = P/(b)

## Multiple Betting Rounds

### Added Complexity
With multiple betting rounds in no-fold game:
- Sequential betting decisions
- Information revelation
- More complex equilibrium

### Strategic Considerations
- Early bets provide information
- Later bets build pot
- Balancing across all decision points

## Extensions

### Asymmetric Information
- Different hand distributions for each player
- Asymmetric bet sizes
- Position advantages

### Bet Size Selection
Allowing multiple bet sizes:
- Larger bets for stronger polarization
- Smaller bets for thinner value
- Mixed strategies over bet sizes

### Non-Uniform Distributions
Using other distributions:
- Discrete distributions
- Skewed distributions
- Realistic poker hand distributions

## Implementation Considerations

### Numerical Solutions
When analytical solutions unavailable:
- Discretize [0,1] into bins
- Solve linear system for equilibrium
- Iterate to convergence

### Verification
Check equilibrium by:
- Computing expected values
- Verifying no profitable deviations
- Simulation against strategy

## Applications to Real Poker

### Large Pot Scenarios
No-fold analysis applies when:
- Many players in pot
- Small relative bet sizes remain
- Late position bets into large pots

### Limit Poker
More applicable in limit poker:
- Fixed bet sizes
- Often correct to call to river
- Similar strategic considerations

### Tournament Bubble
Near bubble in tournaments:
- High fold equity elsewhere
- But some situations favor calling
- Mixed applicability

## Key Insights

### Polarization
- Optimal betting ranges are polarized
- Middle hands prefer to check
- Value and bluffs at extremes

### Bet Sizing Effects
- Smaller bets require more frequent bluffing
- Larger bets allow less frequent bluffing
- Ratio follows pot odds formula

### Information Value
Even when folding is not optimal:
- Betting reveals information
- Checking conceals hand strength
- Strategic implications remain

## Implementation Notes

The Python implementation includes:
- No-fold game simulators
- Equilibrium solvers for [0,1] games
- Threshold calculators
- Expected value functions
- Visualization of betting ranges
- Comparison with fold-possible games

## Advanced Topics

### Game Theory Bounds
- Maximum exploitability
- Worst-case scenarios
- Approximation quality

### Continuous vs. Discrete
- Continuous hand distributions
- Discrete strategy spaces
- Approximation methods

## Key Takeaways

1. No-fold games simplify analysis while retaining key strategic elements
2. Optimal play involves polarized betting ranges
3. Bluff-to-value ratios follow mathematical principles
4. Results provide insights for real poker situations
5. Small bets relative to large pots create no-fold scenarios

## Further Reading

- Connections to signaling games in economics
- Information theory applications
- Extensions to multi-player scenarios
- Relationship to mechanism design
