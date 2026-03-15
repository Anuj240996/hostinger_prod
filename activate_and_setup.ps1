# Script to activate venv and install requirements
# Run this from the project root directory

Write-Host "Activating virtual environment with Python 3.10..." -ForegroundColor Green

# Activate the virtual environment
& ".\venv\Scripts\Activate.ps1"

# Verify Python version
Write-Host "`nPython version in venv:" -ForegroundColor Cyan
python --version

Write-Host "`nPip version:" -ForegroundColor Cyan
pip --version

Write-Host "`nTo install requirements, run:" -ForegroundColor Yellow
Write-Host "  pip install -r DBSolar_19_09_2023\requirements.txt" -ForegroundColor Cyan
Write-Host "`nor for production:" -ForegroundColor Yellow
Write-Host "  pip install -r Requirements_hostinger_prod.txt" -ForegroundColor Cyan
