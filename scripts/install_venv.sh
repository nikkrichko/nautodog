#!/bin/bash

# Script to create a Python virtual environment and install dependencies.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
VENV_NAME="vnautodog"
REQUIREMENTS_FILE="requirements.txt" # Assuming it's in the parent directory of this script's location
PYTHON_ALIAS="python3" # Change this if your python3 alias is different (e.g., python)

# --- Helper Functions ---

# Function to print messages
print_message() {
  echo "--------------------------------------------------"
  echo "$1"
  echo "--------------------------------------------------"
}

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# --- Main Script ---

print_message "Starting venv setup for $VENV_NAME"

# 1. Check for Python
print_message "Step 1: Checking for Python installation..."
if ! command_exists $PYTHON_ALIAS; then
  echo "Error: $PYTHON_ALIAS is not installed or not found in PATH."
  echo "Please install Python 3 and ensure it's added to your PATH."
  exit 1
fi
echo "$PYTHON_ALIAS found: $($PYTHON_ALIAS --version)"

# 2. Check for venv module (usually part of Python 3 standard library)
print_message "Step 2: Checking for Python venv module..."
if ! $PYTHON_ALIAS -m venv -h > /dev/null 2>&1; then
    echo "Error: The Python 'venv' module is not available."
    echo "Please ensure your Python installation includes the venv module."
    exit 1
fi
echo "Python 'venv' module found."

# Determine the project root directory (one level up from the script's directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Full path to the virtual environment
VENV_PATH="$PROJECT_ROOT/$VENV_NAME"
# Full path to the requirements file
REQUIREMENTS_PATH="$PROJECT_ROOT/$REQUIREMENTS_FILE"

print_message "Project root identified as: $PROJECT_ROOT"
print_message "Virtual environment will be created at: $VENV_PATH"
print_message "Requirements file expected at: $REQUIREMENTS_PATH"

# 3. Create Virtual Environment
print_message "Step 3: Creating virtual environment '$VENV_NAME'..."
if [ -d "$VENV_PATH" ]; then
  echo "Virtual environment '$VENV_NAME' already exists at $VENV_PATH."
  read -p "Do you want to remove the existing environment and recreate it? (y/N): " choice
  case "$choice" in
    y|Y )
      echo "Removing existing virtual environment..."
      rm -rf "$VENV_PATH"
      $PYTHON_ALIAS -m venv "$VENV_PATH"
      echo "Virtual environment '$VENV_NAME' recreated."
      ;;
    * )
      echo "Skipping venv creation. Using existing environment."
      ;;
  esac
else
  $PYTHON_ALIAS -m venv "$VENV_PATH"
  echo "Virtual environment '$VENV_NAME' created at $VENV_PATH."
fi

# 4. Activate Virtual Environment and Install Requirements
print_message "Step 4: Activating virtual environment and installing requirements..."

# Source the activate script
# shellcheck source=/dev/null
source "$VENV_PATH/bin/activate"
echo "Virtual environment activated."
echo "Current Python: $(which python)"

# Check if requirements file exists
if [ ! -f "$REQUIREMENTS_PATH" ]; then
    echo "Error: $REQUIREMENTS_FILE not found at $REQUIREMENTS_PATH."
    echo "Please ensure the requirements file is in the project root."
    # Deactivate venv before exiting if created
    deactivate || echo "No active virtual environment to deactivate."
    exit 1
fi

# Install requirements
echo "Installing packages from $REQUIREMENTS_FILE..."
pip install -r "$REQUIREMENTS_PATH"
if [ $? -eq 0 ]; then
  echo "Packages installed successfully."
else
  echo "Error: Failed to install packages from $REQUIREMENTS_FILE."
  echo "Please check the output above for details."
  # Deactivate venv before exiting
  deactivate || echo "No active virtual environment to deactivate."
  exit 1
fi

print_message "Setup complete!"
echo "To activate the virtual environment in your current shell, run:"
echo "  source $VENV_PATH/bin/activate"
echo "Or, if you are in the project root:"
echo "  source $VENV_NAME/bin/activate"

# Note: The script activates the venv for its own execution.
# The user will need to source the activate script again in their own shell
# if they want to use the venv after this script finishes.
