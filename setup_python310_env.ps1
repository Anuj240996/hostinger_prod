# PowerShell script to create a virtual environment with Python 3.10.12
# Run this from your project directory

Write-Host "Setting up Python 3.10.12 virtual environment..." -ForegroundColor Green

# Check if Python 3.10 is available
try {
    $python310 = py -3.10 --version
    Write-Host "Found: $python310" -ForegroundColor Green
    
    # Create virtual environment with Python 3.10
    Write-Host "Creating virtual environment 'venv' with Python 3.10.12..." -ForegroundColor Cyan
    py -3.10 -m venv venv
    
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
    Write-Host "`nTo activate the virtual environment, run:" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "`nThen install requirements:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
    
} catch {
    Write-Host "Error: Python 3.10.12 not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10.12 first from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/release/python-31012/" -ForegroundColor Cyan
}
