import os

import yaml

from magetools.config import MageToolsConfig


def test_config_defaults():
    config = MageToolsConfig()
    assert config.magetools_dir_name == ".magetools"
    assert config.model_name == "gemini-1.5-flash"


def test_config_env_override():
    os.environ["MAGETOOLS_MODEL"] = "test-model"
    config = MageToolsConfig()
    assert config.model_name == "test-model"
    del os.environ["MAGETOOLS_MODEL"]


def test_config_yaml_override(tmp_path):
    yaml_content = {"model_name": "yaml-model", "magetools_dir_name": ".custom_mage"}
    config_file = tmp_path / "magetools.yaml"
    with open(config_file, "w") as f:
        yaml.dump(yaml_content, f)

    config = MageToolsConfig(root_path=tmp_path)
    assert config.model_name == "yaml-model"
    assert config.magetools_dir_name == ".custom_mage"


def test_config_paths(tmp_path):
    config = MageToolsConfig(root_path=tmp_path)
    expected_root = (tmp_path / ".magetools").resolve()
    expected_db = (expected_root / ".chroma_db").resolve()
    assert config.magetools_root == expected_root
    assert config.db_path == expected_db
