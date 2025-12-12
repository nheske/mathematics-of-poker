"""
Unit tests for the generic half-street zero-sum solver helpers.

These tests mirror the Clairvoyance game expectations but call the
protected `_solve_zero_sum_game` helper directly to ensure the linear
programming formulation produces the same strategies as the analytic
solution.
"""

import unittest
import numpy as np
import sys
import os

# Ensure the package root is on the path when tests are run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch11.clairvoyance import ClairvoyanceGame


class TestHalfStreetZeroSumSolver(unittest.TestCase):
    """Validate `_solve_zero_sum_game` against the analytic Clairvoyance solution."""

    def test_solver_matches_clairvoyance_equilibrium(self):
        """LP-based solver should reproduce the analytic Nash equilibrium."""
        game = ClairvoyanceGame(pot_size=1.0, bet_size=1.0)
        payoff_x, _ = game.get_payoff_matrix()

        solution = game.solve_nash_equilibrium()

        expected_call = (2 * game.pot_size) / (2 * game.pot_size + game.bet_size)
        expected_bluff = game.bet_size / (2 * game.pot_size + game.bet_size)

        expected_x = np.array([1.0 - expected_call, expected_call])
        expected_y = np.array([0.0, 1.0 - expected_bluff, 0.0, expected_bluff])
        expected_value = float(expected_x @ payoff_x @ expected_y)

        np.testing.assert_allclose(solution["x_strategy"], expected_x, atol=1e-9)
        np.testing.assert_allclose(solution["y_strategy"], expected_y, atol=1e-9)
        self.assertAlmostEqual(solution["game_value"], expected_value, places=9)

    def test_solver_handles_variable_bet_sizes(self):
        """Solver should track the analytic solution across different bet sizes."""
        pot_size = 1.0
        for bet_size in [0.25, 0.5, 1.0, 3.0, 10.0]:
            with self.subTest(bet_size=bet_size):
                game = ClairvoyanceGame(pot_size=pot_size, bet_size=bet_size)
                payoff_x, _ = game.get_payoff_matrix()

                solution = game.solve_nash_equilibrium()

                expected_call = (2 * pot_size) / (2 * pot_size + bet_size)
                expected_bluff = bet_size / (2 * pot_size + bet_size)

                expected_x = np.array([1.0 - expected_call, expected_call])
                expected_y = np.array([0.0, 1.0 - expected_bluff, 0.0, expected_bluff])
                expected_value = float(expected_x @ payoff_x @ expected_y)

                np.testing.assert_allclose(solution["x_strategy"], expected_x, atol=1e-9)
                np.testing.assert_allclose(solution["y_strategy"], expected_y, atol=1e-9)
                self.assertAlmostEqual(solution["game_value"], expected_value, places=9)

    def test_solver_handles_variable_pot_sizes(self):
        """Solver should track the analytic solution across different pot sizes."""
        bet_size = 1.0
        for pot_size in [0.5, 1.0, 2.5, 5.0, 20.0]:
            with self.subTest(pot_size=pot_size):
                game = ClairvoyanceGame(pot_size=pot_size, bet_size=bet_size)
                payoff_x, _ = game.get_payoff_matrix()

                solution = game.solve_nash_equilibrium()

                expected_call = (2 * pot_size) / (2 * pot_size + bet_size)
                expected_bluff = bet_size / (2 * pot_size + bet_size)

                expected_x = np.array([1.0 - expected_call, expected_call])
                expected_y = np.array([0.0, 1.0 - expected_bluff, 0.0, expected_bluff])
                expected_value = float(expected_x @ payoff_x @ expected_y)

                np.testing.assert_allclose(solution["x_strategy"], expected_x, atol=1e-9)
                np.testing.assert_allclose(solution["y_strategy"], expected_y, atol=1e-9)
                self.assertAlmostEqual(solution["game_value"], expected_value, places=9)


if __name__ == "__main__":
    unittest.main()
