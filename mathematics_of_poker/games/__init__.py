"""
Poker game implementations.

This module contains implementations of various simplified poker games
including half-street games and their optimal solutions.
"""

from .ch10 import (
    OddsAndEvensGame,
    RoshamboGame,
    RoshamboSGame,
    RoshamboFGame,
    CopsAndRobbersGame,
)
from .ch11.half_street import HalfStreetGame
from .ch11 import (
    ClairvoyanceGame,
    ZeroOneGame1,
    ZeroOneGame2,
    simulate_expected_value_game1,
    simulate_expected_value_game2 as _simulate_expected_value_zero_one_game2,
)
from .ch12 import (
    JamOrFoldGame1,
    JamOrFoldGame2,
    simulate_expected_value_jam_or_fold_game1,
    simulate_expected_value_game2 as simulate_expected_value_jam_or_fold_game2,
)

simulate_expected_value_game2 = _simulate_expected_value_zero_one_game2

__all__ = [
    'OddsAndEvensGame',
    'RoshamboGame',
    'RoshamboSGame',
    'RoshamboFGame',
    'CopsAndRobbersGame',
    'HalfStreetGame',
    'ClairvoyanceGame',
    'ZeroOneGame1',
    'ZeroOneGame2',
    'simulate_expected_value_game1',
    'simulate_expected_value_game2',
    'JamOrFoldGame1',
    'JamOrFoldGame2',
    'simulate_expected_value_jam_or_fold_game1',
    'simulate_expected_value_jam_or_fold_game2',
]
