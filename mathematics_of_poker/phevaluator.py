"""Compatibility shim for the vendored ``phevaluator`` package.

This module re-exports the top-level symbols so legacy imports from
``mathematics_of_poker.phevaluator`` continue to function now that the
hand evaluator lives in ``/phevaluator`` within the repository.
"""

from phevaluator import *  # noqa: F401,F403
