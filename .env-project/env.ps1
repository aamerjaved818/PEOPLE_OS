# Environment Configuration & Path Management
# Source this file to configure PATH and environment variables

$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$envDir = $scriptDir

# Python paths
$pythonBin = Join-Path $envDir "python\bin"
$pythonExe = Join-Path $pythonBin "python.exe"
$pipExe = Join-Path $pythonBin "pip.exe"

# Node paths  
$nodeModulesBin = Join-Path $envDir "node\node_modules\.bin"
$nodePath = Join-Path $envDir "node\node_modules"

# Only proceed if paths exist
if (-not (Test-Path $pythonExe)) {
    Write-Error "Python not found at $pythonExe"
    return
}

# Add Python and Node to PATH
$env:PATH = "$pythonBin;$nodeModulesBin;" + $env:PATH

# Set NODE_PATH for require()
$env:NODE_PATH = $nodePath

# Set pip to use local packages
$env:PIP_NO_INDEX = "1"
$env:PIP_FIND_LINKS = Join-Path $envDir "python\packages"

# Python path
$env:PYTHONPATH = (Split-Path -Parent -Path $envDir) + ";$env:PYTHONPATH"

Write-Host "Environment configured:" -ForegroundColor Green
Write-Host "  Python: $pythonExe" -ForegroundColor Gray
Write-Host "  Pip: $pipExe" -ForegroundColor Gray
Write-Host "  Node modules: $nodePath" -ForegroundColor Gray
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Green
Write-Host "  python, pip, npm, npx, node" -ForegroundColor Gray
