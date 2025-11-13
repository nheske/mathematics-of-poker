"""
Chapter 14: You Don't Have To Guess: No-Limit Bet Sizing

This module explores optimal bet sizing in no-limit poker games.
"""

import numpy as np
from typing import List, Tuple, Callable
import matplotlib.pyplot as plt


class NoLimitBettingGame:
    """
    A simplified no-limit betting game with continuous bet sizing.
    """
    
    def __init__(self, pot_size: float = 1.0):
        """
        Initialize no-limit betting game.
        
        Args:
            pot_size: Initial pot size
        """
        self.pot_size = pot_size
    
    def optimal_bet_size_value(self, hand_strength: float, 
                                opponent_call_function: Callable[[float, float], float]) -> float:
        """
        Find optimal bet size for a value bet.
        
        Args:
            hand_strength: Our hand strength [0, 1]
            opponent_call_function: Function(bet_size, hand) -> probability of call
            
        Returns:
            Optimal bet size
        """
        # Grid search over bet sizes
        bet_sizes = np.linspace(0.1, 5.0, 100) * self.pot_size
        best_ev = -np.inf
        best_bet = 0
        
        for bet in bet_sizes:
            ev = self._ev_value_bet(hand_strength, bet, opponent_call_function)
            if ev > best_ev:
                best_ev = ev
                best_bet = bet
        
        return best_bet
    
    def _ev_value_bet(self, hand: float, bet_size: float,
                      opponent_call_function: Callable[[float, float], float]) -> float:
        """
        Calculate EV of a value bet.
        """
        # Sample opponent's calling distribution
        prob_call = opponent_call_function(bet_size, hand)
        
        # Assume when called, we win with probability equal to our hand strength
        # (simplified model)
        prob_win_if_called = hand
        
        ev = prob_call * (prob_win_if_called * (self.pot_size + bet_size) - 
                         (1 - prob_win_if_called) * bet_size) + \
             (1 - prob_call) * self.pot_size
        
        return ev
    
    def pot_odds_calling_threshold(self, bet_size: float) -> float:
        """
        Calculate minimum hand strength needed to call based on pot odds.
        
        Args:
            bet_size: Size of the bet to call
            
        Returns:
            Minimum hand strength to call
        """
        # Pot odds = bet / (pot + 2*bet)
        # Need equity >= pot odds
        pot_odds = bet_size / (self.pot_size + 2 * bet_size)
        return pot_odds


class PolarizedBettingStrategy:
    """
    Models a polarized betting strategy with nuts and bluffs.
    """
    
    def __init__(self, pot_size: float = 1.0):
        self.pot_size = pot_size
    
    def optimal_bluff_frequency(self, bet_size: float) -> float:
        """
        Calculate optimal bluffing frequency for a given bet size.
        
        The optimal bluffing ratio follows the pot odds formula:
        bluffs / value_bets = pot_size / bet_size
        
        Or as a frequency: bluff_freq = pot_size / (pot_size + bet_size)
        
        Args:
            bet_size: Size of the bet
            
        Returns:
            Optimal bluffing frequency
        """
        # Bluff frequency that makes opponent indifferent
        # Opponent needs: prob_bluff * pot = (1-prob_bluff) * (-bet)
        # Solving: prob_bluff = bet / (pot + bet)
        
        return bet_size / (self.pot_size + bet_size)
    
    def bluff_to_value_ratio(self, bet_size: float) -> float:
        """
        Calculate optimal bluff-to-value ratio.
        
        Args:
            bet_size: Size of the bet
            
        Returns:
            Ratio of bluffs to value bets
        """
        return self.pot_size / bet_size


class GeometricBetting:
    """
    Analyzes geometric bet sizing across multiple streets.
    """
    
    def __init__(self, starting_pot: float, starting_stack: float, num_streets: int = 3):
        """
        Initialize geometric betting analyzer.
        
        Args:
            starting_pot: Initial pot size
            starting_stack: Stack size
            num_streets: Number of betting streets
        """
        self.starting_pot = starting_pot
        self.starting_stack = starting_stack
        self.num_streets = num_streets
    
    def calculate_geometric_size(self) -> float:
        """
        Calculate the geometric bet size that allows all-in by final street.
        
        Returns:
            Bet size as fraction of pot
        """
        # If we bet x*pot on each street, after n streets we've bet:
        # total_bet = x*pot + x*(1+2x)*pot + x*(1+2x+2x(1+2x))*pot + ...
        # We want this to equal the starting stack
        
        # For geometric sizing, bet size b such that:
        # b * (1 + b)^(n-1) = stack
        
        # Simplified: solve b where b, b*(pot+2b)/pot, etc. equals stack
        # Iterative solution
        
        for bet_frac in np.linspace(0.1, 2.0, 100):
            pot = self.starting_pot
            total_bet = 0
            
            for street in range(self.num_streets):
                bet = bet_frac * pot
                total_bet += bet
                pot = pot + 2 * bet
            
            if abs(total_bet - self.starting_stack) < 0.01:
                return bet_frac
        
        return 1.0  # Default to pot-sized bets


def demonstrate_bet_sizing_effect():
    """
    Demonstrate how bet sizing affects calling ranges.
    """
    print("=== Bet Sizing and Calling Ranges ===")
    print()
    
    game = NoLimitBettingGame(pot_size=1.0)
    
    bet_sizes_frac = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
    
    print("Pot Size: 1.0")
    print()
    print("Bet (×Pot) | Bet Amount | Pot Odds | Min Equity to Call")
    print("-" * 60)
    
    for frac in bet_sizes_frac:
        bet = frac * game.pot_size
        pot_odds = bet / (game.pot_size + 2 * bet)
        min_equity = game.pot_odds_calling_threshold(bet)
        
        print(f"{frac:10.2f} | {bet:10.2f} | {pot_odds:8.1%} | {min_equity:18.1%}")
    
    print()
    print("Observations:")
    print("- Larger bets require more equity to call")
    print("- Pot odds determine minimum calling threshold")
    print("- Small bets make calling easy, large bets make it difficult")
    print()


def demonstrate_bluffing_frequencies():
    """
    Demonstrate optimal bluffing frequencies for different bet sizes.
    """
    print("=== Optimal Bluffing Frequencies ===")
    print()
    
    strategy = PolarizedBettingStrategy(pot_size=1.0)
    
    bet_sizes_frac = [0.33, 0.5, 0.75, 1.0, 1.5, 2.0]
    
    print("Pot Size: 1.0")
    print()
    print("Bet (×Pot) | Bet Amount | Bluff Freq | Bluff:Value Ratio")
    print("-" * 65)
    
    for frac in bet_sizes_frac:
        bet = frac * strategy.pot_size
        bluff_freq = strategy.optimal_bluff_frequency(bet)
        bluff_ratio = strategy.bluff_to_value_ratio(bet)
        
        print(f"{frac:10.2f} | {bet:10.2f} | {bluff_freq:10.1%} | {bluff_ratio:17.3f}")
    
    print()
    print("Key Insights:")
    print("- Larger bets require fewer bluffs")
    print("- Bluff-to-value ratio = pot_size / bet_size")
    print("- This keeps opponent indifferent between calling and folding")
    print()


def demonstrate_geometric_betting():
    """
    Demonstrate geometric bet sizing across multiple streets.
    """
    print("=== Geometric Bet Sizing ===")
    print()
    
    starting_pot = 1.0
    starting_stack = 10.0
    
    for num_streets in [1, 2, 3]:
        geo = GeometricBetting(starting_pot, starting_stack, num_streets)
        bet_frac = geo.calculate_geometric_size()
        
        print(f"Streets: {num_streets}, Starting Pot: {starting_pot}, Stack: {starting_stack}")
        print(f"Geometric bet size: {bet_frac:.3f}×pot")
        
        # Show progression
        pot = starting_pot
        total_bet = 0
        
        for street in range(num_streets):
            bet = bet_frac * pot
            total_bet += bet
            print(f"  Street {street+1}: Bet {bet:.3f} (into pot of {pot:.3f})")
            pot = pot + 2 * bet
        
        print(f"  Total bet: {total_bet:.3f}, Final pot: {pot:.3f}")
        print()


def analyze_bet_sizing_vs_range():
    """
    Analyze relationship between bet sizing and range composition.
    """
    print("=== Bet Sizing and Range Polarization ===")
    print()
    
    print("General Principles:")
    print()
    print("1. Small Bets (< 0.5×pot):")
    print("   - Can include more medium-strength hands")
    print("   - Less polarized ranges")
    print("   - Easier for opponent to call")
    print("   - Better for thin value and protection")
    print()
    
    print("2. Medium Bets (0.5-1.0×pot):")
    print("   - Balanced between value and bluffs")
    print("   - Standard sizing for many situations")
    print("   - Moderate polarization")
    print()
    
    print("3. Large Bets (> 1.0×pot):")
    print("   - Highly polarized (nuts or bluffs)")
    print("   - Difficult for opponent to call")
    print("   - Requires fewer bluffs")
    print("   - Maximum pressure on opponent")
    print()
    
    print("4. Overbet (> 2.0×pot):")
    print("   - Extremely polarized")
    print("   - Very few bluffs needed")
    print("   - Used with very strong hands or as exploitative bluffs")
    print()


def compare_exploitative_vs_gto():
    """
    Compare GTO bet sizing with exploitative adjustments.
    """
    print("=== GTO vs Exploitative Bet Sizing ===")
    print()
    
    print("GTO Approach:")
    print("- Choose bet size based on range composition")
    print("- Balance bluffs according to pot odds formula")
    print("- Cannot be exploited by perfect opponent")
    print()
    
    print("Exploitative Adjustments:")
    print()
    print("Against Calling Station:")
    print("  - Bet larger with value hands (they'll call anyway)")
    print("  - Bluff less (they call too much)")
    print("  - Focus on thin value betting")
    print()
    
    print("Against Tight Player:")
    print("  - Bluff more frequently (they fold too much)")
    print("  - Can use smaller bet sizes for bluffs")
    print("  - Value bet smaller (to get called)")
    print()
    
    print("Against Aggressive Player:")
    print("  - Check-raise more with strong hands")
    print("  - Trap with slowplays")
    print("  - Avoid medium-sized value bets")
    print()


def main():
    """
    Run no-limit bet sizing examples.
    """
    print("Chapter 14: No-Limit Bet Sizing\n")
    print("=" * 70)
    print()
    
    demonstrate_bet_sizing_effect()
    demonstrate_bluffing_frequencies()
    demonstrate_geometric_betting()
    analyze_bet_sizing_vs_range()
    compare_exploitative_vs_gto()
    
    print("=" * 70)
    print("\nKey Takeaways:")
    print("1. Bet sizing is a powerful strategic tool in no-limit")
    print("2. Pot odds determine minimum calling equity")
    print("3. Bluff frequency should match pot odds offered")
    print("4. Larger bets require fewer bluffs but more polarized ranges")
    print("5. Geometric sizing maintains consistency across streets")
    print("6. Exploitative play adjusts bet sizing based on opponent tendencies")


if __name__ == "__main__":
    main()
