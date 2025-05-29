#!/bin/bash
# This script runs all tests marked as 'smoke'
# located within the 'tests/' directory.
# It should be run from the root of the project.
echo "Running smoke tests..."
pytest -m smoke tests/
