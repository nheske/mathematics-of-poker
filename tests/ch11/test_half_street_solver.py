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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mathematics_of_poker.games.ch11.clairvoyance import ClairvoyanceGame


class TestHalfStreetZeroSumSolver(unittest.TestCase):
    """Validate `_solve_zero_sum_game` against the analytic Clairvoyance solution."""

    def test_solver_matches_clairvoyance_equilibrium(self):
        """LP-based solver should reproduce the analytic Nash equilibrium."""
        game = ClairvoyanceGame(pot_size=1.0, bet_size=1.0)
        payoff_x, payoff_y = game.get_payoff_matrix()

        x_strategy, y_strategy, game_value = game._solve_zero_sum_game(payoff_y.T)
        solution = game.solve_nash_equilibrium()

        np.testing.assert_allclose(x_strategy, solution["x_strategy"], atol=1e-6)
        np.testing.assert_allclose(y_strategy, solution["y_strategy"], atol=1e-6)
        self.assertAlmostEqual(game_value, solution["game_value"], places=6)

    def test_solver_handles_variable_bet_sizes(self):
        """Solver should track the analytic solution across different bet sizes."""
        pot_size = 1.0
        for bet_size in [0.25, 0.5, 1.0, 3.0, 10.0]:
            with self.subTest(bet_size=bet_size):
                game = ClairvoyanceGame(pot_size=pot_size, bet_size=bet_size)
                payoff_x, payoff_y = game.get_payoff_matrix()

                x_strategy, y_strategy, game_value = game._solve_zero_sum_game(payoff_y.T)
                solution = game.solve_nash_equilibrium()

                np.testing.assert_allclose(x_strategy, solution["x_strategy"], atol=1e-6)
                np.testing.assert_allclose(y_strategy, solution["y_strategy"], atol=1e-6)
                self.assertAlmostEqual(game_value, solution["game_value"], places=6)

    def test_solver_handles_variable_pot_sizes(self):
        """Solver should track the analytic solution across different pot sizes."""
        bet_size = 1.0
        for pot_size in [0.5, 1.0, 2.5, 5.0, 20.0]:
            with self.subTest(pot_size=pot_size):
                game = ClairvoyanceGame(pot_size=pot_size, bet_size=bet_size)
                payoff_x, payoff_y = game.get_payoff_matrix()

                x_strategy, y_strategy, game_value = game._solve_zero_sum_game(payoff_y.T)
                solution = game.solve_nash_equilibrium()

                np.testing.assert_allclose(x_strategy, solution["x_strategy"], atol=1e-6)
                np.testing.assert_allclose(y_strategy, solution["y_strategy"], atol=1e-6)
                self.assertAlmostEqual(game_value, solution["game_value"], places=6)


if __name__ == "__main__":
    unittest.main()
