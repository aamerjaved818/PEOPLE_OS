#!/usr/bin/env pwsh
# Starts the backend using the project's virtualenv python.
# This script is intended to be invoked by a Scheduled Task at system startup.

$projectRoot = "D:\\Project\\PEOPLE_OS"
$venvPython = Join-Path $projectRoot ".venv\\Scripts\\python.exe"

if (-Not (Test-Path $venvPython)) {
  Write-Host "Virtualenv python not found at $venvPython. Falling back to system 'python' in PATH.";
  $venvPython = "python"
}

Write-Host "Starting backend with: $venvPython -m backend.main (cwd: $projectRoot)"
Start-Process -FilePath $venvPython -ArgumentList "-m", "backend.main" -WorkingDirectory $projectRoot -WindowStyle Hidden

Write-Host "Backend start command dispatched."
