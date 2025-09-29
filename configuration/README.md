# Configuration Manager

This module provides a reusable configuration loader for Nautodog. The
`ConfigManager` class centralises the parsing of YAML configuration files and
makes the configuration data available throughout the project via a
thread-safe singleton.

## Key capabilities

- **Single initialization** – The configuration file is parsed exactly once per
  process. Subsequent calls to `ConfigManager.instance()` re-use the cached
  configuration.
- **Universal YAML support** – The loader delegates parsing to `ruamel.yaml`,
  allowing complex YAML structures including nested mappings and repeated
  elements.
- **Dot-path accessors** – `ConfigManager.get()` accepts dotted key paths to
  simplify access to deeply nested configuration entries, including list
  indices (e.g., `service.endpoints.0.url`).
- **Undefined key tracking** – Every attempt to read an undefined key is stored
  and can be inspected with `ConfigManager.list_missing_keys()`.
- **Hard reload** – Call `ConfigManager.initialize(path, force_reload=True)` or
  `ConfigManager.instance().reload()` to refresh the in-memory configuration
  after editing the YAML file.
- **Configuration introspection** – Use `ConfigManager.print_configuration()` or
  `ConfigManager.as_yaml()` to inspect the current configuration state.

## Usage

```python
from pathlib import Path
from configuration.config_manager import ConfigManager

# Initialize once at application start-up.
ConfigManager.initialize(Path("config.yaml"))

# Retrieve the singleton anywhere in the codebase.
config = ConfigManager.instance()

database_url = config.get("database.primary.url")
retry_count = config.get("service.retries", default=3)

# Examine undefined accesses (if any).
for missing in config.list_missing_keys():
    print(f"Missing key: {missing.path} (attempted {missing.attempts} times)")

# Refresh the configuration when a forced update is required.
config.reload()

# Print the currently loaded configuration.
config.print_configuration()
```

## Suggested future enhancements

The following features may be useful as the configuration manager is adopted
across the project:

1. **Environment variable overrides** – Allow selected configuration values to
   be overridden by environment variables to simplify containerized or cloud
   deployments.
2. **Schema validation** – Integrate with a validation library (e.g.
   `pydantic` or `jsonschema`) to ensure configuration files adhere to an
   expected structure before being accepted.
3. **Change notifications** – Provide hooks or callbacks that trigger when the
   configuration is reloaded so dependent components can react to updates.
4. **File watching** – Monitor the configuration file for modifications and
   reload automatically, optionally debounced to avoid repeated reloads.
5. **Secrets management integration** – Support fetching sensitive values from
   secret stores (such as AWS Secrets Manager or HashiCorp Vault) referenced in
   the YAML file.

## Testing

A dedicated unit test (`tests/test_config_manager.py`) exercises the most common
usage scenarios. Run the test suite with:

```bash
pytest tests/test_config_manager.py
```
