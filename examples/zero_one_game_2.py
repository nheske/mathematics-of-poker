"""CLI driver for Example 11.3 ([0, 1] Game #2 with fold option)."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

# Ensure package imports work when running from a cloned repository
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch11.zero_one_game_2 import (
    ZeroOneGame2,
    simulate_expected_value,
)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pot", type=float, default=1.0, help="Initial pot size P")
    parser.add_argument(
        "--buckets", type=int, default=40, help="Number of discretisation buckets for MCCFR"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=250_000,
        help="Number of MCCFR iterations to run",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for both Monte Carlo sampling and MCCFR",
    )
    parser.add_argument(
        "--simulate",
        type=int,
        default=0,
        help="If >0, number of Monte Carlo samples to estimate EV under analytic thresholds",
    )
    args = parser.parse_args(argv)

    game = ZeroOneGame2(pot_size=args.pot, num_buckets=args.buckets)

    analytic = game.analytic_solution()
    print("Analytic solution thresholds:")
    for key in ("value_threshold", "call_threshold", "bluff_threshold"):
        print(f"  {key.replace('_', ' ').title()}: {analytic[key]:.6f}")
    print(f"  Expected value for X: {analytic['expected_value_x']:.6f}")
    print(f"  Expected value for Y: {analytic['expected_value_y']:.6f}")

    if args.simulate > 0:
        ev = simulate_expected_value(game, samples=args.simulate, seed=args.seed)
        print(f"Monte Carlo EV estimate for X (samples={args.simulate}): {ev:.6f}")

    print("\nRunning MCCFR ...")
    result = game.solve_mccfr_equilibrium(iterations=args.iterations, seed=args.seed)
    print(f"  Estimated game value (X): {result['game_value']:.6f}")
    print(
        "  Estimated thresholds (value / bluff / call):",
        f"{result['estimated_value_threshold']:.3f}",
        f"{result['estimated_bluff_threshold']:.3f}",
        f"{result['estimated_call_threshold']:.3f}",
    )
    print(f"  Analytic thresholds: {analytic['value_threshold']:.3f} / {analytic['bluff_threshold']:.3f} / {analytic['call_threshold']:.3f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
