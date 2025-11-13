"""
Chapter 12: Headsup With High Blinds: The Jam-or-Fold Game

This module implements the push-or-fold game for short-stack situations.
"""

import numpy as np
from typing import Tuple


class JamOrFoldGame:
    """
    Models a push-or-fold scenario in heads-up poker.
    """
    
    def __init__(self, stack_size: float, small_blind: float, big_blind: float):
        """
        Initialize jam-or-fold game.
        
        Args:
            stack_size: Effective stack size
            small_blind: Small blind amount
            big_blind: Big blind amount
        """
        self.stack_size = stack_size
        self.sb = small_blind
        self.bb = big_blind
        self.pot = small_blind + big_blind
    
    def solve_equilibrium_uniform(self) -> Tuple[float, float]:
        """
        Solve equilibrium for uniform [0,1] hand distribution.
        
        Returns:
            (jam_threshold, call_threshold) where:
            - SB jams with hands > jam_threshold
            - BB calls with hands > call_threshold
        """
        # Analytical solution for uniform distribution
        # Based on pot odds and equity calculations
        
        # Stack-to-pot ratio
        spr = self.stack_size / self.pot
        
        # BB's calling threshold based on pot odds
        # Needs to risk (stack - bb) to win (pot + stack)
        risk = self.stack_size - self.bb
        reward = self.pot + self.stack_size
        
        # For uniform distribution, calling threshold is based on required equity
        # Against uniform jamming range [t_jam, 1], need equity >= risk/(risk+reward)
        
        # Iteratively solve
        jam_threshold = 0.5
        call_threshold = 0.5
        
        for iteration in range(100):
            # Update BB's calling threshold
            # BB needs equity against SB's jamming range
            required_equity = risk / (risk + reward)
            
            # If SB jams with [jam_threshold, 1]
            # BB hand h beats (h - jam_threshold) / (1 - jam_threshold) of SB's range
            # So need h such that (h - jam_threshold) / (1 - jam_threshold) = required_equity
            call_threshold = jam_threshold + required_equity * (1 - jam_threshold)
            call_threshold = min(max(call_threshold, 0), 1)
            
            # Update SB's jamming threshold
            # SB is indifferent at threshold between jamming and folding
            
            # EV of folding for SB = -sb (loses small blind)
            ev_fold = -self.sb
            
            # EV of jamming at threshold
            # P(BB folds) * pot + P(BB calls) * [P(win) * (pot + stack) - P(lose) * stack]
            prob_bb_calls = 1 - call_threshold
            prob_bb_folds = call_threshold
            
            # At jam threshold, assuming hand = jam_threshold
            # If BB calls with [call_threshold, 1], our equity is:
            if call_threshold >= 1:
                equity = 1.0  # BB never calls
            else:
                # Our hand h beats (h - call_threshold) / (1 - call_threshold) of BB's calling range
                # At threshold h = jam_threshold
                if jam_threshold <= call_threshold:
                    equity = 0.0
                else:
                    equity = (jam_threshold - call_threshold) / (1 - call_threshold)
            
            ev_jam = prob_bb_folds * self.pot + \
                     prob_bb_calls * (equity * (self.pot + self.stack_size) - 
                                     (1 - equity) * self.stack_size)
            
            # Find threshold where EV(jam) = EV(fold)
            # This is complex, so we use a simplified approach
            
            # Simplified: SB should jam if EV(jam) > EV(fold)
            # For hands strong enough, always jam
            # For very weak hands, might jam as bluff
            
            # Binary search for value threshold
            low, high = 0.0, 1.0
            for _ in range(50):
                mid = (low + high) / 2
                
                if mid <= call_threshold:
                    equity_mid = 0.0
                else:
                    equity_mid = (mid - call_threshold) / (1 - call_threshold)
                
                ev_jam_mid = prob_bb_folds * self.pot + \
                            prob_bb_calls * (equity_mid * (self.pot + self.stack_size) -
                                           (1 - equity_mid) * self.stack_size)
                
                if ev_jam_mid > ev_fold:
                    high = mid
                else:
                    low = mid
            
            new_jam_threshold = (low + high) / 2
            
            # Check convergence
            if abs(new_jam_threshold - jam_threshold) < 0.001:
                break
            
            jam_threshold = new_jam_threshold
        
        return jam_threshold, call_threshold
    
    def ev_jam(self, hand: float, call_threshold: float) -> float:
        """
        Calculate EV of jamming with given hand.
        
        Args:
            hand: Hand strength [0, 1]
            call_threshold: Opponent's calling threshold
            
        Returns:
            Expected value of jamming
        """
        prob_call = 1 - call_threshold
        prob_fold = call_threshold
        
        if prob_call == 0:
            return self.pot  # BB always folds
        
        # Equity against calling range
        if hand <= call_threshold:
            equity = 0.0
        else:
            equity = (hand - call_threshold) / (1 - call_threshold)
        
        ev = prob_fold * self.pot + \
             prob_call * (equity * (self.pot + self.stack_size) - 
                         (1 - equity) * self.stack_size)
        
        return ev
    
    def ev_fold_sb(self) -> float:
        """
        EV of folding for small blind.
        """
        return -self.sb


def demonstrate_jam_or_fold():
    """
    Demonstrate the jam-or-fold game with different stack sizes.
    """
    print("=== Jam or Fold Game ===")
    print()
    
    sb = 0.5
    bb = 1.0
    
    stack_sizes = [5, 10, 15, 20]
    
    print(f"Blinds: {sb}/{bb}")
    print()
    print("Stack (BB) | Jam Threshold | Call Threshold | SB Jam % | BB Call %")
    print("-" * 75)
    
    for stack in stack_sizes:
        stack_bb = stack * bb
        game = JamOrFoldGame(stack_bb, sb, bb)
        jam_threshold, call_threshold = game.solve_equilibrium_uniform()
        
        jam_pct = (1 - jam_threshold) * 100
        call_pct = (1 - call_threshold) * 100
        
        print(f"{stack:10.0f} | {jam_threshold:13.3f} | {call_threshold:14.3f} | "
              f"{jam_pct:8.1f}% | {call_pct:9.1f}%")
    
    print()
    print("Observations:")
    print("- Shorter stacks -> wider jamming ranges")
    print("- Shorter stacks -> wider calling ranges")
    print("- As stacks increase, play becomes tighter")
    print()


def analyze_specific_scenario():
    """
    Analyze a specific push-or-fold scenario in detail.
    """
    print("=== Detailed Analysis: 10 BB Stacks ===")
    print()
    
    stack = 10.0
    sb = 0.5
    bb = 1.0
    
    game = JamOrFoldGame(stack, sb, bb)
    jam_threshold, call_threshold = game.solve_equilibrium_uniform()
    
    print(f"Stack size: {stack} BB")
    print(f"SB jam threshold: {jam_threshold:.3f} (top {(1-jam_threshold)*100:.1f}%)")
    print(f"BB call threshold: {call_threshold:.3f} (top {(1-call_threshold)*100:.1f}%)")
    print()
    
    # Calculate EVs for different hand strengths
    print("Expected Values:")
    print("-" * 50)
    print("Hand | EV(Jam) | EV(Fold) | Optimal Action")
    print("-" * 50)
    
    test_hands = [0.3, 0.5, 0.7, 0.85, 0.95]
    for hand in test_hands:
        ev_jam = game.ev_jam(hand, call_threshold)
        ev_fold = game.ev_fold_sb()
        optimal = "Jam" if ev_jam > ev_fold else "Fold"
        
        print(f"{hand:4.2f} | {ev_jam:7.3f} | {ev_fold:8.3f} | {optimal}")
    
    print()


def simulate_equilibrium_play(num_hands: int = 10000):
    """
    Simulate the game with equilibrium strategies.
    """
    print("=== Simulation ===")
    
    stack = 10.0
    sb = 0.5
    bb = 1.0
    
    game = JamOrFoldGame(stack, sb, bb)
    jam_threshold, call_threshold = game.solve_equilibrium_uniform()
    
    np.random.seed(42)
    
    sb_total = 0.0
    bb_total = 0.0
    
    jams = 0
    folds = 0
    calls = 0
    bb_folds = 0
    
    for _ in range(num_hands):
        sb_hand = np.random.uniform(0, 1)
        bb_hand = np.random.uniform(0, 1)
        
        # SB decision
        if sb_hand > jam_threshold:
            # SB jams
            jams += 1
            
            # BB decision
            if bb_hand > call_threshold:
                # BB calls
                calls += 1
                
                # Determine winner
                if sb_hand > bb_hand:
                    sb_total += game.pot + stack
                    bb_total -= stack
                else:
                    sb_total -= stack
                    bb_total += game.pot + stack
            else:
                # BB folds
                bb_folds += 1
                sb_total += game.pot
                bb_total -= game.pot
        else:
            # SB folds
            folds += 1
            sb_total -= sb
            bb_total += sb
    
    print(f"Simulated {num_hands} hands")
    print()
    print(f"SB jammed: {jams} ({jams/num_hands*100:.1f}%)")
    print(f"SB folded: {folds} ({folds/num_hands*100:.1f}%)")
    print(f"BB called: {calls} ({calls/jams*100:.1f}% of jams)" if jams > 0 else "BB called: 0")
    print(f"BB folded: {bb_folds} ({bb_folds/jams*100:.1f}% of jams)" if jams > 0 else "BB folded: 0")
    print()
    print(f"SB average EV: {sb_total/num_hands:.4f} BB")
    print(f"BB average EV: {bb_total/num_hands:.4f} BB")
    print()


def main():
    """
    Run jam-or-fold game examples.
    """
    print("Chapter 12: Jam-or-Fold Game\n")
    print("=" * 75)
    print()
    
    demonstrate_jam_or_fold()
    analyze_specific_scenario()
    simulate_equilibrium_play()
    
    print("=" * 75)
    print("\nKey Takeaways:")
    print("1. Short stacks require wider jamming ranges")
    print("2. BB must call with wider range to prevent exploitation")
    print("3. Stack-to-pot ratio is the key parameter")
    print("4. Equilibrium strategies are threshold-based")
    print("5. Real poker requires hand equity calculations")


if __name__ == "__main__":
    main()
