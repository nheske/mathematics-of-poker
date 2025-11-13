"""
Chapter 10: Facing The Nemesis: Game Theory

This module implements basic game theory concepts for poker analysis.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional


class MatrixGame:
    """
    Represents a two-player zero-sum game with a payoff matrix.
    """
    
    def __init__(self, payoff_matrix: np.ndarray):
        """
        Initialize a matrix game.
        
        Args:
            payoff_matrix: Matrix where entry (i,j) is Player 1's payoff
                          when P1 plays strategy i and P2 plays strategy j
        """
        self.payoff_matrix = np.array(payoff_matrix)
        self.num_strategies_p1 = self.payoff_matrix.shape[0]
        self.num_strategies_p2 = self.payoff_matrix.shape[1]
    
    def solve_nash_equilibrium(self) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Solve for Nash equilibrium using linear programming.
        
        Returns:
            Tuple of (p1_strategy, p2_strategy, game_value)
        """
        from scipy.optimize import linprog
        
        # For Player 1 (maximizer)
        # We want to maximize v subject to:
        # sum_i p1[i] * payoff[i,j] >= v for all j
        # sum_i p1[i] = 1, p1[i] >= 0
        
        # Convert to minimization: minimize -v
        # Variables: [p1_1, p1_2, ..., p1_n, v]
        n1 = self.num_strategies_p1
        n2 = self.num_strategies_p2
        
        # Objective: minimize -v (last variable)
        c = np.zeros(n1 + 1)
        c[-1] = -1
        
        # Constraints: sum p1[i] = 1
        A_eq = np.zeros((1, n1 + 1))
        A_eq[0, :n1] = 1
        b_eq = np.array([1])
        
        # Constraints: sum_i p1[i] * payoff[i,j] >= v for all j
        # Rewrite as: -sum_i p1[i] * payoff[i,j] + v <= 0
        A_ub = np.zeros((n2, n1 + 1))
        for j in range(n2):
            A_ub[j, :n1] = -self.payoff_matrix[:, j]
            A_ub[j, -1] = 1
        b_ub = np.zeros(n2)
        
        # Bounds: p1[i] >= 0, v unbounded
        bounds = [(0, None) for _ in range(n1)] + [(None, None)]
        
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, 
                        bounds=bounds, method='highs')
        
        if result.success:
            p1_strategy = result.x[:n1]
            game_value = result.x[-1]
        else:
            raise ValueError("Failed to find Nash equilibrium")
        
        # Solve for Player 2 (minimizer) using dual
        # Variables: [p2_1, p2_2, ..., p2_m, w]
        c2 = np.zeros(n2 + 1)
        c2[-1] = 1  # maximize w (minimize -w)
        
        A_eq2 = np.zeros((1, n2 + 1))
        A_eq2[0, :n2] = 1
        b_eq2 = np.array([1])
        
        A_ub2 = np.zeros((n1, n2 + 1))
        for i in range(n1):
            A_ub2[i, :n2] = self.payoff_matrix[i, :]
            A_ub2[i, -1] = -1
        b_ub2 = np.zeros(n1)
        
        bounds2 = [(0, None) for _ in range(n2)] + [(None, None)]
        
        result2 = linprog(c2, A_ub=A_ub2, b_ub=b_ub2, A_eq=A_eq2, b_eq=b_eq2,
                         bounds=bounds2, method='highs')
        
        if result2.success:
            p2_strategy = result2.x[:n2]
        else:
            raise ValueError("Failed to find Player 2 strategy")
        
        return p1_strategy, p2_strategy, game_value
    
    def expected_value(self, p1_strategy: np.ndarray, p2_strategy: np.ndarray) -> float:
        """
        Calculate expected value for Player 1 given strategies.
        
        Args:
            p1_strategy: Probability distribution over P1's strategies
            p2_strategy: Probability distribution over P2's strategies
            
        Returns:
            Expected payoff for Player 1
        """
        return np.dot(p1_strategy, np.dot(self.payoff_matrix, p2_strategy))


def rock_paper_scissors_example():
    """
    Example: Rock-Paper-Scissors game.
    """
    print("=== Rock-Paper-Scissors ===")
    # Payoff matrix for Player 1
    # Rows: Rock, Paper, Scissors
    # Cols: Rock, Paper, Scissors
    payoff = np.array([
        [0, -1, 1],   # Rock
        [1, 0, -1],   # Paper
        [-1, 1, 0]    # Scissors
    ])
    
    game = MatrixGame(payoff)
    p1_strat, p2_strat, value = game.solve_nash_equilibrium()
    
    print(f"Player 1 Nash strategy: {p1_strat}")
    print(f"Player 2 Nash strategy: {p2_strat}")
    print(f"Game value: {value}")
    print()


def simple_poker_example():
    """
    Example: Simplified poker game.
    Player 1 has options: Bet, Check
    Player 2 (if bet) has options: Call, Fold
    """
    print("=== Simple Poker Game ===")
    # Simplified payoff matrix
    # P1: Bet (with strong hand), Bet (with weak hand - bluff), Check
    # P2: Call (with medium+ hand), Fold (with weak hand)
    
    # This is a simplified representation
    payoff = np.array([
        [2, 1],    # Bet with strong hand
        [-1, 1],   # Bet with weak hand (bluff)
        [0.5, 0.5] # Check (average outcome)
    ])
    
    game = MatrixGame(payoff)
    p1_strat, p2_strat, value = game.solve_nash_equilibrium()
    
    print(f"Player 1 strategy (Strong bet, Bluff, Check): {p1_strat}")
    print(f"Player 2 strategy (Call, Fold): {p2_strat}")
    print(f"Game value: {value}")
    print()


def exploitability_example():
    """
    Demonstrate exploitability of non-equilibrium strategies.
    """
    print("=== Exploitability Example ===")
    payoff = np.array([
        [3, 0],
        [0, 3]
    ])
    
    game = MatrixGame(payoff)
    p1_nash, p2_nash, value = game.solve_nash_equilibrium()
    
    print(f"Nash equilibrium:")
    print(f"  P1: {p1_nash}, P2: {p2_nash}, Value: {value}")
    
    # Try a non-equilibrium strategy
    p1_exploit = np.array([1.0, 0.0])  # Always play first strategy
    
    # Best response for P2
    p2_best_response = np.array([0.0, 1.0])  # Always play second strategy
    
    ev_exploited = game.expected_value(p1_exploit, p2_best_response)
    print(f"\nExploited strategy EV: {ev_exploited}")
    print(f"Nash equilibrium guaranteed EV: {value}")
    print(f"Loss from being exploited: {value - ev_exploited}")
    print()


def main():
    """
    Run examples demonstrating game theory concepts.
    """
    print("Chapter 10: Game Theory Examples\n")
    print("=" * 50)
    print()
    
    rock_paper_scissors_example()
    simple_poker_example()
    exploitability_example()
    
    print("=" * 50)
    print("\nKey Takeaways:")
    print("1. Nash equilibrium provides unexploitable strategies")
    print("2. Mixed strategies are often necessary")
    print("3. Deviating from equilibrium can be exploited")
    print("4. Game value represents guaranteed expected outcome")


if __name__ == "__main__":
    main()
