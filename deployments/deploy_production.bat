@echo off
REM Production Deployment Script for Phase 4B Part 3 (Windows)
REM Handles complete system startup

setlocal enabledelayedexpansion

REM Configuration
set LOG_DIR=logs
set REPORTS_DIR=tmp\reports
set MIGRATIONS_DIR=migrations
set VENV_DIR=.venv
set PYTHON_CMD=.venv\Scripts\python.exe
set STARTUP_TIMEOUT=30

REM Colors (Windows 10+)
set GREEN=[92m
set RED=[91m
set YELLOW=[93m
set BLUE=[94m
set RESET=[0m

REM Create directories
echo [INFO] Creating necessary directories...
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%REPORTS_DIR%" mkdir "%REPORTS_DIR%"
if not exist "%MIGRATIONS_DIR%" mkdir "%MIGRATIONS_DIR%"
echo [SUCCESS] Directories created
echo.

REM Check prerequisites
echo [INFO] Checking prerequisites...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    exit /b 1
)
echo [SUCCESS] Python found
echo.

REM Check .env file
if not exist ".env" (
    echo [WARNING] .env file not found
    echo [INFO] Running environment configuration script...
    %PYTHON_CMD% scripts\configure_environment.py
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to configure environment
        exit /b 1
    )
)
echo [SUCCESS] .env file verified
echo.

REM Setup Python environment
echo [INFO] Setting up Python environment...
if not exist "%VENV_DIR%" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>nul

REM Install requirements
if exist "requirements.txt" (
    echo [INFO] Installing Python dependencies...
    pip install -r requirements.txt >nul 2>nul
) else (
    echo [WARNING] requirements.txt not found
)
echo [SUCCESS] Python environment ready
echo.

REM Check database
echo [INFO] Checking database connectivity...
python -c "
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    exit(1)
" >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Database is accessible
) else (
    echo [ERROR] Database connection failed
    exit /b 1
)
echo.

REM Run migrations
echo [INFO] Running database migrations...
where alembic >nul 2>nul
if %errorlevel% equ 0 (
    alembic upgrade head
    if %errorlevel% neq 0 (
        echo [ERROR] Migrations failed
        exit /b 1
    )
    echo [SUCCESS] Migrations completed
) else (
    echo [WARNING] alembic not installed, skipping migrations
)
echo.

REM Start services
echo [INFO] Starting services...
echo.

REM Start FastAPI API Server
echo [INFO] Starting API Server...
start "peopleOS eBusiness Suite API" cmd /k "%PYTHON_CMD% -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4"
timeout /t 3 /nobreak

REM Start Celery Worker
echo [INFO] Starting Celery Worker...
start "peopleOS eBusiness Suite - Celery Worker" cmd /k "celery -A backend.services.async_tasks worker --loglevel=info --concurrency=4"
timeout /t 2 /nobreak

REM Start Celery Beat
echo [INFO] Starting Celery Beat...
start "peopleOS eBusiness Suite - Celery Beat" cmd /k "celery -A backend.services.async_tasks beat --loglevel=info"
timeout /t 2 /nobreak

REM Print summary
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Phase 4B Part 3 - Production Deployment Ready         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📊 Service URLs:
echo   API Documentation: http://localhost:8000/docs
echo   API Health:        http://localhost:8000/health
echo   Schedules API:     http://localhost:8000/api/v1/analytics/schedules
echo.
echo 📝 Log Files:
echo   Application:       %LOG_DIR%\app.log
echo   Celery Worker:     %LOG_DIR%\celery_worker.log
echo   Celery Beat:       %LOG_DIR%\celery_beat.log
echo.
echo 🛠️  Common Commands:
echo   View Schedules:    curl http://localhost:8000/api/v1/analytics/schedules
echo   Check Celery:      celery -A backend.services.async_tasks inspect active
echo.
echo ✅ System is starting! Check the opened windows for logs.
echo.

REM Keep batch file open
pause
