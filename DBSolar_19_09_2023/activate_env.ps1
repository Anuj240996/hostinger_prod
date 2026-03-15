# Quick script to activate the virtual environment
# Run this from the DBSolar_19_09_2023 directory

Write-Host "Activating virtual environment..." -ForegroundColor Green

# Navigate to the project directory
Set-Location "E:\Production Project Backup\Hostinger Project\DBSolar_19_09_2023\DBSolar_19_09_2023"

# Activate the virtual environment
& ".\env\Scripts\Activate.ps1"

# Verify activation
Write-Host "`nVirtual environment activated!" -ForegroundColor Cyan
Write-Host "Python version:" -ForegroundColor Yellow
python --version

Write-Host "`nCurrent directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host "`nTo run the Django server, use:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor Green
