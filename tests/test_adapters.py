"""Unit tests for magetools adapters module."""

import os
from unittest.mock import patch

import pytest

from magetools.adapters import (
    MockEmbeddingProvider,
    _MockEmbeddingFunction,
    get_default_provider,
)
from magetools.exceptions import ConfigurationError


def test_mock_provider_basics():
    """Verify MockEmbeddingProvider provides basic fallback functionality."""
    p = MockEmbeddingProvider()
    assert "Mock" in p.generate_content("test")
    func = p.get_embedding_function()
    assert isinstance(func, _MockEmbeddingFunction)
    assert len(func(["hello"])[0]) == 768


def test_get_default_provider_no_key():
    """Fallback to MockProvider when API key is missing."""
    os.environ.pop("GOOGLE_API_KEY", None)
    p = get_default_provider()
    assert isinstance(p, MockEmbeddingProvider)


def test_import_genai_error_handling():
    """Ensure ConfigurationError is raised when genai is missing."""
    from magetools.adapters import _import_genai

    with (
        patch("builtins.__import__", side_effect=ImportError),
        pytest.raises(ConfigurationError),
    ):
        _import_genai()
