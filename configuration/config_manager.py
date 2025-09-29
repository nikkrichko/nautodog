"""Configuration management utilities for nautodog.

This module exposes the :class:`ConfigManager` singleton, which centralizes
loading and accessing YAML-based configuration files across the project. The
manager automatically parses the target configuration file into memory and
provides dot-notation access helpers, facilities to inspect undefined keys that
were requested by the application, and tools to refresh the configuration when a
hard update is required.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
import sys
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, TextIO, Union

from ruamel.yaml import YAML


_UNSET = object()


def _convert_to_builtin(value: Any) -> Any:
    """Recursively convert ruamel.yaml containers into built-in Python types."""

    if isinstance(value, MutableMapping):
        return {key: _convert_to_builtin(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_convert_to_builtin(item) for item in value]
    return value


def _ensure_mapping(node: Any) -> MutableMapping[str, Any]:
    """Return *node* if it is mapping-like, otherwise raise ``TypeError``."""

    if isinstance(node, MutableMapping):
        return node
    raise TypeError(
        "Configuration root must be a mapping/dictionary; got " f"{type(node)!r}"
    )


@dataclass(frozen=True)
class MissingKey:
    """Representation of a missing configuration key access."""

    path: str
    attempts: int


class ConfigManager:
    """Singleton loader for YAML configuration files."""

    _instance: Optional["ConfigManager"] = None
    _lock: RLock = RLock()

    def __init__(self, config_path: Path) -> None:
        raise RuntimeError(
            "Direct instantiation is not supported. Use ConfigManager.initialize()."
        )

    @classmethod
    def initialize(
        cls,
        config_path: Union[str, Path],
        *,
        force_reload: bool = False,
    ) -> "ConfigManager":
        """Initialize the singleton with *config_path* if not already done."""

        resolved_path = Path(config_path).expanduser().resolve()
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._config_path = resolved_path  # type: ignore[attr-defined]
                cls._instance._yaml = YAML(typ="safe")  # type: ignore[attr-defined]
                cls._instance._yaml.default_flow_style = False  # type: ignore[attr-defined]
                cls._instance._missing: Dict[str, int] = {}  # type: ignore[attr-defined]
                cls._instance._config: MutableMapping[str, Any] = {}  # type: ignore[attr-defined]
                cls._instance._last_loaded: Optional[datetime] = None  # type: ignore[attr-defined]
                cls._instance._load()  # type: ignore[attr-defined]
            else:
                if resolved_path != cls._instance._config_path and not force_reload:  # type: ignore[attr-defined]
                    raise ValueError(
                        "Configuration already initialized with a different file. "
                        "Use force_reload=True to override."
                    )
                cls._instance._config_path = resolved_path  # type: ignore[attr-defined]
                if force_reload:
                    cls._instance.reload()
        return cls._instance

    @classmethod
    def instance(cls) -> "ConfigManager":
        """Return the active singleton instance."""

        with cls._lock:
            if cls._instance is None:
                raise RuntimeError(
                    "ConfigManager is not initialized. Call ConfigManager.initialize() first."
                )
            return cls._instance

    def _load(self) -> None:
        """Load the YAML configuration into memory."""

        config_path: Path = self._config_path  # type: ignore[attr-defined]
        yaml_loader: YAML = self._yaml  # type: ignore[attr-defined]

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with config_path.open("r", encoding="utf-8") as file:
            data = yaml_loader.load(file) or {}

        mapping = _ensure_mapping(data)
        self._config = mapping  # type: ignore[attr-defined]
        self._missing = {}  # type: ignore[attr-defined]
        self._last_loaded = datetime.now(timezone.utc)  # type: ignore[attr-defined]

    # Public API -----------------------------------------------------------------
    @property
    def path(self) -> Path:
        """Return the path of the configuration file."""

        return self._config_path  # type: ignore[attr-defined]

    @property
    def last_loaded(self) -> Optional[datetime]:
        """Return the UTC timestamp of the last successful load."""

        return self._last_loaded  # type: ignore[attr-defined]

    def to_dict(self) -> Dict[str, Any]:
        """Return a deep copy of the configuration mapping as plain Python objects."""

        return _convert_to_builtin(self._config)  # type: ignore[attr-defined]

    def reload(self) -> None:
        """Force a reload of the configuration file from disk."""

        with self._lock:
            self._load()

    def get(
        self,
        key_path: str,
        default: Any = _UNSET,
        *,
        raise_if_missing: bool = False,
        record_missing: bool = True,
    ) -> Any:
        """Retrieve a configuration value using a dotted path."""

        value = self._config  # type: ignore[attr-defined]
        segments = [segment for segment in key_path.split(".") if segment]
        for segment in segments:
            if isinstance(value, MutableMapping) and segment in value:
                value = value[segment]
            elif isinstance(value, list):
                try:
                    index = int(segment)
                except ValueError:
                    if record_missing:
                        self._missing[key_path] = self._missing.get(key_path, 0) + 1  # type: ignore[attr-defined]
                    if raise_if_missing or default is _UNSET:
                        raise KeyError(
                            f"Configuration list index '{segment}' is not an integer for path '{key_path}'"
                        )
                    return default
                if 0 <= index < len(value):
                    value = value[index]
                else:
                    if record_missing:
                        self._missing[key_path] = self._missing.get(key_path, 0) + 1  # type: ignore[attr-defined]
                    if raise_if_missing or default is _UNSET:
                        raise KeyError(
                            f"Configuration list index '{segment}' out of range for path '{key_path}'"
                        )
                    return default
            else:
                if record_missing:
                    self._missing[key_path] = self._missing.get(key_path, 0) + 1  # type: ignore[attr-defined]
                if raise_if_missing or default is _UNSET:
                    raise KeyError(f"Configuration key '{key_path}' is not defined")
                return default
        return value

    def list_missing_keys(self) -> List[MissingKey]:
        """Return a list of missing key accesses observed so far."""

        return [MissingKey(path=path, attempts=count) for path, count in sorted(self._missing.items())]  # type: ignore[attr-defined]

    def iter_items(self) -> Iterable[tuple[str, Any]]:
        """Iterate over top-level key/value pairs."""

        return self._config.items()  # type: ignore[attr-defined]

    def print_configuration(self, stream: TextIO = sys.stdout) -> None:
        """Print the current configuration to *stream* (defaults to stdout)."""

        yaml_dumper = YAML()
        yaml_dumper.default_flow_style = False
        yaml_dumper.dump(self._config, stream)  # type: ignore[attr-defined]

    def as_yaml(self) -> str:
        """Return the configuration serialized as YAML text."""

        yaml_dumper = YAML()
        yaml_dumper.default_flow_style = False
        buffer = StringIO()
        yaml_dumper.dump(self._config, buffer)  # type: ignore[attr-defined]
        return buffer.getvalue()


__all__ = ["ConfigManager", "MissingKey"]
