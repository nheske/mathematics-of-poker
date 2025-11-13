# Chapter 10: Facing The Nemesis: Game Theory

## Overview

This chapter introduces fundamental game theory concepts as they apply to poker. It covers the concepts of Nash equilibrium, minimax strategies, and optimal play against rational opponents.

## Key Concepts

### Nash Equilibrium
A Nash equilibrium is a set of strategies where no player can improve their expected value by unilaterally changing their strategy, assuming all other players keep their strategies fixed.

### Minimax and Maximin
- **Minimax**: Minimizing the maximum loss
- **Maximin**: Maximizing the minimum gain

In two-player zero-sum games (like heads-up poker), these concepts converge to the same solution.

### Game Theory Optimal (GTO) Play
GTO play refers to a strategy that cannot be exploited by any opponent. Against an optimal opponent, GTO play guarantees that you cannot lose in expectation over the long run.

## Mathematical Foundations

### Two-Player Zero-Sum Games
In these games:
- One player's gain is the other player's loss
- The sum of payoffs is always zero
- There exists an optimal (unexploitable) strategy

### Strategy Spaces
- **Pure Strategy**: A deterministic action plan
- **Mixed Strategy**: A probability distribution over pure strategies

## Applications to Poker

### Unexploitability
An unexploitable strategy in poker:
- Cannot be beaten by any counter-strategy
- May not maximize profit against suboptimal opponents
- Provides a baseline for evaluating play

### Value of Information
Understanding optimal play helps assess:
- When to deviate from GTO for exploitation
- How much value opponents give up by playing suboptimally

## Examples

### Simple Toy Game
Consider a simplified game with:
- Player 1 has a choice between Action A and Action B
- Player 2 has a choice between Action X and Action Y
- Payoffs depend on both players' choices

The optimal mixed strategy can be found by solving for the equilibrium where neither player can improve by changing their strategy.

## Implementation Notes

The Python implementation includes:
- Functions to calculate Nash equilibria for simple matrix games
- Tools for analyzing game trees
- Visualization of strategy spaces and payoff matrices

## Further Reading

- Von Neumann and Morgenstern's "Theory of Games and Economic Behavior"
- John Nash's papers on equilibrium points in n-person games
