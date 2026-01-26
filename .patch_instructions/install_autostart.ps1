#!/usr/bin/env pwsh
<#
Install a Scheduled Task to start the PeopleOS backend at system startup.

Run this script as Administrator.

It creates a task named "PeopleOS Backend" that runs the `start_backend.ps1` script on system startup.
#>

$projectRoot = "D:\\Project\\PEOPLE_OS"
$scriptPath = Join-Path $projectRoot ".patch_instructions\\start_backend.ps1"

if (-not (Test-Path $scriptPath)) {
  Write-Error "start_backend.ps1 not found at $scriptPath"
  exit 1
}

$taskName = 'PeopleOS Backend'
$action = "Powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`""

Write-Host "Creating scheduled task '$taskName' to run at system startup..."

schtasks /Create /TN "$taskName" /TR "$action" /SC ONSTART /RL HIGHEST /F | Out-Null

if ($LASTEXITCODE -eq 0) {
  Write-Host "Scheduled task created: $taskName"
  Write-Host "You can view it in Task Scheduler or run: schtasks /Query /TN '$taskName' /V"
} else {
  Write-Error "Failed to create scheduled task. Exit code: $LASTEXITCODE"
}
