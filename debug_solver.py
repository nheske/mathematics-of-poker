#!/usr/bin/env python3
"""
Debug script for the Clairvoyance Game solver.
"""

import sys
import os
import numpy as np

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.clairvoyance import ClairvoyanceGame


def main():
    """Debug the Clairvoyance Game solver."""
    
    game = ClairvoyanceGame(pot_size=1.0, bet_size=1.0)
    
    # Get payoff matrices
    payoff_x, payoff_y = game.get_payoff_matrix()
    print("Payoff matrix for Y (what we're solving):")
    print(payoff_y)
    print("Shape:", payoff_y.shape)
    print()
    
    # Try to solve manually
    try:
        from scipy.optimize import linprog
        print("Using scipy linear programming...")
        
        # Solve for X (column player, minimizing Y's payoff)
        m, n = payoff_y.shape
        print(f"Matrix dimensions: {m} rows (Y strategies), {n} cols (X strategies)")
        
        # Add constant to make payoffs positive
        min_payoff = np.min(payoff_y)
        print(f"Min payoff: {min_payoff}")
        
        if min_payoff <= 0:
            adjusted_matrix = payoff_y - min_payoff + 1
        else:
            adjusted_matrix = payoff_y
            
        print("Adjusted matrix:")
        print(adjusted_matrix)
        print()
        
        # Set up linear program for X (column player)
        c = np.zeros(n + 1)
        c[-1] = -1  # minimize v
        
        # Constraints: for each Y strategy i, sum(A[i,j] * x[j]) >= v
        A_ub = np.zeros((m, n + 1))
        for i in range(m):
            A_ub[i, :n] = -adjusted_matrix[i, :]  
            A_ub[i, -1] = 1
        
        b_ub = np.zeros(m)
        
        # Equality: sum of probabilities = 1
        A_eq = np.zeros((1, n + 1))
        A_eq[0, :n] = 1
        b_eq = np.array([1])
        
        bounds = [(0, None)] * n + [(None, None)]
        
        print("Linear program setup:")
        print("c:", c)
        print("A_ub:", A_ub)
        print("b_ub:", b_ub)
        print("A_eq:", A_eq)
        print("b_eq:", b_eq)
        print()
        
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        print("Solver result:", result)
        
        if result.success:
            x_strategy = result.x[:n]
            game_value = result.x[-1]
            print(f"X strategy: {x_strategy}")
            print(f"Game value (adjusted): {game_value}")
            
            # Convert back
            if min_payoff <= 0:
                actual_game_value = game_value + min_payoff - 1
            else:
                actual_game_value = game_value
            print(f"Actual game value: {actual_game_value}")
            
    except Exception as e:
        print(f"Error with scipy: {e}")
        
    # Test the full solver
    print("\n" + "="*50)
    print("Testing full solver:")
    solution = game.solve_nash_equilibrium()
    print("X strategy:", solution['x_strategy'])
    print("Y strategy:", solution['y_strategy']) 
    print("Game value:", solution['game_value'])


if __name__ == "__main__":
    main()