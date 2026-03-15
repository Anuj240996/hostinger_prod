# Script to fix urllib3 dependency conflict
# The issue: botocore 1.16.26 requires urllib3<1.26, but requests 2.32.5 needs urllib3>=1.21.1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fixing urllib3 Dependency Conflict" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$requirementsFile = "DBSolar_19_09_2023\requirements_11_01_2026_latest.txt"
$backupFile = "$requirementsFile.backup"

# Create backup
Write-Host "Creating backup of requirements file..." -ForegroundColor Yellow
Copy-Item $requirementsFile $backupFile
Write-Host "Backup created: $backupFile" -ForegroundColor Green
Write-Host ""

# Read the file
$content = Get-Content $requirementsFile

# Solution 1: Update botocore to a newer version that supports urllib3 >= 1.26
Write-Host "Updating botocore to a newer version..." -ForegroundColor Yellow
$content = $content | ForEach-Object {
    if ($_ -match "^botocore==") {
        "botocore>=1.28.0"  # Newer version supports urllib3 >= 1.26
    } else {
        $_
    }
}

# Solution 2: Also update boto3 to match
Write-Host "Updating boto3 to match..." -ForegroundColor Yellow
$content = $content | ForEach-Object {
    if ($_ -match "^boto3==") {
        "boto3>=1.28.0"  # Match botocore version
    } else {
        $_
    }
}

# Solution 3: Add explicit urllib3 constraint that satisfies both
Write-Host "Adding urllib3 constraint..." -ForegroundColor Yellow
# Check if urllib3 is already in the file
$hasUrllib3 = $content | Select-String -Pattern "^urllib3"
if (-not $hasUrllib3) {
    # Add urllib3 constraint after requests line
    $newContent = @()
    foreach ($line in $content) {
        $newContent += $line
        if ($line -match "^requests==") {
            $newContent += "urllib3>=1.26.0,<2.0"  # Compatible with both
        }
    }
    $content = $newContent
} else {
    # Update existing urllib3 constraint
    $content = $content | ForEach-Object {
        if ($_ -match "^urllib3") {
            "urllib3>=1.26.0,<2.0"
        } else {
            $_
        }
    }
}

# Write the updated content
$content | Set-Content $requirementsFile

Write-Host ""
Write-Host "Changes made:" -ForegroundColor Green
Write-Host "  1. Updated botocore to >=1.28.0 (supports urllib3 >= 1.26)" -ForegroundColor Cyan
Write-Host "  2. Updated boto3 to >=1.28.0" -ForegroundColor Cyan
Write-Host "  3. Added/updated urllib3 constraint: >=1.26.0,<2.0" -ForegroundColor Cyan
Write-Host ""
Write-Host "Now try installing again:" -ForegroundColor Yellow
Write-Host "  pip install -r $requirementsFile" -ForegroundColor White
Write-Host ""
Write-Host "If issues persist, you can restore the backup:" -ForegroundColor Yellow
Write-Host "  Copy-Item $backupFile $requirementsFile" -ForegroundColor White
