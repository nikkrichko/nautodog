# This script runs all tests marked as 'regression'
# located within the 'tests/' directory.
# It should be run from the root of the project.
# Ensure you have a valid 'tests/unit/snmp_validator/test_config.yaml'
# for regression tests to run meaningfully.
Write-Host "Running regression tests..."
pytest -m regression tests/
