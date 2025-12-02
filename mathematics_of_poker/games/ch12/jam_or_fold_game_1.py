"""[0, 1] Jam-or-Fold Game #1 (Example 12.1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from ..game_tree import GameTree, GameTreeNode, InformationSet, Player
from ..mccfr import MonteCarloCFR
from .jam_or_fold_common import JamOrFoldBucketGame


@dataclass
class JamOrFoldGame1(JamOrFoldBucketGame):
    """Jam-or-fold game where hand strengths are uniform on ``[0, 1]``."""

    def analytic_solution(self) -> Dict[str, float]:
        """Return the closed-form equilibrium thresholds and game values."""

        S = self.stack_size
        denom = S + 1.0
        call_rate = min(1.0, 1.5 / denom)
        jam_rate = min(1.0, 3.0 * S / (denom * denom))

        if jam_rate <= 0:
            avg_jam_value = -self.small_blind
            integral = 0.0
        else:
            cutoff = min(call_rate, jam_rate)
            part_one = ((1.0 + (S - 1.0) * call_rate) * cutoff) - S * cutoff * cutoff
            part_two = 0.0
            if jam_rate > call_rate:
                part_two = (jam_rate - call_rate) * (1.0 - call_rate * (1.0 + S))
            integral = part_one + part_two
            avg_jam_value = integral / jam_rate if jam_rate > 0 else -self.small_blind

        attacker_value = (integral if jam_rate > 0 else 0.0) - (1.0 - jam_rate) * self.small_blind
        defender_value = -attacker_value

        return {
            "jam_threshold": jam_rate,
            "call_threshold": call_rate,
            "jam_frequency": jam_rate,
            "call_frequency": call_rate,
            "attacker_value": attacker_value,
            "defender_value": defender_value,
        }

    # ------------------------------------------------------------------
    # Extensive-form tree and MCCFR integration
    # ------------------------------------------------------------------
    def build_game_tree(self) -> GameTree:
        if self._tree_cache is not None:
            return self._tree_cache

        root = GameTreeNode(player=Player.CHANCE)
        info_sets: Dict[str, InformationSet] = {}

        prob_bucket = self._bucket_probability()

        for y_idx in range(self.num_buckets):
            y_value = self._bucket_value(y_idx)
            y_key = self._player_bucket_key("Y", y_idx)
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

            # Y folds
            fold_terminal = GameTreeNode(player=Player.TERMINAL, payoffs=self._attacker_fold_payoff())
            y_node.add_child("fold", fold_terminal)

            # Y jams -> chance node for X's hand
            x_chance = GameTreeNode(player=Player.CHANCE)
            y_node.add_child("jam", x_chance)

            for x_idx in range(self.num_buckets):
                x_value = self._bucket_value(x_idx)
                x_key = self._player_bucket_key("X", x_idx)
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

                x_chance.add_child(
                    action=f"X bucket {x_idx}",
                    child=x_node,
                    probability=prob_bucket,
                    metadata={"x_bucket": x_idx, "x_value": x_value},
                )

                fold_terminal_x = GameTreeNode(
                    player=Player.TERMINAL,
                    payoffs=self._defender_fold_payoff(),
                )
                x_node.add_child("fold", fold_terminal_x)

                showdown_payoffs = self._showdown_payoffs(y_value, x_value)
                call_terminal = GameTreeNode(player=Player.TERMINAL, payoffs=showdown_payoffs)
                x_node.add_child("call", call_terminal)

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
        attacker_value = result.expected_value() * self.stack_size
        defender_value = -attacker_value

        info_strategies: Dict[str, Dict[str, float]] = {}
        info_regrets: Dict[str, Dict[str, float]] = {}
        jam_probs: list[float] = []
        call_probs: list[float] = []

        for y_idx in range(self.num_buckets):
            key = self._player_bucket_key("Y", y_idx)
            strategy = result.average_strategy_dict(key)
            info_strategies[key] = strategy
            regrets = result.cumulative_regret_dict(key)
            info_regrets[key] = {
                action: value * self.stack_size for action, value in regrets.items()
            }
            jam_probs.append(strategy.get("jam", 0.0))

        for x_idx in range(self.num_buckets):
            key = self._player_bucket_key("X", x_idx)
            strategy = result.average_strategy_dict(key)
            info_strategies[key] = strategy
            regrets = result.cumulative_regret_dict(key)
            info_regrets[key] = {
                action: value * self.stack_size for action, value in regrets.items()
            }
            call_probs.append(strategy.get("call", 0.0))

        jam_frequency = sum(jam_probs) / self.num_buckets
        call_frequency = sum(call_probs) / self.num_buckets

        jam_bucket_cutoff = self._bucket_cutoff(probabilities=jam_probs)
        call_bucket_cutoff = self._bucket_cutoff(probabilities=call_probs)

        return {
            "game_value": attacker_value,
            "attacker_value": attacker_value,
            "defender_value": defender_value,
            "jam_frequency": jam_frequency,
            "call_frequency": call_frequency,
            "jam_bucket_cutoff": jam_bucket_cutoff,
            "call_bucket_cutoff": call_bucket_cutoff,
            "info_set_strategies": info_strategies,
            "info_set_regrets": info_regrets,
            "estimated_jam_threshold": jam_frequency,
            "estimated_call_threshold": call_frequency,
            "iterations": iterations,
            "num_buckets": self.num_buckets,
            "analytic_solution": self.analytic_solution(),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _bucket_cutoff(self, probabilities: list[float]) -> float:
        last_idx = -1
        for idx, prob in enumerate(probabilities):
            if prob >= 0.5:
                last_idx = idx
            else:
                break
        if last_idx == -1:
            return 0.0
        return self._bucket_value(last_idx)


def simulate_expected_value(
    game: JamOrFoldGame1, samples: int = 200_000, seed: Optional[int] = None
) -> float:
    """Monte Carlo estimate of the attacker's expected value under the analytic policy."""

    rng = np.random.default_rng(seed)
    solution = game.analytic_solution()
    jam_threshold = solution["jam_threshold"]
    call_threshold = solution["call_threshold"]

    attacker_total = 0.0
    for _ in range(samples):
        y = rng.random()
        x = rng.random()

        if y <= jam_threshold:
            if x <= call_threshold:
                # showdown
                if y < x:
                    attacker_total += game.stack_size
                elif x < y:
                    attacker_total -= game.stack_size
                # ties contribute 0
            else:
                attacker_total += game.big_blind
        else:
            attacker_total -= game.small_blind

    return attacker_total / samples
