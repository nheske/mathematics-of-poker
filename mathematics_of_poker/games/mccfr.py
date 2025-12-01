from __future__ import annotations

"""Monte Carlo Counterfactual Regret Minimization for two-player games."""

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

import numpy as np

from .game_tree import GameTree, GameTreeEdge, GameTreeNode, InformationSet, Player


@dataclass
class InfoSetState:
    """Book-keeping for a single information set during MCCFR."""

    info_set: InformationSet
    actions: Tuple[str, ...]
    cumulative_regrets: np.ndarray
    strategy_sum: np.ndarray

    @classmethod
    def from_info_set(cls, info_set: InformationSet) -> "InfoSetState":
        if not info_set.nodes:
            raise ValueError(f"Information set {info_set.key} has no nodes")
        first_node = info_set.nodes[0]
        actions = tuple(edge.action for edge in first_node.edges)
        if not actions:
            raise ValueError(f"Information set {info_set.key} has no outgoing actions")
        for node in info_set.nodes[1:]:
            node_actions = tuple(edge.action for edge in node.edges)
            if node_actions != actions:
                raise ValueError(
                    f"Inconsistent actions in information set {info_set.key}: {node_actions} vs {actions}"
                )
        size = len(actions)
        return cls(
            info_set=info_set,
            actions=actions,
            cumulative_regrets=np.zeros(size, dtype=np.float64),
            strategy_sum=np.zeros(size, dtype=np.float64),
        )

    def current_strategy(self) -> np.ndarray:
        positive_regret = np.maximum(self.cumulative_regrets, 0.0)
        total = positive_regret.sum()
        if total > 1e-12:
            strategy = positive_regret / total
        else:
            strategy = np.full_like(self.cumulative_regrets, 1.0 / len(self.cumulative_regrets))
        return strategy

    def average_strategy(self) -> np.ndarray:
        total = self.strategy_sum.sum()
        if total > 1e-12:
            return self.strategy_sum / total
        return np.full_like(self.strategy_sum, 1.0 / len(self.strategy_sum))

    def average_strategy_dict(self) -> Dict[str, float]:
        avg = self.average_strategy()
        return {action: float(prob) for action, prob in zip(self.actions, avg)}

    def cumulative_regret_dict(self) -> Dict[str, float]:
        return {action: float(reg) for action, reg in zip(self.actions, self.cumulative_regrets)}


@dataclass
class MonteCarloCFRResult:
    """Stores MCCFR outcome and allows further analysis."""

    tree: GameTree
    info_states: Dict[str, InfoSetState]
    iterations: int

    def average_strategy(self, info_key: str) -> np.ndarray:
        return self.info_states[info_key].average_strategy()

    def average_strategy_dict(self, info_key: str) -> Dict[str, float]:
        return self.info_states[info_key].average_strategy_dict()

    def cumulative_regrets(self, info_key: str) -> np.ndarray:
        return self.info_states[info_key].cumulative_regrets.copy()

    def cumulative_regret_dict(self, info_key: str) -> Dict[str, float]:
        return self.info_states[info_key].cumulative_regret_dict()

    def expected_value(self) -> float:
        profile = {key: state.average_strategy() for key, state in self.info_states.items()}
        return self._expected_value(self.tree.root, profile)

    def _expected_value(self, node: GameTreeNode, profile: Dict[str, np.ndarray]) -> float:
        if node.is_terminal:
            # Payoffs stored as (X, Y)
            return float(node.payoffs[0])

        if node.player == Player.CHANCE:
            total = 0.0
            for edge in node.edges:
                total += edge.probability * self._expected_value(edge.child, profile)
            return total

        if node.info_set is None:
            raise ValueError("Player node missing information set")

        strategy = profile[node.info_set.key]
        value = 0.0
        for idx, edge in enumerate(node.edges):
            value += strategy[idx] * self._expected_value(edge.child, profile)
        return value


class MonteCarloCFR:
    """External-sampling MCCFR for two-player zero-sum games."""

    def __init__(self, tree: GameTree):
        self.tree = tree
        self.info_states: Dict[str, InfoSetState] = {
            info.key: InfoSetState.from_info_set(info) for info in tree.all_information_sets()
        }

    def run(self, iterations: int, seed: Optional[int] = None) -> MonteCarloCFRResult:
        if iterations <= 0:
            raise ValueError("iterations must be positive")

        rng = np.random.default_rng(seed)

        # Alternate updates for each player per iteration
        for _ in range(iterations):
            self._cfr(self.tree.root, player_index=0, rng=rng, reach=(1.0, 1.0))
            self._cfr(self.tree.root, player_index=1, rng=rng, reach=(1.0, 1.0))

        return MonteCarloCFRResult(self.tree, self.info_states, iterations)

    def _cfr(
        self,
        node: GameTreeNode,
        player_index: int,
        rng: np.random.Generator,
        reach: Tuple[float, float],
    ) -> float:
        if node.is_terminal:
            return float(node.payoffs[player_index])

        if node.player == Player.CHANCE:
            edge = self._sample_chance(node.edges, rng)
            return self._cfr(edge.child, player_index, rng, reach)

        if node.info_set is None:
            raise ValueError("Player node missing information set")

        info_state = self.info_states[node.info_set.key]
        strategy = info_state.current_strategy()
        player_at_node = 0 if node.player == Player.X else 1

        # Update average strategy with reach probability of the acting player
        info_state.strategy_sum += reach[player_at_node] * strategy

        if player_at_node == player_index:
            # Player we are updating – consider all actions
            action_utilities = np.zeros(len(node.edges), dtype=np.float64)
            node_utility = 0.0
            for idx, edge in enumerate(node.edges):
                next_reach = list(reach)
                next_reach[player_at_node] *= strategy[idx]
                action_utilities[idx] = self._cfr(edge.child, player_index, rng, tuple(next_reach))
                node_utility += strategy[idx] * action_utilities[idx]

            opponent_index = 1 - player_index
            regret = action_utilities - node_utility
            info_state.cumulative_regrets += reach[opponent_index] * regret
            return node_utility

        # Opponent node – sample a single action
        opponent_index = player_at_node
        action_index = self._sample_action(strategy, rng)
        edge = node.edges[action_index]
        next_reach = list(reach)
        next_reach[opponent_index] *= strategy[action_index]
        return self._cfr(edge.child, player_index, rng, tuple(next_reach))

    @staticmethod
    def _sample_action(strategy: np.ndarray, rng: np.random.Generator) -> int:
        cumulative = 0.0
        r = rng.random()
        for idx, prob in enumerate(strategy):
            cumulative += prob
            if r <= cumulative:
                return idx
        return len(strategy) - 1

    @staticmethod
    def _sample_chance(edges: Iterable[GameTreeEdge], rng: np.random.Generator) -> GameTreeEdge:
        edges = list(edges)
        probabilities = [edge.probability for edge in edges]
        total = sum(probabilities)
        if total <= 0:
            raise ValueError("Chance node has non-positive total probability")
        # Normalize in case of rounding issues
        normalized = [p / total for p in probabilities]
        cumulative = 0.0
        r = rng.random()
        for edge, prob in zip(edges, normalized):
            cumulative += prob
            if r <= cumulative:
                return edge
        return edges[-1]
