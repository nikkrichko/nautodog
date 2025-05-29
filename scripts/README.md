# Test Runner Scripts

This directory contains scripts to facilitate running specific categories of tests using `pytest`.

## Prerequisites

-   **Python and Pip**: Ensure Python and pip are installed.
-   **pytest**: Install pytest: `pip install pytest`
-   **Project Dependencies**: Install project dependencies from the root of the repository: `pip install -r requirements.txt`
-   **Test Configuration (for Regression Tests)**: For regression tests, ensure you have a valid `test_config.yaml` file in `tests/unit/snmp_validator/` as per the template and documentation in that directory.

## Scripts

All scripts should be run from the **root directory** of the project.

### Smoke Tests

-   **`run_smoke_tests.sh`** (for Linux/macOS)
    -   Runs all tests marked with the `smoke` pytest marker.
    -   Command: `bash scripts/run_smoke_tests.sh` or `./scripts/run_smoke_tests.sh` (if executable permission is set).
-   **`run_smoke_tests.ps1`** (for Windows PowerShell)
    -   Runs all tests marked with the `smoke` pytest marker.
    -   Command: `Powershell -ExecutionPolicy Bypass -File scripts\run_smoke_tests.ps1`

### Regression Tests

-   **`run_regression_tests.sh`** (for Linux/macOS)
    -   Runs all tests marked with the `regression` pytest marker.
    -   Command: `bash scripts/run_regression_tests.sh` or `./scripts/run_regression_tests.sh` (if executable permission is set).
    -   **Note**: These tests depend on a correctly configured `tests/unit/snmp_validator/test_config.yaml`.
-   **`run_regression_tests.ps1`** (for Windows PowerShell)
    -   Runs all tests marked with the `regression` pytest marker.
    -   Command: `Powershell -ExecutionPolicy Bypass -File scripts\run_regression_tests.ps1`
    -   **Note**: These tests depend on a correctly configured `tests/unit/snmp_validator/test_config.yaml`.

## How it Works

The scripts use `pytest -m <marker_name> tests/` to target tests.
-   `smoke` tests are typically quick checks on basic functionality.
-   `regression` tests are more comprehensive and verify specific credential validation scenarios, often requiring external configuration (like the SNMP device details).

Test files themselves (e.g., `tests/unit/snmp_validator/smoke_snmp_validator.py`) use `pytestmark = pytest.mark.<marker_name>` to label all tests within that file with the respective marker.
