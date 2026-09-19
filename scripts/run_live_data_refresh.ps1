# Refresh the approved external enrichments and rebuild their governed marts.
# All credentials remain in the local .env file and are loaded by the existing
# Python/dbt commands; this script does not print environment-variable values.
[CmdletBinding()]
param(
    [switch]$Append,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $projectRoot '.env'
$pythonExe = Join-Path $projectRoot '.venv\Scripts\python.exe'
$dbtScript = Join-Path $PSScriptRoot 'run_dbt.ps1'

if (-not (Test-Path $envFile)) {
    throw 'Missing .env. Copy .env.example and configure the required local credentials.'
}
if (-not (Test-Path $pythonExe)) {
    throw 'Missing .venv Python executable. Run pip install -r requirements.txt.'
}
if (-not (Test-Path $dbtScript)) {
    throw 'Missing scripts\run_dbt.ps1.'
}

$loadArguments = if ($Append) { @() } else { @('--replace') }
$loadMode = if ($Append) { 'append' } else { 'replace' }

function Invoke-PythonRefresh {
    param(
        [string]$Name,
        [string]$Module,
        [string[]]$ModuleArguments
    )

    Write-Host "[$Name] Starting ($loadMode mode)." -ForegroundColor Cyan
    if ($DryRun) {
        Write-Host "[DRY RUN] $pythonExe -m $Module $($ModuleArguments -join ' ')"
        return
    }

    & $pythonExe -m $Module @ModuleArguments
    if ($LASTEXITCODE -ne 0) {
        throw "[$Name] Failed with exit code $LASTEXITCODE. dbt was not run."
    }
}

Write-Host 'Refreshing approved external data. Credential values are not displayed.' -ForegroundColor Green

Invoke-PythonRefresh -Name 'Open-Meteo weather' `
    -Module 'src.travel_analytics.ingest_live_weather' `
    -ModuleArguments $loadArguments
Invoke-PythonRefresh -Name 'Duffel test flight offers' `
    -Module 'src.travel_analytics.ingest_flight_offers' `
    -ModuleArguments $loadArguments
Invoke-PythonRefresh -Name 'Geoapify hotel discovery' `
    -Module 'src.travel_analytics.ingest_live_hotels' `
    -ModuleArguments $loadArguments

Write-Host '[dbt] Starting full build.' -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "[DRY RUN] $dbtScript -Operation build"
}
else {
    & $dbtScript -Operation build
    if ($LASTEXITCODE -ne 0) {
        throw "[dbt] Build failed with exit code $LASTEXITCODE."
    }
}

Write-Host 'Live-data refresh completed successfully.' -ForegroundColor Green
