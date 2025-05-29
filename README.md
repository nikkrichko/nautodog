# Project Setup: vnautodog Environment

This document provides instructions on how to set up the Python virtual environment for this project, named `vnautodog`. You can either set it up manually or use the provided automation scripts.

## Prerequisites

*   **Python 3**: Ensure Python 3 (3.7 or newer recommended) is installed on your system and accessible via your system's PATH. You can download it from [python.org](https://www.python.org/downloads/).
*   **pip**: Python's package installer, usually comes with Python.
*   **venv**: Python's built-in module for creating virtual environments (standard with Python 3.3+).

## `requirements.txt`

This project uses a `requirements.txt` file to manage dependencies. It lists all the Python packages needed for the project.

## Option 1: Manual Setup

Follow these steps to manually create the virtual environment and install dependencies.

### 1. Create the Virtual Environment

Open your terminal or command prompt, navigate to the project's root directory (where this `README.md` is located), and run:

```bash
# For Linux/macOS
python3 -m venv vnautodog

# For Windows (cmd.exe)
python -m venv vnautodog

# For Windows (PowerShell)
py -m venv vnautodog 
# or python -m venv vnautodog
```
This will create a new folder named `vnautodog` in your project root, which contains the Python interpreter and a copy of pip.

### 2. Activate the Virtual Environment

Before installing dependencies or running your application, you need to activate the environment:

```bash
# For Linux/macOS (bash/zsh)
source vnautodog/bin/activate

# For Windows (cmd.exe)
.\vnautodog\Scripts\activate.bat

# For Windows (PowerShell)
.\vnautodog\Scripts\Activate.ps1
```
Your command prompt should change to indicate that the virtual environment is active (e.g., `(vnautodog) user@host:...$`).

### 3. Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Deactivate the Virtual Environment

When you're done working in the virtual environment, you can deactivate it:

```bash
deactivate
```

This command works on all platforms when an environment is active.

## Option 2: Using Automation Scripts

Helper scripts are provided in the `scripts/` directory to automate the creation of the `vnautodog` virtual environment and installation of dependencies.

### Using `install_venv.sh` (for Linux/macOS)

1.  Open your terminal.
2.  Navigate to the project's root directory.
3.  Make sure the script is executable:
    ```bash
    chmod +x scripts/install_venv.sh
    ```
4.  Run the script:
    ```bash
    bash scripts/install_venv.sh
    ```
    Or if you are already in the `scripts` directory:
    ```bash
    bash ./install_venv.sh
    ```
    The script will check for Python, create the `vnautodog` virtual environment in the project root, activate it for its own session, and install packages from `requirements.txt`.
5.  After the script finishes, you'll need to activate the environment in your current shell session to use it:
    ```bash
    source vnautodog/bin/activate
    ```

### Using `install_venv.ps1` (for Windows PowerShell)

1.  Open PowerShell.
2.  Navigate to the project's root directory.
3.  You may need to adjust your execution policy to run local scripts. For example:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process 
    ```
    (Use with caution and understand the implications of execution policies).
4.  Run the script:
    ```powershell
    .\scripts\install_venv.ps1
    ```
    Or if you are already in the `scripts` directory:
    ```powershell
    .\install_venv.ps1
    ```
    The script will check for Python, create the `vnautodog` virtual environment in the project root, activate it for its own session, and install packages from `requirements.txt`.
5.  After the script finishes, you'll need to activate the environment in your current PowerShell session to use it:
    ```powershell
    .\vnautodog\Scripts\Activate.ps1
    ```

## Working with the Environment

Once the `vnautodog` environment is created and activated, any Python packages you install will be isolated to this environment, and running `python` or `pip` will use the versions within `vnautodog`.
