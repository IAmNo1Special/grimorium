"""Spell Registry - A central registry for all magical spells.

Refactored to be a passive decorator system. No longer a singleton registry.
"""

import logging
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Callable)


def register_spell(func: T) -> T:
    """
    A passive decorator to mark a function as a spell in the Grimorium.

    The decorated function will be tagged with `_grimorium_spell = True`,
    allowing the SpellSync system to discover it during scanning.

    Args:
        func (Callable): The function to register as a spell.

    Returns:
        Callable: The original function, tagged.
    """
    func._grimorium_spell = True
    # Forward compatibility for configuration if needed later
    if not hasattr(func, "_grimorium_config"):
        func._grimorium_config = {}

    return func


class SpellRegistry:
    """
    Deprecated: This class is kept for backward compatibility but should not be used.
    Spells are now managed by SpellSync instances.
    """

    def get_spell(self, name):
        raise NotImplementedError(
            "Global SpellRegistry is deprecated. Use Grimorium instance."
        )

    def get_all_spells(self):
        raise NotImplementedError(
            "Global SpellRegistry is deprecated. Use Grimorium instance."
        )
