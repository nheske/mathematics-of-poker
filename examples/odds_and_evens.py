#!/usr/bin/env python3
"""CLI driver for the Odds and Evens matrix game."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

# Allow running from a checked-out repository without installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch10 import OddsAndEvensGame  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Odds and Evens (Chapter 10)")
    parser.add_argument(
        "--iterations",
        type=int,
        default=10_000,
        help="Number of MCCFR iterations to run (default: 10000)",
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
        help="Chip value awarded to the winner (default: 1.0)",
    )
    return parser.parse_args()


def print_analytic_summary(game: OddsAndEvensGame) -> None:
    solution = game.analytic_solution()
    print("ANALYTIC EQUILIBRIUM")
    print("=====================")
    print(f"Y (evens) mix on penny: {solution['mix_y_penny']:.3f}")
    print(f"X (odds) mix on penny:  {solution['mix_x_penny']:.3f}")
    print(f"Game value to Y:        {solution['game_value_y']:.3f}")
    print(f"Game value to X:        {solution['game_value_x']:.3f}")
    print()


def run_mccfr(game: OddsAndEvensGame, iterations: int, seed: Optional[int]) -> dict:
    result = game.solve_mccfr_equilibrium(iterations=iterations, seed=seed)

    print("MCCFR DIAGNOSTICS")
    print("==================")
    print(f"Iterations:             {iterations}")
    print(f"Estimated EV (Player X): {result['game_value']:.4f}")

    y_strategy = result["info_set_strategies"]["Y:choice"]
    x_strategy = result["info_set_strategies"]["X:choice"]
    print(f"Y strategy:             none={y_strategy['none']:.3f}, penny={y_strategy['penny']:.3f}")
    print(f"X strategy:             none={x_strategy['none']:.3f}, penny={x_strategy['penny']:.3f}")
    print()

    return result


def main() -> None:
    args = parse_args()

    game = OddsAndEvensGame(payoff=args.payoff)

    print("ODDS AND EVENS (Chapter 10)")
    print("===========================")
    print(f"Payoff per win: {game.payoff:.2f}")
    print()

    print_analytic_summary(game)
    run_mccfr(game, iterations=args.iterations, seed=args.seed)

    print("Done.")


if __name__ == "__main__":
    main()
