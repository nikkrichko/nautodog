#Requires -Version 5.1
<#
.SYNOPSIS
    Creates a Python virtual environment and installs dependencies from requirements.txt.
.DESCRIPTION
    This script automates the setup of a Python virtual environment named 'vnautodog'.
    It checks for Python, creates the venv, activates it (for the script's session),
    and installs packages from a 'requirements.txt' file located in the project root.
.NOTES
    Author: AI Assistant
    Version: 1.0
    Make sure Python 3 is installed and in your PATH.
    The 'requirements.txt' file must be present in the project root directory (one level above this script).
#>

# --- Configuration ---
$VenvName = "vnautodog"
$RequirementsFile = "requirements.txt" # Assumed to be in the parent directory
$PythonExecutable = "python" # Change this if your python alias is different (e.g., python3, py)

# --- Helper Functions ---

# Function to print messages
function Print-Message {
    param (
        [string]$Message
    )
    Write-Host "--------------------------------------------------"
    Write-Host $Message
    Write-Host "--------------------------------------------------"
}

# Function to check if a command exists
function Test-CommandExists {
    param (
        [string]$Command
    )
    return (Get-Command $Command -ErrorAction SilentlyContinue) -ne $null
}

# --- Main Script ---

Print-Message "Starting venv setup for $VenvName"

# 1. Check for Python
Print-Message "Step 1: Checking for Python installation..."
if (-not (Test-CommandExists $PythonExecutable)) {
    Write-Error "$PythonExecutable is not installed or not found in PATH."
    Write-Error "Please install Python 3 and ensure it's added to your PATH."
    exit 1
}
$PythonVersion = & $PythonExecutable --version
Print-Message "$PythonExecutable found: $PythonVersion"

# 2. Check for venv module
Print-Message "Step 2: Checking for Python venv module..."
# Attempt to get help for the venv module. If it fails, venv might not be available or working.
try {
    & $PythonExecutable -m venv -h | Out-Null
    Print-Message "Python 'venv' module found."
}
catch {
    Write-Error "The Python 'venv' module is not available or did not execute correctly."
    Write-Error "Please ensure your Python installation includes the venv module."
    exit 1
}

# Determine the project root directory (one level up from the script's directory)
$ScriptPath = $MyInvocation.MyCommand.Path
$ScriptDir = Split-Path -Path $ScriptPath -Parent
$ProjectRoot = Split-Path -Path $ScriptDir -Parent

# Full path to the virtual environment
$VenvPath = Join-Path -Path $ProjectRoot -ChildPath $VenvName
# Full path to the requirements file
$RequirementsPath = Join-Path -Path $ProjectRoot -ChildPath $RequirementsFile

Print-Message "Project root identified as: $ProjectRoot"
Print-Message "Virtual environment will be created at: $VenvPath"
Print-Message "Requirements file expected at: $RequirementsPath"

# 3. Create Virtual Environment
Print-Message "Step 3: Creating virtual environment '$VenvName'..."
if (Test-Path -Path $VenvPath) {
    Write-Warning "Virtual environment '$VenvName' already exists at $VenvPath."
    $choice = Read-Host "Do you want to remove the existing environment and recreate it? (y/N)"
    if ($choice -eq 'y' -or $choice -eq 'Y') {
        Write-Host "Removing existing virtual environment..."
        Remove-Item -Path $VenvPath -Recurse -Force
        & $PythonExecutable -m venv $VenvPath
        Print-Message "Virtual environment '$VenvName' recreated."
    }
    else {
        Print-Message "Skipping venv creation. Using existing environment."
    }
}
else {
    & $PythonExecutable -m venv $VenvPath
    Print-Message "Virtual environment '$VenvName' created at $VenvPath."
}

# 4. Activate Virtual Environment and Install Requirements
Print-Message "Step 4: Activating virtual environment and installing requirements..."

# Path to the activation script
$ActivateScript = Join-Path -Path $VenvPath -ChildPath "Scripts\Activate.ps1" # Common for Windows

if (-not (Test-Path $ActivateScript)) {
    Write-Error "Activation script not found at $ActivateScript. Your venv structure might be different."
    exit 1
}

# In PowerShell, "activating" a venv for the current script means running the activate script
# which modifies the current session's environment variables (like PATH).
# For the user to use the venv after the script, they need to run it in their own session.
try {
    # Invoke the activation script in the current scope
    . $ActivateScript
    Print-Message "Virtual environment activated for this script session."
    $CurrentPython = Get-Command python | Select-Object -ExpandProperty Source
    Print-Message "Current Python: $CurrentPython"
}
catch {
    Write-Error "Failed to activate the virtual environment. Error: $($_.Exception.Message)"
    exit 1
}


# Check if requirements file exists
if (-not (Test-Path -Path $RequirementsPath -PathType Leaf)) {
    Write-Error "$RequirementsFile not found at $RequirementsPath."
    Write-Error "Please ensure the requirements file is in the project root."
    # It's good practice to deactivate if something goes wrong, though in PS it's more about PATH restoration
    # which happens when the script ends or by calling a deactivate function if the venv provides one.
    # For simplicity, we'll just exit.
    exit 1
}

# Install requirements
Print-Message "Installing packages from $RequirementsFile..."
& $PythonExecutable -m pip install -r $RequirementsPath
if ($LASTEXITCODE -eq 0) {
    Print-Message "Packages installed successfully."
}
else {
    Write-Error "Failed to install packages from $RequirementsFile."
    Write-Error "Please check the output above for details."
    exit 1
}

Print-Message "Setup complete!"
Write-Host "To activate the virtual environment in your current PowerShell session, run:"
Write-Host "  & '$ActivateScript'"
Write-Host "Or, if you are in the project root and the venv is '$VenvName':"
Write-Host "  & '.\$VenvName\Scripts\Activate.ps1'"

# Note: The script activates the venv for its own execution.
# The user will need to run the activate script again in their own shell
# if they want to use the venv after this script finishes.
