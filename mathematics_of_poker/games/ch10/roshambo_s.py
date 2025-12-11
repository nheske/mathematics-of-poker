"""Roshambo-S game: bonus payout for victories with scissors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from ..game_tree import GameTree, GameTreeNode, InformationSet, Player
from ..mccfr import MonteCarloCFR


@dataclass
class RoshamboSGame:
    """Variant of rock-paper-scissors with a premium for winning using scissors."""

    payoff: float = 1.0
    scissor_bonus: float = 2.0
    _tree_cache: Optional[GameTree] = field(init=False, default=None, repr=False)

    actions = ("rock", "paper", "scissors")

    def analytic_solution(self) -> Dict[str, Dict[str, float]]:
        """Return the Nash equilibrium mix for the scissors-bonus payoff matrix."""

        if self.payoff <= 0:
            raise ValueError("payoff must be positive")
        if self.scissor_bonus <= 0:
            raise ValueError("scissor_bonus must be positive")

        ratio = self.scissor_bonus / self.payoff
        denom = 2.0 + ratio
        scissors_prob = 1.0 / denom
        paper_prob = scissors_prob
        rock_prob = ratio / denom

        mix = {
            "rock": rock_prob,
            "paper": paper_prob,
            "scissors": scissors_prob,
        }

        return {
            "mix_y": mix.copy(),
            "mix_x": mix.copy(),
            "game_value_y": 0.0,
            "game_value_x": 0.0,
        }

    def build_game_tree(self) -> GameTree:
        if self._tree_cache is not None:
            return self._tree_cache

        root = GameTreeNode(player=Player.CHANCE)
        info_sets: Dict[str, InformationSet] = {}

        y_info = InformationSet(
            "Y:choice",
            player=Player.Y,
            description="Y chooses rock/paper/scissors with scissors bonus variant",
        )
        x_info = InformationSet(
            "X:choice",
            player=Player.X,
            description="X chooses rock/paper/scissors with scissors bonus variant",
        )
        info_sets[y_info.key] = y_info
        info_sets[x_info.key] = x_info

        y_node = GameTreeNode(player=Player.Y, info_set=y_info)
        y_info.add_node(y_node)
        root.add_child(action="start", child=y_node)

        for y_action in self.actions:
            x_node = GameTreeNode(player=Player.X, info_set=x_info)
            x_info.add_node(x_node)
            y_node.add_child(y_action, x_node)

            for x_action in self.actions:
                payoff_x = self._payoff_for_actions(y_action, x_action)
                terminal = GameTreeNode(player=Player.TERMINAL, payoffs=(payoff_x, -payoff_x))
                x_node.add_child(x_action, terminal)

        self._tree_cache = GameTree(root=root, information_sets=info_sets)
        return self._tree_cache

    def solve_mccfr_equilibrium(
        self, iterations: int = 20_000, seed: Optional[int] = None
    ) -> Dict[str, object]:
        if iterations <= 0:
            raise ValueError("iterations must be positive")

        tree = self.build_game_tree()
        solver = MonteCarloCFR(tree)
        result = solver.run(iterations=iterations, seed=seed)

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
        }

    def _payoff_for_actions(self, y_action: str, x_action: str) -> float:
        if y_action == x_action:
            return 0.0

        wins_over = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

        if wins_over[x_action] == y_action:
            return self.scissor_bonus if x_action == "scissors" else self.payoff

        # Otherwise Y wins. Determine if Y's winning action was scissors to apply the bonus.
        return -(
            self.scissor_bonus if y_action == "scissors" else self.payoff
        )
