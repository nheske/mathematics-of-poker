"""Jam-or-fold No-Limit Hold'em utilities for Chapter 12 Example 12.3.

This module provides Monte Carlo tooling for simulating the heads-up
jam-or-fold scenario described in *The Mathematics of Poker*, Chapter 12.
It relies on the bundled ``phevaluator`` hand evaluator to produce
preflop equity estimates using full board runouts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Sequence, Tuple

import numpy as np

from ...phevaluator import Card, evaluate_cards

DeckCard = int
HoleCards = Tuple[DeckCard, DeckCard]
Board = Tuple[DeckCard, DeckCard, DeckCard, DeckCard, DeckCard]
Strategy = Callable[[HoleCards], bool]


def _remove_cards(deck: Sequence[DeckCard], cards: Iterable[DeckCard]) -> list[DeckCard]:
    """Return a deck with the given cards removed."""

    exclude = set(cards)
    return [card for card in deck if card not in exclude]


def _deal_board(rng: np.random.Generator, deck: Sequence[DeckCard]) -> Board:
    """Draw five unique community cards from ``deck``."""

    board = rng.choice(deck, size=5, replace=False)
    return tuple(int(card) for card in board)  # type: ignore[return-value]


def _hand_to_string(hand: HoleCards) -> Tuple[str, str]:
    """Return human-readable labels for a pair of hole cards."""

    return tuple(Card(card).describe_card() for card in hand)


@dataclass
class EquityEstimate:
    """Stores Monte Carlo estimates for a heads-up preflop matchup."""

    attacker_hand: Tuple[str, str]
    defender_hand: Tuple[str, str]
    win: float
    lose: float
    tie: float
    samples: int

    @property
    def equity(self) -> float:
        """Return the attacker's showdown equity (win + tie / 2)."""

        return self.win + 0.5 * self.tie


def estimate_preflop_equity(
    attacker: HoleCards,
    defender: HoleCards,
    *,
    samples: int = 50_000,
    seed: Optional[int] = None,
) -> EquityEstimate:
    """Estimate heads-up preflop equity using Monte Carlo rollouts."""

    if samples <= 0:
        raise ValueError("samples must be positive")

    rng = np.random.default_rng(seed)
    base_deck = list(range(52))
    deck_without_hands = _remove_cards(base_deck, (*attacker, *defender))

    wins = 0
    ties = 0

    deck_array = np.array(deck_without_hands, dtype=np.int64)

    for _ in range(samples):
        board = _deal_board(rng, deck_array)
        attacker_score = evaluate_cards(*attacker, *board)
        defender_score = evaluate_cards(*defender, *board)

        if attacker_score < defender_score:
            wins += 1
        elif attacker_score == defender_score:
            ties += 1

    losses = samples - wins - ties

    return EquityEstimate(
        attacker_hand=_hand_to_string(attacker),
        defender_hand=_hand_to_string(defender),
        win=wins / samples,
        lose=losses / samples,
        tie=ties / samples,
        samples=samples,
    )


def random_hole_cards(rng: Optional[np.random.Generator] = None) -> HoleCards:
    """Sample two distinct cards uniformly from the deck."""

    local_rng = np.random.default_rng() if rng is None else rng
    sample = local_rng.choice(52, size=2, replace=False)
    return tuple(int(card) for card in sample)  # type: ignore[return-value]


def deal_random_matchup(
    rng: Optional[np.random.Generator] = None,
) -> Tuple[HoleCards, HoleCards, Board]:
    """Sample a full heads-up matchup (two hands plus board)."""

    local_rng = np.random.default_rng() if rng is None else rng
    cards = local_rng.choice(52, size=9, replace=False)
    attacker = tuple(int(card) for card in cards[:2])  # type: ignore[return-value]
    defender = tuple(int(card) for card in cards[2:4])  # type: ignore[return-value]
    board = tuple(int(card) for card in cards[4:9])  # type: ignore[return-value]
    return attacker, defender, board


def showdown_winner(
    attacker: HoleCards,
    defender: HoleCards,
    board: Board,
) -> int:
    """Return showdown result: 1 if attacker wins, -1 if loses, 0 if tie."""

    attacker_score = evaluate_cards(*attacker, *board)
    defender_score = evaluate_cards(*defender, *board)
    if attacker_score < defender_score:
        return 1
    if attacker_score > defender_score:
        return -1
    return 0


@dataclass
class HoldemJamOrFoldResult:
    """Aggregate statistics for the jam-or-fold hold'em simulation."""

    samples: int
    stack_size: float
    small_blind: float
    big_blind: float
    attacker_ev: float
    defender_ev: float
    jam_rate: float
    call_rate: float
    call_given_jam_rate: float
    showdown_win_rate: float
    showdown_loss_rate: float
    showdown_tie_rate: float


def always_jam(_: HoleCards) -> bool:
    """Strategy helper that jams every hand."""

    return True


def always_call(_: HoleCards) -> bool:
    """Strategy helper that calls every jam."""

    return True


def simulate_holdem_jam_or_fold(
    *,
    samples: int = 50_000,
    stack_size: float = 5.0,
    small_blind: float = 0.5,
    big_blind: float = 1.0,
    attacker_strategy: Strategy = always_jam,
    defender_strategy: Strategy = always_call,
    seed: Optional[int] = None,
) -> HoldemJamOrFoldResult:
    """Simulate the jam-or-fold hold'em game with configurable strategies."""

    if samples <= 0:
        raise ValueError("samples must be positive")
    if stack_size <= 0:
        raise ValueError("stack_size must be positive")
    if small_blind <= 0 or big_blind <= 0:
        raise ValueError("blind sizes must be positive")

    rng = np.random.default_rng(seed)
    base_deck = list(range(52))

    attacker_ev = 0.0
    defender_ev = 0.0
    jam_count = 0
    call_count = 0
    showdown_wins = 0
    showdown_losses = 0
    showdown_ties = 0

    for _ in range(samples):
        cards = rng.choice(base_deck, size=4, replace=False)
        attacker_hand: HoleCards = (int(cards[0]), int(cards[1]))
        defender_hand: HoleCards = (int(cards[2]), int(cards[3]))

        if not attacker_strategy(attacker_hand):
            attacker_ev -= small_blind
            defender_ev += small_blind
            continue

        jam_count += 1

        if not defender_strategy(defender_hand):
            attacker_ev += big_blind
            defender_ev -= big_blind
            continue

        call_count += 1

        remaining_deck = _remove_cards(base_deck, (*attacker_hand, *defender_hand))
        board = _deal_board(rng, np.array(remaining_deck, dtype=np.int64))
        result = showdown_winner(attacker_hand, defender_hand, board)

        if result > 0:
            attacker_ev += stack_size
            defender_ev -= stack_size
            showdown_wins += 1
        elif result < 0:
            attacker_ev -= stack_size
            defender_ev += stack_size
            showdown_losses += 1
        else:
            showdown_ties += 1

    jam_rate = jam_count / samples
    call_rate = call_count / samples
    call_given_jam_rate = call_count / jam_count if jam_count else 0.0

    if call_count:
        showdown_win_rate = showdown_wins / call_count
        showdown_loss_rate = showdown_losses / call_count
        showdown_tie_rate = showdown_ties / call_count
    else:
        showdown_win_rate = showdown_loss_rate = showdown_tie_rate = 0.0

    defender_ev = -attacker_ev

    return HoldemJamOrFoldResult(
        samples=samples,
        stack_size=stack_size,
        small_blind=small_blind,
        big_blind=big_blind,
        attacker_ev=attacker_ev,
        defender_ev=defender_ev,
        jam_rate=jam_rate,
        call_rate=call_rate,
        call_given_jam_rate=call_given_jam_rate,
        showdown_win_rate=showdown_win_rate,
        showdown_loss_rate=showdown_loss_rate,
        showdown_tie_rate=showdown_tie_rate,
    )
