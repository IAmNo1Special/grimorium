"""Spell Registry - A central registry for all magical spells."""

from typing import Callable, Dict

class SpellRegistry:
    """A singleton class to manage the registration of spells."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpellRegistry, cls).__new__(cls)
            cls._instance._spell_registry: Dict[str, Callable] = {}
        return cls._instance

    def register_spell(self, func: Callable) -> Callable:
        """
        A decorator to register a function as a spell in the Grimorium.

        The decorated function will be added to the spell registry,
        making it discoverable by the SpellSync system.

        Args:
            func (Callable): The function to register as a spell.

        Returns:
            Callable: The original function, unmodified.
        """
        spell_name = func.__name__
        if spell_name in self._spell_registry:
            print(f"Warning: Spell '{spell_name}' is already registered. Overwriting.")
        
        self._spell_registry[spell_name] = func
        print(f"Registered spell: {spell_name}")
        return func

    def get_spell(self, spell_name: str) -> Callable:
        """
        Retrieves a spell from the registry by its name.

        Args:
            spell_name (str): The name of the spell to retrieve.

        Returns:
            Callable: The spell function.
        
        Raises:
            KeyError: If the spell is not found in the registry.
        """
        return self._spell_registry[spell_name]

    def get_all_spells(self) -> Dict[str, Callable]:
        """Returns a dictionary of all registered spells."""
        return self._spell_registry.copy()

# Create a singleton instance of the SpellRegistry
spell_registry = SpellRegistry()

# Make the register_spell method directly available as a decorator
register_spell = spell_registry.register_spell
