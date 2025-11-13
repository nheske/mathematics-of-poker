# Mathematics of Poker

Python implementation of the toy games from [The Mathematics of Poker](https://www.amazon.com/Mathematics-Poker-Bill-Chen/dp/1886070253) by Bill Chen and Jerrod Ankenman.

## Overview

This project implements various game-theoretic models and toy games discussed in "The Mathematics of Poker", providing practical Python implementations for educational and research purposes.

10. Facing The Nemesis: Game Theory
11. One Side of the Street: Half-Street Games

12. Headsup With High Blinds: The Jam-or-Fold Game
13. Poker Made Simple: The AKQ Game
14. You Don't Have To Guess: No-Limit Bet Sizing
15. Player X Strikes Back: Full-Street Games
16. Small Bets, Big Pots: No-Fold [0,1] Games






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

```python
import mathematics_of_poker

# Example usage will be added as games are implemented
```

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
