"""[0, 1] Game #2 implementation (Example 11.3 from *The Mathematics of Poker*).

Player Y can bet or check; if Y bets, Player X may call or fold. Hands are real numbers in
``[0, 1]`` with lower values stronger. We model both the analytic threshold solution and a
discretised extensive-form tree for MCCFR analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np

from ..game_tree import GameTree, GameTreeNode, InformationSet, Player
from ..mccfr import MonteCarloCFR


@dataclass
class ZeroOneGame2:
    """[0, 1] Game #2 where X may fold against Y's bet."""

    pot_size: float = 1.0
    bet_size: float = 1.0
    num_buckets: int = 40

    def __post_init__(self) -> None:
        if self.pot_size < 0:
            raise ValueError("pot_size must be non-negative")
        if self.bet_size <= 0:
            raise ValueError("bet_size must be positive")
        if self.bet_size != 1.0:
            raise ValueError("This implementation assumes unit bet size as in the book example")
        if self.num_buckets < 2:
            raise ValueError("num_buckets must be at least 2")
        self._tree_cache: Optional[GameTree] = None

    # ------------------------------------------------------------------
    # Analytic thresholds and expected values
    # ------------------------------------------------------------------
    def value_threshold(self) -> float:
        """Threshold y such that Y value-bets for y <= threshold."""

        P = self.pot_size
        numerator = P * (2 * P + 1)
        denominator = (P + 1) * (6 * P + 1)
        return numerator / denominator

    def call_threshold(self) -> float:
        """Threshold x such that X calls for x <= threshold."""

        return 2.0 * self.value_threshold()

    def bluff_threshold(self) -> float:
        """Threshold y such that Y bluffs for y >= threshold."""

        P = self.pot_size
        numerator = (2 * P + 1) ** 2
        denominator = (P + 1) * (6 * P + 1)
        return numerator / denominator

    def analytic_solution(self) -> Dict[str, float]:
        """Return analytic thresholds and expected values."""

        a = self.value_threshold()
        b = self.bluff_threshold()
        c = self.call_threshold()
        ev_x = self.expected_value_x(a=a, b=b, c=c)
        ev_y = -ev_x

        return {
            "value_threshold": a,
            "call_threshold": c,
            "bluff_threshold": b,
            "expected_value_x": ev_x,
            "expected_value_y": ev_y,
            "value_fraction": a,
            "check_fraction": max(0.0, b - a),
            "bluff_fraction": max(0.0, 1.0 - b),
        }

    def expected_value_x(self, *, a: Optional[float] = None, b: Optional[float] = None, c: Optional[float] = None) -> float:
        """Closed-form expected value for Player X under threshold strategies."""

        if a is None:
            a = self.value_threshold()
        if b is None:
            b = self.bluff_threshold()
        if c is None:
            c = self.call_threshold()

        P = self.pot_size

        ev_value = (P - 1.0) * (a ** 2) - P * a
        ev_check = P * (b - a) * (b + a - 1.0)
        ev_bluff = (1.0 - b) * (4.0 * a * P + 2.0 * a - P)
        return ev_value + ev_check + ev_bluff

    # ------------------------------------------------------------------
    # Discretised extensive-form tree for MCCFR
    # ------------------------------------------------------------------
    def build_game_tree(self) -> GameTree:
        if self._tree_cache is not None:
            return self._tree_cache

        root = GameTreeNode(player=Player.CHANCE)
        info_sets: Dict[str, InformationSet] = {}

        prob_bucket = 1.0 / self.num_buckets

        for y_idx in range(self.num_buckets):
            y_value = self._bucket_value(y_idx)
            y_key = self._y_info_key(y_idx)
            y_info = InformationSet(
                y_key,
                player=Player.Y,
                description=f"Y decision with hand bucket {y_idx} (≈ {y_value:.3f})",
            )
            info_sets[y_key] = y_info

            y_node = GameTreeNode(player=Player.Y, info_set=y_info)
            y_info.add_node(y_node)

            root.add_child(
                action=f"Y bucket {y_idx}",
                child=y_node,
                probability=prob_bucket,
                metadata={"y_bucket": y_idx, "y_value": y_value},
            )

            # Y checks: chance samples X's card, immediate showdown
            x_check = GameTreeNode(player=Player.CHANCE)
            y_node.add_child("check", x_check)

            for x_idx in range(self.num_buckets):
                x_value = self._bucket_value(x_idx)
                payoff_x = self._showdown_payoff(x_value, y_value)
                terminal = GameTreeNode(
                    player=Player.TERMINAL,
                    payoffs=(payoff_x, -payoff_x),
                )
                x_check.add_child(
                    action=f"X bucket {x_idx}",
                    child=terminal,
                    probability=prob_bucket,
                    metadata={"x_bucket": x_idx, "x_value": x_value},
                )

            # Y bets: chance node for X's card -> X decision node per bucket
            x_bet = GameTreeNode(player=Player.CHANCE)
            y_node.add_child("bet", x_bet)

            for x_idx in range(self.num_buckets):
                x_value = self._bucket_value(x_idx)
                x_key = self._x_info_key(x_idx)
                x_info = info_sets.get(x_key)
                if x_info is None:
                    x_info = InformationSet(
                        x_key,
                        player=Player.X,
                        description=f"X response with hand bucket {x_idx} (≈ {x_value:.3f})",
                    )
                    info_sets[x_key] = x_info

                x_node = GameTreeNode(player=Player.X, info_set=x_info)
                x_info.add_node(x_node)
                x_bet.add_child(
                    action=f"X bucket {x_idx}",
                    child=x_node,
                    probability=prob_bucket,
                    metadata={"x_bucket": x_idx, "x_value": x_value},
                )

                # X folds
                fold_terminal = GameTreeNode(
                    player=Player.TERMINAL,
                    payoffs=(-self.pot_size, self.pot_size),
                )
                x_node.add_child("fold", fold_terminal, metadata={"response": "fold"})

                # X calls
                payoff_call = self._call_payoff(x_value, y_value)
                call_terminal = GameTreeNode(
                    player=Player.TERMINAL,
                    payoffs=(payoff_call, -payoff_call),
                )
                x_node.add_child("call", call_terminal, metadata={"response": "call"})

        self._tree_cache = GameTree(root=root, information_sets=info_sets)
        return self._tree_cache

    def solve_mccfr_equilibrium(
        self, iterations: int = 250_000, seed: Optional[int] = None
    ) -> Dict[str, object]:
        if iterations <= 0:
            raise ValueError("iterations must be positive")

        tree = self.build_game_tree()
        solver = MonteCarloCFR(tree)
        result = solver.run(iterations=iterations, seed=seed)

        info_strategies: Dict[str, Dict[str, float]] = {}
        info_regrets: Dict[str, Dict[str, float]] = {}
        y_bet_probs = []
        for y_idx in range(self.num_buckets):
            key = self._y_info_key(y_idx)
            strategy = result.average_strategy_dict(key)
            info_strategies[key] = strategy
            info_regrets[key] = result.cumulative_regret_dict(key)
            y_bet_probs.append(strategy.get("bet", 0.0))

        x_call_probs = []
        for x_idx in range(self.num_buckets):
            key = self._x_info_key(x_idx)
            strategy = result.average_strategy_dict(key)
            info_strategies[key] = strategy
            info_regrets[key] = result.cumulative_regret_dict(key)
            x_call_probs.append(strategy.get("call", 0.0))

        est_value_threshold, est_bluff_threshold = self._estimate_y_thresholds(y_bet_probs)
        est_call_threshold = self._estimate_call_threshold(x_call_probs)

        return {
            "game_value": result.expected_value(),
            "info_set_strategies": info_strategies,
            "info_set_regrets": info_regrets,
            "estimated_value_threshold": est_value_threshold,
            "estimated_bluff_threshold": est_bluff_threshold,
            "estimated_call_threshold": est_call_threshold,
            "analytic_solution": self.analytic_solution(),
            "iterations": iterations,
            "num_buckets": self.num_buckets,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _bucket_value(self, index: int) -> float:
        return (index + 0.5) / self.num_buckets

    @staticmethod
    def _y_info_key(index: int) -> str:
        return f"Y:bucket[{index}]"

    @staticmethod
    def _x_info_key(index: int) -> str:
        return f"X:bucket[{index}]"

    def _showdown_payoff(self, x_value: float, y_value: float) -> float:
        if x_value < y_value:
            return self.pot_size
        if y_value < x_value:
            return -self.pot_size
        return 0.0

    def _call_payoff(self, x_value: float, y_value: float) -> float:
        swing = self.pot_size + self.bet_size
        if x_value < y_value:
            return swing
        if y_value < x_value:
            return -swing
        return 0.0

    def _estimate_y_thresholds(self, bet_probs: list[float]) -> Tuple[float, float]:
        midpoint = 0.0
        for idx, prob in enumerate(bet_probs):
            if prob >= 0.5:
                midpoint = self._bucket_value(idx)
            else:
                break

        bluff_threshold = 1.0
        for idx in range(len(bet_probs) - 1, -1, -1):
            if bet_probs[idx] >= 0.5:
                bluff_threshold = self._bucket_value(idx)
            else:
                break

        return midpoint, bluff_threshold

    def _estimate_call_threshold(self, call_probs: list[float]) -> float:
        threshold = 0.0
        for idx, prob in enumerate(call_probs):
            if prob >= 0.5:
                threshold = self._bucket_value(idx)
            else:
                break
        return threshold


def simulate_expected_value(
    game: ZeroOneGame2, samples: int = 100_000, seed: Optional[int] = None
) -> float:
    """Monte Carlo estimate of Player X's EV using analytic thresholds."""

    rng = np.random.default_rng(seed)
    a = game.value_threshold()
    b = game.bluff_threshold()
    c = game.call_threshold()

    total = 0.0
    swing_call = game.pot_size + game.bet_size

    for _ in range(samples):
        y = rng.random()
        x = rng.random()

        bet = (y <= a) or (y >= b)
        if not bet:
            if x < y:
                total += game.pot_size
            elif y < x:
                total -= game.pot_size
            # ties contribute 0
            continue

        call = x <= c
        if not call:
            total -= game.pot_size
            continue

        if x < y:
            total += swing_call
        elif y < x:
            total -= swing_call

    return total / samples
