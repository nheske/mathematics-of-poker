import pytest

from mathematics_of_poker.games.ch10 import RoshamboFGame


def test_analytic_solution_ignores_flower():
    game = RoshamboFGame()
    solution = game.analytic_solution()

    expected = {"rock": 1 / 3, "paper": 1 / 3, "scissors": 1 / 3, "flower": 0.0}
    for action, prob in expected.items():
        assert solution["mix_x"][action] == pytest.approx(prob)
        assert solution["mix_y"][action] == pytest.approx(prob)

    assert solution["game_value_x"] == pytest.approx(0.0)
    assert solution["game_value_y"] == pytest.approx(0.0)


def test_mccfr_downweights_flower():
    game = RoshamboFGame()
    result = game.solve_mccfr_equilibrium(iterations=80_000, seed=29)

    y_strategy = result["info_set_strategies"]["Y:choice"]
    x_strategy = result["info_set_strategies"]["X:choice"]

    for action in ("rock", "paper", "scissors"):
        assert y_strategy[action] == pytest.approx(1 / 3, abs=0.1)
        assert x_strategy[action] == pytest.approx(1 / 3, abs=0.1)

    assert y_strategy["flower"] <= 0.1
    assert x_strategy["flower"] <= 0.1
    assert result["game_value"] == pytest.approx(0.0, abs=0.1)
