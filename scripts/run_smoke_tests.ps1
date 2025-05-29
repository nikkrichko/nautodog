# This script runs all tests marked as 'smoke'
# located within the 'tests/' directory.
# It should be run from the root of the project.
Write-Host "Running smoke tests..."
pytest -m smoke tests/
