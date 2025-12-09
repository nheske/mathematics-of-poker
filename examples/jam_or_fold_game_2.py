#!/usr/bin/env python3
"""Example driver for the [0,1] Jam-or-Fold Game #2 (Example 12.2)."""

from __future__ import annotations

import argparse
import os
import sys
from statistics import mean
from typing import Optional

# Ensure package imports work when running from the cloned repository
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch12 import (  # noqa: E402
    JamOrFoldGame2,
    simulate_expected_value_game2,
)
from mathematics_of_poker.utils.plotting import normalize_regret_values  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="[0,1] Jam-or-Fold Game #2 (Example 12.2)")
    parser.add_argument(
        "--stack",
        type=float,
        default=4.0,
        help="Effective stack size S in units (default: 4.0)",
    )
    parser.add_argument(
        "--buckets",
        type=int,
        default=40,
        help="Number of hand-strength buckets for MCCFR discretization (default: 40)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=250_000,
        help="Number of MCCFR iterations to run (default: 250000)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=100_000,
        help="Monte Carlo samples for EV estimation under analytic strategy (default: 100000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2025,
        help="Optional RNG seed for reproducibility",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Display matplotlib charts for jam/call frequencies and regrets",
    )
    parser.add_argument(
        "--plot-file",
        type=str,
        default=None,
        help="Optional path to save the diagnostics figure",
    )
    return parser.parse_args()


def print_analytic_summary(game: JamOrFoldGame2) -> dict:
    solution = game.analytic_solution()
    print("ANALYTIC SOLUTION")
    print("=================")
    print(f"Stack size (S):           {game.stack_size:.2f}")
    print(f"Regime:                   {solution['regime']}")
    print(f"Jam threshold (Y):        {solution['jam_threshold']:.4f}")
    print(f"Call threshold (X):       {solution['call_threshold']:.4f}")
    print(f"Jam frequency:            {solution['jam_frequency']:.4f}")
    print(f"Call frequency:           {solution['call_frequency']:.4f}")
    print(f"Attacker EV (chips):      {solution['attacker_value']:.4f}")
    print(f"Defender EV (chips):      {solution['defender_value']:.4f}")
    print()
    return solution


def run_monte_carlo(game: JamOrFoldGame2, samples: int, seed: Optional[int]) -> None:
    if samples <= 0:
        return
    estimate = simulate_expected_value_game2(game, samples=samples, seed=seed)
    analytic = game.analytic_solution()["attacker_value"]
    print("MONTE CARLO CHECK")
    print("=================")
    print(f"Samples:                  {samples}")
    print(f"Estimated EV (attacker):  {estimate:.4f}")
    print(f"Analytic EV (attacker):   {analytic:.4f}")
    print(f"Absolute error:           {abs(estimate - analytic):.4f}")
    print()


def run_mccfr(game: JamOrFoldGame2, iterations: int, seed: Optional[int]) -> dict:
    result = game.solve_mccfr_equilibrium(iterations=iterations, seed=seed)

    print("MCCFR DIAGNOSTICS")
    print("==================")
    print(
        "Estimated jam threshold:  "
        f"{result['estimated_jam_threshold']:.4f} (jam frequency over uniform buckets)"
    )
    print(
        "Estimated call threshold: "
        f"{result['estimated_call_threshold']:.4f} (call frequency over uniform buckets)"
    )
    print(
        "Jam bucket cutoff (≥50%):  "
        f"{result['jam_bucket_cutoff']:.4f}"
    )
    print(
        "Call bucket cutoff (≥50%): "
        f"{result['call_bucket_cutoff']:.4f}"
    )
    print(f"Game value (attacker):    {result['game_value']:.4f}")
    print(f"Attacker EV (MCCFR):      {result['attacker_value']:.4f}")
    print(f"Defender EV (MCCFR):      {result['defender_value']:.4f}")
    print()

    strategies = result["info_set_strategies"]
    jam_probs = [
        strategies[f"Y:bucket[{idx}]"].get("jam", 0.0)
        for idx in range(game.num_buckets)
    ]
    call_probs = [
        strategies[f"X:bucket[{idx}]"].get("call", 0.0)
        for idx in range(game.num_buckets)
    ]

    print("Sample bucket strategies (jam probability shown):")
    for idx in (0, game.num_buckets // 2, game.num_buckets - 1):
        strategy = strategies[f"Y:bucket[{idx}]"]
        print(f"  Y:bucket[{idx}]: jam={strategy.get('jam', 0.0):.3f}, fold={strategy.get('fold', 0.0):.3f}")
    print()

    def _avg(values: list[float]) -> float:
        return mean(values) if values else 0.0

    solution = game.analytic_solution()
    jam_threshold = solution["jam_threshold"]
    call_threshold = solution["call_threshold"]
    bucket_width = 1.0 / game.num_buckets

    cutoff_idx_jam = int(jam_threshold / bucket_width)
    cutoff_idx_call = int(call_threshold / bucket_width)

    avg_jam_value = _avg(jam_probs[: cutoff_idx_jam + 1])
    avg_jam_above = _avg(jam_probs[cutoff_idx_jam + 1 :])
    avg_call_value = _avg(call_probs[: cutoff_idx_call + 1])
    avg_call_above = _avg(call_probs[cutoff_idx_call + 1 :])

    print("Jam takeaway:")
    if (avg_jam_above or 0.0) <= 0.05:
        print(
            "  MCCFR converges to mostly value jams; bluff frequency is tiny above the threshold." 
        )
    else:
        print(
            "  MCCFR keeps a live bluff band above the threshold, reflecting the weaker showdown edge."
        )
    print(f"  Avg jam prob. ≤ jam threshold:  {avg_jam_value:.3f}")
    print(f"  Avg jam prob. > jam threshold:   {avg_jam_above:.3f}")
    print()

    print("Call takeaway:")
    if (avg_call_above or 0.0) <= 0.05:
        print(
            "  X folds most hands past the defend band—only true bluff-catchers continue." 
        )
    else:
        print(
            "  X continues with a wider defense above the analytic call point due to baseline equity." 
        )
    print(f"  Avg call prob. ≤ call threshold: {avg_call_value:.3f}")
    print(f"  Avg call prob. > call threshold:  {avg_call_above:.3f}")
    print()

    return {
        "result": result,
        "jam_probs": jam_probs,
        "call_probs": call_probs,
    }


def maybe_plot(game: JamOrFoldGame2, mccfr_pack: dict, output_path: Optional[str], show_plot: bool) -> None:
    if not show_plot and not output_path:
        return

    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:  # pragma: no cover
        print("matplotlib is not installed; skipping plot.")
        return

    result = mccfr_pack["result"]
    jam_probs = mccfr_pack["jam_probs"]
    call_probs = mccfr_pack["call_probs"]
    regrets = result.get("info_set_regrets", {})
    iterations = float(result.get("iterations", 0) or 0)

    normalized_regrets = {
        key: normalize_regret_values(regs, normalization=iterations)
        for key, regs in regrets.items()
    }

    buckets = range(game.num_buckets)

    fig, (ax_jam, ax_call) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax_jam.bar(buckets, jam_probs, color="#4C72B0")
    ax_jam.set_ylabel("Jam probability")
    ax_jam.set_title("Player Y average jam probability per bucket")
    ax_jam.set_ylim(0.0, 1.0)

    if normalized_regrets:
        jam_regrets = [normalized_regrets.get(f"Y:bucket[{idx}]", {}).get("jam", 0.0) for idx in buckets]
        ax_jam_twin = ax_jam.twinx()
        ax_jam_twin.plot(
            list(buckets),
            jam_regrets,
            color="#DD8452",
            label="Regret per iteration (jam)",
        )
        ax_jam_twin.set_ylabel("Regret per iteration")
        ax_jam_twin.legend(loc="upper right")

    ax_call.bar(buckets, call_probs, color="#55A868")
    ax_call.set_xlabel("Bucket index")
    ax_call.set_ylabel("Call probability")
    ax_call.set_title("Player X average call probability per bucket")
    ax_call.set_ylim(0.0, 1.0)

    if normalized_regrets:
        call_regrets = [normalized_regrets.get(f"X:bucket[{idx}]", {}).get("call", 0.0) for idx in buckets]
        ax_call_twin = ax_call.twinx()
        ax_call_twin.plot(
            list(buckets),
            call_regrets,
            color="#C44E52",
            label="Regret per iteration (call)",
        )
        ax_call_twin.set_ylabel("Regret per iteration")
        ax_call_twin.legend(loc="upper right")

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, bbox_inches="tight")
        print(f"Saved plot to {output_path}")

    backend = plt.get_backend().lower()
    non_interactive = any(tag in backend for tag in ("agg", "pdf", "svg", "ps", "cairo"))
    if show_plot and not non_interactive:
        plt.show()
    plt.close(fig)


def main() -> None:
    args = parse_args()

    stack_size = args.stack

    print("[0,1] JAM-OR-FOLD GAME #2")
    print("==========================")
    print(f"Stack size (S):   {stack_size:g}")
    print(f"Buckets:          {args.buckets}")
    print(f"Iterations:       {args.iterations}")
    print()

    game = JamOrFoldGame2(stack_size=stack_size, num_buckets=args.buckets)

    print(f"Stack size (S): {game.stack_size}")
    print(f"Big blind:      {game.big_blind}")
    print(f"Small blind:    {game.small_blind}")
    print()

    print_analytic_summary(game)
    run_monte_carlo(game, samples=args.samples, seed=args.seed)
    mccfr_pack = run_mccfr(game, iterations=args.iterations, seed=args.seed)

    maybe_plot(game, mccfr_pack, args.plot_file, args.plot)

    print("Done.")


if __name__ == "__main__":
    main()
