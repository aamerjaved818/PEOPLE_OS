# 🎯 PEOPLE_OS Environment - Quick Navigation

Welcome! This is your self-contained project environment. Start here.

---

## 📍 You Are Here

```
PEOPLE_OS/
└── .env-project/     ← YOU ARE HERE
    ├── python/       (Python 3.12.10 + 119 packages)
    ├── node/         (816 npm packages)
    └── [files below]
```

---

## 📚 Choose Your Path

### 🚀 **First Time Setup**

→ Read: [SETUP_GUIDE.md](SETUP_GUIDE.md)

**Quick start:**

```powershell
.\setup.ps1 -InstallPackages
.\run-all.ps1
```

### 📖 **Want Documentation?**

- [README.md](README.md) - Overview & features
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Step-by-step setup
- [INVENTORY.md](INVENTORY.md) - All packages & versions
- [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) - Script documentation
- [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - Summary & status

### 🔧 **Start Development**

```powershell
# Start all services
.\run-all.ps1

# Or individually:
.\run-backend.ps1 -Reload    # Terminal 1
.\run-frontend.ps1            # Terminal 2
```

### 🛠️ **Manual Setup**

```powershell
# Validate environment
.\setup.ps1

# Install packages
.\setup.ps1 -InstallPackages

# Configure environment
. .\env.ps1

# Use Python directly
python --version
pip list

# Use Node directly
npm list
```

---

## 🎯 Common Tasks

### Start Backend API

```powershell
.\run-backend.ps1 -Reload
# Access: http://localhost:8000/docs
```

### Start Frontend

```powershell
.\run-frontend.ps1
# Access: http://localhost:5173
```

### Run Tests

```powershell
# Python tests
.\python\bin\python -m pytest

# Frontend tests
npm test
```

### Install New Package

```powershell
# Python (from local wheels first)
.\python\bin\pip install --no-index -f .\python\packages package-name

# Node
npm install package-name
```

### Check Python Version

```powershell
.\python\bin\python --version
# Output: Python 3.12.10
```

### Check Node Version

```powershell
.\node\node_modules\.bin\node --version
```

---

## 📋 Available Scripts

| Script           | Purpose          | Command                        |
| ---------------- | ---------------- | ------------------------------ |
| setup.ps1        | Validate & setup | `.\setup.ps1 -InstallPackages` |
| run-backend.ps1  | Start FastAPI    | `.\run-backend.ps1 -Reload`    |
| run-frontend.ps1 | Start Vite       | `.\run-frontend.ps1`           |
| run-all.ps1      | Start both       | `.\run-all.ps1`                |
| env.ps1          | Configure PATH   | `. .\env.ps1`                  |

[Full documentation →](SCRIPTS_REFERENCE.md)

---

## 📦 What's Installed

**Python Packages (119 wheels):**

- Web: FastAPI, Uvicorn, Pydantic
- Database: SQLAlchemy, PostgreSQL
- Testing: pytest, pytest-asyncio
- Development: black, flake8, mypy
- Data: pandas, numpy, openpyxl
- And 90+ more...

[Complete list →](INVENTORY.md)

**Node Packages (816 modules):**

- React 19.2, React Router
- Vite, TypeScript
- TailwindCSS, Radix UI
- Vitest, Playwright
- ESLint, Prettier
- And 800+ more...

[Complete list →](INVENTORY.md)

---

## 🌍 Access Points

Once running:

| Service     | URL                         | Purpose        |
| ----------- | --------------------------- | -------------- |
| Frontend    | http://localhost:5173       | React app      |
| Backend API | http://localhost:8000       | FastAPI server |
| API Docs    | http://localhost:8000/docs  | Swagger UI     |
| API Schema  | http://localhost:8000/redoc | ReDoc UI       |

---

## ⚙️ Environment Details

- **Python:** 3.12.10
- **Node:** Included in node_modules
- **npm:** Included in node_modules
- **Size:** ~2.4 GB
- **Files:** 53,210
- **Status:** ✅ Ready to use

---

## ❓ Troubleshooting

**Python not found?**

```powershell
.\python\bin\python --version
# Use full path, not just "python"
```

**Module errors?**

```powershell
.\setup.ps1 -InstallPackages
# Install from local packages
```

**Port in use?**

```powershell
.\run-backend.ps1 -Port 8001
# Use different port
```

[More help →](SETUP_GUIDE.md#-troubleshooting)

---

## 🚀 Next Steps

### Today

- [ ] Read [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [ ] Run `.\setup.ps1 -InstallPackages`
- [ ] Start with `.\run-all.ps1`

### Development

- [ ] Check API at http://localhost:8000/docs
- [ ] View frontend at http://localhost:5173
- [ ] Create `.env` file in project root
- [ ] Start coding!

### Production

- [ ] Review [SETUP_GUIDE.md#-deployment-to-production](SETUP_GUIDE.md)
- [ ] Copy `.env-project` to server
- [ ] Run setup on target machine
- [ ] Deploy with `.\run-all.ps1`

---

## 📖 Documentation Map

```
START HERE
    ↓
README.md (Overview)
    ↓
SETUP_GUIDE.md (Instructions)
    ├─→ SCRIPTS_REFERENCE.md (Script details)
    ├─→ INVENTORY.md (Packages)
    └─→ SETUP_COMPLETE.md (Summary)
```

---

## 💡 Pro Tips

✨ **Faster startup:**

```powershell
# Load environment once, reuse in terminal
. .\env.ps1
python --version      # Works directly now
pip list              # Works directly
npm list              # Works directly
```

✨ **Development workflow:**

```powershell
# Terminal 1: Backend
.\run-backend.ps1 -Reload

# Terminal 2: Frontend
.\run-frontend.ps1

# Terminal 3: Other work
python manage.py...
npm test
```

✨ **Deployment ready:**

```powershell
# Copy entire folder
Copy-Item .env-project D:\Deployment

# Run on target
D:\Deployment\.env-project\setup.ps1 -InstallPackages
D:\Deployment\.env-project\run-all.ps1
```

---

## 🔒 Security

1. **Keep secrets secure:**
   - Add `.env` to `.gitignore`
   - Never commit database passwords
   - Use environment variables

2. **Verify before deployment:**
   - Check `.env` is configured
   - Validate database connection
   - Test with `pytest`

3. **Keep updated:**
   - Monitor security advisories
   - Update packages periodically
   - Review dependencies

---

## 📞 Quick Reference

### Commands

```powershell
# Setup
.\setup.ps1 -InstallPackages

# Start services
.\run-all.ps1

# Check Python
.\python\bin\python --version

# Check npm packages
.\node\node_modules\.bin\npm list

# Run backend only
.\run-backend.ps1 -Reload

# Run frontend only
.\run-frontend.ps1
```

### Paths

```
Python:     .\python\bin\python.exe
Pip:        .\python\bin\pip.exe
Packages:   .\python\packages\
Node:       .\node\node_modules\
```

### URLs

```
Frontend:   http://localhost:5173
Backend:    http://localhost:8000
API Docs:   http://localhost:8000/docs
ReDoc:      http://localhost:8000/redoc
```

---

## ✅ Checklist

- [ ] Read this file (INDEX.md)
- [ ] Read SETUP_GUIDE.md
- [ ] Run .\setup.ps1 -InstallPackages
- [ ] Start services with .\run-all.ps1
- [ ] Access http://localhost:5173
- [ ] Check http://localhost:8000/docs
- [ ] Create .env file
- [ ] Start developing!

---

## 🎉 Ready to Go!

Everything is set up and ready to use. Just:

```powershell
cd .env-project
.\setup.ps1 -InstallPackages
.\run-all.ps1
```

Then visit:

- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:8000/docs

Happy coding! 🚀

---

**Last Updated:** January 23, 2026  
**Environment:** ✅ Ready  
**Size:** ~2.4 GB  
**Packages:** 935 total (119 Python + 816 Node)

[More help?](SETUP_GUIDE.md) | [All packages?](INVENTORY.md) | [Scripts?](SCRIPTS_REFERENCE.md)
