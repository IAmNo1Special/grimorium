"""Unit tests for magetools CLI."""

from unittest.mock import MagicMock, patch

from magetools.__main__ import init_collection, scan_spells


def test_init_collection_success(tmp_path):
    d = tmp_path / "coll"
    d.mkdir()
    with patch("builtins.input", return_value="y"):
        init_collection(str(d))
    assert (d / "manifest.json").exists()


def test_scan_spells_empty(capsys):
    with patch("magetools.spellsync.discover_and_load_spells") as mock_load:
        mock_load.return_value = None
        scan_spells()
        captured = capsys.readouterr()
        assert "No spells loaded" in captured.out


def test_scan_spells_found(capsys):
    def mock_load(registry=None, **_kwargs):
        if registry is not None:
            registry["my_spell"] = MagicMock()

    with (
        patch("magetools.spellsync.discover_and_load_spells", side_effect=mock_load),
        patch("magetools.spellsync.SpellSync"),
    ):
        scan_spells()
        captured = capsys.readouterr()
        assert "Found 1 spell" in captured.out
        assert "my_spell" in captured.out
