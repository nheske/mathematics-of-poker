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
    
    def solve_nash_equilibrium(self) -> Dict:
        """
        Solve for the Nash equilibrium mixed strategies.
        
        Returns:
            Dictionary containing optimal strategies and game value
        """
        payoff_x, payoff_y = self.get_payoff_matrix()
        
        # For zero-sum games, we can solve using linear programming
        # Player Y maximizes their payoff, Player X minimizes Y's payoff
        # Standard format: rows = strategies for row player (Y), cols = strategies for col player (X)
        # Our matrix has rows = X strategies, cols = Y strategies, so we transpose
        optimal_x, optimal_y, game_value = self._solve_zero_sum_game(payoff_y.T)
        
        return {
            'x_strategy': optimal_x,
            'y_strategy': optimal_y,
            'game_value': game_value,
            'x_labels': self.get_strategy_labels()[0],
            'y_labels': self.get_strategy_labels()[1]
        }

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
            'x_strategy': optimal_x,
            'y_strategy': optimal_y,
            'game_value': game_value,
            'x_labels': self.get_strategy_labels()[0],
            'y_labels': self.get_strategy_labels()[1],
            'iterations': iterations,
        }
    
    def _solve_zero_sum_game(self, payoff_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Solve a zero-sum game using linear programming approach.
        
        Args:
            payoff_matrix: Payoff matrix for the row player (Y in our case)
            
        Returns:
            Tuple of (row_strategy, col_strategy, game_value)
        """
        try:
            from scipy.optimize import linprog
        except ImportError:
            # Fallback to iterative method if scipy not available
            return self._solve_iterative(payoff_matrix)
        
        # Solve for column player (X) first - they want to minimize row player's payoff
        m, n = payoff_matrix.shape

        c = np.zeros(n + 1)
        c[-1] = 1.0  # Minimise the maximal row payoff v

        A_ub = np.zeros((m, n + 1))
        A_ub[:, :n] = payoff_matrix
        A_ub[:, -1] = -1.0
        b_ub = np.zeros(m)

        A_eq = np.zeros((1, n + 1))
        A_eq[0, :n] = 1.0
        b_eq = np.array([1.0])

        bounds = [(0, None)] * n + [(None, None)]

        result = linprog(
            c,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method="highs",
        )

        if not result.success:
            return self._solve_iterative(payoff_matrix)

        x_strategy = result.x[:n]
        row_value = result.x[-1]

        # Solve for row player (Y) using the dual formulation
        c_y = np.zeros(m + 1)
        c_y[-1] = -1.0  # Maximise row payoff -> minimise -w

        A_ub_y = np.zeros((n, m + 1))
        A_ub_y[:, :m] = -payoff_matrix.T
        A_ub_y[:, -1] = 1.0
        b_ub_y = np.zeros(n)

        A_eq_y = np.zeros((1, m + 1))
        A_eq_y[0, :m] = 1.0
        b_eq_y = np.array([1.0])

        bounds_y = [(0, None)] * m + [(None, None)]

        result_y = linprog(
            c_y,
            A_ub=A_ub_y,
            b_ub=b_ub_y,
            A_eq=A_eq_y,
            b_eq=b_eq_y,
            bounds=bounds_y,
            method="highs",
        )

        if not result_y.success:
            y_strategy = np.ones(m) / m
        else:
            y_strategy = result_y.x[:m]

        game_value = -row_value  # convert to column player's perspective

        return self._normalise_strategy(x_strategy), self._normalise_strategy(y_strategy), game_value
    
    def _solve_iterative(self, payoff_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Fallback iterative method for solving zero-sum games.
        Uses fictitious play approximation.
        """
        m, n = payoff_matrix.shape
        
        # Initialize uniform strategies
        x_strategy = np.ones(n) / n
        y_strategy = np.ones(m) / m
        
        # Fictitious play for approximation
        iterations = 1000
        x_cumulative = np.zeros(n)
        y_cumulative = np.zeros(m)
        
        for t in range(iterations):
            # Y's best response to current X strategy
            y_payoffs = payoff_matrix @ x_strategy
            best_y = np.argmax(y_payoffs)
            y_cumulative[best_y] += 1
            
            # X's best response to current Y strategy
            x_payoffs = y_strategy @ payoff_matrix
            best_x = np.argmin(x_payoffs)  # X wants to minimize Y's payoff
            x_cumulative[best_x] += 1
            
            # Update mixed strategies
            y_strategy = y_cumulative / (t + 1)
            x_strategy = x_cumulative / (t + 1)
        
        # Calculate game value
        game_value = float(y_strategy @ payoff_matrix @ x_strategy)
        
        return x_strategy, y_strategy, game_value

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
        x_strategy = solution['x_strategy']
        y_strategy = solution['y_strategy']
        x_labels = solution['x_labels']
        y_labels = solution['y_labels']
        game_value = solution['game_value']
        
        analysis = []
        analysis.append("OPTIMAL STRATEGIES")
        analysis.append("=" * 50)
        analysis.append(f"Game Value: {game_value:.4f}")
        analysis.append("")
        
        analysis.append("Player X (First Player) Strategy:")
        for i, (label, prob) in enumerate(zip(x_labels, x_strategy)):
            if prob > 0.001:  # Only show strategies with significant probability
                analysis.append(f"  {label}: {prob:.4f} ({prob*100:.1f}%)")
        analysis.append("")
        
        analysis.append("Player Y (Second Player) Strategy:")
        for i, (label, prob) in enumerate(zip(y_labels, y_strategy)):
            if prob > 0.001:  # Only show strategies with significant probability
                analysis.append(f"  {label}: {prob:.4f} ({prob*100:.1f}%)")
        
        return "\n".join(analysis)