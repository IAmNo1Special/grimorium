"""Unit tests for manifest.json functionality."""

import json

from magetools.spellsync import _is_spell_allowed, _load_manifest


class TestLoadManifest:
    """Tests for manifest loading."""

    def test_load_manifest_not_found(self, tmp_path):
        """Should return None if manifest doesn't exist."""
        result = _load_manifest(tmp_path)
        assert result is None

    def test_load_manifest_valid(self, tmp_path):
        """Should load valid manifest."""
        manifest = {"whitelist": ["spell_a", "spell_b"], "enabled": True}
        (tmp_path / "manifest.json").write_text(json.dumps(manifest))

        result = _load_manifest(tmp_path)

        assert result == manifest

    def test_load_manifest_invalid_json(self, tmp_path):
        """Should return None for invalid JSON."""
        (tmp_path / "manifest.json").write_text("{ invalid json }")

        result = _load_manifest(tmp_path)

        assert result is None

    def test_load_manifest_not_dict(self, tmp_path):
        """Should return None if manifest is not a dict."""
        (tmp_path / "manifest.json").write_text('["list", "not", "dict"]')

        result = _load_manifest(tmp_path)

        assert result is None


class TestIsSpellAllowed:
    """Tests for spell filtering logic."""

    def test_no_manifest_allows_all(self):
        """All spells allowed when no manifest."""
        assert _is_spell_allowed("any_spell", None) is True

    def test_disabled_collection_blocks_all(self):
        """Disabled collection blocks all spells."""
        manifest = {"enabled": False}

        assert _is_spell_allowed("any_spell", manifest) is False

    def test_whitelist_allows_only_listed(self):
        """Only whitelisted spells allowed."""
        manifest = {"whitelist": ["allowed_spell"]}

        assert _is_spell_allowed("allowed_spell", manifest) is True
        assert _is_spell_allowed("blocked_spell", manifest) is False

    def test_blacklist_blocks_listed(self):
        """Blacklisted spells are blocked."""
        manifest = {"blacklist": ["blocked_spell"]}

        assert _is_spell_allowed("allowed_spell", manifest) is True
        assert _is_spell_allowed("blocked_spell", manifest) is False

    def test_whitelist_and_blacklist_combined(self):
        """Blacklist applies after whitelist."""
        manifest = {
            "whitelist": ["spell_a", "spell_b", "spell_c"],
            "blacklist": ["spell_b"],
        }

        assert _is_spell_allowed("spell_a", manifest) is True
        assert _is_spell_allowed("spell_b", manifest) is False  # Blocked by blacklist
        assert _is_spell_allowed("spell_c", manifest) is True
        assert _is_spell_allowed("spell_d", manifest) is False  # Not in whitelist

    def test_empty_whitelist_blocks_all(self):
        """Empty whitelist means no spells allowed."""
        manifest = {"whitelist": []}

        assert _is_spell_allowed("any_spell", manifest) is False
