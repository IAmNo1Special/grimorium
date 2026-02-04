import logging
import os
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# Default constants
DEFAULT_MAGETOOLS_DIR = ".magetools"
DEFAULT_DB_FOLDER = ".chroma_db"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_EMBEDDING_MODEL = "models/text-embedding-004"


class MageToolsConfig:
    """Configuration loader for magetools."""

    def __init__(
        self,
        root_path: Path | None = None,
        config_path: Path | None = None,
    ):
        self.root_path = root_path or Path.cwd()

        # Load defaults
        self.magetools_dir_name = os.getenv("MAGETOOLS_DIR_NAME", DEFAULT_MAGETOOLS_DIR)
        self.db_folder_name = os.getenv("MAGETOOLS_DB_FOLDER", DEFAULT_DB_FOLDER)
        self.model_name = os.getenv("MAGETOOLS_MODEL", DEFAULT_MODEL)
        self.embedding_model = os.getenv(
            "MAGETOOLS_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL
        )
        self.debug = os.getenv("MAGETOOLS_DEBUG", "false").lower() == "true"

        # Load from YAML if exists
        self.config_path = config_path or self.root_path / "magetools.yaml"
        if self.config_path.exists():
            self._load_from_yaml(self.config_path)

    def _load_from_yaml(self, path: Path):
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    self.magetools_dir_name = data.get(
                        "magetools_dir_name", self.magetools_dir_name
                    )
                    self.db_folder_name = data.get(
                        "db_folder_name", self.db_folder_name
                    )
                    self.model_name = data.get("model_name", self.model_name)
                    self.embedding_model = data.get(
                        "embedding_model", self.embedding_model
                    )
                    self.debug = data.get("debug", self.debug)
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")

    @property
    def magetools_root(self) -> Path:
        """Absolute path to the .magetools directory."""
        return (self.root_path / self.magetools_dir_name).resolve()

    @property
    def db_path(self) -> Path:
        """Absolute path to the database folder."""
        return (self.magetools_root / self.db_folder_name).resolve()

    def validate(self, require_magetools_dir: bool = False) -> list[str]:
        """Validate configuration and return list of warnings.

        Args:
            require_magetools_dir: If True, raises ConfigurationError if .magetools doesn't exist.

        Returns:
            List of warning messages (non-fatal issues).
        """
        from .exceptions import ConfigurationError

        warnings = []

        # Check if root_path exists
        if not self.root_path.exists():
            raise ConfigurationError(
                f"Root path does not exist: {self.root_path}. "
                "Provide a valid root_path or check your working directory."
            )

        # Check if magetools directory exists
        if not self.magetools_root.exists():
            if require_magetools_dir:
                raise ConfigurationError(
                    f"Magetools directory not found at {self.magetools_root}. "
                    f"Create a '{self.magetools_dir_name}' folder to store your spells."
                )
            else:
                warnings.append(
                    f"Magetools directory not found at {self.magetools_root}. "
                    "Spell discovery will not find any spells."
                )

        return warnings


# Default shared config instance
def get_config(root_path: Path | None = None) -> MageToolsConfig:
    return MageToolsConfig(root_path=root_path)
