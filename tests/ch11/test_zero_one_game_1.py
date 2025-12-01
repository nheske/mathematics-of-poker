"""Tests for the [0, 1] Game #1 implementation."""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mathematics_of_poker.games.ch11.zero_one_game_1 import (
    ZeroOneGame1,
    simulate_expected_value,
)


@pytest.mark.parametrize("num_buckets", [10, 30])
def test_optimal_threshold_and_expected_value(num_buckets: int) -> None:
    game = ZeroOneGame1(num_buckets=num_buckets)
    solution = game.analytic_solution()

    assert pytest.approx(0.5) == solution["threshold"]
    assert pytest.approx(-0.25, abs=1e-9) == solution["expected_value_x"]
    assert pytest.approx(0.25, abs=1e-9) == solution["expected_value_y"]


def test_monte_carlo_matches_analytic() -> None:
    game = ZeroOneGame1(num_buckets=40)
    mc_estimate = simulate_expected_value(game, samples=50_000, seed=2025)
    analytic = game.expected_value_x()
    assert math.isclose(mc_estimate, analytic, rel_tol=0.05, abs_tol=0.02)


def test_mccfr_threshold_alignment() -> None:
    game = ZeroOneGame1(num_buckets=15)
    result = game.solve_mccfr_equilibrium(iterations=80_000, seed=42)

    assert "info_set_strategies" in result
    assert result["num_buckets"] == 15

    estimated = result["estimated_threshold"]
    assert pytest.approx(0.5, abs=0.1) == estimated

    game_value = result["game_value"]
    analytic_value = game.expected_value_x()
    assert math.isclose(game_value, analytic_value, rel_tol=0.15, abs_tol=0.05)

    first_bucket = result["info_set_strategies"]["Y:bucket[0]"]
    last_bucket = result["info_set_strategies"]["Y:bucket[14]"]
    assert first_bucket["bet"] > 0.6
    assert last_bucket["bet"] < 0.4
