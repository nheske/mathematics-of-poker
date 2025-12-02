"""Backward-compatibility module for :mod:`mathematics_of_poker.games.half_street`.

The ``HalfStreetGame`` base class now lives in
``mathematics_of_poker.games.ch11.half_street``. Importing this module raises an
explicit error to encourage updating legacy imports.
"""

raise ImportError(
	"HalfStreetGame has moved to mathematics_of_poker.games.ch11.half_street; "
	"please update your imports."
)