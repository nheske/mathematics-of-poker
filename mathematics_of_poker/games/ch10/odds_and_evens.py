"""Odds and Evens matrix game solved via the MCCFR infrastructure."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from ..game_tree import GameTree, GameTreeNode, InformationSet, Player
from ..mccfr import MonteCarloCFR


@dataclass
class OddsAndEvensGame:
    """Simultaneous-move zero-sum game with two pure strategies per player.

    Player X ("odds") collects ``+payoff`` when the total number of pennies is odd.
    Player Y ("evens") collects ``+payoff`` when the total number of pennies is even.
    """

    payoff: float = 1.0
    _tree_cache: Optional[GameTree] = field(init=False, default=None, repr=False)

    def analytic_solution(self) -> Dict[str, float]:
        """Return the Nash equilibrium mix and game value."""

        return {
            "mix_y_penny": 0.5,
            "mix_x_penny": 0.5,
            "game_value_y": 0.0,
            "game_value_x": 0.0,
        }

    def build_game_tree(self) -> GameTree:
        if self._tree_cache is not None:
            # Reuse the cached tree so repeated MCCFR runs avoid rebuilding nodes.
            return self._tree_cache

        # Root chance node fans out into Y's simultaneous move; both players share info sets.
        root = GameTreeNode(player=Player.CHANCE)
        info_sets: Dict[str, InformationSet] = {}

        # Single information set per player because the game is simultaneous.
        y_info = InformationSet("Y:choice", player=Player.Y, description="Y chooses penny or none")
        info_sets[y_info.key] = y_info

        x_info = InformationSet("X:choice", player=Player.X, description="X chooses penny or none")
        info_sets[x_info.key] = x_info

        y_node = GameTreeNode(player=Player.Y, info_set=y_info)
        y_info.add_node(y_node)
        root.add_child(action="start", child=y_node)

        for y_action in ("none", "penny"):
            # Each branch for Y attaches a Player X node that points back to the same info set.
            x_node = GameTreeNode(player=Player.X, info_set=x_info)
            x_info.add_node(x_node)
            y_node.add_child(y_action, x_node)

            for x_action in ("none", "penny"):
                # Terminal payoff is stored from Player X's perspective per framework convention.
                payoff_x = self._payoff_for_actions(y_action, x_action)
                terminal = GameTreeNode(player=Player.TERMINAL, payoffs=(payoff_x, -payoff_x))
                x_node.add_child(x_action, terminal)

        self._tree_cache = GameTree(root=root, information_sets=info_sets)
        return self._tree_cache

    def solve_mccfr_equilibrium(
        self,
        iterations: int = 5_000,
        seed: Optional[int] = None,
        use_cfr_plus: bool = True,
    ) -> Dict[str, object]:
        if iterations <= 0:
            raise ValueError("iterations must be positive")

        tree = self.build_game_tree()
        solver = MonteCarloCFR(tree, use_cfr_plus=use_cfr_plus)
        result = solver.run(iterations=iterations, seed=seed, use_cfr_plus=use_cfr_plus)

        info_strategies: Dict[str, Dict[str, float]] = {}
        info_regrets: Dict[str, Dict[str, float]] = {}

        for info in tree.all_information_sets():
            info_strategies[info.key] = result.average_strategy_dict(info.key)
            info_regrets[info.key] = result.cumulative_regret_dict(info.key)

        return {
            "game_value": result.expected_value(),
            "info_set_strategies": info_strategies,
            "info_set_regrets": info_regrets,
            "iterations": iterations,
            "use_cfr_plus": use_cfr_plus,
            "average_delay": result.average_delay,
            "average_weighting": result.average_weighting,
        }

    def _payoff_for_actions(self, y_action: str, x_action: str) -> float:
        pennies = (y_action == "penny") + (x_action == "penny")
        return self.payoff if pennies % 2 == 1 else -self.payoff
