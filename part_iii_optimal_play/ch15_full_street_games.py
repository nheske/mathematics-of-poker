"""
Chapter 15: Player X Strikes Back: Full-Street Games

This module implements full-street games with multiple decision points.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from enum import Enum


class Action(Enum):
    """Possible actions in a full-street game."""
    CHECK = "check"
    BET = "bet"
    CALL = "call"
    RAISE = "raise"
    FOLD = "fold"


class GameNode:
    """Represents a node in the game tree."""
    
    def __init__(self, player: int, pot: float, to_call: float = 0):
        """
        Initialize a game node.
        
        Args:
            player: Which player acts (1 or 2)
            pot: Current pot size
            to_call: Amount player needs to call
        """
        self.player = player
        self.pot = pot
        self.to_call = to_call
        self.children: Dict[Action, 'GameNode'] = {}
        self.terminal = False
        self.showdown = False
    
    def add_child(self, action: Action, child: 'GameNode'):
        """Add a child node."""
        self.children[action] = child
    
    def mark_terminal(self, showdown: bool = False):
        """Mark this as a terminal node."""
        self.terminal = True
        self.showdown = showdown


class FullStreetGame:
    """
    A full-street poker game with multiple betting rounds.
    """
    
    def __init__(self, pot_size: float = 1.0, bet_size: float = 1.0, 
                 raise_size: float = 2.0):
        """
        Initialize full-street game.
        
        Args:
            pot_size: Initial pot size
            bet_size: Initial bet size
            raise_size: Raise size (total amount)
        """
        self.pot_size = pot_size
        self.bet_size = bet_size
        self.raise_size = raise_size
        self.root = self._build_game_tree()
    
    def _build_game_tree(self) -> GameNode:
        """
        Build the game tree for a full street.
        
        Structure:
        P1: Bet or Check
        ├─ Bet
        │  └─ P2: Call, Raise, or Fold
        │     ├─ Call → Showdown
        │     ├─ Fold → P1 wins
        │     └─ Raise
        │        └─ P1: Call or Fold
        │           ├─ Call → Showdown
        │           └─ Fold → P2 wins
        └─ Check
           └─ P2: Bet or Check
              ├─ Bet
              │  └─ P1: Call, Raise, or Fold
              │     ├─ Call → Showdown
              │     ├─ Fold → P2 wins
              │     └─ Raise
              │        └─ P2: Call or Fold
              │           ├─ Call → Showdown
              │           └─ Fold → P1 wins
              └─ Check → Showdown
        """
        root = GameNode(player=1, pot=self.pot_size)
        
        # P1 bets
        bet_node = GameNode(player=2, pot=self.pot_size + self.bet_size, 
                           to_call=self.bet_size)
        root.add_child(Action.BET, bet_node)
        
        # P2 calls bet
        call_bet_node = GameNode(player=0, pot=self.pot_size + 2*self.bet_size)
        call_bet_node.mark_terminal(showdown=True)
        bet_node.add_child(Action.CALL, call_bet_node)
        
        # P2 folds to bet
        fold_bet_node = GameNode(player=0, pot=self.pot_size + self.bet_size)
        fold_bet_node.mark_terminal(showdown=False)
        bet_node.add_child(Action.FOLD, fold_bet_node)
        
        # P2 raises
        raise_node = GameNode(player=1, pot=self.pot_size + self.bet_size + self.raise_size,
                             to_call=self.raise_size - self.bet_size)
        bet_node.add_child(Action.RAISE, raise_node)
        
        # P1 calls raise
        call_raise_node = GameNode(player=0, pot=self.pot_size + 2*self.raise_size)
        call_raise_node.mark_terminal(showdown=True)
        raise_node.add_child(Action.CALL, call_raise_node)
        
        # P1 folds to raise
        fold_raise_node = GameNode(player=0, pot=self.pot_size + self.bet_size + self.raise_size)
        fold_raise_node.mark_terminal(showdown=False)
        raise_node.add_child(Action.FOLD, fold_raise_node)
        
        # P1 checks
        check_node = GameNode(player=2, pot=self.pot_size)
        root.add_child(Action.CHECK, check_node)
        
        # P2 bets after check
        bet_after_check_node = GameNode(player=1, pot=self.pot_size + self.bet_size,
                                       to_call=self.bet_size)
        check_node.add_child(Action.BET, bet_after_check_node)
        
        # P1 calls bet after check
        call_bet_check_node = GameNode(player=0, pot=self.pot_size + 2*self.bet_size)
        call_bet_check_node.mark_terminal(showdown=True)
        bet_after_check_node.add_child(Action.CALL, call_bet_check_node)
        
        # P1 folds to bet after check
        fold_bet_check_node = GameNode(player=0, pot=self.pot_size + self.bet_size)
        fold_bet_check_node.mark_terminal(showdown=False)
        bet_after_check_node.add_child(Action.FOLD, fold_bet_check_node)
        
        # P1 raises after check-bet
        raise_check_node = GameNode(player=2, pot=self.pot_size + self.bet_size + self.raise_size,
                                    to_call=self.raise_size - self.bet_size)
        bet_after_check_node.add_child(Action.RAISE, raise_check_node)
        
        # P2 calls raise
        call_raise_check_node = GameNode(player=0, pot=self.pot_size + 2*self.raise_size)
        call_raise_check_node.mark_terminal(showdown=True)
        raise_check_node.add_child(Action.CALL, call_raise_check_node)
        
        # P2 folds to raise
        fold_raise_check_node = GameNode(player=0, pot=self.pot_size + self.bet_size + self.raise_size)
        fold_raise_check_node.mark_terminal(showdown=False)
        raise_check_node.add_child(Action.FOLD, fold_raise_check_node)
        
        # P2 checks after check
        check_check_node = GameNode(player=0, pot=self.pot_size)
        check_check_node.mark_terminal(showdown=True)
        check_node.add_child(Action.CHECK, check_check_node)
        
        return root
    
    def print_game_tree(self, node: Optional[GameNode] = None, indent: int = 0, 
                       action_taken: Optional[Action] = None):
        """
        Print the game tree structure.
        
        Args:
            node: Current node (uses root if None)
            indent: Current indentation level
            action_taken: Action that led to this node
        """
        if node is None:
            node = self.root
        
        prefix = "  " * indent
        
        if action_taken:
            print(f"{prefix}{action_taken.value.upper()}")
        
        if node.terminal:
            status = "Showdown" if node.showdown else "Fold"
            print(f"{prefix}  → {status} (Pot: {node.pot:.1f})")
        else:
            player_str = f"P{node.player}" if node.player > 0 else "Terminal"
            to_call_str = f", to call: {node.to_call:.1f}" if node.to_call > 0 else ""
            print(f"{prefix}  {player_str} acts (Pot: {node.pot:.1f}{to_call_str})")
            
            for action, child in node.children.items():
                self.print_game_tree(child, indent + 1, action)


class FullStreetStrategy:
    """
    Represents a strategy for a full-street game.
    """
    
    def __init__(self):
        """Initialize empty strategy."""
        # Strategy maps (node_id, hand) -> action_probabilities
        self.strategy: Dict = {}
    
    def get_action_prob(self, node_id: str, hand: float, action: Action) -> float:
        """Get probability of taking action with given hand at node."""
        key = (node_id, hand, action)
        return self.strategy.get(key, 0.0)
    
    def set_action_prob(self, node_id: str, hand: float, action: Action, prob: float):
        """Set probability of taking action."""
        key = (node_id, hand, action)
        self.strategy[key] = prob


def demonstrate_full_street_tree():
    """
    Demonstrate the full-street game tree structure.
    """
    print("=== Full-Street Game Tree ===")
    print()
    
    game = FullStreetGame(pot_size=2.0, bet_size=1.0, raise_size=3.0)
    
    print("Game Parameters:")
    print(f"  Initial pot: {game.pot_size}")
    print(f"  Bet size: {game.bet_size}")
    print(f"  Raise size: {game.raise_size}")
    print()
    
    print("Game Tree:")
    print()
    game.print_game_tree()
    print()


def analyze_position_value():
    """
    Analyze the value of position in full-street games.
    """
    print("=== Value of Position ===")
    print()
    
    print("Advantages of Acting Last (Player 2):")
    print("1. Information advantage:")
    print("   - Sees P1's action before deciding")
    print("   - Can respond optimally to bets or checks")
    print()
    
    print("2. Pot control:")
    print("   - Can check behind with medium hands")
    print("   - Can bet for value or bluff after P1 checks")
    print()
    
    print("3. Bluff efficiency:")
    print("   - Can bluff when P1 shows weakness (checks)")
    print("   - Knows when pot is contested or not")
    print()
    
    print("Player 1 Advantages:")
    print("1. Initiative:")
    print("   - Can bet first and put pressure on P2")
    print("   - Can represent strong hands with initial bet")
    print()
    
    print("2. Check-raise option:")
    print("   - Can trap P2 with check-raise")
    print("   - Disguises strong hands")
    print()
    
    print("Expected Value Difference:")
    print("  Position advantage varies with bet sizing and stack depth")
    print("  Typical advantage: 0.05-0.15 bets per hand")
    print()


def demonstrate_balanced_strategy():
    """
    Demonstrate principles of balanced strategy.
    """
    print("=== Balanced Strategy Principles ===")
    print()
    
    print("Player 1 Initial Action:")
    print("  • Bet with strong hands (for value)")
    print("  • Bet with weak hands (as bluffs)")
    print("  • Check with medium hands and traps")
    print("  • Maintain bluff-to-value ratio based on pot odds")
    print()
    
    print("Player 2 Response to Bet:")
    print("  • Call with medium-strong hands")
    print("  • Raise with very strong hands and bluffs")
    print("  • Fold with weak hands")
    print("  • Keep P1 indifferent with bluff-catchers")
    print()
    
    print("Player 2 Action After Check:")
    print("  • Bet with strong hands (for value)")
    print("  • Bet with weak hands (as bluffs)")
    print("  • Check behind with medium hands")
    print("  • Balance betting range")
    print()
    
    print("Player 1 Response to Check-Bet:")
    print("  • Similar to P2's response to initial bet")
    print("  • Call with medium-strong hands")
    print("  • Check-raise with very strong hands")
    print()


def calculate_example_frequencies():
    """
    Calculate example optimal frequencies for uniform [0,1] game.
    """
    print("=== Example Optimal Frequencies ===")
    print()
    print("Simplified Full-Street Game (Pot=2, Bet=1)")
    print()
    
    # These are simplified/illustrative values
    print("Player 1 Initial Action:")
    print("  Hand Range    | Action      | Frequency")
    print("  " + "-" * 50)
    print("  [0.80, 1.00]  | Bet (value) | 100%")
    print("  [0.60, 0.80]  | Check/Bet   | Mixed")
    print("  [0.20, 0.60]  | Check       | 100%")
    print("  [0.00, 0.20]  | Bet (bluff) | 50%")
    print()
    
    print("Player 2 Response to P1 Bet:")
    print("  Hand Range    | Action       | Frequency")
    print("  " + "-" * 50)
    print("  [0.85, 1.00]  | Raise        | 100%")
    print("  [0.50, 0.85]  | Call         | 100%")
    print("  [0.40, 0.50]  | Call/Fold    | Mixed")
    print("  [0.00, 0.40]  | Fold         | 100%")
    print()
    
    print("Note: These are illustrative values for educational purposes.")
    print("Actual equilibrium depends on specific game parameters.")
    print()


def main():
    """
    Run full-street game examples.
    """
    print("Chapter 15: Full-Street Games\n")
    print("=" * 70)
    print()
    
    demonstrate_full_street_tree()
    analyze_position_value()
    demonstrate_balanced_strategy()
    calculate_example_frequencies()
    
    print("=" * 70)
    print("\nKey Takeaways:")
    print("1. Full streets have complex decision trees")
    print("2. Position provides significant advantages")
    print("3. Multiple decision points require careful balancing")
    print("4. Check-raise adds strategic depth")
    print("5. Optimal play involves mixed strategies throughout tree")
    print("6. Bluff-to-value ratios must be maintained at each decision point")


if __name__ == "__main__":
    main()
