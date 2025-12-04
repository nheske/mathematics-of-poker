"""[0, 1] Jam-or-Fold Game #2 (Example 12.2)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from .jam_or_fold_game_1 import JamOrFoldGame1


@dataclass
class JamOrFoldGame2(JamOrFoldGame1):
    """Jam-or-fold variant where the better hand has 2/3 equity at showdown."""

    def analytic_solution(self) -> Dict[str, float]:
        S = self.stack_size

        jam_raw = (3.0 * S) / (S * S + 3.0)
        call_raw = (1.5 * (S + 3.0)) / (S * S + 3.0)

        jam_threshold = min(1.0, jam_raw)
        call_threshold = min(1.0, call_raw)

        if jam_threshold <= call_threshold:
            avg_jam_value = (1.0 - call_threshold) * self.big_blind + (self.stack_size / 3.0) * (
                call_threshold - jam_threshold
            )
            regime = "S ≤ 3"
        else:
            avg_jam_value = (1.0 - call_threshold) * self.big_blind - call_threshold * (
                self.stack_size / 3.0
            ) * (jam_threshold - call_threshold) / jam_threshold
            regime = "S > 3"

        attacker_value = jam_threshold * avg_jam_value - (1.0 - jam_threshold) * self.small_blind
        defender_value = -attacker_value

        return {
            "jam_threshold": jam_threshold,
            "call_threshold": call_threshold,
            "jam_frequency": jam_threshold,
            "call_frequency": call_threshold,
            "attacker_value": attacker_value,
            "defender_value": defender_value,
            "regime": regime,
        }

    def _showdown_payoffs(self, attacker_value: float, defender_value: float) -> tuple[float, float]:
        payoff = (self.stack_size / 3.0) * self._payoff_scale
        if attacker_value < defender_value:
            return (-payoff, payoff)
        if defender_value < attacker_value:
            return (payoff, -payoff)
        return (0.0, 0.0)


def simulate_expected_value_game2(
    game: JamOrFoldGame2, samples: int = 200_000, seed: Optional[int] = None
) -> float:
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
                equity = game.stack_size / 3.0
                if y < x:
                    attacker_total += equity
                elif x < y:
                    attacker_total -= equity
            else:
                attacker_total += game.big_blind
        else:
            attacker_total -= game.small_blind

    return attacker_total / samples
