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
from typing import Tuple, Dict, Optional

from ..game_tree import (
    ChanceDistribution,
    GameTree,
    GameTreeNode,
    InformationSet,
    Player,
)
from ..mccfr import MonteCarloCFR
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
        
        X's strategies: [Always Fold when Y bets, Always Call when Y bets]
        Y's strategies: [Check Always, Bet Nuts Only, Bluff Only, Bet Always]
        
        Returns:
            Tuple of (payoff_matrix_x, payoff_matrix_y)
        """
        P = self.pot_size
        B = self.bet_size

        # Payoff matrix for X (rows = X strategies, cols = Y strategies)
        payoff_x = np.zeros((2, 4))

        # Scenario analysis:
        # Y has winning hand (nuts) 50% of the time - beats X at showdown
        # Y has losing hand (bluff) 50% of the time - loses to X at showdown

        # X Strategy 0: Always Fold when Y bets
        payoff_x[0, 0] = 0.0    # Y Check Always: showdown, EV = 0
        payoff_x[0, 1] = 0.0    # Y Bet Nuts Only: lose P when bet, win P when check
        payoff_x[0, 2] = -P     # Y Bluff Only: lose P whether bluffing or checking
        payoff_x[0, 3] = -P     # Y Bet Always: always fold and lose pot P

        # X Strategy 1: Always Call when Y bets
        payoff_x[1, 0] = 0.0           # Y Check Always: showdown, EV = 0
        payoff_x[1, 1] = -B / 2        # Y Bet Nuts Only: lose P+B when bet, win P when check
        payoff_x[1, 2] = B / 2         # Y Bluff Only: lose P when check, win P+B when bluff
        payoff_x[1, 3] = 0.0           # Y Bet Always: symmetric outcomes, EV = 0

        # Y's payoff is negative of X's payoff (zero-sum game)
        payoff_y = -payoff_x

        return payoff_x, payoff_y

    def solve_nash_equilibrium(self) -> Dict:
        """Closed-form Nash equilibrium for the Clairvoyance Game."""

        P = float(self.pot_size)
        B = float(self.bet_size)
        if P < 0 or B <= 0:
            raise ValueError("Pot size must be non-negative and bet size must be positive")

        denominator = 2 * P + B
        bluff_fraction = B / denominator if denominator > 0 else 0.0
        call_probability = (2 * P) / denominator if denominator > 0 else 0.0

        x_strategy = np.array([1.0 - call_probability, call_probability])
        y_strategy = np.array([0.0, 1.0 - bluff_fraction, 0.0, bluff_fraction])

        payoff_x, payoff_y = self.get_payoff_matrix()
        game_value = float(x_strategy @ payoff_x @ y_strategy)

        return {
            "x_strategy": x_strategy,
            "y_strategy": y_strategy,
            "game_value": game_value,
            "x_labels": self.get_strategy_labels()[0],
            "y_labels": self.get_strategy_labels()[1],
            "bluff_fraction": bluff_fraction,
            "call_probability": call_probability,
        }

    def solve_cfr_equilibrium(self, iterations: int = 10000, seed: Optional[int] = None) -> Dict:
        """Approximate the equilibrium using regret-matching CFR."""

        solution = super().solve_cfr_equilibrium(iterations=iterations, seed=seed)
        x_strategy = solution["x_strategy"]
        y_strategy = solution["y_strategy"]

        solution.update(
            {
                "call_probability": float(x_strategy[1]) if len(x_strategy) > 1 else 0.0,
                "bluff_fraction": float(y_strategy[2] + y_strategy[3]) if len(y_strategy) > 3 else 0.0,
            }
        )

        return solution

    def solve_mccfr_equilibrium(
        self, iterations: int = 50000, seed: Optional[int] = None
    ) -> Dict:
        """Approximate the equilibrium using external-sampling MCCFR."""

        tree = self.build_game_tree()
        solver = MonteCarloCFR(tree)
        result = solver.run(iterations=iterations, seed=seed)

        y_nuts_avg = result.average_strategy_dict("Y:nuts")
        y_bluff_avg = result.average_strategy_dict("Y:bluff")
        x_resp_avg = result.average_strategy_dict("X:bet_response")

        y_nuts_reg = result.cumulative_regret_dict("Y:nuts")
        y_bluff_reg = result.cumulative_regret_dict("Y:bluff")
        x_resp_reg = result.cumulative_regret_dict("X:bet_response")

        value_bet = y_nuts_avg.get("bet", 0.0)
        bluff_bet = y_bluff_avg.get("bet", 0.0)
        call_prob = x_resp_avg.get("call", 0.0)

        y_strategy = self._compose_y_strategy(value_bet, bluff_bet)
        x_strategy = np.array([1.0 - call_prob, call_prob])

        game_value = result.expected_value()

        solution = {
            "x_strategy": x_strategy,
            "y_strategy": y_strategy,
            "game_value": game_value,
            "x_labels": self.get_strategy_labels()[0],
            "y_labels": self.get_strategy_labels()[1],
            "call_probability": call_prob,
            "bluff_fraction": bluff_bet,
            "value_bet_fraction": value_bet,
            "iterations": iterations,
            "info_set_strategies": {
                "Y:nuts": y_nuts_avg,
                "Y:bluff": y_bluff_avg,
                "X:bet_response": x_resp_avg,
            },
            "info_set_regrets": {
                "Y:nuts": y_nuts_reg,
                "Y:bluff": y_bluff_reg,
                "X:bet_response": x_resp_reg,
            },
        }

        solution["is_equilibrium"] = self.verify_equilibrium(solution, tolerance=0.05)

        return solution

    @staticmethod
    def _compose_y_strategy(value_bet: float, bluff_bet: float) -> np.ndarray:
        """Map per-hand betting frequencies to the four pure strategies."""

        w_both = max(0.0, min(value_bet, bluff_bet))
        w_value_only = max(0.0, value_bet - w_both)
        w_bluff_only = max(0.0, bluff_bet - w_both)
        w_check_always = max(0.0, 1.0 - (w_both + w_value_only + w_bluff_only))

        strategy = np.array([w_check_always, w_value_only, w_bluff_only, w_both])
        total = strategy.sum()
        if total > 0:
            strategy /= total
        else:
            strategy = np.array([1.0, 0.0, 0.0, 0.0])
        return strategy
    
    def get_strategy_labels(self) -> Tuple[list, list]:
        """Get human-readable labels for strategies."""
        x_labels = ["Always Fold", "Always Call"]
        y_labels = ["Check Always", "Bet Nuts Only", "Bluff Only", "Bet Always"]
        return x_labels, y_labels

    def build_game_tree(self) -> GameTree:
        """Construct the extensive-form tree for the Clairvoyance game."""

        P = float(self.pot_size)
        B = float(self.bet_size)

        root = GameTreeNode(player=Player.CHANCE)

        info_sets: Dict[str, InformationSet] = {}

        y_nuts_info = InformationSet(
            "Y:nuts", player=Player.Y, description="Y decisions with winning hand"
        )
        y_bluff_info = InformationSet(
            "Y:bluff", player=Player.Y, description="Y decisions with losing hand"
        )
        x_response_info = InformationSet(
            "X:bet_response", player=Player.X, description="X response after Y bets"
        )

        for info in (y_nuts_info, y_bluff_info, x_response_info):
            info_sets[info.key] = info

        y_nuts_node = GameTreeNode(player=Player.Y, info_set=y_nuts_info)
        y_nuts_info.add_node(y_nuts_node)

        y_bluff_node = GameTreeNode(player=Player.Y, info_set=y_bluff_info)
        y_bluff_info.add_node(y_bluff_node)

        chance = ChanceDistribution((
            ("Y hand = nuts", 0.5),
            ("Y hand = bluff", 0.5),
        ))
        chance.validate()

        chance_nodes = {
            "Y hand = nuts": (y_nuts_node, "nuts"),
            "Y hand = bluff": (y_bluff_node, "bluff"),
        }

        for action, prob in chance:
            node, hand_label = chance_nodes[action]
            root.add_child(action, node, probability=prob, metadata={"hand": hand_label})

        def terminal(payoff_x: float) -> GameTreeNode:
            return GameTreeNode(player=Player.TERMINAL, payoffs=(payoff_x, -payoff_x))

        # Y has the nuts
        y_nuts_node.add_child("check", terminal(-P), metadata={"hand": "nuts", "action": "check"})

        x_vs_nuts = GameTreeNode(player=Player.X, info_set=x_response_info)
        x_response_info.add_node(x_vs_nuts)
        y_nuts_node.add_child(
            "bet",
            x_vs_nuts,
            metadata={"hand": "nuts", "action": "bet", "bet_size": B},
        )

        x_vs_nuts.add_child("fold", terminal(-P), metadata={"response": "fold"})
        x_vs_nuts.add_child(
            "call",
            terminal(-(P + B)),
            metadata={"response": "call", "pot": P + B},
        )

        # Y has a bluffing hand
        y_bluff_node.add_child("check", terminal(P), metadata={"hand": "bluff", "action": "check"})

        x_vs_bluff = GameTreeNode(player=Player.X, info_set=x_response_info)
        x_response_info.add_node(x_vs_bluff)
        y_bluff_node.add_child(
            "bet",
            x_vs_bluff,
            metadata={"hand": "bluff", "action": "bet", "bet_size": B},
        )

        x_vs_bluff.add_child("fold", terminal(-P), metadata={"response": "fold"})
        x_vs_bluff.add_child(
            "call",
            terminal(P + B),
            metadata={"response": "call", "pot": P + B},
        )

        return GameTree(root=root, information_sets=info_sets)
    
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
        
        # X's calling frequency when Y bets
        call_freq = x_strategy[1] if len(x_strategy) >= 2 else 0
        
        # Y's betting frequencies
        # Y strategies: [Check Always, Bet Nuts Only, Bluff Only, Bet Always]
        # Calculate implied betting frequencies for nuts and bluffs
        
        if len(y_strategy) >= 4:
            p_nuts = y_strategy[1] + y_strategy[3]    # Bet Nuts Only + Bet Always
            p_bluff = y_strategy[2] + y_strategy[3]   # Bluff Only + Bet Always
        else:
            # Handle reduced strategy space if solver eliminated dominated strategies
            p_nuts = 0
            p_bluff = 0
            for i, prob in enumerate(y_strategy):
                if i == 1:  # Bet Nuts Only
                    p_nuts += prob
                elif i == 2:  # Bluff Only  
                    p_bluff += prob
                elif i == 3:  # Bet Always
                    p_nuts += prob
                    p_bluff += prob
        
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