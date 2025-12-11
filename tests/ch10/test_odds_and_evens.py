import pytest

from mathematics_of_poker.games.ch10 import OddsAndEvensGame


def test_analytic_solution_symmetry():
    game = OddsAndEvensGame()
    solution = game.analytic_solution()

    assert solution["game_value_y"] == pytest.approx(0.0)
    assert solution["game_value_x"] == pytest.approx(0.0)
    assert solution["mix_y_penny"] == pytest.approx(0.5)
    assert solution["mix_x_penny"] == pytest.approx(0.5)


def test_mccfr_converges_to_mixed_strategy():
    game = OddsAndEvensGame()
    result = game.solve_mccfr_equilibrium(iterations=20_000, seed=7)

    y_strategy = result["info_set_strategies"]["Y:choice"]
    x_strategy = result["info_set_strategies"]["X:choice"]

    assert y_strategy["penny"] == pytest.approx(0.5, abs=0.1)
    assert x_strategy["penny"] == pytest.approx(0.5, abs=0.1)
    assert result["game_value"] == pytest.approx(0.0, abs=0.1)
