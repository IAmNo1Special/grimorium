"""Unit tests for spell_registry module."""

import pytest

from magetools.spell_registry import SpellRegistry, register_spell


class TestRegisterSpellDecorator:
    """Tests for the @spell decorator."""

    def test_decorator_returns_original_function(self):
        """Decorator should return the original function."""

        def my_func():
            return "hello"

        decorated = register_spell(my_func)

        assert decorated is my_func
        assert decorated() == "hello"

    def test_decorator_adds_grimorium_spell_attribute(self):
        """Decorator should add _grimorium_spell=True attribute."""

        @register_spell
        def my_spell():
            pass

        assert hasattr(my_spell, "_grimorium_spell")
        assert my_spell._grimorium_spell is True

    def test_decorator_adds_grimorium_config_attribute(self):
        """Decorator should add _grimorium_config attribute."""

        @register_spell
        def my_spell():
            pass

        assert hasattr(my_spell, "_grimorium_config")
        assert my_spell._grimorium_config == {}

    def test_decorator_preserves_function_signature(self):
        """Decorator should preserve function name and docstring."""

        @register_spell
        def my_spell_with_doc(x: int, y: str) -> str:
            """This is my docstring."""
            return f"{y}: {x}"

        assert my_spell_with_doc.__name__ == "my_spell_with_doc"
        assert "docstring" in my_spell_with_doc.__doc__

    def test_decorator_preserves_function_behavior(self):
        """Decorated function should behave identically."""

        @register_spell
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        assert add_numbers(2, 3) == 5
        assert add_numbers(a=10, b=20) == 30

    def test_decorator_does_not_override_existing_config(self):
        """Should not override existing _grimorium_config."""

        def my_func():
            pass

        my_func._grimorium_config = {"custom": "config"}

        decorated = register_spell(my_func)

        assert decorated._grimorium_config == {"custom": "config"}

    def test_multiple_decorators(self):
        """Should work with multiple decorators."""

        def other_decorator(func):
            func._other_attr = True
            return func

        @other_decorator
        @register_spell
        def my_spell():
            pass

        assert my_spell._grimorium_spell is True
        assert my_spell._other_attr is True


class TestSpellRegistryDeprecated:
    """Tests for deprecated SpellRegistry class."""

    def test_get_spell_raises_not_implemented(self):
        """get_spell should raise NotImplementedError."""
        registry = SpellRegistry()

        with pytest.raises(NotImplementedError) as exc_info:
            registry.get_spell("any_spell")

        assert "deprecated" in str(exc_info.value).lower()

    def test_get_all_spells_raises_not_implemented(self):
        """get_all_spells should raise NotImplementedError."""
        registry = SpellRegistry()

        with pytest.raises(NotImplementedError) as exc_info:
            registry.get_all_spells()

        assert "deprecated" in str(exc_info.value).lower()


class TestSpellAlias:
    """Tests for the 'spell' alias import."""

    def test_spell_alias_works(self):
        """The @spell alias should work same as @register_spell."""
        from magetools import spell

        @spell
        def my_aliased_spell():
            pass

        assert my_aliased_spell._grimorium_spell is True
