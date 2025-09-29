"""Configuration package exposing the ConfigManager singleton."""

from .config_manager import ConfigManager, MissingKey

__all__ = ["ConfigManager", "MissingKey"]
