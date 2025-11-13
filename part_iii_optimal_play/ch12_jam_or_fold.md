# Chapter 12: Headsup With High Blinds: The Jam-or-Fold Game

## Overview

The jam-or-fold game models short-stack tournament poker where players' primary decisions are to go all-in (jam) or fold. This simplification is highly relevant for real tournament situations.

## Key Concepts

### Game Structure
- **Setup**: Two players, typically with equal short stacks
- **Blinds**: Small blind (SB) and big blind (BB)
- **Actions**: SB can jam (all-in) or fold; BB can call or fold

### Stack-to-Pot Ratio (SPR)
The effective stack size relative to the pot determines strategic considerations:
- Low SPR → More hands become playable
- High SPR → Tighter ranges required

## Mathematical Model

### Hand Distributions
Hands are often represented as:
- Single number representing hand strength [0, 1]
- Discrete rankings (e.g., poker hand rankings)

### Optimal Jamming Range
The SB should jam with:
- Strong hands for value
- Weak hands as bluffs
- Fold medium-strength hands (too weak to jam, too strong to bluff-jam)

### Optimal Calling Range
The BB should call with hands that have sufficient equity against the SB's jamming range.

## Equilibrium Analysis

### SB Strategy
The SB's equilibrium strategy involves:
- Jamming with top x% of hands (value)
- Jamming with bottom y% of hands (bluffs)
- Folding middle-range hands

### BB Strategy
The BB's equilibrium calling strategy:
- Call with top z% of hands
- Fold weaker hands

### Calculating Thresholds
Equilibrium thresholds depend on:
- Stack sizes
- Blind structure
- Hand distribution

## Key Results

### Nash Equilibrium Ranges
For typical short-stack scenarios:
- SB jams with ~40-60% of hands (depends on stack size)
- BB calls with ~20-35% of hands

### Expected Values
At equilibrium:
- Both players have specific expected values
- Neither can improve by deviating

## Implementation Considerations

### Hand Equity Calculations
- Pre-flop all-in equity between hand ranges
- Simplified using hand strength distributions

### Solving the Game
Methods include:
- Analytical solutions for simplified models
- Numerical optimization for complex distributions
- Iterative algorithms to find equilibrium

## Example Calculation

**Scenario:**
- Stack: 10 BB
- SB: 0.5 BB
- BB: 1 BB
- Pot after blinds: 1.5 BB

**Solution:**
Calculate optimal jamming and calling ranges that satisfy equilibrium conditions.

## Applications to Real Poker

### Tournament Play
Jam-or-fold analysis applies to:
- Short-stack push-fold situations
- Late-stage tournament play
- Satellite tournaments

### Strategy Adjustments
Factors affecting real-game play:
- ICM (Independent Chip Model) considerations
- Multiple opponents
- Varying stack sizes

## Implementation Notes

The Python implementation includes:
- Hand strength simulations
- Equilibrium solvers
- Range visualization tools
- Expected value calculators
