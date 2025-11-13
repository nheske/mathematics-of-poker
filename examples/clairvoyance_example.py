#!/usr/bin/env python3
"""
Example script demonstrating the Clairvoyance Game solver.

This script solves Example 11.1 from The Mathematics of Poker and shows
the optimal mixed strategies for both players.
"""

import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.clairvoyance import ClairvoyanceGame


def main():
    """Demonstrate the Clairvoyance Game solver."""
    
    print("THE MATHEMATICS OF POKER - EXAMPLE 11.1")
    print("The Clairvoyance Game")
    print("=" * 60)
    print()
    
    # Create the game with default parameters (pot size = 1, bet size = 1)
    game = ClairvoyanceGame(pot_size=1.0, bet_size=1.0)
    
    print("Game Setup:")
    print(f"- Initial pot size: {game.pot_size}")
    print(f"- Bet size: {game.bet_size}")
    print("- Y is clairvoyant (knows both hands)")
    print("- Y's hand beats X's hand 50% of the time")
    print("- X checks in the dark")
    print("- Y can check or bet")
    print("- If Y bets, X can call or fold")
    print()
    
    # Show the payoff matrices
    payoff_x, payoff_y = game.get_payoff_matrix()
    x_labels, y_labels = game.get_strategy_labels()
    
    print("Payoff Matrix for Player X:")
    print("Strategies:", x_labels)
    print("Y Strategies:", y_labels)
    print(payoff_x)
    print()
    
    print("Payoff Matrix for Player Y:")
    print(payoff_y)
    print()
    
    # Solve for Nash equilibrium
    print("Solving for Nash Equilibrium...")
    solution = game.solve_nash_equilibrium()
    
    # Display the solution
    print(game.analyze_strategies(solution))
    print()
    
    # Show the interpretation
    print(game.get_mixed_strategy_interpretation(solution))
    print()
    
    # Verify it's a valid equilibrium
    is_equilibrium = game.verify_equilibrium(solution)
    print(f"Equilibrium verification: {'PASSED' if is_equilibrium else 'FAILED'}")
    print()
    
    # Show some game theory insights
    print("GAME THEORY INSIGHTS")
    print("=" * 30)
    print("This game demonstrates several key concepts:")
    print("1. The value of information - Y's clairvoyance gives them an advantage")
    print("2. Mixed strategies arise naturally in adversarial settings")
    print("3. Bluffing frequency must be balanced with value betting")
    print("4. Calling frequency must balance between being exploited by bluffs vs value bets")
    print()
    
    # Test different pot and bet sizes
    print("SENSITIVITY ANALYSIS")
    print("=" * 25)
    print("How do optimal strategies change with different bet sizes?")
    print()
    
    for bet_size in [0.5, 1.0, 2.0]:
        print(f"Bet size: {bet_size}")
        test_game = ClairvoyanceGame(pot_size=1.0, bet_size=bet_size)
        test_solution = test_game.solve_nash_equilibrium()
        
        call_freq = test_solution['x_strategy'][1]
        y_strategy = test_solution['y_strategy']
        p_nuts = y_strategy[1] + y_strategy[3]    # Bet with nuts
        p_bluff = y_strategy[2] + y_strategy[3]   # Bet with bluffs
        
        print(f"  X calling frequency: {call_freq:.3f}")
        print(f"  Y value betting frequency: {p_nuts:.3f}")
        print(f"  Y bluffing frequency: {p_bluff:.3f}")
        print(f"  Game value: {test_solution['game_value']:.4f}")
        print()


if __name__ == "__main__":
    main()