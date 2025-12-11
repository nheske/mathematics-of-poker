import pytest

from mathematics_of_poker.games.ch10 import RoshamboSGame


def test_analytic_solution_scissors_bonus_default():
    game = RoshamboSGame()
    solution = game.analytic_solution()

    expected = {"rock": 0.5, "paper": 0.25, "scissors": 0.25}
    for action, prob in expected.items():
        assert solution["mix_x"][action] == pytest.approx(prob)
        assert solution["mix_y"][action] == pytest.approx(prob)
    assert solution["game_value_x"] == pytest.approx(0.0)
    assert solution["game_value_y"] == pytest.approx(0.0)


def test_analytic_solution_scales_with_bonus():
    game = RoshamboSGame(payoff=2.0, scissor_bonus=6.0)
    solution = game.analytic_solution()

    ratio = game.scissor_bonus / game.payoff
    denom = 2.0 + ratio
    expected_rock = ratio / denom
    expected_other = 1.0 / denom

    assert solution["mix_x"]["rock"] == pytest.approx(expected_rock)
    assert solution["mix_x"]["paper"] == pytest.approx(expected_other)
    assert solution["mix_x"]["scissors"] == pytest.approx(expected_other)


def test_mccfr_converges_to_nash_mix():
    game = RoshamboSGame()
    result = game.solve_mccfr_equilibrium(iterations=60_000, seed=19)

    expected = {"rock": 0.5, "paper": 0.25, "scissors": 0.25}
    y_strategy = result["info_set_strategies"]["Y:choice"]
    x_strategy = result["info_set_strategies"]["X:choice"]

    for action, prob in expected.items():
        assert y_strategy[action] == pytest.approx(prob, abs=0.1)
        assert x_strategy[action] == pytest.approx(prob, abs=0.1)

    assert result["game_value"] == pytest.approx(0.0, abs=0.1)
