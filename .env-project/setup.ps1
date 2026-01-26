# PEOPLE_OS Self-Contained Environment Setup
# This script initializes the environment for the project

param(
    [Switch]$InstallPackages,
    [Switch]$SkipValidation
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PEOPLE_OS Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent -Path $scriptDir
$envDir = $scriptDir

Write-Host "Project Root: $projectRoot" -ForegroundColor Yellow
Write-Host "Environment Dir: $envDir" -ForegroundColor Yellow
Write-Host ""

# Validate environment structure
Write-Host "[1/4] Validating environment structure..." -ForegroundColor Cyan

$pythonBin = Join-Path $envDir "python\bin\python.exe"
$pythonPip = Join-Path $envDir "python\bin\pip.exe"
$nodeModules = Join-Path $envDir "node\node_modules"
$pythonPackages = Join-Path $envDir "python\packages"

$components = @{
    "Python Interpreter" = $pythonBin
    "Python Packages Directory" = $pythonPackages
    "Node Modules" = $nodeModules
}

$allValid = $true
foreach ($component in $components.GetEnumerator()) {
    $path = $component.Value
    if (Test-Path $path) {
        Write-Host "  ✓ $($component.Name): Found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($component.Name): NOT FOUND at $path" -ForegroundColor Red
        $allValid = $false
    }
}

if (-not $allValid) {
    Write-Host ""
    Write-Host "ERROR: Some environment components are missing!" -ForegroundColor Red
    Write-Host "Make sure .env-project folder is complete." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test Python
Write-Host "[2/4] Testing Python environment..." -ForegroundColor Cyan

try {
    $pythonVersion = & $pythonBin --version 2>&1
    Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
    
    # Count installed packages
    $packageCount = (Get-ChildItem $pythonPackages -Filter "*.whl" | Measure-Object).Count
    Write-Host "  ✓ Available packages: $packageCount wheels" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python test failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test Node
Write-Host "[3/4] Testing Node environment..." -ForegroundColor Cyan

try {
    $nodeCount = (Get-ChildItem $nodeModules -Directory | Measure-Object).Count
    Write-Host "  ✓ Node modules: $nodeCount directories" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node test failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Optional: Install packages
if ($InstallPackages) {
    Write-Host "[4/4] Installing Python packages..." -ForegroundColor Cyan
    Write-Host "This may take several minutes..." -ForegroundColor Yellow
    
    try {
        & $pythonPip install --no-index --find-links="$pythonPackages" -q -r "$projectRoot\requirements.txt"
        Write-Host "  ✓ Packages installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Package installation failed: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[4/4] Skipping package installation" -ForegroundColor Yellow
    Write-Host "  Run with -InstallPackages to install all dependencies" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Environment Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Show next steps
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review README.md for usage instructions" -ForegroundColor Gray
Write-Host "  2. Run environment setup scripts:" -ForegroundColor Gray
Write-Host "     - .\setup.ps1 -InstallPackages" -ForegroundColor Cyan
Write-Host "  3. Start development:" -ForegroundColor Gray
Write-Host "     - .\run-backend.ps1" -ForegroundColor Cyan
Write-Host "     - .\run-frontend.ps1" -ForegroundColor Cyan
Write-Host ""

Write-Host "Environment Variables:" -ForegroundColor Yellow
Write-Host "  PYTHON_PATH: $pythonBin" -ForegroundColor Gray
Write-Host "  NODE_MODULES: $nodeModules" -ForegroundColor Gray
Write-Host ""
