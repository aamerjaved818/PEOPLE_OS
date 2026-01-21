@echo off
setlocal
title PeopleOS - Enterprise Management System
color 0A
cls

:MAIN_MENU
cls
echo ========================================================
echo   PeopleOS - Unified Enterprise Launcher
echo ========================================================
echo.
echo   [1] Development  - Startup Dev Server (Reload ON)
echo   [2] Production   - Hardware Deployment (Secure Mode)
echo   [3] Testing      - Run Full Test Suite (Pytest/Vitest)
echo   [4] Health Check - System Diagnostics
echo   [5] Exit
echo.
echo ========================================================
set /p choice="Enter Selection [1-5]: "

if "%choice%"=="1" goto DEV_MODE
if "%choice%"=="2" goto PROD_MODE
if "%choice%"=="3" goto TEST_MODE
if "%choice%"=="4" goto HEALTH_CHECK
if "%choice%"=="5" exit
goto MAIN_MENU

:DEV_MODE
echo.
echo [SYSTEM] Launching Development Environment...
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] venv not found.
    pause
    goto MAIN_MENU
)

echo [1/2] Starting Backend...
start "PeopleOS Backend" cmd /k "venv\Scripts\activate && set APP_ENV=development&& python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

echo [2/2] Starting Frontend...
start "PeopleOS Client" cmd /k "npm run dev"

echo.
echo [SUCCESS] Application launched!
pause
goto MAIN_MENU

:PROD_MODE
echo.
echo [SYSTEM] Launching Production Environment...
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] venv not found.
    pause
    goto MAIN_MENU
)

echo [1/5] Backing up Database...
"venv\Scripts\python.exe" scripts\backup_db.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backup failed.
    pause
    goto MAIN_MENU
)

echo [2/5] Running Migrations...
set APP_ENV=production
"venv\Scripts\python.exe" -m backend.migrate_db
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Migration failed.
    pause
    goto MAIN_MENU
)

echo [3/5] Building Frontend...
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend build failed.
    pause
    goto MAIN_MENU
)

echo [4/5] Starting Production Backend...
start "PeopleOS Backend [PROD]" cmd /k "venv\Scripts\activate && set APP_ENV=production&& python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --no-access-log"

echo [5/5] Starting Frontend Preview Server...
start "PeopleOS Frontend [PROD]" cmd /k "npm run preview"

echo [INFO] Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

echo [INFO] Opening Application...
start "" http://localhost:4173

echo.
echo ========================================================
echo   PRODUCTION SERVERS RUNNING
echo   Backend API:  http://localhost:8000
echo   Frontend UI:  http://localhost:4173
echo ========================================================
pause
goto MAIN_MENU

:TEST_MODE
echo.
echo [SYSTEM] Running Test Suites...
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] venv not found.
    pause
    goto MAIN_MENU
)

set APP_ENV=test
"venv\Scripts\python.exe" -m pytest
set BACKEND_STATUS=%ERRORLEVEL%

call npm run test -- run
set FRONTEND_STATUS=%ERRORLEVEL%

echo.
echo ========================================================
if %BACKEND_STATUS% EQU 0 (echo [PASS] Backend Tests) else (echo [FAIL] Backend Tests)
if %FRONTEND_STATUS% EQU 0 (echo [PASS] Frontend Tests) else (echo [FAIL] Frontend Tests)
echo ========================================================
pause
goto MAIN_MENU

:HEALTH_CHECK
echo.
echo [SYSTEM] System Diagnostics...
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] venv not found.
    pause
    goto MAIN_MENU
)

"venv\Scripts\python.exe" scripts\health_check.py
pause
goto MAIN_MENU
