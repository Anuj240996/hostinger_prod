# Script to install problematic packages with proper commands

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing Problematic Packages" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Note: Use 'pip install' before package names!
Write-Host "IMPORTANT: Always use 'pip install' before package names!" -ForegroundColor Yellow
Write-Host "Example: pip install gevent==21.12.0" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install packages that should work
Write-Host "Step 1: Installing packages that should work..." -ForegroundColor Yellow

Write-Host "`nInstalling gevent==21.12.0..." -ForegroundColor Cyan
pip install gevent==21.12.0

Write-Host "`nInstalling llvmlite==0.39.0..." -ForegroundColor Cyan
pip install llvmlite==0.39.0

Write-Host "`nInstalling numba==0.55.1..." -ForegroundColor Cyan
pip install numba==0.55.1

Write-Host ""

# Step 2: Handle Fiona (requires GDAL)
Write-Host "Step 2: Installing Fiona (requires GDAL)..." -ForegroundColor Yellow
Write-Host "Fiona requires GDAL. Options:" -ForegroundColor Cyan
Write-Host "1. Install GDAL first (complex on Windows)" -ForegroundColor White
Write-Host "2. Use conda (if available): conda install -c conda-forge fiona" -ForegroundColor White
Write-Host "3. Skip Fiona if not needed" -ForegroundColor White
Write-Host ""

# Try installing Fiona with pre-built wheel
Write-Host "Attempting to install Fiona..." -ForegroundColor Cyan
pip install Fiona==1.8.21 --no-cache-dir

if ($LASTEXITCODE -ne 0) {
    Write-Host "Fiona installation failed. GDAL is required." -ForegroundColor Red
    Write-Host "`nTo install GDAL on Windows:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal" -ForegroundColor Cyan
    Write-Host "2. Or use: pip install GDAL" -ForegroundColor Cyan
    Write-Host "3. Or skip if not needed for your Django project" -ForegroundColor Cyan
}

Write-Host ""

# Step 3: Handle netCDF4
Write-Host "Step 3: Installing netCDF4==1.5.8..." -ForegroundColor Yellow
pip install netCDF4==1.5.8 --no-cache-dir

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
