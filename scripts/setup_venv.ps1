Write-Host "Creating virtual environment..."
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create virtual environment. Please ensure Python is installed and in your PATH."
    exit 1
}
Write-Host "Activating virtual environment and installing dependencies..."
# PowerShell execution policy might prevent script execution.
# This attempts to run activate.ps1 and then install requirements.
# Users might need to run 'Set-ExecutionPolicy RemoteSigned -Scope Process' or similar if they encounter issues.
try {
    & .\.venv\Scripts\Activate.ps1
    Write-Host "Successfully activated virtual environment in this script's scope."
    Write-Host "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies. Please check requirements.txt and your internet connection."
        # Consider deactivating or cleaning up venv if pip install fails
        exit 1
    }
    Write-Host "Setup complete. Virtual environment '.venv' is ready and dependencies are installed."
    Write-Host "To activate the environment in your PowerShell session, run: .\.venv\Scripts\Activate.ps1"
} catch {
    Write-Error "An error occurred during virtual environment activation or dependency installation."
    Write-Host "You might need to adjust your PowerShell execution policy (e.g., Set-ExecutionPolicy RemoteSigned -Scope Process) or activate the venv manually by running: .\.venv\Scripts\Activate.ps1"
    exit 1
}
