"""Shared pytest fixtures for magetools tests."""

import json
import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tmp_magetools_dir(tmp_path: Path) -> Path:
    """Create a temporary .magetools directory structure."""
    magetools_dir = tmp_path / ".magetools"
    magetools_dir.mkdir()
    return magetools_dir


@pytest.fixture
def sample_collection(tmp_magetools_dir: Path) -> Path:
    """Create a sample collection with manifest and spells."""
    collection = tmp_magetools_dir / "sample_collection"
    collection.mkdir()

    # Create manifest
    manifest = {
        "version": "1.0",
        "enabled": True,
        "whitelist": ["sample_spell", "another_spell"],
    }
    (collection / "manifest.json").write_text(json.dumps(manifest))

    # Create spell file
    spell_code = '''
"""Sample spells module."""

from magetools import spell

@spell
def sample_spell(x: int, y: int) -> int:
    """Add two numbers together."""
    return x + y

@spell
def another_spell(text: str) -> str:
    """Convert text to uppercase."""
    return text.upper()
'''
    (collection / "spells.py").write_text(spell_code)

    return collection


@pytest.fixture
def mock_embedding_provider() -> MagicMock:
    """Create a mock embedding provider."""
    provider = MagicMock()
    provider.get_embedding_function.return_value = MagicMock()
    provider.generate_content.return_value = "Mock generated summary"
    return provider


@pytest.fixture
def mock_vector_store() -> MagicMock:
    """Create a mock vector store."""
    store = MagicMock()
    store.list_collections.return_value = []
    store.get_or_create_collection.return_value = MagicMock()
    return store


@pytest.fixture
def mock_config(tmp_path: Path) -> MagicMock:
    """Create a mock configuration object."""
    config = MagicMock()
    config.magetools_root = tmp_path / ".magetools"
    config.db_path = tmp_path / ".magetools" / ".chroma_db"
    config.model_name = "test-model"
    config.embedding_model = "test-embedding"
    config.debug = False
    config.db_folder_name = ".chroma_db"
    return config


@pytest.fixture
def clean_env() -> Generator[None]:
    """Temporarily clear magetools-related environment variables."""
    saved = {}
    keys_to_clear = [
        "MAGETOOLS_MODEL",
        "MAGETOOLS_DIR_NAME",
        "MAGETOOLS_DB_FOLDER",
        "MAGETOOLS_DEBUG",
        "GOOGLE_API_KEY",
    ]

    for key in keys_to_clear:
        if key in os.environ:
            saved[key] = os.environ.pop(key)

    yield

    # Restore
    for key, value in saved.items():
        os.environ[key] = value


@pytest.fixture
def sample_yaml_config(tmp_path: Path) -> Path:
    """Create a sample magetools.yaml file."""
    import yaml

    config_data = {
        "model_name": "test-yaml-model",
        "embedding_model": "test-yaml-embedding",
        "magetools_dir_name": ".magetools",
        "db_folder_name": ".chroma_db",
        "debug": True,
    }

    config_path = tmp_path / "magetools.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    return config_path
