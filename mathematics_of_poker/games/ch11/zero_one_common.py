"""Shared utilities for Chapter 11 [0, 1] half-street games."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..game_tree import GameTree


@dataclass
class ZeroOneBucketGame:
    """Base class providing validation and helpers for [0, 1] bucketed games."""

    pot_size: float = 1.0
    bet_size: float = 1.0
    num_buckets: int = 40
    _tree_cache: Optional["GameTree"] = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        if self.pot_size < 0:
            raise ValueError("pot_size must be non-negative")
        if self.bet_size <= 0:
            raise ValueError("bet_size must be positive")
        if self.num_buckets < 2:
            raise ValueError("num_buckets must be at least 2")

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
    def _showdown_payoff(self, x_value: float, y_value: float) -> float:
        if x_value < y_value:
            return self.pot_size
        if y_value < x_value:
            return -self.pot_size
        return 0.0

    def _call_payoff(self, x_value: float, y_value: float) -> float:
        swing = self.pot_size + self.bet_size
        if x_value < y_value:
            return swing
        if y_value < x_value:
            return -swing
        return 0.0
