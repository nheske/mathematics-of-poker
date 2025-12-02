"""CLI driver for Example 11.3 ([0, 1] Game #2 with fold option)."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

# Ensure package imports work when running from a cloned repository
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch11.zero_one_game_2 import (  # noqa: E402
    ZeroOneGame2,
    simulate_expected_value,
)
from mathematics_of_poker.utils.plotting import normalize_regret_values  # noqa: E402


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
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Display matplotlib charts for betting/calling strategies (requires GUI backend)",
    )
    parser.add_argument(
        "--plot-file",
        type=str,
        default=None,
        help="Optional path to save MCCFR diagnostics figure",
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

    strategies: dict[str, dict[str, float]] = result.get("info_set_strategies", {})
    y_buckets: list[tuple[float, float]] = []
    for key, strategy in strategies.items():
        if not key.startswith("Y:"):
            continue
        try:
            bucket_idx = _bucket_index(key)
        except ValueError:  # pragma: no cover - defensive guard
            continue
        midpoint = game._bucket_value(bucket_idx)
        y_buckets.append((midpoint, strategy.get("bet", 0.0)))

    bucket_half = 0.5 / game.num_buckets
    value_cutoff = analytic["value_threshold"] + bucket_half
    bluff_cutoff = analytic["bluff_threshold"] - bucket_half

    value_region = [prob for midpoint, prob in y_buckets if midpoint <= value_cutoff]
    mid_region = [prob for midpoint, prob in y_buckets if value_cutoff < midpoint < bluff_cutoff]
    bluff_region = [prob for midpoint, prob in y_buckets if midpoint >= bluff_cutoff]

    def _avg(probs: list[float]) -> float:
        return sum(probs) / len(probs) if probs else 0.0

    avg_value = _avg(value_region)
    avg_mid = _avg(mid_region)
    avg_bluff = _avg(bluff_region)
    max_bluff = max(bluff_region) if bluff_region else 0.0

    print("\n  Bluffing takeaway:")
    if max_bluff <= 0.05:
        print(
            "    MCCFR ends up pure-valuing hands—bet frequency collapses above the bluff"
            " threshold, so folding pressure never materialises."
        )
    else:
        print(
            "    MCCFR preserves a live bluff band above the threshold; Y still fires"
            " selectively to balance X's calling region."
        )
    print(f"    Avg bet prob. (value buckets): {avg_value:.3f}")
    if mid_region:
        print(f"    Avg bet prob. (check buckets): {avg_mid:.3f}")
    print(f"    Avg bet prob. (bluff buckets): {avg_bluff:.3f}")

    if args.plot or args.plot_file:
        maybe_plot(result, args.plot_file)

    return 0


def _bucket_index(key: str) -> int:
    return int(key.split("[")[1][:-1])


def maybe_plot(result: dict, output_path: Optional[str]) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:  # pragma: no cover
        print("matplotlib is not installed; skipping plot.")
        return

    strategies: dict[str, dict[str, float]] = result.get("info_set_strategies", {})
    regrets: dict[str, dict[str, float]] = result.get("info_set_regrets", {})
    normalization = float(result.get("iterations", 0) or 0)
    normalized_regrets = {
        key: normalize_regret_values(value, normalization=normalization)
        for key, value in regrets.items()
    }

    y_keys = sorted((k for k in strategies if k.startswith("Y:")), key=_bucket_index)
    x_keys = sorted((k for k in strategies if k.startswith("X:")), key=_bucket_index)

    if not y_keys or not x_keys:
        print("No strategy data available for plotting.")
        return

    y_bet_probs = [strategies[key].get("bet", 0.0) for key in y_keys]
    x_call_probs = [strategies[key].get("call", 0.0) for key in x_keys]

    fig, (ax_y, ax_x) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax_y.bar(range(len(y_keys)), y_bet_probs, color="#4C72B0")
    ax_y.set_ylabel("Bet probability")
    ax_y.set_title("Player Y average bet probability per bucket")
    ax_y.set_ylim(0.0, 1.0)

    if normalized_regrets:
        y_regrets = [normalized_regrets.get(key, {}).get("bet", 0.0) for key in y_keys]
        ax_y_twin = ax_y.twinx()
        ax_y_twin.plot(
            range(len(y_keys)),
            y_regrets,
            color="#DD8452",
            label="Normalised regret (bet)",
        )
        ax_y_twin.set_ylabel("Regret per iteration")
        ax_y_twin.legend(loc="upper right")

    ax_x.bar(range(len(x_keys)), x_call_probs, color="#55A868")
    ax_x.set_xlabel("Bucket index")
    ax_x.set_ylabel("Call probability")
    ax_x.set_title("Player X average call probability per bucket")
    ax_x.set_ylim(0.0, 1.0)

    if normalized_regrets:
        x_regrets = [normalized_regrets.get(key, {}).get("call", 0.0) for key in x_keys]
        ax_x_twin = ax_x.twinx()
        ax_x_twin.plot(
            range(len(x_keys)),
            x_regrets,
            color="#C44E52",
            label="Normalised regret (call)",
        )
        ax_x_twin.set_ylabel("Regret per iteration")
        ax_x_twin.legend(loc="upper right")

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, bbox_inches="tight")
        print(f"Saved plot to {output_path}")

    backend = plt.get_backend().lower()
    non_interactive = any(tag in backend for tag in ("agg", "pdf", "svg", "ps", "cairo"))
    if not non_interactive:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
