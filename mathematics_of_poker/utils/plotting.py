"""Plotting utilities shared across examples."""

from __future__ import annotations

from typing import Dict, Mapping


def normalize_regret_values(
    regrets: Mapping[str, float], *, normalization: float | None
) -> Dict[str, float]:
    """Return a new dict with regrets scaled by *normalization*.

    Parameters
    ----------
    regrets:
        Mapping from action name to cumulative regret value.
    normalization:
        Positive scalar used to rescale the regrets. If ``None`` or ``<= 0``, the
        original values are returned unchanged.
    """

    if normalization is None or normalization <= 0:
        return {action: float(value) for action, value in regrets.items()}
    scale = 1.0 / normalization
    return {action: float(value) * scale for action, value in regrets.items()}
