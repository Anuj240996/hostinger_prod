# PowerShell script to download and install Python 3.10.12 on Windows
# Run this script as Administrator

Write-Host "Downloading Python 3.10.12..." -ForegroundColor Green

$pythonUrl = "https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe"
$installerPath = "$env:TEMP\python-3.10.12-amd64.exe"

# Download Python installer
Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath

Write-Host "Installing Python 3.10.12..." -ForegroundColor Green
Write-Host "Please check 'Add Python 3.10 to PATH' in the installer window!" -ForegroundColor Yellow

# Run installer with silent install options
# /quiet = silent install
# PrependPath = add to PATH
# InstallAllUsers = install for all users
Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Please restart your terminal/PowerShell to use Python 3.10.12" -ForegroundColor Yellow

# Clean up
Remove-Item $installerPath -ErrorAction SilentlyContinue

# Verify installation
Write-Host "`nChecking installed Python versions:" -ForegroundColor Cyan
Get-Command python* | Select-Object Name, Source
