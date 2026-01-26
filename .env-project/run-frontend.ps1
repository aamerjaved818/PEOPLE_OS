# Start Vite Frontend Development Server using Project Environment
# Usage: .\run-frontend.ps1 [mode]

param(
    [string]$Mode = "dev"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent -Path $scriptDir
$nodeModules = Join-Path $scriptDir "node\node_modules"
$npmBin = Join-Path $nodeModules "\.bin\vite.cmd"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PEOPLE_OS Frontend Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify Node
if (-not (Test-Path $npmBin)) {
    Write-Host "ERROR: Vite not found in node_modules" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
    exit 1
}

Write-Host "Node Modules: $nodeModules" -ForegroundColor Green
Write-Host "Project Root: $projectRoot" -ForegroundColor Green
Write-Host "Mode: $Mode" -ForegroundColor Yellow
Write-Host ""

Write-Host "Starting Vite dev server..." -ForegroundColor Cyan
Write-Host ""

# Set environment
$env:NODE_PATH = $nodeModules
$env:npm_config_node_modules = $nodeModules

# Change to project root and start server
Set-Location $projectRoot

# Run vite directly with Node
$viteBin = Join-Path $nodeModules "vite\bin\vite.js"
& node $viteBin --$Mode
