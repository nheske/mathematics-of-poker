"""
Chapter 16: Small Bets, Big Pots: No-Fold [0,1] Games

This module implements no-fold games where the pot is large relative to bet sizes,
making folding suboptimal.
"""

import numpy as np
from typing import Tuple, List
import matplotlib.pyplot as plt


class NoFoldGame:
    """
    A no-fold game where hands are distributed on [0,1] and folding is never optimal.
    """
    
    def __init__(self, pot_size: float = 10.0, bet_size: float = 1.0):
        """
        Initialize no-fold game.
        
        Args:
            pot_size: Size of the pot (large relative to bet)
            bet_size: Size of the bet (small relative to pot)
        """
        self.pot_size = pot_size
        self.bet_size = bet_size
        
        # Check if no-fold condition holds
        # Any hand should have enough pot odds to call
        # Worst case: hand = 0 has equity = 0
        # Pot odds needed: bet / (pot + 2*bet)
        # For no-fold: even worst hand should call
        # This requires pot >> bet
        
        self.pot_odds = bet_size / (pot_size + 2 * bet_size)
    
    def solve_equilibrium(self) -> Tuple[float, float]:
        """
        Solve for Nash equilibrium betting thresholds.
        
        In a no-fold game, Player 1 should:
        - Bet with strong hands (value betting)
        - Bet with weak hands (bluffing)
        - Check with medium hands
        
        Returns:
            (value_threshold, bluff_threshold) where:
            - P1 bets with hands > value_threshold (value)
            - P1 bets with hands < bluff_threshold (bluffs)
            - P1 checks with hands in [bluff_threshold, value_threshold]
        """
        # For no-fold game, the equilibrium satisfies:
        # 1. P1 is indifferent between betting and checking at thresholds
        # 2. Bluff-to-value ratio makes P2 indifferent (though P2 always calls)
        
        # The optimal bluff-to-value ratio is pot_size / bet_size
        # If P1 bets with [t_high, 1] (value) and [0, t_low] (bluffs)
        # Ratio: t_low / (1 - t_high) = pot / bet
        
        # Additionally, at t_high: EV(bet) = EV(check)
        # At t_low: EV(bet) = EV(check)
        
        # Simplified analytical solution for uniform distribution:
        # t_low = pot / (pot + 3*bet)
        # t_high = (pot + 2*bet) / (pot + 3*bet)
        
        alpha = self.pot_size / self.bet_size
        
        bluff_threshold = alpha / (alpha + 3)
        value_threshold = (alpha + 2) / (alpha + 3)
        
        return value_threshold, bluff_threshold
    
    def ev_bet(self, hand: float, value_threshold: float, bluff_threshold: float) -> float:
        """
        Calculate EV of betting with given hand.
        
        Args:
            hand: Hand strength [0, 1]
            value_threshold: Value betting threshold
            bluff_threshold: Bluffing threshold
            
        Returns:
            Expected value of betting
        """
        # Opponent always calls in no-fold game
        # EV = P(win) * (pot + 2*bet) - P(lose) * bet
        # P(win) = hand (against uniform distribution)
        
        ev = hand * (self.pot_size + 2 * self.bet_size) - (1 - hand) * self.bet_size
        
        return ev
    
    def ev_check(self, hand: float) -> float:
        """
        Calculate EV of checking.
        
        Args:
            hand: Hand strength [0, 1]
            
        Returns:
            Expected value of checking
        """
        # At showdown, win if hand > opponent's hand
        # EV = P(win) * pot
        # P(win) = hand (against uniform distribution)
        
        return hand * self.pot_size


def demonstrate_no_fold_game():
    """
    Demonstrate the no-fold game equilibrium.
    """
    print("=== No-Fold Game Equilibrium ===")
    print()
    
    pot = 10.0
    bet = 1.0
    
    game = NoFoldGame(pot_size=pot, bet_size=bet)
    value_threshold, bluff_threshold = game.solve_equilibrium()
    
    print(f"Pot size: {pot}")
    print(f"Bet size: {bet}")
    print(f"Pot odds: {game.pot_odds:.1%}")
    print()
    
    print("Equilibrium Strategy:")
    print(f"  Value betting threshold: {value_threshold:.3f}")
    print(f"  Bluffing threshold: {bluff_threshold:.3f}")
    print()
    
    print(f"Player 1 bets with:")
    print(f"  • Hands > {value_threshold:.3f} (top {(1-value_threshold)*100:.1f}% - VALUE)")
    print(f"  • Hands < {bluff_threshold:.3f} (bottom {bluff_threshold*100:.1f}% - BLUFFS)")
    print()
    
    print(f"Player 1 checks with:")
    print(f"  • Hands in [{bluff_threshold:.3f}, {value_threshold:.3f}] "
          f"(middle {(value_threshold-bluff_threshold)*100:.1f}%)")
    print()
    
    # Calculate bluff-to-value ratio
    value_freq = 1 - value_threshold
    bluff_freq = bluff_threshold
    bluff_to_value = bluff_freq / value_freq if value_freq > 0 else 0
    
    print(f"Bluff-to-value ratio: {bluff_to_value:.3f}")
    print(f"Pot/Bet ratio: {pot/bet:.3f}")
    print(f"(These should be equal in equilibrium)")
    print()


def analyze_pot_size_effect():
    """
    Analyze how pot size affects equilibrium thresholds.
    """
    print("=== Effect of Pot Size ===")
    print()
    
    bet = 1.0
    pot_sizes = [5, 10, 20, 50, 100]
    
    print(f"Bet size: {bet}")
    print()
    print("Pot Size | Value Thresh | Bluff Thresh | Check Range | Bluff:Value")
    print("-" * 75)
    
    for pot in pot_sizes:
        game = NoFoldGame(pot_size=pot, bet_size=bet)
        value_thresh, bluff_thresh = game.solve_equilibrium()
        check_range = value_thresh - bluff_thresh
        bluff_to_value = bluff_thresh / (1 - value_thresh)
        
        print(f"{pot:8.0f} | {value_thresh:12.3f} | {bluff_thresh:12.3f} | "
              f"{check_range:11.3f} | {bluff_to_value:11.3f}")
    
    print()
    print("Observations:")
    print("- Larger pots → more polarized betting ranges")
    print("- Larger pots → larger check range (more medium hands)")
    print("- Bluff-to-value ratio increases with pot size")
    print()


def compare_ev_at_thresholds():
    """
    Verify indifference at thresholds.
    """
    print("=== Indifference at Thresholds ===")
    print()
    
    game = NoFoldGame(pot_size=10.0, bet_size=1.0)
    value_threshold, bluff_threshold = game.solve_equilibrium()
    
    print(f"Pot: {game.pot_size}, Bet: {game.bet_size}")
    print()
    
    # Check EV at value threshold
    ev_bet_value = game.ev_bet(value_threshold, value_threshold, bluff_threshold)
    ev_check_value = game.ev_check(value_threshold)
    
    print(f"At value threshold ({value_threshold:.3f}):")
    print(f"  EV(Bet):   {ev_bet_value:.4f}")
    print(f"  EV(Check): {ev_check_value:.4f}")
    print(f"  Difference: {abs(ev_bet_value - ev_check_value):.6f}")
    print()
    
    # Check EV at bluff threshold
    ev_bet_bluff = game.ev_bet(bluff_threshold, value_threshold, bluff_threshold)
    ev_check_bluff = game.ev_check(bluff_threshold)
    
    print(f"At bluff threshold ({bluff_threshold:.3f}):")
    print(f"  EV(Bet):   {ev_bet_bluff:.4f}")
    print(f"  EV(Check): {ev_check_bluff:.4f}")
    print(f"  Difference: {abs(ev_bet_bluff - ev_check_bluff):.6f}")
    print()
    
    print("(At equilibrium, EVs should be equal at thresholds)")
    print()


def demonstrate_polarized_range():
    """
    Demonstrate the polarized betting range concept.
    """
    print("=== Polarized Betting Range ===")
    print()
    
    game = NoFoldGame(pot_size=10.0, bet_size=1.0)
    value_threshold, bluff_threshold = game.solve_equilibrium()
    
    print("Why Polarization Occurs:")
    print()
    
    print("Strong Hands (Value Bets):")
    print("  • Win often enough to profit from bet")
    print("  • Want to build pot with best hands")
    print("  • Betting increases EV")
    print()
    
    print("Weak Hands (Bluffs):")
    print("  • Rarely win at showdown anyway")
    print("  • Have little to lose by betting")
    print("  • Needed to balance value bets")
    print()
    
    print("Medium Hands (Check):")
    print("  • Too weak to bet for value")
    print("  • Too strong to use as bluffs")
    print("  • Have showdown value - prefer to check")
    print("  • Checking maximizes EV")
    print()
    
    # Show EV for different hand strengths
    print("Expected Values by Hand Strength:")
    print("Hand  | EV(Bet) | EV(Check) | Optimal")
    print("-" * 45)
    
    test_hands = [0.05, 0.25, 0.50, 0.75, 0.95]
    for hand in test_hands:
        ev_bet = game.ev_bet(hand, value_threshold, bluff_threshold)
        ev_check = game.ev_check(hand)
        optimal = "Bet" if ev_bet > ev_check else "Check"
        
        print(f"{hand:.2f}  | {ev_bet:7.3f} | {ev_check:9.3f} | {optimal}")
    
    print()


def simulate_no_fold_game(num_hands: int = 10000):
    """
    Simulate the no-fold game with equilibrium strategies.
    """
    print("=== Simulation ===")
    
    game = NoFoldGame(pot_size=10.0, bet_size=1.0)
    value_threshold, bluff_threshold = game.solve_equilibrium()
    
    np.random.seed(42)
    
    p1_total = 0.0
    
    bets = 0
    checks = 0
    value_bets = 0
    bluffs = 0
    
    for _ in range(num_hands):
        p1_hand = np.random.uniform(0, 1)
        p2_hand = np.random.uniform(0, 1)
        
        # P1 decides whether to bet or check
        if p1_hand > value_threshold:
            # Value bet
            bets += 1
            value_bets += 1
            
            # P2 always calls (no-fold game)
            if p1_hand > p2_hand:
                p1_total += game.pot_size + game.bet_size
            else:
                p1_total -= game.bet_size
                
        elif p1_hand < bluff_threshold:
            # Bluff
            bets += 1
            bluffs += 1
            
            # P2 always calls
            if p1_hand > p2_hand:
                p1_total += game.pot_size + game.bet_size
            else:
                p1_total -= game.bet_size
                
        else:
            # Check
            checks += 1
            
            # Go to showdown
            if p1_hand > p2_hand:
                p1_total += game.pot_size
            # else p1 gets 0
    
    avg_ev = p1_total / num_hands
    
    print(f"Simulated {num_hands} hands")
    print()
    print(f"P1 bet:   {bets} ({bets/num_hands*100:.1f}%)")
    print(f"  Value:  {value_bets} ({value_bets/num_hands*100:.1f}%)")
    print(f"  Bluffs: {bluffs} ({bluffs/num_hands*100:.1f}%)")
    print(f"P1 check: {checks} ({checks/num_hands*100:.1f}%)")
    print()
    
    if bets > 0:
        bluff_ratio = bluffs / value_bets if value_bets > 0 else 0
        print(f"Actual bluff-to-value ratio: {bluff_ratio:.3f}")
        print(f"Theoretical ratio: {game.pot_size/game.bet_size:.3f}")
        print()
    
    print(f"Average EV for Player 1: {avg_ev:.4f}")
    print(f"(Expected: ~{game.pot_size/2:.4f} in symmetric game)")
    print()


def main():
    """
    Run no-fold game examples.
    """
    print("Chapter 16: No-Fold [0,1] Games\n")
    print("=" * 75)
    print()
    
    demonstrate_no_fold_game()
    analyze_pot_size_effect()
    compare_ev_at_thresholds()
    demonstrate_polarized_range()
    simulate_no_fold_game()
    
    print("=" * 75)
    print("\nKey Takeaways:")
    print("1. Large pots relative to bets create no-fold situations")
    print("2. Optimal strategy is highly polarized")
    print("3. Bet with strong hands (value) and weak hands (bluffs)")
    print("4. Check with medium hands that have showdown value")
    print("5. Bluff-to-value ratio equals pot/bet ratio")
    print("6. Larger pots require more bluffs relative to value bets")


if __name__ == "__main__":
    main()
