#!/usr/bin/env python3
"""
Example script demonstrating the Clairvoyance Game solver.

This script solves Example 11.1 from The Mathematics of Poker and shows
the optimal mixed strategies for both players.

You can choose between the analytic closed-form solver and an approximate
regret-matching (CFR) solver via command-line flags.
"""

import sys
import os
import argparse
from typing import Any, Dict, Optional

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathematics_of_poker.games.ch11.clairvoyance import ClairvoyanceGame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clairvoyance Game example")
    parser.add_argument(
    "--solver",
    choices=["analytic", "cfr", "mccfr"],
    default="analytic",
    help="Which solver to run (default: analytic closed-form)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=20000,
        help="Number of iterations for CFR solver (default: 20000)",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Display matplotlib charts for MCCFR diagnostics (requires matplotlib)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed for CFR solver",
    )
    parser.add_argument(
        "--pot",
        type=float,
        default=1.0,
        help="Initial pot size (default: 1.0)",
    )
    parser.add_argument(
        "--bet",
        type=float,
        default=1.0,
        help="Bet size for player Y (default: 1.0)",
    )
    parser.add_argument(
        "--plot-file",
        type=str,
        default=None,
        help="Optional path to save the MCCFR visualization as an image",
    )
    return parser.parse_args()


def print_header():
    """Print introductory header."""
    
    print("THE MATHEMATICS OF POKER - EXAMPLE 11.1")
    print("The Clairvoyance Game")
    print("=" * 60)
    print()


def display_setup(game: ClairvoyanceGame) -> None:
    """Show game setup information and payoff matrices."""

    print("Game Setup:")
    print(f"- Initial pot size: {game.pot_size}")
    print(f"- Bet size: {game.bet_size}")
    print("- Y is clairvoyant (knows both hands)")
    print("- Y's hand beats X's hand 50% of the time")
    print("- X checks in the dark")
    print("- Y can check or bet")
    print("- If Y bets, X can call or fold")
    print()
    
    payoff_x, payoff_y = game.get_payoff_matrix()
    x_labels, y_labels = game.get_strategy_labels()
    
    print("Payoff Matrix for Player X:")
    print("Strategies:", x_labels)
    print("Y Strategies:", y_labels)
    print(payoff_x)
    print()
    
    print("Payoff Matrix for Player Y:")
    print(payoff_y)
    print()


def run_analytic(game: ClairvoyanceGame) -> None:
    """Run the analytic solver and display results."""

    print("Solving for Nash Equilibrium (analytic)...")
    solution = game.solve_nash_equilibrium()

    print(game.analyze_strategies(solution))
    print()

    print(game.get_mixed_strategy_interpretation(solution))
    print()

    is_equilibrium = game.verify_equilibrium(solution)
    print(f"Equilibrium verification: {'PASSED' if is_equilibrium else 'FAILED'}")
    print()

    print("Closed-form highlights:")
    print(f"- Call probability: {solution['call_probability']:.6f}")
    print(f"- Bluff fraction: {solution['bluff_fraction']:.6f}")
    print(f"- Game value (X): {solution['game_value']:.6f}")
    print()


def run_cfr(game: ClairvoyanceGame, iterations: int, seed: Optional[int]) -> None:
    """Run the CFR solver and display results."""

    print("Solving for Nash Equilibrium (CFR)...")
    print(f"Iterations: {iterations}")
    if seed is not None:
        print(f"Seed: {seed}")

    solution = game.solve_cfr_equilibrium(iterations=iterations, seed=seed)

    print(game.analyze_strategies(solution))
    print()

    print(game.get_mixed_strategy_interpretation(solution))
    print()

    call_prob = solution.get('call_probability', solution['x_strategy'][1])
    bluff_fraction = solution.get('bluff_fraction', solution['y_strategy'][2] + solution['y_strategy'][3])
    print("CFR highlights:")
    print(f"- Average call probability: {call_prob:.6f}")
    print(f"- Average bluff fraction: {bluff_fraction:.6f}")
    print(f"- Average game value (X): {solution['game_value']:.6f}")
    print()

    # Verification with a relaxed tolerance (CFR is approximate)
    is_equilibrium = game.verify_equilibrium(solution, tolerance=1e-2)
    print(f"Approximate equilibrium verification: {'PASSED' if is_equilibrium else 'FAILED'}")
    print()


def run_mccfr(
    game: ClairvoyanceGame,
    iterations: int,
    seed: Optional[int],
    plot: bool = False,
    plot_file: Optional[str] = None,
) -> None:
    """Run the Monte Carlo CFR solver and display results."""

    print("Solving for Nash Equilibrium (Monte Carlo CFR)...")
    print(f"Iterations: {iterations}")
    if seed is not None:
        print(f"Seed: {seed}")

    solution = game.solve_mccfr_equilibrium(iterations=iterations, seed=seed)

    print(game.analyze_strategies(solution))
    print()

    print(game.get_mixed_strategy_interpretation(solution))
    print()

    call_prob = solution["call_probability"]
    bluff_fraction = solution["bluff_fraction"]
    value_fraction = solution["value_bet_fraction"]
    print("Monte Carlo CFR highlights:")
    print(f"- Average call probability: {call_prob:.6f}")
    print(f"- Average value-bet frequency: {value_fraction:.6f}")
    print(f"- Average bluff fraction: {bluff_fraction:.6f}")
    print(f"- Estimated game value (X): {solution['game_value']:.6f}")
    print()

    print("Info-set strategies:")
    for key, strat in solution["info_set_strategies"].items():
        formatted = ", ".join(f"{action}={prob:.4f}" for action, prob in strat.items())
        print(f"  {key}: {formatted}")
    print()

    print("Cumulative regrets:")
    for key, regrets in solution["info_set_regrets"].items():
        formatted = ", ".join(f"{action}={value:.4f}" for action, value in regrets.items())
        print(f"  {key}: {formatted}")
    print()

    print(
        f"Approximate equilibrium verification: {'PASSED' if solution['is_equilibrium'] else 'FAILED'}"
    )
    print()

    if plot or plot_file:
        visualize_mccfr(solution, output_path=plot_file)


def visualize_mccfr(solution: Dict[str, Any], output_path: Optional[str] = None) -> None:
    """Render bar charts for MCCFR info-set strategies and regrets."""

    try:
        import matplotlib.pyplot as plt
    except ImportError:  # pragma: no cover - optional dependency
        print("matplotlib is required for plotting; install it with `pip install matplotlib`.")
        return

    info_set_strategies = solution["info_set_strategies"]
    info_set_regrets = solution["info_set_regrets"]
    keys = list(info_set_strategies.keys())
    if not keys:
        print("No information sets available to visualize.")
        return

    rows = len(keys)
    fig, axes = plt.subplots(rows, 2, figsize=(11, 3.2 * rows))
    row_axes = [axes] if rows == 1 else axes

    for idx, key in enumerate(keys):
        strategy_axes, regret_axes = row_axes[idx]

        actions = list(info_set_strategies[key].keys())
        positions = list(range(len(actions)))
        probabilities = [info_set_strategies[key][action] for action in actions]
        regrets = [info_set_regrets[key][action] for action in actions]

        strategy_axes.bar(positions, probabilities, color="#4C72B0", tick_label=actions)
        strategy_axes.set_ylim(0.0, 1.0)
        strategy_axes.set_ylabel("Probability")
        strategy_axes.set_title(f"{key}: average strategy")
        strategy_axes.grid(axis="y", alpha=0.3, linestyle="--")

        regret_axes.bar(positions, regrets, color="#DD8452", tick_label=actions)
        regret_axes.axhline(0.0, color="black", linewidth=0.8)
        regret_axes.set_ylabel("Cumulative regret")
        regret_axes.set_title(f"{key}: cumulative regret")
        regret_axes.grid(axis="y", alpha=0.3, linestyle="--")

        for ax in (strategy_axes, regret_axes):
            ax.set_xlabel("Action")

    fig.suptitle("MCCFR info-set diagnostics", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    if output_path:
        fig.savefig(output_path, bbox_inches="tight")
        print(f"Saved MCCFR diagnostics to {output_path}")

    backend = ""
    try:
        import matplotlib

        backend = matplotlib.get_backend().lower()
    except Exception:
        backend = ""

    non_interactive = any(
        keyword in backend for keyword in ("agg", "pdf", "svg", "ps", "cairo")
    )

    if non_interactive and not output_path:
        print(
            "Matplotlib backend is non-interactive; rerun with --plot-file to save the chart."
        )

    if not non_interactive:
        plt.show()

    plt.close(fig)


def main():
    """Demonstrate the Clairvoyance Game solver."""

    args = parse_args()

    print_header()

    game = ClairvoyanceGame(pot_size=args.pot, bet_size=args.bet)

    display_setup(game)

    if args.solver == "analytic":
        run_analytic(game)
    elif args.solver == "cfr":
        run_cfr(game, iterations=args.iterations, seed=args.seed)
    else:
        run_mccfr(
            game,
            iterations=args.iterations,
            seed=args.seed,
            plot=args.plot,
            plot_file=args.plot_file,
        )

    # Show some game theory insights
    print("GAME THEORY INSIGHTS")
    print("=" * 30)
    print("This game demonstrates several key concepts:")
    print("1. The value of information - Y's clairvoyance gives them an advantage")
    print("2. Mixed strategies arise naturally in adversarial settings")
    print("3. Bluffing frequency must be balanced with value betting")
    print("4. Calling frequency must balance between being exploited by bluffs vs value bets")
    print()
    
    # Test different pot and bet sizes
    print("SENSITIVITY ANALYSIS")
    print("=" * 25)
    print("How do optimal strategies change with different bet sizes?")
    print()
    
    for bet_size in [0.5, 1.0, 2.0]:
        print(f"Bet size: {bet_size}")
        test_game = ClairvoyanceGame(pot_size=1.0, bet_size=bet_size)
        if args.solver == "analytic":
            test_solution = test_game.solve_nash_equilibrium()
        elif args.solver == "cfr":
            test_solution = test_game.solve_cfr_equilibrium(
                iterations=args.iterations, seed=args.seed
            )
        else:
            test_solution = test_game.solve_mccfr_equilibrium(
                iterations=args.iterations, seed=args.seed
            )
        
        call_freq = test_solution['x_strategy'][1]
        y_strategy = test_solution['y_strategy']
        p_nuts = y_strategy[1] + y_strategy[3]    # Bet with nuts
        p_bluff = y_strategy[2] + y_strategy[3]   # Bet with bluffs
        
        print(f"  X calling frequency: {call_freq:.3f}")
        print(f"  Y value betting frequency: {p_nuts:.3f}")
        print(f"  Y bluffing frequency: {p_bluff:.3f}")
        print(f"  Game value: {test_solution['game_value']:.4f}")
        print()


if __name__ == "__main__":
    main()