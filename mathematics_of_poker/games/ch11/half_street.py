"""
Half-street poker games implementation.

Half-street games have the following characteristics:
- The first player (X) checks in the dark
- The second player (Y) can either check or bet some amount
- If Y bets, X can call (showdown) or fold (if allowed)
- If Y checks, there is a showdown
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
import numpy as np


class HalfStreetGame(ABC):
    """Base class for half-street poker games."""

    def __init__(self, pot_size: float = 1.0):
        """
        Initialize a half-street game.

        Args:
            pot_size: The initial pot size (in betting units)
        """
        self.pot_size = pot_size

    @abstractmethod
    def get_payoff_matrix(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the payoff matrices for both players.

        Returns:
            Tuple of (payoff_matrix_x, payoff_matrix_y) where each matrix
            has shape (x_strategies, y_strategies)
        """
        pass

    @abstractmethod
    def get_strategy_labels(self) -> Tuple[list, list]:
        """
        Get human-readable labels for each player's strategies.

        Returns:
            Tuple of (x_strategy_labels, y_strategy_labels)
        """
        pass

    @abstractmethod
    def solve_nash_equilibrium(self) -> Dict:
        """Return the analytic Nash equilibrium for the concrete game."""
        raise NotImplementedError

    def solve_cfr_equilibrium(self, iterations: int = 10000, seed: Optional[int] = None) -> Dict:
        """Approximate the Nash equilibrium using regret-matching CFR.

        Args:
            iterations: Number of regret-matching iterations to run.
            seed: Optional random seed for reproducibility when tie-breaking is required.

        Returns:
            Dictionary containing approximate strategies and game value.
        """
        payoff_x, payoff_y = self.get_payoff_matrix()
        optimal_x, optimal_y, game_value = self._solve_regret_matching(
            payoff_y.T, iterations=iterations, seed=seed
        )

        return {
            "x_strategy": optimal_x,
            "y_strategy": optimal_y,
            "game_value": game_value,
            "x_labels": self.get_strategy_labels()[0],
            "y_labels": self.get_strategy_labels()[1],
            "iterations": iterations,
        }

    def _solve_regret_matching(
        self,
        payoff_matrix: np.ndarray,
        iterations: int = 10000,
        seed: Optional[int] = None,
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """Solve a zero-sum game using regret-matching (CFR for normal-form games).

        Args:
            payoff_matrix: Payoff matrix for the row player (Y).
            iterations: Number of regret updates to perform.
            seed: Optional random seed to stabilise tie-breaking.

        Returns:
            Tuple of (column_strategy, row_strategy, game_value).
        """

        if iterations <= 0:
            raise ValueError("iterations must be positive")

        rng = np.random.default_rng(seed)

        m, n = payoff_matrix.shape
        regrets_row = np.zeros(m)
        regrets_col = np.zeros(n)
        strategy_sum_row = np.zeros(m)
        strategy_sum_col = np.zeros(n)

        # Start with uniform strategies
        strategy_row = np.ones(m) / m
        strategy_col = np.ones(n) / n

        for _ in range(iterations):
            strategy_sum_row += strategy_row
            strategy_sum_col += strategy_col

            row_payoffs = payoff_matrix @ strategy_col  # payoff per row action
            col_payoffs = -payoff_matrix.T @ strategy_row  # payoff per column action

            utility_row = row_payoffs @ strategy_row
            utility_col = col_payoffs @ strategy_col

            regrets_row += row_payoffs - utility_row
            regrets_col += col_payoffs - utility_col

            strategy_row = self._regrets_to_strategy(regrets_row, rng)
            strategy_col = self._regrets_to_strategy(regrets_col, rng)

        avg_row = strategy_sum_row / iterations
        avg_col = strategy_sum_col / iterations

        avg_row = self._normalise_strategy(avg_row)
        avg_col = self._normalise_strategy(avg_col)

        game_value = float(avg_row @ payoff_matrix @ avg_col)

        return avg_col, avg_row, game_value

    @staticmethod
    def _regrets_to_strategy(regrets: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        positive = np.maximum(regrets, 0.0)
        total = positive.sum()
        if total > 0:
            return positive / total
        # All regrets non-positive: fall back to uniform with minimal random noise
        uniform = np.ones_like(regrets) / len(regrets)
        if rng is None:
            return uniform
        noise = rng.random(len(regrets)) * 1e-9
        return HalfStreetGame._normalise_strategy(uniform + noise)

    @staticmethod
    def _normalise_strategy(strategy: np.ndarray) -> np.ndarray:
        total = strategy.sum()
        if total <= 0:
            return np.ones_like(strategy) / len(strategy)
        return strategy / total

    def analyze_strategies(self, solution: Dict) -> str:
        """
        Provide human-readable analysis of the optimal strategies.

        Args:
            solution: Dictionary returned by solve_nash_equilibrium()

        Returns:
            String containing strategy analysis
        """
        x_strategy = solution["x_strategy"]
        y_strategy = solution["y_strategy"]
        x_labels = solution["x_labels"]
        y_labels = solution["y_labels"]
        game_value = solution["game_value"]

        analysis = []
        analysis.append("OPTIMAL STRATEGIES")
        analysis.append("=" * 50)
        analysis.append(f"Game Value: {game_value:.4f}")
        analysis.append("")

        analysis.append("Player X (First Player) Strategy:")
        for label, prob in zip(x_labels, x_strategy):
            if prob > 0.001:  # Only show strategies with significant probability
                analysis.append(f"  {label}: {prob:.4f} ({prob*100:.1f}%)")
        analysis.append("")

        analysis.append("Player Y (Second Player) Strategy:")
        for label, prob in zip(y_labels, y_strategy):
            if prob > 0.001:  # Only show strategies with significant probability
                analysis.append(f"  {label}: {prob:.4f} ({prob*100:.1f}%)")

        return "\n".join(analysis)
