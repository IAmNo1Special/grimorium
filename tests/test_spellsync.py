"""Unit tests for SpellSync hashing and core logic."""

import hashlib
from unittest.mock import MagicMock, patch


class TestSpellSyncHashing:
    """Tests for SpellSync hash computation logic."""

    def test_compute_grimorium_hash_empty_folder(self, tmp_path):
        """Hash of empty folder should be consistent."""
        from magetools.spellsync import SpellSync

        # Create a mock spell sync with minimal deps
        with patch.object(SpellSync, "__init__", lambda self, **kwargs: None):
            sync = SpellSync()
            sync.MAGETOOLS_ROOT = tmp_path
            sync.config = MagicMock()
            sync.config.db_folder_name = ".chroma_db"

            # Create empty folder
            folder = tmp_path / "test_grimorium"
            folder.mkdir()

            hash1 = sync._compute_grimorium_hash(folder)
            hash2 = sync._compute_grimorium_hash(folder)

            assert hash1 == hash2
            assert hash1 == hashlib.md5().hexdigest()  # Empty hash

    def test_compute_grimorium_hash_with_files(self, tmp_path):
        """Hash should change when file contents change."""
        from magetools.spellsync import SpellSync

        with patch.object(SpellSync, "__init__", lambda self, **kwargs: None):
            sync = SpellSync()
            sync.MAGETOOLS_ROOT = tmp_path
            sync.config = MagicMock()
            sync.config.db_folder_name = ".chroma_db"

            folder = tmp_path / "test_grimorium"
            folder.mkdir()

            # Create initial file
            py_file = folder / "spell.py"
            py_file.write_text("def foo(): pass")

            hash1 = sync._compute_grimorium_hash(folder)

            # Modify file
            py_file.write_text("def bar(): pass")
            hash2 = sync._compute_grimorium_hash(folder)

            assert hash1 != hash2  # Hash should change

    def test_compute_grimorium_hash_ignores_private_files(self, tmp_path):
        """Hash should ignore files starting with . or _."""
        from magetools.spellsync import SpellSync

        with patch.object(SpellSync, "__init__", lambda self, **kwargs: None):
            sync = SpellSync()
            sync.MAGETOOLS_ROOT = tmp_path
            sync.config = MagicMock()
            sync.config.db_folder_name = ".chroma_db"

            folder = tmp_path / "test_grimorium"
            folder.mkdir()

            # Create private files only
            (folder / "_private.py").write_text("secret")
            (folder / ".hidden.py").write_text("hidden")

            hash1 = sync._compute_grimorium_hash(folder)

            # Hash should be empty since all files are ignored
            assert hash1 == hashlib.md5().hexdigest()


class TestExtractSpellDocs:
    """Tests for spell docstring extraction."""

    def test_extract_module_docstring(self, tmp_path):
        """Should extract module-level docstrings."""
        from magetools.spellsync import SpellSync

        with patch.object(SpellSync, "__init__", lambda self, **kwargs: None):
            sync = SpellSync()

            folder = tmp_path / "test"
            folder.mkdir()

            (folder / "spell.py").write_text('"""Module docstring."""\ndef foo(): pass')

            docs = sync._extract_spell_docs(folder)

            assert len(docs) == 1
            assert "Module docstring" in docs[0]

    def test_extract_function_docstring(self, tmp_path):
        """Should extract function docstrings."""
        from magetools.spellsync import SpellSync

        with patch.object(SpellSync, "__init__", lambda self, **kwargs: None):
            sync = SpellSync()

            folder = tmp_path / "test"
            folder.mkdir()

            (folder / "spell.py").write_text(
                'def foo():\n    """Function doc."""\n    pass'
            )

            docs = sync._extract_spell_docs(folder)

            assert len(docs) == 1
            assert "Function doc" in docs[0]

    def test_extract_skips_syntax_errors(self, tmp_path):
        """Should gracefully skip files with syntax errors."""
        from magetools.spellsync import SpellSync

        with patch.object(SpellSync, "__init__", lambda self, **kwargs: None):
            sync = SpellSync()

            folder = tmp_path / "test"
            folder.mkdir()

            (folder / "broken.py").write_text("def foo( syntax error")

            docs = sync._extract_spell_docs(folder)

            assert docs == []  # No crash, empty result
