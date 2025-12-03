# Mathematics of Poker

Python implementation of the toy games from [**The Mathematics of Poker**](https://www.amazon.com/Mathematics-Poker-Bill-Chen/dp/1886070253) by Bill Chen and Jerrod Ankenman.

## Overview

This project implements various game-theoretic models and toy games discussed in "The Mathematics of Poker", and provides practical Python implementations for educational and research purposes.

I have incorporated the solver method of Counterfactual Regret Minimization algorithms as an alternative means of determining optimal play for the various toy games from the book. 

**Counterfactual Regret Minimization (CFR)**
A self-play algorithm that finds near-optimal strategies by repeatedly playing the game against itself.
* Starts with a random strategy
* After each iteration, asks:
“How much better would I have done if I always chose this action?”
* This difference = regret
* Positive regret accumulates → good actions gain weight
* Strategy updates by choosing actions proportional to positive regret
* Repeating this thousands/millions of times → converges to a Nash equilibrium

**Monte Carlo CFR (MCCFR)**
Samples only a few random trajectories each iteration, letting it scale to huge games like poker.

10. Facing The Nemesis: Game Theory
11. [One Side of the Street: Half-Street Games](mathematics_of_poker/games/ch11/ch11_half_street_games.md)
    * Example 11.1 - The Clairvoyance Game
    * Example 11.2 - [0, 1] Game #1 
    * Example 11.3 - [0, 1] Game #2 
12. [Headsup With High Blinds: The Jam-or-Fold Game](mathematics_of_poker/games/ch12/ch12_jam_or_fold.md)
    * Example 12.1 - [0, 1] Jam-or-Fold Game #1
    * Example 12.2 - [0, 1] Jam-or-Fold Game #2
    * Example 12.3 - Jam-or-Fold No-limit Holdem
13. [Poker Made Simple: The AKQ Game](mathematics_of_poker/games/ch13/ch13_akq_game.md)
    * Example 13.1 - AKO Game #1 
    * Example 13.2 - AKQ Game #2
14. You Don't Have To Guess: No-Limit Bet Sizing
    * Example 14.1 - The Half-Street No-Limit Clairvoyance Game
    * Example 14.2 - AKQ Game #3 
    * Example 14.3 - [0, 1] Game #3
15. Player X Strikes Back: Full-Street Games
    * Example 15.1 - AKQ Game #4
    * Example 15.2 - AKO Game #5
16. Small Bets, Big Pots: No-Fold [0,1] Games
    * Example 16.1 - [0, 1] Game #4 
    * Example 16.2 - [0, 1] Game #5
    * Example 16.3 - [0, 1] Game #6 – The Raising Game 
    * Example 16.4 - [0, 1] Game #7
    * Example 16.5 - [0,1] Game #8: The Raising Game with Check-Raise

### Currently Implemented

**Chapter 11: Half-Street Games**
- **Example 11.1 - The Clairvoyance Game**: A simplified poker game where one player has perfect information. Demonstrates Nash equilibrium computation for mixed strategies in zero-sum games.
- **Example 11.2 - [0,1] Game #1**: No-fold half-street game with continuous hand strengths; highlights threshold betting and MCCFR discretisation.
- **Example 11.3 - [0,1] Game #2**: Folding allowed for Player X; analytic thresholds vary with pot size and MCCFR recovers the optimal calling range.

**Chapter 12: Headsup With High Blinds – The Jam-or-Fold Game** ([details](mathematics_of_poker/games/ch12/ch12_jam_or_fold.md))
- **Example 12.1 - [0,1] Jam-or-Fold Game #1**: Players jam or fold from the blinds with equal stacks; includes analytic jam/call thresholds, Monte Carlo validation, and MCCFR diagnostics with visualisations.

### Planned Implementations

**Chapter 11: One Side of the Street: Half-Street Games**
- Example 11.4+ – Additional threshold and mixed-strategy variants

**Chapter 12: Headsup With High Blinds: The Jam-or-Fold Game** ([details](mathematics_of_poker/games/ch12/ch12_jam_or_fold.md))
- Example 12.1 - [0, 1] Jam-or-Fold Game #1
- Example 12.2 - [0, 1] Jam-or-Fold Game #2
- Example 12.3 - Jam-or-Fold No-limit Holdem

**Chapter 13: AKQ Game** ([placeholder](mathematics_of_poker/games/ch13/ch13_akq_game.md))
- Example 13.1 - AKQ Game baseline (coming soon)

**And more chapters to follow...**


## Future Direction

Right now, I’m working through **Chapters 10–21 of _The Mathematics of Poker_** and implementing the core optimal-play models in Python. Once that foundation is in place, I’ll start expanding including:

- **Nit game**
- **7–2 game**
- **Kitty game**
- Other **poker “carnival” variants** and custom incentive structures
- Pot Limit Omaha specific simulations such as calling 4-bets vs. presumed aces

The goal is to create a poker learning resource that leverages 
If you’re into learning:
- Poker math and game theory  
- Python implementations of toy games and solvers  
- CFR and solver related algorithms 
- Pot Limit Omaha (PLO) specifics 

…I’d love to find collaborators.

**PRs, issues, and discussions are very welcome.** If you’d like to get involved, feel free to open an issue to introduce yourself or suggest a direction.



## Project Structure

```
mathematics-of-poker/
├── mathematics_of_poker/     # Main package directory
│   ├── __init__.py          # Package initialization
│   ├── games/               # Game implementations by chapter
│   │   ├── ch11/            # Half-street games
│   │   │   ├── ch11_half_street_games.md
│   │   │   ├── clairvoyance.py
│   │   │   └── ...
│   │   ├── ch12/            # Jam-or-fold games
│   │   │   ├── ch12_jam_or_fold.md
│   │   │   ├── jam_or_fold_game_1.py
│   │   │   └── ...
│   │   ├── ch13/            # AKQ game placeholder
│   │   │   └── ch13_akq_game.md
│   │   └── __init__.py
│   ├── models/              # Data models and structures
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── requirements.txt         # Core dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Installation

### For Users

```bash
pip install -e .
```

### For Development

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Requirements

- Python 3.7+
- NumPy (for numerical computations)
- SciPy (for optimization algorithms)
- Matplotlib (for visualizations)


## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black mathematics_of_poker tests
```

### Linting

```bash
ruff check mathematics_of_poker tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

- Chen, B., & Ankenman, J. (2006). *The Mathematics of Poker*. ConJelCo LLC.
