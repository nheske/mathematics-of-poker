"""Cops and Robbers matrix game (Example 10.5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from ..game_tree import GameTree, GameTreeNode, InformationSet, Player
from ..mccfr import MonteCarloCFR


@dataclass
class CopsAndRobbersGame:
    """Two-action zero-sum game between a cop (Player X) and a robber (Player Y)."""

    patrol_cost: float = 1.0
    arrest_reward: float = 1.0
    robbery_reward: float = 1.0
    _tree_cache: Optional[GameTree] = field(init=False, default=None, repr=False)

    cop_actions = ("patrol", "stand_down")
    robber_actions = ("rob", "stay_home")

    def analytic_solution(self) -> Dict[str, object]:
        """Return the mixed-strategy Nash equilibrium for the default parameters."""

        if self.patrol_cost <= 0 or self.arrest_reward <= 0 or self.robbery_reward <= 0:
            raise ValueError("all payoffs must be positive")

        robber_mix = self.patrol_cost / (
            self.patrol_cost + self.arrest_reward + self.robbery_reward
        )
        # With symmetric unit payoffs this reduces to 1/3.
        p_patrol = self.robbery_reward / (
            self.patrol_cost + self.arrest_reward + self.robbery_reward
        )

        cop_mix = {
            "patrol": p_patrol,
            "stand_down": 1.0 - p_patrol,
        }
        robber_mix_dict = {
            "rob": robber_mix,
            "stay_home": 1.0 - robber_mix,
        }

        # Expected value for the cop under equilibrium mix.
        value_patrol = (
            robber_mix * self.arrest_reward
            - (1.0 - robber_mix) * self.patrol_cost
        )
        value_stand_down = -robber_mix * self.robbery_reward
        cop_value = value_patrol  # should equal value_stand_down at equilibrium

        return {
            "mix_x": cop_mix,
            "mix_y": robber_mix_dict,
            "game_value_x": cop_value,
            "game_value_y": -cop_value,
        }

    def build_game_tree(self) -> GameTree:
        if self._tree_cache is not None:
            return self._tree_cache

        root = GameTreeNode(player=Player.CHANCE)
        info_sets: Dict[str, InformationSet] = {}

        cop_info = InformationSet("X:choice", player=Player.X, description="Cop patrol decision")
        robber_info = InformationSet("Y:choice", player=Player.Y, description="Robber decision")
        info_sets[cop_info.key] = cop_info
        info_sets[robber_info.key] = robber_info

        cop_node = GameTreeNode(player=Player.X, info_set=cop_info)
        cop_info.add_node(cop_node)
        root.add_child(action="start", child=cop_node)

        for cop_action in self.cop_actions:
            robber_node = GameTreeNode(player=Player.Y, info_set=robber_info)
            robber_info.add_node(robber_node)
            cop_node.add_child(cop_action, robber_node)

            for robber_action in self.robber_actions:
                payoff_x = self._payoff_for_actions(cop_action, robber_action)
                terminal = GameTreeNode(player=Player.TERMINAL, payoffs=(payoff_x, -payoff_x))
                robber_node.add_child(robber_action, terminal)

        self._tree_cache = GameTree(root=root, information_sets=info_sets)
        return self._tree_cache

    def solve_mccfr_equilibrium(
        self,
        iterations: int = 25_000,
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

    def _payoff_for_actions(self, cop_action: str, robber_action: str) -> float:
        if cop_action == "patrol":
            if robber_action == "rob":
                return self.arrest_reward
            return -self.patrol_cost

        # Cop stands down
        if robber_action == "rob":
            return -self.robbery_reward
        return 0.0
