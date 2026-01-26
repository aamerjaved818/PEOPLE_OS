@echo off
setlocal
title peopleOS eBusiness Suite Launcher
cd /d "%~dp0"

:: Quick check for .venv
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" start.py %*
) else (
    echo [WARN] .venv not found, attempting system python...
    python start.py %*
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Launcher exited with code %ERRORLEVEL%
    pause
)
