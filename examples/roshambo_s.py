#!/usr/bin/env python3
"""CLI runner for the Roshambo-S (scissors bonus) matrix game."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch10 import RoshamboSGame  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roshambo-S (scissors bonus variant)")
    parser.add_argument(
        "--iterations",
        type=int,
        default=20_000,
        help="Number of MCCFR iterations to run (default: 20000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2025,
        help="Optional RNG seed for reproducibility",
    )
    parser.add_argument(
        "--payoff",
        type=float,
        default=1.0,
        help="Chip value for non-scissor wins (default: 1.0)",
    )
    parser.add_argument(
        "--bonus",
        type=float,
        default=2.0,
        help="Chip value for wins achieved with scissors (default: 2.0)",
    )
    return parser.parse_args()


def print_analytic_summary(game: RoshamboSGame) -> None:
    solution = game.analytic_solution()
    print("ANALYTIC EQUILIBRIUM")
    print("=====================")
    for player, mix in (("Y", solution["mix_y"]), ("X", solution["mix_x"])):
        print(
            f"{player} mix: rock={mix['rock']:.3f}, paper={mix['paper']:.3f}, scissors={mix['scissors']:.3f}"
        )
    print(f"Game value to Y: {solution['game_value_y']:.3f}")
    print(f"Game value to X: {solution['game_value_x']:.3f}")
    print()


def run_mccfr(game: RoshamboSGame, iterations: int, seed: Optional[int]) -> dict:
    result = game.solve_mccfr_equilibrium(iterations=iterations, seed=seed)

    print("MCCFR DIAGNOSTICS")
    print("==================")
    print(f"Iterations:              {iterations}")
    print(f"Estimated EV (Player X): {result['game_value']:.4f}")

    y_strategy = result["info_set_strategies"]["Y:choice"]
    x_strategy = result["info_set_strategies"]["X:choice"]
    print(
        "Y strategy:             rock={rock:.3f}, paper={paper:.3f}, scissors={scissors:.3f}".format(
            **y_strategy
        )
    )
    print(
        "X strategy:             rock={rock:.3f}, paper={paper:.3f}, scissors={scissors:.3f}".format(
            **x_strategy
        )
    )
    print()

    return result


def main() -> None:
    args = parse_args()

    game = RoshamboSGame(payoff=args.payoff, scissor_bonus=args.bonus)

    print("ROSHAMBO-S (Chapter 10)")
    print("======================")
    print(f"Payoff per non-scissor win: {game.payoff:.2f}")
    print(f"Payoff per scissor win:     {game.scissor_bonus:.2f}")
    print()

    print_analytic_summary(game)
    run_mccfr(game, iterations=args.iterations, seed=args.seed)

    print("Done.")


if __name__ == "__main__":
    main()
