from __future__ import annotations

import math

from mathematics_of_poker.games.ch11.zero_one_game_2 import ZeroOneGame2, simulate_expected_value


def test_thresholds_monotonic_with_pot_size():
    game_small = ZeroOneGame2(pot_size=0.5)
    game_large = ZeroOneGame2(pot_size=2.0)

    assert game_small.value_threshold() < game_large.value_threshold()
    assert game_small.call_threshold() < game_large.call_threshold()
    assert game_small.bluff_threshold() > game_large.bluff_threshold()


def test_expected_value_matches_simulation():
    game = ZeroOneGame2(pot_size=1.0, num_buckets=10)
    analytic_ev = game.analytic_solution()["expected_value_x"]
    simulated_ev = simulate_expected_value(game, samples=20_000, seed=13)
    assert math.isclose(simulated_ev, analytic_ev, rel_tol=0.03, abs_tol=0.02)
