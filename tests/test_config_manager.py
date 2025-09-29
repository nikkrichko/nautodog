from pathlib import Path

import pytest
from ruamel.yaml import YAML

from configuration.config_manager import ConfigManager


@pytest.fixture(autouse=True)
def reset_singleton():
    # Ensure each test starts with a clean singleton instance.
    ConfigManager._instance = None  # type: ignore[attr-defined]
    yield
    ConfigManager._instance = None  # type: ignore[attr-defined]


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    source = Path(__file__).parent / "data" / "config_sample.yaml"
    destination = tmp_path / "config.yaml"
    destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return destination


def test_singleton_initialization(config_file: Path) -> None:
    first = ConfigManager.initialize(config_file)
    second = ConfigManager.initialize(config_file)
    assert first is second


def test_get_nested_value_and_missing_tracking(config_file: Path) -> None:
    manager = ConfigManager.initialize(config_file)
    assert manager.get("database.primary.credentials.username") == "admin"
    assert manager.get("service.retries") == 5
    assert manager.get("service.endpoints.0.timeout") == 10

    # Request an undefined key and verify it is tracked.
    with pytest.raises(KeyError):
        manager.get("service.unknown", raise_if_missing=True)

    missing_entries = manager.list_missing_keys()
    assert len(missing_entries) == 1
    assert missing_entries[0].path == "service.unknown"
    assert missing_entries[0].attempts == 1


def test_reload_updates_configuration(config_file: Path) -> None:
    manager = ConfigManager.initialize(config_file)
    assert manager.get("service.retries") == 5

    # Modify the underlying file and ensure reload picks up the change.
    yaml = YAML()
    config_data = yaml.load(config_file.read_text(encoding="utf-8"))
    config_data["service"]["retries"] = 7
    with config_file.open("w", encoding="utf-8") as handle:
        yaml.dump(config_data, handle)

    manager.reload()
    assert manager.get("service.retries") == 7


def test_to_dict_returns_plain_objects(config_file: Path) -> None:
    manager = ConfigManager.initialize(config_file)
    plain = manager.to_dict()
    assert isinstance(plain, dict)
    assert plain["service"]["name"] == "nautodog"
    assert isinstance(plain["database"], dict)
