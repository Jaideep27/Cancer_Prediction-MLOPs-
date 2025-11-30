"""Configuration management utilities."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for loading and accessing config files."""

    _instance: Optional["Config"] = None
    _configs: Dict[str, Any] = {}

    def __new__(cls) -> "Config":
        """Singleton pattern to ensure only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a configuration file.

        Args:
            config_name: Name of the configuration (e.g., 'model_config')
            config_path: Optional custom path to config file

        Returns:
            Configuration dictionary
        """
        if config_name in self._configs:
            return self._configs[config_name]

        if config_path is None:
            config_dir = Path(__file__).parent.parent.parent / "configs"
            config_path = config_dir / f"{config_name}.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self._configs[config_name] = config
        return config

    def get(self, config_name: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            config_name: Name of the configuration
            key: Optional nested key (e.g., 'model.params.learning_rate')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        if config_name not in self._configs:
            self.load(config_name)

        config = self._configs[config_name]

        if key is None:
            return config

        # Support nested keys like 'model.params.learning_rate'
        keys = key.split(".")
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def reload(self, config_name: str) -> Dict[str, Any]:
        """
        Reload a configuration file.

        Args:
            config_name: Name of the configuration

        Returns:
            Reloaded configuration dictionary
        """
        if config_name in self._configs:
            del self._configs[config_name]
        return self.load(config_name)


# Global config instance
_config = Config()


def load_config(config_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a configuration file.

    Args:
        config_name: Name of the configuration
        config_path: Optional custom path to config file

    Returns:
        Configuration dictionary
    """
    return _config.load(config_name, config_path)


def get_config(config_name: str, key: Optional[str] = None, default: Any = None) -> Any:
    """
    Get configuration value.

    Args:
        config_name: Name of the configuration
        key: Optional nested key
        default: Default value if key not found

    Returns:
        Configuration value
    """
    return _config.get(config_name, key, default)


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value
    """
    return os.getenv(key, default)
