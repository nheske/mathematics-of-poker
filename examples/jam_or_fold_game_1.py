#!/usr/bin/env python3
"""Example driver for the [0,1] Jam-or-Fold Game #1 (Example 12.1)."""

import argparse
import os
import sys
from typing import Optional

# Ensure package imports work when running from a cloned repository
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch12 import (  # noqa: E402
    JamOrFoldGame1,
    simulate_expected_value_jam_or_fold_game1,
)
from mathematics_of_poker.utils.plotting import normalize_regret_values  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Jam-or-Fold Game #1 (Example 12.1)")
    parser.add_argument(
        "--stack",
        type=float,
        default=10.0,
        help="Effective stack size S in units (default: 10)",
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


def print_analytic_summary(game: JamOrFoldGame1) -> dict:
    solution = game.analytic_solution()
    print("ANALYTIC SOLUTION")
    print("==================")
    print(f"Stack size (S):           {game.stack_size:.2f}")
    print(f"Jam threshold (Y):        {solution['jam_threshold']:.4f}")
    print(f"Call threshold (X):       {solution['call_threshold']:.4f}")
    print(f"Jam frequency:            {solution['jam_frequency']:.4f}")
    print(f"Call frequency:           {solution['call_frequency']:.4f}")
    print(f"Attacker EV (chips):      {solution['attacker_value']:.4f}")
    print(f"Defender EV (chips):      {solution['defender_value']:.4f}")
    print()
    return solution


def maybe_plot(result: dict, output_path: Optional[str]) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:  # pragma: no cover
        print("matplotlib is not installed; skipping plot.")
        return

    strategies = result["info_set_strategies"]
    regrets = result.get("info_set_regrets", {})
    iterations = float(result.get("iterations", 0) or 0)

    jam_keys = sorted((k for k in strategies if k.startswith("Y:")), key=_bucket_index)
    call_keys = sorted((k for k in strategies if k.startswith("X:")), key=_bucket_index)

    jam_probs = [strategies[key].get("jam", 0.0) for key in jam_keys]
    call_probs = [strategies[key].get("call", 0.0) for key in call_keys]

    normalized_regrets = {
        key: normalize_regret_values(reg, normalization=iterations)
        for key, reg in regrets.items()
    }

    fig, (ax_jam, ax_call) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax_jam.bar(range(len(jam_keys)), jam_probs, color="#4C72B0")
    ax_jam.set_ylabel("Jam probability")
    ax_jam.set_title("Player Y average jam probability per bucket")
    ax_jam.set_ylim(0.0, 1.0)

    if normalized_regrets:
        jam_regrets = [normalized_regrets.get(key, {}).get("jam", 0.0) for key in jam_keys]
        ax_jam_twin = ax_jam.twinx()
        ax_jam_twin.plot(
            range(len(jam_keys)),
            jam_regrets,
            color="#DD8452",
            label="Regret per iteration (jam)",
        )
        ax_jam_twin.set_ylabel("Regret per iteration")
        ax_jam_twin.legend(loc="upper right")

    ax_call.bar(range(len(call_keys)), call_probs, color="#55A868")
    ax_call.set_xlabel("Bucket index")
    ax_call.set_ylabel("Call probability")
    ax_call.set_title("Player X average call probability per bucket")
    ax_call.set_ylim(0.0, 1.0)

    if normalized_regrets:
        call_regrets = [normalized_regrets.get(key, {}).get("call", 0.0) for key in call_keys]
        ax_call_twin = ax_call.twinx()
        ax_call_twin.plot(
            range(len(call_keys)),
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
    if not non_interactive:
        plt.show()
    plt.close(fig)


def _bucket_index(key: str) -> int:
    return int(key.split("[")[1][:-1])


def main() -> None:
    args = parse_args()

    game = JamOrFoldGame1(stack_size=args.stack, num_buckets=args.buckets)

    print("[0,1] JAM-OR-FOLD GAME #1")
    print("==========================")
    print(f"Stack size (S): {game.stack_size}")
    print(f"Big blind:      {game.big_blind}")
    print(f"Small blind:    {game.small_blind}")
    print(f"Buckets:        {game.num_buckets}")
    print(f"Iterations:     {args.iterations}")
    print()

    analytic = print_analytic_summary(game)

    if args.samples > 0:
        estimate = simulate_expected_value_jam_or_fold_game1(
            game, samples=args.samples, seed=args.seed
        )
        print("MONTE CARLO CHECK")
        print("==================")
        print(f"Estimated EV (attacker): {estimate:.4f}")
        print(f"Analytic EV (attacker):  {analytic['attacker_value']:.4f}")
        print(f"Absolute error:          {abs(estimate - analytic['attacker_value']):.4f}")
        print()

    result = game.solve_mccfr_equilibrium(iterations=args.iterations, seed=args.seed)

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

    strategies = result.get("info_set_strategies", {})
    jam_entries: list[tuple[int, float]] = []
    call_entries: list[tuple[int, float]] = []
    for key, strategy in strategies.items():
        if key.startswith("Y:"):
            jam_entries.append((_bucket_index(key), strategy.get("jam", 0.0)))
        elif key.startswith("X:"):
            call_entries.append((_bucket_index(key), strategy.get("call", 0.0)))

    num_buckets = game.num_buckets
    bucket_half = 0.5 / num_buckets

    def _midpoint(index: int) -> float:
        return (index + 0.5) / num_buckets

    def _avg(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    jam_threshold = analytic["jam_threshold"]
    jam_value_region = [prob for idx, prob in jam_entries if _midpoint(idx) <= jam_threshold + bucket_half]
    jam_fold_region = [prob for idx, prob in jam_entries if _midpoint(idx) > jam_threshold + bucket_half]

    call_threshold = analytic["call_threshold"]
    call_value_region = [prob for idx, prob in call_entries if _midpoint(idx) <= call_threshold + bucket_half]
    call_fold_region = [prob for idx, prob in call_entries if _midpoint(idx) > call_threshold + bucket_half]

    avg_jam_value = _avg(jam_value_region)
    avg_jam_above = _avg(jam_fold_region)
    avg_call_value = _avg(call_value_region)
    avg_call_above = _avg(call_fold_region)

    print("Jam/call takeaway:")
    if avg_jam_above <= 0.05:
        print(
            "  Y jams value hands aggressively and all but shuts down once past the"
            " analytic threshold—no light jams needed."
        )
    else:
        print(
            "  Y still sprinkles in jams above the threshold; expect some light"
            " pressure in the fold region."
        )
    if avg_call_above <= 0.05:
        print(
            "  X responds by calling tightly past the defense line, folding almost"
            " everything that should decline the jam."
        )
    else:
        print(
            "  X continues with a wider defence above the analytic call point—"
            "consider more iterations or buckets if you expect a sharper cutoff."
        )
    print(f"  Avg jam prob. ≤ jam threshold:  {avg_jam_value:.3f}")
    print(f"  Avg jam prob. > jam threshold:   {avg_jam_above:.3f}")
    print(f"  Avg call prob. ≤ call threshold: {avg_call_value:.3f}")
    print(f"  Avg call prob. > call threshold:  {avg_call_above:.3f}")
    print()

    if args.plot or args.plot_file:
        maybe_plot(result, args.plot_file)

    print("Done.")


if __name__ == "__main__":
    main()
