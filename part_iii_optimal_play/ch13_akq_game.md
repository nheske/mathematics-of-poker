# Chapter 13: Poker Made Simple: The AKQ Game

## Overview

The AKQ game is a simplified three-card poker game that captures essential strategic elements of real poker while remaining analytically tractable. It's one of the most studied toy games in poker theory.

## Game Structure

### Setup
- **Deck**: Three cards {A, K, Q} where A > K > Q
- **Players**: Two players
- **Antes**: Each player puts in 1 chip
- **Deal**: Each player receives one card (one card remains unseen)

### Betting Structure
- **Round 1**: Player 1 can bet or check
- **Round 2**: 
  - If P1 bets, P2 can call or fold
  - If P1 checks, P2 can bet or check
  - If P2 bets after P1 checks, P1 can call or fold

### Bet Sizing
- Standard bet size: b (typically b = 1)
- Pot size: 2 (from antes)

## Hand Frequencies

Each card appears with equal probability:
- P(A) = 1/3
- P(K) = 1/3  
- P(Q) = 1/3

## Strategic Considerations

### Player 1 Strategy
- **With Ace**: Always bet (strongest hand)
- **With King**: Mixed strategy (can bet or check)
- **With Queen**: Either check (give up) or bluff-bet

### Player 2 Strategy
Player 2's strategy depends on:
- Whether P1 bet or checked
- P2's card
- Probability distributions implied by P1's action

## Nash Equilibrium

### Key Elements
The equilibrium involves:
- **Bet frequencies**: How often to bet with each hand
- **Call frequencies**: How often to call with each hand
- **Bluff frequencies**: How often to bluff with weak hands

### Equilibrium Strategy Example
For b = 1 (bet size = pot size):
- **Player 1 with A**: Bet 100%
- **Player 1 with K**: Bet with some probability p
- **Player 1 with Q**: Bluff with some probability q
- **Player 2 calling frequencies**: Depend on P1's strategy

## Mathematical Analysis

### Expected Value Calculations

**For Player 1 with King:**
- EV(Bet, K) vs EV(Check, K)
- Optimal when opponent's calling strategy makes P1 indifferent

**For Player 1 with Queen:**
- EV(Bluff, Q) should equal EV(Check-Fold, Q) at equilibrium
- This determines optimal bluffing frequency

### Indifference Equations
At equilibrium, Player 2 must be indifferent between calling and folding with King:
```
EV(Call, K) = EV(Fold, K)
```

This constraint determines Player 1's bluffing frequency.

## Key Results

### Bluff-to-Value Ratios
The optimal bluffing ratio relates to pot odds:
- Larger bets require fewer bluffs
- Smaller bets require more bluffs
- Ratio follows: (bluffs)/(value bets) = (pot odds offered)

### Mixed Strategies
Both players must use mixed strategies:
- Pure strategies are exploitable
- Randomization is essential for optimal play

## Extensions

### Different Bet Sizes
Analyzing the AKQ game with different bet sizes (b):
- b < 1: Smaller bets
- b > 1: Larger bets
- b → ∞: All-in

### Multiple Betting Rounds
Adding complexity:
- Check-raise options
- Multiple bet sizes
- More cards in the deck

## Implementation Notes

The Python implementation includes:
- Complete game tree representation
- Nash equilibrium solver
- Strategy visualization
- Expected value calculations for all decision points
- Simulation for verification

## Applications

The AKQ game teaches:
- Fundamental betting theory
- Bluffing ratios
- Indifference principles
- Mixed strategy equilibria
- How bet sizing affects optimal play

## Further Study

The AKQ game provides a foundation for understanding:
- More complex toy games
- Real poker scenarios
- Multi-street games
- Larger card decks
