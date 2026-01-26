# Start FastAPI Backend using Project Environment
# Usage: .\run-backend.ps1 [options]

param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [Switch]$Reload,
    [Switch]$Workers
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent -Path $scriptDir
$pythonBin = Join-Path $scriptDir "python\bin\python.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PEOPLE_OS Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify Python
if (-not (Test-Path $pythonBin)) {
    Write-Host "ERROR: Python not found at $pythonBin" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
    exit 1
}

Write-Host "Python: $pythonBin" -ForegroundColor Green
Write-Host "Project Root: $projectRoot" -ForegroundColor Green
Write-Host "Server: http://$Host`:$Port" -ForegroundColor Green
Write-Host ""

# Build command
$cmd = @(
    "-m", "uvicorn",
    "backend.main:app",
    "--host", $Host,
    "--port", $Port
)

if ($Reload) {
    $cmd += "--reload"
    Write-Host "Mode: Development (with reload)" -ForegroundColor Yellow
} else {
    Write-Host "Mode: Production (no reload)" -ForegroundColor Yellow
}

if ($Workers) {
    $cmd += "--workers", "4"
    Write-Host "Workers: 4" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Cyan
Write-Host ""

# Change to project root and start server
Set-Location $projectRoot
& $pythonBin @cmd
