"""Shared utilities for Chapter 12 jam-or-fold games."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

from ..game_tree import GameTree, GameTreeNode, InformationSet, Player


@dataclass
class JamOrFoldBucketGame:
    """Base class providing bucket helpers and payoffs for jam-or-fold games."""

    stack_size: float = 10.0
    big_blind: float = 1.0
    small_blind: float = 0.5
    num_buckets: int = 40
    _tree_cache: Optional[GameTree] = field(init=False, default=None, repr=False)
    _payoff_scale: float = field(init=False, default=1.0, repr=False)

    def __post_init__(self) -> None:
        if self.stack_size <= 0:
            raise ValueError("stack_size must be positive")
        if self.big_blind <= 0:
            raise ValueError("big_blind must be positive")
        if self.small_blind <= 0:
            raise ValueError("small_blind must be positive")
        if self.stack_size < self.big_blind:
            raise ValueError("stack_size must be at least as large as the big blind")
        if self.num_buckets < 2:
            raise ValueError("num_buckets must be at least 2")
        self._payoff_scale = 1.0 / self.stack_size

    # ------------------------------------------------------------------
    # Bucket helpers
    # ------------------------------------------------------------------
    def _bucket_probability(self) -> float:
        return 1.0 / self.num_buckets

    def _bucket_value(self, index: int) -> float:
        return (index + 0.5) / self.num_buckets

    def _player_bucket_key(self, prefix: str, index: int) -> str:
        return f"{prefix}:bucket[{index}]"

    def _reset_cache(self) -> None:
        self._tree_cache = None

    # ------------------------------------------------------------------
    # Payoff helpers
    # ------------------------------------------------------------------
    def _attacker_fold_payoff(self) -> Tuple[float, float]:
        """Payoffs when the attacker folds immediately."""
        attacker_loss = self.small_blind * self._payoff_scale
        return (attacker_loss, -attacker_loss)

    def _defender_fold_payoff(self) -> Tuple[float, float]:
        """Payoffs when the defender folds facing a jam."""
        defender_loss = self.big_blind * self._payoff_scale
        return (-defender_loss, defender_loss)

    def _showdown_payoffs(self, attacker_value: float, defender_value: float) -> Tuple[float, float]:
        """Return showdown payoffs for the given bucket midpoint values."""

        if attacker_value < defender_value:
            payoff = self.stack_size * self._payoff_scale
            return (-payoff, payoff)
        if defender_value < attacker_value:
            payoff = self.stack_size * self._payoff_scale
            return (payoff, -payoff)
        return (0.0, 0.0)
