# PEOPLE_OS Environment Scripts Reference

Complete reference for all PowerShell scripts in the `.env-project` folder.

---

## 🚀 Quick Command Reference

```powershell
# Initial setup (one-time)
.\setup.ps1 -InstallPackages

# Start backend
.\run-backend.ps1 -Reload

# Start frontend
.\run-frontend.ps1

# Start everything
.\run-all.ps1

# Load environment variables
. .\env.ps1
```

---

## 📜 Script Details

### 1. setup.ps1 - Environment Setup & Validation

**Purpose:** Initialize and validate the environment

**Usage:**

```powershell
.\setup.ps1                    # Validate only
.\setup.ps1 -InstallPackages   # Validate and install packages
```

**Parameters:**

- `-InstallPackages` - Install all Python packages from wheels
- `-SkipValidation` - Skip validation checks (not recommended)

**What it does:**

1. Validates Python installation
2. Validates Python packages directory
3. Validates Node modules
4. (Optional) Installs Python packages
5. Shows summary and next steps

**Expected output:**

```
[1/4] Validating environment structure...
  ✓ Python Interpreter: Found
  ✓ Python Packages Directory: Found
  ✓ Node Modules: Found

[2/4] Testing Python environment...
  ✓ Python: Python 3.12.10
  ✓ Available packages: 119 wheels

[3/4] Testing Node environment...
  ✓ Node modules: 816 directories

[4/4] Skipping package installation
  Run with -InstallPackages to install all dependencies

Setup Complete!
```

**When to use:**

- First time setup
- After copying environment to new location
- To verify integrity
- Before deployment

---

### 2. run-backend.ps1 - Start FastAPI Backend

**Purpose:** Launch the backend API server

**Usage:**

```powershell
.\run-backend.ps1                    # Default settings
.\run-backend.ps1 -Reload            # Development mode
.\run-backend.ps1 -Port 8001         # Custom port
.\run-backend.ps1 -Host 0.0.0.0      # Listen on all interfaces
.\run-backend.ps1 -Workers           # Production mode
```

**Parameters:**

- `-Host` (default: 127.0.0.1) - Server host/IP
- `-Port` (default: 8000) - Server port
- `-Reload` - Enable auto-reload on code changes
- `-Workers` - Run with 4 worker processes

**Environment Variables:**

- `PYTHON_PATH` - Set to project Python
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `SECRET_KEY` - API secret key

**Expected output:**

```
Python: C:\Path\To\.env-project\python\bin\python.exe
Project Root: C:\Path\To\PEOPLE_OS
Server: http://127.0.0.1:8000
Mode: Development (with reload)

Starting server...
INFO:     Started server process [1234]
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Access:**

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**When to use:**

- Development (`-Reload`)
- Testing
- Production deployment (`-Workers`)
- Custom port/host setup

---

### 3. run-frontend.ps1 - Start Vite Dev Server

**Purpose:** Launch the frontend development server

**Usage:**

```powershell
.\run-frontend.ps1                  # Development mode
.\run-frontend.ps1 -Mode dev        # Explicit dev mode
.\run-frontend.ps1 -Mode preview    # Production preview
```

**Parameters:**

- `-Mode` (default: dev) - Server mode (dev/preview)

**Expected output:**

```
Node Modules: C:\Path\To\.env-project\node\node_modules
Project Root: C:\Path\To\PEOPLE_OS
Mode: dev

Starting Vite dev server...

  ➜  local:   http://localhost:5173/
  ➜  press h to show help
```

**Features:**

- Hot Module Replacement (HMR)
- Instant updates on file changes
- Built-in TypeScript support
- CSS/Tailwind processing
- Vite plugins enabled

**Access:**

- App: `http://localhost:5173`
- Check console for HMR status

**When to use:**

- During development
- Testing UI changes
- Debugging frontend issues
- Production preview

---

### 4. run-all.ps1 - Start Complete Stack

**Purpose:** Launch both backend and frontend servers

**Usage:**

```powershell
.\run-all.ps1                       # Start both
.\run-all.ps1 -NoBackend            # Frontend only
.\run-all.ps1 -NoFrontend           # Backend only
```

**Parameters:**

- `-NoBackend` - Skip backend
- `-NoFrontend` - Skip frontend

**What it does:**

1. Opens new terminal for backend
2. Opens new terminal for frontend
3. Shows access URLs
4. Returns control to current terminal

**Expected output:**

```
Starting Backend...
  ✓ Backend started in new window

Starting Frontend...
  ✓ Frontend started in new window

========================================
Services Starting...
========================================

Check the new terminal windows for logs:
  • Backend: http://127.0.0.1:8000
    API Docs: http://127.0.0.1:8000/docs
  • Frontend: http://localhost:5173

Press Ctrl+C in each window to stop services
```

**When to use:**

- Start complete development environment
- CI/CD testing
- Deployment validation
- Automated testing setup

---

### 5. env.ps1 - Environment Configuration

**Purpose:** Configure environment variables and PATH

**Usage:**

```powershell
# Load environment configuration
. .\env.ps1

# Now these work:
python --version
pip install package
npm list
npx command
```

**What it sets:**

- `PATH` - Includes Python and Node executables
- `NODE_PATH` - Node module resolution
- `PIP_NO_INDEX` - Use local packages only
- `PIP_FIND_LINKS` - Local package directory
- `PYTHONPATH` - Project path

**Variables set:**

- `$pythonBin` - Python executable directory
- `$pythonExe` - Python executable path
- `$pipExe` - Pip executable path
- `$nodeModulesBin` - npm executables
- `$nodePath` - node_modules directory

**When to use:**

- Interactive development
- Manual command execution
- Debugging environment setup
- Custom scripts

---

## 🔄 Script Execution Flow

```
User Action → Script Execution → Environment Check →
Process Start → Output Display → Return Control
```

### Typical Development Session

```powershell
# 1. Navigate to environment
cd .\.env-project

# 2. Setup (first time only)
.\setup.ps1 -InstallPackages

# 3. Start everything
.\run-all.ps1

# 4. Work in main terminal while services run in background

# 5. Stop services (Ctrl+C in each window)

# 6. Later sessions, just start services
.\run-all.ps1
```

---

## 🛠️ Custom Script Usage

### Create custom backend startup

```powershell
# Save as custom-backend.ps1
$envDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonBin = Join-Path $envDir "python\bin\python.exe"

& $pythonBin -m uvicorn backend.main:app `
  --host 0.0.0.0 `
  --port 8000 `
  --reload `
  --log-level info
```

### Create custom Node task

```powershell
# Save as custom-build.ps1
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir
$nodeModules = Join-Path $scriptDir "node\node_modules"

$env:NODE_PATH = $nodeModules
Set-Location $projectRoot

& node "$nodeModules\vite\bin\vite.js" build
```

---

## 🐛 Debugging Scripts

### Enable verbose output

```powershell
# Set debug preference
$DebugPreference = "Continue"

# Run script
.\setup.ps1 -Verbose -InstallPackages
```

### Check what script does

```powershell
# Show what commands would run without executing
.\setup.ps1 -WhatIf
```

### Get script info

```powershell
# Show all parameters
Get-Help .\setup.ps1 -Full

# Show examples
Get-Help .\run-backend.ps1 -Examples
```

---

## ⚙️ Script Customization

### Modify default parameters

Edit the script and change default values:

```powershell
# In run-backend.ps1
param(
    [string]$Host = "0.0.0.0",     # Changed from 127.0.0.1
    [int]$Port = 3000,              # Changed from 8000
    [Switch]$Reload = $true,        # Auto-reload by default
    [Switch]$Workers
)
```

### Add pre-flight checks

Add to any script:

```powershell
# Check database connectivity
$testConnection = & $pythonBin -c "import psycopg2; psycopg2.connect(os.environ['DATABASE_URL'])"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Cannot connect to database" -ForegroundColor Red
    exit 1
}
```

---

## 📊 Script Execution Log

Scripts can write logs:

```powershell
# In run-backend.ps1
$logFile = ".\logs\backend-$(Get-Date -Format 'yyyy-MM-dd').log"

& $pythonBin @cmd 2>&1 | Tee-Object -FilePath $logFile
```

---

## 🚨 Error Handling

All scripts include error handling:

```powershell
$ErrorActionPreference = "Stop"  # Stop on first error

try {
    # Script logic
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}
```

---

## 📝 Script Maintenance

### Update script

1. Edit the `.ps1` file
2. Test changes
3. Commit to version control

### Version control

Add to `.gitignore`:

```
.env
logs/
*.log
node_modules/
.venv/
__pycache__/
```

Don't ignore:

```
setup.ps1
run-*.ps1
env.ps1
```

---

## 🎯 Next Steps

1. **First Time:**

   ```powershell
   .\setup.ps1 -InstallPackages
   ```

2. **Development:**

   ```powershell
   .\run-all.ps1
   ```

3. **Deployment:**
   ```powershell
   .\setup.ps1 -InstallPackages
   .\run-backend.ps1 -Workers
   .\run-frontend.ps1 -Mode preview
   ```

---

**Script Version:** 1.0  
**Created:** 2026-01-23  
**Tested on:** PowerShell 5.1+  
**OS:** Windows 10/11

_All scripts are self-contained and require no external dependencies beyond Python 3.12.10 and Node.js packages included in the environment._
