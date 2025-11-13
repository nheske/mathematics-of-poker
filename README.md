# Mathematics of Poker

Python implementation of the toy games from ["Mathematics of Poker" by Bill Chen and Jerrod Ankenman](https://www.amazon.com/Mathematics-Poker-Bill-Chen/dp/1886070253)

## Overview

This repository contains Python implementations and documentation for the theoretical poker games presented in "Mathematics of Poker". The implementations focus on game-theoretic optimal (GTO) strategies and equilibrium analysis.

## Contents

### Part III: Optimal Play

Complete implementation of chapters 10-16, covering fundamental game theory and optimal poker strategies.

See [part_iii_optimal_play/README.md](part_iii_optimal_play/README.md) for detailed information.

**Chapters:**
- Chapter 10: Facing The Nemesis: Game Theory
- Chapter 11: One Side of the Street: Half-Street Games
- Chapter 12: Headsup With High Blinds: The Jam-or-Fold Game
- Chapter 13: Poker Made Simple: The AKQ Game
- Chapter 14: You Don't Have To Guess: No-Limit Bet Sizing
- Chapter 15: Player X Strikes Back: Full-Street Games
- Chapter 16: Small Bets, Big Pots: No-Fold [0,1] Games

## Installation

```bash
# Clone the repository
git clone https://github.com/nheske/mathematics-of-poker.git
cd mathematics-of-poker

# Install dependencies
pip install -r requirements.txt
```

## Requirements

- Python 3.7+
- NumPy
- SciPy
- Matplotlib

## Usage

Each chapter includes both documentation (markdown) and implementation (Python):

```bash
# Run a specific chapter's implementation
cd part_iii_optimal_play
python ch10_game_theory.py
python ch13_akq_game.py
# etc.
```

## Structure

```
mathematics-of-poker/
├── README.md
├── requirements.txt
└── part_iii_optimal_play/
    ├── README.md
    ├── ch10_game_theory.md
    ├── ch10_game_theory.py
    ├── ch11_half_street_games.md
    ├── ch11_half_street_games.py
    └── ...
```

## Features

- **Analytical solutions** for simplified poker games
- **Numerical solvers** for computing Nash equilibria
- **Simulation tools** for verifying theoretical results
- **Comprehensive documentation** explaining game theory concepts
- **Educational examples** demonstrating optimal play

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bill Chen and Jerrod Ankenman for their excellent book
- The poker theory community for continued research and development

## Disclaimer

This is an educational project implementing toy games from poker theory. The simplified models may not directly apply to real poker situations without significant extensions and modifications.
