#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment. Please ensure Python 3 is installed and accessible."
    exit 1
fi
echo "Activating virtual environment..."
source .venv/bin/activate
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Please check requirements.txt and your internet connection."
    exit 1
fi
echo "Setup complete. Virtual environment '.venv' is ready and dependencies are installed."
echo "To activate the environment in your current shell, run: source .venv/bin/activate"
