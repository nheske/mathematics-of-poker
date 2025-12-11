#!/usr/bin/env python3
"""CLI runner for the Cops and Robbers matrix game."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch10 import CopsAndRobbersGame  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cops and Robbers (Chapter 10)")
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
        "--patrol-cost",
        type=float,
        default=1.0,
        help="Cost to the cop for patrolling when the robber stays home (default: 1.0)",
    )
    parser.add_argument(
        "--arrest-reward",
        type=float,
        default=1.0,
        help="Reward to the cop for arresting a robbing burglar (default: 1.0)",
    )
    parser.add_argument(
        "--robbery-reward",
        type=float,
        default=1.0,
        help="Reward to the robber when no patrol occurs and he robs (default: 1.0)",
    )
    return parser.parse_args()


def print_analytic_summary(game: CopsAndRobbersGame) -> None:
    solution = game.analytic_solution()
    print("ANALYTIC EQUILIBRIUM")
    print("=====================")
    cop_mix = solution["mix_x"]
    robber_mix = solution["mix_y"]
    print(
        f"Cop mix: patrol={cop_mix['patrol']:.3f}, stand_down={cop_mix['stand_down']:.3f}"
    )
    print(
        f"Robber mix: rob={robber_mix['rob']:.3f}, stay_home={robber_mix['stay_home']:.3f}"
    )
    print(f"Game value to Cop (X): {solution['game_value_x']:.3f}")
    print(f"Game value to Robber (Y): {solution['game_value_y']:.3f}")
    print()


def run_mccfr(game: CopsAndRobbersGame, iterations: int, seed: Optional[int]) -> dict:
    result = game.solve_mccfr_equilibrium(iterations=iterations, seed=seed)

    print("MCCFR DIAGNOSTICS")
    print("==================")
    print(f"Iterations:              {iterations}")
    print(f"Estimated EV (Player X): {result['game_value']:.4f}")

    cop_strategy = result["info_set_strategies"]["X:choice"]
    robber_strategy = result["info_set_strategies"]["Y:choice"]
    print(
        "Cop strategy:          patrol={patrol:.3f}, stand_down={stand_down:.3f}".format(
            **cop_strategy
        )
    )
    print(
        "Robber strategy:       rob={rob:.3f}, stay_home={stay_home:.3f}".format(
            **robber_strategy
        )
    )
    print()

    return result


def main() -> None:
    args = parse_args()

    game = CopsAndRobbersGame(
        patrol_cost=args.patrol_cost,
        arrest_reward=args.arrest_reward,
        robbery_reward=args.robbery_reward,
    )

    print("COPS AND ROBBERS (Chapter 10)")
    print("=============================")
    print(f"Patrol cost:     {game.patrol_cost:.2f}")
    print(f"Arrest reward:   {game.arrest_reward:.2f}")
    print(f"Robbery reward:  {game.robbery_reward:.2f}")
    print()

    print_analytic_summary(game)
    run_mccfr(game, iterations=args.iterations, seed=args.seed)

    print("Done.")


if __name__ == "__main__":
    main()
