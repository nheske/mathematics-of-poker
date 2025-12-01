"""Tests for the Clairvoyance extensive-form game tree."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mathematics_of_poker.games.ch11.clairvoyance import ClairvoyanceGame
from mathematics_of_poker.games.game_tree import ChanceDistribution, Player


class TestClairvoyanceGameTree(unittest.TestCase):
    def setUp(self) -> None:
        self.game = ClairvoyanceGame(pot_size=1.5, bet_size=2.0)
        self.tree = self.game.build_game_tree()
        self.P = self.game.pot_size
        self.B = self.game.bet_size

    def test_root_structure(self):
        root = self.tree.root
        self.assertEqual(root.player, Player.CHANCE)
        self.assertEqual(len(root.edges), 2)

        probabilities = {edge.action: edge.probability for edge in root.edges}
        self.assertAlmostEqual(probabilities["Y hand = nuts"], 0.5)
        self.assertAlmostEqual(probabilities["Y hand = bluff"], 0.5)

        hands = {edge.metadata["hand"] for edge in root.edges if edge.metadata}
        self.assertSetEqual(hands, {"nuts", "bluff"})
        for edge in root.edges:
            self.assertIs(edge.child.parent, root)
            self.assertEqual(edge.child.action_from_parent, edge.action)

    def test_information_sets(self):
        info_sets = self.tree.information_sets
        self.assertIn("Y:nuts", info_sets)
        self.assertIn("Y:bluff", info_sets)
        self.assertIn("X:bet_response", info_sets)

        x_info = info_sets["X:bet_response"]
        self.assertEqual(x_info.player, Player.X)
        self.assertEqual(len(x_info.nodes), 2)  # one for nuts path, one for bluff path

        y_nuts_info = info_sets["Y:nuts"]
        self.assertEqual(len(y_nuts_info.nodes), 1)
        y_bluff_info = info_sets["Y:bluff"]
        self.assertEqual(len(y_bluff_info.nodes), 1)

    def test_terminal_payoffs(self):
        root = self.tree.root
        nuts_node = next(edge.child for edge in root.edges if edge.action == "Y hand = nuts")
        bluff_node = next(edge.child for edge in root.edges if edge.action == "Y hand = bluff")

        # Y checks with nuts -> X loses pot
        nuts_check = next(edge.child for edge in nuts_node.edges if edge.action == "check")
        self.assertTrue(nuts_check.is_terminal)
        self.assertEqual(nuts_check.payoffs, (-self.P, self.P))

        # Y bets with nuts, X responds
        nuts_bet_edge = next(edge for edge in nuts_node.edges if edge.action == "bet")
        nuts_bet = nuts_bet_edge.child
        self.assertEqual(nuts_bet.info_set.key, "X:bet_response")
        self.assertEqual(nuts_bet_edge.metadata["bet_size"], self.B)
        nuts_fold = next(edge.child for edge in nuts_bet.edges if edge.action == "fold")
        nuts_call = next(edge.child for edge in nuts_bet.edges if edge.action == "call")
        self.assertEqual(nuts_fold.payoffs, (-self.P, self.P))
        self.assertEqual(nuts_call.payoffs, (-(self.P + self.B), self.P + self.B))
        for edge in nuts_bet.edges:
            self.assertIsNotNone(edge.metadata)
            self.assertIn(edge.metadata["response"], {"fold", "call"})

        # Y checks with bluff -> X wins pot
        bluff_check = next(edge.child for edge in bluff_node.edges if edge.action == "check")
        self.assertEqual(bluff_check.payoffs, (self.P, -self.P))

        bluff_bet_edge = next(edge for edge in bluff_node.edges if edge.action == "bet")
        bluff_bet = bluff_bet_edge.child
        self.assertEqual(bluff_bet.info_set.key, "X:bet_response")
        self.assertIsNotNone(bluff_bet_edge.metadata)
        self.assertEqual(bluff_bet_edge.metadata["bet_size"], self.B)
        bluff_fold = next(edge.child for edge in bluff_bet.edges if edge.action == "fold")
        bluff_call = next(edge.child for edge in bluff_bet.edges if edge.action == "call")
        self.assertEqual(bluff_fold.payoffs, (-self.P, self.P))
        self.assertEqual(bluff_call.payoffs, (self.P + self.B, -(self.P + self.B)))

    def test_tree_dump_contains_metadata(self):
        dump = self.tree.dump()
        self.assertIn("chance", dump)
        self.assertIn("bet_size", dump)
        self.assertIn("Terminal", dump)

    def test_chance_distribution_validation(self):
        dist = ChanceDistribution((("a", 0.7), ("b", 0.3)))
        dist.validate()  # should not raise

        with self.assertRaises(ValueError):
            ChanceDistribution((("only", 0.6),)).validate()


if __name__ == "__main__":
    unittest.main()
