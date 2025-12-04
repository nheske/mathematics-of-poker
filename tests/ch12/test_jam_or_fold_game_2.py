from __future__ import annotations

import math

import pytest

from mathematics_of_poker.games.ch12 import (
    JamOrFoldGame2,
    simulate_expected_value_game2,
)


@pytest.mark.parametrize(
    "stack_size, expected_jam, expected_call, regime",
    [
        (1.0, 0.75, 1.0, "S ≤ 3"),
        (2.0, 6.0 / 7.0, 1.0, "S ≤ 3"),
        (4.0, 12.0 / 19.0, 21.0 / 38.0, "S > 3"),
    ],
)
def test_analytic_thresholds(stack_size: float, expected_jam: float, expected_call: float, regime: str) -> None:
    game = JamOrFoldGame2(stack_size=stack_size)
    solution = game.analytic_solution()
    assert math.isclose(solution["jam_threshold"], expected_jam, rel_tol=1e-6)
    assert math.isclose(solution["call_threshold"], expected_call, rel_tol=1e-6)
    assert solution["regime"] == regime


def test_monte_carlo_matches_analytic_value() -> None:
    game = JamOrFoldGame2(stack_size=3.0)
    analytic = game.analytic_solution()["attacker_value"]
    estimate = simulate_expected_value_game2(game, samples=150_000, seed=17)
    assert estimate == pytest.approx(analytic, abs=0.02)


def test_mccfr_converges_to_thresholds() -> None:
    game = JamOrFoldGame2(stack_size=4.0, num_buckets=30)
    result = game.solve_mccfr_equilibrium(iterations=120_000, seed=2025)
    analytic = game.analytic_solution()

    assert 0.0 <= result["jam_frequency"] <= 1.0
    assert 0.0 <= result["call_frequency"] <= 1.0
    assert abs(result["jam_frequency"] - analytic["jam_frequency"]) < 0.2
    assert abs(result["call_frequency"] - analytic["call_frequency"]) < 0.2
    assert result["game_value"] > -game.small_blind
