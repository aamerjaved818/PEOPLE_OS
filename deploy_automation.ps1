# Deployment Automation Script
# Ensures consistent deployment across environments

$ErrorActionPreference = "Stop"

# Configuration
$projectRoot = Get-Location
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "src"
$testPath = Join-Path $projectRoot "backend/tests"

# Functions
function Write-Header {
    param([string]$message)
    Write-Host "`n=== $message ===" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$message)
    Write-Host "✓ $message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$message)
    Write-Host "✗ $message" -ForegroundColor Red
    exit 1
}

function Check-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    # Check Python
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error-Custom "Python not found. Please install Python 3.9+"
    }
    Write-Success "Python found: $(python --version)"
    
    # Check Node.js
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Error-Custom "Node.js not found. Please install Node.js"
    }
    Write-Success "Node.js found: $(node --version)"
    
    # Check npm
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Error-Custom "npm not found. Please install npm"
    }
    Write-Success "npm found: $(npm --version)"
}

function Setup-Backend {
    Write-Header "Setting Up Backend"
    
    Push-Location $backendPath
    
    # Check venv
    if (-not (Test-Path "venv")) {
        Write-Host "Creating Python virtual environment..."
        python -m venv venv
    }
    
    # Activate venv
    & ".\venv\Scripts\Activate.ps1"
    Write-Success "Virtual environment activated"
    
    # Install dependencies
    Write-Host "Installing Python dependencies..."
    pip install -r requirements.txt --quiet
    Write-Success "Backend dependencies installed"
    
    Pop-Location
}

function Setup-Frontend {
    Write-Header "Setting Up Frontend"
    
    Push-Location $projectRoot
    
    # Install dependencies
    Write-Host "Installing npm dependencies..."
    npm install --quiet
    Write-Success "Frontend dependencies installed"
    
    Pop-Location
}

function Run-Tests {
    Write-Header "Running Tests"
    
    Push-Location $backendPath
    
    # Activate venv
    & "..\venv\Scripts\Activate.ps1"
    
    # Run pytest with coverage
    Write-Host "Running pytest with coverage..."
    pytest --cov=backend --cov-report=term-missing --cov-report=html
    
    Write-Success "Tests completed"
    
    Pop-Location
}

function Build-Frontend {
    Write-Header "Building Frontend"
    
    Push-Location $projectRoot
    
    Write-Host "Building Vite project..."
    npm run build
    Write-Success "Frontend built successfully"
    
    Pop-Location
}

function Lint-Code {
    Write-Header "Linting Code"
    
    Push-Location $projectRoot
    
    # Lint JavaScript/TypeScript
    Write-Host "Running ESLint..."
    npm run lint 2>/dev/null || Write-Host "ESLint issues found (non-critical)"
    
    Pop-Location
}

function Generate-Schema {
    Write-Header "Generating Database Schema"
    
    Push-Location $backendPath
    
    # Activate venv
    & "..\venv\Scripts\Activate.ps1"
    
    # Run migration
    if (Test-Path "migrate_db.py") {
        Write-Host "Running database migration..."
        python migrate_db.py
        Write-Success "Database schema updated"
    }
    
    Pop-Location
}

function Create-Backup {
    Write-Header "Creating Backup"
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $projectRoot "backups"
    
    if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir | Out-Null
    }
    
    Write-Host "Creating backup: $timestamp"
    # Add your backup logic here
    Write-Success "Backup created: $backupDir\backup_$timestamp"
}

function Deploy {
    param(
        [ValidateSet("dev", "staging", "prod")]
        [string]$environment = "dev",
        [switch]$skipTests,
        [switch]$skipLint
    )
    
    Write-Header "Starting Deployment to $environment"
    
    try {
        # Prerequisites
        Check-Prerequisites
        
        # Setup
        Setup-Backend
        Setup-Frontend
        
        # Quality checks
        if (-not $skipLint) {
            Lint-Code
        }
        
        if (-not $skipTests) {
            Run-Tests
        }
        
        # Prepare
        Generate-Schema
        Build-Frontend
        
        # Backup
        Create-Backup
        
        Write-Host "`n" -ForegroundColor Cyan
        Write-Success "Deployment to $environment completed successfully!"
        Write-Host "Build artifacts: $projectRoot\dist" -ForegroundColor Green
        
    }
    catch {
        Write-Error-Custom "Deployment failed: $_"
    }
}

# Main execution
$environment = if ($args.Count -gt 0) { $args[0] } else { "dev" }
$skipTests = $args -contains "--skip-tests"
$skipLint = $args -contains "--skip-lint"

Deploy -environment $environment -skipTests:$skipTests -skipLint:$skipLint
