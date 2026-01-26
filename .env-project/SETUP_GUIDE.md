# Self-Contained Environment - Installation & Setup Guide

## 📋 Overview

The PEOPLE_OS project now includes a complete self-contained environment (`.env-project`) with:

- Python 3.12.10 interpreter
- 87 Python packages (pre-downloaded wheels)
- 816 Node.js packages (pre-installed)
- Utility scripts for easy startup

**Total Size:** ~2.4 GB  
**No external dependencies required**

---

## 🚀 Quick Start (5 Minutes)

### 1. First Time Setup

Open PowerShell in the `.env-project` folder and run:

```powershell
.\setup.ps1 -InstallPackages
```

This will:

- ✓ Validate Python installation
- ✓ Verify Node modules
- ✓ Install all Python packages from local wheels
- ✓ Show configuration summary

**Expected output:**

```
========================================
Environment Setup Complete!
========================================
✓ Python: Python 3.12.10
✓ Available packages: 87 wheels
✓ Node modules: 816 directories
✓ Packages installed successfully
```

### 2. Start Backend

From `.env-project` folder:

```powershell
.\run-backend.ps1 -Reload
```

Expected output:

```
Starting server...
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

Visit: `http://localhost:8000/docs` for API documentation

### 3. Start Frontend (New Terminal)

From `.env-project` folder:

```powershell
.\run-frontend.ps1
```

Expected output:

```
  ➜  local:   http://localhost:5173/
```

Visit: `http://localhost:5173` in your browser

### 4. Or Start Both Together

```powershell
.\run-all.ps1
```

This opens two terminal windows:

- One for backend (FastAPI)
- One for frontend (Vite)

---

## 📁 What's Included

### Python Environment

```
.env-project\python\
├── bin\              # Python executable & tools
├── Lib\              # Standard library
├── packages\         # All pip packages (wheels)
└── Scripts\          # Helper scripts
```

**Python Packages by Category:**

- **Framework:** FastAPI, Uvicorn, Starlette
- **Database:** SQLAlchemy, Alembic, PostgreSQL driver
- **Async:** Celery, Redis, APScheduler
- **Security:** bcrypt, JWT, passlib
- **Testing:** pytest, pytest-asyncio, pytest-cov
- **Data:** pandas, numpy, openpyxl, fpdf2
- **Development:** black, flake8, mypy
- **And 50+ more...**

### Node Environment

```
.env-project\node\
└── node_modules\    # All npm packages (816 total)
```

**Node Packages by Category:**

- **Framework:** React 19.2, React Router, Zustand
- **UI:** Radix UI, TailwindCSS, Lucide icons
- **Build:** Vite, TypeScript, esbuild
- **Testing:** Vitest, Playwright, Testing Library
- **Development:** ESLint, Prettier, Husky
- **And 800+ more...**

---

## 🔧 Available Scripts

### Setup & Configuration

```powershell
.\setup.ps1                    # Validate & optionally install packages
.\setup.ps1 -InstallPackages   # Install all Python packages
.\env.ps1                      # Configure PATH & environment variables
```

### Running Services

```powershell
.\run-backend.ps1              # Start FastAPI backend
.\run-backend.ps1 -Reload      # Start with auto-reload (dev mode)
.\run-backend.ps1 -Workers     # Start with multiple workers (prod mode)

.\run-frontend.ps1             # Start Vite dev server
.\run-frontend.ps1 -Mode prod  # Start production build

.\run-all.ps1                  # Start both backend and frontend
.\run-all.ps1 -NoBackend       # Frontend only
.\run-all.ps1 -NoFrontend      # Backend only
```

---

## 💻 Manual Usage

### Use Python from Environment

```powershell
# Check Python version
.\.env-project\python\bin\python --version

# Run Python script
.\.env-project\python\bin\python script.py

# Run pytest
.\.env-project\python\bin\python -m pytest

# Use pip
.\.env-project\python\bin\pip list
.\.env-project\python\bin\pip show fastapi
```

### Use Node from Environment

```powershell
# Check Node/npm version
.\.env-project\node\node_modules\.bin\node --version

# Run npm commands
.\.env-project\node\node_modules\.bin\npm list react

# Run specific tool
.\.env-project\node\node_modules\.bin\eslint --version
```

### Source Environment Configuration

In PowerShell:

```powershell
# Configure PATH with project Python & Node
. .\.env-project\env.ps1

# Now you can use python, pip, npm, npx directly
python --version
npm list
```

---

## 📚 Project Structure

After setup, your project structure is:

```
PEOPLE_OS/
├── .env-project/               # ← SELF-CONTAINED ENVIRONMENT
│   ├── python/                 # Python 3.12 + 87 packages
│   ├── node/                   # Node modules (816 packages)
│   ├── docs/                   # Documentation
│   ├── setup.ps1              # Setup script
│   ├── run-*.ps1              # Run scripts
│   ├── README.md              # Documentation
│   └── INVENTORY.md           # Complete inventory
│
├── backend/                    # Backend code
├── src/                        # Frontend code
├── package.json               # Frontend dependencies
├── requirements.txt           # Backend dependencies
├── .env                       # Environment variables (create this)
└── ... (other project files)
```

---

## 🌍 Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/people_os

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_PORT=8000
API_HOST=0.0.0.0

# Frontend
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=PEOPLE_OS

# Logging
LOG_LEVEL=INFO
```

---

## 🔍 Troubleshooting

### Issue: "Python not found"

**Solution:** Ensure you're using the correct path:

```powershell
# Correct
.\.env-project\python\bin\python

# Wrong - don't use system Python
python  # Uses system Python, not project Python
```

### Issue: "Module not found"

**Solution:** Install packages using the project pip:

```powershell
# Correct - uses local packages
.\.env-project\python\bin\pip install --no-index -f .\.env-project\python\packages -r requirements.txt

# Or use the setup script
.\setup.ps1 -InstallPackages
```

### Issue: "npm ERR! code ENOENT"

**Solution:** Ensure NODE_PATH is set:

```powershell
# Load environment configuration
. .\.env-project\env.ps1

# Now npm should work
npm install
```

### Issue: Port 8000 already in use

**Solution:** Use a different port:

```powershell
.\run-backend.ps1 -Port 8001
```

### Issue: Vite not found

**Solution:** Ensure node_modules are present:

```powershell
# Check
Test-Path .\.env-project\node\node_modules\vite

# If missing, copy from main project
Copy-Item .\node_modules -Destination .\.env-project\node\node_modules -Recurse
```

---

## 📊 Verifying Setup

### Check Python

```powershell
# Should show Python 3.12.10
.\.env-project\python\bin\python --version

# Should list 87+ packages
.\.env-project\python\bin\pip list | Measure-Object

# Should import successfully
.\.env-project\python\bin\python -c "import fastapi; print(fastapi.__version__)"
```

### Check Node

```powershell
# Should show directory exists
Test-Path .\.env-project\node\node_modules\react

# Should list packages
Get-ChildItem .\.env-project\node\node_modules | Measure-Object
```

---

## 🚀 Deployment to Production

### Package for Deployment

```powershell
# Compress entire environment
Compress-Archive -Path .\.env-project -DestinationPath people-os-env.zip

# Copy to server
scp people-os-env.zip user@server:/deploy/
```

### Deploy on Target

```bash
# Extract on server
unzip people-os-env.zip

# Setup
cd .env-project
./setup.ps1 -InstallPackages

# Run
./run-all.ps1
```

**No system dependencies required on target server!**

---

## 🔐 Security Notes

1. **Keep .env file secrets:** Add to .gitignore
2. **Verify package integrity:** Check INVENTORY.md
3. **Update periodically:** Re-download packages for security patches
4. **Use signed commits:** Verify project authenticity

---

## 📞 Support Resources

- **Backend Issues:** Check `backend/README.md`
- **Frontend Issues:** Check `src/` documentation
- **Package Details:** See `INVENTORY.md`
- **Database:** See `backend/schema.sql`

---

## ✅ Setup Checklist

- [ ] Extract `.env-project` folder
- [ ] Run `.\setup.ps1 -InstallPackages`
- [ ] Create `.env` file with config
- [ ] Start backend: `.\run-backend.ps1 -Reload`
- [ ] Start frontend: `.\run-frontend.ps1`
- [ ] Visit `http://localhost:5173`
- [ ] Check API docs at `http://localhost:8000/docs`

---

## 🎉 You're Ready!

Your PEOPLE_OS environment is now fully self-contained and ready to run anywhere!

**Next Steps:**

1. Follow project documentation in `backend/README.md`
2. Check database setup in `backend/schema.sql`
3. Review API documentation at `/docs` endpoint
4. Start developing!

---

**Last Updated:** 2026-01-23  
**Python:** 3.12.10  
**Packages:** 903 (87 Python + 816 Node)  
**Environment Status:** ✅ READY TO USE
