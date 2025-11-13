"""
Chapter 13: Poker Made Simple: The AKQ Game

This module implements the classic AKQ game, a simplified three-card poker game
that captures essential strategic elements.
"""

import numpy as np
from typing import Dict, Tuple
from enum import Enum


class Card(Enum):
    """Cards in the AKQ game."""
    ACE = 3
    KING = 2
    QUEEN = 1


class AKQGame:
    """
    The AKQ game: Two players, three cards {A, K, Q}, one-card hands.
    """
    
    def __init__(self, ante: float = 1.0, bet_size: float = 1.0):
        """
        Initialize AKQ game.
        
        Args:
            ante: Amount each player antes
            bet_size: Size of the bet
        """
        self.ante = ante
        self.bet_size = bet_size
        self.pot = 2 * ante
        
        # Cards and their probabilities
        self.cards = [Card.ACE, Card.KING, Card.QUEEN]
        self.card_prob = 1.0 / 3.0  # Each card equally likely
    
    def solve_equilibrium(self) -> Dict:
        """
        Solve for Nash equilibrium strategies.
        
        Returns:
            Dictionary with equilibrium strategies
        """
        # For the AKQ game with bet size = ante, the equilibrium is known analytically
        
        # Player 1 strategies:
        # - Always bet with Ace
        # - Mix with King (bet with probability p_K)
        # - Mix with Queen (bluff with probability p_Q)
        
        # Player 2 strategies (after P1 bets):
        # - Always call with Ace
        # - Mix with King (call with probability c_K)
        # - Always fold with Queen
        
        # Player 2 strategies (after P1 checks):
        # - Always bet with Ace
        # - Mix with King (bet with probability b_K)
        # - Always check with Queen
        
        # For bet_size = ante = 1:
        # These are the analytical equilibrium values
        
        if abs(self.bet_size - self.ante) < 0.001:
            # Standard AKQ game equilibrium
            p1_bet_ace = 1.0      # Always bet with Ace
            p1_bet_king = 2.0/3.0 # Bet 2/3 of the time with King
            p1_bet_queen = 1.0/3.0 # Bluff 1/3 of the time with Queen
            
            p2_call_ace = 1.0     # Always call with Ace
            p2_call_king = 1.0/3.0 # Call 1/3 of the time with King
            p2_call_queen = 0.0   # Never call with Queen
            
            p2_bet_ace_after_check = 1.0  # Always bet Ace after check
            p2_bet_king_after_check = 1.0/3.0 # Bet King 1/3 after check
            p2_bet_queen_after_check = 0.0 # Never bet Queen after check
            
            p1_call_after_check_ace = 1.0   # Always call with Ace
            p1_call_after_check_king = 1.0/3.0 # Call 1/3 with King
            p1_call_after_check_queen = 0.0 # Never call with Queen
            
        else:
            # For other bet sizes, compute numerically
            # This is a simplification - full solution requires solving equations
            ratio = self.bet_size / self.ante
            
            # Simplified approximations
            p1_bet_ace = 1.0
            p1_bet_king = 1.0 / (1.0 + ratio)
            p1_bet_queen = 1.0 / (2.0 * ratio + 1.0)
            
            p2_call_ace = 1.0
            p2_call_king = 1.0 / (1.0 + 2.0 * ratio)
            p2_call_queen = 0.0
            
            p2_bet_ace_after_check = 1.0
            p2_bet_king_after_check = p1_bet_queen
            p2_bet_queen_after_check = 0.0
            
            p1_call_after_check_ace = 1.0
            p1_call_after_check_king = p2_call_king
            p1_call_after_check_queen = 0.0
        
        return {
            'p1_bet': {
                Card.ACE: p1_bet_ace,
                Card.KING: p1_bet_king,
                Card.QUEEN: p1_bet_queen
            },
            'p2_call_after_bet': {
                Card.ACE: p2_call_ace,
                Card.KING: p2_call_king,
                Card.QUEEN: p2_call_queen
            },
            'p2_bet_after_check': {
                Card.ACE: p2_bet_ace_after_check,
                Card.KING: p2_bet_king_after_check,
                Card.QUEEN: p2_bet_queen_after_check
            },
            'p1_call_after_check_bet': {
                Card.ACE: p1_call_after_check_ace,
                Card.KING: p1_call_after_check_king,
                Card.QUEEN: p1_call_after_check_queen
            }
        }
    
    def calculate_ev(self, strategy: Dict) -> float:
        """
        Calculate expected value for Player 1 given strategies.
        
        Args:
            strategy: Strategy dictionary from solve_equilibrium
            
        Returns:
            Expected value for Player 1
        """
        total_ev = 0.0
        
        # Iterate through all hand combinations
        for p1_card in self.cards:
            for p2_card in self.cards:
                if p1_card == p2_card:
                    continue  # Same card can't be dealt to both
                
                prob = self.card_prob * self.card_prob * 1.5  # Adjust for no replacement
                
                # P1 decides to bet or check
                prob_bet = strategy['p1_bet'][p1_card]
                prob_check = 1 - prob_bet
                
                # Branch 1: P1 bets
                if prob_bet > 0:
                    prob_p2_calls = strategy['p2_call_after_bet'][p2_card]
                    prob_p2_folds = 1 - prob_p2_calls
                    
                    # P2 folds
                    ev_p2_folds = self.pot
                    
                    # P2 calls
                    if p1_card.value > p2_card.value:
                        ev_p2_calls = self.pot + self.bet_size
                    else:
                        ev_p2_calls = -self.bet_size
                    
                    ev_bet = prob_p2_folds * ev_p2_folds + prob_p2_calls * ev_p2_calls
                else:
                    ev_bet = 0
                
                # Branch 2: P1 checks
                if prob_check > 0:
                    prob_p2_bets = strategy['p2_bet_after_check'][p2_card]
                    prob_p2_checks = 1 - prob_p2_bets
                    
                    # P2 checks
                    if p1_card.value > p2_card.value:
                        ev_p2_checks = self.pot
                    else:
                        ev_p2_checks = 0
                    
                    # P2 bets
                    prob_p1_calls = strategy['p1_call_after_check_bet'][p1_card]
                    prob_p1_folds = 1 - prob_p1_calls
                    
                    ev_p1_folds = 0
                    
                    if p1_card.value > p2_card.value:
                        ev_p1_calls = self.pot + self.bet_size
                    else:
                        ev_p1_calls = -self.bet_size
                    
                    ev_p2_bets = prob_p1_folds * ev_p1_folds + prob_p1_calls * ev_p1_calls
                    
                    ev_check = prob_p2_checks * ev_p2_checks + prob_p2_bets * ev_p2_bets
                else:
                    ev_check = 0
                
                total_ev += prob * (prob_bet * ev_bet + prob_check * ev_check)
        
        return total_ev


def demonstrate_akq_equilibrium():
    """
    Demonstrate the AKQ game equilibrium.
    """
    print("=== AKQ Game: Nash Equilibrium ===")
    print()
    
    game = AKQGame(ante=1.0, bet_size=1.0)
    strategy = game.solve_equilibrium()
    
    print(f"Antes: {game.ante}, Bet size: {game.bet_size}, Pot: {game.pot}")
    print()
    
    print("Player 1 Initial Action (Bet Frequencies):")
    print("-" * 50)
    for card in [Card.ACE, Card.KING, Card.QUEEN]:
        freq = strategy['p1_bet'][card]
        print(f"  {card.name:5s}: Bet {freq:.1%} of the time")
    print()
    
    print("Player 2 Response to Bet (Call Frequencies):")
    print("-" * 50)
    for card in [Card.ACE, Card.KING, Card.QUEEN]:
        freq = strategy['p2_call_after_bet'][card]
        print(f"  {card.name:5s}: Call {freq:.1%} of the time")
    print()
    
    print("Player 2 Action After Check (Bet Frequencies):")
    print("-" * 50)
    for card in [Card.ACE, Card.KING, Card.QUEEN]:
        freq = strategy['p2_bet_after_check'][card]
        print(f"  {card.name:5s}: Bet {freq:.1%} of the time")
    print()
    
    print("Player 1 Response to Check-Bet (Call Frequencies):")
    print("-" * 50)
    for card in [Card.ACE, Card.KING, Card.QUEEN]:
        freq = strategy['p1_call_after_check_bet'][card]
        print(f"  {card.name:5s}: Call {freq:.1%} of the time")
    print()
    
    ev = game.calculate_ev(strategy)
    print(f"Expected Value for Player 1: {ev:.4f}")
    print()


def analyze_bet_sizing_effect():
    """
    Analyze how bet sizing affects the equilibrium.
    """
    print("=== Effect of Bet Sizing ===")
    print()
    
    ante = 1.0
    bet_sizes = [0.5, 1.0, 2.0, 3.0]
    
    print("Ante: 1.0")
    print()
    print("Bet Size | P1 Bet K | P1 Bet Q (Bluff) | P2 Call K | Bluff:Value Ratio")
    print("-" * 80)
    
    for bet_size in bet_sizes:
        game = AKQGame(ante=ante, bet_size=bet_size)
        strategy = game.solve_equilibrium()
        
        p1_bet_k = strategy['p1_bet'][Card.KING]
        p1_bet_q = strategy['p1_bet'][Card.QUEEN]
        p2_call_k = strategy['p2_call_after_bet'][Card.KING]
        
        # Bluff to value ratio
        # P1 always bets Ace, sometimes bets King, sometimes bluffs Queen
        # Expected value bets = 1 + p1_bet_k * (1/3) [normalized]
        # Expected bluffs = p1_bet_q * (1/3)
        bluff_to_value = p1_bet_q / (1 + p1_bet_k) if (1 + p1_bet_k) > 0 else 0
        
        print(f"{bet_size:8.1f} | {p1_bet_k:8.1%} | {p1_bet_q:16.1%} | {p2_call_k:9.1%} | {bluff_to_value:17.3f}")
    
    print()
    print("Observations:")
    print("- Larger bets require fewer bluffs")
    print("- Bluff-to-value ratio decreases with bet size")
    print("- Player 2 calls less frequently with larger bets")
    print()


def simulate_akq_game(num_hands: int = 10000):
    """
    Simulate the AKQ game with equilibrium strategies.
    """
    print("=== Simulation ===")
    
    game = AKQGame(ante=1.0, bet_size=1.0)
    strategy = game.solve_equilibrium()
    
    np.random.seed(42)
    
    p1_total = 0.0
    action_counts = {
        'bet': 0, 'check': 0, 'call_bet': 0, 'fold_bet': 0,
        'bet_after_check': 0, 'check_after_check': 0,
        'call_check_bet': 0, 'fold_check_bet': 0
    }
    
    for _ in range(num_hands):
        # Deal cards (without replacement)
        cards = [Card.ACE, Card.KING, Card.QUEEN]
        np.random.shuffle(cards)
        p1_card = cards[0]
        p2_card = cards[1]
        
        # P1 acts
        if np.random.random() < strategy['p1_bet'][p1_card]:
            # P1 bets
            action_counts['bet'] += 1
            
            # P2 responds
            if np.random.random() < strategy['p2_call_after_bet'][p2_card]:
                # P2 calls
                action_counts['call_bet'] += 1
                if p1_card.value > p2_card.value:
                    p1_total += game.pot + game.bet_size
                else:
                    p1_total -= game.bet_size
            else:
                # P2 folds
                action_counts['fold_bet'] += 1
                p1_total += game.pot
        else:
            # P1 checks
            action_counts['check'] += 1
            
            # P2 responds
            if np.random.random() < strategy['p2_bet_after_check'][p2_card]:
                # P2 bets
                action_counts['bet_after_check'] += 1
                
                # P1 responds
                if np.random.random() < strategy['p1_call_after_check_bet'][p1_card]:
                    # P1 calls
                    action_counts['call_check_bet'] += 1
                    if p1_card.value > p2_card.value:
                        p1_total += game.pot + game.bet_size
                    else:
                        p1_total -= game.bet_size
                else:
                    # P1 folds
                    action_counts['fold_check_bet'] += 1
                    p1_total += 0
            else:
                # P2 checks
                action_counts['check_after_check'] += 1
                if p1_card.value > p2_card.value:
                    p1_total += game.pot
                else:
                    p1_total += 0
    
    avg_ev = p1_total / num_hands
    
    print(f"Simulated {num_hands} hands")
    print()
    print("Action frequencies:")
    print(f"  P1 bet: {action_counts['bet']/num_hands:.1%}")
    print(f"  P1 check: {action_counts['check']/num_hands:.1%}")
    if action_counts['bet'] > 0:
        print(f"  P2 called bet: {action_counts['call_bet']/action_counts['bet']:.1%}")
        print(f"  P2 folded to bet: {action_counts['fold_bet']/action_counts['bet']:.1%}")
    if action_counts['check'] > 0:
        print(f"  P2 bet after check: {action_counts['bet_after_check']/action_counts['check']:.1%}")
    print()
    print(f"Average EV for Player 1: {avg_ev:.4f} (antes)")
    print()


def main():
    """
    Run AKQ game examples.
    """
    print("Chapter 13: The AKQ Game\n")
    print("=" * 80)
    print()
    
    demonstrate_akq_equilibrium()
    analyze_bet_sizing_effect()
    simulate_akq_game()
    
    print("=" * 80)
    print("\nKey Takeaways:")
    print("1. AKQ game captures essential poker strategy elements")
    print("2. Optimal play requires mixed strategies (randomization)")
    print("3. Bluffing frequency relates to pot odds")
    print("4. Bet sizing significantly affects optimal strategies")
    print("5. Both players must randomize to avoid exploitation")


if __name__ == "__main__":
    main()
