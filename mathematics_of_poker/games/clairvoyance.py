"""
Implementation of the Clairvoyance Game from Example 11.1 of The Mathematics of Poker.

Game Description:
- One half-street game
- Pot size of P bets
- Limit betting
- Y is clairvoyant (knows both hands)
- Y's concealed hand is drawn randomly: 50% hands that beat X's hand, 50% that don't
- X checks in the dark
- Y can check or bet
- If Y bets, X can call or fold
- If Y checks, there is a showdown
"""

import numpy as np
from typing import Tuple, Dict
from .half_street import HalfStreetGame


class ClairvoyanceGame(HalfStreetGame):
    """
    The Clairvoyance Game where Y has perfect information.
    
    In this game:
    - X has one decision: call or fold when Y bets
    - Y has two decisions based on hand strength:
      - With winning hands: check or bet (value bet)
      - With losing hands: check or bet (bluff)
    
    Since Y acts with perfect information, we model this as Y choosing:
    1. Probability of betting with winning hands
    2. Probability of betting with losing hands
    
    X chooses:
    1. Probability of calling when Y bets
    """
    
    def __init__(self, pot_size: float = 1.0, bet_size: float = 1.0):
        """
        Initialize the Clairvoyance Game.
        
        Args:
            pot_size: Initial pot size (default 1.0)
            bet_size: Size of Y's bet (default 1.0)
        """
        super().__init__(pot_size)
        self.bet_size = bet_size
    
    def get_payoff_matrix(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate payoff matrices for the Clairvoyance Game.
        
        X's strategies: [Fold when Y bets, Call when Y bets]
        Y's strategies: [Check always, Bet nuts only, Bluff only, Bet always]
        
        Returns:
            Tuple of (payoff_matrix_x, payoff_matrix_y)
        """
        P = self.pot_size
        B = self.bet_size
        
        # Payoff matrix for X (rows = X strategies, cols = Y strategies)
        # X strategies: [Always Fold, Always Call]
        # Y strategies: [Check Always, Bet Nuts Only, Bluff Only, Bet Always]
        
        payoff_x = np.zeros((2, 4))
        
        # When X always folds:
        payoff_x[0, 0] = 0.0      # Y checks always: showdown, X wins 50% of time: 0.5 * P - 0.5 * P = 0
        payoff_x[0, 1] = -P/2     # Y bets nuts only: X folds to nuts (50% of time), wins showdown vs bluffs (50%): 0.5 * (-P) + 0.5 * 0 = -P/2
        payoff_x[0, 2] = P/2      # Y bluffs only: X folds to bluffs (50%), wins vs nuts at showdown (50%): 0.5 * (-P) + 0.5 * 0 = P/2
        payoff_x[0, 3] = -P/2     # Y bets always: X always folds, loses P when Y has nuts, loses P when Y bluffs: -P
        
        # When X always calls:
        payoff_x[1, 0] = 0.0      # Y checks always: showdown, expected value = 0
        payoff_x[1, 1] = -B/2     # Y bets nuts only: call and lose to nuts 50%, win at showdown 50%: 0.5 * (-P-B) + 0.5 * 0 = -(P+B)/2
        payoff_x[1, 2] = B/2      # Y bluffs only: call and win vs bluffs 50%, lose at showdown 50%: 0.5 * (P+B) + 0.5 * 0 = (P+B)/2
        payoff_x[1, 3] = 0.0      # Y bets always: 0.5 * (-(P+B)) + 0.5 * (P+B) = 0
        
        # Recalculating more carefully:
        # Scenario analysis:
        # Y has nuts (50% of time): beats X's hand
        # Y has bluff (50% of time): loses to X's hand
        
        # X Always Folds when Y bets:
        payoff_x[0, 0] = 0.0                           # Check always: 0.5*P - 0.5*P = 0 (showdown)
        payoff_x[0, 1] = 0.5 * (-P) + 0.5 * 0         # Bet nuts only: fold to nuts, showdown vs bluff
        payoff_x[0, 2] = 0.5 * 0 + 0.5 * (-P)         # Bluff only: showdown vs nuts, fold to bluff  
        payoff_x[0, 3] = 0.5 * (-P) + 0.5 * (-P)      # Bet always: fold to both
        
        # X Always Calls when Y bets:
        payoff_x[1, 0] = 0.0                                    # Check always: showdown
        payoff_x[1, 1] = 0.5 * (-(P + B)) + 0.5 * 0           # Bet nuts only: call and lose to nuts, showdown vs bluff
        payoff_x[1, 2] = 0.5 * 0 + 0.5 * (P + B)              # Bluff only: showdown vs nuts, call and win vs bluff
        payoff_x[1, 3] = 0.5 * (-(P + B)) + 0.5 * (P + B)     # Bet always: call both
        
        # Simplify:
        payoff_x[0, 1] = -P/2
        payoff_x[0, 2] = -P/2  
        payoff_x[0, 3] = -P
        
        payoff_x[1, 1] = -(P + B)/2
        payoff_x[1, 2] = (P + B)/2
        payoff_x[1, 3] = 0
        
        # Y's payoff is negative of X's payoff (zero-sum game)
        payoff_y = -payoff_x
        
        return payoff_x, payoff_y
    
    def get_strategy_labels(self) -> Tuple[list, list]:
        """Get human-readable labels for strategies."""
        x_labels = ["Always Fold", "Always Call"]
        y_labels = ["Check Always", "Bet Nuts Only", "Bluff Only", "Bet Always"]
        return x_labels, y_labels
    
    def get_mixed_strategy_interpretation(self, solution: Dict) -> str:
        """
        Interpret the mixed strategies in terms of the original game decisions.
        
        Args:
            solution: Dictionary returned by solve_nash_equilibrium()
            
        Returns:
            String with detailed interpretation
        """
        x_strategy = solution['x_strategy']
        y_strategy = solution['y_strategy']
        
        # X's calling frequency  
        call_freq = x_strategy[1] if len(x_strategy) >= 2 else 0
        
        # Y's betting frequencies need to be interpreted
        # Y strategies: [Check Always, Bet Nuts Only, Bluff Only, Bet Always]
        # Convert to betting frequencies for nuts and bluffs
        
        # If we think of Y's strategy as a combination:
        # Let p_nuts = probability of betting with nuts
        # Let p_bluff = probability of betting with bluffs
        
        # Then the pure strategies correspond to:
        # Check Always: p_nuts = 0, p_bluff = 0
        # Bet Nuts Only: p_nuts = 1, p_bluff = 0  
        # Bluff Only: p_nuts = 0, p_bluff = 1
        # Bet Always: p_nuts = 1, p_bluff = 1
        
        # The mixed strategy gives us a distribution over these four options
        # We can calculate the implied betting frequencies:
        
        if len(y_strategy) >= 4:
            p_nuts = y_strategy[1] + y_strategy[3]    # Bet Nuts Only + Bet Always
            p_bluff = y_strategy[2] + y_strategy[3]   # Bluff Only + Bet Always
        else:
            # If we only have 2 Y strategies from the solver, interpret them differently
            # This means the solver found that only 2 of Y's 4 strategies are used
            p_nuts = y_strategy[1] if len(y_strategy) >= 2 else 0  # Assume second strategy is betting nuts
            p_bluff = 0  # No bluffing in optimal strategy
        
        interpretation = []
        interpretation.append("STRATEGY INTERPRETATION")
        interpretation.append("=" * 40)
        interpretation.append(f"X calls when Y bets: {call_freq:.4f} ({call_freq*100:.1f}%)")
        interpretation.append(f"Y bets with winning hands: {p_nuts:.4f} ({p_nuts*100:.1f}%)")
        interpretation.append(f"Y bets with losing hands (bluffs): {p_bluff:.4f} ({p_bluff*100:.1f}%)")
        interpretation.append("")
        interpretation.append("Expected outcomes when Y has a winning hand:")
        interpretation.append(f"  Checks and wins at showdown: {(1-p_nuts)*100:.1f}%")
        interpretation.append(f"  Bets, X folds: {p_nuts*(1-call_freq)*100:.1f}%")
        interpretation.append(f"  Bets, X calls and loses: {p_nuts*call_freq*100:.1f}%")
        interpretation.append("")
        interpretation.append("Expected outcomes when Y has a losing hand:")
        interpretation.append(f"  Checks and loses at showdown: {(1-p_bluff)*100:.1f}%")
        interpretation.append(f"  Bluffs, X folds: {p_bluff*(1-call_freq)*100:.1f}%")
        interpretation.append(f"  Bluffs, X calls and wins: {p_bluff*call_freq*100:.1f}%")
        
        return "\n".join(interpretation)
    
    def verify_equilibrium(self, solution: Dict, tolerance: float = 1e-6) -> bool:
        """
        Verify that the solution is indeed a Nash equilibrium.
        
        Args:
            solution: Dictionary returned by solve_nash_equilibrium()
            tolerance: Numerical tolerance for verification
            
        Returns:
            True if solution is a valid Nash equilibrium
        """
        x_strategy = solution['x_strategy']
        y_strategy = solution['y_strategy']
        payoff_x, payoff_y = self.get_payoff_matrix()
        
        # Calculate expected payoffs for each pure strategy
        x_payoffs = payoff_x @ y_strategy
        y_payoffs = x_strategy @ payoff_y
        
        # In equilibrium, all strategies with positive probability should have equal payoff
        # and no unused strategy should have higher payoff
        
        max_x_payoff = np.max(x_payoffs)
        max_y_payoff = np.max(y_payoffs)
        
        # Check X's strategies
        for i, prob in enumerate(x_strategy):
            if prob > tolerance:
                if abs(x_payoffs[i] - max_x_payoff) > tolerance:
                    return False
            else:
                if x_payoffs[i] > max_x_payoff + tolerance:
                    return False
        
        # Check Y's strategies  
        for i, prob in enumerate(y_strategy):
            if prob > tolerance:
                if abs(y_payoffs[i] - max_y_payoff) > tolerance:
                    return False
            else:
                if y_payoffs[i] > max_y_payoff + tolerance:
                    return False
        
        return True