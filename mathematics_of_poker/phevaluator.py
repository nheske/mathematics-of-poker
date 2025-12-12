"""Compatibility shim for the external ``phevaluator`` package.

This module re-exports the top-level symbols so legacy imports from
``mathematics_of_poker.phevaluator`` continue to function after the
package was moved out of the project namespace.
"""

from phevaluator import *  # noqa: F401,F403
