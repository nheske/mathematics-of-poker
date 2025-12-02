import math

from mathematics_of_poker.games.ch12 import (
    JamOrFoldGame1,
    simulate_expected_value_jam_or_fold_game1,
)


def test_analytic_thresholds_match_closed_form():
    stacks = [1.0, 2.0, 5.0, 10.0]
    for stack in stacks:
        game = JamOrFoldGame1(stack_size=stack)
        solution = game.analytic_solution()
        jam = solution["jam_threshold"]
        call = solution["call_threshold"]

        expected_call = 1.5 / (stack + 1.0)
        expected_jam = 3.0 * stack / ((stack + 1.0) ** 2)

        assert math.isclose(jam, expected_jam, rel_tol=1e-9, abs_tol=1e-9)
        assert math.isclose(call, expected_call, rel_tol=1e-9, abs_tol=1e-9)


def test_monte_carlo_matches_analytic_value():
    game = JamOrFoldGame1(stack_size=5.0)
    analytic = game.analytic_solution()["attacker_value"]
    estimate = simulate_expected_value_jam_or_fold_game1(game, samples=200_000, seed=1234)
    assert abs(estimate - analytic) < 0.02


def test_mccfr_recovers_thresholds():
    game = JamOrFoldGame1(stack_size=5.0, num_buckets=40)
    result = game.solve_mccfr_equilibrium(iterations=150_000, seed=2025)

    analytic = game.analytic_solution()

    # Estimated thresholds should fall on the analytic bucket grid when the
    # discretised MCCFR strategies track the threshold behaviour.
    assert result["estimated_jam_threshold"] <= analytic["jam_threshold"] + 0.15
    assert result["estimated_call_threshold"] <= analytic["call_threshold"] + 0.15

    # Game value should beat the trivial always-fold strategy (-small blind)
    assert result["game_value"] > -game.small_blind - 0.05
