# Start Complete PEOPLE_OS Stack (Backend + Frontend)
# Usage: .\run-all.ps1 [options]

param(
    [Switch]$NoFrontend,
    [Switch]$NoBackend
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PEOPLE_OS Complete Stack" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($NoBackend -and $NoFrontend) {
    Write-Host "ERROR: At least one component must be enabled" -ForegroundColor Red
    exit 1
}

# Store current directory
$originalDir = Get-Location

# Start backend in background if enabled
if (-not $NoBackend) {
    Write-Host "Starting Backend..." -ForegroundColor Yellow
    $backendScript = Join-Path $scriptDir "run-backend.ps1"
    
    if (Test-Path $backendScript) {
        Start-Process pwsh -ArgumentList "-NoExit", "-File", $backendScript
        Write-Host "  ✓ Backend started in new window" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Backend script not found" -ForegroundColor Red
    }
}

Write-Host ""

# Start frontend if enabled
if (-not $NoFrontend) {
    Write-Host "Starting Frontend..." -ForegroundColor Yellow
    $frontendScript = Join-Path $scriptDir "run-frontend.ps1"
    
    if (Test-Path $frontendScript) {
        Start-Process pwsh -ArgumentList "-NoExit", "-File", $frontendScript
        Write-Host "  ✓ Frontend started in new window" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Frontend script not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Services Starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Check the new terminal windows for logs:" -ForegroundColor Yellow
if (-not $NoBackend) {
    Write-Host "  • Backend: http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "    API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Gray
}
if (-not $NoFrontend) {
    Write-Host "  • Frontend: http://localhost:5173" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Press Ctrl+C in each window to stop services" -ForegroundColor Yellow
Write-Host ""

# Return to original directory
Set-Location $originalDir
