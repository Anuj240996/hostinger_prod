# Script to install requirements while skipping problematic fasttext package

Write-Host "Installing requirements while skipping fasttext..." -ForegroundColor Cyan
Write-Host ""

# Read requirements file and filter out fasttext
$requirementsFile = "DBSolar_19_09_2023\requirements.txt"
$tempFile = "$env:TEMP\requirements_no_fasttext.txt"

if (Test-Path $requirementsFile) {
    Write-Host "Reading $requirementsFile..." -ForegroundColor Yellow
    $content = Get-Content $requirementsFile | Where-Object { $_ -notmatch "^fasttext" }
    $content | Set-Content $tempFile
    
    Write-Host "Installing packages (fasttext excluded)..." -ForegroundColor Yellow
    pip install -r $tempFile
    
    Write-Host ""
    Write-Host "Note: fasttext was skipped due to compilation issues." -ForegroundColor Yellow
    Write-Host "If you need fasttext, try:" -ForegroundColor Cyan
    Write-Host "  pip install fasttext-windows" -ForegroundColor White
    Write-Host "  OR" -ForegroundColor Yellow
    Write-Host "  pip install fasttext --no-build-isolation" -ForegroundColor White
    
    Remove-Item $tempFile -ErrorAction SilentlyContinue
} else {
    Write-Host "Requirements file not found: $requirementsFile" -ForegroundColor Red
}
