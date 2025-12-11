import pytest

from mathematics_of_poker.games.ch10 import RoshamboGame


def test_analytic_solution_uniform_mix():
    game = RoshamboGame()
    solution = game.analytic_solution()

    for mix in (solution["mix_y"], solution["mix_x"]):
        assert sum(mix.values()) == pytest.approx(1.0)
        for prob in mix.values():
            assert prob == pytest.approx(1.0 / 3.0)

    assert solution["game_value_y"] == pytest.approx(0.0)
    assert solution["game_value_x"] == pytest.approx(0.0)


def test_mccfr_converges_to_uniform_mix():
    game = RoshamboGame()
    result = game.solve_mccfr_equilibrium(iterations=50_000, seed=11)

    y_strategy = result["info_set_strategies"]["Y:choice"]
    x_strategy = result["info_set_strategies"]["X:choice"]

    for strategy in (y_strategy, x_strategy):
        assert strategy["rock"] == pytest.approx(1.0 / 3.0, abs=0.1)
        assert strategy["paper"] == pytest.approx(1.0 / 3.0, abs=0.1)
        assert strategy["scissors"] == pytest.approx(1.0 / 3.0, abs=0.1)

    assert result["game_value"] == pytest.approx(0.0, abs=0.1)
