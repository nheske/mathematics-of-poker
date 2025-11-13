"""
Chapter 11: One Side of the Street: Half-Street Games

This module implements half-street poker games with a single betting round.
"""

import numpy as np
from typing import Tuple, Callable
import matplotlib.pyplot as plt


class HalfStreetGame:
    """
    A simplified poker game with one betting round.
    Hands are distributed uniformly on [0, 1].
    """
    
    def __init__(self, pot_size: float = 1.0, bet_size: float = 1.0):
        """
        Initialize a half-street game.
        
        Args:
            pot_size: Initial pot size
            bet_size: Size of the bet
        """
        self.pot_size = pot_size
        self.bet_size = bet_size
    
    def ev_bet_and_called(self, hand: float, threshold: float) -> float:
        """
        Expected value of betting and being called.
        
        Args:
            hand: Hand strength in [0, 1]
            threshold: Opponent's calling threshold
            
        Returns:
            Expected value
        """
        # Probability opponent calls
        prob_call = 1 - threshold
        
        if prob_call == 0:
            return self.pot_size  # Always wins pot if opponent never calls
        
        # If called, win if hand > opponent's hand
        # Opponent's hand is uniform on [threshold, 1]
        # P(win | called) = (hand - threshold) / (1 - threshold) if hand > threshold
        if hand <= threshold:
            prob_win = 0
        else:
            prob_win = (hand - threshold) / (1 - threshold)
        
        # EV = P(call) * [P(win|call) * (pot + 2*bet) - P(lose|call) * bet]
        #    + P(fold) * pot
        ev_if_called = prob_win * (self.pot_size + 2 * self.bet_size) - \
                       (1 - prob_win) * self.bet_size
        ev_if_folded = self.pot_size
        
        return prob_call * ev_if_called + (1 - prob_call) * ev_if_folded
    
    def ev_check(self, hand: float) -> float:
        """
        Expected value of checking.
        
        Args:
            hand: Hand strength in [0, 1]
            
        Returns:
            Expected value
        """
        # At showdown, win if hand > opponent's hand
        prob_win = hand
        return prob_win * self.pot_size


class BetOrCheckGame(HalfStreetGame):
    """
    Simple half-street game: Player 1 bets or checks, Player 2 calls or folds.
    """
    
    def solve_equilibrium(self, num_iterations: int = 1000) -> Tuple[float, float]:
        """
        Solve for Nash equilibrium thresholds.
        
        Returns:
            (bet_threshold, call_threshold)
        """
        # Use iterative best response
        call_threshold = 0.5  # Initial guess
        
        for _ in range(num_iterations):
            # Find P1's best response: bet threshold
            bet_threshold = self._find_bet_threshold(call_threshold)
            
            # Find P2's best response: call threshold
            call_threshold = self._find_call_threshold(bet_threshold)
        
        return bet_threshold, call_threshold
    
    def _find_bet_threshold(self, call_threshold: float) -> float:
        """
        Find optimal betting threshold given opponent's calling threshold.
        
        Need to find threshold where EV(bet) = EV(check)
        Actually, bet with strong hands and some bluffs, check medium hands.
        """
        # Simplified: bet with hands above this threshold
        # In reality, should bet strong hands + bluff with weak hands
        
        # Binary search for indifference point
        low, high = 0.0, 1.0
        
        for _ in range(100):
            mid = (low + high) / 2
            ev_bet = self.ev_bet_and_called(mid, call_threshold)
            ev_check = self.ev_check(mid)
            
            if ev_bet > ev_check:
                high = mid
            else:
                low = mid
        
        return (low + high) / 2
    
    def _find_call_threshold(self, bet_threshold: float) -> float:
        """
        Find optimal calling threshold given opponent's betting threshold.
        """
        # Opponent bets with hands > bet_threshold
        # Need pot odds: need to win bet_size / (pot_size + 2*bet_size)
        
        # Simplified calculation
        # When called, opponent has hand uniform on [bet_threshold, 1]
        # P(win) = P(hand > opponent | opponent in [bet_threshold, 1])
        
        # For indifference: EV(call) = EV(fold) = 0
        # Pot odds: need bet_size / (pot_size + 2*bet_size) equity
        required_equity = self.bet_size / (self.pot_size + 2 * self.bet_size)
        
        # If opponent's betting range is [bet_threshold, 1]
        # We need hand such that P(win) = required_equity
        # P(hand > uniform[bet_threshold, 1]) = (hand - bet_threshold)/(1 - bet_threshold)
        
        call_threshold = bet_threshold + required_equity * (1 - bet_threshold)
        
        return min(max(call_threshold, 0), 1)


def demonstrate_bet_or_check():
    """
    Demonstrate the bet-or-check game.
    """
    print("=== Bet or Check Game ===")
    print("Player 1: Bet or Check")
    print("Player 2 (if bet): Call or Fold")
    print()
    
    game = BetOrCheckGame(pot_size=1.0, bet_size=1.0)
    bet_threshold, call_threshold = game.solve_equilibrium()
    
    print(f"Equilibrium bet threshold: {bet_threshold:.3f}")
    print(f"Equilibrium call threshold: {call_threshold:.3f}")
    print()
    
    print(f"Player 1 bets with hands > {bet_threshold:.3f}")
    print(f"Player 2 calls with hands > {call_threshold:.3f}")
    print()
    
    # Calculate expected values at equilibrium
    # Sample some hand strengths
    hands = [0.3, 0.5, 0.7, 0.9]
    print("Expected values for different hands:")
    for hand in hands:
        ev_bet = game.ev_bet_and_called(hand, call_threshold)
        ev_check = game.ev_check(hand)
        optimal_action = "Bet" if ev_bet > ev_check else "Check"
        print(f"  Hand {hand:.1f}: EV(Bet)={ev_bet:.3f}, EV(Check)={ev_check:.3f} -> {optimal_action}")
    print()


def analyze_bet_sizing():
    """
    Analyze how bet sizing affects equilibrium.
    """
    print("=== Bet Sizing Analysis ===")
    
    pot_size = 1.0
    bet_sizes = [0.25, 0.5, 1.0, 2.0, 4.0]
    
    print(f"Pot size: {pot_size}")
    print()
    print("Bet Size | Bet Threshold | Call Threshold")
    print("-" * 50)
    
    for bet_size in bet_sizes:
        game = BetOrCheckGame(pot_size=pot_size, bet_size=bet_size)
        bet_threshold, call_threshold = game.solve_equilibrium()
        print(f"{bet_size:8.2f} | {bet_threshold:13.3f} | {call_threshold:14.3f}")
    
    print()
    print("Observations:")
    print("- Larger bets lead to tighter calling ranges")
    print("- Betting frequency depends on bet size")
    print("- Pot odds principle governs calling thresholds")
    print()


def simulate_game(num_hands: int = 10000):
    """
    Simulate the game with equilibrium strategies.
    """
    print("=== Simulation ===")
    
    game = BetOrCheckGame(pot_size=1.0, bet_size=1.0)
    bet_threshold, call_threshold = game.solve_equilibrium()
    
    np.random.seed(42)
    
    p1_total = 0.0
    
    for _ in range(num_hands):
        # Deal hands
        p1_hand = np.random.uniform(0, 1)
        p2_hand = np.random.uniform(0, 1)
        
        # P1 decides to bet or check
        if p1_hand > bet_threshold:
            # P1 bets
            if p2_hand > call_threshold:
                # P2 calls
                if p1_hand > p2_hand:
                    p1_total += game.pot_size + game.bet_size
                else:
                    p1_total -= game.bet_size
            else:
                # P2 folds
                p1_total += game.pot_size
        else:
            # P1 checks
            if p1_hand > p2_hand:
                p1_total += game.pot_size
            # Otherwise P1 loses pot (gets 0)
    
    avg_ev = p1_total / num_hands
    print(f"Simulated {num_hands} hands")
    print(f"Average EV for Player 1: {avg_ev:.4f}")
    print(f"(Theoretical equilibrium should be close to {game.pot_size/2:.4f})")
    print()


def main():
    """
    Run half-street game examples.
    """
    print("Chapter 11: Half-Street Games\n")
    print("=" * 60)
    print()
    
    demonstrate_bet_or_check()
    analyze_bet_sizing()
    simulate_game()
    
    print("=" * 60)
    print("\nKey Takeaways:")
    print("1. Half-street games isolate single betting round decisions")
    print("2. Optimal strategies involve threshold-based betting")
    print("3. Bet sizing affects optimal calling ranges")
    print("4. Pot odds principle determines calling frequencies")
    print("5. Bluffing is essential for balanced strategy")


if __name__ == "__main__":
    main()
