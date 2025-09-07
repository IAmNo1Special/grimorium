from pathlib import Path


# TODO: Finish & add config manager to handle .yaml config file
class ConfigManager:
    def __init__(self):
        self.grimorium_dir = self.get_user_grimorium_dir()
        self.config_path = self.get_config_filepath()

    def get_user_grimorium_dir() -> Path:
        """Get the user's Grimorium directory.

        If the Grimorium directory doesn't exist, it will be created.

        Returns:
            Path: Path to the user's Grimorium directory.
        """
        return Path.home() / ".grimorium"

    def get_config_filepath() -> Path:
        """Get the path to the user's config file.

        If the config file doesn't exist, it will be created.

        Returns:
            Path: Path to the user's config file.
        """
        config_dir = get_user_grimorium_dir()
        config_filepath = config_dir / "config.yaml"

        # Create config directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)

        return config_filepath
