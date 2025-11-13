"""
Corrected implementation of the Clairvoyance Game using a cleaner approach.
"""

import numpy as np
from typing import Tuple, Dict, Optional
from scipy.optimize import linprog


class ClairvoyanceGameFixed:
    """
    The Clairvoyance Game where Y has perfect information.
    
    Game structure:
    - X has 2 strategies: Fold when Y bets, Call when Y bets  
    - Y has 4 strategies: Check Always, Bet Nuts Only, Bluff Only, Bet Always
    - Matrix is organized as payoff[x_strategy][y_strategy]
    """
    
    def __init__(self, pot_size: float = 1.0, bet_size: float = 1.0):
        self.pot_size = pot_size
        self.bet_size = bet_size
        
    def get_payoff_matrix(self) -> np.ndarray:
        """
        Get payoff matrix from X's perspective.
        Rows = X strategies [Fold, Call]
        Cols = Y strategies [Check Always, Bet Nuts Only, Bluff Only, Bet Always]
        """
        P = self.pot_size
        B = self.bet_size
        
        # Calculate expected payoffs for each combination
        payoff = np.zeros((2, 4))
        
        # X Fold strategy payoffs:
        payoff[0, 0] = 0.0    # Y checks always: showdown, EV = 0
        payoff[0, 1] = 0.0    # Y bets nuts only: 50% win at showdown vs bluff, 50% fold to nuts
        payoff[0, 2] = -P     # Y bluffs only: 50% lose at showdown vs nuts, 50% fold to bluff  
        payoff[0, 3] = -P     # Y bets always: always fold, always lose pot
        
        # X Call strategy payoffs:
        payoff[1, 0] = 0.0           # Y checks always: showdown, EV = 0
        payoff[1, 1] = -(P + B) / 2  # Y bets nuts: 50% win at showdown vs bluff, 50% call and lose to nuts
        payoff[1, 2] = (P + B) / 2   # Y bluffs: 50% lose at showdown vs nuts, 50% call and win vs bluff
        payoff[1, 3] = 0.0           # Y bets always: 50% lose to nuts, 50% win vs bluff
        
        return payoff
    
    def solve_nash_equilibrium(self) -> Dict:
        """Solve for Nash equilibrium using linear programming."""
        payoff_matrix = self.get_payoff_matrix()
        
        # This is a zero-sum game. We'll solve it as:
        # X (row player) wants to maximize their minimum expected payoff
        # Y (column player) wants to minimize X's expected payoff
        
        # Solve for X's mixed strategy first
        m, n = payoff_matrix.shape  # m=2 X strategies, n=4 Y strategies
        
        # X's problem: maximize v such that sum(payoff[i,j] * y[j]) >= v for all i
        # Variables: [v, y1, y2, y3, y4] where y[j] is probability Y plays strategy j
        c = np.zeros(n + 1)
        c[0] = -1  # maximize v (minimize -v)
        
        # Constraints: for each X strategy i: sum(payoff[i,j] * y[j]) - v >= 0
        A_ub = np.zeros((m, n + 1))
        for i in range(m):
            A_ub[i, 0] = 1      # v coefficient
            A_ub[i, 1:] = -payoff_matrix[i, :]  # -payoff coefficients
        
        b_ub = np.zeros(m)
        
        # Equality: sum of Y probabilities = 1
        A_eq = np.zeros((1, n + 1))
        A_eq[0, 1:] = 1
        b_eq = np.array([1])
        
        # Bounds: v unrestricted, probabilities >= 0
        bounds = [(None, None)] + [(0, None)] * n
        
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if not result.success:
            raise ValueError(f"Failed to solve for Y's strategy: {result.message}")
        
        game_value = result.x[0]
        y_strategy = result.x[1:]
        
        # Now solve for X's strategy using the dual
        # Y's problem: minimize w such that sum(payoff[i,j] * x[i]) <= w for all j
        c_dual = np.zeros(m + 1)
        c_dual[0] = 1  # minimize w
        
        # Constraints: for each Y strategy j: sum(payoff[i,j] * x[i]) - w <= 0  
        A_ub_dual = np.zeros((n, m + 1))
        for j in range(n):
            A_ub_dual[j, 0] = -1     # -w coefficient
            A_ub_dual[j, 1:] = payoff_matrix[:, j]  # payoff coefficients
            
        b_ub_dual = np.zeros(n)
        
        # Equality: sum of X probabilities = 1
        A_eq_dual = np.zeros((1, m + 1))
        A_eq_dual[0, 1:] = 1
        b_eq_dual = np.array([1])
        
        # Bounds: w unrestricted, probabilities >= 0
        bounds_dual = [(None, None)] + [(0, None)] * m
        
        result_dual = linprog(c_dual, A_ub=A_ub_dual, b_ub=b_ub_dual, 
                             A_eq=A_eq_dual, b_eq=b_eq_dual, bounds=bounds_dual, method='highs')
        
        if not result_dual.success:
            raise ValueError(f"Failed to solve for X's strategy: {result_dual.message}")
            
        x_strategy = result_dual.x[1:]
        
        return {
            'x_strategy': x_strategy,
            'y_strategy': y_strategy, 
            'game_value': game_value,
            'x_labels': ['Always Fold', 'Always Call'],
            'y_labels': ['Check Always', 'Bet Nuts Only', 'Bluff Only', 'Bet Always']
        }
    
    def analyze_solution(self, solution: Dict) -> str:
        """Analyze the solution and provide interpretation."""
        x_strategy = solution['x_strategy']
        y_strategy = solution['y_strategy']
        game_value = solution['game_value']
        
        analysis = []
        analysis.append("CLAIRVOYANCE GAME - NASH EQUILIBRIUM")
        analysis.append("=" * 50)
        analysis.append(f"Game Value (for X): {game_value:.4f}")
        analysis.append("")
        
        analysis.append("Player X Strategy:")
        call_prob = x_strategy[1]
        fold_prob = x_strategy[0]
        analysis.append(f"  Always Fold: {fold_prob:.4f} ({fold_prob*100:.1f}%)")
        analysis.append(f"  Always Call: {call_prob:.4f} ({call_prob*100:.1f}%)")
        analysis.append("")
        
        analysis.append("Player Y Strategy:")
        for i, (prob, label) in enumerate(zip(y_strategy, solution['y_labels'])):
            analysis.append(f"  {label}: {prob:.4f} ({prob*100:.1f}%)")
        analysis.append("")
        
        # Interpret in terms of betting frequencies
        p_nuts_bet = y_strategy[1] + y_strategy[3]    # Bet Nuts Only + Bet Always
        p_bluff_bet = y_strategy[2] + y_strategy[3]   # Bluff Only + Bet Always
        
        analysis.append("Behavioral Interpretation:")
        analysis.append(f"  X calls when Y bets: {call_prob:.4f} ({call_prob*100:.1f}%)")
        analysis.append(f"  Y bets with nuts: {p_nuts_bet:.4f} ({p_nuts_bet*100:.1f}%)")  
        analysis.append(f"  Y bets with bluffs: {p_bluff_bet:.4f} ({p_bluff_bet*100:.1f}%)")
        
        return "\n".join(analysis)


def main():
    """Test the corrected implementation."""
    game = ClairvoyanceGameFixed(pot_size=1.0, bet_size=1.0)
    
    print("Payoff Matrix (X's perspective):")
    payoff = game.get_payoff_matrix()
    print("Rows: X strategies [Fold, Call]")
    print("Cols: Y strategies [Check Always, Bet Nuts Only, Bluff Only, Bet Always]")
    print(payoff)
    print()
    
    solution = game.solve_nash_equilibrium()
    print(game.analyze_solution(solution))


if __name__ == "__main__":
    main()