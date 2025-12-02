"""[0, 1] Game #1 implementation (Example 11.2 from *The Mathematics of Poker*).

This game models a half-street betting decision without folding. Player Y (second to act)
chooses whether to bet knowing Player X must call every bet. Both players receive
independent samples from the continuous uniform distribution on ``[0, 1]`` and the lower
number wins at showdown.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from ..game_tree import GameTree, GameTreeNode, InformationSet, Player
from ..mccfr import MonteCarloCFR
from .zero_one_common import ZeroOneBucketGame


@dataclass
class ZeroOneGame1(ZeroOneBucketGame):
    """Approximate the [0, 1] Game #1 with discrete buckets for MCCFR analysis."""

    # ------------------------------------------------------------------
    # Analytic solution helpers
    # ------------------------------------------------------------------
    def optimal_threshold(self) -> float:
        """Return the analytic betting threshold for Player Y."""

        return 0.5

    def expected_value_x(self, threshold: Optional[float] = None) -> float:
        """Expected value for Player X given a betting threshold for Y."""

        t = self._clamp_threshold(threshold)
        swing_bet = self.pot_size + self.bet_size
        return swing_bet * self._integral_linear(0.0, t) + self.pot_size * self._integral_linear(t, 1.0)

    def expected_value_y(self, threshold: Optional[float] = None) -> float:
        """Expected value for Player Y (negative of Player X)."""

        return -self.expected_value_x(threshold)

    def analytic_solution(self) -> Dict[str, float]:
        """Return the closed-form solution summary for the game."""

        threshold = self.optimal_threshold()
        return {
            "threshold": threshold,
            "bet_region": (0.0, threshold),
            "check_region": (threshold, 1.0),
            "expected_value_x": self.expected_value_x(threshold),
            "expected_value_y": self.expected_value_y(threshold),
        }

    # ------------------------------------------------------------------
    # MCCFR game-tree construction
    # ------------------------------------------------------------------
    def build_game_tree(self) -> GameTree:
        """Construct (and cache) the discretised game tree for MCCFR."""

        if self._tree_cache is not None:
            return self._tree_cache

        root = GameTreeNode(player=Player.CHANCE)
        info_sets: Dict[str, InformationSet] = {}

        prob_y = self._bucket_probability()
        prob_x = self._bucket_probability()

        for y_idx in range(self.num_buckets):
            y_value = self._bucket_value(y_idx)
            info_key = self._info_key(y_idx)

            info = InformationSet(
                info_key,
                player=Player.Y,
                description=f"Y decision with hand in bucket {y_idx} (value≈{y_value:.3f})",
            )
            info_sets[info_key] = info

            y_node = GameTreeNode(player=Player.Y, info_set=info)
            info.add_node(y_node)

            root.add_child(
                action=f"Y bucket {y_idx}",
                child=y_node,
                probability=prob_y,
                metadata={"y_bucket": y_idx, "y_value": y_value},
            )

            for action in ("bet", "check"):
                x_chance = GameTreeNode(player=Player.CHANCE)
                y_node.add_child(action, x_chance)

                for x_idx in range(self.num_buckets):
                    x_value = self._bucket_value(x_idx)
                    payoff_x = self._terminal_payoff_x(action, y_value, x_value)

                    terminal = GameTreeNode(
                        player=Player.TERMINAL,
                        payoffs=(payoff_x, -payoff_x),
                    )
                    x_chance.add_child(
                        action=f"X bucket {x_idx}",
                        child=terminal,
                        probability=prob_x,
                        metadata={"x_bucket": x_idx, "x_value": x_value},
                    )

        self._tree_cache = GameTree(root=root, information_sets=info_sets)
        return self._tree_cache

    def solve_mccfr_equilibrium(
        self, iterations: int = 200_000, seed: Optional[int] = None
    ) -> Dict[str, object]:
        """Run MCCFR on the discretised game tree and return diagnostics."""

        if iterations <= 0:
            raise ValueError("iterations must be positive")

        tree = self.build_game_tree()
        solver = MonteCarloCFR(tree)
        result = solver.run(iterations=iterations, seed=seed)

        info_strategies: Dict[str, Dict[str, float]] = {}
        info_regrets: Dict[str, Dict[str, float]] = {}
        bet_probabilities = []
        for y_idx in range(self.num_buckets):
            key = self._info_key(y_idx)
            strategy = result.average_strategy_dict(key)
            info_strategies[key] = strategy
            info_regrets[key] = result.cumulative_regret_dict(key)
            bet_probabilities.append(strategy.get("bet", 0.0))

        estimated_threshold = self._estimate_threshold(bet_probabilities)

        return {
            "game_value": result.expected_value(),
            "info_set_strategies": info_strategies,
            "info_set_regrets": info_regrets,
            "estimated_threshold": estimated_threshold,
            "optimal_threshold": self.optimal_threshold(),
            "iterations": iterations,
            "num_buckets": self.num_buckets,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _info_key(self, bucket_index: int) -> str:
        return self._player_bucket_key("Y", bucket_index)

    def _terminal_payoff_x(self, action: str, y_value: float, x_value: float) -> float:
        if action == "check":
            return self._showdown_payoff(x_value, y_value)
        return self._call_payoff(x_value, y_value)

    @staticmethod
    def _integral_linear(a: float, b: float) -> float:
        """Integral of (2y - 1) dy from a to b."""

        return (b**2 - b) - (a**2 - a)

    def _estimate_threshold(self, bet_probabilities: list[float]) -> float:
        """Return the bucket midpoint where betting frequency drops below 50%."""

        last_betting_bucket = -1
        for idx, prob in enumerate(bet_probabilities):
            if prob >= 0.5:
                last_betting_bucket = idx
            else:
                break

        if last_betting_bucket == -1:
            return 0.0
        return self._bucket_value(last_betting_bucket)

    def _clamp_threshold(self, threshold: Optional[float]) -> float:
        if threshold is None:
            threshold = self.optimal_threshold()
        return min(1.0, max(0.0, threshold))


def simulate_expected_value(game: ZeroOneGame1, samples: int = 100_000, seed: Optional[int] = None) -> float:
    """Monte Carlo estimate of Player X's expected value under the analytic policy."""

    rng = np.random.default_rng(seed)
    threshold = game.optimal_threshold()
    swing_bet = game.pot_size + game.bet_size

    total = 0.0
    for _ in range(samples):
        y_value = rng.random()
        x_value = rng.random()
        if y_value <= threshold:
            swing = swing_bet
        else:
            swing = game.pot_size

        if x_value < y_value:
            total += swing
        elif y_value < x_value:
            total -= swing
        # ties contribute 0

    return total / samples
