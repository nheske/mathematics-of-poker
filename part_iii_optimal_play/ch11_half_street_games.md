# Chapter 11: One Side of the Street: Half-Street Games

## Overview

Half-street games are simplified poker models with a single betting round. These games help understand optimal betting strategies without the complexity of multiple streets.

## Key Concepts

### Half-Street Game Structure
A typical half-street game includes:
1. Players receive hands from a distribution
2. A single betting round occurs
3. Hands are shown down if both players put in equal money
4. No additional cards are dealt

### Betting Actions
- **Bet**: Put chips into the pot
- **Check**: Pass action to opponent or go to showdown
- **Call**: Match opponent's bet
- **Fold**: Forfeit the pot
- **Raise**: Increase the bet size

## Mathematical Analysis

### Hand Distributions
Players' hands are drawn from a distribution, often:
- Uniform distribution [0, 1]
- Discrete distributions (e.g., {A, K, Q})

### Strategy Representation
Strategies are typically threshold-based:
- Bet with hands above threshold t₁
- Call bets with hands above threshold t₂
- Fold hands below threshold t₂

### Equilibrium Calculation
Finding Nash equilibrium involves:
1. Setting up expected value equations for both players
2. Solving for optimal thresholds
3. Verifying no player can improve by deviating

## Types of Half-Street Games

### Bet-or-Check, Call-or-Fold
- Player 1: Bet or check
- Player 2 (if facing bet): Call or fold
- Simplest half-street game

### Check-Raise Game
- Player 1: Check
- Player 2: Bet or check
- Player 1 (if facing bet): Call, fold, or raise
- More complex strategic interactions

## Example: Simple Bet-or-Check Game

Consider:
- Pot size: 1
- Bet size: 1
- Hands uniformly distributed on [0, 1]

**Optimal Strategy:**
- Player 1 bets with hands > t₁ (bluff threshold and value threshold)
- Player 2 calls with hands > t₂
- Equilibrium values can be calculated analytically

## Implementation Notes

The Python implementation includes:
- Classes for half-street game states
- Functions to calculate optimal strategies
- Monte Carlo simulation for verification
- Visualization of strategy ranges

## Key Results

### Betting Frequency
The optimal betting frequency depends on:
- Pot size
- Bet size
- Hand distribution

### Bluffing Ratios
Optimal bluffing ratios relate to pot odds:
- More bluffs needed with larger bet sizes
- Bluff-to-value ratios follow mathematical principles

## Applications

Understanding half-street games provides insight into:
- River betting decisions in real poker
- Optimal bluffing frequencies
- Calling ranges against different bet sizes
