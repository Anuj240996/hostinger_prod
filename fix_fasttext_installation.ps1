# Script to fix fasttext installation issue on Windows
# The problem: fasttext==0.9.2 doesn't compile well on Windows with MSVC

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fixing fasttext Installation Issue" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install wheel first (allows using pre-built wheels)
Write-Host "Step 1: Installing wheel package..." -ForegroundColor Yellow
pip install wheel

Write-Host ""

# Step 2: Try installing fasttext with pre-built wheel
Write-Host "Step 2: Attempting to install fasttext..." -ForegroundColor Yellow
Write-Host "Trying pre-built wheel first..." -ForegroundColor Cyan

# Try installing fasttext without version pin to get a newer version that might have wheels
pip install fasttext --no-cache-dir

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Pre-built wheel not available. Trying alternative solutions..." -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "Option 1: Install fasttext-windows (Windows-compatible fork)" -ForegroundColor Cyan
    Write-Host "  pip install fasttext-windows" -ForegroundColor White
    
    Write-Host ""
    Write-Host "Option 2: Skip fasttext if not critical" -ForegroundColor Cyan
    Write-Host "  Create a requirements file without fasttext" -ForegroundColor White
    
    Write-Host ""
    Write-Host "Option 3: Use conda (if available)" -ForegroundColor Cyan
    Write-Host "  conda install -c conda-forge fasttext" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
