# Mathematics of Poker

Python implementation of the toy games from [The Mathematics of Poker](https://www.amazon.com/Mathematics-Poker-Bill-Chen/dp/1886070253) by Bill Chen and Jerrod Ankenman.

## Overview

This project implements various game-theoretic models and toy games discussed in "The Mathematics of Poker", providing practical Python implementations for educational and research purposes.

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






## Project Structure

```
mathematics-of-poker/
├── mathematics_of_poker/     # Main package directory
│   ├── __init__.py          # Package initialization
│   ├── games/               # Game implementations
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

## Usage

### The Clairvoyance Game (Example 11.1)

```python
from mathematics_of_poker.games import ClairvoyanceGame

# Create the game with default parameters (pot=1, bet=1)
game = ClairvoyanceGame(pot_size=1.0, bet_size=1.0)

# Solve for Nash equilibrium
solution = game.solve_nash_equilibrium()

# Display results
print(game.analyze_strategies(solution))
print(game.get_mixed_strategy_interpretation(solution))

# Verify the solution is a valid equilibrium
is_valid = game.verify_equilibrium(solution)
print(f"Valid equilibrium: {is_valid}")
```

### Running Examples

```bash
python examples/clairvoyance_example.py
```

This will demonstrate the Clairvoyance Game with detailed analysis including:
- Payoff matrices for both players
- Optimal mixed strategies  
- Game value and strategic interpretation
- Sensitivity analysis for different bet sizes

To visualize the Monte Carlo CFR diagnostics, install `matplotlib` and run:

```bash
pip install matplotlib
mkdir -p plots  # use 'mkdir plots' on Windows PowerShell
python examples/clairvoyance_example.py --solver mccfr --plot --plot-file plots/mccfr_diagnostics.png
```

The `--plot` flag opens an interactive window when supported, while `--plot-file` saves the
visualization into the `plots/` folder for headless environments and keeps generated PNGs out of
version control.

### Current Limitations

The current implementation finds a valid Nash equilibrium but may converge to the trivial solution where both players always check. Work is ongoing to improve the solver to consistently find the interesting mixed-strategy equilibrium described in the book.

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
