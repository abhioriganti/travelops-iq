# Runs dbt debug with credentials loaded only into this PowerShell process.
# Values from .env are never written to the console.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $projectRoot '.env'
$dbtExe = Join-Path $projectRoot '.venv\Scripts\dbt.exe'
$profilesDir = Join-Path $env:USERPROFILE '.dbt'
$profileFile = Join-Path $profilesDir 'profiles.yml'

if (-not (Test-Path $envFile)) {
    throw 'Missing .env. Copy .env.example to .env and fill the required Snowflake values first.'
}

if (-not (Test-Path $dbtExe)) {
    throw 'Missing project dbt executable. Activate .venv and run: pip install -r requirements.txt'
}

if (-not (Test-Path $profileFile)) {
    throw "Missing $profileFile. Copy dbt\\profiles.yml.example to this location first."
}

Get-Content -LiteralPath $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line.Length -eq 0 -or $line.StartsWith('#')) {
        return
    }

    $pair = $line -split '=', 2
    if ($pair.Count -ne 2 -or [string]::IsNullOrWhiteSpace($pair[0])) {
        throw "Invalid .env entry. Use NAME=value; do not add spaces around the name."
    }

    Set-Item -Path ("Env:" + $pair[0].Trim()) -Value $pair[1]
}

Write-Host 'Running dbt debug. Credential values are not displayed.' -ForegroundColor Cyan
& $dbtExe debug --project-dir (Join-Path $projectRoot 'dbt') --profiles-dir $profilesDir
exit $LASTEXITCODE
