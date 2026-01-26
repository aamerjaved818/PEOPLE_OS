#!/usr/bin/env pwsh
<#
Removes the scheduled task installed by `install_autostart.ps1`.
Run this as Administrator.
#>

$taskName = 'PeopleOS Backend'

Write-Host "Removing scheduled task '$taskName' (if present)..."
schtasks /Delete /TN "$taskName" /F | Out-Null

if ($LASTEXITCODE -eq 0) {
  Write-Host "Scheduled task removed: $taskName"
} else {
  Write-Warning "Could not remove task or it did not exist. Exit code: $LASTEXITCODE"
}
