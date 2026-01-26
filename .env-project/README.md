# PEOPLE_OS - Self-Contained Environment

This folder contains a complete, self-contained environment for the PEOPLE_OS project with all dependencies included.

## Environment Structure

```
.env-project/
├── python/
│   ├── bin/              # Python 3.12 interpreter and executables
│   ├── packages/         # All Python packages (wheels)
│   └── lib/              # Python standard library
├── node/
│   └── node_modules/     # All npm packages
└── docs/                 # Documentation
```

## Contents

### Python Environment

- **Python 3.12.10** - Complete Python interpreter
- **All Backend Dependencies**:
  - FastAPI 0.104.1
  - SQLAlchemy 2.0+
  - Celery 5.3+
  - Redis
  - Pydantic
  - And 70+ more packages

- **All Frontend Build Dependencies**:
  - Testing frameworks (pytest, pytest-asyncio, pytest-cov, pytest-mock)
  - Linting tools (black, flake8, mypy, isort)
  - Development utilities

### Node Environment

- **npm packages** (816 packages)
- **React 19.2** and ecosystem
- **TypeScript 5.8**
- **Build tools**: Vite, Webpack
- **Testing**: Playwright, Vitest
- **UI Libraries**: Radix UI, TailwindCSS
- **And many more...**

## Quick Start

### Using Python from Environment

```powershell
# Use Python from environment
.\.env-project\python\bin\python --version

# Run Python script
.\.env-project\python\bin\python script.py

# Run pip
.\.env-project\python\bin\pip list
```

### Using npm from Environment

```powershell
# Navigate to project
cd .env-project\node

# Use npm
npm list
```

### Setup Scripts

#### Setup.ps1 - Initialize Environment

```powershell
.\setup.ps1
```

This script:

- Registers Python path to environment
- Installs Python packages from wheels
- Sets up Node paths
- Configures development environment

#### Run-Backend.ps1 - Start Backend

```powershell
.\run-backend.ps1
```

Starts FastAPI backend using project Python

#### Run-Frontend.ps1 - Start Frontend

```powershell
.\run-frontend.ps1
```

Starts Vite dev server using project Node

#### Run-All.ps1 - Start Complete Stack

```powershell
.\run-all.ps1
```

Starts both backend and frontend

## Package Information

### Python Packages (87 total)

**Core Framework:**

- fastapi==0.104.1
- uvicorn==0.24.0 / 0.40.0
- starlette==0.27.0
- pydantic==2.5.0
- pydantic-settings==2.1.0

**Database:**

- sqlalchemy==2.0.23+
- alembic==1.12.1
- psycopg2-binary==2.9.9

**Async & Scheduling:**

- celery==5.3.4
- redis==5.0.1+
- APScheduler==3.10.4
- aioredis==2.0.1

**Testing:**

- pytest==7.4.3
- pytest-asyncio==0.21.1
- pytest-cov==4.1.0
- pytest-mock==3.12.0

**Utilities:**

- requests==2.31.0
- pandas==2.1.3
- openpyxl==3.1.2
- fpdf2==2.7.6
- reportlab==4.0.7
- PyJWT==2.8.0
- passlib==1.7.4
- bcrypt==4.1.2

[Full package list available in python/packages/]

### Node Packages (816 total)

**React & Ecosystem:**

- react@19.2.3
- react-dom@19.2.3
- react-router-dom@7.12.0
- zustand@5.0.9
- @tanstack/react-query@5.90.19

**UI & Styling:**

- @radix-ui/\* (multiple components)
- tailwindcss@3.4.17
- lucide-react@0.562.0

**Build & Development:**

- vite@6.2.0
- vitest@4.0.16
- typescript@5.8.2
- eslint@9.39.2
- prettier@3.7.4

**Testing:**

- @playwright/test@1.57.0
- @testing-library/react@16.3.1

[Full package list: node/node_modules/]

## Directory Size

- **Python binary**: ~412 MB
- **Python packages**: ~1.2 GB
- **Node modules**: ~800 MB
- **Total environment**: ~2.4 GB

## Using in Deployment

### Copy to Target Machine

```powershell
# Copy entire .env-project folder
Copy-Item .env-project -Destination \\RemoteServer\Deploy -Recurse
```

### Run Without System Python/Node

```powershell
# Backend (no system Python needed)
.\.env-project\python\bin\python -m uvicorn backend.main:app

# Frontend (no system Node needed)
.\.env-project\node\node\npm run build
```

## Environment Variables

Create `.env` file in project root:

```
DATABASE_URL=postgresql://user:password@localhost/people_os
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

## Troubleshooting

### Python Import Errors

```powershell
# Install packages from wheels
.\.env-project\python\bin\pip install --no-index --find-links=".\.env-project\python\packages" -r requirements.txt
```

### Module Not Found

Ensure you're using the Python from `.env-project\python\bin\python`, not system Python.

### Node Version Issues

All npm packages are pre-installed. Delete node_modules/.package-lock.json if issues occur.

## Updates

To update dependencies:

1. Update requirements.txt / package.json in main project
2. Re-run pip download / npm ci
3. Copy new packages to .env-project

## Security Notes

- This environment is self-contained and independent
- All packages are pinned to specific versions
- Verify package integrity before deployment
- Keep `.env` file with secrets outside version control

## Support

For issues with:

- **Backend**: Check backend/README.md
- **Frontend**: Check src/ configuration
- **Database**: See backend/schema.sql
- **Dependencies**: Review requirements.txt files

---

Created: 2026-01-23
Python Version: 3.12.10
Total Packages: 903 (87 Python + 816 Node)
