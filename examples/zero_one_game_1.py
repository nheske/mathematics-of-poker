#!/usr/bin/env python3
"""Example driver for the [0,1] Game #1 (Example 11.2) from *The Mathematics of Poker*."""

import argparse
import os
import sys
from textwrap import indent
from typing import Optional

# Ensure package imports work when running from cloned repo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch11.zero_one_game_1 import (  # noqa: E402
    ZeroOneGame1,
    simulate_expected_value,
)
from mathematics_of_poker.utils.plotting import normalize_regret_values  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="[0,1] Game #1 example (Example 11.2)")
    parser.add_argument(
        "--buckets",
        type=int,
        default=40,
    help="Number of buckets for discretizing the [0,1] interval (default: 40)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=120_000,
        help="MCCFR iterations to run (default: 120000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2025,
        help="Optional RNG seed for reproducibility",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=50_000,
        help="Monte Carlo samples for EV estimation (default: 50000)",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Display matplotlib bar charts for bucket strategies and regrets",
    )
    parser.add_argument(
        "--plot-file",
        type=str,
        default=None,
        help="Optional path to save the MCCFR diagnostics figure",
    )
    return parser.parse_args()


def print_analytic_summary(game: ZeroOneGame1) -> None:
    solution = game.analytic_solution()
    print("ANALYTIC SOLUTION")
    print("===================")
    print(f"Threshold (Y bets below this hand strength): {solution['threshold']:.4f}")
    print(f"Player X expected value: {solution['expected_value_x']:.4f}")
    print(f"Player Y expected value: {solution['expected_value_y']:.4f}")
    print(f"Betting region: {solution['bet_region']}")
    print(f"Checking region: {solution['check_region']}")
    print()


def run_monte_carlo(game: ZeroOneGame1, samples: int, seed: Optional[int]) -> None:
    print("MONTE CARLO CHECK")
    print("==================")
    estimate = simulate_expected_value(game, samples=samples, seed=seed)
    analytic = game.expected_value_x()
    print(f"Estimated EV for Player X: {estimate:.4f}")
    print(f"Analytic EV:               {analytic:.4f}")
    print(f"Absolute error:            {abs(estimate - analytic):.4f}")
    print()


def run_mccfr(game: ZeroOneGame1, iterations: int, seed: Optional[int]) -> dict:
    print("MCCFR DIAGNOSTICS")
    print("==================")
    result = game.solve_mccfr_equilibrium(iterations=iterations, seed=seed)
    print(f"Iterations:        {iterations}")
    print(f"Buckets:           {result['num_buckets']}")
    print(f"Estimated thresh.: {result['estimated_threshold']:.4f}")
    print(f"Analytic thresh.:  {result['optimal_threshold']:.4f}")
    print(f"Game value (X):    {result['game_value']:.4f}")
    print()

    sample_keys = [f"Y:bucket[{idx}]" for idx in (0, result['num_buckets'] // 2, result['num_buckets'] - 1)]
    print("Sample bucket strategies (bet probability shown):")
    for key in sample_keys:
        strategy = result["info_set_strategies"].get(key, {})
        summary = ", ".join(f"{action}={prob:.3f}" for action, prob in strategy.items())
        print(f"  {key}: {summary}")
    print()

    def _bucket_index(info_key: str) -> int:
        try:
            return int(info_key.split("[")[1][:-1])
        except (IndexError, ValueError):  # pragma: no cover - defensive
            return -1

    half_bucket = result["num_buckets"] // 2
    low_region = []
    high_region = []
    for info_key, strategy in result["info_set_strategies"].items():
        bucket_idx = _bucket_index(info_key)
        if bucket_idx == -1:
            continue
        prob = strategy.get("bet", 0.0)
        if bucket_idx < half_bucket:
            low_region.append(prob)
        else:
            high_region.append(prob)

    avg_low = sum(low_region) / len(low_region) if low_region else 0.0
    avg_high = sum(high_region) / len(high_region) if high_region else 0.0
    max_high = max(high_region) if high_region else 0.0

    print("Bluffing takeaway:")
    if max_high <= 0.05:
        print(
            "  MCCFR confirms Y's optimal play is a pure value bet region—betting dries up"
            " above the threshold, so bluffing provides no gain in this structure."
        )
    else:
        print(
            "  Some buckets above the threshold still mix in bets; consider raising iterations"
            " or buckets if you expect a sharper no-bluff result."
        )
    print(f"  Avg bet prob. below threshold buckets:  {avg_low:.3f}")
    print(f"  Avg bet prob. above threshold buckets: {avg_high:.3f}")
    print()
    return result


def maybe_plot(result: dict, output_path: Optional[str]) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:  # pragma: no cover
        print("matplotlib is not installed; skipping plot.")
        return

    strategies = result["info_set_strategies"]
    regrets = result.get("info_set_regrets") or {}
    normalization = float(result.get("iterations", 0) or 0)
    normalized_regrets = {
        key: normalize_regret_values(regret_dict, normalization=normalization)
        for key, regret_dict in regrets.items()
    }
    buckets = sorted(strategies.keys(), key=lambda k: int(k.split("[")[1][:-1]))

    bet_probs = [strategies[key].get("bet", 0.0) for key in buckets]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(range(len(buckets)), bet_probs, color="#4C72B0")
    ax.set_title("Average bet probability per bucket")
    ax.set_xlabel("Y bucket index")
    ax.set_ylabel("Bet probability")
    ax.set_ylim(0.0, 1.0)

    if normalized_regrets:
        ax2 = ax.twinx()
        regret_vals = [normalized_regrets.get(key, {}).get("bet", 0.0) for key in buckets]
        ax2.plot(
            range(len(buckets)),
            regret_vals,
            color="#DD8452",
            label="Normalised regret (bet)",
        )
        ax2.set_ylabel("Regret per iteration")
        ax2.legend(loc="upper right")

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, bbox_inches="tight")
        print(f"Saved plot to {output_path}")

    backend = plt.get_backend().lower()
    non_interactive = any(tag in backend for tag in ("agg", "pdf", "svg", "ps", "cairo"))
    if not non_interactive:
        plt.show()
    plt.close(fig)


def main() -> None:
    args = parse_args()

    game = ZeroOneGame1(num_buckets=args.buckets)

    print("[0,1] GAME #1")
    print("==============")
    print(f"Pot size: {game.pot_size}")
    print(f"Bet size: {game.bet_size}")
    print(f"Buckets:  {game.num_buckets}")
    print()

    print_analytic_summary(game)
    run_monte_carlo(game, samples=args.samples, seed=args.seed)
    result = run_mccfr(game, iterations=args.iterations, seed=args.seed)

    if args.plot or args.plot_file:
        if "info_set_strategy" not in result:
            # ensure regrets are available (they will be if MonteCarloCFR exposes them)
            pass
        maybe_plot(result, args.plot_file)

    print("Done.")


if __name__ == "__main__":
    main()
