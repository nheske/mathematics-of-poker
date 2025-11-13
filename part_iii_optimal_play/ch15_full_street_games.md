# Chapter 15: Player X Strikes Back: Full-Street Games

## Overview

Full-street games model complete betting rounds with multiple decision points. These games capture more of the complexity of real poker, including multiple betting opportunities and information revelation across a street.

## Key Concepts

### Full-Street Game Structure
A full street includes:
1. Initial action (check or bet)
2. Response to bet (call, raise, or fold)
3. Response to raise (call, reraise, or fold)
4. Potential for multiple raises
5. Final showdown or fold

### Decision Tree Complexity
Full streets have:
- Multiple decision nodes
- Branching game trees
- Path-dependent strategies
- Complex equilibrium calculations

## Game Components

### Action Sequences
Possible sequences in a full street:
- **Check-Check**: Both players check, go to showdown
- **Bet-Call**: One player bets, other calls
- **Bet-Fold**: One player bets, other folds
- **Bet-Raise-Call**: Initial bet, raise, call
- **Bet-Raise-Fold**: Initial bet, raise, fold
- **Check-Bet-Call**: Check, bet, call
- **Check-Bet-Raise-Call**: Check, bet, raise, call

### Bet Sizing Options
In no-limit full-street games:
- Multiple bet sizes available
- Raise sizes (minimum raise, pot-sized, etc.)
- Strategic implications of each size

## Strategic Considerations

### Position Advantage
The player acting last has informational advantage:
- Sees opponent's action first
- Can respond optimally
- Controls pot size more effectively

### Range Polarization
As betting escalates:
- Ranges become more polarized
- Medium hands often fold or check
- Final ranges typically contain only strong hands and bluffs

### Balancing Ranges
At each decision point:
- Value hands and bluffs must be balanced
- Prevents exploitation
- Maintains optimal frequency ratios

## Mathematical Analysis

### Game Tree Representation
Full streets represented as:
- Nodes: Decision points
- Edges: Available actions
- Leaves: Terminal outcomes (fold or showdown)

### Backward Induction
Solving from the end of the tree:
1. Start at terminal nodes
2. Calculate expected values
3. Work backward to find optimal strategies
4. Reach initial decision point

### Equilibrium Calculation
Methods for finding Nash equilibrium:
- **Analytical**: For simple games
- **Linear programming**: For medium complexity
- **CFR (Counterfactual Regret Minimization)**: For complex games

## Example: Full-Street [0,1] Game

**Setup:**
- Hands uniformly distributed on [0, 1]
- Pot size: 1 (from antes)
- Bet size: 1
- Raise size: 2 (total)

**Action Tree:**
```
P1: Bet or Check
├─ Bet
│  └─ P2: Call, Raise, or Fold
│     ├─ Call → Showdown
│     ├─ Fold → P1 wins
│     └─ Raise
│        └─ P1: Call or Fold
│           ├─ Call → Showdown
│           └─ Fold → P2 wins
└─ Check
   └─ P2: Bet or Check
      ├─ Bet
      │  └─ P1: Call or Fold
      │     ├─ Call → Showdown
      │     └─ Fold → P2 wins
      └─ Check → Showdown
```

## Optimal Strategies

### Betting Strategies
- **Initial bet**: Value hands + bluffs (polarized)
- **Check**: Medium hands, traps, weak hands
- **Check-call**: Medium-strong hands
- **Check-raise**: Very strong hands, bluffs

### Raising Strategies
When facing a bet:
- **Raise**: Very strong hands, semi-bluffs
- **Call**: Medium-strong hands, draws
- **Fold**: Weak hands

### Frequencies
Optimal frequencies depend on:
- Hand distributions
- Bet sizes
- Position
- Pot odds offered

## Key Results

### Value of Position
Quantified advantages:
- Expected value difference between positions
- Information value
- Control value

### Raise Frequencies
At equilibrium:
- Raising frequency inversely related to raise size
- Larger raises require tighter ranges
- Balance maintained throughout tree

### Check-Raise Strategies
Check-raising involves:
- Trapping strong hands
- Bluff check-raises
- Balance between value and bluffs

## Multiple Streets vs. Full Street

### Single Full Street
- One complete betting round
- Simplified compared to multi-street
- Still captures key strategic elements

### Multi-Street Games
- Multiple full streets
- Information revelation across streets
- More complex equilibrium
- Covered in advanced analysis

## Implementation Challenges

### Computational Complexity
Full-street games require:
- Efficient tree traversal
- Memory for strategy storage
- Iterative solving algorithms

### Strategy Representation
Strategies stored as:
- Action probabilities at each information set
- Compact representations for similar situations
- Abstractions for continuous hand spaces

## Applications to Real Poker

### River Play
Full-street analysis most applicable to:
- River betting decisions
- Complete information (no more cards)
- Final betting round

### Turn Play
Also applicable with modifications:
- Consider river card possibilities
- Account for future streets
- More complex calculations

## Implementation Notes

The Python implementation includes:
- Game tree builders
- Nash equilibrium solvers
- Strategy evaluators
- Visualization of decision trees
- Expected value calculators
- Range analyzers

## Key Insights

1. Full streets add significant strategic depth
2. Multiple decision points require careful balancing
3. Position provides substantial advantage
4. Optimal play involves complex mixed strategies
5. Real poker applications in river and turn play

## Further Extensions

- Multiple bet sizes
- Asymmetric stacks
- Different starting distributions
- Multiple streets
- More than two players
