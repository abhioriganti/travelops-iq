param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $python)) {
    throw "Virtual environment Python was not found at $python. Activate or create .venv first."
}

# The server reads .env itself. Never echo the file or its secret values.
Write-Host 'Starting the local read-only Travel Analytics MCP server over stdio.'
& $python -m src.travel_analytics.mcp.server
