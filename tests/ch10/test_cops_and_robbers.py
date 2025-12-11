import pytest

from mathematics_of_poker.games.ch10 import CopsAndRobbersGame


def test_analytic_solution_default():
    game = CopsAndRobbersGame()
    solution = game.analytic_solution()

    assert solution["mix_x"]["patrol"] == pytest.approx(1 / 3)
    assert solution["mix_x"]["stand_down"] == pytest.approx(2 / 3)
    assert solution["mix_y"]["rob"] == pytest.approx(1 / 3)
    assert solution["mix_y"]["stay_home"] == pytest.approx(2 / 3)
    assert solution["game_value_x"] == pytest.approx(-1 / 3)
    assert solution["game_value_y"] == pytest.approx(1 / 3)


def test_mccfr_converges_to_equilibrium():
    game = CopsAndRobbersGame()
    result = game.solve_mccfr_equilibrium(iterations=80_000, seed=41)

    cop_strategy = result["info_set_strategies"]["X:choice"]
    robber_strategy = result["info_set_strategies"]["Y:choice"]

    assert cop_strategy["patrol"] == pytest.approx(1 / 3, abs=0.1)
    assert robber_strategy["rob"] == pytest.approx(1 / 3, abs=0.1)
    assert result["game_value"] == pytest.approx(-1 / 3, abs=0.1)
