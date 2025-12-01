"""
Unit tests for the Clairvoyance Game implementation.
"""

import unittest
import numpy as np
import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch11.clairvoyance import ClairvoyanceGame


class TestClairvoyanceGame(unittest.TestCase):
    """Test cases for the Clairvoyance Game."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = ClairvoyanceGame(pot_size=1.0, bet_size=1.0)
    
    def test_initialization(self):
        """Test game initialization."""
        self.assertEqual(self.game.pot_size, 1.0)
        self.assertEqual(self.game.bet_size, 1.0)
    
    def test_payoff_matrix_shape(self):
        """Test that payoff matrices have correct shape."""
        payoff_x, payoff_y = self.game.get_payoff_matrix()
        
        # Should be 2x4 (2 X strategies, 4 Y strategies)
        self.assertEqual(payoff_x.shape, (2, 4))
        self.assertEqual(payoff_y.shape, (2, 4))
    
    def test_zero_sum_property(self):
        """Test that the game is zero-sum."""
        payoff_x, payoff_y = self.game.get_payoff_matrix()
        
        # Y's payoff should be negative of X's payoff
        np.testing.assert_array_almost_equal(payoff_y, -payoff_x)
    
    def test_strategy_labels(self):
        """Test strategy labels."""
        x_labels, y_labels = self.game.get_strategy_labels()
        
        self.assertEqual(len(x_labels), 2)
        self.assertEqual(len(y_labels), 4)
        self.assertIn("Fold", x_labels[0])
        self.assertIn("Call", x_labels[1])
    
    def test_nash_equilibrium_solution(self):
        """Test that Nash equilibrium solver returns valid solution."""
        solution = self.game.solve_nash_equilibrium()
        
        # Check that solution has required keys
        required_keys = ['x_strategy', 'y_strategy', 'game_value', 'x_labels', 'y_labels']
        for key in required_keys:
            self.assertIn(key, solution)
        
        # Check strategy shapes
        self.assertEqual(len(solution['x_strategy']), 2)
        self.assertEqual(len(solution['y_strategy']), 4)
        
        # Check that strategies are valid probability distributions
        np.testing.assert_almost_equal(np.sum(solution['x_strategy']), 1.0)
        np.testing.assert_almost_equal(np.sum(solution['y_strategy']), 1.0)
        
        # Check that all probabilities are non-negative
        self.assertTrue(np.all(solution['x_strategy'] >= 0))
        self.assertTrue(np.all(solution['y_strategy'] >= 0))
    
    def test_equilibrium_verification(self):
        """Test that the computed solution is indeed a Nash equilibrium."""
        solution = self.game.solve_nash_equilibrium()
        is_equilibrium = self.game.verify_equilibrium(solution)
        self.assertTrue(is_equilibrium)
        self.assertAlmostEqual(solution['call_probability'], 2 / 3)
        self.assertAlmostEqual(solution['bluff_fraction'], 1 / 3)
        self.assertAlmostEqual(solution['game_value'], -1 / 3)
    
    def test_different_bet_sizes(self):
        """Test game behavior with different bet sizes."""
        bet_sizes = [0.5, 1.0, 2.0, 5.0]
        
        for bet_size in bet_sizes:
            with self.subTest(bet_size=bet_size):
                game = ClairvoyanceGame(pot_size=1.0, bet_size=bet_size)
                solution = game.solve_nash_equilibrium()
                self.assertTrue(game.verify_equilibrium(solution))

                expected_bluff = bet_size / (2 * game.pot_size + bet_size)
                expected_call = (2 * game.pot_size) / (2 * game.pot_size + bet_size)

                self.assertAlmostEqual(solution['bluff_fraction'], expected_bluff)
                self.assertAlmostEqual(solution['call_probability'], expected_call)
                self.assertAlmostEqual(
                    solution['game_value'],
                    -game.pot_size * bet_size / (2 * game.pot_size + bet_size),
                )
    
    def test_payoff_calculation_edge_cases(self):
        """Test specific payoff calculations."""
        P = self.game.pot_size  # 1.0
        B = self.game.bet_size  # 1.0
        
        payoff_x, payoff_y = self.game.get_payoff_matrix()
        
        # When both players check (Y strategy 0), payoff should be 0
        self.assertAlmostEqual(payoff_x[0, 0], 0.0)  # X fold vs Y check
        self.assertAlmostEqual(payoff_x[1, 0], 0.0)  # X call vs Y check
        
        # When Y bets everything and X calls everything, EV should be 0
        self.assertAlmostEqual(payoff_x[1, 3], 0.0)  # X call vs Y bet always
    
    def test_strategy_interpretation(self):
        """Test strategy interpretation method."""
        solution = self.game.solve_nash_equilibrium()
        interpretation = self.game.get_mixed_strategy_interpretation(solution)
        
        self.assertIsInstance(interpretation, str)
        self.assertIn("call", interpretation.lower())
        self.assertIn("bet", interpretation.lower())
    
    def test_analysis_output(self):
        """Test strategy analysis output."""
        solution = self.game.solve_nash_equilibrium()
        analysis = self.game.analyze_strategies(solution)
        
        self.assertIsInstance(analysis, str)
        self.assertIn("OPTIMAL STRATEGIES", analysis)
        self.assertIn("Game Value", analysis)

    def test_mccfr_equilibrium(self):
        """Monte Carlo CFR should approximate the analytic equilibrium."""
        solution = self.game.solve_mccfr_equilibrium(iterations=40000, seed=1234)

        self.assertIn("info_set_strategies", solution)
        self.assertIn("info_set_regrets", solution)
        self.assertAlmostEqual(solution["call_probability"], 2 / 3, delta=0.05)
        self.assertAlmostEqual(solution["bluff_fraction"], 1 / 3, delta=0.05)
        self.assertAlmostEqual(solution["game_value"], -1 / 3, delta=0.05)

        expected_actions = {
            "Y:nuts": {"check", "bet"},
            "Y:bluff": {"check", "bet"},
            "X:bet_response": {"call", "fold"},
        }
        regrets = solution["info_set_regrets"]
        for key, actions in expected_actions.items():
            self.assertIn(key, regrets)
            self.assertEqual(set(regrets[key].keys()), actions)
            for value in regrets[key].values():
                self.assertIsInstance(value, float)


class TestClairvoyanceGameEdgeCases(unittest.TestCase):
    """Test edge cases for the Clairvoyance Game."""
    
    def test_very_small_bet(self):
        """Test with very small bet size."""
        game = ClairvoyanceGame(pot_size=1.0, bet_size=0.01)
        solution = game.solve_nash_equilibrium()
        self.assertTrue(game.verify_equilibrium(solution))
    
    def test_very_large_bet(self):
        """Test with very large bet size."""
        game = ClairvoyanceGame(pot_size=1.0, bet_size=100.0)
        solution = game.solve_nash_equilibrium()
        self.assertTrue(game.verify_equilibrium(solution))
    
    def test_different_pot_sizes(self):
        """Test with different pot sizes."""
        pot_sizes = [0.5, 2.0, 10.0]
        
        for pot_size in pot_sizes:
            with self.subTest(pot_size=pot_size):
                game = ClairvoyanceGame(pot_size=pot_size, bet_size=1.0)
                solution = game.solve_nash_equilibrium()
                self.assertTrue(game.verify_equilibrium(solution))


if __name__ == '__main__':
    unittest.main()